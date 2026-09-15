# 论文筛选评估

一个面向科研选题的自动化评估工具。项目结合 DeepSeek 与 OpenAlex，通过多阶段流程完成文献查重、研究价值评审、学术影响力预测、候选排序和报告生成。

## English Summary

An LLM-assisted research-idea screening pipeline that combines OpenAlex retrieval, structured evaluation prompts, configurable scoring, resumable runs, and Markdown report generation. It is a decision-support prototype, not an automated peer-review system.

## 功能

- 基于 OpenAlex 检索相似论文并评估选题新颖性
- 从方法新颖性、前沿契合度、领域价值和执行效率等维度评分
- 预测候选选题的潜在学术影响力
- 通过三阶段筛选生成 Top N 研究建议与横向对比报告
- 支持中间状态保存与断点续跑

## 项目结构

```text
.
├── agents/                 # 评估智能体
├── input/                  # 脱敏示例输入
├── prompts/                # 提示词与报告模板
├── tools/                  # LLM、OpenAlex 与文件工具
├── tests/                  # 无 API 离线测试
├── examples/               # 脱敏静态示例输出
├── docs/                   # 发布材料
├── config.py               # 配置加载
├── config.yaml             # 非敏感运行参数
├── main.py                 # 主程序
└── requirements.txt        # Python 依赖
```

## 快速开始

建议使用 Python 3.10 或更高版本。

```bash
python -m venv .venv
```

Windows PowerShell：

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS / Linux：

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

复制环境变量示例并填写本地配置：

```bash
cp .env.example .env
```

Windows PowerShell 可使用：

```powershell
Copy-Item .env.example .env
```

`.env` 中需要配置：

```dotenv
DEEPSEEK_API_KEY=your-deepseek-api-key
OPENALEX_EMAIL=your-email@example.com
```

`OPENALEX_EMAIL` 为可选项，用于加入 OpenAlex Polite Pool。密钥和邮箱不会被 Git 跟踪。

## 输入格式

示例位于 `input/ideas.example.json`。每条记录至少应包含 `Title` 和 `Experiment`：

```json
[
  {
    "Name": "example_idea",
    "Title": "Example Research Idea",
    "Experiment": "Describe the proposed method and evaluation plan."
  }
]
```

如果需要评估自己的数据，请在本地替换示例内容，或先备份示例文件。不要提交含未公开研究构想或个人信息的数据。

## 运行

```bash
python main.py
```

也可以从项目目录外指定输入和输出路径：

```bash
python main.py --input input/my_ideas.json --output output/run-01 --max-items 20 --top-n 3
```

使用 `--no-resume` 忽略已有断点，使用 `--no-save-rejected` 不生成拒绝报告。评分阈值可以用 `--novelty-threshold`、`--frontier-threshold`、`--utility-threshold`、`--efficiency-threshold` 和 `--impact-threshold` 覆盖。真实运行需要 DeepSeek API Key，并可能产生模型调用费用。

结果会写入 `output/reports/` 和 `output/rejected/`。运行日志、断点文件和输出目录默认不纳入版本控制。

## 配置

可在 `config.yaml` 中调整模型名称、评分门槛、维度权重、单次处理数量和最终入选数量。API 密钥只能通过 `.env` 或系统环境变量提供。

## 架构

```mermaid
flowchart TD
  A[JSON 输入] --> B[新颖性检查]
  B --> C[OpenAlex 检索]
  B --> D[多维评审]
  D --> E[影响力预测]
  E --> F[评分与排序]
  F --> G[研究蓝图与汇总报告]
```

每个通过初筛的选题至少需要关键词提取、新颖性判断和综合评审调用；进入后续阶段的选题还会产生影响力预测和蓝图生成调用。实际费用取决于模型、输入长度、检索结果数量和通过率。

## 测试

测试不读取密钥，也不访问 DeepSeek 或 OpenAlex：

```bash
python -m compileall -q .
python -m unittest discover -s tests -v
```

## 局限性

- OpenAlex 的覆盖范围不完整，可能遗漏新论文、预印本和非英文研究。
- LLM 评分不具备客观一致性，模型版本和提示词会影响排名。
- 系统不是系统性文献综述，不能替代同行评议或学术判断。
- 研究构想会发送给配置的模型服务商，使用前应检查其数据政策。
- 不应直接依据系统输出决定论文投稿、课题立项或资金分配。

## 项目状态

这是一个用于展示 AI 应用工程能力的研究辅助原型。静态示例位于 `examples/`，不代表真实 API 运行结果。项目使用 MIT License，详见 `LICENSE`。

## 安全说明

- 不要提交 `.env`、API 密钥、数据库连接串或私人邮箱。
- 发布运行结果前，应再次检查其中是否包含未公开研究内容或个人信息。
- 如果密钥曾以明文写入文件，请先在服务商控制台撤销，再生成新密钥。

## 说明

系统输出由语言模型和外部学术数据生成，只适合作为研究决策辅助，不能替代正式的系统性文献综述、同行评议或学术判断。
