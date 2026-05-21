# Design Document - Employee Controlling System

## Overview

Das Employee Controlling System ist ein umfassendes Modul zur Mitarbeiterverwaltung und Leistungsauswertung, das nahtlos in die bestehende Streamlit Python App integriert wird. Das System besteht aus zwei Hauptkomponenten:

1. **Controlling-Bereich** (Hauptmenü/Sidemenu): Für die tägliche Nutzung durch alle Benutzer zur Erfassung von Leistungsdaten und Erstellung von Auswertungen
2. **Controlling-Einstellungen** (Admin-Panel): Für die Konfiguration von Positionen, Auswertungskriterien und deren Zuordnungen

Das System nutzt eine SQLite-Datenbank für die persistente Speicherung aller Daten und bietet umfangreiche Export- und Archivierungsfunktionen. Alle UI-Komponenten werden mit dem Streamlit shadcn/ui Design-System gestaltet.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit App                             │
├─────────────────────────────────────────────────────────────┤
│  Hauptmenü/Sidemenu                                          │
│  ├─ Controlling (neu)                                        │
│  ├─ CRM                                                      │
│  ├─ Solar Calculator                                         │
│  └─ ...                                                      │
├─────────────────────────────────────────────────────────────┤
│  Admin-Panel                                                 │
│  ├─ Controlling Einstellungen (neu)                         │
│  ├─ Produktverwaltung                                        │
│  └─ ...                                                      │
└─────────────────────────────────────────────────────────────┘
         │                                │
         ▼                                ▼
┌──────────────────┐           ┌──────────────────┐
│ Controlling UI   │           │ Admin Settings   │
│ Module           │           │ Module           │
└──────────────────┘           └──────────────────┘
         │                                │
         └────────────┬───────────────────┘
                      ▼
         ┌────────────────────────┐
         │  Controlling Core      │
         │  - Employee Manager    │
         │  - Position Manager    │
         │  - Criteria Manager    │
         │  - Analytics Engine    │
         │  - Report Generator    │
         └────────────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │  Database Layer        │
         │  - SQLite Database     │
         │  - ORM (SQLAlchemy)    │
         └────────────────────────┘
```

### Technology Stack

- **Frontend**: Streamlit mit shadcn/ui Komponenten
- **Backend**: Python 3.10+
- **Database**: SQLite mit SQLAlchemy ORM
- **Visualization**: Plotly für Charts und Diagramme
- **Export**: ReportLab (PDF), openpyxl (Excel), json (JSON)
- **Date/Time**: datetime, dateutil für Datumsberechnungen


## Components and Interfaces

### 1. Database Models

#### Employee Model
```python
class Employee:
    id: int (Primary Key)
    first_name: str
    last_name: str
    city: str
    birth_date: date
    position_id: int (Foreign Key)
    start_date: date
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    # Computed Properties
    @property
    def age() -> int
    @property
    def days_employed() -> int
    @property
    def full_name() -> str
```

#### Position Model
```python
class Position:
    id: int (Primary Key)
    name: str (Unique)
    description: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
```

#### Criterion Model
```python
class Criterion:
    id: int (Primary Key)
    name: str (Unique)
    description: str
    calculation_method: str (Enum: SUM, AVERAGE, PERCENTAGE, RATIO)
    is_standard: bool
    created_at: datetime
    updated_at: datetime
    is_active: bool
```

#### PositionCriterion Model (Many-to-Many)
```python
class PositionCriterion:
    id: int (Primary Key)
    position_id: int (Foreign Key)
    criterion_id: int (Foreign Key)
    created_at: datetime
```

#### PerformanceData Model
```python
class PerformanceData:
    id: int (Primary Key)
    employee_id: int (Foreign Key)
    criterion_id: int (Foreign Key)
    value: float
    date: date
    created_at: datetime
    updated_at: datetime
```

#### Report Model
```python
class Report:
    id: int (Primary Key)
    employee_id: int (Foreign Key, nullable for multi-employee reports)
    report_type: str (Enum: DAILY, WEEKLY, MONTHLY, QUARTERLY, YEARLY, SINCE_START)
    start_date: date
    end_date: date
    data: JSON (Serialized report data)
    created_at: datetime
