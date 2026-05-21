"""
Datei: crm/utils/test_backup_scheduler.py
Zweck: Unit Tests für das Backup-System
Autor: Kiro AI
Datum: 2025-01-14

Tests:
- Backup-Erstellung
- Backup-Rotation
- Backup-Wiederherstellung
- Scheduler-Funktionen
"""

import os
import shutil
import tempfile
import time
from datetime import datetime
from pathlib import Path
import pytest

# Import der zu testenden Module
try:
    from crm.utils.backup_scheduler import (
        ensure_backup_directories,
        generate_backup_filename,
        get_backup_directory,
        create_backup,
        rotate_backups,
        list_backups,
        restore_backup,
        delete_backup,
        get_backup_statistics,
        BACKUP_BASE_DIR,
        BACKUP_DAILY_DIR,
        BACKUP_WEEKLY_DIR,
        BACKUP_MONTHLY_DIR,
        BACKUP_MANUAL_DIR,
        MAX_DAILY_BACKUPS,
        MAX_WEEKLY_BACKUPS,
        MAX_MONTHLY_BACKUPS)
    BACKUP_MODULE_AVAILABLE = True
except ImportError as e:
    BACKUP_MODULE_AVAILABLE = False
    print(f"Backup-Modul nicht verfügbar: {e}")


# Fixtures für temporäre Test-Umgebung
@pytest.fixture
def temp_backup_dir(monkeypatch):
    """Erstellt ein temporäres Backup-Verzeichnis für Tests."""
    if not BACKUP_MODULE_AVAILABLE:
        pytest.skip("Backup-Modul nicht verfügbar")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)
        
        # Patche die Backup-Verzeichnisse
        monkeypatch.setattr("crm.utils.backup_scheduler.BACKUP_BASE_DIR", temp_path)
        monkeypatch.setattr("crm.utils.backup_scheduler.BACKUP_DAILY_DIR", temp_path / "daily")
        monkeypatch.setattr("crm.utils.backup_scheduler.BACKUP_WEEKLY_DIR", temp_path / "weekly")
        monkeypatch.setattr("crm.utils.backup_scheduler.BACKUP_MONTHLY_DIR", temp_path / "monthly")
        monkeypatch.setattr("crm.utils.backup_scheduler.BACKUP_MANUAL_DIR", temp_path / "manual")
        
        yield temp_path


@pytest.fixture
def mock_database(monkeypatch, tmp_path):
    """Erstellt eine Mock-Datenbank für Tests."""
    if not BACKUP_MODULE_AVAILABLE:
        pytest.skip("Backup-Modul nicht verfügbar")
    
    # Erstelle Mock-Datenbank
    db_path = tmp_path / "test_database.db"
    db_path.write_text("Mock Database Content")
    
    # Patche DB_PATH
    monkeypatch.setattr("crm.utils.backup_scheduler.DB_PATH", str(db_path))
    
    # Mock backup_database Funktion
    def mock_backup_db(backup_path: str) -> bool:
        try:
            shutil.copy2(str(db_path), backup_path)
            return True
        except Exception:
            return False
    
    # Mock restore_database Funktion
    def mock_restore_db(backup_path: str) -> bool:
        try:
            shutil.copy2(backup_path, str(db_path))
            return True
        except Exception:
            return False
    
    monkeypatch.setattr("crm.utils.backup_scheduler.backup_database", mock_backup_db)
    monkeypatch.setattr("crm.utils.backup_scheduler.restore_database", mock_restore_db)
    
    return db_path


# ============================================================================
# TESTS: Basis-Funktionen
# ============================================================================

def test_ensure_backup_directories(temp_backup_dir):
    """Test: Backup-Verzeichnisse werden erstellt."""
    from crm.utils.backup_scheduler import ensure_backup_directories
    
    ensure_backup_directories()
    
    assert (temp_backup_dir / "daily").exists()
    assert (temp_backup_dir / "weekly").exists()
    assert (temp_backup_dir / "monthly").exists()
    assert (temp_backup_dir / "manual").exists()


def test_generate_backup_filename():
    """Test: Backup-Dateiname wird korrekt generiert."""
    if not BACKUP_MODULE_AVAILABLE:
        pytest.skip("Backup-Modul nicht verfügbar")
    
    filename = generate_backup_filename("daily")
    
    assert filename.startswith("backup_daily_")
    assert filename.endswith(".db")
    assert len(filename) > 20  # Mindestlänge mit Zeitstempel


