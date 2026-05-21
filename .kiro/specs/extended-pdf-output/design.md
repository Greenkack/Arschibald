# Design Document: Erweiterte PDF-Ausgabe

## Overview

Die erweiterte PDF-Ausgabe erweitert das bestehende 8-Seiten-PDF-System um optionale Zusatzseiten ab Seite 9. Das System integriert Finanzierungsdetails, Produktdatenblätter, Firmendokumente und alle verfügbaren Diagramme/Visualisierungen. Die Architektur basiert auf einem modularen Ansatz, der die bestehende Funktionalität nicht beeinträchtigt.

**Kernprinzipien:**

- Optionale Aktivierung (Standard: deaktiviert)
- Modularer Aufbau (jede Komponente kann einzeln aktiviert werden)
- Verwendung nur echter Keys aus dem System
- Robuste Fehlerbehandlung mit Fallbacks
- Performance-Optimierung durch Caching und effizientes Merging

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Extended PDF Generation Flow                  │
└─────────────────────────────────────────────────────────────────┘

1. PDF UI (pdf_ui.py)
   ├─ Standard Options (existing)
   └─ Extended Options (NEW)
      ├─ Enable Extended Output Checkbox
      ├─ Financing Details Section
      ├─ Product Datasheets Selection
      ├─ Company Documents Selection
      └─ Charts & Visualizations Selection
         ├─ 2D Charts (existing)
         ├─ 3D Charts (existing)
         └─ PV Visuals (existing)

2. PDF Generator (pdf_generator.py)
   ├─ Generate Standard 8-Page PDF
   └─ IF extended_output_enabled:
      ├─ Append Financing Pages (NEW)
      ├─ Append Product Datasheets (NEW)
      ├─ Append Company Documents (NEW)
      └─ Append Chart Pages (NEW)

3. Extended PDF Module (extended_pdf_generator.py) - NEW
   ├─ FinancingPageGenerator
   ├─ ProductDatasheetMerger
   ├─ CompanyDocumentMerger
   └─ ChartPageGenerator


4. PDF Merger (pdf_template_engine/merger.py)
   ├─ merge_first_eight_pages() (existing)
   └─ append_additional_pages() (NEW)
      └─ Merges extended pages with proper page numbering
```

### Component Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Extended PDF Components                   │
└──────────────────────────────────────────────────────────────┘

extended_pdf_generator.py (NEW)
├─ ExtendedPDFGenerator (Main Class)
│  ├─ __init__(offer_data, analysis_results, options)
│  ├─ generate_extended_pages() -> bytes
│  └─ merge_with_base_pdf(base_pdf_bytes) -> bytes
│
├─ FinancingPageGenerator
│  ├─ generate_financing_page(financing_data) -> bytes
│  ├─ _create_financing_table(options)
│  ├─ _calculate_monthly_rates(amount, rate, months)
│  └─ _format_financing_details(data)
│
├─ ProductDatasheetMerger
│  ├─ merge_datasheets(datasheet_ids) -> bytes
│  ├─ _load_datasheet_from_db(id) -> bytes
│  ├─ _convert_image_to_pdf(image_bytes) -> bytes
│  └─ _merge_pdf_pages(pdf_list) -> bytes
│
├─ CompanyDocumentMerger
│  ├─ merge_documents(document_ids) -> bytes
│  ├─ _load_document_from_db(id) -> bytes
│  └─ _handle_document_format(doc_bytes, format)
│
└─ ChartPageGenerator
   ├─ generate_chart_pages(chart_selection) -> bytes
   ├─ _get_chart_from_analysis(chart_key) -> bytes
   ├─ _create_chart_layout(charts, layout_type)
   └─ _render_chart_page(charts, layout) -> bytes
```

## Components and Interfaces

### 1. Extended PDF UI Module (pdf_ui.py - Extensions)

**New UI Section: Extended Output Options**

```python
def render_extended_pdf_options(
    texts: dict,
    analysis_results: dict,
    project_data: dict,
    active_company_id: int
) -> dict:
    """Renders the extended PDF options UI section.
    
    Returns:
        dict with selected options for extended output
    """
    options = {
        'enabled': False,
        'financing_details': False,
        'product_datasheets': [],
        'company_documents': [],
        'selected_charts': [],
        'chart_layout': 'one_per_page'
    }
    
    # Main toggle
    options['enabled'] = st.checkbox(
        "🔧 Erweiterte PDF-Ausgabe aktivieren",
        help="Fügt zusätzliche Seiten ab Seite 9 hinzu"
    )
    
    if not options['enabled']:
        return options
    
    # Financing section
    with st.expander("💰 Finanzierungsdetails"):
        options['financing_details'] = st.checkbox(
            "Finanzierungsoptionen einbinden"
        )
    
    # Product datasheets section
    with st.expander("📄 Produktdatenblätter"):
        options['product_datasheets'] = render_datasheet_selection()
    
    # Company documents section
    with st.expander("🏢 Firmendokumente"):
        options['company_documents'] = render_document_selection(
            active_company_id
        )
    
    # Charts section
    with st.expander("📊 Diagramme & Visualisierungen"):
        options['selected_charts'] = render_chart_selection(
            analysis_results
        )
        options['chart_layout'] = st.selectbox(
            "Layout",
            ['one_per_page', 'two_per_page', 'four_per_page']
        )
    
    return options
```

**Chart Selection UI with Categories**

```python
def render_chart_selection(analysis_results: dict) -> list[str]:
    """Renders categorized chart selection UI.
    
    Returns:
        List of selected chart keys
    """
    # Chart categories mapping
    CHART_CATEGORIES = {
        'Wirtschaftlichkeit': [
            'cumulative_cashflow_chart_bytes',
            'cost_projection_chart_bytes',
            'break_even_chart_bytes',
            'amortisation_chart_bytes',
            'project_roi_matrix_switcher_chart_bytes',
            'roi_comparison_switcher_chart_bytes'
        ],
        'Produktion & Verbrauch': [
            'monthly_prod_cons_chart_bytes',
            'yearly_production_chart_bytes',
            'daily_production_switcher_chart_bytes',
            'weekly_production_switcher_chart_bytes',
            'yearly_production_switcher_chart_bytes',
            'prod_vs_cons_switcher_chart_bytes'
        ],
        'Eigenverbrauch & Autarkie': [
            'consumption_coverage_pie_chart_bytes',
            'pv_usage_pie_chart_bytes',
            'storage_effect_switcher_chart_bytes',
            'selfuse_stack_switcher_chart_bytes',
            'selfuse_ratio_switcher_chart_bytes'
        ],
        'Finanzielle Analyse': [
            'feed_in_revenue_switcher_chart_bytes',
            'income_projection_switcher_chart_bytes',
            'tariff_cube_switcher_chart_bytes',
            'tariff_comparison_switcher_chart_bytes',
            'cost_growth_switcher_chart_bytes'
        ],
        'CO2 & Umwelt': [
            'co2_savings_value_switcher_chart_bytes'
        ],
        'Vergleiche & Szenarien': [
            'scenario_comparison_switcher_chart_bytes',
            'investment_value_switcher_chart_bytes'
        ]
    }
    
    selected_charts = []
    
    # Category tabs
    tabs = st.tabs(list(CHART_CATEGORIES.keys()) + ["Alle"])
    
    for idx, (category, chart_keys) in enumerate(CHART_CATEGORIES.items()):
        with tabs[idx]:
            st.markdown(f"**{category}**")
            
            # Select all button for category
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button(
                    "Alle auswählen",
                    key=f"select_all_{category}"
                ):
                    for key in chart_keys:
                        if key in analysis_results:
                            if key not in selected_charts:
                                selected_charts.append(key)
            
            # Individual chart checkboxes
            for chart_key in chart_keys:
                if chart_key in analysis_results:
                    chart_name = _get_chart_friendly_name(chart_key)
                    
                    # Show thumbnail preview
                    col_check, col_preview = st.columns([3, 1])
                    
                    with col_check:
                        if st.checkbox(
                            chart_name,
                            key=f"chart_{chart_key}"
                        ):
                            if chart_key not in selected_charts:
                                selected_charts.append(chart_key)
                    
                    with col_preview:
                        if st.button(
                            "👁️",
                            key=f"preview_{chart_key}",
                            help="Vorschau"
                        ):
                            _show_chart_preview(
                                analysis_results[chart_key]
                            )
                else:
                    st.text(
                        f"⚠️ {_get_chart_friendly_name(chart_key)} "
                        "(nicht verfügbar)"
                    )
    
    # "Alle" tab
    with tabs[-1]:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Alle auswählen"):
                selected_charts = [
                    k for k in analysis_results.keys()
                    if k.endswith('_chart_bytes')
                ]
        with col2:
            if st.button("Alle abwählen"):
                selected_charts = []
        
        st.info(f"✓ {len(selected_charts)} Diagramme ausgewählt")
    
    return selected_charts
```

