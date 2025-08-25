"""Add new fields to products table

Revision ID: add_product_fields
Revises: 
Create Date: 2025-08-21 23:57:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_product_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to products table (nullable first)
    op.add_column('products', sa.Column('sku', sa.String(), nullable=True))
    op.add_column('products', sa.Column('keywords', sa.JSON(), nullable=True))
    op.add_column('products', sa.Column('category', sa.String(), nullable=True))
    op.add_column('products', sa.Column('audio_description', sa.Text(), nullable=True))
    
    # Update existing records with default SKU values
    op.execute("UPDATE products SET sku = 'SKU-' || id::text WHERE sku IS NULL")
    
    # Now make sku NOT NULL
    op.alter_column('products', 'sku', nullable=False)
    
    # Change description column type to Text
    op.alter_column('products', 'description', type_=sa.Text())
    
    # Add unique constraint and index on sku
    op.create_unique_constraint('uq_products_sku', 'products', ['sku'])
    op.create_index('ix_products_sku', 'products', ['sku'])


def downgrade():
    # Remove indexes and constraints
    op.drop_index('ix_products_sku', 'products')
    op.drop_constraint('uq_products_sku', 'products', type_='unique')
    
    # Remove new columns
    op.drop_column('products', 'audio_description')
    op.drop_column('products', 'category')
    op.drop_column('products', 'keywords')
    op.drop_column('products', 'sku')
    
    # Revert description column type
    op.alter_column('products', 'description', type_=sa.String())
