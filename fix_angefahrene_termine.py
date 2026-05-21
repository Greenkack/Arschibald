"""
Korrigiere 'Angefahrene Termine' auf den korrekten Wert
"""

import sys
import sqlite3
from pathlib import Path
from datetime import date

DB_PATH = Path(__file__).parent / "data" / "app_data.db"

def fix_angefahrene_termine():
    """Korrigiere 'Angefahrene Termine' auf den gleichen Wert wie 'Angefahrene Termine gesamt'."""
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    today = date.today().isoformat()
    
    # Hole beide Werte
    cursor.execute("""
        SELECT c.name, pd.value, pd.id as data_id, c.id as criterion_id
        FROM controlling_performance_data pd
        JOIN controlling_criteria c ON pd.criterion_id = c.id
        WHERE pd.employee_id = 1 
        AND pd.date = ?
        AND c.name IN ('Angefahrene Termine', 'Angefahrene Termine gesamt')
    """, (today))
    
    data = {row['name']: {'value': row['value'], 'data_id': row['data_id'], 'criterion_id': row['criterion_id']} 
            for row in cursor.fetchall()}
    
    print("\n" + "="*80)
    print("CONTROLLING - ANGEFAHRENE TERMINE KORREKTUR")
    print("="*80)
    
    print("\n📊 AKTUELLE WERTE:")
    for name, info in data.items():
        print(f"  {name}: {info['value']}")
    
    angefahrene_termine_gesamt = data.get('Angefahrene Termine gesamt', {}).get('value', 0)
    angefahrene_termine = data.get('Angefahrene Termine', {}).get('value', None)
    
    if angefahrene_termine is None:
        print("\n❌ 'Angefahrene Termine' existiert nicht in der Datenbank!")
        
        # Hole Criterion ID für "Angefahrene Termine"
        cursor.execute("""
            SELECT id FROM controlling_criteria 
            WHERE name = 'Angefahrene Termine'
        """)
        criterion = cursor.fetchone()
        
        if criterion:
            print(f"➕ Füge 'Angefahrene Termine' = {angefahrene_termine_gesamt} hinzu...")
            cursor.execute("""
                INSERT INTO controlling_performance_data 
                (employee_id, criterion_id, value, date)
                VALUES (?, ?, ?, ?)
            """, (1, criterion['id'], angefahrene_termine_gesamt, today))
            conn.commit()
            print("✅ Wert erfolgreich hinzugefügt!")
        else:
            print("❌ Kriterium 'Angefahrene Termine' existiert nicht!")
            conn.close()
            return
    
    elif angefahrene_termine != angefahrene_termine_gesamt:
        print(f"\n⚠️  INKONSISTENZ GEFUNDEN!")
        print(f"   'Angefahrene Termine': {angefahrene_termine}")
        print(f"   'Angefahrene Termine gesamt': {angefahrene_termine_gesamt}")
        print(f"\n💡 Korrigiere 'Angefahrene Termine' auf {angefahrene_termine_gesamt}...")
        
        # Update
        data_id = data['Angefahrene Termine']['data_id']
        cursor.execute("""
            UPDATE controlling_performance_data
            SET value = ?
            WHERE id = ?
        """, (angefahrene_termine_gesamt, data_id))
        conn.commit()
        
        print("✅ Wert erfolgreich korrigiert!")
    
    else:
        print("\n✅ Werte sind bereits identisch - keine Korrektur erforderlich!")
    
    # Zeige neue Quotas
    cursor.execute("""
        SELECT c.name, pd.value
        FROM controlling_performance_data pd
        JOIN controlling_criteria c ON pd.criterion_id = c.id
        WHERE pd.employee_id = 1 AND pd.date = ?
        AND c.name IN ('Angefahrene Termine', 'Kunden terminiert', 'Verkauf', 
                      'Angefahrene Termine gesamt', 'Getätigte Anrufe gesamt')
    """, (today))
    
    values = {row['name']: row['value'] for row in cursor.fetchall()}
    
    verkauf = values.get('Verkauf', 0)
    angefahrene_termine_gesamt = values.get('Angefahrene Termine gesamt', 0)
    kunden_terminiert = values.get('Kunden terminiert', 0)
    angefahrene_termine = values.get('Angefahrene Termine', 0)
    anrufe_gesamt = values.get('Getätigte Anrufe gesamt', 0)
    
    print("\n" + "="*80)
    print("NEUE QUOTA-BERECHNUNGEN:")
    print("="*80)
    
    if angefahrene_termine_gesamt > 0:
        abschlussquote = (verkauf / angefahrene_termine_gesamt) * 100
        print(f"\n✅ Abschlussquote: {abschlussquote:.1f}%")
        print(f"   ({verkauf} / {angefahrene_termine_gesamt}) × 100")
        if abschlussquote < 15.0:
            print(f"   ⚠️  WARNUNG: Unter Mindestziel von 15.0%")
        else:
            print(f"   ✅ Ziel erreicht!")
    
    if anrufe_gesamt > 0:
        terminquote = (kunden_terminiert / anrufe_gesamt) * 100
        print(f"\n✅ Terminvereinbarungsquote: {terminquote:.1f}%")
        print(f"   ({kunden_terminiert} / {anrufe_gesamt}) × 100")
        if terminquote >= 20.0:
            print(f"   ✅ ERFOLG: Ziel von 20.0% übertroffen!")
        elif terminquote >= 10.0:
            print(f"   ✅ Im Zielbereich")
        else:
            print(f"   ⚠️  WARNUNG: Unter Mindestziel von 10.0%")
    
    if kunden_terminiert > 0:
        anfahrquote = (angefahrene_termine / kunden_terminiert) * 100
        print(f"\n✅ Termine-Anfahrquote: {anfahrquote:.1f}%")
        print(f"   ({angefahrene_termine} / {kunden_terminiert}) × 100")
        if anfahrquote < 70.0:
            print(f"   ⚠️  WARNUNG: Unter Mindestziel von 70.0%")
            print(f"   ({int(kunden_terminiert - angefahrene_termine)} Termine fehlen)")
        else:
            print(f"   ✅ Ziel erreicht!")
    
    print("\n" + "="*80)
    print("✅ KORREKTUR ABGESCHLOSSEN")
    print("="*80)
    print("\nNächste Schritte:")
    print("1. Streamlit-App neu laden (F5)")
    print("2. Neuen Bericht erstellen")
    print("3. Notifications sollten jetzt korrekt angezeigt werden")
    print("="*80 + "\n")
    
    conn.close()


if __name__ == "__main__":
    fix_angefahrene_termine()
