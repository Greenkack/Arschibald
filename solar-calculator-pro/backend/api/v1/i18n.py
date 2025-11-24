"""
i18n API Endpoints
Handles translation management and language preferences
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
import zipfile
import io
from datetime import datetime

from ...core.dependencies import get_db
from ...services.i18n_service import I18nService
from ...models.i18n_schemas import (
    TranslationCreate,
    TranslationUpdate,
    TranslationResponse,
    LanguagePreference,
    TranslationExport,
)

router = APIRouter(prefix="/i18n", tags=["i18n"])


@router.get("/translations")
async def get_translations(
    namespace: Optional[str] = "all",
    language: Optional[str] = None,
    db: Session = Depends(get_db),
) -> List[TranslationResponse]:
    """
    Get all translations, optionally filtered by namespace and language
    """
    service = I18nService(db)
    return service.get_translations(namespace=namespace, language=language)


@router.get("/{language}/{namespace}")
async def get_translation_resource(
    language: str,
    namespace: str,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get translation resource for a specific language and namespace
    Used by i18next backend
    """
    service = I18nService(db)
    return service.get_translation_resource(language, namespace)


@router.post("/translations")
async def create_translation(
    translation: TranslationCreate,
    db: Session = Depends(get_db),
) -> TranslationResponse:
    """
    Create a new translation
    """
    service = I18nService(db)
    return service.create_translation(translation)


@router.put("/translations")
async def update_translation(
    translation: TranslationUpdate,
    db: Session = Depends(get_db),
) -> TranslationResponse:
    """
    Update an existing translation
    """
    service = I18nService(db)
    return service.update_translation(translation)


@router.delete("/translations/{key}")
async def delete_translation(
    key: str,
    namespace: str,
    db: Session = Depends(get_db),
):
    """
    Delete a translation
    """
    service = I18nService(db)
    service.delete_translation(key, namespace)
    return {"message": "Translation deleted successfully"}


@router.get("/export")
async def export_translations(
    format: str = "json",
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """
    Export all translations as a ZIP file
    """
    service = I18nService(db)
    translations = service.export_translations()

    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for lang, namespaces in translations.items():
            for namespace, content in namespaces.items():
                filename = f"{lang}/{namespace}.json"
                zip_file.writestr(filename, json.dumps(content, indent=2, ensure_ascii=False))

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=translations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        },
    )


@router.post("/import")
async def import_translations(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Import translations from a ZIP or JSON file
    """
    service = I18nService(db)

    if file.filename.endswith('.zip'):
        # Handle ZIP file
        content = await file.read()
        zip_buffer = io.BytesIO(content)

        with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
            for filename in zip_file.namelist():
                if filename.endswith('.json'):
                    # Extract language and namespace from path
                    parts = filename.split('/')
                    if len(parts) == 2:
                        language = parts[0]
                        namespace = parts[1].replace('.json', '')

                        # Read and parse JSON
                        json_content = zip_file.read(filename)
                        translations = json.loads(json_content)

                        # Import translations
                        service.import_translations(language, namespace, translations)

    elif file.filename.endswith('.json'):
        # Handle single JSON file
        content = await file.read()
        translations = json.loads(content)

        # Assume format: { "language": { "namespace": { "key": "value" } } }
        for language, namespaces in translations.items():
            for namespace, content in namespaces.items():
                service.import_translations(language, namespace, content)

    else:
        raise HTTPException(status_code=400, detail="Invalid file format. Only .zip and .json files are supported.")

    return {"message": "Translations imported successfully"}


@router.get("/languages")
async def get_supported_languages() -> List[Dict[str, Any]]:
    """
    Get list of supported languages
    """
    from ...i18n.i18n_config import SUPPORTED_LANGUAGES

    return [
        {
            "code": code,
            "name": info["name"],
            "nativeName": info["nativeName"],
            "flag": info["flag"],
            "rtl": info["rtl"],
        }
        for code, info in SUPPORTED_LANGUAGES.items()
    ]


@router.put("/user/language")
async def update_user_language(
    preference: LanguagePreference,
    db: Session = Depends(get_db),
):
    """
    Update user's language preference
    """
    service = I18nService(db)
    service.update_user_language(preference.user_id, preference.language)
    return {"message": "Language preference updated successfully"}


@router.get("/user/{user_id}/language")
async def get_user_language(
    user_id: int,
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """
    Get user's language preference
    """
    service = I18nService(db)
    language = service.get_user_language(user_id)
    return {"language": language}


@router.get("/missing")
async def get_missing_translations(
    language: str,
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Get list of missing translations for a language
    """
    service = I18nService(db)
    return service.get_missing_translations(language)


@router.post("/auto-translate")
async def auto_translate(
    source_language: str,
    target_language: str,
    namespace: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Auto-translate missing translations using translation service
    """
    service = I18nService(db)
    count = service.auto_translate(source_language, target_language, namespace)
    return {"message": f"Auto-translated {count} translations"}


@router.get("/statistics")
async def get_translation_statistics(
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get translation statistics (completion percentage, missing translations, etc.)
    """
    service = I18nService(db)
    return service.get_statistics()
