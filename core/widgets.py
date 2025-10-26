"""Controlled Widget System with Auto-Persistence

This module provides controlled widget wrappers that implement unified state management,
automatic persistence, and validation for all Streamlit widgets.

Key Features:
- Immediate session_state updates
- Debounced database persistence
- Real-time validation with error display
- Consistent behavior across all widget types
- Change detection and tracking
"""

import hashlib
import threading
from collections.abc import Callable
from datetime import datetime
from typing import Any

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

from .session import get_current_session, persist_input

try:
    from .widget_persistence import save_widget_state
    PERSISTENCE_AVAILABLE = True
except ImportError:
    PERSISTENCE_AVAILABLE = False
    save_widget_state = None


class WidgetState:
    """Widget state tracking with change detection and validation"""

    def __init__(self, key: str, value: Any = None):
        self.key = key
        self.value = value
        self.previous_value = None
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.is_valid = True
        self.is_dirty = False
        self.last_changed = datetime.now()
        self.change_count = 0

    def update(self, new_value: Any) -> bool:
        """
        Update widget value and track changes

        Args:
            new_value: New widget value

        Returns:
            True if value changed, False otherwise
        """
        if new_value != self.value:
            self.previous_value = self.value
            self.value = new_value
            self.is_dirty = True
            self.last_changed = datetime.now()
            self.change_count += 1
            return True
        return False

    def add_error(self, error: str) -> None:
        """Add validation error"""
        if error not in self.errors:
            self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """Add validation warning"""
        if warning not in self.warnings:
            self.warnings.append(warning)

    def clear_errors(self) -> None:
        """Clear all errors"""
        self.errors = []
        self.is_valid = True

    def clear_warnings(self) -> None:
        """Clear all warnings"""
        self.warnings = []

    def mark_clean(self) -> None:
        """Mark widget as clean (saved)"""
        self.is_dirty = False


class WidgetRegistry:
    """Global registry for widget states"""

    def __init__(self):
        self._states: dict[str, WidgetState] = {}
        self._lock = threading.Lock()

    def get_state(self, key: str, default_value: Any = None) -> WidgetState:
        """Get or create widget state"""
        with self._lock:
            if key not in self._states:
                self._states[key] = WidgetState(key, default_value)
            return self._states[key]

    def update_state(self, key: str, value: Any) -> bool:
        """Update widget state"""
        state = self.get_state(key)
        return state.update(value)

    def get_all_states(self) -> dict[str, WidgetState]:
        """Get all widget states"""
        with self._lock:
            return self._states.copy()

    def clear_state(self, key: str) -> None:
        """Clear widget state"""
        with self._lock:
            self._states.pop(key, None)

    def clear_all_states(self) -> None:
        """Clear all widget states"""
        with self._lock:
            self._states.clear()


# Global widget registry
_widget_registry = WidgetRegistry()


def get_widget_registry() -> WidgetRegistry:
    """Get global widget registry"""
    return _widget_registry


def _generate_stable_key(prefix: str, label: str = None, **kwargs) -> str:
    """
    Generate stable widget key from parameters

    Args:
        prefix: Widget type prefix (e.g., 'text', 'select')
        label: Widget label
        **kwargs: Additional parameters for key generation

    Returns:
        Stable widget key
    """
    # Create deterministic key from parameters
    key_parts = [prefix]

    if label:
        key_parts.append(label)

    # Add relevant kwargs to key
    for k, v in sorted(kwargs.items()):
        if k not in ['key', 'on_change', 'args', 'kwargs', 'help', 'disabled']:
            key_parts.append(f"{k}={v}")

    key_string = "_".join(str(p) for p in key_parts)

    # Hash if too long
    if len(key_string) > 100:
        hash_suffix = hashlib.md5(key_string.encode()).hexdigest()[:8]
        key_string = f"{prefix}_{hash_suffix}"

    return key_string


