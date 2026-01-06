"""
Script to recalculate unit statuses based on owner signatures
Useful for fixing units that have all owners signed but unit status is incorrect
"""
import sys
import os
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.unit import Unit
from app.models.owner import Owner
from app.models.building import Building
from app.models.project import Project
from app.services.unit_status import update_unit_status
from app.services.majority import calculate_building_majority, calculate_project_majority
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def recalculate_all_unit_statuses(db: Session):
    """Recalculate status for all units"""
    print("======================================================================")
    print("RECALCULATING UNIT STATUSES")
    print("======================================================================")

    units = db.query(Unit).filter(Unit.is_deleted == False).all()
    print(f"Found {len(units)} units to process\n")

    updated_count = 0
    for unit in units:
        try:
            old_status = unit.unit_status
            update_unit_status(str(unit.unit_id), db)
            db.refresh(unit)
            
            if old_status != unit.unit_status:
                print(f"✓ Unit {unit.unit_number}: {old_status} → {unit.unit_status}")
                updated_count += 1
        except Exception as e:
            print(f"✗ Error updating unit {unit.unit_number}: {e}")
            db.rollback()

    print(f"\n======================================================================")
    print(f"✓ Updated {updated_count} units")
    print("======================================================================")

    # Recalculate building and project majorities
    print("\nRecalculating building and project majorities...")
    
    buildings = db.query(Building).filter(Building.is_deleted == False).all()
    for building in buildings:
        try:
            calculate_building_majority(str(building.building_id), db)
        except Exception as e:
            print(f"✗ Error calculating building {building.building_name}: {e}")
            db.rollback()

    projects = db.query(Project).filter(Project.is_deleted == False).all()
    for project in projects:
        try:
            calculate_project_majority(str(project.project_id), db)
        except Exception as e:
            print(f"✗ Error calculating project {project.project_name}: {e}")
            db.rollback()

    print("✓ Recalculation complete")


def main():
    db: Session = SessionLocal()
    try:
        recalculate_all_unit_statuses(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()

