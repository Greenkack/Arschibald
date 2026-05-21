"""
Database Migration: Add Sales Pipeline Tables
Creates tables for pipeline stages, opportunities, activities, and analytics
"""

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON
from datetime import datetime


def upgrade(engine):
    """Create pipeline tables"""
    metadata = MetaData()
    
    # Pipeline Stages
    pipeline_stages = Table(
        'pipeline_stages',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(100), nullable=False),
        Column('stage_type', String(50), nullable=False),
        Column('order_index', Integer, nullable=False),
        Column('probability', Float, default=0.0),
        Column('color', String(20), default='#3B82F6'),
        Column('icon', String(50)),
        Column('description', Text),
        Column('auto_actions', JSON),
        Column('required_fields', JSON),
        Column('time_limit_days', Integer),
        Column('is_active', Boolean, default=True),
        Column('is_system', Boolean, default=False),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow),
        Column('created_by', Integer, ForeignKey('users.id'))
    )
    
    # Opportunities
    opportunities = Table(
        'opportunities',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(200), nullable=False),
        Column('description', Text),
        Column('customer_id', Integer, ForeignKey('customers.id')),
        Column('contact_name', String(100)),
        Column('contact_email', String(100)),
        Column('contact_phone', String(50)),
        Column('stage_id', Integer, ForeignKey('pipeline_stages.id'), nullable=False),
        Column('status', String(50), default='active'),
        Column('estimated_value', Float, nullable=False),
        Column('actual_value', Float),
        Column('currency', String(3), default='EUR'),
        Column('probability', Float),
        Column('weighted_value', Float),
        Column('expected_close_date', DateTime),
        Column('actual_close_date', DateTime),
        Column('stage_entered_at', DateTime, default=datetime.utcnow),
        Column('owner_id', Integer, ForeignKey('users.id'), nullable=False),
        Column('team_id', Integer, ForeignKey('teams.id')),
        Column('source', String(100)),
        Column('campaign_id', Integer, ForeignKey('campaigns.id')),
        Column('custom_fields', JSON),
        Column('tags', JSON),
        Column('win_reason', Text),
        Column('loss_reason', Text),
        Column('competitor', String(100)),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow)
    )
    
    # Opportunity Activities
    opportunity_activities = Table(
        'opportunity_activities',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('opportunity_id', Integer, ForeignKey('opportunities.id'), nullable=False),
        Column('activity_type', String(50), nullable=False),
        Column('subject', String(200)),
        Column('description', Text),
        Column('scheduled_at', DateTime),
        Column('completed_at', DateTime),
        Column('duration_minutes', Integer),
        Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
        Column('created_at', DateTime, default=datetime.utcnow)
    )
    
    # Opportunity Stage History
    opportunity_stage_history = Table(
        'opportunity_stage_history',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('opportunity_id', Integer, ForeignKey('opportunities.id'), nullable=False),
        Column('from_stage_id', Integer, ForeignKey('pipeline_stages.id')),
        Column('to_stage_id', Integer, ForeignKey('pipeline_stages.id'), nullable=False),
        Column('days_in_previous_stage', Integer),
        Column('changed_by', Integer, ForeignKey('users.id'), nullable=False),
        Column('reason', Text),
        Column('created_at', DateTime, default=datetime.utcnow)
    )
    
    # Opportunity Products
    opportunity_products = Table(
        'opportunity_products',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('opportunity_id', Integer, ForeignKey('opportunities.id'), nullable=False),
        Column('product_id', Integer, ForeignKey('products.id'), nullable=False),
        Column('quantity', Integer, default=1),
        Column('unit_price', Float, nullable=False),
        Column('discount_percent', Float, default=0.0),
        Column('total_price', Float, nullable=False),
        Column('description', Text),
        Column('created_at', DateTime, default=datetime.utcnow)
    )
    
    # Pipeline Forecasts
    pipeline_forecasts = Table(
        'pipeline_forecasts',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('forecast_date', DateTime, nullable=False),
        Column('period_start', DateTime, nullable=False),
        Column('period_end', DateTime, nullable=False),
        Column('total_opportunities', Integer),
        Column('total_value', Float),
        Column('weighted_value', Float),
        Column('expected_wins', Integer),
        Column('expected_revenue', Float),
        Column('stage_breakdown', JSON),
        Column('owner_breakdown', JSON),
        Column('confidence_level', Float),
        Column('created_by', Integer, ForeignKey('users.id'), nullable=False),
        Column('created_at', DateTime, default=datetime.utcnow)
    )
    
    # Pipeline Automations
    pipeline_automations = Table(
        'pipeline_automations',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(100), nullable=False),
        Column('description', Text),
        Column('trigger_type', String(50), nullable=False),
        Column('trigger_config', JSON),
        Column('conditions', JSON),
        Column('actions', JSON),
        Column('is_active', Boolean, default=True),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow),
        Column('created_by', Integer, ForeignKey('users.id'), nullable=False)
    )
    
    # Create all tables
    metadata.create_all(engine)
    
    # Insert default pipeline stages
    conn = engine.connect()
    
    default_stages = [
        {'name': 'Lead', 'stage_type': 'lead', 'order_index': 1, 'probability': 10.0, 'color': '#94A3B8', 'is_system': True},
        {'name': 'Qualified', 'stage_type': 'qualified', 'order_index': 2, 'probability': 25.0, 'color': '#60A5FA', 'is_system': True},
        {'name': 'Proposal', 'stage_type': 'proposal', 'order_index': 3, 'probability': 50.0, 'color': '#FBBF24', 'is_system': True},
        {'name': 'Negotiation', 'stage_type': 'negotiation', 'order_index': 4, 'probability': 75.0, 'color': '#F59E0B', 'is_system': True},
        {'name': 'Closed Won', 'stage_type': 'closed_won', 'order_index': 5, 'probability': 100.0, 'color': '#10B981', 'is_system': True},
        {'name': 'Closed Lost', 'stage_type': 'closed_lost', 'order_index': 6, 'probability': 0.0, 'color': '#EF4444', 'is_system': True},
    ]
    
    for stage in default_stages:
        conn.execute(pipeline_stages.insert().values(**stage))
    
    conn.close()
    
    print("✅ Pipeline tables created successfully")
    print("✅ Default pipeline stages inserted")


def downgrade(engine):
    """Drop pipeline tables"""
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    tables_to_drop = [
        'pipeline_automations',
        'pipeline_forecasts',
        'opportunity_products',
        'opportunity_stage_history',
        'opportunity_activities',
        'opportunities',
        'pipeline_stages'
    ]
    
    for table_name in tables_to_drop:
        if table_name in metadata.tables:
            metadata.tables[table_name].drop(engine)
    
    print("✅ Pipeline tables dropped successfully")


if __name__ == "__main__":
    # For testing
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///test_pipeline.db')
    upgrade(engine)
