from typing import Any

import streamlit as st

DEFAULT_SERVICE_DISPLAY_CONFIG = {
    "service_checkmarks_enabled": True,
    # Neuer Default: kein Symbol
    "service_symbol_style": "none",  # check|checkbox|dot|none
    "service_value_column_hidden": False,
    "service_symbol_color": "#000000",
    "service_label_color": "#000000",
}


def _ensure_defaults(cfg: dict[str, Any]) -> None:
    # Ergänze fehlende Keys ohne bestehende Werte zu überschreiben
    for k, v in DEFAULT_SERVICE_DISPLAY_CONFIG.items():
        cfg.setdefault(k, v)


def reset_service_display_config(cfg: dict[str, Any]) -> None:
    for k, v in DEFAULT_SERVICE_DISPLAY_CONFIG.items():
        cfg[k] = v


def render_service_display_config(
        pdf_design_config: dict[str, Any], *, expanded: bool = True, inline: bool = False) -> None:
    """Zeigt die vereinheitlichte UI für die Dienstleistungs-Darstellung auf Seite 6.

    Erwartet ein dict pdf_design_config (aus st.session_state['pdf_design_config']).
    Aktualisiert Werte in-place und sorgt für Defaults.
    """
    if pdf_design_config is None:
        st.warning("pdf_design_config nicht initialisiert.")
        return

    _ensure_defaults(pdf_design_config)

    if inline:
        st.subheader("Seite 6: Dienstleistungen & Produkte – Darstellung")
        col1, col2 = st.columns(2)
        with col1:
            symbol_options = ["check", "checkbox", "dot", "none"]
            labels_map = {
                "check": "Häkchen",
                "checkbox": "Checkbox",
                "dot": "Punkt",
                "none": "Kein Symbol"
            }
            current_style = pdf_design_config.get(
                "service_symbol_style", "none")
            # Anzeige mit Labels, Speicherung des technischen Werts
            sel_label = st.selectbox(
                "Symbol-Stil",
                [labels_map[o] for o in symbol_options],
                index=symbol_options.index(current_style),
                help="Stil des Symbols vor jeder Dienstleistung."
            )
            # Reverse Mapping
            inv_map = {v: k for k, v in labels_map.items()}
            pdf_design_config["service_symbol_style"] = inv_map[sel_label]
            pdf_design_config["service_checkmarks_enabled"] = st.checkbox(
                "Dienstleistungen anzeigen (Symbolspalte)",
                value=pdf_design_config["service_checkmarks_enabled"],
                help="Deaktiviert die komplette Symbolspalte für Dienstleistungen.")
            pdf_design_config["service_value_column_hidden"] = st.checkbox(
                "Wertspalte bei Dienstleistungen & Produkten ausblenden",
                value=pdf_design_config["service_value_column_hidden"],
                help="Blendet die Werte (rechts) für Dienstleistungen UND Produkte aus.")
        with col2:
            pdf_design_config["service_symbol_color"] = st.color_picker(
                "Farbe Symbole", value=pdf_design_config["service_symbol_color"],)
            pdf_design_config["service_label_color"] = st.color_picker(
                "Farbe Texte", value=pdf_design_config["service_label_color"],)
        reset = st.button(
            "Darstellungs-Optionen zurücksetzen",
            type="secondary",
            key="service_display_reset_btn")
        if reset:
            reset_service_display_config(pdf_design_config)
            st.rerun()
        st.caption(
            "Diese Optionen steuern die Darstellung der Dienstleistungen (und optional Produktwerte) auf Seite 6 des Angebots-PDF.")
        # Persistenz sicherstellen
        try:
            if 'pdf_design_config' in st.session_state:
                st.session_state['pdf_design_config'].update(pdf_design_config)
            else:
                st.session_state['pdf_design_config'] = dict(pdf_design_config)
        except Exception:
            pass
        return
    exp = st.expander(
        "Darstellung Dienstleistungen & Produkte (Seite 6)",
        expanded=expanded)
    with exp:
        _render_service_display_inner(pdf_design_config)
        reset = st.button(
            "Darstellungs-Optionen zurücksetzen",
            type="secondary",
            key="service_display_reset_btn")
        if reset:
            reset_service_display_config(pdf_design_config)
            st.rerun()
        st.caption(
            "Diese Optionen steuern die Darstellung der Dienstleistungen (und optional Produktwerte) auf Seite 6 des Angebots-PDF.")


def _render_service_display_inner(pdf_design_config: dict[str, Any]) -> None:
    col1, col2 = st.columns(2)
    with col1:
        symbol_options = ["check", "checkbox", "dot", "none"]
        labels_map = {
            "check": "Häkchen",
            "checkbox": "Checkbox",
            "dot": "Punkt",
            "none": "Kein Symbol"}
        current_style = pdf_design_config.get("service_symbol_style", "none")
        sel_label = st.selectbox(
            "Symbol-Stil",
            [labels_map[o] for o in symbol_options],
            index=symbol_options.index(current_style),
            help="Stil des Symbols vor jeder Dienstleistung.",
            key="srv_symbol_style_expander"
        )
        inv_map = {v: k for k, v in labels_map.items()}
        pdf_design_config["service_symbol_style"] = inv_map[sel_label]
        pdf_design_config["service_checkmarks_enabled"] = st.checkbox(
            "Dienstleistungen anzeigen (Symbolspalte)",
            value=pdf_design_config["service_checkmarks_enabled"],
            help="Deaktiviert die komplette Symbolspalte für Dienstleistungen.",
            key="srv_checkmarks_enabled_expander")
        pdf_design_config["service_value_column_hidden"] = st.checkbox(
            "Wertspalte bei Dienstleistungen & Produkten ausblenden",
            value=pdf_design_config["service_value_column_hidden"],
            help="Blendet die Werte (rechts) für Dienstleistungen UND Produkte aus.",
            key="srv_value_col_hidden_expander")
    with col2:
        pdf_design_config["service_symbol_color"] = st.color_picker(
            "Farbe Symbole",
            value=pdf_design_config["service_symbol_color"],
            key="srv_symbol_color_expander"
        )
        pdf_design_config["service_label_color"] = st.color_picker(
            "Farbe Texte",
            value=pdf_design_config["service_label_color"],
            key="srv_label_color_expander"
        )
