"""
Heat Pump Product Service

This service provides comprehensive heat pump product management including:
- Product data extraction and management
- Advanced filtering and search
- Product comparison
- Intelligent recommendation engine
- Availability tracking
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import math

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from solar-calculator-pro.backend.models.heatpump_product_schemas import (
    HeatPumpSpecification,
    HeatPumpFilterRequest,
    HeatPumpFilterResponse,
    HeatPumpComparisonRequest,
    HeatPumpComparisonResponse,
    HeatPumpRecommendationRequest,
    HeatPumpRecommendation,
    HeatPumpRecommendationResponse,
    HeatPumpAvailability,
    HeatPumpAvailabilityUpdate,
    HeatPumpBulkAvailabilityRequest,
    HeatPumpBulkAvailabilityResponse,
    HeatPumpType)


class HeatPumpProductService:
    """Service for managing heat pump product data"""
    
    def __init__(self):
        """Initialize the heat pump product service"""
        self.products: Dict[str, HeatPumpSpecification] = {}
        self.availability_cache: Dict[str, HeatPumpAvailability] = {}
        self._load_products()
    
    def _load_products(self):
        """Load heat pump products from database"""
        try:
            # Import the legacy heat pump products database
            from heatpump_products_database import HEATPUMP_PRODUCTS
            
            # Convert legacy format to new schema
            for manufacturer, types in HEATPUMP_PRODUCTS.items():
                for hp_type, models in types.items():
                    for model_data in models:
                        product = self._convert_legacy_product(
                            manufacturer, hp_type, model_data
                        )
                        product_id = f"{manufacturer}_{model_data.get('model', '')}".replace(" ", "_")
                        self.products[product_id] = product
                        
                        # Initialize availability
                        self.availability_cache[product_id] = HeatPumpAvailability(
                            product_id=product_id,
                            manufacturer=manufacturer,
                            model=model_data.get('model', ''),
                            available=True,
                            stock_level="in_stock",
                            lead_time_days=14)
            
            print(f"Loaded {len(self.products)} heat pump products")
        except ImportError as e:
            print(f"Warning: Could not load heat pump products database: {e}")
            self.products = {}
    
    def _convert_legacy_product(
        self, manufacturer: str, hp_type: str, model_data: Dict[str, Any]
    ) -> HeatPumpSpecification:
        """Convert legacy product format to new schema"""
        return HeatPumpSpecification(
            model=model_data.get('model', ''),
            manufacturer=manufacturer,
            heatpump_type=hp_type,
            heating_power_kw=model_data.get('heating_power_kw', []),
            cooling_power_kw=model_data.get('cooling_power_kw'),
            cop=model_data.get('cop'),
            scop=model_data.get('scop', 4.0),  # Default SCOP
            eer=model_data.get('eer'),
            seer=model_data.get('seer'),
            min_operating_temp=model_data.get('min_operating_temp'),
            max_operating_temp=model_data.get('max_operating_temp'),
            max_flow_temp=model_data.get('max_flow_temp'),
            refrigerant=model_data.get('refrigerant'),
            installation_type=model_data.get('installation_type'),
            noise_level_db=model_data.get('noise_level_db'),
            weight_kg=model_data.get('weight_kg'),
            dimensions=model_data.get('dimensions'),
            smart_grid_ready=model_data.get('smart_grid_ready', False),
            internet_connectivity=model_data.get('internet_connectivity', False),
            modulating=model_data.get('modulating', False),
            inverter_technology=model_data.get('inverter_technology', False),
            base_price=model_data.get('base_price'),
            installation_cost=model_data.get('installation_cost'),
            available=model_data.get('available', True),
            lead_time_days=model_data.get('lead_time_days', 14),
            warranty_years=model_data.get('warranty_years', 2),
            datasheet_url=model_data.get('datasheet_url'),
            image_url=model_data.get('image_url'),
            metadata=model_data.get('metadata', {}))

    # ==================== Product Retrieval ====================
    
    def get_all_products(self) -> List[HeatPumpSpecification]:
        """Get all heat pump products"""
        return list(self.products.values())
    
    def get_product_by_id(self, product_id: str) -> Optional[HeatPumpSpecification]:
        """Get a specific heat pump product by ID"""
        return self.products.get(product_id)
    
    def get_products_by_manufacturer(self, manufacturer: str) -> List[HeatPumpSpecification]:
        """Get all products from a specific manufacturer"""
        return [
            product for product in self.products.values()
            if product.manufacturer.lower() == manufacturer.lower()
        ]
    
    def get_products_by_type(self, hp_type: HeatPumpType) -> List[HeatPumpSpecification]:
        """Get all products of a specific type"""
        return [
            product for product in self.products.values()
            if product.heatpump_type == hp_type
        ]
    
    # ==================== Filtering ====================
    
    def filter_products(self, filter_request: HeatPumpFilterRequest) -> HeatPumpFilterResponse:
        """Filter heat pump products based on criteria"""
        filtered_products = list(self.products.values())
        
        # Apply manufacturer filter
        if filter_request.manufacturers:
            filtered_products = [
                p for p in filtered_products
                if p.manufacturer in filter_request.manufacturers
            ]
        
        # Apply type filter
        if filter_request.heatpump_types:
            filtered_products = [
                p for p in filtered_products
                if p.heatpump_type in filter_request.heatpump_types
            ]
        
        # Apply power range filter
        if filter_request.min_heating_power is not None:
            filtered_products = [
                p for p in filtered_products
                if max(p.heating_power_kw) >= filter_request.min_heating_power
            ]
        
        if filter_request.max_heating_power is not None:
            filtered_products = [
                p for p in filtered_products
                if min(p.heating_power_kw) <= filter_request.max_heating_power
            ]
        
        # Apply efficiency filters
        if filter_request.min_cop is not None:
            filtered_products = [
                p for p in filtered_products
                if p.cop is not None and p.cop >= filter_request.min_cop
            ]
        
        if filter_request.min_scop is not None:
            filtered_products = [
                p for p in filtered_products
                if p.scop is not None and p.scop >= filter_request.min_scop
            ]
        
        # Apply temperature filters
        if filter_request.min_operating_temp_required is not None:
            filtered_products = [
                p for p in filtered_products
                if p.min_operating_temp is not None and 
                   p.min_operating_temp <= filter_request.min_operating_temp_required
            ]
        
        if filter_request.max_flow_temp_required is not None:
            filtered_products = [
                p for p in filtered_products
                if p.max_flow_temp is not None and 
                   p.max_flow_temp >= filter_request.max_flow_temp_required
            ]
        
        # Apply feature filters
        if filter_request.smart_grid_required:
            filtered_products = [p for p in filtered_products if p.smart_grid_ready]
        
        if filter_request.internet_required:
            filtered_products = [p for p in filtered_products if p.internet_connectivity]
        
        if filter_request.inverter_required:
            filtered_products = [p for p in filtered_products if p.inverter_technology]
        
        # Apply price filter
        if filter_request.max_price is not None:
            filtered_products = [
                p for p in filtered_products
                if p.base_price is not None and p.base_price <= filter_request.max_price
            ]
        
        # Apply availability filter
        if filter_request.available_only:
            filtered_products = [p for p in filtered_products if p.available]
        
        if filter_request.max_lead_time_days is not None:
            filtered_products = [
                p for p in filtered_products
                if p.lead_time_days is not None and 
                   p.lead_time_days <= filter_request.max_lead_time_days
            ]
        
        # Sort products
        filtered_products = self._sort_products(
            filtered_products,
            filter_request.sort_by,
            filter_request.sort_order
        )
        
        # Pagination
        total_count = len(filtered_products)
        total_pages = math.ceil(total_count / filter_request.page_size)
        start_idx = (filter_request.page - 1) * filter_request.page_size
        end_idx = start_idx + filter_request.page_size
        paginated_products = filtered_products[start_idx:end_idx]
        
        return HeatPumpFilterResponse(
            products=paginated_products,
            total_count=total_count,
            page=filter_request.page,
            page_size=filter_request.page_size,
            total_pages=total_pages,
            filters_applied=filter_request.dict(exclude_none=True)
        )

    def _sort_products(
        self, products: List[HeatPumpSpecification], sort_by: str, sort_order: str
    ) -> List[HeatPumpSpecification]:
        """Sort products by specified criteria"""
        reverse = sort_order.lower() == "desc"
        
        if sort_by == "scop":
            return sorted(
                products,
                key=lambda p: p.scop if p.scop is not None else 0,
                reverse=reverse
            )
        elif sort_by == "cop":
            return sorted(
                products,
                key=lambda p: p.cop if p.cop is not None else 0,
                reverse=reverse
            )
        elif sort_by == "price":
            return sorted(
                products,
                key=lambda p: p.base_price if p.base_price is not None else float('inf'),
                reverse=reverse
            )
        elif sort_by == "power":
            return sorted(
                products,
                key=lambda p: max(p.heating_power_kw),
                reverse=reverse
            )
        else:
            return products
    
    # ==================== Comparison ====================
    
    def compare_products(
        self, comparison_request: HeatPumpComparisonRequest
    ) -> HeatPumpComparisonResponse:
        """Compare multiple heat pump products"""
        products = [
            self.products[pid] for pid in comparison_request.product_ids
            if pid in self.products
        ]
        
        if len(products) < 2:
            raise ValueError("At least 2 valid products required for comparison")
        
        # Build comparison matrix
        comparison_matrix = {}
        criteria = comparison_request.comparison_criteria or [
            "efficiency", "power", "cost", "features", "temperature_range"
        ]
        
        for criterion in criteria:
            comparison_matrix[criterion] = self._compare_criterion(products, criterion)
        
        # Determine best in each category
        best_in_category = self._determine_best_in_category(products)
        
        # Generate summary
        summary = self._generate_comparison_summary(products, comparison_matrix)
        
        return HeatPumpComparisonResponse(
            products=products,
            comparison_matrix=comparison_matrix,
            best_in_category=best_in_category,
            summary=summary
        )

    def _compare_criterion(
        self, products: List[HeatPumpSpecification], criterion: str
    ) -> Dict[str, Any]:
        """Compare products on a specific criterion"""
        result = {}
        
        if criterion == "efficiency":
            for product in products:
                product_id = f"{product.manufacturer}_{product.model}".replace(" ", "_")
                result[product_id] = {
                    "cop": product.cop,
                    "scop": product.scop,
                    "eer": product.eer,
                    "seer": product.seer,
                }
        
        elif criterion == "power":
            for product in products:
                product_id = f"{product.manufacturer}_{product.model}".replace(" ", "_")
                result[product_id] = {
                    "heating_power_range": f"{min(product.heating_power_kw)}-{max(product.heating_power_kw)} kW",
                    "max_heating_power": max(product.heating_power_kw),
                }
        
        elif criterion == "cost":
            for product in products:
                product_id = f"{product.manufacturer}_{product.model}".replace(" ", "_")
                total_cost = (product.base_price or 0) + (product.installation_cost or 0)
                result[product_id] = {
                    "base_price": product.base_price,
                    "installation_cost": product.installation_cost,
                    "total_cost": total_cost,
                }
        
        elif criterion == "features":
            for product in products:
                product_id = f"{product.manufacturer}_{product.model}".replace(" ", "_")
                result[product_id] = {
                    "smart_grid_ready": product.smart_grid_ready,
                    "internet_connectivity": product.internet_connectivity,
                    "modulating": product.modulating,
                    "inverter_technology": product.inverter_technology,
                }
        
        elif criterion == "temperature_range":
            for product in products:
                product_id = f"{product.manufacturer}_{product.model}".replace(" ", "_")
                result[product_id] = {
                    "min_operating_temp": product.min_operating_temp,
                    "max_operating_temp": product.max_operating_temp,
                    "max_flow_temp": product.max_flow_temp,
                }
        
        return result
    
    def _determine_best_in_category(
        self, products: List[HeatPumpSpecification]
    ) -> Dict[str, str]:
        """Determine the best product in each category"""
        best = {}
        
        # Best efficiency (SCOP)
        best_scop = max(products, key=lambda p: p.scop if p.scop else 0)
        best["efficiency"] = f"{best_scop.manufacturer} {best_scop.model}"
        
        # Best power
        best_power = max(products, key=lambda p: max(p.heating_power_kw))
        best["power"] = f"{best_power.manufacturer} {best_power.model}"
        
        # Best value (lowest total cost)
        products_with_price = [p for p in products if p.base_price is not None]
        if products_with_price:
            best_value = min(
                products_with_price,
                key=lambda p: (p.base_price or 0) + (p.installation_cost or 0)
            )
            best["value"] = f"{best_value.manufacturer} {best_value.model}"
        
        # Most features
        def count_features(p):
            return sum([
                p.smart_grid_ready,
                p.internet_connectivity,
                p.modulating,
                p.inverter_technology,
            ])
        
        best_features = max(products, key=count_features)
        best["features"] = f"{best_features.manufacturer} {best_features.model}"
        
        return best

    def _generate_comparison_summary(
        self, products: List[HeatPumpSpecification], comparison_matrix: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a summary of the comparison"""
        return {
            "total_products": len(products),
            "manufacturers": list(set(p.manufacturer for p in products)),
            "types": list(set(p.heatpump_type for p in products)),
            "price_range": {
                "min": min((p.base_price for p in products if p.base_price), default=None),
                "max": max((p.base_price for p in products if p.base_price), default=None),
            },
            "power_range": {
                "min": min(min(p.heating_power_kw) for p in products),
                "max": max(max(p.heating_power_kw) for p in products),
            },
            "efficiency_range": {
                "scop_min": min((p.scop for p in products if p.scop), default=None),
                "scop_max": max((p.scop for p in products if p.scop), default=None),
            },
        }
    
    # ==================== Recommendation Engine ====================
    
    def recommend_products(
        self, recommendation_request: HeatPumpRecommendationRequest
    ) -> HeatPumpRecommendationResponse:
        """Generate intelligent heat pump recommendations"""
        # Calculate heat load
        heat_load_kw = self._calculate_heat_load(recommendation_request)
        
        # Determine recommended power range (10% margin)
        recommended_power_range = {
            "min": heat_load_kw * 0.9,
            "max": heat_load_kw * 1.2,
        }
        
        # Filter suitable products
        suitable_products = self._filter_suitable_products(
            recommendation_request, heat_load_kw
        )
        
        # Score and rank products
        recommendations = []
        for product in suitable_products:
            score, reasons = self._calculate_suitability_score(
                product, recommendation_request, heat_load_kw
            )
            
            # Calculate economics
            economics = self._calculate_economics(
                product, recommendation_request, heat_load_kw
            )
            
            recommendation = HeatPumpRecommendation(
                product=product,
                suitability_score=score,
                recommendation_reasons=reasons,
                estimated_annual_cost=economics.get("annual_cost"),
                estimated_savings=economics.get("annual_savings"),
                payback_period_years=economics.get("payback_period"),
                environmental_impact=economics.get("environmental_impact"))
            recommendations.append(recommendation)
        
        # Sort by suitability score
        recommendations.sort(key=lambda r: r.suitability_score, reverse=True)
        
        # Take top 5
        recommendations = recommendations[:5]
        
        # Building analysis
        building_analysis = self._analyze_building(recommendation_request)
        
        return HeatPumpRecommendationResponse(
            recommendations=recommendations,
            building_analysis=building_analysis,
            estimated_heat_load_kw=heat_load_kw,
            recommended_power_range=recommended_power_range)

    def _calculate_heat_load(
        self, request: HeatPumpRecommendationRequest
    ) -> float:
        """Calculate building heat load in kW"""
        # Simplified heat load calculation
        # Real implementation would use detailed building physics
        
        # Base heat load per sqm based on insulation
        insulation_factors = {
            "poor": 100,  # W/sqm
            "average": 70,
            "good": 50,
            "excellent": 30,
        }
        
        base_load_w_per_sqm = insulation_factors.get(
            request.building_insulation.lower(), 70
        )
        
        # Adjust for temperature difference
        temp_diff = request.desired_indoor_temp - request.lowest_outdoor_temp
        temp_factor = temp_diff / 30  # Normalize to 30°C difference
        
        # Calculate total heat load
        heat_load_w = request.building_area_sqm * base_load_w_per_sqm * temp_factor
        heat_load_kw = heat_load_w / 1000
        
        # Add hot water load if required
        if request.hot_water_required:
            hot_water_load_kw = request.building_area_sqm * 0.01  # Rough estimate
            heat_load_kw += hot_water_load_kw
        
        return round(heat_load_kw, 2)
    
    def _filter_suitable_products(
        self, request: HeatPumpRecommendationRequest, heat_load_kw: float
    ) -> List[HeatPumpSpecification]:
        """Filter products suitable for the requirements"""
        suitable = []
        
        for product in self.products.values():
            # Check power range (allow 10% margin)
            max_power = max(product.heating_power_kw)
            if max_power < heat_load_kw * 0.9 or max_power > heat_load_kw * 1.5:
                continue
            
            # Check temperature requirements
            if product.min_operating_temp is not None:
                if product.min_operating_temp > request.lowest_outdoor_temp:
                    continue
            
            # Check cooling requirement
            if request.cooling_required and not product.cooling_power_kw:
                continue
            
            # Check budget
            if request.max_budget is not None and product.base_price is not None:
                total_cost = product.base_price + (product.installation_cost or 0)
                if total_cost > request.max_budget:
                    continue
            
            # Check availability
            if not product.available:
                continue
            
            suitable.append(product)
        
        return suitable

    def _calculate_suitability_score(
        self,
        product: HeatPumpSpecification,
        request: HeatPumpRecommendationRequest,
        heat_load_kw: float) -> Tuple[float, List[str]]:
        """Calculate suitability score (0-100) and reasons"""
        score = 0.0
        reasons = []
        
        # Power match (30 points)
        max_power = max(product.heating_power_kw)
        power_ratio = max_power / heat_load_kw
        if 0.95 <= power_ratio <= 1.15:
            score += 30
            reasons.append("Optimal power match for your heating needs")
        elif 0.9 <= power_ratio <= 1.3:
            score += 20
            reasons.append("Good power match for your heating needs")
        else:
            score += 10
        
        # Efficiency (25 points)
        if product.scop is not None:
            if request.target_scop and product.scop >= request.target_scop:
                score += 25
                reasons.append(f"Exceeds target SCOP of {request.target_scop}")
            elif product.scop >= 4.5:
                score += 25
                reasons.append(f"Excellent efficiency (SCOP: {product.scop})")
            elif product.scop >= 4.0:
                score += 20
                reasons.append(f"Very good efficiency (SCOP: {product.scop})")
            elif product.scop >= 3.5:
                score += 15
                reasons.append(f"Good efficiency (SCOP: {product.scop})")
            else:
                score += 10
        
        # Temperature capability (15 points)
        if product.min_operating_temp is not None:
            temp_margin = request.lowest_outdoor_temp - product.min_operating_temp
            if temp_margin >= 5:
                score += 15
                reasons.append(f"Operates reliably down to {product.min_operating_temp}°C")
            elif temp_margin >= 0:
                score += 10
            else:
                score += 5
        
        # Features (15 points)
        feature_score = 0
        if request.prefer_smart_features:
            if product.smart_grid_ready:
                feature_score += 5
                reasons.append("Smart grid ready for energy optimization")
            if product.internet_connectivity:
                feature_score += 5
                reasons.append("Internet connectivity for remote control")
        if product.inverter_technology:
            feature_score += 3
            reasons.append("Inverter technology for efficient operation")
        if product.modulating:
            feature_score += 2
            reasons.append("Modulating operation for comfort")
        score += min(feature_score, 15)
        
        # Noise level (10 points)
        if request.prefer_quiet and product.noise_level_db is not None:
            if product.noise_level_db <= 45:
                score += 10
                reasons.append(f"Very quiet operation ({product.noise_level_db} dB)")
            elif product.noise_level_db <= 55:
                score += 7
                reasons.append(f"Quiet operation ({product.noise_level_db} dB)")
            else:
                score += 3
        elif product.noise_level_db is not None and product.noise_level_db <= 50:
            score += 5
        
        # Value for money (5 points)
        if product.base_price is not None and product.scop is not None:
            value_ratio = product.scop / (product.base_price / 10000)
            if value_ratio >= 0.5:
                score += 5
                reasons.append("Excellent value for money")
            elif value_ratio >= 0.3:
                score += 3
        
        return round(score, 1), reasons

    def _calculate_economics(
        self,
        product: HeatPumpSpecification,
        request: HeatPumpRecommendationRequest,
        heat_load_kw: float) -> Dict[str, Any]:
        """Calculate economic metrics"""
        # Estimate annual heating hours
        heating_hours_per_year = 2000  # Typical for central Europe
        
        # Calculate annual energy consumption
        if product.scop:
            annual_energy_kwh = (heat_load_kw * heating_hours_per_year) / product.scop
        else:
            annual_energy_kwh = heat_load_kw * heating_hours_per_year / 3.5  # Default SCOP
        
        # Electricity price (EUR/kWh)
        electricity_price = 0.30
        
        # Annual operating cost
        annual_cost = annual_energy_kwh * electricity_price
        
        # Estimate savings compared to gas heating
        gas_price_per_kwh = 0.10
        gas_efficiency = 0.90
        gas_annual_cost = (heat_load_kw * heating_hours_per_year / gas_efficiency) * gas_price_per_kwh
        annual_savings = gas_annual_cost - annual_cost
        
        # Calculate payback period
        total_investment = (product.base_price or 0) + (product.installation_cost or 0)
        payback_period = total_investment / annual_savings if annual_savings > 0 else None
        
        # Environmental impact
        co2_per_kwh_electricity = 0.4  # kg CO2/kWh (grid mix)
        co2_per_kwh_gas = 0.2  # kg CO2/kWh
        annual_co2_electricity = annual_energy_kwh * co2_per_kwh_electricity
        annual_co2_gas = (heat_load_kw * heating_hours_per_year) * co2_per_kwh_gas
        co2_savings = annual_co2_gas - annual_co2_electricity
        
        return {
            "annual_cost": round(annual_cost, 2),
            "annual_savings": round(annual_savings, 2),
            "payback_period": round(payback_period, 1) if payback_period else None,
            "environmental_impact": {
                "annual_co2_kg": round(annual_co2_electricity, 0),
                "co2_savings_vs_gas_kg": round(co2_savings, 0),
            },
        }
    
    def _analyze_building(
        self, request: HeatPumpRecommendationRequest
    ) -> Dict[str, Any]:
        """Analyze building characteristics"""
        return {
            "building_area_sqm": request.building_area_sqm,
            "insulation_quality": request.building_insulation,
            "climate_zone": request.climate_zone,
            "temperature_requirements": {
                "indoor": request.desired_indoor_temp,
                "lowest_outdoor": request.lowest_outdoor_temp,
                "temperature_difference": request.desired_indoor_temp - request.lowest_outdoor_temp,
            },
            "system_requirements": {
                "hot_water": request.hot_water_required,
                "cooling": request.cooling_required,
                "existing_system": request.existing_heating_system,
                "radiator_type": request.radiator_type,
            },
        }
    
    # ==================== Availability Tracking ====================
    
    def get_availability(self, product_id: str) -> Optional[HeatPumpAvailability]:
        """Get availability information for a product"""
        return self.availability_cache.get(product_id)
    
    def update_availability(
        self, availability_update: HeatPumpAvailabilityUpdate
    ) -> HeatPumpAvailability:
        """Update product availability"""
        product_id = availability_update.product_id
        
        if product_id not in self.products:
            raise ValueError(f"Product {product_id} not found")
        
        product = self.products[product_id]
        
        # Update or create availability record
        if product_id in self.availability_cache:
            availability = self.availability_cache[product_id]
            availability.available = availability_update.available
            if availability_update.stock_level:
                availability.stock_level = availability_update.stock_level
            if availability_update.lead_time_days is not None:
                availability.lead_time_days = availability_update.lead_time_days
            if availability_update.next_delivery_date:
                availability.next_delivery_date = availability_update.next_delivery_date
            availability.last_updated = datetime.now()
        else:
            availability = HeatPumpAvailability(
                product_id=product_id,
                manufacturer=product.manufacturer,
                model=product.model,
                available=availability_update.available,
                stock_level=availability_update.stock_level,
                lead_time_days=availability_update.lead_time_days,
                next_delivery_date=availability_update.next_delivery_date)
            self.availability_cache[product_id] = availability
        
        # Update product availability
        product.available = availability_update.available
        if availability_update.lead_time_days is not None:
            product.lead_time_days = availability_update.lead_time_days
        
        return availability

    def check_bulk_availability(
        self, bulk_request: HeatPumpBulkAvailabilityRequest
    ) -> HeatPumpBulkAvailabilityResponse:
        """Check availability for multiple products"""
        availability_list = []
        available_count = 0
        unavailable_count = 0
        low_stock_count = 0
        
        for product_id in bulk_request.product_ids:
            availability = self.get_availability(product_id)
            if availability:
                availability_list.append(availability)
                if availability.available:
                    available_count += 1
                    if availability.stock_level == "low_stock":
                        low_stock_count += 1
                else:
                    unavailable_count += 1
        
        summary = {
            "total_checked": len(bulk_request.product_ids),
            "available_count": available_count,
            "unavailable_count": unavailable_count,
            "low_stock_count": low_stock_count,
        }
        
        return HeatPumpBulkAvailabilityResponse(
            availability=availability_list,
            summary=summary
        )
    
    def suggest_alternatives(self, product_id: str, max_alternatives: int = 3) -> List[str]:
        """Suggest alternative products when one is unavailable"""
        if product_id not in self.products:
            return []
        
        original_product = self.products[product_id]
        
        # Find similar products
        alternatives = []
        for pid, product in self.products.items():
            if pid == product_id:
                continue
            
            # Check if available
            if not product.available:
                continue
            
            # Calculate similarity score
            similarity = 0
            
            # Same type
            if product.heatpump_type == original_product.heatpump_type:
                similarity += 30
            
            # Similar power
            orig_power = max(original_product.heating_power_kw)
            prod_power = max(product.heating_power_kw)
            power_diff = abs(orig_power - prod_power) / orig_power
            if power_diff < 0.1:
                similarity += 30
            elif power_diff < 0.2:
                similarity += 20
            elif power_diff < 0.3:
                similarity += 10
            
            # Similar efficiency
            if original_product.scop and product.scop:
                scop_diff = abs(original_product.scop - product.scop) / original_product.scop
                if scop_diff < 0.1:
                    similarity += 20
                elif scop_diff < 0.2:
                    similarity += 10
            
            # Similar price
            if original_product.base_price and product.base_price:
                price_diff = abs(original_product.base_price - product.base_price) / original_product.base_price
                if price_diff < 0.15:
                    similarity += 20
                elif price_diff < 0.3:
                    similarity += 10
            
            alternatives.append((pid, similarity))
        
        # Sort by similarity and take top alternatives
        alternatives.sort(key=lambda x: x[1], reverse=True)
        return [pid for pid, _ in alternatives[:max_alternatives]]


# Create singleton instance
heatpump_product_service = HeatPumpProductService()
