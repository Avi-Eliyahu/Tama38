"""
Majority Calculation Engine
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.building import Building
from app.models.unit import Unit
from app.models.owner import Owner
from app.models.document import DocumentSignature
from app.models.project import Project
import logging

logger = logging.getLogger(__name__)


def calculate_building_majority(building_id: str, db: Session) -> dict:
    """
    Calculate signature percentage for a building
    Returns: {
        "signature_percentage": float,
        "signature_percentage_by_area": float,
        "traffic_light_status": str,
        "total_owners": int,
        "owners_signed": int,
    }
    """
    building = db.query(Building).filter(Building.building_id == building_id).first()
    if not building:
        raise ValueError("Building not found")
    
    # Get project to determine calculation type
    project = db.query(Project).filter(Project.project_id == building.project_id).first()
    if not project:
        raise ValueError("Project not found")
    
    # Get all units in building
    units = db.query(Unit).filter(
        Unit.building_id == building_id,
        Unit.is_deleted == False
    ).all()
    
    total_owners = 0
    owners_signed = 0
    total_area = 0.0
    signed_area = 0.0
    
    for unit in units:
        # Get owners for this unit
        unit_owners = db.query(Owner).filter(
            Owner.unit_id == unit.unit_id,
            Owner.is_deleted == False,
            Owner.is_current_owner == True
        ).all()
        
        unit_total_owners = len(unit_owners)
        total_owners += unit_total_owners
        
        # Count signed owners (status = SIGNED and signature FINALIZED)
        unit_signed_count = 0
        for owner in unit_owners:
            if owner.owner_status == "SIGNED":
                # Check if signature is finalized
                signature = db.query(DocumentSignature).filter(
                    DocumentSignature.owner_id == owner.owner_id,
                    DocumentSignature.signature_status == "FINALIZED"
                ).first()
                if signature:
                    unit_signed_count += 1
        
        owners_signed += unit_signed_count
        
        # Area calculation
        if unit.area_sqm:
            total_area += float(unit.area_sqm)
            if unit_signed_count == unit_total_owners and unit_total_owners > 0:
                # All owners signed
                signed_area += float(unit.area_sqm)
            elif unit_signed_count > 0:
                # Partial signing - calculate by ownership share
                signed_share = unit_signed_count / unit_total_owners
                signed_area += float(unit.area_sqm) * signed_share
    
    # Calculate percentages
    signature_percentage = (owners_signed / total_owners * 100) if total_owners > 0 else 0.0
    signature_percentage_by_area = (signed_area / total_area * 100) if total_area > 0 else 0.0
    
    # Determine traffic light status
    required_majority = float(project.required_majority_percent)
    critical_threshold = float(project.critical_threshold_percent)
    
    if signature_percentage >= required_majority:
        traffic_light_status = "GREEN"
    elif signature_percentage >= critical_threshold:
        traffic_light_status = "YELLOW"
    else:
        traffic_light_status = "RED"
    
    # Update building record
    building.signature_percentage = signature_percentage
    building.signature_percentage_by_area = signature_percentage_by_area
    building.traffic_light_status = traffic_light_status
    
    # Count units by status
    building.units_signed = len([u for u in units if u.owners_signed == u.total_owners and u.total_owners > 0])
    building.units_partially_signed = len([u for u in units if u.owners_signed > 0 and u.owners_signed < u.total_owners])
    building.units_not_signed = len([u for u in units if u.owners_signed == 0])
    
    db.commit()
    
    logger.info(
        "Majority calculated",
        extra={
            "building_id": str(building_id),
            "signature_percentage": signature_percentage,
            "traffic_light": traffic_light_status,
            "calculation_time_ms": 0,  # TODO: Add timing
        }
    )
    
    return {
        "signature_percentage": float(signature_percentage),
        "signature_percentage_by_area": float(signature_percentage_by_area),
        "traffic_light_status": traffic_light_status,
        "total_owners": total_owners,
        "owners_signed": owners_signed,
        "total_units": len(units),
        "units_signed": building.units_signed,
        "units_partially_signed": building.units_partially_signed,
        "units_not_signed": building.units_not_signed,
    }

