"""
Database Seeding Script
Creates initial data for testing: 2 projects, 4-6 buildings, units, owners, agents, and interactions
Run from backend directory: python scripts/seed_database.py
Or from project root: docker-compose exec backend python scripts/seed_database.py
"""
import sys
import os

# Add backend directory to path (script is in scripts/ but needs app/ from backend/)
# Script is in root/scripts/, backend is in root/backend/
script_dir = os.path.dirname(os.path.abspath(__file__))  # root/scripts/
project_root = os.path.dirname(script_dir)  # root/
backend_dir = os.path.join(project_root, 'backend')  # root/backend/
sys.path.insert(0, backend_dir)

from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from decimal import Decimal
import random
import uuid
from app.core.database import SessionLocal, engine
from app.models.project import Project
from app.models.building import Building
from app.models.unit import Unit
from app.models.owner import Owner
from app.models.user import User
from app.models.interaction import Interaction
from app.core.security import get_password_hash

# Sample data
PROJECTS_DATA = [
    {
        "project_name": "Ramat Gan Urban Renewal - Phase 1",
        "project_code": "RG-UR-2024-001",
        "project_type": "TAMA38_1",
        "location_city": "Ramat Gan",
        "location_address": "Bialik Street Area, Ramat Gan",
        "required_majority_percent": 66.67,
        "majority_calc_type": "HEADCOUNT",
        "critical_threshold_percent": 50.0,
        "project_stage": "ACTIVE",
        "buildings": [
            {
                "building_name": "Bialik Tower A",
                "building_code": "RG-BA-001",
                "address": "15 Bialik Street, Ramat Gan",
                "floor_count": 8,
                "total_units": 24,
                "structure_type": "CONCRETE",
                "current_status": "NEGOTIATING",
                "traffic_light_status": "YELLOW",
            },
            {
                "building_name": "Bialik Tower B",
                "building_code": "RG-BB-002",
                "address": "17 Bialik Street, Ramat Gan",
                "floor_count": 6,
                "total_units": 18,
                "structure_type": "CONCRETE",
                "current_status": "INITIAL",
                "traffic_light_status": "RED",
            },
        ]
    },
    {
        "project_name": "Tel Aviv Center Renovation",
        "project_code": "TA-CR-2024-002",
        "project_type": "TAMA38_2",
        "location_city": "Tel Aviv",
        "location_address": "Rothschild Boulevard Area, Tel Aviv",
        "required_majority_percent": 66.67,
        "majority_calc_type": "AREA",
        "critical_threshold_percent": 50.0,
        "project_stage": "ACTIVE",
        "buildings": [
            {
                "building_name": "Rothschild Heights",
                "building_code": "TA-RH-001",
                "address": "42 Rothschild Boulevard, Tel Aviv",
                "floor_count": 5,
                "total_units": 15,
                "structure_type": "MASONRY",
                "current_status": "APPROVED",
                "traffic_light_status": "GREEN",
            },
            {
                "building_name": "Rothschild Gardens",
                "building_code": "TA-RG-002",
                "address": "48 Rothschild Boulevard, Tel Aviv",
                "floor_count": 4,
                "total_units": 12,
                "structure_type": "MASONRY",
                "current_status": "NEGOTIATING",
                "traffic_light_status": "YELLOW",
            },
            {
                "building_name": "Rothschild Plaza",
                "building_code": "TA-RP-003",
                "address": "52 Rothschild Boulevard, Tel Aviv",
                "floor_count": 7,
                "total_units": 21,
                "structure_type": "CONCRETE",
                "current_status": "RENOVATION_PLANNING",
                "traffic_light_status": "GREEN",
            },
            {
                "building_name": "Rothschild View",
                "building_code": "TA-RV-004",
                "address": "56 Rothschild Boulevard, Tel Aviv",
                "floor_count": 6,
                "total_units": 18,
                "structure_type": "MIXED",
                "current_status": "INITIAL",
                "traffic_light_status": "RED",
            },
        ]
    }
]

