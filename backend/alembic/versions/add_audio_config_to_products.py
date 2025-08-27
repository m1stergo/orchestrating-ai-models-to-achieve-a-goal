"""Add audio_config column to products table

Revision ID: add_audio_config_to_products
Revises: add_user_settings_fields
Create Date: 2025-08-27 00:39:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_audio_config_to_products'
down_revision = 'add_user_settings_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Add audio_config column to products table
    op.add_column('products', sa.Column('audio_config', sa.JSON(), nullable=True))


def downgrade():
    # Remove audio_config column
    op.drop_column('products', 'audio_config')
