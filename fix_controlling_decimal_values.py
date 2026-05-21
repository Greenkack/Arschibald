"""
Migration: Korrigiere fehlerhafte Dezimalwerte in Performance-Daten

Dieses Script findet und korrigiert alle Performance-Daten, die Dezimalwerte
für Zählkriterien haben (z.B. 0.3 statt 3 für "Verkauf").

PROBLEM:
- Quota-Berechnungen wie "QC bestanden" zeigen 666.67% weil Verkauf = 0.3 statt 3
- Ursache: Eingabe-UI erlaubte Dezimalzahlen, aber Kriterien sind Zählwerte

LÖSUNG:
- Rundet alle betroffenen Werte auf ganze Zahlen
- Loggt alle Änderungen zur Nachverfolgung
- Erstellt Backup vor Änderungen
"""

import sys
import sqlite3
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path(__file__).parent / "data" / "app_data.db"

# Kriterien, die nur ganze Zahlen haben sollten
INTEGER_ONLY_CRITERIA = [
    "Verkauf",
    "Kunden terminiert",
    "Angefahrene Termine",
    "Angefahrene Termine gesamt",
    "Getätigte Anrufe gesamt",
    "QC bestanden",
    "Storniert / kein Interesse",
    "Nicht erreicht / neu terminieren",
    "Technisch nicht machbar",
    "Nicht angefahrene Termine",
    "Folgetermin gemacht",
    "Zu teuer gewesen",
    "Angebot erhalten"
]


def find_decimal_values():
    """Finde alle Performance-Daten mit Dezimalwerten für Zählkriterien."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Finde alle betroffenen Datensätze
    placeholders = ','.join('?' * len(INTEGER_ONLY_CRITERIA))
    query = f"""
        SELECT 
            pd.id,
            pd.employee_id,
            pd.criterion_id,
            pd.value,
            pd.date,
            c.name as criterion_name,
            e.first_name || ' ' || e.last_name as employee_name
        FROM controlling_performance_data pd
        JOIN controlling_criteria c ON pd.criterion_id = c.id
        JOIN controlling_employees e ON pd.employee_id = e.id
        WHERE c.name IN ({placeholders})
        AND pd.value != CAST(pd.value AS INTEGER)
        AND pd.value > 0
        ORDER BY pd.date DESC, e.last_name, c.name
    """
    
    cursor.execute(query, INTEGER_ONLY_CRITERIA)
    results = cursor.fetchall()
    
    conn.close()
    return results


def create_backup():
    """Erstelle Backup der Performance-Daten."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.parent / f"app_data_backup_{timestamp}.db"
    
    logger.info(f"Erstelle Backup: {backup_path}")
    
    import shutil
    shutil.copy2(DB_PATH, backup_path)
    
    logger.info(f"✓ Backup erstellt: {backup_path}")
    return backup_path


