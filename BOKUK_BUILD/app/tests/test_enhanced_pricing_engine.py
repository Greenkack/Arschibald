"""Unit tests for Enhanced Pricing Engine

Tests core pricing calculations using comprehensive product data
with all existing product fields and calculate_per methods.
"""

from pricing.enhanced_pricing_engine import (
    FinalPricingResult,
    PriceComponent,
    PricingEngine,
    PricingResult,
)
from pricing.dynamic_key_manager import DynamicKeyManager, KeyCategory
import os
import sys
import unittest
from unittest.mock import patch

# Add the project root to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPriceComponent(unittest.TestCase):
    """Test PriceComponent class with comprehensive product data"""

    def setUp(self):
        """Set up test data"""
        self.sample_product_data = {
            "id": 1,
            "category": "Modul",
            "model_name": "AlphaSolar 450W",
            "brand": "AlphaSolar",
            "price_euro": 180.0,
            "calculate_per": "Stück",
            "capacity_w": 450.0,
            "storage_power_kw": None,
            "power_kw": None,
            "max_cycles": None,
            "warranty_years": 25,
            "technology": "Monokristallin N-Type",
            "feature": "Bifacial",
            "design": "All-Black",
            "upgrade": "Premium",
            "max_kwh_capacity": None,
            "outdoor_opt": True,
            "self_supply_feature": False,
            "shadow_fading": True,
            "smart_home": False,
            "length_m": 2.1,
            "width_m": 1.05,
            "weight_kg": 22.5,
            "efficiency_percent": 21.8,
            "origin_country": "Deutschland",
            "description": "Hocheffizientes PV-Modul",
            "pros": "Hohe Effizienz, lange Garantie",
            "cons": "Höherer Preis",
            "rating": 4.8
        }

    def test_price_component_creation_per_piece(self):
        """Test creating price component with per-piece calculation"""
        comp = PriceComponent(
            product_id=1,
            model_name="AlphaSolar 450W",
            category="Modul",
            brand="AlphaSolar",
            quantity=20,
            price_euro=180.0,
            calculate_per="Stück",
            capacity_w=450.0,
            warranty_years=25,
            technology="Monokristallin N-Type",
            efficiency_percent=21.8
        )

        self.assertEqual(comp.unit_price, 180.0)
        self.assertEqual(comp.total_price, 3600.0)  # 20 * 180
        self.assertIn("ALPHASOLAR_450W_UNIT_PRICE", comp.dynamic_keys)
        self.assertIn("ALPHASOLAR_450W_TOTAL_PRICE", comp.dynamic_keys)
        self.assertEqual(comp.dynamic_keys["ALPHASOLAR_450W_QUANTITY"], 20)

    def test_price_component_creation_per_meter(self):
        """Test creating price component with per-meter calculation"""
        comp = PriceComponent(
            product_id=2,
            model_name="Solar Cable 6mm²",
            category="Kabel",
            brand="CableTech",
            quantity=50,  # 50 meters
            price_euro=2.5,  # per meter
            calculate_per="Meter",
            length_m=1.0,  # per meter
            weight_kg=0.1   # per meter
        )

        self.assertEqual(comp.unit_price, 2.5)
        self.assertEqual(comp.total_price, 125.0)  # 50 * 2.5
        self.assertEqual(
            comp.dynamic_keys["SOLAR_CABLE_6MM_CALCULATE_PER"],
            "Meter")

    def test_price_component_creation_lump_sum(self):
        """Test creating price component with lump sum calculation"""
        comp = PriceComponent(
            product_id=3,
            model_name="Installation Service",
            category="Dienstleistung",
            brand="ServiceCorp",
            quantity=1,
            price_euro=1500.0,
            calculate_per="pauschal"
        )

        self.assertEqual(comp.unit_price, 1500.0)
        # Lump sum regardless of quantity
        self.assertEqual(comp.total_price, 1500.0)

    def test_price_component_creation_per_kwp(self):
        """Test creating price component with per-kWp calculation"""
        comp = PriceComponent(
            product_id=4,
            model_name="Mounting System",
            category="Montagesystem",
            brand="MountTech",
            quantity=9,  # 9 kWp system
            price_euro=50.0,  # base price
            calculate_per="kWp",
            capacity_w=1000.0  # 1 kWp reference
        )

        self.assertEqual(comp.unit_price, 50.0)  # 50 * (1000W / 1000W)
        self.assertEqual(comp.total_price, 450.0)  # 9 * 50

    def test_dynamic_keys_generation(self):
        """Test dynamic key generation for components"""
        comp = PriceComponent(
            product_id=1,
            model_name="Test Module 400W",
            category="Modul",
            brand="TestBrand",
            quantity=10,
            price_euro=200.0,
            technology="PERC",
            efficiency_percent=20.5,
            warranty_years=20
        )

        keys = comp.dynamic_keys

        # Check required keys
        self.assertIn("TEST_MODULE_400W_UNIT_PRICE", keys)
        self.assertIn("TEST_MODULE_400W_TOTAL_PRICE", keys)
        self.assertIn("TEST_MODULE_400W_QUANTITY", keys)
        self.assertIn("TEST_MODULE_400W_CATEGORY", keys)
        self.assertIn("TEST_MODULE_400W_BRAND", keys)

        # Check technical specification keys
        self.assertIn("TEST_MODULE_400W_TECHNOLOGY", keys)
        self.assertIn("TEST_MODULE_400W_EFFICIENCY_PCT", keys)
        self.assertIn("TEST_MODULE_400W_WARRANTY_YEARS", keys)

        # Check values
        self.assertEqual(keys["TEST_MODULE_400W_UNIT_PRICE"], 200.0)
        self.assertEqual(keys["TEST_MODULE_400W_TOTAL_PRICE"], 2000.0)
        self.assertEqual(keys["TEST_MODULE_400W_TECHNOLOGY"], "PERC")


