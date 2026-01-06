"""add_partially_signed_to_unit_status

Revision ID: c5cd1e4e58f7
Revises: 107585aa7109
Create Date: 2026-01-01 12:52:14.475502

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5cd1e4e58f7'
down_revision = '107585aa7109'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add PARTIALLY_SIGNED to unit_status enum
    op.execute("ALTER TYPE unit_status ADD VALUE IF NOT EXISTS 'PARTIALLY_SIGNED'")


def downgrade() -> None:
    # Note: PostgreSQL doesn't support removing enum values easily
    # This would require recreating the enum type, which is complex
    # For now, we'll leave PARTIALLY_SIGNED in the enum
    pass

