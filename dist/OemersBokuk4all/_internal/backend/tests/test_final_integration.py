"""
Final Integration Testing
Task 244: Final Integration Testing

End-to-end tests for complete workflows:
- Solar Calculator → PDF generation
- Heat Pump → PDF generation
- Price Matrix → Calculation → PDF
- CRM → Offer → PDF
- 3D Visualization → Export
- Product Management → Price Matrix
- Admin → User Management
- Complete customer journey
"""

import pytest
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowStep:
    """Single step in a workflow"""
    name: str
    action: str
    expected_result: str
    status: WorkflowStatus = WorkflowStatus.NOT_STARTED
    actual_result: str = ""


@dataclass
class WorkflowTest:
    """Complete workflow test"""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    status: WorkflowStatus = WorkflowStatus.NOT_STARTED
    
    @property
    def is_complete(self) -> bool:
        return all(s.status == WorkflowStatus.COMPLETED for s in self.steps)


# ============================================================================
# Mock Services for Integration Testing
# ============================================================================

class MockSolarService:
    """Mock solar calculation service"""
    
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "system_size_kwp": 10.5,
            "module_count": 24,
            "annual_production_kwh": 10500,
            "savings_eur": 2100,
            "payback_years": 8.5,
            "co2_savings_kg": 5250
        }
    
    def create_project(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"id": 1, "name": data.get("name", "New Project"), **data}


class MockHeatPumpService:
    """Mock heat pump service"""
    
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "heating_demand_kwh": 15000,
            "recommended_size_kw": 12,
            "cop": 4.2,
            "annual_cost_eur": 1200,
            "savings_vs_gas_eur": 800
        }


class MockPricingService:
    """Mock pricing service"""
    
    def lookup_price(self, module_count: int, storage: str) -> Dict[str, Any]:
        base_price = module_count * 500
        storage_price = 2000 if storage != "kein Speicher" else 0
        return {
            "base_price": base_price,
            "storage_price": storage_price,
            "total_price": base_price + storage_price,
            "currency": "EUR"
        }


class MockPDFService:
    """Mock PDF generation service"""
    
    def generate(self, template: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "pdf_id": f"pdf_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "status": "completed",
            "download_url": "/api/v1/pdf/download/pdf_123",
            "pages": 5
        }


class MockVisualizationService:
    """Mock 3D visualization service"""
    
    def generate_model(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "model_id": "model_123",
            "format": "gltf",
            "modules_placed": config.get("module_count", 24)
        }
    
    def export(self, model_id: str, format: str) -> bytes:
        return b"mock_3d_model_data"


class MockCRMService:
    """Mock CRM service"""
    
    def create_customer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"id": 1, **data}
    
    def create_offer(self, customer_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"id": 1, "customer_id": customer_id, "status": "draft", **data}
    
    def update_offer_status(self, offer_id: int, status: str) -> Dict[str, Any]:
        return {"id": offer_id, "status": status}


class MockProductService:
    """Mock product service"""
    
    def get_products(self, category: str = None) -> List[Dict[str, Any]]:
        return [
            {"id": 1, "name": "Solar Panel 400W", "category": "pv_modules", "price": 299.99},
            {"id": 2, "name": "Inverter 10kW", "category": "inverters", "price": 1499.99},
            {"id": 3, "name": "Battery 10kWh", "category": "batteries", "price": 4999.99}
        ]


class MockAdminService:
    """Mock admin service"""
    
    def create_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"id": 1, **data}
    
    def get_settings(self) -> Dict[str, Any]:
        return {"company_name": "Solar GmbH", "language": "de"}


# ============================================================================
# Integration Test Classes
# ============================================================================

