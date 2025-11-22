"""
Component Toggle API Endpoints

API endpoints for managing component-level feature toggles.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from backend.core.dependencies import get_db, get_current_user
from backend.services.component_toggle_service import ComponentToggleService
from backend.models.component_toggle_schemas import (
    ComponentToggleCreate,
    ComponentToggleUpdate,
    ComponentToggleResponse,
    ComponentToggleListResponse,
    ChartToggleRequest,
    FormFieldToggleRequest,
    CalculationOptionToggleRequest,
    ExportFormatToggleRequest,
    ThemeToggleRequest,
    LanguageToggleRequest,
    BulkToggleRequest,
    VisibleChartsResponse,
    EnabledFormFieldsResponse,
    EnabledCalculationOptionsResponse,
    AvailableExportFormatsResponse,
    AvailableThemesResponse,
    AvailableLanguagesResponse
)
from backend.models.component_toggle_models import ComponentToggleCategory


router = APIRouter(prefix="/component-toggles", tags=["Component Toggles"])


# Chart Visibility Toggles

@router.get("/charts", response_model=List[ComponentToggleResponse])
def get_chart_toggles(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all chart visibility toggles"""
    service = ComponentToggleService(db)
    return service.get_chart_toggles(user_id=current_user.id)


@router.post("/charts/toggle", response_model=ComponentToggleResponse)
def toggle_chart(
    request: ChartToggleRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Toggle visibility of a specific chart"""
    service = ComponentToggleService(db)
    return service.toggle_chart(
        chart_type=request.chart_type,
        enabled=request.enabled,
        user_id=current_user.id
    )


@router.get("/charts/visible", response_model=VisibleChartsResponse)
def get_visible_charts(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of visible chart types"""
    service = ComponentToggleService(db)
    charts = service.get_visible_charts(user_id=current_user.id)
    return VisibleChartsResponse(charts=charts)


# Form Field Toggles

@router.get("/form-fields", response_model=List[ComponentToggleResponse])
def get_form_field_toggles(
    form_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all form field toggles"""
    service = ComponentToggleService(db)
    return service.get_form_field_toggles(
        form_name=form_name,
        user_id=current_user.id
    )


@router.post("/form-fields/toggle", response_model=ComponentToggleResponse)
def toggle_form_field(
    request: FormFieldToggleRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Toggle visibility/editability of a form field"""
    service = ComponentToggleService(db)
    return service.toggle_form_field(
        form_name=request.form_name,
        field_key=request.field_key,
        enabled=request.enabled,
        user_id=current_user.id
    )


@router.get("/form-fields/enabled/{form_name}", response_model=EnabledFormFieldsResponse)
def get_enabled_form_fields(
    form_name: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of enabled form fields for a specific form"""
    service = ComponentToggleService(db)
    fields = service.get_enabled_form_fields(
        form_name=form_name,
        user_id=current_user.id
    )
    return EnabledFormFieldsResponse(form_name=form_name, fields=fields)


# Calculation Option Toggles

@router.get("/calculation-options", response_model=List[ComponentToggleResponse])
def get_calculation_option_toggles(
    calculator_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all calculation option toggles"""
    service = ComponentToggleService(db)
    return service.get_calculation_option_toggles(
        calculator_type=calculator_type,
        user_id=current_user.id
    )


@router.post("/calculation-options/toggle", response_model=ComponentToggleResponse)
def toggle_calculation_option(
    request: CalculationOptionToggleRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Toggle a calculation option"""
    service = ComponentToggleService(db)
    return service.toggle_calculation_option(
        calculator_type=request.calculator_type,
        option_key=request.option_key,
        enabled=request.enabled,
        user_id=current_user.id
    )


@router.get(
    "/calculation-options/enabled/{calculator_type}",
    response_model=EnabledCalculationOptionsResponse
)
def get_enabled_calculation_options(
    calculator_type: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of enabled calculation options"""
    service = ComponentToggleService(db)
    options = service.get_enabled_calculation_options(
        calculator_type=calculator_type,
        user_id=current_user.id
    )
    return EnabledCalculationOptionsResponse(
        calculator_type=calculator_type,
        options=options
    )


# Export Format Toggles

@router.get("/export-formats", response_model=List[ComponentToggleResponse])
def get_export_format_toggles(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all export format toggles"""
    service = ComponentToggleService(db)
    return service.get_export_format_toggles(user_id=current_user.id)


@router.post("/export-formats/toggle", response_model=ComponentToggleResponse)
def toggle_export_format(
    request: ExportFormatToggleRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Toggle availability of an export format"""
    service = ComponentToggleService(db)
    return service.toggle_export_format(
        format_key=request.format_key,
        enabled=request.enabled,
        user_id=current_user.id
    )


@router.get("/export-formats/available", response_model=AvailableExportFormatsResponse)
def get_available_export_formats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of available export formats"""
    service = ComponentToggleService(db)
    formats = service.get_available_export_formats(user_id=current_user.id)
    return AvailableExportFormatsResponse(formats=formats)


# UI Theme Toggles

@router.get("/themes", response_model=List[ComponentToggleResponse])
def get_theme_toggles(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all UI theme toggles"""
    service = ComponentToggleService(db)
    return service.get_theme_toggles(user_id=current_user.id)


@router.post("/themes/toggle", response_model=ComponentToggleResponse)
def toggle_theme(
    request: ThemeToggleRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Toggle availability of a UI theme"""
    service = ComponentToggleService(db)
    return service.toggle_theme(
        theme_key=request.theme_key,
        enabled=request.enabled,
        user_id=current_user.id
    )


@router.get("/themes/available", response_model=AvailableThemesResponse)
def get_available_themes(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of available UI themes"""
    service = ComponentToggleService(db)
    themes = service.get_available_themes(user_id=current_user.id)
    return AvailableThemesResponse(themes=themes)


# Language Toggles

@router.get("/languages", response_model=List[ComponentToggleResponse])
def get_language_toggles(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all language toggles"""
    service = ComponentToggleService(db)
    return service.get_language_toggles(user_id=current_user.id)


@router.post("/languages/toggle", response_model=ComponentToggleResponse)
def toggle_language(
    request: LanguageToggleRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Toggle availability of a language"""
    service = ComponentToggleService(db)
    return service.toggle_language(
        language_code=request.language_code,
        enabled=request.enabled,
        user_id=current_user.id
    )


@router.get("/languages/available", response_model=AvailableLanguagesResponse)
def get_available_languages(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of available languages"""
    service = ComponentToggleService(db)
    languages = service.get_available_languages(user_id=current_user.id)
    return AvailableLanguagesResponse(languages=languages)


# Bulk Operations

@router.post("/bulk-toggle")
def bulk_toggle(
    request: BulkToggleRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Bulk enable/disable all toggles in a category"""
    service = ComponentToggleService(db)
    count = service.bulk_toggle(
        category=request.category,
        enabled=request.enabled,
        user_id=current_user.id
    )
    return {"message": f"Updated {count} toggles", "count": count}


@router.get("/all", response_model=ComponentToggleListResponse)
def get_all_toggles(
    category: Optional[ComponentToggleCategory] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all component toggles with optional filtering"""
    service = ComponentToggleService(db)
    return service.get_all_toggles(
        user_id=current_user.id,
        category=category
    )


@router.post("/reset")
def reset_to_defaults(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Reset all toggles to default values"""
    service = ComponentToggleService(db)
    count = service.reset_to_defaults(user_id=current_user.id)
    return {"message": f"Reset {count} toggles to defaults", "count": count}


# CRUD Operations

@router.post("/", response_model=ComponentToggleResponse, status_code=status.HTTP_201_CREATED)
def create_toggle(
    toggle: ComponentToggleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new component toggle"""
    # Implementation would use the service to create a toggle
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Direct toggle creation not yet implemented. Use specific toggle endpoints."
    )


@router.put("/{toggle_id}", response_model=ComponentToggleResponse)
def update_toggle(
    toggle_id: int,
    toggle_update: ComponentToggleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a component toggle"""
    # Implementation would use the service to update a toggle
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Direct toggle update not yet implemented. Use specific toggle endpoints."
    )


@router.delete("/{toggle_id}")
def delete_toggle(
    toggle_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a component toggle"""
    # Implementation would use the service to delete a toggle
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Direct toggle deletion not yet implemented. Use reset endpoint."
    )
