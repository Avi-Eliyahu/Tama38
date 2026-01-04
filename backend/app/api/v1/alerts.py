"""
Alerts API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from datetime import datetime, timedelta, date
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel
import logging

from app.core.database import get_db
from app.models.user import User
from app.models.alert import Alert, AlertRule
from app.models.building import Building
from app.models.task import Task
from app.models.document import DocumentSignature
from app.models.interaction import Interaction
from app.api.dependencies import get_current_user
from app.services.alert_engine import run_alert_checks

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/alerts", tags=["alerts"])


class AlertResponse(BaseModel):
    alert_id: str
    rule_id: Optional[str] = None
    alert_type: str
    severity: str
    title: str
    message: str
    project_id: Optional[str] = None
    building_id: Optional[str] = None
    owner_id: Optional[str] = None
    task_id: Optional[str] = None
    agent_id: Optional[str] = None
    status: str
    acknowledged_at: Optional[str] = None
    resolved_at: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True


class AlertAcknowledgeRequest(BaseModel):
    notes: Optional[str] = None


class AlertResolveRequest(BaseModel):
    resolution_notes: Optional[str] = None


@router.get("", response_model=List[AlertResponse])
async def get_alerts(
    status: Optional[str] = Query(None, description="Filter by status: ACTIVE, ACKNOWLEDGED, RESOLVED, DISMISSED"),
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    severity: Optional[str] = Query(None, description="Filter by severity: LOW, MEDIUM, HIGH, CRITICAL"),
    project_id: Optional[str] = Query(None),
    building_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get alerts (filtered by status, type, severity, project, building)"""
    query = db.query(Alert)
    
    # Role-based filtering
    if current_user.role == "AGENT":
        # Agents see alerts related to their assigned buildings/owners
        query = query.filter(
            or_(
                Alert.agent_id == current_user.user_id,
                Alert.building_id.in_(
                    db.query(Building.building_id).filter(
                        Building.assigned_agent_id == current_user.user_id
                    )
                )
            )
        )
    
    # Apply filters
    if status:
        query = query.filter(Alert.status == status)
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    if severity:
        query = query.filter(Alert.severity == severity)
    if project_id:
        query = query.filter(Alert.project_id == project_id)
    if building_id:
        query = query.filter(Alert.building_id == building_id)
    
    alerts = query.order_by(desc(Alert.created_at)).offset(skip).limit(limit).all()
    
    return [
        AlertResponse(
            alert_id=str(a.alert_id),
            rule_id=str(a.rule_id) if a.rule_id else None,
            alert_type=a.alert_type,
            severity=a.severity,
            title=a.title,
            message=a.message,
            project_id=str(a.project_id) if a.project_id else None,
            building_id=str(a.building_id) if a.building_id else None,
            owner_id=str(a.owner_id) if a.owner_id else None,
            task_id=str(a.task_id) if a.task_id else None,
            agent_id=str(a.agent_id) if a.agent_id else None,
            status=a.status,
            acknowledged_at=a.acknowledged_at.isoformat() if a.acknowledged_at else None,
            resolved_at=a.resolved_at.isoformat() if a.resolved_at else None,
            created_at=a.created_at.isoformat(),
        )
        for a in alerts
    ]


