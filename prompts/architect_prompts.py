from string import Template

ARCHITECT_BLUEPRINT_PROMPT = Template("""
    你是一位首席研究员（Principal Researcher）。一位初级学生提出了一个通过了初步审查的有前途的想法。
    现在你需要为他们撰写一份正式的研究提案（Research Proposal）。
    
    想法标题: $title
    实验细节: $experiment
    
    评审反馈: $critique
    
    任务：生成一份详细的 Markdown 格式的中文报告核心内容（研究计划部分）。
    
    格式规则：
    1. **语言**：主要内容必须使用中文（简体）。
    2. **语气**：学术、严谨、可执行。
    3. **结构**：直接输出以下章节内容，使用三级标题 (###)。
    
    报告结构（必须严格遵守）：
    
    ### 1. 数据集与基准 (Dataset & Baselines)
    - **数据集策略 (Dataset Strategy)**：具体使用哪些公开数据集，以及是否需要构建特定子集。
    - **基线模型 (Baseline Models)**：具体对比哪些架构（如 ResNet, ViT, MAE 等）。
    
    ### 2. 详细实施步骤 (Implementation Steps)
    *请按逻辑顺序分步描述实现过程：*
    - **Step 1: 数据准备与预处理**
      - [具体内容...]
    - **Step 2: 基线复现与环境搭建**
      - [具体内容...]
    - **Step 3: 核心算法实现**
      - [具体内容...]
    - **Step 4: 实验验证与迭代**
      - [具体内容...]
      
    ### 3. 消融实验设计 (Ablation Studies)
    *设计关键实验来验证核心假设：*
    - **实验 A**: 去掉组件 X 的影响...
    - **实验 B**: 不同超参数的敏感性分析...
    
    输出纯 Markdown 内容。
""")
