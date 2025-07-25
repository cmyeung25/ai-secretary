#!/bin/bash

echo "========================================"
echo "       AI 秘書服務器啟動腳本"
echo "========================================"
echo

# 檢查 Python 是否安裝
if ! command -v python3 &> /dev/null; then
    echo "❌ 錯誤：未找到 Python3，請先安裝 Python 3.8+"
    exit 1
fi

# 檢查是否在正確目錄
if [ ! -f "src/main.py" ]; then
    echo "❌ 錯誤：請在 ai_secretary_backend 目錄中運行此腳本"
    exit 1
fi

# 檢查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  警告：未找到 .env 文件"
    echo "請創建 .env 文件並配置以下內容："
    echo
    echo "GOOGLE_API_KEY=your_google_api_key_here"
    echo "NEO4J_URI=neo4j://localhost:7687"
    echo "NEO4J_USER=neo4j"
    echo "NEO4J_PASSWORD=your_neo4j_password_here"
    echo
    exit 1
fi

echo "🔧 檢查並安裝依賴..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ 依賴安裝失敗"
    exit 1
fi

echo
echo "🚀 啟動 AI 秘書服務器..."
echo "服務器將在 http://localhost:5001 啟動"
echo "按 Ctrl+C 停止服務器"
echo

python3 src/main.py

echo
echo "👋 服務器已停止"

