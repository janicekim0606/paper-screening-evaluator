import os
import sys
import json
from string import Template

# 添加父目录到 path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.llm import call_llm, extract_json_from_text
from prompts.impact_prompts import IMPACT_PREDICTION_PROMPT
from errors import InvalidResponseError

def predict_impact(item, novelty_result, critic_result):
    """
    New Agent: 学术影响力预测 (Scholarly Impact Predictor)
    负责预测研究的长期学术影响力
    """
    title = item.get("Title", "")
    experiment = item.get("Experiment", "")
    novelty_highlights = novelty_result.get("highlights", "N/A")
    venue = "Top Conference/Journal" # Placeholder, can be dynamic
    domain = "AI/ML"  # Placeholder, can be made configurable
    
    print(f"[Impact Predictor Agent] Predicting Scholarly Impact for: {title[:50]}...")
    
    prompt = IMPACT_PREDICTION_PROMPT.substitute(
        title=title,
        experiment=experiment,
        novelty_highlights=novelty_highlights,
        venue=venue,
        domain=domain
    )
    
    impact_content = call_llm(prompt, json_mode=True)
    
    impact_result = extract_json_from_text(impact_content)
    if not isinstance(impact_result, dict):
        raise InvalidResponseError(f"学术影响力预测返回了无效 JSON: {title}")
    return impact_result

