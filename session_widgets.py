"""
Session-Aware Widget Helpers
============================

Wrapper für Streamlit-Widgets mit automatischer Session-Persistierung.
"""

import streamlit as st

try:
    from core_integration import persist_session_input, is_feature_enabled
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False
    def persist_session_input(key, value, form_id=None, immediate=False): pass
    def is_feature_enabled(feature): return False


def session_text_input(label, key, form_id="default", **kwargs):
    """
    Text input with automatic session persistence.
    
    Args:
        label: Widget label
        key: Widget key
        form_id: Form ID for grouping
        **kwargs: Additional st.text_input arguments
    
    Returns:
        str: Input value
    """
    # Get value from widget
    value = st.text_input(label, key=key, **kwargs)
    
    # Persist if session management enabled
    if CORE_AVAILABLE and is_feature_enabled('session'):
        # Only persist on actual change
        if f"{key}_last" not in st.session_state or st.session_state[f"{key}_last"] != value:
            persist_session_input(key, value, form_id=form_id)
            st.session_state[f"{key}_last"] = value
    
    return value


def session_number_input(label, key, form_id="default", **kwargs):
    """
    Number input with automatic session persistence.
    
    Args:
        label: Widget label
        key: Widget key
        form_id: Form ID for grouping
        **kwargs: Additional st.number_input arguments
    
    Returns:
        float/int: Input value
    """
    value = st.number_input(label, key=key, **kwargs)
    
    if CORE_AVAILABLE and is_feature_enabled('session'):
        if f"{key}_last" not in st.session_state or st.session_state[f"{key}_last"] != value:
            persist_session_input(key, value, form_id=form_id)
            st.session_state[f"{key}_last"] = value
    
    return value


def session_selectbox(label, options, key, form_id="default", **kwargs):
    """
    Selectbox with automatic session persistence.
    
    Args:
        label: Widget label
        options: Options list
        key: Widget key
        form_id: Form ID for grouping
        **kwargs: Additional st.selectbox arguments
    
    Returns:
        Any: Selected value
    """
    value = st.selectbox(label, options, key=key, **kwargs)
    
    if CORE_AVAILABLE and is_feature_enabled('session'):
        if f"{key}_last" not in st.session_state or st.session_state[f"{key}_last"] != value:
            persist_session_input(key, value, form_id=form_id)
            st.session_state[f"{key}_last"] = value
    
    return value


def session_radio(label, options, key, form_id="default", **kwargs):
    """
    Radio buttons with automatic session persistence.
    
    Args:
        label: Widget label
        options: Options list
        key: Widget key
        form_id: Form ID for grouping
        **kwargs: Additional st.radio arguments
    
    Returns:
        Any: Selected value
    """
    value = st.radio(label, options, key=key, **kwargs)
    
    if CORE_AVAILABLE and is_feature_enabled('session'):
        if f"{key}_last" not in st.session_state or st.session_state[f"{key}_last"] != value:
            persist_session_input(key, value, form_id=form_id)
            st.session_state[f"{key}_last"] = value
    
    return value


def session_checkbox(label, key, form_id="default", **kwargs):
    """
    Checkbox with automatic session persistence.
    
    Args:
        label: Widget label
        key: Widget key
        form_id: Form ID for grouping
        **kwargs: Additional st.checkbox arguments
    
    Returns:
        bool: Checkbox state
    """
    value = st.checkbox(label, key=key, **kwargs)
    
    if CORE_AVAILABLE and is_feature_enabled('session'):
        if f"{key}_last" not in st.session_state or st.session_state[f"{key}_last"] != value:
            persist_session_input(key, value, form_id=form_id)
            st.session_state[f"{key}_last"] = value
    
    return value


def session_slider(label, key, form_id="default", **kwargs):
    """
    Slider with automatic session persistence.
    
    Args:
        label: Widget label
        key: Widget key
        form_id: Form ID for grouping
        **kwargs: Additional st.slider arguments
    
    Returns:
        float/int: Slider value
    """
    value = st.slider(label, key=key, **kwargs)
    
    if CORE_AVAILABLE and is_feature_enabled('session'):
        if f"{key}_last" not in st.session_state or st.session_state[f"{key}_last"] != value:
            persist_session_input(key, value, form_id=form_id)
            st.session_state[f"{key}_last"] = value
    
    return value


def persist_calculation_result(calc_type, result, immediate=False):
    """
    Persist calculation results for recovery.
    
    Args:
        calc_type: Type of calculation (e.g., 'pricing', 'pv_output')
        result: Calculation result dict
        immediate: If True, write to DB immediately
    """
    if CORE_AVAILABLE and is_feature_enabled('session'):
        key = f"calc_result_{calc_type}"
        persist_session_input(key, result, form_id="calculations", immediate=immediate)
