# pdf_styles.py — Logik-Extraktion

Kurzüberblick: Zentrale Styles und ein erweitertes Theme-/Visualisierungs-System für die PDF-Erstellung. Enthält ReportLab-Absatz- und Tabellenstile, Farbpaletten, sowie UI-gestützte Theme-/Chart-Features (Streamlit) inkl. Export/Import von Theme-Definitionen.

## Module, Klassen und Hauptfunktionen

- Basiskonstanten
  - FONT_FAMILY_NORMAL/BOLD/ITALIC: ReportLab-Schriftfamilien (Helvetica-Varianten).
  - DEFAULT_*_COLOR_HEX: Standardfarbwerte.

- get_color_palette(primary_hex, secondary_hex, text_hex, separator_hex) -> Dict[str, reportlab.lib.colors.Color]
  - Aufgabe: Wandelt HEX in ReportLab-Farben und ergänzt white/black/grey/darkgrey.
  - Output-Keys: primary, secondary, text, separator, white, black, grey, darkgrey.

- get_pdf_stylesheet(color_palette) -> StyleSheet1
  - Aufgabe: Erstellt ein ReportLab-StyleSheet mit ParagraphStyles.
  - Enthält u. a.: Normal, HeaderFooterText, OfferMainTitle, SectionTitle, SubSectionTitle, TableText/Number/Header etc.
  - Kontrakt: color_palette muss alle in get_color_palette genannten Keys enthalten.

- Tabellenstile (ReportLab TableStyle)
  - get_base_table_style(color_palette)
  - get_data_table_style(color_palette)
  - get_product_table_style(color_palette)
  - get_main_product_table_style()
  - Aufgabe: Konsistente Tabellenformatierung (Text-/Hintergrundfarben, Paddings, Grid).

- Dataclass ColorScheme
  - Felder: primary, secondary, accent, background, text, success, warning, error (alle HEX-Strings).
  - to_dict() -> Dict[str, str]: Rückgabe als JSON-taugliche Map.

- Klasse PDFVisualEnhancer
  - chart_themes: Matplotlib/Seaborn-Stile (modern/elegant/eco/vibrant) inkl. Farbreihen und Schriftfamilie.
  - shape_library: Helfer zur Generierung von dekorativen Formen (rounded_rect, hexagon, circle, diamond, arrow) für Diagramme/Visuals.
  - create_enhanced_chart(chart_type, data, theme='modern', size=(10, 6), title?, **kwargs) -> bytes
    - Unterstützte chart_type: monthly_generation_enhanced, cost_breakdown_3d (3D-artiges Pie), amortization_timeline, energy_flow (Sankey-ähnlich), roi_dashboard (Multi-Panel).
    - Rückgabe: PNG-Bytes (matplotlib savefig), DPI 300.
    - Datenkontrakte (Auswahl):
      - monthly_generation_enhanced: data.months (1..12), generation[], consumption[]
      - cost_breakdown_3d: data.categories[], data.values[]
      - amortization_timeline: data.years[], data.cumulative_savings[], data.investment (float)
      - energy_flow: Anteile pv_to_battery/home/grid, battery_to_home, grid_to_home (Prozentwerte)
      - roi_dashboard: roi_percent, co2_saved, autarkie, yearly_savings[]
  - create_custom_background(size: (w,h), pattern='gradient'|'dots'|'lines'|'hexagon', colors?, opacity=0.1) -> PIL.Image
  - Private Helpers: `create_*` (pro Chart), `add_gradient_to_bar`, `draw_*` (Formen), `create_*` UI-Elemente.
    - Tabs: Diagramme (chart_style + erweiterte Settings), Layout (Ränder/Abstände), Farben (Palette-Generator via `generate_color_palette`), Effekte (watermark/page_numbers etc.).
  - Tabs: Diagramme (chart_style + erweiterte Settings), Layout (Ränder/Abstände), Farben (Palette-Generator via \_generate\_color\_palette), Effekte (watermark/page_numbers etc.).
    - Speichert Anpassungen in st.session_state.pdf_theme_settings.{chart_customizations, layout_customizations, effects}.
  - _generate_color_palette(base_color: HEX) -> List[HEX]
    - Monochrome Variationen in HSV-Raum.
  - _show_theme_preview(theme_key)
    - Platzhalter: zeigt Info „Theme-Vorschau wird generiert…“.
  - create_custom_theme(name, base_theme?) -> theme_key
    - Legt neues Custom-Theme an und speichert es in st.session_state.custom_themes.

