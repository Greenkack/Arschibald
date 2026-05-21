"""
Test-Skript für Controlling Erweiterte Features

Demonstriert alle 4 neuen Features:
1. Team-Auswertung
2. Mitarbeiter-Vergleich  
3. PDF Bytes Export
4. PDF-Farbeinstellungen
"""

import sys
from pathlib import Path
from datetime import date, timedelta

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.core.database import SessionLocal
from controlling.models import Employee, Position
from controlling.team_analytics import TeamAnalytics
from controlling.report_generator import ReportGenerator
from controlling.pdf_config import get_pdf_config_manager, PDFColorScheme


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Will be closed manually


def test_pdf_color_config():
    """Test PDF-Farbkonfiguration."""
    print("\n" + "="*80)
    print("TEST 1: PDF-FARBKONFIGURATION")
    print("="*80)
    
    config_manager = get_pdf_config_manager()
    
    # Aktuelles Schema
    print("\n📋 Aktuelles Farbschema:")
    current = config_manager.color_scheme
    print(f"  Primärfarbe: {current.primary_color}")
    print(f"  Sekundärfarbe: {current.secondary_color}")
    print(f"  Tabellen-Header: {current.table_header_bg}")
    print(f"  Tabellenzeilen: {current.table_row_bg}")
    
    # Vordefinierte Schemata
    print("\n🎨 Vordefinierte Schemata:")
    schemes = config_manager.get_predefined_schemes()
    for i, name in enumerate(schemes.keys(), 1):
        scheme = schemes[name]
        print(f"  {i}. {name}: {scheme.primary_color}")
    
    # Test: Schema wechseln
    print("\n🔄 Test: Wechsel zu 'Grün' Schema...")
    if config_manager.apply_predefined_scheme("Grün"):
        print("  ✅ Erfolgreich!")
        new_scheme = config_manager.color_scheme
        print(f"  Neue Primärfarbe: {new_scheme.primary_color}")
    else:
        print("  ❌ Fehler!")
    
    # Zurück zu Standard
    print("\n🔄 Zurück zu Standard...")
    config_manager.reset_to_default()
    print("  ✅ Auf Standard zurückgesetzt!")
    
    print("\n✅ PDF-Farbkonfiguration Test abgeschlossen!")


def test_team_analytics():
    """Test Team-Auswertung."""
    print("\n" + "="*80)
    print("TEST 2: TEAM-AUSWERTUNG")
    print("="*80)
    
    db = get_db()
    try:
        # Hole erste Position
        position = db.query(Position).first()
        
        if not position:
            print("  ⚠️  Keine Positionen gefunden - Test übersprungen")
            return
        
        print(f"\n📊 Erstelle Team-Auswertung für Position: {position.name}")
        
        # Zeitraum: Letzte 30 Tage
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        print(f"  Zeitraum: {start_date} bis {end_date}")
        
        team_analytics = TeamAnalytics(db)
        
        try:
            team_data = team_analytics.generate_team_report(
                position_id=position.id,
                start_date=start_date,
                end_date=end_date,
                include_inactive=False
            )
            
            print(f"\n✅ Team-Auswertung erstellt!")
            print(f"  Anzahl Mitarbeiter: {team_data['employee_count']}")
            
            # Team-Quotas
            if team_data['employee_count'] > 0:
                print("\n📈 Team-Quotas:")
                for quota_name, quota_value in team_data['team_quotas'].items():
                    print(f"  {quota_name}: {quota_value:.2f}%")
                
                # Statistiken
                stats = team_data.get('statistics', {}).get('quota_statistics', {})
                if stats:
                    print("\n📊 Statistiken (Abschlussquote):")
                    if 'Abschlussquote' in stats:
                        s = stats['Abschlussquote']
                        print(f"  Durchschnitt: {s['average']:.2f}%")
                        print(f"  Bester: {s['best_performer']} ({s['max']:.2f}%)")
                        print(f"  Schlechtester: {s['worst_performer']} ({s['min']:.2f}%)")
                
                # PDF-Export Test
                print("\n📄 Teste PDF-Export...")
                report_gen = ReportGenerator(db)
                pdf_bytes = report_gen.export_team_report_to_pdf(team_data)
                print(f"  ✅ PDF erstellt! Größe: {len(pdf_bytes)} Bytes")
                
                # Optional: PDF speichern
                # output_path = Path("test_team_auswertung.pdf")
                # output_path.write_bytes(pdf_bytes)
                # print(f"  💾 PDF gespeichert: {output_path}")
            
            print("\n✅ Team-Auswertung Test abgeschlossen!")
        
        except Exception as e:
            print(f"  ❌ Fehler: {e}")
    finally:
        db.close()


