"""
PDF Page Protection Module

Implements intelligent page protection for extended PDF pages (pages 9+).
Ensures that related elements (charts, descriptions, tables) stay together
and are not split across pages.

This module provides:
- KeepTogether wrappers for charts and descriptions
- Automatic PageBreak insertion when space is insufficient
- Special handling for financing information
- Logging of all page protection decisions

Author: Kiro AI Assistant
Date: 2025-01-10
"""

import logging

from reportlab.lib.units import cm
from reportlab.platypus import (
    Flowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    Spacer,
    Table,
)


class ConditionalPageBreak(Flowable):
    """A conditional page break that only triggers if not enough space.

    This flowable checks if there's enough space for the next element
    and inserts a page break if needed. It's more intelligent than a
    regular PageBreak as it only breaks when necessary.
    """

    def __init__(self, min_space_needed: float = 3 * cm):
        """Initialize conditional page break.

        Args:
            min_space_needed: Minimum space needed to avoid break (default: 3cm)
        """
        Flowable.__init__(self)
        self.min_space_needed = min_space_needed
        self.width = 0
        self.height = 0

    def wrap(self, availWidth: float,
             availHeight: float) -> tuple[float, float]:
        """Check if page break is needed.

        Args:
            availWidth: Available width
            availHeight: Available height

        Returns:
            Tuple of (width, height) - triggers break if not enough space
        """
        if availHeight < self.min_space_needed:
            # Not enough space - trigger page break
            return (availWidth, availHeight + 1)  # Request more than available
        # Enough space - no break needed
        return (0, 0)

    def draw(self):
        """Draw method (does nothing)."""


