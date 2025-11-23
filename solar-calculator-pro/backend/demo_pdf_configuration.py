"""
PDF Configuration System Demo
Demonstrates all features of the PDF configuration system
"""

from models.pdf_config_schemas import (
    PDFConfigurationRequest,
    PDFType,
    ComponentType,
    ColorScheme,
    FontFamily,
    PageConfig,
    ComponentConfig,
    CompanySelection,
    ProductRotationConfig,
    PriceIncreaseConfig,
    WatermarkConfig,
    LogoPosition
)
from services.pdf_configuration_service import PDFConfigurationService


def demo_standard_pv_pdf():
    """Demo: Standard PV PDF configuration"""
    print("\n=== Demo 1: Standard PV PDF ===\n")
    
    service = PDFConfigurationService()
    
    # Create standard PV configuration
    config = PDFConfigurationRequest(
        pdf_type=PDFType.STANDARD_PV,
        project_id=123,
        pages=[
            PageConfig(page_number=i, enabled=True, components=[])
            for i in range(1, 9)
        ],
        components=[],
        color_scheme=ColorScheme.BLUE,
        font_family=FontFamily.HELVETICA,
        font_size_base=10,
        include_3d_visualization=True,
        include_charts=True,
        include_calculations=True,
        compress_pdf=True
    )
    
    # Validate and create
    response = service.create_configuration(config)
    
    print(f"Configuration ID: {response.config_id}")
    print(f"PDF Type: {response.pdf_type}")
    print(f"Total Pages: {response.total_pages}")
    print(f"Enabled Pages: {response.enabled_pages}")
    print(f"Estimated Size: {response.estimated_size_mb} MB")
    print(f"Validation Errors: {response.validation_errors}")
    print(f"Validation Warnings: {response.validation_warnings}")


def demo_extended_pv_with_datasheets():
    """Demo: Extended PV PDF with datasheets"""
    print("\n=== Demo 2: Extended PV PDF with Datasheets ===\n")
    
    service = PDFConfigurationService()
    
    # Create extended PV configuration with extra pages
    pages = [
        PageConfig(page_number=i, enabled=True, components=[])
        for i in range(1, 9)
    ]
    
    # Add extra pages for datasheets
    pages.extend([
        PageConfig(
            page_number=9,
            enabled=True,
            components=['datasheet_pv_module'],
            custom_header='PV-Modul Datenblatt'
        ),
        PageConfig(
            page_number=10,
            enabled=True,
            components=['datasheet_inverter'],
            custom_header='Wechselrichter Datenblatt'
        ),
        PageConfig(
            page_number=11,
            enabled=True,
            components=['datasheet_battery'],
            custom_header='Batteriespeicher Datenblatt'
        )
    ])
    
    # Define components
    components = [
        ComponentConfig(
            component_id='datasheet_pv_module',
            component_type=ComponentType.DATASHEET,
            enabled=True,
            page=9,
            position={'x': 50, 'y': 100},
            data_source='product_pv_module_123'
        ),
        ComponentConfig(
            component_id='datasheet_inverter',
            component_type=ComponentType.DATASHEET,
            enabled=True,
            page=10,
            position={'x': 50, 'y': 100},
            data_source='product_inverter_456'
        ),
        ComponentConfig(
            component_id='datasheet_battery',
            component_type=ComponentType.DATASHEET,
            enabled=True,
            page=11,
            position={'x': 50, 'y': 100},
            data_source='product_battery_789'
        )
    ]
    
    config = PDFConfigurationRequest(
        pdf_type=PDFType.EXTENDED_PV,
        project_id=123,
        pages=pages,
        components=components,
        color_scheme=ColorScheme.GREEN,
        font_family=FontFamily.ARIAL,
        font_size_base=10,
        include_3d_visualization=True,
        include_charts=True,
        include_calculations=True,
        include_datasheets=True,
        compress_pdf=True
    )
    
    response = service.create_configuration(config)
    
    print(f"Configuration ID: {response.config_id}")
    print(f"Total Pages: {response.total_pages}")
    print(f"Enabled Pages: {response.enabled_pages}")
    print(f"Total Components: {response.total_components}")
    print(f"Enabled Components: {response.enabled_components}")
    print(f"Estimated Size: {response.estimated_size_mb} MB")


