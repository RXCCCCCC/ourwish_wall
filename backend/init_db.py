"""
数据库初始化脚本
用于创建数据库表和插入测试数据
"""
import sys
import pymysql
from datetime import datetime, timedelta
from app import create_app
from models import db
from config import Config


def init_database():
    """初始化数据库"""
    # Ensure the target database exists (create if missing)
    db_name = Config.DB_NAME
    db_host = Config.DB_HOST
    db_port = Config.DB_PORT
    db_user = Config.DB_USER
    db_password = Config.DB_PASSWORD

    print(f'Checking database `{db_name}` on {db_host}:{db_port}...')
    try:
        conn = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password, charset='utf8mb4')
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            conn.commit()
        conn.close()
        print(f'✓ Database `{db_name}` exists (or was created)')
    except Exception as e:
        print('无法创建或访问数据库，请检查配置和权限:', e)
        raise

    app = create_app('development')
    with app.app_context():
        print('正在创建数据库表...')
        # db.drop_all()  # 如需重建表，手动取消注释并谨慎使用
        db.create_all()
        print('✓ 数据库表创建成功')
        print('生产环境已就绪，数据库表结构初始化完成')


if __name__ == '__main__':
    try:
        init_database()
        print('\n🎉 数据库初始化完成!')
        print('现在可以启动应用了: python app.py')
    except Exception as e:
        print(f'\n❌ 初始化失败: {e}')
        sys.exit(1)
