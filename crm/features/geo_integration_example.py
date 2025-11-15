"""
Geo-Mapping Integration Beispiel

Zeigt, wie das Geo-Mapping-System in die CRM-Anwendung integriert wird.

Anforderungen: 16.1, 16.2, 16.3, 16.4, 16.5
"""

from datetime import datetime, timedelta
from crm.features.geo_mapper import GeoMapper, ensure_geo_columns


def example_1_geocode_customers():
    """
    Beispiel 1: Kunden geocodieren
    
    Requirement: 16.1
    """
    print("="*70)
    print("BEISPIEL 1: Kunden geocodieren")
    print("="*70)
    
    # GeoMapper initialisieren
    mapper = GeoMapper('data/app_data.db')
    
    # Geo-Spalten sicherstellen
    ensure_geo_columns()
    
    # Alle nicht-geocodierten Kunden geocodieren
    print("\n1. Geocodiere alle Kunden ohne Koordinaten...")
    stats = mapper.geocode_all_customers(force_update=False)
    
    print(f"\nGeocoding abgeschlossen:")
    print(f"   - Erfolgreich: {stats['success']}")
    print(f"   - Fehlgeschlagen: {stats['failed']}")
    print(f"   - Übersprungen: {stats['skipped']}")
    
    # Einzelnen Kunden geocodieren
    print("\n2. Einzelnen Kunden geocodieren...")
    success = mapper.update_customer_coordinates(customer_id=1)
    
    if success:
        print("   Kunde 1 erfolgreich geocodiert")
    else:
        print("   Geocoding fehlgeschlagen")


def example_2_show_customers_on_map():
    """
    Beispiel 2: Kunden auf Karte anzeigen
    
    Requirement: 16.2, 16.3
    """
    print("\n" + "="*70)
    print("BEISPIEL 2: Kunden auf Karte anzeigen")
    print("="*70)
    
    mapper = GeoMapper('data/app_data.db')
    
    # Alle Kunden mit Koordinaten abrufen
    print("\n1. Kunden mit Koordinaten abrufen...")
    customers = mapper.get_customers_with_coordinates()
    
    print(f"   {len(customers)} Kunden gefunden")
    
    if customers:
        # Erste 3 Kunden anzeigen
        print("\n   Beispiel-Kunden:")
        for i, customer in enumerate(customers[:3], 1):
            print(f"   {i}. {customer['name']} ({customer['city']})")
            print(f"      📍 {customer['latitude']:.6f}, {customer['longitude']:.6f}")
        
        # Karte erstellen
        print("\n2. Karte erstellen...")
        customer_map = mapper.create_map(customers)
        
        if customer_map:
            # Karte speichern
            map_file = 'kunden_karte.html'
            customer_map.save(map_file)
            print(f"   Karte gespeichert: {map_file}")
            print(f"   Öffnen Sie die Datei im Browser")
        else:
            print("   Karte konnte nicht erstellt werden")
    else:
        print("   Keine Kunden mit Koordinaten gefunden")
        print("   Führen Sie zuerst Beispiel 1 aus")


def example_3_filter_customers():
    """
    Beispiel 3: Kunden nach Stadt filtern
    
    Requirement: 16.2
    """
    print("\n" + "="*70)
    print("BEISPIEL 3: Kunden nach Stadt filtern")
    print("="*70)
    
    mapper = GeoMapper('data/app_data.db')
    
    # Nach Stadt filtern
    city = "Berlin"
    print(f"\n1. Kunden in {city} suchen...")
    customers = mapper.get_customers_with_coordinates({'city': city})
    
    print(f"   {len(customers)} Kunden in {city} gefunden")
    
    if customers:
        for i, customer in enumerate(customers, 1):
            print(f"   {i}. {customer['name']}")
            print(f"      📍 {customer['address']}, {customer['zip_code']} {customer['city']}")
        
        # Karte für diese Stadt erstellen
        print(f"\n2. Karte für {city} erstellen...")
        city_map = mapper.create_map(customers)
        
        if city_map:
            map_file = f'kunden_{city.lower()}.html'
            city_map.save(map_file)
            print(f"   Karte gespeichert: {map_file}")