def demo_multi_pdf_with_rotation():
    """Demo: Multi-PDF with product rotation and price increase"""
    print("\n=== Demo 3: Multi-PDF with Product Rotation ===\n")
    
    service = PDFConfigurationService()
    
    # Define companies
    companies = [
        CompanySelection(
            company_id=1,
            company_name='Solar Solutions GmbH',
            logo_path='/logos/solar_solutions.png',
            color_scheme=ColorScheme.BLUE
        ),
        CompanySelection(
            company_id=2,
            company_name='Green Energy AG',
            logo_path='/logos/green_energy.png',
            color_scheme=ColorScheme.GREEN
        ),
        CompanySelection(
            company_id=3,
            company_name='Eco Power Systems',
            logo_path='/logos/eco_power.png',
            color_scheme=ColorScheme.ORANGE
        )
    ]
    
    # Configure product rotation
    product_rotation = ProductRotationConfig(
        enabled=True,
        avoid_duplicate_brands=True,
        avoid_duplicate_products=True,
        rotation_strategy='sequential',
        product_categories=['pv_modules', 'inverters', 'batteries']
    )
    
    # Configure price increase
    price_increase = PriceIncreaseConfig(
        enabled=True,
        increase_percentage=7.0,
        apply_to_base_price=True,
        compound_increases=True,
        min_price=10000.0,
        max_price=50000.0
    )
    
    config = PDFConfigurationRequest(
        pdf_type=PDFType.MULTI_PDF,
        project_id=123,
        pages=[
            PageConfig(page_number=i, enabled=True, components=[])
            for i in range(1, 9)
        ],
        components=[],
        companies=companies,
        product_rotation=product_rotation,
        price_increase=price_increase,
        color_scheme=ColorScheme.DEFAULT,
        font_family=FontFamily.HELVETICA,
        font_size_base=10,
        include_3d_visualization=True,
        include_charts=True,
        include_calculations=True,
        compress_pdf=True
    )
    
    response = service.create_configuration(config)
    
    print(f"Configuration ID: {response.config_id}")
    print(f"Number of Companies: {len(companies)}")
    print(f"Product Rotation: Enabled")
    print(f"Price Increase: {price_increase.increase_percentage}%")
    print(f"Estimated Total Size: {response.estimated_size_mb} MB")
    print(f"  (Size per company: {response.estimated_size_mb / len(companies):.2f} MB)")
    
    # Simulate price progression
    base_price = 16999.00
    print(f"\nPrice Progression:")
    for i, company in enumerate(companies):
        price = base_price * (1 + price_increase.increase_percentage / 100) ** i
        print(f"  {company.company_name}: {price:,.2f} €")


def demo_watermark_configuration():
    """Demo: PDF with watermark"""
    print("\n=== Demo 4: PDF with Watermark ===\n")
    
    service = PDFConfigurationService()
    
    # Configure watermark
    watermark = WatermarkConfig(
        enabled=True,
        text='ENTWURF',
        opacity=0.15,
        rotation=45.0,
        font_size=60,
        color='#CCCCCC'
    )
    
    config = PDFConfigurationRequest(
        pdf_type=PDFType.STANDARD_PV,
        project_id=123,
        pages=[
            PageConfig(page_number=i, enabled=True, components=[])
            for i in range(1, 9)
        ],
        components=[],
        watermark=watermark,
        color_scheme=ColorScheme.DEFAULT,
        font_family=FontFamily.HELVETICA,
        font_size_base=10,
        compress_pdf=True
    )
    
    response = service.create_configuration(config)
    
    print(f"Configuration ID: {response.config_id}")
    print(f"Watermark: {watermark.text}")
    print(f"Opacity: {watermark.opacity}")
    print(f"Rotation: {watermark.rotation}°")


