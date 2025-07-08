import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.learning import db, User, LearningPath, Topic, Resource, Quiz, Question, QuizAttempt, Note
from src.routes.auth import auth_bp
from src.routes.learning_paths import learning_path_bp
from src.routes.quizzes import quiz_bp
from src.routes.resources import resource_bp
from src.routes.notes import note_bp
from src.routes.analytics import analytics_bp
from src.routes.ai import ai_bp
from src.routes.user import user_bp
from src.routes.recommendations import recommendations_bp
from src.routes.notifications import notifications_bp
from src.routes.activity import activity_bp
from src.routes.feedback import feedback_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Enable CORS for all routes
CORS(app)

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(learning_path_bp, url_prefix='/api')
app.register_blueprint(quiz_bp, url_prefix='/api')
app.register_blueprint(resource_bp, url_prefix='/api')
app.register_blueprint(note_bp, url_prefix='/api')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(ai_bp, url_prefix=\"/api/ai\")
app.register_blueprint(user_bp, url_prefix=\"/api/user\")
app.register_blueprint(recommendations_bp, url_prefix=\"/api/recommendations\")
app.register_blueprint(notifications_bp, url_prefix=\"/api\")
app.register_blueprint(activity_bp, url_prefix="/api")
app.register_blueprint(feedback_bp, url_prefix="/api")

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
