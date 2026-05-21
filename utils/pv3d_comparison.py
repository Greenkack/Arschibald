"""
Vergleichs-Modus für verschiedene PV-Konfigurationen

Dieses Modul ermöglicht den Side-by-Side Vergleich von zwei verschiedenen
PV-Modul-Konfigurationen mit synchronisierten Ansichten und Unterschieds-Hervorhebung.

Author: PV3D Team
Date: 2025-01-03
"""

from typing import Dict, Any, List, Tuple, Optional
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd


def create_comparison_view(
    config_a: Dict[str, Any],
    config_b: Dict[str, Any],
    sync_camera: bool = True
) -> go.Figure:
    """
    Erstellt Side-by-Side Vergleichsansicht für zwei Konfigurationen.
    
    Args:
        config_a: Konfiguration A (links) mit:
            - name: str - Name der Konfiguration
            - module_positions: List[Tuple[float, float, float]] - Modulpositionen
            - building_dims: Dict - Gebäudedimensionen
            - roof_type: str - Dachtyp
            - module_transforms: Dict - Modul-Transformationen (optional)
        config_b: Konfiguration B (rechts) - gleiche Struktur wie config_a
        sync_camera: bool - Kamera-Bewegungen zwischen Ansichten synchronisieren
    
    Returns:
        Plotly Figure mit 1x2 Subplot-Grid
    
    Example:
        >>> config_a = {
        ...     "name": "Optimiert für Ertrag",
        ...     "module_positions": [(0, 0, 0.3), (2, 0, 0.3)],
        ...     "building_dims": {"length": 10, "width": 8, "height": 5},
        ...     "roof_type": "Flachdach"
        ... }
        >>> config_b = {
        ...     "name": "Optimiert für Anzahl",
        ...     "module_positions": [(0, 0, 0.3), (1.5, 0, 0.3), (3, 0, 0.3)],
        ...     "building_dims": {"length": 10, "width": 8, "height": 5},
        ...     "roof_type": "Flachdach"
        ... }
        >>> fig = create_comparison_view(config_a, config_b)
    """
    # Erstelle 1x2 Subplot-Grid
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'scene'}, {'type': 'scene'}]],
        subplot_titles=(
            f"Konfiguration A: {config_a.get('name', 'Unbenannt')}",
            f"Konfiguration B: {config_b.get('name', 'Unbenannt')}"
        ),
        horizontal_spacing=0.05
    )
    
    # Rendere Konfiguration A (links)
    traces_a = _build_scene_traces(config_a)
    for trace in traces_a:
        fig.add_trace(trace, row=1, col=1)
    
    # Rendere Konfiguration B (rechts)
    traces_b = _build_scene_traces(config_b)
    for trace in traces_b:
        fig.add_trace(trace, row=1, col=2)
    
    # Synchronisiere Kamera wenn aktiviert
    if sync_camera:
        camera = dict(
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2),
                center=dict(x=0, y=0, z=0),
                up=dict(x=0, y=0, z=1)
            )
        )
        fig.update_layout(
            scene=camera,
            scene2=camera
        )
    
    # Layout-Anpassungen
    fig.update_layout(
        height=600,
        showlegend=False,
        title_text="Konfigurations-Vergleich",
        title_font_size=20,
        title_x=0.5
    )
    
    # Achsen-Einstellungen für beide Szenen
    axis_settings = dict(
        showbackground=True,
        backgroundcolor="rgb(230, 230, 230)",
        gridcolor="white",
        showgrid=True,
        zeroline=True
    )
    
    fig.update_scenes(
        xaxis=axis_settings,
        yaxis=axis_settings,
        zaxis=axis_settings,
        aspectmode='data'
    )
    
    return fig


