from fastapi import FastAPI, HTTPException, Depends, status, Header, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
import os
import uuid
from dotenv import load_dotenv
from datetime import datetime
from PIL import Image
import io
import httpx

# 加载环境变量
load_dotenv()

# 导入核心模块
from app.agent import WUTourGuideAgent
from app.schemas import Location, NavigationResponse, PlaceInfo, NearbyPlacesResponse, PlaceIntroductionResponse, UserCreate, UserLogin, UserResponse, TokenResponse, ChangePasswordRequest, ResetPasswordRequest, ChatMessage
from app.extended_schemas import ApiResponse
from app.auth_service import AuthService, SessionLocal, DBUser
from app.fitness_service import FitnessService
from app.checkin_service import CheckinService
from app.community_service import CommunityService

app = FastAPI(title="武汉理工大学智能导游", description="基于LangChain的校园导航助手")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
agent = WUTourGuideAgent()
auth_service = AuthService()
fitness_service = FitnessService()
checkin_service = CheckinService()
community_service = CommunityService()

# 静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

# 认证依赖
async def get_current_user(Authorization: Optional[str] = "") -> str:
    """获取当前用户ID"""
    if not Authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未提供认证令牌")
    if Authorization.startswith("Bearer "):
        Authorization = Authorization[7:]
    try:
        import jwt
        payload = jwt.decode(Authorization, auth_service.SECRET_KEY, algorithms=[auth_service.ALGORITHM])
        return payload.get("sub")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证令牌")

