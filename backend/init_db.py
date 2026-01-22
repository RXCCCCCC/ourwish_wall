"""
数据库初始化脚本
用于创建数据库表和插入测试数据
"""
import sys
from datetime import datetime, timedelta
from app import create_app
from models import db, Wish, Comment, Like


def init_database():
    """初始化数据库"""
    app = create_app('development')
    
    with app.app_context():
        print('正在创建数据库表...')
        
        # 删除所有表 (谨慎使用!)
        # db.drop_all()
        
        # 创建所有表
        db.create_all()
        print('✓ 数据库表创建成功')
        
        # 检查是否已有数据
        if Wish.query.first():
            print('数据库已有数据, 跳过测试数据插入')
            return
        
        print('正在插入测试数据...')
        insert_test_data()
        print('✓ 测试数据插入成功')


def insert_test_data():
    """插入测试数据"""
    # 测试心愿数据
    test_wishes = [
        {
            'user_uid': 'RedGuard_001',
            'nickname': '张建国',
            'avatar': '👴',
            'category': '红色传承',
            'content': '愿德兴的红色故事代代相传，让更多年轻人了解这片土地的革命历史。',
            'ai_response': '星星之火，可以燎原。您的心愿是传承的火种。',
            'likes': 88,
            'created_at': datetime.utcnow() - timedelta(days=2)
        },
        {
            'user_uid': 'TechPioneer_007',
            'nickname': '李科技',
            'avatar': '🧑‍💻',
            'category': '产业发展',
            'content': '希望能用VR技术复原方志敏纪念馆，让历史场景活起来，让更多人沉浸式体验红色文化。',
            'ai_response': '科技赋能，产业兴旺，您的想法很有远见。',
            'likes': 56,
            'created_at': datetime.utcnow() - timedelta(days=1)
        },
        {
            'user_uid': 'GreenGuardian_888',
            'nickname': '王环保',
            'avatar': '🌱',
            'category': '生态环保',
            'content': '希望德兴能建设更多的生态公园，让红色旅游与绿色生态完美结合。',
            'ai_response': '绿水青山就是金山银山，您的愿望让人敬佩。',
            'likes': 45,
            'created_at': datetime.utcnow() - timedelta(hours=12)
        },
        {
            'user_uid': 'VillageBuilder_666',
            'nickname': '刘乡建',
            'avatar': '👨‍🌾',
            'category': '乡村建设',
            'content': '期待家乡的道路更宽更平，让红色旅游的游客能更方便地到达各个景点。',
            'ai_response': '乡村振兴，未来可期，您的建议充满智慧。',
            'likes': 72,
            'created_at': datetime.utcnow() - timedelta(hours=6)
        },
        {
            'user_uid': 'CultureKeeper_520',
            'nickname': '陈文化',
            'avatar': '📚',
            'category': '红色传承',
            'content': '建议在学校开设更多红色文化课程，让孩子们从小就接受革命传统教育。',
            'ai_response': '历史不会忘记，传承永不停歇，感谢您的守护。',
            'likes': 103,
            'created_at': datetime.utcnow() - timedelta(hours=3)
        }
    ]
    
    # 插入心愿
    wishes = []
    for wish_data in test_wishes:
        wish = Wish(**wish_data)
        db.session.add(wish)
        wishes.append(wish)
    
    db.session.commit()
    print(f'  ✓ 插入了 {len(wishes)} 条心愿')
    
    # 插入测试评论
    test_comments = [
        {
            'wish_id': 1,
            'user_uid': 'Visitor_001',
            'nickname': '游客甲',
            'avatar': '😊',
            'content': '说得太好了！红色文化是我们的根！',
            'created_at': datetime.utcnow() - timedelta(hours=20)
        },
        {
            'wish_id': 1,
            'user_uid': 'Visitor_002',
            'nickname': '游客乙',
            'avatar': '👍',
            'content': '支持！应该让更多人知道德兴的红色历史。',
            'created_at': datetime.utcnow() - timedelta(hours=18)
        },
        {
            'wish_id': 2,
            'user_uid': 'TechFan_999',
            'nickname': '科技粉',
            'avatar': '🚀',
            'content': 'VR 复原是个好主意，科技让历史更生动！',
            'created_at': datetime.utcnow() - timedelta(hours=10)
        }
    ]
    
    for comment_data in test_comments:
        comment = Comment(**comment_data)
        db.session.add(comment)
    
    db.session.commit()
    print(f'  ✓ 插入了 {len(test_comments)} 条评论')
    
    # 插入测试点赞
    test_likes = [
        {'wish_id': 1, 'user_uid': 'Visitor_001'},
        {'wish_id': 1, 'user_uid': 'Visitor_002'},
        {'wish_id': 2, 'user_uid': 'TechFan_999'},
    ]
    
    for like_data in test_likes:
        like = Like(**like_data)
        db.session.add(like)
    
    db.session.commit()
    print(f'  ✓ 插入了 {len(test_likes)} 条点赞记录')


if __name__ == '__main__':
    try:
        init_database()
        print('\n🎉 数据库初始化完成!')
        print('现在可以启动应用了: python app.py')
    except Exception as e:
        print(f'\n❌ 初始化失败: {e}')
        sys.exit(1)
