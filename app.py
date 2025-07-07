from app import create_app, start_email_monitoring
from app.config import Config
from flask_socketio import SocketIO

if __name__ == '__main__':
    # Create Flask app
    app = create_app()
    
    # Initialize SocketIO with gevent
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')
    
    # Start email monitoring with WebSocket support
    email_tracker = start_email_monitoring(socketio)
    
    print("Email Tracker Application Started")
    print(f"Monitoring: {Config.EMAIL_ADDRESS}")
    print(f"Server: http://localhost:{Config.PORT}")
    print("Real-time updates enabled via WebSocket (gevent)")
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
        # Run Flask app with SocketIO using gevent
        socketio.run(app, debug=Config.DEBUG, port=Config.PORT, host='0.0.0.0')
    except KeyboardInterrupt:
        print("\n Shutting down...")
        email_tracker.stop_monitoring()
        print("Application stopped")