"""
Dropdown and Selection Dynamic Keys Service

This module provides comprehensive dynamic key management for dropdown
options, selections, cascading dropdowns, and selection history.

Requirements: 14.7
Task: 224
"""

from typing import Dict, Any, Optional, List, Set, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

try:
    from backend.core.dynamic_keys import (
        DynamicKeyMixin,
        KeyPrefix,
        DynamicKeyIndex,
        get_global_key_index
    )
except ImportError:
    from core.dynamic_keys import (
        DynamicKeyMixin,
        KeyPrefix,
        DynamicKeyIndex,
        get_global_key_index
    )


class DropdownType(str, Enum):
    """Enumeration of dropdown types"""
    SINGLE_SELECT = "single_select"
    MULTI_SELECT = "multi_select"
    CASCADING = "cascading"
    SEARCHABLE = "searchable"
    GROUPED = "grouped"
    DYNAMIC = "dynamic"
    AUTOCOMPLETE = "autocomplete"


@dataclass
class DropdownOption:
    """
    Represents a single dropdown option with dynamic key.
    """
    key: str
    value: Any
    label: str
    group: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_key: Optional[str] = None
    children_keys: List[str] = field(default_factory=list)
    enabled: bool = True
    visible: bool = True
    sort_order: int = 0
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert option to dictionary"""
        return {
            'key': self.key,
            'value': self.value,
            'label': self.label,
            'group': self.group,
            'metadata': self.metadata,
            'parent_key': self.parent_key,
            'children_keys': self.children_keys,
            'enabled': self.enabled,
            'visible': self.visible,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class SelectionHistoryEntry:
    """
    Represents a single selection history entry.
    """
    dropdown_key: str
    option_key: str
    option_value: Any
    option_label: str
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert history entry to dictionary"""
        return {
            'dropdown_key': self.dropdown_key,
            'option_key': self.option_key,
            'option_value': self.option_value,
            'option_label': self.option_label,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'session_id': self.session_id,
            'metadata': self.metadata
        }


