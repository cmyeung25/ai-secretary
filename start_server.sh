#!/bin/bash

# 檢查 Python 是否安裝
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not found. Please install Python 3."
    echo "On Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo "On macOS: brew install python3"
    exit 1
fi

# 進入後端目錄
cd backend

# 檢查虛擬環境是否存在，如果不存在則創建
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
fi

# 激活虛擬環境
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment."
    exit 1
fi

# 安裝依賴
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install Python dependencies."
    exit 1
fi

# 啟動 Flask 服務器
echo "Starting AI Secretary backend server..."
python src/main.py

