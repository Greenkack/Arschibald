"""Tests for PV-specific pricing engine"""

from unittest.mock import patch

import pytest

# Import the PV pricing engine
try:
    from pricing.enhanced_pricing_engine import PricingResult
    from pricing.pv_pricing_engine import (
        PV_CATEGORIES,
        PVPriceComponent,
        PVPricingEngine,
        calculate_pv_system_pricing,
        create_pv_pricing_engine,
    )
except ImportError as e:
    pytest.skip(
        f"Cannot import PV pricing engine: {e}",
        allow_module_level=True)


class TestPVPriceComponent:
    """Test PV-specific price component"""

    def test_pv_component_creation(self):
        """Test creating PV price component with all fields"""
        component = PVPriceComponent(
            product_id=1,
            model_name="Test PV Module 400W",
            category="modules",
            brand="TestBrand",
            quantity=20,
            price_euro=180.0,
            calculate_per="Stück",
            capacity_w=400.0,
            efficiency_percent=21.5,
            technology="TOPCon",
            warranty_years=25,
            system_capacity_kwp=8.0,
            module_count=20,
            installation_complexity="simple"
        )

        assert component.product_id == 1
        assert component.model_name == "Test PV Module 400W"
        assert component.category == "modules"
        assert component.quantity == 20
        assert component.system_capacity_kwp == 8.0
        assert component.installation_complexity == "simple"

        # Check that dynamic keys are generated
        assert "TEST_PV_MODULE_400W_SYSTEM_KWP" in component.dynamic_keys
        assert "TEST_PV_MODULE_400W_MODULE_COUNT" in component.dynamic_keys
        assert "TEST_PV_MODULE_400W_TECH_TYPE" in component.dynamic_keys

    def test_pv_component_complexity_adjustment(self):
        """Test installation complexity price adjustment"""
        # Simple installation
        simple_comp = PVPriceComponent(
            product_id=1,
            model_name="Test Module",
            category="modules",
            quantity=1,
            price_euro=100.0,
            installation_complexity="simple"
        )

        # Complex installation
        complex_comp = PVPriceComponent(
            product_id=1,
            model_name="Test Module",
            category="modules",
            quantity=1,
            price_euro=100.0,
            installation_complexity="complex"
        )

        # Complex should be 20% more expensive
        assert complex_comp.total_price > simple_comp.total_price
        expected_complex_price = simple_comp.total_price * 1.2
        assert abs(complex_comp.total_price - expected_complex_price) < 0.01

    def test_pv_component_efficiency_keys(self):
        """Test efficiency-based dynamic key generation"""
        high_eff_comp = PVPriceComponent(
            product_id=1,
            model_name="High Efficiency Module",
            category="modules",
            quantity=1,
            price_euro=200.0,
            efficiency_percent=22.0
        )

        standard_eff_comp = PVPriceComponent(
            product_id=2,
            model_name="Standard Module",
            category="modules",
            quantity=1,
            price_euro=180.0,
            efficiency_percent=19.0
        )

        # Check efficiency tier classification
        assert high_eff_comp.dynamic_keys["HIGH_EFFICIENCY_MODULE_EFFICIENCY_TIER"] == "high"
        assert standard_eff_comp.dynamic_keys["STANDARD_MODULE_EFFICIENCY_TIER"] == "standard"


