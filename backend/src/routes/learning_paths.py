from flask import Blueprint, request, jsonify
from src.models.learning import db, LearningPath, Topic, Resource, User
from src.routes.auth import token_required
from sqlalchemy import or_

learning_path_bp = Blueprint('learning_path', __name__)

@learning_path_bp.route('/learning-paths', methods=['GET'])
@token_required
def get_learning_paths(current_user):
    """Get all learning paths for the current user"""
    try:
        page = request.args.get(\'page\', 1, type=int)
        per_page = request.args.get(\'per_page\', 10, type=int)
        subject = request.args.get(\'subject\', \'\')
        difficulty = request.args.get(\'difficulty\', \'\')
        is_active = request.args.get(\'is_active\', type=bool)
        search_query = request.args.get(\'search_query\', \'\')