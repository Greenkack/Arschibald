"""
Kompatibilitätsmodul: multi_offer_generator

Fallback/Stub für die Multi-Angebots-Funktion, damit die App nicht bei ImportError
abbricht. Zeigt in Streamlit einen klaren Hinweis und verhält sich als No-Op.
"""
from __future__ import annotations

from typing import Any


def _show_unavailable(feature_name: str = "Multi-Angebots-Generator") -> None:
    try:
        import streamlit as st  # type: ignore
        st.info(
            "ℹ️ **Multi-Firmen-Angebote: Voraussetzungen**\n\n"
            "Für die Generierung von Angeboten für mehrere Firmen benötigen Sie:\n\n"
            "1️⃣ **Mehrere Firmen konfiguriert** im Admin-Panel → Firmenverwaltung\n"
            "2️⃣ **Vollständige Projektanalyse** durchgeführt\n"
            "3️⃣ **Preiskalkulationen** für alle Firmen abgeschlossen\n\n"
            "👉 Für **Einzel-Firmen-PDFs** nutzen Sie den Tab **'📄 PDF-Ausgabe'** oben.",
            icon="💡",
        )
    except Exception:
        pass


def render(*args: Any, **kwargs: Any) -> None:
    _show_unavailable("Multi-Angebots-Generator")


def render_multi_offer_generator(*args: Any, **kwargs: Any) -> None:
    """Hauptfunktion für GUI-Integration"""
    _show_unavailable("Multi-Angebots-Generator")


def render_product_selection(*args: Any, **kwargs: Any) -> None:
    """Produktauswahl-Logik (optional)"""
    pass  # Stillschweigend ignorieren, da Shim-Modul


def run(*args: Any, **kwargs: Any) -> None:
    _show_unavailable("Multi-Angebots-Generator")


def main(*args: Any, **kwargs: Any) -> None:
    _show_unavailable("Multi-Angebots-Generator")


def show(*args: Any, **kwargs: Any) -> None:
    _show_unavailable("Multi-Angebots-Generator")