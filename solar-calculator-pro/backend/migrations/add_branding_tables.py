# backend/migrations/add_branding_tables.py

"""
Database migration for PDF Branding & Multi-Logo System
Creates tables for company branding, logo positions, templates, and assets
"""

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Boolean, Float, JSON, ForeignKey, DateTime
from datetime import datetime


def upgrade(engine):
    """Create branding tables"""
    metadata = MetaData()
    
    # Company Branding table
    company_branding = Table(
        'company_branding',
        metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('company_id', Integer, ForeignKey('companies.id'), nullable=False, index=True),
        
        # Logo configuration
        Column('logo_path', String(500)),
        Column('logo_base64', Text),
        Column('logo_width', Float, default=100.0),
        Column('logo_height', Float, default=50.0),
        Column('logo_position_x', Float, default=50.0),
        Column('logo_position_y', Float, default=750.0),
        Column('logo_page', String(50), default='all'),
        
        # Color scheme
        Column('primary_color', String(7), default='#0066CC'),
        Column('secondary_color', String(7), default='#003366'),
        Column('accent_color', String(7), default='#FF6600'),
        Column('text_color', String(7), default='#333333'),
        Column('background_color', String(7), default='#FFFFFF'),
        Column('header_color', String(7), default='#0066CC'),
        Column('footer_color', String(7), default='#666666'),
        
        # Typography
        Column('font_family', String(100), default='Helvetica'),
        Column('font_size_base', Integer, default=10),
        Column('font_size_heading', Integer, default=16),
        Column('font_size_subheading', Integer, default=12),
        Column('font_weight', String(20), default='normal'),
        
        # Header configuration
        Column('header_enabled', Boolean, default=True),
        Column('header_text', String(500)),
        Column('header_height', Float, default=80.0),
        Column('header_background_color', String(7)),
        Column('header_text_color', String(7)),
        Column('header_logo_enabled', Boolean, default=True),
        
        # Footer configuration
        Column('footer_enabled', Boolean, default=True),
        Column('footer_text', String(500)),
        Column('footer_height', Float, default=60.0),
        Column('footer_background_color', String(7)),
        Column('footer_text_color', String(7)),
        Column('footer_logo_enabled', Boolean, default=False),
        Column('footer_page_numbers', Boolean, default=True),
        
        # Watermark configuration
        Column('watermark_enabled', Boolean, default=False),
        Column('watermark_text', String(200)),
        Column('watermark_opacity', Float, default=0.1),
        Column('watermark_rotation', Float, default=45.0),
        Column('watermark_font_size', Integer, default=60),
        Column('watermark_color', String(7), default='#CCCCCC'),
        
        # Template configuration
        Column('template_path', String(500)),
        Column('template_type', String(50), default='standard'),
        
        # YML coordinates override
        Column('yml_coordinates', JSON),
        
        # Metadata
        Column('is_active', Boolean, default=True),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    )
    
    # Logo Positions table
    logo_positions = Table(
        'logo_positions',
        metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('branding_id', Integer, ForeignKey('company_branding.id'), nullable=False, index=True),
        
        # Position context
        Column('page_number', Integer),
        Column('context', String(50), default='header'),
        
        # Position from YML coordinates
        Column('x', Float, nullable=False),
        Column('y', Float, nullable=False),
        Column('width', Float),
        Column('height', Float),
        
        # Styling
        Column('opacity', Float, default=1.0),
        Column('rotation', Float, default=0.0),
        Column('scale', Float, default=1.0),
        
        # Metadata
        Column('created_at', DateTime, default=datetime.utcnow)
    )
    
    # Branding Templates table
    branding_templates = Table(
        'branding_templates',
        metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String(200), nullable=False, unique=True),
        Column('description', Text),
        
        # Template configuration (JSON)
        Column('config', JSON, nullable=False),
        
        # Preview
        Column('preview_image', Text),
        
        # Metadata
        Column('is_public', Boolean, default=True),
        Column('created_by', Integer, ForeignKey('users.id')),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    )
    
    # Branding Assets table
    branding_assets = Table(
        'branding_assets',
        metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('company_id', Integer, ForeignKey('companies.id'), nullable=False, index=True),
        
        # Asset information
        Column('asset_type', String(50), nullable=False),
        Column('name', String(200), nullable=False),
        Column('description', Text),
        
        # File information
        Column('file_path', String(500)),
        Column('file_base64', Text),
        Column('file_size', Integer),
        Column('mime_type', String(100)),
        
        # Dimensions (for images)
        Column('width', Integer),
        Column('height', Integer),
        
        # Metadata
        Column('is_primary', Boolean, default=False),
        Column('tags', JSON),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    )
    
    # Create all tables
    metadata.create_all(engine)
    
    print("✅ Branding tables created successfully")


def downgrade(engine):
    """Drop branding tables"""
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    # Drop tables in reverse order (respecting foreign keys)
    tables_to_drop = ['branding_assets', 'branding_templates', 'logo_positions', 'company_branding']
    
    for table_name in tables_to_drop:
        if table_name in metadata.tables:
            metadata.tables[table_name].drop(engine)
            print(f"✅ Dropped table: {table_name}")


if __name__ == "__main__":
    # Example usage
    from sqlalchemy import create_engine
    
    # Create engine (adjust connection string as needed)
    engine = create_engine('sqlite:///./solar_calculator.db')
    
    # Run upgrade
    upgrade(engine)
    
    print("\n✅ Migration completed successfully!")
    print("\nCreated tables:")
    print("  - company_branding")
    print("  - logo_positions")
    print("  - branding_templates")
    print("  - branding_assets")
