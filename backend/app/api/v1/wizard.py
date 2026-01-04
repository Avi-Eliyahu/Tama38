"""
Project Creation Wizard API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.building import Building
from app.models.unit import Unit
from app.models.owner import Owner
from app.models.wizard import WizardDraft
from app.api.dependencies import get_current_user, require_role
from sqlalchemy.orm.attributes import flag_modified
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/projects/wizard", tags=["wizard"])


class WizardStep1(BaseModel):
    project_name: str
    project_code: str
    project_type: str
    location_city: Optional[str] = None
    location_address: Optional[str] = None
    description: Optional[str] = None
    required_majority_percent: float
    critical_threshold_percent: float
    majority_calc_type: str
    launch_date: Optional[str] = None
    estimated_completion_date: Optional[str] = None


class WizardStep2Building(BaseModel):
    building_name: str
    building_code: Optional[str] = None
    address: Optional[str] = None
    floor_count: Optional[int] = None
    structure_type: Optional[str] = None


class WizardStep2(BaseModel):
    buildings: list[WizardStep2Building]


class WizardStep3Unit(BaseModel):
    building_index: int
    unit_number: str
    floor_number: Optional[int] = None
    area_sqm: Optional[float] = None
    room_count: Optional[int] = None


class WizardStep3(BaseModel):
    units: list[WizardStep3Unit]


class WizardStep4Owner(BaseModel):
    unit_index: int
    full_name: str
    id_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    ownership_share_percent: float
    preferred_contact_method: Optional[str] = None
    preferred_language: Optional[str] = None
    link_to_existing: Optional[bool] = False
    existing_owner_id: Optional[str] = None


class WizardStep4(BaseModel):
    owners: list[WizardStep4Owner]


class WizardStartResponse(BaseModel):
    draft_id: str
    expires_at: datetime


class WizardStepRequest(BaseModel):
    draft_id: str
    data: dict


@router.post("/start", response_model=WizardStartResponse)
async def start_wizard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SUPER_ADMIN", "PROJECT_MANAGER"))
):
    """Initialize wizard session"""
    draft = WizardDraft(
        user_id=current_user.user_id,
        step_data={},
        current_step=1,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    
    db.add(draft)
    db.commit()
    db.refresh(draft)
    
    logger.info(
        "Wizard started",
        extra={
            "draft_id": str(draft.draft_id),
            "user_id": str(current_user.user_id),
        }
    )
    
    return WizardStartResponse(
        draft_id=str(draft.draft_id),
        expires_at=draft.expires_at,
    )


@router.post("/step/1")
async def save_step_1(
    step_request: WizardStepRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SUPER_ADMIN", "PROJECT_MANAGER"))
):
    """Save Step 1: Project Information"""
    draft = db.query(WizardDraft).filter(
        WizardDraft.draft_id == step_request.draft_id,
        WizardDraft.user_id == current_user.user_id,
        WizardDraft.is_completed == False
    ).first()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found or already completed"
        )
    
    # Initialize step_data if None
    if draft.step_data is None:
        draft.step_data = {}
    
    draft.step_data["step1"] = step_request.data
    flag_modified(draft, "step_data")  # Mark JSON column as modified
    draft.current_step = 2
    draft.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Step 1 saved", "current_step": 2}


@router.post("/step/2")
async def save_step_2(
    step_request: WizardStepRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SUPER_ADMIN", "PROJECT_MANAGER"))
):
    """Save Step 2: Buildings Setup"""
    draft = db.query(WizardDraft).filter(
        WizardDraft.draft_id == step_request.draft_id,
        WizardDraft.user_id == current_user.user_id,
        WizardDraft.is_completed == False
    ).first()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found or already completed"
        )
    
    # Initialize step_data if None
    if draft.step_data is None:
        draft.step_data = {}
    
    if "step1" not in draft.step_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Step 1 must be completed first"
        )
    
    draft.step_data["step2"] = step_request.data
    flag_modified(draft, "step_data")  # Mark JSON column as modified
    draft.current_step = 3
    draft.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Step 2 saved", "current_step": 3}


@router.post("/step/3")
async def save_step_3(
    step_request: WizardStepRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SUPER_ADMIN", "PROJECT_MANAGER"))
):
    """Save Step 3: Units Setup"""
    draft = db.query(WizardDraft).filter(
        WizardDraft.draft_id == step_request.draft_id,
        WizardDraft.user_id == current_user.user_id,
        WizardDraft.is_completed == False
    ).first()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found or already completed"
        )
    
    # Initialize step_data if None
    if draft.step_data is None:
        draft.step_data = {}
    
    if "step2" not in draft.step_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Step 2 must be completed first"
        )
    
    draft.step_data["step3"] = step_request.data
    flag_modified(draft, "step_data")  # Mark JSON column as modified
    draft.current_step = 4
    draft.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Step 3 saved", "current_step": 4}


@router.post("/step/4")
async def save_step_4(
    step_request: WizardStepRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SUPER_ADMIN", "PROJECT_MANAGER"))
):
    """Save Step 4: Owners Setup"""
    draft = db.query(WizardDraft).filter(
        WizardDraft.draft_id == step_request.draft_id,
        WizardDraft.user_id == current_user.user_id,
        WizardDraft.is_completed == False
    ).first()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found or already completed"
        )
    
    # Initialize step_data if None
    if draft.step_data is None:
        draft.step_data = {}
    
    if "step3" not in draft.step_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Step 3 must be completed first"
        )
    
    draft.step_data["step4"] = step_request.data
    flag_modified(draft, "step_data")  # Mark JSON column as modified
    draft.current_step = 5
    draft.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Step 4 saved", "current_step": 5}


@router.get("/draft/{draft_id}")
async def get_draft(
    draft_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SUPER_ADMIN", "PROJECT_MANAGER"))
):
    """Retrieve saved draft"""
    draft = db.query(WizardDraft).filter(
        WizardDraft.draft_id == draft_id,
        WizardDraft.user_id == current_user.user_id,
        WizardDraft.is_completed == False
    ).first()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found"
        )
    
    if draft.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Draft has expired"
        )
    
    return {
        "draft_id": str(draft.draft_id),
        "current_step": draft.current_step,
        "step_data": draft.step_data,
        "expires_at": draft.expires_at,
    }


class WizardCompleteRequest(BaseModel):
    draft_id: str

@router.post("/complete")
async def complete_wizard(
    complete_request: WizardCompleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SUPER_ADMIN", "PROJECT_MANAGER"))
):
    """Finalize wizard and create project with all entities"""
    draft = db.query(WizardDraft).filter(
        WizardDraft.draft_id == complete_request.draft_id,
        WizardDraft.user_id == current_user.user_id,
        WizardDraft.is_completed == False
    ).first()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found or already completed"
        )
    
    step_data = draft.step_data
    
    # Validate all steps are present
    if not all(key in step_data for key in ["step1", "step2", "step3", "step4"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All steps must be completed"
        )
    
    step1 = step_data["step1"]
    step2 = step_data["step2"]
    step3 = step_data["step3"]
    step4 = step_data["step4"]
    
    try:
        # Create project
        project = Project(
            project_name=step1["project_name"],
            project_code=step1["project_code"],
            project_type=step1["project_type"],
            location_city=step1.get("location_city"),
            location_address=step1.get("location_address"),
            description=step1.get("description"),
            required_majority_percent=step1["required_majority_percent"],
            critical_threshold_percent=step1["critical_threshold_percent"],
            majority_calc_type=step1["majority_calc_type"],
            created_by=current_user.user_id,
            updated_by=current_user.user_id,
        )
        
        if step1.get("launch_date"):
            project.launch_date = datetime.fromisoformat(step1["launch_date"])
        if step1.get("estimated_completion_date"):
            project.estimated_completion_date = datetime.fromisoformat(step1["estimated_completion_date"])
        
        db.add(project)
        db.flush()  # Get project_id
        
        # Create buildings
        buildings = []
        for bldg_data in step2.get("buildings", []):
            building = Building(
                project_id=project.project_id,
                building_name=bldg_data["building_name"],
                building_code=bldg_data.get("building_code"),
                address=bldg_data.get("address"),
                floor_count=bldg_data.get("floor_count"),
                structure_type=bldg_data.get("structure_type"),
            )
            db.add(building)
            buildings.append(building)
        
        db.flush()  # Get building_ids
        
        # Create units
        units = []
        for unit_data in step3.get("units", []):
            building = buildings[unit_data["building_index"]]
            unit = Unit(
                building_id=building.building_id,
                floor_number=unit_data.get("floor_number"),
                unit_number=unit_data["unit_number"],
                area_sqm=unit_data.get("area_sqm"),
                room_count=unit_data.get("room_count"),
                unit_full_identifier=f"{unit_data.get('floor_number', 0)}-{unit_data['unit_number']}",
            )
            db.add(unit)
            units.append(unit)
        
        db.flush()  # Get unit_ids
        
        # Create owners
        for owner_data in step4.get("owners", []):
            unit = units[owner_data["unit_index"]]
            owner = Owner(
                unit_id=unit.unit_id,
                full_name=owner_data["full_name"],
                phone_for_contact=owner_data.get("phone"),
                email=owner_data.get("email"),
                ownership_share_percent=owner_data["ownership_share_percent"],
                preferred_contact_method=owner_data.get("preferred_contact_method"),
                preferred_language=owner_data.get("preferred_language"),
            )
            db.add(owner)
            
            # Update unit owner count
            unit.total_owners = (unit.total_owners or 0) + 1
            unit.is_co_owned = unit.total_owners > 1
        
        # Mark draft as completed
        draft.is_completed = True
        
        db.commit()
        
        logger.info(
            "Wizard completed - project created",
            extra={
                "project_id": str(project.project_id),
                "buildings_count": len(buildings),
                "units_count": len(units),
                "owners_count": len(step4.get("owners", [])),
                "user_id": str(current_user.user_id),
            }
        )
        
        return {
            "message": "Project created successfully",
            "project_id": str(project.project_id),
            "buildings_created": len(buildings),
            "units_created": len(units),
            "owners_created": len(step4.get("owners", [])),
        }
        
    except Exception as e:
        db.rollback()
        logger.error(
            "Wizard completion failed",
            extra={
                "draft_id": str(draft.draft_id),
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )

