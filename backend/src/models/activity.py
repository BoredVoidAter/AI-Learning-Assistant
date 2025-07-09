
from src.database import db
from datetime import datetime

class UserActivity(db.Model):
    __tablename__ = 'user_activity'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    details = db.Column(db.JSON)

    def __repr__(self):
        return f'<UserActivity {self.id}>'
