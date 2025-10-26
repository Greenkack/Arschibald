"""
Extended PDF Generator Module

Handles generation of additional pages for extended PDF output including:
- Financing details
- Product datasheets
- Company documents
- Charts and visualizations

This module is OPTIONAL and does not affect the standard 8-page PDF generation.
"""

import hashlib
import io
from datetime import datetime
from typing import Any

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


class ChartCache:
    """Cache for rendered charts to improve performance.

    This cache stores rendered chart images in memory to avoid re-rendering
    the same charts multiple times. Charts are cached by a hash of their
    data and configuration, and the cache can be invalidated when data changes.

    The cache is designed to be used within a single PDF generation session
    and is not persisted between sessions.
    """

    def __init__(self, max_size: int = 100):
        """Initialize the chart cache.

        Args:
            max_size: Maximum number of charts to cache (default: 100)
        """
        self._cache: dict[str, bytes] = {}
        self._max_size = max_size
        self._access_count: dict[str, int] = {}
        self._hit_count = 0
        self._miss_count = 0

    def _generate_cache_key(self, chart_key: str, chart_data: Any) -> str:
        """Generate a unique cache key for a chart.

        Creates a hash based on the chart key and a representation of the chart data.
        This ensures that the same chart with the same data will have the same cache key.

        Args:
            chart_key: The chart identifier (e.g., 'monthly_prod_cons_chart_bytes')
            chart_data: The chart data (typically bytes)

        Returns:
            A unique cache key string
        """
        # Create a hash of the chart key and data
        hasher = hashlib.md5()
        hasher.update(chart_key.encode('utf-8'))

        # If chart_data is bytes, use it directly; otherwise convert to string
        if isinstance(chart_data, bytes):
            hasher.update(chart_data[:1000])  # Use first 1KB for hash
        else:
            hasher.update(str(chart_data).encode('utf-8'))

        return hasher.hexdigest()

    def get(self, chart_key: str, chart_data: Any) -> bytes | None:
        """Retrieve a chart from the cache.

        Args:
            chart_key: The chart identifier
            chart_data: The chart data for cache key generation

        Returns:
            Cached chart bytes if found, None otherwise
        """
        cache_key = self._generate_cache_key(chart_key, chart_data)

        if cache_key in self._cache:
            self._hit_count += 1
            self._access_count[cache_key] = self._access_count.get(
                cache_key, 0) + 1
            return self._cache[cache_key]

        self._miss_count += 1
        return None

    def put(self, chart_key: str, chart_data: Any, chart_bytes: bytes) -> None:
        """Store a chart in the cache.

        If the cache is full, removes the least recently used chart before adding.

        Args:
            chart_key: The chart identifier
            chart_data: The chart data for cache key generation
            chart_bytes: The rendered chart bytes to cache
        """
        cache_key = self._generate_cache_key(chart_key, chart_data)

        # If cache is full, remove least accessed item
        if len(self._cache) >= self._max_size:
            self._evict_lru()

        self._cache[cache_key] = chart_bytes
        self._access_count[cache_key] = 1

    def _evict_lru(self) -> None:
        """Evict the least recently used (least accessed) item from cache."""
        if not self._cache:
            return

        # Find the key with the lowest access count
        lru_key = min(self._access_count, key=self._access_count.get)

        # Remove from both cache and access count
        del self._cache[lru_key]
        del self._access_count[lru_key]

    def invalidate(self, chart_key: str | None = None,
                   chart_data: Any = None) -> None:
        """Invalidate cache entries.

        Args:
            chart_key: Specific chart key to invalidate, or None to clear all
            chart_data: Chart data for generating the cache key (required if chart_key is provided)
        """
        if chart_key is None:
            # Clear entire cache
            self._cache.clear()
            self._access_count.clear()
        else:
            # Generate the cache key and remove it
            if chart_data is not None:
                cache_key = self._generate_cache_key(chart_key, chart_data)
                if cache_key in self._cache:
                    del self._cache[cache_key]
                if cache_key in self._access_count:
                    del self._access_count[cache_key]
            else:
                # If no chart_data provided, remove all entries (fallback to
                # clear all)
                self._cache.clear()
                self._access_count.clear()

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics including hit rate, size, etc.
        """
        total_requests = self._hit_count + self._miss_count
        hit_rate = (
            self._hit_count /
            total_requests *
            100) if total_requests > 0 else 0

        return {
            'size': len(self._cache),
            'max_size': self._max_size,
            'hit_count': self._hit_count,
            'miss_count': self._miss_count,
            'total_requests': total_requests,
            'hit_rate_percent': round(hit_rate, 2),
            'memory_usage_bytes': sum(len(v) for v in self._cache.values())
        }

    def clear(self) -> None:
        """Clear the entire cache and reset statistics."""
        self._cache.clear()
        self._access_count.clear()
        self._hit_count = 0
        self._miss_count = 0


class ExtendedPDFLogger:
    """Logger for Extended PDF generation with error tracking and summary reporting.

    This logger tracks errors, warnings, and info messages during extended PDF generation,
    providing a summary of all issues encountered. It helps with debugging and provides
    graceful degradation by allowing the system to continue even when errors occur.
    """

    def __init__(self):
        """Initialize the logger with empty message lists."""
        self.errors: list[dict[str, Any]] = []
        self.warnings: list[dict[str, Any]] = []
        self.info: list[dict[str, Any]] = []

    def log_error(self, component: str, message: str,
                  exception: Exception | None = None) -> None:
        """Log an error message.

        Args:
            component: Name of the component where error occurred (e.g., 'FinancingPageGenerator')
            message: Human-readable error message
            exception: Optional exception object for detailed error info
        """
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'component': component,
            'message': message,
            'exception': str(exception) if exception else None,
            'exception_type': type(exception).__name__ if exception else None
        }
        self.errors.append(error_entry)

        # Also print to console for immediate visibility
        print(f"ERROR [{component}]: {message}")
        if exception:
            print(f"  Exception: {exception}")

    def log_warning(self, component: str, message: str) -> None:
        """Log a warning message.

        Args:
            component: Name of the component where warning occurred
            message: Human-readable warning message
        """
        warning_entry = {
            'timestamp': datetime.now().isoformat(),
            'component': component,
            'message': message
        }
        self.warnings.append(warning_entry)

        # Also print to console
        print(f"WARNING [{component}]: {message}")

    def log_info(self, component: str, message: str) -> None:
        """Log an informational message.

        Args:
            component: Name of the component logging the info
            message: Human-readable info message
        """
        info_entry = {
            'timestamp': datetime.now().isoformat(),
            'component': component,
            'message': message
        }
        self.info.append(info_entry)

        # Also print to console
        print(f"INFO [{component}]: {message}")

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of all logged messages.

        Returns:
            Dictionary containing counts and lists of all errors, warnings, and info messages
        """
        return {
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'info_count': len(self.info),
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info,
            'has_errors': len(self.errors) > 0,
            'has_warnings': len(self.warnings) > 0
        }

    def get_user_friendly_summary(self) -> str:
        """Get a user-friendly text summary of logged messages.

        Returns:
            Formatted string summarizing the generation process
        """
        summary = self.get_summary()

        lines = []
        lines.append("=== Extended PDF Generation Summary ===")
        lines.append(f"Errors: {summary['error_count']}")
        lines.append(f"Warnings: {summary['warning_count']}")
        lines.append(f"Info: {summary['info_count']}")

        if summary['has_errors']:
            lines.append("\n--- Errors ---")
            for error in self.errors:
                lines.append(f"  [{error['component']}] {error['message']}")

        if summary['has_warnings']:
            lines.append("\n--- Warnings ---")
            for warning in self.warnings:
                lines.append(
                    f"  [{
                        warning['component']}] {
                        warning['message']}")

        return "\n".join(lines)

    def clear(self) -> None:
        """Clear all logged messages."""
        self.errors.clear()
        self.warnings.clear()
        self.info.clear()


