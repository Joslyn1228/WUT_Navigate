# 武理导航系统 - 数据库设计与可视化图表

---

## 一、数据库设计

### 1.1 索引优化

**索引设计**:
| 表名 | 字段 | 索引类型 | 说明 |
|------|------|----------|------|
| users | email | UNIQUE | 加速登录查询 |
| users | username | UNIQUE | 加速用户名查询 |
| workouts | user_id | INDEX | 加速用户运动记录查询 |
| workouts | start_time | INDEX | 加速时间范围查询 |
| posts | user_id | INDEX | 加速用户帖子查询 |
| posts | created_at | INDEX | 加速按时间排序 |
| checkins | user_id | INDEX | 加速用户打卡查询 |
| checkins | place_id | INDEX | 加速地点打卡统计 |
| places | category | INDEX | 加速分类查询 |
| places | is_checkpoint | INDEX | 加速打卡点筛选 |

**索引创建SQL**:
```sql
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE UNIQUE INDEX idx_users_username ON users(username);

CREATE INDEX idx_workouts_user_id ON workouts(user_id);
CREATE INDEX idx_workouts_start_time ON workouts(start_time);

CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_created_at ON posts(created_at);

CREATE INDEX idx_checkins_user_id ON checkins(user_id);
CREATE INDEX idx_checkins_place_id ON checkins(place_id);

CREATE INDEX idx_places_category ON places(category);
CREATE INDEX idx_places_is_checkpoint ON places(is_checkpoint);
```

### 1.2 数据迁移策略

**迁移步骤**:
1. 备份数据：迁移前执行完整数据库备份
2. 创建新表：创建新结构的表
3. 数据迁移：编写迁移脚本迁移数据
4. 验证数据：验证迁移后数据完整性
5. 切换服务：停服切换到新表
6. 监控运行：上线后监控运行状态

**迁移工具**:
- 使用 alembic 进行数据库迁移管理
- 编写版本化迁移脚本
- 支持回滚操作

### 1.3 数据库备份与恢复

**备份策略**:
| 类型 | 频率 | 保留期 | 存储位置 |
|------|------|--------|----------|
| 每日全量备份 | 每天凌晨2点 | 7天 | 本地 + 云端 |
| 每周增量备份 | 每周日 | 30天 | 云端 |
| 手动备份 | 按需 | 永久 | 本地 |

**备份命令**:
```bash
sqlite3 wut_auth.db ".backup backup/wut_auth_$(date +%Y%m%d).db"
```

**恢复命令**:
```bash
sqlite3 wut_auth.db ".restore backup/wut_auth_20260622.db"
```

---

## 二、可视化架构图

### 2.1 数据流图

```mermaid
flowchart TD
    subgraph 用户层
        A[Web端]
        B[移动端]
        C[小程序]
    end
    
    subgraph 服务层
        D[API网关]
        E[认证服务]
        F[导航服务]
        G[AI服务]
        H[社区服务]
        I[运动服务]
        J[打卡服务]
    end
    
    subgraph 数据层
        K[SQLite数据库]
        L[Redis缓存]
        M[高德地图API]
        N[DeepSeek API]
    end
    
    A --> D
    B --> D
    C --> D
    
    D --> E
    D --> F
    D --> G
    D --> H
    D --> I
    D --> J
    
    E --> K
    F --> K
    F --> M
    G --> N
    H --> K
    I --> K
    J --> K
    
    F --> L
    H --> L
```

### 2.2 用户认证状态图

```mermaid
stateDiagram-v2
    [*] --> 未登录
    未登录 --> 已登录: 登录成功
    已登录 --> 未登录: 退出登录
    已登录 --> 已登录: 访问资源
    已登录 --> 会话过期: Token过期
    会话过期 --> 未登录: 返回登录页
```

### 2.3 运动记录状态图

```mermaid
stateDiagram-v2
    [*] --> 准备开始
    准备开始 --> 运动中: 点击开始运动
    运动中 --> 运动中: 更新位置
    运动中 --> 已结束: 点击结束运动
    已结束 --> 准备开始: 返回首页
```

### 2.4 打卡流程状态图

```mermaid
stateDiagram-v2
    [*] --> 检测位置
    检测位置 --> 在范围内: 位置有效
    检测位置 --> 不在范围内: 位置无效
    不在范围内 --> 检测位置: 重新检测
    在范围内 --> 验证打卡点: 查询数据库
    验证打卡点 --> 打卡成功: 找到有效打卡点
    验证打卡点 --> 打卡失败: 未找到打卡点
    打卡成功 --> 检查成就: 更新用户成就
    检查成就 --> [*]: 完成
    打卡失败 --> [*]: 完成
```

### 2.5 完整系统架构图

```mermaid
flowchart LR
    subgraph 客户端层
        A[Web端\nVue.js 3]
        B[移动端\nH5]
        C[微信小程序]
    end
    
    subgraph API网关层
        D[Nginx]
        E[JWT认证]
    end
    
    subgraph 业务服务层
        F[认证服务]
        G[导航服务]
        H[AI服务]
        I[社区服务]
        J[运动服务]
        K[打卡服务]
        L[讲解服务]
    end
    
    subgraph 数据层
        M[SQLite数据库]
        N[Redis缓存]
    end
    
    subgraph 外部服务
        O[高德地图API]
        P[DeepSeek API]
        Q[Dify平台]
    end
    
    A --> D
    B --> D
    C --> D
    
    D --> E
    E --> F
    E --> G
    E --> H
    E --> I
    E --> J
    E --> K
    E --> L
    
    F --> M
    G --> M
    G --> O
    H --> P
    H --> Q
    I --> M
    J --> M
    K --> M
    L --> M
    
    G --> N
    I --> N
```

---

**文档版本**: v1.0  
**创建日期**: 2026年6月22日  
**适用项目**: 武汉理工大学智能导航系统