"""Tests for Enhanced Heat Pump Pricing Engine"""

from unittest.mock import patch

import pytest

# Import the enhanced heat pump pricing engine
try:
    from pricing.enhanced_heatpump_pricing import (
        HEATPUMP_CATEGORIES,
        EnhancedHeatPumpPricingEngine,
        HeatPumpPriceComponent,
        calculate_heatpump_system_pricing,
        create_enhanced_heatpump_pricing_engine,
    )
    from pricing.enhanced_pricing_engine import PricingResult
except ImportError as e:
    pytest.skip(
        f"Cannot import enhanced heat pump pricing engine: {e}",
        allow_module_level=True)


class TestHeatPumpPriceComponent:
    """Test heat pump-specific price component"""

    def test_heatpump_component_creation(self):
        """Test creating heat pump price component with all fields"""
        component = HeatPumpPriceComponent(
            product_id=1,
            model_name="Vitocal 200-S 8kW",
            category="heatpump",
            brand="Viessmann",
            quantity=1,
            price_euro=8500.0,
            calculate_per="Stück",
            power_kw=8.0,
            warranty_years=5,
            heating_capacity_kw=8.0,
            cop_rating=4.2,
            refrigerant_type="R32",
            installation_complexity="medium",
            labor_hours_required=16.0,
            beg_eligible=True
        )

        assert component.product_id == 1
        assert component.model_name == "Vitocal 200-S 8kW"
        assert component.category == "heatpump"
        assert component.heating_capacity_kw == 8.0
        assert component.cop_rating == 4.2
        assert component.refrigerant_type == "R32"
        assert component.beg_eligible is True

        # Check that dynamic keys are generated
        assert "VITOCAL_200_S_8KW_HEATING_CAPACITY_KW" in component.dynamic_keys
        assert "VITOCAL_200_S_8KW_COP_RATING" in component.dynamic_keys
        assert "VITOCAL_200_S_8KW_REFRIGERANT" in component.dynamic_keys
        assert "VITOCAL_200_S_8KW_LABOR_HOURS" in component.dynamic_keys
        assert "VITOCAL_200_S_8KW_BEG_ELIGIBLE" in component.dynamic_keys

    def test_heatpump_component_complexity_adjustment(self):
        """Test installation complexity price adjustment"""
        # Simple installation
        simple_comp = HeatPumpPriceComponent(
            product_id=1,
            model_name="Simple Heat Pump",
            category="heatpump",
            quantity=1,
            price_euro=5000.0,
            installation_complexity="simple"
        )

        # Complex installation
        complex_comp = HeatPumpPriceComponent(
            product_id=1,
            model_name="Complex Heat Pump",
            category="heatpump",
            quantity=1,
            price_euro=5000.0,
            installation_complexity="complex"
        )

        # Complex should be 30% more expensive
        assert complex_comp.total_price > simple_comp.total_price
        expected_complex_price = simple_comp.total_price * 1.3
        assert abs(complex_comp.total_price - expected_complex_price) < 0.01

    def test_heatpump_component_labor_cost_integration(self):
        """Test labor cost integration in pricing"""
        component = HeatPumpPriceComponent(
            product_id=1,
            model_name="Heat Pump with Labor",
            category="heatpump",
            quantity=1,
            price_euro=5000.0,
            labor_hours_required=20.0,
            installation_complexity="simple"
        )

        # Should include labor cost (20 hours * 75 EUR/hour = 1500 EUR)
        expected_total = 5000.0 + (20.0 * 75.0)  # Base price + labor
        assert abs(component.total_price - expected_total) < 0.01

    def test_heatpump_component_efficiency_classification(self):
        """Test COP-based efficiency classification"""
        high_eff_comp = HeatPumpPriceComponent(
            product_id=1,
            model_name="High Efficiency HP",
            category="heatpump",
            quantity=1,
            price_euro=6000.0,
            cop_rating=4.8
        )

        medium_eff_comp = HeatPumpPriceComponent(
            product_id=2,
            model_name="Medium Efficiency HP",
            category="heatpump",
            quantity=1,
            price_euro=5500.0,
            cop_rating=4.1
        )

        standard_eff_comp = HeatPumpPriceComponent(
            product_id=3,
            model_name="Standard Efficiency HP",
            category="heatpump",
            quantity=1,
            price_euro=5000.0,
            cop_rating=3.6
        )

        # Check efficiency classifications
        assert high_eff_comp.dynamic_keys["HIGH_EFFICIENCY_HP_EFFICIENCY_CLASS"] == "A+++"
        assert medium_eff_comp.dynamic_keys["MEDIUM_EFFICIENCY_HP_EFFICIENCY_CLASS"] == "A++"
        assert standard_eff_comp.dynamic_keys["STANDARD_EFFICIENCY_HP_EFFICIENCY_CLASS"] == "A+"


