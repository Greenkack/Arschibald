"""
Chart PDF Bytes Generation Service

This service provides comprehensive PDF byte generation for all chart types
with German number formatting applied automatically.

Requirements: 14.8
Task: 226
"""

import io
import base64
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from backend.core.pdf_bytes import (
    PDFByteMixin,
    PDFMetadata,
    PDFRenderingEngine,
    REPORTLAB_AVAILABLE
)
from backend.core.german_formatter import GermanNumberFormatter

if REPORTLAB_AVAILABLE:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.platypus import (
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        Image as RLImage
    )
    from reportlab.lib import colors
    from reportlab.graphics.shapes import Drawing, Rect, String, Line
    from reportlab.graphics.charts.linecharts import HorizontalLineChart
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.legends import Legend
    from reportlab.graphics.widgets.markers import makeMarker


class ChartData:
    """Container for chart data with German formatting support"""

    def __init__(
        self,
        title: str,
        data: List[List[float]],
        labels: List[str],
        series_names: Optional[List[str]] = None,
        x_axis_label: str = "",
        y_axis_label: str = "",
        colors: Optional[List[str]] = None
    ):
        self.title = title
        self.data = data
        self.labels = labels
        self.series_names = series_names or [f"Series {i+1}"
                                             for i in range(len(data))]
        self.x_axis_label = x_axis_label
        self.y_axis_label = y_axis_label
        self.colors = colors or self._default_colors()
        self.formatter = GermanNumberFormatter()

    def _default_colors(self) -> List[str]:
        """Get default color palette"""
        return [
            '#2E86AB',  # Blue
            '#A23B72',  # Purple
            '#F18F01',  # Orange
            '#C73E1D',  # Red
            '#6A994E',  # Green
            '#BC4B51',  # Dark Red
            '#8B8C89',  # Gray
            '#F4D35E',  # Yellow
        ]

    def format_value(self, value: float, decimals: int = 2) -> str:
        """Format a value in German format"""
        return self.formatter.format(value, decimals)

    def format_data_german(self) -> List[List[str]]:
        """Format all data values in German format"""
        return [
            [self.format_value(val) for val in series]
            for series in self.data
        ]


