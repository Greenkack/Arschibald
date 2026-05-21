"""
Video-Export-System für 3D-PV-Visualisierung

Dieses Modul ermöglicht den Export von Zeitraffer-Videos der 3D-Visualisierung
in verschiedenen Formaten (MP4, GIF, WebM) und Auflösungen.

Author: PV3D Team
Date: 2025-01-03
"""

from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import os
import tempfile
import streamlit as st


@dataclass
class VideoExportConfig:
    """
    Konfiguration für Video-Export.
    
    Attributes:
        mode: Zeitraffer-Modus ("day", "year", "custom")
        duration_seconds: Video-Länge in Sekunden
        resolution: Video-Auflösung ("720p", "1080p", "4K")
        format: Video-Format ("mp4", "gif", "webm")
        fps: Frames pro Sekunde
        show_overlays: Text-Overlays anzeigen
        output_path: Ausgabe-Pfad
    """
    mode: str = "day"
    duration_seconds: int = 30
    resolution: str = "1080p"
    format: str = "mp4"
    fps: int = 24
    show_overlays: bool = True
    output_path: str = "timelapse.mp4"
    
    def __post_init__(self):
        """Validiert Konfiguration."""
        valid_modes = ["day", "year", "custom"]
        assert self.mode in valid_modes, f"mode muss einer von {valid_modes} sein"
        
        valid_resolutions = ["720p", "1080p", "4K"]
        assert self.resolution in valid_resolutions, f"resolution muss einer von {valid_resolutions} sein"
        
        valid_formats = ["mp4", "gif", "webm"]
        assert self.format in valid_formats, f"format muss einer von {valid_formats} sein"
        
        assert self.duration_seconds > 0, "duration_seconds muss positiv sein"
        assert self.fps > 0, "fps muss positiv sein"


# Auflösungs-Mapping
RESOLUTIONS: Dict[str, Tuple[int, int]] = {
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "4K": (3840, 2160)
}


def get_resolution(resolution_key: str) -> Tuple[int, int]:
    """
    Gibt Breite und Höhe für Auflösungs-Schlüssel zurück.
    
    Args:
        resolution_key: Auflösungs-Schlüssel ("720p", "1080p", "4K")
    
    Returns:
        (width, height) Tupel
    """
    if resolution_key not in RESOLUTIONS:
        raise ValueError(f"Unbekannte Auflösung: {resolution_key}")
    return RESOLUTIONS[resolution_key]


