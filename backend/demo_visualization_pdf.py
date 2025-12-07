"""
Demo: Visualization PDF Bytes Generation

This demo showcases all visualization PDF generation capabilities:
1. 3D Visualization PDF Export (solar panel layouts)
2. Diagram PDF Generation (system architecture)
3. Flowchart PDF Export (process flows)
4. Infographic PDF Generation (statistics and comparisons)
5. Dashboard PDF Export (KPIs and multi-chart layouts)

All PDFs include:
- German number formatting (1.234,56)
- Dynamic keys for tracking
- Professional layouts
"""

import os
from backend.services.visualization_pdf_service import VisualizationPDFService


def demo_3d_visualization_pdf():
    """Demo 3D visualization PDF export"""
    print("\n" + "="*70)
    print("DEMO 1: 3D Visualization PDF Export")
    print("="*70)
    
    service = VisualizationPDFService()
    
    # Sample 3D visualization data (solar panel layout)
    viz_data = {
        'views': {
            'front': {
                'vertices': [
                    [0, 0, 0], [10, 0, 0], [10, 8, 0], [0, 8, 0],
                    [0, 0, 2], [10, 0, 2], [10, 8, 2], [0, 8, 2]
                ],
                'faces': [
                    [[0, 0, 0], [10, 0, 0], [10, 8, 0], [0, 8, 0]],
                    [[0, 0, 2], [10, 0, 2], [10, 8, 2], [0, 8, 2]]
                ],
                'title': 'Front View',
                'stats': {
                    'Modules': 24,
                    'Power (kWp)': 9.6,
                    'Area (m²)': 45.2
                }
            },
            'top': {
                'vertices': [[0, 0, 0], [10, 0, 0], [10, 8, 0], [0, 8, 0]],
                'faces': [[[0, 0, 0], [10, 0, 0], [10, 8, 0], [0, 8, 0]]],
                'title': 'Top View',
                'stats': {
                    'Rows': 4,
                    'Columns': 6,
                    'Spacing (cm)': 2.5
                }
            }
        },
        'modules': [{'id': i} for i in range(24)],
        'total_power': 9.6,
        'area_coverage': 45.2,
        'metadata': {
            'Project': 'Residential Solar Installation',
            'Location': 'Munich, Germany',
            'Date': '15.01.2024',
            'Module Type': 'Trina Solar 400W',
            'Roof Angle': 30.0,
            'Orientation': 'South'
        }
    }
    
    pdf_bytes = service.create_3d_visualization_pdf(
        viz_data,
        title="Solar Panel 3D Layout",
        include_metadata=True
    )
    
    # Save to file
    output_dir = "backend/demo_output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "3d_visualization.pdf")
    
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)
    
    print(f" 3D Visualization PDF created: {output_path}")
    print(f"  Size: {len(pdf_bytes):,} bytes")
    print(f"  Views: {len(viz_data['views'])}")
    print(f"  Total Power: 9,60 kWp (German format)")
    print(f"  Area Coverage: 45,20 m²")


def demo_diagram_pdf():
    """Demo diagram PDF generation"""
    print("\n" + "="*70)
    print("DEMO 2: Diagram PDF Generation")
    print("="*70)
    
    service = VisualizationPDFService()
    
    # Sample system architecture diagram
    diagram_data = {
        'nodes': [
            {'id': 'solar', 'x': 0, 'y': 4, 'label': 'Solar Panels', 
             'shape': 'rectangle', 'color': '#fbbf24', 'width': 2, 'height': 1,
             'value': 9.6},
            {'id': 'inverter', 'x': 0, 'y': 2, 'label': 'Inverter', 
             'shape': 'rectangle', 'color': '#60a5fa', 'width': 2, 'height': 1,
             'value': 10.0},
            {'id': 'battery', 'x': -3, 'y': 0, 'label': 'Battery', 
             'shape': 'rectangle', 'color': '#34d399', 'width': 2, 'height': 1,
             'value': 10.5},
            {'id': 'grid', 'x': 3, 'y': 0, 'label': 'Grid', 
             'shape': 'rectangle', 'color': '#f87171', 'width': 2, 'height': 1},
            {'id': 'home', 'x': 0, 'y': -2, 'label': 'Home', 
             'shape': 'rectangle', 'color': '#a78bfa', 'width': 2, 'height': 1,
             'value': 4500.0}
        ],
        'edges': [
            {'from': 'solar', 'to': 'inverter', 'label': 'DC Power'},
            {'from': 'inverter', 'to': 'battery', 'label': 'Charge'},
            {'from': 'inverter', 'to': 'grid', 'label': 'Feed-in'},
            {'from': 'inverter', 'to': 'home', 'label': 'AC Power'},
            {'from': 'battery', 'to': 'home', 'label': 'Backup'},
            {'from': 'grid', 'to': 'home', 'label': 'Supply'}
        ],
        'legend': {
            'items': [
                {'color': '#fbbf24', 'label': 'Generation'},
                {'color': '#60a5fa', 'label': 'Conversion'},
                {'color': '#34d399', 'label': 'Storage'},
                {'color': '#f87171', 'label': 'Grid'},
                {'color': '#a78bfa', 'label': 'Consumption'}
            ]
        }
    }
    
    pdf_bytes = service.create_diagram_pdf(
        diagram_data,
        diagram_type="system",
        title="Solar Energy System Architecture"
    )
    
    output_path = "backend/demo_output/system_diagram.pdf"
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)
    
    print(f" Diagram PDF created: {output_path}")
    print(f"  Size: {len(pdf_bytes):,} bytes")
    print(f"  Nodes: {len(diagram_data['nodes'])}")
    print(f"  Connections: {len(diagram_data['edges'])}")


