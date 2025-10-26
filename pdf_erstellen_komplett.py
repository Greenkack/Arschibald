from __future__ import annotations

import io
import json
import os
from pathlib import Path
from typing import Any

from pypdf import PdfReader

try:
    from pdf_template_engine import build_dynamic_data, generate_custom_offer_pdf
except Exception as e:
    raise RuntimeError(f"pdf_template_engine nicht verfügbar: {e}")


def _load_texts() -> dict[str, str]:
    """Lädt deutsche Texte aus de.json, falls vorhanden."""
    base_dir = Path(__file__).parent
    de_path = base_dir / "de.json"
    if de_path.exists():
        try:
            return json.loads(de_path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _generate_legacy_pdf_optional(
    project_data: dict[str, Any],
    analysis_results: dict[str, Any],
    company_info: dict[str, Any],
) -> bytes | None:
    """Erzeugt optional die bisherige PDF-Ausgabe (ohne 7-Seiten-Templates).

    Nutzt generate_offer_pdf aus pdf_generator mit disable_main_template_combiner=True,
    sodass nur die alte Ausgabe zurückkommt. Deaktiviert Deckblatt/Anschreiben via inclusion_options.
    """
    try:
        from pdf_generator import generate_offer_pdf
    except Exception:
        return None

    # Abhängigkeiten aus DB/Produkt-DB einbinden
    try:
        from database import (
            get_active_company as db_get_active_company,
        )
        from database import (
            list_company_documents as db_list_company_documents_func,
        )
        from database import (
            load_admin_setting as load_admin_setting_func,
        )
        from database import (
            save_admin_setting as save_admin_setting_func,
        )
    except Exception:
        return None

    try:
        from product_db import (
            get_product_by_id as get_product_by_id_func,
        )
        from product_db import (
            list_products as list_products_func,
        )
    except Exception:
        # Minimal-Fallbacks
        def list_products_func(*args, **kwargs):
            return []

        def get_product_by_id_func(*args, **kwargs):
            return None

    texts = _load_texts()
    active_company = db_get_active_company() or {}
    active_company_id = active_company.get("id")

    inclusion_options = {
        "skip_cover_and_letter": False,
        "include_company_logo": True,
        "include_product_images": True,
        "include_all_documents": True,
        "include_optional_component_details": True,
    }

    try:
        legacy_pdf = generate_offer_pdf(
            project_data=project_data,
            analysis_results=analysis_results,
            company_info=company_info,
            company_logo_base64=company_info.get("logo_base64"),
            selected_title_image_b64=True,
            selected_offer_title_text="",
            selected_cover_letter_text="",
            sections_to_include=True,
            inclusion_options=inclusion_options,
            load_admin_setting_func=load_admin_setting_func,
            save_admin_setting_func=save_admin_setting_func,
            list_products_func=list_products_func,
            get_product_by_id_func=get_product_by_id_func,
            db_list_company_documents_func=db_list_company_documents_func,
            active_company_id=active_company_id,
            texts=texts,
            use_modern_design=True,
            disable_main_template_combiner=True,  # wichtig, sonst Rekursion
        )
        return legacy_pdf
    except Exception:
        return None


def _read_json(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def main(
    project_json: str | None = None,
    analysis_json: str | None = None,
    company_json: str | None = None,
    additional_pdf_path: str | None = None,
    output_pdf: str | None = None,
):
    base_dir = Path(__file__).parent
    coords_dir = base_dir / "coords"
    bg_dir = base_dir / "pdf_templates_static" / "notext"

    project_data = _read_json(project_json)
    analysis_results = _read_json(analysis_json)
    company_info = _read_json(company_json)

    # Dynamische Werte aus App-Daten ableiten
    dynamic_data = build_dynamic_data(
        project_data, analysis_results, company_info)

    # Optionalen Anhang laden
    additional_pdf_bytes = None
    if additional_pdf_path and Path(additional_pdf_path).exists():
        additional_pdf_bytes = Path(additional_pdf_path).read_bytes()

    # Erzeugen und verschmelzen
    pdf_bytes = generate_custom_offer_pdf(
        coords_dir, bg_dir, dynamic_data, additional_pdf_bytes)

    out_path = Path(output_pdf or (base_dir / "recreated_full.pdf"))
    out_path.write_bytes(pdf_bytes)
    # Kurzer Report
    try:
        r = PdfReader(io.BytesIO(pdf_bytes))
        print(f"Erstellt: {out_path} (Seiten: {len(r.pages)})")
    except Exception:
        print(f"Erstellt: {out_path}")


def render_ui() -> None:
    """Kleine Streamlit-UI mit Button 'Angebots PDF erstellen'.

    - Erzeugt 6-seitige Template-PDF aus coords/ + notext Templates.
    - Optional hängt die 'alte' PDF-Ausgabe hinten an.
    - Bietet Download und Seitenzählung an.
    """
    try:
        import streamlit as st
    except Exception:
        raise RuntimeError(
            "Streamlit nicht verfügbar. UI kann nicht gerendert werden.")

    base_dir = Path(__file__).parent
    coords_dir = base_dir / "coords"
    bg_dir = base_dir / "pdf_templates_static" / "notext"

    st.title("Angebots-PDF (7 Seiten Templates + optional alte Ausgabe)")

    use_session = st.checkbox(
        "App-Daten aus Session verwenden (falls vorhanden)",
        value=True)

    project_data: dict[str, Any] = {}
    analysis_results: dict[str, Any] = {}
    company_info: dict[str, Any] = {}

    if use_session:
        try:
            import streamlit as st  # type: ignore
            project_data = st.session_state.get("project_data", {})
            analysis_results = st.session_state.get("calculation_results", {})
            # Firmeninfos: wenn DB aktiv, hole aktive Firma; sonst Upload
            # nutzen
            try:
                from database import get_active_company
                company_info = get_active_company() or {}
            except Exception:
                company_info = {}
        except Exception:
            project_data, analysis_results, company_info = {}, {}, {}

    st.markdown("---")
    st.subheader("Eingabedaten (alternativ per Upload)")
    with st.expander("JSON Uploads (falls nicht Session benutzt)", expanded=not use_session):
        c1, c2, c3 = st.columns(3)
        with c1:
            pj = st.file_uploader("project_data.json", type=["json"])
            if pj is not None:
                try:
                    project_data = json.loads(pj.read().decode("utf-8"))
                except Exception as e:
                    st.error(f"Projekt JSON ungültig: {e}")
        with c2:
            aj = st.file_uploader("analysis_results.json", type=["json"])
            if aj is not None:
                try:
                    analysis_results = json.loads(aj.read().decode("utf-8"))
                except Exception as e:
                    st.error(f"Analyse JSON ungültig: {e}")
        with c3:
            cj = st.file_uploader("company_info.json", type=["json"])
            if cj is not None:
                try:
                    company_info = json.loads(cj.read().decode("utf-8"))
                except Exception as e:
                    st.error(f"Firma JSON ungültig: {e}")

    st.markdown("---")
    append_old = st.checkbox(
        "Alte PDF-Ausgabe hinten anhängen (optional)",
        value=True)

    if st.button("Angebots PDF erstellen", type="primary"):
        if not project_data or not isinstance(project_data, dict):
            st.error("Es liegen keine gültigen Projekt-Daten vor.")
            return

        with st.spinner("Generiere PDF..."):
            try:
                dyn = build_dynamic_data(
                    project_data,
                    analysis_results or {},
                    company_info or {})
                additional_pdf_bytes = None
                if append_old:
                    additional_pdf_bytes = _generate_legacy_pdf_optional(
                        project_data, analysis_results or {}, company_info or {})

                pdf_bytes = generate_custom_offer_pdf(
                    coords_dir, bg_dir, dyn, additional_pdf_bytes)
                if not pdf_bytes:
                    st.error("PDF-Erzeugung fehlgeschlagen.")
                    return

                # Seiten zählen
                try:
                    r = PdfReader(io.BytesIO(pdf_bytes))
                    total_pages = len(r.pages)
                except Exception:
                    total_pages = None

                st.success("PDF erstellt.")
                if total_pages is not None:
                    st.info(f"Seitenzahl: {total_pages}")

                filename = f"Angebot_{
                    project_data.get(
                        'customer_data',
                        {}).get(
                        'last_name',
                        'Unbekannt')}_{
                    os.path.basename(
                        str(base_dir))}.pdf"
                st.download_button(
                    label="PDF herunterladen",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                )
            except Exception as e:
                st.error(f"Fehler bei der PDF-Erzeugung: {e}")
                import traceback as _tb
                st.code(_tb.format_exc())


if __name__ == "__main__":
    # Einfache arg-Parsing ohne externe Libs
    import sys
    args = sys.argv[1:]

    def _get(flag: str) -> str | None:
        if flag in args:
            i = args.index(flag)
            return args[i + 1] if i + 1 < len(args) else None
        return None

    # Auto-Detect Streamlit
    try:
        import streamlit as st  # type: ignore
        _is_st = False
        probe = getattr(st, "_is_running_with_streamlit", None)
        if callable(probe):
            _is_st = bool(probe())
        elif isinstance(probe, bool):
            _is_st = probe
        if _is_st:
            render_ui()
            raise SystemExit(0)
    except Exception:
        pass

    if "--ui" in args:
        try:
            render_ui()
            raise SystemExit(0)
        except Exception as e:
            print(f"UI konnte nicht gestartet werden: {e}")

    # CLI-Modus
    main(
        project_json=_get("--project"),
        analysis_json=_get("--analysis"),
        company_json=_get("--company"),
        additional_pdf_path=_get("--append"),
        output_pdf=_get("--out"),
    )
