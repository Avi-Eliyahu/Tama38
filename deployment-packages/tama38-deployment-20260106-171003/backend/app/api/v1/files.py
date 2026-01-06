"""
File serving endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from uuid import UUID
import os
from app.core.database import get_db
from app.models.document import Document
from app.api.dependencies import get_current_user
from app.models.user import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/files", tags=["files"])


@router.get("/{document_id}")
async def serve_file(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Serve document file (local file serving in Phase 1)"""
    document = db.query(Document).filter(
        Document.document_id == document_id,
        Document.is_deleted == False
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if not os.path.exists(document.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on storage"
        )
    
    logger.info(
        "File served",
        extra={
            "document_id": str(document_id),
            "file_name": document.file_name,
            "user_id": str(current_user.user_id),
        }
    )
    
    return FileResponse(
        document.file_path,
        media_type=document.mime_type or "application/octet-stream",
        filename=document.file_name,
    )