def demo_flowchart_pdf():
    """Demo flowchart PDF export"""
    print("\n" + "="*70)
    print("DEMO 3: Flowchart PDF Export")
    print("="*70)
    
    service = VisualizationPDFService()
    
    # Sample process flowchart
    flowchart_data = {
        'steps': [
            {'id': 1, 'x': 0, 'y': 6, 'type': 'start', 'label': 'Start Installation'},
            {'id': 2, 'x': 0, 'y': 4, 'type': 'process', 'label': 'Site Assessment'},
            {'id': 3, 'x': 0, 'y': 2, 'type': 'decision', 'label': 'Roof Suitable?'},
            {'id': 4, 'x': -2.5, 'y': 0, 'type': 'process', 'label': 'Recommend Alternatives'},
            {'id': 5, 'x': 2.5, 'y': 0, 'type': 'process', 'label': 'Design System'},
            {'id': 6, 'x': 2.5, 'y': -2, 'type': 'process', 'label': 'Install Panels'},
            {'id': 7, 'x': 2.5, 'y': -4, 'type': 'process', 'label': 'Connect Inverter'},
            {'id': 8, 'x': 2.5, 'y': -6, 'type': 'decision', 'label': 'System Test OK?'},
            {'id': 9, 'x': 0, 'y': -8, 'type': 'process', 'label': 'Troubleshoot'},
            {'id': 10, 'x': 2.5, 'y': -10, 'type': 'end', 'label': 'Complete'}
        ],
        'connections': [
            {'from': 1, 'to': 2},
            {'from': 2, 'to': 3},
            {'from': 3, 'to': 4, 'label': 'No'},
            {'from': 3, 'to': 5, 'label': 'Yes'},
            {'from': 5, 'to': 6},
            {'from': 6, 'to': 7},
            {'from': 7, 'to': 8},
            {'from': 8, 'to': 9, 'label': 'No'},
            {'from': 9, 'to': 8},
            {'from': 8, 'to': 10, 'label': 'Yes'}
        ]
    }
    
    pdf_bytes = service.create_flowchart_pdf(
        flowchart_data,
        title="Solar Installation Process Flow"
    )
    
    output_path = "backend/demo_output/process_flowchart.pdf"
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)
    
    print(f" Flowchart PDF created: {output_path}")
    print(f"  Size: {len(pdf_bytes):,} bytes")
    print(f"  Steps: {len(flowchart_data['steps'])}")
    print(f"  Connections: {len(flowchart_data['connections'])}")


def demo_infographic_pdf():
    """Demo infographic PDF generation"""
    print("\n" + "="*70)
    print("DEMO 4: Infographic PDF Generation")
    print("="*70)
    
    service = VisualizationPDFService()
    
    # Sample infographic data
    infographic_data = {
        'sections': [
            {
                'type': 'stat_box',
                'stats': [
                    {'value': 9876.54, 'label': 'Annual Production', 'unit': 'kWh'},
                    {'value': 1234.56, 'label': 'Cost Savings', 'unit': '€'},
                    {'value': 4.5, 'label': 'CO₂ Avoided', 'unit': 'tons'}
                ]
            },
            {
                'type': 'text',
                'title': 'Environmental Impact',
                'text': 'This solar installation will offset approximately 4.5 tons of CO₂ emissions annually, equivalent to planting 200 trees or taking 1 car off the road for a year.'
            },
            {
                'type': 'comparison',
                'title': 'Energy Source Comparison',
                'items': [
                    {'name': 'Solar Energy', 'value': 95, 'max': 100},
                    {'name': 'Wind Energy', 'value': 75, 'max': 100},
                    {'name': 'Natural Gas', 'value': 45, 'max': 100},
                    {'name': 'Coal', 'value': 20, 'max': 100}
                ]
            },
            {
                'type': 'chart',
                'chart_type': 'bar',
                'data': {
                    'x': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    'y': [650, 720, 890, 950, 1100, 1200],
                    'title': 'Monthly Energy Production (kWh)'
                }
            }
        ]
    }
    
    pdf_bytes = service.create_infographic_pdf(
        infographic_data,
        title="Solar Energy Impact Report"
    )
    
    output_path = "backend/demo_output/solar_infographic.pdf"
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)
    
    print(f" Infographic PDF created: {output_path}")
    print(f"  Size: {len(pdf_bytes):,} bytes")
    print(f"  Sections: {len(infographic_data['sections'])}")
    print(f"  Annual Production: 9.876,54 kWh (German format)")
    print(f"  Cost Savings: 1.234,56 € (German format)")


