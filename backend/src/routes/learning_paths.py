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
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        subject = request.args.get('subject', '')
        difficulty = request.args.get('difficulty', '')
        is_active = request.args.get('is_active', type=bool)
        
        # Build query
        query = LearningPath.query.filter(LearningPath.user_id == current_user.id)
        
        # Apply filters
        if subject:
            query = query.filter(LearningPath.subject.ilike(f'%{subject}%'))
        if difficulty:
            query = query.filter(LearningPath.difficulty_level == difficulty)
        if is_active is not None:
            query = query.filter(LearningPath.is_active == is_active)
        
        # Order by creation date (newest first)
        query = query.order_by(LearningPath.created_at.desc())
        
        # Paginate results
        learning_paths = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'learning_paths': [path.to_dict() for path in learning_paths.items],
            'total': learning_paths.total,
            'pages': learning_paths.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_path_bp.route('/learning-paths', methods=['POST'])
@token_required
def create_learning_path(current_user):
    """Create a new learning path"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'subject']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate difficulty level
        difficulty = data.get('difficulty_level', 'beginner')
        if difficulty not in ['beginner', 'intermediate', 'advanced']:
            return jsonify({'error': 'Invalid difficulty level'}), 400
        
        # Create new learning path
        learning_path = LearningPath(
            user_id=current_user.id,
            title=data['title'].strip(),
            description=data.get('description', '').strip(),
            subject=data['subject'].strip(),
            difficulty_level=difficulty,
            estimated_hours=data.get('estimated_hours', 10)
        )
        
        db.session.add(learning_path)
        db.session.commit()
        
        return jsonify({
            'message': 'Learning path created successfully',
            'learning_path': learning_path.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@learning_path_bp.route('/learning-paths/<int:path_id>', methods=['GET'])
@token_required
def get_learning_path(current_user, path_id):
    """Get a specific learning path with its topics"""
    try:
        learning_path = LearningPath.query.filter(
            LearningPath.id == path_id,
            LearningPath.user_id == current_user.id
        ).first()
        
        if not learning_path:
            return jsonify({'error': 'Learning path not found'}), 404
        
        # Get topics with their resources
        topics = Topic.query.filter(
            Topic.learning_path_id == path_id
        ).order_by(Topic.order_index).all()
        
        path_data = learning_path.to_dict()
        path_data['topics'] = []
        
        for topic in topics:
            topic_data = topic.to_dict()
            topic_data['resources'] = [resource.to_dict() for resource in topic.resources]
            path_data['topics'].append(topic_data)
        
        return jsonify({
            'learning_path': path_data
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_path_bp.route('/learning-paths/<int:path_id>', methods=['PUT'])
@token_required
def update_learning_path(current_user, path_id):
    """Update a learning path"""
    try:
        learning_path = LearningPath.query.filter(
            LearningPath.id == path_id,
            LearningPath.user_id == current_user.id
        ).first()
        
        if not learning_path:
            return jsonify({'error': 'Learning path not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'title' in data:
            learning_path.title = data['title'].strip()
        if 'description' in data:
            learning_path.description = data['description'].strip()
        if 'subject' in data:
            learning_path.subject = data['subject'].strip()
        if 'difficulty_level' in data:
            if data['difficulty_level'] in ['beginner', 'intermediate', 'advanced']:
                learning_path.difficulty_level = data['difficulty_level']
        if 'estimated_hours' in data:
            try:
                hours = int(data['estimated_hours'])
                if hours > 0:
                    learning_path.estimated_hours = hours
            except (ValueError, TypeError):
                pass
        if 'is_active' in data:
            learning_path.is_active = bool(data['is_active'])
        if 'progress_percentage' in data:
            try:
                progress = float(data['progress_percentage'])
                if 0 <= progress <= 100:
                    learning_path.progress_percentage = progress
            except (ValueError, TypeError):
                pass
        
        db.session.commit()
        
        return jsonify({
            'message': 'Learning path updated successfully',
            'learning_path': learning_path.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@learning_path_bp.route('/learning-paths/<int:path_id>', methods=['DELETE'])
@token_required
def delete_learning_path(current_user, path_id):
    """Delete a learning path"""
    try:
        learning_path = LearningPath.query.filter(
            LearningPath.id == path_id,
            LearningPath.user_id == current_user.id
        ).first()
        
        if not learning_path:
            return jsonify({'error': 'Learning path not found'}), 404
        
        # Soft delete by setting is_active to False
        learning_path.is_active = False
        db.session.commit()
        
        return jsonify({
            'message': 'Learning path deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@learning_path_bp.route('/learning-paths/<int:path_id>/topics', methods=['POST'])
@token_required
def add_topic_to_path(current_user, path_id):
    """Add a new topic to a learning path"""
    try:
        learning_path = LearningPath.query.filter(
            LearningPath.id == path_id,
            LearningPath.user_id == current_user.id
        ).first()
        
        if not learning_path:
            return jsonify({'error': 'Learning path not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title'):
            return jsonify({'error': 'Topic title is required'}), 400
        
        # Get the next order index
        max_order = db.session.query(db.func.max(Topic.order_index)).filter(
            Topic.learning_path_id == path_id
        ).scalar() or 0
        
        # Create new topic
        topic = Topic(
            learning_path_id=path_id,
            title=data['title'].strip(),
            description=data.get('description', '').strip(),
            order_index=max_order + 1
        )
        
        db.session.add(topic)
        db.session.commit()
        
        return jsonify({
            'message': 'Topic added successfully',
            'topic': topic.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@learning_path_bp.route('/learning-paths/<int:path_id>/progress', methods=['GET'])
@token_required
def get_learning_path_progress(current_user, path_id):
    """Get detailed progress for a learning path"""
    try:
        learning_path = LearningPath.query.filter(
            LearningPath.id == path_id,
            LearningPath.user_id == current_user.id
        ).first()
        
        if not learning_path:
            return jsonify({'error': 'Learning path not found'}), 404
        
        # Get topics and calculate progress
        topics = Topic.query.filter(
            Topic.learning_path_id == path_id
        ).order_by(Topic.order_index).all()
        
        total_topics = len(topics)
        completed_topics = sum(1 for topic in topics if topic.is_completed)
        
        # Calculate resource progress
        total_resources = 0
        completed_resources = 0
        
        for topic in topics:
            topic_resources = len(topic.resources)
            topic_completed_resources = sum(1 for resource in topic.resources if resource.is_completed)
            total_resources += topic_resources
            completed_resources += topic_completed_resources
        
        # Calculate overall progress percentage
        if total_topics > 0:
            topic_progress = (completed_topics / total_topics) * 100
        else:
            topic_progress = 0
        
        if total_resources > 0:
            resource_progress = (completed_resources / total_resources) * 100
        else:
            resource_progress = 0
        
        # Average of topic and resource progress
        overall_progress = (topic_progress + resource_progress) / 2
        
        # Update learning path progress
        learning_path.progress_percentage = overall_progress
        db.session.commit()
        
        return jsonify({
            'learning_path_id': path_id,
            'overall_progress': overall_progress,
            'topic_progress': {
                'total': total_topics,
                'completed': completed_topics,
                'percentage': topic_progress
            },
            'resource_progress': {
                'total': total_resources,
                'completed': completed_resources,
                'percentage': resource_progress
            },
            'topics': [
                {
                    'id': topic.id,
                    'title': topic.title,
                    'is_completed': topic.is_completed,
                    'resources_count': len(topic.resources),
                    'completed_resources': sum(1 for r in topic.resources if r.is_completed)
                }
                for topic in topics
            ]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_path_bp.route('/subjects', methods=['GET'])
@token_required
def get_popular_subjects(current_user):
    """Get popular subjects from user's learning paths"""
    try:
        # Get subjects from user's learning paths
        subjects = db.session.query(
            LearningPath.subject,
            db.func.count(LearningPath.id).label('count')
        ).filter(
            LearningPath.user_id == current_user.id,
            LearningPath.is_active == True
        ).group_by(LearningPath.subject).order_by(
            db.func.count(LearningPath.id).desc()
        ).limit(20).all()
        
        # Also include some common subjects
        common_subjects = [
            'Programming', 'Mathematics', 'Science', 'Languages', 'History',
            'Art', 'Music', 'Business', 'Psychology', 'Philosophy',
            'Computer Science', 'Data Science', 'Web Development', 'Mobile Development'
        ]
        
        user_subjects = [subject[0] for subject in subjects]
        suggested_subjects = [s for s in common_subjects if s not in user_subjects]
        
        return jsonify({
            'user_subjects': [
                {'name': subject[0], 'count': subject[1]}
                for subject in subjects
            ],
            'suggested_subjects': suggested_subjects[:10]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

