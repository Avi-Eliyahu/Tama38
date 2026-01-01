"""
Approval Workflow API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.core.database import get_db
from app.models.user import User
from app.models.document import DocumentSignature, Document
from app.models.owner import Owner
from app.api.dependencies import get_current_user, require_role
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/approvals", tags=["approvals"])


class SignatureInitiate(BaseModel):
    owner_id: str
    document_id: str


class SignatureSign(BaseModel):
    signing_token: str
    signature_data: str  # Base64 encoded signature image


class ApprovalRequest(BaseModel):
    reason: str  # Required for approval


class SignatureResponse(BaseModel):
    signature_id: str
    document_id: str
    owner_id: str
    signature_status: str
    signing_token: Optional[str]
    signed_at: Optional[datetime]
    approved_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class SigningTokenInfo(BaseModel):
    """Public endpoint response for token validation"""
    signature_id: str
    document_id: str
    owner_id: str
    owner_name: str
    document_name: str
    document_type: str
    signature_status: str
    is_valid: bool


@router.post("/signatures/initiate", response_model=SignatureResponse, status_code=status.HTTP_201_CREATED)
async def initiate_signature(
    signature_data: SignatureInitiate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Initiate signing process (creates signature with WAIT_FOR_SIGN status)"""
    # Verify owner exists
    owner = db.query(Owner).filter(
        Owner.owner_id == signature_data.owner_id,
        Owner.is_deleted == False
    ).first()
    
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found"
        )
    
    # Generate signing token
    signing_token = str(uuid.uuid4())
    
    signature = DocumentSignature(
        document_id=UUID(signature_data.document_id),
        owner_id=UUID(signature_data.owner_id),
        signature_status="WAIT_FOR_SIGN",
        signing_token=signing_token,
    )
    
    db.add(signature)
    
    # Update owner status
    owner.owner_status = "WAIT_FOR_SIGN"
    owner.signature_session_id = signature.signature_id
    
    db.commit()
    db.refresh(signature)
    
    logger.info(
        "Signature initiated",
        extra={
            "signature_id": str(signature.signature_id),
            "owner_id": str(signature.owner_id),
            "document_id": str(signature.document_id),
        }
    )
    
    # Convert UUIDs to strings for response
    return SignatureResponse(
        signature_id=str(signature.signature_id),
        document_id=str(signature.document_id),
        owner_id=str(signature.owner_id),
        signature_status=signature.signature_status,
        signing_token=signature.signing_token,
        signed_at=signature.signed_at,
        approved_at=signature.approved_at,
        created_at=signature.created_at,
    )


