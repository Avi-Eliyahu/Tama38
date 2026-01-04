"""
Document Model
"""
from sqlalchemy import Column, String, Enum, Text, Integer, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.database import Base


class Document(Base):
    """Document model - Stored documents and files"""
    __tablename__ = "documents"
    
    document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('owners.owner_id'))
    building_id = Column(UUID(as_uuid=True), ForeignKey('buildings.building_id'))
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.project_id'))
    document_type = Column(Enum('CONTRACT', 'ID_CARD', 'SIGNATURE', 'RENOVATION_PLAN', 'PERMIT', 'OTHER', name='document_type'), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # Local path in Phase 1, S3 key in Phase 2
    file_size_bytes = Column(Integer)
    mime_type = Column(String(100))
    description = Column(Text)
    version = Column(Integer, default=1)
    is_current_version = Column(Boolean, default=True)
    uploaded_by_user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    signatures = relationship("DocumentSignature", back_populates="document", foreign_keys="DocumentSignature.document_id")
    
    # Indexes
    __table_args__ = (
        Index('idx_documents_owner_id', 'owner_id'),
        Index('idx_documents_type', 'document_type'),
    )


class DocumentSignature(Base):
    """Document Signature model - Tracks signature workflow"""
    __tablename__ = "document_signatures"
    
    signature_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.document_id'), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('owners.owner_id'), nullable=False)
    signature_status = Column(Enum('WAIT_FOR_SIGN', 'SIGNED_PENDING_APPROVAL', 'FINALIZED', 'REJECTED', name='signature_status'), nullable=False, default='WAIT_FOR_SIGN')
    signing_token = Column(String(255), unique=True)  # Token for signing link
    signature_data = Column(Text)  # Base64 signature image/data
    signed_at = Column(DateTime)
    signed_document_id = Column(UUID(as_uuid=True), ForeignKey('documents.document_id'), nullable=True)  # Link to uploaded signed contract document
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.task_id'), nullable=True)  # Link to approval task
    approved_by_user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    approved_at = Column(DateTime)
    approval_reason = Column(Text)  # Required for approval
    rejected_by_user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    rejected_at = Column(DateTime)
    rejection_reason = Column(Text)
    is_manual_override = Column(Boolean, default=False)
    manual_override_reason = Column(Text)  # Required for manual override
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="signatures", foreign_keys="[DocumentSignature.document_id]")
    
    # Indexes
    __table_args__ = (
        Index('idx_signatures_owner_id', 'owner_id'),
        Index('idx_signatures_status', 'signature_status'),
        Index('idx_signatures_token', 'signing_token'),
    )

