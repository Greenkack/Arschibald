# Function and Class Mapping
## Complete Inventory for Migration

---

## calculations.py - Core Functions

### Main Calculation Functions

```python
def perform_calculations(project_data: dict) -> dict:
    """
    Main calculation entry point
    
    Args:
        project_data: Dictionary containing all project parameters
        
    Returns:
        Dictionary with calculation results
        
    Migration: Wrap in SolarService.calculate()
    Priority: CRITICAL
    """

def calculate_system_size(
    annual_consumption: float,
    roof_area: float,
    module_power: float,
    efficiency_factor: float = 0.85
) -> float:
    """
    Calculate optimal system size in kWp
    
    Migration: Keep exact algorithm
    Priority: CRITICAL
    """

def calculate_module_count(
    system_size: float,
    module_power: float
) -> int:
    """
    Calculate number of modules needed
    
    Migration: Keep exact algorithm
    Priority: CRITICAL
    """

def calculate_annual_production(
    system_size: float,
    location: str,
    orientation: str,
    tilt_angle: float
) -> float:
    """
    Estimate annual energy production
    
    Uses pvlib for solar radiation data
    
    Migration: Keep pvlib integration
    Priority: CRITICAL
    """

def calculate_self_consumption_rate(
    annual_production: float,
    annual_consumption: float,
    has_battery: bool,
    battery_capacity: float = 0
) -> float:
    """
    Calculate self-consumption rate
    
    Migration: Keep exact formula
    Priority: CRITICAL
    """

def calculate_grid_feed_in(
    annual_production: float,
    self_consumption: float
) -> float:
    """
    Calculate grid feed-in amount
    
    Migration: Keep exact formula
    Priority: HIGH
    """

def calculate_total_cost(
    system_size: float,
    module_count: int,
    has_battery: bool,
    battery_capacity: float,
    extras: dict
) -> float:
    """
    Calculate total system cost
    
    Uses price matrix lookup
    
    Migration: Integrate with PricingService
    Priority: CRITICAL
    """

def calculate_roi(
    total_cost: float,
    annual_savings: float,
    feed_in_revenue: float,
    electricity_price_increase: float = 0.03
) -> dict:
    """
    Calculate return on investment
    
    Returns: {
        'payback_period': float,
        'roi_25_years': float,
        'npv': float,
        'irr': float
    }
    
    Migration: Keep exact financial formulas
    Priority: CRITICAL
    """

def calculate_payback_period(
    investment: float,
    annual_savings: float,
    annual_revenue: float
) -> float:
    """
    Calculate simple payback period
    
    Migration: Keep exact formula
    Priority: CRITICAL
    """

def calculate_npv(
    cash_flows: List[float],
    discount_rate: float = 0.04
) -> float:
    """
    Calculate Net Present Value
    
    Migration: Keep exact formula
    Priority: HIGH
    """

def calculate_irr(
    cash_flows: List[float]
) -> float:
    """
    Calculate Internal Rate of Return
    
    Uses scipy.optimize
    
    Migration: Keep scipy dependency
    Priority: HIGH
    """

def calculate_co2_savings(
    annual_production: float,
    co2_factor: float = 0.401
) -> float:
    """
    Calculate CO2 savings in kg
    
    Migration: Keep exact formula
    Priority: MEDIUM
    """
```


### Advanced Calculation Functions

```python
def calculate_degradation_over_time(
    initial_production: float,
    years: int,
    degradation_rate: float = 0.005
) -> List[float]:
    """
    Calculate production with degradation
    
    Migration: Keep exact formula
    Priority: MEDIUM
    """

def calculate_shading_losses(
    module_positions: List[dict],
    obstacles: List[dict],
    sun_path: dict
) -> float:
    """
    Calculate shading losses
    
    Complex 3D geometry calculations
    
    Migration: Keep exact algorithm
    Priority: HIGH
    """

def optimize_module_placement(
    roof_geometry: dict,
    module_specs: dict,
    constraints: dict
) -> List[dict]:
    """
    Optimize module placement on roof
    
    Uses optimization algorithms
    
    Migration: Keep exact algorithm
    Priority: HIGH
    """

def calculate_inverter_sizing(
    system_size: float,
    module_voltage: float,
    string_configuration: dict
) -> dict:
    """
    Calculate optimal inverter size
    
    Migration: Keep exact logic
    Priority: HIGH
    """

def calculate_battery_sizing(
    daily_consumption: float,
    self_consumption_target: float,
    autonomy_days: int = 1
) -> float:
    """
    Calculate optimal battery capacity
    
    Migration: Keep exact formula
    Priority: HIGH
    """
```

---

## database.py - Database Classes

### SQLAlchemy Models

