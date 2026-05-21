"""
Component-Level Feature Toggle Service

Provides granular control over individual UI components including:
- Chart visibility toggles
- Form field toggles
- Calculation option toggles
- Export format toggles
- UI theme toggles
- Language toggles
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.component_toggle_models import (
    ComponentToggle,
    ComponentToggleCategory,
    ComponentToggleType
)
from backend.models.component_toggle_schemas import (
    ComponentToggleCreate,
    ComponentToggleUpdate,
    ComponentToggleResponse,
    ComponentToggleListResponse
)
from backend.core.base_service import BaseService


class ComponentToggleService(BaseService):
    """Service for managing component-level feature toggles"""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.db = db
    
    # Chart Visibility Toggles
    
    def get_chart_toggles(self, user_id: Optional[int] = None) -> List[ComponentToggleResponse]:
        """Get all chart visibility toggles"""
        query = self.db.query(ComponentToggle).filter(
            ComponentToggle.category == ComponentToggleCategory.CHART
        )
        
        if user_id:
            query = query.filter(ComponentToggle.user_id == user_id)
        
        toggles = query.all()
        return [ComponentToggleResponse.from_orm(t) for t in toggles]
    
    def toggle_chart(
        self,
        chart_type: str,
        enabled: bool,
        user_id: Optional[int] = None
    ) -> ComponentToggleResponse:
        """Toggle visibility of a specific chart type"""
        toggle = self.db.query(ComponentToggle).filter(
            ComponentToggle.category == ComponentToggleCategory.CHART,
            ComponentToggle.component_key == chart_type,
            ComponentToggle.user_id == user_id
        ).first()
        
        if toggle:
            toggle.enabled = enabled
            toggle.updated_at = datetime.utcnow()
        else:
            toggle = ComponentToggle(
                category=ComponentToggleCategory.CHART,
                component_key=chart_type,
                component_name=f"{chart_type.replace('_', ' ').title()} Chart",
                enabled=enabled,
                user_id=user_id,
                toggle_type=ComponentToggleType.VISIBILITY
            )
            self.db.add(toggle)
        
        self.db.commit()
        self.db.refresh(toggle)
        return ComponentToggleResponse.from_orm(toggle)
    
    def get_visible_charts(self, user_id: Optional[int] = None) -> List[str]:
        """Get list of visible chart types"""
        toggles = self.db.query(ComponentToggle).filter(
            ComponentToggle.category == ComponentToggleCategory.CHART,
            ComponentToggle.enabled == True,
            ComponentToggle.user_id == user_id
        ).all()
        
        return [t.component_key for t in toggles]
    
    # Form Field Toggles
    
    def get_form_field_toggles(
        self,
        form_name: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> List[ComponentToggleResponse]:
        """Get all form field toggles"""
        query = self.db.query(ComponentToggle).filter(
            ComponentToggle.category == ComponentToggleCategory.FORM_FIELD
        )
        
        if form_name:
            query = query.filter(ComponentToggle.metadata['form_name'].astext == form_name)
        
        if user_id:
            query = query.filter(ComponentToggle.user_id == user_id)
        
        toggles = query.all()
        return [ComponentToggleResponse.from_orm(t) for t in toggles]
    
    def toggle_form_field(
        self,
        form_name: str,
        field_key: str,
        enabled: bool,
        user_id: Optional[int] = None
    ) -> ComponentToggleResponse:
        """Toggle visibility/editability of a form field"""
        component_key = f"{form_name}.{field_key}"
        
        toggle = self.db.query(ComponentToggle).filter(
            ComponentToggle.category == ComponentToggleCategory.FORM_FIELD,
            ComponentToggle.component_key == component_key,
            ComponentToggle.user_id == user_id
        ).first()
        
        if toggle:
            toggle.enabled = enabled
            toggle.updated_at = datetime.utcnow()
        else:
            toggle = ComponentToggle(
                category=ComponentToggleCategory.FORM_FIELD,
                component_key=component_key,
                component_name=f"{field_key.replace('_', ' ').title()}",
                enabled=enabled,
                user_id=user_id,
                toggle_type=ComponentToggleType.VISIBILITY,
                metadata={"form_name": form_name, "field_key": field_key}
            )
            self.db.add(toggle)
        
        self.db.commit()
        self.db.refresh(toggle)
        return ComponentToggleResponse.from_orm(toggle)
    
    def get_enabled_form_fields(
        self,
        form_name: str,
        user_id: Optional[int] = None
    ) -> List[str]:
        """Get list of enabled form fields for a specific form"""
        toggles = self.db.query(ComponentToggle).filter(
            ComponentToggle.category == ComponentToggleCategory.FORM_FIELD,
            ComponentToggle.enabled == True,
            ComponentToggle.metadata['form_name'].astext == form_name,
            ComponentToggle.user_id == user_id
        ).all()
        
        return [t.metadata.get('field_key') for t in toggles]
    
    # Calculation Option Toggles
    
    def get_calculation_option_toggles(
        self,
        calculator_type: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> List[ComponentToggleResponse]:
        """Get all calculation option toggles"""
        query = self.db.query(ComponentToggle).filter(
            ComponentToggle.category == ComponentToggleCategory.CALCULATION_OPTION
        )
        
        if calculator_type:
            query = query.filter(
                ComponentToggle.metadata['calculator_type'].astext == calculator_type
            )
        
        if user_id:
            query = query.filter(ComponentToggle.user_id == user_id)
        
        toggles = query.all()
        return [ComponentToggleResponse.from_orm(t) for t in toggles]
    
    def toggle_calculation_option(
        self,
        calculator_type: str,
        option_key: str,
        enabled: bool,
        user_id: Optional[int] = None
    ) -> ComponentToggleResponse:
        """Toggle a calculation option"""
        component_key = f"{calculator_type}.{option_key}"
        
        toggle = self.db.query(ComponentToggle).filter(
            ComponentToggle.category == ComponentToggleCategory.CALCULATION_OPTION,
            ComponentToggle.component_key == component_key,
            ComponentToggle.user_id == user_id
        ).first()
        
        if toggle:
            toggle.enabled = enabled
            toggle.updated_at = datetime.utcnow()
        else:
            toggle = ComponentToggle(
                category=ComponentToggleCategory.CALCULATION_OPTION,
                component_key=component_key,
                component_name=f"{option_key.replace('_', ' ').title()}",
                enabled=enabled,
                user_id=user_id,
                toggle_type=ComponentToggleType.FEATURE,
                metadata={"calculator_type": calculator_type, "option_key": option_key}
            )
            self.db.add(toggle)
        
        self.db.commit()
        self.db.refresh(toggle)
        return ComponentToggleResponse.from_orm(toggle)
    
    def get_enabled_calculation_options(
        self,
        calculator_type: str,
        user_id: Optional[int] = None
    ) -> List[str]:
        """Get list of enabled calculation options"""
        toggles = self.db.query(ComponentToggle).filter(
            ComponentToggle.category == ComponentToggleCategory.CALCULATION_OPTION,
            ComponentToggle.enabled == True,
            ComponentToggle.metadata['calculator_type'].astext == calculator_type,
            ComponentToggle.user_id == user_id
        ).all()
        
        return [t.metadata.get('option_key') for t in toggles]
    
    # Export Format Toggles
    
    def get_export_format_toggles(
        self,
        user_id: Optional[int] = None
    ) -> List[ComponentToggleResponse]:
        """Get all export format toggles"""
        query = self.db.query(ComponentToggle).filter(
            ComponentToggle.category == ComponentToggleCategory.EXPORT_FORMAT
        )
        
        if user_id:
            query = query.filter(ComponentToggle.user_id == user_id)
        
        toggles = query.all()
        return [ComponentToggleResponse.from_orm(t) for t in toggles]
    
    def toggle_export_format(
        self,
        format_key: str,
        enabled: bool,
        user_id: Optional[int] = None
    ) -> ComponentToggleResponse:
        """Toggle availability of an export format"""
        toggle = self.db.query(ComponentToggle).filter(
            ComponentToggle.category == ComponentToggleCategory.EXPORT_FORMAT,
            ComponentToggle.component_key == format_key,
            ComponentToggle.user_id == user_id
        ).first()
        
        if toggle:
            toggle.enabled = enabled
            toggle.updated_at = datetime.utcnow()
        else:
            toggle = ComponentToggle(
                category=ComponentToggleCategory.EXPORT_FORMAT,
                component_key=format_key,
                component_name=f"{format_key.upper()} Export",
                enabled=enabled,
                user_id=user_id,
                toggle_type=ComponentToggleType.FEATURE
            )
            self.db.add(toggle)
        
        self.db.commit()
        self.db.refresh(toggle)
        return ComponentToggleResponse.from_orm(toggle)
    
    def get_available_export_formats(
        self,
        user_id: Optional[int] = None
    ) -> List[str]:
        """Get list of available export formats"""
        toggles = self.db.query(ComponentToggle).filter(
            ComponentToggle.category == ComponentToggleCategory.EXPORT_FORMAT,
            ComponentToggle.enabled == True,
            ComponentToggle.user_id == user_id
        ).all()
        
        return [t.component_key for t in toggles]
    
    # UI Theme Toggles
    
    def get_theme_toggles(
        self,
        user_id: Optional[int] = None
    ) -> List[ComponentToggleResponse]:
        """Get all UI theme toggles"""
        query = self.db.query(ComponentToggle).filter(
            ComponentToggle.category == ComponentToggleCategory.UI_THEME
        )
        
        if user_id:
            query = query.filter(ComponentToggle.user_id == user_id)
        
        toggles = query.all()
        return [ComponentToggleResponse.from_orm(t) for t in toggles]
    
    def toggle_theme(
        self,
        theme_key: str,
        enabled: bool,
        user_id: Optional[int] = None
    ) -> ComponentToggleResponse:
        """Toggle availability of a UI theme"""
        toggle = self.db.query(ComponentToggle).filter(
            ComponentToggle.category == ComponentToggleCategory.UI_THEME,
            ComponentToggle.component_key == theme_key,
            ComponentToggle.user_id == user_id
        ).first()
        
        if toggle:
            toggle.enabled = enabled
            toggle.updated_at = datetime.utcnow()
        else:
            toggle = ComponentToggle(
                category=ComponentToggleCategory.UI_THEME,
                component_key=theme_key,
                component_name=f"{theme_key.replace('_', ' ').title()} Theme",
                enabled=enabled,
                user_id=user_id,
                toggle_type=ComponentToggleType.FEATURE
            )
            self.db.add(toggle)
        
        self.db.commit()
        self.db.refresh(toggle)
        return ComponentToggleResponse.from_orm(toggle)
    
    def get_available_themes(
        self,
        user_id: Optional[int] = None
    ) -> List[str]:
        """Get list of available UI themes"""
        toggles = self.db.query(ComponentToggle).filter(
            ComponentToggle.category == ComponentToggleCategory.UI_THEME,
            ComponentToggle.enabled == True,
            ComponentToggle.user_id == user_id
        ).all()
        
        return [t.component_key for t in toggles]
    
    # Language Toggles
    
    def get_language_toggles(
        self,
        user_id: Optional[int] = None
    ) -> List[ComponentToggleResponse]:
        """Get all language toggles"""
        query = self.db.query(ComponentToggle).filter(
            ComponentToggle.category == ComponentToggleCategory.LANGUAGE
        )
        
        if user_id:
            query = query.filter(ComponentToggle.user_id == user_id)
        
        toggles = query.all()
        return [ComponentToggleResponse.from_orm(t) for t in toggles]
    
    def toggle_language(
        self,
        language_code: str,
        enabled: bool,
        user_id: Optional[int] = None
    ) -> ComponentToggleResponse:
        """Toggle availability of a language"""
        toggle = self.db.query(ComponentToggle).filter(
            ComponentToggle.category == ComponentToggleCategory.LANGUAGE,
            ComponentToggle.component_key == language_code,
            ComponentToggle.user_id == user_id
        ).first()
        
        if toggle:
            toggle.enabled = enabled
            toggle.updated_at = datetime.utcnow()
        else:
            toggle = ComponentToggle(
                category=ComponentToggleCategory.LANGUAGE,
                component_key=language_code,
                component_name=self._get_language_name(language_code),
                enabled=enabled,
                user_id=user_id,
                toggle_type=ComponentToggleType.FEATURE
            )
            self.db.add(toggle)
        
        self.db.commit()
        self.db.refresh(toggle)
        return ComponentToggleResponse.from_orm(toggle)
    
    def get_available_languages(
        self,
        user_id: Optional[int] = None
    ) -> List[str]:
        """Get list of available languages"""
        toggles = self.db.query(ComponentToggle).filter(
            ComponentToggle.category == ComponentToggleCategory.LANGUAGE,
            ComponentToggle.enabled == True,
            ComponentToggle.user_id == user_id
        ).all()
        
        return [t.component_key for t in toggles]
    
    # Bulk Operations
    
    def bulk_toggle(
        self,
        category: ComponentToggleCategory,
        enabled: bool,
        user_id: Optional[int] = None
    ) -> int:
        """Bulk enable/disable all toggles in a category"""
        query = self.db.query(ComponentToggle).filter(
            ComponentToggle.category == category
        )
        
        if user_id:
            query = query.filter(ComponentToggle.user_id == user_id)
        
        count = query.update(
            {"enabled": enabled, "updated_at": datetime.utcnow()},
            synchronize_session=False
        )
        
        self.db.commit()
        return count
    
    def get_all_toggles(
        self,
        user_id: Optional[int] = None,
        category: Optional[ComponentToggleCategory] = None
    ) -> ComponentToggleListResponse:
        """Get all component toggles with optional filtering"""
        query = self.db.query(ComponentToggle)
        
        if user_id:
            query = query.filter(ComponentToggle.user_id == user_id)
        
        if category:
            query = query.filter(ComponentToggle.category == category)
        
        toggles = query.all()
        
        return ComponentToggleListResponse(
            toggles=[ComponentToggleResponse.from_orm(t) for t in toggles],
            total=len(toggles)
        )
    
    def reset_to_defaults(
        self,
        user_id: Optional[int] = None
    ) -> int:
        """Reset all toggles to default values"""
        query = self.db.query(ComponentToggle)
        
        if user_id:
            query = query.filter(ComponentToggle.user_id == user_id)
        
        count = query.delete(synchronize_session=False)
        self.db.commit()
        
        # Re-create default toggles
        self._create_default_toggles(user_id)
        
        return count
    
    # Helper Methods
    
    def _get_language_name(self, language_code: str) -> str:
        """Get display name for language code"""
        language_names = {
            "de": "Deutsch",
            "en": "English",
            "fr": "Français",
            "es": "Español",
            "it": "Italiano",
            "nl": "Nederlands",
            "pl": "Polski",
            "cs": "Čeština"
        }
        return language_names.get(language_code, language_code.upper())
    
    def _create_default_toggles(self, user_id: Optional[int] = None):
        """Create default component toggles"""
        defaults = [
            # Charts
            ("line_chart", ComponentToggleCategory.CHART, True),
            ("bar_chart", ComponentToggleCategory.CHART, True),
            ("pie_chart", ComponentToggleCategory.CHART, True),
            ("area_chart", ComponentToggleCategory.CHART, True),
            ("donut_chart", ComponentToggleCategory.CHART, True),
            
            # Export Formats
            ("pdf", ComponentToggleCategory.EXPORT_FORMAT, True),
            ("excel", ComponentToggleCategory.EXPORT_FORMAT, True),
            ("csv", ComponentToggleCategory.EXPORT_FORMAT, True),
            ("json", ComponentToggleCategory.EXPORT_FORMAT, False),
            
            # Themes
            ("light", ComponentToggleCategory.UI_THEME, True),
            ("dark", ComponentToggleCategory.UI_THEME, True),
            ("high_contrast", ComponentToggleCategory.UI_THEME, True),
            
            # Languages
            ("de", ComponentToggleCategory.LANGUAGE, True),
            ("en", ComponentToggleCategory.LANGUAGE, True),
        ]
        
        for key, category, enabled in defaults:
            toggle = ComponentToggle(
                category=category,
                component_key=key,
                component_name=key.replace('_', ' ').title(),
                enabled=enabled,
                user_id=user_id,
                toggle_type=ComponentToggleType.FEATURE
            )
            self.db.add(toggle)
        
        self.db.commit()
