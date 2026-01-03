# Geo-Mapping Integration Guide

## Übersicht

Diese Anleitung zeigt, wie das Geo-Mapping-System in die bestehende CRM-Anwendung integriert wird.

## Schritt 1: Installation der Abhängigkeiten

```bash
# Alle erforderlichen Pakete installieren
pip install -r crm/features/geo_requirements.txt

# Oder einzeln:
pip install geopy folium streamlit-folium
```

## Schritt 2: Datenbank-Migration

Die Geo-Spalten werden automatisch hinzugefügt beim ersten Aufruf:

```python
from crm.features.geo_mapper import ensure_geo_columns

# Fügt latitude, longitude, geocoded_at zur customers-Tabelle hinzu
ensure_geo_columns()
```

**Oder manuell in SQL:**

```sql
ALTER TABLE customers ADD COLUMN latitude REAL;
ALTER TABLE customers ADD COLUMN longitude REAL;
ALTER TABLE customers ADD COLUMN geocoded_at TEXT;
```

## Schritt 3: Integration in CRM-Hauptmenü

### Option A: Als separater Menüpunkt

In `crm.py` oder Ihrer Hauptdatei:

```python
import streamlit as st
from crm.features.geo_ui import show_geo_mapping_ui
from database import DB_PATH

# Im Sidebar-Menü
menu_option = st.sidebar.selectbox(
    "Navigation",
    ["Dashboard", "Kunden", "Pipeline", "Kalender", "Geo-Mapping"]
)

if menu_option == "Geo-Mapping":
    show_geo_mapping_ui(DB_PATH)
```

### Option B: Als Tab im CRM

```python
import streamlit as st
from crm.features.geo_ui import show_geo_mapping_ui

# Tabs erstellen
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Dashboard", "Kunden", "Pipeline", "Kalender", "🗺️ Geo-Mapping"
])

with tab5:
    show_geo_mapping_ui(DB_PATH)
```

## Schritt 4: Integration im Kundenprofil

Fügen Sie ein Geo-Widget zum Kundenprofil hinzu:

```python
from crm.features.geo_ui import show_customer_location_widget

def show_customer_profile(customer_id):
    st.header(f"Kundenprofil: {customer_name}")
    
    # ... andere Kundeninformationen ...
    
    # Geo-Widget hinzufügen
    with st.expander("📍 Standort auf Karte", expanded=False):
        show_customer_location_widget(customer_id, DB_PATH)
```

## Schritt 5: Dashboard-Integration

Zeigen Sie Geo-Statistiken im Dashboard:

```python
from crm.features.geo_mapper import GeoMapper

def show_dashboard():
    mapper = GeoMapper(DB_PATH)
    
    # Statistiken abrufen
    customers = mapper.get_customers_with_coordinates()
    
    # Metriken anzeigen
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Geocodierte Kunden", len(customers))
    
    with col2:
        # Karte als Vorschau
        if customers:
            customer_map = mapper.create_map(customers[:10])
            st_folium(customer_map, width=300, height=200)
```

## Schritt 6: Automatisches Geocoding

Geocodieren Sie neue Kunden automatisch beim Speichern:

```python
from crm.features.geo_mapper import geocode_customer

def save_customer(customer_data):
    # Kunde in Datenbank speichern
    customer_id = save_to_database(customer_data)
    
    # Automatisch geocodieren, wenn Adresse vorhanden
    if customer_data.get('address') and customer_data.get('city'):
        geocode_customer(customer_id, DB_PATH)
    
    return customer_id
```

## Schritt 7: Routenplanung-Workflow

Integrieren Sie Routenplanung in den Workflow:

```python
from crm.features.geo_mapper import GeoMapper
from datetime import datetime

def plan_customer_visits(customer_ids, visit_date):
    mapper = GeoMapper(DB_PATH)
    
    # Route optimieren
    route = mapper.optimize_route(customer_ids)
    
    if route:
        # Termine generieren
        appointments = mapper.export_route_to_calendar(
            route,
            visit_date,
            duration_per_stop_minutes=60
        )
        
        # In Kalender speichern
        saved_count = mapper.save_appointments_to_db(appointments)
        
        st.success(f"✅ {saved_count} Termine erstellt!")
        
        # Routenkarte anzeigen
        route_map = mapper.create_route_map(route)
        st_folium(route_map, width=1000, height=600)
```

## Beispiel: Vollständige Integration

Hier ist ein vollständiges Beispiel für die Integration in `crm.py`:

