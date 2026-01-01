"""
Dashboard API endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta, date
from app.core.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.building import Building
from app.models.owner import Owner
from app.models.interaction import Interaction
from app.models.unit import Unit
from app.models.task import Task
from app.models.document import DocumentSignature
from app.api.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/data")
async def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard data (KPIs, traffic lights, recent interactions, top buildings)"""
    start_time = datetime.utcnow()
    
    # Total Projects
    total_projects = db.query(Project).filter(Project.is_deleted == False).count()
    
    # Active Projects
    active_projects = db.query(Project).filter(
        Project.is_deleted == False,
        Project.project_stage.in_(["PLANNING", "ACTIVE", "APPROVAL"])
    ).count()
    
    # Total Buildings
    total_buildings = db.query(Building).filter(Building.is_deleted == False).count()
    
    # Total Units
    total_units = db.query(Unit).filter(Unit.is_deleted == False).count()
    
    # Total Owners
    total_owners = db.query(Owner).filter(
        Owner.is_deleted == False,
        Owner.is_current_owner == True
    ).count()
    
    # Calculate overall signature percentage
    buildings = db.query(Building).filter(Building.is_deleted == False).all()
    total_signature_sum = sum(float(b.signature_percentage or 0) for b in buildings)
    signed_percentage = total_signature_sum / len(buildings) if buildings else 0.0
    
    # Pending Approvals
    pending_approvals = db.query(DocumentSignature).filter(
        DocumentSignature.signature_status == "SIGNED_PENDING_APPROVAL"
    ).count()
    
    # Overdue Tasks
    today = date.today()
    overdue_tasks = db.query(Task).filter(
        and_(
            Task.due_date < today,
            Task.status.in_(["NOT_STARTED", "IN_PROGRESS", "BLOCKED"])
        )
    ).count()
    
    # Recent Interactions count (last 24 hours)
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    recent_interactions = db.query(Interaction).filter(
        Interaction.interaction_timestamp >= cutoff_time
    ).count()
    
    # Projects by Stage
    projects_by_stage = db.query(
        Project.project_stage,
        func.count(Project.project_id).label('count')
    ).filter(
        Project.is_deleted == False
    ).group_by(Project.project_stage).all()
    
    projects_by_stage_dict = {
        "PLANNING": 0,
        "ACTIVE": 0,
        "APPROVAL": 0,
        "COMPLETED": 0,
        "ARCHIVED": 0,
    }
    for stage, count in projects_by_stage:
        projects_by_stage_dict[stage] = count
    
    # Buildings by Status
    buildings_by_status = db.query(
        Building.current_status,
        func.count(Building.building_id).label('count')
    ).filter(
        Building.is_deleted == False
    ).group_by(Building.current_status).all()
    
    buildings_by_status_dict = {
        "INITIAL": 0,
        "NEGOTIATING": 0,
        "APPROVED": 0,
        "RENOVATION_PLANNING": 0,
        "RENOVATION_ONGOING": 0,
        "COMPLETED": 0,
    }
    for status, count in buildings_by_status:
        buildings_by_status_dict[status] = count
    
    calculation_time = (datetime.utcnow() - start_time).total_seconds() * 1000
    
    logger.info(
        "Dashboard data retrieved",
        extra={
            "user_id": str(current_user.user_id),
            "calculation_time_ms": calculation_time,
        }
    )
    
    return {
        "total_projects": total_projects,
        "active_projects": active_projects,
        "total_buildings": total_buildings,
        "total_units": total_units,
        "total_owners": total_owners,
        "signed_percentage": round(signed_percentage, 2),
        "pending_approvals": pending_approvals,
        "overdue_tasks": overdue_tasks,
        "recent_interactions": recent_interactions,
        "projects_by_stage": projects_by_stage_dict,
        "buildings_by_status": buildings_by_status_dict,
    }

