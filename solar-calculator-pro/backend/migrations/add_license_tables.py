# Database Migration: Add License Management Tables

"""
Migration script to add license management tables to the database.

Run this script to create the necessary tables for license management:
- licenses
- license_validations
- license_features
- license_renewals
"""

from sqlalchemy import create_engine, MetaData
from backend.core.database import Base, engine
from backend.models.license_models import (
    License, LicenseValidation, LicenseFeature, LicenseRenewal
)


def upgrade():
    """Create license management tables"""
    print("Creating license management tables...")
    
    # Create all tables defined in license_models
    Base.metadata.create_all(bind=engine, tables=[
        License.__table__,
        LicenseValidation.__table__,
        LicenseFeature.__table__,
        LicenseRenewal.__table__
    ])
    
    print("✓ License management tables created successfully")
    
    # Seed default features
    seed_default_features()


def downgrade():
    """Drop license management tables"""
    print("Dropping license management tables...")
    
    Base.metadata.drop_all(bind=engine, tables=[
        LicenseRenewal.__table__,
        LicenseFeature.__table__,
        LicenseValidation.__table__,
        License.__table__
    ])
    
    print("✓ License management tables dropped successfully")


def seed_default_features():
    """Seed default licensable features"""
    from sqlalchemy.orm import Session
    from backend.models.license_models import LicenseFeature
    
    print("Seeding default features...")
    
    default_features = [
        {
            "feature_key": "solar_calculator",
            "feature_name": "Solar Calculator",
            "description": "Basic solar system calculations",
            "available_in_trial": True,
            "available_in_basic": True,
            "available_in_professional": True,
            "available_in_enterprise": True,
            "available_in_lifetime": True,
            "category": "core"
        },
        {
            "feature_key": "heatpump_calculator",
            "feature_name": "Heat Pump Calculator",
            "description": "Heat pump sizing and calculations",
            "available_in_trial": True,
            "available_in_basic": True,
            "available_in_professional": True,
            "available_in_enterprise": True,
            "available_in_lifetime": True,
            "category": "core"
        },
        {
            "feature_key": "3d_visualization",
            "feature_name": "3D Visualization",
            "description": "3D roof and module visualization",
            "available_in_trial": False,
            "available_in_basic": False,
            "available_in_professional": True,
            "available_in_enterprise": True,
            "available_in_lifetime": True,
            "category": "visualization"
        },
        {
            "feature_key": "pdf_generation",
            "feature_name": "PDF Generation",
            "description": "Generate professional PDF reports",
            "available_in_trial": True,
            "available_in_basic": True,
            "available_in_professional": True,
            "available_in_enterprise": True,
            "available_in_lifetime": True,
            "category": "export"
        },
        {
            "feature_key": "advanced_pdf",
            "feature_name": "Advanced PDF Features",
            "description": "Extended PDF with custom branding and multi-page",
            "available_in_trial": False,
            "available_in_basic": False,
            "available_in_professional": True,
            "available_in_enterprise": True,
            "available_in_lifetime": True,
            "category": "export"
        },
        {
            "feature_key": "multi_pdf",
            "feature_name": "Multi-PDF Generation",
            "description": "Generate multiple PDFs for different companies",
            "available_in_trial": False,
            "available_in_basic": False,
            "available_in_professional": False,
            "available_in_enterprise": True,
            "available_in_lifetime": True,
            "category": "export"
        },
        {
            "feature_key": "crm",
            "feature_name": "CRM System",
            "description": "Customer relationship management",
            "available_in_trial": False,
            "available_in_basic": False,
            "available_in_professional": True,
            "available_in_enterprise": True,
            "available_in_lifetime": True,
            "category": "business"
        },
        {
            "feature_key": "price_matrix",
            "feature_name": "Price Matrix",
            "description": "Dynamic pricing with Excel-like formulas",
            "available_in_trial": False,
            "available_in_basic": True,
            "available_in_professional": True,
            "available_in_enterprise": True,
            "available_in_lifetime": True,
            "category": "pricing"
        },
        {
            "feature_key": "product_rotation",
            "feature_name": "Product Rotation",
            "description": "Automatic product rotation for multi-PDF",
            "available_in_trial": False,
            "available_in_basic": False,
            "available_in_professional": False,
            "available_in_enterprise": True,
            "available_in_lifetime": True,
            "category": "advanced"
        },
        {
            "feature_key": "api_access",
            "feature_name": "API Access",
            "description": "REST API access for integrations",
            "available_in_trial": False,
            "available_in_basic": False,
            "available_in_professional": True,
            "available_in_enterprise": True,
            "available_in_lifetime": True,
            "category": "integration"
        },
        {
            "feature_key": "unlimited_projects",
            "feature_name": "Unlimited Projects",
            "description": "Create unlimited projects",
            "available_in_trial": False,
            "available_in_basic": False,
            "available_in_professional": True,
            "available_in_enterprise": True,
            "available_in_lifetime": True,
            "category": "limits"
        },
        {
            "feature_key": "multi_user",
            "feature_name": "Multi-User Support",
            "description": "Multiple users per license",
            "available_in_trial": False,
            "available_in_basic": False,
            "available_in_professional": True,
            "available_in_enterprise": True,
            "available_in_lifetime": True,
            "category": "collaboration"
        },
        {
            "feature_key": "white_label",
            "feature_name": "White Label",
            "description": "Custom branding and white-label options",
            "available_in_trial": False,
            "available_in_basic": False,
            "available_in_professional": False,
            "available_in_enterprise": True,
            "available_in_lifetime": True,
            "category": "branding"
        },
        {
            "feature_key": "priority_support",
            "feature_name": "Priority Support",
            "description": "Priority customer support",
            "available_in_trial": False,
            "available_in_basic": False,
            "available_in_professional": True,
            "available_in_enterprise": True,
            "available_in_lifetime": True,
            "category": "support"
        }
    ]
    
    session = Session(bind=engine)
    
    try:
        for feature_data in default_features:
            # Check if feature already exists
            existing = session.query(LicenseFeature).filter(
                LicenseFeature.feature_key == feature_data["feature_key"]
            ).first()
            
            if not existing:
                feature = LicenseFeature(**feature_data)
                session.add(feature)
        
        session.commit()
        print(f"✓ Seeded {len(default_features)} default features")
    except Exception as e:
        session.rollback()
        print(f"✗ Error seeding features: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
