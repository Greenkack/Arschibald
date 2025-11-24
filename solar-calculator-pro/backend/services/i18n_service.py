"""
i18n Service
Handles translation management and language operations
"""

from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from ..models.i18n_models import Translation, UserLanguagePreference
from ..models.i18n_schemas import TranslationCreate, TranslationUpdate, TranslationResponse


class I18nService:
    """Service for managing translations and language preferences"""

    def __init__(self, db: Session):
        self.db = db

    def get_translations(
        self,
        namespace: Optional[str] = None,
        language: Optional[str] = None,
    ) -> List[TranslationResponse]:
        """Get all translations with optional filtering"""
        query = self.db.query(Translation)

        if namespace and namespace != "all":
            query = query.filter(Translation.namespace == namespace)

        translations = query.all()

        # Group by key and namespace
        grouped = {}
        for trans in translations:
            key = f"{trans.namespace}.{trans.key}"
            if key not in grouped:
                grouped[key] = {
                    "key": trans.key,
                    "namespace": trans.namespace,
                    "translations": {},
                    "lastModified": trans.updated_at.isoformat(),
                    "modifiedBy": trans.modified_by or "system",
                }
            grouped[key]["translations"][trans.language] = trans.value

        return list(grouped.values())

    def get_translation_resource(
        self,
        language: str,
        namespace: str,
    ) -> Dict[str, Any]:
        """Get translation resource for i18next backend"""
        translations = (
            self.db.query(Translation)
            .filter(
                Translation.language == language,
                Translation.namespace == namespace,
            )
            .all()
        )

        # Build nested dictionary
        result = {}
        for trans in translations:
            keys = trans.key.split(".")
            current = result
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            current[keys[-1]] = trans.value

        return result

    def create_translation(self, translation: TranslationCreate) -> TranslationResponse:
        """Create a new translation"""
        # Create translations for all languages
        created_translations = []
        for language, value in translation.translations.items():
            db_translation = Translation(
                key=translation.key,
                namespace=translation.namespace,
                language=language,
                value=value,
                modified_by=translation.modified_by,
            )
            self.db.add(db_translation)
            created_translations.append(db_translation)

        self.db.commit()

        return TranslationResponse(
            key=translation.key,
            namespace=translation.namespace,
            translations=translation.translations,
            lastModified=datetime.now().isoformat(),
            modifiedBy=translation.modified_by,
        )

    def update_translation(self, translation: TranslationUpdate) -> TranslationResponse:
        """Update an existing translation"""
        for language, value in translation.translations.items():
            db_translation = (
                self.db.query(Translation)
                .filter(
                    Translation.key == translation.key,
                    Translation.namespace == translation.namespace,
                    Translation.language == language,
                )
                .first()
            )

            if db_translation:
                db_translation.value = value
                db_translation.modified_by = translation.modified_by
                db_translation.updated_at = datetime.now()
            else:
                # Create if doesn't exist
                db_translation = Translation(
                    key=translation.key,
                    namespace=translation.namespace,
                    language=language,
                    value=value,
                    modified_by=translation.modified_by,
                )
                self.db.add(db_translation)

        self.db.commit()

        return TranslationResponse(
            key=translation.key,
            namespace=translation.namespace,
            translations=translation.translations,
            lastModified=datetime.now().isoformat(),
            modifiedBy=translation.modified_by,
        )

    def delete_translation(self, key: str, namespace: str):
        """Delete a translation"""
        self.db.query(Translation).filter(
            Translation.key == key,
            Translation.namespace == namespace,
        ).delete()
        self.db.commit()

    def export_translations(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """Export all translations grouped by language and namespace"""
        translations = self.db.query(Translation).all()

        result = {}
        for trans in translations:
            if trans.language not in result:
                result[trans.language] = {}
            if trans.namespace not in result[trans.language]:
                result[trans.language][trans.namespace] = {}

            # Build nested structure
            keys = trans.key.split(".")
            current = result[trans.language][trans.namespace]
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            current[keys[-1]] = trans.value

        return result

    def import_translations(
        self,
        language: str,
        namespace: str,
        translations: Dict[str, Any],
        prefix: str = "",
    ):
        """Import translations from nested dictionary"""
        for key, value in translations.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                # Recursive for nested objects
                self.import_translations(language, namespace, value, full_key)
            else:
                # Create or update translation
                db_translation = (
                    self.db.query(Translation)
                    .filter(
                        Translation.key == full_key,
                        Translation.namespace == namespace,
                        Translation.language == language,
                    )
                    .first()
                )

                if db_translation:
                    db_translation.value = str(value)
                    db_translation.updated_at = datetime.now()
                else:
                    db_translation = Translation(
                        key=full_key,
                        namespace=namespace,
                        language=language,
                        value=str(value),
                        modified_by="import",
                    )
                    self.db.add(db_translation)

        self.db.commit()

    def update_user_language(self, user_id: int, language: str):
        """Update user's language preference"""
        preference = (
            self.db.query(UserLanguagePreference)
            .filter(UserLanguagePreference.user_id == user_id)
            .first()
        )

        if preference:
            preference.language = language
            preference.updated_at = datetime.now()
        else:
            preference = UserLanguagePreference(
                user_id=user_id,
                language=language,
            )
            self.db.add(preference)

        self.db.commit()

    def get_user_language(self, user_id: int) -> str:
        """Get user's language preference"""
        preference = (
            self.db.query(UserLanguagePreference)
            .filter(UserLanguagePreference.user_id == user_id)
            .first()
        )

        return preference.language if preference else "de"

    def get_missing_translations(self, language: str) -> List[Dict[str, Any]]:
        """Get list of missing translations for a language"""
        # Get all unique keys from default language (de)
        default_keys = (
            self.db.query(Translation.key, Translation.namespace)
            .filter(Translation.language == "de")
            .distinct()
            .all()
        )

        # Get existing keys for target language
        existing_keys = set(
            self.db.query(Translation.key, Translation.namespace)
            .filter(Translation.language == language)
            .all()
        )

        # Find missing keys
        missing = []
        for key, namespace in default_keys:
            if (key, namespace) not in existing_keys:
                missing.append({
                    "key": key,
                    "namespace": namespace,
                })

        return missing

    def auto_translate(
        self,
        source_language: str,
        target_language: str,
        namespace: Optional[str] = None,
    ) -> int:
        """
        Auto-translate missing translations
        Note: This is a placeholder. In production, integrate with a translation API
        like Google Translate, DeepL, or Azure Translator
        """
        missing = self.get_missing_translations(target_language)

        if namespace:
            missing = [m for m in missing if m["namespace"] == namespace]

        count = 0
        for item in missing:
            # Get source translation
            source_trans = (
                self.db.query(Translation)
                .filter(
                    Translation.key == item["key"],
                    Translation.namespace == item["namespace"],
                    Translation.language == source_language,
                )
                .first()
            )

            if source_trans:
                # TODO: Integrate with translation API
                # For now, just copy the source with a marker
                translated_value = f"[AUTO] {source_trans.value}"

                # Create translation
                new_trans = Translation(
                    key=item["key"],
                    namespace=item["namespace"],
                    language=target_language,
                    value=translated_value,
                    modified_by="auto-translate",
                )
                self.db.add(new_trans)
                count += 1

        self.db.commit()
        return count

    def get_statistics(self) -> Dict[str, Any]:
        """Get translation statistics"""
        from ...i18n.i18n_config import SUPPORTED_LANGUAGES

        # Get total keys from default language
        total_keys = (
            self.db.query(Translation)
            .filter(Translation.language == "de")
            .count()
        )

        stats = {
            "total_keys": total_keys,
            "languages": {},
        }

        for lang_code in SUPPORTED_LANGUAGES.keys():
            count = (
                self.db.query(Translation)
                .filter(Translation.language == lang_code)
                .count()
            )

            completion = (count / total_keys * 100) if total_keys > 0 else 0

            stats["languages"][lang_code] = {
                "translated": count,
                "missing": total_keys - count,
                "completion": round(completion, 2),
            }

        return stats
