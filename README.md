# ourwish_wall

小型心愿墙（前后端分离）的演示项目，包含基于 Flask 的后端和基于 Vue 3 + Vite 的移动优先前端。

## 技术栈
- 后端: Python, Flask, SQLAlchemy, PyMySQL
- 前端: Vue 3, Vite, Pinia, Tailwind, Vant
- 数据库: MySQL / MariaDB
- 部署: Gunicorn + Nginx 或 Docker

## 仓库结构（核心）
- `backend/`：Flask 应用、模型、初始化脚本（`app.py`, `models.py`, `init_db.py`）
- `frontend/`：Vue 3 前端应用（`src/`、`vite.config.js`）
- `plans/`：项目设计文档与部署/开发笔记

## 快速开始（本地开发）

1. 准备后端（在项目根或 `backend/`）

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# 配置环境变量，例如 DATABASE_URL
python init_db.py
python app.py
```

2. 准备前端（另开终端）

```bash
cd frontend
npm install
npm run dev
```

前端通过 `/api/*` 代理调用后端（参见 `frontend/src/api/index.js`），Vite 开发模式下会走代理配置。

## 构建与部署要点
- 前端：`cd frontend && npm run build`，将 `dist/` 内容放到服务器的静态目录（Nginx）。
- 后端：在服务器上创建虚拟环境并 `pip install -r requirements.txt`，使用 Gunicorn + systemd 启动，Nginx 负责反向代理 `/api` 到后端（或使用 Docker 部署）。
- 数据库：建议使用阿里云 RDS 或在同机安装 MariaDB。初始化数据库请运行 `backend/init_db.py`。

参考详细部署步骤与示例配置请查看仓库内的 `plans/` 和 `backend/` 中的注释。

## Docker（可选）
项目适合容器化：后端生成镜像运行 Gunicorn，前端构建产物挂载到 Nginx。对小内存服务器建议限制容器内存并减少 Gunicorn worker 数量。

## 运行检查项
- 后端: `systemctl status yourservice` 或 `journalctl -u yourservice -f`
- Nginx: `sudo nginx -t && sudo systemctl reload nginx`

## 联系 / 贡献
欢迎通过 Issues 或 Pull Requests 贡献改进。README 中未覆盖的运行细节可直接查看 `backend/config.py`、`backend/app.py` 与 `frontend/src/api/index.js`。

## 许可证
参见仓库根目录的 `LICENSE` 文件。

