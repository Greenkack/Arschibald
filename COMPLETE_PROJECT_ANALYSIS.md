# 🔍 VOLLSTÄNDIGE PROJEKT-ANALYSE

## Bokuk2 - Kopie - Alle Python-Dateien

**Analysiert am:** 10. November 2025  
**Gesamt Python-Dateien:** 1.112  
**Produktive Dateien (ohne Test/Debug/Demo):** ~200

---

## 📊 KATEGORISIERUNG

### 🎯 **HAUPTMODULE** (in gui.py integriert)

Diese Module werden dynamisch in `gui.py` geladen:

| Modul | Datei | Status | Funktion |
|-------|-------|--------|----------|
| ✅ `locales_module` | `locales.py` | AKTIV | Sprach-/Textdateien |
| ✅ `database_module` | `database.py` | AKTIV | Datenbank-Core |
| ✅ `product_db_module` | `product_db.py` | AKTIV | Produkt-Datenbank |
| ✅ `data_input_module` | `data_input.py` | AKTIV | Dateneingabe |
| ✅ `calculations_module` | `calculations.py` | AKTIV | Berechnungen |
| ✅ `analysis_module` | `analysis.py` | AKTIV | Analysen & Charts |
| ✅ `doc_output_module` | `doc_output.py` | AKTIV | PDF-Ausgabe |
| ✅ `admin_panel_module` | `admin_panel.py` | AKTIV | Admin-Panel |
| ✅ `crm_module` | `crm.py` | AKTIV | CRM-System |
| ✅ `quick_calc_module` | `quick_calc.py` | AKTIV | A.G.E.N.T. |
| ✅ `solar_calculator_module` | `solar_calculator.py` | AKTIV | Solar-Calculator |
| ✅ `heatpump_ui_module` | `heatpump_ui.py` | AKTIV | Wärmepumpen-UI |
| ✅ `crm_dashboard_ui_module` | `crm_dashboard_ui.py` | AKTIV | CRM Dashboard |
| ✅ `crm_pipeline_ui_module` | `crm_pipeline_ui.py` | AKTIV | CRM Pipeline |
| ✅ `crm_calendar_ui_module` | `crm_calendar_ui.py` | AKTIV | CRM Kalender |
| ✅ `ai_companion_module` | `ai_companion.py` | AKTIV | KI-Assistent |
| ✅ `pdf_preview_module` | `pdf_preview.py` | AKTIV | PDF-Vorschau |
| ✅ `multi_offer_module` | `multi_offer_generator.py` | AKTIV | Multi-Angebote |

---

## 🟢 **CORE-MODULE** (direkt importiert)

| Datei | Import in | Status | Zweck |
|-------|-----------|--------|-------|
| ✅ `core_integration.py` | `gui.py` | AKTIV | Core-System-Integration |
| ✅ `theme_manager.py` | `gui.py` | AKTIV | Theme-Verwaltung |
| ✅ `ui_state_manager.py` | `gui.py` | AKTIV | UI-Status |
| ✅ `emoji_toggle.py` | `gui.py`, `solar_calculator.py` | AKTIV | Emoji-Support |
| ✅ `live_preview_helpers.py` | `gui.py` | AKTIV | Live-Vorschau |
| ✅ `intro_screen.py` | Startup | AKTIV | Intro-Bildschirm |

---

## 📦 **BERECHNUNGS-MODULE**

| Datei | Status | Integration | Zweck |
|-------|--------|-------------|-------|
| ✅ `calculations.py` | AKTIV | gui.py | Haupt-Berechnungen |
| ✅ `calculations_extended.py` | AKTIV | pdf_generator.py | Erweiterte Berechnungen |
| ✅ `calculations_heatpump.py` | AKTIV | heatpump_ui.py | Wärmepumpen-Calc |
| ✅ `calculations_heatpump_temp.py` | AKTIV | heatpump_ui.py | WP-Temperaturen |
| ✅ `pv_calculations_core.py` | AKTIV | solar_calculator.py | PV-Kern-Berechnungen |
| ✅ `pv_mounting_calculations.py` | AKTIV | solar_calculator.py | PV-Montage-Calc |
| ✅ `financial_calculations.py` | AKTIV | solar_calculator.py | Finanzen |
| ⚠️ `calculation_bridge.py` | TEILWEISE | - | Bridge-Modul |
| ⚠️ `live_calculation_engine.py` | TEILWEISE | - | Live-Calc-Engine |

---

## 📊 **ADMIN-MODULE**

