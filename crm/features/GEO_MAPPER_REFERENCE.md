# GeoMapper - API-Referenz

## Klasse: GeoMapper

Hauptklasse für Geo-Mapping und Routenplanung.

### Konstruktor

```python
GeoMapper(db_path: str)
```

**Parameter:**
- `db_path` (str): Pfad zur SQLite-Datenbank

**Beispiel:**
```python
from crm.features.geo_mapper import GeoMapper

mapper = GeoMapper('data/app_data.db')
```

---

## Geocoding-Methoden

### geocode_address()

Geocodiert eine Adresse zu Koordinaten.

```python
geocode_address(address: str, city: str, zip_code: str) -> Optional[Tuple[float, float]]
```

**Parameter:**
- `address` (str): Straße und Hausnummer
- `city` (str): Stadt
- `zip_code` (str): Postleitzahl

**Rückgabe:**
- `Tuple[float, float]`: (latitude, longitude) oder None bei Fehler

**Beispiel:**
```python
coords = mapper.geocode_address("Hauptstraße 1", "Berlin", "10115")
if coords:
    lat, lon = coords
    print(f"Koordinaten: {lat}, {lon}")
```

**Requirement:** 16.1

---

### update_customer_coordinates()

Aktualisiert die Koordinaten eines Kunden in der Datenbank.

```python
update_customer_coordinates(customer_id: int) -> bool
```

**Parameter:**
- `customer_id` (int): ID des Kunden

**Rückgabe:**
- `bool`: True bei Erfolg, False bei Fehler

**Beispiel:**
```python
success = mapper.update_customer_coordinates(1)
if success:
    print("Kunde erfolgreich geocodiert")
```

**Requirement:** 16.1

---

### geocode_all_customers()

Geocodiert alle Kunden ohne Koordinaten.

```python
geocode_all_customers(force_update: bool = False) -> Dict[str, int]
```

**Parameter:**
- `force_update` (bool): Wenn True, werden auch bereits geocodierte Kunden aktualisiert

**Rückgabe:**
- `Dict[str, int]`: Statistiken mit Keys 'success', 'failed', 'skipped'

**Beispiel:**
```python
stats = mapper.geocode_all_customers()
print(f"Erfolgreich: {stats['success']}")
print(f"Fehlgeschlagen: {stats['failed']}")
print(f"Übersprungen: {stats['skipped']}")
```

**Requirement:** 16.1

---

## Karten-Methoden

### get_customers_with_coordinates()

Ruft alle Kunden mit Koordinaten ab.

```python
get_customers_with_coordinates(filter_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]
```

**Parameter:**
- `filter_params` (dict, optional): Filter-Parameter (z.B. {'city': 'Berlin'})

**Rückgabe:**
- `List[Dict]`: Liste von Kunden-Dictionaries

**Beispiel:**
```python
# Alle Kunden
customers = mapper.get_customers_with_coordinates()

# Nur Kunden in Berlin
customers = mapper.get_customers_with_coordinates({'city': 'Berlin'})

# Nur Kunden mit PLZ 10115
customers = mapper.get_customers_with_coordinates({'zip_code': '10115'})
```

**Requirement:** 16.2

---

### create_map()

Erstellt eine Folium-Karte mit Kunden-Markern.

```python
create_map(customers: List[Dict[str, Any]], center: Optional[Tuple[float, float]] = None) -> Optional[Any]
```

**Parameter:**
- `customers` (list): Liste von Kunden mit Koordinaten
- `center` (tuple, optional): Zentrum der Karte (lat, lon)

**Rückgabe:**
- `folium.Map`: Folium Map-Objekt oder None bei Fehler

**Beispiel:**
```python
customers = mapper.get_customers_with_coordinates()
customer_map = mapper.create_map(customers)

# Karte speichern
customer_map.save('kunden_karte.html')

# Oder in Streamlit anzeigen
from streamlit_folium import st_folium
st_folium(customer_map, width=1000, height=600)
```

**Requirement:** 16.2, 16.3

---

## Routen-Methoden

### calculate_distance()

Berechnet die Entfernung zwischen zwei Koordinaten (Haversine-Formel).

```python
calculate_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float
```

**Parameter:**
- `coord1` (tuple): (latitude, longitude) des ersten Punkts
- `coord2` (tuple): (latitude, longitude) des zweiten Punkts

**Rückgabe:**
- `float`: Entfernung in Kilometern

**Beispiel:**
```python
berlin = (52.5200, 13.4050)
munich = (48.1351, 11.5820)

distance = mapper.calculate_distance(berlin, munich)
print(f"Entfernung: {distance:.2f} km")  # ca. 585 km
```

**Requirement:** 16.4

---

### optimize_route()

