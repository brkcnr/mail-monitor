from flask import Flask
from app.routes.email_routes import email_bp
from app.services.db import DatabaseService
from app.services.email_tracker import EmailTracker
from app.config import Config

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Validate configuration
    Config.validate_config()
    
    # Initialize database
    db_service = DatabaseService()
    db_service.init_database()
    
    # Register blueprints
    app.register_blueprint(email_bp)
    
    return app

def start_email_monitoring():
    """Start email monitoring service"""
    tracker = EmailTracker()
    tracker.start_monitoring()
    return tracker