"""
Product Management Advanced Service

This service provides advanced product management features including:
- Product lifecycle management
- Product versioning
- Product comparison engine
- Product recommendations based on calculations
- Product availability tracking
- Supplier integration
- Product pricing history
- Product performance analytics
- Integration with price matrix system
"""

import sys
import os
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.core.base_service import BaseService, HealthCheckResult, ServiceStatus
from backend.core.error_wrapper import handle_service_errors
from backend.core.logging_decorator import log_service_call


class ProductLifecycleStatus(Enum):
    """Product lifecycle status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    DISCONTINUED = "discontinued"
    ARCHIVED = "archived"
    PENDING_APPROVAL = "pending_approval"


class ProductAvailabilityStatus(Enum):
    """Product availability status enumeration"""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    BACKORDERED = "backordered"
    DISCONTINUED = "discontinued"


class ProductAdvancedService(BaseService):
    """
    Advanced Product Management Service
    
    Provides advanced features for product management including:
    - Lifecycle management
    - Versioning
    - Comparison engine
    - Recommendations
    - Availability tracking
    - Supplier integration
    - Pricing history
    - Performance analytics
    """
    
    def __init__(self):
        super().__init__("product_advanced")
        self._product_db_module = None
        self._pricing_service = None
        
    def initialize(self) -> None:
        """Initialize the service"""
        try:
            # Import legacy modules
            import product_db
            self._product_db_module = product_db
            self._set_legacy_module(product_db)
            
            # Import pricing service for integration
            from backend.services.pricing_service import get_pricing_service
            self._pricing_service = get_pricing_service()
            
            self._set_initialized(True)
            self.logger.info("Product Advanced Service initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Product Advanced Service: {e}")
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
    
    # ==================== Product Lifecycle Management ====================
    
    @log_service_call(service_name="product_advanced", log_timing=True)
    @handle_service_errors(service_name="product_advanced", error_message="Failed to get product lifecycle")
    def get_product_lifecycle(self, product_id: int) -> Dict[str, Any]:
        """
        Get product lifecycle information.
        
        Args:
            product_id: Product ID
            
        Returns:
            Lifecycle information including status, dates, and history
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        product = self._product_db_module.get_product_by_id(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        # Extract lifecycle data from product
        lifecycle = {
            "product_id": product_id,
            "status": product.get("lifecycle_status", ProductLifecycleStatus.ACTIVE.value),
            "created_at": product.get("created_at"),
            "updated_at": product.get("updated_at"),
            "discontinued_at": product.get("discontinued_at"),
            "archived_at": product.get("archived_at"),
            "version": product.get("version", 1),
            "is_active": product.get("lifecycle_status") == ProductLifecycleStatus.ACTIVE.value
        }
        
        return lifecycle

    @log_service_call(service_name="product_advanced", log_timing=True)
    @handle_service_errors(service_name="product_advanced", error_message="Failed to update product lifecycle")
    def update_product_lifecycle(
        self,
        product_id: int,
        status: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update product lifecycle status.
        
        Args:
            product_id: Product ID
            status: New lifecycle status
            notes: Optional notes about the status change
            
        Returns:
            Updated lifecycle information
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        # Validate status
        try:
            lifecycle_status = ProductLifecycleStatus(status)
        except ValueError:
            raise ValueError(f"Invalid lifecycle status: {status}")
        
        # Get current product
        product = self._product_db_module.get_product_by_id(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        # Update product with new lifecycle status
        update_data = {
            "lifecycle_status": lifecycle_status.value,
            "updated_at": datetime.now().isoformat()
        }
        
        # Add timestamp for specific statuses
        if lifecycle_status == ProductLifecycleStatus.DISCONTINUED:
            update_data["discontinued_at"] = datetime.now().isoformat()
        elif lifecycle_status == ProductLifecycleStatus.ARCHIVED:
            update_data["archived_at"] = datetime.now().isoformat()
        
        success = self._product_db_module.update_product(product_id, update_data)
        if not success:
            raise RuntimeError(f"Failed to update product lifecycle for {product_id}")
        
        self.logger.info(f"Updated product {product_id} lifecycle to {status}")
        
        return self.get_product_lifecycle(product_id)
    
    # ==================== Product Versioning ====================
    
    @log_service_call(service_name="product_advanced", log_timing=True)
    @handle_service_errors(service_name="product_advanced", error_message="Failed to create product version")
    def create_product_version(
        self,
        product_id: int,
        changes: Dict[str, Any],
        version_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new version of a product.
        
        Args:
            product_id: Product ID
            changes: Changes to apply in new version
            version_notes: Notes about this version
            
        Returns:
            New version information
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        # Get current product
        product = self._product_db_module.get_product_by_id(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        # Increment version
        current_version = product.get("version", 1)
        new_version = current_version + 1
        
        # Create version record
        version_data = {
            "product_id": product_id,
            "version": new_version,
            "previous_version": current_version,
            "changes": json.dumps(changes),
            "version_notes": version_notes,
            "created_at": datetime.now().isoformat(),
            "created_by": "system"  # Would be actual user in production
        }
        
        # Update product with new version
        update_data = {
            **changes,
            "version": new_version,
            "updated_at": datetime.now().isoformat()
        }
        
        success = self._product_db_module.update_product(product_id, update_data)
        if not success:
            raise RuntimeError(f"Failed to create product version for {product_id}")
        
        self.logger.info(f"Created version {new_version} for product {product_id}")
        
        return version_data

    @log_service_call(service_name="product_advanced", log_timing=True)
    @handle_service_errors(service_name="product_advanced", error_message="Failed to get product version history")
    def get_product_version_history(
        self,
        product_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get version history for a product.
        
        Args:
            product_id: Product ID
            limit: Maximum number of versions to return
            
        Returns:
            List of version records
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        # In production, this would query a versions table
        # For now, return mock data based on product
        product = self._product_db_module.get_product_by_id(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        current_version = product.get("version", 1)
        
        # Generate version history (mock)
        versions = []
        for v in range(1, current_version + 1):
            versions.append({
                "product_id": product_id,
                "version": v,
                "created_at": product.get("created_at"),
                "changes": "Version created",
                "version_notes": f"Version {v}"
            })
        
        return versions[-limit:]
    
    # ==================== Product Comparison Engine ====================
    
    @log_service_call(service_name="product_advanced", log_timing=True)
    @handle_service_errors(service_name="product_advanced", error_message="Failed to compare products")
    def compare_products(
        self,
        product_ids: List[int],
        comparison_attributes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare multiple products across specified attributes.
        
        Args:
            product_ids: List of product IDs to compare
            comparison_attributes: Specific attributes to compare (None = all)
            
        Returns:
            Comparison matrix with products and attributes
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        if len(product_ids) < 2:
            raise ValueError("At least 2 products required for comparison")
        
        # Get all products
        products = []
        for pid in product_ids:
            product = self._product_db_module.get_product_by_id(pid)
            if product:
                products.append(product)
        
        if len(products) < 2:
            raise ValueError("Could not find enough products for comparison")
        
        # Determine attributes to compare
        if comparison_attributes is None:
            # Use common attributes across all products
            all_keys = set()
            for product in products:
                all_keys.update(product.keys())
            comparison_attributes = sorted(all_keys)
        
        # Build comparison matrix
        comparison = {
            "products": [
                {
                    "id": p["id"],
                    "model_name": p.get("model_name"),
                    "brand": p.get("brand"),
                    "category": p.get("category")
                }
                for p in products
            ],
            "attributes": {},
            "summary": {
                "total_products": len(products),
                "total_attributes": len(comparison_attributes)
            }
        }
        
        # Compare each attribute
        for attr in comparison_attributes:
            values = []
            for product in products:
                values.append({
                    "product_id": product["id"],
                    "value": product.get(attr),
                    "formatted_value": self._format_attribute_value(attr, product.get(attr))
                })
            
            comparison["attributes"][attr] = {
                "values": values,
                "has_differences": len(set(str(v["value"]) for v in values)) > 1
            }
        
        self.logger.info(f"Compared {len(products)} products across {len(comparison_attributes)} attributes")
        
        return comparison

    # ==================== Product Recommendations ====================
    
    @log_service_call(service_name="product_advanced", log_timing=True)
    @handle_service_errors(service_name="product_advanced", error_message="Failed to get product recommendations")
    def get_product_recommendations(
        self,
        calculation_context: Dict[str, Any],
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get product recommendations based on calculation context.
        
        Args:
            calculation_context: Context from solar/heatpump calculations
            category: Filter by product category
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended products with scores
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        # Get all products in category
        products = self._product_db_module.list_products(category=category)
        
        if not products:
            return []
        
        # Score each product based on calculation context
        scored_products = []
        for product in products:
            score = self._calculate_recommendation_score(product, calculation_context)
            if score > 0:
                scored_products.append({
                    **product,
                    "recommendation_score": score,
                    "recommendation_reasons": self._get_recommendation_reasons(product, calculation_context)
                })
        
        # Sort by score and return top N
        scored_products.sort(key=lambda x: x["recommendation_score"], reverse=True)
        recommendations = scored_products[:limit]
        
        self.logger.info(f"Generated {len(recommendations)} product recommendations")
        
        return recommendations
    
    def _calculate_recommendation_score(
        self,
        product: Dict[str, Any],
        context: Dict[str, Any]
    ) -> float:
        """Calculate recommendation score for a product"""
        score = 0.0
        
        # Base score for active products
        if product.get("lifecycle_status") == ProductLifecycleStatus.ACTIVE.value:
            score += 10.0
        
        # Score based on power output match (for solar modules)
        if "required_power" in context and "power_wp" in product:
            required = context["required_power"]
            actual = product["power_wp"]
            if actual:
                # Higher score for closer match
                diff_ratio = abs(actual - required) / required
                if diff_ratio < 0.1:  # Within 10%
                    score += 20.0
                elif diff_ratio < 0.2:  # Within 20%
                    score += 10.0
                elif diff_ratio < 0.5:  # Within 50%
                    score += 5.0
        
        # Score based on efficiency (for solar modules)
        if "efficiency" in product:
            efficiency = product["efficiency"]
            if efficiency:
                # Higher efficiency = higher score
                score += efficiency * 0.5
        
        # Score based on price (prefer mid-range)
        if "price_euro" in product and "budget" in context:
            price = product["price_euro"]
            budget = context["budget"]
            if price and budget:
                price_ratio = price / budget
                if 0.8 <= price_ratio <= 1.2:  # Within budget range
                    score += 15.0
                elif 0.5 <= price_ratio <= 1.5:
                    score += 10.0
                elif price_ratio < 2.0:
                    score += 5.0
        
        # Score based on brand preference
        if "preferred_brands" in context and "brand" in product:
            if product["brand"] in context["preferred_brands"]:
                score += 15.0
        
        return score
    
    def _get_recommendation_reasons(
        self,
        product: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[str]:
        """Get reasons why product is recommended"""
        reasons = []
        
        if product.get("lifecycle_status") == ProductLifecycleStatus.ACTIVE.value:
            reasons.append("Currently available")
        
        if "required_power" in context and "power_wp" in product:
            reasons.append(f"Power output: {product['power_wp']}W")
        
        if "efficiency" in product and product["efficiency"]:
            reasons.append(f"High efficiency: {product['efficiency']}%")
        
        if "preferred_brands" in context and product.get("brand") in context["preferred_brands"]:
            reasons.append(f"Preferred brand: {product['brand']}")
        
        return reasons

    # ==================== Product Availability Tracking ====================
    
    @log_service_call(service_name="product_advanced", log_timing=True)
    @handle_service_errors(service_name="product_advanced", error_message="Failed to get product availability")
    def get_product_availability(self, product_id: int) -> Dict[str, Any]:
        """
        Get product availability information.
        
        Args:
            product_id: Product ID
            
        Returns:
            Availability information including stock levels and status
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        product = self._product_db_module.get_product_by_id(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        # Extract availability data
        stock_quantity = product.get("stock_quantity", 0)
        reorder_point = product.get("reorder_point", 10)
        
        # Determine availability status
        if stock_quantity == 0:
            status = ProductAvailabilityStatus.OUT_OF_STOCK.value
        elif stock_quantity < reorder_point:
            status = ProductAvailabilityStatus.LOW_STOCK.value
        else:
            status = ProductAvailabilityStatus.IN_STOCK.value
        
        availability = {
            "product_id": product_id,
            "status": status,
            "stock_quantity": stock_quantity,
            "reorder_point": reorder_point,
            "available_quantity": max(0, stock_quantity),
            "is_available": stock_quantity > 0,
            "estimated_restock_date": product.get("estimated_restock_date"),
            "last_updated": datetime.now().isoformat()
        }
        
        return availability
    
    @log_service_call(service_name="product_advanced", log_timing=True)
    @handle_service_errors(service_name="product_advanced", error_message="Failed to update product availability")
    def update_product_availability(
        self,
        product_id: int,
        stock_quantity: Optional[int] = None,
        reorder_point: Optional[int] = None,
        estimated_restock_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update product availability information.
        
        Args:
            product_id: Product ID
            stock_quantity: New stock quantity
            reorder_point: New reorder point
            estimated_restock_date: Estimated restock date
            
        Returns:
            Updated availability information
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        update_data = {}
        
        if stock_quantity is not None:
            update_data["stock_quantity"] = stock_quantity
        
        if reorder_point is not None:
            update_data["reorder_point"] = reorder_point
        
        if estimated_restock_date is not None:
            update_data["estimated_restock_date"] = estimated_restock_date
        
        if update_data:
            success = self._product_db_module.update_product(product_id, update_data)
            if not success:
                raise RuntimeError(f"Failed to update availability for product {product_id}")
        
        return self.get_product_availability(product_id)
    
    # ==================== Supplier Integration ====================
    
    @log_service_call(service_name="product_advanced", log_timing=True)
    @handle_service_errors(service_name="product_advanced", error_message="Failed to get product suppliers")
    def get_product_suppliers(self, product_id: int) -> List[Dict[str, Any]]:
        """
        Get suppliers for a product.
        
        Args:
            product_id: Product ID
            
        Returns:
            List of suppliers with pricing and availability
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        product = self._product_db_module.get_product_by_id(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        # In production, this would query a suppliers table
        # For now, return mock supplier data
        suppliers = [
            {
                "supplier_id": 1,
                "supplier_name": "Primary Supplier",
                "product_id": product_id,
                "supplier_sku": f"SUP1-{product_id}",
                "unit_price": product.get("price_euro", 0) * 0.7,  # 30% margin
                "minimum_order_quantity": 10,
                "lead_time_days": 14,
                "is_preferred": True,
                "last_order_date": (datetime.now() - timedelta(days=30)).isoformat()
            }
        ]
        
        return suppliers

    @log_service_call(service_name="product_advanced", log_timing=True)
    @handle_service_errors(service_name="product_advanced", error_message="Failed to add product supplier")
    def add_product_supplier(
        self,
        product_id: int,
        supplier_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add a supplier for a product.
        
        Args:
            product_id: Product ID
            supplier_data: Supplier information
            
        Returns:
            Created supplier record
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        product = self._product_db_module.get_product_by_id(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        # Validate required fields
        if not supplier_data.get("supplier_name"):
            raise ValueError("Supplier name is required")
        
        # Create supplier record
        supplier = {
            "supplier_id": hash(supplier_data.get("supplier_name")) % 10000,  # Mock ID
            "product_id": product_id,
            **supplier_data,
            "created_at": datetime.now().isoformat()
        }
        
        self.logger.info(f"Added supplier {supplier['supplier_name']} for product {product_id}")
        
        return supplier
    
    # ==================== Product Pricing History ====================
    
    @log_service_call(service_name="product_advanced", log_timing=True)
    @handle_service_errors(service_name="product_advanced", error_message="Failed to get pricing history")
    def get_pricing_history(
        self,
        product_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get pricing history for a product.
        
        Args:
            product_id: Product ID
            start_date: Start date for history (ISO format)
            end_date: End date for history (ISO format)
            limit: Maximum number of records
            
        Returns:
            List of pricing history records
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        # Use the existing pricing history function from product_db
        history = self._product_db_module.get_pricing_history(product_id, limit=limit)
        
        # Filter by date range if provided
        if start_date or end_date:
            filtered_history = []
            for record in history:
                record_date = record.get("changed_at", "")
                if start_date and record_date < start_date:
                    continue
                if end_date and record_date > end_date:
                    continue
                filtered_history.append(record)
            history = filtered_history
        
        return history
    
    @log_service_call(service_name="product_advanced", log_timing=True)
    @handle_service_errors(service_name="product_advanced", error_message="Failed to analyze pricing trends")
    def analyze_pricing_trends(
        self,
        product_id: int,
        period_days: int = 90
    ) -> Dict[str, Any]:
        """
        Analyze pricing trends for a product.
        
        Args:
            product_id: Product ID
            period_days: Number of days to analyze
            
        Returns:
            Pricing trend analysis
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        # Get pricing history
        history = self.get_pricing_history(product_id, limit=100)
        
        if not history:
            return {
                "product_id": product_id,
                "has_data": False,
                "message": "No pricing history available"
            }
        
        # Calculate trends
        prices = [h.get("price_euro", 0) for h in history if h.get("price_euro")]
        
        if not prices:
            return {
                "product_id": product_id,
                "has_data": False,
                "message": "No valid price data"
            }
        
        current_price = prices[-1] if prices else 0
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
        
        # Calculate price change
        if len(prices) > 1:
            price_change = prices[-1] - prices[0]
            price_change_percent = (price_change / prices[0]) * 100 if prices[0] > 0 else 0
        else:
            price_change = 0
            price_change_percent = 0
        
        analysis = {
            "product_id": product_id,
            "has_data": True,
            "period_days": period_days,
            "current_price": current_price,
            "min_price": min_price,
            "max_price": max_price,
            "avg_price": avg_price,
            "price_change": price_change,
            "price_change_percent": price_change_percent,
            "trend": "increasing" if price_change > 0 else "decreasing" if price_change < 0 else "stable",
            "volatility": max_price - min_price,
            "data_points": len(prices)
        }
        
        return analysis

    # ==================== Product Performance Analytics ====================
    
    @log_service_call(service_name="product_advanced", log_timing=True)
    @handle_service_errors(service_name="product_advanced", error_message="Failed to get product performance")
    def get_product_performance(
        self,
        product_id: int,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get product performance analytics.
        
        Args:
            product_id: Product ID
            period_days: Analysis period in days
            
        Returns:
            Performance metrics and analytics
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        product = self._product_db_module.get_product_by_id(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        # In production, this would query sales/usage data
        # For now, return mock performance data
        performance = {
            "product_id": product_id,
            "period_days": period_days,
            "metrics": {
                "total_sales": 150,
                "total_revenue": 45000.0,
                "average_order_value": 300.0,
                "units_sold": 150,
                "return_rate": 0.02,  # 2%
                "customer_satisfaction": 4.5,  # out of 5
                "repeat_purchase_rate": 0.35  # 35%
            },
            "trends": {
                "sales_trend": "increasing",
                "revenue_trend": "increasing",
                "satisfaction_trend": "stable"
            },
            "rankings": {
                "category_rank": 3,
                "overall_rank": 15,
                "total_products": 100
            },
            "calculated_at": datetime.now().isoformat()
        }
        
        return performance
    
    @log_service_call(service_name="product_advanced", log_timing=True)
    @handle_service_errors(service_name="product_advanced", error_message="Failed to get category performance")
    def get_category_performance(
        self,
        category: str,
        period_days: int = 30,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get performance analytics for all products in a category.
        
        Args:
            category: Product category
            period_days: Analysis period in days
            limit: Number of top products to return
            
        Returns:
            Category performance with top products
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        # Get all products in category
        products = self._product_db_module.list_products(category=category)
        
        if not products:
            return {
                "category": category,
                "has_data": False,
                "message": "No products in category"
            }
        
        # Get performance for each product
        product_performances = []
        for product in products[:limit]:
            perf = self.get_product_performance(product["id"], period_days)
            product_performances.append({
                "product_id": product["id"],
                "model_name": product.get("model_name"),
                "brand": product.get("brand"),
                "performance": perf
            })
        
        # Sort by total revenue
        product_performances.sort(
            key=lambda x: x["performance"]["metrics"]["total_revenue"],
            reverse=True
        )
        
        # Calculate category totals
        total_revenue = sum(p["performance"]["metrics"]["total_revenue"] for p in product_performances)
        total_units = sum(p["performance"]["metrics"]["units_sold"] for p in product_performances)
        
        category_performance = {
            "category": category,
            "has_data": True,
            "period_days": period_days,
            "total_products": len(products),
            "analyzed_products": len(product_performances),
            "totals": {
                "total_revenue": total_revenue,
                "total_units_sold": total_units,
                "average_revenue_per_product": total_revenue / len(product_performances) if product_performances else 0
            },
            "top_products": product_performances[:limit]
        }
        
        return category_performance

    # ==================== Price Matrix Integration ====================
    
    @log_service_call(service_name="product_advanced", log_timing=True)
    @handle_service_errors(service_name="product_advanced", error_message="Failed to get product pricing from matrix")
    def get_product_pricing_from_matrix(
        self,
        product_id: int,
        quantity: int = 1,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get product pricing from price matrix system.
        
        Args:
            product_id: Product ID
            quantity: Quantity for pricing calculation
            context: Additional context for pricing (discounts, etc.)
            
        Returns:
            Pricing information from matrix
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        product = self._product_db_module.get_product_by_id(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        # Get enhanced pricing from product_db
        pricing = self._product_db_module.calculate_enhanced_product_pricing(
            product,
            quantity=quantity,
            system_context=context or {}
        )
        
        return pricing
    
    @log_service_call(service_name="product_advanced", log_timing=True)
    @handle_service_errors(service_name="product_advanced", error_message="Failed to get bulk pricing")
    def get_bulk_pricing(
        self,
        product_ids: List[int],
        quantities: Optional[List[int]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get bulk pricing for multiple products.
        
        Args:
            product_ids: List of product IDs
            quantities: List of quantities (one per product)
            context: Additional context for pricing
            
        Returns:
            Bulk pricing information
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        if quantities is None:
            quantities = [1] * len(product_ids)
        
        if len(quantities) != len(product_ids):
            raise ValueError("Quantities list must match product_ids list length")
        
        # Get pricing for each product
        product_pricing = []
        total_price = 0.0
        
        for product_id, quantity in zip(product_ids, quantities):
            pricing = self.get_product_pricing_from_matrix(product_id, quantity, context)
            product_pricing.append({
                "product_id": product_id,
                "quantity": quantity,
                "pricing": pricing
            })
            total_price += pricing.get("total_price", 0)
        
        # Calculate bulk discount if applicable
        bulk_discount_percent = 0
        if len(product_ids) >= 10:
            bulk_discount_percent = 5
        elif len(product_ids) >= 5:
            bulk_discount_percent = 3
        
        bulk_discount = total_price * (bulk_discount_percent / 100)
        final_price = total_price - bulk_discount
        
        bulk_pricing = {
            "product_count": len(product_ids),
            "total_quantity": sum(quantities),
            "product_pricing": product_pricing,
            "subtotal": total_price,
            "bulk_discount_percent": bulk_discount_percent,
            "bulk_discount": bulk_discount,
            "total_price": final_price,
            "calculated_at": datetime.now().isoformat()
        }
        
        return bulk_pricing
    
    # ==================== Helper Methods ====================
    
    def _format_attribute_value(self, attribute: str, value: Any) -> str:
        """Format attribute value for display"""
        if value is None:
            return "N/A"
        
        # Format based on attribute type
        if attribute in ["price_euro", "purchase_price_net"]:
            return f"€{value:,.2f}"
        elif attribute in ["efficiency", "margin_percent"]:
            return f"{value}%"
        elif attribute in ["power_wp", "power_output"]:
            return f"{value}W"
        elif isinstance(value, float):
            return f"{value:.2f}"
        else:
            return str(value)


# Singleton instance
_product_advanced_service_instance: Optional[ProductAdvancedService] = None


def get_product_advanced_service() -> ProductAdvancedService:
    """Get or create the ProductAdvancedService singleton instance"""
    global _product_advanced_service_instance
    
    if _product_advanced_service_instance is None:
        _product_advanced_service_instance = ProductAdvancedService()
        _product_advanced_service_instance.initialize()
    
    return _product_advanced_service_instance
