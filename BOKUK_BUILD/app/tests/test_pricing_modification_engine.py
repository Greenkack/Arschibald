"""Tests for Pricing Modification Engine

Tests discount and surcharge calculations, accessory handling,
and the complete pricing formula implementation.
"""


import pytest

from pricing.pricing_modification_engine import (
    AccessoryConfig,
    DiscountConfig,
    PricingModificationEngine,
    SurchargeConfig,
)


class TestDiscountConfig:
    """Test DiscountConfig class"""

    def test_discount_config_creation(self):
        """Test basic discount config creation"""
        config = DiscountConfig(
            discount_type="percentage",
            discount_value=10.0,
            description="Early Payment Discount"
        )

        assert config.discount_type == "percentage"
        assert config.discount_value == 10.0
        assert config.description == "Early Payment Discount"
        assert config.dynamic_key == "DISCOUNT_EARLY_PAYMENT_DISCOUNT"
        assert config.is_active is True
        assert config.priority == 0

    def test_discount_config_custom_key(self):
        """Test discount config with custom dynamic key"""
        config = DiscountConfig(
            discount_type="fixed",
            discount_value=100.0,
            description="Volume Discount",
            dynamic_key="CUSTOM_VOLUME_DISCOUNT"
        )

        assert config.dynamic_key == "CUSTOM_VOLUME_DISCOUNT"

    def test_discount_config_with_conditions(self):
        """Test discount config with conditions"""
        config = DiscountConfig(
            discount_type="percentage",
            discount_value=5.0,
            description="Loyalty Discount",
            conditions={"customer_type": "premium", "order_count": 5},
            minimum_amount=1000.0,
            maximum_discount=200.0
        )

        assert config.conditions["customer_type"] == "premium"
        assert config.minimum_amount == 1000.0
        assert config.maximum_discount == 200.0


class TestSurchargeConfig:
    """Test SurchargeConfig class"""

    def test_surcharge_config_creation(self):
        """Test basic surcharge config creation"""
        config = SurchargeConfig(
            surcharge_type="percentage",
            surcharge_value=5.0,
            description="Rush Order Surcharge"
        )

        assert config.surcharge_type == "percentage"
        assert config.surcharge_value == 5.0
        assert config.description == "Rush Order Surcharge"
        assert config.dynamic_key == "SURCHARGE_RUSH_ORDER_SURCHARGE"
        assert config.is_active is True

    def test_surcharge_config_fixed(self):
        """Test fixed surcharge config"""
        config = SurchargeConfig(
            surcharge_type="fixed",
            surcharge_value=150.0,
            description="Installation Surcharge",
            maximum_surcharge=300.0
        )

        assert config.surcharge_type == "fixed"
        assert config.surcharge_value == 150.0
        assert config.maximum_surcharge == 300.0


class TestAccessoryConfig:
    """Test AccessoryConfig class"""

    def test_accessory_config_creation(self):
        """Test basic accessory config creation"""
        config = AccessoryConfig(
            accessory_id=1,
            name="Monitoring System",
            price=299.99,
            quantity=1,
            category="monitoring"
        )

        assert config.accessory_id == 1
        assert config.name == "Monitoring System"
        assert config.price == 299.99
        assert config.quantity == 1
        assert config.dynamic_key == "ACCESSORY_MONITORING_SYSTEM"
        assert config.is_optional is True

    def test_accessory_config_multiple_quantity(self):
        """Test accessory config with multiple quantities"""
        config = AccessoryConfig(
            accessory_id=2,
            name="Cable Extension",
            price=25.0,
            quantity=5,
            vat_rate=19.0
        )

        assert config.quantity == 5
        assert config.vat_rate == 19.0


