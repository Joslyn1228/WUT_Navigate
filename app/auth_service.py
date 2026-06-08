import bcrypt
import jwt
import time
import uuid
import re
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from app.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from app.extended_schemas import UserInDB

from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Integer, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./wut_auth.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    pool_size=20,
    max_overflow=50,
    pool_timeout=30,
    pool_recycle=1800
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class DBUser(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    nickname = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=False)
    registered_at = Column(DateTime)
    last_login_at = Column(DateTime)
    avatar = Column(String, default="")
    bio = Column(String, default="")
    status = Column(String, default="")
    status_expires_at = Column(DateTime)

class DBCheckin(Base):
    __tablename__ = "checkins"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, index=True)
    place_name = Column(String)
    checkin_time = Column(DateTime)
    latitude = Column(Float, default=0.0)
    longitude = Column(Float, default=0.0)
    activity_id = Column(String, default="")

class DBAchievement(Base):
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, index=True)
    achievement_id = Column(String)
    unlocked_at = Column(DateTime)

class DBActivityCount(Base):
    __tablename__ = "activity_counts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, index=True)
    activity_id = Column(String)
    count = Column(Integer, default=0)

class DBPost(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, index=True)
    content = Column(Text)
    location_name = Column(String, default="")
    latitude = Column(Float, default=0.0)
    longitude = Column(Float, default=0.0)
    campus = Column(String, default="")
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class DBPostImage(Base):
    __tablename__ = "post_images"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    post_id = Column(Integer, index=True)
    image_url = Column(String)
    thumbnail_url = Column(String)
    sort_order = Column(Integer, default=0)

class DBPostLike(Base):
    __tablename__ = "post_likes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    post_id = Column(Integer, index=True)
    user_id = Column(String, index=True)
    created_at = Column(DateTime)

class DBPostComment(Base):
    __tablename__ = "post_comments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    post_id = Column(Integer, index=True)
    user_id = Column(String, index=True)
    parent_comment_id = Column(Integer, index=True, default=0)
    content = Column(Text)
    created_at = Column(DateTime)

class DBPostFavorite(Base):
    __tablename__ = "post_favorites"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    post_id = Column(Integer, index=True)
    user_id = Column(String, index=True)
    created_at = Column(DateTime)

class DBWorkout(Base):
    __tablename__ = "workouts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, index=True)
    workout_type = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    total_distance = Column(Float, default=0.0)
    total_duration = Column(Integer, default=0)
    calories_burned = Column(Float, default=0.0)
    avg_speed = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)

class DBWorkoutRoute(Base):
    __tablename__ = "workout_routes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    workout_id = Column(Integer, index=True)
    latitude = Column(Float, default=0.0)
    longitude = Column(Float, default=0.0)
    timestamp = Column(DateTime)
    sequence = Column(Integer, default=0)

Base.metadata.create_all(bind=engine)

