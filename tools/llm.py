from openai import OpenAI
import sys
import os
import json

# 添加父目录到 path 以便导入 config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def get_client():
    """获取 OpenAI 客户端 (配置为 DeepSeek)"""
    if not config.DEEPSEEK_API_KEY or "your-key" in config.DEEPSEEK_API_KEY:
        raise ValueError("请通过 .env 或系统环境变量配置 DEEPSEEK_API_KEY")
    
    return OpenAI(
        api_key=config.DEEPSEEK_API_KEY,
        base_url=config.DEEPSEEK_BASE_URL
    )

def call_llm(prompt, system_prompt="You are a helpful research assistant.", json_mode=False):
    """
    调用 LLM 生成回复
    :param prompt: 用户提示词
    :param system_prompt: 系统提示词
    :param json_mode: 是否强制返回 JSON 格式
    :return: 响应文本
    """
    client = get_client()
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    try:
        response = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=messages,
            response_format={"type": "json_object"} if json_mode else {"type": "text"},
            temperature=0.3 if json_mode else config.LLM_TEMPERATURE,
            max_tokens=4096,
            timeout=config.LLM_TIMEOUT
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[LLM] Error calling API: {e}")
        return None

def extract_json_from_text(text):
    """尝试从文本中提取 JSON"""
    if not text:
        return None
        
    try:
        # 如果返回的就是纯 JSON
        return json.loads(text)
    except json.JSONDecodeError:
        # 尝试查找 ```json 代码块
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            json_str = text[start:end].strip()
            try:
                return json.loads(json_str)
            except:
                pass
        # 尝试查找 { ... }
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end])
            except:
                pass
        return None
