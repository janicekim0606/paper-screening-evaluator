import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from prompts.novelty_prompts import KEYWORDS_EXTRACTION_PROMPT, NOVELTY_CHECK_PROMPT
from tools.llm import call_llm, extract_json_from_text
from tools.openalex import search_papers
from errors import InvalidResponseError


def check_novelty(item):
    """检索相似论文并返回结构化新颖性评估。"""
    title = item.get("Title", "")
    experiment = item.get("Experiment", "")
    print(f"\n[Novelty Agent] Processing: {title[:50]}...")

    prompt_keywords = KEYWORDS_EXTRACTION_PROMPT.substitute(
        title=title,
        experiment=experiment,
    )
    keywords = extract_json_from_text(call_llm(prompt_keywords, json_mode=True))
    if not isinstance(keywords, list) or not keywords:
        raise InvalidResponseError("关键词提取结果必须是非空数组")

    query = " ".join(str(keyword) for keyword in keywords[:3])
    print(f"  -> Keywords: {keywords}")
    search_result = search_papers(query, limit=config.OPENALEX_LIMIT)
    papers = search_result.papers
    if not papers:
        print("  -> OpenAlex 检索成功但没有返回相似论文，无法据此确认新颖性。")

    papers_context = "".join(
        f"[{index}] {paper['title']} ({paper['publication_year']})\n"
        f"Abstract: {paper['abstract']}\n\n"
        for index, paper in enumerate(papers, start=1)
    )
    prompt_check = NOVELTY_CHECK_PROMPT.substitute(
        title=title,
        experiment=experiment,
        papers_context=papers_context,
    )
    result = extract_json_from_text(call_llm(prompt_check, json_mode=True))
    if not isinstance(result, dict) or "novelty_score" not in result:
        raise InvalidResponseError("新颖性评估结果缺少 novelty_score")

    return {
        "novelty_score": result["novelty_score"],
        "novelty_reason": result.get("reason", "未提供分析理由"),
        "similar_papers": papers,
    }
