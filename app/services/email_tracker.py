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
        self.last_check_time = None  # Track last successful check
        self._running = False
    
    def connect_to_imap(self):
        """Establish IMAP connection with error handling"""
        try:
            if self.mailbox:
                try:
                    self.mailbox.logout()
                except Exception:
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
    
    def get_last_email_date(self):
        """Get the date of the last processed email from database"""
        try:
            with self.db_service.get_connection() as conn:
                c = conn.cursor()
                c.execute('SELECT MAX(received_date) FROM emails')
                result = c.fetchone()
                if result and result[0]:
                    # Parse the stored date string back to datetime
                    return datetime.strptime(result[0], '%d-%m-%Y %H:%M:%S').replace(tzinfo=Config.TIMEZONE)
        except Exception as e:
            print(f"Error getting last email date: {e}")
        
        # Fallback to yesterday if no emails found
        from datetime import timedelta
        return datetime.now(Config.TIMEZONE) - timedelta(days=1)
    
    def is_email_processed(self, message_id):
        """Check if email is already processed"""
        try:
            with self.db_service.get_connection() as conn:
                c = conn.cursor()
                c.execute('SELECT COUNT(*) FROM emails WHERE message_id = ?', (message_id,))
                result = c.fetchone()
                return result[0] > 0 if result else False
        except Exception as e:
            print(f"Error checking if email is processed: {e}")
            return False
    
    def save_email_to_db(self, msg):
        """Save email and its attachments to database"""
        print(f"\nProcessing email: '{msg.subject}' from {msg.from_}")
        
        # Check if already processed (double-check for safety)
        if self.is_email_processed(msg.uid):
            return False
        
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
                return False
            
            # Save attachments if any
            for att in msg.attachments:
                self.db_service.save_attachment(email_id, att.filename, att.payload)
            
            print(f"✓ Saved: '{msg.subject}' from {msg.from_}")
            
            # Update last check time after successful save
            self.last_check_time = local_date
            return True
            
        except Exception as e:
            print(f"✗ Error saving email: {str(e)}")
            return False
    
    def process_emails(self):
        """Main email processing loop"""
        self._running = True
        
        # Initialize last check time
        if self.last_check_time is None:
            self.last_check_time = self.get_last_email_date()
            print(f"Starting email monitoring from: {self.last_check_time}")
        
        while self._running:
            try:
                # Ensure connection
                if not self.is_connected:
                    if not self.connect_to_imap():
                        if self.error_count >= Config.MAX_RETRIES:
                            print(f"Max retries ({Config.MAX_RETRIES}) reached. Waiting {Config.RETRY_DELAY} seconds...")
                            time.sleep(Config.RETRY_DELAY)
                            self.error_count = 0
                        time.sleep(5)
                        continue

                print(f"\nChecking for emails since: {self.last_check_time}")
                
                # Fetch emails received after last check time
                # Use a broader date range and get only recent emails
                search_date = self.last_check_time.date()
                criteria = AND(date_gte=search_date)
                
                all_emails = list(self.mailbox.fetch(criteria, reverse=True))
                
                # Filter emails that are newer than our last check time AND not processed
                new_emails = []
                processed_count = 0
                
                for msg in all_emails:
                    email_time = msg.date.astimezone(Config.TIMEZONE)
                    if email_time > self.last_check_time:
                        # Double-check if not already processed
                        if not self.is_email_processed(msg.uid):
                            new_emails.append(msg)
                        else:
                            processed_count += 1
                
                if new_emails:
                    print(f"Found {len(new_emails)} new emails")
                    
                    for msg in new_emails:
                        try:
                            if self.save_email_to_db(msg):
                                print(f"✓ Processed: '{msg.subject}'")
                        except Exception as e:
                            print(f"✗ Error processing email '{msg.subject}': {str(e)}")
                            self.is_connected = False
                            break
                else:
                    if processed_count > 0:
                        print(f"No new emails found ({processed_count} already processed)")
                    else:
                        print("No new emails found")
                
                time.sleep(Config.CHECK_INTERVAL)
                
            except Exception as e:
                print(f"✗ Error in main loop: {str(e)}")
                self.is_connected = False
                time.sleep(5)
    
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
            except Exception:
                pass
        print("✓ Email monitoring stopped")