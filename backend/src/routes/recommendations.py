from flask import Blueprint, request, jsonify
from src.models.learning import LearningPath, Topic, QuizAttempt, Resource
from src.models.user import User
from src.database import db
from src.utils.auth_utils import token_required
from src.services.ai_service import AIService
from sqlalchemy import func

recommendations_bp = Blueprint("recommendations", __name__)

ai_service = AIService()


@recommendations_bp.route("/study-recommendations", methods=["GET"])
@token_required
def get_study_recommendations(current_user):
    """Get personalized study recommendations for the current user"""
    try:
        # Gather user progress data for AI service
        user_progress = {
            "total_learning_paths": LearningPath.query.filter_by(user_id=current_user.id).count(),
            "completed_learning_paths": LearningPath.query.filter_by(
                user_id=current_user.id, progress_percentage=100
            ).count(),
            "total_quizzes_taken": QuizAttempt.query.filter_by(user_id=current_user.id).count(),
            "average_quiz_score": db.session.query(func.avg(QuizAttempt.percentage))
            .filter_by(user_id=current_user.id)
            .scalar()
            or 0,
            "total_resources_completed": Resource.query.join(Topic)
            .join(LearningPath)
            .filter(LearningPath.user_id == current_user.id, Resource.is_completed == True)
            .count(),
            "last_active": current_user.last_login.isoformat() if current_user.last_login else None,
        }

        learning_style = current_user.learning_style if current_user.learning_style else "general"

        recommendations = ai_service.generate_study_recommendations(user_progress, learning_style)
        return jsonify(recommendations), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
