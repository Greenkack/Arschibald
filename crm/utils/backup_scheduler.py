"""
Datei: crm/utils/backup_scheduler.py
Zweck: Automatisches Backup-System für CRM-Datenbank mit APScheduler
Autor: Kiro AI
Datum: 2025-01-14

Funktionen:
- Automatische tägliche, wöchentliche und monatliche Backups
- Backup-Rotation (7 täglich, 4 wöchentlich, 12 monatlich)
- Manuelle Backup-Erstellung
- Wiederherstellungs-Funktion
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# APScheduler imports
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False
    BackgroundScheduler = None  # type: ignore
    CronTrigger = None  # type: ignore

# Import existing backup functions from database.py
try:
    from database import backup_database, restore_database, DB_PATH
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    backup_database = None  # type: ignore
    restore_database = None  # type: ignore
    DB_PATH = "crm_database.db"


# Backup-Verzeichnisse
BACKUP_BASE_DIR = Path("backups")
BACKUP_DAILY_DIR = BACKUP_BASE_DIR / "daily"
BACKUP_WEEKLY_DIR = BACKUP_BASE_DIR / "weekly"
BACKUP_MONTHLY_DIR = BACKUP_BASE_DIR / "monthly"
BACKUP_MANUAL_DIR = BACKUP_BASE_DIR / "manual"

# Rotation-Limits
MAX_DAILY_BACKUPS = 7
MAX_WEEKLY_BACKUPS = 4
MAX_MONTHLY_BACKUPS = 12
MAX_MANUAL_BACKUPS = 10


def ensure_backup_directories() -> None:
    """Erstellt alle benötigten Backup-Verzeichnisse."""
    for directory in [BACKUP_DAILY_DIR, BACKUP_WEEKLY_DIR, BACKUP_MONTHLY_DIR, BACKUP_MANUAL_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def generate_backup_filename(backup_type: str) -> str:
    """
    Generiert einen Backup-Dateinamen mit Zeitstempel.
    
    Args:
        backup_type: Typ des Backups (daily, weekly, monthly, manual)
        
    Returns:
        Dateiname im Format: backup_TYPE_YYYYMMDD_HHMMSS.db
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"backup_{backup_type}_{timestamp}.db"


def get_backup_directory(backup_type: str) -> Path:
    """
    Gibt das Verzeichnis für einen Backup-Typ zurück.
    
    Args:
        backup_type: Typ des Backups (daily, weekly, monthly, manual)
        
    Returns:
        Path-Objekt des Backup-Verzeichnisses
    """
    directories = {
        "daily": BACKUP_DAILY_DIR,
        "weekly": BACKUP_WEEKLY_DIR,
        "monthly": BACKUP_MONTHLY_DIR,
        "manual": BACKUP_MANUAL_DIR
    }
    return directories.get(backup_type, BACKUP_MANUAL_DIR)


def create_backup(backup_type: str = "manual") -> Tuple[bool, str]:
    """
    Erstellt ein Backup der Datenbank.
    
    Args:
        backup_type: Typ des Backups (daily, weekly, monthly, manual)
        
    Returns:
        Tuple (success: bool, message: str)
    """
    if not DATABASE_AVAILABLE:
        return False, "Datenbank-Modul nicht verfügbar"
    
    try:
        ensure_backup_directories()
        
        # Generiere Backup-Pfad
        backup_dir = get_backup_directory(backup_type)
        backup_filename = generate_backup_filename(backup_type)
        backup_path = backup_dir / backup_filename
        
        # Erstelle Backup
        success = backup_database(str(backup_path))
        
        if success:
            # Führe Rotation durch
            rotate_backups(backup_type)
            return True, f"Backup erfolgreich erstellt: {backup_filename}"
        else:
            return False, "Backup-Erstellung fehlgeschlagen"
            
    except Exception as e:
        return False, f"Fehler beim Backup: {str(e)}"


