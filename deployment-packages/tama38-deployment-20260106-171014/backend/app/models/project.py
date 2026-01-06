"""
Project Model
"""
from sqlalchemy import Column, String, Enum, Text, Date, DateTime, Numeric, Boolean, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.database import Base


class Project(Base):
    """Project model - Top-level container for TAMA 38 urban renewal initiatives"""
    __tablename__ = "projects"
    
    project_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_name = Column(String(255), nullable=False, unique=True)
    project_code = Column(String(50), nullable=False, unique=True)
    project_type = Column(Enum('TAMA38_1', 'TAMA38_2', 'PINUI_BINUI', name='project_type'), nullable=False)
    location_city = Column(String(100))
    location_address = Column(Text)
    location_coordinates = Column(String(100))  # Simplified for Phase 1 (POINT in Phase 2)
    description = Column(Text)
    project_stage = Column(Enum('PLANNING', 'ACTIVE', 'APPROVAL', 'COMPLETED', 'ARCHIVED', name='project_stage'), default='PLANNING')
    budget_total_ils = Column(Numeric(15, 2))
    budget_consumed_ils = Column(Numeric(15, 2), default=0)
    required_majority_percent = Column(Numeric(5, 2), nullable=False)
    majority_calc_type = Column(Enum('HEADCOUNT', 'AREA', 'WEIGHTED', 'CUSTOM', name='majority_calc_type'), nullable=False)
    critical_threshold_percent = Column(Numeric(5, 2), nullable=False)
    launch_date = Column(Date)
    estimated_completion_date = Column(Date)
    actual_completion_date = Column(Date)
    business_sponsor = Column(String(255))
    project_manager_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    is_template = Column(Boolean, default=False)
    custom_config = Column(JSON)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    buildings = relationship("Building", back_populates="project", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_projects_city', 'location_city'),
        Index('idx_projects_status', 'project_stage'),
        Index('idx_projects_created_by', 'created_by'),
    )

