"""
Diagnose-Tool: Zeige tatsächliche Performance-Daten und Quota-Berechnungen

Dieses Tool zeigt GENAU welche Daten für die Quota-Berechnungen verwendet werden.
"""

import sys
import sqlite3
from pathlib import Path
from datetime import date, timedelta
from collections import defaultdict

# Database path
DB_PATH = Path(__file__).parent / "data" / "app_data.db"


def get_all_employees():
    """Liste alle Mitarbeiter."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, first_name, last_name, city
        FROM controlling_employees
        WHERE is_active = 1
        ORDER BY last_name, first_name
    """)
    
    employees = cursor.fetchall()
    conn.close()
    return employees


def get_performance_data(employee_id, days_back=30):
    """Hole alle Performance-Daten für einen Mitarbeiter."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days_back)
    
    cursor.execute("""
        SELECT 
            pd.id,
            pd.date,
            pd.value,
            c.name as criterion_name
        FROM controlling_performance_data pd
        JOIN controlling_criteria c ON pd.criterion_id = c.id
        WHERE pd.employee_id = ?
        AND pd.date BETWEEN ? AND ?
        ORDER BY pd.date DESC, c.name
    """, (employee_id, start_date.isoformat(), end_date.isoformat()))
    
    data = cursor.fetchall()
    conn.close()
    return data, start_date, end_date


def aggregate_by_criterion(performance_data):
    """Aggregiere Daten nach Kriterium."""
    aggregated = defaultdict(float)
    
    for record in performance_data:
        aggregated[record['criterion_name']] += record['value']
    
    return dict(aggregated)


def calculate_quotas_manual(aggregated):
    """Berechne Quotas manuell aus aggregierten Daten."""
    verkauf = aggregated.get("Verkauf", 0)
    kunden_terminiert = aggregated.get("Kunden terminiert", 0)
    angefahrene_termine = aggregated.get("Angefahrene Termine", 0)
    angefahrene_termine_gesamt = aggregated.get("Angefahrene Termine gesamt", 0)
    getaetigte_anrufe_gesamt = aggregated.get("Getätigte Anrufe gesamt", 0)
    qc_bestanden = aggregated.get("QC bestanden", 0)
    nicht_erreicht = aggregated.get("Nicht erreicht / neu terminieren", 0)
    
    quotas = {}
    
    # Abschlussquote
    if angefahrene_termine_gesamt > 0:
        quotas["Abschlussquote"] = (verkauf / angefahrene_termine_gesamt) * 100
    else:
        quotas["Abschlussquote"] = 0.0
    
    # Terminvereinbarungsquote
    if getaetigte_anrufe_gesamt > 0:
        quotas["Terminvereinbarungsquote"] = (kunden_terminiert / getaetigte_anrufe_gesamt) * 100
    else:
        quotas["Terminvereinbarungsquote"] = 0.0
    
    # Termine-Anfahrquote
    if kunden_terminiert > 0:
        quotas["Termine-Anfahrquote"] = (angefahrene_termine / kunden_terminiert) * 100
    else:
        quotas["Termine-Anfahrquote"] = 0.0
    
    # Quote für QC bestanden
    if verkauf > 0:
        quotas["Quote für QC bestanden"] = (qc_bestanden / verkauf) * 100
    else:
        quotas["Quote für QC bestanden"] = 0.0
    
    # Quote der nicht erreichten Kunden
    if getaetigte_anrufe_gesamt > 0:
        quotas["Quote der nicht erreichten Kunden"] = (nicht_erreicht / getaetigte_anrufe_gesamt) * 100
    else:
        quotas["Quote der nicht erreichten Kunden"] = 0.0
    
    return quotas


def diagnose_employee(employee_id, days_back=30):
    """Vollständige Diagnose für einen Mitarbeiter."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Hole Mitarbeiter-Info
    cursor.execute("""
        SELECT 
            e.first_name || ' ' || e.last_name as full_name,
            p.name as position_name
        FROM controlling_employees e
        LEFT JOIN controlling_positions p ON e.position_id = p.id
        WHERE e.id = ?
    """, (employee_id,))
    
    employee = cursor.fetchone()
    conn.close()
    
    if not employee:
        print(f"❌ Mitarbeiter mit ID {employee_id} nicht gefunden!")
        return
    
    print("\n" + "="*100)
    print(f"DIAGNOSE: {employee['full_name']} ({employee['position_name']})")
    print("="*100)
    
    # Hole Performance-Daten
    performance_data, start_date, end_date = get_performance_data(employee_id, days_back)
    
    print(f"Zeitraum: {start_date} bis {end_date} ({days_back} Tage)")
    print(f"Datensätze gefunden: {len(performance_data)}")
    
    if not performance_data:
        print("\n⚠️ Keine Performance-Daten gefunden!")
        return
    
    # Zeige Rohdaten
    print("\n" + "-"*100)
    print("ROHDATEN:")
    print("-"*100)
    print(f"{'Datum':<12} {'Kriterium':<40} {'Wert':<10} {'Typ':<15}")
    print("-"*100)
    
    for record in performance_data:
        value_type = "Ganzzahl" if record['value'] == int(record['value']) else "⚠️ Dezimal"
        print(
            f"{record['date']:<12} "
            f"{record['criterion_name']:<40} "
            f"{record['value']:<10.2f} "
            f"{value_type:<15}"
        )
    
    # Aggregiere Daten
    aggregated = aggregate_by_criterion(performance_data)
    
    print("\n" + "-"*100)
    print("AGGREGIERTE DATEN (Summen pro Kriterium):")
    print("-"*100)
    print(f"{'Kriterium':<40} {'Summe':<10} {'Typ':<15}")
    print("-"*100)
    
    for criterion, value in sorted(aggregated.items()):
        value_type = "Ganzzahl" if value == int(value) else "⚠️ Dezimal"
        print(f"{criterion:<40} {value:<10.2f} {value_type:<15}")
    
    # Berechne Quotas
    quotas = calculate_quotas_manual(aggregated)
    
    print("\n" + "-"*100)
    print("BERECHNETE QUOTAS:")
    print("-"*100)
    print(f"{'Quote':<50} {'Wert':<15} {'Berechnung':<30}")
    print("-"*100)
    
    # Zeige kritische Werte für Diagnose
    verkauf = aggregated.get("Verkauf", 0)
    qc_bestanden = aggregated.get("QC bestanden", 0)
    angefahrene_termine_gesamt = aggregated.get("Angefahrene Termine gesamt", 0)
    kunden_terminiert = aggregated.get("Kunden terminiert", 0)
    getaetigte_anrufe_gesamt = aggregated.get("Getätigte Anrufe gesamt", 0)
    nicht_erreicht = aggregated.get("Nicht erreicht / neu terminieren", 0)
    
    calculations = {
        "Abschlussquote": f"{verkauf:.1f} / {angefahrene_termine_gesamt:.1f}",
        "Terminvereinbarungsquote": f"{kunden_terminiert:.1f} / {getaetigte_anrufe_gesamt:.1f}",
        "Quote für QC bestanden": f"{qc_bestanden:.1f} / {verkauf:.1f}",
        "Quote der nicht erreichten Kunden": f"{nicht_erreicht:.1f} / {getaetigte_anrufe_gesamt:.1f}"
    }
    
    for name, value in quotas.items():
        indicator = " ⚠️" if value > 100 else ""
        calculation = calculations.get(name, "")
        print(f"{name:<50} {value:>7.2f}%{indicator:<6} {calculation:<30}")
    
    # Zeige Probleme
    print("\n" + "="*100)
    print("DIAGNOSE-ERGEBNISSE:")
    print("="*100)
    
    problems = []
    
    # Check 1: Dezimalwerte
    decimal_values = [(k, v) for k, v in aggregated.items() if v != int(v) and v > 0]
    if decimal_values:
        problems.append("❌ DEZIMALWERTE GEFUNDEN:")
        for crit, val in decimal_values:
            problems.append(f"   - {crit}: {val:.4f} (sollte {round(val)} sein)")
    
    # Check 2: QC > Verkauf
    if qc_bestanden > verkauf and verkauf > 0:
        problems.append(f"❌ LOGIKFEHLER: QC bestanden ({qc_bestanden}) > Verkauf ({verkauf})")
    
    # Check 3: Quoten > 100%
    high_quotas = [(k, v) for k, v in quotas.items() if v > 100]
    if high_quotas:
        problems.append("❌ UNMÖGLICHE QUOTEN (> 100%):")
        for name, val in high_quotas:
            problems.append(f"   - {name}: {val:.2f}%")
    
    # Check 4: Verkauf = 0 aber QC > 0
    if verkauf == 0 and qc_bestanden > 0:
        problems.append(f"❌ INKONSISTENZ: QC bestanden = {qc_bestanden}, aber Verkauf = 0")
    
    if problems:
        for problem in problems:
            print(problem)
    else:
        print("✅ Keine Probleme gefunden! Alle Daten sind konsistent.")
    
    print("="*100)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Diagnose-Tool für Controlling Performance-Daten"
    )
    parser.add_argument(
        '--employee-id',
        type=int,
        help='Mitarbeiter-ID für Diagnose'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Anzahl Tage zurück (default: 30)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='Liste alle Mitarbeiter'
    )
    
    args = parser.parse_args()
    
    if args.list:
        # Liste alle Mitarbeiter
        employees = get_all_employees()
        print("\n" + "="*80)
        print("VERFÜGBARE MITARBEITER:")
        print("="*80)
        print(f"{'ID':<6} {'Name':<30} {'Stadt':<20}")
        print("-"*80)
        for emp in employees:
            name = f"{emp['first_name']} {emp['last_name']}"
            print(f"{emp['id']:<6} {name:<30} {emp['city']:<20}")
        print("="*80)
        print(f"\nFühre Diagnose aus mit: python {Path(__file__).name} --employee-id <ID>")
    elif args.employee_id:
        # Diagnose für spezifischen Mitarbeiter
        diagnose_employee(args.employee_id, args.days)
    else:
        # Keine Argumente - zeige Hilfe
        parser.print_help()
        print("\n" + "="*80)
        print("BEISPIELE:")
        print("="*80)
        print(f"  python {Path(__file__).name} --list")
        print(f"  python {Path(__file__).name} --employee-id 1")
        print(f"  python {Path(__file__).name} --employee-id 1 --days 7")
        print("="*80)
