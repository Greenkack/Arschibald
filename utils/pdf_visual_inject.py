"""
PDF-Integration für 3D PV-Visualisierung

Dieses Modul stellt Funktionen bereit, um 3D-Visualisierungen
in PDF-Dokumente einzubetten.
"""

from typing import Dict, Any, Optional
from io import BytesIO

try:
    from reportlab.platypus import Image as RLImage
    from reportlab.lib.units import cm
except ImportError:
    RLImage = None
    cm = None

# Import der pv3d Module
try:
    from utils.pv3d import (
        BuildingDims,
        LayoutConfig,
        render_image_bytes
    )
except ImportError:
    # Fallback für verschiedene Import-Pfade
    try:
        from pv3d import (
            BuildingDims,
            LayoutConfig,
            render_image_bytes
        )
    except ImportError:
        BuildingDims = None
        LayoutConfig = None
        render_image_bytes = None


def make_pv3d_image_flowable(
    project_data: Dict[str, Any],
    dims: 'BuildingDims',
    roof_type: str,
    module_quantity: int,
    layout_config: 'LayoutConfig',
    width_cm: float = 17.0
) -> Optional['RLImage']:
    """
    Erstellt ein ReportLab Image-Flowable für PDF-Integration.

    Diese Funktion rendert eine 3D-Visualisierung der PV-Anlage und
    erstellt daraus ein ReportLab Image-Objekt, das in PDF-Dokumente
    eingefügt werden kann.

    Args:
        project_data: Projektdaten-Dictionary mit Gebäudeinformationen
        dims: BuildingDims mit Gebäudedimensionen
        roof_type: Dachtyp ("Flachdach", "Satteldach", etc.)
        module_quantity: Gewünschte Anzahl der PV-Module
        layout_config: LayoutConfig mit Belegungskonfiguration
        width_cm: Bildbreite in Zentimetern (Standard: 17.0)

    Returns:
        ReportLab Image-Flowable oder None bei Fehler

    Example:
        >>> from utils.pv3d import BuildingDims, LayoutConfig
        >>> dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        >>> layout = LayoutConfig(mode="auto")
        >>> flowable = make_pv3d_image_flowable(
        ...     project_data={},
        ...     dims=dims,
        ...     roof_type="Satteldach",
        ...     module_quantity=20,
        ...     layout_config=layout,
        ...     width_cm=17.0
        ... )
        >>> flowable is not None
        True
    """
    # Prüfe ob alle erforderlichen Module verfügbar sind
    if RLImage is None or cm is None:
        print("ReportLab ist nicht installiert")
        return None

    if render_image_bytes is None:
        print("pv3d Modul ist nicht verfügbar")
        return None

    try:
        # Rufe render_image_bytes() auf
        png_bytes = render_image_bytes(
            project_data=project_data,
            dims=dims,
            roof_type=roof_type,
            module_quantity=module_quantity,
            layout_config=layout_config,
            width=1600,
            height=1000
        )

        # Prüfe ob Rendering erfolgreich war
        if not png_bytes or len(png_bytes) == 0:
            print("3D-Rendering fehlgeschlagen: Keine Bytes zurückgegeben")
            return None

        # Konvertiere PNG-Bytes zu BytesIO
        img_buffer = BytesIO(png_bytes)

        # Berechne Höhe mit Seitenverhältnis 16:10
        # Seitenverhältnis: 1600:1000 = 16:10 = 1.6:1
        height_cm = width_cm / 1.6

        # Erstelle ReportLab Image mit width_cm und berechneter Höhe
        image_flowable = RLImage(
            img_buffer,
            width=width_cm * cm,
            height=height_cm * cm
        )

        return image_flowable

    except Exception as e:
        # Fehlerbehandlung: return None bei Fehler
        print(f"Fehler beim Erstellen des PDF-Image-Flowables: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_pv3d_png_bytes_for_pdf(
    project_data: Dict[str, Any],
    dims: 'BuildingDims',
    roof_type: str,
    module_quantity: int,
    layout_config: 'LayoutConfig'
) -> bytes:
    """
    Wrapper-Funktion für direkten PNG-Bytes Zugriff.

    Diese Funktion ist ein einfacher Wrapper um render_image_bytes()
    für flexible PDF-Integration, wenn direkter Zugriff auf PNG-Bytes
    benötigt wird.

    Args:
        project_data: Projektdaten-Dictionary mit Gebäudeinformationen
        dims: BuildingDims mit Gebäudedimensionen
        roof_type: Dachtyp ("Flachdach", "Satteldach", etc.)
        module_quantity: Gewünschte Anzahl der PV-Module
        layout_config: LayoutConfig mit Belegungskonfiguration

    Returns:
        PNG-Bytes des 3D-Screenshots (1600×1000 px, isometrische Ansicht).
        Leere Bytes (b"") bei Fehler.

    Example:
        >>> from utils.pv3d import BuildingDims, LayoutConfig
        >>> dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        >>> layout = LayoutConfig(mode="auto")
        >>> png_bytes = get_pv3d_png_bytes_for_pdf(
        ...     project_data={},
        ...     dims=dims,
        ...     roof_type="Satteldach",
        ...     module_quantity=20,
        ...     layout_config=layout
        ... )
        >>> len(png_bytes) > 0
        True
    """
    # Prüfe ob render_image_bytes verfügbar ist
    if render_image_bytes is None:
        print("pv3d Modul ist nicht verfügbar")
        return b""

    try:
        # Rufe render_image_bytes() mit Standardparametern auf
        png_bytes = render_image_bytes(
            project_data=project_data,
            dims=dims,
            roof_type=roof_type,
            module_quantity=module_quantity,
            layout_config=layout_config,
            width=1600,
            height=1000
        )

        return png_bytes

    except Exception as e:
        # Fehlerbehandlung: return leere Bytes bei Fehler
        print(f"Fehler beim Abrufen der PNG-Bytes: {e}")
        return b""
