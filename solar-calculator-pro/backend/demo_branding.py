# backend/demo_branding.py

"""
Demo script for PDF Branding & Multi-Logo System
Demonstrates all features with practical examples
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from services.branding_service import BrandingService
from models.branding_schemas import (
    CompanyBrandingCreate,
    CompanyBrandingUpdate,
    LogoPositionCreate,
    BrandingTemplateCreate
)


def demo_basic_branding(db_session):
    """Demo 1: Basic branding setup"""
    print("\n" + "="*60)
    print("DEMO 1: Basic Branding Setup")
    print("="*60)
    
    service = BrandingService(db_session)
    
    # Create branding for company 1
    branding_data = CompanyBrandingCreate(
        company_id=1,
        logo_width=120.0,
        logo_height=60.0,
        logo_position_x=50.0,
        logo_position_y=750.0,
        primary_color="#0066CC",
        secondary_color="#003366",
        accent_color="#FF6600",
        text_color="#333333",
        background_color="#FFFFFF",
        font_family="Helvetica",
        font_size_base=10,
        font_size_heading=16,
        header_enabled=True,
        header_text="Solar Solutions GmbH",
        header_height=80.0,
        header_logo_enabled=True,
        footer_enabled=True,
        footer_text="www.solar-solutions.de | info@solar-solutions.de",
        footer_page_numbers=True,
        watermark_enabled=False
    )
    
    branding = service.create_branding(branding_data)
    print(f" Created branding ID: {branding.id}")
    print(f"   Company ID: {branding.company_id}")
    print(f"   Primary Color: {branding.primary_color}")
    print(f"   Font: {branding.font_family}")
    print(f"   Header: {branding.header_text}")
    
    return branding.id


def demo_logo_positions(db_session, branding_id):
    """Demo 2: Multiple logo positions"""
    print("\n" + "="*60)
    print("DEMO 2: Multiple Logo Positions")
    print("="*60)
    
    service = BrandingService(db_session)
    
    # Header logo (all pages)
    header_position = LogoPositionCreate(
        page_number=None,  # All pages
        context="header",
        x=50.0,
        y=750.0,
        width=120.0,
        height=60.0,
        opacity=1.0,
        rotation=0.0,
        scale=1.0
    )
    pos1 = service.add_logo_position(branding_id, header_position)
    print(f" Added header logo position ID: {pos1.id}")
    print(f"   Position: ({pos1.x}, {pos1.y})")
    print(f"   Size: {pos1.width}x{pos1.height}")
    
    # Footer logo (smaller, all pages)
    footer_position = LogoPositionCreate(
        page_number=None,
        context="footer",
        x=500.0,
        y=30.0,
        width=80.0,
        height=40.0,
        opacity=0.7,
        rotation=0.0,
        scale=1.0
    )
    pos2 = service.add_logo_position(branding_id, footer_position)
    print(f" Added footer logo position ID: {pos2.id}")
    print(f"   Position: ({pos2.x}, {pos2.y})")
    print(f"   Opacity: {pos2.opacity}")
    
    # Watermark logo (rotated, page 1 only)
    watermark_position = LogoPositionCreate(
        page_number=1,
        context="watermark",
        x=200.0,
        y=400.0,
        width=200.0,
        height=100.0,
        opacity=0.1,
        rotation=45.0,
        scale=1.5
    )
    pos3 = service.add_logo_position(branding_id, watermark_position)
    print(f" Added watermark logo position ID: {pos3.id}")
    print(f"   Rotation: {pos3.rotation}°")
    print(f"   Scale: {pos3.scale}x")


def demo_color_scheme(db_session, branding_id):
    """Demo 3: Color scheme application"""
    print("\n" + "="*60)
    print("DEMO 3: Color Scheme Application")
    print("="*60)
    
    service = BrandingService(db_session)
    
    # Get color scheme
    colors = {
        "primary": service.get_color(branding_id, "primary"),
        "secondary": service.get_color(branding_id, "secondary"),
        "accent": service.get_color(branding_id, "accent"),
        "text": service.get_color(branding_id, "text"),
        "background": service.get_color(branding_id, "background"),
        "header": service.get_color(branding_id, "header"),
        "footer": service.get_color(branding_id, "footer")
    }
    
    print(" Color Scheme:")
    for name, color in colors.items():
        print(f"   {name.capitalize()}: {color}")


def demo_watermark(db_session, branding_id):
    """Demo 4: Watermark configuration"""
    print("\n" + "="*60)
    print("DEMO 4: Watermark Configuration")
    print("="*60)
    
    service = BrandingService(db_session)
    
    # Update branding with watermark
    update_data = CompanyBrandingUpdate(
        watermark_enabled=True,
        watermark_text="VERTRAULICH",
        watermark_opacity=0.1,
        watermark_rotation=45.0,
        watermark_font_size=60,
        watermark_color="#CCCCCC"
    )
    
    branding = service.update_branding(branding_id, update_data)
    print(f" Watermark enabled")
    print(f"   Text: {branding.watermark_text}")
    print(f"   Opacity: {branding.watermark_opacity}")
    print(f"   Rotation: {branding.watermark_rotation}°")
    print(f"   Font Size: {branding.watermark_font_size}pt")


def demo_template_system(db_session):
    """Demo 5: Template system"""
    print("\n" + "="*60)
    print("DEMO 5: Template System")
    print("="*60)
    
    service = BrandingService(db_session)
    
    # Create template
    template_data = BrandingTemplateCreate(
        name="Modern Blue Theme",
        description="Professional blue color scheme with modern fonts",
        config={
            "primary_color": "#0066CC",
            "secondary_color": "#003366",
            "accent_color": "#FF6600",
            "text_color": "#333333",
            "background_color": "#FFFFFF",
            "font_family": "Helvetica",
            "font_size_base": 10,
            "font_size_heading": 16,
            "font_size_subheading": 12,
            "header_enabled": True,
            "header_height": 80.0,
            "footer_enabled": True,
            "footer_page_numbers": True,
            "watermark_enabled": False
        },
        is_public=True
    )
    
    template = service.create_template(template_data)
    print(f" Created template ID: {template.id}")
    print(f"   Name: {template.name}")
    print(f"   Description: {template.description}")
    print(f"   Public: {template.is_public}")
    
    # List templates
    templates = service.list_templates(public_only=True)
    print(f"\n Available templates: {len(templates)}")
    for t in templates:
        print(f"   - {t.name}")
    
    return template.id


def demo_pdf_generation(db_session, branding_id):
    """Demo 6: PDF generation with branding"""
    print("\n" + "="*60)
    print("DEMO 6: PDF Generation with Branding")
    print("="*60)
    
    service = BrandingService(db_session)
    
    # Create PDF
    output_file = "demo_branding_output.pdf"
    pdf_canvas = canvas.Canvas(output_file, pagesize=A4)
    page_width, page_height = A4
    
    # Generate 3 pages
    total_pages = 3
    for page_num in range(1, total_pages + 1):
        print(f"\n   Generating page {page_num}...")
        
        # Apply color scheme
        service.apply_color_scheme(pdf_canvas, branding_id)
        
        # Apply header
        service.apply_header(pdf_canvas, branding_id, page_num)
        print(f"    Applied header")
        
        # Apply footer
        service.apply_footer(pdf_canvas, branding_id, page_num, total_pages)
        print(f"    Applied footer")
        
        # Apply watermark
        service.apply_watermark(pdf_canvas, branding_id)
        print(f"    Applied watermark")
        
        # Apply logo positioning
        service.apply_logo_positioning(pdf_canvas, branding_id, page_num, "header")
        print(f"    Applied logo positioning")
        
        # Add page content
        service.apply_font_settings(pdf_canvas, branding_id, "heading")
        pdf_canvas.drawString(100, 650, f"Seite {page_num} - Demo Inhalt")
        
        service.apply_font_settings(pdf_canvas, branding_id, "base")
        pdf_canvas.drawString(100, 600, "Dies ist ein Beispieltext mit Firmen-Branding.")
        pdf_canvas.drawString(100, 580, "Alle Farben, Schriften und Logos werden automatisch angewendet.")
        
        # Next page
        if page_num < total_pages:
            pdf_canvas.showPage()
    
    # Save PDF
    pdf_canvas.save()
    print(f"\n PDF generated: {output_file}")
    print(f"   Pages: {total_pages}")
    print(f"   Size: {Path(output_file).stat().st_size / 1024:.2f} KB")


def demo_multi_company(db_session):
    """Demo 7: Multi-company PDF generation"""
    print("\n" + "="*60)
    print("DEMO 7: Multi-Company PDF Generation")
    print("="*60)
    
    service = BrandingService(db_session)
    
    # Create brandings for 3 companies
    companies = [
        {
            "id": 2,
            "name": "Green Energy AG",
            "color": "#00AA00",
            "header": "Green Energy AG - Nachhaltige Lösungen"
        },
        {
            "id": 3,
            "name": "Solar Power GmbH",
            "color": "#FF9900",
            "header": "Solar Power GmbH - Ihre Energiezukunft"
        },
        {
            "id": 4,
            "name": "Eco Solutions",
            "color": "#0099CC",
            "header": "Eco Solutions - Umweltfreundlich & Effizient"
        }
    ]
    
    branding_ids = []
    
    for company in companies:
        branding_data = CompanyBrandingCreate(
            company_id=company["id"],
            primary_color=company["color"],
            font_family="Helvetica",
            header_enabled=True,
            header_text=company["header"],
            footer_enabled=True,
            footer_page_numbers=True
        )
        
        branding = service.create_branding(branding_data)
        branding_ids.append(branding.id)
        print(f" Created branding for {company['name']}")
        print(f"   ID: {branding.id}, Color: {company['color']}")
    
    # Generate PDF for each company
    for i, branding_id in enumerate(branding_ids):
        company = companies[i]
        output_file = f"demo_company_{company['id']}.pdf"
        
        pdf_canvas = canvas.Canvas(output_file, pagesize=A4)
        
        # Single page per company
        service.apply_header(pdf_canvas, branding_id, 1)
        service.apply_footer(pdf_canvas, branding_id, 1, 1)
        
        service.apply_font_settings(pdf_canvas, branding_id, "heading")
        pdf_canvas.drawString(100, 650, company["name"])
        
        service.apply_font_settings(pdf_canvas, branding_id, "base")
        pdf_canvas.drawString(100, 600, f"Firmen-spezifisches Branding mit Farbe {company['color']}")
        
        pdf_canvas.save()
        print(f"    Generated PDF: {output_file}")
    
    print(f"\n Generated {len(companies)} company-specific PDFs")


def demo_yml_coordinates(db_session, branding_id):
    """Demo 8: YML coordinates integration"""
    print("\n" + "="*60)
    print("DEMO 8: YML Coordinates Integration")
    print("="*60)
    
    service = BrandingService(db_session)
    
    # Try to load YML coordinates for page 1
    try:
        coordinates = service.load_yml_coordinates(branding_id, page_number=1)
        
        if coordinates:
            print(f" Loaded YML coordinates for page 1")
            print(f"   Keys: {list(coordinates.keys())}")
            
            # Show some coordinates
            for key in list(coordinates.keys())[:5]:
                coord = coordinates[key]
                if isinstance(coord, dict):
                    print(f"   {key}: x={coord.get('x')}, y={coord.get('y')}")
        else:
            print("ℹ  No YML coordinates found (file may not exist)")
            print("   This is normal if coords/seite1.yml doesn't exist yet")
    except Exception as e:
        print(f"ℹ  Could not load YML coordinates: {e}")
        print("   This is expected if the coords/ folder doesn't exist yet")


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("PDF BRANDING & MULTI-LOGO SYSTEM - DEMO")
    print("="*60)
    print("\nThis demo showcases all features of the branding system:")
    print("1. Basic branding setup")
    print("2. Multiple logo positions")
    print("3. Color scheme application")
    print("4. Watermark configuration")
    print("5. Template system")
    print("6. PDF generation with branding")
    print("7. Multi-company PDF generation")
    print("8. YML coordinates integration")
    
    # Setup database
    engine = create_engine('sqlite:///./demo_branding.db')
    Session = sessionmaker(bind=engine)
    db_session = Session()
    
    try:
        # Run demos
        branding_id = demo_basic_branding(db_session)
        demo_logo_positions(db_session, branding_id)
        demo_color_scheme(db_session, branding_id)
        demo_watermark(db_session, branding_id)
        template_id = demo_template_system(db_session)
        demo_pdf_generation(db_session, branding_id)
        demo_multi_company(db_session)
        demo_yml_coordinates(db_session, branding_id)
        
        print("\n" + "="*60)
        print(" ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nGenerated files:")
        print("  - demo_branding_output.pdf (3 pages with full branding)")
        print("  - demo_company_2.pdf (Green Energy AG)")
        print("  - demo_company_3.pdf (Solar Power GmbH)")
        print("  - demo_company_4.pdf (Eco Solutions)")
        print("\nDatabase:")
        print("  - demo_branding.db (SQLite database with all branding data)")
        print("\nNext steps:")
        print("  1. Review generated PDFs")
        print("  2. Check database content")
        print("  3. Explore API endpoints at /docs")
        print("  4. Read PDF_BRANDING_GUIDE.md for detailed documentation")
        
    except Exception as e:
        print(f"\n Error during demo: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db_session.close()


if __name__ == "__main__":
    main()