def test_comparison():
    """Test Mitarbeiter-Vergleich."""
    print("\n" + "="*80)
    print("TEST 3: MITARBEITER-VERGLEICH")
    print("="*80)
    
    db = get_db()
    try:
        # Hole erste Position
        position = db.query(Position).first()
        
        if not position:
            print("  ⚠️  Keine Positionen gefunden - Test übersprungen")
            return
        
        # Hole Mitarbeiter dieser Position
        employees = db.query(Employee).filter(
            Employee.position_id == position.id,
            Employee.is_active == True
        ).limit(3).all()
        
        if len(employees) < 2:
            print(f"  ⚠️  Nur {len(employees)} Mitarbeiter gefunden - mindestens 2 erforderlich")
            return
        
        print(f"\n🔍 Erstelle Vergleich für {len(employees)} Mitarbeiter:")
        for emp in employees:
            print(f"  - {emp.full_name}")
        
        # Zeitraum: Letzte 30 Tage
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        team_analytics = TeamAnalytics(db)
        
        try:
            comparison_data = team_analytics.generate_comparison_report(
                employee_ids=[emp.id for emp in employees],
                start_date=start_date,
                end_date=end_date
            )
            
            print(f"\n✅ Vergleich erstellt!")
            
            # Rankings
            rankings = comparison_data.get('comparison_statistics', {}).get('rankings', {})
            
            if rankings and 'Abschlussquote' in rankings:
                print("\n🏆 Ranking - Abschlussquote:")
                for item in rankings['Abschlussquote']:
                    emoji = ""
                    if item['rank'] == 1:
                        emoji = "🥇"
                    elif item['rank'] == 2:
                        emoji = "🥈"
                    elif item['rank'] == 3:
                        emoji = "🥉"
                    
                    print(f"  {emoji} {item['rank']}. {item['name']}: {item['value']:.2f}%")
            
            # Unterschiede
            differences = comparison_data.get('comparison_statistics', {}).get('differences', {})
            
            if differences and 'Abschlussquote' in differences:
                print("\n📊 Leistungsunterschied - Abschlussquote:")
                diff = differences['Abschlussquote']
                print(f"  Bester: {diff['leader']} ({diff['leader_value']:.2f}%)")
                print(f"  Schlechtester: {diff['last']} ({diff['last_value']:.2f}%)")
                print(f"  Differenz: {diff['difference']:.2f}%")
            
            # PDF-Export Test
            print("\n📄 Teste PDF-Export...")
            report_gen = ReportGenerator(db)
            pdf_bytes = report_gen.export_comparison_report_to_pdf(comparison_data)
            print(f"  ✅ PDF erstellt! Größe: {len(pdf_bytes)} Bytes")
            
            print("\n✅ Mitarbeiter-Vergleich Test abgeschlossen!")
        
        except Exception as e:
            print(f"  ❌ Fehler: {e}")
    finally:
        db.close()


def main():
    """Führe alle Tests aus."""
    print("\n" + "="*80)
    print("CONTROLLING - ERWEITERTE FEATURES - TESTLAUF")
    print("="*80)
    print("\nTeste alle 4 neuen Features:")
    print("1. Team-Auswertung")
    print("2. Mitarbeiter-Vergleich")
    print("3. PDF Bytes Export")
    print("4. PDF-Farbeinstellungen")
    
    # Test 1: PDF-Farben
    test_pdf_color_config()
    
    # Test 2: Team-Auswertung (inkl. PDF Export)
    test_team_analytics()
    
    # Test 3: Mitarbeiter-Vergleich (inkl. PDF Export)
    test_comparison()
    
    # Zusammenfassung
    print("\n" + "="*80)
    print("✅ ALLE TESTS ABGESCHLOSSEN!")
    print("="*80)
    print("\nNächste Schritte:")
    print("1. Streamlit-App starten: streamlit run controlling_advanced_features_ui.py")
    print("2. Features in UI testen")
    print("3. PDFs mit verschiedenen Farbschemata exportieren")
    print("\nDokumentation:")
    print("- CONTROLLING_ERWEITERTE_FEATURES.md")
    print("- CONTROLLING_SCHNELLSTART.md")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
