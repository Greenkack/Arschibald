"""
Kompatibilitätsmodul: pdf_preview

Fallback/Stub für die PDF-Vorschau, damit die App nicht bei ImportError abbricht.
Zeigt in Streamlit einen klaren Hinweis und verhält sich als No-Op.
"""
from __future__ import annotations

from typing import Any

# Flag für die GUI, um zu prüfen, ob das vollständige Modul verfügbar ist
PDF_PREVIEW_AVAILABLE = False


def _show_unavailable(feature_name: str = "PDF-Vorschau") -> None:
    try:
        import streamlit as st  # type: ignore
        st.info(
            "ℹ️ **PDF-Vorschau benötigt vollständige Projektdaten**\n\n"
            "Um die Live-Vorschau zu nutzen:\n\n"
            "1️⃣ Gehen Sie zu **'Dateneingabe'** → **'Analysestufe'**\n"
            "2️⃣ Füllen Sie alle erforderlichen Projektinformationen aus\n"
            "3️⃣ Kehren Sie zum Tab **'👁️ PDF-Vorschau'** zurück\n\n"
            "Alternativ: Nutzen Sie **'📄 PDF-Ausgabe'** für direkte PDF-Erzeugung.",
            icon="💡",
        )
    except Exception:
        pass


def render(*args: Any, **kwargs: Any) -> None:
    _show_unavailable("PDF-Vorschau")


def render_preview(*args: Any, **kwargs: Any) -> None:
    _show_unavailable("PDF-Vorschau")


def render_pdf_preview_interface(*args: Any, **kwargs: Any) -> None:
    """Hauptfunktion für GUI-Integration"""
    _show_unavailable("PDF-Vorschau")


def run(*args: Any, **kwargs: Any) -> None:
    _show_unavailable("PDF-Vorschau")


def main(*args: Any, **kwargs: Any) -> None:
    _show_unavailable("PDF-Vorschau")


def show(*args: Any, **kwargs: Any) -> None:
    _show_unavailable("PDF-Vorschau")