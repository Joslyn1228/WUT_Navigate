from typing import Optional, List, Dict
from .schemas import Location, NavigationResponse, NavigationStep, PlaceInfo, NearbyPlace, NearbyPlacesResponse, PlaceIntroductionResponse
from .location_service import AMapService
from .place_database import PlaceDatabase
from .llm_service import LLMService
import math


class WUTourGuideAgent:
    """武汉理工大学智能导游Agent - 全面支持所有功能模块"""
    
    NEARBY_THRESHOLD = 50  # 附近阈值（米）
    
    def __init__(self):
        self.location_service = AMapService()
        self.place_database = PlaceDatabase()
        self.llm_service = LLMService()
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """计算两点之间的距离（米）"""
        R = 6371000
        d_lat = math.radians(lat2 - lat1)
        d_lng = math.radians(lng2 - lng1)
        a = (math.sin(d_lat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(d_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    
    async def _resolve_destination(
        self,
        query: str,
        hinted_place: Optional[str],
        place_names: List[str],
    ) -> Optional[str]:
        """将用户表达解析为标准场所名"""
        place = self.place_database.resolve_place(hinted_place or "", query)
        if place:
            return place.name

        matched = self.place_database.match_place_from_text(query)
        if matched:
            return matched

        if hinted_place:
            resolved = await self.llm_service.resolve_place_name(query, place_names, hinted_place)
            if resolved:
                return resolved

        return await self.llm_service.resolve_place_name(query, place_names, None)

    def _build_context(
        self,
        current_location: Optional[Location],
        place_names: List[str],
    ) -> str:
        parts = []
        if current_location:
            parts.append(f"用户当前位置：纬度 {current_location.latitude}，经度 {current_location.longitude}")
            if current_location.address:
                parts.append(f"地址：{current_location.address}")
            nearby = self.get_nearby_places(current_location, radius=500)
            if nearby.nearby_places:
                names = [f"{p.place.name}({p.distance}米)" for p in nearby.nearby_places[:5]]
                parts.append(f"附近场所：{', '.join(names)}")
        parts.append(f"校内已知场所：{', '.join(place_names)}")
        return "\n".join(parts)

    async def process_query(
        self,
        query: str,
        current_location: Optional[Location] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> NavigationResponse:
        """处理用户查询 - 支持所有功能模块"""
        place_names = [p.name for p in self.place_database.get_all_places()]
        intent_result = await self.llm_service.analyze_query(
            query, place_names, conversation_history
        )
        intent = intent_result.get("intent", "question")
        sub_intents = intent_result.get("sub_intents") or []
        place_hint = intent_result.get("place")

        needs_place = intent in ("navigation", "introduction") or any(
            i in sub_intents for i in ("navigation", "introduction")
        )
        resolved_name = None
        if needs_place:
            resolved_name = await self._resolve_destination(query, place_hint, place_names)

        if intent == "navigation" or "navigation" in sub_intents:
            if not resolved_name:
                return NavigationResponse(
                    status="success",
                    message="请告诉我您要去哪个地方，例如「南湖图书馆」「鉴湖艾特楼」或「学生食堂」。",
                    response_type="text",
                )

            nav_response = await self.get_navigation(current_location, resolved_name)

            if "introduction" in sub_intents or intent == "introduction":
                place = self.place_database.get_place(resolved_name)
                if place:
                    intro = f"\n\n📖 {place.name}介绍：\n{place.description}"
                    nav_response.message = (nav_response.message or "") + intro
                    nav_response.response_type = "navigation"

            return nav_response
        
        elif intent == "introduction":
            if resolved_name:
                place = self.place_database.get_place(resolved_name)
            else:
                place = self.place_database.resolve_place(query)

            if place:
                return NavigationResponse(
                    status="success",
                    message=place.description,
                    place_info=place,
                    response_type="introduction",
                )
            return NavigationResponse(
                status="success",
                message="暂未找到相关场所，您可以试试「南湖图书馆」「西院图书馆」「南湖体育馆」等具体名称。",
                response_type="text",
            )
        
        elif intent == "auth":
            help_text = await self.llm_service.generate_help_response("auth")
            return NavigationResponse(
                status="success",
                message=help_text,
                response_type="text"
            )
        
        elif intent == "fitness":
            help_text = await self.llm_service.generate_help_response("fitness")
            return NavigationResponse(
                status="success",
                message=help_text,
                response_type="text"
            )
        
        elif intent == "checkin":
            help_text = await self.llm_service.generate_help_response("checkin")
            return NavigationResponse(
                status="success",
                message=help_text,
                response_type="text"
            )
        
        elif intent == "community":
            help_text = await self.llm_service.generate_help_response("community")
            return NavigationResponse(
                status="success",
                message=help_text,
                response_type="text"
            )
        
        elif intent == "guide":
            help_text = await self.llm_service.generate_help_response("guide")
            return NavigationResponse(
                status="success",
                message=help_text,
                response_type="text"
            )
        
        elif intent == "greeting":
            return NavigationResponse(
                status="success",
                message="你好！我是武汉理工大学智能助手，请问有什么可以帮助你的？\n\n我可以帮你：\n📍 校园导航与场所介绍\n👤 用户账户管理\n🏃 运动健康服务\n📍 打卡与成就系统\n💬 社区互动功能\n🏛️ 景点讲解",
                response_type="text"
            )
        
        else:
            context = self._build_context(current_location, place_names)
            answer = await self.llm_service.generate_response(
                query, context, conversation_history
            )
            return NavigationResponse(
                status="success",
                message=answer,
                response_type="text",
            )
    
    async def get_navigation(self, start_location: Optional[Location], destination_name: str) -> NavigationResponse:
        """获取导航路线"""
        destination = None
        place = self.place_database.resolve_place(destination_name)
        
        if place:
            destination_name = place.name
            destination = Location(
                latitude=place.latitude,
                longitude=place.longitude,
                address=f"武汉理工大学 {place.name}"
            )
        
        if not destination:
            search_patterns = [
                f"武汉理工大学 {destination_name}",
                f"武汉理工大学南湖校区 {destination_name}",
                f"武汉理工大学马房山校区 {destination_name}",
                f"武汉理工大学余家头校区 {destination_name}"
            ]
            
            for pattern in search_patterns:
                destination = self.location_service.geocode(pattern)
                if destination:
                    break
                destination = self.location_service.search_poi(pattern)
                if destination:
                    break
        
        if not destination:
            return NavigationResponse(
                status="error",
                message=f"无法找到地点：{destination_name}，请尝试使用更具体的名称",
                response_type="text"
            )
        
        if not start_location:
            start_location = Location(
                latitude=30.5075,
                longitude=114.3795,
                address="武汉理工大学南湖校区"
            )
        
        route_data = None
        try:
            route_data = self.location_service.get_walking_route(
                start_location.latitude,
                start_location.longitude,
                destination.latitude,
                destination.longitude
            )
        except Exception as e:
            print(f"获取路线失败: {e}")
        
        total_distance = None
        if route_data and route_data.get("route") and route_data["route"].get("paths"):
            path = route_data["route"]["paths"][0]
            total_distance = float(path["distance"]) / 1000
        
        return NavigationResponse(
            status="success",
            message=f"到{destination_name}的距离约{total_distance:.2f}公里" if total_distance else "",
            destination=destination_name,
            total_distance=total_distance,
            place_info=destination,
            response_type="navigation"
        )
    
    def get_all_places(self) -> List[PlaceInfo]:
        """获取所有场所信息"""
        return self.place_database.get_all_places()
    
    def get_nearby_places(self, current_location: Location, radius: int = 200) -> NearbyPlacesResponse:
        """获取附近的场所"""
        all_places = self.place_database.get_all_places()
        nearby_places = []
        
        for place in all_places:
            distance = self._calculate_distance(
                current_location.latitude,
                current_location.longitude,
                place.latitude,
                place.longitude
            )
            if distance <= radius:
                nearby_places.append(NearbyPlace(
                    place=place,
                    distance=round(distance, 1)
                ))
        
        nearby_places.sort(key=lambda x: x.distance)
        
        return NearbyPlacesResponse(
            status="success",
            message=f"已找到 {len(nearby_places)} 个附近场所",
            nearby_places=nearby_places,
            current_location=current_location
        )
    
    def check_proximity_and_introduce(self, current_location: Location) -> Optional[PlaceIntroductionResponse]:
        """检查是否接近某个场所（50米内），如果是则返回介绍"""
        all_places = self.place_database.get_all_places()
        
        for place in all_places:
            distance = self._calculate_distance(
                current_location.latitude,
                current_location.longitude,
                place.latitude,
                place.longitude
            )
            
            if distance <= self.NEARBY_THRESHOLD:
                return PlaceIntroductionResponse(
                    status="success",
                    message=f"您已到达{place.name}附近！",
                    place=place,
                    is_nearby=True
                )
        
        return None
    
    def get_place_introduction(self, place_name: str) -> PlaceIntroductionResponse:
        """获取指定场所的介绍"""
        place = self.place_database.get_place(place_name)
        
        if place:
            return PlaceIntroductionResponse(
                status="success",
                message=f"{place.name}介绍",
                place=place,
                is_nearby=False
            )
        else:
            return PlaceIntroductionResponse(
                status="error",
                message=f"未找到'{place_name}'的相关信息",
                place=PlaceInfo(
                    name=place_name,
                    category="未知",
                    description="",
                    latitude=0.0,
                    longitude=0.0
                ),
                is_nearby=False
            )
    
    def get_places_by_category(self, category: str) -> List[PlaceInfo]:
        """按类别获取场所列表"""
        return self.place_database.get_places_by_category(category)
    
    def get_categories(self) -> List[str]:
        """获取所有场所类别"""
        all_places = self.place_database.get_all_places()
        categories = set(place.category for place in all_places)
        return sorted(list(categories))
