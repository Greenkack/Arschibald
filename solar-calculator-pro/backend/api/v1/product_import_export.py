"""
Product Import/Export API Endpoints

FastAPI routes for importing and exporting product data
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import io

from ...core.dependencies import get_db
from ...services.product_import_export_service import ProductImportExportService
from ...models.product_import_schemas import (
    ProductImportRequest,
    ProductImportResult,
    ProductExportRequest,
    ProductExportFormat,
    ProductImportMapping,
    CSVImportOptions,
    XMLImportOptions,
    APIImportOptions,
    ProductValidationResult,
    ProductImportTemplate,
    ProductBulkUpdateRequest,
    ProductBulkDeleteRequest
)
from ...core.errors import ImportError, ExportError, ValidationError


router = APIRouter(prefix="/product-import-export", tags=["Product Import/Export"])


# ==================== IMPORT ENDPOINTS ====================

@router.post("/import/excel", response_model=ProductImportResult)
async def import_products_from_excel(
    file: UploadFile = File(...),
    mapping: Optional[ProductImportMapping] = None,
    validate_only: bool = Query(False, description="Only validate without importing"),
    db: Session = Depends(get_db)
):
    """
    Import products from Excel file (.xlsx, .xls)
    
    - **file**: Excel file to import
    - **mapping**: Optional column mapping configuration
    - **validate_only**: If true, only validates without importing
    
    Returns import result with success/error details
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File must be Excel format (.xlsx or .xls)")
    
    try:
        service = ProductImportExportService(db)
        result = service.import_from_excel(
            file.file,
            mapping=mapping,
            validate_only=validate_only
        )
        return result
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/import/csv", response_model=ProductImportResult)
async def import_products_from_csv(
    file: UploadFile = File(...),
    delimiter: str = Query(',', description="CSV delimiter"),
    encoding: str = Query('utf-8', description="File encoding"),
    mapping: Optional[ProductImportMapping] = None,
    validate_only: bool = Query(False, description="Only validate without importing"),
    db: Session = Depends(get_db)
):
    """
    Import products from CSV file
    
    - **file**: CSV file to import
    - **delimiter**: CSV delimiter character (default: comma)
    - **encoding**: File encoding (default: utf-8)
    - **mapping**: Optional column mapping configuration
    - **validate_only**: If true, only validates without importing
    
    Returns import result with success/error details
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV format (.csv)")
    
    try:
        service = ProductImportExportService(db)
        result = service.import_from_csv(
            file.file,
            delimiter=delimiter,
            encoding=encoding,
            mapping=mapping,
            validate_only=validate_only
        )
        return result
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/import/xml", response_model=ProductImportResult)
async def import_products_from_xml(
    file: UploadFile = File(...),
    root_element: str = Query('products', description="Root XML element name"),
    product_element: str = Query('product', description="Product XML element name"),
    validate_only: bool = Query(False, description="Only validate without importing"),
    db: Session = Depends(get_db)
):
    """
    Import products from XML file
    
    - **file**: XML file to import
    - **root_element**: Root XML element name
    - **product_element**: Product XML element name
    - **validate_only**: If true, only validates without importing
    
    Returns import result with success/error details
    """
    if not file.filename.endswith('.xml'):
        raise HTTPException(status_code=400, detail="File must be XML format (.xml)")
    
    try:
        service = ProductImportExportService(db)
        result = service.import_from_xml(
            file.file,
            root_element=root_element,
            product_element=product_element,
            validate_only=validate_only
        )
        return result
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/import/api", response_model=ProductImportResult)
async def import_products_from_api(
    options: APIImportOptions,
    validate_only: bool = Query(False, description="Only validate without importing"),
    db: Session = Depends(get_db)
):
    """
    Import products from external API
    
    - **options**: API import configuration
    - **validate_only**: If true, only validates without importing
    
    Returns import result with success/error details
    """
    try:
        service = ProductImportExportService(db)
        result = service.import_from_api(
            api_url=options.api_url,
            api_key=options.api_key,
            headers=options.headers,
            params=options.params,
            validate_only=validate_only
        )
        return result
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


# ==================== EXPORT ENDPOINTS ====================

@router.post("/export/excel")
async def export_products_to_excel(
    request: ProductExportRequest,
    db: Session = Depends(get_db)
):
    """
    Export products to Excel file
    
    - **request**: Export configuration
    
    Returns Excel file for download
    """
    try:
        service = ProductImportExportService(db)
        excel_bytes = service.export_to_excel(
            filters=request.filters,
            columns=request.columns,
            include_metadata=request.include_metadata
        )
        
        return StreamingResponse(
            io.BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=products_export.xlsx"}
        )
    except ExportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/export/csv")
async def export_products_to_csv(
    request: ProductExportRequest,
    delimiter: str = Query(',', description="CSV delimiter"),
    encoding: str = Query('utf-8', description="File encoding"),
    db: Session = Depends(get_db)
):
    """
    Export products to CSV file
    
    - **request**: Export configuration
    - **delimiter**: CSV delimiter character
    - **encoding**: File encoding
    
    Returns CSV file for download
    """
    try:
        service = ProductImportExportService(db)
        csv_bytes = service.export_to_csv(
            filters=request.filters,
            columns=request.columns,
            delimiter=delimiter,
            encoding=encoding
        )
        
        return StreamingResponse(
            io.BytesIO(csv_bytes),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=products_export.csv"}
        )
    except ExportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/export/xml")
async def export_products_to_xml(
    request: ProductExportRequest,
    root_element: str = Query('products', description="Root XML element name"),
    product_element: str = Query('product', description="Product XML element name"),
    db: Session = Depends(get_db)
):
    """
    Export products to XML file
    
    - **request**: Export configuration
    - **root_element**: Root XML element name
    - **product_element**: Product XML element name
    
    Returns XML file for download
    """
    try:
        service = ProductImportExportService(db)
        xml_bytes = service.export_to_xml(
            filters=request.filters,
            columns=request.columns,
            root_element=root_element,
            product_element=product_element
        )
        
        return StreamingResponse(
            io.BytesIO(xml_bytes),
            media_type="application/xml",
            headers={"Content-Disposition": "attachment; filename=products_export.xml"}
        )
    except ExportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/export/json")
async def export_products_to_json(
    request: ProductExportRequest,
    pretty: bool = Query(True, description="Pretty print JSON"),
    db: Session = Depends(get_db)
):
    """
    Export products to JSON file
    
    - **request**: Export configuration
    - **pretty**: Pretty print JSON
    
    Returns JSON file for download
    """
    try:
        service = ProductImportExportService(db)
        json_bytes = service.export_to_json(
            filters=request.filters,
            columns=request.columns,
            pretty=pretty
        )
        
        return StreamingResponse(
            io.BytesIO(json_bytes),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=products_export.json"}
        )
    except ExportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


# ==================== TEMPLATE ENDPOINTS ====================

@router.get("/template/{format}", response_model=ProductImportTemplate)
async def get_import_template(
    format: ProductExportFormat,
    db: Session = Depends(get_db)
):
    """
    Get import template for specified format
    
    - **format**: Template format (excel, csv, xml, json)
    
    Returns template with required columns and sample data
    """
    columns = [
        "name",
        "sku",
        "category",
        "manufacturer",
        "price",
        "description",
        "spec_power",
        "spec_efficiency",
        "spec_warranty"
    ]
    
    sample_data = [
        {
            "name": "Solar Module 400W Monocrystalline",
            "sku": "SM-400-MONO-001",
            "category": "Solar Modules",
            "manufacturer": "SolarTech GmbH",
            "price": 299.99,
            "description": "High-efficiency monocrystalline solar module with 400W output",
            "spec_power": "400W",
            "spec_efficiency": "21.5%",
            "spec_warranty": "25 years"
        },
        {
            "name": "Inverter 5kW Hybrid",
            "sku": "INV-5K-HYB-001",
            "category": "Inverters",
            "manufacturer": "PowerTech AG",
            "price": 1499.99,
            "description": "5kW hybrid inverter with battery management",
            "spec_power": "5000W",
            "spec_efficiency": "97.5%",
            "spec_warranty": "10 years"
        }
    ]
    
    instructions = """
    Import Instructions:
    
    1. Required Fields:
       - name: Product name (required, max 255 characters)
       - sku: Stock Keeping Unit (required, unique, max 100 characters)
    
    2. Optional Fields:
       - category: Product category
       - manufacturer: Manufacturer name
       - price: Product price (numeric, non-negative)
       - description: Product description
    
    3. Specifications:
       - Add custom specifications with 'spec_' prefix
       - Example: spec_power, spec_efficiency, spec_warranty
    
    4. Format Requirements:
       - Excel: .xlsx or .xls format
       - CSV: UTF-8 encoding, comma-separated
       - XML: <products><product>...</product></products> structure
       - JSON: Array of product objects
    
    5. Validation:
       - SKU must be unique across all products
       - Price must be a valid number >= 0
       - All required fields must be filled
    """
    
    return ProductImportTemplate(
        format=format,
        columns=columns,
        sample_data=sample_data,
        instructions=instructions
    )


@router.get("/template/download/{format}")
async def download_import_template(
    format: ProductExportFormat,
    db: Session = Depends(get_db)
):
    """
    Download import template file
    
    - **format**: Template format (excel, csv, xml, json)
    
    Returns template file for download
    """
    import pandas as pd
    
    # Sample data
    data = {
        "name": ["Solar Module 400W", "Inverter 5kW"],
        "sku": ["SM-400-001", "INV-5K-001"],
        "category": ["Solar Modules", "Inverters"],
        "manufacturer": ["SolarTech", "PowerTech"],
        "price": [299.99, 1499.99],
        "description": ["High-efficiency module", "Hybrid inverter"],
        "spec_power": ["400W", "5000W"],
        "spec_efficiency": ["21.5%", "97.5%"],
        "spec_warranty": ["25 years", "10 years"]
    }
    
    df = pd.DataFrame(data)
    
    if format == ProductExportFormat.EXCEL:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Products', index=False)
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=product_import_template.xlsx"}
        )
    
    elif format == ProductExportFormat.CSV:
        output = io.StringIO()
        df.to_csv(output, index=False)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=product_import_template.csv"}
        )
    
    elif format == ProductExportFormat.JSON:
        json_data = df.to_dict(orient='records')
        import json
        json_str = json.dumps(json_data, indent=2)
        
        return StreamingResponse(
            io.BytesIO(json_str.encode('utf-8')),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=product_import_template.json"}
        )
    
    else:
        raise HTTPException(status_code=400, detail=f"Template format {format} not supported")


# ==================== VALIDATION ENDPOINTS ====================

@router.post("/validate/excel", response_model=ProductValidationResult)
async def validate_excel_file(
    file: UploadFile = File(...),
    mapping: Optional[ProductImportMapping] = None,
    db: Session = Depends(get_db)
):
    """
    Validate Excel file without importing
    
    - **file**: Excel file to validate
    - **mapping**: Optional column mapping configuration
    
    Returns validation result with errors and warnings
    """
    try:
        service = ProductImportExportService(db)
        result = service.import_from_excel(
            file.file,
            mapping=mapping,
            validate_only=True
        )
        
        return ProductValidationResult(
            valid=result.success,
            total_rows=result.total_rows,
            valid_rows=result.imported_count,
            invalid_rows=result.failed_count,
            errors=result.errors or []
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


# ==================== BULK OPERATIONS ====================

@router.post("/bulk/update")
async def bulk_update_products(
    request: ProductBulkUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Bulk update products
    
    - **request**: Bulk update configuration
    
    Returns number of products updated
    """
    try:
        from ...models.catalog_models import Product
        
        # Update products
        updated_count = db.query(Product).filter(
            Product.id.in_(request.product_ids)
        ).update(request.updates, synchronize_session=False)
        
        db.commit()
        
        return {
            "success": True,
            "updated_count": updated_count,
            "message": f"Successfully updated {updated_count} products"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk update failed: {str(e)}")


@router.post("/bulk/delete")
async def bulk_delete_products(
    request: ProductBulkDeleteRequest,
    db: Session = Depends(get_db)
):
    """
    Bulk delete products
    
    - **request**: Bulk delete configuration
    
    Returns number of products deleted
    """
    try:
        from ...models.catalog_models import Product
        
        # Delete products
        deleted_count = db.query(Product).filter(
            Product.id.in_(request.product_ids)
        ).delete(synchronize_session=False)
        
        db.commit()
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "message": f"Successfully deleted {deleted_count} products"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk delete failed: {str(e)}")
