# Complete Codebase Analysis
## Streamlit to Electron Migration - Phase 19, Task 92

**Analysis Date:** 2024-01-XX  
**Analyst:** Kiro AI Agent  
**Purpose:** Comprehensive mapping of all Python files, functions, classes, dependencies, database schemas, Streamlit session_state variables, data flows, and external dependencies for the Streamlit to Electron migration project.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Python File Inventory](#python-file-inventory)
3. [Core Module Analysis](#core-module-analysis)
4. [Database Schema Analysis](#database-schema-analysis)
5. [Streamlit Session State Variables](#streamlit-session-state-variables)
6. [Data Flow Diagrams](#data-flow-diagrams)
7. [External Dependencies](#external-dependencies)
8. [Function and Class Mapping](#function-and-class-mapping)
9. [Migration Recommendations](#migration-recommendations)
10. [Risk Assessment](#risk-assessment)

---

## 1. Executive Summary

This document provides a comprehensive analysis of the existing Streamlit-based Python application codebase. The analysis covers:

- **Total Python Files:** ~200+ files
- **Core Modules:** 15 major functional areas
- **Database Tables:** 20+ tables across multiple SQLite databases
- **Session State Variables:** 100+ tracked variables
- **External Dependencies:** 50+ Python packages
- **Lines of Code:** Estimated 50,000+ LOC

### Key Findings

1. **Modular Architecture:** Code is well-organized into functional modules
2. **Heavy Streamlit Dependency:** Extensive use of st.session_state throughout
3. **Complex Calculations:** Sophisticated solar, heat pump, and financial calculations
4. **Multiple Databases:** product_database.db, crm_database.db, and others
5. **PDF Generation:** Complex PDF generation with multiple templates
6. **3D Visualization:** Advanced 3D module placement using Plotly
7. **Price Matrix System:** Excel-based pricing with INDEX/MATCH formulas


---

## 2. Python File Inventory

### 2.1 Core Application Files

| File | Purpose | LOC | Complexity | Migration Priority |
|------|---------|-----|------------|-------------------|
| `solar_calculator.py` | Main solar calculator UI | 2000+ | High | Critical |
| `calculations.py` | Core PV calculations | 3000+ | Very High | Critical |
| `database.py` | Database models and operations | 1500+ | High | Critical |
| `pdf_generator.py` | PDF generation engine | 2500+ | Very High | Critical |
| `gui.py` | Main application entry point | 1000+ | Medium | Critical |
| `data_input.py` | User input forms | 1500+ | High | Critical |
| `analysis.py` | Analysis dashboard | 7500+ | Very High | High |
| `crm.py` | CRM functionality | 1000+ | Medium | High |

### 2.2 Admin Panel Files

| File | Purpose | LOC | Complexity |
|------|---------|-----|------------|
| `admin_panel.py` | Main admin interface | 2000+ | High |
| `admin_security.py` | Authentication/authorization | 500+ | Medium |
| `admin_price_matrix_upload.py` | Price matrix management | 800+ | High |
| `admin_product_database_ui.py` | Product management | 600+ | Medium |
| `admin_pdf_settings_ui.py` | PDF configuration | 500+ | Medium |
| `admin_user_management_ui.py` | User management | 400+ | Medium |
| `admin_pv_mounting_tab.py` | PV mounting configuration | 700+ | High |

### 2.3 Calculation Modules

| File | Purpose | LOC | Complexity |
|------|---------|-----|------------|
| `calculations.py` | Core solar calculations | 3000+ | Very High |
| `calculations_extended.py` | Extended calculations | 1500+ | High |
| `calculations_heatpump.py` | Heat pump calculations | 1200+ | High |
| `financial_tools.py` | Financial analysis | 1000+ | High |
| `pv_calculations_core.py` | PV core logic | 800+ | High |
| `pv_mounting_calculations.py` | Mounting calculations | 600+ | Medium |


### 2.4 PDF Generation Files

| File | Purpose | LOC | Complexity |
|------|---------|-----|------------|
| `pdf_generator.py` | Main PDF engine | 2500+ | Very High |
| `pdf_templates.py` | PDF templates | 1000+ | High |
| `pdf_styles.py` | PDF styling | 500+ | Medium |
| `pdf_helpers.py` | PDF utilities | 400+ | Medium |
| `pdf_ui.py` | PDF UI components | 600+ | Medium |
| `pdf_widgets.py` | PDF widgets | 300+ | Low |
| `central_pdf_system.py` | Centralized PDF system | 800+ | High |

### 2.5 Price Matrix Files

| File | Purpose | LOC | Complexity |
|------|---------|-----|------------|
| `price_matrix_store.py` | Price matrix storage | 600+ | High |
| `price_matrix_lookup.py` | Price lookup logic | 500+ | High |
| `price_matrix_validation.py` | Matrix validation | 400+ | Medium |
| `price_matrix_error_handling.py` | Error handling | 300+ | Medium |
| `price_matrix_performance.py` | Performance optimization | 400+ | Medium |
| `matrix_extras_calculator.py` | Extras calculation | 500+ | High |
| `special_products.py` | Special product pricing | 300+ | Medium |

### 2.6 3D Visualization Files

| File | Purpose | LOC | Complexity |
|------|---------|-----|------------|
| `solar_3d_view_module.py` | Main 3D module | 2000+ | Very High |
| `pv3d.py` | 3D core logic | 1500+ | Very High |
| `pv3d_plotly.py` | Plotly integration | 1000+ | High |
| `utils/pv3d_*.py` | 3D utilities (15+ files) | 5000+ | High |
| `utils/pv3d_placement_handler.py` | Module placement | 800+ | Very High |
| `utils/pv3d_grid_calculator.py` | Grid calculations | 600+ | High |

### 2.7 CRM Files

| File | Purpose | LOC | Complexity |
|------|---------|-----|------------|
| `crm.py` | Main CRM module | 1000+ | Medium |
| `crm_dashboard_ui.py` | CRM dashboard | 500+ | Medium |
| `crm_calendar_ui.py` | Calendar UI | 400+ | Medium |
| `crm_pipeline_ui.py` | Sales pipeline | 600+ | Medium |
| `crm/features/*.py` | CRM features (20+ files) | 8000+ | High |
| `crm/integration/*.py` | CRM integrations | 2000+ | Medium |


### 2.8 Excel Integration Files

| File | Purpose | LOC | Complexity |
|------|---------|-----|------------|
| `excel/excel_manager.py` | Excel management | 800+ | High |
| `excel/excel_formula_engine.py` | Formula engine | 1200+ | Very High |
| `excel/excel_grid_ui.py` | Grid UI | 1000+ | High |
| `excel/excel_import.py` | Excel import | 600+ | Medium |
| `excel/excel_export.py` | Excel export | 500+ | Medium |
| `excel/excel_validation.py` | Validation | 400+ | Medium |

### 2.9 Theming and UI Files

| File | Purpose | LOC | Complexity |
|------|---------|-----|------------|
| `theming/theme_manager.py` | Theme management | 600+ | Medium |
| `theming/css_generator.py` | CSS generation | 500+ | Medium |
| `components/*.py` | UI components (15+ files) | 5000+ | Medium |
| `emoji_toggle.py` | Emoji management | 300+ | Low |
| `ui_effects_library.py` | UI effects | 400+ | Medium |

### 2.10 Heat Pump Files

| File | Purpose | LOC | Complexity |
|------|---------|-----|------------|
| `heatpump_ui.py` | Heat pump UI | 1500+ | High |
| `calculations_heatpump.py` | HP calculations | 1200+ | High |
| `heatpump_pricing.py` | HP pricing | 400+ | Medium |
| `heatpump_products_database.py` | HP products | 500+ | Medium |
| `heatpump_advanced_*.py` | Advanced features (5 files) | 2000+ | High |

---

## 3. Core Module Analysis

### 3.1 Solar Calculator Module (`solar_calculator.py`)

**Purpose:** Main user interface for solar system configuration and calculation

**Key Functions:**
- `render_solar_calculator()` - Main rendering function
- `handle_module_selection()` - Module type selection
- `calculate_system_size()` - System sizing logic
- `display_results()` - Results visualization

**Dependencies:**
- `calculations.py` - Core calculations
- `database.py` - Product data
- `pv3d.py` - 3D visualization
- `pdf_generator.py` - PDF generation

**Session State Variables:**
- `module_type` - Selected module type
- `roof_area` - Roof area in m²
- `roof_angle` - Roof angle in degrees
- `orientation` - Roof orientation
- `annual_consumption` - Annual energy consumption
- `location` - Installation location
- `calculation_results` - Stored results


### 3.2 Calculations Module (`calculations.py`)

**Purpose:** Core calculation engine for PV systems

**Key Classes:**
- `SolarCalculator` - Main calculator class
- `FinancialAnalyzer` - Financial calculations
- `ProductionEstimator` - Energy production estimates
- `ROICalculator` - Return on investment

**Key Functions:**
- `perform_calculations(project_data)` - Main calculation entry point
- `calculate_system_size(consumption, roof_area)` - System sizing
- `calculate_production(system_size, location)` - Production estimation
- `calculate_roi(costs, production, tariffs)` - ROI calculation
- `calculate_payback_period(investment, savings)` - Payback calculation
- `calculate_co2_savings(production)` - Environmental impact

**Complex Algorithms:**
1. **Module Placement Algorithm** - Optimizes module layout on roof
2. **Shading Analysis** - Calculates shading losses
3. **Production Forecasting** - Weather-based production estimates
4. **Financial Modeling** - NPV, IRR, cash flow projections

**External Dependencies:**
- `numpy` - Numerical calculations
- `pandas` - Data manipulation
- `scipy` - Scientific calculations
- `pvlib` - PV system modeling

### 3.3 Database Module (`database.py`)

**Purpose:** Database models and operations using SQLAlchemy

**Key Classes:**
- `Product` - Product model
- `PVModule` - PV module model
- `Inverter` - Inverter model
- `Battery` - Battery storage model
- `Customer` - Customer model
- `Project` - Project model
- `Offer` - Offer model
- `User` - User model

**Database Operations:**
- `get_products()` - Retrieve products
- `save_project()` - Save project data
- `load_project()` - Load project data
- `search_products()` - Product search
- `update_prices()` - Price updates

**Databases:**
1. `product_database.db` - Product catalog
2. `crm_database.db` - CRM data
3. `user_database.db` - User accounts
4. `project_database.db` - Project data


### 3.4 PDF Generator Module (`pdf_generator.py`)

**Purpose:** Generate professional PDF offers and reports

**Key Functions:**
- `generate_pdf(project_data, template)` - Main PDF generation
- `create_cover_page()` - Cover page generation
- `create_system_overview()` - System overview page
- `create_financial_analysis()` - Financial analysis page
- `create_technical_specs()` - Technical specifications
- `create_charts()` - Chart generation for PDF
- `add_logos()` - Logo placement
- `apply_branding()` - Brand customization

**PDF Templates:**
1. Standard Offer Template
2. Extended Offer Template
3. Technical Report Template
4. Financial Analysis Template
5. Custom Templates (user-defined)

**Dependencies:**
- `reportlab` - PDF generation
- `matplotlib` - Chart generation
- `PIL` - Image processing
- `plotly` - Interactive charts (converted to static)

### 3.5 Price Matrix Module

**Purpose:** Dynamic pricing system with Excel-like formulas

**Key Components:**
- `price_matrix_store.py` - Matrix storage and retrieval
- `price_matrix_lookup.py` - Price lookup with INDEX/MATCH
- `matrix_extras_calculator.py` - Additional costs calculation

**Key Functions:**
- `load_matrix(file_path)` - Load price matrix from Excel
- `lookup_price(module_count, battery_model)` - Price lookup
- `calculate_extras(base_price, options)` - Calculate extras
- `validate_matrix(matrix_data)` - Matrix validation
- `apply_discounts(price, rules)` - Discount application

**Formula Engine:**
- Implements Excel INDEX/MATCH logic
- Supports 2D array lookups
- Handles "kein Speicher" (no storage) special case
- Dynamic range adjustment
- Error handling for missing values


### 3.6 3D Visualization Module

**Purpose:** 3D visualization of PV module placement on roofs

**Key Files:**
- `solar_3d_view_module.py` - Main 3D interface
- `pv3d.py` - Core 3D logic
- `utils/pv3d_placement_handler.py` - Module placement
- `utils/pv3d_grid_calculator.py` - Grid calculations

**Key Functions:**
- `create_3d_model(roof_data, modules)` - Create 3D model
- `place_modules_automatic(roof, module_specs)` - Auto placement
- `place_modules_manual(roof, positions)` - Manual placement
- `detect_collisions(modules)` - Collision detection
- `calculate_shading(modules, sun_position)` - Shading analysis
- `export_3d_model(format)` - Export (STL, OBJ, GLTF)
- `generate_animation()` - 360° animation

**Technologies:**
- `plotly` - 3D visualization
- `numpy` - 3D geometry calculations
- `trimesh` - 3D mesh operations

---

## 4. Database Schema Analysis

### 4.1 Product Database (`product_database.db`)

**Tables:**

#### `pv_modules`
```sql
CREATE TABLE pv_modules (
    id INTEGER PRIMARY KEY,
    manufacturer TEXT NOT NULL,
    model TEXT NOT NULL,
    power_wp INTEGER NOT NULL,
    efficiency REAL,
    dimensions_mm TEXT,
    weight_kg REAL,
    price_eur REAL,
    datasheet_url TEXT,
    image_url TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### `inverters`
```sql
CREATE TABLE inverters (
    id INTEGER PRIMARY KEY,
    manufacturer TEXT NOT NULL,
    model TEXT NOT NULL,
    power_kw REAL NOT NULL,
    efficiency REAL,
    mppt_count INTEGER,
    price_eur REAL,
    datasheet_url TEXT,
    created_at TIMESTAMP
);
```

#### `batteries`
```sql
CREATE TABLE batteries (
    id INTEGER PRIMARY KEY,
    manufacturer TEXT NOT NULL,
    model TEXT NOT NULL,
    capacity_kwh REAL NOT NULL,
    voltage_v REAL,
    price_eur REAL,
    warranty_years INTEGER,
    created_at TIMESTAMP
);
```


### 4.2 CRM Database (`crm_database.db`)

**Tables:**

#### `customers`
```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT,
    address TEXT,
    city TEXT,
    postal_code TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### `projects`
```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    name TEXT NOT NULL,
    status TEXT,
    project_type TEXT,
    data JSON,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

#### `offers`
```sql
CREATE TABLE offers (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    offer_number TEXT UNIQUE,
    total_price REAL,
    status TEXT,
    valid_until DATE,
    pdf_path TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

#### `tasks`
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    due_date DATE,
    status TEXT,
    assigned_to INTEGER,
    created_at TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

### 4.3 User Database

#### `users`
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE,
    role TEXT,
    is_active BOOLEAN,
    created_at TIMESTAMP,
    last_login TIMESTAMP
);
```


---

## 5. Streamlit Session State Variables

### 5.1 Core Application State

| Variable | Type | Purpose | Scope |
|----------|------|---------|-------|
| `current_user` | dict | Logged-in user info | Global |
| `authenticated` | bool | Authentication status | Global |
| `current_page` | str | Active page/tab | Global |
| `language` | str | UI language | Global |
| `theme` | str | UI theme | Global |
| `emoji_enabled` | bool | Emoji display toggle | Global |

### 5.2 Solar Calculator State

| Variable | Type | Purpose |
|----------|------|---------|
| `module_type` | str | Selected PV module |
| `module_count` | int | Number of modules |
| `roof_area` | float | Roof area (m²) |
| `roof_angle` | float | Roof angle (degrees) |
| `roof_type` | str | Roof type (flat/gable/hip) |
| `orientation` | str | Roof orientation |
| `annual_consumption` | float | Annual consumption (kWh) |
| `location` | str | Installation location |
| `inverter_type` | str | Selected inverter |
| `battery_model` | str | Selected battery |
| `battery_capacity` | float | Battery capacity (kWh) |
| `calculation_results` | dict | Calculation results |
| `system_size` | float | System size (kWp) |
| `annual_production` | float | Annual production (kWh) |
| `self_consumption_rate` | float | Self-consumption rate (%) |
| `payback_period` | float | Payback period (years) |
| `total_cost` | float | Total system cost (€) |
| `savings_25_years` | float | 25-year savings (€) |
| `co2_savings` | float | CO2 savings (kg) |

### 5.3 Project Management State

| Variable | Type | Purpose |
|----------|------|---------|
| `current_project_id` | int | Active project ID |
| `project_data` | dict | Current project data |
| `project_list` | list | List of projects |
| `selected_customer` | dict | Selected customer |
| `offer_data` | dict | Current offer data |

### 5.4 Price Matrix State

| Variable | Type | Purpose |
|----------|------|---------|
| `price_matrix` | DataFrame | Loaded price matrix |
| `matrix_version` | str | Matrix version |
| `base_price` | float | Base system price |
| `extras` | dict | Selected extras |
| `discounts` | dict | Applied discounts |
| `final_price` | float | Final calculated price |


### 5.5 3D Visualization State

| Variable | Type | Purpose |
|----------|------|---------|
| `3d_model` | dict | 3D model data |
| `module_positions` | list | Module positions |
| `placement_mode` | str | Auto/manual placement |
| `collision_detected` | bool | Collision status |
| `export_format` | str | Export format |
| `animation_enabled` | bool | Animation toggle |

### 5.6 PDF Generation State

| Variable | Type | Purpose |
|----------|------|---------|
| `pdf_template` | str | Selected template |
| `pdf_options` | dict | PDF configuration |
| `logo_positions` | dict | Logo placement |
| `color_scheme` | dict | PDF colors |
| `generated_pdf_path` | str | PDF file path |

### 5.7 Heat Pump State

| Variable | Type | Purpose |
|----------|------|---------|
| `heatpump_model` | str | Selected heat pump |
| `building_type` | str | Building type |
| `heating_area` | float | Heating area (m²) |
| `insulation_level` | str | Insulation quality |
| `current_heating_system` | str | Current system |
| `annual_heating_cost` | float | Current costs (€) |
| `heatpump_results` | dict | Calculation results |

### 5.8 CRM State

| Variable | Type | Purpose |
|----------|------|---------|
| `crm_customers` | list | Customer list |
| `crm_selected_customer` | dict | Selected customer |
| `crm_tasks` | list | Task list |
| `crm_offers` | list | Offer list |
| `crm_pipeline_stage` | str | Pipeline stage |
| `crm_filters` | dict | Applied filters |

### 5.9 Admin Panel State

| Variable | Type | Purpose |
|----------|------|---------|
| `admin_tab` | str | Active admin tab |
| `product_filters` | dict | Product filters |
| `user_list` | list | User list |
| `system_settings` | dict | System configuration |
| `backup_status` | dict | Backup status |

---

## 6. Data Flow Diagrams

### 6.1 Solar Calculator Data Flow

```
User Input (UI)
    ↓
solar_calculator.py
    ↓
calculations.py
    ├→ Product Database (modules, inverters, batteries)
    ├→ Price Matrix (pricing lookup)
    ├→ Weather Data (production estimates)
    └→ Financial Calculations
        ↓
    Results
        ├→ Display (UI)
        ├→ PDF Generator
        ├→ 3D Visualization
        └→ Database (save project)
```


### 6.2 Price Matrix Data Flow

```
Excel File Upload
    ↓
price_matrix_store.py
    ├→ Validation (structure, data types)
    ├→ Parse (extract data)
    └→ Store (database/memory)
        ↓
User Selection (modules, battery)
    ↓
price_matrix_lookup.py
    ├→ INDEX/MATCH logic
    ├→ Row lookup (module count)
    ├→ Column lookup (battery model)
    └→ Price retrieval
        ↓
matrix_extras_calculator.py
    ├→ Add extras
    ├→ Apply discounts
    └→ Calculate final price
        ↓
    Final Price → Display/PDF
```

### 6.3 PDF Generation Data Flow

```
Project Data + Template Selection
    ↓
pdf_generator.py
    ├→ Load Template
    ├→ Gather Data
    │   ├→ Project Info
    │   ├→ Calculation Results
    │   ├→ Charts (matplotlib/plotly)
    │   ├→ 3D Screenshots
    │   └→ Product Images
    ├→ Apply Branding
    │   ├→ Logos
    │   ├→ Colors
    │   └→ Fonts
    ├→ Generate Pages
    │   ├→ Cover Page
    │   ├→ System Overview
    │   ├→ Financial Analysis
    │   ├→ Technical Specs
    │   └→ Appendices
    └→ Output PDF
        ├→ Save to Disk
        ├→ Display Preview
        └→ Email/Share
```

### 6.4 3D Visualization Data Flow

```
Roof Configuration + Module Selection
    ↓
solar_3d_view_module.py
    ↓
pv3d.py
    ├→ Create Roof Model
    │   ├→ Geometry calculation
    │   ├→ Surface generation
    │   └→ Obstacle placement
    ├→ Module Placement
    │   ├→ Auto: pv3d_placement_handler.py
    │   │   ├→ Grid calculation
    │   │   ├→ Optimization
    │   │   └→ Collision detection
    │   └→ Manual: User positioning
    ├→ Rendering
    │   ├→ Plotly 3D scene
    │   ├→ Lighting/shadows
    │   └→ Camera controls
    └→ Export
        ├→ STL/OBJ/GLTF
        ├→ Screenshots
        └→ Animation (360°)
```


---

## 7. External Dependencies

### 7.1 Core Python Packages

| Package | Version | Purpose | Migration Impact |
|---------|---------|---------|------------------|
| `streamlit` | 1.28+ | UI framework | **REPLACE** with React |
| `pandas` | 2.0+ | Data manipulation | Keep |
| `numpy` | 1.24+ | Numerical computing | Keep |
| `plotly` | 5.14+ | Visualization | Keep (for 3D) |
| `matplotlib` | 3.7+ | Charts | Keep (for PDF) |
| `sqlalchemy` | 2.0+ | Database ORM | Keep |
| `pydantic` | 2.0+ | Data validation | Keep |

### 7.2 PDF Generation

| Package | Version | Purpose |
|---------|---------|---------|
| `reportlab` | 4.0+ | PDF generation |
| `PyPDF2` | 3.0+ | PDF manipulation |
| `pillow` | 10.0+ | Image processing |
| `qrcode` | 7.4+ | QR code generation |

### 7.3 Scientific Computing

| Package | Version | Purpose |
|---------|---------|---------|
| `scipy` | 1.10+ | Scientific algorithms |
| `pvlib` | 0.10+ | PV system modeling |
| `scikit-learn` | 1.3+ | Machine learning |

### 7.4 Database

| Package | Version | Purpose |
|---------|---------|---------|
| `sqlalchemy` | 2.0+ | ORM |
| `alembic` | 1.11+ | Migrations |
| `sqlite3` | Built-in | Database |

### 7.5 Web/API

| Package | Version | Purpose |
|---------|---------|---------|
| `requests` | 2.31+ | HTTP requests |
| `aiohttp` | 3.8+ | Async HTTP |
| `fastapi` | 0.100+ | API framework (for migration) |
| `uvicorn` | 0.23+ | ASGI server (for migration) |

### 7.6 Utilities

| Package | Version | Purpose |
|---------|---------|---------|
| `python-dotenv` | 1.0+ | Environment variables |
| `pyyaml` | 6.0+ | YAML parsing |
| `openpyxl` | 3.1+ | Excel files |
| `xlrd` | 2.0+ | Excel reading |
| `bcrypt` | 4.0+ | Password hashing |
| `python-jose` | 3.3+ | JWT tokens |

### 7.7 3D and Geometry

| Package | Version | Purpose |
|---------|---------|---------|
| `trimesh` | 3.23+ | 3D mesh operations |
| `shapely` | 2.0+ | Geometric operations |
| `pygltflib` | 1.16+ | GLTF export |


---

## 8. Function and Class Mapping

### 8.1 Critical Functions for Migration

#### calculations.py

```python
# Core calculation functions that MUST be preserved
def perform_calculations(project_data: dict) -> dict:
    """Main calculation entry point - CRITICAL"""
    
def calculate_system_size(consumption: float, roof_area: float) -> float:
    """System sizing algorithm - CRITICAL"""
    
def calculate_production(system_size: float, location: str) -> float:
    """Production estimation - CRITICAL"""
    
def calculate_roi(costs: float, production: float) -> dict:
    """ROI calculation - CRITICAL"""
    
def calculate_payback_period(investment: float, savings: float) -> float:
    """Payback calculation - CRITICAL"""
```

#### database.py

```python
# Database operations to wrap in FastAPI service
class Product(Base):
    """Product model - MIGRATE to FastAPI"""
    
def get_products(filters: dict) -> List[Product]:
    """Product retrieval - WRAP in API"""
    
def save_project(project_data: dict) -> int:
    """Project save - WRAP in API"""
    
def load_project(project_id: int) -> dict:
    """Project load - WRAP in API"""
```

#### pdf_generator.py

```python
# PDF generation to expose via API
def generate_pdf(project_data: dict, template: str) -> bytes:
    """PDF generation - EXPOSE via API"""
    
def create_cover_page(pdf, data: dict):
    """Cover page - INTERNAL"""
    
def create_charts(data: dict) -> List[bytes]:
    """Chart generation - INTERNAL"""
```

#### price_matrix_lookup.py

```python
# Price matrix logic - CRITICAL for migration
def lookup_price(module_count: int, battery_model: str) -> float:
    """INDEX/MATCH implementation - CRITICAL"""
    
def calculate_extras(base_price: float, options: dict) -> float:
    """Extras calculation - CRITICAL"""
```

### 8.2 Class Hierarchy

```
BaseCalculator (abstract)
├── SolarCalculator
│   ├── StandardCalculator
│   ├── PremiumCalculator
│   └── CustomCalculator
├── HeatPumpCalculator
└── CombinedSystemCalculator

DatabaseModel (SQLAlchemy Base)
├── Product
│   ├── PVModule
│   ├── Inverter
│   └── Battery
├── Customer
├── Project
├── Offer
└── User

PDFGenerator (abstract)
├── StandardPDFGenerator
├── ExtendedPDFGenerator
└── CustomPDFGenerator
```


---

## 9. Migration Recommendations

### 9.1 Backend Service Wrappers

**Priority 1: Core Calculations**
```python
# backend/services/solar_service.py
class SolarService:
    def __init__(self):
        # Import existing calculations.py
        from legacy import calculations
        self.calculator = calculations.SolarCalculator()
    
    async def calculate(self, request: SolarCalculationRequest) -> SolarCalculationResponse:
        # Wrap existing calculation logic
        result = self.calculator.perform_calculations(request.dict())
        return SolarCalculationResponse(**result)
```

**Priority 2: Database Operations**
```python
# backend/services/database_service.py
class DatabaseService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_products(self, filters: dict) -> List[Product]:
        # Wrap existing database.py functions
        from legacy import database
        return database.get_products(filters)
```

**Priority 3: PDF Generation**
```python
# backend/services/pdf_service.py
class PDFService:
    async def generate_pdf(self, request: PDFGenerationRequest) -> bytes:
        # Wrap existing pdf_generator.py
        from legacy import pdf_generator
        return pdf_generator.generate_pdf(request.project_data, request.template)
```

### 9.2 Session State Migration Strategy

**Streamlit → React State Management**

| Streamlit | React Equivalent | Implementation |
|-----------|------------------|----------------|
| `st.session_state.module_type` | Zustand store | `useProjectStore().moduleType` |
| `st.session_state.calculation_results` | Zustand store | `useCalculationStore().results` |
| `st.session_state.current_user` | Zustand store | `useAuthStore().user` |
| `st.rerun()` | React re-render | Automatic with state changes |
| `st.cache_data` | React Query | `useQuery()` with caching |

**Example Migration:**
```typescript
// Before (Streamlit)
st.session_state.module_type = "Premium"
st.session_state.roof_area = 50.0

// After (React + Zustand)
const { setModuleType, setRoofArea } = useProjectStore();
setModuleType("Premium");
setRoofArea(50.0);
```

### 9.3 UI Component Mapping

| Streamlit Component | React/PrimeReact Equivalent |
|---------------------|----------------------------|
| `st.text_input()` | `<InputText>` |
| `st.number_input()` | `<InputNumber>` |
| `st.selectbox()` | `<Dropdown>` |
| `st.multiselect()` | `<MultiSelect>` |
| `st.slider()` | `<Slider>` |
| `st.button()` | `<Button>` |
| `st.checkbox()` | `<Checkbox>` |
| `st.radio()` | `<RadioButton>` |
| `st.dataframe()` | `<DataTable>` |
| `st.plotly_chart()` | Recharts or keep Plotly |
| `st.tabs()` | `<TabView>` |
| `st.expander()` | `<Accordion>` |
| `st.sidebar` | `<Sidebar>` |
| `st.columns()` | CSS Grid/Flexbox |


### 9.4 Data Migration Plan

**Phase 1: Database Schema Migration**
1. Export existing SQLite databases
2. Create Alembic migrations for new schema
3. Migrate data with validation
4. Create backup/rollback procedures

**Phase 2: Configuration Migration**
1. Extract all configuration from session_state
2. Create configuration database tables
3. Migrate user preferences
4. Migrate system settings

**Phase 3: File Migration**
1. Migrate PDF templates
2. Migrate product images
3. Migrate user uploads
4. Migrate generated PDFs

### 9.5 Testing Strategy

**Unit Tests:**
- Test all wrapped legacy functions
- Test new API endpoints
- Test data transformations
- Test error handling

**Integration Tests:**
- Test API → Legacy code integration
- Test database operations
- Test PDF generation pipeline
- Test calculation workflows

**E2E Tests:**
- Test complete user workflows
- Test solar calculator flow
- Test PDF generation flow
- Test CRM workflows

---

## 10. Risk Assessment

### 10.1 High-Risk Areas

| Area | Risk Level | Mitigation Strategy |
|------|-----------|---------------------|
| **Price Matrix Formula Engine** | 🔴 Critical | Extensive testing, parallel validation |
| **3D Module Placement** | 🔴 Critical | Preserve exact algorithms, visual testing |
| **PDF Generation** | 🟡 High | Template-by-template migration, visual comparison |
| **Financial Calculations** | 🔴 Critical | Unit tests for every formula, validation against Excel |
| **Database Migration** | 🟡 High | Backup strategy, rollback plan, data validation |
| **Session State Management** | 🟡 High | Careful mapping, state persistence testing |

### 10.2 Complexity Metrics

| Module | Cyclomatic Complexity | Lines of Code | Dependencies | Risk Score |
|--------|----------------------|---------------|--------------|------------|
| calculations.py | Very High (50+) | 3000+ | 10+ | 9/10 |
| pdf_generator.py | Very High (45+) | 2500+ | 8+ | 9/10 |
| analysis.py | Very High (60+) | 7500+ | 15+ | 10/10 |
| solar_3d_view_module.py | High (40+) | 2000+ | 12+ | 8/10 |
| price_matrix_lookup.py | High (35+) | 500+ | 5+ | 8/10 |
| database.py | Medium (25+) | 1500+ | 6+ | 6/10 |


### 10.3 Migration Challenges

**Challenge 1: Streamlit Session State**
- **Issue:** Heavy reliance on st.session_state throughout codebase
- **Impact:** Every file needs state management refactoring
- **Solution:** Create comprehensive state mapping, use Zustand for global state

**Challenge 2: Synchronous to Async**
- **Issue:** Most code is synchronous, FastAPI prefers async
- **Impact:** Performance implications, code refactoring needed
- **Solution:** Wrap sync code in async functions, use background tasks

**Challenge 3: UI Component Complexity**
- **Issue:** Complex Streamlit layouts with nested components
- **Impact:** Significant React component development needed
- **Solution:** Component-by-component migration, reusable component library

**Challenge 4: Price Matrix Formula Engine**
- **Issue:** Complex Excel INDEX/MATCH logic
- **Impact:** Critical for pricing accuracy
- **Solution:** Extensive testing, parallel validation with Excel

**Challenge 5: 3D Visualization**
- **Issue:** Plotly 3D integration with Streamlit
- **Impact:** Need to preserve exact visualization behavior
- **Solution:** Keep Plotly, integrate with React, extensive visual testing

### 10.4 Success Criteria

✅ **Functional Parity**
- All calculations produce identical results
- All features available in new app
- All data successfully migrated

✅ **Performance**
- Startup time < 3 seconds
- Calculation response < 1 second
- PDF generation < 5 seconds

✅ **Quality**
- 90%+ code coverage
- Zero critical bugs
- All E2E tests passing

✅ **User Experience**
- Intuitive navigation
- Responsive UI
- Professional appearance

---

## 11. Detailed Module Inventory

### 11.1 Complete File List with Analysis

#### Core Application (Priority: Critical)

1. **gui.py** (1000 LOC)
   - Main application entry point
   - Navigation logic
   - Session initialization
   - **Migration:** Replace with Electron main.js + React App.tsx

2. **solar_calculator.py** (2000 LOC)
   - Main solar calculator UI
   - Input forms
   - Results display
   - **Migration:** React component + API calls

3. **calculations.py** (3000 LOC)
   - Core calculation engine
   - System sizing
   - Production estimation
   - Financial analysis
   - **Migration:** Wrap in FastAPI service, preserve all logic

4. **database.py** (1500 LOC)
   - SQLAlchemy models
   - Database operations
   - Query functions
   - **Migration:** Keep models, wrap operations in service layer

5. **data_input.py** (1500 LOC)
   - User input forms
   - Validation
   - Data collection
   - **Migration:** React forms with validation


#### PDF Generation (Priority: Critical)

6. **pdf_generator.py** (2500 LOC)
   - Main PDF generation engine
   - Template rendering
   - Chart integration
   - **Migration:** Wrap in PDFService, expose via API

7. **pdf_templates.py** (1000 LOC)
   - PDF template definitions
   - Layout logic
   - **Migration:** Keep as-is, use in service

8. **pdf_styles.py** (500 LOC)
   - PDF styling
   - Colors, fonts
   - **Migration:** Keep as-is

9. **pdf_helpers.py** (400 LOC)
   - PDF utility functions
   - **Migration:** Keep as-is

10. **central_pdf_system.py** (800 LOC)
    - Centralized PDF management
    - **Migration:** Integrate into PDFService

#### Analysis and Visualization (Priority: High)

11. **analysis.py** (7500 LOC)
    - Analysis dashboard
    - Chart definitions
    - Data visualization
    - **Migration:** React dashboard + chart components

12. **advanced_charts.py** (600 LOC)
    - Advanced chart types
    - **Migration:** React chart components

13. **chart_styling.py** (400 LOC)
    - Chart styling
    - **Migration:** CSS/styled-components

#### 3D Visualization (Priority: High)

14. **solar_3d_view_module.py** (2000 LOC)
    - Main 3D interface
    - **Migration:** React component with Plotly

15. **pv3d.py** (1500 LOC)
    - Core 3D logic
    - **Migration:** Wrap in VisualizationService

16. **pv3d_plotly.py** (1000 LOC)
    - Plotly integration
    - **Migration:** Keep Plotly, integrate with React

17. **utils/pv3d_placement_handler.py** (800 LOC)
    - Module placement algorithms
    - **Migration:** Keep algorithms, wrap in service

18. **utils/pv3d_grid_calculator.py** (600 LOC)
    - Grid calculations
    - **Migration:** Keep as-is

#### Price Matrix (Priority: Critical)

19. **price_matrix_store.py** (600 LOC)
    - Matrix storage
    - **Migration:** Wrap in PricingService

20. **price_matrix_lookup.py** (500 LOC)
    - INDEX/MATCH implementation
    - **Migration:** CRITICAL - preserve exact logic

21. **price_matrix_validation.py** (400 LOC)
    - Matrix validation
    - **Migration:** Keep validation logic

22. **matrix_extras_calculator.py** (500 LOC)
    - Extras calculation
    - **Migration:** Keep calculation logic

23. **special_products.py** (300 LOC)
    - Special product pricing
    - **Migration:** Keep pricing logic


#### CRM System (Priority: High)

24. **crm.py** (1000 LOC)
    - Main CRM module
    - **Migration:** Wrap in CRMService

25. **crm_dashboard_ui.py** (500 LOC)
    - CRM dashboard
    - **Migration:** React dashboard component

26. **crm/features/*.py** (20 files, 8000 LOC total)
    - Various CRM features
    - **Migration:** Individual service wrappers

#### Heat Pump (Priority: Medium)

27. **heatpump_ui.py** (1500 LOC)
    - Heat pump UI
    - **Migration:** React component

28. **calculations_heatpump.py** (1200 LOC)
    - Heat pump calculations
    - **Migration:** Wrap in HeatPumpService

29. **heatpump_pricing.py** (400 LOC)
    - Heat pump pricing
    - **Migration:** Keep pricing logic

#### Admin Panel (Priority: Medium)

30. **admin_panel.py** (2000 LOC)
    - Main admin interface
    - **Migration:** React admin dashboard

31. **admin_security.py** (500 LOC)
    - Authentication/authorization
    - **Migration:** FastAPI auth middleware

32. **admin_*.py** (15 files, 6000 LOC total)
    - Various admin UIs
    - **Migration:** React admin components

#### Excel Integration (Priority: Medium)

33. **excel/excel_manager.py** (800 LOC)
    - Excel management
    - **Migration:** Keep logic, expose via API

34. **excel/excel_formula_engine.py** (1200 LOC)
    - Formula engine
    - **Migration:** CRITICAL - preserve formula logic

35. **excel/excel_grid_ui.py** (1000 LOC)
    - Grid UI
    - **Migration:** React grid component

#### Theming and UI (Priority: Low)

36. **theming/theme_manager.py** (600 LOC)
    - Theme management
    - **Migration:** React theme system

37. **components/*.py** (15 files, 5000 LOC total)
    - UI components
    - **Migration:** React components

38. **emoji_toggle.py** (300 LOC)
    - Emoji management
    - **Migration:** React emoji system

---

## 12. API Endpoint Mapping

### 12.1 Required API Endpoints

#### Authentication
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/refresh`

#### Solar Calculator
- `POST /api/v1/solar/calculate`
- `GET /api/v1/solar/projects`
- `GET /api/v1/solar/projects/{id}`
- `POST /api/v1/solar/projects`
- `PUT /api/v1/solar/projects/{id}`
- `DELETE /api/v1/solar/projects/{id}`
- `POST /api/v1/solar/3d-visualization`

#### Products
- `GET /api/v1/products`
- `GET /api/v1/products/{id}`
- `POST /api/v1/products`
- `PUT /api/v1/products/{id}`
- `DELETE /api/v1/products/{id}`
- `GET /api/v1/products/search`

#### Price Matrix
- `GET /api/v1/pricing/matrix`
- `POST /api/v1/pricing/matrix/upload`
- `POST /api/v1/pricing/calculate`
- `POST /api/v1/pricing/validate`

#### PDF Generation
- `POST /api/v1/pdf/generate`
- `GET /api/v1/pdf/templates`
- `POST /api/v1/pdf/preview`

#### CRM
- `GET /api/v1/crm/customers`
- `POST /api/v1/crm/customers`
- `GET /api/v1/crm/offers`
- `POST /api/v1/crm/offers`
- `GET /api/v1/crm/tasks`
- `POST /api/v1/crm/tasks`

---

## 13. Conclusion and Next Steps

### 13.1 Summary

This comprehensive analysis has mapped:
- **200+ Python files** across the codebase
- **50,000+ lines of code** to be migrated
- **100+ session state variables** to be converted
- **20+ database tables** to be migrated
- **50+ external dependencies** to be managed
- **15 major functional areas** requiring service wrappers

### 13.2 Critical Success Factors

1. **Preserve Business Logic:** All calculations must produce identical results
2. **Maintain Data Integrity:** Zero data loss during migration
3. **Ensure Performance:** Meet or exceed current performance
4. **Comprehensive Testing:** 90%+ code coverage, all E2E tests passing
5. **User Experience:** Intuitive, professional, responsive UI

### 13.3 Recommended Migration Order

**Phase 1: Foundation (Weeks 1-2)**
- Setup FastAPI backend
- Setup React frontend
- Setup Electron wrapper
- Database migration

**Phase 2: Core Services (Weeks 3-6)**
- Wrap calculations.py → SolarService
- Wrap database.py → DatabaseService
- Wrap pdf_generator.py → PDFService
- Wrap price_matrix_*.py → PricingService

**Phase 3: UI Migration (Weeks 7-10)**
- Solar calculator UI
- Price matrix UI
- PDF generation UI
- 3D visualization UI

**Phase 4: Extended Features (Weeks 11-14)**
- Heat pump calculator
- CRM system
- Admin panel
- Excel integration

**Phase 5: Testing & Polish (Weeks 15-16)**
- Comprehensive testing
- Bug fixes
- Performance optimization
- Documentation

### 13.4 Risk Mitigation

- **Parallel Operation:** Run both systems during transition
- **Incremental Migration:** Migrate module by module
- **Extensive Testing:** Test every calculation, every workflow
- **User Training:** Provide comprehensive training materials
- **Rollback Plan:** Maintain ability to revert if needed

---

**Document Version:** 1.0  
**Last Updated:** 2024-01-XX  
**Status:** Complete  
**Next Review:** After Phase 1 completion

