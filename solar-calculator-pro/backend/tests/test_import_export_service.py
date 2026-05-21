"""
Import/Export Service Tests

Comprehensive tests for import/export functionality
"""

import pytest
import json
from services.import_export_service import (
    ImportExportService,
    ImportConfig,
    ExportConfig,
    ImportFormat,
    ExportFormat,
    DataMapping,
    ValidationRule
)


@pytest.fixture
def service():
    """Create import/export service instance"""
    return ImportExportService()


@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing"""
    return """Name,Email,Age
John Doe,john@example.com,30
Jane Smith,jane@example.com,25
Bob Johnson,bob@example.com,35"""


@pytest.fixture
def sample_json_data():
    """Sample JSON data for testing"""
    return json.dumps([
        {"name": "John", "email": "john@example.com", "age": 30},
        {"name": "Jane", "email": "jane@example.com", "age": 25}
    ])


class TestCSVImport:
    """Test CSV import functionality"""
    
    @pytest.mark.asyncio
    async def test_basic_csv_import(self, service, sample_csv_data):
        """Test basic CSV import"""
        config = ImportConfig(
            format=ImportFormat.CSV,
            mappings=[
                DataMapping(source_field="Name", target_field="name"),
                DataMapping(source_field="Email", target_field="email"),
                DataMapping(source_field="Age", target_field="age", transformation="to_int")
            ],
            validation_rules=[],
            skip_errors=False
        )
        
        result = await service.import_data(sample_csv_data, config)
        
        assert result.success is True
        assert result.total_records == 3
        assert result.imported_records == 3
        assert result.failed_records == 0
    
    @pytest.mark.asyncio
    async def test_csv_import_with_validation(self, service):
        """Test CSV import with validation rules"""
        csv_data = """Name,Email,Age
John Doe,john@example.com,30
,jane@example.com,25
Bob Johnson,invalid_email,35"""
        
        config = ImportConfig(
            format=ImportFormat.CSV,
            mappings=[
                DataMapping(source_field="Name", target_field="name"),
                DataMapping(source_field="Email", target_field="email"),
                DataMapping(source_field="Age", target_field="age", transformation="to_int")
            ],
            validation_rules=[
                ValidationRule(
                    field="name",
                    rule_type="required",
                    parameters={},
                    error_message="Name is required"
                ),
                ValidationRule(
                    field="email",
                    rule_type="custom",
                    parameters={"validator": "email"},
                    error_message="Invalid email"
                )
            ],
            skip_errors=True
        )
        
        result = await service.import_data(csv_data, config)
        
        assert result.total_records == 3
        assert result.imported_records == 1  # Only first record is valid
        assert result.failed_records == 2
        assert len(result.errors) == 2
    
    @pytest.mark.asyncio
    async def test_csv_import_with_transformation(self, service):
        """Test CSV import with data transformation"""
        csv_data = """Name,Email
  JOHN DOE  ,JOHN@EXAMPLE.COM
  jane smith  ,JANE@EXAMPLE.COM"""
        
        config = ImportConfig(
            format=ImportFormat.CSV,
            mappings=[
                DataMapping(source_field="Name", target_field="name", transformation="trim"),
                DataMapping(source_field="Email", target_field="email", transformation="lowercase")
            ],
            validation_rules=[],
            skip_errors=False
        )
        
        result = await service.import_data(csv_data, config)
        
        assert result.success is True
        assert result.imported_records == 2


class TestJSONImport:
    """Test JSON import functionality"""
    
    @pytest.mark.asyncio
    async def test_basic_json_import(self, service, sample_json_data):
        """Test basic JSON import"""
        config = ImportConfig(
            format=ImportFormat.JSON,
            mappings=[
                DataMapping(source_field="name", target_field="name"),
                DataMapping(source_field="email", target_field="email"),
                DataMapping(source_field="age", target_field="age")
            ],
            validation_rules=[],
            skip_errors=False
        )
        
        result = await service.import_data(sample_json_data, config)
        
        assert result.success is True
        assert result.total_records == 2
        assert result.imported_records == 2
    
    @pytest.mark.asyncio
    async def test_json_import_with_nested_data(self, service):
        """Test JSON import with data key"""
        json_data = json.dumps({
            "data": [
                {"name": "John", "email": "john@example.com"},
                {"name": "Jane", "email": "jane@example.com"}
            ]
        })
        
        config = ImportConfig(
            format=ImportFormat.JSON,
            mappings=[
                DataMapping(source_field="name", target_field="name"),
                DataMapping(source_field="email", target_field="email")
            ],
            validation_rules=[],
            skip_errors=False
        )
        
        result = await service.import_data(json_data, config)
        
        assert result.success is True
        assert result.total_records == 2


class TestExcelImport:
    """Test Excel import functionality"""
    
    @pytest.mark.asyncio
    async def test_excel_import(self, service):
        """Test Excel import"""
        # Note: This test requires actual Excel file bytes
        # For now, we'll skip it or mock the pandas read_excel
        pytest.skip("Requires actual Excel file for testing")


class TestXMLImport:
    """Test XML import functionality"""
    
    @pytest.mark.asyncio
    async def test_basic_xml_import(self, service):
        """Test basic XML import"""
        xml_data = """<?xml version="1.0"?>
