# auto_chart_generator.py
"""
AUTOMATISCHE CHART-GENERIERUNG
Erstellt fehlende Charts on-the-fly aus vorhandenen Daten
"""

from __future__ import annotations

import logging
from io import BytesIO
from typing import Any


def generate_placeholder_chart(
        chart_key: str,
        width: int = 800,
        height: int = 600) -> bytes:
    """
    Generiert ein Platzhalter-Chart als PNG

    Args:
        chart_key: Name des Charts
        width: Breite in Pixeln
        height: Höhe in Pixeln

    Returns:
        PNG-Bytes
    """
    try:
        import matplotlib
        import matplotlib.pyplot as plt
        matplotlib.use('Agg')

        fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)

        # Freundlicher Titel
        title = chart_key.replace('_chart_bytes', '').replace('_', ' ').title()

        # Text in der Mitte
        ax.text(0.5, 0.5, f"📊 {title}\n\nChart wird nach Berechnung generiert",
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=16,
                color='#666',
                transform=ax.transAxes)

        ax.axis('off')
        ax.set_facecolor('#f9f9f9')
        fig.patch.set_facecolor('#ffffff')

        # Als Bytes speichern
        buf = BytesIO()
        plt.savefig(
            buf,
            format='png',
            bbox_inches='tight',
            facecolor='#ffffff')
        plt.close(fig)
        buf.seek(0)

        return buf.read()

    except ImportError:
        # Fallback ohne matplotlib
        return create_simple_placeholder_png(chart_key)
    except Exception as e:
        logging.error(f"Fehler beim Generieren des Platzhalter-Charts: {e}")
        return create_simple_placeholder_png(chart_key)


def create_simple_placeholder_png(chart_key: str) -> bytes:
    """
    Erstellt ein einfaches Platzhalter-PNG ohne matplotlib

    Returns:
        PNG-Bytes (1x1 transparentes Pixel als Fallback)
    """
    try:
        from PIL import Image, ImageDraw, ImageFont

        # 800x600 weißes Bild
        img = Image.new('RGB', (800, 600), color='#ffffff')
        draw = ImageDraw.Draw(img)

        # Text
        title = chart_key.replace('_chart_bytes', '').replace('_', ' ').title()
        text = f"📊 {title}\n\nChart wird nach Berechnung generiert"

        # Zentriert
        draw.text((400, 300), text, fill='#666666', anchor='mm')

        # Als PNG
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)

        return buf.read()

    except ImportError:
        # Ultra-Fallback: 1x1 transparentes PNG
        # PNG-Header für 1x1 transparentes Bild
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        return png_data


def auto_generate_missing_charts(
    analysis_results: dict[str, Any],
    chart_keys_needed: list[str]
) -> dict[str, Any]:
    """
    Generiert automatisch fehlende Charts als Platzhalter

    Args:
        analysis_results: Bestehende Ergebnisse
        chart_keys_needed: Liste der benötigten Chart-Keys

    Returns:
        Erweiterte analysis_results mit Platzhalter-Charts
    """
    if not isinstance(analysis_results, dict):
        analysis_results = {}

    generated_count = 0

    for chart_key in chart_keys_needed:
        # Prüfe ob Chart bereits existiert
        if chart_key in analysis_results and analysis_results[chart_key] is not None:
            continue

        # Generiere Platzhalter
        try:
            placeholder_bytes = generate_placeholder_chart(chart_key)
            analysis_results[chart_key] = placeholder_bytes
            generated_count += 1

        except Exception as e:
            logging.error(f"Fehler beim Generieren von {chart_key}: {e}")

    if generated_count > 0:
        logging.info(f"✅ {generated_count} Platzhalter-Charts generiert")

    return analysis_results


