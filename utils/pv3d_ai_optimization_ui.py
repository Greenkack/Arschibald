"""
KI-Optimierung UI Komponente

Dieses Modul stellt UI-Komponenten für die KI-basierte Modul-Optimierung bereit.
Zeigt 3 Layout-Vorschläge mit Bewertungen und ermöglicht Auswahl und Anwendung.

Requirements: 7.1, 7.2, 7.4
"""

from typing import Dict, Any, Optional, List, Tuple
import streamlit as st

try:
    from utils.pv3d_ai_optimization import (
        AILayoutOptimizer,
        OptimizationResult,
        LayoutScore
    )
except ImportError:
    AILayoutOptimizer = None
    OptimizationResult = None
    LayoutScore = None


# ============================================================================
# HAUPTKOMPONENTE
# ============================================================================

def render_ai_optimization_ui(
    roof_length: float,
    roof_width: float,
    roof_type: str,
    roof_pitch: float = 0.0,
    module_width: float = 1.05,
    module_height: float = 1.76,
    module_power_w: float = 400.0,
    key_prefix: str = "ai_opt"
) -> Optional[OptimizationResult]:
    """
    Rendert KI-Optimierung UI mit 3 Layout-Vorschlägen.
    
    Diese Funktion zeigt drei verschiedene Optimierungs-Strategien:
    1. Maximaler Ertrag
    2. Maximale Anzahl
    3. Beste Ästhetik
    
    Für jede Strategie wird eine Bewertung angezeigt und der Benutzer
    kann ein Layout auswählen und anwenden.
    
    Args:
        roof_length: Dachlänge in Metern
        roof_width: Dachbreite in Metern
        roof_type: Dachtyp (z.B. "Flachdach", "Satteldach")
        roof_pitch: Dachneigung in Grad
        module_width: Modulbreite in Metern
        module_height: Modulhöhe in Metern
        module_power_w: Modulleistung in Watt
        key_prefix: Prefix für Streamlit Widget-Keys
    
    Returns:
        Ausgewähltes OptimizationResult oder None
    
    Requirements:
        - 7.1: KI-Optimierung mit 3 Strategien
        - 7.2: Bewertung für jedes Layout
        - 7.4: Auswahl und Anwendung
    
    Example:
        >>> result = render_ai_optimization_ui(
        >>>     roof_length=10.0,
        >>>     roof_width=8.0,
        >>>     roof_type="Satteldach",
        >>>     roof_pitch=30.0
        >>> )
        >>> if result:
        >>>     st.success(f"{result.score.module_count} Module platziert!")
    """
    if AILayoutOptimizer is None:
        st.error("❌ KI-Optimierung nicht verfügbar (Import-Fehler)")
        return None
    
    st.markdown("### 🤖 KI-Optimierung")
    st.markdown(
        "Die KI schlägt drei verschiedene Layouts vor, "
        "optimiert für unterschiedliche Ziele."
    )
    
    # Erstelle Optimierer
    optimizer = AILayoutOptimizer(
        roof_length=roof_length,
        roof_width=roof_width,
        roof_type=roof_type,
        roof_pitch=roof_pitch,
        module_width=module_width,
        module_height=module_height,
        module_power_w=module_power_w
    )
    
    # Berechne Optimierungen (mit Caching)
    with st.spinner("🔄 KI berechnet optimale Layouts..."):
        results = _calculate_optimizations(optimizer, key_prefix)
    
    if not results:
        st.error("❌ Fehler bei der Optimierung")
        return None
    
    # Zeige 3 Layout-Vorschläge
    st.markdown("---")
    st.markdown("#### 📊 Layout-Vorschläge")
    
    # Erstelle 3 Spalten für die Vorschläge
    col1, col2, col3 = st.columns(3)
    
    selected_result = None
    
    # Vorschlag 1: Maximaler Ertrag
    with col1:
        if _render_layout_proposal(
            result=results["max_yield"],
            title="💰 Maximaler Ertrag",
            icon="💰",
            color="#27ae60",
            key_prefix=f"{key_prefix}_yield"
        ):
            selected_result = results["max_yield"]
    
    # Vorschlag 2: Maximale Anzahl
    with col2:
        if _render_layout_proposal(
            result=results["max_count"],
            title="📦 Maximale Anzahl",
            icon="📦",
            color="#3498db",
            key_prefix=f"{key_prefix}_count"
        ):
            selected_result = results["max_count"]
    
    # Vorschlag 3: Beste Ästhetik
    with col3:
        if _render_layout_proposal(
            result=results["aesthetics"],
            title="✨ Beste Ästhetik",
            icon="✨",
            color="#9b59b6",
            key_prefix=f"{key_prefix}_aesthetics"
        ):
            selected_result = results["aesthetics"]
    
    # Zeige Vergleichstabelle
    st.markdown("---")
    _render_comparison_table(results)
    
    # Wenn Layout ausgewählt wurde
    if selected_result:
        st.markdown("---")
        _render_apply_section(selected_result, key_prefix)
    
    return selected_result


# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def _calculate_optimizations(
    optimizer: 'AILayoutOptimizer',
    key_prefix: str
) -> Dict[str, OptimizationResult]:
    """
    Berechnet alle 3 Optimierungen mit Caching.
    
    Args:
        optimizer: AILayoutOptimizer Instanz
        key_prefix: Prefix für Cache-Key
    
    Returns:
        Dictionary mit 3 OptimizationResults
    """
    # Cache-Key basierend auf Dach-Parametern
    cache_key = f"{key_prefix}_optimizations_{optimizer.roof_length}_{optimizer.roof_width}_{optimizer.roof_type}_{optimizer.roof_pitch}"
    
    # Prüfe Cache
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    
    try:
        # Berechne alle 3 Optimierungen
        results = {
            "max_yield": optimizer.optimize_for_max_yield(),
            "max_count": optimizer.optimize_for_max_count(),
            "aesthetics": optimizer.optimize_for_aesthetics()
        }
        
        # Speichere in Cache
        st.session_state[cache_key] = results
        
        return results
    
    except Exception as e:
        st.error(f"❌ Fehler bei Optimierung: {str(e)}")
        return {}


def _render_layout_proposal(
    result: OptimizationResult,
    title: str,
    icon: str,
    color: str,
    key_prefix: str
) -> bool:
    """
    Rendert einen einzelnen Layout-Vorschlag.
    
    Args:
        result: OptimizationResult
        title: Titel des Vorschlags
        icon: Emoji-Icon
        color: Farbe für Hervorhebung
        key_prefix: Prefix für Widget-Keys
    
    Returns:
        True wenn ausgewählt, False sonst
    
    Requirements:
        - 7.2: Bewertung anzeigen
    """
    # Container mit Rahmen
    with st.container():
        # Header mit Icon und Titel
        st.markdown(
            f'<div style="background-color: {color}; padding: 10px; '
            f'border-radius: 10px 10px 0 0; text-align: center;">'
            f'<h3 style="color: white; margin: 0;">{icon} {result.strategy}</h3>'
            f'</div>',
            unsafe_allow_html=True
        )
        
        # Bewertungs-Karte
        st.markdown(
            '<div style="border: 2px solid ' + color + '; '
            'border-radius: 0 0 10px 10px; padding: 15px; '
            'background-color: rgba(255, 255, 255, 0.05);">',
            unsafe_allow_html=True
        )
        
        # Hauptmetriken
        st.metric(
            label="Module",
            value=f"{result.score.module_count}",
            delta=None
        )
        
        st.metric(
            label="Jahresertrag",
            value=f"{result.score.total_yield_kwh:,.0f} kWh",
            delta=None
        )
        
        st.metric(
            label="ROI",
            value=f"{result.score.roi_years:.1f} Jahre",
            delta=None
        )
        
        # Zusätzliche Metriken
        st.caption(f"💰 Kosten: {result.score.cost_eur:,.0f} €")
        st.caption(f"📐 Dachnutzung: {result.score.coverage_percent:.1f}%")
        st.caption(f"✨ Ästhetik: {result.score.aesthetic_score:.0f}/100")
        st.caption(f"🔄 Symmetrie: {result.score.symmetry_score:.0f}/100")
        
        # Gesamtbewertung
        total_score = result.score.get_weighted_score()
        st.progress(total_score / 100)
        st.caption(f"**Gesamtbewertung: {total_score:.0f}/100**")
        
        # Auswahl-Button
        selected = st.button(
            "✓ Auswählen",
            key=f"{key_prefix}_select",
            type="primary",
            use_container_width=True
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return selected


def _render_comparison_table(results: Dict[str, OptimizationResult]) -> None:
    """
    Rendert Vergleichstabelle für alle 3 Layouts.
    
    Args:
        results: Dictionary mit OptimizationResults
    
    Requirements:
        - 7.2: Bewertung für jedes Layout
    """
    st.markdown("#### 📊 Vergleichstabelle")
    
    # Erstelle Tabellen-Daten
    data = {
        "Strategie": [],
        "Module": [],
        "Ertrag (kWh/Jahr)": [],
        "Kosten (€)": [],
        "ROI (Jahre)": [],
        "Dachnutzung (%)": [],
        "Ästhetik": [],
        "Gesamtbewertung": []
    }
    
    for key, result in results.items():
        data["Strategie"].append(result.strategy)
        data["Module"].append(result.score.module_count)
        data["Ertrag (kWh/Jahr)"].append(f"{result.score.total_yield_kwh:,.0f}")
        data["Kosten (€)"].append(f"{result.score.cost_eur:,.0f}")
        data["ROI (Jahre)"].append(f"{result.score.roi_years:.1f}")
        data["Dachnutzung (%)"].append(f"{result.score.coverage_percent:.1f}")
        data["Ästhetik"].append(f"{result.score.aesthetic_score:.0f}/100")
        data["Gesamtbewertung"].append(f"{result.score.get_weighted_score():.0f}/100")
    
    # Zeige Tabelle
    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True
    )