class TestPVPricingEngine:
    """Test PV pricing engine functionality"""

    @pytest.fixture
    def pv_engine(self):
        """Create PV pricing engine for testing"""
        return PVPricingEngine()

    @pytest.fixture
    def sample_pv_products(self):
        """Sample PV products for testing"""
        return {
            "module": {
                "id": 1,
                "model_name": "PV Module 400W Mono",
                "category": "pv-modul",
                "brand": "TestSolar",
                "price_euro": 180.0,
                "calculate_per": "Stück",
                "capacity_w": 400.0,
                "efficiency_percent": 21.0,
                "technology": "TOPCon",
                "warranty_years": 25,
                "length_m": 2.0,
                "width_m": 1.0,
                "weight_kg": 22.0
            },
            "inverter": {
                "id": 2,
                "model_name": "String Inverter 8kW",
                "category": "wechselrichter",
                "brand": "InverterCorp",
                "price_euro": 1200.0,
                "calculate_per": "Stück",
                "power_kw": 8.0,
                "efficiency_percent": 97.5,
                "warranty_years": 12
            },
            "storage": {
                "id": 3,
                "model_name": "Battery Storage 10kWh",
                "category": "speicher",
                "brand": "BatteryCorp",
                "price_euro": 4500.0,
                "calculate_per": "Stück",
                "max_kwh_capacity": 10.0,
                "warranty_years": 10,
                "technology": "LiFePO4"
            },
            "mounting": {
                "id": 4,
                "model_name": "Roof Mounting System",
                "category": "montagesystem",
                "brand": "MountCorp",
                "price_euro": 25.0,
                "calculate_per": "kWp"
            }
        }

    def test_pv_engine_initialization(self, pv_engine):
        """Test PV engine initialization"""
        assert pv_engine.system_type == "pv"
        assert pv_engine.key_manager is not None
        assert pv_engine.logger is not None

    def test_classify_pv_component(self, pv_engine, sample_pv_products):
        """Test PV component classification"""
        # Test module classification
        module_cat = pv_engine._classify_pv_component(
            sample_pv_products["module"])
        assert module_cat == "modules"

        # Test inverter classification
        inverter_cat = pv_engine._classify_pv_component(
            sample_pv_products["inverter"])
        assert inverter_cat == "inverters"

        # Test storage classification
        storage_cat = pv_engine._classify_pv_component(
            sample_pv_products["storage"])
        assert storage_cat == "storage"

        # Test mounting classification
        mounting_cat = pv_engine._classify_pv_component(
            sample_pv_products["mounting"])
        assert mounting_cat == "mounting"

    def test_determine_installation_complexity(self, pv_engine):
        """Test installation complexity determination"""
        # Simple installation
        simple_specs = {
            "installation_type": "roof_mounted",
            "roof_type": "standard",
            "obstacles": False
        }
        complexity = pv_engine._determine_installation_complexity(
            {}, simple_specs)
        assert complexity == "simple"

        # Medium complexity
        medium_specs = {
            "installation_type": "roof_mounted",
            "roof_type": "flat",
            "obstacles": True
        }
        complexity = pv_engine._determine_installation_complexity(
            {}, medium_specs)
        assert complexity == "medium"

        # Complex installation
        complex_specs = {
            "installation_type": "ground_mounted",
            "roof_type": "standard"
        }
        complexity = pv_engine._determine_installation_complexity(
            {}, complex_specs)
        assert complexity == "complex"

    @patch('pricing.pv_pricing_engine.get_product_by_id')
    def test_calculate_pv_system_price(
            self,
            mock_get_product,
            pv_engine,
            sample_pv_products):
        """Test complete PV system price calculation"""
        # Mock product database calls
        def mock_product_lookup(product_id):
            product_map = {
                1: sample_pv_products["module"],
                2: sample_pv_products["inverter"],
                3: sample_pv_products["storage"]
            }
            return product_map.get(product_id)

        mock_get_product.side_effect = mock_product_lookup

        # Define system configuration
        system_config = {
            "components": [
                {"product_id": 1, "quantity": 20},  # 20 modules = 8kWp
                {"product_id": 2, "quantity": 1},   # 1 inverter
                {"product_id": 3, "quantity": 1}    # 1 battery
            ],
            "system_specs": {
                "total_capacity_kwp": 8.0,
                "installation_type": "roof_mounted",
                "roof_type": "standard"
            }
        }

        # Calculate pricing
        result = pv_engine.calculate_pv_system_price(system_config)

        # Verify result structure
        assert isinstance(result, PricingResult)
        assert result.base_price > 0
        assert len(result.components) == 3
        assert result.metadata["system_type"] == "pv"
        assert result.metadata["total_capacity_kwp"] == 8.0

        # Verify dynamic keys
        assert "PV_BASE_PRICE_NET" in result.dynamic_keys
        assert "PV_COMPONENT_COUNT" in result.dynamic_keys
        assert "PV_MODULE_COUNT" in result.dynamic_keys
        assert "PV_TOTAL_CAPACITY_KWP" in result.dynamic_keys

        # Verify price calculation
        expected_price = (
            180.0 * 20 +  # Modules
            1200.0 * 1 +  # Inverter
            4500.0 * 1    # Storage
        )
        # Allow for complexity adjustments
        assert result.base_price >= expected_price

    def test_apply_technology_adjustments(self, pv_engine):
        """Test technology-based pricing adjustments"""
        # TOPCon technology component
        topcon_comp = PVPriceComponent(
            product_id=1,
            model_name="TOPCon Module",
            category="modules",
            quantity=1,
            price_euro=100.0,
            technology="TOPCon"
        )

        # PERC technology component
        perc_comp = PVPriceComponent(
            product_id=2,
            model_name="PERC Module",
            category="modules",
            quantity=1,
            price_euro=100.0,
            technology="PERC"
        )

        # Standard component
        standard_comp = PVPriceComponent(
            product_id=3,
            model_name="Standard Module",
            category="modules",
            quantity=1,
            price_euro=100.0
        )

        # Apply adjustments
        topcon_price = pv_engine._apply_technology_adjustments(
            topcon_comp, 100.0)
        perc_price = pv_engine._apply_technology_adjustments(perc_comp, 100.0)
        standard_price = pv_engine._apply_technology_adjustments(
            standard_comp, 100.0)

        # Verify premiums
        assert topcon_price == 105.0  # 5% premium
        assert perc_price == 102.0    # 2% premium
        assert standard_price == 100.0  # No premium

    def test_apply_efficiency_adjustments(self, pv_engine):
        """Test efficiency-based pricing adjustments"""
        # High efficiency component (>22%)
        high_eff_comp = PVPriceComponent(
            product_id=1,
            model_name="High Eff Module",
            category="modules",
            quantity=1,
            price_euro=100.0,
            efficiency_percent=22.5
        )

        # Medium efficiency component (>20%)
        med_eff_comp = PVPriceComponent(
            product_id=2,
            model_name="Med Eff Module",
            category="modules",
            quantity=1,
            price_euro=100.0,
            efficiency_percent=20.5
        )

        # Standard efficiency component
        std_eff_comp = PVPriceComponent(
            product_id=3,
            model_name="Std Eff Module",
            category="modules",
            quantity=1,
            price_euro=100.0,
            efficiency_percent=19.0
        )

        # Apply adjustments
        high_price = pv_engine._apply_efficiency_adjustments(
            high_eff_comp, 100.0)
        med_price = pv_engine._apply_efficiency_adjustments(
            med_eff_comp, 100.0)
        std_price = pv_engine._apply_efficiency_adjustments(
            std_eff_comp, 100.0)

        # Verify premiums
        assert high_price == 108.0  # 8% premium
        assert med_price == 104.0   # 4% premium
        assert std_price == 100.0   # No premium

    def test_calculate_average_efficiency(self, pv_engine):
        """Test average efficiency calculation"""
        components = [
            PVPriceComponent(
                product_id=1,
                model_name="Module A",
                category="modules",
                quantity=10,
                price_euro=100.0,
                capacity_w=400.0,
                efficiency_percent=21.0
            ),
            PVPriceComponent(
                product_id=2,
                model_name="Module B",
                category="modules",
                quantity=10,
                price_euro=100.0,
                capacity_w=400.0,
                efficiency_percent=20.0
            )
        ]

        avg_efficiency = pv_engine._calculate_average_efficiency(components)

        # Should be weighted average: (21*4000 + 20*4000) / 8000 = 20.5
        assert avg_efficiency == 20.5

    def test_calculate_minimum_warranty(self, pv_engine):
        """Test minimum warranty calculation"""
        components = [
            PVPriceComponent(
                product_id=1,
                model_name="Module",
                category="modules",
                quantity=1,
                price_euro=100.0,
                warranty_years=25
            ),
            PVPriceComponent(
                product_id=2,
                model_name="Inverter",
                category="inverters",
                quantity=1,
                price_euro=100.0,
                warranty_years=12
            )
        ]

        min_warranty = pv_engine._calculate_minimum_warranty(components)
        assert min_warranty == 12

    @patch('pricing.pv_pricing_engine.get_product_by_id')
    def test_validate_capacity_matching(
            self,
            mock_get_product,
            pv_engine,
            sample_pv_products):
        """Test capacity matching validation"""
        def mock_product_lookup(product_id):
            if product_id == 1:
                return sample_pv_products["module"]  # 400W module
            if product_id == 2:
                return sample_pv_products["inverter"]  # 8kW inverter
            return None

        mock_get_product.side_effect = mock_product_lookup

        # Well-matched system: 20 * 400W = 8kW modules, 8kW inverter
        components = [
            {"product_id": 1, "quantity": 20},  # 8kW modules
            {"product_id": 2, "quantity": 1}    # 8kW inverter
        ]

        # Should not raise warnings for well-matched system
        pv_engine._validate_capacity_matching(components)

    @patch('pricing.pv_pricing_engine.get_product_by_id')
    def test_calculate_pv_accessories_price(
            self, mock_get_product, pv_engine, sample_pv_products):
        """Test PV accessories pricing calculation"""
        mock_get_product.return_value = {
            "id": 5,
            "model_name": "DC Cable 10m",
            "category": "kabel",
            "price_euro": 5.0,
            "calculate_per": "Meter"
        }

        accessories = [
            {"product_id": 5, "quantity": 50}  # 50 meters of cable
        ]

        result = pv_engine.calculate_pv_accessories_price(accessories, 10000.0)

        assert result["total_price"] == 250.0  # 50m * 5€/m
        assert result["metadata"]["accessory_count"] == 1
        assert "PV_ACCESSORIES_COUNT" in result["dynamic_keys"]
        assert "PV_ACCESSORIES_TOTAL_PRICE" in result["dynamic_keys"]


