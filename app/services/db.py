import sqlite3
from contextlib import contextmanager
from app.config import Config

class DatabaseService:
    """Service for database operations"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DATABASE_PATH
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            c = conn.cursor()
            
            # Create emails table
            c.execute('''
                CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT UNIQUE,
                    sender TEXT NOT NULL,
                    subject TEXT,
                    body TEXT,
                    received_date TEXT,
                    has_attachment BOOLEAN
                )
            ''')
            
            # Create attachments table
            c.execute('''
                CREATE TABLE IF NOT EXISTS attachments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_id INTEGER,
                    filename TEXT,
                    content BLOB,
                    FOREIGN KEY (email_id) REFERENCES emails (id)
                )
            ''')
            
            conn.commit()
            print("✓ Database initialized successfully")
    
    def save_email(self, message_id, sender, subject, body, received_date, has_attachment):
        """Save email to database"""
        with self.get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute('''
                    INSERT INTO emails (message_id, sender, subject, body, received_date, has_attachment)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (message_id, sender, subject, body, received_date, has_attachment))
                
                conn.commit()
                return c.lastrowid
            except sqlite3.IntegrityError:
                return None  # Email already exists
    
    def save_attachment(self, email_id, filename, content):
        """Save attachment to database"""
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO attachments (email_id, filename, content)
                VALUES (?, ?, ?)
            ''', (email_id, filename, content))
            conn.commit()
    
    def get_all_emails(self):
        """Retrieve all emails with attachment count"""
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('''
                SELECT e.id, e.sender, e.subject, e.received_date, e.has_attachment,
                       COUNT(a.id) as attachment_count
                FROM emails e
                LEFT JOIN attachments a ON e.id = a.email_id
                GROUP BY e.id
                ORDER BY e.received_date DESC
            ''')
            return c.fetchall()
    
    def get_email_attachments(self, email_id):
        """Get attachments for specific email"""
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('''
                SELECT id, filename
                FROM attachments
                WHERE email_id = ?
            ''', (email_id,))
            return c.fetchall()
    
    def get_attachment(self, attachment_id):
        """Get specific attachment"""
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('''
                SELECT filename, content
                FROM attachments
                WHERE id = ?
            ''', (attachment_id,))
            return c.fetchone()