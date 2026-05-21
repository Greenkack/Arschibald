"""
Database Migration: Add Company Tables for Multi-PDF System

This migration creates the necessary tables for the company database system
used in multi-PDF generation.

Run this migration with:
    python -m backend.migrations.add_company_tables
"""

from sqlalchemy import create_engine, text
from backend.core.database import Base, engine
from backend.models.company_models import Company, CompanyDocument, CompanyImage, CompanyPricingRule


def upgrade():
    """Create company-related tables"""
    print("Creating company tables...")
    
    # Create all tables defined in company_models
    Base.metadata.create_all(bind=engine, tables=[
        Company.__table__,
        CompanyDocument.__table__,
        CompanyImage.__table__,
        CompanyPricingRule.__table__
    ])
    
    print("✓ Company tables created successfully")
    
    # Create indexes for better performance
    with engine.connect() as conn:
        print("Creating indexes...")
        
        # Company indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_companies_active ON companies(is_active);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_companies_default ON companies(is_default);
        """))
        
        # Document indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_company_documents_company_id ON company_documents(company_id);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_company_documents_type ON company_documents(document_type);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_company_documents_active ON company_documents(is_active);
        """))
        
        # Image indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_company_images_company_id ON company_images(company_id);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_company_images_type ON company_images(image_type);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_company_images_active ON company_images(is_active);
        """))
        
        # Pricing rule indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_company_pricing_rules_company_id ON company_pricing_rules(company_id);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_company_pricing_rules_type ON company_pricing_rules(rule_type);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_company_pricing_rules_active ON company_pricing_rules(is_active);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_company_pricing_rules_priority ON company_pricing_rules(priority);
        """))
        
        conn.commit()
        
        print("✓ Indexes created successfully")


def downgrade():
    """Drop company-related tables"""
    print("Dropping company tables...")
    
    Base.metadata.drop_all(bind=engine, tables=[
        CompanyPricingRule.__table__,
        CompanyImage.__table__,
        CompanyDocument.__table__,
        Company.__table__
    ])
    
    print("✓ Company tables dropped successfully")


def seed_sample_data():
    """Seed sample company data for testing"""
    from sqlalchemy.orm import Session
    from backend.core.database import SessionLocal
    
    print("Seeding sample company data...")
    
    db = SessionLocal()
    
    try:
        # Create sample companies
        companies = [
            Company(
                name="solar-gmbh",
                display_name="Solar GmbH",
                email="info@solar-gmbh.de",
                phone="+49 123 456789",
                website="https://www.solar-gmbh.de",
                address_street="Sonnenstraße 1",
                address_city="München",
                address_postal_code="80331",
                address_country="Deutschland",
                tax_id="DE123456789",
                primary_color="#0066CC",
                secondary_color="#FF6600",
                accent_color="#00CC66",
                base_markup_percentage=0.0,
                price_increase_percentage=7.0,
                template_prefix="f1",
                is_active=True,
                is_default=True,
                sort_order=1
            ),
            Company(
                name="energie-plus",
                display_name="Energie Plus AG",
                email="kontakt@energie-plus.de",
                phone="+49 234 567890",
                website="https://www.energie-plus.de",
                address_street="Energieweg 10",
                address_city="Berlin",
                address_postal_code="10115",
                address_country="Deutschland",
                tax_id="DE234567890",
                primary_color="#FF6600",
                secondary_color="#0066CC",
                accent_color="#FFCC00",
                base_markup_percentage=5.0,
                price_increase_percentage=7.0,
                template_prefix="f2",
                is_active=True,
                is_default=False,
                sort_order=2
            ),
            Company(
                name="gruene-energie",
                display_name="Grüne Energie GmbH",
                email="info@gruene-energie.de",
                phone="+49 345 678901",
                website="https://www.gruene-energie.de",
                address_street="Ökostraße 5",
                address_city="Hamburg",
                address_postal_code="20095",
                address_country="Deutschland",
                tax_id="DE345678901",
                primary_color="#00CC66",
                secondary_color="#0066CC",
                accent_color="#FFCC00",
                base_markup_percentage=3.0,
                price_increase_percentage=7.0,
                template_prefix="f3",
                is_active=True,
                is_default=False,
                sort_order=3
            )
        ]
        
        for company in companies:
            db.add(company)
        
        db.commit()
        
        print(f"✓ Created {len(companies)} sample companies")
        
        # Create sample documents for first company
        sample_docs = [
            CompanyDocument(
                company_id=1,
                title="Produktdatenblatt PV-Module",
                description="Technische Daten der PV-Module",
                document_type="datasheet",
                file_path="/uploads/documents/pv_module_datasheet.pdf",
                file_name="pv_module_datasheet.pdf",
                include_in_pdf=True,
                pdf_page_number=7,
                is_active=True,
                sort_order=1
            ),
            CompanyDocument(
                company_id=1,
                title="Zertifikat TÜV",
                description="TÜV-Zertifizierung",
                document_type="certificate",
                file_path="/uploads/documents/tuv_certificate.pdf",
                file_name="tuv_certificate.pdf",
                include_in_pdf=True,
                pdf_page_number=8,
                is_active=True,
                sort_order=2
            )
        ]
        
        for doc in sample_docs:
            db.add(doc)
        
        db.commit()
        
        print(f"✓ Created {len(sample_docs)} sample documents")
        
        # Create sample pricing rules
        sample_rules = [
            CompanyPricingRule(
                company_id=1,
                rule_name="Mengenrabatt ab 20 Module",
                rule_type="global",
                discount_percentage=5.0,
                min_quantity=20,
                priority=10,
                is_active=True
            ),
            CompanyPricingRule(
                company_id=1,
                rule_name="Premium-Modul Aufschlag",
                rule_type="category",
                target_name="Premium PV-Module",
                markup_percentage=10.0,
                priority=5,
                is_active=True
            )
        ]
        
        for rule in sample_rules:
            db.add(rule)
        
        db.commit()
        
        print(f"✓ Created {len(sample_rules)} sample pricing rules")
        
        print("✓ Sample data seeded successfully")
        
    except Exception as e:
        print(f"✗ Error seeding sample data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "upgrade":
            upgrade()
        elif command == "downgrade":
            downgrade()
        elif command == "seed":
            seed_sample_data()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python -m backend.migrations.add_company_tables [upgrade|downgrade|seed]")
    else:
        # Default: run upgrade
        upgrade()
        
        # Ask if user wants to seed sample data
        response = input("\nDo you want to seed sample company data? (y/n): ")
        if response.lower() == 'y':
            seed_sample_data()
