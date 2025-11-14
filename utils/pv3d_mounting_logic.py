"""
Aufständerungs-Logik für 3D-Visualisierung

Stellt sicher, dass Aufständerungen nur bei Flachdächern verwendet werden.
"""

import streamlit as st
from typing import Dict, Any, Optional, List


# Dachtypen die Aufständerungen erlauben
FLAT_ROOF_TYPES = [
    "Flachdach",
    "flat",
    "flat_roof",
    "flach"
]

# Dachtypen die KEINE Aufständerungen erlauben
PITCHED_ROOF_TYPES = [
    "Satteldach",
    "Pultdach",
    "Walmdach",
    "Zeltdach",
    "Mansarddach",
    "Sheddach",
    "pitched",
    "gable",
    "hip",
    "mansard"
]


def is_flat_roof(roof_type: str) -> bool:
    """
    Prüft ob ein Dachtyp ein Flachdach ist.
    
    Args:
        roof_type: Dachtyp-String
        
    Returns:
        True wenn Flachdach, False sonst
    """
    if not roof_type:
        return False
    
    roof_type_lower = roof_type.lower().strip()
    
    # Exakte Übereinstimmung mit Flachdach-Typen
    for flat_type in FLAT_ROOF_TYPES:
        if flat_type.lower() in roof_type_lower:
            return True
    
    return False


def is_pitched_roof(roof_type: str) -> bool:
    """
    Prüft ob ein Dachtyp ein Schrägdach ist.
    
    Args:
        roof_type: Dachtyp-String
        
    Returns:
        True wenn Schrägdach, False sonst
    """
    if not roof_type:
        return False
    
    roof_type_lower = roof_type.lower().strip()
    
    # Exakte Übereinstimmung mit Schrägdach-Typen
    for pitched_type in PITCHED_ROOF_TYPES:
        if pitched_type.lower() in roof_type_lower:
            return True
    
    return False


def get_allowed_mounting_types(roof_type: str) -> List[str]:
    """
    Gibt erlaubte Montagetypen für einen Dachtyp zurück.
    
    Args:
        roof_type: Dachtyp-String
        
    Returns:
        Liste von erlaubten Montagetypen
    """
    if is_flat_roof(roof_type):
        # Flachdach: Aufständerung erlaubt
        return [
            "Aufständerung Süd",
            "Aufständerung Ost-West",
            "Aufständerung Optimal",
            "Flach aufliegend"
        ]
    elif is_pitched_roof(roof_type):
        # Schrägdach: Nur Aufdach-Montage
        return [
            "Aufdach-Montage",
            "Indach-Montage"
        ]
    else:
        # Unbekannter Typ: Sichere Defaults
        return [
            "Aufdach-Montage"
        ]


def validate_mounting_selection(
    roof_type: str,
    selected_mounting: str
) -> Dict[str, Any]:
    """
    Validiert ob die gewählte Montage für den Dachtyp erlaubt ist.
    
    Args:
        roof_type: Dachtyp
        selected_mounting: Gewählter Montagetyp
        
    Returns:
        Dictionary mit:
        - valid: bool
        - error: str (bei Fehler)
        - suggestion: str (Alternative)
    """
    result = {
        "valid": True,
        "error": None,
        "suggestion": None
    }
    
    allowed_types = get_allowed_mounting_types(roof_type)
    
    # Prüfe ob Aufständerung bei Schrägdach gewählt wurde
    if is_pitched_roof(roof_type) and "Aufständerung" in selected_mounting:
        result["valid"] = False
        result["error"] = (
            f"[ERROR] Aufständerungen sind nur für Flachdächer erlaubt! "
            f"'{roof_type}' ist ein Schrägdach."
        )
        result["suggestion"] = "Aufdach-Montage"
        return result
    
    # Prüfe ob gewählter Typ in erlaubten Typen
    if selected_mounting not in allowed_types:
        result["valid"] = False
        result["error"] = (
            f"[WARNING] '{selected_mounting}' ist für '{roof_type}' nicht optimal."
        )
        result["suggestion"] = allowed_types[0] if allowed_types else "Aufdach-Montage"
    
    return result


