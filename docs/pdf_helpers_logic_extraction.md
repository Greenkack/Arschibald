# pdf_helpers.py — vollständige Logik-Extraktion

Ziel: Helfer für dynamische Kopf-/Fußzeilen in PDFs dokumentieren. Ergänzt `pdf_generator.py` um Flowables zur Seitentitel-/Seitengesamtzahl-Steuerung und Build-Strategien.

## Überblick

- Rolle: ReportLab-Flowables zur Kommunikation mit Canvas (Seitentitel, Gesamtseitenzahl), Utility-Funktionen für Story-Manipulation und zweiphasigen Build.
- Hauptbestandteile:
  - Klassen: `PageTitleSetter(Flowable)`, `TotalPagesSetter(Flowable)`
  - Funktionen: `add_page_title_to_story(story, title)`, `prepare_pdf_with_correct_page_numbers(doc, story)`, `create_section_title_mapping()`, `integrate_dynamic_headers_into_existing_pdf()`
  - Streamlit-Beispiel: `create_streamlit_pdf_with_enhanced_headers(...)` mit `page_layout_handler`-Hook aus `pdf_generator`.

## Kontrakte

- `PageTitleSetter.draw()`
  - Erwartet: `self.canv.current_chapter_title_for_header` am Canvas; setzt aktuellen Titel.
- `TotalPagesSetter.draw()`
  - Setzt `self.canv.total_pages` für Seitenzählung im Header/Footer.
- `prepare_pdf_with_correct_page_numbers(doc, story) -> bytes`
  - Führt 2 Builds aus: (1) temp zum Ermitteln `total_pages`, (2) final nach Insert eines `TotalPagesSetter` an Index 0.
- `create_section_title_mapping() -> Dict[str,str]`
  - Einheitliche Anzeige-Texte pro Abschnitt-Key (ProjectOverview, TechnicalComponents, ...).

## Integration in pdf_generator

- Vor Sektionsinhalten: `add_page_title_to_story(story, section_titles[section_key])` einfügen.
- Header/Footer-Layer: In `page_layout_handler(canvas, ...)` den `canvas.current_chapter_title_for_header` und `canvas.total_pages` auswerten und anzeigen.
- Für korrekte Seitenzahlen: `prepare_pdf_with_correct_page_numbers(doc, story)` statt einfachem `doc.build(...)` nutzen.

## Edge-Cases

- Canvas-Attribute nicht vorhanden: defensiv prüfen (`hasattr`) beim Lesen/Schreiben in Layout-Handler.
- Story-Inserts: Reihenfolge beachten (Deckblatt → Titel setzen; danach Abschnitte jeweils per Setter).

## Migration: Electron + TypeScript

- ReportLab-Äquivalent in Node: bei Umstieg auf TS-PDF-Stack (pdf-lib, pdfmake) die Seitentitel/Gesamtseitenzahl als „global state“ im Renderer setzen und beim Seiten-Render berücksichtigen; zweiphasiger Build ggf. via erstem Durchlauf zum Counten der Seiten.

## Tests (skizziert)

- Story mit 3 Abschnitten → Header zeigt jeweiligen Titel; Gesamtseitenzahl korrekt in Footer.
- Setter mehrfach in Story: letzter gesetzter Titel pro Seite wird im Header gerendert.
