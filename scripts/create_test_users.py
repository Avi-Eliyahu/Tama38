"""
Script to create test users for each role
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        for user_data in test_users:
            # Check if user exists
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if existing:
                print(f"User {user_data['email']} already exists, skipping...")
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
        print(f"Created {created_count} test users")
        print("\nTest users:")
        for user_data in test_users:
            print(f"  {user_data['email']} / {user_data['password']} ({user_data['role']})")
    except Exception as e:
        db.rollback()
        print(f"Error creating test users: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()

