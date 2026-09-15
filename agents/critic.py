import sys
import os

# 添加父目录到 path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from tools.llm import call_llm, extract_json_from_text
from prompts.critic_prompts import CRITIC_REVIEW_PROMPT
from errors import InvalidResponseError

def review_idea(item, novelty_result):
    """
    Step 2: 毒舌评论员 (The Critic)
    使用四维评估体系进行深度评审
    """
    title = item.get("Title", "")
    experiment = item.get("Experiment", "")
    methodological_novelty = novelty_result.get("novelty_score") # 从查重阶段继承新颖性分数
    
    print(f"[Critic Agent] Reviewing with 4D Matrix: {title[:50]}...")
    
    prompt = CRITIC_REVIEW_PROMPT.substitute(
        title=title,
        experiment=experiment,
        methodological_novelty=methodological_novelty,
        novelty_reason=novelty_result.get('novelty_reason')
    )
    
    result_json = call_llm(prompt, json_mode=True)
    result = extract_json_from_text(result_json)
    
    if not result:
        print(f"[Critic] Error: Failed to parse JSON. Raw: {result_json}")
        raise InvalidResponseError("综合评审返回了无效 JSON")
    
    print(f"  -> Evaluation Result: MN={result.get('methodological_novelty')}, FA={result.get('frontier_alignment')}, DU={result.get('domain_utility')}, EE={result.get('execution_efficiency')}")
    return result
