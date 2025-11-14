"""
Reset Admin Protected Areas - Setzt alle Bereiche auf standardmäßig geschützt
"""
import sys
sys.path.insert(0, r'c:\Users\win10\Desktop\Bokuk2 - Kopie')

print('=' * 80)
print('ADMIN PROTECTED AREAS - DATENBANK RESET')
print('=' * 80)
print()

try:
    from database import get_db_connection
    import json
    
    # Neue geschützte Bereiche (ALLE außer economic_settings, ui_customization, pdf_settings)
    new_protected_areas = {
        'build_infos': True,
        'user_management': True,
        'company_management': True,
        'product_management': True,
        'product_database': True,
        'pv_mounting': True,  # [OK] NEU GESCHÜTZT
        'services_management': True,
        'price_matrix': True,  # [OK] NEU GESCHÜTZT
        'economic_settings': True,  # [OK] NEU GESCHÜTZT
        'tariff_management': True,  # [OK] NEU GESCHÜTZT
        'heatpump_settings': True,
        'ui_customization': True,  # [OK] NEU GESCHÜTZT
        'logo_management': True,
        'intro_settings': True,
        'payment_terms': True,
        'visualization_settings': True,  # [OK] NEU GESCHÜTZT
        'pdf_settings': True,  # [OK] NEU GESCHÜTZT
        'advanced_settings': True,  # [OK] NEU GESCHÜTZT
    }
    
    print('🔄 Aktualisiere Datenbank...')
    print('-' * 80)
    
    conn = get_db_connection()
    if not conn:
        print('[ERROR] Keine Datenbankverbindung möglich!')
        sys.exit(1)
    
    cursor = conn.cursor()
    
    # Lösche alte Einstellung
    cursor.execute("DELETE FROM admin_settings WHERE key = 'protected_admin_areas'")
    
    # Füge neue Einstellung ein
    cursor.execute("""
        INSERT INTO admin_settings (key, value)
        VALUES ('protected_admin_areas', ?)
    """, (json.dumps(new_protected_areas),))
    
    conn.commit()
    conn.close()
    
    print('[OK] Datenbank erfolgreich aktualisiert!')
    print()
    print('[CHART] Neue Konfiguration:')
    print('-' * 80)
    
    protected_count = sum(1 for v in new_protected_areas.values() if v)
    total_count = len(new_protected_areas)
    
    print(f'🔒 Geschützte Bereiche: {protected_count}/{total_count}')
    print()
    
    for area_id, is_protected in sorted(new_protected_areas.items()):
        status = '🔒 GESCHÜTZT' if is_protected else '🔓 OFFEN'
        print(f'  {area_id:30s} → {status}')
    
    print()
    print('=' * 80)
    print('[OK] ERFOLG: Alle gewünschten Bereiche sind jetzt geschützt!')
    print('=' * 80)
    print()
    print('[WARNING]  WICHTIG: Starte die Streamlit-App neu, damit die Änderungen wirksam werden!')
    print('   (Session State wird beim Neustart zurückgesetzt)')
    
except Exception as e:
    print(f'[ERROR] Fehler: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
