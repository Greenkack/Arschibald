"""
Tests for PDF Page Protection Module

Tests the KeepTogether functionality and page protection logic
for extended PDF pages (pages 9+).

Author: Kiro AI Assistant
Date: 2025-01-10
"""

import pytest
import io
from reportlab.platypus import Paragraph, Image, Table, Spacer, KeepTogether
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from pdf_page_protection import (
    PageProtectionManager,
    ConditionalPageBreak,
    create_protected_chart_element,
    create_protected_table_element
)


class TestPageProtectionManager:
    """Tests for PageProtectionManager class."""

    def test_initialization(self):
        """Test that PageProtectionManager initializes correctly."""
        manager = PageProtectionManager(
            doc_height=29.7 * cm,
            min_space_at_bottom=3 * cm,
            enable_logging=True
        )

        assert manager.doc_height == 29.7 * cm
        assert manager.min_space_at_bottom == 3 * cm
        assert manager.enable_logging is True
        assert manager.current_page == 1
        assert len(manager.protection_log) == 0

    def test_should_apply_protection_pages_1_to_8(self):
        """Test that protection is NOT applied to pages 1-8."""
        manager = PageProtectionManager(doc_height=29.7 * cm)

        # Pages 1-8 should NOT have protection
        for page in range(1, 9):
            manager.set_current_page(page)
            assert manager.should_apply_protection() is False

    def test_should_apply_protection_pages_9_plus(self):
        """Test that protection IS applied to pages 9+."""
        manager = PageProtectionManager(doc_height=29.7 * cm)

        # Pages 9+ should have protection
        for page in range(9, 20):
            manager.set_current_page(page)
            assert manager.should_apply_protection() is True

    def test_wrap_chart_with_description_no_protection(self):
        """Test chart wrapping when protection is disabled (pages 1-8)."""
        manager = PageProtectionManager(doc_height=29.7 * cm)
        manager.set_current_page(5)  # Page 5 - no protection

        styles = getSampleStyleSheet()
        title = Paragraph("Test Chart", styles['Heading2'])
        chart = Spacer(1, 10 * cm)  # Mock chart
        description = Paragraph("Test description", styles['BodyText'])

        result = manager.wrap_chart_with_description(
            chart=chart,
            title=title,
            description=description,
            chart_key="test_chart"
        )

        # Should return a list, not KeepTogether
        assert isinstance(result, list)
        assert len(result) == 5  # title, spacer, chart, spacer, description

    def test_wrap_chart_with_description_with_protection(self):
        """Test chart wrapping when protection is enabled (pages 9+)."""
        manager = PageProtectionManager(doc_height=29.7 * cm)
        manager.set_current_page(9)  # Page 9 - protection enabled

        styles = getSampleStyleSheet()
        title = Paragraph("Test Chart", styles['Heading2'])
        chart = Spacer(1, 10 * cm)  # Mock chart
        description = Paragraph("Test description", styles['BodyText'])

        result = manager.wrap_chart_with_description(
            chart=chart,
            title=title,
            description=description,
            chart_key="test_chart"
        )

        # Should return KeepTogether
        assert isinstance(result, KeepTogether)

        # Check that protection was logged
        assert len(manager.protection_log) == 1
        assert manager.protection_log[0]['element_type'] == 'chart_with_description'
        assert manager.protection_log[0]['page'] == 9

    def test_wrap_table_with_title_no_protection(self):
        """Test table wrapping when protection is disabled."""
        manager = PageProtectionManager(doc_height=29.7 * cm)
        manager.set_current_page(3)  # Page 3 - no protection

        styles = getSampleStyleSheet()
        title = Paragraph("Test Table", styles['Heading3'])
        table = Table([['A', 'B'], ['1', '2']])

        result = manager.wrap_table_with_title(
            table=table,
            title=title,
            table_id="test_table"
        )

        # Should return a list
        assert isinstance(result, list)
        assert len(result) == 3  # title, spacer, table

    def test_wrap_table_with_title_with_protection(self):
        """Test table wrapping when protection is enabled."""
        manager = PageProtectionManager(doc_height=29.7 * cm)
        manager.set_current_page(10)  # Page 10 - protection enabled

        styles = getSampleStyleSheet()
        title = Paragraph("Test Table", styles['Heading3'])
        table = Table([['A', 'B'], ['1', '2']])

        result = manager.wrap_table_with_title(
            table=table,
            title=title,
            table_id="test_table"
        )

        # Should return KeepTogether
        assert isinstance(result, KeepTogether)

        # Check that protection was logged
        assert len(manager.protection_log) == 1
        assert manager.protection_log[0]['element_type'] == 'table_with_title'

    def test_wrap_financing_section_with_protection(self):
        """Test financing section wrapping with strict protection."""
        manager = PageProtectionManager(doc_height=29.7 * cm)
        manager.set_current_page(9)  # Page 9 - protection enabled

        styles = getSampleStyleSheet()
        title = Paragraph("Finanzierung", styles['Heading2'])
        table = Table([['Kredit', '10000€'], ['Zinsen', '5%']])
        description = Paragraph("Finanzierungsdetails", styles['BodyText'])

        result = manager.wrap_financing_section(
            title=title,
            table=table,
            description=description,
            section_id="financing_credit"
        )

        # Should return KeepTogether
        assert isinstance(result, KeepTogether)

        # Check that protection was logged with strict flag
        assert len(manager.protection_log) == 1
        log_entry = manager.protection_log[0]
        assert log_entry['element_type'] == 'financing_section'
        assert log_entry['action'] == 'wrapped_in_keeptogether_strict'
        assert 'strict_protection_for_financing' in log_entry['details']

    def test_wrap_chart_with_legend(self):
        """Test chart with legend wrapping."""
        manager = PageProtectionManager(doc_height=29.7 * cm)
        manager.set_current_page(11)  # Page 11 - protection enabled

        chart = Spacer(1, 10 * cm)  # Mock chart
        legend = Spacer(1, 2 * cm)  # Mock legend

        result = manager.wrap_chart_with_legend(
            chart=chart,
            legend=legend,
            chart_key="test_chart_with_legend"
        )

        # Should return KeepTogether
        assert isinstance(result, KeepTogether)

        # Check logging
        assert len(manager.protection_log) == 1
        assert manager.protection_log[0]['element_type'] == 'chart_with_legend'

    def test_wrap_chart_with_footnote(self):
        """Test chart with footnote wrapping."""
        manager = PageProtectionManager(doc_height=29.7 * cm)
        manager.set_current_page(12)  # Page 12 - protection enabled

        styles = getSampleStyleSheet()
        chart = Spacer(1, 10 * cm)  # Mock chart
        footnote = Paragraph("* Footnote text", styles['BodyText'])

        result = manager.wrap_chart_with_footnote(
            chart=chart,
            footnote=footnote,
            chart_key="test_chart_with_footnote"
        )

        # Should return KeepTogether
        assert isinstance(result, KeepTogether)

        # Check logging
        assert len(manager.protection_log) == 1
        assert manager.protection_log[0]['element_type'] == 'chart_with_footnote'

    def test_create_conditional_pagebreak_no_protection(self):
        """Test conditional page break when protection is disabled."""
        manager = PageProtectionManager(doc_height=29.7 * cm)
        manager.set_current_page(4)  # Page 4 - no protection

        result = manager.create_conditional_pagebreak(min_space_needed=5 * cm)

        # Should return a zero-height spacer
        assert isinstance(result, Spacer)

    def test_create_conditional_pagebreak_with_protection(self):
        """Test conditional page break when protection is enabled."""
        manager = PageProtectionManager(doc_height=29.7 * cm)
        manager.set_current_page(13)  # Page 13 - protection enabled

        result = manager.create_conditional_pagebreak(min_space_needed=5 * cm)

        # Should return ConditionalPageBreak
        assert isinstance(result, ConditionalPageBreak)
        assert result.min_space_needed == 5 * cm

        # Check logging
        assert len(manager.protection_log) == 1
        assert manager.protection_log[0]['element_type'] == 'conditional_pagebreak'

    def test_check_if_pagebreak_needed(self):
        """Test page break necessity check."""
        manager = PageProtectionManager(
            doc_height=29.7 * cm,
            min_space_at_bottom=3 * cm
        )
        manager.set_current_page(9)  # Protection enabled

        # Element fits - no break needed
        assert manager.check_if_pagebreak_needed(
            element_height=5 * cm,
            current_position=10 * cm
        ) is False

        # Element doesn't fit - break needed
        assert manager.check_if_pagebreak_needed(
            element_height=10 * cm,
            current_position=8 * cm
        ) is True

    def test_prevent_orphan_heading(self):
        """Test orphan heading prevention."""
        manager = PageProtectionManager(doc_height=29.7 * cm)
        manager.set_current_page(14)  # Protection enabled

        styles = getSampleStyleSheet()
        heading = Paragraph("Section Title", styles['Heading2'])
        content = [
            Paragraph("First paragraph", styles['BodyText']),
            Paragraph("Second paragraph", styles['BodyText'])
        ]

        result = manager.prevent_orphan_heading(heading, content)

        # Should return list with KeepTogether for heading + first content
        assert isinstance(result, list)
        assert len(result) == 2  # KeepTogether + remaining content
        assert isinstance(result[0], KeepTogether)

    def test_add_spacing_with_pagebreak_check(self):
        """Test spacing with automatic page break check."""
        manager = PageProtectionManager(doc_height=29.7 * cm)
        manager.set_current_page(15)  # Protection enabled

        result = manager.add_spacing_with_pagebreak_check(
            spacing=1.0 * cm,
            min_space_for_next=5.0 * cm
        )

        # Should return list with spacer and conditional page break
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], Spacer)
        assert isinstance(result[1], ConditionalPageBreak)

    def test_protection_summary(self):
        """Test protection summary generation."""
        manager = PageProtectionManager(doc_height=29.7 * cm)
        manager.set_current_page(9)

        styles = getSampleStyleSheet()

        # Add several protected elements
        manager.wrap_chart_with_description(
            chart=Spacer(1, 10 * cm),
            title=Paragraph("Chart 1", styles['Heading2']),
            description=Paragraph("Desc 1", styles['BodyText']),
            chart_key="chart1"
        )

        manager.set_current_page(10)
        manager.wrap_table_with_title(
            table=Table([['A', 'B']]),
            title=Paragraph("Table 1", styles['Heading3']),
            table_id="table1"
        )

        summary = manager.get_protection_summary()

        assert summary['total_protections'] == 2
        assert 'chart_with_description' in summary['by_type']
        assert 'table_with_title' in summary['by_type']
        assert 9 in summary['by_page']
        assert 10 in summary['by_page']


