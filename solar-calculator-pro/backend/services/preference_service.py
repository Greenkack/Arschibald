# backend/services/preference_service.py

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import uuid

from backend.models.preference_models import UserPreference, PreferenceTemplate, PreferenceSync
from backend.models.preference_schemas import (
    PreferenceCreate, PreferenceUpdate, PreferenceExport, PreferenceImport,
    PreferenceTemplateCreate, PreferenceSyncRequest, PreferenceResetRequest,
    PreferenceSearchRequest, PreferenceStatistics
)


class PreferenceService:
    """Service for managing user preferences"""

    def __init__(self, db: Session):
        self.db = db
        self.default_preferences = self._load_default_preferences()

    def _load_default_preferences(self) -> Dict[str, Dict[str, Any]]:
        """Load system default preferences"""
        return {
            "ui": {
                "theme": {"value": "light", "data_type": "string"},
                "language": {"value": "de", "data_type": "string"},
                "sidebar_collapsed": {"value": False, "data_type": "boolean"},
                "items_per_page": {"value": 25, "data_type": "number"},
                "date_format": {"value": "DD.MM.YYYY", "data_type": "string"},
                "time_format": {"value": "HH:mm", "data_type": "string"},
            },
            "calculation": {
                "auto_save": {"value": True, "data_type": "boolean"},
                "default_location": {"value": "Berlin", "data_type": "string"},
                "precision": {"value": 2, "data_type": "number"},
                "show_advanced_options": {"value": False, "data_type": "boolean"},
            },
            "pdf": {
                "default_template": {"value": "standard", "data_type": "string"},
                "auto_download": {"value": True, "data_type": "boolean"},
                "include_charts": {"value": True, "data_type": "boolean"},
                "compression_level": {"value": "medium", "data_type": "string"},
            },
            "notifications": {
                "enabled": {"value": True, "data_type": "boolean"},
                "sound": {"value": True, "data_type": "boolean"},
                "desktop": {"value": True, "data_type": "boolean"},
                "email": {"value": False, "data_type": "boolean"},
            },
        }

    def get_preference(self, user_id: int, category: str, key: str) -> Optional[UserPreference]:
        """Get a specific preference"""
        return self.db.query(UserPreference).filter(
            and_(
                UserPreference.user_id == user_id,
                UserPreference.category == category,
                UserPreference.key == key
            )
        ).first()

    def get_preferences_by_category(self, user_id: int, category: str) -> List[UserPreference]:
        """Get all preferences for a category"""
        return self.db.query(UserPreference).filter(
            and_(
                UserPreference.user_id == user_id,
                UserPreference.category == category
            )
        ).all()

    def get_all_preferences(self, user_id: int) -> Dict[str, Dict[str, Any]]:
        """Get all preferences for a user, organized by category"""
        preferences = self.db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).all()

        result = {}
        for pref in preferences:
            if pref.category not in result:
                result[pref.category] = {}
            
            # Parse value based on data type
            value = self._parse_value(pref.value, pref.data_type)
            result[pref.category][pref.key] = {
                "value": value,
                "data_type": pref.data_type,
                "is_default": pref.is_default,
                "updated_at": pref.updated_at
            }

        # Fill in defaults for missing preferences
        for category, prefs in self.default_preferences.items():
            if category not in result:
                result[category] = {}
            for key, default_value in prefs.items():
                if key not in result[category]:
                    result[category][key] = {
                        **default_value,
                        "is_default": True,
                        "updated_at": None
                    }

        return result

    def create_preference(self, user_id: int, preference: PreferenceCreate) -> UserPreference:
        """Create a new preference"""
        # Check if preference already exists
        existing = self.get_preference(user_id, preference.category, preference.key)
        if existing:
            raise ValueError(f"Preference {preference.category}.{preference.key} already exists")

        # Serialize value
        value_str = self._serialize_value(preference.value, preference.data_type)

        db_preference = UserPreference(
            user_id=user_id,
            category=preference.category,
            key=preference.key,
            value=value_str,
            data_type=preference.data_type,
            is_default=False
        )

        self.db.add(db_preference)
        self.db.commit()
        self.db.refresh(db_preference)

        return db_preference

    def update_preference(self, user_id: int, category: str, key: str, 
                         update: PreferenceUpdate) -> UserPreference:
        """Update an existing preference"""
        preference = self.get_preference(user_id, category, key)

        if not preference:
            # Create if doesn't exist
            default = self.default_preferences.get(category, {}).get(key)
            if not default:
                raise ValueError(f"Unknown preference {category}.{key}")
            
            return self.create_preference(user_id, PreferenceCreate(
                category=category,
                key=key,
                value=update.value,
                data_type=default["data_type"]
            ))

        # Update existing
        preference.value = self._serialize_value(update.value, preference.data_type)
        preference.is_default = False
        preference.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(preference)

        return preference

    def bulk_update_preferences(self, user_id: int, 
                               preferences: List[Dict[str, Any]]) -> List[UserPreference]:
        """Bulk update multiple preferences"""
        updated = []

        for pref_data in preferences:
            category = pref_data.get("category")
            key = pref_data.get("key")
            value = pref_data.get("value")

            if not all([category, key, value is not None]):
                continue

            try:
                updated_pref = self.update_preference(
                    user_id, category, key, PreferenceUpdate(value=value)
                )
                updated.append(updated_pref)
            except Exception as e:
                # Log error but continue with other preferences
                print(f"Error updating preference {category}.{key}: {str(e)}")

        return updated

    def delete_preference(self, user_id: int, category: str, key: str) -> bool:
        """Delete a preference (revert to default)"""
        preference = self.get_preference(user_id, category, key)
        if not preference:
            return False

        self.db.delete(preference)
        self.db.commit()
        return True

    def reset_preferences(self, user_id: int, reset_request: PreferenceResetRequest) -> int:
        """Reset preferences to defaults"""
        query = self.db.query(UserPreference).filter(UserPreference.user_id == user_id)

        if reset_request.category:
            query = query.filter(UserPreference.category == reset_request.category)

        if reset_request.keys:
            query = query.filter(UserPreference.key.in_(reset_request.keys))

        count = query.delete(synchronize_session=False)
        self.db.commit()

        return count

    def export_preferences(self, user_id: int) -> PreferenceExport:
        """Export all preferences"""
        preferences = self.get_all_preferences(user_id)

        return PreferenceExport(
            user_id=user_id,
            preferences=preferences
        )

    def import_preferences(self, user_id: int, import_data: PreferenceImport) -> int:
        """Import preferences"""
        count = 0

        for category, prefs in import_data.preferences.items():
            for key, pref_data in prefs.items():
                try:
                    value = pref_data.get("value")
                    data_type = pref_data.get("data_type", "string")

                    existing = self.get_preference(user_id, category, key)

                    if existing and not import_data.overwrite_existing:
                        continue

                    if existing:
                        self.update_preference(
                            user_id, category, key, PreferenceUpdate(value=value)
                        )
                    else:
                        self.create_preference(user_id, PreferenceCreate(
                            category=category,
                            key=key,
                            value=value,
                            data_type=data_type
                        ))

                    count += 1
                except Exception as e:
                    print(f"Error importing preference {category}.{key}: {str(e)}")

        return count

    def sync_preferences(self, user_id: int, sync_request: PreferenceSyncRequest) -> PreferenceSync:
        """Sync preferences across devices"""
        # Create sync record
        sync_record = PreferenceSync(
            user_id=user_id,
            device_id=sync_request.device_id,
            device_name=sync_request.device_name,
            sync_data=json.dumps(sync_request.preferences),
            sync_status='success'
        )

        self.db.add(sync_record)

        # Update preferences from sync
        for category, prefs in sync_request.preferences.items():
            for key, pref_data in prefs.items():
                try:
                    value = pref_data.get("value")
                    self.update_preference(
                        user_id, category, key, PreferenceUpdate(value=value)
                    )
                except Exception as e:
                    sync_record.sync_status = 'partial'
                    print(f"Error syncing preference {category}.{key}: {str(e)}")

        self.db.commit()
        self.db.refresh(sync_record)

        return sync_record

    def get_statistics(self, user_id: int) -> PreferenceStatistics:
        """Get preference statistics"""
        preferences = self.db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).all()

        categories = {}
        last_updated = None

        for pref in preferences:
            categories[pref.category] = categories.get(pref.category, 0) + 1
            if not last_updated or pref.updated_at > last_updated:
                last_updated = pref.updated_at

        device_count = self.db.query(PreferenceSync).filter(
            PreferenceSync.user_id == user_id
        ).distinct(PreferenceSync.device_id).count()

        return PreferenceStatistics(
            total_preferences=len(preferences),
            categories=categories,
            last_updated=last_updated,
            sync_status='synced' if device_count > 0 else 'not_synced',
            device_count=device_count
        )

    def search_preferences(self, user_id: int, 
                          search_request: PreferenceSearchRequest) -> List[UserPreference]:
        """Search preferences"""
        query = self.db.query(UserPreference).filter(UserPreference.user_id == user_id)

        if search_request.category:
            query = query.filter(UserPreference.category == search_request.category)

        if search_request.key_pattern:
            query = query.filter(UserPreference.key.like(f"%{search_request.key_pattern}%"))

        return query.all()

    # Template management
    def create_template(self, template: PreferenceTemplateCreate) -> PreferenceTemplate:
        """Create a preference template"""
        db_template = PreferenceTemplate(
            name=template.name,
            description=template.description,
            category=template.category,
            preferences=json.dumps(template.preferences),
            is_system=False
        )

        self.db.add(db_template)
        self.db.commit()
        self.db.refresh(db_template)

        return db_template

    def get_templates(self, category: Optional[str] = None) -> List[PreferenceTemplate]:
        """Get preference templates"""
        query = self.db.query(PreferenceTemplate)

        if category:
            query = query.filter(PreferenceTemplate.category == category)

        return query.all()

    def apply_template(self, user_id: int, template_id: int) -> int:
        """Apply a template to user preferences"""
        template = self.db.query(PreferenceTemplate).filter(
            PreferenceTemplate.id == template_id
        ).first()

        if not template:
            raise ValueError(f"Template {template_id} not found")

        preferences = json.loads(template.preferences)
        count = 0

        for key, pref_data in preferences.items():
            try:
                value = pref_data.get("value")
                data_type = pref_data.get("data_type", "string")

                self.update_preference(
                    user_id, template.category, key, PreferenceUpdate(value=value)
                )
                count += 1
            except Exception as e:
                print(f"Error applying template preference {key}: {str(e)}")

        return count

    # Helper methods
    def _serialize_value(self, value: Any, data_type: str) -> str:
        """Serialize value to string"""
        if data_type in ['object', 'array']:
            return json.dumps(value)
        return str(value)

    def _parse_value(self, value_str: str, data_type: str) -> Any:
        """Parse value from string"""
        if data_type == 'boolean':
            return value_str.lower() in ['true', '1', 'yes']
        elif data_type == 'number':
            try:
                return float(value_str) if '.' in value_str else int(value_str)
            except ValueError:
                return 0
        elif data_type in ['object', 'array']:
            try:
                return json.loads(value_str)
            except json.JSONDecodeError:
                return {} if data_type == 'object' else []
        return value_str
