ARSCHIBALD (Python Streamlit App)
│
├── 📄 HAUPTEINSTIEGSPUNKTE
│   ├── gui.py                                    # Haupt-Streamlit-App (Multi-Page Entry)
│   ├── admin_panel.py                            # Admin-Interface
│   ├── admin_core_status_extended_ui.py          # Extended Dashboard
│   └── admin_panel_shadcn.py                     # shadcn UI Admin
│
├── 🗄️ KERNMODULE
│   ├── database.py                               # Zentrale DB-Logik (2900+ Zeilen)
│   ├── calculations.py                           # PV-Berechnungen
│   ├── calculations_extended.py                  # Erweiterte Berechnungen
│   ├── calculations_heatpump.py                  # Wärmepumpen-Kalkulation
│   ├── financial_calculations.py                 # Finanzanalyse
│   ├── pv_calculations_core.py                   # PV-Berechnungs-Kern
│   ├── crm.py                                    # CRM-Kern
│   └── locales.py                                # i18n/Textressourcen
│
├── 📑 PDF-GENERIERUNGSSYSTEM
│   ├── pdf_generator.py                          # End-to-End PDF-Erstellung
│   ├── central_pdf_system.py                     # Zentrales PDF-System
│   ├── pdf_styles.py                             # PDF-Styling
│   ├── pdf_ui.py                                 # PDF-UI-Komponenten
│   ├── pdf_widgets.py                            # PDF-Widgets
│   ├── pdf_preview.py                            # PDF-Vorschau
│   ├── pdf_templates.py                          # Template-Management
│   ├── pdf_pricing_integration.py                # Pricing-Integration
│   ├── pdf_pricing_templates.py                  # Pricing-Templates
│   ├── pdf_services_integration.py               # Services-Integration
│   ├── pdf_payment_summary.py                    # Zahlungszusammenfassung
│   ├── pdf_with_payment.py                       # PDF mit Zahlung
│   ├── pdf_visual_inject.py                      # Visuelle Injection
│   ├── pdf_zu_markdown.py                        # PDF → Markdown
│   ├── pdf_zu_png.py                             # PDF → PNG
│   ├── multi_offer_generator.py                  # Multi-Angebots-Generator
│   ├── product_rotation_engine.py                # Produkt-Rotation
│   └── price_modification_engine.py              # Preismodifikation
│   │
│   └── 📁 pdf_template_engine/
│       ├── __init__.py
│       ├── dynamic_overlay.py                    # Text-Overlay-Engine (ReportLab)
│       ├── overlay.py                            # Basis-Overlay
│       ├── merger.py                             # PDF-Merge
│       ├── placeholders.py                       # Platzhalter-Mapping
│       └── prepare_backgrounds.py                # Background-Vorbereitung
│
├── 📂 PDF-TEMPLATES & KOORDINATEN
│   ├── 📁 pdf_templates_static/
│   │   ├── 📁 notext/                            # Hintergrund-PDFs ohne Text
│   │   │   ├── nt_nt_01.pdf bis nt_nt_08.pdf    # Standard 8 Seiten
│   │   │   └── hp_nt_01.pdf bis hp_nt_08.pdf    # Wärmepumpe 8 Seiten
│   │   │
│   │   ├── 📁 multi/                             # Multi-Firma Templates
│   │   │   └── multi_nt_{01-08}_f{1-6}.pdf      # 8 Seiten × 6 Firmen = 48 PDFs
│   │   │
│   │   └── merge_zips.py                         # ZIP-Merge-Tool
│   │
│   ├── 📁 coords_multi/                          # Firma-spezifische Koordinaten
│   │   └── seite{1-8}_f{1-7}.yml                # YAML-Koordinaten pro Seite/Firma
│   │
│   └── 📁 multi_pdf_positioning/                 # Positionierungs-System
│       ├── 📁 analysis/
│       ├── 📁 demo_batch_output/
│       ├── 📁 output/
│       ├── 📁 validation_reports/
│       └── 📁 validation_reports_verify/
│
├── 💰 PRICING-SYSTEM
│   ├── 📁 pricing/
│   │   ├── __init__.py
│   │   ├── README.md
│   │   ├── CACHE_DOCUMENTATION.md
│   │   ├── advanced_pricing_formula.py           # Erweiterte Formeln
│   │   ├── calculate_per_engine.py               # Per-Calculation Engine
│   │   ├── combined_pricing_engine.py            # Kombinierter Engine
│   │   ├── enhanced_pricing_engine.py            # Enhanced Engine
│   │   ├── enhanced_heatpump_pricing.py          # Wärmepumpen-Pricing
│   │   ├── pv_pricing_engine.py                  # PV-Pricing
│   │   ├── pricing_modification_engine.py        # Modifikationen
│   │   ├── pricing_cache.py                      # Caching
│   │   ├── cache_performance.py                  # Cache-Performance
│   │   ├── pricing_validation.py                 # Validierung
│   │   ├── pricing_errors.py                     # Fehlerbehandlung
│   │   ├── pricing_audit.py                      # Audit-Trail
│   │   ├── profitability_reporting.py            # Profit-Reports
│   │   ├── profit_margin_manager.py              # Margin-Management
│   │   ├── vat_manager.py                        # MwSt.-Verwaltung
│   │   ├── dynamic_key_manager.py                # Dynamische Keys
│   │   ├── economic_analysis_integration.py      # Wirtschaftsanalyse
│   │   ├── real_time_pricing_updates.py          # Echtzeit-Updates
│   │   ├── demo_enhanced_pricing.py              # Demo Enhanced
│   │   └── demo_pricing_cache.py                 # Demo Cache
│   │
│   ├── price_matrix_lookup.py                    # Matrix-Lookup
│   ├── price_matrix_validation.py                # Matrix-Validierung
│   ├── price_matrix_performance.py               # Matrix-Performance
│   ├── price_matrix_store.py                     # Matrix-Store
│   ├── price_matrix_examples.py                  # Beispiele
│   ├── price_matrix_error_handler.py             # Fehlerbehandlung
│   ├── price_matrix_error_handling.py            # Error-Handling
│   └── price_matrix_error_ui.py                  # Error-UI
│
├── 👥 CRM-SYSTEM
│   ├── 📁 crm/ (angenommen, basierend auf imports)
│   │   └── features/
│   │       └── contract_manager.py               # Vertrags-/Garantieverwaltung
│   │
│   ├── crm_api.py                                # CRM API
│   ├── crm_database.py                           # CRM-Datenbank
│   ├── crm_ui.py                                 # CRM-UI
│   └── contracts.py                              # Verträge
│
├── 🏢 PRODUKTDATENBANK
│   ├── product_db.py                             # Produkt-DB-Kern
│   ├── product_database.db                       # SQLite-Datenbank
│   ├── product_attributes.py                     # Produkt-Attribute
│   ├── special_products.py                       # Spezial-Produkte
│   ├── heatpump_database.py                      # Wärmepumpen-DB
│   ├── heatpump_utils.py                         # Wärmepumpen-Utils
│   ├── pv_mounting_database.py                   # PV-Montage-DB
│   ├── pv_mounting_db_bridge.py                  # Montage-DB-Bridge
│   ├── pv_mounting_calculations.py               # Montage-Berechnungen
│   ├── seed_pv_database.py                       # DB-Seed-Script
│   ├── seed_pv_database_extended.py              # Extended Seed
│   ├── professional_pv_modules.csv               # PV-Module-Daten
│   └── storage_resolver_demo.py                  # Speicher-Resolver
│
├── 🎨 THEMING & UI
│   ├── 📁 theming/
│   │   ├── __init__.py
│   │   ├── theme_manager.py                      # Theme-Manager
│   │   ├── theme_selector_ui.py                  # Theme-Selector
│   │   ├── theme_cache.py                        # Theme-Cache
│   │   ├── theme_validator.py                    # Theme-Validierung
│   │   ├── theme_tokens.py                       # Theme-Tokens
│   │   ├── theme_errors.py                       # Theme-Fehler
│   │   ├── theme_logger.py                       # Theme-Logging
│   │   ├── css_generator.py                      # CSS-Generator
│   │   ├── pdf_styles.py                         # PDF-Styles
│   │   ├── state_manager.py                      # State-Management
│   │   ├── accessibility.py                      # Barrierefreiheit
│   │   ├── error_handler.py                      # Error-Handler
│   │   ├── error_dashboard.py                    # Error-Dashboard
│   │   ├── monitoring_dashboard.py               # Monitoring
│   │   ├── performance_optimizer.py              # Performance
│   │   ├── hot_reload_manager.py                 # Hot-Reload
│   │   ├── dev_mode.py                           # Dev-Mode
│   │   ├── validation_display.py                 # Validierungs-Anzeige
│   │   │
│   │   ├── 📁 themes/                            # Theme-Definitionen (JSON)
│   │   │   ├── shadcn-default.json
│   │   │   ├── shadcn-dark.json
│   │   │   ├── shadcn-blue.json
│   │   │   ├── shadcn-blue-dark.json
│   │   │   ├── shadcn-purple.json
│   │   │   ├── shadcn-purple-dark.json
│   │   │   ├── shadcn-green.json
│   │   │   ├── shadcn-red.json
│   │   │   ├── shadcn-amber.json
│   │   │   ├── shadcn-cyan.json
│   │   │   ├── shadcn-forest.json
│   │   │   ├── shadcn-ocean.json
│   │   │   ├── shadcn-sunset.json
│   │   │   ├── demo-blue.json
│   │   │   ├── demo-blue-dark.json
│   │   │   ├── demo-green.json
│   │   │   └── demo-purple.json
│   │   │
│   │   └── 📁 amazing/awesome-streamlit-themes/  # Externe Themes
│   │       └── [bootstrap, cyberpunk, dark-mode, editorial, financial, 
│   │           healthcare, material-design, saas-startup, tailwind, toddler]/
│   │           ├── .streamlit/
│   │           └── static/
│   │
│   └── theme_manager.py                          # Root Theme-Manager
│
├── 🧩 KOMPONENTEN
│   ├── 📁 components/
│   │   ├── __init__.py
│   │   ├── shadcn_ui_integration.py              # shadcn-ui Wrapper
│   │   ├── progress_manager.py                   # Progress-Komponente
│   │   ├── carousel_ui_utils.py                  # Karussell-Utils
│   │   ├── carousel_ui_utils_native.py           # Native Karussell
│   │   └── carousel_preview.py                   # Karussell-Vorschau
│   │
│   ├── 📁 widgets/
│   │   └── __init__.py
│   │
│   ├── session_widgets.py                        # Session-Widgets
│   ├── ui_chart_helpers.py                       # Chart-Helpers
│   ├── ui_effects_library.py                     # UI-Effekte
│   ├── ui_settings_handler.py                    # UI-Settings
│   ├── ui_state_manager.py                       # UI-State
│   ├── advanced_charts.py                        # Erweiterte Charts
│   ├── advanced_features.py                      # Erweiterte Features
│   └── auto_chart_generator.py                   # Auto-Chart
│
├── 🏗️ CORE-SYSTEM
│   ├── 📁 core/
│   │   ├── __init__.py
│   │   ├── session.py                            # Session-Persistence
│   │   ├── router.py                             # Routing-System
│   │   └── navigation_history.py                 # Navigation-Historie
│   │
│   ├── app_status.py                             # App-Status
│   ├── app_tracing.py                            # Tracing
│   ├── app_evaluation.py                         # Evaluation
│   ├── app_health_monitor.py                     # Health-Monitor
│   ├── app_diagnostics.py                        # Diagnostik
│   ├── robustness_core.py                        # Robustheit
│   ├── performance_handler.py                    # Performance
│   ├── error_handler.py                          # Error-Handling
│   └── system_check.py                           # System-Check
│
├── 🖼️ 3D-VISUALISIERUNG
│   ├── pv3d.py                                   # 3D-Haupt-Modul
│   ├── pv3d_plotly.py                            # Plotly-3D
│   ├── pv_visuals.py                             # PV-Visuals
│   ├── solar_3d_view_enhanced.py                 # Enhanced 3D-View
│   ├── solar_3d_view_module.py                   # 3D-View-Modul
│   │
│   └── 📁 utils/
│       ├── __init__.py
│       ├── pv3d.py                               # PV-3D-Utils
│       ├── pv3d_plotly.py                        # Plotly-Utils
│       ├── pv3d_analysis.py                      # 3D-Analyse
│       ├── pv3d_export.py                        # 3D-Export
│       ├── pv3d_export_buttons.py                # Export-Buttons
│       ├── pv3d_optimization.py                  # Optimierung
│       ├── pv3d_performance.py                   # Performance
│       ├── pv3d_placement_handler.py             # Platzierungs-Handler
│       ├── pv3d_module_placement_ui.py           # Platzierungs-UI
│       ├── pv3d_mounting_logic.py                # Montage-Logik
│       ├── pv3d_roof_type_logic.py               # Dachtyp-Logik
│       ├── pv3d_grid_calculator.py               # Grid-Calculator
│       ├── pv3d_ui_components.py                 # UI-Komponenten
│       ├── pv3d_help.py                          # Hilfe-System
│       ├── pv3d_wow_features.py                  # WOW-Features
│       ├── pv_module_placement_system.py         # Platzierungs-System
│       ├── pv_module_placement_ui.py             # Platzierungs-UI
│       ├── pv_module_rendering_3d.py             # 3D-Rendering
│       ├── solar_animation.py                    # Solar-Animation
│       ├── shadcn_animations.py                  # shadcn-Animationen
│       ├── shadcn_chart_theme.py                 # Chart-Theme
│       ├── shadcn_responsive.py                  # Responsive
│       ├── shadcn_sidebar.py                     # Sidebar
│       ├── shadcn_migration_helpers.py           # Migration-Helpers
│       ├── pdf_visual_inject.py                  # PDF-Visual
│       ├── export_coords.py                      # Koordinaten-Export
│       ├── remove_text.py                        # Text-Entfernung
│       └── coords_raw.yaml                       # Rohe Koordinaten
│
├── 🔧 UTILS & HELPER
│   ├── utils.py                                  # Allgemeine Utils
│   ├── analysis_utils.py                         # Analyse-Utils
│   ├── analysis.py                               # Analyse-Modul
│   ├── calculation_bridge.py                     # Calculation-Bridge
│   ├── solar_calculator_bridge.py                # Solar-Calculator-Bridge
│   ├── solar_calculator_pricing_integration.py   # Pricing-Integration
│   ├── solar_calculator_pv_mounting_integration.py # Mounting-Integration
│   ├── solar_calculator_pv_mounting.py           # PV-Mounting
│   ├── services_integration.py                   # Services-Integration
│   └── doc_output.py                             # Dokumentations-Output
│
├── 👨‍💼 ADMIN-PANEL & MANAGEMENT
│   ├── admin_security.py                         # Sicherheit
│   ├── admin_user_management_ui.py               # User-Management
│   ├── admin_build_infos_ui.py                   # Build-Infos
│   ├── admin_logo_management_ui.py               # Logo-Management
│   ├── admin_logo_positions_ui.py                # Logo-Positionen
│   ├── admin_brand_logo_management_ui.py         # Brand-Logos
│   ├── admin_module_alias_mapping_ui.py          # Modul-Aliases
│   ├── admin_payment_terms_ui.py                 # Zahlungsbedingungen
│   ├── admin_pdf_settings_ui.py                  # PDF-Einstellungen
│   ├── admin_pricing_rule_ui.py                  # Pricing-Regeln
│   ├── admin_profit_margin_ui.py                 # Profit-Margins
│   ├── admin_product_database_ui.py              # Produkt-DB-UI
│   ├── admin_product_attributes_ui.py            # Produkt-Attribute
│   ├── admin_services_ui.py                      # Services-UI
│   ├── admin_price_matrix_upload.py              # Matrix-Upload
│   ├── admin_pv_mounting_ui.py                   # PV-Montage-UI
│   ├── admin_pv_mounting_tab.py                  # PV-Montage-Tab
│   ├── admin_heating_costs_config_ui.py          # Heizkosten-Config
│   ├── admin_heatpump_settings_ui.py             # Wärmepumpen-Settings
│   ├── admin_intro_settings_ui.py                # Intro-Settings
│   ├── admin_ui_effects_settings.py              # UI-Effekte
│   ├── brand_logo_db.py                          # Brand-Logo-DB
│   ├── user_management.py                        # User-Management
│   └── user_menu.py                              # User-Menü
│
├── 📊 EXCEL-INTEGRATION
│   ├── excel_manager.py                          # Excel-Manager
│   ├── excel_grid_ui.py                          # Excel-Grid-UI
│   ├── excel_integration.py                      # Excel-Integration
│   ├── excel_uploader.py                         # Excel-Uploader
│   └── 📁 excel/ (Daten-Ordner)
│
├── 📋 PAGES (Streamlit Multi-Page)
│   └── 📁 pages/
│       └── [Streamlit Page-Dateien]
│
├── 🤖 AI-AGENT & COMPANION
│   ├── agent_ui.py                               # Agent-UI
│   ├── ai_companion.py                           # AI-Companion
│   ├── voice_command.py                          # Sprach-Befehle
│   └── translate_agent_ui.py                     # Übersetzungs-Agent
│
├── 📈 SOLAR-CALCULATOR
│   ├── solar_calculator.py                       # Solar-Calculator-Haupt
│   ├── solar_calculator_shadcn.py                # shadcn-Version
│   └── simulate_solar_calculator.py              # Simulation
│
├── 🌡️ WÄRMEPUMPEN-SYSTEM
│   ├── calculations_heatpump.py                  # Berechnungen
│   ├── heatpump_pricing.py                       # Pricing
│   ├── heatpump_ui.py                            # UI
│   ├── heatpump_utils.py                         # Utils
│   ├── waermepumpen_parser.py                    # Parser
│   ├── waermepumpen_produkte_monobloc_hybrid.json # Produktdaten
│   │
│   ├── 📁 wp_implements/                         # Implementierungs-Daten
│   │   ├── 📁 angebot/
│   │   ├── 📁 excel/
│   │   └── WP_implementierung.pdf
│   │
│   └── 📁 mirror/www.heizungsdiscount24.de/waermepumpen/ # Web-Scraping-Daten
│       └── [Umfangreiche Herstellerverzeichnisse]
│
├── 📂 DATENVERZEICHNISSE
│   ├── 📁 data/
│   │   ├── app_data.db                           # Haupt-SQLite-DB
│   │   ├── 📁 product_datasheets/                # Produktdatenblätter
│   │   │   └── [Verzeichnisse 6-341 mit PDFs]
│   │   └── [Weitere Daten-Dateien]
│   │
│   ├── 📁 json/                                  # JSON-Daten
│   │   └── 1/, 2/, 3/ (mit imgs/)
│   │
│   ├── 📁 logs/                                  # Log-Dateien
│   ├── 📁 uploads/                               # Uploads
│   ├── 📁 static/css/                            # CSS-Dateien
│   ├── 📁 temp/                                  # Temp-Dateien
│   └── 📁 evaluation_results/                    # Evaluierungs-Ergebnisse
│
├── 🧪 TESTS
│   └── 📁 tests/
│       ├── [270+ Test-Dateien]
│       ├── test_crm_integration.py
│       ├── test_pdf_generation.py
│       ├── test_agent_isolation.py
│       ├── test_price_system.py
│       ├── test_3d_visualization_fixes.py
│       ├── manual_test_8_page_*.pdf
│       ├── test_integration.db
│       └── [Weitere Test-PDFs und Configs]
│
├── 🔧 TOOLS & UTILITIES
│   ├── 📁 tools/
│   │   ├── build_installer.ps1                   # Installer-Build
│   │   ├── cleanup_pdf_ui.py
│   │   ├── count_pages.py
│   │   ├── custom_dynamic_calculation.py
│   │   ├── debug_dynamic_page3.py
│   │   ├── debug_page3_check.py
│   │   ├── delete_except_keep.py
│   │   ├── import_module_attributes_from_pdf.py
│   │   ├── import_module_attributes_generic.py
│   │   ├── pv_berechnungen_50.py
│   │   ├── schema_extractor.py
│   │   ├── smoke_crm_save.py
│   │   ├── theme_generator.py
│   │   ├── trace_pdf_dependencies.py
│   │   ├── validate_theme.py
│   │   ├── repo_porter.py
│   │   ├── repo_porter_select.py
│   │   ├── run_normal_pdf.py
│   │   │
│   │   ├── 📁 _stubs/                            # Stubs für Abhängigkeiten
│   │   │   ├── components/__init__.py
│   │   │   ├── components/progress_manager.py
│   │   │   └── streamlit/__init__.py
│   │   │
│   │   ├── 📁 out_selected/                      # Output-Patches
│   │   │   └── patches/
│   │   │
│   │   └── 📁 portings/                          # Porting-System
│   │       ├── index_dst.csv
│   │       ├── index_src.csv
│   │       ├── report.json
│   │       └── patches/
│   │
│   └── 📁 nützliche tools/
│       ├── cache_leerer.py
│       └── all_py_tools/
│
├── 🔨 REPAIR & MIGRATION
│   ├── 📁 repair_pdf/                            # PDF-Reparatur-Skripte
│   │   ├── admin_panel.py
│   │   ├── analysis.py
│   │   ├── calculations.py
│   │   ├── calculations_extended.py
│   │   ├── central_pdf_system.py
│   │   ├── doc_output.py
│   │   ├── financial_tools.py
│   │   ├── multi_offer_generator.py
│   │   ├── pdf_generator.py
│   │   ├── pdf_preview.py
│   │   ├── pdf_styles.py
│   │   ├── pdf_ui.py
│   │   ├── pdf_widgets.py
│   │   └── product_db.py
│   │
│   ├── app_auto_fixer.py
│   ├── auto_repair_100.py
│   ├── repair_plan_100.py
│   ├── migrations.py
│   ├── migrate_logo_database.py
│   ├── update_tariffs.py
│   └── upload_matrix.py
│
├── 🌐 KNOWLEDGE BASE
│   └── 📁 knowledge_base/
│
├── 📚 DOKUMENTATION
│   ├── 📁 docs/
│   ├── 📁 unterkonstruktion_pv/
│   │   ├── Komponenten für PV-Montagesysteme je Dachtyp.md
│   │   ├── Komponenten für PV-Montagesysteme je Dachtyp.pdf
│   │   └── Komponenten für PV-Montagesysteme je Dachtyp.txt
│   │
│   └── [180+ Markdown-Dokumentationsdateien]:
│       ├── Probleme_zu_behandeln.md
│       ├── .github/copilot-instructions.md
│       ├── 3D_*.md
│       ├── TASK_*.md (130+ Task-Dokumentationen)
│       ├── PRICE_MATRIX_SYSTEM_COMPLETE.md
│       ├── ADMIN_*.md
│       ├── SHADCN_*.md
│       ├── PV_*.md
│       └── [Viele weitere Feature-Dokumentationen]
│
├── 🔍 ANALYSE & DEBUG
│   ├── analyse_alle_amortisationszeit_berechnungen.py
│   ├── analyse_alle_duplikate.py
│   ├── analyze_core_integration.py
│   ├── analyze_excel.py
│   ├── analyze_missing_features.py
│   ├── analyze_pricing_keys_usage.py
│   ├── ultra_deep_analysis.py
│   ├── check_imports.py
│   ├── check_product_image_details.py
│   ├── check_product_images.py
│   ├── check_solar_calculator_integration.py
│   ├── debug_*.py (20+ Debug-Skripte)
│   ├── quick_calc.py
│   ├── quick_check.py
│   └── simple_*.py (10+ Simple-Tests)
│
├── ✅ VERIFICATION & VALIDATION
│   ├── verify_*.py (35+ Verifikations-Skripte)
│   ├── verify_3d_dependencies.py
│   ├── verify_error_handling_complete.py
│   ├── verify_extended_pdf.py
│   ├── verify_german_formatting.py
│   ├── verify_hot_reload.py
│   └── [Weitere Verifikationen]
│
├── 🧹 CLEANUP & MAINTENANCE
│   ├── add_all_declarations.py
│   ├── add_plotly_separators.py
│   ├── add_test_product_images.py
│   ├── apply_german_formatting.py
│   ├── auto_replace_emojis_safe.py
│   ├── remove_all_tags.py
│   ├── remove_unwanted_manufacturers.py
│   ├── replace_all_emojis.py
│   ├── reset_protected_areas.py
│   ├── restore_placeholders_from_backup.py
│   ├── simple_emoji_replacer.py
│   ├── teilen.py
│   ├── show_carousel_improvements.py
│   ├── show_db_structure.py
│   └── clear_python_cache.py
│
├── 🏗️ BUILD & DEPLOYMENT
│   ├── bokuk2.spec                               # PyInstaller Spec
│   ├── setup.py                                  # Setup-Script
│   ├── pyproject.toml                            # Modern Python-Projekt
│   ├── 📁 dist/                                  # Build-Output
│   ├── 📁 installer_output/                      # Installer-Output
│   ├── 📁 htmlcov/                               # Coverage-Reports
│   └── 📁 wheelhouse/                            # Python Wheels
│
├── 📦 DEPENDENCIES & CONFIG
│   ├── requirements.txt                          # Main Requirements
│   ├── requirements_strict.txt                   # Strict Versions
│   ├── requirements_flexible.txt                 # Flexible Versions
│   ├── schema.json                               # JSON-Schema
│   ├── placeholders.py                           # Platzhalter-Definitionen
│   │
│   └── 📁 .streamlit/ (implizit)
│       └── config.toml                           # Streamlit-Config
│
├── 📋 REPORTS & PERFORMANCE
│   ├── 📁 reports/
│   │   ├── pylint-duplicates.txt
│   │   └── ruff.txt
│   │
│   ├── performance_metrics_*.json
│   ├── performance_results_*.json
│   └── SYSTEM_CHECK_REPORT.md
│
├── 🗂️ SONSTIGE ORDNER
│   ├── 📁 KOPIE/
│   ├── 📁 venv_complete/                         # Virtual Environment
│   ├── 📁 vive/
│   ├── 📁 notwendig oder nicht/
│   │   ├── need or not/
│   │   └── zu implementieren/
│   └── 📁 .github/
│       └── copilot-instructions.md               # GitHub Copilot Config
│
└── 🔢 VERSIONIERTE ORDNER (Legacy/Backup?)
    ├── 0.9.0/
    ├── 1.0.0/
    ├── 1.28.0/
    ├── 2.0.0/
    ├── 3.10.0/
    ├── 4.5.0/
    ├── 13.5.0/
    └── 23.0.0/

