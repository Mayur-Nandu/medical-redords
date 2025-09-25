from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = '0002_add_ssn_encrypted'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('patients', sa.Column('ssn_encrypted', sa.LargeBinary(), nullable=True))


def downgrade() -> None:
    op.drop_column('patients', 'ssn_encrypted')

