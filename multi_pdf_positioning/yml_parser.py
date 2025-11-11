"""
YML Parser Module for Multi-PDF Positioning System

This module parses YML coordinate files and extracts text elements with their attributes.
It preserves the original structure and formatting of the YML files.
"""

import re
from dataclasses import dataclass
from typing import List, Tuple, Optional
from pathlib import Path


@dataclass
class YMLElement:
    """
    Represents a text element from a YML coordinate file.
    
    Attributes:
        text: The text content (can be empty string for placeholders)
        position: Tuple of (x1, y1, x2, y2) coordinates
        font: Font name (e.g., "Helvetica-Bold")
        font_size: Font size in points
        color: Color as integer value
        index: Original position in the file (0-based)
        raw_block: Original raw text block for format preservation
    """
    text: str
    position: Tuple[float, float, float, float]
    font: str
    font_size: float
    color: int
    index: int
    raw_block: str = ""


class YMLParser:
    """
    Parser for YML coordinate files.
    
    This parser extracts text elements while preserving the original
    formatting and structure of the YML files.
    """
    
    # Regex patterns for parsing YML elements
    TEXT_PATTERN = re.compile(r'^Text:\s*(.*)$', re.MULTILINE)
    POSITION_PATTERN = re.compile(r'^Position:\s*\(([^)]+)\)$', re.MULTILINE)
    FONT_PATTERN = re.compile(r'^Schriftart:\s*(.+)$', re.MULTILINE)
    FONT_SIZE_PATTERN = re.compile(r'^Schriftgröße:\s*([0-9.]+)$', re.MULTILINE)
    COLOR_PATTERN = re.compile(r'^Farbe:\s*(\d+)$', re.MULTILINE)
    SEPARATOR = "----------------------------------------"
    
    def __init__(self):
        """Initialize the YML parser."""
        self.elements: List[YMLElement] = []
        self.raw_content: str = ""
        self.file_path: Optional[Path] = None
    
    def parse_yml(self, yml_path: str) -> List[YMLElement]:
        """
        Parse a YML coordinate file and extract all text elements.
        
        Args:
            yml_path: Path to the YML file
            
        Returns:
            List of YMLElement objects with all attributes
            
        Raises:
            FileNotFoundError: If the YML file doesn't exist
            ValueError: If the YML format is invalid
        """
        self.file_path = Path(yml_path)
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"YML file not found: {yml_path}")
        
        # Read the entire file content
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.raw_content = f.read()
        
        # Split content into blocks using the separator
        blocks = self._split_into_blocks(self.raw_content)
        
        # Parse each block
        self.elements = []
        for index, block in enumerate(blocks):
            if block.strip():  # Skip empty blocks
                element = self._parse_block(block, index)
                if element:
                    self.elements.append(element)
        
        return self.elements
    
    def _split_into_blocks(self, content: str) -> List[str]:
        """
        Split YML content into individual element blocks.
        
        Args:
            content: Raw YML file content
            
        Returns:
            List of text blocks, one per element
        """
        # Split by separator and keep the separator info
        blocks = content.split(self.SEPARATOR)
        return blocks
    
    def _parse_block(self, block: str, index: int) -> Optional[YMLElement]:
        """
        Parse a single YML block into a YMLElement.
        
        Args:
            block: Text block containing one element's data
            index: Position index in the file
            
        Returns:
            YMLElement object or None if parsing fails
        """
        try:
            # Extract text (can be empty)
            text_match = self.TEXT_PATTERN.search(block)
            text = text_match.group(1).strip() if text_match else ""
            
            # Extract position
            position_match = self.POSITION_PATTERN.search(block)
            if not position_match:
                return None
            
            position_str = position_match.group(1)
            position_values = [float(x.strip()) for x in position_str.split(',')]
            if len(position_values) != 4:
                return None
            position = tuple(position_values)
            
            # Extract font
            font_match = self.FONT_PATTERN.search(block)
            if not font_match:
                return None
            font = font_match.group(1).strip()
            
            # Extract font size
            font_size_match = self.FONT_SIZE_PATTERN.search(block)
            if not font_size_match:
                return None
            font_size = float(font_size_match.group(1))
            
            # Extract color
            color_match = self.COLOR_PATTERN.search(block)
            if not color_match:
                return None
            color = int(color_match.group(1))
            
            # Create element with raw block for format preservation
            element = YMLElement(
                text=text,
                position=position,
                font=font,
                font_size=font_size,
                color=color,
                index=index,
                raw_block=block
            )
            
            return element
            
        except (ValueError, AttributeError, IndexError) as e:
            # Log parsing error but continue
            print(f"Warning: Failed to parse block at index {index}: {e}")
            return None
    
    def get_elements(self) -> List[YMLElement]:
        """
        Get the list of parsed elements.
        
        Returns:
            List of YMLElement objects
        """
        return self.elements
    
    def get_element_by_text(self, text: str) -> Optional[YMLElement]:
        """
        Find an element by its text content.
        
        Args:
            text: Text to search for
            
        Returns:
            YMLElement if found, None otherwise
        """
        for element in self.elements:
            if element.text == text:
                return element
        return None
    
    def get_elements_by_font(self, font: str) -> List[YMLElement]:
        """
        Find all elements with a specific font.
        
        Args:
            font: Font name to search for
            
        Returns:
            List of matching YMLElement objects
        """
        return [elem for elem in self.elements if elem.font == font]
    
    def get_non_empty_elements(self) -> List[YMLElement]:
        """
        Get all elements that have non-empty text.
        
        Returns:
            List of YMLElement objects with text content
        """
        return [elem for elem in self.elements if elem.text.strip()]
    
    def get_empty_elements(self) -> List[YMLElement]:
        """
        Get all elements that have empty text (placeholders).
        
        Returns:
            List of YMLElement objects without text content
        """
        return [elem for elem in self.elements if not elem.text.strip()]
    
    def validate_elements(self) -> Tuple[bool, List[str]]:
        """
        Validate that all parsed elements have valid data.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        for elem in self.elements:
            # Check position bounds (A4 page: 595x842 points)
            x1, y1, x2, y2 = elem.position
            if not (0 <= x1 < x2 <= 595):
                errors.append(f"Element {elem.index}: Invalid X coordinates ({x1}, {x2})")
            if not (0 <= y1 < y2 <= 842):
                errors.append(f"Element {elem.index}: Invalid Y coordinates ({y1}, {y2})")
            
            # Check font size
            if elem.font_size <= 0:
                errors.append(f"Element {elem.index}: Invalid font size ({elem.font_size})")
            
            # Check color
            if elem.color < 0:
                errors.append(f"Element {elem.index}: Invalid color value ({elem.color})")
        
        return len(errors) == 0, errors
    
    def get_statistics(self) -> dict:
        """
        Get statistics about the parsed YML file.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "total_elements": len(self.elements),
            "non_empty_elements": len(self.get_non_empty_elements()),
            "empty_elements": len(self.get_empty_elements()),
            "unique_fonts": len(set(elem.font for elem in self.elements)),
            "unique_colors": len(set(elem.color for elem in self.elements)),
            "file_path": str(self.file_path) if self.file_path else None
        }


def parse_yml(yml_path: str) -> List[YMLElement]:
    """
    Convenience function to parse a YML file.
    
    Args:
        yml_path: Path to the YML file
        
    Returns:
        List of YMLElement objects
    """
    parser = YMLParser()
    return parser.parse_yml(yml_path)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        yml_file = sys.argv[1]
    else:
        yml_file = "coords_multi/seite1_f1.yml"
    
    try:
        parser = YMLParser()
        elements = parser.parse_yml(yml_file)
        
        print(f"\n=== YML Parser Results ===")
        print(f"File: {yml_file}")
        print(f"\nStatistics:")
        stats = parser.get_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print(f"\n=== First 5 Elements ===")
        for elem in elements[:5]:
            print(f"\nElement {elem.index}:")
            print(f"  Text: '{elem.text}'")
            print(f"  Position: {elem.position}")
            print(f"  Font: {elem.font} ({elem.font_size}pt)")
            print(f"  Color: {elem.color}")
        
        # Validate
        is_valid, errors = parser.validate_elements()
        if is_valid:
            print(f"\n✓ All elements are valid")
        else:
            print(f"\n✗ Validation errors:")
            for error in errors:
                print(f"  - {error}")
                
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
