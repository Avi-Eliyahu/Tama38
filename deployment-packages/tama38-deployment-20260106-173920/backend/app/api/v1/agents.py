"""
Agent-specific API endpoints for mobile application
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date, timedelta
from app.core.database import get_db
from app.models.user import User
from app.models.owner import Owner
from app.models.unit import Unit
from app.models.building import Building
from app.models.task import Task
from app.models.interaction import Interaction
from app.api.dependencies import get_current_user, require_role
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agents", tags=["agents"])


class LeadResponse(BaseModel):
    """Lead/Owner information for agent mobile app"""
    owner_id: str
    owner_name: str
    unit_id: str
    unit_number: str
    building_id: str
    building_name: str
    phone_for_contact: Optional[str]
    email: Optional[str]
    owner_status: str
    priority: str  # HIGH, MEDIUM, LOW based on status and last contact
    last_contact_date: Optional[date]
    days_since_contact: Optional[int]
    pending_tasks_count: int
    signature_percentage: float
    preferred_contact_method: Optional[str]
    
    class Config:
        from_attributes = True


class AgentDashboardResponse(BaseModel):
    """Agent dashboard summary"""
    total_leads: int
    high_priority_leads: int
    pending_tasks: int
    overdue_tasks: int
    recent_interactions_today: int
    leads_by_status: dict


@router.get("/my-leads", response_model=List[LeadResponse])
async def get_my_leads(
    priority_filter: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("AGENT"))
):
    """Get agent's assigned leads (owners) with priority sorting"""
    # Get assigned owners
    query = db.query(Owner).filter(
        Owner.assigned_agent_id == current_user.user_id,
        Owner.is_deleted == False,
        Owner.is_current_owner == True
    )
    
    if status_filter:
        query = query.filter(Owner.owner_status == status_filter)
    
    owners = query.all()
    
    # Get units and buildings for these owners
    unit_ids = [o.unit_id for o in owners]
    owner_ids = [o.owner_id for o in owners]
    units = db.query(Unit).filter(Unit.unit_id.in_(unit_ids)).all()
    unit_map = {u.unit_id: u for u in units}
    
    building_ids = [u.building_id for u in units]
    buildings = db.query(Building).filter(Building.building_id.in_(building_ids)).all()
    building_map = {b.building_id: b for b in buildings}
    
    # Get task counts for each owner
    task_counts = {}
    tasks = db.query(Task).filter(
        Task.owner_id.in_(owner_ids),
        Task.status.in_(["NOT_STARTED", "IN_PROGRESS", "BLOCKED", "OVERDUE"])
    ).all()
    for task in tasks:
        if task.owner_id:
            task_counts[str(task.owner_id)] = task_counts.get(str(task.owner_id), 0) + 1
    
    # Build lead responses with priority calculation
    leads = []
    today = date.today()
    
    for owner in owners:
        unit = unit_map.get(owner.unit_id)
        if not unit:
            continue
        
        building = building_map.get(unit.building_id)
        if not building:
            continue
        
        # Calculate priority
        priority = "MEDIUM"
        days_since = None
        
        if owner.last_contact_date:
            days_since = (today - owner.last_contact_date).days
            if owner.owner_status in ["NOT_CONTACTED", "NEGOTIATING"]:
                if days_since > 7:
                    priority = "HIGH"
                elif days_since > 3:
                    priority = "MEDIUM"
                else:
                    priority = "LOW"
            elif owner.owner_status == "WAIT_FOR_SIGN":
                priority = "HIGH"
            elif owner.owner_status == "REFUSED":
                priority = "LOW"
        else:
            if owner.owner_status == "NOT_CONTACTED":
                priority = "HIGH"
        
        # Apply priority filter
        if priority_filter and priority != priority_filter:
            continue
        
        leads.append(LeadResponse(
            owner_id=str(owner.owner_id),
            owner_name=owner.full_name,
            unit_id=str(unit.unit_id),
            unit_number=unit.unit_number,
            building_id=str(building.building_id),
            building_name=building.building_name,
            phone_for_contact=owner.phone_for_contact,
            email=owner.email,
            owner_status=owner.owner_status,
            priority=priority,
            last_contact_date=owner.last_contact_date,
            days_since_contact=days_since,
            pending_tasks_count=task_counts.get(str(owner.owner_id), 0),
            signature_percentage=float(unit.signature_percentage or 0),
            preferred_contact_method=owner.preferred_contact_method,
        ))
    
    # Sort by priority (HIGH -> MEDIUM -> LOW) then by days since contact
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    leads.sort(key=lambda x: (
        priority_order.get(x.priority, 99),
        x.days_since_contact if x.days_since_contact is not None else 999
    ))
    
    # Apply pagination
    paginated_leads = leads[skip:skip + limit]
    
    logger.info(
        "Agent leads retrieved",
        extra={
            "agent_id": str(current_user.user_id),
            "total_leads": len(leads),
            "returned": len(paginated_leads),
        }
    )
    
    return paginated_leads


@router.get("/dashboard", response_model=AgentDashboardResponse)
async def get_agent_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("AGENT"))
):
    """Get agent dashboard summary"""
    # Get assigned owners
    owners = db.query(Owner).filter(
        Owner.assigned_agent_id == current_user.user_id,
        Owner.is_deleted == False,
        Owner.is_current_owner == True
    ).all()
    
    # Count by status
    leads_by_status = {}
    high_priority_count = 0
    today = date.today()
    
    for owner in owners:
        status = owner.owner_status
        leads_by_status[status] = leads_by_status.get(status, 0) + 1
        
        # Count high priority
        if status in ["NOT_CONTACTED", "WAIT_FOR_SIGN"]:
            high_priority_count += 1
        elif status == "NEGOTIATING" and owner.last_contact_date:
            days_since = (today - owner.last_contact_date).days
            if days_since > 7:
                high_priority_count += 1
    
    # Get tasks
    tasks = db.query(Task).filter(
        Task.assigned_to_agent_id == current_user.user_id
    ).all()
    
    pending_tasks = len([t for t in tasks if t.status in ["NOT_STARTED", "IN_PROGRESS", "BLOCKED"]])
    overdue_tasks = len([t for t in tasks if t.status == "OVERDUE" or (t.due_date and t.due_date < today and t.status != "COMPLETED")])
    
    # Get today's interactions
    today_start = datetime.combine(today, datetime.min.time())
    recent_interactions = db.query(Interaction).filter(
        Interaction.agent_id == current_user.user_id,
        Interaction.interaction_timestamp >= today_start
    ).count()
    
    return AgentDashboardResponse(
        total_leads=len(owners),
        high_priority_leads=high_priority_count,
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,
        recent_interactions_today=recent_interactions,
        leads_by_status=leads_by_status,
    )


@router.get("/my-assigned-owners")
async def get_my_assigned_owners(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("AGENT"))
):
    """Get agent's assigned owners (alias for /owners endpoint with agent filtering)"""
    from app.api.v1.owners import OwnerResponse
    
    owners = db.query(Owner).filter(
        Owner.assigned_agent_id == current_user.user_id,
        Owner.is_deleted == False,
        Owner.is_current_owner == True
    ).offset(skip).limit(limit).all()
    
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

