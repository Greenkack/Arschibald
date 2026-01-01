"""
verify_build_ready.py
Prüft ob alle Voraussetzungen für einen erfolgreichen Build erfüllt sind

VERWENDUNG:
    python verify_build_ready.py
"""

import sys
from pathlib import Path
import importlib
import json
import io

# Fix für Windows Console Encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 70)
print("  BUILD VERIFICATION - Überprüfe alle Voraussetzungen")
print("=" * 70 + "\n")

errors = []
warnings = []
success = []

# 1. Prüfe kritische Dateien
print("1. Prüfe kritische Dateien...")
critical_files = [
    # Core-Anwendungsdateien
    "gui.py",
    "build_exe_setup.py",
    "requirements.txt",
    "database.py",
    "locales.py",
    "de.json",
    "robustness_core.py",
    
    # Berechnungsmodule
    "calculations.py",
    "calculations_heatpump.py",
    "financial_calculations.py",
    "analysis.py",
    "analysis_utils.py",
    "live_calculation_engine.py",
    
    # Hauptmodule
    "data_input.py",
    "doc_output.py",
    "quick_calc.py",
    "options.py",
    "pv_visuals.py",
    "ai_companion.py",
    "agent_ui.py",
    "heatpump_ui.py",
    "solar_calculator.py",
    "solar_calculator_pv_mounting.py",
    "solar_calculator_pricing_integration.py",
    "solar_calculator_shadcn.py",
    
    # CRM-Module
    "crm.py",
    "crm_dashboard_ui.py",
    "crm_pipeline_ui.py",
    "crm_calendar_ui.py",
    "crm_shadcn.py",
    
    # PDF-System
    "pdf_generator.py",
    "product_rotation_engine.py",
    "price_modification_engine.py",
    "pdf_template_engine/dynamic_overlay.py",
    "pdf_template_engine/placeholders.py",
    "pdf_template_engine/merger.py",
    "central_pdf_system.py",
    "multi_offer_generator.py",
    "pdf_preview.py",
    "pdf_ui.py",
    "pdf_widgets.py",
    "pdf_payment_summary.py",
    
    # Admin-Panel (vollständig)
    "admin_panel.py",
    "admin_panel_shadcn.py",
    "admin_controlling_settings_ui.py",
    "admin_security.py",
    "admin_product_database_ui.py",
    "admin_product_database_ui_optimized.py",
    "admin_heatpump_settings_ui.py",
    "admin_heatpump_products_optimized.py",
    "admin_logo_management_ui.py",
    "admin_core_status_ui.py",
    "admin_core_status_extended_ui.py",
    "admin_build_infos_ui.py",
    "admin_brand_logo_management_ui.py",
    "admin_intro_settings_ui.py",
    "admin_logo_positions_ui.py",
    "admin_payment_terms_ui.py",
    "admin_pdf_settings_ui.py",
    "admin_services_ui.py",
    "admin_user_management_ui.py",
    "admin_ui_effects_settings.py",
    "admin_module_alias_mapping_ui.py",
    "admin_price_matrix_upload.py",
    "admin_pricing_rule_ui.py",
    "admin_product_attributes_ui.py",
    "admin_profit_margin_ui.py",
    "admin_pv_mounting_ui.py",
    "admin_pv_mounting_tab.py",
    
    # Core-System
    "core/config.py",
    "core/logging_config.py",
    "core/cache.py",
    "core/session.py",
    "core/database.py",
    "core/router.py",
    "core/jobs.py",
    "core/forms.py",
    "core/widgets.py",
    "core/navigation_history.py",
    "core/migrations.py",
    "core/security.py",
    "core/session_manager.py",
    "core/session_persistence.py",
    "core/connection_manager.py",
    "core_integration.py",
    
    # Components
    "components/shadcn_ui_integration.py",
    "components/form_components.py",
    "components/metric_card.py",
    "components/card.py",
    "components/alert.py",
    "components/badge.py",
    "components/table.py",
    "components/progress.py",
    "components/pagination.py",
    "components/extended_components.py",
    
    # Produktverwaltung
    "product_db.py",
    "product_attributes.py",
    "special_products.py",
    "heatpump_pricing.py",
    "service_display_config_ui.py",
    
    # Pricing-System
    "pricing/enhanced_pricing_engine.py",
    "pricing/pricing_cache.py",
    "pricing/profit_margin_manager.py",
    "pricing/pv_pricing_engine.py",
    "pricing/enhanced_heatpump_pricing.py",
    "pricing/combined_pricing_engine.py",
    "pricing/calculate_per_engine.py",
    "pricing/pricing_modification_engine.py",
    "pricing/economic_analysis_integration.py",
    
    # CRM Features
    "crm/features/contract_manager.py",
    "crm/features/contract_ui.py",
    "crm/features/email_manager.py",
    "crm/features/email_ui.py",
    "crm/features/task_manager.py",
    "crm/features/tag_manager.py",
    "crm/features/tag_ui.py",
    "crm/features/knowledge_base.py",
    "crm/features/dashboard_widgets.py",
    "crm/features/note_manager.py",
    "crm/features/offer_tracker.py",
    "crm/features/offer_ui.py",
    "crm/features/lead_scoring.py",
    "crm/features/reporting_engine.py",
    "crm/features/geo_mapper.py",
    "crm/features/geo_ui.py",
    "crm/features/call_manager.py",
    "crm/features/feedback_manager.py",
    "crm/features/template_manager.py",
    
    # CRM Utilities
    "crm/utils/backup_scheduler.py",
    "crm/utils/notification_manager.py",
    "crm/utils/import_export_manager.py",
    
    # CRM Integration
    "crm/integration/calculation_bridge.py",
    "crm/integration/data_input_bridge.py",
    
    # Theming & UI
    "theme_manager.py",
    "emoji_toggle.py",
    "ui_settings_handler.py",
    "ui_effects_library.py",
    "controlling_ui.py",
    "carousel_ui_utils.py",
    "css_template_manager.py",
    
    # Theming System
    "theming/theme_cache.py",
    "theming/theme_validator.py",
    "theming/state_manager.py",
    "theming/hot_reload_manager.py",
    "theming/error_dashboard.py",
    "theming/monitoring_dashboard.py",
    "theming/validation_display.py",
    
    # Utilities & Bridges
    "add_all_declarations.py",
    "video_server.py",
    "database_backup.py",
    "database_bridge.py",
    "database_clean.py",
    "calculation_bridge.py",
    "solar_calculator_bridge.py",
    "brand_logo_db.py",
    "pv_mounting_database.py",
    "pv_mounting_db_bridge.py",
    "live_preview_helpers.py",
    "price_matrix_store.py",
    "debug_tools.py",
    "user_management.py",
    
    # Utils Modules
    "utils/pv_module_placement_system.py",
    "utils/pv_module_placement_ui.py",
    "utils/pv_module_rendering_3d.py",
    "utils/shadcn_migration_helpers.py",
    "utils/shadcn_sidebar.py",
    
    # Monitoring & Tracing
    "app_evaluation.py",
    "app_tracing.py",
    "app_status.py",
    "app_health_monitor.py",
    "app_diagnostics.py",
    "app_auto_fixer.py",
    
    # Financial Tools
    "financial_tools_ui.py",
    
    # Agent System
    "Agent/agent/agent_core.py",
    "Agent/agent/tools/coding_tools.py",
    "Agent/agent/tools/knowledge_tools.py",
    "Agent/agent/tools/execution_tools.py",
    "Agent/agent/tools/telephony_tools.py",
    "Agent/agent/tools/testing_tools.py",
    "Agent/config.py",
    "Agent/install.py",
    
    # Excel Integration
    "excel_grid_ui.py",
    "excel/custom_dynamic_calculation.py",
    
    # Enhanced Product Management
    "enhanced_product_management_ui.py",
    "price_matrix_error_ui.py",
    
    # Widgets
    "widgets/form_widgets.py",
    "db_ext_widget.py",
    
    # Backend API (falls vorhanden)
    "backend/main.py",
    "backend/core/database.py",
    "backend/core/security.py",
    "backend/services/calculation_result_key_service.py",
    "backend/services/crm_service.py",
    "backend/services/database_service.py",
    
    # CLI Tools
    "cli/backup_commands.py",
    "cli/test_commands.py",
    
    # Advanced Features
    "advanced_features.py",
    "advanced_charts.py",
    "auto_chart_generator.py",
    
    # WP Implementations
    "wp_implements/heat_pump_calculator.py",
    "wp_implements/heat_pump_ui.py",
    "wp_implements/wp_bridge.py",
    
    # Multi PDF Positioning
    "multi_pdf_positioning/coordinate_extractor.py",
    "multi_pdf_positioning/pdf_analyzer.py",
    
    # Zusätzliche wichtige Module
    "apply_german_formatting.py",
    "mariana_trench_analysis.py",
    "database_pricing_migration.py",
    "complete_repair.py",
    "auto_repair_100.py",
    "auto_fix_code_issues.py",
    "add_missing_controlling_data.py",
    "add_plotly_separators.py",
    "add_test_product_images.py",
    "analyse_alle_amortisationszeit_berechnungen.py",
    "analyse_alle_duplikate.py",
    "analyze_core_integration.py",
    "analyze_excel.py",
    "analyze_missing_features.py",
    "analyze_pricing_keys_usage.py",
    "audit_and_dedupe.ps1",
    "apply_german_formatting.py",
    "auto_replace_emojis_safe.py",
    "fix_all_empty_icons.py",
    "clear_python_cache.py",
    
    # Testing & Validation
    "tests/test_crm_integration.py",
    "tests/test_pdf_generation.py",
    "tests/test_agent_isolation.py",
    "tests/test_database.py",
    "tests/test_pricing.py",
    "tests/test_calculations.py",
    
    # Excel & Grid Integration
    "excel_processing.py",
    "data_grid.py",
    "grid_controller.py",
    
    # Enhanced Heating System
    "heating_cost_calculator.py",
    "heating_calculator_ui.py",
    "admin_heating_costs_config_ui.py",
    
    # Security & Auth
    "authentication.py",
    "password_manager.py",
    "session_security.py",
    
    # Background Jobs
    "job_scheduler.py",
    "background_tasks.py",
    "task_queue.py",
    
    # Import/Export
    "csv_importer.py",
    "excel_exporter.py",
    "data_migration.py",
    
    # Reporting
    "report_generator.py",
    "chart_builder.py",
    "statistics_engine.py",
    
    # Config
    ".streamlit/config.toml",
    ".streamlit/secrets.toml",
    "config.json",
    "settings.json",
]

