"""Tests for Combined Pricing Engine"""

from unittest.mock import Mock, patch

import pytest

# Import the combined pricing engine
try:
    from pricing.combined_pricing_engine import (
        CombinedPricingEngine,
        CombinedPricingResult,
        calculate_combined_system_pricing,
        create_combined_pricing_engine,
    )
    from pricing.enhanced_heatpump_pricing import HeatPumpPriceComponent
    from pricing.enhanced_pricing_engine import PricingResult
    from pricing.pv_pricing_engine import PVPriceComponent
except ImportError as e:
    pytest.skip(
        f"Cannot import combined pricing engine: {e}",
        allow_module_level=True)


class TestCombinedPricingResult:
    """Test combined pricing result data structure"""

    def test_combined_pricing_result_creation(self):
        """Test creating combined pricing result"""
        result = CombinedPricingResult(
            combined_base_price=15000.0,
            combined_final_price=14250.0,
            system_synergy_discount=750.0,
            metadata={"system_type": "combined"}
        )

        assert result.combined_base_price == 15000.0
        assert result.combined_final_price == 14250.0
        assert result.system_synergy_discount == 750.0
        assert result.metadata["system_type"] == "combined"
        assert result.calculation_timestamp is not None


class TestCombinedPricingEngine:
    """Test combined pricing engine functionality"""

    @pytest.fixture
    def combined_engine(self):
        """Create combined pricing engine for testing"""
        return CombinedPricingEngine()

    @pytest.fixture
    def mock_pv_result(self):
        """Mock PV pricing result"""
        pv_components = [
            PVPriceComponent(
                product_id=1,
                model_name="PV Module 400W",
                category="modules",
                quantity=20,
                price_euro=180.0,
                smart_home=True
            )
        ]

        return PricingResult(
            base_price=8000.0,
            components=pv_components,
            dynamic_keys={
                "PV_TOTAL_CAPACITY_KWP": 8.0,
                "PV_MODULE_COUNT": 20,
                "PV_BASE_PRICE_NET": 8000.0
            },
            metadata={"system_type": "pv"}
        )

    @pytest.fixture
    def mock_heatpump_result(self):
        """Mock heat pump pricing result"""
        hp_components = [
            HeatPumpPriceComponent(
                product_id=2,
                model_name="Heat Pump 8kW",
                category="heatpump",
                quantity=1,
                price_euro=7000.0,
                smart_home=True
            )
        ]

        return PricingResult(
            base_price=7000.0,
            components=hp_components,
            dynamic_keys={
                "HP_TOTAL_HEATING_CAPACITY_KW": 8.0,
                "HP_BASE_PRICE_NET": 7000.0,
                "HP_BEG_ELIGIBLE_COMPONENTS": 1
            },
            metadata={"system_type": "heatpump"}
        )

    def test_combined_engine_initialization(self, combined_engine):
        """Test combined engine initialization"""
        assert combined_engine.system_type == "combined"
        assert combined_engine.pv_engine is not None
        assert combined_engine.heatpump_engine is not None
        assert combined_engine.logger is not None

    @patch('pricing.combined_pricing_engine.PVPricingEngine')
    @patch('pricing.combined_pricing_engine.EnhancedHeatPumpPricingEngine')
    def test_calculate_combined_system_price(
            self,
            mock_hp_engine_class,
            mock_pv_engine_class,
            combined_engine,
            mock_pv_result,
            mock_heatpump_result):
        """Test complete combined system price calculation"""
        # Mock the engine instances
        mock_pv_engine = Mock()
        mock_hp_engine = Mock()
        mock_pv_engine_class.return_value = mock_pv_engine
        mock_hp_engine_class.return_value = mock_hp_engine

        # Set up mock returns
        mock_pv_engine.calculate_pv_system_price.return_value = mock_pv_result
        mock_hp_engine.calculate_heatpump_system_price.return_value = mock_heatpump_result

        # Replace engine instances
        combined_engine.pv_engine = mock_pv_engine
        combined_engine.heatpump_engine = mock_hp_engine

        # Define system configuration
        system_config = {
            "pv_system": {
                "components": [{"product_id": 1, "quantity": 20}],
                "system_specs": {"total_capacity_kwp": 8.0}
            },
            "heatpump_system": {
                "components": [{"product_id": 2, "quantity": 1}],
                "system_specs": {"heating_demand_kw": 8.0}
            },
            "combined_specs": {
                "synergy_discount_percent": 5.0,
                "energy_management_system": True
            }
        }

        # Calculate combined pricing
        result = combined_engine.calculate_combined_system_price(system_config)

        # Verify result structure
        assert isinstance(result, CombinedPricingResult)
        assert result.pv_result == mock_pv_result
        assert result.heatpump_result == mock_heatpump_result
        assert result.combined_base_price == 15000.0  # 8000 + 7000
        assert result.system_synergy_discount > 0
        assert result.combined_final_price < result.combined_base_price

        # Verify metadata
        assert result.metadata["system_type"] == "combined"
        assert result.metadata["has_pv"] is True
        assert result.metadata["has_heatpump"] is True
        assert result.metadata["synergy_discount_applied"] is True

    def test_calculate_system_synergy_discount(
            self, combined_engine, mock_pv_result, mock_heatpump_result):
        """Test system synergy discount calculation"""
        combined_specs = {
            "synergy_discount_percent": 5.0,
            "energy_management_system": True,
            "max_synergy_discount_percent": 15.0
        }

        discount = combined_engine._calculate_system_synergy_discount(
            mock_pv_result, mock_heatpump_result, combined_specs
        )

        # Should apply base 5% + 3% for energy management + 2% for smart home =
        # 10%
        expected_discount = 15000.0 * 0.10  # 10% of combined base price
        assert abs(discount - expected_discount) < 0.01

    def test_calculate_system_synergy_discount_single_system(
            self, combined_engine, mock_pv_result):
        """Test synergy discount with only one system (should be 0)"""
        combined_specs = {"synergy_discount_percent": 5.0}

        discount = combined_engine._calculate_system_synergy_discount(
            mock_pv_result, None, combined_specs
        )

        assert discount == 0.0

    def test_has_smart_home_integration(
            self,
            combined_engine,
            mock_pv_result,
            mock_heatpump_result):
        """Test smart home integration detection"""
        # Both systems have smart home integration
        has_integration = combined_engine._has_smart_home_integration(
            mock_pv_result, mock_heatpump_result
        )
        assert has_integration is True

        # Remove smart home from one component
        mock_pv_result.components[0].smart_home = False
        has_integration = combined_engine._has_smart_home_integration(
            mock_pv_result, mock_heatpump_result
        )
        assert has_integration is False

    def test_has_storage_synergy(
            self,
            combined_engine,
            mock_pv_result,
            mock_heatpump_result):
        """Test storage synergy detection"""
        # Add storage component to PV system
        storage_component = PVPriceComponent(
            product_id=3,
            model_name="Battery Storage",
            category="storage",
            quantity=1,
            price_euro=5000.0
        )
        mock_pv_result.components.append(storage_component)

        has_synergy = combined_engine._has_storage_synergy(
            mock_pv_result, mock_heatpump_result
        )
        assert has_synergy is True

    def test_generate_combined_dynamic_keys(
            self,
            combined_engine,
            mock_pv_result,
            mock_heatpump_result):
        """Test combined dynamic key generation"""
        combined_base_price = 15000.0
        combined_final_price = 14250.0
        synergy_discount = 750.0

        keys = combined_engine._generate_combined_dynamic_keys(
            mock_pv_result, mock_heatpump_result, combined_base_price,
            combined_final_price, synergy_discount
        )

        # Check combined system keys
        assert keys["COMBINED_BASE_PRICE"] == combined_base_price
        assert keys["COMBINED_FINAL_PRICE"] == combined_final_price
        assert keys["COMBINED_SYNERGY_DISCOUNT"] == synergy_discount
        assert keys["COMBINED_SYSTEM_COUNT"] == 2

        # Check individual system totals
        assert keys["COMBINED_PV_TOTAL"] == 8000.0
        assert keys["COMBINED_HP_TOTAL"] == 7000.0

        # Check capacity information
        assert keys["COMBINED_PV_CAPACITY_KWP"] == 8.0
        assert keys["COMBINED_HP_CAPACITY_KW"] == 8.0

        # Check prefixed individual keys
        assert "PV_PV_TOTAL_CAPACITY_KWP" in keys
        assert "HP_HP_TOTAL_HEATING_CAPACITY_KW" in keys

    def test_extract_pv_capacity(self, combined_engine, mock_pv_result):
        """Test PV capacity extraction"""
        capacity = combined_engine._extract_pv_capacity(mock_pv_result)
        assert capacity == 8.0

        # Test with None result
        capacity = combined_engine._extract_pv_capacity(None)
        assert capacity is None

    def test_extract_heatpump_capacity(
            self, combined_engine, mock_heatpump_result):
        """Test heat pump capacity extraction"""
        capacity = combined_engine._extract_heatpump_capacity(
            mock_heatpump_result)
        assert capacity == 8.0

        # Test with None result
        capacity = combined_engine._extract_heatpump_capacity(None)
        assert capacity is None

    def test_calculate_combined_financing(self, combined_engine):
        """Test combined system financing calculation"""
        combined_result = CombinedPricingResult(
            combined_final_price=15000.0
        )

        financing_config = {
            "down_payment": 3000.0,
            "interest_rate_percent": 4.0,
            "loan_term_years": 10
        }

        financing_result = combined_engine.calculate_combined_financing(
            combined_result, financing_config
        )

        assert financing_result["financing_required"] is True
        assert financing_result["loan_amount"] == 15000.0
        assert financing_result["down_payment"] == 3000.0
        assert financing_result["financed_amount"] == 12000.0
        assert financing_result["monthly_payment"] > 0
        assert "dynamic_keys" in financing_result

    def test_calculate_combined_financing_no_loan_needed(
            self, combined_engine):
        """Test financing when down payment covers full amount"""
        combined_result = CombinedPricingResult(
            combined_final_price=10000.0
        )

        financing_config = {
            "down_payment": 12000.0,  # More than total price
            "interest_rate_percent": 4.0,
            "loan_term_years": 10
        }

        financing_result = combined_engine.calculate_combined_financing(
            combined_result, financing_config
        )

        assert financing_result["financing_required"] is False
        assert financing_result["financed_amount"] == 0.0
        assert financing_result["monthly_payment"] == 0.0

    @patch('pricing.combined_pricing_engine.EnhancedHeatPumpPricingEngine')
    def test_calculate_combined_subsidies(
            self,
            mock_hp_engine_class,
            combined_engine,
            mock_pv_result,
            mock_heatpump_result):
        """Test combined system subsidy calculation"""
        # Mock heat pump engine for BEG calculation
        mock_hp_engine = Mock()
        mock_hp_engine.calculate_beg_subsidy_integration.return_value = {
            "integration_successful": True,
            "beg_calculation": {"subsidy_amount_net": 3500.0}
        }
        combined_engine.heatpump_engine = mock_hp_engine

        combined_result = CombinedPricingResult(
            pv_result=mock_pv_result,
            heatpump_result=mock_heatpump_result,
            combined_final_price=15000.0
        )

        subsidy_config = {
            "pv_subsidies": {
                "subsidy_rate_percent": 10.0,
                "max_subsidy_amount": 1000.0
            },
            "beg_subsidies": {
                "natural_refrigerant": True,
                "replace_old_heating": True
            },
            "combined_system_bonus": {
                "bonus_rate_percent": 2.0,
                "max_bonus_amount": 500.0
            }
        }

        subsidy_result = combined_engine.calculate_combined_subsidies(
            combined_result, subsidy_config
        )

        assert subsidy_result["total_subsidies"] > 0
        assert "pv_subsidies" in subsidy_result["subsidy_details"]
        assert "beg_subsidies" in subsidy_result["subsidy_details"]
        assert "combined_bonus" in subsidy_result["subsidy_details"]
        assert subsidy_result["final_price_after_subsidies"] < combined_result.combined_final_price

    def test_calculate_pv_subsidies(self, combined_engine, mock_pv_result):
        """Test PV subsidy calculation"""
        pv_subsidy_config = {
            "subsidy_rate_percent": 15.0,
            "max_subsidy_amount": 1500.0
        }

        subsidy = combined_engine._calculate_pv_subsidies(
            mock_pv_result, pv_subsidy_config)

        # Should be 15% of 8000 = 1200, which is less than max 1500
        assert subsidy == 1200.0

    def test_calculate_pv_subsidies_with_cap(
            self, combined_engine, mock_pv_result):
        """Test PV subsidy calculation with cap"""
        pv_subsidy_config = {
            "subsidy_rate_percent": 15.0,
            "max_subsidy_amount": 1000.0  # Lower cap
        }

        subsidy = combined_engine._calculate_pv_subsidies(
            mock_pv_result, pv_subsidy_config)

        # Should be capped at 1000
        assert subsidy == 1000.0

    def test_calculate_combined_system_bonus(
            self,
            combined_engine,
            mock_pv_result,
            mock_heatpump_result):
        """Test combined system bonus calculation"""
        combined_result = CombinedPricingResult(
            pv_result=mock_pv_result,
            heatpump_result=mock_heatpump_result,
            combined_base_price=15000.0
        )

        bonus_config = {
            "bonus_rate_percent": 3.0,
            "max_bonus_amount": 600.0
        }

        bonus = combined_engine._calculate_combined_system_bonus(
            combined_result, bonus_config)

        # Should be 3% of 15000 = 450, which is less than max 600
        assert bonus == 450.0

    def test_calculate_combined_system_bonus_single_system(
            self, combined_engine, mock_pv_result):
        """Test combined system bonus with only one system (should be 0)"""
        combined_result = CombinedPricingResult(
            pv_result=mock_pv_result,
            heatpump_result=None,
            combined_base_price=8000.0
        )

        bonus_config = {"bonus_rate_percent": 3.0}

        bonus = combined_engine._calculate_combined_system_bonus(
            combined_result, bonus_config)
        assert bonus == 0.0

    def test_validate_combined_system_configuration(self, combined_engine):
        """Test combined system configuration validation"""
        # Valid configuration
        valid_config = {
            "pv_system": {
                "components": [{"product_id": 1, "quantity": 20}],
                "system_specs": {"total_capacity_kwp": 8.0}
            },
            "heatpump_system": {
                "components": [{"product_id": 2, "quantity": 1}],
                "system_specs": {"heating_demand_kw": 8.0}
            }
        }

        validation = combined_engine.validate_combined_system_configuration(
            valid_config)

        assert validation["is_valid"] is True
        assert len(validation["errors"]) == 0

    def test_validate_combined_system_configuration_empty(
            self, combined_engine):
        """Test validation with empty configuration"""
        empty_config = {
            "pv_system": {},
            "heatpump_system": {}
        }

        validation = combined_engine.validate_combined_system_configuration(
            empty_config)

        assert validation["is_valid"] is False
        assert len(validation["errors"]) > 0
        assert "At least one system" in validation["errors"][0]

    def test_check_system_compatibility(self, combined_engine):
        """Test system compatibility checking"""
        # Well-balanced system
        pv_config = {
            "system_specs": {"total_capacity_kwp": 8.0}
        }
        heatpump_config = {
            "system_specs": {"heating_demand_kw": 8.0}
        }

        recommendations = combined_engine._check_system_compatibility(
            pv_config, heatpump_config)

        # Should have recommendations for smart home integration
        assert len(recommendations) > 0
        assert any("smart home" in rec.lower() for rec in recommendations)

    def test_check_system_compatibility_undersized_pv(self, combined_engine):
        """Test compatibility check with undersized PV"""
        pv_config = {
            "system_specs": {"total_capacity_kwp": 2.0}  # Small PV
        }
        heatpump_config = {
            "system_specs": {"heating_demand_kw": 10.0}  # Large heat pump
        }

        recommendations = combined_engine._check_system_compatibility(
            pv_config, heatpump_config)

        # Should recommend increasing PV capacity
        assert any("increasing PV capacity" in rec for rec in recommendations)

    def test_check_system_compatibility_oversized_pv(self, combined_engine):
        """Test compatibility check with oversized PV"""
        pv_config = {
            "system_specs": {"total_capacity_kwp": 20.0}  # Large PV
        }
        heatpump_config = {
            "system_specs": {"heating_demand_kw": 5.0}  # Small heat pump
        }

        recommendations = combined_engine._check_system_compatibility(
            pv_config, heatpump_config)

        # Should recommend battery storage or reducing PV
        assert any("oversized" in rec for rec in recommendations)


