# Geo-Mapping & Routenplanung - Quick Reference

## Übersicht

Das Geo-Mapping-System ermöglicht die Visualisierung von Kunden auf Karten und die Planung optimierter Routen für Außendienstbesuche.

## Hauptfunktionen

### 1. Geocoding (Adresse → Koordinaten)

```python
from crm.features.geo_mapper import GeoMapper

mapper = GeoMapper(db_path)

# Einzelnen Kunden geocodieren
success = mapper.update_customer_coordinates(customer_id=1)

# Alle Kunden geocodieren
stats = mapper.geocode_all_customers(force_update=False)
print(f"Erfolgreich: {stats['success']}, Fehlgeschlagen: {stats['failed']}")
```

### 2. Kunden auf Karte anzeigen

```python
# Kunden mit Koordinaten abrufen
customers = mapper.get_customers_with_coordinates()

# Optional: Nach Stadt filtern
customers = mapper.get_customers_with_coordinates({'city': 'Berlin'})

# Karte erstellen
customer_map = mapper.create_map(customers)

# Karte speichern
customer_map.save('kunden_karte.html')
```

### 3. Routenplanung

```python
# Route für mehrere Kunden optimieren
customer_ids = [1, 5, 12, 8, 3]
route = mapper.optimize_route(customer_ids)

# Routenkarte erstellen
route_map = mapper.create_route_map(route)

# Routendetails anzeigen
for i, stop in enumerate(route):
    print(f"Stopp {i+1}: {stop['name']}")
    print(f"  Entfernung: {stop['distance_km']} km")
    print(f"  Gesamt: {stop['cumulative_distance_km']} km")
```

### 4. Kalender-Export

```python
from datetime import datetime

# Termine aus Route generieren
start_date = datetime(2024, 6, 15, 9, 0)  # 15. Juni 2024, 9:00 Uhr
appointments = mapper.export_route_to_calendar(
    route,
    start_date,
    duration_per_stop_minutes=60
)

# Termine in Datenbank speichern
saved_count = mapper.save_appointments_to_db(appointments)
print(f"{saved_count} Termine gespeichert")
```

## UI-Integration

### In CRM-Dashboard einbinden

```python
from crm.features.geo_ui import show_geo_mapping_ui

# In Streamlit-App
show_geo_mapping_ui(db_path)
```

### Kunden-Widget im Profil

```python
from crm.features.geo_ui import show_customer_location_widget

# Im Kundenprofil
show_customer_location_widget(customer_id, db_path)
```

## Hilfsfunktionen

### Entfernung berechnen

```python
# Entfernung zwischen zwei Koordinaten (in km)
distance = mapper.calculate_distance(
    (52.5200, 13.4050),  # Berlin
    (48.1351, 11.5820)   # München
)
print(f"Entfernung: {distance:.2f} km")
```

### Geo-Spalten sicherstellen

```python
from crm.features.geo_mapper import ensure_geo_columns

# Fügt latitude, longitude, geocoded_at zur customers-Tabelle hinzu
ensure_geo_columns()
```

## Installation

### Erforderliche Pakete

```bash
pip install geopy folium streamlit-folium
```

### Datenbank-Migration

Die Geo-Spalten werden automatisch hinzugefügt beim ersten Aufruf von `ensure_geo_columns()`.

## Tipps & Best Practices

### Geocoding

- **Rate Limiting**: Nominatim (OpenStreetMap) hat ein Rate-Limit von 1 Request/Sekunde
- **Batch-Geocoding**: Verwenden Sie `geocode_all_customers()` für viele Kunden
- **Fehlerbehandlung**: Nicht alle Adressen können geocodiert werden (unvollständige Daten)

### Routenplanung

- **Algorithmus**: Verwendet Nearest Neighbor (nicht optimal, aber schnell)
- **Startpunkt**: Kann optional angegeben werden, sonst wird erster Kunde verwendet
- **Fahrzeit**: Wird mit 10 Minuten pro km geschätzt (anpassbar)

### Performance

- **Marker-Cluster**: Bei >20 Kunden wird automatisch Clustering verwendet
- **Caching**: Geocodierte Koordinaten werden in DB gespeichert
- **Offline**: Karten können als HTML gespeichert und offline genutzt werden

## Fehlerbehebung

### Geocoding funktioniert nicht

```python
# Prüfen, ob geopy installiert ist
from crm.features.geo_mapper import GEOCODING_AVAILABLE
print(f"Geocoding verfügbar: {GEOCODING_AVAILABLE}")

# Falls False:
# pip install geopy
```

### Karten werden nicht angezeigt

```python
# Prüfen, ob folium installiert ist
from crm.features.geo_mapper import FOLIUM_AVAILABLE
print(f"Folium verfügbar: {FOLIUM_AVAILABLE}")

# Falls False:
# pip install folium streamlit-folium
```

### Adresse wird nicht gefunden

- Prüfen Sie, ob Adresse, Stadt und PLZ vollständig sind
- Versuchen Sie manuelle Koordinaten-Eingabe
- Nutzen Sie alternative Geocoding-Services (Google Maps API)

## Beispiel-Workflow

```python
from crm.features.geo_mapper import GeoMapper
from datetime import datetime

# 1. GeoMapper initialisieren
mapper = GeoMapper('data/app_data.db')

# 2. Alle Kunden geocodieren
print("Geocodiere Kunden...")
stats = mapper.geocode_all_customers()
print(f"✅ {stats['success']} Kunden geocodiert")

# 3. Kunden für Route auswählen
customer_ids = [1, 5, 12, 8, 3]

# 4. Route optimieren
print("Optimiere Route...")
route = mapper.optimize_route(customer_ids)
print(f"✅ Route: {route[-1]['cumulative_distance_km']:.2f} km")

# 5. Routenkarte erstellen
route_map = mapper.create_route_map(route)
route_map.save('route.html')
print("✅ Karte gespeichert: route.html")

# 6. Termine generieren
start_date = datetime(2024, 6, 15, 9, 0)
appointments = mapper.export_route_to_calendar(route, start_date, 60)

# 7. Termine speichern
saved = mapper.save_appointments_to_db(appointments)
print(f"✅ {saved} Termine im Kalender gespeichert")
```

## API-Referenz

Siehe `crm/features/GEO_MAPPER_REFERENCE.md` für vollständige API-Dokumentation.

## Support

Bei Fragen oder Problemen:
- Prüfen Sie die Logs auf Fehlermeldungen
- Testen Sie mit `test_geo_mapper.py`
- Kontaktieren Sie den Support