class PageProtectionManager:
    """Manages page protection for extended PDF pages.

    This class provides intelligent page protection that ensures related
    elements stay together on the same page. It applies only to pages 9+
    (extended PDF pages) and leaves pages 1-8 (standard PDF) unchanged.
    """

    def __init__(
        self,
        doc_height: float,
        min_space_at_bottom: float = 3 * cm,
        enable_logging: bool = True
    ):
        """Initialize the page protection manager.

        Args:
            doc_height: Document height in points
            min_space_at_bottom: Minimum space to reserve at page bottom (default: 3cm)
            enable_logging: Whether to log page protection decisions (default: True)
        """
        self.doc_height = doc_height
        self.min_space_at_bottom = min_space_at_bottom
        self.enable_logging = enable_logging
        self.logger = logging.getLogger(__name__)

        # Track current page number (will be updated externally)
        self.current_page = 1

        # Track protection decisions for reporting
        self.protection_log: list[dict] = []

    def set_current_page(self, page_num: int) -> None:
        """Update the current page number.

        Args:
            page_num: Current page number
        """
        self.current_page = page_num

    def should_apply_protection(self) -> bool:
        """Check if page protection should be applied.

        Page protection only applies to pages 9+ (extended PDF pages).
        Pages 1-8 (standard PDF) are not affected.

        This is a critical method that ensures:
        - Pages 1-8 (standard PDF with templates) remain unchanged
        - Pages 9+ (extended PDF with charts, financing, etc.) get protection
        - Financing information on pages 9+ is especially protected

        Returns:
            True if protection should be applied, False otherwise
        """
        return self.current_page >= 9

    def wrap_chart_with_description(
        self,
        chart: Flowable,
        title: Paragraph,
        description: Paragraph | None = None,
        chart_key: str = ""
    ) -> Flowable:
        """Wrap a chart with its title and description using KeepTogether.

        This ensures that the chart, title, and description always appear
        together on the same page and are never split.

        Args:
            chart: Chart flowable (Image or custom chart flowable)
            title: Title paragraph
            description: Optional description paragraph
            chart_key: Chart identifier for logging

        Returns:
            KeepTogether flowable containing all elements, or the elements
            as-is if protection is not applicable
        """
        if not self.should_apply_protection():
            # No protection for pages 1-8
            elements = [title, Spacer(1, 0.3 * cm), chart]
            if description:
                elements.extend([Spacer(1, 0.3 * cm), description])
            return elements

        # Build element list
        elements = [
            title,
            Spacer(1, 0.3 * cm),
            chart
        ]

        if description:
            elements.extend([
                Spacer(1, 0.3 * cm),
                description
            ])

        # Wrap in KeepTogether
        protected = KeepTogether(elements)

        # Log the protection decision
        self._log_protection(
            element_type='chart_with_description',
            element_id=chart_key,
            page=self.current_page,
            action='wrapped_in_keeptogether'
        )

        return protected

    def wrap_table_with_title(
        self,
        table: Table,
        title: Paragraph,
        table_id: str = ""
    ) -> Flowable:
        """Wrap a table with its title using KeepTogether.

        Args:
            table: Table flowable
            title: Title paragraph
            table_id: Table identifier for logging

        Returns:
            KeepTogether flowable containing title and table
        """
        if not self.should_apply_protection():
            return [title, Spacer(1, 0.3 * cm), table]

        elements = [
            title,
            Spacer(1, 0.3 * cm),
            table
        ]

        protected = KeepTogether(elements)

        self._log_protection(
            element_type='table_with_title',
            element_id=table_id,
            page=self.current_page,
            action='wrapped_in_keeptogether'
        )

        return protected

    def wrap_financing_section(
        self,
        title: Paragraph,
        table: Table,
        description: Paragraph | None = None,
        section_id: str = ""
    ) -> Flowable:
        """Wrap a financing section (title, table, description) using KeepTogether.

        Financing sections are treated with extra care to ensure they stay
        together, as they contain critical financial information.

        This method applies STRICT protection for financing information:
        - Always applies on pages 9+ (extended PDF)
        - Never splits financing tables across pages
        - Keeps title, table, and description together
        - Logs all protection decisions for financing sections

        Args:
            title: Section title paragraph
            table: Financing table
            description: Optional description paragraph
            section_id: Section identifier for logging

        Returns:
            KeepTogether flowable containing all elements
        """
        if not self.should_apply_protection():
            elements = [title, Spacer(1, 0.3 * cm), table]
            if description:
                elements.extend([Spacer(1, 0.5 * cm), description])
            return elements

        elements = [
            title,
            Spacer(1, 0.3 * cm),
            table
        ]

        if description:
            elements.extend([
                Spacer(1, 0.5 * cm),
                description
            ])

        protected = KeepTogether(elements)

        self._log_protection(
            element_type='financing_section',
            element_id=section_id,
            page=self.current_page,
            action='wrapped_in_keeptogether_strict',
            details='strict_protection_for_financing'
        )

        return protected

    def wrap_chart_with_legend(
        self,
        chart: Flowable,
        legend: Flowable,
        chart_key: str = ""
    ) -> Flowable:
        """Wrap a chart with its legend using KeepTogether.

        Args:
            chart: Chart flowable
            legend: Legend flowable
            chart_key: Chart identifier for logging

        Returns:
            KeepTogether flowable containing chart and legend
        """
        if not self.should_apply_protection():
            return [chart, Spacer(1, 0.2 * cm), legend]

        elements = [
            chart,
            Spacer(1, 0.2 * cm),
            legend
        ]

        protected = KeepTogether(elements)

        self._log_protection(
            element_type='chart_with_legend',
            element_id=chart_key,
            page=self.current_page,
            action='wrapped_in_keeptogether'
        )

        return protected

    def wrap_chart_with_footnote(
        self,
        chart: Flowable,
        footnote: Paragraph,
        chart_key: str = ""
    ) -> Flowable:
        """Wrap a chart with its footnote using KeepTogether.

        Args:
            chart: Chart flowable
            footnote: Footnote paragraph
            chart_key: Chart identifier for logging

        Returns:
            KeepTogether flowable containing chart and footnote
        """
        if not self.should_apply_protection():
            return [chart, Spacer(1, 0.2 * cm), footnote]

        elements = [
            chart,
            Spacer(1, 0.2 * cm),
            footnote
        ]

        protected = KeepTogether(elements)

        self._log_protection(
            element_type='chart_with_footnote',
            element_id=chart_key,
            page=self.current_page,
            action='wrapped_in_keeptogether'
        )

        return protected

    def add_spacing_between_charts(
        self,
        spacing: float = 1.0 * cm
    ) -> Spacer:
        """Add appropriate spacing between consecutive charts.

        Args:
            spacing: Spacing amount in points (default: 1cm)

        Returns:
            Spacer flowable
        """
        return Spacer(1, spacing)

    def create_conditional_pagebreak(
        self,
        min_space_needed: float = 3 * cm
    ) -> ConditionalPageBreak:
        """Create a conditional page break.

        This page break only triggers if there's not enough space
        on the current page for the next element.

        Args:
            min_space_needed: Minimum space needed to avoid break (default: 3cm)

        Returns:
            ConditionalPageBreak flowable
        """
        if not self.should_apply_protection():
            # Return a zero-height spacer for pages 1-8
            return Spacer(1, 0)

        self._log_protection(
            element_type='conditional_pagebreak',
            element_id='',
            page=self.current_page,
            action='conditional_pagebreak_created',
            details=f'min_space={min_space_needed:.1f}'
        )

        return ConditionalPageBreak(min_space_needed)

    def check_if_pagebreak_needed(
        self,
        element_height: float,
        current_position: float
    ) -> bool:
        """Check if a PageBreak is needed before adding an element.

        Args:
            element_height: Height of the element to be added
            current_position: Current vertical position on page

        Returns:
            True if PageBreak is needed, False otherwise
        """
        if not self.should_apply_protection():
            return False

        # Calculate available space
        available_space = current_position - self.min_space_at_bottom

        # Check if element fits
        needs_break = element_height > available_space

        if needs_break:
            self._log_protection(
                element_type='pagebreak',
                element_id='',
                page=self.current_page,
                action='pagebreak_inserted',
                details=f'element_height={
                    element_height:.1f}, available={
                    available_space:.1f}')

        return needs_break

    def create_pagebreak_if_needed(
        self,
        element_height: float,
        current_position: float
    ) -> PageBreak | None:
        """Create a PageBreak if needed before adding an element.

        Args:
            element_height: Height of the element to be added
            current_position: Current vertical position on page

        Returns:
            PageBreak flowable if needed, None otherwise
        """
        if self.check_if_pagebreak_needed(element_height, current_position):
            return PageBreak()
        return None

    def prevent_orphan_heading(
        self,
        heading: Paragraph,
        following_content: list[Flowable]
    ) -> list[Flowable]:
        """Prevent a heading from appearing alone at the bottom of a page.

        If a heading would appear at the bottom of a page without its
        following content, this method ensures they stay together.

        Args:
            heading: Heading paragraph
            following_content: Content that follows the heading

        Returns:
            List of flowables with appropriate protection
        """
        if not self.should_apply_protection():
            return [heading] + following_content

        # Wrap heading with at least the first element of following content
        if following_content:
            elements_to_keep = [heading, following_content[0]]
            remaining = following_content[1:]

            protected = KeepTogether(elements_to_keep)

            self._log_protection(
                element_type='orphan_heading_prevention',
                element_id='',
                page=self.current_page,
                action='heading_protected_with_content'
            )

            return [protected] + remaining
        return [heading]

    def check_space_for_paragraph(
        self,
        paragraph: Paragraph,
        available_height: float
    ) -> bool:
        """Check if there's enough space for a paragraph.

        Args:
            paragraph: Paragraph to check
            available_height: Available height on current page

        Returns:
            True if paragraph fits, False otherwise
        """
        if not self.should_apply_protection():
            return True

        # Estimate paragraph height (rough estimate)
        # In practice, reportlab will handle this automatically
        # This is mainly for logging purposes
        estimated_height = 1.0 * cm  # Conservative estimate

        return available_height >= estimated_height + self.min_space_at_bottom

    def handle_oversized_element(
        self,
        element: Flowable,
        max_height: float,
        element_id: str = ""
    ) -> list[Flowable]:
        """Handle an element that is too large for a single page.

        When a KeepTogether element is too large for a single page,
        this method handles it gracefully:
        1. Logs the oversized element for debugging
        2. Returns the element as-is (ReportLab will split automatically)
        3. Documents the decision in the protection log

        Special cases handled:
        - Very large charts: Returned as-is, may overflow page
        - Large tables: ReportLab splits automatically
        - Multiple consecutive charts: Spacing is adjusted

        Args:
            element: The oversized flowable
            max_height: Maximum height available on a page
            element_id: Element identifier for logging

        Returns:
            List of flowables (may be split or original)
        """
        self._log_protection(
            element_type='oversized_element',
            element_id=element_id,
            page=self.current_page,
            action='oversized_element_detected',
            details=f'max_height={
                max_height:.1f}, allowing_reportlab_auto_split')

        # Return the element as-is
        # ReportLab's platypus framework will handle splitting automatically
        # KeepTogether will be relaxed if the element is too large
        return [element]

    def add_spacing_with_pagebreak_check(
        self,
        spacing: float = 1.0 * cm,
        min_space_for_next: float = 5.0 * cm
    ) -> list[Flowable]:
        """Add spacing between elements with automatic page break if needed.

        This method adds spacing between consecutive elements (e.g., charts)
        and automatically inserts a page break if there's not enough space
        for the next element.

        Args:
            spacing: Spacing amount (default: 1cm)
            min_space_for_next: Minimum space needed for next element (default: 5cm)

        Returns:
            List of flowables (spacer and possibly conditional page break)
        """
        if not self.should_apply_protection():
            return [Spacer(1, spacing)]

        elements = [
            Spacer(1, spacing),
            self.create_conditional_pagebreak(min_space_for_next)
        ]

        self._log_protection(
            element_type='spacing_with_check',
            element_id='',
            page=self.current_page,
            action='spacing_added_with_pagebreak_check',
            details=f'spacing={
                spacing:.1f}, min_space={
                min_space_for_next:.1f}')

        return elements

    def _log_protection(
        self,
        element_type: str,
        element_id: str,
        page: int,
        action: str,
        details: str = ""
    ) -> None:
        """Log a page protection decision.

        Args:
            element_type: Type of element being protected
            element_id: Element identifier
            page: Page number
            action: Action taken
            details: Additional details
        """
        log_entry = {
            'element_type': element_type,
            'element_id': element_id,
            'page': page,
            'action': action,
            'details': details
        }

        self.protection_log.append(log_entry)

        if self.enable_logging:
            log_msg = f"[Page {page}] {action}: {element_type}"
            if element_id:
                log_msg += f" ({element_id})"
            if details:
                log_msg += f" - {details}"
            self.logger.info(log_msg)

    def get_protection_summary(self) -> dict:
        """Get a summary of all page protection decisions.

        Returns:
            Dictionary with protection statistics and log
        """
        return {
            'total_protections': len(self.protection_log),
            'by_type': self._count_by_type(),
            'by_page': self._count_by_page(),
            'log': self.protection_log
        }

    def _count_by_type(self) -> dict:
        """Count protection decisions by element type."""
        counts = {}
        for entry in self.protection_log:
            element_type = entry['element_type']
            counts[element_type] = counts.get(element_type, 0) + 1
        return counts

    def _count_by_page(self) -> dict:
        """Count protection decisions by page."""
        counts = {}
        for entry in self.protection_log:
            page = entry['page']
            counts[page] = counts.get(page, 0) + 1
        return counts

    def print_protection_summary(self) -> None:
        """Print a human-readable summary of page protection decisions."""
        summary = self.get_protection_summary()

        print("\n" + "=" * 60)
        print("PAGE PROTECTION SUMMARY")
        print("=" * 60)
        print(f"Total protections applied: {summary['total_protections']}")

        print("\nBy element type:")
        for element_type, count in sorted(summary['by_type'].items()):
            print(f"  {element_type}: {count}")

        print("\nBy page:")
        for page, count in sorted(summary['by_page'].items()):
            print(f"  Page {page}: {count}")

        print("=" * 60 + "\n")


