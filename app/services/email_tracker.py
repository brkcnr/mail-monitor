import time
import threading
from datetime import datetime, date
from imap_tools import MailBox, AND
from app.config import Config
from app.services.db import DatabaseService

class EmailTracker:
    """Service for tracking and processing emails"""
    
    def __init__(self):
        self.db_service = DatabaseService()
        self.mailbox = None
        self.is_connected = False
        self.last_error_time = None
        self.error_count = 0
        self.app_start_time = date.today()
        self._running = False
    
    def connect_to_imap(self):
        """Establish IMAP connection with error handling"""
        try:
            if self.mailbox:
                try:
                    self.mailbox.logout()
                except:  # noqa: E722
                    pass
            
            print("Connecting to IMAP server...")
            self.mailbox = MailBox(Config.IMAP_SERVER).login(
                Config.EMAIL_ADDRESS,
                Config.EMAIL_PASSWORD
            )
            self.mailbox.folder.set('INBOX')
            self.is_connected = True
            self.error_count = 0
            print("✓ Successfully connected to IMAP server")
            return True
        except Exception as e:
            self.error_count += 1
            self.last_error_time = datetime.now(Config.TIMEZONE)
            self.is_connected = False
            self.mailbox = None
            print(f"✗ IMAP connection error (attempt {self.error_count}): {str(e)}")
            return False
    
    def save_email_to_db(self, msg):
        """Save email and its attachments to database"""
        print(f"\nProcessing email: '{msg.subject}' from {msg.from_}")
        
        # Convert UTC time to GMT+3 and format as string
        local_date = msg.date.astimezone(Config.TIMEZONE)
        received_date_str = local_date.strftime('%d-%m-%Y %H:%M:%S')
        
        try:
            # Save email
            email_id = self.db_service.save_email(
                message_id=msg.uid,
                sender=msg.from_,
                subject=msg.subject,
                body=msg.text,
                received_date=received_date_str,
                has_attachment=bool(msg.attachments)
            )
            
            if email_id is None:
                print(f"↷ Skipped: '{msg.subject}' (already exists)")
                return False
            
            # Save attachments if any
            for att in msg.attachments:
                self.db_service.save_attachment(email_id, att.filename, att.payload)
            
            print(f"✓ Saved: '{msg.subject}' from {msg.from_}")
            return True
            
        except Exception as e:
            print(f"✗ Error saving email: {str(e)}")
            return False
    
    def process_emails(self):
        """Main email processing loop"""
        self._running = True
        while self._running:
            try:
                # Ensure connection
                if not self.is_connected:
                    if not self.connect_to_imap():
                        if self.error_count >= Config.MAX_RETRIES:
                            print(f"Max retries ({Config.MAX_RETRIES}) reached. Waiting {Config.RETRY_DELAY} seconds...")
                            time.sleep(Config.RETRY_DELAY)
                            self.error_count = 0
                        time.sleep(5)  # Short delay before retry
                        continue

                print("\nChecking for new emails...")
                # Fetch only unseen emails from today
                criteria = AND(date_gte=self.app_start_time, seen=False)
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
                
                time.sleep(Config.CHECK_INTERVAL)
                
            except Exception as e:
                print(f"✗ Error in main loop: {str(e)}")
                self.is_connected = False  # Force reconnection
                time.sleep(5)  # Short delay before retry
    
    def start_monitoring(self):
        """Start email monitoring in background thread"""
        email_thread = threading.Thread(target=self.process_emails, daemon=True)
        email_thread.start()
        print("✓ Email monitoring started")
    
    def stop_monitoring(self):
        """Stop email monitoring"""
        self._running = False
        if self.mailbox:
            try:
                self.mailbox.logout()
            except:  # noqa: E722
                pass
        print("✓ Email monitoring stopped")