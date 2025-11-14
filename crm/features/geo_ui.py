"""
CRM Geo-Mapping UI

Streamlit-Benutzeroberfläche für Geo-Mapping und Routenplanung

Anforderungen: 16.1, 16.2, 16.3, 16.4, 16.5
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os

try:
    from crm.features.geo_mapper import (
        GeoMapper, ensure_geo_columns,
        GEOCODING_AVAILABLE, FOLIUM_AVAILABLE
    )
except ImportError:
    from geo_mapper import (
        GeoMapper, ensure_geo_columns,
        GEOCODING_AVAILABLE, FOLIUM_AVAILABLE
    )

try:
    from streamlit_folium import st_folium
    STREAMLIT_FOLIUM_AVAILABLE = True
except ImportError:
    STREAMLIT_FOLIUM_AVAILABLE = False
    print("WARNUNG: streamlit-folium nicht installiert")
    print("Installieren Sie mit: pip install streamlit-folium")


def show_geo_mapping_ui(db_path: str):
    """
    Hauptfunktion für die Geo-Mapping UI
    
    Args:
        db_path: Pfad zur Datenbank
        
    Requirement: 16.1, 16.2, 16.3, 16.4, 16.5
    """
    st.title("🗺️ Geo-Mapping & Routenplanung")
    
    # Prüfen, ob erforderliche Bibliotheken installiert sind
    if not GEOCODING_AVAILABLE:
        st.error("[WARNING] Geocoding nicht verfügbar. Bitte installieren Sie: `pip install geopy`")
        return
    
    if not FOLIUM_AVAILABLE:
        st.error("[WARNING] Kartenvisualisierung nicht verfügbar. Bitte installieren Sie: `pip install folium`")
        return
    
    if not STREAMLIT_FOLIUM_AVAILABLE:
        st.warning("[WARNING] Streamlit-Folium nicht installiert. Karten können nicht angezeigt werden.")
        st.info("Installieren Sie mit: `pip install streamlit-folium`")
    
    # Geo-Spalten sicherstellen
    ensure_geo_columns()
    
    # GeoMapper initialisieren
    mapper = GeoMapper(db_path)
    
    # Tab-Navigation
    tab1, tab2, tab3, tab4 = st.tabs([
        "📍 Kunden-Karte",
        "🔄 Geocoding",
        "🚗 Routenplanung",
        "[CHART] Statistiken"
    ])
    
    with tab1:
        show_customer_map_tab(mapper)
    
    with tab2:
        show_geocoding_tab(mapper)
    
    with tab3:
        show_route_planning_tab(mapper)
    
    with tab4:
        show_statistics_tab(mapper)


def show_customer_map_tab(mapper: GeoMapper):
    """
    Tab für Kunden-Karte
    
    Requirement: 16.2, 16.3
    """
    st.header("Kunden auf der Karte")
    
    # Filter
    col1, col2 = st.columns(2)
    
    with col1:
        filter_city = st.text_input("Stadt filtern (optional)", key="map_filter_city")
    
    with col2:
        filter_zip = st.text_input("PLZ filtern (optional)", key="map_filter_zip")
    
    # Filter-Parameter zusammenstellen
    filter_params = {}
    if filter_city:
        filter_params['city'] = filter_city
    if filter_zip:
        filter_params['zip_code'] = filter_zip
    
    # Kunden abrufen
    customers = mapper.get_customers_with_coordinates(filter_params)
    
    if not customers:
        st.info("[INFO] Keine Kunden mit Koordinaten gefunden. Führen Sie zuerst das Geocoding durch.")
        return
    
    st.success(f"[OK] {len(customers)} Kunden mit Koordinaten gefunden")
    
    # Karte erstellen
    customer_map = mapper.create_map(customers)
    
    if customer_map and STREAMLIT_FOLIUM_AVAILABLE:
        # Karte anzeigen
        st_folium(customer_map, width=1000, height=600)
    elif customer_map:
        # Karte als HTML speichern und Link anzeigen
        map_path = "temp_customer_map.html"
        customer_map.save(map_path)
        st.success(f"Karte wurde gespeichert: {map_path}")
        st.info("Öffnen Sie die Datei in Ihrem Browser, um die Karte anzuzeigen.")
    
    # Kundenliste anzeigen
    with st.expander("📋 Kundenliste anzeigen"):
        for i, customer in enumerate(customers, 1):
            st.write(f"**{i}. {customer['name']}**")
            if customer['company']:
                st.write(f"   Firma: {customer['company']}")
            st.write(f"   📍 {customer['address']}, {customer['zip_code']} {customer['city']}")
            if customer['email']:
                st.write(f"   📧 {customer['email']}")
            if customer['phone']:
                st.write(f"   📞 {customer['phone']}")
            st.write(f"   🌍 Koordinaten: {customer['latitude']:.6f}, {customer['longitude']:.6f}")
            st.divider()


def show_geocoding_tab(mapper: GeoMapper):
    """
    Tab für Geocoding
    
    Requirement: 16.1
    """
    st.header("Geocoding von Kundenadressen")
    
    st.info("""
    **Was ist Geocoding?**
    
    Geocoding wandelt Adressen in geografische Koordinaten (Breitengrad, Längengrad) um.
    Dies ermöglicht die Darstellung auf Karten und die Routenplanung.
    """)
    
    # Statistiken abrufen
    conn = mapper._get_connection()
    try:
        cursor = conn.cursor()
        
        # Gesamt-Kunden
        cursor.execute("SELECT COUNT(*) FROM customers WHERE city IS NOT NULL")
        total_customers = cursor.fetchone()[0]
        
        # Geocodierte Kunden
        cursor.execute("""
            SELECT COUNT(*) FROM customers 
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """)
        geocoded_customers = cursor.fetchone()[0]
        
        # Nicht geocodierte Kunden
        not_geocoded = total_customers - geocoded_customers
        
    finally:
        conn.close()
    
    # Statistiken anzeigen
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Gesamt-Kunden", total_customers)
    
    with col2:
        st.metric("Geocodiert", geocoded_customers)
    
    with col3:
        st.metric("Noch zu geocodieren", not_geocoded)
    
    st.divider()
    
    # Geocoding-Optionen
    st.subheader("Geocoding durchführen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Alle nicht-geocodierten Kunden geocodieren", type="primary"):
            with st.spinner("Geocoding läuft..."):
                stats = mapper.geocode_all_customers(force_update=False)
                
                st.success(f"""
                [OK] Geocoding abgeschlossen!
                
                - Erfolgreich: {stats['success']}
                - Fehlgeschlagen: {stats['failed']}
                - Übersprungen: {stats['skipped']}
                """)
    
    with col2:
        if st.button("🔄 Alle Kunden neu geocodieren"):
            if st.checkbox("Ich bestätige, dass alle Kunden neu geocodiert werden sollen"):
                with st.spinner("Geocoding läuft..."):
                    stats = mapper.geocode_all_customers(force_update=True)
                    
                    st.success(f"""
                    [OK] Geocoding abgeschlossen!
                    
                    - Erfolgreich: {stats['success']}
                    - Fehlgeschlagen: {stats['failed']}
                    """)
    
    st.divider()
    
    # Einzelnen Kunden geocodieren
    st.subheader("Einzelnen Kunden geocodieren")
    
    # Kunden-Auswahl
    conn = mapper._get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, first_name, last_name, city, latitude, longitude
            FROM customers
            WHERE city IS NOT NULL
            ORDER BY last_name, first_name
        """)
        
        customers = []
        for row in cursor.fetchall():
            status = "[OK]" if row['latitude'] and row['longitude'] else "[ERROR]"
            customers.append({
                'id': row['id'],
                'label': f"{status} {row['first_name']} {row['last_name']} ({row['city']})",
                'geocoded': bool(row['latitude'] and row['longitude'])
            })
    finally:
        conn.close()
    
    if customers:
        selected_customer = st.selectbox(
            "Kunde auswählen",
            options=customers,
            format_func=lambda x: x['label'],
            key="geocode_single_customer"
        )
        
        if st.button("📍 Diesen Kunden geocodieren"):
            with st.spinner("Geocoding..."):
                success = mapper.update_customer_coordinates(selected_customer['id'])
                
                if success:
                    st.success("[OK] Kunde erfolgreich geocodiert!")
                    st.rerun()
                else:
                    st.error("[ERROR] Geocoding fehlgeschlagen. Prüfen Sie die Adresse.")


