"""
Buildings API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.core.database import get_db
from app.models.user import User
from app.models.building import Building
from app.models.project import Project
from app.api.dependencies import get_current_user, require_role
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/buildings", tags=["buildings"])


class BuildingCreate(BaseModel):
    project_id: str
    building_name: str
    building_code: Optional[str] = None
    address: Optional[str] = None
    floor_count: Optional[int] = None
    total_units: Optional[int] = None
    structure_type: Optional[str] = None
    assigned_agent_id: Optional[str] = None


class BuildingResponse(BaseModel):
    building_id: str
    project_id: str
    building_name: str
    building_code: Optional[str]
    address: Optional[str]
    floor_count: Optional[int]
    total_units: Optional[int]
    current_status: str
    signature_percentage: float
    traffic_light_status: str
    assigned_agent_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[BuildingResponse])
async def list_buildings(
    project_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List buildings (optionally filtered by project)"""
    query = db.query(Building).filter(Building.is_deleted == False)
    
    if project_id:
        query = query.filter(Building.project_id == project_id)
    
    # Role-based filtering
    if current_user.role == "AGENT":
        # Agents see buildings assigned to them OR unassigned buildings (assigned_agent_id is None)
        query = query.filter(
            (Building.assigned_agent_id == current_user.user_id) |
            (Building.assigned_agent_id.is_(None))
        )
    
    buildings = query.offset(skip).limit(limit).all()
    
    # Convert UUIDs to strings for response
    return [
        BuildingResponse(
            building_id=str(b.building_id),
            project_id=str(b.project_id),
            building_name=b.building_name,
            building_code=b.building_code,
            address=b.address,
            floor_count=b.floor_count,
            total_units=b.total_units,
            current_status=b.current_status,
            signature_percentage=float(b.signature_percentage) if b.signature_percentage is not None else 0.0,
            traffic_light_status=b.traffic_light_status,
            assigned_agent_id=str(b.assigned_agent_id) if b.assigned_agent_id else None,
            created_at=b.created_at,
        )
        for b in buildings
    ]


@router.post("", response_model=BuildingResponse, status_code=status.HTTP_201_CREATED)
async def create_building(
    building_data: BuildingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new building"""
    # Verify project exists
    project = db.query(Project).filter(
        Project.project_id == building_data.project_id,
        Project.is_deleted == False
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    building = Building(
        project_id=UUID(building_data.project_id),
        building_name=building_data.building_name,
        building_code=building_data.building_code,
        address=building_data.address,
        floor_count=building_data.floor_count,
        total_units=building_data.total_units,
        structure_type=building_data.structure_type,
        assigned_agent_id=UUID(building_data.assigned_agent_id) if building_data.assigned_agent_id else None,
    )
    
    db.add(building)
    db.commit()
    db.refresh(building)
    
    logger.info(
        "Building created",
        extra={
            "building_id": str(building.building_id),
            "project_id": str(building.project_id),
            "user_id": str(current_user.user_id),
        }
    )
    
    # Convert UUIDs to strings for response
    return BuildingResponse(
        building_id=str(building.building_id),
        project_id=str(building.project_id),
        building_name=building.building_name,
        building_code=building.building_code,
        address=building.address,
        floor_count=building.floor_count,
        total_units=building.total_units,
        current_status=building.current_status,
        signature_percentage=float(building.signature_percentage),
        traffic_light_status=building.traffic_light_status,
        assigned_agent_id=str(building.assigned_agent_id) if building.assigned_agent_id else None,
        created_at=building.created_at,
    )


@router.get("/{building_id}", response_model=BuildingResponse)
async def get_building(
    building_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get building details"""
    building = db.query(Building).filter(
        Building.building_id == building_id,
        Building.is_deleted == False
    ).first()
    
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found"
        )
    
    # Convert UUIDs to strings for response
    return BuildingResponse(
        building_id=str(building.building_id),
        project_id=str(building.project_id),
        building_name=building.building_name,
        building_code=building.building_code,
        address=building.address,
        floor_count=building.floor_count,
        total_units=building.total_units,
        current_status=building.current_status,
        signature_percentage=float(building.signature_percentage),
        traffic_light_status=building.traffic_light_status,
        assigned_agent_id=str(building.assigned_agent_id) if building.assigned_agent_id else None,
        created_at=building.created_at,
    )


class BuildingUpdate(BaseModel):
    building_name: Optional[str] = None
    building_code: Optional[str] = None
    address: Optional[str] = None
    floor_count: Optional[int] = None
    total_units: Optional[int] = None
    assigned_agent_id: Optional[str] = None


@router.put("/{building_id}", response_model=BuildingResponse)
async def update_building(
    building_id: UUID,
    building_data: BuildingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SUPER_ADMIN", "PROJECT_MANAGER"))
):
    """Update building (admin/manager only)"""
    building = db.query(Building).filter(
        Building.building_id == building_id,
        Building.is_deleted == False
    ).first()
    
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found"
        )
    
    # Update fields
    if building_data.building_name is not None:
        building.building_name = building_data.building_name
    if building_data.building_code is not None:
        building.building_code = building_data.building_code
    if building_data.address is not None:
        building.address = building_data.address
    if building_data.floor_count is not None:
        building.floor_count = building_data.floor_count
    if building_data.total_units is not None:
        building.total_units = building_data.total_units
    
    # Handle agent assignment
    if building_data.assigned_agent_id is not None:
        if building_data.assigned_agent_id == "":
            # Unassign agent
            building.assigned_agent_id = None
        else:
            # Verify agent exists and is an AGENT role
            from app.models.user import User
            agent = db.query(User).filter(
                User.user_id == UUID(building_data.assigned_agent_id),
                User.role == "AGENT",
                User.is_active == True
            ).first()
            
            if not agent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Agent not found or inactive"
                )
            
            building.assigned_agent_id = UUID(building_data.assigned_agent_id)
    
    db.commit()
    db.refresh(building)
    
    logger.info(
        "Building updated",
        extra={
            "building_id": str(building_id),
            "user_id": str(current_user.user_id),
            "assigned_agent_id": str(building.assigned_agent_id) if building.assigned_agent_id else None,
        }
    )
    
    # Convert UUIDs to strings for response
    return BuildingResponse(
        building_id=str(building.building_id),
        project_id=str(building.project_id),
        building_name=building.building_name,
        building_code=building.building_code,
        address=building.address,
        floor_count=building.floor_count,
        total_units=building.total_units,
        current_status=building.current_status,
        signature_percentage=float(building.signature_percentage),
        traffic_light_status=building.traffic_light_status,
        assigned_agent_id=str(building.assigned_agent_id) if building.assigned_agent_id else None,
        created_at=building.created_at,
    )

