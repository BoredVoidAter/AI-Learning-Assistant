from flask import Blueprint, request, jsonify
from src.models.learning import db, Note, User, Resource
from src.routes.auth import token_required
from sqlalchemy import or_

note_bp = Blueprint("note", __name__)

@note_bp.route("/notes", methods=["GET"])
@token_required
def get_notes(current_user):
    """Get all notes for the current user with optional filtering and pagination"""
    try:
        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        search = request.args.get("search", "")
        resource_id = request.args.get("resource_id", type=int)
        is_favorite = request.args.get("is_favorite", type=bool)
        tag = request.args.get("tag", "")
        search_query = request.args.get("search_query", "")
        
        # Build query
        query = Note.query.filter(Note.user_id == current_user.id)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    Note.title.ilike(f"%{search}%"),
                    Note.content.ilike(f"%{search}%")
                )
            )
        if resource_id:
            query = query.filter(Note.resource_id == resource_id)
        if is_favorite is not None:
            query = query.filter(Note.is_favorite == is_favorite)
        if tag:
            query = query.filter(Note.tags.contains([tag]))
        if search_query:
            query = query.filter(or_(
                Note.title.ilike(f"%{search_query}%"),
                Note.content.ilike(f"%{search_query}%")
            ))
        # Order by creation date (newest first)
        query = query.order_by(Note.created_at.desc())
        
        # Paginate results
        notes = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        note_list = []
        for note in notes.items:
            note_data = note.to_dict()
            if note.resource:
                note_data["resource_title"] = note.resource.title
            note_list.append(note_data)
        
        return jsonify({
            "notes": note_list,
            "total": notes.total,
            "pages": notes.pages,
            "current_page": page,
            "per_page": per_page
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@note_bp.route("/notes", methods=["POST"])
@token_required
def create_note(current_user):
    """Create a new note"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["title", "content"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400
        
        resource_id = data.get("resource_id")
        if resource_id:
            # Verify resource exists and belongs to user (indirectly via learning path)
            resource = db.session.query(Resource).join(Topic).join(LearningPath).filter(
                Resource.id == resource_id,
                LearningPath.user_id == current_user.id
            ).first()
            if not resource:
                return jsonify({"error": "Resource not found or access denied"}), 404
        
        # Create new note
        note = Note(
            user_id=current_user.id,
            resource_id=resource_id,
            title=data["title"].strip(),
            content=data["content"].strip(),
            tags=data.get("tags"),
            is_favorite=data.get("is_favorite", False)
        )
        
        db.session.add(note)
        db.session.commit()
        
        return jsonify({
            "message": "Note created successfully",
            "note": note.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@note_bp.route("/notes/<int:note_id>", methods=["GET"])
@token_required
def get_note(current_user, note_id):
    """Get a specific note"""
    try:
        note = Note.query.filter(
            Note.id == note_id,
            Note.user_id == current_user.id
        ).first()
        
        if not note:
            return jsonify({"error": "Note not found"}), 404
        
        note_data = note.to_dict()
        if note.resource:
            note_data["resource_title"] = note.resource.title
        
        return jsonify({
            "note": note_data
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@note_bp.route("/notes/<int:note_id>", methods=["PUT"])
@token_required
def update_note(current_user, note_id):
    """Update a specific note"""
    try:
        note = Note.query.filter(
            Note.id == note_id,
            Note.user_id == current_user.id
        ).first()
        
        if not note:
            return jsonify({"error": "Note not found"}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if "title" in data:
            note.title = data["title"].strip()
        if "content" in data:
            note.content = data["content"].strip()
        if "tags" in data:
            note.tags = data["tags"]
        if "is_favorite" in data:
            note.is_favorite = bool(data["is_favorite"])
        
        db.session.commit()
        
        return jsonify({
            "message": "Note updated successfully",
            "note": note.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@note_bp.route("/notes/<int:note_id>", methods=["DELETE"])
@token_required
def delete_note(current_user, note_id):
    """Delete a specific note"""
    try:
        note = Note.query.filter(
            Note.id == note_id,
            Note.user_id == current_user.id
        ).first()
        
        if not note:
            return jsonify({"error": "Note not found"}), 404
        
        db.session.delete(note)
        db.session.commit()
        
        return jsonify({"message": "Note deleted successfully"}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

