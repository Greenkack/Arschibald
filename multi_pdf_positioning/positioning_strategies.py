"""
Positioning Strategies Module for Multi-PDF Positioning System

This module implements different positioning strategies for text elements
based on firma-specific design patterns. Each strategy creates a unique
layout optimized for the respective firma's PDF template design.
"""

from typing import List, Tuple, Dict, Optional
from multi_pdf_positioning.yml_parser import YMLElement
from multi_pdf_positioning.pdf_analyzer import PDFAnalysis


class PositioningStrategy:
    """
    Base class for positioning strategies.
    
    Each strategy implements a unique layout pattern for positioning
    text elements based on design characteristics.
    """
    
    def __init__(self, pdf_analysis: PDFAnalysis):
        """
        Initialize the strategy with PDF analysis data.
        
        Args:
            pdf_analysis: PDFAnalysis object with design information
        """
        self.pdf_analysis = pdf_analysis
        self.page_width = pdf_analysis.page_size["width"]
        self.page_height = pdf_analysis.page_size["height"]
        self.margin = 50  # Standard margin
        self.spacing = 15  # Spacing between elements
    
    def apply(
        self,
        elements: List[YMLElement]
    ) -> List[Tuple[float, float, float, float]]:
        """
        Apply the positioning strategy to elements.
        
        Args:
            elements: List of YMLElement objects to position
            
        Returns:
            List of position tuples (x1, y1, x2, y2) for each element
        """
        raise NotImplementedError("Subclasses must implement apply()")
    
    def _get_element_dimensions(
        self,
        element: YMLElement
    ) -> Tuple[float, float]:
        """
        Get the width and height of an element.
        
        Args:
            element: YMLElement object
            
        Returns:
            Tuple of (width, height)
        """
        x1, y1, x2, y2 = element.position
        return (x2 - x1, y2 - y1)
    
    def _categorize_elements(
        self,
        elements: List[YMLElement]
    ) -> Dict[str, List[YMLElement]]:
        """
        Categorize elements by importance/type.
        
        Args:
            elements: List of YMLElement objects
            
        Returns:
            Dictionary with categorized elements
        """
        categories = {
            "headers": [],
            "important_values": [],
            "customer_info": [],
            "other": []
        }
        
        for elem in elements:
            text = elem.text.strip().upper()
            
            # Headers (static labels)
            if any(keyword in text for keyword in [
                "PHOTOVOLTAIK", "ANGEBOT", "ERSTELLT FÜR",
                "ÜBERSICHT", "ZUSAMMENFASSUNG"
            ]):
                categories["headers"].append(elem)
            
            # Important values (dynamic data)
            elif any(keyword in text.lower() for keyword in [
                "kwp", "preis", "ertrag", "amortisation",
                "leistung", "kosten"
            ]):
                categories["important_values"].append(elem)
            
            # Customer info
            elif any(keyword in text.lower() for keyword in [
                "kunde", "name", "adresse", "datum", "ansprechpartner"
            ]):
                categories["customer_info"].append(elem)
            
            # Everything else
            else:
                categories["other"].append(elem)
        
        return categories


class HeaderFocusedStrategy(PositioningStrategy):
    """
    Strategy 1: Header-Focused Layout (Firma 1)
    
    - Hauptüberschrift oben links
    - Wichtige Werte (kWp) rechts unten
    - Kundeninfo zentriert unter Überschrift
    """
    
    def apply(
        self,
        elements: List[YMLElement]
    ) -> List[Tuple[float, float, float, float]]:
        """
        Apply header-focused positioning strategy.
        
        Args:
            elements: List of YMLElement objects to position
            
        Returns:
            List of position tuples (x1, y1, x2, y2) for each element
        """
        if not elements:
            return []
        
        # Categorize elements
        categories = self._categorize_elements(elements)
        
        # Create position mapping
        positions = [None] * len(elements)
        
        # Position headers (top left)
        y_offset = self.page_height - self.margin
        for elem in categories["headers"]:
            width, height = self._get_element_dimensions(elem)
            x1 = self.margin
            y1 = y_offset - height
            x2 = x1 + width
            y2 = y_offset
            
            positions[elem.index] = (x1, y1, x2, y2)
            y_offset -= (height + self.spacing)
        
        # Position customer info (centered, below headers)
        center_x = self.page_width / 2
        for elem in categories["customer_info"]:
            width, height = self._get_element_dimensions(elem)
            x1 = center_x - width / 2
            y1 = y_offset - height
            x2 = x1 + width
            y2 = y_offset
            
            positions[elem.index] = (x1, y1, x2, y2)
            y_offset -= (height + self.spacing)
        
        # Position important values (bottom right)
        y_offset = self.margin + 100  # Start from bottom
        for elem in categories["important_values"]:
            width, height = self._get_element_dimensions(elem)
            x1 = self.page_width - self.margin - width
            y1 = y_offset
            x2 = x1 + width
            y2 = y1 + height
            
            positions[elem.index] = (x1, y1, x2, y2)
            y_offset += (height + self.spacing)
        
        # Position other elements (left side, middle)
        y_offset = self.page_height / 2
        for elem in categories["other"]:
            width, height = self._get_element_dimensions(elem)
            x1 = self.margin
            y1 = y_offset - height
            x2 = x1 + width
            y2 = y_offset
            
            # Ensure we don't go below margin
            if y1 < self.margin:
                # Switch to right column if we run out of space
                x1 = self.page_width / 2
                x2 = x1 + width
                y1 = self.page_height / 2 - height
                y2 = self.page_height / 2
            
            positions[elem.index] = (x1, y1, x2, y2)
            y_offset -= (height + self.spacing)
        
        # Fill any None positions with fallback
        for i, pos in enumerate(positions):
            if pos is None:
                width, height = self._get_element_dimensions(elements[i])
                positions[i] = (
                    self.margin,
                    self.margin,
                    self.margin + width,
                    self.margin + height
                )
        
        return positions