```


### 2. Core Components

#### EmployeeManager
```python
class EmployeeManager:
    def create_employee(first_name, last_name, city, birth_date, position_id, start_date) -> Employee
    def update_employee(employee_id, **kwargs) -> Employee
    def delete_employee(employee_id) -> bool
    def get_employee(employee_id) -> Employee
    def list_employees(filters=None) -> List[Employee]
    def search_employees(query) -> List[Employee]
    def calculate_age(birth_date) -> int
    def calculate_days_employed(start_date) -> int
```

#### PositionManager
```python
class PositionManager:
    def create_position(name, description) -> Position
    def update_position(position_id, **kwargs) -> Position
    def delete_position(position_id) -> bool
    def get_position(position_id) -> Position
    def list_positions() -> List[Position]
    def assign_criteria(position_id, criterion_ids) -> bool
    def remove_criteria(position_id, criterion_ids) -> bool
    def get_position_criteria(position_id) -> List[Criterion]
```

#### CriterionManager
```python
class CriterionManager:
    def create_criterion(name, description, calculation_method, is_standard=False) -> Criterion
    def update_criterion(criterion_id, **kwargs) -> Criterion
    def delete_criterion(criterion_id) -> bool
    def get_criterion(criterion_id) -> Criterion
    def list_criteria() -> List[Criterion]
    def get_standard_criteria() -> List[Criterion]
```

#### PerformanceDataManager
```python
class PerformanceDataManager:
    def record_performance(employee_id, criterion_id, value, date) -> PerformanceData
    def update_performance(performance_id, value) -> PerformanceData
    def get_performance_data(employee_id, start_date, end_date, criterion_ids=None) -> List[PerformanceData]
    def bulk_record_performance(employee_id, data_dict, date) -> List[PerformanceData]
```


#### AnalyticsEngine
```python
class AnalyticsEngine:
    def calculate_quotas(performance_data, criteria_mapping) -> Dict[str, float]
    def calculate_ratio_description(quota_percentage, criterion_name) -> str
    def aggregate_data(performance_data, period_type) -> Dict
    def calculate_comparison(employees, start_date, end_date) -> Dict
    
    # Quota Calculations
    def calculate_abschlussquote(verkauf, angefahrene_termine_gesamt) -> float
    def calculate_terminvereinbarungsquote(kunden_terminiert, getaetigte_anrufe_gesamt) -> float
    def calculate_anfahrquote(angefahrene_termine, kunden_terminiert) -> float
    def calculate_nicht_interessiert_quote(storniert_kein_interesse, angefahrene_termine_gesamt) -> float
    def calculate_technisch_nicht_machbar_quote(technisch_nicht_machbar, angefahrene_termine_gesamt) -> float
    def calculate_nicht_erreicht_quote(nicht_erreicht, getaetigte_anrufe_gesamt) -> float
    def calculate_folgetermin_quote(folgetermin_gemacht, angefahrene_termine_gesamt) -> float
    def calculate_angebot_quote(angebot_erhalten, angefahrene_termine_gesamt) -> float
    def calculate_zu_teuer_quote(zu_teuer, angefahrene_termine_gesamt) -> float
    def calculate_qc_bestanden_quote(qc_bestanden, verkauf) -> float
```

#### ReportGenerator
```python
class ReportGenerator:
    def generate_report(employee_id, report_type, start_date=None, end_date=None) -> Report
    def generate_comparison_report(employee_ids, report_type, start_date=None, end_date=None) -> Report
    def save_report(report) -> int
    def load_report(report_id) -> Report
    def list_reports(filters=None) -> List[Report]
    def export_report_pdf(report) -> bytes
    def export_report_excel(report) -> bytes
    def export_report_json(report) -> str
```

#### ChartGenerator
```python
class ChartGenerator:
    def create_bar_chart(data, title, x_label, y_label) -> plotly.Figure
    def create_column_chart(data, title, x_label, y_label) -> plotly.Figure
    def create_donut_chart(data, title) -> plotly.Figure
    def create_dashboard(report_data) -> List[plotly.Figure]
    def apply_shadcn_theme(figure) -> plotly.Figure