class TestPVPricingConvenienceFunctions:
    """Test convenience functions for PV pricing"""

    def test_create_pv_pricing_engine(self):
        """Test PV pricing engine creation"""
        engine = create_pv_pricing_engine()
        assert isinstance(engine, PVPricingEngine)
        assert engine.system_type == "pv"

    @patch('pricing.pv_pricing_engine.get_product_by_id')
    def test_calculate_pv_system_pricing(self, mock_get_product):
        """Test convenience function for PV system pricing"""
        mock_get_product.return_value = {
            "id": 1,
            "model_name": "Test Module",
            "category": "pv-modul",
            "price_euro": 100.0,
            "capacity_w": 400.0
        }

        system_config = {
            "components": [{"product_id": 1, "quantity": 10}],
            "system_specs": {"total_capacity_kwp": 4.0}
        }

        result = calculate_pv_system_pricing(system_config)
        assert isinstance(result, PricingResult)
        assert result.base_price > 0


class TestPVCategories:
    """Test PV category definitions"""

    def test_pv_categories_structure(self):
        """Test PV categories are properly defined"""
        assert isinstance(PV_CATEGORIES, dict)

        # Check required categories
        required_categories = [
            "modules",
            "inverters",
            "storage",
            "mounting",
            "cables",
            "accessories",
            "services"]
        for category in required_categories:
            assert category in PV_CATEGORIES
            assert isinstance(PV_CATEGORIES[category], list)
            assert len(PV_CATEGORIES[category]) > 0

    def test_pv_category_keywords(self):
        """Test PV category keywords are reasonable"""
        # Modules should include common module keywords
        module_keywords = PV_CATEGORIES["modules"]
        assert any("modul" in keyword for keyword in module_keywords)

        # Inverters should include inverter keywords
        inverter_keywords = PV_CATEGORIES["inverters"]
        assert any(
            "wechselrichter" in keyword for keyword in inverter_keywords)

        # Storage should include storage keywords
        storage_keywords = PV_CATEGORIES["storage"]
        assert any("speicher" in keyword for keyword in storage_keywords)


if __name__ == "__main__":
    pytest.main([__file__])
