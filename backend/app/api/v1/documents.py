"""
Documents API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
import os
import shutil
from pathlib import Path
from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.document import Document
from app.models.owner import Owner
from app.api.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


class DocumentResponse(BaseModel):
    document_id: str
    owner_id: Optional[str]
    document_type: str
    file_name: str
    file_size_bytes: Optional[int]
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    owner_id: Optional[str] = Form(None),
    building_id: Optional[str] = Form(None),
    project_id: Optional[str] = Form(None),
    document_type: str = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a document (local storage in Phase 1)"""
    # Validate file type and size
    allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {allowed_types}"
        )
    
    # Max file size: 10MB
    max_size = 10 * 1024 * 1024
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 10MB limit"
        )
    
    # Validate owner exists if provided
    if owner_id:
        owner = db.query(Owner).filter(
            Owner.owner_id == owner_id,
            Owner.is_deleted == False
        ).first()
        if not owner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Owner not found"
            )
    
    # Create storage directory if it doesn't exist
    storage_path = Path(settings.STORAGE_PATH) / "documents"
    storage_path.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    import uuid
    file_id = uuid.uuid4()
    file_extension = Path(file.filename).suffix
    file_path = storage_path / f"{file_id}{file_extension}"
    
    # Save file
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)
    
    # Create document record
    document = Document(
        owner_id=UUID(owner_id) if owner_id else None,
        building_id=UUID(building_id) if building_id else None,
        project_id=UUID(project_id) if project_id else None,
        document_type=document_type,
        file_name=file.filename,
        file_path=str(file_path),
        file_size_bytes=len(file_content),
        mime_type=file.content_type,
        description=description,
        uploaded_by_user_id=current_user.user_id,
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    logger.info(
        "Document uploaded",
        extra={
            "document_id": str(document.document_id),
            "file_name": file.filename,
            "file_size": len(file_content),
            "user_id": str(current_user.user_id),
        }
    )
    
    # Convert UUIDs to strings for response
    return DocumentResponse(
        document_id=str(document.document_id),
        owner_id=str(document.owner_id) if document.owner_id else None,
        document_type=document.document_type,
        file_name=document.file_name,
        file_size_bytes=document.file_size_bytes,
        description=document.description,
        created_at=document.created_at,
    )


@router.get("/{document_id}/download")
async def get_document_download_url(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get document download URL (local file path in Phase 1)"""
    document = db.query(Document).filter(
        Document.document_id == document_id,
        Document.is_deleted == False
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check file exists
    if not os.path.exists(document.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found on storage"
        )
    
    # Return download URL (in Phase 1, this is a local path; in Phase 2, it would be a presigned S3 URL)
    return {
        "download_url": f"/api/v1/files/{document.document_id}",
        "file_name": document.file_name,
        "expires_in": 900,  # 15 minutes
    }


@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    owner_id: Optional[UUID] = Query(None),
    building_id: Optional[UUID] = Query(None),
    project_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List documents"""
    query = db.query(Document).filter(Document.is_deleted == False)
    
    if owner_id:
        query = query.filter(Document.owner_id == owner_id)
    if building_id:
        query = query.filter(Document.building_id == building_id)
    if project_id:
        query = query.filter(Document.project_id == project_id)
    
    documents = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    # Convert UUIDs to strings for response
    return [
        DocumentResponse(
            document_id=str(d.document_id),
            owner_id=str(d.owner_id) if d.owner_id else None,
            document_type=d.document_type,
            file_name=d.file_name,
            file_size_bytes=d.file_size_bytes,
            description=d.description,
            created_at=d.created_at,
        )
        for d in documents
    ]

