"""
Create Hebrew Sample Database Script
Creates a sample Hebrew database with:
- 2 projects
- First project: 4 buildings
- Second project: 2 buildings
- 16-28 units per building
- 1-3 owners per unit
- All text fields translated to Hebrew (except emails and IDs)
"""
import sys
import os
import subprocess
from datetime import datetime, date, timedelta
from decimal import Decimal
from urllib.parse import urlparse
import random
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.config import settings
from app.models.project import Project
from app.models.building import Building
from app.models.unit import Unit
from app.models.owner import Owner
from app.models.user import User
from app.core.security import get_password_hash
from deep_translator import GoogleTranslator, MyMemoryTranslator

# Translation cache
_translation_cache = {}


def translate_to_hebrew(text: str, use_cache: bool = True) -> str:
    """Translate English text to Hebrew"""
    if not text or not isinstance(text, str):
        return text
    
    # Check cache
    if use_cache and text in _translation_cache:
        return _translation_cache[text]
    
    try:
        # Try Google Translate first (more accurate)
        translator = GoogleTranslator(source='en', target='he')
        translated = translator.translate(text)
        if use_cache:
            _translation_cache[text] = translated
        return translated
    except Exception as e:
        try:
            # Fallback to MyMemory
            translator = MyMemoryTranslator(source='en', target='he')
            translated = translator.translate(text)
            if use_cache:
                _translation_cache[text] = translated
            return translated
        except Exception as e2:
            print(f"  Warning: Could not translate '{text}': {e2}")
            # Return original text if translation fails
            return text


def parse_database_url(url: str):
    """Parse DATABASE_URL into components"""
    parsed = urlparse(url)
    return {
        'host': parsed.hostname or 'localhost',
        'port': parsed.port or 5432,
        'database': parsed.path.lstrip('/'),
        'user': parsed.username or 'postgres',
        'password': parsed.password or ''
   }


def create_database(db_name: str):
    """Create a new PostgreSQL database"""
    db_config = parse_database_url(settings.DATABASE_URL)
    
    # Connect to postgres database to create new database
    conn = psycopg2.connect(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
        database='postgres'  # Connect to default postgres database
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
    exists = cursor.fetchone()
    
    if exists:
        print(f"⚠ Database '{db_name}' already exists. Dropping it...")
        cursor.execute(f"DROP DATABASE {db_name}")
    
    cursor.execute(f"CREATE DATABASE {db_name}")
    cursor.close()
    conn.close()
    
    print(f"✓ Created database: {db_name}")


def run_migrations(target_db: str):
    """Run Alembic migrations on target database"""
    db_config = parse_database_url(settings.DATABASE_URL)
    
    # Temporarily update DATABASE_URL
    original_url = settings.DATABASE_URL
    new_url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{target_db}"
    
    # Update environment variable
    os.environ['DATABASE_URL'] = new_url
    
    try:
        # Run alembic upgrade head
        result = subprocess.run(
            ['alembic', 'upgrade', 'head'],
            cwd=os.path.join(os.path.dirname(__file__), '..'),
            capture_output=True,
            text=True,
            check=True
        )
        print("✓ Database migrations completed")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running migrations: {e.stderr}")
        raise
    finally:
        # Restore original DATABASE_URL
        os.environ['DATABASE_URL'] = original_url


# Hebrew names for owners
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


def generate_hebrew_name():
    """Generate a random Hebrew name"""
    first_name = random.choice(HEBREW_FIRST_NAMES)
    last_name = random.choice(HEBREW_LAST_NAMES)
    return f"{first_name} {last_name}"


def generate_phone() -> str:
    """Generate a random Israeli phone number"""
    prefix = random.choice(["050", "051", "052", "053", "054", "055", "056", "057", "058"])
    number = f"{random.randint(1000000, 9999999)}"
    return f"{prefix}-{number}"


def generate_email(first_name: str, last_name: str) -> str:
    """Generate email from name (keep in English/Latin)"""
    # Transliteration map for common Hebrew names
    translit_map = {
        'אברהם': 'avraham', 'יצחק': 'yitzhak', 'יעקב': 'yaakov', 'משה': 'moshe',
        'דוד': 'david', 'שלמה': 'shlomo', 'יוסף': 'yosef', 'בנימין': 'benjamin',
        'שרה': 'sarah', 'רבקה': 'rivka', 'רחל': 'rachel', 'לאה': 'leah',
        'כהן': 'cohen', 'לוי': 'levi', 'ישראל': 'israel',
        'יונתן': 'yonatan', 'דניאל': 'daniel', 'אליהו': 'eliyahu', 'שמואל': 'shmuel',
        'אהרון': 'aharon', 'יהודה': 'yehuda', 'ראובן': 'reuven', 'שמעון': 'shimon',
        'חוה': 'chava', 'נעמי': 'naomi', 'תמר': 'tamar', 'מיכל': 'michal',
        'עדינה': 'adina', 'חנה': 'chana', 'אלישבע': 'elishava', 'ציפורה': 'tzipora',
        'שלום': 'shalom', 'בן-דוד': 'bendavid', 'בן-חיים': 'benhaim',
        'בן-שמואל': 'benshmuel', 'בן-אברהם': 'benavraham', 'בן-יעקב': 'benyaakov',
        'רוזן': 'rozen', 'גולד': 'gold', 'כספי': 'kesefi', 'דיין': 'dayan',
        'שטרן': 'stern', 'ברגר': 'berger', 'כץ': 'katz'
    }
    
    # Transliterate names
    first_translit = translit_map.get(first_name, first_name)
    last_translit = translit_map.get(last_name, last_name)
    
    # Remove Hebrew characters and keep only ASCII
    first_clean = ''.join(c for c in first_translit if ord(c) < 128).lower()
    last_clean = ''.join(c for c in last_translit if ord(c) < 128).lower()
    
    # If still contains non-ASCII, use generic name
    if not first_clean or not last_clean:
        base = f"user{random.randint(1000, 9999)}"
    else:
        base = f"{first_clean}.{last_clean}".replace(" ", "").replace("-", "")
    
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "walla.co.il", "012.net.il"]
    return f"{base}{random.randint(1, 999)}@{random.choice(domains)}"


