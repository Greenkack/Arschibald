"""
Test-Tool für Controlling Quota-Berechnungen

Dieses Tool hilft beim Testen und Validieren der Quota-Berechnungen
im Controlling-System.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from controlling.analytics import AnalyticsEngine
from controlling.models import PerformanceData, Criterion, CalculationMethod, Base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from datetime import date


def create_test_session():
    """Erstellt eine Test-Datenbank-Session im Speicher."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    session = Session(engine)
    return session, engine


def create_test_criterion(session: Session, name: str):
    """Erstellt ein Test-Kriterium."""
    criterion = Criterion(
        name=name,
        description=f"Test criterion: {name}",
        calculation_method=CalculationMethod.SUM,
        is_standard=True
    )
    session.add(criterion)
    session.commit()
    return criterion


def create_test_performance_data(
    session: Session,
    criterion: Criterion,
    value: float,
    test_date: date = None
):
    """Erstellt einen Test-Performance-Datensatz."""
    if test_date is None:
        test_date = date.today()
    
    perf_data = PerformanceData(
        employee_id=1,  # Dummy ID
        criterion_id=criterion.id,
        value=value,
        date=test_date
    )
    session.add(perf_data)
    session.commit()
    return perf_data


def test_scenario_1():
    """
    Test-Szenario 1: Normale Werte (wie vom User beschrieben)
    
    Getätigte Anrufe gesamt: 30
    Kunden terminiert: 11
    Angefahrene Termine gesamt: 10
    Verkauf: 0
    QC bestanden: 2
    """
    print("\n" + "="*80)
    print("TEST-SZENARIO 1: Normale Testwerte")
    print("="*80)
    
    session, engine = create_test_session()
    analytics = AnalyticsEngine(session)
    
    # Kriterien erstellen
    criteria = {
        "Getätigte Anrufe gesamt": 30,
        "Kunden terminiert": 11,
        "Angefahrene Termine gesamt": 10,
        "Angefahrene Termine": 10,
        "Verkauf": 0,
        "QC bestanden": 2,
        "Nicht erreicht / neu terminieren": 1,
        "Storniert / kein Interesse": 0,
        "Technisch nicht machbar": 0,
        "Folgetermin gemacht": 0,
        "Angebot erhalten": 0,
        "Zu teuer gewesen": 0,
    }
    
    performance_data = []
    for crit_name, value in criteria.items():
        criterion = create_test_criterion(session, crit_name)
        perf = create_test_performance_data(session, criterion, value)
        performance_data.append(perf)
    
    # Quotas berechnen
    quotas = analytics.calculate_quotas(performance_data)
    
    print("\nBerechnete Quotas:")
    print("-" * 80)
    for name, value in quotas.items():
        print(f"{name:50s}: {value:7.2f}%")
    
    print("\nRatio-Beschreibungen:")
    print("-" * 80)
    for name, value in quotas.items():
        desc = analytics.calculate_ratio_description(value, name)
        print(f"{name:50s}: {desc}")
    
    # Erwartete Werte
    print("\n" + "="*80)
    print("ERWARTETE WERTE:")
    print("="*80)
    print(f"{'Terminvereinbarungsquote':50s}: {(11/30)*100:7.2f}% (11/30)")
    print(f"{'Quote der nicht erreichten Kunden':50s}: {(1/30)*100:7.2f}% (1/30)")
    print(f"{'Quote für QC bestanden':50s}: {'0.00':>7s}% (2/0 → Division durch 0)")
    print(f"{'Abschlussquote':50s}: {'0.00':>7s}% (0/10)")
    
    session.close()
    engine.dispose()


def test_scenario_2():
    """
    Test-Szenario 2: Korrekte Werte (mit Verkäufen)
    
    Getätigte Anrufe gesamt: 30
    Kunden terminiert: 11
    Angefahrene Termine gesamt: 10
    Verkauf: 3
    QC bestanden: 2
    """
    print("\n" + "="*80)
    print("TEST-SZENARIO 2: Mit tatsächlichen Verkäufen")
    print("="*80)
    
    session, engine = create_test_session()
    analytics = AnalyticsEngine(session)
    
    # Kriterien erstellen
    criteria = {
        "Getätigte Anrufe gesamt": 30,
        "Kunden terminiert": 11,
        "Angefahrene Termine gesamt": 10,
        "Angefahrene Termine": 10,
        "Verkauf": 3,  # KORRIGIERT: 3 statt 0
        "QC bestanden": 2,
        "Nicht erreicht / neu terminieren": 1,
        "Storniert / kein Interesse": 0,
        "Technisch nicht machbar": 0,
        "Folgetermin gemacht": 0,
        "Angebot erhalten": 0,
        "Zu teuer gewesen": 0,
    }
    
    performance_data = []
    for crit_name, value in criteria.items():
        criterion = create_test_criterion(session, crit_name)
        perf = create_test_performance_data(session, criterion, value)
        performance_data.append(perf)
    
    # Quotas berechnen
    quotas = analytics.calculate_quotas(performance_data)
    
    print("\nBerechnete Quotas:")
    print("-" * 80)
    for name, value in quotas.items():
        print(f"{name:50s}: {value:7.2f}%")
    
    print("\nRatio-Beschreibungen:")
    print("-" * 80)
    for name, value in quotas.items():
        desc = analytics.calculate_ratio_description(value, name)
        print(f"{name:50s}: {desc}")
    
    # Erwartete Werte
    print("\n" + "="*80)
    print("ERWARTETE WERTE:")
    print("="*80)
    print(f"{'Terminvereinbarungsquote':50s}: {(11/30)*100:7.2f}% (11/30)")
    print(f"{'Abschlussquote':50s}: {(3/10)*100:7.2f}% (3/10)")
    print(f"{'Quote für QC bestanden':50s}: {(2/3)*100:7.2f}% (2/3)")
    
    session.close()
    engine.dispose()


