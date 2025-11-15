#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Füge __all__ Deklarationen zu allen kritischen Modulen hinzu
"""

import ast
import re
from pathlib import Path
from typing import List, Set

# Liste der 25 Module ohne __all__
MODULES_NEEDING_ALL = [
    'admin_panel.py',
    'heatpump_ui.py',
    'analysis.py',
    'calculations.py',
    'database.py',
    'pdf_generator.py',
    'central_pdf_system.py',
    'admin_heatpump_settings_ui.py',
    'admin_heating_costs_config_ui.py',
    'admin_logo_management_ui.py',
    'admin_payment_terms_ui.py',
    'heatpump_products_database.py',
    'calculations_heatpump.py',
    'pdf_template_engine.py',
    'pdf_ui.py',
    'pdf_preview.py',
    'pv3d.py',
    'pv3d_plotly.py',
    'pdf_visual_inject.py',
    'utils.py',
    'debug_tools.py',
    'theme_manager.py',
    'product_db.py',
    'brand_logo_db.py',
    'price_matrix_store.py',
]

def extract_public_names(file_path: Path) -> Set[str]:
    """Extrahiere alle öffentlichen Namen aus einem Modul"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        
        public_names = set()
        
        for node in ast.walk(tree):
            # Funktionen
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_'):
                    public_names.add(node.name)
            
            # Klassen
            elif isinstance(node, ast.ClassDef):
                if not node.name.startswith('_'):
                    public_names.add(node.name)
            
            # Variablen (nur Top-Level)
            elif isinstance(node, ast.Assign):
                if hasattr(node, 'targets'):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if not target.id.startswith('_') and target.id.isupper():
                                public_names.add(target.id)
        
        return public_names
    
    except Exception as e:
        print(f"   Fehler beim Parsen von {file_path.name}: {str(e)[:50]}")
        return set()

def has_all_declaration(file_path: Path) -> bool:
    """Prüfe ob Modul bereits __all__ hat"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return '__all__' in content
    except:
        return False

def add_all_declaration(file_path: Path, public_names: Set[str]) -> bool:
    """Füge __all__ Deklaration hinzu"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Finde erste Code-Zeile nach Imports
        insert_position = 0
        in_docstring = False
        docstring_marker = None
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Docstring-Behandlung
            if i == 0 and (stripped.startswith('"""') or stripped.startswith("'''")):
                docstring_marker = stripped[:3]
                in_docstring = True
                continue
            
            if in_docstring:
                if docstring_marker in stripped:
                    in_docstring = False
                    insert_position = i + 1
                continue
            
            # Skip Kommentare und Imports
            if stripped.startswith('#'):
                continue
            if stripped.startswith('import ') or stripped.startswith('from '):
                insert_position = i + 1
                continue
            
            # Erste echte Code-Zeile gefunden
            if stripped and not stripped.startswith('#'):
                break
        
        # Erstelle __all__ Deklaration
        sorted_names = sorted(public_names)
        if len(sorted_names) <= 5:
            all_decl = f"__all__ = {sorted_names}\n\n"
        else:
            # Mehrzeilig für bessere Lesbarkeit
            all_decl = "__all__ = [\n"
            for name in sorted_names:
                all_decl += f"    '{name}',\n"
            all_decl += "]\n\n"
        
        # Einfügen
        lines.insert(insert_position, all_decl)
        
        # Zurückschreiben
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return True
    
    except Exception as e:
        print(f"   Fehler beim Schreiben: {str(e)[:50]}")
        return False

def main():
    print("=" * 80)
    print("__all__ DEKLARATIONEN HINZUFÜGEN")
    print("=" * 80)
    print(f"\nBearbeite {len(MODULES_NEEDING_ALL)} Module...\n")
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for module_name in MODULES_NEEDING_ALL:
        file_path = Path(module_name)
        
        if not file_path.exists():
            print(f"{module_name}: Nicht gefunden")
            skip_count += 1
            continue
        
        if has_all_declaration(file_path):
            print(f"{module_name}: Hat bereits __all__")
            skip_count += 1
            continue
        
        print(f"{module_name}: Analysiere...")
        
        public_names = extract_public_names(file_path)
        
        if not public_names:
            print(f"   Keine öffentlichen Namen gefunden, skip")
            skip_count += 1
            continue
        
        print(f"   {len(public_names)} öffentliche Namen gefunden")
        
        if add_all_declaration(file_path, public_names):
            print(f"   __all__ hinzugefügt")
            success_count += 1
        else:
            error_count += 1
    
    print("\n" + "=" * 80)
    print("FERTIG")
    print("=" * 80)
    print(f"Erfolgreich: {success_count}")
    print(f"Übersprungen: {skip_count}")
    print(f"Fehler: {error_count}")

if __name__ == "__main__":
    main()