| Datei | Status | UI-Integration |
|-------|--------|----------------|
| ✅ `admin_panel.py` | AKTIV | gui.py → Hauptmodul |
| ✅ `admin_security.py` | AKTIV | admin_panel.py |
| ✅ `admin_brand_logo_management_ui.py` | AKTIV | admin_panel.py |
| ✅ `admin_build_infos_ui.py` | AKTIV | admin_panel.py |
| ✅ `admin_core_status_ui.py` | AKTIV | admin_panel.py |
| ✅ `admin_core_status_extended_ui.py` | AKTIV | admin_panel.py |
| ✅ `admin_heating_costs_config_ui.py` | AKTIV | admin_panel.py |
| ✅ `admin_heatpump_settings_ui.py` | AKTIV | admin_panel.py |
| ✅ `admin_intro_settings_ui.py` | AKTIV | admin_panel.py |
| ⚠️ `admin_intro_settings_ui_NEW.py` | DUPLICATE | Neue Version? |
| ✅ `admin_logo_management_ui.py` | AKTIV | admin_panel.py |
| ✅ `admin_logo_positions_ui.py` | AKTIV | admin_panel.py |
| ✅ `admin_module_alias_mapping_ui.py` | AKTIV | admin_panel.py |
| ✅ `admin_payment_terms_ui.py` | AKTIV | admin_panel.py |
| ✅ `admin_pdf_settings_ui.py` | AKTIV | admin_panel.py |
| ✅ `admin_pricing_rule_ui.py` | AKTIV | admin_panel.py |
| ✅ `admin_product_attributes_ui.py` | AKTIV | admin_panel.py |
| ✅ `admin_product_database_ui.py` | AKTIV | admin_panel.py |
| ✅ `admin_profit_margin_ui.py` | AKTIV | admin_panel.py |
| ✅ `admin_pv_mounting_ui.py` | AKTIV | admin_panel.py |
| ⚠️ `admin_pv_mounting_tab.py` | TEILWEISE | Alte Version? |
| ⚠️ `admin_pv_mounting_tab_v2.py` | TEILWEISE | Neue Version? |
| ✅ `admin_services_ui.py` | AKTIV | admin_panel.py |
| ✅ `admin_ui_effects_settings.py` | AKTIV | admin_panel.py |
| ✅ `admin_user_management_ui.py` | AKTIV | admin_panel.py |

---

## 📄 **PDF-MODULE**

| Datei | Status | Integration |
|-------|--------|-------------|
| ✅ `pdf_generator.py` | AKTIV | doc_output.py |
| ✅ `pdf_templates.py` | AKTIV | pdf_generator.py |
| ✅ `pdf_styles.py` | AKTIV | pdf_generator.py |
| ✅ `extended_pdf_generator.py` | AKTIV | doc_output.py |
| ✅ `pdf_chart_renderer.py` | AKTIV | pdf_generator.py |
| ✅ `pdf_helpers.py` | AKTIV | pdf_generator.py |
| ✅ `pdf_pricing_integration.py` | AKTIV | pdf_generator.py |
| ✅ `pdf_services_integration.py` | AKTIV | pdf_generator.py |
| ✅ `pdf_payment_integration.py` | AKTIV | pdf_generator.py |
| ✅ `pdf_payment_summary.py` | AKTIV | pdf_generator.py |
| ✅ `pdf_widgets.py` | AKTIV | pdf_generator.py |
| ✅ `pdf_ui.py` | AKTIV | doc_output.py |
| ⚠️ `pdf_atomizer.py` | TEILWEISE | PDF-Atomisierung |
| ⚠️ `pdf_chart_generator_protected.py` | TEILWEISE | Protected Charts |
| ⚠️ `pdf_dynamic_tariff_section.py` | TEILWEISE | Dynamische Tarife |
| ⚠️ `pdf_erstellen_komplett.py` | TEILWEISE | Alternativer Generator? |
| ⚠️ `pdf_generation_bridge.py` | TEILWEISE | Bridge-Modul |
| ⚠️ `pdf_generator_cli.py` | CLI-TOOL | Command-Line |
| ⚠️ `pdf_generator_patch.py` | PATCH | Hotfix-Modul |
| ⚠️ `pdf_integration_helper.py` | HELPER | Helper-Modul |
| ⚠️ `pdf_migration.py` | MIGRATION | Daten-Migration |
| ⚠️ `pdf_page_protection.py` | TEILWEISE | Seiten-Schutz |
| ⚠️ `pdf_pricing_templates.py` | TEILWEISE | Preis-Templates |
| ⚠️ `pdf_recover.py` | TOOL | Recovery-Tool |
| ⚠️ `pdf_with_payment.py` | TEILWEISE | Payment-Integration |
| ⚠️ `pdf_zu_markdown.py` | TOOL | PDF→Markdown |
| ⚠️ `pdf_zu_png.py` | TOOL | PDF→PNG |

