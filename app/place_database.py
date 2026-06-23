from typing import Dict, List, Optional
from .schemas import PlaceInfo

class PlaceDatabase:
    """校内场所数据库"""

    PLACE_ALIASES: Dict[str, str] = {
        "马房山图书馆": "西院图书馆",
        "鉴湖": "鉴湖艾特楼",
        "艾特楼": "鉴湖艾特楼",
        "学生活动中心": "大学生活动中心",
        "活动中心": "大学生活动中心",
        "一食堂": "学生食堂",
        "二食堂": "学生食堂",
        "食堂": "学生食堂",
        "体育馆": "南湖体育馆",
    }
    
    # 南湖校区地理边界
    NANHU_BOUNDS = {
        'min_lat': 30.5000,
        'max_lat': 30.5150,
        'min_lng': 114.3720,
        'max_lng': 114.3900
    }
    
    def __init__(self):
        self.places: Dict[str, PlaceInfo] = self._load_places()
    
    def _load_places(self) -> Dict[str, PlaceInfo]:
        """加载武汉理工大学场所数据"""
        return {
            "南湖图书馆": PlaceInfo(
                name="南湖图书馆",
                category="图书馆",
                description="武汉理工大学南湖校区图书馆，建筑面积约4.3万平方米，是学校的文献信息中心。馆内藏书丰富，环境优雅，设有多个自习区域和电子阅览室，是学子们学习研究的理想场所。",
                latitude=30.509736,
                longitude=114.333502,
                voice_description="南湖图书馆位于南湖校区中心位置，开放时间为早上8点至晚上10点。"
            ),
            "西院图书馆": PlaceInfo(
                name="西院图书馆",
                category="图书馆",
                description="西院图书馆是学校最早的图书馆之一，历史悠久，馆藏丰富。馆内设有多个专业书库和阅览座位，为师生提供良好的学习环境。",
                latitude=30.519158,
                longitude=114.353908,
                voice_description="西院图书馆位于马房山校区西院，建筑风格古朴典雅。"
            ),
            "鉴湖艾特楼": PlaceInfo(
                name="鉴湖艾特楼",
                category="教学楼",
                description="鉴湖艾特楼是学校主要的教学场所之一，包括多栋教学楼，设有各类教室和实验室，承担着大量的本科教学任务。",
                latitude=30.512679,
                longitude=114.343067,
                voice_description="鉴湖艾特楼与学海楼是学校最高的教学楼，流传着神秘的传说..."
            ),
            "南湖体育馆": PlaceInfo(
                name="南湖体育馆",
                category="体育场馆",
                description="南湖体育馆是学校现代化的体育设施，设有室内篮球场、羽毛球场、游泳馆等，是师生进行体育锻炼和举办各类体育赛事的重要场所。",
                latitude=30.505464,
                longitude=114.330938,
                voice_description="南湖体育馆配备先进的体育设施，欢迎师生前来锻炼。"
            ),
            "马房山校区": PlaceInfo(
                name="马房山校区",
                category="校区",
                description="马房山校区是武汉理工大学的主校区之一，位于武汉市洪山区，校园环境优美，历史底蕴深厚，设有多个学院和研究机构。",
                latitude=30.518657,
                longitude=114.353283,
                voice_description="马房山校区分为东院、西院和鉴湖三个部分。"
            ),
            "南湖校区": PlaceInfo(
                name="南湖校区",
                category="校区",
                description="南湖校区是武汉理工大学的新校区，位于南湖之滨，环境优美，现代化设施齐全，是学校主要的教学和科研基地之一。",
                latitude=30.509565,
                longitude=114.33495,
                voice_description="南湖校区于2005年建成投入使用。"
            ),
            "余家头校区": PlaceInfo(
                name="余家头校区",
                category="校区",
                description="余家头校区位于武汉市武昌区，濒临长江，是学校交通学院、航运学院等学院的所在地，具有鲜明的水运交通特色。",
                latitude=30.606321,
                longitude=114.356604,
                voice_description="余家头校区拥有国内一流的水运交通实验设施。"
            ),
            "行政楼": PlaceInfo(
                name="行政楼",
                category="办公楼",
                description="行政楼是学校的行政管理中心，设有校长办公室、各职能部门办公室，是学校决策和管理的核心场所。",
                latitude=30.5420,
                longitude=114.3620,
                voice_description="行政楼位于马房山校区西院中心位置。"
            ),
            "大学生活动中心": PlaceInfo(
                name="大学生活动中心",
                category="活动场所",
                description="大学生活动中心是学生社团活动和各类校园文化活动的主要举办地，设有多个活动室和多功能厅。",
                latitude=30.5080,
                longitude=114.3810,
                voice_description="大学生活动中心经常举办各类文艺演出和社团活动。"
            ),
            "食堂": PlaceInfo(
                name="学生食堂",
                category="餐饮",
                description="学校各校区均设有多个学生食堂，提供丰富多样的餐饮选择，满足不同口味需求。",
                latitude=30.5070,
                longitude=114.3800,
                voice_description="南湖校区有一食堂、二食堂和风味餐厅。"
            )
        }
    
    def get_place(self, name: str) -> Optional[PlaceInfo]:
        """根据名称获取场所信息"""
        if not name:
            return None
        name = name.strip()
        if name in self.places:
            return self.places[name]
        if name in self.PLACE_ALIASES:
            return self.places.get(self.PLACE_ALIASES[name])
        for place_name, info in self.places.items():
            if name in place_name or place_name in name:
                return info
        return None

    def _disambiguate_library(self, text: str) -> Optional[str]:
        if "南湖" in text or "新校区" in text:
            return "南湖图书馆"
        if any(k in text for k in ("西院", "马房山", "鉴湖", "东院")):
            return "西院图书馆"
        return None

    def match_place_from_text(self, text: str) -> Optional[str]:
        """从自然语言文本中匹配最佳场所标准名"""
        if not text:
            return None
        text = text.strip()

        for name in sorted(self.places.keys(), key=len, reverse=True):
            if name in text:
                return name

        for alias, canonical in sorted(self.PLACE_ALIASES.items(), key=lambda x: len(x[0]), reverse=True):
            if alias in text:
                return canonical

        if "图书馆" in text:
            library = self._disambiguate_library(text)
            if library:
                return library

        for place in self.places.values():
            core = place.name.replace("武汉理工大学", "").strip()
            if len(core) >= 2 and core in text:
                return place.name

        keyword_hits = self.search_places(text)
        if len(keyword_hits) == 1:
            return keyword_hits[0].name
        return None

    def resolve_place(self, name_or_query: str, query_context: str = "") -> Optional[PlaceInfo]:
        """综合别名、模糊匹配与上下文消歧"""
        combined = f"{name_or_query} {query_context}".strip()
        matched_name = self.match_place_from_text(combined)
        if matched_name:
            return self.places.get(matched_name)
        return self.get_place(name_or_query.strip())
    
    def search_places(self, keyword: str) -> List[PlaceInfo]:
        """搜索场所"""
        results = []
        keyword = keyword.lower()
        for place in self.places.values():
            if keyword in place.name.lower() or keyword in place.category.lower():
                results.append(place)
        return results
    
    def get_all_places(self) -> List[PlaceInfo]:
        """获取所有场所"""
        return list(self.places.values())
    
    def get_places_by_category(self, category: str) -> List[PlaceInfo]:
        """按类别获取场所"""
        return [place for place in self.places.values() if place.category == category]
    
    def is_in_nanhu_campus(self, place: PlaceInfo) -> bool:
        """检查场所是否在南湖校区内"""
        bounds = self.NANHU_BOUNDS
        return (bounds['min_lat'] <= place.latitude <= bounds['max_lat'] and
                bounds['min_lng'] <= place.longitude <= bounds['max_lng'])
    
    def get_nanhu_places(self) -> List[PlaceInfo]:
        """获取南湖校区内的所有场所"""
        return [place for place in self.places.values() if self.is_in_nanhu_campus(place)]