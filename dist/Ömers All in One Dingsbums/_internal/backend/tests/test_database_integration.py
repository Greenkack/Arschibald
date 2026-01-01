"""
Tests for Database Integration with Universal Data

Tests for Task 222: Database Integration
Requirements: 14.4, 14.7
"""

import pytest
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.database import Base
from backend.core.dynamic_keys import KeyPrefix
from backend.core.pdf_bytes import PDFMetadata
from backend.models.database_models import (
    User, Customer, Project, SolarCalculation,
    Product, Offer, Task
)
from backend.services.universal_data_service import (
    UniversalDataService,
    BulkPDFGenerator
)


@pytest.fixture
def test_db():
    """Create a temporary test database"""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    # Create engine and session
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    # Cleanup
    session.close()
    engine.dispose()  # Close all connections
    os.close(db_fd)
    
    # Try to remove file, ignore errors on Windows
    try:
        os.unlink(db_path)
    except PermissionError:
        pass  # File will be cleaned up by OS


@pytest.fixture
def service(test_db):
    """Create UniversalDataService instance"""
    return UniversalDataService(test_db)


class TestDatabaseModels:
    """Test database models with universal data support"""
    
    def test_user_model_creation(self, test_db):
        """Test creating a user with universal data support"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed123",
            full_name="Test User",
            role="admin"
        )
        
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.dynamic_key is None  # Not generated yet
        assert user.pdf_bytes is None
    
    def test_customer_model_creation(self, test_db):
        """Test creating a customer"""
        customer = Customer(
            name="Test Customer",
            email="customer@example.com",
            phone="+49 123 456789",
            address="Test Street 123",
            city="Berlin",
            postal_code="10115"
        )
        
        test_db.add(customer)
        test_db.commit()
        test_db.refresh(customer)
        
        assert customer.id is not None
        assert customer.name == "Test Customer"
    
    def test_project_model_creation(self, test_db):
        """Test creating a project"""
        project = Project(
            name="Solar Installation",
            customer_id=1,
            project_type="solar",
            status="draft"
        )
        
        test_db.add(project)
        test_db.commit()
        test_db.refresh(project)
        
        assert project.id is not None
        assert project.project_type == "solar"


class TestDynamicKeyGeneration:
    """Test dynamic key generation for database records"""
    
    def test_generate_key_for_user(self, test_db, service):
        """Test generating dynamic key for user"""
        user = User(
            username="keytest",
            email="key@test.com",
            hashed_password="hash"
        )
        
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Generate key
        key = service.generate_key_for_record(user, KeyPrefix.USER)
        
        assert key is not None
        assert key.startswith("USR_")
        assert user.dynamic_key == key
    
    def test_generate_key_for_customer(self, test_db, service):
        """Test generating dynamic key for customer"""
        customer = Customer(name="Key Test Customer")
        
        test_db.add(customer)
        test_db.commit()
        test_db.refresh(customer)
        
        key = service.generate_key_for_record(customer, KeyPrefix.CUSTOMER)
        
        assert key.startswith("CUS_")
        assert customer.dynamic_key == key
    
    def test_bulk_key_generation(self, test_db, service):
        """Test bulk key generation"""
        customers = [
            Customer(name=f"Customer {i}")
            for i in range(5)
        ]
        
        for customer in customers:
            test_db.add(customer)
        test_db.commit()
        
        for customer in customers:
            test_db.refresh(customer)
        
        keys = service.bulk_generate_keys(customers, KeyPrefix.CUSTOMER)
        
        assert len(keys) == 5
        assert all(key.startswith("CUS_") for key in keys)
        assert len(set(keys)) == 5  # All unique


class TestPDFGeneration:
    """Test PDF generation for database records"""
    
    def test_generate_pdf_for_user(self, test_db, service):
        """Test generating PDF for user"""
        user = User(
            username="pdftest",
            email="pdf@test.com",
            hashed_password="hash",
            full_name="PDF Test User"
        )
        
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Generate PDF
        pdf_bytes = service.generate_pdf_for_record(user)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert user.pdf_bytes == pdf_bytes
        assert pdf_bytes.startswith(b'%PDF')  # PDF header
    
    def test_generate_pdf_with_metadata(self, test_db, service):
        """Test generating PDF with custom metadata"""
        customer = Customer(
            name="PDF Customer",
            email="customer@pdf.com"
        )
        
        test_db.add(customer)
        test_db.commit()
        test_db.refresh(customer)
        
        metadata = PDFMetadata(
            title="Customer Report",
            author="Test System",
            subject="Customer Information"
        )
        
        pdf_bytes = service.generate_pdf_for_record(customer, metadata)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
    
    def test_bulk_pdf_generation(self, test_db, service):
        """Test bulk PDF generation"""
        products = [
            Product(
                name=f"Product {i}",
                category="Solar",
                price=1000.0 + i * 100
            )
            for i in range(3)
        ]
        
        for product in products:
            test_db.add(product)
        test_db.commit()
        
        for product in products:
            test_db.refresh(product)
        
        pdf_list = service.bulk_generate_pdfs(products)
        
        assert len(pdf_list) == 3
        assert all(len(pdf) > 0 for pdf in pdf_list)
        assert all(product.has_pdf() for product in products)


class TestKeyAndPDFCombined:
    """Test combined key and PDF generation"""
    
    def test_generate_key_and_pdf(self, test_db, service):
        """Test generating both key and PDF"""
        project = Project(
            name="Combined Test",
            customer_id=1,
            project_type="solar"
        )
        
        test_db.add(project)
        test_db.commit()
        test_db.refresh(project)
        
        key, pdf_bytes = service.generate_key_and_pdf(
            project,
            KeyPrefix.PROJECT
        )
        
        assert key.startswith("PRJ_")
        assert len(pdf_bytes) > 0
        assert project.dynamic_key == key
        assert project.pdf_bytes == pdf_bytes
    
    def test_bulk_generate_keys_and_pdfs(self, test_db, service):
        """Test bulk generation of keys and PDFs"""
        offers = [
            Offer(
                customer_id=1,
                offer_number=f"OFF-2024-{i:03d}",
                total_amount=5000.0 + i * 1000
            )
            for i in range(3)
        ]
        
        for offer in offers:
            test_db.add(offer)
        test_db.commit()
        
        for offer in offers:
            test_db.refresh(offer)
        
        results = service.bulk_generate_keys_and_pdfs(
            offers,
            KeyPrefix.OFFER
        )
        
        assert len(results) == 3
        
        for key, pdf_bytes in results:
            assert key.startswith("OFF_")
            assert len(pdf_bytes) > 0
        
        # Verify all offers have keys and PDFs
        assert all(offer.dynamic_key is not None for offer in offers)
        assert all(offer.has_pdf() for offer in offers)


class TestKeyLookup:
    """Test key-based lookups"""
    
    def test_get_by_dynamic_key(self, test_db, service):
        """Test retrieving record by dynamic key"""
        customer = Customer(name="Lookup Test")
        
        test_db.add(customer)
        test_db.commit()
        test_db.refresh(customer)
        
        key = service.generate_key_for_record(customer, KeyPrefix.CUSTOMER)
        
        # Retrieve by key
        found = service.get_by_dynamic_key(Customer, key)
        
        assert found is not None
        assert found.id == customer.id
        assert found.name == customer.name
    
    def test_get_by_prefix(self, test_db, service):
        """Test retrieving records by key prefix"""
        customers = [
            Customer(name=f"Prefix Test {i}")
            for i in range(3)
        ]
        
        for customer in customers:
            test_db.add(customer)
        test_db.commit()
        
        for customer in customers:
            test_db.refresh(customer)
            service.generate_key_for_record(customer, KeyPrefix.CUSTOMER)
        
        # Get all customers by prefix
        found = service.get_by_prefix(Customer, "CUS")
        
        assert len(found) >= 3


class TestPDFManagement:
    """Test PDF management operations"""
    
    def test_get_records_with_pdf(self, test_db, service):
        """Test getting records that have PDFs"""
        # Create some records with PDFs
        with_pdf = [
            Product(name=f"With PDF {i}", price=100.0)
            for i in range(2)
        ]
        
        # Create some without PDFs
        without_pdf = [
            Product(name=f"Without PDF {i}", price=200.0)
            for i in range(2)
        ]
        
        for product in with_pdf + without_pdf:
            test_db.add(product)
        test_db.commit()
        
        for product in with_pdf + without_pdf:
            test_db.refresh(product)
        
        # Generate PDFs only for first group
        service.bulk_generate_pdfs(with_pdf)
        
        # Query records with PDFs
        found = service.get_records_with_pdf(Product)
        
        assert len(found) >= 2
    
    def test_regenerate_pdf(self, test_db, service):
        """Test regenerating PDF"""
        customer = Customer(name="Regenerate Test")
        
        test_db.add(customer)
        test_db.commit()
        test_db.refresh(customer)
        
        # Generate initial PDF
        pdf1 = service.generate_pdf_for_record(customer)
        
        # Regenerate
        pdf2 = service.regenerate_pdf(customer)
        
        assert pdf2 is not None
        assert len(pdf2) > 0
        # PDFs should be similar but may differ slightly
        assert customer.pdf_bytes == pdf2
    
    def test_delete_pdf(self, test_db, service):
        """Test deleting PDF"""
        product = Product(name="Delete PDF Test", price=500.0)
        
        test_db.add(product)
        test_db.commit()
        test_db.refresh(product)
        
        # Generate PDF
        service.generate_pdf_for_record(product)
        assert product.has_pdf()
        
        # Delete PDF
        deleted = service.delete_pdf(product)
        
        assert deleted is True
        assert not product.has_pdf()
        assert product.pdf_bytes is None


class TestFormattedData:
    """Test formatted data retrieval"""
    
    def test_get_formatted_data(self, test_db, service):
        """Test getting formatted data"""
        calc = SolarCalculation(
            project_id=1,
            system_size=10.5,
            module_count=30,
            total_cost=15000.0,
            annual_production=12500.0
        )
        
        test_db.add(calc)
        test_db.commit()
        test_db.refresh(calc)
        
        # Get formatted data in German format
        formatted = service.get_formatted_data(calc, locale='de-DE')
        
        assert 'system_size' in formatted
        assert 'total_cost' in formatted
        # Numbers should be in German format
        assert ',' in formatted['system_size']  # Decimal comma
    
    def test_export_to_json(self, test_db, service):
        """Test exporting to JSON"""
        customer = Customer(
            name="JSON Test",
            email="json@test.com"
        )
        
        test_db.add(customer)
        test_db.commit()
        test_db.refresh(customer)
        
        json_str = service.export_to_json(customer)
        
        assert json_str is not None
        assert '"name"' in json_str
        assert '"JSON Test"' in json_str


class TestStatistics:
    """Test statistics and reporting"""
    
    def test_get_statistics(self, test_db, service):
        """Test getting statistics"""
        # Create some customers
        customers = [
            Customer(name=f"Stats Test {i}")
            for i in range(5)
        ]
        
        for customer in customers:
            test_db.add(customer)
        test_db.commit()
        
        for customer in customers:
            test_db.refresh(customer)
        
        # Generate keys for some
        service.bulk_generate_keys(customers[:3], KeyPrefix.CUSTOMER)
        
        # Generate PDFs for some
        service.bulk_generate_pdfs(customers[:2])
        
        # Get statistics
        stats = service.get_statistics(Customer)
        
        assert stats['total_records'] >= 5
        assert stats['records_with_keys'] >= 3
        assert stats['records_with_pdfs'] >= 2


class TestBulkPDFGenerator:
    """Test bulk PDF generator"""
    
    def test_generate_pdfs_batch(self, test_db):
        """Test batch PDF generation"""
        generator = BulkPDFGenerator(test_db)
        
        # Create many records
        tasks = [
            Task(
                title=f"Task {i}",
                description=f"Description {i}",
                status="open"
            )
            for i in range(10)
        ]
        
        for task in tasks:
            test_db.add(task)
        test_db.commit()
        
        for task in tasks:
            test_db.refresh(task)
        
        # Generate PDFs in batches
        results = generator.generate_pdfs_batch(
            tasks,
            batch_size=3
        )
        
        assert results['total_records'] == 10
        assert results['generated'] == 10
        assert results['success_rate'] == 100.0
    
    def test_batch_with_progress_callback(self, test_db):
        """Test batch generation with progress callback"""
        generator = BulkPDFGenerator(test_db)
        
        products = [
            Product(name=f"Batch Product {i}", price=100.0)
            for i in range(5)
        ]
        
        for product in products:
            test_db.add(product)
        test_db.commit()
        
        for product in products:
            test_db.refresh(product)
        
        progress_calls = []
        
        def progress_callback(current, total):
            progress_calls.append((current, total))
        
        results = generator.generate_pdfs_batch(
            products,
            batch_size=2,
            progress_callback=progress_callback
        )
        
        assert len(progress_calls) > 0
        assert progress_calls[-1][0] == 5  # Final progress
        assert progress_calls[-1][1] == 5  # Total


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
