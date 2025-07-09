from flask import Blueprint, request, jsonify
from src.models.user import User
from src.database import db
from src.utils.auth_utils import token_required

user_bp = Blueprint("user", __name__)


@user_bp.route("/profile", methods=["GET"])
@token_required
def get_user_profile(current_user):
    """Get the current user's profile information"""
    return jsonify(current_user.to_dict()), 200


@user_bp.route("/profile", methods=["PUT"])
@token_required
def update_user_profile(current_user):
    """Update the current user's profile information"""
    data = request.get_json()

    current_user.first_name = data.get("first_name", current_user.first_name)
    current_user.last_name = data.get("last_name", current_user.last_name)
    current_user.learning_style = data.get("learning_style", current_user.learning_style)
    current_user.preferred_difficulty = data.get("preferred_difficulty", current_user.preferred_difficulty)
    current_user.daily_goal_minutes = data.get("daily_goal_minutes", current_user.daily_goal_minutes)
    current_user.study_reminders_enabled = data.get("study_reminders_enabled", current_user.study_reminders_enabled)
    current_user.notification_email = data.get("notification_email", current_user.notification_email)

    db.session.commit()
    return jsonify(current_user.to_dict()), 200


@user_bp.route("/profile/password", methods=["PUT"])
@token_required
def update_password(current_user):
    """Update the current user's password"""
    data = request.get_json()
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not old_password or not new_password:
        return jsonify({"error": "Old password and new password are required"}), 400

    if not current_user.check_password(old_password):
        return jsonify({"error": "Invalid old password"}), 401

    current_user.set_password(new_password)
    db.session.commit()
    return jsonify({"message": "Password updated successfully"}), 200


@user_bp.route("/profile/delete", methods=["DELETE"])
@token_required
def delete_user_profile(current_user):
    """Delete the current user's profile"""
    db.session.delete(current_user)
    db.session.commit()
    return jsonify({"message": "User profile deleted successfully"}), 200
