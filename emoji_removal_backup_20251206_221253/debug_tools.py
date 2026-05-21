"""Utility helpers for centralised debug logging within the Streamlit app.

Erweitert um:
- Kategorien-basierte Filterung
- Automatische Instrumentierung zentraler Berechnungsfunktionen
- Performance-Timer
- Kontrolle über große Payload-Logs (z. B. PDF-Bytes)
- Toolbar mit Konfigurationsoptionen
"""
from __future__ import annotations

import functools
import importlib
import json
import logging
import time
from collections.abc import Iterable
from contextlib import contextmanager
from datetime import datetime
from typing import Any

try:
    import streamlit as st  # type: ignore
except Exception:  # pragma: no cover - fallback when Streamlit not available
    st = None  # type: ignore

LOGGER_NAME = "bokuk.debug"
DEBUG_SESSION_KEY = "_debug_events"
DEBUG_MODE_KEY = "debug_mode"
DEBUG_CATEGORY_KEY = "_debug_category_filters"
INSTRUMENTED_TARGETS_KEY = "_debug_instrumented_targets"
MAX_DEBUG_EVENTS = 2000

DEFAULT_DEBUG_CATEGORIES: dict[str, bool] = {
    "general": True,
    "calculations": True,
    "pricing": True,
    "visualizations": True,
    "pdf": True,
    "performance": True,
    "stability": True,
}

INSTRUMENTATION_TARGETS: list[tuple[str, str, str]] = [
    ("calculations", "perform_calculations", "calculations"),
    ("calculations_extended", "run_all_extended_analyses", "calculations"),
    ("analysis", "render_analysis", "visualizations"),
    ("analysis", "render_extended_calculations_dashboard", "visualizations"),
    ("analysis", "render_pricing_modifications_ui", "visualizations"),
    ("analysis", "render_tariff_comparison_switcher", "visualizations"),
    ("solar_calculator", "render_solar_calculator", "pricing"),
    ("pdf_template_engine.placeholders", "build_dynamic_data", "pdf"),
    ("central_pdf_system", "PDFSystemManager.generate_pdf", "pdf"),
    ("central_pdf_system", "PDFSystemManager.generate_pdf_central", "pdf"),
    ("central_pdf_system", "PDFSystemManager._try_standard_pdf_generator", "pdf"),
    ("central_pdf_system", "PDFSystemManager._dummy_mega_hybrid_pdf", "pdf"),
]

logger = logging.getLogger(LOGGER_NAME)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _ensure_logging_configured() -> None:
    """Configure logging handler for debug output once."""
    if logger.handlers:
        return

    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False


def _ensure_category_filters() -> dict[str, bool]:
    filters = DEFAULT_DEBUG_CATEGORIES.copy()
    if st is None:
        return filters

    if DEBUG_CATEGORY_KEY not in st.session_state:
        st.session_state[DEBUG_CATEGORY_KEY] = filters
    else:
        # add new categories automatically
        for key, value in DEFAULT_DEBUG_CATEGORIES.items():
            st.session_state[DEBUG_CATEGORY_KEY].setdefault(key, value)
        filters = st.session_state[DEBUG_CATEGORY_KEY]

    return filters


def _get_category_filters() -> dict[str, bool]:
    if st is None:
        return DEFAULT_DEBUG_CATEGORIES
    return st.session_state.get(
        DEBUG_CATEGORY_KEY,
        DEFAULT_DEBUG_CATEGORIES.copy())


def _truncate(value: Any, max_length: int = 400) -> str:
    if isinstance(value, (bytes, bytearray)):
        preview = value[: max_length]
        try:
            decoded = preview.decode("utf-8", errors="replace")
        except Exception:
            decoded = str(preview)
        suffix = "…" if len(value) > max_length else ""
        return f"bytes[{len(value)}]: {decoded}{suffix}"

    text = repr(value)
    if len(text) > max_length:
        return text[: max_length] + "…"
    return text


