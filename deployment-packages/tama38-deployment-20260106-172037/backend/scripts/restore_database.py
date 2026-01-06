"""
Database Restore Script
Restores a PostgreSQL backup using pg_restore
"""
import sys
import os
import subprocess
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


def restore_backup(backup_file: str, target_db: str = None, clean: bool = False):
    """
    Restore a database backup using pg_restore
    
    Args:
        backup_file: Path to backup file (.sql or .dump)
        target_db: Target database name (default: from DATABASE_URL)
        clean: Drop existing objects before restoring
    """
    # Parse database URL
    db_config = parse_database_url(settings.DATABASE_URL)
    
    if target_db is None:
        target_db = db_config['database']
    
    backup_path = Path(backup_file)
    if not backup_path.exists():
        print(f"✗ Error: Backup file not found: {backup_file}")
        sys.exit(1)
    
    # Set PGPASSWORD environment variable
    env = os.environ.copy()
    if db_config['password']:
        env['PGPASSWORD'] = db_config['password']
    
    # Check if it's a custom format (.dump) or SQL format (.sql)
    is_custom_format = backup_path.suffix == '.dump' or backup_path.suffix == ''
    
    print("=" * 70)
    print("DATABASE RESTORE")
    print("=" * 70)
    print(f"Backup file: {backup_file}")
    print(f"Target database: {target_db}")
    print(f"Host: {db_config['host']}:{db_config['port']}")
    print(f"User: {db_config['user']}")
    if clean:
        print("⚠ WARNING: Will drop existing objects!")
    print("=" * 70)
    
    if is_custom_format:
        # Use pg_restore for custom format
        cmd = [
            'pg_restore',
            '-h', db_config['host'],
            '-p', str(db_config['port']),
            '-U', db_config['user'],
            '-d', target_db,
        ]
        
        if clean:
            cmd.append('--clean')
        
        cmd.append(str(backup_path))
    else:
        # Use psql for SQL format
        cmd = [
            'psql',
            '-h', db_config['host'],
            '-p', str(db_config['port']),
            '-U', db_config['user'],
            '-d', target_db,
            '-f', str(backup_path)
        ]
    
    try:
        print(f"\nRestoring backup...")
        result = subprocess.run(
            cmd,
            env=env,
            check=True
        )
        
        print(f"\n✓ Backup restored successfully to database: {target_db}")
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error restoring backup:")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"  {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        tool = 'pg_restore' if is_custom_format else 'psql'
        print(f"\n✗ Error: {tool} not found!")
        print("  Please install PostgreSQL client tools:")
        print("  - Windows: Download from https://www.postgresql.org/download/windows/")
        print("  - Linux: sudo apt-get install postgresql-client")
        print("  - macOS: brew install postgresql")
        sys.exit(1)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Restore TAMA38 database backup')
    parser.add_argument('backup_file', help='Path to backup file')
    parser.add_argument('--target-db', '-d', help='Target database name (default: from DATABASE_URL)')
    parser.add_argument('--clean', '-c', action='store_true', help='Drop existing objects before restoring')
    args = parser.parse_args()
    
    restore_backup(args.backup_file, args.target_db, args.clean)


if __name__ == "__main__":
    main()

