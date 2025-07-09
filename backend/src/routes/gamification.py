from flask import Blueprint, request, jsonify, current_app
from src.models.user import User
from src.database import db
from src.models.gamification import Achievement, UserAchievement, UserLevel, Badge, UserBadge, Leaderboard
from src.services.gamification_service import GamificationService
from src.utils.auth_utils import token_required
from datetime import datetime, date, timedelta

gamification_bp = Blueprint('gamification', __name__)

@gamification_bp.route('/gamification/profile', methods=['GET'])
@token_required
def get_user_gamification_profile(current_user):
    """Get user's complete gamification profile"""
    try:
        current_user_id = current_user.id
        stats = GamificationService.get_user_stats(current_user_id)
        
        return jsonify({
            'profile': stats
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting gamification profile: {str(e)}")
        return jsonify({'error': 'Failed to get gamification profile'}), 500

@gamification_bp.route('/gamification/achievements', methods=['GET'])
@token_required
def get_achievements(current_user):
    """Get all achievements with user progress"""
    try:
        current_user_id = current_user.id
        
        # Get all active achievements
        achievements = Achievement.query.filter_by(is_active=True).all()
        
        # Get user's earned achievements
        user_achievements = {
            ua.achievement_id: ua for ua in 
            UserAchievement.query.filter_by(user_id=current_user_id).all()
        }
        
        achievement_list = []
        for achievement in achievements:
            achievement_dict = achievement.to_dict()
            user_achievement = user_achievements.get(achievement.id)
            
            achievement_dict['earned'] = user_achievement is not None
            achievement_dict['earned_at'] = user_achievement.earned_at.isoformat() if user_achievement else None
            achievement_dict['progress'] = user_achievement.progress_value if user_achievement else 0
            
            # Calculate current progress for unearned achievements
            if not achievement_dict['earned']:
                progress = GamificationService._calculate_achievement_progress(current_user_id, achievement)
                achievement_dict['progress'] = progress
                achievement_dict['progress_percentage'] = min(100, (progress / achievement.condition_target) * 100)
            else:
                achievement_dict['progress_percentage'] = 100
            
            achievement_list.append(achievement_dict)
        
        # Sort by earned status and then by category
        achievement_list.sort(key=lambda x: (not x['earned'], x['category'], x['name']))
        
        return jsonify({
            'achievements': achievement_list
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting achievements: {str(e)}")
        return jsonify({'error': 'Failed to get achievements'}), 500

@gamification_bp.route('/gamification/badges', methods=['GET'])
@token_required
def get_badges(current_user):
    """Get all badges with user status"""
    try:
        current_user_id = current_user.id
        
        # Get all active badges
        badges = Badge.query.filter_by(is_active=True).all()
        
        # Get user's earned badges
        user_badges = {
            ub.badge_id: ub for ub in 
            UserBadge.query.filter_by(user_id=current_user_id).all()
        }
        
        badge_list = []
        for badge in badges:
            badge_dict = badge.to_dict()
            user_badge = user_badges.get(badge.id)
            
            badge_dict['earned'] = user_badge is not None
            badge_dict['earned_at'] = user_badge.earned_at.isoformat() if user_badge else None
            
            badge_list.append(badge_dict)
        
        # Sort by earned status and then by category
        badge_list.sort(key=lambda x: (not x['earned'], x['category'], x['name']))
        
        return jsonify({
            'badges': badge_list
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting badges: {str(e)}")
        return jsonify({'error': 'Failed to get badges'}), 500

@gamification_bp.route('/gamification/leaderboard/<leaderboard_type>/<category>', methods=['GET'])
@token_required
def get_leaderboard(current_user, leaderboard_type, category):
    """Get leaderboard for specific type and category"""
    try:
        # Validate parameters
        valid_types = ['weekly', 'monthly', 'all_time']
        valid_categories = ['points', 'quizzes', 'streak']
        
        if leaderboard_type not in valid_types:
            return jsonify({'error': 'Invalid leaderboard type'}), 400
        
        if category not in valid_categories:
            return jsonify({'error': 'Invalid category'}), 400
        
        current_user_id = current_user.id
        limit = request.args.get('limit', 50, type=int)
        
        # Get current period dates
        today = date.today()
        if leaderboard_type == 'weekly':
            period_start = today - timedelta(days=today.weekday())
        elif leaderboard_type == 'monthly':
            period_start = today.replace(day=1)
        else:  # all_time
            period_start = date(2024, 1, 1)
        
        # Get leaderboard entries
        leaderboard_entries = Leaderboard.query.filter_by(
            leaderboard_type=leaderboard_type,
            category=category,
            period_start=period_start
        ).order_by(Leaderboard.rank.asc()).limit(limit).all()
        
        # Get current user's position
        user_position = Leaderboard.query.filter_by(
            user_id=current_user_id,
            leaderboard_type=leaderboard_type,
            category=category,
            period_start=period_start
        ).first()
        
        return jsonify({
            'leaderboard': [entry.to_dict() for entry in leaderboard_entries],
            'user_position': user_position.to_dict() if user_position else None,
            'leaderboard_type': leaderboard_type,
            'category': category,
            'period_start': period_start.isoformat(),
            'total_entries': len(leaderboard_entries)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting leaderboard: {str(e)}")
        return jsonify({'error': 'Failed to get leaderboard'}), 500

@gamification_bp.route('/gamification/level-progress', methods=['GET'])
@token_required
def get_level_progress(current_user):
    """Get detailed level progress information"""
    try:
        current_user_id = current_user.id
        user_level = UserLevel.query.filter_by(user_id=current_user_id).first()
        
        if not user_level:
            user_level = GamificationService.initialize_user_level(current_user_id)
        
        # Calculate progress to next level
        current_level_points = GamificationService._calculate_points_for_level(user_level.current_level)
        next_level_points = GamificationService._calculate_points_for_level(user_level.current_level + 1)
        progress_in_level = user_level.total_points - current_level_points
        points_needed_for_level = next_level_points - current_level_points
        progress_percentage = (progress_in_level / points_needed_for_level) * 100
        
        return jsonify({
            'level_info': user_level.to_dict(),
            'progress': {
                'current_level_points': current_level_points,
                'next_level_points': next_level_points,
                'progress_in_level': progress_in_level,
                'points_needed_for_level': points_needed_for_level,
                'progress_percentage': progress_percentage
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting level progress: {str(e)}")
        return jsonify({'error': 'Failed to get level progress'}), 500

@gamification_bp.route('/gamification/recent-achievements', methods=['GET'])
@token_required
def get_recent_achievements(current_user):
    """Get user's recent achievements"""
    try:
        current_user_id = current_user.id
        limit = request.args.get('limit', 10, type=int)
        
        recent_achievements = db.session.query(UserAchievement, Achievement).join(
            Achievement
        ).filter(
            UserAchievement.user_id == current_user_id
        ).order_by(
            UserAchievement.earned_at.desc()
        ).limit(limit).all()
        
        achievement_list = []
        for user_achievement, achievement in recent_achievements:
            achievement_dict = achievement.to_dict()
            achievement_dict['earned_at'] = user_achievement.earned_at.isoformat()
            achievement_list.append(achievement_dict)
        
        return jsonify({
            'recent_achievements': achievement_list
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting recent achievements: {str(e)}")
        return jsonify({'error': 'Failed to get recent achievements'}), 500

@gamification_bp.route('/gamification/stats', methods=['GET'])
@token_required
def get_gamification_stats(current_user):
    """Get overall gamification statistics"""
    try:
        current_user_id = current_user.id
        
        # Get user level
        user_level = UserLevel.query.filter_by(user_id=current_user_id).first()
        if not user_level:
            user_level = GamificationService.initialize_user_level(current_user_id)
        
        # Count achievements and badges
        achievements_count = UserAchievement.query.filter_by(user_id=current_user_id).count()
        total_achievements = Achievement.query.filter_by(is_active=True).count()
        
        badges_count = UserBadge.query.filter_by(user_id=current_user_id).count()
        total_badges = Badge.query.filter_by(is_active=True).count()
        
        # Get leaderboard positions
        leaderboard_positions = {}
        for lb_type in ['weekly', 'monthly', 'all_time']:
            for category in ['points', 'quizzes', 'streak']:
                today = date.today()
                if lb_type == 'weekly':
                    period_start = today - timedelta(days=today.weekday())
                elif lb_type == 'monthly':
                    period_start = today.replace(day=1)
                else:
                    period_start = date(2024, 1, 1)
                
                entry = Leaderboard.query.filter_by(
                    user_id=current_user_id,
                    leaderboard_type=lb_type,
                    category=category,
                    period_start=period_start
                ).first()
                
                if entry:
                    leaderboard_positions[f"{lb_type}_{category}"] = entry.rank
        
        return jsonify({
            'stats': {
                'level': user_level.current_level,
                'total_points': user_level.total_points,
                'achievements_earned': achievements_count,
                'total_achievements': total_achievements,
                'achievement_completion_rate': (achievements_count / total_achievements * 100) if total_achievements > 0 else 0,
                'badges_earned': badges_count,
                'total_badges': total_badges,
                'badge_completion_rate': (badges_count / total_badges * 100) if total_badges > 0 else 0,
                'current_streak': user_level.current_learning_streak,
                'longest_streak': user_level.longest_learning_streak,
                'leaderboard_positions': leaderboard_positions
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting gamification stats: {str(e)}")
        return jsonify({'error': 'Failed to get gamification stats'}), 500

# Helper function for calculating achievement progress
def _calculate_achievement_progress(user_id, achievement):
    """Calculate current progress towards an achievement"""
    condition_type = achievement.condition_type
    condition_resource = achievement.condition_resource
    
    if condition_type == 'count':
        if condition_resource == 'learning_paths_completed':
            from src.models.activity import UserActivity
            return db.session.query(UserActivity).filter_by(
                user_id=user_id,
                activity_type='learning_path_completed'
            ).count()
        elif condition_resource == 'quizzes_completed':
            from src.models.learning import QuizAttempt
            return QuizAttempt.query.filter_by(user_id=user_id).count()
        elif condition_resource == 'resources_viewed':
            from src.models.activity import UserActivity
            return db.session.query(UserActivity).filter_by(
                user_id=user_id,
                activity_type='resource_viewed'
            ).count()
        elif condition_resource == 'notes_created':
            from src.models.learning import Note
            return Note.query.filter_by(user_id=user_id).count()
    
    elif condition_type == 'streak':
        user_level = UserLevel.query.filter_by(user_id=user_id).first()
        if user_level and condition_resource == 'learning_streak':
            return user_level.current_learning_streak
    
    elif condition_type == 'score':
        if condition_resource == 'average_quiz_score':
            from src.models.learning import QuizAttempt
            attempts = QuizAttempt.query.filter_by(user_id=user_id).all()
            if attempts:
                return sum(attempt.percentage for attempt in attempts) / len(attempts)
    
    elif condition_type == 'time':
        user_level = UserLevel.query.filter_by(user_id=user_id).first()
        if user_level and condition_resource == 'total_points':
            return user_level.total_points
    
    return 0

# Add the helper function to GamificationService
GamificationService._calculate_achievement_progress = staticmethod(_calculate_achievement_progress)

