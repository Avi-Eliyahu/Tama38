"""
Task Creation Service
Creates approval tasks for managers/admins
"""
from sqlalchemy.orm import Session
from app.models.task import Task
from app.models.user import User
from app.models.building import Building
from app.models.owner import Owner
from uuid import UUID
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def create_signature_approval_task(
    owner_id: UUID,
    building_id: UUID,
    requested_by_agent_id: UUID,
    db: Session
) -> Task:
    """
    Create an approval task for managers/admins to approve owner signature.
    
    Returns the created task.
    """
    # Get owner and building info for task description
    from app.models.unit import Unit
    owner = db.query(Owner).filter(Owner.owner_id == owner_id).first()
    building = db.query(Building).filter(Building.building_id == building_id).first()
    
    if not owner or not building:
        raise ValueError("Owner or building not found")
    
    # Get unit info for description
    unit = db.query(Unit).filter(Unit.unit_id == owner.unit_id).first()
    unit_number = unit.unit_number if unit else 'N/A'
    
    # Get all managers and admins
    managers = db.query(User).filter(
        User.role.in_(["PROJECT_MANAGER", "SUPER_ADMIN"]),
        User.is_active == True
    ).all()
    
    if not managers:
        raise ValueError("No managers or admins found to assign task")
    
    # For now, assign to first manager/admin (could be enhanced to assign to all or distribute)
    assigned_manager = managers[0]
    
    # Create task
    task = Task(
        building_id=building_id,
        owner_id=owner_id,
        task_type="MANAGER_REVIEW",
        title=f"Approve signature for {owner.full_name}",
        description=f"Agent has requested approval to mark {owner.full_name} (Unit {unit_number}, Building {building.building_name}) as SIGNED.",
        assigned_to_agent_id=assigned_manager.user_id,  # Note: assigned_to_agent_id field is used for managers too
        assigned_by_user_id=requested_by_agent_id,
        due_date=(datetime.utcnow() + timedelta(days=2)).date(),  # 2 days to approve
        priority="HIGH",
        status="NOT_STARTED"
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    logger.info(
        "Signature approval task created",
        extra={
            "task_id": str(task.task_id),
            "owner_id": str(owner_id),
            "building_id": str(building_id),
            "requested_by": str(requested_by_agent_id),
            "assigned_to": str(assigned_manager.user_id),
        }
    )
    
    return task

