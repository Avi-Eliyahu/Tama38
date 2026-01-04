"""
Fix Data Consistency: Ensure all owners of SIGNED units are also SIGNED
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.unit import Unit
from app.models.owner import Owner
from app.services.unit_status import update_unit_status
from app.services.majority import calculate_building_majority
from app.models.building import Building
from app.models.project import Project


def fix_signed_units_owners(db: Session, dry_run: bool = False):
    """
    Fix data consistency: For all units with status SIGNED,
    ensure all their owners also have status SIGNED.
    
    Args:
        db: Database session
        dry_run: If True, only show what would be changed without making changes
    """
    print("=" * 70)
    print("FIXING SIGNED UNITS - ENSURING OWNERS ARE ALSO SIGNED")
    print("=" * 70)
    
    if dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made\n")
    
    # Find all units with status SIGNED
    signed_units = db.query(Unit).filter(
        Unit.unit_status == 'SIGNED',
        Unit.is_deleted == False
    ).all()
    
    print(f"Found {len(signed_units)} units with status SIGNED\n")
    
    total_owners_fixed = 0
    units_fixed = 0
    
    for unit in signed_units:
        # Get all current owners for this unit
        owners = db.query(Owner).filter(
            Owner.unit_id == unit.unit_id,
            Owner.is_deleted == False,
            Owner.is_current_owner == True
        ).all()
        
        if not owners:
            print(f"⚠️  Unit {unit.unit_number} (ID: {unit.unit_id}) has status SIGNED but no owners!")
            continue
        
        # Find owners that are not SIGNED
        non_signed_owners = [o for o in owners if o.owner_status != 'SIGNED']
        
        if non_signed_owners:
            print(f"Unit {unit.unit_number} (Building: {unit.building_id}):")
            print(f"  Total owners: {len(owners)}")
            print(f"  Owners not SIGNED: {len(non_signed_owners)}")
            
            for owner in non_signed_owners:
                print(f"    - {owner.full_name}: {owner.owner_status} → SIGNED")
                
                if not dry_run:
                    owner.owner_status = 'SIGNED'
                    total_owners_fixed += 1
            
            units_fixed += 1
            print()
    
    if not dry_run:
        db.commit()
        print("=" * 70)
        print("FIX COMPLETE")
        print("=" * 70)
        print(f"Fixed {total_owners_fixed} owners in {units_fixed} units")
        
        # Recalculate unit statuses to ensure consistency
        print("\nRecalculating unit statuses...")
        for unit in signed_units:
            try:
                update_unit_status(str(unit.unit_id), db)
            except Exception as e:
                print(f"  ⚠️  Error recalculating unit {unit.unit_id}: {e}")
        
        # Recalculate building majorities
        print("\nRecalculating building majorities...")
        building_ids = {str(unit.building_id) for unit in signed_units}
        for building_id in building_ids:
            try:
                calculate_building_majority(building_id, db)
            except Exception as e:
                print(f"  ⚠️  Error recalculating building {building_id}: {e}")
        
        print("\n✓ All fixes applied and statuses recalculated")
    else:
        print("=" * 70)
        print("DRY RUN COMPLETE")
        print("=" * 70)
        print(f"Would fix {total_owners_fixed} owners in {units_fixed} units")
        print("\nRun without --dry-run to apply changes")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix signed units to ensure owners are also signed')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        fix_signed_units_owners(db, dry_run=args.dry_run)
    except Exception as e:
        db.rollback()
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

