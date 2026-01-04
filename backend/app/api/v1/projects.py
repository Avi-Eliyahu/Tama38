"""
Projects API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.core.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.building import Building
from app.api.dependencies import get_current_user, require_role
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectCreate(BaseModel):
    project_name: str
    project_code: str
    project_type: str
    location_city: Optional[str] = None
    location_address: Optional[str] = None
    description: Optional[str] = None
    required_majority_percent: float
    critical_threshold_percent: float
    majority_calc_type: str
    launch_date: Optional[str] = None
    estimated_completion_date: Optional[str] = None


class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    description: Optional[str] = None
    project_stage: Optional[str] = None


class ProjectResponse(BaseModel):
    project_id: str
    project_name: str
    project_code: str
    project_type: str
    location_city: Optional[str]
    location_address: Optional[str]
    description: Optional[str]
    project_stage: str
    required_majority_percent: float
    critical_threshold_percent: float
    majority_calc_type: str
    created_at: str
    updated_at: str
    
    @classmethod
    def from_orm(cls, obj):
        """Convert SQLAlchemy model to Pydantic model with UUID to string conversion"""
        data = {
            'project_id': str(obj.project_id),
            'project_name': obj.project_name,
            'project_code': obj.project_code,
            'project_type': obj.project_type,
            'location_city': obj.location_city,
            'location_address': obj.location_address,
            'description': obj.description,
            'project_stage': obj.project_stage,
            'required_majority_percent': float(obj.required_majority_percent),
            'critical_threshold_percent': float(obj.critical_threshold_percent),
            'majority_calc_type': obj.majority_calc_type,
            'created_at': obj.created_at.isoformat() if obj.created_at else datetime.utcnow().isoformat(),
            'updated_at': obj.updated_at.isoformat() if obj.updated_at else datetime.utcnow().isoformat(),
        }
        return cls(**data)
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all projects (with role-based filtering)"""
    query = db.query(Project).filter(Project.is_deleted == False)
    
    # Filter by role (agents can only see projects with buildings assigned to them)
    if current_user.role == "AGENT":
        # Use subquery to find project_ids that have buildings assigned to this agent
        from sqlalchemy import exists
        assigned_project_ids = db.query(Building.project_id).filter(
            Building.assigned_agent_id == current_user.user_id,
            Building.is_deleted == False
        ).distinct()
        query = query.filter(Project.project_id.in_(assigned_project_ids))
    
    projects = query.order_by(desc(Project.created_at)).offset(skip).limit(limit).all()
    # Convert UUIDs to strings for response
    return [
        ProjectResponse(
            project_id=str(p.project_id),
            project_name=p.project_name,
            project_code=p.project_code,
            project_type=p.project_type,
            location_city=p.location_city,
            location_address=p.location_address,
            description=p.description,
            project_stage=p.project_stage,
            required_majority_percent=float(p.required_majority_percent),
            critical_threshold_percent=float(p.critical_threshold_percent),
            majority_calc_type=p.majority_calc_type,
            created_at=p.created_at.isoformat() if p.created_at else datetime.utcnow().isoformat(),
            updated_at=p.updated_at.isoformat() if p.updated_at else datetime.utcnow().isoformat(),
        )
        for p in projects
    ]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SUPER_ADMIN", "PROJECT_MANAGER"))
):
    """Create a new project"""
    # Check if project code already exists
    existing = db.query(Project).filter(Project.project_code == project_data.project_code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project code already exists"
        )
    
    project = Project(
        project_name=project_data.project_name,
        project_code=project_data.project_code,
        project_type=project_data.project_type,
        location_city=project_data.location_city,
        location_address=project_data.location_address,
        description=project_data.description,
        required_majority_percent=project_data.required_majority_percent,
        critical_threshold_percent=project_data.critical_threshold_percent,
        majority_calc_type=project_data.majority_calc_type,
        created_by=current_user.user_id,
        updated_by=current_user.user_id,
    )
    
    if project_data.launch_date:
        project.launch_date = datetime.fromisoformat(project_data.launch_date)
    if project_data.estimated_completion_date:
        project.estimated_completion_date = datetime.fromisoformat(project_data.estimated_completion_date)
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    logger.info(
        "Project created",
        extra={
            "project_id": str(project.project_id),
            "user_id": str(current_user.user_id),
        }
    )
    
    # Convert UUID to string for response
    return ProjectResponse(
        project_id=str(project.project_id),
        project_name=project.project_name,
        project_code=project.project_code,
        project_type=project.project_type,
        location_city=project.location_city,
        location_address=project.location_address,
        description=project.description,
        project_stage=project.project_stage,
        required_majority_percent=float(project.required_majority_percent),
        critical_threshold_percent=float(project.critical_threshold_percent),
        majority_calc_type=project.majority_calc_type,
        created_at=project.created_at.isoformat() if project.created_at else datetime.utcnow().isoformat(),
        updated_at=project.updated_at.isoformat() if project.updated_at else datetime.utcnow().isoformat(),
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get project details"""
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.is_deleted == False
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Role-based access control: Agents can only access projects with buildings assigned to them
    if current_user.role == "AGENT":
        # Check if agent has any buildings assigned in this project
        assigned_building = db.query(Building).filter(
            Building.project_id == project_id,
            Building.assigned_agent_id == current_user.user_id,
            Building.is_deleted == False
        ).first()
        
        if not assigned_building:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this project"
            )
    
    # Convert UUID to string for response
    return ProjectResponse(
        project_id=str(project.project_id),
        project_name=project.project_name,
        project_code=project.project_code,
        project_type=project.project_type,
        location_city=project.location_city,
        location_address=project.location_address,
        description=project.description,
        project_stage=project.project_stage,
        required_majority_percent=float(project.required_majority_percent),
        critical_threshold_percent=float(project.critical_threshold_percent),
        majority_calc_type=project.majority_calc_type,
        created_at=project.created_at.isoformat() if project.created_at else datetime.utcnow().isoformat(),
        updated_at=project.updated_at.isoformat() if project.updated_at else datetime.utcnow().isoformat(),
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SUPER_ADMIN", "PROJECT_MANAGER"))
):
    """Update project"""
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.is_deleted == False
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project_data.project_name:
        project.project_name = project_data.project_name
    if project_data.description is not None:
        project.description = project_data.description
    if project_data.project_stage:
        project.project_stage = project_data.project_stage
    
    project.updated_by = current_user.user_id
    project.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(project)
    
    # Convert UUID to string for response
    return ProjectResponse(
        project_id=str(project.project_id),
        project_name=project.project_name,
        project_code=project.project_code,
        project_type=project.project_type,
        location_city=project.location_city,
        location_address=project.location_address,
        description=project.description,
        project_stage=project.project_stage,
        required_majority_percent=float(project.required_majority_percent),
        critical_threshold_percent=float(project.critical_threshold_percent),
        majority_calc_type=project.majority_calc_type,
        created_at=project.created_at.isoformat() if project.created_at else datetime.utcnow().isoformat(),
        updated_at=project.updated_at.isoformat() if project.updated_at else datetime.utcnow().isoformat(),
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SUPER_ADMIN"))
):
    """Soft delete project and all related entities (buildings, units, owners)"""
    from app.models.building import Building
    from app.models.unit import Unit
    from app.models.owner import Owner
    
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.is_deleted == False
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Soft delete all related buildings
    buildings = db.query(Building).filter(
        Building.project_id == project_id,
        Building.is_deleted == False
    ).all()
    
    for building in buildings:
        building.is_deleted = True
        building.updated_at = datetime.utcnow()
        
        # Soft delete all units in this building
        units = db.query(Unit).filter(
            Unit.building_id == building.building_id,
            Unit.is_deleted == False
        ).all()
        
        for unit in units:
            unit.is_deleted = True
            unit.updated_at = datetime.utcnow()
            
            # Soft delete all owners of this unit
            owners = db.query(Owner).filter(
                Owner.unit_id == unit.unit_id,
                Owner.is_deleted == False
            ).all()
            
            for owner in owners:
                owner.is_deleted = True
                owner.updated_at = datetime.utcnow()
    
    # Soft delete the project
    project.is_deleted = True
    project.updated_by = current_user.user_id
    project.updated_at = datetime.utcnow()
    
    db.commit()
    
    return None

