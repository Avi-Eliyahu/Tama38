"""
Add PARTIALLY_SIGNED to unit_status enum in database
"""
import sys
import os
from sqlalchemy import text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import engine

# Connect to database and add enum value
with engine.connect() as conn:
    try:
        # Check if value already exists
        result = conn.execute(text("SELECT unnest(enum_range(NULL::unit_status))"))
        existing_values = [row[0] for row in result]
        
        if 'PARTIALLY_SIGNED' in existing_values:
            print("✓ PARTIALLY_SIGNED already exists in unit_status enum")
        else:
            # Add the value
            conn.execute(text("ALTER TYPE unit_status ADD VALUE 'PARTIALLY_SIGNED'"))
            conn.commit()
            print("✓ Added PARTIALLY_SIGNED to unit_status enum")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()

