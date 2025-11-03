"""
PyInstaller Spec-Datei für Bokuk2 Solar Calculator
===================================================
Erstellt eine standalone .exe mit allen Dependencies
"""

# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Basis-Pfad
BASE_DIR = Path.cwd()

# Alle Python-Dateien die inkludiert werden müssen
python_files = [
    'gui.py',
    'analysis.py',
    'calculations.py',
    'calculations_extended.py',
    'calculations_heatpump.py',
    'solar_calculator.py',
    'admin_panel.py',
    'data_input.py',
    'crm.py',
    'init_database.py',
    'user_management.py',
    'user_menu.py',
    'intro_screen.py',
    'database.py',
    'database_bridge.py',
]

# Daten-Dateien die inkludiert werden müssen
datas = [
    # PDF Templates
    ('pdf_templates_static', 'pdf_templates_static'),
    ('coords', 'coords'),
    ('coords_multi', 'coords_multi'),
    ('coords_wp', 'coords_wp'),
    
    # Assets
    ('assets', 'assets'),
    ('static', 'static'),
    ('json', 'json'),
    
    # Streamlit Config
    ('.streamlit', '.streamlit'),
    
    # Config Files
    ('.env.example', '.'),
    ('requirements.txt', '.'),
]

# Hidden Imports (Module die PyInstaller nicht automatisch findet)
hiddenimports = [
    'streamlit',
    'streamlit.web.cli',
    'streamlit.runtime.scriptrunner.magic_funcs',
    'pandas',
    'numpy',
    'plotly',
    'reportlab',
    'pypdf',
    'PyPDF2',
    'PIL',
    'sqlalchemy',
    'pydantic',
    'yaml',
    'openpyxl',
    'altair',
    'pdfplumber',
    'matplotlib',
    'scipy',
    'sklearn',
    'pvlib',
    'numpy_financial',
]

# Binaries (DLLs etc.)
binaries = []

# Analysis - Findet alle Dependencies
a = Analysis(
    ['gui.py'],
    pathex=[str(BASE_DIR)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib.tests',
        'numpy.tests',
        'pandas.tests',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# PYZ - Komprimiert Python Bytecode
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None,
)

# EXE - Erstellt die ausführbare Datei
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Bokuk2_SolarCalculator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Console für Streamlit erforderlich
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if Path('assets/icon.ico').exists() else None,
)

# COLLECT - Sammelt alle Dateien in einem Verzeichnis
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Bokuk2_SolarCalculator',
)
