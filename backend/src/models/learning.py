from datetime import datetime
from src.database import db


class LearningPath(db.Model):
    __tablename__ = "learning_paths"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject = db.Column(db.String(100), nullable=False)
    difficulty_level = db.Column(db.String(20), default="beginner")
    estimated_hours = db.Column(db.Integer, default=10)
    is_active = db.Column(db.Boolean, default=True)
    progress_percentage = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    topics = db.relationship("Topic", backref="learning_path", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "subject": self.subject,
            "difficulty_level": self.difficulty_level,
            "estimated_hours": self.estimated_hours,
            "is_active": self.is_active,
            "progress_percentage": self.progress_percentage,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "topics_count": len(self.topics) if self.topics else 0,
        }


class Topic(db.Model):
    __tablename__ = "topics"

    id = db.Column(db.Integer, primary_key=True)
    learning_path_id = db.Column(db.Integer, db.ForeignKey("learning_paths.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    order_index = db.Column(db.Integer, default=0)
    is_completed = db.Column(db.Boolean, default=False)
    completion_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    resources = db.relationship("Resource", backref="topic", lazy=True, cascade="all, delete-orphan")
    quizzes = db.relationship("Quiz", backref="topic", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "learning_path_id": self.learning_path_id,
            "title": self.title,
            "description": self.description,
            "order_index": self.order_index,
            "is_completed": self.is_completed,
            "completion_date": self.completion_date.isoformat() if self.completion_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resources_count": len(self.resources) if self.resources else 0,
            "quizzes_count": len(self.quizzes) if self.quizzes else 0,
        }


class Resource(db.Model):
    __tablename__ = "resources"

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    resource_type = db.Column(db.String(50), nullable=False)  # video, article, book, course, etc.
    url = db.Column(db.String(500), nullable=True)
    content = db.Column(db.Text, nullable=True)  # For stored content
    duration_minutes = db.Column(db.Integer, nullable=True)
    difficulty_level = db.Column(db.String(20), default="intermediate")
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "topic_id": self.topic_id,
            "title": self.title,
            "description": self.description,
            "resource_type": self.resource_type,
            "url": self.url,
            "content": self.content,
            "duration_minutes": self.duration_minutes,
            "difficulty_level": self.difficulty_level,
            "is_completed": self.is_completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Quiz(db.Model):
    __tablename__ = "quizzes"

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    difficulty_level = db.Column(db.String(20), default="intermediate")
    time_limit_minutes = db.Column(db.Integer, default=15)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    questions = db.relationship("Question", backref="quiz", lazy=True, cascade="all, delete-orphan")
    attempts = db.relationship("QuizAttempt", backref="quiz", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "topic_id": self.topic_id,
            "title": self.title,
            "description": self.description,
            "difficulty_level": self.difficulty_level,
            "time_limit_minutes": self.time_limit_minutes,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "questions_count": len(self.questions) if self.questions else 0,
        }


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), default="multiple_choice")  # multiple_choice, true_false, short_answer
    correct_answer = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=True)  # For multiple choice questions
    explanation = db.Column(db.Text, nullable=True)
    points = db.Column(db.Integer, default=1)
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "quiz_id": self.quiz_id,
            "question_text": self.question_text,
            "question_type": self.question_type,
            "correct_answer": self.correct_answer,
            "options": self.options,
            "explanation": self.explanation,
            "points": self.points,
            "order_index": self.order_index,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)
    score = db.Column(db.Float, default=0.0)
    max_score = db.Column(db.Float, default=0.0)
    percentage = db.Column(db.Float, default=0.0)
    time_taken_minutes = db.Column(db.Integer, nullable=True)
    answers = db.Column(db.JSON, nullable=True)  # Store user answers
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "quiz_id": self.quiz_id,
            "score": self.score,
            "max_score": self.max_score,
            "percentage": self.percentage,
            "time_taken_minutes": self.time_taken_minutes,
            "answers": self.answers,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.id"), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.JSON, nullable=True)  # Array of tags
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "resource_id": self.resource_id,
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "is_favorite": self.is_favorite,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }