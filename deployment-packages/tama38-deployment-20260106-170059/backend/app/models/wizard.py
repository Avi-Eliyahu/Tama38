"""
Wizard Draft Model
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timedelta
from app.core.database import Base


class WizardDraft(Base):
    """Wizard Draft model - Temporary storage for incomplete wizard sessions"""
    __tablename__ = "wizard_drafts"
    
    draft_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    step_data = Column(JSON)  # Store all step data as JSON
    current_step = Column(Integer, default=1)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=7))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_completed = Column(Boolean, default=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_wizard_drafts_user_id', 'user_id'),
        Index('idx_wizard_drafts_expires', 'expires_at'),
    )

