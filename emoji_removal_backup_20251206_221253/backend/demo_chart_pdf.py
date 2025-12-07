"""
Demo: Chart PDF Bytes Generation

This demo showcases all chart types with German formatting.
"""

from backend.services.chart_pdf_service import (
    ChartData,
    ChartPDFService,
    create_line_chart_pdf,
    create_bar_chart_pdf,
    create_pie_chart_pdf,
    create_area_chart_pdf,
    create_scatter_plot_pdf,
    REPORTLAB_AVAILABLE
)
from backend.core.pdf_bytes import PDFMetadata


def demo_line_chart():
    """Demo line chart generation"""
    print("\n=== Line Chart Demo ===")

    service = ChartPDFService()

    # Create chart data
    chart_data = ChartData(
        title="Solar Energy Production Over Time",
        data=[
            [1200.50, 1350.75, 1500.25, 1650.00, 1800.50, 1950.75],
            [1100.25, 1250.50, 1400.75, 1550.25, 1700.00, 1850.50]
        ],
        labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        series_names=["System A (kWh)", "System B (kWh)"],
        x_axis_label="Month",
        y_axis_label="Energy Production (kWh)"
    )

    # Generate PDF
    pdf_bytes = service.create_line_chart_pdf(chart_data)

    # Save to file
    with open("demo_line_chart.pdf", "wb") as f:
        f.write(pdf_bytes)

    print(f"✓ Line chart PDF generated: {len(pdf_bytes)} bytes")
    print("  Saved as: demo_line_chart.pdf")
    print(f"  Data points: {len(chart_data.labels)}")
    print(f"  Series: {len(chart_data.data)}")


def demo_bar_chart():
    """Demo bar chart generation"""
    print("\n=== Bar Chart Demo ===")

    # Using convenience function
    pdf_bytes = create_bar_chart_pdf(
        title="Product Sales Comparison",
        data=[
            [15000.00, 18000.50, 22000.75],
            [12000.25, 16000.00, 20000.50],
            [10000.50, 14000.75, 18000.25]
        ],
        labels=["Product A", "Product B", "Product C"],
        series_names=["Q1 2024 (€)", "Q2 2024 (€)", "Q3 2024 (€)"],
        x_axis_label="Products",
        y_axis_label="Sales (€)"
    )

    # Save to file
    with open("demo_bar_chart.pdf", "wb") as f:
        f.write(pdf_bytes)

    print(f"✓ Bar chart PDF generated: {len(pdf_bytes)} bytes")
    print("  Saved as: demo_bar_chart.pdf")


def demo_pie_chart():
    """Demo pie chart generation"""
    print("\n=== Pie Chart Demo ===")

    service = ChartPDFService()

    # Create chart data
    chart_data = ChartData(
        title="Market Share Distribution",
        data=[[35.50, 28.25, 18.75, 12.00, 5.50]],
        labels=[
            "Solar Panels",
            "Inverters",
            "Batteries",
            "Mounting Systems",
            "Others"
        ]
    )

    # Generate PDF with metadata
    metadata = PDFMetadata(
        title="Market Share Analysis",
        author="Solar Calculator Pro",
        subject="Market Distribution",
        keywords=["market", "share", "analysis"]
    )

    pdf_bytes = service.create_pie_chart_pdf(chart_data, metadata)

    # Save to file
    with open("demo_pie_chart.pdf", "wb") as f:
        f.write(pdf_bytes)

    print(f"✓ Pie chart PDF generated: {len(pdf_bytes)} bytes")
    print("  Saved as: demo_pie_chart.pdf")
    print(f"  Categories: {len(chart_data.labels)}")


def demo_area_chart():
    """Demo area chart generation"""
    print("\n=== Area Chart Demo ===")

    # Using convenience function
    pdf_bytes = create_area_chart_pdf(
        title="Cumulative Energy Savings",
        data=[
            [500.00, 1050.50, 1650.75, 2300.25, 3000.00,
             3750.50, 4550.75, 5400.25]
        ],
        labels=["Year 1", "Year 2", "Year 3", "Year 4",
                "Year 5", "Year 6", "Year 7", "Year 8"],
        series_names=["Savings (€)"],
        x_axis_label="Time Period",
        y_axis_label="Cumulative Savings (€)"
    )

    # Save to file
    with open("demo_area_chart.pdf", "wb") as f:
        f.write(pdf_bytes)

    print(f"✓ Area chart PDF generated: {len(pdf_bytes)} bytes")
    print("  Saved as: demo_area_chart.pdf")