```python
import streamlit as st
from database import DB_PATH
from crm.features.geo_ui import show_geo_mapping_ui, show_customer_location_widget
from crm.features.geo_mapper import GeoMapper, ensure_geo_columns

# Beim Start: Geo-Spalten sicherstellen
ensure_geo_columns()

# Hauptmenü
st.sidebar.title("CRM Navigation")
menu = st.sidebar.radio(
    "Menü",
    ["Dashboard", "Kunden", "Pipeline", "Kalender", "🗺️ Geo-Mapping"]
)

if menu == "🗺️ Geo-Mapping":
    # Geo-Mapping UI anzeigen
    show_geo_mapping_ui(DB_PATH)

elif menu == "Kunden":
    # Kundenliste mit Geo-Info
    st.title("Kundenverwaltung")
    
    # Kunden auswählen
    customer_id = st.selectbox("Kunde auswählen", get_customer_list())
    
    if customer_id:
        # Kundenprofil anzeigen
        show_customer_details(customer_id)
        
        # Geo-Widget hinzufügen
        st.divider()
        st.subheader("📍 Standort")
        show_customer_location_widget(customer_id, DB_PATH)

elif menu == "Dashboard":
    # Dashboard mit Geo-Statistiken
    st.title("CRM Dashboard")
    
    mapper = GeoMapper(DB_PATH)
    customers = mapper.get_customers_with_coordinates()
    
    # Metriken
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Gesamt-Kunden", get_total_customers())
    
    with col2:
        st.metric("Geocodierte Kunden", len(customers))
    
    with col3:
        percent = (len(customers) / get_total_customers() * 100) if get_total_customers() > 0 else 0
        st.metric("Geocodiert (%)", f"{percent:.1f}%")
    
    # Karten-Vorschau
    if customers:
        st.subheader("🗺️ Kunden-Übersicht")
        customer_map = mapper.create_map(customers)
        from streamlit_folium import st_folium
        st_folium(customer_map, width=1000, height=400)
```

## Best Practices

### 1. Fehlerbehandlung

```python
from crm.features.geo_mapper import GEOCODING_AVAILABLE, FOLIUM_AVAILABLE

if not GEOCODING_AVAILABLE:
    st.error("⚠️ Geocoding nicht verfügbar. Bitte installieren Sie: pip install geopy")
    st.stop()

if not FOLIUM_AVAILABLE:
    st.warning("⚠️ Kartenvisualisierung eingeschränkt. Installieren Sie: pip install folium")
```

### 2. Performance

```python
# Geocoding in Batches
@st.cache_data(ttl=3600)  # Cache für 1 Stunde
def get_geocoded_customers():
    mapper = GeoMapper(DB_PATH)
    return mapper.get_customers_with_coordinates()

# Karten cachen
@st.cache_resource
def create_customer_map(customer_ids):
    mapper = GeoMapper(DB_PATH)
    customers = [c for c in get_geocoded_customers() if c['id'] in customer_ids]
    return mapper.create_map(customers)
```

### 3. Benutzer-Feedback

```python
# Geocoding mit Progress-Bar
import streamlit as st

def geocode_all_with_progress():
    mapper = GeoMapper(DB_PATH)
    
    # Kunden ohne Koordinaten zählen
    conn = mapper._get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM customers WHERE latitude IS NULL")
    total = cursor.fetchone()[0]
    conn.close()
    
    if total == 0:
        st.info("✅ Alle Kunden bereits geocodiert")
        return
    
    # Progress-Bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Geocoding durchführen
    stats = mapper.geocode_all_customers()
    
    progress_bar.progress(100)
    status_text.text(f"✅ {stats['success']} Kunden geocodiert")
```

### 4. Sicherheit

```python
# Nur für autorisierte Benutzer
def show_geo_mapping():
    if not st.session_state.get('user_authenticated'):
        st.error("⚠️ Bitte melden Sie sich an")
        return
    
    if not st.session_state.get('user_role') in ['admin', 'manager']:
        st.error("⚠️ Keine Berechtigung für Geo-Mapping")
        return
    
    show_geo_mapping_ui(DB_PATH)
```

## Troubleshooting

### Problem: Geocoding funktioniert nicht

**Lösung:**
```python
# Prüfen, ob geopy installiert ist
try:
    import geopy
    print("✅ geopy installiert")
except ImportError:
    print("❌ geopy nicht installiert")
    print("Installieren Sie mit: pip install geopy")
```

### Problem: Karten werden nicht angezeigt

**Lösung:**
```python
# Prüfen, ob folium und streamlit-folium installiert sind
try:
    import folium
    from streamlit_folium import st_folium
    print("✅ Folium installiert")
except ImportError as e:
    print(f"❌ Fehler: {e}")
    print("Installieren Sie mit: pip install folium streamlit-folium")
```

### Problem: Adresse wird nicht gefunden

**Lösung:**
```python
# Manuelle Koordinaten-Eingabe ermöglichen
def manual_geocode(customer_id):
    st.subheader("Manuelle Koordinaten-Eingabe")
    
    col1, col2 = st.columns(2)
    
    with col1:
        lat = st.number_input("Breitengrad", format="%.6f")
    
    with col2:
        lon = st.number_input("Längengrad", format="%.6f")
    
    if st.button("Koordinaten speichern"):
        # In Datenbank speichern
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE customers 
            SET latitude = ?, longitude = ?, geocoded_at = ?
            WHERE id = ?
        """, (lat, lon, datetime.now().isoformat(), customer_id))
        conn.commit()
        conn.close()
        
        st.success("✅ Koordinaten gespeichert")
```

## Weitere Ressourcen

- **Quick Reference:** `docs/GEO_MAPPING_QUICK_REFERENCE.md`
- **API-Referenz:** `crm/features/GEO_MAPPER_REFERENCE.md`
- **Beispiele:** `crm/features/geo_integration_example.py`
- **Tests:** `crm/features/test_geo_mapper.py`

## Support

Bei Fragen oder Problemen:
1. Prüfen Sie die Dokumentation
2. Führen Sie die Tests aus: `python crm/features/test_geo_mapper.py`
3. Prüfen Sie die Beispiele: `python crm/features/geo_integration_example.py`
4. Kontaktieren Sie den Support
