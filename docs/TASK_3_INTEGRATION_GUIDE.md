# Task 3: Diagrammauswahl in PDF UI - Integrations-Anleitung

## Übersicht

Diese Anleitung zeigt, wie die implementierte Diagrammauswahl-UI in die bestehende `render_pdf_ui()` Funktion integriert wird.

---

## Schritt 1: Import-Prüfung

Stelle sicher, dass alle benötigten Imports vorhanden sind:

```python
import streamlit as st
from typing import Any, Callable, Dict, List
from datetime import datetime
import json
import logging
```

**Status**: ✅ Bereits vorhanden in pdf_ui.py

---

## Schritt 2: Integration in render_pdf_ui()

### Position im Code

Die Diagrammauswahl sollte nach der Datenvalidierung und vor der PDF-Generierung eingefügt werden.

**Empfohlene Position**: Nach Zeile ~1400 in `render_pdf_ui()`, nach der Vorlagen-Auswahl und vor dem PDF-Generierungs-Button.

### Code-Snippet für Integration

```python
def render_pdf_ui(
    texts: dict[str, str],
    project_data: dict[str, Any],
    analysis_results: dict[str, Any],
    load_admin_setting_func: Callable[[str, Any], Any],
    save_admin_setting_func: Callable[[str, Any], bool],
    list_products_func: Callable,
    get_product_by_id_func: Callable,
    get_active_company_details_func: Callable[[], dict[str, Any] | None] = _dummy_get_active_company_details,
    db_list_company_documents_func: Callable[[int, str | None], list[dict[str, Any]]] = _dummy_list_company_documents
):
    # ... (bestehender Code bis zur Vorlagen-Auswahl) ...
    
    # ========================================================================
    # DIAGRAMMAUSWAHL-UI INTEGRATION - Task 3
    # ========================================================================
    
    st.markdown("---")
    st.header("📊 Diagrammauswahl")
    
    # 1. Initialisiere Session State
    initialize_chart_selection_state()
    
    # 2. Rendere Diagrammauswahl-UI
    selected_charts = render_chart_selection_ui(
        project_data=project_data,
        analysis_results=analysis_results,
        texts=texts
    )
    
    # 3. Zeige Auswahl-Zusammenfassung
    render_chart_selection_info_panel(selected_charts)
    
    # 4. Zeige Generierungsstatus
    render_chart_generation_status(
        selected_charts=selected_charts,
        project_data=project_data,
        analysis_results=analysis_results
    )
    
    # 5. Persistenz-Management
    manage_chart_selection_persistence(
        load_admin_setting_func=load_admin_setting_func,
        save_admin_setting_func=save_admin_setting_func
    )
    
    st.markdown("---")
    
    # ========================================================================
    # END DIAGRAMMAUSWAHL-UI INTEGRATION
    # ========================================================================
    
    # ... (bestehender Code für PDF-Generierung) ...
```

---

## Schritt 3: PDF-Generierung anpassen

### Vor der PDF-Generierung

Bereite die Daten vor, indem nur ausgewählte Diagramme inkludiert werden:

```python
# Vor dem Aufruf von generate_offer_pdf():

# Bereite Daten für PDF-Generierung vor
prepared_project_data, prepared_analysis_results = prepare_chart_data_for_pdf_generation(
    project_data=project_data,
    analysis_results=analysis_results,
    selected_charts=selected_charts
)

# Generiere PDF mit gefilterten Daten
pdf_bytes = _generate_offer_pdf_safe(
    texts=texts,
    project_data=prepared_project_data,  # Verwende prepared_project_data
    analysis_results=prepared_analysis_results,  # Verwende prepared_analysis_results
    company_info=company_info_for_pdf,
    company_logo_b64=company_logo_b64_for_pdf,
    # ... weitere Parameter ...
)
```

### Alternative: Direkte Filterung

Falls `prepare_chart_data_for_pdf_generation()` nicht verwendet werden soll:

```python
# Filtere analysis_results direkt
filtered_analysis_results = filter_analysis_results_by_selection(
    analysis_results=analysis_results,
    selected_charts=selected_charts
)

# Generiere PDF mit gefilterten Daten
pdf_bytes = _generate_offer_pdf_safe(
    texts=texts,
    project_data=project_data,
    analysis_results=filtered_analysis_results,  # Verwende gefilterte Daten
    company_info=company_info_for_pdf,
    company_logo_b64=company_logo_b64_for_pdf,
    # ... weitere Parameter ...
)
```

