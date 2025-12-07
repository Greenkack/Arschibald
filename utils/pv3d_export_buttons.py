"""
Export-Buttons für 3D-Visualisierung

Fügt fehlende Export-Buttons hinzu, die tatsächlich die Exports ausführen.
"""

import streamlit as st
from typing import Dict, Any, Optional
import io
import base64


def render_export_action_buttons(
    export_options: Dict[str, Any],
    figure_data: Optional[Any] = None,
    scene_data: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Rendert Action-Buttons für alle aktivierten Export-Optionen.
    
    Args:
        export_options: Dictionary mit Export-Einstellungen
        figure_data: Plotly Figure für Exports
        scene_data: Szenen-Daten für Exports
        
    Returns:
        Dictionary mit Export-Ergebnissen
    """
    results = {}
    
    st.markdown("### Export starten")
    st.caption("Klicken Sie auf einen Button um den Export zu starten")
    
    # Screenshot Export Button
    if export_options.get("export_screenshot", False):
        if st.button(
            " Screenshot exportieren",
            key="btn_export_screenshot",
            use_container_width=True,
            type="primary"
        ):
            results["screenshot"] = _export_screenshot_action(
                figure_data,
                export_options.get("screenshot_format", "PNG"),
                export_options.get("screenshot_resolution", (1920, 1080))
            )
    
    # Multi-View Export Button
    if export_options.get("export_multiview", False):
        if st.button(
            " Multi-View exportieren",
            key="btn_export_multiview",
            use_container_width=True
        ):
            results["multiview"] = _export_multiview_action(
                scene_data,
                export_options.get("multiview_resolution", (1200, 750))
            )
    
    # 360° Animation Button
    if export_options.get("export_360", False):
        if st.button(
            " 360° Animation exportieren",
            key="btn_export_360",
            use_container_width=True
        ):
            results["animation_360"] = _export_360_action(
                scene_data,
                export_options.get("animation_frames", 36),
                export_options.get("animation_resolution", (600, 450))
            )
    
    # 3D-Modell Export Button
    if export_options.get("export_3d_model", False):
        if st.button(
            "3D-Modell exportieren",
            key="btn_export_3d_model",
            use_container_width=True
        ):
            results["model_3d"] = _export_3d_model_action(
                scene_data,
                export_options.get("model_format", "STL")
            )
    
    # CSV Export Button
    if export_options.get("export_csv", False):
        if st.button(
            "CSV exportieren",
            key="btn_export_csv",
            use_container_width=True
        ):
            results["csv"] = _export_csv_action(scene_data)
    
    # JSON Export Button
    if export_options.get("export_json", False):
        if st.button(
            " JSON exportieren",
            key="btn_export_json",
            use_container_width=True
        ):
            results["json"] = _export_json_action(scene_data)
    
    return results


def _export_screenshot_action(figure, format_type: str, resolution: tuple) -> Dict:
    """Führt Screenshot-Export aus"""
    try:
        from utils.pv3d_export import export_screenshot
        
        with st.spinner(f"Erstelle {format_type} Screenshot..."):
            result = export_screenshot(
                figure,
                format_type=format_type.lower(),
                width=resolution[0],
                height=resolution[1]
            )
            
            if result.get("success"):
                st.success(f"Screenshot erfolgreich erstellt!")
                
                # Download-Button anbieten
                st.download_button(
                    label=f" {format_type} herunterladen",
                    data=result["data"],
                    file_name=result["filename"],
                    mime=result["mime_type"],
                    key="download_screenshot"
                )
                
                return {"success": True, "message": "Screenshot erstellt"}
            else:
                st.error(f"Fehler: {result.get('error', 'Unbekannter Fehler')}")
                return {"success": False, "error": result.get("error")}
                
    except Exception as e:
        st.error(f"Export fehlgeschlagen: {e}")
        return {"success": False, "error": str(e)}


def _export_multiview_action(scene_data, resolution: tuple) -> Dict:
    """Führt Multi-View Export aus"""
    try:
        from utils.pv3d_export import export_multi_view
        
        with st.spinner("Erstelle Multi-View Screenshots..."):
            result = export_multi_view(
                scene_data,
                resolution=resolution
            )
            
            if result.get("success"):
                st.success(f"{len(result.get('views', []))} Ansichten erstellt!")
                
                # ZIP-Download anbieten
                if "zip_data" in result:
                    st.download_button(
                        label=" Multi-View ZIP herunterladen",
                        data=result["zip_data"],
                        file_name=result.get("filename", "multiview.zip"),
                        mime="application/zip",
                        key="download_multiview"
                    )
                
                return {"success": True, "message": "Multi-View erstellt"}
            else:
                st.error(f"Fehler: {result.get('error')}")
                return {"success": False, "error": result.get("error")}
                
    except Exception as e:
        st.error(f"Export fehlgeschlagen: {e}")
        return {"success": False, "error": str(e)}


def _export_360_action(scene_data, frames: int, resolution: tuple) -> Dict:
    """Führt 360° Animation Export aus"""
    try:
        from utils.pv3d_export import export_360_animation
        
        with st.spinner(f"Erstelle 360° Animation ({frames} Frames)..."):
            progress_bar = st.progress(0)
            
            result = export_360_animation(
                scene_data,
                frames=frames,
                resolution=resolution,
                progress_callback=lambda p: progress_bar.progress(p)
            )
            
            progress_bar.empty()
            
            if result.get("success"):
                st.success(f"Animation mit {frames} Frames erstellt!")
                
                # GIF-Download anbieten
                if "gif_data" in result:
                    st.download_button(
                        label=" Animation (GIF) herunterladen",
                        data=result["gif_data"],
                        file_name=result.get("filename", "animation_360.gif"),
                        mime="image/gif",
                        key="download_360"
                    )
                
                return {"success": True, "message": "Animation erstellt"}
            else:
                st.error(f"Fehler: {result.get('error')}")
                return {"success": False, "error": result.get("error")}
                
    except Exception as e:
        st.error(f"Export fehlgeschlagen: {e}")
        return {"success": False, "error": str(e)}


def _export_3d_model_action(scene_data, model_format: str) -> Dict:
    """Führt 3D-Modell Export aus"""
    try:
        from utils.pv3d_export import export_3d_model
        
        with st.spinner(f"Erstelle {model_format} Modell..."):
            result = export_3d_model(
                scene_data,
                format_type=model_format.lower()
            )
            
            if result.get("success"):
                st.success(f"3D-Modell ({model_format}) erstellt!")
                
                # Download anbieten
                st.download_button(
                    label=f" {model_format} herunterladen",
                    data=result["data"],
                    file_name=result["filename"],
                    mime=result.get("mime_type", "application/octet-stream"),
                    key="download_3d_model"
                )
                
                return {"success": True, "message": "3D-Modell erstellt"}
            else:
                st.error(f"Fehler: {result.get('error')}")
                return {"success": False, "error": result.get("error")}
                
    except Exception as e:
        st.error(f"Export fehlgeschlagen: {e}")
        return {"success": False, "error": str(e)}


def _export_csv_action(scene_data) -> Dict:
    """Führt CSV Export aus"""
    try:
        import pandas as pd
        
        with st.spinner("Erstelle CSV..."):
            # Extrahiere Modul-Daten
            modules_data = []
            if scene_data and "modules" in scene_data:
                for i, module in enumerate(scene_data["modules"]):
                    modules_data.append({
                        "Modul_Nr": i + 1,
                        "X": module.get("x", 0),
                        "Y": module.get("y", 0),
                        "Z": module.get("z", 0),
                        "Rotation": module.get("rotation", 0),
                        "Neigung": module.get("tilt", 0),
                        "Leistung_W": module.get("power", 0)
                    })
            
            if modules_data:
                df = pd.DataFrame(modules_data)
                csv_data = df.to_csv(index=False).encode('utf-8')
                
                st.success(f"CSV mit {len(modules_data)} Modulen erstellt!")
                
                st.download_button(
                    label=" CSV herunterladen",
                    data=csv_data,
                    file_name="pv_module_data.csv",
                    mime="text/csv",
                    key="download_csv"
                )
                
                return {"success": True, "message": "CSV erstellt"}
            else:
                st.warning("Keine Modul-Daten zum Exportieren")
                return {"success": False, "error": "Keine Daten"}
                
    except Exception as e:
        st.error(f"Export fehlgeschlagen: {e}")
        return {"success": False, "error": str(e)}


def _export_json_action(scene_data) -> Dict:
    """Führt JSON Export aus"""
    try:
        import json
        
        with st.spinner("Erstelle JSON..."):
            if scene_data:
                json_data = json.dumps(scene_data, indent=2).encode('utf-8')
                
                st.success("JSON erstellt!")
                
                st.download_button(
                    label=" JSON herunterladen",
                    data=json_data,
                    file_name="pv_scene_data.json",
                    mime="application/json",
                    key="download_json"
                )
                
                return {"success": True, "message": "JSON erstellt"}
            else:
                st.warning("Keine Szenen-Daten zum Exportieren")
                return {"success": False, "error": "Keine Daten"}
                
    except Exception as e:
        st.error(f"Export fehlgeschlagen: {e}")
        return {"success": False, "error": str(e)}


__all__ = ['render_export_action_buttons']