```


### 3. UI Components

#### Controlling Main UI (controlling_ui.py)
```python
def render_controlling_page():
    """Main controlling page in Hauptmenü/Sidemenu"""
    - Employee selection with filters
    - Performance data entry form
    - Report generation controls
    - Report visualization dashboard
    - Export buttons
    - Archive access

def render_employee_selector(filters):
    """Employee selection with filtering"""
    - Multi-select for employees
    - Filters: Position, Name, City, Start Date
    - Search functionality

def render_performance_entry_form(employee, criteria):
    """Form for entering performance data"""
    - Dynamic form based on employee's position criteria
    - Date selector
    - Numeric inputs for each criterion
    - Bulk save functionality

def render_report_controls():
    """Controls for report generation"""
    - Report type selector (Daily, Weekly, Monthly, Quarterly, Yearly, Since Start)
    - Date range picker
    - Generate button
    - Save report button

def render_report_dashboard(report_data):
    """Dashboard displaying report visualizations"""
    - Multiple charts in grid layout
    - Quota cards with percentages
    - Ratio descriptions
    - Interactive tooltips

def render_archive_browser():
    """Browser for saved reports"""
    - List of saved reports
    - Filters and search
    - Load and export buttons
```


#### Admin Controlling Settings UI (admin_controlling_settings_ui.py)
```python
def render_admin_controlling_settings():
    """Main admin settings page with password protection"""
    - Password authentication
    - Tab navigation: Employees, Positions, Criteria, Assignments

def render_employee_management_tab():
    """Employee CRUD operations"""
    - Employee list with edit/delete actions
    - Add employee form
    - Employee details view

def render_position_management_tab():
    """Position CRUD operations"""
    - Position list with edit/delete actions
    - Add position form
    - Warning on delete if employees assigned

def render_criterion_management_tab():
    """Criterion CRUD operations"""
    - Criterion list (standard + custom)
    - Add criterion form
    - Edit/delete actions
    - Calculation method selector

def render_assignment_tab():
    """Position-Criterion assignments"""
    - Position selector
    - Available criteria list
    - Assigned criteria list
    - Drag-and-drop or checkbox assignment
