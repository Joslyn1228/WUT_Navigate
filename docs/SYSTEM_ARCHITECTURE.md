# 武汉理工大学智能导航系统 - 完整系统架构设计

## 目录
1. [系统概述
2. [技术架构
3. [核心模块设计
4. [数据库设计
5. [API接口设计
6. [部署方案
7. [测试方案

---

## 1. 系统概述

### 1.1 项目简介
武汉理工大学智能导航系统是一个功能完整的校园导航与社交平台，提供高精度定位、智能导航、景点讲解、运动健康、校园社交等功能。

### 1.2 核心功能
- 🗺️ **定位与导航**：高精度校内定位，步行/骑行/通勤车导航
- 🤖 **智能聊天**：自然语言交互，语音输入输出
- 📖 **景点讲解**：电子围栏触发，多种讲解形式
- 🏃 **运动健康**：路线跟踪，卡路里计算，成就系统
- 📱 **校内社区**：社交分享，点赞评论
- 📸 **游览打卡**：打卡成就，海报分享

### 1.3 系统目标
- 定位精度5米以内
- 支持多种导航模式
- 语音交互支持
- 实时位置监测
- 完整的用户体系

---

## 2. 技术架构

### 2.1 技术栈

#### 后端技术栈
```
- **框架：FastAPI
- **数据库**：
  - PostgreSQL（关系型数据库）：用户、景点、打卡数据
  - Redis（缓存）：热点数据缓存
- **地图服务**：高德地图API
- **AI服务**：DeepSeek API
- **认证**：JWT
- **部署**：Docker + Nginx

#### 前端技术栈
- **Web端**：HTML5 + Vue.js 3
- **移动端**：React Native / Flutter（可选）
- **地图组件**：高德地图JavaScript API
- **语音服务**：Web Speech API

### 2.2 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                           客户端层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Web端     │  │  Android端     │  │  iOS端     │        │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
└─────────┼──────────────────┼──────────────────┼──────────────────┘
          │                  │                  │
┌─────────┴──────────────────┴──────────────────┴──────────────────┐
│                        API网关层                        │
│                    Nginx + JWT认证                      │
└─────────────────────────────┬───────────────────────────────┘
                              │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼───────┐    ┌──────────────┐    ┌──────────────┐
│  定位服务    │    │  AI服务   │    │  社区服务   │
│  (高德地图    │    │  (DeepSeek) │    │  (PostgreSQL│
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                       │                       │
┌───────▼───────┐    ┌───────▼───────┐    ┌───────▼───────┐
│  运动健康    │    │  景点讲解    │    │  游览打卡    │
│  模块        │    │  模块        │    │  模块        │
└───────────────┘    └───────────────┘    └───────────────┘
        │                       │                       │
└───────────────────────────────┼───────────────────────────────┘
                        ┌───────▼───────┐
                        │  Redis缓存    │
                        └───────────────┘
```

---

## 3. 核心模块设计

### 3.1 定位与导航模块

#### 功能需求
- 高精度校内定位（误差5米以内）
- 校内POI数据管理
- 多种导航模式：步行、骑行、通勤车
- 实时导航指引

#### 核心功能设计

```python
# app/navigation_service.py
class NavigationService:
    """导航服务"""
    
    def __init__(self):
        self.location_service = LocationService()
        self.place_database = PlaceDatabase()
    
    async def get_route(
        self, 
        start: Location, 
        destination: Location, 
        mode: str = "walking"
    ) -> Route:
        """获取导航路线"""
        pass
    
    async def search_destination(self, query: str) -> Optional[Location]:
        """搜索目的地"""
        pass
    
    async def get_navigation_steps(self, route_id: str) -> List[NavigationStep]:
        """获取导航步骤"""
        pass
```

### 3.2 智能聊天模块

#### 功能需求
- 自然语言问答
- 语音输入输出
- 上下文理解
- 校内知识库
- 友好聊天界面

#### 核心功能
```python
# app/chat_service.py
class ChatService:
    """聊天服务"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.knowledge_base = KnowledgeBase()
    
    async def chat(
        self, 
        user_id: str, 
        query: str, 
        context: Optional[List[Message]]
    ) -> ChatResponse:
        """聊天"""
        pass
    
    async def text_to_speech(self, text: str) -> bytes:
        """文本转语音"""
        pass
    
    async def speech_to_text(self, audio: bytes) -> str:
        """语音转文本"""
        pass
```

### 3.3 地点讲解模块

#### 功能需求
- 电子围栏（可配置
- 实时位置监测
- 多种讲解形式
- 收藏分享功能

#### 核心功能
```python
# app/guide_service.py
class GuideService:
    """讲解服务"""
    
    def __init__(self):
        self.electronic_fences = {}
        self.favorites_db = FavoritesDatabase()
    
    async def check_proximity(
        self, 
        user_id: str, 
        location: Location
    ) -> Optional[Place]:
        """检查接近"""
        pass
    
    async def get_place_guide(
        self, 
        place_id: str
    ) -> GuideContent:
        """获取讲解内容"""
        pass
    
    async def favorite_place(
        self, 
        user_id: str, 
        place_id: str
    ) -> bool:
        """收藏景点"""
        pass
    
    async def share_guide(
        self, 
        user_id: str, 
        place_id: str, 
        platform: str
    ) -> str:
        """分享讲解"""
        pass
```

### 3.4 运动与健康模块

#### 功能需求
- 运动路线跟踪
- 卡路里计算
- 运动数据统计
- 运动成就系统

#### 核心功能
```python
# app/fitness_service.py
class FitnessService:
    """运动健康服务"""
    
    def __init__(self):
        self.workout_db = WorkoutDatabase()
        self.achievement_system = AchievementSystem()
    
    async def start_workout(
        self, 
        user_id: str, 
        workout_type: str
    ) -> str:
        """开始运动"""
        pass
    
    async def update_workout(
        self, 
        workout_id: str, 
        location: Location
    ) -> WorkoutUpdate:
        """更新运动"""
        pass
    
    async def end_workout(
        self, 
        workout_id: str
    ) -> WorkoutSummary:
        """结束运动"""
        pass
    
    async def get_fitness_stats(
        self, 
        user_id: str, 
        period: str
    ) -> FitnessStats:
        """获取运动统计"""
        pass
```

### 3.5 校内社区模块

#### 功能需求
- 社交分享（文字、图片、定位
- 点赞评论功能

#### 核心功能
```python
# app/community_service.py
class CommunityService:
    """社区服务"""
    
    def __init__(self):
        self.post_db = PostDatabase()
        self.comment_db = CommentDatabase()
    
    async def create_post(
        self, 
        user_id: str, 
        content: str, 
        images: Optional[List[str]],
        location: Optional[Location]
    ) -> Post:
        """发布帖子"""
        pass
    
    async def like_post(
        self, 
        user_id: str, 
        post_id: str
    ) -> bool:
        """点赞"""
        pass
    
    async def comment_post(
        self, 
        user_id: str, 
        post_id: str, 
        comment: str
    ) -> Comment:
        """评论"""
        pass
    
    async def get_feed(
        self, 
        user_id: str, 
        page: int
    ) -> List[Post]:
        """获取动态"""
        pass
```

### 3.6 游览打卡模块

#### 功能需求
- 打卡点设置
- 位置打卡
- 成就系统
- 打卡历史
- 海报分享

#### 核心功能
```python
# app/checkin_service.py
class CheckinService:
    """打卡服务"""
    
    def __init__(self):
        self.checkpoint_db = CheckpointDatabase()
        self.achievement_system = AchievementSystem()
    
    async def checkin(
        self, 
        user_id: str, 
        location: Location
    ) -> CheckinResult:
        """打卡"""
        pass
    
    async def get_achievement(
        self, 
        user_id: str
    ) -> List[Achievement]:
        """获取成就"""
        pass
    
    async def get_checkin_history(
        self, 
        user_id: str
    ) -> List[CheckinRecord]:
        """获取打卡历史"""
        pass
    
    async def generate_poster(
        self, 
        user_id: str, 
        checkin_id: str
    ) -> bytes:
        """生成打卡海报"""
        pass
```

---

## 4. 数据库设计

### 4.1 数据库架构

#### 用户表 (users)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(50),
    avatar_url VARCHAR(255),
    height DECIMAL(5,2),
    weight DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 景点表 (places)
```sql
CREATE TABLE places (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    description TEXT,
    latitude DECIMAL(10,6) NOT NULL,
    longitude DECIMAL(10,6) NOT NULL,
    geofence_radius INTEGER DEFAULT 20,
    voice_url VARCHAR(255),
    video_url VARCHAR(255),
    images JSONB,
    is_checkpoint BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 运动记录表 (workouts)
```sql
CREATE TABLE workouts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    workout_type VARCHAR(20),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    total_distance DECIMAL(10,2),
    total_duration INTEGER,
    calories_burned DECIMAL(10,2),
    route_points JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 社区帖子表 (posts)
```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    content TEXT NOT NULL,
    images JSONB,
    location_latitude DECIMAL(10,6),
    location_longitude DECIMAL(10,6),
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 打卡记录表 (checkins)
```sql
CREATE TABLE checkins (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    place_id INTEGER REFERENCES places(id),
    checkin_time TIMESTAMP DEFAULT NOW(),
    location_latitude DECIMAL(10,6),
    location_longitude DECIMAL(10,6),
    is_valid BOOLEAN DEFAULT TRUE
);
```

#### 成就表 (achievements)
```sql
CREATE TABLE achievements (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    type VARCHAR(50),
    required_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 用户成就表 (user_achievements)
```sql
CREATE TABLE user_achievements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    achievement_id INTEGER REFERENCES achievements(id),
    earned_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, achievement_id)
);
```

---

## 5. API接口设计

### 5.1 认证接口

#### POST /api/auth/register
注册新用户

#### POST /api/auth/login
用户登录

#### GET /api/auth/profile
获取用户信息

### 5.2 导航接口

#### GET /api/navigation/route
获取导航路线

#### GET /api/navigation/search
搜索目的地

### 5.3 聊天接口

#### POST /api/chat/send
发送聊天消息

#### POST /api/chat/speech
语音聊天

### 5.4 讲解接口

#### GET /api/guide/places
获取景点列表

#### GET /api/guide/places/:id
获取景点详情

#### POST /api/guide/favorites
收藏景点

### 5.5 运动接口

#### POST /api/fitness/start
开始运动

#### POST /api/fitness/update
更新运动

#### POST /api/fitness/end
结束运动

#### GET /api/fitness/stats
获取运动统计

### 5.6 社区接口

#### GET /api/community/feed
获取动态

#### POST /api/community/post
发布帖子

#### POST /api/community/like
点赞

#### POST /api/community/comment
评论

### 5.7 打卡接口

#### POST /api/checkin
打卡

#### GET /api/checkin/history
打卡历史

#### GET /api/checkin/achievements
获取成就

#### GET /api/checkin/poster
生成海报

---

## 6. 部署方案

### 6.1 开发环境
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/wut_nav
      - REDIS_URL=redis://redis:6379/0
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=wut_nav
  redis:
    image: redis:7
  nginx:
    image: nginx:alpine
    ports:
      - "80:80
```

### 6.2 生产环境
- 使用云服务器部署
- HTTPS加密
- 负载均衡
- 数据库备份
- 日志监控

---

## 7. 测试方案

### 7.1 测试类型

#### 单元测试
- 核心模块测试覆盖率 ≥80%
- 使用pytest框架

#### 集成测试
- API接口测试
- 模块间交互测试

#### 性能测试
- 并发用户测试
- 响应时间测试

#### 安全测试
- SQL注入测试
- XSS攻击测试
- 用户数据加密测试

---

## 8. 交付物清单

1. 完整源代码
2. 数据库设计文档
3. API接口文档
4. 用户操作手册
5. 管理员手册
6. 系统部署指南
7. 测试报告
8. 问题清单
