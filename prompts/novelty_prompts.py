from string import Template

KEYWORDS_EXTRACTION_PROMPT = Template("""
    我有一个研究想法。请提取 3-5 个具体的英文搜索关键词（Search Keywords），用于在 OpenAlex/Google Scholar 上查找相关论文。
    
    标题: $title
    实验细节: $experiment
    
    仅返回一个 JSON 字符串列表，例如 ["keyword1", "keyword2"]
""")

NOVELTY_CHECK_PROMPT = Template("""
    你是一位顶级 AI 会议（CVPR/NeurIPS）的严格新颖性审查员。
    
    我的研究想法:
    标题: $title
    实验细节: $experiment
    
    找到的现有论文:
    $papers_context
    
    任务:
    将我的想法与现有论文进行比较。
    - 我的想法是否已经被这些论文中的任何一篇做过了？
    - 它是否只是一个微不足道的变体？
    
    输出 JSON 格式:
    {
        "novelty_score": <浮点数, 0.0-10.0, 例如 8.5, 0 表示完全重复, 10 表示开创性>,
        "reason": "<用中文简短解释，如果是重复的，请引用具体论文>"
    }
""")
