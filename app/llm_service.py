import os
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from typing import Optional, Dict, Any, List
import json

load_dotenv()

class LLMService:
    """大语言模型服务封装 - 全面支持武理导航平台所有功能"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
        self._model = None
        self._intent_model = None
        
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

    @property
    def intent_model(self):
        if self._intent_model is None:
            self._intent_model = ChatOpenAI(
                model="deepseek-chat",
                api_key=self.api_key,
                base_url=self.api_base,
                temperature=0.1
            )
        return self._intent_model

    @staticmethod
    def _extract_json(text: str) -> Optional[dict]:
        if not text:
            return None
        text = text.strip()
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if fence_match:
            text = fence_match.group(1).strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        brace_match = re.search(r"\{[\s\S]*\}", text)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass
        return None

    def _build_intent_system_prompt(self, place_names: Optional[List[str]] = None) -> str:
        places_section = ""
        if place_names:
            places_section = f"""
=== 已知校内场所（place 字段必须从中选取标准名称，无法确定时填 null）===
{", ".join(place_names)}
"""
        return f"""
你是武汉理工大学导航平台的意图理解模块。请结合对话上下文，准确理解用户的真实需求。

=== 意图类型 ===
- navigation: 想去某处、问路、怎么走、导航、带我到…
- introduction: 询问某场所是什么、介绍、特色、历史
- auth: 注册、登录、密码、头像、账户
- fitness: 运动、跑步、步行、骑行、运动统计
- checkin: 打卡、签到、成就、徽章
- community: 发帖、动态、评论、点赞
- guide: 景点讲解、语音讲解、收听介绍
- greeting: 你好、在吗等问候
- question: 其他一般性问题

=== 复合意图 ===
若用户同时要求「导航+介绍」（如「带我去南湖图书馆并介绍一下」），intent 填主意图 navigation，sub_intents 填 ["navigation", "introduction"]。

=== 口语理解示例 ===
- 「马房山那边图书馆」→ place: 西院图书馆
- 「鉴湖教学楼」→ place: 鉴湖艾特楼
- 「想去吃饭」→ place: 学生食堂
- 「图书馆在哪」→ intent: navigation 或 introduction，place 需结合上下文（南湖→南湖图书馆）
- 「刚才说的那个图书馆」→ 参考对话历史推断 place
{places_section}
=== 输出要求 ===
只输出一个 JSON 对象，不要 markdown，不要解释。字段：
- intent: 字符串，上述类型之一
- place: 标准场所名或 null
- sub_intents: 字符串数组，无复合意图时省略或 []
- confidence: 0~1 的数字
- rewritten_query: 用一句话概括用户真实意图（中文）
""".strip()

    def _format_conversation_history(self, history: Optional[List[Dict[str, str]]]) -> str:
        if not history:
            return "（无历史对话）"
        lines = []
        for msg in history[-6:]:
            role = "用户" if msg.get("role") == "user" else "助手"
            content = (msg.get("content") or "").strip()
            if content:
                lines.append(f"{role}：{content}")
        return "\n".join(lines) if lines else "（无历史对话）"

    async def analyze_query(
        self,
        query: str,
        place_names: Optional[List[str]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> dict:
        """分析用户查询意图，支持对话上下文与场所列表"""
        system_prompt = self._build_intent_system_prompt(place_names)
        history_text = self._format_conversation_history(conversation_history)

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"""对话历史：
{history_text}

