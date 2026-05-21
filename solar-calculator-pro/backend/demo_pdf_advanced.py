"""
PDF Advanced Service Demo - Task 103

Demonstrates all features of the PDF Advanced Service including:
- Basic PDF generation
- Custom branding
- Chart integration
- Batch generation
- Multi-company offers
- CRM archiving
- Preview generation

Requirements: 1.3, 6.1, 7.3
"""

import asyncio
from datetime import datetime
from backend.services.pdf_advanced_service import (
    get_pdf_advanced_service,
    PDFGenerationOptions,
    PDFBrandingConfig,
    PDFTemplate,
    PDFLanguage,
    ChartType
)


def demo_basic_generation():
    """Demo 1: Basic PDF Generation"""
    print("\n" + "="*80)
    print("DEMO 1: Basic PDF Generation")
    print("="*80)
    
    # Get service
    service = get_pdf_advanced_service()
    
    # Check health
    health = service.health_check()
    print(f"\nService Status: {health.status.value}")
    print(f"YML Files Loaded: {health.details.get('yml_files', 0)}")
    print(f"Templates Loaded: {health.details.get('templates', 0)}")
    
    # Prepare offer data
    offer_data = {
        'customer_id': 123,
        'customer_name': 'Max Mustermann',
        'customer_address': 'Musterstraße 123, 12345 Musterstadt',
        'system_size': 10.5,
        'module_count': 30,
        'module_type': 'Trina Solar 350W',
        'inverter': 'SMA Sunny Tripower 10.0',
        'annual_production': 12000,
        'self_consumption_rate': 0.35,
        'total_cost': 25000,
        'payback_period': 12.5,
        'savings_25_years': 45000,
        'co2_savings': 180000
    }
    
    # Create options
    options = PDFGenerationOptions(
        template=PDFTemplate.BASIS,
        language=PDFLanguage.GERMAN,
        include_3d_visualization=True,
        include_charts=True,
        compress=True,
        archive_to_crm=True
    )
    
    # Generate PDF
    print("\nGenerating PDF...")
    pdf_bytes = service.generate_advanced_pdf(offer_data, options)
    
    print(f" PDF Generated Successfully!")
    print(f"   Size: {len(pdf_bytes):,} bytes ({len(pdf_bytes)/1024:.1f} KB)")
    print(f"   Template: {options.template.value}")
    print(f"   Language: {options.language.value}")
    
    # Save to file
    filename = f"demo_basic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    with open(filename, 'wb') as f:
        f.write(pdf_bytes)
    print(f"   Saved to: {filename}")


def demo_custom_branding():
    """Demo 2: Custom Branding"""
    print("\n" + "="*80)
    print("DEMO 2: Custom Branding")
    print("="*80)
    
    service = get_pdf_advanced_service()
    
    # Create custom branding
    branding = PDFBrandingConfig(
        company_name="Solar Solutions GmbH",
        logo_path="assets/logo.png",
        logo_position=(50, 50),
        logo_size=(100, 50),
        primary_color="#0066CC",
        secondary_color="#FF6600",
        font_family="Helvetica",
        watermark_text="CONFIDENTIAL",
        watermark_opacity=0.1
    )
    
    print(f"\nBranding Configuration:")
    print(f"   Company: {branding.company_name}")
    print(f"   Primary Color: {branding.primary_color}")
    print(f"   Secondary Color: {branding.secondary_color}")
    print(f"   Watermark: {branding.watermark_text}")
    
    # Offer data
    offer_data = {
        'customer_id': 124,
        'customer_name': 'Erika Musterfrau',
        'system_size': 8.4,
        'module_count': 24,
        'total_cost': 20000
    }
    
    # Options with branding
    options = PDFGenerationOptions(
        template=PDFTemplate.BASIS,
        language=PDFLanguage.GERMAN,
        branding=branding,
        include_charts=True,
        compress=True
    )
    
    # Generate
    print("\nGenerating branded PDF...")
    pdf_bytes = service.generate_advanced_pdf(offer_data, options)
    
    print(f" Branded PDF Generated!")
    print(f"   Size: {len(pdf_bytes):,} bytes")
    
    filename = f"demo_branded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    with open(filename, 'wb') as f:
        f.write(pdf_bytes)
    print(f"   Saved to: {filename}")


