from string import Template

# 阶段 1: 新颖性/前沿性拒绝报告模板
NOVELTY_REJECTION_TEMPLATE = Template("""# 研究题目评审决议书 (Rejected)

## 0. 题目基本信息
- **研究题目**: $title
- **核心领域**: 由研究题目与实验描述确定
- **初步描述**: $title_description

## 1. 评审结论
**最终状态**: ❌ 已拒绝 (Rejected)
**拒绝环节**: 阶段 1: 新颖性与前沿性初筛

## 2. 详细评分结果 (专家五维评分矩阵)
*注：因项目在第一阶段新颖性/前沿性初筛中未达标，故触发中止机制，未进行后续维度的深度评估。*

| 评估维度 | 得分 | 合格阈值 | 结论 |
| :--- | :--- | :--- | :--- |
| **方法论新颖性 (Methodological Novelty)** | $methodological_novelty | $threshold_novelty | [FAIL] |
| **前沿契合度 (Frontier Alignment)** | 尚未评估 | $threshold_frontier | [N/A] |
| **领域应用价值 (Domain Utility)** | N/A | N/A | [N/A] |
| **资源博弈可行性 (Execution Efficiency)** | N/A | N/A | [N/A] |
| **学术影响力预测 (Scholarly Impact)** | N/A | N/A | [N/A] |

## 3. 拒绝原因及依据 (Critique & Evidence)
- **失败原因**: $novelty_reason
- **判定依据**: 系统检测到该思路与以下已发表论文高度重合（相似度 > 85%）：
$similar_papers_list
- **改进建议**: 建议避开已有的方法，尝试从新的视角（如数据分布、跨域场景）入手。
""")

# 阶段 2: 质量/价值拒绝报告模板
QUALITY_REJECTION_TEMPLATE = Template("""# 研究题目评审决议书 (Rejected)

## 0. 题目基本信息
- **研究题目**: $title
- **核心领域**: 由研究题目与实验描述确定
- **初步描述**: $title_description

## 1. 评审结论
**最终状态**: ❌ 已拒绝 (Rejected)
**拒绝环节**: 阶段 2: 领域价值与落地深研

## 2. 详细评分结果 (专家五维评分矩阵)
| 评估维度 | 得分 | 合格阈值 | 结论 |
| :--- | :--- | :--- | :--- |
| **方法论新颖性 (Methodological Novelty)** | $methodological_novelty | $threshold_novelty | [PASS] |
| **前沿契合度 (Frontier Alignment)** | $frontier_alignment | $threshold_frontier | [PASS] |
| **领域应用价值 (Domain Utility)** | $domain_utility | $threshold_utility | [FAIL] |
| **资源博弈可行性 (Execution Efficiency)** | $execution_efficiency | $threshold_efficiency | [FAIL] |
| **学术影响力预测 (Scholarly Impact)** | $scholarly_impact | $threshold_impact | [INFO] |

## 3. 拒绝原因及依据 (Critique & Evidence)
- **失败原因**: 领域价值不足或实现难度/资源错位。
- **判定依据**: 
$critique
- **改进建议**: 该项研究目前处于本批次排名的末 50%，建议加强对实际生物学场景痛点的调研。
""")

# 接受报告模板 (Accepted Report)
ACCEPTED_REPORT_TEMPLATE = Template("""# 研究蓝图与接受报告 (Accepted Blueprint)

## 1. 题目详细描述
- **正式题目**: $title
- **题目简介**: $title_description

## 2. 选题背景与科学意义
### 🔥 学术热度
$frontier_background

### 🎯 领域痛点
$domain_painpoint

## 3. 专家五维评估矩阵
> **综合得分**: **$total_score** / 70.0

| 评估维度 | 评分 | 权重 | 权重设定理由 |
| :--- | :--- | :--- | :--- |
| **方法论新颖性 (MN)** | $methodological_novelty | $weight_mn | 防止重复造轮子，奖励原始创新 |
| **前沿契合度 (FA)** | $frontier_alignment | $weight_fa | 确保技术不落后，符合学术前沿趋势 |
| **领域应用价值 (DU)** | $domain_utility | $weight_du | 解决实际学科痛点是核心目标 (高权重) |
| **资源博弈可行性 (EE)** | $execution_efficiency | $weight_ee | 确保在有限算力下可执行 |
| **学术影响力预测 (SI)** | $scholarly_impact | $weight_si | 关注长期的知识传播与社区贡献 |

## 4. 核心入选理由
### 💡 核心突破口
$key_innovation

### 🚀 策略优势
$strategic_advantage

## 5. 研究计划与实施步骤
$research_plan

## 6. 预期成果
### 🏆 理论成果
$theoretical_outcome

### 📈 实际表现
$practical_performance

## 7. 未来学术影响力预测
$future_impact_prediction
""")

# Top 3 横向对比报告模板
FINAL_COMPARISON_TEMPLATE = Template("""# 顶层决策报告：Top 3 选题横向对比

## 1. 入选项目概览
本报告对本次自动化筛选出的前三名（Top 3）高价值选题进行横向比对，旨在为决策者提供最终执行建议。

| 排名 | 研究题目 | 核心技术路径 | 核心价值 |
| :--- | :--- | :--- | :--- |
| **Rank 1** | $title_1 | $tech_1 | $value_1 |
| **Rank 2** | $title_2 | $tech_2 | $value_2 |
| **Rank 3** | $title_3 | $tech_3 | $value_3 |

## 2. 专家维度评分比对
| 题目 | 前沿契合度 | 方法新颖性 | 领域价值 | 可行性 | 影响力 | **加权总分** |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Rank 1** | $fa_1 | $mn_1 | $du_1 | $ee_1 | $si_1 | **$total_1** |
| **Rank 2** | $fa_2 | $mn_2 | $du_2 | $ee_2 | $si_2 | **$total_2** |
| **Rank 3** | $fa_3 | $mn_3 | $du_3 | $ee_3 | $si_3 | **$total_3** |

## 3. 综合推荐意见 (Expert Summary)
- **最佳推荐 (Highly Recommended)**: **$best_title**。
  - *理由*: $best_reason
- **高潜力备选**: **$runner_up_title**。
  - *理由*: $runner_up_reason
- **多样性建议**: **$third_title**。
  - *理由*: $third_reason

---
**系统评估完成时间**: $timestamp
""")
