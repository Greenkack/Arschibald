"""
PDF Analyzer Module for Multi-PDF Positioning System

This module analyzes PDF templates and extracts design information including
page dimensions, color regions, and safe zones for text placement.
"""

import json
from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path
import PyPDF2


@dataclass
class DesignRegion:
    """
    Represents a design region in a PDF template.

    Attributes:
        type: Region type (header, content, footer)
        bounds: Rectangle coordinates (x1, y1, x2, y2)
        dominant_color: Hex color code
        suggested_text_color: Recommended text color for this region
    """
    type: str
    bounds: Dict[str, float]
    dominant_color: str
    suggested_text_color: str


@dataclass
class VisualElement:
    """
    Represents a visual element (shape, line, etc.) in the PDF.

    Attributes:
        type: Element type (shape, line, etc.)
        position: List of coordinates
        color: Hex color code
    """
    type: str
    position: List[float]
    color: str


@dataclass
class SafeZone:
    """
    Represents a safe zone for text placement.

    Attributes:
        x1: Left coordinate
        y1: Bottom coordinate
        x2: Right coordinate
        y2: Top coordinate
    """
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass
class PDFAnalysis:
    """
    Complete analysis result for a PDF template.

    Attributes:
        firma: Firma number (1-6)
        seite: Seite number (1-8)
        page_size: Dictionary with width and height
        design_regions: List of identified design regions
        visual_elements: List of visual elements
        safe_zones: List of safe zones for text
        color_palette: List of hex color codes
    """
    firma: int
    seite: int
    page_size: Dict[str, float]
    design_regions: List[DesignRegion]
    visual_elements: List[VisualElement]
    safe_zones: List[SafeZone]
    color_palette: List[str]