def _summarise_call(
        args: tuple[Any, ...], kwargs: dict[str, Any], limit: int = 3) -> dict[str, Any]:
    summary_args = [_truncate(arg) for arg in list(args)[:limit]]
    if len(args) > limit:
        summary_args.append("…")
    summary_kwargs = {k: _truncate(v) for k, v in list(kwargs.items())[:limit]}
    if len(kwargs) > limit:
        summary_kwargs["…"] = "…"
    return {"args": summary_args, "kwargs": summary_kwargs}


def _summarise_result(result: Any) -> dict[str, Any]:
    if isinstance(result, dict):
        summary = {k: _truncate(v) for k, v in list(result.items())[:5]}
        if len(result) > 5:
            summary["…"] = "…"
        return summary
    if isinstance(result, (list, tuple, set)):
        seq = list(result)
        summary = [_truncate(v) for v in seq[:5]]
        if len(seq) > 5:
            summary.append("…")
        return {"sequence": summary, "items": len(seq)}
    return {"value": _truncate(result)}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def init_debug_mode(default_enabled: bool = False) -> bool:
    """Initialise the debug mode flag and session storage."""
    _ensure_logging_configured()
    _ensure_category_filters()

    if st is None:
        logger.setLevel(logging.DEBUG if default_enabled else logging.INFO)
        return default_enabled

    if DEBUG_MODE_KEY not in st.session_state:
        st.session_state[DEBUG_MODE_KEY] = default_enabled

    enabled = bool(st.session_state.get(DEBUG_MODE_KEY, False))
    logger.setLevel(logging.DEBUG if enabled else logging.INFO)

    if DEBUG_SESSION_KEY not in st.session_state:
        st.session_state[DEBUG_SESSION_KEY] = []

    if INSTRUMENTED_TARGETS_KEY not in st.session_state:
        st.session_state[INSTRUMENTED_TARGETS_KEY] = set()

    if enabled:
        ensure_instrumentation()

    return enabled


def set_debug_mode(enabled: bool) -> None:
    """Toggle the debug mode flag and update logging level."""
    _ensure_logging_configured()

    if st is not None:
        st.session_state[DEBUG_MODE_KEY] = bool(enabled)
        if DEBUG_SESSION_KEY not in st.session_state:
            st.session_state[DEBUG_SESSION_KEY] = []
        if INSTRUMENTED_TARGETS_KEY not in st.session_state:
            st.session_state[INSTRUMENTED_TARGETS_KEY] = set()
    logger.setLevel(logging.DEBUG if enabled else logging.INFO)

    if enabled:
        ensure_instrumentation()


def debug_enabled() -> bool:
    if st is not None:
        return bool(st.session_state.get(DEBUG_MODE_KEY, False))
    return logger.level <= logging.DEBUG


def is_category_enabled(category: str) -> bool:
    filters = _get_category_filters()
    return filters.get(category, True)


def set_category_enabled(category: str, enabled: bool) -> None:
    filters = _ensure_category_filters()
    filters[category] = enabled
    if st is not None:
        st.session_state[DEBUG_CATEGORY_KEY] = filters


def debug_log(
    source: str,
    message: str,
    *,
    category: str = "general",
    level: int = logging.DEBUG,
    **context: Any,
) -> None:
    """Store a debug event in logger and optional Streamlit session state."""
    _ensure_logging_configured()

    log_message = f"[{category}] {source}: {message}"
    if context:
        log_message += f" | {json.dumps(context,
                                        default=str,
                                        ensure_ascii=False)}"

    if level >= logging.ERROR:
        logger.error(log_message)
    elif level >= logging.WARNING:
        logger.warning(log_message)
    elif debug_enabled():
        logger.debug(log_message)
    else:
        logger.info(log_message)

    if st is None:
        return

    if DEBUG_SESSION_KEY not in st.session_state:
        st.session_state[DEBUG_SESSION_KEY] = []

    st.session_state[DEBUG_SESSION_KEY].append(
        {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
            "source": source,
            "message": message,
            "context": context,
            "category": category,
        }
    )

    if len(st.session_state[DEBUG_SESSION_KEY]) > MAX_DEBUG_EVENTS:
        st.session_state[DEBUG_SESSION_KEY] = st.session_state[DEBUG_SESSION_KEY][-MAX_DEBUG_EVENTS:]


