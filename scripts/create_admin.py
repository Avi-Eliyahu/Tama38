"""
Script to create initial admin user
Run from backend directory: python scripts/create_admin.py
Or from project root: docker-compose exec backend python scripts/create_admin.py
"""
import sys
import os

# Add backend directory to path (script is in scripts/ but needs app/ from backend/)
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
import uuid

def create_admin():
    """Create initial admin user"""
    db: Session = SessionLocal()
    try:
        # Check if admin already exists
        admin = db.query(User).filter(User.email == "admin@tama38.local").first()
        if admin:
            print("Admin user already exists")
            return
        
        # Create admin user
        admin_user = User(
            user_id=uuid.uuid4(),
            email="admin@tama38.local",
            hashed_password=get_password_hash("Admin123!@#"),
            full_name="System Administrator",
            role="SUPER_ADMIN",
            is_active=True,
            is_verified=True,
        )
        
        db.add(admin_user)
        db.commit()
        print("Admin user created successfully")
        print("Email: admin@tama38.local")
        print("Password: Admin123!@#")
    except Exception as e:
        db.rollback()
        print(f"Error creating admin user: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()

