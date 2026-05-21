"""
Configuration file for Multi-PDF Positioning System
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
PDF_DIR = BASE_DIR / "pdf_templates_static" / "multi"
YML_DIR = BASE_DIR / "coords_multi"
BACKUP_DIR = BASE_DIR / "coords_multi_backup"
OUTPUT_DIR = BASE_DIR / "multi_pdf_positioning" / "output"
ANALYSIS_DIR = BASE_DIR / "multi_pdf_positioning" / "analysis"

# Ensure directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

# Firmen and Seiten configuration
FIRMEN = [1, 2, 3, 4, 5, 6]
SEITEN = [1, 2, 3, 4, 5, 6, 7, 8]

# PDF page dimensions (A4 in points)
PAGE_WIDTH = 595
PAGE_HEIGHT = 842

# Positioning rules
POSITIONING_RULES = {
    "min_margin": 10,  # Minimum distance from edge
    "min_spacing": 5,  # Minimum distance between elements
    "page_width": PAGE_WIDTH,
    "page_height": PAGE_HEIGHT,
}

# Processing options
CREATE_BACKUP = True
VALIDATE_OUTPUT = True
PARALLEL_PROCESSING = False  # Set to True for faster processing

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FILE = BASE_DIR / "multi_pdf_positioning" / "positioning.log"