def _build_scene_traces(config: Dict[str, Any]) -> List[go.Mesh3d]:
    """
    Erstellt alle 3D-Traces für eine Konfiguration.
    
    Args:
        config: Konfigurations-Dictionary
    
    Returns:
        Liste von Plotly Traces (Meshes)
    """
    from utils.pv3d_plotly import (
        create_complete_box,
        create_pv_module_3d
    )
    
    traces = []
    
    # Gebäude-Basis
    building_dims = config.get("building_dims", {})
    length = building_dims.get("length", 10.0)
    width = building_dims.get("width", 8.0)
    height = building_dims.get("height", 5.0)
    
    building_mesh = create_complete_box(
        x_min=-length/2, x_max=length/2,
        y_min=-width/2, y_max=width/2,
        z_min=0, z_max=height,
        color='#e0e0e0',
        name='Box'
    )
    traces.append(building_mesh)
    
    # PV-Module
    module_positions = config.get("module_positions", [])
    module_transforms = config.get("module_transforms", {})
    
    for i, (x, y, z) in enumerate(module_positions):
        transform = module_transforms.get(i, {})
        
        module_mesh, _ = create_pv_module_3d(
            x, y, z,
            azimuth_deg=transform.get("azimuth", 180.0),
            tilt_deg=transform.get("tilt", 30.0),
            color='#1a1a1a'
        )
        traces.append(module_mesh)
    
    return traces


def highlight_differences(
    fig: go.Figure,
    config_a: Dict[str, Any],
    config_b: Dict[str, Any],
    tolerance: float = 0.1
) -> go.Figure:
    """
    Hebt Unterschiede zwischen zwei Konfigurationen hervor.
    
    Markiert Module die nur in einer Konfiguration vorhanden sind:
    - Rot (X): Nur in Konfiguration A
    - Grün (O): Nur in Konfiguration B
    
    Args:
        fig: Plotly Figure mit Vergleichsansicht
        config_a: Konfiguration A
        config_b: Konfiguration B
        tolerance: Toleranz für Positions-Vergleich in Metern
    
    Returns:
        Aktualisierte Figure mit Unterschieds-Markierungen
    
    Example:
        >>> fig = create_comparison_view(config_a, config_b)
        >>> fig = highlight_differences(fig, config_a, config_b)
    """
    # Extrahiere Modulpositionen
    positions_a = config_a.get("module_positions", [])
    positions_b = config_b.get("module_positions", [])
    
    # Finde unterschiedliche Module (mit Toleranz)
    only_in_a = []
    only_in_b = list(positions_b)  # Kopie
    
    for pos_a in positions_a:
        found_match = False
        for pos_b in positions_b:
            if _positions_equal(pos_a, pos_b, tolerance):
                found_match = True
                if pos_b in only_in_b:
                    only_in_b.remove(pos_b)
                break
        
        if not found_match:
            only_in_a.append(pos_a)
    
    # Markiere Module die nur in A sind (rot, X)
    if only_in_a:
        x_coords = [pos[0] for pos in only_in_a]
        y_coords = [pos[1] for pos in only_in_a]
        z_coords = [pos[2] for pos in only_in_a]
        
        fig.add_trace(go.Scatter3d(
            x=x_coords, y=y_coords, z=z_coords,
            mode='markers',
            marker=dict(
                size=12,
                color='red',
                symbol='x',
                line=dict(width=2, color='darkred')
            ),
            name='Nur in A',
            showlegend=True,
            hovertemplate='<b>Nur in A</b><br>Position: (%{x:.2f}, %{y:.2f}, %{z:.2f})<extra></extra>'
        ), row=1, col=1)
    
    # Markiere Module die nur in B sind (grün, Kreis)
    if only_in_b:
        x_coords = [pos[0] for pos in only_in_b]
        y_coords = [pos[1] for pos in only_in_b]
        z_coords = [pos[2] for pos in only_in_b]
        
        fig.add_trace(go.Scatter3d(
            x=x_coords, y=y_coords, z=z_coords,
            mode='markers',
            marker=dict(
                size=12,
                color='green',
                symbol='circle',
                line=dict(width=2, color='darkgreen')
            ),
            name='Nur in B',
            showlegend=True,
            hovertemplate='<b>Nur in B</b><br>Position: (%{x:.2f}, %{y:.2f}, %{z:.2f})<extra></extra>'
        ), row=1, col=2)
    
    # Update Layout für Legende
    fig.update_layout(
        showlegend=True,
        legend=dict(
            x=0.5,
            y=-0.1,
            xanchor='center',
            yanchor='top',
            orientation='h'
        )
    )
    
    return fig


