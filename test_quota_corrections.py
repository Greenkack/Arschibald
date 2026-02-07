"""
Test für korrigierte Controlling-Quotenberechnungen
Verifiziert:
1. Call Agent hat KEINE "Termine-Anfahrquote"
2. "QC bestanden Quote" für Call Agent = QC bestanden / Kunden terminiert
3. Verkäufer hat weiterhin "Termine-Anfahrquote"
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from controlling.analytics import AnalyticsEngine
from controlling.models import Criterion, PerformanceData, Position, Employee
from datetime import date


class MockCriterion:
    def __init__(self, name):
        self.name = name


class MockPerformanceData:
    def __init__(self, criterion_name, value):
        self.criterion = MockCriterion(criterion_name)
        self.value = value


def test_call_agent_quotas():
    """Test Call Agent: KEINE Anfahrquote, korrekte QC-Quote"""
    print("\n" + "="*70)
    print("TEST 1: Call Agent Quotas")
    print("="*70)
    
    # Mock DB session
    class MockDB:
        pass
    
    analytics = AnalyticsEngine(MockDB())
    
    # Simuliere Call Agent Daten
    performance_data = [
        MockPerformanceData("Kunden terminiert", 100),
        MockPerformanceData("Getätigte Anrufe gesamt", 500),
        MockPerformanceData("QC bestanden", 14),
        MockPerformanceData("Verkauf", 10),
    ]
    
    quotas = analytics.calculate_quotas(performance_data, position_name="Call Agent")
    
    print(f"\nBerechnete Quotas für Call Agent:")
    for quota_name, quota_value in sorted(quotas.items()):
        print(f"  {quota_name}: {quota_value:.2f}%")
    
    # Verifizierungen
    print("\n--- Verifizierung ---")
    
    # 1. Termine-Anfahrquote sollte NICHT existieren
    if "Termine-Anfahrquote" in quotas:
        print("❌ FEHLER: Call Agent sollte KEINE 'Termine-Anfahrquote' haben!")
        return False
    else:
        print("✅ OK: 'Termine-Anfahrquote' nicht vorhanden (korrekt)")
    
    # 2. QC bestanden Quote = QC bestanden / Kunden terminiert
    expected_qc_quote = (14 / 100) * 100  # 14.00%
    actual_qc_quote = quotas.get("QC bestanden Quote", 0)
    
    if abs(actual_qc_quote - expected_qc_quote) < 0.01:
        print(f"✅ OK: 'QC bestanden Quote' = {actual_qc_quote:.2f}% (14 / 100 = 14.00%)")
    else:
        print(f"❌ FEHLER: 'QC bestanden Quote' = {actual_qc_quote:.2f}%, erwartet {expected_qc_quote:.2f}%")
        return False
    
    # 3. Terminvereinbarungsquote = Kunden terminiert / Getätigte Anrufe
    expected_termin_quote = (100 / 500) * 100  # 20.00%
    actual_termin_quote = quotas.get("Terminvereinbarungsquote", 0)
    
    if abs(actual_termin_quote - expected_termin_quote) < 0.01:
        print(f"✅ OK: 'Terminvereinbarungsquote' = {actual_termin_quote:.2f}% (100 / 500 = 20.00%)")
    else:
        print(f"❌ FEHLER: 'Terminvereinbarungsquote' = {actual_termin_quote:.2f}%, erwartet {expected_termin_quote:.2f}%")
        return False
    
    return True


def test_verkaeufer_quotas():
    """Test Verkäufer: HAT Anfahrquote, QC-Quote mit Verkauf"""
    print("\n" + "="*70)
    print("TEST 2: Verkäufer Quotas")
    print("="*70)
    
    # Mock DB session
    class MockDB:
        pass
    
    analytics = AnalyticsEngine(MockDB())
    
    # Simuliere Verkäufer Daten
    performance_data = [
        MockPerformanceData("Kunden terminiert", 50),
        MockPerformanceData("Angefahrene Termine", 40),
        MockPerformanceData("Verkauf", 15),
        MockPerformanceData("QC bestanden", 12),
        MockPerformanceData("Getätigte Anrufe gesamt", 200),
    ]
    
    quotas = analytics.calculate_quotas(performance_data, position_name="Verkäufer")
    
    print(f"\nBerechnete Quotas für Verkäufer:")
    for quota_name, quota_value in sorted(quotas.items()):
        print(f"  {quota_name}: {quota_value:.2f}%")
    
    # Verifizierungen
    print("\n--- Verifizierung ---")
    
    # 1. Termine-Anfahrquote sollte existieren
    if "Termine-Anfahrquote" not in quotas:
        print("❌ FEHLER: Verkäufer sollte 'Termine-Anfahrquote' haben!")
        return False
    else:
        expected_anfahrquote = (40 / 50) * 100  # 80.00%
        actual_anfahrquote = quotas.get("Termine-Anfahrquote", 0)
        if abs(actual_anfahrquote - expected_anfahrquote) < 0.01:
            print(f"✅ OK: 'Termine-Anfahrquote' = {actual_anfahrquote:.2f}% (40 / 50 = 80.00%)")
        else:
            print(f"❌ FEHLER: 'Termine-Anfahrquote' = {actual_anfahrquote:.2f}%, erwartet {expected_anfahrquote:.2f}%")
            return False
    
    # 2. QC bestanden Quote = QC bestanden / Verkauf (für Verkäufer!)
    expected_qc_quote = (12 / 15) * 100  # 80.00%
    actual_qc_quote = quotas.get("QC bestanden Quote", 0)
    
    if abs(actual_qc_quote - expected_qc_quote) < 0.01:
        print(f"✅ OK: 'QC bestanden Quote' = {actual_qc_quote:.2f}% (12 / 15 = 80.00%)")
    else:
        print(f"❌ FEHLER: 'QC bestanden Quote' = {actual_qc_quote:.2f}%, erwartet {expected_qc_quote:.2f}%")
        return False
    
    # 3. Abschlussquote = Verkauf / Angefahrene Termine (für Verkäufer!)
    expected_abschluss = (15 / 40) * 100  # 37.50%
    actual_abschluss = quotas.get("Abschlussquote", 0)
    
    if abs(actual_abschluss - expected_abschluss) < 0.01:
        print(f"✅ OK: 'Abschlussquote' = {actual_abschluss:.2f}% (15 / 40 = 37.50%)")
    else:
        print(f"❌ FEHLER: 'Abschlussquote' = {actual_abschluss:.2f}%, erwartet {expected_abschluss:.2f}%")
        return False
    
    return True


def main():
    print("\n" + "="*70)
    print("CONTROLLING QUOTENBERECHNUNG - KORREKTHEITS-TEST")
    print("="*70)
    
    test1_ok = test_call_agent_quotas()
    test2_ok = test_verkaeufer_quotas()
    
    print("\n" + "="*70)
    print("ZUSAMMENFASSUNG")
    print("="*70)
    
    if test1_ok and test2_ok:
        print("✅ ALLE TESTS BESTANDEN!")
        print("\n✓ Call Agent: Keine Anfahrquote ✓")
        print("✓ Call Agent: QC bestanden Quote = QC bestanden / Kunden terminiert ✓")
        print("✓ Verkäufer: Hat Anfahrquote ✓")
        print("✓ Verkäufer: QC bestanden Quote = QC bestanden / Verkauf ✓")
        return 0
    else:
        print("❌ TESTS FEHLGESCHLAGEN!")
        if not test1_ok:
            print("  - Call Agent Tests fehlgeschlagen")
        if not test2_ok:
            print("  - Verkäufer Tests fehlgeschlagen")
        return 1


if __name__ == "__main__":
    exit(main())
