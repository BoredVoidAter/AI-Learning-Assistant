from datetime import datetime, date, timedelta
from src.models.learning import db, User, QuizAttempt, LearningPath, Quiz, Resource, Note
from src.models.gamification import Achievement, UserAchievement, UserLevel, Badge, UserBadge, Leaderboard
from src.models.activity import UserActivity
import math

class GamificationService:
    
    @staticmethod
    def initialize_user_level(user_id):
        """Initialize level tracking for a new user"""
        existing_level = UserLevel.query.filter_by(user_id=user_id).first()
        if not existing_level:
            user_level = UserLevel(user_id=user_id)
            db.session.add(user_level)
            db.session.commit()
            return user_level
        return existing_level
    
    @staticmethod
    def award_points(user_id, points, category='general'):
        """Award points to a user and update their level"""
        user_level = UserLevel.query.filter_by(user_id=user_id).first()
        if not user_level:
            user_level = GamificationService.initialize_user_level(user_id)
        
        # Add points to appropriate category
        if category == 'learning':
            user_level.learning_points += points
        elif category == 'quiz':
            user_level.quiz_points += points
        elif category == 'achievement':
            user_level.achievement_points += points
        elif category == 'social':
            user_level.social_points += points
        
        user_level.total_points += points
        
        # Check for level up
        GamificationService._check_level_up(user_level)
        
        db.session.commit()
        return user_level
    
    @staticmethod
    def _check_level_up(user_level):
        """Check if user should level up and update accordingly"""
        points_for_next_level = GamificationService._calculate_points_for_level(user_level.current_level + 1)
        
        while user_level.total_points >= points_for_next_level:
            user_level.current_level += 1
            points_for_next_level = GamificationService._calculate_points_for_level(user_level.current_level + 1)
        
        user_level.points_to_next_level = points_for_next_level - user_level.total_points
    
    @staticmethod
    def _calculate_points_for_level(level):
        """Calculate total points needed to reach a specific level"""
        # Exponential growth: level^2 * 100
        return level * level * 100
    
    @staticmethod
    def update_learning_streak(user_id):
        """Update user's learning streak"""
        user_level = UserLevel.query.filter_by(user_id=user_id).first()
        if not user_level:
            user_level = GamificationService.initialize_user_level(user_id)
        
        today = date.today()
        
        if user_level.last_activity_date:
            days_diff = (today - user_level.last_activity_date).days
            
            if days_diff == 1:
                # Consecutive day - increment streak
                user_level.current_learning_streak += 1
            elif days_diff > 1:
                # Streak broken - reset
                user_level.current_learning_streak = 1
            # If days_diff == 0, same day activity, don't change streak
        else:
            # First activity
            user_level.current_learning_streak = 1
        
        # Update longest streak if current is longer
        if user_level.current_learning_streak > user_level.longest_learning_streak:
            user_level.longest_learning_streak = user_level.current_learning_streak
        
        user_level.last_activity_date = today
        db.session.commit()
        
        # Check for streak-based achievements
        GamificationService.check_achievements(user_id)
        
        return user_level
    
    @staticmethod
    def check_achievements(user_id):
        """Check and award achievements for a user"""
        user = User.query.get(user_id)
        if not user:
            return []
        
        # Get all active achievements
        achievements = Achievement.query.filter_by(is_active=True).all()
        newly_earned = []
        
        for achievement in achievements:
            # Check if user already has this achievement
            existing = UserAchievement.query.filter_by(
                user_id=user_id, 
                achievement_id=achievement.id
            ).first()
            
            if existing:
                continue
            
            # Check if user meets the achievement criteria
            if GamificationService._check_achievement_criteria(user_id, achievement):
                # Award the achievement
                user_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id
                )
                db.session.add(user_achievement)
                
                # Award points for the achievement
                GamificationService.award_points(user_id, achievement.points, 'achievement')
                
                newly_earned.append(achievement)
        
        db.session.commit()
        return newly_earned
    
    @staticmethod
    def _check_achievement_criteria(user_id, achievement):
        """Check if user meets specific achievement criteria"""
        condition_type = achievement.condition_type
        condition_target = achievement.condition_target
        condition_resource = achievement.condition_resource
        
        if condition_type == 'count':
            if condition_resource == 'learning_paths_completed':
                count = db.session.query(UserActivity).filter_by(
                    user_id=user_id,
                    activity_type='learning_path_completed'
                ).count()
            elif condition_resource == 'quizzes_completed':
                count = QuizAttempt.query.filter_by(user_id=user_id).count()
            elif condition_resource == 'resources_viewed':
                count = db.session.query(UserActivity).filter_by(
                    user_id=user_id,
                    activity_type='resource_viewed'
                ).count()
            elif condition_resource == 'notes_created':
                count = Note.query.filter_by(user_id=user_id).count()
            else:
                return False
            
            return count >= condition_target
        
        elif condition_type == 'streak':
            user_level = UserLevel.query.filter_by(user_id=user_id).first()
            if not user_level:
                return False
            
            if condition_resource == 'learning_streak':
                return user_level.current_learning_streak >= condition_target
        
        elif condition_type == 'score':
            if condition_resource == 'average_quiz_score':
                attempts = QuizAttempt.query.filter_by(user_id=user_id).all()
                if not attempts:
                    return False
                
                avg_score = sum(attempt.percentage for attempt in attempts) / len(attempts)
                return avg_score >= condition_target
        
        elif condition_type == 'time':
            user_level = UserLevel.query.filter_by(user_id=user_id).first()
            if not user_level:
                return False
            
            if condition_resource == 'total_points':
                return user_level.total_points >= condition_target
        
        return False
    
    @staticmethod
    def check_badges(user_id):
        """Check and award badges for a user"""
        badges = Badge.query.filter_by(is_active=True).all()
        newly_earned = []
        
        for badge in badges:
            # Check if user already has this badge
            existing = UserBadge.query.filter_by(
                user_id=user_id,
                badge_id=badge.id
            ).first()
            
            if existing:
                continue
            
            # Check badge criteria (similar to achievements but simpler)
            if GamificationService._check_badge_criteria(user_id, badge):
                user_badge = UserBadge(
                    user_id=user_id,
                    badge_id=badge.id
                )
                db.session.add(user_badge)
                newly_earned.append(badge)
        
        db.session.commit()
        return newly_earned
    
    @staticmethod
    def _check_badge_criteria(user_id, badge):
        """Check if user meets badge criteria"""
        condition_type = badge.condition_type
        condition_value = badge.condition_value
        
        if condition_type == 'level':
            user_level = UserLevel.query.filter_by(user_id=user_id).first()
            return user_level and user_level.current_level >= condition_value
        
        elif condition_type == 'achievements':
            achievement_count = UserAchievement.query.filter_by(user_id=user_id).count()
            return achievement_count >= condition_value
        
        elif condition_type == 'points':
            user_level = UserLevel.query.filter_by(user_id=user_id).first()
            return user_level and user_level.total_points >= condition_value
        
        return False
    
    @staticmethod
    def update_leaderboards():
        """Update all leaderboards (should be run periodically)"""
        today = date.today()
        
        # Weekly leaderboard (Monday to Sunday)
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Monthly leaderboard
        month_start = today.replace(day=1)
        if today.month == 12:
            month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        # Update weekly leaderboards
        GamificationService._update_leaderboard_category('weekly', 'points', week_start, week_end)
        GamificationService._update_leaderboard_category('weekly', 'quizzes', week_start, week_end)
        
        # Update monthly leaderboards
        GamificationService._update_leaderboard_category('monthly', 'points', month_start, month_end)
        GamificationService._update_leaderboard_category('monthly', 'quizzes', month_start, month_end)
        
        # Update all-time leaderboards
        GamificationService._update_leaderboard_category('all_time', 'points', None, None)
        GamificationService._update_leaderboard_category('all_time', 'streak', None, None)
    
    @staticmethod
    def _update_leaderboard_category(leaderboard_type, category, period_start, period_end):
        """Update a specific leaderboard category"""
        if leaderboard_type == 'all_time':
            if category == 'points':
                # All-time points leaderboard
                users = db.session.query(UserLevel).order_by(UserLevel.total_points.desc()).all()
            elif category == 'streak':
                # All-time streak leaderboard
                users = db.session.query(UserLevel).order_by(UserLevel.longest_learning_streak.desc()).all()
            else:
                return
            
            period_start = date(2024, 1, 1)  # Project start date
            period_end = date.today()
        else:
            # For weekly/monthly, we need to calculate scores for the period
            if category == 'points':
                # Points earned in the period (simplified - using total points for now)
                users = db.session.query(UserLevel).order_by(UserLevel.total_points.desc()).all()
            elif category == 'quizzes':
                # Quizzes completed in the period
                users = db.session.query(UserLevel).order_by(UserLevel.quiz_points.desc()).all()
            else:
                return
        
        # Clear existing leaderboard entries for this period
        Leaderboard.query.filter_by(
            leaderboard_type=leaderboard_type,
            category=category,
            period_start=period_start
        ).delete()
        
        # Create new leaderboard entries
        for rank, user_level in enumerate(users[:100], 1):  # Top 100
            if category == 'points':
                score = user_level.total_points
            elif category == 'quizzes':
                score = user_level.quiz_points
            elif category == 'streak':
                score = user_level.longest_learning_streak
            else:
                continue
            
            leaderboard_entry = Leaderboard(
                user_id=user_level.user_id,
                leaderboard_type=leaderboard_type,
                category=category,
                score=score,
                rank=rank,
                period_start=period_start,
                period_end=period_end
            )
            db.session.add(leaderboard_entry)
        
        db.session.commit()
    
    @staticmethod
    def get_user_stats(user_id):
        """Get comprehensive gamification stats for a user"""
        user_level = UserLevel.query.filter_by(user_id=user_id).first()
        if not user_level:
            user_level = GamificationService.initialize_user_level(user_id)
        
        # Get achievements
        achievements = db.session.query(UserAchievement, Achievement).join(
            Achievement
        ).filter(UserAchievement.user_id == user_id).all()
        
        # Get badges
        badges = db.session.query(UserBadge, Badge).join(
            Badge
        ).filter(UserBadge.user_id == user_id).all()
        
        # Get leaderboard positions
        leaderboard_positions = {}
        for lb_type in ['weekly', 'monthly', 'all_time']:
            for category in ['points', 'quizzes', 'streak']:
                entry = Leaderboard.query.filter_by(
                    user_id=user_id,
                    leaderboard_type=lb_type,
                    category=category
                ).first()
                if entry:
                    leaderboard_positions[f"{lb_type}_{category}"] = entry.rank
        
        return {
            'level': user_level.to_dict(),
            'achievements': [
                {
                    'user_achievement': ua.to_dict(),
                    'achievement': achievement.to_dict()
                }
                for ua, achievement in achievements
            ],
            'badges': [
                {
                    'user_badge': ub.to_dict(),
                    'badge': badge.to_dict()
                }
                for ub, badge in badges
            ],
            'leaderboard_positions': leaderboard_positions
        }