def ensure_all_charts_exist(
    analysis_results: dict[str, Any]
) -> dict[str, Any]:
    """
    Stellt sicher dass ALLE 55 Charts existieren (mit Platzhaltern wenn nötig)

    Args:
        analysis_results: Bestehende Ergebnisse

    Returns:
        Vollständige analysis_results mit ALLEN Charts
    """
    try:
        from pdf_ui import CHART_KEY_TO_FRIENDLY_NAME_MAP

        all_chart_keys = list(CHART_KEY_TO_FRIENDLY_NAME_MAP.keys())

        return auto_generate_missing_charts(
            analysis_results=analysis_results,
            chart_keys_needed=all_chart_keys
        )

    except ImportError:
        logging.error("Konnte CHART_KEY_TO_FRIENDLY_NAME_MAP nicht laden")
        return analysis_results
    except Exception as e:
        logging.error(f"Fehler beim Sicherstellen aller Charts: {e}")
        return analysis_results


def auto_fix_pdf_charts(
    analysis_results: dict[str, Any],
    force_all: bool = False
) -> dict[str, Any]:
    """
    AUTO-FIX: Stellt sicher dass alle Charts verfügbar sind

    Args:
        analysis_results: Bestehende Ergebnisse
        force_all: Wenn True, werden ALLE 55 Charts erzwungen (mit Platzhaltern)

    Returns:
        Korrigierte analysis_results
    """
    if force_all:
        # Erzwinge ALLE Charts
        return ensure_all_charts_exist(analysis_results)
    # Nur fehlende kritische Charts
    critical_charts = [
        'monthly_prod_cons_chart_bytes',
        'cost_projection_chart_bytes',
        'cumulative_cashflow_chart_bytes',
        'roi_chart_bytes',
        'energy_balance_chart_bytes',
    ]

    return auto_generate_missing_charts(
        analysis_results=analysis_results,
        chart_keys_needed=critical_charts
    )


# ============================================================================
# INTEGRATION MIT SESSION STATE
# ============================================================================

def auto_fix_session_state_charts(force_all: bool = True):
    """
    AUTO-FIX für Streamlit Session State

    Verwendung in admin_panel.py:
        from auto_chart_generator import auto_fix_session_state_charts

        # Nach perform_calculations():
        auto_fix_session_state_charts(force_all=True)

    Args:
        force_all: Wenn True, werden ALLE 55 Charts erzwungen
    """
    try:
        import streamlit as st

        # Prüfe ob analysis_results vorhanden
        if 'analysis_results' not in st.session_state:
            return

        analysis_results = st.session_state.analysis_results

        # Auto-Fix
        fixed_results = auto_fix_pdf_charts(
            analysis_results=analysis_results,
            force_all=force_all
        )

        # Zurückschreiben
        st.session_state.analysis_results = fixed_results

        # Zähle Charts
        chart_count = sum(
            1 for key, value in fixed_results.items()
            if key.endswith('_chart_bytes') and value is not None
        )

        logging.info(f"🔧 Auto-Fix: {chart_count} Charts in Session State")

    except Exception as e:
        logging.error(f"Fehler beim Auto-Fix von Session State: {e}")


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def get_chart_availability_report(
        analysis_results: dict[str, Any]) -> dict[str, Any]:
    """
    Erstellt einen Report über Chart-Verfügbarkeit

    Returns:
        Dict mit Statistiken
    """
    try:
        from pdf_ui import CHART_KEY_TO_FRIENDLY_NAME_MAP

        all_charts = list(CHART_KEY_TO_FRIENDLY_NAME_MAP.keys())

        available = []
        missing = []
        placeholder = []

        for chart_key in all_charts:
            if chart_key not in analysis_results or analysis_results[chart_key] is None:
                missing.append(chart_key)
            else:
                chart_bytes = analysis_results[chart_key]
                # Prüfe ob Platzhalter (sehr klein)
                if isinstance(chart_bytes, bytes) and len(chart_bytes) < 500:
                    placeholder.append(chart_key)
                else:
                    available.append(chart_key)

        return {
            'total': len(all_charts),
            'available': len(available),
            'missing': len(missing),
            'placeholder': len(placeholder),
            'percentage_available': (
                len(available) /
                len(all_charts) *
                100) if len(all_charts) > 0 else 0,
            'available_list': available,
            'missing_list': missing,
            'placeholder_list': placeholder}

    except Exception as e:
        logging.error(f"Fehler beim Chart-Report: {e}")
        return {'error': str(e)}