### 2. Extended PDF Generator Module (NEW)

**File: `extended_pdf_generator.py`**

```python
"""
Extended PDF Generator Module

Handles generation of additional pages for extended PDF output including:
- Financing details
- Product datasheets
- Company documents
- Charts and visualizations
"""

from typing import Any
import io
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor


class ExtendedPDFGenerator:
    """Main class for generating extended PDF pages."""
    
    def __init__(
        self,
        offer_data: dict[str, Any],
        analysis_results: dict[str, Any],
        options: dict[str, Any],
        theme: dict[str, Any]
    ):
        self.offer_data = offer_data
        self.analysis_results = analysis_results
        self.options = options
        self.theme = theme
        self.width, self.height = A4
    
    def generate_extended_pages(self) -> bytes:
        """Generates all extended pages based on options.
        
        Returns:
            PDF bytes containing all extended pages
        """
        writer = PdfWriter()
        
        try:
            # Add financing pages
            if self.options.get('financing_details'):
                financing_pages = self._generate_financing_pages()
                self._add_pages_to_writer(writer, financing_pages)
            
            # Add product datasheets
            if self.options.get('product_datasheets'):
                datasheet_pages = self._merge_product_datasheets()
                self._add_pages_to_writer(writer, datasheet_pages)
            
            # Add company documents
            if self.options.get('company_documents'):
                document_pages = self._merge_company_documents()
                self._add_pages_to_writer(writer, document_pages)
            
            # Add chart pages
            if self.options.get('selected_charts'):
                chart_pages = self._generate_chart_pages()
                self._add_pages_to_writer(writer, chart_pages)
            
            # Write to bytes
            output = io.BytesIO()
            writer.write(output)
            return output.getvalue()
        
        except Exception as e:
            print(f"Error generating extended pages: {e}")
            return b''  # Return empty bytes on error
```

    def _generate_financing_pages(self) -> bytes:
        """Generates financing detail pages."""
        generator = FinancingPageGenerator(
            self.offer_data,
            self.theme
        )
        return generator.generate()
    
    def _merge_product_datasheets(self) -> bytes:
        """Merges selected product datasheets."""
        merger = ProductDatasheetMerger()
        return merger.merge(
            self.options['product_datasheets']
        )
    
    def _merge_company_documents(self) -> bytes:
        """Merges selected company documents."""
        merger = CompanyDocumentMerger()
        return merger.merge(
            self.options['company_documents']
        )
    
    def _generate_chart_pages(self) -> bytes:
        """Generates pages with charts."""
        generator = ChartPageGenerator(
            self.analysis_results,
            self.options['chart_layout'],
            self.theme
        )
        return generator.generate(
            self.options['selected_charts']
        )
    
    def _add_pages_to_writer(
        self,
        writer: PdfWriter,
        pdf_bytes: bytes
    ) -> None:
        """Adds pages from PDF bytes to writer."""
        if not pdf_bytes:
            return
        
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            for page in reader.pages:
                writer.add_page(page)
        except Exception as e:
            print(f"Error adding pages: {e}")

class FinancingPageGenerator:
    """Generates financing detail pages."""

    def __init__(self, offer_data: dict, theme: dict):
        self.offer_data = offer_data
        self.theme = theme
        self.width, self.height = A4
    
    def generate(self) -> bytes:
        """Generates financing pages.
        
        Returns:
            PDF bytes with financing details
        """
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # Get financing data from offer_data
        financing_options = self._get_financing_options()
        
        if not financing_options:
            return b''
        
        # Page 1: Financing Overview
        self._draw_financing_overview(c, financing_options)
        c.showPage()
        
        # Page 2: Detailed Financing Calculations
        self._draw_financing_details(c, financing_options)
        c.showPage()
        
        c.save()
        return buffer.getvalue()
    
    def _get_financing_options(self) -> list[dict]:
        """Extracts financing options from offer data.
        
        Uses real keys from payment_terms configuration.
        """
        # Load from admin settings
        from database import load_admin_setting
        
        payment_terms = load_admin_setting('payment_terms', {})
        payment_options = payment_terms.get('payment_options', [])
        
        # Filter for financing options
        financing_opts = [
            opt for opt in payment_options
            if opt.get('payment_type') == 'financing'
            and opt.get('enabled', False)
        ]
        
        return financing_opts
    
    def _draw_financing_overview(
        self,
        c: canvas.Canvas,
        options: list[dict]
    ) -> None:
        """Draws financing overview page."""
        # Title
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(
            HexColor(self.theme['colors']['primary'])
        )
        c.drawString(2*cm, self.height - 3*cm, "Finanzierungsoptionen")
        
        # Subtitle
        c.setFont("Helvetica", 12)
        c.setFillColor(HexColor("#000000"))
        c.drawString(
            2*cm,
            self.height - 4*cm,
            "Flexible Zahlungsmöglichkeiten für Ihre Photovoltaikanlage"
        )
        
        # Draw financing options table
        y_pos = self.height - 6*cm
        
        for idx, option in enumerate(options):
            self._draw_financing_option_box(c, option, y_pos)
            y_pos -= 5*cm
            
            if y_pos < 3*cm:
                break  # Page full
    
    def _draw_financing_option_box(
        self,
        c: canvas.Canvas,
        option: dict,
        y_pos: float
    ) -> None:
        """Draws a single financing option box."""
        # Box background
        c.setFillColor(HexColor("#F5F5F5"))
        c.rect(2*cm, y_pos, self.width - 4*cm, 4*cm, fill=1)
        
        # Option name
        c.setFillColor(HexColor("#000000"))
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2.5*cm, y_pos + 3.5*cm, option.get('name', 'N/A'))
        
        # Description
        c.setFont("Helvetica", 10)
        c.drawString(
            2.5*cm,
            y_pos + 3*cm,
            option.get('description', '')
        )
        
        # Financing details
        financing_details = option.get('financing_options', [])
        if financing_details:
            detail = financing_details[0]  # First option
            
            y_detail = y_pos + 2.2*cm
            c.setFont("Helvetica", 9)
            
            # Duration
            duration = detail.get('duration_months', 0)
            c.drawString(
                2.5*cm,
                y_detail,
                f"Laufzeit: {duration} Monate ({duration//12} Jahre)"
            )
            
            # Interest rate
            rate = detail.get('interest_rate', 0)
            c.drawString(
                2.5*cm,
                y_detail - 0.5*cm,
                f"Zinssatz: {rate}% p.a."
            )
            
            # Calculate monthly rate (example)
            total_amount = self.offer_data.get('grand_total', 0)
            monthly_rate = self._calculate_monthly_rate(
                total_amount,
                rate,
                duration
            )
            
            c.setFont("Helvetica-Bold", 11)
            c.drawString(
                2.5*cm,
                y_detail - 1.2*cm,
                f"Monatliche Rate: {monthly_rate:,.2f} €"
            )
    
    def _calculate_monthly_rate(
        self,
        amount: float,
        annual_rate: float,
        months: int
    ) -> float:
        """Calculates monthly payment using annuity formula."""
        if months == 0 or annual_rate == 0:
            return amount / max(months, 1)
        
        monthly_rate = annual_rate / 100 / 12
        factor = (1 + monthly_rate) ** months
        monthly_payment = amount * (
            monthly_rate * factor / (factor - 1)
        )
        
        return monthly_payment

