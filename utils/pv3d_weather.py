"""
Realistische Wetter-Simulation für 3D-PV-Visualisierung

Dieses Modul implementiert ein Wetter-System mit verschiedenen Wetterbedingungen
(Sonnig, Bewölkt, Regen, Schnee, Nebel) und deren Auswirkungen auf die
3D-Visualisierung und den PV-Ertrag.

Author: PV3D Team
Date: 2025-01-03
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field
import plotly.graph_objects as go
import numpy as np
import streamlit as st


@dataclass
class WeatherCondition:
    """
    Definiert Wetterbedingungen und deren Auswirkungen.
    
    Attributes:
        name: Anzeigename der Wetterbedingung
        sky_color: Himmel-Farbe als Hex-Code
        ambient_light: Umgebungslicht-Intensität (0-1)
        sun_intensity: Direkte Sonnenintensität (0-1)
        diffuse_factor: Diffuse Strahlungs-Faktor (0-1)
        yield_factor: Ertragsfaktor relativ zu optimalen Bedingungen (0-1)
        particles: Ob Partikel-Effekte (Regen/Schnee) angezeigt werden
        visibility_km: Sichtweite in Kilometern
        description: Beschreibung der Wetterbedingung
    """
    name: str
    sky_color: str
    ambient_light: float
    sun_intensity: float
    diffuse_factor: float
    yield_factor: float
    particles: bool = False
    visibility_km: float = 50.0
    description: str = ""
    
    def __post_init__(self):
        """Validiert Werte nach Initialisierung."""
        assert 0.0 <= self.ambient_light <= 1.0, "ambient_light muss zwischen 0 und 1 liegen"
        assert 0.0 <= self.sun_intensity <= 1.0, "sun_intensity muss zwischen 0 und 1 liegen"
        assert 0.0 <= self.diffuse_factor <= 1.0, "diffuse_factor muss zwischen 0 und 1 liegen"
        assert 0.0 <= self.yield_factor <= 1.0, "yield_factor muss zwischen 0 und 1 liegen"
        assert self.visibility_km > 0, "visibility_km muss positiv sein"


# Vordefinierte Wetterbedingungen
WEATHER_CONDITIONS: Dict[str, WeatherCondition] = {
    "sonnig": WeatherCondition(
        name="Sonnig ☀️",
        sky_color="#87CEEB",  # Sky Blue
        ambient_light=0.8,
        sun_intensity=1.0,
        diffuse_factor=0.2,
        yield_factor=1.0,
        particles=False,
        visibility_km=50.0,
        description="Klarer Himmel, optimale Bedingungen für PV-Ertrag"
    ),
    "bewoelkt": WeatherCondition(
        name="Bewölkt ☁️",
        sky_color="#B0C4DE",  # Light Steel Blue
        ambient_light=0.6,
        sun_intensity=0.4,
        diffuse_factor=0.8,
        yield_factor=0.6,
        particles=False,
        visibility_km=30.0,
        description="Bedeckter Himmel, reduzierte direkte Sonneneinstrahlung"
    ),
    "regen": WeatherCondition(
        name="Regen 🌧️",
        sky_color="#778899",  # Light Slate Gray
        ambient_light=0.4,
        sun_intensity=0.2,
        diffuse_factor=0.9,
        yield_factor=0.3,
        particles=True,
        visibility_km=10.0,
        description="Regenwetter, stark reduzierte Sonneneinstrahlung"
    ),
    "schnee": WeatherCondition(
        name="Schnee ❄️",
        sky_color="#F0F8FF",  # Alice Blue
        ambient_light=0.7,
        sun_intensity=0.3,
        diffuse_factor=0.85,
        yield_factor=0.1,  # Schneebedeckung reduziert Ertrag stark
        particles=True,
        visibility_km=5.0,
        description="Schneefall, Module können bedeckt sein"
    ),
    "nebel": WeatherCondition(
        name="Nebel 🌫️",
        sky_color="#DCDCDC",  # Gainsboro
        ambient_light=0.5,
        sun_intensity=0.1,
        diffuse_factor=0.95,
        yield_factor=0.2,
        particles=False,
        visibility_km=1.0,
        description="Dichter Nebel, sehr geringe Sichtweite"
    )
}


def get_weather_condition(weather_key: str) -> WeatherCondition:
    """
    Gibt WeatherCondition für gegebenen Schlüssel zurück.
    
    Args:
        weather_key: Schlüssel der Wetterbedingung (z.B. "sonnig")
    
    Returns:
        WeatherCondition Objekt
    
    Raises:
        KeyError: Wenn weather_key nicht existiert
    """
    if weather_key not in WEATHER_CONDITIONS:
        raise KeyError(
            f"Unbekannte Wetterbedingung: {weather_key}. "
            f"Verfügbar: {list(WEATHER_CONDITIONS.keys())}"
        )
    return WEATHER_CONDITIONS[weather_key]


def get_all_weather_conditions() -> Dict[str, WeatherCondition]:
    """
    Gibt alle verfügbaren Wetterbedingungen zurück.
    
    Returns:
        Dictionary mit allen WeatherCondition Objekten
    """
    return WEATHER_CONDITIONS.copy()


def apply_weather_to_scene(
    fig: go.Figure,
    weather_key: str = "sonnig",
    building_center: Tuple[float, float, float] = (0.0, 0.0, 0.0)
) -> go.Figure:
    """
    Wendet Wetterbedingungen auf 3D-Szene an.
    
    Ändert Hintergrundfarbe, Beleuchtung und fügt optional
    Partikel-Effekte (Regen/Schnee) hinzu.
    
    Args:
        fig: Plotly Figure Objekt
        weather_key: Schlüssel der Wetterbedingung
        building_center: Zentrum des Gebäudes für Partikel-Platzierung
    
    Returns:
        Modifizierte Plotly Figure
    """
    try:
        weather = get_weather_condition(weather_key)
    except KeyError:
        st.warning(f"Unbekannte Wetterbedingung '{weather_key}', verwende 'sonnig'")
        weather = WEATHER_CONDITIONS["sonnig"]
    
    # Update Hintergrundfarbe (Himmel)
    fig.update_layout(
        scene=dict(
            bgcolor=weather.sky_color,
            xaxis=dict(
                backgroundcolor=weather.sky_color,
                gridcolor="rgba(255, 255, 255, 0.2)"
            ),
            yaxis=dict(
                backgroundcolor=weather.sky_color,
                gridcolor="rgba(255, 255, 255, 0.2)"
            ),
            zaxis=dict(
                backgroundcolor=weather.sky_color,
                gridcolor="rgba(255, 255, 255, 0.2)"
            )
        )
    )
    
    # Update Beleuchtung aller Meshes
    for trace in fig.data:
        if hasattr(trace, 'lighting') and isinstance(trace, go.Mesh3d):
            trace.lighting = dict(
                ambient=weather.ambient_light,
                diffuse=weather.diffuse_factor,
                specular=0.5 * weather.sun_intensity,
                roughness=0.3,
                fresnel=0.2
            )
    
    # Füge Partikel-Effekte hinzu
    if weather.particles:
        if weather_key == "regen":
            fig = add_rain_particles(fig, building_center)
        elif weather_key == "schnee":
            fig = add_snow_particles(fig, building_center)
    
    return fig


def add_rain_particles(
    fig: go.Figure,
    building_center: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    n_drops: int = 200,
    area_size: float = 30.0
) -> go.Figure:
    """
    Fügt Regen-Partikel zur Szene hinzu.
    
    Args:
        fig: Plotly Figure Objekt
        building_center: Zentrum des Gebäudes
        n_drops: Anzahl der Regentropfen
        area_size: Größe des Regen-Bereichs in Metern
    
    Returns:
        Figure mit Regen-Partikeln
    """
    cx, cy, cz = building_center
    
    # Generiere Regentropfen zufällig verteilt
    x = np.random.uniform(cx - area_size/2, cx + area_size/2, n_drops)
    y = np.random.uniform(cy - area_size/2, cy + area_size/2, n_drops)
    z = np.random.uniform(cz + 5, cz + 20, n_drops)  # Über dem Gebäude
    
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers',
        marker=dict(
            size=2,
            color='rgba(100, 150, 200, 0.5)',
            symbol='diamond',
            line=dict(width=0)
        ),
        name='Regen',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    return fig


def add_snow_particles(
    fig: go.Figure,
    building_center: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    n_flakes: int = 150,
    area_size: float = 30.0
) -> go.Figure:
    """
    Fügt Schnee-Partikel zur Szene hinzu.
    
    Args:
        fig: Plotly Figure Objekt
        building_center: Zentrum des Gebäudes
        n_flakes: Anzahl der Schneeflocken
        area_size: Größe des Schnee-Bereichs in Metern
    
    Returns:
        Figure mit Schnee-Partikeln
    """
    cx, cy, cz = building_center
    
    # Generiere Schneeflocken zufällig verteilt
    x = np.random.uniform(cx - area_size/2, cx + area_size/2, n_flakes)
    y = np.random.uniform(cy - area_size/2, cy + area_size/2, n_flakes)
    z = np.random.uniform(cz + 5, cz + 20, n_flakes)  # Über dem Gebäude
    
    # Verschiedene Größen für realistischeren Effekt
    sizes = np.random.uniform(2, 4, n_flakes)
    
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers',
        marker=dict(
            size=sizes,
            color='rgba(255, 255, 255, 0.8)',
            symbol='circle',
            line=dict(width=0)
        ),
        name='Schnee',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    return fig


def calculate_weather_yield_impact(
    base_yield_kwh: float,
    weather_key: str
) -> Dict[str, float]:
    """
    Berechnet Ertragsverlust durch Wetterbedingungen.
    
    Args:
        base_yield_kwh: Basis-Ertrag unter optimalen Bedingungen
        weather_key: Schlüssel der Wetterbedingung
    
    Returns:
        Dictionary mit:
            - base_yield: Basis-Ertrag (kWh)
            - weather_factor: Wetter-Faktor (0-1)
            - actual_yield: Tatsächlicher Ertrag (kWh)
            - loss_kwh: Verlust in kWh
            - loss_percent: Verlust in Prozent
    """
    try:
        weather = get_weather_condition(weather_key)
    except KeyError:
        weather = WEATHER_CONDITIONS["sonnig"]
    
    actual_yield = base_yield_kwh * weather.yield_factor
    loss_kwh = base_yield_kwh - actual_yield
    loss_percent = (1 - weather.yield_factor) * 100
    
    return {
        "base_yield": base_yield_kwh,
        "weather_factor": weather.yield_factor,
        "actual_yield": actual_yield,
        "loss_kwh": loss_kwh,
        "loss_percent": loss_percent
    }


def calculate_weather_yield_impact_multiple(
    base_yields_kwh: List[float],
    weather_key: str
) -> List[Dict[str, float]]:
    """
    Berechnet Ertragsverlust für mehrere Module.
    
    Args:
        base_yields_kwh: Liste von Basis-Erträgen für jedes Modul
        weather_key: Schlüssel der Wetterbedingung
    
    Returns:
        Liste von Dictionaries mit Ertrags-Daten pro Modul
    """
    return [
        calculate_weather_yield_impact(yield_val, weather_key)
        for yield_val in base_yields_kwh
    ]


def get_weather_statistics(weather_key: str) -> Dict[str, Any]:
    """
    Gibt detaillierte Statistiken für eine Wetterbedingung zurück.
    
    Args:
        weather_key: Schlüssel der Wetterbedingung
    
    Returns:
        Dictionary mit Statistiken
    """
    try:
        weather = get_weather_condition(weather_key)
    except KeyError:
        return {"error": f"Unbekannte Wetterbedingung: {weather_key}"}
    
    return {
        "name": weather.name,
        "description": weather.description,
        "sky_color": weather.sky_color,
        "ambient_light_percent": weather.ambient_light * 100,
        "sun_intensity_percent": weather.sun_intensity * 100,
        "diffuse_factor_percent": weather.diffuse_factor * 100,
        "yield_factor_percent": weather.yield_factor * 100,
        "has_particles": weather.particles,
        "visibility_km": weather.visibility_km
    }


def simulate_annual_weather_distribution() -> Dict[str, float]:
    """
    Simuliert realistische Wetter-Verteilung über ein Jahr.
    
    Basiert auf durchschnittlichen Wetterdaten für Deutschland.
    
    Returns:
        Dictionary mit Anzahl Tage pro Wetterbedingung
    """
    # Durchschnittliche Verteilung für Deutschland
    return {
        "sonnig": 80,      # ~22% sonnige Tage
        "bewoelkt": 150,   # ~41% bewölkte Tage
        "regen": 100,      # ~27% Regentage
        "schnee": 20,      # ~5% Schneetage
        "nebel": 15        # ~4% Nebeltage
    }


def calculate_annual_weather_adjusted_yield(
    base_annual_yield_kwh: float,
    weather_distribution: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Berechnet wetter-adjustierten Jahresertrag.
    
    Args:
        base_annual_yield_kwh: Basis-Jahresertrag unter optimalen Bedingungen
        weather_distribution: Optionale benutzerdefinierte Wetter-Verteilung
    
    Returns:
        Dictionary mit:
            - base_annual_yield: Basis-Jahresertrag
            - weather_adjusted_yield: Wetter-adjustierter Ertrag
            - total_loss_kwh: Gesamtverlust
            - total_loss_percent: Gesamtverlust in Prozent
            - breakdown_by_weather: Aufschlüsselung nach Wetterbedingung
    """
    if weather_distribution is None:
        weather_distribution = simulate_annual_weather_distribution()
    
    total_days = sum(weather_distribution.values())
    daily_base_yield = base_annual_yield_kwh / 365
    
    weather_adjusted_yield = 0.0
    breakdown = {}
    
    for weather_key, days in weather_distribution.items():
        try:
            weather = get_weather_condition(weather_key)
            daily_yield = daily_base_yield * weather.yield_factor
            total_yield_for_weather = daily_yield * days
            weather_adjusted_yield += total_yield_for_weather
            
            breakdown[weather_key] = {
                "days": days,
                "yield_factor": weather.yield_factor,
                "total_yield_kwh": total_yield_for_weather,
                "avg_daily_yield_kwh": daily_yield
            }
        except KeyError:
            continue
    
    total_loss_kwh = base_annual_yield_kwh - weather_adjusted_yield
    total_loss_percent = (total_loss_kwh / base_annual_yield_kwh) * 100
    
    return {
        "base_annual_yield": base_annual_yield_kwh,
        "weather_adjusted_yield": weather_adjusted_yield,
        "total_loss_kwh": total_loss_kwh,
        "total_loss_percent": total_loss_percent,
        "breakdown_by_weather": breakdown,
        "total_days_simulated": total_days
    }


# Hilfsfunktionen für Session State Integration
def init_weather_session_state() -> None:
    """Initialisiert Wetter-bezogene Session State Variablen."""
    if "current_weather" not in st.session_state:
        st.session_state["current_weather"] = "sonnig"
    
    if "weather_history" not in st.session_state:
        st.session_state["weather_history"] = []


def set_current_weather(weather_key: str) -> bool:
    """
    Setzt aktuelle Wetterbedingung in Session State.
    
    Args:
        weather_key: Schlüssel der Wetterbedingung
    
    Returns:
        True wenn erfolgreich, False bei ungültigem Schlüssel
    """
    if weather_key not in WEATHER_CONDITIONS:
        return False
    
    st.session_state["current_weather"] = weather_key
    
    # Füge zu Historie hinzu
    if "weather_history" not in st.session_state:
        st.session_state["weather_history"] = []
    
    st.session_state["weather_history"].append({
        "weather": weather_key,
        "timestamp": st.session_state.get("current_timestamp", 0)
    })
    
    return True


def get_current_weather() -> str:
    """
    Gibt aktuelle Wetterbedingung aus Session State zurück.
    
    Returns:
        Schlüssel der aktuellen Wetterbedingung
    """
    return st.session_state.get("current_weather", "sonnig")
