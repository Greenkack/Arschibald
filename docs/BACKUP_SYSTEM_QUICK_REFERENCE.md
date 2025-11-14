# Backup-System - Quick Reference

## Übersicht

Das automatische Backup-System für die CRM-Datenbank bietet vollständige Backup- und Wiederherstellungsfunktionen mit automatischer Rotation.

## Features

### ✅ Automatische Backups
- **Täglich**: Jeden Tag um 2:00 Uhr (max. 7 Backups)
- **Wöchentlich**: Jeden Sonntag um 3:00 Uhr (max. 4 Backups)
- **Monatlich**: Am 1. jeden Monats um 4:00 Uhr (max. 12 Backups)

### ✅ Manuelle Backups
- Jederzeit manuell Backups erstellen
- Unbegrenzte Anzahl (max. 10 werden behalten)

### ✅ Backup-Rotation
- Alte Backups werden automatisch gelöscht
- Neueste Backups werden immer behalten

### ✅ Wiederherstellung
- Einfache Wiederherstellung mit Bestätigung
- Automatisches Sicherheits-Backup vor Wiederherstellung

### ✅ Backup-Verwaltung
- Übersicht aller Backups
- Filterung nach Typ
- Größenanzeige und Statistiken
- Löschen einzelner Backups

## Verwendung

### Admin-Panel

1. Öffnen Sie das Admin-Panel (Tab F)
2. Wählen Sie "💾 Backup-Verwaltung"
3. Nutzen Sie die verschiedenen Tabs:
   - **Übersicht**: Schnellüberblick und Schnellaktionen
   - **Backups verwalten**: Manuelles Backup erstellen, Liste aller Backups
   - **Automatische Backups**: Scheduler starten/stoppen, Zeitplan anzeigen
   - **Statistiken**: Detaillierte Backup-Statistiken

### Programmatische Verwendung

```python
from crm.utils.backup_scheduler import (
    create_backup,
    list_backups,
    restore_backup,
    delete_backup,
    start_scheduler,
    stop_scheduler,
    get_scheduler_status,
    get_backup_statistics
)

# Manuelles Backup erstellen
success, message = create_backup("manual")
if success:
    print(f"Backup erfolgreich: {message}")

# Alle Backups auflisten
backups = list_backups()
for backup in backups:
    print(f"{backup['filename']} - {backup['size_mb']} MB - {backup['created_str']}")

# Backup wiederherstellen
backup_path = backups[0]['path']
success, message = restore_backup(backup_path)

# Scheduler starten
success, message = start_scheduler()
if success:
    print("Automatische Backups aktiviert")

# Scheduler-Status prüfen
status = get_scheduler_status()
print(f"Scheduler läuft: {status['running']}")

# Statistiken abrufen
stats = get_backup_statistics()
print(f"Gesamt Backups: {stats['total_backups']}")
print(f"Gesamtgröße: {stats['total_size_mb']} MB")
```

## Backup-Verzeichnisse

```
backups/
├── daily/          # Tägliche Backups (max. 7)
├── weekly/         # Wöchentliche Backups (max. 4)
├── monthly/        # Monatliche Backups (max. 12)
└── manual/         # Manuelle Backups (max. 10)
```

## Backup-Dateinamen

Format: `backup_TYPE_YYYYMMDD_HHMMSS.db`

Beispiele:
- `backup_daily_20251115_020000.db`
- `backup_weekly_20251117_030000.db`
- `backup_monthly_20251201_040000.db`
- `backup_manual_20251115_143022.db`

## Sicherheits-Features

### Vor Wiederherstellung
- Automatisches Sicherheits-Backup der aktuellen Datenbank
- Bestätigungsdialog erforderlich
- Sicherheits-Backup wird im `manual/` Ordner gespeichert

### Backup-Rotation
- Alte Backups werden automatisch gelöscht
- Nur die neuesten Backups werden behalten
- Rotation erfolgt nach jedem Backup

## Anforderungen

### Python-Pakete
```bash
pip install apscheduler
```

### Abhängigkeiten
- `database.py`: Für `backup_database()` und `restore_database()` Funktionen
- `streamlit`: Für UI-Komponenten

## Scheduler-Konfiguration

Der Scheduler verwendet APScheduler mit CronTrigger:

```python
# Tägliches Backup um 2:00 Uhr
CronTrigger(hour=2, minute=0)

# Wöchentliches Backup (Sonntag 3:00 Uhr)
CronTrigger(day_of_week="sun", hour=3, minute=0)

# Monatliches Backup (1. des Monats 4:00 Uhr)
CronTrigger(day=1, hour=4, minute=0)
```

## Fehlerbehandlung

### Backup-Erstellung fehlgeschlagen
```python
success, message = create_backup("manual")
if not success:
    print(f"Fehler: {message}")
    # Prüfen Sie:
    # - Schreibrechte im backups/ Verzeichnis
    # - Verfügbarer Speicherplatz
    # - Datenbank-Zugriff
```

