import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompts.impact_prompts import IMPACT_PREDICTION_PROMPT
from tools.llm import call_llm, extract_json_from_text
from errors import InvalidResponseError


def predict_impact(item, novelty_result, critic_result):
    """预测研究的长期学术影响力并验证必要字段。"""
    title = item.get("Title", "")
    experiment = item.get("Experiment", "")
    print(f"[Impact Predictor Agent] Predicting Scholarly Impact for: {title[:50]}...")

    prompt = IMPACT_PREDICTION_PROMPT.substitute(
        title=title,
        experiment=experiment,
        novelty_highlights=novelty_result.get("highlights", "N/A"),
        venue="Top Conference/Journal",
        domain="AI/ML",
    )
    result = extract_json_from_text(call_llm(prompt, json_mode=True))
    if not isinstance(result, dict) or "总体潜力评分" not in result:
        raise InvalidResponseError("影响力预测结果缺少总体潜力评分")
    return result
