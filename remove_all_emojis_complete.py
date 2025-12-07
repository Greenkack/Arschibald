"""
KOMPLETTE EMOJI-ENTFERNUNG
===========================
Entfernt ALLE Emojis aus allen Python-Dateien im Projekt.
User-Anforderung: "ich möchte dass du in allen vorhandenen Codes...
                    zu 100% alle codes und dateien... alle vorhandene emojis entfernst!"

Strategie:
1. Alle .py Dateien durchsuchen
2. Unicode-Emoji-Zeichen identifizieren und entfernen
3. Funktionalität bewahren (nur Emojis entfernen, keine Syntax-Änderungen)
4. Backup vor Änderungen
5. Detailliertes Reporting

SICHER: Nutzt Regex-basierte Entfernung nur für Emojis, keine Codelogik-Änderungen
"""

import re
import os
from pathlib import Path
from typing import List, Tuple, Dict
import shutil
from datetime import datetime

# Umfassende Emoji-Ranges (Unicode 13.0+)
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # Emoticons
    "\U0001F300-\U0001F5FF"  # Symbole & Piktogramme
    "\U0001F680-\U0001F6FF"  # Transport & Kartensymbole
    "\U0001F1E0-\U0001F1FF"  # Flaggen (iOS)
    "\U00002702-\U000027B0"  # Dingbats
    "\U000024C2-\U0001F251"  # Umschlossene Zeichen
    "\U0001F900-\U0001F9FF"  # Ergänzende Symbole
    "\U0001FA00-\U0001FA6F"  # Erweiterte Symbole
    "\U00002600-\U000026FF"  # Verschiedene Symbole (Sonne, Mond, etc.)
    "\U00002700-\U000027BF"  # Dingbats
    "\uFE00-\uFE0F"          # Variationsselektoren
    "\u200D"                 # Zero Width Joiner (für zusammengesetzte Emojis)
    "]+",
    flags=re.UNICODE
)

# Dateien/Ordner die ausgeschlossen werden sollen
EXCLUDE_PATTERNS = [
    '__pycache__',
    '.git',
    'venv',
    'env',
    '.venv',
    'node_modules',
    '.pytest_cache',
    'build',
    'dist',
    '*.egg-info',
    '.streamlit',
    'migrations',  # Datenbank-Migrations könnten sensibel sein
]

# Backup-Verzeichnis
BACKUP_DIR = Path('emoji_removal_backup_' + datetime.now().strftime('%Y%m%d_%H%M%S'))


def should_exclude_path(path: Path) -> bool:
    """Prüft ob Pfad ausgeschlossen werden soll"""
    path_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return True
    return False


def find_all_python_files(root_dir: Path) -> List[Path]:
    """Findet alle Python-Dateien im Projekt"""
    python_files = []
    for file_path in root_dir.rglob('*.py'):
        if not should_exclude_path(file_path):
            python_files.append(file_path)
    return python_files


def count_emojis_in_text(text: str) -> int:
    """Zählt Emojis in Text"""
    return len(EMOJI_PATTERN.findall(text))


def remove_emojis_from_text(text: str) -> Tuple[str, int]:
    """
    Entfernt alle Emojis aus Text
    
    Returns:
        (cleaned_text, count_removed)
    """
    original = text
    cleaned = EMOJI_PATTERN.sub('', text)
    count = len(EMOJI_PATTERN.findall(original))
    return cleaned, count


def process_file(file_path: Path, dry_run: bool = False) -> Dict:
    """
    Verarbeitet eine einzelne Datei
    
    Returns:
        Dict mit Statistiken: {
            'path': Path,
            'emojis_found': int,
            'emojis_removed': int,
            'modified': bool,
            'error': str or None
        }
    """
    result = {
        'path': file_path,
        'emojis_found': 0,
        'emojis_removed': 0,
        'modified': False,
        'error': None
    }
    
    try:
        # Datei lesen
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Emojis zählen
        emojis_found = count_emojis_in_text(original_content)
        result['emojis_found'] = emojis_found
        
        if emojis_found == 0:
            return result
        
        # Emojis entfernen
        cleaned_content, emojis_removed = remove_emojis_from_text(original_content)
        result['emojis_removed'] = emojis_removed
        
        # Prüfen ob Änderungen vorliegen
        if original_content != cleaned_content:
            result['modified'] = True
            
            if not dry_run:
                # Backup erstellen
                backup_path = BACKUP_DIR / file_path.relative_to(Path.cwd())
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_path)
                
                # Geänderte Datei schreiben
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
    
    except Exception as e:
        result['error'] = str(e)
    
    return result


