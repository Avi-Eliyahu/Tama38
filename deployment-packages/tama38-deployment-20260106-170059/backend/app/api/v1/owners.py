"""
Owners API endpoints with multi-unit support
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from pathlib import Path
from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.owner import Owner
from app.models.unit import Unit
from app.models.building import Building
from app.api.dependencies import get_current_user
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/owners", tags=["owners"])


class OwnerCreate(BaseModel):
    unit_id: str
    full_name: str
    id_number: Optional[str] = None  # Will be encrypted in Phase 2
    phone: Optional[str] = None  # Will be encrypted in Phase 2
    email: Optional[EmailStr] = None
    ownership_share_percent: float
    preferred_contact_method: Optional[str] = None
    preferred_language: Optional[str] = None
    link_to_existing: Optional[bool] = False
    existing_owner_id: Optional[str] = None


class OwnerResponse(BaseModel):
    owner_id: str
    unit_id: str
    full_name: str
    phone_for_contact: Optional[str]
    email: Optional[str]
    ownership_share_percent: float
    owner_status: str
    preferred_contact_method: Optional[str]
    preferred_language: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[OwnerResponse])
async def list_owners(
    unit_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List owners (optionally filtered by unit)"""
    query = db.query(Owner).filter(Owner.is_deleted == False)
    
    if unit_id:
        query = query.filter(Owner.unit_id == unit_id)
    
    # Role-based filtering
    if current_user.role == "AGENT":
        # Check building assignment instead of owner assignment
        if unit_id:
            # Filter by building assignment instead of owner assignment
            from app.models.unit import Unit
            from app.models.building import Building
            unit = db.query(Unit).filter(Unit.unit_id == unit_id).first()
            if unit:
                building = db.query(Building).filter(Building.building_id == unit.building_id).first()
                if building and building.assigned_agent_id == current_user.user_id:
                    # Building is assigned to this agent, show all owners in this unit
                    pass  # No additional filter needed
                else:
                    # Building not assigned to agent, filter by owner assignment as fallback
                    query = query.filter(Owner.assigned_agent_id == current_user.user_id)
            else:
                # Unit not found, filter by owner assignment
                query = query.filter(Owner.assigned_agent_id == current_user.user_id)
        else:
            # No unit_id specified, filter by building assignment OR owner assignment via join
            from app.models.unit import Unit
            from app.models.building import Building
            from sqlalchemy import or_
            query = query.join(Unit).join(Building).filter(
                or_(
                    Building.assigned_agent_id == current_user.user_id,
                    Owner.assigned_agent_id == current_user.user_id
                )
            )
    
    owners = query.offset(skip).limit(limit).all()
    # Convert UUIDs to strings for response
    return [
        OwnerResponse(
            owner_id=str(o.owner_id),
            unit_id=str(o.unit_id),
            full_name=o.full_name,
            phone_for_contact=o.phone_for_contact,
            email=o.email,
            ownership_share_percent=float(o.ownership_share_percent),
            owner_status=o.owner_status,
            preferred_contact_method=o.preferred_contact_method,
            preferred_language=o.preferred_language,
            created_at=o.created_at,
        )
        for o in owners
    ]