---

## 💰 **PRICING-MODULE**

| Datei | Status | Integration |
|-------|--------|-------------|
| ✅ `dynamic_pricing_engine.py` | AKTIV | solar_calculator.py |
| ✅ `price_matrix_lookup.py` | AKTIV | solar_calculator.py |
| ✅ `price_matrix_store.py` | AKTIV | admin_panel.py |
| ✅ `price_matrix_validation.py` | AKTIV | admin_panel.py |
| ✅ `price_modification_engine.py` | AKTIV | solar_calculator.py |
| ✅ `solar_calculator_pricing_integration.py` | AKTIV | solar_calculator.py |
| ⚠️ `price_matrix_examples.py` | BEISPIELE | Dokumentation |
| ⚠️ `matrix_extras_calculator.py` | TEILWEISE | Extras-Calc |
| ⚠️ `matrix_loader.py` | TEILWEISE | Matrix-Loader |

---

## 🗄️ **DATENBANK-MODULE**

| Datei | Status | Integration |
|-------|--------|-------------|
| ✅ `database.py` | AKTIV | gui.py |
| ✅ `product_db.py` | AKTIV | gui.py |
| ✅ `pv_mounting_database.py` | AKTIV | solar_calculator.py |
| ✅ `heatpump_products_database.py` | AKTIV | heatpump_ui.py |
| ✅ `brand_logo_db.py` | AKTIV | admin_panel.py |
| ⚠️ `database_bridge.py` | TEILWEISE | Bridge-Modul |
| ⚠️ `database_clean.py` | TOOL | DB-Cleanup |
| ⚠️ `database_pricing_migration.py` | MIGRATION | Preis-Migration |
| ⚠️ `database_backup.py` | TOOL | Backup-Tool |
| ⚠️ `pv_mounting_db_bridge.py` | TEILWEISE | PV-Bridge |
| ⚠️ `init_database.py` | SETUP | DB-Init |
| ⚠️ `optimize_database.py` | TOOL | DB-Optimierung |

---

## 📱 **UI-MODULE**

| Datei | Status | Integration |
|-------|--------|-------------|
| ✅ `ui_state_manager.py` | AKTIV | gui.py |
| ✅ `ui_chart_helpers.py` | AKTIV | analysis.py |
| ✅ `ui_effects_library.py` | AKTIV | gui.py |
| ✅ `ui_settings_handler.py` | AKTIV | admin_panel.py |
| ✅ `carousel_ui_utils.py` | AKTIV | admin_panel.py |
| ⚠️ `carousel_ui_utils_native.py` | ALT | Native Version |
| ✅ `carousel_preview.py` | AKTIV | admin_panel.py |
| ✅ `excel_grid_ui.py` | AKTIV | admin_panel.py |
| ✅ `css_template_manager.py` | AKTIV | gui.py |
| ⚠️ `inject_css.py` | TEILWEISE | CSS-Injection |
| ⚠️ `temp_slider_checkbox_css.py` | TEMP | Temporäres CSS |

---

## 🎨 **CHART & VISUALISIERUNG**

| Datei | Status | Integration |
|-------|--------|-------------|
| ✅ `advanced_charts.py` | AKTIV | analysis.py |
| ✅ `chart_styling.py` | AKTIV | analysis.py |
| ✅ `auto_chart_generator.py` | AKTIV | analysis.py |
| ✅ `pv_visuals.py` | AKTIV | gui.py |
| ✅ `solar_3d_view_module.py` | AKTIV | solar_calculator.py |
| ⚠️ `solar_3d_view_enhanced.py` | TEILWEISE | Enhanced Version |
| ⚠️ `chart_styling_improvements.py` | TEILWEISE | Verbesserungen |
| ⚠️ `advanced_features.py` | TEILWEISE | Erweiterte Features |

---

## 🔧 **UTILITIES & HELPERS**

