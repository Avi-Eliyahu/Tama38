"""
Task Model
"""
from sqlalchemy import Column, String, Enum, Text, Date, Time, Numeric, Boolean, DateTime, ForeignKey, Index, ARRAY
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.database import Base


class Task(Base):
    """Task model - Agent action items and follow-ups"""
    __tablename__ = "tasks"
    
    task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    building_id = Column(UUID(as_uuid=True), ForeignKey('buildings.building_id'))
    owner_id = Column(UUID(as_uuid=True), ForeignKey('owners.owner_id'))
    task_type = Column(Enum('FOLLOW_UP_CALL', 'SCHEDULE_MEETING', 'SEND_DOCUMENT', 'MANAGER_REVIEW', 'SITE_VISIT', 'HANDLE_OBJECTION', name='task_type'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    assigned_to_agent_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    assigned_by_user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    due_date = Column(Date)
    due_time = Column(Time)
    status = Column(Enum('NOT_STARTED', 'IN_PROGRESS', 'BLOCKED', 'COMPLETED', 'OVERDUE', 'CANCELLED', name='task_status'), default='NOT_STARTED')
    priority = Column(Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='priority'), default='MEDIUM')
    estimated_hours = Column(Numeric(4, 2))
    actual_hours = Column(Numeric(4, 2))
    dependencies = Column(ARRAY(UUID(as_uuid=True)))  # Task IDs that must be completed first
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    notes = Column(Text)
    
    # Indexes
    __table_args__ = (
        Index('idx_tasks_assigned_to', 'assigned_to_agent_id'),
        Index('idx_tasks_status', 'status'),
        Index('idx_tasks_due_date', 'due_date'),
    )