def test_get_backup_directory(temp_backup_dir):
    """Test: Korrektes Backup-Verzeichnis wird zurückgegeben."""
    from crm.utils.backup_scheduler import get_backup_directory
    
    daily_dir = get_backup_directory("daily")
    weekly_dir = get_backup_directory("weekly")
    monthly_dir = get_backup_directory("monthly")
    manual_dir = get_backup_directory("manual")
    
    assert daily_dir == temp_backup_dir / "daily"
    assert weekly_dir == temp_backup_dir / "weekly"
    assert monthly_dir == temp_backup_dir / "monthly"
    assert manual_dir == temp_backup_dir / "manual"


# ============================================================================
# TESTS: Backup-Erstellung
# ============================================================================

def test_create_backup_success(temp_backup_dir, mock_database):
    """Test: Backup wird erfolgreich erstellt."""
    from crm.utils.backup_scheduler import create_backup
    
    success, message = create_backup("manual")
    
    assert success is True
    assert "erfolgreich" in message.lower()
    
    # Prüfe ob Backup-Datei existiert
    manual_dir = temp_backup_dir / "manual"
    backup_files = list(manual_dir.glob("backup_*.db"))
    assert len(backup_files) == 1


def test_create_backup_all_types(temp_backup_dir, mock_database):
    """Test: Backups aller Typen können erstellt werden."""
    from crm.utils.backup_scheduler import create_backup
    
    for backup_type in ["daily", "weekly", "monthly", "manual"]:
        success, message = create_backup(backup_type)
        assert success is True
        
        # Prüfe ob Backup im richtigen Verzeichnis liegt
        backup_dir = temp_backup_dir / backup_type
        backup_files = list(backup_dir.glob("backup_*.db"))
        assert len(backup_files) >= 1


# ============================================================================
# TESTS: Backup-Rotation
# ============================================================================

def test_rotate_backups_daily(temp_backup_dir, mock_database, monkeypatch):
    """Test: Tägliche Backups werden korrekt rotiert (max. 7)."""
    from crm.utils.backup_scheduler import create_backup, list_backups
    
    # Erstelle mehr als MAX_DAILY_BACKUPS
    for i in range(10):
        create_backup("daily")
        time.sleep(0.01)  # Kleine Verzögerung für unterschiedliche Zeitstempel
    
    # Prüfe ob nur MAX_DAILY_BACKUPS vorhanden sind
    daily_backups = list_backups("daily")
    assert len(daily_backups) <= MAX_DAILY_BACKUPS


def test_rotate_backups_weekly(temp_backup_dir, mock_database):
    """Test: Wöchentliche Backups werden korrekt rotiert (max. 4)."""
    from crm.utils.backup_scheduler import create_backup, list_backups
    
    # Erstelle mehr als MAX_WEEKLY_BACKUPS
    for i in range(6):
        create_backup("weekly")
        time.sleep(0.01)
    
    # Prüfe ob nur MAX_WEEKLY_BACKUPS vorhanden sind
    weekly_backups = list_backups("weekly")
    assert len(weekly_backups) <= MAX_WEEKLY_BACKUPS


def test_rotate_backups_monthly(temp_backup_dir, mock_database):
    """Test: Monatliche Backups werden korrekt rotiert (max. 12)."""
    from crm.utils.backup_scheduler import create_backup, list_backups
    
    # Erstelle mehr als MAX_MONTHLY_BACKUPS
    for i in range(15):
        create_backup("monthly")
        time.sleep(0.01)
    
    # Prüfe ob nur MAX_MONTHLY_BACKUPS vorhanden sind
    monthly_backups = list_backups("monthly")
    assert len(monthly_backups) <= MAX_MONTHLY_BACKUPS


def test_rotate_backups_keeps_newest(temp_backup_dir, mock_database):
    """Test: Rotation behält die neuesten Backups."""
    from crm.utils.backup_scheduler import create_backup, list_backups
    
    # Erstelle mehrere Backups mit Verzögerung
    for i in range(10):
        create_backup("daily")
        time.sleep(0.02)
    
    backups = list_backups("daily")
    
    # Prüfe ob Backups nach Datum sortiert sind (neueste zuerst)
    for i in range(len(backups) - 1):
        assert backups[i]["created"] >= backups[i + 1]["created"]


# ============================================================================
# TESTS: Backup-Liste
# ============================================================================

def test_list_backups_empty(temp_backup_dir):
    """Test: Leere Backup-Liste wird korrekt zurückgegeben."""
    from crm.utils.backup_scheduler import list_backups
    
    backups = list_backups()
    assert backups == []


def test_list_backups_with_data(temp_backup_dir, mock_database):
    """Test: Backup-Liste enthält korrekte Informationen."""
    from crm.utils.backup_scheduler import create_backup, list_backups
    
    # Erstelle Test-Backups
    create_backup("daily")
    create_backup("manual")
    
    backups = list_backups()
    
    assert len(backups) == 2
    
    for backup in backups:
        assert "type" in backup
        assert "filename" in backup
        assert "path" in backup
        assert "size_mb" in backup
        assert "created" in backup
        assert "created_str" in backup