Optimiert eine Route für mehrere Kunden (Nearest Neighbor Algorithmus).

```python
optimize_route(customer_ids: List[int], start_location: Optional[Tuple[float, float]] = None) -> List[Dict[str, Any]]
```

**Parameter:**
- `customer_ids` (list): Liste von Kunden-IDs
- `start_location` (tuple, optional): Startpunkt (lat, lon)

**Rückgabe:**
- `List[Dict]`: Liste von Kunden in optimierter Reihenfolge mit Entfernungen

**Beispiel:**
```python
# Route für 5 Kunden
customer_ids = [1, 5, 12, 8, 3]
route = mapper.optimize_route(customer_ids)

# Routendetails
for i, stop in enumerate(route):
    print(f"Stopp {i+1}: {stop['name']}")
    print(f"  Entfernung: {stop['distance_km']} km")
    print(f"  Gesamt: {stop['cumulative_distance_km']} km")

# Gesamtstrecke
total = route[-1]['cumulative_distance_km']
print(f"Gesamtstrecke: {total} km")
```

**Requirement:** 16.4

---

### create_route_map()

Erstellt eine Karte mit optimierter Route.

```python
create_route_map(route: List[Dict[str, Any]]) -> Optional[Any]
```

**Parameter:**
- `route` (list): Optimierte Route von optimize_route()

**Rückgabe:**
- `folium.Map`: Folium Map-Objekt oder None bei Fehler

**Beispiel:**
```python
route = mapper.optimize_route([1, 5, 12, 8, 3])
route_map = mapper.create_route_map(route)

# Karte speichern
route_map.save('route.html')
```

**Requirement:** 16.4

---

## Kalender-Methoden

### export_route_to_calendar()

Exportiert eine Route als Kalender-Termine.

```python
export_route_to_calendar(
    route: List[Dict[str, Any]], 
    start_date: datetime, 
    duration_per_stop_minutes: int = 60
) -> List[Dict[str, Any]]
```

**Parameter:**
- `route` (list): Optimierte Route
- `start_date` (datetime): Startdatum und -zeit
- `duration_per_stop_minutes` (int): Dauer pro Stopp in Minuten (default: 60)

**Rückgabe:**
- `List[Dict]`: Liste von Termin-Dictionaries

**Beispiel:**
```python
from datetime import datetime

route = mapper.optimize_route([1, 5, 12])
start_date = datetime(2024, 6, 15, 9, 0)  # 15. Juni 2024, 9:00 Uhr

appointments = mapper.export_route_to_calendar(
    route,
    start_date,
    duration_per_stop_minutes=60
)

# Termine anzeigen
for apt in appointments:
    print(f"{apt['title']}")
    print(f"  Start: {apt['start_time']}")
    print(f"  Ende: {apt['end_time']}")
    print(f"  Ort: {apt['location']}")
```

**Requirement:** 16.5

---

### save_appointments_to_db()

Speichert Termine in der Datenbank.

```python
save_appointments_to_db(appointments: List[Dict[str, Any]]) -> int
```

**Parameter:**
- `appointments` (list): Liste von Termin-Dictionaries

**Rückgabe:**
- `int`: Anzahl der gespeicherten Termine

**Beispiel:**
```python
appointments = mapper.export_route_to_calendar(route, start_date, 60)
saved_count = mapper.save_appointments_to_db(appointments)

print(f"{saved_count} Termine gespeichert")
```

**Requirement:** 16.5

---

## Hilfsfunktionen

### ensure_geo_columns()

Stellt sicher, dass die Geo-Spalten in der customers-Tabelle existieren.

```python
ensure_geo_columns() -> bool
```

**Rückgabe:**
- `bool`: True bei Erfolg, False bei Fehler

**Beispiel:**
```python
from crm.features.geo_mapper import ensure_geo_columns

success = ensure_geo_columns()
if success:
    print("Geo-Spalten erfolgreich hinzugefügt")
```

**Requirement:** 16.1

---

### geocode_customer()

Geocodiert einen einzelnen Kunden (Convenience-Funktion).

```python
geocode_customer(customer_id: int, db_path: str = None) -> bool
```

**Parameter:**
- `customer_id` (int): ID des Kunden
- `db_path` (str, optional): Pfad zur Datenbank

**Rückgabe:**
- `bool`: True bei Erfolg, False bei Fehler

**Beispiel:**
```python
from crm.features.geo_mapper import geocode_customer

success = geocode_customer(1)
```

---

### get_customer_map()

Erstellt eine Karte mit allen Kunden (Convenience-Funktion).

```python
get_customer_map(filter_params: Optional[Dict[str, Any]] = None, db_path: str = None) -> Optional[Any]
```

