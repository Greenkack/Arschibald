# pdf_template_engine/dynamic_overlay.py – vollständige Logik-Extraktion

Dieses Modul erzeugt die sechsseitigen Text-Overlays auf Basis der YML-Koordinaten (`coords/seite1.yml` … `seite6.yml`), zeichnet dynamische Elemente (Firmenlogo, KPI-Donuts, Dreieck), und merged das Overlay mit statischen Hintergründen (`pdf_templates_static/notext/nt_nt_01.pdf` … `nt_nt_06.pdf`). Optional werden weitere Seiten hinten angehängt. Es ist die zentrale Render- und Merge-Pipeline für das „6-Seiten-Haupttemplate“.

## Überblick und Abhängigkeiten

- Abhängigkeiten: reportlab (Canvas, ImageReader), pypdf (PdfReader/Writer/Transformation), A4, Color, base64.
- Interne Abhängigkeiten: `PLACEHOLDER_MAPPING` aus `pdf_template_engine/placeholders.py`; optional `database.load_admin_setting` für Wasserzeichen.
- Eingaben: `coords/*.yml` (Text, Position(x0,y0,x1,y1), Schriftart/-größe, Farbe), `dynamic_data` (Key→Wert aus `build_dynamic_data`).
- Ausgaben: Bytes eines fertigen PDF (Overlay, gemerged mit Hintergründen, inkl. optionaler Zusatzseiten).

## Öffentliche API

- `generate_overlay(coords_dir: Path, dynamic_data: Dict[str, str], total_pages: int = 6) -> bytes`
  - Erzeugt ein sechsseitiges Overlay-PDF anhand der YML-Einträge; zeichnet Logo, Seite-1-Donuts und Seite-4-Bilder.
  - Nutzt `PLACEHOLDER_MAPPING`, um Beispieltexte aus YML durch `dynamic_data`-Werte zu ersetzen.
  - Nutzt `total_pages` ausschließlich für die Seitennummerierung „Seite x von XX“.

- `merge_with_background(overlay_bytes: bytes, bg_dir: Path) -> bytes`
  - Merged für Seiten 1–6 je ein statisches PDF als Hintergrund: bevorzugt `nt_nt_XX.pdf`, sonst `nt_XX.pdf`.
  - Optional auf Seite 1: `haus.pdf` als zusätzliche Ebene (skaliert auf 30%, zentriert) zwischen Standard-Hintergrund und Overlay.
  - Fallbacks: Wenn kein Hintergrund gefunden werden kann, wird nur das Overlay genutzt.

- `append_additional_pages(base_pdf: bytes, additional_pdf: Optional[bytes]) -> bytes`
  - Hängt ein optionales Zusatz-PDF hinten an (alle Seiten). Bei None wird das Basis-PDF unverändert zurückgegeben.

- `generate_custom_offer_pdf(coords_dir: Path, bg_dir: Path, dynamic_data: Dict[str, str], additional_pdf: Optional[bytes] = None) -> bytes`
  - End-to-End: berechnet `total_pages` (6 + Zusatzseiten), erzeugt Overlay, merged mit Hintergrund, hängt ggf. an.

## Interne Helfer

- `_to_bool(val, default=False) -> bool`: Toleranter Bool-Parser ("1", "true", "yes", numerisch).
- `_draw_global_watermark(c, w, h)`: Optionaler diagonal gesetzter Text aus Admin-Settings (`pdf_global_watermark_*`). Aktuell im Code vorbereitet; Zeichnung in `generate_overlay` nicht aktiviert. Kann leicht ergänzt werden.
- `parse_coords_file(path: Path) -> List[Dict]]`: Minimal-YML-Parser ohne externe Abhängigkeit.
  - Trennt Einträge per Trennlinie (`---` oder viele `-`).
  - Unterstützt Felder: `Text:`, `Position: x0 y0 x1 y1` (Komma/Punkt), `Schriftart:`, `Schriftgröße:`, `Farbe:` (int oder 0xRRGGBB).
- `int_to_color(value: int) -> Color`: 0xRRGGBB → reportlab Color.
- `_draw_company_logo(c, dynamic_data, w, h)`: Zeichnet `company_logo_b64` links oben, maskiert vorher die Template-Logo-Box mit Weiß.
- `_draw_donut`, `_draw_page1_kpi_donuts(...)`: Donut-Ring mit Anteil; Seite 1 zeigt zwei Donuts für Autarkie und Eigenverbrauch (Werte aus `dynamic_data` mit robusten Fallback-Keys). Verhindert Doppeldruck der originalen „54%/42%“-Texte aus Seite 1.
- `_draw_top_right_triangle(c, w, h, size=36)`: Kleines gefülltes Dreieck als Akzent oben rechts.
- `_draw_page4_component_images(c, dynamic_data, w, h)`: Zeichnet bis zu drei Base64-Bilder (Modul/WR/Speicher) positionsgenau in Seite 4.