def _render_apply_section(
    result: OptimizationResult,
    key_prefix: str
) -> None:
    """
    Rendert Anwendungs-Sektion für ausgewähltes Layout.
    
    Args:
        result: Ausgewähltes OptimizationResult
        key_prefix: Prefix für Widget-Keys
    
    Requirements:
        - 7.4: Auswahl und Anwendung
    """
    st.markdown("### ✅ Layout ausgewählt")
    
    # Zeige Zusammenfassung
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Strategie", result.strategy)
    
    with col2:
        st.metric("Module", result.score.module_count)
    
    with col3:
        st.metric("Ertrag", f"{result.score.total_yield_kwh:,.0f} kWh")
    
    # Anwendungs-Optionen
    st.markdown("#### ⚙️ Anwendungs-Optionen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        animate = st.checkbox(
            "Mit Animation anwenden",
            value=True,
            key=f"{key_prefix}_animate",
            help="Module werden nacheinander platziert"
        )
    
    with col2:
        animation_speed = st.slider(
            "Animations-Geschwindigkeit",
            min_value=1,
            max_value=10,
            value=5,
            key=f"{key_prefix}_speed",
            help="1 = langsam, 10 = schnell",
            disabled=not animate
        )
    
    # Anwenden-Button
    if st.button(
        "🚀 Layout anwenden",
        key=f"{key_prefix}_apply",
        type="primary",
        use_container_width=True
    ):
        _apply_layout(result, animate, animation_speed)


def _apply_layout(
    result: OptimizationResult,
    animate: bool,
    animation_speed: int
) -> None:
    """
    Wendet ausgewähltes Layout an.
    
    Args:
        result: OptimizationResult zum Anwenden
        animate: Ob Animation verwendet werden soll
        animation_speed: Geschwindigkeit der Animation (1-10)
    
    Requirements:
        - 7.4: Animierte Layout-Anwendung
    """
    # Speichere Positionen in Session State
    st.session_state["placed_module_positions"] = result.positions
    st.session_state["placed_module_count"] = len(result.positions)
    
    # Speichere Metadaten
    st.session_state["ai_optimization_applied"] = True
    st.session_state["ai_optimization_strategy"] = result.strategy
    st.session_state["ai_optimization_score"] = result.score
    
    # Animation-Einstellungen
    if animate:
        st.session_state["apply_animation"] = True
        st.session_state["animation_speed"] = animation_speed
        st.session_state["animation_current_index"] = 0
    
    # Erfolgs-Meldung
    st.success(
        f"✅ Layout '{result.strategy}' erfolgreich angewendet! "
        f"{len(result.positions)} Module platziert."
    )
    
    # Zeige Statistiken
    st.info(
        f"📊 **Erwarteter Jahresertrag:** {result.score.total_yield_kwh:,.0f} kWh\n\n"
        f"💰 **Geschätzte Kosten:** {result.score.cost_eur:,.0f} €\n\n"
        f"⏱️ **ROI:** {result.score.roi_years:.1f} Jahre"
    )
    
    # Rerun um Visualisierung zu aktualisieren
    st.rerun()


