"""
API Usage Examples

This module provides comprehensive examples of how to use the Solar Calculator Pro API
from Python applications.
"""

import requests
from typing import Dict, Any, Optional
import json


class SolarCalculatorAPIClient:
    """
    Python client for Solar Calculator Pro API
    
    Example usage:
        client = SolarCalculatorAPIClient("http://localhost:8000")
        client.login("admin", "password")
        result = client.calculate_solar(roof_area=50.0, ...)
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.token: Optional[str] = None
        self.session = requests.Session()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login and obtain access token
        
        Args:
            username: Username
            password: Password
        
        Returns:
            Login response with access token
        
        Example:
            >>> client = SolarCalculatorAPIClient()
            >>> response = client.login("admin", "password")
            >>> print(response["access_token"])
        """
        response = self.session.post(
            f"{self.api_url}/auth/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        self.token = data["access_token"]
        return data
    
    def calculate_solar(
        self,
        roof_area: float,
        roof_type: str,
        roof_angle: float,
        orientation: str,
        module_type: str,
        annual_consumption: float,
        location: str
    ) -> Dict[str, Any]:
        """
        Calculate solar system parameters
        
        Args:
            roof_area: Roof area in square meters
            roof_type: Type of roof (flat, gable, hip)
            roof_angle: Roof angle in degrees
            orientation: Roof orientation (north, south, east, west)
            module_type: Type of solar module
            annual_consumption: Annual electricity consumption in kWh
            location: Location/city name
        
        Returns:
            Calculation results
        
        Example:
            >>> result = client.calculate_solar(
            ...     roof_area=50.0,
            ...     roof_type="flat",
            ...     roof_angle=30.0,
            ...     orientation="south",
            ...     module_type="standard",
            ...     annual_consumption=4000.0,
            ...     location="Berlin"
            ... )
            >>> print(f"System size: {result['system_size']} kWp")
            >>> print(f"Module count: {result['module_count']}")
        """
        response = self.session.post(
            f"{self.api_url}/solar/calculate",
            headers=self._get_headers(),
            json={
                "roof_area": roof_area,
                "roof_type": roof_type,
                "roof_angle": roof_angle,
                "orientation": orientation,
                "module_type": module_type,
                "annual_consumption": annual_consumption,
                "location": location
            }
        )
        response.raise_for_status()
        return response.json()
    
    def create_project(
        self,
        name: str,
        customer_name: str,
        customer_email: str,
        project_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new project
        
        Args:
            name: Project name
            customer_name: Customer name
            customer_email: Customer email
            project_type: Type of project (solar, heatpump, combined)
            data: Project data
        
        Returns:
            Created project
        
        Example:
            >>> project = client.create_project(
            ...     name="Müller Residence",
            ...     customer_name="Hans Müller",
            ...     customer_email="hans@example.com",
            ...     project_type="solar",
            ...     data={"system_size": 10.5}
            ... )
            >>> print(f"Project ID: {project['id']}")
        """
        response = self.session.post(
            f"{self.api_url}/solar/projects",
            headers=self._get_headers(),
            json={
                "name": name,
                "customer_name": customer_name,
                "customer_email": customer_email,
                "project_type": project_type,
                "data": data
            }
        )
        response.raise_for_status()
        return response.json()
    
    def list_projects(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        List all projects with pagination
        
        Args:
            page: Page number
            page_size: Number of items per page
        
        Returns:
            Paginated list of projects
        
        Example:
            >>> projects = client.list_projects(page=1, page_size=10)
            >>> for project in projects['items']:
            ...     print(f"{project['name']}: {project['status']}")
        """
        response = self.session.get(
            f"{self.api_url}/solar/projects",
            headers=self._get_headers(),
            params={"page": page, "page_size": page_size}
        )
        response.raise_for_status()
        return response.json()
    
    def calculate_price(
        self,
        module_count: int,
        battery_model: str,
        extras: list = None,
        discounts: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Calculate price using price matrix
        
        Args:
            module_count: Number of solar modules
            battery_model: Battery storage model name
            extras: List of extra services
            discounts: Dictionary of discount types and amounts
        
        Returns:
            Price calculation result
        
        Example:
            >>> price = client.calculate_price(
            ...     module_count=30,
            ...     battery_model="Tesla Powerwall 2",
            ...     extras=["monitoring", "insurance"],
            ...     discounts={"early_bird": 0.05}
            ... )
            >>> print(f"Total: {price['formatted']['total_price']}")
        """
        response = self.session.post(
            f"{self.api_url}/pricing/calculate",
            headers=self._get_headers(),
            json={
                "module_count": module_count,
                "battery_model": battery_model,
                "extras": extras or [],
                "discounts": discounts or {}
            }
        )
        response.raise_for_status()
        return response.json()
    
    def generate_pdf(
        self,
        project_id: int,
        template: str = "standard",
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate PDF report for project
        
        Args:
            project_id: Project ID
            template: PDF template name
            options: PDF generation options
        
        Returns:
            PDF generation result with download URL
        
        Example:
            >>> pdf = client.generate_pdf(
            ...     project_id=1,
            ...     template="standard",
            ...     options={"include_charts": True, "include_3d": True}
            ... )
            >>> print(f"PDF URL: {pdf['pdf_url']}")
        """
        response = self.session.post(
            f"{self.api_url}/pdf/generate",
            headers=self._get_headers(),
            json={
                "project_id": project_id,
                "template": template,
                "options": options or {}
            }
        )
        response.raise_for_status()
        return response.json()
    
    def list_products(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List products with optional filtering
        
        Args:
            page: Page number
            page_size: Number of items per page
            category: Filter by category
        
        Returns:
            Paginated list of products
        
        Example:
            >>> products = client.list_products(category="solar_modules")
            >>> for product in products['items']:
            ...     print(f"{product['name']}: {product['formatted']['price']}")
        """
        params = {"page": page, "page_size": page_size}
        if category:
            params["category"] = category
        
        response = self.session.get(
            f"{self.api_url}/products",
            headers=self._get_headers(),
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def create_customer(
        self,
        name: str,
        email: str,
        phone: str,
        address: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Create a new customer in CRM
        
        Args:
            name: Customer name
            email: Customer email
            phone: Customer phone
            address: Customer address dictionary
        
        Returns:
            Created customer
        
        Example:
            >>> customer = client.create_customer(
            ...     name="Maria Schmidt",
            ...     email="maria@example.com",
            ...     phone="+49 123 456789",
            ...     address={
            ...         "street": "Hauptstraße 123",
            ...         "city": "Berlin",
            ...         "postal_code": "10115",
            ...         "country": "Germany"
            ...     }
            ... )
            >>> print(f"Customer ID: {customer['id']}")
        """
        response = self.session.post(
            f"{self.api_url}/crm/customers",
            headers=self._get_headers(),
            json={
                "name": name,
                "email": email,
                "phone": phone,
                "address": address
            }
        )
        response.raise_for_status()
        return response.json()


def example_complete_workflow():
    """
    Example: Complete workflow from calculation to PDF generation
    """
    print("=== Complete Solar Calculator Workflow ===\n")
    
    # Initialize client
    client = SolarCalculatorAPIClient()
    
    # 1. Login
    print("1. Logging in...")
    login_response = client.login("admin", "password")
    print(f"   ✓ Logged in successfully\n")
    
    # 2. Calculate solar system
    print("2. Calculating solar system...")
    calculation = client.calculate_solar(
        roof_area=50.0,
        roof_type="flat",
        roof_angle=30.0,
        orientation="south",
        module_type="standard",
        annual_consumption=4000.0,
        location="Berlin"
    )
    print(f"   ✓ System size: {calculation['formatted']['system_size']}")
    print(f"   ✓ Module count: {calculation['module_count']}")
    print(f"   ✓ Annual production: {calculation['formatted']['annual_production']}\n")
    
    # 3. Create project
    print("3. Creating project...")
    project = client.create_project(
        name="Müller Residence Solar Installation",
        customer_name="Hans Müller",
        customer_email="hans.mueller@example.com",
        project_type="solar",
        data=calculation
    )
    print(f"   ✓ Project created with ID: {project['id']}\n")
    
    # 4. Calculate price
    print("4. Calculating price...")
    price = client.calculate_price(
        module_count=calculation['module_count'],
        battery_model="Tesla Powerwall 2",
        extras=["monitoring", "insurance"],
        discounts={"early_bird": 0.05}
    )
    print(f"   ✓ Base price: {price['formatted']['base_price']}")
    print(f"   ✓ Total price: {price['formatted']['total_price']}\n")
    
    # 5. Generate PDF
    print("5. Generating PDF report...")
    pdf = client.generate_pdf(
        project_id=project['id'],
        template="standard",
        options={
            "include_charts": True,
            "include_3d": True,
            "language": "de"
        }
    )
    print(f"   ✓ PDF generated: {pdf['file_name']}")
    print(f"   ✓ Size: {pdf['size_bytes']} bytes\n")
    
    print("=== Workflow completed successfully! ===")


def example_crm_workflow():
    """
    Example: CRM workflow - create customer, offer, and task
    """
    print("=== CRM Workflow ===\n")
    
    client = SolarCalculatorAPIClient()
    client.login("admin", "password")
    
    # 1. Create customer
    print("1. Creating customer...")
    customer = client.create_customer(
        name="Maria Schmidt",
        email="maria.schmidt@example.com",
        phone="+49 30 12345678",
        address={
            "street": "Berliner Straße 45",
            "city": "Berlin",
            "postal_code": "10715",
            "country": "Germany"
        }
    )
    print(f"   ✓ Customer created: {customer['name']} (ID: {customer['id']})\n")
    
    # 2. Create offer
    print("2. Creating offer...")
    offer_response = client.session.post(
        f"{client.api_url}/crm/offers",
        headers=client._get_headers(),
        json={
            "customer_id": customer['id'],
            "amount": 15675.0,
            "valid_until": "2024-02-28",
            "status": "draft",
            "description": "Solar installation with 30 modules and battery storage"
        }
    )
    offer = offer_response.json()
    print(f"   ✓ Offer created: {offer['formatted']['amount']}\n")
    
    # 3. Create follow-up task
    print("3. Creating follow-up task...")
    task_response = client.session.post(
        f"{client.api_url}/crm/tasks",
        headers=client._get_headers(),
        json={
            "title": "Follow up with Maria Schmidt",
            "description": "Call customer to discuss the solar installation offer",
            "customer_id": customer['id'],
            "due_date": "2024-01-25",
            "priority": "high"
        }
    )
    task = task_response.json()
    print(f"   ✓ Task created: {task['title']}\n")
    
    print("=== CRM workflow completed! ===")


def example_product_management():
    """
    Example: Product management operations
    """
    print("=== Product Management ===\n")
    
    client = SolarCalculatorAPIClient()
    client.login("admin", "password")
    
    # 1. List products
    print("1. Listing solar modules...")
    products = client.list_products(category="solar_modules", page_size=5)
    print(f"   ✓ Found {products['total']} products")
    for product in products['items'][:3]:
        print(f"   - {product['name']}: {product['formatted']['price']}")
    print()
    
    # 2. Search products
    print("2. Searching for 400W modules...")
    search_response = client.session.get(
        f"{client.api_url}/products/search",
        headers=client._get_headers(),
        params={"q": "400W", "category": "solar_modules"}
    )
    search_results = search_response.json()
    print(f"   ✓ Found {len(search_results['items'])} matching products\n")
    
    print("=== Product management completed! ===")


def example_error_handling():
    """
    Example: Proper error handling
    """
    print("=== Error Handling Examples ===\n")
    
    client = SolarCalculatorAPIClient()
    
    # Example 1: Authentication error
    print("1. Testing authentication error...")
    try:
        client.login("invalid_user", "wrong_password")
    except requests.exceptions.HTTPError as e:
        print(f"   ✓ Caught authentication error: {e.response.status_code}")
        error_data = e.response.json()
        print(f"   Message: {error_data['error']['message']}\n")
    
    # Example 2: Validation error
    print("2. Testing validation error...")
    client.login("admin", "password")
    try:
        client.calculate_solar(
            roof_area=-10.0,  # Invalid: negative value
            roof_type="flat",
            roof_angle=30.0,
            orientation="south",
            module_type="standard",
            annual_consumption=4000.0,
            location="Berlin"
        )
    except requests.exceptions.HTTPError as e:
        print(f"   ✓ Caught validation error: {e.response.status_code}")
        error_data = e.response.json()
        print(f"   Message: {error_data['error']['message']}\n")
    
    # Example 3: Not found error
    print("3. Testing not found error...")
    try:
        response = client.session.get(
            f"{client.api_url}/solar/projects/99999",
            headers=client._get_headers()
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"   ✓ Caught not found error: {e.response.status_code}")
        error_data = e.response.json()
        print(f"   Message: {error_data['error']['message']}\n")
    
    print("=== Error handling examples completed! ===")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Solar Calculator Pro API - Usage Examples")
    print("="*60 + "\n")
    
    # Run examples
    try:
        example_complete_workflow()
        print("\n" + "-"*60 + "\n")
        
        example_crm_workflow()
        print("\n" + "-"*60 + "\n")
        
        example_product_management()
        print("\n" + "-"*60 + "\n")
        
        example_error_handling()
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Make sure the API server is running at http://localhost:8000")