class PDFAnalyzer:
    """
    Analyzer for PDF templates.

    This analyzer extracts metadata and design characteristics from PDF files
    to inform optimal text positioning strategies.
    """

    def __init__(self, pdf_dir: Optional[str] = None):
        """
        Initialize the PDF analyzer.

        Args:
            pdf_dir: Directory containing PDF files (optional)
        """
        self.analysis_results: List[PDFAnalysis] = []
        self.pdf_dir = Path(pdf_dir) if pdf_dir else None

    def analyze_pdf(self, pdf_path: str) -> PDFAnalysis:
        """
        Analyze a PDF template and extract design characteristics.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            PDFAnalysis object with all extracted information

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If the PDF is invalid or corrupted
        """
        pdf_file = Path(pdf_path)

        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Extract firma and seite from filename
        # Format: multi_nt_01_f1.pdf
        filename = pdf_file.stem
        parts = filename.split('_')
        try:
            seite = int(parts[2])  # "01" -> 1
            firma = int(parts[3][1:])  # "f1" -> 1
        except (IndexError, ValueError) as e:
            raise ValueError(f"Invalid PDF filename format: {filename}") from e

        # Extract page size
        page_size = self._extract_page_size(pdf_path)

        # Extract color palette
        color_palette = self._extract_color_palette(pdf_path, firma, seite)

        # Analyze design regions with color information
        design_regions = self._analyze_design_regions(
            page_size,
            firma,
            seite,
            color_palette
        )

        # Define safe zones
        safe_zones = self._define_safe_zones(page_size, design_regions)

        # Detect visual elements (simplified)
        visual_elements = self._detect_visual_elements(
            page_size,
            design_regions
        )

        # Create analysis result
        analysis = PDFAnalysis(
            firma=firma,
            seite=seite,
            page_size=page_size,
            design_regions=design_regions,
            visual_elements=visual_elements,
            safe_zones=safe_zones,
            color_palette=color_palette
        )

        return analysis

    def _extract_page_size(self, pdf_path: str) -> Dict[str, float]:
        """
        Extract page dimensions from PDF.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary with width and height in points

        Raises:
            ValueError: If PDF cannot be read or has no pages
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                if len(pdf_reader.pages) == 0:
                    raise ValueError(f"PDF has no pages: {pdf_path}")

                # Get first page
                page = pdf_reader.pages[0]

                # Get page dimensions
                mediabox = page.mediabox
                width = float(mediabox.width)
                height = float(mediabox.height)

                return {
                    "width": width,
                    "height": height
                }

        except Exception as e:
            raise ValueError(f"Failed to read PDF {pdf_path}: {e}") from e

    def _extract_color_palette(
        self,
        pdf_path: str,
        firma: int,
        seite: int
    ) -> List[str]:
        """
        Extract color palette from PDF (simplified).

        This is a simplified implementation that assigns typical colors
        based on firma number to represent different design styles.

        Args:
            pdf_path: Path to the PDF file
            firma: Firma number
            seite: Seite number

        Returns:
            List of hex color codes
        """
        # Simplified color palettes per firma
        firma_palettes = {
            1: ["#007BFF", "#FFFFFF", "#F8F9FA", "#000000"],
            2: ["#28A745", "#FFFFFF", "#E9ECEF", "#212529"],
            3: ["#DC3545", "#FFFFFF", "#F1F3F5", "#343A40"],
            4: ["#FFC107", "#FFFFFF", "#F5F5F5", "#495057"],
            5: ["#17A2B8", "#FFFFFF", "#E7E7E7", "#6C757D"],
            6: ["#6F42C1", "#FFFFFF", "#F0F0F0", "#868E96"]
        }

        return firma_palettes.get(firma, ["#FFFFFF", "#000000"])

    def _analyze_design_regions(
        self,
        page_size: Dict[str, float],
        firma: int,
        seite: int,
        color_palette: List[str]
    ) -> List[DesignRegion]:
        """
        Identify design regions based on Y-coordinates and firma style.

        This implementation divides the page into regions and assigns
        colors based on the firma's design palette.

        Args:
            page_size: Dictionary with width and height
            firma: Firma number
            seite: Seite number
            color_palette: List of colors for this firma

        Returns:
            List of DesignRegion objects
        """
        width = page_size["width"]
        height = page_size["height"]

        regions = []

        # Primary color (brand color)
        primary_color = color_palette[0] if color_palette else "#007BFF"
        bg_color = color_palette[1] if len(color_palette) > 1 else "#FFFFFF"
        light_bg = color_palette[2] if len(color_palette) > 2 else "#F8F9FA"
        text_color = color_palette[3] if len(color_palette) > 3 else "#000000"

        # Header region (top 20% of page) - often has brand color
        header = DesignRegion(
            type="header",
            bounds={
                "x1": 0,
                "y1": height * 0.8,
                "x2": width,
                "y2": height
            },
            dominant_color=primary_color,
            suggested_text_color="#FFFFFF"
        )
        regions.append(header)

        # Content region (middle 70% of page)
        content = DesignRegion(
            type="content",
            bounds={
                "x1": 0,
                "y1": height * 0.1,
                "x2": width,
                "y2": height * 0.8
            },
            dominant_color=bg_color,
            suggested_text_color=text_color
        )
        regions.append(content)

        # Footer region (bottom 10% of page)
        footer = DesignRegion(
            type="footer",
            bounds={
                "x1": 0,
                "y1": 0,
                "x2": width,
                "y2": height * 0.1
            },
            dominant_color=light_bg,
            suggested_text_color=text_color
        )
        regions.append(footer)

        return regions

    def _detect_visual_elements(
        self,
        page_size: Dict[str, float],
        design_regions: List[DesignRegion]
    ) -> List[VisualElement]:
        """
        Detect visual elements in the PDF (simplified).

        This is a simplified implementation that creates placeholder
        visual elements based on design regions.

        Args:
            page_size: Dictionary with width and height
            design_regions: List of design regions

        Returns:
            List of VisualElement objects
        """
        visual_elements = []

        # Create visual elements for each region
        for region in design_regions:
            bounds = region.bounds
            element = VisualElement(
                type="shape",
                position=[
                    bounds["x1"],
                    bounds["y1"],
                    bounds["x2"],
                    bounds["y2"]
                ],
                color=region.dominant_color
            )
            visual_elements.append(element)

        return visual_elements

    def _define_safe_zones(
        self,
        page_size: Dict[str, float],
        design_regions: List[DesignRegion]
    ) -> List[SafeZone]:
        """
        Define safe zones for text placement based on design regions.

        Safe zones have margins from page edges and avoid overlapping
        with critical design elements.

        Args:
            page_size: Dictionary with width and height
            design_regions: List of design regions

        Returns:
            List of SafeZone objects
        """
        width = page_size["width"]
        height = page_size["height"]

        safe_zones = []

        # Standard margins
        margin = 50  # 50 points margin on all sides

        # Create safe zones for each region
        for region in design_regions:
            bounds = region.bounds

            # Add margin within each region
            safe_zone = SafeZone(
                x1=max(bounds["x1"] + margin, margin),
                y1=max(bounds["y1"] + 10, margin),
                x2=min(bounds["x2"] - margin, width - margin),
                y2=min(bounds["y2"] - 10, height - margin)
            )

            # Only add if zone has positive dimensions
            if safe_zone.x2 > safe_zone.x1 and safe_zone.y2 > safe_zone.y1:
                safe_zones.append(safe_zone)

        # If no safe zones created, add default
        if not safe_zones:
            safe_zones.append(SafeZone(
                x1=margin,
                y1=margin,
                x2=width - margin,
                y2=height - margin
            ))

        return safe_zones

    def analyze_all_pdfs(
        self,
        pdf_dir: Optional[str] = None,
        firmen: Optional[List[int]] = None,
        seiten: Optional[List[int]] = None
    ) -> List[PDFAnalysis]:
        """
        Analyze all PDF templates in batch.

        Args:
            pdf_dir: Directory containing PDF files (uses self.pdf_dir if None)
            firmen: List of firma numbers to analyze (default: [1-6])
            seiten: List of seite numbers to analyze (default: [1-8])

        Returns:
            List of PDFAnalysis objects for all analyzed PDFs

        Raises:
            ValueError: If pdf_dir is not provided and not set in __init__
        """
        # Use provided directory or instance directory
        directory = Path(pdf_dir) if pdf_dir else self.pdf_dir

        if not directory:
            raise ValueError("PDF directory must be provided")

        if not directory.exists():
            raise FileNotFoundError(f"PDF directory not found: {directory}")

        # Default to all firmen and seiten
        if firmen is None:
            firmen = [1, 2, 3, 4, 5, 6]
        if seiten is None:
            seiten = [1, 2, 3, 4, 5, 6, 7, 8]

        self.analysis_results = []
        errors = []

        # Analyze each combination
        total = len(firmen) * len(seiten)
        current = 0

        print(f"\nAnalyzing {total} PDF templates...")

        for firma in firmen:
            for seite in seiten:
                current += 1
                # Construct filename: multi_nt_01_f1.pdf
                filename = f"multi_nt_{seite:02d}_f{firma}.pdf"
                if filename != 0:
                    pdf_path = directory / filename
                else:
                    pdf_path = 0.0

                try:
                    analysis = self.analyze_pdf(str(pdf_path))
                    self.analysis_results.append(analysis)

                    if current % 10 == 0 or current == total:
                        print(f"  Progress: {current}/{total} PDFs analyzed")

                except Exception as e:
                    error_msg = f"Failed to analyze {filename}: {e}"
                    errors.append(error_msg)
                    print(f"  Warning: {error_msg}")

        print(f"\nCompleted: {len(self.analysis_results)} PDFs analyzed")
        if errors:
            print(f"Errors: {len(errors)} PDFs failed")

        return self.analysis_results

    def save_analysis_results(
        self,
        output_path: str,
        include_summary: bool = True
    ) -> None:
        """
        Save analysis results to JSON file.

        Args:
            output_path: Path to output JSON file
            include_summary: Whether to include summary statistics
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert dataclasses to dictionaries
        results_dict = {
            "total_pdfs": len(self.analysis_results),
            "analyses": []
        }

        for analysis in self.analysis_results:
            analysis_dict = {
                "firma": analysis.firma,
                "seite": analysis.seite,
                "page_size": analysis.page_size,
                "design_regions": [
                    {
                        "type": r.type,
                        "bounds": r.bounds,
                        "dominant_color": r.dominant_color,
                        "suggested_text_color": r.suggested_text_color
                    }
                    for r in analysis.design_regions
                ],
                "visual_elements": [
                    {
                        "type": e.type,
                        "position": e.position,
                        "color": e.color
                    }
                    for e in analysis.visual_elements
                ],
                "safe_zones": [
                    {
                        "x1": z.x1,
                        "y1": z.y1,
                        "x2": z.x2,
                        "y2": z.y2
                    }
                    for z in analysis.safe_zones
                ],
                "color_palette": analysis.color_palette
            }
            results_dict["analyses"].append(analysis_dict)

        # Add summary if requested
        if include_summary:
            results_dict["summary"] = self._generate_summary()

        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_dict, f, indent=2, ensure_ascii=False)

        print(f"\nAnalysis results saved to: {output_file}")

    def _generate_summary(self) -> Dict:
        """
        Generate summary statistics for all analyses.

        Returns:
            Dictionary with summary statistics
        """
        if not self.analysis_results:
            return {}

        # Group by firma
        firma_stats = {}
        for analysis in self.analysis_results:
            firma = analysis.firma
            if firma not in firma_stats:
                firma_stats[firma] = {
                    "count": 0,
                    "color_palette": analysis.color_palette,
                    "avg_safe_zone_area": 0,
                    "design_regions": len(analysis.design_regions)
                }

            firma_stats[firma]["count"] += 1

            # Calculate safe zone area
            total_area = sum(
                (z.x2 - z.x1) * (z.y2 - z.y1)
                for z in analysis.safe_zones
            )
            firma_stats[firma]["avg_safe_zone_area"] += total_area

        # Calculate averages
        for firma, stats in firma_stats.items():
            if stats["count"] > 0:
                stats["avg_safe_zone_area"] /= stats["count"]
                stats["avg_safe_zone_area"] = round(
                    stats["avg_safe_zone_area"],
                    2
                )

        return {
            "total_analyses": len(self.analysis_results),
            "firmen_analyzed": len(firma_stats),
            "firma_statistics": firma_stats
        }

    def get_analysis(self) -> List[PDFAnalysis]:
        """
        Get all analysis results.

        Returns:
            List of PDFAnalysis objects
        """
        return self.analysis_results

    def get_analysis_by_firma(self, firma: int) -> List[PDFAnalysis]:
        """
        Get all analyses for a specific firma.

        Args:
            firma: Firma number

        Returns:
            List of PDFAnalysis objects for the firma
        """
        return [a for a in self.analysis_results if a.firma == firma]

    def get_analysis_by_seite(self, seite: int) -> List[PDFAnalysis]:
        """
        Get all analyses for a specific seite.

        Args:
            seite: Seite number

        Returns:
            List of PDFAnalysis objects for the seite
        """
        return [a for a in self.analysis_results if a.seite == seite]


