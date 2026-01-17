"""
Users API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import datetime
from app.core.database import get_db
from app.models.user import User
from app.api.dependencies import get_current_user, require_role
from app.core.security import get_password_hash
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


class UserCreateRequest(BaseModel):
    email: str
    password: str
    full_name: str
    role: str
    phone: Optional[str] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format (allowing .local domains)"""
        if '@' not in v or '.' not in v.split('@')[1]:
            raise ValueError('Invalid email format')
        return v.lower().strip()
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate role is PROJECT_MANAGER or AGENT"""
        if v not in ['PROJECT_MANAGER', 'AGENT']:
            raise ValueError('Role must be PROJECT_MANAGER or AGENT')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password minimum length"""
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


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


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SUPER_ADMIN"))
):
    """Create a new user (PROJECT_MANAGER or AGENT) - Super Admin only"""
    # Check if user with email already exists
    existing_user = db.query(User).filter(
        User.email == user_data.email,
        User.is_deleted == False
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
        phone=user_data.phone,
        is_active=True,
        is_verified=False,
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"User created: {new_user.email} with role {new_user.role} by {current_user.email}")
        
        return UserResponse(
            user_id=str(new_user.user_id),
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.role,
            is_active=new_user.is_active,
            phone=new_user.phone,
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SUPER_ADMIN"))
):
    """Delete a user (soft delete) - Super Admin only"""
    user = db.query(User).filter(
        User.user_id == user_id,
        User.is_deleted == False
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting self
    if user.user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Prevent deleting SUPER_ADMIN users
    if user.role == "SUPER_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete SUPER_ADMIN users"
        )
    
    # Soft delete
    user.is_deleted = True
    user.is_active = False
    
    try:
        db.commit()
        logger.info(f"User deleted: {user.email} by {current_user.email}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