class DropdownKeyManager:
    """
    Manager for generating and tracking dynamic keys for dropdown
    options and selections.

    This class provides methods to attach dynamic keys to all dropdown
    options, create key mappings, implement cascading dropdowns, and
    manage selection history.
    """

    def __init__(self):
        """Initialize the dropdown key manager"""
        self.key_index = get_global_key_index()
        self.dropdown_registry: Dict[str, 'Dropdown'] = {}
        self.option_registry: Dict[str, DropdownOption] = {}
        self.selection_history: List[SelectionHistoryEntry] = []
        self.cascading_relationships: Dict[str, List[str]] = {}

    def create_dropdown_key(
        self,
        dropdown_id: str,
        dropdown_type: DropdownType,
        form_id: Optional[str] = None,
        custom_suffix: Optional[str] = None
    ) -> str:
        """
        Create a dynamic key for a dropdown.

        Args:
            dropdown_id: ID of the dropdown
            dropdown_type: Type of the dropdown
            form_id: Optional form ID if dropdown is part of a form
            custom_suffix: Optional custom suffix

        Returns:
            Generated dynamic key

        Example:
            >>> manager = DropdownKeyManager()
            >>> key = manager.create_dropdown_key(
            ...     "module_type",
            ...     DropdownType.SINGLE_SELECT,
            ...     "solar_calc_form"
            ... )
            >>> print(key)
            'DRP_20231116_143052_a1b2c3d4_solar_calc_form_module_type'
        """
        # Create composite suffix
        suffix_parts = []
        if form_id:
            suffix_parts.append(form_id)
        suffix_parts.append(dropdown_id)
        if custom_suffix:
            suffix_parts.append(custom_suffix)
        suffix = "_".join(suffix_parts)

        # Generate key using mixin
        mixin = DynamicKeyMixin()
        key = mixin.generate_dynamic_key(
            prefix=KeyPrefix.DATA,
            include_timestamp=True,
            include_uuid=True,
            custom_suffix=suffix
        )

        # Store metadata
        metadata = {
            'dropdown_id': dropdown_id,
            'dropdown_type': dropdown_type.value,
            'form_id': form_id,
            'created_at': datetime.now().isoformat()
        }

        self.key_index.add(key, None, metadata)

        return key

    def create_option_key(
        self,
        dropdown_key: str,
        option_value: Any,
        option_label: str,
        parent_key: Optional[str] = None
    ) -> str:
        """
        Create a dynamic key for a dropdown option.

        Args:
            dropdown_key: Key of the parent dropdown
            option_value: Value of the option
            option_label: Display label of the option
            parent_key: Optional parent option key for cascading

        Returns:
            Generated dynamic key

        Example:
            >>> manager = DropdownKeyManager()
            >>> dropdown_key = "DRP_20231116_143052_a1b2c3d4_module_type"
            >>> option_key = manager.create_option_key(
            ...     dropdown_key,
            ...     "monocrystalline",
            ...     "Monocrystalline"
            ... )
        """
        # Create suffix from option value
        suffix = f"{dropdown_key}_opt_{str(option_value)}"

        # Generate key
        mixin = DynamicKeyMixin()
        key = mixin.generate_dynamic_key(
            prefix=KeyPrefix.DATA,
            include_timestamp=False,
            include_uuid=True,
            custom_suffix=suffix
        )

        # Store metadata
        metadata = {
            'dropdown_key': dropdown_key,
            'option_value': option_value,
            'option_label': option_label,
            'parent_key': parent_key,
            'created_at': datetime.now().isoformat()
        }

        self.key_index.add(key, None, metadata)

        return key

    def register_dropdown(
        self,
        dropdown_id: str,
        dropdown_type: DropdownType,
        label: str,
        options: List[Dict[str, Any]],
        form_id: Optional[str] = None,
        default_value: Any = None,
        multiple: bool = False,
        searchable: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'Dropdown':
        """
        Register a dropdown with dynamic key and options.

        Args:
            dropdown_id: ID of the dropdown
            dropdown_type: Type of dropdown
            label: Display label
            options: List of option dictionaries
            form_id: Optional form ID
            default_value: Default selected value(s)
            multiple: Whether multiple selection is allowed
            searchable: Whether dropdown is searchable
            metadata: Additional metadata

        Returns:
            Dropdown object with dynamic key

        Example:
            >>> manager = DropdownKeyManager()
            >>> dropdown = manager.register_dropdown(
            ...     "module_type",
            ...     DropdownType.SINGLE_SELECT,
            ...     "Module Type",
            ...     [
            ...         {"value": "mono", "label": "Monocrystalline"},
            ...         {"value": "poly", "label": "Polycrystalline"}
            ...     ]
            ... )
        """
        # Create dropdown key
        dropdown_key = self.create_dropdown_key(
            dropdown_id,
            dropdown_type,
            form_id
        )

        # Create dropdown object
        dropdown = Dropdown(
            key=dropdown_key,
            dropdown_id=dropdown_id,
            dropdown_type=dropdown_type,
            label=label,
            form_id=form_id,
            default_value=default_value,
            multiple=multiple,
            searchable=searchable,
            metadata=metadata or {}
        )

        # Register options
        for opt_data in options:
            option = self._create_option_from_dict(
                dropdown_key,
                opt_data
            )
            dropdown.add_option(option)
            self.option_registry[option.key] = option

        # Register dropdown
        self.dropdown_registry[dropdown_key] = dropdown

        return dropdown

    def _create_option_from_dict(
        self,
        dropdown_key: str,
        opt_data: Dict[str, Any],
        parent_key: Optional[str] = None
    ) -> DropdownOption:
        """
        Create a DropdownOption from dictionary data.

        Args:
            dropdown_key: Key of parent dropdown
            opt_data: Option data dictionary
            parent_key: Optional parent option key

        Returns:
            DropdownOption object
        """
        value = opt_data.get('value')
        label = opt_data.get('label', str(value))

        # Create option key
        option_key = self.create_option_key(
            dropdown_key,
            value,
            label,
            parent_key
        )

        # Create option
        option = DropdownOption(
            key=option_key,
            value=value,
            label=label,
            group=opt_data.get('group'),
            metadata=opt_data.get('metadata', {}),
            parent_key=parent_key,
            enabled=opt_data.get('enabled', True),
            visible=opt_data.get('visible', True),
            sort_order=opt_data.get('sort_order', 0)
        )

        # Handle children for cascading dropdowns
        if 'children' in opt_data:
            for child_data in opt_data['children']:
                child_option = self._create_option_from_dict(
                    dropdown_key,
                    child_data,
                    option_key
                )
                option.children_keys.append(child_option.key)
                self.option_registry[child_option.key] = child_option

        return option

    def get_dropdown_by_key(self, key: str) -> Optional['Dropdown']:
        """
        Retrieve a dropdown by its dynamic key.

        Args:
            key: Dynamic key to lookup

        Returns:
            Dropdown object or None if not found
        """
        return self.dropdown_registry.get(key)

    def get_option_by_key(self, key: str) -> Optional[DropdownOption]:
        """
        Retrieve an option by its dynamic key.

        Args:
            key: Dynamic key to lookup

        Returns:
            DropdownOption object or None if not found
        """
        return self.option_registry.get(key)

    def get_options_by_dropdown(
        self,
        dropdown_key: str,
        include_disabled: bool = False,
        include_hidden: bool = False
    ) -> List[DropdownOption]:
        """
        Get all options for a specific dropdown.

        Args:
            dropdown_key: Key of the dropdown
            include_disabled: Whether to include disabled options
            include_hidden: Whether to include hidden options

        Returns:
            List of DropdownOption objects
        """
        dropdown = self.get_dropdown_by_key(dropdown_key)
        if not dropdown:
            return []

        options = dropdown.get_options()

        # Filter based on flags - both conditions must be met
        filtered_options = []
        for opt in options:
            # Check enabled status
            if not include_disabled and not opt.enabled:
                continue
            # Check visible status
            if not include_hidden and not opt.visible:
                continue
            filtered_options.append(opt)

        return filtered_options

    def get_option_by_value(
        self,
        dropdown_key: str,
        value: Any
    ) -> Optional[DropdownOption]:
        """
        Get an option by its value within a dropdown.

        Args:
            dropdown_key: Key of the dropdown
            value: Value to search for

        Returns:
            DropdownOption or None if not found
        """
        dropdown = self.get_dropdown_by_key(dropdown_key)
        if not dropdown:
            return None

        return dropdown.get_option_by_value(value)

    def register_cascading_dropdown(
        self,
        parent_dropdown_id: str,
        child_dropdown_id: str,
        parent_form_id: Optional[str] = None,
        child_form_id: Optional[str] = None,
        filter_function: Optional[Callable] = None
    ) -> tuple[str, str]:
        """
        Register a cascading relationship between two dropdowns.

        Args:
            parent_dropdown_id: ID of parent dropdown
            child_dropdown_id: ID of child dropdown
            parent_form_id: Optional form ID for parent
            child_form_id: Optional form ID for child
            filter_function: Optional function to filter child options

        Returns:
            Tuple of (parent_key, child_key)

        Example:
            >>> manager = DropdownKeyManager()
            >>> parent_key, child_key = manager.register_cascading_dropdown(
            ...     "country",
            ...     "state"
            ... )
        """
        # Get or create parent dropdown key
        parent_key = self.create_dropdown_key(
            parent_dropdown_id,
            DropdownType.CASCADING,
            parent_form_id
        )

        # Get or create child dropdown key
        child_key = self.create_dropdown_key(
            child_dropdown_id,
            DropdownType.CASCADING,
            child_form_id
        )

        # Register relationship
        if parent_key not in self.cascading_relationships:
            self.cascading_relationships[parent_key] = []
        self.cascading_relationships[parent_key].append(child_key)

        # Store filter function if provided
        if filter_function:
            if parent_key not in self.dropdown_registry:
                # Create placeholder dropdown
                self.dropdown_registry[parent_key] = Dropdown(
                    key=parent_key,
                    dropdown_id=parent_dropdown_id,
                    dropdown_type=DropdownType.CASCADING,
                    label=parent_dropdown_id,
                    form_id=parent_form_id
                )
            self.dropdown_registry[parent_key].cascading_filter = (
                filter_function
            )

        return parent_key, child_key

    def get_cascading_children(
        self,
        parent_key: str
    ) -> List[str]:
        """
        Get all child dropdown keys for a parent dropdown.

        Args:
            parent_key: Key of parent dropdown

        Returns:
            List of child dropdown keys
        """
        return self.cascading_relationships.get(parent_key, []).copy()

    def filter_cascading_options(
        self,
        parent_key: str,
        parent_value: Any,
        child_key: str
    ) -> List[DropdownOption]:
        """
        Filter child dropdown options based on parent selection.

        Args:
            parent_key: Key of parent dropdown
            parent_value: Selected value in parent
            child_key: Key of child dropdown

        Returns:
            Filtered list of child options

        Example:
            >>> manager = DropdownKeyManager()
            >>> # After selecting "USA" in country dropdown
            >>> states = manager.filter_cascading_options(
            ...     country_key,
            ...     "USA",
            ...     state_key
            ... )
        """
        parent_dropdown = self.get_dropdown_by_key(parent_key)
        child_dropdown = self.get_dropdown_by_key(child_key)

        if not parent_dropdown or not child_dropdown:
            return []

        # Get parent option
        parent_option = parent_dropdown.get_option_by_value(parent_value)
        if not parent_option:
            return []

        # Get child options
        child_options = child_dropdown.get_options()

        # Apply cascading filter if available
        if hasattr(parent_dropdown, 'cascading_filter'):
            filter_func = parent_dropdown.cascading_filter
            if filter_func:
                return [
                    opt for opt in child_options
                    if filter_func(parent_option, opt)
                ]

        # Default: filter by parent_key relationship
        return [
            opt for opt in child_options
            if opt.parent_key == parent_option.key
        ]

    def record_selection(
        self,
        dropdown_key: str,
        option_key: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SelectionHistoryEntry:
        """
        Record a selection in the history.

        Args:
            dropdown_key: Key of the dropdown
            option_key: Key of selected option
            user_id: Optional user ID
            session_id: Optional session ID
            metadata: Optional metadata

        Returns:
            SelectionHistoryEntry object

        Example:
            >>> manager = DropdownKeyManager()
            >>> entry = manager.record_selection(
            ...     dropdown_key,
            ...     option_key,
            ...     user_id="user123"
            ... )
        """
        option = self.get_option_by_key(option_key)
        if not option:
            raise ValueError(f"Option not found: {option_key}")

        entry = SelectionHistoryEntry(
            dropdown_key=dropdown_key,
            option_key=option_key,
            option_value=option.value,
            option_label=option.label,
            user_id=user_id,
            session_id=session_id,
            metadata=metadata or {}
        )

        self.selection_history.append(entry)

        # Update dropdown's current selection
        dropdown = self.get_dropdown_by_key(dropdown_key)
        if dropdown:
            dropdown.set_selected_value(option.value)

        return entry

    def get_selection_history(
        self,
        dropdown_key: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[SelectionHistoryEntry]:
        """
        Get selection history with optional filters.

        Args:
            dropdown_key: Optional dropdown key filter
            user_id: Optional user ID filter
            session_id: Optional session ID filter
            limit: Optional limit on number of results

        Returns:
            List of SelectionHistoryEntry objects

        Example:
            >>> manager = DropdownKeyManager()
            >>> history = manager.get_selection_history(
            ...     dropdown_key=dropdown_key,
            ...     limit=10
            ... )
        """
        filtered = self.selection_history

        if dropdown_key:
            filtered = [
                e for e in filtered
                if e.dropdown_key == dropdown_key
            ]

        if user_id:
            filtered = [
                e for e in filtered
                if e.user_id == user_id
            ]

        if session_id:
            filtered = [
                e for e in filtered
                if e.session_id == session_id
            ]

        # Sort by timestamp (most recent first)
        filtered = sorted(
            filtered,
            key=lambda e: e.timestamp,
            reverse=True
        )

        if limit:
            filtered = filtered[:limit]

        return filtered

    def get_most_selected_options(
        self,
        dropdown_key: str,
        limit: int = 5
    ) -> List[tuple[DropdownOption, int]]:
        """
        Get the most frequently selected options for a dropdown.

        Args:
            dropdown_key: Key of the dropdown
            limit: Maximum number of options to return

        Returns:
            List of (option, count) tuples sorted by frequency

        Example:
            >>> manager = DropdownKeyManager()
            >>> popular = manager.get_most_selected_options(
            ...     dropdown_key,
            ...     limit=3
            ... )
            >>> for option, count in popular:
            ...     print(f"{option.label}: {count} selections")
        """
        # Count selections
        selection_counts: Dict[str, int] = {}

        for entry in self.selection_history:
            if entry.dropdown_key == dropdown_key:
                key = entry.option_key
                selection_counts[key] = selection_counts.get(key, 0) + 1

        # Get options and sort by count
        option_counts = []
        for option_key, count in selection_counts.items():
            option = self.get_option_by_key(option_key)
            if option:
                option_counts.append((option, count))

        option_counts.sort(key=lambda x: x[1], reverse=True)

        return option_counts[:limit]

    def clear_selection_history(
        self,
        dropdown_key: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> int:
        """
        Clear selection history with optional filters.

        Args:
            dropdown_key: Optional dropdown key filter
            user_id: Optional user ID filter

        Returns:
            Number of entries cleared
        """
        initial_count = len(self.selection_history)

        if dropdown_key and user_id:
            self.selection_history = [
                e for e in self.selection_history
                if not (e.dropdown_key == dropdown_key and
                        e.user_id == user_id)
            ]
        elif dropdown_key:
            self.selection_history = [
                e for e in self.selection_history
                if e.dropdown_key != dropdown_key
            ]
        elif user_id:
            self.selection_history = [
                e for e in self.selection_history
                if e.user_id != user_id
            ]
        else:
            self.selection_history.clear()

        return initial_count - len(self.selection_history)

    def export_dropdown_schema(
        self,
        dropdown_key: str
    ) -> Dict[str, Any]:
        """
        Export the complete schema of a dropdown including all options.

        Args:
            dropdown_key: Key of the dropdown

        Returns:
            Dictionary containing dropdown schema

        Example:
            >>> manager = DropdownKeyManager()
            >>> schema = manager.export_dropdown_schema(dropdown_key)
            >>> print(schema['total_options'])
        """
        dropdown = self.get_dropdown_by_key(dropdown_key)
        if not dropdown:
            return {}

        options = dropdown.get_options()

        return {
            'dropdown_key': dropdown_key,
            'dropdown_id': dropdown.dropdown_id,
            'dropdown_type': dropdown.dropdown_type.value,
            'label': dropdown.label,
            'form_id': dropdown.form_id,
            'multiple': dropdown.multiple,
            'searchable': dropdown.searchable,
            'total_options': len(options),
            'options': [opt.to_dict() for opt in options],
            'cascading_children': self.get_cascading_children(dropdown_key),
            'current_selection': dropdown.get_selected_value(),
            'metadata': dropdown.metadata
        }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about registered dropdowns and selections.

        Returns:
            Dictionary with statistics
        """
        total_dropdowns = len(self.dropdown_registry)
        total_options = len(self.option_registry)
        total_selections = len(self.selection_history)

        dropdowns_by_type = {}
        for dropdown in self.dropdown_registry.values():
            dtype = dropdown.dropdown_type.value
            dropdowns_by_type[dtype] = dropdowns_by_type.get(dtype, 0) + 1

        return {
            'total_dropdowns': total_dropdowns,
            'total_options': total_options,
            'total_selections': total_selections,
            'dropdowns_by_type': dropdowns_by_type,
            'cascading_relationships': len(self.cascading_relationships),
            'average_options_per_dropdown': (
                total_options / total_dropdowns if total_dropdowns > 0
                else 0
            )
        }


class Dropdown:
    """
    Represents a dropdown with dynamic key and options.
    """

    def __init__(
        self,
        key: str,
        dropdown_id: str,
        dropdown_type: DropdownType,
        label: str,
        form_id: Optional[str] = None,
        default_value: Any = None,
        multiple: bool = False,
        searchable: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize dropdown"""
        self.key = key
        self.dropdown_id = dropdown_id
        self.dropdown_type = dropdown_type
        self.label = label
        self.form_id = form_id
        self.default_value = default_value
        self.multiple = multiple
        self.searchable = searchable
        self.metadata = metadata or {}
        self.options: List[DropdownOption] = []
        self.selected_value: Any = default_value
        self.cascading_filter: Optional[Callable] = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def add_option(self, option: DropdownOption) -> None:
        """Add an option to the dropdown"""
        self.options.append(option)
        self.updated_at = datetime.now()

    def remove_option(self, option_key: str) -> bool:
        """Remove an option by key"""
        initial_len = len(self.options)
        self.options = [opt for opt in self.options if opt.key != option_key]
        self.updated_at = datetime.now()
        return len(self.options) < initial_len

    def get_options(self) -> List[DropdownOption]:
        """Get all options"""
        return sorted(self.options, key=lambda opt: opt.sort_order)

    def get_option_by_value(self, value: Any) -> Optional[DropdownOption]:
        """Get option by value"""
        for option in self.options:
            if option.value == value:
                return option
        return None

    def get_option_by_key(self, key: str) -> Optional[DropdownOption]:
        """Get option by key"""
        for option in self.options:
            if option.key == key:
                return option
        return None

    def set_selected_value(self, value: Any) -> None:
        """Set the selected value"""
        self.selected_value = value
        self.updated_at = datetime.now()

    def get_selected_value(self) -> Any:
        """Get the selected value"""
        return self.selected_value

    def get_selected_option(self) -> Optional[DropdownOption]:
        """Get the selected option object"""
        if self.selected_value is None:
            return None
        return self.get_option_by_value(self.selected_value)

    def to_dict(self) -> Dict[str, Any]:
        """Convert dropdown to dictionary"""
        return {
            'key': self.key,
            'dropdown_id': self.dropdown_id,
            'dropdown_type': self.dropdown_type.value,
            'label': self.label,
            'form_id': self.form_id,
            'default_value': self.default_value,
            'selected_value': self.selected_value,
            'multiple': self.multiple,
            'searchable': self.searchable,
            'metadata': self.metadata,
            'total_options': len(self.options),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


# Global dropdown key manager instance
_global_dropdown_manager = DropdownKeyManager()


def get_dropdown_manager() -> DropdownKeyManager:
    """
    Get the global dropdown key manager instance.

    Returns:
        Global DropdownKeyManager instance
    """
    return _global_dropdown_manager
