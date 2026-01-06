"""Check ownership percentages for all units"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.unit import Unit
from app.models.owner import Owner

db = SessionLocal()
units = db.query(Unit).filter(Unit.is_deleted == False).all()

print(f"Checking {len(units)} units for ownership percentage issues...\n")

issues_found = []
units_with_1_owner_not_100 = []
units_not_total_100 = []

for unit in units:
    owners = db.query(Owner).filter(
        Owner.unit_id == unit.unit_id,
        Owner.is_deleted == False,
        Owner.is_current_owner == True
    ).all()
    
    if not owners:
        continue
    
    total = sum(float(o.ownership_share_percent) for o in owners)
    
    # Check single owner units
    if len(owners) == 1:
        if abs(float(owners[0].ownership_share_percent) - 100.0) > 0.01:
            units_with_1_owner_not_100.append({
                'unit': unit,
                'owner': owners[0],
                'current': float(owners[0].ownership_share_percent)
            })
    
    # Check if total is not 100%
    if abs(total - 100.0) > 0.01:
        units_not_total_100.append({
            'unit': unit,
            'owners': owners,
            'total': total
        })

print(f"Units with 1 owner not at 100%: {len(units_with_1_owner_not_100)}")
if units_with_1_owner_not_100:
    print("\nDetails:")
    for item in units_with_1_owner_not_100[:10]:  # Show first 10
        print(f"  Unit {item['unit'].unit_number}: {item['owner'].full_name} has {item['current']:.2f}%")

print(f"\nUnits not totaling 100%: {len(units_not_total_100)}")
if units_not_total_100:
    print("\nDetails:")
    for item in units_not_total_100[:10]:  # Show first 10
        print(f"  Unit {item['unit'].unit_number}: Total = {item['total']:.2f}%")
        for owner in item['owners']:
            print(f"    - {owner.full_name}: {float(owner.ownership_share_percent):.2f}%")

if not units_with_1_owner_not_100 and not units_not_total_100:
    print("\n✅ All units have correct ownership percentages!")
else:
    print(f"\n⚠️  Found {len(units_with_1_owner_not_100) + len(units_not_total_100)} units needing fixes")

db.close()