| Datei | Status | Integration |
|-------|--------|-------------|
| ✅ `utils.py` | AKTIV | Diverse Module |
| ✅ `german_formatting.py` | AKTIV | Diverse Module |
| ✅ `analysis_utils.py` | AKTIV | analysis.py |
| ✅ `session_widgets.py` | AKTIV | gui.py |
| ✅ `robustness_core.py` | AKTIV | gui.py |
| ✅ `performance_handler.py` | AKTIV | gui.py |
| ⚠️ `apply_german_formatting.py` | TOOL | Formatierungs-Tool |
| ⚠️ `generate_universal_hover_template.py` | TOOL | Template-Generator |

---

## 🏢 **CRM-MODULE**

| Datei | Status | Integration |
|-------|--------|-------------|
| ✅ `crm.py` | AKTIV | gui.py |
| ✅ `crm_dashboard_ui.py` | AKTIV | gui.py |
| ✅ `crm_pipeline_ui.py` | AKTIV | gui.py |
| ✅ `crm_calendar_ui.py` | AKTIV | gui.py |

---

## 🌡️ **WÄRMEPUMPEN-MODULE**

| Datei | Status | Integration |
|-------|--------|-------------|
| ✅ `heatpump_ui.py` | AKTIV | gui.py |
| ✅ `heatpump_pricing.py` | AKTIV | heatpump_ui.py |
| ✅ `heatpump_products_database.py` | AKTIV | heatpump_ui.py |
| ✅ `heatpump_advanced_calculations.py` | AKTIV | heatpump_ui.py |
| ✅ `heatpump_advanced_charts.py` | AKTIV | heatpump_ui.py |
| ✅ `heatpump_dynamic_tariff.py` | AKTIV | heatpump_ui.py |
| ⚠️ `heatpump_advanced_features.py` | TEILWEISE | Erweiterte Features |
| ⚠️ `heatpump_advanced_features_part2.py` | TEILWEISE | Features Teil 2 |
| ⚠️ `heatpump_advanced_features_part3.py` | TEILWEISE | Features Teil 3 |
| ⚠️ `heatpump_dynamic_tariff_charts.py` | TEILWEISE | Dynamische Tarife |

---

## 🔨 **TOOLS & MIGRATION**

| Datei | Typ | Zweck |
|-------|-----|-------|
| ⚠️ `migrate_logo_database.py` | MIGRATION | Logo-DB-Migration |
| ⚠️ `migrate_profile_image.py` | MIGRATION | Profil-Bild-Migration |
| ⚠️ `migrate_super_admin.py` | MIGRATION | Admin-Migration |
| ⚠️ `migrate_widgets_bulk.py` | MIGRATION | Widget-Migration |
| ⚠️ `create_super_admin.py` | SETUP | Admin erstellen |
| ⚠️ `seed_pv_database.py` | SETUP | PV-DB-Seed |
| ⚠️ `seed_pv_database_extended.py` | SETUP | Extended Seed |
| ⚠️ `clean_duplicates.py` | TOOL | Duplikate entfernen |
| ⚠️ `clean_unicode_emojis.py` | TOOL | Emoji-Cleanup |
| ⚠️ `cleanup_session_state.py` | TOOL | Session-Cleanup |
| ⚠️ `clear_python_cache.py` | TOOL | Cache-Clear |
| ⚠️ `force_cleanup_session_state.py` | TOOL | Force-Cleanup |
| ⚠️ `update_tariffs.py` | TOOL | Tarif-Update |
| ⚠️ `upload_matrix.py` | TOOL | Matrix-Upload |

---

## 📋 **MULTI-OFFER-MODULE**

| Datei | Status | Integration |
|-------|--------|-------------|
| ✅ `multi_offer_generator.py` | AKTIV | gui.py |
| ⚠️ `multi_offer_generator_new.py` | NEUE VERSION | Alternative? |
| ⚠️ `multi_offer_generator_old.py` | ALTE VERSION | Backup? |
| ⚠️ `multi_offer_generator_cli.py` | CLI | Command-Line |
| ⚠️ `multi_pdf_integration.py` | TEILWEISE | PDF-Integration |
| ⚠️ `multi_pdf_integration_complete.py` | TEILWEISE | Complete Version |

---

## ❓ **UNKLARE MODULE** (müssen geprüft werden)

