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
    print("   - GET /emails")
    print("   - GET /emails/<id>/attachments") 
    print("   - GET /attachments/<id>/download")
    print("   - GET /health")
    
    try:
        # Run Flask app
        app.run(debug=Config.DEBUG, port=Config.PORT)
    except KeyboardInterrupt:
        print("\n Shutting down...")
        email_tracker.stop_monitoring()
        print(" Application stopped")