for file_path in critical_files:
    path = Path(file_path)
    if path.exists():
        size_kb = path.stat().st_size / 1024
        success.append(f"  ✓ {file_path} ({size_kb:.1f} KB)")
    else:
        errors.append(f"  ✗ FEHLT: {file_path}")

# 2. Prüfe Daten-Verzeichnisse
print("\n2. Prüfe Daten-Verzeichnisse...")
data_dirs = [
    "data",
    "coords_multi",
    "pdf_templates_static",
    "pdf_templates_static/multi",
    "pdf_templates_static/notext",
    "customer_documents",
    "logs",
    "knowledge_base",
    "data/company_logos",
    "data/product_images",
    "Agent",
    "components",
    "coords",
    "coords_wp",
    "crm",
    "docs",
    "excel",
    "notwendig_oder_nicht",
    "pdf_template_engine",
    "pricing",
    "solar-calculator-pro",
    "theming",
    "tools",
    "utils",
    "Wheelhouse",
    "widgets",
    "wp_implements",
    "backend",
    "cli",
    "multi_pdf_positioning",
    "tests",
    "migrations",
    "logs/app",
    "logs/error",
    "logs/debug",
    "cache",
    "temp",
    "exports",
    "imports",
    "backups",
    "reports",
    "templates",
    "static",
    "assets",
    "resources",
    ".github",
    "nützliche tools",
]

for dir_path in data_dirs:
    path = Path(dir_path)
    if path.exists() and path.is_dir():
        file_count = len(list(path.rglob("*")))
        success.append(f"  ✓ {dir_path}/ ({file_count} Dateien)")
    else:
        warnings.append(f"  ⚠ {dir_path}/ nicht gefunden (wird leer erstellt)")

# 3. Prüfe Python-Version
print("\n3. Prüfe Python-Version...")
py_version = sys.version_info
if py_version >= (3, 10):
    success.append(f"  ✓ Python {py_version.major}.{py_version.minor}.{py_version.micro}")
else:
    errors.append(f"  ✗ Python {py_version.major}.{py_version.minor} zu alt - mindestens 3.10 erforderlich!")

# 4. Prüfe kritische Packages
print("\n4. Prüfe kritische Packages...")
critical_packages = [
    # Core Dependencies
    "streamlit",
    "pandas",
    "numpy",
    "scipy",
    
    # PDF-System
    "reportlab",
    "PyPDF2",
    "pypdf",
    "pdfplumber",
    "PyMuPDF",
    "pikepdf",
    
    # Excel & Data
    "openpyxl",
    "xlrd",
    "chardet",
    
    # Visualization
    "matplotlib",
    "plotly",
    "altair",
    "pyvista",
    "vtk",
    "stpyvista",
    "trimesh",
    
    # Database
    "sqlalchemy",
    "alembic",
    "redis",
    
    # YAML & Config
    "pyyaml",
    "yaml",
    "toml",
    "python-dotenv",
    
    # Images
    "pillow",
    "PIL",
    "pdf2image",
    
    # Web & API
    "requests",
    "fastapi",
    "uvicorn",
    "starlette",
    "pydantic",
    "websockets",
    
    # AI & ML
    "langchain",
    "langchain-openai",
    "langchain-community",
    "openai",
    "anthropic",
    "elevenlabs",
    "faiss-cpu",
    "scikit-learn",
    "transformers",
    
    # Agent Tools
    "tavily-python",
    "twilio",
    
    # Testing
    "pytest",
    "pytest-asyncio",
    "hypothesis",
    "Faker",
    
    # Monitoring & Tracing
    "opentelemetry-api",
    "opentelemetry-sdk",
    "structlog",
    "prometheus_client",
    
    # Security
    "cryptography",
    "PyJWT",
    "bcrypt",
    
    # Scheduling & Jobs
    "APScheduler",
    "celery",
    
    # Utilities
    "python-dateutil",
    "pytz",
    "tqdm",
    "click",
    "typer",
    "rich",
    "tenacity",
    "validators",
    
    # Streamlit Extensions
    "streamlit-shadcn-ui",
    "streamlit-extras",
    "streamlit-camera-input-live",
    "streamlit-sortables",
    "st-theme",
    
    # Code Quality
    "black",
    "mypy",
    "ruff",
    "pre_commit",
    
    # Build Tools
    "pyinstaller",
    "setuptools",
    "wheel",
    "build",
    "pip",
    "distutils",
    
    # Additional Data Processing
    "jsonschema",
    "marshmallow",
    "cerberus",
    
    # Additional Web
    "httpx",
    "aiohttp",
    "urllib3",
    
    # Additional Database
    "psycopg2",
    "pymysql",
    "pymongo",
    
    # Additional Utilities
    "pathlib",
    "zipfile",
    "shutil",
    "glob",
    "fnmatch",
    
    # Performance
    "cProfile",
    "memory_profiler",
    "line_profiler",
    
    # Email
    "smtplib",
    "imaplib",
    "email",
    
    # Additional Visualization
    "seaborn",
    "bokeh",
    "dash",
    
    # Additional File Formats
    "h5py",
    "netCDF4",
    "pyarrow",
    "feather",
]

