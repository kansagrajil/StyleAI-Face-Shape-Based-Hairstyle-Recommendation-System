"""
Flask Application Factory.
Creates and configures the Flask application, registers blueprints,
initializes services, and sets up CORS and error handlers.
"""

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from server.config import get_config


# Global limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://"
)


def create_app(config_class=None):
    """
    Application factory pattern.
    
    Args:
        config_class: Optional config class override (used in testing).
    
    Returns:
        Configured Flask application instance.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

    app = Flask(
        __name__,
        static_folder='../client',
        static_url_path=''
    )


    # Load configuration
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    # Configure production logging
    from logging.handlers import RotatingFileHandler
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    file_handler = RotatingFileHandler(os.path.join(log_dir, 'app.log'), maxBytes=10*1024*1024, backupCount=5)
    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)


    # Ensure upload directory exists
    upload_folder = app.config.get('UPLOAD_FOLDER', 'server/uploads')
    os.makedirs(upload_folder, exist_ok=True)

    # Initialize extensions
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5000", "http://127.0.0.1:5000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    limiter.init_app(app)

    # Initialize database connection
    from server.services.db_service import DatabaseService
    app.db = DatabaseService(app.config['MONGO_URI'])

    # Initialize Flask-Login
    from flask_login import LoginManager
    from server.models.user import User

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        user_doc = app.db.find_user_by_id(user_id)
        if user_doc:
            return User(user_doc)
        return None


    # Initialize ML services (lazy-loaded to avoid slow startup if model missing)
    app.face_service = None
    app.classifier_service = None
    app.genai_service = None

    def _get_face_service():
        if app.face_service is None:
            from server.services.face_service import FaceService
            app.face_service = FaceService()
        return app.face_service

    def _get_classifier_service():
        if app.classifier_service is None:
            from server.services.classifier_service import ClassifierService
            app.classifier_service = ClassifierService(app.config['MODEL_PATH'])
        return app.classifier_service

    def _get_genai_service():
        if app.genai_service is None:
            from server.services.genai_service import GenAIService
            app.genai_service = GenAIService(app.config['GEMINI_API_KEY'])
        return app.genai_service

    app.get_face_service = _get_face_service
    app.get_classifier_service = _get_classifier_service
    app.get_genai_service = _get_genai_service

    # Register blueprints
    from server.routes.auth_routes import auth_bp
    from server.routes.analyze_routes import analyze_bp
    from server.routes.recommend_routes import recommend_bp
    from server.routes.history_routes import history_bp
    from server.routes.tryon_routes import tryon_bp
    from server.routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(analyze_bp, url_prefix='/api')
    app.register_blueprint(recommend_bp, url_prefix='/api')
    app.register_blueprint(history_bp, url_prefix='/api')
    app.register_blueprint(tryon_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # Serve frontend pages and uploads
    @app.route('/')
    def serve_index():
        return app.send_static_file('index.html')

    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        from flask import send_from_directory
        upload_dir = os.path.abspath(app.config.get('UPLOAD_FOLDER', 'server/uploads'))
        return send_from_directory(upload_dir, filename)

    @app.route('/<path:path>')
    def serve_static(path):
        return app.send_static_file(path)


    # Global error handlers
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'error': 'Bad request', 'message': str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404

    @app.errorhandler(413)
    def payload_too_large(e):
        return jsonify({'error': 'File too large', 'message': 'Maximum file size is 5MB'}), 413

    @app.errorhandler(429)
    def rate_limited(e):
        return jsonify({'error': 'Rate limited', 'message': 'Too many requests, please slow down'}), 429

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': 'Internal server error', 'message': 'Something went wrong'}), 500

    return app
