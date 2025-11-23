"""
Universal Dynamic Key Manager

This module provides a universal dynamic key management system that works for ALL data types
in the application, not just PV-specific data. It imports keys from diverse existing files
and manages PDF bytes for all data types.

This is the implementation of Task 124: PDF Dynamic Keys & PDF Bytes Universal System

Requirements: 1.3, 14.1, 14.2
Task: 124 - PDF Dynamic Keys & PDF Bytes Universal System
"""

import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pathlib import Path
from decimal import Decimal

# Import core infrastructure
try:
    from ...backend.core.dynamic_keys import (
        DynamicKeyMixin,
        KeyPrefix,
        DynamicKeyIndex,
        get_global_key_index
    )
    from ...backend.core.pdf_bytes import PDFByteMixin, PDFMetadata
    from ...backend.core.german_formatter import GermanNumberFormatter
except (ImportError, ValueError):
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from backend.core.dynamic_keys import (
        DynamicKeyMixin,
        KeyPrefix,
        DynamicKeyIndex,
        get_global_key_index
    )
    from backend.core.pdf_bytes import PDFByteMixin, PDFMetadata
    from backend.core.german_formatter import GermanNumberFormatter

logger = logging.getLogger(__name__)


class UniversalKeyPrefix:
    """
    Universal key prefixes for ALL data types in the application.
    
    This extends the base KeyPrefix enum with comprehensive coverage
    for all modules and data types.
    """
    
    # Solar Calculator (PV)
    PV_SYSTEM_SIZE = "PV_SYS_SIZE"
    PV_MODULE_COUNT = "PV_MOD_CNT"
    PV_ANNUAL_PRODUCTION = "PV_ANN_PROD"
    PV_SELF_CONSUMPTION = "PV_SELF_CONS"
    PV_PAYBACK_PERIOD = "PV_PAYBACK"
    PV_TOTAL_COST = "PV_COST"
    PV_SAVINGS = "PV_SAV"
    PV_CO2_SAVINGS = "PV_CO2"
    
    # Heat Pump (WP)
    HP_SYSTEM_TYPE = "HP_SYS_TYPE"
    HP_HEATING_CAPACITY = "HP_HEAT_CAP"
    HP_COP = "HP_COP"
    HP_ANNUAL_COST = "HP_ANN_COST"
    HP_SAVINGS = "HP_SAV"
    HP_EFFICIENCY = "HP_EFF"
    
    # Price Matrix
    PRICE_BASE = "PRICE_BASE"
    PRICE_MODULE = "PRICE_MOD"
    PRICE_INVERTER = "PRICE_INV"
    PRICE_BATTERY = "PRICE_BAT"
    PRICE_INSTALLATION = "PRICE_INST"
    PRICE_TOTAL = "PRICE_TOT"
    PRICE_DISCOUNT = "PRICE_DISC"
    PRICE_SURCHARGE = "PRICE_SURCH"
    
    # Products
    PRODUCT_NAME = "PROD_NAME"
    PRODUCT_MANUFACTURER = "PROD_MANUF"
    PRODUCT_POWER = "PROD_PWR"
    PRODUCT_EFFICIENCY = "PROD_EFF"
    PRODUCT_PRICE = "PROD_PRICE"
    PRODUCT_WARRANTY = "PROD_WARR"
    
    # Customer/CRM
    CUSTOMER_NAME = "CUST_NAME"
    CUSTOMER_EMAIL = "CUST_EMAIL"
    CUSTOMER_PHONE = "CUST_PHONE"
    CUSTOMER_ADDRESS = "CUST_ADDR"
    CUSTOMER_CITY = "CUST_CITY"
    CUSTOMER_POSTAL = "CUST_POST"
    
    # Project
    PROJECT_NAME = "PRJ_NAME"
    PROJECT_TYPE = "PRJ_TYPE"
    PROJECT_STATUS = "PRJ_STATUS"
    PROJECT_DATE = "PRJ_DATE"
    PROJECT_VALUE = "PRJ_VALUE"
    
    # Roof Data
    ROOF_AREA = "ROOF_AREA"
    ROOF_TYPE = "ROOF_TYPE"
    ROOF_ANGLE = "ROOF_ANG"
    ROOF_ORIENTATION = "ROOF_ORI"
    
    # 3D Visualization
    VIS_3D_MODULE_PLACEMENT = "VIS_3D_PLCMT"
    VIS_3D_ROOF_MODEL = "VIS_3D_ROOF"
    VIS_3D_EXPORT = "VIS_3D_EXP"
    
    # Charts (all 10 types)
    CHART_CIRCLE = "CHT_CIRCLE"
    CHART_DONUT = "CHT_DONUT"
    CHART_BAR = "CHT_BAR"
    CHART_COLUMN = "CHT_COLUMN"
    CHART_LINE = "CHT_LINE"
    CHART_AREA = "CHT_AREA"
    CHART_PIE = "CHT_PIE"
    CHART_POLAR = "CHT_POLAR"
    CHART_RADAR = "CHT_RADAR"
    CHART_WATERFALL = "CHT_WATERFALL"
    
    # Documents and Media
    DOC_PDF = "DOC_PDF"
    DOC_IMAGE = "DOC_IMG"
    DOC_DATASHEET = "DOC_SHEET"
    DOC_MANUAL = "DOC_MAN"
    
    # Configuration
    CONFIG_SETTING = "CFG_SET"
    CONFIG_THEME = "CFG_THEME"
    CONFIG_LANGUAGE = "CFG_LANG"
    
    # Generic
    DATA_TEXT = "DATA_TXT"
    DATA_NUMBER = "DATA_NUM"
    DATA_CURRENCY = "DATA_CUR"
    DATA_PERCENTAGE = "DATA_PCT"
    DATA_KWH = "DATA_KWH"
    DATA_YEARS = "DATA_YRS"


