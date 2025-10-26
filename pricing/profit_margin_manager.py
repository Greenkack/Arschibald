"""Profit Margin Manager

Handles profit margin configuration and calculation with support for different
calculation methods (calculate_per) including per piece, per meter, lump sum, per kWp, etc.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

try:
    from database import get_db_connection, load_admin_setting, save_admin_setting
    from product_db import (
        get_product_by_id,
        list_products,
        update_product_pricing_fields,
    )
except ImportError:
    # Fallback for testing without database
    def get_product_by_id(product_id: int) -> dict[str, Any] | None:
        return None

    def update_product_pricing_fields(
            product_id: int, fields: dict[str, Any]) -> bool:
        return False

    def get_db_connection():
        return None

    def load_admin_setting(key: str, default: Any = None) -> Any:
        return default

    def save_admin_setting(key: str, value: Any) -> bool:
        return True

    def list_products(category: str | None = None,
                      company_id: int | None = None) -> list[dict[str, Any]]:
        return []

logger = logging.getLogger(__name__)


@dataclass
class MarginConfig:
    """Configuration for profit margins"""
    margin_type: str  # 'percentage' or 'fixed'
    margin_value: float
    applies_to: str  # 'product', 'category', 'global'
    priority: int = 0
    calculate_per_method: str | None = None  # For method-specific margins
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate margin configuration"""
        if self.margin_type not in ['percentage', 'fixed']:
            raise ValueError(
                f"Invalid margin_type: {
                    self.margin_type}. Must be 'percentage' or 'fixed'")

        if self.applies_to not in ['product', 'category', 'global']:
            raise ValueError(
                f"Invalid applies_to: {
                    self.applies_to}. Must be 'product', 'category', or 'global'")

        if self.margin_type == 'percentage' and (
                self.margin_value < 0 or self.margin_value > 1000):
            logger.warning(f"Unusual percentage margin: {self.margin_value}%")

        if self.margin_type == 'fixed' and self.margin_value < 0:
            raise ValueError("Fixed margin cannot be negative")


@dataclass
class MarginBreakdown:
    """Detailed breakdown of margin calculation"""
    purchase_price: float
    margin_amount: float
    selling_price: float
    margin_percentage: float
    source: str  # 'product', 'category', 'global'
    calculate_per_method: str | None = None
    quantity: float = 1.0
    total_purchase_cost: float = field(init=False)
    total_selling_price: float = field(init=False)
    total_margin_amount: float = field(init=False)

    def __post_init__(self):
        """Calculate totals based on quantity and calculation method"""
        self.total_purchase_cost = self._calculate_total_cost(
            self.purchase_price)
        self.total_selling_price = self._calculate_total_cost(
            self.selling_price)
        self.total_margin_amount = self.total_selling_price - self.total_purchase_cost

    def _calculate_total_cost(self, unit_price: float) -> float:
        """Calculate total cost based on calculate_per method"""
        if not self.calculate_per_method:
            return unit_price * self.quantity

        method = self.calculate_per_method.lower().strip()

        if method in ["stück", "piece", "unit"]:
            return unit_price * self.quantity
        if method in ["meter", "m"]:
            return unit_price * self.quantity  # quantity represents meters
        if method in ["pauschal", "lump_sum", "flat"]:
            return unit_price  # Ignore quantity for lump sum
        if method in ["kwp", "kw_peak"]:
            return unit_price * self.quantity  # quantity represents kWp
        # Default to per piece
        return unit_price * self.quantity


