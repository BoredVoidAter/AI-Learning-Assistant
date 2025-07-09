from datetime import datetime
from src.database import db

class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    feedback_type = db.Column(db.String(50), nullable=False)  # 'bug_report', 'feature_request', 'content_feedback', 'general'
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))  # 'ui_ux', 'performance', 'content_quality', 'functionality', 'other'
    priority = db.Column(db.String(20), default='medium')  # 'low', 'medium', 'high', 'critical'
    status = db.Column(db.String(20), default='open')  # 'open', 'in_progress', 'resolved', 'closed'
    
    # Related content (optional)
    related_learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'), nullable=True)
    related_quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=True)
    related_resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=True)
    
    # Metadata
    browser_info = db.Column(db.Text)  # User agent, browser version, etc.
    device_info = db.Column(db.Text)  # Screen resolution, device type, etc.
    url_context = db.Column(db.String(500))  # URL where feedback was submitted
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # Admin response
    admin_response = db.Column(db.Text, nullable=True)
    admin_id = db.Column(db.Integer, nullable=True)  # ID of admin who responded
    
    # Relationships
    user = db.relationship('User', backref='feedback_submissions')
    learning_path = db.relationship('LearningPath', backref='feedback')
    quiz = db.relationship('Quiz', backref='feedback')
    resource = db.relationship('Resource', backref='feedback')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'feedback_type': self.feedback_type,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'status': self.status,
            'related_learning_path_id': self.related_learning_path_id,
            'related_quiz_id': self.related_quiz_id,
            'related_resource_id': self.related_resource_id,
            'browser_info': self.browser_info,
            'device_info': self.device_info,
            'url_context': self.url_context,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'admin_response': self.admin_response,
            'admin_id': self.admin_id,
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email
            } if self.user else None,
            'learning_path': {
                'id': self.learning_path.id,
                'title': self.learning_path.title
            } if self.learning_path else None,
            'quiz': {
                'id': self.quiz.id,
                'title': self.quiz.title
            } if self.quiz else None,
            'resource': {
                'id': self.resource.id,
                'title': self.resource.title
            } if self.resource else None
        }

class FeedbackComment(db.Model):
    __tablename__ = 'feedback_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    is_admin_comment = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    feedback = db.relationship('Feedback', backref='comments')
    user = db.relationship('User', backref='feedback_comments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'feedback_id': self.feedback_id,
            'user_id': self.user_id,
            'comment': self.comment,
            'is_admin_comment': self.is_admin_comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user': {
                'id': self.user.id,
                'username': self.user.username
            } if self.user else None
        }

class ContentRating(db.Model):
    __tablename__ = 'content_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)  # 'learning_path', 'quiz', 'resource'
    content_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='content_ratings')
    
    # Composite unique constraint to prevent duplicate ratings
    __table_args__ = (db.UniqueConstraint('user_id', 'content_type', 'content_id', name='unique_user_content_rating'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_type': self.content_type,
            'content_id': self.content_id,
            'rating': self.rating,
            'review': self.review,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user': {
                'id': self.user.id,
                'username': self.user.username
            } if self.user else None
        }

