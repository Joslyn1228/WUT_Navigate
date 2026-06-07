# 武汉理工大学智能导航系统 - API文档

## 目录
- [基础信息](#基础信息)
- [认证接口](#认证接口)
- [导航接口](#导航接口)
- [打卡接口](#打卡接口)
- [运动健康接口](#运动健康接口)
- [社区接口](#社区接口)
- [景点讲解接口](#景点讲解接口)

---

## 基础信息

### 基础URL
```
http://localhost:8080
```

### 响应格式
所有接口返回JSON格式：
```json
{
  "success": true,
  "message": "操作成功",
  "data": {}
}
```

---

## 认证接口

### 用户注册
**POST** `/api/auth/register`

请求体：
```json
{
  "username": "string",
  "password": "string",
  "email": "string",
  "nickname": "string (可选)"
}
```

响应：
```json
{
  "success": true,
  "message": "注册成功",
  "data": {
    "user_id": 1,
    "username": "string",
    "nickname": "string"
  }
}
```

### 用户登录
**POST** `/api/auth/login`

请求体：
```json
{
  "username": "string",
  "password": "string"
}
```

响应：
```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "access_token": "string",
    "token_type": "Bearer",
    "expires_in": 86400
  }
}
```

### 获取用户信息
**GET** `/api/auth/profile`

响应：
```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "id": 1,
    "username": "string",
    "nickname": "string",
    "email": "string",
    "avatar_url": "string (可选)",
    "height": 175.5 (可选),
    "weight": 65.0 (可选),
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### 更新用户信息
**PUT** `/api/auth/profile`

请求体：
```json
{
  "nickname": "string (可选)",
  "avatar_url": "string (可选)",
  "height": 175.5 (可选),
  "weight": 65.0 (可选)
}
```

---

## 导航接口

### 获取导航路线
**POST** `/api/navigation/route`

请求体：
```json
{
  "start": {
    "latitude": 30.5075,
    "longitude": 114.3795,
    "address": "南湖校区"
  },
  "destination": {
    "latitude": 30.5067,
    "longitude": 114.3792,
    "address": "南湖图书馆"
  },
  "mode": "walking"
}
```

`mode`可选值：`walking`（步行）、`riding`（骑行）、`shuttle`（校车）

响应：
```json
{
  "success": true,
  "message": "路线规划成功",
  "data": {
    "total_distance": 1500,
    "total_duration": 1200,
    "steps": [
      {
        "instruction": "向前走100米",
        "distance": 100,
        "duration": 90
      }
    ],
    "route_polyline": "string (可选)"
  }
}
```

### 搜索目的地
**GET** `/api/navigation/search`

参数：
- `keyword`: 搜索关键词
- `city`: 城市（默认：武汉市）

响应：
```json
{
  "success": true,
  "message": "搜索成功",
  "data": [
    {
      "id": 1,
      "name": "南湖图书馆",
      "category": "图书馆",
      "latitude": 30.5067,
      "longitude": 114.3792,
      "address": "武汉理工大学南湖校区"
    }
  ]
}
```

---

## 打卡接口

### 景点打卡
**POST** `/api/checkin`

请求体：
```json
{
  "latitude": 30.5067,
  "longitude": 114.3792,
  "place_id": 1,
  "place_name": "南湖图书馆",
  "place_latitude": 30.5067,
  "place_longitude": 114.3792,
  "geofence_radius": 20
}
```

响应：
```json
{
  "success": true,
  "message": "成功在南湖图书馆打卡！",
  "data": {
    "place_name": "南湖图书馆",
    "new_achievements": [
      {
        "id": 1,
        "name": "首次打卡",
        "description": "完成第一次打卡",
        "icon": "🎯",
        "type": "checkin",
        "required_count": 1
      }
    ]
  }
}
```

### 获取打卡历史
**GET** `/api/checkin/history`

参数：
- `limit`: 限制数量（默认：50）

响应：
```json
{
  "success": true,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "place_id": 1,
      "place_name": "南湖图书馆",
      "checkin_time": "2024-01-01T12:00:00Z",
      "latitude": 30.5067,
      "longitude": 114.3792
    }
  ]
}
```

### 获取成就列表
**GET** `/api/checkin/achievements`

响应：
```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "earned": [
      {
        "achievement": {
          "id": 1,
          "name": "首次打卡",
          "description": "完成第一次打卡",
          "icon": "🎯",
          "type": "checkin"
        },
        "earned_at": "2024-01-01T12:00:00Z",
        "is_new": false
      }
    ],
    "not_earned": [
      {
        "id": 2,
        "name": "打卡达人",
        "description": "累计打卡10次",
        "icon": "🏆",
        "type": "checkin"
      }
    ]
  }
}
```

### 获取打卡统计
**GET** `/api/checkin/statistics`

响应：
```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "total_checkins": 15,
    "consecutive_days": 5,
    "unique_places": 8,
    "place_stats": {
      "南湖图书馆": 3,
      "南湖体育馆": 2
    },
    "earned_achievements": 2
  }
}
```

---

## 运动健康接口

### 开始运动
**POST** `/api/fitness/start`

请求体：
```json
{
  "workout_type": "walking",
  "start_latitude": 30.5075,
  "start_longitude": 114.3795
}
```

`workout_type`可选值：`walking`、`running`、`cycling`

响应：
```json
{
  "success": true,
  "message": "运动已开始",
  "data": {
    "workout_id": 1
  }
}
```

### 更新运动位置
**POST** `/api/fitness/update`

请求体：
```json
{
  "workout_id": 1,
  "latitude": 30.5080,
  "longitude": 114.3800
}
```

响应：
```json
{
  "success": true,
  "message": "更新成功",
  "data": {
    "workout_id": 1,
    "current_distance": 200,
    "current_duration": 180,
    "location": {
      "latitude": 30.5080,
      "longitude": 114.3800
    }
  }
}
```

### 结束运动
**POST** `/api/fitness/end`

请求体：
```json
{
  "workout_id": 1
}
```

响应：
```json
{
  "success": true,
  "message": "运动已结束",
  "data": {
    "id": 1,
    "total_distance": 1500,
    "total_duration": 1200,
    "calories_burned": 120.5,
    "avg_speed": 4.5
  }
}
```

### 获取运动统计
**GET** `/api/fitness/statistics`

参数：
- `period`: 统计周期（`day`、`week`、`month`）

响应：
```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "period": "week",
    "total_distance": 15000,
    "total_duration": 7200,
    "total_calories": 1200.5,
    "workout_count": 5,
    "avg_distance": 3000,
    "avg_duration": 1440
  }
}
```

### 获取运动历史
**GET** `/api/fitness/history`

参数：
- `limit`: 限制数量（默认：20）

响应：
```json
{
  "success": true,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "workout_type": "walking",
      "start_time": "2024-01-01T12:00:00Z",
      "end_time": "2024-01-01T12:30:00Z",
      "total_distance": 1500,
      "total_duration": 1800,
      "calories_burned": 120.5
    }
  ]
}
```

---

## 社区接口

### 获取动态列表
**GET** `/api/community/feed`

参数：
- `page`: 页码（默认：1）
- `page_size`: 每页数量（默认：20）

响应：
```json
{
  "success": true,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "user_id": 1,
      "user_nickname": "用户1",
      "user_avatar": "string (可选)",
      "content": "今天在南湖图书馆打卡了！",
      "images": ["image_url_1", "image_url_2"],
      "location_latitude": 30.5067,
      "location_longitude": 114.3792,
      "likes_count": 10,
      "comments_count": 3,
      "is_liked": false,
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

### 发布动态
**POST** `/api/community/post`

请求体：
```json
{
  "content": "今天在南湖图书馆打卡了！",
  "images": ["image_url_1", "image_url_2"],
  "latitude": 30.5067,
  "longitude": 114.3792
}
```

响应：
```json
{
  "success": true,
  "message": "发布成功",
  "data": {
    "id": 1,
    "content": "今天在南湖图书馆打卡了！",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

### 点赞/取消点赞
**POST** `/api/community/like`

请求体：
```json
{
  "post_id": 1
}
```

响应：
```json
{
  "success": true,
  "message": "操作成功"
}
```

### 评论动态
**POST** `/api/community/comment`

请求体：
```json
{
  "post_id": 1,
  "content": "太棒了！"
}
```

响应：
```json
{
  "success": true,
  "message": "评论成功",
  "data": {
    "id": 1,
    "content": "太棒了！",
    "user_nickname": "用户1",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

### 获取用户动态
**GET** `/api/community/user-posts`

参数：
- `page`: 页码（默认：1）
- `page_size`: 每页数量（默认：20）

响应同获取动态列表。

### 搜索动态
**GET** `/api/community/search`

参数：
- `keyword`: 搜索关键词
- `page`: 页码（默认：1）
- `page_size`: 每页数量（默认：20）

响应同获取动态列表。

---

## 景点讲解接口

### 获取景点列表
**GET** `/api/guide/places`

参数：
- `category`: 分类（可选）
- `keyword`: 关键词（可选）

响应：
```json
{
  "success": true,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "name": "南湖图书馆",
      "category": "图书馆",
      "description": "武汉理工大学南湖校区图书馆...",
      "latitude": 30.5067,
      "longitude": 114.3792,
      "geofence_radius": 20,
      "is_checkpoint": true
    }
  ]
}
```

### 获取景点详情
**GET** `/api/guide/places/{place_id}`

响应：
```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "id": 1,
    "name": "南湖图书馆",
    "category": "图书馆",
    "text": "武汉理工大学南湖校区图书馆是...",
    "voice_url": "string (可选)",
    "video_url": "string (可选)",
    "images": ["image_url_1", "image_url_2"],
    "is_favorited": false
  }
}
```

### 检查接近景点（自动讲解）
**GET** `/api/guide/check-proximity`

参数：
- `latitude`: 用户纬度
- `longitude`: 用户经度

响应（接近景点时）：
```json
{
  "success": true,
  "message": "您已到达南湖图书馆附近！",
  "data": {
    "place": {
      "id": 1,
      "name": "南湖图书馆",
      "category": "图书馆",
      "description": "武汉理工大学南湖校区图书馆...",
      "latitude": 30.5067,
      "longitude": 114.3792
    },
    "is_nearby": true
  }
}
```

### 收藏景点
**POST** `/api/guide/favorite`

请求体：
```json
{
  "place_id": 1
}
```

响应：
```json
{
  "success": true,
  "message": "收藏成功"
}
```

### 取消收藏景点
**DELETE** `/api/guide/favorite/{place_id}`

响应：
```json
{
  "success": true,
  "message": "取消收藏成功"
}
```

### 获取收藏列表
**GET** `/api/guide/favorites`

响应：
```json
{
  "success": true,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "name": "南湖图书馆",
      "category": "图书馆",
      "description": "武汉理工大学南湖校区图书馆...",
      "latitude": 30.5067,
      "longitude": 114.3792
    }
  ]
}
```

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未认证或认证已过期 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 注意事项

1. 所有需要认证的接口需要在请求头中添加：`Authorization: Bearer {access_token}`
2. 坐标使用WGS84格式（即高德地图GCJ-02）
3. 时间格式统一使用ISO 8601标准
4. 图片上传需要使用Multipart/form-data格式
