"""
Demo Script for Company Database System

This script demonstrates how to use the company database system for multi-PDF generation.
Run this after setting up the database and running migrations.

Usage:
    python -m backend.demo_company_system
"""

from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.services.company_service import CompanyService
from backend.models.company_schemas import (
    CompanyCreate, CompanyUpdate,
    CompanyDocumentCreate, CompanyImageCreate,
    CompanyPricingRuleCreate
)


def demo_create_company(db: Session):
    """Demo: Create a new company"""
    print("\n" + "="*80)
    print("DEMO 1: Creating a New Company")
    print("="*80)
    
    service = CompanyService(db)
    
    company_data = CompanyCreate(
        name="demo-solar",
        display_name="Demo Solar GmbH",
        email="info@demo-solar.de",
        phone="+49 123 456789",
        website="https://www.demo-solar.de",
        address_street="Demostraße 123",
        address_city="Berlin",
        address_postal_code="10115",
        address_country="Deutschland",
        tax_id="DE999999999",
        primary_color="#0066CC",
        secondary_color="#FF6600",
        accent_color="#00CC66",
        base_markup_percentage=0.0,
        price_increase_percentage=7.0,
        template_prefix="f4",
        is_active=True,
        is_default=False,
        sort_order=10
    )
    
    company = service.create_company(company_data)
    
    print(f"\n✓ Created company:")
    print(f"  ID: {company.id}")
    print(f"  Name: {company.name}")
    print(f"  Display Name: {company.display_name}")
    print(f"  Email: {company.email}")
    print(f"  Primary Color: {company.primary_color}")
    print(f"  Template Prefix: {company.template_prefix}")
    print(f"  Price Increase: {company.price_increase_percentage}%")
    
    return company.id


def demo_list_companies(db: Session):
    """Demo: List all companies"""
    print("\n" + "="*80)
    print("DEMO 2: Listing All Companies")
    print("="*80)
    
    service = CompanyService(db)
    companies = service.get_companies(active_only=False)
    
    print(f"\n✓ Found {len(companies)} companies:")
    for company in companies:
        status = "✓ Active" if company.is_active else "✗ Inactive"
        default = " [DEFAULT]" if company.is_default else ""
        print(f"\n  {company.id}. {company.display_name}{default}")
        print(f"     Name: {company.name}")
        print(f"     Status: {status}")
        print(f"     Email: {company.email}")
        print(f"     Template: {company.template_prefix}")
        print(f"     Markup: {company.base_markup_percentage}%")
        print(f"     Price Increase: {company.price_increase_percentage}%")


def demo_add_documents(db: Session, company_id: int):
    """Demo: Add documents to a company"""
    print("\n" + "="*80)
    print("DEMO 3: Adding Documents to Company")
    print("="*80)
    
    service = CompanyService(db)
    
    documents = [
        CompanyDocumentCreate(
            company_id=company_id,
            title="PV-Module Datenblatt",
            description="Technische Spezifikationen der PV-Module",
            document_type="datasheet",
            file_path="/uploads/documents/pv_datasheet.pdf",
            file_name="pv_datasheet.pdf",
            include_in_pdf=True,
            pdf_page_number=7,
            tags=["pv", "module", "technical"],
            sort_order=1,
            is_active=True
        ),
        CompanyDocumentCreate(
            company_id=company_id,
            title="TÜV Zertifikat",
            description="TÜV-Zertifizierung für Qualitätssicherung",
            document_type="certificate",
            file_path="/uploads/documents/tuv_cert.pdf",
            file_name="tuv_cert.pdf",
            include_in_pdf=True,
            pdf_page_number=8,
            tags=["certificate", "tuv", "quality"],
            sort_order=2,
            is_active=True
        ),
        CompanyDocumentCreate(
            company_id=company_id,
            title="Produktbroschüre",
            description="Marketing-Broschüre mit allen Produkten",
            document_type="brochure",
            file_path="/uploads/documents/brochure.pdf",
            file_name="brochure.pdf",
            include_in_pdf=False,
            tags=["marketing", "products"],
            sort_order=3,
            is_active=True
        )
    ]
    
    print(f"\n✓ Adding {len(documents)} documents:")
    for doc_data in documents:
        doc = service.create_company_document(doc_data)
        include_status = "✓ Include in PDF" if doc.include_in_pdf else "✗ Not in PDF"
        print(f"\n  {doc.id}. {doc.title}")
        print(f"     Type: {doc.document_type}")
        print(f"     File: {doc.file_name}")
        print(f"     Status: {include_status}")
        if doc.include_in_pdf:
            print(f"     PDF Page: {doc.pdf_page_number}")
        print(f"     Tags: {', '.join(doc.tags)}")


