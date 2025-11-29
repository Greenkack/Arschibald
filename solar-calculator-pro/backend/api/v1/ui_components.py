"""
Interactive UI Components API

Provides REST API for interactive UI components:
- All dropdown menus
- Sliders for continuous values
- Date picker components
- Checkbox groups
- Info tooltips with explanations

Requirements: funktionen.txt - "interaktive Steuerelemente"
Task: 281. Interactive UI Components
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, date
from enum import Enum

router = APIRouter(prefix="/ui/components", tags=["UI Components"])


# ==================== Enums ====================

class ComponentType(str, Enum):
    DROPDOWN = "dropdown"
    SLIDER = "slider"
    DATE_PICKER = "date_picker"
    CHECKBOX_GROUP = "checkbox_group"
    RADIO_GROUP = "radio_group"
    NUMBER_INPUT = "number_input"
    TEXT_INPUT = "text_input"


class SliderType(str, Enum):
    CONTINUOUS = "continuous"
    DISCRETE = "discrete"
    RANGE = "range"


# ==================== Pydantic Models ====================

class DropdownOption(BaseModel):
    """Dropdown option"""
    value: str
    label: str
    disabled: bool = False
    group: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