```


    
    def _draw_financing_details(
        self,
        c: canvas.Canvas,
        options: list[dict]
    ) -> None:
        """Draws detailed financing calculations page."""
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(
            2*cm,
            self.height - 3*cm,
            "Detaillierte Finanzierungsberechnung"
        )
        
        # Detailed table for each option
        y_pos = self.height - 5*cm
        
        for option in options:
            financing_opts = option.get('financing_options', [])
            
            for fin_opt in financing_opts:
                if y_pos < 5*cm:
                    c.showPage()
                    y_pos = self.height - 3*cm
                
                self._draw_financing_calculation_table(
                    c,
                    option,
                    fin_opt,
                    y_pos
                )
                y_pos -= 8*cm
    
    def _draw_financing_calculation_table(
        self,
        c: canvas.Canvas,
        option: dict,
        fin_opt: dict,
        y_pos: float
    ) -> None:
        """Draws detailed calculation table for one financing option."""
        from reportlab.platypus import Table, TableStyle
        from reportlab.lib import colors
        
        # Calculate values
        total_amount = self.offer_data.get('grand_total', 0)
        duration = fin_opt.get('duration_months', 60)
        rate = fin_opt.get('interest_rate', 0)
        monthly_rate = self._calculate_monthly_rate(
            total_amount,
            rate,
            duration
        )
        total_payment = monthly_rate * duration
        total_interest = total_payment - total_amount
        
        # Create table data
        data = [
            ['Position', 'Wert'],
            ['Finanzierungsbetrag', f'{total_amount:,.2f} €'],
            ['Laufzeit', f'{duration} Monate'],
            ['Zinssatz p.a.', f'{rate}%'],
            ['Monatliche Rate', f'{monthly_rate:,.2f} €'],
            ['Gesamtzahlung', f'{total_payment:,.2f} €'],
            ['Zinskosten gesamt', f'{total_interest:,.2f} €']
        ]
        
        # Draw table (simplified - in real implementation use Table)
        c.setFont("Helvetica", 10)
        for idx, row in enumerate(data):
            y = y_pos - (idx * 0.7*cm)
            c.drawString(2.5*cm, y, row[0])
            c.drawString(10*cm, y, row[1])


class ProductDatasheetMerger:
    """Merges product datasheets from database."""
    
    def merge(self, datasheet_ids: list[int]) -> bytes:
        """Merges selected product datasheets.
        
        Args:
            datasheet_ids: List of product IDs with datasheets
        
        Returns:
            PDF bytes with merged datasheets
        """
        if not datasheet_ids:
            return b''
        
        writer = PdfWriter()
        
        for product_id in datasheet_ids:
            try:
                datasheet_bytes = self._load_datasheet(product_id)
                if datasheet_bytes:
                    reader = PdfReader(io.BytesIO(datasheet_bytes))
                    for page in reader.pages:
                        writer.add_page(page)
            except Exception as e:
                print(
                    f"Error loading datasheet for product {product_id}: {e}"
                )
                continue
        
        output = io.BytesIO()
        writer.write(output)
        return output.getvalue()
    
    def _load_datasheet(self, product_id: int) -> bytes | None:
        """Loads product datasheet from database.
        
        Uses real database structure from product_db.py
        """
        try:
            from product_db import get_product_by_id
            
            product = get_product_by_id(product_id)
            if not product:
                return None
            
            # Check if product has datasheet
            datasheet_path = product.get('datasheet_path')
            if not datasheet_path:
                return None
            
            # Load file
            import os
            if os.path.exists(datasheet_path):
                with open(datasheet_path, 'rb') as f:
                    return f.read()
            
            return None
        
        except Exception as e:
            print(f"Error loading datasheet: {e}")
            return None


class CompanyDocumentMerger:
    """Merges company documents from database."""
    
    def merge(self, document_ids: list[int]) -> bytes:
        """Merges selected company documents.
        
        Args:
            document_ids: List of company document IDs
        
        Returns:
            PDF bytes with merged documents
        """
        if not document_ids:
            return b''
        
        writer = PdfWriter()
        
        for doc_id in document_ids:
            try:
                doc_bytes = self._load_document(doc_id)
                if doc_bytes:
                    reader = PdfReader(io.BytesIO(doc_bytes))
                    for page in reader.pages:
                        writer.add_page(page)
            except Exception as e:
                print(f"Error loading document {doc_id}: {e}")
                continue
        
        output = io.BytesIO()
        writer.write(output)
        return output.getvalue()
    
    def _load_document(self, doc_id: int) -> bytes | None:
        """Loads company document from database.
        
        Uses real database structure from database.py
        """
        try:
            from database import get_company_document_file_path
            
            file_path = get_company_document_file_path(doc_id)
            if not file_path:
                return None
            
            import os
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    return f.read()
            
            return None
        
        except Exception as e:
            print(f"Error loading document: {e}")
            return None
```