| Datei | Status | Empfehlung |
|-------|--------|------------|
| ✅ `info_platform.py` | AKTIV | In gui.py Z. 2909 (render_info_platform) |
| ✅ `options.py` | AKTIV | In gui.py Z. 2916 (render_options) |
| ❓ `map_integration.py` | MODUL EXISTIERT | Prüfen & integrieren |
| ❓ `scenario_manager.py` | MODUL EXISTIERT | Prüfen & integrieren |
| ❓ `voice_command.py` | DRAWER-ACTION | In gui.py Z. 1509 (drawer) |
| ❓ `user_menu.py` | MODUL EXISTIERT | render_profile_editor in gui.py Z. 2099 |
| ❓ `BUG_5_FIX_COMPLETE.py` | Bug-Fix-Code | Prüfen & integrieren |
| ❓ `FINAL_FIX_VERIFICATION.py` | Verifikation | Prüfen |
| ❓ `final_pricing_calculation_exact.py` | Pricing-Calc | Integrieren? |
| ❓ `final_pricing_calculation_with_keys.py` | Pricing-Calc | Integrieren? |
| ❓ `final_test_main_files.py` | Test | Ignorieren |
| ❓ `FORMATIERUNG_REFERENZ.py` | Referenz | Dokumentation |
| ❓ `MASTER_FIX.py` | Master-Fix | Prüfen |
| ❓ `PHASE_3_USAGE_EXAMPLE.py` | Beispiel | Dokumentation |
| ❓ `PDF_FIXES_TEST.py` | Test | Ignorieren |
| ❓ `complete_export.py` | Export-Tool | Prüfen |
| ❓ `drawer_actions.py` | UI-Actions | Prüfen |
| ❓ `enhanced_product_management_ui.py` | Enhanced UI | Integrieren? |
| ❓ `excel_eval.py` | Excel-Eval | Prüfen |
| ❓ `financing_page_generator_enhanced.py` | PDF-Financing | Integrieren? |
| ❓ `indent_3d_view.py` | Indent-Tool | Ignorieren |
| ❓ `info_platform.py` | Info-Plattform | Prüfen |
| ❓ `make_all_classes_serializable.py` | Serialization | Prüfen |
| ❓ `map_integration.py` | Karten-Integration | Integrieren? |
| ❓ `options.py` | Optionen | Prüfen |
| ❓ `payment_terms.py` | Zahlungsbedingungen | Integrieren? |
| ❓ `payment_terms_ui.py` | Payment-UI | Integrieren? |
| ❓ `product_attributes.py` | Produkt-Attribute | Integrieren? |
| ❓ `product_rotation_engine.py` | Produkt-Rotation | Integrieren? |
| ❓ `reset_protected_areas.py` | Reset-Tool | Tool |
| ❓ `restore_placeholders_from_backup.py` | Restore-Tool | Tool |
| ❓ `run_2d_tests.py` | Test | Ignorieren |
| ❓ `scenario_manager.py` | Szenarien | Integrieren? |
| ❓ `service_display_config_ui.py` | Service-Config | Integrieren? |
| ❓ `services_integration.py` | Services | Integrieren? |
| ❓ `setup.py` | Setup | Setup-Datei |
| ❓ `show_carousel_improvements.py` | Show-Tool | Demo |
| ❓ `show_db_structure.py` | Show-Tool | Tool |
| ❓ `simulate_solar_calculator.py` | Simulation | Test |
| ❓ `solar_calculator_bridge.py` | Bridge | Prüfen |
| ❓ `solar_calculator_pv_mounting.py` | PV-Mounting | Integrieren? |
| ❓ `solar_calculator_pv_mounting_integration.py` | Integration | Integrieren? |
| ❓ `special_products.py` | Spezial-Produkte | Integrieren? |
| ❓ `storage_model_resolver.py` | Storage-Resolver | Integrieren? |
| ❓ `storage_resolver_demo.py` | Demo | Ignorieren |
| ❓ `teilen.py` | Teilen-Funktion | Integrieren? |
| ❓ `translate_agent_ui.py` | Übersetzungs-UI | Integrieren? |
| ❓ `user_management.py` | User-Management | Integrieren? |
| ❓ `user_menu.py` | User-Menü | Integrieren? |
| ❓ `voice_command.py` | Sprach-Steuerung | Integrieren? |

---

## 📊 ZUSAMMENFASSUNG

### Status-Übersicht

- ✅ **VOLLSTÄNDIG AKTIV:** ~80 Module (40%)
- ⚠️ **TEILWEISE AKTIV:** ~60 Module (30%)
- ❓ **UNKLAR/ZU PRÜFEN:** ~60 Module (30%)

### Nächste Schritte

1. ❓-Module einzeln analysieren
2. ⚠️-Module zu 100% integrieren
3. Duplikate entfernen (z.B. `_old`, `_new` Versionen)
4. Tools dokumentieren

**FAZIT:** Die Kern-Funktionalität ist vollständig implementiert. Es gibt viele Hilfs-Module und alternative Versionen die geprüft werden müssen.
