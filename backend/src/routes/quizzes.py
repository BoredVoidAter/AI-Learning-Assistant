from flask import Blueprint, request, jsonify
from src.models.learning import Quiz, Question, QuizAttempt, Topic, LearningPath
from src.database import db
from src.utils.auth_utils import token_required
from datetime import datetime
import random
from sqlalchemy import or_

quiz_bp = Blueprint("quiz", __name__)


@quiz_bp.route("/quizzes", methods=["GET"])
@token_required
def get_quizzes(current_user):
    """Get quizzes for user's learning paths"""
    try:
        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        topic_id = request.args.get("topic_id", type=int)
        difficulty = request.args.get("difficulty", "")
        search_query = request.args.get("search_query", "")

        # Build query - only quizzes from user's learning paths
        query = (
            db.session.query(Quiz)
            .join(Topic)
            .join(LearningPath)
            .filter(LearningPath.user_id == current_user.id, Quiz.is_active == True)
        )

        # Apply filters
        if topic_id:
            query = query.filter(Quiz.topic_id == topic_id)
        if difficulty:
            query = query.filter(Quiz.difficulty_level == difficulty)
        if search_query:
            query = query.filter(
                or_(Quiz.title.ilike(f"%{search_query}%"), Quiz.description.ilike(f"%{search_query}%"))
            )
        # Order by creation date
        query = query.order_by(Quiz.created_at.desc())

        # Paginate results
        quizzes = query.paginate(page=page, per_page=per_page, error_out=False)

        quiz_list = []
        for quiz in quizzes.items:
            quiz_data = quiz.to_dict()
            # Add topic and learning path info
            quiz_data["topic_title"] = quiz.topic.title
            quiz_data["learning_path_title"] = quiz.topic.learning_path.title
            # Add user's best attempt
            best_attempt = (
                QuizAttempt.query.filter(
                    QuizAttempt.user_id == current_user.id,
                    QuizAttempt.quiz_id == quiz.id,
                    QuizAttempt.completed_at.isnot(None),
                )
                .order_by(QuizAttempt.percentage.desc())
                .first()
            )
            quiz_data["best_score"] = best_attempt.percentage if best_attempt else None
            quiz_list.append(quiz_data)

        return (
            jsonify(
                {
                    "quizzes": quiz_list,
                    "total": quizzes.total,
                    "pages": quizzes.pages,
                    "current_page": page,
                    "per_page": per_page,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@quiz_bp.route("/quizzes", methods=["POST"])
@token_required
def create_quiz(current_user):
    """Create a new quiz"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["topic_id", "title"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400

        # Verify topic belongs to user
        topic = (
            db.session.query(Topic)
            .join(LearningPath)
            .filter(Topic.id == data["topic_id"], LearningPath.user_id == current_user.id)
            .first()
        )

        if not topic:
            return jsonify({"error": "Topic not found or access denied"}), 404

        # Validate difficulty level
        difficulty = data.get("difficulty_level", "intermediate")
        if difficulty not in ["beginner", "intermediate", "advanced"]:
            return jsonify({"error": "Invalid difficulty level"}), 400

        # Create new quiz
        quiz = Quiz(
            topic_id=data["topic_id"],
            title=data["title"].strip(),
            description=data.get("description", "").strip(),
            difficulty_level=difficulty,
            time_limit_minutes=data.get("time_limit_minutes", 15),
        )

        db.session.add(quiz)
        db.session.commit()

        return jsonify({"message": "Quiz created successfully", "quiz": quiz.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@quiz_bp.route("/quizzes/<int:quiz_id>", methods=["GET"])
@token_required
def get_quiz(current_user, quiz_id):
    """Get a specific quiz with questions"""
    try:
        # Verify quiz belongs to user
        quiz = (
            db.session.query(Quiz)
            .join(Topic)
            .join(LearningPath)
            .filter(Quiz.id == quiz_id, LearningPath.user_id == current_user.id)
            .first()
        )

        if not quiz:
            return jsonify({"error": "Quiz not found or access denied"}), 404

        # Get questions
        questions = Question.query.filter(Question.quiz_id == quiz_id).order_by(Question.order_index).all()

        quiz_data = quiz.to_dict()
        quiz_data["questions"] = []

        for question in questions:
            question_data = question.to_dict()
            # Don't include correct answer in the response
            question_data.pop("correct_answer", None)
            quiz_data["questions"].append(question_data)

        return jsonify({"quiz": quiz_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@quiz_bp.route("/quizzes/<int:quiz_id>/questions", methods=["POST"])
@token_required
def add_question_to_quiz(current_user, quiz_id):
    """Add a question to a quiz"""
    try:
        # Verify quiz belongs to user
        quiz = (
            db.session.query(Quiz)
            .join(Topic)
            .join(LearningPath)
            .filter(Quiz.id == quiz_id, LearningPath.user_id == current_user.id)
            .first()
        )

        if not quiz:
            return jsonify({"error": "Quiz not found or access denied"}), 404

        data = request.get_json()

        # Validate required fields
        required_fields = ["question_text", "correct_answer"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400

        # Validate question type
        question_type = data.get("question_type", "multiple_choice")
        if question_type not in ["multiple_choice", "true_false", "short_answer"]:
            return jsonify({"error": "Invalid question type"}), 400

        # For multiple choice, validate options
        if question_type == "multiple_choice":
            options = data.get("options", [])
            if not options or len(options) < 2:
                return jsonify({"error": "Multiple choice questions need at least 2 options"}), 400
            if data["correct_answer"] not in options:
                return jsonify({"error": "Correct answer must be one of the options"}), 400

        # Get the next order index
        max_order = (
            db.session.query(db.func.max(Question.order_index)).filter(Question.quiz_id == quiz_id).scalar() or 0
        )

        # Create new question
        question = Question(
            quiz_id=quiz_id,
            question_text=data["question_text"].strip(),
            question_type=question_type,
            correct_answer=data["correct_answer"].strip(),
            options=data.get("options", []) if question_type == "multiple_choice" else None,
            explanation=data.get("explanation", "").strip(),
            points=data.get("points", 1),
            order_index=max_order + 1,
        )

        db.session.add(question)
        db.session.commit()

        return jsonify({"message": "Question added successfully", "question": question.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@quiz_bp.route("/quizzes/<int:quiz_id>/start", methods=["POST"])
@token_required
def start_quiz_attempt(current_user, quiz_id):
    """Start a new quiz attempt"""
    try:
        # Verify quiz belongs to user
        quiz = (
            db.session.query(Quiz)
            .join(Topic)
            .join(LearningPath)
            .filter(Quiz.id == quiz_id, LearningPath.user_id == current_user.id)
            .first()
        )

        if not quiz:
            return jsonify({"error": "Quiz not found or access denied"}), 404

        # Check if quiz has questions
        questions_count = Question.query.filter(Question.quiz_id == quiz_id).count()
        if questions_count == 0:
            return jsonify({"error": "Quiz has no questions"}), 400

        # Create new quiz attempt
        attempt = QuizAttempt(
            user_id=current_user.id, quiz_id=quiz_id, max_score=questions_count  # Assuming 1 point per question
        )

        db.session.add(attempt)
        db.session.commit()

        # Get questions for the attempt (randomize order)
        questions = Question.query.filter(Question.quiz_id == quiz_id).all()

        random.shuffle(questions)

        attempt_data = attempt.to_dict()
        attempt_data["questions"] = []

        for question in questions:
            question_data = question.to_dict()
            # Don't include correct answer
            question_data.pop("correct_answer", None)
            # Randomize multiple choice options
            if question.question_type == "multiple_choice" and question.options:
                options = question.options.copy()
                random.shuffle(options)
                question_data["options"] = options
            attempt_data["questions"].append(question_data)

        return jsonify({"message": "Quiz attempt started", "attempt": attempt_data}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@quiz_bp.route("/quiz-attempts/<int:attempt_id>/submit", methods=["POST"])
@token_required
def submit_quiz_attempt(current_user, attempt_id):
    """Submit answers for a quiz attempt"""
    try:
        # Get the attempt
        attempt = QuizAttempt.query.filter(
            QuizAttempt.id == attempt_id, QuizAttempt.user_id == current_user.id
        ).first()

        if not attempt:
            return jsonify({"error": "Quiz attempt not found"}), 404

        if attempt.completed_at:
            return jsonify({"error": "Quiz attempt already completed"}), 400

        data = request.get_json()
        answers = data.get("answers", {})

        if not answers:
            return jsonify({"error": "No answers provided"}), 400

        # Get quiz questions
        questions = Question.query.filter(Question.quiz_id == attempt.quiz_id).all()

        # Calculate score
        total_points = 0
        earned_points = 0
        detailed_results = []

        for question in questions:
            total_points += question.points
            user_answer = answers.get(str(question.id), "").strip()
            is_correct = False

            # Check answer based on question type
            if question.question_type == "multiple_choice":
                is_correct = user_answer.lower() == question.correct_answer.lower()
            elif question.question_type == "true_false":
                is_correct = user_answer.lower() == question.correct_answer.lower()
            elif question.question_type == "short_answer":
                # Simple string comparison (could be enhanced with fuzzy matching)
                is_correct = user_answer.lower().strip() == question.correct_answer.lower().strip()

            if is_correct:
                earned_points += question.points

            detailed_results.append(
                {
                    "question_id": question.id,
                    "user_answer": user_answer,
                    "correct_answer": question.correct_answer,
                    "is_correct": is_correct,
                    "points_earned": question.points if is_correct else 0,
                    "explanation": question.explanation,
                }
            )

        # Calculate percentage
        percentage = (earned_points / total_points * 100) if total_points > 0 else 0

        # Calculate time taken
        time_taken = (datetime.utcnow() - attempt.started_at).total_seconds() / 60

        # Update attempt
        attempt.score = earned_points
        attempt.max_score = total_points
        attempt.percentage = percentage
        attempt.time_taken_minutes = int(time_taken)
        attempt.answers = answers
        attempt.completed_at = datetime.utcnow()

        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Quiz completed successfully",
                    "results": {
                        "attempt_id": attempt.id,
                        "score": earned_points,
                        "max_score": total_points,
                        "percentage": percentage,
                        "time_taken_minutes": int(time_taken),
                        "detailed_results": detailed_results,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@quiz_bp.route("/quiz-attempts", methods=["GET"])
@token_required
def get_quiz_attempts(current_user):
    """Get user's quiz attempts"""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        quiz_id = request.args.get("quiz_id", type=int)

        query = QuizAttempt.query.filter(QuizAttempt.user_id == current_user.id)

        if quiz_id:
            query = query.filter(QuizAttempt.quiz_id == quiz_id)

        # Order by completion date (newest first)
        query = query.order_by(QuizAttempt.completed_at.desc().nullslast())

        attempts = query.paginate(page=page, per_page=per_page, error_out=False)

        attempts_list = []
        for attempt in attempts.items:
            attempt_data = attempt.to_dict()
            # Add quiz info
            quiz = Quiz.query.get(attempt.quiz_id)
            if quiz:
                attempt_data["quiz_title"] = quiz.title
                attempt_data["topic_title"] = quiz.topic.title
            attempts_list.append(attempt_data)

        return (
            jsonify(
                {
                    "attempts": attempts_list,
                    "total": attempts.total,
                    "pages": attempts.pages,
                    "current_page": page,
                    "per_page": per_page,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@quiz_bp.route("/quiz-attempts/<int:attempt_id>", methods=["GET"])
@token_required
def get_quiz_attempt_details(current_user, attempt_id):
    """Get detailed results of a quiz attempt"""
    try:
        attempt = QuizAttempt.query.filter(
            QuizAttempt.id == attempt_id, QuizAttempt.user_id == current_user.id
        ).first()

        if not attempt:
            return jsonify({"error": "Quiz attempt not found"}), 404

        if not attempt.completed_at:
            return jsonify({"error": "Quiz attempt not completed yet"}), 400

        # Get quiz and questions
        quiz = Quiz.query.get(attempt.quiz_id)
        questions = Question.query.filter(Question.quiz_id == attempt.quiz_id).order_by(Question.order_index).all()

        # Build detailed results
        detailed_results = []
        for question in questions:
            user_answer = attempt.answers.get(str(question.id), "") if attempt.answers else ""
            is_correct = False

            # Check if answer is correct
            if question.question_type == "multiple_choice":
                is_correct = user_answer.lower() == question.correct_answer.lower()
            elif question.question_type == "true_false":
                is_correct = user_answer.lower() == question.correct_answer.lower()
            elif question.question_type == "short_answer":
                is_correct = user_answer.lower().strip() == question.correct_answer.lower().strip()

            detailed_results.append(
                {"question": question.to_dict(), "user_answer": user_answer, "is_correct": is_correct}
            )

        attempt_data = attempt.to_dict()
        attempt_data["quiz"] = quiz.to_dict()
        attempt_data["detailed_results"] = detailed_results

        return jsonify({"attempt": attempt_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