class ChartPageGenerator:
    """Generates pages with charts and visualizations."""

    def __init__(
        self,
        analysis_results: dict,
        layout: str,
        theme: dict
    ):
        self.analysis_results = analysis_results
        self.layout = layout
        self.theme = theme
        self.width, self.height = A4
    
    def generate(self, chart_keys: list[str]) -> bytes:
        """Generates pages with selected charts.
        
        Args:
            chart_keys: List of chart keys from analysis_results
        
        Returns:
            PDF bytes with chart pages
        """
        if not chart_keys:
            return b''
        
        # Group charts by layout
        if self.layout == 'one_per_page':
            return self._generate_one_per_page(chart_keys)
        elif self.layout == 'two_per_page':
            return self._generate_two_per_page(chart_keys)
        elif self.layout == 'four_per_page':
            return self._generate_four_per_page(chart_keys)
        else:
            return self._generate_one_per_page(chart_keys)
    
    def _generate_one_per_page(self, chart_keys: list[str]) -> bytes:
        """Generates one chart per page."""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        for chart_key in chart_keys:
            chart_bytes = self.analysis_results.get(chart_key)
            if not chart_bytes:
                continue
            
            # Draw chart title
            chart_name = self._get_chart_name(chart_key)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(2*cm, self.height - 2*cm, chart_name)
            
            # Draw chart image
            try:
                from reportlab.lib.utils import ImageReader
                img = ImageReader(io.BytesIO(chart_bytes))
                
                # Calculate dimensions (maintain aspect ratio)
                img_width = self.width - 4*cm
                img_height = self.height - 6*cm
                
                c.drawImage(
                    img,
                    2*cm,
                    3*cm,
                    width=img_width,
                    height=img_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )
            except Exception as e:
                print(f"Error drawing chart {chart_key}: {e}")
                c.drawString(
                    2*cm,
                    self.height / 2,
                    f"Fehler beim Laden des Diagramms: {chart_name}"
                )
            
            c.showPage()
        
        c.save()
        return buffer.getvalue()
    
    def _generate_two_per_page(self, chart_keys: list[str]) -> bytes:
        """Generates two charts per page (2x1 layout)."""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        for i in range(0, len(chart_keys), 2):
            # Top chart
            if i < len(chart_keys):
                self._draw_chart_in_area(
                    c,
                    chart_keys[i],
                    2*cm,
                    self.height / 2 + 1*cm,
                    self.width - 4*cm,
                    self.height / 2 - 3*cm
                )
            
            # Bottom chart
            if i + 1 < len(chart_keys):
                self._draw_chart_in_area(
                    c,
                    chart_keys[i + 1],
                    2*cm,
                    2*cm,
                    self.width - 4*cm,
                    self.height / 2 - 3*cm
                )
            
            c.showPage()
        
        c.save()
        return buffer.getvalue()
    
    def _generate_four_per_page(self, chart_keys: list[str]) -> bytes:
        """Generates four charts per page (2x2 layout)."""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        for i in range(0, len(chart_keys), 4):
            # Top-left
            if i < len(chart_keys):
                self._draw_chart_in_area(
                    c,
                    chart_keys[i],
                    2*cm,
                    self.height / 2 + 1*cm,
                    self.width / 2 - 3*cm,
                    self.height / 2 - 3*cm
                )
            
            # Top-right
            if i + 1 < len(chart_keys):
                self._draw_chart_in_area(
                    c,
                    chart_keys[i + 1],
                    self.width / 2 + 1*cm,
                    self.height / 2 + 1*cm,
                    self.width / 2 - 3*cm,
                    self.height / 2 - 3*cm
                )
            
            # Bottom-left
            if i + 2 < len(chart_keys):
                self._draw_chart_in_area(
                    c,
                    chart_keys[i + 2],
                    2*cm,
                    2*cm,
                    self.width / 2 - 3*cm,
                    self.height / 2 - 3*cm
                )
            
            # Bottom-right
            if i + 3 < len(chart_keys):
                self._draw_chart_in_area(
                    c,
                    chart_keys[i + 3],
                    self.width / 2 + 1*cm,
                    2*cm,
                    self.width / 2 - 3*cm,
                    self.height / 2 - 3*cm
                )
            
            c.showPage()
        
        c.save()
        return buffer.getvalue()
    
    def _draw_chart_in_area(
        self,
        c: canvas.Canvas,
        chart_key: str,
        x: float,
        y: float,
        width: float,
        height: float
    ) -> None:
        """Draws a chart in a specific area."""
        chart_bytes = self.analysis_results.get(chart_key)
        if not chart_bytes:
            return
        
        # Draw title
        chart_name = self._get_chart_name(chart_key)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x, y + height + 0.3*cm, chart_name)
        
        # Draw chart
        try:
            from reportlab.lib.utils import ImageReader
            img = ImageReader(io.BytesIO(chart_bytes))
            
            c.drawImage(
                img,
                x,
                y,
                width=width,
                height=height,
                preserveAspectRatio=True,
                mask='auto'
            )
        except Exception as e:
            print(f"Error drawing chart {chart_key}: {e}")
            c.setFont("Helvetica", 8)
            c.drawString(x, y + height / 2, "Fehler beim Laden")
    
    def _get_chart_name(self, chart_key: str) -> str:
        """Gets friendly name for chart key."""
        # Map from chart_key_to_friendly_name_map in pdf_generator.py
        CHART_NAMES = {
            'monthly_prod_cons_chart_bytes': 'Monatliche Produktion/Verbrauch',
            'cost_projection_chart_bytes': 'Stromkosten-Hochrechnung',
            'cumulative_cashflow_chart_bytes': 'Kumulierter Cashflow',
            'consumption_coverage_pie_chart_bytes': 'Verbrauchsdeckung',
            'pv_usage_pie_chart_bytes': 'PV-Nutzung',
            'daily_production_switcher_chart_bytes': 'Tagesproduktion (3D)',
            'weekly_production_switcher_chart_bytes': 'Wochenproduktion (3D)',
            'yearly_production_switcher_chart_bytes': 'Jahresproduktion (3D)',
            'project_roi_matrix_switcher_chart_bytes': 'Projektrendite-Matrix (3D)',
            'feed_in_revenue_switcher_chart_bytes': 'Einspeisevergütung (3D)',
            'prod_vs_cons_switcher_chart_bytes': 'Produktion vs. Verbrauch (3D)',
            'tariff_cube_switcher_chart_bytes': 'Tarifvergleich (3D)',
            'co2_savings_value_switcher_chart_bytes': 'CO2-Ersparnis (3D)',
            'investment_value_switcher_chart_bytes': 'Investitionsnutzwert (3D)',
            'storage_effect_switcher_chart_bytes': 'Speicherwirkung (3D)',
            'selfuse_stack_switcher_chart_bytes': 'Eigenverbrauch (3D)',
            'cost_growth_switcher_chart_bytes': 'Stromkostensteigerung (3D)',
            'selfuse_ratio_switcher_chart_bytes': 'Eigenverbrauchsgrad (3D)',
            'roi_comparison_switcher_chart_bytes': 'ROI-Vergleich (3D)',
            'scenario_comparison_switcher_chart_bytes': 'Szenarienvergleich (3D)',
            'tariff_comparison_switcher_chart_bytes': 'Vorher/Nachher (3D)',
            'income_projection_switcher_chart_bytes': 'Einnahmenprognose (3D)',
            'yearly_production_chart_bytes': 'Jahresproduktion',
            'break_even_chart_bytes': 'Break-Even-Analyse',
            'amortisation_chart_bytes': 'Amortisation'
        }
        
        return CHART_NAMES.get(chart_key, chart_key)

```



## Data Models

### Extended PDF Options Model

```python
ExtendedPDFOptions = {
    'enabled': bool,  # Master toggle
    'financing_details': bool,  # Include financing pages
    'product_datasheets': list[int],  # Product IDs
    'company_documents': list[int],  # Document IDs
    'selected_charts': list[str],  # Chart keys
    'chart_layout': str,  # 'one_per_page', 'two_per_page', 'four_per_page'
    'page_order': list[str]  # Order of sections
}
```

### Financing Data Model (from payment_terms)

```python
FinancingOption = {
    'id': str,
    'name': str,
    'description': str,
    'payment_type': 'financing',
    'enabled': bool,
    'financing_options': list[FinancingDetail]
}

FinancingDetail = {
    'name': str,
    'duration_months': int,
    'interest_rate': float,
    'monthly_fee': float,
    'min_amount': float,
    'max_amount': float
}
```

### Chart Selection Model

```python
ChartSelection = {
    'chart_key': str,  # Key from analysis_results
    'category': str,  # Category name
    'friendly_name': str,  # Display name
    'available': bool,  # Whether chart exists in analysis_results
    'selected': bool  # User selection
}
```

## Error Handling

### Graceful Degradation Strategy

```python
def generate_extended_pdf_safe(
    base_pdf_bytes: bytes,
    options: dict
) -> bytes:
    """Safely generates extended PDF with fallback.
    
    If extended generation fails, returns base PDF unchanged.
    """
    try:
        if not options.get('enabled'):
            return base_pdf_bytes
        
        # Generate extended pages
        extended_pages = generate_extended_pages(options)
        
        if not extended_pages:
            print("Warning: No extended pages generated")
            return base_pdf_bytes
        
        # Merge with base PDF
        merged_pdf = merge_pdfs(base_pdf_bytes, extended_pages)
        
        return merged_pdf
    
    except Exception as e:
        print(f"Error in extended PDF generation: {e}")
        print("Falling back to base PDF")
        return base_pdf_bytes
