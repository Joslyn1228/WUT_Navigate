import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from typing import Optional, Dict, Any
import json

load_dotenv()

class LLMService:
    """大语言模型服务封装 - 全面支持武理导航平台所有功能"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
        self._model = None
        
        self.system_prompt = """
你是武汉理工大学智能助手，专为师生和访客提供全方位的校园服务。

=== 服务范围 ===
我可以帮助您了解和使用武理导航平台的所有功能：

🏫 【校园导航】
- 校园内路径规划和导航指引
- 校内场所详细介绍（图书馆、教学楼、体育馆等）
- 支持南湖校区、马房山校区、余家头校区三个校区

👤 【用户账户】
- 注册登录流程说明
- 个人信息管理（头像、昵称、个性签名）
- 密码重置与安全设置
- 临时状态设置（维持6小时）

🏃 【运动健康】
- 运动记录功能（步行、跑步、骑行）
- 运动统计数据（周统计、月统计、累计统计）
- 运动历史记录查询

📍 【打卡系统】
- 位置打卡功能说明
- 成就系统（连续打卡、打卡次数、特定地点打卡）
- 打卡统计数据查看

💬 【社区互动】
- 发布动态（文字+图片，最多9张）
- 点赞和评论互动
- 动态搜索功能

🏛️ 【景点讲解】
- 校内景点介绍
- 实时语音讲解（50米内自动触发）
- 景点分类浏览

=== 回答原则 ===
1. 使用中文回复，语言简洁明了
2. 保持友好热情的语气
3. 当用户询问功能使用方法时，提供清晰的操作指引
4. 如果遇到无法回答的问题，礼貌地说明
5. 可以回答关于武汉理工大学的一般性问题

=== 常见问题处理 ===
- 用户问"怎么注册" → 解释注册流程
- 用户问"怎么打卡" → 说明打卡功能使用方法
- 用户问"怎么运动" → 说明运动功能使用方法
- 用户问"怎么发帖" → 说明社区发帖流程
- 用户问"去XX怎么走" → 提供导航指引
- 用户问"XX是什么" → 提供场所介绍