class CenterProminentStrategy(PositioningStrategy):
    """
    Strategy 2: Center-Prominent Layout (Firma 2)
    
    - Hauptüberschrift zentriert
    - Wichtige Werte rechts oben
    - Kundeninfo links oben
    """
    
    def apply(
        self,
        elements: List[YMLElement]
    ) -> List[Tuple[float, float, float, float]]:
        """
        Apply center-prominent positioning strategy.
        
        Args:
            elements: List of YMLElement objects to position
            
        Returns:
            List of position tuples (x1, y1, x2, y2) for each element
        """
        if not elements:
            return []
        
        categories = self._categorize_elements(elements)
        positions = [None] * len(elements)
        
        # Position headers (centered at top)
        y_offset = self.page_height - self.margin
        center_x = self.page_width / 2
        for elem in categories["headers"]:
            width, height = self._get_element_dimensions(elem)
            x1 = center_x - width / 2
            y1 = y_offset - height
            x2 = x1 + width
            y2 = y_offset
            
            positions[elem.index] = (x1, y1, x2, y2)
            y_offset -= (height + self.spacing * 2)  # Extra spacing for prominence
        
        # Position customer info (left top)
        y_offset = self.page_height - self.margin - 100
        for elem in categories["customer_info"]:
            width, height = self._get_element_dimensions(elem)
            x1 = self.margin
            y1 = y_offset - height
            x2 = x1 + width
            y2 = y_offset
            
            positions[elem.index] = (x1, y1, x2, y2)
            y_offset -= (height + self.spacing)
        
        # Position important values (right top)
        y_offset = self.page_height - self.margin - 100
        for elem in categories["important_values"]:
            width, height = self._get_element_dimensions(elem)
            x1 = self.page_width - self.margin - width
            y1 = y_offset - height
            x2 = x1 + width
            y2 = y_offset
            
            positions[elem.index] = (x1, y1, x2, y2)
            y_offset -= (height + self.spacing)
        
        # Position other elements (centered, middle)
        y_offset = self.page_height / 2
        for elem in categories["other"]:
            width, height = self._get_element_dimensions(elem)
            x1 = center_x - width / 2
            y1 = y_offset - height
            x2 = x1 + width
            y2 = y_offset
            
            # Ensure we don't go below margin
            if y1 < self.margin:
                y1 = self.margin
                y2 = y1 + height
            
            positions[elem.index] = (x1, y1, x2, y2)
            y_offset -= (height + self.spacing)
        
        # Fill any None positions
        for i, pos in enumerate(positions):
            if pos is None:
                width, height = self._get_element_dimensions(elements[i])
                positions[i] = (
                    center_x - width / 2,
                    self.margin,
                    center_x + width / 2,
                    self.margin + height
                )
        
        return positions