# ============================================================================
# ZUSÄTZLICHE UI-KOMPONENTEN
# ============================================================================

def render_ai_optimization_info() -> None:
    """
    Rendert Info-Panel über KI-Optimierung.
    
    Zeigt Erklärung der drei Strategien.
    
    Example:
        >>> with st.sidebar:
        >>>     render_ai_optimization_info()
    """
    st.markdown("### 🤖 KI-Optimierung")
    
    with st.expander("ℹ️ Wie funktioniert die KI-Optimierung?"):
        st.markdown("""
        Die KI analysiert Ihr Dach und schlägt drei optimierte Layouts vor:
        
        **💰 Maximaler Ertrag**
        - Platziert Module an Positionen mit bester Sonneneinstrahlung
        - Vermeidet verschattete Bereiche
        - Optimale Ausrichtung für maximalen Ertrag
        
        **📦 Maximale Anzahl**
        - Dichte Packung mit minimalem Abstand (5cm)
        - Nutzt gesamte verfügbare Dachfläche
        - Maximiert Anzahl der Module
        
        **✨ Beste Ästhetik**
        - Symmetrische Anordnung
        - Gleichmäßige Abstände (20cm)
        - Zentrierte Platzierung
        - Harmonisches Gesamtbild
        
        Jedes Layout wird nach mehreren Kriterien bewertet:
        - Ertrag (kWh/Jahr)
        - Anzahl Module
        - Kosten und ROI
        - Ästhetik und Symmetrie
        """)


def render_ai_optimization_status() -> None:
    """
    Rendert Status-Panel für angewendete KI-Optimierung.
    
    Zeigt welche Strategie aktuell angewendet ist.
    
    Example:
        >>> if st.session_state.get("ai_optimization_applied"):
        >>>     render_ai_optimization_status()
    """
    if not st.session_state.get("ai_optimization_applied"):
        return
    
    strategy = st.session_state.get("ai_optimization_strategy", "Unbekannt")
    score = st.session_state.get("ai_optimization_score")
    
    st.markdown("### ✅ KI-Optimierung aktiv")
    
    with st.container():
        st.info(
            f"**Strategie:** {strategy}\n\n"
            f"**Module:** {score.module_count if score else 'N/A'}\n\n"
            f"**Ertrag:** {score.total_yield_kwh:,.0f} kWh/Jahr" if score else "N/A"
        )
        
        if st.button("🔄 Neue Optimierung", key="reset_ai_opt"):
            st.session_state["ai_optimization_applied"] = False
            st.session_state["ai_optimization_strategy"] = None
            st.session_state["ai_optimization_score"] = None
            st.rerun()


def render_ai_optimization_animation() -> bool:
    """
    Rendert Animation für Layout-Anwendung.
    
    Zeigt Module nacheinander an (animiert).
    
    Returns:
        True wenn Animation läuft, False wenn fertig
    
    Requirements:
        - 7.4: Animierte Layout-Anwendung
    
    Example:
        >>> if render_ai_optimization_animation():
        >>>     st.info("Animation läuft...")
    """
    if not st.session_state.get("apply_animation"):
        return False
    
    positions = st.session_state.get("placed_module_positions", [])
    current_index = st.session_state.get("animation_current_index", 0)
    speed = st.session_state.get("animation_speed", 5)
    
    if current_index >= len(positions):
        # Animation fertig
        st.session_state["apply_animation"] = False
        st.session_state["animation_current_index"] = 0
        return False
    
    # Zeige Fortschritt
    progress = (current_index + 1) / len(positions)
    st.progress(progress)
    st.caption(f"Platziere Modul {current_index + 1} von {len(positions)}...")
    
    # Erhöhe Index für nächsten Frame
    # Geschwindigkeit: 1 = 1 Modul pro Frame, 10 = 10 Module pro Frame
    st.session_state["animation_current_index"] = min(
        current_index + speed,
        len(positions)
    )
    
    # Trigger Rerun für nächsten Frame
    import time
    time.sleep(0.1)  # Kurze Pause zwischen Frames
    st.rerun()
    
    return True
