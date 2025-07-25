# AI 秘書部署指南

## 🚀 快速啟動

### 1. 後端設置

#### 安裝 Python 依賴
```bash
cd ai_secretary_backend
pip install -r requirements.txt
```

#### 配置環境變數
創建 `.env` 文件並填入以下內容：
```bash
# Google API 設定
GOOGLE_API_KEY=your_google_api_key_here

# Neo4j 數據庫設定
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password_here

# MCP 設定（可選）
ENABLE_MCP=false
```

#### 啟動後端服務
```bash
python src/main.py
```
服務將在 `http://localhost:5001` 啟動

### 2. 前端設置

#### 安裝 Node.js 依賴
```bash
cd ai_secretary_frontend
npm install
```

#### 構建前端
```bash
npm run build
```

#### 部署前端到後端
```bash
# Windows
xcopy /E /I dist\* ..\ai_secretary_backend\src\static\

# macOS/Linux
cp -r dist/* ../ai_secretary_backend/src/static/
```

### 3. 訪問應用
打開瀏覽器訪問：`http://localhost:5001`

## 🔧 詳細配置

### Neo4j 數據庫設置

1. **下載並安裝 Neo4j**
   - 訪問 [Neo4j 官網](https://neo4j.com/download/)
   - 下載 Neo4j Desktop 或 Community Edition

2. **啟動 Neo4j**
   - 創建新的數據庫實例
   - 設置用戶名和密碼
   - 啟動數據庫服務

3. **配置連接**
   - 默認 URI: `neo4j://localhost:7687`
   - 默認用戶名: `neo4j`
   - 密碼: 您設置的密碼

### Google API Key 獲取

1. **訪問 Google Cloud Console**
   - 前往 [Google Cloud Console](https://console.cloud.google.com/)

2. **啟用 Generative AI API**
   - 搜索並啟用 "Generative Language API"

3. **創建 API Key**
   - 前往 "憑證" 頁面
   - 點擊 "創建憑證" > "API 金鑰"
   - 複製生成的 API Key

### MCP 服務器集成（可選）

如果您有 MCP 服務器，可以在 `.env` 中配置：
```bash
ENABLE_MCP=true
MCP_FILE_SERVER_URL=http://localhost:3001/events
MCP_FILE_SERVER_TOKEN=your_token
```

## 🐛 故障排除

### 常見問題

1. **Neo4j 連接失敗**
   - 確保 Neo4j 服務正在運行
   - 檢查 URI、用戶名和密碼是否正確
   - 確認防火牆沒有阻擋 7687 端口

2. **Google API 錯誤**
   - 確認 API Key 正確
   - 檢查 Generative Language API 是否已啟用
   - 確認 API 配額沒有超限

3. **前端無法訪問**
   - 確認後端服務正在運行
   - 檢查前端文件是否正確複製到 `src/static/`
   - 清除瀏覽器緩存

4. **依賴安裝失敗**
   - 確認 Python 版本 >= 3.8
   - 確認 Node.js 版本 >= 16
   - 嘗試使用虛擬環境

### 日誌查看

後端日誌會顯示在終端中，包括：
- 服務啟動信息
- API 請求日誌
- 錯誤信息
- MCP 連接狀態

## 🔒 安全注意事項

1. **保護 API Key**
   - 不要將 `.env` 文件提交到版本控制
   - 定期輪換 API Key

2. **數據庫安全**
   - 使用強密碼
   - 限制網絡訪問
   - 定期備份數據

3. **生產部署**
   - 使用 HTTPS
   - 配置防火牆
   - 設置監控和日誌

## 📊 功能測試

啟動後，您可以測試以下功能：

1. **基本對話**
   ```
   你好！
   ```

2. **記憶功能**
   ```
   [記住] 我的生日是 10 月 26 日
   搜索我的生日
   ```

3. **MCP 狀態**（如果啟用）
   ```
   mcp status
   ```

## 🚀 生產部署

### 使用 Docker（推薦）

1. **創建 Dockerfile**
2. **配置 docker-compose.yml**
3. **部署到雲服務**

### 手動部署

1. **配置反向代理**（Nginx/Apache）
2. **設置 SSL 證書**
3. **配置進程管理**（PM2/Supervisor）

## 📞 支持

如果遇到問題，請檢查：
1. 日誌輸出
2. 網絡連接
3. 配置文件
4. 依賴版本

需要幫助時，請提供詳細的錯誤信息和環境配置。

