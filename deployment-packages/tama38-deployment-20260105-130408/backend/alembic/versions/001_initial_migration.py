"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2025-12-30 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Helper function to create enum column - SQLAlchemy will create the type automatically
def enum_column(column_name, enum_name, enum_values, **kwargs):
    """Create an enum column - SQLAlchemy will create the enum type if it doesn't exist"""
    return sa.Column(
        column_name,
        postgresql.ENUM(*enum_values, name=enum_name, create_type=True),
        **kwargs
    )

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enum types will be created automatically by SQLAlchemy when tables are created

    # Create users table
    op.create_table(
        'users',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        enum_column('role', 'user_role', ['SUPER_ADMIN', 'PROJECT_MANAGER', 'AGENT', 'TENANT'], nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('phone', sa.String(20)),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('last_login', sa.DateTime()),
        sa.Column('is_deleted', sa.Boolean(), default=False),
    )
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_role', 'users', ['role'])

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('project_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_name', sa.String(255), nullable=False, unique=True),
        sa.Column('project_code', sa.String(50), nullable=False, unique=True),
        enum_column('project_type', 'project_type', ['TAMA38_1', 'TAMA38_2', 'PINUI_BINUI'], nullable=False),
        sa.Column('location_city', sa.String(100)),
        sa.Column('location_address', sa.Text()),
        sa.Column('location_coordinates', sa.String(100)),
        sa.Column('description', sa.Text()),
        enum_column('project_stage', 'project_stage', ['PLANNING', 'ACTIVE', 'APPROVAL', 'COMPLETED', 'ARCHIVED'], default='PLANNING'),
        sa.Column('budget_total_ils', sa.Numeric(15, 2)),
        sa.Column('budget_consumed_ils', sa.Numeric(15, 2), default=0),
        sa.Column('required_majority_percent', sa.Numeric(5, 2), nullable=False),
        enum_column('majority_calc_type', 'majority_calc_type', ['HEADCOUNT', 'AREA', 'WEIGHTED', 'CUSTOM'], nullable=False),
        sa.Column('critical_threshold_percent', sa.Numeric(5, 2), nullable=False),
        sa.Column('launch_date', sa.Date()),
        sa.Column('estimated_completion_date', sa.Date()),
        sa.Column('actual_completion_date', sa.Date()),
        sa.Column('business_sponsor', sa.String(255)),
        sa.Column('project_manager_id', postgresql.UUID(as_uuid=True)),
        sa.Column('is_template', sa.Boolean(), default=False),
        sa.Column('custom_config', postgresql.JSON),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.ForeignKeyConstraint(['project_manager_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.user_id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.user_id']),
    )
    op.create_index('idx_projects_city', 'projects', ['location_city'])
    op.create_index('idx_projects_status', 'projects', ['project_stage'])
    op.create_index('idx_projects_created_by', 'projects', ['created_by'])

    # Create buildings table
    op.create_table(
        'buildings',
        sa.Column('building_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('building_name', sa.String(255), nullable=False),
        sa.Column('building_code', sa.String(50)),
        sa.Column('address', sa.Text()),
        sa.Column('coordinates', sa.String(100)),
        sa.Column('floor_count', sa.Integer()),
        sa.Column('total_units', sa.Integer()),
        sa.Column('total_area_sqm', sa.Numeric(10, 2)),
        sa.Column('construction_year', sa.Integer()),
        sa.Column('structure_type', sa.Enum('CONCRETE', 'MASONRY', 'MIXED', 'OTHER', name='structure_type')),
        sa.Column('seismic_rating', sa.Enum('UNSAFE', 'REQUIRES_REINFORCEMENT', 'REINFORCED', 'MODERN', name='seismic_rating')),
        sa.Column('current_status', sa.Enum('INITIAL', 'NEGOTIATING', 'APPROVED', 'RENOVATION_PLANNING', 'RENOVATION_ONGOING', 'COMPLETED', name='building_status'), default='INITIAL'),
        sa.Column('signature_percentage', sa.Numeric(5, 2), default=0),
        sa.Column('signature_percentage_by_area', sa.Numeric(5, 2), default=0),
        sa.Column('signature_percentage_by_cost', sa.Numeric(5, 2), default=0),
        enum_column('traffic_light_status', 'traffic_light', ['GREEN', 'YELLOW', 'RED', 'GRAY'], default='GRAY'),
        sa.Column('units_signed', sa.Integer(), default=0),
        sa.Column('units_partially_signed', sa.Integer(), default=0),
        sa.Column('units_not_signed', sa.Integer(), default=0),
        sa.Column('units_refused', sa.Integer(), default=0),
        sa.Column('estimated_bonus_ils', sa.Numeric(15, 2)),
        sa.Column('actual_bonus_ils', sa.Numeric(15, 2)),
        sa.Column('assigned_agent_id', postgresql.UUID(as_uuid=True)),
        sa.Column('secondary_agent_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True))),
        sa.Column('inspector_id', postgresql.UUID(as_uuid=True)),
        sa.Column('difficulty_score', sa.Integer()),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id']),
        sa.ForeignKeyConstraint(['assigned_agent_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['inspector_id'], ['users.user_id']),
    )
    op.create_index('idx_buildings_project_id', 'buildings', ['project_id'])
    op.create_index('idx_buildings_status', 'buildings', ['current_status'])
    op.create_index('idx_buildings_signature_pct', 'buildings', ['signature_percentage'])
    op.create_index('idx_buildings_traffic_light', 'buildings', ['traffic_light_status'])

    # Create units table
    op.create_table(
        'units',
        sa.Column('unit_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('building_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('floor_number', sa.SmallInteger()),
        sa.Column('unit_number', sa.String(10), nullable=False),
        sa.Column('unit_code', sa.String(50)),
        sa.Column('unit_full_identifier', sa.String(50)),
        sa.Column('area_sqm', sa.Numeric(8, 2)),
        sa.Column('room_count', sa.SmallInteger()),
        sa.Column('estimated_value_ils', sa.Numeric(12, 2)),
        sa.Column('estimated_renovation_cost_ils', sa.Numeric(12, 2)),
        enum_column('unit_status', 'unit_status', ['NOT_CONTACTED', 'NEGOTIATING', 'AGREED_TO_SIGN', 'SIGNED', 'FINALIZED', 'REFUSED', 'INACTIVE'], default='NOT_CONTACTED'),
        sa.Column('total_owners', sa.Integer(), default=0),
        sa.Column('owners_signed', sa.Integer(), default=0),
        sa.Column('signature_percentage', sa.Numeric(5, 2), default=0),
        sa.Column('is_co_owned', sa.Boolean(), default=False),
        sa.Column('is_rented', sa.Boolean(), default=False),
        sa.Column('tenant_name', sa.String(255)),
        sa.Column('first_contact_date', sa.Date()),
        sa.Column('last_contact_date', sa.Date()),
        sa.Column('last_activity_timestamp', sa.DateTime()),
        sa.Column('days_since_contact', sa.Integer()),
        sa.Column('primary_contract_id', postgresql.UUID(as_uuid=True)),
        sa.Column('renovation_plan_document_id', postgresql.UUID(as_uuid=True)),
        sa.Column('complexity_notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.ForeignKeyConstraint(['building_id'], ['buildings.building_id']),
    )
    op.create_index('idx_units_building_id', 'units', ['building_id'])
    op.create_index('idx_units_status', 'units', ['unit_status'])

    # Create documents table (without foreign keys initially - will add after owners)
    op.create_table(
        'documents',
        sa.Column('document_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True)),
        sa.Column('building_id', postgresql.UUID(as_uuid=True)),
        sa.Column('project_id', postgresql.UUID(as_uuid=True)),
        enum_column('document_type', 'document_type', ['CONTRACT', 'ID_CARD', 'SIGNATURE', 'RENOVATION_PLAN', 'PERMIT', 'OTHER'], nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_size_bytes', sa.Integer()),
        sa.Column('mime_type', sa.String(100)),
        sa.Column('description', sa.Text()),
        sa.Column('version', sa.Integer(), default=1),
        sa.Column('is_current_version', sa.Boolean(), default=True),
        sa.Column('uploaded_by_user_id', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.ForeignKeyConstraint(['building_id'], ['buildings.building_id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id']),
        sa.ForeignKeyConstraint(['uploaded_by_user_id'], ['users.user_id']),
    )
    op.create_index('idx_documents_type', 'documents', ['document_type'])

    # Create owners table (before document_signatures)
    op.create_table(
        'owners',
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('unit_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('id_number_encrypted', postgresql.BYTEA()),
        sa.Column('id_number_hash', postgresql.BYTEA()),
        enum_column('id_type', 'id_type', ['ISRAELI_ID', 'PASSPORT', 'BUSINESS_ID', 'OTHER']),
        sa.Column('date_of_birth', sa.Date()),
        sa.Column('phone_encrypted', postgresql.BYTEA()),
        sa.Column('phone_hash', postgresql.BYTEA()),
        sa.Column('phone_for_contact', sa.String(20)),
        sa.Column('email', sa.String(255)),
        enum_column('preferred_contact_method', 'contact_method', ['PHONE', 'WHATSAPP', 'EMAIL', 'IN_PERSON', 'NONE']),
        enum_column('preferred_language', 'language', ['HEBREW', 'ARABIC', 'RUSSIAN', 'ENGLISH', 'OTHER']),
        sa.Column('accessibility_needs', sa.Text()),
        sa.Column('is_elderly', sa.Boolean(), default=False),
        sa.Column('is_vulnerable', sa.Boolean(), default=False),
        sa.Column('ownership_share_percent', sa.Numeric(5, 2), nullable=False),
        enum_column('ownership_type', 'ownership_type', ['SOLE_OWNER', 'CO_OWNER_JOINT', 'CO_OWNER_SEPARATE', 'TENANT_REPRESENTATIVE']),
        sa.Column('is_primary_contact', sa.Boolean(), default=False),
        enum_column('owner_status', 'owner_status', ['NOT_CONTACTED', 'PENDING_SIGNATURE', 'NEGOTIATING', 'AGREED_TO_SIGN', 'WAIT_FOR_SIGN', 'SIGNED', 'REFUSED', 'DECEASED', 'INCAPACITATED'], default='NOT_CONTACTED'),
        enum_column('refusal_reason', 'refusal_reason', ['NOT_INTERESTED', 'PRICE_OBJECTION', 'LEGAL_DISPUTE', 'NO_CONSENSUS_WITH_CO_OWNER', 'OTHER']),
        sa.Column('refusal_reason_detail', sa.Text()),
        sa.Column('signature_date', sa.Date()),
        sa.Column('signature_session_id', postgresql.UUID(as_uuid=True)),
        sa.Column('assigned_agent_id', postgresql.UUID(as_uuid=True)),
        sa.Column('is_current_owner', sa.Boolean(), default=True),
        sa.Column('ownership_start_date', sa.Date()),
        sa.Column('ownership_end_date', sa.Date()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.ForeignKeyConstraint(['unit_id'], ['units.unit_id']),
        sa.ForeignKeyConstraint(['assigned_agent_id'], ['users.user_id']),
    )
    op.create_index('idx_owners_unit_id', 'owners', ['unit_id'])
    op.create_index('idx_owners_status', 'owners', ['owner_status'])
    op.create_index('idx_owners_agent', 'owners', ['assigned_agent_id'])

    # Create document_signatures table (after owners and documents)
    op.create_table(
        'document_signatures',
        sa.Column('signature_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        enum_column('signature_status', 'signature_status', ['WAIT_FOR_SIGN', 'SIGNED_PENDING_APPROVAL', 'FINALIZED', 'REJECTED'], nullable=False, default='WAIT_FOR_SIGN'),
        sa.Column('signing_token', sa.String(255), unique=True),
        sa.Column('signature_data', sa.Text()),
        sa.Column('signed_at', sa.DateTime()),
        sa.Column('approved_by_user_id', postgresql.UUID(as_uuid=True)),
        sa.Column('approved_at', sa.DateTime()),
        sa.Column('approval_reason', sa.Text()),
        sa.Column('rejected_by_user_id', postgresql.UUID(as_uuid=True)),
        sa.Column('rejected_at', sa.DateTime()),
        sa.Column('rejection_reason', sa.Text()),
        sa.Column('is_manual_override', sa.Boolean(), default=False),
        sa.Column('manual_override_reason', sa.Text()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['document_id'], ['documents.document_id']),
        sa.ForeignKeyConstraint(['owner_id'], ['owners.owner_id']),
        sa.ForeignKeyConstraint(['approved_by_user_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['rejected_by_user_id'], ['users.user_id']),
    )
    op.create_index('idx_signatures_owner_id', 'document_signatures', ['owner_id'])
    op.create_index('idx_signatures_status', 'document_signatures', ['signature_status'])
    op.create_index('idx_signatures_token', 'document_signatures', ['signing_token'])
    
    # Add foreign key constraint for owners.signature_session_id (after document_signatures exists)
    op.create_foreign_key(
        'fk_owners_signature_session',
        'owners', 'document_signatures',
        ['signature_session_id'], ['signature_id']
    )
    
    # Add foreign key for documents.owner_id (after owners exists)
    op.create_foreign_key(
        'fk_documents_owner',
        'documents', 'owners',
        ['owner_id'], ['owner_id']
    )
    op.create_index('idx_documents_owner_id', 'documents', ['owner_id'])
    
    # Add foreign key for documents.primary_contract_id and renovation_plan_document_id
    op.create_foreign_key(
        'fk_units_primary_contract',
        'units', 'documents',
        ['primary_contract_id'], ['document_id']
    )
    op.create_foreign_key(
        'fk_units_renovation_plan',
        'units', 'documents',
        ['renovation_plan_document_id'], ['document_id']
    )

    # Create interactions_log table
    op.create_table(
        'interactions_log',
        sa.Column('log_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        enum_column('interaction_type', 'interaction_type', ['PHONE_CALL', 'IN_PERSON_MEETING', 'WHATSAPP', 'EMAIL', 'SMS', 'VIDEO_CALL', 'SCHEDULED_MEETING'], nullable=False),
        sa.Column('interaction_date', sa.Date(), nullable=False),
        sa.Column('interaction_timestamp', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('duration_minutes', sa.Integer()),
        enum_column('outcome', 'outcome', ['POSITIVE', 'NEUTRAL', 'NEGATIVE', 'NOT_AVAILABLE', 'DECLINED', 'AGREED_TO_MEET', 'AGREED_TO_SIGN']),
        sa.Column('call_summary', sa.Text(), nullable=False),
        sa.Column('key_objection', sa.String(255)),
        sa.Column('next_action', sa.String(500)),
        sa.Column('next_follow_up_date', sa.Date()),
        enum_column('follow_up_type', 'follow_up_type', ['REMINDER_CALL', 'MEETING', 'SEND_DOCUMENT', 'FOLLOW_WITH_MANAGER']),
        enum_column('sentiment', 'sentiment', ['VERY_POSITIVE', 'POSITIVE', 'NEUTRAL', 'NEGATIVE', 'VERY_NEGATIVE']),
        sa.Column('is_escalated', sa.Boolean(), default=False),
        sa.Column('escalation_reason', sa.Text()),
        sa.Column('attempted', sa.Boolean(), default=True),
        enum_column('contact_method_used', 'contact_method', ['PHONE', 'WHATSAPP', 'EMAIL', 'IN_PERSON']),
        enum_column('source', 'source', ['MOBILE_APP', 'WEB_APP', 'MANUAL_ENTRY', 'CRM_INTEGRATION'], default='WEB_APP'),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['owners.owner_id']),
        sa.ForeignKeyConstraint(['agent_id'], ['users.user_id']),
    )
    op.create_index('idx_interactions_owner_id', 'interactions_log', ['owner_id'])
    op.create_index('idx_interactions_agent_id', 'interactions_log', ['agent_id'])
    op.create_index('idx_interactions_date', 'interactions_log', ['interaction_date'])
    op.create_index('idx_interactions_outcome', 'interactions_log', ['outcome'])

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('task_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('building_id', postgresql.UUID(as_uuid=True)),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True)),
        enum_column('task_type', 'task_type', ['FOLLOW_UP_CALL', 'SCHEDULE_MEETING', 'SEND_DOCUMENT', 'MANAGER_REVIEW', 'SITE_VISIT', 'HANDLE_OBJECTION'], nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('assigned_to_agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('due_date', sa.Date()),
        sa.Column('due_time', sa.Time()),
        enum_column('status', 'task_status', ['NOT_STARTED', 'IN_PROGRESS', 'BLOCKED', 'COMPLETED', 'OVERDUE', 'CANCELLED'], default='NOT_STARTED'),
        enum_column('priority', 'priority', ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'], default='MEDIUM'),
        sa.Column('estimated_hours', sa.Numeric(4, 2)),
        sa.Column('actual_hours', sa.Numeric(4, 2)),
        sa.Column('dependencies', postgresql.ARRAY(postgresql.UUID(as_uuid=True))),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('notes', sa.Text()),
        sa.ForeignKeyConstraint(['building_id'], ['buildings.building_id']),
        sa.ForeignKeyConstraint(['owner_id'], ['owners.owner_id']),
        sa.ForeignKeyConstraint(['assigned_to_agent_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['assigned_by_user_id'], ['users.user_id']),
    )
    op.create_index('idx_tasks_assigned_to', 'tasks', ['assigned_to_agent_id'])
    op.create_index('idx_tasks_status', 'tasks', ['status'])
    op.create_index('idx_tasks_due_date', 'tasks', ['due_date'])

    # Create wizard_drafts table
    op.create_table(
        'wizard_drafts',
        sa.Column('draft_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('step_data', postgresql.JSON),
        sa.Column('current_step', sa.Integer(), default=1),
        sa.Column('expires_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('is_completed', sa.Boolean(), default=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
    )
    op.create_index('idx_wizard_drafts_user_id', 'wizard_drafts', ['user_id'])
    op.create_index('idx_wizard_drafts_expires', 'wizard_drafts', ['expires_at'])

    # Create audit_log_extended table
    op.create_table(
        'audit_log_extended',
        sa.Column('audit_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('table_name', sa.String(100), nullable=False),
        sa.Column('record_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('old_values', postgresql.JSON),
        sa.Column('new_values', postgresql.JSON),
        sa.Column('changed_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('changed_at', sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column('reason_text', sa.Text()),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('request_id', sa.String(255)),
        sa.ForeignKeyConstraint(['changed_by_user_id'], ['users.user_id']),
    )
    op.create_index('idx_audit_table_record', 'audit_log_extended', ['table_name', 'record_id'])
    op.create_index('idx_audit_user', 'audit_log_extended', ['changed_by_user_id'])
    op.create_index('idx_audit_date', 'audit_log_extended', ['changed_at'])
    op.create_index('idx_audit_request_id', 'audit_log_extended', ['request_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('audit_log_extended')
    op.drop_table('wizard_drafts')
    op.drop_table('tasks')
    op.drop_table('interactions_log')
    op.drop_table('document_signatures')
    op.drop_table('owners')
    op.drop_table('documents')
    op.drop_table('units')
    op.drop_table('buildings')
    op.drop_table('projects')
    op.drop_table('users')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS priority")
    op.execute("DROP TYPE IF EXISTS task_status")
    op.execute("DROP TYPE IF EXISTS task_type")
    op.execute("DROP TYPE IF EXISTS signature_status")
    op.execute("DROP TYPE IF EXISTS document_type")
    op.execute("DROP TYPE IF EXISTS source")
    op.execute("DROP TYPE IF EXISTS sentiment")
    op.execute("DROP TYPE IF EXISTS follow_up_type")
    op.execute("DROP TYPE IF EXISTS outcome")
    op.execute("DROP TYPE IF EXISTS interaction_type")
    op.execute("DROP TYPE IF EXISTS refusal_reason")
    op.execute("DROP TYPE IF EXISTS owner_status")
    op.execute("DROP TYPE IF EXISTS ownership_type")
    op.execute("DROP TYPE IF EXISTS language")
    op.execute("DROP TYPE IF EXISTS contact_method")
    op.execute("DROP TYPE IF EXISTS id_type")
    op.execute("DROP TYPE IF EXISTS unit_status")
    op.execute("DROP TYPE IF EXISTS traffic_light")
    op.execute("DROP TYPE IF EXISTS building_status")
    op.execute("DROP TYPE IF EXISTS seismic_rating")
    op.execute("DROP TYPE IF EXISTS structure_type")
    op.execute("DROP TYPE IF EXISTS user_role")
    op.execute("DROP TYPE IF EXISTS majority_calc_type")
    op.execute("DROP TYPE IF EXISTS project_stage")
    op.execute("DROP TYPE IF EXISTS project_type")

