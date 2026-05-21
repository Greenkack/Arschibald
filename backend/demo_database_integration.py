"""
Database Integration Demo

Demonstrates the database integration features from Task 222.

Requirements: 14.4, 14.7
"""

import os
import sys
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from core.database import Base
from core.dynamic_keys import KeyPrefix
from core.pdf_bytes import PDFMetadata
from models.database_models import (
    User, Customer, Project, SolarCalculation,
    Product, Offer, Task
)
from services.universal_data_service import (
    UniversalDataService,
    BulkPDFGenerator
)


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def demo_basic_operations():
    """Demonstrate basic database operations"""
    print_section("1. Basic Database Operations")
    
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    print(f"Creating temporary database: {db_path}")
    
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Create service
        service = UniversalDataService(db)
        
        # Create a customer
        print("\nCreating customer...")
        customer = Customer(
            name="Solar Solutions GmbH",
            email="info@solar-solutions.de",
            phone="+49 30 12345678",
            address="Sonnenallee 123",
            city="Berlin",
            postal_code="10115"
        )
        
        db.add(customer)
        db.commit()
        db.refresh(customer)
        
        print(f" Customer created with ID: {customer.id}")
        
        # Generate dynamic key
        print("\nGenerating dynamic key...")
        key = service.generate_key_for_record(customer, KeyPrefix.CUSTOMER)
        print(f" Generated key: {key}")
        
        # Generate PDF
        print("\nGenerating PDF...")
        metadata = PDFMetadata(
            title="Customer Information",
            author="Solar Calculator Pro",
            subject="Customer Details"
        )
        pdf_bytes = service.generate_pdf_for_record(customer, metadata)
        print(f" Generated PDF: {len(pdf_bytes)} bytes")
        
        # Save PDF to file
        pdf_file = "customer_demo.pdf"
        with open(pdf_file, 'wb') as f:
            f.write(pdf_bytes)
        print(f" Saved PDF to: {pdf_file}")
        
        # Get formatted data
        print("\nGetting formatted data...")
        formatted = service.get_formatted_data(customer, locale='de-DE')
        print(f" Formatted data:")
        for key, value in formatted.items():
            if not key.startswith('_') and value:
                print(f"  {key}: {value}")
        
        return db, service
        
    except Exception as e:
        print(f" Error: {e}")
        db.close()
        os.close(db_fd)
        os.unlink(db_path)
        raise


def demo_bulk_operations(db, service):
    """Demonstrate bulk operations"""
    print_section("2. Bulk Operations")
    
    # Create multiple products
    print("\nCreating 10 products...")
    products = []
    for i in range(10):
        product = Product(
            name=f"Solar Module {i+1}",
            category="PV Module",
            manufacturer="SolarTech",
            price=500.0 + i * 50,
            is_active=True
        )
        products.append(product)
        db.add(product)
    
    db.commit()
    for product in products:
        db.refresh(product)
    
    print(f" Created {len(products)} products")
    
    # Bulk generate keys
    print("\nGenerating keys for all products...")
    keys = service.bulk_generate_keys(products, KeyPrefix.PRODUCT)
    print(f" Generated {len(keys)} keys")
    print(f"  First key: {keys[0]}")
    print(f"  Last key: {keys[-1]}")
    
    # Bulk generate PDFs
    print("\nGenerating PDFs for all products...")
    pdfs = service.bulk_generate_pdfs(products)
    print(f" Generated {len(pdfs)} PDFs")
    print(f"  Total size: {sum(len(pdf) for pdf in pdfs)} bytes")
    
    # Get statistics
    print("\nGetting statistics...")
    stats = service.get_statistics(Product)
    print(f" Statistics:")
    print(f"  Total records: {stats['total_records']}")
    print(f"  With keys: {stats['records_with_keys']}")
    print(f"  With PDFs: {stats['records_with_pdfs']}")
    print(f"  Key coverage: {stats['key_coverage_percent']:.1f}%")
    print(f"  PDF coverage: {stats['pdf_coverage_percent']:.1f}%")


