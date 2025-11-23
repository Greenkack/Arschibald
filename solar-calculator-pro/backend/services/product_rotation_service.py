"""
Product Rotation Service for Multi-PDF Generation

This service implements the critical product rotation logic for multi-PDF generation.
When generating multiple offers for different companies, each offer should have
DIFFERENT products/brands than previous offers to provide variety and comparison.

Key Features:
- Brand tracking (avoid repeating brands across offers)
- Product tracking (avoid repeating products across offers)
- Automatic product selection with exclusion filters
- Compatibility checking between products
- Category-based rotation (PV modules, inverters, batteries, etc.)
- Price-aware rotation (maintain similar price ranges)
"""

import sys
import os
from typing import Dict, Any, Optional, List, Set, Tuple
from datetime import datetime
from enum import Enum
import random

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.core.base_service import BaseService, HealthCheckResult, ServiceStatus
from backend.core.error_wrapper import handle_service_errors
from backend.core.logging_decorator import log_service_call


class ProductCategory(Enum):
    """Product categories for rotation"""
    PV_MODULE = "pv_module"
    INVERTER = "inverter"
    BATTERY = "battery"
    MOUNTING = "mounting"
    CABLE = "cable"
    ACCESSORY = "accessory"


class RotationStrategy(Enum):
    """Rotation strategies"""
    AVOID_BRANDS = "avoid_brands"  # Avoid previously used brands
    AVOID_PRODUCTS = "avoid_products"  # Avoid previously used products
    AVOID_BOTH = "avoid_both"  # Avoid both brands and products
    PRICE_SIMILAR = "price_similar"  # Select products with similar price
    PRICE_HIGHER = "price_higher"  # Select products with higher price
    PRICE_LOWER = "price_lower"  # Select products with lower price


