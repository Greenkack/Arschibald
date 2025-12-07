# crm/features/test_dashboard_widgets.py
"""
Unit Tests für Dashboard Widget System
Testet Widget-Rendering, Auto-Refresh und Konfiguration

Author: Kiro AI
Version: 1.0
Date: 2025-01-14
"""

import json
import sqlite3
import tempfile
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def test_db():
    """Erstellt eine temporäre Test-Datenbank"""
    with tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.db') as f:
        db_path = f.name

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Erstelle notwendige Tabellen
    cursor.execute("""
        CREATE TABLE crm_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'open',
            priority TEXT DEFAULT 'medium',
            due_date DATE,
            customer_id INTEGER,
            project_id INTEGER,
            lead_id INTEGER,
            assigned_to TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE crm_appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            appointment_date DATE NOT NULL,
            appointment_time TEXT,
            customer_id INTEGER,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE crm_leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT NOT NULL,
            estimated_value REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE user_dashboard_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL UNIQUE,
            widget_config TEXT,
            auto_refresh_enabled BOOLEAN DEFAULT 0,
            refresh_interval INTEGER DEFAULT 60,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    yield conn
    conn.close()


def test_open_tasks_widget_get_data(test_db):
    """Test: OpenTasksWidget holt Daten korrekt"""
    from crm.features.dashboard_widgets import OpenTasksWidget

    # Füge Test-Aufgaben hinzu
    cursor = test_db.cursor()
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    cursor.execute("""
        INSERT INTO crm_tasks (title, priority, due_date, status)
        VALUES (?, ?, ?, ?)
    """, ("Wichtige Aufgabe", "high", today.isoformat(), "open"))

    cursor.execute("""
        INSERT INTO crm_tasks (title, priority, due_date, status)
        VALUES (?, ?, ?, ?)
    """, ("Normale Aufgabe", "medium", tomorrow.isoformat(), "open"))

    cursor.execute("""
        INSERT INTO crm_tasks (title, priority, due_date, status)
        VALUES (?, ?, ?, ?)
    """, ("Erledigte Aufgabe", "low", today.isoformat(), "completed"))

    test_db.commit()

    # Mock get_db_connection
    with patch('crm.features.dashboard_widgets.get_db_connection',
               return_value=test_db):
        widget = OpenTasksWidget()
        tasks = widget.get_data()

        # Prüfe Ergebnisse
        assert len(tasks) == 2  # Nur offene Aufgaben
        assert tasks[0]['priority'] == 'high'  # Sortiert nach Priorität
        assert tasks[0]['title'] == "Wichtige Aufgabe"
        assert tasks[1]['priority'] == 'medium'


def test_upcoming_appointments_widget_get_data(test_db):
    """Test: UpcomingAppointmentsWidget holt Daten korrekt"""
    from crm.features.dashboard_widgets import UpcomingAppointmentsWidget

    # Füge Test-Termine hinzu
    cursor = test_db.cursor()
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=8)

    cursor.execute("""
        INSERT INTO crm_appointments
        (title, appointment_date, appointment_time, location)
        VALUES (?, ?, ?, ?)
    """, ("Termin Heute", today.isoformat(), "10:00", "Büro"))

    cursor.execute("""
        INSERT INTO crm_appointments
        (title, appointment_date, appointment_time, location)
        VALUES (?, ?, ?, ?)
    """, ("Termin Morgen", tomorrow.isoformat(), "14:00", "Kunde"))

    cursor.execute("""
        INSERT INTO crm_appointments
        (title, appointment_date, appointment_time, location)
        VALUES (?, ?, ?, ?)
    """, ("Termin nächste Woche", next_week.isoformat(), "09:00", "Remote"))

    test_db.commit()

    # Mock get_db_connection
    with patch('crm.features.dashboard_widgets.get_db_connection',
               return_value=test_db):
        widget = UpcomingAppointmentsWidget()
        appointments = widget.get_data()

        # Prüfe Ergebnisse
        assert len(appointments) == 2  # Nur nächste 7 Tage
        assert appointments[0]['title'] == "Termin Heute"
        assert appointments[1]['title'] == "Termin Morgen"


def test_pipeline_overview_widget_get_data(test_db):
    """Test: PipelineOverviewWidget holt Daten korrekt"""
    from crm.features.dashboard_widgets import PipelineOverviewWidget

    # Füge Test-Leads hinzu
    cursor = test_db.cursor()

    cursor.execute("""
        INSERT INTO crm_leads (status, estimated_value)
        VALUES (?, ?)
    """, ("new", 10000))

    cursor.execute("""
        INSERT INTO crm_leads (status, estimated_value)
        VALUES (?, ?)
    """, ("new", 15000))

    cursor.execute("""
        INSERT INTO crm_leads (status, estimated_value)
        VALUES (?, ?)
    """, ("qualified", 20000))

    cursor.execute("""
        INSERT INTO crm_leads (status, estimated_value)
        VALUES (?, ?)
    """, ("won", 30000))

    test_db.commit()

    # Mock get_db_connection
    with patch('crm.features.dashboard_widgets.get_db_connection',
               return_value=test_db):
        widget = PipelineOverviewWidget()
        data = widget.get_data()

        # Prüfe Ergebnisse
        assert 'new' in data
        assert data['new']['count'] == 2
        assert data['new']['value'] == 25000
        assert data['qualified']['count'] == 1
        assert data['qualified']['value'] == 20000


def test_revenue_tracking_widget_get_data(test_db):
    """Test: RevenueTrackingWidget holt Daten korrekt"""
    from crm.features.dashboard_widgets import RevenueTrackingWidget

    # Füge Test-Leads hinzu
    cursor = test_db.cursor()
    current_month = datetime.now().strftime('%Y-%m')
    current_year = datetime.now().strftime('%Y')

    # Gewonnene Deals diesen Monat
    cursor.execute("""
        INSERT INTO crm_leads (status, estimated_value, created_at)
        VALUES (?, ?, ?)
    """, ("won", 50000, f"{current_month}-15 10:00:00"))

    cursor.execute("""
        INSERT INTO crm_leads (status, estimated_value, created_at)
        VALUES (?, ?, ?)
    """, ("won", 30000, f"{current_month}-20 14:00:00"))

    # Verlorener Deal
    cursor.execute("""
        INSERT INTO crm_leads (status, estimated_value, created_at)
        VALUES (?, ?, ?)
    """, ("lost", 20000, f"{current_month}-10 09:00:00"))

    test_db.commit()

    # Mock get_db_connection
    with patch('crm.features.dashboard_widgets.get_db_connection',
               return_value=test_db):
        widget = RevenueTrackingWidget()
        data = widget.get_data()

        # Prüfe Ergebnisse
        assert data['monthly_revenue'] == 80000
        assert data['yearly_revenue'] == 80000
        assert data['avg_deal_size'] == 40000
        assert data['conversion_rate'] == pytest.approx(66.67, rel=0.1)


def test_widget_manager_default_config():
    """Test: WidgetManager gibt Standard-Konfiguration zurück"""
    from crm.features.dashboard_widgets import WidgetManager

    manager = WidgetManager()
    config = manager._get_default_config()

    # Prüfe Standard-Konfiguration
    assert 'open_tasks' in config
    assert config['open_tasks']['visible'] is True
    assert config['open_tasks']['order'] == 1
    assert 'upcoming_appointments' in config
    assert 'pipeline_overview' in config
    assert 'revenue_tracking' in config


def test_widget_manager_save_and_load_config(test_db):
    """Test: WidgetManager speichert und lädt Konfiguration"""
    from crm.features.dashboard_widgets import WidgetManager
    import sqlite3

    manager = WidgetManager()

    # Test-Konfiguration
    test_config = {
        'open_tasks': {'visible': False, 'order': 3},
        'upcoming_appointments': {'visible': True, 'order': 1},
        'pipeline_overview': {'visible': True, 'order': 2},
        'revenue_tracking': {'visible': False, 'order': 4}
    }

    # Get database path from test_db
    db_path = test_db.execute("PRAGMA database_list").fetchone()[2]

    # Mock get_db_connection to return new connections each time
    def get_new_conn():
        conn = sqlite3.connect(db_path)
        return conn

    with patch('crm.features.dashboard_widgets.get_db_connection',
               side_effect=get_new_conn):
        # Speichere Konfiguration
        success = manager.save_widget_config("test_user", test_config)
        assert success is True

        # Lade Konfiguration
        loaded_config = manager.get_widget_config("test_user")
        assert loaded_config == test_config
        assert loaded_config['open_tasks']['visible'] is False
        assert loaded_config['upcoming_appointments']['order'] == 1


def test_widget_manager_load_nonexistent_config(test_db):
    """Test: WidgetManager gibt Default zurück bei nicht existierendem User"""
    from crm.features.dashboard_widgets import WidgetManager

    manager = WidgetManager()

    # Mock get_db_connection
    with patch('crm.features.dashboard_widgets.get_db_connection',
               return_value=test_db):
        # Lade Konfiguration für nicht existierenden User
        config = manager.get_widget_config("nonexistent_user")

        # Sollte Default-Konfiguration zurückgeben
        assert config == manager._get_default_config()


def test_widget_render_without_database():
    """Test: Widgets funktionieren ohne Datenbank (zeigen Info)"""
    from crm.features.dashboard_widgets import OpenTasksWidget

    # Mock get_db_connection to return None
    with patch('crm.features.dashboard_widgets.get_db_connection',
               return_value=None):
        widget = OpenTasksWidget()
        tasks = widget.get_data()

        # Sollte leere Liste zurückgeben
        assert tasks == []


def test_widget_base_class():
    """Test: DashboardWidget Basis-Klasse"""
    from crm.features.dashboard_widgets import DashboardWidget

    widget = DashboardWidget(
        widget_id="test_widget",
        title="Test Widget",
        icon="",
        default_visible=True
    )

    assert widget.widget_id == "test_widget"
    assert widget.title == "Test Widget"
    assert widget.icon == ""
    assert widget.default_visible is True

    # render() sollte NotImplementedError werfen
    with pytest.raises(NotImplementedError):
        widget.render()


def test_widget_manager_render_widgets_order(test_db):
    """Test: WidgetManager rendert Widgets in korrekter Reihenfolge"""
    from crm.features.dashboard_widgets import WidgetManager
    import sqlite3

    manager = WidgetManager()

    # Konfiguration mit umgekehrter Reihenfolge
    test_config = {
        'open_tasks': {'visible': True, 'order': 4},
        'upcoming_appointments': {'visible': True, 'order': 3},
        'pipeline_overview': {'visible': True, 'order': 2},
        'revenue_tracking': {'visible': True, 'order': 1}
    }

    # Get database path from test_db
    db_path = test_db.execute("PRAGMA database_list").fetchone()[2]

    # Mock get_db_connection to return new connections each time
    def get_new_conn():
        conn = sqlite3.connect(db_path)
        return conn

    with patch('crm.features.dashboard_widgets.get_db_connection',
               side_effect=get_new_conn):
        manager.save_widget_config("test_user", test_config)

        # Lade und prüfe Reihenfolge
        config = manager.get_widget_config("test_user")
        sorted_widgets = sorted(
            config.items(),
            key=lambda x: x[1].get('order', 999)
        )

        # Prüfe dass revenue_tracking zuerst kommt
        assert sorted_widgets[0][0] == 'revenue_tracking'
        assert sorted_widgets[1][0] == 'pipeline_overview'
        assert sorted_widgets[2][0] == 'upcoming_appointments'
        assert sorted_widgets[3][0] == 'open_tasks'


def test_widget_manager_hide_widgets(test_db):
    """Test: WidgetManager versteckt nicht-sichtbare Widgets"""
    from crm.features.dashboard_widgets import WidgetManager
    import sqlite3

    manager = WidgetManager()

    # Konfiguration mit versteckten Widgets
    test_config = {
        'open_tasks': {'visible': False, 'order': 1},
        'upcoming_appointments': {'visible': True, 'order': 2},
        'pipeline_overview': {'visible': False, 'order': 3},
        'revenue_tracking': {'visible': True, 'order': 4}
    }

    # Get database path from test_db
    db_path = test_db.execute("PRAGMA database_list").fetchone()[2]

    # Mock get_db_connection to return new connections each time
    def get_new_conn():
        conn = sqlite3.connect(db_path)
        return conn

    with patch('crm.features.dashboard_widgets.get_db_connection',
               side_effect=get_new_conn):
        manager.save_widget_config("test_user", test_config)
        config = manager.get_widget_config("test_user")

        # Zähle sichtbare Widgets
        visible_count = sum(
            1 for w in config.values() if w.get('visible', True))
        assert visible_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
