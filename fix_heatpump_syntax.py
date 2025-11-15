"""
Fix broken if-statements in heatpump_ui.py

Das Auto-Fix-Tool hat unsinnige Division-by-Zero Checks eingefügt.
Dieses Script entfernt sie.
"""

import re

def fix_heatpump_ui():
    """Repariert alle kaputten if-Statements in heatpump_ui.py"""
    
    filepath = "heatpump_ui.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern 1: if ZAHL != 0: EXPR else: 0.0 → EXPR
    # Beispiel: if 1190 != 0: oil_l / 1190.0 if oil_l > 0 else 0 else: oil_tons = 0.0
    
    # Pattern für Divisionen mit sinnlosem Check
    patterns = [
        # Pattern: if KONSTANTE != 0:\n    VAR = EXPR\nelse:\n    VAR = 0.0
        (r'if (\d+) != 0:\s+(\w+) = ([^;]+?)\s+else:\s+\2 = 0\.0', r'\2 = \3'),
        
        # Pattern in st.metric: if KONSTANTE != 0:\n    delta=... else: delta=...
        (r'if (\d+) != 0:\s+delta=([^;]+?)\s+else:\s+delta = [^;]+', r'delta=\2'),
        
        # Pattern in go.Scatter3d: if 2 != 0:\n    x=[...],\nelse:\n    x = 0.0
        (r'if 2 != 0:\s+x=(\[[^\]]+\]),\s+else:\s+x = 0\.0', r'x=\1,'),
        (r'if 2 != 0:\s+z=(\[[^\]]+\]),\s+else:\s+z = 0\.0', r'z=\1,'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Manuelle Fixes für spezifische Fälle
    fixes = [
        # Line 452: oil_tons
        (
            """oil_tons = oil_l / 1190.0 if oil_l > 0 else 0""",
            "oil_tons = oil_l / 1190.0 if oil_l > 0 else 0"
        ),
        # Line 2749-2753: go.Scatter3d x parameter
        (
            """x = [hp_x_offset + hp_width/2, 0],
                        y=[0, 0],
                        z = [hp_height/2, building_height/2],""",
            """x=[hp_x_offset + hp_width/2, 0],
                        y=[0, 0],
                        z=[hp_height/2, building_height/2],"""
        ),
    ]
    
    for old, new in fixes:
        content = content.replace(old, new)
    
    # Schreibe reparierte Datei
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    changes = len(content) - len(original_content)
    print(f"{filepath} repariert")
    print(f"   Größenänderung: {changes:+d} Zeichen")
    
    # Teste Import
    try:
        import heatpump_ui
        print("Import-Test erfolgreich")
        return True
    except SyntaxError as e:
        print(f"Syntax-Fehler bleibt: {e}")
        return False

if __name__ == "__main__":
    success = fix_heatpump_ui()
    exit(0 if success else 1)