class UniversalDataType:
    """Enumeration of universal data types for formatting"""
    
    TEXT = "text"
    NUMBER = "number"
    INTEGER = "integer"
    FLOAT = "float"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    KWH = "kwh"
    YEARS = "years"
    DATE = "date"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    IMAGE = "image"
    DOCUMENT = "document"
    CHART = "chart"
    DIAGRAM = "diagram"
    VISUALIZATION_3D = "visualization_3d"


class UniversalDynamicKeyManager:
    """
    Universal Dynamic Key Manager for ALL data types.
    
    This manager handles:
    - Importing keys from diverse existing files (calculations.py, database.py, product_db.py, etc.)
    - Generating dynamic keys for all data types
    - Managing key-value associations with metadata
    - Providing fast lookup and retrieval
    - German formatting for all numeric types
    - PDF bytes generation for all data types
    
    Example:
        >>> manager = UniversalDynamicKeyManager()
        >>> # Import from calculations
        >>> calc_keys = manager.import_from_calculations(calculation_results)
        >>> # Import from database
        >>> db_keys = manager.import_from_database(database_records)
        >>> # Import from products
        >>> prod_keys = manager.import_from_products(product_data)
        >>> # Get formatted value
        >>> formatted = manager.get_formatted_value(key, data_type='currency')
    """
    
    def __init__(self):
        """Initialize the universal key manager"""
        self.index = get_global_key_index()
        self.formatter = GermanNumberFormatter()
        self._key_mappings: Dict[str, str] = {}
        self._source_tracking: Dict[str, str] = {}  # Track where keys came from
    
    def import_from_calculations(
        self,
        calculation_data: Dict[str, Any],
        source: str = "calculations.py"
    ) -> Dict[str, str]:
        """
        Import keys from calculation results (calculations.py, calculations_extended.py).
        
        Args:
            calculation_data: Dictionary with calculation results
            source: Source file name for tracking
            
        Returns:
            Dictionary mapping original keys to dynamic keys
        """
        key_mappings = {}
        
        # System size (kWp)
        if 'system_size' in calculation_data:
            key = self._generate_key(
                UniversalKeyPrefix.PV_SYSTEM_SIZE,
                calculation_data['system_size']
            )
            key_mappings['system_size'] = key
            self._add_to_index(
                key,
                calculation_data['system_size'],
                UniversalDataType.FLOAT,
                'kWp',
                source
            )
        
        # Module count
        if 'module_count' in calculation_data:
            key = self._generate_key(
                UniversalKeyPrefix.PV_MODULE_COUNT,
                calculation_data['module_count']
            )
            key_mappings['module_count'] = key
            self._add_to_index(
                key,
                calculation_data['module_count'],
                UniversalDataType.INTEGER,
                'pieces',
                source
            )
        
        # Annual production (kWh)
        if 'annual_production' in calculation_data:
            key = self._generate_key(
                UniversalKeyPrefix.PV_ANNUAL_PRODUCTION,
                calculation_data['annual_production']
            )
            key_mappings['annual_production'] = key
            self._add_to_index(
                key,
                calculation_data['annual_production'],
                UniversalDataType.KWH,
                'kWh',
                source
            )
        
        # Self consumption rate (%)
        if 'self_consumption_rate' in calculation_data:
            key = self._generate_key(
                UniversalKeyPrefix.PV_SELF_CONSUMPTION,
                calculation_data['self_consumption_rate']
            )
            key_mappings['self_consumption_rate'] = key
            self._add_to_index(
                key,
                calculation_data['self_consumption_rate'],
                UniversalDataType.PERCENTAGE,
                '%',
                source
            )
        
        # Payback period (years)
        if 'payback_period' in calculation_data:
            key = self._generate_key(
                UniversalKeyPrefix.PV_PAYBACK_PERIOD,
                calculation_data['payback_period']
            )
            key_mappings['payback_period'] = key
            self._add_to_index(
                key,
                calculation_data['payback_period'],
                UniversalDataType.YEARS,
                'years',
                source
            )
        
        # Total cost (€)
        if 'total_cost' in calculation_data:
            key = self._generate_key(
                UniversalKeyPrefix.PV_TOTAL_COST,
                calculation_data['total_cost']
            )
            key_mappings['total_cost'] = key
            self._add_to_index(
                key,
                calculation_data['total_cost'],
                UniversalDataType.CURRENCY,
                '€',
                source
            )
        
        # Savings
        if 'savings_25_years' in calculation_data:
            key = self._generate_key(
                UniversalKeyPrefix.PV_SAVINGS,
                calculation_data['savings_25_years']
            )
            key_mappings['savings_25_years'] = key
            self._add_to_index(
                key,
                calculation_data['savings_25_years'],
                UniversalDataType.CURRENCY,
                '€',
                source
            )
        
        # CO2 savings
        if 'co2_savings' in calculation_data:
            key = self._generate_key(
                UniversalKeyPrefix.PV_CO2_SAVINGS,
                calculation_data['co2_savings']
            )
            key_mappings['co2_savings'] = key
            self._add_to_index(
                key,
                calculation_data['co2_savings'],
                UniversalDataType.FLOAT,
                'kg CO₂',
                source
            )
        
        self._key_mappings.update(key_mappings)
        logger.info(f"Imported {len(key_mappings)} keys from {source}")
        return key_mappings
    
    def import_from_database(
        self,
        database_records: List[Dict[str, Any]],
        source: str = "database.py"
    ) -> Dict[str, str]:
        """
        Import keys from database records (database.py).
        
        Args:
            database_records: List of database records
            source: Source file name for tracking
            
        Returns:
            Dictionary mapping original keys to dynamic keys
        """
        key_mappings = {}
        
        for record in database_records:
            # Customer data
            if 'customer_name' in record:
                key = self._generate_key(
                    UniversalKeyPrefix.CUSTOMER_NAME,
                    record['customer_name']
                )
                key_mappings[f"customer_name_{record.get('id', '')}"] = key
                self._add_to_index(
                    key,
                    record['customer_name'],
                    UniversalDataType.TEXT,
                    None,
                    source
                )
            
            # Project data
            if 'project_name' in record:
                key = self._generate_key(
                    UniversalKeyPrefix.PROJECT_NAME,
                    record['project_name']
                )
                key_mappings[f"project_name_{record.get('id', '')}"] = key
                self._add_to_index(
                    key,
                    record['project_name'],
                    UniversalDataType.TEXT,
                    None,
                    source
                )
        
        self._key_mappings.update(key_mappings)
        logger.info(f"Imported {len(key_mappings)} keys from {source}")
        return key_mappings
    
    def import_from_products(
        self,
        product_data: Dict[str, Any],
        source: str = "product_db.py"
    ) -> Dict[str, str]:
        """
        Import keys from product database (product_db.py).
        
        Args:
            product_data: Dictionary with product information
            source: Source file name for tracking
            
        Returns:
            Dictionary mapping original keys to dynamic keys
        """
        key_mappings = {}
        
        # Product name
        if 'product_name' in product_data:
            key = self._generate_key(
                UniversalKeyPrefix.PRODUCT_NAME,
                product_data['product_name']
            )
            key_mappings['product_name'] = key
            self._add_to_index(
                key,
                product_data['product_name'],
                UniversalDataType.TEXT,
                None,
                source
            )
        
        # Manufacturer
        if 'manufacturer' in product_data:
            key = self._generate_key(
                UniversalKeyPrefix.PRODUCT_MANUFACTURER,
                product_data['manufacturer']
            )
            key_mappings['manufacturer'] = key
            self._add_to_index(
                key,
                product_data['manufacturer'],
                UniversalDataType.TEXT,
                None,
                source
            )
        
        # Power
        if 'power' in product_data:
            key = self._generate_key(
                UniversalKeyPrefix.PRODUCT_POWER,
                product_data['power']
            )
            key_mappings['power'] = key
            self._add_to_index(
                key,
                product_data['power'],
                UniversalDataType.FLOAT,
                'W',
                source
            )
        
        # Price
        if 'price' in product_data:
            key = self._generate_key(
                UniversalKeyPrefix.PRODUCT_PRICE,
                product_data['price']
            )
            key_mappings['price'] = key
            self._add_to_index(
                key,
                product_data['price'],
                UniversalDataType.CURRENCY,
                '€',
                source
            )
        
        self._key_mappings.update(key_mappings)
        logger.info(f"Imported {len(key_mappings)} keys from {source}")
        return key_mappings
    
    def import_from_price_matrix(
        self,
        pricing_data: Dict[str, Any],
        source: str = "price_matrix_lookup.py"
    ) -> Dict[str, str]:
        """
        Import keys from price matrix (price_matrix_*.py files).
        
        Args:
            pricing_data: Dictionary with pricing information
            source: Source file name for tracking
            
        Returns:
            Dictionary mapping original keys to dynamic keys
        """
        key_mappings = {}
        
        # Base price
        if 'base_price' in pricing_data:
            key = self._generate_key(
                UniversalKeyPrefix.PRICE_BASE,
                pricing_data['base_price']
            )
            key_mappings['base_price'] = key
            self._add_to_index(
                key,
                pricing_data['base_price'],
                UniversalDataType.CURRENCY,
                '€',
                source
            )
        
        # Total price
        if 'total_price' in pricing_data:
            key = self._generate_key(
                UniversalKeyPrefix.PRICE_TOTAL,
                pricing_data['total_price']
            )
            key_mappings['total_price'] = key
            self._add_to_index(
                key,
                pricing_data['total_price'],
                UniversalDataType.CURRENCY,
                '€',
                source
            )
        
        # Discount
        if 'discount' in pricing_data:
            key = self._generate_key(
                UniversalKeyPrefix.PRICE_DISCOUNT,
                pricing_data['discount']
            )
            key_mappings['discount'] = key
            self._add_to_index(
                key,
                pricing_data['discount'],
                UniversalDataType.CURRENCY,
                '€',
                source
            )
        
        self._key_mappings.update(key_mappings)
        logger.info(f"Imported {len(key_mappings)} keys from {source}")
        return key_mappings
    
    def import_from_3d_visualization(
        self,
        visualization_data: Dict[str, Any],
        source: str = "pv3d.py"
    ) -> Dict[str, str]:
        """
        Import keys from 3D visualization (pv3d.py, utils/pv3d_*.py).
        
        Args:
            visualization_data: Dictionary with 3D visualization data
            source: Source file name for tracking
            
        Returns:
            Dictionary mapping original keys to dynamic keys
        """
        key_mappings = {}
        
        # Module placement
        if 'module_placement' in visualization_data:
            key = self._generate_key(
                UniversalKeyPrefix.VIS_3D_MODULE_PLACEMENT,
                str(visualization_data['module_placement'])
            )
            key_mappings['module_placement'] = key
            self._add_to_index(
                key,
                visualization_data['module_placement'],
                UniversalDataType.VISUALIZATION_3D,
                None,
                source
            )
        
        # Roof model
        if 'roof_model' in visualization_data:
            key = self._generate_key(
                UniversalKeyPrefix.VIS_3D_ROOF_MODEL,
                str(visualization_data['roof_model'])
            )
            key_mappings['roof_model'] = key
            self._add_to_index(
                key,
                visualization_data['roof_model'],
                UniversalDataType.VISUALIZATION_3D,
                None,
                source
            )
        
        self._key_mappings.update(key_mappings)
        logger.info(f"Imported {len(key_mappings)} keys from {source}")
        return key_mappings
    
    def import_from_charts(
        self,
        chart_data: Dict[str, Any],
        chart_type: str,
        source: str = "charts"
    ) -> Dict[str, str]:
        """
        Import keys from chart data (all 10 chart types).
        
        Args:
            chart_data: Dictionary with chart data
            chart_type: Type of chart (CIRCLE, DONUT, BAR, etc.)
            source: Source file name for tracking
            
        Returns:
            Dictionary mapping original keys to dynamic keys
        """
        key_mappings = {}
        
        # Map chart type to prefix
        chart_prefix_map = {
            'CIRCLE': UniversalKeyPrefix.CHART_CIRCLE,
            'DONUT': UniversalKeyPrefix.CHART_DONUT,
            'BAR': UniversalKeyPrefix.CHART_BAR,
            'COLUMN': UniversalKeyPrefix.CHART_COLUMN,
            'LINE': UniversalKeyPrefix.CHART_LINE,
            'AREA': UniversalKeyPrefix.CHART_AREA,
            'PIE': UniversalKeyPrefix.CHART_PIE,
            'POLAR': UniversalKeyPrefix.CHART_POLAR,
            'RADAR': UniversalKeyPrefix.CHART_RADAR,
            'WATERFALL': UniversalKeyPrefix.CHART_WATERFALL,
        }
        
        prefix = chart_prefix_map.get(chart_type.upper(), UniversalKeyPrefix.CHART_BAR)
        
        # Generate key for chart
        key = self._generate_key(prefix, str(chart_data))
        key_mappings[f"chart_{chart_type}"] = key
        self._add_to_index(
            key,
            chart_data,
            UniversalDataType.CHART,
            chart_type,
            source
        )
        
        self._key_mappings.update(key_mappings)
        logger.info(f"Imported {len(key_mappings)} keys from {source}")
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
    
    def get_formatted_value(
        self,
        key: str,
        data_type: Optional[str] = None
    ) -> str:
        """
        Get formatted value by dynamic key with German formatting.
        
        Args:
            key: Dynamic key to lookup
            data_type: Optional data type override
            
        Returns:
            Formatted value string (German format for numbers)
        """
        value = self.index.get(key)
        metadata = self.index.get_metadata(key)
        
        if value is None:
            return ""
        
        # Determine data type
        if data_type is None and metadata:
            data_type = metadata.get('data_type')
        
        # Format based on type
        if data_type == UniversalDataType.CURRENCY:
            return self.formatter.format_currency(float(value))
        elif data_type == UniversalDataType.PERCENTAGE:
            return self.formatter.format_percent(float(value))
        elif data_type == UniversalDataType.KWH:
            return f"{self.formatter.format(float(value))} kWh"
        elif data_type == UniversalDataType.YEARS:
            return f"{self.formatter.format(float(value), 1)} Jahre"
        elif data_type in [UniversalDataType.FLOAT, UniversalDataType.NUMBER]:
            return self.formatter.format(float(value))
        elif data_type == UniversalDataType.INTEGER:
            return str(int(value))
        else:
            return str(value)
    
    def get_all_keys_by_source(self, source: str) -> List[str]:
        """
        Get all keys from a specific source file.
        
        Args:
            source: Source file name
            
        Returns:
            List of dynamic keys from that source
        """
        return [
            key for key, src in self._source_tracking.items()
            if src == source
        ]
    
    def get_all_keys_by_type(self, data_type: str) -> List[str]:
        """
        Get all keys of a specific data type.
        
        Args:
            data_type: Data type (currency, percentage, kwh, etc.)
            
        Returns:
            List of dynamic keys of that type
        """
        all_keys = []
        for key in self._key_mappings.values():
            metadata = self.index.get_metadata(key)
            if metadata and metadata.get('data_type') == data_type:
                all_keys.append(key)
        return all_keys
    
    def export_all_keys(self) -> Dict[str, Any]:
        """
        Export all keys and their values with metadata.
        
        Returns:
            Dictionary with all keys, values, and metadata
        """
        result = {}
        for original_key, dynamic_key in self._key_mappings.items():
            result[original_key] = {
                'dynamic_key': dynamic_key,
                'value': self.index.get(dynamic_key),
                'formatted_value': self.get_formatted_value(dynamic_key),
                'metadata': self.index.get_metadata(dynamic_key),
                'source': self._source_tracking.get(dynamic_key)
            }
        return result
    
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
    
    def _add_to_index(
        self,
        key: str,
        value: Any,
        data_type: str,
        unit: Optional[str],
        source: str
    ):
        """
        Add a key-value pair to the index with metadata.
        
        Args:
            key: Dynamic key
            value: Value to store
            data_type: Data type
            unit: Unit of measurement (if applicable)
            source: Source file name
        """
        metadata = {
            'data_type': data_type,
            'unit': unit,
            'source': source,
            'created_at': datetime.now().isoformat()
        }
        
        self.index.add(key, value, metadata)
        self._source_tracking[key] = source


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize universal manager
    manager = UniversalDynamicKeyManager()
    
    # Import from calculations
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
    calc_keys = manager.import_from_calculations(calculation_data)
    
    # Import from products
    product_data = {
        'product_name': 'Trina Solar TSM-400W',
        'manufacturer': 'Trina Solar',
        'power': 400.0,
        'price': 250.00
    }
    prod_keys = manager.import_from_products(product_data)
    
    # Import from price matrix
    pricing_data = {
        'base_price': 15000.00,
        'total_price': 16999.00,
        'discount': 500.00
    }
    price_keys = manager.import_from_price_matrix(pricing_data)
    
    # Export all keys
    all_keys = manager.export_all_keys()
    logger.info(f"Total keys: {len(all_keys)}")
    
    # Print formatted values
    for original_key, key_data in all_keys.items():
        logger.info(f"{original_key}: {key_data['formatted_value']} (from {key_data['source']})")
