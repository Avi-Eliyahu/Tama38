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
    
    # Base queries - filter by agent assignment if user is an agent
    project_query = db.query(Project).filter(Project.is_deleted == False)
    building_query = db.query(Building).filter(Building.is_deleted == False)
    unit_query = db.query(Unit).filter(Unit.is_deleted == False)
    owner_query = db.query(Owner).filter(
        Owner.is_deleted == False,
        Owner.is_current_owner == True
    )
    
    # Role-based filtering for agents
    if current_user.role == "AGENT":
        # Create subqueries for assigned buildings and projects
        assigned_building_ids_subq = db.query(Building.building_id).filter(
            Building.assigned_agent_id == current_user.user_id,
            Building.is_deleted == False
        )
        
        assigned_project_ids_subq = db.query(Building.project_id).filter(
            Building.assigned_agent_id == current_user.user_id,
            Building.is_deleted == False
        ).distinct()
        
        # Filter projects that have assigned buildings
        project_query = project_query.filter(Project.project_id.in_(assigned_project_ids_subq))
        
        # Filter buildings assigned to agent
        building_query = building_query.filter(Building.assigned_agent_id == current_user.user_id)
        
        # Filter units from assigned buildings
        unit_query = unit_query.filter(Unit.building_id.in_(assigned_building_ids_subq))
        
        # Filter owners from units in assigned buildings
        owner_query = owner_query.join(Unit).filter(Unit.building_id.in_(assigned_building_ids_subq))
    
    # Total Projects
    total_projects = project_query.count()
    
    # Active Projects
    active_projects = project_query.filter(
        Project.project_stage.in_(["PLANNING", "ACTIVE", "APPROVAL"])
    ).count()
    
    # Total Buildings
    total_buildings = building_query.count()
    
    # Total Units
    total_units = unit_query.count()
    
    # Total Owners
    total_owners = owner_query.count()
    
    # Calculate overall signature percentage from assigned buildings only
    buildings = building_query.all()
    total_signature_sum = sum(float(b.signature_percentage or 0) for b in buildings)
    signed_percentage = total_signature_sum / len(buildings) if buildings else 0.0
    
    # Pending Approvals - filter by agent if needed
    approval_query = db.query(DocumentSignature).filter(
        DocumentSignature.signature_status == "SIGNED_PENDING_APPROVAL"
    )
    if current_user.role == "AGENT":
        # Only show approvals for owners assigned to this agent
        approval_query = approval_query.join(Owner).filter(
            Owner.assigned_agent_id == current_user.user_id
        )
    pending_approvals = approval_query.count()
    
    # Overdue Tasks - filter by agent if needed
    today = date.today()
    task_query = db.query(Task).filter(
        and_(
            Task.due_date < today,
            Task.status.in_(["NOT_STARTED", "IN_PROGRESS", "BLOCKED"])
        )
    )
    if current_user.role == "AGENT":
        # Only show tasks assigned to this agent
        task_query = task_query.filter(Task.assigned_to_agent_id == current_user.user_id)
    overdue_tasks = task_query.count()
    
    # Recent Interactions count (last 24 hours) - filter by agent if needed
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    interaction_query = db.query(Interaction).filter(
        Interaction.interaction_timestamp >= cutoff_time
    )
    if current_user.role == "AGENT":
        # Only show interactions by this agent
        interaction_query = interaction_query.filter(Interaction.agent_id == current_user.user_id)
    recent_interactions = interaction_query.count()
    
    # Projects by Stage - use filtered project_query
    projects_by_stage = db.query(
        Project.project_stage,
        func.count(Project.project_id).label('count')
    ).filter(
        Project.is_deleted == False
    )
    if current_user.role == "AGENT":
        # Filter by assigned project IDs
        assigned_project_ids = db.query(Building.project_id).filter(
            Building.assigned_agent_id == current_user.user_id,
            Building.is_deleted == False
        ).distinct()
        projects_by_stage = projects_by_stage.filter(Project.project_id.in_(assigned_project_ids))
    projects_by_stage = projects_by_stage.group_by(Project.project_stage).all()
    
    projects_by_stage_dict = {
        "PLANNING": 0,
        "ACTIVE": 0,
        "APPROVAL": 0,
        "COMPLETED": 0,
        "ARCHIVED": 0,
    }
    for stage, count in projects_by_stage:
        projects_by_stage_dict[stage] = count
    
    # Buildings by Status - use filtered building_query
    buildings_by_status_query = db.query(
        Building.current_status,
        func.count(Building.building_id).label('count')
    ).filter(
        Building.is_deleted == False
    )
    if current_user.role == "AGENT":
        # Filter by assigned buildings
        buildings_by_status_query = buildings_by_status_query.filter(
            Building.assigned_agent_id == current_user.user_id
        )
    buildings_by_status = buildings_by_status_query.group_by(Building.current_status).all()
    
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

