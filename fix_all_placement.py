#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fixe __all__ Platzierung - muss NACH allen Imports kommen
"""

from pathlib import Path
import re

def fix_all_placement(file_path: Path) -> bool:
    """Verschiebe __all__ nach allen Imports"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Finde __all__ Deklaration
        all_match = re.search(r'(__all__\s*=\s*\[.*?\])', content, re.DOTALL)
        if not all_match:
            return False
        
        all_declaration = all_match.group(1)
        
        # Entferne alte __all__ Deklaration
        content_without_all = content.replace(all_declaration, '')
        
        # Finde letzte Import-Zeile
        lines = content_without_all.split('\n')
        last_import_idx = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                last_import_idx = i
        
        # Füge __all__ nach letztem Import ein
        lines.insert(last_import_idx + 1, '\n' + all_declaration + '\n')
        
        # Schreibe zurück
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return True
    
    except Exception as e:
        print(f"[ERROR] {file_path.name}: {str(e)[:50]}")
        return False

# Files mit __all__ Problemen
PROBLEMATIC_FILES = [
    'analysis.py',
    'calculations.py',
    'pdf_generator.py',
    'database.py',
    'admin_panel.py',
    'heatpump_ui.py',
    'central_pdf_system.py',
    'admin_heatpump_settings_ui.py',
]

print("[TOOL] Fixe __all__ Platzierung...")
for file_name in PROBLEMATIC_FILES:
    file_path = Path(file_name)
    if file_path.exists():
        if fix_all_placement(file_path):
            print(f"[OK] {file_name}")
        else:
            print(f"[SKIP]  {file_name}: Kein __all__ gefunden")
    else:
        print(f"[SKIP]  {file_name}: Nicht gefunden")