@router.get("/signatures/waiting", response_model=List[SignatureResponse])
async def get_waiting_signatures(
    owner_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get signatures waiting for owner to sign"""
    query = db.query(DocumentSignature).filter(
        DocumentSignature.signature_status == "WAIT_FOR_SIGN"
    )
    
    if owner_id:
        query = query.filter(DocumentSignature.owner_id == owner_id)
    
    signatures = query.order_by(desc(DocumentSignature.created_at)).offset(skip).limit(limit).all()
    # Convert UUIDs to strings for response
    return [
        SignatureResponse(
            signature_id=str(s.signature_id),
            document_id=str(s.document_id),
            owner_id=str(s.owner_id),
            signature_status=s.signature_status,
            signing_token=s.signing_token,
            signed_at=s.signed_at,
            approved_at=s.approved_at,
            created_at=s.created_at,
        )
        for s in signatures
    ]


@router.get("/sign/validate/{token}", response_model=SigningTokenInfo)
async def validate_signing_token(
    token: str,
    db: Session = Depends(get_db)
):
    """Public endpoint to validate signing token and get signature details (no auth required)"""
    signature = db.query(DocumentSignature).filter(
        DocumentSignature.signing_token == token
    ).first()
    
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired signing token"
        )
    
    if signature.signature_status != "WAIT_FOR_SIGN":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Signature is not available for signing. Current status: {signature.signature_status}"
        )
    
    # Get document and owner details
    document = db.query(Document).filter(Document.document_id == signature.document_id).first()
    owner = db.query(Owner).filter(Owner.owner_id == signature.owner_id).first()
    
    if not document or not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document or owner not found"
        )
    
    return SigningTokenInfo(
        signature_id=str(signature.signature_id),
        document_id=str(signature.document_id),
        owner_id=str(signature.owner_id),
        owner_name=owner.full_name,
        document_name=document.file_name,
        document_type=document.document_type,
        signature_status=signature.signature_status,
        is_valid=True,
    )


@router.post("/sign/{token}", response_model=SignatureResponse)
async def sign_document_by_token(
    token: str,
    sign_data: SignatureSign,
    db: Session = Depends(get_db)
):
    """Public endpoint for owner to sign document using token (no auth required)"""
    signature = db.query(DocumentSignature).filter(
        DocumentSignature.signing_token == token
    ).first()
    
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired signing token"
        )
    
    if signature.signature_status != "WAIT_FOR_SIGN":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Signature is not in WAIT_FOR_SIGN status. Current status: {signature.signature_status}"
        )
    
    if signature.signing_token != sign_data.signing_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signing token"
        )
    
    # Update signature
    signature.signature_status = "SIGNED_PENDING_APPROVAL"
    signature.signature_data = sign_data.signature_data
    signature.signed_at = datetime.utcnow()
    
    # Update owner status
    owner = db.query(Owner).filter(Owner.owner_id == signature.owner_id).first()
    if owner:
        owner.owner_status = "SIGNED"
        owner.signature_date = datetime.utcnow().date()
    
    db.commit()
    db.refresh(signature)
    
    logger.info(
        "Document signed via token",
        extra={
            "signature_id": str(signature.signature_id),
            "owner_id": str(signature.owner_id),
        }
    )
    
    # Convert UUIDs to strings for response
    return SignatureResponse(
        signature_id=str(signature.signature_id),
        document_id=str(signature.document_id),
        owner_id=str(signature.owner_id),
        signature_status=signature.signature_status,
        signing_token=signature.signing_token,
        signed_at=signature.signed_at,
        approved_at=signature.approved_at,
        created_at=signature.created_at,
    )


@router.get("/queue", response_model=List[SignatureResponse])
async def get_approval_queue(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SUPER_ADMIN", "PROJECT_MANAGER"))
):
    """Get approval queue (signatures pending manager approval)"""
    signatures = db.query(DocumentSignature).filter(
        DocumentSignature.signature_status == "SIGNED_PENDING_APPROVAL"
    ).order_by(desc(DocumentSignature.signed_at)).offset(skip).limit(limit).all()
    
    # Convert UUIDs to strings for response
    return [
        SignatureResponse(
            signature_id=str(s.signature_id),
            document_id=str(s.document_id),
            owner_id=str(s.owner_id),
            signature_status=s.signature_status,
            signing_token=s.signing_token,
            signed_at=s.signed_at,
            approved_at=s.approved_at,
            created_at=s.created_at,
        )
        for s in signatures
    ]


@router.post("/{signature_id}/approve", response_model=SignatureResponse)
async def approve_signature(
    signature_id: UUID,
    approval_data: ApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SUPER_ADMIN", "PROJECT_MANAGER"))
):
    """Manager approves signature (changes status to FINALIZED)"""
    if not approval_data.reason or len(approval_data.reason.strip()) < 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval reason is required and must be at least 20 characters"
        )
    
    signature = db.query(DocumentSignature).filter(
        DocumentSignature.signature_id == signature_id
    ).first()
    
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signature not found"
        )
    
    if signature.signature_status != "SIGNED_PENDING_APPROVAL":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Signature is not pending approval. Current status: {signature.signature_status}"
        )
    
    # Approve signature
    signature.signature_status = "FINALIZED"
    signature.approved_by_user_id = current_user.user_id
    signature.approved_at = datetime.utcnow()
    signature.approval_reason = approval_data.reason
    
    # Update owner status
    owner = db.query(Owner).filter(Owner.owner_id == signature.owner_id).first()
    if owner:
        owner.owner_status = "SIGNED"
    
    db.commit()
    
    # Trigger majority recalculation
    from app.services.majority import calculate_building_majority
    from app.models.unit import Unit
    owner = db.query(Owner).filter(Owner.owner_id == signature.owner_id).first()
    if owner:
        unit = db.query(Unit).filter(Unit.unit_id == owner.unit_id).first()
        if unit:
            try:
                calculate_building_majority(str(unit.building_id), db)
            except Exception as e:
                logger.error(f"Failed to recalculate majority: {e}")
    
    logger.info(
        "Signature approved",
        extra={
            "signature_id": str(signature.signature_id),
            "approved_by": str(current_user.user_id),
            "reason": approval_data.reason[:50],
        }
    )
    
    db.refresh(signature)
    # Convert UUIDs to strings for response
    return SignatureResponse(
        signature_id=str(signature.signature_id),
        document_id=str(signature.document_id),
        owner_id=str(signature.owner_id),
        signature_status=signature.signature_status,
        signing_token=signature.signing_token,
        signed_at=signature.signed_at,
        approved_at=signature.approved_at,
        created_at=signature.created_at,
    )


@router.post("/{signature_id}/reject", response_model=SignatureResponse)
async def reject_signature(
    signature_id: UUID,
    rejection_data: ApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SUPER_ADMIN", "PROJECT_MANAGER"))
):
    """Manager rejects signature (returns to WAIT_FOR_SIGN)"""
    signature = db.query(DocumentSignature).filter(
        DocumentSignature.signature_id == signature_id
    ).first()
    
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signature not found"
        )
    
    signature.signature_status = "WAIT_FOR_SIGN"
    signature.rejected_by_user_id = current_user.user_id
    signature.rejected_at = datetime.utcnow()
    signature.rejection_reason = rejection_data.reason
    
    # Update owner status
    owner = db.query(Owner).filter(Owner.owner_id == signature.owner_id).first()
    if owner:
        owner.owner_status = "WAIT_FOR_SIGN"
    
    db.commit()
    db.refresh(signature)
    
    # Convert UUIDs to strings for response
    return SignatureResponse(
        signature_id=str(signature.signature_id),
        document_id=str(signature.document_id),
        owner_id=str(signature.owner_id),
        signature_status=signature.signature_status,
        signing_token=signature.signing_token,
        signed_at=signature.signed_at,
        approved_at=signature.approved_at,
        created_at=signature.created_at,
    )

