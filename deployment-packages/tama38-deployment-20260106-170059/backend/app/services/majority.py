"""
Majority Calculation Engine
Calculates building/project progress based on signed units (not owners).
A unit is considered SIGNED only when ALL owners have signed.
PARTIALLY_SIGNED units count as 0% for progress calculation.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.building import Building
from app.models.unit import Unit
from app.models.owner import Owner
from app.models.project import Project
from app.services.unit_status import update_unit_status
import logging

logger = logging.getLogger(__name__)


def calculate_building_majority(building_id: str, db: Session) -> dict:
    """
    Calculate signature percentage for a building based on SIGNED units.
    
    HEADCOUNT method: (fully signed units) / (total units) × 100
    AREA method: (sum area of fully signed units) / (total area) × 100
    
    PARTIALLY_SIGNED units count as 0% (not included in numerator).
    
    Returns: {
        "signature_percentage": float,  # HEADCOUNT method
        "signature_percentage_by_area": float,  # AREA method
        "traffic_light_status": str,
        "total_units": int,
        "units_signed": int,
        "units_partially_signed": int,
        "units_not_signed": int,
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
    
    # Update unit statuses first
    for unit in units:
        update_unit_status(str(unit.unit_id), db)
    
    # Re-query units to get updated statuses
    units = db.query(Unit).filter(
        Unit.building_id == building_id,
        Unit.is_deleted == False
    ).all()
    
    # Count units by status
    units_signed = 0  # All owners signed
    units_partially_signed = 0  # Some owners signed
    units_not_signed = 0  # No owners signed
    total_area = 0.0
    signed_area = 0.0
    
    for unit in units:
        # Get owners for this unit
        unit_owners = db.query(Owner).filter(
            Owner.unit_id == unit.unit_id,
            Owner.is_deleted == False,
            Owner.is_current_owner == True
        ).all()
        
        if not unit_owners:
            units_not_signed += 1
            if unit.area_sqm:
                total_area += float(unit.area_sqm)
            continue
        
        # Count signed owners (only status == 'SIGNED' counts)
        signed_count = sum(1 for owner in unit_owners if owner.owner_status == 'SIGNED')
        total_count = len(unit_owners)
        
        # Area calculation
        if unit.area_sqm:
            total_area += float(unit.area_sqm)
        
        # Determine unit status
        if signed_count == total_count and total_count > 0:
            # All owners signed - unit is SIGNED
            units_signed += 1
            if unit.area_sqm:
                signed_area += float(unit.area_sqm)
        elif signed_count > 0:
            # Some owners signed - unit is PARTIALLY_SIGNED (counts as 0%)
            units_partially_signed += 1
            # signed_area remains unchanged (partial units don't count)
        else:
            # No owners signed - unit is NOT_SIGNED
            units_not_signed += 1
    
    total_units = len(units)
    
    # Calculate percentages based on calculation method
    # HEADCOUNT: signed units / total units
    signature_percentage = (units_signed / total_units * 100) if total_units > 0 else 0.0
    
    # AREA: signed area / total area
    signature_percentage_by_area = (signed_area / total_area * 100) if total_area > 0 else 0.0
    
    # Use the appropriate percentage based on project's majority_calc_type
    if project.majority_calc_type == 'AREA':
        percentage_for_traffic_light = signature_percentage_by_area
    else:  # HEADCOUNT or default
        percentage_for_traffic_light = signature_percentage
    
    # Determine traffic light status
    required_majority = float(project.required_majority_percent)
    critical_threshold = float(project.critical_threshold_percent)
    
    if percentage_for_traffic_light >= required_majority:
        traffic_light_status = "GREEN"
    elif percentage_for_traffic_light >= critical_threshold:
        traffic_light_status = "YELLOW"
    else:
        traffic_light_status = "RED"
    
    # Update building record
    building.signature_percentage = signature_percentage
    building.signature_percentage_by_area = signature_percentage_by_area
    building.traffic_light_status = traffic_light_status
    building.units_signed = units_signed
    building.units_partially_signed = units_partially_signed
    building.units_not_signed = units_not_signed
    
    db.commit()
    
    logger.info(
        "Majority calculated",
        extra={
            "building_id": str(building_id),
            "signature_percentage": signature_percentage,
            "signature_percentage_by_area": signature_percentage_by_area,
            "traffic_light": traffic_light_status,
            "units_signed": units_signed,
            "total_units": total_units,
            "calculation_method": project.majority_calc_type,
        }
    )
    
    return {
        "signature_percentage": float(signature_percentage),
        "signature_percentage_by_area": float(signature_percentage_by_area),
        "traffic_light_status": traffic_light_status,
        "total_units": total_units,
        "units_signed": units_signed,
        "units_partially_signed": units_partially_signed,
        "units_not_signed": units_not_signed,
    }


def calculate_project_majority(project_id: str, db: Session) -> dict:
    """
    Calculate signature percentage for a project based on SIGNED units across all buildings.
    
    HEADCOUNT: (fully signed units in project) / (total units in project) × 100
    AREA: (sum area of fully signed units) / (total area) × 100
    
    Returns: {
        "signature_percentage": float,
        "signature_percentage_by_area": float,
        "total_units": int,
        "units_signed": int,
        "units_partially_signed": int,
        "units_not_signed": int,
    }
    """
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise ValueError("Project not found")
    
    # Get all buildings in project
    buildings = db.query(Building).filter(
        Building.project_id == project_id,
        Building.is_deleted == False
    ).all()
    
    # Aggregate across all buildings
    total_units = 0
    units_signed = 0
    units_partially_signed = 0
    units_not_signed = 0
    total_area = 0.0
    signed_area = 0.0
    
    for building in buildings:
        # Recalculate building majority first
        calculate_building_majority(str(building.building_id), db)
        
        # Get units in this building
        units = db.query(Unit).filter(
            Unit.building_id == building.building_id,
            Unit.is_deleted == False
        ).all()
        
        total_units += len(units)
        units_signed += building.units_signed
        units_partially_signed += building.units_partially_signed
        units_not_signed += building.units_not_signed
        
        # Calculate area
        for unit in units:
            if unit.area_sqm:
                total_area += float(unit.area_sqm)
                # Check if unit is fully signed
                unit_owners = db.query(Owner).filter(
                    Owner.unit_id == unit.unit_id,
                    Owner.is_deleted == False,
                    Owner.is_current_owner == True
                ).all()
                if unit_owners:
                    signed_count = sum(1 for owner in unit_owners if owner.owner_status == 'SIGNED')
                    if signed_count == len(unit_owners):
                        signed_area += float(unit.area_sqm)
    
    # Calculate percentages
    signature_percentage = (units_signed / total_units * 100) if total_units > 0 else 0.0
    signature_percentage_by_area = (signed_area / total_area * 100) if total_area > 0 else 0.0
    
    logger.info(
        "Project majority calculated",
        extra={
            "project_id": str(project_id),
            "signature_percentage": signature_percentage,
            "signature_percentage_by_area": signature_percentage_by_area,
            "units_signed": units_signed,
            "total_units": total_units,
        }
    )
    
    return {
        "signature_percentage": float(signature_percentage),
        "signature_percentage_by_area": float(signature_percentage_by_area),
        "total_units": total_units,
        "units_signed": units_signed,
        "units_partially_signed": units_partially_signed,
        "units_not_signed": units_not_signed,
    }

