#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Findet undefinierte Single-Letter Variablen (Überbleibsel von Auto-Fixes)
"""

import ast
import re
from pathlib import Path

def check_file(file_path):
    """Prüft eine Datei auf undefinierte Variablen"""
    try:
        code = file_path.read_text(encoding='utf-8')
        
        # Erst Syntax prüfen
        try:
            ast.parse(code)
        except SyntaxError:
            return []  # Syntax-Fehler werden separat gehandhabt
        
        problems = []
        
        # Suche nach 'if SINGLE_LETTER <op>' Pattern
        pattern = re.compile(r'\bif\s+([A-Z])\s*[!=<>]', re.MULTILINE)
        matches = pattern.finditer(code)
        
        for match in matches:
            line_num = code[:match.start()].count('\n') + 1
            var_name = match.group(1)
            
            # Prüfe ob Variable vorher definiert wurde
            code_before = code[:match.start()]
            var_def = re.search(rf'^\s*{var_name}\s*=', code_before, re.MULTILINE)
            
            if not var_def:
                # Hole Kontext-Zeile
                lines = code.split('\n')
                context = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                problems.append({
                    'file': str(file_path.relative_to(Path.cwd())),
                    'line': line_num,
                    'var': var_name,
                    'context': context
                })
        
        return problems
        
    except Exception:
        return []

def main():
    print("=" * 80)
    print("SUCHE NACH UNDEFINIERTEN SINGLE-LETTER VARIABLEN")
    print("=" * 80)
    print()
    
    # Nur Python-Dateien in relevanten Ordnern
    root = Path('.')
    patterns = ['*.py']
    exclude_dirs = {'.venv', '__pycache__', '.git', 'venv', 'env', 'node_modules'}
    
    all_problems = []
    
    for pattern in patterns:
        for file_path in root.rglob(pattern):
            # Überspringe ausgeschlossene Ordner
            if any(ex in file_path.parts for ex in exclude_dirs):
                continue
            
            problems = check_file(file_path)
            all_problems.extend(problems)
    
    if all_problems:
        print(f"GEFUNDEN: {len(all_problems)} undefinierte Variablen\n")
        
        for p in all_problems:
            print(f"{p['file']}")
            print(f"   Zeile {p['line']}: Variable '{p['var']}' undefiniert")
            print(f"   Code: {p['context']}")
            print()
    else:
        print("Keine undefinierten Single-Letter Variablen gefunden!")
    
    print("=" * 80)
    return len(all_problems)

if __name__ == "__main__":
    exit(main())
