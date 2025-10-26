# Konsolidierung Dienstleistungs-Darstellung (Seite 6)

Dieser Patch vereinheitlicht die UI-Konfiguration für die Darstellung der Dienstleistungen (und optional Produkt-Werte) auf Seite 6 des PDF-Angebots.

Änderungen:

1. Neues Modul `service_display_config_ui.py` mit Funktion `render_service_display_config()`.
2. `pdf_ui.py` nutzt jetzt ausschließlich diesen Helper (alter Expander-Code entfernt).
3. `doc_output.py` nutzt ebenfalls den Helper; duplicierter Abschnitt entfernt.
4. Defensive Initialisierung für `extended_features['wow_features']` ergänzt.
5. Einheitliche Werte für `service_symbol_style`: `check | checkbox | dot | none` (Benutzerfreundliche Labels im Selectbox, Speicherung der technischen Werte).
6. Reset-Button setzt alle relevanten Keys zurück:
   - service_checkmarks_enabled
   - service_symbol_style
   - service_value_column_hidden
   - service_symbol_color
   - service_label_color

Verwendung:

Importiere bei Bedarf:

```python
from service_display_config_ui import render_service_display_config
render_service_display_config(st.session_state['pdf_design_config'])
```

Rendering Engine Kopplung:
`pdf_template_engine/placeholders.py` und `dynamic_overlay.py` lesen die Flags:
`service_symbol_style`, `service_value_column_hidden`, `service_symbol_color`, `service_label_color`, `service_checkmarks_enabled`.

Rückwärtskompatibilität:
Ehemalige Werte wie deutsche Begriffe ("Häkchen") werden nicht mehr gesetzt; falls sie in Altdaten existieren, wird per Default-Fallback auf `check` normalisiert.

Letzte Prüfung: Keine Syntax- oder Lint-Fehler (Stand Konsolidierungstag).
