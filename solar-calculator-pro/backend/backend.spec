# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Solar Calculator Pro Backend

This spec file packages the FastAPI backend into a standalone executable
that can be bundled with the Electron application.

Usage:
    pyinstaller backend.spec

Output:
    dist/backend.exe (Windows)
    dist/backend (Linux/macOS)
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Get the backend directory
backend_dir = os.path.abspath(SPECPATH)

# Collect all data files
datas = []

# Add templates if they exist
templates_dir = os.path.join(backend_dir, 'templates')
if os.path.exists(templates_dir):
    datas.append((templates_dir, 'templates'))

# Add static files if they exist
static_dir = os.path.join(backend_dir, 'static')
if os.path.exists(static_dir):
    datas.append((static_dir, 'static'))

# Add migrations
migrations_dir = os.path.join(backend_dir, 'migrations')
if os.path.exists(migrations_dir):
    datas.append((migrations_dir, 'migrations'))

# Add .env.example
env_example = os.path.join(backend_dir, '.env.example')
if os.path.exists(env_example):
    datas.append((env_example, '.'))

# Collect data files from packages
datas += collect_data_files('fastapi')
datas += collect_data_files('uvicorn')
datas += collect_data_files('sqlalchemy')
datas += collect_data_files('alembic')

# Hidden imports - modules that PyInstaller might miss
hiddenimports = [
    # FastAPI and dependencies
    'fastapi',
    'fastapi.routing',
    'fastapi.responses',
    'fastapi.middleware',
    'fastapi.middleware.cors',
    'fastapi.staticfiles',
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    
    # Database
    'sqlalchemy',
    'sqlalchemy.ext.asyncio',
    'sqlalchemy.orm',
    'sqlalchemy.pool',
    'aiosqlite',
    'alembic',
    'alembic.runtime',
    'alembic.runtime.migration',
    
    # Authentication
    'jose',
    'jose.jwt',
    'passlib',
    'passlib.context',
    'passlib.hash',
    
    # Validation
    'pydantic',
    'pydantic.fields',
    'pydantic.main',
    'pydantic_settings',
    
    # WebSocket
    'socketio',
    'python_socketio',
    
    # Security
    'slowapi',
    
    # Utilities
    'dateutil',
    'dateutil.parser',
    'dotenv',
    
    # Performance
    'redis',
    'psutil',
    'aiofiles',
    
    # Standard library modules that might be missed
    'email.mime',
    'email.mime.text',
    'email.mime.multipart',
    'email.mime.base',
    'email.encoders',
]

# Collect all submodules from our application
hiddenimports += collect_submodules('api')
hiddenimports += collect_submodules('core')
hiddenimports += collect_submodules('models')
hiddenimports += collect_submodules('services')
hiddenimports += collect_submodules('middleware')

# Binaries - platform-specific libraries
binaries = []

# Analysis
a = Analysis(
    ['main.py'],
    pathex=[backend_dir],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude test modules
        'pytest',
        'pytest_asyncio',
        'pytest_cov',
        '_pytest',
        
        # Exclude development tools
        'black',
        'flake8',
        'mypy',
        
        # Exclude unnecessary modules
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'IPython',
        'jupyter',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate entries
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Use UPX compression
    console=True,  # Show console window for logging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path if available
)

# Collect all files
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='backend',
)
