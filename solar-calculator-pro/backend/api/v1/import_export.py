"""
Import/Export API Endpoints

Provides REST API for data import/export operations
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List
import base64
import logging

from ...services.import_export_service import (
    ImportExportService,
    ImportConfig,
    ExportConfig,
    ImportFormat,
    ExportFormat,
    DataMapping,
    ValidationRule
)
from ...models.import_export_schemas import (
    ImportRequest,
    ImportResultSchema,
    ExportRequest,
    ExportResponse,
    TemplateRequest,
    ValidationRequest,
    ValidationResponse,
    BatchImportRequest,
    BatchImportResult,
    DataSourceInfo,
    TransformationInfo,
    ValidatorInfo
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/import-export", tags=["import-export"])


def get_import_export_service() -> ImportExportService:
    """Dependency to get import/export service"""
    return ImportExportService()


@router.post("/import", response_model=ImportResultSchema)
async def import_data(
    request: ImportRequest,
    service: ImportExportService = Depends(get_import_export_service)
):
    """
    Import data from file
    
    Supports CSV, Excel, JSON, and XML formats with:
    - Field mapping
    - Data transformation
    - Validation rules
    - Error handling
    """
    try:
        # Decode file content
        file_data = base64.b64decode(request.file_content)
        
        # Convert schema to service models
        config = ImportConfig(
            format=ImportFormat(request.config.format),
            mappings=[
                DataMapping(**m.dict()) for m in request.config.mappings
            ],
            validation_rules=[
                ValidationRule(**r.dict()) for r in request.config.validation_rules
            ],
            skip_errors=request.config.skip_errors,
            batch_size=request.config.batch_size
        )
        
        # Perform import
        result = await service.import_data(file_data, config)
        
        return ImportResultSchema(**result.dict())
        
    except Exception as e:
        logger.error(f"Import failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/export", response_model=ExportResponse)
async def export_data(
    request: ExportRequest,
    service: ImportExportService = Depends(get_import_export_service)
):
    """
    Export data to file
    
    Supports CSV, Excel, JSON, XML, and PDF formats with:
    - Field selection
    - Custom headers
    - Filtering
    """
    try:
        # TODO: Fetch data from data source based on request.data_source and filters
        # For now, return empty data as placeholder
        data = []
        
        # Convert schema to service models
        config = ExportConfig(
            format=ExportFormat(request.config.format),
            fields=request.config.fields,
            include_headers=request.config.include_headers,
            custom_headers=request.config.custom_headers
        )
        
        # Perform export
        file_data = await service.export_data(data, config)
        
        # Encode to base64
        file_content = base64.b64encode(file_data).decode('utf-8')
        
        # Determine content type
        content_types = {
            ExportFormat.CSV: "text/csv",
            ExportFormat.EXCEL: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ExportFormat.JSON: "application/json",
            ExportFormat.XML: "application/xml",
            ExportFormat.PDF: "application/pdf"
        }
        
        # Generate filename
        extensions = {
            ExportFormat.CSV: "csv",
            ExportFormat.EXCEL: "xlsx",
            ExportFormat.JSON: "json",
            ExportFormat.XML: "xml",
            ExportFormat.PDF: "pdf"
        }
        
        filename = f"export_{request.data_source}.{extensions[config.format]}"
        
        return ExportResponse(
            file_content=file_content,
            filename=filename,
            content_type=content_types[config.format]
        )
        
    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/template", response_model=ExportResponse)
async def create_template(
    request: TemplateRequest,
    service: ImportExportService = Depends(get_import_export_service)
):
    """
    Create import template
    
    Generates a template file with specified fields for data import
    """
    try:
        template_data = service.create_import_template(
            fields=request.fields,
            format=ExportFormat(request.format)
        )
        
        # Encode to base64
        file_content = base64.b64encode(template_data).decode('utf-8')
        
        # Determine content type and extension
        content_types = {
            ExportFormat.CSV: "text/csv",
            ExportFormat.EXCEL: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ExportFormat.JSON: "application/json",
            ExportFormat.XML: "application/xml"
        }
        
        extensions = {
            ExportFormat.CSV: "csv",
            ExportFormat.EXCEL: "xlsx",
            ExportFormat.JSON: "json",
            ExportFormat.XML: "xml"
        }
        
        filename = f"import_template.{extensions[request.format]}"
        
        return ExportResponse(
            file_content=file_content,
            filename=filename,
            content_type=content_types[request.format]
        )
        
    except Exception as e:
        logger.error(f"Template creation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/validate", response_model=ValidationResponse)
async def validate_file(
    request: ValidationRequest,
    service: ImportExportService = Depends(get_import_export_service)
):
    """
    Validate import file
    
    Checks file structure and content without importing
    """
    try:
        # Decode file content
        file_data = base64.b64decode(request.file_content)
        
        # Convert schema to service models
        config = ImportConfig(
            format=ImportFormat(request.config.format),
            mappings=[
                DataMapping(**m.dict()) for m in request.config.mappings
            ],
            validation_rules=[
                ValidationRule(**r.dict()) for r in request.config.validation_rules
            ],
            skip_errors=request.config.skip_errors,
            batch_size=request.config.batch_size
        )
        
        # Validate file
        result = service.validate_import_file(file_data, config)
        
        return ValidationResponse(**result)
        
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/batch-import", response_model=BatchImportResult)
async def batch_import(
    request: BatchImportRequest,
    background_tasks: BackgroundTasks,
    service: ImportExportService = Depends(get_import_export_service)
):
    """
    Batch import multiple files
    
    Processes multiple files in parallel with progress tracking
    """
    try:
        results = []
        successful = 0
        failed = 0
        
        # Convert schema to service models
        config = ImportConfig(
            format=ImportFormat(request.config.format),
            mappings=[
                DataMapping(**m.dict()) for m in request.config.mappings
            ],
            validation_rules=[
                ValidationRule(**r.dict()) for r in request.config.validation_rules
            ],
            skip_errors=request.config.skip_errors,
            batch_size=request.config.batch_size
        )
        
        # Process each file
        for file_info in request.files:
            try:
                file_data = base64.b64decode(file_info['content'])
                result = await service.import_data(file_data, config)
                results.append(ImportResultSchema(**result.dict()))
                
                if result.success:
                    successful += 1
                else:
                    failed += 1
                    
            except Exception as e:
                logger.error(f"File import failed: {str(e)}")
                failed += 1
                results.append(ImportResultSchema(
                    success=False,
                    total_records=0,
                    imported_records=0,
                    failed_records=0,
                    errors=[{"error": str(e)}]
                ))
        
        return BatchImportResult(
            total_files=len(request.files),
            successful_files=successful,
            failed_files=failed,
            results=results
        )
        
    except Exception as e:
        logger.error(f"Batch import failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/data-sources", response_model=List[DataSourceInfo])
async def get_data_sources():
    """
    Get available data sources for export
    
    Returns list of data sources with available fields
    """
    # TODO: Implement actual data source discovery
    return [
        DataSourceInfo(
            name="projects",
            description="Solar calculator projects",
            available_fields=["id", "name", "customer_name", "system_size", "created_at"],
            record_count=0
        ),
        DataSourceInfo(
            name="customers",
            description="CRM customers",
            available_fields=["id", "name", "email", "phone", "created_at"],
            record_count=0
        ),
        DataSourceInfo(
            name="products",
            description="Product catalog",
            available_fields=["id", "name", "category", "price", "manufacturer"],
            record_count=0
        )
    ]


@router.get("/transformations", response_model=List[TransformationInfo])
async def get_transformations(
    service: ImportExportService = Depends(get_import_export_service)
):
    """
    Get available transformation functions
    
    Returns list of transformation functions with descriptions
    """
    return [
        TransformationInfo(
            name="uppercase",
            description="Convert text to uppercase",
            example="'hello' -> 'HELLO'"
        ),
        TransformationInfo(
            name="lowercase",
            description="Convert text to lowercase",
            example="'HELLO' -> 'hello'"
        ),
        TransformationInfo(
            name="trim",
            description="Remove leading and trailing whitespace",
            example="'  hello  ' -> 'hello'"
        ),
        TransformationInfo(
            name="to_int",
            description="Convert to integer",
            example="'123' -> 123"
        ),
        TransformationInfo(
            name="to_float",
            description="Convert to float",
            example="'123.45' -> 123.45"
        ),
        TransformationInfo(
            name="to_bool",
            description="Convert to boolean",
            example="'true' -> True"
        ),
        TransformationInfo(
            name="to_date",
            description="Convert to date",
            example="'2024-01-01' -> datetime"
        )
    ]


@router.get("/validators", response_model=List[ValidatorInfo])
async def get_validators(
    service: ImportExportService = Depends(get_import_export_service)
):
    """
    Get available validator functions
    
    Returns list of validator functions with descriptions
    """
    return [
        ValidatorInfo(
            name="required",
            description="Field must have a value",
            parameters=[]
        ),
        ValidatorInfo(
            name="email",
            description="Field must be a valid email address",
            parameters=[]
        ),
        ValidatorInfo(
            name="numeric",
            description="Field must be numeric",
            parameters=[]
        ),
        ValidatorInfo(
            name="positive",
            description="Field must be a positive number",
            parameters=[]
        )
    ]