- render_pdf_visual_enhancer(texts)
  - Streamlit-UI für den Visual Enhancer (Tabs: Diagramme, Hintergründe, Formen, Layouts). Demos und Downloads.

- render_pdf_theme_manager(texts)
  - Streamlit-UI: Tabs „Themes“, „Visualisierungen“, „Verwaltung“.
  - Verwaltung/Export: Exportiert aktuelles Theme inkl. Einstellungen und timestamp (datetime.now). Hinweis: Der Code nutzt datetime.now(), stellt aber keinen eindeutigen Import in diesem Modul-Snippet sicher; bitte prüfen/ergänzen.
  - Verwaltung/Import: JSON einlesen, rudimentärer Import (Platzhalter-Logik).

## Daten- und State-Verträge

- color_palette (Dict)
  - Muss mindestens enthalten: primary, secondary, text, separator, white, black, grey, darkgrey.

- st.session_state Keys
  - pdf_theme_settings: {'selected_theme', 'custom_colors', 'custom_fonts', 'chart_customizations', 'layout_customizations', 'effects'}
  - custom_themes: Dict[str, ThemeDef]
  - pdf_visual_enhancer / pdf_theme_manager: Instanzen im Session-State für UI-Rendering.

## Integration in die PDF-Pipeline

- get_pdf_stylesheet und TableStyles: werden von pdf_generator.py für Story/Flowables genutzt.
- Effects (z. B. Seitenzahlen, Wasserzeichen) sind aktuell UI-Einstellungen; Integration in den tatsächlichen PDF-Build erfolgt über pdf_generator (page_layout_handler, header/footer, optionales Watermarking).
- Visual Enhancer erzeugt PNG-Images, die als Abbildungen in PDFs eingebunden werden können.

## Edge Cases und Fehlerverhalten

- Fehlende Farben/Keys in color_palette: führt zu KeyError; empfohlen: immer über get_color_palette() erzeugen.
- Matplotlib/Seaborn Backend: Für Headless-Umgebungen sicherstellen, dass der passende Backend/Treiber (und Fonts) verfügbar ist.
- Export/Import: Import-Fehler werden im UI abgefangen und als Streamlit-Fehler angezeigt.
- datetime in Export: sicherstellen, dass "from datetime import datetime" vorhanden ist, wenn Export genutzt wird.

## Migration zu Electron + PrimeReact + TypeScript

- Stylesheet/ParagraphStyles
  - TS-Pendants: pdf-lib/pdfmake oder @react-pdf/renderer. ParagraphStyles werden als Style-Objekte abgebildet.

- Farb-/Theme-System
  - ColorScheme als TS-Interface; Persistenz als JSON im app userData.
  - Chart-/Layout-/Effekt-Settings in Redux/Zustand oder React Context halten.

- Diagramme/Visuals
  - Plotly.js oder Chart.js. Export als PNG
    - Option 1: node-kaleido (Plotly) für toImage.
    - Option 2: Puppeteer/Screenshot von Canvas/SVG.

- Hintergrund-/Formgenerator
  - Canvas (HTML5) oder svg.js für dynamische Muster/Formen; Export als PNG/SVG.

- Import/Export
  - Reines JSON mit Schema-Validierung (z. B. zod) und Versionskennung.

## Test-/Verifikationshinweise

- Unit: get_color_palette (HEX→ReportLab-Farben), _generate_color_palette (5 HEX-Werte, gültiges HEX-Format).
- Snapshot: get_pdf_stylesheet erzeugt alle erwarteten Style-Namen.
- UI: Session-State-Initialisierung und Persistenz der Auswahl (selected_theme, effects).
- Visuals: create_enhanced_chart produziert gültige PNG-Bytes (>0), bei fehlerhaften Daten Fallback.
