"""
Admin Wärmepumpen-Produktverwaltung - OPTIMIZED VERSION
Verwendet SQLite statt riesiger Python-Dateien
Memory-Safe mit Pagination und Lazy Loading
"""
import streamlit as st
import pandas as pd
from migrate_heatpump_to_db import HeatpumpDatabaseMigrator


class HeatpumpProductAdmin:
    """Optimierte Wärmepumpen-Verwaltung"""
    
    def __getstate__(self):
        return self.__dict__.copy()
    
    def __setstate__(self, state):
        self.__dict__.update(state)
    
    def __init__(self, db_path: str = "data/app_data.db"):
        self.db = HeatpumpDatabaseMigrator(db_path)
        self.items_per_page = 50


def render_heatpump_admin_ui():
    """Streamlit UI für Wärmepumpen-Produktverwaltung"""
    st.title("🌡️ Wärmepumpen-Produktverwaltung (Optimiert)")
    
    # Session State
    if 'hp_current_page' not in st.session_state:
        st.session_state.hp_current_page = 1
    if 'hp_selected_manufacturer' not in st.session_state:
        st.session_state.hp_selected_manufacturer = None
    if 'hp_selected_type' not in st.session_state:
        st.session_state.hp_selected_type = None
    
    admin = HeatpumpProductAdmin()
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Dashboard", "🔍 Modelle durchsuchen", "🎯 Modell-Finder", "⚙️ Tools"]
    )
    
    # ============ TAB 1: DASHBOARD ============
    with tab1:
        st.subheader("Wärmepumpen-Datenbank Übersicht")
        
        stats = admin.db.export_statistics()
        
        if stats.get('total_models', 0) > 0:
            # Metriken
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🌡️ Gesamt Modelle", f"{stats['total_models']:,}")
            with col2:
                st.metric("🏭 Hersteller", len(stats.get('by_manufacturer', {})))
            with col3:
                st.metric("⭐ Ø SCOP", stats.get('avg_scop', 0.0))
            with col4:
                st.metric("📊 Ø Rating", stats.get('avg_rating', 0.0))
            
            st.divider()
            
            # Nach Hersteller
            st.subheader("Modelle nach Hersteller")
            manufacturer_data = []
            for manufacturer, count in stats.get('by_manufacturer', {}).items():
                manufacturer_data.append({
                    'Hersteller': manufacturer,
                    'Anzahl Modelle': count
                })
            
            if manufacturer_data:
                df_manufacturers = pd.DataFrame(manufacturer_data)
                st.dataframe(df_manufacturers, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # Nach Typ
            st.subheader("Modelle nach Typ")
            type_data = []
            for hp_type, count in stats.get('by_type', {}).items():
                type_data.append({
                    'Typ': hp_type,
                    'Anzahl Modelle': count
                })
            
            if type_data:
                df_types = pd.DataFrame(type_data)
                st.dataframe(df_types, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Keine Wärmepumpen-Daten gefunden!")
            st.info("💡 Führen Sie zuerst die Migration aus: `python migrate_heatpump_to_db.py`")
    
    # ============ TAB 2: MODELLE DURCHSUCHEN ============
    with tab2:
        st.subheader("Wärmepumpen-Modelle durchsuchen")
        
        # Filter
        col1, col2 = st.columns(2)
        
        with col1:
            manufacturers = admin.db.get_manufacturers()
            if manufacturers:
                manufacturer_filter = st.selectbox(
                    "🏭 Hersteller filtern",
                    ["Alle Hersteller"] + manufacturers,
                    key="hp_manufacturer_filter"
                )
                if manufacturer_filter != "Alle Hersteller":
                    st.session_state.hp_selected_manufacturer = manufacturer_filter
                else:
                    st.session_state.hp_selected_manufacturer = None
            else:
                st.info("Keine Hersteller gefunden")
        
        with col2:
            if st.session_state.hp_selected_manufacturer:
                types = admin.db.get_types_by_manufacturer(st.session_state.hp_selected_manufacturer)
                type_filter = st.selectbox(
                    "🌡️ Typ filtern",
                    ["Alle Typen"] + types,
                    key="hp_type_filter"
                )
                if type_filter != "Alle Typen":
                    st.session_state.hp_selected_type = type_filter
                else:
                    st.session_state.hp_selected_type = None
            else:
                st.info("Wählen Sie zuerst einen Hersteller")
                st.session_state.hp_selected_type = None
        
        # Anzahl ermitteln
        total_count = admin.db.get_model_count(
            manufacturer=st.session_state.hp_selected_manufacturer,
            heatpump_type=st.session_state.hp_selected_type
        )
        
        if total_count > 0:
            total_pages = (total_count + admin.items_per_page - 1) // admin.items_per_page
            
            st.write(f"📊 **{total_count} Modelle gefunden** (Seite {st.session_state.hp_current_page} von {total_pages})")
            
            # Modelle laden
            models = admin.db.get_models_paginated(
                page=st.session_state.hp_current_page,
                items_per_page=admin.items_per_page,
                manufacturer=st.session_state.hp_selected_manufacturer,
                heatpump_type=st.session_state.hp_selected_type
            )
            
            if models:
                # Als Tabelle anzeigen
                table_data = []
                for model in models:
                    # Heizleistungen als String
                    powers_str = ", ".join([f"{p} kW" for p in model['heating_power_kw']])
                    
                    table_data.append({
                        'ID': model['id'],
                        'Hersteller': model['manufacturer'],
                        'Typ': model['heatpump_type'],
                        'Modell': model['model'],
                        'Heizleistung': powers_str,
                        'SCOP': model['scop'],
                        'Max. VL-Temp': f"{model['max_flow_temp']}°C",
                        'Preis': model['price_range'],
                        'Rating': f"⭐ {model['rating']}"
                    })
                
                df_models = pd.DataFrame(table_data)
                st.dataframe(df_models, use_container_width=True, hide_index=True, height=400)
                
                # Details expandable
                st.divider()
                st.subheader("Modell-Details")
                
                selected_model_id = st.selectbox(
                    "Modell für Details auswählen",
                    [m['id'] for m in models],
                    format_func=lambda x: next(m['model'] for m in models if m['id'] == x),
                    key="selected_model_detail"
                )
                
                selected_model = next((m for m in models if m['id'] == selected_model_id), None)
                
                if selected_model:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Technische Daten:**")
                        st.write(f"- Hersteller: {selected_model['manufacturer']}")
                        st.write(f"- Typ: {selected_model['heatpump_type']}")
                        st.write(f"- Modell: {selected_model['model']}")
                        st.write(f"- SCOP: {selected_model['scop']}")
                        st.write(f"- Max. Vorlauftemperatur: {selected_model['max_flow_temp']}°C")
                        st.write(f"- Kältemittel: {selected_model['refrigerant']}")
                        st.write(f"- Preisklasse: {selected_model['price_range']}")
                        st.write(f"- Rating: ⭐ {selected_model['rating']}/5")
                    
                    with col2:
                        st.write("**Verfügbare Heizleistungen:**")
                        for power in selected_model['heating_power_kw']:
                            st.write(f"- {power} kW")
                        
                        if selected_model['features']:
                            st.write("\n**Features:**")
                            for feature in selected_model['features']:
                                st.write(f"✓ {feature}")
                        
                        if selected_model['awards']:
                            st.write("\n**Auszeichnungen:**")
                            for award in selected_model['awards']:
                                st.write(f"🏆 {award}")
                
                # Pagination
                col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
                
                with col1:
                    if st.button("⏮️ Erste", disabled=(st.session_state.hp_current_page == 1), key="hp_first"):
                        st.session_state.hp_current_page = 1
                        st.rerun()
                
                with col2:
                    if st.button("◀️ Zurück", disabled=(st.session_state.hp_current_page == 1), key="hp_prev"):
                        st.session_state.hp_current_page -= 1
                        st.rerun()
                
                with col3:
                    jump_page = st.number_input(
                        "Gehe zu Seite:",
                        min_value=1,
                        max_value=total_pages,
                        value=st.session_state.hp_current_page,
                        key="hp_page_jump"
                    )
                    if jump_page != st.session_state.hp_current_page:
                        st.session_state.hp_current_page = jump_page
                        st.rerun()
                
                with col4:
                    if st.button("▶️ Weiter", disabled=(st.session_state.hp_current_page >= total_pages), key="hp_next"):
                        st.session_state.hp_current_page += 1
                        st.rerun()
                
                with col5:
                    if st.button("⏭️ Letzte", disabled=(st.session_state.hp_current_page >= total_pages), key="hp_last"):
                        st.session_state.hp_current_page = total_pages
                        st.rerun()
            else:
                st.warning("Keine Modelle auf dieser Seite.")
        else:
            st.info("ℹ️ Keine Modelle gefunden. Passen Sie die Filter an.")
    
    # ============ TAB 3: MODELL-FINDER ============
    with tab3:
        st.subheader("🎯 Passende Wärmepumpe finden")
        st.write("Finden Sie die ideale Wärmepumpe basierend auf Ihren Anforderungen.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            heating_requirement = st.number_input(
                "Benötigte Heizleistung (kW)",
                min_value=1.0,
                max_value=50.0,
                value=8.0,
                step=0.5,
                key="finder_heating_req"
            )
            
            min_scop = st.slider(
                "Minimaler SCOP-Wert",
                min_value=3.0,
                max_value=5.5,
                value=4.0,
                step=0.1,
                key="finder_min_scop"
            )
        
        with col2:
            manufacturers = admin.db.get_manufacturers()
            finder_manufacturer = st.selectbox(
                "Hersteller (optional)",
                ["Beliebig"] + manufacturers,
                key="finder_manufacturer"
            )
            
            all_types = ["Luft-Wasser-Wärmepumpe", "Sole-Wasser-Wärmepumpe", "Wasser-Wasser-Wärmepumpe"]
            finder_type = st.selectbox(
                "Typ (optional)",
                ["Beliebig"] + all_types,
                key="finder_type"
            )
        
        if st.button("🔍 Passende Modelle suchen", use_container_width=True):
            suitable_models = admin.db.find_suitable_model(
                heating_requirement_kw=heating_requirement,
                heatpump_type=None if finder_type == "Beliebig" else finder_type,
                manufacturer=None if finder_manufacturer == "Beliebig" else finder_manufacturer,
                min_scop=min_scop
            )
            
            if suitable_models:
                st.success(f"✅ {len(suitable_models)} passende Modelle gefunden!")
                
                for idx, model in enumerate(suitable_models, 1):
                    with st.expander(f"#{idx}: {model['manufacturer']} {model['model']} - ⭐ {model['rating']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Typ:** {model['heatpump_type']}")
                            st.write(f"**SCOP:** {model['scop']}")
                            st.write(f"**Max. VL-Temp:** {model['max_flow_temp']}°C")
                            st.write(f"**Kältemittel:** {model['refrigerant']}")
                            st.write(f"**Preis:** {model['price_range']}")
                        
                        with col2:
                            st.write("**Heizleistungen:**")
                            for power in model['heating_power_kw']:
                                if power >= heating_requirement:
                                    st.write(f"✅ {power} kW (passt!)")
                                else:
                                    st.write(f"- {power} kW")
                            
                            if model['features']:
                                st.write("\n**Features:**")
                                for feature in model['features'][:5]:  # Max 5 Features anzeigen
                                    st.write(f"✓ {feature}")
                            
                            if model['awards']:
                                st.write("\n**Auszeichnungen:**")
                                for award in model['awards'][:3]:  # Max 3 Awards
                                    st.write(f"🏆 {award}")
            else:
                st.warning("⚠️ Keine passenden Modelle gefunden. Passen Sie die Kriterien an.")
    
    # ============ TAB 4: TOOLS ============
    with tab4:
        st.subheader("Datenbank-Tools")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🔧 Datenbank-Wartung**")
            
            if st.button("🔄 Tabellen initialisieren"):
                admin.db.create_heatpump_tables()
                st.success("✅ Wärmepumpen-Tabellen erstellt/überprüft!")
            
            if st.button("📊 Statistiken neu berechnen"):
                stats = admin.db.export_statistics()
                st.json(stats)
            
            if st.button("🔄 Session State zurücksetzen"):
                st.session_state.hp_current_page = 1
                st.session_state.hp_selected_manufacturer = None
                st.session_state.hp_selected_type = None
                st.success("✅ Session zurückgesetzt!")
                st.rerun()
        
        with col2:
            st.write("**📥 Migration**")
            st.info("Migration aus `heatpump_products_database.py` durchführen:")
            st.code("python migrate_heatpump_to_db.py", language="bash")
            
            st.warning("⚠️ **Wichtig:** Migration löscht existierende Wärmepumpen-Daten!")
            
            if st.button("⚠️ Migration starten (gefährlich!)", type="secondary"):
                try:
                    from migrate_heatpump_to_db import migrate_heatpump_products_to_db
                    
                    with st.spinner("Migration läuft..."):
                        success = migrate_heatpump_products_to_db()
                    
                    if success:
                        st.success("✅ Migration erfolgreich!")
                        st.rerun()
                    else:
                        st.error("❌ Migration fehlgeschlagen!")
                except ImportError:
                    st.error("❌ heatpump_products_database.py nicht gefunden!")
                except Exception as e:
                    st.error(f"❌ Fehler: {e}")


if __name__ == "__main__":
    render_heatpump_admin_ui()
