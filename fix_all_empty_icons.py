"""
fix_all_empty_icons.py
Entfernt automatisch alle leeren  Parameter aus Python-Dateien
"""

import re
from pathlib import Path

def fix_empty_icons_in_file(file_path: Path) -> tuple[bool, int]:
    """
    Entfernt leere  Parameter aus einer Datei.
    
    Returns:
        (changed, count) - Ob Datei geändert wurde und Anzahl Ersetzungen
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        # Pattern für:  oder 
        # Mit oder ohne Komma/Klammer danach
        patterns = [
            r',\s*icon\s*=\s*["\']["\']',  # 
            r'icon\s*=\s*["\'][\'"]\s*,',  # 
            r'\(\s*icon\s*=\s*["\']["\']',  # 
            r'icon\s*=\s*["\']["\']',      #  allgemein
        ]
        
        count = 0
        for pattern in patterns:
            matches = re.findall(pattern, content)
            count += len(matches)
            
            if ', icon=' in pattern or 'icon=' in pattern and ',' in pattern:
                # Entferne  inklusive Komma
                content = re.sub(pattern, '', content)
            else:
                # Nur  entfernen
                content = re.sub(pattern, '', content)
        
        # Zusätzliche Cleanup: Mehrfache Kommata
        content = re.sub(r',\s*,', ',', content)
        # Cleanup: Komma vor schließender Klammer
        content = re.sub(r',\s*\)', ')', content)
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True, count
        
        return False, 0
        
    except Exception as e:
        print(f"  Fehler bei {file_path}: {e}")
        return False, 0


def main():
    print("=" * 70)
    print("  EMOJI FIX - Entferne alle leeren  Parameter")
    print("=" * 70 + "\n")
    
    # Finde alle Python-Dateien
    py_files = []
    for py_file in Path(".").rglob("*.py"):
        # Überspringe Backups und Cache
        if any(skip in str(py_file) for skip in [
            "emoji_removal_backup",
            "__pycache__",
            ".venv",
            "venv",
            "build",
            "dist",
        ]):
            continue
        py_files.append(py_file)
    
    print(f"Prüfe {len(py_files)} Python-Dateien...\n")
    
    changed_files = []
    total_fixes = 0
    
    for py_file in py_files:
        changed, count = fix_empty_icons_in_file(py_file)
        if changed:
            changed_files.append((str(py_file), count))
            total_fixes += count
            print(f"  ✓ {py_file} - {count} Fixes")
    
    print("\n" + "=" * 70)
    print(f"  ERGEBNIS: {len(changed_files)} Dateien geändert, {total_fixes} Fixes")
    print("=" * 70 + "\n")
    
    if changed_files:
        print("Geänderte Dateien:")
        for file, count in changed_files[:20]:  # Erste 20
            print(f"  - {file} ({count})")
        
        if len(changed_files) > 20:
            print(f"  ... und {len(changed_files) - 20} weitere")
    else:
        print("Keine Änderungen notwendig - alle Dateien sind sauber!")


if __name__ == "__main__":
    main()