## Render- und Ersetzungs-Flow (generate_overlay)

Pro Seite 1…6:

1) Koordinaten lesen (`coords/seite{i}.yml`) → Liste Elemente.
2) Logo zeichnen, Akzent-Dreieck zeichnen; auf Seite 1 zusätzlich KPI-Donuts, auf Seite 4 Produktbilder.
3) Für jedes Element:
   - `text` aus YML → Lookup in `PLACEHOLDER_MAPPING` → Key → `dynamic_data[key]` oder Originaltext.
   - Koordinaten: Y wird top-left-orientiert (ReportLab) konvertiert (`draw_y = page_height - y1`).
   - Schrift: `font`/`font_size` als Wunsch; Fallback `Helvetica`.
   - Farbe: `Farbe:` als int → `int_to_color`.
   - Spezialfälle:
     - Seite 1: Keys `self_supply_rate_percent` und `self_consumption_percent` werden nicht gedruckt (Donut-Zentrum übernimmt die Zahlenanzeige).
     - Fußzeile rechts: Automatische Ersetzung der weißen Ziffer 1…6 in der Fußzeile durch „Seite x von XX“ (Heuristik via Position/Farbe/Ziffer).
     - Zentrierte Keys (Seite 2 Pfeile und Gegenstücke): Strings anhand Bounding-Box horizontal mittig zeichnen.
4) `showPage()` und am Ende `save()` → Overlay-PDF als Bytes.

## Merge-Flow (merge_with_background)

- Für jede Seite 1…6: Hintergrund suchen (`nt_nt_XX.pdf` → `nt_XX.pdf`).
- Optional (nur Seite 1): `haus.pdf` als zusätzliche Ebene über dem Standard-Hintergrund (30% skaliert). Wenn kein Standard-Hintergrund vorhanden ist, kann `haus.pdf` als Basis genutzt werden (Blank-Seite, transformiertes Haus, dann Overlay).
- Am Ende wird die Overlay-Seite gemerged. Fallback: nur Overlay-Seite übernehmen.

## End-to-End (generate_custom_offer_pdf)

- `total_pages` = 6 + Seitenzahl des optionalen Zusatz-PDF.
- Overlay erzeugen → mit Hintergrund mergen → Zusatzseiten anhängen.

## Datenkontrakte und Schlüssel

- Erwartet `dynamic_data`-Keys aus `placeholders.build_dynamic_data`, u. a.:
  - `customer_*`, `company_*`, KPI-Werte (kWp, kWh/Jahr, %), monetäre Felder (€, Cent/kWh), Seite-2-KWh-Anteile, Seite-3-Erträge, Seite-4-Komponentenfelder, Bilder-Base64.
- `PLACEHOLDER_MAPPING` verbindet die `coords/*.yml`-Beispieltexte mit diesen Keys.

## Edge-Cases und Robustheit

- Fehlende YML/Template-Seiten → leere Liste bzw. Fallback ohne Hintergrund; PDF bleibt erzeugbar.
- Fehlendes Firmenlogo/Bilder → einfach übersprungen.
- Fonts/Farben nicht lesbar → Fallbacks (`Helvetica`, Schwarz).
- Seitennummer-Heuristik ist defensiv; bei Nichttreffern wird der Originaltext gedruckt.
- Zusätzliche Haus-Ebene (haus.pdf): robustes Fallback (unskaliertes Mergen bei Fehlversuch bzw. Nutzung als Basis).

## TypeScript/Electron-Portierung

- Renderer: Keine PDF-APIs. Empfohlen: Alles im Main-Prozess (Node) über pdf-lib oder HummusJS/ghostscript.
- Services (Main):
  - `parseCoords(file: string): Element[]` (einfacher Parser)
  - `buildOverlay(coordsDir: string, data: Record<string,string>, totalPages=6): Buffer`
  - `mergeWithBackground(overlay: Buffer, bgDir: string): Buffer`
  - `appendAdditional(base: Buffer, add?: Buffer): Buffer`
  - `generateCustomOffer(...)`
- Grafik: Donuts lassen sich mit pdf-lib Pfaden zeichnen; Bilder (Base64) via `embedPng/Jpeg`.
- Farbe: Integer 0xRRGGBB → r,g,b durch Bit-Operationen.

## Tests (empfohlen)

- Unit: `parse_coords_file` (Positions-Parsing, Farben, Schriftgrößen), `int_to_color` (RGB-Extraktion), Donut-Zeichenlogik (extents), Seitennummer-Heuristik (pos/color/isdigit).
- Integration: Minimal-Overlay mit 1–2 Elementen und Mergen ohne Hintergründe; mit `haus.pdf` als Zusatz; mit Zusatz-PDF.
- Snapshot-Test: Gegen ein goldenes PDF (nur Overlay), um Textplatzierungen stabil zu halten.