class AsymmetricModernStrategy(PositioningStrategy):
    """
    Strategy 3: Asymmetric-Modern Layout (Firma 3)
    
    - Hauptüberschrift rechts oben
    - Wichtige Werte links unten
    - Kundeninfo rechts Mitte
    """
    
    def apply(
        self,
        elements: List[YMLElement]
    ) -> List[Tuple[float, float, float, float]]:
        """
        Apply asymmetric-modern positioning strategy.
        
        Args:
            elements: List of YMLElement objects to position
            
        Returns:
            List of position tuples (x1, y1, x2, y2) for each element
        """
        if not elements:
            return []
        
        categories = self._categorize_elements(elements)
        positions = [None] * len(elements)
        
        # Position headers (right top)
        y_offset = self.page_height - self.margin
        for elem in categories["headers"]:
            width, height = self._get_element_dimensions(elem)
            x1 = self.page_width - self.margin - width
            y1 = y_offset - height
            x2 = x1 + width
            y2 = y_offset
            
            positions[elem.index] = (x1, y1, x2, y2)
            y_offset -= (height + self.spacing)
        
        # Position customer info (right middle)
        y_offset = self.page_height / 2 + 100
        for elem in categories["customer_info"]:
            width, height = self._get_element_dimensions(elem)
            x1 = self.page_width - self.margin - width
            y1 = y_offset - height
            x2 = x1 + width
            y2 = y_offset
            
            positions[elem.index] = (x1, y1, x2, y2)
            y_offset -= (height + self.spacing)
        
        # Position important values (left bottom)
        y_offset = self.margin + 150
        for elem in categories["important_values"]:
            width, height = self._get_element_dimensions(elem)
            x1 = self.margin
            y1 = y_offset
            x2 = x1 + width
            y2 = y1 + height
            
            positions[elem.index] = (x1, y1, x2, y2)
            y_offset += (height + self.spacing)
        
        # Position other elements (left middle)
        y_offset = self.page_height / 2
        for elem in categories["other"]:
            width, height = self._get_element_dimensions(elem)
            x1 = self.margin
            y1 = y_offset - height
            x2 = x1 + width
            y2 = y_offset
            
            # Ensure we don't go below margin
            if y1 < self.margin:
                y1 = self.margin
                y2 = y1 + height
            
            positions[elem.index] = (x1, y1, x2, y2)
            y_offset -= (height + self.spacing)
        
        # Fill any None positions
        for i, pos in enumerate(positions):
            if pos is None:
                width, height = self._get_element_dimensions(elements[i])
                positions[i] = (
                    self.margin,
                    self.page_height / 2,
                    self.margin + width,
                    self.page_height / 2 + height
                )
        
        return positions


class GridBasedStrategy(PositioningStrategy):
    """
    Strategy 4: Grid-Based Layout (Firma 4)
    
    - Verteile Elemente in 3x3 Grid
    - Positioniere wichtige Werte im Zentrum
    - Symmetrische Anordnung
    """
    
    def apply(
        self,
        elements: List[YMLElement]
    ) -> List[Tuple[float, float, float, float]]:
        """
        Apply grid-based positioning strategy.
        
        Args:
            elements: List of YMLElement objects to position
            
        Returns:
            List of position tuples (x1, y1, x2, y2) for each element
        """
        if not elements:
            return []
        
        categories = self._categorize_elements(elements)
        positions = [None] * len(elements)
        
        # Define 3x3 grid
        grid_cols = 3
        grid_rows = 3
        
        usable_width = self.page_width - 2 * self.margin
        usable_height = self.page_height - 2 * self.margin
        
        if grid_cols != 0:
            cell_width = usable_width / grid_cols
        else:
            cell_width = 0.0
        if grid_rows != 0:
            cell_height = usable_height / grid_rows
        else:
            cell_height = 0.0
        
        # Position important values in center (row 1, col 1)
        center_row = 1
        center_col = 1
        for i, elem in enumerate(categories["important_values"]):
            width, height = self._get_element_dimensions(elem)
            
            # Center in middle cell
            cell_center_x = self.margin + center_col * cell_width + cell_width / 2
            cell_center_y = self.page_height - self.margin - center_row * cell_height - cell_height / 2
            
            x1 = cell_center_x - width / 2
            y1 = cell_center_y - height / 2
            x2 = x1 + width
            y2 = y1 + height
            
            positions[elem.index] = (x1, y1, x2, y2)
        
        # Position headers in top row
        top_row = 0
        for i, elem in enumerate(categories["headers"]):
            width, height = self._get_element_dimensions(elem)
            col = i % grid_cols
            
            cell_center_x = self.margin + col * cell_width + cell_width / 2
            cell_center_y = self.page_height - self.margin - top_row * cell_height - cell_height / 2
            
            x1 = cell_center_x - width / 2
            y1 = cell_center_y - height / 2
            x2 = x1 + width
            y2 = y1 + height
            
            positions[elem.index] = (x1, y1, x2, y2)
        
        # Position customer info in left column
        left_col = 0
        for i, elem in enumerate(categories["customer_info"]):
            width, height = self._get_element_dimensions(elem)
            row = 1 + i  # Start from row 1
            
            if row >= grid_rows:
                row = grid_rows - 1
            
            cell_center_x = self.margin + left_col * cell_width + cell_width / 2
            cell_center_y = self.page_height - self.margin - row * cell_height - cell_height / 2
            
            x1 = cell_center_x - width / 2
            y1 = cell_center_y - height / 2
            x2 = x1 + width
            y2 = y1 + height
            
            positions[elem.index] = (x1, y1, x2, y2)
        
        # Position other elements in remaining cells
        available_cells = [
            (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)
        ]
        
        for i, elem in enumerate(categories["other"]):
            if i >= len(available_cells):
                break
            
            row, col = available_cells[i]
            width, height = self._get_element_dimensions(elem)
            
            cell_center_x = self.margin + col * cell_width + cell_width / 2
            cell_center_y = self.page_height - self.margin - row * cell_height - cell_height / 2
            
            x1 = cell_center_x - width / 2
            y1 = cell_center_y - height / 2
            x2 = x1 + width
            y2 = y1 + height
            
            positions[elem.index] = (x1, y1, x2, y2)
        
        # Fill any None positions
        for i, pos in enumerate(positions):
            if pos is None:
                width, height = self._get_element_dimensions(elements[i])
                # Place in bottom right cell
                x1 = self.page_width - self.margin - width
                y1 = self.margin
                x2 = x1 + width
                y2 = y1 + height
                positions[i] = (x1, y1, x2, y2)
        
        return positions


