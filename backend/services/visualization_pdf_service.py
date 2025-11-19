"""
Visualization PDF Bytes Service

This service generates PDF bytes for various visualization types:
- 3D visualizations (solar panel layouts, building models)
- Diagrams (system architecture, flow diagrams)
- Flowcharts (process flows, decision trees)
- Infographics (statistics, comparisons)
- Dashboards (multi-chart layouts, KPI displays)

All visualizations are rendered with German number formatting (1.234,56)
and include dynamic keys for tracking and retrieval.
"""

import io
import base64
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, FancyArrowPatch
from matplotlib.collections import PatchCollection
import numpy as np
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
from PIL import Image, ImageDraw, ImageFont

from backend.core.german_formatter import GermanNumberFormatter
from backend.core.dynamic_keys import DynamicKeyMixin, KeyPrefix


class VisualizationPDFService:
    """Service for generating PDF bytes from various visualization types"""
    
    def __init__(self):
        self.formatter = GermanNumberFormatter()
        self.key_mixin = DynamicKeyMixin()
        self.default_dpi = 300
        self.default_figsize = (10, 8)
    
    # ==================== 3D Visualization PDF Export ====================
    
    def create_3d_visualization_pdf(
        self,
        visualization_data: Dict[str, Any],
        title: str = "3D Visualization",
        include_metadata: bool = True
    ) -> bytes:
        """
        Create PDF from 3D visualization data (solar panels, building models, etc.)
        
        Args:
            visualization_data: Dict containing 3D model data, views, and metadata
            title: Title for the PDF document
            include_metadata: Whether to include metadata page
            
        Returns:
            PDF bytes
        """
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Generate dynamic key
        dynamic_key = self.key_mixin.generate_dynamic_key(KeyPrefix.VISUALIZATION_3D)
        
        # Title page
        pdf.setFont("Helvetica-Bold", 24)
        pdf.drawCentredString(width / 2, height - 50, title)
        
        pdf.setFont("Helvetica", 10)
        pdf.drawCentredString(width / 2, height - 70, f"Generated: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        pdf.drawCentredString(width / 2, height - 85, f"Key: {dynamic_key}")
        
        y_position = height - 120
        
        # Render 3D views if available
        if 'views' in visualization_data:
            for view_name, view_data in visualization_data['views'].items():
                if y_position < 150:
                    pdf.showPage()
                    y_position = height - 50
                
                # View title
                pdf.setFont("Helvetica-Bold", 14)
                pdf.drawString(50, y_position, f"{view_name.title()} View")
                y_position -= 25
                
                # Render view image
                if 'image' in view_data:
                    img_bytes = self._render_3d_view_image(view_data)
                    img_reader = ImageReader(io.BytesIO(img_bytes))
                    pdf.drawImage(img_reader, 50, y_position - 300, width=500, height=300)
                    y_position -= 320
                
                # View statistics
                if 'stats' in view_data:
                    pdf.setFont("Helvetica", 10)
                    for key, value in view_data['stats'].items():
                        formatted_value = self._format_value(value)
                        pdf.drawString(70, y_position, f"{key}: {formatted_value}")
                        y_position -= 15
                
                y_position -= 20
        
        # Module placement details
        if 'modules' in visualization_data:
            if y_position < 200:
                pdf.showPage()
                y_position = height - 50
            
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(50, y_position, "Module Placement Details")
            y_position -= 25
            
            modules = visualization_data['modules']
            pdf.setFont("Helvetica", 10)
            pdf.drawString(70, y_position, f"Total Modules: {len(modules)}")
            y_position -= 15
            
            if 'total_power' in visualization_data:
                power_formatted = self.formatter.format(visualization_data['total_power'], decimal_places=2)
                pdf.drawString(70, y_position, f"Total Power: {power_formatted} kWp")
                y_position -= 15
            
            if 'area_coverage' in visualization_data:
                area_formatted = self.formatter.format(visualization_data['area_coverage'], decimal_places=2)
                pdf.drawString(70, y_position, f"Area Coverage: {area_formatted} m²")
                y_position -= 15
        
        # Metadata page
        if include_metadata and 'metadata' in visualization_data:
            pdf.showPage()
            self._add_metadata_page(pdf, visualization_data['metadata'], dynamic_key)
        
        pdf.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    def _render_3d_view_image(self, view_data: Dict[str, Any]) -> bytes:
        """Render a 3D view to image bytes"""
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Extract coordinates
        if 'vertices' in view_data and 'faces' in view_data:
            vertices = np.array(view_data['vertices'])
            faces = view_data['faces']
            
            # Plot 3D surface
            from mpl_toolkits.mplot3d.art3d import Poly3DCollection
            poly = Poly3DCollection(faces, alpha=0.7, facecolor='skyblue', edgecolor='black')
            ax.add_collection3d(poly)
            
            # Set limits
            ax.set_xlim(vertices[:, 0].min(), vertices[:, 0].max())
            ax.set_ylim(vertices[:, 1].min(), vertices[:, 1].max())
            ax.set_zlim(vertices[:, 2].min(), vertices[:, 2].max())
        
        # Labels
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        
        if 'title' in view_data:
            ax.set_title(view_data['title'])
        
        # Save to bytes
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=self.default_dpi, bbox_inches='tight')
        buffer.seek(0)
        plt.close(fig)
        
        return buffer.getvalue()
    
    # ==================== Diagram PDF Generation ====================
    
    def create_diagram_pdf(
        self,
        diagram_data: Dict[str, Any],
        diagram_type: str = "system",
        title: str = "System Diagram"
    ) -> bytes:
        """
        Create PDF from diagram data (system architecture, component diagrams)
        
        Args:
            diagram_data: Dict containing nodes, edges, and layout information
            diagram_type: Type of diagram (system, component, network, etc.)
            title: Title for the diagram
            
        Returns:
            PDF bytes
        """
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=landscape(A4))
        width, height = landscape(A4)
        
        # Generate dynamic key
        dynamic_key = self.key_mixin.generate_dynamic_key(KeyPrefix.CHART)
        
        # Title
        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawCentredString(width / 2, height - 40, title)
        pdf.setFont("Helvetica", 9)
        pdf.drawCentredString(width / 2, height - 55, f"Key: {dynamic_key}")
        
        # Render diagram
        diagram_img = self._render_diagram(diagram_data, diagram_type)
        img_reader = ImageReader(io.BytesIO(diagram_img))
        
        # Center the diagram
        img_width = width - 100
        img_height = height - 150
        pdf.drawImage(img_reader, 50, 50, width=img_width, height=img_height, preserveAspectRatio=True)
        
        # Legend if available
        if 'legend' in diagram_data:
            self._add_diagram_legend(pdf, diagram_data['legend'], width, height)
        
        pdf.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    def _render_diagram(self, diagram_data: Dict[str, Any], diagram_type: str) -> bytes:
        """Render diagram to image bytes using matplotlib"""
        fig, ax = plt.subplots(figsize=(14, 10))
        ax.set_aspect('equal')
        ax.axis('off')
        
        nodes = diagram_data.get('nodes', [])
        edges = diagram_data.get('edges', [])
        
        # Draw edges first (so they appear behind nodes)
        for edge in edges:
            start = edge['from']
            end = edge['to']
            
            # Find node positions
            start_node = next((n for n in nodes if n['id'] == start), None)
            end_node = next((n for n in nodes if n['id'] == end), None)
            
            if start_node and end_node:
                arrow = FancyArrowPatch(
                    (start_node['x'], start_node['y']),
                    (end_node['x'], end_node['y']),
                    arrowstyle='->', mutation_scale=20, linewidth=2,
                    color=edge.get('color', 'gray'), alpha=0.7
                )
                ax.add_patch(arrow)
                
                # Edge label
                if 'label' in edge:
                    mid_x = (start_node['x'] + end_node['x']) / 2
                    mid_y = (start_node['y'] + end_node['y']) / 2
                    ax.text(mid_x, mid_y, edge['label'], fontsize=8, ha='center',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        # Draw nodes
        for node in nodes:
            x, y = node['x'], node['y']
            width = node.get('width', 1.5)
            height = node.get('height', 1.0)
            color = node.get('color', 'lightblue')
            shape = node.get('shape', 'rectangle')
            
            if shape == 'rectangle':
                box = FancyBboxPatch(
                    (x - width/2, y - height/2), width, height,
                    boxstyle="round,pad=0.1", facecolor=color,
                    edgecolor='black', linewidth=2
                )
                ax.add_patch(box)
            elif shape == 'circle':
                circle = Circle((x, y), width/2, facecolor=color, edgecolor='black', linewidth=2)
                ax.add_patch(circle)
            
            # Node label
            label = node.get('label', '')
            ax.text(x, y, label, fontsize=10, ha='center', va='center', weight='bold')
            
            # Node value (if numeric, format with German formatting)
            if 'value' in node:
                formatted_value = self._format_value(node['value'])
                ax.text(x, y - height/3, formatted_value, fontsize=8, ha='center', va='center')
        
        # Set limits with padding
        if nodes:
            x_coords = [n['x'] for n in nodes]
            y_coords = [n['y'] for n in nodes]
            padding = 2
            ax.set_xlim(min(x_coords) - padding, max(x_coords) + padding)
            ax.set_ylim(min(y_coords) - padding, max(y_coords) + padding)
        
        # Save to bytes
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=self.default_dpi, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        plt.close(fig)
        
        return buffer.getvalue()
    
    # ==================== Flowchart PDF Export ====================
    
    def create_flowchart_pdf(
        self,
        flowchart_data: Dict[str, Any],
        title: str = "Process Flowchart"
    ) -> bytes:
        """
        Create PDF from flowchart data (process flows, decision trees)
        
        Args:
            flowchart_data: Dict containing steps, decisions, and flow connections
            title: Title for the flowchart
            
        Returns:
            PDF bytes
        """
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Generate dynamic key
        dynamic_key = self.key_mixin.generate_dynamic_key(KeyPrefix.CHART)
        
        # Title
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawCentredString(width / 2, height - 40, title)
        pdf.setFont("Helvetica", 9)
        pdf.drawCentredString(width / 2, height - 55, f"Key: {dynamic_key}")
        
        # Render flowchart
        flowchart_img = self._render_flowchart(flowchart_data)
        img_reader = ImageReader(io.BytesIO(flowchart_img))
        
        # Add flowchart image
        img_width = width - 80
        img_height = height - 120
        pdf.drawImage(img_reader, 40, 40, width=img_width, height=img_height, preserveAspectRatio=True)
        
        pdf.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    def _render_flowchart(self, flowchart_data: Dict[str, Any]) -> bytes:
        """Render flowchart to image bytes"""
        fig, ax = plt.subplots(figsize=(10, 14))
        ax.set_aspect('equal')
        ax.axis('off')
        
        steps = flowchart_data.get('steps', [])
        connections = flowchart_data.get('connections', [])
        
        # Draw connections
        for conn in connections:
            start_step = next((s for s in steps if s['id'] == conn['from']), None)
            end_step = next((s for s in steps if s['id'] == conn['to']), None)
            
            if start_step and end_step:
                arrow = FancyArrowPatch(
                    (start_step['x'], start_step['y'] - 0.5),
                    (end_step['x'], end_step['y'] + 0.5),
                    arrowstyle='->', mutation_scale=25, linewidth=2.5,
                    color='darkblue', alpha=0.7
                )
                ax.add_patch(arrow)
                
                # Connection label (e.g., "Yes", "No")
                if 'label' in conn:
                    mid_x = (start_step['x'] + end_step['x']) / 2
                    mid_y = (start_step['y'] + end_step['y']) / 2
                    ax.text(mid_x + 0.3, mid_y, conn['label'], fontsize=9, 
                           style='italic', color='darkblue')
        
        # Draw steps
        for step in steps:
            x, y = step['x'], step['y']
            step_type = step.get('type', 'process')
            label = step.get('label', '')
            
            if step_type == 'start' or step_type == 'end':
                # Rounded rectangle for start/end
                box = FancyBboxPatch(
                    (x - 1.2, y - 0.4), 2.4, 0.8,
                    boxstyle="round,pad=0.15", facecolor='lightgreen' if step_type == 'start' else 'lightcoral',
                    edgecolor='black', linewidth=2
                )
                ax.add_patch(box)
            elif step_type == 'decision':
                # Diamond for decision
                diamond_points = [
                    [x, y + 0.6], [x + 1.0, y], [x, y - 0.6], [x - 1.0, y]
                ]
                diamond = plt.Polygon(diamond_points, facecolor='lightyellow', 
                                     edgecolor='black', linewidth=2)
                ax.add_patch(diamond)
            else:
                # Rectangle for process
                box = Rectangle((x - 1.0, y - 0.4), 2.0, 0.8, 
                               facecolor='lightblue', edgecolor='black', linewidth=2)
                ax.add_patch(box)
            
            # Step label (wrap text if too long)
            wrapped_label = self._wrap_text(label, 20)
            ax.text(x, y, wrapped_label, fontsize=9, ha='center', va='center', weight='bold')
        
        # Set limits
        if steps:
            x_coords = [s['x'] for s in steps]
            y_coords = [s['y'] for s in steps]
            padding = 2
            ax.set_xlim(min(x_coords) - padding, max(x_coords) + padding)
            ax.set_ylim(min(y_coords) - padding, max(y_coords) + padding)
        
        # Save to bytes
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=self.default_dpi, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        plt.close(fig)
        
        return buffer.getvalue()
    
    # ==================== Infographic PDF Generation ====================
    
    def create_infographic_pdf(
        self,
        infographic_data: Dict[str, Any],
        title: str = "Infographic"
    ) -> bytes:
        """
        Create PDF from infographic data (statistics, comparisons, visual data)
        
        Args:
            infographic_data: Dict containing sections, charts, icons, and text
            title: Title for the infographic
            
        Returns:
            PDF bytes
        """
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Generate dynamic key
        dynamic_key = self.key_mixin.generate_dynamic_key(KeyPrefix.CHART)
        
        # Header with title
        pdf.setFillColorRGB(0.2, 0.4, 0.8)
        pdf.rect(0, height - 80, width, 80, fill=True, stroke=False)
        
        pdf.setFillColorRGB(1, 1, 1)
        pdf.setFont("Helvetica-Bold", 24)
        pdf.drawCentredString(width / 2, height - 45, title)
        pdf.setFont("Helvetica", 9)
        pdf.drawCentredString(width / 2, height - 65, f"Key: {dynamic_key}")
        
        pdf.setFillColorRGB(0, 0, 0)  # Reset to black
        
        y_position = height - 100
        
        # Render sections
        sections = infographic_data.get('sections', [])
        for section in sections:
            if y_position < 100:
                pdf.showPage()
                y_position = height - 50
            
            section_type = section.get('type', 'text')
            
            if section_type == 'stat_box':
                y_position = self._add_stat_box(pdf, section, y_position, width)
            elif section_type == 'comparison':
                y_position = self._add_comparison(pdf, section, y_position, width)
            elif section_type == 'chart':
                y_position = self._add_infographic_chart(pdf, section, y_position, width)
            elif section_type == 'text':
                y_position = self._add_text_section(pdf, section, y_position, width)
            
            y_position -= 20  # Spacing between sections
        
        pdf.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    def _add_stat_box(self, pdf: canvas.Canvas, section: Dict[str, Any], 
                      y_position: float, page_width: float) -> float:
        """Add a statistics box to the infographic"""
        stats = section.get('stats', [])
        box_height = 80
        box_width = (page_width - 100) / len(stats)
        
        for i, stat in enumerate(stats):
            x = 50 + i * box_width
            
            # Draw box
            pdf.setFillColorRGB(0.9, 0.95, 1.0)
            pdf.setStrokeColorRGB(0.2, 0.4, 0.8)
            pdf.setLineWidth(2)
            pdf.rect(x, y_position - box_height, box_width - 10, box_height, fill=True, stroke=True)
            
            # Value
            pdf.setFillColorRGB(0.2, 0.4, 0.8)
            pdf.setFont("Helvetica-Bold", 28)
            value_formatted = self._format_value(stat.get('value', 0))
            pdf.drawCentredString(x + box_width/2 - 5, y_position - 35, value_formatted)
            
            # Label
            pdf.setFillColorRGB(0, 0, 0)
            pdf.setFont("Helvetica", 11)
            label = stat.get('label', '')
            pdf.drawCentredString(x + box_width/2 - 5, y_position - 55, label)
            
            # Unit
            if 'unit' in stat:
                pdf.setFont("Helvetica", 9)
                pdf.drawCentredString(x + box_width/2 - 5, y_position - 70, stat['unit'])
        
        return y_position - box_height - 10
    
    def _add_comparison(self, pdf: canvas.Canvas, section: Dict[str, Any],
                       y_position: float, page_width: float) -> float:
        """Add a comparison section to the infographic"""
        items = section.get('items', [])
        
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(60, y_position, section.get('title', 'Comparison'))
        y_position -= 25
        
        for item in items:
            # Item name
            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawString(70, y_position, item.get('name', ''))
            
            # Progress bar
            value = item.get('value', 0)
            max_value = item.get('max', 100)
            bar_width = 300
            bar_height = 15
            progress = (value / max_value) * bar_width if max_value > 0 else 0
            
            # Background bar
            pdf.setFillColorRGB(0.9, 0.9, 0.9)
            pdf.rect(250, y_position - 5, bar_width, bar_height, fill=True, stroke=False)
            
            # Progress bar
            pdf.setFillColorRGB(0.2, 0.7, 0.3)
            pdf.rect(250, y_position - 5, progress, bar_height, fill=True, stroke=False)
            
            # Value label
            pdf.setFillColorRGB(0, 0, 0)
            pdf.setFont("Helvetica", 10)
            value_formatted = self._format_value(value)
            pdf.drawString(560, y_position, value_formatted)
            
            y_position -= 25
        
        return y_position
    
    def _add_infographic_chart(self, pdf: canvas.Canvas, section: Dict[str, Any],
                               y_position: float, page_width: float) -> float:
        """Add a chart to the infographic"""
        chart_type = section.get('chart_type', 'bar')
        chart_data = section.get('data', {})
        
        # Generate chart image
        chart_img = self._generate_mini_chart(chart_data, chart_type)
        img_reader = ImageReader(io.BytesIO(chart_img))
        
        # Add chart
        chart_height = 200
        pdf.drawImage(img_reader, 60, y_position - chart_height, 
                     width=page_width - 120, height=chart_height, preserveAspectRatio=True)
        
        return y_position - chart_height - 10
    
    def _add_text_section(self, pdf: canvas.Canvas, section: Dict[str, Any],
                         y_position: float, page_width: float) -> float:
        """Add a text section to the infographic"""
        title = section.get('title', '')
        text = section.get('text', '')
        
        if title:
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(60, y_position, title)
            y_position -= 20
        
        # Wrap and draw text
        pdf.setFont("Helvetica", 10)
        max_width = page_width - 120
        lines = self._wrap_text_to_width(text, max_width, pdf)
        
        for line in lines:
            pdf.drawString(70, y_position, line)
            y_position -= 15
        
        return y_position
    
    # ==================== Dashboard PDF Export ====================
    
    def create_dashboard_pdf(
        self,
        dashboard_data: Dict[str, Any],
        title: str = "Dashboard"
    ) -> bytes:
        """
        Create PDF from dashboard data (multi-chart layouts, KPI displays)
        
        Args:
            dashboard_data: Dict containing widgets, charts, and KPIs
            title: Title for the dashboard
            
        Returns:
            PDF bytes
        """
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=landscape(A4))
        width, height = landscape(A4)
        
        # Generate dynamic key
        dynamic_key = self.key_mixin.generate_dynamic_key(KeyPrefix.CHART)
        
        # Header
        pdf.setFillColorRGB(0.15, 0.15, 0.15)
        pdf.rect(0, height - 60, width, 60, fill=True, stroke=False)
        
        pdf.setFillColorRGB(1, 1, 1)
        pdf.setFont("Helvetica-Bold", 22)
        pdf.drawString(30, height - 35, title)
        pdf.setFont("Helvetica", 9)
        pdf.drawString(30, height - 50, f"Generated: {datetime.now().strftime('%d.%m.%Y %H:%M')} | Key: {dynamic_key}")
        
        pdf.setFillColorRGB(0, 0, 0)  # Reset to black
        
        # KPI Section
        if 'kpis' in dashboard_data:
            self._add_kpi_section(pdf, dashboard_data['kpis'], width, height)
        
        # Widgets/Charts Grid
        if 'widgets' in dashboard_data:
            self._add_dashboard_widgets(pdf, dashboard_data['widgets'], width, height)
        
        pdf.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    def _add_kpi_section(self, pdf: canvas.Canvas, kpis: List[Dict[str, Any]], 
                        page_width: float, page_height: float):
        """Add KPI cards to dashboard"""
        kpi_count = len(kpis)
        kpi_width = (page_width - 60) / kpi_count
        y_position = page_height - 80
        
        for i, kpi in enumerate(kpis):
            x = 30 + i * kpi_width
            
            # KPI card background
            pdf.setFillColorRGB(0.95, 0.97, 1.0)
            pdf.setStrokeColorRGB(0.7, 0.7, 0.7)
            pdf.setLineWidth(1)
            pdf.rect(x, y_position - 70, kpi_width - 10, 70, fill=True, stroke=True)
            
            # KPI value
            pdf.setFillColorRGB(0.1, 0.3, 0.7)
            pdf.setFont("Helvetica-Bold", 24)
            value_formatted = self._format_value(kpi.get('value', 0))
            pdf.drawCentredString(x + kpi_width/2 - 5, y_position - 30, value_formatted)
            
            # KPI label
            pdf.setFillColorRGB(0, 0, 0)
            pdf.setFont("Helvetica", 10)
            pdf.drawCentredString(x + kpi_width/2 - 5, y_position - 50, kpi.get('label', ''))
            
            # Trend indicator
            if 'trend' in kpi:
                trend = kpi['trend']
                trend_color = (0, 0.7, 0) if trend > 0 else (0.7, 0, 0)
                pdf.setFillColorRGB(*trend_color)
                trend_symbol = "▲" if trend > 0 else "▼"
                pdf.setFont("Helvetica", 12)
                pdf.drawCentredString(x + kpi_width/2 - 5, y_position - 65, 
                                    f"{trend_symbol} {abs(trend):.1f}%")
    
    def _add_dashboard_widgets(self, pdf: canvas.Canvas, widgets: List[Dict[str, Any]],
                               page_width: float, page_height: float):
        """Add widget grid to dashboard"""
        # Calculate grid layout (2x2 or 2x3 depending on widget count)
        widget_count = len(widgets)
        cols = 2 if widget_count <= 4 else 3
        rows = (widget_count + cols - 1) // cols
        
        widget_width = (page_width - 60) / cols
        widget_height = (page_height - 200) / rows
        
        for i, widget in enumerate(widgets):
            row = i // cols
            col = i % cols
            
            x = 30 + col * widget_width
            y = page_height - 180 - (row + 1) * widget_height
            
            # Widget border
            pdf.setStrokeColorRGB(0.8, 0.8, 0.8)
            pdf.setLineWidth(1)
            pdf.rect(x, y, widget_width - 10, widget_height - 10, fill=False, stroke=True)
            
            # Widget title
            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawString(x + 10, y + widget_height - 25, widget.get('title', 'Widget'))
            
            # Widget content
            widget_type = widget.get('type', 'chart')
            if widget_type == 'chart':
                chart_img = self._generate_mini_chart(widget.get('data', {}), 
                                                      widget.get('chart_type', 'line'))
                img_reader = ImageReader(io.BytesIO(chart_img))
                pdf.drawImage(img_reader, x + 10, y + 10, 
                            width=widget_width - 30, height=widget_height - 50,
                            preserveAspectRatio=True)
    
    # ==================== Helper Methods ====================
    
    def _generate_mini_chart(self, data: Dict[str, Any], chart_type: str) -> bytes:
        """Generate a small chart image for embedding"""
        fig, ax = plt.subplots(figsize=(6, 4))
        
        x_data = data.get('x', [])
        y_data = data.get('y', [])
        
        if chart_type == 'line':
            ax.plot(x_data, y_data, linewidth=2, marker='o', color='#2563eb')
            ax.fill_between(x_data, y_data, alpha=0.3, color='#2563eb')
        elif chart_type == 'bar':
            ax.bar(x_data, y_data, color='#10b981', alpha=0.8)
        elif chart_type == 'pie':
            ax.pie(y_data, labels=x_data, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
        
        # Format y-axis with German numbers
        if chart_type != 'pie':
            ax.yaxis.set_major_formatter(
                plt.FuncFormatter(lambda x, p: self.formatter.format(x, decimal_places=0))
            )
        
        ax.set_title(data.get('title', ''), fontsize=10, weight='bold')
        ax.grid(True, alpha=0.3)
        
        # Save to bytes
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        plt.close(fig)
        
        return buffer.getvalue()
    
    def _add_metadata_page(self, pdf: canvas.Canvas, metadata: Dict[str, Any], dynamic_key: str):
        """Add a metadata page to the PDF"""
        width, height = A4
        
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, height - 50, "Metadata")
        
        y_position = height - 80
        pdf.setFont("Helvetica", 10)
        
        # Add dynamic key
        pdf.drawString(70, y_position, f"Dynamic Key: {dynamic_key}")
        y_position -= 20
        
        # Add metadata fields
        for key, value in metadata.items():
            if y_position < 50:
                break
            formatted_value = self._format_value(value)
            pdf.drawString(70, y_position, f"{key}: {formatted_value}")
            y_position -= 15
    
    def _add_diagram_legend(self, pdf: canvas.Canvas, legend: Dict[str, Any],
                           page_width: float, page_height: float):
        """Add legend to diagram"""
        items = legend.get('items', [])
        x_start = 50
        y_start = 30
        
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(x_start, y_start, "Legend:")
        
        x_position = x_start + 60
        for item in items:
            # Color box
            color = item.get('color', 'gray')
            pdf.setFillColor(colors.HexColor(color) if color.startswith('#') else colors.gray)
            pdf.rect(x_position, y_start - 5, 15, 10, fill=True, stroke=True)
            
            # Label
            pdf.setFillColorRGB(0, 0, 0)
            pdf.setFont("Helvetica", 9)
            pdf.drawString(x_position + 20, y_start, item.get('label', ''))
            
            x_position += 120
    
    def _format_value(self, value: Any) -> str:
        """Format a value with German formatting if numeric"""
        if isinstance(value, (int, float)):
            return self.formatter.format(value, decimal_places=2)
        return str(value)
    
    def _wrap_text(self, text: str, max_length: int) -> str:
        """Wrap text to multiple lines"""
        if len(text) <= max_length:
            return text
        
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_length:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
    
    def _wrap_text_to_width(self, text: str, max_width: float, pdf: canvas.Canvas) -> List[str]:
        """Wrap text to fit within a specific width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if pdf.stringWidth(test_line, "Helvetica", 10) <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    # ==================== Batch Export ====================
    
    def export_multiple_visualizations(
        self,
        visualizations: List[Dict[str, Any]],
        output_format: str = "separate"
    ) -> Dict[str, bytes]:
        """
        Export multiple visualizations to PDF
        
        Args:
            visualizations: List of visualization data dicts with 'type' and 'data' keys
            output_format: "separate" for individual PDFs or "combined" for single PDF
            
        Returns:
            Dict mapping dynamic keys to PDF bytes
        """
        results = {}
        
        if output_format == "separate":
            for viz in visualizations:
                viz_type = viz.get('type', 'diagram')
                viz_data = viz.get('data', {})
                title = viz.get('title', 'Visualization')
                
                if viz_type == '3d':
                    pdf_bytes = self.create_3d_visualization_pdf(viz_data, title)
                elif viz_type == 'diagram':
                    pdf_bytes = self.create_diagram_pdf(viz_data, title=title)
                elif viz_type == 'flowchart':
                    pdf_bytes = self.create_flowchart_pdf(viz_data, title)
                elif viz_type == 'infographic':
                    pdf_bytes = self.create_infographic_pdf(viz_data, title)
                elif viz_type == 'dashboard':
                    pdf_bytes = self.create_dashboard_pdf(viz_data, title)
                else:
                    continue
                
                key = self.key_mixin.generate_dynamic_key(KeyPrefix.CHART, custom_suffix=viz_type)
                results[key] = pdf_bytes
        
        return results
    
    def to_base64(self, pdf_bytes: bytes) -> str:
        """Convert PDF bytes to base64 string"""
        return base64.b64encode(pdf_bytes).decode('utf-8')