class AuthService:
    def __init__(self):
        self.login_attempts: Dict[str, int] = {}
        self.login_attempt_timestamps: Dict[str, int] = {}
        self.verification_tokens: Dict[str, str] = {}
        self.MAX_LOGIN_ATTEMPTS = 5
        self.LOCKOUT_DURATION = 300
        self.SECRET_KEY = "wuhan_university_of_technology_secret_key_2024"
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 43200
        self.REFRESH_TOKEN_EXPIRE_DAYS = 30

    def get_db(self):
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def validate_email(self, email: str) -> bool:
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

    def validate_password(self, password: str) -> bool:
        if len(password) < 8 or len(password) > 20:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?`~' for c in password)
        
        count = 0
        if has_upper: count += 1
        if has_lower: count += 1
        if has_digit: count += 1
        if has_special: count += 1
        
        return count >= 2

    def validate_nickname(self, nickname: str) -> bool:
        if len(nickname) < 2 or len(nickname) > 20:
            return False
        pattern = r'^[\u4e00-\u9fa5a-zA-Z0-9_]+$'
        return re.match(pattern, nickname) is not None

    def hash_password(self, password: str) -> bytes:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def verify_password(self, plain_password: str, hashed_password: bytes) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        expire = datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode = data.copy()
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def register_user(self, user_create: UserCreate) -> Dict[str, str]:
        db = next(self.get_db())
        
        if not self.validate_nickname(user_create.nickname):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="昵称格式错误：2-20个字符，允许中英文、数字和下划线"
            )
        
        if not self.validate_email(user_create.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱格式不正确"
            )
        
        if not self.validate_password(user_create.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="密码要求：8-20位，包含大小写字母、数字和特殊符号至少两种组合"
            )
        
        if user_create.password != user_create.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="两次输入的密码不一致"
            )
        
        existing_user = db.query(DBUser).filter(DBUser.email == user_create.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被注册"
            )
        
        hashed_password = self.hash_password(user_create.password)
        verification_token = str(uuid.uuid4())
        
        db_user = DBUser(
            id=str(uuid.uuid4()),
            nickname=user_create.nickname,
            email=user_create.email,
            hashed_password=hashed_password.decode('utf-8'),
            is_active=True,
            registered_at=datetime.utcnow()
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return {
            "message": "注册成功，您可以立即登录"
        }

    def verify_email(self, token: str) -> Dict[str, str]:
        user_id = self.verification_tokens.get(token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的验证链接"
            )
        
        db = next(self.get_db())
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户不存在"
            )
        
        if user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="账号已激活"
            )
        
        user.is_active = True
        db.commit()
        del self.verification_tokens[token]
        
        return {"message": "邮箱验证成功，账号已激活"}

    def login_user(self, user_login: UserLogin) -> TokenResponse:
        email = user_login.email
        password = user_login.password
        
        current_time = time.time()
        
        attempts = self.login_attempts.get(email, 0)
        last_attempt_time = self.login_attempt_timestamps.get(email, 0)
        
        if attempts >= self.MAX_LOGIN_ATTEMPTS:
            if current_time - last_attempt_time < self.LOCKOUT_DURATION:
                remaining = int(self.LOCKOUT_DURATION - (current_time - last_attempt_time))
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=f"账号已锁定，请{remaining}秒后再试"
                )
            else:
                self.login_attempts[email] = 0
        
        db = next(self.get_db())
        user = db.query(DBUser).filter(DBUser.email == email).first()
        
        if not user:
            self.login_attempts[email] = attempts + 1
            self.login_attempt_timestamps[email] = current_time
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="账号未激活，请先验证邮箱"
            )
        
        if not self.verify_password(password, user.hashed_password.encode('utf-8')):
            self.login_attempts[email] = attempts + 1
            self.login_attempt_timestamps[email] = current_time
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误"
            )
        
        self.login_attempts[email] = 0
        user.last_login_at = datetime.utcnow()
        db.commit()
        
        access_token_expires = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.id, "nickname": user.nickname, "email": user.email},
            expires_delta=access_token_expires
        )
        refresh_token = self.create_refresh_token(data={"sub": user.id})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                nickname=user.nickname,
                email=user.email,
                is_active=user.is_active,
                registered_at=user.registered_at.isoformat() if user.registered_at else None,
                last_login_at=user.last_login_at.isoformat() if user.last_login_at else None
            )
        )

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的刷新令牌"
                )
            
            user_id = payload.get("sub")
            
            db = next(self.get_db())
            user = db.query(DBUser).filter(DBUser.id == user_id).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户不存在"
                )
            
            access_token_expires = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self.create_access_token(
                data={"sub": user.id, "nickname": user.nickname, "email": user.email},
                expires_delta=access_token_expires
            )
            new_refresh_token = self.create_refresh_token(data={"sub": user.id})
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                user=UserResponse(
                    id=user.id,
                    nickname=user.nickname,
                    email=user.email,
                    is_active=user.is_active,
                    registered_at=user.registered_at.isoformat() if user.registered_at else None,
                    last_login_at=user.last_login_at.isoformat() if user.last_login_at else None
                )
            )
        
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌"
            )

    def get_user_by_id(self, user_id: str) -> Optional[DBUser]:
        db = next(self.get_db())
        return db.query(DBUser).filter(DBUser.id == user_id).first()

    def change_password(self, user_id: str, old_password: str, new_password: str) -> Dict[str, str]:
        db = next(self.get_db())
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        if not self.verify_password(old_password, user.hashed_password.encode('utf-8')):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="原密码错误"
            )
        
        if not self.validate_password(new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新密码要求：8-20位，包含大小写字母、数字和特殊符号至少两种组合"
            )
        
        user.hashed_password = self.hash_password(new_password).decode('utf-8')
        db.commit()
        
        return {"message": "密码修改成功"}

    def forgot_password(self, email: str) -> Dict[str, str]:
        db = next(self.get_db())
        user = db.query(DBUser).filter(DBUser.email == email).first()
        
        if not user:
            return {"message": "如果该邮箱已注册，将发送重置链接"}
        
        reset_token = str(uuid.uuid4())
        self.verification_tokens[reset_token] = user.id
        
        return {
            "message": "如果该邮箱已注册，将发送重置链接",
            "reset_token": reset_token
        }

    def reset_password(self, token: str, new_password: str) -> Dict[str, str]:
        user_id = self.verification_tokens.get(token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的重置链接"
            )
        
        db = next(self.get_db())
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户不存在"
            )
        
        if not self.validate_password(new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="密码要求：8-20位，包含大小写字母、数字和特殊符号至少两种组合"
            )
        
        user.hashed_password = self.hash_password(new_password).decode('utf-8')
        db.commit()
        del self.verification_tokens[token]
        
        return {"message": "密码重置成功"}

    def update_profile(self, user_id: str, avatar: Optional[str] = None, bio: Optional[str] = None) -> Dict[str, str]:
        db = next(self.get_db())
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        if avatar is not None:
            user.avatar = avatar
        
        if bio is not None:
            user.bio = bio[:100]
        
        db.commit()
        
        return {"message": "个人信息更新成功"}

    def set_status(self, user_id: str, status: str) -> Dict[str, str]:
        db = next(self.get_db())
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        if len(status) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="状态最多10个字符"
            )
        
        user.status = status
        user.status_expires_at = datetime.utcnow() + timedelta(hours=6)
        
        db.commit()
        
        return {
            "message": "状态设置成功",
            "status": status,
            "expires_at": user.status_expires_at.isoformat()
        }

    def get_profile(self, user_id: str) -> Dict[str, Any]:
        db = next(self.get_db())
        try:
            user = db.query(DBUser).filter(DBUser.id == user_id).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )
            
            now = datetime.utcnow()
            current_status = user.status if user.status_expires_at and user.status_expires_at > now else ""
            
            return {
                "id": user.id,
                "nickname": user.nickname,
                "email": user.email,
                "avatar": user.avatar,
                "bio": user.bio,
                "status": current_status,
                "status_expires_at": user.status_expires_at.isoformat() if user.status_expires_at else None,
                "registered_at": user.registered_at.isoformat() if user.registered_at else None,
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取用户信息失败: {str(e)}"
            )
        finally:
            db.close()