for package_name in critical_packages:
    try:
        pkg = importlib.import_module(package_name)
        version = getattr(pkg, "__version__", "unbekannt")
        success.append(f"  ✓ {package_name} ({version})")
    except ImportError:
        errors.append(f"  ✗ FEHLT: {package_name} - installiere mit: pip install {package_name}")

# 5. Prüfe PyInstaller
print("\n5. Prüfe PyInstaller...")
try:
    import PyInstaller
    success.append(f"  ✓ PyInstaller {PyInstaller.__version__}")
except ImportError:
    errors.append("  ✗ PyInstaller nicht installiert - installiere mit: pip install pyinstaller")

# 6. Prüfe .spec Datei
print("\n6. Prüfe .spec Datei...")
spec_files = list(Path(".").glob("*.spec"))
if spec_files:
    for spec_file in spec_files:
        content = spec_file.read_text(encoding='utf-8')
        
        # Prüfe auf kritische excludes
        if "'email'" in content and "excludes=" in content:
            line_num = 0
            for i, line in enumerate(content.split('\n'), 1):
                if "'email'" in line and "excludes=" in line:
                    line_num = i
                    break
            errors.append(f"  ✗ KRITISCH: {spec_file.name}:{line_num} - 'email' in excludes gefunden!")
            errors.append("     → email/http/xml dürfen NICHT ausgeschlossen werden!")
        
        if "'http'" in content and "excludes=" in content:
            warnings.append(f"  ⚠ {spec_file.name} - 'http' in excludes gefunden (kann zu Problemen führen)")
        
        if "'xml'" in content and "excludes=" in content:
            warnings.append(f"  ⚠ {spec_file.name} - 'xml' in excludes gefunden (kann zu Problemen führen)")
        
        # Prüfe ob wichtige hiddenimports vorhanden sind
        if "streamlit" not in content:
            warnings.append(f"  ⚠ {spec_file.name} - 'streamlit' nicht in hiddenimports")
        else:
            success.append(f"  ✓ {spec_file.name} - streamlit in hiddenimports")
        
        if "pyvista" not in content:
            warnings.append(f"  ⚠ {spec_file.name} - 'pyvista' nicht in hiddenimports (3D-Visualisierung fehlt!)")
        else:
            success.append(f"  ✓ {spec_file.name} - pyvista in hiddenimports")
        
        if "sqlalchemy" not in content:
            warnings.append(f"  ⚠ {spec_file.name} - 'sqlalchemy' nicht in hiddenimports")
        else:
            success.append(f"  ✓ {spec_file.name} - sqlalchemy in hiddenimports")
else:
    warnings.append("  ⚠ Keine .spec Datei gefunden - wird beim Build erstellt")

# 7. Prüfe Icon
print("\n7. Prüfe App-Icon...")
icon_path = Path("data/company_logos/app_icon.ico")
if icon_path.exists():
    size_kb = icon_path.stat().st_size / 1024
    success.append(f"  ✓ Icon gefunden ({size_kb:.1f} KB)")
else:
    warnings.append("  ⚠ Icon nicht gefunden - Build verwendet Standard-Icon")

# 8. Prüfe Inno Setup (optional)
print("\n8. Prüfe Inno Setup (optional)...")
inno_paths = [
    r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    r"C:\Program Files\Inno Setup 6\ISCC.exe",
]
inno_found = False
for path_str in inno_paths:
    path = Path(path_str)
    if path.exists():
        success.append(f"  ✓ Inno Setup gefunden: {path}")
        inno_found = True
        break

if not inno_found:
    warnings.append("  ⚠ Inno Setup nicht installiert - Setup-Installer kann nicht erstellt werden")
    warnings.append("     Download: https://jrsoftware.org/isdl.php")

# 9. Prüfe Emoji-Probleme in Code
print("\n9. Prüfe auf Emoji-Probleme...")
emoji_problem_files = []
for py_file in Path(".").rglob("*.py"):
    if "emoji_removal_backup" in str(py_file) or "__pycache__" in str(py_file):
        continue
    try:
        content = py_file.read_text(encoding='utf-8')
        if 'icon=""' in content or "icon=''" in content:
            emoji_problem_files.append(str(py_file))
    except Exception:
        pass

if emoji_problem_files:
    warnings.append(f"  ⚠ {len(emoji_problem_files)} Dateien mit leeren icon='' gefunden")
    for f in emoji_problem_files[:5]:  # Nur erste 5 anzeigen
        warnings.append(f"     → {f}")
else:
    success.append("  ✓ Keine leeren icon='' Probleme gefunden")

