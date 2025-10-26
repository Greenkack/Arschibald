"""
Protected Chart Page Generator Module

Implements chart page generation using reportlab.platypus with KeepTogether
for intelligent page protection. This ensures charts, titles, and descriptions
stay together and are not split across pages.

This module integrates with pdf_page_protection.py to provide:
- KeepTogether for charts with titles and descriptions
- KeepTogether for tables with titles
- KeepTogether for financing sections
- Automatic page breaks when space is insufficient
- Special handling for charts with legends and footnotes

Author: Kiro AI Assistant
Date: 2025-01-10
"""

import io
from typing import Any

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Import page protection manager
from pdf_page_protection import PageProtectionManager


class ProtectedChartPageGenerator:
    """Generates chart pages with intelligent page protection.

    This generator uses reportlab.platypus with KeepTogether to ensure
    that charts, titles, and descriptions stay together on the same page.
    It applies page protection only to pages 9+ (extended PDF pages).
    """

    def __init__(
        self,
        analysis_results: dict,
        theme: dict,
        logger: Any | None = None,
        enable_page_protection: bool = True
    ):
        """Initialize protected chart page generator.

        Args:
            analysis_results: Analysis results dictionary with chart bytes
            theme: Theme configuration
            logger: Logger instance for tracking errors and warnings (optional)
            enable_page_protection: Whether to enable page protection (default: True)
        """
        self.analysis_results = analysis_results
        self.theme = theme
        self.logger = logger
        self.width, self.height = A4
        self.enable_page_protection = enable_page_protection

        # Initialize page protection manager
        if enable_page_protection:
            self.protection_manager = PageProtectionManager(
                doc_height=self.height,
                min_space_at_bottom=3 * cm,
                enable_logging=True
            )
        else:
            self.protection_manager = None

        # Initialize styles
        self._init_styles()

        # Track current page for protection manager
        self.current_page = 9  # Extended PDF starts at page 9

    def _init_styles(self) -> None:
        """Initialize paragraph styles for charts."""
        base_styles = getSampleStyleSheet()

        # Chart title style
        self.chart_title_style = ParagraphStyle(
            'ChartTitle',
            parent=base_styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#003366'),
            spaceAfter=6,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )

        # Chart description style
        self.chart_description_style = ParagraphStyle(
            'ChartDescription',
            parent=base_styles['BodyText'],
            fontSize=10,
            textColor=HexColor('#333333'),
            spaceAfter=12,
            spaceBefore=6,
            alignment=TA_LEFT
        )

        # Table title style
        self.table_title_style = ParagraphStyle(
            'TableTitle',
            parent=base_styles['Heading3'],
            fontSize=12,
            textColor=HexColor('#003366'),
            spaceAfter=6,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )

        # Financing section title style
        self.financing_title_style = ParagraphStyle(
            'FinancingTitle',
            parent=base_styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#003366'),
            spaceAfter=8,
            spaceBefore=16,
            fontName='Helvetica-Bold'
        )

    def generate(self, chart_keys: list[str]) -> bytes:
        """Generates pages with selected charts using platypus.

        Args:
            chart_keys: List of chart keys from analysis_results

        Returns:
            PDF bytes with chart pages
        """
        if not chart_keys:
            if self.logger:
                self.logger.log_warning(
                    'ProtectedChartPageGenerator',
                    'No chart keys provided'
                )
            return b''

        if self.logger:
            self.logger.log_info(
                'ProtectedChartPageGenerator',
                f'Generating {len(chart_keys)} charts with page protection'
            )

        try:
            # Create PDF document
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=2 * cm,
                leftMargin=2 * cm,
                topMargin=2 * cm,
                bottomMargin=2 * cm
            )

            # Build story with protected elements
            story = []

            for i, chart_key in enumerate(chart_keys):
                # Update current page for protection manager
                if self.protection_manager:
                    self.protection_manager.set_current_page(self.current_page)

                # Add chart with protection
                chart_elements = self._create_protected_chart(chart_key)
                if chart_elements:
                    if isinstance(chart_elements, list):
                        story.extend(chart_elements)
                    else:
                        story.append(chart_elements)

                    # Add spacing between charts
                    if i < len(chart_keys) - 1:
                        if self.protection_manager:
                            spacing_elements = (
                                self.protection_manager
                                .add_spacing_with_pagebreak_check(
                                    spacing=1.0 * cm,
                                    min_space_for_next=8.0 * cm
                                )
                            )
                            story.extend(spacing_elements)
                        else:
                            story.append(Spacer(1, 1.0 * cm))

                # Estimate page increment (rough estimate)
                # Each chart typically takes 1 page
                self.current_page += 1

            # Build PDF
            doc.build(story)

            result = buffer.getvalue()

            if self.logger:
                self.logger.log_info(
                    'ProtectedChartPageGenerator',
                    f'Successfully generated chart pages ({len(result)} bytes)'
                )

            # Print protection summary if enabled
            if self.protection_manager:
                self.protection_manager.print_protection_summary()

            return result

        except Exception as e:
            if self.logger:
                self.logger.log_error(
                    'ProtectedChartPageGenerator',
                    'Error generating chart pages',
                    e
                )
            return b''

    def _create_protected_chart(self, chart_key: str) -> Any:
        """Creates a protected chart element with title and description.

        Args:
            chart_key: Chart key from analysis_results

        Returns:
            Protected flowable or list of flowables
        """
        # Get chart bytes
        chart_bytes = self.analysis_results.get(chart_key)
        if not chart_bytes:
            if self.logger:
                self.logger.log_warning(
                    'ProtectedChartPageGenerator',
                    f'Chart {chart_key} not found in analysis results'
                )
            return None

        # Get chart name and description
        chart_name = self._get_chart_name(chart_key)
        chart_description = self._get_chart_description(chart_key)

        # Create title paragraph
        title = Paragraph(chart_name, self.chart_title_style)

        # Create chart image
        try:
            img_reader = ImageReader(io.BytesIO(chart_bytes))
            chart_image = Image(
                io.BytesIO(chart_bytes),
                width=self.width - 4 * cm,
                # Leave space for title/desc
                height=(self.height - 8 * cm) * 0.7,
                kind='proportional'
            )
        except Exception as e:
            if self.logger:
                self.logger.log_error(
                    'ProtectedChartPageGenerator',
                    f'Error creating image for chart {chart_key}',
                    e
                )
            # Return error message
            error_text = f"Fehler beim Laden des Diagramms: {chart_name}"
            return [
                title,
                Spacer(1, 0.5 * cm),
                Paragraph(error_text, self.chart_description_style)
            ]

        # Create description paragraph if available
        description = None
        if chart_description:
            description = Paragraph(
                chart_description,
                self.chart_description_style)

        # Apply page protection if enabled
        if self.protection_manager:
            return self.protection_manager.wrap_chart_with_description(
                chart=chart_image,
                title=title,
                description=description,
                chart_key=chart_key
            )
        # No protection - return as list
        elements = [title, Spacer(1, 0.3 * cm), chart_image]
        if description:
            elements.extend([Spacer(1, 0.3 * cm), description])
        return elements

    def _get_chart_name(self, chart_key: str) -> str:
        """Gets friendly name for a chart key.

        Args:
            chart_key: Chart key from analysis_results

        Returns:
            Friendly name for the chart
        """
        # Chart name mapping
        chart_names = {
            # Financial charts
            'cumulative_cashflow_chart_bytes': 'Kumulierter Cashflow',
            'cost_projection_chart_bytes': 'Stromkosten-Hochrechnung',
            'break_even_chart_bytes': 'Break-Even-Analyse',
            'amortisation_chart_bytes': 'Amortisationsdiagramm',
            'roi_chart_bytes': 'ROI-Entwicklung',
            'financing_comparison_chart_bytes': 'Finanzierungsvergleich',

            # Production & consumption charts
            'monthly_prod_cons_chart_bytes': 'Monatliche Produktion vs. Verbrauch',
            'yearly_production_chart_bytes': 'Jahresproduktion',
            'energy_balance_chart_bytes': 'Energiebilanz',
            'monthly_savings_chart_bytes': 'Monatliche Einsparungen',
            'yearly_comparison_chart_bytes': 'Jahresvergleich',

            # Environmental charts
            'co2_savings_chart_bytes': 'CO₂-Einsparung',

            # Extended charts
            'scenario_comparison_chart_bytes': 'Szenario-Vergleich',
            'tariff_comparison_chart_bytes': 'Tarif-Vergleich',
            'income_projection_chart_bytes': 'Einnahmen-Projektion',
            'battery_usage_chart_bytes': 'Batterie-Nutzung',
            'grid_interaction_chart_bytes': 'Netz-Interaktion',

            # Analysis charts
            'advanced_analysis_chart_bytes': 'Erweiterte Analyse',
            'sensitivity_analysis_chart_bytes': 'Sensitivitäts-Analyse',
            'optimization_chart_bytes': 'Optimierungs-Analyse',

            # Summary charts
            'summary_chart_bytes': 'Zusammenfassung',
            'comparison_chart_bytes': 'Vergleich',
        }

        return chart_names.get(chart_key, chart_key.replace('_', ' ').title())

    def _get_chart_description(self, chart_key: str) -> str | None:
        """Gets description for a chart key.

        First checks if a dynamic description is available in analysis_results,
        then falls back to static descriptions.

        Args:
            chart_key: Chart key from analysis_results

        Returns:
            Description text or None
        """
        # Check for dynamic description (Task 4.4)
        description_key = chart_key.replace('_bytes', '_description')
        if description_key in self.analysis_results:
            return self.analysis_results[description_key]

        # Fallback to static descriptions
        descriptions = {
            'monthly_prod_cons_chart_bytes': (
                'Diese Darstellung zeigt Ihnen, wie Ihre PV-Anlage im Einklang '
                'mit den Jahreszeiten arbeitet. In den sonnenreichen Sommermonaten '
                'erzeugen Sie deutlich mehr Strom als Sie verbrauchen.'
            ),
            'cost_projection_chart_bytes': (
                'Hier sehen Sie, wie sich Ihre Stromkosten mit und ohne PV-Anlage '
                'entwickeln. Während herkömmliche Stromkosten Jahr für Jahr steigen, '
                'bleiben Sie mit Ihrer eigenen Solaranlage unabhängig.'
            ),
            'cumulative_cashflow_chart_bytes': (
                'Diese Kurve zeigt Ihren finanziellen Erfolgsweg. Anfangs investieren '
                'Sie, aber schon nach wenigen Jahren kehrt sich das Blatt: Ihre Anlage '
                'arbeitet für Sie und erwirtschaftet echte Gewinne.'
            ),
            'energy_balance_chart_bytes': (
                'Dieses Diagramm zeigt, wie unabhängig Sie vom Stromnetz werden. '
                'Je größer der grüne Anteil, desto mehr Ihres Haushaltsstroms kommt '
                'direkt vom eigenen Dach.'
            ),
            'co2_savings_chart_bytes': (
                'Ihre persönliche CO₂-Bilanz: Mit Ihrer PV-Anlage leisten Sie einen '
                'aktiven Beitrag zum Klimaschutz. Jede erzeugte kWh spart CO₂ ein.'
            ),
        }

        return descriptions.get(chart_key)

    def create_protected_table(
        self,
        table_data: list,
        title_text: str,
        table_id: str = ""
    ) -> Any:
        """Creates a protected table element with title.

        Args:
            table_data: Table data as list of lists
            title_text: Title text
            table_id: Table identifier for logging

        Returns:
            Protected flowable or list of flowables
        """
        # Create title paragraph
        title = Paragraph(title_text, self.table_title_style)

        # Create table
        table = Table(table_data)

        # Apply basic table style
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F5F5F5')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#CCCCCC')),
        ]))

        # Apply page protection if enabled
        if self.protection_manager:
            return self.protection_manager.wrap_table_with_title(
                table=table,
                title=title,
                table_id=table_id
            )
        return [title, Spacer(1, 0.3 * cm), table]

    def create_protected_financing_section(
        self,
        title_text: str,
        table_data: list,
        description_text: str | None = None,
        section_id: str = ""
    ) -> Any:
        """Creates a protected financing section.

        Args:
            title_text: Section title text
            table_data: Table data as list of lists
            description_text: Optional description text
            section_id: Section identifier for logging

        Returns:
            Protected flowable or list of flowables
        """
        # Create title paragraph
        title = Paragraph(title_text, self.financing_title_style)

        # Create table
        table = Table(table_data)

        # Apply financing table style (more prominent)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F0F8FF')),
            ('GRID', (0, 0), (-1, -1), 1.5, HexColor('#003366')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))

        # Create description paragraph if provided
        description = None
        if description_text:
            description = Paragraph(
                description_text,
                self.chart_description_style)

        # Apply page protection if enabled (STRICT for financing)
        if self.protection_manager:
            return self.protection_manager.wrap_financing_section(
                title=title,
                table=table,
                description=description,
                section_id=section_id
            )
        elements = [title, Spacer(1, 0.3 * cm), table]
        if description:
            elements.extend([Spacer(1, 0.5 * cm), description])
        return elements

    def get_protection_summary(self) -> dict | None:
        """Get page protection summary.

        Returns:
            Protection summary dictionary or None if protection is disabled
        """
        if self.protection_manager:
            return self.protection_manager.get_protection_summary()
        return None


# Helper functions for easy integration

def create_protected_chart_pages(
    analysis_results: dict,
    chart_keys: list[str],
    theme: dict,
    logger: Any | None = None
) -> bytes:
    """Helper function to create protected chart pages.

    Args:
        analysis_results: Analysis results dictionary with chart bytes
        chart_keys: List of chart keys to include
        theme: Theme configuration
        logger: Optional logger instance

    Returns:
        PDF bytes with protected chart pages
    """
    generator = ProtectedChartPageGenerator(
        analysis_results=analysis_results,
        theme=theme,
        logger=logger,
        enable_page_protection=True
    )

    return generator.generate(chart_keys)
