# Design Document - 3D Visualisierung Fehlende Funktionen Wiederherstellen

## Overview

Die 3D-Visualisierung enthält umfangreichen Code (3282 Zeilen in solar_3d_view_module.py), aber die UI-Elemente werden nicht korrekt angezeigt. Das Problem liegt wahrscheinlich daran, dass:

1. Die Datei zu lang ist und möglicherweise abgeschnitten wird
2. Die Funktion `_render_3d_view_impl()` nicht vollständig ausgeführt wird
3. Es gibt Fehler im Code, die die Ausführung stoppen
4. Die UI-Elemente sind in Expandern versteckt, die nicht geöffnet werden

## Architecture

### Problemanalyse

Die Datei `solar_3d_view_module.py` ist extrem lang (3282 Zeilen). Dies kann zu folgenden Problemen führen:

1. **Performance-Probleme**: Streamlit muss die gesamte Datei bei jedem Rerun parsen
2. **Speicher-Probleme**: Große Session State Objekte können Probleme verursachen
3. **Code-Struktur**: Die Funktion `_render_3d_view_impl()` ist wahrscheinlich zu lang und komplex

### Lösungsansatz

Wir werden die Datei in mehrere kleinere Module aufteilen:

```
utils/
  pv3d_plotly.py          # Bereits vorhanden - 3D Rendering
  pv3d_ui_components.py   # NEU - UI-Komponenten
  pv3d_analysis.py        # NEU - Analyse-Funktionen
  pv3d_export.py          # NEU - Export-Funktionen
  pv3d_optimization.py    # NEU - Optimierungs-Funktionen

solar_3d_view_module.py   # Hauptdatei - nur Orchestrierung
```

## Components and Interfaces

### 1. pv3d_ui_components.py

Enthält alle UI-Rendering-Funktionen:

```python
def render_basis_settings(project_data: Dict) -> Dict[str, Any]:
    """Rendert Basis-Einstellungen Expander"""
    pass

def render_module_placement(project_data: Dict) -> Dict[str, Any]:
    """Rendert Modul-Belegung Expander"""
    pass

def render_advanced_controls(project_data: Dict) -> Dict[str, Any]:
    """Rendert Erweiterte Kontrolle Expander"""
    pass

def render_analysis_panel(project_data: Dict) -> Dict[str, Any]:
    """Rendert Analyse Expander"""
    pass

def render_export_options(project_data: Dict) -> Dict[str, Any]:
    """Rendert Export-Optionen Expander"""
    pass
```

### 2. pv3d_analysis.py

Enthält Analyse-Funktionen:

```python
def run_optimization_assistant(
    dims: BuildingDims,
    goal: str,
    constraints: Dict
) -> Dict[str, Any]:
    """Führt Optimierungs-Assistent aus"""
    pass

def calculate_shading_analysis(
    module_positions: List,
    time_of_day: float,
    date: datetime
) -> Dict[int, float]:
    """Berechnet Verschattung für alle Module"""
    pass

def calculate_yield_heatmap(
    module_positions: List,
    module_transforms: Dict,
    latitude: float
) -> Dict[int, float]:
    """Berechnet Ertrags-Heatmap"""
    pass
```

### 3. pv3d_export.py

Enthält Export-Funktionen:

```python
def export_screenshot(
    fig: go.Figure,
    format: str = "png"
) -> bytes:
    """Exportiert Screenshot"""
    pass

def export_multi_view(
    project_data: Dict,
    dims: BuildingDims,
    views: List[str]
) -> Dict[str, bytes]:
    """Exportiert Multi-View Screenshots"""
    pass

def export_360_animation(
    project_data: Dict,
    dims: BuildingDims,
    frames: int = 36
) -> bytes:
    """Exportiert 360° Animation"""
    pass
```

### 4. pv3d_optimization.py

Enthält Optimierungs-Logik:

```python
def optimize_layout(
    dims: BuildingDims,
    goal: str,
    constraints: Dict
) -> AdvancedLayoutConfig:
    """Optimiert Layout basierend auf Ziel"""
    pass

def evaluate_configuration(
    config: AdvancedLayoutConfig,
    dims: BuildingDims
) -> Dict[str, float]:
    """Bewertet eine Konfiguration"""
    pass
```

