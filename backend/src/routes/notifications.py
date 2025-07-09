from flask import Blueprint, request, jsonify
from src.models.notification import Notification
from src.database import db
from src.utils.auth_utils import token_required
from datetime import datetime

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("/notifications", methods=["GET"])
@token_required
def get_notifications(current_user):
    """Get all notifications for the current user"""
    notifications = (
        Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    )
    return jsonify([n.to_dict() for n in notifications]), 200


@notifications_bp.route("/notifications/unread_count", methods=["GET"])
@token_required
def get_unread_notifications_count(current_user):
    """Get the count of unread notifications for the current user"""
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({"unread_count": count}), 200


@notifications_bp.route("/notifications/<int:notification_id>/mark_read", methods=["PUT"])
@token_required
def mark_notification_read(current_user, notification_id):
    """Mark a specific notification as read"""
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first()
    if not notification:
        return jsonify({"error": "Notification not found"}), 404

    notification.is_read = True
    db.session.commit()
    return jsonify(notification.to_dict()), 200


@notifications_bp.route("/notifications/mark_all_read", methods=["PUT"])
@token_required
def mark_all_notifications_read(current_user):
    """Mark all notifications for the current user as read"""
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).all()
    for notification in notifications:
        notification.is_read = True
    db.session.commit()
    return jsonify({"message": "All notifications marked as read"}), 200


@notifications_bp.route("/notifications/<int:notification_id>", methods=["DELETE"])
@token_required
def delete_notification(current_user, notification_id):
    """Delete a specific notification"""
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first()
    if not notification:
        return jsonify({"error": "Notification not found"}), 404

    db.session.delete(notification)
    db.session.commit()
    return jsonify({"message": "Notification deleted successfully"}), 200


# Example of how to create a notification (can be called from other parts of the backend)
def create_notification(user_id, message, notification_type=None):
    notification = Notification(user_id=user_id, message=message, notification_type=notification_type)
    db.session.add(notification)
    db.session.commit()
    return notification