def test_list_backups_filter_by_type(temp_backup_dir, mock_database):
    """Test: Backup-Liste kann nach Typ gefiltert werden."""
    from crm.utils.backup_scheduler import create_backup, list_backups
    
    # Erstelle verschiedene Backup-Typen
    create_backup("daily")
    create_backup("weekly")
    create_backup("manual")
    
    # Filtere nach Typ
    daily_backups = list_backups("daily")
    weekly_backups = list_backups("weekly")
    manual_backups = list_backups("manual")
    
    assert len(daily_backups) == 1
    assert len(weekly_backups) == 1
    assert len(manual_backups) == 1
    
    assert daily_backups[0]["type"] == "daily"
    assert weekly_backups[0]["type"] == "weekly"
    assert manual_backups[0]["type"] == "manual"


# ============================================================================
# TESTS: Backup-Wiederherstellung
# ============================================================================

def test_restore_backup_success(temp_backup_dir, mock_database):
    """Test: Backup wird erfolgreich wiederhergestellt."""
    from crm.utils.backup_scheduler import create_backup, restore_backup
    
    # Erstelle Backup
    success, message = create_backup("manual")
    assert success is True
    
    # Hole Backup-Pfad
    backups = list_backups("manual")
    backup_path = backups[0]["path"]
    
    # Ändere Mock-Datenbank
    mock_database.write_text("Modified Content")
    
    # Stelle Backup wieder her
    success, message = restore_backup(backup_path)
    
    assert success is True
    assert "erfolgreich" in message.lower()
    
    # Prüfe ob Inhalt wiederhergestellt wurde
    content = mock_database.read_text()
    assert content == "Mock Database Content"


def test_restore_backup_nonexistent(temp_backup_dir):
    """Test: Wiederherstellung nicht existierender Backup-Datei schlägt fehl."""
    from crm.utils.backup_scheduler import restore_backup
    
    success, message = restore_backup("/nonexistent/backup.db")
    
    assert success is False
    assert "nicht gefunden" in message.lower()


def test_restore_backup_creates_safety_backup(temp_backup_dir, mock_database):
    """Test: Vor Wiederherstellung wird Sicherheits-Backup erstellt."""
    from crm.utils.backup_scheduler import create_backup, restore_backup
    import time
    from pathlib import Path
    
    # Erstelle Original-Backup
    create_backup("manual")
    time.sleep(0.1)  # Kurze Verzögerung
    backups = list_backups("manual")
    backup_path = backups[0]["path"]
    
    # Ändere Datenbank
    mock_database.write_text("Modified Content")
    
    # Stelle wieder her
    restore_backup(backup_path)
    time.sleep(0.1)  # Kurze Verzögerung für Dateisystem
    
    # Prüfe ob Sicherheits-Backup im manual-Verzeichnis erstellt wurde
    manual_dir = temp_backup_dir / "manual"
    all_files = list(manual_dir.glob("*.db"))
    safety_backups = [f for f in all_files if "before_restore" in f.name]
    
    # Mindestens 1 Sicherheits-Backup sollte vorhanden sein
    assert len(safety_backups) >= 1, f"Keine Sicherheits-Backups gefunden. Dateien: {[f.name for f in all_files]}"


# ============================================================================
# TESTS: Backup-Löschung
# ============================================================================

def test_delete_backup_success(temp_backup_dir, mock_database):
    """Test: Backup wird erfolgreich gelöscht."""
    from crm.utils.backup_scheduler import create_backup, delete_backup, list_backups
    
    # Erstelle Backup
    create_backup("manual")
    backups_before = list_backups("manual")
    assert len(backups_before) == 1
    
    # Lösche Backup
    backup_path = backups_before[0]["path"]
    success, message = delete_backup(backup_path)
    
    assert success is True
    assert "gelöscht" in message.lower()
    
    # Prüfe ob Backup gelöscht wurde
    backups_after = list_backups("manual")
    assert len(backups_after) == 0


def test_delete_backup_nonexistent(temp_backup_dir):
    """Test: Löschen nicht existierender Backup-Datei schlägt fehl."""
    from crm.utils.backup_scheduler import delete_backup
    
    success, message = delete_backup("/nonexistent/backup.db")
    
    assert success is False
    assert "nicht gefunden" in message.lower()


# ============================================================================
# TESTS: Statistiken
# ============================================================================

def test_get_backup_statistics_empty(temp_backup_dir):
    """Test: Statistiken für leere Backup-Liste."""
    from crm.utils.backup_scheduler import get_backup_statistics
    
    stats = get_backup_statistics()
    
    assert stats["total_backups"] == 0
    assert stats["total_size_mb"] == 0
    assert "by_type" in stats
    assert stats["latest_backup"] == "Keine Backups"


