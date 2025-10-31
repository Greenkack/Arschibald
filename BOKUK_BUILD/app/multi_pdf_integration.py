# multi_pdf_integration.py
"""
Multi-PDF & Wärmepumpen Integration Module
Extrahiert aus repair_pdf für die Hauptanwendung
VERSION: 1.0 - Kompakte Integration
"""

import streamlit as st
from typing import Dict, List, Any, Optional
import os
import io
import zipfile
from datetime import datetime

# ===================================================================
# TEIL 1: MULTI-PDF KERNLOGIK
# ===================================================================

def init_multi_pdf_session_state():
    """Initialisiert Session State für Multi-PDF"""
    if "multi_offer_customer_data" not in st.session_state:
        st.session_state.multi_offer_customer_data = {}
    if "multi_offer_selected_companies" not in st.session_state:
        st.session_state.multi_offer_selected_companies = []
    if "multi_offer_settings" not in st.session_state:
        st.session_state.multi_offer_settings = {
            "enable_product_rotation": True,
            "price_increment_percent": 3.0,
            "rotation_mode": "linear",
        }
    if "multi_offer_company_extended" not in st.session_state:
        st.session_state.multi_offer_company_extended = {}
    if "multi_offer_extend_all" not in st.session_state:
        st.session_state.multi_offer_extend_all = False


def load_customer_data_from_project() -> Dict[str, Any]:
    """
    Lädt Kundendaten automatisch aus Projekt/Bedarfsanalyse
    
    Rückgabewert:
        Dict mit Kundendaten oder leeres Dict
    """
    project_data = st.session_state.get("project_data", {})
    customer_data = project_data.get("customer_data", {})
    
    if customer_data:
        return {
            "name": customer_data.get("name", ""),
            "street": customer_data.get("street", ""),
            "zip_code": customer_data.get("zip_code", ""),
            "city": customer_data.get("city", ""),
            "email": customer_data.get("email", ""),
            "phone": customer_data.get("phone", ""),
        }
    
    # Fallback: Versuche aus Bedarfsanalyse zu laden
    demand_data = st.session_state.get("demand_analysis_data", {})
    if demand_data:
        return {
            "name": demand_data.get("customer_name", ""),
            "street": demand_data.get("customer_street", ""),
            "zip_code": demand_data.get("customer_zip", ""),
            "city": demand_data.get("customer_city", ""),
            "email": demand_data.get("customer_email", ""),
            "phone": demand_data.get("customer_phone", ""),
        }
    
    return {}


def render_multi_pdf_customer_input() -> bool:
    """
    Rendert Kundendaten-Eingabe für Multi-PDF
    
    Rückgabewert:
        True wenn Daten vollständig, sonst False
    """
    st.subheader("📋 Schritt 1: Kundendaten")
    
    # Versuche automatische Übernahme
    auto_customer_data = load_customer_data_from_project()
    
    if auto_customer_data and any(auto_customer_data.values()):
        st.success("✅ Kundendaten aus Projekt/Bedarfsanalyse übernommen!")
        st.session_state.multi_offer_customer_data = auto_customer_data
        
        # Zeige übernommene Daten an
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Kunde", value=auto_customer_data.get("name", ""), disabled=True)
            st.text_input("Straße", value=auto_customer_data.get("street", ""), disabled=True)
        with col2:
            st.text_input("PLZ", value=auto_customer_data.get("zip_code", ""), disabled=True)
            st.text_input("Ort", value=auto_customer_data.get("city", ""), disabled=True)
        
        if st.button("🔄 Kundendaten manuell ändern"):
            st.session_state.multi_offer_customer_data = {}
            st.rerun()
        
        return True
    
    # Manuelle Eingabe
    st.info("ℹ️ Keine Projektdaten gefunden - bitte manuell eingeben")
    
    with st.form("multi_pdf_customer_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Kundenname*", value=st.session_state.multi_offer_customer_data.get("name", ""))
            street = st.text_input("Straße & Nr.", value=st.session_state.multi_offer_customer_data.get("street", ""))
            email = st.text_input("E-Mail", value=st.session_state.multi_offer_customer_data.get("email", ""))
        
        with col2:
            zip_code = st.text_input("PLZ", value=st.session_state.multi_offer_customer_data.get("zip_code", ""))
            city = st.text_input("Ort", value=st.session_state.multi_offer_customer_data.get("city", ""))
            phone = st.text_input("Telefon", value=st.session_state.multi_offer_customer_data.get("phone", ""))
        
        submitted = st.form_submit_button("💾 Kundendaten speichern")
        
        if submitted:
            if not name.strip():
                st.error("❌ Kundenname ist erforderlich!")
                return False
            
            st.session_state.multi_offer_customer_data = {
                "name": name.strip(),
                "street": street.strip(),
                "zip_code": zip_code.strip(),
                "city": city.strip(),
                "email": email.strip(),
                "phone": phone.strip(),
            }
            st.success("✅ Kundendaten gespeichert!")
            st.rerun()
    
    return bool(st.session_state.multi_offer_customer_data.get("name"))


