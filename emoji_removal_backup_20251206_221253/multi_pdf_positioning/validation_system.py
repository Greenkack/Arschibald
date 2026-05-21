"""
Validation System Module for Multi-PDF Positioning System

This module provides comprehensive validation for text element positions,
including boundary checks, collision detection, and validation reporting.

Requirements covered:
- 6.1: Position validation within PDF bounds
- 6.2: Collision detection and spacing validation
- 6.3: Margin validation
- 6.4: Validation reporting
- 6.5: Warning and error documentation
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
from enum import Enum
from datetime import datetime
from multi_pdf_positioning.yml_parser import YMLElement


class ValidationLevel(Enum):
    """Validation message severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class ValidationMessage:
    """
    Represents a validation message.
    
    Attributes:
        level: Severity level (INFO, WARNING, ERROR)
        message: Description of the validation issue
        element_index: Index of the element (if applicable)
        position: Position coordinates (if applicable)
        details: Additional details about the issue
    """
    level: ValidationLevel
    message: str
    element_index: Optional[int] = None
    position: Optional[Tuple[float, float, float, float]] = None
    details: Optional[str] = None


@dataclass
class CollisionInfo:
    """
    Information about a collision between two elements.
    
    Attributes:
        element1_index: Index of first element
        element2_index: Index of second element
        element1_position: Position of first element
        element2_position: Position of second element
        overlap_area: Area of overlap in square points
        overlap_rect: Rectangle of overlap (x1, y1, x2, y2)
    """
    element1_index: int
    element2_index: int
    element1_position: Tuple[float, float, float, float]
    element2_position: Tuple[float, float, float, float]
    overlap_area: float
    overlap_rect: Tuple[float, float, float, float]


@dataclass
class ValidationReport:
    """
    Comprehensive validation report.
    
    Attributes:
        firma: Firma number
        seite: Seite number
        timestamp: When validation was performed
        total_elements: Total number of elements validated
        messages: List of validation messages
        collisions: List of detected collisions
        is_valid: Overall validation status
        summary: Summary statistics
    """
    firma: Optional[int] = None
    seite: Optional[int] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    total_elements: int = 0
    messages: List[ValidationMessage] = field(default_factory=list)
    collisions: List[CollisionInfo] = field(default_factory=list)
    is_valid: bool = True
    summary: Dict[str, int] = field(default_factory=dict)
    
    def add_message(self, level: ValidationLevel, message: str, 
                   element_index: Optional[int] = None,
                   position: Optional[Tuple[float, float, float, float]] = None,
                   details: Optional[str] = None):
        """Add a validation message to the report."""
        msg = ValidationMessage(
            level=level,
            message=message,
            element_index=element_index,
            position=position,
            details=details
        )
        self.messages.append(msg)
        
        # Update validity status
        if level == ValidationLevel.ERROR:
            self.is_valid = False
    
    def get_errors(self) -> List[ValidationMessage]:
        """Get all error messages."""
        return [m for m in self.messages if m.level == ValidationLevel.ERROR]
    
    def get_warnings(self) -> List[ValidationMessage]:
        """Get all warning messages."""
        return [m for m in self.messages if m.level == ValidationLevel.WARNING]
    
    def get_info(self) -> List[ValidationMessage]:
        """Get all info messages."""
        return [m for m in self.messages if m.level == ValidationLevel.INFO]
    
    def calculate_summary(self):
        """Calculate summary statistics."""
        self.summary = {
            "total_messages": len(self.messages),
            "errors": len(self.get_errors()),
            "warnings": len(self.get_warnings()),
            "info": len(self.get_info()),
            "collisions": len(self.collisions),
            "elements_validated": self.total_elements
        }


