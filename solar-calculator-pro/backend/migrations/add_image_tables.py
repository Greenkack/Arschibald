# backend/migrations/add_image_tables.py
"""
Migration script to add image management tables
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_image_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create product_images table
    op.create_table(
        'product_images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('original_path', sa.String(length=500), nullable=False),
        sa.Column('original_size', sa.Integer(), nullable=False),
        sa.Column('original_width', sa.Integer(), nullable=False),
        sa.Column('original_height', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('file_hash', sa.String(length=64), nullable=False),
        sa.Column('alt_text', sa.String(length=500), nullable=True),
        sa.Column('caption', sa.Text(), nullable=True),
        sa.Column('variants', sa.JSON(), nullable=True),
        sa.Column('cdn_url', sa.String(length=500), nullable=True),
        sa.Column('cdn_enabled', sa.Boolean(), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_images_id'), 'product_images', ['id'], unique=False)
    op.create_index(op.f('ix_product_images_product_id'), 'product_images', ['product_id'], unique=False)
    op.create_index(op.f('ix_product_images_file_hash'), 'product_images', ['file_hash'], unique=False)
    
    # Create image_variants table
    op.create_table(
        'image_variants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('image_id', sa.Integer(), nullable=False),
        sa.Column('variant_name', sa.String(length=50), nullable=False),
        sa.Column('width', sa.Integer(), nullable=False),
        sa.Column('height', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('quality', sa.Integer(), nullable=True),
        sa.Column('format', sa.String(length=10), nullable=True),
        sa.Column('cdn_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['image_id'], ['product_images.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_image_variants_id'), 'image_variants', ['id'], unique=False)
    op.create_index(op.f('ix_image_variants_image_id'), 'image_variants', ['image_id'], unique=False)
    
    # Create image_galleries table
    op.create_table(
        'image_galleries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('layout', sa.String(length=50), nullable=True),
        sa.Column('columns', sa.Integer(), nullable=True),
        sa.Column('product_category', sa.String(length=100), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_image_galleries_id'), 'image_galleries', ['id'], unique=False)
    
    # Create image_search_index table
    op.create_table(
        'image_search_index',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('image_id', sa.Integer(), nullable=False),
        sa.Column('search_text', sa.Text(), nullable=False),
        sa.Column('keywords', sa.JSON(), nullable=True),
        sa.Column('indexed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['image_id'], ['product_images.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_image_search_index_id'), 'image_search_index', ['id'], unique=False)
    op.create_index(op.f('ix_image_search_index_image_id'), 'image_search_index', ['image_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_image_search_index_image_id'), table_name='image_search_index')
    op.drop_index(op.f('ix_image_search_index_id'), table_name='image_search_index')
    op.drop_table('image_search_index')
    
    op.drop_index(op.f('ix_image_galleries_id'), table_name='image_galleries')
    op.drop_table('image_galleries')
    
    op.drop_index(op.f('ix_image_variants_image_id'), table_name='image_variants')
    op.drop_index(op.f('ix_image_variants_id'), table_name='image_variants')
    op.drop_table('image_variants')
    
    op.drop_index(op.f('ix_product_images_file_hash'), table_name='product_images')
    op.drop_index(op.f('ix_product_images_product_id'), table_name='product_images')
    op.drop_index(op.f('ix_product_images_id'), table_name='product_images')
    op.drop_table('product_images')