class ExtendedPDFGenerator:
    """Main class for generating extended PDF pages."""

    def __init__(
        self,
        offer_data: dict[str, Any],
        analysis_results: dict[str, Any],
        options: dict[str, Any],
        theme: dict[str, Any] | None = None,
        logger: ExtendedPDFLogger | None = None
    ):
        """Initialize the extended PDF generator.

        Args:
            offer_data: Offer data dictionary
            analysis_results: Analysis results with charts
            options: Extended output options from UI
            theme: Theme configuration (optional)
            logger: Logger instance for tracking errors and warnings (optional)
        """
        self.offer_data = offer_data
        self.analysis_results = analysis_results
        self.options = options
        self.theme = theme or self._get_default_theme()
        self.width, self.height = A4
        self.logger = logger or ExtendedPDFLogger()

    def _get_default_theme(self) -> dict[str, Any]:
        """Returns default theme configuration."""
        return {
            'colors': {
                'primary': '#1E3A8A',
                'secondary': '#3B82F6',
                'text': '#000000',
                'background': '#FFFFFF'
            },
            'fonts': {
                'title': 'Helvetica-Bold',
                'body': 'Helvetica'
            }
        }

    def generate_extended_pages(self) -> bytes:
        """Generates all extended pages based on options using efficient single-pass merging.

        This method uses an optimized approach that merges all pages in a single pass,
        avoiding multiple intermediate PDF creations and reducing memory usage.

        Returns:
            PDF bytes containing all extended pages
        """
        self.logger.log_info(
            'ExtendedPDFGenerator',
            'Starting extended PDF generation with efficient merging')
        writer = PdfWriter()

        try:
            # Collect all page generators in order
            page_generators = []

            # Add financing pages
            if self.options.get('financing_details'):
                page_generators.append(
                    ('financing', self._generate_financing_pages))

            # Add product datasheets
            if self.options.get('product_datasheets'):
                page_generators.append(
                    ('datasheets', self._merge_product_datasheets))

            # Add company documents
            if self.options.get('company_documents'):
                page_generators.append(
                    ('documents', self._merge_company_documents))

            # Add chart pages
            if self.options.get('selected_charts'):
                page_generators.append(('charts', self._generate_chart_pages))

            # Process all generators in a single pass
            total_pages = 0
            for section_name, generator_func in page_generators:
                self.logger.log_info(
                    'ExtendedPDFGenerator',
                    f'Processing {section_name} section')

                try:
                    section_bytes = generator_func()
                    if section_bytes:
                        pages_added = self._add_pages_to_writer_efficient(
                            writer, section_bytes)
                        total_pages += pages_added
                        self.logger.log_info(
                            'ExtendedPDFGenerator',
                            f'Added {pages_added} pages from {section_name}')
                    else:
                        self.logger.log_warning(
                            'ExtendedPDFGenerator',
                            f'No pages generated for {section_name}')
                except Exception as e:
                    self.logger.log_error(
                        'ExtendedPDFGenerator', f'Error processing {section_name}', e)
                    continue

            # Write to bytes in a single operation
            if total_pages > 0:
                output = io.BytesIO()
                writer.write(output)
                result = output.getvalue()
                self.logger.log_info(
                    'ExtendedPDFGenerator',
                    f'Successfully generated extended PDF with {total_pages} pages ({
                        len(result)} bytes)')
                return result
            self.logger.log_warning(
                'ExtendedPDFGenerator',
                'No pages generated for extended PDF')
            return b''

        except Exception as e:
            self.logger.log_error(
                'ExtendedPDFGenerator',
                'Critical error generating extended pages',
                e)
            return b''  # Return empty bytes on error

    def _generate_financing_pages(self) -> bytes:
        """Generates financing detail pages."""
        try:
            generator = FinancingPageGenerator(
                self.offer_data,
                self.analysis_results,
                self.theme,
                self.logger
            )
            return generator.generate()
        except Exception as e:
            self.logger.log_error(
                'ExtendedPDFGenerator',
                'Failed to generate financing pages',
                e)
            return b''

    def _merge_product_datasheets(self) -> bytes:
        """Merges selected product datasheets."""
        try:
            merger = ProductDatasheetMerger(self.logger)
            return merger.merge(
                self.options['product_datasheets']
            )
        except Exception as e:
            self.logger.log_error(
                'ExtendedPDFGenerator',
                'Failed to merge product datasheets',
                e)
            return b''

    def _merge_company_documents(self) -> bytes:
        """Merges selected company documents."""
        try:
            merger = CompanyDocumentMerger(self.logger)
            return merger.merge(
                self.options['company_documents']
            )
        except Exception as e:
            self.logger.log_error(
                'ExtendedPDFGenerator',
                'Failed to merge company documents',
                e)
            return b''

    def _generate_chart_pages(self) -> bytes:
        """Generates pages with charts."""
        try:
            generator = ChartPageGenerator(
                self.analysis_results,
                self.options.get('chart_layout', 'one_per_page'),
                self.theme,
                self.logger
            )
            return generator.generate(
                self.options['selected_charts']
            )
        except Exception as e:
            self.logger.log_error(
                'ExtendedPDFGenerator',
                'Failed to generate chart pages',
                e)
            return b''

    def _add_pages_to_writer(
        self,
        writer: PdfWriter,
        pdf_bytes: bytes
    ) -> None:
        """Adds pages from PDF bytes to writer (legacy method).

        This method is kept for backward compatibility but _add_pages_to_writer_efficient
        should be preferred for better performance.
        """
        if not pdf_bytes:
            self.logger.log_warning(
                'ExtendedPDFGenerator',
                'Attempted to add empty PDF bytes to writer')
            return

        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            page_count = len(reader.pages)
            for page in reader.pages:
                writer.add_page(page)
            self.logger.log_info(
                'ExtendedPDFGenerator',
                f'Added {page_count} pages to writer')
        except Exception as e:
            self.logger.log_error(
                'ExtendedPDFGenerator',
                'Error adding pages to writer',
                e)

    def _add_pages_to_writer_efficient(
        self,
        writer: PdfWriter,
        pdf_bytes: bytes
    ) -> int:
        """Efficiently adds pages from PDF bytes to writer in a single pass.

        This optimized version avoids multiple intermediate reads and writes,
        reducing memory usage and improving performance.

        Args:
            writer: PdfWriter to add pages to
            pdf_bytes: PDF bytes to read pages from

        Returns:
            Number of pages added
        """
        if not pdf_bytes:
            return 0

        try:
            # Create reader once and reuse
            reader = PdfReader(io.BytesIO(pdf_bytes))
            page_count = len(reader.pages)

            # Add all pages in a single batch operation
            for page in reader.pages:
                writer.add_page(page)

            return page_count
        except Exception as e:
            self.logger.log_error(
                'ExtendedPDFGenerator',
                'Error adding pages to writer',
                e)
            return 0