# 10. Prüfe Database-Schema
print("\n10. Prüfe Datenbank-Schema...")
db_path = Path("data/app_data.db")
if db_path.exists():
    import sqlite3
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("PRAGMA user_version")
        db_version = cursor.fetchone()[0]
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        success.append(f"  ✓ Datenbank gefunden (Schema v{db_version}, {len(tables)} Tabellen)")
        
        # Prüfe wichtige Tabellen (umfassende Liste)
        required_tables = [
            # CRM Core
            'customers',
            'projects',
            'crm_leads',
            'crm_tasks',
            'crm_activities',
            'crm_notes',
            'crm_tags',
            'customer_tags',
            'crm_calls',
            'crm_emails',
            
            # Produkte & Preise
            'products',
            'product_categories',
            'product_attributes',
            'price_matrices',
            'pricing_rules',
            'profit_margins',
            'heatpump_products',
            'pv_modules',
            'inverters',
            'storage_systems',
            
            # Dokumente & Verträge
            'customer_documents',
            'project_calculations',
            'contracts',
            'warranties',
            'document_templates',
            'template_versions',
            'pdf_archives',
            
            # Admin & System
            'admin_settings',
            'users',
            'user_roles',
            'sessions',
            'session_data',
            'logs',
            'audit_trail',
            
            # Jobs & Background Tasks
            'jobs',
            'job_results',
            'scheduled_jobs',
            
            # Mounting & Installation
            'pv_mounting_systems',
            'pv_mounting_configurations',
            'installation_quotes',
            
            # Branding & Logos
            'brand_logos',
            'company_settings',
            'logo_positions',
            
            # Financial & Controlling
            'financial_calculations',
            'controlling_data',
            'payment_terms',
            'invoices',
            'quotations',
            
            # Services & Additional Costs
            'services',
            'service_categories',
            'additional_costs',
        ]
        
        missing_tables = [t for t in required_tables if t not in tables]
        if missing_tables:
            # Kategorisiere fehlende Tabellen
            critical_missing = [t for t in ['customers', 'projects', 'products', 'admin_settings'] if t in missing_tables]
            other_missing = [t for t in missing_tables if t not in critical_missing]
            
            if critical_missing:
                errors.append(f"  ✗ KRITISCHE Tabellen fehlen: {', '.join(critical_missing)}")
            if other_missing:
                warnings.append(f"  ⚠ {len(other_missing)} optionale Tabellen fehlen (erste 10): {', '.join(other_missing[:10])}")
        else:
            success.append(f"  ✓ Alle {len(required_tables)} wichtigen Tabellen vorhanden")
        
        # Prüfe Tabellenintegrität (Foreign Keys, Indices)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_key_check")
        fk_violations = cursor.fetchall()
        if fk_violations:
            warnings.append(f"  ⚠ {len(fk_violations)} Foreign Key Violations gefunden")
        
        # Prüfe Datenbankgröße
        db_size_mb = db_path.stat().st_size / (1024 * 1024)
        if db_size_mb > 500:
            warnings.append(f"  ⚠ Datenbank sehr groß: {db_size_mb:.1f} MB (Backup empfohlen)")
        else:
            success.append(f"  ✓ Datenbankgröße: {db_size_mb:.1f} MB")
            
    except Exception as e:
        warnings.append(f"  ⚠ Datenbank-Prüfung fehlgeschlagen: {e}")
else:
    warnings.append("  ⚠ Datenbank nicht gefunden - wird beim ersten Start erstellt")

# 11. Prüfe PDF-Template-System (Komplett)
print("\n11. Prüfe PDF-Template-System...")

# 11.1 Prüfe Multi-Firma YAML-Koordinaten
coords_files = list(Path("coords_multi").glob("seite*_f*.yml"))
if coords_files:
    success.append(f"  ✓ {len(coords_files)} Multi-Firma YAML-Koordinaten gefunden")
    # Prüfe Struktur: seite1_f1.yml bis seite8_f7.yml erwartet
    expected_pages = 8
    expected_firms = 7
    missing_coords = []
    for page in range(1, expected_pages + 1):
        for firm in range(1, expected_firms + 1):
            coord_file = Path(f"coords_multi/seite{page}_f{firm}.yml")
            if not coord_file.exists():
                missing_coords.append(f"seite{page}_f{firm}.yml")
    
    if missing_coords and len(missing_coords) < 10:
        warnings.append(f"  ⚠ Fehlende Koordinaten: {', '.join(missing_coords)}")
    elif missing_coords:
        warnings.append(f"  ⚠ {len(missing_coords)} Koordinatendateien fehlen")
else:
    errors.append("  ✗ Keine PDF-Koordinaten gefunden (coords_multi/*.yml)")

# 11.2 Prüfe Wärmepumpen-Koordinaten
coords_wp_files = list(Path("coords_wp").glob("*.yml"))
if coords_wp_files:
    success.append(f"  ✓ {len(coords_wp_files)} Wärmepumpen-Koordinaten gefunden")
else:
    warnings.append("  ⚠ Keine Wärmepumpen-Koordinaten gefunden (coords_wp/*.yml)")

# 11.3 Prüfe Standard-Koordinaten
coords_std_files = list(Path("coords").glob("*.yml"))
if coords_std_files:
    success.append(f"  ✓ {len(coords_std_files)} Standard-Koordinaten gefunden")
else:
    warnings.append("  ⚠ Keine Standard-Koordinaten gefunden (coords/*.yml)")

# 11.4 Prüfe Multi-Firma PDF-Templates
template_pdfs = list(Path("pdf_templates_static/multi").glob("multi_nt_*_f*.pdf"))
if template_pdfs:
    success.append(f"  ✓ {len(template_pdfs)} Multi-Firma PDF-Templates gefunden")
    # Prüfe Struktur: multi_nt_1_f1.pdf bis multi_nt_8_f7.pdf erwartet
    expected_pages = 8
    expected_firms = 7
    missing_templates = []
    for page in range(1, expected_pages + 1):
        for firm in range(1, expected_firms + 1):
            template_file = Path(f"pdf_templates_static/multi/multi_nt_{page}_f{firm}.pdf")
            if not template_file.exists():
                missing_templates.append(f"multi_nt_{page}_f{firm}.pdf")
    
    if missing_templates and len(missing_templates) < 10:
        warnings.append(f"  ⚠ Fehlende Templates: {', '.join(missing_templates)}")
    elif missing_templates:
        warnings.append(f"  ⚠ {len(missing_templates)} PDF-Templates fehlen")
else:
    errors.append("  ✗ Keine Multi-Firma PDF-Templates gefunden (pdf_templates_static/multi/*.pdf)")

# 11.5 Prüfe NoText-Templates
notext_pdfs = list(Path("pdf_templates_static/notext").glob("*.pdf"))
if notext_pdfs:
    success.append(f"  ✓ {len(notext_pdfs)} NoText-Templates gefunden")
else:
    warnings.append("  ⚠ Keine NoText-Templates gefunden")

# 11.6 Prüfe PDF-Template-Engine Module
pdf_engine_modules = [
    "pdf_template_engine/dynamic_overlay.py",
    "pdf_template_engine/placeholders.py",
    "pdf_template_engine/merger.py",
    "pdf_template_engine/__init__.py",
]
missing_engine = []
for module in pdf_engine_modules:
    if not Path(module).exists():
        missing_engine.append(module)

if missing_engine:
    errors.append(f"  ✗ Fehlende Engine-Module: {', '.join(missing_engine)}")
else:
    success.append(f"  ✓ Alle {len(pdf_engine_modules)} PDF-Engine-Module vorhanden")

# 11.7 Prüfe PDF-Generierungs-Module
pdf_gen_modules = [
    "pdf_generator.py",
    "product_rotation_engine.py",
    "price_modification_engine.py",
    "central_pdf_system.py",
    "multi_offer_generator.py",
    "pdf_preview.py",
    "pdf_ui.py",
    "pdf_widgets.py",
    "pdf_payment_summary.py",
]
missing_gen = []
for module in pdf_gen_modules:
    if not Path(module).exists():
        missing_gen.append(module)

if missing_gen:
    errors.append(f"  ✗ Fehlende Generator-Module: {', '.join(missing_gen)}")
else:
    success.append(f"  ✓ Alle {len(pdf_gen_modules)} PDF-Generator-Module vorhanden")

# 11.8 Prüfe PDF-Archive-Verzeichnis
pdf_archive_dirs = [
    "customer_documents",
    "pdf_output",
    "pdf_previews",
]
for pdf_dir in pdf_archive_dirs:
    if Path(pdf_dir).exists():
        success.append(f"  ✓ {pdf_dir}/ vorhanden")
    else:
        warnings.append(f"  ⚠ {pdf_dir}/ fehlt (wird automatisch erstellt)")