def render_mounting_selection_with_validation(
    roof_type: str,
    current_selection: Optional[str] = None
) -> str:
    """
    Rendert Montagetyp-Auswahl mit automatischer Validierung.
    
    Args:
        roof_type: Aktueller Dachtyp
        current_selection: Aktuell gewählter Montagetyp
        
    Returns:
        Gewählter (und validierter) Montagetyp
    """
    # Hole erlaubte Montagetypen
    allowed_types = get_allowed_mounting_types(roof_type)
    
    # Info-Box über Dachtyp
    if is_flat_roof(roof_type):
        st.info(
            f"[INFO] **Flachdach erkannt**: Aufständerungen sind verfügbar. "
            f"Module werden mit optimaler Neigung montiert."
        )
    elif is_pitched_roof(roof_type):
        st.info(
            f"[INFO] **Schrägdach erkannt** ({roof_type}): Module werden direkt "
            f"auf der Dachfläche montiert. Aufständerungen sind nicht verfügbar."
        )
    
    # Validiere aktuelle Auswahl
    if current_selection:
        validation = validate_mounting_selection(roof_type, current_selection)
        
        if not validation["valid"]:
            st.warning(validation["error"])
            if validation["suggestion"]:
                # FIX: Zeige Empfehlung, aber überschreibe Auswahl NICHT automatisch
                # Der Benutzer soll selbst entscheiden
                st.info(f"[IDEA] Empfehlung: {validation['suggestion']}")
                # ENTFERNT: current_selection = validation["suggestion"]
    
    # Setze Default wenn keine Auswahl ODER wenn aktuelle Auswahl ungültig ist
    # FIX: Nur setzen wenn current_selection None ist, nicht wenn ungültig
    if not current_selection:
        current_selection = allowed_types[0] if allowed_types else "Aufdach-Montage"
    elif current_selection not in allowed_types:
        # Wenn ungültig, verwende ersten erlaubten Typ als Fallback
        # aber zeige Warnung (wurde bereits oben gemacht)
        current_selection = allowed_types[0] if allowed_types else "Aufdach-Montage"
    
    # Render Selectbox mit nur erlaubten Optionen
    selected_mounting = st.selectbox(
        "Montagetyp",
        options=allowed_types,
        index=allowed_types.index(current_selection) if current_selection in allowed_types else 0,
        help=_get_mounting_help_text(roof_type),
        key="mounting_type_validated"
    )
    
    return selected_mounting


def _get_mounting_help_text(roof_type: str) -> str:
    """Gibt kontextbezogenen Hilfetext für Montagetyp zurück"""
    if is_flat_roof(roof_type):
        return (
            "Wählen Sie die Aufständerungsart für Ihr Flachdach. "
            "Aufständerungen ermöglichen optimale Modulneigung für maximalen Ertrag."
        )
    elif is_pitched_roof(roof_type):
        return (
            "Wählen Sie die Montageart für Ihr Schrägdach. "
            "Module werden direkt auf der geneigten Dachfläche montiert."
        )
    else:
        return "Wählen Sie die Montageart für Ihre PV-Anlage."


def get_mounting_config_for_roof_type(
    roof_type: str,
    mounting_type: str
) -> Dict[str, Any]:
    """
    Gibt Montage-Konfiguration basierend auf Dachtyp zurück.
    
    Args:
        roof_type: Dachtyp
        mounting_type: Montagetyp
        
    Returns:
        Dictionary mit Montage-Konfiguration
    """
    config = {
        "use_mounting": False,
        "tilt_angle": 0,
        "azimuth": 180,  # Süd
        "row_spacing": 0,
        "mounting_height": 0
    }
    
    if is_flat_roof(roof_type):
        # Flachdach: Aufständerung konfigurieren
        config["use_mounting"] = True
        
        if "Süd" in mounting_type:
            config["tilt_angle"] = 30
            config["azimuth"] = 180
            config["row_spacing"] = 1.5
            config["mounting_height"] = 0.3
        elif "Ost-West" in mounting_type:
            config["tilt_angle"] = 15
            config["azimuth"] = 90  # Wird für Ost-West angepasst
            config["row_spacing"] = 0.5
            config["mounting_height"] = 0.2
        elif "Optimal" in mounting_type:
            config["tilt_angle"] = 35
            config["azimuth"] = 180
            config["row_spacing"] = 2.0
            config["mounting_height"] = 0.4
        elif "Flach" in mounting_type:
            config["tilt_angle"] = 5
            config["azimuth"] = 180
            config["row_spacing"] = 0.1
            config["mounting_height"] = 0.1
    
    elif is_pitched_roof(roof_type):
        # Schrägdach: Keine Aufständerung
        config["use_mounting"] = False
        config["tilt_angle"] = 0  # Wird von Dachneigung übernommen
        config["azimuth"] = 180
        config["row_spacing"] = 0
        config["mounting_height"] = 0
    
    return config


__all__ = [
    'is_flat_roof',
    'is_pitched_roof',
    'get_allowed_mounting_types',
    'validate_mounting_selection',
    'render_mounting_selection_with_validation',
    'get_mounting_config_for_roof_type'
]