class TestPricingModificationEngine:
    """Test PricingModificationEngine class"""

    @pytest.fixture
    def engine(self):
        """Create a pricing modification engine for testing"""
        return PricingModificationEngine()

    @pytest.fixture
    def sample_discount(self):
        """Create a sample discount configuration"""
        return DiscountConfig(
            discount_type="percentage",
            discount_value=10.0,
            description="Early Payment Discount"
        )

    @pytest.fixture
    def sample_surcharge(self):
        """Create a sample surcharge configuration"""
        return SurchargeConfig(
            surcharge_type="percentage",
            surcharge_value=5.0,
            description="Rush Order Surcharge"
        )

    @pytest.fixture
    def sample_accessory(self):
        """Create a sample accessory configuration"""
        return AccessoryConfig(
            accessory_id=1,
            name="Monitoring System",
            price=300.0,
            quantity=1
        )

    def test_engine_initialization(self, engine):
        """Test engine initialization"""
        assert isinstance(engine, PricingModificationEngine)
        assert len(engine.discounts) == 0
        assert len(engine.surcharges) == 0
        assert len(engine.accessories) == 0

    def test_add_discount(self, engine, sample_discount):
        """Test adding a discount configuration"""
        engine.add_discount(sample_discount)

        assert len(engine.discounts) == 1
        assert engine.discounts[0] == sample_discount

    def test_add_surcharge(self, engine, sample_surcharge):
        """Test adding a surcharge configuration"""
        engine.add_surcharge(sample_surcharge)

        assert len(engine.surcharges) == 1
        assert engine.surcharges[0] == sample_surcharge

    def test_add_accessory(self, engine, sample_accessory):
        """Test adding an accessory configuration"""
        engine.add_accessory(sample_accessory)

        assert len(engine.accessories) == 1
        assert engine.accessories[0] == sample_accessory

    def test_basic_calculation_no_modifications(self, engine):
        """Test basic calculation with no modifications"""
        base_price = 1000.0
        result = engine.calculate_modifications(base_price)

        assert result.original_amount == 1000.0
        assert result.accessories_cost == 0.0
        assert result.total_discounts == 0.0
        assert result.total_surcharges == 0.0
        assert result.final_amount == 1000.0
        assert len(result.applied_modifications) == 0

    def test_calculation_with_accessories(self, engine, sample_accessory):
        """Test calculation with accessories"""
        engine.add_accessory(sample_accessory)
        base_price = 1000.0
        selected_accessories = [1]

        result = engine.calculate_modifications(
            base_price, selected_accessories
        )

        assert result.original_amount == 1000.0
        assert result.accessories_cost == 300.0
        assert result.final_amount == 1300.0
        assert len(result.applied_modifications) == 1

    def test_calculation_with_percentage_discount(
            self, engine, sample_discount):
        """Test calculation with percentage discount"""
        engine.add_discount(sample_discount)
        base_price = 1000.0

        result = engine.calculate_modifications(base_price)

        # 10% discount on 1000 = 100
        assert result.original_amount == 1000.0
        assert result.total_discounts == 100.0
        assert result.final_amount == 900.0
        assert len(result.applied_modifications) == 1

    def test_calculation_with_percentage_surcharge(
            self, engine, sample_surcharge):
        """Test calculation with percentage surcharge"""
        engine.add_surcharge(sample_surcharge)
        base_price = 1000.0

        result = engine.calculate_modifications(base_price)

        # 5% surcharge on 1000 = 50
        assert result.original_amount == 1000.0
        assert result.total_surcharges == 50.0
        assert result.final_amount == 1050.0
        assert len(result.applied_modifications) == 1

    def test_calculation_with_fixed_discount(self, engine):
        """Test calculation with fixed discount"""
        fixed_discount = DiscountConfig(
            discount_type="fixed",
            discount_value=150.0,
            description="Fixed Discount"
        )
        engine.add_discount(fixed_discount)
        base_price = 1000.0

        result = engine.calculate_modifications(base_price)

        assert result.original_amount == 1000.0
        assert result.total_discounts == 150.0
        assert result.final_amount == 850.0

    def test_calculation_with_fixed_surcharge(self, engine):
        """Test calculation with fixed surcharge"""
        fixed_surcharge = SurchargeConfig(
            surcharge_type="fixed",
            surcharge_value=200.0,
            description="Fixed Surcharge"
        )
        engine.add_surcharge(fixed_surcharge)
        base_price = 1000.0

        result = engine.calculate_modifications(base_price)

        assert result.original_amount == 1000.0
        assert result.total_surcharges == 200.0
        assert result.final_amount == 1200.0

    def test_complete_pricing_formula(self, engine):
        """Test the complete pricing formula implementation"""
        # Add accessories
        accessory = AccessoryConfig(
            accessory_id=1,
            name="Monitoring",
            price=200.0,
            quantity=1
        )
        engine.add_accessory(accessory)

        # Add percentage discount
        pct_discount = DiscountConfig(
            discount_type="percentage",
            discount_value=10.0,
            description="Percentage Discount"
        )
        engine.add_discount(pct_discount)

        # Add percentage surcharge
        pct_surcharge = SurchargeConfig(
            surcharge_type="percentage",
            surcharge_value=5.0,
            description="Percentage Surcharge"
        )
        engine.add_surcharge(pct_surcharge)

        # Add fixed discount
        fixed_discount = DiscountConfig(
            discount_type="fixed",
            discount_value=50.0,
            description="Fixed Discount"
        )
        engine.add_discount(fixed_discount)

        # Add fixed surcharge
        fixed_surcharge = SurchargeConfig(
            surcharge_type="fixed",
            surcharge_value=30.0,
            description="Fixed Surcharge"
        )
        engine.add_surcharge(fixed_surcharge)

        base_price = 1000.0
        selected_accessories = [1]

        result = engine.calculate_modifications(
            base_price, selected_accessories
        )

        # Formula: (Matrix Price + Accessories) × (1 - Discount%) ×
        #          (1 + Surcharge%) - Fixed Discounts + Fixed Surcharges
        # Step 1: 1000 + 200 = 1200 (with accessories)
        # Step 2: 1200 × (1 - 0.10) = 1200 × 0.90 = 1080 (after % discount)
        # Step 3: 1080 × (1 + 0.05) = 1080 × 1.05 = 1134 (after % surcharge)
        # Step 4: 1134 - 50 + 30 = 1114 (after fixed modifications)

        assert result.original_amount == 1000.0
        assert result.accessories_cost == 200.0
        # 120 (10% of 1200) + 50 (fixed)
        assert result.total_discounts == 170.0
        assert result.total_surcharges == 84.0   # 54 (5% of 1080) + 30 (fixed)
        assert result.final_amount == 1114.0
        # 4 modifications + 1 accessory
        assert len(result.applied_modifications) == 5

    def test_discount_with_minimum_amount(self, engine):
        """Test discount with minimum amount condition"""
        discount = DiscountConfig(
            discount_type="percentage",
            discount_value=10.0,
            description="High Value Discount",
            minimum_amount=2000.0
        )
        engine.add_discount(discount)

        # Test with amount below minimum
        result_low = engine.calculate_modifications(1000.0)
        assert result_low.total_discounts == 0.0

        # Test with amount above minimum
        result_high = engine.calculate_modifications(2500.0)
        assert result_high.total_discounts == 250.0  # 10% of 2500

    def test_discount_with_maximum_cap(self, engine):
        """Test discount with maximum cap"""
        discount = DiscountConfig(
            discount_type="percentage",
            discount_value=20.0,
            description="Capped Discount",
            maximum_discount=150.0
        )
        engine.add_discount(discount)

        # Test with amount that would exceed cap
        result = engine.calculate_modifications(1000.0)
        # 20% of 1000 = 200, but capped at 150
        assert result.total_discounts == 150.0

    def test_discount_with_conditions(self, engine):
        """Test discount with custom conditions"""
        discount = DiscountConfig(
            discount_type="percentage",
            discount_value=15.0,
            description="Premium Customer Discount",
            conditions={"customer_type": "premium"}
        )
        engine.add_discount(discount)

        # Test without matching conditions
        result_no_match = engine.calculate_modifications(
            1000.0, context={"customer_type": "standard"}
        )
        assert result_no_match.total_discounts == 0.0

        # Test with matching conditions
        result_match = engine.calculate_modifications(
            1000.0, context={"customer_type": "premium"}
        )
        assert result_match.total_discounts == 150.0  # 15% of 1000

    def test_priority_ordering(self, engine):
        """Test that modifications are applied in priority order"""
        # Add discounts with different priorities
        high_priority = DiscountConfig(
            discount_type="percentage",
            discount_value=5.0,
            description="High Priority",
            priority=10
        )
        low_priority = DiscountConfig(
            discount_type="percentage",
            discount_value=10.0,
            description="Low Priority",
            priority=1
        )

        # Add in reverse order to test sorting
        engine.add_discount(low_priority)
        engine.add_discount(high_priority)

        # Check that they are sorted by priority
        assert engine.discounts[0].priority == 10
        assert engine.discounts[1].priority == 1

    def test_negative_final_amount_prevention(self, engine):
        """Test that final amount cannot go negative"""
        # Add a very large discount
        large_discount = DiscountConfig(
            discount_type="fixed",
            discount_value=2000.0,
            description="Huge Discount"
        )
        engine.add_discount(large_discount)

        base_price = 1000.0
        result = engine.calculate_modifications(base_price)

        # Final amount should be 0, not negative
        assert result.final_amount == 0.0

    def test_dynamic_keys_generation(
            self,
            engine,
            sample_discount,
            sample_accessory):
        """Test that dynamic keys are properly generated"""
        engine.add_discount(sample_discount)
        engine.add_accessory(sample_accessory)

        base_price = 1000.0
        selected_accessories = [1]

        result = engine.calculate_modifications(
            base_price, selected_accessories
        )

        # Check that dynamic keys are present
        assert "PRICING_BASE_PRICE" in result.dynamic_keys
        assert "PRICING_FINAL_AMOUNT" in result.dynamic_keys
        assert "DISCOUNT_EARLY_PAYMENT_DISCOUNT" in result.dynamic_keys
        assert "ACCESSORY_MONITORING_SYSTEM" in result.dynamic_keys

    def test_clear_methods(
            self,
            engine,
            sample_discount,
            sample_surcharge,
            sample_accessory):
        """Test clearing configurations"""
        engine.add_discount(sample_discount)
        engine.add_surcharge(sample_surcharge)
        engine.add_accessory(sample_accessory)

        assert len(engine.discounts) == 1
        assert len(engine.surcharges) == 1
        assert len(engine.accessories) == 1

        engine.clear_discounts()
        assert len(engine.discounts) == 0

        engine.clear_surcharges()
        assert len(engine.surcharges) == 0

        engine.clear_accessories()
        assert len(engine.accessories) == 0

    def test_get_active_configurations(self, engine):
        """Test getting active configurations"""
        # Add active discount
        active_discount = DiscountConfig(
            discount_type="percentage",
            discount_value=10.0,
            description="Active Discount",
            is_active=True
        )
        # Add inactive discount
        inactive_discount = DiscountConfig(
            discount_type="percentage",
            discount_value=5.0,
            description="Inactive Discount",
            is_active=False
        )

        engine.add_discount(active_discount)
        engine.add_discount(inactive_discount)

        active_discounts = engine.get_active_discounts()
        assert len(active_discounts) == 1
        assert active_discounts[0].description == "Active Discount"

    def test_validation_errors(self, engine):
        """Test validation error handling"""
        # Test invalid discount type
        with pytest.raises(ValueError):
            invalid_discount = DiscountConfig(
                discount_type="invalid",
                discount_value=10.0,
                description="Invalid Discount"
            )
            engine.add_discount(invalid_discount)

        # Test negative discount value
        with pytest.raises(ValueError):
            negative_discount = DiscountConfig(
                discount_type="percentage",
                discount_value=-10.0,
                description="Negative Discount"
            )
            engine.add_discount(negative_discount)

        # Test negative accessory price
        with pytest.raises(ValueError):
            negative_accessory = AccessoryConfig(
                accessory_id=1,
                name="Invalid Accessory",
                price=-100.0
            )
            engine.add_accessory(negative_accessory)

    def test_calculation_breakdown(self, engine):
        """Test that calculation breakdown is properly populated"""
        base_price = 1000.0
        result = engine.calculate_modifications(base_price)

        breakdown = result.calculation_breakdown
        assert "original_amount" in breakdown
        assert "accessories_cost" in breakdown
        assert "amount_with_accessories" in breakdown
        assert "total_discounts" in breakdown
        assert "total_surcharges" in breakdown
        assert "final_amount" in breakdown
        assert "net_modification" in breakdown

        assert breakdown["original_amount"] == 1000.0
        assert breakdown["final_amount"] == 1000.0
        assert breakdown["net_modification"] == 0.0
