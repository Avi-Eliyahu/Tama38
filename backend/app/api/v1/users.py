"""
Users API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.core.database import get_db
from app.models.user import User
from app.api.dependencies import get_current_user, require_role
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


class UserResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    phone: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[UserResponse])
async def list_users(
    role: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SUPER_ADMIN", "PROJECT_MANAGER"))
):
    """List users (optionally filtered by role) - Admin/Manager only"""
    query = db.query(User).filter(User.is_deleted == False)
    
    if role:
        query = query.filter(User.role == role)
    
    users = query.all()
    
    return [
        UserResponse(
            user_id=str(u.user_id),
            email=u.email,
            full_name=u.full_name,
            role=u.role,
            is_active=u.is_active,
            phone=u.phone,
        )
        for u in users
    ]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user details"""
    user = db.query(User).filter(
        User.user_id == user_id,
        User.is_deleted == False
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Users can only see their own details unless they're admin/manager
    if current_user.role not in ["SUPER_ADMIN", "PROJECT_MANAGER"] and current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own user details"
        )
    
    return UserResponse(
        user_id=str(user.user_id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        phone=user.phone,
    )

