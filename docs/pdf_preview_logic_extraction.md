# pdf_preview.py — vollständige Logik-Extraktion

Ziel: PDF-Live-Vorschau beschreiben: Preview-Engine mit Cache, Umwandlung PDF→Bilder (PyMuPDF), Anzeige in verschiedenen Modi, Download.

## Überblick

- Rolle: Streamlit-Frontend für Vorschau der generierten Angebote; nutzt `pdf_generator.generate_offer_pdf_with_main_templates`.
- Klassen/Funktionen:
  - `PDFPreviewEngine` mit `generate_preview_pdf(...)` (Cache + Generator-Aufruf), `_create_cache_key(...)`, `pdf_to_images(pdf_bytes, max_pages)`.
  - `render_pdf_preview_interface(project_data, analysis_results, company_info, texts, load_admin_setting_func, save_admin_setting_func, list_products_func, get_product_by_id_func, db_list_company_documents_func, active_company_id)`
  - `create_preview_thumbnail(pdf_bytes, page_num=0, size=(200,280))`
- Externe Abhängigkeiten: `reportlab` (optional), `PIL.Image`, `fitz` (PyMuPDF) für PDF→PNG.

## Datenflüsse & Kontrakte

- Engine-Input für PDF-Erzeugung: identisch zu `pdf_ui`/`pdf_generator`-Kontrakt — `project_data`, `analysis_results`, `company_info`, `inclusion_options`, `texts`, plus optionale Felder (`company_logo_base64`, Vorlagen-Texte, Sections, Admin-Funktionen, active_company_id).
- Cache-Key: einfacher String aus Kundennamen, Modulanzahl und Optionsflags; kann für Kollisionen erweitert/gehärtet werden.
- Output: `bytes` (PDF) → via `pdf_to_images` in `Image`-Liste für Anzeige.

## UI-Bedienkonzept

- Spaltenlayout: Links Optionen, rechts Vorschau.
- Vorschau-Modi: „Schnellvorschau“ (erste 3 Seiten als Bilder), „Vollständige Vorschau“ (iframe-Embed), „Seitenweise“ (Navigation, Zoom, Anmerkungen-Flag).
- Auto-Update (Stub): konfigurierbare Wartezeit; aktuell kein Timer-Thread.
- Download-Button für aktuelle Vorschau-PDF.

## Edge-Cases

- Fehlende Dependencies (PyMuPDF) → Meldung + Abbruch.
- Fehler im Generator → Anzeige und None-Rückgabe.
- Großes PDF → `max_pages` begrenzen; `preview_dpi` steuert Qualität/Performance.

## Migration: Electron + TypeScript

- Renderer-Komponente „PDFPreview“:
  - Generierung: IPC-Call an Main (Python/TS) und Rückgabe als `ArrayBuffer`.
  - Preview: `pdf.js` zum Rendern & Seiten-Navigation, Zoom, Thumbnails.
  - Caching: Key aus Offer-Hash (z. B. SHA-1 der Inputs) + LRU-Cache.

## Tests (skizziert)

- Happy Path: gültige Inputs → PDF bytes → 1–3 Vorschau-Bilder.
- Seitenweise Modus: Navigation 1→N und zurück, Zoom 50–200%.
- Fehlende PyMuPDF: UI weist auf „pip install pymupdf“ hin.
