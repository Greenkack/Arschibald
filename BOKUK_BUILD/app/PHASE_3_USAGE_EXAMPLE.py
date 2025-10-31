"""
Phase 3 - Session Persistence Usage Examples
============================================

Zeigt wie man session_widgets.py in bestehenden Formularen nutzt.
"""

import streamlit as st
from session_widgets import (
    session_text_input,
    session_number_input,
    session_selectbox,
    session_checkbox,
    persist_calculation_result,
)


def example_customer_form():
    """
    Beispiel: Kundenformular mit Session-Persistierung
    
    Bei Browser-Refresh bleiben alle Eingaben erhalten!
    """
    st.markdown("### 👤 Kundendaten (mit Auto-Save)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # VORHER: st.text_input("Vorname", key="first_name")
        # NACHHER: Automatische Persistierung
        first_name = session_text_input(
            label="Vorname",
            key="customer_first_name",
            form_id="customer_data",  # Gruppiert alle Kundendaten
            placeholder="Max"
        )
    
    with col2:
        last_name = session_text_input(
            label="Nachname",
            key="customer_last_name",
            form_id="customer_data",
            placeholder="Mustermann"
        )
    
    email = session_text_input(
        label="E-Mail",
        key="customer_email",
        form_id="customer_data",
        placeholder="max@example.com"
    )
    
    col3, col4 = st.columns(2)
    
    with col3:
        num_persons = session_number_input(
            label="Anzahl Personen",
            key="customer_num_persons",
            form_id="customer_data",
            min_value=1,
            max_value=20,
            value=4
        )
    
    with col4:
        customer_type = session_selectbox(
            label="Kundentyp",
            options=["Privatkunde", "Gewerbekunde", "Landwirtschaft"],
            key="customer_type",
            form_id="customer_data"
        )
    
    newsletter = session_checkbox(
        label="Newsletter abonnieren",
        key="customer_newsletter",
        form_id="customer_data"
    )
    
    # Zeige Session-Status
    if st.session_state.get('user_session_recovered'):
        st.success("✅ Daten automatisch wiederhergestellt")
    
    return {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'num_persons': num_persons,
        'customer_type': customer_type,
        'newsletter': newsletter,
    }


def example_calculation_with_persistence():
    """
    Beispiel: Berechnung mit Ergebnis-Persistierung
    
    Nach Browser-Refresh ist das Ergebnis sofort verfügbar!
    """
    st.markdown("### 🧮 Berechnung mit Auto-Save")
    
    # Input
    investment = session_number_input(
        label="Investition (€)",
        key="calc_investment",
        form_id="calculation",
        min_value=0.0,
        value=15000.0,
        step=1000.0
    )
    
    savings_per_year = session_number_input(
        label="Ersparnis pro Jahr (€)",
        key="calc_savings",
        form_id="calculation",
        min_value=0.0,
        value=1500.0,
        step=100.0
    )
    
    if st.button("Berechnen", key="calc_button"):
        # Berechnung durchführen
        amortization_years = investment / savings_per_year if savings_per_year > 0 else 0
        
        result = {
            'investment': investment,
            'savings_per_year': savings_per_year,
            'amortization_years': amortization_years,
            'total_savings_20y': savings_per_year * 20,
        }
        
        # WICHTIG: Ergebnis persistieren für Recovery
        persist_calculation_result(
            calc_type='simple_amortization',
            result=result,
            immediate=True  # Sofort in DB schreiben
        )
        
        # In session_state speichern für aktuellen Tab
        st.session_state.last_calc_result = result
    
    # Ergebnis anzeigen (auch nach Refresh verfügbar)
    if 'last_calc_result' in st.session_state:
        result = st.session_state.last_calc_result
        
        st.markdown("#### 📊 Ergebnis:")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Amortisationszeit",
                f"{result['amortization_years']:.1f} Jahre"
            )
        
        with col2:
            st.metric(
                "Gesamtersparnis (20 Jahre)",
                f"{result['total_savings_20y']:,.0f} €"
            )
        
        st.info("💡 Diese Daten bleiben nach Browser-Refresh erhalten!")


def example_migration_pattern():
    """
    Beispiel: Schrittweise Migration von Standard zu Session-Widgets
    """
    st.markdown("### 🔄 Migrations-Muster")
    
    st.code("""
# === VORHER (Standard Streamlit) ===
name = st.text_input("Name", key="name")
age = st.number_input("Alter", key="age", min_value=0)
city = st.selectbox("Stadt", ["Berlin", "Hamburg", "München"], key="city")

# === NACHHER (Mit Session-Persistence) ===
from session_widgets import session_text_input, session_number_input, session_selectbox

name = session_text_input("Name", key="name", form_id="user_profile")
age = session_number_input("Alter", key="age", form_id="user_profile", min_value=0)
city = session_selectbox("Stadt", ["Berlin", "Hamburg", "München"], key="city", form_id="user_profile")

# VORTEILE:
# ✅ Bei Browser-Refresh bleiben alle Werte erhalten
# ✅ Multi-Tab-Unterstützung (gleiche Session)
# ✅ Automatische Gruppierung nach form_id
# ✅ Keine manuelle Persistierung notwendig
# ✅ Zero Breaking Changes - drop-in replacement
    """, language="python")


def example_advanced_usage():
    """
    Beispiel: Erweiterte Nutzung
    """
    st.markdown("### 🎓 Erweiterte Nutzung")
    
    st.markdown("#### 1. Immediate Write für kritische Daten:")
    st.code("""
from session_widgets import persist_session_input

# Sofort in DB schreiben (nicht warten)
persist_session_input(
    key="critical_data",
    value=important_value,
    form_id="critical_form",
    immediate=True  # ⚡ Sofort persistieren
)
    """, language="python")
    
    st.markdown("#### 2. Berechnungsergebnisse speichern:")
    st.code("""
from session_widgets import persist_calculation_result

# Nach komplexer Berechnung
result = expensive_calculation()
persist_calculation_result(
    calc_type='complex_pricing',
    result=result,
    immediate=True
)
# Nach Refresh ist result sofort verfügbar!
    """, language="python")
    
    st.markdown("#### 3. Feature deaktivieren (fallback):")
    st.code("""
# In .env:
FEATURE_SESSION_PERSISTENCE=false

# Widgets funktionieren weiterhin normal!
# Nur ohne Persistierung
    """, language="bash")


def main():
    """Haupt-Demo-App"""
    st.set_page_config(
        page_title="Phase 3 - Session Persistence Demo",
        page_icon="💾",
        layout="wide"
    )
    
    st.title("💾 Phase 3: Session Persistence Demo")
    
    # Tab-Navigation
    tab1, tab2, tab3, tab4 = st.tabs([
        "👤 Kundenformular",
        "🧮 Berechnung",
        "🔄 Migration",
        "🎓 Advanced"
    ])
    
    with tab1:
        customer_data = example_customer_form()
        
        with st.expander("📋 Eingabedaten anzeigen"):
            st.json(customer_data)
    
    with tab2:
        example_calculation_with_persistence()
    
    with tab3:
        example_migration_pattern()
    
    with tab4:
        example_advanced_usage()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **💡 Tipp:** Drücke F5 um Browser zu refreshen - alle Daten bleiben erhalten!
    
    **Konfiguration:**
    - `.env`: `FEATURE_SESSION_PERSISTENCE=true`
    - Session-TTL: 24 Stunden (konfigurierbar)
    - DB: `./data/app_data.db`
    """)


if __name__ == "__main__":
    main()
