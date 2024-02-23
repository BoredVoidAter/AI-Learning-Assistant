from flask import Blueprint, request, jsonify
from src.models.learning import db, Resource, Topic, LearningPath
from src.routes.auth import token_required
from sqlalchemy import or_

resource_bp = Blueprint("resource", __name__)

@resource_bp.route("/resources", methods=["GET"])
@token_required
def get_resources(current_user):
    """Get all resources for the current user with optional filtering and pagination"""
    try:
        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        search = request.args.get("search", "")
        topic_id = request.args.get("topic_id", type=int)
        resource_type = request.args.get("resource_type", "")
        difficulty = request.args.get("difficulty_level", "")
        search_query = request.args.get("search_query", "")
        
        # Build query - only resources from user's learning paths
        query = db.session.query(Resource).join(Topic).join(LearningPath).filter(
            LearningPath.user_id == current_user.id
        )
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    Resource.title.ilike(f"%{search}%"),
                    Resource.description.ilike(f"%{search}%")
                )
            )
        if topic_id:
            query = query.filter(Resource.topic_id == topic_id)
        if resource_type:
            query = query.filter(Resource.resource_type == resource_type)
        if difficulty:
            query = query.filter(Resource.difficulty_level == difficulty)
        if search_query:
            query = query.filter(or_(
                Resource.title.ilike(f"%{search_query}%"),
                Resource.description.ilike(f"%{search_query}%"),
                Resource.content.ilike(f"%{search_query}%")
            ))
        # Order by creation date (newest first)
        query = query.order_by(Resource.created_at.desc())
        
        # Paginate results
        resources = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        resource_list = []
        for resource in resources.items:
            resource_data = resource.to_dict()
            # Add topic and learning path info
            resource_data["topic_title"] = resource.topic.title
            resource_data["learning_path_title"] = resource.topic.learning_path.title
            resource_list.append(resource_data)
        
        return jsonify({
            "resources": resource_list,
            "total": resources.total,
            "pages": resources.pages,
            "current_page": page,
            "per_page": per_page
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@resource_bp.route("/resources", methods=["POST"])
@token_required
def create_resource(current_user):
    """Create a new resource"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["topic_id", "title", "resource_type"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400
        
        # Verify topic belongs to user
        topic = db.session.query(Topic).join(LearningPath).filter(
            Topic.id == data["topic_id"],
            LearningPath.user_id == current_user.id
        ).first()
        
        if not topic:
            return jsonify({"error": "Topic not found or access denied"}), 404
        
        # Validate resource type
        resource_type = data["resource_type"]
        if resource_type not in ["video", "article", "book", "course", "exercise", "other"]:
            return jsonify({"error": "Invalid resource type"}), 400
        
        # Validate difficulty level
        difficulty = data.get("difficulty_level", "intermediate")
        if difficulty not in ["beginner", "intermediate", "advanced"]:
            return jsonify({"error": "Invalid difficulty level"}), 400
        
        # Create new resource
        resource = Resource(
            topic_id=data["topic_id"],
            title=data["title"].strip(),
            description=data.get("description", "").strip(),
            resource_type=resource_type,
            url=data.get("url"),
            content=data.get("content"),
            duration_minutes=data.get("duration_minutes"),
            difficulty_level=difficulty
        )
        
        db.session.add(resource)
        db.session.commit()
        
        return jsonify({
            "message": "Resource created successfully",
            "resource": resource.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@resource_bp.route("/resources/<int:resource_id>", methods=["GET"])
@token_required
def get_resource(current_user, resource_id):
    """Get a specific resource"""
    try:
        # Verify resource belongs to user
        resource = db.session.query(Resource).join(Topic).join(LearningPath).filter(
            Resource.id == resource_id,
            LearningPath.user_id == current_user.id
        ).first()
        
        if not resource:
            return jsonify({"error": "Resource not found or access denied"}), 404
        
        return jsonify({
            "resource": resource.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@resource_bp.route("/resources/<int:resource_id>", methods=["PUT"])
@token_required
def update_resource(current_user, resource_id):
    """Update a specific resource"""
    try:
        resource = db.session.query(Resource).join(Topic).join(LearningPath).filter(
            Resource.id == resource_id,
            LearningPath.user_id == current_user.id
        ).first()
        
        if not resource:
            return jsonify({"error": "Resource not found or access denied"}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if "title" in data:
            resource.title = data["title"].strip()
        if "description" in data:
            resource.description = data["description"].strip()
        if "resource_type" in data:
            if data["resource_type"] in ["video", "article", "book", "course", "exercise", "other"]:
                resource.resource_type = data["resource_type"]
        if "url" in data:
            resource.url = data["url"]
        if "content" in data:
            resource.content = data["content"]
        if "duration_minutes" in data:
            try:
                minutes = int(data["duration_minutes"])
                if minutes >= 0:
                    resource.duration_minutes = minutes
            except (ValueError, TypeError):
                pass
        if "difficulty_level" in data:
            if data["difficulty_level"] in ["beginner", "intermediate", "advanced"]:
                resource.difficulty_level = data["difficulty_level"]
        if "is_completed" in data:
            resource.is_completed = bool(data["is_completed"])
        
        db.session.commit()
        
        return jsonify({
            "message": "Resource updated successfully",
            "resource": resource.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@resource_bp.route("/resources/<int:resource_id>", methods=["DELETE"])
@token_required
def delete_resource(current_user, resource_id):
    """Delete a specific resource"""
    try:
        resource = db.session.query(Resource).join(Topic).join(LearningPath).filter(
            Resource.id == resource_id,
            LearningPath.user_id == current_user.id
        ).first()
        
        if not resource:
            return jsonify({"error": "Resource not found or access denied"}), 404
        
        db.session.delete(resource)
        db.session.commit()
        
        return jsonify({"message": "Resource deleted successfully"}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