def create_hebrew_sample_database(target_db: str = "tama38_hebrew_sample"):
    """
    Create a Hebrew sample database with the specified structure
    """
    print("=" * 70)
    print("CREATING HEBREW SAMPLE DATABASE")
    print("=" * 70)
    
    # Step 1: Create database
    print("\nStep 1: Creating database...")
    create_database(target_db)
    
    # Step 2: Run migrations
    print("\nStep 2: Running migrations...")
    run_migrations(target_db)
    
    # Step 3: Connect to new database
    print("\nStep 3: Connecting to new database...")
    db_config = parse_database_url(settings.DATABASE_URL)
    new_url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{target_db}"
    
    # Create new engine and session
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    new_engine = create_engine(new_url)
    NewSessionLocal = sessionmaker(bind=new_engine)
    db = NewSessionLocal()
    
    try:
        # Step 4: Create admin user
        print("\nStep 4: Creating admin user...")
        admin = User(
            email="admin@tama38.local",
            hashed_password=get_password_hash("Admin123!@#"),
            full_name="מנהל מערכת",  # System Administrator in Hebrew
            role="SUPER_ADMIN",
            is_active=True,
            is_verified=True,
        )
        db.add(admin)
        db.flush()
        print("✓ Created admin user")
        
        # Step 5: Create sample projects and data
        print("\nStep 5: Creating sample projects, buildings, units, and owners...")
        
        # Project 1: 4 buildings
        project1_name_en = "Ramat Gan Urban Renewal - Phase 1"
        project1_name_he = translate_to_hebrew(project1_name_en)
        
        project1 = Project(
            project_name=project1_name_he,
            project_code="RG-UR-2024-001",
            project_type="TAMA38_1",
            location_city=translate_to_hebrew("Ramat Gan"),
            location_address=translate_to_hebrew("Bialik Street Area, Ramat Gan"),
            description=translate_to_hebrew("Urban renewal project in Ramat Gan city center"),
            required_majority_percent=Decimal("66.67"),
            majority_calc_type="HEADCOUNT",
            critical_threshold_percent=Decimal("50.0"),
            project_stage="ACTIVE",
            business_sponsor=translate_to_hebrew("Ramat Gan Municipality"),
            launch_date=date.today() - timedelta(days=180),
            estimated_completion_date=date.today() + timedelta(days=365),
        )
        db.add(project1)
        db.flush()
        print(f"  ✓ Created project: {project1_name_he}")
        
        # Project 1 buildings: 4 buildings with 16-28 units each
        building_counts = [16, 20, 24, 28]  # 4 buildings
        for i, unit_count in enumerate(building_counts, 1):
            building_name_en = f"Building {i}"
            building_name_he = translate_to_hebrew(building_name_en)
            building_address_he = translate_to_hebrew(f"{i * 10} Bialik Street, Ramat Gan")
            
            building = Building(
                project_id=project1.project_id,
                building_name=building_name_he,
                building_code=f"RG-B{i:02d}",
                address=building_address_he,
                floor_count=random.randint(4, 8),
                total_units=unit_count,
                structure_type=random.choice(["CONCRETE", "MASONRY", "MIXED"]),
                current_status=random.choice(["INITIAL", "NEGOTIATING", "APPROVED"]),
                traffic_light_status=random.choice(["GREEN", "YELLOW", "RED", "GRAY"]),
                signature_percentage=Decimal(str(random.uniform(0, 85))),
            )
            db.add(building)
            db.flush()
            print(f"    ✓ Created building: {building_name_he} ({unit_count} units)")
            
            # Create units for this building
            floor_count = building.floor_count
            units_per_floor = unit_count // floor_count
            unit_counter = 1
            
            for floor in range(1, floor_count + 1):
                units_on_floor = units_per_floor if floor < floor_count else unit_count - (floor - 1) * units_per_floor
                
                for unit_num in range(1, units_on_floor + 1):
                    unit = Unit(
                        building_id=building.building_id,
                        floor_number=floor,
                        unit_number=str(unit_num),
                        unit_full_identifier=f"{floor}-{unit_num}",
                        area_sqm=Decimal(str(random.uniform(60, 120))),
                        room_count=random.choice([3, 4, 5]),
                        unit_status=random.choice(["NOT_CONTACTED", "NEGOTIATING", "AGREED_TO_SIGN", "SIGNED", "PARTIALLY_SIGNED"]),
                        signature_percentage=Decimal(str(random.uniform(0, 100))),
                    )
                    db.add(unit)
                    db.flush()
                    
                    # Create 1-3 owners per unit
                    num_owners = random.randint(1, 3)
                    total_share = 100.0
                    
                    for owner_idx in range(num_owners):
                        owner_name = generate_hebrew_name()
                        first_name, last_name = owner_name.split(' ', 1)
                        
                        if owner_idx == num_owners - 1:
                            ownership_share = total_share
                        else:
                            min_share = 20.0
                            max_share = min(50.0, total_share - min_share * (num_owners - owner_idx - 1))
                            ownership_share = round(random.uniform(min_share, max_share), 2)
                            total_share -= ownership_share
                        
                        owner = Owner(
                            unit_id=unit.unit_id,
                            full_name=owner_name,
                            phone_for_contact=generate_phone(),
                            email=generate_email(first_name, last_name),
                            id_type="ISRAELI_ID",
                            ownership_share_percent=Decimal(str(ownership_share)),
                            ownership_type="SOLE_OWNER" if num_owners == 1 else "CO_OWNER_JOINT",
                            owner_status=random.choice(["NOT_CONTACTED", "NEGOTIATING", "AGREED_TO_SIGN", "SIGNED", "WAIT_FOR_SIGN"]),
                            is_primary_contact=(owner_idx == 0),
                            preferred_contact_method=random.choice(["PHONE", "WHATSAPP", "EMAIL"]),
                            preferred_language="HEBREW",
                            is_current_owner=True,
                        )
                        db.add(owner)
                    
                    unit.total_owners = num_owners
                    unit.is_co_owned = (num_owners > 1)
        
        # Project 2: 2 buildings
        project2_name_en = "Tel Aviv Center Renovation"
        project2_name_he = translate_to_hebrew(project2_name_en)
        
        project2 = Project(
            project_name=project2_name_he,
            project_code="TA-CR-2024-002",
            project_type="TAMA38_2",
            location_city=translate_to_hebrew("Tel Aviv"),
            location_address=translate_to_hebrew("Rothschild Boulevard Area, Tel Aviv"),
            description=translate_to_hebrew("Renovation project in Tel Aviv city center"),
            required_majority_percent=Decimal("66.67"),
            majority_calc_type="AREA",
            critical_threshold_percent=Decimal("50.0"),
            project_stage="ACTIVE",
            business_sponsor=translate_to_hebrew("Tel Aviv Municipality"),
            launch_date=date.today() - timedelta(days=120),
            estimated_completion_date=date.today() + timedelta(days=400),
        )
        db.add(project2)
        db.flush()
        print(f"  ✓ Created project: {project2_name_he}")
        
        # Project 2 buildings: 2 buildings with 16-28 units each
        building_counts = [18, 26]  # 2 buildings
        for i, unit_count in enumerate(building_counts, 1):
            building_name_en = f"Rothschild Building {i}"
            building_name_he = translate_to_hebrew(building_name_en)
            building_address_he = translate_to_hebrew(f"{40 + i * 2} Rothschild Boulevard, Tel Aviv")
            
            building = Building(
                project_id=project2.project_id,
                building_name=building_name_he,
                building_code=f"TA-RB{i:02d}",
                address=building_address_he,
                floor_count=random.randint(5, 7),
                total_units=unit_count,
                structure_type=random.choice(["CONCRETE", "MASONRY", "MIXED"]),
                current_status=random.choice(["INITIAL", "NEGOTIATING", "APPROVED"]),
                traffic_light_status=random.choice(["GREEN", "YELLOW", "RED", "GRAY"]),
                signature_percentage=Decimal(str(random.uniform(0, 85))),
            )
            db.add(building)
            db.flush()
            print(f"    ✓ Created building: {building_name_he} ({unit_count} units)")
            
            # Create units for this building
            floor_count = building.floor_count
            units_per_floor = unit_count // floor_count
            unit_counter = 1
            
            for floor in range(1, floor_count + 1):
                units_on_floor = units_per_floor if floor < floor_count else unit_count - (floor - 1) * units_per_floor
                
                for unit_num in range(1, units_on_floor + 1):
                    unit = Unit(
                        building_id=building.building_id,
                        floor_number=floor,
                        unit_number=str(unit_num),
                        unit_full_identifier=f"{floor}-{unit_num}",
                        area_sqm=Decimal(str(random.uniform(60, 120))),
                        room_count=random.choice([3, 4, 5]),
                        unit_status=random.choice(["NOT_CONTACTED", "NEGOTIATING", "AGREED_TO_SIGN", "SIGNED", "PARTIALLY_SIGNED"]),
                        signature_percentage=Decimal(str(random.uniform(0, 100))),
                    )
                    db.add(unit)
                    db.flush()
                    
                    # Create 1-3 owners per unit
                    num_owners = random.randint(1, 3)
                    total_share = 100.0
                    
                    for owner_idx in range(num_owners):
                        owner_name = generate_hebrew_name()
                        first_name, last_name = owner_name.split(' ', 1)
                        
                        if owner_idx == num_owners - 1:
                            ownership_share = total_share
                        else:
                            min_share = 20.0
                            max_share = min(50.0, total_share - min_share * (num_owners - owner_idx - 1))
                            ownership_share = round(random.uniform(min_share, max_share), 2)
                            total_share -= ownership_share
                        
                        owner = Owner(
                            unit_id=unit.unit_id,
                            full_name=owner_name,
                            phone_for_contact=generate_phone(),
                            email=generate_email(first_name, last_name),
                            id_type="ISRAELI_ID",
                            ownership_share_percent=Decimal(str(ownership_share)),
                            ownership_type="SOLE_OWNER" if num_owners == 1 else "CO_OWNER_JOINT",
                            owner_status=random.choice(["NOT_CONTACTED", "NEGOTIATING", "AGREED_TO_SIGN", "SIGNED", "WAIT_FOR_SIGN"]),
                            is_primary_contact=(owner_idx == 0),
                            preferred_contact_method=random.choice(["PHONE", "WHATSAPP", "EMAIL"]),
                            preferred_language="HEBREW",
                            is_current_owner=True,
                        )
                        db.add(owner)
                    
                    unit.total_owners = num_owners
                    unit.is_co_owned = (num_owners > 1)
        
        # Commit all changes
        db.commit()
        
        # Print statistics
        print("\n" + "=" * 70)
        print("DATABASE CREATION COMPLETE")
        print("=" * 70)
        projects_count = db.query(Project).count()
        buildings_count = db.query(Building).count()
        units_count = db.query(Unit).count()
        owners_count = db.query(Owner).count()
        
        print(f"Projects: {projects_count}")
        print(f"Buildings: {buildings_count}")
        print(f"Units: {units_count}")
        print(f"Owners: {owners_count}")
        print(f"\nDatabase name: {target_db}")
        print(f"\nTo connect to this database, update DATABASE_URL:")
        print(f"  DATABASE_URL=postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{target_db}")
        print("=" * 70)
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ Error creating database: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Create Hebrew sample database')
    parser.add_argument('--db-name', '-d', default='tama38_hebrew_sample', help='Target database name')
    args = parser.parse_args()
    
    create_hebrew_sample_database(args.db_name)


if __name__ == "__main__":
    main()

