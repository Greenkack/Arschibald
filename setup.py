"""
Setup Script für Ömer's All in One DingsBums
=============================================
Komplettes Installations-Paket für die ultimative Solar-Kalkulations-Suite
"""

from setuptools import setup, find_packages
import os
import shutil
from pathlib import Path

# Version der Anwendung
VERSION = "2.5.0"
DESCRIPTION = "Ömer's All in One DingsBums"

# Alle erforderlichen Python-Pakete (aus requirements.txt)
REQUIRED_PACKAGES = [
    # Core Framework
    "streamlit==1.49.1",
    "pandas==2.3.2",
    "numpy==2.3.2",
    "plotly==6.3.0",
    
    # PDF Generation & Processing
    "reportlab==4.4.3",
    "pypdf==6.0.0",
    "PyPDF2==3.0.1",
    "PyPDF3==1.0.6",
    "PyPDF4==1.27.0",
    "pdfplumber==0.11.7",
    "PyMuPDF==1.26.4",
    "pdf2image==1.17.0",
    "pdfminer.six==20250506",
    "pypdfium2==4.30.0",
    "pikepdf>=9.0.0",
    
    # Image Processing
    "pillow==11.3.0",
    
    # Database & ORM
    "SQLAlchemy==2.0.43",
    "alembic==1.16.5",
    
    # Configuration & Environment
    "python-dotenv==1.1.1",
    "pydantic==2.11.9",
    "pydantic_core==2.33.2",
    "PyYAML==6.0.2",
    "PyYAML-ft==8.0.0",
    "toml==0.10.2",
    "tomlkit==0.13.3",
    
    # HTTP & API
    "requests==2.32.5",
    "fastapi==0.116.1",
    "uvicorn==0.35.0",
    "starlette==0.47.3",
    "python-multipart==0.0.20",
    "h11==0.16.0",
    
    # Excel Processing
    "openpyxl==3.1.5",
    "xlrd==2.0.2",
    "et_xmlfile==2.0.0",
    
    # Data Visualization
    "altair==5.5.0",
    "matplotlib==3.10.6",
    "kaleido==1.0.0",
    "pydeck==0.9.1",
    
    # Scientific Computing
    "scipy==1.16.1",
    "scikit-learn==1.7.1",
    "numpy-financial==1.0.0",
    "numexpr==2.11.0",
    
    # PV-specific
    "pvlib==0.13.0",
    
    # 3D Visualization
    "pyvista>=0.43.10",
    "vtk>=9.3.0",
    "stpyvista>=0.1.4",
    "trimesh>=4.4.9",
    
    # Streamlit Extensions
    "streamlit-extras==0.7.8",
    "streamlit-shadcn-ui==0.1.18",
    "streamlit-camera-input-live==0.2.0",
    "streamlit-card==1.0.2",
    "streamlit-sortables==0.3.1",
    "streamlit-toggle-switch==1.0.2",
    "streamlit-vertical-slider==2.5.5",
    "streamlit-image-coordinates==0.4.0",
    "streamlit-keyup==0.3.0",
    "streamlit-notify==0.3.1",
    "streamlit-embedcode==0.1.2",
    "streamlit-avatar==0.1.3",
    "streamlit_faker==0.0.4",
    "st-annotated-text==4.0.2",
    "st-theme==1.2.3",
    
    # Scheduling & Background Jobs
    "APScheduler==3.11.0",
    
    # Utilities
    "python-dateutil==2.9.0.post0",
    "pytz==2025.2",
    "tzdata==2025.2",
    "tzlocal==5.3.1",
    "cryptography==45.0.7",
    "beautifulsoup4==4.13.5",
    "Faker==37.8.0",
    "rich==14.1.0",
    "tqdm==4.67.1",
    "click==8.2.1",
    "typer==0.19.2",
    
    # Web Scraping & HTML Processing
    "lxml==6.0.1",
    "soupsieve==2.8",
    
    # Markdown & Documentation
    "Markdown==3.9",
    "markdown-it-py==4.0.0",
    "markdownlit==0.0.7",
    "mdurl==0.1.2",
    "Pygments==2.19.2",
    "pymdown-extensions==10.16.1",
    
    # AI & Agent Framework (KAI)
    "langchain==0.3.27",
    "langchain-openai==0.3.0",
    "langchain-community==0.3.21",
    "tavily-python==0.5.0",
    "faiss-cpu==1.10.0",
    
    # Cloud & Storage
    "boto3==1.40.32",
    "botocore==1.40.32",
    "s3transfer==0.14.0",
    
    # Communication
    "twilio==9.4.0",
    "elevenlabs==2.20.1",
    "websockets==14.1",
    
    # Monitoring & Logging
    "prometheus_client==0.22.1",
    "structlog==25.4.0",
    "logistro==1.1.0",
    "watchdog==6.0.0",
    
    # Caching & Performance
    "cachetools==6.2.0",
    "redis==6.4.0",
    
    # Security & Authentication
    "PyJWT==2.10.1",
    "pyOpenSSL==25.2.0",
    "asn1crypto==1.5.1",
    "cffi==1.17.1",
    "pycparser==2.22",
    
    # Data Processing & Serialization
    "pyarrow==21.0.0",
    "orjson==3.11.3",
    "simplejson==3.20.1",
    "protobuf==6.31.1",
    "jsonschema==4.25.1",
    "jsonschema-specifications==2025.4.1",
    
    # Git Integration
    "GitPython==3.1.45",
    "gitdb==4.0.12",
    "smmap==5.0.2",
    
    # Code Quality & Formatting
    "black==25.9.0",
    "ruff==0.13.2",
    "mypy==1.18.2",
    "mypy_extensions==1.1.0",
    
    # Testing
    "pytest==8.4.2",
    "pytest-asyncio==1.2.0",
    "pytest-cov>=7.0.0",
    "pytest-sugar>=1.1.1",
    "hypothesis==6.140.2",
    
    # Build & Packaging
    "build==1.2.2.post1",
    "setuptools==80.9.0",
    "wheel==0.45.1",
    "pyproject_hooks==1.2.0",
    "packaging==25.0",
    
    # UI Components
    "htbuilder==0.9.0",
    "favicon==0.7.0",
    
    # Database Specific
    "duckdb==1.4.0",
    "snowflake-connector-python==3.17.3",
    "snowflake-snowpark-python==1.38.0",
    "greenlet==3.2.4",
    
    # Parser & Templating
    "Jinja2==3.1.6",
    "MarkupSafe==3.0.2",
    "Mako==1.3.10",
    "pyparsing==3.2.3",
    "libcst==1.8.4",
    
    # Miscellaneous
    "altex==0.2.0",
    "choreographer==1.0.10",
    "narwhals==2.3.0",
    "tenacity==9.1.2",
    "validators==0.35.0",
    "sortedcontainers==2.4.0",
    "threadpoolctl==3.6.0",
    "shellingham==1.5.4",
    "shellescape==3.8.1",
    "entrypoints==0.4",
    "attrs==25.3.0",
    "blinker==1.9.0",
    "colorama==0.4.6",
    "charset-normalizer==3.4.3",
    "certifi==2025.8.3",
    "urllib3==2.5.0",
    "idna==3.10",
    "sniffio==1.3.1",
    "anyio==4.10.0",
    "referencing==0.36.2",
    "rpds-py==0.27.1",
    "typing_extensions==4.15.0",
    "typing-inspection==0.4.1",
    "six==1.17.0",
    "joblib==1.5.2",
    "cloudpickle==3.1.1",
    "cycler==0.12.1",
    "contourpy==1.3.3",
    "fonttools==4.59.2",
    "kiwisolver==1.4.9",
    "jmespath==1.0.1",
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

# Python Module die inkludiert werden müssen (ALLE .py Dateien im Hauptverzeichnis)
PYTHON_MODULES = [
    # Core Application Files
    "gui.py",
    "solar_calculator.py",
    "data_input.py",
    "crm.py",
    "admin_panel.py",
    "intro_screen.py",
    "user_management.py",
    "user_menu.py",
    "init_database.py",
    
    # Database Layer
    "database.py",
    "database_bridge.py",
    "database_clean.py",
    "database_backup.py",
    
    # Calculations Engine
    "calculations.py",
    "calculations_extended.py",
    "calculations_heatpump.py",
    "calculations_cli.py",
    "calculation_bridge.py",
    
    # Analysis & Reporting
    "analysis.py",
    "analysis_utils.py",
    
    # PDF Generation System
    "central_pdf_system.py",
    "pdf_generator.py",
    "pdf_chart_styles.py",
    "pdf_preview.py",
    "pdf_ui.py",
    "pdf_visual_inject.py",
    
    # 3D Visualization
    "pv3d.py",
    "pv3d_plotly.py",
    
    # Admin UI Components
    "admin_brand_logo_management_ui.py",
    "admin_build_infos_ui.py",
    "admin_core_status_ui.py",
    "admin_core_status_extended_ui.py",
    "admin_heating_costs_config_ui.py",
    "admin_heatpump_settings_ui.py",
    "admin_intro_settings_ui.py",
    "admin_logo_management_ui.py",
    "admin_logo_positions_ui.py",
    "admin_module_alias_mapping_ui.py",
    "admin_payment_terms_ui.py",
    "admin_pdf_settings_ui.py",
    "admin_pricing_rule_ui.py",
    "admin_product_attributes_ui.py",
    "admin_product_database_ui.py",
    "admin_profit_margin_ui.py",
    "admin_pv_mounting_ui.py",
    "admin_pv_mounting_tab.py",
    "admin_services_ui.py",
    "admin_security.py",
    "admin_ui_effects_settings.py",
    "admin_user_management_ui.py",
    
    # CRM Components
    "crm_dashboard_ui.py",
    "crm_calendar_ui.py",
    "crm_pipeline_ui.py",
    
    # Chart & Visualization
    "chart_styling.py",
    "chart_styling_improvements.py",
    "auto_chart_generator.py",
    "advanced_charts.py",
    
    # UI Components & Utilities
    "carousel_ui_utils.py",
    "carousel_ui_utils_native.py",
    "carousel_preview.py",
    "drawer_actions.py",
    "dynamic_overlay.py",
    "excel_grid_ui.py",
    
    # Product & Pricing
    "product_db.py",
    "brand_logo_db.py",
    "heatpump_products_database.py",
    "dynamic_pricing_engine.py",
    
    # Configuration & Theming
    "theme_manager.py",
    "css_template_manager.py",
    "german_formatting.py",
    
    # Advanced Features
    "advanced_features.py",
    "ai_companion.py",
    "agent_ui.py",
    
    # Integration & Export
    "core_integration.py",
    "doc_output.py",
    
    # Utilities
    "utils.py",
    "app_status.py",
    "placeholders.py",
    "waermepumpen_parser.py",
    
    # Sub-packages (werden automatisch durch find_packages() erfasst)
    "pricing",          # Pricing Engine Package
    "pdf_template_engine",  # PDF Template System
    "components",       # UI Components Package
    "core",            # Core System Package
    "utils",           # Utilities Package
    "excel",           # Excel Integration Package
    "widgets",         # Widget Library
    "cli",             # Command Line Interface
    "multi_pdf_positioning",  # Multi-PDF Positioning System
]

def read_requirements():
    """Liest requirements.txt und gibt Liste zurück"""
    req_file = Path(__file__).parent / "requirements.txt"
    if req_file.exists():
        with open(req_file, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return REQUIRED_PACKAGES

setup(
    name="oemers-all-in-one-dingsbums",
    version=VERSION,
    description=DESCRIPTION,
    long_description=open("README.md", "r", encoding="utf-8").read() if os.path.exists("README.md") else DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Ömer's Development Team",
    author_email="support@oemers-dingsbums.com",
    url="https://github.com/Greenkack/Arschibald",
    
    # Python Version
    python_requires=">=3.10",
    
    # Pakete - findet ALLE Pakete automatisch
    packages=find_packages(
        exclude=[
            "tests*", 
            "Agent*", 
            "archive*", 
            "backups*", 
            "docs*", 
            ".venv*",
            "nützliche tools*",
            "tools*",
            "*__pycache__*",
            "*.pyc",
            "*.pyo",
        ]
    ),
    
    # Alle Python-Module im Root-Verzeichnis
    py_modules=[
        os.path.splitext(f)[0] for f in PYTHON_MODULES 
        if f.endswith('.py')
    ],
    
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
            "*.svg",
            "*.db",
            "*.sqlite",
            "*.sqlite3",
            "*.csv",
            "*.txt",
            "*.toml",
            "*.ini",
            "*.conf",
            "*.md",
            "*.html",
            "*.css",
            "*.js",
            "*.xml",
        ],
        "pdf_templates_static": ["*"],
        "coords": ["*"],
        "coords_multi": ["*"],
        "coords_wp": ["*"],
        "assets": ["*"],
        "static": ["*"],
        "json": ["*"],
        "mirror": ["*"],
        ".streamlit": ["*.toml"],
    },
    
    # Entry Points - Kommandozeilen-Befehle
    entry_points={
        "console_scripts": [
            "oemers-dingsbums=gui:main",
            "oemers-admin=admin_panel:main",
            "oemers-init=init_database:main",
            "oemers-calc=calculations_cli:main",
        ],
    },
    
    # Klassifizierungen
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Visualization",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Environment :: Web Environment",
        "Framework :: Streamlit",
        "Natural Language :: German",
    ],
    
    # Lizenz
    license="MIT",
    
    # Keywords
    keywords=[
        "solar", "calculator", "pv", "photovoltaik", 
        "angebot", "kalkulation", "wärmepumpe", "heatpump",
        "crm", "pdf", "visualization", "3d", "energy",
        "ömer", "all-in-one", "dingsbums", "wp", "energie",
        "strom", "verbrauch", "kosten", "heizung", "heizkosten",
        "stromkosten", "stromverbrauch", "energieberatung", "solarrechner",
        "wärmepumpenrechner", "heizkostenrechner", "energie kosten",
        "software", "app", "application", "business", "management",
        "tool", "tools", "utility", "utilities", "data", "analysis",
        "heizlast", "fbh", "heizlastberechnung", "heizlast berechnung",
        "floor heating", "floorheating", "fußbodenheizung", "fußbodenheizungsberechnung",
        "heating cost calculation", "heatingcostcalculation", "heizkostenberechnung",
        "data science", "data processing", "data visualization",
        "reporting", "report generator", "angebotserstellung", "angebot generator",
        "pdf generator", "pdf reporting", "pdf berichtserstellung",
        "admin panel", "user management", "kundendatenbank", "kundenverwaltung",
        "projektmanagement", "project management", "calendar", "terminplanung",
        "task management", "aufgabenverwaltung", "crm system", "crm software",
        "business management", "geschäftsverwaltung", "energy efficiency",
        "energieeffizienz", "sustainability", "nachhaltigkeit",
        "renewable energy", "erneuerbare energie", "green energy", "grüne energie",
        "environment", "umwelt", "climate change", "klimawandel",
        "carbon footprint", "co2 fußabdruck", "emissions", "emissionen",
        "energy monitoring", "energiemonitoring", "consumption tracking", "verbrauchsverfolgung",
        "kostenanalyse", "cost analysis", "financial planning", "finanzplanung",
        "budgeting", "budgetierung", "forecasting", "prognose",
        "investment analysis", "investitionsanalyse", "risk management", "risikomanagement",
        "compliance", "compliance management", "data security", "datensicherheit",
        "privacy", "datenschutz", "user interface", "benutzeroberfläche",
        "user experience", "benutzererfahrung", "ux", "ui",
        "streamlit", "fastapi", "python", "software development", "softwareentwicklung",
        "open source", "opensource", "github", "gitlab",
        "collaboration", "zusammenarbeit", "teamwork", "agile", "scrum",
        "kanban", "projektplanung", "projektmanagement software",
        "task tracking", "aufgabenverfolgung", "time management", "zeitmanagement",
        "productivity", "produktivität", "efficiency", "effizienz",
        "automation", "automatisierung", "workflow", "arbeitsablauf",
        "integration", "integration services", "api", "web services",
        ],
    
    # Projekt URLs
    project_urls={
        "Bug Reports": "https://github.com/Greenkack/Arschibald/issues",
        "Source": "https://github.com/Greenkack/Arschibald",
        "Documentation": "https://github.com/Greenkack/Arschibald/wiki",
    },
    
    # Zusätzliche Metadaten
    zip_safe=False,  # Paket nicht als ZIP verpacken für bessere Kompatibilität
)
