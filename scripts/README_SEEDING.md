# Database Seeding Script

This script populates the TAMA38 database with realistic test data for development and testing purposes.

## What It Creates

The seeding script creates:

- **2 Projects**:
  - Ramat Gan Urban Renewal - Phase 1 (TAMA38_1)
  - Tel Aviv Center Renovation (TAMA38_2)

- **6 Buildings** (distributed across projects):
  - Project 1: Bialik Tower A, Bialik Tower B
  - Project 2: Rothschild Heights, Rothschild Gardens, Rothschild Plaza, Rothschild View

- **108 Units** (distributed across all buildings)

- **31 Owners** with:
  - Israeli names and contact information
  - Various ownership statuses (NOT_CONTACTED, NEGOTIATING, AGREED_TO_SIGN, SIGNED, WAIT_FOR_SIGN, REFUSED)
  - Different ownership shares (including co-ownership examples)
  - Assigned to different agents

- **4 Agents**:
  - Rina Cohen (rina.cohen@tama38.local)
  - Amir Levi (amir.levi@tama38.local)
  - Tamar Mizrahi (tamar.mizrahi@tama38.local)
  - Oren Avraham (oren.avraham@tama38.local)

- **111+ Interaction Logs** (2-5 interactions per owner)

## How to Run

### Using Docker Compose (Recommended)

```bash
# Copy script to container and run
docker cp scripts/seed_database.py tama38_backend:/app/seed_database.py
docker-compose exec backend python /app/seed_database.py
```

### Direct Python (if running locally)

```bash
cd backend
python ../scripts/seed_database.py
```

## Login Credentials

After seeding, you can login with:

- **Admin**: `admin@tama38.local` / `Admin123!@#`
- **Agent 1**: `rina.cohen@tama38.local` / `Agent123!@#`
- **Agent 2**: `amir.levi@tama38.local` / `Agent123!@#`
- **Agent 3**: `tamar.mizrahi@tama38.local` / `Agent123!@#`
- **Agent 4**: `oren.avraham@tama38.local` / `Agent123!@#`

## Data Characteristics

### Projects
- Mix of TAMA38_1 and TAMA38_2 project types
- Different calculation types (HEADCOUNT, AREA)
- Active project stage
- Realistic locations in Ramat Gan and Tel Aviv

### Buildings
- Various statuses: INITIAL, NEGOTIATING, APPROVED, RENOVATION_PLANNING
- Traffic light statuses: GREEN, YELLOW, RED, GRAY
- Different structure types: CONCRETE, MASONRY, MIXED
- Signature percentages ranging from 20-85%

### Owners
- Realistic Israeli names
- Various contact methods (PHONE, WHATSAPP, EMAIL)
- Multiple languages (HEBREW, ENGLISH, RUSSIAN)
- Different ownership statuses for testing workflows
- Some co-ownership examples

### Interactions
- Mix of interaction types (PHONE_CALL, WHATSAPP, IN_PERSON_MEETING, EMAIL, SMS)
- Various outcomes and sentiments
- Spread across the last 90 days
- Assigned to different agents

## Notes

- The script uses realistic but fictional data
- All owners have Israeli ID numbers (for testing purposes)
- Phone numbers follow Israeli format (050-XXXXXXX)
- The script is idempotent - you can run it multiple times, but it will create duplicate data
- To reset the database, drop and recreate it, then run migrations and this script

## Customization

You can modify the data in `scripts/seed_database.py`:
- `PROJECTS_DATA`: Project and building definitions
- `OWNERS_DATA`: Owner information
- `AGENTS_DATA`: Agent information
- Adjust ranges and distributions in the creation functions

