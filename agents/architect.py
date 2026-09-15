import sys
import os
import datetime

# 添加父目录到 path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from tools.llm import call_llm
from prompts.architect_prompts import ARCHITECT_BLUEPRINT_PROMPT
from prompts.report_templates import ACCEPTED_REPORT_TEMPLATE

def generate_blueprint(item, novelty_result, critic_result):
    """
    Step 3: 架构师 (The Architect)
    负责生成详细的研究提案，补充技术路线
    """
    title = item.get("Title", "")
    experiment = item.get("Experiment", "")
    
    print(f"[Architect Agent] Designing Detailed Blueprint: {title[:50]}...")
    
    # 1. 首先让 AI 生成详细的研究计划和问答
    prompt = ARCHITECT_BLUEPRINT_PROMPT.substitute(
        title=title,
        experiment=experiment,
        critique=critic_result.get('critique', '')
    )
    
    plan_content = call_llm(prompt, json_mode=False)
    
    # 格式化影响力预测内容
    impact_data = critic_result.get('impact_analysis_full', {})
    if not impact_data or "error" in impact_data:
        impact_md = "_暂无有效的影响力预测数据。_"
    else:
        # 构建 Markdown 格式的影响力报告
        sub_dims = impact_data.get("子维度分析", {})
        sub_dims_md = ""
        for k, v in sub_dims.items():
            score = v.get('评分', 'N/A')
            reason = v.get('理由', '无')
            sub_dims_md += f"#### {k}\n- **评分**: {score}/10\n- **评语**: {reason}\n\n"

        impact_md = (
            f"> 📊 **总体潜力评分**: **{impact_data.get('总体潜力评分', 'N/A')} / 10.0**\n\n"
            f"### 核心评估结论\n"
            f"- ✅ **优势摘要**: {impact_data.get('评估摘要', '暂无')}\n"
            f"- ⚠️ **主要限制**: {impact_data.get('主要限制', '暂无')}\n\n"
            f"### 详细维度分析\n{sub_dims_md}"
        )

    # 2. 使用 ACCEPTED_REPORT_TEMPLATE 组装最终报告
    report_content = ACCEPTED_REPORT_TEMPLATE.substitute(
        title=title,
        title_description=experiment[:200] + "...",
        frontier_background=critic_result.get("frontier_background", "暂无背景描述"),
        domain_painpoint=critic_result.get("domain_painpoint", "暂无痛点描述"),
        total_score=f"{critic_result.get('total_score', 0):.2f}",
        methodological_novelty=f"{critic_result.get('methodological_novelty', 0):.1f}",
        frontier_alignment=f"{critic_result.get('frontier_alignment', 0):.1f}",
        domain_utility=f"{critic_result.get('domain_utility', 0):.1f}",
        execution_efficiency=f"{critic_result.get('execution_efficiency', 0):.1f}",
        scholarly_impact=f"{critic_result.get('scholarly_impact', 0):.1f}",
        weight_mn=config.WEIGHT_MN,
        weight_fa=config.WEIGHT_FA,
        weight_du=config.WEIGHT_DU,
        weight_ee=config.WEIGHT_EE,
        weight_si=config.WEIGHT_SI,
        key_innovation=critic_result.get("key_innovation", "未明确"),
        strategic_advantage=critic_result.get("strategic_advantage", "未明确"),
        research_plan=plan_content,
        theoretical_outcome=critic_result.get("theoretical_outcome", "预期产出待定"),
        practical_performance=critic_result.get("practical_performance", "预期性能待定"),
        future_impact_prediction=impact_md,
        references="*(参考文献列表待自动补全)*"
    )
        
    return report_content
