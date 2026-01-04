"""
Approval Workflow API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from pathlib import Path
from app.core.database import get_db
from app.core.config import settings
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
    reason: Optional[str] = None  # Optional for approval, required for rejection


class SignatureResponse(BaseModel):
    signature_id: str
    document_id: str
    owner_id: str
    signature_status: str
    signing_token: Optional[str]
    signed_at: Optional[datetime]
    approved_at: Optional[datetime]
    created_at: datetime
    task_id: Optional[str] = None
    signed_document_id: Optional[str] = None
    signed_document_name: Optional[str] = None
    
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
    owner_id: str = Form(...),
    document_id: str = Form(...),
    signed_document: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Initiate signing process (creates signature with WAIT_FOR_SIGN status)
    
    Optionally accepts a signed document file upload for manual/paper signatures.
    """
    # Verify owner exists
    owner = db.query(Owner).filter(
        Owner.owner_id == UUID(owner_id),
        Owner.is_deleted == False
    ).first()
    
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found"
        )
    
    # Handle signed document upload if provided
    signed_document_id = None
    signed_document_name = None
    if signed_document:
        # Validate file type and size
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
        if signed_document.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {allowed_types}"
            )
        
        # Max file size: 10MB
        max_size = 10 * 1024 * 1024
        file_content = await signed_document.read()
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 10MB limit"
            )
        
        # Create storage directory if it doesn't exist
        storage_path = Path(settings.STORAGE_PATH) / "documents"
        storage_path.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_uuid = uuid.uuid4()
        file_extension = Path(signed_document.filename).suffix
        file_path = storage_path / f"{file_uuid}{file_extension}"
        
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Create Document record for signed document
        signed_doc = Document(
            owner_id=UUID(owner_id),
            document_type='SIGNED_CONTRACT',
            file_name=signed_document.filename,
            file_path=str(file_path),
            file_size_bytes=len(file_content),
            mime_type=signed_document.content_type,
            description=f"Signed document uploaded by agent for signature initiation",
            uploaded_by_user_id=current_user.user_id,
        )
        
        db.add(signed_doc)
        db.flush()  # Flush to get the document_id
        signed_document_id = signed_doc.document_id
        signed_document_name = signed_doc.file_name
        
        logger.info(
            "Signed document uploaded",
            extra={
                "document_id": str(signed_document_id),
                "file_name": signed_document.filename,
                "user_id": str(current_user.user_id),
            }
        )
    
    # Generate signing token
    signing_token = str(uuid.uuid4())
    
    signature = DocumentSignature(
        document_id=UUID(document_id),
        owner_id=UUID(owner_id),
        signature_status="WAIT_FOR_SIGN",
        signing_token=signing_token,
        signed_document_id=signed_document_id,
    )
    
    db.add(signature)
    db.flush()  # Flush to get signature_id
    
    # Update owner status
    owner.owner_status = "WAIT_FOR_SIGN"
    owner.signature_session_id = signature.signature_id
    
    # Create approval task and link bidirectionally
    from app.models.unit import Unit
    from app.services.task_creation import create_signature_approval_task
    
    unit = db.query(Unit).filter(Unit.unit_id == owner.unit_id).first()
    if unit:
        try:
            task = create_signature_approval_task(
                owner_id=UUID(owner_id),
                building_id=unit.building_id,
                requested_by_agent_id=current_user.user_id,
                signature_id=signature.signature_id,
                db=db
            )
            # Link signature to task (bidirectional)
            signature.task_id = task.task_id
        except Exception as e:
            logger.error(f"Failed to create approval task: {e}")
            # Continue without task - signature is still created
    
    db.commit()
    db.refresh(signature)
    
    logger.info(
        "Signature initiated",
        extra={
            "signature_id": str(signature.signature_id),
            "owner_id": str(signature.owner_id),
            "document_id": str(signature.document_id),
            "signed_document_id": str(signed_document_id) if signed_document_id else None,
            "task_id": str(signature.task_id) if signature.task_id else None,
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
        task_id=str(signature.task_id) if signature.task_id else None,
        signed_document_id=str(signature.signed_document_id) if signature.signed_document_id else None,
        signed_document_name=signed_document_name,
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
        
        # Update unit status based on all owners
        from app.services.unit_status import update_unit_status
        update_unit_status(str(owner.unit_id), db)
    
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
    owner_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get approval queue (signatures pending manager approval)"""
    query = db.query(DocumentSignature).filter(
        DocumentSignature.signature_status == "SIGNED_PENDING_APPROVAL"
    )
    
    # Role-based access control: Agents can only see approvals for owners assigned to them
    if current_user.role == "AGENT":
        query = query.join(Owner, DocumentSignature.owner_id == Owner.owner_id).filter(Owner.assigned_agent_id == current_user.user_id)
        if owner_id:
            # Additional check: ensure the owner is assigned to them
            query = query.filter(Owner.owner_id == owner_id)
    elif current_user.role not in ["SUPER_ADMIN", "PROJECT_MANAGER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only agents, managers, and admins can view approvals"
        )
    else:
        # Managers and admins can filter by owner_id if provided
        if owner_id:
            query = query.filter(DocumentSignature.owner_id == owner_id)
    
    signatures = query.order_by(desc(DocumentSignature.signed_at)).offset(skip).limit(limit).all()
    
    # Get signed document names for signatures that have signed_document_id
    signed_doc_map = {}
    signed_doc_ids = [s.signed_document_id for s in signatures if s.signed_document_id]
    if signed_doc_ids:
        signed_docs = db.query(Document).filter(Document.document_id.in_(signed_doc_ids)).all()
        signed_doc_map = {str(doc.document_id): doc.file_name for doc in signed_docs}
    
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
            task_id=str(s.task_id) if s.task_id else None,
            signed_document_id=str(s.signed_document_id) if s.signed_document_id else None,
            signed_document_name=signed_doc_map.get(str(s.signed_document_id)) if s.signed_document_id else None,
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
    # Reason is optional for approval
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
    signature.approval_reason = approval_data.reason if approval_data.reason else None
    
    # Mark linked task as completed if exists
    if signature.task_id:
        from app.models.task import Task
        task = db.query(Task).filter(Task.task_id == signature.task_id).first()
        if task:
            task.status = "COMPLETED"
            task.completed_at = datetime.utcnow()
            if approval_data.reason:
                task.notes = (task.notes or "") + f"\n[Approval Notes]: {approval_data.reason}"
    
    # Update owner status
    owner = db.query(Owner).filter(Owner.owner_id == signature.owner_id).first()
    if owner:
        owner.owner_status = "SIGNED"
        
        # Update unit status based on all owners
        from app.services.unit_status import update_unit_status
        update_unit_status(str(owner.unit_id), db)
    
    db.commit()
    
    # Trigger majority recalculation
    from app.services.majority import calculate_building_majority, calculate_project_majority
    from app.models.unit import Unit
    from app.models.building import Building
    owner = db.query(Owner).filter(Owner.owner_id == signature.owner_id).first()
    if owner:
        unit = db.query(Unit).filter(Unit.unit_id == owner.unit_id).first()
        if unit:
            try:
                calculate_building_majority(str(unit.building_id), db)
                building = db.query(Building).filter(Building.building_id == unit.building_id).first()
                if building:
                    calculate_project_majority(str(building.project_id), db)
            except Exception as e:
                logger.error(f"Failed to recalculate majority: {e}")
    
    logger.info(
        "Signature approved",
        extra={
            "signature_id": str(signature.signature_id),
            "approved_by": str(current_user.user_id),
            "reason": approval_data.reason[:50] if approval_data.reason else None,
            "task_id": str(signature.task_id) if signature.task_id else None,
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
    # Reason is required for rejection
    if not rejection_data.reason or len(rejection_data.reason.strip()) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rejection reason is required and must be at least 10 characters"
        )
    
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
    
    # Mark linked task as completed if exists
    if signature.task_id:
        from app.models.task import Task
        task = db.query(Task).filter(Task.task_id == signature.task_id).first()
        if task:
            task.status = "COMPLETED"
            task.completed_at = datetime.utcnow()
            task.notes = (task.notes or "") + f"\n[Rejection Notes]: {rejection_data.reason}"
    
    # Update owner status
    owner = db.query(Owner).filter(Owner.owner_id == signature.owner_id).first()
    if owner:
        owner.owner_status = "WAIT_FOR_SIGN"
    
    db.commit()
    db.refresh(signature)
    
    # Get signed document name if exists
    signed_document_name = None
    if signature.signed_document_id:
        signed_doc = db.query(Document).filter(Document.document_id == signature.signed_document_id).first()
        if signed_doc:
            signed_document_name = signed_doc.file_name
    
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
        task_id=str(signature.task_id) if signature.task_id else None,
        signed_document_id=str(signature.signed_document_id) if signature.signed_document_id else None,
        signed_document_name=signed_document_name,
    )