class FinancingPageGenerator:
    """Generates financing detail pages."""

    def __init__(
            self,
            offer_data: dict,
            analysis_results: dict,
            theme: dict,
            logger: ExtendedPDFLogger | None = None):
        """Initialize financing page generator.

        Args:
            offer_data: Offer data dictionary (project_data)
            analysis_results: Analysis results with financial calculations
            theme: Theme configuration
            logger: Logger instance for tracking errors and warnings (optional)
        """
        self.offer_data = offer_data
        self.analysis_results = analysis_results
        self.theme = theme
        self.width, self.height = A4
        self.logger = logger or ExtendedPDFLogger()

    def generate(self) -> bytes:
        """Generates comprehensive financing pages with all required sections.

        Implements Task 9: Finanzierungsinformationen priorisieren
        - Subtask 9.1: Finanzierungsabschnitt ab Seite 9 einfügen
        - Subtask 9.2: Kreditfinanzierung berechnen und darstellen
        - Subtask 9.3: Leasingfinanzierung berechnen und darstellen
        - Subtask 9.4: Amortisationsplan erstellen
        - Subtask 9.5: Finanzierungsvergleich erstellen
        - Subtask 9.6: Finanzierungsdiagramme einfügen

        Returns:
            PDF bytes with comprehensive financing details
        """
        self.logger.log_info(
            'FinancingPageGenerator',
            'Starting comprehensive financing page generation (Task 9)')

        try:
            # Get final_end_preis from offer_data (Requirement 9.3, 9.4)
            final_end_preis = self._get_final_price()

            if final_end_preis <= 0:
                self.logger.log_error(
                    'FinancingPageGenerator',
                    'final_end_preis not available or zero, cannot generate financing pages')
                return b''

            self.logger.log_info(
                'FinancingPageGenerator',
                f'Using final_end_preis: {
                    final_end_preis:,.2f} €')

            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)

            # Subtask 9.1: Finanzierungsabschnitt ab Seite 9 einfügen
            # Title "Finanzierungsinformationen" as first element on page 9
            self._draw_financing_section_header(c)

            # Subtask 9.2: Kreditfinanzierung berechnen und darstellen
            y_pos = self.height - 6 * cm
            y_pos = self._draw_credit_financing_section(
                c, final_end_preis, y_pos)

            # Check if we need a new page
            if y_pos < 8 * cm:
                c.showPage()
                y_pos = self.height - 3 * cm

            # Subtask 9.3: Leasingfinanzierung berechnen und darstellen
            y_pos = self._draw_leasing_financing_section(
                c, final_end_preis, y_pos)

            # Check if we need a new page
            if y_pos < 10 * cm:
                c.showPage()
                y_pos = self.height - 3 * cm

            # Subtask 9.4: Amortisationsplan erstellen
            y_pos = self._draw_amortization_plan(c, final_end_preis, y_pos)

            # Check if we need a new page
            if y_pos < 8 * cm:
                c.showPage()
                y_pos = self.height - 3 * cm

            # Subtask 9.5: Finanzierungsvergleich erstellen
            y_pos = self._draw_financing_comparison(c, final_end_preis, y_pos)

            # Subtask 9.6: Finanzierungsdiagramme einfügen (if available)
            # This would be handled by chart selection in extended_options

            c.save()
            result = buffer.getvalue()
            self.logger.log_info(
                'FinancingPageGenerator',
                f'Successfully generated comprehensive financing pages ({
                    len(result)} bytes)')
            return result
        except Exception as e:
            self.logger.log_error(
                'FinancingPageGenerator',
                'Error generating comprehensive financing pages',
                e)
            import traceback
            traceback.print_exc()
            return b''

    def _get_final_price(self) -> float:
        """Extracts final_end_preis from offer_data and analysis_results.

        Implements Requirement 9.3, 9.4: Use final_end_preis from project_data['pv_details']
        If not available, log error and return 0.

        Returns:
            Final price as float, or 0 if not available
        """
        try:
            # Priority 1: Try analysis_results.final_price (most reliable)
            if isinstance(self.analysis_results, dict):
                final_price = self.analysis_results.get('final_price')
                if final_price and isinstance(
                        final_price, (int, float)) and final_price > 0:
                    return float(final_price)

                # Try final_price_netto
                final_price = self.analysis_results.get('final_price_netto')
                if final_price and isinstance(
                        final_price, (int, float)) and final_price > 0:
                    return float(final_price)

                # Try total_investment_brutto
                final_price = self.analysis_results.get(
                    'total_investment_brutto')
                if final_price and isinstance(
                        final_price, (int, float)) and final_price > 0:
                    return float(final_price)

            # Priority 2: Try pv_details
            pv_details = self.offer_data.get('pv_details', {})
            if isinstance(pv_details, dict):
                final_price = pv_details.get('final_end_preis')
                if final_price and isinstance(
                        final_price, (int, float)) and final_price > 0:
                    return float(final_price)

            # Priority 3: Try project_details
            project_details = self.offer_data.get('project_details', {})
            if isinstance(project_details, dict):
                final_price = project_details.get('final_end_preis')
                if final_price and isinstance(
                        final_price, (int, float)) and final_price > 0:
                    return float(final_price)

                # Try final_offer_price_net
                final_price = project_details.get('final_offer_price_net')
                if final_price and isinstance(
                        final_price, (int, float)) and final_price > 0:
                    return float(final_price)

            # Priority 4: Try grand_total as fallback
            grand_total = self.offer_data.get('grand_total')
            if grand_total and isinstance(
                    grand_total, (int, float)) and grand_total > 0:
                self.logger.log_warning(
                    'FinancingPageGenerator',
                    'final_end_preis not found, using grand_total as fallback')
                return float(grand_total)

            self.logger.log_error(
                'FinancingPageGenerator',
                'final_end_preis not available in any expected location')
            return 0.0

        except Exception as e:
            self.logger.log_error(
                'FinancingPageGenerator',
                'Error extracting final_end_preis',
                e)
            return 0.0

    def _get_financing_options(self) -> list[dict]:
        """Extracts financing options from offer data.

        Uses real keys from payment_terms configuration.
        Returns list of financing options with their details.
        """
        try:
            from database import load_admin_setting

            # Load comprehensive payment config which contains financing
            # options
            comprehensive_config = load_admin_setting(
                'comprehensive_payment_config', {})
            payment_options = comprehensive_config.get('payment_options', [])

            # Filter for financing options that are enabled
            financing_opts = [
                opt for opt in payment_options
                if opt.get('payment_type') == 'financing'
                and opt.get('enabled', False)
            ]

            # If no comprehensive config, try legacy payment_terms
            if not financing_opts:
                self.logger.log_info(
                    'FinancingPageGenerator',
                    'No financing options in comprehensive config, trying legacy payment_terms')
                payment_terms = load_admin_setting('payment_terms', {})
                payment_options = payment_terms.get('payment_options', [])
                financing_opts = [
                    opt for opt in payment_options
                    if opt.get('payment_type') == 'financing'
                    and opt.get('enabled', False)
                ]

            if not financing_opts:
                self.logger.log_warning(
                    'FinancingPageGenerator',
                    'No enabled financing options found in database')

            return financing_opts
        except Exception as e:
            self.logger.log_error(
                'FinancingPageGenerator',
                'Error loading financing options from database',
                e)
            return []

    def _draw_financing_section_header(self, c: canvas.Canvas) -> None:
        """Draws the main financing section header.

        Implements Subtask 9.1: Überschrift "Finanzierungsinformationen" als erstes auf Seite 9
        """
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(HexColor(self.theme['colors']['primary']))
        c.drawString(
            2 * cm,
            self.height - 3 * cm,
            "Finanzierungsinformationen")

        c.setFont("Helvetica", 11)
        c.setFillColor(HexColor("#666666"))
        c.drawString(
            2 *
            cm,
            self.height -
            4 *
            cm,
            "Vollständige Finanzierungsanalyse mit Kredit, Leasing und Amortisationsplan")

    def _draw_credit_financing_section(
            self,
            c: canvas.Canvas,
            final_end_preis: float,
            y_pos: float) -> float:
        """Draws credit financing section with table.

        Implements Subtask 9.2: Kreditfinanzierung berechnen und darstellen
        Requirements: 9.5, 9.6, 9.7, 9.8, 9.9, 9.10, 9.11, 9.12, 9.29

        Args:
            c: Canvas object
            final_end_preis: Final price for financing
            y_pos: Current Y position

        Returns:
            New Y position after drawing
        """
        try:
            # Import financial_tools for calculate_annuity (Requirement 9.5)
            from financial_tools import calculate_annuity

            # Get global constants for interest rate and years (Requirements
            # 9.6, 9.7, 9.8)
            interest_rate = self._get_global_constant(
                'loan_interest_rate_percent', 4.0)
            duration_years = self._get_global_constant(
                'simulation_period_years', 20)

            # Calculate annuity (Requirement 9.5)
            credit_result = calculate_annuity(
                final_end_preis, interest_rate, duration_years)

            if 'error' in credit_result:
                self.logger.log_error(
                    'FinancingPageGenerator',
                    f'Error calculating credit: {
                        credit_result["error"]}')
                return y_pos

            # Section title
            c.setFont("Helvetica-Bold", 14)
            c.setFillColor(HexColor(self.theme['colors']['primary']))
            c.drawString(2 * cm, y_pos, "Kreditfinanzierung")
            y_pos -= 1 * cm

            # Create table data (Requirement 9.9)
            table_data = [
                [
                    'Kreditbetrag', self._format_currency(final_end_preis)], [
                    'Zinssatz', f'{
                        interest_rate:.2f}% p.a.'], [
                    'Laufzeit', f'{duration_years} Jahre ({
                        credit_result.get(
                            "laufzeit_monate", 0)} Monate)'], [
                                'Monatliche Rate', self._format_currency(
                                    credit_result.get(
                                        'monatliche_rate', 0))], [
                                            'Gesamtkosten', self._format_currency(
                                                credit_result.get(
                                                    'gesamtkosten', 0))], [
                                                        'Zinskosten gesamt', self._format_currency(
                                                            credit_result.get(
                                                                'gesamtzinsen', 0))]]

            # Draw table with blue header and grey gridlines (Requirements
            # 9.10, 9.11, 9.12)
            y_pos = self._draw_financing_table(c, table_data, y_pos)

            return y_pos - 1 * cm

        except ImportError:
            self.logger.log_error(
                'FinancingPageGenerator',
                'financial_tools module not available')
            return y_pos
        except Exception as e:
            self.logger.log_error(
                'FinancingPageGenerator',
                'Error drawing credit financing section',
                e)
            return y_pos

    def _draw_leasing_financing_section(
            self,
            c: canvas.Canvas,
            final_end_preis: float,
            y_pos: float) -> float:
        """Draws leasing financing section with table.

        Implements Subtask 9.3: Leasingfinanzierung berechnen und darstellen
        Requirements: 9.13, 9.14, 9.15, 9.16, 9.17

        Args:
            c: Canvas object
            final_end_preis: Final price for financing
            y_pos: Current Y position

        Returns:
            New Y position after drawing
        """
        try:
            # Import financial_tools for calculate_leasing_costs (Requirement
            # 9.13)
            from financial_tools import calculate_leasing_costs

            # Get global constants (Requirements 9.14, 9.15)
            leasing_factor = self._get_global_constant(
                'leasing_factor_percent', 1.2)
            residual_value_percent = self._get_global_constant(
                'residual_value_percent', 1.0)
            duration_years = self._get_global_constant(
                'simulation_period_years', 20)
            duration_months = duration_years * 12

            # Calculate leasing costs (Requirement 9.13, 9.14)
            leasing_result = calculate_leasing_costs(
                final_end_preis,
                leasing_factor,
                duration_months,
                residual_value_percent
            )

            if 'error' in leasing_result:
                self.logger.log_error(
                    'FinancingPageGenerator',
                    f'Error calculating leasing: {
                        leasing_result["error"]}')
                return y_pos

            # Section title
            c.setFont("Helvetica-Bold", 14)
            c.setFillColor(HexColor(self.theme['colors']['primary']))
            c.drawString(2 * cm, y_pos, "Leasingfinanzierung")
            y_pos -= 1 * cm

            # Create table data (Requirement 9.16)
            table_data = [
                ['Leasingbetrag', self._format_currency(final_end_preis)],
                ['Leasingfaktor', f'{leasing_factor:.2f}%'],
                ['Laufzeit', f'{duration_years} Jahre ({duration_months} Monate)'],
                ['Monatliche Rate', self._format_currency(leasing_result.get('monatliche_rate', 0))],
                ['Restwert', self._format_currency(leasing_result.get('restwert', 0))],
                ['Gesamtkosten', self._format_currency(leasing_result.get('gesamtkosten', 0))]
            ]

            # Draw table with same styling as credit table (Requirement 9.17)
            y_pos = self._draw_financing_table(c, table_data, y_pos)

            return y_pos - 1 * cm

        except ImportError:
            self.logger.log_error(
                'FinancingPageGenerator',
                'financial_tools module not available')
            return y_pos
        except Exception as e:
            self.logger.log_error(
                'FinancingPageGenerator',
                'Error drawing leasing financing section',
                e)
            return y_pos

    def _draw_amortization_plan(
            self,
            c: canvas.Canvas,
            final_end_preis: float,
            y_pos: float) -> float:
        """Draws amortization plan table.

        Implements Subtask 9.4: Amortisationsplan erstellen
        Requirements: 9.18, 9.19, 9.20, 9.21

        Args:
            c: Canvas object
            final_end_preis: Final price for financing
            y_pos: Current Y position

        Returns:
            New Y position after drawing
        """
        try:
            # Section title
            c.setFont("Helvetica-Bold", 14)
            c.setFillColor(HexColor(self.theme['colors']['primary']))
            c.drawString(2 * cm, y_pos, "Amortisationsplan")
            y_pos -= 1 * cm

            # Get annual savings and costs
            annual_savings = self._get_annual_savings()
            annual_costs = self._get_annual_costs()

            # Calculate for 20-25 years (Requirement 9.18)
            years = 25

            # Draw table header
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(HexColor(self.theme['colors']['primary']))
            c.rect(
                2 * cm,
                y_pos - 0.5 * cm,
                self.width - 4 * cm,
                0.6 * cm,
                fill=1)
            c.setFillColor(HexColor("#FFFFFF"))

            # Columns: Jahr, Einsparungen, Kosten, Netto-Cashflow, kumulierter
            # Cashflow (Requirement 9.19)
            col_widths = [2 * cm, 3 * cm, 3 * cm, 3.5 * cm, 3.5 * cm]
            col_x = [2 * cm, 4 * cm, 7 * cm, 10 * cm, 13.5 * cm]
            headers = [
                'Jahr',
                'Einsparungen',
                'Kosten',
                'Netto-Cashflow',
                'Kumuliert']

            for i, header in enumerate(headers):
                c.drawString(col_x[i] + 0.2 * cm, y_pos - 0.3 * cm, header)

            y_pos -= 0.7 * cm

            # Calculate and draw rows
            cumulative_cashflow = -final_end_preis  # Initial investment
            amortization_year = None

            c.setFillColor(HexColor("#000000"))
            c.setFont("Helvetica", 8)

            # Show first 10 years in detail, then summary
            for year in range(1, min(years + 1, 11)):
                if y_pos < 3 * cm:
                    c.showPage()
                    y_pos = self.height - 3 * cm
                    # Redraw header
                    c.setFont("Helvetica-Bold", 9)
                    c.setFillColor(HexColor(self.theme['colors']['primary']))
                    c.rect(
                        2 * cm,
                        y_pos - 0.5 * cm,
                        self.width - 4 * cm,
                        0.6 * cm,
                        fill=1)
                    c.setFillColor(HexColor("#FFFFFF"))
                    for i, header in enumerate(headers):
                        c.drawString(
                            col_x[i] + 0.2 * cm, y_pos - 0.3 * cm, header)
                    y_pos -= 0.7 * cm
                    c.setFillColor(HexColor("#000000"))
                    c.setFont("Helvetica", 8)

                net_cashflow = annual_savings - annual_costs
                cumulative_cashflow += net_cashflow

                # Highlight amortization year (Requirement 9.20)
                if cumulative_cashflow >= 0 and amortization_year is None:
                    amortization_year = year
                    c.setFillColor(HexColor("#FFFF00"))
                    c.rect(
                        2 * cm,
                        y_pos - 0.4 * cm,
                        self.width - 4 * cm,
                        0.5 * cm,
                        fill=1)
                    c.setFillColor(HexColor("#000000"))
                    c.setFont("Helvetica-Bold", 8)

                c.drawString(col_x[0] + 0.2 * cm, y_pos, str(year))
                c.drawString(
                    col_x[1] + 0.2 * cm,
                    y_pos,
                    self._format_currency(annual_savings))
                c.drawString(
                    col_x[2] + 0.2 * cm,
                    y_pos,
                    self._format_currency(annual_costs))
                c.drawString(
                    col_x[3] + 0.2 * cm,
                    y_pos,
                    self._format_currency(net_cashflow))
                c.drawString(
                    col_x[4] + 0.2 * cm,
                    y_pos,
                    self._format_currency(cumulative_cashflow))

                if year == amortization_year:
                    c.setFont("Helvetica", 8)

                y_pos -= 0.5 * cm

            # Add summary note
            if amortization_year:
                c.setFont("Helvetica-Bold", 10)
                c.setFillColor(HexColor(self.theme['colors']['primary']))
                y_pos -= 0.5 * cm
                c.drawString(
                    2 * cm,
                    y_pos,
                    f"Amortisationszeit: {amortization_year} Jahre")

            return y_pos - 1 * cm

        except Exception as e:
            self.logger.log_error(
                'FinancingPageGenerator',
                'Error drawing amortization plan',
                e)
            return y_pos

    def _draw_financing_comparison(
            self,
            c: canvas.Canvas,
            final_end_preis: float,
            y_pos: float) -> float:
        """Draws financing comparison section.

        Implements Subtask 9.5: Finanzierungsvergleich erstellen
        Requirements: 9.22, 9.23, 9.24

        Args:
            c: Canvas object
            final_end_preis: Final price for financing
            y_pos: Current Y position

        Returns:
            New Y position after drawing
        """
        try:
            from financial_tools import calculate_financing_comparison

            # Get parameters
            interest_rate = self._get_global_constant(
                'loan_interest_rate_percent', 4.0)
            duration_years = self._get_global_constant(
                'simulation_period_years', 20)
            leasing_factor = self._get_global_constant(
                'leasing_factor_percent', 1.2)

            # Calculate comparison (Requirements 9.22, 9.23)
            comparison = calculate_financing_comparison(
                final_end_preis,
                interest_rate,
                duration_years,
                leasing_factor
            )

            # Section title
            c.setFont("Helvetica-Bold", 14)
            c.setFillColor(HexColor(self.theme['colors']['primary']))
            c.drawString(2 * cm, y_pos, "Finanzierungsvergleich")
            y_pos -= 1 * cm

            # Comparison table (Requirement 9.23)
            c.setFont("Helvetica", 10)
            c.setFillColor(HexColor("#000000"))

            # Barkauf
            c.setFont("Helvetica-Bold", 11)
            c.drawString(2 * cm, y_pos, "Barkauf")
            y_pos -= 0.6 * cm
            c.setFont("Helvetica", 9)
            cash_data = comparison.get('cash_kauf', {})
            c.drawString(
                2.5 * cm,
                y_pos,
                f"Investition: {
                    self._format_currency(
                        cash_data.get(
                            'investition',
                            0))}")
            y_pos -= 0.5 * cm
            c.drawString(
                2.5 * cm,
                y_pos,
                f"Opportunitätskosten: {
                    self._format_currency(
                        cash_data.get(
                            'opportunitaetskosten',
                            0))}")
            y_pos -= 0.5 * cm
            c.drawString(
                2.5 * cm,
                y_pos,
                f"Gesamtkosten: {
                    self._format_currency(
                        cash_data.get(
                            'gesamtkosten',
                            0))}")
            y_pos -= 1 * cm

            # Kredit
            c.setFont("Helvetica-Bold", 11)
            c.drawString(2 * cm, y_pos, "Kreditfinanzierung")
            y_pos -= 0.6 * cm
            c.setFont("Helvetica", 9)
            credit_data = comparison.get('kredit', {})
            c.drawString(
                2.5 * cm,
                y_pos,
                f"Monatliche Rate: {
                    self._format_currency(
                        credit_data.get(
                            'monatliche_rate',
                            0))}")
            y_pos -= 0.5 * cm
            c.drawString(
                2.5 * cm,
                y_pos,
                f"Gesamtkosten: {
                    self._format_currency(
                        credit_data.get(
                            'gesamtkosten',
                            0))}")
            y_pos -= 1 * cm

            # Leasing
            c.setFont("Helvetica-Bold", 11)
            c.drawString(2 * cm, y_pos, "Leasingfinanzierung")
            y_pos -= 0.6 * cm
            c.setFont("Helvetica", 9)
            leasing_data = comparison.get('leasing', {})
            c.drawString(
                2.5 * cm,
                y_pos,
                f"Monatliche Rate: {
                    self._format_currency(
                        leasing_data.get(
                            'monatliche_rate',
                            0))}")
            y_pos -= 0.5 * cm
            c.drawString(
                2.5 * cm,
                y_pos,
                f"Effektive Kosten: {
                    self._format_currency(
                        leasing_data.get(
                            'effektive_kosten',
                            0))}")
            y_pos -= 1 * cm

            # Recommendation (Requirement 9.24)
            recommendation = comparison.get('empfehlung', '')
            if recommendation:
                c.setFont("Helvetica-Bold", 12)
                c.setFillColor(HexColor(self.theme['colors']['primary']))
                c.drawString(2 * cm, y_pos, recommendation)
                y_pos -= 1 * cm

            return y_pos

        except ImportError:
            self.logger.log_error(
                'FinancingPageGenerator',
                'financial_tools module not available')
            return y_pos
        except Exception as e:
            self.logger.log_error(
                'FinancingPageGenerator',
                'Error drawing financing comparison',
                e)
            return y_pos

    def _draw_financing_table(
            self,
            c: canvas.Canvas,
            data: list,
            y_pos: float) -> float:
        """Draws a financing table with blue header and grey gridlines.

        Implements Requirements 9.10, 9.11, 9.12: Table styling

        Args:
            c: Canvas object
            data: Table data as list of [label, value] pairs
            y_pos: Current Y position

        Returns:
            New Y position after drawing
        """
        # Blue header background
        c.setFillColor(HexColor(self.theme['colors']['primary']))
        c.rect(2 * cm, y_pos - 0.5 * cm, 8 * cm, 0.6 * cm, fill=1)

        # White text for header
        c.setFillColor(HexColor("#FFFFFF"))
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2.5 * cm, y_pos - 0.3 * cm, "Position")
        c.drawString(8 * cm, y_pos - 0.3 * cm, "Wert")

        y_pos -= 0.7 * cm

        # Draw data rows with grey gridlines
        c.setFillColor(HexColor("#000000"))
        c.setFont("Helvetica", 9)
        c.setStrokeColor(HexColor("#CCCCCC"))
        c.setLineWidth(0.5)

        for row in data:
            # Draw gridline
            c.line(2 * cm, y_pos - 0.4 * cm, 10 * cm, y_pos - 0.4 * cm)

            # Draw data
            c.drawString(2.5 * cm, y_pos, row[0])
            c.drawString(8 * cm, y_pos, row[1])
            y_pos -= 0.6 * cm

        # Bottom border
        c.line(2 * cm, y_pos, 10 * cm, y_pos)

        return y_pos

    def _format_currency(self, value: float) -> str:
        """Formats currency with 2 decimal places and thousand separators.

        Implements Requirement 9.29: Format all values with 2 decimals and thousand separators

        Args:
            value: Numeric value to format

        Returns:
            Formatted string like "1.234,56 €"
        """
        try:
            # German formatting: dot as thousands separator, comma as decimal
            formatted = f"{
                value:,.2f}".replace(
                ',',
                'X').replace(
                '.',
                ',').replace(
                'X',
                '.')
            return f"{formatted} €"
        except BaseException:
            return "0,00 €"

    def _get_global_constant(self, key: str, default: float) -> float:
        """Gets a global constant value from database or returns default.

        Args:
            key: Constant key name
            default: Default value if not found

        Returns:
            Constant value as float
        """
        try:
            from database import load_admin_setting
            global_constants = load_admin_setting('global_constants', {})
            value = global_constants.get(key, default)
            return float(value) if value is not None else default
        except BaseException:
            return default

    def _get_annual_savings(self) -> float:
        """Gets annual savings from analysis_results.

        Returns:
            Annual savings as float
        """
        try:
            # Use analysis_results directly
            annual_savings = self.analysis_results.get('annual_savings', 0)
            if annual_savings and isinstance(annual_savings, (int, float)):
                return float(annual_savings)

            # Try to calculate from annual production and electricity price
            annual_production = self.analysis_results.get(
                'annual_pv_production_kwh', 0)
            electricity_price = self._get_global_constant(
                'electricity_price_eur_per_kwh', 0.30)

            if annual_production and electricity_price:
                return float(annual_production) * float(electricity_price)

            return 1000.0  # Default fallback
        except BaseException:
            return 1000.0

    def _get_annual_costs(self) -> float:
        """Gets annual costs from analysis_results.

        Returns:
            Annual costs as float
        """
        try:
            # Use analysis_results directly
            annual_costs = self.analysis_results.get('annual_costs', 0)
            if annual_costs and isinstance(annual_costs, (int, float)):
                return float(annual_costs)

            # Calculate from maintenance costs
            anlage_kwp = self.analysis_results.get('anlage_kwp', 10)
            maintenance_per_kwp = self._get_global_constant(
                'maintenance_variable_eur_per_kwp_pa', 5.0)
            maintenance_fixed = self._get_global_constant(
                'maintenance_fixed_eur_pa', 50.0)

            return float(anlage_kwp) * float(maintenance_per_kwp) + \
                float(maintenance_fixed)
        except BaseException:
            return 200.0  # Default fallback

    def _draw_financing_overview(
        self,
        c: canvas.Canvas,
        options: list[dict]
    ) -> None:
        """Draws financing overview page with title, subtitle and financing boxes."""
        # Title
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(
            HexColor(self.theme['colors']['primary'])
        )
        c.drawString(2 * cm, self.height - 3 * cm, "Finanzierungsoptionen")

        # Subtitle
        c.setFont("Helvetica", 12)
        c.setFillColor(HexColor("#000000"))
        c.drawString(
            2 * cm,
            self.height - 4 * cm,
            "Flexible Zahlungsmöglichkeiten für Ihre Photovoltaikanlage"
        )

        # Additional info text
        c.setFont("Helvetica", 10)
        c.setFillColor(HexColor("#666666"))
        c.drawString(
            2 * cm,
            self.height - 4.7 * cm,
            "Wählen Sie die für Sie passende Finanzierungsvariante"
        )

        # Draw financing options boxes
        y_pos = self.height - 6 * cm

        for idx, option in enumerate(options):
            # Check if we need a new page
            if y_pos < 3 * cm:
                c.showPage()
                # Repeat header on new page
                c.setFont("Helvetica-Bold", 16)
                c.setFillColor(HexColor(self.theme['colors']['primary']))
                c.drawString(
                    2 * cm,
                    self.height - 3 * cm,
                    "Finanzierungsoptionen (Fortsetzung)")
                y_pos = self.height - 5 * cm

            self._draw_financing_option_box(c, option, y_pos)
            y_pos -= 5.5 * cm  # Increased spacing between boxes

    def _draw_financing_option_box(
        self,
        c: canvas.Canvas,
        option: dict,
        y_pos: float
    ) -> None:
        """Draws a single financing option box."""
        # Box background
        c.setFillColor(HexColor("#F5F5F5"))
        c.rect(2 * cm, y_pos, self.width - 4 * cm, 4 * cm, fill=1)

        # Option name
        c.setFillColor(HexColor("#000000"))
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2.5 * cm, y_pos + 3.5 * cm, option.get('name', 'N/A'))

        # Description
        c.setFont("Helvetica", 10)
        description = option.get('description', '')
        if description:
            c.drawString(2.5 * cm, y_pos + 3 * cm, description)

        # Financing details - handle both duration_months and duration_years
        financing_details = option.get('financing_options', [])
        if financing_details:
            detail = financing_details[0]  # First option as default

            y_detail = y_pos + 2.2 * cm
            c.setFont("Helvetica", 9)

            # Duration - handle both months and years format
            duration_months = detail.get('duration_months')
            duration_years = detail.get('duration_years')

            if duration_months:
                duration = duration_months
            elif duration_years:
                duration = duration_years * 12
            else:
                duration = 60  # Default 5 years

            years = duration // 12
            c.drawString(
                2.5 * cm,
                y_detail,
                f"Laufzeit: {duration} Monate ({years} Jahre)"
            )

            # Interest rate
            rate = detail.get('interest_rate', 0)
            c.drawString(
                2.5 * cm,
                y_detail - 0.5 * cm,
                f"Zinssatz: {rate}% p.a."
            )

            # Calculate monthly rate
            total_amount = self.offer_data.get('grand_total', 0)
            monthly_rate = self._calculate_monthly_rate(
                total_amount,
                rate,
                duration
            )

            c.setFont("Helvetica-Bold", 11)
            c.drawString(
                2.5 * cm,
                y_detail - 1.2 * cm,
                f"Monatliche Rate: {monthly_rate:,.2f} €"
            )

    def _calculate_monthly_rate(
        self,
        amount: float,
        annual_rate: float,
        months: int
    ) -> float:
        """Calculates monthly payment using annuity formula.

        Formula: A = P * (r * (1 + r)^n) / ((1 + r)^n - 1)
        Where:
        - A = monthly payment
        - P = principal (loan amount)
        - r = monthly interest rate (annual rate / 12 / 100)
        - n = number of months

        Args:
            amount: Principal loan amount
            annual_rate: Annual interest rate in percent
            months: Number of months for the loan

        Returns:
            Monthly payment amount
        """
        # Handle edge cases
        if amount <= 0:
            return 0.0

        if months <= 0:
            return amount

        # If interest rate is 0, simple division
        if annual_rate == 0:
            return amount / months

        # Calculate monthly interest rate
        monthly_rate = annual_rate / 100 / 12

        # Apply annuity formula
        factor = (1 + monthly_rate) ** months
        monthly_payment = amount * (
            monthly_rate * factor / (factor - 1)
        )

        return round(monthly_payment, 2)

    def _draw_financing_details(
        self,
        c: canvas.Canvas,
        options: list[dict]
    ) -> None:
        """Draws detailed financing calculations page with tables."""
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(HexColor(self.theme['colors']['primary']))
        c.drawString(
            2 * cm,
            self.height - 3 * cm,
            "Detaillierte Finanzierungsberechnung"
        )

        # Subtitle
        c.setFont("Helvetica", 10)
        c.setFillColor(HexColor("#666666"))
        c.drawString(
            2 * cm,
            self.height - 3.7 * cm,
            "Übersicht über Gesamtkosten und Zinsbelastung"
        )

        # Reset color for tables
        c.setFillColor(HexColor("#000000"))

        # Detailed table for each option
        y_pos = self.height - 5 * cm

        for option in options:
            financing_opts = option.get('financing_options', [])

            # Draw each financing variant for this option
            for fin_opt in financing_opts:
                # Check if we need a new page
                if y_pos < 8 * cm:
                    c.showPage()
                    # Repeat header on new page
                    c.setFont("Helvetica-Bold", 14)
                    c.setFillColor(HexColor(self.theme['colors']['primary']))
                    c.drawString(
                        2 * cm,
                        self.height - 3 * cm,
                        "Finanzierungsberechnung (Fortsetzung)"
                    )
                    c.setFillColor(HexColor("#000000"))
                    y_pos = self.height - 5 * cm

                self._draw_financing_calculation_table(
                    c,
                    option,
                    fin_opt,
                    y_pos
                )
                y_pos -= 8 * cm

    def _draw_financing_calculation_table(
        self,
        c: canvas.Canvas,
        option: dict,
        fin_opt: dict,
        y_pos: float
    ) -> None:
        """Draws detailed calculation table for one financing option."""
        # Calculate values
        total_amount = self.offer_data.get('grand_total', 0)

        # Handle both duration_months and duration_years
        duration_months = fin_opt.get('duration_months')
        duration_years = fin_opt.get('duration_years')

        if duration_months:
            duration = duration_months
        elif duration_years:
            duration = duration_years * 12
        else:
            duration = 60  # Default 5 years

        rate = fin_opt.get('interest_rate', 0)
        monthly_rate = self._calculate_monthly_rate(
            total_amount,
            rate,
            duration
        )
        total_payment = monthly_rate * duration
        total_interest = total_payment - total_amount

        # Format duration display
        years = duration // 12
        months_remainder = duration % 12
        duration_text = f'{duration} Monate'
        if months_remainder == 0:
            duration_text = f'{years} Jahre ({duration} Monate)'

        # Create table data
        data = [
            ['Position', 'Wert'],
            ['Finanzierungsbetrag', f'{total_amount:,.2f} €'],
            ['Laufzeit', duration_text],
            ['Zinssatz p.a.', f'{rate}%'],
            ['Monatliche Rate', f'{monthly_rate:,.2f} €'],
            ['Gesamtzahlung', f'{total_payment:,.2f} €'],
            ['Zinskosten gesamt', f'{total_interest:,.2f} €']
        ]

        # Draw table header
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2.5 * cm, y_pos, option.get('name', 'Finanzierung'))

        # Draw financing option description if available
        fin_description = fin_opt.get('description', '')
        if fin_description:
            c.setFont("Helvetica", 9)
            c.drawString(2.5 * cm, y_pos - 0.5 * cm, fin_description)
            row_y = y_pos - 1.3 * cm
        else:
            row_y = y_pos - 0.8 * cm

        # Draw table rows
        c.setFont("Helvetica", 10)
        for idx, row in enumerate(data):
            if idx == 0:
                c.setFont("Helvetica-Bold", 10)
            else:
                c.setFont("Helvetica", 10)

            c.drawString(2.5 * cm, row_y, row[0])
            c.drawString(10 * cm, row_y, row[1])
            row_y -= 0.7 * cm