class ValidationSystem:
    """
    Comprehensive validation system for text element positions.
    
    This system validates positions against PDF bounds, checks for collisions,
    and generates detailed validation reports.
    """
    
    def __init__(self, 
                 page_width: float = 595,
                 page_height: float = 842,
                 min_margin: float = 10,
                 min_spacing: float = 5):
        """
        Initialize the validation system.
        
        Args:
            page_width: PDF page width in points (default: 595 for A4)
            page_height: PDF page height in points (default: 842 for A4)
            min_margin: Minimum distance from page edges in points
            min_spacing: Minimum spacing between elements in points
        """
        self.page_width = page_width
        self.page_height = page_height
        self.min_margin = min_margin
        self.min_spacing = min_spacing
    
    def validate_positions(
        self,
        positions: List[Tuple[float, float, float, float]],
        elements: Optional[List[YMLElement]] = None
    ) -> ValidationReport:
        """
        Validate a list of positions comprehensively.
        
        This function performs all validation checks:
        - Boundary validation (within PDF bounds)
        - Margin validation (minimum distance from edges)
        - Dimension validation (valid width and height)
        - Collision detection (overlapping elements)
        
        Args:
            positions: List of position tuples (x1, y1, x2, y2)
            elements: Optional list of YMLElement objects for context
            
        Returns:
            ValidationReport with all validation results
            
        Requirements: 6.1, 6.2, 6.3
        """
        report = ValidationReport(total_elements=len(positions))
        
        if not positions:
            report.add_message(
                ValidationLevel.WARNING,
                "No positions to validate"
            )
            report.calculate_summary()
            return report
        
        # Validate each position
        for i, pos in enumerate(positions):
            self._validate_single_position(pos, i, report, elements)
        
        # Detect collisions
        collisions = self.detect_collisions(positions)
        report.collisions = collisions
        
        if collisions:
            report.add_message(
                ValidationLevel.ERROR,
                f"Found {len(collisions)} collision(s) between elements"
            )
            
            # Add details for each collision
            for collision in collisions:
                report.add_message(
                    ValidationLevel.ERROR,
                    f"Collision between elements {collision.element1_index} "
                    f"and {collision.element2_index}",
                    details=f"Overlap area: {collision.overlap_area:.2f} sq pts, "
                           f"Overlap rect: {collision.overlap_rect}"
                )
        
        # Calculate summary
        report.calculate_summary()
        
        return report
    
    def _validate_single_position(
        self,
        position: Tuple[float, float, float, float],
        index: int,
        report: ValidationReport,
        elements: Optional[List[YMLElement]] = None
    ):
        """
        Validate a single position.
        
        Args:
            position: Position tuple (x1, y1, x2, y2)
            index: Element index
            report: ValidationReport to add messages to
            elements: Optional list of YMLElement objects
        """
        x1, y1, x2, y2 = position
        
        # Get element text for better error messages
        element_text = ""
        if elements and index < len(elements):
            element_text = f" ('{elements[index].text[:30]}')"
        
        # Check if position is within page bounds (0-595, 0-842)
        if x1 < 0:
            report.add_message(
                ValidationLevel.ERROR,
                f"Element {index}{element_text}: x1 ({x1:.2f}) is negative",
                element_index=index,
                position=position
            )
        
        if y1 < 0:
            report.add_message(
                ValidationLevel.ERROR,
                f"Element {index}{element_text}: y1 ({y1:.2f}) is negative",
                element_index=index,
                position=position
            )
        
        if x2 > self.page_width:
            report.add_message(
                ValidationLevel.ERROR,
                f"Element {index}{element_text}: x2 ({x2:.2f}) exceeds page width ({self.page_width})",
                element_index=index,
                position=position
            )
        
        if y2 > self.page_height:
            report.add_message(
                ValidationLevel.ERROR,
                f"Element {index}{element_text}: y2 ({y2:.2f}) exceeds page height ({self.page_height})",
                element_index=index,
                position=position
            )
        
        # Check minimum margin from edges (10 points)
        if x1 < self.min_margin:
            report.add_message(
                ValidationLevel.WARNING,
                f"Element {index}{element_text}: x1 ({x1:.2f}) is too close to left edge "
                f"(min margin: {self.min_margin})",
                element_index=index,
                position=position
            )
        
        if y1 < self.min_margin:
            report.add_message(
                ValidationLevel.WARNING,
                f"Element {index}{element_text}: y1 ({y1:.2f}) is too close to bottom edge "
                f"(min margin: {self.min_margin})",
                element_index=index,
                position=position
            )
        
        if x2 > self.page_width - self.min_margin:
            report.add_message(
                ValidationLevel.WARNING,
                f"Element {index}{element_text}: x2 ({x2:.2f}) is too close to right edge "
                f"(min margin: {self.min_margin})",
                element_index=index,
                position=position
            )
        
        if y2 > self.page_height - self.min_margin:
            report.add_message(
                ValidationLevel.WARNING,
                f"Element {index}{element_text}: y2 ({y2:.2f}) is too close to top edge "
                f"(min margin: {self.min_margin})",
                element_index=index,
                position=position
            )
        
        # Check valid dimensions
        if x2 <= x1:
            report.add_message(
                ValidationLevel.ERROR,
                f"Element {index}{element_text}: Invalid width (x2 {x2:.2f} <= x1 {x1:.2f})",
                element_index=index,
                position=position
            )
        
        if y2 <= y1:
            report.add_message(
                ValidationLevel.ERROR,
                f"Element {index}{element_text}: Invalid height (y2 {y2:.2f} <= y1 {y1:.2f})",
                element_index=index,
                position=position
            )
        
        # Check for very small elements (might be unintentional)
        width = x2 - x1
        height = y2 - y1
        
        if width < 5:
            report.add_message(
                ValidationLevel.WARNING,
                f"Element {index}{element_text}: Very small width ({width:.2f} pts)",
                element_index=index,
                position=position
            )
        
        if height < 5:
            report.add_message(
                ValidationLevel.WARNING,
                f"Element {index}{element_text}: Very small height ({height:.2f} pts)",
                element_index=index,
                position=position
            )
    
    def detect_collisions(
        self,
        positions: List[Tuple[float, float, float, float]]
    ) -> List[CollisionInfo]:
        """
        Detect collisions between text elements.
        
        Two elements collide if they overlap or are closer than min_spacing.
        
        Args:
            positions: List of position tuples (x1, y1, x2, y2)
            
        Returns:
            List of CollisionInfo objects for detected collisions
            
        Requirements: 6.2, 3.4
        """
        collisions = []
        
        # Check each pair of positions
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                pos1 = positions[i]
                pos2 = positions[j]
                
                # Expand rectangles by min_spacing for collision detection
                expanded_pos1 = self._expand_rect(pos1, self.min_spacing)
                expanded_pos2 = self._expand_rect(pos2, self.min_spacing)
                
                # Check for overlap
                if self._rectangles_overlap(expanded_pos1, expanded_pos2):
                    # Calculate overlap details
                    overlap_rect = self._calculate_overlap_rect(
                        expanded_pos1, expanded_pos2
                    )
                    overlap_area = self._calculate_rect_area(overlap_rect)
                    
                    collision = CollisionInfo(
                        element1_index=i,
                        element2_index=j,
                        element1_position=pos1,
                        element2_position=pos2,
                        overlap_area=overlap_area,
                        overlap_rect=overlap_rect
                    )
                    collisions.append(collision)
        
        return collisions
    
    def resolve_collisions(
        self,
        positions: List[Tuple[float, float, float, float]],
        collisions: List[CollisionInfo],
        max_iterations: int = 10
    ) -> List[Tuple[float, float, float, float]]:
        """
        Automatically resolve collisions by adjusting positions.
        
        This function attempts to resolve collisions by moving elements
        away from each other while maintaining page bounds.
        
        Args:
            positions: List of position tuples (x1, y1, x2, y2)
            collisions: List of detected collisions
            max_iterations: Maximum number of adjustment iterations
            
        Returns:
            List of adjusted positions with reduced/eliminated collisions
            
        Requirements: 6.2
        """
        if not collisions:
            return positions
        
        adjusted_positions = [pos for pos in positions]
        
        for iteration in range(max_iterations):
            # Re-detect collisions with current positions
            current_collisions = self.detect_collisions(adjusted_positions)
            
            if not current_collisions:
                # All collisions resolved
                break
            
            # Adjust positions for each collision
            for collision in current_collisions:
                idx1 = collision.element1_index
                idx2 = collision.element2_index
                
                pos1 = adjusted_positions[idx1]
                pos2 = adjusted_positions[idx2]
                
                # Calculate centers
                center1_x = (pos1[0] + pos1[2]) / 2
                center1_y = (pos1[1] + pos1[3]) / 2
                center2_x = (pos2[0] + pos2[2]) / 2
                center2_y = (pos2[1] + pos2[3]) / 2
                
                # Calculate direction to move elements apart
                dx = center2_x - center1_x
                dy = center2_y - center1_y
                
                # Normalize direction
                distance = (dx**2 + dy**2)**0.5
                if distance > 0:
                    dx /= distance
                    dy /= distance
                
                # Move elements apart by min_spacing
                move_distance = self.min_spacing + 2
                
                # Adjust element 1 (move away from element 2)
                new_pos1 = (
                    pos1[0] - dx * move_distance,
                    pos1[1] - dy * move_distance,
                    pos1[2] - dx * move_distance,
                    pos1[3] - dy * move_distance
                )
                
                # Adjust element 2 (move away from element 1)
                new_pos2 = (
                    pos2[0] + dx * move_distance,
                    pos2[1] + dy * move_distance,
                    pos2[2] + dx * move_distance,
                    pos2[3] + dy * move_distance
                )
                
                # Ensure bounds
                new_pos1 = self._ensure_bounds(new_pos1)
                new_pos2 = self._ensure_bounds(new_pos2)
                
                adjusted_positions[idx1] = new_pos1
                adjusted_positions[idx2] = new_pos2
        
        return adjusted_positions
    
    def _expand_rect(
        self,
        rect: Tuple[float, float, float, float],
        margin: float
    ) -> Tuple[float, float, float, float]:
        """Expand a rectangle by a margin on all sides."""
        x1, y1, x2, y2 = rect
        return (x1 - margin, y1 - margin, x2 + margin, y2 + margin)
    
    def _rectangles_overlap(
        self,
        rect1: Tuple[float, float, float, float],
        rect2: Tuple[float, float, float, float]
    ) -> bool:
        """Check if two rectangles overlap."""
        x1_a, y1_a, x2_a, y2_a = rect1
        x1_b, y1_b, x2_b, y2_b = rect2
        
        # Check if one rectangle is to the left of the other
        if x2_a <= x1_b or x2_b <= x1_a:
            return False
        
        # Check if one rectangle is above the other
        if y2_a <= y1_b or y2_b <= y1_a:
            return False
        
        return True
    
    def _calculate_overlap_rect(
        self,
        rect1: Tuple[float, float, float, float],
        rect2: Tuple[float, float, float, float]
    ) -> Tuple[float, float, float, float]:
        """Calculate the rectangle of overlap between two rectangles."""
        x1_a, y1_a, x2_a, y2_a = rect1
        x1_b, y1_b, x2_b, y2_b = rect2
        
        x1_overlap = max(x1_a, x1_b)
        y1_overlap = max(y1_a, y1_b)
        x2_overlap = min(x2_a, x2_b)
        y2_overlap = min(y2_a, y2_b)
        
        return (x1_overlap, y1_overlap, x2_overlap, y2_overlap)
    
    def _calculate_rect_area(
        self,
        rect: Tuple[float, float, float, float]
    ) -> float:
        """Calculate the area of a rectangle."""
        x1, y1, x2, y2 = rect
        
        if x2 > x1 and y2 > y1:
            return (x2 - x1) * (y2 - y1)
        
        return 0.0
    
    def _ensure_bounds(
        self,
        position: Tuple[float, float, float, float]
    ) -> Tuple[float, float, float, float]:
        """Ensure a position is within PDF page bounds with margins."""
        x1, y1, x2, y2 = position
        
        # Calculate element dimensions
        width = x2 - x1
        height = y2 - y1
        
        # Ensure minimum bounds
        x1 = max(x1, self.min_margin)
        y1 = max(y1, self.min_margin)
        
        # Ensure maximum bounds
        x2 = min(x2, self.page_width - self.min_margin)
        y2 = min(y2, self.page_height - self.min_margin)
        
        # If element is too wide/tall, adjust
        if x2 - x1 < width:
            x2 = x1 + min(width, self.page_width - 2 * self.min_margin)
        
        if y2 - y1 < height:
            y2 = y1 + min(height, self.page_height - 2 * self.min_margin)
        
        # Final validation
        x1 = max(self.min_margin, min(x1, self.page_width - self.min_margin))
        y1 = max(self.min_margin, min(y1, self.page_height - self.min_margin))
        x2 = max(x1 + 1, min(x2, self.page_width - self.min_margin))
        y2 = max(y1 + 1, min(y2, self.page_height - self.min_margin))
        
        return (x1, y1, x2, y2)
    
    def generate_validation_report(
        self,
        positions: List[Tuple[float, float, float, float]],
        elements: Optional[List[YMLElement]] = None,
        firma: Optional[int] = None,
        seite: Optional[int] = None
    ) -> ValidationReport:
        """
        Generate a comprehensive validation report.
        
        This function performs all validation checks and generates a detailed
        report with errors, warnings, and summary statistics.
        
        Args:
            positions: List of position tuples (x1, y1, x2, y2)
            elements: Optional list of YMLElement objects for context
            firma: Optional firma number
            seite: Optional seite number
            
        Returns:
            ValidationReport with all validation results
            
        Requirements: 6.4, 6.5
        """
        report = self.validate_positions(positions, elements)
        report.firma = firma
        report.seite = seite
        
        # Add summary information
        if report.is_valid:
            report.add_message(
                ValidationLevel.INFO,
                f"All {len(positions)} positions are valid"
            )
        else:
            report.add_message(
                ValidationLevel.ERROR,
                f"Validation failed with {len(report.get_errors())} error(s) "
                f"and {len(report.get_warnings())} warning(s)"
            )
        
        return report
    
    def format_report(self, report: ValidationReport) -> str:
        """
        Format a validation report as a human-readable string.
        
        Args:
            report: ValidationReport to format
            
        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 70)
        lines.append("VALIDATION REPORT")
        lines.append("=" * 70)
        
        if report.firma is not None and report.seite is not None:
            lines.append(f"Firma: {report.firma}, Seite: {report.seite}")
        
        lines.append(f"Timestamp: {report.timestamp}")
        lines.append(f"Status: {'VALID' if report.is_valid else 'INVALID'}")
        lines.append("")
        
        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 70)
        for key, value in report.summary.items():
            lines.append(f"  {key}: {value}")
        lines.append("")
        
        # Errors
        errors = report.get_errors()
        if errors:
            lines.append(f"ERRORS ({len(errors)})")
            lines.append("-" * 70)
            for msg in errors:
                lines.append(f"  {msg.message}")
                if msg.details:
                    lines.append(f"    Details: {msg.details}")
            lines.append("")
        
        # Warnings
        warnings = report.get_warnings()
        if warnings:
            lines.append(f"WARNINGS ({len(warnings)})")
            lines.append("-" * 70)
            for msg in warnings:
                lines.append(f"  ⚠ {msg.message}")
                if msg.details:
                    lines.append(f"    Details: {msg.details}")
            lines.append("")
        
        # Collisions
        if report.collisions:
            lines.append(f"COLLISIONS ({len(report.collisions)})")
            lines.append("-" * 70)
            for collision in report.collisions:
                lines.append(
                    f"  Elements {collision.element1_index} and "
                    f"{collision.element2_index}"
                )
                lines.append(f"    Overlap area: {collision.overlap_area:.2f} sq pts")
                lines.append(f"    Overlap rect: {collision.overlap_rect}")
            lines.append("")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)


# Convenience functions
def validate_positions(
    positions: List[Tuple[float, float, float, float]],
    elements: Optional[List[YMLElement]] = None,
    page_width: float = 595,
    page_height: float = 842,
    min_margin: float = 10,
    min_spacing: float = 5
) -> ValidationReport:
    """
    Convenience function to validate positions.
    
    Args:
        positions: List of position tuples (x1, y1, x2, y2)
        elements: Optional list of YMLElement objects
        page_width: PDF page width in points
        page_height: PDF page height in points
        min_margin: Minimum distance from edges
        min_spacing: Minimum spacing between elements
        
    Returns:
        ValidationReport with validation results
    """
    validator = ValidationSystem(page_width, page_height, min_margin, min_spacing)
    return validator.validate_positions(positions, elements)


def detect_collisions(
    positions: List[Tuple[float, float, float, float]],
    min_spacing: float = 5
) -> List[CollisionInfo]:
    """
    Convenience function to detect collisions.
    
    Args:
        positions: List of position tuples (x1, y1, x2, y2)
        min_spacing: Minimum spacing between elements
        
    Returns:
        List of CollisionInfo objects
    """
    validator = ValidationSystem(min_spacing=min_spacing)
    return validator.detect_collisions(positions)


def generate_validation_report(
    positions: List[Tuple[float, float, float, float]],
    elements: Optional[List[YMLElement]] = None,
    firma: Optional[int] = None,
    seite: Optional[int] = None
) -> ValidationReport:
    """
    Convenience function to generate a validation report.
    
    Args:
        positions: List of position tuples (x1, y1, x2, y2)
        elements: Optional list of YMLElement objects
        firma: Optional firma number
        seite: Optional seite number
        
    Returns:
        ValidationReport with all validation results
    """
    validator = ValidationSystem()
    return validator.generate_validation_report(positions, elements, firma, seite)


if __name__ == "__main__":
    # Example usage
    print("\n=== Validation System Demo ===\n")
    
    # Create validator
    validator = ValidationSystem()
    
    print("Configuration:")
    print(f"  Page size: {validator.page_width} x {validator.page_height} pts")
    print(f"  Min margin: {validator.min_margin} pts")
    print(f"  Min spacing: {validator.min_spacing} pts")
    print()
    
    # Test positions
    test_positions = [
        (50, 50, 200, 100),      # Valid
        (5, 50, 200, 100),       # Too close to left edge (warning)
        (400, 50, 600, 100),     # Exceeds page width (error)
        (100, 75, 250, 125),     # Overlaps with first (collision)
        (300, 300, 400, 400),    # Valid, no overlap
    ]
    
    print("Test Positions:")
    for i, pos in enumerate(test_positions):
        print(f"  {i}: {pos}")
    print()
    
    # Validate positions
    print("--- Running Validation ---")
    report = validator.generate_validation_report(test_positions, firma=1, seite=1)
    
    # Print formatted report
    print(validator.format_report(report))
    
    # Test collision resolution
    if report.collisions:
        print("\n--- Testing Collision Resolution ---")
        adjusted = validator.resolve_collisions(
            test_positions,
            report.collisions,
            max_iterations=5
        )
        
        print("Adjusted Positions:")
        for i, pos in enumerate(adjusted):
            print(f"  {i}: {pos}")
        
        # Re-validate
        new_report = validator.validate_positions(adjusted)
        print(f"\nAfter adjustment:")
        print(f"  Collisions: {len(new_report.collisions)}")
        print(f"  Errors: {len(new_report.get_errors())}")
        print(f"  Warnings: {len(new_report.get_warnings())}")
    
    print("\nValidation System module ready")
