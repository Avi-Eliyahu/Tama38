"""
Owner Model
"""
from sqlalchemy import Column, String, Enum, Text, Numeric, Boolean, Date, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, BYTEA
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.database import Base


class Owner(Base):
    """Owner model - Legal entities with ownership stakes in units"""
    __tablename__ = "owners"
    
    owner_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unit_id = Column(UUID(as_uuid=True), ForeignKey('units.unit_id'), nullable=False)
    full_name = Column(String(255), nullable=False)  # Encrypted PII in Phase 2
    id_number_encrypted = Column(BYTEA)  # Encrypted in Phase 2
    id_number_hash = Column(BYTEA)  # Hash for lookups
    id_type = Column(Enum('ISRAELI_ID', 'PASSPORT', 'BUSINESS_ID', 'OTHER', name='id_type'))
    date_of_birth = Column(Date)  # Encrypted in Phase 2
    phone_encrypted = Column(BYTEA)  # Encrypted in Phase 2
    phone_hash = Column(BYTEA)  # Hash for lookups
    phone_for_contact = Column(String(20))  # Masked phone for display
    email = Column(String(255))
    preferred_contact_method = Column(Enum('PHONE', 'WHATSAPP', 'EMAIL', 'IN_PERSON', 'NONE', name='contact_method'))
    preferred_language = Column(Enum('HEBREW', 'ARABIC', 'RUSSIAN', 'ENGLISH', 'OTHER', name='language'))
    accessibility_needs = Column(Text)
    is_elderly = Column(Boolean, default=False)
    is_vulnerable = Column(Boolean, default=False)
    ownership_share_percent = Column(Numeric(5, 2), nullable=False)
    ownership_type = Column(Enum('SOLE_OWNER', 'CO_OWNER_JOINT', 'CO_OWNER_SEPARATE', 'TENANT_REPRESENTATIVE', name='ownership_type'))
    is_primary_contact = Column(Boolean, default=False)
    owner_status = Column(Enum('NOT_CONTACTED', 'PENDING_SIGNATURE', 'NEGOTIATING', 'AGREED_TO_SIGN', 'WAIT_FOR_SIGN', 'SIGNED', 'REFUSED', 'DECEASED', 'INCAPACITATED', name='owner_status'), default='NOT_CONTACTED')
    refusal_reason = Column(Enum('NOT_INTERESTED', 'PRICE_OBJECTION', 'LEGAL_DISPUTE', 'NO_CONSENSUS_WITH_CO_OWNER', 'OTHER', name='refusal_reason'))
    refusal_reason_detail = Column(Text)
    signature_date = Column(Date)
    signature_session_id = Column(UUID(as_uuid=True), ForeignKey('document_signatures.signature_id'))
    assigned_agent_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    is_current_owner = Column(Boolean, default=True)
    ownership_start_date = Column(Date)
    ownership_end_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    unit = relationship("Unit", back_populates="owners")
    
    # Indexes
    __table_args__ = (
        Index('idx_owners_unit_id', 'unit_id'),
        Index('idx_owners_status', 'owner_status'),
        Index('idx_owners_agent', 'assigned_agent_id'),
    )

