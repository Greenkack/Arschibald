"""
Core module initialization
"""

from backend.core.config import settings
from backend.core.database import get_db, engine, Base

# PDF byte generation is imported separately to avoid circular dependencies
# Import with: from backend.core.pdf_bytes import PDFByteMixin, etc.

__all__ = ["settings", "get_db", "engine", "Base"]