def demo_add_images(db: Session, company_id: int):
    """Demo: Add images to a company"""
    print("\n" + "="*80)
    print("DEMO 4: Adding Images to Company")
    print("="*80)
    
    service = CompanyService(db)
    
    images = [
        CompanyImageCreate(
            company_id=company_id,
            title="PV-Module Produktfoto",
            description="Hochauflösendes Foto der PV-Module",
            image_type="product",
            file_path="/uploads/images/pv_module.jpg",
            file_name="pv_module.jpg",
            width=1920,
            height=1080,
            include_in_pdf=True,
            pdf_page_number=3,
            pdf_position_x=20.0,
            pdf_position_y=100.0,
            pdf_width=170.0,
            pdf_height=95.0,
            tags=["product", "pv", "module"],
            sort_order=1,
            is_active=True
        ),
        CompanyImageCreate(
            company_id=company_id,
            title="Firmengebäude",
            description="Foto des Firmengebäudes",
            image_type="facility",
            file_path="/uploads/images/facility.jpg",
            file_name="facility.jpg",
            width=1920,
            height=1080,
            include_in_pdf=True,
            pdf_page_number=8,
            pdf_position_x=20.0,
            pdf_position_y=200.0,
            pdf_width=80.0,
            pdf_height=60.0,
            tags=["facility", "building"],
            sort_order=2,
            is_active=True
        )
    ]
    
    print(f"\n✓ Adding {len(images)} images:")
    for img_data in images:
        img = service.create_company_image(img_data)
        include_status = "✓ Include in PDF" if img.include_in_pdf else "✗ Not in PDF"
        print(f"\n  {img.id}. {img.title}")
        print(f"     Type: {img.image_type}")
        print(f"     File: {img.file_name}")
        print(f"     Dimensions: {img.width}x{img.height}px")
        print(f"     Status: {include_status}")
        if img.include_in_pdf:
            print(f"     PDF Page: {img.pdf_page_number}")
            print(f"     PDF Size: {img.pdf_width}x{img.pdf_height}mm")
        print(f"     Tags: {', '.join(img.tags)}")


def demo_add_pricing_rules(db: Session, company_id: int):
    """Demo: Add pricing rules to a company"""
    print("\n" + "="*80)
    print("DEMO 5: Adding Pricing Rules to Company")
    print("="*80)
    
    service = CompanyService(db)
    
    rules = [
        CompanyPricingRuleCreate(
            company_id=company_id,
            rule_name="Mengenrabatt ab 20 Module",
            rule_type="global",
            discount_percentage=5.0,
            min_quantity=20,
            priority=10,
            is_active=True
        ),
        CompanyPricingRuleCreate(
            company_id=company_id,
            rule_name="Mengenrabatt ab 50 Module",
            rule_type="global",
            discount_percentage=10.0,
            min_quantity=50,
            priority=15,
            is_active=True
        ),
        CompanyPricingRuleCreate(
            company_id=company_id,
            rule_name="Premium-Module Aufschlag",
            rule_type="category",
            target_name="Premium PV-Module",
            markup_percentage=15.0,
            priority=5,
            is_active=True
        ),
        CompanyPricingRuleCreate(
            company_id=company_id,
            rule_name="Sommer-Aktion 2024",
            rule_type="global",
            discount_percentage=3.0,
            priority=20,
            is_active=False  # Not active yet
        )
    ]
    
    print(f"\n✓ Adding {len(rules)} pricing rules:")
    for rule_data in rules:
        rule = service.create_pricing_rule(rule_data)
        status = "✓ Active" if rule.is_active else "✗ Inactive"
        print(f"\n  {rule.id}. {rule.rule_name}")
        print(f"     Type: {rule.rule_type}")
        print(f"     Priority: {rule.priority}")
        print(f"     Status: {status}")
        
        if rule.markup_percentage > 0:
            print(f"     Markup: +{rule.markup_percentage}%")
        if rule.discount_percentage > 0:
            print(f"     Discount: -{rule.discount_percentage}%")
        if rule.min_quantity:
            print(f"     Min Quantity: {rule.min_quantity}")
        if rule.target_name:
            print(f"     Target: {rule.target_name}")


