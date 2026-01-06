"""
Verify that all units have owners and statuses are correct
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.unit import Unit
from app.models.owner import Owner

def verify():
    db = SessionLocal()
    try:
        units = db.query(Unit).filter(Unit.is_deleted == False).all()
        
        stats = {
            'total': len(units),
            'with_owners': 0,
            'without_owners': 0,
            'signed': 0,
            'partially_signed': 0,
            'not_contacted': 0,
            'negotiating': 0,
            'other': 0,
        }
        
        units_without_owners = []
        
        for unit in units:
            owners = db.query(Owner).filter(
                Owner.unit_id == unit.unit_id,
                Owner.is_deleted == False,
                Owner.is_current_owner == True
            ).all()
            
            if len(owners) > 0:
                stats['with_owners'] += 1
            else:
                stats['without_owners'] += 1
                units_without_owners.append(unit)
            
            # Count by status
            if unit.unit_status == 'SIGNED':
                stats['signed'] += 1
            elif unit.unit_status == 'PARTIALLY_SIGNED':
                stats['partially_signed'] += 1
            elif unit.unit_status == 'NOT_CONTACTED':
                stats['not_contacted'] += 1
            elif unit.unit_status == 'NEGOTIATING':
                stats['negotiating'] += 1
            else:
                stats['other'] += 1
        
        print("=" * 70)
        print("UNIT OWNERS VERIFICATION")
        print("=" * 70)
        print(f"\nTotal units: {stats['total']}")
        print(f"Units with owners: {stats['with_owners']}")
        print(f"Units without owners: {stats['without_owners']}")
        
        if units_without_owners:
            print(f"\n⚠ Units without owners:")
            for unit in units_without_owners[:10]:
                print(f"  - Unit {unit.unit_number} (ID: {unit.unit_id})")
            if len(units_without_owners) > 10:
                print(f"  ... and {len(units_without_owners) - 10} more")
        
        print(f"\nUnit Status Distribution:")
        print(f"  SIGNED: {stats['signed']}")
        print(f"  PARTIALLY_SIGNED: {stats['partially_signed']}")
        print(f"  NOT_CONTACTED: {stats['not_contacted']}")
        print(f"  NEGOTIATING: {stats['negotiating']}")
        print(f"  Other: {stats['other']}")
        
        print("\n" + "=" * 70)
        if stats['without_owners'] == 0:
            print("✓ All units have at least one owner")
        else:
            print(f"⚠ {stats['without_owners']} units still need owners")
        print("=" * 70)
        
    finally:
        db.close()

if __name__ == "__main__":
    verify()