```

### Error Logging

```python
class ExtendedPDFLogger:
    """Logs errors and warnings during extended PDF generation."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def log_error(self, component: str, message: str):
        """Logs an error."""
        self.errors.append({
            'component': component,
            'message': message,
            'timestamp': datetime.now()
        })
        print(f"ERROR [{component}]: {message}")
    
    def log_warning(self, component: str, message: str):
        """Logs a warning."""
        self.warnings.append({
            'component': component,
            'message': message,
            'timestamp': datetime.now()
        })
        print(f"WARNING [{component}]: {message}")
    
    def get_summary(self) -> dict:
        """Returns summary of errors and warnings."""
        return {
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'errors': self.errors,
            'warnings': self.warnings
        }
```

## Testing Strategy

### Unit Tests

```python
def test_extended_pdf_options_parsing():
    """Test that options are correctly parsed."""
    options = {
        'enabled': True,
        'financing_details': True,
        'selected_charts': ['chart1', 'chart2']
    }
    
    assert options['enabled'] == True
    assert len(options['selected_charts']) == 2

def test_financing_page_generation():
    """Test financing page generation."""
    generator = FinancingPageGenerator(offer_data, theme)
    pdf_bytes = generator.generate()
    
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 0

def test_chart_layout_one_per_page():
    """Test one chart per page layout."""
    generator = ChartPageGenerator(analysis_results, 'one_per_page', theme)
    pdf_bytes = generator.generate(['chart1', 'chart2'])
    
    # Should have 2 pages
    reader = PdfReader(io.BytesIO(pdf_bytes))
    assert len(reader.pages) == 2
```

### Integration Tests

```python
def test_full_extended_pdf_generation():
    """Test complete extended PDF generation."""
    options = {
        'enabled': True,
        'financing_details': True,
        'product_datasheets': [1, 2],
        'company_documents': [1],
        'selected_charts': ['chart1', 'chart2', 'chart3'],
        'chart_layout': 'two_per_page'
    }
    
    base_pdf = generate_base_8_page_pdf()
    extended_pdf = generate_extended_pdf(base_pdf, options)
    
    reader = PdfReader(io.BytesIO(extended_pdf))
    
    # Should have more than 8 pages
    assert len(reader.pages) > 8
```

## Performance Optimization

### Caching Strategy

```python
class ChartCache:
    """Caches rendered charts to avoid re-rendering."""
    
    def __init__(self):
        self._cache = {}
    
    def get(self, chart_key: str) -> bytes | None:
        """Gets cached chart."""
        return self._cache.get(chart_key)
    
    def set(self, chart_key: str, chart_bytes: bytes):
        """Caches chart."""
        self._cache[chart_key] = chart_bytes
    
    def clear(self):
        """Clears cache."""
        self._cache.clear()
```

### Lazy Loading

```python
def load_charts_lazy(chart_keys: list[str]) -> Generator:
    """Lazily loads charts one at a time."""
    for key in chart_keys:
        yield load_chart(key)
```

## Migration Path

### Phase 1: Core Infrastructure

1. Create `extended_pdf_generator.py` module
2. Add UI toggle in `pdf_ui.py`
3. Implement basic page appending in `merger.py`

### Phase 2: Financing Integration

1. Implement `FinancingPageGenerator`
2. Connect to payment_terms configuration
3. Add financing UI section

### Phase 3: Document Integration

1. Implement `ProductDatasheetMerger`
2. Implement `CompanyDocumentMerger`
3. Add document selection UI

### Phase 4: Chart Integration

1. Implement `ChartPageGenerator`
2. Add categorized chart selection UI
3. Implement layout options

### Phase 5: Polish & Testing

1. Add error handling and logging
2. Implement caching
3. Performance optimization
4. Comprehensive testing

## Success Criteria

1. ✅ Extended PDF can be optionally enabled/disabled
2. ✅ Financing details are correctly rendered
3. ✅ Product datasheets are successfully merged
4. ✅ Company documents are successfully merged
5. ✅ All available charts can be selected and rendered
6. ✅ Multiple layout options work correctly
7. ✅ Page numbering is correct throughout
8. ✅ No regression in base 8-page PDF functionality
9. ✅ Performance is acceptable (< 30 seconds for typical extended PDF)
10. ✅ Error handling prevents crashes and provides fallbacks

## Settings & Configuration System

### Admin Settings Structure

```python
# Extended admin_settings structure for PDF & UI configuration

EXTENDED_ADMIN_SETTINGS = {
    # Existing settings...
    'visualization_settings': {
        # Global chart colors
        'global_chart_colors': {
            'primary': '#2563EB',  # blue-600
            'secondary': '#22C55E',  # green-500
            'tertiary': '#F59E0B',  # amber-500
            'background': '#FFFFFF',
            'grid': '#E5E7EB',
            'text': '#1F2937'
        },
        
        # Color palettes library
        'color_palettes': {
            'corporate': {
                'name': 'Corporate',
                'colors': ['#0F172A', '#2563EB', '#64748B', '#94A3B8'],
                'description': 'Professional blue-gray tones'
            },
            'eco': {
                'name': 'Eco',
                'colors': ['#065F46', '#10B981', '#34D399', '#6EE7B7'],
                'description': 'Green tones for sustainability'
            },
            'energy': {
                'name': 'Energy',
                'colors': ['#EA580C', '#F59E0B', '#FCD34D', '#FDE68A'],
                'description': 'Orange-yellow energy tones'
            },
            'accessible': {
                'name': 'Accessible',
                'colors': ['#1E40AF', '#DC2626', '#059669', '#D97706'],
                'description': 'Colorblind-friendly palette'
            }
        },
        
        # Individual chart configurations
        'chart_configs': {
            'monthly_prod_cons_chart': {
                'use_global': True,
                'custom_colors': {
                    'production': '#22C55E',
                    'consumption': '#EF4444'
                },
                'chart_type': 'line',
                'show_markers': True
            },
            'cumulative_cashflow_chart': {
                'use_global': True,
                'custom_colors': {
                    'cashflow': '#2563EB'
                },
                'chart_type': 'line',
                'show_zero_line': True
            },
            # ... more chart configs
        }
    },
    
    # PDF Design Settings
    'pdf_design_settings': {
        'primary_color': '#003366',
        'secondary_color': '#808080',
        'font_family_main': 'Helvetica',
        'font_family_bold': 'Helvetica-Bold',
        'font_sizes': {
            'h1': 18,
            'h2': 14,
            'body': 10,
            'small': 8
        },
        'logo_position': 'top_right',  # 'top_left', 'top_right', 'center'
        'footer_format': 'page_number',  # 'page_number', 'custom', 'none'
        'footer_custom_text': '',
        'header_enabled': True,
        'watermark_enabled': False,
        'watermark_text': 'VERTRAULICH',
        'watermark_opacity': 0.1
    },
    
    # UI Theme Settings
    'ui_theme_settings': {
        'active_theme': 'light',
        'themes': {
            'light': {
                'name': 'Light Theme',
                'primary': '#2563EB',
                'secondary': '#64748B',
                'background': '#FFFFFF',
                'surface': '#F8FAFC',
                'text': '#1E293B',
                'text_secondary': '#64748B'
            },
            'dark': {
                'name': 'Dark Theme',
                'primary': '#3B82F6',
                'secondary': '#94A3B8',
                'background': '#0F172A',
                'surface': '#1E293B',
                'text': '#F1F5F9',
                'text_secondary': '#CBD5E1'
            },
            'corporate': {
                'name': 'Corporate Theme',
                'primary': '#003366',
                'secondary': '#0066CC',
                'background': '#FFFFFF',
                'surface': '#F0F4F8',
                'text': '#1A202C',
                'text_secondary': '#4A5568'
            }
        }
    },
    
    # PDF Layout Options
    'pdf_layout_options': {
        'available_layouts': {
            'standard_8': {
                'name': 'Standard (8 Seiten)',
                'enabled': True,
                'pages': 8,
                'description': 'Standard-Layout mit 8 Seiten'
            },
            'extended': {
                'name': 'Erweitert (mit Zusatzseiten)',
                'enabled': True,
                'base_pages': 8,
                'description': 'Erweiterbares Layout mit optionalen Zusatzseiten'
            },
            'compact': {
                'name': 'Kompakt (6 Seiten)',
                'enabled': False,
                'pages': 6,
                'description': 'Reduziertes Layout für schnelle Angebote'
            }
        },
        'default_layout': 'standard_8'
    },
    
    # PDF Template Management
    'pdf_templates': {
        'active_template': 'default',
        'templates': {
            'default': {
                'name': 'Standard Template',
                'description': 'Standard PDF-Template',
                'template_files': {
                    'normal': 'pdf_templates_static/notext/nt_nt_{:02d}.pdf',
                    'heatpump': 'pdf_templates_static/notext/hp_nt_{:02d}.pdf'
                },
                'coords_files': {
                    'normal': 'coords/seite{}.yml',
                    'heatpump': 'coords_wp/wp_seite{}.yml'
                },
                'preview_image': None
            }
        }
    },
    
    # Design Configuration Versions
    'design_config_versions': {
        'current_version': 'v1.0',
        'versions': {
            'v1.0': {
                'name': 'Default v1.0',
                'created_at': '2025-01-01T00:00:00',
                'config': {
                    # Snapshot of all design settings
                }
            }
        }
    }
}
```

### Settings UI Module

**File: `admin_pdf_settings_ui.py` (NEW)**

```python
"""
Admin UI for PDF & Design Settings