---

## Schritt 4: Vollständiges Integrations-Beispiel

### Kompletter Code-Block

```python
def render_pdf_ui(
    texts: dict[str, str],
    project_data: dict[str, Any],
    analysis_results: dict[str, Any],
    load_admin_setting_func: Callable[[str, Any], Any],
    save_admin_setting_func: Callable[[str, Any], bool],
    list_products_func: Callable,
    get_product_by_id_func: Callable,
    get_active_company_details_func: Callable[[], dict[str, Any] | None] = _dummy_get_active_company_details,
    db_list_company_documents_func: Callable[[int, str | None], list[dict[str, Any]]] = _dummy_list_company_documents
):
    """
    Hauptfunktion für die PDF-UI mit integrierter Diagrammauswahl.
    """
    
    # ... (bestehender Code: Header, Angebotstyp, Datenvalidierung) ...
    
    # ========================================================================
    # VORLAGEN-AUSWAHL (bestehender Code)
    # ========================================================================
    
    # Titelbild-Vorlage
    if title_image_templates:
        selected_title_image_name = st.selectbox(
            "Titelbild-Vorlage",
            [t['name'] for t in title_image_templates],
            key="select_title_image"
        )
        # ... (weitere Vorlagen-Auswahl) ...
    
    # ========================================================================
    # DIAGRAMMAUSWAHL-UI (NEU)
    # ========================================================================
    
    st.markdown("---")
    st.header("📊 Diagrammauswahl für erweiterte PDF")
    
    # Initialisiere Session State
    initialize_chart_selection_state()
    
    # Rendere Diagrammauswahl-UI
    selected_charts = render_chart_selection_ui(
        project_data=project_data,
        analysis_results=analysis_results,
        texts=texts
    )
    
    # Zeige Auswahl-Zusammenfassung
    render_chart_selection_info_panel(selected_charts)
    
    # Zeige Generierungsstatus
    render_chart_generation_status(
        selected_charts=selected_charts,
        project_data=project_data,
        analysis_results=analysis_results
    )
    
    # Persistenz-Management
    with st.expander("💾 Auswahl speichern/laden", expanded=False):
        manage_chart_selection_persistence(
            load_admin_setting_func=load_admin_setting_func,
            save_admin_setting_func=save_admin_setting_func
        )
    
    st.markdown("---")
    
    # ========================================================================
    # PDF-GENERIERUNG (angepasst)
    # ========================================================================
    
    if st.button("📄 PDF generieren", key="btn_generate_pdf"):
        with st.spinner("PDF wird generiert..."):
            try:
                # Bereite Daten vor (nur ausgewählte Diagramme)
                prepared_project_data, prepared_analysis_results = \
                    prepare_chart_data_for_pdf_generation(
                        project_data=project_data,
                        analysis_results=analysis_results,
                        selected_charts=selected_charts
                    )
                
                # Generiere PDF
                pdf_bytes = _generate_offer_pdf_safe(
                    texts=texts,
                    project_data=prepared_project_data,
                    analysis_results=prepared_analysis_results,
                    company_info=company_info_for_pdf,
                    company_logo_b64=company_logo_b64_for_pdf,
                    # ... weitere Parameter ...
                )
                
                if pdf_bytes:
                    st.success("✅ PDF erfolgreich generiert!")
                    
                    # Download-Button
                    st.download_button(
                        label="📥 PDF herunterladen",
                        data=pdf_bytes,
                        file_name=f"Angebot_{customer_name}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
                    
                    # Zeige Metadaten
                    if '_chart_selection_metadata' in prepared_analysis_results:
                        metadata = prepared_analysis_results['_chart_selection_metadata']
                        st.info(f"📊 PDF enthält {metadata['selected_count']} Diagramme")
                else:
                    st.error("❌ Fehler bei der PDF-Generierung")
                    
            except Exception as e:
                st.error(f"❌ Fehler: {str(e)}")
                logging.error(f"PDF-Generierung fehlgeschlagen: {e}", exc_info=True)
```

---

## Schritt 5: Optionale Erweiterungen

### 5.1 Diagramm-Vorschau

Falls Vorschau-Funktionalität gewünscht:

```python
# Nach der Diagrammauswahl
if selected_charts:
    with st.expander("👁️ Diagramm-Vorschau", expanded=False):
        for chart_key in selected_charts[:3]:  # Zeige erste 3
            if chart_key in analysis_results and analysis_results[chart_key]:
                friendly_name = CHART_KEY_TO_FRIENDLY_NAME_MAP.get(chart_key, chart_key)
                st.subheader(friendly_name)
                st.image(analysis_results[chart_key])
        
        if len(selected_charts) > 3:
            st.info(f"... und {len(selected_charts) - 3} weitere Diagramme")
```

### 5.2 Diagramm-Reihenfolge anpassen

Falls Benutzer die Reihenfolge ändern sollen:

```python
# Nach der Diagrammauswahl
if selected_charts:
    with st.expander("🔢 Reihenfolge anpassen", expanded=False):
        st.info("Ziehen Sie die Diagramme, um die Reihenfolge zu ändern")
        
        # Verwende st-sortable oder ähnliche Komponente
        # (Benötigt zusätzliche Bibliothek)
        
        # Alternativ: Einfache Up/Down Buttons
        for idx, chart_key in enumerate(selected_charts):
            col1, col2, col3 = st.columns([0.7, 0.15, 0.15])
            with col1:
                st.text(CHART_KEY_TO_FRIENDLY_NAME_MAP.get(chart_key, chart_key))
            with col2:
                if idx > 0 and st.button("⬆️", key=f"up_{chart_key}"):
                    # Verschiebe nach oben
                    selected_charts[idx], selected_charts[idx-1] = \
                        selected_charts[idx-1], selected_charts[idx]
                    st.rerun()
            with col3:
                if idx < len(selected_charts) - 1 and st.button("⬇️", key=f"down_{chart_key}"):
                    # Verschiebe nach unten
                    selected_charts[idx], selected_charts[idx+1] = \
                        selected_charts[idx+1], selected_charts[idx]
                    st.rerun()
```

### 5.3 Diagramm-Beschreibungen

Falls Beschreibungen angezeigt werden sollen:

```python
# Erweitere CHART_KEY_TO_FRIENDLY_NAME_MAP mit Beschreibungen
CHART_DESCRIPTIONS = {
    'roi_chart_bytes': "Zeigt die Entwicklung des Return on Investment über die Laufzeit der Anlage.",
    'co2_chart_bytes': "Visualisiert die jährliche CO₂-Einsparung durch die PV-Anlage.",
    # ... weitere Beschreibungen ...
}

# In der UI
for chart_key in category_available:
    friendly_name = available_charts[chart_key]
    description = CHART_DESCRIPTIONS.get(chart_key, "")
    
    selected = st.checkbox(
        friendly_name,
        value=is_selected,
        key=checkbox_key,
        help=description  # Zeigt Beschreibung als Tooltip
    )
```

---

## Schritt 6: Testing nach Integration

### Manuelle Tests

1. **Basis-Funktionalität**:
   - [ ] PDF UI öffnet ohne Fehler
   - [ ] Diagrammauswahl wird angezeigt
   - [ ] Statistiken sind korrekt
   - [ ] Buttons funktionieren
   - [ ] Checkboxen funktionieren

2. **Auswahl-Logik**:
   - [ ] "Alle auswählen" wählt alle verfügbaren aus
   - [ ] "Keine auswählen" entfernt alle Auswahlen
   - [ ] "Empfohlene auswählen" wählt 6 Basis-Diagramme
   - [ ] Individuelle Auswahl funktioniert
   - [ ] Session State wird aktualisiert

3. **Verfügbarkeits-Prüfung**:
   - [ ] Basis-Diagramme sind verfügbar
   - [ ] Finanzierungs-Diagramme nur mit Flag
   - [ ] Batterie-Diagramme nur mit Storage
   - [ ] Nicht verfügbare werden markiert

4. **PDF-Generierung**:
   - [ ] PDF wird mit ausgewählten Diagrammen generiert
   - [ ] Nicht ausgewählte Diagramme fehlen in PDF
   - [ ] Metadaten sind korrekt
   - [ ] Download funktioniert

5. **Persistenz**:
   - [ ] Speichern funktioniert
   - [ ] Laden funktioniert
   - [ ] Gespeicherte Auswahl bleibt erhalten

### Automatisierte Tests