═══════════════════════════════════════════════════════════════════
ZUSAMMENFASSUNG DER HAUPTMODULE
═══════════════════════════════════════════════════════════════════

📌 EINSTIEGSPUNKTE
   • gui.py - Haupt-Streamlit-App
   • admin_panel.py - Admin-Interface

📌 KERNSYSTEME (7 Hauptbereiche)
   1. PDF-Generierung (pdf_generator.py + pdf_template_engine/)
   2. Preisberechnung (pricing/ + price_matrix_*.py)
   3. CRM (crm.py + crm_*.py)
   4. Produktdatenbank (product_db.py + heatpump_database.py)
   5. 3D-Visualisierung (pv3d.py + utils/pv3d_*.py)
   6. Berechnungen (calculations*.py)
   7. Theming (theming/)

📌 DATENBANKSTRUKTUREN
   • SQLite: data/app_data.db
   • Tabellen: customers, projects, products, price_matrices, 
               contracts, warranties, crm_leads, customer_documents

📌 UNTERSTÜTZTE FEATURES
   • Multi-Firma PDF-Generierung (6 Firmen × 8 Seiten)
   • Produkt-Rotation & Preismodifikation
   • 3D-PV-Modul-Platzierung (Plotly/PyVista)
   • Wärmepumpen-Konfiguration
   • shadcn-ui Integration
   • CRM mit Vertrags-/Garantieverwaltung
   • Excel-Import/Export
   • AI-Agent & Voice-Commands
   • Hot-Reload & Dev-Mode
   • Umfangreiches Theme-System (17 Themes)

📌 TESTING
   • 270+ Test-Dateien
   • Unit, Integration, End-to-End Tests
   • PDF-Validierungstests
   • Performance-Tests

═══════════════════════════════════════════════════════════════════
GESAMT-STATISTIK
═══════════════════════════════════════════════════════════════════
Python-Dateien (geschätzt): ~600 Dateien
Dokumentation (MD): ~180 Dateien
PDF-Templates: 56 PDFs (8 Standard + 48 Multi-Firma)
YAML-Koordinaten: 56 Dateien (8 Seiten × 7 Firmen)
Test-Dateien: 270+ Dateien
Produktdatenblätter: ~200 Verzeichnisse
Wärmepumpen-Daten: ~1000+ HTML-Scraping-Seiten