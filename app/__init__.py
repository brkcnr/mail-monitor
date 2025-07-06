from flask import Flask
from app.routes.email_routes import email_bp
from app.routes.web_routes import web_bp
from app.services.db import DatabaseService
from app.services.email_tracker import EmailTracker
from app.config import Config

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    app.secret_key = 'your-secret-key-here'  # Required for flash messages
    
    # Validate configuration
    Config.validate_config()
    
    # Initialize database
    db_service = DatabaseService()
    db_service.init_database()
    
    # Register blueprints
    app.register_blueprint(email_bp)  # API routes
    app.register_blueprint(web_bp)    # Web routes
    
    return app

def start_email_monitoring():
    """Start email monitoring service"""
    tracker = EmailTracker()
    tracker.start_monitoring()
    return tracker