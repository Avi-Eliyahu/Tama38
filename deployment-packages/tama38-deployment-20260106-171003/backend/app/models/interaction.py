"""
Interaction Model
"""
from sqlalchemy import Column, String, Enum, Text, Integer, Boolean, Date, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.database import Base


class Interaction(Base):
    """Interaction model - Audit trail of all agent-owner contacts"""
    __tablename__ = "interactions_log"
    
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('owners.owner_id'), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    interaction_type = Column(Enum('PHONE_CALL', 'IN_PERSON_MEETING', 'WHATSAPP', 'EMAIL', 'SMS', 'VIDEO_CALL', 'SCHEDULED_MEETING', name='interaction_type'), nullable=False)
    interaction_date = Column(Date, nullable=False)
    interaction_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    duration_minutes = Column(Integer)
    outcome = Column(Enum('POSITIVE', 'NEUTRAL', 'NEGATIVE', 'NOT_AVAILABLE', 'DECLINED', 'AGREED_TO_MEET', 'AGREED_TO_SIGN', name='outcome'))
    call_summary = Column(Text, nullable=False)  # Mandatory
    key_objection = Column(String(255))
    next_action = Column(String(500))
    next_follow_up_date = Column(Date)
    follow_up_type = Column(Enum('REMINDER_CALL', 'MEETING', 'SEND_DOCUMENT', 'FOLLOW_WITH_MANAGER', name='follow_up_type'))
    sentiment = Column(Enum('VERY_POSITIVE', 'POSITIVE', 'NEUTRAL', 'NEGATIVE', 'VERY_NEGATIVE', name='sentiment'))
    is_escalated = Column(Boolean, default=False)
    escalation_reason = Column(Text)
    attempted = Column(Boolean, default=True)
    contact_method_used = Column(Enum('PHONE', 'WHATSAPP', 'EMAIL', 'IN_PERSON', name='contact_method'))
    source = Column(Enum('MOBILE_APP', 'WEB_APP', 'MANUAL_ENTRY', 'CRM_INTEGRATION', name='source'), default='WEB_APP')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_interactions_owner_id', 'owner_id'),
        Index('idx_interactions_agent_id', 'agent_id'),
        Index('idx_interactions_date', 'interaction_date'),
        Index('idx_interactions_outcome', 'outcome'),
    )

