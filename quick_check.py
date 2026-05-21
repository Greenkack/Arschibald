#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Schnelle Final-Check ohne Details"""
import sys
import ast
import importlib
from pathlib import Path

# Syntax-Check
py_files = [f for f in Path('.').rglob('*.py') 
           if '__pycache__' not in str(f) and 'venv' not in str(f) and '_syntax_errors_backup' not in str(f)]
syntax_ok = 0
for f in py_files[:1000]:
    try:
        ast.parse(f.read_text(encoding='utf-8'))
        syntax_ok += 1
    except:
        pass

# Import-Check
critical_mods = ['admin_panel', 'analysis', 'calculations', 'database', 'pdf_generator', 
                'heatpump_products_database', 'central_pdf_system']
imports_ok = 0
for mod in critical_mods:
    try:
        importlib.import_module(mod)
        imports_ok += 1
    except:
        pass

print("="*60)
print("SCHNELL-CHECK ERGEBNIS")
print("="*60)
print(f"SYNTAX:  {syntax_ok}/{len(py_files[:1000])} OK ({syntax_ok/len(py_files[:1000])*100:.1f}%)")
print(f"IMPORTS: {imports_ok}/{len(critical_mods)} OK ({imports_ok/len(critical_mods)*100:.1f}%)")
print("="*60)
