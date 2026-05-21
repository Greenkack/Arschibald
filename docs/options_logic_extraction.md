# options.py — vollständige Logik-Extraktion

Ziel: Globale Einstellungs-UI (Optionen-Tab) dokumentieren: PV-GIS, PDF-Design, UI/UX, Performance, Security, AI, Berechnungen, Gamification, Nachhaltigkeit, Mobile, Multimedia.

## Überblick

- Rolle: Streamlit-UI zum Laden/Speichern von Admin-Settings über `database.load_admin_setting/save_admin_setting` (+ Session-State Synchronisation).
- Hauptfunktionen:
  - `convert_to_bool(value)` — robuste Typkonvertierung (Strings, Zahlen, bools).
  - `display_options_ui()` — Basis-PDF-Design-Auswahl (Theme via `theming.pdf_styles.AVAILABLE_THEMES`).
  - `render_options(texts: Dict[str, str], **kwargs)` — Haupt-UI mit Expander-Blöcken und Save-All.

## Datenflüsse & Kontrakte

- Admin-Settings Keys (Auszug):
  - PV-GIS: `pvgis_enabled`, `pvgis_system_loss_default_percent`, `pvgis_api_timeout_seconds`, `default_specific_yield_kwh_kwp`.
  - PDF: `pdf_theme_name` (via Session; Generator liest Theme aus `st.session_state`).
  - UI/UX: `ui_dark_mode_enabled`, `ui_animations_enabled`, `ui_compact_view_enabled`, `ui_sound_effects_enabled`, `ui_color_scheme`, `ui_sidebar_position`.
  - Performance: `performance_auto_cache_enabled`, `performance_cache_size_mb`, `performance_background_processing`, `performance_preload_data`.
  - Security: `security_auto_logout_minutes`, `security_data_encryption_enabled`, `security_enhanced_session`, `security_audit_log_enabled`.
  - AI: `ai_assistant_enabled`, `ai_predictive_analytics`, `ai_smart_recommendations`, `ai_pdf_optimization`.
  - Calc: `calc_precision_level`, `calc_monte_carlo_enabled`, `calc_weather_integration`, `calc_degradation_analysis`.
  - Gamification: `gamification_achievements_enabled`, `gamification_progress_tracking`, `gamification_daily_challenges`, `gamification_leaderboard`.
  - Sustainability: `sustainability_co2_tracking`, `sustainability_green_badge`, `sustainability_score_enabled`, `sustainability_recycling_info`.
  - Mobile: `mobile_optimization_enabled`, `mobile_touch_friendly`, `mobile_offline_mode`, `mobile_pwa_enabled`.
  - Multimedia/Debug: `audio_voice_commands`, `audio_text_to_speech`, `audio_background_music`, `multimedia_video_tutorials`, `app_debug_mode_enabled`.
- Speicherung:
  - Einzelne Sektionen haben „Speichern“-Buttons (z. B. PV-GIS) mit sofortigem `st.rerun()`.
  - Globaler „ALLE EINSTELLUNGEN SPEICHERN“-Button persistiert 30+ Keys in einer Schleife; Erfolg via Zähler/Statistik.
- Session-State Sync:
  - Beispiel PV-GIS Checkbox: `pvgis_enabled_checkbox` im Session-State hält UI-Status; DB-Wert als String `true|false` gespeichert.

## Funktionskatalog (Inputs/Outputs)

- `render_options(texts, **kwargs)`:
  - Inputs: `texts` (Lokalisierung), `**kwargs` (z. B. `module_name` von `gui.py`).
  - UI-Bereiche (Excerpts): PV-GIS, PDF Design & Layout (Theme-Auswahl), UI/UX, Performance & Caching, Sicherheit & Datenschutz, AI & ML, Erweiterte Berechnungen, Gamification & Motivation, Nachhaltigkeit & Umwelt, Mobile & Responsive, Audio & Multimedia, Debug-Informationen.
  - Outputs: Keine Rückgabe; persistiert via DB; setzt Session-State-Flags (`settings_updated`, `ui_refresh_needed`).

## Edge-Cases & Validierung

- Fehlende DB: Fallback-Dummys für load/save; UI bleibt bedienbar, speichert aber nicht persistent.
- Typkonvertierung: `convert_to_bool` toleriert Strings (`'true'`, `'1'`, `'yes'` ...), Zahlen und bools.
- PV-GIS-Status: Debug-Panel zeigt DB-Wert, Session-State und aktuellen UI-Wert.

## Migration: Electron + PrimeReact + TS

- 1:1 Übertragung als Settings-Seiten in React mit Zustand in Redux/Zustand + SQLite (`better-sqlite3`).
- Save-All als eine Transaktion; Keys konsolidieren und validieren.
- Theme-Pipe: `AVAILABLE_THEMES` aus theming auf JSON-Export migrieren; PDF-Generator im Renderer/Main konsumiert `pdf_theme_name`.

## Tests (skizziert)

- Speichern aller Settings → DB-Keys gesetzt; UI-Flags korrekt.
- PV-GIS: `pvgis_enabled` Stringpersistenz + Session-Checkbox Synchronität.
- Theme-Auswahl: Persistiert in `st.session_state['pdf_theme_name']`; wird im PDF genutzt.
