from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

def create_agent(llm, tools, prompt):
    """創建並返回一個 LangChain Agent。"""
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        handle_parsing_errors=True,  # 處理解析錯誤
        max_iterations=3,  # 限制最大迭代次數
        early_stopping_method="generate"  # 早期停止方法
    )
    return agent_executor

def get_agent_prompt(tools):
    """返回 Agent 的 Prompt Template。"""
    template = """你是一個功能強大的 AI 秘書，旨在幫助使用者管理日程、處理郵件、查詢資訊等。你擁有長期記憶，可以記住使用者的個人資訊和對話歷史。

請嚴格按照以下格式回答：

Thought: 我需要思考使用者想要什麼
Action: [選擇一個工具名稱]
Action Input: [工具的輸入參數]
Observation: [工具的執行結果會自動填入]
... (可以重複 Thought/Action/Action Input/Observation)
Thought: 我現在知道最終答案了
Final Answer: [給使用者的最終回答]

可用的工具：
{tools}

工具名稱：{tool_names}

使用者輸入：{input}

{agent_scratchpad}"""
    return PromptTemplate.from_template(template, partial_variables={"tool_names": ", ".join([tool.name for tool in tools])})



