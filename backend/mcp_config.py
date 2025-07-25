"""
MCP 服務器配置文件
在這裡配置您的 MCP 服務器連接信息
"""

import os
from typing import List, Dict, Any

def get_mcp_servers_config() -> List[Dict[str, Any]]:
    """
    獲取 MCP 服務器配置
    您可以在這裡添加您的 MCP 服務器配置
    """
    
    # 從環境變數讀取配置
    servers = []
    
    # 示例配置 1: 文件系統服務器
    if os.getenv("MCP_FILE_SERVER_URL"):
        servers.append({
            "name": "file_server",
            "url": os.getenv("MCP_FILE_SERVER_URL"),
            "auth_token": os.getenv("MCP_FILE_SERVER_TOKEN"),
            "headers": {
                "X-Client-Name": "AI-Secretary"
            },
            "timeout": 30
        })
    
    # 示例配置 2: 數據庫服務器
    if os.getenv("MCP_DATABASE_SERVER_URL"):
        servers.append({
            "name": "database_server", 
            "url": os.getenv("MCP_DATABASE_SERVER_URL"),
            "auth_token": os.getenv("MCP_DATABASE_SERVER_TOKEN"),
            "timeout": 60
        })
    
    # 示例配置 3: API 服務器
    if os.getenv("MCP_API_SERVER_URL"):
        servers.append({
            "name": "api_server",
            "url": os.getenv("MCP_API_SERVER_URL"),
            "auth_token": os.getenv("MCP_API_SERVER_TOKEN"),
            "headers": {
                "X-API-Version": "v1",
                "X-Client-Name": "AI-Secretary"
            },
            "timeout": 45
        })
    
    # 硬編碼配置示例（用於測試）
    # 取消註釋並修改以下配置來添加您的 MCP 服務器
    """
    servers.extend([
        {
            "name": "my_mcp_server",
            "url": "http://localhost:3001/events",
            "auth_token": "your_auth_token_here",
            "headers": {
                "X-Custom-Header": "custom_value"
            },
            "timeout": 30
        },
        {
            "name": "another_server",
            "url": "https://your-mcp-server.com/sse",
            "auth_token": "another_token",
            "timeout": 60
        }
    ])
    """
    
    return servers

def get_mcp_settings() -> Dict[str, Any]:
    """
    獲取 MCP 全局設置
    """
    return {
        "enable_mcp": os.getenv("ENABLE_MCP", "false").lower() == "true",
        "auto_reconnect": os.getenv("MCP_AUTO_RECONNECT", "true").lower() == "true",
        "max_reconnect_attempts": int(os.getenv("MCP_MAX_RECONNECT_ATTEMPTS", "3")),
        "reconnect_delay": int(os.getenv("MCP_RECONNECT_DELAY", "5")),  # 秒
        "health_check_interval": int(os.getenv("MCP_HEALTH_CHECK_INTERVAL", "60"))  # 秒
    }

# 環境變數配置說明
"""
在您的 .env 文件中添加以下配置來啟用 MCP 集成：

# 啟用 MCP 功能
ENABLE_MCP=true

# MCP 服務器配置
MCP_FILE_SERVER_URL=http://localhost:3001/events
MCP_FILE_SERVER_TOKEN=your_file_server_token

MCP_DATABASE_SERVER_URL=http://localhost:3002/events  
MCP_DATABASE_SERVER_TOKEN=your_database_server_token

MCP_API_SERVER_URL=https://your-api-server.com/sse
MCP_API_SERVER_TOKEN=your_api_server_token

# MCP 設置
MCP_AUTO_RECONNECT=true
MCP_MAX_RECONNECT_ATTEMPTS=3
MCP_RECONNECT_DELAY=5
MCP_HEALTH_CHECK_INTERVAL=60
"""