# Israeli names and addresses
OWNERS_DATA = [
    # Project 1, Building 1 (Bialik Tower A)
    {"name": "David Cohen", "phone": "050-1234567", "email": "david.cohen@example.com", "id": "123456789", "status": "NEGOTIATING", "share": 100},
    {"name": "Sarah Levi", "phone": "052-2345678", "email": "sarah.levi@example.com", "id": "234567890", "status": "AGREED_TO_SIGN", "share": 100},
    {"name": "Moshe Mizrahi", "phone": "054-3456789", "email": "moshe.mizrahi@example.com", "id": "345678901", "status": "SIGNED", "share": 100},
    {"name": "Rachel Avraham", "phone": "050-4567890", "email": "rachel.avraham@example.com", "id": "456789012", "status": "NOT_CONTACTED", "share": 100},
    {"name": "Yosef Ben-David", "phone": "052-5678901", "email": "yosef.bendavid@example.com", "id": "567890123", "status": "NEGOTIATING", "share": 100},
    {"name": "Miriam Shalom", "phone": "054-6789012", "email": "miriam.shalom@example.com", "id": "678901234", "status": "WAIT_FOR_SIGN", "share": 100},
    {"name": "Aharon Friedman", "phone": "050-7890123", "email": "aharon.friedman@example.com", "id": "789012345", "status": "REFUSED", "share": 100},
    {"name": "Esther Goldberg", "phone": "052-8901234", "email": "esther.goldberg@example.com", "id": "890123456", "status": "SIGNED", "share": 100},
    # Co-owners example
    {"name": "Ruth and Shimon Katz", "phone": "050-9012345", "email": "ruth.katz@example.com", "id": "901234567", "status": "NEGOTIATING", "share": 50},
    {"name": "Shimon Katz", "phone": "052-0123456", "email": "shimon.katz@example.com", "id": "012345678", "status": "NEGOTIATING", "share": 50},
    
    # Project 1, Building 2 (Bialik Tower B)
    {"name": "Daniel Rosen", "phone": "054-1234567", "email": "daniel.rosen@example.com", "id": "111111111", "status": "NOT_CONTACTED", "share": 100},
    {"name": "Leah Schwartz", "phone": "050-2222222", "email": "leah.schwartz@example.com", "id": "222222222", "status": "NOT_CONTACTED", "share": 100},
    {"name": "Yitzhak Meir", "phone": "052-3333333", "email": "yitzhak.meir@example.com", "id": "333333333", "status": "NEGOTIATING", "share": 100},
    {"name": "Chana Weiss", "phone": "054-4444444", "email": "chana.weiss@example.com", "id": "444444444", "status": "AGREED_TO_SIGN", "share": 100},
    {"name": "Shlomo Baruch", "phone": "050-5555555", "email": "shlomo.baruch@example.com", "id": "555555555", "status": "REFUSED", "share": 100},
    
    # Project 2, Building 1 (Rothschild Heights)
    {"name": "Avi Tal", "phone": "052-6666666", "email": "avi.tal@example.com", "id": "666666666", "status": "SIGNED", "share": 100},
    {"name": "Tova Segal", "phone": "054-7777777", "email": "tova.segal@example.com", "id": "777777777", "status": "SIGNED", "share": 100},
    {"name": "Eliyahu Gross", "phone": "050-8888888", "email": "eliyahu.gross@example.com", "id": "888888888", "status": "SIGNED", "share": 100},
    {"name": "Rivka Adler", "phone": "052-9999999", "email": "rivka.adler@example.com", "id": "999999999", "status": "WAIT_FOR_SIGN", "share": 100},
    {"name": "Menachem Stein", "phone": "054-1010101", "email": "menachem.stein@example.com", "id": "101010101", "status": "NEGOTIATING", "share": 100},
    
    # Project 2, Building 2 (Rothschild Gardens)
    {"name": "Yael Rubin", "phone": "050-2020202", "email": "yael.rubin@example.com", "id": "202020202", "status": "AGREED_TO_SIGN", "share": 100},
    {"name": "Baruch Klein", "phone": "052-3030303", "email": "baruch.klein@example.com", "id": "303030303", "status": "NEGOTIATING", "share": 100},
    {"name": "Devorah Berger", "phone": "054-4040404", "email": "devorah.berger@example.com", "id": "404040404", "status": "NOT_CONTACTED", "share": 100},
    
    # Project 2, Building 3 (Rothschild Plaza)
    {"name": "Gershon Feiner", "phone": "050-5050505", "email": "gershon.feiner@example.com", "id": "505050505", "status": "SIGNED", "share": 100},
    {"name": "Hannah Morgenstern", "phone": "052-6060606", "email": "hannah.morgenstern@example.com", "id": "606060606", "status": "SIGNED", "share": 100},
    {"name": "Yehuda Horowitz", "phone": "054-7070707", "email": "yehuda.horowitz@example.com", "id": "707070707", "status": "SIGNED", "share": 100},
    {"name": "Sima Landau", "phone": "050-8080808", "email": "sima.landau@example.com", "id": "808080808", "status": "WAIT_FOR_SIGN", "share": 100},
    {"name": "Zvi Perlman", "phone": "052-9090909", "email": "zvi.perlman@example.com", "id": "909090909", "status": "NEGOTIATING", "share": 100},
    
    # Project 2, Building 4 (Rothschild View)
    {"name": "Malka Stern", "phone": "054-1111111", "email": "malka.stern@example.com", "id": "111111112", "status": "NOT_CONTACTED", "share": 100},
    {"name": "Pinchas Gruber", "phone": "050-2222223", "email": "pinchas.gruber@example.com", "id": "222222223", "status": "NOT_CONTACTED", "share": 100},
    {"name": "Bracha Heller", "phone": "052-3333334", "email": "bracha.heller@example.com", "id": "333333334", "status": "NEGOTIATING", "share": 100},
]