class ChartPDFService:
    """
    Service for generating PDF bytes from chart data.

    Supports:
    - Line charts
    - Bar charts
    - Pie charts
    - Area charts
    - Scatter plots

    All charts automatically apply German number formatting.
    """

    def __init__(self):
        self.engine = PDFRenderingEngine()
        self.formatter = GermanNumberFormatter()
        self.width = 400
        self.height = 250

    def _get_max_value(self, chart_data: ChartData) -> float:
        """Get maximum value from chart data, handling empty data"""
        try:
            max_val = max(max(series) for series in chart_data.data
                          if series)
            return max_val * 1.1
        except (ValueError, TypeError):
            return 100  # Default value for empty data

    def create_line_chart_pdf(
        self,
        chart_data: ChartData,
        metadata: Optional[PDFMetadata] = None
    ) -> bytes:
        """
        Generate PDF bytes for a line chart.

        Args:
            chart_data: Chart data container
            metadata: Optional PDF metadata

        Returns:
            bytes: PDF document as bytes
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab required for PDF generation")

        buffer = io.BytesIO()

        if metadata is None:
            metadata = PDFMetadata(
                title=f"Line Chart - {chart_data.title}",
                subject="Line Chart Visualization"
            )

        doc = self.engine.create_document(buffer, metadata)
        story = []

        # Add title
        story.append(self._create_title(chart_data.title))
        story.append(Spacer(1, 20))

        # Create line chart
        drawing = self._create_line_chart_drawing(chart_data)
        story.append(drawing)
        story.append(Spacer(1, 20))

        # Add data table
        story.append(self._create_data_table(chart_data))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def create_bar_chart_pdf(
        self,
        chart_data: ChartData,
        metadata: Optional[PDFMetadata] = None
    ) -> bytes:
        """
        Generate PDF bytes for a bar chart.

        Args:
            chart_data: Chart data container
            metadata: Optional PDF metadata

        Returns:
            bytes: PDF document as bytes
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab required for PDF generation")

        buffer = io.BytesIO()

        if metadata is None:
            metadata = PDFMetadata(
                title=f"Bar Chart - {chart_data.title}",
                subject="Bar Chart Visualization"
            )

        doc = self.engine.create_document(buffer, metadata)
        story = []

        # Add title
        story.append(self._create_title(chart_data.title))
        story.append(Spacer(1, 20))

        # Create bar chart
        drawing = self._create_bar_chart_drawing(chart_data)
        story.append(drawing)
        story.append(Spacer(1, 20))

        # Add data table
        story.append(self._create_data_table(chart_data))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def create_pie_chart_pdf(
        self,
        chart_data: ChartData,
        metadata: Optional[PDFMetadata] = None
    ) -> bytes:
        """
        Generate PDF bytes for a pie chart.

        Args:
            chart_data: Chart data container (uses first series only)
            metadata: Optional PDF metadata

        Returns:
            bytes: PDF document as bytes
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab required for PDF generation")

        buffer = io.BytesIO()

        if metadata is None:
            metadata = PDFMetadata(
                title=f"Pie Chart - {chart_data.title}",
                subject="Pie Chart Visualization"
            )

        doc = self.engine.create_document(buffer, metadata)
        story = []

        # Add title
        story.append(self._create_title(chart_data.title))
        story.append(Spacer(1, 20))

        # Create pie chart
        drawing = self._create_pie_chart_drawing(chart_data)
        story.append(drawing)
        story.append(Spacer(1, 20))

        # Add data table
        story.append(self._create_pie_data_table(chart_data))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def create_area_chart_pdf(
        self,
        chart_data: ChartData,
        metadata: Optional[PDFMetadata] = None
    ) -> bytes:
        """
        Generate PDF bytes for an area chart.

        Args:
            chart_data: Chart data container
            metadata: Optional PDF metadata

        Returns:
            bytes: PDF document as bytes
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab required for PDF generation")

        buffer = io.BytesIO()

        if metadata is None:
            metadata = PDFMetadata(
                title=f"Area Chart - {chart_data.title}",
                subject="Area Chart Visualization"
            )

        doc = self.engine.create_document(buffer, metadata)
        story = []

        # Add title
        story.append(self._create_title(chart_data.title))
        story.append(Spacer(1, 20))

        # Create area chart (similar to line chart with fill)
        drawing = self._create_area_chart_drawing(chart_data)
        story.append(drawing)
        story.append(Spacer(1, 20))

        # Add data table
        story.append(self._create_data_table(chart_data))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def create_scatter_plot_pdf(
        self,
        chart_data: ChartData,
        metadata: Optional[PDFMetadata] = None
    ) -> bytes:
        """
        Generate PDF bytes for a scatter plot.

        Args:
            chart_data: Chart data container
            metadata: Optional PDF metadata

        Returns:
            bytes: PDF document as bytes
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab required for PDF generation")

        buffer = io.BytesIO()

        if metadata is None:
            metadata = PDFMetadata(
                title=f"Scatter Plot - {chart_data.title}",
                subject="Scatter Plot Visualization"
            )

        doc = self.engine.create_document(buffer, metadata)
        story = []

        # Add title
        story.append(self._create_title(chart_data.title))
        story.append(Spacer(1, 20))

        # Create scatter plot
        drawing = self._create_scatter_plot_drawing(chart_data)
        story.append(drawing)
        story.append(Spacer(1, 20))

        # Add data table
        story.append(self._create_data_table(chart_data))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _create_title(self, title: str) -> Paragraph:
        """Create formatted title paragraph"""
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'ChartTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=10,
            alignment=TA_CENTER
        )
        return Paragraph(title, title_style)

    def _create_line_chart_drawing(
        self,
        chart_data: ChartData
    ) -> Drawing:
        """Create line chart drawing"""
        drawing = Drawing(self.width, self.height)

        chart = HorizontalLineChart()
        chart.x = 50
        chart.y = 50
        chart.width = self.width - 100
        chart.height = self.height - 100

        # Set data
        chart.data = chart_data.data

        # Configure axes
        chart.categoryAxis.categoryNames = chart_data.labels
        chart.categoryAxis.labels.boxAnchor = 'n'
        chart.categoryAxis.labels.angle = 45
        chart.categoryAxis.labels.fontSize = 8

        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = self._get_max_value(chart_data)
        chart.valueAxis.labels.fontSize = 8

        # Format value axis labels in German
        chart.valueAxis.labelTextFormat = lambda x: self.formatter.format(
            x, 0
        )

        # Set colors
        for i, color in enumerate(chart_data.colors[:len(chart_data.data)]):
            chart.lines[i].strokeColor = colors.HexColor(color)
            chart.lines[i].strokeWidth = 2

        # Add legend
        legend = self._create_legend(chart_data)
        legend.x = 50
        legend.y = self.height - 30

        drawing.add(chart)
        drawing.add(legend)

        return drawing

    def _create_bar_chart_drawing(
        self,
        chart_data: ChartData
    ) -> Drawing:
        """Create bar chart drawing"""
        drawing = Drawing(self.width, self.height)

        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 50
        chart.width = self.width - 100
        chart.height = self.height - 100

        # Set data
        chart.data = chart_data.data

        # Configure axes
        chart.categoryAxis.categoryNames = chart_data.labels
        chart.categoryAxis.labels.boxAnchor = 'n'
        chart.categoryAxis.labels.angle = 45
        chart.categoryAxis.labels.fontSize = 8

        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = self._get_max_value(chart_data)
        chart.valueAxis.labels.fontSize = 8

        # Format value axis labels in German
        chart.valueAxis.labelTextFormat = lambda x: self.formatter.format(
            x, 0
        )

        # Set colors
        for i, color in enumerate(chart_data.colors[:len(chart_data.data)]):
            chart.bars[i].fillColor = colors.HexColor(color)

        # Add legend
        legend = self._create_legend(chart_data)
        legend.x = 50
        legend.y = self.height - 30

        drawing.add(chart)
        drawing.add(legend)

        return drawing

    def _create_pie_chart_drawing(
        self,
        chart_data: ChartData
    ) -> Drawing:
        """Create pie chart drawing"""
        drawing = Drawing(self.width, self.height)

        # Use first series only for pie chart
        data = chart_data.data[0] if chart_data.data else []

        pie = Pie()
        pie.x = 100
        pie.y = 50
        pie.width = 150
        pie.height = 150
        pie.data = data
        pie.labels = chart_data.labels

        # Set colors
        for i, color in enumerate(chart_data.colors[:len(data)]):
            pie.slices[i].fillColor = colors.HexColor(color)

        # Format labels with German numbers
        pie.slices.labelRadius = 1.2
        pie.slices.fontSize = 8

        # Add legend with German-formatted values
        legend = Legend()
        legend.x = 280
        legend.y = 150
        legend.dx = 8
        legend.dy = 8
        legend.fontName = 'Helvetica'
        legend.fontSize = 8
        legend.boxAnchor = 'w'
        legend.columnMaximum = 10
        legend.strokeWidth = 0
        legend.strokeColor = colors.white
        legend.deltax = 75
        legend.deltay = 10
        legend.autoXPadding = 5
        legend.yGap = 0
        legend.dxTextSpace = 5
        legend.alignment = 'right'
        legend.dividerLines = 1 | 2 | 4
        legend.dividerOffsY = 4.5
        legend.subCols.rpad = 30

        # Set legend colors and labels with German formatting
        legend.colorNamePairs = [
            (colors.HexColor(chart_data.colors[i]),
             f"{label}: {self.formatter.format(val)}")
            for i, (label, val) in enumerate(zip(chart_data.labels, data))
        ]

        drawing.add(pie)
        drawing.add(legend)

        return drawing

    def _create_area_chart_drawing(
        self,
        chart_data: ChartData
    ) -> Drawing:
        """Create area chart drawing (line chart with filled area)"""
        drawing = Drawing(self.width, self.height)

        chart = HorizontalLineChart()
        chart.x = 50
        chart.y = 50
        chart.width = self.width - 100
        chart.height = self.height - 100

        # Set data
        chart.data = chart_data.data

        # Configure axes
        chart.categoryAxis.categoryNames = chart_data.labels
        chart.categoryAxis.labels.boxAnchor = 'n'
        chart.categoryAxis.labels.angle = 45
        chart.categoryAxis.labels.fontSize = 8

        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = self._get_max_value(chart_data)
        chart.valueAxis.labels.fontSize = 8

        # Format value axis labels in German
        chart.valueAxis.labelTextFormat = lambda x: self.formatter.format(
            x, 0
        )

        # Set colors and fill
        for i, color in enumerate(chart_data.colors[:len(chart_data.data)]):
            chart.lines[i].strokeColor = colors.HexColor(color)
            chart.lines[i].strokeWidth = 2
            # Enable area fill
            chart.lines[i].fillColor = colors.HexColor(color)
            chart.lines[i].fillColor.alpha = 0.3

        # Add legend
        legend = self._create_legend(chart_data)
        legend.x = 50
        legend.y = self.height - 30

        drawing.add(chart)
        drawing.add(legend)

        return drawing

    def _create_scatter_plot_drawing(
        self,
        chart_data: ChartData
    ) -> Drawing:
        """Create scatter plot drawing"""
        drawing = Drawing(self.width, self.height)

        chart = HorizontalLineChart()
        chart.x = 50
        chart.y = 50
        chart.width = self.width - 100
        chart.height = self.height - 100

        # Set data
        chart.data = chart_data.data

        # Configure axes
        chart.categoryAxis.categoryNames = chart_data.labels
        chart.categoryAxis.labels.boxAnchor = 'n'
        chart.categoryAxis.labels.angle = 45
        chart.categoryAxis.labels.fontSize = 8

        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = self._get_max_value(chart_data)
        chart.valueAxis.labels.fontSize = 8

        # Format value axis labels in German
        chart.valueAxis.labelTextFormat = lambda x: self.formatter.format(
            x, 0
        )

        # Configure as scatter plot (no lines, only markers)
        for i, color in enumerate(chart_data.colors[:len(chart_data.data)]):
            chart.lines[i].strokeColor = None  # No lines
            chart.lines[i].symbol = makeMarker('Circle')
            chart.lines[i].symbol.size = 5
            chart.lines[i].symbol.fillColor = colors.HexColor(color)

        # Add legend
        legend = self._create_legend(chart_data)
        legend.x = 50
        legend.y = self.height - 30

        drawing.add(chart)
        drawing.add(legend)

        return drawing

    def _create_legend(self, chart_data: ChartData) -> Legend:
        """Create legend for chart"""
        legend = Legend()
        legend.fontName = 'Helvetica'
        legend.fontSize = 8
        legend.boxAnchor = 'sw'
        legend.columnMaximum = 1
        legend.strokeWidth = 0
        legend.strokeColor = colors.white
        legend.deltax = 75
        legend.deltay = 10
        legend.autoXPadding = 5
        legend.yGap = 0
        legend.dxTextSpace = 5
        legend.alignment = 'right'

        # Set legend colors and labels
        legend.colorNamePairs = [
            (colors.HexColor(chart_data.colors[i]), name)
            for i, name in enumerate(chart_data.series_names)
        ]

        return legend

    def _create_data_table(self, chart_data: ChartData) -> Table:
        """Create data table with German-formatted numbers"""
        # Header row
        header = [''] + chart_data.series_names

        # Data rows
        rows = [header]
        for i, label in enumerate(chart_data.labels):
            row = [label]
            for series in chart_data.data:
                if i < len(series):
                    row.append(self.formatter.format(series[i]))
                else:
                    row.append('-')
            rows.append(row)

        # Create table
        table = Table(rows)

        # Style
        style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]

        table.setStyle(TableStyle(style))
        return table

    def _create_pie_data_table(self, chart_data: ChartData) -> Table:
        """Create data table for pie chart with German-formatted numbers"""
        # Use first series only
        data = chart_data.data[0] if chart_data.data else []

        # Calculate total and percentages
        total = sum(data)

        # Header row
        rows = [['Category', 'Value', 'Percentage']]

        # Data rows
        for label, value in zip(chart_data.labels, data):
            percentage = (value / total * 100) if total > 0 else 0
            rows.append([
                label,
                self.formatter.format(value),
                self.formatter.format_percent(percentage / 100)
            ])

        # Total row
        rows.append([
            'Total',
            self.formatter.format(total),
            '100,00 %'
        ])

        # Create table
        table = Table(rows)

        # Style
        style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]

        table.setStyle(TableStyle(style))
        return table


# Convenience functions

def create_line_chart_pdf(
    title: str,
    data: List[List[float]],
    labels: List[str],
    series_names: Optional[List[str]] = None,
    **kwargs
) -> bytes:
    """
    Convenience function to create line chart PDF.

    Args:
        title: Chart title
        data: List of data series
        labels: Category labels
        series_names: Optional series names
        **kwargs: Additional ChartData parameters

    Returns:
        bytes: PDF document as bytes
    """
    chart_data = ChartData(
        title=title,
        data=data,
        labels=labels,
        series_names=series_names,
        **kwargs
    )
    service = ChartPDFService()
    return service.create_line_chart_pdf(chart_data)


def create_bar_chart_pdf(
    title: str,
    data: List[List[float]],
    labels: List[str],
    series_names: Optional[List[str]] = None,
    **kwargs
) -> bytes:
    """
    Convenience function to create bar chart PDF.

    Args:
        title: Chart title
        data: List of data series
        labels: Category labels
        series_names: Optional series names
        **kwargs: Additional ChartData parameters

    Returns:
        bytes: PDF document as bytes
    """
    chart_data = ChartData(
        title=title,
        data=data,
        labels=labels,
        series_names=series_names,
        **kwargs
    )
    service = ChartPDFService()
    return service.create_bar_chart_pdf(chart_data)


def create_pie_chart_pdf(
    title: str,
    data: List[float],
    labels: List[str],
    **kwargs
) -> bytes:
    """
    Convenience function to create pie chart PDF.

    Args:
        title: Chart title
        data: Data values (single series)
        labels: Category labels
        **kwargs: Additional ChartData parameters

    Returns:
        bytes: PDF document as bytes
    """
    chart_data = ChartData(
        title=title,
        data=[data],  # Wrap in list for single series
        labels=labels,
        **kwargs
    )
    service = ChartPDFService()
    return service.create_pie_chart_pdf(chart_data)


def create_area_chart_pdf(
    title: str,
    data: List[List[float]],
    labels: List[str],
    series_names: Optional[List[str]] = None,
    **kwargs
) -> bytes:
    """
    Convenience function to create area chart PDF.

    Args:
        title: Chart title
        data: List of data series
        labels: Category labels
        series_names: Optional series names
        **kwargs: Additional ChartData parameters

    Returns:
        bytes: PDF document as bytes
    """
    chart_data = ChartData(
        title=title,
        data=data,
        labels=labels,
        series_names=series_names,
        **kwargs
    )
    service = ChartPDFService()
    return service.create_area_chart_pdf(chart_data)


def create_scatter_plot_pdf(
    title: str,
    data: List[List[float]],
    labels: List[str],
    series_names: Optional[List[str]] = None,
    **kwargs
) -> bytes:
    """
    Convenience function to create scatter plot PDF.

    Args:
        title: Chart title
        data: List of data series
        labels: Category labels
        series_names: Optional series names
        **kwargs: Additional ChartData parameters

    Returns:
        bytes: PDF document as bytes
    """
    chart_data = ChartData(
        title=title,
        data=data,
        labels=labels,
        series_names=series_names,
        **kwargs
    )
    service = ChartPDFService()
    return service.create_scatter_plot_pdf(chart_data)
