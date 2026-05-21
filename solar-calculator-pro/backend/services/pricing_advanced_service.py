"""
PricingAdvancedService - Advanced Pricing Features

This service extends the basic PricingService with advanced features:
- Dynamic pricing rules engine
- Volume discount calculations
- Time-based pricing
- Customer-specific pricing
- Bundle pricing logic
- Promotional pricing
- Currency conversion
- Price history tracking

Requirements: 1.3, 4.5, 6.1
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import logging
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import base pricing service - create a simple mock for standalone use
class PricingService:
    """Mock pricing service for standalone use"""
    def health_check(self):
        return {"service": "PricingService", "status": "healthy"}

def get_pricing_service():
    """Get pricing service instance"""
    return PricingService()

logger = logging.getLogger(__name__)


class PricingRuleType(Enum):
    """Types of pricing rules"""
    VOLUME_DISCOUNT = "volume_discount"
    TIME_BASED = "time_based"
    CUSTOMER_SPECIFIC = "customer_specific"
    BUNDLE = "bundle"
    PROMOTIONAL = "promotional"
    SEASONAL = "seasonal"


class DiscountType(Enum):
    """Types of discounts"""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    TIERED = "tiered"


class PricingAdvancedService:
    """
    Advanced pricing service with dynamic rules and calculations
    """
    
    def __init__(self):
        """Initialize the advanced pricing service"""
        self.logger = logger
        self.base_service = get_pricing_service()
        self._rules_cache = {}
        self._price_history = []
        self._exchange_rates = {}

    def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        return {
            "service": "PricingAdvancedService",
            "status": "healthy",
            "base_service": self.base_service.health_check(),
            "rules_count": len(self._rules_cache),
            "timestamp": datetime.now().isoformat()
        }

    # ========================================================================
    # Dynamic Pricing Rules Engine
    # ========================================================================
    
    def create_pricing_rule(
        self,
        name: str,
        rule_type: str,
        conditions: Dict[str, Any],
        actions: Dict[str, Any],
        priority: int = 0,
        active: bool = True,
        valid_from: Optional[datetime] = None,
        valid_until: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Create a dynamic pricing rule
        
        Args:
            name: Rule name
            rule_type: Type of rule (volume_discount, time_based, etc.)
            conditions: Conditions that trigger the rule
            actions: Actions to apply when conditions are met
            priority: Rule priority (higher = applied first)
            active: Whether rule is active
            valid_from: Start date for rule validity
            valid_until: End date for rule validity
            
        Returns:
            Dictionary with rule_id and status
        """
        try:
            rule_id = f"rule_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            
            rule = {
                'id': rule_id,
                'name': name,
                'type': rule_type,
                'conditions': conditions,
                'actions': actions,
                'priority': priority,
                'active': active,
                'valid_from': valid_from.isoformat() if valid_from else None,
                'valid_until': valid_until.isoformat() if valid_until else None,
                'created_at': datetime.now().isoformat()
            }
            
            self._rules_cache[rule_id] = rule
            
            return {
                'success': True,
                'rule_id': rule_id,
                'message': f'Pricing rule "{name}" created successfully'
            }
            
        except Exception as e:
            self.logger.exception(f"Error creating pricing rule: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def apply_pricing_rules(
        self,
        base_price: float,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply all applicable pricing rules to a base price
        
        Args:
            base_price: Base price before rules
            context: Context for rule evaluation (customer, quantity, date, etc.)
            
        Returns:
            Dictionary with final price and applied rules
        """
        try:
            current_price = Decimal(str(base_price))
            applied_rules = []
            
            # Get active rules sorted by priority
            active_rules = [
                rule for rule in self._rules_cache.values()
                if rule['active'] and self._is_rule_valid(rule)
            ]
            active_rules.sort(key=lambda r: r['priority'], reverse=True)
            
            # Apply each rule
            for rule in active_rules:
                if self._evaluate_conditions(rule['conditions'], context):
                    adjustment = self._apply_rule_actions(
                        current_price,
                        rule['actions'],
                        context
                    )
                    
                    if adjustment != 0:
                        current_price += adjustment
                        applied_rules.append({
                            'rule_id': rule['id'],
                            'rule_name': rule['name'],
                            'adjustment': float(adjustment),
                            'type': rule['type']
                        })
            
            return {
                'success': True,
                'base_price': float(base_price),
                'final_price': float(current_price),
                'total_adjustment': float(current_price - Decimal(str(base_price))),
                'applied_rules': applied_rules,
                'rules_count': len(applied_rules)
            }
            
        except Exception as e:
            self.logger.exception(f"Error applying pricing rules: {e}")
            return {
                'success': False,
                'error': str(e),
                'base_price': base_price,
                'final_price': base_price
            }

    def _is_rule_valid(self, rule: Dict[str, Any]) -> bool:
        """Check if rule is currently valid based on date range"""
        now = datetime.now()
        
        if rule.get('valid_from'):
            valid_from = datetime.fromisoformat(rule['valid_from'])
            if now < valid_from:
                return False
        
        if rule.get('valid_until'):
            valid_until = datetime.fromisoformat(rule['valid_until'])
            if now > valid_until:
                return False
        
        return True
    
    def _evaluate_conditions(
        self,
        conditions: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate if conditions are met"""
        for key, condition_value in conditions.items():
            context_value = context.get(key)
            
            if isinstance(condition_value, dict):
                # Complex condition with operators
                if 'min' in condition_value and context_value < condition_value['min']:
                    return False
                if 'max' in condition_value and context_value > condition_value['max']:
                    return False
                if 'equals' in condition_value and context_value != condition_value['equals']:
                    return False
                if 'in' in condition_value and context_value not in condition_value['in']:
                    return False
            else:
                # Simple equality check
                if context_value != condition_value:
                    return False
        
        return True
    
    def _apply_rule_actions(
        self,
        current_price: Decimal,
        actions: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Decimal:
        """Apply rule actions and return price adjustment"""
        adjustment = Decimal('0')
        
        if 'discount_percentage' in actions:
            discount = current_price * Decimal(str(actions['discount_percentage'])) / Decimal('100')
            adjustment -= discount
        
        if 'discount_amount' in actions:
            adjustment -= Decimal(str(actions['discount_amount']))
        
        if 'markup_percentage' in actions:
            markup = current_price * Decimal(str(actions['markup_percentage'])) / Decimal('100')
            adjustment += markup
        
        if 'markup_amount' in actions:
            adjustment += Decimal(str(actions['markup_amount']))
        
        if 'set_price' in actions:
            adjustment = Decimal(str(actions['set_price'])) - current_price
        
        return adjustment

    # ========================================================================
    # Volume Discount Calculations
    # ========================================================================
    
    def calculate_volume_discount(
        self,
        quantity: int,
        unit_price: float,
        discount_tiers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate volume-based discount
        
        Args:
            quantity: Number of units
            unit_price: Price per unit
            discount_tiers: List of discount tiers
                Example: [
                    {'min_quantity': 10, 'discount_percentage': 5},
                    {'min_quantity': 50, 'discount_percentage': 10},
                    {'min_quantity': 100, 'discount_percentage': 15}
                ]
        
        Returns:
            Dictionary with pricing details
        """
        try:
            # Sort tiers by min_quantity descending
            sorted_tiers = sorted(
                discount_tiers,
                key=lambda t: t['min_quantity'],
                reverse=True
            )
            
            # Find applicable tier
            applicable_tier = None
            for tier in sorted_tiers:
                if quantity >= tier['min_quantity']:
                    applicable_tier = tier
                    break
            
            base_total = Decimal(str(unit_price)) * quantity
            
            if applicable_tier:
                discount_pct = Decimal(str(applicable_tier['discount_percentage']))
                discount_amount = base_total * discount_pct / Decimal('100')
                final_total = base_total - discount_amount
                
                return {
                    'success': True,
                    'quantity': quantity,
                    'unit_price': float(unit_price),
                    'base_total': float(base_total),
                    'discount_tier': applicable_tier,
                    'discount_percentage': float(discount_pct),
                    'discount_amount': float(discount_amount),
                    'final_total': float(final_total),
                    'savings': float(discount_amount)
                }
            else:
                return {
                    'success': True,
                    'quantity': quantity,
                    'unit_price': float(unit_price),
                    'base_total': float(base_total),
                    'discount_tier': None,
                    'discount_percentage': 0,
                    'discount_amount': 0,
                    'final_total': float(base_total),
                    'savings': 0
                }
            
        except Exception as e:
            self.logger.exception(f"Error calculating volume discount: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ========================================================================
    # Time-Based Pricing
    # ========================================================================
    
    def calculate_time_based_price(
        self,
        base_price: float,
        pricing_schedule: Dict[str, Any],
        target_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate price based on time/date
        
        Args:
            base_price: Base price
            pricing_schedule: Schedule with time-based adjustments
                Example: {
                    'weekday_multiplier': 1.0,
                    'weekend_multiplier': 1.1,
                    'peak_hours': {'start': 9, 'end': 17, 'multiplier': 1.2},
                    'seasonal': {
                        'summer': {'months': [6, 7, 8], 'multiplier': 1.15},
                        'winter': {'months': [12, 1, 2], 'multiplier': 0.95}
                    }
                }
            target_date: Date to calculate for (default: now)
            
        Returns:
            Dictionary with adjusted price
        """
        try:
            if target_date is None:
                target_date = datetime.now()
            
            price = Decimal(str(base_price))
            adjustments = []
            
            # Weekday/Weekend adjustment
            is_weekend = target_date.weekday() >= 5
            if is_weekend and 'weekend_multiplier' in pricing_schedule:
                multiplier = Decimal(str(pricing_schedule['weekend_multiplier']))
                price *= multiplier
                adjustments.append({
                    'type': 'weekend',
                    'multiplier': float(multiplier)
                })
            elif not is_weekend and 'weekday_multiplier' in pricing_schedule:
                multiplier = Decimal(str(pricing_schedule['weekday_multiplier']))
                price *= multiplier
                adjustments.append({
                    'type': 'weekday',
                    'multiplier': float(multiplier)
                })
            
            # Peak hours adjustment
            if 'peak_hours' in pricing_schedule:
                peak = pricing_schedule['peak_hours']
                current_hour = target_date.hour
                if peak['start'] <= current_hour < peak['end']:
                    multiplier = Decimal(str(peak['multiplier']))
                    price *= multiplier
                    adjustments.append({
                        'type': 'peak_hours',
                        'multiplier': float(multiplier)
                    })
            
            # Seasonal adjustment
            if 'seasonal' in pricing_schedule:
                current_month = target_date.month
                for season_name, season_data in pricing_schedule['seasonal'].items():
                    if current_month in season_data['months']:
                        multiplier = Decimal(str(season_data['multiplier']))
                        price *= multiplier
                        adjustments.append({
                            'type': 'seasonal',
                            'season': season_name,
                            'multiplier': float(multiplier)
                        })
                        break
            
            return {
                'success': True,
                'base_price': float(base_price),
                'final_price': float(price),
                'target_date': target_date.isoformat(),
                'adjustments': adjustments,
                'total_multiplier': float(price / Decimal(str(base_price)))
            }
            
        except Exception as e:
            self.logger.exception(f"Error calculating time-based price: {e}")
            return {
                'success': False,
                'error': str(e),
                'base_price': base_price,
                'final_price': base_price
            }

    # ========================================================================
    # Customer-Specific Pricing
    # ========================================================================
    
    def get_customer_price(
        self,
        customer_id: str,
        product_id: str,
        base_price: float,
        quantity: int = 1
    ) -> Dict[str, Any]:
        """
        Get customer-specific pricing
        
        Args:
            customer_id: Customer identifier
            product_id: Product identifier
            base_price: Base price
            quantity: Quantity
            
        Returns:
            Dictionary with customer-specific price
        """
        try:
            # Get customer pricing rules
            customer_rules = self._get_customer_pricing_rules(customer_id)
            
            if not customer_rules:
                return {
                    'success': True,
                    'customer_id': customer_id,
                    'product_id': product_id,
                    'base_price': base_price,
                    'final_price': base_price,
                    'has_custom_pricing': False
                }
            
            # Apply customer-specific rules
            context = {
                'customer_id': customer_id,
                'product_id': product_id,
                'quantity': quantity
            }
            
            result = self.apply_pricing_rules(base_price, context)
            
            return {
                'success': True,
                'customer_id': customer_id,
                'product_id': product_id,
                'base_price': base_price,
                'final_price': result['final_price'],
                'has_custom_pricing': True,
                'applied_rules': result.get('applied_rules', [])
            }
            
        except Exception as e:
            self.logger.exception(f"Error getting customer price: {e}")
            return {
                'success': False,
                'error': str(e),
                'base_price': base_price,
                'final_price': base_price
            }
    
    def _get_customer_pricing_rules(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get pricing rules for specific customer"""
        return [
            rule for rule in self._rules_cache.values()
            if rule['type'] == PricingRuleType.CUSTOMER_SPECIFIC.value
            and rule.get('conditions', {}).get('customer_id') == customer_id
        ]

    # ========================================================================
    # Bundle Pricing Logic
    # ========================================================================
    
    def calculate_bundle_price(
        self,
        items: List[Dict[str, Any]],
        bundle_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate bundle pricing
        
        Args:
            items: List of items in bundle
                Example: [
                    {'product_id': 'solar_panel', 'quantity': 20, 'unit_price': 250},
                    {'product_id': 'inverter', 'quantity': 1, 'unit_price': 1500},
                    {'product_id': 'battery', 'quantity': 1, 'unit_price': 5000}
                ]
            bundle_rules: Bundle pricing rules
                Example: {
                    'discount_percentage': 10,
                    'free_items': ['installation'],
                    'bonus_items': [{'product_id': 'warranty', 'quantity': 1}]
                }
        
        Returns:
            Dictionary with bundle pricing
        """
        try:
            # Calculate individual totals
            individual_total = Decimal('0')
            item_details = []
            
            for item in items:
                item_total = Decimal(str(item['unit_price'])) * item['quantity']
                individual_total += item_total
                
                item_details.append({
                    'product_id': item['product_id'],
                    'quantity': item['quantity'],
                    'unit_price': float(item['unit_price']),
                    'total': float(item_total)
                })
            
            # Apply bundle discount
            bundle_total = individual_total
            discount_amount = Decimal('0')
            
            if bundle_rules and 'discount_percentage' in bundle_rules:
                discount_pct = Decimal(str(bundle_rules['discount_percentage']))
                discount_amount = individual_total * discount_pct / Decimal('100')
                bundle_total = individual_total - discount_amount
            
            # Add bonus items
            bonus_items = []
            if bundle_rules and 'bonus_items' in bundle_rules:
                bonus_items = bundle_rules['bonus_items']
            
            return {
                'success': True,
                'items': item_details,
                'items_count': len(items),
                'individual_total': float(individual_total),
                'bundle_discount_percentage': float(bundle_rules.get('discount_percentage', 0)) if bundle_rules else 0,
                'bundle_discount_amount': float(discount_amount),
                'bundle_total': float(bundle_total),
                'savings': float(discount_amount),
                'bonus_items': bonus_items,
                'free_items': bundle_rules.get('free_items', []) if bundle_rules else []
            }
            
        except Exception as e:
            self.logger.exception(f"Error calculating bundle price: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ========================================================================
    # Promotional Pricing
    # ========================================================================
    
    def create_promotion(
        self,
        name: str,
        promotion_type: str,
        discount_value: float,
        valid_from: datetime,
        valid_until: datetime,
        conditions: Optional[Dict[str, Any]] = None,
        max_uses: Optional[int] = None,
        max_uses_per_customer: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a promotional pricing campaign
        
        Args:
            name: Promotion name
            promotion_type: Type (percentage, fixed_amount, buy_x_get_y)
            discount_value: Discount value
            valid_from: Start date
            valid_until: End date
            conditions: Additional conditions
            max_uses: Maximum total uses
            max_uses_per_customer: Maximum uses per customer
            
        Returns:
            Dictionary with promotion_id
        """
        try:
            promo_id = f"promo_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            
            promotion = {
                'id': promo_id,
                'name': name,
                'type': promotion_type,
                'discount_value': discount_value,
                'valid_from': valid_from.isoformat(),
                'valid_until': valid_until.isoformat(),
                'conditions': conditions or {},
                'max_uses': max_uses,
                'max_uses_per_customer': max_uses_per_customer,
                'current_uses': 0,
                'customer_uses': {},
                'created_at': datetime.now().isoformat()
            }
            
            # Create as pricing rule
            rule_result = self.create_pricing_rule(
                name=name,
                rule_type=PricingRuleType.PROMOTIONAL.value,
                conditions=conditions or {},
                actions={'discount_percentage': discount_value} if promotion_type == 'percentage' else {'discount_amount': discount_value},
                priority=100,  # High priority for promotions
                active=True,
                valid_from=valid_from,
                valid_until=valid_until
            )
            
            return {
                'success': True,
                'promotion_id': promo_id,
                'rule_id': rule_result.get('rule_id'),
                'message': f'Promotion "{name}" created successfully'
            }
            
        except Exception as e:
            self.logger.exception(f"Error creating promotion: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def apply_promotion_code(
        self,
        promo_code: str,
        base_price: float,
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Apply promotion code to price
        
        Args:
            promo_code: Promotion code
            base_price: Base price
            customer_id: Optional customer ID for tracking
            
        Returns:
            Dictionary with discounted price
        """
        try:
            # Find promotion by code
            promotion = self._find_promotion_by_code(promo_code)
            
            if not promotion:
                return {
                    'success': False,
                    'error': 'Invalid promotion code',
                    'base_price': base_price,
                    'final_price': base_price
                }
            
            # Check validity
            now = datetime.now()
            valid_from = datetime.fromisoformat(promotion['valid_from'])
            valid_until = datetime.fromisoformat(promotion['valid_until'])
            
            if now < valid_from or now > valid_until:
                return {
                    'success': False,
                    'error': 'Promotion code has expired',
                    'base_price': base_price,
                    'final_price': base_price
                }
            
            # Apply discount
            price = Decimal(str(base_price))
            
            if promotion['type'] == 'percentage':
                discount = price * Decimal(str(promotion['discount_value'])) / Decimal('100')
                final_price = price - discount
            else:  # fixed_amount
                discount = Decimal(str(promotion['discount_value']))
                final_price = price - discount
            
            return {
                'success': True,
                'promo_code': promo_code,
                'promotion_name': promotion['name'],
                'base_price': float(base_price),
                'discount_amount': float(discount),
                'final_price': float(final_price),
                'savings': float(discount)
            }
            
        except Exception as e:
            self.logger.exception(f"Error applying promotion code: {e}")
            return {
                'success': False,
                'error': str(e),
                'base_price': base_price,
                'final_price': base_price
            }
    
    def _find_promotion_by_code(self, promo_code: str) -> Optional[Dict[str, Any]]:
        """Find promotion by code"""
        # In real implementation, this would query a database
        # For now, search in rules cache
        for rule in self._rules_cache.values():
            if rule['type'] == PricingRuleType.PROMOTIONAL.value:
                if rule.get('conditions', {}).get('promo_code') == promo_code:
                    # Extract discount info from actions
                    actions = rule.get('actions', {})
                    promotion = dict(rule)
                    if 'discount_percentage' in actions:
                        promotion['type'] = 'percentage'
                        promotion['discount_value'] = actions['discount_percentage']
                    elif 'discount_amount' in actions:
                        promotion['type'] = 'fixed_amount'
                        promotion['discount_value'] = actions['discount_amount']
                    return promotion
        return None

    # ========================================================================
    # Currency Conversion
    # ========================================================================
    
    def set_exchange_rate(
        self,
        from_currency: str,
        to_currency: str,
        rate: float
    ) -> Dict[str, Any]:
        """
        Set exchange rate between currencies
        
        Args:
            from_currency: Source currency code (e.g., 'EUR')
            to_currency: Target currency code (e.g., 'USD')
            rate: Exchange rate
            
        Returns:
            Dictionary with success status
        """
        try:
            key = f"{from_currency}_{to_currency}"
            self._exchange_rates[key] = {
                'rate': rate,
                'updated_at': datetime.now().isoformat()
            }
            
            return {
                'success': True,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'rate': rate,
                'message': f'Exchange rate set: 1 {from_currency} = {rate} {to_currency}'
            }
            
        except Exception as e:
            self.logger.exception(f"Error setting exchange rate: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def convert_currency(
        self,
        amount: float,
        from_currency: str,
        to_currency: str
    ) -> Dict[str, Any]:
        """
        Convert amount from one currency to another
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Dictionary with converted amount
        """
        try:
            if from_currency == to_currency:
                return {
                    'success': True,
                    'amount': amount,
                    'from_currency': from_currency,
                    'to_currency': to_currency,
                    'converted_amount': amount,
                    'rate': 1.0
                }
            
            # Get exchange rate
            key = f"{from_currency}_{to_currency}"
            rate_data = self._exchange_rates.get(key)
            
            if not rate_data:
                # Try reverse rate
                reverse_key = f"{to_currency}_{from_currency}"
                reverse_rate_data = self._exchange_rates.get(reverse_key)
                
                if reverse_rate_data:
                    rate = 1.0 / reverse_rate_data['rate']
                else:
                    return {
                        'success': False,
                        'error': f'Exchange rate not found for {from_currency} to {to_currency}'
                    }
            else:
                rate = rate_data['rate']
            
            converted_amount = Decimal(str(amount)) * Decimal(str(rate))
            
            return {
                'success': True,
                'amount': amount,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'converted_amount': float(converted_amount),
                'rate': rate
            }
            
        except Exception as e:
            self.logger.exception(f"Error converting currency: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_multi_currency_price(
        self,
        base_price: float,
        base_currency: str,
        target_currencies: List[str]
    ) -> Dict[str, Any]:
        """
        Get price in multiple currencies
        
        Args:
            base_price: Base price
            base_currency: Base currency code
            target_currencies: List of target currency codes
            
        Returns:
            Dictionary with prices in all currencies
        """
        try:
            prices = {
                base_currency: base_price
            }
            
            for currency in target_currencies:
                if currency != base_currency:
                    result = self.convert_currency(base_price, base_currency, currency)
                    if result['success']:
                        prices[currency] = result['converted_amount']
            
            return {
                'success': True,
                'base_price': base_price,
                'base_currency': base_currency,
                'prices': prices
            }
            
        except Exception as e:
            self.logger.exception(f"Error getting multi-currency price: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ========================================================================
    # Price History Tracking
    # ========================================================================
    
    def record_price_change(
        self,
        product_id: str,
        old_price: float,
        new_price: float,
        reason: str,
        changed_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record a price change in history
        
        Args:
            product_id: Product identifier
            old_price: Previous price
            new_price: New price
            reason: Reason for change
            changed_by: User who made the change
            
        Returns:
            Dictionary with history_id
        """
        try:
            history_id = f"hist_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            
            change_record = {
                'id': history_id,
                'product_id': product_id,
                'old_price': old_price,
                'new_price': new_price,
                'change_amount': new_price - old_price,
                'change_percentage': ((new_price - old_price) / old_price * 100) if old_price > 0 else 0,
                'reason': reason,
                'changed_by': changed_by,
                'timestamp': datetime.now().isoformat()
            }
            
            self._price_history.append(change_record)
            
            return {
                'success': True,
                'history_id': history_id,
                'message': 'Price change recorded'
            }
            
        except Exception as e:
            self.logger.exception(f"Error recording price change: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_price_history(
        self,
        product_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get price change history
        
        Args:
            product_id: Optional product filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of records
            
        Returns:
            Dictionary with history records
        """
        try:
            filtered_history = self._price_history
            
            # Filter by product
            if product_id:
                filtered_history = [
                    h for h in filtered_history
                    if h['product_id'] == product_id
                ]
            
            # Filter by date range
            if start_date:
                filtered_history = [
                    h for h in filtered_history
                    if datetime.fromisoformat(h['timestamp']) >= start_date
                ]
            
            if end_date:
                filtered_history = [
                    h for h in filtered_history
                    if datetime.fromisoformat(h['timestamp']) <= end_date
                ]
            
            # Sort by timestamp descending
            filtered_history.sort(
                key=lambda h: h['timestamp'],
                reverse=True
            )
            
            # Apply limit
            filtered_history = filtered_history[:limit]
            
            return {
                'success': True,
                'history': filtered_history,
                'count': len(filtered_history)
            }
            
        except Exception as e:
            self.logger.exception(f"Error getting price history: {e}")
            return {
                'success': False,
                'error': str(e),
                'history': []
            }
    
    def get_price_trend(
        self,
        product_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get price trend analysis
        
        Args:
            product_id: Product identifier
            days: Number of days to analyze
            
        Returns:
            Dictionary with trend analysis
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            history_result = self.get_price_history(
                product_id=product_id,
                start_date=start_date
            )
            
            if not history_result['success']:
                return history_result
            
            history = history_result['history']
            
            if not history:
                return {
                    'success': True,
                    'product_id': product_id,
                    'trend': 'stable',
                    'changes_count': 0,
                    'message': 'No price changes in the specified period'
                }
            
            # Calculate trend
            total_change = sum(h['change_amount'] for h in history)
            avg_change = total_change / len(history)
            
            if avg_change > 0:
                trend = 'increasing'
            elif avg_change < 0:
                trend = 'decreasing'
            else:
                trend = 'stable'
            
            return {
                'success': True,
                'product_id': product_id,
                'period_days': days,
                'trend': trend,
                'changes_count': len(history),
                'total_change': total_change,
                'average_change': avg_change,
                'latest_price': history[0]['new_price'] if history else None,
                'oldest_price': history[-1]['old_price'] if history else None
            }
            
        except Exception as e:
            self.logger.exception(f"Error getting price trend: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
_pricing_advanced_service_instance = None


def get_pricing_advanced_service() -> PricingAdvancedService:
    """Get singleton instance of PricingAdvancedService"""
    global _pricing_advanced_service_instance
    if _pricing_advanced_service_instance is None:
        _pricing_advanced_service_instance = PricingAdvancedService()
    return _pricing_advanced_service_instance
