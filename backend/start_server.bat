@echo off
echo ========================================
echo        AI 秘書服務器啟動腳本
echo ========================================
echo.

REM 檢查 Python 是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：未找到 Python，請先安裝 Python 3.8+
    pause
    exit /b 1
)

REM 檢查是否在正確目錄
if not exist "src\main.py" (
    echo ❌ 錯誤：請在 ai_secretary_backend 目錄中運行此腳本
    pause
    exit /b 1
)

REM 檢查 .env 文件
if not exist ".env" (
    echo ⚠️  警告：未找到 .env 文件
    echo 請創建 .env 文件並配置以下內容：
    echo.
    echo GOOGLE_API_KEY=your_google_api_key_here
    echo NEO4J_URI=neo4j://localhost:7687
    echo NEO4J_USER=neo4j
    echo NEO4J_PASSWORD=your_neo4j_password_here
    echo.
    pause
    exit /b 1
)

echo 🔧 檢查並安裝依賴...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ 依賴安裝失敗
    pause
    exit /b 1
)

echo.
echo 🚀 啟動 AI 秘書服務器...
echo 服務器將在 http://localhost:5001 啟動
echo 按 Ctrl+C 停止服務器
echo.

python src\main.py

echo.
echo 👋 服務器已停止
pause

