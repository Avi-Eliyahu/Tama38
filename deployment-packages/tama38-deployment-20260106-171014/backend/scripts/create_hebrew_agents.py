"""
Create 4 Agents with Hebrew Names
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


def generate_email_from_hebrew_name(hebrew_name: str, index: int) -> str:
    """
    Generate a simple email from Hebrew name using transliteration pattern
    """
    # Simple transliteration patterns for common Hebrew names
    transliteration_map = {
        'דוד': 'david',
        'יוסף': 'yosef',
        'שלמה': 'shlomo',
        'אברהם': 'avraham',
        'יצחק': 'itzhak',
        'יעקב': 'yaakov',
        'משה': 'moshe',
        'אהרון': 'aharon',
        'דניאל': 'daniel',
        'יונתן': 'yonatan',
        'שמואל': 'shmuel',
        'ראובן': 'reuven',
        'בנימין': 'benjamin',
        'יהודה': 'yehuda',
        'אליהו': 'eliyahu',
        'שמעון': 'shimon',
        'חנה': 'hana',
        'מרים': 'miriam',
        'שרה': 'sara',
        'רחל': 'rachel',
        'לאה': 'lea',
        'רבקה': 'rivka',
        'אסתר': 'ester',
        'דבורה': 'devora',
        'תמר': 'tamar',
        'רות': 'rut',
        'מיכל': 'michal',
        'נעמי': 'naomi',
        'ציפורה': 'tzipora',
        'עדינה': 'adina',
        'אלישבע': 'elishava',
        'כהן': 'cohen',
        'לוי': 'levi',
    }
    
    # Try to find transliteration, otherwise use generic
    parts = hebrew_name.split()
    if len(parts) >= 2:
        first_name = parts[0]
        last_name = parts[-1]
        first_translit = transliteration_map.get(first_name, f'agent{index}')
        last_translit = transliteration_map.get(last_name, f'agent{index}')
        return f"{first_translit}.{last_translit}@tama38.local"
    else:
        name_translit = transliteration_map.get(hebrew_name, f'agent{index}')
        return f"{name_translit}@tama38.local"


def create_hebrew_agents(db: Session, dry_run: bool = False):
    """
    Create 4 agents with Hebrew names.
    
    Args:
        db: Database session
        dry_run: If True, only show what would be created without making changes
    """
    print("=" * 70)
    print("CREATING 4 AGENTS WITH HEBREW NAMES")
    print("=" * 70)
    
    if dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made\n")
    
    # Hebrew agent names
    agents_data = [
        {"name": "דוד כהן", "phone": "050-1111111"},
        {"name": "שרה לוי", "phone": "052-2222222"},
        {"name": "יוסף אברהם", "phone": "054-3333333"},
        {"name": "רחל דוד", "phone": "050-4444444"},
    ]
    
    default_password = "Agent123!@#"
    created_count = 0
    skipped_count = 0
    
    for i, agent_data in enumerate(agents_data, start=1):
        email = generate_email_from_hebrew_name(agent_data["name"], i)
        
        # Check if user already exists
        existing_user = db.query(User).filter(
            User.email == email,
            User.is_deleted == False
        ).first()
        
        if existing_user:
            print(f"⚠️  Agent {i}: {agent_data['name']} ({email}) already exists - skipping")
            skipped_count += 1
            continue
        
        print(f"Agent {i}:")
        print(f"  Name: {agent_data['name']}")
        print(f"  Email: {email}")
        print(f"  Phone: {agent_data['phone']}")
        print(f"  Role: AGENT")
        print(f"  Password: {default_password}")
        
        if not dry_run:
            user = User(
                email=email,
                hashed_password=get_password_hash(default_password),
                full_name=agent_data["name"],
                role="AGENT",
                phone=agent_data["phone"],
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            created_count += 1
        print()
    
    if not dry_run:
        db.commit()
        print("=" * 70)
        print("CREATION COMPLETE")
        print("=" * 70)
        print(f"Created {created_count} agents")
        if skipped_count > 0:
            print(f"Skipped {skipped_count} existing agents")
        
        # Verify the created agents
        print("\nVerifying created agents...")
        agents = db.query(User).filter(
            User.role == "AGENT",
            User.is_deleted == False
        ).all()
        print(f"  Total agents in database: {len(agents)}")
        for agent in agents[-4:]:  # Show last 4 (should be the ones we just created)
            print(f"    - {agent.full_name} ({agent.email})")
    else:
        print("=" * 70)
        print("DRY RUN COMPLETE")
        print("=" * 70)
        print(f"Would create {len(agents_data) - skipped_count} agents")
        print(f"Would skip {skipped_count} existing agents")
        print("\nRun without --dry-run to create agents")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Create 4 agents with Hebrew names')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be created without making changes')
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        create_hebrew_agents(db, dry_run=args.dry_run)
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