AGENTS_DATA = [
    {"name": "Rina Cohen", "email": "rina.cohen@tama38.local", "phone": "050-1111111", "role": "AGENT"},
    {"name": "Amir Levi", "email": "amir.levi@tama38.local", "phone": "052-2222222", "role": "AGENT"},
    {"name": "Tamar Mizrahi", "email": "tamar.mizrahi@tama38.local", "phone": "054-3333333", "role": "AGENT"},
    {"name": "Oren Avraham", "email": "oren.avraham@tama38.local", "phone": "050-4444444", "role": "AGENT"},
]

INTERACTION_TYPES = ["PHONE_CALL", "WHATSAPP", "IN_PERSON_MEETING", "EMAIL", "SMS"]
OUTCOMES = ["POSITIVE", "NEUTRAL", "NEGATIVE", "AGREED_TO_MEET", "AGREED_TO_SIGN"]
SENTIMENTS = ["VERY_POSITIVE", "POSITIVE", "NEUTRAL", "NEGATIVE", "VERY_NEGATIVE"]

def create_users(db: Session):
    """Create 4 agents"""
    print("Creating agents...")
    agents = []
    for agent_data in AGENTS_DATA:
        user = User(
            email=agent_data["email"],
            hashed_password=get_password_hash("Agent123!@#"),
            full_name=agent_data["name"],
            role=agent_data["role"],
            phone=agent_data["phone"],
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        agents.append(user)
    
    db.commit()
    print(f"✓ Created {len(agents)} agents")
    return agents

def create_projects_and_buildings(db: Session, agents: list):
    """Create projects, buildings, units, and owners"""
    print("\nCreating projects, buildings, units, and owners...")
    
    projects = []
    all_buildings = []
    all_units = []
    all_owners = []
    
    owner_index = 0
    
    for project_data in PROJECTS_DATA:
        # Create project
        project = Project(
            project_name=project_data["project_name"],
            project_code=project_data["project_code"],
            project_type=project_data["project_type"],
            location_city=project_data["location_city"],
            location_address=project_data["location_address"],
            required_majority_percent=Decimal(str(project_data["required_majority_percent"])),
            majority_calc_type=project_data["majority_calc_type"],
            critical_threshold_percent=Decimal(str(project_data["critical_threshold_percent"])),
            project_stage=project_data["project_stage"],
            launch_date=date.today() - timedelta(days=180),
            estimated_completion_date=date.today() + timedelta(days=365),
        )
        db.add(project)
        db.flush()
        projects.append(project)
        print(f"  ✓ Created project: {project.project_name}")
        
        # Create buildings for this project
        for building_data in project_data["buildings"]:
            building = Building(
                project_id=project.project_id,
                building_name=building_data["building_name"],
                building_code=building_data["building_code"],
                address=building_data["address"],
                floor_count=building_data["floor_count"],
                total_units=building_data["total_units"],
                structure_type=building_data["structure_type"],
                current_status=building_data["current_status"],
                traffic_light_status=building_data["traffic_light_status"],
                assigned_agent_id=random.choice(agents).user_id if agents else None,
                signature_percentage=Decimal(str(random.uniform(20, 85))),
            )
            db.add(building)
            db.flush()
            all_buildings.append(building)
            print(f"    ✓ Created building: {building.building_name}")
            
            # Create units for this building
            units_per_floor = building_data["total_units"] // building_data["floor_count"]
            unit_counter = 1
            
            for floor in range(1, building_data["floor_count"] + 1):
                units_on_floor = units_per_floor if floor < building_data["floor_count"] else building_data["total_units"] - (floor - 1) * units_per_floor
                
                for unit_num in range(1, units_on_floor + 1):
                    unit = Unit(
                        building_id=building.building_id,
                        floor_number=floor,
                        unit_number=str(unit_num),
                        unit_full_identifier=f"{floor}-{unit_num}",
                        area_sqm=Decimal(str(random.uniform(60, 120))),
                        room_count=random.choice([3, 4, 5]),
                        unit_status=random.choice(["NOT_CONTACTED", "NEGOTIATING", "AGREED_TO_SIGN", "SIGNED", "REFUSED"]),
                        signature_percentage=Decimal(str(random.uniform(0, 100))),
                    )
                    db.add(unit)
                    db.flush()
                    all_units.append(unit)
                    
                    # Create owner(s) for this unit
                    if owner_index < len(OWNERS_DATA):
                        owner_data = OWNERS_DATA[owner_index]
                        owner_index += 1
                        
                        # Check if co-owner
                        is_co_owner = owner_data["share"] < 100
                        if is_co_owner:
                            unit.is_co_owned = True
                            unit.total_owners = 2
                        else:
                            unit.total_owners = 1
                        
                        owner = Owner(
                            unit_id=unit.unit_id,
                            full_name=owner_data["name"],
                            phone_for_contact=owner_data["phone"],
                            email=owner_data["email"],
                            id_type="ISRAELI_ID",
                            ownership_share_percent=Decimal(str(owner_data["share"])),
                            ownership_type="SOLE_OWNER" if owner_data["share"] == 100 else "CO_OWNER_JOINT",
                            owner_status=owner_data["status"],
                            is_primary_contact=True,
                            preferred_contact_method=random.choice(["PHONE", "WHATSAPP", "EMAIL"]),
                            preferred_language=random.choice(["HEBREW", "ENGLISH", "RUSSIAN"]),
                            assigned_agent_id=random.choice(agents).user_id if agents else None,
                        )
                        db.add(owner)
                        all_owners.append(owner)
                        
                        # If co-owner, create second owner
                        if is_co_owner and owner_index < len(OWNERS_DATA):
                            co_owner_data = OWNERS_DATA[owner_index]
                            owner_index += 1
                            co_owner = Owner(
                                unit_id=unit.unit_id,
                                full_name=co_owner_data["name"],
                                phone_for_contact=co_owner_data["phone"],
                                email=co_owner_data["email"],
                                id_type="ISRAELI_ID",
                                ownership_share_percent=Decimal(str(co_owner_data["share"])),
                                ownership_type="CO_OWNER_JOINT",
                                owner_status=co_owner_data["status"],
                                is_primary_contact=False,
                                preferred_contact_method=random.choice(["PHONE", "WHATSAPP", "EMAIL"]),
                                preferred_language=random.choice(["HEBREW", "ENGLISH", "RUSSIAN"]),
                                assigned_agent_id=random.choice(agents).user_id if agents else None,
                            )
                            db.add(co_owner)
                            all_owners.append(co_owner)
                    
                    unit_counter += 1
            
            db.commit()
    
    print(f"\n✓ Created {len(projects)} projects")
    print(f"✓ Created {len(all_buildings)} buildings")
    print(f"✓ Created {len(all_units)} units")
    print(f"✓ Created {len(all_owners)} owners")
    
    return projects, all_buildings, all_units, all_owners

def create_interactions(db: Session, owners: list, agents: list):
    """Create interaction logs"""
    print("\nCreating interaction logs...")
    
    interactions = []
    base_date = date.today() - timedelta(days=90)
    
    for owner in owners:
        # Create 2-5 interactions per owner
        num_interactions = random.randint(2, 5)
        
        for i in range(num_interactions):
            interaction_date = base_date + timedelta(days=random.randint(0, 90))
            interaction = Interaction(
                owner_id=owner.owner_id,
                agent_id=random.choice(agents).user_id,
                interaction_type=random.choice(INTERACTION_TYPES),
                interaction_date=interaction_date,
                interaction_timestamp=datetime.combine(interaction_date, datetime.min.time()) + timedelta(hours=random.randint(9, 17)),
                duration_minutes=random.randint(5, 60),
                outcome=random.choice(OUTCOMES),
                call_summary=f"Contacted owner {owner.full_name} regarding TAMA38 project. Discussed renovation plans and timeline.",
                sentiment=random.choice(SENTIMENTS),
                contact_method_used=random.choice(["PHONE", "WHATSAPP", "EMAIL", "IN_PERSON"]),
                source="WEB_APP",
            )
            db.add(interaction)
            interactions.append(interaction)
    
    db.commit()
    print(f"✓ Created {len(interactions)} interaction logs")
    return interactions

def main():
    """Main seeding function"""
    print("=" * 60)
    print("TAMA38 Database Seeding Script")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Create agents
        agents = create_users(db)
        
        # Create projects, buildings, units, and owners
        projects, buildings, units, owners = create_projects_and_buildings(db, agents)
        
        # Create interactions
        interactions = create_interactions(db, owners, agents)
        
        print("\n" + "=" * 60)
        print("Seeding completed successfully!")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  - Projects: {len(projects)}")
        print(f"  - Buildings: {len(buildings)}")
        print(f"  - Units: {len(units)}")
        print(f"  - Owners: {len(owners)}")
        print(f"  - Agents: {len(agents)}")
        print(f"  - Interactions: {len(interactions)}")
        print(f"\nYou can now login with:")
        print(f"  - Admin: admin@tama38.local / Admin123!@#")
        for agent in agents:
            print(f"  - {agent.full_name}: {agent.email} / Agent123!@#")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()

