from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash
from src.models.user import User
from src.database import db
from src.utils.auth_utils import token_required
import re

auth_bp = Blueprint('auth', __name__)



def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    return True, "Password is valid"

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        # Validate input
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters long'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=data.get('first_name', '').strip(),
            last_name=data.get('last_name', '').strip(),
            learning_style=data.get('learning_style', 'visual'),
            preferred_difficulty=data.get('preferred_difficulty', 'intermediate'),
            daily_goal_minutes=data.get('daily_goal_minutes', 30)
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = user.generate_token()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'token': token
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return token"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Generate token
        token = user.generate_token()
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'token': token
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get current user's profile"""
    try:
        return jsonify({
            'user': current_user.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update current user's profile"""
    try:
        data = request.get_json()
        
        # Update allowed fields
        if 'first_name' in data:
            current_user.first_name = data['first_name'].strip()
        if 'last_name' in data:
            current_user.last_name = data['last_name'].strip()
        if 'learning_style' in data:
            if data['learning_style'] in ['visual', 'auditory', 'kinesthetic', 'reading']:
                current_user.learning_style = data['learning_style']
        if 'preferred_difficulty' in data:
            if data['preferred_difficulty'] in ['beginner', 'intermediate', 'advanced']:
                current_user.preferred_difficulty = data['preferred_difficulty']
        if 'daily_goal_minutes' in data:
            try:
                minutes = int(data['daily_goal_minutes'])
                if 5 <= minutes <= 480:  # 5 minutes to 8 hours
                    current_user.daily_goal_minutes = minutes
            except (ValueError, TypeError):
                pass
        
        # Update email if provided
        if 'email' in data:
            new_email = data['email'].strip().lower()
            if validate_email(new_email):
                # Check if email is already taken by another user
                existing_user = User.query.filter(
                    User.email == new_email,
                    User.id != current_user.id
                ).first()
                if not existing_user:
                    current_user.email = new_email
                else:
                    return jsonify({'error': 'Email already taken'}), 400
            else:
                return jsonify({'error': 'Invalid email format'}), 400
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': current_user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """Change user's password"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        current_password = data['current_password']
        new_password = data['new_password']
        
        # Verify current password
        if not current_user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Validate new password
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Update password
        current_user.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            'message': 'Password changed successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Verify if a token is valid"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'valid': False, 'error': 'Token is required'}), 400
        
        user = User.verify_token(token)
        if user and user.is_active:
            return jsonify({
                'valid': True,
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({
                'valid': False,
                'error': 'Invalid or expired token'
            }), 401
    
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': str(e)
        }), 500