def example_4_calculate_distances():
    """
    Beispiel 4: Entfernungen berechnen
    
    Requirement: 16.4
    """
    print("\n" + "="*70)
    print("BEISPIEL 4: Entfernungen berechnen")
    print("="*70)
    
    mapper = GeoMapper('data/app_data.db')
    
    # Bekannte Koordinaten
    cities = {
        'Berlin': (52.5200, 13.4050),
        'München': (48.1351, 11.5820),
        'Hamburg': (53.5511, 9.9937),
        'Köln': (50.9375, 6.9603)
    }
    
    print("\n1. Entfernungen zwischen deutschen Städten:")
    print()
    
    # Entfernungen berechnen
    for city1, coords1 in cities.items():
        for city2, coords2 in cities.items():
            if city1 < city2:  # Jedes Paar nur einmal
                distance = mapper.calculate_distance(coords1, coords2)
                print(f"   {city1} → {city2}: {distance:.2f} km")


def example_5_optimize_route():
    """
    Beispiel 5: Route optimieren
    
    Requirement: 16.4
    """
    print("\n" + "="*70)
    print("BEISPIEL 5: Route optimieren")
    print("="*70)
    
    mapper = GeoMapper('data/app_data.db')
    
    # Kunden mit Koordinaten abrufen
    customers = mapper.get_customers_with_coordinates()
    
    if len(customers) < 2:
        print("   Mindestens 2 Kunden mit Koordinaten erforderlich")
        print("   Führen Sie zuerst Beispiel 1 aus")
        return
    
    # Erste 5 Kunden für Route auswählen
    customer_ids = [c['id'] for c in customers[:5]]
    
    print(f"\n1. Route für {len(customer_ids)} Kunden optimieren...")
    print(f"   Kunden-IDs: {customer_ids}")
    
    # Route optimieren
    route = mapper.optimize_route(customer_ids)
    
    if route:
        print(f"\n   Route optimiert!")
        print(f"   📏 Gesamtstrecke: {route[-1]['cumulative_distance_km']:.2f} km")
        
        print("\n2. Routendetails:")
        for i, stop in enumerate(route, 1):
            print(f"\n   Stopp {i}: {stop['name']}")
            print(f"      📍 {stop['address']}, {stop['zip_code']} {stop['city']}")
            if i > 1:
                print(f"      🚗 Entfernung vom vorherigen Stopp: {stop['distance_km']:.2f} km")
            print(f"      📏 Gesamtstrecke bis hier: {stop['cumulative_distance_km']:.2f} km")
        
        # Routenkarte erstellen
        print("\n3. Routenkarte erstellen...")
        route_map = mapper.create_route_map(route)
        
        if route_map:
            map_file = 'optimierte_route.html'
            route_map.save(map_file)
            print(f"   Routenkarte gespeichert: {map_file}")
    else:
        print("   Route konnte nicht optimiert werden")


