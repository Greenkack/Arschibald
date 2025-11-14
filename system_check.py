#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Umfassende System-Prüfung für die gesamte App
Prüft alle Abhängigkeiten, Imports und Konfigurationen
"""

import sys
import importlib
from pathlib import Path
from typing import List, Tuple

def check_package(package_name: str, import_name: str = None) -> Tuple[bool, str]:
    """Prüft ob ein Paket installiert und importierbar ist"""
    if import_name is None:
        import_name = package_name
    
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'unknown')
        return True, version
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error: {e}"

def main():
    print("=" * 80)
    print("[SEARCH] UMFASSENDE SYSTEM-PRÜFUNG - BOKUK2 APP")
    print("=" * 80)
    print()
    
    # Kategorien von Paketen
    categories = {
        "[DESIGN] STREAMLIT & WEB": [
            ("streamlit", "streamlit"),
            ("plotly", "plotly"),
            ("altair", "altair"),
            ("pydeck", "pydeck"),
            ("streamlit-extras", "streamlit_extras"),
            ("streamlit-shadcn-ui", "streamlit_shadcn_ui"),
            ("st-annotated-text", "st_annotated_text"),
        ],
        
        "[CHART] DATENVERARBEITUNG": [
            ("pandas", "pandas"),
            ("numpy", "numpy"),
            ("openpyxl", "openpyxl"),
            ("xlrd", "xlrd"),
            ("scipy", "scipy"),
            ("scikit-learn", "sklearn"),
        ],
        
        "[FILE] PDF & DOKUMENTE": [
            ("reportlab", "reportlab"),
            ("PyPDF2", "PyPDF2"),
            ("pdfplumber", "pdfplumber"),
            ("pdf2image", "pdf2image"),
            ("pikepdf", "pikepdf"),
        ],
        
        "🔐 AUTHENTIFIZIERUNG & SECURITY": [
            ("PyJWT", "jwt"),
            ("cryptography", "cryptography"),
            ("python-dotenv", "dotenv"),
        ],
        
        "🗄️ DATENBANK": [
            ("SQLAlchemy", "sqlalchemy"),
            ("redis", "redis"),
            ("duckdb", "duckdb"),
        ],
        
        "🌐 HTTP & API": [
            ("requests", "requests"),
            ("fastapi", "fastapi"),
            ("uvicorn", "uvicorn"),
            ("websockets", "websockets"),
        ],
        
        "🤖 AI & MACHINE LEARNING": [
            ("langchain", "langchain"),
            ("langchain-openai", "langchain_openai"),
            ("langchain-community", "langchain_community"),
            ("faiss-cpu", "faiss"),
            ("elevenlabs", "elevenlabs"),
        ],
        
        "[DESIGN] PV & 3D VISUALISIERUNG": [
            ("pyvista", "pyvista"),
            ("vtk", "vtk"),
            ("stpyvista", "stpyvista"),
            ("trimesh", "trimesh"),
            ("pvlib", "pvlib"),
        ],
        
        "🧪 TESTING": [
            ("pytest", "pytest"),
            ("pytest-asyncio", "pytest_asyncio"),
            ("hypothesis", "hypothesis"),
            ("Faker", "faker"),
        ],
        
        "🛠️ ENTWICKLUNGSTOOLS": [
            ("black", "black"),
            ("ruff", "ruff"),
            ("mypy", "mypy"),
            ("pre-commit", "pre_commit"),
        ],
    }
    
    total_packages = 0
    installed_packages = 0
    missing_packages = []
    
    for category, packages in categories.items():
        print(f"\n{category}")
        print("-" * 80)
        
        for package_name, import_name in packages:
            total_packages += 1
            success, info = check_package(package_name, import_name)
            
            if success:
                installed_packages += 1
                print(f"  [OK] {package_name:30s} v{info}")
            else:
                print(f"  [ERROR] {package_name:30s} FEHLT!")
                missing_packages.append((package_name, info))
    
    # Python Standard Library (kritisch)
    print(f"\n🐍 PYTHON STANDARD LIBRARY")
    print("-" * 80)
    std_libs = ["json", "io", "pathlib", "typing", "datetime", "os", "sys", "re"]
    for lib in std_libs:
        success, info = check_package(lib, lib)
        if success:
            print(f"  [OK] {lib:30s} Standard")
        else:
            print(f"  [ERROR] {lib:30s} FEHLT!")
    
    # Lokale Module prüfen
    print(f"\n[PACKAGE] LOKALE MODULE")
    print("-" * 80)
    local_modules = [
        "heatpump_products_database",
        "calculations",
        "admin_panel",
        "heatpump_ui",
        "analysis_utils",
    ]
    
    for module in local_modules:
        success, info = check_package(module, module)
        if success:
            print(f"  [OK] {module:30s} OK")
        else:
            print(f"  [WARNING]  {module:30s} {info[:40]}")
    
    # Konfigurationsdateien prüfen
    print(f"\n⚙️  KONFIGURATIONSDATEIEN")
    print("-" * 80)
    
    config_files = [
        "config/heating_costs_config.json",
        "config/heatpump_prices_config.json",
        "heatpump_products_database.py",
        "requirements.txt",
        ".env",
    ]
    
    for config_file in config_files:
        file_path = Path(config_file)
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  [OK] {config_file:40s} ({size:,} bytes)")
        else:
            print(f"  [WARNING]  {config_file:40s} NICHT GEFUNDEN")
    
    # Zusammenfassung
    print("\n" + "=" * 80)
    print("[CHART] ZUSAMMENFASSUNG")
    print("=" * 80)
    print(f"[OK] Installiert:  {installed_packages}/{total_packages} Pakete ({installed_packages/total_packages*100:.1f}%)")
    print(f"[ERROR] Fehlend:      {len(missing_packages)} Pakete")
    
    if missing_packages:
        print("\n[WARNING]  FEHLENDE PAKETE:")
        for pkg, error in missing_packages:
            print(f"   • {pkg}")
        
        print("\n[IDEA] Installation mit:")
        print(f"   pip install {' '.join([pkg for pkg, _ in missing_packages])}")
    else:
        print("\n🎉 ALLE PAKETE SIND INSTALLIERT!")
    
    print("\n" + "=" * 80)
    print(f"🐍 Python Version: {sys.version}")
    print(f"📍 Python Path: {sys.executable}")
    print("=" * 80)

if __name__ == "__main__":
    main()
