import os
import sys
import time
import datetime
import argparse
import json
import hashlib
import math
from pathlib import Path
from tqdm import tqdm
import config
from tools.data import load_data, sanitize_report_filename, save_report
from agents.novelty import check_novelty
from agents.critic import review_idea
from agents.architect import generate_blueprint
from agents.impact_predictor import predict_impact
from prompts.report_templates import (
    NOVELTY_REJECTION_TEMPLATE, 
    QUALITY_REJECTION_TEMPLATE, 
    FINAL_COMPARISON_TEMPLATE
)
from scoring import ScoreWeights, phase_one_score, phase_two_score, total_score as calculate_total_score
from errors import InvalidResponseError

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = PROJECT_ROOT / "output"
STAGING_PATH = PROJECT_ROOT / "PHASE1_STAGING.json"
PROGRESS_PATH = PROJECT_ROOT / "PROGRESS.log"


def configure_output_encoding():
    """让 Windows 控制台以 UTF-8 输出，并安全替换无法显示的字符。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")


def input_fingerprint(input_path):
    """返回输入文件的稳定指纹，用于隔离断点数据。"""
    return {
        "path": str(input_path.resolve()),
        "sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
    }


def write_error_report(stage, title, error, index):
    """记录单个选题的失败阶段和错误摘要。"""
    error_dir = OUTPUT_ROOT / "errors"
    error_dir.mkdir(parents=True, exist_ok=True)
    (error_dir / f"{index + 1:03d}_{stage}.md").write_text(
        f"# Evaluation Error\n\n- Stage: {stage}\n- Title: {title}\n"
        f"- Error type: {type(error).__name__}\n- Error: {error}\n",
        encoding="utf-8",
    )


def save_rejected_report(filename, content):
    """按运行配置保存拒绝报告。"""
    if config.SAVE_REJECTED:
        save_report(filename, content, OUTPUT_ROOT / "rejected")


def report_name(prefix, title):
    """生成报告的完整逻辑标题，供保存和存在性检查共同使用。"""
    return f"{prefix}_{title}"


def parse_args():
    """解析运行参数，命令行值覆盖配置文件。"""
    parser = argparse.ArgumentParser(description="评估科研选题并生成研究报告")
    parser.add_argument("--input", type=Path, default=PROJECT_ROOT / config.DEFAULT_INPUT_PATH)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / config.DEFAULT_OUTPUT_PATH)
    parser.add_argument("--max-items", type=int, default=config.MAX_ITEMS_TO_PROCESS)
    parser.add_argument("--top-n", type=int, default=config.TARGET_ACCEPTED_COUNT)
    parser.add_argument("--novelty-threshold", type=float, default=None)
    parser.add_argument("--frontier-threshold", type=float, default=None)
    parser.add_argument("--utility-threshold", type=float, default=None)
    parser.add_argument("--efficiency-threshold", type=float, default=None)
    parser.add_argument("--impact-threshold", type=float, default=None)
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--no-save-rejected", action="store_true")
    return parser.parse_args()

def main():
    global OUTPUT_ROOT, STAGING_PATH, PROGRESS_PATH
    configure_output_encoding()
    args = parse_args()
    OUTPUT_ROOT = args.output if args.output.is_absolute() else PROJECT_ROOT / args.output
    STAGING_PATH = OUTPUT_ROOT / "PHASE1_STAGING.json"
    PROGRESS_PATH = OUTPUT_ROOT / "PROGRESS.log"
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    if args.no_resume and STAGING_PATH.exists():
        STAGING_PATH.unlink()

    config.MAX_ITEMS_TO_PROCESS = max(0, args.max_items)
    config.TARGET_ACCEPTED_COUNT = max(0, args.top_n)
    config.set_runtime_overrides({
        "THRESHOLD_NOVELTY": args.novelty_threshold,
        "THRESHOLD_FRONTIER": args.frontier_threshold,
        "THRESHOLD_UTILITY": args.utility_threshold,
        "THRESHOLD_EFFICIENCY": args.efficiency_threshold,
        "THRESHOLD_IMPACT": args.impact_threshold,
    })
    if args.no_save_rejected:
        config.SAVE_REJECTED = False

    print("=== 自动化研究思路评估系统 (V2.0 专业版) ===")
    
    # 1. 加载数据
    input_path = args.input if args.input.is_absolute() else PROJECT_ROOT / args.input
    
    items = load_data(input_path)
    if not items:
        print("❌ 错误: 未能加载输入数据，请检查 input/输入.json 是否存在。")
        return
        
    # 2. 阶段 1: 初筛 (新颖性与前沿性)
    print(f"\n=== 阶段 1: 新颖性与前沿性初筛 (目标评分: {config.THRESHOLD_NOVELTY}) ===")
    
    pre_candidates = []
    processed_titles = []
    
    staging_path = STAGING_PATH
    if staging_path.exists():
        with open(staging_path, "r", encoding="utf-8") as f:
            staged_data = json.load(f)
            if (
                isinstance(staged_data, dict)
                and staged_data.get("input") == input_fingerprint(input_path)
                and isinstance(staged_data.get("candidates"), list)
            ):
                pre_candidates = staged_data["candidates"]
                processed_titles = [d["item"]["Title"] for d in pre_candidates]
                print(f"[Resume] Loaded {len(pre_candidates)} candidates and checking rejected files...")
            else:
                print("[Resume] Staging file does not match current input; starting fresh.")

    start_time = time.time()
    
    # 按照配置处理前 N 个题目
    process_limit = min(len(items), config.MAX_ITEMS_TO_PROCESS)
    target_items = items[:process_limit]
    
    for idx, item in enumerate(target_items):
        title = item.get("Title", "Untitled Idea")
        
        # 检查是否已在候选池或已拒绝
        rej_file1 = OUTPUT_ROOT / "rejected" / f"{sanitize_report_filename(report_name('REJECTED_PHASE1_NOVELTY', title))}.md"
        rej_file2 = OUTPUT_ROOT / "rejected" / f"{sanitize_report_filename(report_name('REJECTED_PHASE1_FRONTIER', title))}.md"
        
        if title in processed_titles or os.path.exists(rej_file1) or os.path.exists(rej_file2):
            # print(f"  ⏭️ 跳过已处理: {title[:20]}...")
            continue

        print(f"\n[{idx+1}/{process_limit}] 正在处理: {title[:50]}...")
        with PROGRESS_PATH.open("a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now()}: Processing {idx+1}/{process_limit} - {title}\n")
            f.flush()
        title_safe = title
        
        try:
            # Step 1.1: 新颖性与重复性检查
            novelty_res = check_novelty(item)
            
            # 若第一阶段分数不足 (硬门槛)
            if not novelty_res or novelty_res['novelty_score'] < config.THRESHOLD_NOVELTY:
                reason = novelty_res['novelty_reason'] if novelty_res else "系统无法获取有效新颖性分析结果"
                print(f"  ❌ 拒绝: {title[:20]}... [新颖性分: {novelty_res['novelty_score'] if novelty_res else 0}]")
                
                papers_text = ""
                if novelty_res:
                    for p in novelty_res.get('similar_papers', []):
                        papers_text += f"- **{p['title']}** ({p['publication_year']})\n  - URL: {p.get('landing_page_url')}\n"
                
                rpt = NOVELTY_REJECTION_TEMPLATE.substitute(
                    title=title,
                    title_description=item.get("Experiment", "")[:200] + "...",
                    methodological_novelty=novelty_res['novelty_score'] if novelty_res else 0,
                    threshold_novelty=config.THRESHOLD_NOVELTY,
                    threshold_frontier=config.THRESHOLD_FRONTIER,
                    novelty_reason=reason,
                    similar_papers_list=papers_text if papers_text else "经 OpenAlex 查重未发现强相关论文，由于方法论过于传统被 AI 判定低分。"
                )
                save_rejected_report(report_name("REJECTED_PHASE1_NOVELTY", title_safe), rpt)
                continue

            # Step 1.2: 学术前沿性专家初评
            critic_res = review_idea(item, novelty_res)
            # 加权计算初筛分 (重心在新颖度)
            score_r1 = phase_one_score(
                critic_res['methodological_novelty'],
                critic_res['frontier_alignment'],
            )
            
            if score_r1 < config.THRESHOLD_FRONTIER:
                print(f"  ❌ 拒绝: {title[:20]}... [前沿性分不足: {score_r1:.2f}]")
                rpt = NOVELTY_REJECTION_TEMPLATE.substitute(
                    title=title,
                    title_description=item.get("Experiment", "")[:200] + "...",
                    methodological_novelty=critic_res['methodological_novelty'],
                    threshold_novelty=config.THRESHOLD_NOVELTY,
                    threshold_frontier=config.THRESHOLD_FRONTIER,
                    novelty_reason=f"前沿评价: {critic_res.get('critique', '缺乏前瞻性研究价值')}",
                    similar_papers_list="通过了初步数据库查重，但在同行评议模型中被判定为学术路径常规，缺乏突破潜力。"
                )
                save_rejected_report(report_name("REJECTED_PHASE1_FRONTIER", title_safe), rpt)
                continue

            # 通过初筛进入待定池
            result_item = {
                "item": item, 
                "novelty_res": novelty_res, 
                "critic_res": critic_res,
                "score_r1": score_r1
            }
            pre_candidates.append(result_item)
            
            # 保存中间结果
            with STAGING_PATH.open("w", encoding="utf-8") as f:
                json.dump(
                    {"input": input_fingerprint(input_path), "candidates": pre_candidates},
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
            
            with PROGRESS_PATH.open("a", encoding="utf-8") as f:
                f.write(f"{datetime.datetime.now()}: FINISHED {idx+1}/{process_limit}\n")
                f.flush()

        except Exception as e:
            write_error_report("phase1", title, e, idx)
            print(f"  ⚠️ 报错跳过: {title[:20]} | Error: {str(e)}")
            continue

    # 3. 阶段 2: 质量与动态排名筛选
    print(f"\n=== 阶段 2: 质量综合审查与横向排名 (初筛通过: {len(pre_candidates)} 个) ===")
    
    scored_candidates = []
    
    # 限制并发量或打印进度
    for idx, cand in enumerate(tqdm(pre_candidates, desc="Phase 2 Analysis")):
        c = cand['critic_res']
        
        # New Agent Call: 学术影响力预测 (The 5th Dimension)
        # 注意: 这会增加 LLM 调用成本
        try:
            impact_res = predict_impact(cand['item'], cand['novelty_res'], c)
        except Exception as error:
            write_error_report("impact", cand['item']['Title'], error, idx)
            print(f"  ⚠️ 影响力预测失败，跳过排名: {cand['item']['Title'][:30]}")
            continue
        cand['impact_res'] = impact_res
        
        # 评分异常或未达门槛时进入失败记录，不伪装成刚好合格。
        try:
            scholarly_impact = float(impact_res["总体潜力评分"])
        except (KeyError, ValueError, TypeError):
            write_error_report(
                "impact",
                cand['item']['Title'],
                InvalidResponseError("影响力评分不是有效数字"),
                idx,
            )
            continue
        if not math.isfinite(scholarly_impact) or not 0 <= scholarly_impact <= 10:
            write_error_report(
                "impact",
                cand['item']['Title'],
                InvalidResponseError("影响力评分超出 0-10 范围"),
                idx,
            )
            continue

        try:
            execution_efficiency = float(c["execution_efficiency"])
        except (KeyError, ValueError, TypeError):
            write_error_report(
                "quality",
                cand['item']['Title'],
                InvalidResponseError("执行效率评分不是有效数字"),
                idx,
            )
            continue
        if execution_efficiency < config.THRESHOLD_EFFICIENCY:
            write_error_report(
                "quality",
                cand['item']['Title'],
                InvalidResponseError("执行效率未达到配置门槛"),
                idx,
            )
            continue
        if scholarly_impact < config.THRESHOLD_IMPACT:
            write_error_report(
                "quality",
                cand['item']['Title'],
                InvalidResponseError("学术影响力未达到配置门槛"),
                idx,
            )
            continue
            
        cand['scholarly_impact'] = scholarly_impact

        # 计算质量分 (侧重领域价值与落地性)
        score_r2 = phase_two_score(c['domain_utility'], c['execution_efficiency'])
        
        # 惩罚项：如果领域价值极低则直接应用惩罚
        # 综合加权总分 (按权重表，现在是 5 个维度)
        candidate_total_score = calculate_total_score(
            {
                'methodological_novelty': c['methodological_novelty'],
                'frontier_alignment': c['frontier_alignment'],
                'domain_utility': c['domain_utility'],
                'execution_efficiency': c['execution_efficiency'],
                'scholarly_impact': scholarly_impact,
            },
            ScoreWeights(config.WEIGHT_MN, config.WEIGHT_FA, config.WEIGHT_DU, config.WEIGHT_EE, config.WEIGHT_SI),
            config.THRESHOLD_UTILITY,
        )
        
        cand['total_score'] = candidate_total_score
        cand['score_r2'] = score_r2
        scored_candidates.append(cand)

    # 锦标赛动态排名逻辑：仅保留本批次 Top 50%
    scored_candidates.sort(key=lambda x: x['score_r2'], reverse=True)
    passed_candidates = scored_candidates[:max(1, len(scored_candidates) // 2)]
    
    # 将淘汰的一半记录到 rejected
    for rj in scored_candidates[len(passed_candidates):]:
        title_safe = rj['item']['Title']
        rpt = QUALITY_REJECTION_TEMPLATE.substitute(
            title=rj['item']['Title'],
            title_description=rj['item']['Experiment'][:200] + "...",
            methodological_novelty=rj['critic_res']['methodological_novelty'],
            frontier_alignment=rj['critic_res']['frontier_alignment'],
            domain_utility=rj['critic_res']['domain_utility'],
            execution_efficiency=rj['critic_res']['execution_efficiency'],
            scholarly_impact=f"{rj.get('scholarly_impact', 0):.1f}",
            threshold_novelty=config.THRESHOLD_NOVELTY,
            threshold_frontier=config.THRESHOLD_FRONTIER,
            threshold_utility=config.THRESHOLD_UTILITY,
            threshold_efficiency=config.THRESHOLD_EFFICIENCY,
            threshold_impact=config.THRESHOLD_IMPACT,
            critique=f"动态竞争结果：在当前批次对比中，由于横向对比分数({rj['score_r2']:.2f})未进入前50%被淘汰。{rj['critic_res'].get('critique')}"
        )
        save_rejected_report(report_name("REJECTED_PHASE2_QUALITY", title_safe), rpt)

    # 4. 阶段 3: 蓝图生成与报告保存
    print(f"\n=== 阶段 3: 最终优选与蓝图生成 (入围人数: {len(passed_candidates)}) ===")
    
    passed_candidates.sort(key=lambda x: x['total_score'], reverse=True)
    final_selection = passed_candidates[:config.TARGET_ACCEPTED_COUNT]
    
    for i, res in enumerate(final_selection):
        title_safe = res['item']['Title']
        print(f"  ⭐ 选定 [Rank {i+1}]: {res['item']['Title'][:40]} | 总分: {res['total_score']:.2f}")
        
        res['critic_res']['total_score'] = res['total_score']
        res['critic_res']['scholarly_impact'] = res['scholarly_impact'] # 注入影响力分数以便 report 使用
        res['critic_res']['impact_analysis_full'] = res.get('impact_res', {}) # 注入完整影响力分析结果
        report = generate_blueprint(res['item'], res['novelty_res'], res['critic_res'])
        save_report(report_name(f"ACCEPTED_RANK{i+1}", title_safe), report, OUTPUT_ROOT / "reports")

    # 5. Top 3 汇总横向对比报告
    if len(final_selection) >= 2:
        print(f"\n=== 正在生成 Top 3 对比分析报告 ===")
        comparison_data = {}
        for i in range(3):
            if i < len(final_selection):
                c = final_selection[i]
                comparison_data[f"title_{i+1}"] = c['item']['Title']
                comparison_data[f"tech_{i+1}"] = c['critic_res'].get('key_innovation', '核心技术路径：' + c['item']['Experiment'][:100])
                comparison_data[f"value_{i+1}"] = c['critic_res'].get('strategic_advantage', '该方案具有较强的领域应用价值。')
                comparison_data[f"fa_{i+1}"] = c['critic_res']['frontier_alignment']
                comparison_data[f"mn_{i+1}"] = c['critic_res']['methodological_novelty']
                comparison_data[f"du_{i+1}"] = c['critic_res']['domain_utility']
                comparison_data[f"ee_{i+1}"] = c['critic_res']['execution_efficiency']
                comparison_data[f"si_{i+1}"] = f"{c.get('scholarly_impact', 0):.1f}"
                comparison_data[f"total_{i+1}"] = f"{c['total_score']:.2f}"
            else:
                comparison_data[f"title_{i+1}"] = "N/A"
                comparison_data[f"tech_{i+1}"] = "无"
                comparison_data[f"value_{i+1}"] = "无"
                comparison_data[f"fa_{i+1}"] = "-"
                comparison_data[f"mn_{i+1}"] = "-"
                comparison_data[f"du_{i+1}"] = "-"
                comparison_data[f"ee_{i+1}"] = "-"
                comparison_data[f"si_{i+1}"] = "-"
                comparison_data[f"total_{i+1}"] = "0.00"

        c_rpt = FINAL_COMPARISON_TEMPLATE.substitute(
            **comparison_data,
            best_title=final_selection[0]['item']['Title'],
            best_reason=final_selection[0]['critic_res'].get('critique', '综合各项指标表现最优。')[:300],
            runner_up_title=final_selection[1]['item']['Title'] if len(final_selection)>1 else "N/A",
            runner_up_reason=final_selection[1]['critic_res'].get('critique', '表现优异，略逊于冠军项。')[:300] if len(final_selection)>1 else "N/A",
            third_title=final_selection[2]['item']['Title'] if len(final_selection)>2 else "N/A",
            third_reason=final_selection[2]['critic_res'].get('critique', '具有一定参考价值。')[:300] if len(final_selection)>2 else "N/A",
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        save_report("FINAL_COMPARISON_TOP3_REPORT", c_rpt, OUTPUT_ROOT / "reports")

    duration = (time.time() - start_time) / 60
    print(f"\n=== 全部流程完成! 结果保存在 output 文件夹中。总耗时: {duration:.2f} 分钟 ===")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(error_msg)
        with (PROJECT_ROOT / "CRASH_DEBUG.txt").open("w", encoding="utf-8") as f:
            f.write(error_msg)
        sys.exit(1)
