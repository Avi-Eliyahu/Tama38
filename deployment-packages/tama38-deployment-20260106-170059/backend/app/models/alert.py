"""
Alert Models
"""
from sqlalchemy import Column, String, Enum, Text, Boolean, DateTime, ForeignKey, Index, JSON, Numeric
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.database import Base


class AlertRule(Base):
    """Alert Rule model - Configurable alert rules"""
    __tablename__ = "alert_rules"
    
    rule_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_name = Column(String(255), nullable=False)
    rule_type = Column(Enum(
        'THRESHOLD_VIOLATION',
        'AGENT_INACTIVITY',
        'OVERDUE_TASK',
        'PENDING_APPROVAL',
        'OWNERSHIP_TRANSFER',
        'SYSTEM_ERROR',
        name='alert_rule_type'
    ), nullable=False)
    condition_logic = Column(JSON)  # JSON structure for rule conditions
    severity = Column(Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='alert_severity'), default='MEDIUM')
    delivery_channels = Column(ARRAY(String))  # ['IN_APP', 'EMAIL', 'SMS', 'WHATSAPP']
    is_active = Column(Boolean, default=True)
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_alert_rules_type', 'rule_type'),
        Index('idx_alert_rules_active', 'is_active'),
    )


class Alert(Base):
    """Alert model - Generated alerts"""
    __tablename__ = "alerts"
    
    alert_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(UUID(as_uuid=True), ForeignKey('alert_rules.rule_id'), nullable=True)
    alert_type = Column(Enum(
        'THRESHOLD_VIOLATION',
        'AGENT_INACTIVITY',
        'OVERDUE_TASK',
        'PENDING_APPROVAL',
        'OWNERSHIP_TRANSFER',
        'SYSTEM_ERROR',
        name='alert_type'
    ), nullable=False)
    severity = Column(Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='alert_severity'), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Related entity references
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.project_id'), nullable=True)
    building_id = Column(UUID(as_uuid=True), ForeignKey('buildings.building_id'), nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('owners.owner_id'), nullable=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.task_id'), nullable=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=True)
    
    # Alert metadata
    alert_metadata = Column(JSON)  # Additional context data
    status = Column(Enum('ACTIVE', 'ACKNOWLEDGED', 'RESOLVED', 'DISMISSED', name='alert_status'), default='ACTIVE')
    
    # User actions
    acknowledged_by_user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_by_user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text)
    
    # Delivery tracking
    delivery_channels = Column(ARRAY(String))  # Channels used to deliver this alert
    delivered_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    rule = relationship("AlertRule", backref="alerts")
    project = relationship("Project", backref="alerts")
    building = relationship("Building", backref="alerts")
    owner = relationship("Owner", backref="alerts")
    task = relationship("Task", backref="alerts")
    agent = relationship("User", foreign_keys=[agent_id], backref="agent_alerts")
    acknowledged_by = relationship("User", foreign_keys=[acknowledged_by_user_id], backref="acknowledged_alerts")
    resolved_by = relationship("User", foreign_keys=[resolved_by_user_id], backref="resolved_alerts")
    
    # Indexes
    __table_args__ = (
        Index('idx_alerts_status', 'status'),
        Index('idx_alerts_type', 'alert_type'),
        Index('idx_alerts_severity', 'severity'),
        Index('idx_alerts_created', 'created_at'),
        Index('idx_alerts_project', 'project_id'),
        Index('idx_alerts_building', 'building_id'),
        Index('idx_alerts_agent', 'agent_id'),
    )