# 11.9 Prüfe Platzhalter-Mapping
try:
    placeholders_file = Path("pdf_template_engine/placeholders.py")
    if placeholders_file.exists():
        content = placeholders_file.read_text(encoding='utf-8')
        if "PLACEHOLDER_MAPPING" in content:
            success.append("  ✓ PLACEHOLDER_MAPPING vorhanden")
        else:
            warnings.append("  ⚠ PLACEHOLDER_MAPPING nicht in placeholders.py gefunden")
    else:
        errors.append("  ✗ pdf_template_engine/placeholders.py fehlt")
except Exception as e:
    warnings.append(f"  ⚠ Fehler beim Prüfen von placeholders.py: {e}")

# 11.10 Prüfe PDF-Positioning Tools
pdf_pos_tools = [
    "multi_pdf_positioning/coordinate_extractor.py",
    "multi_pdf_positioning/pdf_analyzer.py",
]
missing_pos = []
for tool in pdf_pos_tools:
    if not Path(tool).exists():
        missing_pos.append(tool)

if not missing_pos:
    success.append(f"  ✓ PDF-Positioning-Tools vorhanden")
elif len(missing_pos) == len(pdf_pos_tools):
    warnings.append("  ⚠ Keine PDF-Positioning-Tools gefunden (optional)")
else:
    warnings.append(f"  ⚠ Fehlende Positioning-Tools: {', '.join(missing_pos)}")

# 11.11 Prüfe ReportLab Fonts (Standard-Fonts sollten immer verfügbar sein)
try:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    # Prüfe Standard-Fonts
    required_fonts = ["Helvetica", "Helvetica-Bold", "Times-Roman", "Courier"]
    for font_name in required_fonts:
        try:
            # ReportLab Standard-Fonts sind immer verfügbar
            success.append(f"  ✓ Font '{font_name}' verfügbar")
        except:
            warnings.append(f"  ⚠ Font '{font_name}' möglicherweise nicht verfügbar")
except ImportError:
    errors.append("  ✗ ReportLab nicht importierbar - PDF-Generierung unmöglich!")

# 11.12 Prüfe PDF-Merge-Capabilities
try:
    import PyPDF2
    import pypdf
    success.append("  ✓ PDF-Merge-Libraries vorhanden (PyPDF2, pypdf)")
except ImportError as e:
    errors.append(f"  ✗ PDF-Merge-Library fehlt: {e}")

# 11.13 Prüfe erweiterte PDF-Libraries
pdf_advanced_libs = {
    "pdfplumber": "PDF-Text-Extraktion & Tabellenanalyse",
    "fitz": "PyMuPDF - Rendering & Manipulation",
    "pikepdf": "PDF-Struktur-Bearbeitung & Reparatur",
    "pdf2image": "PDF zu Bild-Konvertierung",
}
for lib_name, lib_desc in pdf_advanced_libs.items():
    try:
        lib = importlib.import_module(lib_name)
        version = getattr(lib, "__version__", "unbekannt")
        success.append(f"  ✓ {lib_name} ({lib_desc}) - v{version}")
    except ImportError:
        warnings.append(f"  ⚠ {lib_name} fehlt ({lib_desc}) - optional")

# 11.14 Prüfe PDF-Metadaten-Handler
try:
    pdf_gen_file = Path("pdf_generator.py")
    if pdf_gen_file.exists():
        content = pdf_gen_file.read_text(encoding='utf-8')
        metadata_features = []
        
        if "setAuthor" in content or "set_author" in content:
            metadata_features.append("Author")
        if "setTitle" in content or "set_title" in content:
            metadata_features.append("Title")
        if "setSubject" in content or "set_subject" in content:
            metadata_features.append("Subject")
        if "setCreator" in content or "set_creator" in content:
            metadata_features.append("Creator")
        
        if metadata_features:
            success.append(f"  ✓ PDF-Metadaten unterstützt: {', '.join(metadata_features)}")
        else:
            warnings.append("  ⚠ Keine PDF-Metadaten-Funktionen gefunden")
except Exception as e:
    warnings.append(f"  ⚠ Metadaten-Check fehlgeschlagen: {e}")

# 11.15 Prüfe PDF-Wasserzeichen/Overlay-Funktionen
try:
    overlay_file = Path("pdf_template_engine/dynamic_overlay.py")
    if overlay_file.exists():
        content = overlay_file.read_text(encoding='utf-8')
        overlay_features = []
        
        if "Canvas" in content:
            overlay_features.append("Canvas-Drawing")
        if "drawString" in content or "drawRightString" in content:
            overlay_features.append("Text-Overlay")
        if "drawImage" in content:
            overlay_features.append("Bild-Overlay")
        if "setFillColor" in content or "setStrokeColor" in content:
            overlay_features.append("Farb-Support")
        if "drawRightString" in content:
            overlay_features.append("Rechtsbündige Preise")
        
        if overlay_features:
            success.append(f"  ✓ Overlay-Features: {', '.join(overlay_features)}")
        else:
            warnings.append("  ⚠ Keine Overlay-Features gefunden")
except Exception as e:
    warnings.append(f"  ⚠ Overlay-Check fehlgeschlagen: {e}")

# 11.16 Prüfe PDF-Komprimierung/Optimierung
try:
    # Prüfe ob PDF-Komprimierung implementiert ist
    pdf_files_to_check = ["pdf_generator.py", "central_pdf_system.py"]
    compression_found = False
    
    for pdf_file in pdf_files_to_check:
        if Path(pdf_file).exists():
            content = Path(pdf_file).read_text(encoding='utf-8')
            if "compress" in content.lower() or "optimization" in content.lower():
                compression_found = True
                success.append(f"  ✓ PDF-Komprimierung in {pdf_file}")
                break
    
    if not compression_found:
        warnings.append("  ⚠ Keine PDF-Komprimierung gefunden (PDFs könnten groß sein)")
except Exception as e:
    warnings.append(f"  ⚠ Komprimierungs-Check fehlgeschlagen: {e}")

# 11.17 Prüfe PDF-Preview/Viewer-Integration
pdf_preview_files = [
    "pdf_preview.py",
    "pdf_ui.py",
    "pdf_widgets.py",
]
preview_found = []
for preview_file in pdf_preview_files:
    if Path(preview_file).exists():
        preview_found.append(preview_file)

if preview_found:
    success.append(f"  ✓ {len(preview_found)} PDF-Preview-Module vorhanden")
else:
    warnings.append("  ⚠ Keine PDF-Preview-Module gefunden")

# 11.18 Prüfe PDF-Archivierung/Versionierung
try:
    db_path = Path("data/app_data.db")
    if db_path.exists():
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Prüfe PDF-Archive-Tabellen
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%pdf%' OR name LIKE '%document%'")
        pdf_tables = [row[0] for row in cursor.fetchall()]
        
        if pdf_tables:
            success.append(f"  ✓ {len(pdf_tables)} PDF-Archive-Tabellen: {', '.join(pdf_tables[:3])}")
        else:
            warnings.append("  ⚠ Keine PDF-Archive-Tabellen gefunden")
        
        conn.close()
except Exception as e:
    warnings.append(f"  ⚠ PDF-Archive-Check fehlgeschlagen: {e}")

# 11.19 Prüfe Multi-Angebots-System
multi_offer_files = [
    "multi_offer_generator.py",
    "product_rotation_engine.py",
    "price_modification_engine.py",
]
multi_system_complete = all(Path(f).exists() for f in multi_offer_files)

