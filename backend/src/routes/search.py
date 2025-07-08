from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.learning import db, User, LearningPath, Quiz, Resource, Note, Topic
from src.models.feedback import Feedback
from sqlalchemy import or_, and_, func
from datetime import datetime, timedelta

search_bp = Blueprint('search', __name__)

@search_bp.route('/search/global', methods=['GET'])
@jwt_required()
def global_search():
    """Perform global search across all content types"""
    try:
        current_user_id = get_jwt_identity()
        query = request.args.get('q', '').strip()
        content_types = request.args.getlist('types')  # learning_paths, quizzes, resources, notes
        limit = request.args.get('limit', 20, type=int)
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        if not content_types:
            content_types = ['learning_paths', 'quizzes', 'resources', 'notes']
        
        results = {
            'query': query,
            'results': {},
            'total_results': 0
        }
        
        # Search Learning Paths
        if 'learning_paths' in content_types:
            learning_paths = LearningPath.query.filter(
                or_(
                    LearningPath.title.ilike(f'%{query}%'),
                    LearningPath.description.ilike(f'%{query}%'),
                    LearningPath.subject.ilike(f'%{query}%')
                )
            ).limit(limit).all()
            
            results['results']['learning_paths'] = [
                {
                    **lp.to_dict(),
                    'type': 'learning_path',
                    'relevance_score': _calculate_relevance_score(query, lp.title, lp.description)
                }
                for lp in learning_paths
            ]
            results['total_results'] += len(learning_paths)
        
        # Search Quizzes
        if 'quizzes' in content_types:
            quizzes = Quiz.query.filter(
                or_(
                    Quiz.title.ilike(f'%{query}%'),
                    Quiz.description.ilike(f'%{query}%'),
                    Quiz.subject.ilike(f'%{query}%')
                )
            ).limit(limit).all()
            
            results['results']['quizzes'] = [
                {
                    **quiz.to_dict(),
                    'type': 'quiz',
                    'relevance_score': _calculate_relevance_score(query, quiz.title, quiz.description)
                }
                for quiz in quizzes
            ]
            results['total_results'] += len(quizzes)
        
        # Search Resources
        if 'resources' in content_types:
            resources = Resource.query.filter(
                or_(
                    Resource.title.ilike(f'%{query}%'),
                    Resource.description.ilike(f'%{query}%'),
                    Resource.content.ilike(f'%{query}%'),
                    Resource.tags.ilike(f'%{query}%')
                )
            ).limit(limit).all()
            
            results['results']['resources'] = [
                {
                    **resource.to_dict(),
                    'type': 'resource',
                    'relevance_score': _calculate_relevance_score(query, resource.title, resource.description, resource.content)
                }
                for resource in resources
            ]
            results['total_results'] += len(resources)
        
        # Search Notes (user's own notes only)
        if 'notes' in content_types:
            notes = Note.query.filter(
                and_(
                    Note.user_id == current_user_id,
                    or_(
                        Note.title.ilike(f'%{query}%'),
                        Note.content.ilike(f'%{query}%'),
                        Note.tags.ilike(f'%{query}%')
                    )
                )
            ).limit(limit).all()
            
            results['results']['notes'] = [
                {
                    **note.to_dict(),
                    'type': 'note',
                    'relevance_score': _calculate_relevance_score(query, note.title, note.content)
                }
                for note in notes
            ]
            results['total_results'] += len(notes)
        
        # Sort all results by relevance score
        all_results = []
        for content_type, items in results['results'].items():
            all_results.extend(items)
        
        all_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        results['sorted_results'] = all_results[:limit]
        
        return jsonify(results), 200
        
    except Exception as e:
        current_app.logger.error(f"Error in global search: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500

@search_bp.route('/search/suggestions', methods=['GET'])
@jwt_required()
def search_suggestions():
    """Get search suggestions based on partial query"""
    try:
        current_user_id = get_jwt_identity()
        query = request.args.get('q', '').strip()
        limit = request.args.get('limit', 10, type=int)
        
        if len(query) < 2:
            return jsonify({'suggestions': []}), 200
        
        suggestions = []
        
        # Get suggestions from learning paths
        lp_suggestions = db.session.query(LearningPath.title).filter(
            LearningPath.title.ilike(f'%{query}%')
        ).limit(limit // 4).all()
        suggestions.extend([{'text': title[0], 'type': 'learning_path'} for title in lp_suggestions])
        
        # Get suggestions from quizzes
        quiz_suggestions = db.session.query(Quiz.title).filter(
            Quiz.title.ilike(f'%{query}%')
        ).limit(limit // 4).all()
        suggestions.extend([{'text': title[0], 'type': 'quiz'} for title in quiz_suggestions])
        
        # Get suggestions from resources
        resource_suggestions = db.session.query(Resource.title).filter(
            Resource.title.ilike(f'%{query}%')
        ).limit(limit // 4).all()
        suggestions.extend([{'text': title[0], 'type': 'resource'} for title in resource_suggestions])
        
        # Get suggestions from user's notes
        note_suggestions = db.session.query(Note.title).filter(
            and_(
                Note.user_id == current_user_id,
                Note.title.ilike(f'%{query}%')
            )
        ).limit(limit // 4).all()
        suggestions.extend([{'text': title[0], 'type': 'note'} for title in note_suggestions])
        
        # Remove duplicates and limit results
        unique_suggestions = []
        seen_texts = set()
        for suggestion in suggestions:
            if suggestion['text'] not in seen_texts:
                unique_suggestions.append(suggestion)
                seen_texts.add(suggestion['text'])
                if len(unique_suggestions) >= limit:
                    break
        
        return jsonify({'suggestions': unique_suggestions}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting search suggestions: {str(e)}")
        return jsonify({'error': 'Failed to get suggestions'}), 500

@search_bp.route('/search/advanced', methods=['POST'])
@jwt_required()
def advanced_search():
    """Perform advanced search with filters"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        query = data.get('query', '').strip()
        filters = data.get('filters', {})
        sort_by = data.get('sort_by', 'relevance')  # relevance, date, title
        sort_order = data.get('sort_order', 'desc')  # asc, desc
        page = data.get('page', 1)
        per_page = data.get('per_page', 20)
        
        results = {
            'query': query,
            'filters': filters,
            'results': [],
            'pagination': {}
        }
        
        # Build base queries for each content type
        queries = {}
        
        # Learning Paths
        if filters.get('include_learning_paths', True):
            lp_query = LearningPath.query
            
            if query:
                lp_query = lp_query.filter(
                    or_(
                        LearningPath.title.ilike(f'%{query}%'),
                        LearningPath.description.ilike(f'%{query}%'),
                        LearningPath.subject.ilike(f'%{query}%')
                    )
                )
            
            # Apply filters
            if filters.get('subject'):
                lp_query = lp_query.filter(LearningPath.subject.ilike(f'%{filters["subject"]}%'))
            
            if filters.get('difficulty'):
                lp_query = lp_query.filter(LearningPath.difficulty_level == filters['difficulty'])
            
            if filters.get('date_from'):
                date_from = datetime.fromisoformat(filters['date_from'])
                lp_query = lp_query.filter(LearningPath.created_at >= date_from)
            
            if filters.get('date_to'):
                date_to = datetime.fromisoformat(filters['date_to'])
                lp_query = lp_query.filter(LearningPath.created_at <= date_to)
            
            queries['learning_paths'] = lp_query
        
        # Quizzes
        if filters.get('include_quizzes', True):
            quiz_query = Quiz.query
            
            if query:
                quiz_query = quiz_query.filter(
                    or_(
                        Quiz.title.ilike(f'%{query}%'),
                        Quiz.description.ilike(f'%{query}%'),
                        Quiz.subject.ilike(f'%{query}%')
                    )
                )
            
            # Apply filters
            if filters.get('subject'):
                quiz_query = quiz_query.filter(Quiz.subject.ilike(f'%{filters["subject"]}%'))
            
            if filters.get('difficulty'):
                quiz_query = quiz_query.filter(Quiz.difficulty_level == filters['difficulty'])
            
            if filters.get('date_from'):
                date_from = datetime.fromisoformat(filters['date_from'])
                quiz_query = quiz_query.filter(Quiz.created_at >= date_from)
            
            if filters.get('date_to'):
                date_to = datetime.fromisoformat(filters['date_to'])
                quiz_query = quiz_query.filter(Quiz.created_at <= date_to)
            
            queries['quizzes'] = quiz_query
        
        # Resources
        if filters.get('include_resources', True):
            resource_query = Resource.query
            
            if query:
                resource_query = resource_query.filter(
                    or_(
                        Resource.title.ilike(f'%{query}%'),
                        Resource.description.ilike(f'%{query}%'),
                        Resource.content.ilike(f'%{query}%'),
                        Resource.tags.ilike(f'%{query}%')
                    )
                )
            
            # Apply filters
            if filters.get('resource_type'):
                resource_query = resource_query.filter(Resource.resource_type == filters['resource_type'])
            
            if filters.get('date_from'):
                date_from = datetime.fromisoformat(filters['date_from'])
                resource_query = resource_query.filter(Resource.created_at >= date_from)
            
            if filters.get('date_to'):
                date_to = datetime.fromisoformat(filters['date_to'])
                resource_query = resource_query.filter(Resource.created_at <= date_to)
            
            queries['resources'] = resource_query
        
        # Notes (user's own only)
        if filters.get('include_notes', True):
            note_query = Note.query.filter_by(user_id=current_user_id)
            
            if query:
                note_query = note_query.filter(
                    or_(
                        Note.title.ilike(f'%{query}%'),
                        Note.content.ilike(f'%{query}%'),
                        Note.tags.ilike(f'%{query}%')
                    )
                )
            
            # Apply filters
            if filters.get('date_from'):
                date_from = datetime.fromisoformat(filters['date_from'])
                note_query = note_query.filter(Note.created_at >= date_from)
            
            if filters.get('date_to'):
                date_to = datetime.fromisoformat(filters['date_to'])
                note_query = note_query.filter(Note.created_at <= date_to)
            
            queries['notes'] = note_query
        
        # Execute queries and combine results
        all_results = []
        
        for content_type, query_obj in queries.items():
            items = query_obj.all()
            for item in items:
                result = item.to_dict()
                result['type'] = content_type[:-1]  # Remove 's' from plural
                result['relevance_score'] = _calculate_relevance_score(
                    query, 
                    getattr(item, 'title', ''),
                    getattr(item, 'description', ''),
                    getattr(item, 'content', '')
                ) if query else 1.0
                all_results.append(result)
        
        # Sort results
        if sort_by == 'relevance':
            all_results.sort(key=lambda x: x['relevance_score'], reverse=(sort_order == 'desc'))
        elif sort_by == 'date':
            all_results.sort(key=lambda x: x.get('created_at', ''), reverse=(sort_order == 'desc'))
        elif sort_by == 'title':
            all_results.sort(key=lambda x: x.get('title', '').lower(), reverse=(sort_order == 'desc'))
        
        # Paginate results
        total_results = len(all_results)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_results = all_results[start_idx:end_idx]
        
        results['results'] = paginated_results
        results['pagination'] = {
            'page': page,
            'per_page': per_page,
            'total': total_results,
            'pages': (total_results + per_page - 1) // per_page,
            'has_next': end_idx < total_results,
            'has_prev': page > 1
        }
        
        return jsonify(results), 200
        
    except Exception as e:
        current_app.logger.error(f"Error in advanced search: {str(e)}")
        return jsonify({'error': 'Advanced search failed'}), 500

@search_bp.route('/search/popular', methods=['GET'])
@jwt_required()
def popular_searches():
    """Get popular search terms and trending content"""
    try:
        # This is a simplified implementation
        # In a real app, you'd track search queries and content views
        
        popular_terms = [
            'machine learning',
            'python programming',
            'data science',
            'web development',
            'artificial intelligence',
            'javascript',
            'react',
            'database design',
            'algorithms',
            'software engineering'
        ]
        
        # Get recently created content
        recent_learning_paths = LearningPath.query.order_by(
            LearningPath.created_at.desc()
        ).limit(5).all()
        
        recent_quizzes = Quiz.query.order_by(
            Quiz.created_at.desc()
        ).limit(5).all()
        
        recent_resources = Resource.query.order_by(
            Resource.created_at.desc()
        ).limit(5).all()
        
        return jsonify({
            'popular_terms': popular_terms,
            'trending_content': {
                'learning_paths': [lp.to_dict() for lp in recent_learning_paths],
                'quizzes': [quiz.to_dict() for quiz in recent_quizzes],
                'resources': [resource.to_dict() for resource in recent_resources]
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting popular searches: {str(e)}")
        return jsonify({'error': 'Failed to get popular searches'}), 500

def _calculate_relevance_score(query, title, description, content=None):
    """Calculate relevance score for search results"""
    if not query:
        return 1.0
    
    query_lower = query.lower()
    score = 0.0
    
    # Title matches (highest weight)
    if title and query_lower in title.lower():
        score += 10.0
        if title.lower().startswith(query_lower):
            score += 5.0  # Bonus for title starting with query
    
    # Description matches (medium weight)
    if description and query_lower in description.lower():
        score += 5.0
    
    # Content matches (lower weight)
    if content and query_lower in content.lower():
        score += 2.0
    
    # Exact matches get bonus points
    if title and title.lower() == query_lower:
        score += 20.0
    
    # Word count bonus (longer content might be more comprehensive)
    if content:
        word_count = len(content.split())
        score += min(word_count / 100, 2.0)  # Max 2 points for word count
    
    return score