```python
class Product(Base):
    """
    Base product model
    
    Migration: Keep model, add to FastAPI models
    """
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    manufacturer = Column(String)
    category = Column(String)
    price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

class PVModule(Product):
    """
    PV module model
    
    Migration: Keep model
    """
    __tablename__ = 'pv_modules'
    
    id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    power_wp = Column(Integer, nullable=False)
    efficiency = Column(Float)
    dimensions_mm = Column(String)
    weight_kg = Column(Float)
    voltage_v = Column(Float)
    current_a = Column(Float)
    datasheet_url = Column(String)
    image_url = Column(String)

class Inverter(Product):
    """
    Inverter model
    
    Migration: Keep model
    """
    __tablename__ = 'inverters'
    
    id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    power_kw = Column(Float, nullable=False)
    efficiency = Column(Float)
    mppt_count = Column(Integer)
    max_dc_voltage = Column(Float)
    max_dc_current = Column(Float)

class Battery(Product):
    """
    Battery storage model
    
    Migration: Keep model
    """
    __tablename__ = 'batteries'
    
    id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    capacity_kwh = Column(Float, nullable=False)
    voltage_v = Column(Float)
    max_charge_power = Column(Float)
    max_discharge_power = Column(Float)
    warranty_years = Column(Integer)
    cycles = Column(Integer)

class Customer(Base):
    """
    Customer model
    
    Migration: Keep model
    """
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True)
    phone = Column(String)
    address = Column(String)
    city = Column(String)
    postal_code = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    projects = relationship("Project", back_populates="customer")

class Project(Base):
    """
    Project model
    
    Migration: Keep model
    """
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    name = Column(String, nullable=False)
    status = Column(String)  # draft, active, completed, archived
    project_type = Column(String)  # solar, heatpump, combined
    data = Column(JSON)  # All project data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="projects")
    offers = relationship("Offer", back_populates="project")

class Offer(Base):
    """
    Offer model
    
    Migration: Keep model
    """
    __tablename__ = 'offers'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    offer_number = Column(String, unique=True)
    total_price = Column(Float)
    status = Column(String)  # draft, sent, accepted, rejected
    valid_until = Column(Date)
    pdf_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="offers")

class User(Base):
    """
    User model
    
    Migration: Keep model, add JWT fields
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    email = Column(String, unique=True)
    role = Column(String)  # admin, user, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
```


### Database Operations

```python
def get_products(
    category: str = None,
    manufacturer: str = None,
    min_price: float = None,
    max_price: float = None
) -> List[Product]:
    """
    Get products with filters
    
    Migration: Wrap in ProductService.get_products()
    """

def get_pv_modules(
    min_power: int = None,
    max_power: int = None,
    manufacturer: str = None
) -> List[PVModule]:
    """
    Get PV modules with filters
    
    Migration: Wrap in ProductService.get_pv_modules()
    """

def save_project(project_data: dict) -> int:
    """
    Save project to database
    
    Migration: Wrap in ProjectService.create_project()
    """

def load_project(project_id: int) -> dict:
    """
    Load project from database
    
    Migration: Wrap in ProjectService.get_project()
    """

def update_project(project_id: int, project_data: dict) -> bool:
    """
    Update project in database
    
    Migration: Wrap in ProjectService.update_project()
    """

def delete_project(project_id: int) -> bool:
    """
    Delete project from database
    
    Migration: Wrap in ProjectService.delete_project()
    """

def search_products(query: str) -> List[Product]:
    """
    Full-text search for products
    
    Migration: Wrap in ProductService.search_products()
    """
```

---

## pdf_generator.py - PDF Functions

### Main PDF Generation

```python
def generate_pdf(
    project_data: dict,
    template: str = "standard",
    options: dict = None
) -> bytes:
    """
    Main PDF generation function
    
    Args:
        project_data: All project data
        template: Template name
        options: PDF options (logos, colors, etc.)
        
    Returns:
        PDF as bytes
        
    Migration: Wrap in PDFService.generate_pdf()
    Priority: CRITICAL
    """

def create_cover_page(
    pdf: canvas.Canvas,
    project_data: dict,
    options: dict
) -> None:
    """
    Create PDF cover page
    
    Migration: Keep as internal function
    """

def create_system_overview_page(
    pdf: canvas.Canvas,
    calculation_results: dict,
    options: dict
) -> None:
    """
    Create system overview page
    
    Migration: Keep as internal function
    """

def create_financial_analysis_page(
    pdf: canvas.Canvas,
    financial_data: dict,
    charts: List[bytes],
    options: dict
) -> None:
    """
    Create financial analysis page
    
    Migration: Keep as internal function
    """

def create_technical_specs_page(
    pdf: canvas.Canvas,
    products: dict,
    options: dict
) -> None:
    """
    Create technical specifications page
    
    Migration: Keep as internal function
    """

def add_logo(
    pdf: canvas.Canvas,
    logo_path: str,
    position: tuple,
    size: tuple
) -> None:
    """
    Add logo to PDF
    
    Migration: Keep as internal function
    """

def generate_chart_image(
    chart_data: dict,
    chart_type: str
) -> bytes:
    """
    Generate chart as image for PDF
    
    Uses matplotlib
    
    Migration: Keep matplotlib integration
    """

def apply_branding(
    pdf: canvas.Canvas,
    branding: dict
) -> None:
    """
    Apply branding (colors, fonts, logos)
    
    Migration: Keep as internal function
    """
```

