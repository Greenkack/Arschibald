"""
Standalone unit tests for German Number Formatter

This is a standalone test file that can be run directly without pytest.
"""

import sys
from pathlib import Path
from decimal import Decimal

# Add core directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.german_formatter import (
    GermanNumberFormatter,
    format_german,
    parse_german,
    format_currency_german,
    format_percent_german,
    validate_german
)


def test_format_simple():
    """Test basic formatting"""
    formatter = GermanNumberFormatter()
