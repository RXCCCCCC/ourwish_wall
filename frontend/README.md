# 德兴“红脉新声”心愿云墙 - 前端项目

这是基于 Vue 3 + Tailwind CSS + Vant 4 构建的心愿墙 H5 前端项目。

## 🛠️ 技术栈
- **核心框架**: Vue 3
- **构建工具**: Vite
- **UI 样式**: Tailwind CSS (布局/原子类) + Vant 4 (移动端组件库)
- **状态管理**: Pinia
- **图表可视化**: ECharts + echarts-wordcloud
- **网络请求**: Axios

## 🚀 快速开始

### 1. 安装依赖
```bash
npm install
```

### 2. 本地开发运行
```bash
npm run dev
```
启动后访问控制台输出的地址（通常是 http://localhost:5173/）。
本地开发时，API 请求会被代理到 `http://127.0.0.1:5000` (Flask 后端默认端口)。

### 3. 构建生产环境代码
```bash
npm run build
```
构建完成后，生成的静态文件位于 `dist/` 目录。

## 📂 部署指南 (配合 Nginx)

将 `dist/` 目录下的所有文件上传至服务器目录（例如 `/var/www/wishwall/dist`）。

Nginx 配置示例：
```nginx
server {
    listen 80;
    server_name your_ip_or_domain;

    # 前端静态文件
    location / {
        root /var/www/wishwall/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 转发
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📝 二次开发说明

1. **对接真实后端**:
   - 打开 `src/components/WishForm.vue`。
   - 找到 `onSubmit` 方法中的 `// Mock API call` 部分。
   - 取消 Axios 调用的注释，确保后端 API 路径为 `/api/wishes`。

2. **修改图表数据**:
   - 打开 `src/components/charts/ChartsBoard.vue`。
   - `initPieChart` 和 `initWordCloud` 中的 `data` 数组目前是硬编码的，后续可通过 API 获取。