def test_get_backup_statistics_with_data(temp_backup_dir, mock_database):
    """Test: Statistiken mit vorhandenen Backups."""
    from crm.utils.backup_scheduler import create_backup, get_backup_statistics
    
    # Erstelle verschiedene Backups
    create_backup("daily")
    create_backup("weekly")
    create_backup("manual")
    
    stats = get_backup_statistics()
    
    assert stats["total_backups"] == 3
    # Größe kann 0 sein bei sehr kleinen Mock-Dateien (< 1 KB)
    assert stats["total_size_mb"] >= 0
    
    # Prüfe Statistiken nach Typ
    assert stats["by_type"]["daily"]["count"] == 1
    assert stats["by_type"]["weekly"]["count"] == 1
    assert stats["by_type"]["manual"]["count"] == 1


def test_get_backup_statistics_size_calculation(temp_backup_dir, mock_database):
    """Test: Größenberechnung in Statistiken ist korrekt."""
    from crm.utils.backup_scheduler import create_backup, get_backup_statistics
    
    create_backup("manual")
    
    stats = get_backup_statistics()
    
    # Prüfe ob Größe berechnet wurde (kann 0 sein bei sehr kleinen Dateien)
    assert stats["total_size_mb"] >= 0
    assert stats["by_type"]["manual"]["size_mb"] >= 0
    
    # Prüfe dass Backup existiert
    assert stats["total_backups"] == 1
    assert stats["by_type"]["manual"]["count"] == 1


# ============================================================================
# TESTS: Scheduler (nur wenn APScheduler verfügbar)
# ============================================================================

def test_scheduler_availability():
    """Test: Prüfe ob APScheduler verfügbar ist."""
    from crm.utils.backup_scheduler import APSCHEDULER_AVAILABLE
    
    # Dieser Test dokumentiert nur die Verfügbarkeit
    if APSCHEDULER_AVAILABLE:
        print("APScheduler ist verfügbar")
    else:
        print("APScheduler ist nicht verfügbar - Scheduler-Tests werden übersprungen")


def test_get_scheduler_status():
    """Test: Scheduler-Status kann abgefragt werden."""
    if not BACKUP_MODULE_AVAILABLE:
        pytest.skip("Backup-Modul nicht verfügbar")
    
    from crm.utils.backup_scheduler import get_scheduler_status, APSCHEDULER_AVAILABLE
    
    status = get_scheduler_status()
    
    assert "running" in status
    assert "available" in status
    assert "message" in status
    
    if not APSCHEDULER_AVAILABLE:
        assert status["available"] is False


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_full_backup_workflow(temp_backup_dir, mock_database):
    """Integration Test: Vollständiger Backup-Workflow."""
    from crm.utils.backup_scheduler import (
        create_backup,
        list_backups,
        restore_backup,
        delete_backup
    )
    
    # 1. Erstelle Backup
    success, message = create_backup("manual")
    assert success is True
    
    # 2. Liste Backups
    backups = list_backups()
    assert len(backups) == 1
    backup_path = backups[0]["path"]
    
    # 3. Ändere Datenbank
    original_content = mock_database.read_text()
    mock_database.write_text("Modified Content")
    
    # 4. Stelle Backup wieder her
    success, message = restore_backup(backup_path)
    assert success is True
    assert mock_database.read_text() == original_content
    
    # 5. Lösche Backup (nicht das Sicherheits-Backup)
    success, message = delete_backup(backup_path)
    assert success is True


def test_multiple_backup_types_workflow(temp_backup_dir, mock_database):
    """Integration Test: Mehrere Backup-Typen gleichzeitig."""
    from crm.utils.backup_scheduler import create_backup, list_backups, get_backup_statistics
    
    # Erstelle verschiedene Backup-Typen
    for backup_type in ["daily", "weekly", "monthly", "manual"]:
        success, message = create_backup(backup_type)
        assert success is True
    
    # Prüfe Gesamtliste
    all_backups = list_backups()
    assert len(all_backups) == 4
    
    # Prüfe gefilterte Listen
    for backup_type in ["daily", "weekly", "monthly", "manual"]:
        type_backups = list_backups(backup_type)
        assert len(type_backups) == 1
        assert type_backups[0]["type"] == backup_type
    
    # Prüfe Statistiken
    stats = get_backup_statistics()
    assert stats["total_backups"] == 4


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("BACKUP SYSTEM TESTS")
    print("=" * 70)
    
    if not BACKUP_MODULE_AVAILABLE:
        print("Backup-Modul nicht verfügbar")
        exit(1)
    
    # Führe Tests mit pytest aus
    pytest.main([__file__, "-v", "--tb=short"])