def _positions_equal(
    pos1: Tuple[float, float, float],
    pos2: Tuple[float, float, float],
    tolerance: float
) -> bool:
    """
    Prüft ob zwei Positionen innerhalb der Toleranz gleich sind.
    
    Args:
        pos1: Position 1 (x, y, z)
        pos2: Position 2 (x, y, z)
        tolerance: Maximale Abweichung in Metern
    
    Returns:
        True wenn Positionen gleich sind (innerhalb Toleranz)
    """
    distance = (
        (pos1[0] - pos2[0])**2 +
        (pos1[1] - pos2[1])**2 +
        (pos1[2] - pos2[2])**2
    )**0.5
    return distance <= tolerance


def create_comparison_table(
    config_a: Dict[str, Any],
    config_b: Dict[str, Any]
) -> pd.DataFrame:
    """
    Erstellt Vergleichstabelle mit Kennzahlen für beide Konfigurationen.
    
    Args:
        config_a: Konfiguration A mit Kennzahlen:
            - name: str
            - module_count: int
            - total_yield_kwh: float
            - total_cost_eur: float
            - roi_years: float
            - co2_savings_kg: float
        config_b: Konfiguration B (gleiche Struktur)
    
    Returns:
        Pandas DataFrame mit Vergleichstabelle
    
    Example:
        >>> df = create_comparison_table(config_a, config_b)
        >>> st.dataframe(df, use_container_width=True)
    """
    # Sammle Kennzahlen
    metrics = {
        "Metrik": [
            "Modulanzahl",
            "Gesamtertrag (kWh/Jahr)",
            "Kosten (€)",
            "ROI (Jahre)",
            "CO₂-Einsparung (kg/Jahr)",
            "Ertrag pro Modul (kWh)"
        ],
        config_a.get("name", "Konfiguration A"): [
            config_a.get("module_count", 0),
            config_a.get("total_yield_kwh", 0),
            config_a.get("total_cost_eur", 0),
            config_a.get("roi_years", 0),
            config_a.get("co2_savings_kg", 0),
            config_a.get("total_yield_kwh", 0) / max(config_a.get("module_count", 1), 1)
        ],
        config_b.get("name", "Konfiguration B"): [
            config_b.get("module_count", 0),
            config_b.get("total_yield_kwh", 0),
            config_b.get("total_cost_eur", 0),
            config_b.get("roi_years", 0),
            config_b.get("co2_savings_kg", 0),
            config_b.get("total_yield_kwh", 0) / max(config_b.get("module_count", 1), 1)
        ]
    }
    
    # Berechne Differenzen
    differences = []
    for i in range(len(metrics["Metrik"])):
        val_a = metrics[config_a.get("name", "Konfiguration A")][i]
        val_b = metrics[config_b.get("name", "Konfiguration B")][i]
        diff = val_b - val_a
        
        # Berechne prozentuale Differenz
        if val_a != 0:
            diff_percent = (diff / val_a) * 100
            differences.append(f"{diff:+.1f} ({diff_percent:+.1f}%)")
        else:
            differences.append(f"{diff:+.1f}")
    
    metrics["Differenz (B - A)"] = differences
    
    # Erstelle DataFrame
    df = pd.DataFrame(metrics)
    
    return df


