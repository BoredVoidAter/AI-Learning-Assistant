from flask import Blueprint, request, jsonify
from src.models.learning import db, UserActivity
from src.utils.auth_utils import token_required
from datetime import datetime

activity_bp = Blueprint("activity_bp", __name__)

@activity_bp.route("/activities", methods=["POST"])
@token_required
def log_activity(current_user):
    data = request.get_json()
    activity_type = data.get("activity_type")
    activity_details = data.get("activity_details")

    if not activity_type:
        return jsonify({"error": "Activity type is required"}), 400

    new_activity = UserActivity(
        user_id=current_user.id,
        activity_type=activity_type,
        activity_details=activity_details
    )
    db.session.add(new_activity)
    db.session.commit()

    return jsonify({"message": "Activity logged successfully", "activity": new_activity.to_dict()}), 201

@activity_bp.route("/activities", methods=["GET"])
@token_required
def get_activities(current_user):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    activity_type = request.args.get("activity_type")

    query = UserActivity.query.filter_by(user_id=current_user.id)

    if activity_type:
        query = query.filter_by(activity_type=activity_type)

    activities = query.order_by(UserActivity.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "activities": [activity.to_dict() for activity in activities.items],
        "total_activities": activities.total,
        "pages": activities.pages,
        "current_page": activities.page
    }), 200


