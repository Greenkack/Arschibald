"""
Demo script for Multi-PDF Template & Koordinaten System

This script demonstrates how to use the MultiPDFTemplateService to:
- Discover available companies
- Load templates and coordinates
- Validate company data
- Batch process multiple companies

Requirements: 1.3, 6.1, 7.3
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from services.multi_pdf_template_service import MultiPDFTemplateService
import json


def print_section(title: str):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_discover_companies():
    """Demo: Discover available companies"""
    print_section("1. Discover Available Companies")
    
    service = MultiPDFTemplateService()
    companies = service.discover_companies()
    
    print(f"Found {len(companies)} companies:")
    for company_id in companies:
        print(f"  - Company {company_id}")
    
    return service, companies


def demo_company_summary(service: MultiPDFTemplateService, company_id: int):
    """Demo: Get company summary"""
    print_section(f"2. Company {company_id} Summary")
    
    summary = service.get_company_summary(company_id)
    
    print(f"Company ID: {summary['company_id']}")
    print(f"\nTemplates:")
    print(f"  Total: {summary['templates']['total']}")
    print(f"  Existing: {summary['templates']['existing']}")
    print(f"  Missing: {summary['templates']['missing']}")
    print(f"  Valid: {summary['templates']['valid']}")
    print(f"  Total Size: {summary['templates']['total_size_bytes']:,} bytes")
    
    if summary['templates']['missing_files']:
        print(f"\n  Missing template files:")
        for file in summary['templates']['missing_files']:
            print(f"    - {file}")
    
    print(f"\nCoordinates:")
    print(f"  Total: {summary['coordinates']['total']}")
    print(f"  Existing: {summary['coordinates']['existing']}")
    print(f"  Missing: {summary['coordinates']['missing']}")
    print(f"  Valid: {summary['coordinates']['valid']}")
    
    if summary['coordinates']['missing_files']:
        print(f"\n  Missing coordinate files:")
        for file in summary['coordinates']['missing_files']:
            print(f"    - {file}")
    
    print(f"\nReady for PDF Generation: {summary['ready_for_generation']}")


def demo_template_details(service: MultiPDFTemplateService, company_id: int):
    """Demo: Get template details"""
    print_section(f"3. Template Details for Company {company_id}")
    
    templates = service.get_all_templates_for_company(company_id, pages=8)
    
    print(f"Templates for Company {company_id}:")
    for template in templates:
        status = "✓" if template.exists else "✗"
        size = f"{template.file_size:,} bytes" if template.file_size else "N/A"
        print(f"  {status} Page {template.page_number}: {template.file_path.name} ({size})")


def demo_coordinate_details(service: MultiPDFTemplateService, company_id: int):
    """Demo: Get coordinate details"""
    print_section(f"4. Coordinate Details for Company {company_id}")
    
    coordinates = service.get_all_coordinates_for_company(company_id, pages=8)
    
    print(f"Coordinates for Company {company_id}:")
    for coord in coordinates:
        status = "✓" if coord.exists else "✗"
        num_coords = len(coord.coordinates) if coord.coordinates else 0
        print(f"  {status} Page {coord.page_number}: {coord.file_path.name} ({num_coords} elements)")


def demo_load_specific_coordinate(service: MultiPDFTemplateService, company_id: int, page: int):
    """Demo: Load specific coordinate file"""
    print_section(f"5. Load Coordinates for Company {company_id}, Page {page}")
    
    coordinates = service.load_coordinates(company_id, page)
    
    if coordinates:
        print(f"Loaded coordinates from: {service.get_coordinate_path(company_id, page)}")
        print(f"\nCoordinate elements:")
        for key, value in coordinates.items():
            print(f"  {key}:")
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key}: {sub_value}")
            else:
                print(f"    {value}")
    else:
        print(f"Could not load coordinates for company {company_id}, page {page}")


def demo_validation(service: MultiPDFTemplateService, company_id: int):
    """Demo: Validate company data"""
    print_section(f"6. Validation for Company {company_id}")
    
    # Validate templates
    templates_valid, templates_missing = service.validate_company_templates(company_id, pages=8)
    print(f"Templates Validation:")
    print(f"  Valid: {templates_valid}")
    if not templates_valid:
        print(f"  Missing {len(templates_missing)} files:")
        for file in templates_missing:
            print(f"    - {file}")
    
    # Validate coordinates
    coords_valid, coords_missing = service.validate_company_coordinates(company_id, pages=8)
    print(f"\nCoordinates Validation:")
    print(f"  Valid: {coords_valid}")
    if not coords_valid:
        print(f"  Missing {len(coords_missing)} files:")
        for file in coords_missing:
            print(f"    - {file}")
    
    print(f"\nOverall Status: {'✓ Ready' if (templates_valid and coords_valid) else '✗ Not Ready'}")


def demo_batch_operations(service: MultiPDFTemplateService, company_ids: list):
    """Demo: Batch operations"""
    print_section("7. Batch Operations")
    
    print(f"Loading templates for companies: {company_ids}")
    templates = service.batch_load_templates(company_ids, pages=3)
    
    print(f"\nLoaded templates:")
    for company_id, pages in templates.items():
        loaded_count = sum(1 for content in pages.values() if content is not None)
        print(f"  Company {company_id}: {loaded_count}/3 pages loaded")
    
    print(f"\nLoading coordinates for companies: {company_ids}")
    coordinates = service.batch_load_coordinates(company_ids, pages=3)
    
    print(f"\nLoaded coordinates:")
    for company_id, pages in coordinates.items():
        loaded_count = sum(1 for coords in pages.values() if coords is not None)
        print(f"  Company {company_id}: {loaded_count}/3 pages loaded")


def demo_all_companies_summary(service: MultiPDFTemplateService):
    """Demo: Get summary for all companies"""
    print_section("8. All Companies Summary")
    
    summary = service.get_all_companies_summary()
    
    print(f"Total Companies: {summary['total_companies']}")
    print(f"Companies Ready: {summary['companies_ready']}")
    print(f"Companies with Issues: {summary['companies_with_issues']}")
    print(f"\nCompany IDs: {summary['company_ids']}")
    
    print(f"\nDetailed Status:")
    for company_id, details in summary['details'].items():
        status = "✓ Ready" if details['ready_for_generation'] else "✗ Not Ready"
        print(f"  Company {company_id}: {status}")
        print(f"    Templates: {details['templates']['existing']}/{details['templates']['total']}")
        print(f"    Coordinates: {details['coordinates']['existing']}/{details['coordinates']['total']}")


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("  Multi-PDF Template & Koordinaten System - Demo")
    print("=" * 80)
    
    try:
        # 1. Discover companies
        service, companies = demo_discover_companies()
        
        if not companies:
            print("\n⚠ No companies found!")
            print("Make sure the following directories exist and contain files:")
            print(f"  - {service.template_base_dir}")
            print(f"  - {service.coordinate_base_dir}")
            return
        
        # 2. Get summary for first company
        first_company = companies[0]
        demo_company_summary(service, first_company)
        
        # 3. Get template details
        demo_template_details(service, first_company)
        
        # 4. Get coordinate details
        demo_coordinate_details(service, first_company)
        
        # 5. Load specific coordinate
        demo_load_specific_coordinate(service, first_company, page=1)
        
        # 6. Validate company
        demo_validation(service, first_company)
        
        # 7. Batch operations (if multiple companies)
        if len(companies) > 1:
            demo_batch_operations(service, companies[:2])
        
        # 8. All companies summary
        demo_all_companies_summary(service)
        
        print_section("Demo Complete")
        print("✓ All demonstrations completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