def create_protected_chart_element(
    chart_image: Image,
    title_text: str,
    description_text: str,
    styles: dict,
    chart_key: str = "",
    protection_manager: PageProtectionManager | None = None
) -> Flowable:
    """Helper function to create a protected chart element.

    This is a convenience function that creates a chart with title and
    description, wrapped in KeepTogether if page protection is enabled.

    Args:
        chart_image: Chart image flowable
        title_text: Title text
        description_text: Description text
        styles: Style dictionary with 'ChartTitle' and 'ChartDescription' styles
        chart_key: Chart identifier
        protection_manager: Optional PageProtectionManager instance

    Returns:
        Protected flowable or list of flowables
    """
    # Create title paragraph
    title = Paragraph(title_text, styles.get('ChartTitle'))

    # Create description paragraph
    description = Paragraph(description_text, styles.get('ChartDescription'))

    # Apply protection if manager is provided
    if protection_manager:
        return protection_manager.wrap_chart_with_description(
            chart_image,
            title,
            description,
            chart_key
        )
    # No protection - return as list
    return [
        title,
        Spacer(1, 0.3 * cm),
        chart_image,
        Spacer(1, 0.3 * cm),
        description
    ]


def create_protected_table_element(
    table: Table,
    title_text: str,
    styles: dict,
    table_id: str = "",
    protection_manager: PageProtectionManager | None = None
) -> Flowable:
    """Helper function to create a protected table element.

    Args:
        table: Table flowable
        title_text: Title text
        styles: Style dictionary with 'TableTitle' style
        table_id: Table identifier
        protection_manager: Optional PageProtectionManager instance

    Returns:
        Protected flowable or list of flowables
    """
    # Create title paragraph
    title = Paragraph(title_text, styles.get('TableTitle'))

    # Apply protection if manager is provided
    if protection_manager:
        return protection_manager.wrap_table_with_title(
            table,
            title,
            table_id
        )
    # No protection - return as list
    return [
        title,
        Spacer(1, 0.3 * cm),
        table
    ]
