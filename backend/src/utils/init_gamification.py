from src.models.learning import db
from src.models.gamification import Achievement, Badge

def initialize_achievements():
    """Initialize default achievements"""
    achievements_data = [
        # Learning Path Achievements
        {
            'name': 'First Steps',
            'description': 'Complete your first learning path',
            'icon': 'graduation-cap',
            'category': 'learning',
            'points': 100,
            'rarity': 'common',
            'condition_type': 'count',
            'condition_target': 1,
            'condition_resource': 'learning_paths_completed'
        },
        {
            'name': 'Learning Enthusiast',
            'description': 'Complete 5 learning paths',
            'icon': 'book-open',
            'category': 'learning',
            'points': 500,
            'rarity': 'rare',
            'condition_type': 'count',
            'condition_target': 5,
            'condition_resource': 'learning_paths_completed'
        },
        {
            'name': 'Knowledge Master',
            'description': 'Complete 10 learning paths',
            'icon': 'crown',
            'category': 'learning',
            'points': 1000,
            'rarity': 'epic',
            'condition_type': 'count',
            'condition_target': 10,
            'condition_resource': 'learning_paths_completed'
        },
        
        # Quiz Achievements
        {
            'name': 'Quiz Rookie',
            'description': 'Complete your first quiz',
            'icon': 'brain',
            'category': 'quiz',
            'points': 50,
            'rarity': 'common',
            'condition_type': 'count',
            'condition_target': 1,
            'condition_resource': 'quizzes_completed'
        },
        {
            'name': 'Quiz Champion',
            'description': 'Complete 25 quizzes',
            'icon': 'trophy',
            'category': 'quiz',
            'points': 750,
            'rarity': 'rare',
            'condition_type': 'count',
            'condition_target': 25,
            'condition_resource': 'quizzes_completed'
        },
        {
            'name': 'Perfect Score',
            'description': 'Achieve 95% average quiz score',
            'icon': 'star',
            'category': 'quiz',
            'points': 1500,
            'rarity': 'epic',
            'condition_type': 'score',
            'condition_target': 95,
            'condition_resource': 'average_quiz_score'
        },
        
        # Streak Achievements
        {
            'name': 'Consistent Learner',
            'description': 'Maintain a 7-day learning streak',
            'icon': 'calendar',
            'category': 'milestone',
            'points': 300,
            'rarity': 'rare',
            'condition_type': 'streak',
            'condition_target': 7,
            'condition_resource': 'learning_streak'
        },
        {
            'name': 'Dedication Master',
            'description': 'Maintain a 30-day learning streak',
            'icon': 'flame',
            'category': 'milestone',
            'points': 2000,
            'rarity': 'legendary',
            'condition_type': 'streak',
            'condition_target': 30,
            'condition_resource': 'learning_streak'
        },
        
        # Resource Achievements
        {
            'name': 'Curious Explorer',
            'description': 'View 50 learning resources',
            'icon': 'search',
            'category': 'learning',
            'points': 200,
            'rarity': 'common',
            'condition_type': 'count',
            'condition_target': 50,
            'condition_resource': 'resources_viewed'
        },
        
        # Note-taking Achievements
        {
            'name': 'Note Taker',
            'description': 'Create 10 notes',
            'icon': 'file-text',
            'category': 'learning',
            'points': 150,
            'rarity': 'common',
            'condition_type': 'count',
            'condition_target': 10,
            'condition_resource': 'notes_created'
        },
        
        # Point Milestones
        {
            'name': 'Rising Star',
            'description': 'Earn 1,000 total points',
            'icon': 'trending-up',
            'category': 'milestone',
            'points': 100,
            'rarity': 'rare',
            'condition_type': 'time',
            'condition_target': 1000,
            'condition_resource': 'total_points'
        },
        {
            'name': 'Point Collector',
            'description': 'Earn 5,000 total points',
            'icon': 'gem',
            'category': 'milestone',
            'points': 500,
            'rarity': 'epic',
            'condition_type': 'time',
            'condition_target': 5000,
            'condition_resource': 'total_points'
        }
    ]
    
    for achievement_data in achievements_data:
        existing = Achievement.query.filter_by(name=achievement_data['name']).first()
        if not existing:
            achievement = Achievement(**achievement_data)
            db.session.add(achievement)
    
    db.session.commit()
    print(f"Initialized {len(achievements_data)} achievements")

def initialize_badges():
    """Initialize default badges"""
    badges_data = [
        # Level Badges
        {
            'name': 'Novice',
            'description': 'Reach level 5',
            'icon': 'shield',
            'color': '#10B981',
            'category': 'level',
            'condition_type': 'level',
            'condition_value': 5
        },
        {
            'name': 'Apprentice',
            'description': 'Reach level 10',
            'icon': 'shield',
            'color': '#3B82F6',
            'category': 'level',
            'condition_type': 'level',
            'condition_value': 10
        },
        {
            'name': 'Expert',
            'description': 'Reach level 20',
            'icon': 'shield',
            'color': '#8B5CF6',
            'category': 'level',
            'condition_type': 'level',
            'condition_value': 20
        },
        {
            'name': 'Master',
            'description': 'Reach level 50',
            'icon': 'shield',
            'color': '#F59E0B',
            'category': 'level',
            'condition_type': 'level',
            'condition_value': 50
        },
        
        # Achievement Badges
        {
            'name': 'Achiever',
            'description': 'Earn 5 achievements',
            'icon': 'award',
            'color': '#EF4444',
            'category': 'achievement',
            'condition_type': 'achievements',
            'condition_value': 5
        },
        {
            'name': 'Overachiever',
            'description': 'Earn 10 achievements',
            'icon': 'award',
            'color': '#DC2626',
            'category': 'achievement',
            'condition_type': 'achievements',
            'condition_value': 10
        },
        
        # Point Badges
        {
            'name': 'Point Hunter',
            'description': 'Earn 2,500 points',
            'icon': 'target',
            'color': '#06B6D4',
            'category': 'points',
            'condition_type': 'points',
            'condition_value': 2500
        },
        {
            'name': 'Point Master',
            'description': 'Earn 10,000 points',
            'icon': 'target',
            'color': '#0891B2',
            'category': 'points',
            'condition_type': 'points',
            'condition_value': 10000
        }
    ]
    
    for badge_data in badges_data:
        existing = Badge.query.filter_by(name=badge_data['name']).first()
        if not existing:
            badge = Badge(**badge_data)
            db.session.add(badge)
    
    db.session.commit()
    print(f"Initialized {len(badges_data)} badges")

def initialize_gamification_data():
    """Initialize all gamification data"""
    print("Initializing gamification data...")
    initialize_achievements()
    initialize_badges()
    print("Gamification data initialization complete!")

if __name__ == '__main__':
    # This can be run standalone to initialize data
    from src.models.learning import app
    with app.app_context():
        initialize_gamification_data()