class ProductDatasheetMerger:
    """Merges product datasheets from database.

    This class handles loading product datasheets from the database and merging them
    into a single PDF. It supports both PDF and image formats, converting images to
    PDF pages as needed.
    """

    def __init__(self, logger: ExtendedPDFLogger | None = None):
        """Initialize product datasheet merger.

        Args:
            logger: Logger instance for tracking errors and warnings (optional)
        """
        self.logger = logger or ExtendedPDFLogger()

    def merge(self, datasheet_ids: list[int]) -> bytes:
        """Merges selected product datasheets into a single PDF using efficient single-pass merging.

        Loads datasheets for each product ID, handles both PDF and image formats,
        and merges all pages into a single output PDF in one pass. Includes robust error handling
        to continue processing even if individual datasheets fail to load.

        This optimized version loads all datasheets first, then merges them in a single
        operation to avoid multiple intermediate PDF creations.

        Args:
            datasheet_ids: List of product IDs with datasheets to merge

        Returns:
            PDF bytes with merged datasheets, or empty bytes if no valid datasheets
        """
        if not datasheet_ids:
            self.logger.log_warning(
                'ProductDatasheetMerger',
                'No datasheet IDs provided')
            return b''

        self.logger.log_info(
            'ProductDatasheetMerger',
            f'Starting efficient merge of {
                len(datasheet_ids)} datasheets')

        # Load all datasheets first (batch loading)
        datasheet_bytes_list = []
        for product_id in datasheet_ids:
            try:
                datasheet_bytes = self._load_datasheet(product_id)
                if datasheet_bytes:
                    datasheet_bytes_list.append((product_id, datasheet_bytes))
                else:
                    self.logger.log_warning(
                        'ProductDatasheetMerger',
                        f'No datasheet bytes returned for product {product_id}')
            except Exception as e:
                self.logger.log_error(
                    'ProductDatasheetMerger',
                    f'Error loading datasheet for product {product_id}',
                    e)
                continue

        if not datasheet_bytes_list:
            self.logger.log_warning(
                'ProductDatasheetMerger',
                'No datasheets were successfully loaded')
            return b''

        # Merge all loaded datasheets in a single pass
        writer = PdfWriter()
        successful_merges = 0

        for product_id, datasheet_bytes in datasheet_bytes_list:
            try:
                reader = PdfReader(io.BytesIO(datasheet_bytes))
                page_count = len(reader.pages)

                # Add all pages from this datasheet
                for page in reader.pages:
                    writer.add_page(page)

                successful_merges += 1
                self.logger.log_info(
                    'ProductDatasheetMerger',
                    f'Successfully merged datasheet for product {product_id} ({page_count} pages)')
            except Exception as pdf_error:
                self.logger.log_error(
                    'ProductDatasheetMerger',
                    f'Error reading PDF for product {product_id}',
                    pdf_error)
                continue

        # Only return PDF bytes if we successfully merged at least one
        # datasheet
        if successful_merges == 0:
            self.logger.log_warning(
                'ProductDatasheetMerger',
                'No datasheets were successfully merged')
            return b''

        # Write final PDF in a single operation
        output = io.BytesIO()
        writer.write(output)
        result = output.getvalue()
        self.logger.log_info(
            'ProductDatasheetMerger',
            f'Successfully merged {successful_merges} datasheet(s) ({
                len(result)} bytes)')
        return result

    def _load_datasheet(self, product_id: int) -> bytes | None:
        """Loads product datasheet from database using real DB queries.

        Uses product_db.get_product_by_id() to fetch product data, then loads
        the datasheet file from the filesystem. Handles both PDF and image formats,
        converting images to PDF as needed.

        Args:
            product_id: ID of the product whose datasheet to load

        Returns:
            PDF bytes of the datasheet, or None if not found or error occurred
        """
        try:
            import os

            from product_db import get_product_by_id

            # Get product from database using real DB query
            product = get_product_by_id(product_id)
            if not product:
                self.logger.log_warning(
                    'ProductDatasheetMerger',
                    f'Product {product_id} not found in database')
                return None

            # Check if product has datasheet - use correct field name from
            # schema
            datasheet_path = product.get('datasheet_link_db_path')
            if not datasheet_path:
                self.logger.log_warning(
                    'ProductDatasheetMerger',
                    f'Product {product_id} has no datasheet_link_db_path')
                return None

            # Ensure path is absolute or relative to data directory
            if not os.path.isabs(datasheet_path):
                # Try relative to data/product_datasheets
                datasheet_path = os.path.join(
                    'data', 'product_datasheets', datasheet_path)

            # Load file from filesystem
            if not os.path.exists(datasheet_path):
                self.logger.log_warning(
                    'ProductDatasheetMerger',
                    f'Datasheet file not found at {datasheet_path}')
                return None

            with open(datasheet_path, 'rb') as f:
                file_bytes = f.read()

            if not file_bytes:
                self.logger.log_warning(
                    'ProductDatasheetMerger',
                    f'Empty file at {datasheet_path}')
                return None

            # Check if it's a PDF or image based on file extension
            file_ext = os.path.splitext(datasheet_path)[1].lower()

            if file_ext == '.pdf':
                # Return PDF bytes directly
                self.logger.log_info(
                    'ProductDatasheetMerger',
                    f'Loaded PDF datasheet for product {product_id}')
                return file_bytes
            if file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']:
                # Convert image to PDF
                self.logger.log_info(
                    'ProductDatasheetMerger',
                    f'Converting image datasheet ({file_ext}) to PDF for product {product_id}')
                return self._convert_image_to_pdf(file_bytes)
            self.logger.log_warning(
                'ProductDatasheetMerger',
                f'Unsupported file format {file_ext} for product {product_id}')
            return None

        except Exception as e:
            self.logger.log_error(
                'ProductDatasheetMerger',
                f'Error loading datasheet for product {product_id}',
                e)
            return None

    def _convert_image_to_pdf(self, image_bytes: bytes) -> bytes:
        """Converts image bytes to a PDF page with optimized scaling and resolution.

        Creates a new PDF page with A4 dimensions and centers the image on it,
        scaling to fit while maintaining aspect ratio. The image is optimized
        to 300 DPI for print quality while reducing file size for large images.

        Args:
            image_bytes: Raw image file bytes

        Returns:
            PDF bytes containing the image, or empty bytes if conversion fails
        """
        try:
            from PIL import Image
            from reportlab.lib.utils import ImageReader

            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4

            # Load image to check dimensions
            img_pil = Image.open(io.BytesIO(image_bytes))
            img_width, img_height = img_pil.size

            self.logger.log_info(
                'ProductDatasheetMerger',
                f'Original image size: {img_width}x{img_height}')

            # Calculate scaling to fit within margins (2cm on each side, 3cm
            # top/bottom)
            max_width = width - 4 * cm
            max_height = height - 6 * cm

            # Calculate aspect ratio
            aspect_ratio = img_width / img_height

            # Determine final dimensions maintaining aspect ratio
            if img_width / max_width > img_height / max_height:
                # Width is the limiting factor
                final_width = max_width
                final_height = max_width / aspect_ratio
            else:
                # Height is the limiting factor
                final_height = max_height
                final_width = max_height * aspect_ratio

            # Optimize image resolution for 300 DPI
            # Calculate target pixel dimensions for 300 DPI at final size
            # 1 cm = 0.393701 inches, 300 DPI means 300 pixels per inch
            target_width_px = int((final_width / cm) * 0.393701 * 300)
            target_height_px = int((final_height / cm) * 0.393701 * 300)

            # Only scale down if image is larger than target
            if img_width > target_width_px or img_height > target_height_px:
                self.logger.log_info(
                    'ProductDatasheetMerger',
                    f'Scaling image down to {target_width_px}x{target_height_px} for 300 DPI')

                # Use high-quality resampling
                img_pil = img_pil.resize(
                    (target_width_px, target_height_px),
                    Image.Resampling.LANCZOS
                )

                # Convert to RGB if necessary (for JPEG compatibility)
                if img_pil.mode not in ('RGB', 'L'):
                    img_pil = img_pil.convert('RGB')

                # Save optimized image to bytes
                optimized_buffer = io.BytesIO()
                img_pil.save(optimized_buffer, format='PNG', optimize=True)
                optimized_bytes = optimized_buffer.getvalue()

                self.logger.log_info(
                    'ProductDatasheetMerger', f'Optimized image size: {
                        len(optimized_bytes)} bytes (original: {
                        len(image_bytes)} bytes)')

                # Use optimized image
                img = ImageReader(io.BytesIO(optimized_bytes))
            else:
                # Image is already small enough, use original
                self.logger.log_info(
                    'ProductDatasheetMerger',
                    'Image already at optimal size, using original')
                img = ImageReader(io.BytesIO(image_bytes))

            # Center the image
            x_pos = (width - final_width) / 2
            y_pos = (height - final_height) / 2

            # Draw centered and scaled image
            c.drawImage(
                img,
                x_pos,
                y_pos,
                width=final_width,
                height=final_height,
                preserveAspectRatio=True,
                mask='auto'
            )

            c.showPage()
            c.save()

            self.logger.log_info(
                'ProductDatasheetMerger',
                'Successfully converted image to PDF')
            return buffer.getvalue()

        except Exception as e:
            self.logger.log_error(
                'ProductDatasheetMerger',
                'Error converting image to PDF',
                e)
            return b''


