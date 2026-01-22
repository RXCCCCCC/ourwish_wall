"""
Flask 主应用 - 心愿墙后端 API
"""
import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import func

from config import config
from models import db, Wish, Comment, Like, CommentLike, RateLimit
from services.ai_service import AIService
from services.text_filter import TextFilter


def create_app(config_name='default'):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # 注册路由
    register_routes(app)
    
    # 注册错误处理
    register_error_handlers(app)
    
    return app


def get_client_ip():
    """获取客户端 IP 地址"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr


def check_rate_limit(action, limit_period=60, max_requests=1):
    """
    检查频率限制
    
    Args:
        action: 操作类型
        limit_period: 限制周期(秒)
        max_requests: 周期内最大请求数
        
    Returns:
        tuple: (is_allowed, error_message)
    """
    client_ip = get_client_ip()
    cutoff_time = datetime.utcnow() - timedelta(seconds=limit_period)
    
    # 查询该 IP 在限制周期内的请求次数
    recent_requests = RateLimit.query.filter(
        RateLimit.client_ip == client_ip,
        RateLimit.action == action,
        RateLimit.created_at > cutoff_time
    ).count()
    
    if recent_requests >= max_requests:
        return False, f'操作过于频繁, 请 {limit_period} 秒后再试'
    
    # 记录本次请求
    rate_limit = RateLimit(client_ip=client_ip, action=action)
    db.session.add(rate_limit)
    db.session.commit()
    
    return True, None


def register_routes(app):
    """注册所有路由"""
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """健康检查"""
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @app.route('/api/wishes', methods=['GET'])
    def get_wishes():
        """
        获取心愿列表
        Query params:
            - page: 页码 (default: 1)
            - per_page: 每页数量 (default: 10)
            - category: 类别过滤 (optional)
            - user_uid: 当前用户ID (optional, 用于返回点赞状态)
        """
        page = request.args.get('page', 1, type=int)
        per_page = min(
            request.args.get('per_page', app.config['DEFAULT_PAGE_SIZE'], type=int),
            app.config['MAX_PAGE_SIZE']
        )
        category = request.args.get('category', type=str)
        user_uid = request.args.get('user_uid', type=str)
        
        # 构建查询
        query = Wish.query
        if category:
            query = query.filter_by(category=category)
        
        # 按创建时间倒序
        query = query.order_by(Wish.created_at.desc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        wishes = [wish.to_dict(include_comments=True, user_uid=user_uid) for wish in pagination.items]
        
        return jsonify({
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'wishes': wishes
        })
    
    @app.route('/api/wishes', methods=['POST'])
    def create_wish():
        """
        发布心愿
        Request body:
            {
                "user_uid": "RedGuard_007",
                "nickname": "红脉卫士",
                "avatar": "https://...",
                "category": "乡村建设",
                "content": "希望家乡的路修得更好..."
            }
        """
        # 频率限制检查
        if app.config['RATE_LIMIT_ENABLED']:
            is_allowed, error_msg = check_rate_limit(
                'post_wish',
                app.config['RATE_LIMIT_PERIOD'],
                app.config['RATE_LIMIT_MAX_REQUESTS']
            )
            if not is_allowed:
                return jsonify({'error': error_msg}), 429
        
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['user_uid', 'nickname', 'category', 'content']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'缺少必填字段: {field}'}), 400
        
        # 验证类别
        valid_categories = ['红色传承', '乡村建设', '产业发展', '生态环保']
        if data['category'] not in valid_categories:
            return jsonify({'error': '无效的心愿类别'}), 400
        
        # 内容验证和过滤
        content = data['content'].strip()
        is_valid, error_msg = TextFilter.validate_content(
            content, 
            app.config['MAX_CONTENT_LENGTH']
        )
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # 生成 AI 回复
        ai_response = AIService.generate_response(content, data['category'])
        
        # 创建心愿
        wish = Wish(
            user_uid=data['user_uid'],
            nickname=data['nickname'],
            avatar=data.get('avatar', ''),
            category=data['category'],
            content=content,
            ai_response=ai_response,
            client_ip=get_client_ip()
        )
        
        try:
            db.session.add(wish)
            db.session.commit()
            return jsonify(wish.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'创建心愿失败: {e}')
            return jsonify({'error': '创建心愿失败, 请稍后重试'}), 500
    
    @app.route('/api/wishes/<int:wish_id>/like', methods=['POST'])
    def toggle_like(wish_id):
        """
        点赞/取消点赞
        Request body:
            {
                "user_uid": "RedGuard_007",
                "action": "like"  # 或 "unlike"
            }
        """
        wish = Wish.query.get_or_404(wish_id)
        data = request.get_json()
        
        user_uid = data.get('user_uid')
        action = data.get('action', 'like')
        
        if not user_uid:
            return jsonify({'error': '缺少 user_uid'}), 400
        
        # 查找是否已点赞
        existing_like = Like.query.filter_by(
            wish_id=wish_id,
            user_uid=user_uid
        ).first()
        
        try:
            if action == 'like':
                if existing_like:
                    return jsonify({'error': '您已经点赞过了'}), 400
                
                # 添加点赞
                like = Like(wish_id=wish_id, user_uid=user_uid)
                db.session.add(like)
                wish.likes += 1
                
            elif action == 'unlike':
                if not existing_like:
                    return jsonify({'error': '您还未点赞'}), 400
                
                # 取消点赞
                db.session.delete(existing_like)
                wish.likes = max(0, wish.likes - 1)
            
            else:
                return jsonify({'error': '无效的操作'}), 400
            
            db.session.commit()
            return jsonify({
                'id': wish.id,
                'likes': wish.likes,
                'action': action
            })
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'点赞操作失败: {e}')
            return jsonify({'error': '操作失败, 请稍后重试'}), 500
    
    @app.route('/api/wishes/<int:wish_id>/comments', methods=['GET'])
    def get_comments(wish_id):
        """获取心愿的评论列表"""
        wish = Wish.query.get_or_404(wish_id)
        user_uid = request.args.get('user_uid', type=str)
        comments = Comment.query.filter_by(wish_id=wish_id)\
            .order_by(Comment.created_at.desc())\
            .all()
        
        return jsonify({
            'wish_id': wish_id,
            'comments': [comment.to_dict(user_uid=user_uid) for comment in comments]
        })
    
    @app.route('/api/wishes/<int:wish_id>/comments', methods=['POST'])
    def create_comment(wish_id):
        """
        添加评论
        Request body:
            {
                "user_uid": "RedGuard_007",
                "nickname": "张三",
                "avatar": "https://...",
                "content": "很好的想法"
            }
        """
        wish = Wish.query.get_or_404(wish_id)
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['user_uid', 'nickname', 'content']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'缺少必填字段: {field}'}), 400
        
        # 内容验证
        content = data['content'].strip()
        is_valid, error_msg = TextFilter.validate_content(content, max_length=200)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # 创建评论
        comment = Comment(
            wish_id=wish_id,
            user_uid=data['user_uid'],
            nickname=data['nickname'],
            avatar=data.get('avatar', ''),
            content=content
        )
        
        try:
            db.session.add(comment)
            db.session.commit()
            return jsonify(comment.to_dict(user_uid=data['user_uid'])), 201
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'创建评论失败: {e}')
            return jsonify({'error': '创建评论失败, 请稍后重试'}), 500
    
    @app.route('/api/wishes/<int:wish_id>/comments/<int:comment_id>', methods=['DELETE'])
    def delete_comment(wish_id, comment_id):
        """
        删除评论 (仅评论作者或心愿发布者可删除)
        Request body:
            {
                "user_uid": "RedGuard_007"
            }
        """
        wish = Wish.query.get_or_404(wish_id)
        comment = Comment.query.get_or_404(comment_id)
        
        if comment.wish_id != wish_id:
            return jsonify({'error': '评论不属于该心愿'}), 400
        
        data = request.get_json() or {}
        user_uid = data.get('user_uid')
        
        if not user_uid:
            return jsonify({'error': '缺少 user_uid'}), 400
        
        # 权限检查: 评论作者或心愿发布者可删除
        if user_uid != comment.user_uid and user_uid != wish.user_uid:
            return jsonify({'error': '无权删除此评论'}), 403
        
        try:
            # 先删除关联的评论点赞记录
            CommentLike.query.filter_by(comment_id=comment_id).delete(synchronize_session=False)
            
            db.session.delete(comment)
            db.session.commit()
            return jsonify({'ok': True, 'message': '评论已删除'})
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'删除评论失败: {e}')
            return jsonify({'error': '删除失败, 请稍后重试'}), 500
    
    @app.route('/api/wishes/<int:wish_id>/comments/<int:comment_id>/like', methods=['POST'])
    def toggle_comment_like(wish_id, comment_id):
        """
        评论点赞/取消点赞
        Request body:
            {
                "user_uid": "RedGuard_007",
                "action": "like"  # 或 "unlike"
            }
        """
        wish = Wish.query.get_or_404(wish_id)
        comment = Comment.query.get_or_404(comment_id)
        
        if comment.wish_id != wish_id:
            return jsonify({'error': '评论不属于该心愿'}), 400
        
        data = request.get_json()
        user_uid = data.get('user_uid')
        action = data.get('action', 'like')
        
        if not user_uid:
            return jsonify({'error': '缺少 user_uid'}), 400
        
        # 查找是否已点赞
        existing_like = CommentLike.query.filter_by(
            comment_id=comment_id,
            user_uid=user_uid
        ).first()
        
        try:
            if action == 'like':
                if existing_like:
                    return jsonify({'error': '您已经点赞过了'}), 400
                
                # 添加点赞
                like = CommentLike(comment_id=comment_id, user_uid=user_uid)
                db.session.add(like)
                comment.likes += 1
                
            elif action == 'unlike':
                if not existing_like:
                    return jsonify({'error': '您还未点赞'}), 400
                
                # 取消点赞
                db.session.delete(existing_like)
                comment.likes = max(0, comment.likes - 1)
            
            else:
                return jsonify({'error': '无效的操作'}), 400
            
            db.session.commit()
            return jsonify({
                'id': comment.id,
                'likes': comment.likes,
                'action': action
            })
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'评论点赞操作失败: {e}')
            return jsonify({'error': '操作失败, 请稍后重试'}), 500
    
    @app.route('/api/wishes/<int:wish_id>', methods=['DELETE'])
    def delete_wish(wish_id):
        """
        删除心愿 (仅发布者可删除)
        Request body:
            {
                "user_uid": "RedGuard_007"
            }
        """
        wish = Wish.query.get_or_404(wish_id)
        data = request.get_json()
        user_uid = data.get('user_uid')
        
        if not user_uid:
            return jsonify({'error': '缺少 user_uid'}), 400
        
        # 权限检查: 仅发布者可删除
        if user_uid != wish.user_uid:
            return jsonify({'error': '无权删除此心愿'}), 403
        
        try:
            # 先删除关联的点赞和评论，避免数据库外键约束阻止删除
            try:
                Like.query.filter_by(wish_id=wish_id).delete(synchronize_session=False)
            except Exception:
                # 如果 likes 表不存在或出错，忽略并继续
                pass

            try:
                # 删除该心愿下所有评论的点赞记录
                comment_ids = [c.id for c in Comment.query.filter_by(wish_id=wish_id).all()]
                if comment_ids:
                    CommentLike.query.filter(CommentLike.comment_id.in_(comment_ids)).delete(synchronize_session=False)
            except Exception:
                pass

            try:
                Comment.query.filter_by(wish_id=wish_id).delete(synchronize_session=False)
            except Exception:
                pass

            db.session.delete(wish)
            db.session.commit()
            return jsonify({'ok': True, 'message': '心愿已删除'})
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'删除心愿失败: {e}')
            return jsonify({'error': '删除失败, 请稍后重试'}), 500
    
    @app.route('/api/stats', methods=['GET'])
    def get_stats():
        """
        获取统计数据 (用于前端图表)
        Returns:
            {
                "pie_data": [...],
                "word_cloud": [...]
            }
        """
        # 饼图数据 - 按类别统计心愿数量
        category_stats = db.session.query(
            Wish.category,
            func.count(Wish.id).label('count')
        ).group_by(Wish.category).all()
        
        pie_data = [
            {'name': category, 'value': count}
            for category, count in category_stats
        ]
        
        # 词云数据 - 简化实现: 统计类别和关键词
        # ⚠️ 实际使用时可以使用 jieba 等分词库进行更精确的词频统计
        word_cloud = [
            {'name': '红色基因', 'value': 100},
            {'name': '乡村振兴', 'value': 92},
            {'name': '德兴', 'value': 80},
            {'name': '科技赋能', 'value': 73},
            {'name': '旅游', 'value': 65},
            {'name': '传承', 'value': 60},
            {'name': '创新', 'value': 55},
            {'name': '富裕', 'value': 48},
            {'name': '美好生活', 'value': 42},
            {'name': '生态', 'value': 39}
        ]
        
        return jsonify({
            'pie_data': pie_data,
            'word_cloud': word_cloud
        })


def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': '资源不存在'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'服务器错误: {error}')
        return jsonify({'error': '服务器内部错误, 请稍后重试'}), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        db.session.rollback()
        app.logger.error(f'未处理的异常: {error}')
        return jsonify({'error': '请求处理失败'}), 500


if __name__ == '__main__':
    # 获取环境变量指定的配置 (默认为开发环境)
    config_name = os.getenv('FLASK_ENV', 'development')
    app = create_app(config_name)
    
    # 创建数据库表 (仅开发环境, 生产环境请使用迁移工具)
    with app.app_context():
        db.create_all()
    
    # 启动应用
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
