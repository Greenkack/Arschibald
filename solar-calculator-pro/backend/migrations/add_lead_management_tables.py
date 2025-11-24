"""
Database Migration: Add Lead Management Tables
Creates tables for lead management, scoring, assignment, and nurturing
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_lead_management'
down_revision = None  # Update this with the previous migration
branch_labels = None
depends_on = None


def upgrade():
    """Create lead management tables"""
    
    # Create leads table
    op.create_table(
        'leads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('company', sa.String(length=255), nullable=True),
        sa.Column('job_title', sa.String(length=100), nullable=True),
        sa.Column('street', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('status', sa.Enum('new', 'contacted', 'qualified', 'proposal', 'negotiation', 'won', 'lost', 'nurturing', name='leadstatus'), nullable=True),
        sa.Column('source', sa.Enum('website', 'referral', 'social_media', 'email_campaign', 'phone', 'event', 'partner', 'advertisement', 'organic_search', 'paid_search', 'other', name='leadsource'), nullable=False),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'urgent', name='leadpriority'), nullable=True),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('score_breakdown', sa.Text(), nullable=True),
        sa.Column('assigned_to_id', sa.Integer(), nullable=True),
        sa.Column('assigned_at', sa.DateTime(), nullable=True),
        sa.Column('interested_in', sa.Text(), nullable=True),
        sa.Column('estimated_value', sa.Float(), nullable=True),
        sa.Column('estimated_close_date', sa.DateTime(), nullable=True),
        sa.Column('first_contact_date', sa.DateTime(), nullable=True),
        sa.Column('last_contact_date', sa.DateTime(), nullable=True),
        sa.Column('next_follow_up_date', sa.DateTime(), nullable=True),
        sa.Column('contact_count', sa.Integer(), nullable=True),
        sa.Column('converted', sa.Boolean(), nullable=True),
        sa.Column('converted_at', sa.DateTime(), nullable=True),
        sa.Column('converted_to_customer_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_to_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['converted_to_customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leads_email'), 'leads', ['email'], unique=True)
    op.create_index(op.f('ix_leads_id'), 'leads', ['id'], unique=False)
    op.create_index(op.f('ix_leads_status'), 'leads', ['status'], unique=False)
    op.create_index(op.f('ix_leads_source'), 'leads', ['source'], unique=False)
    op.create_index(op.f('ix_leads_score'), 'leads', ['score'], unique=False)
    op.create_index(op.f('ix_leads_converted'), 'leads', ['converted'], unique=False)
    
    # Create lead_activities table
    op.create_table(
        'lead_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lead_id', sa.Integer(), nullable=False),
        sa.Column('activity_type', sa.String(length=50), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('outcome', sa.String(length=100), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lead_activities_id'), 'lead_activities', ['id'], unique=False)
    op.create_index(op.f('ix_lead_activities_lead_id'), 'lead_activities', ['lead_id'], unique=False)
    
    # Create lead_scoring_rules table
    op.create_table(
        'lead_scoring_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('field', sa.String(length=100), nullable=False),
        sa.Column('operator', sa.String(length=20), nullable=False),
        sa.Column('value', sa.String(length=255), nullable=True),
        sa.Column('points', sa.Integer(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lead_scoring_rules_id'), 'lead_scoring_rules', ['id'], unique=False)
    
    # Create lead_assignment_rules table
    op.create_table(
        'lead_assignment_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('conditions', sa.Text(), nullable=False),
        sa.Column('assign_to_user_id', sa.Integer(), nullable=True),
        sa.Column('assign_to_team_id', sa.Integer(), nullable=True),
        sa.Column('assignment_method', sa.String(length=50), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assign_to_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lead_assignment_rules_id'), 'lead_assignment_rules', ['id'], unique=False)
    
    # Create lead_nurturing_campaigns table
    op.create_table(
        'lead_nurturing_campaigns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lead_id', sa.Integer(), nullable=False),
        sa.Column('campaign_name', sa.String(length=255), nullable=False),
        sa.Column('campaign_type', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('current_step', sa.Integer(), nullable=True),
        sa.Column('total_steps', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('last_action_at', sa.DateTime(), nullable=True),
        sa.Column('next_action_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('emails_sent', sa.Integer(), nullable=True),
        sa.Column('emails_opened', sa.Integer(), nullable=True),
        sa.Column('emails_clicked', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lead_nurturing_campaigns_id'), 'lead_nurturing_campaigns', ['id'], unique=False)
    op.create_index(op.f('ix_lead_nurturing_campaigns_lead_id'), 'lead_nurturing_campaigns', ['lead_id'], unique=False)
    
    # Create lead_source_analytics table
    op.create_table(
        'lead_source_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source', sa.Enum('website', 'referral', 'social_media', 'email_campaign', 'phone', 'event', 'partner', 'advertisement', 'organic_search', 'paid_search', 'other', name='leadsource'), nullable=False),
        sa.Column('source_detail', sa.String(length=255), nullable=True),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('leads_generated', sa.Integer(), nullable=True),
        sa.Column('leads_qualified', sa.Integer(), nullable=True),
        sa.Column('leads_converted', sa.Integer(), nullable=True),
        sa.Column('total_value', sa.Float(), nullable=True),
        sa.Column('average_score', sa.Float(), nullable=True),
        sa.Column('average_conversion_time_days', sa.Float(), nullable=True),
        sa.Column('cost', sa.Float(), nullable=True),
        sa.Column('cost_per_lead', sa.Float(), nullable=True),
        sa.Column('roi', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lead_source_analytics_id'), 'lead_source_analytics', ['id'], unique=False)
    op.create_index(op.f('ix_lead_source_analytics_source'), 'lead_source_analytics', ['source'], unique=False)


def downgrade():
    """Drop lead management tables"""
    
    op.drop_index(op.f('ix_lead_source_analytics_source'), table_name='lead_source_analytics')
    op.drop_index(op.f('ix_lead_source_analytics_id'), table_name='lead_source_analytics')
    op.drop_table('lead_source_analytics')
    
    op.drop_index(op.f('ix_lead_nurturing_campaigns_lead_id'), table_name='lead_nurturing_campaigns')
    op.drop_index(op.f('ix_lead_nurturing_campaigns_id'), table_name='lead_nurturing_campaigns')
    op.drop_table('lead_nurturing_campaigns')
    
    op.drop_index(op.f('ix_lead_assignment_rules_id'), table_name='lead_assignment_rules')
    op.drop_table('lead_assignment_rules')
    
    op.drop_index(op.f('ix_lead_scoring_rules_id'), table_name='lead_scoring_rules')
    op.drop_table('lead_scoring_rules')
    
    op.drop_index(op.f('ix_lead_activities_lead_id'), table_name='lead_activities')
    op.drop_index(op.f('ix_lead_activities_id'), table_name='lead_activities')
    op.drop_table('lead_activities')
    
    op.drop_index(op.f('ix_leads_converted'), table_name='leads')
    op.drop_index(op.f('ix_leads_score'), table_name='leads')
    op.drop_index(op.f('ix_leads_source'), table_name='leads')
    op.drop_index(op.f('ix_leads_status'), table_name='leads')
    op.drop_index(op.f('ix_leads_id'), table_name='leads')
    op.drop_index(op.f('ix_leads_email'), table_name='leads')
    op.drop_table('leads')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS leadstatus')
    op.execute('DROP TYPE IF EXISTS leadsource')
    op.execute('DROP TYPE IF EXISTS leadpriority')
