"""
PV-Specific Dynamic Key Manager

This module provides dynamic key management specifically for PV (Photovoltaic) PDF generation.
It imports keys from existing files and manages PDF bytes for all PV-related data types.

Requirements: 1.3, 4.5, 14.1, 14.2
Task: 115 - Standard PV PDF Dynamic Keys & PDF Bytes
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

# Import core dynamic key infrastructure
try:
    # Try relative import first (when used as module)
    from ...backend.core.dynamic_keys import (
        DynamicKeyMixin,
        KeyPrefix,
        DynamicKeyIndex,
        get_global_key_index
    )
    from ...backend.core.pdf_bytes import PDFByteMixin, PDFMetadata, PDFRenderingEngine
except (ImportError, ValueError):
    # Fall back to absolute import (when run directly)
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from backend.core.dynamic_keys import (
        DynamicKeyMixin,
        KeyPrefix,
        DynamicKeyIndex,
        get_global_key_index
    )
    from backend.core.pdf_bytes import PDFByteMixin, PDFMetadata, PDFRenderingEngine

logger = logging.getLogger(__name__)


class PVKeyPrefix:
    """PV-specific key prefixes extending the base KeyPrefix"""
    
    # Calculation results
    SYSTEM_SIZE = "PV_SYS_SIZE"
    MODULE_COUNT = "PV_MOD_CNT"
    ANNUAL_PRODUCTION = "PV_ANN_PROD"
    SELF_CONSUMPTION = "PV_SELF_CONS"
    PAYBACK_PERIOD = "PV_PAYBACK"
    TOTAL_COST = "PV_COST"
    SAVINGS_25Y = "PV_SAV_25Y"
    CO2_SAVINGS = "PV_CO2_SAV"
    
    # Product data
    MODULE_TYPE = "PV_MOD_TYPE"
    MODULE_POWER = "PV_MOD_PWR"
    MODULE_EFFICIENCY = "PV_MOD_EFF"
    INVERTER_TYPE = "PV_INV_TYPE"
    INVERTER_POWER = "PV_INV_PWR"
    BATTERY_TYPE = "PV_BAT_TYPE"
    BATTERY_CAPACITY = "PV_BAT_CAP"
    
    # Customer data
    CUSTOMER_NAME = "PV_CUST_NAME"
    CUSTOMER_ADDRESS = "PV_CUST_ADDR"
    CUSTOMER_CITY = "PV_CUST_CITY"
    CUSTOMER_POSTAL = "PV_CUST_POST"
    
    # Roof data
    ROOF_AREA = "PV_ROOF_AREA"
    ROOF_TYPE = "PV_ROOF_TYPE"
    ROOF_ANGLE = "PV_ROOF_ANG"
    ROOF_ORIENTATION = "PV_ROOF_ORI"
    
    # Pricing data
    BASE_PRICE = "PV_PRICE_BASE"
    MODULE_PRICE = "PV_PRICE_MOD"
    INVERTER_PRICE = "PV_PRICE_INV"
    BATTERY_PRICE = "PV_PRICE_BAT"
    INSTALLATION_PRICE = "PV_PRICE_INST"
    TOTAL_PRICE = "PV_PRICE_TOT"
    
    # 3D Visualization
    VISUALIZATION_3D = "PV_VIS_3D"
    MODULE_PLACEMENT = "PV_PLCMT"
    
    # Charts
    CHART_PRODUCTION = "PV_CHT_PROD"
    CHART_CONSUMPTION = "PV_CHT_CONS"
    CHART_SAVINGS = "PV_CHT_SAV"
    CHART_PAYBACK = "PV_CHT_PAY"
    CHART_CO2 = "PV_CHT_CO2"


class PVDataModel(DynamicKeyMixin, PDFByteMixin):
    """
    Base model for PV data with dynamic keys and PDF bytes generation.
    
    This class combines dynamic key management with PDF generation capabilities
    specifically for PV-related data.
    """
    
    def __init__(self, data: Dict[str, Any]):
        DynamicKeyMixin.__init__(self)
        PDFByteMixin.__init__(self)
        self.data = data
        self._german_formatter = GermanNumberFormatter()
    
    def _get_default_title(self) -> str:
        return "PV System Data"
    
    def _get_default_subject(self) -> str:
        return "Photovoltaic System Information"
    
    def _render_to_pdf(self, story: List, doc):
        """Render PV data to PDF"""
        from reportlab.platypus import Paragraph, Spacer, Table
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        
        styles = getSampleStyleSheet()
        
        # Add title
        story.append(Paragraph(self._get_default_title(), styles['Heading1']))
        story.append(Spacer(1, 12))
        
        # Add data as table
        table_data = [['Parameter', 'Value']]
        for key, value in self.data.items():
            formatted_value = self._format_value(value)
            table_data.append([key, formatted_value])
        
        table = Table(table_data)
        table.setStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        story.append(table)
    
    def _format_value(self, value: Any) -> str:
        """Format value with German formatting if numeric"""
        if isinstance(value, (int, float)):
            return self._german_formatter.format(value)
        return str(value)


class GermanNumberFormatter:
    """
    German number formatter for PV data.
    
    Formats numbers according to German conventions:
    - Dot (.) as thousands separator
    - Comma (,) as decimal separator
    - 2 decimal places for currency
    """
    
    @staticmethod
    def format(value: float, decimals: int = 2) -> str:
        """
        Format number in German format.
        
        Args:
            value: Number to format
            decimals: Number of decimal places
            
        Returns:
            Formatted string (e.g., "16.999,00")
        """
        formatted = f"{value:,.{decimals}f}"
        # Replace comma with temp, dot with comma, temp with dot
        return formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
    
    @staticmethod
    def format_currency(value: float) -> str:
        """
        Format currency in German format.
        
        Args:
            value: Amount to format
            
        Returns:
            Formatted string (e.g., "16.999,00 €")
        """
        formatted = GermanNumberFormatter.format(value, 2)
        return f"{formatted} €"
    
    @staticmethod
    def format_kwh(value: float) -> str:
        """
        Format kWh value in German format.
        
        Args:
            value: kWh value to format
            
        Returns:
            Formatted string (e.g., "12.500,00 kWh")
        """
        formatted = GermanNumberFormatter.format(value, 2)
        return f"{formatted} kWh"
    
    @staticmethod
    def format_percentage(value: float) -> str:
        """
        Format percentage in German format.
        
        Args:
            value: Percentage value (0-100)
            
        Returns:
            Formatted string (e.g., "85,50 %")
        """
        formatted = GermanNumberFormatter.format(value, 2)
        return f"{formatted} %"
    
    @staticmethod
    def format_years(value: float) -> str:
        """
        Format years value in German format.
        
        Args:
            value: Years value
            
        Returns:
            Formatted string (e.g., "12,5 Jahre")
        """
        formatted = GermanNumberFormatter.format(value, 1)
        return f"{formatted} Jahre"


class PVDynamicKeyManager:
    """
    Manager for PV-specific dynamic keys.
    
    This class handles:
    - Importing keys from existing files
    - Generating dynamic keys for all PV data types
    - Managing key-value associations
    - Providing fast lookup
    """
    
    def __init__(self):
        self.index = get_global_key_index()
        self.formatter = GermanNumberFormatter()
        self._key_mappings: Dict[str, str] = {}
    
    def import_calculation_keys(self, calculation_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Import keys from calculation data.
        
        Args:
            calculation_data: Dictionary with calculation results
            
        Returns:
            Dictionary mapping original keys to dynamic keys
        """
        key_mappings = {}
        
        # System size
        if 'system_size' in calculation_data:
            key = self._generate_key(PVKeyPrefix.SYSTEM_SIZE, calculation_data['system_size'])
            key_mappings['system_size'] = key
            self.index.add(key, calculation_data['system_size'], {
                'type': 'float',
                'unit': 'kWp',
                'category': 'calculation'
            })
        
        # Module count
        if 'module_count' in calculation_data:
            key = self._generate_key(PVKeyPrefix.MODULE_COUNT, calculation_data['module_count'])
            key_mappings['module_count'] = key
            self.index.add(key, calculation_data['module_count'], {
                'type': 'integer',
                'unit': 'pieces',
                'category': 'calculation'
            })
        
        # Annual production
        if 'annual_production' in calculation_data:
            key = self._generate_key(PVKeyPrefix.ANNUAL_PRODUCTION, calculation_data['annual_production'])
            key_mappings['annual_production'] = key
            self.index.add(key, calculation_data['annual_production'], {
                'type': 'float',
                'unit': 'kWh',
                'category': 'calculation'
            })
        
        # Self consumption rate
        if 'self_consumption_rate' in calculation_data:
            key = self._generate_key(PVKeyPrefix.SELF_CONSUMPTION, calculation_data['self_consumption_rate'])
            key_mappings['self_consumption_rate'] = key
            self.index.add(key, calculation_data['self_consumption_rate'], {
                'type': 'float',
                'unit': 'percentage',
                'category': 'calculation'
            })
        
        # Payback period
        if 'payback_period' in calculation_data:
            key = self._generate_key(PVKeyPrefix.PAYBACK_PERIOD, calculation_data['payback_period'])
            key_mappings['payback_period'] = key
            self.index.add(key, calculation_data['payback_period'], {
                'type': 'float',
                'unit': 'years',
                'category': 'calculation'
            })
        
        # Total cost
        if 'total_cost' in calculation_data:
            key = self._generate_key(PVKeyPrefix.TOTAL_COST, calculation_data['total_cost'])
            key_mappings['total_cost'] = key
            self.index.add(key, calculation_data['total_cost'], {
                'type': 'float',
                'unit': 'currency',
                'category': 'calculation'
            })
        
        # 25-year savings
        if 'savings_25_years' in calculation_data:
            key = self._generate_key(PVKeyPrefix.SAVINGS_25Y, calculation_data['savings_25_years'])
            key_mappings['savings_25_years'] = key
            self.index.add(key, calculation_data['savings_25_years'], {
                'type': 'float',
                'unit': 'currency',
                'category': 'calculation'
            })
        
        # CO2 savings
        if 'co2_savings' in calculation_data:
            key = self._generate_key(PVKeyPrefix.CO2_SAVINGS, calculation_data['co2_savings'])
            key_mappings['co2_savings'] = key
            self.index.add(key, calculation_data['co2_savings'], {
                'type': 'float',
                'unit': 'kg',
                'category': 'calculation'
            })
        
        self._key_mappings.update(key_mappings)
        return key_mappings
    
    def import_product_keys(self, product_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Import keys from product data.
        
        Args:
            product_data: Dictionary with product information
            
        Returns:
            Dictionary mapping original keys to dynamic keys
        """
        key_mappings = {}
        
        # Module data
        if 'module_type' in product_data:
            key = self._generate_key(PVKeyPrefix.MODULE_TYPE, product_data['module_type'])
            key_mappings['module_type'] = key
            self.index.add(key, product_data['module_type'], {
                'type': 'string',
                'category': 'product'
            })
        
        if 'module_power' in product_data:
            key = self._generate_key(PVKeyPrefix.MODULE_POWER, product_data['module_power'])
            key_mappings['module_power'] = key
            self.index.add(key, product_data['module_power'], {
                'type': 'float',
                'unit': 'Wp',
                'category': 'product'
            })
        
        # Inverter data
        if 'inverter_type' in product_data:
            key = self._generate_key(PVKeyPrefix.INVERTER_TYPE, product_data['inverter_type'])
            key_mappings['inverter_type'] = key
            self.index.add(key, product_data['inverter_type'], {
                'type': 'string',
                'category': 'product'
            })
        
        # Battery data
        if 'battery_type' in product_data:
            key = self._generate_key(PVKeyPrefix.BATTERY_TYPE, product_data['battery_type'])
            key_mappings['battery_type'] = key
            self.index.add(key, product_data['battery_type'], {
                'type': 'string',
                'category': 'product'
            })
        
        if 'battery_capacity' in product_data:
            key = self._generate_key(PVKeyPrefix.BATTERY_CAPACITY, product_data['battery_capacity'])
            key_mappings['battery_capacity'] = key
            self.index.add(key, product_data['battery_capacity'], {
                'type': 'float',
                'unit': 'kWh',
                'category': 'product'
            })
        
        self._key_mappings.update(key_mappings)
        return key_mappings
    
    def import_customer_keys(self, customer_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Import keys from customer data.
        
        Args:
            customer_data: Dictionary with customer information
            
        Returns:
            Dictionary mapping original keys to dynamic keys
        """
        key_mappings = {}
        
        if 'customer_name' in customer_data:
            key = self._generate_key(PVKeyPrefix.CUSTOMER_NAME, customer_data['customer_name'])
            key_mappings['customer_name'] = key
            self.index.add(key, customer_data['customer_name'], {
                'type': 'string',
                'category': 'customer'
            })
        
        if 'customer_address' in customer_data:
            key = self._generate_key(PVKeyPrefix.CUSTOMER_ADDRESS, customer_data['customer_address'])
            key_mappings['customer_address'] = key
            self.index.add(key, customer_data['customer_address'], {
                'type': 'string',
                'category': 'customer'
            })
        
        if 'customer_city' in customer_data:
            key = self._generate_key(PVKeyPrefix.CUSTOMER_CITY, customer_data['customer_city'])
            key_mappings['customer_city'] = key
            self.index.add(key, customer_data['customer_city'], {
                'type': 'string',
                'category': 'customer'
            })
        
        self._key_mappings.update(key_mappings)
        return key_mappings
    
    def import_pricing_keys(self, pricing_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Import keys from pricing data with German formatting.
        
        Args:
            pricing_data: Dictionary with pricing information
            
        Returns:
            Dictionary mapping original keys to dynamic keys
        """
        key_mappings = {}
        
        # Base price
        if 'base_price' in pricing_data:
            key = self._generate_key(PVKeyPrefix.BASE_PRICE, pricing_data['base_price'])
            key_mappings['base_price'] = key
            formatted_value = self.formatter.format_currency(pricing_data['base_price'])
            self.index.add(key, formatted_value, {
                'type': 'currency',
                'raw_value': pricing_data['base_price'],
                'category': 'pricing'
            })
        
        # Total price
        if 'total_price' in pricing_data:
            key = self._generate_key(PVKeyPrefix.TOTAL_PRICE, pricing_data['total_price'])
            key_mappings['total_price'] = key
            formatted_value = self.formatter.format_currency(pricing_data['total_price'])
            self.index.add(key, formatted_value, {
                'type': 'currency',
                'raw_value': pricing_data['total_price'],
                'category': 'pricing'
            })
        
        # Module price
        if 'module_price' in pricing_data:
            key = self._generate_key(PVKeyPrefix.MODULE_PRICE, pricing_data['module_price'])
            key_mappings['module_price'] = key
            formatted_value = self.formatter.format_currency(pricing_data['module_price'])
            self.index.add(key, formatted_value, {
                'type': 'currency',
                'raw_value': pricing_data['module_price'],
                'category': 'pricing'
            })
        
        # Inverter price
        if 'inverter_price' in pricing_data:
            key = self._generate_key(PVKeyPrefix.INVERTER_PRICE, pricing_data['inverter_price'])
            key_mappings['inverter_price'] = key
            formatted_value = self.formatter.format_currency(pricing_data['inverter_price'])
            self.index.add(key, formatted_value, {
                'type': 'currency',
                'raw_value': pricing_data['inverter_price'],
                'category': 'pricing'
            })
        
        # Battery price
        if 'battery_price' in pricing_data:
            key = self._generate_key(PVKeyPrefix.BATTERY_PRICE, pricing_data['battery_price'])
            key_mappings['battery_price'] = key
            formatted_value = self.formatter.format_currency(pricing_data['battery_price'])
            self.index.add(key, formatted_value, {
                'type': 'currency',
                'raw_value': pricing_data['battery_price'],
                'category': 'pricing'
            })
        
        self._key_mappings.update(key_mappings)
        return key_mappings
    
    def get_value_by_key(self, key: str) -> Any:
        """
        Get value by dynamic key.
        
        Args:
            key: Dynamic key to lookup
            
        Returns:
            Value associated with key or None
        """
        return self.index.get(key)
    
    def get_formatted_value(self, key: str) -> str:
        """
        Get formatted value by dynamic key.
        
        Args:
            key: Dynamic key to lookup
            
        Returns:
            Formatted value string
        """
        value = self.index.get(key)
        metadata = self.index.get_metadata(key)
        
        if value is None:
            return ""
        
        if metadata and 'unit' in metadata:
            unit = metadata['unit']
            if unit == 'currency':
                return str(value)  # Already formatted
            elif unit == 'kWh':
                return self.formatter.format_kwh(float(value))
            elif unit == 'percentage':
                return self.formatter.format_percentage(float(value))
            elif unit == 'years':
                return self.formatter.format_years(float(value))
        
        return str(value)
    
    def get_all_keys_by_category(self, category: str) -> List[str]:
        """
        Get all keys for a specific category.
        
        Args:
            category: Category name (e.g., 'calculation', 'product', 'pricing')
            
        Returns:
            List of dynamic keys
        """
        all_keys = []
        for prefix in [PVKeyPrefix.SYSTEM_SIZE, PVKeyPrefix.MODULE_COUNT, 
                      PVKeyPrefix.ANNUAL_PRODUCTION, PVKeyPrefix.TOTAL_PRICE]:
            keys = self.index.get_keys_by_prefix(prefix)
            for key in keys:
                metadata = self.index.get_metadata(key)
                if metadata and metadata.get('category') == category:
                    all_keys.append(key)
        return all_keys
    
    def _generate_key(self, prefix: str, value: Any) -> str:
        """
        Generate a dynamic key for a value.
        
        Args:
            prefix: Key prefix
            value: Value to generate key for
            
        Returns:
            Generated dynamic key
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Create a simple hash of the value
        value_hash = str(hash(str(value)))[-6:]
        return f"{prefix}_{timestamp}_{value_hash}"
    
    def export_all_keys(self) -> Dict[str, Any]:
        """
        Export all keys and their values.
        
        Returns:
            Dictionary with all keys and values
        """
        result = {}
        for original_key, dynamic_key in self._key_mappings.items():
            result[original_key] = {
                'dynamic_key': dynamic_key,
                'value': self.index.get(dynamic_key),
                'formatted_value': self.get_formatted_value(dynamic_key),
                'metadata': self.index.get_metadata(dynamic_key)
            }
        return result


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize manager
    manager = PVDynamicKeyManager()
    
    # Sample calculation data
    calculation_data = {
        'system_size': 10.5,
        'module_count': 30,
        'annual_production': 12500.0,
        'self_consumption_rate': 85.5,
        'payback_period': 12.5,
        'total_cost': 16999.00,
        'savings_25_years': 45000.00,
        'co2_savings': 125000.0
    }
    
    # Import keys
    calc_keys = manager.import_calculation_keys(calculation_data)
    logger.info(f"Imported {len(calc_keys)} calculation keys")
    
    # Sample pricing data
    pricing_data = {
        'base_price': 15000.00,
        'total_price': 16999.00,
        'module_price': 8000.00,
        'inverter_price': 3000.00,
        'battery_price': 5000.00
    }
    
    # Import pricing keys
    price_keys = manager.import_pricing_keys(pricing_data)
    logger.info(f"Imported {len(price_keys)} pricing keys")
    
    # Export all keys
    all_keys = manager.export_all_keys()
    logger.info(f"Total keys: {len(all_keys)}")
    
    # Print formatted values
    for original_key, key_data in all_keys.items():
        logger.info(f"{original_key}: {key_data['formatted_value']}")