def demo_dashboard_pdf():
    """Demo dashboard PDF export"""
    print("\n" + "="*70)
    print("DEMO 5: Dashboard PDF Export")
    print("="*70)
    
    service = VisualizationPDFService()
    
    # Sample dashboard data
    dashboard_data = {
        'kpis': [
            {'value': 9876.54, 'label': 'Total Production (kWh)', 'trend': 12.5},
            {'value': 1234.56, 'label': 'Revenue (€)', 'trend': 8.3},
            {'value': 89.5, 'label': 'System Efficiency (%)', 'trend': -2.1},
            {'value': 156, 'label': 'Active Projects', 'trend': 15.7}
        ],
        'widgets': [
            {
                'title': 'Energy Production Trend',
                'type': 'chart',
                'chart_type': 'line',
                'data': {
                    'x': [1, 2, 3, 4, 5, 6],
                    'y': [850, 920, 1050, 980, 1100, 1200],
                    'title': 'Monthly Production (kWh)'
                }
            },
            {
                'title': 'Energy Distribution',
                'type': 'chart',
                'chart_type': 'pie',
                'data': {
                    'x': ['Self-Consumption', 'Grid Feed-in', 'Battery Storage'],
                    'y': [45, 35, 20],
                    'title': 'Energy Usage'
                }
            },
            {
                'title': 'System Performance',
                'type': 'chart',
                'chart_type': 'bar',
                'data': {
                    'x': ['Q1', 'Q2', 'Q3', 'Q4'],
                    'y': [2500, 3200, 3800, 2800],
                    'title': 'Quarterly Production (kWh)'
                }
            },
            {
                'title': 'Cost Savings',
                'type': 'chart',
                'chart_type': 'line',
                'data': {
                    'x': [1, 2, 3, 4, 5, 6],
                    'y': [180, 210, 245, 220, 260, 290],
                    'title': 'Monthly Savings (€)'
                }
            }
        ]
    }
    
    pdf_bytes = service.create_dashboard_pdf(
        dashboard_data,
        title="Solar Energy Performance Dashboard"
    )
    
    output_path = "backend/demo_output/performance_dashboard.pdf"
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)
    
    print(f" Dashboard PDF created: {output_path}")
    print(f"  Size: {len(pdf_bytes):,} bytes")
    print(f"  KPIs: {len(dashboard_data['kpis'])}")
    print(f"  Widgets: {len(dashboard_data['widgets'])}")
    print(f"  Total Production: 9.876,54 kWh (German format)")


def demo_batch_export():
    """Demo batch export of multiple visualizations"""
    print("\n" + "="*70)
    print("DEMO 6: Batch Export")
    print("="*70)
    
    service = VisualizationPDFService()
    
    visualizations = [
        {
            'type': 'diagram',
            'title': 'System Overview',
            'data': {
                'nodes': [
                    {'id': 'A', 'x': 0, 'y': 0, 'label': 'Solar', 'shape': 'circle', 'color': '#fbbf24'},
                    {'id': 'B', 'x': 3, 'y': 0, 'label': 'Home', 'shape': 'rectangle', 'color': '#a78bfa'}
                ],
                'edges': [{'from': 'A', 'to': 'B', 'label': 'Power'}]
            }
        },
        {
            'type': 'flowchart',
            'title': 'Quick Process',
            'data': {
                'steps': [
                    {'id': 1, 'x': 0, 'y': 0, 'type': 'start', 'label': 'Start'},
                    {'id': 2, 'x': 0, 'y': -2, 'type': 'end', 'label': 'End'}
                ],
                'connections': [{'from': 1, 'to': 2}]
            }
        }
    ]
    
    results = service.export_multiple_visualizations(visualizations, "separate")
    
    print(f" Batch export completed")
    print(f"  Visualizations exported: {len(results)}")
    
    for i, (key, pdf_bytes) in enumerate(results.items(), 1):
        output_path = f"backend/demo_output/batch_export_{i}.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        print(f"  {i}. {key}: {len(pdf_bytes):,} bytes -> {output_path}")


def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("VISUALIZATION PDF BYTES - COMPREHENSIVE DEMO")
    print("="*70)
    print("\nThis demo showcases all visualization PDF generation capabilities")
    print("with German number formatting (1.234,56) and dynamic keys.")
    
    demo_3d_visualization_pdf()
    demo_diagram_pdf()
    demo_flowchart_pdf()
    demo_infographic_pdf()
    demo_dashboard_pdf()
    demo_batch_export()
    
    print("\n" + "="*70)
    print("ALL DEMOS COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("\nGenerated PDFs are saved in: backend/demo_output/")
    print("\nFeatures demonstrated:")
    print("   3D visualization PDF export with multiple views")
    print("   System diagram PDF generation with legend")
    print("   Process flowchart PDF export with decision nodes")
    print("   Infographic PDF with stats, comparisons, and charts")
    print("   Dashboard PDF with KPIs and widget grid")
    print("   Batch export of multiple visualizations")
    print("   German number formatting throughout (1.234,56)")
    print("   Dynamic keys for all PDFs")
    print("   Professional layouts and styling")


if __name__ == "__main__":
    main()
