"""
Agent Permission Service
Verifies agent access to buildings and owners
"""
from sqlalchemy.orm import Session
from app.models.building import Building
from app.models.owner import Owner
from app.models.unit import Unit
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


def verify_agent_has_building_access(agent_id: UUID, building_id: UUID, db: Session) -> bool:
    """
    Verify that an agent has access to a building.
    Agent has access if building.assigned_agent_id == agent_id
    """
    building = db.query(Building).filter(
        Building.building_id == building_id,
        Building.is_deleted == False
    ).first()
    
    if not building:
        return False
    
    return building.assigned_agent_id == agent_id


def verify_agent_has_owner_access(agent_id: UUID, owner_id: UUID, db: Session) -> bool:
    """
    Verify that an agent has access to an owner.
    Agent has access if:
    1. Owner is assigned to the agent (owner.assigned_agent_id == agent_id), OR
    2. Owner's unit's building is assigned to the agent
    """
    owner = db.query(Owner).filter(
        Owner.owner_id == owner_id,
        Owner.is_deleted == False
    ).first()
    
    if not owner:
        return False
    
    # Check if owner is directly assigned to agent
    if owner.assigned_agent_id == agent_id:
        return True
    
    # Check if owner's unit's building is assigned to agent
    unit = db.query(Unit).filter(
        Unit.unit_id == owner.unit_id,
        Unit.is_deleted == False
    ).first()
    
    if not unit:
        return False
    
    return verify_agent_has_building_access(agent_id, unit.building_id, db)

