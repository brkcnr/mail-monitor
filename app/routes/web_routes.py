from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app.services.db import DatabaseService
from app.models.email_model import Email, Attachment
from app.config import Config

web_bp = Blueprint('web', __name__)
db_service = DatabaseService()

@web_bp.route('/')
def index():
    """Home page with dashboard"""
    try:
        # Get email statistics
        email_rows = db_service.get_all_emails()
        total_emails = len(email_rows)
        emails_with_attachments = sum(1 for row in email_rows if row[4])  # has_attachment column
        
        # Get recent emails (last 5)
        recent_emails = email_rows[:5] if email_rows else []
        
        stats = {
            'total_emails': total_emails,
            'emails_with_attachments': emails_with_attachments,
            'recent_emails_count': len(recent_emails)
        }
        
        return render_template('index.html', stats=stats, recent_emails=recent_emails)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('index.html', stats={}, recent_emails=[])

@web_bp.route('/emails')
def emails_page():
    """Email list page"""
    try:
        email_rows = db_service.get_all_emails()
        
        emails = [
            Email(
                id=row[0],
                sender=row[1],
                subject=row[2],
                received_date=row[3],
                has_attachment=row[4],
                attachment_count=row[5]
            )
            for row in email_rows
        ]
        
        return render_template('emails.html', emails=emails)
    except Exception as e:
        flash(f'Error loading emails: {str(e)}', 'error')
        return render_template('emails.html', emails=[])

@web_bp.route('/emails/<int:email_id>')
def email_detail(email_id):
    """Email detail page"""
    try:
        # Get email details
        with db_service.get_connection() as conn:
            c = conn.cursor()
            c.execute('''
                SELECT id, message_id, sender, subject, body, received_date, has_attachment
                FROM emails WHERE id = ?
            ''', (email_id,))
            email_row = c.fetchone()
        
        if not email_row:
            flash('Email not found', 'error')
            return redirect(url_for('web.emails_page'))
        
        email = Email(
            id=email_row[0],
            message_id=email_row[1],
            sender=email_row[2],
            subject=email_row[3],
            body=email_row[4],
            received_date=email_row[5],
            has_attachment=email_row[6]
        )
        
        # Get attachments if any
        attachments = []
        if email.has_attachment:
            attachment_rows = db_service.get_email_attachments(email_id)
            attachments = [
                Attachment(id=row[0], filename=row[1], email_id=email_id)
                for row in attachment_rows
            ]
        
        return render_template('email_detail.html', email=email, attachments=attachments)
    except Exception as e:
        flash(f'Error loading email details: {str(e)}', 'error')
        return redirect(url_for('web.emails_page'))

@web_bp.route('/stats')
def get_stats():
    """API endpoint for live stats (for AJAX updates)"""
    try:
        email_rows = db_service.get_all_emails()
        total_emails = len(email_rows)
        emails_with_attachments = sum(1 for row in email_rows if row[4])
        
        return jsonify({
            'total_emails': total_emails,
            'emails_with_attachments': emails_with_attachments,
            'monitoring_status': 'Active',
            'last_updated': 'Just now'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500