@router.get("/count")
async def get_alert_count(
    status: Optional[str] = Query("ACTIVE", description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get count of alerts (default: ACTIVE alerts)"""
    query = db.query(Alert)
    
    # Role-based filtering
    if current_user.role == "AGENT":
        query = query.filter(
            or_(
                Alert.agent_id == current_user.user_id,
                Alert.building_id.in_(
                    db.query(Building.building_id).filter(
                        Building.assigned_agent_id == current_user.user_id
                    )
                )
            )
        )
    
    if status:
        query = query.filter(Alert.status == status)
    
    count = query.count()
    
    return {
        "count": count,
        "status": status or "ALL"
    }


@router.get("/history", response_model=List[AlertResponse])
async def get_alert_history(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get alert history (resolved/dismissed alerts)"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(Alert).filter(
        Alert.created_at >= cutoff_date,
        Alert.status.in_(["RESOLVED", "DISMISSED"])
    )
    
    # Role-based filtering
    if current_user.role == "AGENT":
        query = query.filter(
            or_(
                Alert.agent_id == current_user.user_id,
                Alert.building_id.in_(
                    db.query(Building.building_id).filter(
                        Building.assigned_agent_id == current_user.user_id
                    )
                )
            )
        )
    
    alerts = query.order_by(desc(Alert.created_at)).offset(skip).limit(limit).all()
    
    return [
        AlertResponse(
            alert_id=str(a.alert_id),
            rule_id=str(a.rule_id) if a.rule_id else None,
            alert_type=a.alert_type,
            severity=a.severity,
            title=a.title,
            message=a.message,
            project_id=str(a.project_id) if a.project_id else None,
            building_id=str(a.building_id) if a.building_id else None,
            owner_id=str(a.owner_id) if a.owner_id else None,
            task_id=str(a.task_id) if a.task_id else None,
            agent_id=str(a.agent_id) if a.agent_id else None,
            status=a.status,
            acknowledged_at=a.acknowledged_at.isoformat() if a.acknowledged_at else None,
            resolved_at=a.resolved_at.isoformat() if a.resolved_at else None,
            created_at=a.created_at.isoformat(),
        )
        for a in alerts
    ]


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    request: AlertAcknowledgeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Acknowledge an alert"""
    alert = db.query(Alert).filter(Alert.alert_id == UUID(alert_id)).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if alert.status != "ACTIVE":
        raise HTTPException(status_code=400, detail=f"Alert is already {alert.status}")
    
    # Role-based access check
    if current_user.role == "AGENT":
        # Agents can only acknowledge alerts related to them
        if alert.agent_id != current_user.user_id:
            building = db.query(Building).filter(Building.building_id == alert.building_id).first()
            if not building or building.assigned_agent_id != current_user.user_id:
                raise HTTPException(status_code=403, detail="Not authorized to acknowledge this alert")
    
    alert.status = "ACKNOWLEDGED"
    alert.acknowledged_by_user_id = current_user.user_id
    alert.acknowledged_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alert)
    
    logger.info(f"Alert {alert_id} acknowledged by user {current_user.user_id}")
    
    return {
        "alert_id": str(alert.alert_id),
        "status": alert.status,
        "acknowledged_at": alert.acknowledged_at.isoformat()
    }


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    request: AlertResolveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resolve an alert"""
    alert = db.query(Alert).filter(Alert.alert_id == UUID(alert_id)).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if alert.status == "RESOLVED":
        raise HTTPException(status_code=400, detail="Alert is already resolved")
    
    # Only managers and admins can resolve alerts
    if current_user.role not in ["SUPER_ADMIN", "PROJECT_MANAGER"]:
        raise HTTPException(status_code=403, detail="Only managers can resolve alerts")
    
    alert.status = "RESOLVED"
    alert.resolved_by_user_id = current_user.user_id
    alert.resolved_at = datetime.utcnow()
    if request.resolution_notes:
        alert.resolution_notes = request.resolution_notes
    
    db.commit()
    db.refresh(alert)
    
    logger.info(f"Alert {alert_id} resolved by user {current_user.user_id}")
    
    return {
        "alert_id": str(alert.alert_id),
        "status": alert.status,
        "resolved_at": alert.resolved_at.isoformat()
    }


@router.post("/{alert_id}/dismiss")
async def dismiss_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Dismiss an alert (mark as dismissed)"""
    alert = db.query(Alert).filter(Alert.alert_id == UUID(alert_id)).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if alert.status == "RESOLVED":
        raise HTTPException(status_code=400, detail="Cannot dismiss a resolved alert")
    
    alert.status = "DISMISSED"
    alert.acknowledged_by_user_id = current_user.user_id
    alert.acknowledged_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alert)
    
    logger.info(f"Alert {alert_id} dismissed by user {current_user.user_id}")
    
    return {
        "alert_id": str(alert.alert_id),
        "status": alert.status,
        "dismissed_at": alert.acknowledged_at.isoformat()
    }


@router.post("/check")
async def trigger_alert_checks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually trigger alert checks (admin/manager only)"""
    if current_user.role not in ["SUPER_ADMIN", "PROJECT_MANAGER"]:
        raise HTTPException(status_code=403, detail="Only managers can trigger alert checks")
    
    try:
        result = run_alert_checks(db)
        return {
            "message": "Alert checks completed",
            "result": result
        }
    except Exception as e:
        logger.error(f"Error running alert checks: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to run alert checks: {str(e)}")