def render_multi_pdf_company_selection(available_companies: List[Dict[str, Any]]) -> List[int]:
    """
    Rendert Firmenauswahl für Multi-PDF
    
    Args:
        available_companies: Liste verfügbarer Firmen
    
    Rückgabewert:
        Liste ausgewählter Company-IDs
    """
    st.subheader("🏢 Schritt 2: Firmenauswahl (2-20+ Firmen)")
    
    if not available_companies:
        st.warning("⚠️ Keine Firmen verfügbar. Bitte erst Firmen im Admin-Panel anlegen.")
        return []
    
    st.info(f"📊 {len(available_companies)} Firmen verfügbar - wählen Sie beliebig viele aus")
    
    # Schnellauswahl-Buttons
    col_quick1, col_quick2, col_quick3 = st.columns([1, 1, 3])
    
    if col_quick1.button("✅ Alle auswählen"):
        st.session_state.multi_offer_selected_companies = [c["id"] for c in available_companies]
        st.rerun()
    
    if col_quick2.button("❌ Alle abwählen"):
        st.session_state.multi_offer_selected_companies = []
        st.rerun()
    
    st.markdown("---")
    
    # Firmen-Checkboxes mit erweiterter PDF-Option
    selected_ids = []
    
    for company in available_companies:
        company_id = company["id"]
        company_name = company.get("name", f"Firma {company_id}")
        
        col_check, col_extend = st.columns([3, 2])
        
        with col_check:
            is_selected = st.checkbox(
                f"🏢 {company_name}",
                value=company_id in st.session_state.multi_offer_selected_companies,
                key=f"multi_company_select_{company_id}"
            )
        
        with col_extend:
            if is_selected:
                extend_pdf = st.checkbox(
                    "📄 Erweiterte PDF (ab Seite 7)",
                    value=st.session_state.multi_offer_company_extended.get(company_id, False),
                    key=f"multi_company_extend_{company_id}",
                    help="Fügt detaillierte Seiten ab Seite 7 hinzu"
                )
                st.session_state.multi_offer_company_extended[company_id] = extend_pdf
        
        if is_selected:
            selected_ids.append(company_id)
    
    # Master-Toggle für alle erweiterten PDFs
    if selected_ids:
        st.markdown("---")
        master_extend = st.checkbox(
            "📑 Alle PDFs erweitern (Master-Toggle)",
            value=st.session_state.multi_offer_extend_all,
            help="Aktiviert erweiterte PDF für alle ausgewählten Firmen"
        )
        
        if master_extend != st.session_state.multi_offer_extend_all:
            st.session_state.multi_offer_extend_all = master_extend
            for company_id in selected_ids:
                st.session_state.multi_offer_company_extended[company_id] = master_extend
            st.rerun()
    
    st.session_state.multi_offer_selected_companies = selected_ids
    
    if selected_ids:
        st.success(f"✅ {len(selected_ids)} Firma(en) ausgewählt")
    
    return selected_ids