@router.post("", response_model=OwnerResponse, status_code=status.HTTP_201_CREATED)
async def create_owner(
    owner_data: OwnerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new owner (with multi-unit support)"""
    # Verify unit exists
    unit = db.query(Unit).filter(
        Unit.unit_id == owner_data.unit_id,
        Unit.is_deleted == False
    ).first()
    
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )
    
    # Check if linking to existing owner
    if owner_data.link_to_existing and owner_data.existing_owner_id:
        existing_owner = db.query(Owner).filter(
            Owner.owner_id == owner_data.existing_owner_id,
            Owner.is_deleted == False
        ).first()
        
        if not existing_owner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Existing owner not found"
            )
        
        # Create new owner record linked to same person (multi-unit ownership)
        owner = Owner(
            unit_id=UUID(owner_data.unit_id),
            full_name=existing_owner.full_name,  # Use existing owner's name
            id_number_hash=existing_owner.id_number_hash,  # Link via hash
            phone_hash=existing_owner.phone_hash,
            phone_for_contact=owner_data.phone or existing_owner.phone_for_contact,
            email=owner_data.email or existing_owner.email,
            ownership_share_percent=owner_data.ownership_share_percent,
            preferred_contact_method=owner_data.preferred_contact_method or existing_owner.preferred_contact_method,
            preferred_language=owner_data.preferred_language or existing_owner.preferred_language,
            assigned_agent_id=existing_owner.assigned_agent_id,
        )
    else:
        # Create new owner
        owner = Owner(
            unit_id=UUID(owner_data.unit_id),
            full_name=owner_data.full_name,
            phone_for_contact=owner_data.phone,
            email=owner_data.email,
            ownership_share_percent=owner_data.ownership_share_percent,
            preferred_contact_method=owner_data.preferred_contact_method,
            preferred_language=owner_data.preferred_language,
            assigned_agent_id=current_user.user_id if current_user.role == "AGENT" else None,
        )
    
    # Validate ownership share totals 100% per unit
    existing_owners = db.query(Owner).filter(
        Owner.unit_id == owner_data.unit_id,
        Owner.is_deleted == False,
        Owner.is_current_owner == True
    ).all()
    
    total_share = sum(float(o.ownership_share_percent) for o in existing_owners) + owner_data.ownership_share_percent
    
    if total_share > 100.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Total ownership share cannot exceed 100%. Current total: {total_share}%"
        )
    
    db.add(owner)
    
    # Update unit owner counts
    unit.total_owners = len(existing_owners) + 1
    unit.is_co_owned = unit.total_owners > 1
    
    db.commit()
    db.refresh(owner)
    
    logger.info(
        "Owner created",
        extra={
            "owner_id": str(owner.owner_id),
            "unit_id": str(owner.unit_id),
            "user_id": str(current_user.user_id),
            "is_multi_unit": owner_data.link_to_existing or False,
        }
    )
    
    # Convert UUIDs to strings for response
    return OwnerResponse(
        owner_id=str(owner.owner_id),
        unit_id=str(owner.unit_id),
        full_name=owner.full_name,
        phone_for_contact=owner.phone_for_contact,
        email=owner.email,
        ownership_share_percent=float(owner.ownership_share_percent),
        owner_status=owner.owner_status,
        preferred_contact_method=owner.preferred_contact_method,
        preferred_language=owner.preferred_language,
        created_at=owner.created_at,
    )


@router.get("/{owner_id}", response_model=OwnerResponse)
async def get_owner(
    owner_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get owner details"""
    owner = db.query(Owner).filter(
        Owner.owner_id == owner_id,
        Owner.is_deleted == False
    ).first()
    
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found"
        )
    
    # Convert UUIDs to strings for response
    return OwnerResponse(
        owner_id=str(owner.owner_id),
        unit_id=str(owner.unit_id),
        full_name=owner.full_name,
        phone_for_contact=owner.phone_for_contact,
        email=owner.email,
        ownership_share_percent=float(owner.ownership_share_percent),
        owner_status=owner.owner_status,
        preferred_contact_method=owner.preferred_contact_method,
        preferred_language=owner.preferred_language,
        created_at=owner.created_at,
    )


