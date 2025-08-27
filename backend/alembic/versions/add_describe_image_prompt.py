"""Add describe_image_prompt column to user_settings table

Revision ID: add_describe_image_prompt
Revises: add_audio_config_to_products
Create Date: 2025-08-27 03:32:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_describe_image_prompt'
down_revision = 'add_audio_config_to_products'
branch_labels = None
depends_on = None


def upgrade():
    # Add describe_image_prompt column to user_settings table
    op.add_column('user_settings', sa.Column('describe_image_prompt', sa.Text(), nullable=True))


def downgrade():
    # Remove describe_image_prompt column
    op.drop_column('user_settings', 'describe_image_prompt')
