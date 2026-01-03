"""
Tests für das CRM Reporting Engine Modul

Testet:
- Report-Generierung (Verkaufsübersicht, Conversion-Funnel, Lead-Quellen)
- Export-Funktionen (Excel, CSV, HTML)
- Report-Vorlagen-Speicherung und -Verwaltung
- Custom Report Builder

Requirements: 9.1, 9.2, 9.3
"""

import json
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import pytest

from crm.features.reporting_engine import (
    ReportingEngine,
    format_currency,
    format_percentage,
    get_available_tables,
    get_table_columns)


@pytest.fixture
def test_db():
    """Erstellt eine temporäre Test-Datenbank mit Beispieldaten."""
    # Temporäre Datei erstellen
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tabellen erstellen
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            company_name TEXT,
            email TEXT,
            phone_mobile TEXT,
            creation_date TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            project_name TEXT NOT NULL,
            project_status TEXT,
            offer_status TEXT DEFAULT 'draft',
            offer_sent_date DATE,
            offer_accepted_date DATE,
            offer_value REAL,
            rejection_reason TEXT,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE crm_leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            status TEXT NOT NULL,
            source TEXT,
            estimated_value REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Testdaten einfügen
    today = datetime.now()
    
    # Kunden
    customers = [
        ("Max", "Mustermann", "Musterfirma GmbH", "max@example.com", "0123456789", (today - timedelta(days=30)).strftime("%Y-%m-%d")),
        ("Anna", "Schmidt", "Schmidt Solar", "anna@example.com", "0987654321", (today - timedelta(days=60)).strftime("%Y-%m-%d")),
        ("Peter", "Müller", None, "peter@example.com", "0555555555", (today - timedelta(days=90)).strftime("%Y-%m-%d")),
    ]
    
    cursor.executemany(
        "INSERT INTO customers (first_name, last_name, company_name, email, phone_mobile, creation_date) VALUES (?, ?, ?, ?, ?, ?)",
        customers
    )
    
    # Projekte mit verschiedenen Status
    projects = [
        (1, "PV-Anlage Dach", "active", "accepted", (today - timedelta(days=20)).strftime("%Y-%m-%d"), 
         (today - timedelta(days=15)).strftime("%Y-%m-%d"), 25000.0, None),
        (1, "PV-Anlage Garage", "active", "sent", (today - timedelta(days=10)).strftime("%Y-%m-%d"), 
         None, 15000.0, None),
        (2, "Großanlage", "active", "accepted", (today - timedelta(days=45)).strftime("%Y-%m-%d"), 
         (today - timedelta(days=40)).strftime("%Y-%m-%d"), 50000.0, None),
        (2, "Erweiterung", "active", "rejected", (today - timedelta(days=25)).strftime("%Y-%m-%d"), 
         None, 20000.0, "Zu teuer"),
        (3, "Kleinanlage", "active", "sent", (today - timedelta(days=5)).strftime("%Y-%m-%d"), 
         None, 12000.0, None),
    ]
    
    cursor.executemany(
        """INSERT INTO projects (customer_id, project_name, project_status, offer_status, 
           offer_sent_date, offer_accepted_date, offer_value, rejection_reason) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        projects
    )
    
    # Leads mit verschiedenen Status und Quellen
    leads = [
        ("Firma A", "lead", "Website", 30000.0, (today - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")),
        ("Firma B", "qualified", "Website", 25000.0, (today - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")),
        ("Firma C", "proposal", "Empfehlung", 40000.0, (today - timedelta(days=15)).strftime("%Y-%m-%d %H:%M:%S")),
        ("Firma D", "won", "Empfehlung", 35000.0, (today - timedelta(days=20)).strftime("%Y-%m-%d %H:%M:%S")),
        ("Firma E", "lost", "Messe", 20000.0, (today - timedelta(days=25)).strftime("%Y-%m-%d %H:%M:%S")),
        ("Firma F", "lead", "Website", 15000.0, (today - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")),
        ("Firma G", "qualified", "Messe", 28000.0, (today - timedelta(days=35)).strftime("%Y-%m-%d %H:%M:%S")),
        ("Firma H", "won", "Website", 32000.0, (today - timedelta(days=40)).strftime("%Y-%m-%d %H:%M:%S")),
    ]
    
    cursor.executemany(
        "INSERT INTO crm_leads (company_name, status, source, estimated_value, created_at) VALUES (?, ?, ?, ?, ?)",
        leads
    )
    
    conn.commit()
    
    yield conn
    
    # Cleanup
    try:
        conn.close()
    except:
        pass
    
    # Windows-kompatibles Cleanup mit Retry
    import time
    for _ in range(3):
        try:
            Path(db_path).unlink()
            break
        except PermissionError:
            time.sleep(0.1)
        except FileNotFoundError:
            break


class TestReportingEngine:
    """Tests für die ReportingEngine Klasse."""
    
    def test_initialization(self, test_db):
        """Test: Engine-Initialisierung erstellt saved_reports Tabelle."""
        engine = ReportingEngine(test_db)
        
        cursor = test_db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='saved_reports'")
        result = cursor.fetchone()
        
        assert result is not None, "saved_reports Tabelle sollte erstellt werden"
    
    def test_sales_overview_report(self, test_db):
        """Test: Verkaufsübersicht Report wird korrekt generiert."""
        engine = ReportingEngine(test_db)
        
        # Report für letzte 90 Tage
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        
        result = engine.get_sales_overview(
            start_date=start_date,
            end_date=end_date,
            period="monthly"
        )
        
        assert result["success"] is True, "Report sollte erfolgreich sein"
        assert "data" in result, "Result sollte DataFrame enthalten"
        assert "summary" in result, "Result sollte Summary enthalten"
        assert "chart" in result, "Result sollte Chart enthalten"
        
        # Summary prüfen
        summary = result["summary"]
        assert summary["total_offers"] == 5, "Sollte 5 Angebote haben"
        assert summary["accepted_offers"] == 2, "Sollte 2 angenommene Angebote haben"
        assert summary["rejected_offers"] == 1, "Sollte 1 abgelehntes Angebot haben"
        assert summary["pending_offers"] == 2, "Sollte 2 ausstehende Angebote haben"
        assert summary["conversion_rate"] == 40.0, "Conversion Rate sollte 40% sein"
        assert summary["total_value"] == 122000.0, "Gesamtwert sollte 122000 sein"
    
    def test_sales_overview_no_data(self, test_db):
        """Test: Verkaufsübersicht mit leerem Zeitraum."""
        engine = ReportingEngine(test_db)
        
        # Zeitraum in der Zukunft (keine Daten)
        start_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
        
        result = engine.get_sales_overview(
            start_date=start_date,
            end_date=end_date,
            period="monthly"
        )
        
        assert result["success"] is False, "Report sollte fehlschlagen bei fehlenden Daten"
        assert "message" in result, "Sollte Fehlermeldung enthalten"
    
    def test_conversion_funnel_report(self, test_db):
        """Test: Conversion Funnel Report wird korrekt generiert."""
        engine = ReportingEngine(test_db)
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        
        result = engine.get_conversion_funnel(
            start_date=start_date,
            end_date=end_date
        )
        
        assert result["success"] is True, "Report sollte erfolgreich sein"
        assert "funnel_stages" in result, "Result sollte Funnel-Stufen enthalten"
        assert "conversion_rates" in result, "Result sollte Conversion-Raten enthalten"
        assert "chart" in result, "Result sollte Chart enthalten"
        
        # Funnel-Stufen prüfen
        funnel = result["funnel_stages"]
        assert funnel["lead"] == 2, "Sollte 2 Leads haben"
        assert funnel["qualified"] == 2, "Sollte 2 qualifizierte Leads haben"
        assert funnel["proposal"] == 1, "Sollte 1 Proposal haben"
        assert funnel["won"] == 2, "Sollte 2 gewonnene Leads haben"
        assert funnel["lost"] == 1, "Sollte 1 verlorenen Lead haben"
        
        # Conversion-Raten prüfen
        rates = result["conversion_rates"]
        assert "overall_conversion" in rates, "Sollte Gesamt-Conversion-Rate haben"
        assert rates["overall_conversion"] > 0, "Conversion-Rate sollte größer 0 sein"
    
    def test_lead_sources_report(self, test_db):
        """Test: Lead-Quellen Report wird korrekt generiert."""
        engine = ReportingEngine(test_db)
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        
        result = engine.get_lead_sources_report(
            start_date=start_date,
            end_date=end_date
        )
        
        assert result["success"] is True, "Report sollte erfolgreich sein"
        assert "data" in result, "Result sollte DataFrame enthalten"
        assert "chart" in result, "Result sollte Chart enthalten"
        
        # Daten prüfen
        df = result["data"]
        assert len(df) == 3, "Sollte 3 verschiedene Quellen haben (Website, Empfehlung, Messe)"
        
        # Website sollte die meisten Leads haben
        website_row = df[df['source'] == 'Website'].iloc[0]
        assert website_row['count'] == 4, "Website sollte 4 Leads haben"
        
        # Conversion-Raten sollten berechnet sein
        assert 'conversion_rate' in df.columns, "Sollte Conversion-Rate-Spalte haben"
    
    def test_custom_report_builder(self, test_db):
        """Test: Custom Report Builder funktioniert korrekt."""
        engine = ReportingEngine(test_db)
        
        # Einfacher Report: Alle Kunden
        result = engine.build_custom_report(
            table="customers",
            columns=["first_name", "last_name", "email"],
            limit=10
        )
        
        assert result["success"] is True, "Report sollte erfolgreich sein"
        assert "data" in result, "Result sollte DataFrame enthalten"
        assert result["row_count"] == 3, "Sollte 3 Kunden haben"
        
        df = result["data"]
        assert list(df.columns) == ["first_name", "last_name", "email"], "Sollte gewählte Spalten haben"
    
    def test_custom_report_with_filters(self, test_db):
        """Test: Custom Report mit Filtern."""
        engine = ReportingEngine(test_db)
        
        # Report mit Filter
        result = engine.build_custom_report(
            table="projects",
            columns=["project_name", "offer_status", "offer_value"],
            filters={"offer_status": "accepted"}
        )
        
        assert result["success"] is True, "Report sollte erfolgreich sein"
        assert result["row_count"] == 2, "Sollte 2 angenommene Angebote haben"
        
        df = result["data"]
        assert all(df['offer_status'] == 'accepted'), "Alle Zeilen sollten Status 'accepted' haben"
    
    def test_custom_report_with_grouping(self, test_db):
        """Test: Custom Report mit Gruppierung und Aggregation."""
        engine = ReportingEngine(test_db)
        
        # Report mit Gruppierung
        result = engine.build_custom_report(
            table="projects",
            columns=["offer_status", "offer_value"],
            group_by=["offer_status"],
            aggregations={"offer_value": "SUM"}
        )
        
        assert result["success"] is True, "Report sollte erfolgreich sein"
        
        df = result["data"]
        assert "offer_status" in df.columns, "Sollte Gruppierungs-Spalte haben"
        assert "offer_value_sum" in df.columns, "Sollte Aggregations-Spalte haben"


class TestExportFunctions:
    """Tests für Export-Funktionen."""
    
    def test_export_to_excel(self, test_db):
        """Test: Excel-Export funktioniert."""
        engine = ReportingEngine(test_db)
        
        # Testdaten erstellen
        df = pd.DataFrame({
            'Name': ['Test 1', 'Test 2'],
            'Wert': [100, 200],
            'Status': ['aktiv', 'inaktiv']
        })
        
        # Export
        excel_bytes = engine.export_to_excel(df, "test.xlsx")
        
        assert isinstance(excel_bytes, bytes), "Sollte Bytes zurückgeben"
        assert len(excel_bytes) > 0, "Excel-Datei sollte nicht leer sein"
        
        # Versuche Excel-Datei zu lesen (validiert Format)
        import io
        excel_io = io.BytesIO(excel_bytes)
        df_read = pd.read_excel(excel_io)
        
        assert len(df_read) == 2, "Sollte 2 Zeilen haben"
        assert list(df_read.columns) == ['Name', 'Wert', 'Status'], "Sollte korrekte Spalten haben"
    
    def test_export_to_csv(self, test_db):
        """Test: CSV-Export funktioniert."""
        engine = ReportingEngine(test_db)
        
        # Testdaten erstellen
        df = pd.DataFrame({
            'Name': ['Test 1', 'Test 2'],
            'Wert': [100, 200]
        })
        
        # Export
        csv_string = engine.export_to_csv(df)
        
        assert isinstance(csv_string, str), "Sollte String zurückgeben"
        assert 'Name,Wert' in csv_string, "Sollte Header enthalten"
        assert 'Test 1,100' in csv_string, "Sollte Daten enthalten"
    
    def test_export_chart_to_html(self, test_db):
        """Test: Chart HTML-Export funktioniert."""
        engine = ReportingEngine(test_db)
        
        # Einfaches Chart erstellen
        import plotly.graph_objects as go
        fig = go.Figure(data=[go.Bar(x=['A', 'B'], y=[1, 2])])
        
        # Export
        html_string = engine.export_chart_to_html(fig)
        
        assert isinstance(html_string, str), "Sollte String zurückgeben"
        assert '<html>' in html_string, "Sollte HTML enthalten"
        assert 'plotly' in html_string.lower(), "Sollte Plotly-Code enthalten"


class TestReportTemplates:
    """Tests für Report-Vorlagen-Verwaltung."""
    
    def test_save_report_template(self, test_db):
        """Test: Report-Vorlage speichern."""
        engine = ReportingEngine(test_db)
        
        config = {
            "table": "customers",
            "columns": ["first_name", "last_name"],
            "filters": {"email": "test@example.com"}
        }
        
        result = engine.save_report_template(
            name="Test Vorlage",
            report_type="custom",
            config=config,
            description="Eine Test-Vorlage",
            created_by="Test User"
        )
        
        assert result["success"] is True, "Speichern sollte erfolgreich sein"
        assert "template_id" in result, "Sollte Template-ID zurückgeben"
        assert result["template_id"] > 0, "Template-ID sollte positiv sein"
    
    def test_load_report_template(self, test_db):
        """Test: Report-Vorlage laden."""
        engine = ReportingEngine(test_db)
        
        # Erst speichern
        config = {
            "table": "projects",
            "columns": ["project_name", "offer_value"]
        }
        
        save_result = engine.save_report_template(
            name="Projekt Report",
            report_type="custom",
            config=config
        )
        
        template_id = save_result["template_id"]
        
        # Dann laden
        load_result = engine.load_report_template(template_id)
        
        assert load_result["success"] is True, "Laden sollte erfolgreich sein"
        assert "template" in load_result, "Sollte Template-Daten enthalten"
        
        template = load_result["template"]
        assert template["name"] == "Projekt Report", "Name sollte übereinstimmen"
        assert template["report_type"] == "custom", "Typ sollte übereinstimmen"
        assert template["config"]["table"] == "projects", "Config sollte übereinstimmen"
    
    def test_list_report_templates(self, test_db):
        """Test: Alle Report-Vorlagen auflisten."""
        engine = ReportingEngine(test_db)
        
        # Mehrere Vorlagen erstellen
        for i in range(3):
            engine.save_report_template(
                name=f"Vorlage {i+1}",
                report_type="custom",
                config={"test": i}
            )
        
        # Auflisten
        templates = engine.list_report_templates()
        
        assert len(templates) >= 3, "Sollte mindestens 3 Vorlagen haben"
        assert all('name' in t for t in templates), "Alle sollten Namen haben"
        assert all('report_type' in t for t in templates), "Alle sollten Typ haben"
    
    def test_delete_report_template(self, test_db):
        """Test: Report-Vorlage löschen."""
        engine = ReportingEngine(test_db)
        
        # Vorlage erstellen
        save_result = engine.save_report_template(
            name="Zu löschende Vorlage",
            report_type="custom",
            config={}
        )
        
        template_id = save_result["template_id"]
        
        # Löschen
        delete_result = engine.delete_report_template(template_id)
        
        assert delete_result["success"] is True, "Löschen sollte erfolgreich sein"
        
        # Versuche zu laden (sollte fehlschlagen)
        load_result = engine.load_report_template(template_id)
        assert load_result["success"] is False, "Laden sollte fehlschlagen nach Löschen"
    
    def test_delete_nonexistent_template(self, test_db):
        """Test: Nicht-existierende Vorlage löschen."""
        engine = ReportingEngine(test_db)
        
        result = engine.delete_report_template(99999)
        
        assert result["success"] is False, "Löschen sollte fehlschlagen"
        assert "nicht gefunden" in result["message"].lower(), "Sollte entsprechende Meldung haben"


class TestHelperFunctions:
    """Tests für Hilfsfunktionen."""
    
    def test_get_available_tables(self, test_db):
        """Test: Verfügbare Tabellen abrufen."""
        tables = get_available_tables(test_db)
        
        assert isinstance(tables, list), "Sollte Liste zurückgeben"
        assert "customers" in tables, "Sollte customers Tabelle enthalten"
        assert "projects" in tables, "Sollte projects Tabelle enthalten"
        assert "crm_leads" in tables, "Sollte crm_leads Tabelle enthalten"
    
    def test_get_table_columns(self, test_db):
        """Test: Tabellen-Spalten abrufen."""
        columns = get_table_columns(test_db, "customers")
        
        assert isinstance(columns, list), "Sollte Liste zurückgeben"
        assert "first_name" in columns, "Sollte first_name Spalte enthalten"
        assert "last_name" in columns, "Sollte last_name Spalte enthalten"
        assert "email" in columns, "Sollte email Spalte enthalten"
    
    def test_format_currency(self):
        """Test: Währungsformatierung."""
        assert format_currency(1000.50) == "€ 1.000,50"
        assert format_currency(25000) == "€ 25.000,00"
        assert format_currency(0) == "€ 0,00"
    
    def test_format_percentage(self):
        """Test: Prozent-Formatierung."""
        assert format_percentage(25.5) == "25,5%"
        assert format_percentage(100) == "100,0%"
        assert format_percentage(0) == "0,0%"


# Pytest Konfiguration
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
