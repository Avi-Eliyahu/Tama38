# Apartment Renumbering Guide

## Overview

This guide explains how to renumber apartments sequentially (1, 2, 3...) per building, across floors. Apartments are numbered sequentially starting from floor 1:
- **Floor 1**: Apartments 1, 2, 3...
- **Floor 2**: Apartments continue from where floor 1 ended (e.g., 4, 5, 6...)
- **Floor 3**: Apartments continue from where floor 2 ended (e.g., 7, 8, 9...)
- And so on...

## Changes Made

### 1. UI Terminology Updated ✅
- Changed "Unit" to "Apartment" in English translations
- Changed "יחידה" to "דירה" in Hebrew translations
- Updated all UI components to display "Apartment" instead of "Unit"

### 2. Backend API Sorting ✅
- Updated `/api/v1/units` endpoint to sort units by apartment number (unit_number)
- Units are now returned in sequential order (1, 2, 3...)

### 3. Frontend Sorting ✅
- Updated `BuildingDetail` component to sort apartments by number
- Apartments are displayed in sequential order in the UI

### 4. Renumbering Script ✅
- Created `backend/scripts/renumber_apartments.py` to renumber existing apartments

## Running the Renumbering Script

### Dry Run (Preview Changes)

```bash
# Preview changes for all buildings
docker-compose exec backend python scripts/renumber_apartments.py --dry-run

# Preview changes for a specific building
docker-compose exec backend python scripts/renumber_apartments.py --building-id BUILDING_ID --dry-run
```

### Apply Changes

```bash
# Renumber all buildings
docker-compose exec backend python scripts/renumber_apartments.py

# Renumber a specific building
docker-compose exec backend python scripts/renumber_apartments.py --building-id BUILDING_ID
```

### Example Output

```
Processing building: Building A (abc123...)
  Found 15 apartments
  Will renumber 15 apartments:
    Apartment 101 -> 1 (Floor: 1, Unit ID: def456...)
    Apartment 102 -> 2 (Floor: 1, Unit ID: ghi789...)
    Apartment 201 -> 3 (Floor: 2, Unit ID: jkl012...)
    ...
  ✓ Successfully renumbered 15 apartments
```

## How It Works

1. **Floor-First Ordering**: The script orders apartments by `floor_number` first, then by current `unit_number` within each floor
2. **Sequential Numbering Across Floors**: Apartments are renumbered sequentially starting from 1, continuing across all floors:
   - Floor 1: 1, 2, 3...
   - Floor 2: continues from where Floor 1 ended (e.g., 4, 5, 6...)
   - Floor 3: continues from where Floor 2 ended (e.g., 7, 8, 9...)
3. **Full Identifier Update**: The `unit_full_identifier` field is updated to reflect the new numbering while preserving floor information (e.g., "2-4" for Floor 2, Apartment 4)

## Important Notes

- **Backup First**: Always backup your database before running the renumbering script
- **Dry Run**: Always use `--dry-run` first to preview changes
- **One Building at a Time**: For safety, consider renumbering one building at a time
- **No Data Loss**: The script only changes `unit_number` and `unit_full_identifier` fields
- **Relationships Preserved**: All relationships (owners, interactions, etc.) remain intact

## Verification

After renumbering, verify:
1. Apartments are numbered 1, 2, 3... sequentially per building
2. UI displays apartments in sequential order
3. All relationships (owners, documents) still work correctly
4. Floor numbers are preserved (only apartment numbers changed)

## Troubleshooting

If apartments are not displaying in order:
1. Clear browser cache
2. Verify backend API is returning sorted results
3. Check that `unit_number` values are numeric strings ("1", "2", "3" not "A1", "B2")

