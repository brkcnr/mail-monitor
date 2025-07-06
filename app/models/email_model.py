from dataclasses import dataclass
from typing import Optional

@dataclass
class Email:
    """Email data model"""
    id: Optional[int] = None
    message_id: Optional[str] = None
    sender: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    received_date: Optional[str] = None
    has_attachment: bool = False
    attachment_count: int = 0

@dataclass
class Attachment:
    """Attachment data model"""
    id: Optional[int] = None
    email_id: Optional[int] = None
    filename: Optional[str] = None
    content: Optional[bytes] = None