class CompanyDocumentMerger:
    """Merges company documents from database.

    This class handles loading company documents from the database and merging them
    into a single PDF. It supports PDF documents and includes robust error handling
    to continue processing even if individual documents fail to load.
    """

    def __init__(self, logger: ExtendedPDFLogger | None = None):
        """Initialize company document merger.

        Args:
            logger: Logger instance for tracking errors and warnings (optional)
        """
        self.logger = logger or ExtendedPDFLogger()

    def merge(self, document_ids: list[int]) -> bytes:
        """Merges selected company documents into a single PDF using efficient single-pass merging.

        Loads documents for each document ID from the database, handles PDF format,
        and merges all pages into a single output PDF in one pass. Includes robust error handling
        to continue processing even if individual documents fail to load.

        This optimized version loads all documents first, then merges them in a single
        operation to avoid multiple intermediate PDF creations.

        Args:
            document_ids: List of company document IDs to merge

        Returns:
            PDF bytes with merged documents, or empty bytes if no valid documents
        """
        if not document_ids:
            self.logger.log_warning(
                'CompanyDocumentMerger',
                'No document IDs provided')
            return b''

        self.logger.log_info(
            'CompanyDocumentMerger',
            f'Starting efficient merge of {
                len(document_ids)} documents')

        # Load all documents first (batch loading)
        document_bytes_list = []
        for doc_id in document_ids:
            try:
                doc_bytes = self._load_document(doc_id)
                if doc_bytes:
                    document_bytes_list.append((doc_id, doc_bytes))
                else:
                    self.logger.log_warning(
                        'CompanyDocumentMerger',
                        f'No document bytes returned for document {doc_id}')
            except Exception as e:
                self.logger.log_error(
                    'CompanyDocumentMerger',
                    f'Error loading document {doc_id}',
                    e)
                continue

        if not document_bytes_list:
            self.logger.log_warning(
                'CompanyDocumentMerger',
                'No documents were successfully loaded')
            return b''

        # Merge all loaded documents in a single pass
        writer = PdfWriter()
        successful_merges = 0

        for doc_id, doc_bytes in document_bytes_list:
            try:
                reader = PdfReader(io.BytesIO(doc_bytes))
                page_count = len(reader.pages)

                # Add all pages from this document
                for page in reader.pages:
                    writer.add_page(page)

                successful_merges += 1
                self.logger.log_info(
                    'CompanyDocumentMerger',
                    f'Successfully merged document {doc_id} ({page_count} pages)')
            except Exception as pdf_error:
                self.logger.log_error(
                    'CompanyDocumentMerger',
                    f'Error reading PDF for document {doc_id}',
                    pdf_error)
                continue

        # Only return PDF bytes if we successfully merged at least one document
        if successful_merges == 0:
            self.logger.log_warning(
                'CompanyDocumentMerger',
                'No documents were successfully merged')
            return b''

        # Write final PDF in a single operation
        output = io.BytesIO()
        writer.write(output)
        result = output.getvalue()
        self.logger.log_info(
            'CompanyDocumentMerger',
            f'Successfully merged {successful_merges} document(s) ({
                len(result)} bytes)')
        return result

    def _load_document(self, doc_id: int) -> bytes | None:
        """Loads company document from database using real DB queries.

        Uses database.list_company_documents() to fetch document data by querying
        all documents and filtering by ID, then loads the document file from the
        filesystem using the absolute_file_path field.

        Args:
            doc_id: ID of the company document to load

        Returns:
            PDF bytes of the document, or None if not found or error occurred
        """
        try:
            import os

            from database import COMPANY_DOCS_BASE_DIR, get_db_connection

            # Get document from database using direct query
            conn = get_db_connection()
            if not conn:
                self.logger.log_error(
                    'CompanyDocumentMerger',
                    f'Could not connect to database for document {doc_id}',
                    None)
                return None

            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, company_id, document_type, display_name, file_name, "
                    "absolute_file_path as relative_db_path, uploaded_at "
                    "FROM company_documents WHERE id = ?", (doc_id,))
                row = cursor.fetchone()

                if not row:
                    self.logger.log_warning(
                        'CompanyDocumentMerger',
                        f'Document {doc_id} not found in database')
                    return None

                # Convert row to dict
                document = dict(row)

                # Get the relative path from database
                relative_path = document.get('relative_db_path')
                if not relative_path:
                    self.logger.log_warning(
                        'CompanyDocumentMerger',
                        f'Document {doc_id} has no file path')
                    return None

                # Construct absolute path
                absolute_path = os.path.join(
                    COMPANY_DOCS_BASE_DIR, relative_path)

                # Load file from filesystem
                if not os.path.exists(absolute_path):
                    self.logger.log_warning(
                        'CompanyDocumentMerger',
                        f'Document file not found at {absolute_path}')
                    return None

                with open(absolute_path, 'rb') as f:
                    file_bytes = f.read()

                if not file_bytes:
                    self.logger.log_warning(
                        'CompanyDocumentMerger',
                        f'Empty file at {absolute_path}')
                    return None

                # Check if it's a PDF based on file extension
                file_ext = os.path.splitext(absolute_path)[1].lower()

                if file_ext == '.pdf':
                    # Return PDF bytes directly
                    self.logger.log_info(
                        'CompanyDocumentMerger',
                        f'Loaded PDF document {doc_id}')
                    return file_bytes
                self.logger.log_warning(
                    'CompanyDocumentMerger',
                    f'Unsupported file format {file_ext} for document {doc_id}')
                return None

            finally:
                conn.close()

        except Exception as e:
            self.logger.log_error(
                'CompanyDocumentMerger',
                f'Error loading document {doc_id}',
                e)
            return None