Provides comprehensive configuration interface for:
- PDF design settings
- Chart color configurations
- UI themes
- PDF templates
- Layout options
"""

import streamlit as st
from database import load_admin_setting, save_admin_setting
import json


def render_pdf_settings_ui():
    """Main entry point for PDF settings UI."""
    st.header("📄 PDF & Design Einstellungen")
    
    tabs = st.tabs([
        "PDF Design",
        "Diagramm-Farben",
        "UI Themes",
        "PDF Templates",
        "Layout-Optionen"
    ])
    
    with tabs[0]:
        render_pdf_design_settings()
    
    with tabs[1]:
        render_chart_color_settings()
    
    with tabs[2]:
        render_ui_theme_settings()
    
    with tabs[3]:
        render_pdf_template_settings()
    
    with tabs[4]:
        render_layout_options_settings()


def render_pdf_design_settings():
    """Renders PDF design configuration UI."""
    st.subheader("🎨 PDF Design-Einstellungen")
    
    # Load current settings
    pdf_design = load_admin_setting('pdf_design_settings', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Farben**")
        
        primary_color = st.color_picker(
            "Primärfarbe",
            value=pdf_design.get('primary_color', '#003366'),
            help="Hauptfarbe für Überschriften und Akzente"
        )
        
        secondary_color = st.color_picker(
            "Sekundärfarbe",
            value=pdf_design.get('secondary_color', '#808080'),
            help="Farbe für Tabellen und Hintergründe"
        )
    
    with col2:
        st.markdown("**Schriftarten**")
        
        font_family = st.selectbox(
            "Schriftart",
            options=['Helvetica', 'Times-Roman', 'Courier'],
            index=['Helvetica', 'Times-Roman', 'Courier'].index(
                pdf_design.get('font_family_main', 'Helvetica')
            )
        )
        
        st.markdown("**Schriftgrößen**")
        font_sizes = pdf_design.get('font_sizes', {})
        
        h1_size = st.number_input(
            "H1 Größe",
            value=font_sizes.get('h1', 18),
            min_value=12,
            max_value=24
        )
        
        body_size = st.number_input(
            "Body Größe",
            value=font_sizes.get('body', 10),
            min_value=8,
            max_value=14
        )
    
    st.markdown("**Logo & Layout**")
    
    col3, col4 = st.columns(2)
    
    with col3:
        logo_position = st.selectbox(
            "Logo-Position",
            options=['top_left', 'top_right', 'center'],
            format_func=lambda x: {
                'top_left': 'Oben Links',
                'top_right': 'Oben Rechts',
                'center': 'Zentriert'
            }[x],
            index=['top_left', 'top_right', 'center'].index(
                pdf_design.get('logo_position', 'top_right')
            )
        )
    
    with col4:
        footer_format = st.selectbox(
            "Footer-Format",
            options=['page_number', 'custom', 'none'],
            format_func=lambda x: {
                'page_number': 'Mit Seitenzahl',
                'custom': 'Custom Text',
                'none': 'Kein Footer'
            }[x],
            index=['page_number', 'custom', 'none'].index(
                pdf_design.get('footer_format', 'page_number')
            )
        )
    
    if footer_format == 'custom':
        footer_text = st.text_input(
            "Custom Footer Text",
            value=pdf_design.get('footer_custom_text', '')
        )
    else:
        footer_text = ''
    
    # Watermark settings
    st.markdown("**Wasserzeichen**")
    
    col5, col6 = st.columns(2)
    
    with col5:
        watermark_enabled = st.checkbox(
            "Wasserzeichen aktivieren",
            value=pdf_design.get('watermark_enabled', False)
        )
    
    with col6:
        if watermark_enabled:
            watermark_text = st.text_input(
                "Wasserzeichen Text",
                value=pdf_design.get('watermark_text', 'VERTRAULICH')
            )
            
            watermark_opacity = st.slider(
                "Transparenz",
                min_value=0.0,
                max_value=0.5,
                value=pdf_design.get('watermark_opacity', 0.1),
                step=0.05
            )
        else:
            watermark_text = ''
            watermark_opacity = 0.1
    
    # Save button
    if st.button("💾 Einstellungen speichern", type="primary"):
        updated_settings = {
            'primary_color': primary_color,
            'secondary_color': secondary_color,
            'font_family_main': font_family,
            'font_family_bold': f"{font_family}-Bold",
            'font_sizes': {
                'h1': h1_size,
                'h2': int(h1_size * 0.8),
                'body': body_size,
                'small': int(body_size * 0.8)
            },
            'logo_position': logo_position,
            'footer_format': footer_format,
            'footer_custom_text': footer_text,
            'watermark_enabled': watermark_enabled,
            'watermark_text': watermark_text,
            'watermark_opacity': watermark_opacity
        }
        
        if save_admin_setting('pdf_design_settings', updated_settings):
            st.success("✅ Einstellungen erfolgreich gespeichert!")
            st.rerun()
        else:
            st.error("❌ Fehler beim Speichern der Einstellungen")
    
    # Preview
    with st.expander("👁️ Vorschau"):
        render_pdf_design_preview(pdf_design)


def render_chart_color_settings():
    """Renders chart color configuration UI."""
    st.subheader("📊 Diagramm-Farbeinstellungen")
    
    # Load current settings
    viz_settings = load_admin_setting('visualization_settings', {})
    
    # Tabs for global and individual settings
    sub_tabs = st.tabs(["Globale Farben", "Farbpaletten", "Individuelle Diagramme"])
    
    with sub_tabs[0]:
        render_global_chart_colors(viz_settings)
    
    with sub_tabs[1]:
        render_color_palettes(viz_settings)
    
    with sub_tabs[2]:
        render_individual_chart_configs(viz_settings)


def render_global_chart_colors(viz_settings: dict):
    """Renders global chart color settings."""
    st.markdown("**Globale Diagramm-Farben**")
    st.info("Diese Farben werden für alle Diagramme verwendet, sofern keine individuellen Farben festgelegt sind.")
    
    global_colors = viz_settings.get('global_chart_colors', {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        primary = st.color_picker(
            "Primärfarbe",
            value=global_colors.get('primary', '#2563EB')
        )
        
        secondary = st.color_picker(
            "Sekundärfarbe",
            value=global_colors.get('secondary', '#22C55E')
        )
    
    with col2:
        tertiary = st.color_picker(
            "Tertiärfarbe",
            value=global_colors.get('tertiary', '#F59E0B')
        )
        
        background = st.color_picker(
            "Hintergrund",
            value=global_colors.get('background', '#FFFFFF')
        )
    
    with col3:
        grid = st.color_picker(
            "Gitter",
            value=global_colors.get('grid', '#E5E7EB')
        )
        
        text = st.color_picker(
            "Text",
            value=global_colors.get('text', '#1F2937')
        )
    
    if st.button("💾 Globale Farben speichern"):
        viz_settings['global_chart_colors'] = {
            'primary': primary,
            'secondary': secondary,
            'tertiary': tertiary,
            'background': background,
            'grid': grid,
            'text': text
        }
        
        if save_admin_setting('visualization_settings', viz_settings):
            st.success("✅ Globale Farben gespeichert!")
            st.rerun()


def render_color_palettes(viz_settings: dict):
    """Renders color palette library."""
    st.markdown("**Farbpaletten-Bibliothek**")
    
    palettes = viz_settings.get('color_palettes', {})
    
    # Predefined palettes
    PREDEFINED_PALETTES = {
        'corporate': {
            'name': 'Corporate',
            'colors': ['#0F172A', '#2563EB', '#64748B', '#94A3B8'],
            'description': 'Professionelle Blau-Grau-Töne'
        },
        'eco': {
            'name': 'Eco',
            'colors': ['#065F46', '#10B981', '#34D399', '#6EE7B7'],
            'description': 'Grüne Töne für Nachhaltigkeit'
        },
        'energy': {
            'name': 'Energy',
            'colors': ['#EA580C', '#F59E0B', '#FCD34D', '#FDE68A'],
            'description': 'Orange-Gelb Energie-Töne'
        },
        'accessible': {
            'name': 'Accessible',
            'colors': ['#1E40AF', '#DC2626', '#059669', '#D97706'],
            'description': 'Farbenblind-freundliche Palette'
        }
    }
    
    # Display palettes
    for palette_id, palette in PREDEFINED_PALETTES.items():
        with st.expander(f"🎨 {palette['name']} - {palette['description']}"):
            # Show color swatches
            cols = st.columns(len(palette['colors']))
            for idx, color in enumerate(palette['colors']):
                with cols[idx]:
                    st.color_picker(
                        f"Farbe {idx+1}",
                        value=color,
                        key=f"palette_{palette_id}_{idx}",
                        disabled=True
                    )
            
            if st.button(f"Palette '{palette['name']}' anwenden", key=f"apply_{palette_id}"):
                # Apply palette to global colors
                viz_settings['global_chart_colors'] = {
                    'primary': palette['colors'][0],
                    'secondary': palette['colors'][1] if len(palette['colors']) > 1 else palette['colors'][0],
                    'tertiary': palette['colors'][2] if len(palette['colors']) > 2 else palette['colors'][0],
                    'background': '#FFFFFF',
                    'grid': '#E5E7EB',
                    'text': '#1F2937'
                }
                
                if save_admin_setting('visualization_settings', viz_settings):
                    st.success(f"✅ Palette '{palette['name']}' angewendet!")
                    st.rerun()
```

def render_individual_chart_configs(viz_settings: dict):
    """Renders individual chart configuration UI."""
    st.markdown("**Individuelle Diagramm-Konfiguration**")
    st.info("Hier können Sie für jedes Diagramm individuelle Farben festlegen, die die globalen Einstellungen überschreiben.")

    chart_configs = viz_settings.get('chart_configs', {})
    
    # Chart categories
    CHART_CATEGORIES = {
        'Wirtschaftlichkeit': [
            ('cumulative_cashflow_chart', 'Kumulierter Cashflow'),
            ('cost_projection_chart', 'Stromkosten-Hochrechnung'),
            ('break_even_chart', 'Break-Even-Analyse'),
            ('amortisation_chart', 'Amortisation')
        ],
        'Produktion & Verbrauch': [
            ('monthly_prod_cons_chart', 'Monatliche Produktion/Verbrauch'),
            ('yearly_production_chart', 'Jahresproduktion'),
            ('daily_production_switcher_chart', 'Tagesproduktion (3D)')
        ],
        'Eigenverbrauch': [
            ('consumption_coverage_pie_chart', 'Verbrauchsdeckung'),
            ('pv_usage_pie_chart', 'PV-Nutzung')
        ]
    }
    
    # Select category
    selected_category = st.selectbox(
        "Kategorie wählen",
        options=list(CHART_CATEGORIES.keys())
    )
    
    # Select chart
    charts_in_category = CHART_CATEGORIES[selected_category]
    selected_chart = st.selectbox(
        "Diagramm wählen",
        options=[c[0] for c in charts_in_category],
        format_func=lambda x: next(c[1] for c in charts_in_category if c[0] == x)
    )
    
    # Get current config for selected chart
    chart_config = chart_configs.get(selected_chart, {
        'use_global': True,
        'custom_colors': {}
    })
    
    # Configuration UI
    use_global = st.checkbox(
        "Globale Farben verwenden",
        value=chart_config.get('use_global', True),
        key=f"use_global_{selected_chart}"
    )
    
    if not use_global:
        st.markdown("**Custom-Farben**")
        
        # Different color options based on chart type
        if 'pie' in selected_chart:
            # Pie charts need multiple colors
            num_colors = st.number_input(
                "Anzahl Farben",
                min_value=2,
                max_value=10,
                value=len(chart_config.get('custom_colors', {}).get('segments', [])) or 4
            )
            
            colors = []
            cols = st.columns(min(num_colors, 4))
            for i in range(num_colors):
                with cols[i % 4]:
                    color = st.color_picker(
                        f"Farbe {i+1}",
                        value=chart_config.get('custom_colors', {}).get('segments', ['#2563EB'] * num_colors)[i] if i < len(chart_config.get('custom_colors', {}).get('segments', [])) else '#2563EB',
                        key=f"color_{selected_chart}_{i}"
                    )
                    colors.append(color)
            
            custom_colors = {'segments': colors}
        
        elif 'prod_cons' in selected_chart or 'vs' in selected_chart:
            # Charts with two data series
            col1, col2 = st.columns(2)
            
            with col1:
                production_color = st.color_picker(
                    "Produktion/Serie 1",
                    value=chart_config.get('custom_colors', {}).get('production', '#22C55E'),
                    key=f"prod_{selected_chart}"
                )
            
            with col2:
                consumption_color = st.color_picker(
                    "Verbrauch/Serie 2",
                    value=chart_config.get('custom_colors', {}).get('consumption', '#EF4444'),
                    key=f"cons_{selected_chart}"
                )
            
            custom_colors = {
                'production': production_color,
                'consumption': consumption_color
            }
        
        else:
            # Single color charts
            primary_color = st.color_picker(
                "Primärfarbe",
                value=chart_config.get('custom_colors', {}).get('primary', '#2563EB'),
                key=f"primary_{selected_chart}"
            )
            
            custom_colors = {'primary': primary_color}
        
        # Additional options
        st.markdown("**Zusätzliche Optionen**")
        
        background_color = st.color_picker(
            "Hintergrundfarbe",
            value=chart_config.get('custom_colors', {}).get('background', '#FFFFFF'),
            key=f"bg_{selected_chart}"
        )
        
        grid_color = st.color_picker(
            "Gitterfarbe",
            value=chart_config.get('custom_colors', {}).get('grid', '#E5E7EB'),
            key=f"grid_{selected_chart}"
        )
        
        custom_colors['background'] = background_color
        custom_colors['grid'] = grid_color
    
    else:
        custom_colors = {}
    
    # Save button
    col_save, col_reset = st.columns(2)
    
    with col_save:
        if st.button("💾 Speichern", key=f"save_{selected_chart}"):
            chart_configs[selected_chart] = {
                'use_global': use_global,
                'custom_colors': custom_colors
            }
            
            viz_settings['chart_configs'] = chart_configs
            
            if save_admin_setting('visualization_settings', viz_settings):
                st.success(f"✅ Konfiguration für '{selected_chart}' gespeichert!")
                st.rerun()
    
    with col_reset:
        if st.button("🔄 Auf Global zurücksetzen", key=f"reset_{selected_chart}"):
            if selected_chart in chart_configs:
                del chart_configs[selected_chart]
                viz_settings['chart_configs'] = chart_configs
                
                if save_admin_setting('visualization_settings', viz_settings):
                    st.success("✅ Auf globale Einstellungen zurückgesetzt!")
                    st.rerun()

def render_ui_theme_settings():
    """Renders UI theme configuration."""
    st.subheader("🎨 UI Theme-Einstellungen")

    # Load current settings
    theme_settings = load_admin_setting('ui_theme_settings', {})
    
    # Active theme selection
    active_theme = theme_settings.get('active_theme', 'light')
    themes = theme_settings.get('themes', {})
    
    st.markdown("**Aktives Theme**")
    
    theme_options = list(themes.keys())
    selected_theme = st.selectbox(
        "Theme auswählen",
        options=theme_options,
        index=theme_options.index(active_theme) if active_theme in theme_options else 0,
        format_func=lambda x: themes[x].get('name', x)
    )
    
    if st.button("✅ Theme aktivieren"):
        theme_settings['active_theme'] = selected_theme
        if save_admin_setting('ui_theme_settings', theme_settings):
            st.success(f"✅ Theme '{themes[selected_theme]['name']}' aktiviert!")
            st.rerun()
    
    # Theme preview
    st.markdown("**Theme-Vorschau**")
    render_theme_preview(themes[selected_theme])
    
    # Edit theme
    with st.expander("✏️ Theme bearbeiten"):
        render_theme_editor(selected_theme, themes, theme_settings)

def render_theme_preview(theme: dict):
    """Renders a preview of the theme."""
    st.markdown(f"""
    <div style="
        background-color: {theme['background']};
        padding: 20px;
        border-radius: 8px;
        border: 1px solid {theme['primary']};
    ">
        <h3 style="color: {theme['primary']};">Überschrift (Primärfarbe)</h3>
        <p style="color: {theme['text']};">
            Dies ist ein Beispieltext in der Haupttextfarbe.
        </p>
        <p style="color: {theme['text_secondary']};">
            Dies ist ein Beispieltext in der sekundären Textfarbe.
        </p>
        <div style="
            background-color: {theme['surface']};
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
        ">
            <span style="color: {theme['secondary']};">Surface-Element mit Sekundärfarbe</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_theme_editor(theme_id: str, themes: dict, theme_settings: dict):
    """Renders theme editor UI."""
    theme = themes[theme_id]

    st.markdown(f"**Theme bearbeiten: {theme['name']}**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        primary = st.color_picker(
            "Primärfarbe",
            value=theme['primary'],
            key=f"edit_primary_{theme_id}"
        )
        
        secondary = st.color_picker(
            "Sekundärfarbe",
            value=theme['secondary'],
            key=f"edit_secondary_{theme_id}"
        )
        
        background = st.color_picker(
            "Hintergrund",
            value=theme['background'],
            key=f"edit_bg_{theme_id}"
        )
    
    with col2:
        surface = st.color_picker(
            "Surface",
            value=theme['surface'],
            key=f"edit_surface_{theme_id}"
        )
        
        text = st.color_picker(
            "Text",
            value=theme['text'],
            key=f"edit_text_{theme_id}"
        )
        
        text_secondary = st.color_picker(
            "Text Sekundär",
            value=theme['text_secondary'],
            key=f"edit_text_sec_{theme_id}"
        )
    
    if st.button("💾 Theme speichern", key=f"save_theme_{theme_id}"):
        themes[theme_id] = {
            'name': theme['name'],
            'primary': primary,
            'secondary': secondary,
            'background': background,
            'surface': surface,
            'text': text,
            'text_secondary': text_secondary
        }
        
        theme_settings['themes'] = themes
        
        if save_admin_setting('ui_theme_settings', theme_settings):
            st.success("✅ Theme gespeichert!")
            st.rerun()