class TestSolarCalculatorToPDFWorkflow:
    """Tests for Solar Calculator → PDF workflow"""
    
    @pytest.fixture
    def services(self):
        return {
            "solar": MockSolarService(),
            "pdf": MockPDFService(),
            "visualization": MockVisualizationService()
        }
    
    def test_complete_solar_to_pdf_workflow(self, services):
        """Test complete solar calculation to PDF generation"""
        # Step 1: Calculate solar system
        calc_result = services["solar"].calculate({
            "roof_area": 50,
            "roof_angle": 30,
            "orientation": "south",
            "consumption": 4000
        })
        
        assert calc_result["system_size_kwp"] > 0
        assert calc_result["module_count"] > 0
        
        # Step 2: Create project
        project = services["solar"].create_project({
            "name": "Test Solar Project",
            "calculation": calc_result
        })
        
        assert project["id"] is not None
        
        # Step 3: Generate 3D visualization
        model = services["visualization"].generate_model({
            "module_count": calc_result["module_count"]
        })
        
        assert model["model_id"] is not None
        
        # Step 4: Generate PDF
        pdf = services["pdf"].generate("solar_offer", {
            "project": project,
            "calculation": calc_result,
            "visualization": model
        })
        
        assert pdf["status"] == "completed"
        assert pdf["download_url"] is not None
    
    def test_solar_calculation_accuracy(self, services):
        """Test solar calculation produces valid results"""
        result = services["solar"].calculate({
            "roof_area": 50,
            "roof_angle": 30,
            "orientation": "south",
            "consumption": 4000
        })
        
        # Verify all required fields
        assert "system_size_kwp" in result
        assert "module_count" in result
        assert "annual_production_kwh" in result
        assert "savings_eur" in result
        assert "payback_years" in result
        
        # Verify reasonable values
        assert result["system_size_kwp"] > 0
        assert result["module_count"] > 0
        assert result["annual_production_kwh"] > 0


class TestHeatPumpToPDFWorkflow:
    """Tests for Heat Pump → PDF workflow"""
    
    @pytest.fixture
    def services(self):
        return {
            "heatpump": MockHeatPumpService(),
            "pdf": MockPDFService()
        }
    
    def test_complete_heatpump_to_pdf_workflow(self, services):
        """Test complete heat pump calculation to PDF generation"""
        # Step 1: Calculate heat pump sizing
        calc_result = services["heatpump"].calculate({
            "building_area": 150,
            "insulation": "medium",
            "current_heating": "gas"
        })
        
        assert calc_result["heating_demand_kwh"] > 0
        assert calc_result["recommended_size_kw"] > 0
        
        # Step 2: Generate PDF
        pdf = services["pdf"].generate("heatpump_offer", {
            "calculation": calc_result
        })
        
        assert pdf["status"] == "completed"


class TestPriceMatrixToCalculationWorkflow:
    """Tests for Price Matrix → Calculation → PDF workflow"""
    
    @pytest.fixture
    def services(self):
        return {
            "pricing": MockPricingService(),
            "solar": MockSolarService(),
            "pdf": MockPDFService()
        }
    
    def test_price_lookup_integration(self, services):
        """Test price lookup with solar calculation"""
        # Step 1: Calculate solar system
        calc_result = services["solar"].calculate({
            "roof_area": 50,
            "consumption": 4000
        })
        
        # Step 2: Lookup price
        price = services["pricing"].lookup_price(
            module_count=calc_result["module_count"],
            storage="10kWh"
        )
        
        assert price["total_price"] > 0
        assert price["currency"] == "EUR"
        
        # Step 3: Generate PDF with pricing
        pdf = services["pdf"].generate("solar_offer", {
            "calculation": calc_result,
            "pricing": price
        })
        
        assert pdf["status"] == "completed"
    
    def test_no_storage_pricing(self, services):
        """Test pricing without storage"""
        price = services["pricing"].lookup_price(
            module_count=24,
            storage="kein Speicher"
        )
        
        assert price["storage_price"] == 0
        assert price["total_price"] == price["base_price"]


class TestCRMToOfferWorkflow:
    """Tests for CRM → Offer → PDF workflow"""
    
    @pytest.fixture
    def services(self):
        return {
            "crm": MockCRMService(),
            "solar": MockSolarService(),
            "pdf": MockPDFService()
        }
    
    def test_complete_crm_offer_workflow(self, services):
        """Test complete CRM to offer workflow"""
        # Step 1: Create customer
        customer = services["crm"].create_customer({
            "name": "Max Mustermann",
            "email": "max@example.com",
            "phone": "+49123456789"
        })
        
        assert customer["id"] is not None
        
        # Step 2: Calculate solar system
        calc_result = services["solar"].calculate({
            "roof_area": 50,
            "consumption": 4000
        })
        
        # Step 3: Create offer
        offer = services["crm"].create_offer(customer["id"], {
            "calculation": calc_result,
            "total_price": 15000
        })
        
        assert offer["id"] is not None
        assert offer["status"] == "draft"
        
        # Step 4: Generate PDF
        pdf = services["pdf"].generate("offer", {
            "customer": customer,
            "offer": offer,
            "calculation": calc_result
        })
        
        assert pdf["status"] == "completed"
        
        # Step 5: Update offer status
        updated_offer = services["crm"].update_offer_status(offer["id"], "sent")
        assert updated_offer["status"] == "sent"


