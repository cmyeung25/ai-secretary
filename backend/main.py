import os
from dotenv import load_dotenv

# 載入環境變數，確保在任何模組導入之前執行
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from agent_core import create_agent, get_agent_prompt
from memory_manager import MemoryManager
from tools import get_all_tools
from mcp_integration import MCPManager
from mcp_config import get_mcp_servers_config, get_mcp_settings
import uuid
import google.generativeai as genai

# 配置 Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 顯式禁用 Application Default Credentials (ADC)
os.environ["GOOGLE_API_USE_ADC"] = "False"

class AISecretary:
    """AI 秘書主類別。"""
    
    def __init__(self):
        # 初始化 LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.1,
            google_api_key=os.getenv("GOOGLE_API_KEY") # 確保 API Key 被傳遞
        )
        
        # 初始化記憶管理器
        self.memory_manager = MemoryManager(
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            neo4j_uri=os.getenv("NEO4J_URI", "neo4j://localhost:7687"),
            neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
            neo4j_password=os.getenv("NEO4J_PASSWORD", "password")
        )
        
        # 初始化 MCP 管理器
        self.mcp_manager = None
        self._setup_mcp()
        
        # 初始化工具
        self.tools = self._get_all_tools()
        
        # 初始化 Agent
        self.agent = create_agent(self.llm, self.tools, get_agent_prompt(self.tools))
        
        # 會話 ID
        self.session_id = str(uuid.uuid4())
    
    def _setup_mcp(self):
        """設置 MCP 連接"""
        mcp_settings = get_mcp_settings()
        
        if not mcp_settings.get("enable_mcp", False):
            print("📋 MCP 功能已禁用")
            return
        
        try:
            self.mcp_manager = MCPManager()
            server_configs = get_mcp_servers_config()
            
            if not server_configs:
                print("📋 未配置 MCP 服務器")
                return
            
            print(f"🔌 正在連接 {len(server_configs)} 個 MCP 服務器...")
            
            connected_count = 0
            for config in server_configs:
                from mcp_integration import MCPServerConfig
                server_config = MCPServerConfig(**config)
                if self.mcp_manager.add_server(server_config):
                    connected_count += 1
            
            if connected_count > 0:
                mcp_tools = self.mcp_manager.get_all_tools()
                print(f"✅ 成功連接 {connected_count} 個 MCP 服務器，載入 {len(mcp_tools)} 個工具")
            else:
                print("⚠️ 未能連接任何 MCP 服務器")
                self.mcp_manager = None
                
        except Exception as e:
            print(f"❌ MCP 設置失敗: {str(e)}")
            self.mcp_manager = None
    
    def _get_all_tools(self):
        """獲取所有可用工具（包括 MCP 工具）"""
        # 獲取基本工具
        tools = get_all_tools(self.memory_manager)
        
        # 添加 MCP 工具
        if self.mcp_manager:
            mcp_tools = self.mcp_manager.get_all_tools()
            tools.extend(mcp_tools)
            print(f"🔧 總共載入 {len(tools)} 個工具（包括 {len(mcp_tools)} 個 MCP 工具）")
        else:
            print(f"🔧 總共載入 {len(tools)} 個基本工具")
        
        return tools
    
    def chat(self, user_input: str) -> str:
        """與 AI 秘書對話。"""
        try:
            # 記錄用戶輸入
            self.memory_manager.process_message(self.session_id, "user", user_input)
            
            # 獲取 AI 回覆
            response = self.agent.invoke({"input": user_input})
            ai_response = response["output"]
            
            # 記錄 AI 回覆
            self.memory_manager.process_message(self.session_id, "assistant", ai_response)
            
            return ai_response
        
        except Exception as e:
            error_msg = f"處理請求時發生錯誤：{str(e)}"
            print(error_msg)
            return error_msg
    
    def get_mcp_status(self) -> dict:
        """獲取 MCP 服務器狀態"""
        if not self.mcp_manager:
            return {"enabled": False, "servers": {}}
        
        return {
            "enabled": True,
            "servers": self.mcp_manager.get_status()
        }
    
    def close(self):
        """關閉 AI 秘書。"""
        self.memory_manager.close()
        if self.mcp_manager:
            self.mcp_manager.disconnect_all()

def main():
    """主函數。"""
    print("🤖 AI 秘書已啟動！")
    print("輸入 'quit' 或 'exit' 退出程式。")
    print("輸入 '[記住] 內容' 來明確標記重要資訊。")
    print("輸入 'mcp status' 查看 MCP 服務器狀態。")
    print("-" * 50)
    
    # 創建 AI 秘書實例
    secretary = AISecretary()
    
    try:
        while True:
            # 獲取用戶輸入
            user_input = input("\n您: ").strip()
            
            # 檢查退出條件
            if user_input.lower() in ["quit", "exit", "退出", "結束"]:
                print("👋 再見！")
                break
            
            # 檢查 MCP 狀態命令
            if user_input.lower() == "mcp status":
                status = secretary.get_mcp_status()
                print(f"\n📊 MCP 狀態: {status}")
                continue
            
            if not user_input:
                continue
            
            # 獲取 AI 回覆
            print("\n🤖 AI 秘書: ", end="")
            response = secretary.chat(user_input)
            print(response)
    
    except KeyboardInterrupt:
        print("\n\n👋 程式已中斷，再見！")
    
    finally:
        # 關閉連接
        secretary.close()

if __name__ == "__main__":
    main()

