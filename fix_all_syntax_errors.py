"""
Comprehensive Syntax Error Fixer
Behebt alle kaputten Auto-Fixes aus fix_all_issues.py
"""

import re
import os
from pathlib import Path

def fix_broken_auto_fixes():
    """Findet und behebt alle kaputten if-Statements."""
    
    fixed_files = []
    errors = []
    
    # Alle Python-Dateien durchsuchen
    for py_file in Path('.').rglob('*.py'):
        if any(skip in str(py_file) for skip in ['venv', '.git', '__pycache__', 'site-packages']):
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original = content
            
            # Pattern 1: if ZAHL != 0:\n    VAR OP= EXPR\nelse:\n    VAR OP = 0.0
            # Beispiel: if 1190 != 0:\n    oil_tons = oil_l / 1190.0\nelse:\n    oil_tons = 0.0
            pattern1 = r'if (\d+) != 0:\s+(\w+)\s*([+\-*/]?=)\s*([^\n]+)\s+else:\s+\2\s*\3\s*0\.0'
            content = re.sub(pattern1, r'\2 \3 \4', content, flags=re.MULTILINE)
            
            # Pattern 2: Falsche Operatoren (Leerzeichen in +=, -=, etc.)
            # Beispiel: total = 0.0 → total = 0.0
            content = re.sub(r'(\w+)\s*([+\-*/])\s+=\s*0\.0', r'\1 = 0.0', content)
            
            # Pattern 3: if in dict initialization
            # Beispiel: if VAR != 0:\n    x=[...],\nelse:\n    x = 0.0
            pattern3 = r'if \d+ != 0:\s+([xyz])=(\[[^\]]+\]),\s+else:\s+\1 = 0\.0'
            content = re.sub(pattern3, r'\1=\2,', content, flags=re.MULTILINE | re.DOTALL)
            
            # Pattern 4: if in eye=dict(...) context
            pattern4 = r'if (\w+) != 0:\s+([xyz])=([^,\n]+),\s+else:\s+\2 = 0\.0'
            def replace_eye_dict(match):
                var = match.group(1)
                axis = match.group(2)
                expr = match.group(3).strip()
                return f'{axis}={expr} if {var} != 0 else 0.0,'
            content = re.sub(pattern4, replace_eye_dict, content, flags=re.MULTILINE | re.DOTALL)
            
            # Pattern 5: if with center=dict
            pattern5 = r'if \d+ != 0:\s+center=(dict\([^)]+\))\s+else:\s+center = 0\.0'
            content = re.sub(pattern5, r'center=\1', content, flags=re.MULTILINE | re.DOTALL)
            
            if content != original:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_files.append(str(py_file))
                print(f"[OK] Fixed: {py_file}")
        
        except Exception as e:
            errors.append((str(py_file), str(e)))
    
    return fixed_files, errors


if __name__ == "__main__":
    print("="*80)
    print("COMPREHENSIVE SYNTAX ERROR FIXER")
    print("="*80)
    print("Suche nach kaputten Auto-Fixes...\n")
    
    fixed, errors = fix_broken_auto_fixes()
    
    print(f"\n{'='*80}")
    print(f"[OK] {len(fixed)} Dateien repariert")
    if fixed:
        for f in fixed:
            print(f"   - {f}")
    
    if errors:
        print(f"\n[ERROR] {len(errors)} Fehler:")
        for f, e in errors:
            print(f"   - {f}: {e}")
    
    print(f"{'='*80}\n")
    
    # Test imports
    print("Teste kritische Module...")
    test_modules = ['product_db', 'calculations', 'heatpump_ui', 'solar_calculator', 'analysis']
    
    success = 0
    for module in test_modules:
        try:
            __import__(module)
            print(f"[OK] {module}")
            success += 1
        except SyntaxError as e:
            print(f"[ERROR] {module}: {e}")
        except Exception as e:
            print(f"[WARNING]  {module}: {e}")
    
    print(f"\n{success}/{len(test_modules)} Module erfolgreich importiert")