当前用户输入：{query}"""),
        ])

        chain = prompt | self.intent_model
        response = await chain.ainvoke({})
        result = self._extract_json(response.content)

        if result and result.get("intent"):
            normalized = {
                "intent": result.get("intent", "question"),
                "place": result.get("place") or None,
                "sub_intents": result.get("sub_intents") or [],
                "confidence": result.get("confidence", 0.8),
                "rewritten_query": result.get("rewritten_query", query),
                "query": query,
            }
            if normalized["place"] == "null":
                normalized["place"] = None
            return normalized

        return self._analyze_query_fallback(query, place_names, conversation_history)
    
    def _analyze_query_fallback(
        self,
        query: str,
        place_names: Optional[List[str]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> dict:
        """意图分析降级处理"""
        keywords_map = {
            "navigation": ["去", "怎么走", "导航", "路线", "在哪", "到达", "带我去", "领我去", "怎么到"],
            "introduction": ["是什么", "介绍", "怎么样", "历史", "特色", "讲讲", "说说"],
            "auth": ["注册", "登录", "密码", "头像", "账户", "账号", "个人信息"],
            "fitness": ["运动", "跑步", "步行", "骑行", "统计", "历史", "记录"],
            "checkin": ["打卡", "签到", "成就", "徽章", "连续"],
            "community": ["发帖", "动态", "评论", "点赞", "分享", "帖子"],
            "guide": ["讲解", "景点", "收听", "语音"],
        }

        detected_intents = []
        for intent, keywords in keywords_map.items():
            if any(keyword in query for keyword in keywords):
                detected_intents.append(intent)

        place = None
        search_text = query
        if place_names:
            for name in sorted(place_names, key=len, reverse=True):
                if name in search_text:
                    place = name
                    break
        if not place and conversation_history:
            for msg in reversed(conversation_history):
                if msg.get("role") == "user":
                    for name in sorted(place_names or [], key=len, reverse=True):
                        if name in (msg.get("content") or ""):
                            place = name
                            break
                if place:
                    break

        if "navigation" in detected_intents and "introduction" in detected_intents:
            primary = "navigation"
            sub_intents = ["navigation", "introduction"]
        elif detected_intents:
            primary = detected_intents[0]
            sub_intents = detected_intents[:2] if len(detected_intents) > 1 else []
        elif any(greeting in query for greeting in ["你好", "嗨", "哈喽", "Hi", "Hello", "在吗"]):
            primary = "greeting"
            sub_intents = []
        else:
            primary = "question"
            sub_intents = []

        result = {
            "intent": primary,
            "place": place,
            "sub_intents": sub_intents,
            "confidence": 0.5,
            "rewritten_query": query,
            "query": query,
        }
        return result

    async def resolve_place_name(
        self,
        query: str,
        place_names: List[str],
        hinted_place: Optional[str] = None,
    ) -> Optional[str]:
        """用 LLM 将口语化表达规范化为标准场所名"""
        if hinted_place and hinted_place in place_names:
            return hinted_place

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"""从用户话术中识别要去的/要介绍的校内场所。
标准场所列表：{", ".join(place_names)}
只输出 JSON：{{"place": "标准名或null"}}，不要其他文字。"""),
            HumanMessage(content=f"用户说：{query}\n初步识别：{hinted_place or '无'}"),
        ])
        chain = prompt | self.intent_model
        response = await chain.ainvoke({})
        parsed = self._extract_json(response.content)
        if parsed:
            place = parsed.get("place")
            if place and place != "null" and place in place_names:
                return place
        return hinted_place
    
    async def generate_response(
        self,
        query: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """生成自然语言响应"""
        messages = [SystemMessage(content=self.system_prompt)]
        if conversation_history:
            for msg in conversation_history[-6:]:
                content = (msg.get("content") or "").strip()
                if not content:
                    continue
                if msg.get("role") == "user":
                    messages.append(HumanMessage(content=content))
                else:
                    messages.append(AIMessage(content=content))
        context_block = f"上下文信息：{context}\n\n" if context else ""
        messages.append(HumanMessage(content=f"{context_block}用户问题：{query}"))
        
        response = await self.model.ainvoke(messages)
        return response.content
    
    async def extract_locations(self, query: str) -> dict:
        """从查询中提取位置信息"""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="请从用户查询中提取出发地和目的地信息。如果没有明确提到出发地或目的地，请将其设为null。返回JSON格式。"),
            HumanMessage(content=f"用户查询：{query}")
        ])
        
        chain = prompt | self.intent_model
        response = await chain.ainvoke({})
        
        parsed = self._extract_json(response.content)
        if parsed:
            return parsed
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