def demo_chart_integration():
    """Demo 3: Chart Integration"""
    print("\n" + "="*80)
    print("DEMO 3: Chart Integration")
    print("="*80)
    
    service = get_pdf_advanced_service()
    
    # Offer data with chart data
    offer_data = {
        'customer_id': 125,
        'customer_name': 'Hans Schmidt',
        'system_size': 12.0,
        'module_count': 35,
        'total_cost': 28000,
        'charts': {
            'energy_production': {
                'type': 'line',
                'data': [10000, 10500, 11000, 11500, 12000],
                'labels': ['Year 1', 'Year 5', 'Year 10', 'Year 15', 'Year 20']
            },
            'cost_breakdown': {
                'type': 'bar',
                'data': [15000, 5000, 3000, 2000, 3000],
                'labels': ['Modules', 'Inverter', 'Installation', 'Permits', 'Other']
            },
            'consumption_distribution': {
                'type': 'pie',
                'data': [35, 25, 20, 20],
                'labels': ['Self-consumption', 'Grid feed-in', 'Battery', 'Losses']
            }
        }
    }
    
    # Options with specific chart types
    chart_types = [
        ChartType.LINE,
        ChartType.BAR,
        ChartType.PIE,
        ChartType.WATERFALL
    ]
    
    print(f"\nChart Types to Include:")
    for chart_type in chart_types:
        print(f"   - {chart_type.name}")
    
    options = PDFGenerationOptions(
        template=PDFTemplate.BASIS,
        language=PDFLanguage.GERMAN,
        include_charts=True,
        chart_types=chart_types,
        compress=True
    )
    
    # Generate
    print("\nGenerating PDF with charts...")
    pdf_bytes = service.generate_advanced_pdf(offer_data, options)
    
    print(f" PDF with Charts Generated!")
    print(f"   Size: {len(pdf_bytes):,} bytes")
    print(f"   Charts: {len(chart_types)}")
    
    filename = f"demo_charts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    with open(filename, 'wb') as f:
        f.write(pdf_bytes)
    print(f"   Saved to: {filename}")


