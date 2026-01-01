# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
import importlib.metadata

block_cipher = None

# Daten-Dateien sammeln
datas = []

# Streamlit Metadata hinzufügen
try:
    st_dist = importlib.metadata.distribution('streamlit')
    # _path points to the dist-info directory
    st_dist_path = Path(st_dist._path)
    if st_dist_path.exists():
        datas.append((str(st_dist_path), st_dist_path.name))
        print(f"Added streamlit metadata from: {st_dist_path}")
except Exception as e:
    print(f"WARNING: Could not find streamlit metadata: {e}")

# Basis-Verzeichnisse die eingebunden werden sollen
data_dirs = [
    'data',
    'coords_multi',
    'pdf_templates_static',
    'customer_documents',
    '.streamlit',
]

# Nur existierende Verzeichnisse hinzufügen
for dir_name in data_dirs:
    dir_path = Path(dir_name)
    if dir_path.exists() and dir_path.is_dir():
        datas.append((str(dir_path), dir_name))

# Wichtige Einzeldateien
important_files = [
    'locales.py',
    'requirements.txt',
    'de.json',
]

for file_name in important_files:
    file_path = Path(file_name)
    if file_path.exists() and file_path.is_file():
        datas.append((str(file_path), '.'))

# Optionale Verzeichnisse (falls vorhanden)
optional_dirs = [
    'theming',
    'components',
    'core',
    'backend',
    'crm',
    'pdf_template_engine',
    'tools',
    'tests',
    'ui',
    'static',
    'assets',
]

for dir_name in optional_dirs:
    dir_path = Path(dir_name)
    if dir_path.exists() and dir_path.is_dir():
        datas.append((str(dir_path), dir_name))

# Hidden Imports - alle wichtigen Module
hiddenimports = [
    'streamlit',
    'streamlit.web.cli',
    'streamlit.runtime.scriptrunner.magic_funcs',
    'pandas',
    'numpy',
    'openpyxl',
    'reportlab',
    'pypdf',
    'PyPDF2',
    'pyvista',
    'pyvistaqt',
    'matplotlib',
    'plotly',
    'sqlite3',
    'json',
    'yaml',
    'toml',
    'PIL',
    'click',
    'altair',
    'tornado',
    'watchdog',
    'validators',
    'packaging',
    'pyarrow',
    'tzlocal',
    'pytz',
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'idna',
    'pydeck',
    'gitpython',
    'git',
]

# Binaries ausschließen (reduziert Größe)
binaries = []

a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'test', 'unittest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Ömers All in One Dingsbums',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Console für Debugging, später auf False setzen
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='data/company_logos/app_icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Ömers All in One Dingsbums',
)
