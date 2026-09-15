import json
import os

def load_data(file_path):
    """加载 JSON 数据文件"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"[Data] Loaded {len(data)} items from {file_path}")
    return data

def save_report(title, content, output_dir):
    """保存 Markdown 报告"""
    os.makedirs(output_dir, exist_ok=True)
    # 清理文件名
    safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    safe_title = safe_title.replace(" ", "_")
    
    filename = f"{safe_title}.md"
    path = os.path.join(output_dir, filename)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[Report] Saved to {path}")
