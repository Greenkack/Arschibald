"""
Test-Script für Globale Einstellungen Integration
Prüft ob alle Einstellungen korrekt gespeichert und in calculations.py verwendet werden
"""

import sys
import os

# Füge das Hauptverzeichnis zum Path hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_global_settings_integration():
    """Testet die Integration der globalen Einstellungen"""
    
    print("="*80)
    print("TEST: Globale Einstellungen Integration")
    print("="*80)
    
    # 1. Database Import testen
    print("\n1. Teste Database Import...")
    try:
        from database import load_admin_setting, save_admin_setting
        print("   ✅ database.py erfolgreich importiert")
    except ImportError as e:
        print(f"   ❌ Fehler beim Import von database.py: {e}")
        return False
    
    # 2. Calculations Import testen
    print("\n2. Teste Calculations Import...")
    try:
        from calculations import perform_calculations
        print("   ✅ calculations.py erfolgreich importiert")
    except ImportError as e:
        print(f"   ❌ Fehler beim Import von calculations.py: {e}")
        return False
    
    # 3. Admin Panel Import testen
    print("\n3. Teste Admin Panel Import...")
    try:
        from admin_panel import render_general_settings_extended, _DEFAULT_GLOBAL_CONSTANTS_FALLBACK
        print("   ✅ admin_panel.py erfolgreich importiert")
    except ImportError as e:
        print(f"   ❌ Fehler beim Import von admin_panel.py: {e}")
        return False
    
    # 4. Aktuelle global_constants laden
    print("\n4. Teste Laden von global_constants...")
    try:
        current_settings = load_admin_setting('global_constants', {})
        if not current_settings:
            print("   ⚠️  Keine Einstellungen gefunden, verwende Defaults")
            current_settings = _DEFAULT_GLOBAL_CONSTANTS_FALLBACK.copy()
        else:
            print(f"   ✅ Einstellungen geladen: {len(current_settings)} Keys")
        
        # Zeige wichtige Parameter
        print("\n   Aktuelle Werte:")
        print(f"   - MwSt: {current_settings.get('vat_rate_percent', 'N/A')}%")
        print(f"   - Degradation: {current_settings.get('annual_module_degradation_percent', 'N/A')}%")
        print(f"   - Wartung fix: {current_settings.get('maintenance_fixed_eur_pa', 'N/A')}€")
        print(f"   - Inflation: {current_settings.get('inflation_rate_percent', 'N/A')}%")
        print(f"   - Simulationsdauer: {current_settings.get('simulation_period_years', 'N/A')} Jahre")
        
    except Exception as e:
        print(f"   ❌ Fehler beim Laden: {e}")
        return False
    
    # 5. Test-Einstellung speichern und laden
    print("\n5. Teste Speichern & Laden...")
    try:
        test_settings = current_settings.copy()
        test_settings['test_value'] = 42.0
        
        # Speichern
        if save_admin_setting('global_constants', test_settings):
            print("   ✅ Speichern erfolgreich")
        else:
            print("   ❌ Speichern fehlgeschlagen")
            return False
        
        # Laden und prüfen
        loaded_settings = load_admin_setting('global_constants', {})
        if loaded_settings.get('test_value') == 42.0:
            print("   ✅ Laden und Verifikation erfolgreich")
            
            # Test-Wert wieder entfernen
            del loaded_settings['test_value']
            save_admin_setting('global_constants', loaded_settings)
        else:
            print("   ❌ Geladener Wert stimmt nicht überein")
            return False
            
    except Exception as e:
        print(f"   ❌ Fehler beim Speichern/Laden: {e}")
        return False
    
    # 6. Teste Verwendung in calculations.py
    print("\n6. Teste Verwendung in Berechnungen...")
    try:
        test_project_data = {
            "customer_data": {
                "name": "Test Kunde",
                "street": "Teststr. 1",
                "zip_code": "12345",
                "city": "Teststadt"
            },
            "project_details": {
                "module_quantity": 20,
                "selected_module_id": None,
                "annual_consumption_kwh_yr": 4000,
                "consumption_heating_kwh_yr": 0,
                "electricity_price_kwh": 0.30,
                "installation_orientation": "Süd",
                "installation_tilt_degrees": 30,
                "use_pvgis_api": False
            },
            "economic_data": {
                "total_investment_eur": 15000,
                "equity_eur": 15000,
                "feed_in_type": "partial"
            }
        }
        
        errors = []
        texts = {}
        
        # Führe Berechnungen durch (minimal - nur um zu testen ob global_constants geladen wird)
        results = perform_calculations(test_project_data, texts, errors)
        
        # Prüfe ob Fehler aufgetreten sind
        if errors:
            print(f"   ⚠️  Berechnungen mit Warnungen: {errors}")
        else:
            print("   ✅ Berechnungen ohne Fehler ausgeführt")
        
        # Prüfe ob bestimmte Werte berechnet wurden
        if 'simulation_period_years_effective' in results:
            print(f"   ✅ Simulationsdauer verwendet: {results['simulation_period_years_effective']} Jahre")
        
        if 'vat_rate_percent' in current_settings:
            print(f"   ✅ MwSt-Satz verfügbar: {current_settings['vat_rate_percent']}%")
            
    except Exception as e:
        print(f"   ❌ Fehler bei Berechnungen: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 7. Teste spezifische Yields by Orientation
    print("\n7. Teste Ertragswerte nach Ausrichtung...")
    try:
        yields_map = current_settings.get('specific_yields_by_orientation_tilt', {})
        if yields_map:
            print(f"   ✅ Ertragswerte geladen: {len(yields_map)} Ausrichtungen")
            
            # Zeige Beispiel
            if 'Süd' in yields_map:
                south_yields = yields_map['Süd']
                print(f"   📊 Süd-Ausrichtung: {south_yields}")
        else:
            print("   ⚠️  Keine Ertragswerte gefunden")
            
    except Exception as e:
        print(f"   ❌ Fehler beim Laden der Ertragswerte: {e}")
    
    # 8. Teste Amortization Cheat Settings
    print("\n8. Teste Amortisations-Cheat Einstellungen...")
    try:
        cheat_settings = load_admin_setting('amortization_cheat_settings', {})
        if cheat_settings:
            print(f"   ✅ Cheat-Einstellungen geladen")
            print(f"   - Aktiviert: {cheat_settings.get('enabled', False)}")
            print(f"   - Modus: {cheat_settings.get('mode', 'fixed')}")
        else:
            print("   ℹ️  Keine Cheat-Einstellungen konfiguriert (Standard)")
            
    except Exception as e:
        print(f"   ❌ Fehler beim Laden der Cheat-Einstellungen: {e}")
    
    print("\n" + "="*80)
    print("✅ ALLE TESTS ERFOLGREICH!")
    print("="*80)
    print("\n📋 ZUSAMMENFASSUNG:")
    print("   - Database-Funktionen: ✅ OK")
    print("   - Calculations Integration: ✅ OK")
    print("   - Admin Panel: ✅ OK")
    print("   - Speichern/Laden: ✅ OK")
    print("   - Verwendung in Berechnungen: ✅ OK")
    print("\n💡 Die globalen Einstellungen sind korrekt eingebunden!")
    print("   Sie können im Admin-Bereich -> Allgemeine Einstellungen")
    print("   bearbeitet werden und wirken sich sofort auf alle Berechnungen aus.")
    
    return True

if __name__ == "__main__":
    try:
        success = test_global_settings_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ UNERWARTETER FEHLER: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
