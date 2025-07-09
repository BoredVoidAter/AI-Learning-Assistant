from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import jwt
import os
from src.database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Learning preferences
    learning_style = db.Column(db.String(50), nullable=True)  # visual, auditory, kinesthetic, reading
    preferred_difficulty = db.Column(db.String(20), default="intermediate")  # beginner, intermediate, advanced
    daily_goal_minutes = db.Column(db.Integer, default=30)
    last_login = db.Column(db.DateTime, nullable=True)
    study_reminders_enabled = db.Column(db.Boolean, default=True)
    notification_email = db.Column(db.Boolean, default=True)
    # Relationships
    learning_paths = db.relationship("LearningPath", backref="user", lazy=True, cascade="all, delete-orphan")
    quiz_attempts = db.relationship("QuizAttempt", backref="user", lazy=True, cascade="all, delete-orphan")
    notes = db.relationship("Note", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the user's password"""
        return check_password_hash(self.password_hash, password)

    def generate_token(self):
        """Generate JWT token for authentication"""
        payload = {
            "user_id": self.id,
            "username": self.username,
            "exp": datetime.utcnow().timestamp() + 86400,  # 24 hours
        }
        return jwt.encode(payload, os.environ.get("SECRET_KEY", "default-secret"), algorithm="HS256")

    @staticmethod
    def verify_token(token):
        """Verify JWT token and return user"""
        try:
            payload = jwt.decode(token, os.environ.get("SECRET_KEY", "default-secret"), algorithms=["HS256"])
            return User.query.get(payload["user_id"])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "learning_style": self.learning_style,
            "preferred_difficulty": self.preferred_difficulty,
            "daily_goal_minutes": self.daily_goal_minutes,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "study_reminders_enabled": self.study_reminders_enabled,
            "notification_email": self.notification_email,
        }