def test_scenario_3_problem():
    """
    Test-Szenario 3: PROBLEMFALL - Dezimalwerte statt ganzer Zahlen
    
    Verkauf: 0.3 (FALSCH! Sollte 3 sein)
    QC bestanden: 2
    
    Dies würde 666.67% ergeben!
    """
    print("\n" + "="*80)
    print("TEST-SZENARIO 3: PROBLEMFALL - Dezimalwerte (sollte Warnung erzeugen!)")
    print("="*80)
    
    session, engine = create_test_session()
    analytics = AnalyticsEngine(session)
    
    # Kriterien mit FALSCHEN Dezimalwerten
    criteria = {
        "Getätigte Anrufe gesamt": 30,
        "Kunden terminiert": 11,
        "Angefahrene Termine gesamt": 10,
        "Angefahrene Termine": 10,
        "Verkauf": 0.3,  # FEHLER! Sollte 3 sein
        "QC bestanden": 2,
        "Nicht erreicht / neu terminieren": 1,
        "Storniert / kein Interesse": 0,
        "Technisch nicht machbar": 0,
        "Folgetermin gemacht": 0,
        "Angebot erhalten": 0,
        "Zu teuer gewesen": 0,
    }
    
    performance_data = []
    for crit_name, value in criteria.items():
        criterion = create_test_criterion(session, crit_name)
        perf = create_test_performance_data(session, criterion, value)
        performance_data.append(perf)
    
    # Quotas berechnen (sollte Warnungen loggen!)
    print("\n>>> Achtung: Die folgende Berechnung sollte Validierungswarnungen erzeugen!\n")
    quotas = analytics.calculate_quotas(performance_data)
    
    print("\nBerechnete Quotas:")
    print("-" * 80)
    for name, value in quotas.items():
        indicator = " ⚠️" if value > 100 else ""
        print(f"{name:50s}: {value:7.2f}%{indicator}")
    
    print("\nRatio-Beschreibungen:")
    print("-" * 80)
    for name, value in quotas.items():
        desc = analytics.calculate_ratio_description(value, name)
        indicator = " ← FEHLER!" if "⚠️" in desc else ""
        print(f"{name:50s}: {desc}{indicator}")
    
    print("\n" + "="*80)
    print("PROBLEM IDENTIFIZIERT:")
    print("="*80)
    print(f"QC Quote = (2 / 0.3) × 100 = {(2/0.3)*100:.2f}%")
    print("Dies ist mathematisch korrekt für die FALSCHEN Eingabedaten!")
    print("Das Problem liegt bei den Eingabedaten, nicht der Berechnung!")
    
    session.close()
    engine.dispose()


if __name__ == "__main__":
    print("\n" + "="*80)
    print("CONTROLLING QUOTA CALCULATION TESTER")
    print("="*80)
    print("\nDieses Tool testet die Quota-Berechnungen mit verschiedenen Szenarien.")
    print("Achte auf Validierungswarnungen im Terminal!")
    
    # Alle Szenarien ausführen
    test_scenario_1()
    test_scenario_2()
    test_scenario_3_problem()
    
    print("\n" + "="*80)
    print("ZUSAMMENFASSUNG")
    print("="*80)
    print("""
GEFUNDENE PROBLEME:

1. RATIO-BESCHREIBUNGEN bei Quoten > 100%:
   - VORHER: "Jeder 0. Verkauf" (unmöglich!)
   - JETZT: "⚠️ 6.67× pro Verkauf (Daten prüfen!)"
   
2. DATENVALIDIERUNG:
   - Dezimalwerte bei Zählwerten werden jetzt gewarnt
   - Logische Inkonsistenzen (z.B. QC > Verkauf) werden erkannt
   
3. HAUPTURSACHE des 666.67% Fehlers:
   - Falsche Dateneingabe: 0.3 statt 3 für "Verkauf"
   - Die Berechnungslogik selbst ist KORREKT
   - Das Problem liegt bei den EINGABEDATEN

EMPFEHLUNGEN:

1. Prüfe die Datenquelle: Wo werden Performance-Daten eingegeben?
2. Validiere bei Eingabe: Nur ganze Zahlen für Zählwerte erlauben
3. Konsistenz prüfen: QC kann nie > Verkauf sein
4. Nutze die neuen Validierungswarnungen im Log

Führe diesen Test erneut aus nachdem du die Datenquelle korrigiert hast!
""")
    
    print("="*80 + "\n")