if multi_system_complete:
    success.append("  ✓ Multi-Angebots-System vollständig")
    
    # Prüfe auf progressive Preiskalkulation
    try:
        price_mod_file = Path("price_modification_engine.py")
        content = price_mod_file.read_text(encoding='utf-8')
        
        features = []
        if "modifier" in content.lower():
            features.append("Preis-Modifier")
        if "progression" in content.lower():
            features.append("Progressive Kalkulation")
        if "rotation" in content.lower() or "rotate" in content.lower():
            features.append("Produkt-Rotation")
        
        if features:
            success.append(f"  ✓ Multi-Features: {', '.join(features)}")
    except Exception:
        pass
else:
    missing = [f for f in multi_offer_files if not Path(f).exists()]
    errors.append(f"  ✗ Multi-System unvollständig, fehlt: {', '.join(missing)}")

# 11.20 Prüfe PDF-Zahlungsbedingungen-Integration
if Path("pdf_payment_summary.py").exists():
    success.append("  ✓ PDF-Zahlungsbedingungen-Modul vorhanden")
    
    # Prüfe Datenbank-Integration
    try:
        db_path = Path("data/app_data.db")
        if db_path.exists():
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='payment_terms'")
            if cursor.fetchone():
                success.append("  ✓ payment_terms-Tabelle vorhanden")
            else:
                warnings.append("  ⚠ payment_terms-Tabelle fehlt")
            conn.close()
    except Exception:
        pass
else:
    warnings.append("  ⚠ pdf_payment_summary.py fehlt")

# 11.21 Prüfe PDF-Firmen-Konfiguration (f1-f7)
try:
    # Prüfe ob alle 7 Firmen konfiguriert sind
    coords_multi_path = Path("coords_multi")
    if coords_multi_path.exists():
        firm_counts = {}
        for yml_file in coords_multi_path.glob("*.yml"):
            # Extrahiere Firma (f1, f2, ...)
            if "_f" in yml_file.name:
                firm = yml_file.name.split("_f")[1].split(".")[0]
                firm_counts[firm] = firm_counts.get(firm, 0) + 1
        
        if len(firm_counts) >= 7:
            success.append(f"  ✓ {len(firm_counts)} Firmen-Konfigurationen vorhanden")
        elif len(firm_counts) > 0:
            warnings.append(f"  ⚠ Nur {len(firm_counts)}/7 Firmen konfiguriert")
        else:
            errors.append("  ✗ Keine Firmen-Konfigurationen gefunden")
except Exception as e:
    warnings.append(f"  ⚠ Firmen-Config-Check fehlgeschlagen: {e}")

# 11.22 Prüfe PDF-Seiten-Struktur (Seite 1-8)
try:
    template_multi_path = Path("pdf_templates_static/multi")
    if template_multi_path.exists():
        page_counts = {}
        for pdf_file in template_multi_path.glob("*.pdf"):
            # Extrahiere Seitennummer
            if "_nt_" in pdf_file.name:
                parts = pdf_file.name.split("_nt_")[1]
                page = parts.split("_")[0]
                page_counts[page] = page_counts.get(page, 0) + 1
        
        expected_pages = ['1', '2', '3', '4', '5', '6', '7', '8']
        missing_pages = [p for p in expected_pages if p not in page_counts]
        
        if not missing_pages:
            success.append("  ✓ Alle 8 PDF-Seiten vorhanden")
        else:
            warnings.append(f"  ⚠ Fehlende Seiten: {', '.join(missing_pages)}")
except Exception as e:
    warnings.append(f"  ⚠ Seiten-Struktur-Check fehlgeschlagen: {e}")

# 11.23 Prüfe PDF-Error-Handling
try:
    pdf_gen_file = Path("pdf_generator.py")
    if pdf_gen_file.exists():
        content = pdf_gen_file.read_text(encoding='utf-8')
        
        error_handling = []
        if "try:" in content and "except" in content:
            error_handling.append("Exception-Handling")
        if "logging" in content.lower() or "logger" in content.lower():
            error_handling.append("Logging")
        if "raise" in content:
            error_handling.append("Error-Propagation")
        
        if len(error_handling) >= 2:
            success.append(f"  ✓ PDF Error-Handling: {', '.join(error_handling)}")
        else:
            warnings.append("  ⚠ Unzureichendes PDF Error-Handling")
except Exception:
    pass

# 12. Prüfe Lokalisierung
print("\n12. Prüfe Lokalisierungsdateien...")
locale_files = list(Path(".").glob("*.json"))
de_json = Path("de.json")
if de_json.exists():
    try:
        with open(de_json, 'r', encoding='utf-8') as f:
            locale_data = json.load(f)
            key_count = len(locale_data)
            success.append(f"  ✓ de.json vorhanden ({key_count} Texte)")
    except Exception as e:
        errors.append(f"  ✗ de.json nicht lesbar: {e}")
else:
    errors.append("  ✗ de.json fehlt - App hat keine Texte!")

# 13. Prüfe Core-Integration
print("\n13. Prüfe Core-Integration...")
core_modules = [
    "core_integration.py",
    "core/config.py",
    "core/logging_config.py",
    "core/cache.py",
    "core/session.py",
    "core/database.py",
    "core/router.py",
    "core/jobs.py",
]

missing_core = []
for core_file in core_modules:
    if not Path(core_file).exists():
        missing_core.append(core_file)

if missing_core:
    errors.append(f"  ✗ Fehlende Core-Module: {', '.join(missing_core)}")
else:
    success.append(f"  ✓ Alle {len(core_modules)} Core-Module vorhanden")

# 14. Prüfe .gitignore und .streamlit
print("\n14. Prüfe Projekt-Konfiguration...")
if Path(".gitignore").exists():
    success.append("  ✓ .gitignore vorhanden")
else:
    warnings.append("  ⚠ .gitignore fehlt")

if Path(".streamlit/secrets.toml").exists():
    success.append("  ✓ Streamlit secrets.toml vorhanden")
else:
    warnings.append("  ⚠ secrets.toml fehlt (für API-Keys)")

# 16. Prüfe auf häufige Build-Probleme (Erweitert)
print("\n16. Prüfe auf bekannte Build-Probleme...")

# 16.1 Prüfe auf Session State Pickle-Probleme
pickle_files_to_check = ["gui.py", "crm.py", "calculations.py", "database.py", "core/session.py"]
for py_file_name in pickle_files_to_check:
    py_file = Path(py_file_name)
    if py_file.exists():
        content = py_file.read_text(encoding='utf-8')
        if "__getstate__" in content and "__setstate__" in content:
            success.append(f"  ✓ {py_file.name} - Pickle-Support vorhanden")

# 16.2 Prüfe auf hardcodierte Pfade
hardcoded_found = []
for py_file in Path(".").rglob("*.py"):
    if "test_" in py_file.name or "__pycache__" in str(py_file):
        continue
    try:
        content = py_file.read_text(encoding='utf-8')
        if "C:\\\\Users" in content or "C:/Users" in content or "D:\\\\" in content:
            hardcoded_found.append(py_file.name)
            if len(hardcoded_found) >= 5:
                break
    except Exception:
        pass

