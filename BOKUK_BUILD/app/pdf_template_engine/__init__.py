"""
pdf_template_engine

Öffentliche API zum Erzeugen der 7-seitigen Haupt-PDF mittels Templates:
- build_dynamic_data: erzeugt dynamische Werte aus App-Daten
- generate_custom_offer_pdf: erstellt Overlay, merged mit Templates, hängt optional weitere Seiten an
"""

from pathlib import Path
from typing import Any, Dict, Optional

from .dynamic_overlay import (
    append_additional_pages,
    generate_custom_offer_pdf,
    generate_overlay,
    merge_with_background,
)
from .placeholders import PLACEHOLDER_MAPPING, build_dynamic_data

__all__ = [
    "build_dynamic_data",
    "PLACEHOLDER_MAPPING",
    "generate_overlay",
    "merge_with_background",
    "append_additional_pages",
    "generate_custom_offer_pdf",
]