<data>
    <record>
        <name>John Doe</name>
        <email>john@example.com</email>
        <age>30</age>
    </record>
    <record>
        <name>Jane Smith</name>
        <email>jane@example.com</email>
        <age>25</age>
    </record>
</data>"""
        
        config = ImportConfig(
            format=ImportFormat.XML,
            mappings=[
                DataMapping(source_field="name", target_field="name"),
                DataMapping(source_field="email", target_field="email"),
                DataMapping(source_field="age", target_field="age", transformation="to_int")
            ],
            validation_rules=[],
            skip_errors=False
        )
        
        result = await service.import_data(xml_data, config)
        
        assert result.success is True
        assert result.total_records == 2
        assert result.imported_records == 2


class TestExport:
    """Test export functionality"""
    
    @pytest.mark.asyncio
    async def test_csv_export(self, service):
        """Test CSV export"""
        data = [
            {"id": 1, "name": "John", "email": "john@example.com"},
            {"id": 2, "name": "Jane", "email": "jane@example.com"}
        ]
        
        config = ExportConfig(
            format=ExportFormat.CSV,
            fields=["id", "name", "email"],
            include_headers=True
        )
        
        result = await service.export_data(data, config)
        
        assert isinstance(result, bytes)
        assert b"id,name,email" in result
        assert b"John" in result
        assert b"Jane" in result
    
    @pytest.mark.asyncio
    async def test_json_export(self, service):
        """Test JSON export"""
        data = [
            {"id": 1, "name": "John"},
            {"id": 2, "name": "Jane"}
        ]
        
        config = ExportConfig(
            format=ExportFormat.JSON,
            fields=["id", "name"],
            include_headers=True
        )
        
        result = await service.export_data(data, config)
        
        assert isinstance(result, bytes)
        exported_data = json.loads(result.decode('utf-8'))
        assert len(exported_data) == 2
        assert exported_data[0]["name"] == "John"
    
    @pytest.mark.asyncio
    async def test_export_with_custom_headers(self, service):
        """Test export with custom headers"""
        data = [
            {"id": 1, "name": "John"}
        ]
        
        config = ExportConfig(
            format=ExportFormat.CSV,
            fields=["id", "name"],
            include_headers=True,
            custom_headers={"id": "ID", "name": "Full Name"}
        )
        
        result = await service.export_data(data, config)
        
        assert b"ID,Full Name" in result


class TestValidation:
    """Test validation functionality"""
    
    def test_required_validation(self, service):
        """Test required field validation"""
        record = {"name": "", "email": "test@example.com"}
        rules = [
            ValidationRule(
                field="name",
                rule_type="required",
                parameters={},
                error_message="Name is required"
            )
        ]
        
        errors = service._validate_record(record, rules)
        
        assert len(errors) == 1
        assert "Name is required" in errors
    
    def test_range_validation(self, service):
        """Test range validation"""
        record = {"age": 150}
        rules = [
            ValidationRule(
                field="age",
                rule_type="range",
                parameters={"min": 0, "max": 120},
                error_message="Age must be between 0 and 120"
            )
        ]
        
        errors = service._validate_record(record, rules)
        
        assert len(errors) == 1
        assert "Age must be between 0 and 120" in errors
    
    def test_pattern_validation(self, service):
        """Test pattern validation"""
        record = {"phone": "invalid"}
        rules = [
            ValidationRule(
                field="phone",
                rule_type="pattern",
                parameters={"pattern": r"^\+?[0-9]{10,15}$"},
                error_message="Invalid phone format"
            )
        ]
        
        errors = service._validate_record(record, rules)
        
        assert len(errors) == 1
        assert "Invalid phone format" in errors


class TestTransformation:
    """Test transformation functionality"""
    
    def test_uppercase_transformation(self, service):
        """Test uppercase transformation"""
        record = {"name": "john doe"}
        mappings = [
            DataMapping(source_field="name", target_field="name", transformation="uppercase")
        ]
        
        result = service._apply_mappings(record, mappings)
        
        assert result["name"] == "JOHN DOE"
    
    def test_lowercase_transformation(self, service):
        """Test lowercase transformation"""
        record = {"email": "JOHN@EXAMPLE.COM"}
        mappings = [
            DataMapping(source_field="email", target_field="email", transformation="lowercase")
        ]
        
        result = service._apply_mappings(record, mappings)
        
        assert result["email"] == "john@example.com"
    
    def test_trim_transformation(self, service):
        """Test trim transformation"""
        record = {"name": "  John Doe  "}
        mappings = [
            DataMapping(source_field="name", target_field="name", transformation="trim")
        ]
        
        result = service._apply_mappings(record, mappings)
        
        assert result["name"] == "John Doe"
    
    def test_to_int_transformation(self, service):
        """Test to_int transformation"""
        record = {"age": "30"}
        mappings = [
            DataMapping(source_field="age", target_field="age", transformation="to_int")
        ]
        
        result = service._apply_mappings(record, mappings)
        
        assert result["age"] == 30
        assert isinstance(result["age"], int)
    
    def test_to_float_transformation(self, service):
        """Test to_float transformation"""
        record = {"price": "99.99"}
        mappings = [
            DataMapping(source_field="price", target_field="price", transformation="to_float")
        ]
        
        result = service._apply_mappings(record, mappings)
        
        assert result["price"] == 99.99
        assert isinstance(result["price"], float)
    
    def test_custom_transformation(self, service):
        """Test custom transformation"""
        service.register_transformation(
            'double',
            lambda x: int(x) * 2 if x else None
        )
        
        record = {"value": "5"}
        mappings = [
            DataMapping(source_field="value", target_field="value", transformation="double")
        ]
        
        result = service._apply_mappings(record, mappings)
        
        assert result["value"] == 10


class TestTemplates:
    """Test template functionality"""
    
    def test_csv_template_creation(self, service):
        """Test CSV template creation"""
        fields = ["name", "email", "phone"]
        template = service.create_import_template(fields, ExportFormat.CSV)
        
        assert isinstance(template, bytes)
        assert b"name,email,phone" in template
    
    def test_excel_template_creation(self, service):
        """Test Excel template creation"""
        fields = ["name", "email"]
        template = service.create_import_template(fields, ExportFormat.EXCEL)
        
        assert isinstance(template, bytes)
        assert len(template) > 0


class TestFileValidation:
    """Test file validation functionality"""
    
    def test_valid_csv_file(self, service, sample_csv_data):
        """Test validation of valid CSV file"""
        config = ImportConfig(
            format=ImportFormat.CSV,
            mappings=[
                DataMapping(source_field="Name", target_field="name"),
                DataMapping(source_field="Email", target_field="email")
            ],
            validation_rules=[
                ValidationRule(
                    field="name",
                    rule_type="required",
                    parameters={},
                    error_message="Name required"
                )
            ],
            skip_errors=False
        )
        
        result = service.validate_import_file(sample_csv_data, config)
        
        assert result["valid"] is True
        assert result["record_count"] == 3
        assert "Name" in result["fields"]
    
    def test_invalid_csv_file(self, service):
        """Test validation of invalid CSV file"""
        csv_data = """Name,Email
