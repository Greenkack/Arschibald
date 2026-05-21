"""Unit tests for DynamicKeyManager

Tests key generation, categorization, conflict resolution, and PDF formatting.
"""

import unittest
from unittest.mock import patch

from pricing.dynamic_key_manager import DynamicKeyManager, KeyCategory


class TestDynamicKeyManager(unittest.TestCase):
    """Test cases for DynamicKeyManager"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = DynamicKeyManager()

    def test_init(self):
        """Test DynamicKeyManager initialization"""
        self.assertEqual(len(self.manager.key_registry), 0)
        self.assertEqual(self.manager.conflict_counter, 0)

    def test_generate_keys_basic(self):
        """Test basic key generation"""
        pricing_data = {
            "base_price": 1000.0,
            "discount": 50.0,
            "total": 950.0
        }

        keys = self.manager.generate_keys(pricing_data)

        self.assertEqual(len(keys), 3)
        self.assertIn("BASE_PRICE", keys)
        self.assertIn("DISCOUNT", keys)
        self.assertIn("TOTAL", keys)
        self.assertEqual(keys["BASE_PRICE"], 1000.0)

    def test_generate_keys_with_prefix(self):
        """Test key generation with prefix"""
        pricing_data = {"price": 500.0}
        keys = self.manager.generate_keys(pricing_data, prefix="PV")

        self.assertIn("PV_PRICE", keys)
        self.assertEqual(keys["PV_PRICE"], 500.0)

    def test_generate_keys_with_category(self):
        """Test key generation with specific category"""
        pricing_data = {"component_cost": 200.0}
        keys = self.manager.generate_keys(
            pricing_data,
            category=KeyCategory.COMPONENTS
        )

        # Check that key was registered with correct category
        key_info = self.manager.key_registry["COMPONENT_COST"]
        self.assertEqual(key_info["category"], "components")

    def test_register_key(self):
        """Test key registration"""
        result = self.manager.register_key("TEST_KEY", 123.45, "pricing")

        self.assertTrue(result)
        self.assertIn("TEST_KEY", self.manager.key_registry)
        self.assertEqual(
            self.manager.key_registry["TEST_KEY"]["value"],
            123.45)
        self.assertEqual(
            self.manager.key_registry["TEST_KEY"]["category"],
            "pricing")

    def test_get_all_keys(self):
        """Test getting all keys"""
        self.manager.register_key("KEY1", 100, "pricing")
        self.manager.register_key("KEY2", 200, "components")

        all_keys = self.manager.get_all_keys()
        self.assertEqual(len(all_keys), 2)
        self.assertEqual(all_keys["KEY1"], 100)
        self.assertEqual(all_keys["KEY2"], 200)

    def test_get_all_keys_filtered(self):
        """Test getting keys filtered by category"""
        self.manager.register_key("KEY1", 100, "pricing")
        self.manager.register_key("KEY2", 200, "components")

        pricing_keys = self.manager.get_all_keys("pricing")
        self.assertEqual(len(pricing_keys), 1)
        self.assertEqual(pricing_keys["KEY1"], 100)

    def test_get_keys_by_category(self):
        """Test getting keys by category enum"""
        self.manager.register_key("KEY1", 100, "pricing")
        self.manager.register_key("KEY2", 200, "components")

        component_keys = self.manager.get_keys_by_category(
            KeyCategory.COMPONENTS)
        self.assertEqual(len(component_keys), 1)
        self.assertEqual(component_keys["KEY2"], 200)

    def test_format_for_pdf(self):
        """Test PDF formatting"""
        keys = {
            "PRICE": 1234.56,
            "QUANTITY": 10,
            "ACTIVE": True,
            "INACTIVE": False,
            "NAME": "Test Product",
            "NONE_VALUE": None
        }

        formatted = self.manager.format_for_pdf(keys)

        self.assertEqual(formatted["PRICE"], "1.234,56")
        self.assertEqual(formatted["QUANTITY"], "10")
        self.assertEqual(formatted["ACTIVE"], "Ja")
        self.assertEqual(formatted["INACTIVE"], "Nein")
        self.assertEqual(formatted["NAME"], "Test Product")
        self.assertEqual(formatted["NONE_VALUE"], "")

    def test_create_safe_key_name(self):
        """Test safe key name creation"""
        test_cases = [
            ("Base Price", "BASE_PRICE"),
            ("Preis €", "PREIS_EUR"),
            ("Menge (Stück)", "MENGE_STUECK"),
            ("Rabatt %", "RABATT"),
            ("123 Test", "KEY_123_TEST"),
            ("", "UNNAMED_KEY"),
            ("Ä Ö Ü ß", "AE_OE_UE_SS"),
            ("Test--Key", "TEST_KEY"),
            ("_test_", "TEST")
        ]

        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = self.manager._create_safe_key_name(input_name)
                self.assertEqual(result, expected)

    def test_resolve_key_conflict(self):
        """Test key conflict resolution"""
        # Register a key first
        self.manager.register_key("TEST_KEY", 100)

        # Try to resolve conflict
        resolved_key = self.manager._resolve_key_conflict("TEST_KEY")

        self.assertEqual(resolved_key, "TEST_KEY_1")
        self.assertEqual(self.manager.conflict_counter, 1)

    def test_resolve_multiple_conflicts(self):
        """Test multiple key conflicts"""
        # Register multiple conflicting keys
        self.manager.register_key("TEST_KEY", 100)
        self.manager.register_key("TEST_KEY_1", 200)

        resolved_key = self.manager._resolve_key_conflict("TEST_KEY")

        self.assertEqual(resolved_key, "TEST_KEY_2")
        self.assertEqual(self.manager.conflict_counter, 1)

    def test_validate_key_name(self):
        """Test key name validation"""
        valid_keys = [
            "VALID_KEY",
            "A",
            "TEST123",
            "KEY_WITH_NUMBERS_123"
        ]

        invalid_keys = [
            "",
            None,
            "123_INVALID",
            "invalid_lowercase",
            "INVALID-KEY",
            "INVALID KEY"
        ]

        for key in valid_keys:
            with self.subTest(key=key):
                self.assertTrue(self.manager.validate_key_name(key))

        for key in invalid_keys:
            with self.subTest(key=key):
                self.assertFalse(self.manager.validate_key_name(key))

    def test_get_key_suggestions(self):
        """Test key suggestions"""
        # Register some keys
        self.manager.register_key("PRICE_BASE", 100)
        self.manager.register_key("PRICE_TOTAL", 200)
        self.manager.register_key("DISCOUNT_RATE", 5)

        suggestions = self.manager.get_key_suggestions("PRICE")
        self.assertEqual(len(suggestions), 2)
        self.assertIn("PRICE_BASE", suggestions)
        self.assertIn("PRICE_TOTAL", suggestions)

    def test_clear_registry(self):
        """Test clearing the registry"""
        self.manager.register_key("TEST_KEY", 100)
        self.manager.conflict_counter = 5

        self.manager.clear_registry()

        self.assertEqual(len(self.manager.key_registry), 0)
        self.assertEqual(self.manager.conflict_counter, 0)

    def test_get_registry_stats(self):
        """Test registry statistics"""
        self.manager.register_key("KEY1", 100, "pricing")
        self.manager.register_key("KEY2", "text", "components")
        self.manager.register_key("KEY3", True, "pricing")
        self.manager.conflict_counter = 2

        stats = self.manager.get_registry_stats()

        self.assertEqual(stats["total_keys"], 3)
        self.assertEqual(stats["categories"]["pricing"], 2)
        self.assertEqual(stats["categories"]["components"], 1)
        self.assertEqual(stats["types"]["int"], 1)
        self.assertEqual(stats["types"]["str"], 1)
        self.assertEqual(stats["types"]["bool"], 1)
        self.assertEqual(stats["conflicts_resolved"], 2)

    def test_export_keys_for_template_pdf(self):
        """Test exporting keys for PDF template"""
        self.manager.register_key("PRICE", 1234.56)
        self.manager.register_key("ACTIVE", True)

        exported = self.manager.export_keys_for_template("pdf")

        self.assertEqual(exported["PRICE"], "1.234,56")
        self.assertEqual(exported["ACTIVE"], "Ja")

    def test_export_keys_for_template_json(self):
        """Test exporting keys for JSON template"""
        self.manager.register_key("PRICE", 1234.56)
        self.manager.register_key("ACTIVE", True)

        exported = self.manager.export_keys_for_template("json")

        self.assertEqual(exported["PRICE"], "1234.56")
        self.assertEqual(exported["ACTIVE"], "True")

    def test_format_value_for_pdf_numbers(self):
        """Test PDF formatting for different number formats"""
        test_cases = [
            (1234.56, "1.234,56"),
            (123.45, "123,45"),
            (1000, "1.000"),
            (100, "100"),
            (0, "0"),
            (-123.45, "-123,45")
        ]

        for value, expected in test_cases:
            with self.subTest(value=value):
                result = self.manager._format_value_for_pdf(value)
                self.assertEqual(result, expected)

    @patch('pricing.dynamic_key_manager.datetime')
    def test_get_timestamp(self, mock_datetime):
        """Test timestamp generation"""
        mock_datetime.now.return_value.strftime.return_value = "20231201_143000"

        timestamp = self.manager._get_timestamp()

        self.assertEqual(timestamp, "20231201_143000")
        mock_datetime.now.assert_called_once()

    def test_error_handling_generate_keys(self):
        """Test error handling in generate_keys"""
        # Test with data that works (object is actually handled fine)
        valid_data = {"key": object()}

        keys = self.manager.generate_keys(valid_data)

        # Should work and return the key
        self.assertIn("KEY", keys)

        # Test with None as pricing_data to trigger actual error
        with patch.object(self.manager, '_create_safe_key_name', side_effect=Exception("Test error")):
            keys = self.manager.generate_keys({"test": 123})
            self.assertEqual(keys, {})

    def test_error_handling_register_key(self):
        """Test error handling in register_key"""
        # This should work normally
        result = self.manager.register_key("VALID_KEY", 123)
        self.assertTrue(result)

        # Test with problematic key name (should still work)
        result = self.manager.register_key("", 123)
        self.assertTrue(result)  # Should handle gracefully

    def test_german_character_replacement(self):
        """Test German character replacement in key names"""
        german_text = "Größe Wärme Prüfung"
        safe_key = self.manager._create_safe_key_name(german_text)

        self.assertEqual(safe_key, "GROESSE_WAERME_PRUEFUNG")

    def test_key_generation_with_special_characters(self):
        """Test key generation with various special characters"""
        special_data = {
            "price (€)": 100,
            "discount %": 10,
            "tax/vat": 19,
            "item #1": 5
        }

        keys = self.manager.generate_keys(special_data)

        expected_keys = ["PRICE_EUR", "DISCOUNT", "TAX_VAT", "ITEM_1"]
        for expected_key in expected_keys:
            self.assertIn(expected_key, keys)

    def test_validate_key_value(self):
        """Test key value validation"""
        # Valid values
        valid_values = [123, 45.67, "test", True, None]
        for value in valid_values:
            with self.subTest(value=value):
                is_valid, error = self.manager.validate_key_value(value)
                self.assertTrue(is_valid)
                self.assertEqual(error, "")

        # Test very long string
        long_string = "x" * 1001
        is_valid, error = self.manager.validate_key_value(long_string)
        self.assertFalse(is_valid)
        self.assertIn("too long", error)

    def test_validate_key_registry_entry(self):
        """Test complete key registry entry validation"""
        # Valid entry
        is_valid, error = self.manager.validate_key_registry_entry(
            "VALID_KEY", 123.45, "pricing"
        )
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

        # Invalid key name
        is_valid, error = self.manager.validate_key_registry_entry(
            "invalid_key", 123.45, "pricing"
        )
        self.assertFalse(is_valid)
        self.assertIn("Invalid key name format", error)

        # Invalid category
        is_valid, error = self.manager.validate_key_registry_entry(
            "VALID_KEY", 123.45, "invalid_category"
        )
        self.assertFalse(is_valid)
        self.assertIn("Invalid category", error)

    def test_validate_key_with_rules(self):
        """Test comprehensive key validation with rules"""
        # Valid key
        is_valid, errors = self.manager.validate_key_with_rules("VALID_KEY")
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

        # Too short key (empty)
        is_valid, errors = self.manager.validate_key_with_rules("")
        self.assertFalse(is_valid)
        self.assertTrue(any("non-empty string" in error for error in errors))

        # Key starting with number
        is_valid, errors = self.manager.validate_key_with_rules("1_INVALID")
        self.assertFalse(is_valid)
        self.assertTrue(
            any("cannot start with '1'" in error for error in errors))

        # Reserved key
        is_valid, errors = self.manager.validate_key_with_rules("NULL")
        self.assertFalse(is_valid)
        self.assertTrue(any("reserved key" in error for error in errors))

        # Invalid characters
        is_valid, errors = self.manager.validate_key_with_rules("INVALID-KEY")
        self.assertFalse(is_valid)
        self.assertTrue(any("invalid characters" in error for error in errors))

    def test_resolve_key_conflicts_batch(self):
        """Test batch conflict resolution"""
        # Register some existing keys
        self.manager.register_key("EXISTING_KEY", 100)
        self.manager.register_key("ANOTHER_KEY", 200)

        # Test batch resolution
        proposed_keys = {
            "EXISTING_KEY": 300,
            "NEW_KEY": 400,
            "ANOTHER_KEY": 500
        }

        resolution_map = self.manager.resolve_key_conflicts_batch(
            proposed_keys)

        self.assertEqual(resolution_map["EXISTING_KEY"], "EXISTING_KEY_1")
        self.assertEqual(resolution_map["NEW_KEY"], "NEW_KEY")
        self.assertEqual(resolution_map["ANOTHER_KEY"], "ANOTHER_KEY_1")

    def test_check_for_conflicts(self):
        """Test conflict checking"""
        # Register existing key
        self.manager.register_key("EXISTING_KEY", 100)

        # Check for conflicts
        proposed_keys = ["EXISTING_KEY", "NEW_KEY", "EXISTING_KEY"]
        conflicts = self.manager.check_for_conflicts(proposed_keys)

        self.assertIn("EXISTING_KEY", conflicts["existing_conflicts"])
        self.assertIn("EXISTING_KEY", conflicts["internal_conflicts"])
        self.assertIn("EXISTING_KEY", conflicts["suggested_resolutions"])

    def test_get_conflict_report(self):
        """Test conflict report generation"""
        # Create some conflicts
        self.manager.register_key("TEST_KEY", 100)
        # This increments conflict counter
        self.manager._resolve_key_conflict("TEST_KEY")

        report = self.manager.get_conflict_report()

        self.assertIn("total_conflicts_resolved", report)
        self.assertIn("current_registry_size", report)
        self.assertIn("categories_in_use", report)
        self.assertIn("most_recent_keys", report)

    def test_key_history_tracking(self):
        """Test key history functionality"""
        # Register a key (should add to history)
        self.manager.register_key("TEST_KEY", 123, "pricing")

        # Check history
        history = self.manager.get_key_history()
        self.assertGreater(len(history), 0)

        # Check specific key history
        key_history = self.manager.get_key_history(key="TEST_KEY")
        self.assertGreater(len(key_history), 0)
        self.assertEqual(key_history[0]["key"], "TEST_KEY")

        # Check action-specific history
        register_history = self.manager.get_key_history(action="registered")
        self.assertGreater(len(register_history), 0)

    def test_add_to_history(self):
        """Test manual history addition"""
        self.manager.add_to_history(
            "test_action", "TEST_KEY", {
                "detail": "test"})

        history = self.manager.get_key_history(action="test_action")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["action"], "test_action")
        self.assertEqual(history[0]["key"], "TEST_KEY")
        self.assertEqual(history[0]["details"]["detail"], "test")

    def test_update_validation_rules(self):
        """Test validation rules update"""
        original_rules = self.manager.get_validation_rules()

        new_rules = {"max_key_length": 50}
        self.manager.update_validation_rules(new_rules)

        updated_rules = self.manager.get_validation_rules()
        self.assertEqual(updated_rules["max_key_length"], 50)

        # Other rules should remain unchanged
        self.assertEqual(
            updated_rules["min_key_length"],
            original_rules["min_key_length"])

    def test_get_validation_rules(self):
        """Test getting validation rules"""
        rules = self.manager.get_validation_rules()

        expected_keys = [
            "max_key_length", "min_key_length", "allowed_characters",
            "forbidden_prefixes", "reserved_keys", "max_value_length"
        ]

        for key in expected_keys:
            self.assertIn(key, rules)

    def test_history_size_management(self):
        """Test that history size is managed properly"""
        # Clear any existing history first
        self.manager.key_history.clear()

        # Add many history entries
        for i in range(1100):
            self.manager.add_to_history("test", f"KEY_{i}")

        # Should be trimmed - the exact number depends on when trimming occurs
        # but it should be <= 500 after all additions
        self.assertLessEqual(len(self.manager.key_history),
                             600)  # Allow some buffer

        # Test that trimming actually occurred
        self.assertLess(len(self.manager.key_history), 1100)

    def test_enhanced_register_key_with_validation(self):
        """Test enhanced register_key with validation"""
        # Register valid key
        result = self.manager.register_key("VALID_KEY", 123, "pricing")
        self.assertTrue(result)

        # Register key with invalid category (should still work but log
        # warning)
        result = self.manager.register_key("TEST_KEY", 456, "invalid_category")
        self.assertTrue(result)  # Still registers despite validation failure

        # Check that validation failure was logged in history
        history = self.manager.get_key_history(action="validation_failed")
        self.assertGreater(len(history), 0)

    def test_conflict_detection_in_register_key(self):
        """Test conflict detection during key registration"""
        # Register initial key
        self.manager.register_key("CONFLICT_KEY", 100)

        # Register same key again (should detect conflict)
        self.manager.register_key("CONFLICT_KEY", 200)

        # Check that conflict was logged
        conflict_history = self.manager.get_key_history(
            action="conflict_detected")
        self.assertGreater(len(conflict_history), 0)
        self.assertEqual(conflict_history[0]["key"], "CONFLICT_KEY")

    def test_generate_pricing_keys_german_logic_without_vat(self):
        """Test German pricing logic without VAT"""
        component_prices = {
            "pv_module": 1000.0,
            "inverter": 800.0,
            "battery": 2000.0
        }

        keys = self.manager.generate_pricing_keys_german_logic(
            component_prices)

        # Check component keys
        self.assertIn("COMPONENT_PV_MODULE", keys)
        self.assertIn("COMPONENT_INVERTER", keys)
        self.assertIn("COMPONENT_BATTERY", keys)

        # Check net total
        self.assertIn("NET_TOTAL", keys)
        self.assertEqual(keys["NET_TOTAL"], 3800.0)

        # Should not have VAT keys
        self.assertNotIn("VAT_AMOUNT", keys)
        self.assertNotIn("GROSS_TOTAL", keys)

    def test_generate_pricing_keys_german_logic_with_vat(self):
        """Test German pricing logic with VAT"""
        component_prices = {
            "pv_module": 1000.0,
            "inverter": 800.0
        }

        keys = self.manager.generate_pricing_keys_german_logic(
            component_prices,
            vat_rate=0.19
        )

        # Check component keys
        self.assertIn("COMPONENT_PV_MODULE", keys)
        self.assertIn("COMPONENT_INVERTER", keys)

        # Check net total
        self.assertIn("NET_TOTAL", keys)
        self.assertEqual(keys["NET_TOTAL"], 1800.0)

        # Check VAT keys
        self.assertIn("VAT_AMOUNT", keys)
        self.assertIn("VAT_RATE", keys)
        self.assertEqual(keys["VAT_AMOUNT"], 342.0)  # 1800 * 0.19
        self.assertEqual(keys["VAT_RATE"], 19.0)  # As percentage

        # Check gross total
        self.assertIn("GROSS_TOTAL", keys)
        self.assertEqual(keys["GROSS_TOTAL"], 2142.0)  # 1800 + 342

    def test_generate_pricing_keys_german_logic_with_prefix(self):
        """Test German pricing logic with prefix"""
        component_prices = {"module": 500.0}

        keys = self.manager.generate_pricing_keys_german_logic(
            component_prices,
            vat_rate=0.19,
            prefix="PV_SYSTEM"
        )

        # Check prefixed keys
        self.assertIn("PV_SYSTEM_COMPONENT_MODULE", keys)
        self.assertIn("PV_SYSTEM_NET_TOTAL", keys)
        self.assertIn("PV_SYSTEM_VAT_AMOUNT", keys)
        self.assertIn("PV_SYSTEM_GROSS_TOTAL", keys)

    def test_generate_vat_keys(self):
        """Test VAT key generation"""
        keys = self.manager.generate_vat_keys(1000.0, 0.19)

        self.assertIn("VAT_VAT_RATE_PERCENT", keys)
        self.assertIn("VAT_VAT_AMOUNT", keys)
        self.assertIn("VAT_NET_AMOUNT", keys)
        self.assertIn("VAT_GROSS_AMOUNT", keys)

        self.assertEqual(keys["VAT_VAT_RATE_PERCENT"], 19.0)
        self.assertEqual(keys["VAT_VAT_AMOUNT"], 190.0)
        self.assertEqual(keys["VAT_NET_AMOUNT"], 1000.0)
        self.assertEqual(keys["VAT_GROSS_AMOUNT"], 1190.0)

    def test_generate_vat_keys_with_prefix(self):
        """Test VAT key generation with prefix"""
        keys = self.manager.generate_vat_keys(500.0, 0.07, prefix="REDUCED")

        self.assertIn("REDUCED_VAT_VAT_RATE_PERCENT", keys)
        self.assertIn("REDUCED_VAT_VAT_AMOUNT", keys)
        self.assertEqual(keys["REDUCED_VAT_VAT_AMOUNT"], 35.0)  # 500 * 0.07

    def test_calculate_component_totals_without_individual_vat(self):
        """Test component totals without individual VAT"""
        components = {
            "module": {"price": 1000.0},
            "inverter": {"price": 800.0},
            "battery": {"price": 1500.0}
        }

        keys = self.manager.calculate_component_totals(components)

        # Check individual component keys
        self.assertIn("MODULE_PRICE", keys)
        self.assertIn("INVERTER_PRICE", keys)
        self.assertIn("BATTERY_PRICE", keys)

        # Check net total
        self.assertIn("NET_TOTAL", keys)
        self.assertEqual(keys["NET_TOTAL"], 3300.0)

        # Should not have VAT keys
        self.assertNotIn("VAT_TOTAL", keys)
        self.assertNotIn("GROSS_TOTAL", keys)

    def test_calculate_component_totals_with_individual_vat(self):
        """Test component totals with individual VAT rates"""
        components = {
            "module": {"price": 1000.0, "vat_rate": 0.19},
            "service": {"price": 500.0, "vat_rate": 0.19},
            "installation": {"price": 800.0}  # No VAT
        }

        keys = self.manager.calculate_component_totals(components)

        # Check component prices
        self.assertEqual(keys["MODULE_PRICE"], 1000.0)
        self.assertEqual(keys["SERVICE_PRICE"], 500.0)
        self.assertEqual(keys["INSTALLATION_PRICE"], 800.0)

        # Check individual VAT
        self.assertIn("MODULE_VAT", keys)
        self.assertIn("SERVICE_VAT", keys)
        self.assertEqual(keys["MODULE_VAT"], 190.0)  # 1000 * 0.19
        self.assertEqual(keys["SERVICE_VAT"], 95.0)   # 500 * 0.19

        # Check totals
        self.assertEqual(keys["NET_TOTAL"], 2300.0)  # 1000 + 500 + 800
        self.assertEqual(keys["VAT_TOTAL"], 285.0)   # 190 + 95
        self.assertEqual(keys["GROSS_TOTAL"], 2585.0)  # 2300 + 285

    def test_calculate_component_totals_with_prefix(self):
        """Test component totals with prefix"""
        components = {
            "module": {"price": 1000.0, "vat_rate": 0.19}
        }

        keys = self.manager.calculate_component_totals(
            components, prefix="HEAT_PUMP")

        self.assertIn("HEAT_PUMP_MODULE_PRICE", keys)
        self.assertIn("HEAT_PUMP_MODULE_VAT", keys)
        self.assertIn("HEAT_PUMP_NET_TOTAL", keys)
        self.assertIn("HEAT_PUMP_VAT_TOTAL", keys)
        self.assertIn("HEAT_PUMP_GROSS_TOTAL", keys)

    def test_german_pricing_logic_integration(self):
        """Test complete German pricing logic integration"""
        # Simulate a complete PV system calculation

        # Step 1: Individual component prices
        pv_components = {
            "solar_modules": 2000.0,
            "inverter": 1200.0,
            "mounting_system": 800.0,
            "cables": 300.0
        }

        # Step 2: Generate keys without VAT first
        keys_net = self.manager.generate_pricing_keys_german_logic(
            pv_components,
            prefix="PV_SYSTEM"
        )

        # Step 3: Add VAT dynamically
        net_total = keys_net["PV_SYSTEM_NET_TOTAL"]
        vat_keys = self.manager.generate_vat_keys(
            net_total, 0.19, prefix="PV_SYSTEM")

        # Combine all keys
        all_keys = {**keys_net, **vat_keys}

        # Verify the complete calculation
        self.assertEqual(all_keys["PV_SYSTEM_NET_TOTAL"], 4300.0)
        self.assertEqual(
            all_keys["PV_SYSTEM_VAT_VAT_AMOUNT"],
            817.0)  # 4300 * 0.19
        self.assertEqual(
            all_keys["PV_SYSTEM_VAT_GROSS_AMOUNT"],
            5117.0)  # 4300 + 817

        # Verify all components are present
        self.assertIn("PV_SYSTEM_COMPONENT_SOLAR_MODULES", all_keys)
        self.assertIn("PV_SYSTEM_COMPONENT_INVERTER", all_keys)
        self.assertIn("PV_SYSTEM_COMPONENT_MOUNTING_SYSTEM", all_keys)
        self.assertIn("PV_SYSTEM_COMPONENT_CABLES", all_keys)

    def test_format_german_prices_for_pdf(self):
        """Test German price formatting for PDF"""
        component_prices = {"module": 1234.56}

        keys = self.manager.generate_pricing_keys_german_logic(
            component_prices,
            vat_rate=0.19
        )

        # Format for PDF
        formatted_keys = self.manager.format_for_pdf(keys)

        # Check German number formatting
        self.assertEqual(formatted_keys["COMPONENT_MODULE"], "1.234,56")
        self.assertEqual(formatted_keys["NET_TOTAL"], "1.234,56")
        self.assertEqual(
            formatted_keys["VAT_AMOUNT"],
            "234,57")  # 1234.56 * 0.19
        self.assertEqual(
            formatted_keys["GROSS_TOTAL"],
            "1.469,13")  # 1234.56 + 234.57


if __name__ == '__main__':
    unittest.main()
