from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'patients',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('mrn', sa.String(length=64), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('sex', sa.String(length=32), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=32), nullable=True),
        sa.Column('address_line1', sa.String(length=255), nullable=True),
        sa.Column('address_line2', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_patients_mrn', 'patients', ['mrn'], unique=True)
    op.create_index('ix_patients_first_name', 'patients', ['first_name'])
    op.create_index('ix_patients_last_name', 'patients', ['last_name'])

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('actor_id', sa.String(length=128), nullable=True),
        sa.Column('actor_role', sa.String(length=64), nullable=True),
        sa.Column('action', sa.String(length=64), nullable=False),
        sa.Column('resource_type', sa.String(length=64), nullable=False),
        sa.Column('resource_id', sa.String(length=128), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=64), nullable=True),
        sa.Column('request_id', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_resource_type', 'audit_logs', ['resource_type'])
    op.create_index('ix_audit_logs_resource_id', 'audit_logs', ['resource_id'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])
    op.create_index('ix_audit_logs_request_id', 'audit_logs', ['request_id'])


def downgrade() -> None:
    op.drop_index('ix_audit_logs_request_id', table_name='audit_logs')
    op.drop_index('ix_audit_logs_created_at', table_name='audit_logs')
    op.drop_index('ix_audit_logs_resource_id', table_name='audit_logs')
    op.drop_index('ix_audit_logs_resource_type', table_name='audit_logs')
    op.drop_index('ix_audit_logs_action', table_name='audit_logs')
    op.drop_table('audit_logs')

    op.drop_index('ix_patients_last_name', table_name='patients')
    op.drop_index('ix_patients_first_name', table_name='patients')
    op.drop_index('ix_patients_mrn', table_name='patients')
    op.drop_table('patients')

