# backend/api/v1/preferences.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from backend.core.dependencies import get_db, get_current_user
from backend.services.preference_service import PreferenceService
from backend.models.preference_schemas import (
    PreferenceCreate, PreferenceUpdate, PreferenceResponse,
    PreferenceBulkUpdate, PreferenceExport, PreferenceImport,
    PreferenceTemplateCreate, PreferenceTemplateResponse,
    PreferenceSyncRequest, PreferenceSyncResponse,
    PreferenceResetRequest, PreferenceSearchRequest,
    PreferenceStatistics
)

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("/", response_model=Dict[str, Dict[str, Any]])
async def get_all_preferences(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all preferences for the current user"""
    service = PreferenceService(db)
    return service.get_all_preferences(current_user["id"])


@router.get("/category/{category}", response_model=List[PreferenceResponse])
async def get_preferences_by_category(
    category: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all preferences for a specific category"""
    service = PreferenceService(db)
    preferences = service.get_preferences_by_category(current_user["id"], category)
    return preferences


@router.get("/{category}/{key}", response_model=PreferenceResponse)
async def get_preference(
    category: str,
    key: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific preference"""
    service = PreferenceService(db)
    preference = service.get_preference(current_user["id"], category, key)
    
    if not preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preference {category}.{key} not found"
        )
    
    return preference


@router.post("/", response_model=PreferenceResponse, status_code=status.HTTP_201_CREATED)
async def create_preference(
    preference: PreferenceCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new preference"""
    service = PreferenceService(db)
    
    try:
        return service.create_preference(current_user["id"], preference)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{category}/{key}", response_model=PreferenceResponse)
async def update_preference(
    category: str,
    key: str,
    update: PreferenceUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a preference"""
    service = PreferenceService(db)
    
    try:
        return service.update_preference(current_user["id"], category, key, update)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/bulk", response_model=List[PreferenceResponse])
async def bulk_update_preferences(
    bulk_update: PreferenceBulkUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk update multiple preferences"""
    service = PreferenceService(db)
    return service.bulk_update_preferences(current_user["id"], bulk_update.preferences)


@router.delete("/{category}/{key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_preference(
    category: str,
    key: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a preference (revert to default)"""
    service = PreferenceService(db)
    
    if not service.delete_preference(current_user["id"], category, key):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preference {category}.{key} not found"
        )


@router.post("/reset", response_model=Dict[str, int])
async def reset_preferences(
    reset_request: PreferenceResetRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset preferences to defaults"""
    service = PreferenceService(db)
    count = service.reset_preferences(current_user["id"], reset_request)
    
    return {"reset_count": count}


@router.get("/export/all", response_model=PreferenceExport)
async def export_preferences(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export all preferences"""
    service = PreferenceService(db)
    return service.export_preferences(current_user["id"])


@router.post("/import", response_model=Dict[str, int])
async def import_preferences(
    import_data: PreferenceImport,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import preferences"""
    service = PreferenceService(db)
    count = service.import_preferences(current_user["id"], import_data)
    
    return {"imported_count": count}


@router.post("/sync", response_model=PreferenceSyncResponse)
async def sync_preferences(
    sync_request: PreferenceSyncRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync preferences across devices"""
    service = PreferenceService(db)
    sync_record = service.sync_preferences(current_user["id"], sync_request)
    
    return PreferenceSyncResponse(
        sync_id=sync_record.id,
        status=sync_record.sync_status,
        synced_at=sync_record.last_sync_at,
        conflicts=[]
    )


@router.get("/statistics", response_model=PreferenceStatistics)
async def get_statistics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get preference statistics"""
    service = PreferenceService(db)
    return service.get_statistics(current_user["id"])


@router.post("/search", response_model=List[PreferenceResponse])
async def search_preferences(
    search_request: PreferenceSearchRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search preferences"""
    service = PreferenceService(db)
    return service.search_preferences(current_user["id"], search_request)


# Template endpoints
@router.get("/templates", response_model=List[PreferenceTemplateResponse])
async def get_templates(
    category: str = None,
    db: Session = Depends(get_db)
):
    """Get preference templates"""
    service = PreferenceService(db)
    return service.get_templates(category)


@router.post("/templates", response_model=PreferenceTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template: PreferenceTemplateCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a preference template"""
    service = PreferenceService(db)
    return service.create_template(template)


@router.post("/templates/{template_id}/apply", response_model=Dict[str, int])
async def apply_template(
    template_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply a template to user preferences"""
    service = PreferenceService(db)
    
    try:
        count = service.apply_template(current_user["id"], template_id)
        return {"applied_count": count}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
