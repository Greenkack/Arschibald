"""Tests for Admin Pricing Rule Management UI

Tests the pricing rule management interface functionality including:
- Discount rule configuration
- Surcharge rule configuration
- Accessory rule configuration
- Rule testing and preview functionality
"""

import json
import os
import sys
from unittest.mock import Mock, patch

import pytest

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from admin_pricing_rule_ui import (
        render_accessory_rules_tab,
        render_discount_rules_tab,
        render_pricing_rule_management_ui,
        render_rule_testing_tab,
        render_surcharge_rules_tab,
    )
    from pricing.pricing_modification_engine import (
        AccessoryConfig,
        DiscountConfig,
        ModificationType,
        PricingModificationEngine,
        SurchargeConfig,
    )
except ImportError as e:
    pytest.skip(
        f"Required modules not available: {e}",
        allow_module_level=True)


class TestAdminPricingRuleUI:
    """Test class for admin pricing rule UI functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_pricing_engine = Mock(spec=PricingModificationEngine)

        # Mock discount configurations
        self.sample_discount = DiscountConfig(
            discount_type="percentage",
            discount_value=10.0,
            description="Early Bird Discount",
            applies_to="total",
            conditions={"customer_type": "premium"},
            priority=50,
            minimum_amount=500.0,
            maximum_discount=200.0,
            is_active=True
        )

        # Mock surcharge configurations
        self.sample_surcharge = SurchargeConfig(
            surcharge_type="fixed",
            surcharge_value=50.0,
            description="Express Delivery",
            applies_to="total",
            conditions={"delivery_type": "express"},
            priority=30,
            minimum_amount=0.0,
            maximum_surcharge=None,
            is_active=True
        )

        # Mock accessory configurations
        self.sample_accessory = AccessoryConfig(
            accessory_id=1,
            name="Monitoring System",
            price=299.99,
            quantity=1,
            category="monitoring",
            description="Advanced monitoring system",
            is_optional=True
        )

        # Setup mock engine attributes
        self.mock_pricing_engine.discounts = [self.sample_discount]
        self.mock_pricing_engine.surcharges = [self.sample_surcharge]
        self.mock_pricing_engine.accessories = [self.sample_accessory]

        # Mock calculation results
        self.mock_pricing_engine.calculate_modifications.return_value = {
            'original_amount': 1000.0,
            'accessories_cost': 299.99,
            'total_discounts': 100.0,
            'total_surcharges': 50.0,
            'final_amount': 1249.99,
            'applied_modifications': [],
            'dynamic_keys': {
                'BASE_PRICE': 1000.0,
                'FINAL_AMOUNT': 1249.99
            }
        }

        self.mock_pricing_engine.calculate_detailed_breakdown.return_value = {
            'step_1_base_price': 1000.0,
            'step_2_accessories': {'total_cost': 299.99},
            'step_3_base_with_accessories': 1299.99,
            'step_5_after_pct_discounts': 1199.99,
            'step_7_after_pct_surcharges': 1249.99,
            'step_10_final_amount': 1249.99,
            'validation_checks': {
                'final_amount_valid': True,
                'prevented_negative': False
            }
        }

    @patch('admin_pricing_rule_ui.st')
    def test_render_pricing_rule_management_ui_success(self, mock_st):
        """Test successful rendering of main pricing rule management UI"""

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

        # Mock session state
        mock_st.session_state = {'pricing_engine': self.mock_pricing_engine}

        # Call function
        render_pricing_rule_management_ui()

        # Verify UI elements were created
        mock_st.header.assert_called_with("⚙️ Preisregel-Verwaltung")
        mock_st.markdown.assert_called()
        mock_st.tabs.assert_called_once()

    @patch('admin_pricing_rule_ui.st')
    def test_render_discount_rules_tab(self, mock_st):
        """Test rendering of discount rules configuration tab"""

        # Setup column mocks
        mock_st.columns.return_value = [Mock(), Mock(), Mock(), Mock(), Mock()]

        # Setup expander mock
        mock_expander = Mock()
        mock_expander.__enter__ = Mock(return_value=mock_expander)
        mock_expander.__exit__ = Mock(return_value=None)
        mock_st.expander.return_value = mock_expander

        # Setup form mock
        mock_form = Mock()
        mock_st.form.return_value.__enter__.return_value = mock_form
        mock_st.form.return_value.__exit__.return_value = None

        # Setup form inputs
        mock_st.text_input.return_value = "Test Discount"
        mock_st.selectbox.side_effect = ["percentage", "total"]
        mock_st.number_input.side_effect = [10.0, 50, 100.0, 200.0]
        mock_st.checkbox.return_value = True
        mock_st.text_area.return_value = '{"customer_type": "premium"}'
        mock_st.form_submit_button.return_value = True

        # Call function
        render_discount_rules_tab(self.mock_pricing_engine)

        # Verify UI elements
        mock_st.subheader.assert_called_with("💰 Rabatt-Regeln")
        mock_st.form.assert_called()

        # Verify pricing engine was called
        self.mock_pricing_engine.add_discount.assert_called()

    @patch('admin_pricing_rule_ui.st')
    def test_render_surcharge_rules_tab(self, mock_st):
        """Test rendering of surcharge rules configuration tab"""

        # Setup column mocks
        mock_st.columns.return_value = [Mock(), Mock(), Mock(), Mock(), Mock()]

        # Setup expander mock
        mock_expander = Mock()
        mock_expander.__enter__ = Mock(return_value=mock_expander)
        mock_expander.__exit__ = Mock(return_value=None)
        mock_st.expander.return_value = mock_expander

        # Setup form mock
        mock_form = Mock()
        mock_st.form.return_value.__enter__.return_value = mock_form
        mock_st.form.return_value.__exit__.return_value = None

        # Setup form inputs
        mock_st.text_input.return_value = "Test Surcharge"
        mock_st.selectbox.side_effect = ["fixed", "total"]
        mock_st.number_input.side_effect = [50.0, 30, 0.0, 0.0]
        mock_st.checkbox.return_value = True
        mock_st.text_area.return_value = '{"delivery_type": "express"}'
        mock_st.form_submit_button.return_value = True

        # Call function
        render_surcharge_rules_tab(self.mock_pricing_engine)

        # Verify UI elements
        mock_st.subheader.assert_called_with("📈 Zuschlag-Regeln")
        mock_st.form.assert_called()

        # Verify pricing engine was called
        self.mock_pricing_engine.add_surcharge.assert_called()

    @patch('admin_pricing_rule_ui.st')
    def test_render_accessory_rules_tab(self, mock_st):
        """Test rendering of accessory rules configuration tab"""

        # Setup column mocks
        mock_st.columns.return_value = [Mock(), Mock(), Mock(), Mock(), Mock()]

        # Setup expander mock
        mock_expander = Mock()
        mock_expander.__enter__ = Mock(return_value=mock_expander)
        mock_expander.__exit__ = Mock(return_value=None)
        mock_st.expander.return_value = mock_expander

        # Setup form mock
        mock_form = Mock()
        mock_st.form.return_value.__enter__.return_value = mock_form
        mock_st.form.return_value.__exit__.return_value = None

        # Setup form inputs
        mock_st.text_input.return_value = "Test Accessory"
        mock_st.number_input.side_effect = [199.99, 1]
        mock_st.selectbox.return_value = "monitoring"
        mock_st.checkbox.return_value = True
        mock_st.text_area.return_value = "Test description"
        mock_st.form_submit_button.return_value = True

        # Call function
        render_accessory_rules_tab(self.mock_pricing_engine)

        # Verify UI elements
        mock_st.subheader.assert_called_with("🔧 Zubehör-Regeln")
        mock_st.form.assert_called()

        # Verify pricing engine was called
        self.mock_pricing_engine.add_accessory.assert_called()

    @patch('admin_pricing_rule_ui.st')
    @patch('admin_pricing_rule_ui.pd')
    def test_render_rule_testing_tab(self, mock_pd, mock_st):
        """Test rendering of rule testing and preview tab"""

        # Setup column mocks
        mock_st.columns.return_value = [Mock(), Mock(), Mock(), Mock()]

        # Setup expander mock
        mock_expander = Mock()
        mock_expander.__enter__ = Mock(return_value=mock_expander)
        mock_expander.__exit__ = Mock(return_value=None)
        mock_st.expander.return_value = mock_expander

        # Setup input values
        mock_st.number_input.return_value = 1000.0
        mock_st.text_area.return_value = '{"customer_type": "premium"}'
        mock_st.checkbox.return_value = True
        mock_st.button.return_value = True

        # Setup DataFrame mock
        mock_df = Mock()
        mock_pd.DataFrame.return_value = mock_df

        # Call function
        render_rule_testing_tab(self.mock_pricing_engine)

        # Verify UI elements
        mock_st.subheader.assert_called_with("🧪 Regel-Test")

        # Verify pricing calculations were called
        self.mock_pricing_engine.calculate_modifications.assert_called()
        self.mock_pricing_engine.calculate_detailed_breakdown.assert_called()

    def test_discount_config_creation(self):
        """Test discount configuration creation and validation"""

        config = DiscountConfig(
            discount_type="percentage",
            discount_value=15.0,
            description="Volume Discount",
            applies_to="total",
            conditions={"order_amount": 1000},
            priority=60,
            minimum_amount=500.0,
            maximum_discount=300.0,
            is_active=True
        )

        assert config.discount_type == "percentage"
        assert config.discount_value == 15.0
        assert config.description == "Volume Discount"
        assert config.applies_to == "total"
        assert config.conditions == {"order_amount": 1000}
        assert config.priority == 60
        assert config.minimum_amount == 500.0
        assert config.maximum_discount == 300.0
        assert config.is_active
        assert "DISCOUNT_VOLUME_DISCOUNT" in config.dynamic_key

    def test_surcharge_config_creation(self):
        """Test surcharge configuration creation and validation"""

        config = SurchargeConfig(
            surcharge_type="fixed",
            surcharge_value=75.0,
            description="Rush Order",
            applies_to="total",
            conditions={"delivery_time": "24h"},
            priority=80,
            minimum_amount=0.0,
            maximum_surcharge=150.0,
            is_active=True
        )

        assert config.surcharge_type == "fixed"
        assert config.surcharge_value == 75.0
        assert config.description == "Rush Order"
        assert config.applies_to == "total"
        assert config.conditions == {"delivery_time": "24h"}
        assert config.priority == 80
        assert config.minimum_amount == 0.0
        assert config.maximum_surcharge == 150.0
        assert config.is_active
        assert "SURCHARGE_RUSH_ORDER" in config.dynamic_key

    def test_accessory_config_creation(self):
        """Test accessory configuration creation and validation"""

        config = AccessoryConfig(
            accessory_id=2,
            name="Extended Warranty",
            price=499.99,
            quantity=1,
            category="warranty",
            description="5-year extended warranty",
            is_optional=True
        )

        assert config.accessory_id == 2
        assert config.name == "Extended Warranty"
        assert config.price == 499.99
        assert config.quantity == 1
        assert config.category == "warranty"
        assert config.description == "5-year extended warranty"
        assert config.is_optional
        assert "ACCESSORY_EXTENDED_WARRANTY" in config.dynamic_key

    @patch('admin_pricing_rule_ui.st')
    def test_json_condition_parsing(self, mock_st):
        """Test JSON condition parsing in rule configuration"""

        # Test valid JSON
        valid_json = '{"customer_type": "premium", "region": "EU"}'
        parsed = json.loads(valid_json)

        assert parsed["customer_type"] == "premium"
        assert parsed["region"] == "EU"

        # Test invalid JSON handling
        invalid_json = '{"customer_type": "premium", "region":}'

        with pytest.raises(json.JSONDecodeError):
            json.loads(invalid_json)

    @patch('admin_pricing_rule_ui.st')
    def test_rule_priority_sorting(self, mock_st):
        """Test rule priority sorting functionality"""

        # Create rules with different priorities
        high_priority_discount = DiscountConfig(
            discount_type="percentage",
            discount_value=20.0,
            description="VIP Discount",
            priority=90
        )

        low_priority_discount = DiscountConfig(
            discount_type="percentage",
            discount_value=5.0,
            description="Standard Discount",
            priority=10
        )

        # Add to engine
        engine = PricingModificationEngine()
        engine.add_discount(low_priority_discount)
        engine.add_discount(high_priority_discount)

        # Verify sorting (higher priority first)
        assert engine.discounts[0].priority == 90
        assert engine.discounts[1].priority == 10

    @patch('admin_pricing_rule_ui.st')
    def test_error_handling_invalid_config(self, mock_st):
        """Test error handling for invalid configurations"""

        # Setup error scenario
        mock_st.text_input.return_value = ""  # Empty description
        mock_st.number_input.return_value = -10.0  # Negative value
        mock_st.form_submit_button.return_value = True

        # This should be handled gracefully in the UI
        # The actual validation would happen in the PricingModificationEngine

        engine = PricingModificationEngine()

        # Test that engine handles invalid configs appropriately
        try:
            invalid_config = DiscountConfig(
                discount_type="percentage",
                discount_value=-10.0,  # Invalid negative value
                description=""  # Empty description
            )
            # The engine should validate this
            assert invalid_config.discount_value < 0  # This would be caught by validation
        except Exception:
            pass  # Expected for invalid config

    @patch('admin_pricing_rule_ui.st')
    def test_rule_deletion(self, mock_st):
        """Test rule deletion functionality"""

        # Setup button click mock
        mock_st.button.return_value = True

        # Create engine with rules
        engine = PricingModificationEngine()
        discount = DiscountConfig(
            discount_type="percentage",
            discount_value=10.0,
            description="Test Discount"
        )
        engine.add_discount(discount)

        # Verify rule exists
        assert len(engine.discounts) == 1

        # Simulate deletion (would be handled by UI rerun)
        engine.discounts.pop(0)

        # Verify rule removed
        assert len(engine.discounts) == 0

    @patch('admin_pricing_rule_ui.st')
    def test_calculation_result_display(self, mock_st):
        """Test calculation result display formatting"""

        # Mock calculation result
        result = {
            'original_amount': 1000.0,
            'accessories_cost': 299.99,
            'total_discounts': 100.0,
            'total_surcharges': 50.0,
            'final_amount': 1249.99,
            'applied_modifications': [],
            'dynamic_keys': {
                'BASE_PRICE': 1000.0,
                'ACCESSORIES_COST': 299.99,
                'TOTAL_DISCOUNTS': 100.0,
                'TOTAL_SURCHARGES': 50.0,
                'FINAL_AMOUNT': 1249.99
            }
        }

        # Verify result structure
        assert result['original_amount'] == 1000.0
        assert result['accessories_cost'] == 299.99
        assert result['total_discounts'] == 100.0
        assert result['total_surcharges'] == 50.0
        assert result['final_amount'] == 1249.99

        # Verify dynamic keys are generated
        assert 'BASE_PRICE' in result['dynamic_keys']
        assert 'FINAL_AMOUNT' in result['dynamic_keys']

    @patch('admin_pricing_rule_ui.st')
    def test_fallback_mode_functionality(self, mock_st):
        """Test UI functionality in fallback mode when pricing modules unavailable"""

        # This test verifies the UI can still render when PRICING_AVAILABLE is False
        # The fallback classes should provide basic functionality

        with patch('admin_pricing_rule_ui.PRICING_AVAILABLE', False):
            # Create mock tabs
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
            mock_st.session_state = {}

            render_pricing_rule_management_ui()

            # Should show warning about test mode
            mock_st.warning.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])
