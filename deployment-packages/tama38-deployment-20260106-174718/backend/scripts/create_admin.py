"""
Script to create initial admin user
Run from backend directory: python scripts/create_admin.py
Or via docker: docker-compose exec backend python scripts/create_admin.py
"""
import sys
import os

# Ensure we're in the backend directory context
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
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
            print(f"User ID: {admin.user_id}")
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
        print("=" * 50)
        print("Admin user created successfully!")
        print("=" * 50)
        print("Email: admin@tama38.local")
        print("Password: Admin123!@#")
        print(f"User ID: {admin_user.user_id}")
        print("=" * 50)
    except Exception as e:
        db.rollback()
        print(f"ERROR: Failed to create admin user: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()

