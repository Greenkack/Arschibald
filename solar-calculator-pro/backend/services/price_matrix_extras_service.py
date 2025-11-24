"""
Price Matrix Extras and Services Service

Comprehensive service for calculating extras, services, bundles, and conditional pricing
in the price matrix system. Extracts and enhances logic from special_products.py and
services_integration.py.

This service handles:
- Special products (extras) calculation
- Service pricing (standard and optional)
- Bundle pricing with discounts
- Conditional pricing rules
- Custom pricing rules
"""

from typing import Any, Optional
from decimal import Decimal
from enum import Enum


class PricingRuleType(Enum):
    """Types of pricing rules"""
    VOLUME_DISCOUNT = "volume_discount"
    BUNDLE_DISCOUNT = "bundle_discount"
    CONDITIONAL = "conditional"
    TIME_BASED = "time_based"
    CUSTOMER_SPECIFIC = "customer_specific"


class CalculationBasis(Enum):
    """Basis for service/extra calculations"""
    PER_KWP = "kWp"
    PER_SQM = "m²"
    PER_HOUR = "Stunde"
    PER_PIECE = "Stück"
    FLAT_RATE = "Pauschal"


class PriceMatrixExtrasService:
    """Service for calculating extras, services, and applying pricing rules"""
    
    def __init__(self, db_connection=None):
        """
        Initialize the service
        
        Args:
            db_connection: Database connection (optional, will use default if not provided)
        """
        self.db = db_connection
    
    def calculate_special_products(
        self,
        project_details: dict[str, Any],
        selected_products: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Calculate costs for special products (extras)
        
        Special products are marked with is_special_product = 1 and are
        calculated in addition to the base price matrix price.
        
        Args:
            project_details: Project configuration and details
            selected_products: List of selected products with IDs and quantities
            
        Returns:
            Dictionary with:
            {
                'total': Decimal,
                'items': list[dict],
                'count': int,
                'formatted_total': str
            }
        """
        result = {
            'total': Decimal('0.00'),
            'items': [],
            'count': 0
        }
        
        for product in selected_products:
            if self._is_special_product(product):
                item = self._calculate_product_cost(product, project_details)
                result['items'].append(item)
                result['total'] += Decimal(str(item['total_price']))
                result['count'] += 1
        
        result['formatted_total'] = self._format_currency(result['total'])
        return result
    
    def calculate_services(
        self,
        project_details: dict[str, Any],
        selected_service_ids: list[int],
        include_standard: bool = True
    ) -> dict[str, Any]:
        """
        Calculate service pricing
        
        Args:
            project_details: Project configuration for quantity calculations
            selected_service_ids: IDs of selected optional services
            include_standard: Whether to include standard services (always included in matrix mode)
            
        Returns:
            Dictionary with:
            {
                'standard_services': list[dict],
                'optional_services': list[dict],
                'total_standard': Decimal,
                'total_optional': Decimal,
                'total_services': Decimal,
                'formatted_total_standard': str,
                'formatted_total_optional': str,
                'formatted_total_services': str
            }
        """
        standard_services = []
        optional_services = []
        total_standard = Decimal('0.00')
        total_optional = Decimal('0.00')
        
        # Get all services from database
        all_services = self._get_services_from_db()
        
        # Process standard services
        if include_standard:
            for service in all_services:
                if service.get('is_standard', False):
                    service_detail = self._calculate_service_cost(service, project_details)
                    standard_services.append(service_detail)
                    total_standard += Decimal(str(service_detail['total_price']))
        
        # Process optional services
        for service in all_services:
            if not service.get('is_standard', False) and service['id'] in selected_service_ids:
                service_detail = self._calculate_service_cost(service, project_details)
                optional_services.append(service_detail)
                total_optional += Decimal(str(service_detail['total_price']))
        
        return {
            'standard_services': standard_services,
            'optional_services': optional_services,
            'total_standard': total_standard,
            'total_optional': total_optional,
            'total_services': total_standard + total_optional,
            'formatted_total_standard': self._format_currency(total_standard),
            'formatted_total_optional': self._format_currency(total_optional),
            'formatted_total_services': self._format_currency(total_standard + total_optional)
        }
    
    def calculate_bundle_pricing(
        self,
        items: list[dict[str, Any]],
        bundle_rules: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Calculate bundle pricing with discounts
        
        Args:
            items: List of items in the bundle
            bundle_rules: List of bundle discount rules
            
        Returns:
            Dictionary with:
            {
                'original_total': Decimal,
                'discount_amount': Decimal,
                'discount_percentage': Decimal,
                'final_total': Decimal,
                'applied_rules': list[dict],
                'formatted_original': str,
                'formatted_discount': str,
                'formatted_final': str
            }
        """
        original_total = Decimal('0.00')
        for item in items:
            original_total += Decimal(str(item.get('total_price', 0)))
        
        # Find applicable bundle rules
        applicable_rules = self._find_applicable_bundle_rules(items, bundle_rules)
        
        # Calculate total discount
        discount_amount = Decimal('0.00')
        for rule in applicable_rules:
            if rule['type'] == 'percentage':
                discount_amount += original_total * (Decimal(str(rule['value'])) / Decimal('100'))
            elif rule['type'] == 'fixed':
                discount_amount += Decimal(str(rule['value']))
        
        final_total = original_total - discount_amount
        discount_percentage = (discount_amount / original_total * Decimal('100')) if original_total > 0 else Decimal('0')
        
        return {
            'original_total': original_total,
            'discount_amount': discount_amount,
            'discount_percentage': discount_percentage,
            'final_total': final_total,
            'applied_rules': applicable_rules,
            'formatted_original': self._format_currency(original_total),
            'formatted_discount': self._format_currency(discount_amount),
            'formatted_final': self._format_currency(final_total)
        }
    
    def apply_conditional_pricing(
        self,
        base_price: Decimal,
        conditions: dict[str, Any],
        pricing_rules: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Apply conditional pricing rules
        
        Args:
            base_price: Base price before conditional adjustments
            conditions: Current conditions (e.g., system_size, customer_type, season)
            pricing_rules: List of conditional pricing rules
            
        Returns:
            Dictionary with:
            {
                'base_price': Decimal,
                'adjustments': list[dict],
                'total_adjustment': Decimal,
                'final_price': Decimal,
                'formatted_base': str,
                'formatted_adjustment': str,
                'formatted_final': str
            }
        """
        adjustments = []
        total_adjustment = Decimal('0.00')
        
        for rule in pricing_rules:
            if self._evaluate_condition(rule['condition'], conditions):
                adjustment = self._calculate_adjustment(base_price, rule)
                adjustments.append({
                    'rule_name': rule.get('name', 'Unnamed Rule'),
                    'rule_type': rule.get('type'),
                    'amount': adjustment,
                    'formatted_amount': self._format_currency(adjustment)
                })
                total_adjustment += adjustment
        
        final_price = base_price + total_adjustment
        
        return {
            'base_price': base_price,
            'adjustments': adjustments,
            'total_adjustment': total_adjustment,
            'final_price': final_price,
            'formatted_base': self._format_currency(base_price),
            'formatted_adjustment': self._format_currency(total_adjustment),
            'formatted_final': self._format_currency(final_price)
        }
    
    def apply_custom_pricing_rules(
        self,
        pricing_data: dict[str, Any],
        custom_rules: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Apply custom pricing rules defined by user
        
        Args:
            pricing_data: Current pricing data
            custom_rules: List of custom rules to apply
            
        Returns:
            Updated pricing data with custom rules applied
        """
        result = pricing_data.copy()
        applied_rules = []
        
        for rule in custom_rules:
            if rule.get('enabled', True):
                rule_result = self._apply_single_custom_rule(result, rule)
                if rule_result['applied']:
                    applied_rules.append(rule_result)
                    result = rule_result['updated_pricing']
        
        result['applied_custom_rules'] = applied_rules
        return result
    
    # Private helper methods
    
    def _is_special_product(self, product: dict[str, Any]) -> bool:
        """Check if a product is marked as special product"""
        # Check by ID if available
        if 'id' in product and product['id']:
            return self._check_special_product_by_id(product['id'])
        
        # Check by name as fallback
        if 'model_name' in product and product['model_name']:
            return self._check_special_product_by_name(product['model_name'])
        
        return False
    
    def _check_special_product_by_id(self, product_id: int) -> bool:
        """Query database to check if product is special"""
        if not self.db:
            return False
        
        try:
            cursor = self.db.cursor()
            cursor.execute(
                "SELECT is_special_product FROM products WHERE id = ?",
                (product_id,)
            )
            row = cursor.fetchone()
            return bool(row[0]) if row and row[0] else False
        except Exception:
            return False
    
    def _check_special_product_by_name(self, model_name: str) -> bool:
        """Query database to check if product is special by name"""
        if not self.db:
            return False
        
        try:
            cursor = self.db.cursor()
            cursor.execute(
                "SELECT is_special_product FROM products WHERE model_name = ?",
                (model_name,)
            )
            row = cursor.fetchone()
            return bool(row[0]) if row and row[0] else False
        except Exception:
            return False
    
    def _calculate_product_cost(
        self,
        product: dict[str, Any],
        project_details: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate cost for a single product"""
        unit_price = Decimal(str(product.get('price', 0)))
        quantity = product.get('quantity', 1)
        
        # Apply quantity-based calculation if needed
        if product.get('calculate_per'):
            quantity = self._calculate_quantity(
                product['calculate_per'],
                project_details
            )
        
        total_price = unit_price * Decimal(str(quantity))
        
        return {
            'id': product.get('id'),
            'name': product.get('name', product.get('model_name', 'Unknown')),
            'category': product.get('category', 'Extra'),
            'unit_price': unit_price,
            'quantity': quantity,
            'calculate_per': product.get('calculate_per', 'Stück'),
            'total_price': total_price,
            'formatted_unit_price': self._format_currency(unit_price),
            'formatted_total': self._format_currency(total_price)
        }
    
    def _calculate_service_cost(
        self,
        service: dict[str, Any],
        project_details: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate cost for a single service"""
        unit_price = Decimal(str(service.get('price', 0)))
        calculate_per = service.get('calculate_per', 'Stück')
        
        quantity = self._calculate_quantity(calculate_per, project_details)
        total_price = unit_price * Decimal(str(quantity))
        
        return {
            'id': service['id'],
            'name': service['name'],
            'description': service.get('description', ''),
            'category': service.get('category', 'Service'),
            'unit_price': unit_price,
            'quantity': quantity,
            'calculate_per': calculate_per,
            'total_price': total_price,
            'is_standard': service.get('is_standard', False),
            'pdf_order': service.get('pdf_order', 0),
            'formatted_unit_price': self._format_currency(unit_price),
            'formatted_total': self._format_currency(total_price)
        }
    
    def _calculate_quantity(
        self,
        calculate_per: str,
        project_details: dict[str, Any]
    ) -> float:
        """
        Calculate quantity based on calculation basis and project details
        
        Args:
            calculate_per: Calculation basis (kWp, m², Stunde, Stück, Pauschal)
            project_details: Project configuration
            
        Returns:
            Calculated quantity
        """
        if calculate_per == CalculationBasis.PER_KWP.value:
            # Try multiple possible keys for kWp
            kwp = (project_details.get('anlage_kwp') or
                   project_details.get('pv_kwp') or
                   project_details.get('system_size_kwp') or
                   project_details.get('kwp'))
            
            if kwp is None:
                # Calculate from module data
                module_quantity = project_details.get('module_quantity', 0)
                module_power = project_details.get('module_power_w', 0)
                if module_quantity > 0 and module_power > 0:
                    kwp = (module_quantity * module_power) / 1000.0
            
            return float(kwp) if kwp else 1.0
        
        elif calculate_per == CalculationBasis.PER_SQM.value:
            # Use roof area or estimate from kWp
            roof_area = project_details.get('roof_area_m2')
            if roof_area:
                return float(roof_area)
            
            # Estimate: ~6-8 m² per kWp
            kwp = project_details.get('anlage_kwp') or project_details.get('pv_kwp', 1.0)
            return float(kwp) * 7.0
        
        elif calculate_per == CalculationBasis.PER_HOUR.value:
            # Estimate installation time based on system size
            kwp = project_details.get('anlage_kwp') or project_details.get('pv_kwp', 1.0)
            return max(8.0, float(kwp) * 2.0)  # Minimum 8 hours, 2 hours per kWp
        
        elif calculate_per in [CalculationBasis.PER_PIECE.value, CalculationBasis.FLAT_RATE.value]:
            return 1.0
        
        return 1.0
    
    def _get_services_from_db(self) -> list[dict[str, Any]]:
        """Get all services from database"""
        if not self.db:
            return []
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT id, name, description, category, price, calculate_per,
                       is_standard, pdf_order
                FROM services
                ORDER BY pdf_order, name
            """)
            
            rows = cursor.fetchall()
            services = []
            for row in rows:
                services.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'category': row[3],
                    'price': row[4],
                    'calculate_per': row[5],
                    'is_standard': bool(row[6]),
                    'pdf_order': row[7]
                })
            
            return services
        except Exception:
            return []
    
    def _find_applicable_bundle_rules(
        self,
        items: list[dict[str, Any]],
        bundle_rules: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Find bundle rules that apply to the given items"""
        applicable = []
        
        for rule in bundle_rules:
            if self._check_bundle_rule_applies(items, rule):
                applicable.append(rule)
        
        return applicable
    
    def _check_bundle_rule_applies(
        self,
        items: list[dict[str, Any]],
        rule: dict[str, Any]
    ) -> bool:
        """Check if a bundle rule applies to the items"""
        required_items = rule.get('required_items', [])
        required_categories = rule.get('required_categories', [])
        min_items = rule.get('min_items', 0)
        min_total = rule.get('min_total', 0)
        
        # Check minimum items
        if len(items) < min_items:
            return False
        
        # Check minimum total
        total = sum(Decimal(str(item.get('total_price', 0))) for item in items)
        if total < Decimal(str(min_total)):
            return False
        
        # Check required items
        if required_items:
            item_ids = {item.get('id') for item in items}
            if not all(req_id in item_ids for req_id in required_items):
                return False
        
        # Check required categories
        if required_categories:
            item_categories = {item.get('category') for item in items}
            if not all(req_cat in item_categories for req_cat in required_categories):
                return False
        
        return True
    
    def _evaluate_condition(
        self,
        condition: dict[str, Any],
        context: dict[str, Any]
    ) -> bool:
        """Evaluate a conditional pricing rule"""
        condition_type = condition.get('type')
        field = condition.get('field')
        operator = condition.get('operator')
        value = condition.get('value')
        
        if field not in context:
            return False
        
        context_value = context[field]
        
        if operator == 'equals':
            return context_value == value
        elif operator == 'not_equals':
            return context_value != value
        elif operator == 'greater_than':
            return float(context_value) > float(value)
        elif operator == 'less_than':
            return float(context_value) < float(value)
        elif operator == 'greater_equal':
            return float(context_value) >= float(value)
        elif operator == 'less_equal':
            return float(context_value) <= float(value)
        elif operator == 'in':
            return context_value in value
        elif operator == 'not_in':
            return context_value not in value
        
        return False
    
    def _calculate_adjustment(
        self,
        base_price: Decimal,
        rule: dict[str, Any]
    ) -> Decimal:
        """Calculate price adjustment based on rule"""
        adjustment_type = rule.get('adjustment_type')
        adjustment_value = Decimal(str(rule.get('adjustment_value', 0)))
        
        if adjustment_type == 'percentage':
            return base_price * (adjustment_value / Decimal('100'))
        elif adjustment_type == 'fixed':
            return adjustment_value
        elif adjustment_type == 'multiplier':
            return base_price * adjustment_value - base_price
        
        return Decimal('0.00')
    
    def _apply_single_custom_rule(
        self,
        pricing_data: dict[str, Any],
        rule: dict[str, Any]
    ) -> dict[str, Any]:
        """Apply a single custom pricing rule"""
        result = {
            'applied': False,
            'rule_name': rule.get('name', 'Custom Rule'),
            'updated_pricing': pricing_data.copy()
        }
        
        rule_type = rule.get('type')
        
        if rule_type == 'discount':
            # Apply discount
            discount_value = Decimal(str(rule.get('value', 0)))
            if rule.get('value_type') == 'percentage':
                current_total = Decimal(str(pricing_data.get('total', 0)))
                discount_amount = current_total * (discount_value / Decimal('100'))
            else:
                discount_amount = discount_value
            
            result['updated_pricing']['total'] = Decimal(str(pricing_data.get('total', 0))) - discount_amount
            result['updated_pricing']['discount_applied'] = discount_amount
            result['applied'] = True
        
        elif rule_type == 'surcharge':
            # Apply surcharge
            surcharge_value = Decimal(str(rule.get('value', 0)))
            if rule.get('value_type') == 'percentage':
                current_total = Decimal(str(pricing_data.get('total', 0)))
                surcharge_amount = current_total * (surcharge_value / Decimal('100'))
            else:
                surcharge_amount = surcharge_value
            
            result['updated_pricing']['total'] = Decimal(str(pricing_data.get('total', 0))) + surcharge_amount
            result['updated_pricing']['surcharge_applied'] = surcharge_amount
            result['applied'] = True
        
        return result
    
    def _format_currency(self, amount: Decimal) -> str:
        """Format currency in German format: 1.234,56 €"""
        # Convert to string with 2 decimal places
        formatted = f"{amount:.2f}"
        
        # Split into integer and decimal parts
        if '.' in formatted:
            integer_part, decimal_part = formatted.split('.')
        else:
            integer_part, decimal_part = formatted, "00"
        
        # Add thousand separators (dots) to integer part
        if len(integer_part) > 3:
            # Reverse, add dots every 3 digits, then reverse back
            reversed_int = integer_part[::-1]
            grouped = '.'.join(reversed_int[i:i+3] for i in range(0, len(reversed_int), 3))
            integer_part = grouped[::-1]
        
        return f"{integer_part},{decimal_part} €"
