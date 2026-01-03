"""
Product Management Service

This service wraps the legacy product_db.py module and provides
a clean API interface for product management operations.
"""

import sys
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import time
import hashlib
import json
import base64

# Add parent directory to path to import product_db module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.core.base_service import BaseService, HealthCheckResult, ServiceStatus
from backend.core.error_wrapper import handle_service_errors, ErrorContext
from backend.core.logging_decorator import log_service_call


class ProductService(BaseService):
    """
    Service wrapper for product management functionality.
    
    Wraps the legacy product_db.py module and provides:
    - Product CRUD operations
    - Product search and filtering
    - Product image upload handling
    - Product import/export functionality
    - Input validation
    - Error handling and logging
    - Health checks
    """
    
    def __init__(self):
        super().__init__("product_management")
        self._product_db_module = None
        
    def initialize(self) -> None:
        """Initialize the service and load legacy product_db module"""
        try:
            # Import the legacy product_db module
            import product_db
            self._product_db_module = product_db
            self._set_legacy_module(product_db)
            self._set_initialized(True)
            self.logger.info("Product Management Service initialized successfully")
        except ImportError as e:
            self.logger.error(f"Failed to import product_db module: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize Product Management Service: {e}")
            raise
    
    def health_check(self) -> HealthCheckResult:
        """Perform health check on the service"""
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
        
        # Check if database is available
        if not self._product_db_module.DB_AVAILABLE:
            return HealthCheckResult(
                status=ServiceStatus.DEGRADED,
                message="Database not available",
                details={"db_available": False}
            )
        
        # Check if key functions are available
        required_functions = [
            'add_product', 'update_product', 'delete_product',
            'get_product_by_id', 'list_products', 'get_product_by_model_name'
        ]
        missing_functions = []
        
        for func_name in required_functions:
            if not hasattr(self._product_db_module, func_name):
                missing_functions.append(func_name)
        
        if missing_functions:
            return HealthCheckResult(
                status=ServiceStatus.DEGRADED,
                message=f"Missing functions: {', '.join(missing_functions)}",
                details={"missing_functions": missing_functions}
            )
        
        # Try to get product count
        try:
            products = self._product_db_module.list_products()
            product_count = len(products) if products else 0
        except Exception as e:
            return HealthCheckResult(
                status=ServiceStatus.DEGRADED,
                message=f"Database query failed: {str(e)}",
                details={"error": str(e)}
            )
        
        return HealthCheckResult(
            status=ServiceStatus.HEALTHY,
            message="Service is healthy",
            details={
                "db_available": True,
                "product_count": product_count
            }
        )
    
    # ==================== CRUD Operations ====================
    
    @log_service_call(service_name="product_management", log_timing=True)
    @handle_service_errors(service_name="product_management", error_message="Failed to create product")
    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new product.
        
        Args:
            product_data: Product data dictionary
            
        Returns:
            Created product with ID
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If creation fails
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized. Call initialize() first.")
        
        # Validate required fields
        if not product_data.get('category'):
            raise ValueError("Product category is required")
        
        if not product_data.get('model_name'):
            raise ValueError("Product model_name is required")
        
        # Add product using legacy module
        product_id = self._product_db_module.add_product(product_data)
        
        if product_id is None:
            raise RuntimeError("Failed to create product. Product may already exist.")
        
        # Retrieve the created product
        created_product = self._product_db_module.get_product_by_id(product_id)
        
        if not created_product:
            raise RuntimeError(f"Product created but could not be retrieved (ID: {product_id})")
        
        self.logger.info(f"Product created successfully: {product_data.get('model_name')} (ID: {product_id})")
        
        return created_product
    
    @log_service_call(service_name="product_management", log_timing=True)
    @handle_service_errors(service_name="product_management", error_message="Failed to get product")
    def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a product by ID.
        
        Args:
            product_id: Product ID
            
        Returns:
            Product data or None if not found
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized. Call initialize() first.")
        
        product = self._product_db_module.get_product_by_id(product_id)
        
        if product:
            self.logger.info(f"Product retrieved: ID {product_id}")
        else:
            self.logger.warning(f"Product not found: ID {product_id}")
        
        return product
    
    @log_service_call(service_name="product_management", log_timing=True)
    @handle_service_errors(service_name="product_management", error_message="Failed to get product by model name")
    def get_product_by_model_name(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a product by model name.
        
        Args:
            model_name: Product model name
            
        Returns:
            Product data or None if not found
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized. Call initialize() first.")
        
        if not model_name or not model_name.strip():
            raise ValueError("Model name cannot be empty")
        
        product = self._product_db_module.get_product_by_model_name(model_name)
        
        if product:
            self.logger.info(f"Product retrieved by model name: {model_name}")
        else:
            self.logger.warning(f"Product not found by model name: {model_name}")
        
        return product
    
    @log_service_call(service_name="product_management", log_timing=True)
    @handle_service_errors(service_name="product_management", error_message="Failed to update product")
    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing product.
        
        Args:
            product_id: Product ID
            product_data: Updated product data
            
        Returns:
            Updated product data
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If update fails
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized. Call initialize() first.")
        
        # Check if product exists
        existing_product = self._product_db_module.get_product_by_id(product_id)
        if not existing_product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        # Update product using legacy module
        success = self._product_db_module.update_product(product_id, product_data)
        
        if not success:
            raise RuntimeError(f"Failed to update product ID {product_id}")
        
        # Retrieve the updated product
        updated_product = self._product_db_module.get_product_by_id(product_id)
        
        if not updated_product:
            raise RuntimeError(f"Product updated but could not be retrieved (ID: {product_id})")
        
        self.logger.info(f"Product updated successfully: ID {product_id}")
        
        return updated_product
    
    @log_service_call(service_name="product_management", log_timing=True)
    @handle_service_errors(service_name="product_management", error_message="Failed to delete product")
    def delete_product(self, product_id: int) -> bool:
        """
        Delete a product.
        
        Args:
            product_id: Product ID
            
        Returns:
            True if deleted successfully
            
        Raises:
            RuntimeError: If deletion fails
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized. Call initialize() first.")
        
        # Check if product exists
        existing_product = self._product_db_module.get_product_by_id(product_id)
        if not existing_product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        # Delete product using legacy module
        success = self._product_db_module.delete_product(product_id)
        
        if not success:
            raise RuntimeError(f"Failed to delete product ID {product_id}")
        
        self.logger.info(f"Product deleted successfully: ID {product_id}")
        
        return True
    
    # ==================== Search and Filtering ====================
    
    @log_service_call(service_name="product_management", log_timing=True)
    @handle_service_errors(service_name="product_management", error_message="Failed to list products")
    def list_products(
        self,
        category: Optional[str] = None,
        company_id: Optional[int] = None,
        search_term: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List products with optional filtering.
        
        Args:
            category: Filter by category
            company_id: Filter by company ID
            search_term: Search in model name, brand, or description
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of products
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized. Call initialize() first.")
        
        # Get products from legacy module
        products = self._product_db_module.list_products(category=category, company_id=company_id)
        
        # Apply search filter if provided
        if search_term and search_term.strip():
            search_lower = search_term.lower().strip()
            products = [
                p for p in products
                if (search_lower in (p.get('model_name') or '').lower() or
                    search_lower in (p.get('brand') or '').lower() or
                    search_lower in (p.get('description') or '').lower())
            ]
        
        # Apply pagination if provided
        if offset is not None and offset > 0:
            products = products[offset:]
        
        if limit is not None and limit > 0:
            products = products[:limit]
        
        self.logger.info(f"Listed {len(products)} products (category={category}, search={search_term})")
        
        return products
    
    @log_service_call(service_name="product_management", log_timing=True)
    @handle_service_errors(service_name="product_management", error_message="Failed to search products")
    def search_products(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Advanced product search with multiple filters.
        
        Args:
            query: Search query
            filters: Additional filters (category, price_range, etc.)
            limit: Maximum number of results
            
        Returns:
            List of matching products
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized. Call initialize() first.")
        
        filters = filters or {}
        
        # Get all products
        products = self._product_db_module.list_products(
            category=filters.get('category'),
            company_id=filters.get('company_id')
        )
        
        # Apply search query
        if query and query.strip():
            query_lower = query.lower().strip()
            products = [
                p for p in products
                if (query_lower in (p.get('model_name') or '').lower() or
                    query_lower in (p.get('brand') or '').lower() or
                    query_lower in (p.get('description') or '').lower() or
                    query_lower in (p.get('category') or '').lower())
            ]
        
        # Apply price range filter
        if 'price_min' in filters:
            products = [p for p in products if (p.get('price_euro') or 0) >= filters['price_min']]
        
        if 'price_max' in filters:
            products = [p for p in products if (p.get('price_euro') or 0) <= filters['price_max']]
        
        # Apply brand filter
        if 'brand' in filters and filters['brand']:
            brand_lower = filters['brand'].lower()
            products = [p for p in products if (p.get('brand') or '').lower() == brand_lower]
        
        # Apply limit
        products = products[:limit]
        
        self.logger.info(f"Search returned {len(products)} products for query: {query}")
        
        return products
    
    @log_service_call(service_name="product_management", log_timing=True)
    @handle_service_errors(service_name="product_management", error_message="Failed to get product categories")
    def get_categories(self) -> List[str]:
        """
        Get all product categories.
        
        Returns:
            List of category names
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized. Call initialize() first.")
        
        categories = self._product_db_module.list_product_categories()
        
        self.logger.info(f"Retrieved {len(categories)} product categories")
        
        return categories
    
    # ==================== Image Management ====================
    
    @log_service_call(service_name="product_management", log_timing=True)
    @handle_service_errors(service_name="product_management", error_message="Failed to upload product image")
    def upload_product_image(
        self,
        product_id: int,
        image_data: str,
        image_format: str = "base64"
    ) -> Dict[str, Any]:
        """
        Upload and attach an image to a product.
        
        Args:
            product_id: Product ID
            image_data: Image data (base64 encoded string or file path)
            image_format: Format of image_data ("base64" or "file_path")
            
        Returns:
            Updated product data
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If upload fails
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized. Call initialize() first.")
        
        # Check if product exists
        existing_product = self._product_db_module.get_product_by_id(product_id)
        if not existing_product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        # Process image data based on format
        if image_format == "file_path":
            # Read file and convert to base64
            if not os.path.exists(image_data):
                raise ValueError(f"Image file not found: {image_data}")
            
            with open(image_data, 'rb') as f:
                image_bytes = f.read()
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        elif image_format == "base64":
            # Use as-is
            image_base64 = image_data
        else:
            raise ValueError(f"Unsupported image format: {image_format}")
        
        # Update product image using legacy module
        success = self._product_db_module.update_product_image(product_id, image_base64)
        
        if not success:
            raise RuntimeError(f"Failed to upload image for product ID {product_id}")
        
        # Retrieve the updated product
        updated_product = self._product_db_module.get_product_by_id(product_id)
        
        if not updated_product:
            raise RuntimeError(f"Product updated but could not be retrieved (ID: {product_id})")
        
        self.logger.info(f"Image uploaded successfully for product ID {product_id}")
        
        return updated_product
    
    @log_service_call(service_name="product_management", log_timing=True)
    @handle_service_errors(service_name="product_management", error_message="Failed to delete product image")
    def delete_product_image(self, product_id: int) -> Dict[str, Any]:
        """
        Delete the image from a product.
        
        Args:
            product_id: Product ID
            
        Returns:
            Updated product data
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized. Call initialize() first.")
        
        # Check if product exists
        existing_product = self._product_db_module.get_product_by_id(product_id)
        if not existing_product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        # Remove image by setting to None
        success = self._product_db_module.update_product_image(product_id, None)
        
        if not success:
            raise RuntimeError(f"Failed to delete image for product ID {product_id}")
        
        # Retrieve the updated product
        updated_product = self._product_db_module.get_product_by_id(product_id)
        
        self.logger.info(f"Image deleted successfully for product ID {product_id}")
        
        return updated_product
    
    # ==================== Import/Export ====================
    
    @log_service_call(service_name="product_management", log_timing=True)
    @handle_service_errors(service_name="product_management", error_message="Failed to export products")
    def export_products(
        self,
        category: Optional[str] = None,
        company_id: Optional[int] = None,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Export products to various formats.
        
        Args:
            category: Filter by category
            company_id: Filter by company ID
            format: Export format ("json", "csv", "excel")
            
        Returns:
            Export data with metadata
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized. Call initialize() first.")
        
        # Get products
        products = self._product_db_module.list_products(category=category, company_id=company_id)
        
        export_data = {
            "export_date": datetime.now().isoformat(),
            "format": format,
            "product_count": len(products),
            "filters": {
                "category": category,
                "company_id": company_id
            },
            "products": products
        }
        
        if format == "json":
            # Already in JSON-compatible format
            pass
        elif format == "csv":
            # Convert to CSV format (simplified)
            export_data["csv_data"] = self._convert_to_csv(products)
        elif format == "excel":
            # Placeholder for Excel export
            export_data["excel_data"] = "Excel export not yet implemented"
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        self.logger.info(f"Exported {len(products)} products in {format} format")
        
        return export_data
    
    @log_service_call(service_name="product_management", log_timing=True)
    @handle_service_errors(service_name="product_management", error_message="Failed to import products")
    def import_products(
        self,
        import_data: Dict[str, Any],
        format: str = "json",
        update_existing: bool = False
    ) -> Dict[str, Any]:
        """
        Import products from various formats.
        
        Args:
            import_data: Import data
            format: Import format ("json", "csv", "excel")
            update_existing: Whether to update existing products
            
        Returns:
            Import results with statistics
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized. Call initialize() first.")
        
        products_to_import = []
        
        if format == "json":
            products_to_import = import_data.get("products", [])
        elif format == "csv":
            # Parse CSV data
            products_to_import = self._parse_csv(import_data.get("csv_data", ""))
        elif format == "excel":
            raise ValueError("Excel import not yet implemented")
        else:
            raise ValueError(f"Unsupported import format: {format}")
        
        # Import products
        results = {
            "total": len(products_to_import),
            "created": 0,
            "updated": 0,
            "failed": 0,
            "errors": []
        }
        
        for product_data in products_to_import:
            try:
                model_name = product_data.get('model_name')
                if not model_name:
                    results["failed"] += 1
                    results["errors"].append("Product missing model_name")
                    continue
                
                # Check if product exists
                existing = self._product_db_module.get_product_by_model_name(model_name)
                
                if existing:
                    if update_existing:
                        # Update existing product
                        success = self._product_db_module.update_product(existing['id'], product_data)
                        if success:
                            results["updated"] += 1
                        else:
                            results["failed"] += 1
                            results["errors"].append(f"Failed to update: {model_name}")
                    else:
                        results["failed"] += 1
                        results["errors"].append(f"Product already exists: {model_name}")
                else:
                    # Create new product
                    product_id = self._product_db_module.add_product(product_data)
                    if product_id:
                        results["created"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append(f"Failed to create: {model_name}")
            
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Error processing product: {str(e)}")
        
        self.logger.info(
            f"Import completed: {results['created']} created, "
            f"{results['updated']} updated, {results['failed']} failed"
        )
        
        return results
    
    # ==================== Helper Methods ====================
    
    def _convert_to_csv(self, products: List[Dict[str, Any]]) -> str:
        """Convert products to CSV format"""
        if not products:
            return ""
        
        # Get all unique keys from all products
        all_keys = set()
        for product in products:
            all_keys.update(product.keys())
        
        # Sort keys for consistent output
        headers = sorted(all_keys)
        
        # Build CSV
        lines = [",".join(headers)]
        
        for product in products:
            values = []
            for key in headers:
                value = product.get(key, "")
                # Escape commas and quotes
                if value is not None:
                    value_str = str(value).replace('"', '""')
                    if ',' in value_str or '"' in value_str:
                        value_str = f'"{value_str}"'
                    values.append(value_str)
                else:
                    values.append("")
            lines.append(",".join(values))
        
        return "\n".join(lines)
    
    def _parse_csv(self, csv_data: str) -> List[Dict[str, Any]]:
        """Parse CSV data to product dictionaries"""
        if not csv_data or not csv_data.strip():
            return []
        
        lines = csv_data.strip().split('\n')
        if len(lines) < 2:
            return []
        
        # Parse headers
        headers = [h.strip() for h in lines[0].split(',')]
        
        # Parse data rows
        products = []
        for line in lines[1:]:
            values = [v.strip().strip('"') for v in line.split(',')]
            if len(values) == len(headers):
                product = dict(zip(headers, values))
                products.append(product)
        
        return products


# Create singleton instance
_product_service_instance: Optional[ProductService] = None


def get_product_service() -> ProductService:
    """Get or create the ProductService singleton instance"""
    global _product_service_instance
    
    if _product_service_instance is None:
        _product_service_instance = ProductService()
        _product_service_instance.initialize()
    
    return _product_service_instance

    # ==================== Attribute Management Methods ====================
    
    def get_all_attributes(self) -> List[Dict[str, Any]]:
        """Get all product attributes"""
        # Mock implementation - in production, this would query the database
        return [
            {
                "id": 1,
                "name": "power_output",
                "label": "Power Output",
                "type": "number",
                "required": True,
                "unit": "kW",
                "group_id": 1,
                "group_name": "Technical Specifications",
                "order": 1,
                "is_custom": False
            },
            {
                "id": 2,
                "name": "efficiency",
                "label": "Efficiency",
                "type": "number",
                "required": True,
                "unit": "%",
                "group_id": 1,
                "group_name": "Technical Specifications",
                "order": 2,
                "is_custom": False
            }
        ]
    
    def create_attribute(self, attribute_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new product attribute"""
        # Validate required fields
        if not attribute_data.get('name'):
            raise ValueError("Attribute name is required")
        if not attribute_data.get('label'):
            raise ValueError("Attribute label is required")
        if not attribute_data.get('type'):
            raise ValueError("Attribute type is required")
        
        # Mock implementation - in production, this would insert into database
        attribute = {
            "id": 100,  # Would be auto-generated
            **attribute_data,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
        
        self.logger.info(f"Created attribute: {attribute['name']}")
        return attribute
    
    def update_attribute(self, attribute_id: int, attribute_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing product attribute"""
        # Mock implementation - in production, this would update the database
        attribute = {
            "id": attribute_id,
            **attribute_data,
            "updated_at": "2024-01-01T00:00:00"
        }
        
        self.logger.info(f"Updated attribute ID: {attribute_id}")
        return attribute
    
    def delete_attribute(self, attribute_id: int) -> bool:
        """Delete a product attribute"""
        # Mock implementation - in production, this would delete from database
        self.logger.info(f"Deleted attribute ID: {attribute_id}")
        return True
    
    # ==================== Attribute Group Methods ====================
    
    def get_all_attribute_groups(self) -> List[Dict[str, Any]]:
        """Get all attribute groups"""
        # Mock implementation
        return [
            {
                "id": 1,
                "name": "technical_specs",
                "label": "Technical Specifications",
                "description": "Technical specifications and performance data",
                "order": 1,
                "is_collapsible": True,
                "is_expanded_by_default": True
            },
            {
                "id": 2,
                "name": "physical_dimensions",
                "label": "Physical Dimensions",
                "description": "Size and weight specifications",
                "order": 2,
                "is_collapsible": True,
                "is_expanded_by_default": False
            }
        ]
    
    def create_attribute_group(self, group_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new attribute group"""
        if not group_data.get('name'):
            raise ValueError("Group name is required")
        if not group_data.get('label'):
            raise ValueError("Group label is required")
        
        group = {
            "id": 100,
            **group_data,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
        
        self.logger.info(f"Created attribute group: {group['name']}")
        return group
    
    def update_attribute_group(self, group_id: int, group_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing attribute group"""
        group = {
            "id": group_id,
            **group_data,
            "updated_at": "2024-01-01T00:00:00"
        }
        
        self.logger.info(f"Updated attribute group ID: {group_id}")
        return group
    
    def delete_attribute_group(self, group_id: int) -> bool:
        """Delete an attribute group"""
        self.logger.info(f"Deleted attribute group ID: {group_id}")
        return True
    
    # ==================== Attribute Template Methods ====================
    
    def get_all_attribute_templates(self) -> List[Dict[str, Any]]:
        """Get all attribute templates"""
        # Mock implementation
        return [
            {
                "id": 1,
                "name": "Solar Module Template",
                "description": "Standard attributes for solar modules",
                "category": "Solar Modules",
                "attributes": [1, 2, 3, 4],
                "created_at": "2024-01-01T00:00:00"
            },
            {
                "id": 2,
                "name": "Inverter Template",
                "description": "Standard attributes for inverters",
                "category": "Inverters",
                "attributes": [1, 5, 6],
                "created_at": "2024-01-01T00:00:00"
            }
        ]
    
    def create_attribute_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new attribute template"""
        if not template_data.get('name'):
            raise ValueError("Template name is required")
        if not template_data.get('category'):
            raise ValueError("Template category is required")
        if not template_data.get('attributes') or len(template_data['attributes']) == 0:
            raise ValueError("Template must include at least one attribute")
        
        template = {
            "id": 100,
            **template_data,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
        
        self.logger.info(f"Created attribute template: {template['name']}")
        return template
    
    def update_attribute_template(self, template_id: int, template_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing attribute template"""
        template = {
            "id": template_id,
            **template_data,
            "updated_at": "2024-01-01T00:00:00"
        }
        
        self.logger.info(f"Updated attribute template ID: {template_id}")
        return template
    
    def delete_attribute_template(self, template_id: int) -> bool:
        """Delete an attribute template"""
        self.logger.info(f"Deleted attribute template ID: {template_id}")
        return True


# Create singleton instance
_product_service_instance: Optional[ProductService] = None

