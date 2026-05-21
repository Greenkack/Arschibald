"""
PDF Byte Generation Examples

This file demonstrates various use cases for the PDF byte generation system.
"""

import sys
from pathlib import Path

# Add parent directory to path for backend imports
parent_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_path))

from backend.core.pdf_bytes import (
    PDFByteMixin,
    PDFMetadata,
    PDFRenderingEngine,
    SimplePDFDocument,
    create_pdf_from_dict,
    create_pdf_from_text,
    REPORTLAB_AVAILABLE
)

if REPORTLAB_AVAILABLE:
    from reportlab.platypus import Paragraph, Spacer, Table, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from reportlab.lib import colors


def example_1_simple_text_pdf():
    """Example 1: Create a simple text PDF"""
    print("Example 1: Simple Text PDF")
    
    text = """
    This is a simple PDF document created from text.
    
    It supports multiple paragraphs and basic formatting.
    
    The PDF Byte Generation system makes it easy to create
    professional documents from any text content.
    """
    
    pdf_bytes = create_pdf_from_text(text, title="Simple Document")
    
    # Save to file
    with open("example_1_simple.pdf", "wb") as f:
        f.write(pdf_bytes)
    
    print(f"✓ Created example_1_simple.pdf ({len(pdf_bytes)} bytes)")


def example_2_dictionary_pdf():
    """Example 2: Create PDF from dictionary"""
    print("\nExample 2: Dictionary PDF")
    
    data = {
        "Customer Name": "John Doe",
        "Order Number": "ORD-2024-001",
        "Order Date": "2024-01-15",
        "Total Amount": 1234.56,
        "Tax": 234.56,
        "Grand Total": 1469.12,
        "Status": "Paid"
    }
    
    metadata = PDFMetadata(
        title="Order Summary",
        author="Sales System",
        subject="Order ORD-2024-001",
        keywords=["order", "invoice", "sales"]
    )
    
    pdf_bytes = create_pdf_from_dict(data, title="Order Summary", metadata=metadata)
    
    with open("example_2_dictionary.pdf", "wb") as f:
        f.write(pdf_bytes)
    
    print(f"✓ Created example_2_dictionary.pdf ({len(pdf_bytes)} bytes)")


