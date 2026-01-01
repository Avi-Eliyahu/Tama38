"""
Authentication API endpoints
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, field_validator
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.core.config import settings
from app.models.user import User
from app.api.dependencies import get_current_user
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


class LoginRequest(BaseModel):
    email: str  # Changed from EmailStr to allow .local domains
    password: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format (allowing .local domains)"""
        if '@' not in v or '.' not in v.split('@')[1]:
            raise ValueError('Invalid email format')
        return v.lower().strip()


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
    request: Request = None
):
    """Authenticate user and return tokens"""
    import json
    import os
    request_id = getattr(request.state, 'request_id', None) if request else None
    
    # #region agent log
    with open('/app/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"location":"auth.py:49","message":"login endpoint called","data":{"email":login_data.email,"request_id":str(request_id)},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"E"})+"\n")
    # #endregion
    
    logger.info(
        "Login attempt",
        extra={
            "request_id": request_id,
            "email": login_data.email,
        }
    )
    
    # #region agent log
    with open('/app/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"location":"auth.py:66","message":"Before user query","data":{"email":login_data.email},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"F"})+"\n")
    # #endregion
    
    user = db.query(User).filter(User.email == login_data.email).first()
    
    # #region agent log
    with open('/app/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"location":"auth.py:68","message":"After user query","data":{"user_found":user is not None,"user_id":str(user.user_id) if user else None},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"F"})+"\n")
    # #endregion
    
    # #region agent log
    with open('/app/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"location":"auth.py:70","message":"Before verify_password","data":{},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"G"})+"\n")
    # #endregion
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        logger.warning(
            "Login failed - invalid credentials",
            extra={
                "request_id": request_id,
                "email": login_data.email,
            }
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if not user.is_active:
        logger.warning(
            "Login failed - user inactive",
            extra={
                "request_id": request_id,
                "user_id": str(user.user_id),
            }
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    # #region agent log
    import json
    with open('/app/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"location":"auth.py:95","message":"Password verified, before commit","data":{"user_id":str(user.user_id)},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"H"})+"\n")
    # #endregion
    
    # Update last login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    # #region agent log
    with open('/app/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"location":"auth.py:100","message":"After commit, before token creation","data":{},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"I"})+"\n")
    # #endregion
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.user_id), "role": user.role})
    refresh_token = create_refresh_token(data={"sub": str(user.user_id)})
    
    # #region agent log
    with open('/app/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"location":"auth.py:105","message":"Tokens created, before return","data":{"has_access_token":bool(access_token),"has_refresh_token":bool(refresh_token)},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"J"})+"\n")
    # #endregion
    
    logger.info(
        "Login successful",
        extra={
            "request_id": request_id,
            "user_id": str(user.user_id),
            "role": user.role,
        }
    )
    
    response_data = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "user_id": str(user.user_id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        }
    )
    
    # #region agent log
    with open('/app/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"location":"auth.py:125","message":"Before returning response","data":{},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"J"})+"\n")
    # #endregion
    
    return response_data


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
    request: Request = None
):
    """Refresh access token using refresh token"""
    request_id = getattr(request.state, 'request_id', None) if request else None
    
    payload = decode_token(refresh_data.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        logger.warning(
            "Token refresh failed - invalid token",
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.user_id == user_id, User.is_active == True).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    access_token = create_access_token(data={"sub": str(user.user_id), "role": user.role})
    refresh_token = create_refresh_token(data={"sub": str(user.user_id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "user_id": str(user.user_id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        }
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse(
        user_id=str(current_user.user_id),
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """Logout user (token invalidation handled client-side in Phase 1)"""
    logger.info(
        "User logged out",
        extra={"user_id": str(current_user.user_id)}
    )
    return {"message": "Logged out successfully"}

