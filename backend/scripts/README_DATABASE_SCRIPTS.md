# Database Backup, Restore, and Sample Database Scripts

This directory contains scripts for backing up, restoring, and creating sample databases.

## Scripts

### 1. `backup_database.py` - Database Backup

Creates a PostgreSQL backup of the current database using `pg_dump`.

**Usage:**

**Recommended (via Docker):**
```bash
# From project root directory
docker-compose exec backend python scripts/backup_database.py

# Specify output directory
docker-compose exec backend python scripts/backup_database.py --output-dir /app/backups

# Specify filename
docker-compose exec backend python scripts/backup_database.py --filename my_backup.sql
```

**Local Python (requires dependencies installed):**
```bash
# From backend directory
# First install dependencies:
pip install -r requirements.txt

# Then run:
python scripts/backup_database.py
```

**Output:**
- Creates a compressed backup file in `backend/backups/` directory (default)
- Filename format: `tama38_backup_YYYYMMDD_HHMMSS.sql`
- Format: Custom PostgreSQL format (compressed)

**Requirements:**
- PostgreSQL client tools (`pg_dump`) must be installed
- Database connection configured in `DATABASE_URL` environment variable

---

### 2. `restore_database.py` - Database Restore

Restores a PostgreSQL backup using `pg_restore` or `psql`.

**Usage:**

**Recommended (via Docker):**
```bash
# From project root directory
# Restore from backup file
docker-compose exec backend python scripts/restore_database.py backups/tama38_backup_20240101_120000.sql

# Restore to specific database
docker-compose exec backend python scripts/restore_database.py backups/my_backup.sql --target-db my_database

# Clean restore (drops existing objects first)
docker-compose exec backend python scripts/restore_database.py backups/my_backup.sql --clean
```

**Local Python (requires dependencies installed):**
```bash
# From backend directory
# First install dependencies:
pip install -r requirements.txt

# Then run:
python scripts/restore_database.py backups/my_backup.sql
```

**Options:**
- `backup_file` (required): Path to backup file
- `--target-db, -d`: Target database name (default: from DATABASE_URL)
- `--clean, -c`: Drop existing objects before restoring

**Requirements:**
- PostgreSQL client tools (`pg_restore` or `psql`) must be installed
- Database connection configured in `DATABASE_URL` environment variable

---

### 3. `create_hebrew_sample_db.py` - Hebrew Sample Database

Creates a sample Hebrew database with:
- **2 projects**
- **Project 1**: 4 buildings (16, 20, 24, 28 units respectively)
- **Project 2**: 2 buildings (18, 26 units respectively)
- **16-28 units per building**
- **1-3 owners per unit**
- All text fields translated to Hebrew (except emails and IDs)

**Usage:**

**Recommended (via Docker):**
```bash
# From project root directory
# Create default database (tama38_hebrew_sample)
docker-compose exec backend python scripts/create_hebrew_sample_db.py

# Specify database name
docker-compose exec backend python scripts/create_hebrew_sample_db.py --db-name my_hebrew_db
```

**Local Python (requires dependencies installed):**
```bash
# From backend directory
# First install dependencies:
pip install -r requirements.txt

# Then run:
python scripts/create_hebrew_sample_db.py
```

**What it does:**
1. Creates a new PostgreSQL database
2. Runs Alembic migrations to create schema
3. Creates admin user (Hebrew name)
4. Creates 2 projects with Hebrew names and descriptions
5. Creates buildings with Hebrew names and addresses
6. Creates units (16-28 per building)
7. Creates owners (1-3 per unit) with Hebrew names
8. Translates all text fields to Hebrew using Google Translate API

**Requirements:**
- PostgreSQL client tools
- Internet connection for translation API
- `deep-translator` package (installed via requirements.txt)

**Translation:**
- Uses Google Translate API (with MyMemory fallback)
- Caches translations for performance
- Keeps emails and IDs in original format

**After creation:**
To use the Hebrew database, update your `DATABASE_URL`:
```bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tama38_hebrew_sample
```

Or update `.env` file:
```
DATABASE_URL=postgresql://postgres:postgres@database:5432/tama38_hebrew_sample
```

---

## Quick Start Examples

### Backup current database:
```bash
# Via Docker (recommended)
docker-compose exec backend python scripts/backup_database.py

# Or locally (requires pip install -r requirements.txt first)
cd backend
python scripts/backup_database.py
```

### Restore from backup:
```bash
# Via Docker (recommended)
docker-compose exec backend python scripts/restore_database.py backups/tama38_backup_20240101_120000.sql

# Or locally (requires pip install -r requirements.txt first)
cd backend
python scripts/restore_database.py backups/tama38_backup_20240101_120000.sql
```

### Create Hebrew sample database:
```bash
# Via Docker (recommended)
docker-compose exec backend python scripts/create_hebrew_sample_db.py

# Or locally (requires pip install -r requirements.txt first)
cd backend
python scripts/create_hebrew_sample_db.py
```

### Create Hebrew database and backup it:
```bash
# Via Docker (recommended)
# Create Hebrew database
docker-compose exec backend python scripts/create_hebrew_sample_db.py --db-name tama38_hebrew_sample

# Backup the Hebrew database (update DATABASE_URL in docker-compose.yml or use --target-db)
docker-compose exec backend python scripts/backup_database.py --filename hebrew_sample_backup.sql
```

---

## CLI Restore Instructions (Manual)

If you prefer to restore manually using PostgreSQL CLI tools:

### For Custom Format (.dump) backups:
```bash
pg_restore -h localhost -p 5432 -U postgres -d target_database_name backup_file.dump
```

### For SQL Format (.sql) backups:
```bash
psql -h localhost -p 5432 -U postgres -d target_database_name -f backup_file.sql
```

### With password prompt:
```bash
PGPASSWORD=your_password pg_restore -h localhost -p 5432 -U postgres -d target_database_name backup_file.dump
```

### Clean restore (drop existing objects):
```bash
pg_restore --clean -h localhost -p 5432 -U postgres -d target_database_name backup_file.dump
```

---

## Notes

- All scripts use the `DATABASE_URL` from environment variables or `.env` file
- Backup files are stored in `backend/backups/` directory by default
- Hebrew sample database uses translation API - ensure internet connection
- Translation may take time for large datasets (caching helps)
- Email addresses remain in Latin characters for compatibility
- IDs (UUIDs, codes) remain unchanged