def demo_scatter_plot():
    """Demo scatter plot generation"""
    print("\n=== Scatter Plot Demo ===")

    service = ChartPDFService()

    # Create chart data
    chart_data = ChartData(
        title="Temperature vs. Solar Panel Efficiency",
        data=[
            [15.5, 20.25, 25.75, 30.50, 35.25, 40.00],
            [98.5, 96.25, 93.75, 90.50, 87.25, 84.00]
        ],
        labels=["Point 1", "Point 2", "Point 3",
                "Point 4", "Point 5", "Point 6"],
        series_names=["Temperature (°C)", "Efficiency (%)"],
        x_axis_label="Measurement Points",
        y_axis_label="Values"
    )

    pdf_bytes = service.create_scatter_plot_pdf(chart_data)

    # Save to file
    with open("demo_scatter_plot.pdf", "wb") as f:
        f.write(pdf_bytes)

    print(f"✓ Scatter plot PDF generated: {len(pdf_bytes)} bytes")
    print("  Saved as: demo_scatter_plot.pdf")


def demo_german_formatting():
    """Demo German number formatting in charts"""
    print("\n=== German Formatting Demo ===")

    service = ChartPDFService()

    # Create chart with large numbers
    chart_data = ChartData(
        title="Large Numbers with German Formatting",
        data=[
            [1234567.89, 2345678.90, 3456789.01, 4567890.12]
        ],
        labels=["Q1", "Q2", "Q3", "Q4"],
        series_names=["Revenue (€)"]
    )

    # Show formatted values
    print("\nOriginal values:")
    for val in chart_data.data[0]:
        print(f"  {val}")

    print("\nGerman formatted values:")
    for val in chart_data.data[0]:
        formatted = chart_data.format_value(val)
        print(f"  {formatted}")

    # Generate PDF
    pdf_bytes = service.create_bar_chart_pdf(chart_data)

    # Save to file
    with open("demo_german_formatting.pdf", "wb") as f:
        f.write(pdf_bytes)

    print(f"\n✓ German formatting PDF generated: {len(pdf_bytes)} bytes")
    print("  Saved as: demo_german_formatting.pdf")


def demo_multi_series():
    """Demo chart with multiple series"""
    print("\n=== Multi-Series Chart Demo ===")

    service = ChartPDFService()

    # Create chart with multiple series
    chart_data = ChartData(
        title="Solar System Performance Comparison",
        data=[
            [1000.00, 1100.50, 1200.75, 1300.25, 1400.00],
            [950.25, 1050.00, 1150.50, 1250.75, 1350.25],
            [900.50, 1000.75, 1100.25, 1200.00, 1300.50],
            [850.75, 950.25, 1050.00, 1150.50, 1250.75]
        ],
        labels=["Jan", "Feb", "Mar", "Apr", "May"],
        series_names=[
            "System A (kWh)",
            "System B (kWh)",
            "System C (kWh)",
            "System D (kWh)"
        ],
        colors=["#2E86AB", "#A23B72", "#F18F01", "#6A994E"]
    )

    pdf_bytes = service.create_line_chart_pdf(chart_data)

    # Save to file
    with open("demo_multi_series.pdf", "wb") as f:
        f.write(pdf_bytes)

    print(f"✓ Multi-series chart PDF generated: {len(pdf_bytes)} bytes")
    print("  Saved as: demo_multi_series.pdf")
    print(f"  Series count: {len(chart_data.data)}")


def demo_all_charts():
    """Generate all chart types"""
    print("\n" + "=" * 60)
    print("Chart PDF Bytes Generation - Complete Demo")
    print("=" * 60)

    if not REPORTLAB_AVAILABLE:
        print("\n❌ Error: reportlab not installed")
        print("Install with: pip install reportlab")
        return

    try:
        demo_line_chart()
        demo_bar_chart()
        demo_pie_chart()
        demo_area_chart()
        demo_scatter_plot()
        demo_german_formatting()
        demo_multi_series()

        print("\n" + "=" * 60)
        print("✓ All demos completed successfully!")
        print("=" * 60)
        print("\nGenerated files:")
        print("  - demo_line_chart.pdf")
        print("  - demo_bar_chart.pdf")
        print("  - demo_pie_chart.pdf")
        print("  - demo_area_chart.pdf")
        print("  - demo_scatter_plot.pdf")
        print("  - demo_german_formatting.pdf")
        print("  - demo_multi_series.pdf")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo_all_charts()
