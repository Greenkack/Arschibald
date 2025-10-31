#!/usr/bin/env python3
"""
Intelligenter Backup-Manager
"""
import datetime
import glob
import os
import zipfile


def create_smart_backup():
    """Erstellt intelligentes Backup der wichtigsten Dateien"""

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}"

    # Wichtige Dateien/Ordner definieren
    important_items = [
        "*.py",
        "*.json",
        "*.txt",
        "*.md",
        "input/",
        "*.db",
        "config/",
        "templates/",
    ]

    # Ausschließen
    exclude_patterns = [
        "__pycache__",
        "*.pyc",
        ".git",
        "node_modules",
        "venv",
        "env",
        ".env",
        "backup_*",
    ]

    print(f"💾 ERSTELLE BACKUP: {backup_name}.zip")

    with zipfile.ZipFile(f"{backup_name}.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        files_added = 0

        for pattern in important_items:
            if pattern.endswith('/'):  # Ordner
                folder = pattern.rstrip('/')
                if os.path.exists(folder):
                    for root, dirs, files in os.walk(folder):
                        # Ausgeschlossene Ordner entfernen
                        dirs[:] = [
                            d for d in dirs if not any(
                                ex in d for ex in exclude_patterns)]

                        for file in files:
                            if not any(ex in file for ex in exclude_patterns):
                                file_path = os.path.join(root, file)
                                zipf.write(file_path)
                                files_added += 1
            else:  # Datei-Pattern
                for file_path in glob.glob(pattern, recursive=True):
                    if not any(ex in file_path for ex in exclude_patterns):
                        zipf.write(file_path)
                        files_added += 1

        print(f"✅ {files_added} Dateien ins Backup gepackt")

    # Backup-Info schreiben
    info_file = f"{backup_name}_info.txt"
    with open(info_file, 'w') as f:
        f.write(f"Backup erstellt: {datetime.datetime.now()}\n")
        f.write(f"Dateien: {files_added}\n")
        f.write(
            f"Größe: {
                os.path.getsize(
                    f'{backup_name}.zip') /
                1024 /
                1024:.2f} MB\n")

    print(f"📋 Backup-Info: {info_file}")

    # Alte Backups bereinigen (behalte nur die letzten 5)
    cleanup_old_backups()


def cleanup_old_backups(keep_count=5):
    """Löscht alte Backups, behält nur die neuesten"""

    backup_files = glob.glob("backup_*.zip")
    backup_files.sort(key=os.path.getctime, reverse=True)

    if len(backup_files) > keep_count:
        old_backups = backup_files[keep_count:]
        for old_backup in old_backups:
            os.remove(old_backup)
            # Lösche auch Info-Datei
            info_file = old_backup.replace('.zip', '_info.txt')
            if os.path.exists(info_file):
                os.remove(info_file)

        print(f"🧹 {len(old_backups)} alte Backups gelöscht")


if __name__ == "__main__":
    create_smart_backup()
