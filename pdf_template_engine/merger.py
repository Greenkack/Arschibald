# merger.py  (nur die Pfad-Definition und Schleife ändern)
import io
from pathlib import Path

from pypdf import PdfReader, PdfWriter

# Use the correct path to template files
BG = Path(__file__).parent.parent / "pdf_templates_static" / "notext"


def merge_first_eight_pages(overlay_bytes: bytes) -> bytes:
    """Merges 8 pages with their background templates.

    Args:
        overlay_bytes: PDF bytes containing the overlay content for
            8 pages

    Returns:
        Merged PDF bytes with backgrounds and overlays for 8 pages
    """
    writer = PdfWriter()
    ovl = PdfReader(io.BytesIO(overlay_bytes))

    # Changed from range(1, 8) to range(1, 9) for 8 pages
    for i in range(1, 9):
        base = PdfReader(BG / f"nt_nt_{i:02d}.pdf").pages[0]
        base.merge_page(ovl.pages[i - 1])    # Overlay drüber
        writer.add_page(base)

    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def merge_first_seven_pages(overlay_bytes: bytes) -> bytes:
    """DEPRECATED: Use merge_first_eight_pages() instead.

    This function is kept for backward compatibility but will be
    removed in a future version.
    The PDF system now generates 8 pages by default.

    Args:
        overlay_bytes: PDF bytes containing the overlay content

    Returns:
        Merged PDF bytes (now returns 8 pages via
            merge_first_eight_pages)
    """
    import warnings
    warnings.warn(
        "merge_first_seven_pages is deprecated, use "
        "merge_first_eight_pages instead",
        DeprecationWarning,
        stacklevel=2
    )
    return merge_first_eight_pages(overlay_bytes)
