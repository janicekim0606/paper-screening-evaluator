# CHANGELOG

## [2.0.1] - 2026-01-06
### 已添加
- 新增了对全量题目的报告跟踪机制，确保无论被拒绝还是接受，每个题目都生成对应的 Markdown 文件。
- 为 `main.py` 增加了基于阶段的错误拦截，防止某一个 LLM 调用失败导致整个流水线崩溃。
- 完善了 Top 3 对比报告的空值填充逻辑。

### 已修改
- **逻辑优化**: 强化了动态排名筛选，修正了阶段 2 的惩罚项计算逻辑，确保 `REJECTED_QUALITY` 报告包含具体的维度得分明细。
- **稳定性提升**: 为 LLM 调用增加了更长的超时容忍，并在主循环中增加了更多的 `try-except` 包裹。
- **报告格式**: 统一了 `output/rejected` 和 `output/reports` 的命名规范，方便后期对比。

## [2.0.0] - 2026-01-06

### Added
- 引入全新的“四维评估体系”：方法论新颖性 (MN)、前沿契合度 (FA)、领域应用价值 (DU)、资源博弈可行性 (EE)。
- 新增 `FINAL_COMPARISON_TEMPLATE` 用于生成 Top 3 选题的横向对比报告。
- 在 `config.yaml` 中新增不同维度的权重配置和更严苛的动态筛选阈值。
- 在 `main.py` 中实现了三阶段递进式筛选机制与锦标赛动态排名。

### Changed
- 重构 `NOVELTY_REJECTION_TEMPLATE` 和 `QUALITY_REJECTION_TEMPLATE`，增加证据链（相似论文或痛点分析）显示。
- 重构 `ACCEPTED_REPORT_TEMPLATE`，增加选题背景、科学意义、预期成果等板块。
- 更新 `CRITIC_REVIEW_PROMPT`，使 AI 评审专家能根据四维指标进行打分。
- 优化 `main.py` 逻辑，实现了根据目标接受数（Target Accepted Count）进行动态淘汰的机制，以降低虚高接受率。

### Fixed
- 修正了原本评分维度过于单一（仅新颖、有趣、可行）导致筛选结果平庸的问题。
- 解决了原本代码中接受率偏高、筛选门槛模糊的问题。