```


## Data Models

### Standard Criteria

The system provides 14 standard criteria that are pre-configured:

1. **Kunden terminiert**: Number of customers scheduled for appointments
2. **QC bestanden**: Number of quality control checks passed
3. **Storniert / kein Interesse**: Number of cancelled or uninterested customers
4. **Nicht erreicht / neu terminieren**: Number of customers not reached requiring rescheduling
5. **Technisch nicht machbar**: Number of technically unfeasible projects
6. **Angefahrene Termine**: Number of appointments attended
7. **Nicht angefahrene Termine**: Number of appointments not attended
8. **Verkauf**: Number of sales completed
9. **Folgetermin gemacht**: Number of follow-up appointments scheduled
10. **Zu teuer gewesen**: Number of customers who found pricing too high
11. **Angebot erhalten**: Number of quotes provided
12. **Getätigte Anrufe gesamt**: Total number of calls made
13. **Angefahrene Termine gesamt**: Total number of appointments attended
14. **Sonstiges**: Miscellaneous activities

### Quota Definitions

Quotas are calculated as percentages based on the following formulas:

1. **Abschlussquote** = (Verkauf / Angefahrene Termine gesamt) × 100
2. **Terminvereinbarungsquote** = (Kunden terminiert / Getätigte Anrufe gesamt) × 100
3. **Termine-Anfahrquote** = (Angefahrene Termine / Kunden terminiert) × 100
4. **Nicht interessierte Kunden Quote** = (Storniert/kein Interesse / Angefahrene Termine gesamt) × 100
5. **Technisch nicht machbar Quote** = (Technisch nicht machbar / Angefahrene Termine gesamt) × 100
6. **Quote der nicht erreichten Kunden** = (Nicht erreicht / Getätigte Anrufe gesamt) × 100
7. **Quote für Folgetermine-Vereinbarungen** = (Folgetermin gemacht / Angefahrene Termine gesamt) × 100
8. **Quote für Angebote** = (Angebot erhalten / Angefahrene Termine gesamt) × 100
9. **Quote für zu teuer** = (Zu teuer / Angefahrene Termine gesamt) × 100
10. **Quote für QC bestanden** = (QC bestanden / Verkauf) × 100

### Ratio Descriptions

For each quota, a descriptive ratio is calculated:
- Formula: `1 : (100 / quota_percentage)`
- Example: If Abschlussquote = 25%, then "Jeder 4. angefahrene Termin ist ein Verkauf"
- Example: If Terminvereinbarungsquote = 10%, then "Jeder 10. Anruf führt zu einem Termin"


### Report Types and Date Ranges

#### Daily Report
- Start Date: Selected date
- End Date: Selected date
- Aggregation: Sum of all values for the selected date

#### Weekly Report
- Start Date: Monday of selected week
- End Date: Sunday of selected week
- Aggregation: Sum of all values for the week

#### Monthly Report
- Start Date: First day of selected month
- End Date: Last day of selected month
- Aggregation: Sum of all values for the month

#### Quarterly Report
- Q1: January 1 - March 31
- Q2: April 1 - June 30
- Q3: July 1 - September 30
- Q4: October 1 - December 31
- Aggregation: Sum of all values for the quarter

#### Yearly Report
- Start Date: January 1 of selected year
- End Date: December 31 of selected year
- Aggregation: Sum of all values for the year

#### Since Start Report
- Start Date: Employee's start_date
- End Date: Current date
- Aggregation: Sum of all values since employment began


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Employee Data Persistence Round-Trip
*For any* valid employee with all required fields (first_name, last_name, city, birth_date, position_id, start_date), saving the employee to the database and then retrieving it should return an employee with identical field values.
**Validates: Requirements 2.1, 2.5**

### Property 2: Age Calculation Correctness
*For any* birth date in the past, the calculated age should equal the difference in years between the birth date and the current date, accounting for whether the birthday has occurred this year.
**Validates: Requirements 2.2**

### Property 3: Days Employed Calculation Correctness
*For any* start date in the past, the calculated days employed should equal the number of calendar days between the start date and the current date.
**Validates: Requirements 2.3**

### Property 4: Employee Retrieval Completeness
*For any* employee stored in the database, retrieving that employee by ID should return all stored fields without data loss.
**Validates: Requirements 3.1**

### Property 5: Employee Update Persistence
*For any* employee and any valid field updates, updating the employee and then retrieving it should reflect all the changes made.
**Validates: Requirements 3.2**

### Property 6: Employee Deletion Archival
*For any* employee, deleting that employee should result in the employee being marked as inactive (is_active=False) and not appearing in the active employee list.
**Validates: Requirements 3.3**

### Property 7: Position Name Uniqueness
*For any* two positions in the database, their names should be distinct (case-insensitive comparison).
**Validates: Requirements 4.1**

### Property 8: Position Update Persistence
*For any* position and any valid field updates, updating the position and then retrieving it should reflect all the changes made.
**Validates: Requirements 4.2**

### Property 9: Position Deletion Protection
*For any* position that has at least one employee assigned, attempting to delete that position should either fail with an error or require reassignment of all employees.
**Validates: Requirements 4.3, 4.5**

### Property 10: Criterion Name Uniqueness
*For any* two criteria in the database, their names should be distinct (case-insensitive comparison).
**Validates: Requirements 5.1**

### Property 11: Criterion Update Persistence
*For any* criterion and any valid field updates, updating the criterion and then retrieving it should reflect all the changes made.
**Validates: Requirements 5.3**

### Property 12: Criterion Deletion Protection
*For any* criterion that is assigned to at least one position, attempting to delete that criterion should either fail with an error or show a warning.
**Validates: Requirements 5.4**

### Property 13: Position Criteria Display Completeness
*For any* position, retrieving the available criteria should return all criteria in the database.
**Validates: Requirements 6.1**

### Property 14: Position-Criterion Assignment Persistence
*For any* position and set of criteria, assigning those criteria to the position and then retrieving the position's criteria should return exactly the assigned criteria.
**Validates: Requirements 6.2**

### Property 15: Position-Criterion Removal Persistence
*For any* position with assigned criteria, removing a criterion and then retrieving the position's criteria should not include the removed criterion.
**Validates: Requirements 6.3**

### Property 16: Employee Criteria Inheritance
*For any* employee assigned to a position, the employee should have access to all criteria assigned to that position.
**Validates: Requirements 6.5**

### Property 17: Non-Admin Access Denial
*For any* user without admin privileges, attempting to access the controlling settings should be denied.
**Validates: Requirements 7.4**

### Property 18: Employee Criteria Display
*For any* employee, displaying their performance entry form should show all criteria assigned to their position.
**Validates: Requirements 8.1**

### Property 19: Performance Data Numeric Validation
*For any* performance data input, the system should only accept numeric values (integers or floats) and reject non-numeric inputs.
**Validates: Requirements 8.2**

### Property 20: Performance Data Persistence with Timestamp
*For any* performance data entry, saving it should store the data with a timestamp, and retrieving it should return the same values with the correct timestamp.
**Validates: Requirements 8.3**

### Property 21: Performance Data Employee-Date Association
*For any* performance data, it should be correctly associated with the specified employee ID and date, and retrieving data for that employee and date should include the saved entry.
**Validates: Requirements 8.5**

### Property 22: Report Time Period Data Retrieval
*For any* time period (start_date, end_date) and employee, retrieving performance data for that period should return only data where the date falls within the specified range (inclusive).
**Validates: Requirements 9.2**

### Property 23: Performance Data Grouping by Criteria
*For any* set of performance data, grouping by criterion should result in all data for each criterion being grouped together with no data loss.
**Validates: Requirements 9.3**

### Property 24: Report Calculation Uses Correct Criteria
*For any* report generation, the calculations should only use criteria that are assigned to the employee's position.
**Validates: Requirements 9.5**

### Property 25: All Quotas Calculated
*For any* report with sufficient performance data, all 10 standard quotas (Abschlussquote, Terminvereinbarungsquote, Termine-Anfahrquote, nicht interessierte Kunden Quote, technisch nicht machbar Quote, Quote der nicht erreichten Kunden, Quote für Folgetermine-Vereinbarungen, Quote für Angebote, Quote für zu teuer, Quote für QC bestanden) should be calculated and included in the report.
**Validates: Requirements 10.1**

### Property 26: Quota Calculation Formula Correctness
*For any* performance data with non-zero denominators, each quota should be calculated as (numerator / denominator) × 100, where numerator and denominator are the appropriate criteria values.
**Validates: Requirements 10.2**

### Property 27: Quota Sum Invariant
*For any* set of mutually exclusive quotas that should sum to 100%, the sum of those quotas should equal 100% (within floating-point tolerance).
**Validates: Requirements 10.3**

### Property 28: Ratio Description Generation
*For any* quota greater than 0%, a ratio description should be generated in the format "Jeder X. [context] ist [outcome]" where X = round(100 / quota_percentage).
**Validates: Requirements 11.1**

### Property 29: Ratio Calculation Formula
*For any* quota percentage Q > 0, the ratio X should be calculated as X = 100 / Q, representing "1 in X" occurrences.
**Validates: Requirements 11.2**

### Property 30: Ratio Descriptions for All Quotas
*For any* report with calculated quotas, a ratio description should be provided for each quota.
**Validates: Requirements 11.4**

### Property 31: Chart Generation Completeness
*For any* report, generating visualizations should produce at least one bar chart, one column chart, and one donut chart.
**Validates: Requirements 12.1**

### Property 32: Chart Data Completeness
*For any* report, all criteria and quotas in the report data should be represented in at least one of the generated charts.
**Validates: Requirements 12.3**

### Property 33: Report Saving Persistence
*For any* report, saving it to the database and then retrieving it should return a report with identical data, timestamp, and employee association.
**Validates: Requirements 13.2**

### Property 34: Report Archival Completeness
*For any* report being saved, all components (charts data, quotas, raw performance data) should be serialized and stored in the database.
**Validates: Requirements 13.3**

### Property 35: Saved Reports Retrieval
*For any* set of saved reports in the database, listing all reports should return all saved reports without omission.
**Validates: Requirements 13.5**

### Property 36: Export Format Support
*For any* report, export functions should be available for all three formats: PDF, Excel, and JSON.
**Validates: Requirements 14.1**

### Property 37: PDF Export Completeness
*For any* report exported to PDF, the PDF should contain representations of all charts, all quota tables, and all descriptive text from the report.
**Validates: Requirements 14.2**

### Property 38: Excel Export Completeness
*For any* report exported to Excel, the Excel file should contain all raw performance data and all calculated quotas in structured tables.
**Validates: Requirements 14.3**

### Property 39: JSON Export Round-Trip
*For any* report, exporting to JSON and then parsing the JSON should produce a data structure equivalent to the original report data.
**Validates: Requirements 14.4**

### Property 40: Report Loading Restoration
*For any* saved report, loading it from the database should restore all charts data, tables, and metadata in their original form.
**Validates: Requirements 15.1, 15.2**

### Property 41: Loaded Report Metadata Display
*For any* loaded report, the displayed report should include the time period (start_date, end_date) and creation timestamp.
**Validates: Requirements 15.3**

### Property 42: Employee List Display with Positions
*For any* set of active employees, displaying the employee list should show each employee with their associated position name.
**Validates: Requirements 16.1**

### Property 43: Employee Filtering Correctness
*For any* filter criteria (position, name, city, or start_date), applying the filter should return only employees that match the criteria, and all matching employees should be included.
**Validates: Requirements 16.2**

### Property 44: Filtered Report Inclusion
*For any* active filter, generating a report should only include performance data for employees that match the filter criteria.
**Validates: Requirements 16.3**

### Property 45: Archive Chronological Sorting
*For any* set of saved reports, listing them from the archive should return reports sorted by creation timestamp in descending order (newest first).
**Validates: Requirements 18.1**

### Property 46: Historical Report Data Integrity
*For any* historical report, loading it should return the exact data that was saved, with no modifications or data loss.
**Validates: Requirements 18.2**

### Property 47: Criterion Calculation Method Assignment
*For any* criterion, assigning a calculation method and then retrieving the criterion should return the criterion with the assigned calculation method.
**Validates: Requirements 19.1, 19.3**

### Property 48: Report Uses Assigned Calculation Methods
*For any* report, calculations for each criterion should use the calculation method assigned to that criterion at the time of report generation.
**Validates: Requirements 19.4**

### Property 49: Calculation Method Change Effect
*For any* criterion, changing its calculation method should result in future reports using the new method while historical reports remain unchanged.
**Validates: Requirements 19.5**

### Property 50: Comparison Report Multi-Employee Support
*For any* set of 2 to 10 employees, generating a comparison report should include data for all selected employees.
**Validates: Requirements 20.1**

### Property 51: Comparison Report Metric Completeness
*For any* comparison report, all quotas and metrics should be calculated and displayed for each employee in the comparison.
**Validates: Requirements 20.2**

### Property 52: Comparison Report Archival
*For any* comparison report being saved, all employee IDs included in the comparison should be stored in the report metadata.
**Validates: Requirements 20.5**

### Property 53: Quota Threshold Notification
*For any* employee and quota, if the quota exceeds a configured threshold, a notification should be generated.
**Validates: Requirements 21.1**

### Property 54: Quota Threshold Warning
*For any* employee and quota, if the quota falls below a configured threshold, a warning should be generated.
**Validates: Requirements 21.2**


## Error Handling

### Input Validation Errors
- **Invalid Date Formats**: Birth dates and start dates must be valid dates in the past
- **Invalid Numeric Values**: Performance data must be non-negative numbers
- **Missing Required Fields**: All required fields must be provided when creating employees, positions, or criteria
- **Duplicate Names**: Position and criterion names must be unique

### Business Logic Errors
- **Position Deletion with Employees**: Prevent deletion of positions that have employees assigned
- **Criterion Deletion with Assignments**: Warn when deleting criteria that are assigned to positions
- **Division by Zero**: Handle cases where quota denominators are zero (display 0% or "keine Daten")
- **Invalid Date Ranges**: Ensure start_date <= end_date for reports

### Database Errors
- **Connection Failures**: Gracefully handle database connection issues
- **Transaction Failures**: Rollback transactions on errors
- **Constraint Violations**: Handle unique constraint violations with user-friendly messages

### Authentication Errors
- **Invalid Password**: Display error message for incorrect admin password
- **Unauthorized Access**: Deny access to admin features for non-admin users
- **Session Expiration**: Handle expired sessions gracefully

### Export Errors
- **File Generation Failures**: Handle errors during PDF, Excel, or JSON generation
- **Insufficient Data**: Handle cases where reports have insufficient data for certain visualizations
- **Large Data Sets**: Handle memory issues with very large exports


## Testing Strategy

### Unit Testing

Unit tests will verify specific functionality and edge cases:

**Employee Management Tests:**
- Test employee creation with valid data
- Test employee creation with invalid data (missing fields, invalid dates)
- Test employee update operations
- Test employee deletion and archival
- Test age calculation with various birth dates (including leap years, edge of year)
- Test days employed calculation with various start dates

**Position Management Tests:**
- Test position creation with unique names
- Test position creation with duplicate names (should fail)
- Test position update operations
- Test position deletion with and without assigned employees

**Criterion Management Tests:**
- Test criterion creation with unique names
- Test standard criteria initialization
- Test custom criterion creation
- Test criterion deletion with and without position assignments

**Performance Data Tests:**
- Test performance data recording with valid values
- Test performance data recording with invalid values (negative, non-numeric)
- Test performance data retrieval for various date ranges
- Test bulk performance data recording

**Analytics Tests:**
- Test quota calculations with various data sets
- Test quota calculations with zero denominators
- Test ratio description generation
- Test report aggregation for different time periods

**Report Tests:**
- Test report generation for all report types (daily, weekly, monthly, quarterly, yearly, since start)
- Test report saving and loading
- Test report export to PDF, Excel, JSON
- Test comparison report generation

### Property-Based Testing

Property-based tests will verify universal properties across many randomly generated inputs. We will use the **Hypothesis** library for Python property-based testing, configured to run a minimum of 100 iterations per test.

Each property-based test will be tagged with a comment explicitly referencing the correctness property from the design document using this format: `# Feature: employee-controlling-system, Property {number}: {property_text}`

