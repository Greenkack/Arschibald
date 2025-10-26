# === AUTO-GENERATED INSERT PATCH ===
# target_module: pdf_template_engine/placeholders.py

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---
from __future__ import annotations

import re
from functools import lru_cache
from typing import Any


# --- DEF BLOCK START: func USE_PERFORM_CALCULATIONS ---
def USE_PERFORM_CALCULATIONS(context: dict[str, Any]) -> dict[str, Any]:
    """
    DEF Block:
    Nutzt calculations.perform_calculations(context) und liefert die berechneten Werte
    zurück. Side-effect-frei; passt sich an bestehende Struktur an.
    """
    return perform_calculations(context)
# --- DEF BLOCK END ---


# --- DEF BLOCK START: func _fit_to_float ---
def _fit_to_float(x: Any) -> float:
    try:
        return float(str(x).replace(',', '.'))
    except Exception:
        return 0.0
# --- DEF BLOCK END ---


# --- DEF BLOCK START: func _normalize_tariff_to_eur_per_kwh ---
def _normalize_tariff_to_eur_per_kwh(val: Any) -> float | None:
    if val in (None, ""):
        return None
    v = _fit_to_float(val)
    if v == 0.0:
        return 0.0
    return v / 100.0 if v > 1.0 else v
# --- DEF BLOCK END ---


# --- DEF BLOCK START: func resolve_feed_in_tariff_eur_per_kwh ---
@lru_cache(maxsize=128)
def resolve_feed_in_tariff_eur_per_kwh(
    anlage_kwp: float,
    mode: str,
    load_admin_setting_func,
    analysis_results_snapshot: tuple | None = None,
    project_data_snapshot: tuple | None = None,
    default_parts_under_10_eur_per_kwh: float = 0.0786,
) -> float:
    """Neue robuste Einspeisetarif-Ermittlung (€/kWh). Nutzt Admin-Settings, sonst analysis_results, sonst Default."""
    try:
        mode_l = (mode or "parts").strip().lower()
        if mode_l not in ("parts", "full"):
            mode_l = "parts"
        tariffs_data = {}
        try:
            tariffs_data = load_admin_setting_func("feed_in_tariffs", {}) or {}
        except Exception:
            tariffs_data = {}
        tariffs_list = tariffs_data.get(
            mode_l, []) if isinstance(
            tariffs_data, dict) else []
        chosen = None
        for trf in tariffs_list or []:
            try:
                if _fit_to_float(
                    trf.get(
                        "kwp_min",
                        0)) <= anlage_kwp <= _fit_to_float(
                    trf.get(
                        "kwp_max",
                        999)):
                    chosen = _normalize_tariff_to_eur_per_kwh(
                        trf.get("ct_per_kwh"))
                    break
            except Exception:
                continue
        if chosen is None and analysis_results_snapshot:
            # Snapshot tuple: (einspeiseverguetung_eur_per_kwh, ... ) – wir
            # übergeben hier nur einen Wert bei Bedarf
            try:
                ar_val = analysis_results_snapshot[0]
                norm = _normalize_tariff_to_eur_per_kwh(ar_val)
                if norm is not None and norm > 0:
                    chosen = norm
            except Exception:
                pass
        if chosen is None or chosen <= 0:
            chosen = default_parts_under_10_eur_per_kwh
        return float(chosen)
    except Exception:
        return default_parts_under_10_eur_per_kwh
# --- DEF BLOCK END ---


# --- DEF BLOCK START: func get_feed_in_tariff_eur_per_kwh ---
def get_feed_in_tariff_eur_per_kwh(anlage_kwp: float, mode: str, load_admin_setting_func) -> float:  # noqa: D401
    return resolve_feed_in_tariff_eur_per_kwh(
        anlage_kwp, mode, load_admin_setting_func)
# --- DEF BLOCK END ---


# --- DEF BLOCK START: func fmt_number ---
def fmt_number(
        value: Any,
        decimal_places: int = 2,
        suffix: str = "",
        force_german: bool = True) -> str:
    """Formatiert Zahlen im deutschen Format mit Punkt als Tausendertrennzeichen und Komma als Dezimaltrennzeichen."""
    try:
        if value is None or value == "":
            return "0,00" + (" " + suffix if suffix else "")

        # String bereinigen falls nötig
        if isinstance(value, str):
            # Entferne Einheiten und unerwünschte Zeichen
            clean_val = re.sub(r'[^\d,.-]', '', value)
            clean_val = clean_val.replace(',', '.')
        else:
            clean_val = str(value)

        num = float(clean_val)

        if force_german:
            # Deutsche Formatierung: Tausendertrennzeichen = Punkt,
            # Dezimaltrennzeichen = Komma
            if decimal_places == 0:
                formatted = f"{
                    num:,.0f}".replace(
                    ',',
                    '#').replace(
                    '.',
                    ',').replace(
                    '#',
                    '.')
            else:
                formatted = f"{
                    num:,.{decimal_places}f}".replace(
                    ',',
                    '#').replace(
                    '.',
                    ',').replace(
                    '#',
                    '.')
        else:
            # Fallback: Standard-Formatierung
            formatted = f"{num:.{decimal_places}f}"

        return formatted + (" " + suffix if suffix else "")

    except (ValueError, TypeError):
        return "0" + (",00" if decimal_places > 0 else "") + \
            (" " + suffix if suffix else "")
# --- DEF BLOCK END ---
