"""Add is_active column to admin table

Revision ID: add_is_active_admin
Revises: 341489a97fe0
Create Date: 2025-12-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_is_active_admin'
down_revision = '341489a97fe0'
branch_labels = None
depends_on = None


def upgrade():
    # Add is_active column to admin table with default True
    op.add_column('admin', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))


def downgrade():
    # Remove is_active column from admin table
    op.drop_column('admin', 'is_active')

