"""
Product Data Import/Export Service

Handles importing and exporting product data in multiple formats:
- Excel (.xlsx, .xls)
- CSV (.csv)
- XML (.xml)
- JSON (via API)

Features:
- Data validation and mapping
- Error handling and reporting
- Batch processing
- Format conversion
- API integration
"""

import pandas as pd
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Union, BinaryIO
from datetime import datetime
import io
import json
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..models.product_schemas import (
    ProductCreate,
    ProductUpdate,
    ProductImportResult,
    ProductExportFormat,
    ProductImportMapping
)
from ..models.catalog_models import Product, ProductCategory, ProductManufacturer
from ..core.errors import ValidationError, ImportError, ExportError


class ProductImportExportService:
    """Service for importing and exporting product data"""
    
    def __init__(self, db: Session):
        self.db = db
        self.supported_import_formats = ['.xlsx', '.xls', '.csv', '.xml', '.json']
        self.supported_export_formats = ['excel', 'csv', 'xml', 'json']
        
    # ==================== EXCEL IMPORT ====================
    
    def import_from_excel(
        self,
        file: BinaryIO,
        mapping: Optional[ProductImportMapping] = None,
        validate_only: bool = False
    ) -> ProductImportResult:
        """
        Import products from Excel file
        
        Args:
            file: Excel file binary stream
            mapping: Column mapping configuration
            validate_only: If True, only validate without importing
            
        Returns:
            ProductImportResult with success/error details
        """
        try:
            # Read Excel file
            df = pd.read_excel(file, sheet_name=0)
            
            # Apply column mapping if provided
            if mapping:
                df = self._apply_column_mapping(df, mapping)
            
            # Validate data
            validation_errors = self._validate_dataframe(df)
            
            if validation_errors:
                return ProductImportResult(
                    success=False,
                    total_rows=len(df),
                    imported_count=0,
                    failed_count=len(df),
                    errors=validation_errors
                )
            
            if validate_only:
                return ProductImportResult(
                    success=True,
                    total_rows=len(df),
                    imported_count=0,
                    failed_count=0,
                    message="Validation successful"
                )
            
            # Import products
            return self._import_products_from_dataframe(df)
            
        except Exception as e:
            raise ImportError(f"Excel import failed: {str(e)}")
    
    # ==================== CSV IMPORT ====================
    
    def import_from_csv(
        self,
        file: BinaryIO,
        delimiter: str = ',',
        encoding: str = 'utf-8',
        mapping: Optional[ProductImportMapping] = None,
        validate_only: bool = False
    ) -> ProductImportResult:
        """
        Import products from CSV file
        
        Args:
            file: CSV file binary stream
            delimiter: CSV delimiter character
            encoding: File encoding
            mapping: Column mapping configuration
            validate_only: If True, only validate without importing
            
        Returns:
            ProductImportResult with success/error details
        """
        try:
            # Read CSV file
            df = pd.read_csv(file, delimiter=delimiter, encoding=encoding)
            
            # Apply column mapping if provided
            if mapping:
                df = self._apply_column_mapping(df, mapping)
            
            # Validate data
            validation_errors = self._validate_dataframe(df)
            
            if validation_errors:
                return ProductImportResult(
                    success=False,
                    total_rows=len(df),
                    imported_count=0,
                    failed_count=len(df),
                    errors=validation_errors
                )
            
            if validate_only:
                return ProductImportResult(
                    success=True,
                    total_rows=len(df),
                    imported_count=0,
                    failed_count=0,
                    message="Validation successful"
                )
            
            # Import products
            return self._import_products_from_dataframe(df)
            
        except Exception as e:
            raise ImportError(f"CSV import failed: {str(e)}")
    
    # ==================== XML IMPORT ====================
    
    def import_from_xml(
        self,
        file: BinaryIO,
        root_element: str = 'products',
        product_element: str = 'product',
        validate_only: bool = False
    ) -> ProductImportResult:
        """
        Import products from XML file
        
        Args:
            file: XML file binary stream
            root_element: Root XML element name
            product_element: Product XML element name
            validate_only: If True, only validate without importing
            
        Returns:
            ProductImportResult with success/error details
        """
        try:
            # Parse XML
            tree = ET.parse(file)
            root = tree.getroot()
            
            # Extract products
            products_data = []
            for product_elem in root.findall(f'.//{product_element}'):
                product_dict = self._xml_element_to_dict(product_elem)
                products_data.append(product_dict)
            
            # Convert to DataFrame for validation
            df = pd.DataFrame(products_data)
            
            # Validate data
            validation_errors = self._validate_dataframe(df)
            
            if validation_errors:
                return ProductImportResult(
                    success=False,
                    total_rows=len(df),
                    imported_count=0,
                    failed_count=len(df),
                    errors=validation_errors
                )
            
            if validate_only:
                return ProductImportResult(
                    success=True,
                    total_rows=len(df),
                    imported_count=0,
                    failed_count=0,
                    message="Validation successful"
                )
            
            # Import products
            return self._import_products_from_dataframe(df)
            
        except Exception as e:
            raise ImportError(f"XML import failed: {str(e)}")
    
    # ==================== API INTEGRATION ====================
    
    def import_from_api(
        self,
        api_url: str,
        api_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        validate_only: bool = False
    ) -> ProductImportResult:
        """
        Import products from external API
        
        Args:
            api_url: API endpoint URL
            api_key: API authentication key
            headers: Additional HTTP headers
            params: Query parameters
            validate_only: If True, only validate without importing
            
        Returns:
            ProductImportResult with success/error details
        """
        import requests
        
        try:
            # Prepare headers
            request_headers = headers or {}
            if api_key:
                request_headers['Authorization'] = f'Bearer {api_key}'
            
            # Make API request
            response = requests.get(api_url, headers=request_headers, params=params)
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Handle different response structures
            if isinstance(data, dict) and 'products' in data:
                products_data = data['products']
            elif isinstance(data, list):
                products_data = data
            else:
                raise ImportError("Unexpected API response format")
            
            # Convert to DataFrame
            df = pd.DataFrame(products_data)
            
            # Validate data
            validation_errors = self._validate_dataframe(df)
            
            if validation_errors:
                return ProductImportResult(
                    success=False,
                    total_rows=len(df),
                    imported_count=0,
                    failed_count=len(df),
                    errors=validation_errors
                )
            
            if validate_only:
                return ProductImportResult(
                    success=True,
                    total_rows=len(df),
                    imported_count=0,
                    failed_count=0,
                    message="Validation successful"
                )
            
            # Import products
            return self._import_products_from_dataframe(df)
            
        except requests.RequestException as e:
            raise ImportError(f"API import failed: {str(e)}")
        except Exception as e:
            raise ImportError(f"API import failed: {str(e)}")
    
    # ==================== EXCEL EXPORT ====================
    
    def export_to_excel(
        self,
        filters: Optional[Dict[str, Any]] = None,
        columns: Optional[List[str]] = None,
        include_metadata: bool = True
    ) -> bytes:
        """
        Export products to Excel file
        
        Args:
            filters: Filter criteria for products
            columns: Specific columns to export
            include_metadata: Include metadata sheet
            
        Returns:
            Excel file as bytes
        """
        try:
            # Get products
            products = self._get_products_for_export(filters)
            
            # Convert to DataFrame
            df = self._products_to_dataframe(products, columns)
            
            # Create Excel file
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Products', index=False)
                
                if include_metadata:
                    metadata_df = self._create_metadata_dataframe()
                    metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            raise ExportError(f"Excel export failed: {str(e)}")
    
    # ==================== CSV EXPORT ====================
    
    def export_to_csv(
        self,
        filters: Optional[Dict[str, Any]] = None,
        columns: Optional[List[str]] = None,
        delimiter: str = ',',
        encoding: str = 'utf-8'
    ) -> bytes:
        """
        Export products to CSV file
        
        Args:
            filters: Filter criteria for products
            columns: Specific columns to export
            delimiter: CSV delimiter character
            encoding: File encoding
            
        Returns:
            CSV file as bytes
        """
        try:
            # Get products
            products = self._get_products_for_export(filters)
            
            # Convert to DataFrame
            df = self._products_to_dataframe(products, columns)
            
            # Create CSV file
            output = io.StringIO()
            df.to_csv(output, sep=delimiter, encoding=encoding, index=False)
            
            return output.getvalue().encode(encoding)
            
        except Exception as e:
            raise ExportError(f"CSV export failed: {str(e)}")
    
    # ==================== XML EXPORT ====================
    
    def export_to_xml(
        self,
        filters: Optional[Dict[str, Any]] = None,
        columns: Optional[List[str]] = None,
        root_element: str = 'products',
        product_element: str = 'product'
    ) -> bytes:
        """
        Export products to XML file
        
        Args:
            filters: Filter criteria for products
            columns: Specific columns to export
            root_element: Root XML element name
            product_element: Product XML element name
            
        Returns:
            XML file as bytes
        """
        try:
            # Get products
            products = self._get_products_for_export(filters)
            
            # Create XML structure
            root = ET.Element(root_element)
            
            for product in products:
                product_elem = ET.SubElement(root, product_element)
                product_dict = self._product_to_dict(product, columns)
                
                for key, value in product_dict.items():
                    child = ET.SubElement(product_elem, key)
                    child.text = str(value) if value is not None else ''
            
            # Convert to string
            tree = ET.ElementTree(root)
            output = io.BytesIO()
            tree.write(output, encoding='utf-8', xml_declaration=True)
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            raise ExportError(f"XML export failed: {str(e)}")
    
    # ==================== JSON EXPORT ====================
    
    def export_to_json(
        self,
        filters: Optional[Dict[str, Any]] = None,
        columns: Optional[List[str]] = None,
        pretty: bool = True
    ) -> bytes:
        """
        Export products to JSON file
        
        Args:
            filters: Filter criteria for products
            columns: Specific columns to export
            pretty: Pretty print JSON
            
        Returns:
            JSON file as bytes
        """
        try:
            # Get products
            products = self._get_products_for_export(filters)
            
            # Convert to list of dicts
            products_data = [
                self._product_to_dict(product, columns)
                for product in products
            ]
            
            # Create JSON
            indent = 2 if pretty else None
            json_str = json.dumps(products_data, indent=indent, default=str)
            
            return json_str.encode('utf-8')
            
        except Exception as e:
            raise ExportError(f"JSON export failed: {str(e)}")
    
    # ==================== HELPER METHODS ====================
    
    def _apply_column_mapping(
        self,
        df: pd.DataFrame,
        mapping: ProductImportMapping
    ) -> pd.DataFrame:
        """Apply column name mapping to DataFrame"""
        rename_dict = {}
        
        if mapping.name_column:
            rename_dict[mapping.name_column] = 'name'
        if mapping.sku_column:
            rename_dict[mapping.sku_column] = 'sku'
        if mapping.category_column:
            rename_dict[mapping.category_column] = 'category'
        if mapping.manufacturer_column:
            rename_dict[mapping.manufacturer_column] = 'manufacturer'
        if mapping.price_column:
            rename_dict[mapping.price_column] = 'price'
        if mapping.description_column:
            rename_dict[mapping.description_column] = 'description'
        
        return df.rename(columns=rename_dict)
    
    def _validate_dataframe(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Validate DataFrame for product import"""
        errors = []
        
        # Check required columns
        required_columns = ['name', 'sku']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            errors.append({
                'type': 'missing_columns',
                'message': f"Missing required columns: {', '.join(missing_columns)}"
            })
            return errors
        
        # Validate each row
        for idx, row in df.iterrows():
            row_errors = []
            
            # Validate name
            if pd.isna(row.get('name')) or not str(row.get('name')).strip():
                row_errors.append('Name is required')
            
            # Validate SKU
            if pd.isna(row.get('sku')) or not str(row.get('sku')).strip():
                row_errors.append('SKU is required')
            
            # Validate price if present
            if 'price' in row and not pd.isna(row['price']):
                try:
                    price = float(row['price'])
                    if price < 0:
                        row_errors.append('Price must be non-negative')
                except (ValueError, TypeError):
                    row_errors.append('Invalid price format')
            
            if row_errors:
                errors.append({
                    'row': idx + 2,  # +2 for header and 0-indexing
                    'errors': row_errors
                })
        
        return errors
    
    def _import_products_from_dataframe(
        self,
        df: pd.DataFrame
    ) -> ProductImportResult:
        """Import products from validated DataFrame"""
        imported_count = 0
        failed_count = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                # Create product
                product_data = self._row_to_product_data(row)
                product = Product(**product_data)
                
                self.db.add(product)
                self.db.commit()
                
                imported_count += 1
                
            except IntegrityError as e:
                self.db.rollback()
                failed_count += 1
                errors.append({
                    'row': idx + 2,
                    'error': f"Duplicate SKU or constraint violation: {str(e)}"
                })
            except Exception as e:
                self.db.rollback()
                failed_count += 1
                errors.append({
                    'row': idx + 2,
                    'error': str(e)
                })
        
        return ProductImportResult(
            success=failed_count == 0,
            total_rows=len(df),
            imported_count=imported_count,
            failed_count=failed_count,
            errors=errors if errors else None
        )
    
    def _row_to_product_data(self, row: pd.Series) -> Dict[str, Any]:
        """Convert DataFrame row to product data dictionary"""
        data = {
            'name': str(row['name']).strip(),
            'sku': str(row['sku']).strip(),
        }
        
        # Optional fields
        if 'description' in row and not pd.isna(row['description']):
            data['description'] = str(row['description']).strip()
        
        if 'price' in row and not pd.isna(row['price']):
            data['price'] = float(row['price'])
        
        if 'category' in row and not pd.isna(row['category']):
            data['category'] = str(row['category']).strip()
        
        if 'manufacturer' in row and not pd.isna(row['manufacturer']):
            data['manufacturer'] = str(row['manufacturer']).strip()
        
        # Handle specifications as JSON
        spec_columns = [col for col in row.index if col.startswith('spec_')]
        if spec_columns:
            specifications = {}
            for col in spec_columns:
                if not pd.isna(row[col]):
                    spec_name = col.replace('spec_', '')
                    specifications[spec_name] = row[col]
            if specifications:
                data['specifications'] = specifications
        
        return data
    
    def _xml_element_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """Convert XML element to dictionary"""
        result = {}
        
        for child in element:
            if len(child) == 0:  # Leaf node
                result[child.tag] = child.text
            else:  # Has children
                result[child.tag] = self._xml_element_to_dict(child)
        
        return result
    
    def _get_products_for_export(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Product]:
        """Get products for export with optional filters"""
        query = self.db.query(Product)
        
        if filters:
            if 'category' in filters:
                query = query.filter(Product.category == filters['category'])
            if 'manufacturer' in filters:
                query = query.filter(Product.manufacturer == filters['manufacturer'])
            if 'min_price' in filters:
                query = query.filter(Product.price >= filters['min_price'])
            if 'max_price' in filters:
                query = query.filter(Product.price <= filters['max_price'])
        
        return query.all()
    
    def _products_to_dataframe(
        self,
        products: List[Product],
        columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Convert products to DataFrame"""
        data = [self._product_to_dict(product, columns) for product in products]
        return pd.DataFrame(data)
    
    def _product_to_dict(
        self,
        product: Product,
        columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Convert product to dictionary"""
        data = {
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'description': product.description,
            'category': product.category,
            'manufacturer': product.manufacturer,
            'price': product.price,
            'created_at': product.created_at.isoformat() if hasattr(product, 'created_at') else None,
            'updated_at': product.updated_at.isoformat() if hasattr(product, 'updated_at') else None,
        }
        
        # Add specifications
        if hasattr(product, 'specifications') and product.specifications:
            for key, value in product.specifications.items():
                data[f'spec_{key}'] = value
        
        # Filter columns if specified
        if columns:
            data = {k: v for k, v in data.items() if k in columns}
        
        return data
    
    def _create_metadata_dataframe(self) -> pd.DataFrame:
        """Create metadata DataFrame for export"""
        metadata = {
            'Export Date': [datetime.now().isoformat()],
            'Total Products': [self.db.query(Product).count()],
            'Categories': [self.db.query(ProductCategory).count()],
            'Manufacturers': [self.db.query(ProductManufacturer).count()],
        }
        return pd.DataFrame(metadata)
