"""
Position Calculator Module for Multi-PDF Positioning System

This module calculates optimal positions for text elements based on PDF design
analysis and positioning strategies. It includes collision detection and
boundary validation.
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
from multi_pdf_positioning.yml_parser import YMLElement
from multi_pdf_positioning.pdf_analyzer import PDFAnalysis, SafeZone


# Positioning rules and constraints
POSITIONING_RULES = {
    # Minimum distance from page edges (in points)
    "min_margin": 10,
    
    # Minimum spacing between text elements (in points)
    "min_spacing": 5,
    
    # Page dimensions for A4 (in points)
    "page_width": 595,
    "page_height": 842,
    
    # Importance weights for different text elements
    # Higher weight = more prominent positioning
    "importance_weights": {
        "ERSTELLT FÜR:": 0.9,
        "PHOTOVOLTAIK": 0.95,
        "ANGEBOT": 1.0,
        "kWp_anlage_anlage": 1.0,
        "kunde_vorname_und_nachname": 0.85,
        "datum": 0.7,
        "preis": 0.95,
    },
    
    # Default importance for unlisted elements
    "default_importance": 0.5,
    
    # Grid settings for fallback positioning
    "grid_columns": 3,
    "grid_rows": 3,
    "grid_padding": 20,
}


@dataclass
class CollisionInfo:
    """
    Information about a collision between two elements.
    
    Attributes:
        element1_index: Index of first element
        element2_index: Index of second element
        overlap_area: Area of overlap in square points
    """
    element1_index: int
    element2_index: int
    overlap_area: float


class PositionCalculator:
    """
    Calculator for optimal text element positions.
    
    This calculator uses PDF design analysis and positioning strategies
    to determine the best placement for text elements.
    """
    
    def __init__(self, rules: Optional[Dict] = None):
        """
        Initialize the position calculator.
        
        Args:
            rules: Custom positioning rules (uses POSITIONING_RULES if None)
        """
        self.rules = rules if rules else POSITIONING_RULES
        self.collisions: List[CollisionInfo] = []
    
    def ensure_bounds(
        self,
        position: Tuple[float, float, float, float]
    ) -> Tuple[float, float, float, float]:
        """
        Ensure a position is within PDF page bounds with margins.
        
        Args:
            position: Tuple of (x1, y1, x2, y2) coordinates
            
        Returns:
            Adjusted position tuple within bounds
        """
        x1, y1, x2, y2 = position
        
        min_margin = self.rules["min_margin"]
        page_width = self.rules["page_width"]
        page_height = self.rules["page_height"]
        
        # Calculate element dimensions
        width = x2 - x1
        height = y2 - y1
        
        # Ensure minimum bounds
        x1 = max(x1, min_margin)
        y1 = max(y1, min_margin)
        
        # Ensure maximum bounds
        x2 = min(x2, page_width - min_margin)
        y2 = min(y2, page_height - min_margin)
        
        # If element is too wide/tall, adjust
        if x2 - x1 < width:
            # Element doesn't fit, keep left edge and truncate
            x2 = x1 + min(width, page_width - 2 * min_margin)
        
        if y2 - y1 < height:
            # Element doesn't fit, keep bottom edge and truncate
            y2 = y1 + min(height, page_height - 2 * min_margin)
        
        # Final validation
        x1 = max(min_margin, min(x1, page_width - min_margin))
        y1 = max(min_margin, min(y1, page_height - min_margin))
        x2 = max(x1 + 1, min(x2, page_width - min_margin))
        y2 = max(y1 + 1, min(y2, page_height - min_margin))
        
        return (x1, y1, x2, y2)
    
    def check_collisions(
        self,
        positions: List[Tuple[float, float, float, float]]
    ) -> List[CollisionInfo]:
        """
        Check for collisions between text elements.
        
        Args:
            positions: List of position tuples (x1, y1, x2, y2)
            
        Returns:
            List of CollisionInfo objects for detected collisions
        """
        collisions = []
        min_spacing = self.rules["min_spacing"]
        
        # Check each pair of positions
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                pos1 = positions[i]
                pos2 = positions[j]
                
                # Expand rectangles by min_spacing for collision detection
                x1_a, y1_a, x2_a, y2_a = pos1
                x1_b, y1_b, x2_b, y2_b = pos2
                
                # Add spacing buffer
                x1_a -= min_spacing
                y1_a -= min_spacing
                x2_a += min_spacing
                y2_a += min_spacing
                
                # Check for overlap
                if self._rectangles_overlap(
                    (x1_a, y1_a, x2_a, y2_a),
                    (x1_b, y1_b, x2_b, y2_b)
                ):
                    # Calculate overlap area
                    overlap_area = self._calculate_overlap_area(
                        (x1_a, y1_a, x2_a, y2_a),
                        (x1_b, y1_b, x2_b, y2_b)
                    )
                    
                    collision = CollisionInfo(
                        element1_index=i,
                        element2_index=j,
                        overlap_area=overlap_area
                    )
                    collisions.append(collision)
        
        self.collisions = collisions
        return collisions
    
    def _rectangles_overlap(
        self,
        rect1: Tuple[float, float, float, float],
        rect2: Tuple[float, float, float, float]
    ) -> bool:
        """
        Check if two rectangles overlap.
        
        Args:
            rect1: First rectangle (x1, y1, x2, y2)
            rect2: Second rectangle (x1, y1, x2, y2)
            
        Returns:
            True if rectangles overlap, False otherwise
        """
        x1_a, y1_a, x2_a, y2_a = rect1
        x1_b, y1_b, x2_b, y2_b = rect2
        
        # Check if one rectangle is to the left of the other
        if x2_a <= x1_b or x2_b <= x1_a:
            return False
        
        # Check if one rectangle is above the other
        if y2_a <= y1_b or y2_b <= y1_a:
            return False
        
        return True
    
    def _calculate_overlap_area(
        self,
        rect1: Tuple[float, float, float, float],
        rect2: Tuple[float, float, float, float]
    ) -> float:
        """
        Calculate the area of overlap between two rectangles.
        
        Args:
            rect1: First rectangle (x1, y1, x2, y2)
            rect2: Second rectangle (x1, y1, x2, y2)
            
        Returns:
            Overlap area in square points
        """
        x1_a, y1_a, x2_a, y2_a = rect1
        x1_b, y1_b, x2_b, y2_b = rect2
        
        # Calculate intersection rectangle
        x1_overlap = max(x1_a, x1_b)
        y1_overlap = max(y1_a, y1_b)
        x2_overlap = min(x2_a, x2_b)
        y2_overlap = min(y2_a, y2_b)
        
        # Calculate area
        if x2_overlap > x1_overlap and y2_overlap > y1_overlap:
            width = x2_overlap - x1_overlap
            height = y2_overlap - y1_overlap
            return width * height
        
        return 0.0
    
    def calculate_positions(
        self,
        elements: List[YMLElement],
        pdf_analysis: PDFAnalysis,
        strategy: Optional[str] = None
    ) -> List[Tuple[float, float, float, float]]:
        """
        Calculate optimal positions for text elements.
        
        This is the main function that determines new positions based on
        the PDF design analysis and selected positioning strategy.
        
        Args:
            elements: List of YMLElement objects to position
            pdf_analysis: PDFAnalysis object with design information
            strategy: Positioning strategy name (uses grid if None)
            
        Returns:
            List of position tuples (x1, y1, x2, y2) for each element
        """
        if not elements:
            return []
        
        # Import positioning strategies
        try:
            from multi_pdf_positioning.positioning_strategies import apply_strategy
            
            # If strategy is specified as firma-based, use it
            if strategy and strategy.startswith("firma"):
                # Extract firma number from strategy name (e.g., "firma1")
                try:
                    firma = int(strategy.replace("firma", ""))
                    seite = pdf_analysis.seite
                    return apply_strategy(firma, seite, elements, pdf_analysis)
                except (ValueError, AttributeError):
                    pass
            
            # Auto-select strategy based on PDF analysis
            if hasattr(pdf_analysis, 'firma'):
                firma = pdf_analysis.firma
                seite = pdf_analysis.seite
                return apply_strategy(firma, seite, elements, pdf_analysis)
        
        except ImportError:
            # Strategies not available, fall back to grid
            pass
        
        # Use grid-based positioning as default/fallback
        return self._grid_based_positioning(elements, pdf_analysis)
    
    def _grid_based_positioning(
        self,
        elements: List[YMLElement],
        pdf_analysis: PDFAnalysis
    ) -> List[Tuple[float, float, float, float]]:
        """
        Position elements using a simple grid layout.
        
        This is a fallback strategy that distributes elements evenly
        across a grid on the page.
        
        Args:
            elements: List of YMLElement objects to position
            pdf_analysis: PDFAnalysis object with design information
            
        Returns:
            List of position tuples (x1, y1, x2, y2) for each element
        """
        page_width = pdf_analysis.page_size["width"]
        page_height = pdf_analysis.page_size["height"]
        
        grid_cols = self.rules["grid_columns"]
        grid_rows = self.rules["grid_rows"]
        padding = self.rules["grid_padding"]
        margin = self.rules["min_margin"]
        
        # Calculate cell dimensions
        usable_width = page_width - 2 * margin
        usable_height = page_height - 2 * margin
        
        cell_width = (usable_width - (grid_cols - 1) * padding) / grid_cols
        cell_height = (usable_height - (grid_rows - 1) * padding) / grid_rows
        
        positions = []
        
        for i, element in enumerate(elements):
            # Calculate grid position
            row = i // grid_cols
            col = i % grid_cols
            
            # If we exceed grid capacity, wrap around
            if row >= grid_rows:
                row = row % grid_rows
            
            # Calculate position
            x1 = margin + col * (cell_width + padding)
            y1 = page_height - margin - (row + 1) * (cell_height + padding)
            
            # Use original element dimensions if they fit
            orig_width = element.position[2] - element.position[0]
            orig_height = element.position[3] - element.position[1]
            
            # Limit to cell size
            width = min(orig_width, cell_width)
            height = min(orig_height, cell_height)
            
            x2 = x1 + width
            y2 = y1 + height
            
            # Ensure bounds
            position = self.ensure_bounds((x1, y1, x2, y2))
            positions.append(position)
        
        return positions
    
    def get_element_importance(self, element: YMLElement) -> float:
        """
        Get the importance weight for an element.
        
        Args:
            element: YMLElement object
            
        Returns:
            Importance weight (0.0 to 1.0)
        """
        text = element.text.strip()
        
        # Check if text matches any known important elements
        weights = self.rules["importance_weights"]
        
        if text in weights:
            return weights[text]
        
        # Check for partial matches (e.g., dynamic values)
        for key in weights:
            if key in text or text in key:
                return weights[key]
        
        return self.rules["default_importance"]
    
    def validate_positions(
        self,
        positions: List[Tuple[float, float, float, float]]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all positions meet requirements.
        
        Args:
            positions: List of position tuples to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        min_margin = self.rules["min_margin"]
        page_width = self.rules["page_width"]
        page_height = self.rules["page_height"]
        
        for i, pos in enumerate(positions):
            x1, y1, x2, y2 = pos
            
            # Check bounds
            if x1 < min_margin:
                errors.append(
                    f"Position {i}: x1 ({x1:.1f}) < min margin ({min_margin})"
                )
            if y1 < min_margin:
                errors.append(
                    f"Position {i}: y1 ({y1:.1f}) < min margin ({min_margin})"
                )
            if x2 > page_width - min_margin:
                errors.append(
                    f"Position {i}: x2 ({x2:.1f}) > max ({page_width - min_margin})"
                )
            if y2 > page_height - min_margin:
                errors.append(
                    f"Position {i}: y2 ({y2:.1f}) > max ({page_height - min_margin})"
                )
            
            # Check dimensions
            if x2 <= x1:
                errors.append(
                    f"Position {i}: Invalid width (x2 {x2:.1f} <= x1 {x1:.1f})"
                )
            if y2 <= y1:
                errors.append(
                    f"Position {i}: Invalid height (y2 {y2:.1f} <= y1 {y1:.1f})"
                )
        
        # Check for collisions
        collisions = self.check_collisions(positions)
        if collisions:
            errors.append(
                f"Found {len(collisions)} collision(s) between elements"
            )
            for collision in collisions[:5]:  # Show first 5
                errors.append(
                    f"  Collision: Element {collision.element1_index} "
                    f"and {collision.element2_index} "
                    f"(overlap: {collision.overlap_area:.1f} sq pts)"
                )
        
        return len(errors) == 0, errors


def calculate_positions(
    elements: List[YMLElement],
    pdf_analysis: PDFAnalysis,
    strategy: Optional[str] = None
) -> List[Tuple[float, float, float, float]]:
    """
    Convenience function to calculate positions.
    
    Args:
        elements: List of YMLElement objects to position
        pdf_analysis: PDFAnalysis object with design information
        strategy: Positioning strategy name (optional)
        
    Returns:
        List of position tuples (x1, y1, x2, y2) for each element
    """
    calculator = PositionCalculator()
    return calculator.calculate_positions(elements, pdf_analysis, strategy)


if __name__ == "__main__":
    # Example usage
    print("\n=== Position Calculator Demo ===")
    
    # Create calculator
    calculator = PositionCalculator()
    
    print("\nPositioning Rules:")
    for key, value in POSITIONING_RULES.items():
        if not isinstance(value, dict):
            print(f"  {key}: {value}")
    
    # Test ensure_bounds
    print("\n--- Testing ensure_bounds() ---")
    test_positions = [
        (50, 50, 200, 100),  # Valid position
        (-10, 50, 200, 100),  # x1 out of bounds
        (50, -10, 200, 100),  # y1 out of bounds
        (500, 50, 700, 100),  # x2 out of bounds
        (50, 800, 200, 900),  # y2 out of bounds
    ]
    
    for pos in test_positions:
        adjusted = calculator.ensure_bounds(pos)
        print(f"  Original: {pos}")
        print(f"  Adjusted: {adjusted}")
        print()
    
    # Test collision detection
    print("--- Testing check_collisions() ---")
    test_positions = [
        (50, 50, 150, 100),
        (100, 75, 200, 125),  # Overlaps with first
        (300, 300, 400, 400),  # No overlap
    ]
    
    collisions = calculator.check_collisions(test_positions)
    print(f"  Positions: {len(test_positions)}")
    print(f"  Collisions found: {len(collisions)}")
    for collision in collisions:
        print(f"    Elements {collision.element1_index} and "
              f"{collision.element2_index}: "
              f"{collision.overlap_area:.1f} sq pts overlap")
    
    # Test validation
    print("\n--- Testing validate_positions() ---")
    is_valid, errors = calculator.validate_positions(test_positions)
    print(f"  Valid: {is_valid}")
    if errors:
        print("  Errors:")
        for error in errors:
            print(f"    - {error}")
    
    print("\n[OK] Position Calculator module ready")
