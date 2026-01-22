"""
配置文件 - 数据库连接和应用配置
⚠️ 请根据实际环境修改以下配置
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env when present
load_dotenv()

class Config:
    """应用配置类"""
    
    # Flask 密钥 - 用于 session 加密
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-please-change-in-production'
    
    # ⚠️ 数据库配置 - 优先使用完整的 `DATABASE_URL` 环境变量
    # 格式: mysql+pymysql://用户名:密码@主机:端口/数据库名
    DATABASE_URL = os.environ.get('DATABASE_URL')

    # 或者分别配置各个参数 (来自 .env 或环境变量)
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')  # 从环境中读取, 推荐使用 .env
    DB_NAME = os.environ.get('DB_NAME', 'ourwish_wall')

    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # SQLAlchemy 配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # 设置为 True 可以看到 SQL 语句
    
    # CORS 配置 - 允许的前端域名
    # ⚠️ 生产环境请修改为实际的前端域名
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # 防刷限流配置
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_PERIOD = 60  # 秒
    RATE_LIMIT_MAX_REQUESTS = 1  # 在周期内最多允许的请求数
    
    # 分页配置
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 50
    
    # ⚠️ AI 服务配置 (可选 - 如果接入真实 LLM API)
    AI_SERVICE_ENABLED = os.environ.get('AI_SERVICE_ENABLED', 'false').lower() == 'true'
    AI_API_KEY = os.environ.get('AI_API_KEY', '')  # ⚠️ 如果使用通义千问/文心一言,请填写 API Key
    AI_API_ENDPOINT = os.environ.get('AI_API_ENDPOINT', '')  # API 端点
    
    # 内容审核
    SENSITIVE_WORDS_ENABLED = True
    MAX_CONTENT_LENGTH = 500  # 心愿内容最大字数


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    # ⚠️ 生产环境务必设置强密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'CHANGE_THIS_TO_A_RANDOM_SECRET_KEY'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