### Wiederherstellung fehlgeschlagen
```python
success, message = restore_backup(backup_path)
if not success:
    print(f"Fehler: {message}")
    # Prüfen Sie:
    # - Backup-Datei existiert
    # - Backup-Datei ist nicht beschädigt
    # - Schreibrechte für Datenbank
```

### Scheduler startet nicht
```python
success, message = start_scheduler()
if not success:
    print(f"Fehler: {message}")
    # Prüfen Sie:
    # - APScheduler ist installiert
    # - Scheduler läuft nicht bereits
```

## Best Practices

### 1. Regelmäßige Überprüfung
- Prüfen Sie regelmäßig die Backup-Statistiken
- Stellen Sie sicher, dass der Scheduler läuft
- Überprüfen Sie verfügbaren Speicherplatz

### 2. Test-Wiederherstellung
- Testen Sie regelmäßig die Wiederherstellung
- Verwenden Sie eine Test-Umgebung
- Dokumentieren Sie den Wiederherstellungsprozess

### 3. Externe Backups
- Kopieren Sie wichtige Backups auf externe Medien
- Nutzen Sie Cloud-Speicher für zusätzliche Sicherheit
- Erstellen Sie vor wichtigen Änderungen manuelle Backups

### 4. Monitoring
- Überwachen Sie Backup-Größen
- Achten Sie auf ungewöhnliche Änderungen
- Prüfen Sie Backup-Erfolg in Logs

## Troubleshooting

### Problem: Scheduler läuft nicht
**Lösung**: 
```python
# Prüfen Sie den Status
status = get_scheduler_status()
print(status)

# Starten Sie den Scheduler neu
stop_scheduler()
start_scheduler()
```

### Problem: Backups werden nicht rotiert
**Lösung**:
- Prüfen Sie Schreibrechte im Backup-Verzeichnis
- Überprüfen Sie die Rotation-Limits in `backup_scheduler.py`

### Problem: Wiederherstellung schlägt fehl
**Lösung**:
- Prüfen Sie ob Backup-Datei existiert und lesbar ist
- Stellen Sie sicher, dass keine andere Anwendung die Datenbank verwendet
- Prüfen Sie Schreibrechte für die Datenbank-Datei

## API-Referenz

### create_backup(backup_type: str) -> Tuple[bool, str]
Erstellt ein Backup der Datenbank.

**Parameter:**
- `backup_type`: "daily", "weekly", "monthly", oder "manual"

**Returns:**
- `(True, message)` bei Erfolg
- `(False, error_message)` bei Fehler

### list_backups(backup_type: Optional[str] = None) -> List[Dict]
Listet alle verfügbaren Backups auf.

**Parameter:**
- `backup_type`: Optional - Filtert nach Typ

**Returns:**
- Liste von Dictionaries mit Backup-Informationen

### restore_backup(backup_path: str) -> Tuple[bool, str]
Stellt ein Backup wieder her.

**Parameter:**
- `backup_path`: Pfad zur Backup-Datei

**Returns:**
- `(True, message)` bei Erfolg
- `(False, error_message)` bei Fehler

### delete_backup(backup_path: str) -> Tuple[bool, str]
Löscht ein Backup.

**Parameter:**
- `backup_path`: Pfad zur Backup-Datei

**Returns:**
- `(True, message)` bei Erfolg
- `(False, error_message)` bei Fehler

### start_scheduler() -> Tuple[bool, str]
Startet den automatischen Backup-Scheduler.

**Returns:**
- `(True, message)` bei Erfolg
- `(False, error_message)` bei Fehler

### stop_scheduler() -> Tuple[bool, str]
Stoppt den automatischen Backup-Scheduler.

**Returns:**
- `(True, message)` bei Erfolg
- `(False, error_message)` bei Fehler

### get_scheduler_status() -> Dict
Gibt den Status des Schedulers zurück.

**Returns:**
- Dictionary mit Scheduler-Informationen

### get_backup_statistics() -> Dict
Gibt Statistiken über alle Backups zurück.

**Returns:**
- Dictionary mit Backup-Statistiken

## Support

Bei Problemen oder Fragen:
1. Prüfen Sie die Logs in der Konsole
2. Überprüfen Sie die Test-Suite: `pytest crm/utils/test_backup_scheduler.py`
3. Konsultieren Sie die vollständige Dokumentation in `crm/utils/BACKUP_SYSTEM_README.md`

## Changelog

### Version 1.0.0 (2025-01-15)
- Initiale Implementierung
- Automatische Backups (täglich, wöchentlich, monatlich)
- Manuelle Backup-Erstellung
- Backup-Rotation
- Wiederherstellungs-Funktion
- Admin-Panel Integration
- Vollständige Test-Suite