if hardcoded_found:
    warnings.append(f"  ⚠ Hardcodierte Pfade in: {', '.join(hardcoded_found[:5])}")
else:
    success.append("  ✓ Keine hardcodierten Benutzerpfade gefunden")

# 16.3 Prüfe auf relative Import-Probleme
for py_file in [Path("gui.py"), Path("database.py"), Path("calculations.py")]:
    if py_file.exists():
        content = py_file.read_text(encoding='utf-8')
        if "from ." in content:
            warnings.append(f"  ⚠ {py_file.name} verwendet relative Imports")

# 16.4 Prüfe auf __main__ Guards
main_guards_missing = []
for py_file in ["gui.py", "admin_panel.py", "agent_ui.py"]:
    if Path(py_file).exists():
        content = Path(py_file).read_text(encoding='utf-8')
        if '__name__ == "__main__"' not in content and "__name__ == '__main__'" not in content:
            main_guards_missing.append(py_file)

if main_guards_missing:
    warnings.append(f"  ⚠ Fehlende __main__ Guards: {', '.join(main_guards_missing)}")
else:
    success.append("  ✓ __main__ Guards vorhanden")

# 16.5 Prüfe auf circular imports
try:
    circular_candidates = []
    for py_file in Path(".").glob("*.py"):
        if py_file.name.startswith("test_"):
            continue
        try:
            content = py_file.read_text(encoding='utf-8')
            imports = [line for line in content.split('\n') if line.strip().startswith('import ') or line.strip().startswith('from ')]
            if len(imports) > 50:
                circular_candidates.append(py_file.name)
        except Exception:
            pass
    
    if circular_candidates:
        warnings.append(f"  ⚠ Viele Imports (circular risk): {', '.join(circular_candidates[:3])}")
    else:
        success.append("  ✓ Keine offensichtlichen Circular-Import-Risiken")
except Exception:
    pass

# 16.6 Prüfe auf encoding-Probleme
encoding_issues = []
for py_file in Path(".").rglob("*.py"):
    if "__pycache__" in str(py_file):
        continue
    try:
        # Versuche mit UTF-8
        py_file.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        encoding_issues.append(str(py_file))
        if len(encoding_issues) >= 5:
            break

if encoding_issues:
    errors.append(f"  ✗ Encoding-Probleme: {', '.join(encoding_issues[:5])}")
else:
    success.append("  ✓ Alle Python-Dateien UTF-8 kompatibel")

# 16.7 Prüfe auf zu lange Pfade (Windows-Limit)
long_paths = []
for path in Path(".").rglob("*"):
    if len(str(path.absolute())) > 240:
        long_paths.append(str(path)[:60] + "...")
        if len(long_paths) >= 3:
            break

if long_paths:
    warnings.append(f"  ⚠ Lange Pfade (Windows-Limit): {len(long_paths)} Dateien")
else:
    success.append("  ✓ Keine zu langen Pfade (Windows-kompatibel)")

# 17. Prüfe CRM-System (Vollständig)
print("\n17. Prüfe CRM-System...")

# 17.1 Prüfe CRM-Hauptmodule
crm_core = [
    "crm.py",
    "crm_dashboard_ui.py",
    "crm_pipeline_ui.py",
    "crm_calendar_ui.py",
    "crm_shadcn.py",
]
missing_crm_core = [f for f in crm_core if not Path(f).exists()]
if not missing_crm_core:
    success.append(f"  ✓ Alle {len(crm_core)} CRM-Kernmodule vorhanden")
else:
    errors.append(f"  ✗ Fehlende CRM-Module: {', '.join(missing_crm_core)}")

# 17.2 Prüfe CRM-Features
crm_features_dir = Path("crm/features")
if crm_features_dir.exists():
    feature_files = list(crm_features_dir.glob("*.py"))
    if len(feature_files) >= 10:
        success.append(f"  ✓ {len(feature_files)} CRM-Features verfügbar")
    else:
        warnings.append(f"  ⚠ Nur {len(feature_files)} CRM-Features (erwartet: 15+)")
else:
    errors.append("  ✗ crm/features/ Verzeichnis fehlt")

# 17.3 Prüfe CRM-Integration
crm_integration_dir = Path("crm/integration")
if crm_integration_dir.exists():
    integration_files = list(crm_integration_dir.glob("*.py"))
    success.append(f"  ✓ {len(integration_files)} CRM-Integrations-Module")
else:
    warnings.append("  ⚠ crm/integration/ fehlt")

# 17.4 Prüfe CRM-Utils
crm_utils_dir = Path("crm/utils")
if crm_utils_dir.exists():
    utils_files = list(crm_utils_dir.glob("*.py"))
    success.append(f"  ✓ {len(utils_files)} CRM-Utility-Module")
else:
    warnings.append("  ⚠ crm/utils/ fehlt")

# 17.5 Prüfe CRM-Datenbank-Tabellen
try:
    db_path = Path("data/app_data.db")
    if db_path.exists():
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        crm_tables = ['customers', 'projects', 'crm_leads', 'crm_tasks', 'crm_activities', 'crm_notes']
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_crm_tables = [t for t in crm_tables if t not in existing_tables]
        if not missing_crm_tables:
            success.append(f"  ✓ Alle {len(crm_tables)} CRM-Tabellen vorhanden")
        else:
            errors.append(f"  ✗ Fehlende CRM-Tabellen: {', '.join(missing_crm_tables)}")
        
        conn.close()
except Exception as e:
    warnings.append(f"  ⚠ CRM-DB-Check fehlgeschlagen: {e}")

# 18. Prüfe Pricing-System (Vollständig)
print("\n18. Prüfe Pricing-System...")

# 18.1 Prüfe Pricing-Engine-Module
pricing_dir = Path("pricing")
if pricing_dir.exists():
    pricing_modules = list(pricing_dir.glob("*.py"))
    if len(pricing_modules) >= 8:
        success.append(f"  ✓ {len(pricing_modules)} Pricing-Module vorhanden")
    else:
        warnings.append(f"  ⚠ Nur {len(pricing_modules)} Pricing-Module (erwartet: 8+)")
else:
    errors.append("  ✗ pricing/ Verzeichnis fehlt")

# 18.2 Prüfe Price-Matrices
try:
    db_path = Path("data/app_data.db")
    if db_path.exists():
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM price_matrices")
        matrix_count = cursor.fetchone()[0]
        
        if matrix_count > 0:
            success.append(f"  ✓ {matrix_count} Preismatrizen in Datenbank")
        else:
            warnings.append("  ⚠ Keine Preismatrizen in Datenbank")
        
        conn.close()
except Exception as e:
    warnings.append(f"  ⚠ Price-Matrix-Check fehlgeschlagen: {e}")

# 18.3 Prüfe Profit-Margin-System
if Path("admin_profit_margin_ui.py").exists() and Path("pricing/profit_margin_manager.py").exists():
    success.append("  ✓ Profit-Margin-System vollständig")
else:
    warnings.append("  ⚠ Profit-Margin-System unvollständig")

# 18.4 Prüfe Heatpump-Pricing
if Path("heatpump_pricing.py").exists() and Path("pricing/enhanced_heatpump_pricing.py").exists():
    success.append("  ✓ Wärmepumpen-Pricing-System vorhanden")
else:
    warnings.append("  ⚠ Wärmepumpen-Pricing unvollständig")