def _handle_widget_change(
    key: str,
    value: Any,
    validator: Callable[[Any], tuple[bool, list[str], list[str]]] | None = None
) -> None:
    """
    Handle widget value change with validation and persistence

    Args:
        key: Widget key
        value: New widget value
        validator: Optional validation function returning (is_valid, errors, warnings)
    """
    # Get widget state
    registry = get_widget_registry()
    state = registry.get_state(key)

    # Update state
    changed = state.update(value)

    if not changed:
        return

    # Clear previous validation results
    state.clear_errors()
    state.clear_warnings()

    # Run validation if provided
    if validator:
        try:
            is_valid, errors, warnings = validator(value)
            state.is_valid = is_valid

            for error in errors:
                state.add_error(error)

            for warning in warnings:
                state.add_warning(warning)
        except Exception as e:
            logger.error("Widget validation failed", key=key, error=str(e))
            state.add_error(f"Validation error: {str(e)}")

    # Persist to session_state and schedule DB write
    try:
        persist_input(key, value)
        logger.debug("Widget value persisted", key=key, value=value)

        # Also persist to widget persistence engine
        if PERSISTENCE_AVAILABLE and save_widget_state:
            session = get_current_session()
            save_widget_state(
                session_id=session.session_id,
                widget_key=key,
                widget_value=value,
                is_valid=state.is_valid,
                errors=state.errors,
                warnings=state.warnings
            )
    except Exception as e:
        logger.error("Widget persistence failed", key=key, error=str(e))


def _display_widget_errors(state: WidgetState) -> None:
    """Display widget validation errors and warnings"""
    if not STREAMLIT_AVAILABLE or not st:
        return

    if state.errors:
        for error in state.errors:
            st.error(f"❌ {error}", icon="🚨")

    if state.warnings:
        for warning in state.warnings:
            st.warning(f"⚠️ {warning}", icon="⚠️")


def s_text(
    label: str = None,
    value: str = "",
    key: str = None,
    max_chars: int = None,
    type: str = "default",
    help: str = None,
    placeholder: str = None,
    disabled: bool = False,
    validator: Callable[[str], tuple[bool, list[str], list[str]]] | None = None,
    **kwargs
) -> str:
    """
    Controlled text input with auto-persistence

    Args:
        label: Widget label
        value: Default value
        key: Widget key (auto-generated if not provided)
        max_chars: Maximum character limit
        type: Input type ('default' or 'password')
        help: Help text
        placeholder: Placeholder text
        disabled: Whether widget is disabled
        validator: Optional validation function
        **kwargs: Additional Streamlit text_input parameters

    Returns:
        Current text value
    """
    if not STREAMLIT_AVAILABLE or not st:
        return value

    # Generate stable key if not provided
    if not key:
        key = _generate_stable_key("text", label, type=type)

    # Get widget state
    registry = get_widget_registry()
    state = registry.get_state(key, value)

    # Get current value from session_state or use default
    current_value = st.session_state.get(key, state.value or value)

    # Create on_change callback
    def on_change():
        new_value = st.session_state[key]
        _handle_widget_change(key, new_value, validator)

    # Render widget
    result = st.text_input(
        label or key,
        value=current_value,
        key=key,
        max_chars=max_chars,
        type=type,
        help=help,
        placeholder=placeholder,
        disabled=disabled,
        on_change=on_change,
        **kwargs
    )

    # Display errors/warnings
    _display_widget_errors(state)

    return result


def s_number(
    label: str = None,
    value: int | float = 0,
    key: str = None,
    min_value: int | float = None,
    max_value: int | float = None,
    step: int | float = None,
    format: str = None,
    help: str = None,
    disabled: bool = False,
    validator: Callable[[int | float], tuple[bool, list[str], list[str]]] | None = None,
    **kwargs
) -> int | float:
    """
    Controlled number input with auto-persistence

    Args:
        label: Widget label
        value: Default value
        key: Widget key (auto-generated if not provided)
        min_value: Minimum value
        max_value: Maximum value
        step: Step size
        format: Number format string
        help: Help text
        disabled: Whether widget is disabled
        validator: Optional validation function
        **kwargs: Additional Streamlit number_input parameters

    Returns:
        Current number value
    """
    if not STREAMLIT_AVAILABLE or not st:
        return value

    # Generate stable key if not provided
    if not key:
        key = _generate_stable_key(
            "number", label, min=min_value, max=max_value)

    # Get widget state
    registry = get_widget_registry()
    state = registry.get_state(key, value)

    # Get current value from session_state or use default
    current_value = st.session_state.get(
        key, state.value if state.value is not None else value)

    # Create on_change callback
    def on_change():
        new_value = st.session_state[key]
        _handle_widget_change(key, new_value, validator)

    # Render widget
    result = st.number_input(
        label or key,
        value=current_value,
        key=key,
        min_value=min_value,
        max_value=max_value,
        step=step,
        format=format,
        help=help,
        disabled=disabled,
        on_change=on_change,
        **kwargs
    )

    # Display errors/warnings
    _display_widget_errors(state)

    return result