class ProductRotationService(BaseService):
    """
    Product Rotation Service
    
    Manages automatic product rotation for multi-PDF generation.
    Ensures each offer has different products/brands than previous offers.
    """
    
    def __init__(self):
        super().__init__("product_rotation")
        self._product_db_module = None
        self._used_brands: Dict[str, Set[str]] = {}  # category -> set of used brands
        self._used_products: Dict[str, Set[int]] = {}  # category -> set of used product IDs
        
    def initialize(self) -> None:
        """Initialize the service"""
        try:
            # Import legacy modules
            import product_db
            self._product_db_module = product_db
            self._set_legacy_module(product_db)
            
            self._set_initialized(True)
            self.logger.info("Product Rotation Service initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Product Rotation Service: {e}")
            raise
    
    def health_check(self) -> HealthCheckResult:
        """Perform health check"""
        if not self.is_initialized:
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                message="Service not initialized"
            )
        
        if self._product_db_module is None:
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                message="Product DB module not loaded"
            )
        
        return HealthCheckResult(
            status=ServiceStatus.HEALTHY,
            message="Service is healthy"
        )
    
    # ==================== Rotation State Management ====================
    
    def reset_rotation_state(self) -> None:
        """Reset rotation state (clear all tracked brands and products)"""
        self._used_brands.clear()
        self._used_products.clear()
        self.logger.info("Reset product rotation state")
    
    def get_rotation_state(self) -> Dict[str, Any]:
        """
        Get current rotation state.
        
        Returns:
            Dictionary with used brands and products per category
        """
        return {
            "used_brands": {
                category: list(brands) 
                for category, brands in self._used_brands.items()
            },
            "used_products": {
                category: list(products) 
                for category, products in self._used_products.items()
            },
            "total_used_brands": sum(len(brands) for brands in self._used_brands.values()),
            "total_used_products": sum(len(products) for products in self._used_products.values())
        }
    
    def mark_brand_used(self, category: str, brand: str) -> None:
        """
        Mark a brand as used in a category.
        
        Args:
            category: Product category
            brand: Brand name
        """
        if category not in self._used_brands:
            self._used_brands[category] = set()
        self._used_brands[category].add(brand)
        self.logger.debug(f"Marked brand '{brand}' as used in category '{category}'")
    
    def mark_product_used(self, category: str, product_id: int) -> None:
        """
        Mark a product as used in a category.
        
        Args:
            category: Product category
            product_id: Product ID
        """
        if category not in self._used_products:
            self._used_products[category] = set()
        self._used_products[category].add(product_id)
        self.logger.debug(f"Marked product {product_id} as used in category '{category}'")
    
    def is_brand_used(self, category: str, brand: str) -> bool:
        """
        Check if a brand has been used in a category.
        
        Args:
            category: Product category
            brand: Brand name
            
        Returns:
            True if brand has been used
        """
        return brand in self._used_brands.get(category, set())
    
    def is_product_used(self, category: str, product_id: int) -> bool:
        """
        Check if a product has been used in a category.
        
        Args:
            category: Product category
            product_id: Product ID
            
        Returns:
            True if product has been used
        """
        return product_id in self._used_products.get(category, set())
    
    # ==================== Product Selection with Rotation ====================
    
    @log_service_call(service_name="product_rotation", log_timing=True)
    @handle_service_errors(service_name="product_rotation", error_message="Failed to select rotated product")
    def select_rotated_product(
        self,
        category: str,
        strategy: str = RotationStrategy.AVOID_BOTH.value,
        reference_product_id: Optional[int] = None,
        price_tolerance: float = 0.2,
        required_specs: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Select a product with rotation logic applied.
        
        Args:
            category: Product category to select from
            strategy: Rotation strategy to use
            reference_product_id: Reference product for price comparison
            price_tolerance: Price tolerance (0.2 = ±20%)
            required_specs: Required specifications (e.g., min power, efficiency)
            
        Returns:
            Selected product or None if no suitable product found
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        # Get all products in category
        all_products = self._get_products_by_category(category)
        
        if not all_products:
            self.logger.warning(f"No products found in category '{category}'")
            return None
        
        # Apply rotation filters
        strategy_enum = RotationStrategy(strategy)
        filtered_products = self._apply_rotation_filters(
            all_products,
            category,
            strategy_enum
        )
        
        if not filtered_products:
            self.logger.warning(f"No products available after rotation filters in category '{category}'")
            # Fallback: return any product if rotation filters are too strict
            filtered_products = all_products
        
        # Apply specification filters
        if required_specs:
            filtered_products = self._apply_spec_filters(filtered_products, required_specs)
        
        if not filtered_products:
            self.logger.warning(f"No products match required specifications in category '{category}'")
            return None
        
        # Apply price filters if reference product provided
        if reference_product_id:
            reference_product = self._product_db_module.get_product_by_id(reference_product_id)
            if reference_product:
                filtered_products = self._apply_price_filters(
                    filtered_products,
                    reference_product,
                    strategy_enum,
                    price_tolerance
                )
        
        if not filtered_products:
            self.logger.warning(f"No products match price criteria in category '{category}'")
            return None
        
        # Select best product from filtered list
        selected_product = self._select_best_product(filtered_products, strategy_enum)
        
        if selected_product:
            # Mark as used
            self.mark_brand_used(category, selected_product.get("brand", ""))
            self.mark_product_used(category, selected_product["id"])
            
            self.logger.info(
                f"Selected product {selected_product['id']} "
                f"(Brand: {selected_product.get('brand')}, "
                f"Model: {selected_product.get('model_name')}) "
                f"for category '{category}'"
            )
        
        return selected_product
    
    @log_service_call(service_name="product_rotation", log_timing=True)
    @handle_service_errors(service_name="product_rotation", error_message="Failed to select product set")
    def select_product_set(
        self,
        categories: List[str],
        strategy: str = RotationStrategy.AVOID_BOTH.value,
        reference_products: Optional[Dict[str, int]] = None,
        price_tolerance: float = 0.2,
        required_specs: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Select a complete set of products across multiple categories.
        
        Args:
            categories: List of product categories
            strategy: Rotation strategy to use
            reference_products: Reference products per category for price comparison
            price_tolerance: Price tolerance (0.2 = ±20%)
            required_specs: Required specifications per category
            
        Returns:
            Dictionary mapping category to selected product
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        product_set = {}
        
        for category in categories:
            ref_product_id = reference_products.get(category) if reference_products else None
            specs = required_specs.get(category) if required_specs else None
            
            product = self.select_rotated_product(
                category=category,
                strategy=strategy,
                reference_product_id=ref_product_id,
                price_tolerance=price_tolerance,
                required_specs=specs
            )
            
            product_set[category] = product
        
        self.logger.info(f"Selected product set for {len(categories)} categories")
        
        return product_set
    
    # ==================== Compatibility Checking ====================
    
    @log_service_call(service_name="product_rotation", log_timing=True)
    @handle_service_errors(service_name="product_rotation", error_message="Failed to check compatibility")
    def check_product_compatibility(
        self,
        product_set: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check compatibility between products in a set.
        
        Args:
            product_set: Dictionary mapping category to product
            
        Returns:
            Compatibility report with issues and warnings
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        issues = []
        warnings = []
        
        # Check PV module and inverter compatibility
        if "pv_module" in product_set and "inverter" in product_set:
            pv_module = product_set["pv_module"]
            inverter = product_set["inverter"]
            
            if pv_module and inverter:
                # Check voltage compatibility
                module_voc = pv_module.get("voc_v", 0)
                inverter_max_voltage = inverter.get("max_dc_voltage", 0)
                
                if module_voc > inverter_max_voltage:
                    issues.append({
                        "type": "voltage_mismatch",
                        "message": f"Module Voc ({module_voc}V) exceeds inverter max voltage ({inverter_max_voltage}V)",
                        "severity": "critical"
                    })
                
                # Check power compatibility
                module_power = pv_module.get("power_wp", 0)
                inverter_power = inverter.get("max_power_w", 0)
                
                if module_power > inverter_power * 1.2:  # Allow 20% oversizing
                    warnings.append({
                        "type": "power_mismatch",
                        "message": f"Module power ({module_power}W) significantly exceeds inverter capacity ({inverter_power}W)",
                        "severity": "warning"
                    })
        
        # Check battery and inverter compatibility
        if "battery" in product_set and "inverter" in product_set:
            battery = product_set["battery"]
            inverter = product_set["inverter"]
            
            if battery and inverter:
                # Check if inverter supports battery
                inverter_has_battery = inverter.get("has_battery_support", False)
                
                if not inverter_has_battery:
                    issues.append({
                        "type": "battery_not_supported",
                        "message": "Selected inverter does not support battery storage",
                        "severity": "critical"
                    })
                
                # Check voltage compatibility
                battery_voltage = battery.get("voltage_v", 0)
                inverter_battery_voltage = inverter.get("battery_voltage_v", 0)
                
                if battery_voltage != inverter_battery_voltage and inverter_battery_voltage > 0:
                    issues.append({
                        "type": "battery_voltage_mismatch",
                        "message": f"Battery voltage ({battery_voltage}V) does not match inverter ({inverter_battery_voltage}V)",
                        "severity": "critical"
                    })
        
        compatibility_report = {
            "is_compatible": len(issues) == 0,
            "has_warnings": len(warnings) > 0,
            "issues": issues,
            "warnings": warnings,
            "checked_at": datetime.now().isoformat()
        }
        
        self.logger.info(
            f"Compatibility check: {len(issues)} issues, {len(warnings)} warnings"
        )
        
        return compatibility_report
    
    # ==================== Helper Methods ====================
    
    def _get_products_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all products in a category"""
        # Map category to product database category
        category_mapping = {
            ProductCategory.PV_MODULE.value: "PV Module",
            ProductCategory.INVERTER.value: "Inverter",
            ProductCategory.BATTERY.value: "Battery",
            ProductCategory.MOUNTING.value: "Mounting",
            ProductCategory.CABLE.value: "Cable",
            ProductCategory.ACCESSORY.value: "Accessory"
        }
        
        db_category = category_mapping.get(category, category)
        products = self._product_db_module.list_products(category=db_category)
        
        return products if products else []
    
    def _apply_rotation_filters(
        self,
        products: List[Dict[str, Any]],
        category: str,
        strategy: RotationStrategy
    ) -> List[Dict[str, Any]]:
        """Apply rotation filters based on strategy"""
        filtered = []
        
        for product in products:
            product_id = product["id"]
            brand = product.get("brand", "")
            
            # Check based on strategy
            if strategy == RotationStrategy.AVOID_BRANDS:
                if not self.is_brand_used(category, brand):
                    filtered.append(product)
            
            elif strategy == RotationStrategy.AVOID_PRODUCTS:
                if not self.is_product_used(category, product_id):
                    filtered.append(product)
            
            elif strategy == RotationStrategy.AVOID_BOTH:
                if not self.is_brand_used(category, brand) and not self.is_product_used(category, product_id):
                    filtered.append(product)
            
            else:
                # For price-based strategies, don't filter by brand/product
                filtered.append(product)
        
        return filtered
    
    def _apply_spec_filters(
        self,
        products: List[Dict[str, Any]],
        required_specs: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply specification filters"""
        filtered = []
        
        for product in products:
            meets_specs = True
            
            for spec_key, spec_value in required_specs.items():
                product_value = product.get(spec_key)
                
                if product_value is None:
                    meets_specs = False
                    break
                
                # Handle different comparison types
                if isinstance(spec_value, dict):
                    # Range or comparison
                    if "min" in spec_value and product_value < spec_value["min"]:
                        meets_specs = False
                        break
                    if "max" in spec_value and product_value > spec_value["max"]:
                        meets_specs = False
                        break
                else:
                    # Exact match
                    if product_value != spec_value:
                        meets_specs = False
                        break
            
            if meets_specs:
                filtered.append(product)
        
        return filtered
    
    def _apply_price_filters(
        self,
        products: List[Dict[str, Any]],
        reference_product: Dict[str, Any],
        strategy: RotationStrategy,
        tolerance: float
    ) -> List[Dict[str, Any]]:
        """Apply price-based filters"""
        reference_price = reference_product.get("price_euro", 0)
        
        if reference_price == 0:
            return products
        
        filtered = []
        
        for product in products:
            product_price = product.get("price_euro", 0)
            
            if product_price == 0:
                continue
            
            price_ratio = product_price / reference_price
            
            if strategy == RotationStrategy.PRICE_SIMILAR:
                # Within tolerance range
                if (1 - tolerance) <= price_ratio <= (1 + tolerance):
                    filtered.append(product)
            
            elif strategy == RotationStrategy.PRICE_HIGHER:
                # Higher but within reasonable range
                if 1.0 < price_ratio <= (1 + tolerance * 2):
                    filtered.append(product)
            
            elif strategy == RotationStrategy.PRICE_LOWER:
                # Lower but within reasonable range
                if (1 - tolerance * 2) <= price_ratio < 1.0:
                    filtered.append(product)
            
            else:
                # No price filter
                filtered.append(product)
        
        return filtered
    
    def _select_best_product(
        self,
        products: List[Dict[str, Any]],
        strategy: RotationStrategy
    ) -> Optional[Dict[str, Any]]:
        """Select the best product from filtered list"""
        if not products:
            return None
        
        # For now, select randomly to ensure variety
        # In production, could use more sophisticated selection logic
        return random.choice(products)
    
    def _format_attribute_value(self, attr: str, value: Any) -> str:
        """Format attribute value for display"""
        if value is None:
            return "N/A"
        
        if isinstance(value, (int, float)):
            if "price" in attr.lower():
                return f"€{value:,.2f}"
            elif "power" in attr.lower():
                return f"{value}W"
            elif "voltage" in attr.lower():
                return f"{value}V"
            elif "efficiency" in attr.lower():
                return f"{value}%"
            else:
                return str(value)
        
        return str(value)


# Singleton instance
_product_rotation_service = None


def get_product_rotation_service() -> ProductRotationService:
    """Get singleton instance of Product Rotation Service"""
    global _product_rotation_service
    if _product_rotation_service is None:
        _product_rotation_service = ProductRotationService()
        _product_rotation_service.initialize()
    return _product_rotation_service