def render_pdf_template_settings():
    """Renders PDF template management UI."""
    st.subheader("📄 PDF Template-Verwaltung")

    # Load current settings
    template_settings = load_admin_setting('pdf_templates', {})
    
    active_template = template_settings.get('active_template', 'default')
    templates = template_settings.get('templates', {})
    
    # Active template selection
    st.markdown("**Aktives Template**")
    
    template_options = list(templates.keys())
    selected_template = st.selectbox(
        "Template auswählen",
        options=template_options,
        index=template_options.index(active_template) if active_template in template_options else 0,
        format_func=lambda x: templates[x].get('name', x)
    )
    
    if st.button("✅ Template aktivieren"):
        template_settings['active_template'] = selected_template
        if save_admin_setting('pdf_templates', template_settings):
            st.success(f"✅ Template '{templates[selected_template]['name']}' aktiviert!")
            st.rerun()
    
    # Template details
    template = templates[selected_template]
    
    with st.expander("ℹ️ Template-Details"):
        st.markdown(f"**Name:** {template['name']}")
        st.markdown(f"**Beschreibung:** {template['description']}")
        st.markdown(f"**Template-Dateien (Normal):** `{template['template_files']['normal']}`")
        st.markdown(f"**Template-Dateien (Wärmepumpe):** `{template['template_files']['heatpump']}`")
        st.markdown(f"**Koordinaten-Dateien (Normal):** `{template['coords_files']['normal']}`")
        st.markdown(f"**Koordinaten-Dateien (Wärmepumpe):** `{template['coords_files']['heatpump']}`")
    
    # Add new template
    with st.expander("➕ Neues Template hinzufügen"):
        render_add_template_ui(templates, template_settings)