def log_payload(
    source: str,
    label: str,
    payload: Any,
    *,
    category: str = "general",
    preview_length: int = 800,
) -> None:
    """Log potentially large payloads (PDF bytes, JSON etc.) safely."""
    info: dict[str, Any] = {}
    if isinstance(payload, (bytes, bytearray)):
        info["size_bytes"] = len(payload)
        info["preview"] = _truncate(payload, preview_length)
    else:
        info["preview"] = _truncate(payload, preview_length)
    debug_log(source, label, category=category, payload=info)


@contextmanager
def debug_timer(
        action: str,
        *,
        source: str = "debug",
        category: str = "performance"):
    start = time.perf_counter()
    debug_log(source, f"{action} gestartet", category=category)
    try:
        yield
    except Exception as exc:  # pragma: no cover - debugging aid
        duration_ms = (time.perf_counter() - start) * 1000
        debug_log(
            source,
            f"{action} fehlgeschlagen",
            category="stability",
            duration_ms=duration_ms,
            error=repr(exc),
            level=logging.ERROR,
        )
        raise
    else:
        duration_ms = (time.perf_counter() - start) * 1000
        debug_log(
            source,
            f"{action} abgeschlossen",
            category=category,
            duration_ms=duration_ms)


# ---------------------------------------------------------------------------
# Instrumentation
# ---------------------------------------------------------------------------


def _get_instrumented_registry() -> set:
    if st is not None:
        registry = st.session_state.setdefault(INSTRUMENTED_TARGETS_KEY, set())
        return registry
    if not hasattr(_get_instrumented_registry, "_memory_registry"):
        # type: ignore[attr-defined]
        _get_instrumented_registry._memory_registry = set()
    # type: ignore[attr-defined]
    return _get_instrumented_registry._memory_registry


def ensure_instrumentation(
        targets: Iterable[tuple[str, str, str]] | None = None) -> None:
    """Apply instrumentation wrappers to configured targets."""
    if not debug_enabled():
        return

    registry = _get_instrumented_registry()
    entries = list(targets) if targets else INSTRUMENTATION_TARGETS

    for module_name, func_path, category in entries:
        target_id = f"{module_name}.{func_path}"
        if target_id in registry:
            continue
        try:
            module = importlib.import_module(module_name)
            attr_parent = module
            attr_name = func_path
            if "." in func_path:
                parts = func_path.split(".")
                for part in parts[:-1]:
                    attr_parent = getattr(attr_parent, part, None)
                    if attr_parent is None:
                        break
                attr_name = parts[-1]

            if attr_parent is None:
                debug_log(
                    "debug.instrumentation",
                    f"Ziel nicht gefunden: {target_id}",
                    category="stability",
                )
                registry.add(target_id)
                continue

            func = getattr(attr_parent, attr_name, None)
            if func is None or not callable(func):
                debug_log(
                    "debug.instrumentation",
                    f"Ziel nicht gefunden: {target_id}",
                    category="stability",
                )
                registry.add(target_id)
                continue

            if getattr(func, "_debug_instrumented", False):
                registry.add(target_id)
                continue

            @functools.wraps(func)
            def wrapper(
                *args: Any,
                __func=func,
                __target=target_id,
                    **kwargs: Any):
                call_summary = _summarise_call(args, kwargs)
                debug_log(
                    __target,
                    "Aufruf gestartet",
                    category=category,
                    call=call_summary,
                )
                start = time.perf_counter()
                try:
                    result = __func(*args, **kwargs)
                except Exception as exc:  # pragma: no cover - runtime instrumentation
                    duration_ms = (time.perf_counter() - start) * 1000
                    debug_log(
                        __target,
                        "Aufruf fehlgeschlagen",
                        category="stability",
                        duration_ms=duration_ms,
                        error=repr(exc),
                        call=call_summary,
                        level=logging.ERROR,
                    )
                    raise
                duration_ms = (time.perf_counter() - start) * 1000
                result_summary = _summarise_result(result)
                debug_log(
                    __target,
                    "Aufruf erfolgreich",
                    category=category,
                    duration_ms=duration_ms,
                    result=result_summary,
                )
                return result

            wrapper._debug_instrumented = True  # type: ignore[attr-defined]
            setattr(attr_parent, attr_name, wrapper)
            registry.add(target_id)
            debug_log(
                "debug.instrumentation",
                f"Instrumentiert: {target_id}",
                category="performance",
            )
        except ImportError as exc:
            debug_log(
                "debug.instrumentation",
                f"Import fehlgeschlagen: {target_id}",
                category="stability",
                error=repr(exc),
            )
            registry.add(target_id)