def export_timelapse_video(
    fig: go.Figure,
    config: VideoExportConfig,
    progress_callback: Optional[callable] = None
) -> Dict[str, Any]:
    """
    Exportiert Zeitraffer-Video der 3D-Visualisierung.
    
    Args:
        fig: Plotly Figure
        config: Video-Export-Konfiguration
        progress_callback: Optional Callback für Fortschritt (0.0-1.0)
    
    Returns:
        {
            "success": bool,
            "output_path": str,
            "file_size_mb": float,
            "duration_seconds": float,
            "frame_count": int,
            "error": str (nur bei Fehler)
        }
    """
    try:
        # Validiere Konfiguration
        width, height = get_resolution(config.resolution)
        frame_count = config.duration_seconds * config.fps
        
        # Generiere Frames basierend auf Modus
        if config.mode == "day":
            frames = _generate_day_timelapse_frames(
                fig, frame_count, config.show_overlays, progress_callback
            )
        elif config.mode == "year":
            frames = _generate_year_timelapse_frames(
                fig, frame_count, config.show_overlays, progress_callback
            )
        else:  # custom
            frames = _generate_custom_frames(
                fig, frame_count, progress_callback
            )
        
        # Exportiere Video
        success, output_path = _export_frames_to_video(
            frames, config.output_path, config.fps, 
            width, height, config.format, progress_callback
        )
        
        if success and os.path.exists(output_path):
            file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
            
            return {
                "success": True,
                "output_path": output_path,
                "file_size_mb": file_size,
                "duration_seconds": config.duration_seconds,
                "frame_count": frame_count
            }
        else:
            return {
                "success": False,
                "error": "Video-Export fehlgeschlagen"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def _generate_day_timelapse_frames(
    fig: go.Figure,
    frame_count: int,
    show_overlays: bool,
    progress_callback: Optional[callable] = None
) -> List[bytes]:
    """
    Generiert Frames für Tagesverlauf (24h in 30s).
    
    Args:
        fig: Plotly Figure
        frame_count: Anzahl der Frames
        show_overlays: Text-Overlays anzeigen
        progress_callback: Optional Callback für Fortschritt
    
    Returns:
        Liste von Frame-Daten (als Bytes)
    """
    frames = []
    
    for i in range(frame_count):
        # Berechne Tageszeit (0-24 Stunden)
        hour = (i / frame_count) * 24
        
        # Update Sonnenposition
        fig_copy = _update_sun_position(fig, hour)
        
        # Füge Text-Overlay hinzu
        if show_overlays:
            fig_copy = _add_time_overlay(fig_copy, hour)
        
        # Rendere Frame
        frame_data = _render_figure_to_bytes(fig_copy)
        frames.append(frame_data)
        
        # Progress Callback
        if progress_callback:
            progress = (i + 1) / frame_count
            progress_callback(progress * 0.8)  # 80% für Frame-Generierung
    
    return frames


def _generate_year_timelapse_frames(
    fig: go.Figure,
    frame_count: int,
    show_overlays: bool,
    progress_callback: Optional[callable] = None
) -> List[bytes]:
    """
    Generiert Frames für Jahresverlauf (12 Monate in 60s).
    
    Args:
        fig: Plotly Figure
        frame_count: Anzahl der Frames
        show_overlays: Text-Overlays anzeigen
        progress_callback: Optional Callback für Fortschritt
    
    Returns:
        Liste von Frame-Daten (als Bytes)
    """
    frames = []
    months = ["Januar", "Februar", "März", "April", "Mai", "Juni",
              "Juli", "August", "September", "Oktober", "November", "Dezember"]
    
    for i in range(frame_count):
        # Berechne Monat (0-11)
        month_index = int((i / frame_count) * 12)
        month_index = min(month_index, 11)  # Clamp to 11
        
        # Update Szene für Monat
        fig_copy = _update_scene_for_month(fig, month_index)
        
        # Füge Text-Overlay hinzu
        if show_overlays:
            fig_copy = _add_month_overlay(fig_copy, months[month_index])
        
        # Rendere Frame
        frame_data = _render_figure_to_bytes(fig_copy)
        frames.append(frame_data)
        
        # Progress Callback
        if progress_callback:
            progress = (i + 1) / frame_count
            progress_callback(progress * 0.8)
    
    return frames


def _generate_custom_frames(
    fig: go.Figure,
    frame_count: int,
    progress_callback: Optional[callable] = None
) -> List[bytes]:
    """
    Generiert benutzerdefinierte Frames.
    
    Args:
        fig: Plotly Figure
        frame_count: Anzahl der Frames
        progress_callback: Optional Callback für Fortschritt
    
    Returns:
        Liste von Frame-Daten (als Bytes)
    """
    frames = []
    
    for i in range(frame_count):
        # Rendere aktuellen Frame
        frame_data = _render_figure_to_bytes(fig)
        frames.append(frame_data)
        
        # Progress Callback
        if progress_callback:
            progress = (i + 1) / frame_count
            progress_callback(progress * 0.8)
    
    return frames


def _update_sun_position(fig: go.Figure, hour: float) -> go.Figure:
    """
    Aktualisiert Sonnenposition für gegebene Stunde.
    
    Args:
        fig: Plotly Figure
        hour: Stunde (0-24)
    
    Returns:
        Aktualisierte Figure
    """
    # Importiere solar_animation wenn verfügbar
    try:
        from utils.solar_animation import calculate_sun_position
        
        # Berechne Sonnenposition
        sun_pos = calculate_sun_position(hour)
        
        # Update Figure (vereinfacht)
        # In echter Implementierung würde hier die Beleuchtung aktualisiert
        fig_copy = go.Figure(fig)
        
        return fig_copy
    except ImportError:
        # Fallback: Gebe Original zurück
        return go.Figure(fig)


def _update_scene_for_month(fig: go.Figure, month_index: int) -> go.Figure:
    """
    Aktualisiert Szene für gegebenen Monat.
    
    Args:
        fig: Plotly Figure
        month_index: Monats-Index (0-11)
    
    Returns:
        Aktualisierte Figure
    """
    # Erstelle Kopie
    fig_copy = go.Figure(fig)
    
    # Update Beleuchtung basierend auf Jahreszeit
    # Winter: weniger Licht, Sommer: mehr Licht
    season_factor = 0.5 + 0.5 * np.sin((month_index - 3) * np.pi / 6)
    
    # Update alle Meshes
    for trace in fig_copy.data:
        if hasattr(trace, 'lighting') and isinstance(trace, go.Mesh3d):
            trace.lighting = dict(
                ambient=0.5 + 0.3 * season_factor,
                diffuse=0.7 + 0.2 * season_factor,
                specular=0.5,
                roughness=0.3
            )
    
    return fig_copy


def _add_time_overlay(fig: go.Figure, hour: float) -> go.Figure:
    """
    Fügt Zeit-Overlay zum Frame hinzu.
    
    Args:
        fig: Plotly Figure
        hour: Stunde (0-24)
    
    Returns:
        Figure mit Overlay
    """
    # Formatiere Zeit
    hour_int = int(hour)
    minute = int((hour - hour_int) * 60)
    time_str = f"{hour_int:02d}:{minute:02d} Uhr"
    
    # Füge Annotation hinzu
    fig.add_annotation(
        text=time_str,
        xref="paper", yref="paper",
        x=0.02, y=0.98,
        showarrow=False,
        font=dict(size=20, color="white"),
        bgcolor="rgba(0, 0, 0, 0.5)",
        borderpad=10
    )
    
    return fig


def _add_month_overlay(fig: go.Figure, month_name: str) -> go.Figure:
    """
    Fügt Monats-Overlay zum Frame hinzu.
    
    Args:
        fig: Plotly Figure
        month_name: Monatsname
    
    Returns:
        Figure mit Overlay
    """
    # Füge Annotation hinzu
    fig.add_annotation(
        text=month_name,
        xref="paper", yref="paper",
        x=0.02, y=0.98,
        showarrow=False,
        font=dict(size=24, color="white", family="Arial Black"),
        bgcolor="rgba(0, 0, 0, 0.6)",
        borderpad=15
    )
    
    return fig


def _render_figure_to_bytes(fig: go.Figure) -> bytes:
    """
    Rendert Plotly Figure zu Bild-Bytes.
    
    Args:
        fig: Plotly Figure
    
    Returns:
        Bild-Daten als Bytes
    """
    try:
        # Versuche kaleido zu verwenden
        img_bytes = fig.to_image(format="png")
        return img_bytes
    except Exception as e:
        # Fallback: Leeres Bild
        st.warning(f"Konnte Frame nicht rendern: {e}")
        # Erstelle 1x1 schwarzes Bild als Fallback
        return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'


def _export_frames_to_video(
    frames: List[bytes],
    output_path: str,
    fps: int,
    width: int,
    height: int,
    format: str,
    progress_callback: Optional[callable] = None
) -> Tuple[bool, str]:
    """
    Exportiert Frames zu Video-Datei.
    
    Args:
        frames: Liste von Frame-Daten
        output_path: Ausgabe-Pfad
        fps: Frames pro Sekunde
        width: Video-Breite
        height: Video-Höhe
        format: Video-Format
        progress_callback: Optional Callback für Fortschritt
    
    Returns:
        (success, output_path) Tupel
    """
    try:
        # Versuche imageio zu verwenden
        import imageio
        from PIL import Image
        import io
        
        # Konvertiere Bytes zu Bildern
        images = []
        for i, frame_bytes in enumerate(frames):
            try:
                img = Image.open(io.BytesIO(frame_bytes))
                # Resize auf gewünschte Auflösung
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                images.append(np.array(img))
                
                # Progress Callback
                if progress_callback:
                    progress = 0.8 + (i + 1) / len(frames) * 0.2
                    progress_callback(progress)
            except Exception as e:
                st.warning(f"Konnte Frame {i} nicht konvertieren: {e}")
                continue
        
        if not images:
            return False, output_path
        
        # Exportiere basierend auf Format
        if format == "gif":
            imageio.mimsave(output_path, images, fps=fps, loop=0)
        elif format == "mp4":
            imageio.mimsave(output_path, images, fps=fps, codec='libx264')
        elif format == "webm":
            imageio.mimsave(output_path, images, fps=fps, codec='libvpx-vp9')
        
        return True, output_path
    
    except ImportError:
        st.error("imageio ist nicht installiert. Bitte installieren Sie es mit: pip install imageio imageio-ffmpeg")
        return False, output_path
    except Exception as e:
        st.error(f"Fehler beim Video-Export: {e}")
        return False, output_path


def create_export_config_ui() -> VideoExportConfig:
    """
    Erstellt UI für Video-Export-Konfiguration.
    
    Returns:
        VideoExportConfig Objekt
    """
    st.sidebar.subheader("🎬 Video-Export Einstellungen")
    
    # Modus
    mode = st.sidebar.selectbox(
        "Zeitraffer-Modus",
        options=["day", "year", "custom"],
        format_func=lambda x: {
            "day": "Tagesverlauf (24h)",
            "year": "Jahresverlauf (12 Monate)",
            "custom": "Benutzerdefiniert"
        }[x],
        help="Wählen Sie den Zeitraffer-Modus"
    )
    
    # Dauer
    if mode == "day":
        default_duration = 30
        help_text = "24 Stunden in X Sekunden"
    elif mode == "year":
        default_duration = 60
        help_text = "12 Monate in X Sekunden"
    else:
        default_duration = 10
        help_text = "Benutzerdefinierte Dauer"
    
    duration = st.sidebar.slider(
        "Video-Dauer (Sekunden)",
        min_value=5,
        max_value=120,
        value=default_duration,
        step=5,
        help=help_text
    )
    
    # Auflösung
    resolution = st.sidebar.selectbox(
        "Auflösung",
        options=["720p", "1080p", "4K"],
        index=1,
        help="Höhere Auflösung = größere Datei"
    )
    
    # Format
    format = st.sidebar.selectbox(
        "Format",
        options=["mp4", "gif", "webm"],
        help="MP4: Beste Qualität, GIF: Kleine Datei, WebM: Web-optimiert"
    )
    
    # FPS
    fps = st.sidebar.slider(
        "Frames pro Sekunde",
        min_value=12,
        max_value=60,
        value=24,
        step=6,
        help="Höhere FPS = flüssigere Animation"
    )
    
    # Overlays
    show_overlays = st.sidebar.checkbox(
        "Text-Overlays anzeigen",
        value=True,
        help="Zeigt Datum/Uhrzeit im Video"
    )
    
    # Ausgabe-Pfad
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"timelapse_{timestamp}.{format}"
    
    return VideoExportConfig(
        mode=mode,
        duration_seconds=duration,
        resolution=resolution,
        format=format,
        fps=fps,
        show_overlays=show_overlays,
        output_path=output_path
    )


def render_export_button(fig: go.Figure) -> None:
    """
    Rendert Export-Button und handhabt Export-Prozess.
    
    Args:
        fig: Plotly Figure zum Exportieren
    """
    # Erstelle Konfiguration
    config = create_export_config_ui()
    
    # Export-Button
    if st.sidebar.button("🎬 Video exportieren", type="primary"):
        # Progress Bar
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()
        
        def update_progress(progress: float):
            progress_bar.progress(progress)
            if progress < 0.8:
                status_text.text(f"Generiere Frames... {int(progress * 100)}%")
            else:
                status_text.text(f"Exportiere Video... {int(progress * 100)}%")
        
        # Exportiere Video
        status_text.text("Starte Export...")
        result = export_timelapse_video(fig, config, update_progress)
        
        # Zeige Ergebnis
        if result["success"]:
            progress_bar.progress(1.0)
            status_text.text("✅ Export erfolgreich!")
            
            st.sidebar.success(
                f"Video exportiert!\n\n"
                f"📁 Datei: {result['output_path']}\n"
                f"📊 Größe: {result['file_size_mb']:.2f} MB\n"
                f"⏱️ Dauer: {result['duration_seconds']}s\n"
                f"🎞️ Frames: {result['frame_count']}"
            )
            
            # Download-Button
            if os.path.exists(result["output_path"]):
                with open(result["output_path"], "rb") as f:
                    st.sidebar.download_button(
                        label="📥 Video herunterladen",
                        data=f,
                        file_name=os.path.basename(result["output_path"]),
                        mime=f"video/{config.format}"
                    )
        else:
            progress_bar.empty()
            status_text.empty()
            st.sidebar.error(f"❌ Export fehlgeschlagen: {result.get('error', 'Unbekannter Fehler')}")


# Hilfsfunktionen für Session State
def init_video_export_session_state() -> None:
    """Initialisiert Video-Export Session State."""
    if "video_export_history" not in st.session_state:
        st.session_state["video_export_history"] = []


def add_to_export_history(result: Dict[str, Any]) -> None:
    """
    Fügt Export-Ergebnis zur Historie hinzu.
    
    Args:
        result: Export-Ergebnis Dictionary
    """
    if "video_export_history" not in st.session_state:
        st.session_state["video_export_history"] = []
    
    st.session_state["video_export_history"].append({
        "timestamp": datetime.now().isoformat(),
        "result": result
    })


def get_export_history() -> List[Dict[str, Any]]:
    """
    Gibt Export-Historie zurück.
    
    Returns:
        Liste von Export-Ergebnissen
    """
    return st.session_state.get("video_export_history", [])
