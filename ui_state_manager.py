"""Hilfsfunktionen zur robusten Verwaltung des Streamlit Session State.

Diese Utilities implementieren die in ``data/robust.md`` beschriebenen Patterns:
- Persistente Ablage wichtiger Zustände
- Option A/B zur Vermeidung des Widget-Cleanup
- Zentraler Reset-Mechanismus
"""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import streamlit as st

_PERSISTENT_REGISTRY_KEY = "_persistent_state_registry"
_WIDGET_MIRROR_PREFIX = "_widget_mirror_"


def _ensure_registry() -> list[str]:
    registry = st.session_state.get(_PERSISTENT_REGISTRY_KEY)
    if not isinstance(registry, list):
        registry = []
        st.session_state[_PERSISTENT_REGISTRY_KEY] = registry
    return registry


def register_persistent_keys(keys: Iterable[str]) -> None:
    """Merkt sich Session-State-Keys, die über Seiten hinweg erhalten bleiben sollen."""
    registry = _ensure_registry()
    for key in keys:
        if key and key not in registry:
            registry.append(key)


def ensure_session_defaults(defaults: dict[str, Any]) -> None:
    """Initialisiert fehlende Session-State-Werte und registriert sie als persistent."""
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    register_persistent_keys(defaults.keys())


def keep_session_state_alive(keys: Iterable[str] | None = None) -> None:
    """Verhindert den Streamlit-Widget-Cleanup durch Selbstzuweisung gespeicherter Werte."""
    if keys is None:
        keys = _ensure_registry()
    for key in list(keys):
        if key in st.session_state:
            try:
                st.session_state[key] = st.session_state[key]
            except Exception:
                # Ignoriere schreibgeschützte oder komplexe Objekte
                continue


def mirror_widget_value(
        persistent_key: str,
        default: Any = None,
        *,
        widget_key: str | None = None) -> str:
    """Synchronisiert einen dauerhaften State-Key mit einem Widget-Key (Option B).

    Wichtig: Diese Funktion wird VOR dem Widget-Render aufgerufen und setzt den
    initialen Widget-Wert. Sie überschreibt NICHT User-Änderungen während eines Reruns.
    """
    ensure_session_defaults({persistent_key: default})
    register_persistent_keys([persistent_key])

    if widget_key is None:
        widget_key = f"{_WIDGET_MIRROR_PREFIX}{persistent_key}"

    # NUR beim ersten Mal (wenn widget_key noch nicht existiert) synchronisieren
    # Danach behält das Widget seinen Wert, bis commit_widget_value aufgerufen
    # wird
    if widget_key not in st.session_state:
        st.session_state[widget_key] = st.session_state[persistent_key]

    return widget_key


def commit_widget_value(
        persistent_key: str,
        *,
        widget_key: str | None = None) -> None:
    """Überträgt den Wert eines Widget-Keys zurück in den persistenten State."""
    if widget_key is None:
        widget_key = f"{_WIDGET_MIRROR_PREFIX}{persistent_key}"
    if widget_key in st.session_state:
        st.session_state[persistent_key] = st.session_state[widget_key]


def reset_app_state(*, preserve: Iterable[str] | None = None) -> None:
    """Löscht den Session State kontrolliert, optional mit Whitelist."""
    preserve_set = set(preserve or [])
    preserve_set.add(_PERSISTENT_REGISTRY_KEY)
    keys_to_delete = [
        key for key in list(
            st.session_state.keys()) if key not in preserve_set]
    for key in keys_to_delete:
        st.session_state.pop(key, None)
    registry = st.session_state.get(_PERSISTENT_REGISTRY_KEY)
    if isinstance(registry, list):
        registry[:] = [key for key in registry if key in st.session_state]


def get_persistent_registry() -> list[str]:
    """Debug-Hilfe: gibt die aktuelle Registry zurück."""
    return list(_ensure_registry())


def request_rerun() -> None:
    """Fordert einen Streamlit-Rerun an und unterstützt ältere API-Namen."""
    rerun = getattr(st, "rerun", None)
    if callable(rerun):
        rerun()
        return

    experimental_rerun = getattr(st, "experimental_rerun", None)
    if callable(experimental_rerun):
        experimental_rerun()


def set_current_page(page_key: str, *, trigger_rerun: bool = True) -> None:
    """Aktualisiert die aktuelle Seite und markiert den Verlauf entsprechend."""
    previous_page = st.session_state.get("selected_page_key_sui")
    skip_append = bool(st.session_state.get("nav_history_skip_append", False))

    st.session_state.current_page = page_key
    st.session_state.selected_page_key_sui = page_key
    st.session_state.selected_page_key_prev = page_key
    if previous_page != page_key:
        st.session_state.nav_event = True

    if "last_rendered_page_key" in st.session_state:
        st.session_state.last_rendered_page_key = page_key

    if "_navigation_in_progress" in st.session_state:
        st.session_state._navigation_in_progress = False

    history = st.session_state.get("nav_history")
    if isinstance(history, list) and not skip_append:
        if not history or history[-1] != page_key:
            history.append(page_key)

    st.session_state.nav_history_skip_append = False

    if trigger_rerun and previous_page != page_key:
        request_rerun()
