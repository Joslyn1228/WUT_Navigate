from pydantic import BaseModel
from typing import Optional, List

class Location(BaseModel):
    """地理位置信息"""
    latitude: float
    longitude: float
    address: Optional[str] = None

class PlaceInfo(BaseModel):
    """场所信息"""
    name: str
    category: str
    description: str
    latitude: float
    longitude: float
    image_url: Optional[str] = None
    voice_description: Optional[str] = None
    distance: Optional[float] = None  # 距用户当前位置的距离

class NearbyPlace(BaseModel):
    """附近场所信息"""
    place: PlaceInfo
    distance: float  # 距离（米）

class NavigationStep(BaseModel):
    """导航步骤"""
    instruction: str
    distance: float
    duration: int
    latitude: float
    longitude: float

class NavigationResponse(BaseModel):
    """导航响应"""
    status: str
    message: str
    destination: Optional[str] = None
    total_distance: Optional[float] = None
    total_duration: Optional[int] = None
    steps: Optional[List[NavigationStep]] = None
    place_info: Optional[Location] = None
    response_type: str = "text"  # text, navigation, introduction, nearby

class AgentResponse(BaseModel):
    """Agent响应"""
    text: str
    response_type: str = "text"
    data: Optional[dict] = None

class NearbyPlacesResponse(BaseModel):
    """附近场所响应"""
    status: str
    message: str
    nearby_places: List[NearbyPlace]
    current_location: Optional[Location] = None

class PlaceIntroductionResponse(BaseModel):
    """场所介绍响应"""
    status: str
    message: str
    place: PlaceInfo
    is_nearby: bool = False  # 是否在附近（50米内）

# 用户认证相关模型

class UserCreate(BaseModel):
    """用户注册请求"""
    nickname: str
    email: str
    password: str
    confirm_password: str

class UserLogin(BaseModel):
    """用户登录请求"""
    email: str
    password: str
    remember_me: Optional[bool] = False

class UserResponse(BaseModel):
    """用户信息响应"""
    id: str
    nickname: str
    email: str
    is_active: bool
    registered_at: Optional[str] = None
    last_login_at: Optional[str] = None

class TokenResponse(BaseModel):
    """令牌响应"""
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse

class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str
    new_password: str

class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    token: str
    new_password: str