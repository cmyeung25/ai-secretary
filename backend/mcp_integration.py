"""
MCP (Model Context Protocol) 集成模組
支持通過 SSE 連接到 MCP 服務器並將其工具集成到 LangChain Agent 中
"""

import json
import asyncio
import aiohttp
import sseclient
import requests
from typing import Dict, List, Any, Optional, Callable
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import threading
import queue
import time
from datetime import datetime

class MCPServerConfig(BaseModel):
    """MCP 服務器配置"""
    name: str = Field(description="服務器名稱")
    url: str = Field(description="SSE 連接 URL")
    auth_token: Optional[str] = Field(default=None, description="認證令牌")
    headers: Optional[Dict[str, str]] = Field(default=None, description="額外的 HTTP 頭")
    timeout: int = Field(default=30, description="連接超時時間（秒）")

class MCPTool(BaseModel):
    """MCP 工具定義"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    server_name: str

class MCPClient:
    """MCP 客戶端，處理與 MCP 服務器的通信"""
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.tools: Dict[str, MCPTool] = {}
        self.connection_active = False
        self.response_queue = queue.Queue()
        self.request_id_counter = 0
        self.pending_requests: Dict[str, queue.Queue] = {}
        
    def connect(self) -> bool:
        """連接到 MCP 服務器，Playwright MCP 僅使用 SSE，不請求 /tools"""
        headers = self.config.headers or {}
        if self.config.auth_token:
            headers['Authorization'] = f'Bearer {self.config.auth_token}'
        health_url = None
        if self.config.url.endswith('/events'):
            health_url = self.config.url.replace('/events', '/health')
        elif self.config.url.endswith('/sse'):
            health_url = self.config.url.replace('/sse', '/health')
        if health_url:
            try:
                response = requests.get(health_url, headers=headers, timeout=5)
                if response.status_code == 200:
                    print(f"✅ MCP 服務器健康檢查通過: {self.config.name}")
                else:
                    print(f"⚠️ MCP 服務器健康檢查失敗: {self.config.name} (狀態碼: {response.status_code})，繼續嘗試 SSE 連接")
            except Exception as e:
                print(f"⚠️ MCP 服務器健康檢查異常: {self.config.name} - {str(e)}，繼續嘗試 SSE 連接")
        try:
            self._start_sse_listener()
            # 只對非 Playwright MCP 服務器請求 /tools
            if self.config.name.lower() != "playwright":
                self._fetch_tools()
            self.connection_active = True
            print(f"✅ 成功連接到 MCP 服務器（SSE）: {self.config.name}")
            return True
        except Exception as e:
            print(f"❌ 連接 MCP 服務器（SSE）失敗: {self.config.name} - {str(e)}")
            return False
    
    def _start_sse_listener(self):
        """啟動 SSE 事件監聽器"""
        def sse_listener():
            try:
                headers = self.config.headers or {}
                if self.config.auth_token:
                    headers['Authorization'] = f'Bearer {self.config.auth_token}'
                
                response = requests.get(
                    self.config.url, 
                    headers=headers, 
                    stream=True,
                    timeout=self.config.timeout
                )
                
                client = sseclient.SSEClient(response)
                
                for event in client.events():
                    if event.data:
                        try:
                            data = json.loads(event.data)
                            self._handle_sse_event(data)
                        except json.JSONDecodeError:
                            print(f"⚠️ 無法解析 SSE 事件數據: {event.data}")
                            
            except Exception as e:
                print(f"❌ SSE 監聽器錯誤: {str(e)}")
                self.connection_active = False
        
        thread = threading.Thread(target=sse_listener, daemon=True)
        thread.start()
    
    def _handle_sse_event(self, data: Dict[str, Any]):
        """處理 SSE 事件"""
        event_type = data.get('type')
        request_id = data.get('request_id')
        
        if event_type == 'tool_response' and request_id:
            # 工具執行回應
            if request_id in self.pending_requests:
                self.pending_requests[request_id].put(data)
        elif event_type == 'tools_list':
            # 工具列表更新
            self._update_tools(data.get('tools', []))
        elif event_type == 'error':
            # 錯誤事件
            print(f"❌ MCP 服務器錯誤: {data.get('message', 'Unknown error')}")
    
    def _fetch_tools(self):
        """獲取可用工具列表"""
        try:
            headers = self.config.headers or {}
            if self.config.auth_token:
                headers['Authorization'] = f'Bearer {self.config.auth_token}'
            
            # 發送獲取工具列表的請求
            tools_url = self.config.url.replace('/events', '/tools')
            response = requests.get(tools_url, headers=headers, timeout=self.config.timeout)
            
            if response.status_code == 200:
                tools_data = response.json()
                self._update_tools(tools_data.get('tools', []))
            else:
                print(f"⚠️ 無法獲取工具列表: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 獲取工具列表失敗: {str(e)}")
    
    def _update_tools(self, tools_data: List[Dict[str, Any]]):
        """更新工具列表"""
        for tool_data in tools_data:
            tool = MCPTool(
                name=tool_data['name'],
                description=tool_data['description'],
                input_schema=tool_data.get('input_schema', {}),
                server_name=self.config.name
            )
            self.tools[tool.name] = tool
        
        print(f"📋 從 {self.config.name} 載入了 {len(self.tools)} 個工具")
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """執行 MCP 工具"""
        if not self.connection_active:
            return {"error": "MCP 服務器未連接"}
        
        if tool_name not in self.tools:
            return {"error": f"工具 '{tool_name}' 不存在"}
        
        try:
            # 生成請求 ID
            request_id = f"req_{self.request_id_counter}_{int(time.time())}"
            self.request_id_counter += 1
            
            # 創建回應隊列
            response_queue = queue.Queue()
            self.pending_requests[request_id] = response_queue
            
            # 發送工具執行請求
            request_data = {
                "type": "tool_call",
                "request_id": request_id,
                "tool_name": tool_name,
                "parameters": parameters
            }
            
            headers = self.config.headers or {}
            if self.config.auth_token:
                headers['Authorization'] = f'Bearer {self.config.auth_token}'
            headers['Content-Type'] = 'application/json'
            
            execute_url = self.config.url.replace('/events', '/execute')
            response = requests.post(
                execute_url, 
                json=request_data, 
                headers=headers,
                timeout=self.config.timeout
            )
            
            if response.status_code != 200:
                return {"error": f"工具執行請求失敗: {response.status_code}"}
            
            # 等待回應
            try:
                result = response_queue.get(timeout=30)  # 30秒超時
                return result.get('result', {"error": "無回應數據"})
            except queue.Empty:
                return {"error": "工具執行超時"}
            finally:
                # 清理請求
                if request_id in self.pending_requests:
                    del self.pending_requests[request_id]
                    
        except Exception as e:
            return {"error": f"工具執行失敗: {str(e)}"}
    
    def get_tools(self) -> Dict[str, MCPTool]:
        """獲取所有可用工具"""
        return self.tools.copy()
    
    def disconnect(self):
        """斷開連接"""
        self.connection_active = False
        print(f"🔌 已斷開與 MCP 服務器的連接: {self.config.name}")

class MCPLangChainTool(BaseTool):
    """將 MCP 工具包裝為 LangChain 工具"""
    
    name: str
    description: str
    mcp_client: MCPClient
    mcp_tool_name: str
    
    def __init__(self, mcp_tool: MCPTool, mcp_client: MCPClient, **kwargs):
        super().__init__(
            name=mcp_tool.name,
            description=mcp_tool.description,
            mcp_client=mcp_client,
            mcp_tool_name=mcp_tool.name,
            **kwargs
        )
    
    def _run(self, **kwargs) -> str:
        """執行 MCP 工具"""
        try:
            result = self.mcp_client.execute_tool(self.mcp_tool_name, kwargs)
            
            if "error" in result:
                return f"工具執行錯誤: {result['error']}"
            
            # 格式化結果
            if isinstance(result, dict):
                if "content" in result:
                    return str(result["content"])
                elif "message" in result:
                    return str(result["message"])
                else:
                    return json.dumps(result, ensure_ascii=False, indent=2)
            else:
                return str(result)
                
        except Exception as e:
            return f"工具執行異常: {str(e)}"

class MCPManager:
    """MCP 管理器，管理多個 MCP 服務器連接"""
    
    def __init__(self):
        self.clients: Dict[str, MCPClient] = {}
        self.langchain_tools: List[MCPLangChainTool] = []
    
    def add_server(self, config: MCPServerConfig) -> bool:
        """添加 MCP 服務器"""
        if config.name in self.clients:
            print(f"⚠️ MCP 服務器 '{config.name}' 已存在")
            return False
        
        client = MCPClient(config)
        if client.connect():
            self.clients[config.name] = client
            self._create_langchain_tools(client)
            return True
        return False
    
    def _create_langchain_tools(self, client: MCPClient):
        """為 MCP 客戶端創建 LangChain 工具"""
        for tool_name, mcp_tool in client.get_tools().items():
            langchain_tool = MCPLangChainTool(mcp_tool, client)
            self.langchain_tools.append(langchain_tool)
    
    def get_all_tools(self) -> List[MCPLangChainTool]:
        """獲取所有 LangChain 工具"""
        return self.langchain_tools.copy()
    
    def get_server_tools(self, server_name: str) -> List[MCPLangChainTool]:
        """獲取特定服務器的工具"""
        if server_name not in self.clients:
            return []
        
        return [tool for tool in self.langchain_tools 
                if tool.mcp_client.config.name == server_name]
    
    def disconnect_all(self):
        """斷開所有連接"""
        for client in self.clients.values():
            client.disconnect()
        self.clients.clear()
        self.langchain_tools.clear()
    
    def get_status(self) -> Dict[str, Any]:
        """獲取所有服務器的狀態"""
        status = {}
        for name, client in self.clients.items():
            status[name] = {
                "connected": client.connection_active,
                "tools_count": len(client.tools),
                "url": client.config.url
            }
        return status

# 使用示例
def create_mcp_manager_with_servers(server_configs: List[Dict[str, Any]]) -> MCPManager:
    """創建 MCP 管理器並連接服務器"""
    manager = MCPManager()
    
    for config_dict in server_configs:
        config = MCPServerConfig(**config_dict)
        manager.add_server(config)
    
    return manager

# 配置示例
EXAMPLE_MCP_SERVERS = [
    {
        "name": "file_server",
        "url": "http://localhost:3001/events",
        "auth_token": "your_token_here",
        "headers": {"X-Custom-Header": "value"}
    },
    {
        "name": "database_server", 
        "url": "http://localhost:3002/events",
        "timeout": 60
    }
]

