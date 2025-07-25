from langchain.tools import BaseTool
from typing import Optional, Type, Any
from pydantic import BaseModel, Field
import datetime
import json

class CalendarSearchInput(BaseModel):
    """日曆搜索工具的輸入模式。"""
    query: str = Field(description="搜索查詢，例如 '下週的會議' 或 '明天的行程'")
    date_range: Optional[str] = Field(default=None, description="日期範圍，例如 '2025-07-23 to 2025-07-30'")

class CalendarTool(BaseTool):
    """日曆管理工具。"""
    name: str = "calendar_search"
    description: str = "搜索和查詢使用者的日曆行程。可以查找特定日期的會議、事件或行程安排。"
    args_schema: Type[BaseModel] = CalendarSearchInput

    def _run(self, query: str, date_range: Optional[str] = None) -> str:
        """執行日曆搜索。"""
        # TODO: 整合真實的日曆 API (例如 Google Calendar API 或 Outlook Calendar API)
        return "日曆功能尚未實現。請聯繫管理員進行配置。"

class EmailSearchInput(BaseModel):
    """郵件搜索工具的輸入模式。"""
    query: str = Field(description="搜索查詢，例如 '來自張三的郵件' 或 '關於專案A的郵件'")
    sender: Optional[str] = Field(default=None, description="發件人")
    subject_contains: Optional[str] = Field(default=None, description="主題包含的關鍵字")

class EmailTool(BaseTool):
    """郵件管理工具。"""
    name: str = "email_search"
    description: str = "搜索和查詢使用者的郵件。可以根據發件人、主題、內容等條件搜索郵件。"
    args_schema: Type[BaseModel] = EmailSearchInput

    def _run(self, query: str, sender: Optional[str] = None, subject_contains: Optional[str] = None) -> str:
        """執行郵件搜索。"""
        # TODO: 整合真實的郵件 API (例如 Gmail API 或 Outlook Mail API)
        return "郵件功能尚未實現。請聯繫管理員進行配置。"

class TaskManagementInput(BaseModel):
    """任務管理工具的輸入模式。"""
    action: str = Field(description="操作類型：'create', 'list', 'update', 'complete'")
    task_title: Optional[str] = Field(default=None, description="任務標題")
    due_date: Optional[str] = Field(default=None, description="截止日期 (YYYY-MM-DD)")
    priority: Optional[str] = Field(default=None, description="優先級：'high', 'medium', 'low'")
    task_id: Optional[str] = Field(default=None, description="任務ID（用於更新或完成任務）")

class TaskManagementTool(BaseTool):
    """任務管理工具。"""
    name: str = "task_management"
    description: str = "管理使用者的任務和待辦事項。可以創建、查看、更新和完成任務。"
    args_schema: Type[BaseModel] = TaskManagementInput

    def _run(self, action: str, task_title: Optional[str] = None, due_date: Optional[str] = None, 
             priority: Optional[str] = None, task_id: Optional[str] = None) -> str:
        """執行任務管理操作。"""
        # 這裡是模擬實現，實際應該整合真實的任務管理系統
        
        if action == "create":
            if not task_title:
                return "錯誤：創建任務需要提供任務標題。"
            
            # 模擬創建任務
            new_task = {
                "id": f"task_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "title": task_title,
                "due_date": due_date,
                "priority": priority or "medium",
                "status": "pending"
            }
            return f"已創建新任務：{task_title}（ID: {new_task['id']}）"
        
        elif action == "list":
            # TODO: 整合真實的任務管理系統 API
            return "任務列表功能尚未實現。請聯繫管理員進行配置。"
        
        elif action == "complete":
            if not task_id:
                return "錯誤：完成任務需要提供任務ID。"
            return f"已完成任務 {task_id}。"
        
        elif action == "update":
            if not task_id:
                return "錯誤：更新任務需要提供任務ID。"
            return f"已更新任務 {task_id}。"
        
        else:
            return f"不支援的操作：{action}。支援的操作：create, list, update, complete。"

class MemorySearchInput(BaseModel):
    """記憶搜索工具的輸入模式。"""
    query: str = Field(description="搜索查詢，例如 '張三的聯絡方式' 或 '上次討論的專案'")

class MemorySearchTool(BaseTool):
    """記憶搜索工具。"""
    name: str = "memory_search"
    description: str = "搜索使用者的長期記憶，包括個人資訊、對話歷史、重要決定等。"
    args_schema: Type[BaseModel] = MemorySearchInput
    memory_manager: Any = Field(default=None, exclude=True) # 將 memory_manager 定義為 Pydantic 字段，並排除在序列化之外

    def __init__(self, memory_manager: Any = None, **kwargs):
        super().__init__(**kwargs)
        self.memory_manager = memory_manager

    def _run(self, query: str) -> str:
        """執行記憶搜索。"""
        if not self.memory_manager:
            return "記憶管理器未初始化。"
        
        try:
            results = self.memory_manager.search_memory(query)
            
            # 優先使用智能搜索結果
            smart_results = results.get("smart_results", [])
            if smart_results:
                result_text = f"找到與 '{query}' 相關的記憶：\n\n"
                
                for i, result in enumerate(smart_results[:5], 1):  # 顯示前5個結果
                    source_type = "向量搜索" if result["source"] == "vector_search" else "圖搜索"
                    score = result.get("enhanced_score", result.get("score", 0.0))
                    priority = result.get("priority_score", 0.0)
                    
                    result_text += f"{i}. [{source_type}] (分數: {score:.2f}, 重要性: {priority:.2f})\n"
                    result_text += f"   {result['content'][:150]}...\n"
                    
                    # 添加分類信息
                    classification = result.get("classification", {})
                    if classification:
                        primary_type = classification.get("primary_type", "")
                        if primary_type != "general":
                            result_text += f"   類型: {primary_type}\n"
                    
                    # 添加元數據信息
                    metadata = result.get("metadata", {})
                    if metadata:
                        if "speaker" in metadata:
                            result_text += f"   來源: {metadata['speaker']}\n"
                        if "timestamp" in metadata:
                            result_text += f"   時間: {metadata['timestamp']}\n"
                    
                    result_text += "\n"
                
                # 添加摘要
                summary = results.get("summary", "")
                if summary and len(smart_results) > 3:
                    result_text += f"\n📋 記憶摘要：\n{summary}"
                
                return result_text
            
            # 回退到組合搜索結果
            combined_results = results.get("combined_results", [])
            if combined_results:
                result_text = f"找到與 '{query}' 相關的記憶：\n\n"
                
                for i, result in enumerate(combined_results[:5], 1):
                    source_type = "向量搜索" if result["source"] == "vector_search" else "圖搜索"
                    score = result.get("score", 0.0)
                    
                    result_text += f"{i}. [{source_type}] (相關性: {score:.2f})\n"
                    result_text += f"   {result['content'][:150]}...\n"
                    
                    metadata = result.get("metadata", {})
                    if metadata and "speaker" in metadata:
                        result_text += f"   來源: {metadata['speaker']}\n"
                    
                    result_text += "\n"
                
                return result_text
            
            return f"未找到與 '{query}' 相關的記憶。"
            
        except Exception as e:
            return f"搜索記憶時發生錯誤：{str(e)}"

def get_all_tools(memory_manager=None):
    """獲取所有可用的工具。"""
    tools = [
        CalendarTool(),
        EmailTool(),
        TaskManagementTool(),
    ]
    
    if memory_manager:
        tools.append(MemorySearchTool(memory_manager))
    
    return tools

