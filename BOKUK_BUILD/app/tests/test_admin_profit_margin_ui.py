"""Tests for Admin Profit Margin Management UI

Tests the profit margin management interface functionality including:
- Global margin configuration
- Category margin configuration
- Product-specific margin configuration
- Margin calculation preview and validation
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from admin_profit_margin_ui import (
        render_category_margins_tab,
        render_global_margins_tab,
        render_margin_preview_tab,
        render_product_margins_tab,
        render_profit_margin_management_ui,
    )
    from pricing.profit_margin_manager import (
        MarginBreakdown,
        MarginConfig,
        ProfitMarginManager,
    )
except ImportError as e:
    pytest.skip(
        f"Required modules not available: {e}",
        allow_module_level=True)


class TestAdminProfitMarginUI:
    """Test class for admin profit margin UI functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_margin_manager = Mock(spec=ProfitMarginManager)

        # Mock return values
        self.mock_margin_manager.get_all_margins.return_value = {
            'global_margins': {
                'default': {
                    'margin_type': 'percentage',
                    'margin_value': 25.0,
                    'applies_to': 'global',
                    'priority': 0,
                    'calculate_per_method': None
                }
            },
            'category_margins': {
                'Modul': {
                    'margin_type': 'percentage',
                    'margin_value': 30.0,
                    'applies_to': 'category',
                    'priority': 50,
                    'calculate_per_method': None
                }
            }
        }

        self.mock_margin_manager.get_available_categories.return_value = [
            'Modul', 'Wechselrichter', 'Batteriespeicher', 'Zubehör'
        ]

        self.mock_margin_manager.get_margin_breakdown.return_value = MarginBreakdown(
            purchase_price=100.0,
            margin_amount=25.0,
            selling_price=125.0,
            margin_percentage=25.0,
            source='global',
            calculate_per_method='Stück',
            quantity=1.0
        )

        self.mock_margin_manager.calculate_total_price_with_margin.return_value = {
            'unit_purchase_price': 100.0,
            'unit_selling_price': 125.0,
            'unit_margin_amount': 25.0,
            'quantity': 1.0,
            'calculate_per': 'Stück',
            'total_purchase_price': 100.0,
            'total_selling_price': 125.0,
            'total_margin_amount': 25.0,
            'margin_percentage': 25.0,
            'margin_source': 'global'}

        # Mock products data
        self.mock_products = [
            {
                'id': 1,
                'model_name': 'Test Module 400W',
                'brand': 'TestBrand',
                'category': 'Modul',
                'price_euro': 180.0,
                'calculate_per': 'Stück',
                'margin_type': 'percentage',
                'margin_value': 25.0,
                'margin_priority': 100
            },
            {
                'id': 2,
                'model_name': 'Test Inverter 5kW',
                'brand': 'TestBrand',
                'category': 'Wechselrichter',
                'price_euro': 800.0,
                'calculate_per': 'Stück',
                'margin_type': 'fixed',
                'margin_value': 200.0,
                'margin_priority': 90
            }
        ]

    @patch('admin_profit_margin_ui.st')
    @patch('admin_profit_margin_ui.ProfitMarginManager')
    def test_render_profit_margin_management_ui_success(
            self, mock_manager_class, mock_st):
        """Test successful rendering of main profit margin management UI"""

        # Setup mocks
        mock_manager_class.return_value = self.mock_margin_manager

        # Create mock tabs that support context manager protocol
        mock_tab1 = Mock()
        mock_tab1.__enter__ = Mock(return_value=mock_tab1)
        mock_tab1.__exit__ = Mock(return_value=None)
        mock_tab2 = Mock()
        mock_tab2.__enter__ = Mock(return_value=mock_tab2)
        mock_tab2.__exit__ = Mock(return_value=None)
        mock_tab3 = Mock()
        mock_tab3.__enter__ = Mock(return_value=mock_tab3)
        mock_tab3.__exit__ = Mock(return_value=None)
        mock_tab4 = Mock()
        mock_tab4.__enter__ = Mock(return_value=mock_tab4)
        mock_tab4.__exit__ = Mock(return_value=None)

        mock_st.tabs.return_value = [
            mock_tab1, mock_tab2, mock_tab3, mock_tab4]

        # Call function
        render_profit_margin_management_ui()

        # Verify UI elements were created
        mock_st.header.assert_called_with("🎯 Gewinnspannen-Verwaltung")
        mock_st.markdown.assert_called()
        mock_st.tabs.assert_called_once()

        # Verify margin manager was initialized
        mock_manager_class.assert_called_once()

    @patch('admin_profit_margin_ui.st')
    def test_render_global_margins_tab(self, mock_st):
        """Test rendering of global margins configuration tab"""

        # Setup form mock
        mock_form = Mock()
        mock_st.form.return_value.__enter__.return_value = mock_form
        mock_st.form.return_value.__exit__.return_value = None

        # Setup column mocks
        mock_st.columns.return_value = [Mock(), Mock(), Mock(), Mock()]

        # Setup expander mock
        mock_expander = Mock()
        mock_expander.__enter__ = Mock(return_value=mock_expander)
        mock_expander.__exit__ = Mock(return_value=None)
        mock_st.expander.return_value = mock_expander

        # Setup form inputs
        mock_st.selectbox.side_effect = ["default", "percentage"]
        mock_st.number_input.side_effect = [25.0, 0]
        mock_st.form_submit_button.return_value = True

        # Setup margin manager methods
        self.mock_margin_manager.set_global_margin.return_value = True

        # Call function
        render_global_margins_tab(self.mock_margin_manager)

        # Verify UI elements
        mock_st.subheader.assert_called_with("🌍 Globale Gewinnspannen")
        mock_st.form.assert_called()

        # Verify margin manager was called
        self.mock_margin_manager.get_all_margins.assert_called()

    @patch('admin_profit_margin_ui.st')
    def test_render_category_margins_tab(self, mock_st):
        """Test rendering of category margins configuration tab"""

        # Setup form mock
        mock_form = Mock()
        mock_st.form.return_value.__enter__.return_value = mock_form
        mock_st.form.return_value.__exit__.return_value = None

        # Setup column mocks
        mock_st.columns.return_value = [Mock(), Mock(), Mock(), Mock(), Mock()]

        # Setup expander mock
        mock_expander = Mock()
        mock_expander.__enter__ = Mock(return_value=mock_expander)
        mock_expander.__exit__ = Mock(return_value=None)
        mock_st.expander.return_value = mock_expander

        # Setup form inputs
        mock_st.selectbox.side_effect = ["Modul", "percentage"]
        mock_st.number_input.side_effect = [30.0, 50]
        mock_st.form_submit_button.return_value = True

        # Setup margin manager methods
        self.mock_margin_manager.set_category_margin.return_value = True

        # Call function
        render_category_margins_tab(self.mock_margin_manager)

        # Verify UI elements
        mock_st.subheader.assert_called_with("📂 Kategorie-Gewinnspannen")

        # Verify margin manager methods were called
        self.mock_margin_manager.get_available_categories.assert_called()
        self.mock_margin_manager.get_all_margins.assert_called()

    @patch('admin_profit_margin_ui.st')
    @patch('admin_profit_margin_ui.list_products')
    def test_render_product_margins_tab(self, mock_list_products, mock_st):
        """Test rendering of product-specific margins configuration tab"""

        # Setup mocks
        mock_list_products.return_value = self.mock_products

        # Setup form mock
        mock_form = Mock()
        mock_st.form.return_value.__enter__.return_value = mock_form
        mock_st.form.return_value.__exit__.return_value = None

        # Setup column mocks
        mock_st.columns.return_value = [Mock(), Mock(), Mock(), Mock()]

        # Setup expander mock
        mock_expander = Mock()
        mock_expander.__enter__ = Mock(return_value=mock_expander)
        mock_expander.__exit__ = Mock(return_value=None)
        mock_st.expander.return_value = mock_expander

        # Setup form inputs
        mock_st.selectbox.side_effect = [
            "Alle", "Test Module 400W (TestBrand)", "percentage"]
        mock_st.number_input.side_effect = [25.0, 100]
        mock_st.form_submit_button.side_effect = [
            True, False]  # Submit, don't remove

        # Setup margin manager methods
        self.mock_margin_manager.set_product_margin.return_value = True

        # Call function
        render_product_margins_tab(self.mock_margin_manager)

        # Verify UI elements
        mock_st.subheader.assert_called_with(
            "📦 Produkt-spezifische Gewinnspannen")

        # Verify products were loaded
        mock_list_products.assert_called()

    @patch('admin_profit_margin_ui.st')
    @patch('admin_profit_margin_ui.list_products')
    def test_render_margin_preview_tab(self, mock_list_products, mock_st):
        """Test rendering of margin calculation preview tab"""

        # Setup mocks
        mock_list_products.return_value = self.mock_products

        # Setup column mocks
        mock_st.columns.return_value = [Mock(), Mock(), Mock(), Mock()]

        # Setup input values
        mock_st.number_input.side_effect = [
            100.0, 1.0]  # purchase_price, quantity
        mock_st.selectbox.side_effect = [
            "Stück", "Keine Auswahl", "Keine Auswahl"]
        mock_st.button.side_effect = [True, False]  # Calculate, don't compare

        # Call function
        render_margin_preview_tab(self.mock_margin_manager)

        # Verify UI elements
        mock_st.subheader.assert_called_with("🧮 Kalkulations-Vorschau")

        # Verify margin calculations were called
        self.mock_margin_manager.get_margin_breakdown.assert_called()
        self.mock_margin_manager.calculate_total_price_with_margin.assert_called()

    @patch('admin_profit_margin_ui.st')
    def test_margin_config_validation(self, mock_st):
        """Test margin configuration validation"""

        # Test valid percentage margin
        config = MarginConfig(
            margin_type="percentage",
            margin_value=25.0,
            applies_to="global",
            priority=0
        )

        assert config.margin_type == "percentage"
        assert config.margin_value == 25.0
        assert config.applies_to == "global"

        # Test valid fixed margin
        config_fixed = MarginConfig(
            margin_type="fixed",
            margin_value=50.0,
            applies_to="product",
            priority=100
        )

        assert config_fixed.margin_type == "fixed"
        assert config_fixed.margin_value == 50.0
        assert config_fixed.applies_to == "product"

    def test_margin_breakdown_calculation(self):
        """Test margin breakdown calculation logic"""

        breakdown = MarginBreakdown(
            purchase_price=100.0,
            margin_amount=25.0,
            selling_price=125.0,
            margin_percentage=25.0,
            source='global',
            calculate_per_method='Stück',
            quantity=2.0
        )

        assert breakdown.purchase_price == 100.0
        assert breakdown.margin_amount == 25.0
        assert breakdown.selling_price == 125.0
        assert breakdown.margin_percentage == 25.0
        assert breakdown.source == 'global'
        assert breakdown.quantity == 2.0

    @patch('admin_profit_margin_ui.st')
    def test_error_handling(self, mock_st):
        """Test error handling in UI functions"""

        # Setup column mocks
        mock_st.columns.return_value = [Mock(), Mock()]

        # Setup form mock
        mock_form = Mock()
        mock_st.form.return_value.__enter__.return_value = mock_form
        mock_st.form.return_value.__exit__.return_value = None

        # Setup margin manager to raise exception
        error_manager = Mock()
        error_manager.get_all_margins.side_effect = Exception("Database error")

        # Call function that should handle the error
        render_global_margins_tab(error_manager)

        # Verify error was handled (st.error should be called)
        mock_st.error.assert_called()

    @patch('admin_profit_margin_ui.st')
    def test_fallback_mode_when_pricing_unavailable(self, mock_st):
        """Test UI works in fallback mode when pricing modules are unavailable"""

        # Create mock tabs that support context manager protocol
        mock_tab1 = Mock()
        mock_tab1.__enter__ = Mock(return_value=mock_tab1)
        mock_tab1.__exit__ = Mock(return_value=None)
        mock_tab2 = Mock()
        mock_tab2.__enter__ = Mock(return_value=mock_tab2)
        mock_tab2.__exit__ = Mock(return_value=None)
        mock_tab3 = Mock()
        mock_tab3.__enter__ = Mock(return_value=mock_tab3)
        mock_tab3.__exit__ = Mock(return_value=None)
        mock_tab4 = Mock()
        mock_tab4.__enter__ = Mock(return_value=mock_tab4)
        mock_tab4.__exit__ = Mock(return_value=None)

        mock_st.tabs.return_value = [
            mock_tab1, mock_tab2, mock_tab3, mock_tab4]

        # This test verifies the UI can still render when PRICING_AVAILABLE is False
        # The fallback classes should be used

        with patch('admin_profit_margin_ui.PRICING_AVAILABLE', False):
            render_profit_margin_management_ui()

            # Should show warning about test mode
            mock_st.warning.assert_called()

    def test_calculate_per_method_handling(self):
        """Test handling of different calculate_per methods"""

        methods = ["Stück", "Meter", "pauschal", "kWp"]

        for method in methods:
            breakdown = MarginBreakdown(
                purchase_price=100.0,
                margin_amount=25.0,
                selling_price=125.0,
                margin_percentage=25.0,
                source='global',
                calculate_per_method=method,
                quantity=1.0
            )

            assert breakdown.calculate_per_method == method
            # Verify the breakdown handles the method correctly
            assert breakdown.total_purchase_cost >= 0
            assert breakdown.total_selling_price >= 0


if __name__ == "__main__":
    pytest.main([__file__])
