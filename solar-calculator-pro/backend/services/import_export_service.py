"""
Universal Import/Export Service

Provides comprehensive data import/export functionality with:
- Multiple format support (CSV, Excel, JSON, XML)
- Data mapping and transformation
- Validation rules
- Batch processing
- Progress tracking
"""

from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
import pandas as pd
import json
import xml.etree.ElementTree as ET
from io import BytesIO, StringIO
import csv
from datetime import datetime
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class ImportFormat(str, Enum):
    """Supported import formats"""
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    XML = "xml"


class ExportFormat(str, Enum):
    """Supported export formats"""
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    XML = "xml"
    PDF = "pdf"


class ValidationRule(BaseModel):
    """Validation rule definition"""
    field: str
    rule_type: str  # required, type, range, pattern, custom
    parameters: Dict[str, Any] = Field(default_factory=dict)
    error_message: str


class DataMapping(BaseModel):
    """Data field mapping definition"""
    source_field: str
    target_field: str
    transformation: Optional[str] = None  # Function name for transformation
    default_value: Optional[Any] = None


class ImportConfig(BaseModel):
    """Import configuration"""
    format: ImportFormat
    mappings: List[DataMapping]
    validation_rules: List[ValidationRule]
    skip_errors: bool = False
    batch_size: int = 100


class ExportConfig(BaseModel):
    """Export configuration"""
    format: ExportFormat
    fields: List[str]
    include_headers: bool = True
    custom_headers: Optional[Dict[str, str]] = None


