from flask import Blueprint, jsonify, send_file
import io
from app.services.db import DatabaseService
from app.models.email_model import Email, Attachment

email_bp = Blueprint('emails', __name__, url_prefix='/api')
db_service = DatabaseService()

@email_bp.route('/emails', methods=['GET'])
def get_emails():
    """Get all emails with attachment information"""
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
            ).__dict__
            for row in email_rows
        ]
        
        return jsonify({'emails': emails})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@email_bp.route('/emails/<int:email_id>/attachments', methods=['GET'])
def get_attachments(email_id):
    """Get attachments for a specific email"""
    try:
        attachment_rows = db_service.get_email_attachments(email_id)
        
        attachments = [
            Attachment(
                id=row[0],
                filename=row[1],
                email_id=email_id
            ).__dict__
            for row in attachment_rows
        ]
        
        return jsonify({'attachments': attachments})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@email_bp.route('/attachments/<int:attachment_id>/download', methods=['GET'])
def download_attachment(attachment_id):
    """Download a specific attachment"""
    try:
        result = db_service.get_attachment(attachment_id)
        
        if result is None:
            return jsonify({'error': 'Attachment not found'}), 404
            
        filename, content = result
        
        return send_file(
            io.BytesIO(content),
            download_name=filename,
            as_attachment=True
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@email_bp.route('/attachments/<int:attachment_id>/view', methods=['GET'])
def view_attachment(attachment_id):
    """View a specific attachment inline (for images, PDFs, etc.)"""
    try:
        result = db_service.get_attachment(attachment_id)
        
        if result is None:
            return jsonify({'error': 'Attachment not found'}), 404
            
        filename, content = result
        
        # Determine content type based on file extension
        import mimetypes
        content_type, _ = mimetypes.guess_type(filename)
        
        if content_type is None:
            content_type = 'application/octet-stream'
        
        return send_file(
            io.BytesIO(content),
            mimetype=content_type,
            as_attachment=False,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@email_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'email-tracker'})