class TestPricingEngine(unittest.TestCase):
    """Test PricingEngine class"""

    def setUp(self):
        """Set up test data"""
        self.engine = PricingEngine(
            "pv", enable_caching=False)  # Disable caching for consistent tests

        # Mock product database responses
        self.mock_products = {
            1: {
                "id": 1,
                "category": "Modul",
                "model_name": "AlphaSolar 450W",
                "brand": "AlphaSolar",
                "price_euro": 180.0,
                "calculate_per": "Stück",
                "capacity_w": 450.0,
                "warranty_years": 25,
                "technology": "Monokristallin",
                "efficiency_percent": 21.8
            },
            2: {
                "id": 2,
                "category": "Wechselrichter",
                "model_name": "PowerMax 5K",
                "brand": "InvertCorp",
                "price_euro": 800.0,
                "calculate_per": "Stück",
                "power_kw": 5.0,
                "warranty_years": 10,
                "technology": "String",
                "efficiency_percent": 97.5
            },
            3: {
                "id": 3,
                "category": "Batteriespeicher",
                "model_name": "EnergyCell 10kWh",
                "brand": "StoreIt",
                "price_euro": 3500.0,
                "calculate_per": "Stück",
                "storage_power_kw": 10.0,
                "max_cycles": 6000,
                "warranty_years": 15,
                "technology": "LiFePO4"
            }
        }

    @patch('pricing.enhanced_pricing_engine.get_product_by_id')
    def test_calculate_base_price_simple(self, mock_get_product):
        """Test basic price calculation with simple components"""
        # Mock database calls
        mock_get_product.side_effect = lambda pid: self.mock_products.get(pid)

        components = [
            {"product_id": 1, "quantity": 20},  # 20 modules
            {"product_id": 2, "quantity": 1},   # 1 inverter
        ]

        result = self.engine.calculate_base_price(components)

        self.assertIsInstance(result, PricingResult)
        self.assertEqual(result.base_price, 4400.0)  # 20*180 + 1*800
        self.assertEqual(len(result.components), 2)
        self.assertIn("PV_BASE_PRICE_NET", result.dynamic_keys)
        self.assertEqual(result.metadata["system_type"], "pv")

    @patch('pricing.enhanced_pricing_engine.get_product_by_id')
    def test_calculate_base_price_with_storage(self, mock_get_product):
        """Test price calculation including battery storage"""
        mock_get_product.side_effect = lambda pid: self.mock_products.get(pid)

        components = [
            {"product_id": 1, "quantity": 16},  # 16 modules
            {"product_id": 2, "quantity": 1},   # 1 inverter
            {"product_id": 3, "quantity": 1},   # 1 battery
        ]

        result = self.engine.calculate_base_price(components)

        expected_price = 16 * 180.0 + 800.0 + 3500.0  # 7180.0
        self.assertEqual(result.base_price, expected_price)
        self.assertEqual(len(result.components), 3)

        # Check category totals in dynamic keys
        self.assertIn("PV_MODUL_TOTAL", result.dynamic_keys)
        self.assertIn("PV_WECHSELRICHTER_TOTAL", result.dynamic_keys)
        self.assertIn("PV_BATTERIESPEICHER_TOTAL", result.dynamic_keys)

    def test_apply_modifications_percentage_discount(self):
        """Test applying percentage-based discount"""
        base_price = 5000.0
        modifications = {
            "discount_percent": 10.0,
            "discount_fixed": 0.0,
            "surcharge_percent": 0.0,
            "surcharge_fixed": 0.0,
            "accessories_cost": 0.0
        }

        result = self.engine.apply_modifications(base_price, modifications)

        self.assertEqual(result["original_price"], 5000.0)
        self.assertEqual(result["discount_percent_amount"], 500.0)
        self.assertEqual(result["final_price"], 4500.0)
        self.assertIn("PV_DISCOUNT_PERCENT", result["dynamic_keys"])

    def test_apply_modifications_complex_formula(self):
        """Test complex pricing formula with all modifications"""
        base_price = 5000.0
        modifications = {
            "discount_percent": 5.0,      # 5% discount
            "discount_fixed": 100.0,      # 100€ fixed discount
            "surcharge_percent": 2.0,     # 2% surcharge
            "surcharge_fixed": 50.0,      # 50€ fixed surcharge
            "accessories_cost": 200.0     # 200€ accessories
        }

        result = self.engine.apply_modifications(base_price, modifications)

        # Formula: (5000 + 200) × (1 - 0.05) × (1 + 0.02) - 100 + 50
        # = 5200 × 0.95 × 1.02 - 100 + 50
        # = 5038.8 - 100 + 50 = 4988.8

        expected_price = 4988.8
        self.assertAlmostEqual(result["final_price"], expected_price, places=2)
        self.assertEqual(result["accessories_cost"], 200.0)
        self.assertEqual(result["total_discounts"], 360.0)  # 260 + 100
        self.assertAlmostEqual(
            result["total_surcharges"],
            148.8,
            places=1)  # 98.8 + 50

    @patch('pricing.enhanced_pricing_engine.get_product_by_id')
    def test_generate_final_price_complete(self, mock_get_product):
        """Test complete final price generation with VAT"""
        mock_get_product.side_effect = lambda pid: self.mock_products.get(pid)

        calculation_data = {
            "components": [
                {"product_id": 1, "quantity": 10},
                {"product_id": 2, "quantity": 1}
            ],
            "modifications": {
                "discount_percent": 5.0,
                "accessories_cost": 100.0
            },
            "vat_rate": 19.0
        }

        result = self.engine.generate_final_price(calculation_data)

        self.assertIsInstance(result, FinalPricingResult)
        self.assertEqual(result.base_price, 2600.0)  # 10*180 + 800

        # Check VAT calculation
        expected_net = (2600.0 + 100.0) * 0.95  # 2565.0
        expected_vat = expected_net * 0.19  # 487.35
        expected_gross = expected_net + expected_vat  # 3052.35

        self.assertAlmostEqual(result.final_price_net, expected_net, places=2)
        self.assertAlmostEqual(result.vat_amount, expected_vat, places=2)
        self.assertAlmostEqual(
            result.final_price_gross,
            expected_gross,
            places=2)

        # Check dynamic keys
        self.assertIn("PV_FINAL_PRICE_NET", result.dynamic_keys)
        self.assertIn("PV_VAT_AMOUNT", result.dynamic_keys)
        self.assertIn("PV_FINAL_PRICE_GROSS", result.dynamic_keys)

    def test_validate_pricing_data_valid(self):
        """Test validation of valid pricing data"""
        valid_data = {
            "components": [
                {"product_id": 1, "quantity": 10},
                {"model_name": "Test Product", "quantity": 5}
            ],
            "modifications": {
                "discount_percent": 5.0,
                "surcharge_fixed": 100.0
            }
        }

        self.assertTrue(self.engine.validate_pricing_data(valid_data))

    def test_validate_pricing_data_invalid(self):
        """Test validation of invalid pricing data"""
        # Missing components
        invalid_data1 = {"modifications": {}}
        self.assertFalse(self.engine.validate_pricing_data(invalid_data1))

        # Invalid component structure
        # Missing product identifier
        invalid_data2 = {"components": [{"quantity": 5}]}
        self.assertFalse(self.engine.validate_pricing_data(invalid_data2))

        # Invalid quantity
        invalid_data3 = {"components": [{"product_id": 1, "quantity": -5}]}
        self.assertFalse(self.engine.validate_pricing_data(invalid_data3))

        # Invalid modification type
        invalid_data4 = {
            "components": [{"product_id": 1, "quantity": 1}],
            "modifications": {"discount_percent": "invalid"}
        }
        self.assertFalse(self.engine.validate_pricing_data(invalid_data4))

    def test_system_type_validation(self):
        """Test system type validation"""
        # Valid system types
        pv_engine = PricingEngine("pv")
        self.assertEqual(pv_engine.system_type, "pv")

        hp_engine = PricingEngine("heatpump")
        self.assertEqual(hp_engine.system_type, "heatpump")

        combined_engine = PricingEngine("combined")
        self.assertEqual(combined_engine.system_type, "combined")

        # Invalid system type should raise ValueError
        with self.assertRaises(ValueError):
            PricingEngine("invalid_type")


