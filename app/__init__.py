from flask import Flask
from flask_socketio import SocketIO
from app.routes.email_routes import email_bp
from app.routes.web_routes import web_bp
from app.services.db import DatabaseService
from app.services.email_tracker import EmailTracker
from app.config import Config

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    app.secret_key = Config.SECRET_KEY
    
    Config.validate_config()
    
    # Initialize database
    db_service = DatabaseService()
    db_service.init_database()
    
    # Register blueprints
    app.register_blueprint(email_bp)
    app.register_blueprint(web_bp)
    
    return app

def start_email_monitoring(socketio=None):
    """Start email monitoring service with optional WebSocket support"""
    tracker = EmailTracker(socketio=socketio)
    tracker.start_monitoring()
    return tracker