def render_comparison_ui() -> Optional[Tuple[Dict[str, Any], Dict[str, Any]]]:
    """
    Rendert UI für Konfigurations-Vergleich.
    
    Ermöglicht Auswahl von zwei gespeicherten Konfigurationen zum Vergleich.
    
    Returns:
        Tuple (config_a, config_b) oder None wenn keine Auswahl
    
    Example:
        >>> configs = render_comparison_ui()
        >>> if configs:
        ...     config_a, config_b = configs
        ...     fig = create_comparison_view(config_a, config_b)
        ...     st.plotly_chart(fig)
    """
    st.sidebar.subheader("🔄 Konfigurations-Vergleich")
    
    # Hole gespeicherte Konfigurationen
    saved_configs = st.session_state.get("saved_configurations", {})
    
    if len(saved_configs) < 2:
        st.sidebar.warning("Mindestens 2 Konfigurationen erforderlich")
        return None
    
    config_names = list(saved_configs.keys())
    
    # Auswahl Konfiguration A
    config_a_name = st.sidebar.selectbox(
        "Konfiguration A",
        config_names,
        index=0,
        key="comparison_config_a"
    )
    
    # Auswahl Konfiguration B
    available_for_b = [name for name in config_names if name != config_a_name]
    config_b_name = st.sidebar.selectbox(
        "Konfiguration B",
        available_for_b,
        index=0,
        key="comparison_config_b"
    )
    
    # Optionen
    sync_camera = st.sidebar.checkbox(
        "Kamera synchronisieren",
        value=True,
        help="Synchronisiert Kamera-Bewegungen zwischen beiden Ansichten"
    )
    
    show_differences = st.sidebar.checkbox(
        "Unterschiede hervorheben",
        value=True,
        help="Markiert Module die nur in einer Konfiguration vorhanden sind"
    )
    
    # Speichere Optionen in Session State
    st.session_state["comparison_sync_camera"] = sync_camera
    st.session_state["comparison_show_differences"] = show_differences
    
    # Hole Konfigurationen
    config_a = saved_configs[config_a_name]
    config_b = saved_configs[config_b_name]
    
    return (config_a, config_b)


def save_configuration(
    name: str,
    module_positions: List[Tuple[float, float, float]],
    building_dims: Dict[str, float],
    roof_type: str,
    module_transforms: Optional[Dict[int, Dict[str, float]]] = None,
    metrics: Optional[Dict[str, float]] = None
) -> bool:
    """
    Speichert eine Konfiguration für späteren Vergleich.
    
    Args:
        name: Name der Konfiguration
        module_positions: Liste von Modulpositionen
        building_dims: Gebäudedimensionen
        roof_type: Dachtyp
        module_transforms: Modul-Transformationen (optional)
        metrics: Berechnete Kennzahlen (optional)
    
    Returns:
        True wenn erfolgreich gespeichert
    
    Example:
        >>> save_configuration(
        ...     name="Optimiert für Ertrag",
        ...     module_positions=[(0, 0, 0.3), (2, 0, 0.3)],
        ...     building_dims={"length": 10, "width": 8, "height": 5},
        ...     roof_type="Flachdach",
        ...     metrics={"total_yield_kwh": 5000, "module_count": 2}
        ... )
    """
    if "saved_configurations" not in st.session_state:
        st.session_state["saved_configurations"] = {}
    
    config = {
        "name": name,
        "module_positions": module_positions,
        "building_dims": building_dims,
        "roof_type": roof_type,
        "module_transforms": module_transforms or {},
        "module_count": len(module_positions),
        "saved_at": pd.Timestamp.now().isoformat()
    }
    
    # Füge Metriken hinzu wenn vorhanden
    if metrics:
        config.update(metrics)
    
    st.session_state["saved_configurations"][name] = config
    
    return True


def delete_configuration(name: str) -> bool:
    """
    Löscht eine gespeicherte Konfiguration.
    
    Args:
        name: Name der zu löschenden Konfiguration
    
    Returns:
        True wenn erfolgreich gelöscht
    """
    saved_configs = st.session_state.get("saved_configurations", {})
    
    if name in saved_configs:
        del saved_configs[name]
        st.session_state["saved_configurations"] = saved_configs
        return True
    
    return False


def list_saved_configurations() -> List[str]:
    """
    Gibt Liste aller gespeicherten Konfigurationen zurück.
    
    Returns:
        Liste von Konfigurations-Namen
    """
    saved_configs = st.session_state.get("saved_configurations", {})
    return list(saved_configs.keys())


def init_comparison_session_state() -> None:
    """
    Initialisiert Session State für Vergleichs-Modus.
    
    Sollte beim App-Start aufgerufen werden.
    """
    if "saved_configurations" not in st.session_state:
        st.session_state["saved_configurations"] = {}
    
    if "comparison_sync_camera" not in st.session_state:
        st.session_state["comparison_sync_camera"] = True
    
    if "comparison_show_differences" not in st.session_state:
        st.session_state["comparison_show_differences"] = True
