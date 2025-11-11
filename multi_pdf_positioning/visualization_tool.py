"""
Visualization Tool Module for Multi-PDF Positioning System

This module provides visualization capabilities for text element positions,
including overlay images comparing old and new positions, and comparison views.

Requirements covered:
- 7.1: Visualize positions
- 7.2: Create overlay images with old and new positions
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json
from datetime import datetime

from multi_pdf_positioning.yml_parser import YMLElement


@dataclass
class VisualizationConfig:
    """
    Configuration for visualization rendering.
    
    Attributes:
        page_width: PDF page width in points
        page_height: PDF page height in points
        scale_factor: Scale factor for image rendering (higher = larger image)
        old_position_color: Color for old positions (RGB tuple)
        new_position_color: Color for new positions (RGB tuple)
        collision_color: Color for collisions (RGB tuple)
        background_color: Background color (RGB tuple)
        line_width: Width of position rectangles
        show_labels: Whether to show element labels
        show_indices: Whether to show element indices
        font_size: Font size for labels
    """
    page_width: float = 595
    page_height: float = 842
    scale_factor: float = 2.0
    old_position_color: Tuple[int, int, int] = (255, 0, 0)  # Red
    new_position_color: Tuple[int, int, int] = (0, 255, 0)  # Green
    collision_color: Tuple[int, int, int] = (255, 165, 0)  # Orange
    background_color: Tuple[int, int, int] = (255, 255, 255)  # White
    line_width: int = 2
    show_labels: bool = True
    show_indices: bool = True
    font_size: int = 10


class VisualizationTool:
    """
    Tool for visualizing text element positions.
    
    This tool creates visual representations of positions, including:
    - Overlay images showing old and new positions
    - Comparison views side-by-side
    - Collision highlighting
    """
    
    def __init__(self, config: Optional[VisualizationConfig] = None):
        """
        Initialize the visualization tool.
        
        Args:
            config: Visualization configuration (uses default if None)
        """
        self.config = config if config else VisualizationConfig()
        
        # Try to load a font for labels
        try:
            self.font = ImageFont.truetype("arial.ttf", self.config.font_size)
        except:
            # Fall back to default font
            self.font = ImageFont.load_default()
    
    def create_overlay_image(
        self,
        old_positions: List[Tuple[float, float, float, float]],
        new_positions: List[Tuple[float, float, float, float]],
        elements: Optional[List[YMLElement]] = None,
        output_path: Optional[str] = None,
        title: Optional[str] = None
    ) -> Image.Image:
        """
        Create an overlay image showing old and new positions.
        
        Old positions are shown in red, new positions in green.
        
        Args:
            old_positions: List of old position tuples (x1, y1, x2, y2)
            new_positions: List of new position tuples (x1, y1, x2, y2)
            elements: Optional list of YMLElement objects for labels
            output_path: Optional path to save the image
            title: Optional title for the image
            
        Returns:
            PIL Image object
            
        Requirements: 7.1, 7.2
        """
        # Calculate image dimensions
        img_width = int(self.config.page_width * self.config.scale_factor)
        img_height = int(self.config.page_height * self.config.scale_factor)
        
        # Create image
        img = Image.new('RGB', (img_width, img_height), self.config.background_color)
        draw = ImageDraw.Draw(img)
        
        # Draw title if provided
        if title:
            draw.text((10, 10), title, fill=(0, 0, 0), font=self.font)
        
        # Draw old positions (red)
        for i, pos in enumerate(old_positions):
            self._draw_position(
                draw,
                pos,
                self.config.old_position_color,
                label=f"Old {i}" if self.config.show_indices else None,
                alpha=128  # Semi-transparent
            )
        
        # Draw new positions (green)
        for i, pos in enumerate(new_positions):
            label = None
            if self.config.show_indices:
                label = f"New {i}"
            elif self.config.show_labels and elements and i < len(elements):
                # Show element text as label
                text = elements[i].text[:20]
                if text:
                    label = text
            
            self._draw_position(
                draw,
                pos,
                self.config.new_position_color,
                label=label
            )
        
        # Save if output path provided
        if output_path:
            img.save(output_path)
        
        return img
    
    def create_comparison_view(
        self,
        old_positions: List[Tuple[float, float, float, float]],
        new_positions: List[Tuple[float, float, float, float]],
        elements: Optional[List[YMLElement]] = None,
        output_path: Optional[str] = None,
        firma: Optional[int] = None,
        seite: Optional[int] = None
    ) -> Image.Image:
        """
        Create a side-by-side comparison view of old and new positions.
        
        Args:
            old_positions: List of old position tuples (x1, y1, x2, y2)
            new_positions: List of new position tuples (x1, y1, x2, y2)
            elements: Optional list of YMLElement objects for labels
            output_path: Optional path to save the image
            firma: Optional firma number for title
            seite: Optional seite number for title
            
        Returns:
            PIL Image object with side-by-side comparison
            
        Requirements: 7.1, 7.2
        """
        # Calculate image dimensions
        single_width = int(self.config.page_width * self.config.scale_factor)
        single_height = int(self.config.page_height * self.config.scale_factor)
        
        # Create combined image (side by side with gap)
        gap = 20
        img_width = single_width * 2 + gap
        img_height = single_height + 60  # Extra space for titles
        
        img = Image.new('RGB', (img_width, img_height), self.config.background_color)
        draw = ImageDraw.Draw(img)
        
        # Draw main title
        title = "Position Comparison"
        if firma is not None and seite is not None:
            title += f" - Firma {firma}, Seite {seite}"
        draw.text((10, 10), title, fill=(0, 0, 0), font=self.font)
        
        # Draw "Old Positions" title
        draw.text((10, 35), "Old Positions", fill=self.config.old_position_color, font=self.font)
        
        # Draw "New Positions" title
        draw.text((single_width + gap + 10, 35), "New Positions", fill=self.config.new_position_color, font=self.font)
        
        # Offset for content area
        y_offset = 50
        
        # Draw old positions on left side
        for i, pos in enumerate(old_positions):
            label = None
            if self.config.show_labels and elements and i < len(elements):
                text = elements[i].text[:15]
                if text:
                    label = f"{i}: {text}"
            elif self.config.show_indices:
                label = str(i)
            
            self._draw_position(
                draw,
                pos,
                self.config.old_position_color,
                label=label,
                x_offset=0,
                y_offset=y_offset
            )
        
        # Draw new positions on right side
        for i, pos in enumerate(new_positions):
            label = None
            if self.config.show_labels and elements and i < len(elements):
                text = elements[i].text[:15]
                if text:
                    label = f"{i}: {text}"
            elif self.config.show_indices:
                label = str(i)
            
            self._draw_position(
                draw,
                pos,
                self.config.new_position_color,
                label=label,
                x_offset=single_width + gap,
                y_offset=y_offset
            )
        
        # Save if output path provided
        if output_path:
            img.save(output_path)
        
        return img
    
    def create_collision_visualization(
        self,
        positions: List[Tuple[float, float, float, float]],
        collisions: List[Tuple[int, int]],
        elements: Optional[List[YMLElement]] = None,
        output_path: Optional[str] = None,
        title: Optional[str] = None
    ) -> Image.Image:
        """
        Create a visualization highlighting collisions between elements.
        
        Args:
            positions: List of position tuples (x1, y1, x2, y2)
            collisions: List of collision pairs (element1_index, element2_index)
            elements: Optional list of YMLElement objects for labels
            output_path: Optional path to save the image
            title: Optional title for the image
            
        Returns:
            PIL Image object
        """
        # Calculate image dimensions
        img_width = int(self.config.page_width * self.config.scale_factor)
        img_height = int(self.config.page_height * self.config.scale_factor)
        
        # Create image
        img = Image.new('RGB', (img_width, img_height), self.config.background_color)
        draw = ImageDraw.Draw(img)
        
        # Draw title
        if title:
            draw.text((10, 10), title, fill=(0, 0, 0), font=self.font)
        else:
            draw.text((10, 10), f"Collisions: {len(collisions)}", fill=(0, 0, 0), font=self.font)
        
        # Create set of colliding element indices
        colliding_indices = set()
        for idx1, idx2 in collisions:
            colliding_indices.add(idx1)
            colliding_indices.add(idx2)
        
        # Draw all positions
        for i, pos in enumerate(positions):
            # Use collision color for colliding elements
            color = self.config.collision_color if i in colliding_indices else (200, 200, 200)
            
            label = None
            if self.config.show_labels and elements and i < len(elements):
                text = elements[i].text[:15]
                if text:
                    label = f"{i}: {text}"
            elif self.config.show_indices:
                label = str(i)
            
            self._draw_position(draw, pos, color, label=label)
        
        # Draw lines connecting colliding elements
        for idx1, idx2 in collisions:
            if idx1 < len(positions) and idx2 < len(positions):
                pos1 = positions[idx1]
                pos2 = positions[idx2]
                
                # Calculate centers
                center1 = self._scale_point(
                    ((pos1[0] + pos1[2]) / 2, (pos1[1] + pos1[3]) / 2)
                )
                center2 = self._scale_point(
                    ((pos2[0] + pos2[2]) / 2, (pos2[1] + pos2[3]) / 2)
                )
                
                # Draw line
                draw.line([center1, center2], fill=self.config.collision_color, width=2)
        
        # Save if output path provided
        if output_path:
            img.save(output_path)
        
        return img
    
    def create_movement_visualization(
        self,
        old_positions: List[Tuple[float, float, float, float]],
        new_positions: List[Tuple[float, float, float, float]],
        elements: Optional[List[YMLElement]] = None,
        output_path: Optional[str] = None,
        title: Optional[str] = None
    ) -> Image.Image:
        """
        Create a visualization showing movement from old to new positions.
        
        Arrows show the direction and magnitude of movement.
        
        Args:
            old_positions: List of old position tuples (x1, y1, x2, y2)
            new_positions: List of new position tuples (x1, y1, x2, y2)
            elements: Optional list of YMLElement objects for labels
            output_path: Optional path to save the image
            title: Optional title for the image
            
        Returns:
            PIL Image object
        """
        # Calculate image dimensions
        img_width = int(self.config.page_width * self.config.scale_factor)
        img_height = int(self.config.page_height * self.config.scale_factor)
        
        # Create image
        img = Image.new('RGB', (img_width, img_height), self.config.background_color)
        draw = ImageDraw.Draw(img)
        
        # Draw title
        if title:
            draw.text((10, 10), title, fill=(0, 0, 0), font=self.font)
        
        # Draw positions and movement arrows
        for i in range(min(len(old_positions), len(new_positions))):
            old_pos = old_positions[i]
            new_pos = new_positions[i]
            
            # Draw old position (faded)
            self._draw_position(
                draw,
                old_pos,
                (200, 200, 200),
                label=None
            )
            
            # Draw new position
            label = None
            if self.config.show_labels and elements and i < len(elements):
                text = elements[i].text[:15]
                if text:
                    label = f"{i}: {text}"
            elif self.config.show_indices:
                label = str(i)
            
            self._draw_position(
                draw,
                new_pos,
                self.config.new_position_color,
                label=label
            )
            
            # Draw arrow from old to new
            old_center = self._scale_point(
                ((old_pos[0] + old_pos[2]) / 2, (old_pos[1] + old_pos[3]) / 2)
            )
            new_center = self._scale_point(
                ((new_pos[0] + new_pos[2]) / 2, (new_pos[1] + new_pos[3]) / 2)
            )
            
            # Only draw arrow if there's significant movement
            distance = ((new_center[0] - old_center[0])**2 + 
                       (new_center[1] - old_center[1])**2)**0.5
            
            if distance > 5:  # Minimum movement threshold
                self._draw_arrow(draw, old_center, new_center, (0, 0, 255))
        
        # Save if output path provided
        if output_path:
            img.save(output_path)
        
        return img
    
    def _draw_position(
        self,
        draw: ImageDraw.ImageDraw,
        position: Tuple[float, float, float, float],
        color: Tuple[int, int, int],
        label: Optional[str] = None,
        alpha: int = 255,
        x_offset: int = 0,
        y_offset: int = 0
    ):
        """
        Draw a position rectangle on the image.
        
        Args:
            draw: ImageDraw object
            position: Position tuple (x1, y1, x2, y2)
            color: RGB color tuple
            label: Optional label text
            alpha: Transparency (0-255)
            x_offset: X offset for positioning
            y_offset: Y offset for positioning
        """
        x1, y1, x2, y2 = position
        
        # Scale coordinates
        x1_scaled = int(x1 * self.config.scale_factor) + x_offset
        y1_scaled = int((self.config.page_height - y2) * self.config.scale_factor) + y_offset
        x2_scaled = int(x2 * self.config.scale_factor) + x_offset
        y2_scaled = int((self.config.page_height - y1) * self.config.scale_factor) + y_offset
        
        # Draw rectangle
        draw.rectangle(
            [x1_scaled, y1_scaled, x2_scaled, y2_scaled],
            outline=color,
            width=self.config.line_width
        )
        
        # Draw label if provided
        if label:
            # Position label at top-left of rectangle
            label_x = x1_scaled + 2
            label_y = y1_scaled + 2
            
            # Draw label background for readability
            bbox = draw.textbbox((label_x, label_y), label, font=self.font)
            draw.rectangle(bbox, fill=(255, 255, 255, 200))
            
            # Draw label text
            draw.text((label_x, label_y), label, fill=color, font=self.font)
    
    def _scale_point(
        self,
        point: Tuple[float, float]
    ) -> Tuple[int, int]:
        """
        Scale a point from PDF coordinates to image coordinates.
        
        Args:
            point: Point tuple (x, y) in PDF coordinates
            
        Returns:
            Scaled point tuple (x, y) in image coordinates
        """
        x, y = point
        x_scaled = int(x * self.config.scale_factor)
        y_scaled = int((self.config.page_height - y) * self.config.scale_factor)
        return (x_scaled, y_scaled)
    
    def _draw_arrow(
        self,
        draw: ImageDraw.ImageDraw,
        start: Tuple[int, int],
        end: Tuple[int, int],
        color: Tuple[int, int, int],
        arrow_size: int = 10
    ):
        """
        Draw an arrow from start to end point.
        
        Args:
            draw: ImageDraw object
            start: Start point (x, y)
            end: End point (x, y)
            color: RGB color tuple
            arrow_size: Size of arrow head
        """
        # Draw line
        draw.line([start, end], fill=color, width=2)
        
        # Calculate arrow head
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = (dx**2 + dy**2)**0.5
        
        if length > 0:
            # Normalize direction
            dx /= length
            dy /= length
            
            # Calculate arrow head points
            angle = 0.5  # Angle of arrow head
            
            # Left point
            left_x = end[0] - arrow_size * (dx * 0.866 + dy * 0.5)
            left_y = end[1] - arrow_size * (dy * 0.866 - dx * 0.5)
            
            # Right point
            right_x = end[0] - arrow_size * (dx * 0.866 - dy * 0.5)
            right_y = end[1] - arrow_size * (dy * 0.866 + dx * 0.5)
            
            # Draw arrow head
            draw.polygon(
                [end, (int(left_x), int(left_y)), (int(right_x), int(right_y))],
                fill=color
            )
    
    def generate_visualization_report(
        self,
        old_positions: List[Tuple[float, float, float, float]],
        new_positions: List[Tuple[float, float, float, float]],
        elements: Optional[List[YMLElement]] = None,
        output_dir: Optional[str] = None,
        firma: Optional[int] = None,
        seite: Optional[int] = None
    ) -> Dict[str, str]:
        """
        Generate a complete set of visualization images.
        
        Creates:
        - Overlay image
        - Comparison view
        - Movement visualization
        
        Args:
            old_positions: List of old position tuples
            new_positions: List of new position tuples
            elements: Optional list of YMLElement objects
            output_dir: Directory to save images
            firma: Optional firma number
            seite: Optional seite number
            
        Returns:
            Dictionary mapping visualization type to file path
        """
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = Path("visualizations")
            output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename prefix
        prefix = ""
        if firma is not None and seite is not None:
            prefix = f"f{firma}_s{seite}_"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate visualizations
        results = {}
        
        # Overlay image
        overlay_path = output_path / f"{prefix}overlay_{timestamp}.png"
        self.create_overlay_image(
            old_positions,
            new_positions,
            elements,
            str(overlay_path),
            title=f"Position Overlay - Firma {firma}, Seite {seite}" if firma and seite else "Position Overlay"
        )
        results["overlay"] = str(overlay_path)
        
        # Comparison view
        comparison_path = output_path / f"{prefix}comparison_{timestamp}.png"
        self.create_comparison_view(
            old_positions,
            new_positions,
            elements,
            str(comparison_path),
            firma,
            seite
        )
        results["comparison"] = str(comparison_path)
        
        # Movement visualization
        movement_path = output_path / f"{prefix}movement_{timestamp}.png"
        self.create_movement_visualization(
            old_positions,
            new_positions,
            elements,
            str(movement_path),
            title=f"Position Movement - Firma {firma}, Seite {seite}" if firma and seite else "Position Movement"
        )
        results["movement"] = str(movement_path)
        
        return results


# Convenience functions
def create_overlay_image(
    old_positions: List[Tuple[float, float, float, float]],
    new_positions: List[Tuple[float, float, float, float]],
    elements: Optional[List[YMLElement]] = None,
    output_path: Optional[str] = None
) -> Image.Image:
    """
    Convenience function to create an overlay image.
    
    Args:
        old_positions: List of old position tuples
        new_positions: List of new position tuples
        elements: Optional list of YMLElement objects
        output_path: Optional path to save the image
        
    Returns:
        PIL Image object
    """
    tool = VisualizationTool()
    return tool.create_overlay_image(old_positions, new_positions, elements, output_path)


def create_comparison_view(
    old_positions: List[Tuple[float, float, float, float]],
    new_positions: List[Tuple[float, float, float, float]],
    elements: Optional[List[YMLElement]] = None,
    output_path: Optional[str] = None,
    firma: Optional[int] = None,
    seite: Optional[int] = None
) -> Image.Image:
    """
    Convenience function to create a comparison view.
    
    Args:
        old_positions: List of old position tuples
        new_positions: List of new position tuples
        elements: Optional list of YMLElement objects
        output_path: Optional path to save the image
        firma: Optional firma number
        seite: Optional seite number
        
    Returns:
        PIL Image object
    """
    tool = VisualizationTool()
    return tool.create_comparison_view(
        old_positions, new_positions, elements, output_path, firma, seite
    )


if __name__ == "__main__":
    # Example usage
    print("\n=== Visualization Tool Demo ===\n")
    
    # Create visualization tool
    tool = VisualizationTool()
    
    print("Configuration:")
    print(f"  Page size: {tool.config.page_width} x {tool.config.page_height} pts")
    print(f"  Scale factor: {tool.config.scale_factor}")
    print(f"  Old position color: {tool.config.old_position_color}")
    print(f"  New position color: {tool.config.new_position_color}")
    print()
    
    # Test positions
    old_positions = [
        (50, 700, 200, 750),
        (250, 700, 400, 750),
        (50, 600, 200, 650),
    ]
    
    new_positions = [
        (100, 720, 250, 770),  # Moved right and up
        (300, 680, 450, 730),  # Moved right and down
        (80, 580, 230, 630),   # Moved right and down
    ]
    
    print("Creating visualizations...")
    
    # Create overlay
    print("  - Overlay image")
    overlay = tool.create_overlay_image(
        old_positions,
        new_positions,
        output_path="test_overlay.png",
        title="Test Overlay"
    )
    
    # Create comparison
    print("  - Comparison view")
    comparison = tool.create_comparison_view(
        old_positions,
        new_positions,
        output_path="test_comparison.png",
        firma=1,
        seite=1
    )
    
    # Create movement visualization
    print("  - Movement visualization")
    movement = tool.create_movement_visualization(
        old_positions,
        new_positions,
        output_path="test_movement.png",
        title="Test Movement"
    )
    
    print("\n✓ Visualization Tool module ready")
    print("  Generated test images:")
    print("    - test_overlay.png")
    print("    - test_comparison.png")
    print("    - test_movement.png")
