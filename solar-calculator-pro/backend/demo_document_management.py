"""
Document Management System Demo

Demonstrates all features of the document management system.
"""

import io
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.services.document_service import DocumentService
from backend.models.document_schemas import (
    DocumentCreate, DocumentUpdate, DocumentSearchRequest,
    DocumentTemplateCreate, DocumentShareCreate,
    DocumentGenerateRequest, DocumentType, DocumentStatus
)


def demo_document_crud(service: DocumentService, user_id: int = 1):
    """Demonstrate document CRUD operations"""
    print("\n" + "="*60)
    print("DOCUMENT CRUD OPERATIONS")
    print("="*60)
    
    # Create document
    print("\n1. Creating document...")
    file_content = io.BytesIO(b"This is a test PDF document content")
    document_data = DocumentCreate(
        name="Test Invoice",
        description="Sample invoice for demonstration",
        type=DocumentType.PDF,
        file_name="invoice.pdf",
        file_path="",
        file_size=len(file_content.getvalue()),
        mime_type="application/pdf",
        tags=["invoice", "test", "demo"]
    )
    
    document = service.create_document(document_data, file_content, user_id)
    print(f" Created document: {document.name} (ID: {document.id})")
    print(f"  - Type: {document.type}")
    print(f"  - Status: {document.status}")
    print(f"  - Version: {document.version}")
    print(f"  - Tags: {document.tags}")
    
    # Get document
    print("\n2. Retrieving document...")
    retrieved = service.get_document(document.id)
    print(f" Retrieved document: {retrieved.name}")
    print(f"  - File size: {retrieved.file_size} bytes")
    print(f"  - Created: {retrieved.created_at}")
    
    # Update document
    print("\n3. Updating document...")
    update_data = DocumentUpdate(
        name="Updated Invoice",
        description="Updated description",
        status=DocumentStatus.ACTIVE,
        tags=["invoice", "updated", "important"]
    )
    updated = service.update_document(document.id, update_data, user_id)
    print(f" Updated document: {updated.name}")
    print(f"  - New status: {updated.status}")
    print(f"  - New tags: {updated.tags}")
    
    return document


def demo_versioning(service: DocumentService, document_id: int, user_id: int = 1):
    """Demonstrate document versioning"""
    print("\n" + "="*60)
    print("DOCUMENT VERSIONING")
    print("="*60)
    
    # Create version 2
    print("\n1. Creating version 2...")
    file_content_v2 = io.BytesIO(b"This is version 2 of the document with more content")
    version_2 = service.create_version(document_id, file_content_v2, user_id)
    print(f" Created version 2: {version_2.name}")
    print(f"  - Version: {version_2.version}")
    print(f"  - Is latest: {version_2.is_latest_version}")
    
    # Create version 3
    print("\n2. Creating version 3...")
    file_content_v3 = io.BytesIO(b"This is version 3 with even more content and improvements")
    version_3 = service.create_version(document_id, file_content_v3, user_id)
    print(f" Created version 3: {version_3.name}")
    print(f"  - Version: {version_3.version}")
    print(f"  - Is latest: {version_3.is_latest_version}")
    
    # Get all versions
    print("\n3. Retrieving all versions...")
    versions = service.get_versions(document_id)
    print(f" Found {len(versions)} versions:")
    for v in versions:
        latest_marker = " (LATEST)" if v.is_latest_version else ""
        print(f"  - Version {v.version}: {v.file_size} bytes{latest_marker}")


def demo_templates(service: DocumentService, user_id: int = 1):
    """Demonstrate document templates"""
    print("\n" + "="*60)
    print("DOCUMENT TEMPLATES")
    print("="*60)
    
    # Create template
    print("\n1. Creating invoice template...")
    template_data = DocumentTemplateCreate(
        name="Standard Invoice Template",
        description="Template for generating invoices",
        type=DocumentType.PDF,
        template_path="templates/invoice.pdf",
        template_variables=["customer_name", "invoice_number", "total_amount", "date"],
        category="financial",
        tags=["invoice", "billing"]
    )
    template = service.create_template(template_data, user_id)
    print(f" Created template: {template.name} (ID: {template.id})")
    print(f"  - Type: {template.type}")
    print(f"  - Category: {template.category}")
    print(f"  - Variables: {template.template_variables}")
    
    # List templates
    print("\n2. Listing templates...")
    templates = service.list_templates(type=DocumentType.PDF)
    print(f" Found {len(templates)} PDF templates:")
    for t in templates:
        print(f"  - {t.name} ({t.category})")
    
    return template


