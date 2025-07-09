from datetime import datetime
from src.database import db

class Achievement(db.Model):
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), nullable=False)  # Icon name for frontend
    category = db.Column(db.String(50), nullable=False)  # 'learning', 'quiz', 'social', 'milestone'
    points = db.Column(db.Integer, default=0)  # Points awarded for this achievement
    rarity = db.Column(db.String(20), default='common')  # 'common', 'rare', 'epic', 'legendary'
    
    # Conditions for earning the achievement
    condition_type = db.Column(db.String(50), nullable=False)  # 'count', 'streak', 'score', 'time'
    condition_target = db.Column(db.Integer, nullable=False)  # Target value to achieve
    condition_resource = db.Column(db.String(50), nullable=False)  # What to count/measure
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'category': self.category,
            'points': self.points,
            'rarity': self.rarity,
            'condition_type': self.condition_type,
            'condition_target': self.condition_target,
            'condition_resource': self.condition_resource,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class UserAchievement(db.Model):
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress_value = db.Column(db.Integer, default=0)  # Current progress towards achievement
    
    # Relationships
    user = db.relationship('User', backref='user_achievements')
    achievement = db.relationship('Achievement', backref='user_achievements')
    
    # Unique constraint to prevent duplicate achievements
    __table_args__ = (db.UniqueConstraint('user_id', 'achievement_id', name='unique_user_achievement'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'achievement_id': self.achievement_id,
            'earned_at': self.earned_at.isoformat() if self.earned_at else None,
            'progress_value': self.progress_value,
            'achievement': self.achievement.to_dict() if self.achievement else None
        }

class UserLevel(db.Model):
    __tablename__ = 'user_levels'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    current_level = db.Column(db.Integer, default=1)
    total_points = db.Column(db.Integer, default=0)
    points_to_next_level = db.Column(db.Integer, default=100)
    
    # Experience breakdown
    learning_points = db.Column(db.Integer, default=0)
    quiz_points = db.Column(db.Integer, default=0)
    achievement_points = db.Column(db.Integer, default=0)
    social_points = db.Column(db.Integer, default=0)
    
    # Streaks
    current_learning_streak = db.Column(db.Integer, default=0)
    longest_learning_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('level', uselist=False))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'current_level': self.current_level,
            'total_points': self.total_points,
            'points_to_next_level': self.points_to_next_level,
            'learning_points': self.learning_points,
            'quiz_points': self.quiz_points,
            'achievement_points': self.achievement_points,
            'social_points': self.social_points,
            'current_learning_streak': self.current_learning_streak,
            'longest_learning_streak': self.longest_learning_streak,
            'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Badge(db.Model):
    __tablename__ = 'badges'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(20), nullable=False)  # Hex color code
    category = db.Column(db.String(50), nullable=False)
    
    # Badge earning conditions
    condition_type = db.Column(db.String(50), nullable=False)
    condition_value = db.Column(db.Integer, nullable=False)
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'category': self.category,
            'condition_type': self.condition_type,
            'condition_value': self.condition_value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class UserBadge(db.Model):
    __tablename__ = 'user_badges'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='user_badges')
    badge = db.relationship('Badge', backref='user_badges')
    
    # Unique constraint to prevent duplicate badges
    __table_args__ = (db.UniqueConstraint('user_id', 'badge_id', name='unique_user_badge'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'badge_id': self.badge_id,
            'earned_at': self.earned_at.isoformat() if self.earned_at else None,
            'badge': self.badge.to_dict() if self.badge else None
        }

class Leaderboard(db.Model):
    __tablename__ = 'leaderboards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    leaderboard_type = db.Column(db.String(50), nullable=False)  # 'weekly', 'monthly', 'all_time'
    category = db.Column(db.String(50), nullable=False)  # 'points', 'quizzes', 'learning_paths', 'streak'
    score = db.Column(db.Integer, nullable=False)
    rank = db.Column(db.Integer, nullable=False)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='leaderboard_entries')
    
    # Unique constraint for user per leaderboard period
    __table_args__ = (db.UniqueConstraint('user_id', 'leaderboard_type', 'category', 'period_start', name='unique_leaderboard_entry'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'leaderboard_type': self.leaderboard_type,
            'category': self.category,
            'score': self.score,
            'rank': self.rank,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user': {
                'id': self.user.id,
                'username': self.user.username
            } if self.user else None
        }

