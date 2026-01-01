"""
Script to create test users for each role
Run from backend directory: python scripts/create_test_users.py
Or via docker: docker-compose exec backend python scripts/create_test_users.py
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

def create_test_users():
    """Create test users for each role"""
    db: Session = SessionLocal()
    try:
        test_users = [
            {
                "email": "super_admin@test.com",
                "password": "Test123!@#",
                "full_name": "Super Admin User",
                "role": "SUPER_ADMIN",
            },
            {
                "email": "project_manager@test.com",
                "password": "Test123!@#",
                "full_name": "Project Manager User",
                "role": "PROJECT_MANAGER",
            },
            {
                "email": "agent1@test.com",
                "password": "Test123!@#",
                "full_name": "Agent One",
                "role": "AGENT",
            },
            {
                "email": "agent2@test.com",
                "password": "Test123!@#",
                "full_name": "Agent Two",
                "role": "AGENT",
            },
            {
                "email": "tenant1@test.com",
                "password": "Test123!@#",
                "full_name": "Tenant One",
                "role": "TENANT",
            },
        ]
        
        created_count = 0
        skipped_count = 0
        
        for user_data in test_users:
            # Check if user exists
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if existing:
                print(f"⏭️  User {user_data['email']} already exists, skipping...")
                skipped_count += 1
                continue
            
            user = User(
                user_id=uuid.uuid4(),
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"],
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            created_count += 1
        
        db.commit()
        
        print("=" * 50)
        print(f"Created {created_count} test users")
        if skipped_count > 0:
            print(f"Skipped {skipped_count} existing users")
        print("=" * 50)
        print("\nTest users:")
        for user_data in test_users:
            print(f"  {user_data['email']} / {user_data['password']} ({user_data['role']})")
        print("=" * 50)
    except Exception as e:
        db.rollback()
        print(f"ERROR: Failed to create test users: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()

