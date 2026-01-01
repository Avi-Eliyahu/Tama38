"""
Unit Model
"""
from sqlalchemy import Column, String, Enum, Text, Integer, SmallInteger, Numeric, Boolean, Date, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.database import Base


class Unit(Base):
    """Unit model - Individual apartments/properties"""
    __tablename__ = "units"
    
    unit_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    building_id = Column(UUID(as_uuid=True), ForeignKey('buildings.building_id'), nullable=False)
    floor_number = Column(SmallInteger)
    unit_number = Column(String(10), nullable=False)
    unit_code = Column(String(50))
    unit_full_identifier = Column(String(50))  # Computed: "Floor-Unit"
    area_sqm = Column(Numeric(8, 2))
    room_count = Column(SmallInteger)
    estimated_value_ils = Column(Numeric(12, 2))
    estimated_renovation_cost_ils = Column(Numeric(12, 2))
    unit_status = Column(Enum('NOT_CONTACTED', 'NEGOTIATING', 'AGREED_TO_SIGN', 'SIGNED', 'FINALIZED', 'REFUSED', 'INACTIVE', name='unit_status'), default='NOT_CONTACTED')
    total_owners = Column(Integer, default=0)
    owners_signed = Column(Integer, default=0)
    signature_percentage = Column(Numeric(5, 2), default=0)
    is_co_owned = Column(Boolean, default=False)
    is_rented = Column(Boolean, default=False)
    tenant_name = Column(String(255))
    first_contact_date = Column(Date)
    last_contact_date = Column(Date)
    last_activity_timestamp = Column(DateTime)
    days_since_contact = Column(Integer)
    primary_contract_id = Column(UUID(as_uuid=True), ForeignKey('documents.document_id'))
    renovation_plan_document_id = Column(UUID(as_uuid=True), ForeignKey('documents.document_id'))
    complexity_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    building = relationship("Building", back_populates="units")
    owners = relationship("Owner", back_populates="unit", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_units_building_id', 'building_id'),
        Index('idx_units_status', 'unit_status'),
    )

