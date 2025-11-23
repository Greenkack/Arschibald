"""
Demo script for PDF Chart Service
Generates examples of all 10 chart types with different color schemes
"""

from services.pdf_chart_service import PDFChartService, ChartType, ColorScheme
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


def main():
    """Generate demo PDF with all chart types"""
    service = PDFChartService()
    
    # Create PDF
    pdf_path = "demo_charts_output.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)
    page_width, page_height = A4
    
    # Page 1: Pie and Donut Charts
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, page_height - 50, "PDF Chart Integration - Demo")
    c.setFont("Helvetica", 12)
    c.drawString(50, page_height - 70, "10 Chart Types with German Formatting")
    
    # Pie Chart
    pie_data = {
        'labels': ['PV-Module', 'Wechselrichter', 'Speicher', 'Installation'],
        'values': [8500, 3200, 4500, 2800]
    }
    pie_chart = service.generate_chart(
        ChartType.PIE,
        pie_data,
        width=250,
        height=200,
        color_scheme=ColorScheme.SOLAR,
        title="Kostenverteilung (Pie Chart)",
        show_legend=True
    )
    pie_chart.drawOn(c, 50, page_height - 350)
    
    # Donut Chart
    donut_chart = service.generate_chart(
        ChartType.DONUT,
        pie_data,
        width=250,
        height=200,
        color_scheme=ColorScheme.NATURE,
        title="Kostenverteilung (Donut Chart)",
        show_legend=True
    )
    donut_chart.drawOn(c, 320, page_height - 350)
    
    c.showPage()
    
    # Page 2: Bar and Column Charts
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, page_height - 50, "Bar und Column Charts")
    
    bar_data = {
        'categories': ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun'],
        'series': [[1200, 1350, 1500, 1650, 1800, 1900]]
    }
    
    # Bar Chart
    bar_chart = service.generate_chart(
        ChartType.BAR,
        bar_data,
        width=250,
        height=200,
        color_scheme=ColorScheme.PROFESSIONAL,
        title="Monatliche Produktion (Bar)",
        x_label="Produktion (kWh)",
        y_label="Monat"
    )
    bar_chart.drawOn(c, 50, page_height - 300)
    
    # Column Chart
    column_chart = service.generate_chart(
        ChartType.COLUMN,
        bar_data,
        width=250,
        height=200,
        color_scheme=ColorScheme.VIBRANT,
        title="Monatliche Produktion (Column)",
        x_label="Monat",
        y_label="Produktion (kWh)"
    )
    column_chart.drawOn(c, 320, page_height - 300)
    
    c.showPage()

    
    # Page 3: Line and Area Charts
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, page_height - 50, "Line und Area Charts")
    
    line_data = {
        'categories': ['Q1', 'Q2', 'Q3', 'Q4'],
        'series': [[1000, 1200, 1100, 1400], [900, 1100, 1300, 1350]],
        'series_names': ['2023', '2024']
    }
    
    # Line Chart
    line_chart = service.generate_chart(
        ChartType.LINE,
        line_data,
        width=250,
        height=200,
        color_scheme=ColorScheme.PROFESSIONAL,
        title="Quartalsproduktion (Line)",
        x_label="Quartal",
        y_label="Produktion (kWh)",
        show_legend=True
    )
    line_chart.drawOn(c, 50, page_height - 300)
    
    # Area Chart
    area_chart = service.generate_chart(
        ChartType.AREA,
        line_data,
        width=250,
        height=200,
        color_scheme=ColorScheme.SOLAR,
        title="Quartalsproduktion (Area)",
        x_label="Quartal",
        y_label="Produktion (kWh)",
        show_legend=True
    )
    area_chart.drawOn(c, 320, page_height - 300)
    
    c.showPage()
    
    # Page 4: Circle and Polar Charts
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, page_height - 50, "Circle und Polar Charts")
    
    # Circle Chart
    circle_data = {
        'value': 85.5,
        'max_value': 100,
        'label': 'Effizienz'
    }
    circle_chart = service.generate_chart(
        ChartType.CIRCLE,
        circle_data,
        width=250,
        height=250,
        color_scheme=ColorScheme.NATURE,
        title="System-Effizienz (Circle)",
        show_values=True
    )
    circle_chart.drawOn(c, 50, page_height - 350)
    
    # Polar Chart
    polar_data = {
        'categories': ['N', 'NO', 'O', 'SO', 'S', 'SW', 'W', 'NW'],
        'values': [60, 70, 85, 90, 95, 90, 75, 65]
    }
    polar_chart = service.generate_chart(
        ChartType.POLAR,
        polar_data,
        width=250,
        height=250,
        color_scheme=ColorScheme.PROFESSIONAL,
        title="Ausrichtungsanalyse (Polar)",
        show_values=True
    )
    polar_chart.drawOn(c, 320, page_height - 350)
    
    c.showPage()
    
    # Page 5: Radar and Waterfall Charts
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, page_height - 50, "Radar und Waterfall Charts")
    
    # Radar Chart
    radar_data = {
        'categories': ['Leistung', 'Effizienz', 'Kosten', 'Wartung', 'Garantie'],
        'series': [[85, 90, 70, 80, 95], [75, 85, 85, 75, 90]],
        'series_names': ['Produkt A', 'Produkt B']
    }
    radar_chart = service.generate_chart(
        ChartType.RADAR,
        radar_data,
        width=250,
        height=250,
        color_scheme=ColorScheme.VIBRANT,
        title="Produktvergleich (Radar)",
        show_legend=True
    )
    radar_chart.drawOn(c, 50, page_height - 350)
    
    # Waterfall Chart
    waterfall_data = {
        'categories': ['Start', 'Einnahmen', 'Ausgaben', 'Steuern', 'Ende'],
        'values': [10000, 5000, -3000, -1000, 0]
    }
    waterfall_chart = service.generate_chart(
        ChartType.WATERFALL,
        waterfall_data,
        width=250,
        height=250,
        color_scheme=ColorScheme.PROFESSIONAL,
        title="Cash-Flow-Analyse (Waterfall)",
        x_label="Kategorie",
        y_label="Betrag (€)",
        show_values=True
    )
    waterfall_chart.drawOn(c, 320, page_height - 350)
    
    c.showPage()
    
    # Page 6: Color Schemes Comparison
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, page_height - 50, "Farbschemata-Vergleich")
    
    simple_data = {
        'labels': ['A', 'B', 'C', 'D'],
        'values': [25, 30, 25, 20]
    }
    
    schemes = [
        (ColorScheme.SOLAR, "Solar"),
        (ColorScheme.NATURE, "Nature"),
        (ColorScheme.PROFESSIONAL, "Professional"),
        (ColorScheme.VIBRANT, "Vibrant"),
        (ColorScheme.MONOCHROME, "Monochrome")
    ]
    
    y_pos = page_height - 150
    for i, (scheme, name) in enumerate(schemes):
        if i > 0 and i % 2 == 0:
            y_pos -= 200
        
        x_pos = 50 if i % 2 == 0 else 320
        
        chart = service.generate_chart(
            ChartType.PIE,
            simple_data,
            width=200,
            height=150,
            color_scheme=scheme,
            title=f"Schema: {name}",
            show_legend=False
        )
        chart.drawOn(c, x_pos, y_pos)
    
    c.showPage()
    
    # Page 7: 3D Effects Demonstration
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, page_height - 50, "3D-Effekte Demonstration")
    
    # 2D Pie
    pie_2d = service.generate_chart(
        ChartType.PIE,
        pie_data,
        width=250,
        height=200,
        color_scheme=ColorScheme.PROFESSIONAL,
        enable_3d=False,
        title="2D Pie Chart"
    )
    pie_2d.drawOn(c, 50, page_height - 300)
    
    # 3D Pie
    pie_3d = service.generate_chart(
        ChartType.PIE,
        pie_data,
        width=250,
        height=200,
        color_scheme=ColorScheme.PROFESSIONAL,
        enable_3d=True,
        title="3D Pie Chart"
    )
    pie_3d.drawOn(c, 320, page_height - 300)
    
    # Add summary
    c.setFont("Helvetica", 10)
    c.drawString(50, page_height - 350, "Alle Diagramme verwenden deutsche Zahlenformatierung:")
    c.drawString(50, page_height - 370, f"• Währung: {service.format_currency(16999.00)}")
    c.drawString(50, page_height - 390, f"• Prozent: {service.format_percentage(85.5)}")
    c.drawString(50, page_height - 410, f"• Energie: {service.format_kwh(12500)}")
    c.drawString(50, page_height - 430, f"• Zahlen: {service.format_german_number(1234567.89, 2)}")
    
    # Save PDF
    c.save()
    print(f"Demo PDF erstellt: {pdf_path}")
    print("\nGenerierte Diagrammtypen:")
    print("1. PIE - Kreisdiagramm")
    print("2. DONUT - Ringdiagramm")
    print("3. BAR - Horizontales Balkendiagramm")
    print("4. COLUMN - Vertikales Säulendiagramm")
    print("5. LINE - Liniendiagramm")
    print("6. AREA - Flächendiagramm")
    print("7. CIRCLE - Kreisfortschritt")
    print("8. POLAR - Polardiagramm")
    print("9. RADAR - Netzdiagramm")
    print("10. WATERFALL - Wasserfalldiagramm")
    print("\nFarbschemata:")
    print("• SOLAR - Gelb/Orange/Rot-Töne")
    print("• NATURE - Grün/Blau/Erdtöne")
    print("• PROFESSIONAL - Blau/Grau/Corporate")
    print("• VIBRANT - Leuchtende Farben")
    print("• MONOCHROME - Graustufen")


if __name__ == "__main__":
    main()
