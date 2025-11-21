# Data Flow Diagrams
## Complete System Data Flows

---

## 1. Solar Calculator Complete Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│  (Streamlit → React Migration)                                   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT VALIDATION                              │
│  - Roof area (10-500 m²)                                        │
│  - Roof angle (0-90°)                                           │
│  - Annual consumption (1000-50000 kWh)                          │
│  - Location (German postal codes)                               │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PRODUCT SELECTION                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ PV Modules   │  │  Inverters   │  │  Batteries   │         │
│  │ Database     │  │  Database    │  │  Database    │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                 │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 CORE CALCULATIONS                                │
│  (calculations.py)                                               │
│                                                                  │
│  1. System Sizing                                               │
│     ├─ Calculate optimal kWp                                    │
│     ├─ Calculate module count                                   │
│     └─ Validate roof capacity                                   │
│                                                                  │
│  2. Production Estimation                                       │
│     ├─ Get solar radiation data (pvlib)                        │
│     ├─ Apply orientation factor                                │
│     ├─ Apply tilt angle factor                                 │
│     ├─ Apply shading losses                                    │
│     └─ Calculate annual production                             │
│                                                                  │
│  3. Self-Consumption Analysis                                   │
│     ├─ Calculate consumption profile                           │
│     ├─ Calculate production profile                            │
│     ├─ Calculate overlap                                       │
│     └─ Apply battery storage effect                            │
│                                                                  │
│  4. Financial Analysis                                          │
│     ├─ Get system cost (Price Matrix)                         │
│     ├─ Calculate annual savings                                │
│     ├─ Calculate feed-in revenue                               │
│     ├─ Calculate ROI                                           │
│     ├─ Calculate payback period                                │
│     ├─ Calculate NPV                                           │
│     └─ Calculate IRR                                           │
│                                                                  │
│  5. Environmental Impact                                        │
│     ├─ Calculate CO2 savings                                   │
│     └─ Calculate equivalent trees                              │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PRICE MATRIX LOOKUP                           │
│  (price_matrix_lookup.py)                                       │
│                                                                  │
│  Input: module_count, battery_model                            │
│                                                                  │
│  1. Load Price Matrix                                           │
│     └─ Excel file → pandas DataFrame                           │
│                                                                  │
│  2. Row Lookup (MATCH)                                          │
│     └─ Find row where module_count matches                     │
│                                                                  │
│  3. Column Lookup (MATCH)                                       │
│     └─ Find column where battery_model matches                 │
│                                                                  │
│  4. Price Retrieval (INDEX)                                     │
│     └─ Get value at [row, column]                              │
│                                                                  │
│  5. Extras Calculation                                          │
│     ├─ Add selected extras                                     │
│     ├─ Apply discounts                                         │
│     └─ Calculate final price                                   │
│                                                                  │
│  Output: total_system_cost                                      │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    3D VISUALIZATION                              │
│  (pv3d.py, solar_3d_view_module.py)                            │
│                                                                  │
│  1. Roof Model Creation                                         │
│     ├─ Create roof geometry (flat/gable/hip)                   │
│     ├─ Add obstacles (chimneys, windows)                       │
│     └─ Define boundaries                                       │
│                                                                  │
│  2. Module Placement                                            │
│     ├─ Automatic Placement:                                    │
│     │  ├─ Grid calculation                                     │
│     │  ├─ Optimization algorithm                               │
│     │  └─ Collision detection                                  │
│     └─ Manual Placement:                                       │
│        └─ User positioning with validation                     │
│                                                                  │
│  3. Rendering                                                   │
│     ├─ Create Plotly 3D scene                                  │
│     ├─ Add lighting and shadows                                │
│     └─ Add camera controls                                     │
│                                                                  │
│  4. Export                                                      │
│     ├─ Screenshot (PNG)                                        │
│     ├─ 3D Model (STL/OBJ/GLTF)                                │
│     └─ Animation (GIF/MP4)                                     │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RESULTS DISPLAY                               │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  System Overview                                          │  │
│  │  - System size: X.X kWp                                  │  │
│  │  - Module count: XX modules                              │  │
│  │  - Annual production: X,XXX kWh                          │  │
│  │  - Self-consumption: XX%                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Financial Analysis                                       │  │
│  │  - Total cost: XX,XXX €                                  │  │
│  │  - Annual savings: X,XXX €                               │  │
│  │  - Payback period: X.X years                             │  │
│  │  - 25-year savings: XXX,XXX €                            │  │
│  │  - ROI: XX%                                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Charts                                                   │  │
│  │  - Production vs Consumption                             │  │
│  │  - Cash Flow Over Time                                   │  │
│  │  - Savings Breakdown                                     │  │
│  │  - CO2 Savings                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  3D Visualization                                         │  │
│  │  - Interactive 3D model                                  │  │
│  │  - Module placement                                      │  │
│  │  - Export options                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    USER ACTIONS                                  │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Save Project │  │ Generate PDF │  │ Export Data  │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                  │
│         ▼                  ▼                  ▼                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Database   │  │ PDF Generator│  │ Excel Export │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

