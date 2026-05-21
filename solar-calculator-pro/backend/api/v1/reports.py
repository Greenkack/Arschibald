# backend/api/v1/reports.py

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from typing import List, Optional
from sqlalchemy.orm import Session

from ...core.dependencies import get_db, get_current_user
from ...models.report_schemas import (
    ReportGenerationRequest, ReportResponse,
    ReportHistoryResponse, ReportListItem,
    ReportType, ReportFormat
)
from ...services.report_generation_service import ReportGenerationService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportGenerationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a report based on project data
    
    - **project_id**: ID of the project to generate report for
    - **report_type**: Type of report (detailed, executive, technical, financial, environmental, custom)
    - **format**: Output format (pdf, html, json, excel, csv)
    - **template_id**: Optional template ID to use
    - **custom_sections**: Optional custom sections for custom reports
    """
    try:
        # Get project data from database
        # This is a placeholder - implement actual project data retrieval
        project_data = {
            "name": "Sample Solar Project",
            "customer_name": "John Doe",
            "location": "Berlin, Germany",
            "system_size": 10.5,
            "module_count": 30,
            "module_type": "Premium 350W",
            "inverter": "SMA Sunny Tripower 10.0",
            "battery": "Tesla Powerwall 2",
            "mounting_type": "Roof-mounted",
            "annual_production": 12500,
            "self_consumption_rate": 0.35,
            "grid_feed_in": 8125,
            "performance_ratio": 0.85,
            "total_cost": 16999.00,
            "annual_savings": 1850.00,
            "payback_period": 9.2,
            "roi_25_years": 245.5,
            "roi_percentage": 245.5,
            "npv": 25000.00,
            "irr": 0.12,
            "co2_savings": 6250,
            "co2_savings_25_years": 156250,
            "trees_equivalent": 312,
            "cars_equivalent": 1,
            "roof_area": 60.0,
            "roof_angle": 30.0,
            "orientation": "South",
            "shading_factor": 0.95,
            "recommendations": [
                "System is optimally sized for your consumption",
                "Consider adding battery storage for increased self-consumption",
                "Regular maintenance recommended every 6 months"
            ],
            "monthly_production": [800, 950, 1200, 1350, 1450, 1500, 1480, 1400, 1250, 1050, 850, 750],
            "cost_breakdown": {
                "modules": 6000,
                "inverter": 2500,
                "battery": 5000,
                "mounting": 1500,
                "installation": 1500,
                "permits": 499
            }
        }
        
        # Generate report
        service = ReportGenerationService()
        result = await service.generate_report(
            request=request,
            project_data=project_data,
            user_id=current_user.get("sub", "unknown")
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Download a generated report"""
    try:
        service = ReportGenerationService()
        
        # Find report file
        report_files = list(service.output_dir.glob(f"{report_id}.*"))
        
        if not report_files:
            raise HTTPException(status_code=404, detail="Report not found")
        
        report_file = report_files[0]
        
        return FileResponse(
            path=str(report_file),
            filename=report_file.name,
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download report: {str(e)}")


@router.get("/{report_id}/preview")
async def preview_report(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Preview a generated report (HTML only)"""
    try:
        service = ReportGenerationService()
        
        # Find HTML report file
        html_file = service.output_dir / f"{report_id}.html"
        
        if not html_file.exists():
            raise HTTPException(status_code=404, detail="HTML preview not available")
        
        return FileResponse(
            path=str(html_file),
            media_type="text/html"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to preview report: {str(e)}")


@router.get("/history", response_model=ReportHistoryResponse)
async def get_report_history(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    report_type: Optional[ReportType] = Query(None, description="Filter by report type"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get report generation history"""
    try:
        # This is a placeholder - implement actual history retrieval from database
        reports = [
            ReportListItem(
                report_id="123e4567-e89b-12d3-a456-426614174000",
                project_id=1,
                project_name="Sample Solar Project",
                report_type=ReportType.DETAILED,
                format=ReportFormat.PDF,
                generated_at="2024-01-15T10:30:00",
                file_size=1024000,
                download_url="/api/v1/reports/123e4567-e89b-12d3-a456-426614174000/download"
            )
        ]
        
        return ReportHistoryResponse(
            reports=reports,
            total=len(reports),
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve report history: {str(e)}")


@router.delete("/{report_id}")
async def delete_report(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a generated report"""
    try:
        service = ReportGenerationService()
        
        # Find and delete all report files with this ID
        report_files = list(service.output_dir.glob(f"{report_id}.*"))
        
        if not report_files:
            raise HTTPException(status_code=404, detail="Report not found")
        
        for report_file in report_files:
            report_file.unlink()
        
        return {"message": "Report deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete report: {str(e)}")


@router.get("/types")
async def get_report_types():
    """Get available report types"""
    return {
        "report_types": [
            {
                "value": ReportType.DETAILED,
                "label": "Detailed Report",
                "description": "Comprehensive report with all project details, calculations, and analysis"
            },
            {
                "value": ReportType.EXECUTIVE,
                "label": "Executive Summary",
                "description": "High-level summary for decision makers with key metrics and recommendations"
            },
            {
                "value": ReportType.TECHNICAL,
                "label": "Technical Report",
                "description": "Detailed technical specifications, system design, and installation requirements"
            },
            {
                "value": ReportType.FINANCIAL,
                "label": "Financial Report",
                "description": "Comprehensive financial analysis including ROI, cash flow, and financing options"
            },
            {
                "value": ReportType.ENVIRONMENTAL,
                "label": "Environmental Report",
                "description": "Environmental impact analysis including CO₂ savings and sustainability metrics"
            },
            {
                "value": ReportType.CUSTOM,
                "label": "Custom Report",
                "description": "Customizable report with user-selected sections and content"
            }
        ],
        "formats": [
            {"value": ReportFormat.PDF, "label": "PDF", "description": "Portable Document Format"},
            {"value": ReportFormat.HTML, "label": "HTML", "description": "Web page format"},
            {"value": ReportFormat.JSON, "label": "JSON", "description": "Machine-readable data format"},
            {"value": ReportFormat.EXCEL, "label": "Excel", "description": "Microsoft Excel spreadsheet"},
            {"value": ReportFormat.CSV, "label": "CSV", "description": "Comma-separated values"}
        ]
    }