class SolarCalculationReport(PDFByteMixin):
    """Example 3: Solar calculation report"""
    
    def __init__(self, customer, system_size, module_count, annual_production,
                 total_cost, savings_25_years, payback_period):
        super().__init__()
        self.customer = customer
        self.system_size = system_size
        self.module_count = module_count
        self.annual_production = annual_production
        self.total_cost = total_cost
        self.savings_25_years = savings_25_years
        self.payback_period = payback_period
    
    def _get_default_title(self):
        return f"Solar System Calculation - {self.customer}"
    
    def _get_default_subject(self):
        return "Solar PV System Sizing and Financial Analysis"
    
    def _render_to_pdf(self, story, doc):
        if not REPORTLAB_AVAILABLE:
            return
        
        styles = getSampleStyleSheet()
        
        # Custom title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Title
        story.append(Paragraph("Solar System Calculation Report", title_style))
        story.append(Spacer(1, 20))
        
        # Customer info
        story.append(Paragraph(f"<b>Customer:</b> {self.customer}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # System specifications table
        story.append(Paragraph("<b>System Specifications</b>", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        spec_data = [
            ['Parameter', 'Value'],
            ['System Size', f"{self._pdf_engine.format_german_number(self.system_size)} kWp"],
            ['Number of Modules', str(self.module_count)],
            ['Annual Production', f"{self._pdf_engine.format_german_number(self.annual_production)} kWh/year"]
        ]
        
        spec_table = self._pdf_engine.create_table(spec_data, col_widths=[200, 200])
        story.append(spec_table)
        story.append(Spacer(1, 20))
        
        # Financial analysis table
        story.append(Paragraph("<b>Financial Analysis</b>", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        financial_data = [
            ['Parameter', 'Value'],
            ['Total Investment', f"{self._pdf_engine.format_german_number(self.total_cost)} €"],
            ['25-Year Savings', f"{self._pdf_engine.format_german_number(self.savings_25_years)} €"],
            ['Payback Period', f"{self._pdf_engine.format_german_number(self.payback_period)} years"],
            ['ROI', f"{self._pdf_engine.format_german_number((self.savings_25_years / self.total_cost - 1) * 100)} %"]
        ]
        
        financial_table = self._pdf_engine.create_table(financial_data, col_widths=[200, 200])
        story.append(financial_table)
        story.append(Spacer(1, 30))
        
        # Conclusion
        story.append(Paragraph("<b>Conclusion</b>", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        conclusion = f"""
        Based on the analysis, a {self._pdf_engine.format_german_number(self.system_size)} kWp 
        solar system with {self.module_count} modules is recommended. The system will produce 
        approximately {self._pdf_engine.format_german_number(self.annual_production)} kWh per year 
        and will pay for itself in {self._pdf_engine.format_german_number(self.payback_period)} years.
        """
        
        story.append(Paragraph(conclusion, styles['Normal']))


def example_3_solar_report():
    """Example 3: Solar calculation report"""
    print("\nExample 3: Solar Calculation Report")
    
    if not REPORTLAB_AVAILABLE:
        print("⚠ Skipped (reportlab not installed)")
        return
    
    report = SolarCalculationReport(
        customer="Max Mustermann",
        system_size=10.5,
        module_count=30,
        annual_production=12000.50,
        total_cost=15000.00,
        savings_25_years=45000.75,
        payback_period=8.5
    )
    
    metadata = PDFMetadata(
        title="Solar Calculation - Max Mustermann",
        author="Solar Calculator Pro",
        subject="PV System Sizing",
        keywords=["solar", "pv", "calculation"]
    )
    
    report.set_pdf_metadata(metadata)
    report.save_pdf("example_3_solar_report.pdf")
    
    print("✓ Created example_3_solar_report.pdf")


class InvoiceDocument(PDFByteMixin):
    """Example 4: Professional invoice"""
    
    def __init__(self, invoice_number, customer, items, tax_rate=0.19):
        super().__init__()
        self.invoice_number = invoice_number
        self.customer = customer
        self.items = items
        self.tax_rate = tax_rate
        
        # Calculate totals
        self.subtotal = sum(item['quantity'] * item['price'] for item in items)
        self.tax = self.subtotal * tax_rate
        self.total = self.subtotal + self.tax
    
    def _get_default_title(self):
        return f"Invoice {self.invoice_number}"
    
    def _render_to_pdf(self, story, doc):
        if not REPORTLAB_AVAILABLE:
            return
        
        styles = getSampleStyleSheet()
        
        # Header
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Title'],
            fontSize=28,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER
        )
        
        story.append(Paragraph("INVOICE", header_style))
        story.append(Spacer(1, 30))
        
        # Invoice info
        info_data = [
            ['Invoice Number:', self.invoice_number],
            ['Customer:', self.customer['name']],
            ['Address:', self.customer['address']],
            ['Date:', self.customer.get('date', '2024-01-15')]
        ]
        
        for label, value in info_data:
            story.append(Paragraph(f"<b>{label}</b> {value}", styles['Normal']))
        
        story.append(Spacer(1, 30))
        
        # Items table
        table_data = [['Item', 'Quantity', 'Unit Price', 'Total']]
        
        for item in self.items:
            total_price = item['quantity'] * item['price']
            table_data.append([
                item['description'],
                str(item['quantity']),
                f"{self._pdf_engine.format_german_number(item['price'])} €",
                f"{self._pdf_engine.format_german_number(total_price)} €"
            ])
        
        # Add subtotal, tax, and total rows
        table_data.append(['', '', 'Subtotal:', f"{self._pdf_engine.format_german_number(self.subtotal)} €"])
        table_data.append(['', '', f'Tax ({int(self.tax_rate * 100)}%):', f"{self._pdf_engine.format_german_number(self.tax)} €"])
        table_data.append(['', '', '<b>Total:</b>', f"<b>{self._pdf_engine.format_german_number(self.total)} €</b>"])
        
        # Custom table style
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -4), 1, colors.black),
            ('LINEABOVE', (2, -3), (-1, -3), 1, colors.black),
            ('LINEABOVE', (2, -1), (-1, -1), 2, colors.black),
        ]
        
        table = self._pdf_engine.create_table(table_data, style=table_style)
        story.append(table)
        story.append(Spacer(1, 30))
        
        # Payment terms
        story.append(Paragraph("<b>Payment Terms:</b>", styles['Heading3']))
        story.append(Paragraph("Payment due within 30 days.", styles['Normal']))


def example_4_invoice():
    """Example 4: Professional invoice"""
    print("\nExample 4: Professional Invoice")
    
    if not REPORTLAB_AVAILABLE:
        print("⚠ Skipped (reportlab not installed)")
        return
    
    customer = {
        'name': 'ABC Solar GmbH',
        'address': 'Musterstraße 123, 12345 Berlin',
        'date': '2024-01-15'
    }
    
    items = [
        {'description': 'Solar Panel 400W', 'quantity': 30, 'price': 250.00},
        {'description': 'Inverter 10kW', 'quantity': 1, 'price': 2500.00},
        {'description': 'Mounting System', 'quantity': 1, 'price': 1500.00},
        {'description': 'Installation', 'quantity': 1, 'price': 3000.00}
    ]
    
    invoice = InvoiceDocument(
        invoice_number='INV-2024-001',
        customer=customer,
        items=items
    )
    
    metadata = PDFMetadata(
        title='Invoice INV-2024-001',
        author='Solar Calculator Pro',
        subject='Solar System Installation',
        keywords=['invoice', 'solar', 'installation']
    )
    
    invoice.set_pdf_metadata(metadata)
    invoice.save_pdf("example_4_invoice.pdf")
    
    print("✓ Created example_4_invoice.pdf")


def example_5_base64_encoding():
    """Example 5: Base64 encoding for API transmission"""
    print("\nExample 5: Base64 Encoding")
    
    doc = SimplePDFDocument(
        title="API Document",
        content="This document will be base64-encoded for API transmission."
    )
    
    # Get base64-encoded PDF
    pdf_base64 = doc.to_pdf_base64()
    
    print(f"✓ Generated base64-encoded PDF ({len(pdf_base64)} characters)")
    print(f"  First 100 characters: {pdf_base64[:100]}...")
    
    # Decode and save
    import base64
    pdf_bytes = base64.b64decode(pdf_base64)
    
    with open("example_5_base64.pdf", "wb") as f:
        f.write(pdf_bytes)
    
    print("✓ Decoded and saved example_5_base64.pdf")


def example_6_german_formatting():
    """Example 6: German number formatting showcase"""
    print("\nExample 6: German Number Formatting")
    
    engine = PDFRenderingEngine()
    
    test_numbers = [
        0,
        1,
        10,
        100,
        1000,
        10000,
        100000,
        1000000,
        0.5,
        0.99,
        1234.56,
        9999.99,
        123456.789
    ]
    
    print("\nNumber Formatting Examples:")
    print("-" * 50)
    for num in test_numbers:
        formatted = engine.format_german_number(num)
        print(f"{num:>15} → {formatted:>20}")
    
    # Create PDF with formatted numbers
    data = {
        "Small Number": 0.5,
        "Medium Number": 1234.56,
        "Large Number": 1000000.99,
        "Very Large": 123456789.12
    }
    
    pdf_bytes = create_pdf_from_dict(data, title="German Number Formatting")
    
    with open("example_6_formatting.pdf", "wb") as f:
        f.write(pdf_bytes)
    
    print("\n✓ Created example_6_formatting.pdf")


def run_all_examples():
    """Run all examples"""
    print("=" * 60)
    print("PDF Byte Generation Examples")
    print("=" * 60)
    
    if not REPORTLAB_AVAILABLE:
        print("\n⚠ WARNING: reportlab not installed")
        print("Some examples will be skipped.")
        print("Install with: pip install reportlab\n")
    
    example_1_simple_text_pdf()
    example_2_dictionary_pdf()
    example_3_solar_report()
    example_4_invoice()
    example_5_base64_encoding()
    example_6_german_formatting()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_examples()
