"""
Building Model
"""
from sqlalchemy import Column, String, Enum, Text, Integer, Numeric, Boolean, DateTime, ForeignKey, Index, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.database import Base


class Building(Base):
    """Building model - Physical buildings within a project"""
    __tablename__ = "buildings"
    
    building_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.project_id'), nullable=False)
    building_name = Column(String(255), nullable=False)
    building_code = Column(String(50))
    address = Column(Text)
    coordinates = Column(String(100))  # Simplified for Phase 1
    floor_count = Column(Integer)
    total_units = Column(Integer)
    total_area_sqm = Column(Numeric(10, 2))
    construction_year = Column(Integer)
    structure_type = Column(Enum('CONCRETE', 'MASONRY', 'MIXED', 'OTHER', name='structure_type'))
    seismic_rating = Column(Enum('UNSAFE', 'REQUIRES_REINFORCEMENT', 'REINFORCED', 'MODERN', name='seismic_rating'))
    current_status = Column(Enum('INITIAL', 'NEGOTIATING', 'APPROVED', 'RENOVATION_PLANNING', 'RENOVATION_ONGOING', 'COMPLETED', name='building_status'), default='INITIAL')
    signature_percentage = Column(Numeric(5, 2), default=0)
    signature_percentage_by_area = Column(Numeric(5, 2), default=0)
    signature_percentage_by_cost = Column(Numeric(5, 2), default=0)
    traffic_light_status = Column(Enum('GREEN', 'YELLOW', 'RED', 'GRAY', name='traffic_light'), default='GRAY')
    units_signed = Column(Integer, default=0)
    units_partially_signed = Column(Integer, default=0)
    units_not_signed = Column(Integer, default=0)
    units_refused = Column(Integer, default=0)
    estimated_bonus_ils = Column(Numeric(15, 2))
    actual_bonus_ils = Column(Numeric(15, 2))
    assigned_agent_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    secondary_agent_ids = Column(ARRAY(UUID(as_uuid=True)))
    inspector_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    difficulty_score = Column(Integer)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    project = relationship("Project", back_populates="buildings")
    units = relationship("Unit", back_populates="building", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_buildings_project_id', 'project_id'),
        Index('idx_buildings_status', 'current_status'),
        Index('idx_buildings_signature_pct', 'signature_percentage'),
        Index('idx_buildings_traffic_light', 'traffic_light_status'),
    )

