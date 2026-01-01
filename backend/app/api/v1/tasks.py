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
from app.api.dependencies import get_current_user
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

