"""
Units API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.core.database import get_db
from app.models.user import User
from app.models.unit import Unit
from app.models.building import Building
from app.api.dependencies import get_current_user, require_role
from app.services.unit_status import update_unit_status
from app.services.majority import calculate_building_majority, calculate_project_majority
from app.models.project import Project
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/units", tags=["units"])


class UnitCreate(BaseModel):
    building_id: str
    floor_number: Optional[int] = None
    unit_number: str
    unit_code: Optional[str] = None
    area_sqm: Optional[float] = None
    room_count: Optional[int] = None
    estimated_value_ils: Optional[float] = None


class UnitResponse(BaseModel):
    unit_id: str
    building_id: str
    floor_number: Optional[int]
    unit_number: str
    area_sqm: Optional[float]
    unit_status: str
    total_owners: int
    owners_signed: int
    signature_percentage: float
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[UnitResponse])
async def list_units(
    building_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List units (optionally filtered by building)"""
    query = db.query(Unit).filter(Unit.is_deleted == False)
    
    if building_id:
        query = query.filter(Unit.building_id == building_id)
    
    # Role-based filtering: Agents can only see units from buildings assigned to them
    if current_user.role == "AGENT":
        # Join with Building to filter by assigned_agent_id
        query = query.join(Building).filter(Building.assigned_agent_id == current_user.user_id)
    
    # Sort by unit_number (apartment number) - convert to integer for proper numeric sorting
    # Handle cases where unit_number might not be numeric
    from sqlalchemy import cast, Integer
    units = query.order_by(
        cast(Unit.unit_number, Integer).nulls_last(),
        Unit.unit_number
    ).offset(skip).limit(limit).all()
    # Convert UUIDs to strings for response
    return [
        UnitResponse(
            unit_id=str(u.unit_id),
            building_id=str(u.building_id),
            floor_number=u.floor_number,
            unit_number=u.unit_number,
            area_sqm=float(u.area_sqm) if u.area_sqm else None,
            unit_status=u.unit_status,
            total_owners=u.total_owners or 0,
            owners_signed=u.owners_signed or 0,
            signature_percentage=float(u.signature_percentage or 0),
            created_at=u.created_at,
        )
        for u in units
    ]


@router.post("", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
async def create_unit(
    unit_data: UnitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new unit"""
    # Verify building exists
    building = db.query(Building).filter(
        Building.building_id == unit_data.building_id,
        Building.is_deleted == False
    ).first()
    
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found"
        )
    
    # Generate unit_full_identifier
    unit_full_identifier = f"{unit_data.floor_number or 0}-{unit_data.unit_number}"
    
    unit = Unit(
        building_id=UUID(unit_data.building_id),
        floor_number=unit_data.floor_number,
        unit_number=unit_data.unit_number,
        unit_code=unit_data.unit_code,
        unit_full_identifier=unit_full_identifier,
        area_sqm=unit_data.area_sqm,
        room_count=unit_data.room_count,
        estimated_value_ils=unit_data.estimated_value_ils,
    )
    
    db.add(unit)
    db.commit()
    db.refresh(unit)
    
    logger.info(
        "Unit created",
        extra={
            "unit_id": str(unit.unit_id),
            "building_id": str(unit.building_id),
            "user_id": str(current_user.user_id),
        }
    )
    
    # Convert UUIDs to strings for response
    return UnitResponse(
        unit_id=str(unit.unit_id),
        building_id=str(unit.building_id),
        floor_number=unit.floor_number,
        unit_number=unit.unit_number,
        area_sqm=float(unit.area_sqm) if unit.area_sqm else None,
        unit_status=unit.unit_status,
        total_owners=unit.total_owners or 0,
        owners_signed=unit.owners_signed or 0,
        signature_percentage=float(unit.signature_percentage or 0),
        created_at=unit.created_at,
    )


@router.get("/{unit_id}", response_model=UnitResponse)
async def get_unit(
    unit_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get unit details"""
    unit = db.query(Unit).filter(
        Unit.unit_id == unit_id,
        Unit.is_deleted == False
    ).first()
    
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )
    
    # Role-based access control: Agents can only access units from buildings assigned to them
    if current_user.role == "AGENT":
        building = db.query(Building).filter(Building.building_id == unit.building_id).first()
        if not building or building.assigned_agent_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this unit"
            )
    
    # Convert UUIDs to strings for response
    return UnitResponse(
        unit_id=str(unit.unit_id),
        building_id=str(unit.building_id),
        floor_number=unit.floor_number,
        unit_number=unit.unit_number,
        area_sqm=float(unit.area_sqm) if unit.area_sqm else None,
        unit_status=unit.unit_status,
        total_owners=unit.total_owners or 0,
        owners_signed=unit.owners_signed or 0,
        signature_percentage=float(unit.signature_percentage or 0),
        created_at=unit.created_at,
    )


@router.post("/{unit_id}/recalculate-status")
async def recalculate_unit_status(
    unit_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SUPER_ADMIN", "PROJECT_MANAGER"))
):
    """Recalculate unit status based on owner signatures and cascade to building/project"""
    unit = db.query(Unit).filter(
        Unit.unit_id == unit_id,
        Unit.is_deleted == False
    ).first()
    
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )
    
    old_status = unit.unit_status
    
    # Recalculate unit status
    new_status = update_unit_status(str(unit_id), db)
    db.refresh(unit)
    
    # Cascade to building and project
    building = db.query(Building).filter(Building.building_id == unit.building_id).first()
    if building:
        calculate_building_majority(str(building.building_id), db)
        project = db.query(Project).filter(Project.project_id == building.project_id).first()
        if project:
            calculate_project_majority(str(project.project_id), db)
    
    logger.info(
        "Unit status recalculated",
        extra={
            "unit_id": str(unit_id),
            "old_status": old_status,
            "new_status": new_status,
            "user_id": str(current_user.user_id),
        }
    )
    
    return {
        "unit_id": str(unit_id),
        "old_status": old_status,
        "new_status": new_status,
        "unit_status": unit.unit_status,
        "total_owners": unit.total_owners,
        "owners_signed": unit.owners_signed,
    }