class UserInput(BaseModel):
    query: str
    current_location: Optional[Location] = None
    conversation_history: Optional[List[ChatMessage]] = None

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.post("/api/chat", response_model=NavigationResponse)
async def chat_with_agent(input_data: UserInput):
    """与导游Agent对话"""
    try:
        history = None
        if input_data.conversation_history:
            history = [msg.model_dump() for msg in input_data.conversation_history]
        result = await agent.process_query(
            input_data.query,
            input_data.current_location,
            history,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/places", response_model=List[PlaceInfo])
async def get_all_places():
    """获取所有校内场所信息"""
    return agent.get_all_places()

@app.get("/api/places/categories", response_model=List[str])
async def get_place_categories():
    """获取所有场所类别"""
    return agent.get_categories()

@app.get("/api/places/category/{category}", response_model=List[PlaceInfo])
async def get_places_by_category(category: str):
    """按类别获取场所列表"""
    return agent.get_places_by_category(category)

@app.get("/api/navigate")
async def navigate(
    from_lat: float, 
    from_lng: float, 
    to_place: str
):
    """获取从当前位置到目标地点的导航路线"""
    try:
        start_location = Location(latitude=from_lat, longitude=from_lng)
        result = await agent.get_navigation(start_location, to_place)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/nearby", response_model=NearbyPlacesResponse)
async def get_nearby_places(
    lat: float, 
    lng: float, 
    radius: Optional[int] = 200
):
    """获取附近的场所（实时讲解功能）"""
    try:
        current_location = Location(latitude=lat, longitude=lng)
        return agent.get_nearby_places(current_location, radius)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/check_proximity")
async def check_proximity(
    lat: float, 
    lng: float
):
    """检查是否接近某个场所（50米内自动讲解）"""
    try:
        current_location = Location(latitude=lat, longitude=lng)
        result = agent.check_proximity_and_introduce(current_location)
        if result:
            return result
        else:
            return {
                "status": "success",
                "message": "当前位置附近没有需要讲解的场所",
                "nearby_found": False
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/place/introduction", response_model=PlaceIntroductionResponse)
async def get_place_introduction(
    place_name: str
):
    """获取指定场所的介绍（文字+语音）"""
    try:
        return agent.get_place_introduction(place_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 认证接口 ====================
@app.post("/api/auth/register")
async def register_user(user_create: UserCreate):
    """用户注册"""
    try:
        result = auth_service.register_user(user_create)
        return {
            "success": True,
            "message": result["message"],
            "data": None
        }
    except HTTPException as e:
        return {
            "success": False,
            "message": e.detail,
            "data": None
        }

@app.post("/api/auth/verify-email")
async def verify_email(token: str):
    """邮箱验证"""
    try:
        result = auth_service.verify_email(token)
        return {
            "success": True,
            "message": result["message"],
            "data": None
        }
    except HTTPException as e:
        return {
            "success": False,
            "message": e.detail,
            "data": None
        }

@app.post("/api/auth/login")
async def login_user(user_login: UserLogin):
    """用户登录"""
    try:
        result = auth_service.login_user(user_login)
        return result
    except HTTPException as e:
        return {
            "success": False,
            "message": e.detail
        }

@app.get("/api/auth/debug/users")
async def debug_get_all_users():
    """调试接口：查看所有用户（生产环境应删除）"""
    db = SessionLocal()
    try:
        users = db.query(DBUser).all()
        return {
            "success": True,
            "users": [
                {
                    "id": u.id,
                    "nickname": u.nickname,
                    "email": u.email,
                    "is_active": u.is_active,
                    "registered_at": u.registered_at.isoformat() if u.registered_at else None
                }
                for u in users
            ]
        }
    finally:
        db.close()

@app.post("/api/auth/refresh-token")
async def refresh_token(refresh_token: str):
    """刷新访问令牌"""
    try:
        result = auth_service.refresh_token(refresh_token)
        return {
            "success": True,
            "message": "令牌刷新成功",
            "data": result.dict()
        }
    except HTTPException as e:
        return {
            "success": False,
            "message": e.detail,
            "data": None
        }

@app.get("/api/auth/profile")
async def get_user_profile(authorization: Optional[str] = Header(None)):
    """获取用户信息"""
    try:
        user_id = await get_current_user(authorization or "")
        profile = auth_service.get_profile(user_id)
        return {
            "success": True,
            "message": "获取成功",
            "data": profile
        }
    except HTTPException as e:
        return {
            "success": False,
            "message": e.detail,
            "data": None
        }



class UpdateProfileRequest(BaseModel):
    avatar: Optional[str] = None
    bio: Optional[str] = None
    profile_background: Optional[str] = None

@app.put("/api/auth/profile")
async def update_user_profile(
    request: UpdateProfileRequest,
    authorization: Optional[str] = Header(None)
):
    """更新用户个人信息（支持JSON）"""
    try:
        user_id = await get_current_user(authorization or "")
        result = auth_service.update_profile(
            user_id,
            request.avatar,
            request.bio,
            request.profile_background
        )
        return {
            "success": True,
            "message": result["message"],
            "data": None
        }
    except HTTPException as e:
        return {
            "success": False,
            "message": e.detail,
            "data": None
        }

@app.post("/api/auth/profile/background")
async def upload_profile_background(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    """上传个人主页背景图"""
    try:
        user_id = await get_current_user(authorization or "")

        file_content = await file.read()
        if len(file_content) > 5 * 1024 * 1024:
            return {"success": False, "message": "背景图片不能超过5MB", "data": None}

        content_type = file.content_type or ""
        if content_type not in ["image/jpeg", "image/png", "image/gif", "image/webp"]:
            return {"success": False, "message": "仅支持 JPG / PNG / GIF / WEBP 格式", "data": None}

        ext_map = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/gif": "gif",
            "image/webp": "webp"
        }
        ext = ext_map.get(content_type, "jpg")
        upload_dir = "static/uploads/backgrounds"
        os.makedirs(upload_dir, exist_ok=True)

        file_name = f"{user_id}_{uuid.uuid4().hex[:12]}.{ext}"
        file_path = os.path.join(upload_dir, file_name)
        with open(file_path, "wb") as f:
            f.write(file_content)

        background_url = f"/static/uploads/backgrounds/{file_name}"
        result = auth_service.set_profile_background(user_id, background_url)

        old_bg = result.get("old_background", "")
        if old_bg.startswith("/static/uploads/backgrounds/"):
            old_path = old_bg.lstrip("/")
            if os.path.isfile(old_path):
                try:
                    os.remove(old_path)
                except OSError:
                    pass

        return {
            "success": True,
            "message": result["message"],
            "data": {"url": background_url}
        }
    except HTTPException as e:
        return {"success": False, "message": e.detail, "data": None}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

@app.delete("/api/auth/profile/background")
async def delete_profile_background(authorization: Optional[str] = Header(None)):
    """清除个人主页自定义背景"""
    try:
        user_id = await get_current_user(authorization or "")
        result = auth_service.clear_profile_background(user_id)

        old_bg = result.get("old_background", "")
        if old_bg.startswith("/static/uploads/backgrounds/"):
            old_path = old_bg.lstrip("/")
            if os.path.isfile(old_path):
                try:
                    os.remove(old_path)
                except OSError:
                    pass

        return {"success": True, "message": result["message"], "data": None}
    except HTTPException as e:
        return {"success": False, "message": e.detail, "data": None}

@app.post("/api/auth/status")
async def set_user_status(status: str = Form(...), authorization: Optional[str] = Header(None)):
    """设置用户状态（emoji，维持6小时）"""
    try:
        user_id = await get_current_user(authorization or "")
        result = auth_service.set_status(user_id, status)
        return {
            "success": True,
            "message": result["message"],
            "data": {
                "status": result["status"],
                "expires_at": result["expires_at"]
            }
        }
    except HTTPException as e:
        return {
            "success": False,
            "message": e.detail,
            "data": None
        }

@app.post("/api/auth/change-password")
async def change_password(request: ChangePasswordRequest, authorization: Optional[str] = Header(None)):
    """修改密码"""
    try:
        user_id = await get_current_user(authorization or "")
        result = auth_service.change_password(user_id, request.old_password, request.new_password)
        return {
            "success": True,
            "message": result["message"],
            "data": None
        }
    except HTTPException as e:
        return {
            "success": False,
            "message": e.detail,
            "data": None
        }

@app.post("/api/auth/forgot-password")
async def forgot_password(email: str):
    """忘记密码"""
    try:
        result = auth_service.forgot_password(email)
        return {
            "success": True,
            "message": result["message"],
            "data": None
        }
    except HTTPException as e:
        return {
            "success": False,
            "message": e.detail,
            "data": None
        }

@app.post("/api/auth/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """重置密码"""
    try:
        result = auth_service.reset_password(request.token, request.new_password)
        return {
            "success": True,
            "message": result["message"],
            "data": None
        }
    except HTTPException as e:
        return {
            "success": False,
            "message": e.detail,
            "data": None
        }

# ==================== 运动健康接口 ====================
@app.post("/api/fitness/start", response_model=ApiResponse)
async def start_workout(
    workout_type: str,
    start_latitude: float,
    start_longitude: float,
    Authorization: Optional[str] = Header(None)
):
    """开始运动"""
    try:
        user_id = await get_current_user(Authorization or "")
        from app.extended_schemas import WorkoutType as WT, Location
        workout_type_enum = WT(workout_type)
        start_location = Location(latitude=start_latitude, longitude=start_longitude)
        workout_id = await fitness_service.start_workout(user_id, workout_type_enum, start_location)
        return ApiResponse(
            success=True,
            message="运动已开始",
            data={"workout_id": workout_id}
        )
    except ValueError as e:
        return ApiResponse(success=False, message=str(e))
    except HTTPException as e:
        return ApiResponse(success=False, message=e.detail)
    except Exception as e:
        return ApiResponse(success=False, message=str(e))

@app.post("/api/fitness/update", response_model=ApiResponse)
async def update_workout(
    workout_id: int,
    latitude: float,
    longitude: float,
    Authorization: Optional[str] = Header(None)
):
    """更新运动位置"""
    try:
        user_id = await get_current_user(Authorization or "")
        from app.extended_schemas import Location
        location = Location(latitude=latitude, longitude=longitude)
        result = await fitness_service.update_workout(user_id, workout_id, location)
        return ApiResponse(
            success=True,
            message="更新成功",
            data=result
        )
    except ValueError as e:
        return ApiResponse(success=False, message=str(e))
    except HTTPException as e:
        return ApiResponse(success=False, message=e.detail)
    except Exception as e:
        return ApiResponse(success=False, message=str(e))

@app.post("/api/fitness/end", response_model=ApiResponse)
async def end_workout(
    workout_id: int,
    distance: Optional[float] = None,
    duration: Optional[int] = None,
    calories: Optional[float] = None,
    Authorization: Optional[str] = Header(None)
):
    """结束运动"""
    try:
        user_id = await get_current_user(Authorization or "")
        user = auth_service.get_user_by_id(user_id)
        weight = user.weight if user and hasattr(user, 'weight') and user.weight else None
        summary = await fitness_service.end_workout(user_id, workout_id, weight, distance, duration, calories)
        return ApiResponse(
            success=True,
            message="运动已结束",
            data=summary.dict()
        )
    except ValueError as e:
        return ApiResponse(success=False, message=str(e))
    except HTTPException as e:
        return ApiResponse(success=False, message=e.detail)
    except Exception as e:
        return ApiResponse(success=False, message=str(e))

@app.get("/api/fitness/statistics", response_model=ApiResponse)
async def get_fitness_stats(
    period: str = "week",
    Authorization: Optional[str] = Header(None)
):
    """获取运动统计"""
    try:
        user_id = await get_current_user(Authorization or "")
        from app.extended_schemas import FitnessStatsPeriod as FSP
        period_enum = FSP(period)
        stats = await fitness_service.get_fitness_stats(user_id, period_enum)
        return ApiResponse(
            success=True,
            message="获取成功",
            data=stats.dict()
        )
    except ValueError as e:
        return ApiResponse(success=False, message=str(e))
    except HTTPException as e:
        return ApiResponse(success=False, message=e.detail)
    except Exception as e:
        return ApiResponse(success=False, message=str(e))

@app.get("/api/fitness/history", response_model=ApiResponse)
async def get_workout_history(
    limit: int = 20,
    Authorization: Optional[str] = Header(None)
):
    """获取运动历史"""
    try:
        user_id = await get_current_user(Authorization or "")
        history = await fitness_service.get_workout_history(user_id, limit)
        return ApiResponse(
            success=True,
            message="获取成功",
            data=history
        )
    except HTTPException as e:
        return ApiResponse(success=False, message=e.detail)
    except Exception as e:
        return ApiResponse(success=False, message=str(e))

# ==================== 打卡接口 ====================
@app.post("/api/checkin", response_model=ApiResponse)
async def checkin(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    place_id: Optional[int] = None,
    place_name: Optional[str] = None,
    place_latitude: Optional[float] = None,
    place_longitude: Optional[float] = None,
    geofence_radius: int = 20,
    Authorization: Optional[str] = Header(None)
):
    """打卡（基于时间段自动匹配活动）"""
    try:
        user_id = await get_current_user(Authorization or "")
        from app.extended_schemas import Location
        
        user_location = Location(latitude=latitude or 0, longitude=longitude or 0) if latitude and longitude else None
        place_location = Location(latitude=place_latitude or 0, longitude=place_longitude or 0) if place_latitude and place_longitude else None
        
        result = await checkin_service.checkin(
            user_id, user_location, place_id, place_name, place_location, geofence_radius
        )
        achievements_data = [a.dict() for a in result.new_achievements] if result.new_achievements else []
        return ApiResponse(
            success=result.success,
            message=result.message,
            data={
                "message": result.message,
                "place_name": result.place_name,
                "new_achievements": achievements_data
            }
        )
    except HTTPException as e:
        return ApiResponse(success=False, message=e.detail)
    except Exception as e:
        return ApiResponse(success=False, message=str(e))

@app.get("/api/checkin/history", response_model=ApiResponse)
async def get_checkin_history(
    limit: int = 50,
    Authorization: Optional[str] = Header(None)
):
    """获取打卡历史"""
    try:
        user_id = await get_current_user(Authorization or "")
        history = await checkin_service.get_checkin_history(user_id, limit)
        history_list = [h.dict() for h in history]
        return ApiResponse(
            success=True,
            message="获取成功",
            data=history_list
        )
    except HTTPException as e:
        return ApiResponse(success=False, message=e.detail)
    except Exception as e:
        return ApiResponse(success=False, message=str(e))

@app.get("/api/checkin/achievements", response_model=ApiResponse)
async def get_achievements(Authorization: Optional[str] = Header(None)):
    """获取成就列表"""
    try:
        user_id = await get_current_user(Authorization or "")
        earned, not_earned = await checkin_service.get_all_achievements(user_id)
        earned_list = [{"achievement": ea.achievement.dict(), "earned_at": ea.earned_at.isoformat()} for ea in earned]
        not_earned_list = [a.dict() for a in not_earned]
        return ApiResponse(
            success=True,
            message="获取成功",
            data={
                "earned": earned_list,
                "not_earned": not_earned_list
            }
        )
    except HTTPException as e:
        return ApiResponse(success=False, message=e.detail)
    except Exception as e:
        return ApiResponse(success=False, message=str(e))

@app.get("/api/checkin/statistics", response_model=ApiResponse)
async def get_checkin_statistics(Authorization: Optional[str] = Header(None)):
    """获取打卡统计"""
    try:
        user_id = await get_current_user(Authorization or "")
        stats = await checkin_service.get_checkin_statistics(user_id)
        return ApiResponse(
            success=True,
            message="获取成功",
            data=stats
        )
    except HTTPException as e:
        return ApiResponse(success=False, message=e.detail)
    except Exception as e:
        return ApiResponse(success=False, message=str(e))

# ==================== 社区接口 ====================
@app.get("/api/community/feed", response_model=ApiResponse)
async def get_feed(
    page: int = 1,
    page_size: int = 20,
    Authorization: Optional[str] = Header(None)
):
    """获取动态列表"""
    try:
        user_id = await get_current_user(Authorization or "") if Authorization else None
        posts = await community_service.get_feed(user_id, page, page_size)
        posts_list = []
        for post in posts:
            post_dict = post.dict()
            if 'comments' in post_dict and post_dict['comments']:
                post_dict['comments'] = [c.dict() for c in post_dict['comments']]
            posts_list.append(post_dict)
        return ApiResponse(
            success=True,
            message="获取成功",
            data=posts_list
        )
    except HTTPException as e:
        return ApiResponse(success=False, message=e.detail)
    except Exception as e:
        return ApiResponse(success=False, message=str(e))

@app.post("/api/community/post", response_model=ApiResponse)
async def create_post(
    content: Optional[str] = Form(None),
    Authorization: Optional[str] = Header(None),
    images: Optional[str] = Form(None),
    location_name: Optional[str] = Form(None),
    campus: Optional[str] = Form(None)
):
    """发布动态"""
    try:
        user_id = await get_current_user(Authorization or "")
        images_list = []
        if images:
            import json
            try:
                images_list = json.loads(images)
            except:
                images_list = images.split(',')
        post = await community_service.create_post(user_id, content, images_list, location_name, campus)
        return ApiResponse(
            success=True,
            message="发布成功",
            data=post.dict()
        )
    except HTTPException as e:
        return ApiResponse(success=False, message=e.detail)
    except Exception as e:
        return ApiResponse(success=False, message=str(e))

@app.post("/api/community/like", response_model=ApiResponse)
async def like_post(
    post_id: int,
    Authorization: Optional[str] = Header(None)
):
    """点赞/取消点赞"""
    try:
        user_id = await get_current_user(Authorization or "")
        success = await community_service.like_post(user_id, post_id)
        if success:
            return ApiResponse(success=True, message="操作成功")
        else:
            return ApiResponse(success=False, message="帖子不存在")
    except HTTPException as e:
        return ApiResponse(success=False, message=e.detail)
    except Exception as e:
        return ApiResponse(success=False, message=str(e))

@app.delete("/api/community/post/{post_id}", response_model=ApiResponse)
async def delete_post(
    post_id: int,
    Authorization: Optional[str] = Header(None)
):
    """删除动态"""
    try:
        user_id = await get_current_user(Authorization or "")
        success = await community_service.delete_post(user_id, post_id)
        if success:
            return ApiResponse(success=True, message="删除成功")
        else:
            return ApiResponse(success=False, message="帖子不存在或无权删除")
    except HTTPException as e:
        return ApiResponse(success=False, message=e.detail)
    except Exception as e:
        return ApiResponse(success=False, message=str(e))

@app.post("/api/community/comment", response_model=ApiResponse)
async def comment_post(
    post_id: int,
    content: str,
    Authorization: Optional[str] = Header(None)
):
    """评论动态"""
    try:
        user_id = await get_current_user(Authorization or "")
        comment = await community_service.comment_post(user_id, post_id, content)
        if comment:
            return ApiResponse(
                success=True,
                message="评论成功",
                data=comment.dict()
            )
        else:
            return ApiResponse(success=False, message="帖子不存在")
    except HTTPException as e:
        return ApiResponse(success=False, message=e.detail)
    except Exception as e:
        return ApiResponse(success=False, message=str(e))

@app.get("/api/community/comments", response_model=ApiResponse)
async def get_comments(
    post_id: int,
    Authorization: Optional[str] = Header(None)
):
    """获取动态评论"""
    try:
        user_id = await get_current_user(Authorization or "")
        post = await community_service.get_post(post_id, user_id)
        if post:
            return ApiResponse(
                success=True,
                message="获取成功",
                data=post.comments or []
            )
        else:
            return ApiResponse(success=False, message="帖子不存在")
    except HTTPException as e:
        return ApiResponse(success=False, message=e.detail)
    except Exception as e:
        return ApiResponse(success=False, message=str(e))

@app.get("/api/community/user-posts", response_model=ApiResponse)
async def get_user_posts(
    page: int = 1,
    page_size: int = 20,
    Authorization: Optional[str] = Header(None)
):
    """获取用户动态"""
    try:
        user_id = await get_current_user(Authorization or "")
        posts = await community_service.get_user_posts(user_id, page, page_size)
        total = await community_service.get_user_post_count(user_id)
        posts_list = []
        for post in posts:
            post_dict = post.dict()
            if 'comments' in post_dict and post_dict['comments']:
                post_dict['comments'] = [c.dict() for c in post_dict['comments']]
            posts_list.append(post_dict)
        return ApiResponse(
            success=True,
            message="获取成功",
            data={
                "posts": posts_list,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        )
    except HTTPException as e:
        return ApiResponse(success=False, message=e.detail)
    except Exception as e:
        return ApiResponse(success=False, message=str(e))

@app.get("/api/community/search", response_model=ApiResponse)
async def search_posts(
    keyword: str,
    page: int = 1,
    page_size: int = 20,
    Authorization: Optional[str] = Header(None)
):
    """搜索动态"""
    try:
        posts = await community_service.search_posts(keyword, page, page_size)
        posts_list = [post.dict() for post in posts]
        return ApiResponse(
            success=True,
            message="获取成功",
            data=posts_list
        )
    except HTTPException as e:
        return ApiResponse(success=False, message=e.detail)
    except Exception as e:
        return ApiResponse(success=False, message=str(e))

# ==================== 图片上传接口 ====================
@app.post("/api/community/upload-images")
async def upload_images(
    files: List[UploadFile] = File(...),
    Authorization: Optional[str] = Header(None)
):
    """上传图片（最多9张，单张<2MB，支持JPG/PNG/GIF）"""
    try:
        user_id = await get_current_user(Authorization or "")
        
        if len(files) > 9:
            return ApiResponse(success=False, message="最多支持上传9张图片")
        
        UPLOAD_DIR = "static/uploads/posts"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        results = []
        
        for file in files:
            # 检查文件大小
            file_content = await file.read()
            if len(file_content) > 2 * 1024 * 1024:
                return ApiResponse(success=False, message=f"图片 {file.filename} 超过2MB限制")
            
            # 检查文件格式
            content_type = file.content_type
            if content_type not in ["image/jpeg", "image/png", "image/gif"]:
                return ApiResponse(success=False, message=f"图片 {file.filename} 格式不支持，仅支持JPG/PNG/GIF")
            
            # 生成文件名
            ext = content_type.split("/")[1]
            file_name = f"{uuid.uuid4()}.{ext}"
            thumbnail_name = f"{uuid.uuid4()}_thumb.{ext}"
            
            # 保存原图
            file_path = os.path.join(UPLOAD_DIR, file_name)
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            # 生成缩略图 (300x300)
            thumbnail_path = os.path.join(UPLOAD_DIR, thumbnail_name)
            try:
                img = Image.open(io.BytesIO(file_content))
                img.thumbnail((300, 300))
                img.save(thumbnail_path)
            except Exception as e:
                thumbnail_path = file_path
                thumbnail_name = file_name
            
            # 构建相对URL (避免0.0.0.0问题)
            image_url = f"/static/uploads/posts/{file_name}"
            thumbnail_url = f"/static/uploads/posts/{thumbnail_name}"
            
            results.append({
                "image_url": image_url,
                "thumbnail_url": thumbnail_url
            })
        
        return ApiResponse(
            success=True,
            message="上传成功",
            data=results
        )
    except HTTPException as e:
        return ApiResponse(success=False, message=e.detail)
    except Exception as e:
        return ApiResponse(success=False, message=str(e))

# ==================== 位置解析接口 ====================
@app.get("/api/community/reverse-geocode")
async def reverse_geocode(
    lat: float,
    lng: float
):
    """反向地理编码，获取地点名称和校区信息"""
    try:
        amap_key = os.getenv("AMAP_WEB_SERVICE_KEY")
        if not amap_key:
            raise HTTPException(status_code=500, detail="未配置高德地图API密钥")
        
        # 调用高德地图反向地理编码API
        url = f"https://restapi.amap.com/v3/geocode/regeo?location={lng},{lat}&key={amap_key}&radius=1000&extensions=all"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
        
        if data.get("status") != "1":
            return {
                "success": False,
                "message": "地理编码失败",
                "data": None
            }
        
        regeocode = data.get("regeocode", {})
        formatted_address = regeocode.get("formatted_address", "")
        address_component = regeocode.get("addressComponent", {})
        
        # 提取校区信息
        campus = ""
        building_name = ""
        
        district = address_component.get("district", "")
        street = address_component.get("street", "")
        street_number = address_component.get("streetNumber", "")
        
        # 判断校区
        location_desc = formatted_address + " " + district + " " + street
        if "南湖" in location_desc:
            campus = "南湖"
        elif "马房山" in location_desc:
            campus = "马房山"
        elif "余家头" in location_desc:
            campus = "余家头"
        
        # 提取建筑名称
        poi_list = regeocode.get("pois", [])
        if poi_list:
            for poi in poi_list:
                if "武汉理工大学" in poi.get("name", ""):
                    building_name = poi.get("name", "").replace("武汉理工大学", "").strip()
                    break
        
        return {
            "success": True,
            "message": "解析成功",
            "data": {
                "place_name": formatted_address,
                "campus": campus,
                "building_name": building_name,
                "district": district,
                "street": street,
                "street_number": street_number
            }
        }
    except HTTPException as e:
        return {"success": False, "message": e.detail, "data": None}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

# ==================== 景点讲解接口 ====================
@app.get("/api/guide/favorites", response_model=ApiResponse)
async def get_favorites(Authorization: Optional[str] = Header(None)):
    """获取收藏列表"""
    try:
        user_id = await get_current_user(Authorization or "")
        places = agent.get_all_places()
        return ApiResponse(
            success=True,
            message="获取成功",
            data=[p.dict() for p in places[:5]]
        )
    except HTTPException as e:
        return ApiResponse(success=False, message=e.detail)
    except Exception as e:
        return ApiResponse(success=False, message=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )