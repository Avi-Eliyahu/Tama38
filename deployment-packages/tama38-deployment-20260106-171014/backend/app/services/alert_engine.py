"""
Alert Rules Engine
Checks conditions and generates alerts
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta, date
from typing import List
import logging

from app.models.alert import Alert, AlertRule
from app.models.building import Building
from app.models.task import Task
from app.models.document import DocumentSignature
from app.models.interaction import Interaction
from app.models.user import User
from app.models.owner import Owner

logger = logging.getLogger(__name__)


def check_threshold_violations(db: Session) -> List[Alert]:
    """Check for buildings below critical threshold"""
    alerts = []
    
    # Get all active buildings
    buildings = db.query(Building).filter(
        Building.is_deleted == False,
        Building.signature_percentage.isnot(None)
    ).all()
    
    for building in buildings:
        # Get project to check critical threshold
        project = building.project
        if not project:
            continue
        
        critical_threshold = float(project.critical_threshold_percent or 50.0) if project.critical_threshold_percent else 50.0
        signature_pct = float(building.signature_percentage or 0.0)
        
        # Check if building is below critical threshold
        if signature_pct < critical_threshold:
            # Check if alert already exists
            existing_alert = db.query(Alert).filter(
                Alert.building_id == building.building_id,
                Alert.alert_type == "THRESHOLD_VIOLATION",
                Alert.status == "ACTIVE"
            ).first()
            
            if not existing_alert:
                alert = Alert(
                    alert_type="THRESHOLD_VIOLATION",
                    severity="HIGH" if signature_pct < critical_threshold * 0.5 else "MEDIUM",
                    title=f"Building {building.building_name} below critical threshold",
                    message=f"Building {building.building_name} signature percentage ({signature_pct:.1f}%) is below critical threshold ({critical_threshold}%)",
                    building_id=building.building_id,
                    project_id=building.project_id,
                    alert_metadata={
                        "signature_percentage": signature_pct,
                        "critical_threshold": critical_threshold,
                        "traffic_light_status": building.traffic_light_status
                    },
                    delivery_channels=["IN_APP"],
                    status="ACTIVE"
                )
                db.add(alert)
                alerts.append(alert)
                logger.info(f"Created threshold violation alert for building {building.building_id}")
    
    db.commit()
    return alerts


def check_agent_inactivity(db: Session, days_threshold: int = 3) -> List[Alert]:
    """Check for agent inactivity (no interactions for X days)"""
    alerts = []
    
    cutoff_date = date.today() - timedelta(days=days_threshold)
    
    # Get all active agents
    agents = db.query(User).filter(
        User.role == "AGENT",
        User.is_active == True
    ).all()
    
    for agent in agents:
        # Check last interaction
        last_interaction = db.query(Interaction).filter(
            Interaction.agent_id == agent.user_id
        ).order_by(Interaction.interaction_date.desc()).first()
        
        if not last_interaction or last_interaction.interaction_date < cutoff_date:
            # Check if alert already exists
            existing_alert = db.query(Alert).filter(
                Alert.agent_id == agent.user_id,
                Alert.alert_type == "AGENT_INACTIVITY",
                Alert.status == "ACTIVE"
            ).first()
            
            if not existing_alert:
                days_inactive = (date.today() - last_interaction.interaction_date).days if last_interaction else days_threshold + 1
                
                alert = Alert(
                    alert_type="AGENT_INACTIVITY",
                    severity="MEDIUM",
                    title=f"Agent {agent.full_name or agent.email} inactive",
                    message=f"Agent {agent.full_name or agent.email} has no interactions for {days_inactive} days",
                    agent_id=agent.user_id,
                    alert_metadata={
                        "days_inactive": days_inactive,
                        "last_interaction_date": last_interaction.interaction_date.isoformat() if last_interaction else None
                    },
                    delivery_channels=["IN_APP"],
                    status="ACTIVE"
                )
                db.add(alert)
                alerts.append(alert)
                logger.info(f"Created inactivity alert for agent {agent.user_id}")
    
    db.commit()
    return alerts


def check_overdue_tasks(db: Session) -> List[Alert]:
    """Check for overdue tasks"""
    alerts = []
    
    today = date.today()
    
    # Get overdue tasks
    overdue_tasks = db.query(Task).filter(
        Task.due_date < today,
        Task.status.in_(["NOT_STARTED", "IN_PROGRESS", "BLOCKED"])
    ).all()
    
    for task in overdue_tasks:
        # Check if alert already exists
        existing_alert = db.query(Alert).filter(
            Alert.task_id == task.task_id,
            Alert.alert_type == "OVERDUE_TASK",
            Alert.status == "ACTIVE"
        ).first()
        
        if not existing_alert:
            days_overdue = (today - task.due_date).days
            
            alert = Alert(
                alert_type="OVERDUE_TASK",
                severity="HIGH" if task.priority == "CRITICAL" else "MEDIUM",
                title=f"Overdue task: {task.title}",
                message=f"Task '{task.title}' assigned to agent is {days_overdue} days overdue",
                task_id=task.task_id,
                agent_id=task.assigned_to_agent_id,
                building_id=task.building_id,
                owner_id=task.owner_id,
                alert_metadata={
                    "days_overdue": days_overdue,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat()
                },
                delivery_channels=["IN_APP"],
                status="ACTIVE"
            )
            db.add(alert)
            alerts.append(alert)
            logger.info(f"Created overdue task alert for task {task.task_id}")
    
    db.commit()
    return alerts


def check_pending_approvals(db: Session, days_threshold: int = 7) -> List[Alert]:
    """Check for pending approvals older than threshold"""
    alerts = []
    
    cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)
    
    # Get pending approvals
    pending_approvals = db.query(DocumentSignature).filter(
        DocumentSignature.signature_status == "SIGNED_PENDING_APPROVAL",
        DocumentSignature.created_at < cutoff_date
    ).all()
    
    for signature in pending_approvals:
        # Check if alert already exists (simplified check)
        existing_alert = db.query(Alert).filter(
            Alert.owner_id == signature.owner_id,
            Alert.alert_type == "PENDING_APPROVAL",
            Alert.status == "ACTIVE"
        ).first()
        
        if not existing_alert:
            days_pending = (datetime.utcnow() - signature.created_at).days
            
            # Get owner and building info
            from app.models.unit import Unit
            owner = db.query(Owner).filter(Owner.owner_id == signature.owner_id).first()
            building_id = None
            if owner and owner.unit_id:
                # Get building from owner's unit
                unit = db.query(Unit).filter(Unit.unit_id == owner.unit_id).first()
                if unit:
                    building_id = unit.building_id
            
            alert = Alert(
                alert_type="PENDING_APPROVAL",
                severity="HIGH" if days_pending > 14 else "MEDIUM",
                title=f"Pending approval for {owner.full_name if owner else 'Owner'}",
                message=f"Signature approval pending for {days_pending} days",
                owner_id=signature.owner_id,
                building_id=building_id,
                alert_metadata={
                    "signature_id": str(signature.signature_id),
                    "days_pending": days_pending,
                    "signed_at": signature.created_at.isoformat()
                },
                delivery_channels=["IN_APP"],
                status="ACTIVE"
            )
            db.add(alert)
            alerts.append(alert)
            logger.info(f"Created pending approval alert for signature {signature.signature_id}")
    
    db.commit()
    return alerts


def run_alert_checks(db: Session) -> dict:
    """Run all alert checks and return summary"""
    logger.info("Running alert checks...")
    
    threshold_alerts = check_threshold_violations(db)
    inactivity_alerts = check_agent_inactivity(db)
    overdue_alerts = check_overdue_tasks(db)
    approval_alerts = check_pending_approvals(db)
    
    total_alerts = len(threshold_alerts) + len(inactivity_alerts) + len(overdue_alerts) + len(approval_alerts)
    
    logger.info(f"Alert checks completed: {total_alerts} new alerts created")
    
    return {
        "threshold_violations": len(threshold_alerts),
        "agent_inactivity": len(inactivity_alerts),
        "overdue_tasks": len(overdue_alerts),
        "pending_approvals": len(approval_alerts),
        "total": total_alerts
    }

