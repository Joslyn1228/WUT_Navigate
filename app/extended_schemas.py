"""
扩展数据模型 - 包含所有核心模块的数据定义
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== 用户相关 ====================
class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., max_length=50)
    email: EmailStr
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6)


class User(UserBase):
    """用户模型"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """用户更新模型"""
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str


class UserInDB(BaseModel):
    """数据库用户模型"""
    id: str
    nickname: str
    email: str
    hashed_password: str
    is_active: bool = False
    registered_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None


class Token(BaseModel):
    """Token模型"""
    access_token: str
    token_type: str
    expires_in: int


# ==================== 景点相关 ====================
class PlaceType(str, Enum):
    """景点类型"""
    LIBRARY = "图书馆"
    TEACHING_BUILDING = "教学楼"
    SPORTS_GROUND = "体育场馆"
    CAMPUS = "校区"
    OFFICE_BUILDING = "办公楼"
    ACTIVITY_CENTER = "活动场所"
    DINING_HALL = "餐饮"
    LANDMARK = "地标建筑"


class PlaceBase(BaseModel):
    """景点基础模型"""
    name: str = Field(..., max_length=100)
    category: PlaceType
    description: Optional[str] = None
    latitude: float
    longitude: float
    geofence_radius: int = Field(default=20, description="电子围栏半径（米）")
    voice_url: Optional[str] = None
    video_url: Optional[str] = None
    images: Optional[List[str]] = None
    is_checkpoint: bool = False


class PlaceCreate(PlaceBase):
    """景点创建模型"""
    pass


class Place(PlaceBase):
    """景点模型"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class PlaceWithDistance(Place):
    """带距离的景点"""
    distance: Optional[float] = None


# ==================== 导航相关 ====================
class NavigationMode(str, Enum):
    """导航模式"""
    WALKING = "walking"
    RIDING = "riding"
    SHUTTLE = "shuttle"


class NavigationStep(BaseModel):
    """导航步骤"""
    instruction: str
    distance: float
    duration: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class Route(BaseModel):
    """导航路线"""
    start_location: "Location"
    destination_location: "Location"
    mode: NavigationMode
    total_distance: float
    total_duration: int
    steps: List[NavigationStep]
    route_polyline: Optional[str] = None


class Location(BaseModel):
    """地理位置"""
    latitude: float
    longitude: float
    address: Optional[str] = None


class NavigationRequest(BaseModel):
    """导航请求"""
    start: Location
    destination: Location
    mode: NavigationMode = NavigationMode.WALKING


class NavigationResponse(BaseModel):
    """导航响应"""
    status: str
    message: str
    route: Optional[Route] = None
    destination: Optional[str] = None
    total_distance: Optional[float] = None


# ==================== 运动健康相关 ====================
class WorkoutType(str, Enum):
    """运动类型"""
    WALKING = "walking"
    RUNNING = "running"
    CYCLING = "cycling"


class WorkoutBase(BaseModel):
    """运动基础模型"""
    workout_type: WorkoutType
    start_time: datetime


class WorkoutCreate(WorkoutBase):
    """运动创建模型"""
    pass


class WorkoutUpdate(BaseModel):
    """运动更新模型"""
    current_location: Location


class WorkoutSummary(BaseModel):
    """运动总结"""
    workout_id: int
    user_id: str
    workout_type: WorkoutType
    start_time: datetime
    end_time: datetime
    duration: int
    distance: float
    calories: float
    start_location: Optional[Location] = None
    end_location: Optional[Location] = None


class Workout(WorkoutBase):
    """运动模型"""
    id: Optional[int] = None
    workout_id: Optional[int] = None
    user_id: str
    start_location: Optional[Location] = None
    end_time: Optional[datetime] = None
    end_location: Optional[Location] = None
    duration: int = 0
    distance: float = 0.0
    calories: float = 0.0
    route: List[Dict[str, float]] = []
    total_distance: Optional[float] = None
    total_duration: Optional[int] = None
    calories_burned: Optional[float] = None
    route_points: Optional[List[Location]] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class FitnessStatsPeriod(str, Enum):
    """统计周期"""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL = "all"


class FitnessStats(BaseModel):
    """运动统计"""
    period: FitnessStatsPeriod
    total_distance: float
    total_duration: int
    total_calories: float
    workout_count: int
    avg_distance: float
    avg_duration: int


# ==================== 社区相关 ====================
class PostBase(BaseModel):
    """帖子基础模型"""
    content: str
    images: Optional[List[Dict[str, Any]]] = None
    location: Optional[str] = None


class PostCreate(PostBase):
    """帖子创建模型"""
    pass


class CommentBase(BaseModel):
    """评论基础模型"""
    content: str


class CommentCreate(CommentBase):
    """评论创建模型"""
    pass


class Comment(CommentBase):
    """评论模型"""
    id: int
    post_id: int
    user_id: str
    user_nickname: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class Post(PostBase):
    """帖子模型"""
    id: int
    user_id: str
    user_nickname: Optional[str] = None
    user_avatar: Optional[str] = None
    likes_count: int = 0
    comments_count: int = 0
    created_at: datetime
    is_liked: bool = False
    comments: Optional[List[Comment]] = None
    
    class Config:
        from_attributes = True


# ==================== 打卡相关 ====================
class CheckinResult(BaseModel):
    """打卡结果"""
    success: bool
    message: str
    place_name: Optional[str] = None
    new_achievements: Optional[List["Achievement"]] = None
    consecutive_days: Optional[int] = 0  # 连续打卡天数


class CheckinRecord(BaseModel):
    """打卡记录"""
    id: int
    user_id: str = ""
    place_id: int = 0
    place_name: str = ""
    checkin_time: datetime
    latitude: float = 0.0
    longitude: float = 0.0
    
    class Config:
        from_attributes = True


class AchievementType(str, Enum):
    """成就类型"""
    CHECKIN = "checkin"
    FITNESS = "fitness"
    COLLECTION = "collection"
    STREAK = "streak"
    EXPLORE = "explore"
    HIDDEN = "hidden"


class AchievementBase(BaseModel):
    """成就基础模型"""
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    type: AchievementType
    required_count: int = 1
    rarity: Optional[str] = "common"
    hidden: Optional[bool] = False
    display_name: Optional[str] = None
    display_desc: Optional[str] = None


class Achievement(AchievementBase):
    """成就模型"""
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserAchievement(BaseModel):
    """用户成就"""
    achievement: Achievement
    earned_at: datetime
    is_new: bool = False


# ==================== 讲解相关 ====================
class GuideMediaType(str, Enum):
    """讲解媒体类型"""
    TEXT = "text"
    VOICE = "voice"
    VIDEO = "video"
    IMAGES = "images"


class GuideContent(BaseModel):
    """讲解内容"""
    place_id: int
    place_name: str
    text: str
    voice_url: Optional[str] = None
    video_url: Optional[str] = None
    images: Optional[List[str]] = None
    is_favorited: bool = False


class FavoritePlace(BaseModel):
    """收藏景点"""
    user_id: int
    place_id: int
    added_at: datetime


# ==================== 通用响应 ====================
class ApiResponse(BaseModel):
    """通用API响应"""
    success: bool
    message: str
    data: Optional[Any] = None


class ListResponse(BaseModel):
    """列表响应"""
    items: List[Any]
    total: int
    page: int
    page_size: int


# 确保前向引用可用
Route.update_forward_refs()
CheckinResult.update_forward_refs()
