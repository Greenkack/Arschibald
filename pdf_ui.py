"""
Kompatibilitätsmodul: pdf_ui

Dieses Modul dient als Fallback/Stub, wenn die ursprüngliche PDF-UI entfernt oder
verschoben wurde. Es verhindert ImportError und zeigt in Streamlit eine klare
Hinweismeldung statt die App abstürzen zu lassen.
"""
from __future__ import annotations

from typing import Any


def _show_unavailable(feature_name: str = "PDF UI") -> None:
    try:
        import streamlit as st  # type: ignore
        st.info(
            "ℹ️ **Legacy PDF UI archiviert**\n\n"
            "Diese alte Oberfläche wurde entfernt. Nutzen Sie stattdessen:\n\n"
            "👉 **Tab '📄 PDF-Ausgabe'** oben für die Standard-PDF-Erzeugung mit vollständigen Projektdaten.\n\n"
            "Der Kern-PDF-Generator ist voll funktionsfähig.",
            icon="💡",
        )
    except Exception:
        # Außerhalb von Streamlit (z. B. Import-Check): nur stillschweigend zurück
        pass


def render(*args: Any, **kwargs: Any) -> None:
    _show_unavailable("PDF UI")


def render_pdf_ui(*args: Any, **kwargs: Any) -> None:
    """Hauptfunktion für GUI-Integration - wird von gui.py aufgerufen"""
    _show_unavailable("PDF UI")


def run(*args: Any, **kwargs: Any) -> None:
    _show_unavailable("PDF UI")


def main(*args: Any, **kwargs: Any) -> None:
    _show_unavailable("PDF UI")


def show(*args: Any, **kwargs: Any) -> None:
    _show_unavailable("PDF UI")