class DiagonalFlowStrategy(PositioningStrategy):
    """
    Strategy 5: Diagonal-Flow Layout (Firma 5)
    
    - Positioniere Elemente diagonal von links oben nach rechts unten
    - Wichtige Werte folgen diagonaler Linie
    """
    
    def apply(
        self,
        elements: List[YMLElement]
    ) -> List[Tuple[float, float, float, float]]:
        """
        Apply diagonal-flow positioning strategy.
        
        Args:
            elements: List of YMLElement objects to position
            
        Returns:
            List of position tuples (x1, y1, x2, y2) for each element
        """
        if not elements:
            return []
        
        categories = self._categorize_elements(elements)
        positions = [None] * len(elements)
        
        # Create diagonal flow from top-left to bottom-right
        usable_width = self.page_width - 2 * self.margin
        usable_height = self.page_height - 2 * self.margin
        
        # Combine all elements in priority order
        ordered_elements = (
            categories["headers"] +
            categories["important_values"] +
            categories["customer_info"] +
            categories["other"]
        )
        
        # Calculate diagonal positions
        num_elements = len(ordered_elements)
        if num_elements > 0:
            if max != 0:
                x_step = usable_width / max(num_elements - 1, 1)
            else:
                x_step = 0.0
            if max != 0:
                y_step = usable_height / max(num_elements - 1, 1)
            else:
                y_step = 0.0
            
            for i, elem in enumerate(ordered_elements):
                width, height = self._get_element_dimensions(elem)
                
                # Calculate position along diagonal
                x1 = self.margin + i * x_step
                y1 = self.page_height - self.margin - i * y_step - height
                x2 = x1 + width
                y2 = y1 + height
                
                # Ensure within bounds
                if x2 > self.page_width - self.margin:
                    x2 = self.page_width - self.margin
                    x1 = x2 - width
                
                if y1 < self.margin:
                    y1 = self.margin
                    y2 = y1 + height
                
                positions[elem.index] = (x1, y1, x2, y2)
        
        # Fill any None positions
        for i, pos in enumerate(positions):
            if pos is None:
                width, height = self._get_element_dimensions(elements[i])
                positions[i] = (
                    self.margin,
                    self.margin,
                    self.margin + width,
                    self.margin + height
                )
        
        return positions