class TestDynamicKeyManager(unittest.TestCase):
    """Test DynamicKeyManager class"""

    def setUp(self):
        """Set up test data"""
        self.key_manager = DynamicKeyManager()

    def test_generate_keys_basic(self):
        """Test basic key generation"""
        pricing_data = {
            "base_price": 1000.0,
            "discount_amount": 100.0,
            "final_price": 900.0
        }

        keys = self.key_manager.generate_keys(pricing_data, prefix="PV")

        self.assertIn("PV_BASE_PRICE", keys)
        self.assertIn("PV_DISCOUNT_AMOUNT", keys)
        self.assertIn("PV_FINAL_PRICE", keys)
        self.assertEqual(keys["PV_BASE_PRICE"], 1000.0)

    def test_create_safe_key_name(self):
        """Test safe key name creation"""
        # Test German characters
        self.assertEqual(
            self.key_manager._create_safe_key_name("Wärmepumpe Größe"),
            "WAERMEPUMPE_GROESSE"
        )

        # Test special characters
        self.assertEqual(
            self.key_manager._create_safe_key_name("Price (€/kWh)"),
            "PRICE_EUR_KWH"
        )

        # Test numbers at start
        self.assertEqual(
            self.key_manager._create_safe_key_name("5kW Inverter"),
            "KEY_5KW_INVERTER"
        )

        # Test empty string
        self.assertEqual(
            self.key_manager._create_safe_key_name(""),
            "UNNAMED_KEY"
        )

    def test_key_conflict_resolution(self):
        """Test key conflict resolution"""
        # Register a key
        self.key_manager.register_key("TEST_KEY", 100.0)

        # Try to register the same key again
        resolved_key = self.key_manager._resolve_key_conflict("TEST_KEY")
        self.assertEqual(resolved_key, "TEST_KEY_1")

        # Register the resolved key and try again
        self.key_manager.register_key("TEST_KEY_1", 200.0)
        resolved_key2 = self.key_manager._resolve_key_conflict("TEST_KEY")
        self.assertEqual(resolved_key2, "TEST_KEY_2")

    def test_format_for_pdf(self):
        """Test PDF formatting"""
        keys = {
            "PRICE": 1234.56,
            "QUANTITY": 10,
            "ENABLED": True,
            "DISABLED": False,
            "NAME": "Test Product",
            "EMPTY": None
        }

        formatted = self.key_manager.format_for_pdf(keys)

        self.assertEqual(formatted["PRICE"], "1.234,56")
        self.assertEqual(formatted["QUANTITY"], "10")
        self.assertEqual(formatted["ENABLED"], "Ja")
        self.assertEqual(formatted["DISABLED"], "Nein")
        self.assertEqual(formatted["NAME"], "Test Product")
        self.assertEqual(formatted["EMPTY"], "")

    def test_category_filtering(self):
        """Test filtering keys by category"""
        # Register keys in different categories
        self.key_manager.register_key(
            "PRICE_1", 100.0, KeyCategory.PRICING.value)
        self.key_manager.register_key(
            "COMP_1", "Module", KeyCategory.COMPONENTS.value)
        self.key_manager.register_key(
            "DISC_1", 50.0, KeyCategory.DISCOUNTS.value)

        # Test category filtering
        pricing_keys = self.key_manager.get_all_keys(KeyCategory.PRICING.value)
        self.assertIn("PRICE_1", pricing_keys)
        self.assertNotIn("COMP_1", pricing_keys)

        component_keys = self.key_manager.get_all_keys(
            KeyCategory.COMPONENTS.value)
        self.assertIn("COMP_1", component_keys)
        self.assertNotIn("PRICE_1", component_keys)

    def test_registry_stats(self):
        """Test registry statistics"""
        # Register some keys
        self.key_manager.register_key(
            "PRICE", 100.0, KeyCategory.PRICING.value)
        self.key_manager.register_key(
            "NAME", "Test", KeyCategory.COMPONENTS.value)
        self.key_manager.register_key(
            "ENABLED", True, KeyCategory.SYSTEM.value)

        stats = self.key_manager.get_registry_stats()

        self.assertEqual(stats["total_keys"], 3)
        self.assertEqual(stats["categories"][KeyCategory.PRICING.value], 1)
        self.assertEqual(stats["categories"][KeyCategory.COMPONENTS.value], 1)
        self.assertEqual(stats["types"]["float"], 1)
        self.assertEqual(stats["types"]["str"], 1)
        self.assertEqual(stats["types"]["bool"], 1)

    def test_key_validation(self):
        """Test key name validation"""
        # Valid keys
        self.assertTrue(self.key_manager.validate_key_name("VALID_KEY"))
        self.assertTrue(self.key_manager.validate_key_name("A"))
        self.assertTrue(self.key_manager.validate_key_name("KEY_123"))

        # Invalid keys
        self.assertFalse(self.key_manager.validate_key_name(""))
        self.assertFalse(self.key_manager.validate_key_name(
            "123_KEY"))  # Starts with number
        self.assertFalse(
            self.key_manager.validate_key_name("key"))      # Lowercase
        self.assertFalse(self.key_manager.validate_key_name(
            "KEY-NAME"))  # Contains dash


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete pricing system"""

    @patch('pricing.enhanced_pricing_engine.get_product_by_id')
    def test_complete_pv_system_pricing(self, mock_get_product):
        """Test complete PV system pricing with all features"""
        # Mock comprehensive product data
        mock_products = {
            1: {  # PV Module
                "id": 1, "category": "Modul", "model_name": "AlphaSolar 450W",
                "brand": "AlphaSolar", "price_euro": 180.0, "calculate_per": "Stück",
                "capacity_w": 450.0, "warranty_years": 25, "technology": "Monokristallin",
                "feature": "Bifacial", "design": "All-Black", "efficiency_percent": 21.8
            },
            2: {  # Inverter
                "id": 2, "category": "Wechselrichter", "model_name": "PowerMax 5K",
                "brand": "InvertCorp", "price_euro": 800.0, "calculate_per": "Stück",
                "power_kw": 5.0, "warranty_years": 10, "efficiency_percent": 97.5
            },
            3: {  # Mounting per kWp
                "id": 3, "category": "Montagesystem", "model_name": "RoofMount Pro",
                "brand": "MountTech", "price_euro": 80.0, "calculate_per": "kWp",
                "capacity_w": 1000.0, "warranty_years": 20
            },
            4: {  # Cable per meter
                "id": 4, "category": "Kabel", "model_name": "Solar Cable 6mm²",
                "brand": "CableTech", "price_euro": 2.5, "calculate_per": "Meter",
                "length_m": 1.0
            }
        }

        mock_get_product.side_effect = lambda pid: mock_products.get(pid)

        # Create PV pricing engine
        engine = PricingEngine("pv")

        # Define system components
        calculation_data = {
            "components": [
                {"product_id": 1, "quantity": 20},  # 20 modules = 9 kWp
                {"product_id": 2, "quantity": 1},   # 1 inverter
                {"product_id": 3, "quantity": 9},   # 9 kWp mounting
                {"product_id": 4, "quantity": 50}   # 50m cable
            ],
            "modifications": {
                "discount_percent": 5.0,
                "accessories_cost": 300.0,  # Additional accessories
                "surcharge_fixed": 100.0    # Rush order surcharge
            },
            "vat_rate": 19.0
        }

        # Calculate final price
        result = engine.generate_final_price(calculation_data)

        # Verify calculations
        expected_base = 20 * 180 + 800 + 9 * 80 + 50 * 2.5  # 4545.0
        self.assertEqual(result.base_price, expected_base)

        # Verify component types
        component_categories = [comp.category for comp in result.components]
        self.assertIn("Modul", component_categories)
        self.assertIn("Wechselrichter", component_categories)
        self.assertIn("Montagesystem", component_categories)
        self.assertIn("Kabel", component_categories)

        # Verify dynamic keys include all component types
        keys = result.dynamic_keys
        self.assertIn("ALPHASOLAR_450W_TOTAL_PRICE", keys)
        self.assertIn("POWERMAX_5K_TOTAL_PRICE", keys)
        self.assertIn("ROOFMOUNT_PRO_TOTAL_PRICE", keys)
        self.assertIn("SOLAR_CABLE_6MM_TOTAL_PRICE", keys)

        # Verify system-level keys
        self.assertIn("PV_BASE_PRICE_NET", keys)
        self.assertIn("PV_FINAL_PRICE_NET", keys)
        self.assertIn("PV_FINAL_PRICE_GROSS", keys)
        self.assertIn("PV_VAT_AMOUNT", keys)

        # Verify category totals
        self.assertIn("PV_MODUL_TOTAL", keys)
        self.assertIn("PV_WECHSELRICHTER_TOTAL", keys)

        # Verify final price is positive and reasonable
        self.assertGreater(result.final_price_net, 0)
        self.assertGreater(result.final_price_gross, result.final_price_net)
        self.assertEqual(result.metadata["system_type"], "pv")
        self.assertTrue(result.metadata["calculation_complete"])


if __name__ == '__main__':
    # Set up logging for tests
    logging.basicConfig(level=logging.DEBUG)

    # Run tests
    unittest.main(verbosity=2)