class ImportResult(BaseModel):
    """Import operation result"""
    success: bool
    total_records: int
    imported_records: int
    failed_records: int
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ImportExportService:
    """Universal import/export service"""
    
    def __init__(self):
        self.transformations: Dict[str, Callable] = {}
        self.validators: Dict[str, Callable] = {}
        self._register_default_transformations()
        self._register_default_validators()
    
    def _register_default_transformations(self):
        """Register default transformation functions"""
        self.transformations.update({
            'uppercase': lambda x: str(x).upper() if x else None,
            'lowercase': lambda x: str(x).lower() if x else None,
            'trim': lambda x: str(x).strip() if x else None,
            'to_int': lambda x: int(x) if x else None,
            'to_float': lambda x: float(x) if x else None,
            'to_bool': lambda x: str(x).lower() in ('true', '1', 'yes') if x else False,
            'to_date': lambda x: pd.to_datetime(x) if x else None,
        })
    
    def _register_default_validators(self):
        """Register default validation functions"""
        self.validators.update({
            'required': lambda x: x is not None and str(x).strip() != '',
            'email': lambda x: '@' in str(x) if x else False,
            'numeric': lambda x: str(x).replace('.', '').replace('-', '').isdigit() if x else False,
            'positive': lambda x: float(x) > 0 if x else False,
        })
    
    def register_transformation(self, name: str, func: Callable):
        """Register custom transformation function"""
        self.transformations[name] = func
    
    def register_validator(self, name: str, func: Callable):
        """Register custom validator function"""
        self.validators[name] = func
    
    # ==================== IMPORT METHODS ====================
    
    async def import_data(
        self,
        data: Union[bytes, str],
        config: ImportConfig,
        progress_callback: Optional[Callable] = None
    ) -> ImportResult:
        """
        Import data from various formats
        
        Args:
            data: Raw data (bytes for binary formats, str for text)
            config: Import configuration
            progress_callback: Optional callback for progress updates
            
        Returns:
            ImportResult with statistics and errors
        """
        try:
            # Parse data based on format
            if config.format == ImportFormat.CSV:
                records = self._parse_csv(data)
            elif config.format == ImportFormat.EXCEL:
                records = self._parse_excel(data)
            elif config.format == ImportFormat.JSON:
                records = self._parse_json(data)
            elif config.format == ImportFormat.XML:
                records = self._parse_xml(data)
            else:
                raise ValueError(f"Unsupported import format: {config.format}")
            
            # Process records in batches
            return await self._process_import_batch(
                records, config, progress_callback
            )
            
        except Exception as e:
            logger.error(f"Import failed: {str(e)}")
            return ImportResult(
                success=False,
                total_records=0,
                imported_records=0,
                failed_records=0,
                errors=[{"error": str(e)}]
            )
    
    def _parse_csv(self, data: Union[bytes, str]) -> List[Dict[str, Any]]:
        """Parse CSV data"""
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        
        reader = csv.DictReader(StringIO(data))
        return list(reader)
    
    def _parse_excel(self, data: bytes) -> List[Dict[str, Any]]:
        """Parse Excel data"""
        df = pd.read_excel(BytesIO(data))
        return df.to_dict('records')
    
    def _parse_json(self, data: Union[bytes, str]) -> List[Dict[str, Any]]:
        """Parse JSON data"""
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        
        parsed = json.loads(data)
        
        # Handle both array and object with data key
        if isinstance(parsed, list):
            return parsed
        elif isinstance(parsed, dict) and 'data' in parsed:
            return parsed['data']
        else:
            return [parsed]
    
    def _parse_xml(self, data: Union[bytes, str]) -> List[Dict[str, Any]]:
        """Parse XML data"""
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        
        root = ET.fromstring(data)
        records = []
        
        # Assume structure: <root><record>...</record></root>
        for record_elem in root:
            record = {}
            for child in record_elem:
                record[child.tag] = child.text
            records.append(record)
        
        return records
    
    async def _process_import_batch(
        self,
        records: List[Dict[str, Any]],
        config: ImportConfig,
        progress_callback: Optional[Callable]
    ) -> ImportResult:
        """Process import records in batches"""
        total = len(records)
        imported = 0
        failed = 0
        errors = []
        warnings = []
        
        for i in range(0, total, config.batch_size):
            batch = records[i:i + config.batch_size]
            
            for idx, record in enumerate(batch):
                try:
                    # Apply mappings
                    mapped_record = self._apply_mappings(record, config.mappings)
                    
                    # Validate
                    validation_errors = self._validate_record(
                        mapped_record, config.validation_rules
                    )
                    
                    if validation_errors:
                        if config.skip_errors:
                            failed += 1
                            errors.append({
                                "record_index": i + idx,
                                "errors": validation_errors
                            })
                            continue
                        else:
                            raise ValueError(f"Validation failed: {validation_errors}")
                    
                    imported += 1
                    
                except Exception as e:
                    failed += 1
                    errors.append({
                        "record_index": i + idx,
                        "error": str(e)
                    })
                    
                    if not config.skip_errors:
                        break
            
            # Progress callback
            if progress_callback:
                await progress_callback(i + len(batch), total)
        
        return ImportResult(
            success=failed == 0 or config.skip_errors,
            total_records=total,
            imported_records=imported,
            failed_records=failed,
            errors=errors,
            warnings=warnings
        )
    
    def _apply_mappings(
        self,
        record: Dict[str, Any],
        mappings: List[DataMapping]
    ) -> Dict[str, Any]:
        """Apply field mappings and transformations"""
        mapped = {}
        
        for mapping in mappings:
            value = record.get(mapping.source_field, mapping.default_value)
            
            # Apply transformation if specified
            if mapping.transformation and value is not None:
                if mapping.transformation in self.transformations:
                    try:
                        value = self.transformations[mapping.transformation](value)
                    except Exception as e:
                        logger.warning(
                            f"Transformation '{mapping.transformation}' failed: {e}"
                        )
            
            mapped[mapping.target_field] = value
        
        return mapped
    
    def _validate_record(
        self,
        record: Dict[str, Any],
        rules: List[ValidationRule]
    ) -> List[str]:
        """Validate record against rules"""
        errors = []
        
        for rule in rules:
            value = record.get(rule.field)
            
            if rule.rule_type == 'required':
                if not self.validators['required'](value):
                    errors.append(rule.error_message)
            
            elif rule.rule_type == 'type':
                expected_type = rule.parameters.get('type')
                if value is not None and not isinstance(value, eval(expected_type)):
                    errors.append(rule.error_message)
            
            elif rule.rule_type == 'range':
                if value is not None:
                    min_val = rule.parameters.get('min')
                    max_val = rule.parameters.get('max')
                    if min_val is not None and value < min_val:
                        errors.append(rule.error_message)
                    if max_val is not None and value > max_val:
                        errors.append(rule.error_message)
            
            elif rule.rule_type == 'pattern':
                import re
                pattern = rule.parameters.get('pattern')
                if value and not re.match(pattern, str(value)):
                    errors.append(rule.error_message)
            
            elif rule.rule_type == 'custom':
                validator_name = rule.parameters.get('validator')
                if validator_name in self.validators:
                    if not self.validators[validator_name](value):
                        errors.append(rule.error_message)
        
        return errors
    
    # ==================== EXPORT METHODS ====================
    
    async def export_data(
        self,
        data: List[Dict[str, Any]],
        config: ExportConfig
    ) -> bytes:
        """
        Export data to various formats
        
        Args:
            data: List of records to export
            config: Export configuration
            
        Returns:
            Exported data as bytes
        """
        try:
            # Filter fields
            filtered_data = self._filter_fields(data, config.fields)
            
            # Apply custom headers if specified
            if config.custom_headers:
                filtered_data = self._apply_custom_headers(
                    filtered_data, config.custom_headers
                )
            
            # Export based on format
            if config.format == ExportFormat.CSV:
                return self._export_csv(filtered_data, config.include_headers)
            elif config.format == ExportFormat.EXCEL:
                return self._export_excel(filtered_data, config.include_headers)
            elif config.format == ExportFormat.JSON:
                return self._export_json(filtered_data)
            elif config.format == ExportFormat.XML:
                return self._export_xml(filtered_data)
            else:
                raise ValueError(f"Unsupported export format: {config.format}")
                
        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            raise
    
    def _filter_fields(
        self,
        data: List[Dict[str, Any]],
        fields: List[str]
    ) -> List[Dict[str, Any]]:
        """Filter data to include only specified fields"""
        return [
            {field: record.get(field) for field in fields}
            for record in data
        ]
    
    def _apply_custom_headers(
        self,
        data: List[Dict[str, Any]],
        headers: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Apply custom header names"""
        return [
            {headers.get(k, k): v for k, v in record.items()}
            for record in data
        ]
    
    def _export_csv(self, data: List[Dict[str, Any]], include_headers: bool) -> bytes:
        """Export to CSV format"""
        output = StringIO()
        
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            if include_headers:
                writer.writeheader()
            writer.writerows(data)
        
        return output.getvalue().encode('utf-8')
    
    def _export_excel(self, data: List[Dict[str, Any]], include_headers: bool) -> bytes:
        """Export to Excel format"""
        df = pd.DataFrame(data)
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, header=include_headers)
        
        output.seek(0)
        return output.read()
    
    def _export_json(self, data: List[Dict[str, Any]]) -> bytes:
        """Export to JSON format"""
        return json.dumps(data, indent=2, default=str).encode('utf-8')
    
    def _export_xml(self, data: List[Dict[str, Any]]) -> bytes:
        """Export to XML format"""
        root = ET.Element('data')
        
        for record in data:
            record_elem = ET.SubElement(root, 'record')
            for key, value in record.items():
                field_elem = ET.SubElement(record_elem, key)
                field_elem.text = str(value) if value is not None else ''
        
        return ET.tostring(root, encoding='utf-8')
    
    # ==================== TEMPLATE METHODS ====================
    
    def create_import_template(
        self,
        fields: List[str],
        format: ExportFormat = ExportFormat.CSV
    ) -> bytes:
        """Create an import template with specified fields"""
        template_data = [{field: '' for field in fields}]
        config = ExportConfig(
            format=format,
            fields=fields,
            include_headers=True
        )
        return self.export_data(template_data, config)
    
    def validate_import_file(
        self,
        data: Union[bytes, str],
        config: ImportConfig
    ) -> Dict[str, Any]:
        """Validate import file without importing"""
        try:
            # Parse data
            if config.format == ImportFormat.CSV:
                records = self._parse_csv(data)
            elif config.format == ImportFormat.EXCEL:
                records = self._parse_excel(data)
            elif config.format == ImportFormat.JSON:
                records = self._parse_json(data)
            elif config.format == ImportFormat.XML:
                records = self._parse_xml(data)
            else:
                return {"valid": False, "error": "Unsupported format"}
            
            # Validate structure
            if not records:
                return {"valid": False, "error": "No records found"}
            
            # Check required fields
            required_fields = [
                m.source_field for m in config.mappings
                if any(r.field == m.target_field and r.rule_type == 'required'
                       for r in config.validation_rules)
            ]
            
            missing_fields = [
                field for field in required_fields
                if field not in records[0]
            ]
            
            if missing_fields:
                return {
                    "valid": False,
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }
            
            return {
                "valid": True,
                "record_count": len(records),
                "fields": list(records[0].keys())
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
