# /backend/src/env_loader.py
import os
from pathlib import Path
from dotenv import load_dotenv

def load_environment_variables():
    """从项目根目录加载.env文件"""
    # 获取当前文件的绝对路径
    current_dir = Path(__file__).resolve().parent
    
    # 计算项目根目录路径（向上回溯两级到backend/src的父目录）
    project_root = current_dir.parent.parent
    
    # 构建.env文件的完整路径
    env_path = project_root / '.env'
    
    # 检查文件是否存在并加载
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"✅ 从 {env_path} 成功加载环境变量")
    else:
        print(f"⚠️ 警告: 未找到.env文件在 {env_path}")
    
    # 返回根目录路径（可选）
    return project_root

# 调用函数加载环境变量
PROJECT_ROOT = load_environment_variables()