def fix_decimal_values(dry_run=True):
    """
    Korrigiere Dezimalwerte zu ganzen Zahlen.
    
    Args:
        dry_run: Wenn True, zeige nur an was geändert würde ohne zu speichern
    """
    # Finde fehlerhafte Werte
    logger.info("Suche nach fehlerhaften Dezimalwerten...")
    decimal_values = find_decimal_values()
    
    if not decimal_values:
        logger.info("✓ Keine fehlerhaften Werte gefunden!")
        return
    
    logger.warning(f"⚠️ {len(decimal_values)} fehlerhafte Einträge gefunden!")
    
    print("\n" + "="*100)
    print("GEFUNDENE FEHLERHAFTE WERTE:")
    print("="*100)
    print(f"{'ID':<6} {'Mitarbeiter':<25} {'Kriterium':<35} {'Datum':<12} {'Aktuell':<10} {'Korrigiert':<10}")
    print("-"*100)
    
    changes = []
    for row in decimal_values:
        original_value = row['value']
        corrected_value = round(original_value)
        
        print(
            f"{row['id']:<6} "
            f"{row['employee_name']:<25} "
            f"{row['criterion_name']:<35} "
            f"{row['date']:<12} "
            f"{original_value:<10.2f} "
            f"{corrected_value:<10}"
        )
        
        changes.append({
            'id': row['id'],
            'employee_name': row['employee_name'],
            'criterion_name': row['criterion_name'],
            'date': row['date'],
            'original': original_value,
            'corrected': corrected_value,
            'difference': abs(original_value - corrected_value)
        })
    
    print("="*100)
    
    # Statistiken
    total_diff = sum(c['difference'] for c in changes)
    max_diff = max(c['difference'] for c in changes)
    avg_diff = total_diff / len(changes) if changes else 0
    
    print(f"\nSTATISTIKEN:")
    print(f"  Anzahl fehlerhafter Einträge: {len(changes)}")
    print(f"  Durchschnittliche Abweichung: {avg_diff:.4f}")
    print(f"  Maximale Abweichung: {max_diff:.4f}")
    
    # Zeige besonders kritische Fälle
    critical_cases = [c for c in changes if c['difference'] > 0.5]
    if critical_cases:
        print(f"\n⚠️ KRITISCHE FÄLLE (Abweichung > 0.5):")
        for case in critical_cases:
            print(
                f"  {case['employee_name']}: {case['criterion_name']} = "
                f"{case['original']:.2f} → {case['corrected']} "
                f"(Δ {case['difference']:.2f})"
            )
    
    if dry_run:
        print("\n" + "="*100)
        print("DRY RUN MODUS - Keine Änderungen gespeichert!")
        print("Führe das Script mit '--fix' aus, um die Änderungen anzuwenden:")
        print(f"  python {Path(__file__).name} --fix")
        print("="*100)
        return
    
    # Wirkliche Korrektur durchführen
    print("\n" + "="*100)
    print("KORREKTUR WIRD DURCHGEFÜHRT...")
    print("="*100)
    
    # Backup erstellen
    backup_path = create_backup()
    
    # Änderungen anwenden
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    corrected_count = 0
    for change in changes:
        cursor.execute(
            "UPDATE controlling_performance_data SET value = ? WHERE id = ?",
            (float(change['corrected']), change['id'])
        )
        corrected_count += 1
    
    conn.commit()
    conn.close()
    
    logger.info(f"✓ {corrected_count} Einträge korrigiert!")
    logger.info(f"✓ Backup gespeichert unter: {backup_path}")
    
    print("\n" + "="*100)
    print("KORREKTUR ABGESCHLOSSEN!")
    print("="*100)
    print(f"✓ {corrected_count} Performance-Daten korrigiert")
    print(f"✓ Backup: {backup_path}")
    print("\nNÄCHSTE SCHRITTE:")
    print("1. Führe die Quota-Berechnungen erneut aus")
    print("2. Prüfe ob die Werte jetzt korrekt sind")
    print("3. Falls Probleme auftreten, restore das Backup:")
    print(f"   copy \"{backup_path}\" \"{DB_PATH}\"")
    print("="*100)


def verify_fix():
    """Verifiziere dass keine Dezimalwerte mehr vorhanden sind."""
    logger.info("Verifiziere Korrektur...")
    decimal_values = find_decimal_values()
    
    if not decimal_values:
        logger.info("✓ VERIFIZIERUNG ERFOLGREICH - Keine Dezimalwerte gefunden!")
        return True
    else:
        logger.error(f"✗ VERIFIZIERUNG FEHLGESCHLAGEN - {len(decimal_values)} Dezimalwerte gefunden!")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Korrigiere fehlerhafte Dezimalwerte in Performance-Daten"
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Führe die Korrektur wirklich durch (ohne: nur Anzeige)'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verifiziere dass keine Dezimalwerte vorhanden sind'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*100)
    print("CONTROLLING PERFORMANCE DATA - DEZIMALWERT-KORREKTUR")
    print("="*100)
    print(f"Datenbank: {DB_PATH}")
    print(f"Modus: {'KORREKTUR' if args.fix else 'VORSCHAU (DRY RUN)'}")
    print("="*100 + "\n")
    
    if args.verify:
        # Nur verifizieren
        verify_fix()
    elif args.fix:
        # Wirkliche Korrektur
        fix_decimal_values(dry_run=False)
        # Automatische Verifizierung nach Korrektur
        print("\n")
        verify_fix()
    else:
        # Vorschau (Dry Run)
        fix_decimal_values(dry_run=True)
