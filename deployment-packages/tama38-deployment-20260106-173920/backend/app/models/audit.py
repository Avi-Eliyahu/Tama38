"""
Audit Log Model
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.database import Base


class AuditLog(Base):
    """Audit Log model - Comprehensive audit trail"""
    __tablename__ = "audit_log_extended"
    
    audit_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_name = Column(String(100), nullable=False)
    record_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String(50), nullable=False)  # INSERT, UPDATE, DELETE, MANUAL_OVERRIDE
    old_values = Column(JSON)
    new_values = Column(JSON)
    changed_by_user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reason_text = Column(Text)  # Required for manual overrides
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    request_id = Column(String(255))  # Request ID for tracing
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_table_record', 'table_name', 'record_id'),
        Index('idx_audit_user', 'changed_by_user_id'),
        Index('idx_audit_date', 'changed_at'),
        Index('idx_audit_request_id', 'request_id'),
    )

