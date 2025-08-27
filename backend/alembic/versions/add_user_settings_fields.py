"""Add new fields to user_settings table

Revision ID: add_user_settings_fields
Revises: add_product_fields
Create Date: 2025-08-26 04:13:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_user_settings_fields'
down_revision = 'add_product_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to user_settings table
    op.add_column('user_settings', sa.Column('generate_description_prompt', sa.Text(), nullable=True))
    op.add_column('user_settings', sa.Column('generate_promotional_audio_script_prompt', sa.Text(), nullable=True))
    op.add_column('user_settings', sa.Column('categories', sa.JSON(), nullable=True))


def downgrade():
    # Remove new columns
    op.drop_column('user_settings', 'categories')
    op.drop_column('user_settings', 'generate_promotional_audio_script_prompt')
    op.drop_column('user_settings', 'generate_description_prompt')