def show_route_planning_tab(mapper: GeoMapper):
    """
    Tab für Routenplanung
    
    Requirement: 16.4, 16.5
    """
    st.header("Routenplanung")
    
    st.info("""
    **Routenplanung**
    
    Wählen Sie mehrere Kunden aus und lassen Sie eine optimierte Route berechnen.
    Die Route kann dann als Termine in den Kalender exportiert werden.
    """)
    
    # Kunden mit Koordinaten abrufen
    customers = mapper.get_customers_with_coordinates()
    
    if not customers:
        st.warning("[WARNING] Keine Kunden mit Koordinaten gefunden. Führen Sie zuerst das Geocoding durch.")
        return
    
    # Kunden-Auswahl
    st.subheader("Kunden für Route auswählen")
    
    # Multiselect für Kunden
    customer_options = {
        f"{c['name']} ({c['city']})": c['id'] 
        for c in customers
    }
    
    selected_customer_names = st.multiselect(
        "Kunden auswählen (mindestens 2)",
        options=list(customer_options.keys()),
        key="route_customers"
    )
    
    selected_customer_ids = [customer_options[name] for name in selected_customer_names]
    
    if len(selected_customer_ids) < 2:
        st.info("[INFO] Wählen Sie mindestens 2 Kunden für eine Route aus.")
        return
    
    st.success(f"[OK] {len(selected_customer_ids)} Kunden ausgewählt")
    
    # Route berechnen
    if st.button("🚗 Route optimieren", type="primary"):
        with st.spinner("Route wird berechnet..."):
            route = mapper.optimize_route(selected_customer_ids)
            
            if not route:
                st.error("[ERROR] Routenberechnung fehlgeschlagen")
                return
            
            # Route in Session State speichern
            st.session_state['current_route'] = route
            
            st.success(f"[OK] Route optimiert! Gesamtstrecke: {route[-1]['cumulative_distance_km']} km")
    
    # Route anzeigen, falls vorhanden
    if 'current_route' in st.session_state:
        route = st.session_state['current_route']
        
        st.divider()
        st.subheader("Optimierte Route")
        
        # Routendetails
        total_distance = route[-1]['cumulative_distance_km']
        st.metric("Gesamtstrecke", f"{total_distance} km")
        
        # Routenliste
        with st.expander("📋 Routendetails anzeigen", expanded=True):
            for i, stop in enumerate(route):
                st.write(f"**Stopp {i + 1}: {stop['name']}**")
                if stop['company']:
                    st.write(f"   Firma: {stop['company']}")
                st.write(f"   📍 {stop['address']}, {stop['zip_code']} {stop['city']}")
                if i > 0:
                    st.write(f"   🚗 Entfernung vom vorherigen Stopp: {stop['distance_km']} km")
                st.write(f"   📏 Gesamtstrecke bis hier: {stop['cumulative_distance_km']} km")
                st.divider()
        
        # Karte anzeigen
        route_map = mapper.create_route_map(route)
        
        if route_map and STREAMLIT_FOLIUM_AVAILABLE:
            st.subheader("🗺️ Routenkarte")
            st_folium(route_map, width=1000, height=600)
        elif route_map:
            map_path = "temp_route_map.html"
            route_map.save(map_path)
            st.success(f"Routenkarte wurde gespeichert: {map_path}")
        
        # Kalender-Export
        st.divider()
        st.subheader("📅 Route in Kalender exportieren")
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Startdatum",
                value=datetime.now().date(),
                key="route_start_date"
            )
            start_time = st.time_input(
                "Startzeit",
                value=datetime.now().replace(hour=9, minute=0).time(),
                key="route_start_time"
            )
        
        with col2:
            duration_per_stop = st.number_input(
                "Dauer pro Stopp (Minuten)",
                min_value=15,
                max_value=240,
                value=60,
                step=15,
                key="route_duration"
            )
        
        # Startdatum und -zeit kombinieren
        start_datetime = datetime.combine(start_date, start_time)
        
        # Termine generieren
        appointments = mapper.export_route_to_calendar(
            route,
            start_datetime,
            duration_per_stop
        )
        
        # Termine-Vorschau
        with st.expander("📋 Termine-Vorschau", expanded=True):
            for i, apt in enumerate(appointments, 1):
                start = datetime.fromisoformat(apt['start_time'])
                end = datetime.fromisoformat(apt['end_time'])
                
                st.write(f"**Termin {i}**")
                st.write(f"   {apt['title']}")
                st.write(f"   🕐 {start.strftime('%H:%M')} - {end.strftime('%H:%M')}")
                st.write(f"   📍 {apt['location']}")
                st.divider()
        
        # In Kalender speichern
        if st.button("💾 Termine in Kalender speichern", type="primary"):
            saved_count = mapper.save_appointments_to_db(appointments)
            
            if saved_count > 0:
                st.success(f"[OK] {saved_count} Termine erfolgreich im Kalender gespeichert!")
                st.balloons()
                
                # Route aus Session State entfernen
                del st.session_state['current_route']
            else:
                st.error("[ERROR] Fehler beim Speichern der Termine")