**Key Property-Based Tests:**

1. **Employee Data Round-Trip** (Property 1): For any valid employee data, save→load should preserve all fields
2. **Age Calculation** (Property 2): For any past birth date, age calculation should be correct
3. **Days Employed Calculation** (Property 3): For any past start date, days employed should be correct
4. **Quota Calculations** (Properties 26, 27): For any performance data, quota formulas should be correct and sum appropriately
5. **Ratio Calculations** (Property 29): For any quota > 0%, ratio calculation should follow the formula
6. **Date Range Filtering** (Property 22): For any date range, only data within range should be retrieved
7. **Export Round-Trip** (Property 39): For any report, JSON export→parse should preserve data
8. **Filter Correctness** (Property 43): For any filter criteria, all and only matching employees should be returned

### Integration Testing

Integration tests will verify the interaction between components:

- Test complete workflow: Create employee → Record performance → Generate report → Export
- Test admin workflow: Create position → Create criteria → Assign criteria → Create employee
- Test UI integration: Verify Streamlit components render correctly with data
- Test database transactions: Verify rollback on errors
- Test authentication flow: Verify password protection and session management

### Performance Testing

- Test report generation with 100+ employees
- Test database queries with large datasets
- Test export generation with large reports
- Verify caching mechanisms improve performance

