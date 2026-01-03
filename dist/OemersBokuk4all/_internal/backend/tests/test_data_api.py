"""
Tests for Data API Endpoints

Tests for dynamic keys and PDF generation API endpoints.

Task: 231 - API Endpoints for Dynamic Keys and PDF
Requirements: 14.4, 14.5, 14.10
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import base64
import sys
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
project_root = backend_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.main import app
from backend.core.database import Base, get_db
from backend.core.dynamic_keys import KeyPrefix
from backend.core.pdf_bytes import PDFMetadata
from backend.models.database_models import UniversalDatabaseModel


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_data_api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function")
def test_db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_record(test_db):
    """Create a sample record for testing"""
    db = TestingSessionLocal()
    
    record = UniversalDatabaseModel(
        data_type="test",
        content={"value": 123.45, "name": "Test Record"}
    )
    
    # Generate key and PDF
    record.generate_and_store_key(KeyPrefix.DATA)
    record.generate_and_store_pdf()
    
    db.add(record)
    db.commit()
    db.refresh(record)
    
    yield record
    
    db.close()


class TestGetPDFByDynamicKey:
    """Tests for GET /api/v1/data/pdf/{dynamic_key}"""
    
    def test_get_pdf_success(self, sample_record):
        """Test successful PDF retrieval"""
        response = client.get(f"/api/v1/data/pdf/{sample_record.dynamic_key}")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert len(response.content) > 0
    
    def test_get_pdf_invalid_key(self, test_db):
        """Test with invalid key format"""
        response = client.get("/api/v1/data/pdf/invalid_key")
        
        assert response.status_code == 400
        assert "Invalid dynamic key" in response.json()["detail"]
    
    def test_get_pdf_not_found(self, test_db):
        """Test with non-existent key"""
        response = client.get("/api/v1/data/pdf/DAT_20231116_143052_a1b2c3d4")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_pdf_no_pdf_generated(self, test_db):
        """Test record without PDF"""
        db = TestingSessionLocal()
        
        record = UniversalDatabaseModel(
            data_type="test",
            content={"value": 100}
        )
        record.generate_and_store_key(KeyPrefix.DATA)
        # Don't generate PDF
        
        db.add(record)
        db.commit()
        db.refresh(record)
        
        response = client.get(f"/api/v1/data/pdf/{record.dynamic_key}")
        
        assert response.status_code == 404
        assert "PDF not generated" in response.json()["detail"]
        
        db.close()


class TestGeneratePDF:
    """Tests for POST /api/v1/data/generate-pdf"""
    
    def test_generate_pdf_success(self, test_db):
        """Test successful PDF generation"""
        db = TestingSessionLocal()
        
        record = UniversalDatabaseModel(
            data_type="test",
            content={"value": 200}
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        
        response = client.post(
            f"/api/v1/data/generate-pdf?record_id={record.id}",
            json={
                "title": "Test PDF",
                "author": "Test Author",
                "include_base64": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["size_bytes"] > 0
        assert "PDF generated successfully" in data["message"]
        
        db.close()
    
    def test_generate_pdf_with_base64(self, test_db):
        """Test PDF generation with base64 encoding"""
        db = TestingSessionLocal()
        
        record = UniversalDatabaseModel(
            data_type="test",
            content={"value": 300}
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        
        response = client.post(
            f"/api/v1/data/generate-pdf?record_id={record.id}",
            json={
                "title": "Test PDF",
                "include_base64": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "pdf_base64" in data
        assert len(data["pdf_base64"]) > 0
        
        # Verify base64 can be decoded
        pdf_bytes = base64.b64decode(data["pdf_base64"])
        assert len(pdf_bytes) > 0
        
        db.close()
    
    def test_generate_pdf_record_not_found(self, test_db):
        """Test with non-existent record ID"""
        response = client.post(
            "/api/v1/data/generate-pdf?record_id=99999",
            json={"title": "Test"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestGetDataByKey:
    """Tests for GET /api/v1/data/by-key/{key}"""
    
    def test_get_data_success(self, sample_record):
        """Test successful data retrieval"""
        response = client.get(f"/api/v1/data/by-key/{sample_record.dynamic_key}")
        
        assert response.status_code == 200
        data = response.json()
        assert "dynamic_key" in data
        assert data["dynamic_key"] == sample_record.dynamic_key
        assert "content" in data
    
    def test_get_data_with_pdf(self, sample_record):
        """Test data retrieval with PDF"""
        response = client.get(
            f"/api/v1/data/by-key/{sample_record.dynamic_key}?include_pdf=true"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "pdf_bytes" in data
        assert "pdf_size_bytes" in data
        assert len(data["pdf_bytes"]) > 0
    
    def test_get_data_formatted(self, sample_record):
        """Test formatted data retrieval"""
        response = client.get(
            f"/api/v1/data/by-key/{sample_record.dynamic_key}?formatted=true&locale=de-DE"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
    
    def test_get_data_invalid_key(self, test_db):
        """Test with invalid key"""
        response = client.get("/api/v1/data/by-key/invalid")
        
        assert response.status_code == 400
    
    def test_get_data_not_found(self, test_db):
        """Test with non-existent key"""
        response = client.get("/api/v1/data/by-key/DAT_20231116_143052_a1b2c3d4")
        
        assert response.status_code == 404


class TestBulkGeneratePDF:
    """Tests for POST /api/v1/data/bulk-pdf"""
    
    def test_bulk_generate_success(self, test_db):
        """Test successful bulk PDF generation"""
        db = TestingSessionLocal()
        
        # Create multiple records
        records = []
        for i in range(5):
            record = UniversalDatabaseModel(
                data_type="test",
                content={"value": i * 100}
            )
            db.add(record)
            records.append(record)
        
        db.commit()
        for record in records:
            db.refresh(record)
        
        record_ids = [r.id for r in records]
        
        response = client.post(
            "/api/v1/data/bulk-pdf",
            json={
                "record_ids": record_ids,
                "batch_size": 2,
                "metadata": {
                    "title": "Bulk Test",
                    "author": "Test"
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_records"] == 5
        assert data["generated"] == 5
        assert data["failed"] == 0
        assert data["success_rate"] == 100.0
        
        db.close()
    
    def test_bulk_generate_no_records(self, test_db):
        """Test with no matching records"""
        response = client.post(
            "/api/v1/data/bulk-pdf",
            json={
                "record_ids": [99999, 99998],
                "batch_size": 10
            }
        )
        
        assert response.status_code == 404


class TestSearchKeys:
    """Tests for GET /api/v1/data/keys/search"""
    
    def test_search_all_keys(self, sample_record):
        """Test searching all keys"""
        response = client.get("/api/v1/data/keys/search")
        
        assert response.status_code == 200
        data = response.json()
        assert "keys" in data
        assert "total" in data
        assert len(data["keys"]) > 0
    
    def test_search_by_prefix(self, sample_record):
        """Test searching by prefix"""
        response = client.get("/api/v1/data/keys/search?prefix=DAT")
        
        assert response.status_code == 200
        data = response.json()
        assert all(key.startswith("DAT_") for key in data["keys"])
    
    def test_search_with_pagination(self, test_db):
        """Test pagination"""
        db = TestingSessionLocal()
        
        # Create multiple records
        for i in range(10):
            record = UniversalDatabaseModel(
                data_type="test",
                content={"value": i}
            )
            record.generate_and_store_key(KeyPrefix.DATA)
            db.add(record)
        
        db.commit()
        
        response = client.get("/api/v1/data/keys/search?limit=5&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["keys"]) <= 5
        assert data["limit"] == 5
        assert data["offset"] == 0
        
        db.close()
    
    def test_search_invalid_prefix(self, test_db):
        """Test with invalid prefix"""
        response = client.get("/api/v1/data/keys/search?prefix=INVALID")
        
        assert response.status_code == 400


class TestKeyStatistics:
    """Tests for GET /api/v1/data/keys/statistics"""
    
    def test_get_statistics(self, sample_record):
        """Test getting key statistics"""
        response = client.get("/api/v1/data/keys/statistics")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_keys" in data
        assert "keys_by_prefix" in data
        assert "records_with_keys" in data
        assert data["total_keys"] > 0


class TestPDFStatistics:
    """Tests for GET /api/v1/data/pdf/statistics"""
    
    def test_get_pdf_statistics(self, sample_record):
        """Test getting PDF statistics"""
        response = client.get("/api/v1/data/pdf/statistics")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_records" in data
        assert "records_with_pdfs" in data
        assert "pdf_coverage_percent" in data
        assert "total_pdf_size_bytes" in data
        assert "average_pdf_size_bytes" in data


class TestDeletePDF:
    """Tests for DELETE /api/v1/data/pdf/{dynamic_key}"""
    
    def test_delete_pdf_success(self, sample_record):
        """Test successful PDF deletion"""
        response = client.delete(f"/api/v1/data/pdf/{sample_record.dynamic_key}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_delete_pdf_not_found(self, test_db):
        """Test deleting non-existent PDF"""
        db = TestingSessionLocal()
        
        record = UniversalDatabaseModel(
            data_type="test",
            content={"value": 100}
        )
        record.generate_and_store_key(KeyPrefix.DATA)
        # Don't generate PDF
        
        db.add(record)
        db.commit()
        db.refresh(record)
        
        response = client.delete(f"/api/v1/data/pdf/{record.dynamic_key}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        
        db.close()


class TestRegeneratePDF:
    """Tests for POST /api/v1/data/pdf/{dynamic_key}/regenerate"""
    
    def test_regenerate_pdf_success(self, sample_record):
        """Test successful PDF regeneration"""
        response = client.post(
            f"/api/v1/data/pdf/{sample_record.dynamic_key}/regenerate",
            json={
                "title": "Regenerated PDF",
                "author": "Test Author",
                "include_base64": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["size_bytes"] > 0
    
    def test_regenerate_pdf_with_base64(self, sample_record):
        """Test PDF regeneration with base64"""
        response = client.post(
            f"/api/v1/data/pdf/{sample_record.dynamic_key}/regenerate",
            json={
                "title": "Regenerated PDF",
                "include_base64": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "pdf_base64" in data
        assert len(data["pdf_base64"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