def demo_custom_logo_positions():
    """Demo: Custom logo positions per page"""
    print("\n=== Demo 5: Custom Logo Positions ===\n")
    
    service = PDFConfigurationService()
    
    # Define logo positions for different pages
    logo_positions = {
        1: LogoPosition(x=50, y=50, width=150, height=50, page=1),
        2: LogoPosition(x=450, y=50, width=100, height=33, page=2),
        3: LogoPosition(x=250, y=750, width=100, height=33, page=3)
    }
    
    config = PDFConfigurationRequest(
        pdf_type=PDFType.STANDARD_PV,
        project_id=123,
        pages=[
            PageConfig(page_number=i, enabled=True, components=[])
            for i in range(1, 9)
        ],
        components=[],
        logo_positions=logo_positions,
        color_scheme=ColorScheme.DEFAULT,
        font_family=FontFamily.HELVETICA,
        font_size_base=10,
        compress_pdf=True
    )
    
    response = service.create_configuration(config)
    
    print(f"Configuration ID: {response.config_id}")
    print(f"Logo Positions:")
    for page, pos in logo_positions.items():
        print(f"  Page {page}: ({pos.x}, {pos.y}) - {pos.width}x{pos.height}pt")


def demo_validation_errors():
    """Demo: Configuration with validation errors"""
    print("\n=== Demo 6: Validation Errors ===\n")
    
    service = PDFConfigurationService()
    
    # Create invalid configuration (missing required pages)
    config = PDFConfigurationRequest(
        pdf_type=PDFType.STANDARD_PV,
        project_id=123,
        pages=[
            PageConfig(page_number=1, enabled=True, components=[]),
            PageConfig(page_number=2, enabled=True, components=[])
            # Missing pages 3-8!
        ],
        components=[],
        color_scheme=ColorScheme.DEFAULT,
        font_family=FontFamily.HELVETICA,
        font_size_base=10,
        compress_pdf=True
    )
    
    response = service.create_configuration(config)
    
    print(f"Configuration ID: {response.config_id}")
    print(f"\nValidation Errors:")
    for error in response.validation_errors:
        print(f"  ❌ {error}")
    
    print(f"\nValidation Warnings:")
    for warning in response.validation_warnings:
        print(f"  ⚠️  {warning}")


def demo_get_default_configuration():
    """Demo: Get default configuration for PDF type"""
    print("\n=== Demo 7: Default Configuration ===\n")
    
    service = PDFConfigurationService()
    
    for pdf_type in PDFType:
        config = service.get_default_configuration(pdf_type)
        print(f"{pdf_type.value}:")
        print(f"  Pages: {len(config.pages)}")
        print(f"  Components: {len(config.components)}")
        print()


def demo_configuration_lifecycle():
    """Demo: Complete configuration lifecycle"""
    print("\n=== Demo 8: Configuration Lifecycle ===\n")
    
    service = PDFConfigurationService()
    
    # 1. Create configuration
    print("1. Creating configuration...")
    config = PDFConfigurationRequest(
        pdf_type=PDFType.STANDARD_PV,
        project_id=123,
        pages=[
            PageConfig(page_number=i, enabled=True, components=[])
            for i in range(1, 9)
        ],
        components=[],
        color_scheme=ColorScheme.BLUE,
        font_family=FontFamily.HELVETICA,
        font_size_base=10,
        compress_pdf=True
    )
    
    response = service.create_configuration(config)
    config_id = response.config_id
    print(f"   Created: {config_id}")
    
    # 2. Get configuration
    print("\n2. Retrieving configuration...")
    retrieved = service.get_configuration(config_id)
    print(f"   Retrieved: {retrieved.pdf_type}")
    
    # 3. Update configuration
    print("\n3. Updating configuration...")
    config.color_scheme = ColorScheme.GREEN
    config.font_size_base = 12
    update_response = service.update_configuration(config_id, config)
    print(f"   Updated: Color scheme = {config.color_scheme}, Font size = {config.font_size_base}")
    
    # 4. List configurations
    print("\n4. Listing configurations...")
    list_result = service.list_configurations(page=1, page_size=10)
    print(f"   Total configurations: {list_result['total']}")
    
    # 5. Delete configuration
    print("\n5. Deleting configuration...")
    success = service.delete_configuration(config_id)
    print(f"   Deleted: {success}")


if __name__ == '__main__':
    print("=" * 60)
    print("PDF Configuration System - Comprehensive Demo")
    print("=" * 60)
    
    demo_standard_pv_pdf()
    demo_extended_pv_with_datasheets()
    demo_multi_pdf_with_rotation()
    demo_watermark_configuration()
    demo_custom_logo_positions()
    demo_validation_errors()
    demo_get_default_configuration()
    demo_configuration_lifecycle()
    
    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)
