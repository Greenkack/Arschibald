import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(page_title="CRM Tab Test", layout="wide")

st.title(" CRM Tab Test")

# Import CRM
try:
    import crm
    st.success(" CRM Modul geladen")
    
    # Check if render_crm has tabs
    import inspect
    source = inspect.getsource(crm.render_crm)
    
    if "st.tabs" in source:
        st.success(" st.tabs() gefunden im Code!")
        st.code("""
crm_tabs = st.tabs([
    " Kundenverwaltung",
    " Lead Scoring", 
    " Backup & Daten"
])
        """, language="python")
    else:
        st.error(" KEINE Tabs gefunden!")
        
    # Show first 50 lines of render_crm
    lines = source.split('\n')[:50]
    st.subheader("Erste 50 Zeilen von render_crm():")
    st.code('\n'.join(lines), language="python")
    
except Exception as e:
    st.error(f" Fehler: {e}")
    import traceback
    st.code(traceback.format_exc())
