"""Global Emoji Toggle Support.

Dieses Modul stellt Helferfunktionen bereit, um Emojis in der gesamten
Streamlit-Anwendung abhängig von einer Einstellung ein- oder auszublenden.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from functools import wraps
from typing import Any

import streamlit as st

try:  # pragma: no cover - defensive Fallback für Einzellauf ohne Datenbank
    from database import load_admin_setting
except Exception:  # noqa: BLE001 - wir wollen jeden Fehler abfangen
    # type: ignore[misc]
    def load_admin_setting(key: str, default: Any = None) -> Any:
        """Fallback, wenn keine Datenbank verfügbar ist."""
        return default

_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F1E0-\U0001F1FF"  # Flags
    "\U0001F300-\U0001F5FF"  # Symbole & Piktogramme
    "\U0001F600-\U0001F64F"  # Emoticons
    "\U0001F680-\U0001F6FF"  # Transport & Karten
    "\U0001F700-\U0001F77F"  # Alchemistische Symbole
    "\U0001F780-\U0001F7FF"  # Geometrische Erweiterungen
    "\U0001F800-\U0001F8FF"  # Ergänzende Pfeile
    "\U0001F900-\U0001F9FF"  # Zusätzliche Symbole & Piktogramme
    "\U0001FA00-\U0001FA6F"  # Schach, Domino, Mahjong
    "\U0001FA70-\U0001FAFF"  # Symbole und Piktogramme Erweiterung-A
    "\U00002600-\U000026FF"  # Verschiedene Symbole
    "\U00002700-\U000027BF"  # Dingbats
    "\U000024C2-\U0001F251"  # Umschließende Buchstaben/Zahlen
    "]+",
)

_ZERO_WIDTH_JOINER = "\u200d"
_VARIATION_SELECTOR = "\ufe0f"
_PATCHED = False


def should_show_emojis() -> bool:
    """Gibt zurück, ob Emojis angezeigt werden sollen."""
    return bool(st.session_state.get("show_emojis", True))


def _strip_emojis(text: str) -> str:
    """Entfernt Emojis sowie Variations-Selector und Joiner aus Texten."""
    cleaned = _EMOJI_PATTERN.sub("", text)
    if _VARIATION_SELECTOR in cleaned:
        cleaned = cleaned.replace(_VARIATION_SELECTOR, "")
    if _ZERO_WIDTH_JOINER in cleaned:
        cleaned = cleaned.replace(_ZERO_WIDTH_JOINER, "")
    return cleaned


def _sanitize_argument(value: Any) -> Any:
    """Entfernt Emojis aus typischen Streamlit-Argumenten."""
    if should_show_emojis():
        return value

    if isinstance(value, str):
        return _strip_emojis(value)

    if isinstance(
            value, Iterable) and not isinstance(
            value, (str, bytes, dict)):
        value_type = type(value)
        return value_type(_sanitize_argument(item) for item in value)

    if isinstance(value, dict):
        return {key: _sanitize_argument(val) for key, val in value.items()}

    return value


def _patch_method(cls: type, method_name: str) -> None:
    """Patcht eine Methode einer Klasse, um Emojis optional zu entfernen."""
    original = getattr(cls, method_name, None)
    if original is None or getattr(
        original,
        "__emoji_toggle_patched__",
            False):
        return

    @wraps(original)
    def wrapped(self, *args: Any, **kwargs: Any):
        if should_show_emojis():
            return original(self, *args, **kwargs)

        sanitized_args = tuple(_sanitize_argument(arg) for arg in args)
        sanitized_kwargs = {
            key: _sanitize_argument(val) for key,
            val in kwargs.items()}
        return original(self, *sanitized_args, **sanitized_kwargs)

    wrapped.__emoji_toggle_patched__ = True  # type: ignore[attr-defined]
    setattr(cls, method_name, wrapped)


def initialize_emoji_support() -> None:
    """Initialisiert den Emoji-Toggle und patcht relevante Streamlit-Methoden."""
    global _PATCHED

    if "show_emojis" not in st.session_state:
        try:
            default_value = bool(load_admin_setting("ui_show_emojis", True))
        except Exception:  # noqa: BLE001 - falls Datenbankzugriff fehlschlägt
            default_value = True
        st.session_state["show_emojis"] = default_value

    if _PATCHED:
        return

    from streamlit.delta_generator import (
        DeltaGenerator,  # Lazy Import für Streamlit intern
    )

    methods_to_patch = [
        "markdown",
        "write",
        "text",
        "caption",
        "subheader",
        "header",
        "title",
        "info",
        "success",
        "warning",
        "error",
        "exception",
        "button",
        "link_button",
        "download_button",
        "checkbox",
        "radio",
        "selectbox",
        "multiselect",
        "slider",
        "select_slider",
        "toggle",
        "tabs",
        "expander",
        "metric",
        "altair_chart",
        "pydeck_chart",
        "plotly_chart",
    ]

    for method_name in methods_to_patch:
        _patch_method(DeltaGenerator, method_name)

    _PATCHED = True


def set_show_emojis(enabled: bool) -> None:
    """Setzt den Emoji-Status im Session-State und sorgt für Konsistenz."""
    st.session_state["show_emojis"] = bool(enabled)


__all__ = [
    "initialize_emoji_support",
    "should_show_emojis",
    "set_show_emojis",
]
