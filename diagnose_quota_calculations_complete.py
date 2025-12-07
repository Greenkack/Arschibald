"""
Vollständige Diagnose der Controlling-Quotas
mit exakten Berechnungen basierend auf der Datenbank
"""

import sys
import sqlite3
from pathlib import Path
from datetime import date, datetime, timedelta

DB_PATH = Path(__file__).parent / "data" / "app_data.db"

def diagnose_quota_calculations():
    """Zeige exakte Quota-Berechnungen mit allen Zwischenschritten."""
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Hole alle Daten für Mitarbeiter 1 vom heutigen Datum
    today = date.today().isoformat()
    
    cursor.execute("""
        SELECT c.name, pd.value
        FROM controlling_performance_data pd
        JOIN controlling_criteria c ON pd.criterion_id = c.id
        WHERE pd.employee_id = 1 AND pd.date = ?
        ORDER BY c.name
    """, (today,))
    
    data = {row['name']: row['value'] for row in cursor.fetchall()}
    
    if not data:
        print(f"❌ Keine Daten gefunden für heute ({today})")
        conn.close()
        return
    
    print("\n" + "="*80)
    print("CONTROLLING QUOTA DIAGNOSE")
    print("="*80)
    print(f"Mitarbeiter ID: 1 (Mustafa Cetin)")
    print(f"Datum: {today}")
    print("="*80)
    
    print("\n📊 ROHDATEN AUS DATENBANK:")
    print("-"*80)
    for name in sorted(data.keys()):
        print(f"  {name:40s}: {data[name]:>10.2f}")
    print("-"*80)
    
    # Extrahiere relevante Werte
    verkauf = data.get('Verkauf', 0)
    angefahrene_termine_gesamt = data.get('Angefahrene Termine gesamt', 0)
    kunden_terminiert = data.get('Kunden terminiert', 0)
    getaetigte_anrufe_gesamt = data.get('Getätigte Anrufe gesamt', 0)
    angefahrene_termine = data.get('Angefahrene Termine', 0)
    
    print("\n🔢 QUOTA-BERECHNUNGEN:")
    print("="*80)
    
    # 1. Abschlussquote
    print("\n1️⃣  ABSCHLUSSQUOTE (Closing Rate)")
    print("-"*80)
    print(f"   Formel: (Verkauf / Angefahrene Termine gesamt) × 100")
    print(f"   Werte:  ({verkauf} / {angefahrene_termine_gesamt}) × 100")
    
    if angefahrene_termine_gesamt > 0:
        abschlussquote = (verkauf / angefahrene_termine_gesamt) * 100
        print(f"   Ergebnis: {abschlussquote:.2f}%")
        print(f"   Bedeutung: Von {int(angefahrene_termine_gesamt)} angefahrenen Terminen führten")
        print(f"              {int(verkauf)} zu einem Verkauf")
        
        # Threshold-Check
        threshold = 15.0
        if abschlussquote < threshold:
            print(f"   ⚠️  WARNUNG: Unter Mindestziel von {threshold}%")
        else:
            print(f"   ✅ Ziel erreicht (>= {threshold}%)")
    else:
        print(f"   ❌ FEHLER: Division durch 0 - Angefahrene Termine gesamt = 0")
    
    # 2. Terminvereinbarungsquote
    print("\n2️⃣  TERMINVEREINBARUNGSQUOTE (Appointment Scheduling Rate)")
    print("-"*80)
    print(f"   Formel: (Kunden terminiert / Getätigte Anrufe gesamt) × 100")
    print(f"   Werte:  ({kunden_terminiert} / {getaetigte_anrufe_gesamt}) × 100")
    
    if getaetigte_anrufe_gesamt > 0:
        terminquote = (kunden_terminiert / getaetigte_anrufe_gesamt) * 100
        print(f"   Ergebnis: {terminquote:.2f}%")
        print(f"   Bedeutung: Von {int(getaetigte_anrufe_gesamt)} Anrufen führten")
        print(f"              {int(kunden_terminiert)} zu einem Termin")
        
        # Threshold-Check
        threshold_low = 10.0
        threshold_high = 20.0
        if terminquote < threshold_low:
            print(f"   ⚠️  WARNUNG: Unter Mindestziel von {threshold_low}%")
        elif terminquote >= threshold_high:
            print(f"   ✅ ERFOLG: Ziel von {threshold_high}% übertroffen!")
        else:
            print(f"   ✅ Im Zielbereich ({threshold_low}% - {threshold_high}%)")
    else:
        print(f"   ❌ FEHLER: Division durch 0 - Getätigte Anrufe gesamt = 0")
    
    # 3. Termine-Anfahrquote
    print("\n3️⃣  TERMINE-ANFAHRQUOTE (Appointment Attendance Rate)")
    print("-"*80)
    print(f"   Formel: (Angefahrene Termine / Kunden terminiert) × 100")
    print(f"   Werte:  ({angefahrene_termine} / {kunden_terminiert}) × 100")
    
    if kunden_terminiert > 0:
        anfahrquote = (angefahrene_termine / kunden_terminiert) * 100
        print(f"   Ergebnis: {anfahrquote:.2f}%")
        print(f"   Bedeutung: Von {int(kunden_terminiert)} terminierten Kunden wurden")
        print(f"              {int(angefahrene_termine)} tatsächlich angefahren")
        
        # Threshold-Check
        threshold = 70.0
        if anfahrquote < threshold:
            print(f"   ⚠️  WARNUNG: Unter Mindestziel von {threshold}%")
            print(f"   💡 Hinweis: Fehlende Termine = {int(kunden_terminiert - angefahrene_termine)}")
        else:
            print(f"   ✅ Ziel erreicht (>= {threshold}%)")
    else:
        print(f"   ❌ FEHLER: Division durch 0 - Kunden terminiert = 0")
    
    print("\n" + "="*80)
    print("ZUSAMMENFASSUNG ALLER PROBLEME:")
    print("="*80)
    
    probleme = []
    
    # Check 1: Angefahrene Termine gesamt vs. angefahrene Termine
    if angefahrene_termine_gesamt != angefahrene_termine:
        probleme.append({
            'name': 'Inkonsistente Termine-Daten',
            'details': f"'Angefahrene Termine gesamt' ({angefahrene_termine_gesamt}) != "
                      f"'Angefahrene Termine' ({angefahrene_termine})",
            'fix': "Diese beiden Werte sollten identisch sein!"
        })
    
    # Check 2: Angefahrene Termine = 0
    if angefahrene_termine == 0 and kunden_terminiert > 0:
        probleme.append({
            'name': '0% Anfahrquote',
            'details': f"{int(kunden_terminiert)} Kunden terminiert, aber 0 Termine angefahren",
            'fix': f"'Angefahrene Termine' sollte auf {int(angefahrene_termine_gesamt)} gesetzt werden"
        })
    
    # Check 3: Verkauf > Angefahrene Termine gesamt
    if verkauf > angefahrene_termine_gesamt:
        probleme.append({
            'name': 'Verkauf > Angefahrene Termine',
            'details': f"Verkauf ({verkauf}) > Angefahrene Termine gesamt ({angefahrene_termine_gesamt})",
            'fix': "Logisch unmöglich - kann nicht mehr verkaufen als Termine angefahren!"
        })
    
    if probleme:
        for i, problem in enumerate(probleme, 1):
            print(f"\n❌ PROBLEM {i}: {problem['name']}")
            print(f"   Details: {problem['details']}")
            print(f"   Fix:     {problem['fix']}")
    else:
        print("\n✅ Keine Dateninkonsistenzen gefunden!")
    
    print("\n" + "="*80)
    print("EMPFOHLENE KORREKTUREN:")
    print("="*80)
    
    if angefahrene_termine == 0 and angefahrene_termine_gesamt > 0:
        print(f"\n1. Setze 'Angefahrene Termine' von {angefahrene_termine} auf {angefahrene_termine_gesamt}")
        print(f"   → Anfahrquote würde dann: {(angefahrene_termine_gesamt / kunden_terminiert * 100):.2f}% betragen")
    
    conn.close()


if __name__ == "__main__":
    diagnose_quota_calculations()
