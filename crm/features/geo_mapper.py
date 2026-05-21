"""
CRM Geo-Mapping und Routenplanung

Dieses Modul bietet Funktionen für:
- Geocoding von Kundenadressen
- Kartenvisualisierung mit Kunden-Markern
- Routenplanung und -optimierung
- Export von Routen für Kalender

Anforderungen: 16.1, 16.2, 16.3, 16.4, 16.5
"""

import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import math

# Geocoding
try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError
    GEOCODING_AVAILABLE = True
except ImportError:
    GEOCODING_AVAILABLE = False
    print("WARNUNG: geopy nicht installiert. Geocoding nicht verfügbar.")
    print("Installieren Sie mit: pip install geopy")

# Mapping
try:
    import folium
    from folium import plugins
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    print("WARNUNG: folium nicht installiert. Kartenvisualisierung nicht verfügbar.")
    print("Installieren Sie mit: pip install folium")


class GeoMapper:
    """Hauptklasse für Geo-Mapping und Routenplanung"""
    
    def __init__(self, db_path: str):
        """
        Initialisiert den GeoMapper
        
        Args:
            db_path: Pfad zur SQLite-Datenbank
        """
        self.db_path = db_path
        self.geocoder = None
        
        if GEOCODING_AVAILABLE:
            # Nominatim Geocoder (OpenStreetMap) - kostenlos
            self.geocoder = Nominatim(user_agent="solar_crm_app")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Erstellt eine Datenbankverbindung"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def geocode_address(self, address: str, city: str, zip_code: str) -> Optional[Tuple[float, float]]:
        """
        Geocodiert eine Adresse zu Koordinaten
        
        Args:
            address: Straße und Hausnummer
            city: Stadt
            zip_code: Postleitzahl
            
        Returns:
            Tuple (latitude, longitude) oder None bei Fehler
            
        Requirement: 16.1
        """
        if not GEOCODING_AVAILABLE or not self.geocoder:
            print("Geocoding nicht verfügbar")
            return None
        
        # Vollständige Adresse zusammenbauen
        full_address = f"{address}, {zip_code} {city}, Germany"
        
        try:
            location = self.geocoder.geocode(full_address, timeout=10)
            if location:
                return (location.latitude, location.longitude)
            else:
                print(f"Adresse nicht gefunden: {full_address}")
                return None
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"Geocoding-Fehler für {full_address}: {e}")
            return None
        except Exception as e:
            print(f"Unerwarteter Fehler beim Geocoding: {e}")
            return None
    
    def update_customer_coordinates(self, customer_id: int) -> bool:
        """
        Aktualisiert die Koordinaten eines Kunden
        
        Args:
            customer_id: ID des Kunden
            
        Returns:
            True bei Erfolg, False bei Fehler
            
        Requirement: 16.1
        """
        conn = self._get_connection()
        try:
            # Kundendaten abrufen
            cursor = conn.cursor()
            cursor.execute("""
                SELECT address, house_number, city, zip_code 
                FROM customers 
                WHERE id = ?
            """, (customer_id))
            
            row = cursor.fetchone()
            if not row:
                print(f"Kunde {customer_id} nicht gefunden")
                return False
            
            # Adresse zusammenbauen
            address = row['address'] or ""
            house_number = row['house_number'] or ""
            full_address = f"{address} {house_number}".strip()
            city = row['city'] or ""
            zip_code = row['zip_code'] or ""
            
            if not full_address or not city:
                print(f"Unvollständige Adresse für Kunde {customer_id}")
                return False
            
            # Geocoding durchführen
            coords = self.geocode_address(full_address, city, zip_code)
            if not coords:
                return False
            
            # Koordinaten in Datenbank speichern
            cursor.execute("""
                UPDATE customers 
                SET latitude = ?, longitude = ?, geocoded_at = ?
                WHERE id = ?
            """, (coords[0], coords[1], datetime.now().isoformat(), customer_id))
            
            conn.commit()
            print(f"Koordinaten für Kunde {customer_id} aktualisiert: {coords}")
            return True
            
        except Exception as e:
            print(f"Fehler beim Aktualisieren der Koordinaten: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def geocode_all_customers(self, force_update: bool = False) -> Dict[str, int]:
        """
        Geocodiert alle Kunden ohne Koordinaten
        
        Args:
            force_update: Wenn True, werden auch bereits geocodierte Kunden aktualisiert
            
        Returns:
            Dictionary mit Statistiken (success, failed, skipped)
            
        Requirement: 16.1
        """
        conn = self._get_connection()
        stats = {"success": 0, "failed": 0, "skipped": 0}
        
        try:
            cursor = conn.cursor()
            
            # Kunden ohne Koordinaten oder alle (bei force_update)
            if force_update:
                cursor.execute("SELECT id FROM customers WHERE city IS NOT NULL")
            else:
                cursor.execute("""
                    SELECT id FROM customers 
                    WHERE city IS NOT NULL 
                    AND (latitude IS NULL OR longitude IS NULL)
                """)
            
            customer_ids = [row['id'] for row in cursor.fetchall()]
            
            print(f"Geocodiere {len(customer_ids)} Kunden...")
            
            for customer_id in customer_ids:
                if self.update_customer_coordinates(customer_id):
                    stats["success"] += 1
                else:
                    stats["failed"] += 1
            
            return stats
            
        except Exception as e:
            print(f"Fehler beim Geocodieren aller Kunden: {e}")
            return stats
        finally:
            conn.close()
    
    def get_customers_with_coordinates(self, filter_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Ruft alle Kunden mit Koordinaten ab
        
        Args:
            filter_params: Optionale Filter (z.B. {'city': 'Berlin'})
            
        Returns:
            Liste von Kunden-Dictionaries
            
        Requirement: 16.2
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    id, first_name, last_name, company_name,
                    address, house_number, city, zip_code,
                    email, phone_mobile, phone_landline,
                    latitude, longitude
                FROM customers
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            """
            
            params = []
            
            # Filter anwenden
            if filter_params:
                if 'city' in filter_params:
                    query += " AND city = ?"
                    params.append(filter_params['city'])
                if 'zip_code' in filter_params:
                    query += " AND zip_code = ?"
                    params.append(filter_params['zip_code'])
            
            query += " ORDER BY last_name, first_name"
            
            cursor.execute(query, params)
            
            customers = []
            for row in cursor.fetchall():
                customers.append({
                    'id': row['id'],
                    'name': f"{row['first_name']} {row['last_name']}".strip(),
                    'company': row['company_name'],
                    'address': f"{row['address']} {row['house_number']}".strip(),
                    'city': row['city'],
                    'zip_code': row['zip_code'],
                    'email': row['email'],
                    'phone': row['phone_mobile'] or row['phone_landline'],
                    'latitude': row['latitude'],
                    'longitude': row['longitude']
                })
            
            return customers
            
        except Exception as e:
            print(f"Fehler beim Abrufen der Kunden: {e}")
            return []
        finally:
            conn.close()
    
    def create_map(self, customers: List[Dict[str, Any]], center: Optional[Tuple[float, float]] = None) -> Optional[Any]:
        """
        Erstellt eine Folium-Karte mit Kunden-Markern
        
        Args:
            customers: Liste von Kunden mit Koordinaten
            center: Zentrum der Karte (lat, lon). Wenn None, wird automatisch berechnet
            
        Returns:
            Folium Map-Objekt oder None bei Fehler
            
        Requirement: 16.2, 16.3
        """
        if not FOLIUM_AVAILABLE:
            print("Folium nicht verfügbar")
            return None
        
        if not customers:
            print("Keine Kunden zum Anzeigen")
            return None
        
        # Zentrum berechnen, falls nicht angegeben
        if center is None:
            avg_lat = sum(c['latitude'] for c in customers) / len(customers)
            avg_lon = sum(c['longitude'] for c in customers) / len(customers)
            center = (avg_lat, avg_lon)
        
        # Karte erstellen
        m = folium.Map(
            location=center,
            zoom_start=10,
            tiles='OpenStreetMap'
        )
        
        # Marker für jeden Kunden hinzufügen
        for customer in customers:
            # Popup-Inhalt erstellen
            popup_html = f"""
            <div style="font-family: Arial; min-width: 200px;">
                <h4 style="margin: 0 0 10px 0;">{customer['name']}</h4>
                {f"<p style='margin: 5px 0;'><b>{customer['company']}</b></p>" if customer['company'] else ""}
                <p style="margin: 5px 0;"> {customer['address']}<br>{customer['zip_code']} {customer['city']}</p>
                {f"<p style='margin: 5px 0;'> {customer['email']}</p>" if customer['email'] else ""}
                {f"<p style='margin: 5px 0;'> {customer['phone']}</p>" if customer['phone'] else ""}
                <p style="margin: 10px 0 0 0;"><a href="#" onclick="alert('Kunde-ID: {customer['id']}')">Details anzeigen</a></p>
            </div>
            """
            
            # Marker hinzufügen
            folium.Marker(
                location=[customer['latitude'], customer['longitude']],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=customer['name'],
                icon=folium.Icon(color='blue', icon='home', prefix='fa')
            ).add_to(m)
        
        # Marker-Cluster hinzufügen für bessere Performance bei vielen Markern
        if len(customers) > 20:
            marker_cluster = plugins.MarkerCluster()
            for customer in customers:
                folium.Marker(
                    location=[customer['latitude'], customer['longitude']],
                    popup=customer['name']
                ).add_to(marker_cluster)
            marker_cluster.add_to(m)
        
        return m
    
    def calculate_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """
        Berechnet die Entfernung zwischen zwei Koordinaten (Haversine-Formel)
        
        Args:
            coord1: (latitude, longitude) des ersten Punkts
            coord2: (latitude, longitude) des zweiten Punkts
            
        Returns:
            Entfernung in Kilometern
            
        Requirement: 16.4
        """
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        # Erdradius in km
        R = 6371.0
        
        # Koordinaten in Radiant umwandeln
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine-Formel
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    def optimize_route(self, customer_ids: List[int], start_location: Optional[Tuple[float, float]] = None) -> List[Dict[str, Any]]:
        """
        Optimiert eine Route für mehrere Kunden (Nearest Neighbor Algorithmus)
        
        Args:
            customer_ids: Liste von Kunden-IDs
            start_location: Startpunkt (lat, lon). Wenn None, wird der erste Kunde verwendet
            
        Returns:
            Liste von Kunden in optimierter Reihenfolge mit Entfernungen
            
        Requirement: 16.4
        """
        if not customer_ids:
            return []
        
        # Kundendaten abrufen
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(customer_ids))
            cursor.execute(f"""
                SELECT 
                    id, first_name, last_name, company_name,
                    address, house_number, city, zip_code,
                    latitude, longitude
                FROM customers
                WHERE id IN ({placeholders})
                AND latitude IS NOT NULL AND longitude IS NOT NULL
            """, customer_ids)
            
            customers = []
            for row in cursor.fetchall():
                customers.append({
                    'id': row['id'],
                    'name': f"{row['first_name']} {row['last_name']}".strip(),
                    'company': row['company_name'],
                    'address': f"{row['address']} {row['house_number']}".strip(),
                    'city': row['city'],
                    'zip_code': row['zip_code'],
                    'latitude': row['latitude'],
                    'longitude': row['longitude']
                })
            
            if not customers:
                return []
            
            # Nearest Neighbor Algorithmus
            route = []
            remaining = customers.copy()
            
            # Startpunkt festlegen
            if start_location:
                current_location = start_location
            else:
                # Ersten Kunden als Start verwenden
                first_customer = remaining.pop(0)
                route.append({**first_customer, 'distance_km': 0, 'cumulative_distance_km': 0})
                current_location = (first_customer['latitude'], first_customer['longitude'])
            
            total_distance = 0
            
            # Nächsten nächsten Nachbarn finden
            while remaining:
                nearest = None
                min_distance = float('inf')
                
                for customer in remaining:
                    distance = self.calculate_distance(
                        current_location,
                        (customer['latitude'], customer['longitude'])
                    )
                    
                    if distance < min_distance:
                        min_distance = distance
                        nearest = customer
                
                if nearest:
                    total_distance += min_distance
                    route.append({
                        **nearest,
                        'distance_km': round(min_distance, 2),
                        'cumulative_distance_km': round(total_distance, 2)
                    })
                    remaining.remove(nearest)
                    current_location = (nearest['latitude'], nearest['longitude'])
            
            return route
            
        except Exception as e:
            print(f"Fehler bei der Routenoptimierung: {e}")
            return []
        finally:
            conn.close()
    
    def create_route_map(self, route: List[Dict[str, Any]]) -> Optional[Any]:
        """
        Erstellt eine Karte mit optimierter Route
        
        Args:
            route: Optimierte Route von optimize_route()
            
        Returns:
            Folium Map-Objekt oder None bei Fehler
            
        Requirement: 16.4
        """
        if not FOLIUM_AVAILABLE or not route:
            return None
        
        # Zentrum berechnen
        avg_lat = sum(c['latitude'] for c in route) / len(route)
        avg_lon = sum(c['longitude'] for c in route) / len(route)
        
        # Karte erstellen
        m = folium.Map(
            location=(avg_lat, avg_lon),
            zoom_start=10,
            tiles='OpenStreetMap'
        )
        
        # Route als Linie zeichnen
        route_coords = [(c['latitude'], c['longitude']) for c in route]
        folium.PolyLine(
            route_coords,
            color='blue',
            weight=3,
            opacity=0.7
        ).add_to(m)
        
        # Marker für jeden Stopp
        for i, customer in enumerate(route):
            # Popup-Inhalt
            popup_html = f"""
            <div style="font-family: Arial; min-width: 200px;">
                <h4 style="margin: 0 0 10px 0;">Stopp {i + 1}: {customer['name']}</h4>
                {f"<p style='margin: 5px 0;'><b>{customer['company']}</b></p>" if customer['company'] else ""}
                <p style="margin: 5px 0;"> {customer['address']}<br>{customer['zip_code']} {customer['city']}</p>
                <p style="margin: 5px 0;"> Entfernung: {customer.get('distance_km', 0)} km</p>
                <p style="margin: 5px 0;"> Gesamt: {customer.get('cumulative_distance_km', 0)} km</p>
            </div>
            """
            
            # Marker-Farbe je nach Position
            if i == 0:
                color = 'green'  # Start
                icon = 'play'
            elif i == len(route) - 1:
                color = 'red'  # Ende
                icon = 'stop'
            else:
                color = 'blue'  # Zwischenstopp
                icon = 'info-sign'
            
            folium.Marker(
                location=[customer['latitude'], customer['longitude']],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"Stopp {i + 1}: {customer['name']}",
                icon=folium.Icon(color=color, icon=icon, prefix='glyphicon')
            ).add_to(m)
        
        return m
    
    def export_route_to_calendar(self, route: List[Dict[str, Any]], start_date: datetime, 
                                 duration_per_stop_minutes: int = 60) -> List[Dict[str, Any]]:
        """
        Exportiert eine Route als Kalender-Termine
        
        Args:
            route: Optimierte Route
            start_date: Startdatum und -zeit
            duration_per_stop_minutes: Dauer pro Stopp in Minuten
            
        Returns:
            Liste von Termin-Dictionaries für crm_appointments
            
        Requirement: 16.5
        """
        appointments = []
        current_time = start_date
        
        for i, customer in enumerate(route):
            # Fahrzeit zum nächsten Kunden (10 Minuten pro km, mindestens 10 Minuten)
            if i > 0:
                travel_time = max(10, int(customer.get('distance_km', 0) * 10))
                current_time += timedelta(minutes=travel_time)
            
            # Termin erstellen
            appointment = {
                'customer_id': customer['id'],
                'title': f"Kundenbesuch: {customer['name']}",
                'description': f"Routenplanung - Stopp {i + 1}\n\nAdresse: {customer['address']}, {customer['zip_code']} {customer['city']}",
                'start_time': current_time.isoformat(),
                'end_time': (current_time + timedelta(minutes=duration_per_stop_minutes)).isoformat(),
                'location': f"{customer['address']}, {customer['zip_code']} {customer['city']}",
                'appointment_type': 'customer_visit'
            }
            
            appointments.append(appointment)
            
            # Zeit für nächsten Termin
            current_time += timedelta(minutes=duration_per_stop_minutes)
        
        return appointments
    
    def save_appointments_to_db(self, appointments: List[Dict[str, Any]]) -> int:
        """
        Speichert Termine in der Datenbank
        
        Args:
            appointments: Liste von Termin-Dictionaries
            
        Returns:
            Anzahl der gespeicherten Termine
            
        Requirement: 16.5
        """
        conn = self._get_connection()
        saved_count = 0
        
        try:
            cursor = conn.cursor()
            
            for apt in appointments:
                cursor.execute("""
                    INSERT INTO crm_appointments 
                    (customer_id, title, description, start_time, end_time, location, appointment_type, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    apt['customer_id'],
                    apt['title'],
                    apt['description'],
                    apt['start_time'],
                    apt['end_time'],
                    apt['location'],
                    apt.get('appointment_type', 'customer_visit'),
                    datetime.now().isoformat()
                ))
                saved_count += 1
            
            conn.commit()
            print(f"{saved_count} Termine erfolgreich gespeichert")
            return saved_count
            
        except Exception as e:
            print(f"Fehler beim Speichern der Termine: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()


def ensure_geo_columns():
    """
    Stellt sicher, dass die Geo-Spalten in der customers-Tabelle existieren
    
    Requirement: 16.1
    """
    from database import get_db_connection
    
    conn = get_db_connection()
    if not conn:
        print("Keine Datenbankverbindung")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Prüfen, welche Spalten bereits existieren
        cursor.execute("PRAGMA table_info(customers)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        # Geo-Spalten hinzufügen, falls nicht vorhanden
        columns_to_add = {
            'latitude': 'REAL',
            'longitude': 'REAL',
            'geocoded_at': 'TEXT'
        }
        
        for col_name, col_type in columns_to_add.items():
            if col_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE customers ADD COLUMN {col_name} {col_type}")
                    print(f"Spalte '{col_name}' zur Tabelle 'customers' hinzugefügt")
                except sqlite3.OperationalError as e:
                    print(f"Warnung: Spalte '{col_name}' konnte nicht hinzugefügt werden: {e}")
        
        conn.commit()
        print("Geo-Spalten erfolgreich überprüft/hinzugefügt")
        return True
        
    except Exception as e:
        print(f"Fehler beim Hinzufügen der Geo-Spalten: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# Hilfsfunktionen für einfache Verwendung

def geocode_customer(customer_id: int, db_path: str = None) -> bool:
    """Geocodiert einen einzelnen Kunden"""
    if db_path is None:
        from database import DB_PATH
        db_path = DB_PATH
    
    mapper = GeoMapper(db_path)
    return mapper.update_customer_coordinates(customer_id)


def get_customer_map(filter_params: Optional[Dict[str, Any]] = None, db_path: str = None) -> Optional[Any]:
    """Erstellt eine Karte mit allen Kunden"""
    if db_path is None:
        from database import DB_PATH
        db_path = DB_PATH
    
    mapper = GeoMapper(db_path)
    customers = mapper.get_customers_with_coordinates(filter_params)
    return mapper.create_map(customers)


def plan_route(customer_ids: List[int], start_date: datetime = None, db_path: str = None) -> Tuple[List[Dict[str, Any]], Optional[Any]]:
    """
    Plant eine optimierte Route und gibt Route + Karte zurück
    
    Returns:
        Tuple (route, map)
    """
    if db_path is None:
        from database import DB_PATH
        db_path = DB_PATH
    
    if start_date is None:
        start_date = datetime.now()
    
    mapper = GeoMapper(db_path)
    route = mapper.optimize_route(customer_ids)
    route_map = mapper.create_route_map(route) if route else None
    
    return route, route_map