class TestConditionalPageBreak:
    """Tests for ConditionalPageBreak class."""

    def test_initialization(self):
        """Test ConditionalPageBreak initialization."""
        cpb = ConditionalPageBreak(min_space_needed=5 * cm)
        assert cpb.min_space_needed == 5 * cm
        assert cpb.width == 0
        assert cpb.height == 0

    def test_wrap_with_sufficient_space(self):
        """Test wrap when there's sufficient space."""
        cpb = ConditionalPageBreak(min_space_needed=3 * cm)
        width, height = cpb.wrap(availWidth=15 * cm, availHeight=10 * cm)

        # Should return (0, 0) - no break needed
        assert width == 0
        assert height == 0

    def test_wrap_with_insufficient_space(self):
        """Test wrap when there's insufficient space."""
        cpb = ConditionalPageBreak(min_space_needed=5 * cm)
        width, height = cpb.wrap(availWidth=15 * cm, availHeight=2 * cm)

        # Should request more than available - triggers break
        assert height > 2 * cm


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_create_protected_chart_element_with_manager(self):
        """Test creating protected chart element with manager."""
        styles = getSampleStyleSheet()
        chart_styles = {
            'ChartTitle': styles['Heading2'],
            'ChartDescription': styles['BodyText']
        }

        manager = PageProtectionManager(doc_height=29.7 * cm)
        manager.set_current_page(9)  # Protection enabled

        # Create mock chart image
        chart_image = Spacer(1, 10 * cm)

        result = create_protected_chart_element(
            chart_image=chart_image,
            title_text="Test Chart",
            description_text="Test description",
            styles=chart_styles,
            chart_key="test_chart",
            protection_manager=manager
        )

        # Should return KeepTogether
        assert isinstance(result, KeepTogether)

    def test_create_protected_chart_element_without_manager(self):
        """Test creating chart element without protection manager."""
        styles = getSampleStyleSheet()
        chart_styles = {
            'ChartTitle': styles['Heading2'],
            'ChartDescription': styles['BodyText']
        }

        chart_image = Spacer(1, 10 * cm)

        result = create_protected_chart_element(
            chart_image=chart_image,
            title_text="Test Chart",
            description_text="Test description",
            styles=chart_styles,
            chart_key="test_chart",
            protection_manager=None
        )

        # Should return list
        assert isinstance(result, list)
        assert len(result) == 5  # title, spacer, chart, spacer, description

    def test_create_protected_table_element_with_manager(self):
        """Test creating protected table element with manager."""
        styles = getSampleStyleSheet()
        table_styles = {
            'TableTitle': styles['Heading3']
        }

        manager = PageProtectionManager(doc_height=29.7 * cm)
        manager.set_current_page(10)  # Protection enabled

        table = Table([['A', 'B'], ['1', '2']])

        result = create_protected_table_element(
            table=table,
            title_text="Test Table",
            styles=table_styles,
            table_id="test_table",
            protection_manager=manager
        )

        # Should return KeepTogether
        assert isinstance(result, KeepTogether)

    def test_create_protected_table_element_without_manager(self):
        """Test creating table element without protection manager."""
        styles = getSampleStyleSheet()
        table_styles = {
            'TableTitle': styles['Heading3']
        }

        table = Table([['A', 'B'], ['1', '2']])

        result = create_protected_table_element(
            table=table,
            title_text="Test Table",
            styles=table_styles,
            table_id="test_table",
            protection_manager=None
        )

        # Should return list
        assert isinstance(result, list)
        assert len(result) == 3  # title, spacer, table