def example_6_export_to_calendar():
    """
    Beispiel 6: Route in Kalender exportieren
    
    Requirement: 16.5
    """
    print("\n" + "="*70)
    print("BEISPIEL 6: Route in Kalender exportieren")
    print("="*70)
    
    mapper = GeoMapper('data/app_data.db')
    
    # Kunden mit Koordinaten abrufen
    customers = mapper.get_customers_with_coordinates()
    
    if len(customers) < 2:
        print("   Mindestens 2 Kunden mit Koordinaten erforderlich")
        return
    
    # Route optimieren
    customer_ids = [c['id'] for c in customers[:3]]
    route = mapper.optimize_route(customer_ids)
    
    if not route:
        print("   Route konnte nicht optimiert werden")
        return
    
    print(f"\n1. Route mit {len(route)} Stopps erstellt")
    
    # Startdatum festlegen (nächster Montag, 9:00 Uhr)
    today = datetime.now()
    days_until_monday = (7 - today.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7
    
    start_date = today + timedelta(days=days_until_monday)
    start_date = start_date.replace(hour=9, minute=0, second=0, microsecond=0)
    
    print(f"   📅 Startdatum: {start_date.strftime('%d.%m.%Y %H:%M')}")
    
    # Termine generieren
    print("\n2. Termine generieren...")
    appointments = mapper.export_route_to_calendar(
        route,
        start_date,
        duration_per_stop_minutes=60
    )
    
    print(f"   {len(appointments)} Termine erstellt")
    
    # Termine anzeigen
    print("\n3. Termine-Übersicht:")
    for i, apt in enumerate(appointments, 1):
        start = datetime.fromisoformat(apt['start_time'])
        end = datetime.fromisoformat(apt['end_time'])
        
        print(f"\n   Termin {i}:")
        print(f"      {apt['title']}")
        print(f"      🕐 {start.strftime('%H:%M')} - {end.strftime('%H:%M')}")
        print(f"      📍 {apt['location']}")
    
    # In Datenbank speichern
    print("\n4. Termine in Kalender speichern...")
    saved_count = mapper.save_appointments_to_db(appointments)
    
    if saved_count > 0:
        print(f"   {saved_count} Termine erfolgreich gespeichert")
        print("   Die Termine sind jetzt im CRM-Kalender sichtbar")
    else:
        print("   Fehler beim Speichern der Termine")


def example_7_complete_workflow():
    """
    Beispiel 7: Kompletter Workflow
    
    Zeigt den typischen Workflow von Geocoding bis Kalender-Export
    
    Requirement: 16.1, 16.2, 16.3, 16.4, 16.5
    """
    print("\n" + "="*70)
    print("BEISPIEL 7: Kompletter Workflow")
    print("="*70)
    
    mapper = GeoMapper('data/app_data.db')
    
    # Schritt 1: Geo-Spalten sicherstellen
    print("\n📋 Schritt 1: Datenbank vorbereiten")
    ensure_geo_columns()
    print("   Geo-Spalten vorhanden")
    
    # Schritt 2: Kunden geocodieren
    print("\n📍 Schritt 2: Kunden geocodieren")
    stats = mapper.geocode_all_customers()
    print(f"   {stats['success']} Kunden geocodiert")
    
    # Schritt 3: Kunden auf Karte anzeigen
    print("\n🗺️ Schritt 3: Kundenkarte erstellen")
    customers = mapper.get_customers_with_coordinates()
    
    if customers:
        customer_map = mapper.create_map(customers)
        if customer_map:
            customer_map.save('workflow_kunden.html')
            print(f"   Karte mit {len(customers)} Kunden erstellt")
    
    # Schritt 4: Route planen
    print("\n🚗 Schritt 4: Route planen")
    
    if len(customers) >= 3:
        customer_ids = [c['id'] for c in customers[:3]]
        route = mapper.optimize_route(customer_ids)
        
        if route:
            print(f"   Route optimiert: {route[-1]['cumulative_distance_km']:.2f} km")
            
            # Routenkarte
            route_map = mapper.create_route_map(route)
            if route_map:
                route_map.save('workflow_route.html')
                print("   Routenkarte erstellt")
            
            # Schritt 5: Kalender-Export
            print("\n📅 Schritt 5: Termine erstellen")
            
            start_date = datetime.now() + timedelta(days=1)
            start_date = start_date.replace(hour=9, minute=0, second=0, microsecond=0)
            
            appointments = mapper.export_route_to_calendar(route, start_date, 60)
            saved_count = mapper.save_appointments_to_db(appointments)
            
            print(f"   {saved_count} Termine im Kalender gespeichert")
            
            print("\n" + "="*70)
            print("WORKFLOW ERFOLGREICH ABGESCHLOSSEN")
            print("="*70)
            print("\nErstellt:")
            print("  - workflow_kunden.html (Kundenkarte)")
            print("  - workflow_route.html (Routenkarte)")
            print(f"  - {saved_count} Termine im CRM-Kalender")
        else:
            print("   Route konnte nicht optimiert werden")
    else:
        print("   Mindestens 3 Kunden mit Koordinaten erforderlich")


def run_all_examples():
    """Führt alle Beispiele nacheinander aus"""
    print("\n" + "="*70)
    print("GEO-MAPPING INTEGRATION BEISPIELE")
    print("="*70)
    print("\nDiese Beispiele zeigen die Integration des Geo-Mapping-Systems")
    print("in die CRM-Anwendung.")
    print()
    
    try:
        example_1_geocode_customers()
        example_2_show_customers_on_map()
        example_3_filter_customers()
        example_4_calculate_distances()
        example_5_optimize_route()
        example_6_export_to_calendar()
        example_7_complete_workflow()
        
        print("\n" + "="*70)
        print("ALLE BEISPIELE ERFOLGREICH AUSGEFÜHRT")
        print("="*70)
        
    except Exception as e:
        print(f"\nFehler: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # Einzelne Beispiele ausführen
    import sys
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        
        examples = {
            '1': example_1_geocode_customers,
            '2': example_2_show_customers_on_map,
            '3': example_3_filter_customers,
            '4': example_4_calculate_distances,
            '5': example_5_optimize_route,
            '6': example_6_export_to_calendar,
            '7': example_7_complete_workflow,
        }
        
        if example_num in examples:
            examples[example_num]()
        else:
            print(f"Unbekanntes Beispiel: {example_num}")
            print("Verfügbare Beispiele: 1-7")
    else:
        # Alle Beispiele ausführen
        run_all_examples()
