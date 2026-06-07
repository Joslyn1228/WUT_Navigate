import requests
import os
from dotenv import load_dotenv
from typing import Optional, Tuple
from .schemas import Location

load_dotenv()

class AMapService:
    """高德地图服务封装"""
    
    def __init__(self):
        self.web_service_key = os.getenv("AMAP_WEB_SERVICE_KEY")
        self.base_url = "https://restapi.amap.com/v3"
    
    def geocode(self, address: str, city: str = "武汉市") -> Optional[Location]:
        """地址转坐标"""
        # 首先尝试地理编码（更可靠）
        url = f"{self.base_url}/geocode/geo"
        params = {
            "address": address,
            "city": city,
            "key": self.web_service_key
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            if data["status"] == "1" and data["geocodes"]:
                location = data["geocodes"][0]["location"]
                lng, lat = map(float, location.split(","))
                return Location(
                    latitude=lat,
                    longitude=lng,
                    address=data["geocodes"][0]["formatted_address"]
                )
            return None
        except Exception as e:
            print(f"地理编码失败: {e}")
            return None
    
    def search_poi(self, keywords: str, city: str = "武汉市") -> Optional[Location]:
        """POI搜索"""
        url = f"{self.base_url}/place/text"
        params = {
            "keywords": keywords,
            "city": city,
            "types": "141202|150000|170000",  # 教育、文化、体育等类型
            "key": self.web_service_key
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            if data["status"] == "1" and data["pois"]:
                # 返回第一个匹配的POI
                poi = data["pois"][0]
                lng, lat = map(float, poi["location"].split(","))
                # 使用formatted_address或name字段
                address = poi.get("address", "") or poi.get("name", "")
                # 如果地址只是校区名称，不返回（避免误匹配）
                if "校区" in address and len(address) < 30:
                    return None
                return Location(
                    latitude=lat,
                    longitude=lng,
                    address=address
                )
            return None
        except Exception as e:
            print(f"POI搜索失败: {e}")
            return None
    
    def reverse_geocode(self, lat: float, lng: float) -> Optional[str]:
        """坐标转地址"""
        url = f"{self.base_url}/geocode/regeo"
        params = {
            "location": f"{lng},{lat}",
            "key": self.web_service_key
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            if data["status"] == "1":
                return data["regeocode"]["formatted_address"]
            return None
        except Exception as e:
            print(f"逆地理编码失败: {e}")
            return None
    
    def get_walking_route(self, from_lat: float, from_lng: float, to_lat: float, to_lng: float) -> Optional[dict]:
        """获取步行路线"""
        url = f"{self.base_url}/direction/walking"
        params = {
            "origin": f"{from_lng},{from_lat}",
            "destination": f"{to_lng},{to_lat}",
            "key": self.web_service_key
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            if data["status"] == "1":
                return data
            return None
        except Exception as e:
            print(f"获取步行路线失败: {e}")
            return None
    
    def get_distance(self, from_lat: float, from_lng: float, to_lat: float, to_lng: float) -> Optional[Tuple[float, int]]:
        """计算两点距离和预计时间"""
        route = self.get_walking_route(from_lat, from_lng, to_lat, to_lng)
        if route and route["route"]:
            distance = float(route["route"]["distance"]) / 1000  # 转为公里
            duration = int(route["route"]["time"])  # 秒
            return distance, duration
        return None