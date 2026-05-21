# Fix: Bedarfsanalyse Radio-Button bleibt immer auf "Photovoltaik + Wärmepumpe"

## Problem

Die Auswahl des Anlagenmodus in der Bedarfsanalyse funktionierte nicht richtig. Obwohl der User "Nur Photovoltaik" oder "Nur Wärmepumpe" auswählte, sprang die Auswahl sofort zurück auf "Photovoltaik + Wärmepumpe".

## Ursache

Das Problem lag in der Verwendung der `mirror_widget_value()` und `commit_widget_value()` Funktionen:

1. **Mirror überschrieb User-Auswahl**: Bei jedem Rerun wurde `mirror_widget_value()` aufgerufen und setzte den Widget-Key auf den Wert des persistenten Keys - **bevor** Streamlit die User-Auswahl verarbeiten konnte
2. **Rückgabewert wurde ignoriert**: Die Variable `selected_mode_code` enthielt die User-Auswahl, wurde aber nie verwendet
3. **Komplexe Indirektion**: Der mirror/commit Mechanismus war zu komplex und fehleranfällig für einfache Widget-Interaktionen

### Original Code Flow (DEFEKT)

```python
# 1. Mirror setzt Widget-Key auf "pv_wp_combined"
mode_widget_key = mirror_widget_value("demand_mode_selection", ...)

# 2. Radio rendert mit diesem Key
selected_mode_code = st.radio(..., key=mode_widget_key)  # User wählt "pv_only"

# 3. Commit kopiert Widget-Key → Persistent-Key
commit_widget_value("demand_mode_selection", ...)  # Setzt demand_mode_selection = "pv_only"

# 4. NÄCHSTER RERUN: Mirror überschreibt Widget-Key WIEDER mit "pv_wp_combined"!
# → User-Auswahl geht verloren
```

## Lösung

### Datei: `data_input.py` (Zeilen 193-227)

Ersetzt den komplexen mirror/commit Mechanismus durch eine **direkte, einfache Lösung**:

```python
# Direkter Ansatz ohne mirror/commit
current_mode = st.session_state.get("demand_mode_selection", "pv_wp_combined")

# Legacy-Werte umwandeln
if current_mode in legacy_map_modes:
    current_mode = legacy_map_modes[current_mode]
    st.session_state.demand_mode_selection = current_mode

# Index für Radio-Button finden
current_index = list(register_options.keys()).index(current_mode)

# Radio mit direktem Index rendern
selected_mode_code = st.radio(
    "Bedarfsanalyse-Modus",
    options=list(register_options.keys()),
    index=current_index,  # ← WICHTIG: Setzt initialen Wert
    key="demand_mode_selection_radio_widget",
)

# Nur bei Änderung Session State aktualisieren
if selected_mode_code != current_mode:
    st.session_state.demand_mode_selection = selected_mode_code
```

### Vorteile der neuen Lösung

1. ✅ **Keine Überschreibung**: User-Auswahl wird nie überschrieben
2. ✅ **Direkter Zugriff**: Kein indirekter mirror/commit Mechanismus mehr
3. ✅ **Rückgabewert wird genutzt**: `selected_mode_code` wird tatsächlich verwendet
4. ✅ **Einfacher zu verstehen**: Klarer, linearer Code-Flow
5. ✅ **Persistent**: `demand_mode_selection` wird in `_persistent_state_registry` registriert

### Datei: `ui_state_manager.py` (Zeilen 55-72)

Die Änderung hier wurde rückgängig gemacht, da der mirror/commit Mechanismus für diese Komponente nicht mehr verwendet wird. Der Code bleibt für andere Komponenten, die ihn noch nutzen.

## Funktionsweise nach dem Fix

### User-Interaktion Flow

1. **Erster Render**:
   - `current_mode` = "pv_wp_combined" (default)
   - Radio zeigt "Photovoltaik + Wärmepumpe" (index=2)

2. **User klickt "Nur Photovoltaik"**:
   - Radio ändert sich visuell
   - `selected_mode_code` = "pv_only"
   - Streamlit triggert Rerun

3. **Zweiter Render (nach User-Klick)**:
   - `current_mode` wird aus Session State geladen = "pv_only" ✓
   - Radio zeigt "Nur Photovoltaik" (index=0) ✓
   - Auswahl bleibt erhalten! ✓

## Test-Schritte

1. Starte die App und gehe zu "Projekt - Bedarfsanalyse"
2. Standardmäßig sollte "Photovoltaik + Wärmepumpe" ausgewählt sein
3. Klicke auf "Nur Photovoltaik"
   - ✅ Auswahl sollte auf "Nur Photovoltaik" bleiben
   - ✅ Info-Text sollte sich ändern
4. Klicke auf "Nur Wärmepumpe"
   - ✅ Auswahl sollte auf "Nur Wärmepumpe" bleiben
5. Navigiere zu einer anderen Seite und zurück
   - ✅ Deine letzte Auswahl sollte noch da sein (Persistenz)

## Weitere Verbesserungen

Falls das Problem auch bei anderen Radio-Buttons oder Select-Widgets auftritt, sollte die gleiche Lösung angewendet werden:

- Verwende `index` Parameter direkt
- Nutze den Rückgabewert des Widgets
- Vermeide mirror/commit für einfache Widgets
- Nur für komplexe Multi-Widget-Szenarien ist mirror/commit sinnvoll

## Betroffene Dateien

- ✅ `data_input.py` - Bedarfsanalyse Radio-Button repariert
- ✅ `ui_state_manager.py` - Dokumentation aktualisiert (keine Code-Änderung nötig)