def render_add_template_ui(templates: dict, template_settings: dict):
    """Renders UI for adding new PDF template."""
    st.markdown("**Neues Template erstellen**")

    template_id = st.text_input(
        "Template-ID",
        help="Eindeutige ID für das Template (z.B. 'modern', 'classic')"
    )
    
    template_name = st.text_input(
        "Template-Name",
        help="Anzeigename für das Template"
    )
    
    template_description = st.text_area(
        "Beschreibung",
        help="Kurze Beschreibung des Templates"
    )
    
    st.markdown("**Template-Dateipfade**")
    
    normal_template_path = st.text_input(
        "Normal Template Pfad",
        value="pdf_templates_static/notext/nt_nt_{:02d}.pdf",
        help="Pfad-Pattern für normale Templates (mit {:02d} für Seitenzahl)"
    )
    
    hp_template_path = st.text_input(
        "Wärmepumpe Template Pfad",
        value="pdf_templates_static/notext/hp_nt_{:02d}.pdf",
        help="Pfad-Pattern für Wärmepumpen-Templates"
    )
    
    normal_coords_path = st.text_input(
        "Normal Koordinaten Pfad",
        value="coords/seite{}.yml",
        help="Pfad-Pattern für normale Koordinaten-Dateien"
    )
    
    hp_coords_path = st.text_input(
        "Wärmepumpe Koordinaten Pfad",
        value="coords_wp/wp_seite{}.yml",
        help="Pfad-Pattern für Wärmepumpen-Koordinaten"
    )
    
    if st.button("➕ Template hinzufügen"):
        if not template_id or template_id in templates:
            st.error("❌ Ungültige oder bereits vorhandene Template-ID")
            return
        
        templates[template_id] = {
            'name': template_name,
            'description': template_description,
            'template_files': {
                'normal': normal_template_path,
                'heatpump': hp_template_path
            },
            'coords_files': {
                'normal': normal_coords_path,
                'heatpump': hp_coords_path
            },
            'preview_image': None
        }
        
        template_settings['templates'] = templates
        
        if save_admin_setting('pdf_templates', template_settings):
            st.success(f"✅ Template '{template_name}' hinzugefügt!")
            st.rerun()

def render_layout_options_settings():
    """Renders PDF layout options configuration."""
    st.subheader("📐 Layout-Optionen")

    # Load current settings
    layout_settings = load_admin_setting('pdf_layout_options', {})
    
    available_layouts = layout_settings.get('available_layouts', {})
    default_layout = layout_settings.get('default_layout', 'standard_8')
    
    st.markdown("**Verfügbare Layouts**")
    
    for layout_id, layout in available_layouts.items():
        with st.expander(f"📄 {layout['name']}"):
            st.markdown(f"**Beschreibung:** {layout['description']}")
            
            if 'pages' in layout:
                st.markdown(f"**Seitenanzahl:** {layout['pages']}")
            elif 'base_pages' in layout:
                st.markdown(f"**Basis-Seiten:** {layout['base_pages']} (erweiterbar)")
            
            col1, col2 = st.columns(2)
            
            with col1:
                enabled = st.checkbox(
                    "Aktiviert",
                    value=layout['enabled'],
                    key=f"layout_enabled_{layout_id}"
                )
            
            with col2:
                is_default = st.checkbox(
                    "Als Standard",
                    value=(default_layout == layout_id),
                    key=f"layout_default_{layout_id}"
                )
            
            if st.button("💾 Speichern", key=f"save_layout_{layout_id}"):
                available_layouts[layout_id]['enabled'] = enabled
                
                if is_default:
                    layout_settings['default_layout'] = layout_id
                
                layout_settings['available_layouts'] = available_layouts
                
                if save_admin_setting('pdf_layout_options', layout_settings):
                    st.success(f"✅ Layout '{layout['name']}' aktualisiert!")
                    st.rerun()

def render_pdf_design_preview(pdf_design: dict):
    """Renders a preview of PDF design settings."""
    st.markdown("**PDF Design-Vorschau**")

    # Create a simple preview
    st.markdown(f"""
    <div style="
        background-color: white;
        padding: 20px;
        border: 2px solid {pdf_design.get('primary_color', '#003366')};
        border-radius: 8px;
    ">
        <h1 style="
            color: {pdf_design.get('primary_color', '#003366')};
            font-family: {pdf_design.get('font_family_main', 'Helvetica')};
            font-size: {pdf_design.get('font_sizes', {}).get('h1', 18)}pt;
        ">
            Angebot für Photovoltaikanlage
        </h1>
        
        <p style="
            color: {pdf_design.get('secondary_color', '#808080')};
            font-family: {pdf_design.get('font_family_main', 'Helvetica')};
            font-size: {pdf_design.get('font_sizes', {}).get('body', 10)}pt;
        ">
            Dies ist eine Vorschau des PDF-Designs mit den aktuellen Einstellungen.
        </p>
        
        <div style="
            background-color: {pdf_design.get('secondary_color', '#808080')}22;
            padding: 10px;
            margin-top: 10px;
            border-radius: 4px;
        ">
            <span style="font-size: {pdf_design.get('font_sizes', {}).get('small', 8)}pt;">
                Beispiel für einen Tabellenbereich oder Hintergrund
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

```