def s_select(
    options: list[Any],
    label: str = None,
    index: int = 0,
    key: str = None,
    format_func: Callable = str,
    help: str = None,
    disabled: bool = False,
    validator: Callable[[Any], tuple[bool, list[str], list[str]]] | None = None,
    **kwargs
) -> Any:
    """
    Controlled selectbox with auto-persistence

    Args:
        options: List of options
        label: Widget label
        index: Default selected index
        key: Widget key (auto-generated if not provided)
        format_func: Function to format options
        help: Help text
        disabled: Whether widget is disabled
        validator: Optional validation function
        **kwargs: Additional Streamlit selectbox parameters

    Returns:
        Selected option
    """
    if not STREAMLIT_AVAILABLE or not st:
        return options[index] if options else None

    # Generate stable key if not provided
    if not key:
        key = _generate_stable_key("select", label)

    # Get widget state
    registry = get_widget_registry()
    default_value = options[index] if options and index < len(
        options) else None
    state = registry.get_state(key, default_value)

    # Get current value from session_state or use default
    current_value = st.session_state.get(
        key, state.value if state.value is not None else default_value)

    # Determine current index
    try:
        current_index = options.index(
            current_value) if current_value in options else index
    except (ValueError, IndexError):
        current_index = index

    # Create on_change callback
    def on_change():
        new_value = st.session_state[key]
        _handle_widget_change(key, new_value, validator)

    # Render widget
    result = st.selectbox(
        label or key,
        options=options,
        index=current_index,
        key=key,
        format_func=format_func,
        help=help,
        disabled=disabled,
        on_change=on_change,
        **kwargs
    )

    # Display errors/warnings
    _display_widget_errors(state)

    return result


def s_checkbox(
    label: str = None,
    value: bool = False,
    key: str = None,
    help: str = None,
    disabled: bool = False,
    validator: Callable[[bool], tuple[bool, list[str], list[str]]] | None = None,
    **kwargs
) -> bool:
    """
    Controlled checkbox with auto-persistence

    Args:
        label: Widget label
        value: Default value
        key: Widget key (auto-generated if not provided)
        help: Help text
        disabled: Whether widget is disabled
        validator: Optional validation function
        **kwargs: Additional Streamlit checkbox parameters

    Returns:
        Current checkbox value
    """
    if not STREAMLIT_AVAILABLE or not st:
        return value

    # Generate stable key if not provided
    if not key:
        key = _generate_stable_key("checkbox", label)

    # Get widget state
    registry = get_widget_registry()
    state = registry.get_state(key, value)

    # Get current value from session_state or use default
    current_value = st.session_state.get(
        key, state.value if state.value is not None else value)

    # Create on_change callback
    def on_change():
        new_value = st.session_state[key]
        _handle_widget_change(key, new_value, validator)

    # Render widget
    result = st.checkbox(
        label or key,
        value=current_value,
        key=key,
        help=help,
        disabled=disabled,
        on_change=on_change,
        **kwargs
    )

    # Display errors/warnings
    _display_widget_errors(state)

    return result


def s_date(
    label: str = None,
    value: Any = None,
    key: str = None,
    min_value: Any = None,
    max_value: Any = None,
    help: str = None,
    disabled: bool = False,
    validator: Callable[[Any], tuple[bool, list[str], list[str]]] | None = None,
    **kwargs
) -> Any:
    """
    Controlled date input with auto-persistence

    Args:
        label: Widget label
        value: Default value
        key: Widget key (auto-generated if not provided)
        min_value: Minimum date
        max_value: Maximum date
        help: Help text
        disabled: Whether widget is disabled
        validator: Optional validation function
        **kwargs: Additional Streamlit date_input parameters

    Returns:
        Current date value
    """
    if not STREAMLIT_AVAILABLE or not st:
        return value

    # Generate stable key if not provided
    if not key:
        key = _generate_stable_key("date", label)

    # Get widget state
    registry = get_widget_registry()
    state = registry.get_state(key, value)

    # Get current value from session_state or use default
    current_value = st.session_state.get(
        key, state.value if state.value is not None else value)

    # Create on_change callback
    def on_change():
        new_value = st.session_state[key]
        _handle_widget_change(key, new_value, validator)

    # Render widget
    result = st.date_input(
        label or key,
        value=current_value,
        key=key,
        min_value=min_value,
        max_value=max_value,
        help=help,
        disabled=disabled,
        on_change=on_change,
        **kwargs
    )

    # Display errors/warnings
    _display_widget_errors(state)

    return result


