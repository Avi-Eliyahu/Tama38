"""
Script to renumber apartments sequentially (1, 2, 3...) per building
across floors. Apartments are numbered sequentially starting from floor 1:
- Floor 1: Apartments 1, 2, 3...
- Floor 2: Apartments continue from where floor 1 ended (e.g., 4, 5, 6...)
- Floor 3: Apartments continue from where floor 2 ended (e.g., 7, 8, 9...)
- And so on...

Run from backend directory: python scripts/renumber_apartments.py
Or from project root: docker-compose exec backend python scripts/renumber_apartments.py

Usage:
    python scripts/renumber_apartments.py [--building-id BUILDING_ID] [--dry-run]
    
    --building-id: Optional. Renumber apartments for specific building only
    --dry-run: Show what would be changed without actually updating the database
"""
import sys
import os
import argparse
from sqlalchemy.orm import Session
from sqlalchemy import cast, Integer

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.core.database import SessionLocal
from app.models.unit import Unit
from app.models.building import Building
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def renumber_apartments(building_id: str = None, dry_run: bool = False):
    """
    Renumber apartments sequentially (1, 2, 3...) per building
    
    Args:
        building_id: Optional building ID to renumber. If None, renumbers all buildings
        dry_run: If True, only show what would be changed without updating
    """
    db: Session = SessionLocal()
    
    try:
        # Get buildings to process
        if building_id:
            buildings = db.query(Building).filter(
                Building.building_id == building_id,
                Building.is_deleted == False
            ).all()
            if not buildings:
                logger.error(f"Building {building_id} not found")
                return
        else:
            buildings = db.query(Building).filter(Building.is_deleted == False).all()
        
        total_changed = 0
        
        for building in buildings:
            logger.info(f"\nProcessing building: {building.building_name or building.building_code} ({building.building_id})")
            
            # Get all units for this building, ordered by floor_number first, then unit_number
            # This ensures apartments are numbered sequentially across floors:
            # Floor 1: 1, 2, 3
            # Floor 2: 4, 5, 6
            # Floor 3: 7, 8, 9
            # etc.
            units = db.query(Unit).filter(
                Unit.building_id == building.building_id,
                Unit.is_deleted == False
            ).order_by(
                Unit.floor_number.nulls_last(),  # Order by floor first
                cast(Unit.unit_number, Integer).nulls_last(),  # Then by current unit_number
                Unit.unit_number
            ).all()
            
            if not units:
                logger.info(f"  No units found for this building")
                continue
            
            logger.info(f"  Found {len(units)} apartments")
            
            # Renumber sequentially starting from 1
            changes = []
            for index, unit in enumerate(units, start=1):
                new_number = str(index)
                old_number = unit.unit_number
                
                if old_number != new_number:
                    changes.append({
                        'unit_id': str(unit.unit_id),
                        'old_number': old_number,
                        'new_number': new_number,
                        'floor': unit.floor_number
                    })
                    
                    if not dry_run:
                        unit.unit_number = new_number
                        # Update unit_full_identifier if it exists
                        if unit.floor_number is not None:
                            unit.unit_full_identifier = f"{unit.floor_number}-{new_number}"
                        else:
                            unit.unit_full_identifier = new_number
            
            if changes:
                logger.info(f"  Will renumber {len(changes)} apartments:")
                # Group changes by floor for better readability
                changes_by_floor = {}
                for change in changes:
                    floor = change['floor'] if change['floor'] is not None else 0
                    if floor not in changes_by_floor:
                        changes_by_floor[floor] = []
                    changes_by_floor[floor].append(change)
                
                for floor in sorted(changes_by_floor.keys()):
                    floor_label = f"Floor {floor}" if floor > 0 else "No floor"
                    logger.info(f"    {floor_label}:")
                    for change in changes_by_floor[floor]:
                        logger.info(f"      Apartment {change['old_number']} -> {change['new_number']} "
                                  f"(Unit ID: {change['unit_id'][:8]}...)")
                total_changed += len(changes)
                
                if not dry_run:
                    db.commit()
                    logger.info(f"  ✓ Successfully renumbered {len(changes)} apartments")
            else:
                logger.info(f"  All apartments already numbered sequentially")
        
        if dry_run:
            logger.info(f"\n✓ DRY RUN: Would renumber {total_changed} apartments")
            logger.info("Run without --dry-run to apply changes")
        else:
            logger.info(f"\n✓ Successfully renumbered {total_changed} apartments across {len(buildings)} building(s)")
            
    except Exception as e:
        db.rollback()
        logger.error(f"Error renumbering apartments: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Renumber apartments sequentially per building')
    parser.add_argument('--building-id', type=str, help='Building ID to renumber (optional)')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying them')
    
    args = parser.parse_args()
    
    renumber_apartments(building_id=args.building_id, dry_run=args.dry_run)

