"""
Tasks API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date
from app.core.database import get_db
from app.models.user import User
from app.models.task import Task
from app.api.dependencies import get_current_user, require_role
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskCreate(BaseModel):
    building_id: Optional[str] = None
    owner_id: Optional[str] = None
    task_type: str
    title: str
    description: Optional[str] = None
    assigned_to_agent_id: str
    due_date: Optional[str] = None
    priority: Optional[str] = "MEDIUM"


class TaskResponse(BaseModel):
    task_id: str
    building_id: Optional[str]
    owner_id: Optional[str]
    task_type: str
    title: str
    description: Optional[str]
    assigned_to_agent_id: str
    due_date: Optional[date]
    status: str
    priority: str
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new task"""
    task = Task(
        building_id=UUID(task_data.building_id) if task_data.building_id else None,
        owner_id=UUID(task_data.owner_id) if task_data.owner_id else None,
        task_type=task_data.task_type,
        title=task_data.title,
        description=task_data.description,
        assigned_to_agent_id=UUID(task_data.assigned_to_agent_id),
        assigned_by_user_id=current_user.user_id,
        due_date=datetime.fromisoformat(task_data.due_date).date() if task_data.due_date else None,
        priority=task_data.priority,
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    logger.info(
        "Task created",
        extra={
            "task_id": str(task.task_id),
            "assigned_to": str(task.assigned_to_agent_id),
            "created_by": str(current_user.user_id),
        }
    )
    
    # Convert UUIDs to strings for response
    return TaskResponse(
        task_id=str(task.task_id),
        building_id=str(task.building_id) if task.building_id else None,
        owner_id=str(task.owner_id) if task.owner_id else None,
        task_type=task.task_type,
        title=task.title,
        description=task.description,
        assigned_to_agent_id=str(task.assigned_to_agent_id),
        due_date=task.due_date,
        status=task.status,
        priority=task.priority,
        created_at=task.created_at,
    )


@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    assigned_to: Optional[UUID] = Query(None),
    status_filter: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List tasks"""
    query = db.query(Task)
    
    if assigned_to:
        query = query.filter(Task.assigned_to_agent_id == assigned_to)
    elif current_user.role == "AGENT":
        # Agents see only their tasks
        query = query.filter(Task.assigned_to_agent_id == current_user.user_id)
    
    if status_filter:
        query = query.filter(Task.status == status_filter)
    
    tasks = query.order_by(desc(Task.created_at)).offset(skip).limit(limit).all()
    # Convert UUIDs to strings for response
    return [
        TaskResponse(
            task_id=str(t.task_id),
            building_id=str(t.building_id) if t.building_id else None,
            owner_id=str(t.owner_id) if t.owner_id else None,
            task_type=t.task_type,
            title=t.title,
            description=t.description,
            assigned_to_agent_id=str(t.assigned_to_agent_id),
            due_date=t.due_date,
            status=t.status,
            priority=t.priority,
            created_at=t.created_at,
        )
        for t in tasks
    ]


@router.get("/my-tasks", response_model=List[TaskResponse])
async def get_my_tasks(
    status_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's tasks"""
    query = db.query(Task).filter(Task.assigned_to_agent_id == current_user.user_id)
    
    if status_filter:
        query = query.filter(Task.status == status_filter)
    
    tasks = query.order_by(desc(Task.created_at)).all()
    # Convert UUIDs to strings for response
    return [
        TaskResponse(
            task_id=str(t.task_id),
            building_id=str(t.building_id) if t.building_id else None,
            owner_id=str(t.owner_id) if t.owner_id else None,
            task_type=t.task_type,
            title=t.title,
            description=t.description,
            assigned_to_agent_id=str(t.assigned_to_agent_id),
            due_date=t.due_date,
            status=t.status,
            priority=t.priority,
            created_at=t.created_at,
        )
        for t in tasks
    ]


@router.get("/overdue", response_model=List[TaskResponse])
async def get_overdue_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overdue tasks"""
    today = date.today()
    query = db.query(Task).filter(
        and_(
            Task.due_date < today,
            Task.status.in_(["NOT_STARTED", "IN_PROGRESS", "BLOCKED"])
        )
    )
    
    if current_user.role == "AGENT":
        query = query.filter(Task.assigned_to_agent_id == current_user.user_id)
    
    tasks = query.order_by(Task.due_date).all()
    # Convert UUIDs to strings for response
    return [
        TaskResponse(
            task_id=str(t.task_id),
            building_id=str(t.building_id) if t.building_id else None,
            owner_id=str(t.owner_id) if t.owner_id else None,
            task_type=t.task_type,
            title=t.title,
            description=t.description,
            assigned_to_agent_id=str(t.assigned_to_agent_id),
            due_date=t.due_date,
            status=t.status,
            priority=t.priority,
            created_at=t.created_at,
        )
        for t in tasks
    ]


@router.put("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark task as completed"""
    task = db.query(Task).filter(Task.task_id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check permission
    if current_user.role == "AGENT" and task.assigned_to_agent_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only complete your own tasks"
        )
    
    task.status = "COMPLETED"
    task.completed_at = datetime.utcnow()
    
    # If this is a MANAGER_REVIEW task with an owner_id, it means signature approval
    # But we don't auto-approve here - use the approve-signature endpoint instead
    # This endpoint just marks the task as completed
    
    db.commit()
    db.refresh(task)
    
    # Convert UUIDs to strings for response
    return TaskResponse(
        task_id=str(task.task_id),
        building_id=str(task.building_id) if task.building_id else None,
        owner_id=str(task.owner_id) if task.owner_id else None,
        task_type=task.task_type,
        title=task.title,
        description=task.description,
        assigned_to_agent_id=str(task.assigned_to_agent_id),
        due_date=task.due_date,
        status=task.status,
        priority=task.priority,
        created_at=task.created_at,
    )


class SignatureApprovalRequest(BaseModel):
    notes: Optional[str] = None


class SignatureApprovalResponse(BaseModel):
    task_id: str
    owner_id: str
    owner_status: str
    message: str


@router.post("/{task_id}/approve-signature", response_model=SignatureApprovalResponse)
async def approve_signature(
    task_id: UUID,
    approval_data: Optional[SignatureApprovalRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SUPER_ADMIN", "PROJECT_MANAGER"))
):
    """Approve signature via task (manager/admin only)"""
    task = db.query(Task).filter(Task.task_id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Verify this is a MANAGER_REVIEW task
    if task.task_type != "MANAGER_REVIEW":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This endpoint is only for MANAGER_REVIEW tasks"
        )
    
    # Verify task is assigned to current user (or allow any manager/admin)
    if task.assigned_to_agent_id != current_user.user_id and current_user.role != "SUPER_ADMIN":
        # Allow super admins to approve any task, but managers can only approve their own
        if current_user.role == "PROJECT_MANAGER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only approve tasks assigned to you"
            )
    
    if not task.owner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task does not have an associated owner"
        )
    
    # Get owner
    from app.models.owner import Owner
    owner = db.query(Owner).filter(Owner.owner_id == task.owner_id).first()
    
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found"
        )
    
    # Verify owner is in WAIT_FOR_SIGN status
    if owner.owner_status != "WAIT_FOR_SIGN":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Owner is not in WAIT_FOR_SIGN status. Current status: {owner.owner_status}"
        )
    
    # Update owner status to SIGNED
    owner.owner_status = "SIGNED"
    owner.signature_date = datetime.utcnow().date()
    
    # Mark task as completed
    task.status = "COMPLETED"
    task.completed_at = datetime.utcnow()
    if approval_data and approval_data.notes:
        task.notes = (task.notes or "") + f"\n[Approval Notes]: {approval_data.notes}"
    
    db.commit()
    
    # Trigger cascade recalculation
    from app.models.unit import Unit
    from app.models.building import Building
    from app.services.unit_status import update_unit_status
    from app.services.majority import calculate_building_majority, calculate_project_majority
    import json
    import time
    log_path = r'c:\projects\pinoy\.cursor\debug.log'
    
    # #region agent log
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"tasks.py:333","message":"starting cascade recalculation","data":{"owner_id":str(task.owner_id),"owner_status":owner.owner_status,"unit_id":str(owner.unit_id)},"timestamp":int(time.time()*1000)})+'\n')
    except: pass
    # #endregion
    
    unit = db.query(Unit).filter(Unit.unit_id == owner.unit_id).first()
    if unit:
        try:
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"tasks.py:342","message":"calling update_unit_status","data":{"unit_id":str(unit.unit_id),"building_id":str(unit.building_id)},"timestamp":int(time.time()*1000)})+'\n')
            except: pass
            # #endregion
            
            updated_status = update_unit_status(str(unit.unit_id), db)
            
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"tasks.py:347","message":"unit status updated","data":{"unit_id":str(unit.unit_id),"updated_status":updated_status},"timestamp":int(time.time()*1000)})+'\n')
            except: pass
            # #endregion
            
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"tasks.py:350","message":"calling calculate_building_majority","data":{"building_id":str(unit.building_id)},"timestamp":int(time.time()*1000)})+'\n')
            except: pass
            # #endregion
            
            building_result = calculate_building_majority(str(unit.building_id), db)
            
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"tasks.py:355","message":"building majority calculated","data":{"building_id":str(unit.building_id),"signature_percentage":building_result.get("signature_percentage"),"units_signed":building_result.get("units_signed")},"timestamp":int(time.time()*1000)})+'\n')
            except: pass
            # #endregion
            
            building = db.query(Building).filter(Building.building_id == unit.building_id).first()
            if building:
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"tasks.py:361","message":"calling calculate_project_majority","data":{"project_id":str(building.project_id)},"timestamp":int(time.time()*1000)})+'\n')
                except: pass
                # #endregion
                
                project_result = calculate_project_majority(str(building.project_id), db)
                
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"tasks.py:366","message":"project majority calculated","data":{"project_id":str(building.project_id),"signature_percentage":project_result.get("signature_percentage"),"units_signed":project_result.get("units_signed")},"timestamp":int(time.time()*1000)})+'\n')
                except: pass
                # #endregion
        except Exception as e:
            # #region agent log
            try:
                import traceback
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"tasks.py:372","message":"cascade recalculation error","data":{"error":str(e),"traceback":traceback.format_exc()},"timestamp":int(time.time()*1000)})+'\n')
            except: pass
            # #endregion
            logger.error(f"Failed to recalculate progress after signature approval: {e}")
            # Don't fail the request, just log
    
    logger.info(
        "Signature approved via task",
        extra={
            "task_id": str(task_id),
            "owner_id": str(task.owner_id),
            "approved_by": str(current_user.user_id),
        }
    )
    
    return SignatureApprovalResponse(
        task_id=str(task_id),
        owner_id=str(task.owner_id),
        owner_status="SIGNED",
        message=f"Owner signature approved. Status updated to SIGNED."
    )

