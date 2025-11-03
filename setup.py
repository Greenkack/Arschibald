"""
Setup Script für Bokuk2 Solar Calculator Application
=====================================================
Erstellt ein komplettes Installations-Paket mit allen Dependencies
"""

from setuptools import setup, find_packages
import os
import shutil
from pathlib import Path

# Version der Anwendung
VERSION = "2.0.0"
DESCRIPTION = "Bokuk2 Solar Calculator - Professionelle PV-Anlagen Kalkulation"

# Alle erforderlichen Python-Pakete
REQUIRED_PACKAGES = [
    "streamlit==1.49.1",
    "pandas==2.3.2",
    "numpy==2.3.2",
    "plotly==6.3.0",
    "reportlab==4.4.3",
    "pypdf==6.0.0",
    "PyPDF2==3.0.1",
    "pillow==11.3.0",
    "python-dotenv==1.1.1",
    "SQLAlchemy==2.0.43",
    "pydantic==2.11.9",
    "PyYAML==6.0.2",
    "requests==2.32.5",
    "openpyxl==3.1.5",
    "altair==5.5.0",
    "pdfplumber==0.11.7",
    "matplotlib==3.10.6",
    "scipy==1.16.1",
    "scikit-learn==1.7.1",
    "pvlib==0.13.0",
    "numpy-financial==1.0.0",
    
    # Streamlit Extensions
    "streamlit-extras==0.7.8",
    "streamlit-shadcn-ui==0.1.18",
    "streamlit-camera-input-live==0.2.0",
    "streamlit-card==1.0.2",
    "streamlit-sortables==0.3.1",
    "streamlit-toggle-switch==1.0.2",
    "st-annotated-text==4.0.2",
    
    # Database & API
    "fastapi==0.116.1",
    "uvicorn==0.35.0",
    "APScheduler==3.11.0",
    
    # Utilities
    "python-dateutil==2.9.0.post0",
    "pytz==2025.2",
    "cryptography==45.0.7",
    "beautifulsoup4==4.13.5",
    "Faker==37.8.0",
    "rich==14.1.0",
    "tqdm==4.67.1",
]

# Dateien und Verzeichnisse, die kopiert werden müssen
DATA_FILES = [
    # Datenbank
    ("database", ["database.py", "database_bridge.py", "database_clean.py"]),
    
    # PDF Templates
    ("pdf_templates_static", []),  # Gesamtes Verzeichnis
    ("coords", []),  # Gesamtes Verzeichnis
    ("coords_multi", []),  # Gesamtes Verzeichnis
    ("coords_wp", []),  # Gesamtes Verzeichnis
    
    # Konfiguration
    (".", [".env.example", "requirements.txt"]),
    
    # Statische Assets
    ("assets", []),  # Gesamtes Verzeichnis
    ("static", []),  # Gesamtes Verzeichnis
    
    # JSON Konfigurationen
    ("json", []),  # Gesamtes Verzeichnis
    
    # Streamlit Config
    (".streamlit", ["config.toml"]),
]

# Python Module die inkludiert werden müssen
PYTHON_MODULES = [
    "analysis.py",
    "calculations.py",
    "calculations_extended.py",
    "calculations_heatpump.py",
    "solar_calculator.py",
    "admin_panel.py",
    "data_input.py",
    "crm.py",
    "gui.py",
    "init_database.py",
    "user_management.py",
    "user_menu.py",
    "intro_screen.py",
    "pricing",
    "pdf_template_engine",
    "components",
    "core",
    "utils",
]

def read_requirements():
    """Liest requirements.txt und gibt Liste zurück"""
    req_file = Path(__file__).parent / "requirements.txt"
    if req_file.exists():
        with open(req_file, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return REQUIRED_PACKAGES

setup(
    name="bokuk2-solar-calculator",
    version=VERSION,
    description=DESCRIPTION,
    long_description=open("README.md", "r", encoding="utf-8").read() if os.path.exists("README.md") else DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Bokuk2 Development Team",
    author_email="support@bokuk2.com",
    url="https://github.com/Greenkack/Arschibald",
    
    # Python Version
    python_requires=">=3.10",
    
    # Pakete
    packages=find_packages(
        exclude=["tests*", "Agent*", "archive*", "backups*", "docs*", ".venv*"]
    ),
    
    # Dependencies
    install_requires=read_requirements(),
    
    # Zusätzliche Dateien
    include_package_data=True,
    package_data={
        "": [
            "*.yaml",
            "*.yml",
            "*.json",
            "*.pdf",
            "*.png",
            "*.jpg",
            "*.jpeg",
            "*.ico",
            "*.db",
            "*.csv",
            "*.toml",
        ],
    },
    
    # Entry Points
    entry_points={
        "console_scripts": [
            "bokuk2=gui:main",
            "bokuk2-admin=admin_panel:main",
            "bokuk2-init=init_database:main",
        ],
    },
    
    # Klassifizierungen
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: Microsoft :: Windows",
        "Environment :: Web Environment",
        "Framework :: Streamlit",
    ],
    
    # Lizenz
    license="MIT",
    
    # Keywords
    keywords="solar calculator pv photovoltaik angebot kalkulation",
    
    # Projekt URLs
    project_urls={
        "Bug Reports": "https://github.com/Greenkack/Arschibald/issues",
        "Source": "https://github.com/Greenkack/Arschibald",
    },
)
