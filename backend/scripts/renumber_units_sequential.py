"""
Renumber Units Sequentially: Change unit numbers to be sequential from 1 to N per building
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import SessionLocal
from app.models.unit import Unit
from app.models.building import Building


def renumber_units_sequential(db: Session, dry_run: bool = False):
    """
    Renumber all units sequentially from 1 to N per building.
    
    Args:
        db: Database session
        dry_run: If True, only show what would be changed without making changes
    """
    print("=" * 70)
    print("RENUMBERING UNITS SEQUENTIALLY (1 to N per building)")
    print("=" * 70)
    
    if dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made\n")
    
    # Get all buildings
    buildings = db.query(Building).filter(Building.is_deleted == False).all()
    
    print(f"Found {len(buildings)} buildings\n")
    
    total_units_renumbered = 0
    
    for building in buildings:
        # Get all units for this building, ordered by floor_number and created_at
        # This ensures consistent ordering that doesn't depend on unit_number
        units = db.query(Unit).filter(
            Unit.building_id == building.building_id,
            Unit.is_deleted == False
        ).order_by(
            Unit.floor_number.asc().nullsfirst(),
            Unit.created_at.asc().nullsfirst(),
            Unit.unit_id.asc()  # Fallback to unit_id for stable ordering
        ).all()
        
        if not units:
            continue
        
        print(f"Building: {building.building_name} ({building.building_code or 'N/A'})")
        print(f"  Total units: {len(units)}")
        
        # Check if renumbering is needed
        needs_renumbering = False
        for i, unit in enumerate(units, start=1):
            expected_number = str(i)
            if unit.unit_number != expected_number:
                needs_renumbering = True
                break
        
        if not needs_renumbering:
            print(f"  ✓ Units already sequential (1-{len(units)})\n")
            continue
        
        print(f"  Renumbering units:")
        for i, unit in enumerate(units, start=1):
            old_number = unit.unit_number
            new_number = str(i)
            old_full_id = unit.unit_full_identifier
            # Keep floor_number in full identifier, but unit_number is sequential
            new_full_id = f"{unit.floor_number or 0}-{new_number}" if unit.floor_number else new_number
            
            print(f"    Unit {old_number} (floor {unit.floor_number or 'N/A'}) → {new_number}")
            if old_full_id != new_full_id:
                print(f"      Full ID: {old_full_id} → {new_full_id}")
            
            if not dry_run:
                unit.unit_number = new_number
                unit.unit_full_identifier = new_full_id
                total_units_renumbered += 1
        
        print()
    
    if not dry_run:
        db.commit()
        print("=" * 70)
        print("RENUMBERING COMPLETE")
        print("=" * 70)
        print(f"Renumbered {total_units_renumbered} units")
        
        # Verify the changes - check if units are sequential when sorted by unit_number
        print("\nVerifying changes...")
        verification_passed = True
        for building in buildings:
            units = db.query(Unit).filter(
                Unit.building_id == building.building_id,
                Unit.is_deleted == False
            ).all()
            
            # Sort units by unit_number numerically
            sorted_units = sorted(units, key=lambda u: int(u.unit_number) if u.unit_number.isdigit() else 999)
            
            for i, unit in enumerate(sorted_units, start=1):
                expected_number = str(i)
                if unit.unit_number != expected_number:
                    print(f"  ⚠️  Building {building.building_name}: Unit {unit.unit_number} should be {expected_number}")
                    verification_passed = False
                    break  # Only report first issue per building
        
        if verification_passed:
            print("  ✅ All units are now sequential")
        else:
            print("  ⚠️  Some units still need attention")
    else:
        print("=" * 70)
        print("DRY RUN COMPLETE")
        print("=" * 70)
        print(f"Would renumber {total_units_renumbered} units")
        print("\nRun without --dry-run to apply changes")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Renumber units sequentially from 1 to N per building')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        renumber_units_sequential(db, dry_run=args.dry_run)
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

