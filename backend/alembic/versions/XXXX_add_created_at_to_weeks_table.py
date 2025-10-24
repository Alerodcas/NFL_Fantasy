"""add created_at to weeks table

Revision ID: XXXX
Revises: YYYY
Create Date: 2024-XX-XX XX:XX:XX.XXXXXX

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'XXXX'
down_revision = 'YYYY'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('weeks', sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()))

def downgrade():
    op.drop_column('weeks', 'created_at')