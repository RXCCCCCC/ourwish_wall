"""
数据库模型定义
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Wish(db.Model):
    """心愿表"""
    __tablename__ = 'wishes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_uid = db.Column(db.String(64), nullable=False, index=True)
    nickname = db.Column(db.String(64), nullable=False)
    avatar = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(32), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=True)
    likes = db.Column(db.Integer, default=0)
    client_ip = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 关联评论
    comments = db.relationship('Comment', backref='wish', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_comments=False):
        """转换为字典格式"""
        data = {
            'id': self.id,
            'user_uid': self.user_uid,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'category': self.category,
            'content': self.content,
            'ai_response': self.ai_response,
            'likes': self.likes,
            'created_at': self.created_at.strftime('%Y年%m月%d日') if self.created_at else '',
        }
        
        if include_comments:
            data['comments'] = [comment.to_dict() for comment in self.comments.all()]
        
        return data
    
    def __repr__(self):
        return f'<Wish {self.id}: {self.nickname}>'


class Comment(db.Model):
    """评论表"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    wish_id = db.Column(db.Integer, db.ForeignKey('wishes.id'), nullable=False, index=True)
    user_uid = db.Column(db.String(64), nullable=False, index=True)
    nickname = db.Column(db.String(64), nullable=False)
    avatar = db.Column(db.String(255), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'wish_id': self.wish_id,
            'user_uid': self.user_uid,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'content': self.content,
            'created_at': self.created_at.strftime('%Y年%m月%d日') if self.created_at else '',
        }
    
    def __repr__(self):
        return f'<Comment {self.id} on Wish {self.wish_id}>'


class Like(db.Model):
    """点赞记录表 - 防止重复点赞"""
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    wish_id = db.Column(db.Integer, db.ForeignKey('wishes.id'), nullable=False, index=True)
    user_uid = db.Column(db.String(64), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 联合唯一索引 - 一个用户对一条心愿只能点赞一次
    __table_args__ = (
        db.UniqueConstraint('wish_id', 'user_uid', name='unique_wish_user_like'),
    )
    
    def __repr__(self):
        return f'<Like {self.user_uid} -> Wish {self.wish_id}>'


class RateLimit(db.Model):
    """访问频率限制记录表"""
    __tablename__ = 'rate_limits'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_ip = db.Column(db.String(45), nullable=False, index=True)
    action = db.Column(db.String(32), nullable=False)  # 操作类型: 'post_wish', 'post_comment'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<RateLimit {self.client_ip} - {self.action}>'
