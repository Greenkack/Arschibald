"""
API endpoints for results export functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
from sqlalchemy.orm import Session

from ...core.dependencies import get_db
from ...services.export_service import ExportService
from ...models.export_schemas import (
    ExportRequest, ExportResponse, BatchExportRequest, ExportHistory
)

router = APIRouter(prefix="/exports", tags=["exports"])

# Initialize export service
export_service = ExportService()


@router.post("/", response_model=ExportResponse)
async def create_export(
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Export a result in the specified format.
    
    Supported formats:
    - PDF: Professional report with charts and tables
    - Excel: Spreadsheet with multiple sheets and charts
    - CSV: Comma-separated values with German number formatting
    - JSON: Structured data export
    - XML: XML-formatted data export
    """
    # Fetch result data from database
    # This is a placeholder - implement actual data fetching
    result_data = await fetch_result_data(request.result_id, db)
    
    if not result_data:
        raise HTTPException(status_code=404, detail="Result not found")
    
    # Create export
    export_response = await export_service.export_result(request, result_data)
    
    # Schedule cleanup in background
    background_tasks.add_task(
        export_service.cleanup_expired_exports
    )
    
    return export_response


@router.post("/batch", response_model=List[ExportResponse])
async def create_batch_export(
    request: BatchExportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Export multiple results in batch.
    
    Can optionally combine all results into a single file.
    """
    # Fetch all result data
    results_data = []
    for result_id in request.result_ids:
        result_data = await fetch_result_data(result_id, db)
        if result_data:
            results_data.append(result_data)
    
    if not results_data:
        raise HTTPException(status_code=404, detail="No results found")
    
    # Create batch export
    exports = await export_service.batch_export(request, results_data)
    
    # Schedule cleanup
    background_tasks.add_task(
        export_service.cleanup_expired_exports
    )
    
    return exports


@router.get("/{export_id}/download")
async def download_export(export_id: str):
    """
    Download an exported file.
    
    Files are available for 24 hours after creation.
    """
    file_path = export_service.get_export_file(export_id)
    
    if not file_path or not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Export not found or expired"
        )
    
    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type='application/octet-stream'
    )


@router.get("/history", response_model=List[ExportHistory])
async def get_export_history(
    result_id: int = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get export history for a user or specific result.
    """
    # Placeholder - implement actual database query
    history = []
    return history


@router.delete("/{export_id}")
async def delete_export(export_id: str):
    """
    Delete an export file before it expires.
    """
    file_path = export_service.get_export_file(export_id)
    
    if not file_path:
        raise HTTPException(status_code=404, detail="Export not found")
    
    if file_path.exists():
        file_path.unlink()
    
    # Remove from cache
    if export_id in export_service.exports_cache:
        del export_service.exports_cache[export_id]
    
    return {"message": "Export deleted successfully"}


@router.get("/formats")
async def get_supported_formats():
    """
    Get list of supported export formats and their options.
    """
    return {
        "formats": [
            {
                "name": "pdf",
                "description": "PDF document with charts and tables",
                "options": {
                    "include_charts": "boolean",
                    "include_tables": "boolean",
                    "include_summary": "boolean",
                    "page_size": ["A4", "Letter", "Legal"],
                    "orientation": ["portrait", "landscape"]
                }
            },
            {
                "name": "excel",
                "description": "Excel spreadsheet with multiple sheets",
                "options": {
                    "include_charts": "boolean",
                    "include_formulas": "boolean",
                    "freeze_panes": "boolean",
                    "auto_filter": "boolean"
                }
            },
            {
                "name": "csv",
                "description": "CSV file with German number formatting",
                "options": {
                    "delimiter": "string",
                    "encoding": "string",
                    "include_headers": "boolean",
                    "decimal_separator": "string",
                    "thousands_separator": "string"
                }
            },
            {
                "name": "json",
                "description": "JSON structured data",
                "options": {
                    "pretty_print": "boolean",
                    "include_metadata": "boolean",
                    "date_format": ["iso", "unix", "custom"]
                }
            },
            {
                "name": "xml",
                "description": "XML formatted data",
                "options": {
                    "root_element": "string",
                    "include_schema": "boolean",
                    "pretty_print": "boolean"
                }
            }
        ]
    }


# Helper functions

async def fetch_result_data(result_id: int, db: Session) -> dict:
    """
    Fetch result data from database.
    This is a placeholder - implement actual data fetching logic.
    """
    # Example structure
    return {
        "id": result_id,
        "title": f"Solar Calculation Result #{result_id}",
        "summary": {
            "System Size": "10.5 kWp",
            "Annual Production": "12,500 kWh",
            "Total Cost": "16.999,00 €",
            "Payback Period": "8.5 years",
            "25-Year Savings": "45.000,00 €",
            "CO2 Savings": "125 tons"
        },
        "tables": {
            "Monthly Production": [
                ["Month", "Production (kWh)", "Consumption (kWh)", "Grid Feed-in (kWh)"],
                ["January", "650", "400", "250"],
                ["February", "800", "380", "420"],
                ["March", "1100", "350", "750"],
                ["April", "1250", "320", "930"],
                ["May", "1400", "300", "1100"],
                ["June", "1450", "280", "1170"],
                ["July", "1500", "270", "1230"],
                ["August", "1380", "290", "1090"],
                ["September", "1150", "310", "840"],
                ["October", "900", "340", "560"],
                ["November", "700", "370", "330"],
                ["December", "620", "390", "230"]
            ],
            "Financial Analysis": [
                ["Year", "Production Value (€)", "Savings (€)", "Cumulative Savings (€)"],
                ["1", "2.500,00", "1.800,00", "1.800,00"],
                ["2", "2.500,00", "1.800,00", "3.600,00"],
                ["3", "2.500,00", "1.800,00", "5.400,00"],
                ["5", "2.500,00", "1.800,00", "9.000,00"],
                ["10", "2.500,00", "1.800,00", "18.000,00"],
                ["15", "2.500,00", "1.800,00", "27.000,00"],
                ["20", "2.500,00", "1.800,00", "36.000,00"],
                ["25", "2.500,00", "1.800,00", "45.000,00"]
            ]
        },
        "chart_data": {
            "line_chart": {
                "title": "Monthly Energy Production",
                "x_label": "Month",
                "y_label": "Energy (kWh)",
                "data": [
                    {"x": "Jan", "y": 650},
                    {"x": "Feb", "y": 800},
                    {"x": "Mar", "y": 1100},
                    {"x": "Apr", "y": 1250},
                    {"x": "May", "y": 1400},
                    {"x": "Jun", "y": 1450},
                    {"x": "Jul", "y": 1500},
                    {"x": "Aug", "y": 1380},
                    {"x": "Sep", "y": 1150},
                    {"x": "Oct", "y": 900},
                    {"x": "Nov", "y": 700},
                    {"x": "Dec", "y": 620}
                ]
            }
        }
    }