def show_statistics_tab(mapper: GeoMapper):
    """
    Tab für Statistiken
    
    Requirement: 16.2
    """
    st.header("Geo-Mapping Statistiken")
    
    conn = mapper._get_connection()
    try:
        cursor = conn.cursor()
        
        # Gesamt-Statistiken
        cursor.execute("SELECT COUNT(*) FROM customers")
        total_customers = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM customers 
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """)
        geocoded_customers = cursor.fetchone()[0]
        
        # Prozentsatz
        if total_customers > 0:
            geocoded_percent = (geocoded_customers / total_customers) * 100
        else:
            geocoded_percent = 0
        
        # Metriken
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Gesamt-Kunden", total_customers)
        
        with col2:
            st.metric("Geocodiert", geocoded_customers)
        
        with col3:
            st.metric("Geocodiert (%)", f"{geocoded_percent:.1f}%")
        
        st.divider()
        
        # Kunden nach Stadt
        st.subheader("Kunden nach Stadt")
        
        cursor.execute("""
            SELECT 
                city,
                COUNT(*) as total,
                SUM(CASE WHEN latitude IS NOT NULL THEN 1 ELSE 0 END) as geocoded
            FROM customers
            WHERE city IS NOT NULL
            GROUP BY city
            ORDER BY total DESC
            LIMIT 10
        """)
        
        city_stats = cursor.fetchall()
        
        if city_stats:
            for row in city_stats:
                city = row['city']
                total = row['total']
                geocoded = row['geocoded']
                percent = (geocoded / total * 100) if total > 0 else 0
                
                st.write(f"**{city}**: {geocoded}/{total} geocodiert ({percent:.0f}%)")
        else:
            st.info("Keine Daten verfügbar")
        
        st.divider()
        
        # Letzte Geocoding-Aktivitäten
        st.subheader("Letzte Geocoding-Aktivitäten")
        
        cursor.execute("""
            SELECT 
                first_name, last_name, city, geocoded_at
            FROM customers
            WHERE geocoded_at IS NOT NULL
            ORDER BY geocoded_at DESC
            LIMIT 10
        """)
        
        recent_geocoded = cursor.fetchall()
        
        if recent_geocoded:
            for row in recent_geocoded:
                name = f"{row['first_name']} {row['last_name']}"
                city = row['city']
                geocoded_at = row['geocoded_at']
                
                try:
                    dt = datetime.fromisoformat(geocoded_at)
                    time_str = dt.strftime("%d.%m.%Y %H:%M")
                except:
                    time_str = geocoded_at
                
                st.write(f"[OK] **{name}** ({city}) - {time_str}")
        else:
            st.info("Noch keine Geocoding-Aktivitäten")
    
    finally:
        conn.close()


# Hilfsfunktion für Integration in CRM
def show_customer_location_widget(customer_id: int, db_path: str):
    """
    Widget zur Anzeige der Kundenposition (für Kundenprofil)
    
    Args:
        customer_id: ID des Kunden
        db_path: Pfad zur Datenbank
    """
    mapper = GeoMapper(db_path)
    
    conn = mapper._get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT latitude, longitude, geocoded_at
            FROM customers
            WHERE id = ?
        """, (customer_id,))
        
        row = cursor.fetchone()
        
        if row and row['latitude'] and row['longitude']:
            st.success(f"📍 Koordinaten: {row['latitude']:.6f}, {row['longitude']:.6f}")
            
            if row['geocoded_at']:
                try:
                    dt = datetime.fromisoformat(row['geocoded_at'])
                    st.caption(f"Geocodiert am: {dt.strftime('%d.%m.%Y %H:%M')}")
                except:
                    pass
            
            # Mini-Karte anzeigen
            if FOLIUM_AVAILABLE and STREAMLIT_FOLIUM_AVAILABLE:
                import folium
                m = folium.Map(
                    location=[row['latitude'], row['longitude']],
                    zoom_start=15
                )
                folium.Marker(
                    [row['latitude'], row['longitude']],
                    icon=folium.Icon(color='blue', icon='home', prefix='fa')
                ).add_to(m)
                
                st_folium(m, width=400, height=300)
        else:
            st.info("📍 Noch nicht geocodiert")
            
            if st.button("Jetzt geocodieren", key=f"geocode_{customer_id}"):
                with st.spinner("Geocoding..."):
                    success = mapper.update_customer_coordinates(customer_id)
                    
                    if success:
                        st.success("[OK] Erfolgreich geocodiert!")
                        st.rerun()
                    else:
                        st.error("[ERROR] Geocoding fehlgeschlagen")
    
    finally:
        conn.close()
