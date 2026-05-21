"""
Database Migration: Add Result History Tables

Creates tables for storing calculation result history, versioning, comparison, and sharing.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_result_history'
down_revision = None  # Set to previous migration
branch_labels = None
depends_on = None


def upgrade():
    """Create result history tables"""
    
    # Create result_history table
    op.create_table(
        'result_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('result_type', sa.String(length=50), nullable=False),
        sa.Column('result_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('input_data', sa.JSON(), nullable=False),
        sa.Column('output_data', sa.JSON(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=True, default=1),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('is_favorite', sa.Boolean(), nullable=True, default=False),
        sa.Column('is_archived', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['parent_id'], ['result_history.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for result_history
    op.create_index('ix_result_history_user_id', 'result_history', ['user_id'])
    op.create_index('ix_result_history_project_id', 'result_history', ['project_id'])
    op.create_index('ix_result_history_result_type', 'result_history', ['result_type'])
    op.create_index('ix_result_history_is_favorite', 'result_history', ['is_favorite'])
    op.create_index('ix_result_history_is_archived', 'result_history', ['is_archived'])
    op.create_index('ix_result_history_created_at', 'result_history', ['created_at'])
    
    # Create result_tags table
    op.create_table(
        'result_tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('result_id', sa.Integer(), nullable=False),
        sa.Column('tag_name', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['result_id'], ['result_history.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for result_tags
    op.create_index('ix_result_tags_result_id', 'result_tags', ['result_id'])
    op.create_index('ix_result_tags_tag_name', 'result_tags', ['tag_name'])
    
    # Create result_shares table
    op.create_table(
        'result_shares',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('result_id', sa.Integer(), nullable=False),
        sa.Column('shared_by_user_id', sa.Integer(), nullable=False),
        sa.Column('shared_with_user_id', sa.Integer(), nullable=True),
        sa.Column('share_token', sa.String(length=255), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=True, default=False),
        sa.Column('can_edit', sa.Boolean(), nullable=True, default=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('accessed_at', sa.DateTime(), nullable=True),
        sa.Column('access_count', sa.Integer(), nullable=True, default=0),
        sa.ForeignKeyConstraint(['result_id'], ['result_history.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['shared_by_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['shared_with_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('share_token')
    )
    
    # Create indexes for result_shares
    op.create_index('ix_result_shares_result_id', 'result_shares', ['result_id'])
    op.create_index('ix_result_shares_share_token', 'result_shares', ['share_token'])
    
    # Create result_comparisons table
    op.create_table(
        'result_comparisons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('comparison_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('result_ids', sa.JSON(), nullable=False),
        sa.Column('comparison_type', sa.String(length=50), nullable=False),
        sa.Column('metrics_to_compare', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for result_comparisons
    op.create_index('ix_result_comparisons_user_id', 'result_comparisons', ['user_id'])
    op.create_index('ix_result_comparisons_created_at', 'result_comparisons', ['created_at'])


def downgrade():
    """Drop result history tables"""
    
    # Drop indexes
    op.drop_index('ix_result_comparisons_created_at', table_name='result_comparisons')
    op.drop_index('ix_result_comparisons_user_id', table_name='result_comparisons')
    op.drop_index('ix_result_shares_share_token', table_name='result_shares')
    op.drop_index('ix_result_shares_result_id', table_name='result_shares')
    op.drop_index('ix_result_tags_tag_name', table_name='result_tags')
    op.drop_index('ix_result_tags_result_id', table_name='result_tags')
    op.drop_index('ix_result_history_created_at', table_name='result_history')
    op.drop_index('ix_result_history_is_archived', table_name='result_history')
    op.drop_index('ix_result_history_is_favorite', table_name='result_history')
    op.drop_index('ix_result_history_result_type', table_name='result_history')
    op.drop_index('ix_result_history_project_id', table_name='result_history')
    op.drop_index('ix_result_history_user_id', table_name='result_history')
    
    # Drop tables
    op.drop_table('result_comparisons')
    op.drop_table('result_shares')
    op.drop_table('result_tags')
    op.drop_table('result_history')