def s_file(
    label: str = None,
    type: str | list[str] = None,
    key: str = None,
    accept_multiple_files: bool = False,
    help: str = None,
    disabled: bool = False,
    validator: Callable[[Any], tuple[bool, list[str], list[str]]] | None = None,
    **kwargs
) -> Any:
    """
    Controlled file uploader with auto-persistence

    Args:
        label: Widget label
        type: Allowed file types
        key: Widget key (auto-generated if not provided)
        accept_multiple_files: Whether to accept multiple files
        help: Help text
        disabled: Whether widget is disabled
        validator: Optional validation function
        **kwargs: Additional Streamlit file_uploader parameters

    Returns:
        Uploaded file(s)
    """
    if not STREAMLIT_AVAILABLE or not st:
        return None

    # Generate stable key if not provided
    if not key:
        key = _generate_stable_key(
            "file", label, type=type, multiple=accept_multiple_files)

    # Get widget state
    registry = get_widget_registry()
    state = registry.get_state(key, None)

    # Create on_change callback
    def on_change():
        new_value = st.session_state[key]
        _handle_widget_change(key, new_value, validator)

    # Render widget
    result = st.file_uploader(
        label or key,
        type=type,
        key=key,
        accept_multiple_files=accept_multiple_files,
        help=help,
        disabled=disabled,
        on_change=on_change,
        **kwargs
    )

    # Display errors/warnings
    _display_widget_errors(state)

    return result


def s_multiselect(
    options: list[Any],
    label: str = None,
    default: list[Any] = None,
    key: str = None,
    format_func: Callable = str,
    max_selections: int = None,
    help: str = None,
    disabled: bool = False,
    validator: Callable[[list[Any]], tuple[bool, list[str], list[str]]] | None = None,
    **kwargs
) -> list[Any]:
    """
    Controlled multiselect with auto-persistence

    Args:
        options: List of options
        label: Widget label
        default: Default selected values
        key: Widget key (auto-generated if not provided)
        format_func: Function to format options
        max_selections: Maximum number of selections
        help: Help text
        disabled: Whether widget is disabled
        validator: Optional validation function
        **kwargs: Additional Streamlit multiselect parameters

    Returns:
        List of selected options
    """
    if not STREAMLIT_AVAILABLE or not st:
        return default or []

    # Generate stable key if not provided
    if not key:
        key = _generate_stable_key("multiselect", label)

    # Get widget state
    registry = get_widget_registry()
    state = registry.get_state(key, default or [])

    # Get current value from session_state or use default
    current_value = st.session_state.get(
        key, state.value if state.value is not None else (
            default or []))

    # Create on_change callback
    def on_change():
        new_value = st.session_state[key]
        _handle_widget_change(key, new_value, validator)

    # Render widget
    result = st.multiselect(
        label or key,
        options=options,
        default=current_value,
        key=key,
        format_func=format_func,
        max_selections=max_selections,
        help=help,
        disabled=disabled,
        on_change=on_change,
        **kwargs
    )

    # Display errors/warnings
    _display_widget_errors(state)

    return result


def s_slider(label: str = None,
             min_value: int | float = 0,
             max_value: int | float = 100,
             value: int | float | tuple = None,
             key: str = None,
             step: int | float = None,
             format: str = None,
             help: str = None,
             disabled: bool = False,
             validator: Callable[[int | float | tuple],
                                 tuple[bool,
                                       list[str],
                                       list[str]]] | None = None,
             **kwargs) -> int | float | tuple:
    """
    Controlled slider with auto-persistence

    Args:
        label: Widget label
        min_value: Minimum value
        max_value: Maximum value
        value: Default value (single value or tuple for range)
        key: Widget key (auto-generated if not provided)
        step: Step size
        format: Number format string
        help: Help text
        disabled: Whether widget is disabled
        validator: Optional validation function
        **kwargs: Additional Streamlit slider parameters

    Returns:
        Current slider value
    """
    if not STREAMLIT_AVAILABLE or not st:
        return value if value is not None else min_value

    # Generate stable key if not provided
    if not key:
        key = _generate_stable_key(
            "slider", label, min=min_value, max=max_value)

    # Get widget state
    default_value = value if value is not None else min_value
    registry = get_widget_registry()
    state = registry.get_state(key, default_value)

    # Get current value from session_state or use default
    current_value = st.session_state.get(
        key, state.value if state.value is not None else default_value)

    # Create on_change callback
    def on_change():
        new_value = st.session_state[key]
        _handle_widget_change(key, new_value, validator)

    # Render widget
    result = st.slider(
        label or key,
        min_value=min_value,
        max_value=max_value,
        value=current_value,
        key=key,
        step=step,
        format=format,
        help=help,
        disabled=disabled,
        on_change=on_change,
        **kwargs
    )

    # Display errors/warnings
    _display_widget_errors(state)

    return result


