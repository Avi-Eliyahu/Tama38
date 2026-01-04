"""
Recalculate all building and project progress based on signed units
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.building import Building
from app.models.project import Project
from app.services.majority import calculate_building_majority, calculate_project_majority


def recalculate_all(db: Session):
    """Recalculate all buildings and projects"""
    
    # Get all projects
    projects = db.query(Project).filter(Project.is_deleted == False).all()
    
    print("=" * 70)
    print("RECALCULATING BUILDING AND PROJECT PROGRESS")
    print("=" * 70)
    
    for project in projects:
        print(f"\nProject: {project.project_name}")
        
        # Get buildings in project
        buildings = db.query(Building).filter(
            Building.project_id == project.project_id,
            Building.is_deleted == False
        ).all()
        
        print(f"  Buildings: {len(buildings)}")
        
        # Recalculate each building
        for building in buildings:
            try:
                result = calculate_building_majority(str(building.building_id), db)
                print(f"    ✓ {building.building_name}: {result['signature_percentage']:.1f}% "
                      f"({result['units_signed']}/{result['total_units']} units signed)")
            except Exception as e:
                print(f"    ✗ {building.building_name}: Error - {e}")
        
        # Recalculate project
        try:
            result = calculate_project_majority(str(project.project_id), db)
            print(f"\n  Project Total: {result['signature_percentage']:.1f}% "
                  f"({result['units_signed']}/{result['total_units']} units signed)")
        except Exception as e:
            print(f"\n  Project Total: Error - {e}")
    
    print("\n" + "=" * 70)
    print("✓ Recalculation complete")
    print("=" * 70)


def main():
    db = SessionLocal()
    try:
        recalculate_all(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()

