# 生产环境部署指南

## 部署前准备

### 1. 清理开发数据
✅ 已完成：所有演示数据已从代码中移除

### 2. 环境变量配置

在生产服务器上创建 `.env` 文件或设置以下环境变量：

```bash
# 数据库配置（生产环境必须修改）
DATABASE_URL=mysql+pymysql://your_user:your_password@your_host:3306/ourwish_wall?charset=utf8mb4

# 或分别配置
DB_USER=your_production_user
DB_PASSWORD=your_strong_password
DB_HOST=your_database_host
DB_PORT=3306
DB_NAME=ourwish_wall

# Flask 配置
FLASK_ENV=production
SECRET_KEY=your_very_secure_random_secret_key_here

# AI 服务配置（可选）
AI_SERVICE_ENABLED=true
AI_MODEL=your_ai_model
AI_API_KEY=your_api_key
AI_API_BASE=https://your-api-endpoint.com
```

### 3. 数据库初始化

**重要**：生产环境数据库必须使用 `utf8mb4` 字符集

```bash
# 在 MySQL 中创建数据库
CREATE DATABASE ourwish_wall CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 创建用户并授权（可选）
CREATE USER 'wish_user'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON ourwish_wall.* TO 'wish_user'@'%';
FLUSH PRIVILEGES;
```

## 后端部署

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 初始化数据库表

```bash
python init_db.py
```

输出应为：
```
正在创建数据库表...
✓ 数据库表创建成功
生产环境已就绪，数据库表结构初始化完成

🎉 数据库初始化完成!
```

### 3. 生产环境运行

**不要使用** `python app.py` 在生产环境运行！

推荐使用 Gunicorn：

```bash
pip install gunicorn

# 启动服务（4个工作进程）
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

使用 systemd 管理（推荐）：

创建 `/etc/systemd/system/ourwish-backend.service`：

```ini
[Unit]
Description=OurWish Wall Backend
After=network.target mysql.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/ourwish_wall/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable ourwish-backend
sudo systemctl start ourwish-backend
```

## 前端部署

### 1. 配置 API 地址

修改 `frontend/.env.production`（如不存在则创建）：

```bash
VITE_API_BASE_URL=https://your-api-domain.com
```

### 2. 构建生产版本

```bash
cd frontend
npm install
npm run build
```

构建产物在 `frontend/dist/` 目录

### 3. 部署静态文件

#### 使用 Nginx（推荐）

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /path/to/ourwish_wall/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # 反向代理后端 API
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用 HTTPS（强烈推荐）：
```bash
sudo certbot --nginx -d your-domain.com
```

## 安全检查清单

- [ ] 数据库使用强密码
- [ ] `SECRET_KEY` 设置为随机值（可用 `python -c "import secrets; print(secrets.token_hex(32))"` 生成）
- [ ] 关闭 Flask 的 `DEBUG` 模式（`FLASK_ENV=production`）
- [ ] 配置防火墙，只开放必要端口（80, 443）
- [ ] 数据库不直接暴露到公网
- [ ] 定期备份数据库
- [ ] 设置速率限制（后端已有基础实现）
- [ ] 配置 CORS（如前后端不同域）
- [ ] 启用 HTTPS

## 监控与维护

### 日志查看

后端日志：
```bash
sudo journalctl -u ourwish-backend -f
```

Nginx 日志：
```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 数据库备份

```bash
# 每日自动备份（添加到 crontab）
0 2 * * * mysqldump -u wish_user -p'password' ourwish_wall > /backup/ourwish_$(date +\%Y\%m\%d).sql
```

### 更新部署

后端更新：
```bash
cd backend
git pull
pip install -r requirements.txt
sudo systemctl restart ourwish-backend
```

前端更新：
```bash
cd frontend
git pull
npm install
npm run build
# Nginx 会自动使用新的 dist 目录
```

## 性能优化建议

1. **数据库索引**：已在 models 中定义，确保迁移时应用
2. **静态资源 CDN**：前端 dist 可部署到 CDN
3. **数据库连接池**：SQLAlchemy 默认启用
4. **Nginx 缓存**：配置静态资源缓存头
5. **启用 gzip**：Nginx 中启用 gzip 压缩

## 故障排查

### 前端无法连接后端
- 检查 Nginx 代理配置
- 确认后端服务运行中：`sudo systemctl status ourwish-backend`
- 查看后端日志

### 数据库连接失败
- 检查环境变量配置
- 确认数据库服务运行：`sudo systemctl status mysql`
- 验证数据库用户权限

### AI 回复不工作
- 检查 `AI_SERVICE_ENABLED` 是否为 true
- 验证 API key 和 endpoint 配置
- 查看后端日志中的 AI 服务错误

## 技术支持

如遇到问题，请查看：
- 后端日志：`journalctl -u ourwish-backend`
- Nginx 错误日志：`/var/log/nginx/error.log`
- 数据库日志：`/var/log/mysql/error.log`
