from flask import Flask, send_file, jsonify
import os
from datetime import datetime, date, timedelta
import sqlite3
from dotenv import load_dotenv
from imap_tools import MailBox, AND
import time
import threading
import io
from datetime import timezone

# Load environment variables
load_dotenv()

# Define timezone (GMT+3)
TIMEZONE = timezone(timedelta(hours=3))

# Track when the application started
APP_START_TIME = date.today()

class EmailTracker:
    def __init__(self, db_path='emails.db'):
        self.db_path = db_path
        self.mailbox = None
        self.is_connected = False
        self.last_error_time = None
        self.error_count = 0
        self.max_retries = 3
        self.retry_delay = 60  # seconds

    def connect_to_imap(self):
        """Establish IMAP connection with error handling"""
        try:
            if self.mailbox:
                try:
                    self.mailbox.logout()
                except:  # noqa: E722
                    pass
            
            print("Connecting to IMAP server...")
            self.mailbox = MailBox(os.getenv('IMAP_SERVER')).login(
                os.getenv('EMAIL_ADDRESS'),
                os.getenv('EMAIL_PASSWORD')
            )
            self.mailbox.folder.set('INBOX')
            self.is_connected = True
            self.error_count = 0
            print("✓ Successfully connected to IMAP server")
            return True
        except Exception as e:
            self.error_count += 1
            self.last_error_time = datetime.now(TIMEZONE)
            self.is_connected = False
            self.mailbox = None
            print(f"✗ IMAP connection error (attempt {self.error_count}): {str(e)}")
            return False

    def save_email_to_db(self, msg):
        """Save email and its attachments to database"""
        print(f"\nProcessing email: '{msg.subject}' from {msg.from_}")
        
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            
            # Convert UTC time to GMT+3 and format as string
            local_date = msg.date.astimezone(TIMEZONE)
            received_date_str = local_date.strftime('%d-%m-%Y %H:%M:%S')
            
            try:
                # Insert email with unique message_id
                c.execute('''
                    INSERT INTO emails (message_id, sender, subject, body, received_date, has_attachment)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (msg.uid, msg.from_, msg.subject, msg.text, received_date_str, bool(msg.attachments)))
                
                email_id = c.lastrowid
                
                # Save attachments if any
                for att in msg.attachments:
                    c.execute('''
                        INSERT INTO attachments (email_id, filename, content)
                        VALUES (?, ?, ?)
                    ''', (email_id, att.filename, att.payload))
                
                conn.commit()
                print(f"✓ Saved: '{msg.subject}' from {msg.from_}")
                return True
                
            except sqlite3.IntegrityError:
                print(f"↷ Skipped: '{msg.subject}' (already exists)")
                return False
            except Exception as e:
                print(f"✗ Error saving email: {str(e)}")
                return False

    def process_emails(self):
        """Main email processing loop"""
        while True:
            try:
                # Ensure connection
                if not self.is_connected:
                    if not self.connect_to_imap():
                        if self.error_count >= self.max_retries:
                            print(f"Max retries ({self.max_retries}) reached. Waiting {self.retry_delay} seconds...")
                            time.sleep(self.retry_delay)
                            self.error_count = 0
                        time.sleep(5)  # Short delay before retry
                        continue

                print("\nChecking for new emails...")
                # Fetch only unseen emails from today
                criteria = AND(date_gte=APP_START_TIME, seen=False)
                new_emails = list(self.mailbox.fetch(criteria))
                
                if new_emails:
                    print(f"Found {len(new_emails)} new emails")
                    
                    for msg in new_emails:
                        try:
                            if self.save_email_to_db(msg):
                                # Mark as seen only if successfully saved
                                self.mailbox.flag(msg.uid, ['\\Seen'], True)
                                print(f"✓ Marked as seen: '{msg.subject}'")
                        except Exception as e:
                            print(f"✗ Error processing email '{msg.subject}': {str(e)}")
                            self.is_connected = False  # Force reconnection on error
                            break
                else:
                    print("No new emails found")
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"✗ Error in main loop: {str(e)}")
                self.is_connected = False  # Force reconnection
                time.sleep(5)  # Short delay before retry

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
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
    conn.close()

@app.route('/emails/<int:email_id>/attachments', methods=['GET'])
def get_attachments(email_id):
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT id, filename
        FROM attachments
        WHERE email_id = ?
    ''', (email_id,))
    
    attachments = [
        {
            'id': row[0],
            'filename': row[1]
        }
        for row in c.fetchall()
    ]
    
    conn.close()
    return jsonify({'attachments': attachments})

@app.route('/attachments/<int:attachment_id>/download', methods=['GET'])
def download_attachment(attachment_id):
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT filename, content
        FROM attachments
        WHERE id = ?
    ''', (attachment_id,))
    
    result = c.fetchone()
    if result is None:
        conn.close()
        return 'Attachment not found', 404
        
    filename, content = result
    conn.close()
    
    return send_file(
        io.BytesIO(content),
        download_name=filename,
        as_attachment=True
    )

@app.route('/emails', methods=['GET'])
def get_emails():
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT e.id, e.sender, e.subject, e.received_date, e.has_attachment,
               COUNT(a.id) as attachment_count
        FROM emails e
        LEFT JOIN attachments a ON e.id = a.email_id
        GROUP BY e.id
        ORDER BY e.received_date DESC
    ''')
    
    emails = [
        {
            'id': row[0],
            'sender': row[1],
            'subject': row[2],
            'received_date': row[3],
            'has_attachment': row[4],
            'attachment_count': row[5]
        }
        for row in c.fetchall()
    ]
    
    conn.close()
    return {'emails': emails}

if __name__ == '__main__':
    init_db()
    
    # Start email tracker in background
    tracker = EmailTracker()
    email_thread = threading.Thread(target=tracker.process_emails, daemon=True)
    email_thread.start()
    
    app.run(debug=True, port=5000)