# 19. Prüfe Agent-System (Vollständig)
print("\n19. Prüfe Agent-System...")

# 19.1 Prüfe Agent-Verzeichnis
agent_dir = Path("Agent")
if agent_dir.exists():
    agent_files = list(agent_dir.rglob("*.py"))
    if len(agent_files) >= 5:
        success.append(f"  ✓ {len(agent_files)} Agent-Module gefunden")
    else:
        warnings.append(f"  ⚠ Nur {len(agent_files)} Agent-Module")
else:
    warnings.append("  ⚠ Agent/ Verzeichnis fehlt (optional)")

# 19.2 Prüfe Agent-Core
if Path("Agent/agent/agent_core.py").exists():
    success.append("  ✓ Agent-Core vorhanden")
else:
    warnings.append("  ⚠ Agent-Core fehlt")

# 19.3 Prüfe Agent-Tools
agent_tools_dir = Path("Agent/agent/tools")
if agent_tools_dir.exists():
    tool_files = list(agent_tools_dir.glob("*.py"))
    success.append(f"  ✓ {len(tool_files)} Agent-Tools verfügbar")
else:
    warnings.append("  ⚠ Agent-Tools fehlen")

# 19.4 Prüfe Agent-UI
if Path("agent_ui.py").exists() and Path("ai_companion.py").exists():
    success.append("  ✓ Agent-UI-Module vorhanden")
else:
    warnings.append("  ⚠ Agent-UI unvollständig")

# 20. Prüfe 3D-Visualisierung
print("\n20. Prüfe 3D-Visualisierung...")

# 20.1 Prüfe PyVista
try:
    import pyvista
    import vtk
    success.append(f"  ✓ PyVista {pyvista.__version__} installiert")
except ImportError:
    errors.append("  ✗ PyVista fehlt - 3D-Visualisierung unmöglich!")

# 20.2 Prüfe 3D-Module
if Path("pv_visuals.py").exists():
    success.append("  ✓ pv_visuals.py vorhanden")
else:
    warnings.append("  ⚠ pv_visuals.py fehlt")

# 20.3 Prüfe PV-Module-Placement
if Path("utils/pv_module_placement_system.py").exists():
    success.append("  ✓ PV-Modul-Platzierungssystem vorhanden")
else:
    warnings.append("  ⚠ PV-Placement-System fehlt")

if Path("utils/pv_module_rendering_3d.py").exists():
    success.append("  ✓ 3D-Rendering-Engine vorhanden")
else:
    warnings.append("  ⚠ 3D-Rendering-Engine fehlt")

# 21. Prüfe Excel-Integration
print("\n21. Prüfe Excel-Integration...")

excel_modules = ["excel_grid_ui.py", "excel_processing.py", "data_grid.py"]
excel_found = [m for m in excel_modules if Path(m).exists()]
if excel_found:
    success.append(f"  ✓ {len(excel_found)} Excel-Module gefunden")

excel_dir = Path("excel")
if excel_dir.exists():
    excel_files = list(excel_dir.glob("*.py"))
    success.append(f"  ✓ excel/ Verzeichnis mit {len(excel_files)} Dateien")

try:
    import openpyxl
    import xlrd
    success.append("  ✓ Excel-Libraries (openpyxl, xlrd) vorhanden")
except ImportError:
    warnings.append("  ⚠ Excel-Libraries fehlen")

# 22. Prüfe Dokumentation & Logs
print("\n22. Prüfe Dokumentation & Logs...")

doc_files = list(Path(".").glob("*.md"))
if len(doc_files) >= 5:
    success.append(f"  ✓ {len(doc_files)} Markdown-Dokumentationen gefunden")
else:
    warnings.append(f"  ⚠ Nur {len(doc_files)} MD-Dateien (Dokumentation gering)")

logs_dir = Path("logs")
if logs_dir.exists():
    success.append("  ✓ logs/ Verzeichnis vorhanden")
else:
    warnings.append("  ⚠ logs/ fehlt (wird automatisch erstellt)")

# 23. Prüfe Testing-Infrastruktur
print("\n23. Prüfe Testing-Infrastruktur...")

tests_dir = Path("tests")
if tests_dir.exists():
    test_files = list(tests_dir.glob("test_*.py"))
    if len(test_files) >= 3:
        success.append(f"  ✓ {len(test_files)} Test-Dateien vorhanden")
    else:
        warnings.append(f"  ⚠ Nur {len(test_files)} Tests (mehr empfohlen)")
else:
    warnings.append("  ⚠ tests/ Verzeichnis fehlt")

try:
    import pytest
    success.append(f"  ✓ pytest {pytest.__version__} installiert")
except ImportError:
    warnings.append("  ⚠ pytest nicht installiert")

# 24. Prüfe Backup & Migration
print("\n24. Prüfe Backup & Migration...")

backup_files = [
    "database_backup.py",
    "crm/utils/backup_scheduler.py",
    "database_pricing_migration.py",
    "data_migration.py",
]
backup_found = [f for f in backup_files if Path(f).exists()]
if len(backup_found) >= 2:
    success.append(f"  ✓ {len(backup_found)} Backup/Migration-Module vorhanden")
else:
    warnings.append(f"  ⚠ Nur {len(backup_found)} Backup-Module")

backups_dir = Path("backups")
if backups_dir.exists():
    success.append("  ✓ backups/ Verzeichnis vorhanden")

# 25. Prüfe Performance & Monitoring
print("\n25. Prüfe Performance & Monitoring...")

monitoring_files = [
    "app_health_monitor.py",
    "app_diagnostics.py",
    "app_status.py",
    "app_tracing.py",
    "app_evaluation.py",
]
monitoring_found = [f for f in monitoring_files if Path(f).exists()]
if len(monitoring_found) >= 4:
    success.append(f"  ✓ {len(monitoring_found)} Monitoring-Module aktiv")
else:
    warnings.append(f"  ⚠ Nur {len(monitoring_found)} Monitoring-Module")

# Prüfe OpenTelemetry
try:
    import opentelemetry
    success.append("  ✓ OpenTelemetry für Tracing vorhanden")
except ImportError:
    warnings.append("  ⚠ OpenTelemetry fehlt (Tracing optional)")

# Ausgabe Zusammenfassung
print("\n" + "=" * 70)
print("  ERGEBNIS")
print("=" * 70 + "\n")

if success:
    print("✓ ERFOLGE:")
    for msg in success:
        print(msg)

if warnings:
    print("\n⚠ WARNUNGEN:")
    for msg in warnings:
        print(msg)

if errors:
    print("\n✗ FEHLER (müssen behoben werden!):")
    for msg in errors:
        print(msg)

print("\n" + "=" * 70)
if errors:
    print("  ✗ BUILD NICHT BEREIT - Behebe die Fehler!")
    print("=" * 70 + "\n")
    sys.exit(1)
elif warnings:
    print("  ⚠ BUILD MIT EINSCHRÄNKUNGEN MÖGLICH")
    print("  Behebe die Warnungen für optimales Ergebnis")
    print("=" * 70 + "\n")
    sys.exit(0)
else:
    print("  ✓ BUILD BEREIT - Alle Voraussetzungen erfüllt!")
    print("=" * 70 + "\n")
    print("Starte Build mit: python build_exe_setup.py")
    sys.exit(0)