def demo_generation(service: DocumentService, template_id: int, user_id: int = 1):
    """Demonstrate document generation"""
    print("\n" + "="*60)
    print("DOCUMENT GENERATION")
    print("="*60)
    
    print("\n1. Generating document from template...")
    generate_request = DocumentGenerateRequest(
        template_id=template_id,
        output_name="Invoice_2024_001.pdf",
        variables={
            "customer_name": "John Doe",
            "invoice_number": "INV-2024-001",
            "total_amount": "1.234,56 €",
            "date": "15.01.2024"
        },
        tags=["invoice", "2024", "customer-123"]
    )
    
    generated = service.generate_from_template(generate_request, user_id)
    if generated:
        print(f" Generated document: {generated.name}")
        print(f"  - Type: {generated.type}")
        print(f"  - Tags: {generated.tags}")
        print(f"  - Metadata: {generated.metadata}")
    else:
        print(" Failed to generate document")


def demo_sharing(service: DocumentService, document_id: int, user_id: int = 1):
    """Demonstrate document sharing"""
    print("\n" + "="*60)
    print("DOCUMENT SHARING")
    print("="*60)
    
    # Share with user
    print("\n1. Sharing document with user...")
    share_data = DocumentShareCreate(
        document_id=document_id,
        shared_with_user_id=2,
        can_view=True,
        can_edit=False,
        can_delete=False,
        can_share=False,
        expires_at=datetime.utcnow() + timedelta(days=30),
        message="Please review this document"
    )
    
    share = service.share_document(share_data, user_id)
    if share:
        print(f" Shared document (Share ID: {share.id})")
        print(f"  - Shared with user: {share.shared_with_user_id}")
        print(f"  - Permissions: View={share.can_view}, Edit={share.can_edit}")
        print(f"  - Access token: {share.access_token[:20]}...")
        print(f"  - Expires: {share.expires_at}")
    
    # Share via email
    print("\n2. Sharing document via email...")
    email_share_data = DocumentShareCreate(
        document_id=document_id,
        shared_with_email="user@example.com",
        can_view=True,
        can_edit=False,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    
    email_share = service.share_document(email_share_data, user_id)
    if email_share:
        print(f" Shared via email: {email_share.shared_with_email}")
        print(f"  - Access token: {email_share.access_token[:20]}...")


def demo_search(service: DocumentService, user_id: int = 1):
    """Demonstrate document search"""
    print("\n" + "="*60)
    print("DOCUMENT SEARCH")
    print("="*60)
    
    # Search by query
    print("\n1. Searching by query 'invoice'...")
    search_request = DocumentSearchRequest(
        query="invoice",
        limit=10
    )
    documents, total = service.search_documents(search_request, user_id)
    print(f" Found {total} documents:")
    for doc in documents:
        print(f"  - {doc.name} ({doc.type}, {doc.status})")
    
    # Search by type and status
    print("\n2. Searching by type and status...")
    search_request = DocumentSearchRequest(
        type=DocumentType.PDF,
        status=DocumentStatus.ACTIVE,
        limit=10
    )
    documents, total = service.search_documents(search_request, user_id)
    print(f" Found {total} active PDF documents")
    
    # Search by tags
    print("\n3. Searching by tags...")
    search_request = DocumentSearchRequest(
        tags=["invoice", "important"],
        limit=10
    )
    documents, total = service.search_documents(search_request, user_id)
    print(f" Found {total} documents with specified tags")
    
    # Search by date range
    print("\n4. Searching by date range...")
    search_request = DocumentSearchRequest(
        created_after=datetime.utcnow() - timedelta(days=7),
        limit=10
    )
    documents, total = service.search_documents(search_request, user_id)
    print(f" Found {total} documents created in last 7 days")


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("DOCUMENT MANAGEMENT SYSTEM DEMO")
    print("="*60)
    
    # Initialize database session
    db = SessionLocal()
    
    try:
        # Initialize service
        service = DocumentService(db)
        user_id = 1  # Demo user ID
        
        # Run demos
        document = demo_document_crud(service, user_id)
        demo_versioning(service, document.id, user_id)
        template = demo_templates(service, user_id)
        demo_generation(service, template.id, user_id)
        demo_sharing(service, document.id, user_id)
        demo_search(service, user_id)
        
        print("\n" + "="*60)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nAll document management features demonstrated:")
        print(" Document CRUD operations")
        print(" Document versioning")
        print(" Document templates")
        print(" Document generation")
        print(" Document sharing")
        print(" Document search")
        
    except Exception as e:
        print(f"\n Error during demo: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