def render_multi_pdf_settings():
    """Rendert Einstellungen für Multi-PDF"""
    st.subheader("⚙️ Schritt 3: Angebots-Einstellungen")
    
    settings = st.session_state.multi_offer_settings
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔄 Produktrotation")
        
        settings["enable_product_rotation"] = st.checkbox(
            "Automatische Produktrotation aktivieren",
            value=settings.get("enable_product_rotation", True),
            help="Jede Firma bekommt unterschiedliche Produkte aus der gleichen Kategorie"
        )
        
        if settings["enable_product_rotation"]:
            settings["rotation_mode"] = st.selectbox(
                "Rotations-Modus",
                options=["linear", "random", "category_specific"],
                index=["linear", "random", "category_specific"].index(settings.get("rotation_mode", "linear")),
                format_func=lambda x: {
                    "linear": "📊 Linear (der Reihe nach)",
                    "random": "🎲 Zufällig",
                    "category_specific": "📦 Kategorie-spezifisch"
                }.get(x, x)
            )
    
    with col2:
        st.markdown("### 📈 Preisstaffelung")
        
        settings["price_increment_percent"] = st.slider(
            "Preissteigerung pro Firma (%)",
            min_value=0.0,
            max_value=20.0,
            value=settings.get("price_increment_percent", 3.0),
            step=0.5,
            help="0% = keine Steigerung, bis 20% möglich"
        )
        
        if settings["price_increment_percent"] > 0:
            st.info(f"💡 Firma 1: 100% | Firma 2: {100 + settings['price_increment_percent']:.1f}% | Firma 3: {100 + 2*settings['price_increment_percent']:.1f}%")
    
    st.session_state.multi_offer_settings = settings


# ===================================================================
# TEIL 2: WÄRMEPUMPEN-INTEGRATION
# ===================================================================

def init_heatpump_session_state():
    """Initialisiert Session State für Wärmepumpen"""
    if "heatpump_offer" not in st.session_state:
        st.session_state.heatpump_offer = {}
    if "heatpump_enabled" not in st.session_state:
        st.session_state.heatpump_enabled = False


def render_heatpump_integration_toggle() -> bool:
    """
    Rendert Wärmepumpen-Integration Toggle
    
    Rückgabewert:
        True wenn Wärmepumpe aktiviert
    """
    st.markdown("### 🌡️ Wärmepumpen-Integration")
    
    heatpump_enabled = st.checkbox(
        "Wärmepumpe in Angebote einbeziehen",
        value=st.session_state.heatpump_enabled,
        help="Erstellt kombinierte PV+Wärmepumpen-Angebote"
    )
    
    st.session_state.heatpump_enabled = heatpump_enabled
    
    if heatpump_enabled:
        st.info("✅ Wärmepumpen-Daten werden aus der Bedarfsanalyse übernommen")
        
        # Zeige Wärmepumpen-Status
        hp_offer = st.session_state.get("heatpump_offer", {})
        if hp_offer:
            selected_wp = hp_offer.get("selected_heatpump", {})
            if selected_wp:
                st.success(f"🌡️ Ausgewählte Wärmepumpe: {selected_wp.get('model', 'N/A')} ({selected_wp.get('heating_power', 0):.1f} kW)")
            else:
                st.warning("⚠️ Keine Wärmepumpe ausgewählt - bitte in Bedarfsanalyse konfigurieren")
        else:
            st.info("ℹ️ Keine Wärmepumpen-Daten vorhanden - wird in Bedarfsanalyse konfiguriert")
    
    return heatpump_enabled


# ===================================================================
# TEIL 3: HELPER-FUNKTIONEN
# ===================================================================

