from string import Template

CRITIC_REVIEW_PROMPT = Template("""
    你是一位 CVPR/ICCV 的资深领域主席（Senior Area Chair），精通计算机视觉与海洋生物学交叉领域。你需要从“五维评估体系”出发，严谨评估以下研究想法。
    
    研究想法:
    标题: $title
    实验细节: $experiment
    
    新颖性初筛结果:
    - 方法论新颖评分: $methodological_novelty/10.
    - 相似性分析: $novelty_reason
    
    任务：请针对以下五个维度进行深度打分和评价。
    
    1. 方法论新颖性 (Methodological Novelty): 
       - 核心贡献是现有模块的简单组合（A+B），还是针对特定问题提出的原始创新？
       - 逻辑推导是否严密？
       
    2. 前沿契合度 (Frontier Alignment):
       - 是否应用了近两年的主流范式（如：多模态、自监督 MAE、扩散模型、状态空间模型 MAMBA 等）？
       - 是否处于学术热点（如：分布外泛化 OOD、长尾分布处理）？
       
    3. 领域应用价值 (Domain Utility):
       - 针对目标研究领域，方案是否解决了明确且重要的实际痛点？
       - 是否能为领域专家提供可解释、可验证的洞察？
       
    4. 资源博弈可行性 (Execution Efficiency):
       - 实现难度 vs. 硬件成本。在单卡/低算力下能否复现？
       - 实验设计是否闭环，基准对比（Baseline）是否清晰？

    5. 学术影响力预测 (Scholarly Impact):
       - 预测该研究的长期学术贡献，是否可能成为基石性文献？
       - 是否具有社区塑造潜力，能引发深入讨论或跟进？
       
    输出 JSON 格式（严格遵循以下字段）:
    {
        "methodological_novelty": <浮点数, 0.0-10.0>,
        "frontier_alignment": <浮点数, 0.0-10.0>,
        "domain_utility": <浮点数, 0.0-10.0>,
        "execution_efficiency": <浮点数, 0.0-10.0>,
        "scholarly_impact": <浮点数, 0.0-10.0>,
        "critique": "<用中文给出专业、严谨、具有建设性的学术评审意见>",
        "key_innovation": "<简述该想法的核心创新点>",
        "strategic_advantage": "<简述该选题在当前学术竞争中的优势>",
        "frontier_background": "<描述该技术范式在当前 CV 领域的前沿背景>",
        "domain_painpoint": "<描述该研究针对的领域具体痛点>",
        "theoretical_outcome": "<预期的理论成果或范式改进>",
        "practical_performance": "<预计在实际数据集上能达到的性能或鲁棒性提升>",
        "decision": "<ACCEPT 或 REJECT>"
    }
""")