class SidebarLayoutStrategy(PositioningStrategy):
    """
    Strategy 6: Sidebar-Layout (Firma 6)
    
    - Positioniere Hauptinfo in linker Spalte
    - Positioniere wichtige Werte in rechter Spalte
    - Klare vertikale Trennung
    """
    
    def apply(
        self,
        elements: List[YMLElement]
    ) -> List[Tuple[float, float, float, float]]:
        """
        Apply sidebar-layout positioning strategy.
        
        Args:
            elements: List of YMLElement objects to position
            
        Returns:
            List of position tuples (x1, y1, x2, y2) for each element
        """
        if not elements:
            return []
        
        categories = self._categorize_elements(elements)
        positions = [None] * len(elements)
        
        # Define sidebar widths
        sidebar_width = (self.page_width - 3 * self.margin) / 2
        left_x = self.margin
        right_x = self.margin * 2 + sidebar_width
        
        # Position headers and customer info in left sidebar
        y_offset = self.page_height - self.margin
        
        for elem in categories["headers"]:
            width, height = self._get_element_dimensions(elem)
            width = min(width, sidebar_width)  # Limit to sidebar width
            
            x1 = left_x
            y1 = y_offset - height
            x2 = x1 + width
            y2 = y_offset
            
            positions[elem.index] = (x1, y1, x2, y2)
            y_offset -= (height + self.spacing)
        
        # Add spacing between headers and customer info
        y_offset -= self.spacing
        
        for elem in categories["customer_info"]:
            width, height = self._get_element_dimensions(elem)
            width = min(width, sidebar_width)
            
            x1 = left_x
            y1 = y_offset - height
            x2 = x1 + width
            y2 = y_offset
            
            positions[elem.index] = (x1, y1, x2, y2)
            y_offset -= (height + self.spacing)
        
        # Position other elements in left sidebar
        for elem in categories["other"]:
            width, height = self._get_element_dimensions(elem)
            width = min(width, sidebar_width)
            
            x1 = left_x
            y1 = y_offset - height
            x2 = x1 + width
            y2 = y_offset
            
            # Ensure we don't go below margin
            if y1 < self.margin:
                y1 = self.margin
                y2 = y1 + height
            
            positions[elem.index] = (x1, y1, x2, y2)
            y_offset -= (height + self.spacing)
        
        # Position important values in right sidebar
        y_offset = self.page_height - self.margin
        
        for elem in categories["important_values"]:
            width, height = self._get_element_dimensions(elem)
            width = min(width, sidebar_width)
            
            x1 = right_x
            y1 = y_offset - height
            x2 = x1 + width
            y2 = y_offset
            
            positions[elem.index] = (x1, y1, x2, y2)
            y_offset -= (height + self.spacing)
        
        # Fill any None positions
        for i, pos in enumerate(positions):
            if pos is None:
                width, height = self._get_element_dimensions(elements[i])
                width = min(width, sidebar_width)
                positions[i] = (
                    left_x,
                    self.margin,
                    left_x + width,
                    self.margin + height
                )
        
        return positions


def select_strategy(
    firma: int,
    seite: int,
    pdf_analysis: PDFAnalysis
) -> PositioningStrategy:
    """
    Select the appropriate positioning strategy based on firma and seite.
    
    Args:
        firma: Firma number (1-6)
        seite: Seite number (1-8)
        pdf_analysis: PDFAnalysis object with design information
        
    Returns:
        PositioningStrategy instance for the firma
        
    Raises:
        ValueError: If firma number is invalid
    """
    # Map firma numbers to strategies
    strategy_map = {
        1: HeaderFocusedStrategy,
        2: CenterProminentStrategy,
        3: AsymmetricModernStrategy,
        4: GridBasedStrategy,
        5: DiagonalFlowStrategy,
        6: SidebarLayoutStrategy
    }
    
    if firma not in strategy_map:
        raise ValueError(
            f"Invalid firma number: {firma}. Must be between 1 and 6."
        )
    
    # Get strategy class
    strategy_class = strategy_map[firma]
    
    # Create and return strategy instance
    return strategy_class(pdf_analysis)


def apply_strategy(
    firma: int,
    seite: int,
    elements: List[YMLElement],
    pdf_analysis: PDFAnalysis
) -> List[Tuple[float, float, float, float]]:
    """
    Convenience function to select and apply a positioning strategy.
    
    Args:
        firma: Firma number (1-6)
        seite: Seite number (1-8)
        elements: List of YMLElement objects to position
        pdf_analysis: PDFAnalysis object with design information
        
    Returns:
        List of position tuples (x1, y1, x2, y2) for each element
    """
    strategy = select_strategy(firma, seite, pdf_analysis)
    return strategy.apply(elements)


if __name__ == "__main__":
    # Example usage
    print("\n=== Positioning Strategies Demo ===")
    
    print("\nAvailable Strategies:")
    strategies = {
        1: "Header-Focused (Firma 1)",
        2: "Center-Prominent (Firma 2)",
        3: "Asymmetric-Modern (Firma 3)",
        4: "Grid-Based (Firma 4)",
        5: "Diagonal-Flow (Firma 5)",
        6: "Sidebar-Layout (Firma 6)"
    }
    
    for firma, name in strategies.items():
        print(f"  Firma {firma}: {name}")
    
    print("\nPositioning Strategies module ready")