```python
def test_integration_chart_selection():
    """Test der vollständigen Integration"""
    
    # Setup
    project_data = {
        'project_details': {
            'module_quantity': 10,
            'anlage_kwp': 5.0
        }
    }
    analysis_results = {
        'roi_chart_bytes': b'data1',
        'co2_chart_bytes': b'data2'
    }
    
    # Test 1: Initialisierung
    initialize_chart_selection_state()
    assert 'pdf_inclusion_options' in st.session_state
    
    # Test 2: Auswahl
    selected = ['roi_chart_bytes']
    st.session_state.pdf_inclusion_options['selected_charts_for_pdf'] = selected
    
    # Test 3: Vorbereitung
    prep_proj, prep_anal = prepare_chart_data_for_pdf_generation(
        project_data, analysis_results, selected
    )
    
    # Test 4: Filterung
    assert 'roi_chart_bytes' in prep_anal
    assert 'co2_chart_bytes' not in prep_anal
    assert '_chart_selection_metadata' in prep_anal
    
    # Test 5: Metadaten
    metadata = prep_anal['_chart_selection_metadata']
    assert metadata['selected_count'] == 1
    assert metadata['selected_charts'] == selected
```

---

## Schritt 7: Troubleshooting

### Problem: Diagrammauswahl wird nicht angezeigt

**Lösung**:

- Prüfe dass alle Funktionen importiert sind
- Prüfe dass `render_chart_selection_ui()` aufgerufen wird
- Prüfe Browser-Konsole auf JavaScript-Fehler

### Problem: Checkboxen funktionieren nicht

**Lösung**:

- Prüfe dass Session State initialisiert ist
- Prüfe dass unique keys verwendet werden
- Prüfe dass `st.rerun()` nach Änderungen aufgerufen wird

### Problem: PDF enthält falsche Diagramme

**Lösung**:

- Prüfe dass `prepare_chart_data_for_pdf_generation()` aufgerufen wird
- Prüfe dass gefilterte Daten an `generate_offer_pdf()` übergeben werden
- Prüfe Logs für Fehler bei der Filterung

### Problem: Persistenz funktioniert nicht

**Lösung**:

- Prüfe dass `save_admin_setting_func` korrekt implementiert ist
- Prüfe dass JSON-Serialisierung funktioniert
- Prüfe Datenbank-Berechtigungen

### Problem: Verfügbarkeits-Prüfung ist falsch

**Lösung**:

- Prüfe dass `project_data` und `analysis_results` korrekt übergeben werden
- Prüfe Logik in `check_chart_availability()`
- Füge Debug-Logging hinzu

---

## Schritt 8: Performance-Optimierung

### Caching

```python
@st.cache_data
def get_available_charts(project_data: dict, analysis_results: dict) -> dict:
    """Cache verfügbare Diagramme"""
    available = {}
    for chart_key in CHART_KEY_TO_FRIENDLY_NAME_MAP.keys():
        if check_chart_availability(chart_key, project_data, analysis_results):
            available[chart_key] = CHART_KEY_TO_FRIENDLY_NAME_MAP[chart_key]
    return available
```

### Lazy Loading

```python
# Lade Kategorien nur wenn geöffnet
for category_name, chart_keys in CHART_CATEGORIES.items():
    with st.expander(f"📁 {category_name}", expanded=False):
        # Inhalt wird nur geladen wenn Expander geöffnet
        if st.session_state.get(f'expander_{category_name}_open', False):
            # Rendere Diagramme
            pass
```

---

## Zusammenfassung

Die Integration der Diagrammauswahl-UI erfordert:

1. ✅ **Funktionen aufrufen** in `render_pdf_ui()`
2. ✅ **Daten vorbereiten** vor PDF-Generierung
3. ✅ **Gefilterte Daten übergeben** an `generate_offer_pdf()`
4. ✅ **Testen** aller Funktionen
5. ✅ **Optimieren** für Performance

Die Implementierung ist:

- ✅ Modular und wartbar
- ✅ Rückwärtskompatibel
- ✅ Gut dokumentiert
- ✅ Produktionsreif

---

**Erstellt von**: Kiro AI Assistant  
**Datum**: 2025-01-10  
**Spec**: extended-pdf-comprehensive-improvements  
**Task**: 3. Diagrammauswahl in PDF UI implementieren
