import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompts.critic_prompts import CRITIC_REVIEW_PROMPT
from tools.llm import call_llm, extract_json_from_text
from errors import InvalidResponseError


def review_idea(item, novelty_result):
    """使用四维评估体系对研究思路进行评审。"""
    title = item.get("Title", "")
    experiment = item.get("Experiment", "")
    methodological_novelty = novelty_result.get("novelty_score")
    print(f"[Critic Agent] Reviewing with 4D Matrix: {title[:50]}...")

    prompt = CRITIC_REVIEW_PROMPT.substitute(
        title=title,
        experiment=experiment,
        methodological_novelty=methodological_novelty,
        novelty_reason=novelty_result.get("novelty_reason"),
    )
    result = extract_json_from_text(call_llm(prompt, json_mode=True))
    required = (
        "methodological_novelty",
        "frontier_alignment",
        "domain_utility",
        "execution_efficiency",
    )
    if not isinstance(result, dict) or any(key not in result for key in required):
        raise InvalidResponseError("评审结果缺少必要评分维度")

    print(
        "  -> Evaluation Result: "
        f"MN={result['methodological_novelty']}, "
        f"FA={result['frontier_alignment']}, "
        f"DU={result['domain_utility']}, "
        f"EE={result['execution_efficiency']}"
    )
    return result
