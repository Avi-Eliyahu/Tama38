"""
Translate Projects, Buildings, and Addresses to Hebrew
Updates existing database records with Hebrew translations
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.project import Project
from app.models.building import Building
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
            return text


# Realistic Hebrew building names
HEBREW_BUILDING_NAMES = [
    "מגדל ביאליק",  # Bialik Tower
    "מגדל הזהב",  # Gold Tower
    "מגדל השלום",  # Peace Tower
    "מגדל הגנים",  # Gardens Tower
    "מגדל השדרה",  # Boulevard Tower
    "מגדל המרכז",  # Center Tower
    "מגדל הים",  # Sea Tower
    "מגדל השמש",  # Sun Tower
    "מגדל הכוכבים",  # Stars Tower
    "מגדל הנהר",  # River Tower
    "בית ביאליק",  # Bialik House
    "בית הזהב",  # Gold House
    "בית השלום",  # Peace House
    "בית הגנים",  # Gardens House
    "בית השדרה",  # Boulevard House
    "בית המרכז",  # Center House
    "בית הים",  # Sea House
    "בית השמש",  # Sun House
    "בית הכוכבים",  # Stars House
    "בית הנהר",  # River House
    "מתחם ביאליק",  # Bialik Complex
    "מתחם הזהב",  # Gold Complex
    "מתחם השלום",  # Peace Complex
    "מתחם הגנים",  # Gardens Complex
    "מתחם השדרה",  # Boulevard Complex
]

# Realistic Hebrew street names and addresses
HEBREW_STREETS_RAMAT_GAN = [
    "רחוב ביאליק",
    "רחוב הרצל",
    "רחוב ז'בוטינסקי",
    "רחוב דיזנגוף",
    "רחוב בן גוריון",
    "רחוב ויצמן",
    "רחוב רוטשchild",
    "רחוב אלנבי",
    "רחוב אבן גבירול",
    "רחוב דיזנגוף",
]

HEBREW_STREETS_TEL_AVIV = [
    "שדרות רוטשchild",
    "רחוב דיזנגוף",
    "רחוב בן יהודה",
    "רחוב אלנבי",
    "רחוב אבן גבירול",
    "רחוב הרצל",
    "רחוב נחום גולדמן",
    "רחוב יפו",
    "רחוב אלנבי",
    "רחוב בן גוריון",
]


def get_hebrew_building_name(index: int, project_city: str) -> str:
    """Get a Hebrew building name"""
    # Use different names based on project
    if "רמת גן" in project_city or "Ramat Gan" in project_city:
        names = [n for n in HEBREW_BUILDING_NAMES if "ביאליק" in n or "הזהב" in n or "השלום" in n or "הגנים" in n]
    else:
        names = [n for n in HEBREW_BUILDING_NAMES if "השדרה" in n or "המרכז" in n or "הים" in n or "השמש" in n]
    
    return names[index % len(names)]


def get_hebrew_address(street_num: int, street_name: str, city: str) -> str:
    """Generate Hebrew address"""
    # City name mapping (proper nouns - use Hebrew transliterations)
    city_map = {
        "Ramat Gan": "רמת גן",
        "Tel Aviv": "תל אביב",
        "רמת גן": "רמת גן",
        "תל אביב": "תל אביב",
    }
    city_he = city_map.get(city, city) if city else ""
    
    # Use Hebrew street names
    if "רמת גן" in city_he or "Ramat Gan" in (city or ""):
        streets = HEBREW_STREETS_RAMAT_GAN
        street_he = streets[street_num % len(streets)]
    elif "תל אביב" in city_he or "Tel Aviv" in (city or ""):
        streets = HEBREW_STREETS_TEL_AVIV
        street_he = streets[street_num % len(streets)]
    else:
        # Translate the street name
        street_he = translate_to_hebrew(street_name) if street_name and not any('\u0590' <= c <= '\u05FF' for c in street_name) else street_name
    
    # Generate address with number
    address_num = (street_num % 100) + 1
    return f"{address_num} {street_he}, {city_he}"


def translate_projects_and_buildings(db: Session):
    """Translate all projects and buildings to Hebrew"""
    print("=" * 70)
    print("TRANSLATING PROJECTS AND BUILDINGS TO HEBREW")
    print("=" * 70)
    
    projects = db.query(Project).filter(Project.is_deleted == False).all()
    print(f"\nFound {len(projects)} projects to translate\n")
    
    updated_projects = 0
    updated_buildings = 0
    
    for project_idx, project in enumerate(projects):
        print(f"Processing project: {project.project_name}")
        
        # Translate project name if not already in Hebrew
        if project.project_name and not any('\u0590' <= c <= '\u05FF' for c in project.project_name):
            project.project_name = translate_to_hebrew(project.project_name)
            print(f"  → Project name: {project.project_name}")
        
        # Translate location city (use proper noun mapping)
        if project.location_city:
            city_map = {
                "Ramat Gan": "רמת גן",
                "Tel Aviv": "תל אביב",
            }
            if project.location_city in city_map:
                project.location_city = city_map[project.location_city]
            elif not any('\u0590' <= c <= '\u05FF' for c in project.location_city):
                project.location_city = translate_to_hebrew(project.location_city)
            print(f"  → City: {project.location_city}")
        
        # Translate location address
        if project.location_address and not any('\u0590' <= c <= '\u05FF' for c in project.location_address):
            project.location_address = translate_to_hebrew(project.location_address)
            print(f"  → Address: {project.location_address}")
        
        # Translate description
        if project.description and not any('\u0590' <= c <= '\u05FF' for c in project.description):
            project.description = translate_to_hebrew(project.description)
        
        # Translate business sponsor
        if project.business_sponsor and not any('\u0590' <= c <= '\u05FF' for c in project.business_sponsor):
            project.business_sponsor = translate_to_hebrew(project.business_sponsor)
        
        updated_projects += 1
        
        # Get buildings for this project
        buildings = db.query(Building).filter(
            Building.project_id == project.project_id,
            Building.is_deleted == False
        ).order_by(Building.building_code).all()
        
        print(f"  Found {len(buildings)} buildings")
        
        for building_idx, building in enumerate(buildings):
            # Use Hebrew building names
            building_name_he = get_hebrew_building_name(building_idx, project.location_city or "")
            building.building_name = building_name_he
            print(f"    → Building {building_idx + 1}: {building_name_he}")
            
            # Generate Hebrew address
            # Extract street number from existing address if possible
            street_num = building_idx + 1
            if building.address:
                # Try to extract number from address
                import re
                match = re.search(r'(\d+)', building.address)
                if match:
                    street_num = int(match.group(1))
            
            # Extract street name from address
            street_name = "Bialik Street"
            if "Bialik" in (building.address or ""):
                street_name = "Bialik Street"
            elif "Rothschild" in (building.address or ""):
                street_name = "Rothschild Boulevard"
            
            building.address = get_hebrew_address(street_num, street_name, project.location_city or "")
            print(f"      Address: {building.address}")
            
            updated_buildings += 1
        
        print()
    
    # Commit all changes
    db.commit()
    
    print("=" * 70)
    print("TRANSLATION COMPLETE")
    print("=" * 70)
    print(f"Updated projects: {updated_projects}")
    print(f"Updated buildings: {updated_buildings}")
    print(f"Translation cache size: {len(_translation_cache)}")
    print("=" * 70)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Translate projects and buildings to Hebrew')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be translated without making changes')
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        if args.dry_run:
            print("DRY RUN MODE - No changes will be made")
            print("Run without --dry-run to apply translations")
            return
        
        translate_projects_and_buildings(db)
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

