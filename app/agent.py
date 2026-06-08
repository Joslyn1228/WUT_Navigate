from typing import Optional, List
from .schemas import Location, NavigationResponse, NavigationStep, PlaceInfo, NearbyPlace, NearbyPlacesResponse, PlaceIntroductionResponse
from .location_service import AMapService
from .place_database import PlaceDatabase
from .llm_service import LLMService
import math


class WUTourGuideAgent:
    """武汉理工大学智能导游Agent"""
    
    NEARBY_THRESHOLD = 50  # 附近阈值（米）
    
    def __init__(self):
        self.location_service = AMapService()
        self.place_database = PlaceDatabase()
        self.llm_service = LLMService()
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """计算两点之间的距离（米）"""
        # 使用Haversine公式计算球面距离
        R = 6371000  # 地球半径（米）
        d_lat = math.radians(lat2 - lat1)
        d_lng = math.radians(lng2 - lng1)
        a = (math.sin(d_lat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(d_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    
    async def process_query(self, query: str, current_location: Optional[Location] = None) -> NavigationResponse:
        """处理用户查询"""
        # 分析查询意图
        intent_result = await self.llm_service.analyze_query(query)
        intent = intent_result.get("intent", "question")
        
        if intent == "navigation":
            # 从意图分析结果中获取目的地
            destination = intent_result.get("place")
            
            if not destination:
                return NavigationResponse(
                    status="error",
                    message="请告诉我您要去哪个地方",
                    response_type="text"
                )
            
            return await self.get_navigation(current_location, destination)
        
        elif intent == "introduction":
            # 提取场所名称
            place_name = intent_result.get("place") or query
            place = self.place_database.get_place(place_name)
            
            if place:
                return NavigationResponse(
                    status="success",
                    message=place.description,
                    place_info=place,
                    response_type="introduction"
                )
            else:
                return NavigationResponse(
                    status="error",
                    message=f"未找到'{place_name}'相关信息，试试其他场所吧！",
                    response_type="text"
                )
        
        else:
            # 一般性问题，使用LLM回答
            context = f"当前位置：{current_location}" if current_location else ""
            answer = await self.llm_service.generate_response(query, context)
            return NavigationResponse(
                status="success",
                message=answer,
                response_type="text"
            )
    
    async def get_navigation(self, start_location: Optional[Location], destination_name: str) -> NavigationResponse:
        """获取导航路线 - 优先使用数据库中的精确坐标"""
        
        # 1. 优先从数据库获取精确坐标（最可靠）
        destination = None
        place = self.place_database.get_place(destination_name)
        if place:
            destination = Location(
                latitude=place.latitude,
                longitude=place.longitude,
                address=f"武汉理工大学 {place.name}"
            )
            print(f"📍 使用数据库坐标: {place.name} ({place.latitude}, {place.longitude})")
        
        # 2. 如果数据库中没有，尝试使用高德地图API搜索
        if not destination:
            print(f"⚠️ 数据库中未找到 '{destination_name}'，尝试高德地图搜索")
            search_patterns = [
                f"武汉理工大学 {destination_name}",
                f"武汉理工大学南湖校区 {destination_name}",
                f"武汉理工大学马房山校区 {destination_name}",
                f"武汉理工大学余家头校区 {destination_name}"
            ]
            
            for pattern in search_patterns:
                destination = self.location_service.geocode(pattern)
                if destination:
                    print(f"✅ 地理编码找到: {pattern}")
                    break
                destination = self.location_service.search_poi(pattern)
                if destination:
                    print(f"✅ POI搜索找到: {pattern}")
                    break
        
        if not destination:
            return NavigationResponse(
                status="error",
                message=f"无法找到地点：{destination_name}，请尝试使用更具体的名称",
                response_type="text"
            )
        
        # 如果没有起点位置，使用南湖校区中心坐标
        if not start_location:
            start_location = Location(
                latitude=30.5075,
                longitude=114.3795,
                address="武汉理工大学南湖校区"
            )
        
        # 获取步行路线
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
        
        # 返回导航结果，包含总距离和地点信息
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
        
        # 按距离排序
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