def demo_key_lookups(db, service):
    """Demonstrate key-based lookups"""
    print_section("3. Key-Based Lookups")
    
    # Create a project
    print("\nCreating project...")
    project = Project(
        name="Residential Solar Installation",
        customer_id=1,
        project_type="solar",
        status="active"
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    key = service.generate_key_for_record(project, KeyPrefix.PROJECT)
    print(f" Created project with key: {key}")
    
    # Find by key
    print("\nFinding project by key...")
    found = service.get_by_dynamic_key(Project, key)
    if found:
        print(f" Found project: {found.name}")
        print(f"  Status: {found.status}")
        print(f"  Type: {found.project_type}")
    else:
        print(" Project not found")
    
    # Find by prefix
    print("\nFinding all projects by prefix...")
    all_projects = service.get_by_prefix(Project, "PRJ")
    print(f" Found {len(all_projects)} projects with PRJ prefix")


def demo_batch_pdf_generation(db):
    """Demonstrate batch PDF generation with progress"""
    print_section("4. Batch PDF Generation with Progress")
    
    generator = BulkPDFGenerator(db)
    
    # Create tasks
    print("\nCreating 20 tasks...")
    tasks = []
    for i in range(20):
        task = Task(
            title=f"Task {i+1}",
            description=f"Description for task {i+1}",
            status="open",
            priority="medium"
        )
        tasks.append(task)
        db.add(task)
    
    db.commit()
    for task in tasks:
        db.refresh(task)
    
    print(f" Created {len(tasks)} tasks")
    
    # Generate PDFs with progress
    print("\nGenerating PDFs in batches...")
    
    progress_updates = []
    
    def progress_callback(current, total):
        percent = (current / total) * 100
        progress_updates.append((current, total))
        print(f"  Progress: {percent:.1f}% ({current}/{total})")
    
    results = generator.generate_pdfs_batch(
        tasks,
        batch_size=5,
        progress_callback=progress_callback
    )
    
    print(f"\n Batch generation complete:")
    print(f"  Total records: {results['total_records']}")
    print(f"  Generated: {results['generated']}")
    print(f"  Failed: {results['failed']}")
    print(f"  Success rate: {results['success_rate']:.1f}%")
    print(f"  Progress updates: {len(progress_updates)}")


def demo_solar_calculation(db, service):
    """Demonstrate solar calculation with formatting"""
    print_section("5. Solar Calculation with German Formatting")
    
    # Create solar calculation
    print("\nCreating solar calculation...")
    calc = SolarCalculation(
        project_id=1,
        system_size=10.5,
        module_count=30,
        annual_production=12500.75,
        self_consumption_rate=0.35,
        payback_period=12.5,
        total_cost=15750.00,
        savings_25_years=45250.50,
        co2_savings=187.5
    )
    
    db.add(calc)
    db.commit()
    db.refresh(calc)
    
    print(f" Created solar calculation")
    
    # Generate key and PDF
    key, pdf = service.generate_key_and_pdf(
        calc,
        KeyPrefix.SOLAR_CALCULATION
    )
    print(f" Generated key: {key}")
    print(f" Generated PDF: {len(pdf)} bytes")
    
    # Get formatted values
    print("\nFormatted values (German format):")
    print(f"  System Size: {calc.get_formatted_value('system_size')} kWp")
    print(f"  Module Count: {calc.module_count}")
    print(f"  Annual Production: {calc.get_formatted_value('annual_production')} kWh")
    print(f"  Total Cost: {calc.get_formatted_value('total_cost', format_type='currency')}")
    print(f"  Savings (25 years): {calc.get_formatted_value('savings_25_years', format_type='currency')}")
    print(f"  Payback Period: {calc.get_formatted_value('payback_period')} years")
    
    # Export to JSON
    print("\nExporting to JSON...")
    json_str = service.export_to_json(calc)
    print(f" JSON export: {len(json_str)} characters")
    print(f"  Preview: {json_str[:200]}...")


def demo_pdf_management(db, service):
    """Demonstrate PDF management operations"""
    print_section("6. PDF Management")
    
    # Create offers
    print("\nCreating offers...")
    offers = []
    for i in range(5):
        offer = Offer(
            customer_id=1,
            offer_number=f"OFF-2024-{i+1:03d}",
            status="draft",
            total_amount=5000.0 + i * 1000
        )
        offers.append(offer)
        db.add(offer)
    
    db.commit()
    for offer in offers:
        db.refresh(offer)
    
    print(f" Created {len(offers)} offers")
    
    # Generate PDFs for first 3
    print("\nGenerating PDFs for first 3 offers...")
    service.bulk_generate_pdfs(offers[:3])
    print(" PDFs generated")
    
    # Find offers with PDFs
    print("\nFinding offers with PDFs...")
    with_pdfs = service.get_records_with_pdf(Offer)
    print(f" Found {len(with_pdfs)} offers with PDFs")
    
    # Find offers without PDFs
    print("\nFinding offers without PDFs...")
    without_pdfs = service.get_records_without_pdf(Offer)
    print(f" Found {len(without_pdfs)} offers without PDFs")
    
    # Regenerate PDF
    print("\nRegenerating PDF for first offer...")
    new_pdf = service.regenerate_pdf(offers[0])
    print(f" Regenerated PDF: {len(new_pdf)} bytes")
    
    # Delete PDF
    print("\nDeleting PDF from second offer...")
    deleted = service.delete_pdf(offers[1])
    print(f" PDF deleted: {deleted}")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("DATABASE INTEGRATION DEMO")
    print("Task 222: Database Integration")
    print("=" * 60)
    
    try:
        # Run demos
        db, service = demo_basic_operations()
        demo_bulk_operations(db, service)
        demo_key_lookups(db, service)
        demo_batch_pdf_generation(db)
        demo_solar_calculation(db, service)
        demo_pdf_management(db, service)
        
        print_section("Demo Complete")
        print(" All demonstrations completed successfully!")
        print("\nGenerated files:")
        print("  - customer_demo.pdf")
        
        # Cleanup
        db.close()
        
    except Exception as e:
        print(f"\n Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