class TestEnhancedHeatPumpPricingEngine:
    """Test enhanced heat pump pricing engine functionality"""

    @pytest.fixture
    def hp_engine(self):
        """Create enhanced heat pump pricing engine for testing"""
        return EnhancedHeatPumpPricingEngine()

    @pytest.fixture
    def sample_heatpump_products(self):
        """Sample heat pump products for testing"""
        return {
            "heatpump": {
                "id": 1,
                "model_name": "Vitocal 200-S 8kW",
                "category": "waermepumpe",
                "brand": "Viessmann",
                "price_euro": 8500.0,
                "calculate_per": "Stück",
                "power_kw": 8.0,
                "warranty_years": 5,
                "description": "Luft-Wasser-Wärmepumpe mit COP 4.2 und R32 Kältemittel",
                "labor_hours": 16.0},
            "storage": {
                "id": 2,
                "model_name": "Vitocell 300-V 300L",
                "category": "pufferspeicher",
                "brand": "Viessmann",
                "price_euro": 1200.0,
                "calculate_per": "Stück",
                "max_kwh_capacity": 15.0,
                "warranty_years": 10,
                "labor_hours": 4.0},
            "installation": {
                "id": 3,
                "model_name": "Wärmepumpen Installation Standard",
                "category": "dienstleistung",
                "brand": "ServiceCorp",
                "price_euro": 2500.0,
                "calculate_per": "pauschal",
                "labor_hours": 32.0,
                "description": "Komplette Installation und Inbetriebnahme"},
            "accessories": {
                "id": 4,
                "model_name": "Rohrleitungsset DN25",
                "category": "zubehoer",
                "brand": "PipeCorp",
                "price_euro": 150.0,
                "calculate_per": "Stück",
                "labor_hours": 2.0}}

    def test_hp_engine_initialization(self, hp_engine):
        """Test heat pump engine initialization"""
        assert hp_engine.system_type == "heatpump"
        assert hp_engine.key_manager is not None
        assert hp_engine.logger is not None
        assert hp_engine.labor_rate == 75.0

    def test_classify_heatpump_component(
            self, hp_engine, sample_heatpump_products):
        """Test heat pump component classification"""
        # Test heat pump classification
        hp_cat = hp_engine._classify_heatpump_component(
            sample_heatpump_products["heatpump"])
        assert hp_cat == "heatpump"

        # Test storage classification
        storage_cat = hp_engine._classify_heatpump_component(
            sample_heatpump_products["storage"])
        assert storage_cat == "storage"

        # Test installation classification
        install_cat = hp_engine._classify_heatpump_component(
            sample_heatpump_products["installation"])
        assert install_cat == "installation"

        # Test accessories classification
        acc_cat = hp_engine._classify_heatpump_component(
            sample_heatpump_products["accessories"])
        assert acc_cat == "accessories"

    def test_determine_installation_complexity(self, hp_engine):
        """Test installation complexity determination"""
        # Simple installation
        simple_specs = {
            "building_type": "residential",
            "existing_heating_system": "none",
            "requires_electrical_upgrade": False
        }
        complexity = hp_engine._determine_installation_complexity(
            {}, simple_specs)
        assert complexity == "simple"

        # Medium complexity
        medium_specs = {
            "building_type": "residential",
            "existing_heating_system": "gas",
            "requires_electrical_upgrade": True
        }
        complexity = hp_engine._determine_installation_complexity(
            {}, medium_specs)
        assert complexity == "medium"

        # Complex installation
        complex_specs = {
            "building_type": "commercial",
            "existing_heating_system": "oil"
        }
        complexity = hp_engine._determine_installation_complexity(
            {}, complex_specs)
        assert complexity == "complex"

    def test_extract_cop_rating(self, hp_engine):
        """Test COP rating extraction from product data"""
        # Direct COP field
        product_with_cop = {"cop": 4.2}
        cop = hp_engine._extract_cop_rating(product_with_cop)
        assert cop == 4.2

        # COP in description
        product_with_desc = {
            "description": "Wärmepumpe mit COP 4.5 bei A7/W35",
            "model_name": "Test HP"
        }
        cop = hp_engine._extract_cop_rating(product_with_desc)
        assert cop == 4.5

        # Technology-based default
        product_inverter = {"technology": "Inverter Wärmepumpe"}
        cop = hp_engine._extract_cop_rating(product_inverter)
        assert cop == 4.2

        # Air source default
        product_air = {"technology": "Luft-Wasser"}
        cop = hp_engine._extract_cop_rating(product_air)
        assert cop == 3.8

    def test_extract_refrigerant_type(self, hp_engine):
        """Test refrigerant type extraction"""
        # Direct refrigerant field
        product_with_ref = {"refrigerant": "R32"}
        ref = hp_engine._extract_refrigerant_type(product_with_ref)
        assert ref == "R32"

        # Refrigerant in description
        product_with_desc = {
            "description": "Wärmepumpe mit R290 Kältemittel",
            "model_name": "Eco HP"
        }
        ref = hp_engine._extract_refrigerant_type(product_with_desc)
        assert ref == "R290"

        # No refrigerant info
        product_no_ref = {"description": "Standard Wärmepumpe"}
        ref = hp_engine._extract_refrigerant_type(product_no_ref)
        assert ref is None

    def test_determine_beg_eligibility(self, hp_engine):
        """Test BEG eligibility determination"""
        # Heat pump category - should be eligible
        hp_product = {"category": "waermepumpe"}
        eligible = hp_engine._determine_beg_eligibility(hp_product)
        assert eligible is True

        # High COP - should be eligible
        high_cop_product = {
            "description": "HP with COP 4.0",
            "model_name": "Test"}
        eligible = hp_engine._determine_beg_eligibility(high_cop_product)
        assert eligible is True

        # Low COP - should not be eligible
        low_cop_product = {
            "description": "HP with COP 3.0",
            "model_name": "Test"}
        eligible = hp_engine._determine_beg_eligibility(low_cop_product)
        assert eligible is False

    @patch('pricing.enhanced_heatpump_pricing.get_product_by_id')
    def test_calculate_heatpump_system_price(
            self,
            mock_get_product,
            hp_engine,
            sample_heatpump_products):
        """Test complete heat pump system price calculation"""
        # Mock product database calls
        def mock_product_lookup(product_id):
            product_map = {
                1: sample_heatpump_products["heatpump"],
                2: sample_heatpump_products["storage"],
                3: sample_heatpump_products["installation"]
            }
            return product_map.get(product_id)

        mock_get_product.side_effect = mock_product_lookup

        # Define system configuration
        system_config = {
            "components": [
                {"product_id": 1, "quantity": 1},  # Heat pump
                {"product_id": 2, "quantity": 1},  # Storage
                {"product_id": 3, "quantity": 1}   # Installation
            ],
            "system_specs": {
                "heating_demand_kw": 8.0,
                "building_type": "residential",
                "existing_heating_system": "gas"
            }
        }

        # Calculate pricing
        result = hp_engine.calculate_heatpump_system_price(system_config)

        # Verify result structure
        assert isinstance(result, PricingResult)
        assert result.base_price > 0
        assert len(result.components) == 3
        assert result.metadata["system_type"] == "heatpump"
        assert result.metadata["heating_demand_kw"] == 8.0

        # Verify dynamic keys
        assert "HP_BASE_PRICE_NET" in result.dynamic_keys
        assert "HP_COMPONENT_COUNT" in result.dynamic_keys
        assert "HP_TOTAL_HEATING_CAPACITY_KW" in result.dynamic_keys
        assert "HP_TOTAL_LABOR_HOURS" in result.dynamic_keys
        assert "HP_BEG_ELIGIBLE_COMPONENTS" in result.dynamic_keys

    def test_apply_cop_adjustments(self, hp_engine):
        """Test COP-based pricing adjustments"""
        # Very high COP component
        very_high_cop_comp = HeatPumpPriceComponent(
            product_id=1,
            model_name="Very High COP HP",
            category="heatpump",
            quantity=1,
            price_euro=1000.0,
            cop_rating=4.8
        )

        # High COP component
        high_cop_comp = HeatPumpPriceComponent(
            product_id=2,
            model_name="High COP HP",
            category="heatpump",
            quantity=1,
            price_euro=1000.0,
            cop_rating=4.2
        )

        # Standard COP component
        standard_cop_comp = HeatPumpPriceComponent(
            product_id=3,
            model_name="Standard COP HP",
            category="heatpump",
            quantity=1,
            price_euro=1000.0,
            cop_rating=3.5
        )

        # Apply adjustments
        very_high_price = hp_engine._apply_cop_adjustments(
            very_high_cop_comp, 1000.0)
        high_price = hp_engine._apply_cop_adjustments(high_cop_comp, 1000.0)
        standard_price = hp_engine._apply_cop_adjustments(
            standard_cop_comp, 1000.0)

        # Verify premiums
        assert very_high_price == 1100.0  # 10% premium
        assert high_price == 1050.0       # 5% premium
        assert standard_price == 1000.0   # No premium

    def test_apply_refrigerant_adjustments(self, hp_engine):
        """Test refrigerant-based pricing adjustments"""
        # Natural refrigerant component
        natural_comp = HeatPumpPriceComponent(
            product_id=1,
            model_name="Natural Refrigerant HP",
            category="heatpump",
            quantity=1,
            price_euro=1000.0,
            refrigerant_type="R290"
        )

        # R32 refrigerant component
        r32_comp = HeatPumpPriceComponent(
            product_id=2,
            model_name="R32 HP",
            category="heatpump",
            quantity=1,
            price_euro=1000.0,
            refrigerant_type="R32"
        )

        # Standard refrigerant component
        standard_comp = HeatPumpPriceComponent(
            product_id=3,
            model_name="Standard HP",
            category="heatpump",
            quantity=1,
            price_euro=1000.0,
            refrigerant_type="R410A"
        )

        # Apply adjustments
        natural_price = hp_engine._apply_refrigerant_adjustments(
            natural_comp, 1000.0)
        r32_price = hp_engine._apply_refrigerant_adjustments(r32_comp, 1000.0)
        standard_price = hp_engine._apply_refrigerant_adjustments(
            standard_comp, 1000.0)

        # Verify premiums
        assert natural_price == 1080.0  # 8% premium for natural refrigerant
        assert r32_price == 1020.0      # 2% premium for R32
        assert standard_price == 1000.0  # No premium

    def test_calculate_average_cop(self, hp_engine):
        """Test average COP calculation"""
        components = [
            HeatPumpPriceComponent(
                product_id=1,
                model_name="HP A",
                category="heatpump",
                quantity=1,
                price_euro=5000.0,
                heating_capacity_kw=6.0,
                cop_rating=4.0
            ),
            HeatPumpPriceComponent(
                product_id=2,
                model_name="HP B",
                category="heatpump",
                quantity=1,
                price_euro=6000.0,
                heating_capacity_kw=4.0,
                cop_rating=4.5
            )
        ]

        avg_cop = hp_engine._calculate_average_cop(components)

        # Should be weighted average: (4.0*6.0 + 4.5*4.0) / 10.0 = 4.2
        assert avg_cop == 4.2

    def test_calculate_beg_eligibility_ratio(self, hp_engine):
        """Test BEG eligibility ratio calculation"""
        components = [
            HeatPumpPriceComponent(
                product_id=1,
                model_name="Eligible HP",
                category="heatpump",
                quantity=1,
                price_euro=5000.0,
                beg_eligible=True
            ),
            HeatPumpPriceComponent(
                product_id=2,
                model_name="Non-eligible Accessory",
                category="accessories",
                quantity=1,
                price_euro=100.0,
                beg_eligible=False
            ),
            HeatPumpPriceComponent(
                product_id=3,
                model_name="Eligible Storage",
                category="storage",
                quantity=1,
                price_euro=1000.0,
                beg_eligible=True
            )
        ]

        ratio = hp_engine._calculate_beg_eligibility_ratio(components)
        assert ratio == 2.0 / 3.0  # 2 out of 3 components eligible

    @patch('pricing.enhanced_heatpump_pricing.calculate_beg_subsidy')
    def test_calculate_beg_subsidy_integration(
            self, mock_beg_subsidy, hp_engine):
        """Test BEG subsidy integration"""
        # Mock BEG subsidy calculation
        mock_beg_subsidy.return_value = {
            "applied_pct": 50.0,
            "subsidy_amount_net": 5000.0,
            "eligible_costs_net": 10000.0,
            "effective_total_after_subsidy_net": 5000.0
        }

        # Create mock pricing result
        pricing_result = PricingResult(
            base_price=10000.0,
            components=[],
            dynamic_keys={},
            metadata={}
        )

        # BEG configuration
        beg_config = {
            "natural_refrigerant": True,
            "replace_old_heating": True,
            "low_income": False
        }

        # Calculate BEG integration
        result = hp_engine.calculate_beg_subsidy_integration(
            pricing_result, beg_config)

        # Verify integration
        assert result["integration_successful"] is True
        assert "HP_BEG_SUBSIDY_PERCENT" in result["dynamic_keys"]
        assert "HP_BEG_SUBSIDY_AMOUNT" in result["dynamic_keys"]
        assert result["dynamic_keys"]["HP_BEG_NATURAL_REFRIGERANT"] is True
        assert result["dynamic_keys"]["HP_BEG_REPLACE_OLD_HEATING"] is True
        assert result["dynamic_keys"]["HP_BEG_LOW_INCOME"] is False


