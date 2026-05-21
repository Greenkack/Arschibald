"""
Logik-Korrektur für Controlling Performance-Daten

Dieses Tool korrigiert logisch unmögliche Datensätze:
- QC bestanden > Verkauf → QC = min(QC, Verkauf)
- Kunden terminiert > Anrufe → Warnung
- Fehlende kritische Werte → Hinzufügen/Schätzen
"""

import sys
import sqlite3
from pathlib import Path
from datetime import date

# Database path
DB_PATH = Path(__file__).parent / "data" / "app_data.db"


def find_logic_errors():
    """Finde alle Performance-Daten mit logischen Inkonsistenzen."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Hole alle Performance-Daten gruppiert nach employee_id und date
    cursor.execute("""
        SELECT 
            pd.employee_id,
            pd.date,
            e.first_name || ' ' || e.last_name as employee_name,
            GROUP_CONCAT(c.name || ':' || pd.value) as data
        FROM controlling_performance_data pd
        JOIN controlling_employees e ON pd.employee_id = e.id
        JOIN controlling_criteria c ON pd.criterion_id = c.id
        GROUP BY pd.employee_id, pd.date
        ORDER BY pd.date DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    errors = []
    
    for row in rows:
        # Parse die Daten
        data_dict = {}
        for item in row['data'].split(','):
            if ':' in item:
                name, value = item.split(':', 1)
                data_dict[name] = float(value)
        
        verkauf = data_dict.get('Verkauf', 0)
        qc_bestanden = data_dict.get('QC bestanden', 0)
        kunden_terminiert = data_dict.get('Kunden terminiert', 0)
        anrufe_gesamt = data_dict.get('Getätigte Anrufe gesamt', 0)
        
        # Check 1: QC > Verkauf
        if qc_bestanden > verkauf and verkauf > 0:
            errors.append({
                'type': 'QC_GT_VERKAUF',
                'employee_id': row['employee_id'],
                'employee_name': row['employee_name'],
                'date': row['date'],
                'verkauf': verkauf,
                'qc_bestanden': qc_bestanden,
                'message': f"QC bestanden ({qc_bestanden}) > Verkauf ({verkauf})"
            })
        
        # Check 2: Terminierte > Anrufe
        if kunden_terminiert > anrufe_gesamt and anrufe_gesamt > 0:
            errors.append({
                'type': 'TERMINIERT_GT_ANRUFE',
                'employee_id': row['employee_id'],
                'employee_name': row['employee_name'],
                'date': row['date'],
                'kunden_terminiert': kunden_terminiert,
                'anrufe_gesamt': anrufe_gesamt,
                'message': f"Kunden terminiert ({kunden_terminiert}) > Anrufe ({anrufe_gesamt})"
            })
    
    return errors


def fix_logic_errors(dry_run=True):
    """
    Korrigiere logische Inkonsistenzen.
    
    Strategie:
    - Wenn QC > Verkauf: Setze QC = Verkauf (konservativ)
    - Wenn Terminiert > Anrufe: Nur Warnung, keine automatische Korrektur
    """
    errors = find_logic_errors()
    
    if not errors:
        print("\n✅ Keine logischen Inkonsistenzen gefunden!")
        return
    
    print("\n" + "="*100)
    print(f"⚠️ {len(errors)} LOGISCHE INKONSISTENZEN GEFUNDEN!")
    print("="*100)
    
    for err in errors:
        print(f"\n{err['employee_name']} - {err['date']}:")
        print(f"  {err['message']}")
        
        if err['type'] == 'QC_GT_VERKAUF':
            print(f"  → VORGESCHLAGENE KORREKTUR: Setze QC bestanden von {err['qc_bestanden']} auf {err['verkauf']}")
        elif err['type'] == 'TERMINIERT_GT_ANRUFE':
            print(f"  → WARNUNG: Bitte manuell prüfen!")
    
    if dry_run:
        print("\n" + "="*100)
        print("DRY RUN MODUS - Keine Änderungen gespeichert!")
        print("Führe das Script mit '--fix' aus, um die Korrekturen anzuwenden:")
        print(f"  python {Path(__file__).name} --fix")
        print("="*100)
        return
    
    # Wirkliche Korrektur
    print("\n" + "="*100)
    print("KORREKTUR WIRD DURCHGEFÜHRT...")
    print("="*100)
    
    # Backup erstellen
    from datetime import datetime
    import shutil
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.parent / f"app_data_backup_logic_{timestamp}.db"
    shutil.copy2(DB_PATH, backup_path)
    print(f"✓ Backup erstellt: {backup_path}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    fixed_count = 0
    
    for err in errors:
        if err['type'] == 'QC_GT_VERKAUF':
            # Korrigiere QC bestanden
            cursor.execute("""
                UPDATE controlling_performance_data
                SET value = ?
                WHERE employee_id = ?
                AND date = ?
                AND criterion_id = (SELECT id FROM controlling_criteria WHERE name = 'QC bestanden')
            """, (err['verkauf'], err['employee_id'], err['date']))
            
            fixed_count += 1
            print(f"✓ Korrigiert: {err['employee_name']} - {err['date']}: QC = {err['verkauf']}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*100)
    print(f"✓ {fixed_count} Inkonsistenzen korrigiert!")
    print(f"✓ Backup: {backup_path}")
    print("="*100)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Korrigiere logische Inkonsistenzen in Performance-Daten"
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Führe die Korrektur wirklich durch (ohne: nur Anzeige)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*100)
    print("CONTROLLING PERFORMANCE DATA - LOGIK-KORREKTUR")
    print("="*100)
    print(f"Datenbank: {DB_PATH}")
    print(f"Modus: {'KORREKTUR' if args.fix else 'VORSCHAU (DRY RUN)'}")
    print("="*100)
    
    fix_logic_errors(dry_run=not args.fix)