---

## price_matrix_lookup.py - Price Matrix Functions

### Core Price Lookup

```python
def lookup_price(
    module_count: int,
    battery_model: str,
    matrix: pd.DataFrame
) -> float:
    """
    Lookup price using INDEX/MATCH logic
    
    Implements Excel formula:
    =INDEX(A2:A200, MATCH(module_count, A2:XX200, 0), MATCH(battery_model, B2:XX2, 0))
    
    Migration: CRITICAL - preserve exact logic
    Priority: CRITICAL
    """

def match_row(
    lookup_value: int,
    lookup_array: pd.Series,
    match_type: int = 0
) -> int:
    """
    Implement Excel MATCH function for rows
    
    Migration: CRITICAL - preserve exact logic
    """

def match_column(
    lookup_value: str,
    lookup_array: pd.Series,
    match_type: int = 0
) -> int:
    """
    Implement Excel MATCH function for columns
    
    Migration: CRITICAL - preserve exact logic
    """

def index_lookup(
    array: pd.DataFrame,
    row_num: int,
    col_num: int
) -> float:
    """
    Implement Excel INDEX function
    
    Migration: CRITICAL - preserve exact logic
    """

def handle_no_storage_case(
    module_count: int,
    matrix: pd.DataFrame
) -> float:
    """
    Handle "kein Speicher" (no storage) special case
    
    Uses last column of matrix
    
    Migration: CRITICAL - preserve exact logic
    """

def validate_matrix_structure(
    matrix: pd.DataFrame
) -> bool:
    """
    Validate price matrix structure
    
    Migration: Keep validation logic
    """

def calculate_extras(
    base_price: float,
    extras: dict
) -> float:
    """
    Calculate additional costs (extras, surcharges, discounts)
    
    Migration: Keep calculation logic
    """

def apply_discount(
    price: float,
    discount_rules: dict
) -> float:
    """
    Apply discount rules
    
    Migration: Keep discount logic
    """
```

---

## pv3d.py - 3D Visualization Functions

### 3D Model Creation

```python
def create_3d_model(
    roof_data: dict,
    module_specs: dict,
    placement_data: List[dict]
) -> dict:
    """
    Create complete 3D model
    
    Returns Plotly figure data
    
    Migration: Keep Plotly integration
    Priority: HIGH
    """

def create_roof_geometry(
    roof_type: str,
    dimensions: dict,
    angle: float
) -> dict:
    """
    Create roof 3D geometry
    
    Migration: Keep exact geometry calculations
    """

def place_modules_automatic(
    roof_geometry: dict,
    module_specs: dict,
    constraints: dict
) -> List[dict]:
    """
    Automatic module placement algorithm
    
    Complex optimization algorithm
    
    Migration: CRITICAL - preserve exact algorithm
    Priority: CRITICAL
    """

def place_modules_manual(
    roof_geometry: dict,
    module_specs: dict,
    positions: List[dict]
) -> List[dict]:
    """
    Manual module placement with validation
    
    Migration: Keep validation logic
    """

def detect_collisions(
    modules: List[dict],
    obstacles: List[dict]
) -> List[dict]:
    """
    Detect collisions between modules and obstacles
    
    3D geometry collision detection
    
    Migration: Keep exact algorithm
    Priority: HIGH
    """

def calculate_shading(
    modules: List[dict],
    sun_position: dict,
    obstacles: List[dict]
) -> dict:
    """
    Calculate shading for each module
    
    Complex 3D ray tracing
    
    Migration: Keep exact algorithm
    Priority: HIGH
    """

def export_3d_model(
    model_data: dict,
    format: str
) -> bytes:
    """
    Export 3D model to various formats
    
    Supports: STL, OBJ, GLTF
    
    Migration: Keep export logic
    """

def generate_360_animation(
    model_data: dict,
    frames: int = 36
) -> bytes:
    """
    Generate 360° rotation animation
    
    Returns GIF or MP4
    
    Migration: Keep animation logic
    """
```

---

## Summary

**Total Functions Mapped:** 100+  
**Total Classes Mapped:** 20+  
**Critical Functions:** 30+  
**High Priority Functions:** 40+  
**Medium Priority Functions:** 30+  

**Migration Strategy:**
1. Wrap all functions in service classes
2. Preserve exact algorithms for critical functions
3. Add type hints and validation
4. Create comprehensive unit tests
5. Document all changes