def s_textarea(
    label: str = None,
    value: str = "",
    key: str = None,
    height: int = None,
    max_chars: int = None,
    help: str = None,
    placeholder: str = None,
    disabled: bool = False,
    validator: Callable[[str], tuple[bool, list[str], list[str]]] | None = None,
    **kwargs
) -> str:
    """
    Controlled text area with auto-persistence

    Args:
        label: Widget label
        value: Default value
        key: Widget key (auto-generated if not provided)
        height: Height in pixels
        max_chars: Maximum character limit
        help: Help text
        placeholder: Placeholder text
        disabled: Whether widget is disabled
        validator: Optional validation function
        **kwargs: Additional Streamlit text_area parameters

    Returns:
        Current text value
    """
    if not STREAMLIT_AVAILABLE or not st:
        return value

    # Generate stable key if not provided
    if not key:
        key = _generate_stable_key("textarea", label)

    # Get widget state
    registry = get_widget_registry()
    state = registry.get_state(key, value)

    # Get current value from session_state or use default
    current_value = st.session_state.get(key, state.value or value)

    # Create on_change callback
    def on_change():
        new_value = st.session_state[key]
        _handle_widget_change(key, new_value, validator)

    # Render widget
    result = st.text_area(
        label or key,
        value=current_value,
        key=key,
        height=height,
        max_chars=max_chars,
        help=help,
        placeholder=placeholder,
        disabled=disabled,
        on_change=on_change,
        **kwargs
    )

    # Display errors/warnings
    _display_widget_errors(state)

    return result


def s_radio(
    options: list[Any],
    label: str = None,
    index: int = 0,
    key: str = None,
    format_func: Callable = str,
    horizontal: bool = False,
    help: str = None,
    disabled: bool = False,
    validator: Callable[[Any], tuple[bool, list[str], list[str]]] | None = None,
    **kwargs
) -> Any:
    """
    Controlled radio buttons with auto-persistence

    Args:
        options: List of options
        label: Widget label
        index: Default selected index
        key: Widget key (auto-generated if not provided)
        format_func: Function to format options
        horizontal: Whether to display horizontally
        help: Help text
        disabled: Whether widget is disabled
        validator: Optional validation function
        **kwargs: Additional Streamlit radio parameters

    Returns:
        Selected option
    """
    if not STREAMLIT_AVAILABLE or not st:
        return options[index] if options else None

    # Generate stable key if not provided
    if not key:
        key = _generate_stable_key("radio", label, horizontal=horizontal)

    # Get widget state
    registry = get_widget_registry()
    default_value = options[index] if options and index < len(
        options) else None
    state = registry.get_state(key, default_value)

    # Get current value from session_state or use default
    current_value = st.session_state.get(
        key, state.value if state.value is not None else default_value)

    # Determine current index
    try:
        current_index = options.index(
            current_value) if current_value in options else index
    except (ValueError, IndexError):
        current_index = index

    # Create on_change callback
    def on_change():
        new_value = st.session_state[key]
        _handle_widget_change(key, new_value, validator)

    # Render widget
    result = st.radio(
        label or key,
        options=options,
        index=current_index,
        key=key,
        format_func=format_func,
        horizontal=horizontal,
        help=help,
        disabled=disabled,
        on_change=on_change,
        **kwargs
    )

    # Display errors/warnings
    _display_widget_errors(state)

    return result


# Utility functions for widget management

def get_widget_state(key: str) -> WidgetState | None:
    """Get widget state by key"""
    registry = get_widget_registry()
    return registry.get_state(key)


def clear_widget_state(key: str) -> None:
    """Clear widget state"""
    registry = get_widget_registry()
    registry.clear_state(key)


def clear_all_widget_states() -> None:
    """Clear all widget states"""
    registry = get_widget_registry()
    registry.clear_all_states()


def get_all_widget_states() -> dict[str, WidgetState]:
    """Get all widget states"""
    registry = get_widget_registry()
    return registry.get_all_states()


def get_dirty_widgets() -> list[str]:
    """Get list of dirty (unsaved) widget keys"""
    registry = get_widget_registry()
    states = registry.get_all_states()
    return [key for key, state in states.items() if state.is_dirty]


def get_invalid_widgets() -> list[str]:
    """Get list of invalid widget keys"""
    registry = get_widget_registry()
    states = registry.get_all_states()
    return [key for key, state in states.items() if not state.is_valid]


def mark_all_widgets_clean() -> None:
    """Mark all widgets as clean (saved)"""
    registry = get_widget_registry()
    states = registry.get_all_states()
    for state in states.values():
        state.mark_clean()