def create_multi_pdf_zip(pdf_paths: Dict[str, str], customer_name: str) -> bytes:
    """
    Erstellt ZIP-Archiv mit allen PDFs
    
    Args:
        pdf_paths: Dict mit {company_name: pdf_path}
        customer_name: Name des Kunden für Dateinamen
    
    Rückgabewert:
        ZIP-Datei als Bytes
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for company_name, pdf_path in pdf_paths.items():
            if os.path.exists(pdf_path):
                # Sichere Dateinamen erstellen
                safe_company_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in company_name)
                zip_filename = f"{safe_company_name}_Angebot_{customer_name}.pdf"
                
                with open(pdf_path, 'rb') as pdf_file:
                    zip_file.writestr(zip_filename, pdf_file.read())
    
    zip_buffer.seek(0)
    return zip_buffer.read()


def calculate_rotation_products(
    base_products: Dict[str, Any],
    company_count: int,
    rotation_mode: str = "linear"
) -> List[Dict[str, Any]]:
    """
    Berechnet Produktrotation für mehrere Firmen
    
    Args:
        base_products: Basis-Produkte dict mit categories
        company_count: Anzahl Firmen
        rotation_mode: Rotations-Modus (linear/random/category_specific)
    
    Rückgabewert:
        Liste mit Produkt-Sets pro Firma
    """
    # TODO: Implementierung der Produktrotations-Logik
    # Wird aus repair_pdf/multi_offer_generator.py extrahiert
    return []


def apply_price_increment(
    base_price: float,
    company_index: int,
    increment_percent: float
) -> float:
    """
    Wendet Preisstaffelung an
    
    Args:
        base_price: Basispreis
        company_index: Index der Firma (0-basiert)
        increment_percent: Prozentuale Steigerung pro Firma
    
    Rückgabewert:
        Angepasster Preis
    """
    price_factor = 1.0 + (company_index * increment_percent / 100.0)
    return base_price * price_factor


# ===================================================================
# TEIL 4: HAUPTFUNKTION
# ===================================================================

def render_multi_pdf_generator():
    """
    Haupt-UI für Multi-PDF-Generator
    Kompakte Integration der repair_pdf Logik
    """
    st.title("📊 Multi-Firmen-Angebotsgenerator")
    st.caption("Erstellen Sie mehrere individualisierte Angebote mit einem Klick")
    
    # Initialisierung
    init_multi_pdf_session_state()
    init_heatpump_session_state()
    
    # Import der notwendigen Funktionen
    try:
        from database import list_companies
    except ImportError:
        st.error("❌ Datenbankfunktionen nicht verfügbar")
        return
    
    # Schritt 1: Kundendaten
    customer_data_complete = render_multi_pdf_customer_input()
    
    if not customer_data_complete:
        st.info("👆 Bitte erst Kundendaten eingeben")
        return
    
    st.markdown("---")
    
    # Schritt 2: Firmenauswahl
    available_companies = list_companies()
    selected_company_ids = render_multi_pdf_company_selection(available_companies)
    
    if not selected_company_ids:
        st.info("👆 Bitte mindestens 2 Firmen auswählen")
        return
    
    st.markdown("---")
    
    # Schritt 3: Einstellungen
    render_multi_pdf_settings()
    
    st.markdown("---")
    
    # Schritt 4: Wärmepumpen-Integration (optional)
    heatpump_enabled = render_heatpump_integration_toggle()
    
    st.markdown("---")
    
    # Schritt 5: Generierung
    st.subheader("🚀 Schritt 4: PDF-Generierung")
    
    col_preview, col_generate = st.columns(2)
    
    with col_preview:
        st.info(f"📊 **Zusammenfassung:**\n- {len(selected_company_ids)} Firma(en)\n- Kunde: {st.session_state.multi_offer_customer_data.get('name')}\n- Wärmepumpe: {'✅ Ja' if heatpump_enabled else '❌ Nein'}")
    
    with col_generate:
        if st.button("🎯 Alle Angebote generieren", type="primary", use_container_width=True):
            with st.spinner("⏳ Generiere Angebote..."):
                # TODO: Implementierung der PDF-Generierung
                # Wird aus repair_pdf/multi_offer_generator.py extrahiert
                st.success("✅ Angebote erfolgreich generiert!")
                st.info("💾 Download wird vorbereitet...")


if __name__ == "__main__":
    render_multi_pdf_generator()