def demo_load_company_data(db: Session, company_id: int):
    """Demo: Load complete company data"""
    print("\n" + "="*80)
    print("DEMO 6: Loading Complete Company Data")
    print("="*80)
    
    service = CompanyService(db)
    data = service.load_company_data(company_id)
    
    print(f"\n✓ Loaded complete data for company {company_id}:")
    
    # Company info
    company = data['company']
    print(f"\n  Company Information:")
    print(f"    Name: {company.display_name}")
    print(f"    Email: {company.email}")
    print(f"    Phone: {company.phone}")
    print(f"    Website: {company.website}")
    
    # Branding
    branding = data['branding']
    print(f"\n  Branding:")
    print(f"    Logo: {branding['logo_path']}")
    print(f"    Logo Position: ({branding['logo_position']['x']}, {branding['logo_position']['y']}) mm")
    print(f"    Logo Size: {branding['logo_position']['width']}x{branding['logo_position']['height']} mm")
    print(f"    Primary Color: {branding['colors']['primary']}")
    print(f"    Secondary Color: {branding['colors']['secondary']}")
    print(f"    Accent Color: {branding['colors']['accent']}")
    
    # Pricing
    pricing = data['pricing']
    print(f"\n  Pricing:")
    print(f"    Base Markup: {pricing['base_markup']}%")
    print(f"    Price Increase (Multi-PDF): {pricing['price_increase']}%")
    
    # Template
    template = data['template']
    print(f"\n  Template:")
    print(f"    Prefix: {template['prefix']}")
    print(f"    Folder: {template['folder']}")
    
    # Documents
    documents = data['documents']
    print(f"\n  Documents: {len(documents)}")
    for doc in documents:
        print(f"    - {doc.title} ({doc.document_type})")
    
    # Images
    images = data['images']
    print(f"\n  Images: {len(images)}")
    for img in images:
        print(f"    - {img.title} ({img.image_type})")
    
    # Pricing Rules
    rules = data['pricing_rules']
    print(f"\n  Pricing Rules: {len(rules)}")
    for rule in rules:
        print(f"    - {rule.rule_name} (Priority: {rule.priority})")


def demo_multi_company_selection(db: Session):
    """Demo: Get companies for multi-PDF selection"""
    print("\n" + "="*80)
    print("DEMO 7: Multi-PDF Company Selection")
    print("="*80)
    
    service = CompanyService(db)
    companies = service.get_companies(active_only=True)
    
    print(f"\n✓ Available companies for multi-PDF generation:")
    print(f"  Total: {len(companies)} active companies")
    
    for i, company in enumerate(companies, 1):
        print(f"\n  [{i}] {company.display_name}")
        print(f"      Template: {company.template_prefix}")
        print(f"      Price Increase: {company.price_increase_percentage}%")
        print(f"      Documents: {len(company.documents)}")
        print(f"      Images: {len(company.images)}")
        print(f"      Pricing Rules: {len(company.pricing_rules)}")
    
    print(f"\n  💡 Select multiple companies to generate PDFs for all at once!")
    print(f"     Example: Select companies 1, 2, 3 → Generate 3 PDFs with one click")


def demo_update_company(db: Session, company_id: int):
    """Demo: Update company data"""
    print("\n" + "="*80)
    print("DEMO 8: Updating Company Data")
    print("="*80)
    
    service = CompanyService(db)
    
    # Get current data
    company = service.get_company(company_id)
    print(f"\n  Current data:")
    print(f"    Display Name: {company.display_name}")
    print(f"    Price Increase: {company.price_increase_percentage}%")
    print(f"    Primary Color: {company.primary_color}")
    
    # Update
    update_data = CompanyUpdate(
        display_name="Demo Solar GmbH (Updated)",
        price_increase_percentage=10.0,
        primary_color="#FF0000"
    )
    
    updated = service.update_company(company_id, update_data)
    
    print(f"\n  ✓ Updated data:")
    print(f"    Display Name: {updated.display_name}")
    print(f"    Price Increase: {updated.price_increase_percentage}%")
    print(f"    Primary Color: {updated.primary_color}")


def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("COMPANY DATABASE SYSTEM - DEMO")
    print("="*80)
    print("\nThis demo shows how to use the company database system for multi-PDF generation.")
    print("Make sure you have run the database migration first!")
    
    db = SessionLocal()
    
    try:
        # Demo 1: Create company
        company_id = demo_create_company(db)
        
        # Demo 2: List companies
        demo_list_companies(db)
        
        # Demo 3: Add documents
        demo_add_documents(db, company_id)
        
        # Demo 4: Add images
        demo_add_images(db, company_id)
        
        # Demo 5: Add pricing rules
        demo_add_pricing_rules(db, company_id)
        
        # Demo 6: Load complete data
        demo_load_company_data(db, company_id)
        
        # Demo 7: Multi-company selection
        demo_multi_company_selection(db)
        
        # Demo 8: Update company
        demo_update_company(db, company_id)
        
        print("\n" + "="*80)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\nNext steps:")
        print("  1. Explore the API endpoints at http://localhost:8000/docs")
        print("  2. Create your own companies via API or admin UI")
        print("  3. Upload logos, documents, and images")
        print("  4. Configure pricing rules")
        print("  5. Test multi-PDF generation")
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
