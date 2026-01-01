"""core/forms.py - Form Management"""
import streamlit as st
from typing import Any, Dict, Optional, Callable

def create_form(form_id: str, submit_label: str = "Submit") -> Dict[str, Any]:
    """Erstelle ein Streamlit-Formular mit Validierung"""
    form_data = {}
    
    with st.form(form_id):
        yield form_data
        submitted = st.form_submit_button(submit_label)
        
    return submitted, form_data

def validate_form(data: Dict[str, Any], rules: Dict[str, Callable]) -> tuple[bool, Dict[str, str]]:
    """Validiere Formulardaten"""
    errors = {}
    for field, rule in rules.items():
        if field in data:
            error = rule(data[field])
            if error:
                errors[field] = error
    return len(errors) == 0, errors
