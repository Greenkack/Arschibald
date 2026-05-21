#!/usr/bin/env python3
"""
Script zum Entfernen aller [TAG]-Markierungen aus Python-Dateien.
Entfernt alle Texte in eckigen Klammern wie [OK], [FILE], [CHART], etc.
"""

import re
import os
from pathlib import Path

# Dateien die ignoriert werden sollen
IGNORE_FILES = {
    'remove_all_tags.py',
    'remove_bracket_tags.py',
    '.git',
    '__pycache__',
    'node_modules',
    '.venv',
    'venv',
}

# Verzeichnisse die ignoriert werden sollen
IGNORE_DIRS = {
    '.git',
    '__pycache__',
    'node_modules',
    '.venv',
    'venv',
    'logs',
    '.kiro',
    'docs',
}

def should_process_file(filepath):
    """Prüft ob eine Datei verarbeitet werden soll."""
    # Nur Python-Dateien
    if not filepath.endswith('.py'):
        return False
    
    # Ignorierte Dateien überspringen
    if any(ignore in str(filepath) for ignore in IGNORE_FILES):
        return False
    
    # Ignorierte Verzeichnisse überspringen
    if any(ignore in str(filepath) for ignore in IGNORE_DIRS):
        return False
    
    return True

def remove_tags_from_content(content):
    """Entfernt [TAG]-Markierungen aus dem Inhalt."""
    
    # Pattern für alle [TAG]-Markierungen
    patterns = [
        # Standard Tags in Strings
        (r'\[OK\]\s*', ''),
        (r'\[FILE\]\s*', ''),
        (r'\[CHART\]\s*', ''),
        (r'\[PACKAGE\]\s*', ''),
        (r'\[TARGET\]\s*', ''),
        (r'\[SEARCH\]\s*', ''),
        (r'\[TOOL\]\s*', ''),
        (r'\[INFO\]\s*', ''),
        (r'\[DELETE\]\s*', ''),
        (r'\[DISPLAY\]\s*', ''),
        (r'\[TRUE\]\s*', ''),
        (r'\[FALSE\]\s*', ''),
        (r'\[ERROR\]\s*', ''),
        (r'\[SUCCESS\]\s*', ''),
        (r'\[WARNING\]\s*', ''),
        (r'\[DEBUG\]\s*', ''),
        
        # Tags mit Leerzeichen davor
        (r'\s+\[OK\]', ''),
        (r'\s+\[FILE\]', ''),
        (r'\s+\[CHART\]', ''),
        (r'\s+\[PACKAGE\]', ''),
        (r'\s+\[TARGET\]', ''),
        (r'\s+\[SEARCH\]', ''),
        (r'\s+\[TOOL\]', ''),
        (r'\s+\[INFO\]', ''),
        (r'\s+\[DELETE\]', ''),
        (r'\s+\[DISPLAY\]', ''),
    ]
    
    modified_content = content
    replacements_made = 0
    
    for pattern, replacement in patterns:
        before = modified_content
        modified_content = re.sub(pattern, replacement, modified_content)
        if before != modified_content:
            replacements_made += re.subn(pattern, replacement, before)[1]
    
    return modified_content, replacements_made

def process_file(filepath):
    """Verarbeitet eine einzelne Datei."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        modified_content, replacements = remove_tags_from_content(original_content)
        
        if replacements > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            return True, replacements
        
        return False, 0
        
    except Exception as e:
        print(f"❌ Fehler bei {filepath}: {e}")
        return False, 0

def main():
    """Hauptfunktion - durchsucht alle Python-Dateien und entfernt Tags."""
    
    workspace_root = Path(__file__).parent
    print(f"🔍 Durchsuche Workspace: {workspace_root}")
    print("=" * 60)
    
    total_files = 0
    modified_files = 0
    total_replacements = 0
    
    # Durchsuche alle Python-Dateien
    for root, dirs, files in os.walk(workspace_root):
        # Entferne ignorierte Verzeichnisse aus der Suche
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            filepath = os.path.join(root, file)
            
            if should_process_file(filepath):
                total_files += 1
                was_modified, replacements = process_file(filepath)
                
                if was_modified:
                    modified_files += 1
                    total_replacements += replacements
                    rel_path = os.path.relpath(filepath, workspace_root)
                    print(f"✅ {rel_path}: {replacements} Tags entfernt")
    
    print("=" * 60)
    print(f"\n📊 Zusammenfassung:")
    print(f"   Dateien gescannt: {total_files}")
    print(f"   Dateien modifiziert: {modified_files}")
    print(f"   Tags entfernt: {total_replacements}")
    print("\n✨ Fertig! Alle [TAG]-Markierungen wurden entfernt.")

if __name__ == "__main__":
    main()
