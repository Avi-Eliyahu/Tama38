"""
Unit Status Calculation Service
Calculates unit status based on owner signatures: SIGNED, PARTIALLY_SIGNED, or NOT_SIGNED
"""
from sqlalchemy.orm import Session
from app.models.unit import Unit
from app.models.owner import Owner
import logging

logger = logging.getLogger(__name__)


def calculate_unit_status(unit_id: str, db: Session) -> str:
    """
    Calculate unit status based on owner signatures.
    
    Returns:
        - 'SIGNED': All owners have status 'SIGNED'
        - 'PARTIALLY_SIGNED': At least one owner signed but not all
        - 'NOT_SIGNED': No owners signed
    """
    unit = db.query(Unit).filter(Unit.unit_id == unit_id).first()
    if not unit:
        raise ValueError(f"Unit {unit_id} not found")
    
    # Get all current owners for this unit
    owners = db.query(Owner).filter(
        Owner.unit_id == unit_id,
        Owner.is_deleted == False,
        Owner.is_current_owner == True
    ).all()
    
    if not owners:
        # No owners - consider as NOT_CONTACTED
        return 'NOT_CONTACTED'
    
    # Count signed owners (only status == 'SIGNED' counts)
    signed_count = sum(1 for owner in owners if owner.owner_status == 'SIGNED')
    total_count = len(owners)
    
    if signed_count == total_count and total_count > 0:
        return 'SIGNED'
    elif signed_count > 0:
        return 'PARTIALLY_SIGNED'
    else:
        return 'NOT_CONTACTED'


def update_unit_status(unit_id: str, db: Session) -> str:
    """
    Calculate and update unit status in database.
    Returns the calculated status.
    """
    import json
    import time
    log_path = r'c:\projects\pinoy\.cursor\debug.log'
    
    unit = db.query(Unit).filter(Unit.unit_id == unit_id).first()
    if not unit:
        raise ValueError(f"Unit {unit_id} not found")
    
    # #region agent log
    try:
        old_unit_status = unit.unit_status
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"unit_status.py:55","message":"update_unit_status entry","data":{"unit_id":str(unit_id),"current_unit_status":old_unit_status},"timestamp":int(time.time()*1000)})+'\n')
    except: pass
    # #endregion
    
    # Get all current owners
    owners = db.query(Owner).filter(
        Owner.unit_id == unit_id,
        Owner.is_deleted == False,
        Owner.is_current_owner == True
    ).all()
    
    # Update counts
    unit.total_owners = len(owners)
    unit.owners_signed = sum(1 for owner in owners if owner.owner_status == 'SIGNED')
    
    # #region agent log
    try:
        owner_statuses = [o.owner_status for o in owners]
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"unit_status.py:70","message":"owner statuses before calculation","data":{"unit_id":str(unit_id),"total_owners":unit.total_owners,"owners_signed":unit.owners_signed,"owner_statuses":owner_statuses},"timestamp":int(time.time()*1000)})+'\n')
    except: pass
    # #endregion
    
    # Calculate status
    if not owners:
        new_status = 'NOT_CONTACTED'
    elif unit.owners_signed == unit.total_owners and unit.total_owners > 0:
        new_status = 'SIGNED'
    elif unit.owners_signed > 0:
        new_status = 'PARTIALLY_SIGNED'
    else:
        new_status = 'NOT_CONTACTED'
    
    # #region agent log
    try:
        will_update = unit.unit_status in ['NOT_CONTACTED', 'SIGNED', 'PARTIALLY_SIGNED']
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"unit_status.py:82","message":"status calculation result","data":{"unit_id":str(unit_id),"calculated_status":new_status,"current_status":old_unit_status,"will_update":will_update},"timestamp":int(time.time()*1000)})+'\n')
    except: pass
    # #endregion
    
    # Update unit status - ALWAYS update if all owners signed (regardless of current status)
    # If all owners signed, unit should be SIGNED
    if unit.owners_signed == unit.total_owners and unit.total_owners > 0:
        unit.unit_status = 'SIGNED'
    elif unit.unit_status in ['NOT_CONTACTED', 'SIGNED', 'PARTIALLY_SIGNED']:
        # Only update signature-related statuses, keep others like NEGOTIATING, REFUSED
        unit.unit_status = new_status
    
    # #region agent log
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"unit_status.py:95","message":"unit status after update","data":{"unit_id":str(unit_id),"old_status":old_unit_status,"new_status":unit.unit_status},"timestamp":int(time.time()*1000)})+'\n')
    except: pass
    # #endregion
    
    db.commit()
    
    logger.debug(
        f"Updated unit {unit_id} status",
        extra={
            "unit_id": str(unit_id),
            "old_status": unit.unit_status,
            "new_status": new_status,
            "total_owners": unit.total_owners,
            "owners_signed": unit.owners_signed,
        }
    )
    
    return new_status

