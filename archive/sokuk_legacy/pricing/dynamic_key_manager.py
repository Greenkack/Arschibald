"""Dynamic Key Manager

Manages dynamic key generation and PDF integration for the enhanced pricing system.
Provides consistent key naming, categorization, and PDF-ready formatting.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class KeyCategory(Enum):
    """Categories for organizing dynamic keys"""
    PRICING = "pricing"
    COMPONENTS = "components"
    SERVICES = "services"  # Dienstleistungen
    DISCOUNTS = "discounts"
    SURCHARGES = "surcharges"
    TAXES = "taxes"
    VAT = "vat"  # Mehrwertsteuer
    TOTALS = "totals"
    NET_TOTALS = "net_totals"  # Nettosummen
    GROSS_TOTALS = "gross_totals"  # Bruttosummen
    SYSTEM = "system"
    METADATA = "metadata"


class DynamicKeyManager:
    """Manages dynamic key generation and PDF integration"""

    def __init__(self):
        self.key_registry: dict[str, dict[str, Any]] = {}
        self.conflict_counter = 0
        self.key_history: list[dict[str, Any]] = []
        self.validation_rules: dict[str, Any] = self._init_validation_rules()

    def _init_validation_rules(self) -> dict[str, Any]:
        """Initialize validation rules for keys

        Returns:
            Dictionary with validation rules
        """
        return {
            "max_key_length": 100,
            "min_key_length": 1,
            "allowed_characters": r"[A-Z0-9_]",
            "forbidden_prefixes": [
                "_",
                "0",
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9"],
            "reserved_keys": [
                "NULL",
                "NONE",
                "EMPTY",
                "UNDEFINED"],
            "max_value_length": 1000}

    def generate_keys(
        self,
        pricing_data: dict[str, Any],
        prefix: str = "",
        category: KeyCategory = KeyCategory.PRICING
    ) -> dict[str, Any]:
        """Generate dynamic keys from pricing data

        Args:
            pricing_data: Dictionary with pricing values
            prefix: Optional prefix for all keys
            category: Category for key organization

        Returns:
            Dictionary with generated dynamic keys
        """
        try:
            generated_keys = {}

            for key, value in pricing_data.items():
                # Create safe key name
                safe_key = self._create_safe_key_name(key)

                # Add prefix if provided
                if prefix:
                    full_key = f"{prefix}_{safe_key}"
                else:
                    full_key = safe_key

                # Handle conflicts
                final_key = self._resolve_key_conflict(full_key)

                # Register the key
                self.register_key(final_key, value, category.value)

                # Add to generated keys
                generated_keys[final_key] = value

            return generated_keys

        except Exception as e:
            logger.error(f"Error generating keys: {e}")
            return {}

    def register_key(
        self,
        key: str,
        value: Any,
        category: str = "pricing"
    ) -> bool:
        """Register a key in the key registry

        Args:
            key: Key name
            value: Key value
            category: Key category

        Returns:
            True if registered successfully
        """
        try:
            # Validate the complete entry
            is_valid, error_msg = self.validate_key_registry_entry(
                key, value, category)
            if not is_valid:
                logger.warning(
                    f"Key validation failed for '{key}': {error_msg}")
                self.add_to_history(
                    "validation_failed", key, {
                        "error": error_msg})
                # Still register but log the issue

            # Check for conflicts
            if key in self.key_registry:
                self.add_to_history("conflict_detected", key, {
                    "existing_value": self.key_registry[key]["value"],
                    "new_value": value
                })

            self.key_registry[key] = {
                "value": value,
                "category": category,
                "type": type(value).__name__,
                "registered_at": self._get_timestamp()
            }

            self.add_to_history("registered", key, {
                "category": category,
                "type": type(value).__name__
            })

            return True

        except Exception as e:
            logger.error(f"Error registering key '{key}': {e}")
            self.add_to_history("registration_error", key, {"error": str(e)})
            return False

    def get_all_keys(self, filter_category: str |
                     None = None) -> dict[str, Any]:
        """Get all registered keys, optionally filtered by category

        Args:
            filter_category: Optional category filter

        Returns:
            Dictionary of keys and their values
        """
        if filter_category:
            return {
                key: info["value"]
                for key, info in self.key_registry.items()
                if info["category"] == filter_category
            }
        return {
            key: info["value"]
            for key, info in self.key_registry.items()
        }

    def format_for_pdf(self, keys: dict[str, Any]) -> dict[str, str]:
        """Format keys for PDF template integration

        Args:
            keys: Dictionary of keys and values

        Returns:
            Dictionary with PDF-ready formatted values
        """
        try:
            formatted_keys = {}

            for key, value in keys.items():
                formatted_value = self._format_value_for_pdf(value)
                formatted_keys[key] = formatted_value

            return formatted_keys

        except Exception as e:
            logger.error(f"Error formatting keys for PDF: {e}")
            return {}

    def get_keys_by_category(self, category: KeyCategory) -> dict[str, Any]:
        """Get keys filtered by category enum

        Args:
            category: KeyCategory enum value

        Returns:
            Dictionary of keys in the specified category
        """
        return self.get_all_keys(category.value)

    def clear_registry(self) -> None:
        """Clear all registered keys"""
        self.key_registry.clear()
        self.conflict_counter = 0

    def get_registry_stats(self) -> dict[str, Any]:
        """Get statistics about the key registry

        Returns:
            Dictionary with registry statistics
        """
        stats = {
            "total_keys": len(self.key_registry),
            "categories": {},
            "types": {},
            "conflicts_resolved": self.conflict_counter
        }

        for key_info in self.key_registry.values():
            category = key_info["category"]
            key_type = key_info["type"]

            stats["categories"][category] = (
                stats["categories"].get(category, 0) + 1
            )
            stats["types"][key_type] = (
                stats["types"].get(key_type, 0) + 1
            )

        return stats

    def validate_key_name(self, key_name: str) -> bool:
        """Validate if a key name follows naming conventions

        Args:
            key_name: Key name to validate

        Returns:
            True if valid, False otherwise
        """
        if not key_name or not isinstance(key_name, str):
            return False

        # Check if it matches safe key pattern
        pattern = r'^[A-Z][A-Z0-9_]*[A-Z0-9]$|^[A-Z]$'
        return bool(re.match(pattern, key_name))

    def validate_key_value(self, value: Any) -> tuple[bool, str]:
        """Validate if a key value is suitable for PDF templates

        Args:
            value: Value to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Try to format the value for PDF
            formatted = self._format_value_for_pdf(value)

            # Check if formatted value is reasonable length
            if len(formatted) > 1000:
                return False, "Formatted value too long for PDF template"

            return True, ""
        except Exception as e:
            return False, f"Cannot format value for PDF: {str(e)}"

    def validate_key_registry_entry(
        self,
        key: str,
        value: Any,
        category: str
    ) -> tuple[bool, str]:
        """Validate a complete key registry entry

        Args:
            key: Key name
            value: Key value
            category: Key category

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate key name
        if not self.validate_key_name(key):
            return False, f"Invalid key name format: '{key}'"

        # Validate key value
        value_valid, value_error = self.validate_key_value(value)
        if not value_valid:
            return False, value_error

        # Validate category
        valid_categories = [cat.value for cat in KeyCategory]
        if category not in valid_categories:
            return False, f"Invalid category: '{category}'"

        return True, ""

    def validate_key_with_rules(self, key: str) -> tuple[bool, list[str]]:
        """Validate key against comprehensive rules

        Args:
            key: Key name to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if not key or not isinstance(key, str):
            errors.append("Key must be a non-empty string")
            return False, errors

        # Check length
        if len(key) < self.validation_rules["min_key_length"]:
            errors.append(
                f"Key too short (minimum {
                    self.validation_rules['min_key_length']} characters)")

        if len(key) > self.validation_rules["max_key_length"]:
            errors.append(
                f"Key too long (maximum {
                    self.validation_rules['max_key_length']} characters)")

        # Check allowed characters
        if not re.match(
                f"^{self.validation_rules['allowed_characters']}+$", key):
            errors.append(
                "Key contains invalid characters (only A-Z, 0-9, _ allowed)")

        # Check forbidden prefixes
        for prefix in self.validation_rules["forbidden_prefixes"]:
            if key.startswith(prefix):
                errors.append(f"Key cannot start with '{prefix}'")

        # Check reserved keys
        if key in self.validation_rules["reserved_keys"]:
            errors.append(f"'{key}' is a reserved key name")

        return len(errors) == 0, errors

    def add_to_history(self, action: str, key: str,
                       details: dict[str, Any] = None) -> None:
        """Add an action to the key history

        Args:
            action: Action type (register, conflict, validate, etc.)
            key: Key name involved
            details: Additional details about the action
        """
        history_entry = {
            "timestamp": self._get_timestamp(),
            "action": action,
            "key": key,
            "details": details or {}
        }

        self.key_history.append(history_entry)

        # Keep history size manageable
        if len(self.key_history) > 1000:
            self.key_history = self.key_history[-500:]  # Keep last 500 entries

    def get_key_history(self, key: str = None,
                        action: str = None) -> list[dict[str, Any]]:
        """Get key history, optionally filtered

        Args:
            key: Filter by specific key name
            action: Filter by specific action type

        Returns:
            List of history entries
        """
        history = self.key_history

        if key:
            history = [entry for entry in history if entry["key"] == key]

        if action:
            history = [entry for entry in history if entry["action"] == action]

        return history

    def update_validation_rules(self, new_rules: dict[str, Any]) -> None:
        """Update validation rules

        Args:
            new_rules: Dictionary with new validation rules
        """
        self.validation_rules.update(new_rules)
        logger.info(f"Updated validation rules: {new_rules}")

    def get_validation_rules(self) -> dict[str, Any]:
        """Get current validation rules

        Returns:
            Dictionary with current validation rules
        """
        return self.validation_rules.copy()

    def get_key_suggestions(self, partial_key: str) -> list[str]:
        """Get key suggestions based on partial key name

        Args:
            partial_key: Partial key name

        Returns:
            List of matching key suggestions
        """
        partial_upper = partial_key.upper()
        suggestions = []

        for key in self.key_registry.keys():
            if partial_upper in key:
                suggestions.append(key)

        return sorted(suggestions)[:10]  # Limit to 10 suggestions

    def export_keys_for_template(
            self, template_format: str = "pdf") -> dict[str, str]:
        """Export all keys in format suitable for template system

        Args:
            template_format: Format type ("pdf", "html", "json")

        Returns:
            Dictionary with formatted keys
        """
        if template_format.lower() == "pdf":
            return self.format_for_pdf(self.get_all_keys())
        if template_format.lower() == "json":
            return {key: str(value)
                    for key, value in self.get_all_keys().items()}
        return {key: str(value) for key, value in self.get_all_keys().items()}

    def _create_safe_key_name(self, name: str) -> str:
        """Create a safe key name for PDF templates

        Args:
            name: Original name

        Returns:
            Safe key name with only alphanumeric characters and underscores
        """
        if not isinstance(name, str):
            name = str(name)

        # Convert to uppercase
        safe_name = name.upper()

        # Replace common German characters and currency symbols
        replacements = {
            'Ä': 'AE', 'Ö': 'OE', 'Ü': 'UE', 'ß': 'SS',
            'ä': 'ae', 'ö': 'oe', 'ü': 'ue', '€': 'EUR'
        }

        for old, new in replacements.items():
            safe_name = safe_name.replace(old, new)

        # Replace spaces and special characters with underscores
        safe_name = re.sub(r'[^A-Z0-9_]', '_', safe_name)

        # Remove multiple consecutive underscores
        safe_name = re.sub(r'_+', '_', safe_name)

        # Remove leading/trailing underscores
        safe_name = safe_name.strip('_')

        # Ensure it starts with a letter or underscore
        if safe_name and safe_name[0].isdigit():
            safe_name = f"KEY_{safe_name}"

        # Ensure minimum length
        if not safe_name:
            safe_name = "UNNAMED_KEY"

        return safe_name

    def _resolve_key_conflict(self, key: str) -> str:
        """Resolve key naming conflicts

        Args:
            key: Proposed key name

        Returns:
            Unique key name
        """
        original_key = key
        counter = 1

        while key in self.key_registry:
            key = f"{original_key}_{counter}"
            counter += 1

            # Prevent infinite loops
            if counter > 1000:
                logger.warning(
                    f"Too many conflicts for key '{original_key}', "
                    f"using timestamp"
                )
                key = f"{original_key}_{self._get_timestamp()}"
                break

        if key != original_key:
            self.conflict_counter += 1
            logger.debug(f"Resolved key conflict: '{original_key}' -> '{key}'")

        return key

    def resolve_key_conflicts_batch(
            self, keys: dict[str, Any]) -> dict[str, str]:
        """Resolve conflicts for a batch of keys

        Args:
            keys: Dictionary of proposed keys and values

        Returns:
            Dictionary mapping original keys to resolved keys
        """
        resolution_map = {}

        for original_key in keys:
            resolved_key = self._resolve_key_conflict(original_key)
            resolution_map[original_key] = resolved_key

        return resolution_map

    def check_for_conflicts(
            self, proposed_keys: list[str]) -> dict[str, list[str]]:
        """Check for potential conflicts with proposed keys

        Args:
            proposed_keys: List of proposed key names

        Returns:
            Dictionary with conflict information
        """
        conflicts = {
            "existing_conflicts": [],
            "internal_conflicts": [],
            "suggested_resolutions": {}
        }

        # Check against existing keys
        for key in proposed_keys:
            if key in self.key_registry:
                conflicts["existing_conflicts"].append(key)

        # Check for internal conflicts (duplicates in proposed list)
        seen_keys = set()
        for key in proposed_keys:
            if key in seen_keys:
                conflicts["internal_conflicts"].append(key)
            seen_keys.add(key)

        # Generate suggested resolutions
        for key in conflicts["existing_conflicts"] + \
                conflicts["internal_conflicts"]:
            conflicts["suggested_resolutions"][key] = self._resolve_key_conflict(
                key)

        return conflicts

    def get_conflict_report(self) -> dict[str, Any]:
        """Get a report of all conflicts that have been resolved

        Returns:
            Dictionary with conflict statistics and history
        """
        return {
            "total_conflicts_resolved": self.conflict_counter,
            "current_registry_size": len(self.key_registry),
            "categories_in_use": list(set(
                info["category"] for info in self.key_registry.values()
            )),
            "most_recent_keys": list(self.key_registry.keys())[-10:] if self.key_registry else []
        }

    def _format_value_for_pdf(self, value: Any) -> str:
        """Format a value for PDF template display

        Args:
            value: Value to format

        Returns:
            Formatted string value
        """
        if value is None:
            return ""
        if isinstance(value, bool):
            return "Ja" if value else "Nein"
        if isinstance(value, (int, float)):
            # Format numbers with German locale (comma as decimal separator)
            if isinstance(value, float):
                # Round to 2 decimal places for currency
                if abs(value) >= 1000:
                    formatted = f"{value:,.2f}"
                    return formatted.replace(
                        ",",
                        "X").replace(
                        ".",
                        ",").replace(
                        "X",
                        ".")
                return f"{value:.2f}".replace(".", ",")
            return f"{value:,}".replace(",", ".")
        if isinstance(value, str):
            return value
        return str(value)

    def _get_timestamp(self) -> str:
        """Get current timestamp as string"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def generate_pricing_keys_german_logic(
        self,
        component_prices: dict[str, float],
        vat_rate: float | None = None,
        prefix: str = ""
    ) -> dict[str, Any]:
        """Generate keys following German pricing logic

        Args:
            component_prices: Dictionary with component names and net prices
            vat_rate: Optional VAT rate (e.g., 0.19 for 19%)
            prefix: Optional prefix for all keys

        Returns:
            Dictionary with all pricing keys (components, net total, VAT, gross total)
        """
        all_keys = {}

        # 1. Generate keys for individual component prices
        component_keys = self.generate_keys(
            component_prices,
            prefix=f"{prefix}_COMPONENT" if prefix else "COMPONENT",
            category=KeyCategory.COMPONENTS
        )
        all_keys.update(component_keys)

        # 2. Calculate net total (sum of all components)
        net_total = sum(component_prices.values())
        net_total_key = f"{prefix}_NET_TOTAL" if prefix else "NET_TOTAL"
        self.register_key(
            net_total_key,
            net_total,
            KeyCategory.NET_TOTALS.value)
        all_keys[net_total_key] = net_total

        # 3. Optional VAT calculation
        if vat_rate is not None:
            vat_amount = net_total * vat_rate
            vat_amount_key = f"{prefix}_VAT_AMOUNT" if prefix else "VAT_AMOUNT"
            vat_rate_key = f"{prefix}_VAT_RATE" if prefix else "VAT_RATE"

            self.register_key(
                vat_amount_key,
                vat_amount,
                KeyCategory.VAT.value)
            self.register_key(
                vat_rate_key,
                vat_rate * 100,
                KeyCategory.VAT.value)  # As percentage

            all_keys[vat_amount_key] = vat_amount
            all_keys[vat_rate_key] = vat_rate * 100

            # 4. Calculate gross total (net + VAT)
            gross_total = net_total + vat_amount
            gross_total_key = f"{prefix}_GROSS_TOTAL" if prefix else "GROSS_TOTAL"
            self.register_key(
                gross_total_key,
                gross_total,
                KeyCategory.GROSS_TOTALS.value)
            all_keys[gross_total_key] = gross_total

        return all_keys

    def generate_vat_keys(
        self,
        net_amount: float,
        vat_rate: float,
        prefix: str = ""
    ) -> dict[str, Any]:
        """Generate VAT-related keys dynamically

        Args:
            net_amount: Net amount before VAT
            vat_rate: VAT rate (e.g., 0.19 for 19%)
            prefix: Optional prefix for keys

        Returns:
            Dictionary with VAT keys
        """
        vat_keys = {}

        vat_amount = net_amount * vat_rate
        gross_amount = net_amount + vat_amount

        # Generate keys
        keys_data = {
            "vat_rate_percent": vat_rate * 100,
            "vat_amount": vat_amount,
            "net_amount": net_amount,
            "gross_amount": gross_amount
        }

        vat_keys = self.generate_keys(
            keys_data,
            prefix=f"{prefix}_VAT" if prefix else "VAT",
            category=KeyCategory.VAT
        )

        return vat_keys

    def calculate_component_totals(
        self,
        components: dict[str, dict[str, Any]],
        prefix: str = ""
    ) -> dict[str, Any]:
        """Calculate totals for components with individual VAT handling

        Args:
            components: Dict with component data including price and optional vat_rate
            prefix: Optional prefix for keys

        Returns:
            Dictionary with component total keys
        """
        total_keys = {}
        net_total = 0.0
        vat_total = 0.0

        # Process each component
        for comp_name, comp_data in components.items():
            price = comp_data.get("price", 0.0)
            vat_rate = comp_data.get("vat_rate", None)

            # Add to net total
            net_total += price

            # Generate component key with proper formatting
            safe_comp_name = self._create_safe_key_name(comp_name)
            comp_key = f"{prefix}_{safe_comp_name}_PRICE" if prefix else f"{safe_comp_name}_PRICE"
            self.register_key(comp_key, price, KeyCategory.COMPONENTS.value)
            total_keys[comp_key] = price

            # Handle individual VAT if specified
            if vat_rate is not None:
                comp_vat = price * vat_rate
                vat_total += comp_vat

                comp_vat_key = f"{prefix}_{safe_comp_name}_VAT" if prefix else f"{safe_comp_name}_VAT"
                self.register_key(
                    comp_vat_key, comp_vat, KeyCategory.VAT.value)
                total_keys[comp_vat_key] = comp_vat

        # Generate total keys
        net_key = f"{prefix}_NET_TOTAL" if prefix else "NET_TOTAL"
        self.register_key(net_key, net_total, KeyCategory.NET_TOTALS.value)
        total_keys[net_key] = net_total

        if vat_total > 0:
            vat_key = f"{prefix}_VAT_TOTAL" if prefix else "VAT_TOTAL"
            gross_key = f"{prefix}_GROSS_TOTAL" if prefix else "GROSS_TOTAL"

            self.register_key(vat_key, vat_total, KeyCategory.VAT.value)
            self.register_key(
                gross_key,
                net_total + vat_total,
                KeyCategory.GROSS_TOTALS.value)

            total_keys[vat_key] = vat_total
            total_keys[gross_key] = net_total + vat_total

        return total_keys
