"""
YML Generator Module for Multi-PDF Positioning System

This module generates updated YML coordinate files with new positions while
preserving all other attributes and formatting. It ensures that only position
coordinates are modified, keeping text, fonts, colors, and structure intact.
"""

import re
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from multi_pdf_positioning.yml_parser import YMLElement, YMLParser
from multi_pdf_positioning.yml_format_preserver import YMLFormatPreserver


class YMLGenerator:
    """
    Generator for YML coordinate files with updated positions.
    
    This class takes parsed YML elements and new positions, then generates
    updated YML files while preserving all formatting and non-position attributes.
    """
    
    SEPARATOR = "----------------------------------------"
    
    def __init__(self):
        """Initialize the YML generator."""
        self.format_preserver: Optional[YMLFormatPreserver] = None
        self.original_elements: List[YMLElement] = []
        self.validation_errors: List[str] = []
    
    def format_position(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float
    ) -> str:
        """
        Format position coordinates for YML output.
        
        This ensures consistent formatting of position tuples matching
        the original YML file format.
        
        Args:
            x1: Left X coordinate
            y1: Bottom Y coordinate
            x2: Right X coordinate
            y2: Top Y coordinate
            
        Returns:
            Formatted position string like "(48.0, 70.0, 220.0, 87.0)"
        """
        # Format with one decimal place to match original format
        return f"({x1}, {y1}, {x2}, {y2})"
    
    def generate_yml(
        self,
        elements: List[YMLElement],
        new_positions: List[Tuple[float, float, float, float]],
        output_path: str,
        original_yml_path: Optional[str] = None
    ) -> str:
        """
        Generate a YML file with updated positions.
        
        This is the main function that creates a new YML file with updated
        position coordinates while preserving all other attributes and formatting.
        
        Args:
            elements: List of YMLElement objects with original data
            new_positions: List of new position tuples (x1, y1, x2, y2)
            output_path: Path where the new YML file should be written
            original_yml_path: Path to original YML file for format preservation
                              (uses output_path if None)
            
        Returns:
            The generated YML content as a string
            
        Raises:
            ValueError: If elements and positions lists don't match in length
            FileNotFoundError: If original YML file doesn't exist
        """
        # Validate inputs
        if len(elements) != len(new_positions):
            raise ValueError(
                f"Mismatch: {len(elements)} elements but {len(new_positions)} positions"
            )
        
        # Store original elements for validation
        self.original_elements = elements
        
        # Determine original file path for format preservation
        if original_yml_path is None:
            original_yml_path = output_path
        
        # Load format preserver
        self.format_preserver = YMLFormatPreserver()
        
        try:
            self.format_preserver.load_original(original_yml_path)
        except FileNotFoundError:
            # If original doesn't exist, we'll create with default formatting
            print(f"Warning: Original file not found, using default formatting")
            self.format_preserver = None
        
        # Generate the new YML content
        if self.format_preserver:
            # Use format preserver to maintain original formatting
            yml_content = self.format_preserver.reconstruct_yml(elements, new_positions)
        else:
            # Generate with default formatting
            yml_content = self._generate_with_default_format(elements, new_positions)
        
        # Write to output file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(yml_content)
        
        return yml_content
    
    def _generate_with_default_format(
        self,
        elements: List[YMLElement],
        new_positions: List[Tuple[float, float, float, float]]
    ) -> str:
        """
        Generate YML content with default formatting.
        
        This is used when the original file is not available for format preservation.
        
        Args:
            elements: List of YMLElement objects
            new_positions: List of new position tuples
            
        Returns:
            YML content as string
        """
        blocks = []
        
        for element, new_pos in zip(elements, new_positions):
            # Format position
            position_str = self.format_position(
                new_pos[0], new_pos[1], new_pos[2], new_pos[3]
            )
            
            # Create block with all attributes
            block_lines = [
                f"Text: {element.text}",
                f"Position: {position_str}",
                f"Schriftart: {element.font}",
                f"Schriftgröße: {element.font_size}",
                f"Farbe: {element.color}"
            ]
            
            blocks.append('\n'.join(block_lines))
        
        # Join blocks with separator
        content = f'\n{self.SEPARATOR}\n'.join(blocks)
        
        # Add final separator and newline
        content += f'\n{self.SEPARATOR}\n'
        
        return content
    
    def preserve_formatting(
        self,
        element: YMLElement,
        new_position: Tuple[float, float, float, float]
    ) -> str:
        """
        Create a formatted block for an element with preserved formatting.
        
        This function ensures that the original formatting (whitespace,
        separators, attribute order) is maintained when updating positions.
        
        Args:
            element: The YMLElement to format
            new_position: New position tuple (x1, y1, x2, y2)
            
        Returns:
            Formatted YML block as string
        """
        if self.format_preserver:
            return self.format_preserver.preserve_formatting(element, new_position)
        
        # Fallback to default formatting
        position_str = self.format_position(
            new_position[0], new_position[1], new_position[2], new_position[3]
        )
        
        lines = [
            f"Text: {element.text}",
            f"Position: {position_str}",
            f"Schriftart: {element.font}",
            f"Schriftgröße: {element.font_size}",
            f"Farbe: {element.color}"
        ]
        
        return '\n'.join(lines)
    
    def validate_yml_output(
        self,
        yml_path: str,
        original_elements: Optional[List[YMLElement]] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate that a generated YML file is correct.
        
        This function checks that:
        - All original elements are present
        - Only positions have changed
        - YML format is valid
        - All attributes except position are preserved
        
        Args:
            yml_path: Path to the YML file to validate
            original_elements: Original elements to compare against
                              (uses stored elements if None)
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Use stored original elements if not provided
        if original_elements is None:
            original_elements = self.original_elements
        
        if not original_elements:
            errors.append("No original elements available for comparison")
            return False, errors
        
        # Parse the generated YML file
        try:
            parser = YMLParser()
            generated_elements = parser.parse_yml(yml_path)
        except Exception as e:
            errors.append(f"Failed to parse generated YML: {e}")
            return False, errors
        
        # Check element count
        if len(generated_elements) != len(original_elements):
            errors.append(
                f"Element count mismatch: original={len(original_elements)}, "
                f"generated={len(generated_elements)}"
            )
            return False, errors
        
        # Check each element
        for i, (orig, gen) in enumerate(zip(original_elements, generated_elements)):
            # Check text (must be identical)
            if orig.text != gen.text:
                errors.append(
                    f"Element {i}: Text changed from '{orig.text}' to '{gen.text}'"
                )
            
            # Check font (must be identical)
            if orig.font != gen.font:
                errors.append(
                    f"Element {i}: Font changed from '{orig.font}' to '{gen.font}'"
                )
            
            # Check font size (must be identical)
            if orig.font_size != gen.font_size:
                errors.append(
                    f"Element {i}: Font size changed from {orig.font_size} "
                    f"to {gen.font_size}"
                )
            
            # Check color (must be identical)
            if orig.color != gen.color:
                errors.append(
                    f"Element {i}: Color changed from {orig.color} to {gen.color}"
                )
            
            # Position is expected to change, so we don't validate it matches
            # But we do validate it's within bounds
            x1, y1, x2, y2 = gen.position
            if not (0 <= x1 < x2 <= 595):
                errors.append(
                    f"Element {i}: Invalid X coordinates ({x1}, {x2})"
                )
            if not (0 <= y1 < y2 <= 842):
                errors.append(
                    f"Element {i}: Invalid Y coordinates ({y1}, {y2})"
                )
        
        # Validate YML format using format preserver
        if self.format_preserver:
            try:
                # Read generated content
                with open(yml_path, 'r', encoding='utf-8') as f:
                    generated_content = f.read()
                
                # Validate format preservation
                format_valid, format_errors = self.format_preserver.validate_preservation(
                    yml_path, generated_content
                )
                
                if not format_valid:
                    errors.extend(format_errors)
            except Exception as e:
                errors.append(f"Format validation error: {e}")
        
        self.validation_errors = errors
        return len(errors) == 0, errors
    
    def get_validation_report(self) -> Dict[str, any]:
        """
        Get a detailed validation report.
        
        Returns:
            Dictionary with validation statistics and errors
        """
        return {
            "is_valid": len(self.validation_errors) == 0,
            "error_count": len(self.validation_errors),
            "errors": self.validation_errors,
            "original_element_count": len(self.original_elements),
            "has_format_preserver": self.format_preserver is not None
        }
    
    def batch_generate(
        self,
        yml_files: List[str],
        position_calculator_func,
        output_dir: Optional[str] = None
    ) -> Dict[str, bool]:
        """
        Generate multiple YML files in batch.
        
        Args:
            yml_files: List of YML file paths to process
            position_calculator_func: Function that takes elements and returns new positions
            output_dir: Output directory (uses same dir as input if None)
            
        Returns:
            Dictionary mapping file paths to success status
        """
        results = {}
        
        for yml_file in yml_files:
            try:
                # Parse original file
                parser = YMLParser()
                elements = parser.parse_yml(yml_file)
                
                # Calculate new positions
                new_positions = position_calculator_func(elements)
                
                # Determine output path
                if output_dir:
                    output_path = Path(output_dir) / Path(yml_file).name
                else:
                    output_path = yml_file
                
                # Generate new YML
                self.generate_yml(elements, new_positions, str(output_path), yml_file)
                
                # Validate
                is_valid, errors = self.validate_yml_output(str(output_path), elements)
                
                results[yml_file] = is_valid
                
                if not is_valid:
                    print(f"Validation errors for {yml_file}:")
                    for error in errors[:5]:  # Show first 5 errors
                        print(f"  - {error}")
                
            except Exception as e:
                print(f"Error processing {yml_file}: {e}")
                results[yml_file] = False
        
        return results


def generate_yml(
    elements: List[YMLElement],
    new_positions: List[Tuple[float, float, float, float]],
    output_path: str,
    original_yml_path: Optional[str] = None
) -> str:
    """
    Convenience function to generate a YML file.
    
    Args:
        elements: List of YMLElement objects with original data
        new_positions: List of new position tuples (x1, y1, x2, y2)
        output_path: Path where the new YML file should be written
        original_yml_path: Path to original YML file for format preservation
        
    Returns:
        The generated YML content as a string
    """
    generator = YMLGenerator()
    return generator.generate_yml(elements, new_positions, output_path, original_yml_path)


def validate_yml_output(
    yml_path: str,
    original_elements: List[YMLElement]
) -> Tuple[bool, List[str]]:
    """
    Convenience function to validate a generated YML file.
    
    Args:
        yml_path: Path to the YML file to validate
        original_elements: Original elements to compare against
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    generator = YMLGenerator()
    generator.original_elements = original_elements
    return generator.validate_yml_output(yml_path, original_elements)


if __name__ == "__main__":
    # Example usage and testing
    import sys
    from multi_pdf_positioning.yml_parser import YMLParser
    from multi_pdf_positioning.position_calculator import PositionCalculator
    from multi_pdf_positioning.pdf_analyzer import PDFAnalyzer
    
    print("\n=== YML Generator Demo ===")
    
    # Check if YML file provided
    if len(sys.argv) > 1:
        yml_file = sys.argv[1]
    else:
        yml_file = "coords_multi/seite1_f1.yml"
    
    try:
        # Parse original YML
        print(f"\n1. Parsing original YML: {yml_file}")
        parser = YMLParser()
        elements = parser.parse_yml(yml_file)
        print(f"   Found {len(elements)} elements")
        
        # Calculate new positions (using simple offset for demo)
        print(f"\n2. Calculating new positions (demo: +10 offset)")
        new_positions = []
        for elem in elements:
            x1, y1, x2, y2 = elem.position
            # Simple demo: shift everything right and down by 10 points
            new_pos = (x1 + 10, y1 + 10, x2 + 10, y2 + 10)
            new_positions.append(new_pos)
        
        # Generate new YML
        output_file = "multi_pdf_positioning/test_output_generated.yml"
        print(f"\n3. Generating new YML: {output_file}")
        generator = YMLGenerator()
        content = generator.generate_yml(elements, new_positions, output_file, yml_file)
        print(f"   Generated {len(content)} characters")
        
        # Validate output
        print(f"\n4. Validating generated YML")
        is_valid, errors = generator.validate_yml_output(output_file, elements)
        
        if is_valid:
            print("   [OK] Validation passed!")
        else:
            print(f"   [ERROR] Validation failed with {len(errors)} errors:")
            for error in errors[:10]:  # Show first 10 errors
                print(f"     - {error}")
        
        # Show validation report
        print(f"\n5. Validation Report")
        report = generator.get_validation_report()
        for key, value in report.items():
            if key != 'errors':
                print(f"   {key}: {value}")
        
        # Show sample of generated content
        print(f"\n6. Sample of generated content (first 500 chars):")
        print(content[:500])
        print("   ...")
        
        print(f"\n[OK] YML Generator demo complete")
        print(f"  Output file: {output_file}")
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
