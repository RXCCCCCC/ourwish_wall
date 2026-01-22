# 心愿墙后端 API

"数字传承 · 红色德兴"心愿墙项目的 Flask 后端服务。

## 技术栈

- **框架**: Flask 2.3+
- **数据库**: MySQL 8.0
- **ORM**: SQLAlchemy + PyMySQL
- **Python 版本**: 3.10+

## 项目结构

```
backend/
├── app.py              # Flask 主应用和路由
├── models.py           # 数据库模型 (Wish, Comment, Like, RateLimit)
├── config.py           # 配置文件 (⚠️ 需要修改数据库配置)
├── init_db.py          # 数据库初始化脚本
├── requirements.txt    # Python 依赖
├── services/
│   ├── ai_service.py   # AI 回复生成服务
│   └── text_filter.py  # 文本过滤服务
└── README.md          # 本文件
```

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置数据库

⚠️ **重要**: 请修改 `config.py` 中的数据库配置:

```python
# config.py 中需要修改的配置
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = 'your_password'  # ⚠️ 修改为您的 MySQL 密码
DB_NAME = 'ourwish_wall'
```

### 3. 创建数据库

在 MySQL 中创建数据库:

```sql
CREATE DATABASE ourwish_wall CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 初始化数据库

运行初始化脚本创建表结构并插入测试数据:

```bash
python init_db.py
```

### 5. 启动开发服务器

```bash
python app.py
```

服务将运行在 `http://localhost:5000`

## API 接口文档

### 基础信息

- **Base URL**: `http://localhost:5000/api`
- **数据格式**: JSON
- **字符编码**: UTF-8

### 接口列表

#### 1. 健康检查

```
GET /api/health
```

**响应示例**:
```json
{
  "status": "ok",
  "timestamp": "2026-01-22T10:30:00"
}
```

#### 2. 获取心愿列表

```
GET /api/wishes?page=1&per_page=10&category=红色传承
```

**参数**:
- `page`: 页码 (可选, 默认 1)
- `per_page`: 每页数量 (可选, 默认 10, 最大 50)
- `category`: 类别过滤 (可选)

**响应示例**:
```json
{
  "total": 100,
  "page": 1,
  "per_page": 10,
  "wishes": [
    {
      "id": 1,
      "user_uid": "RedGuard_007",
      "nickname": "张建国",
      "avatar": "👴",
      "category": "红色传承",
      "content": "愿德兴的红色故事...",
      "ai_response": "星星之火，可以燎原...",
      "likes": 88,
      "created_at": "2026年01月22日",
      "comments": [...]
    }
  ]
}
```

#### 3. 发布心愿

```
POST /api/wishes
```

**请求体**:
```json
{
  "user_uid": "RedGuard_007",
  "nickname": "红脉卫士",
  "avatar": "https://...",
  "category": "乡村建设",
  "content": "希望家乡的路修得更好..."
}
```

**限制**: 
- 同一 IP 每 60 秒只能发布 1 条心愿
- 内容最多 500 字

**响应**: 返回新创建的心愿对象 (状态码 201)

#### 4. 点赞/取消点赞

```
POST /api/wishes/:id/like
```

**请求体**:
```json
{
  "user_uid": "RedGuard_007",
  "action": "like"  // 或 "unlike"
}
```

**响应**:
```json
{
  "id": 1,
  "likes": 89,
  "action": "like"
}
```

#### 5. 获取评论列表

```
GET /api/wishes/:id/comments
```

**响应**:
```json
{
  "wish_id": 1,
  "comments": [
    {
      "id": 1,
      "user_uid": "Visitor_001",
      "nickname": "游客甲",
      "avatar": "😊",
      "content": "说得太好了！",
      "created_at": "2026年01月22日"
    }
  ]
}
```

#### 6. 添加评论

```
POST /api/wishes/:id/comments
```

**请求体**:
```json
{
  "user_uid": "RedGuard_007",
  "nickname": "张三",
  "avatar": "https://...",
  "content": "很好的想法"
}
```

**限制**: 评论内容最多 200 字

**响应**: 返回新创建的评论对象 (状态码 201)

#### 7. 删除评论

```
DELETE /api/wishes/:wish_id/comments/:comment_id
```

**请求体**:
```json
{
  "user_uid": "RedGuard_007"
}
```