@router.get("/{owner_id}/units", response_model=List[dict])
async def get_owner_units(
    owner_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all units owned by this owner (multi-unit ownership support)"""
    owner = db.query(Owner).filter(
        Owner.owner_id == owner_id,
        Owner.is_deleted == False
    ).first()
    
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found"
        )
    
    # Find all units owned by same person (via id_number_hash or phone_hash)
    if owner.id_number_hash:
        same_owners = db.query(Owner).filter(
            Owner.id_number_hash == owner.id_number_hash,
            Owner.is_deleted == False,
            Owner.is_current_owner == True
        ).all()
    elif owner.phone_hash:
        same_owners = db.query(Owner).filter(
            Owner.phone_hash == owner.phone_hash,
            Owner.is_deleted == False,
            Owner.is_current_owner == True
        ).all()
    else:
        same_owners = [owner]
    
    # Get units for these owners
    unit_ids = [o.unit_id for o in same_owners]
    units = db.query(Unit).filter(Unit.unit_id.in_(unit_ids)).all()
    
    result = []
    for unit in units:
        unit_owner = next((o for o in same_owners if o.unit_id == unit.unit_id), None)
        result.append({
            "unit_id": str(unit.unit_id),
            "unit_number": unit.unit_number,
            "floor_number": unit.floor_number,
            "building_id": str(unit.building_id),
            "ownership_share_percent": float(unit_owner.ownership_share_percent) if unit_owner else 0,
        })
    
    return result


@router.get("/search", response_model=List[OwnerResponse])
async def search_owners(
    query: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search for existing owners by name or ID"""
    search_filter = or_(
        Owner.full_name.ilike(f"%{query}%"),
        Owner.phone_for_contact.ilike(f"%{query}%"),
        Owner.email.ilike(f"%{query}%"),
    )
    
    owners = db.query(Owner).filter(
        search_filter,
        Owner.is_deleted == False,
        Owner.is_current_owner == True
    ).limit(20).all()
    
    # Convert UUIDs to strings for response
    return [
        OwnerResponse(
            owner_id=str(o.owner_id),
            unit_id=str(o.unit_id),
            full_name=o.full_name,
            phone_for_contact=o.phone_for_contact,
            email=o.email,
            ownership_share_percent=float(o.ownership_share_percent),
            owner_status=o.owner_status,
            preferred_contact_method=o.preferred_contact_method,
            preferred_language=o.preferred_language,
            created_at=o.created_at,
        )
        for o in owners
    ]


class OwnerStatusUpdate(BaseModel):
    owner_status: str
    notes: Optional[str] = None


class OwnerStatusUpdateResponse(BaseModel):
    owner_id: str
    owner_status: str
    approval_task_id: Optional[str] = None
    message: str


@router.put("/{owner_id}/status", response_model=OwnerStatusUpdateResponse)
async def update_owner_status(
    owner_id: UUID,
    owner_status: str = Form(...),
    notes: Optional[str] = Form(None),
    signed_contract_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update owner status (agent only, with approval workflow for SIGN)
    
    When status is WAIT_FOR_SIGN, a signed contract PDF file is required.
    """
    # Get owner
    owner = db.query(Owner).filter(
        Owner.owner_id == owner_id,
        Owner.is_deleted == False
    ).first()
    
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found"
        )
    
    # Get unit and building for permission check
    unit = db.query(Unit).filter(Unit.unit_id == owner.unit_id).first()
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )
    
    # Get building to access project_id
    building = db.query(Building).filter(Building.building_id == unit.building_id).first()
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found"
        )
    
    # Permission check: Agents can only update owners in buildings assigned to them
    if current_user.role == "AGENT":
        from app.services.agent_permissions import verify_agent_has_owner_access
        if not verify_agent_has_owner_access(current_user.user_id, owner_id, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update owners in buildings assigned to you"
            )
    elif current_user.role not in ["SUPER_ADMIN", "PROJECT_MANAGER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only agents, managers, and admins can update owner status"
        )
    
    # Validate status: Agents can only set workflow statuses
    workflow_statuses = ["NOT_CONTACTED", "NEGOTIATING", "AGREED_TO_SIGN", "WAIT_FOR_SIGN"]
    restricted_statuses = ["SIGNED", "REFUSED"]
    
    if current_user.role == "AGENT":
        if owner_status in restricted_statuses:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Agents cannot set status to {owner_status}. Use WAIT_FOR_SIGN to request approval."
            )
        if owner_status not in workflow_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status for agent: {owner_status}"
            )
    
    # If setting to WAIT_FOR_SIGN, require signed contract file
    signed_document_id = None
    if owner_status == "WAIT_FOR_SIGN":
        # Require file upload for WAIT_FOR_SIGN status
        if not signed_contract_file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Signed contract PDF file is required when setting status to WAIT_FOR_SIGN"
            )
        
        # Validate file type (PDF only)
        if signed_contract_file.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed for signed contracts"
            )
        
        # Validate file size (10MB max)
        max_size = 10 * 1024 * 1024
        file_content = await signed_contract_file.read()
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
        file_extension = Path(signed_contract_file.filename).suffix or ".pdf"
        file_path = storage_path / f"{file_uuid}{file_extension}"
        
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Create Document record for signed contract
        from app.models.document import Document
        signed_doc = Document(
            owner_id=owner_id,
            building_id=unit.building_id,
            project_id=building.project_id,
            document_type="CONTRACT",  # Use CONTRACT type (SIGNED_CONTRACT not in enum)
            file_name=signed_contract_file.filename,
            file_path=str(file_path),
            file_size_bytes=len(file_content),
            mime_type=signed_contract_file.content_type,
            description=f"Signed contract uploaded when owner status changed to WAIT_FOR_SIGN",
            uploaded_by_user_id=current_user.user_id,
        )
        
        db.add(signed_doc)
        db.flush()  # Flush to get the document_id
        signed_document_id = signed_doc.document_id
        
        logger.info(
            "Signed contract uploaded for status change",
            extra={
                "owner_id": str(owner_id),
                "document_id": str(signed_document_id),
                "file_name": signed_contract_file.filename,
                "user_id": str(current_user.user_id),
            }
        )
    
    # If setting to WAIT_FOR_SIGN or requesting SIGN, create approval task
    approval_task_id = None
    if owner_status == "WAIT_FOR_SIGN":
        from app.services.task_creation import create_signature_approval_task
        from app.models.document import DocumentSignature, Document
        
        try:
            # First, check if a DocumentSignature exists for this owner
            # Look for either pending approval or wait for sign status
            signature = db.query(DocumentSignature).filter(
                DocumentSignature.owner_id == owner_id,
                DocumentSignature.signature_status.in_(["SIGNED_PENDING_APPROVAL", "WAIT_FOR_SIGN"])
            ).order_by(DocumentSignature.created_at.desc()).first()
            
            if not signature:
                # Find or create a document for this owner (use first CONTRACT document or create placeholder)
                document = db.query(Document).filter(
                    Document.owner_id == owner_id,
                    Document.document_type == "CONTRACT"
                ).first()
                
                if not document:
                    # Create a placeholder document for status change workflow
                    document = Document(
                        owner_id=owner_id,
                        building_id=unit.building_id,
                        project_id=building.project_id,
                        document_type="CONTRACT",
                        file_name="Status Change Request",
                        file_path="",  # No file for status change
                        file_size_bytes=0,
                        mime_type="application/pdf",
                        description=f"Placeholder document created for owner status change to WAIT_FOR_SIGN",
                        uploaded_by_user_id=current_user.user_id,
                    )
                    db.add(document)
                    db.flush()
                
                # Create DocumentSignature for status change workflow
                # If signed_document_id is provided, owner has already signed - needs manager approval
                # If not provided, we're waiting for owner to sign
                signature_status = "SIGNED_PENDING_APPROVAL" if signed_document_id else "WAIT_FOR_SIGN"
                signature = DocumentSignature(
                    document_id=document.document_id,
                    owner_id=owner_id,
                    signature_status=signature_status,
                    signing_token=str(uuid.uuid4()),
                    signed_at=datetime.utcnow() if signed_document_id else None,  # Set signed_at if document provided
                    signed_document_id=signed_document_id,  # Link to uploaded signed contract
                )
                db.add(signature)
                db.flush()
            else:
                # Update existing signature with signed document if provided
                if signed_document_id:
                    signature.signed_document_id = signed_document_id
                    # If we're adding a signed document, update status to pending approval
                    if signature.signature_status == "WAIT_FOR_SIGN":
                        signature.signature_status = "SIGNED_PENDING_APPROVAL"
                        signature.signed_at = datetime.utcnow()
                    db.flush()
            
            # Only create approval task if signature is pending approval (signed document provided)
            if signature.signature_status == "SIGNED_PENDING_APPROVAL":
                approval_task = create_signature_approval_task(
                    owner_id=owner_id,
                    building_id=unit.building_id,
                    requested_by_agent_id=current_user.user_id,
                    db=db
                )
                approval_task_id = str(approval_task.task_id)
                
                # Link the signature to the task (bidirectional)
                signature.task_id = approval_task.task_id
                db.flush()
                
                logger.info(
                    "Approval task created for owner status change",
                    extra={
                        "owner_id": str(owner_id),
                        "task_id": approval_task_id,
                        "signature_id": str(signature.signature_id),
                        "requested_by": str(current_user.user_id),
                    }
                )
            else:
                logger.info(
                    "Signature created in WAIT_FOR_SIGN status - no approval task needed yet",
                    extra={
                        "owner_id": str(owner_id),
                        "signature_id": str(signature.signature_id),
                    }
                )
        except Exception as e:
            logger.error(f"Failed to create approval task: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create approval task: {str(e)}"
            )
    
    # Update owner status
    old_status = owner.owner_status
    owner.owner_status = owner_status
    if notes:
        # Store notes in owner record if needed (could add notes field to Owner model)
        pass
    
    db.commit()
    db.refresh(owner)
    
    # Trigger cascade recalculation (unless status is WAIT_FOR_SIGN, which waits for approval)
    if owner_status != "WAIT_FOR_SIGN":
        from app.services.unit_status import update_unit_status
        from app.services.majority import calculate_building_majority, calculate_project_majority
        
        try:
            update_unit_status(str(unit.unit_id), db)
            calculate_building_majority(str(unit.building_id), db)
            calculate_project_majority(str(building.project_id), db)
        except Exception as e:
            logger.error(f"Failed to recalculate progress: {e}")
            # Don't fail the request, just log the error
    
    message = f"Owner status updated from {old_status} to {owner_status}"
    if approval_task_id:
        message += ". Approval task created for manager review."
    if signed_document_id:
        message += " Signed contract uploaded."
    
    logger.info(
        "Owner status updated",
        extra={
            "owner_id": str(owner_id),
            "old_status": old_status,
            "new_status": owner_status,
            "user_id": str(current_user.user_id),
            "approval_task_id": approval_task_id,
            "signed_document_id": str(signed_document_id) if signed_document_id else None,
        }
    )
    
    return OwnerStatusUpdateResponse(
        owner_id=str(owner_id),
        owner_status=owner_status,
        approval_task_id=approval_task_id,
        message=message
    )

