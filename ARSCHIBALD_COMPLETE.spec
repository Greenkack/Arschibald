# -*- mode: python ; coding: utf-8 -*-
# OemersBokuk4all COMPLETE - Vollständige Build-Konfiguration
# Alle Komponenten, keine Ausnahmen, 100% funktionsfähig

import sys
import os
from pathlib import Path
import site

block_cipher = None

# Basis-Pfad
BASE_DIR = os.path.dirname(os.path.abspath(SPEC))

# ===== DATEN-DATEIEN SAMMELN =====
datas = []

# Kritische Einzeldateien
critical_files = [
    'de.json',              # Sprachdatei MUSS enthalten sein
    'locales.py',           # Lokalisierungsmodul
    'requirements.txt',     # Dependencies
    'database.py',          # Hauptdatenbank
    'calculations.py',      # Berechnungen
    'calculations_heatpump.py',
    'pdf_generator.py',     # PDF-Engine
    'product_rotation_engine.py',
    'price_modification_engine.py',
]

for file_name in critical_files:
    file_path = Path(file_name)
    if file_path.exists():
        datas.append((str(file_path), '.'))
        print(f"✓ Datei hinzugefügt: {file_name}")

# Alle Datenverzeichnisse - VOLLSTÄNDIG
data_dirs = [
    'data',
    'coords_multi',
    'pdf_templates_static',
    'pdf_template_engine',
    'customer_documents',
    '.streamlit',
    'theming',
    'components',
    'core',
    'backend',
    'crm',
    'tools',
    'ui',
    'static',
    'assets',
    'tests',
    'Agent',
    'nützliche tools',
]

for dir_name in data_dirs:
    dir_path = Path(dir_name)
    if dir_path.exists() and dir_path.is_dir():
        datas.append((str(dir_path), dir_name))
        print(f"✓ Verzeichnis hinzugefügt: {dir_name}")

# ===== ALLE DIST-INFO METADATEN =====
# Dies ist KRITISCH für importlib.metadata
site_packages = site.getsitepackages()
if isinstance(site_packages, list):
    site_packages_dir = site_packages[0]
else:
    site_packages_dir = site_packages

# Wichtigste Pakete mit Metadaten
critical_packages = [
    'streamlit',
    'pandas',
    'numpy',
    'plotly',
    'pyvista',
    'matplotlib',
    'reportlab',
    'pypdf',
    'PyPDF2',
    'openpyxl',
    'pillow',
    'altair',
    'click',
    'tornado',
    'pyarrow',
    'sqlalchemy',
    'pydantic',
    'requests',
    'urllib3',
    'certifi',
    'packaging',
    'protobuf',
    'langchain',
    'langchain_core',
    'langchain_openai',
    'langchain_community',
    'langchain_anthropic',
    'anthropic',
    'openai',
    'tiktoken',
    'faiss',
    'chromadb',
    'transformers',
    'torch',
    'tensorflow',
    'scikit-learn',
    'duckdb',
    'duckdb-engine',
]

# Suche und füge alle dist-info Ordner hinzu
for pkg in critical_packages:
    for sp_dir in site.getsitepackages():
        sp_path = Path(sp_dir)
        if not sp_path.exists():
            continue
        # Suche nach allen möglichen Varianten
        patterns = [
            f"{pkg}-*.dist-info",
            f"{pkg.lower()}-*.dist-info",
            f"{pkg.upper()}-*.dist-info",
            f"{pkg.replace('-', '_')}-*.dist-info",
        ]
        for pattern in patterns:
            for dist_info in sp_path.glob(pattern):
                if dist_info.is_dir():
                    datas.append((str(dist_info), dist_info.name))
                    print(f"✓ Metadata hinzugefügt: {dist_info.name}")
                    break

