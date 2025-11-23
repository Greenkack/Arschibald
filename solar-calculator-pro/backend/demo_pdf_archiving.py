"""
Demo: PDF Archiving & CRM Integration

This demo shows how to use the PDF archiving service to automatically
save PDFs to customer records with metadata and versioning.

Requirements: 1.3, 6.1
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from solar-calculator-pro.backend.services.pdf_archiving_service import PDFArchivingService, PDFMetadata


def create_sample_pdf() -> bytes:
    """Create a sample PDF for demonstration"""
    return b"%PDF-1.4\n%Sample PDF content for demo\n%%EOF"


def demo_basic_archiving():
    """Demo: Basic PDF archiving"""
    print("\n" + "="*60)
    print("DEMO 1: Basic PDF Archiving")
    print("="*60)
    
    service = PDFArchivingService()
    
    # Create sample PDF
    pdf_bytes = create_sample_pdf()
    
    # Archive PDF
    print("\n📄 Archiving PDF to customer record...")
    doc_id = service.auto_save_to_crm(
        pdf_bytes=pdf_bytes,
        filename="Angebot_Mustermann_PV.pdf",
        customer_id=1,
        project_id=10,
        company_name="Mustermann GmbH",
        products=[
            {"name": "PV Module Trina Solar 400W", "quantity": 20},
            {"name": "Wechselrichter Fronius 10kW", "quantity": 1},
            {"name": "Batteriespeicher BYD 10kWh", "quantity": 1}
        ],
        total_price=16999.00
    )
    
    if doc_id:
        print(f"✅ PDF archived successfully!")
        print(f"   Document ID: {doc_id}")
    else:
        print("❌ Failed to archive PDF")


def demo_metadata_extraction():
    """Demo: PDF metadata extraction"""
    print("\n" + "="*60)
    print("DEMO 2: PDF Metadata Extraction")
    print("="*60)
    
    service = PDFArchivingService()
    
    # Create sample PDF
    pdf_bytes = create_sample_pdf()
    
    # Create metadata
    print("\n📋 Creating PDF metadata...")
    metadata = service.create_metadata(
        pdf_bytes=pdf_bytes,
        filename="Angebot_Schmidt_v2_2025-01-15.pdf",
        company_id=2,
        company_name="Schmidt Solar GmbH",
        products=[
            {"name": "PV Module", "quantity": 25},
            {"name": "Wechselrichter", "quantity": 1}
        ],
        total_price=18500.00
    )
    
    print("\n✅ Metadata created:")
    print(f"   Creation Date: {metadata.creation_date}")
    print(f"   Company: {metadata.company_name} (ID: {metadata.company_id})")
    print(f"   Products: {len(metadata.products)} items")
    print(f"   Total Price: {metadata.total_price:,.2f} €")
    print(f"   PDF Type: {metadata.pdf_type}")
    print(f"   Version: {metadata.version}")
    print(f"   File Size: {metadata.file_size / 1024:.1f} KB")
    print(f"   Checksum: {metadata.checksum[:16]}...")


def demo_versioning():
    """Demo: PDF versioning"""
    print("\n" + "="*60)
    print("DEMO 3: PDF Versioning")
    print("="*60)
    
    service = PDFArchivingService()
    
    # Get next version number
    print("\n🔢 Getting next version number...")
    version = service.get_next_version_number(
        customer_id=1,
        pdf_type='offer_pdf',
        project_id=10
    )
    
    print(f"✅ Next version: v{version}")
    
    # Create versioned filename
    metadata = PDFMetadata(
        creation_date=datetime.now(),
        company_id=1
    )
    
    versioned_name = service.create_versioned_filename(
        "Angebot_Mustermann.pdf",
        version,
        metadata
    )
    
    print(f"   Versioned filename: {versioned_name}")


def demo_pdf_history():
    """Demo: PDF history retrieval"""
    print("\n" + "="*60)
    print("DEMO 4: PDF History")
    print("="*60)
    
    service = PDFArchivingService()
    
    # Get PDF history for customer
    print("\n📚 Retrieving PDF history for customer...")
    history = service.get_pdf_history(
        customer_id=1,
        pdf_type='offer_pdf'
    )
    
    print(f"\n✅ Found {len(history)} PDFs:")
    for doc in history[:5]:  # Show first 5
        print(f"\n   📄 {doc.get('display_name', 'Unknown')}")
        print(f"      Type: {doc.get('type_label', doc.get('doc_type', 'Unknown'))}")
        print(f"      Date: {doc.get('formatted_date', doc.get('uploaded_at', 'Unknown'))}")
        if doc.get('version'):
            print(f"      Version: v{doc['version']}")


def demo_pdf_search():
    """Demo: PDF search"""
    print("\n" + "="*60)
    print("DEMO 5: PDF Search")
    print("="*60)
    
    service = PDFArchivingService()
    
    # Search PDFs
    print("\n🔍 Searching for PDFs...")
    results = service.search_pdfs(
        search_term='Angebot',
        pdf_type='offer_pdf',
        start_date=datetime.now() - timedelta(days=30)
    )
    
    print(f"\n✅ Found {len(results)} matching PDFs:")
    for doc in results[:5]:  # Show first 5
        print(f"\n   📄 {doc.get('display_name', 'Unknown')}")
        print(f"      Customer: {doc.get('customer_name', 'Unknown')}")
        print(f"      Date: {doc.get('uploaded_at', 'Unknown')}")


def demo_pdf_export():
    """Demo: PDF export"""
    print("\n" + "="*60)
    print("DEMO 6: PDF Export")
    print("="*60)
    
    service = PDFArchivingService()
    
    # Export PDF
    print("\n💾 Exporting PDF from archive...")
    pdf_bytes = service.export_pdf(document_id=1)
    
    if pdf_bytes:
        print(f"✅ PDF exported successfully!")
        print(f"   Size: {len(pdf_bytes) / 1024:.1f} KB")
    else:
        print("❌ PDF not found or export failed")


def demo_statistics():
    """Demo: PDF statistics"""
    print("\n" + "="*60)
    print("DEMO 7: PDF Statistics")
    print("="*60)
    
    service = PDFArchivingService()
    
    # Get statistics
    print("\n📊 Getting PDF archive statistics...")
    stats = service.get_pdf_statistics()
    
    print("\n✅ Statistics:")
    print(f"   Total PDFs: {stats.get('total_pdfs', 0)}")
    print(f"   Total Customers: {stats.get('total_customers', 0)}")
    
    if stats.get('by_type'):
        print("\n   By Type:")
        for pdf_type, count in stats['by_type'].items():
            print(f"      {pdf_type}: {count}")


def demo_complete_workflow():
    """Demo: Complete workflow"""
    print("\n" + "="*60)
    print("DEMO 8: Complete Workflow")
    print("="*60)
    
    service = PDFArchivingService()
    
    # Step 1: Create PDF with offer data
    print("\n📄 Step 1: Creating PDF with offer data...")
    pdf_bytes = create_sample_pdf()
    
    offer_data = {
        'customer_id': 1,
        'customer': {'name': 'Mustermann GmbH'},
        'project_type': 'pv',
        'products': [
            {"name": "PV Module Trina Solar 400W", "quantity": 20, "price": 200.00},
            {"name": "Wechselrichter Fronius 10kW", "quantity": 1, "price": 2500.00},
            {"name": "Batteriespeicher BYD 10kWh", "quantity": 1, "price": 5000.00}
        ],
        'total_cost': 16999.00,
        'offer_id': 'OFF-2025-001',
        'created_at': datetime.now().isoformat()
    }
    
    # Step 2: Archive PDF
    print("\n💾 Step 2: Archiving PDF to CRM...")
    doc_id = service.auto_save_to_crm(
        pdf_bytes=pdf_bytes,
        filename="Angebot_Mustermann_PV_2025.pdf",
        customer_id=offer_data['customer_id'],
        project_id=10,
        offer_data=offer_data
    )
    
    if doc_id:
        print(f"✅ PDF archived with ID: {doc_id}")
        
        # Step 3: Retrieve PDF history
        print("\n📚 Step 3: Retrieving PDF history...")
        history = service.get_pdf_history(customer_id=1)
        print(f"✅ Customer has {len(history)} PDFs in archive")
        
        # Step 4: Get statistics
        print("\n📊 Step 4: Getting statistics...")
        stats = service.get_pdf_statistics(customer_id=1)
        print(f"✅ Customer statistics: {stats.get('total_pdfs', 0)} PDFs")
        
        print("\n🎉 Complete workflow executed successfully!")
    else:
        print("❌ Workflow failed at archiving step")


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("PDF ARCHIVING & CRM INTEGRATION - DEMO")
    print("="*60)
    print("\nThis demo shows the PDF archiving service capabilities:")
    print("  1. Basic PDF archiving")
    print("  2. Metadata extraction")
    print("  3. PDF versioning")
    print("  4. PDF history retrieval")
    print("  5. PDF search")
    print("  6. PDF export")
    print("  7. Statistics")
    print("  8. Complete workflow")
    
    try:
        demo_basic_archiving()
        demo_metadata_extraction()
        demo_versioning()
        demo_pdf_history()
        demo_pdf_search()
        demo_pdf_export()
        demo_statistics()
        demo_complete_workflow()
        
        print("\n" + "="*60)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error running demos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