请根据用户问题，判断属于哪个功能模块，并提供准确的回答。
        """.strip()
    
    @property
    def model(self):
        if self._model is None:
            self._model = ChatOpenAI(
                model="deepseek-chat",
                api_key=self.api_key,
                base_url=self.api_base,
                temperature=0.7
            )
        return self._model
    
    async def analyze_query(self, query: str) -> dict:
        """分析用户查询意图，支持所有功能模块"""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""
你是一个意图分析助手。请分析用户的查询意图，判断是以下哪种类型：

1. navigation: 请求导航或路线规划，包含'去'、'怎么走'、'导航'、'路线'等关键词
2. introduction: 请求场所介绍，询问某个地方是什么样的
3. auth: 用户账户相关问题，包含'注册'、'登录'、'密码'、'头像'、'账户'等关键词
4. fitness: 运动健康相关问题，包含'运动'、'跑步'、'步行'、'统计'、'历史'等关键词
5. checkin: 打卡相关问题，包含'打卡'、'成就'、'签到'等关键词
6. community: 社区相关问题，包含'发帖'、'动态'、'评论'、'点赞'等关键词
7. guide: 景点讲解相关，包含'讲解'、'景点'、'介绍'等关键词
8. question: 一般性问题，不涉及以上类别
9. greeting: 问候或闲聊

请返回JSON格式，包含intent字段和相关参数。如果涉及具体场所或功能，请包含相关字段。
"""),
            HumanMessage(content=f"用户查询：{query}")
        ])
        
        chain = prompt | self.model
        response = await chain.ainvoke({})
        
        try:
            result = json.loads(response.content)
            return result
        except:
            return self._analyze_query_fallback(query)
    
    def _analyze_query_fallback(self, query: str) -> dict:
        """意图分析降级处理"""
        keywords_map = {
            "navigation": ["去", "怎么走", "导航", "路线", "位置", "在哪", "到达"],
            "introduction": ["是什么", "介绍", "怎么样", "历史", "特色"],
            "auth": ["注册", "登录", "密码", "头像", "账户", "账号", "个人信息"],
            "fitness": ["运动", "跑步", "步行", "骑行", "统计", "历史", "记录"],
            "checkin": ["打卡", "签到", "成就", "徽章", "连续"],
            "community": ["发帖", "动态", "评论", "点赞", "分享", "帖子"],
            "guide": ["讲解", "景点", "介绍", "收听"],
        }
        
        for intent, keywords in keywords_map.items():
            if any(keyword in query for keyword in keywords):
                return {"intent": intent, "query": query}
        
        if any(greeting in query for greeting in ["你好", "嗨", "哈喽", "Hi", "Hello"]):
            return {"intent": "greeting", "query": query}
        
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
            return json.loads(response.content)
        except:
            return {"origin": None, "destination": None}
    
    async def get_function_call(self, query: str) -> Dict[str, Any]:
        """根据用户查询生成函数调用信息"""
        intent = await self.analyze_query(query)
        intent_type = intent.get("intent", "question")
        
        function_map = {
            "navigation": {
                "function": "navigate",
                "description": "获取导航路线",
                "requires_params": ["destination"]
            },
            "introduction": {
                "function": "get_place_introduction",
                "description": "获取场所介绍",
                "requires_params": ["place_name"]
            },
            "auth": {
                "function": "auth_help",
                "description": "用户账户帮助",
                "requires_params": []
            },
            "fitness": {
                "function": "fitness_help",
                "description": "运动健康帮助",
                "requires_params": []
            },
            "checkin": {
                "function": "checkin_help",
                "description": "打卡系统帮助",
                "requires_params": []
            },
            "community": {
                "function": "community_help",
                "description": "社区功能帮助",
                "requires_params": []
            },
            "guide": {
                "function": "guide_help",
                "description": "景点讲解帮助",
                "requires_params": []
            }
        }
        
        return function_map.get(intent_type, {
            "function": "general_answer",
            "description": "通用回答",
            "requires_params": []
        })
    
    async def generate_help_response(self, intent_type: str) -> str:
        """根据意图类型生成帮助信息"""
        help_templates = {
            "auth": """
【用户账户功能】

🔐 注册登录
- 支持邮箱注册，需要验证邮箱
- 登录后可使用所有功能
- 支持密码重置功能

👤 个人信息
- 可设置头像和昵称
- 可设置临时状态（维持6小时）
- 可修改密码和个性签名

如有具体问题，请告诉我！
            """,
            "fitness": """
【运动健康功能】

🏃 开始运动
- 支持步行、跑步、骑行三种类型
- 自动记录运动轨迹
- 实时更新位置

📊 运动统计
- 周统计：查看本周运动数据
- 月统计：查看本月运动数据
- 累计统计：查看历史累计数据

📝 运动历史
- 查看所有运动记录
- 显示运动时间和距离

如有具体问题，请告诉我！
            """,
            "checkin": """
【打卡系统功能】

📍 位置打卡
- 到达打卡点附近自动检测
- 支持手动打卡
- 打卡成功获得积分

🏆 成就系统
- 连续打卡成就
- 打卡次数成就
- 特定地点打卡成就

📈 打卡统计
- 查看打卡历史
- 查看获得的成就

如有具体问题，请告诉我！
            """,
            "community": """
【社区互动功能】

📝 发布动态
- 支持文字和图片
- 可添加位置信息
- 最多上传9张图片

💬 互动功能
- 点赞动态
- 评论动态
- 搜索动态

🔍 搜索功能
- 按关键词搜索动态
- 查看用户发布的所有动态

如有具体问题，请告诉我！
            """,
            "navigation": """
【导航服务】

📍 路线规划
- 支持南湖、马房山、余家头三个校区
- 输入起点和终点获取路线
- 支持步行导航

🏛️ 场所介绍
- 图书馆、教学楼、体育馆等
- 提供详细场所信息
- 支持语音讲解

🔍 附近场所
- 显示附近的场所
- 支持50米内自动讲解

如有具体问题，请告诉我！
            """,
            "guide": """
【景点讲解功能】

🏛️ 校内景点
- 浏览校内所有景点
- 按类别筛选（图书馆、教学楼等）
- 查看景点详细介绍

🔊 语音讲解
- 到达景点50米内自动触发
- 支持手动点击收听
- 提供丰富的景点故事

🗺️ 地图浏览
- 查看校园地图
- 定位当前位置
- 查看周边景点

如有具体问题，请告诉我！
            """
        }
        
        return help_templates.get(intent_type, "请问有什么可以帮助你的？")