### 5. solar_3d_view_module.py (Refactored)

Hauptdatei wird stark vereinfacht:

```python
def render_3d_view():
    """Hauptfunktion - Orchestriert alle Komponenten"""
    
    # 1. Lade Daten
    project_data = load_project_data()
    
    # 2. Rendere UI-Komponenten
    basis_settings = render_basis_settings(project_data)
    module_settings = render_module_placement(project_data)
    advanced_settings = render_advanced_controls(project_data)
    analysis_settings = render_analysis_panel(project_data)
    export_settings = render_export_options(project_data)
    
    # 3. Erstelle 3D-Szene
    fig = build_plotly_scene(
        project_data=project_data,
        dims=basis_settings['dims'],
        roof_type=basis_settings['roof_type'],
        module_quantity=module_settings['quantity'],
        layout_config=advanced_settings['layout_config']
    )
    
    # 4. Zeige 3D-Szene
    st.plotly_chart(fig, use_container_width=True)
    
    # 5. Führe Analysen aus (falls aktiviert)
    if analysis_settings.get('run_optimization'):
        run_optimization_assistant(...)
    
    if analysis_settings.get('show_shading'):
        calculate_shading_analysis(...)
    
    if analysis_settings.get('show_heatmap'):
        calculate_yield_heatmap(...)
    
    # 6. Führe Exports aus (falls angefordert)
    if export_settings.get('export_screenshot'):
        export_screenshot(...)
```

## Data Models

### UI Settings Model

```python
@dataclass
class UISettings:
    # Basis
    building_length: float
    building_width: float
    building_height: float
    roof_type: str
    
    # Module
    layout_mode: str
    mounting_type: str
    use_garage: bool
    use_facade: bool
    
    # Erweitert
    enable_collision: bool
    selected_modules: List[int]
    
    # Analyse
    enable_optimization: bool
    optimization_goal: str
    enable_shading: bool
    enable_heatmap: bool
    
    # Export
    export_format: str
    export_resolution: Tuple[int, int]
```

## Error Handling

### Fehlerbehandlung auf mehreren Ebenen:

1. **Import-Fehler**: Graceful Fallback wenn Module fehlen
2. **Daten-Fehler**: Validierung aller Eingaben
3. **Rendering-Fehler**: Try-Catch um jeden UI-Block
4. **Export-Fehler**: Klare Fehlermeldungen für Benutzer

```python
def safe_render_component(render_func, component_name):
    """Wrapper für sichere UI-Komponenten-Rendering"""
    try:
        return render_func()
    except Exception as e:
        st.error(f"❌ Fehler beim Laden von {component_name}: {e}")
        return {}
```

## Testing Strategy

### Unit Tests

- Teste jede UI-Komponente isoliert
- Teste Analyse-Funktionen mit Mock-Daten
- Teste Export-Funktionen mit verschiedenen Formaten

### Integration Tests

- Teste vollständigen Workflow: Einstellungen → Rendering → Export
- Teste mit verschiedenen Dachformen und Modulanzahlen
- Teste Performance mit großen Anlagen (100+ Module)

### UI Tests

- Teste alle Expander öffnen/schließen
- Teste alle Buttons und Slider
- Teste Session State Persistenz

## Implementation Notes

### Prioritäten

1. **Phase 1**: Datei aufteilen und Basis-UI wiederherstellen
2. **Phase 2**: Analyse-Funktionen aktivieren
3. **Phase 3**: Export-Funktionen aktivieren
4. **Phase 4**: Optimierung und Performance

### Backwards Compatibility

- Alle bestehenden Session State Keys beibehalten
- Alte Konfigurationen müssen weiterhin funktionieren
- Keine Breaking Changes für PDF-Generator

### Performance Optimizations

- Caching für teure Berechnungen
- Lazy Loading für UI-Komponenten
- Debouncing für Slider-Inputs
- Async Export für große Dateien
