from flask import Blueprint, request, jsonify
from src.models.learning import db, User, LearningPath, Topic, QuizAttempt, Resource
from src.routes.auth import token_required
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
import calendar

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard', methods=['GET'])
@token_required
def get_dashboard_data(current_user):
    """Get comprehensive dashboard data for the user"""
    try:
        # Time range for analytics (default: last 30 days)
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Basic statistics
        total_learning_paths = LearningPath.query.filter(
            LearningPath.user_id == current_user.id,
            LearningPath.is_active == True
        ).count()
        
        completed_learning_paths = LearningPath.query.filter(
            LearningPath.user_id == current_user.id,
            LearningPath.is_active == True,
            LearningPath.progress_percentage >= 100
        ).count()
        
        total_quizzes_taken = QuizAttempt.query.filter(
            QuizAttempt.user_id == current_user.id,
            QuizAttempt.completed_at.isnot(None)
        ).count()
        
        # Recent quiz attempts for average score
        recent_quiz_attempts = QuizAttempt.query.filter(
            QuizAttempt.user_id == current_user.id,
            QuizAttempt.completed_at.isnot(None),
            QuizAttempt.completed_at >= start_date
        ).all()
        
        average_quiz_score = 0
        if recent_quiz_attempts:
            total_score = sum(attempt.percentage for attempt in recent_quiz_attempts)
            average_quiz_score = total_score / len(recent_quiz_attempts)
        
        # Learning streak (consecutive days with activity)
        learning_streak = calculate_learning_streak(current_user.id)
        
        # Study time estimation (based on completed resources)
        total_study_time = db.session.query(
            func.sum(Resource.duration_minutes)
        ).join(Topic).join(LearningPath).filter(
            LearningPath.user_id == current_user.id,
            Resource.is_completed == True,
            Resource.duration_minutes.isnot(None)
        ).scalar() or 0
        
        # Progress by subject
        subject_progress = db.session.query(
            LearningPath.subject,
            func.avg(LearningPath.progress_percentage).label('avg_progress'),
            func.count(LearningPath.id).label('count')
        ).filter(
            LearningPath.user_id == current_user.id,
            LearningPath.is_active == True
        ).group_by(LearningPath.subject).all()
        
        # Recent activity (last 7 days)
        recent_activity = get_recent_activity(current_user.id, 7)
        
        # Quiz performance trends
        quiz_trends = get_quiz_performance_trends(current_user.id, days)
        
        # Learning goals progress
        daily_goal_progress = calculate_daily_goal_progress(current_user, days)
        
        return jsonify({
            'overview': {
                'total_learning_paths': total_learning_paths,
                'completed_learning_paths': completed_learning_paths,
                'completion_rate': (completed_learning_paths / total_learning_paths * 100) if total_learning_paths > 0 else 0,
                'total_quizzes_taken': total_quizzes_taken,
                'average_quiz_score': round(average_quiz_score, 1),
                'learning_streak_days': learning_streak,
                'total_study_time_minutes': total_study_time,
                'total_study_time_hours': round(total_study_time / 60, 1)
            },
            'subject_progress': [
                {
                    'subject': item.subject,
                    'average_progress': round(item.avg_progress, 1),
                    'learning_paths_count': item.count
                }
                for item in subject_progress
            ],
            'recent_activity': recent_activity,
            'quiz_performance_trends': quiz_trends,
            'daily_goal_progress': daily_goal_progress
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/learning-progress', methods=['GET'])
@token_required
def get_learning_progress(current_user):
    """Get detailed learning progress analytics"""
    try:
        # Get all learning paths with detailed progress
        learning_paths = LearningPath.query.filter(
            LearningPath.user_id == current_user.id,
            LearningPath.is_active == True
        ).all()
        
        progress_data = []
        for path in learning_paths:
            # Get topics progress
            topics = Topic.query.filter(
                Topic.learning_path_id == path.id
            ).all()
            
            total_topics = len(topics)
            completed_topics = sum(1 for topic in topics if topic.is_completed)
            
            # Get resources progress
            total_resources = 0
            completed_resources = 0
            for topic in topics:
                topic_resources = len(topic.resources)
                topic_completed = sum(1 for resource in topic.resources if resource.is_completed)
                total_resources += topic_resources
                completed_resources += topic_completed
            
            # Calculate time spent
            time_spent = db.session.query(
                func.sum(Resource.duration_minutes)
            ).join(Topic).filter(
                Topic.learning_path_id == path.id,
                Resource.is_completed == True,
                Resource.duration_minutes.isnot(None)
            ).scalar() or 0
            
            progress_data.append({
                'learning_path': path.to_dict(),
                'topics_progress': {
                    'total': total_topics,
                    'completed': completed_topics,
                    'percentage': (completed_topics / total_topics * 100) if total_topics > 0 else 0
                },
                'resources_progress': {
                    'total': total_resources,
                    'completed': completed_resources,
                    'percentage': (completed_resources / total_resources * 100) if total_resources > 0 else 0
                },
                'time_spent_minutes': time_spent,
                'time_spent_hours': round(time_spent / 60, 1)
            })
        
        return jsonify({
            'learning_progress': progress_data
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/quiz-analytics', methods=['GET'])
@token_required
def get_quiz_analytics(current_user):
    """Get detailed quiz performance analytics"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all quiz attempts in the time range
        quiz_attempts = QuizAttempt.query.filter(
            QuizAttempt.user_id == current_user.id,
            QuizAttempt.completed_at.isnot(None),
            QuizAttempt.completed_at >= start_date
        ).order_by(QuizAttempt.completed_at.desc()).all()
        
        if not quiz_attempts:
            return jsonify({
                'total_attempts': 0,
                'average_score': 0,
                'best_score': 0,
                'improvement_trend': 0,
                'performance_by_difficulty': [],
                'performance_by_subject': [],
                'recent_attempts': []
            }), 200
        
        # Basic statistics
        total_attempts = len(quiz_attempts)
        average_score = sum(attempt.percentage for attempt in quiz_attempts) / total_attempts
        best_score = max(attempt.percentage for attempt in quiz_attempts)
        
        # Calculate improvement trend (compare first half vs second half)
        mid_point = total_attempts // 2
        if mid_point > 0:
            first_half_avg = sum(attempt.percentage for attempt in quiz_attempts[mid_point:]) / (total_attempts - mid_point)
            second_half_avg = sum(attempt.percentage for attempt in quiz_attempts[:mid_point]) / mid_point
            improvement_trend = second_half_avg - first_half_avg
        else:
            improvement_trend = 0
        
        # Performance by difficulty
        difficulty_performance = {}
        for attempt in quiz_attempts:
            quiz = attempt.quiz
            difficulty = quiz.difficulty_level
            if difficulty not in difficulty_performance:
                difficulty_performance[difficulty] = {'scores': [], 'count': 0}
            difficulty_performance[difficulty]['scores'].append(attempt.percentage)
            difficulty_performance[difficulty]['count'] += 1
        
        performance_by_difficulty = [
            {
                'difficulty': difficulty,
                'average_score': sum(data['scores']) / len(data['scores']),
                'attempts_count': data['count'],
                'best_score': max(data['scores'])
            }
            for difficulty, data in difficulty_performance.items()
        ]
        
        # Performance by subject
        subject_performance = {}
        for attempt in quiz_attempts:
            subject = attempt.quiz.topic.learning_path.subject
            if subject not in subject_performance:
                subject_performance[subject] = {'scores': [], 'count': 0}
            subject_performance[subject]['scores'].append(attempt.percentage)
            subject_performance[subject]['count'] += 1
        
        performance_by_subject = [
            {
                'subject': subject,
                'average_score': sum(data['scores']) / len(data['scores']),
                'attempts_count': data['count'],
                'best_score': max(data['scores'])
            }
            for subject, data in subject_performance.items()
        ]
        
        # Recent attempts (last 10)
        recent_attempts = []
        for attempt in quiz_attempts[:10]:
            attempt_data = attempt.to_dict()
            attempt_data['quiz_title'] = attempt.quiz.title
            attempt_data['topic_title'] = attempt.quiz.topic.title
            attempt_data['subject'] = attempt.quiz.topic.learning_path.subject
            recent_attempts.append(attempt_data)
        
        return jsonify({
            'total_attempts': total_attempts,
            'average_score': round(average_score, 1),
            'best_score': round(best_score, 1),
            'improvement_trend': round(improvement_trend, 1),
            'performance_by_difficulty': performance_by_difficulty,
            'performance_by_subject': performance_by_subject,
            'recent_attempts': recent_attempts
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/study-time', methods=['GET'])
@token_required
def get_study_time_analytics(current_user):
    """Get study time analytics"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Daily study time (based on completed resources)
        daily_study_time = db.session.query(
            func.date(Resource.created_at).label('date'),
            func.sum(Resource.duration_minutes).label('total_minutes')
        ).join(Topic).join(LearningPath).filter(
            LearningPath.user_id == current_user.id,
            Resource.is_completed == True,
            Resource.created_at >= start_date,
            Resource.duration_minutes.isnot(None)
        ).group_by(func.date(Resource.created_at)).all()
        
        # Study time by subject
        subject_study_time = db.session.query(
            LearningPath.subject,
            func.sum(Resource.duration_minutes).label('total_minutes')
        ).join(Topic).join(Resource).filter(
            LearningPath.user_id == current_user.id,
            Resource.is_completed == True,
            Resource.created_at >= start_date,
            Resource.duration_minutes.isnot(None)
        ).group_by(LearningPath.subject).all()
        
        # Weekly averages
        weekly_averages = []
        current_date = start_date
        while current_date < datetime.utcnow():
            week_end = current_date + timedelta(days=7)
            week_study_time = db.session.query(
                func.sum(Resource.duration_minutes)
            ).join(Topic).join(LearningPath).filter(
                LearningPath.user_id == current_user.id,
                Resource.is_completed == True,
                Resource.created_at >= current_date,
                Resource.created_at < week_end,
                Resource.duration_minutes.isnot(None)
            ).scalar() or 0
            
            weekly_averages.append({
                'week_start': current_date.strftime('%Y-%m-%d'),
                'total_minutes': week_study_time,
                'daily_average': week_study_time / 7
            })
            current_date = week_end
        
        return jsonify({
            'daily_study_time': [
                {
                    'date': item.date.strftime('%Y-%m-%d'),
                    'minutes': item.total_minutes,
                    'hours': round(item.total_minutes / 60, 1)
                }
                for item in daily_study_time
            ],
            'subject_study_time': [
                {
                    'subject': item.subject,
                    'total_minutes': item.total_minutes,
                    'total_hours': round(item.total_minutes / 60, 1)
                }
                for item in subject_study_time
            ],
            'weekly_averages': weekly_averages,
            'total_study_time': sum(item.total_minutes for item in subject_study_time),
            'daily_goal_minutes': current_user.daily_goal_minutes
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_learning_streak(user_id):
    """Calculate consecutive days of learning activity"""
    try:
        # Get dates with activity (quiz attempts or completed resources)
        quiz_dates = db.session.query(
            func.date(QuizAttempt.completed_at).label('activity_date')
        ).filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.completed_at.isnot(None)
        ).distinct().subquery()
        
        resource_dates = db.session.query(
            func.date(Resource.created_at).label('activity_date')
        ).join(Topic).join(LearningPath).filter(
            LearningPath.user_id == user_id,
            Resource.is_completed == True
        ).distinct().subquery()
        
        # Combine activity dates
        activity_dates = db.session.query(
            quiz_dates.c.activity_date
        ).union(
            db.session.query(resource_dates.c.activity_date)
        ).order_by(quiz_dates.c.activity_date.desc()).all()
        
        if not activity_dates:
            return 0
        
        # Calculate streak
        streak = 0
        current_date = datetime.utcnow().date()
        
        for activity_date in activity_dates:
            date_obj = activity_date[0]
            if date_obj == current_date or date_obj == current_date - timedelta(days=1):
                streak += 1
                current_date = date_obj - timedelta(days=1)
            else:
                break
        
        return streak
    
    except Exception:
        return 0

def get_recent_activity(user_id, days):
    """Get recent learning activity"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Recent quiz attempts
        recent_quizzes = QuizAttempt.query.filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.completed_at >= start_date,
            QuizAttempt.completed_at.isnot(None)
        ).order_by(QuizAttempt.completed_at.desc()).limit(5).all()
        
        # Recent completed resources
        recent_resources = db.session.query(Resource).join(Topic).join(LearningPath).filter(
            LearningPath.user_id == user_id,
            Resource.is_completed == True,
            Resource.created_at >= start_date
        ).order_by(Resource.created_at.desc()).limit(5).all()
        
        activity = []
        
        for quiz in recent_quizzes:
            activity.append({
                'type': 'quiz_completed',
                'title': f"Completed quiz: {quiz.quiz.title}",
                'score': quiz.percentage,
                'date': quiz.completed_at.isoformat(),
                'subject': quiz.quiz.topic.learning_path.subject
            })
        
        for resource in recent_resources:
            activity.append({
                'type': 'resource_completed',
                'title': f"Completed: {resource.title}",
                'resource_type': resource.resource_type,
                'date': resource.created_at.isoformat(),
                'subject': resource.topic.learning_path.subject
            })
        
        # Sort by date
        activity.sort(key=lambda x: x['date'], reverse=True)
        
        return activity[:10]
    
    except Exception:
        return []

def get_quiz_performance_trends(user_id, days):
    """Get quiz performance trends over time"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Group quiz attempts by week
        weekly_performance = db.session.query(
            func.extract('week', QuizAttempt.completed_at).label('week'),
            func.extract('year', QuizAttempt.completed_at).label('year'),
            func.avg(QuizAttempt.percentage).label('avg_score'),
            func.count(QuizAttempt.id).label('attempts_count')
        ).filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.completed_at >= start_date,
            QuizAttempt.completed_at.isnot(None)
        ).group_by(
            func.extract('week', QuizAttempt.completed_at),
            func.extract('year', QuizAttempt.completed_at)
        ).order_by(
            func.extract('year', QuizAttempt.completed_at),
            func.extract('week', QuizAttempt.completed_at)
        ).all()
        
        return [
            {
                'week': int(item.week),
                'year': int(item.year),
                'average_score': round(item.avg_score, 1),
                'attempts_count': item.attempts_count
            }
            for item in weekly_performance
        ]
    
    except Exception:
        return []

def calculate_daily_goal_progress(user, days):
    """Calculate progress towards daily learning goals"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        daily_goal = user.daily_goal_minutes
        
        # Get daily study time
        daily_times = db.session.query(
            func.date(Resource.created_at).label('date'),
            func.sum(Resource.duration_minutes).label('total_minutes')
        ).join(Topic).join(LearningPath).filter(
            LearningPath.user_id == user.id,
            Resource.is_completed == True,
            Resource.created_at >= start_date,
            Resource.duration_minutes.isnot(None)
        ).group_by(func.date(Resource.created_at)).all()
        
        # Calculate goal achievement
        days_met_goal = sum(1 for day in daily_times if day.total_minutes >= daily_goal)
        total_days = len(daily_times) if daily_times else days
        goal_achievement_rate = (days_met_goal / total_days * 100) if total_days > 0 else 0
        
        return {
            'daily_goal_minutes': daily_goal,
            'days_met_goal': days_met_goal,
            'total_active_days': len(daily_times),
            'goal_achievement_rate': round(goal_achievement_rate, 1),
            'average_daily_minutes': round(sum(day.total_minutes for day in daily_times) / len(daily_times), 1) if daily_times else 0
        }
    
    except Exception:
        return {
            'daily_goal_minutes': user.daily_goal_minutes,
            'days_met_goal': 0,
            'total_active_days': 0,
            'goal_achievement_rate': 0,
            'average_daily_minutes': 0
        }