def rotate_backups(backup_type: str) -> None:
    """
    Führt Backup-Rotation durch und löscht alte Backups.
    
    Args:
        backup_type: Typ des Backups (daily, weekly, monthly, manual)
    """
    max_backups = {
        "daily": MAX_DAILY_BACKUPS,
        "weekly": MAX_WEEKLY_BACKUPS,
        "monthly": MAX_MONTHLY_BACKUPS,
        "manual": MAX_MANUAL_BACKUPS
    }
    
    max_count = max_backups.get(backup_type, MAX_MANUAL_BACKUPS)
    backup_dir = get_backup_directory(backup_type)
    
    # Hole alle Backup-Dateien sortiert nach Änderungsdatum (neueste zuerst)
    backup_files = sorted(
        backup_dir.glob("backup_*.db"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    # Lösche alte Backups
    for old_backup in backup_files[max_count:]:
        try:
            old_backup.unlink()
            print(f"Altes Backup gelöscht: {old_backup.name}")
        except Exception as e:
            print(f"Fehler beim Löschen von {old_backup.name}: {e}")


def list_backups(backup_type: Optional[str] = None) -> List[Dict[str, any]]:
    """
    Listet alle verfügbaren Backups auf.
    
    Args:
        backup_type: Optional - Filtert nach Backup-Typ (daily, weekly, monthly, manual)
        
    Returns:
        Liste von Dictionaries mit Backup-Informationen
    """
    ensure_backup_directories()
    backups = []
    
    # Bestimme zu durchsuchende Verzeichnisse
    if backup_type:
        directories = [(backup_type, get_backup_directory(backup_type))]
    else:
        directories = [
            ("daily", BACKUP_DAILY_DIR),
            ("weekly", BACKUP_WEEKLY_DIR),
            ("monthly", BACKUP_MONTHLY_DIR),
            ("manual", BACKUP_MANUAL_DIR)
        ]
    
    # Sammle alle Backups
    for btype, directory in directories:
        for backup_file in directory.glob("backup_*.db"):
            stat = backup_file.stat()
            backups.append({
                "type": btype,
                "filename": backup_file.name,
                "path": str(backup_file),
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(stat.st_mtime),
                "created_str": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            })
    
    # Sortiere nach Erstellungsdatum (neueste zuerst)
    backups.sort(key=lambda x: x["created"], reverse=True)
    
    return backups


def restore_backup(backup_path: str) -> Tuple[bool, str]:
    """
    Stellt ein Backup wieder her.
    
    Args:
        backup_path: Pfad zur Backup-Datei
        
    Returns:
        Tuple (success: bool, message: str)
    """
    if not DATABASE_AVAILABLE:
        return False, "Datenbank-Modul nicht verfügbar"
    
    try:
        # Prüfe ob Backup-Datei existiert
        if not os.path.exists(backup_path):
            return False, f"Backup-Datei nicht gefunden: {backup_path}"
        
        # Erstelle Sicherheits-Backup der aktuellen DB vor Wiederherstellung
        ensure_backup_directories()
        safety_backup_path = BACKUP_MANUAL_DIR / f"before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        if os.path.exists(DB_PATH):
            shutil.copy2(DB_PATH, safety_backup_path)
            print(f"Sicherheits-Backup erstellt: {safety_backup_path}")
        
        # Stelle Backup wieder her
        success = restore_database(backup_path)
        
        if success:
            return True, f"Backup erfolgreich wiederhergestellt: {os.path.basename(backup_path)}"
        else:
            return False, "Wiederherstellung fehlgeschlagen"
            
    except Exception as e:
        return False, f"Fehler bei Wiederherstellung: {str(e)}"


def delete_backup(backup_path: str) -> Tuple[bool, str]:
    """
    Löscht ein Backup.
    
    Args:
        backup_path: Pfad zur Backup-Datei
        
    Returns:
        Tuple (success: bool, message: str)
    """
    try:
        if not os.path.exists(backup_path):
            return False, f"Backup-Datei nicht gefunden: {backup_path}"
        
        os.remove(backup_path)
        return True, f"Backup gelöscht: {os.path.basename(backup_path)}"
        
    except Exception as e:
        return False, f"Fehler beim Löschen: {str(e)}"


# ============================================================================
# SCHEDULER-FUNKTIONEN
# ============================================================================

# Globaler Scheduler
_scheduler: Optional[BackgroundScheduler] = None


def scheduled_daily_backup() -> None:
    """Job-Funktion für tägliche Backups (2:00 Uhr)."""
    print(f"[{datetime.now()}] Starte tägliches Backup...")
    success, message = create_backup("daily")
    print(f"[{datetime.now()}] {message}")


def scheduled_weekly_backup() -> None:
    """Job-Funktion für wöchentliche Backups (Sonntag 3:00 Uhr)."""
    print(f"[{datetime.now()}] Starte wöchentliches Backup...")
    success, message = create_backup("weekly")
    print(f"[{datetime.now()}] {message}")


def scheduled_monthly_backup() -> None:
    """Job-Funktion für monatliche Backups (1. des Monats 4:00 Uhr)."""
    print(f"[{datetime.now()}] Starte monatliches Backup...")
    success, message = create_backup("monthly")
    print(f"[{datetime.now()}] {message}")


def start_scheduler() -> Tuple[bool, str]:
    """
    Startet den Backup-Scheduler.
    
    Returns:
        Tuple (success: bool, message: str)
    """
    global _scheduler
    
    if not APSCHEDULER_AVAILABLE:
        return False, "APScheduler nicht installiert. Bitte installieren: pip install apscheduler"
    
    if _scheduler is not None and _scheduler.running:
        return False, "Scheduler läuft bereits"
    
    try:
        _scheduler = BackgroundScheduler()
        
        # Tägliches Backup um 2:00 Uhr
        _scheduler.add_job(
            scheduled_daily_backup,
            CronTrigger(hour=2, minute=0),
            id="daily_backup",
            name="Tägliches Backup",
            replace_existing=True
        )
        
        # Wöchentliches Backup (Sonntag 3:00 Uhr)
        _scheduler.add_job(
            scheduled_weekly_backup,
            CronTrigger(day_of_week="sun", hour=3, minute=0),
            id="weekly_backup",
            name="Wöchentliches Backup",
            replace_existing=True
        )
        
        # Monatliches Backup (1. des Monats 4:00 Uhr)
        _scheduler.add_job(
            scheduled_monthly_backup,
            CronTrigger(day=1, hour=4, minute=0),
            id="monthly_backup",
            name="Monatliches Backup",
            replace_existing=True
        )
        
        _scheduler.start()
        
        return True, "Backup-Scheduler erfolgreich gestartet"
        
    except Exception as e:
        return False, f"Fehler beim Starten des Schedulers: {str(e)}"


def stop_scheduler() -> Tuple[bool, str]:
    """
    Stoppt den Backup-Scheduler.
    
    Returns:
        Tuple (success: bool, message: str)
    """
    global _scheduler
    
    if _scheduler is None or not _scheduler.running:
        return False, "Scheduler läuft nicht"
    
    try:
        _scheduler.shutdown()
        _scheduler = None
        return True, "Backup-Scheduler gestoppt"
        
    except Exception as e:
        return False, f"Fehler beim Stoppen des Schedulers: {str(e)}"


def get_scheduler_status() -> Dict[str, any]:
    """
    Gibt den Status des Schedulers zurück.
    
    Returns:
        Dictionary mit Scheduler-Informationen
    """
    if not APSCHEDULER_AVAILABLE:
        return {
            "running": False,
            "available": False,
            "message": "APScheduler nicht installiert"
        }
    
    if _scheduler is None:
        return {
            "running": False,
            "available": True,
            "message": "Scheduler nicht gestartet"
        }
    
    jobs = []
    if _scheduler.running:
        for job in _scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.strftime("%Y-%m-%d %H:%M:%S") if job.next_run_time else "N/A"
            })
    
    return {
        "running": _scheduler.running,
        "available": True,
        "jobs": jobs,
        "message": "Scheduler aktiv" if _scheduler.running else "Scheduler gestoppt"
    }


def get_backup_statistics() -> Dict[str, any]:
    """
    Gibt Statistiken über alle Backups zurück.
    
    Returns:
        Dictionary mit Backup-Statistiken
    """
    backups = list_backups()
    
    total_size_mb = sum(b["size_mb"] for b in backups)
    
    stats_by_type = {}
    for btype in ["daily", "weekly", "monthly", "manual"]:
        type_backups = [b for b in backups if b["type"] == btype]
        stats_by_type[btype] = {
            "count": len(type_backups),
            "size_mb": round(sum(b["size_mb"] for b in type_backups), 2),
            "latest": type_backups[0]["created_str"] if type_backups else "Keine Backups"
        }
    
    return {
        "total_backups": len(backups),
        "total_size_mb": round(total_size_mb, 2),
        "by_type": stats_by_type,
        "latest_backup": backups[0]["created_str"] if backups else "Keine Backups"
    }
