import json
import hashlib
import os
import re

from errors import InputValidationError


def sanitize_report_filename(title):
    """生成带稳定短哈希的跨平台报告文件名主体。"""
    original_title = str(title)
    safe_title = "".join(
        character for character in original_title
        if character.isalnum() or character in " _-"
    )
    safe_title = re.sub(r"\s+", "_", safe_title).strip("._")
    readable_title = safe_title[:110] or "untitled"
    title_hash = hashlib.sha256(original_title.encode("utf-8")).hexdigest()[:10]
    return f"{readable_title}_{title_hash}"


def load_data(file_path):
    """加载并校验 JSON 输入数据。"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise InputValidationError("输入 JSON 顶层必须是数组")
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise InputValidationError(f"第 {index + 1} 条输入必须是对象")
        if not str(item.get("Title", "")).strip():
            raise InputValidationError(f"第 {index + 1} 条输入缺少 Title")
        if not str(item.get("Experiment", "")).strip():
            raise InputValidationError(f"第 {index + 1} 条输入缺少 Experiment")

    print(f"[Data] Loaded {len(data)} items from {file_path}")
    return data


def save_report(title, content, output_dir):
    """保存 Markdown 报告。"""
    os.makedirs(output_dir, exist_ok=True)
    safe_title = sanitize_report_filename(title)
    path = os.path.join(output_dir, f"{safe_title}.md")

    with open(path, "w", encoding="utf-8") as file:
        file.write(content)

    print(f"[Report] Saved to {path}")