class TestCombinedPricingConvenienceFunctions:
    """Test convenience functions for combined pricing"""

    def test_create_combined_pricing_engine(self):
        """Test combined pricing engine creation"""
        engine = create_combined_pricing_engine()
        assert isinstance(engine, CombinedPricingEngine)
        assert engine.system_type == "combined"

    @patch('pricing.combined_pricing_engine.CombinedPricingEngine')
    def test_calculate_combined_system_pricing(self, mock_engine_class):
        """Test convenience function for combined system pricing"""
        mock_engine = Mock()
        mock_result = CombinedPricingResult(combined_base_price=15000.0)
        mock_engine.calculate_combined_system_price.return_value = mock_result
        mock_engine_class.return_value = mock_engine

        system_config = {
            "pv_system": {"components": [{"product_id": 1, "quantity": 10}]},
            "heatpump_system": {"components": [{"product_id": 2, "quantity": 1}]}
        }

        result = calculate_combined_system_pricing(system_config)
        assert isinstance(result, CombinedPricingResult)
        assert result.combined_base_price == 15000.0


class TestCombinedPricingIntegration:
    """Integration tests for combined pricing"""

    @patch('pricing.combined_pricing_engine.PVPricingEngine')
    @patch('pricing.combined_pricing_engine.EnhancedHeatPumpPricingEngine')
    def test_full_combined_pricing_workflow(
            self, mock_hp_engine_class, mock_pv_engine_class):
        """Test complete combined pricing workflow"""
        # Set up mock engines
        mock_pv_engine = Mock()
        mock_hp_engine = Mock()
        mock_pv_engine_class.return_value = mock_pv_engine
        mock_hp_engine_class.return_value = mock_hp_engine

        # Mock results
        pv_result = PricingResult(
            base_price=10000.0,
            components=[],
            dynamic_keys={"PV_TOTAL_CAPACITY_KWP": 10.0},
            metadata={}
        )
        hp_result = PricingResult(
            base_price=8000.0,
            components=[],
            dynamic_keys={"HP_TOTAL_HEATING_CAPACITY_KW": 8.0},
            metadata={}
        )

        mock_pv_engine.calculate_pv_system_price.return_value = pv_result
        mock_hp_engine.calculate_heatpump_system_price.return_value = hp_result
        mock_hp_engine.calculate_beg_subsidy_integration.return_value = {
            "integration_successful": True,
            "beg_calculation": {"subsidy_amount_net": 4000.0}
        }

        # Create engine and calculate
        engine = CombinedPricingEngine()
        engine.pv_engine = mock_pv_engine
        engine.heatpump_engine = mock_hp_engine

        system_config = {
            "pv_system": {
                "components": [{"product_id": 1, "quantity": 25}],
                "system_specs": {"total_capacity_kwp": 10.0}
            },
            "heatpump_system": {
                "components": [{"product_id": 2, "quantity": 1}],
                "system_specs": {"heating_demand_kw": 8.0}
            },
            "combined_specs": {
                "synergy_discount_percent": 5.0,
                "energy_management_system": True
            }
        }

        # Calculate combined pricing
        result = engine.calculate_combined_system_price(system_config)

        # Verify complete workflow
        assert result.combined_base_price == 18000.0  # 10000 + 8000
        assert result.system_synergy_discount > 0
        assert result.combined_final_price < result.combined_base_price
        assert "COMBINED_BASE_PRICE" in result.combined_dynamic_keys
        assert "COMBINED_PV_CAPACITY_KWP" in result.combined_dynamic_keys
        assert "COMBINED_HP_CAPACITY_KW" in result.combined_dynamic_keys

        # Test financing
        financing_config = {
            "down_payment": 5000.0,
            "interest_rate_percent": 3.5,
            "loan_term_years": 15
        }
        financing_result = engine.calculate_combined_financing(
            result, financing_config)
        assert financing_result["financing_required"] is True

        # Test subsidies
        subsidy_config = {
            "beg_subsidies": {"natural_refrigerant": True},
            "combined_system_bonus": {"bonus_rate_percent": 2.0}
        }
        subsidy_result = engine.calculate_combined_subsidies(
            result, subsidy_config)
        assert subsidy_result["total_subsidies"] > 0


if __name__ == "__main__":
    pytest.main([__file__])