**Parameter:**
- `filter_params` (dict, optional): Filter-Parameter
- `db_path` (str, optional): Pfad zur Datenbank

**Rückgabe:**
- `folium.Map`: Folium Map-Objekt oder None

**Beispiel:**
```python
from crm.features.geo_mapper import get_customer_map

customer_map = get_customer_map({'city': 'Berlin'})
customer_map.save('berlin_kunden.html')
```

---

### plan_route()

Plant eine optimierte Route (Convenience-Funktion).

```python
plan_route(
    customer_ids: List[int], 
    start_date: datetime = None, 
    db_path: str = None
) -> Tuple[List[Dict[str, Any]], Optional[Any]]
```

**Parameter:**
- `customer_ids` (list): Liste von Kunden-IDs
- `start_date` (datetime, optional): Startdatum
- `db_path` (str, optional): Pfad zur Datenbank

**Rückgabe:**
- `Tuple`: (route, map)

**Beispiel:**
```python
from crm.features.geo_mapper import plan_route
from datetime import datetime

route, route_map = plan_route(
    [1, 5, 12],
    start_date=datetime(2024, 6, 15, 9, 0)
)

if route_map:
    route_map.save('route.html')
```

---

## Datenstrukturen

### Kunden-Dictionary

```python
{
    'id': 1,
    'name': 'Max Mustermann',
    'company': 'Solar GmbH',
    'address': 'Hauptstraße 1',
    'city': 'Berlin',
    'zip_code': '10115',
    'email': 'max@example.com',
    'phone': '0171234567',
    'latitude': 52.5200,
    'longitude': 13.4050
}
```

### Routen-Stopp-Dictionary

```python
{
    'id': 1,
    'name': 'Max Mustermann',
    'company': 'Solar GmbH',
    'address': 'Hauptstraße 1',
    'city': 'Berlin',
    'zip_code': '10115',
    'latitude': 52.5200,
    'longitude': 13.4050,
    'distance_km': 5.2,              # Entfernung vom vorherigen Stopp
    'cumulative_distance_km': 15.8   # Gesamtstrecke bis hier
}
```

### Termin-Dictionary

```python
{
    'customer_id': 1,
    'title': 'Kundenbesuch: Max Mustermann',
    'description': 'Routenplanung - Stopp 1\n\nAdresse: Hauptstraße 1, 10115 Berlin',
    'start_time': '2024-06-15T09:00:00',
    'end_time': '2024-06-15T10:00:00',
    'location': 'Hauptstraße 1, 10115 Berlin',
    'appointment_type': 'customer_visit'
}
```

---

## Konstanten

### GEOCODING_AVAILABLE

```python
GEOCODING_AVAILABLE: bool
```

Gibt an, ob Geocoding verfügbar ist (geopy installiert).

**Beispiel:**
```python
from crm.features.geo_mapper import GEOCODING_AVAILABLE

if not GEOCODING_AVAILABLE:
    print("Bitte installieren Sie geopy: pip install geopy")
```

---

### FOLIUM_AVAILABLE

```python
FOLIUM_AVAILABLE: bool
```

Gibt an, ob Folium verfügbar ist (folium installiert).

**Beispiel:**
```python
from crm.features.geo_mapper import FOLIUM_AVAILABLE

if not FOLIUM_AVAILABLE:
    print("Bitte installieren Sie folium: pip install folium")
```

---

## Fehlerbehandlung

Alle Methoden behandeln Fehler intern und geben entsprechende Werte zurück:

- Geocoding-Fehler: `None` oder `False`
- Datenbank-Fehler: Rollback und Fehlermeldung
- Leere Eingaben: Leere Listen oder `None`

**Beispiel:**
```python
# Geocoding mit Fehlerbehandlung
coords = mapper.geocode_address("Ungültige Adresse", "Stadt", "12345")
if coords is None:
    print("Geocoding fehlgeschlagen")
else:
    print(f"Koordinaten: {coords}")

# Route mit Fehlerbehandlung
route = mapper.optimize_route([])
if not route:
    print("Keine Route berechnet (leere Eingabe)")
```

---

## Performance-Tipps

1. **Batch-Geocoding**: Verwenden Sie `geocode_all_customers()` statt einzelner Aufrufe
2. **Caching**: Geocodierte Koordinaten werden in DB gespeichert
3. **Rate-Limiting**: Nominatim hat 1 Request/Sekunde Limit
4. **Marker-Cluster**: Automatisch bei >20 Kunden aktiviert
5. **Offline-Karten**: Speichern Sie Karten als HTML für Offline-Nutzung

---

## Beispiele

Siehe `docs/GEO_MAPPING_QUICK_REFERENCE.md` für vollständige Beispiele und Workflows.
