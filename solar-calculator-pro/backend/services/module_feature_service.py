"""
Module Feature Service

This module provides module-level feature toggle management for major application modules.
"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from backend.services.feature_flag_service import FeatureFlagService
from backend.models.feature_flag_schemas import FeatureFlagCreate, FeatureFlagType
from backend.core.errors import APIError
import logging

logger = logging.getLogger(__name__)


class ModuleFeatureService:
    """Service for managing module-level feature toggles"""
    
    # Module feature keys
    SOLAR_CALCULATOR = "module.solar_calculator"
    HEAT_PUMP = "module.heat_pump"
    PRICE_MATRIX = "module.price_matrix"
    PDF_GENERATION = "module.pdf_generation"
    CRM = "module.crm"
    VISUALIZATION_3D = "module.3d_visualization"
    
    # Sub-feature keys for Solar Calculator
    SOLAR_BASIC_CALC = "module.solar_calculator.basic_calculation"
    SOLAR_ADVANCED_CALC = "module.solar_calculator.advanced_calculation"
    SOLAR_SHADING_ANALYSIS = "module.solar_calculator.shading_analysis"
    SOLAR_BATTERY_STORAGE = "module.solar_calculator.battery_storage"
    SOLAR_FINANCIAL_ANALYSIS = "module.solar_calculator.financial_analysis"
    SOLAR_WEATHER_INTEGRATION = "module.solar_calculator.weather_integration"
    SOLAR_MONITORING = "module.solar_calculator.monitoring"
    
    # Sub-feature keys for Heat Pump
    HEAT_PUMP_BASIC_CALC = "module.heat_pump.basic_calculation"
    HEAT_PUMP_ADVANCED_CALC = "module.heat_pump.advanced_calculation"
    HEAT_PUMP_DYNAMIC_TARIFF = "module.heat_pump.dynamic_tariff"
    HEAT_PUMP_PV_INTEGRATION = "module.heat_pump.pv_integration"
    HEAT_PUMP_ENVIRONMENTAL = "module.heat_pump.environmental_analysis"
    
    # Sub-feature keys for Price Matrix
    PRICE_MATRIX_UPLOAD = "module.price_matrix.upload"
    PRICE_MATRIX_FORMULA_ENGINE = "module.price_matrix.formula_engine"
    PRICE_MATRIX_VALIDATION = "module.price_matrix.validation"
    PRICE_MATRIX_VERSIONING = "module.price_matrix.versioning"
    PRICE_MATRIX_EXTRAS = "module.price_matrix.extras"
    PRICE_MATRIX_MULTI_CURRENCY = "module.price_matrix.multi_currency"
    
    # Sub-feature keys for PDF Generation
    PDF_BASIC_GENERATION = "module.pdf_generation.basic"
    PDF_ADVANCED_TEMPLATES = "module.pdf_generation.advanced_templates"
    PDF_MULTI_LANGUAGE = "module.pdf_generation.multi_language"
    PDF_CUSTOM_BRANDING = "module.pdf_generation.custom_branding"
    PDF_BATCH_PROCESSING = "module.pdf_generation.batch_processing"
    PDF_CHART_INTEGRATION = "module.pdf_generation.chart_integration"
    
    # Sub-feature keys for CRM
    CRM_CUSTOMER_MANAGEMENT = "module.crm.customer_management"
    CRM_OFFER_TRACKING = "module.crm.offer_tracking"
    CRM_TASK_MANAGEMENT = "module.crm.task_management"
    CRM_COMMUNICATION = "module.crm.communication"
    CRM_LEAD_SCORING = "module.crm.lead_scoring"
    CRM_FORECASTING = "module.crm.forecasting"
    CRM_CONTRACT_MANAGEMENT = "module.crm.contract_management"
    
    # Sub-feature keys for 3D Visualization
    VIZ_3D_BASIC = "module.3d_visualization.basic"
    VIZ_3D_ADVANCED_RENDERING = "module.3d_visualization.advanced_rendering"
    VIZ_3D_AUTO_PLACEMENT = "module.3d_visualization.auto_placement"
    VIZ_3D_COLLISION_DETECTION = "module.3d_visualization.collision_detection"
    VIZ_3D_ANIMATION = "module.3d_visualization.animation"
    VIZ_3D_EXPORT = "module.3d_visualization.export"
    VIZ_3D_MOUNTING_SYSTEM = "module.3d_visualization.mounting_system"
    
    def __init__(self, db: Session):
        self.db = db
        self.feature_service = FeatureFlagService(db)
    
    def initialize_module_features(self, created_by: Optional[int] = None) -> Dict[str, str]:
        """
        Initialize all module-level feature flags
        
        Args:
            created_by: ID of user creating the flags
            
        Returns:
            Dictionary with status of each module initialization
        """
        results = {}
        
        # Define all module features
        module_features = [
            # Main modules
            (self.SOLAR_CALCULATOR, "Solar Calculator Module", "Enable/disable the entire Solar Calculator module", True),
            (self.HEAT_PUMP, "Heat Pump Module", "Enable/disable the entire Heat Pump module", True),
            (self.PRICE_MATRIX, "Price Matrix Module", "Enable/disable the entire Price Matrix module", True),
            (self.PDF_GENERATION, "PDF Generation Module", "Enable/disable the entire PDF Generation module", True),
            (self.CRM, "CRM Module", "Enable/disable the entire CRM module", True),
            (self.VISUALIZATION_3D, "3D Visualization Module", "Enable/disable the entire 3D Visualization module", True),
            
            # Solar Calculator sub-features
            (self.SOLAR_BASIC_CALC, "Solar Basic Calculation", "Basic solar system calculations", True),
            (self.SOLAR_ADVANCED_CALC, "Solar Advanced Calculation", "Advanced solar calculations with optimization", True),
            (self.SOLAR_SHADING_ANALYSIS, "Solar Shading Analysis", "Shading analysis and loss calculations", False),
            (self.SOLAR_BATTERY_STORAGE, "Solar Battery Storage", "Battery storage sizing and ROI analysis", True),
            (self.SOLAR_FINANCIAL_ANALYSIS, "Solar Financial Analysis", "Detailed financial analysis and projections", True),
            (self.SOLAR_WEATHER_INTEGRATION, "Solar Weather Integration", "Weather data integration and forecasting", False),
            (self.SOLAR_MONITORING, "Solar Monitoring", "Real-time monitoring integration", False),
            
            # Heat Pump sub-features
            (self.HEAT_PUMP_BASIC_CALC, "Heat Pump Basic Calculation", "Basic heat pump sizing calculations", True),
            (self.HEAT_PUMP_ADVANCED_CALC, "Heat Pump Advanced Calculation", "Advanced heat pump calculations", True),
            (self.HEAT_PUMP_DYNAMIC_TARIFF, "Heat Pump Dynamic Tariff", "Dynamic tariff optimization", True),
            (self.HEAT_PUMP_PV_INTEGRATION, "Heat Pump PV Integration", "Combined PV + Heat Pump optimization", True),
            (self.HEAT_PUMP_ENVIRONMENTAL, "Heat Pump Environmental Analysis", "Environmental impact analysis", True),
            
            # Price Matrix sub-features
            (self.PRICE_MATRIX_UPLOAD, "Price Matrix Upload", "Upload and manage price matrices", True),
            (self.PRICE_MATRIX_FORMULA_ENGINE, "Price Matrix Formula Engine", "Excel formula engine (INDEX/MATCH)", True),
            (self.PRICE_MATRIX_VALIDATION, "Price Matrix Validation", "Matrix structure and data validation", True),
            (self.PRICE_MATRIX_VERSIONING, "Price Matrix Versioning", "Version control for price matrices", True),
            (self.PRICE_MATRIX_EXTRAS, "Price Matrix Extras", "Extras and special products pricing", True),
            (self.PRICE_MATRIX_MULTI_CURRENCY, "Price Matrix Multi-Currency", "Multi-currency support", False),
            
            # PDF Generation sub-features
            (self.PDF_BASIC_GENERATION, "PDF Basic Generation", "Basic PDF generation", True),
            (self.PDF_ADVANCED_TEMPLATES, "PDF Advanced Templates", "Advanced template system", True),
            (self.PDF_MULTI_LANGUAGE, "PDF Multi-Language", "Multi-language PDF support", False),
            (self.PDF_CUSTOM_BRANDING, "PDF Custom Branding", "Custom branding and logos", True),
            (self.PDF_BATCH_PROCESSING, "PDF Batch Processing", "Batch PDF generation", True),
            (self.PDF_CHART_INTEGRATION, "PDF Chart Integration", "Chart integration in PDFs", True),
            
            # CRM sub-features
            (self.CRM_CUSTOMER_MANAGEMENT, "CRM Customer Management", "Customer database management", True),
            (self.CRM_OFFER_TRACKING, "CRM Offer Tracking", "Offer creation and tracking", True),
            (self.CRM_TASK_MANAGEMENT, "CRM Task Management", "Task and activity management", True),
            (self.CRM_COMMUNICATION, "CRM Communication", "Email and communication tracking", True),
            (self.CRM_LEAD_SCORING, "CRM Lead Scoring", "Automated lead scoring", False),
            (self.CRM_FORECASTING, "CRM Forecasting", "Sales forecasting", False),
            (self.CRM_CONTRACT_MANAGEMENT, "CRM Contract Management", "Contract and warranty management", True),
            
            # 3D Visualization sub-features
            (self.VIZ_3D_BASIC, "3D Visualization Basic", "Basic 3D visualization", True),
            (self.VIZ_3D_ADVANCED_RENDERING, "3D Advanced Rendering", "Photo-realistic rendering", False),
            (self.VIZ_3D_AUTO_PLACEMENT, "3D Auto Placement", "Automatic module placement", True),
            (self.VIZ_3D_COLLISION_DETECTION, "3D Collision Detection", "Collision detection and validation", True),
            (self.VIZ_3D_ANIMATION, "3D Animation", "360° animations and presentations", True),
            (self.VIZ_3D_EXPORT, "3D Export", "Export to various 3D formats", True),
            (self.VIZ_3D_MOUNTING_SYSTEM, "3D Mounting System", "Mounting system visualization", True),
        ]
        
        for key, name, description, enabled in module_features:
            try:
                # Check if feature already exists
                existing = self.feature_service.get_feature_flag_by_key(key)
                if existing:
                    results[key] = "already_exists"
                    continue
                
                # Create feature flag
                flag_data = FeatureFlagCreate(
                    key=key,
                    name=name,
                    description=description,
                    enabled=enabled,
                    flag_type=FeatureFlagType.GLOBAL
                )
                
                self.feature_service.create_feature_flag(flag_data, created_by)
                results[key] = "created"
                logger.info(f"Created module feature: {key}")
                
            except Exception as e:
                results[key] = f"error: {str(e)}"
                logger.error(f"Failed to create module feature {key}: {e}")
        
        return results
    
    def is_module_enabled(self, module_key: str, user_id: Optional[int] = None) -> bool:
        """
        Check if a module is enabled
        
        Args:
            module_key: Module feature key
            user_id: Optional user ID
            
        Returns:
            True if module is enabled
        """
        response = self.feature_service.is_feature_enabled(module_key, user_id)
        return response.enabled
    
    def is_sub_feature_enabled(
        self,
        module_key: str,
        sub_feature_key: str,
        user_id: Optional[int] = None
    ) -> bool:
        """
        Check if a sub-feature is enabled (requires parent module to be enabled)
        
        Args:
            module_key: Parent module feature key
            sub_feature_key: Sub-feature key
            user_id: Optional user ID
            
        Returns:
            True if both module and sub-feature are enabled
        """
        # Check parent module first
        if not self.is_module_enabled(module_key, user_id):
            return False
        
        # Check sub-feature
        response = self.feature_service.is_feature_enabled(sub_feature_key, user_id)
        return response.enabled
    
    def get_module_status(self, user_id: Optional[int] = None) -> Dict[str, Dict[str, bool]]:
        """
        Get status of all modules and their sub-features
        
        Args:
            user_id: Optional user ID
            
        Returns:
            Dictionary with module status
        """
        modules = {
            "solar_calculator": {
                "module": self.SOLAR_CALCULATOR,
                "sub_features": [
                    self.SOLAR_BASIC_CALC,
                    self.SOLAR_ADVANCED_CALC,
                    self.SOLAR_SHADING_ANALYSIS,
                    self.SOLAR_BATTERY_STORAGE,
                    self.SOLAR_FINANCIAL_ANALYSIS,
                    self.SOLAR_WEATHER_INTEGRATION,
                    self.SOLAR_MONITORING,
                ]
            },
            "heat_pump": {
                "module": self.HEAT_PUMP,
                "sub_features": [
                    self.HEAT_PUMP_BASIC_CALC,
                    self.HEAT_PUMP_ADVANCED_CALC,
                    self.HEAT_PUMP_DYNAMIC_TARIFF,
                    self.HEAT_PUMP_PV_INTEGRATION,
                    self.HEAT_PUMP_ENVIRONMENTAL,
                ]
            },
            "price_matrix": {
                "module": self.PRICE_MATRIX,
                "sub_features": [
                    self.PRICE_MATRIX_UPLOAD,
                    self.PRICE_MATRIX_FORMULA_ENGINE,
                    self.PRICE_MATRIX_VALIDATION,
                    self.PRICE_MATRIX_VERSIONING,
                    self.PRICE_MATRIX_EXTRAS,
                    self.PRICE_MATRIX_MULTI_CURRENCY,
                ]
            },
            "pdf_generation": {
                "module": self.PDF_GENERATION,
                "sub_features": [
                    self.PDF_BASIC_GENERATION,
                    self.PDF_ADVANCED_TEMPLATES,
                    self.PDF_MULTI_LANGUAGE,
                    self.PDF_CUSTOM_BRANDING,
                    self.PDF_BATCH_PROCESSING,
                    self.PDF_CHART_INTEGRATION,
                ]
            },
            "crm": {
                "module": self.CRM,
                "sub_features": [
                    self.CRM_CUSTOMER_MANAGEMENT,
                    self.CRM_OFFER_TRACKING,
                    self.CRM_TASK_MANAGEMENT,
                    self.CRM_COMMUNICATION,
                    self.CRM_LEAD_SCORING,
                    self.CRM_FORECASTING,
                    self.CRM_CONTRACT_MANAGEMENT,
                ]
            },
            "3d_visualization": {
                "module": self.VISUALIZATION_3D,
                "sub_features": [
                    self.VIZ_3D_BASIC,
                    self.VIZ_3D_ADVANCED_RENDERING,
                    self.VIZ_3D_AUTO_PLACEMENT,
                    self.VIZ_3D_COLLISION_DETECTION,
                    self.VIZ_3D_ANIMATION,
                    self.VIZ_3D_EXPORT,
                    self.VIZ_3D_MOUNTING_SYSTEM,
                ]
            }
        }
        
        status = {}
        
        for module_name, module_data in modules.items():
            module_enabled = self.is_module_enabled(module_data["module"], user_id)
            
            sub_features_status = {}
            for sub_feature_key in module_data["sub_features"]:
                # Sub-feature is only truly enabled if parent module is enabled
                sub_features_status[sub_feature_key] = (
                    module_enabled and 
                    self.feature_service.is_feature_enabled(sub_feature_key, user_id).enabled
                )
            
            status[module_name] = {
                "enabled": module_enabled,
                "sub_features": sub_features_status
            }
        
        return status
    
    def enable_module(self, module_key: str) -> bool:
        """
        Enable a module
        
        Args:
            module_key: Module feature key
            
        Returns:
            True if successful
        """
        flag = self.feature_service.get_feature_flag_by_key(module_key)
        if not flag:
            raise APIError(404, f"Module feature '{module_key}' not found")
        
        from backend.models.feature_flag_schemas import FeatureFlagUpdate
        self.feature_service.update_feature_flag(
            flag.id,
            FeatureFlagUpdate(enabled=True)
        )
        
        logger.info(f"Enabled module: {module_key}")
        return True
    
    def disable_module(self, module_key: str) -> bool:
        """
        Disable a module
        
        Args:
            module_key: Module feature key
            
        Returns:
            True if successful
        """
        flag = self.feature_service.get_feature_flag_by_key(module_key)
        if not flag:
            raise APIError(404, f"Module feature '{module_key}' not found")
        
        from backend.models.feature_flag_schemas import FeatureFlagUpdate
        self.feature_service.update_feature_flag(
            flag.id,
            FeatureFlagUpdate(enabled=False)
        )
        
        logger.info(f"Disabled module: {module_key}")
        return True
    
    def enable_sub_feature(self, sub_feature_key: str) -> bool:
        """
        Enable a sub-feature
        
        Args:
            sub_feature_key: Sub-feature key
            
        Returns:
            True if successful
        """
        flag = self.feature_service.get_feature_flag_by_key(sub_feature_key)
        if not flag:
            raise APIError(404, f"Sub-feature '{sub_feature_key}' not found")
        
        from backend.models.feature_flag_schemas import FeatureFlagUpdate
        self.feature_service.update_feature_flag(
            flag.id,
            FeatureFlagUpdate(enabled=True)
        )
        
        logger.info(f"Enabled sub-feature: {sub_feature_key}")
        return True
    
    def disable_sub_feature(self, sub_feature_key: str) -> bool:
        """
        Disable a sub-feature
        
        Args:
            sub_feature_key: Sub-feature key
            
        Returns:
            True if successful
        """
        flag = self.feature_service.get_feature_flag_by_key(sub_feature_key)
        if not flag:
            raise APIError(404, f"Sub-feature '{sub_feature_key}' not found")
        
        from backend.models.feature_flag_schemas import FeatureFlagUpdate
        self.feature_service.update_feature_flag(
            flag.id,
            FeatureFlagUpdate(enabled=False)
        )
        
        logger.info(f"Disabled sub-feature: {sub_feature_key}")
        return True
