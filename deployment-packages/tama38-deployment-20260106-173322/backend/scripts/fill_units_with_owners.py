"""
Fill all units with owners (1-3 randomly) and ensure owner signature statuses
reflect unit statuses correctly.
"""
import sys
import os
import random
from datetime import datetime, date

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.unit import Unit
from app.models.owner import Owner
from app.models.building import Building
from app.models.project import Project
from app.services.unit_status import update_unit_status
import uuid


# Sample Hebrew and English names for owners
HEBREW_FIRST_NAMES = [
    "אברהם", "יצחק", "יעקב", "משה", "דוד", "שלמה", "יוסף", "בנימין",
    "שרה", "רבקה", "רחל", "לאה", "מרים", "אסתר", "רות", "דבורה",
    "יונתן", "דניאל", "אליהו", "שמואל", "אהרון", "יהודה", "ראובן", "שמעון",
    "חוה", "נעמי", "תמר", "מיכל", "עדינה", "חנה", "אלישבע", "ציפורה"
]

HEBREW_LAST_NAMES = [
    "כהן", "לוי", "ישראל", "דוד", "משה", "אברהם", "יוסף", "יעקב",
    "שלום", "בן-דוד", "בן-חיים", "בן-שמואל", "בן-אברהם", "בן-יעקב",
    "רוזן", "גולד", "כספי", "דיין", "שטרן", "ברגר", "כץ", "לוי"
]

ENGLISH_FIRST_NAMES = [
    "John", "David", "Michael", "Daniel", "Robert", "James", "William", "Richard",
    "Sarah", "Rachel", "Miriam", "Esther", "Ruth", "Deborah", "Hannah", "Leah",
    "Joseph", "Benjamin", "Samuel", "Aaron", "Jacob", "Isaac", "Abraham", "Solomon",
    "Mary", "Elizabeth", "Rebecca", "Naomi", "Tamar", "Michal", "Adina", "Tzipora"
]

ENGLISH_LAST_NAMES = [
    "Cohen", "Levi", "Israel", "David", "Moses", "Abraham", "Joseph", "Jacob",
    "Shalom", "Ben-David", "Ben-Haim", "Ben-Shmuel", "Ben-Avraham", "Ben-Yaakov",
    "Rosen", "Gold", "Kesef", "Dayan", "Stern", "Berger", "Katz", "Levy"
]


def generate_owner_name(use_hebrew: bool = True):
    """Generate a random owner name"""
    if use_hebrew and random.random() > 0.3:  # 70% Hebrew names
        first_name = random.choice(HEBREW_FIRST_NAMES)
        last_name = random.choice(HEBREW_LAST_NAMES)
    else:
        first_name = random.choice(ENGLISH_FIRST_NAMES)
        last_name = random.choice(ENGLISH_LAST_NAMES)
    
    return first_name, last_name


def generate_phone() -> str:
    """Generate a random Israeli phone number"""
    # Israeli mobile format: 05X-XXXXXXX
    prefix = random.choice(["050", "051", "052", "053", "054", "055", "056", "057", "058"])
    number = f"{random.randint(1000000, 9999999)}"
    return f"{prefix}-{number}"


def generate_email(first_name: str, last_name: str) -> str:
    """Generate email from name"""
    base = f"{first_name.lower()}.{last_name.lower()}".replace(" ", "").replace("-", "")
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "walla.co.il", "012.net.il"]
    return f"{base}{random.randint(1, 999)}@{random.choice(domains)}"


def get_owner_status_for_unit_status(unit_status: str, owner_index: int, total_owners: int) -> str:
    """
    Determine owner status based on desired unit status.
    
    Logic:
    - If unit should be SIGNED: all owners get 'SIGNED'
    - If unit should be PARTIALLY_SIGNED: first owner gets 'SIGNED', others get 'NOT_CONTACTED'
    - If unit should be NOT_SIGNED: all owners get 'NOT_CONTACTED'
    - Other statuses: distribute randomly
    """
    if unit_status == 'SIGNED':
        return 'SIGNED'
    elif unit_status == 'PARTIALLY_SIGNED':
        # First owner signed, others not
        return 'SIGNED' if owner_index == 0 else 'NOT_CONTACTED'
    elif unit_status == 'NOT_SIGNED' or unit_status == 'NOT_CONTACTED':
        return 'NOT_CONTACTED'
    elif unit_status == 'NEGOTIATING':
        # Random distribution: some negotiating, some not contacted
        return 'NEGOTIATING' if random.random() > 0.5 else 'NOT_CONTACTED'
    elif unit_status == 'AGREED_TO_SIGN':
        # Some agreed, some negotiating
        if owner_index == 0:
            return 'AGREED_TO_SIGN'
        elif owner_index == 1 and total_owners > 1:
            return 'NEGOTIATING' if random.random() > 0.5 else 'AGREED_TO_SIGN'
        else:
            return 'NOT_CONTACTED'
    elif unit_status == 'REFUSED':
        # All refused or some refused
        return 'REFUSED' if random.random() > 0.3 else 'NOT_CONTACTED'
    else:
        return 'NOT_CONTACTED'


