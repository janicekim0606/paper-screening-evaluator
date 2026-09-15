import os
import yaml
from dotenv import load_dotenv

# 1. 加载环境变量 (.env) - 优先级最高，用于敏感信息
load_dotenv()

# 2. 加载配置文件 (config.yaml) - 用于通用设置
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")
try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        _config = yaml.safe_load(f)
except FileNotFoundError:
    print(f"[Config] Warning: config.yaml not found at {CONFIG_PATH}. Using defaults.")
    _config = {}

# --- Helper to get config value ---
def get_conf(path, default=None):
    """从 _config 字典中安全获取嵌套值，例如 'api.deepseek_key'"""
    keys = path.split('.')
    val = _config
    for k in keys:
        if isinstance(val, dict):
            val = val.get(k)
        else:
            return default
    return val if val is not None else default

# --- Configuration Variables ---

# 密钥只允许通过环境变量提供，避免误提交到版本库。
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = get_conf("api.deepseek_base_url", "https://api.deepseek.com")
OPENALEX_EMAIL = os.getenv("OPENALEX_EMAIL")

# LLM Settings
LLM_MODEL = get_conf("llm.model_name", "deepseek-chat")
LLM_TEMPERATURE = float(get_conf("llm.temperature", 0.7))
LLM_TIMEOUT = int(get_conf("llm.timeout", 120))

# Thresholds
THRESHOLD_NOVELTY = float(get_conf("thresholds.novelty", 7.0))
THRESHOLD_FRONTIER = float(get_conf("thresholds.frontier_alignment", 7.0))
THRESHOLD_UTILITY = float(get_conf("thresholds.domain_utility", 7.5))
THRESHOLD_EFFICIENCY = float(get_conf("thresholds.execution_efficiency", 6.0))
THRESHOLD_IMPACT = float(get_conf("thresholds.scholarly_impact", 6.5))

# Weights
WEIGHT_MN = float(get_conf("weights.methodological_novelty", 1.5))
WEIGHT_FA = float(get_conf("weights.frontier_alignment", 1.5))
WEIGHT_DU = float(get_conf("weights.domain_utility", 2.0))
WEIGHT_EE = float(get_conf("weights.execution_efficiency", 1.0))
WEIGHT_SI = float(get_conf("weights.scholarly_impact", 1.0))

# Execution Settings
MAX_ITEMS_TO_PROCESS = int(get_conf("execution.max_items_to_process", 60))
TARGET_ACCEPTED_COUNT = int(get_conf("execution.target_accepted_count", 3))
SAVE_REJECTED = get_conf("execution.save_rejected", True)

# Validation
if not DEEPSEEK_API_KEY:
    print("[Config] Warning: DEEPSEEK_API_KEY is missing! Please set it in .env or the environment.")

