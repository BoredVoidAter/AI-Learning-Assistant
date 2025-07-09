from flask import Blueprint, request, jsonify
from src.models.learning import LearningPath, Topic, Resource
from src.models.user import User
from src.database import db
from src.utils.auth_utils import token_required
from sqlalchemy import or_

learning_path_bp = Blueprint("learning_path", __name__)


@learning_path_bp.route("/learning-paths", methods=["GET"])
@token_required
def get_learning_paths(current_user):
    """Get all learning paths for the current user"""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        subject = request.args.get("subject", "")
        difficulty = request.args.get("difficulty", "")
        is_active = request.args.get("is_active", type=lambda v: v.lower() == 'true')
        search_query = request.args.get("search_query", "")

        query = LearningPath.query.filter_by(user_id=current_user.id)

        if subject:
            query = query.filter(LearningPath.subject.ilike(f"%{subject}%"))

        if difficulty:
            query = query.filter(LearningPath.difficulty_level.ilike(f"%{difficulty}%"))

        if is_active is not None:
            query = query.filter(LearningPath.is_active == is_active)

        if search_query:
            query = query.filter(
                or_(
                    LearningPath.title.ilike(f"%{search_query}%"),
                    LearningPath.description.ilike(f"%{search_query}%"),
                )
            )

        learning_paths = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify(
            {
                "learning_paths": [
                    learning_path.to_dict() for learning_path in learning_paths.items
                ],
                "total": learning_paths.total,
                "pages": learning_paths.pages,
                "current_page": learning_paths.page,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 400
