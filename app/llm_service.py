import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from typing import Optional

load_dotenv()

class LLMService:
    """大语言模型服务封装"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
        self.model = ChatOpenAI(
            model="deepseek-chat",
            api_key=self.api_key,
            base_url=self.api_base,
            temperature=0.7
        )
        
        self.system_prompt = """
你是武汉理工大学智能导游助手，专门为师生和访客提供校园导航、场所介绍等服务。

核心职责：
1. 回答关于武汉理工大学各校区的问题
2. 提供校园内路径规划和导航指引
3. 介绍校内场所的详细信息
4. 用友好、热情的语气与用户交流

当用户询问导航时：
- 请提取出发地和目的地信息
- 如果缺少信息，请询问用户补充

当用户询问场所信息时：
- 提供详细的场所描述
- 可以介绍场所的历史、特色等

回答要求：
- 使用中文回复
- 语言简洁明了
- 保持友好热情
- 避免使用专业术语过多
        """.strip()
    
    async def analyze_query(self, query: str) -> dict:
        """分析用户查询意图"""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="你是一个意图分析助手。请分析用户的查询意图，判断是以下哪种类型：\n1. navigation: 请求导航或路线规划，包含'去'、'怎么走'、'导航'、'路线'等关键词\n2. introduction: 请求场所介绍，询问某个地方是什么样的\n3. question: 一般性问题\n4. greeting: 问候或闲聊\n\n请返回JSON格式，包含intent字段和相关参数。如果是navigation或introduction，还需要包含place字段表示目标场所名称。"),
            HumanMessage(content=f"用户查询：{query}")
        ])
        
        chain = prompt | self.model
        response = await chain.ainvoke({})
        
        try:
            import json
            result = json.loads(response.content)
            # 如果意图是navigation但没有place，尝试从query中提取
            if result.get("intent") == "navigation" and not result.get("place"):
                # 简单的关键词匹配提取目的地
                places = ["南湖图书馆", "西院图书馆", "鉴湖教学楼", "南湖体育馆", "马房山校区", "南湖校区", "余家头校区", "行政楼", "大学生活动中心", "学生食堂"]
                for place in places:
                    if place in query:
                        result["place"] = place
                        break
            return result
        except:
            # 如果解析失败，尝试简单规则判断
            if any(keyword in query for keyword in ["去", "怎么走", "导航", "路线"]):
                # 尝试提取目的地
                places = ["南湖图书馆", "西院图书馆", "鉴湖教学楼", "南湖体育馆", "马房山校区", "南湖校区", "余家头校区", "行政楼", "大学生活动中心", "学生食堂"]
                found_place = None
                for place in places:
                    if place in query:
                        found_place = place
                        break
                return {"intent": "navigation", "place": found_place}
            elif any(keyword in query for keyword in ["是什么", "介绍", "怎么样", "在哪"]):
                places = ["南湖图书馆", "西院图书馆", "鉴湖教学楼", "南湖体育馆", "马房山校区", "南湖校区", "余家头校区", "行政楼", "大学生活动中心", "学生食堂"]
                found_place = None
                for place in places:
                    if place in query:
                        found_place = place
                        break
                return {"intent": "introduction", "place": found_place}
            return {"intent": "question", "query": query}
    
    async def generate_response(self, query: str, context: Optional[str] = None) -> str:
        """生成自然语言响应"""
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"上下文信息：{context}\n\n用户问题：{query}")
        ]
        
        response = await self.model.ainvoke(messages)
        return response.content
    
    async def extract_locations(self, query: str) -> dict:
        """从查询中提取位置信息"""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="请从用户查询中提取出发地和目的地信息。如果没有明确提到出发地或目的地，请将其设为null。返回JSON格式。"),
            HumanMessage(content=f"用户查询：{query}")
        ])
        
        chain = prompt | self.model
        response = await chain.ainvoke({})
        
        try:
            import json
            return json.loads(response.content)
        except:
            return {"origin": None, "destination": None}