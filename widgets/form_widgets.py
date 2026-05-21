"""widgets/form_widgets.py - Custom Form Widgets"""
import streamlit as st
from typing import Any, Optional

def text_input_with_validation(label: str, key: str, validator: Optional[callable] = None, **kwargs) -> str:
    """Text-Input mit Validierung"""
    value = st.text_input(label, key=key, **kwargs)
    if validator and value:
        error = validator(value)
        if error:
            st.error(error)
    return value

def number_input_with_validation(label: str, key: str, min_value: Optional[float] = None, max_value: Optional[float] = None, **kwargs) -> float:
    """Number-Input mit Range-Validierung"""
    value = st.number_input(label, key=key, min_value=min_value, max_value=max_value, **kwargs)
    return value
