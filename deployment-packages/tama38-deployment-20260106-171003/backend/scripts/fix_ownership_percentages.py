"""
Fix Ownership Percentages: Ensure all units have 100% total ownership
- Units with 1 owner: owner gets 100%
- Units with multiple owners: normalize shares to total 100%
"""
import sys
import os
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.unit import Unit
from app.models.owner import Owner


def fix_ownership_percentages(db: Session, dry_run: bool = False):
    """
    Fix ownership percentages to ensure all units total 100%.
    
    Args:
        db: Database session
        dry_run: If True, only show what would be changed without making changes
    """
    print("=" * 70)
    print("FIXING OWNERSHIP PERCENTAGES - ENSURING 100% TOTAL PER UNIT")
    print("=" * 70)
    
    if dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made\n")
    
    # Find all units
    units = db.query(Unit).filter(Unit.is_deleted == False).all()
    
    print(f"Found {len(units)} units\n")
    
    units_fixed = 0
    owners_updated = 0
    
    for unit in units:
        # Get all current owners for this unit
        owners = db.query(Owner).filter(
            Owner.unit_id == unit.unit_id,
            Owner.is_deleted == False,
            Owner.is_current_owner == True
        ).all()
        
        if not owners:
            continue
        
        # Calculate current total ownership
        current_total = sum(float(o.ownership_share_percent) for o in owners)
        
        # Check if fix is needed - be strict about exactly 100%
        needs_fix = False
        
        if len(owners) == 1:
            # Single owner should have exactly 100%
            if abs(float(owners[0].ownership_share_percent) - 100.0) > 0.001:
                needs_fix = True
        else:
            # Multiple owners should total exactly 100%
            if abs(current_total - 100.0) > 0.001:  # Very small tolerance for floating point
                needs_fix = True
        
        if needs_fix:
            print(f"Unit {unit.unit_number} (Building: {unit.building_id}):")
            print(f"  Current total: {current_total:.2f}%")
            print(f"  Owners: {len(owners)}")
            
            if len(owners) == 1:
                # Single owner: set to 100%
                old_share = float(owners[0].ownership_share_percent)
                print(f"    - {owners[0].full_name}: {old_share:.2f}% → 100.00%")
                
                if not dry_run:
                    owners[0].ownership_share_percent = Decimal('100.00')
                    owners[0].ownership_type = 'SOLE_OWNER'
                    owners_updated += 1
            else:
                # Multiple owners: normalize to 100%
                if current_total == 0:
                    # If total is 0, distribute equally
                    equal_share = Decimal('100.00') / len(owners)
                    for owner in owners:
                        old_share = float(owner.ownership_share_percent)
                        new_share = round(equal_share, 2)
                        print(f"    - {owner.full_name}: {old_share:.2f}% → {new_share:.2f}% (equal distribution)")
                        
                        if not dry_run:
                            owner.ownership_share_percent = new_share
                            owner.ownership_type = 'CO_OWNER_JOINT'
                            owners_updated += 1
                else:
                    # Normalize based on current proportions to ensure exactly 100%
                    # Calculate new shares proportionally
                    new_shares = []
                    for i, owner in enumerate(owners):
                        old_share = float(owner.ownership_share_percent)
                        if current_total > 0:
                            # Calculate proportional share
                            proportion = old_share / current_total
                            new_share = proportion * 100
                        else:
                            # Equal distribution if total is 0
                            new_share = 100.0 / len(owners)
                        
                        new_shares.append(new_share)
                    
                    # Adjust to ensure exact 100% total
                    total_new = sum(new_shares)
                    if abs(total_new - 100.0) > 0.001:
                        # Adjust the last owner to make total exactly 100%
                        adjustment = 100.0 - total_new
                        new_shares[-1] += adjustment
                    
                    # Round to 2 decimal places and ensure last owner gets remainder
                    rounded_shares = [round(s, 2) for s in new_shares[:-1]]
                    last_share = round(100.0 - sum(rounded_shares), 2)
                    rounded_shares.append(last_share)
                    
                    for i, owner in enumerate(owners):
                        old_share = float(owner.ownership_share_percent)
                        new_share = Decimal(str(rounded_shares[i]))
                        print(f"    - {owner.full_name}: {old_share:.2f}% → {new_share:.2f}%")
                        
                        if not dry_run:
                            owner.ownership_share_percent = new_share
                            if owner.ownership_type == 'SOLE_OWNER':
                                owner.ownership_type = 'CO_OWNER_JOINT'
                            owners_updated += 1
            
            units_fixed += 1
            print()
    
    if not dry_run:
        db.commit()
        print("=" * 70)
        print("FIX COMPLETE")
        print("=" * 70)
        print(f"Fixed {owners_updated} owners in {units_fixed} units")
        
        # Verify the fix
        print("\nVerifying fixes...")
        verification_passed = True
        for unit in units:
            owners = db.query(Owner).filter(
                Owner.unit_id == unit.unit_id,
                Owner.is_deleted == False,
                Owner.is_current_owner == True
            ).all()
            
            if owners:
                total = sum(float(o.ownership_share_percent) for o in owners)
                if abs(total - 100.0) > 0.01:
                    print(f"  ⚠️  Unit {unit.unit_number}: Total is {total:.2f}% (should be 100%)")
                    verification_passed = False
        
        if verification_passed:
            print("  ✅ All units now have 100% total ownership")
        else:
            print("  ⚠️  Some units still need attention")
    else:
        print("=" * 70)
        print("DRY RUN COMPLETE")
        print("=" * 70)
        print(f"Would update {owners_updated} owners in {units_fixed} units")
        print("\nRun without --dry-run to apply changes")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix ownership percentages to total 100% per unit')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        fix_ownership_percentages(db, dry_run=args.dry_run)
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

