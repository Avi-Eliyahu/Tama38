"""add_signed_document_id_and_task_id_to_document_signatures

Revision ID: 504e7e80f9d1
Revises: c5cd1e4e58f7
Create Date: 2026-01-03 21:40:39.366776

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '504e7e80f9d1'
down_revision = 'c5cd1e4e58f7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add signed_document_id column to document_signatures table
    op.add_column('document_signatures', 
        sa.Column('signed_document_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_signatures_signed_document',
        'document_signatures', 'documents',
        ['signed_document_id'], ['document_id']
    )
    
    # Add task_id column to document_signatures table
    op.add_column('document_signatures',
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_signatures_task',
        'document_signatures', 'tasks',
        ['task_id'], ['task_id']
    )


def downgrade() -> None:
    # Remove foreign keys first
    op.drop_constraint('fk_signatures_task', 'document_signatures', type_='foreignkey')
    op.drop_constraint('fk_signatures_signed_document', 'document_signatures', type_='foreignkey')
    
    # Remove columns
    op.drop_column('document_signatures', 'task_id')
    op.drop_column('document_signatures', 'signed_document_id')

