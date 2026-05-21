# Reporting and Analytics API Endpoints

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.core.dependencies import get_db, get_current_user
from backend.services.reporting_service import ReportingService
from backend.models.reporting_schemas import (
    ReportCreate, ReportUpdate, ReportExecute, ReportResponse,
    ScheduleCreate, ScheduleUpdate, ScheduleResponse,
    DashboardCreate, DashboardResponse, WidgetCreate, WidgetUpdate, WidgetResponse,
    KPICreate, KPIResponse, PredictionRequest, PredictionResponse,
    ExportRequest, ExportResponse
)
from backend.models.reporting_models import Report, Dashboard, KPI

router = APIRouter(prefix="/reporting", tags=["reporting"])


# ==================== Report Builder Endpoints ====================

@router.post("/reports", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: ReportCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new report definition"""
    service = ReportingService(db)
    report = service.create_report(report_data, current_user["id"])
    
    return {
        "id": report.id,
        "name": report.name,
        "report_type": report.report_type,
        "created_at": report.created_at
    }


@router.get("/reports", response_model=List[dict])
async def list_reports(
    report_type: Optional[str] = None,
    is_public: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all reports"""
    query = db.query(Report)
    
    # Filter by user's reports or public reports
    query = query.filter(
        (Report.owner_id == current_user["id"]) | (Report.is_public == True)
    )
    
    if report_type:
        query = query.filter(Report.report_type == report_type)
    
    if is_public is not None:
        query = query.filter(Report.is_public == is_public)
    
    reports = query.all()
    
    return [
        {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "report_type": r.report_type,
            "is_public": r.is_public,
            "tags": r.tags,
            "created_at": r.created_at,
            "updated_at": r.updated_at
        }
        for r in reports
    ]


@router.get("/reports/{report_id}", response_model=dict)
async def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get report details"""
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check access
    if report.owner_id != current_user["id"] and not report.is_public:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "id": report.id,
        "name": report.name,
        "description": report.description,
        "report_type": report.report_type,
        "definition": report.definition,
        "is_public": report.is_public,
        "tags": report.tags,
        "created_at": report.created_at,
        "updated_at": report.updated_at
    }


@router.put("/reports/{report_id}", response_model=dict)
async def update_report(
    report_id: int,
    report_data: ReportUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update report definition"""
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if report.owner_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update fields
    if report_data.definition:
        report.definition = report_data.definition.dict()
    if report_data.name:
        report.name = report_data.name
    if report_data.description is not None:
        report.description = report_data.description
    if report_data.is_public is not None:
        report.is_public = report_data.is_public
    if report_data.tags is not None:
        report.tags = report_data.tags
    
    report.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Report updated successfully"}


@router.delete("/reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a report"""
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if report.owner_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    db.delete(report)
    db.commit()


@router.post("/reports/execute", response_model=ReportResponse)
async def execute_report(
    execute_request: ReportExecute,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Execute a report and return results"""
    service = ReportingService(db)
    
    try:
        result = service.execute_report(execute_request, current_user["id"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Scheduled Reports Endpoints ====================

@router.post("/schedules", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule_data: ScheduleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a report schedule"""
    service = ReportingService(db)
    schedule = service.create_schedule(schedule_data)
    
    return {
        "id": schedule.id,
        "report_id": schedule.report_id,
        "frequency": schedule.frequency,
        "next_run": schedule.next_run
    }


@router.get("/schedules", response_model=List[ScheduleResponse])
async def list_schedules(
    report_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all schedules"""
    from backend.models.reporting_models import ReportSchedule
    
    query = db.query(ReportSchedule).join(Report).filter(
        Report.owner_id == current_user["id"]
    )
    
    if report_id:
        query = query.filter(ReportSchedule.report_id == report_id)
    
    schedules = query.all()
    
    return [
        ScheduleResponse(
            id=s.id,
            report_id=s.report_id,
            report_name=s.report.name,
            frequency=s.frequency,
            time_of_day=s.time_of_day,
            recipients=s.recipients,
            format=s.format,
            enabled=s.enabled,
            last_run=s.last_run,
            next_run=s.next_run,
            created_at=s.created_at
        )
        for s in schedules
    ]


@router.put("/schedules/{schedule_id}", response_model=dict)
async def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a schedule"""
    from backend.models.reporting_models import ReportSchedule
    
    schedule = db.query(ReportSchedule).filter(ReportSchedule.id == schedule_id).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Check access
    if schedule.report.owner_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update fields
    if schedule_data.frequency:
        schedule.frequency = schedule_data.frequency
    if schedule_data.time_of_day:
        schedule.time_of_day = schedule_data.time_of_day
    if schedule_data.recipients:
        schedule.recipients = schedule_data.recipients
    if schedule_data.format:
        schedule.format = schedule_data.format
    if schedule_data.enabled is not None:
        schedule.enabled = schedule_data.enabled
    
    # Recalculate next run
    service = ReportingService(db)
    schedule.next_run = service._calculate_next_run(schedule.frequency, schedule.time_of_day)
    
    db.commit()
    
    return {"message": "Schedule updated successfully"}


@router.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a schedule"""
    from backend.models.reporting_models import ReportSchedule
    
    schedule = db.query(ReportSchedule).filter(ReportSchedule.id == schedule_id).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    if schedule.report.owner_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    db.delete(schedule)
    db.commit()


# ==================== Dashboard Endpoints ====================

@router.post("/dashboards", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_dashboard(
    dashboard_data: DashboardCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new dashboard"""
    service = ReportingService(db)
    dashboard = service.create_dashboard(dashboard_data, current_user["id"])
    
    return {
        "id": dashboard.id,
        "name": dashboard.name,
        "created_at": dashboard.created_at
    }


@router.get("/dashboards", response_model=List[dict])
async def list_dashboards(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all dashboards"""
    dashboards = db.query(Dashboard).filter(
        (Dashboard.owner_id == current_user["id"]) | (Dashboard.is_public == True)
    ).all()
    
    return [
        {
            "id": d.id,
            "name": d.name,
            "description": d.description,
            "is_public": d.is_public,
            "widget_count": len(d.widgets),
            "created_at": d.created_at
        }
        for d in dashboards
    ]


@router.get("/dashboards/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(
    dashboard_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get dashboard with all widgets"""
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    if dashboard.owner_id != current_user["id"] and not dashboard.is_public:
        raise HTTPException(status_code=403, detail="Access denied")
    
    service = ReportingService(db)
    
    widgets = []
    for widget in dashboard.widgets:
        widget_data = service.get_widget_data(widget.id)
        widgets.append(
            WidgetResponse(
                id=widget.id,
                dashboard_id=widget.dashboard_id,
                config=widget.config,
                position_x=widget.position_x,
                position_y=widget.position_y,
                data=widget_data["data"],
                last_updated=widget_data["last_updated"]
            )
        )
    
    return DashboardResponse(
        id=dashboard.id,
        name=dashboard.name,
        description=dashboard.description,
        is_public=dashboard.is_public,
        layout=dashboard.layout,
        widgets=widgets,
        created_at=dashboard.created_at,
        updated_at=dashboard.updated_at
    )


@router.post("/dashboards/{dashboard_id}/widgets", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_widget(
    dashboard_id: int,
    widget_data: WidgetCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add a widget to dashboard"""
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    if dashboard.owner_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    service = ReportingService(db)
    widget = service.create_widget(widget_data)
    
    return {
        "id": widget.id,
        "dashboard_id": widget.dashboard_id,
        "created_at": widget.created_at
    }


# ==================== KPI Endpoints ====================

@router.post("/kpis", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_kpi(
    kpi_data: KPICreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new KPI"""
    service = ReportingService(db)
    kpi = service.create_kpi(kpi_data, current_user["id"])
    
    return {
        "id": kpi.id,
        "name": kpi.name,
        "metric": kpi.metric,
        "created_at": kpi.created_at
    }


@router.get("/kpis", response_model=List[dict])
async def list_kpis(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all KPIs"""
    kpis = db.query(KPI).filter(KPI.owner_id == current_user["id"]).all()
    
    return [
        {
            "id": k.id,
            "name": k.name,
            "metric": k.metric,
            "created_at": k.created_at
        }
        for k in kpis
    ]


@router.get("/kpis/{kpi_id}/calculate", response_model=KPIResponse)
async def calculate_kpi(
    kpi_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Calculate current KPI value"""
    kpi = db.query(KPI).filter(KPI.id == kpi_id).first()
    
    if not kpi:
        raise HTTPException(status_code=404, detail="KPI not found")
    
    if kpi.owner_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    service = ReportingService(db)
    result = service.calculate_kpi(kpi_id)
    
    return result


# ==================== Predictive Analytics Endpoints ====================

@router.post("/predictions", response_model=PredictionResponse)
async def create_prediction(
    prediction_request: PredictionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate predictions using machine learning"""
    service = ReportingService(db)
    
    try:
        result = service.create_prediction(prediction_request, current_user["id"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Data Export Endpoints ====================

@router.post("/exports", response_model=ExportResponse)
async def export_data(
    export_request: ExportRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Export data in specified format"""
    service = ReportingService(db)
    
    try:
        result = service.export_data(export_request, current_user["id"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exports/download/{export_id}")
async def download_export(
    export_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Download exported file"""
    from backend.models.reporting_models import DataExport
    from fastapi.responses import FileResponse
    
    export = db.query(DataExport).filter(DataExport.id == export_id).first()
    
    if not export:
        raise HTTPException(status_code=404, detail="Export not found")
    
    if export.exported_by != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if datetime.now() > export.expires_at:
        raise HTTPException(status_code=410, detail="Export has expired")
    
    return FileResponse(
        path=export.file_path,
        filename=export.file_name,
        media_type="application/octet-stream"
    )
