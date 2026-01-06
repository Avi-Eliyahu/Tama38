"""
Database Models
Import all models here so Alembic can detect them
"""
from app.models.user import User
from app.models.project import Project
from app.models.building import Building
from app.models.unit import Unit
from app.models.owner import Owner
from app.models.interaction import Interaction
from app.models.document import Document, DocumentSignature
from app.models.task import Task
from app.models.wizard import WizardDraft
from app.models.audit import AuditLog
from app.models.alert import Alert, AlertRule

__all__ = [
    "User",
    "Project",
    "Building",
    "Unit",
    "Owner",
    "Interaction",
    "Document",
    "DocumentSignature",
    "Task",
    "WizardDraft",
    "AuditLog",
    "Alert",
    "AlertRule",
]
