import time
import threading
from datetime import datetime, date
from imap_tools import MailBox, AND
from app.config import Config
from app.services.db import DatabaseService

class EmailTracker:
    """Service for tracking and processing emails"""
    
    def __init__(self, socketio=None):
        self.db_service = DatabaseService()
        self.mailbox = None
        self.is_connected = False
        self.last_error_time = None
        self.error_count = 0
        self.last_check_time = None
        self._running = False
        self.socketio = socketio  # WebSocket instance for real-time updates
    
    def emit_update(self, event_type, data):
        """Emit real-time update via WebSocket"""
        if self.socketio:
            self.socketio.emit(event_type, data)
    
    def connect_to_imap(self):
        """Establish IMAP connection with error handling"""
        try:
            if self.mailbox:
                try:
                    self.mailbox.logout()
                except Exception:
                    pass
            
            print("Connecting to IMAP server...")
            self.emit_update('status_update', {
                'type': 'connection',
                'status': 'connecting',
                'message': 'Connecting to IMAP server...'
            })
            
            self.mailbox = MailBox(Config.IMAP_SERVER).login(
                Config.EMAIL_ADDRESS,
                Config.EMAIL_PASSWORD
            )
            self.mailbox.folder.set('INBOX')
            self.is_connected = True
            self.error_count = 0
            print("✓ Successfully connected to IMAP server")
            
            self.emit_update('status_update', {
                'type': 'connection',
                'status': 'connected',
                'message': 'Successfully connected to IMAP server'
            })
            return True
        except Exception as e:
            self.error_count += 1
            self.last_error_time = datetime.now(Config.TIMEZONE)
            self.is_connected = False
            self.mailbox = None
            error_msg = f"IMAP connection error (attempt {self.error_count}): {str(e)}"
            print(f"✗ {error_msg}")
            
            self.emit_update('status_update', {
                'type': 'error',
                'status': 'disconnected',
                'message': error_msg,
                'error_count': self.error_count
            })
            return False
    
    def get_last_email_date(self):
        """Get the date of the last processed email from database"""
        try:
            with self.db_service.get_connection() as conn:
                c = conn.cursor()
                c.execute('SELECT MAX(received_date) FROM emails')
                result = c.fetchone()
                if result and result[0]:
                    return datetime.strptime(result[0], '%d-%m-%Y %H:%M:%S').replace(tzinfo=Config.TIMEZONE)
        except Exception as e:
            print(f"Error getting last email date: {e}")
        
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
        
        if self.is_email_processed(msg.uid):
            return False
        
        local_date = msg.date.astimezone(Config.TIMEZONE)
        received_date_str = local_date.strftime('%d-%m-%Y %H:%M:%S')
        
        try:
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
            attachment_count = 0
            for att in msg.attachments:
                self.db_service.save_attachment(email_id, att.filename, att.payload)
                attachment_count += 1
            
            print(f"✓ Saved: '{msg.subject}' from {msg.from_}")
            
            # Emit real-time update for new email
            self.emit_update('new_email', {
                'id': email_id,
                'sender': msg.from_,
                'subject': msg.subject,
                'received_date': received_date_str,
                'has_attachment': bool(msg.attachments),
                'attachment_count': attachment_count
            })
            
            # Update stats
            stats = self.get_current_stats()
            self.emit_update('stats_update', stats)
            
            self.last_check_time = local_date
            return True
            
        except Exception as e:
            print(f"✗ Error saving email: {str(e)}")
            return False
    
    def get_current_stats(self):
        """Get current email statistics"""
        try:
            email_rows = self.db_service.get_all_emails()
            total_emails = len(email_rows)
            emails_with_attachments = sum(1 for row in email_rows if row[4])
            
            return {
                'total_emails': total_emails,
                'emails_with_attachments': emails_with_attachments,
                'monitoring_status': 'Active' if self.is_connected else 'Disconnected',
                'last_updated': datetime.now().strftime('%H:%M:%S')
            }
        except Exception:
            return {
                'total_emails': 0,
                'emails_with_attachments': 0,
                'monitoring_status': 'Error',
                'last_updated': datetime.now().strftime('%H:%M:%S')
            }
    
    def process_emails(self):
        """Main email processing loop"""
        self._running = True
        
        if self.last_check_time is None:
            self.last_check_time = self.get_last_email_date()
            print(f"Starting email monitoring from: {self.last_check_time}")
        
        while self._running:
            try:
                if not self.is_connected:
                    if not self.connect_to_imap():
                        if self.error_count >= Config.MAX_RETRIES:
                            print(f"Max retries ({Config.MAX_RETRIES}) reached. Waiting {Config.RETRY_DELAY} seconds...")
                            time.sleep(Config.RETRY_DELAY)
                            self.error_count = 0
                        time.sleep(5)
                        continue

                print(f"\nChecking for emails since: {self.last_check_time}")
                
                # Emit checking status
                self.emit_update('status_update', {
                    'type': 'checking',
                    'status': 'checking',
                    'message': 'Checking for new emails...',
                    'last_check': self.last_check_time.strftime('%H:%M:%S')
                })
                
                search_date = self.last_check_time.date()
                criteria = AND(date_gte=search_date)
                
                all_emails = list(self.mailbox.fetch(criteria, reverse=True))
                
                new_emails = []
                processed_count = 0
                
                for msg in all_emails:
                    email_time = msg.date.astimezone(Config.TIMEZONE)
                    if email_time > self.last_check_time:
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
                    status_msg = f"No new emails found ({processed_count} already processed)" if processed_count > 0 else "No new emails found"
                    print(status_msg)
                    
                    self.emit_update('status_update', {
                        'type': 'check_complete',
                        'status': 'active',
                        'message': status_msg
                    })
                
                time.sleep(Config.CHECK_INTERVAL)
                
            except Exception as e:
                print(f"✗ Error in main loop: {str(e)}")
                self.is_connected = False
                self.emit_update('status_update', {
                    'type': 'error',
                    'status': 'error',
                    'message': f'Error in main loop: {str(e)}'
                })
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