# Database Migration: Add Reporting and Analytics Tables

"""
Migration script to add reporting and analytics tables to the database.

Tables created:
- reports: Report definitions
- report_schedules: Scheduled report executions
- report_executions: Report execution history
- dashboards: Dashboard definitions
- dashboard_widgets: Dashboard widgets
- kpis: KPI definitions
- kpi_values: KPI value history
- prediction_models: ML prediction models
- predictions: Prediction results
- data_exports: Data export history
"""

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Float
from datetime import datetime


def upgrade(engine):
    """Create reporting tables"""
    metadata = MetaData()
    
    # Reports table
    reports = Table(
        'reports', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String(255), nullable=False, index=True),
        Column('description', Text, nullable=True),
        Column('report_type', String(50), nullable=False, index=True),
        Column('definition', JSON, nullable=False),
        Column('owner_id', Integer, ForeignKey('users.id'), nullable=False),
        Column('is_public', Boolean, default=False),
        Column('tags', JSON, default='[]'),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    )
    
    # Report schedules table
    report_schedules = Table(
        'report_schedules', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('report_id', Integer, ForeignKey('reports.id'), nullable=False),
        Column('frequency', String(50), nullable=False),
        Column('time_of_day', String(5), nullable=False),
        Column('recipients', JSON, nullable=False),
        Column('format', String(20), nullable=False),
        Column('enabled', Boolean, default=True),
        Column('last_run', DateTime, nullable=True),
        Column('next_run', DateTime, nullable=False),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    )
    
    # Report executions table
    report_executions = Table(
        'report_executions', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('report_id', Integer, ForeignKey('reports.id'), nullable=False),
        Column('executed_by', Integer, ForeignKey('users.id'), nullable=False),
        Column('executed_at', DateTime, default=datetime.utcnow, index=True),
        Column('parameters', JSON, default='{}'),
        Column('format', String(20), nullable=False),
        Column('status', String(20), nullable=False),
        Column('result_file', String(500), nullable=True),
        Column('error_message', Text, nullable=True),
        Column('execution_time_ms', Integer, nullable=True),
        Column('row_count', Integer, nullable=True)
    )
    
    # Dashboards table
    dashboards = Table(
        'dashboards', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String(255), nullable=False, index=True),
        Column('description', Text, nullable=True),
        Column('owner_id', Integer, ForeignKey('users.id'), nullable=False),
        Column('is_public', Boolean, default=False),
        Column('layout', String(20), default='grid'),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    )
    
    # Dashboard widgets table
    dashboard_widgets = Table(
        'dashboard_widgets', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('dashboard_id', Integer, ForeignKey('dashboards.id'), nullable=False),
        Column('config', JSON, nullable=False),
        Column('position_x', Integer, default=0),
        Column('position_y', Integer, default=0),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    )
    
    # KPIs table
    kpis = Table(
        'kpis', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String(255), nullable=False, index=True),
        Column('metric', String(100), nullable=False, index=True),
        Column('target', JSON, nullable=False),
        Column('data_source', String(255), nullable=False),
        Column('calculation', JSON, nullable=False),
        Column('owner_id', Integer, ForeignKey('users.id'), nullable=False),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    )
    
    # KPI values table
    kpi_values = Table(
        'kpi_values', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('kpi_id', Integer, ForeignKey('kpis.id'), nullable=False),
        Column('value', Float, nullable=False),
        Column('target_value', Float, nullable=False),
        Column('achievement_percentage', Float, nullable=False),
        Column('period_start', DateTime, nullable=False, index=True),
        Column('period_end', DateTime, nullable=False, index=True),
        Column('calculated_at', DateTime, default=datetime.utcnow)
    )
    
    # Prediction models table
    prediction_models = Table(
        'prediction_models', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String(255), nullable=False, index=True),
        Column('model_type', String(50), nullable=False),
        Column('data_source', String(255), nullable=False),
        Column('target_field', String(100), nullable=False),
        Column('feature_fields', JSON, nullable=False),
        Column('model_data', JSON, nullable=False),
        Column('accuracy_metrics', JSON, nullable=False),
        Column('trained_at', DateTime, default=datetime.utcnow),
        Column('created_by', Integer, ForeignKey('users.id'), nullable=False)
    )
    
    # Predictions table
    predictions = Table(
        'predictions', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('model_id', Integer, ForeignKey('prediction_models.id'), nullable=False),
        Column('predictions', JSON, nullable=False),
        Column('confidence_intervals', JSON, nullable=False),
        Column('prediction_period', Integer, nullable=False),
        Column('generated_at', DateTime, default=datetime.utcnow, index=True)
    )
    
    # Data exports table
    data_exports = Table(
        'data_exports', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('data_source', String(255), nullable=False),
        Column('filters', JSON, default='[]'),
        Column('fields', JSON, default='[]'),
        Column('format', String(20), nullable=False),
        Column('file_name', String(500), nullable=False),
        Column('file_path', String(1000), nullable=False),
        Column('file_size', Integer, nullable=False),
        Column('row_count', Integer, nullable=False),
        Column('exported_by', Integer, ForeignKey('users.id'), nullable=False),
        Column('exported_at', DateTime, default=datetime.utcnow, index=True),
        Column('expires_at', DateTime, nullable=False)
    )
    
    # Create all tables
    metadata.create_all(engine)
    
    print("✅ Reporting tables created successfully")


def downgrade(engine):
    """Drop reporting tables"""
    metadata = MetaData()
    
    # Drop tables in reverse order (to handle foreign keys)
    table_names = [
        'data_exports',
        'predictions',
        'prediction_models',
        'kpi_values',
        'kpis',
        'dashboard_widgets',
        'dashboards',
        'report_executions',
        'report_schedules',
        'reports'
    ]
    
    for table_name in table_names:
        table = Table(table_name, metadata)
        table.drop(engine, checkfirst=True)
    
    print("✅ Reporting tables dropped successfully")


if __name__ == "__main__":
    # Example usage
    from backend.core.database import engine
    
    print("Running reporting tables migration...")
    upgrade(engine)
    print("Migration completed!")
