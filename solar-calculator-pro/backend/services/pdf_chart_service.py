"""
PDF Chart Service - Comprehensive chart rendering for PDF export
Supports 10 chart types with German formatting and YML positioning
"""

from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import io
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing, String, Line, Rect, Circle, Wedge, Polygon
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.legends import Legend
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import math


class ChartType(Enum):
    """Supported chart types"""
    CIRCLE = "circle"
    DONUT = "donut"
    BAR = "bar"
    COLUMN = "column"
    LINE = "line"
    AREA = "area"
    PIE = "pie"
    POLAR = "polar"
    RADAR = "radar"
    WATERFALL = "waterfall"


class ColorScheme(Enum):
    """Available color schemes"""
    SOLAR = "solar"  # Yellow, orange, red tones
    NATURE = "nature"  # Green, blue, earth tones
    PROFESSIONAL = "professional"  # Blue, gray, corporate
    VIBRANT = "vibrant"  # Bright, high-contrast colors
    MONOCHROME = "monochrome"  # Grayscale variations


class PDFChartService:
    """Service for generating charts in PDF format"""
    
    def __init__(self):
        self.color_schemes = self._init_color_schemes()
        
    def _init_color_schemes(self) -> Dict[str, List[colors.Color]]:
        """Initialize color schemes for charts"""
        return {
            ColorScheme.SOLAR.value: [
                colors.Color(1, 0.8, 0),      # Bright yellow
                colors.Color(1, 0.6, 0),      # Orange
                colors.Color(1, 0.4, 0),      # Dark orange
                colors.Color(0.9, 0.2, 0),    # Red-orange
                colors.Color(0.8, 0, 0),      # Red
                colors.Color(0.6, 0, 0),      # Dark red
            ],
            ColorScheme.NATURE.value: [
                colors.Color(0.2, 0.6, 0.2),  # Green
                colors.Color(0.1, 0.5, 0.7),  # Blue
                colors.Color(0.4, 0.5, 0.2),  # Olive
                colors.Color(0.2, 0.4, 0.6),  # Sky blue
                colors.Color(0.5, 0.3, 0.1),  # Brown
                colors.Color(0.3, 0.6, 0.4),  # Teal
            ],
            ColorScheme.PROFESSIONAL.value: [
                colors.Color(0.2, 0.4, 0.7),  # Corporate blue
                colors.Color(0.5, 0.5, 0.5),  # Gray
                colors.Color(0.3, 0.5, 0.8),  # Light blue
                colors.Color(0.4, 0.4, 0.4),  # Dark gray
                colors.Color(0.6, 0.6, 0.6),  # Light gray
                colors.Color(0.1, 0.3, 0.6),  # Navy
            ],
            ColorScheme.VIBRANT.value: [
                colors.Color(1, 0, 0.5),      # Magenta
                colors.Color(0, 0.8, 1),      # Cyan
                colors.Color(1, 0.8, 0),      # Yellow
                colors.Color(0.5, 0, 1),      # Purple
                colors.Color(0, 1, 0.5),      # Spring green
                colors.Color(1, 0.4, 0),      # Orange
            ],
            ColorScheme.MONOCHROME.value: [
                colors.Color(0.2, 0.2, 0.2),  # Very dark gray
                colors.Color(0.4, 0.4, 0.4),  # Dark gray
                colors.Color(0.5, 0.5, 0.5),  # Medium gray
                colors.Color(0.6, 0.6, 0.6),  # Light gray
                colors.Color(0.7, 0.7, 0.7),  # Very light gray
                colors.Color(0.8, 0.8, 0.8),  # Almost white
            ]
        }

    
    def format_german_number(self, value: float, decimal_places: int = 2) -> str:
        """Format number with German locale (dot as thousand separator, comma as decimal)"""
        if value is None:
            return "0,00"
        
        # Format with decimal places
        formatted = f"{value:,.{decimal_places}f}"
        
        # Replace English formatting with German
        formatted = formatted.replace(",", "X")  # Temp placeholder
        formatted = formatted.replace(".", ",")  # Decimal point to comma
        formatted = formatted.replace("X", ".")  # Thousand separator to dot
        
        return formatted
    
    def format_currency(self, value: float) -> str:
        """Format as German currency"""
        return f"{self.format_german_number(value, 2)} €"
    
    def format_percentage(self, value: float) -> str:
        """Format as German percentage"""
        return f"{self.format_german_number(value, 1)}%"
    
    def format_kwh(self, value: float) -> str:
        """Format as kWh"""
        return f"{self.format_german_number(value, 0)} kWh"

    
    def generate_chart(
        self,
        chart_type: ChartType,
        data: Dict[str, Any],
        width: float = 400,
        height: float = 300,
        color_scheme: ColorScheme = ColorScheme.PROFESSIONAL,
        enable_3d: bool = False,
        title: str = "",
        x_label: str = "",
        y_label: str = "",
        show_legend: bool = True,
        show_values: bool = True
    ) -> Drawing:
        """
        Generate a chart drawing for PDF
        
        Args:
            chart_type: Type of chart to generate
            data: Chart data (format depends on chart type)
            width: Chart width in points
            height: Chart height in points
            color_scheme: Color scheme to use
            enable_3d: Enable 3D effects
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            show_legend: Show legend
            show_values: Show data values on chart
            
        Returns:
            Drawing object ready for PDF
        """
        if chart_type == ChartType.PIE:
            return self._generate_pie_chart(data, width, height, color_scheme, enable_3d, title, show_legend, show_values)
        elif chart_type == ChartType.DONUT:
            return self._generate_donut_chart(data, width, height, color_scheme, enable_3d, title, show_legend, show_values)
        elif chart_type == ChartType.BAR:
            return self._generate_bar_chart(data, width, height, color_scheme, enable_3d, title, x_label, y_label, show_legend, show_values)
        elif chart_type == ChartType.COLUMN:
            return self._generate_column_chart(data, width, height, color_scheme, enable_3d, title, x_label, y_label, show_legend, show_values)
        elif chart_type == ChartType.LINE:
            return self._generate_line_chart(data, width, height, color_scheme, enable_3d, title, x_label, y_label, show_legend, show_values)
        elif chart_type == ChartType.AREA:
            return self._generate_area_chart(data, width, height, color_scheme, enable_3d, title, x_label, y_label, show_legend, show_values)
        elif chart_type == ChartType.CIRCLE:
            return self._generate_circle_chart(data, width, height, color_scheme, title, show_values)
        elif chart_type == ChartType.POLAR:
            return self._generate_polar_chart(data, width, height, color_scheme, title, show_legend, show_values)
        elif chart_type == ChartType.RADAR:
            return self._generate_radar_chart(data, width, height, color_scheme, title, show_legend, show_values)
        elif chart_type == ChartType.WATERFALL:
            return self._generate_waterfall_chart(data, width, height, color_scheme, title, x_label, y_label, show_values)
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")

    
    def _generate_pie_chart(
        self,
        data: Dict[str, Any],
        width: float,
        height: float,
        color_scheme: ColorScheme,
        enable_3d: bool,
        title: str,
        show_legend: bool,
        show_values: bool
    ) -> Drawing:
        """Generate pie chart"""
        drawing = Drawing(width, height)
        
        # Add title
        if title:
            drawing.add(String(width/2, height-20, title, fontSize=14, textAnchor='middle', fontName='Helvetica-Bold'))
        
        # Create pie chart
        pie = Pie()
        pie.x = 50
        pie.y = 50
        pie.width = min(width, height) - 150
        pie.height = min(width, height) - 150
        
        # Set data
        labels = data.get('labels', [])
        values = data.get('values', [])
        pie.data = values
        pie.labels = labels
        
        # Apply colors
        colors_list = self.color_schemes[color_scheme.value]
        pie.slices.strokeColor = colors.white
        pie.slices.strokeWidth = 2
        for i, color in enumerate(colors_list):
            if i < len(values):
                pie.slices[i].fillColor = color
        
        # 3D effect
        if enable_3d:
            pie.slices.popout = 10
            pie.sideLabels = 1
        
        # Show values
        if show_values:
            pie.slices.fontName = 'Helvetica'
            pie.slices.fontSize = 10
            pie.slices.labelRadius = 1.2
        
        drawing.add(pie)
        
        # Add legend
        if show_legend:
            legend = self._create_legend(labels, colors_list[:len(labels)], width-150, height-100)
            drawing.add(legend)
        
        return drawing

    
    def _generate_donut_chart(
        self,
        data: Dict[str, Any],
        width: float,
        height: float,
        color_scheme: ColorScheme,
        enable_3d: bool,
        title: str,
        show_legend: bool,
        show_values: bool
    ) -> Drawing:
        """Generate donut chart (pie with inner circle)"""
        drawing = self._generate_pie_chart(data, width, height, color_scheme, enable_3d, title, show_legend, show_values)
        
        # Add inner circle to create donut effect
        pie_size = min(width, height) - 150
        center_x = 50 + pie_size/2
        center_y = 50 + pie_size/2
        inner_radius = pie_size * 0.4
        
        inner_circle = Circle(center_x, center_y, inner_radius)
        inner_circle.fillColor = colors.white
        inner_circle.strokeColor = None
        drawing.add(inner_circle)
        
        return drawing

    
    def _generate_bar_chart(
        self,
        data: Dict[str, Any],
        width: float,
        height: float,
        color_scheme: ColorScheme,
        enable_3d: bool,
        title: str,
        x_label: str,
        y_label: str,
        show_legend: bool,
        show_values: bool
    ) -> Drawing:
        """Generate horizontal bar chart"""
        drawing = Drawing(width, height)
        
        # Add title
        if title:
            drawing.add(String(width/2, height-20, title, fontSize=14, textAnchor='middle', fontName='Helvetica-Bold'))
        
        # Create bar chart
        bc = HorizontalBarChart()
        bc.x = 100
        bc.y = 50
        bc.width = width - 200
        bc.height = height - 100
        
        # Set data
        categories = data.get('categories', [])
        series_data = data.get('series', [])
        bc.data = series_data
        bc.categoryAxis.categoryNames = categories
        
        # Apply colors
        colors_list = self.color_schemes[color_scheme.value]
        for i, color in enumerate(colors_list):
            if i < len(series_data):
                bc.bars[i].fillColor = color
        
        # 3D effect
        if enable_3d:
            bc.bars.strokeColor = colors.black
            bc.bars.strokeWidth = 1
        
        # Axis labels
        bc.categoryAxis.labels.fontName = 'Helvetica'
        bc.categoryAxis.labels.fontSize = 9
        bc.valueAxis.labels.fontName = 'Helvetica'
        bc.valueAxis.labels.fontSize = 9
        
        # Format value axis with German numbers
        bc.valueAxis.labelTextFormat = lambda x: self.format_german_number(x, 0)
        
        drawing.add(bc)
        
        # Add axis labels
        if x_label:
            drawing.add(String(width/2, 30, x_label, fontSize=10, textAnchor='middle'))
        if y_label:
            drawing.add(String(30, height/2, y_label, fontSize=10, textAnchor='middle'))
        
        return drawing

    
    def _generate_column_chart(
        self,
        data: Dict[str, Any],
        width: float,
        height: float,
        color_scheme: ColorScheme,
        enable_3d: bool,
        title: str,
        x_label: str,
        y_label: str,
        show_legend: bool,
        show_values: bool
    ) -> Drawing:
        """Generate vertical column chart"""
        drawing = Drawing(width, height)
        
        # Add title
        if title:
            drawing.add(String(width/2, height-20, title, fontSize=14, textAnchor='middle', fontName='Helvetica-Bold'))
        
        # Create column chart
        bc = VerticalBarChart()
        bc.x = 80
        bc.y = 80
        bc.width = width - 150
        bc.height = height - 150
        
        # Set data
        categories = data.get('categories', [])
        series_data = data.get('series', [])
        bc.data = series_data
        bc.categoryAxis.categoryNames = categories
        
        # Apply colors
        colors_list = self.color_schemes[color_scheme.value]
        for i, color in enumerate(colors_list):
            if i < len(series_data):
                bc.bars[i].fillColor = color
        
        # 3D effect
        if enable_3d:
            bc.bars.strokeColor = colors.black
            bc.bars.strokeWidth = 1
        
        # Axis labels
        bc.categoryAxis.labels.fontName = 'Helvetica'
        bc.categoryAxis.labels.fontSize = 9
        bc.categoryAxis.labels.angle = 45
        bc.valueAxis.labels.fontName = 'Helvetica'
        bc.valueAxis.labels.fontSize = 9
        
        # Format value axis with German numbers
        bc.valueAxis.labelTextFormat = lambda x: self.format_german_number(x, 0)
        
        drawing.add(bc)
        
        # Add axis labels
        if x_label:
            drawing.add(String(width/2, 50, x_label, fontSize=10, textAnchor='middle'))
        if y_label:
            drawing.add(String(30, height/2, y_label, fontSize=10, textAnchor='middle'))
        
        return drawing

    
    def _generate_line_chart(
        self,
        data: Dict[str, Any],
        width: float,
        height: float,
        color_scheme: ColorScheme,
        enable_3d: bool,
        title: str,
        x_label: str,
        y_label: str,
        show_legend: bool,
        show_values: bool
    ) -> Drawing:
        """Generate line chart"""
        drawing = Drawing(width, height)
        
        # Add title
        if title:
            drawing.add(String(width/2, height-20, title, fontSize=14, textAnchor='middle', fontName='Helvetica-Bold'))
        
        # Create line chart
        lc = HorizontalLineChart()
        lc.x = 80
        lc.y = 80
        lc.width = width - 150
        lc.height = height - 150
        
        # Set data
        categories = data.get('categories', [])
        series_data = data.get('series', [])
        series_names = data.get('series_names', [])
        lc.data = series_data
        lc.categoryAxis.categoryNames = categories
        
        # Apply colors
        colors_list = self.color_schemes[color_scheme.value]
        for i, color in enumerate(colors_list):
            if i < len(series_data):
                lc.lines[i].strokeColor = color
                lc.lines[i].strokeWidth = 2
                if enable_3d:
                    lc.lines[i].strokeWidth = 3
        
        # Axis labels
        lc.categoryAxis.labels.fontName = 'Helvetica'
        lc.categoryAxis.labels.fontSize = 9
        lc.valueAxis.labels.fontName = 'Helvetica'
        lc.valueAxis.labels.fontSize = 9
        
        # Format value axis with German numbers
        lc.valueAxis.labelTextFormat = lambda x: self.format_german_number(x, 0)
        
        drawing.add(lc)
        
        # Add legend
        if show_legend and series_names:
            legend = self._create_legend(series_names, colors_list[:len(series_names)], width-150, height-100)
            drawing.add(legend)
        
        # Add axis labels
        if x_label:
            drawing.add(String(width/2, 50, x_label, fontSize=10, textAnchor='middle'))
        if y_label:
            drawing.add(String(30, height/2, y_label, fontSize=10, textAnchor='middle'))
        
        return drawing

    
    def _generate_area_chart(
        self,
        data: Dict[str, Any],
        width: float,
        height: float,
        color_scheme: ColorScheme,
        enable_3d: bool,
        title: str,
        x_label: str,
        y_label: str,
        show_legend: bool,
        show_values: bool
    ) -> Drawing:
        """Generate area chart (filled line chart)"""
        drawing = Drawing(width, height)
        
        # Add title
        if title:
            drawing.add(String(width/2, height-20, title, fontSize=14, textAnchor='middle', fontName='Helvetica-Bold'))
        
        # Get data
        categories = data.get('categories', [])
        series_data = data.get('series', [])
        series_names = data.get('series_names', [])
        
        # Calculate chart area
        chart_x = 80
        chart_y = 80
        chart_width = width - 150
        chart_height = height - 150
        
        # Find data range
        all_values = [val for series in series_data for val in series]
        min_val = min(all_values) if all_values else 0
        max_val = max(all_values) if all_values else 100
        value_range = max_val - min_val if max_val != min_val else 1
        
        # Apply colors
        colors_list = self.color_schemes[color_scheme.value]
        
        # Draw each series as filled area
        for series_idx, series in enumerate(series_data):
            if series_idx >= len(colors_list):
                break
            
            # Create polygon points for area
            points = []
            x_step = chart_width / (len(categories) - 1) if len(categories) > 1 else chart_width
            
            # Top line points
            for i, value in enumerate(series):
                x = chart_x + i * x_step
                y = chart_y + ((value - min_val) / value_range) * chart_height
                points.append((x, y))
            
            # Bottom line points (reverse order)
            for i in range(len(series) - 1, -1, -1):
                x = chart_x + i * x_step
                y = chart_y
                points.append((x, y))
            
            # Create filled polygon
            area = Polygon(points)
            area.fillColor = colors_list[series_idx]
            area.fillOpacity = 0.5 if not enable_3d else 0.7
            area.strokeColor = colors_list[series_idx]
            area.strokeWidth = 2
            drawing.add(area)
        
        # Add axis labels
        if x_label:
            drawing.add(String(width/2, 50, x_label, fontSize=10, textAnchor='middle'))
        if y_label:
            drawing.add(String(30, height/2, y_label, fontSize=10, textAnchor='middle'))
        
        # Add legend
        if show_legend and series_names:
            legend = self._create_legend(series_names, colors_list[:len(series_names)], width-150, height-100)
            drawing.add(legend)
        
        return drawing

    
    def _generate_circle_chart(
        self,
        data: Dict[str, Any],
        width: float,
        height: float,
        color_scheme: ColorScheme,
        title: str,
        show_values: bool
    ) -> Drawing:
        """Generate circle chart (progress/gauge chart)"""
        drawing = Drawing(width, height)
        
        # Add title
        if title:
            drawing.add(String(width/2, height-20, title, fontSize=14, textAnchor='middle', fontName='Helvetica-Bold'))
        
        # Get data
        value = data.get('value', 0)
        max_value = data.get('max_value', 100)
        label = data.get('label', '')
        
        # Calculate percentage
        percentage = (value / max_value) * 100 if max_value > 0 else 0
        
        # Draw circle
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 3
        
        # Background circle
        bg_circle = Circle(center_x, center_y, radius)
        bg_circle.fillColor = colors.lightgrey
        bg_circle.strokeColor = colors.grey
        bg_circle.strokeWidth = 2
        drawing.add(bg_circle)
        
        # Progress circle (as wedge)
        colors_list = self.color_schemes[color_scheme.value]
        angle = (percentage / 100) * 360
        
        if angle > 0:
            progress_wedge = Wedge(center_x, center_y, radius, 90, 90 - angle)
            progress_wedge.fillColor = colors_list[0]
            progress_wedge.strokeColor = colors.white
            progress_wedge.strokeWidth = 2
            drawing.add(progress_wedge)
        
        # Center text
        if show_values:
            value_text = self.format_german_number(value, 1)
            drawing.add(String(center_x, center_y + 10, value_text, 
                             fontSize=20, textAnchor='middle', fontName='Helvetica-Bold'))
            drawing.add(String(center_x, center_y - 10, label, 
                             fontSize=12, textAnchor='middle'))
        
        return drawing

    
    def _generate_polar_chart(
        self,
        data: Dict[str, Any],
        width: float,
        height: float,
        color_scheme: ColorScheme,
        title: str,
        show_legend: bool,
        show_values: bool
    ) -> Drawing:
        """Generate polar chart"""
        drawing = Drawing(width, height)
        
        # Add title
        if title:
            drawing.add(String(width/2, height-20, title, fontSize=14, textAnchor='middle', fontName='Helvetica-Bold'))
        
        # Get data
        categories = data.get('categories', [])
        values = data.get('values', [])
        
        # Calculate center and radius
        center_x = width / 2
        center_y = height / 2
        max_radius = min(width, height) / 3
        
        # Find max value for scaling
        max_value = max(values) if values else 1
        
        # Draw concentric circles (grid)
        for i in range(1, 5):
            r = max_radius * (i / 4)
            circle = Circle(center_x, center_y, r)
            circle.fillColor = None
            circle.strokeColor = colors.lightgrey
            circle.strokeWidth = 1
            drawing.add(circle)
        
        # Draw data as polygon
        if len(values) > 0:
            angle_step = 360 / len(values)
            points = []
            
            for i, value in enumerate(values):
                angle_rad = math.radians(90 - i * angle_step)
                radius = (value / max_value) * max_radius
                x = center_x + radius * math.cos(angle_rad)
                y = center_y + radius * math.sin(angle_rad)
                points.append((x, y))
            
            # Close the polygon
            if points:
                colors_list = self.color_schemes[color_scheme.value]
                polygon = Polygon(points)
                polygon.fillColor = colors_list[0]
                polygon.fillOpacity = 0.5
                polygon.strokeColor = colors_list[0]
                polygon.strokeWidth = 2
                drawing.add(polygon)
        
        # Draw axis lines and labels
        for i, category in enumerate(categories):
            angle_rad = math.radians(90 - i * angle_step)
            x_end = center_x + max_radius * math.cos(angle_rad)
            y_end = center_y + max_radius * math.sin(angle_rad)
            
            line = Line(center_x, center_y, x_end, y_end)
            line.strokeColor = colors.grey
            line.strokeWidth = 1
            drawing.add(line)
            
            # Add category label
            label_x = center_x + (max_radius + 20) * math.cos(angle_rad)
            label_y = center_y + (max_radius + 20) * math.sin(angle_rad)
            drawing.add(String(label_x, label_y, category, fontSize=9, textAnchor='middle'))
        
        return drawing

    
    def _generate_radar_chart(
        self,
        data: Dict[str, Any],
        width: float,
        height: float,
        color_scheme: ColorScheme,
        title: str,
        show_legend: bool,
        show_values: bool
    ) -> Drawing:
        """Generate radar chart (spider chart)"""
        drawing = Drawing(width, height)
        
        # Add title
        if title:
            drawing.add(String(width/2, height-20, title, fontSize=14, textAnchor='middle', fontName='Helvetica-Bold'))
        
        # Get data
        categories = data.get('categories', [])
        series_data = data.get('series', [])
        series_names = data.get('series_names', [])
        
        # Calculate center and radius
        center_x = width / 2
        center_y = height / 2
        max_radius = min(width, height) / 3
        
        # Find max value for scaling
        all_values = [val for series in series_data for val in series]
        max_value = max(all_values) if all_values else 1
        
        # Draw concentric circles (grid)
        for i in range(1, 6):
            r = max_radius * (i / 5)
            circle = Circle(center_x, center_y, r)
            circle.fillColor = None
            circle.strokeColor = colors.lightgrey
            circle.strokeWidth = 1
            drawing.add(circle)
        
        # Draw axis lines
        angle_step = 360 / len(categories) if categories else 360
        for i, category in enumerate(categories):
            angle_rad = math.radians(90 - i * angle_step)
            x_end = center_x + max_radius * math.cos(angle_rad)
            y_end = center_y + max_radius * math.sin(angle_rad)
            
            line = Line(center_x, center_y, x_end, y_end)
            line.strokeColor = colors.grey
            line.strokeWidth = 1
            drawing.add(line)
            
            # Add category label
            label_x = center_x + (max_radius + 20) * math.cos(angle_rad)
            label_y = center_y + (max_radius + 20) * math.sin(angle_rad)
            drawing.add(String(label_x, label_y, category, fontSize=9, textAnchor='middle'))
        
        # Draw data series
        colors_list = self.color_schemes[color_scheme.value]
        for series_idx, series in enumerate(series_data):
            if series_idx >= len(colors_list):
                break
            
            points = []
            for i, value in enumerate(series):
                angle_rad = math.radians(90 - i * angle_step)
                radius = (value / max_value) * max_radius
                x = center_x + radius * math.cos(angle_rad)
                y = center_y + radius * math.sin(angle_rad)
                points.append((x, y))
            
            if points:
                polygon = Polygon(points)
                polygon.fillColor = colors_list[series_idx]
                polygon.fillOpacity = 0.3
                polygon.strokeColor = colors_list[series_idx]
                polygon.strokeWidth = 2
                drawing.add(polygon)
        
        # Add legend
        if show_legend and series_names:
            legend = self._create_legend(series_names, colors_list[:len(series_names)], width-150, height-100)
            drawing.add(legend)
        
        return drawing

    
    def _generate_waterfall_chart(
        self,
        data: Dict[str, Any],
        width: float,
        height: float,
        color_scheme: ColorScheme,
        title: str,
        x_label: str,
        y_label: str,
        show_values: bool
    ) -> Drawing:
        """Generate waterfall chart"""
        drawing = Drawing(width, height)
        
        # Add title
        if title:
            drawing.add(String(width/2, height-20, title, fontSize=14, textAnchor='middle', fontName='Helvetica-Bold'))
        
        # Get data
        categories = data.get('categories', [])
        values = data.get('values', [])
        
        # Calculate chart area
        chart_x = 80
        chart_y = 80
        chart_width = width - 150
        chart_height = height - 150
        
        # Calculate cumulative values
        cumulative = 0
        cumulative_values = []
        for value in values:
            cumulative_values.append(cumulative)
            cumulative += value
        
        # Find range
        all_values = cumulative_values + [cumulative]
        min_val = min(all_values)
        max_val = max(all_values)
        value_range = max_val - min_val if max_val != min_val else 1
        
        # Colors
        colors_list = self.color_schemes[color_scheme.value]
        positive_color = colors_list[0]
        negative_color = colors_list[1] if len(colors_list) > 1 else colors.red
        
        # Draw bars
        bar_width = chart_width / (len(categories) + 1)
        for i, (category, value, cum_val) in enumerate(zip(categories, values, cumulative_values)):
            x = chart_x + i * bar_width
            
            # Calculate bar height and position
            if value >= 0:
                bar_bottom = chart_y + ((cum_val - min_val) / value_range) * chart_height
                bar_height = (value / value_range) * chart_height
                bar_color = positive_color
            else:
                bar_bottom = chart_y + ((cum_val + value - min_val) / value_range) * chart_height
                bar_height = (-value / value_range) * chart_height
                bar_color = negative_color
            
            # Draw bar
            bar = Rect(x, bar_bottom, bar_width * 0.8, bar_height)
            bar.fillColor = bar_color
            bar.strokeColor = colors.black
            bar.strokeWidth = 1
            drawing.add(bar)
            
            # Draw connector line to next bar
            if i < len(categories) - 1:
                next_cum = cumulative_values[i + 1]
                line_y = chart_y + ((cum_val + value - min_val) / value_range) * chart_height
                next_line_y = chart_y + ((next_cum - min_val) / value_range) * chart_height
                
                line = Line(x + bar_width * 0.8, line_y, x + bar_width, next_line_y)
                line.strokeColor = colors.grey
                line.strokeWidth = 1
                line.strokeDashArray = [3, 3]
                drawing.add(line)
            
            # Add value label
            if show_values:
                value_text = self.format_german_number(value, 0)
                label_y = bar_bottom + bar_height + 10 if value >= 0 else bar_bottom - 10
                drawing.add(String(x + bar_width * 0.4, label_y, value_text, 
                                 fontSize=8, textAnchor='middle'))
            
            # Add category label
            drawing.add(String(x + bar_width * 0.4, chart_y - 10, category, 
                             fontSize=9, textAnchor='middle'))
        
        # Add axis labels
        if x_label:
            drawing.add(String(width/2, 50, x_label, fontSize=10, textAnchor='middle'))
        if y_label:
            drawing.add(String(30, height/2, y_label, fontSize=10, textAnchor='middle'))
        
        return drawing

    
    def _create_legend(
        self,
        labels: List[str],
        colors_list: List[colors.Color],
        x: float,
        y: float
    ) -> Legend:
        """Create a legend for charts"""
        legend = Legend()
        legend.x = x
        legend.y = y
        legend.dx = 8
        legend.dy = 8
        legend.fontName = 'Helvetica'
        legend.fontSize = 9
        legend.boxAnchor = 'nw'
        legend.columnMaximum = 10
        legend.strokeWidth = 1
        legend.strokeColor = colors.black
        legend.deltax = 75
        legend.deltay = 10
        legend.autoXPadding = 5
        legend.yGap = 0
        legend.dxTextSpace = 5
        legend.alignment = 'right'
        legend.dividerLines = 1|2|4
        legend.dividerOffsY = 4.5
        legend.subCols.rpad = 30
        
        legend.colorNamePairs = [(colors_list[i], labels[i]) for i in range(len(labels))]
        
        return legend
    
    def generate_chart_pdf_bytes(
        self,
        chart_type: ChartType,
        data: Dict[str, Any],
        width: float = 400,
        height: float = 300,
        **kwargs
    ) -> bytes:
        """
        Generate chart and return as PDF bytes
        
        Args:
            chart_type: Type of chart
            data: Chart data
            width: Chart width
            height: Chart height
            **kwargs: Additional chart options
            
        Returns:
            PDF bytes
        """
        # Generate chart drawing
        drawing = self.generate_chart(chart_type, data, width, height, **kwargs)
        
        # Create PDF in memory
        buffer = io.BytesIO()
        pdf_canvas = canvas.Canvas(buffer, pagesize=A4)
        
        # Render drawing to PDF
        drawing.drawOn(pdf_canvas, 0, 0)
        pdf_canvas.save()
        
        # Get PDF bytes
        buffer.seek(0)
        return buffer.read()
    
    def position_chart_from_yml(
        self,
        pdf_canvas: canvas.Canvas,
        chart_drawing: Drawing,
        yml_coords: Dict[str, Any]
    ):
        """
        Position chart on PDF canvas using YML coordinates
        
        Args:
            pdf_canvas: ReportLab canvas
            chart_drawing: Chart drawing to position
            yml_coords: YML coordinates dict with x, y, width, height
        """
        x = yml_coords.get('x', 0)
        y = yml_coords.get('y', 0)
        
        # Draw chart at specified position
        chart_drawing.drawOn(pdf_canvas, x, y)