def main(dry_run: bool = True):
    """Hauptfunktion"""
    print("=" * 80)
    print("KOMPLETTE EMOJI-ENTFERNUNG FÜR BOKUK2-PROJEKT")
    print("=" * 80)
    print()
    
    if dry_run:
        print("  DRY-RUN MODUS (keine Änderungen)")
    else:
        print(" LIVE-MODUS (Dateien werden geändert!)")
    print()
    
    # Projektverzeichnis
    root_dir = Path.cwd()
    print(f"Projektverzeichnis: {root_dir}")
    print()
    
    # Python-Dateien finden
    print("Suche Python-Dateien...")
    python_files = find_all_python_files(root_dir)
    print(f"Gefunden: {len(python_files)} Python-Dateien")
    print()
    
    if not dry_run:
        # Backup-Verzeichnis erstellen
        BACKUP_DIR.mkdir(exist_ok=True)
        print(f"Backup-Verzeichnis: {BACKUP_DIR}")
        print()
    
    # Dateien verarbeiten
    print("Verarbeite Dateien...")
    print("-" * 80)
    
    results = []
    total_emojis_found = 0
    total_emojis_removed = 0
    files_modified = 0
    files_with_errors = 0
    
    for i, file_path in enumerate(python_files, 1):
        result = process_file(file_path, dry_run=dry_run)
        results.append(result)
        
        total_emojis_found += result['emojis_found']
        total_emojis_removed += result['emojis_removed']
        
        if result['modified']:
            files_modified += 1
            rel_path = file_path.relative_to(root_dir)
            status = "DRY-RUN" if dry_run else "GEÄNDERT"
            print(f"[{status}] {rel_path}: {result['emojis_removed']} Emojis entfernt")
        
        if result['error']:
            files_with_errors += 1
            rel_path = file_path.relative_to(root_dir)
            print(f"[FEHLER] {rel_path}: {result['error']}")
        
        # Fortschritts-Update alle 50 Dateien
        if i % 50 == 0:
            print(f"  ... {i}/{len(python_files)} Dateien verarbeitet")
    
    # Zusammenfassung
    print()
    print("=" * 80)
    print("ZUSAMMENFASSUNG")
    print("=" * 80)
    print(f"Dateien gesamt:         {len(python_files)}")
    print(f"Dateien mit Emojis:     {files_modified}")
    print(f"Dateien mit Fehlern:    {files_with_errors}")
    print(f"Emojis gefunden:        {total_emojis_found}")
    print(f"Emojis entfernt:        {total_emojis_removed}")
    print()
    
    if dry_run:
        print("=" * 80)
        print("DRY-RUN ABGESCHLOSSEN")
        print("=" * 80)
        print()
        print("Um die Änderungen wirklich durchzuführen:")
        print("  python remove_all_emojis_complete.py --live")
        print()
    else:
        print("=" * 80)
        print("ÄNDERUNGEN ABGESCHLOSSEN")
        print("=" * 80)
        print()
        print(f"Backup gespeichert in: {BACKUP_DIR}")
        print()
        print("Zum Rückgängigmachen:")
        print(f"  Kopieren Sie die Dateien aus {BACKUP_DIR} zurück")
        print()
    
    # Top 20 Dateien mit meisten Emojis
    if files_modified > 0:
        print("TOP 20 DATEIEN MIT MEISTEN EMOJIS:")
        print("-" * 80)
        
        sorted_results = sorted(
            [r for r in results if r['emojis_found'] > 0],
            key=lambda x: x['emojis_found'],
            reverse=True
        )[:20]
        
        for result in sorted_results:
            rel_path = result['path'].relative_to(root_dir)
            print(f"  {result['emojis_found']:3d} Emojis: {rel_path}")
        print()
    
    return results


if __name__ == '__main__':
    import sys
    
    # Kommandozeilen-Argument prüfen
    dry_run = '--live' not in sys.argv
    
    if not dry_run:
        print()
        print("  WARNUNG: Live-Modus aktiviert!")
        print("  Dateien werden permanent geändert!")
        print()
        
        confirmation = input("Fortfahren? (ja/nein): ").strip().lower()
        if confirmation != 'ja':
            print("Abgebrochen.")
            sys.exit(0)
        print()
    
    main(dry_run=dry_run)