John,john@example.com"""
        
        config = ImportConfig(
            format=ImportFormat.CSV,
            mappings=[
                DataMapping(source_field="Phone", target_field="phone")
            ],
            validation_rules=[
                ValidationRule(
                    field="phone",
                    rule_type="required",
                    parameters={},
                    error_message="Phone required"
                )
            ],
            skip_errors=False
        )
        
        result = service.validate_import_file(csv_data, config)
        
        assert result["valid"] is False
        assert "Missing required fields" in result["error"]


class TestBatchProcessing:
    """Test batch processing functionality"""
    
    @pytest.mark.asyncio
    async def test_batch_processing(self, service):
        """Test batch processing with progress callback"""
        # Generate large dataset
        records = [f"User {i},user{i}@example.com" for i in range(150)]
        csv_data = "Name,Email\n" + "\n".join(records)
        
        progress_updates = []
        
        async def progress_callback(current, total):
            progress_updates.append((current, total))
        
        config = ImportConfig(
            format=ImportFormat.CSV,
            mappings=[
                DataMapping(source_field="Name", target_field="name"),
                DataMapping(source_field="Email", target_field="email")
            ],
            validation_rules=[],
            skip_errors=False,
            batch_size=50
        )
        
        result = await service.import_data(csv_data, config, progress_callback)
        
        assert result.success is True
        assert result.imported_records == 150
        assert len(progress_updates) > 0  # Progress was tracked


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
