from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.learning import db, User
from src.models.feedback import Feedback, FeedbackComment, ContentRating
from src.utils.validation import validate_required_fields
from datetime import datetime
import json

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/feedback', methods=['POST'])
@jwt_required()
def submit_feedback():
    """Submit new feedback"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['feedback_type', 'title', 'description']
        if not validate_required_fields(data, required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Validate feedback type
        valid_types = ['bug_report', 'feature_request', 'content_feedback', 'general']
        if data['feedback_type'] not in valid_types:
            return jsonify({'error': 'Invalid feedback type'}), 400
        
        # Create new feedback
        feedback = Feedback(
            user_id=current_user_id,
            feedback_type=data['feedback_type'],
            title=data['title'],
            description=data['description'],
            category=data.get('category'),
            priority=data.get('priority', 'medium'),
            related_learning_path_id=data.get('related_learning_path_id'),
            related_quiz_id=data.get('related_quiz_id'),
            related_resource_id=data.get('related_resource_id'),
            browser_info=data.get('browser_info'),
            device_info=data.get('device_info'),
            url_context=data.get('url_context')
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        return jsonify({
            'message': 'Feedback submitted successfully',
            'feedback': feedback.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error submitting feedback: {str(e)}")
        return jsonify({'error': 'Failed to submit feedback'}), 500

@feedback_bp.route('/feedback', methods=['GET'])
@jwt_required()
def get_user_feedback():
    """Get user's feedback submissions"""
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        feedback_type = request.args.get('type')
        
        # Build query
        query = Feedback.query.filter_by(user_id=current_user_id)
        
        if status:
            query = query.filter_by(status=status)
        if feedback_type:
            query = query.filter_by(feedback_type=feedback_type)
        
        # Order by creation date (newest first)
        query = query.order_by(Feedback.created_at.desc())
        
        # Paginate
        feedback_pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        feedback_list = [feedback.to_dict() for feedback in feedback_pagination.items]
        
        return jsonify({
            'feedback': feedback_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': feedback_pagination.total,
                'pages': feedback_pagination.pages,
                'has_next': feedback_pagination.has_next,
                'has_prev': feedback_pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting user feedback: {str(e)}")
        return jsonify({'error': 'Failed to get feedback'}), 500

@feedback_bp.route('/feedback/<int:feedback_id>', methods=['GET'])
@jwt_required()
def get_feedback_detail(feedback_id):
    """Get detailed feedback with comments"""
    try:
        current_user_id = get_jwt_identity()
        
        feedback = Feedback.query.filter_by(
            id=feedback_id, 
            user_id=current_user_id
        ).first()
        
        if not feedback:
            return jsonify({'error': 'Feedback not found'}), 404
        
        # Get comments
        comments = FeedbackComment.query.filter_by(
            feedback_id=feedback_id
        ).order_by(FeedbackComment.created_at.asc()).all()
        
        feedback_dict = feedback.to_dict()
        feedback_dict['comments'] = [comment.to_dict() for comment in comments]
        
        return jsonify({'feedback': feedback_dict}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting feedback detail: {str(e)}")
        return jsonify({'error': 'Failed to get feedback detail'}), 500

@feedback_bp.route('/feedback/<int:feedback_id>/comments', methods=['POST'])
@jwt_required()
def add_feedback_comment(feedback_id):
    """Add comment to feedback"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('comment'):
            return jsonify({'error': 'Comment is required'}), 400
        
        # Check if feedback exists and belongs to user
        feedback = Feedback.query.filter_by(
            id=feedback_id, 
            user_id=current_user_id
        ).first()
        
        if not feedback:
            return jsonify({'error': 'Feedback not found'}), 404
        
        # Create comment
        comment = FeedbackComment(
            feedback_id=feedback_id,
            user_id=current_user_id,
            comment=data['comment'],
            is_admin_comment=False
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'message': 'Comment added successfully',
            'comment': comment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding feedback comment: {str(e)}")
        return jsonify({'error': 'Failed to add comment'}), 500

@feedback_bp.route('/content-rating', methods=['POST'])
@jwt_required()
def submit_content_rating():
    """Submit or update content rating"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['content_type', 'content_id', 'rating']
        if not validate_required_fields(data, required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Validate content type
        valid_types = ['learning_path', 'quiz', 'resource']
        if data['content_type'] not in valid_types:
            return jsonify({'error': 'Invalid content type'}), 400
        
        # Validate rating
        if not isinstance(data['rating'], int) or data['rating'] < 1 or data['rating'] > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        # Check if rating already exists
        existing_rating = ContentRating.query.filter_by(
            user_id=current_user_id,
            content_type=data['content_type'],
            content_id=data['content_id']
        ).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.rating = data['rating']
            existing_rating.review = data.get('review')
            existing_rating.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'message': 'Rating updated successfully',
                'rating': existing_rating.to_dict()
            }), 200
        else:
            # Create new rating
            rating = ContentRating(
                user_id=current_user_id,
                content_type=data['content_type'],
                content_id=data['content_id'],
                rating=data['rating'],
                review=data.get('review')
            )
            
            db.session.add(rating)
            db.session.commit()
            
            return jsonify({
                'message': 'Rating submitted successfully',
                'rating': rating.to_dict()
            }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error submitting content rating: {str(e)}")
        return jsonify({'error': 'Failed to submit rating'}), 500

@feedback_bp.route('/content-rating/<content_type>/<int:content_id>', methods=['GET'])
@jwt_required()
def get_content_ratings(content_type, content_id):
    """Get ratings for specific content"""
    try:
        # Validate content type
        valid_types = ['learning_path', 'quiz', 'resource']
        if content_type not in valid_types:
            return jsonify({'error': 'Invalid content type'}), 400
        
        # Get all ratings for this content
        ratings = ContentRating.query.filter_by(
            content_type=content_type,
            content_id=content_id
        ).all()
        
        if not ratings:
            return jsonify({
                'ratings': [],
                'average_rating': 0,
                'total_ratings': 0
            }), 200
        
        # Calculate average rating
        total_rating = sum(rating.rating for rating in ratings)
        average_rating = total_rating / len(ratings)
        
        return jsonify({
            'ratings': [rating.to_dict() for rating in ratings],
            'average_rating': round(average_rating, 2),
            'total_ratings': len(ratings)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting content ratings: {str(e)}")
        return jsonify({'error': 'Failed to get ratings'}), 500

@feedback_bp.route('/content-rating/user/<content_type>/<int:content_id>', methods=['GET'])
@jwt_required()
def get_user_content_rating(content_type, content_id):
    """Get user's rating for specific content"""
    try:
        current_user_id = get_jwt_identity()
        
        # Validate content type
        valid_types = ['learning_path', 'quiz', 'resource']
        if content_type not in valid_types:
            return jsonify({'error': 'Invalid content type'}), 400
        
        rating = ContentRating.query.filter_by(
            user_id=current_user_id,
            content_type=content_type,
            content_id=content_id
        ).first()
        
        if not rating:
            return jsonify({'rating': None}), 200
        
        return jsonify({'rating': rating.to_dict()}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting user content rating: {str(e)}")
        return jsonify({'error': 'Failed to get user rating'}), 500

@feedback_bp.route('/feedback/stats', methods=['GET'])
@jwt_required()
def get_feedback_stats():
    """Get feedback statistics for the user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get feedback counts by type
        feedback_by_type = db.session.query(
            Feedback.feedback_type,
            db.func.count(Feedback.id).label('count')
        ).filter_by(user_id=current_user_id).group_by(Feedback.feedback_type).all()
        
        # Get feedback counts by status
        feedback_by_status = db.session.query(
            Feedback.status,
            db.func.count(Feedback.id).label('count')
        ).filter_by(user_id=current_user_id).group_by(Feedback.status).all()
        
        # Get total feedback count
        total_feedback = Feedback.query.filter_by(user_id=current_user_id).count()
        
        # Get resolved feedback count
        resolved_feedback = Feedback.query.filter_by(
            user_id=current_user_id, 
            status='resolved'
        ).count()
        
        return jsonify({
            'total_feedback': total_feedback,
            'resolved_feedback': resolved_feedback,
            'feedback_by_type': [
                {'type': item.feedback_type, 'count': item.count} 
                for item in feedback_by_type
            ],
            'feedback_by_status': [
                {'status': item.status, 'count': item.count} 
                for item in feedback_by_status
            ]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting feedback stats: {str(e)}")
        return jsonify({'error': 'Failed to get feedback statistics'}), 500

