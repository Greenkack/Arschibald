"""
Diagnose: Kamuran Dogancay Performance-Daten und Berechnungen
"""

import sqlite3
from datetime import date
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "app_data.db"

def diagnose_employee_calculations(employee_id: int, employee_name: str):
    """Diagnose für einen spezifischen Mitarbeiter."""
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=" * 80)
    print(f"DIAGNOSE: {employee_name} (ID: {employee_id})")
    print("=" * 80)
    
    # Hole ALLE Performance-Daten
    cursor.execute("""
        SELECT c.name, pd.value, pd.date
        FROM controlling_performance_data pd
        JOIN controlling_criteria c ON pd.criterion_id = c.id
        WHERE pd.employee_id = ?
        ORDER BY pd.date DESC, c.name
    """, (employee_id,))
    
    all_data = cursor.fetchall()
    
    if not all_data:
        print("\n❌ PROBLEM: KEINE Performance-Daten gefunden!")
        print("   Mitarbeiter hat keine einzigen Leistungsdaten in der Datenbank!")
        conn.close()
        return
    
    # Gruppiere nach Datum
    data_by_date = {}
    for row in all_data:
        date_str = row['date']
        if date_str not in data_by_date:
            data_by_date[date_str] = {}
        data_by_date[date_str][row['name']] = row['value']
    
    print(f"\n📅 Anzahl unterschiedlicher Daten: {len(data_by_date)}")
    print(f"📊 Gesamtanzahl Einträge: {len(all_data)}")
    
    # Zeige die letzten 3 Einträge
    print("\n" + "=" * 80)
    print("LETZTE 3 DATENEINTRÄGE:")
    print("=" * 80)
    
    for date_str in sorted(data_by_date.keys(), reverse=True)[:3]:
        data = data_by_date[date_str]
        print(f"\n📅 Datum: {date_str}")
        print("-" * 80)
        
        # Wichtige Werte extrahieren
        verkauf = data.get('Verkauf', 0)
        kunden_terminiert = data.get('Kunden terminiert', 0)
        angefahrene_termine = data.get('Angefahrene Termine', 0)
        angefahrene_termine_gesamt = data.get('Angefahrene Termine gesamt', 0)
        getaetigte_anrufe_gesamt = data.get('Getätigte Anrufe gesamt', 0)
        qc_bestanden = data.get('QC bestanden', 0)
        
        print(f"  Verkauf: {verkauf}")
        print(f"  Angefahrene Termine gesamt: {angefahrene_termine_gesamt}")
        print(f"  Kunden terminiert: {kunden_terminiert}")
        print(f"  Getätigte Anrufe gesamt: {getaetigte_anrufe_gesamt}")
        print(f"  Angefahrene Termine: {angefahrene_termine}")
        print(f"  QC bestanden: {qc_bestanden}")
        
        print("\n  📈 BERECHNUNGEN:")
        
        # 1. Abschlussquote
        if angefahrene_termine_gesamt > 0:
            abschlussquote = (verkauf / angefahrene_termine_gesamt) * 100
            print(f"  - Abschlussquote: ({verkauf} / {angefahrene_termine_gesamt}) × 100 = {abschlussquote:.2f}%")
        else:
            print(f"  - Abschlussquote: 0.00% (keine angefahrenen Termine)")
        
        # 2. Terminvereinbarungsquote
        if getaetigte_anrufe_gesamt > 0:
            terminquote = (kunden_terminiert / getaetigte_anrufe_gesamt) * 100
            print(f"  - Terminvereinbarungsquote: ({kunden_terminiert} / {getaetigte_anrufe_gesamt}) × 100 = {terminquote:.2f}%")
        else:
            print(f"  - Terminvereinbarungsquote: 0.00% (keine Anrufe)")
        
        # 3. Termine-Anfahrquote
        if kunden_terminiert > 0:
            anfahrquote = (angefahrene_termine / kunden_terminiert) * 100
            print(f"  - Termine-Anfahrquote: ({angefahrene_termine} / {kunden_terminiert}) × 100 = {anfahrquote:.2f}%")
        else:
            print(f"  - Termine-Anfahrquote: 0.00% (keine terminierten Kunden)")
        
        # 4. QC bestanden Quote
        if verkauf > 0:
            qc_quote = (qc_bestanden / verkauf) * 100
            print(f"  - QC bestanden Quote: ({qc_bestanden} / {verkauf}) × 100 = {qc_quote:.2f}%")
            if qc_quote > 100:
                print(f"    ⚠️ WARNUNG: QC bestanden ({qc_bestanden}) > Verkauf ({verkauf}) - DATENFEHLER!")
        else:
            print(f"  - QC bestanden Quote: 0.00% (kein Verkauf)")
        
        # Alle Werte anzeigen
        print("\n  📋 ALLE KRITERIEN:")
        for name, value in sorted(data.items()):
            if value > 0:
                print(f"    {name}: {value}")
    
    # Aggregiere ALLE Daten über alle Zeiträume
    print("\n" + "=" * 80)
    print("AGGREGIERTE WERTE (ALLE ZEITRÄUME):")
    print("=" * 80)
    
    aggregated = {}
    for date_str, data in data_by_date.items():
        for name, value in data.items():
            if name not in aggregated:
                aggregated[name] = 0
            aggregated[name] += value
    
    verkauf_total = aggregated.get('Verkauf', 0)
    angefahrene_termine_gesamt_total = aggregated.get('Angefahrene Termine gesamt', 0)
    kunden_terminiert_total = aggregated.get('Kunden terminiert', 0)
    getaetigte_anrufe_gesamt_total = aggregated.get('Getätigte Anrufe gesamt', 0)
    angefahrene_termine_total = aggregated.get('Angefahrene Termine', 0)
    qc_bestanden_total = aggregated.get('QC bestanden', 0)
    
    print(f"\nVerkauf (gesamt): {verkauf_total}")
    print(f"Angefahrene Termine gesamt: {angefahrene_termine_gesamt_total}")
    print(f"Kunden terminiert: {kunden_terminiert_total}")
    print(f"Getätigte Anrufe gesamt: {getaetigte_anrufe_gesamt_total}")
    print(f"QC bestanden: {qc_bestanden_total}")
    
    print("\n📈 AGGREGIERTE QUOTAS:")
    
    if angefahrene_termine_gesamt_total > 0:
        abschlussquote = (verkauf_total / angefahrene_termine_gesamt_total) * 100
        print(f"Abschlussquote: {abschlussquote:.2f}%")
    else:
        print(f"Abschlussquote: 0.00%")
    
    if getaetigte_anrufe_gesamt_total > 0:
        terminquote = (kunden_terminiert_total / getaetigte_anrufe_gesamt_total) * 100
        print(f"Terminvereinbarungsquote: {terminquote:.2f}%")
    else:
        print(f"Terminvereinbarungsquote: 0.00%")
    
    if kunden_terminiert_total > 0:
        anfahrquote = (angefahrene_termine_total / kunden_terminiert_total) * 100
        print(f"Termine-Anfahrquote: {anfahrquote:.2f}%")
    else:
        print(f"Termine-Anfahrquote: 0.00%")
    
    if verkauf_total > 0:
        qc_quote = (qc_bestanden_total / verkauf_total) * 100
        print(f"QC bestanden Quote: {qc_quote:.2f}%")
        if qc_quote > 100:
            print(f"⚠️ DATENFEHLER: QC bestanden ({qc_bestanden_total}) > Verkauf ({verkauf_total})")
    else:
        print(f"QC bestanden Quote: 0.00%")
    
    conn.close()


if __name__ == "__main__":
    # Diagnose für beide Mitarbeiter
    print("\n")
    diagnose_employee_calculations(1, "Mustafa Cetin")
    print("\n\n")
    diagnose_employee_calculations(3, "Kamuran Dogancay")
