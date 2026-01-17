"""add_indexes_for_multi_unit_ownership

Revision ID: 7a8b9c0d1e2f
Revises: 504e7e80f9d1
Create Date: 2026-01-04 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a8b9c0d1e2f'
down_revision = '504e7e80f9d1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add indexes on hash fields for efficient multi-unit ownership lookups
    # These indexes enable fast queries to find all units owned by the same person
    # Using partial indexes (WHERE clause) to only index non-null values
    op.execute("CREATE INDEX IF NOT EXISTS idx_owners_id_hash ON owners (id_number_hash) WHERE id_number_hash IS NOT NULL")
    op.execute("CREATE INDEX IF NOT EXISTS idx_owners_phone_hash ON owners (phone_hash) WHERE phone_hash IS NOT NULL")


def downgrade() -> None:
    # Remove indexes
    op.execute("DROP INDEX IF EXISTS idx_owners_phone_hash")
    op.execute("DROP INDEX IF EXISTS idx_owners_id_hash")