class ProfitMarginManager:
    """Manages profit margins with calculate_per support"""

    def __init__(self):
        """Initialize profit margin manager"""
        self.logger = logging.getLogger(f"{__name__}.ProfitMarginManager")
        self._global_margins: dict[str, MarginConfig] = {}
        self._category_margins: dict[str, MarginConfig] = {}
        self._load_global_margins()

    def set_product_margin(
            self,
            product_id: int,
            margin_config: MarginConfig) -> bool:
        """Set margin configuration for a specific product

        Args:
            product_id: ID of the product
            margin_config: Margin configuration to apply

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate product exists
            product = get_product_by_id(product_id)
            if not product:
                self.logger.error(f"Product not found: {product_id}")
                return False

            # Update product with margin configuration
            margin_fields = {
                'margin_type': margin_config.margin_type,
                'margin_value': margin_config.margin_value,
                'margin_priority': margin_config.priority,
                'last_price_update': datetime.now().isoformat()
            }

            success = update_product_pricing_fields(product_id, margin_fields)
            if success:
                self.logger.info(
                    f"Updated margin for product {product_id}: {
                        margin_config.margin_type} {
                        margin_config.margin_value}")
            else:
                self.logger.error(
                    f"Failed to update margin for product {product_id}")

            return success

        except Exception as e:
            self.logger.error(f"Error setting product margin: {e}")
            return False

    def set_global_margin(
            self,
            margin_config: MarginConfig,
            category: str | None = None) -> bool:
        """Set global or category-level margin configuration

        Args:
            margin_config: Margin configuration to apply
            category: Optional category to apply margin to (None for global)

        Returns:
            True if successful, False otherwise
        """
        try:
            if category:
                # Category-level margin
                margin_config.applies_to = 'category'
                self._category_margins[category] = margin_config
                self.logger.info(
                    f"Set category margin for '{category}': {
                        margin_config.margin_type} {
                        margin_config.margin_value}")

                # Persist category margins
                success = self._save_category_margins()
                if not success:
                    self.logger.error(
                        f"Failed to persist category margin for '{category}'")
                    return False
            else:
                # Global margin
                margin_config.applies_to = 'global'
                key = margin_config.calculate_per_method or 'default'
                self._global_margins[key] = margin_config
                self.logger.info(
                    f"Set global margin for '{key}': {
                        margin_config.margin_type} {
                        margin_config.margin_value}")

                # Persist global margins
                success = self._save_global_margins()
                if not success:
                    self.logger.error(
                        f"Failed to persist global margin for '{key}'")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Error setting global margin: {e}")
            return False

    def calculate_selling_price(
            self,
            purchase_price: float,
            product_id: int | None = None,
            category: str | None = None,
            calculate_per: str | None = None,
            quantity: float = 1.0) -> float:
        """Calculate selling price based on purchase price and applicable margins

        Args:
            purchase_price: Base purchase price
            product_id: Optional product ID for product-specific margins
            category: Optional category for category-specific margins
            calculate_per: Calculation method for method-specific margins
            quantity: Quantity for total price calculation

        Returns:
            Calculated selling price
        """
        try:
            margin_breakdown = self.get_margin_breakdown(
                purchase_price=purchase_price,
                product_id=product_id,
                category=category,
                calculate_per=calculate_per,
                quantity=quantity
            )

            return margin_breakdown.selling_price

        except Exception as e:
            self.logger.error(f"Error calculating selling price: {e}")
            return purchase_price  # Fallback to purchase price

    def get_margin_breakdown(
            self,
            purchase_price: float,
            product_id: int | None = None,
            category: str | None = None,
            calculate_per: str | None = None,
            quantity: float = 1.0) -> MarginBreakdown:
        """Get detailed margin breakdown with priority resolution

        Args:
            purchase_price: Base purchase price
            product_id: Optional product ID for product-specific margins
            category: Optional category for category-specific margins
            calculate_per: Calculation method for method-specific margins
            quantity: Quantity for total calculation

        Returns:
            MarginBreakdown with detailed calculation information
        """
        try:
            # Find applicable margin configuration (priority: product >
            # category > global)
            margin_config = self._find_applicable_margin(
                product_id, category, calculate_per)

            if not margin_config:
                # No margin configured, return purchase price as selling price
                return MarginBreakdown(
                    purchase_price=purchase_price,
                    margin_amount=0.0,
                    selling_price=purchase_price,
                    margin_percentage=0.0,
                    source='none',
                    calculate_per_method=calculate_per,
                    quantity=quantity
                )

            # Calculate margin amount and selling price
            if margin_config.margin_type == 'percentage':
                margin_amount = purchase_price * \
                    (margin_config.margin_value / 100.0)
                selling_price = purchase_price + margin_amount
                margin_percentage = margin_config.margin_value
            else:  # fixed
                margin_amount = margin_config.margin_value
                selling_price = purchase_price + margin_amount
                margin_percentage = (
                    margin_amount /
                    purchase_price *
                    100.0) if purchase_price > 0 else 0.0

            return MarginBreakdown(
                purchase_price=purchase_price,
                margin_amount=margin_amount,
                selling_price=selling_price,
                margin_percentage=margin_percentage,
                source=margin_config.applies_to,
                calculate_per_method=calculate_per,
                quantity=quantity
            )

        except Exception as e:
            self.logger.error(f"Error getting margin breakdown: {e}")
            # Return fallback breakdown
            return MarginBreakdown(
                purchase_price=purchase_price,
                margin_amount=0.0,
                selling_price=purchase_price,
                margin_percentage=0.0,
                source='error',
                calculate_per_method=calculate_per,
                quantity=quantity
            )

    def calculate_total_price_with_margin(self,
                                          purchase_price: float,
                                          quantity: float,
                                          calculate_per: str,
                                          product_id: int | None = None,
                                          category: str | None = None) -> dict[str,
                                                                               float]:
        """Calculate total price including margin based on calculate_per method

        Args:
            purchase_price: Unit purchase price
            quantity: Quantity to calculate for
            calculate_per: Calculation method ("Stück", "Meter", "pauschal", "kWp", etc.)
            product_id: Optional product ID for product-specific margins
            category: Optional category for category-specific margins

        Returns:
            Dictionary with detailed price breakdown
        """
        try:
            # Get margin breakdown for unit price
            margin_breakdown = self.get_margin_breakdown(
                purchase_price=purchase_price,
                product_id=product_id,
                category=category,
                calculate_per=calculate_per,
                quantity=quantity
            )

            # Calculate method-specific totals
            method = calculate_per.lower().strip() if calculate_per else "stück"

            if method in ["stück", "piece", "unit"]:
                total_purchase = purchase_price * quantity
                total_selling = margin_breakdown.selling_price * quantity
            elif method in ["meter", "m"]:
                total_purchase = purchase_price * quantity  # quantity = meters
                total_selling = margin_breakdown.selling_price * quantity
            elif method in ["pauschal", "lump_sum", "flat"]:
                total_purchase = purchase_price  # Ignore quantity
                total_selling = margin_breakdown.selling_price
            elif method in ["kwp", "kw_peak"]:
                total_purchase = purchase_price * quantity  # quantity = kWp
                total_selling = margin_breakdown.selling_price * quantity
            else:
                # Default to per piece
                total_purchase = purchase_price * quantity
                total_selling = margin_breakdown.selling_price * quantity

            total_margin = total_selling - total_purchase

            return {
                'unit_purchase_price': purchase_price,
                'unit_selling_price': margin_breakdown.selling_price,
                'unit_margin_amount': margin_breakdown.margin_amount,
                'quantity': quantity,
                'calculate_per': calculate_per,
                'total_purchase_price': total_purchase,
                'total_selling_price': total_selling,
                'total_margin_amount': total_margin,
                'margin_percentage': margin_breakdown.margin_percentage,
                'margin_source': margin_breakdown.source
            }

        except Exception as e:
            self.logger.error(
                f"Error calculating total price with margin: {e}")
            # Return fallback calculation
            total_purchase = purchase_price * quantity
            return {
                'unit_purchase_price': purchase_price,
                'unit_selling_price': purchase_price,
                'unit_margin_amount': 0.0,
                'quantity': quantity,
                'calculate_per': calculate_per,
                'total_purchase_price': total_purchase,
                'total_selling_price': total_purchase,
                'total_margin_amount': 0.0,
                'margin_percentage': 0.0,
                'margin_source': 'error'
            }

    def _find_applicable_margin(
            self,
            product_id: int | None = None,
            category: str | None = None,
            calculate_per: str | None = None) -> MarginConfig | None:
        """Find applicable margin configuration based on priority

        Priority: product-specific > category-specific > global (method-specific) > global (default)

        Args:
            product_id: Product ID to check for product-specific margins
            category: Category to check for category-specific margins
            calculate_per: Calculation method to check for method-specific margins

        Returns:
            Applicable MarginConfig or None if no margin found
        """
        try:
            # 1. Product-specific margin (highest priority)
            if product_id:
                product = get_product_by_id(product_id)
                if product and product.get('margin_type') and product.get(
                        'margin_value') is not None:
                    return MarginConfig(
                        margin_type=product['margin_type'],
                        margin_value=float(product['margin_value']),
                        applies_to='product',
                        priority=product.get('margin_priority', 100),
                        calculate_per_method=product.get('calculate_per')
                    )

            # 2. Category-specific margin
            if category and category in self._category_margins:
                return self._category_margins[category]

            # 3. Global method-specific margin
            if calculate_per and calculate_per in self._global_margins:
                return self._global_margins[calculate_per]

            # 4. Global default margin
            if 'default' in self._global_margins:
                return self._global_margins['default']

            return None

        except Exception as e:
            self.logger.error(f"Error finding applicable margin: {e}")
            return None

    def _load_global_margins(self):
        """Load global margin configurations from admin settings"""
        try:
            # Load global margins from admin settings
            global_margins_data = load_admin_setting(
                'profit_margins_global', {})

            if global_margins_data:
                for key, margin_data in global_margins_data.items():
                    try:
                        self._global_margins[key] = MarginConfig(
                            margin_type=margin_data['margin_type'],
                            margin_value=margin_data['margin_value'],
                            applies_to='global',
                            priority=margin_data.get('priority', 0),
                            calculate_per_method=margin_data.get('calculate_per_method')
                        )
                    except (KeyError, ValueError) as e:
                        self.logger.warning(
                            f"Invalid global margin data for '{key}': {e}")
            else:
                # Set default margins if none exist
                self._set_default_global_margins()

            # Load category margins from admin settings
            category_margins_data = load_admin_setting(
                'profit_margins_category', {})

            if category_margins_data:
                for category, margin_data in category_margins_data.items():
                    try:
                        self._category_margins[category] = MarginConfig(
                            margin_type=margin_data['margin_type'],
                            margin_value=margin_data['margin_value'],
                            applies_to='category',
                            priority=margin_data.get('priority', 50),
                            calculate_per_method=margin_data.get('calculate_per_method')
                        )
                    except (KeyError, ValueError) as e:
                        self.logger.warning(
                            f"Invalid category margin data for '{category}': {e}")

            self.logger.info(
                f"Loaded {len(self._global_margins)} global and {len(self._category_margins)} category margin configurations")

        except Exception as e:
            self.logger.error(f"Error loading margins: {e}")
            # Fallback to defaults
            self._set_default_global_margins()

    def _set_default_global_margins(self):
        """Set default global margin configurations"""
        try:
            # Default global margin
            self._global_margins['default'] = MarginConfig(
                margin_type='percentage',
                margin_value=25.0,  # 25% default margin
                applies_to='global',
                priority=0
            )

            # Method-specific margins
            self._global_margins['pauschal'] = MarginConfig(
                margin_type='percentage',
                margin_value=30.0,  # Higher margin for services
                applies_to='global',
                priority=10,
                calculate_per_method='pauschal'
            )

            # Save defaults to admin settings
            self._save_global_margins()

            self.logger.info("Set default global margin configurations")

        except Exception as e:
            self.logger.error(f"Error setting default global margins: {e}")

    def _save_global_margins(self) -> bool:
        """Save global margins to admin settings"""
        try:
            global_margins_data = {}

            for key, margin_config in self._global_margins.items():
                global_margins_data[key] = {
                    'margin_type': margin_config.margin_type,
                    'margin_value': margin_config.margin_value,
                    'priority': margin_config.priority,
                    'calculate_per_method': margin_config.calculate_per_method,
                    'created_at': margin_config.created_at.isoformat(),
                    'updated_at': margin_config.updated_at.isoformat()
                }

            success = save_admin_setting(
                'profit_margins_global', global_margins_data)
            if success:
                self.logger.info("Saved global margins to admin settings")
            else:
                self.logger.error(
                    "Failed to save global margins to admin settings")

            return success

        except Exception as e:
            self.logger.error(f"Error saving global margins: {e}")
            return False

    def _save_category_margins(self) -> bool:
        """Save category margins to admin settings"""
        try:
            category_margins_data = {}

            for category, margin_config in self._category_margins.items():
                category_margins_data[category] = {
                    'margin_type': margin_config.margin_type,
                    'margin_value': margin_config.margin_value,
                    'priority': margin_config.priority,
                    'calculate_per_method': margin_config.calculate_per_method,
                    'created_at': margin_config.created_at.isoformat(),
                    'updated_at': margin_config.updated_at.isoformat()
                }

            success = save_admin_setting(
                'profit_margins_category', category_margins_data)
            if success:
                self.logger.info("Saved category margins to admin settings")
            else:
                self.logger.error(
                    "Failed to save category margins to admin settings")

            return success

        except Exception as e:
            self.logger.error(f"Error saving category margins: {e}")
            return False

    def get_all_margins(self) -> dict[str, Any]:
        """Get all configured margins for reporting/admin purposes

        Returns:
            Dictionary with all margin configurations
        """
        try:
            return {
                'global_margins': {k: {
                    'margin_type': v.margin_type,
                    'margin_value': v.margin_value,
                    'applies_to': v.applies_to,
                    'priority': v.priority,
                    'calculate_per_method': v.calculate_per_method
                } for k, v in self._global_margins.items()},
                'category_margins': {k: {
                    'margin_type': v.margin_type,
                    'margin_value': v.margin_value,
                    'applies_to': v.applies_to,
                    'priority': v.priority,
                    'calculate_per_method': v.calculate_per_method
                } for k, v in self._category_margins.items()}
            }

        except Exception as e:
            self.logger.error(f"Error getting all margins: {e}")
            return {'global_margins': {}, 'category_margins': {}}

    def set_category_margin(
            self,
            category: str,
            margin_config: MarginConfig) -> bool:
        """Set margin configuration for a specific category

        Args:
            category: Product category name
            margin_config: Margin configuration to apply

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate category exists in products
            products_in_category = list_products(category=category)
            if not products_in_category:
                self.logger.warning(
                    f"No products found in category '{category}', but setting margin anyway")

            margin_config.applies_to = 'category'
            return self.set_global_margin(margin_config, category=category)

        except Exception as e:
            self.logger.error(f"Error setting category margin: {e}")
            return False

    def remove_category_margin(self, category: str) -> bool:
        """Remove margin configuration for a specific category

        Args:
            category: Product category name

        Returns:
            True if successful, False otherwise
        """
        try:
            if category in self._category_margins:
                del self._category_margins[category]
                success = self._save_category_margins()
                if success:
                    self.logger.info(
                        f"Removed category margin for '{category}'")
                else:
                    self.logger.error(
                        f"Failed to persist removal of category margin for '{category}'")
                return success
            self.logger.warning(
                f"No margin configuration found for category '{category}'")
            return True  # Not an error if it doesn't exist

        except Exception as e:
            self.logger.error(f"Error removing category margin: {e}")
            return False

    def get_available_categories(self) -> list[str]:
        """Get list of available product categories

        Returns:
            List of category names
        """
        try:
            products = list_products()
            categories = set()

            for product in products:
                if product.get('category'):
                    categories.add(product['category'])

            return sorted(list(categories))

        except Exception as e:
            self.logger.error(f"Error getting available categories: {e}")
            return []

    def apply_margin_to_category_products(
            self, category: str, margin_config: MarginConfig) -> dict[str, Any]:
        """Apply margin configuration to all products in a category

        Args:
            category: Product category name
            margin_config: Margin configuration to apply

        Returns:
            Dictionary with application results
        """
        try:
            products = list_products(category=category)

            if not products:
                return {
                    'success': False,
                    'message': f"No products found in category '{category}'",
                    'updated_count': 0,
                    'failed_count': 0,
                    'products': []
                }

            updated_count = 0
            failed_count = 0
            results = []

            for product in products:
                try:
                    success = self.set_product_margin(
                        product['id'], margin_config)
                    if success:
                        updated_count += 1
                        results.append({
                            'product_id': product['id'],
                            'model_name': product.get('model_name', ''),
                            'success': True
                        })
                    else:
                        failed_count += 1
                        results.append({
                            'product_id': product['id'],
                            'model_name': product.get('model_name', ''),
                            'success': False,
                            'error': 'Failed to update product margin'
                        })

                except Exception as e:
                    failed_count += 1
                    results.append({
                        'product_id': product['id'],
                        'model_name': product.get('model_name', ''),
                        'success': False,
                        'error': str(e)
                    })

            return {
                'success': failed_count == 0,
                'message': f"Updated {updated_count} products, {failed_count} failed",
                'updated_count': updated_count,
                'failed_count': failed_count,
                'products': results}

        except Exception as e:
            self.logger.error(
                f"Error applying margin to category products: {e}")
            return {
                'success': False,
                'message': f"Error applying margin: {e}",
                'updated_count': 0,
                'failed_count': 0,
                'products': []
            }

    def get_margin_priority_info(self,
                                 product_id: int | None = None,
                                 category: str | None = None,
                                 calculate_per: str | None = None) -> dict[str,
                                                                           Any]:
        """Get detailed information about margin priority resolution

        Args:
            product_id: Product ID to check
            category: Category to check
            calculate_per: Calculation method to check

        Returns:
            Dictionary with priority resolution information
        """
        try:
            priority_info = {
                'product_margin': None,
                'category_margin': None,
                'global_method_margin': None,
                'global_default_margin': None,
                'selected_margin': None,
                'selection_reason': None
            }

            # Check product-specific margin
            if product_id:
                product = get_product_by_id(product_id)
                if product and product.get('margin_type') and product.get(
                        'margin_value') is not None:
                    priority_info['product_margin'] = {
                        'margin_type': product['margin_type'],
                        'margin_value': product['margin_value'],
                        'priority': product.get('margin_priority', 100),
                        'source': 'product'
                    }

            # Check category-specific margin
            if category and category in self._category_margins:
                margin_config = self._category_margins[category]
                priority_info['category_margin'] = {
                    'margin_type': margin_config.margin_type,
                    'margin_value': margin_config.margin_value,
                    'priority': margin_config.priority,
                    'source': 'category'
                }

            # Check global method-specific margin
            if calculate_per and calculate_per in self._global_margins:
                margin_config = self._global_margins[calculate_per]
                priority_info['global_method_margin'] = {
                    'margin_type': margin_config.margin_type,
                    'margin_value': margin_config.margin_value,
                    'priority': margin_config.priority,
                    'source': 'global_method'
                }

            # Check global default margin
            if 'default' in self._global_margins:
                margin_config = self._global_margins['default']
                priority_info['global_default_margin'] = {
                    'margin_type': margin_config.margin_type,
                    'margin_value': margin_config.margin_value,
                    'priority': margin_config.priority,
                    'source': 'global_default'
                }

            # Determine selected margin (priority: product > category > global
            # method > global default)
            if priority_info['product_margin']:
                priority_info['selected_margin'] = priority_info['product_margin']
                priority_info['selection_reason'] = 'Product-specific margin has highest priority'
            elif priority_info['category_margin']:
                priority_info['selected_margin'] = priority_info['category_margin']
                priority_info[
                    'selection_reason'] = 'Category-specific margin selected (no product margin)'
            elif priority_info['global_method_margin']:
                priority_info['selected_margin'] = priority_info['global_method_margin']
                priority_info[
                    'selection_reason'] = 'Global method-specific margin selected (no product/category margin)'
            elif priority_info['global_default_margin']:
                priority_info['selected_margin'] = priority_info['global_default_margin']
                priority_info[
                    'selection_reason'] = 'Global default margin selected (no other margins available)'
            else:
                priority_info['selection_reason'] = 'No margin configuration found'

            return priority_info

        except Exception as e:
            self.logger.error(f"Error getting margin priority info: {e}")
            return {
                'product_margin': None,
                'category_margin': None,
                'global_method_margin': None,
                'global_default_margin': None,
                'selected_margin': None,
                'selection_reason': f'Error: {e}'
            }

    def validate_margin_config(self, margin_config: MarginConfig) -> bool:
        """Validate margin configuration

        Args:
            margin_config: Margin configuration to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # Basic validation is done in MarginConfig.__post_init__
            # Additional business logic validation can be added here

            if margin_config.margin_type == 'percentage':
                if margin_config.margin_value < 0:
                    self.logger.error("Percentage margin cannot be negative")
                    return False
                if margin_config.margin_value > 500:  # 500% seems excessive
                    self.logger.warning(
                        f"Very high percentage margin: {
                            margin_config.margin_value}%")

            if margin_config.margin_type == 'fixed':
                if margin_config.margin_value < 0:
                    self.logger.error("Fixed margin cannot be negative")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating margin config: {e}")
            return False
