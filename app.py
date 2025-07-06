from app import create_app, start_email_monitoring
from app.config import Config

if __name__ == '__main__':
    # Create Flask app
    app = create_app()
    
    # Start email monitoring in background
    email_tracker = start_email_monitoring()
    
    print("Email Tracker Application Started")
    print(f"Monitoring: {Config.EMAIL_ADDRESS}")
    print(f"Server: http://localhost:{Config.PORT}")
    print("Available endpoints:")
    print("   Web Interface:")
    print("     - Dashboard: /")
    print("     - Emails: /emails")
    print("     - Email Detail: /emails/<id>")
    print("   API Endpoints:")
    print("     - GET /api/emails")
    print("     - GET /api/emails/<id>/attachments") 
    print("     - GET /api/attachments/<id>/download")
    print("     - GET /api/attachments/<id>/view")
    print("     - GET /api/health")
    
    try:
        # Run Flask app
        app.run(debug=Config.DEBUG, port=Config.PORT)
    except KeyboardInterrupt:
        print("\n Shutting down...")
        email_tracker.stop_monitoring()
        print("Application stopped")