import sys
import os
import json

# 添加父目录到 path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from tools.llm import call_llm, extract_json_from_text
from tools.openalex import search_papers
from prompts.novelty_prompts import KEYWORDS_EXTRACTION_PROMPT, NOVELTY_CHECK_PROMPT

def check_novelty(item):
    """
    Step 1: 查重 Agent
    """
    title = item.get("Title", "")
    experiment = item.get("Experiment", "")
    
    print(f"\n[Novelty Agent] Processing: {title[:50]}...")
    
    # 1. 提取关键词
    prompt_keywords = KEYWORDS_EXTRACTION_PROMPT.substitute(
        title=title,
        experiment=experiment
    )
    
    keywords_json = call_llm(prompt_keywords, json_mode=True)
    keywords = extract_json_from_text(keywords_json)
    
    if not keywords or not isinstance(keywords, list):
        keywords = [title] # Fallback
        
    print(f"  -> Keywords: {keywords}")
    
    # 2. 搜索论文 (使用前3个关键词组合，或者只用 Title)
    # 为了提高召回率，我们构建一个查询字符串
    query = " ".join(keywords[:3])
    papers = search_papers(query, limit=5)
    
    if not papers:
        print("  -> No similar papers found (OpenAlex returned empty). Assuming Novel.")
        return {
            "novelty_score": 8,
            "novelty_reason": "No similar papers found in search.",
            "similar_papers": []
        }
        
    # 3. LLM 判决
    papers_context = ""
    for i, p in enumerate(papers):
        papers_context += f"[{i+1}] {p['title']} ({p['publication_year']})\nAbstract: {p['abstract']}\n\n"
        
    prompt_check = NOVELTY_CHECK_PROMPT.substitute(
        title=title,
        experiment=experiment,
        papers_context=papers_context
    )
    
    result_json = call_llm(prompt_check, json_mode=True)
    result = extract_json_from_text(result_json)
    
    if not result:
        print(f"[Novelty] Error: Failed to parse JSON. Raw: {result_json}")
        return {
            "novelty_score": 0,
            "novelty_reason": "系统错误：LLM 未能生成有效的 JSON 响应。",
            "similar_papers": []
        }
    
    return {
        "novelty_score": result.get("novelty_score", 5),
        "novelty_reason": result.get("reason", "Analysis failed"),
        "similar_papers": papers
    }