**权限**: 仅评论作者或心愿发布者可删除

**响应**:
```json
{
  "ok": true,
  "message": "评论已删除"
}
```

#### 8. 删除心愿

```
DELETE /api/wishes/:id
```

**请求体**:
```json
{
  "user_uid": "RedGuard_007"
}
```

**权限**: 仅发布者可删除

**响应**:
```json
{
  "ok": true,
  "message": "心愿已删除"
}
```

#### 9. 获取统计数据

```
GET /api/stats
```

**响应**:
```json
{
  "pie_data": [
    {"name": "红色传承", "value": 120},
    {"name": "乡村建设", "value": 80}
  ],
  "word_cloud": [
    {"name": "德兴", "value": 50},
    {"name": "致富", "value": 30}
  ]
}
```

## 生产环境部署

### 1. 环境配置

创建 `.env` 文件:

```bash
FLASK_ENV=production
SECRET_KEY=your_random_secret_key_here
DATABASE_URL=mysql+pymysql://user:password@host:3306/dbname
CORS_ORIGINS=https://your-frontend-domain.com
```

### 2. 使用 Gunicorn 部署

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

参数说明:
- `-w 4`: 4 个工作进程
- `-b 0.0.0.0:5000`: 绑定到所有接口的 5000 端口

### 3. Nginx 反向代理配置示例

```nginx
server {
    listen 80;
    server_name api.yourwishwall.com;

    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 4. Systemd 服务配置

创建 `/etc/systemd/system/wishwall.service`:

```ini
[Unit]
Description=Wish Wall Backend API
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl start wishwall
sudo systemctl enable wishwall
```

## 注意事项

### ⚠️ 必须修改的配置

1. **数据库密码**: `config.py` 中的 `DB_PASSWORD`
2. **密钥**: 生产环境的 `SECRET_KEY` (建议使用随机字符串)
3. **CORS 配置**: `CORS_ORIGINS` 改为实际的前端域名
4. **敏感词库**: `services/text_filter.py` 中的敏感词列表

### 可选配置

1. **AI 服务**: 如需接入通义千问/文心一言, 修改 `config.py` 中的:
   - `AI_SERVICE_ENABLED = True`
   - `AI_API_KEY = 'your_api_key'`
   - `AI_API_ENDPOINT = 'https://...'`
   
   然后取消 `services/ai_service.py` 中 LLM 实现的注释

2. **词云优化**: 当前词云数据是静态的, 可以使用 `jieba` 分词库进行动态生成

## 安全建议

1. ✅ 已实现频率限制 (防刷)
2. ✅ 已实现敏感词过滤
3. ✅ 已实现 CORS 跨域配置
4. ⚠️ 建议在生产环境使用 HTTPS
5. ⚠️ 建议定期备份数据库
6. ⚠️ 建议配置日志收集和监控

## 数据库维护

### 清理过期的频率限制记录

建议定期清理 `rate_limits` 表中的旧数据:

```sql
DELETE FROM rate_limits WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 DAY);
```

可以配置 cron 任务自动执行。

## 故障排查

### 1. 数据库连接失败

检查:
- MySQL 服务是否运行
- `config.py` 中的数据库配置是否正确
- 数据库用户是否有足够的权限

### 2. CORS 错误

检查:
- `config.py` 中的 `CORS_ORIGINS` 配置
- 前端请求的域名是否在允许列表中

### 3. 500 错误

查看日志输出, 检查:
- 数据库连接是否正常
- 是否有 Python 代码错误

## 开发指南

### 添加新的 API 接口

1. 在 `app.py` 的 `register_routes` 函数中添加路由
2. 如需新的数据表, 在 `models.py` 中定义模型
3. 运行 `init_db.py` 更新数据库结构

### 测试 API

推荐使用 Postman 或 curl:

```bash
# 获取心愿列表
curl http://localhost:5000/api/wishes

# 发布心愿
curl -X POST http://localhost:5000/api/wishes \
  -H "Content-Type: application/json" \
  -d '{"user_uid":"test","nickname":"测试","category":"红色传承","content":"测试内容"}'
```

## 许可证

本项目仅用于"数字传承 · 红色德兴"实践活动。

## 联系方式

如有问题, 请联系项目负责人。
