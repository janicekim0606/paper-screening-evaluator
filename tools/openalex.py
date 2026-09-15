import pyalex
from pyalex import Works
import sys
import os
from dataclasses import dataclass

# 添加父目录到 path 以便导入 config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from errors import ExternalServiceError


@dataclass(frozen=True)
class SearchResult:
    papers: list[dict]
    query: str

def init_openalex():
    """初始化 OpenAlex 配置"""
    if config.OPENALEX_EMAIL and "example.com" not in config.OPENALEX_EMAIL:
        pyalex.config.email = config.OPENALEX_EMAIL
        print("[OpenAlex] 已启用 Polite Pool")
    else:
        print("[OpenAlex] 未配置有效邮箱，使用默认公共池 (速度较慢)")

def search_papers(query, limit=5):
    """
    在 OpenAlex 中搜索论文
    :param query: 搜索关键词字符串
    :param limit: 返回结果数量
    :return: 论文列表 (包含 title, abstract, year, cited_by_count, id)
    """
    try:
        # 初始化
        init_openalex()
        
        print(f"[OpenAlex] Searching for: {query}...")
        
        # 执行搜索
        # 使用 search_filter 进行全文/摘要搜索，并按相关性排序
        results = (
            Works()
            .search(query)
            .filter(from_publication_date="2020-01-01") # 仅搜索 2020 年以后的论文，保证时效性
            .get(return_meta=False, per_page=limit)
        )
        
        papers = []
        for work in results:
            # OpenAlex 的摘要通常是倒排索引格式 (AbstractInvertedIndex)，pyalex 会自动处理吗？
            # pyalex 返回的 dict 中，abstract_inverted_index 需要重组，或者直接看是否有 abstract 字段
            # 注意：OpenAlex API 默认返回 abstract_inverted_index，需要手动还原文本
            
            abstract_text = "No abstract available."
            if work.get("abstract_inverted_index"):
                # 简单的还原逻辑
                index = work["abstract_inverted_index"]
                if index:
                    # 创建一个长度足够的列表
                    max_len = max([max(positions) for positions in index.values()]) + 1
                    words = [""] * max_len
                    for word, positions in index.items():
                        for pos in positions:
                            words[pos] = word
                    abstract_text = " ".join(words)
            
            papers.append({
                "id": work.get("id"),
                "title": work.get("title"),
                "publication_year": work.get("publication_year"),
                "cited_by_count": work.get("cited_by_count"),
                "abstract": abstract_text[:1500] + "..." if len(abstract_text) > 1500 else abstract_text, # 截断过长摘要
                "doi": work.get("doi"),
                "landing_page_url": work.get("landing_page_url")
            })
            
        return SearchResult(papers=papers, query=query)

    except Exception as e:
        raise ExternalServiceError(f"OpenAlex 检索失败: {e}") from e
