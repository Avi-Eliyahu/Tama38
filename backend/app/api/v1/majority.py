"""
Majority Engine API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.database import get_db
from app.models.user import User
from app.models.building import Building
from app.api.dependencies import get_current_user
from app.services.majority import calculate_building_majority
import logging
import time

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/buildings", tags=["majority"])


@router.get("/{building_id}/majority")
async def get_building_majority(
    building_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current majority calculation for a building"""
    building = db.query(Building).filter(
        Building.building_id == building_id,
        Building.is_deleted == False
    ).first()
    
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found"
        )
    
    # Calculate majority
    start_time = time.time()
    result = calculate_building_majority(str(building_id), db)
    calculation_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    # Log performance
    if calculation_time > 3000:
        logger.warning(
            "Majority calculation exceeded 3 seconds",
            extra={
                "building_id": str(building_id),
                "calculation_time_ms": calculation_time,
            }
        )
    
    result["calculation_time_ms"] = calculation_time
    return result


@router.post("/{building_id}/recalculate")
async def recalculate_majority(
    building_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Force recalculation of majority for a building"""
    building = db.query(Building).filter(
        Building.building_id == building_id,
        Building.is_deleted == False
    ).first()
    
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found"
        )
    
    start_time = time.time()
    result = calculate_building_majority(str(building_id), db)
    calculation_time = (time.time() - start_time) * 1000
    
    logger.info(
        "Majority recalculated",
        extra={
            "building_id": str(building_id),
            "user_id": str(current_user.user_id),
            "calculation_time_ms": calculation_time,
        }
    )
    
    result["calculation_time_ms"] = calculation_time
    return result