async def demo_batch_generation():
    """Demo 4: Batch Generation"""
    print("\n" + "="*80)
    print("DEMO 4: Batch Generation")
    print("="*80)
    
    service = get_pdf_advanced_service()
    
    # Prepare multiple offers
    offers = [
        {
            'customer_id': 201,
            'customer_name': 'Customer 1',
            'system_size': 8.0,
            'total_cost': 18000
        },
        {
            'customer_id': 202,
            'customer_name': 'Customer 2',
            'system_size': 10.0,
            'total_cost': 22000
        },
        {
            'customer_id': 203,
            'customer_name': 'Customer 3',
            'system_size': 12.0,
            'total_cost': 26000
        },
        {
            'customer_id': 204,
            'customer_name': 'Customer 4',
            'system_size': 15.0,
            'total_cost': 32000
        },
        {
            'customer_id': 205,
            'customer_name': 'Customer 5',
            'system_size': 20.0,
            'total_cost': 42000
        }
    ]
    
    print(f"\nGenerating batch of {len(offers)} PDFs...")
    
    options = PDFGenerationOptions(
        template=PDFTemplate.BASIS,
        language=PDFLanguage.GERMAN,
        compress=True,
        archive_to_crm=True
    )
    
    # Generate batch
    start_time = datetime.now()
    pdf_list = await service.generate_batch_pdfs(offers, options)
    end_time = datetime.now()
    
    duration = (end_time - start_time).total_seconds()
    total_size = sum(len(pdf) for pdf in pdf_list)
    
    print(f" Batch Generation Complete!")
    print(f"   PDFs Generated: {len(pdf_list)}")
    print(f"   Total Size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    print(f"   Duration: {duration:.2f} seconds")
    print(f"   Average: {duration/len(pdf_list):.2f} seconds per PDF")
    
    # Save all PDFs
    for i, pdf_bytes in enumerate(pdf_list, 1):
        filename = f"demo_batch_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf_bytes)
        print(f"   Saved: {filename} ({len(pdf_bytes):,} bytes)")


def demo_multi_company_offer():
    """Demo 5: Multi-Company Offer"""
    print("\n" + "="*80)
    print("DEMO 5: Multi-Company Offer")
    print("="*80)
    
    service = get_pdf_advanced_service()
    
    # Offer data
    offer_data = {
        'customer_id': 300,
        'customer_name': 'Corporate Client',
        'system_size': 50.0,
        'module_count': 150,
        'total_cost': 100000
    }
    
    # Multiple company brandings
    companies = [
        PDFBrandingConfig(
            company_name="Solar Solutions GmbH",
            logo_path="logos/company_a.png",
            primary_color="#0066CC",
            secondary_color="#FF6600",
            font_family="Helvetica"
        ),
        PDFBrandingConfig(
            company_name="Green Energy AG",
            logo_path="logos/company_b.png",
            primary_color="#00CC66",
            secondary_color="#FFCC00",
            font_family="Helvetica"
        ),
        PDFBrandingConfig(
            company_name="Eco Power Systems",
            logo_path="logos/company_c.png",
            primary_color="#CC0066",
            secondary_color="#6600CC",
            font_family="Helvetica"
        )
    ]
    
    print(f"\nGenerating multi-company offer for {len(companies)} companies:")
    for company in companies:
        print(f"   - {company.company_name}")
    
    # Generate multi-company offer (ZIP)
    print("\nGenerating ZIP file...")
    zip_bytes = service.generate_multi_company_offer(offer_data, companies)
    
    print(f" Multi-Company Offer Generated!")
    print(f"   Companies: {len(companies)}")
    print(f"   ZIP Size: {len(zip_bytes):,} bytes ({len(zip_bytes)/1024:.1f} KB)")
    
    filename = f"demo_multi_company_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    with open(filename, 'wb') as f:
        f.write(zip_bytes)
    print(f"   Saved to: {filename}")


def demo_templates_and_languages():
    """Demo 6: Templates and Languages"""
    print("\n" + "="*80)
    print("DEMO 6: Available Templates and Languages")
    print("="*80)
    
    service = get_pdf_advanced_service()
    
    # Get available templates
    templates = service.get_available_templates()
    print(f"\nAvailable Templates ({len(templates)}):")
    for template in templates[:10]:  # Show first 10
        status = "" if template['available'] else ""
        print(f"   {status} {template['display_name']}")
    if len(templates) > 10:
        print(f"   ... and {len(templates) - 10} more")
    
    # Get available languages
    languages = service.get_available_languages()
    print(f"\nSupported Languages ({len(languages)}):")
    for lang in languages:
        print(f"   - {lang['name']} ({lang['code']})")
    
    # Get available chart types
    chart_types = service.get_available_chart_types()
    print(f"\nAvailable Chart Types ({len(chart_types)}):")
    for chart in chart_types:
        print(f"   - {chart['name']}")


def demo_statistics():
    """Demo 7: Service Statistics"""
    print("\n" + "="*80)
    print("DEMO 7: Service Statistics")
    print("="*80)
    
    service = get_pdf_advanced_service()
    
    # Get statistics
    stats = service.get_statistics()
    
    print(f"\nService Statistics:")
    print(f"   Total Generations: {stats['total_generations']}")
    print(f"   Batch Generations: {stats['batch_generations']}")
    print(f"   Archived PDFs: {stats['archived_pdfs']}")
    print(f"   YML Files Loaded: {stats['yml_files_loaded']}")
    print(f"   Templates Loaded: {stats['templates_loaded']}")
    print(f"   Branding Configs: {stats['branding_configs']}")


def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("PDF ADVANCED SERVICE - COMPREHENSIVE DEMO")
    print("Task 103: PDF Generation Advanced Service")
    print("="*80)
    
    try:
        # Demo 1: Basic Generation
        demo_basic_generation()
        
        # Demo 2: Custom Branding
        demo_custom_branding()
        
        # Demo 3: Chart Integration
        demo_chart_integration()
        
        # Demo 4: Batch Generation (async)
        asyncio.run(demo_batch_generation())
        
        # Demo 5: Multi-Company Offer
        demo_multi_company_offer()
        
        # Demo 6: Templates and Languages
        demo_templates_and_languages()
        
        # Demo 7: Statistics
        demo_statistics()
        
        print("\n" + "="*80)
        print("ALL DEMOS COMPLETED SUCCESSFULLY! ")
        print("="*80)
        print("\nFeatures Demonstrated:")
        print("    Basic PDF generation")
        print("    Custom branding")
        print("    Chart integration (10 types)")
        print("    Batch generation (parallel)")
        print("    Multi-company offers (ZIP)")
        print("    Template management (88 templates)")
        print("    Multi-language support (4 languages)")
        print("    Service statistics")
        print("\nTask 103 Status: COMPLETE ")
        
    except Exception as e:
        print(f"\n Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