# ---------------------------------------------------------------------------
# Event storage helpers
# ---------------------------------------------------------------------------


def get_debug_events(limit: int | None = None) -> list[dict[str, Any]]:
    if st is None:
        return []
    events: list[dict[str, Any]] = st.session_state.get(DEBUG_SESSION_KEY, [])
    if limit is not None and limit > 0:
        return events[-limit:]
    return events


def clear_debug_events() -> None:
    if st is None:
        return
    st.session_state[DEBUG_SESSION_KEY] = []


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------


def render_debug_toolbar(location: str = "sidebar") -> None:
    """Render the debug toggle plus latest events in the UI."""
    if st is None:
        return

    container = st.sidebar if location == "sidebar" else st.container()
    widget_prefix = f"{location}_"
    with container:
        st.markdown("---")
        st.markdown("### 🛠️ Debug-Tools")

        enabled = bool(st.session_state.get(DEBUG_MODE_KEY, False))
        new_enabled = st.toggle(
            "Debug-Modus aktivieren",
            value=enabled,
            key=f"{widget_prefix}debug_mode_toggle",
            help="Aktiviert ausführliche Logs aller Schritte."
        )

        if new_enabled != enabled:
            set_debug_mode(new_enabled)

        filters = _ensure_category_filters()
        with st.expander("Kategorie-Filter und Optionen", expanded=False):
            cols = st.columns(2)
            items = list(filters.items())
            half = (len(items) + 1) // 2
            for column, chunk in zip(
                    cols, [items[:half], items[half:]], strict=False):
                with column:
                    for key, value in chunk:
                        toggled = st.checkbox(
                            key,
                            value=value,
                            key=f"{widget_prefix}debug_category_{key}",
                        )
                        if toggled != value:
                            set_category_enabled(key, toggled)

            if st.button(
                "Instrumentierung erneut anwenden",
                    key=f"{widget_prefix}debug_reinstrument"):
                ensure_instrumentation()
                st.success("Instrumentierung aktualisiert")

        cols = st.columns([3, 1])
        with cols[0]:
            if st.button("Debug-Logs leeren",
                         key=f"{widget_prefix}debug_clear_button"):
                clear_debug_events()
        with cols[1]:
            st.caption(
                f"Events: {len(st.session_state.get(DEBUG_SESSION_KEY, []))}")

        active_filters = _get_category_filters()
        events_to_display = [
            event for event in reversed(get_debug_events(limit=200))
            if active_filters.get(event.get("category", "general"), True)
        ]

        if events_to_display:
            st.markdown("#### Zuletzt protokolliert")
            for event in events_to_display[:20]:
                title = f"[{event['timestamp']}] [{event.get('category',
                                                             'general')}] {event['source']}"
                with st.expander(title):
                    st.write(event['message'])
                    if event.get('context'):
                        st.json(event['context'])
        else:
            st.caption("Keine Events für die ausgewählten Kategorien.")


__all__ = [
    "debug_log",
    "debug_timer",
    "debug_enabled",
    "init_debug_mode",
    "set_debug_mode",
    "set_category_enabled",
    "is_category_enabled",
    "log_payload",
    "ensure_instrumentation",
    "render_debug_toolbar",
    "get_debug_events",
    "clear_debug_events",
]
