"""
i18n Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime


class TranslationBase(BaseModel):
    """Base translation schema"""

    key: str = Field(..., description="Translation key (e.g., 'common.save')")
    namespace: str = Field(..., description="Namespace (e.g., 'common', 'errors')")


class TranslationCreate(TranslationBase):
    """Schema for creating a translation"""

    translations: Dict[str, str] = Field(
        ..., description="Translations for all languages"
    )
    modified_by: str = Field(default="system", description="User who created the translation")


class TranslationUpdate(TranslationBase):
    """Schema for updating a translation"""

    translations: Dict[str, str] = Field(
        ..., description="Updated translations for all languages"
    )
    modified_by: str = Field(default="system", description="User who updated the translation")


class TranslationResponse(TranslationBase):
    """Schema for translation response"""

    translations: Dict[str, str] = Field(..., description="Translations for all languages")
    lastModified: str = Field(..., description="Last modification timestamp")
    modifiedBy: str = Field(..., description="User who last modified the translation")

    class Config:
        from_attributes = True


class TranslationResource(BaseModel):
    """Schema for i18next resource"""

    language: str
    namespace: str
    translations: Dict[str, any]


class LanguagePreference(BaseModel):
    """Schema for user language preference"""

    user_id: int
    language: str = Field(..., pattern="^[a-z]{2}(-[A-Z]{2})?$")


class TranslationExport(BaseModel):
    """Schema for translation export"""

    format: str = Field(default="json", pattern="^(json|csv|xlsx)$")
    languages: Optional[list[str]] = None
    namespaces: Optional[list[str]] = None


class TranslationImport(BaseModel):
    """Schema for translation import"""

    format: str = Field(..., pattern="^(json|csv|xlsx)$")
    overwrite: bool = Field(default=False, description="Overwrite existing translations")


class TranslationStatistics(BaseModel):
    """Schema for translation statistics"""

    total_keys: int
    languages: Dict[str, Dict[str, any]]


class MissingTranslation(BaseModel):
    """Schema for missing translation"""

    key: str
    namespace: str
    source_value: Optional[str] = None


class AutoTranslateRequest(BaseModel):
    """Schema for auto-translate request"""

    source_language: str
    target_language: str
    namespace: Optional[str] = None
    provider: str = Field(default="google", pattern="^(google|deepl|azure)$")


class TranslationHistoryResponse(BaseModel):
    """Schema for translation history"""

    id: int
    translation_id: int
    old_value: Optional[str]
    new_value: str
    modified_by: str
    modified_at: datetime

    class Config:
        from_attributes = True
