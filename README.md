# 武汉理工大学智能导游系统

🎓 基于 FastAPI + LangChain 的校园智能导游系统

## 🚀 功能特性

### 1. 智能导航
- 📍 实时位置获取
- 🗺️ 校园路径规划导航
- 🏛️ 精准定位武汉理工大学各校区

### 2. 实时讲解
- 🎯 50米内场所自动检测
- 📖 文字介绍 + 语音播放
- 🏛️ 图书馆、学院楼、食堂等设施介绍

### 3. 打卡系统
- ⏰ 基于时间段的活动打卡
- 🏆 Steam风格成就系统
- 🔥 连续打卡天数追踪

### 4. 社区功能
- 📝 动态发布（文字+图片+位置）
- ❤️ 点赞、评论、收藏
- 📍 自动识别校区

### 5. 用户系统
- 👤 个人主页
- 🖼️ 头像上传
- ✨ 个性签名和状态（emoji）

## 🛠️ 技术栈

- **后端**: FastAPI, SQLAlchemy, LangChain
- **前端**: HTML5, CSS3, JavaScript
- **地图**: 高德地图 JavaScript API + Web API
- **数据库**: SQLite
- **AI**: DeepSeek 大模型

## 📦 安装

1. 克隆项目
```bash
git clone https://github.com/Joslyn1228/WUT_Navigate.git
cd WUT_Navigate
```

2. 创建虚拟环境
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
创建 `.env` 文件：
```env
DEEPSEEK_API_KEY=your_api_key
AMAP_WEB_SERVICE_KEY=your_amap_key
AMAP_JS_API_KEY=your_amap_js_key
```

5. 启动服务器
```bash
uvicorn main:app --reload
```

6. 访问
- 前端: http://localhost:8000
- API文档: http://localhost:8000/docs

## 📁 项目结构

```
WUT_Navigate/
├── app/
│   ├── auth_service.py        # 用户认证服务
│   ├── checkin_service.py     # 打卡服务
│   ├── community_service.py   # 社区服务
│   └── extended_schemas.py    # 数据模型
├── static/
│   └── index.html             # 前端页面
├── main.py                     # 应用入口
├── requirements.txt            # 依赖列表
└── .env                       # 环境变量
```

## 🎯 成就系统

| 成就 | 名称 | 描述 |
|------|------|------|
| 🎯 | 初来乍到 | 完成第一次打卡 |
| 🏃 | 运动达人 | 累计打卡10次 |
| 🔥 | 连续打卡王 | 连续打卡7天 |
| 📚 | 图书馆常客 | 打卡图书馆5次 |

## 📝 API接口

### 认证相关
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/profile` - 获取用户信息
- `PUT /api/auth/profile` - 更新用户信息

### 打卡相关
- `POST /api/checkin` - 打卡
- `GET /api/checkin/statistics` - 获取打卡统计
- `GET /api/checkin/history` - 获取打卡历史

### 社区相关
- `POST /api/community/post` - 发布动态
- `GET /api/community/feed` - 获取动态列表
- `POST /api/community/like` - 点赞
- `POST /api/community/comment` - 评论
- `POST /api/community/upload-images` - 上传图片

## 📄 许可证

MIT License

## 👤 作者

Joslyn

## 🙏 致谢

- 武汉理工大学
- DeepSeek AI
- 高德地图
