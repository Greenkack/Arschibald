from __future__ import annotations

import ast
import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PYTHON_SYNTAX_TARGETS = [
    "gui.py",
    "database.py",
    "product_db.py",
    "pdf_generator.py",
    "doc_output.py",
    "core/session.py",
    "core/session_repository.py",
    "core/alembic/env.py",
    "core/example_navigation_usage.py",
    "pricing/dynamic_key_manager.py",
    "pricing/pricing_validation.py",
    "pricing/vat_manager.py",
]


def test_core_python_files_parse() -> None:
    for relative_path in PYTHON_SYNTAX_TARGETS:
        source_path = ROOT / relative_path
        source = source_path.read_text(encoding="utf-8")
        ast.parse(source, filename=str(source_path))


def test_declared_exports_exist() -> None:
    for module_name in [
        "database",
        "pricing.pricing_validation",
        "pricing.vat_manager",
        "theme_manager",
    ]:
        module = importlib.import_module(module_name)
        missing = [name for name in getattr(module, "__all__", []) if not hasattr(module, name)]
        assert missing == [], f"{module_name} exports missing symbols: {missing}"


def test_custom_content_type_display_is_total() -> None:
    doc_output = importlib.import_module("doc_output")

    assert doc_output.get_custom_content_type_display("text") == ("Text", "TXT")
    assert doc_output.get_custom_content_type_display("image") == ("Bild", "IMG")
    assert doc_output.get_custom_content_type_display("table") == ("Tabelle", "TBL")
    assert doc_output.get_custom_content_type_display("unknown") == ("Inhalt", "DOC")


def test_product_db_import_error_message_keeps_exception_text() -> None:
    product_db = importlib.import_module("product_db")

    message = product_db.format_database_import_error("Importfehler", RuntimeError("boom"))

    assert "Importfehler" in message
    assert "boom" in message


def test_plaintext_pdf_fallback_returns_pdf_bytes_or_none() -> None:
    pdf_generator = importlib.import_module("pdf_generator")

    payload = pdf_generator._create_plaintext_pdf_fallback(
        project_data={"customer_data": {"first_name": "Ada", "last_name": "Lovelace"}},
        analysis_results={"total_cost": 1234.56},
        texts={"app_title": "ARSCHIBALD"},
        company_info={"name": "Example GmbH"},
        selected_offer_title_text="Testangebot",
        selected_cover_letter_text="Kurztext",
    )

    assert payload is None or payload.startswith(b"%PDF")
