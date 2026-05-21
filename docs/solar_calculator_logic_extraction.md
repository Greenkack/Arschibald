# solar_calculator.py — Logik-Extraktion

Kurzüberblick: Eigenständiger Menüpunkt zur Technik-Auswahl (Module, Wechselrichter, Speicher, Zusatzkomponenten). Schreibt seine Ergebnisse in st.session_state.project_data['project_details'] kompatibel zu data_input.

## Hauptablauf und Verträge

- render_solar_calculator(texts, module_name=None)
  - Initialisiert project_data-Teilbäume: project_details, customer_data, economic_data.
  - Produktlisten per product_db.list_products(category) mit Fallback-Dummys, falls Import fehlschlägt.
  - UI-Blöcke:
    1) Module
       - Inputs: module_quantity (int), selected_module_name (selectbox)
       - Seiteneffekte: selected_module_id, selected_module_capacity_w; anlage_kwp = quantity * capacity_w / 1000.
    2) Wechselrichter
       - Inputs: selected_inverter_name, selected_inverter_quantity (>=1)
       - Seiteneffekte: selected_inverter_id, selected_inverter_power_kw_single, selected_inverter_power_kw (= single * qty)
       - Zusätzlich: schreibt inverter_power_kw auf project_data Top-Level (für Analysen).
    3) Speicher (optional)
       - include_storage (bool), selected_storage_name, selected_storage_storage_power_kw
       - Seiteneffekte: selected_storage_id; zeigt Modellkapazität wenn verfügbar.
    4) Zusatzkomponenten (optional)
       - include_additional_components (bool)
       - Auswahl je Kategorie mit robustem Label-Fallback: Wallbox, Energiemanagementsystem, Leistungsoptimierer, Carport, Notstromversorgung, Tierabwehrschutz
  - Je Auswahl: legt `selected_*_name` und `selected_*_id`
  - Abschluss: st.success Hinweistexte.

- Hilfsfunktionen
  - _get_text(texts, key, fallback?): sichere Textauflösung mit Fallback.
  - _ensure_project_data_dicts(): legt die benötigten Dicts in session_state an.
  - _product_names_by_category(category, texts) -> List[str]: holt model_name-Liste aus product_db; bei leer/nicht verfügbar, Rückgabe Dummy-Hinweis.

## Daten- und State-Verträge

- st.session_state.project_data['project_details'] schreibt/liest u. a.:
  - module_quantity: int
  - selected_module_name: Optional[str]
  - selected_module_id: Optional[int]
  - selected_module_capacity_w: float
  - anlage_kwp: float
  - selected_inverter_name: Optional[str]
  - selected_inverter_id: Optional[int]
  - selected_inverter_quantity: int
  - selected_inverter_power_kw_single: float
  - selected_inverter_power_kw: float
  - include_storage: bool
  - selected_storage_name: Optional[str]
  - selected_storage_id: Optional[int]
  - selected_storage_storage_power_kw: float
  - include_additional_components: bool
  - selected_{wallbox,ems,optimizer,carport,notstrom,tierabwehr}_name/id

- st.session_state.project_data Top-Level
  - inverter_power_kw: float (Summe, abgeleitet aus WR-Anzahl * WR-Leistung)

## Abhängigkeiten

- product_db.list_products(category), product_db.get_product_by_model_name(name)
  - Fehlerrobust durch Try/Except mit Dummy-Fallbacks; UI bleibt funktionsfähig.

## Edge Cases

- Produktlisten leer: UI zeigt Platzhalter („Keine Produkte in DB“); IDs bleiben None.
- Ungültige Quantities: number_input erzwingt Grenzen (z. B. min 0 oder 1).
- Mismatch bei vorausgefüllten Werten: Selectbox wählt sicheren Index 0 (Bitte wählen…), wenn current nicht in Optionen.

## Migration zu Electron + PrimeReact + TypeScript

- Produkte aus SQLite via better-sqlite3 (Renderer) oder IPC-Service; gleiche Filter nach category.
- State in Redux/Zustand; project_data.project_details Schema als TS-Interface.
- ID-Auflösung bei Auswahl: nach model_name ein Produkt-Objekt holen und Felder mappen.
- kWp-Berechnung und WR-Gesamtleistung als selektoren/reselect.

## Tests

- Prefill: Vorbelegte project_details werden korrekt als Default-Werte angezeigt.
- Auswahl: Änderung der Auswahl setzt IDs und abgeleitete Werte (anlage_kwp, selected_inverter_power_kw).
- Speicher-Komponente: Modellkapazität wird angezeigt und kann überschrieben werden.
