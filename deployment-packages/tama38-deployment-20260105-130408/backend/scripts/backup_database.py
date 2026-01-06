"""
Database Backup Script
Creates a PostgreSQL backup using pg_dump
"""
import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings


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


def create_backup(backup_dir: str = None, filename: str = None):
    """
    Create a database backup using pg_dump
    
    Args:
        backup_dir: Directory to save backup (default: ./backups)
        filename: Backup filename (default: tama38_backup_YYYYMMDD_HHMMSS.sql)
    
    Returns:
        Path to the created backup file
    """
    # Parse database URL
    db_config = parse_database_url(settings.DATABASE_URL)
    
    # Set backup directory
    if backup_dir is None:
        backup_dir = os.path.join(os.path.dirname(__file__), '..', 'backups')
    
    backup_path = Path(backup_dir)
    backup_path.mkdir(parents=True, exist_ok=True)
    
    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'tama38_backup_{timestamp}.sql'
    
    backup_file = backup_path / filename
    
    # Set PGPASSWORD environment variable
    env = os.environ.copy()
    if db_config['password']:
        env['PGPASSWORD'] = db_config['password']
    
    # Build pg_dump command
    cmd = [
        'pg_dump',
        '-h', db_config['host'],
        '-p', str(db_config['port']),
        '-U', db_config['user'],
        '-d', db_config['database'],
        '-F', 'c',  # Custom format (compressed)
        '-f', str(backup_file)
    ]
    
    print("=" * 70)
    print("DATABASE BACKUP")
    print("=" * 70)
    print(f"Database: {db_config['database']}")
    print(f"Host: {db_config['host']}:{db_config['port']}")
    print(f"User: {db_config['user']}")
    print(f"Backup file: {backup_file}")
    print("=" * 70)
    
    try:
        # Run pg_dump
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        
        file_size = backup_file.stat().st_size
        print(f"\n✓ Backup created successfully!")
        print(f"  File: {backup_file}")
        print(f"  Size: {file_size / 1024 / 1024:.2f} MB")
        print("\nTo restore this backup, run:")
        print(f"  python scripts/restore_database.py {backup_file}")
        print("\nOr use pg_restore directly:")
        print(f"  pg_restore -h {db_config['host']} -p {db_config['port']} -U {db_config['user']} -d <target_db> {backup_file}")
        
        return str(backup_file)
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error creating backup:")
        print(f"  {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("\n✗ Error: pg_dump not found!")
        print("  Please install PostgreSQL client tools:")
        print("  - Windows: Download from https://www.postgresql.org/download/windows/")
        print("  - Linux: sudo apt-get install postgresql-client")
        print("  - macOS: brew install postgresql")
        sys.exit(1)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Backup TAMA38 database')
    parser.add_argument('--output-dir', '-o', help='Backup output directory', default=None)
    parser.add_argument('--filename', '-f', help='Backup filename', default=None)
    args = parser.parse_args()
    
    create_backup(args.output_dir, args.filename)


if __name__ == "__main__":
    main()