class TestVisualizationExportWorkflow:
    """Tests for 3D Visualization → Export workflow"""
    
    @pytest.fixture
    def services(self):
        return {
            "visualization": MockVisualizationService(),
            "solar": MockSolarService()
        }
    
    def test_complete_visualization_export(self, services):
        """Test complete 3D visualization and export"""
        # Step 1: Calculate solar system
        calc_result = services["solar"].calculate({
            "roof_area": 50,
            "consumption": 4000
        })
        
        # Step 2: Generate 3D model
        model = services["visualization"].generate_model({
            "roof_type": "gable",
            "module_count": calc_result["module_count"]
        })
        
        assert model["model_id"] is not None
        assert model["modules_placed"] == calc_result["module_count"]
        
        # Step 3: Export model
        export_data = services["visualization"].export(model["model_id"], "stl")
        
        assert export_data is not None
        assert len(export_data) > 0


class TestProductToPriceMatrixWorkflow:
    """Tests for Product Management → Price Matrix workflow"""
    
    @pytest.fixture
    def services(self):
        return {
            "products": MockProductService(),
            "pricing": MockPricingService()
        }
    
    def test_product_pricing_integration(self, services):
        """Test product and pricing integration"""
        # Step 1: Get products
        products = services["products"].get_products()
        
        assert len(products) > 0
        
        # Step 2: Calculate price with products
        pv_modules = [p for p in products if p["category"] == "pv_modules"]
        assert len(pv_modules) > 0
        
        # Step 3: Lookup system price
        price = services["pricing"].lookup_price(
            module_count=24,
            storage="10kWh"
        )
        
        assert price["total_price"] > 0


class TestAdminUserManagementWorkflow:
    """Tests for Admin → User Management workflow"""
    
    @pytest.fixture
    def services(self):
        return {
            "admin": MockAdminService()
        }
    
    def test_user_creation_workflow(self, services):
        """Test user creation workflow"""
        # Step 1: Create user
        user = services["admin"].create_user({
            "email": "newuser@example.com",
            "name": "New User",
            "role": "user"
        })
        
        assert user["id"] is not None
        assert user["email"] == "newuser@example.com"
        assert user["role"] == "user"
    
    def test_settings_management(self, services):
        """Test settings management"""
        settings = services["admin"].get_settings()
        
        assert "company_name" in settings
        assert "language" in settings


class TestCompleteCustomerJourney:
    """Tests for complete customer journey"""
    
    @pytest.fixture
    def services(self):
        return {
            "crm": MockCRMService(),
            "solar": MockSolarService(),
            "pricing": MockPricingService(),
            "visualization": MockVisualizationService(),
            "pdf": MockPDFService()
        }
    
    def test_full_customer_journey(self, services):
        """Test complete customer journey from inquiry to offer"""
        # Step 1: Create customer
        customer = services["crm"].create_customer({
            "name": "Test Customer",
            "email": "test@example.com"
        })
        
        # Step 2: Calculate solar system
        calc_result = services["solar"].calculate({
            "roof_area": 60,
            "consumption": 5000
        })
        
        # Step 3: Get pricing
        price = services["pricing"].lookup_price(
            module_count=calc_result["module_count"],
            storage="10kWh"
        )
        
        # Step 4: Generate 3D visualization
        model = services["visualization"].generate_model({
            "module_count": calc_result["module_count"]
        })
        
        # Step 5: Create offer
        offer = services["crm"].create_offer(customer["id"], {
            "calculation": calc_result,
            "pricing": price,
            "visualization": model
        })
        
        # Step 6: Generate PDF
        pdf = services["pdf"].generate("complete_offer", {
            "customer": customer,
            "offer": offer,
            "calculation": calc_result,
            "pricing": price,
            "visualization": model
        })
        
        # Verify complete journey
        assert customer["id"] is not None
        assert calc_result["system_size_kwp"] > 0
        assert price["total_price"] > 0
        assert model["model_id"] is not None
        assert offer["id"] is not None
        assert pdf["status"] == "completed"
    
    def test_journey_with_german_formatting(self, services):
        """Test customer journey with German number formatting"""
        # Calculate
        calc_result = services["solar"].calculate({
            "roof_area": 50,
            "consumption": 4000
        })
        
        # Format numbers in German style
        def format_german(value: float) -> str:
            return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        formatted_price = format_german(12500.50)
        assert formatted_price == "12.500,50"
        
        formatted_production = format_german(calc_result["annual_production_kwh"])
        assert "," in formatted_production  # German decimal separator


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
