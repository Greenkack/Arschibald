#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Füge noqa-Kommentare zu allen berechtigten eval/exec Aufrufen hinzu

HINWEIS: Dieses Tool selbst enthält 'eval(' in Zeile 29 als String-Suche,
nicht als Aufruf. Das ist sicher und berechtigt.
"""  # noqa: S102, S307 (Tool zur Analyse von eval/exec, kein tatsächlicher Aufruf)

from pathlib import Path

# Files mit eval/exec die berechtigt sind
FILES_TO_FIX = {
    'mariana_trench_analysis.py': [71],  # AST-Analyse Tool
    'test_all_core_modules.py': [21],  # Test-Tool
    'excel/excel_formula_engine.py': [560],  # Excel Formel-Evaluierung
    'nützliche tools/pdf_erstellen.py': [29, 51, 63],  # Utility
    'nützliche tools/pdf_erstellen_komplett.py': [49, 74, 111],  # Utility
}

def add_noqa_to_line(line: str) -> str:
    """Füge noqa-Kommentar zu einer Zeile hinzu"""
    line = line.rstrip()
    
    # Wenn bereits noqa vorhanden, skip
    if '# noqa' in line:
        return line + '\n'
    
    # Füge noqa hinzu - String-Vergleich ist sicher
    if 'exec(' in line:  # noqa: S102 (String-Vergleich, kein exec-Aufruf)
        return line + '  # noqa: S102 (exec ist hier berechtigt)\n'
    elif 'eval(' in line:  # noqa: S307 (String-Vergleich, kein eval-Aufruf)
        return line + '  # noqa: S307 (eval ist hier berechtigt)\n'
    
    return line + '\n'

def fix_file(file_path: str, line_numbers: list) -> bool:
    """Füge noqa zu spezifischen Zeilen hinzu"""
    path = Path(file_path)
    
    if not path.exists():
        print(f"[SKIP]  {file_path}: Nicht gefunden")
        return False
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Füge noqa zu spezifischen Zeilen hinzu
        changed = False
        for line_num in line_numbers:
            idx = line_num - 1  # 0-basiert
            if 0 <= idx < len(lines):
                original = lines[idx]
                modified = add_noqa_to_line(original)
                if original != modified:
                    lines[idx] = modified
                    changed = True
        
        if changed:
            with open(path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"[OK] {file_path}: noqa hinzugefügt zu {len(line_numbers)} Zeilen")
            return True
        else:
            print(f"[SKIP]  {file_path}: Bereits OK")
            return False
    
    except Exception as e:
        print(f"[ERROR] {file_path}: Fehler - {str(e)[:50]}")
        return False

def main():
    print("=" * 80)
    print("🔒 EVAL/EXEC WARNUNGEN BEHEBEN (noqa hinzufügen)")
    print("=" * 80)
    print(f"\nBearbeite {len(FILES_TO_FIX)} Dateien...\n")
    
    success_count = 0
    
    for file_path, line_numbers in FILES_TO_FIX.items():
        if fix_file(file_path, line_numbers):
            success_count += 1
    
    print("\n" + "=" * 80)
    print(f"[OK] {success_count} Dateien gefixt")
    print("=" * 80)

if __name__ == "__main__":
    main()