class TestIntegration:
    """Integration tests for page protection."""

    def test_multiple_charts_with_protection(self):
        """Test protecting multiple charts in sequence."""
        manager = PageProtectionManager(doc_height=29.7 * cm)
        manager.set_current_page(9)

        styles = getSampleStyleSheet()

        # Create multiple protected charts
        for i in range(5):
            manager.wrap_chart_with_description(
                chart=Spacer(
                    1,
                    10 * cm),
                title=Paragraph(
                    f"Chart {
                        i + 1}",
                    styles['Heading2']),
                description=Paragraph(
                    f"Description {
                        i + 1}",
                    styles['BodyText']),
                chart_key=f"chart_{
                    i + 1}")
            manager.set_current_page(manager.current_page + 1)

        summary = manager.get_protection_summary()
        assert summary['total_protections'] == 5
        assert summary['by_type']['chart_with_description'] == 5

    def test_mixed_elements_with_protection(self):
        """Test protecting mixed element types."""
        manager = PageProtectionManager(doc_height=29.7 * cm)
        manager.set_current_page(9)

        styles = getSampleStyleSheet()

        # Chart
        manager.wrap_chart_with_description(
            chart=Spacer(1, 10 * cm),
            title=Paragraph("Chart", styles['Heading2']),
            description=Paragraph("Chart desc", styles['BodyText']),
            chart_key="chart1"
        )

        # Table
        manager.wrap_table_with_title(
            table=Table([['A', 'B']]),
            title=Paragraph("Table", styles['Heading3']),
            table_id="table1"
        )

        # Financing section
        manager.wrap_financing_section(
            title=Paragraph("Financing", styles['Heading2']),
            table=Table([['Credit', '10000€']]),
            description=Paragraph("Financing desc", styles['BodyText']),
            section_id="financing1"
        )

        summary = manager.get_protection_summary()
        assert summary['total_protections'] == 3
        assert 'chart_with_description' in summary['by_type']
        assert 'table_with_title' in summary['by_type']
        assert 'financing_section' in summary['by_type']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