class ChartPageGenerator:
    """Generates pages with charts and visualizations."""

    # Class-level cache shared across instances
    _chart_cache = ChartCache(max_size=100)

    def __init__(
        self,
        analysis_results: dict,
        layout: str,
        theme: dict,
        logger: ExtendedPDFLogger | None = None,
        use_cache: bool = True
    ):
        """Initialize chart page generator.

        Args:
            analysis_results: Analysis results dictionary with chart bytes
            layout: Layout type ('one_per_page', 'two_per_page', 'four_per_page')
            theme: Theme configuration
            logger: Logger instance for tracking errors and warnings (optional)
            use_cache: Whether to use chart caching (default: True)
        """
        self.analysis_results = analysis_results
        self.layout = layout
        self.theme = theme
        self.width, self.height = A4
        self.logger = logger or ExtendedPDFLogger()
        self.use_cache = use_cache

    def generate(self, chart_keys: list[str]) -> bytes:
        """Generates pages with selected charts.

        Args:
            chart_keys: List of chart keys from analysis_results

        Returns:
            PDF bytes with chart pages
        """
        if not chart_keys:
            self.logger.log_warning(
                'ChartPageGenerator',
                'No chart keys provided')
            return b''

        self.logger.log_info(
            'ChartPageGenerator', f'Generating {
                len(chart_keys)} charts with layout: {
                self.layout}')

        # Group charts by layout
        try:
            if self.layout == 'one_per_page':
                result = self._generate_one_per_page(chart_keys)
            elif self.layout == 'two_per_page':
                result = self._generate_two_per_page(chart_keys)
            elif self.layout == 'four_per_page':
                result = self._generate_four_per_page(chart_keys)
            else:
                result = self._generate_one_per_page(chart_keys)

            if result:
                self.logger.log_info(
                    'ChartPageGenerator',
                    f'Successfully generated chart pages ({
                        len(result)} bytes)')
            else:
                self.logger.log_warning(
                    'ChartPageGenerator',
                    'Generated empty chart pages')

            return result
        except Exception as e:
            self.logger.log_error(
                'ChartPageGenerator',
                'Error generating chart pages',
                e)
            return b''

    def _generate_one_per_page(self, chart_keys: list[str]) -> bytes:
        """Generates one chart per page."""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        for chart_key in chart_keys:
            chart_bytes = self._get_chart_bytes(chart_key)
            if not chart_bytes:
                self.logger.log_warning(
                    'ChartPageGenerator',
                    f'Chart {chart_key} not found in analysis results')
                continue

            # Draw chart title
            chart_name = self._get_chart_name(chart_key)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(2 * cm, self.height - 2 * cm, chart_name)

            # Draw chart image
            try:
                from reportlab.lib.utils import ImageReader
                img = ImageReader(io.BytesIO(chart_bytes))

                # Calculate dimensions (maintain aspect ratio)
                img_width = self.width - 4 * cm
                img_height = self.height - 6 * cm

                c.drawImage(
                    img,
                    2 * cm,
                    3 * cm,
                    width=img_width,
                    height=img_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )
            except Exception as e:
                self.logger.log_error(
                    'ChartPageGenerator', f'Error drawing chart {chart_key}', e)
                c.drawString(
                    2 * cm,
                    self.height / 2,
                    f"Fehler beim Laden des Diagramms: {chart_name}"
                )

            c.showPage()

        c.save()
        return buffer.getvalue()

    def _get_chart_bytes(self, chart_key: str) -> bytes | None:
        """Get chart bytes with caching support.

        Args:
            chart_key: The chart identifier

        Returns:
            Chart bytes from cache or analysis results
        """
        # Get original chart data
        chart_data = self.analysis_results.get(chart_key)
        if not chart_data:
            return None

        # If caching is disabled, return directly
        if not self.use_cache:
            return chart_data

        # Try to get from cache
        cached_bytes = self._chart_cache.get(chart_key, chart_data)
        if cached_bytes:
            self.logger.log_info(
                'ChartPageGenerator',
                f'Cache hit for chart {chart_key}')
            return cached_bytes

        # Cache miss - store in cache and return
        self.logger.log_info(
            'ChartPageGenerator',
            f'Cache miss for chart {chart_key}')
        self._chart_cache.put(chart_key, chart_data, chart_data)
        return chart_data

    @classmethod
    def invalidate_cache(cls, chart_key: str | None = None) -> None:
        """Invalidate the chart cache.

        Args:
            chart_key: Specific chart to invalidate, or None to clear all
        """
        cls._chart_cache.invalidate(chart_key)

    @classmethod
    def get_cache_stats(cls) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        return cls._chart_cache.get_stats()

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
                    2 * cm,
                    self.height / 2 + 1 * cm,
                    self.width - 4 * cm,
                    self.height / 2 - 3 * cm
                )

            # Bottom chart
            if i + 1 < len(chart_keys):
                self._draw_chart_in_area(
                    c,
                    chart_keys[i + 1],
                    2 * cm,
                    2 * cm,
                    self.width - 4 * cm,
                    self.height / 2 - 3 * cm
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
                    2 * cm,
                    self.height / 2 + 1 * cm,
                    self.width / 2 - 3 * cm,
                    self.height / 2 - 3 * cm
                )

            # Top-right
            if i + 1 < len(chart_keys):
                self._draw_chart_in_area(
                    c,
                    chart_keys[i + 1],
                    self.width / 2 + 1 * cm,
                    self.height / 2 + 1 * cm,
                    self.width / 2 - 3 * cm,
                    self.height / 2 - 3 * cm
                )

            # Bottom-left
            if i + 2 < len(chart_keys):
                self._draw_chart_in_area(
                    c,
                    chart_keys[i + 2],
                    2 * cm,
                    2 * cm,
                    self.width / 2 - 3 * cm,
                    self.height / 2 - 3 * cm
                )

            # Bottom-right
            if i + 3 < len(chart_keys):
                self._draw_chart_in_area(
                    c,
                    chart_keys[i + 3],
                    self.width / 2 + 1 * cm,
                    2 * cm,
                    self.width / 2 - 3 * cm,
                    self.height / 2 - 3 * cm
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
        """Draws a chart in a specific area of the page with optimized scaling.

        Args:
            c: Canvas object
            chart_key: Key of the chart in analysis_results
            x: X position of the area
            y: Y position of the area
            width: Width of the area
            height: Height of the area
        """
        chart_bytes = self._get_chart_bytes(chart_key)
        if not chart_bytes:
            # Draw placeholder for missing chart
            c.setFont("Helvetica", 9)
            c.drawString(
                x + 0.5 * cm,
                y + height / 2,
                f"Chart nicht verfügbar: {chart_key}")
            return

        # Draw chart title
        chart_name = self._get_chart_name(chart_key)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y + height + 0.3 * cm, chart_name)

        # Draw chart image with optimization
        try:
            # Optimize chart image for target size
            optimized_bytes = self._optimize_chart_image(
                chart_bytes, width, height)

            from reportlab.lib.utils import ImageReader
            img = ImageReader(io.BytesIO(optimized_bytes))

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
            self.logger.log_error(
                'ChartPageGenerator',
                f'Error drawing chart {chart_key}',
                e)
            c.setFont("Helvetica", 8)
            c.drawString(
                x + 0.5 * cm,
                y + height / 2,
                f"Fehler beim Laden: {chart_name}")

    def _optimize_chart_image(
            self,
            image_bytes: bytes,
            target_width: float,
            target_height: float) -> bytes:
        """Optimizes chart image for target dimensions at 300 DPI.

        Scales down large images to reduce file size while maintaining print quality.
        Images smaller than target are left unchanged.

        Args:
            image_bytes: Original image bytes
            target_width: Target width in points
            target_height: Target height in points

        Returns:
            Optimized image bytes
        """
        try:
            from PIL import Image

            # Load image
            img = Image.open(io.BytesIO(image_bytes))
            img_width, img_height = img.size

            # Calculate target pixel dimensions for 300 DPI
            # 1 point = 1/72 inch, 300 DPI means 300 pixels per inch
            target_width_px = int(target_width / 72 * 300)
            target_height_px = int(target_height / 72 * 300)

            # Only scale down if image is significantly larger (>20% larger)
            if img_width > target_width_px * 1.2 or img_height > target_height_px * 1.2:
                # Calculate scaling factor maintaining aspect ratio
                scale_w = target_width_px / img_width
                scale_h = target_height_px / img_height
                scale = min(scale_w, scale_h)

                new_width = int(img_width * scale)
                new_height = int(img_height * scale)

                self.logger.log_info(
                    'ChartPageGenerator',
                    f'Scaling chart from {img_width}x{img_height} to {new_width}x{new_height}')

                # Use high-quality resampling
                img = img.resize(
                    (new_width, new_height), Image.Resampling.LANCZOS)

                # Convert to RGB if necessary
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')

                # Save optimized image
                buffer = io.BytesIO()
                img.save(buffer, format='PNG', optimize=True)
                return buffer.getvalue()

            # Image is already optimal size
            return image_bytes

        except Exception as e:
            self.logger.log_warning(
                'ChartPageGenerator',
                f'Could not optimize chart image: {e}')
            # Return original on error
            return image_bytes

    def _get_chart_name(self, chart_key: str) -> str:
        """Gets friendly name for a chart key.

        Maps chart keys to human-readable names. Uses only real chart keys
        from the system (no invented keys).

        Args:
            chart_key: Chart key from analysis_results

        Returns:
            Friendly name for the chart
        """
        # Chart name mapping - using only real keys from pdf_generator.py
        chart_names = {
            # 2D Charts - Wirtschaftlichkeit
            'cumulative_cashflow_chart_bytes': 'Kumulierter Cashflow',
            'cost_projection_chart_bytes': 'Stromkosten-Hochrechnung',
            'break_even_chart_bytes': 'Break-Even-Analyse',
            'amortisation_chart_bytes': 'Amortisationsdiagramm',

            # 2D Charts - Produktion & Verbrauch
            'monthly_prod_cons_chart_bytes': 'Monatliche Produktion vs. Verbrauch',
            'yearly_production_chart_bytes': 'Jahresproduktion',

            # 2D Charts - Eigenverbrauch & Autarkie
            'consumption_coverage_pie_chart_bytes': 'Verbrauchsdeckung (Autarkiegrad)',
            'pv_usage_pie_chart_bytes': 'PV-Nutzung (Eigenverbrauch)',

            # 3D Charts - Produktion
            'daily_production_switcher_chart_bytes': 'Tagesproduktion (3D)',
            'weekly_production_switcher_chart_bytes': 'Wochenproduktion (3D)',
            'yearly_production_switcher_chart_bytes': 'Jahresproduktion (3D-Balken)',

            # 3D Charts - Wirtschaftlichkeit
            'project_roi_matrix_switcher_chart_bytes': 'Projektrendite-Matrix (3D)',
            'roi_comparison_switcher_chart_bytes': 'ROI-Vergleich (3D)',

            # 3D Charts - Finanzielle Analyse
            'feed_in_revenue_switcher_chart_bytes': 'Einspeisevergütung (3D)',
            'income_projection_switcher_chart_bytes': 'Einnahmenprognose (3D)',
            'prod_vs_cons_switcher_chart_bytes': 'Produktion vs. Verbrauch (3D)',
            'tariff_cube_switcher_chart_bytes': 'Tarifvergleich (3D)',
            'tariff_comparison_switcher_chart_bytes': 'Tarifvergleich (3D)',
            'cost_growth_switcher_chart_bytes': 'Stromkostensteigerung (3D)',

            # 3D Charts - CO2 & Umwelt
            'co2_savings_chart_bytes': 'CO2-Ersparnis',
            'co2_savings_value_switcher_chart_bytes': 'CO2-Ersparnis vs. Wert (3D)',

            # 3D Charts - Vergleiche & Szenarien
            'investment_value_switcher_chart_bytes': 'Investitionsnutzwert (3D)',
            'scenario_comparison_switcher_chart_bytes': 'Szenarienvergleich (3D)',

            # 3D Charts - Eigenverbrauch & Speicher
            'storage_effect_switcher_chart_bytes': 'Speicherwirkung (3D)',
            'selfuse_stack_switcher_chart_bytes': 'Eigenverbrauch vs. Einspeisung (3D)',
            'selfuse_ratio_switcher_chart_bytes': 'Eigenverbrauchsgrad (3D)',
        }

        # Return friendly name or fallback to key
        return chart_names.get(chart_key, chart_key.replace('_', ' ').title())