def fill_units_with_owners(db: Session, dry_run: bool = True):
    """Fill all units with owners (1-3 randomly)"""
    
    # Get all units without owners or with 0 owners
    all_units = db.query(Unit).filter(Unit.is_deleted == False).all()
    
    units_to_fill = []
    units_with_owners = []
    
    for unit in all_units:
        owners = db.query(Owner).filter(
            Owner.unit_id == unit.unit_id,
            Owner.is_deleted == False,
            Owner.is_current_owner == True
        ).all()
        
        if len(owners) == 0:
            units_to_fill.append(unit)
        else:
            units_with_owners.append((unit, owners))
    
    print("=" * 70)
    print("FILL UNITS WITH OWNERS")
    print("=" * 70)
    print(f"\nUnits without owners: {len(units_to_fill)}")
    print(f"Units with owners: {len(units_with_owners)}")
    
    if dry_run:
        print("\n" + "=" * 70)
        print("DRY RUN MODE - No changes made")
        print("Run with --execute to actually create owners")
        print("=" * 70)
        return
    
    # Create owners for units without owners
    created_count = 0
    for unit in units_to_fill:
        # Random number of owners: 1-3
        num_owners = random.randint(1, 3)
        
        # Determine target unit status (random distribution)
        status_distribution = random.random()
        if status_distribution < 0.3:  # 30% SIGNED
            target_status = 'SIGNED'
        elif status_distribution < 0.6:  # 30% PARTIALLY_SIGNED
            target_status = 'PARTIALLY_SIGNED'
        else:  # 40% NOT_CONTACTED or other
            target_status = random.choice(['NOT_CONTACTED', 'NEGOTIATING', 'AGREED_TO_SIGN'])
        
        # Create owners
        total_share = 100.0
        for i in range(num_owners):
            first_name, last_name = generate_owner_name()
            full_name = f"{first_name} {last_name}"
            
            # Calculate ownership share
            if i == num_owners - 1:
                # Last owner gets remainder
                ownership_share = total_share
            else:
                # Distribute shares (at least 20% per owner)
                min_share = 20.0
                max_share = min(50.0, total_share - min_share * (num_owners - i - 1))
                ownership_share = round(random.uniform(min_share, max_share), 2)
                total_share -= ownership_share
            
            # Determine owner status based on target unit status
            owner_status = get_owner_status_for_unit_status(target_status, i, num_owners)
            
            owner = Owner(
                unit_id=unit.unit_id,
                full_name=full_name,
                phone_for_contact=generate_phone(),
                email=generate_email(first_name, last_name),
                ownership_share_percent=ownership_share,
                ownership_type='SOLE_OWNER' if num_owners == 1 else 'CO_OWNER_JOINT',
                is_primary_contact=(i == 0),
                owner_status=owner_status,
                preferred_contact_method=random.choice(['PHONE', 'WHATSAPP', 'EMAIL']),
                preferred_language=random.choice(['HEBREW', 'ENGLISH', 'RUSSIAN']),
                is_current_owner=True,
            )
            
            db.add(owner)
            created_count += 1
        
        # Update unit status after creating owners
        update_unit_status(str(unit.unit_id), db)
        
        print(f"✓ Created {num_owners} owners for unit {unit.unit_number} (target status: {target_status})")
    
    # Update existing units to ensure status consistency
    updated_count = 0
    for unit, owners in units_with_owners:
        # Check current unit status
        current_status = unit.unit_status
        
        # Count signed owners
        signed_count = sum(1 for owner in owners if owner.owner_status == 'SIGNED')
        total_count = len(owners)
        
        # Determine what status should be
        if signed_count == total_count and total_count > 0:
            expected_status = 'SIGNED'
        elif signed_count > 0:
            expected_status = 'PARTIALLY_SIGNED'
        else:
            expected_status = 'NOT_CONTACTED'
        
        # If status doesn't match, update owners to match unit status
        if current_status in ['SIGNED', 'PARTIALLY_SIGNED', 'NOT_CONTACTED'] and current_status != expected_status:
            # Update owners to match unit status
            for i, owner in enumerate(owners):
                new_status = get_owner_status_for_unit_status(current_status, i, total_count)
                if owner.owner_status != new_status:
                    owner.owner_status = new_status
                    updated_count += 1
                    print(f"  Updated owner {owner.full_name} status: {owner.owner_status} -> {new_status}")
            
            # Recalculate unit status
            update_unit_status(str(unit.unit_id), db)
    
    db.commit()
    
    print("\n" + "=" * 70)
    print(f"✓ Created {created_count} owners")
    print(f"✓ Updated {updated_count} owner statuses for consistency")
    print("=" * 70)
    
    # Verify: check units without owners
    remaining_units = db.query(Unit).filter(Unit.is_deleted == False).all()
    units_still_empty = []
    for unit in remaining_units:
        owners = db.query(Owner).filter(
            Owner.unit_id == unit.unit_id,
            Owner.is_deleted == False,
            Owner.is_current_owner == True
        ).all()
        if len(owners) == 0:
            units_still_empty.append(unit)
    
    if units_still_empty:
        print(f"\n⚠ Warning: {len(units_still_empty)} units still have no owners")
    else:
        print("\n✓ All units now have at least one owner")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fill units with owners')
    parser.add_argument('--execute', action='store_true', help='Actually create owners (default is dry-run)')
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        fill_units_with_owners(db, dry_run=not args.execute)
    finally:
        db.close()


if __name__ == "__main__":
    main()

