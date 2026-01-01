"""
shadcn/ui Component Library for Streamlit

This package provides shadcn/ui-styled components for Streamlit applications.
"""

from .shadcn_base import ShadcnComponent
from .card import Card
from .alert import Alert, AlertDialog
from .badge import Badge, BadgeGroup
from .form_components import (
    Input,
    DatePicker,
    Calendar,
    InputOTP,
    input_field,
    date_picker,
    calendar,
    input_otp
)
from .table import Table, table, override_dataframe_styling
from .metric_card import (
    MetricCard,
    MetricCardGroup,
    metric_card,
    metric_card_group
)
from .accordion import Accordion, accordion
from .breadcrumb import Breadcrumb, breadcrumb
from .dropdown import DropdownMenu, dropdown_menu
from .popover import Popover, popover
from .progress import Progress, progress
from .skeleton import Skeleton, SkeletonCard, skeleton, skeleton_card
from .pagination import Pagination, pagination

__all__ = [
    'ShadcnComponent',
    'Card',
    'Alert',
    'AlertDialog',
    'Badge',
    'BadgeGroup',
    'Input',
    'DatePicker',
    'Calendar',
    'InputOTP',
    'input_field',
    'date_picker',
    'calendar',
    'input_otp',
    'Table',
    'table',
    'override_dataframe_styling',
    'MetricCard',
    'MetricCardGroup',
    'metric_card',
    'metric_card_group',
    'Accordion',
    'accordion',
    'Breadcrumb',
    'breadcrumb',
    'DropdownMenu',
    'dropdown_menu',
    'Popover',
    'popover',
    'Progress',
    'progress',
    'Skeleton',
    'SkeletonCard',
    'skeleton',
    'skeleton_card',
    'Pagination',
    'pagination',
]
