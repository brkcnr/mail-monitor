import os
from datetime import timezone, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class"""
    
    # Database
    DATABASE_PATH = 'emails.db'
    
    # Email Configuration
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    IMAP_SERVER = os.getenv('IMAP_SERVER', 'imap.gmail.com')
    IMAP_PORT = int(os.getenv('IMAP_PORT', 993))
    
    # Timezone (GMT+3)
    TIMEZONE = timezone(timedelta(hours=3))
    
    # Email Processing Configuration
    CHECK_INTERVAL = 30  # seconds
    MAX_RETRIES = 3
    RETRY_DELAY = 60  # seconds
    
    # Flask Configuration
    DEBUG = True
    PORT = 5000
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present"""
        required_vars = ['EMAIL_ADDRESS', 'EMAIL_PASSWORD', 'IMAP_SERVER']
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True