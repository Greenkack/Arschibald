#!/usr/bin/env python
"""
fix_all_tuple_errors.py
=======================
Automatisches Fixen aller Database-Tuple-Fehler im gesamten Projekt.

Problem: cursor.execute(..., (variable)) → FALSCH (String)
Fix:     cursor.execute(..., (variable,)) → RICHTIG (Tuple)
"""
import re
from pathlib import Path

def fix_tuple_errors(file_path: Path) -> int:
    """
    Findet und fixt Tuple-Fehler in einer Python-Datei.
    
    Returns:
        Anzahl der gefixten Fehler
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Regex-Pattern: cursor.execute(..., (variable)) ohne Komma
        # Sucht nach: (variable) am Ende, gefolgt von )
        pattern = r'cursor\.execute\([^)]+\?,\s*\(([a-zA-Z_][a-zA-Z0-9_]*)\)\)'
        
        # Ersetze (variable) mit (variable,)
        def replacer(match):
            var_name = match.group(1)
            # Rekonstruiere den kompletten Match mit Komma
            return match.group(0).replace(f'({var_name})', f'({var_name},)')
        
        content = re.sub(pattern, replacer, content)
        
        # Zähle Änderungen
        changes = content.count(',)') - original_content.count(',)')
        
        if changes > 0:
            # Speichere nur wenn Änderungen vorhanden
            file_path.write_text(content, encoding='utf-8')
            print(f"✅ {file_path.name}: {changes} Fehler gefixt")
            return changes
        
        return 0
        
    except Exception as e:
        print(f"⚠️ Fehler bei {file_path.name}: {e}")
        return 0

def main():
    """Scanne alle Python-Dateien und fixe Tuple-Fehler."""
    project_root = Path(__file__).parent
    
    # Ignoriere bestimmte Verzeichnisse
    ignore_dirs = {'.venv', 'venv', 'env', '__pycache__', 'node_modules', 
                   '.git', 'dist', 'build', 'emoji_removal_backup_20251206_221253'}
    
    total_fixes = 0
    files_fixed = 0
    
    print("🔍 Scanne Projekt nach Tuple-Fehlern...\n")
    
    # Scanne alle .py Dateien
    for py_file in project_root.rglob('*.py'):
        # Ignoriere Backup-Verzeichnisse
        if any(ignore_dir in py_file.parts for ignore_dir in ignore_dirs):
            continue
        
        fixes = fix_tuple_errors(py_file)
        if fixes > 0:
            total_fixes += fixes
            files_fixed += 1
    
    print(f"\n{'='*60}")
    print(f"🎉 FERTIG!")
    print(f"{'='*60}")
    print(f"Dateien gefixt: {files_fixed}")
    print(f"Fehler gefixt: {total_fixes}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