class TestHeatPumpPricingConvenienceFunctions:
    """Test convenience functions for heat pump pricing"""

    def test_create_enhanced_heatpump_pricing_engine(self):
        """Test enhanced heat pump pricing engine creation"""
        engine = create_enhanced_heatpump_pricing_engine()
        assert isinstance(engine, EnhancedHeatPumpPricingEngine)
        assert engine.system_type == "heatpump"

    @patch('pricing.enhanced_heatpump_pricing.get_product_by_id')
    def test_calculate_heatpump_system_pricing(self, mock_get_product):
        """Test convenience function for heat pump system pricing"""
        mock_get_product.return_value = {
            "id": 1,
            "model_name": "Test Heat Pump",
            "category": "waermepumpe",
            "price_euro": 5000.0,
            "power_kw": 8.0,
            "labor_hours": 16.0
        }

        system_config = {
            "components": [{"product_id": 1, "quantity": 1}],
            "system_specs": {"heating_demand_kw": 8.0}
        }

        result = calculate_heatpump_system_pricing(system_config)
        assert isinstance(result, PricingResult)
        assert result.base_price > 0


class TestHeatPumpCategories:
    """Test heat pump category definitions"""

    def test_heatpump_categories_structure(self):
        """Test heat pump categories are properly defined"""
        assert isinstance(HEATPUMP_CATEGORIES, dict)

        # Check required categories
        required_categories = [
            "heatpump",
            "storage",
            "installation",
            "accessories",
            "controls",
            "piping"]
        for category in required_categories:
            assert category in HEATPUMP_CATEGORIES
            assert isinstance(HEATPUMP_CATEGORIES[category], list)
            assert len(HEATPUMP_CATEGORIES[category]) > 0

    def test_heatpump_category_keywords(self):
        """Test heat pump category keywords are reasonable"""
        # Heat pump should include common heat pump keywords
        hp_keywords = HEATPUMP_CATEGORIES["heatpump"]
        assert any("waermepumpe" in keyword for keyword in hp_keywords)
        assert any("heatpump" in keyword for keyword in hp_keywords)

        # Storage should include storage keywords
        storage_keywords = HEATPUMP_CATEGORIES["storage"]
        assert any("speicher" in keyword for keyword in storage_keywords)

        # Installation should include service keywords
        install_keywords = HEATPUMP_CATEGORIES["installation"]
        assert any("dienstleistung" in keyword for keyword in install_keywords)


if __name__ == "__main__":
    pytest.main([__file__])
