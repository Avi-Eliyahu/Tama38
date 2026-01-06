"""
Interactions API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date, timedelta
from app.core.database import get_db
from app.models.user import User
from app.models.interaction import Interaction
from app.models.owner import Owner
from app.api.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/interactions", tags=["interactions"])


class InteractionCreate(BaseModel):
    owner_id: str
    interaction_type: str
    interaction_date: str
    duration_minutes: Optional[int] = None
    outcome: Optional[str] = None
    call_summary: str  # Mandatory
    key_objection: Optional[str] = None
    next_action: Optional[str] = None
    next_follow_up_date: Optional[str] = None
    follow_up_type: Optional[str] = None
    sentiment: Optional[str] = None
    is_escalated: Optional[bool] = False
    escalation_reason: Optional[str] = None
    attempted: Optional[bool] = True
    contact_method_used: Optional[str] = None


class InteractionResponse(BaseModel):
    log_id: str
    owner_id: str
    agent_id: str
    interaction_type: str
    interaction_date: date
    interaction_timestamp: datetime
    duration_minutes: Optional[int]
    outcome: Optional[str]
    call_summary: str
    sentiment: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
async def create_interaction(
    interaction_data: InteractionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Log an interaction (mandatory call summary)"""
    # Validate owner exists
    owner = db.query(Owner).filter(
        Owner.owner_id == interaction_data.owner_id,
        Owner.is_deleted == False
    ).first()
    
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found"
        )
    
    # Validate mandatory call summary
    if not interaction_data.call_summary or len(interaction_data.call_summary.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Call summary is mandatory and cannot be empty"
        )
    
    interaction = Interaction(
        owner_id=UUID(interaction_data.owner_id),
        agent_id=current_user.user_id,
        interaction_type=interaction_data.interaction_type,
        interaction_date=datetime.fromisoformat(interaction_data.interaction_date).date(),
        interaction_timestamp=datetime.utcnow(),
        duration_minutes=interaction_data.duration_minutes,
        outcome=interaction_data.outcome,
        call_summary=interaction_data.call_summary,
        key_objection=interaction_data.key_objection,
        next_action=interaction_data.next_action,
        next_follow_up_date=datetime.fromisoformat(interaction_data.next_follow_up_date).date() if interaction_data.next_follow_up_date else None,
        follow_up_type=interaction_data.follow_up_type,
        sentiment=interaction_data.sentiment,
        is_escalated=interaction_data.is_escalated,
        escalation_reason=interaction_data.escalation_reason,
        attempted=interaction_data.attempted,
        contact_method_used=interaction_data.contact_method_used,
    )
    
    db.add(interaction)
    
    # Update owner's last contact date
    owner.last_contact_date = interaction.interaction_date
    owner.last_activity_timestamp = interaction.interaction_timestamp
    
    db.commit()
    db.refresh(interaction)
    
    logger.info(
        "Interaction logged",
        extra={
            "interaction_id": str(interaction.log_id),
            "owner_id": str(interaction.owner_id),
            "agent_id": str(interaction.agent_id),
            "interaction_type": interaction.interaction_type,
        }
    )
    
    # Convert UUIDs to strings for response
    return InteractionResponse(
        log_id=str(interaction.log_id),
        owner_id=str(interaction.owner_id),
        agent_id=str(interaction.agent_id),
        interaction_type=interaction.interaction_type,
        interaction_date=interaction.interaction_date,
        interaction_timestamp=interaction.interaction_timestamp,
        duration_minutes=interaction.duration_minutes,
        outcome=interaction.outcome,
        call_summary=interaction.call_summary,
        sentiment=interaction.sentiment,
        created_at=interaction.created_at,
    )


@router.get("", response_model=List[InteractionResponse])
async def list_interactions(
    owner_id: Optional[UUID] = Query(None),
    agent_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List interactions (filtered by owner or agent)"""
    query = db.query(Interaction)
    
    if owner_id:
        query = query.filter(Interaction.owner_id == owner_id)
    
    if agent_id:
        query = query.filter(Interaction.agent_id == agent_id)
    elif current_user.role == "AGENT":
        # Agents can only see their own interactions
        query = query.filter(Interaction.agent_id == current_user.user_id)
    
    interactions = query.order_by(desc(Interaction.interaction_timestamp)).offset(skip).limit(limit).all()
    # Convert UUIDs to strings for response
    return [
        InteractionResponse(
            log_id=str(i.log_id),
            owner_id=str(i.owner_id),
            agent_id=str(i.agent_id),
            interaction_type=i.interaction_type,
            interaction_date=i.interaction_date,
            interaction_timestamp=i.interaction_timestamp,
            duration_minutes=i.duration_minutes,
            outcome=i.outcome,
            call_summary=i.call_summary,
            sentiment=i.sentiment,
            created_at=i.created_at,
        )
        for i in interactions
    ]


@router.get("/recent", response_model=List[InteractionResponse])
async def get_recent_interactions(
    hours: int = Query(24, ge=1, le=168),  # Default 24 hours, max 1 week
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recent interactions (last N hours)"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    query = db.query(Interaction).filter(
        Interaction.interaction_timestamp >= cutoff_time
    )
    
    if current_user.role == "AGENT":
        query = query.filter(Interaction.agent_id == current_user.user_id)
    
    interactions = query.order_by(desc(Interaction.interaction_timestamp)).limit(100).all()
    # Convert UUIDs to strings for response
    return [
        InteractionResponse(
            log_id=str(i.log_id),
            owner_id=str(i.owner_id),
            agent_id=str(i.agent_id),
            interaction_type=i.interaction_type,
            interaction_date=i.interaction_date,
            interaction_timestamp=i.interaction_timestamp,
            duration_minutes=i.duration_minutes,
            outcome=i.outcome,
            call_summary=i.call_summary,
            sentiment=i.sentiment,
            created_at=i.created_at,
        )
        for i in interactions
    ]

