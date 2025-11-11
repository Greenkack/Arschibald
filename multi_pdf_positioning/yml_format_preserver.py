"""
YML Format Preservation Module

This module handles preserving the original formatting of YML files,
including separators, whitespace, and structure.
"""

import re
from typing import List, Dict, Tuple
from pathlib import Path
from multi_pdf_positioning.yml_parser import YMLElement


class YMLFormatPreserver:
    """
    Preserves the original formatting of YML coordinate files.
    
    This class ensures that when YML files are regenerated with new positions,
    all other aspects of the file (separators, whitespace, attribute order) 
    remain exactly as they were.
    """
    
    SEPARATOR = "----------------------------------------"
    
    def __init__(self):
        """Initialize the format preserver."""
        self.original_content: str = ""
        self.blocks: List[str] = []
        self.separators: List[str] = []
        self.file_structure: Dict = {}
    
    def load_original(self, yml_path: str) -> None:
        """
        Load and analyze the original YML file structure.
        
        Args:
            yml_path: Path to the original YML file
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        file_path = Path(yml_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"YML file not found: {yml_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            self.original_content = f.read()
        
        self._analyze_structure()
    
    def _analyze_structure(self) -> None:
        """
        Analyze the structure of the original YML file.
        
        This extracts information about separators, line endings,
        and whitespace patterns.
        """
        # Detect line ending style
        if '\r\n' in self.original_content:
            self.file_structure['line_ending'] = '\r\n'
        else:
            self.file_structure['line_ending'] = '\n'
        
        # Split into blocks
        self.blocks = self.original_content.split(self.SEPARATOR)
        
        # Store separator information (including trailing newlines)
        self.file_structure['separator'] = self.SEPARATOR
        self.file_structure['num_blocks'] = len(self.blocks)
        
        # Analyze each block's structure
        self.file_structure['block_patterns'] = []
        for block in self.blocks:
            if block.strip():
                pattern = self._extract_block_pattern(block)
                self.file_structure['block_patterns'].append(pattern)
    
    def _extract_block_pattern(self, block: str) -> Dict:
        """
        Extract the formatting pattern from a block.
        
        Args:
            block: A single YML block
            
        Returns:
            Dictionary describing the block's format
        """
        lines = block.split('\n')
        
        pattern = {
            'leading_newlines': 0,
            'trailing_newlines': 0,
            'attribute_order': [],
            'indentation': {}
        }
        
        # Count leading empty lines
        for line in lines:
            if line.strip():
                break
            pattern['leading_newlines'] += 1
        
        # Count trailing empty lines
        for line in reversed(lines):
            if line.strip():
                break
            pattern['trailing_newlines'] += 1
        
        # Extract attribute order and indentation
        for line in lines:
            if line.strip():
                if line.startswith('Text:'):
                    pattern['attribute_order'].append('Text')
                    pattern['indentation']['Text'] = len(line) - len(line.lstrip())
                elif line.startswith('Position:'):
                    pattern['attribute_order'].append('Position')
                    pattern['indentation']['Position'] = len(line) - len(line.lstrip())
                elif line.startswith('Schriftart:'):
                    pattern['attribute_order'].append('Schriftart')
                    pattern['indentation']['Schriftart'] = len(line) - len(line.lstrip())
                elif line.startswith('Schriftgröße:'):
                    pattern['attribute_order'].append('Schriftgröße')
                    pattern['indentation']['Schriftgröße'] = len(line) - len(line.lstrip())
                elif line.startswith('Farbe:'):
                    pattern['attribute_order'].append('Farbe')
                    pattern['indentation']['Farbe'] = len(line) - len(line.lstrip())
        
        return pattern
    
    def preserve_formatting(self, element: YMLElement, new_position: Tuple[float, float, float, float]) -> str:
        """
        Create a formatted block for an element with a new position,
        preserving the original formatting.
        
        Args:
            element: The YMLElement to format
            new_position: New position tuple (x1, y1, x2, y2)
            
        Returns:
            Formatted YML block as string
        """
        # Use the original block as template if available
        if element.raw_block:
            return self._update_position_in_block(element.raw_block, new_position)
        
        # Otherwise, use the standard format pattern
        return self._create_block_from_pattern(element, new_position)
    
    def _update_position_in_block(self, block: str, new_position: Tuple[float, float, float, float]) -> str:
        """
        Update only the position in an existing block.
        
        Args:
            block: Original block text
            new_position: New position tuple
            
        Returns:
            Updated block with new position
        """
        # Format the new position
        position_str = f"({new_position[0]}, {new_position[1]}, {new_position[2]}, {new_position[3]})"
        
        # Replace the position line
        position_pattern = re.compile(r'^(Position:\s*)\([^)]+\)(.*)$', re.MULTILINE)
        updated_block = position_pattern.sub(r'\1' + position_str + r'\2', block)
        
        return updated_block
    
    def _create_block_from_pattern(self, element: YMLElement, new_position: Tuple[float, float, float, float]) -> str:
        """
        Create a new block following the standard pattern.
        
        Args:
            element: The YMLElement
            new_position: New position tuple
            
        Returns:
            Formatted YML block
        """
        line_ending = self.file_structure.get('line_ending', '\n')
        
        # Standard format (matching the original files)
        lines = [
            f"Text: {element.text}",
            f"Position: ({new_position[0]}, {new_position[1]}, {new_position[2]}, {new_position[3]})",
            f"Schriftart: {element.font}",
            f"Schriftgröße: {element.font_size}",
            f"Farbe: {element.color}"
        ]
        
        return line_ending.join(lines)
    
    def reconstruct_yml(self, elements: List[YMLElement], new_positions: List[Tuple[float, float, float, float]]) -> str:
        """
        Reconstruct the complete YML file with new positions.
        
        Args:
            elements: List of YMLElement objects
            new_positions: List of new position tuples (same order as elements)
            
        Returns:
            Complete YML file content as string
            
        Raises:
            ValueError: If elements and positions lists don't match
        """
        if len(elements) != len(new_positions):
            raise ValueError(f"Mismatch: {len(elements)} elements but {len(new_positions)} positions")
        
        line_ending = self.file_structure.get('line_ending', '\n')
        separator = self.file_structure.get('separator', self.SEPARATOR)
        
        # Build the new content
        blocks = []
        for element, new_pos in zip(elements, new_positions):
            block = self.preserve_formatting(element, new_pos)
            blocks.append(block)
        
        # Join blocks with separator
        content = (line_ending + separator + line_ending).join(blocks)
        
        # Add final separator and newline if original had it
        if self.original_content.rstrip().endswith(separator):
            content += line_ending + separator + line_ending
        
        return content
    
    def get_structure_info(self) -> Dict:
        """
        Get information about the file structure.
        
        Returns:
            Dictionary with structure information
        """
        return {
            'line_ending': self.file_structure.get('line_ending', 'unknown'),
            'separator': self.file_structure.get('separator', 'unknown'),
            'num_blocks': self.file_structure.get('num_blocks', 0),
            'has_patterns': len(self.file_structure.get('block_patterns', [])) > 0
        }
    
    def validate_preservation(self, original_path: str, new_content: str) -> Tuple[bool, List[str]]:
        """
        Validate that formatting has been preserved correctly.
        
        Args:
            original_path: Path to original file
            new_content: New file content
            
        Returns:
            Tuple of (is_valid, list_of_differences)
        """
        differences = []
        
        # Load original if not already loaded
        if not self.original_content:
            self.load_original(original_path)
        
        # Check line endings
        original_line_ending = '\r\n' if '\r\n' in self.original_content else '\n'
        new_line_ending = '\r\n' if '\r\n' in new_content else '\n'
        if original_line_ending != new_line_ending:
            differences.append(f"Line ending mismatch: original={repr(original_line_ending)}, new={repr(new_line_ending)}")
        
        # Check separator usage
        original_sep_count = self.original_content.count(self.SEPARATOR)
        new_sep_count = new_content.count(self.SEPARATOR)
        if original_sep_count != new_sep_count:
            differences.append(f"Separator count mismatch: original={original_sep_count}, new={new_sep_count}")
        
        # Check number of blocks
        original_blocks = len([b for b in self.original_content.split(self.SEPARATOR) if b.strip()])
        new_blocks = len([b for b in new_content.split(self.SEPARATOR) if b.strip()])
        if original_blocks != new_blocks:
            differences.append(f"Block count mismatch: original={original_blocks}, new={new_blocks}")
        
        # Check that all non-position attributes are preserved
        original_lines = [line for line in self.original_content.split('\n') if line.strip() and not line.startswith('Position:')]
        new_lines = [line for line in new_content.split('\n') if line.strip() and not line.startswith('Position:')]
        
        if len(original_lines) != len(new_lines):
            differences.append(f"Non-position line count mismatch: original={len(original_lines)}, new={len(new_lines)}")
        
        return len(differences) == 0, differences


def preserve_yml_format(yml_path: str, elements: List[YMLElement], 
                       new_positions: List[Tuple[float, float, float, float]]) -> str:
    """
    Convenience function to preserve YML format with new positions.
    
    Args:
        yml_path: Path to original YML file
        elements: List of YMLElement objects
        new_positions: List of new position tuples
        
    Returns:
        New YML content with preserved formatting
    """
    preserver = YMLFormatPreserver()
    preserver.load_original(yml_path)
    return preserver.reconstruct_yml(elements, new_positions)


if __name__ == "__main__":
    # Example usage
    import sys
    from multi_pdf_positioning.yml_parser import YMLParser
    
    if len(sys.argv) > 1:
        yml_file = sys.argv[1]
    else:
        yml_file = "coords_multi/seite1_f1.yml"
    
    try:
        # Parse the YML file
        parser = YMLParser()
        elements = parser.parse_yml(yml_file)
        
        # Load format preserver
        preserver = YMLFormatPreserver()
        preserver.load_original(yml_file)
        
        print(f"\n=== YML Format Preserver ===")
        print(f"File: {yml_file}")
        print(f"\nStructure Info:")
        info = preserver.get_structure_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        # Test: reconstruct with same positions (should be identical except positions might have different float formatting)
        original_positions = [elem.position for elem in elements]
        reconstructed = preserver.reconstruct_yml(elements, original_positions)
        
        print(f"\n=== Validation ===")
        is_valid, differences = preserver.validate_preservation(yml_file, reconstructed)
        if is_valid:
            print("✓ Format preservation validated successfully")
        else:
            print("✗ Format preservation issues:")
            for diff in differences:
                print(f"  - {diff}")
        
        # Show first block comparison
        print(f"\n=== First Block Comparison ===")
        original_first = preserver.original_content.split(preserver.SEPARATOR)[0]
        reconstructed_first = reconstructed.split(preserver.SEPARATOR)[0]
        print("Original:")
        print(original_first[:200])
        print("\nReconstructed:")
        print(reconstructed_first[:200])
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