# ===== HIDDEN IMPORTS - VOLLSTÄNDIG =====
hiddenimports = [
    # Streamlit Core
    'streamlit',
    'streamlit.web.cli',
    'streamlit.web.bootstrap',
    'streamlit.runtime',
    'streamlit.runtime.scriptrunner',
    'streamlit.runtime.scriptrunner.magic_funcs',
    'streamlit.runtime.state',
    'streamlit.runtime.state.session_state',
    'streamlit.runtime.state.session_state_proxy',
    'streamlit.runtime.caching',
    'streamlit.runtime.legacy_caching',
    'streamlit.elements',
    'streamlit.components',
    'streamlit.components.v1',
    
    # Encodings - KRITISCH
    'encodings',
    'encodings.utf_8',
    'encodings.cp1252',
    'encodings.latin_1',
    'encodings.ascii',
    'encodings.idna',
    
    # Standard Library
    'sqlite3',
    'json',
    'csv',
    'xml',
    'xml.etree',
    'xml.etree.ElementTree',
    'email',
    'email.mime',
    'email.mime.text',
    'email.mime.multipart',
    'urllib',
    'urllib.request',
    'urllib.parse',
    'http',
    'http.client',
    
    # DuckDB - KRITISCH für Core-System
    'duckdb',
    'duckdb_engine',
    'duckdb_engine.dialect',
    'sqlalchemy.dialects.duckdb',
    
    # Data Processing
    'pandas',
    'pandas._libs',
    'pandas._libs.tslibs',
    'numpy',
    'numpy.core',
    'numpy.core._multiarray_umath',
    'openpyxl',
    'openpyxl.styles',
    'pyarrow',
    'pyarrow.parquet',
    
    # PDF
    'reportlab',
    'reportlab.pdfgen',
    'reportlab.pdfgen.canvas',
    'reportlab.lib',
    'reportlab.lib.pagesizes',
    'reportlab.lib.colors',
    'reportlab.lib.units',
    'pypdf',
    'PyPDF2',
    'pymupdf',
    'fitz',
    
    # AI & LangChain - VOLLSTÄNDIG
    'langchain',
    'langchain.agents',
    'langchain.chains',
    'langchain.prompts',
    'langchain.memory',
    'langchain.callbacks',
    'langchain.schema',
    'langchain.tools',
    'langchain.text_splitter',
    'langchain.document_loaders',
    'langchain.vectorstores',
    'langchain_core',
    'langchain_core.messages',
    'langchain_core.prompts',
    'langchain_core.tools',
    'langchain_core.language_models',
    'langchain_core.runnables',
    'langchain_openai',
    'langchain_openai.chat_models',
    'langchain_openai.embeddings',
    'langchain_community',
    'langchain_community.document_loaders',
    'langchain_community.vectorstores',
    'langchain_community.embeddings',
    'langchain_anthropic',
    'anthropic',
    'openai',
    'openai.types',
    'tiktoken',
    'tiktoken_ext',
    'tiktoken_ext.openai_public',
    'faiss',
    'chromadb',
    'chromadb.api',
    'chromadb.config',
    
    # ML/AI Libraries
    'transformers',
    'transformers.models',
    'torch',
    'torch.nn',
    'torch.utils',
    'torch.utils.data',
    'tensorflow',
    'tensorflow.keras',
    'sklearn',
    'sklearn.preprocessing',
    'sklearn.feature_extraction',
    'sklearn.metrics',
    
    # Visualization
    'matplotlib',
    'matplotlib.pyplot',
    'matplotlib.backends',
    'matplotlib.backends.backend_agg',
    'plotly',
    'plotly.express',
    'plotly.graph_objects',
    'altair',
    'bokeh',
    'pyvista',
    'pyvistaqt',
    'vtk',
    
    # PIL/Pillow
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    
    # Web/API
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'idna',
    'aiohttp',
    'fastapi',
    'starlette',
    'uvicorn',
    
    # Configuration
    'yaml',
    'toml',
    'configparser',
    'packaging',
    'packaging.version',
    'packaging.specifiers',
    
    # Database
    'sqlalchemy',
    'sqlalchemy.ext',
    'sqlalchemy.ext.declarative',
    'sqlalchemy.orm',
    
    # Scientific
    'scipy',
    'scipy.special',
    'scipy.stats',
    'sklearn',
    'statsmodels',
    
    # Utilities
    'click',
    'tornado',
    'watchdog',
    'validators',
    'pytz',
    'tzlocal',
    'dateutil',
    'dateutil.parser',
    'tqdm',
    'rich',
    
    # Cryptography
    'cryptography',
    'bcrypt',
    
    # AI/ML (falls verwendet)
    'torch',
    'transformers',
    'langchain',
    'langchain.agents',
    'langchain.chains',
    'langchain.llms',
    
    # Project-specific
    'locales',
    'database',
    'calculations',
    'calculations_heatpump',
    'pdf_generator',
    'product_rotation_engine',
    'price_modification_engine',
]

# ===== BINARIES =====
binaries = []

# ===== ANALYSIS =====
a = Analysis(
    ['gui.py'],
    pathex=[BASE_DIR],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        '_tkinter',
        'test',
        'unittest',
        'pytest',
        'hypothesis',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ===== PYZ =====
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

# ===== EXE =====
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OemersBokuk4all',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # True für Debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='data/company_logos/app_icon.ico' if os.path.exists('data/company_logos/app_icon.ico') else None,
)

# ===== COLLECT =====
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OemersBokuk4all',
)
