"""
Cleanup script to find and remove orphaned entities (buildings without projects, etc.)
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.project import Project
from app.models.building import Building
from app.models.unit import Unit
from app.models.owner import Owner
from datetime import datetime


def find_orphaned_buildings(db: Session):
    """Find buildings that reference non-existent or deleted projects"""
    # Find buildings where project doesn't exist or is deleted
    all_buildings = db.query(Building).filter(Building.is_deleted == False).all()
    orphaned = []
    
    for building in all_buildings:
        project = db.query(Project).filter(
            Project.project_id == building.project_id
        ).first()
        
        if not project or project.is_deleted:
            orphaned.append(building)
    
    return orphaned


def find_orphaned_units(db: Session):
    """Find units that reference non-existent or deleted buildings"""
    all_units = db.query(Unit).filter(Unit.is_deleted == False).all()
    orphaned = []
    
    for unit in all_units:
        building = db.query(Building).filter(
            Building.building_id == unit.building_id
        ).first()
        
        if not building or building.is_deleted:
            orphaned.append(unit)
    
    return orphaned


def find_orphaned_owners(db: Session):
    """Find owners that reference non-existent or deleted units"""
    all_owners = db.query(Owner).filter(Owner.is_deleted == False).all()
    orphaned = []
    
    for owner in all_owners:
        unit = db.query(Unit).filter(
            Unit.unit_id == owner.unit_id
        ).first()
        
        if not unit or unit.is_deleted:
            orphaned.append(owner)
    
    return orphaned


def soft_delete_orphaned_entities(db: Session, dry_run: bool = True):
    """Soft delete orphaned entities"""
    orphaned_buildings = find_orphaned_buildings(db)
    orphaned_units = find_orphaned_units(db)
    orphaned_owners = find_orphaned_owners(db)
    
    print("=" * 60)
    print("ORPHANED ENTITIES REPORT")
    print("=" * 60)
    
    print(f"\nOrphaned Buildings: {len(orphaned_buildings)}")
    for building in orphaned_buildings:
        project = db.query(Project).filter(Project.project_id == building.project_id).first()
        project_status = "DELETED" if project and project.is_deleted else "NOT FOUND"
        print(f"  - {building.building_name} (ID: {building.building_id})")
        print(f"    Project ID: {building.project_id} ({project_status})")
    
    print(f"\nOrphaned Units: {len(orphaned_units)}")
    for unit in orphaned_units[:10]:  # Show first 10
        building = db.query(Building).filter(Building.building_id == unit.building_id).first()
        building_status = "DELETED" if building and building.is_deleted else "NOT FOUND"
        print(f"  - Unit {unit.unit_number} (ID: {unit.unit_id})")
        print(f"    Building ID: {unit.building_id} ({building_status})")
    if len(orphaned_units) > 10:
        print(f"  ... and {len(orphaned_units) - 10} more")
    
    print(f"\nOrphaned Owners: {len(orphaned_owners)}")
    for owner in orphaned_owners[:10]:  # Show first 10
        unit = db.query(Unit).filter(Unit.unit_id == owner.unit_id).first()
        unit_status = "DELETED" if unit and unit.is_deleted else "NOT FOUND"
        print(f"  - {owner.full_name} (ID: {owner.owner_id})")
        print(f"    Unit ID: {owner.unit_id} ({unit_status})")
    if len(orphaned_owners) > 10:
        print(f"  ... and {len(orphaned_owners) - 10} more")
    
    if dry_run:
        print("\n" + "=" * 60)
        print("DRY RUN MODE - No changes made")
        print("Run with --execute to actually delete these entities")
        print("=" * 60)
        return
    
    # Actually delete
    print("\n" + "=" * 60)
    print("DELETING ORPHANED ENTITIES...")
    print("=" * 60)
    
    deleted_count = 0
    
    # Delete orphaned owners first (they reference units)
    for owner in orphaned_owners:
        owner.is_deleted = True
        owner.updated_at = datetime.utcnow()
        deleted_count += 1
    
    # Delete orphaned units (they reference buildings)
    for unit in orphaned_units:
        unit.is_deleted = True
        unit.updated_at = datetime.utcnow()
        deleted_count += 1
    
    # Delete orphaned buildings last
    for building in orphaned_buildings:
        building.is_deleted = True
        building.updated_at = datetime.utcnow()
        deleted_count += 1
    
    db.commit()
    
    print(f"\n✓ Soft-deleted {deleted_count} orphaned entities")
    print(f"  - {len(orphaned_owners)} owners")
    print(f"  - {len(orphaned_units)} units")
    print(f"  - {len(orphaned_buildings)} buildings")
    print("=" * 60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Cleanup orphaned entities')
    parser.add_argument('--execute', action='store_true', help='Actually delete entities (default is dry-run)')
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        soft_delete_orphaned_entities(db, dry_run=not args.execute)
    finally:
        db.close()


if __name__ == "__main__":
    main()

