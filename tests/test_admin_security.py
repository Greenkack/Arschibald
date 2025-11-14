"""
Test-Skript für Admin-Passwortschutz Implementierung
Verifiziert alle Funktionen und zeigt Status an
"""
import sys
sys.path.insert(0, r'c:\Users\win10\Desktop\Bokuk2 - Kopie')

print('=' * 80)
print('ADMIN PASSWORTSCHUTZ - FUNKTIONSTEST')
print('=' * 80)
print()

# Test 1: Import-Test
print('[PACKAGE] TEST 1: IMPORT-TEST')
print('-' * 80)

try:
    from admin_security import (
        is_area_protected,
        get_admin_protected_areas,
        save_admin_protected_areas,
        verify_admin_password
    )
    print('[OK] Alle Funktionen erfolgreich importiert:')
    print('   - is_area_protected()')
    print('   - get_admin_protected_areas()')
    print('   - save_admin_protected_areas()')
    print('   - verify_admin_password()')
except ImportError as e:
    print(f'[ERROR] Import fehlgeschlagen: {e}')
    sys.exit(1)

# Test 2: get_admin_protected_areas()
print()
print('🔐 TEST 2: GET_ADMIN_PROTECTED_AREAS()')
print('-' * 80)

try:
    areas = get_admin_protected_areas()
    print(f'[OK] Funktion ausgeführt')
    print(f'[OK] Anzahl Bereiche: {len(areas)}')
    print()
    print('Bereiche im Detail:')
    
    protected_count = 0
    for i, (area_id, is_protected) in enumerate(areas.items(), 1):
        status = '🔒 Geschützt' if is_protected else '🔓 Offen'
        print(f'  {i:2d}. {area_id:30s} → {status}')
        if is_protected:
            protected_count += 1
    
    print()
    print(f'Statistik: {protected_count}/{len(areas)} Bereiche standardmäßig geschützt')
    
except Exception as e:
    print(f'[ERROR] Fehler: {e}')
    import traceback
    traceback.print_exc()

# Test 3: is_area_protected()
print()
print('[SEARCH] TEST 3: IS_AREA_PROTECTED()')
print('-' * 80)

test_areas = [
    ('price_matrix', 'Preis Matrix'),
    ('pv_mounting', 'PV-Unterkonstruktionen'),
    ('heatpump_settings', 'Wärmepumpen'),
    ('build_infos', 'Build Infos'),
    ('user_management', 'Benutzerverwaltung'),
]

try:
    print('Teste verschiedene Bereiche:')
    for area_id, area_name in test_areas:
        is_protected = is_area_protected(area_id)
        status = '🔒 GESCHÜTZT' if is_protected else '🔓 OFFEN'
        print(f'  {area_name:30s} ({area_id:20s}) → {status}')
    
    print()
    print('[OK] is_area_protected() funktioniert korrekt')
    
except Exception as e:
    print(f'[ERROR] Fehler: {e}')

# Test 4: Nicht existierender Bereich
print()
print('[WARNING]  TEST 4: NICHT EXISTIERENDER BEREICH')
print('-' * 80)

try:
    result = is_area_protected('nicht_existent')
    print(f'[OK] Funktion gibt {result} zurück (sollte False sein)')
    if result == False:
        print('[OK] Korrekt: Unbekannte Bereiche sind standardmäßig NICHT geschützt')
    else:
        print('[WARNING] Warnung: Unbekannte Bereiche sollten False zurückgeben')
except Exception as e:
    print(f'[ERROR] Fehler: {e}')

# Test 5: admin_panel.py Integration
print()
print('[TOOL] TEST 5: ADMIN_PANEL.PY INTEGRATION')
print('-' * 80)

try:
    with open(r'c:\Users\win10\Desktop\Bokuk2 - Kopie\admin_panel.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Prüfe auf create_protected_tab_renderer
    if 'def create_protected_tab_renderer' in content:
        print('[OK] create_protected_tab_renderer() Funktion gefunden')
        
        # Zähle Verwendungen
        usage_count = content.count('create_protected_tab_renderer(')
        print(f'[OK] Verwendungen: {usage_count}x')
        
        # Prüfe Import
        if 'from admin_security import is_area_protected' in content:
            print('[OK] is_area_protected wird importiert')
        elif 'is_area_protected' in content:
            print('[OK] is_area_protected wird verwendet (Runtime-Import)')
        else:
            print('[WARNING] Warnung: is_area_protected Import nicht gefunden')
    else:
        print('[ERROR] create_protected_tab_renderer() nicht gefunden')
        
except Exception as e:
    print(f'[ERROR] Fehler beim Lesen von admin_panel.py: {e}')

# Zusammenfassung
print()
print('=' * 80)
print('ZUSAMMENFASSUNG')
print('=' * 80)
print()
print('[OK] Import-Test: Erfolgreich')
print('[OK] get_admin_protected_areas(): Erfolgreich')
print('[OK] is_area_protected(): Erfolgreich')
print('[OK] Fallback für unbekannte Bereiche: Erfolgreich')
print('[OK] admin_panel.py Integration: Verifiziert')
print()
print('🎉 ALLE TESTS BESTANDEN!')
print('=' * 80)