def analyze_pdf(pdf_path: str) -> PDFAnalysis:
    """
    Convenience function to analyze a single PDF.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        PDFAnalysis object
    """
    analyzer = PDFAnalyzer()
    return analyzer.analyze_pdf(pdf_path)


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
    else:
        pdf_file = "pdf_templates_static/multi/multi_nt_01_f1.pdf"

    try:
        analyzer = PDFAnalyzer()
        analysis = analyzer.analyze_pdf(pdf_file)

        print("\n=== PDF Analysis Results ===")
        print(f"File: {pdf_file}")
        print(f"Firma: {analysis.firma}")
        print(f"Seite: {analysis.seite}")
        print(f"\nPage Size:")
        print(f"  Width: {analysis.page_size['width']} points")
        print(f"  Height: {analysis.page_size['height']} points")

        print(f"\nColor Palette ({len(analysis.color_palette)}):")
        for color in analysis.color_palette:
            print(f"  - {color}")

        print(f"\nDesign Regions ({len(analysis.design_regions)}):")
        for region in analysis.design_regions:
            print(f"  - {region.type}:")
            print(f"    Bounds: {region.bounds}")
            print(f"    Color: {region.dominant_color}")
            print(f"    Text Color: {region.suggested_text_color}")

        print(f"\nVisual Elements ({len(analysis.visual_elements)}):")
        for i, elem in enumerate(analysis.visual_elements[:3]):
            print(f"  - Element {i+1}: {elem.type}")
            print(f"    Position: {elem.position}")
            print(f"    Color: {elem.color}")

        print(f"\nSafe Zones ({len(analysis.safe_zones)}):")
        for i, zone in enumerate(analysis.safe_zones):
            print(f"  - Zone {i+1}:")
            print(f"    ({zone.x1:.1f}, {zone.y1:.1f}) to "
                  f"({zone.x2:.1f}, {zone.y2:.1f})")
            size_str = f"{zone.x2-zone.x1:.1f} x {zone.y2-zone.y1:.1f}"
            print(f"    Size: {size_str}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
