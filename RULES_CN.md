# 项目开发规则 (Project Rules)

为了维护代码质量和项目架构的稳定性，所有贡献者（包括人类开发者和 AI 助手）必须遵守以下规则：

## 1. 架构原则
-   **模块化 (Modularity)**：严禁将业务逻辑堆砌在 `main.py` 中。新功能必须封装在 `agents/` 或 `tools/` 下的独立模块中。
    -   `agents/architect.py`: 负责生成最终的研究计划蓝图。
    -   `agents/critic.py`: 负责对研究思路进行详细的多维度评审。
    -   `agents/novelty.py`: 负责快速初筛，判断新颖性。
    -   `agents/impact_predictor.py`: 负责预测研究的长期学术影响力。
-   **关注点分离 (Separation of Concerns)**：
    -   `agents/` 只负责流程控制和决策逻辑。
    -   `prompts/` 只负责存放提示词模板。**严禁在 Python 代码中硬编码 Prompt 字符串。**
    -   `tools/` 只负责底层能力（如 API 调用、文件读写）。

## 2. 提示词工程 (Prompt Engineering)
-   **独立管理**：所有 Prompt 必须存放在 `prompts/` 目录下的对应文件中（如 `novelty_prompts.py`）。
-   **模板化**：必须使用 Python 的 `string.Template` 类，通过 `$variable` 形式传递参数，禁止使用 f-string 拼接长文本。
-   **输出模板**：生成的报告（包括拒绝报告）必须使用 `prompts/report_templates.py` 中的固定模板，确保格式统一。
-   **语言规范**：Prompt 的指令部分建议使用**中文**（根据用户最新要求），以确保输出内容的语言风格符合预期。

## 3. 代码规范
-   **类型安全**：在关键接口（如 API 返回值解析）处必须进行错误处理（如 `try-except`），防止因 LLM 输出格式错误导致程序崩溃。
-   **注释**：所有函数必须包含文档字符串（Docstring），说明输入参数和返回值。
-   **配置管理**：
    -   用户可配置的参数（如阈值、运行数量）应放在 `config.yaml` 中。
    -   代码中应通过 `config.py` 模块读取这些配置，严禁在业务代码中硬编码常量。
    -   敏感信息（API Key）必须通过环境变量（`.env`）管理。

## 4. 变更流程
-   在修改核心逻辑前，必须先阅读 `README_CN.md` 理解项目背景。
-   修改 Prompt 时，需确保不破坏原有的 JSON 输出格式要求，否则会导致解析失败。
-   **文档同步**：当对项目功能、配置参数或行为逻辑做出修改时，必须同步更新 `README_CN.md`，确保文档与代码保持一致。

## 5. 评分与筛选
-   **评分必须支持浮点数**（如 8.5），以提高区分度。
-   **加权总分机制**：根据 `config.py` 中的权重配置，计算综合得分。主要指标包括：
    -   方法论新颖性 (Methodological Novelty)
    -   前沿对齐度 (Frontier Alignment)
    -   领域应用价值 (Domain Utility)
    -   执行效率 (Execution Efficiency)
-   **排序逻辑**：筛选阶段优先依照**加权总分**进行排序，并结合锦标赛机制（Score R2）筛选出最优方案。淘汰方案需生成拒绝报告。
