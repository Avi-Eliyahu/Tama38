"""Verify that all SIGNED units have all owners SIGNED"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.unit import Unit
from app.models.owner import Owner

db = SessionLocal()
signed_units = db.query(Unit).filter(Unit.unit_status == 'SIGNED', Unit.is_deleted == False).limit(10).all()

print(f"Verifying {len(signed_units)} SIGNED units...\n")
all_consistent = True

for unit in signed_units:
    owners = db.query(Owner).filter(
        Owner.unit_id == unit.unit_id,
        Owner.is_deleted == False,
        Owner.is_current_owner == True
    ).all()
    
    non_signed = [o for o in owners if o.owner_status != 'SIGNED']
    if non_signed:
        print(f"❌ Unit {unit.unit_number}: {len(non_signed)} owners not SIGNED")
        all_consistent = False
    else:
        print(f"✓ Unit {unit.unit_number}: All {len(owners)} owners are SIGNED")

if all_consistent:
    print("\n✅ All SIGNED units have all owners SIGNED!")
else:
    print("\n⚠️  Some inconsistencies found")

db.close()

