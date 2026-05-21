# Copilot Instructions - ARSCHIBALD (Bokuk2)

## Project Overview
**ARSCHIBALD** (Ömers All in One Dingsbums) ist eine Enterprise-Anwendung für Photovoltaik- und Wärmepumpen-Konfiguration mit automatisierter PDF-Angebotserstellung, 3D-Visualisierung, CRM-Integration und Mitarbeiter-Controlling. 

**Technologie-Stack**:
- **Frontend**: Streamlit 1.49.1 (Multi-Page-App)
- **Backend**: Python 3.13
- **Datenbank**: SQLite3 (embedded)
- **PDF**: ReportLab 4.4.3 + PyPDF2
- **3D**: PyVista 0.43+ (VTK-basiert)
- **Build**: PyInstaller + Inno Setup

**Haupteinstiegspunkt**: `gui.py` (4633 Zeilen) - Orchestriert alle Module mit Fail-Safe Loading Pattern

## Architecture & Core Systems

### 1. PDF Generation System (Multi-Firma)
**Kritisch**: Firmen-spezifische PDF-Generierung mit dynamischen Overlays und Produkt-Rotation.

**Zentrale Dateien**:
- `pdf_template_engine/dynamic_overlay.py`: Hauptlogik für Text-Overlays mit ReportLab
- `pdf_generator.py`: End-to-end PDF-Erstellung
- `product_rotation_engine.py`: Automatische Produktvariation für Multi-Angebote
- `price_modification_engine.py`: Progressive Preiskalkulation (modifier + progression)

**Template-System**:
```
coords_multi/seite{N}_f{X}.yml   # Firma-spezifische Koordinaten (f1-f7)
pdf_templates_static/multi/multi_nt_{N}_f{X}.pdf  # Firma-Backgrounds (Seite 1-8)
```

**Wichtig**:
- Koordinaten sind `(x1, y1, x2, y2)` in PDF-Einheiten (ReportLab A4)
- Rechtsbündige Preise: Nutze `drawRightString(x2, y, text)` NICHT `drawString(x1, y, text)`
- Platzhalter-Mapping: `PLACEHOLDER_MAPPING` in `pdf_template_engine/placeholders.py`
- Text-Alignment via Listen: `right_align_tokens_s7`, `right_align_tokens_s8_static` in `dynamic_overlay.py`

**Workflow**:
1. `generate_multi_offer_pdfs()` orchestriert Multi-Firma-Batch
2. `rotate_products()` variiert Hersteller/Modelle zwischen Firmen (product_rotation_engine.py)
3. `calculate_price_with_products()` berechnet kaskadierende Preise (Firma 1: +15%, weitere: +5% progressiv)
4. `generate_multi_firm_pdf()` erstellt firma-spezifische PDFs mit `coords_multi/` und `multi/` Templates

**Product Rotation Engine** (`product_rotation_engine.py`):
```python
def rotate_products(
    original_products: Dict[str, dict],
    used_brands: Set[str],
    firm_index: int
) -> Dict[str, dict]:
    """Rotiert Produkte zu anderen Marken.
    - Gleiche Spezifikationen (±10% Toleranz)
    - Bevorzugt unbenutzte Marken
    - WR + Speicher: Gleiche Marke wenn möglich
    """
    # Lade alle verfügbaren Produkte
    all_products = load_all_products()  # → product_db.list_products()
    
    # Für jede Kategorie: Finde Alternative
    rotated = {}
    for category, original in original_products.items():
        candidates = find_similar_products(
            original, 
            all_products[category],
            exclude_brands=used_brands
        )
        rotated[category] = candidates[0] if candidates else original
    
    return rotated
```

**Price Modification Engine** (`price_modification_engine.py`):
```python
def apply_modification(
    base_price: float,
    modifier_pct: float,    # z.B. 15% für Firma 1
    firm_index: int = 0,
    progression_pct: float = 5  # +5% pro weitere Firma
) -> float:
    """Progressive Preisanpassung für Multi-PDFs.
    
    Formel: base * (1 + (modifier + progression * firm_index) / 100)
    Beispiel:
    - Firma 1: 100€ * 1.15 = 115€  (+15%)
    - Firma 2: 100€ * 1.20 = 120€  (+20%)
    - Firma 3: 100€ * 1.25 = 125€  (+25%)
    """
    total_modifier = modifier_pct + (progression_pct * firm_index)
    return base_price * (1 + total_modifier / 100)
```

### 2. Database System (SQLite)
**Hauptdatei**: `database.py` (2900+ Zeilen) - Zentrales Datenbank-Modul

**Tabellen-Struktur**:
- **CRM**: `customers`, `projects`, `crm_leads`, `crm_tasks`, `crm_activities`
- **Produkte**: `products` (PV-Module, Wechselrichter, Speicher, etc.)
- **Preise**: `price_matrices`, `pricing_rules`, `profit_margins`
- **PDF-Archiv**: `customer_documents`, `project_calculations`
- **Verträge**: `contracts`, `warranties` (siehe `crm/features/contract_manager.py`)

### 2a. Product Database System (product_db.py)
**Hauptdatei**: `product_db.py` (1811 Zeilen) - Produktdatenbank-Verwaltung

**Core Functions**:
```python
from product_db import (
    list_products,              # Produkte auflisten mit Filtern
    add_product,                # Neues Produkt hinzufügen
    update_product,             # Produkt aktualisieren
    delete_product,             # Produkt löschen
    get_product_by_id,          # Produkt per ID laden
    get_product_by_model_name,  # Produkt per Modellname
    list_product_categories     # Kategorien auflisten
)

# Produkt-Schema
product = {
    'category': 'PV-Modul',        # REQUIRED
    'model_name': 'Vertex S 400W',  # REQUIRED, UNIQUE
    'brand': 'Trina Solar',
    'price_euro': 120.50,
    'capacity_w': 400,
    'power_kw': 0.4,
    'efficiency_percent': 21.5,
    'warranty_years': 25,
    'length_m': 1.754,
    'width_m': 1.096,
    'weight_kg': 21.0,
    # Enhanced Pricing Fields
    'calculate_per': 'Stück',       # Berechnungsbasis
    'purchase_price_net': 95.00,    # EK netto
    'margin_type': 'percentage',    # oder 'fixed'
    'margin_value': 20.0,           # 20% Marge
    'is_special_product': 0,        # Matrix-Preislogik
    # PV-Modul Details
    'cell_technology': 'Monokristallin N-Type TOPCon',
    'module_structure': 'Glas-Glas',
    'cell_type': '108 Halbzellen',
    'version': 'All-Black',
    'module_warranty_text': '25 Jahre Produktgarantie'
}
```

**Wichtige Patterns**:
```python
# Liste mit Paginierung
products = list_products(
    category='PV-Modul',
    page=1,
    per_page=50,
    search_term='Trina'
)

# Mit dynamischen Pricing-Keys
from product_db import get_products_with_dynamic_keys
products_with_keys = get_products_with_dynamic_keys(
    category='PV-Modul',
    include_pricing=True
)

# Enhanced Pricing Calculation
from product_db import calculate_enhanced_product_pricing
pricing = calculate_enhanced_product_pricing(
    product_id=123,
    quantity=20,
    pricing_mode='matrix'  # oder 'direct'
)
```

**Tabellen-Migration**:
```python
def _migrate_product_table_columns(conn: sqlite3.Connection):
    """Fügt fehlende Spalten automatisch hinzu"""
    expected_columns = {
        'cell_technology': 'TEXT',
        'calculate_per': 'TEXT',
        'purchase_price_net': 'REAL',
        'margin_value': 'REAL',
        'is_special_product': 'INTEGER',
        # ... 30+ weitere Felder
    }
    
    # Prüfe existierende Spalten
    cursor.execute("PRAGMA table_info(products)")
    existing = {row[1] for row in cursor.fetchall()}
    
    # Füge fehlende hinzu
    for col, type in expected_columns.items():
        if col not in existing:
            cursor.execute(
                f"ALTER TABLE products ADD COLUMN {col} {type} DEFAULT ..."
            )
```

**Monitoring Integration**:
```python
from app_tracing import app_tracer

@app_tracer(operation_name="product_db.list_products")
def list_products(category=None, page=1, per_page=50):
    # Business Logic
    pass
```

**Konventionen**:
```python
# IMMER Row Factory verwenden
conn.row_factory = sqlite3.Row

# Migrations mit PRAGMA
cursor.execute("PRAGMA table_info(customers)")
# Dann ALTER TABLE ADD COLUMN falls fehlt
```

**Datenbankzugriff**:
- `get_db_connection()` gibt Connection mit Row Factory
- Pfad: `data/app_data.db` (konfigurierbar via `DB_PATH`)
- Monitoring via `@trace_database` Decorator (optional)

**Schema-Versioning**:
```python
DB_SCHEMA_VERSION = 14  # Aktuell in database.py

def init_db(conn):
    """Initialisiert/Migriert Datenbank"""
    cursor = conn.cursor()
    
    # Prüfe existierende Spalten
    cursor.execute("PRAGMA table_info(customers)")
    existing_cols = {row[1] for row in cursor.fetchall()}
    
    # Füge fehlende Spalten hinzu (KEIN DROP TABLE!)
    if 'email' not in existing_cols:
        cursor.execute(
            "ALTER TABLE customers ADD COLUMN email TEXT"
        )
    
    # Schema-Version speichern
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_info (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    cursor.execute(
        "INSERT OR REPLACE INTO schema_info VALUES (?, ?)",
        ('version', str(DB_SCHEMA_VERSION))
    )
    conn.commit()
```

**CRM-Datenmodell** (Erweitert):
```python
# Kern-Tabellen
customers → projects → crm_activities
    ↓           ↓
 crm_leads   contracts/warranties
    ↓
customer_documents

# Wichtige Beziehungen
- customers.id → projects.customer_id (1:N)
- projects.id → contracts.project_id (1:N)
- projects.id → warranties.project_id (1:N)
- customer_documents.customer_id → customers.id (N:1)
```

### 3. Admin Security System
**Hauptdateien**: `admin_security.py` (358 Zeilen), `authentication.py` (150 Zeilen)

**Passwortschutz für Admin-Bereiche**:
```python
from admin_security import (
    require_admin_auth,          # Authentifizierung erzwingen
    verify_admin_password,       # Passwort prüfen
    is_area_protected,           # Bereichsschutz-Status
    get_admin_protected_areas,   # Geschützte Bereiche laden
    save_admin_protected_areas   # Schutz-Konfiguration speichern
)

# Pattern: Admin-Bereich schützen
def render_protected_admin_section():
    """Geschützter Admin-Bereich mit Passwort"""
    
    # Prüfe Authentifizierung
    if not require_admin_auth(
        area_id='product_database',
        area_name='Produktdatenbank'
    ):
        return  # Zeigt Login-Dialog, blockiert Zugriff
    
    # Authentifiziert - zeige Admin-UI
    st.header("Produktdatenbank")
    # ... Admin-Logik
```

**Geschützte Bereiche** (Standardkonfiguration):
```python
PROTECTED_AREAS = {
    'build_infos': True,           # Build-Infos
    'user_management': True,       # Benutzerverwaltung
    'company_management': True,    # Firmenverwaltung
    'product_management': True,    # Produktverwaltung
    'product_database': True,      # Produktdatenbank CRUD
    'pv_mounting': True,           # PV-Unterkonstruktionen
    'services_management': True,   # Dienstleistungen
    'price_matrix': True,          # Preis-Matrizen
    'controlling_settings': True,  # Controlling
    'heatpump_settings': True,     # Wärmepumpen
    'logo_management': True,       # Logo-Verwaltung
    'pdf_settings': True,          # PDF-Vorlagen
}
```

**Owner-Bypass** (Hardcoded Super-Admin):
```python
def is_owner(username: str, password: str) -> bool:
    """Besitzer hat IMMER Zugriff (Bypass)"""
    OWNER_USERNAME = "TSchwarz"
    OWNER_PASSWORD = "Timur2014"
    return username == OWNER_USERNAME and password == OWNER_PASSWORD
```

**Authentication Manager** (`authentication.py`):
```python
from authentication import AuthenticationManager

auth_mgr = AuthenticationManager(db_path="data/app_data.db")

# Benutzer anlegen
auth_mgr.create_user(
    username="admin",
    password="secret123",
    email="admin@example.com",
    role="admin"
)

# Credentials prüfen
user = auth_mgr.verify_credentials("admin", "secret123")
if user:
    st.session_state['authenticated_user'] = user
    st.session_state['is_admin'] = True

# Passwort ändern
auth_mgr.change_password(
    username="admin",
    old_password="secret123",
    new_password="newsecret456"
)
```

**Password Hashing**:
```python
import hashlib
import secrets

def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """PBKDF2-HMAC SHA256 mit 100.000 Iterationen"""
    if salt is None:
        salt = secrets.token_hex(32)
    
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # Iterationen
    ).hex()
    
    return password_hash, salt
```

**Session State Integration**:
```python
# Nach erfolgreichem Login
if verify_admin_password(username, password):
    st.session_state[f'admin_auth_{area_id}'] = True
    st.session_state['admin_username'] = username
    st.rerun()

# Logout
if st.button("Abmelden"):
    for key in list(st.session_state.keys()):
        if key.startswith('admin_auth_'):
            del st.session_state[key]
    st.rerun()
```

### 4. Streamlit Session State Management
**KRITISCH**: Session State ist **pickle-serializable** erforderlich!

**Pattern für custom Classes**:
```python
class MyClass:
    def __getstate__(self):
        """Ermöglicht Pickle-Serialisierung für Session State"""
        return self.__dict__.copy()
    
    def __setstate__(self, state):
        """Ermöglicht Pickle-Deserialisierung für Session State"""
        self.__dict__.update(state)
```

**Session State Konventionen**:
- `st.session_state['calculation_results']`: Berechnungsergebnisse
- `st.session_state['project_data']`: Aktuelles Projekt
- `st.session_state['crm_view_mode']`: CRM Navigation ('list', 'detail', 'add_customer', etc.)
- `st.session_state['selected_customer_id']`: Aktiver Kunde

**Core Module**: `core/session.py` - Session persistence & navigation tracking

### 4. Navigation & Routing System
**Dateien**: `core/router.py`, `core/navigation_history.py`

**Pattern**:
```python
from core.router import get_router, navigate

router = get_router()
navigate('crm', params={'customer_id': 123})  # Navigate with params
router.go_back()  # Browser-style navigation
```

**Breadcrumbs**: `render_breadcrumbs()` für Navigation-Historie

## Core Integration System

### Feature Flags
**Datei**: `core_integration.py` - Zentrales Feature-Toggle-System

**Verfügbare Features**:
- `config`: Konfigurationsverwaltung
- `logging`: Strukturiertes Logging
- `cache`: Performance-Caching
- `session`: Session-Persistenz
- `database`: DB Connection Pooling
- `security`: Authentifizierung & Authorization
- `router`: Multi-Page Routing
- `navigation`: Browser-Style History
- `jobs`: Background Job Scheduler
- `migrations`: Database Migrations
- `cache_extensions`: Cache-Erweiterungen
- `db_extensions`: DB-Erweiterungen
- `di_container`: Dependency Injection

**Aktivierung via ENV**:
```bash
FEATURE_CONFIG=true
FEATURE_LOGGING=true
FEATURE_ROUTER=true
# Alle Features default: true
```

**Usage Pattern**:
```python
from core_integration import is_feature_enabled, log_info

if is_feature_enabled('logging'):
    log_info("my_operation", data={"key": "value"})
```

### Core Module: Router (`core/router.py` - 834 Zeilen)
**Pattern**: Browser-Style Navigation mit History & Guards

```python
from core.router import get_router, navigate

# Navigation mit Parametern
router = get_router()
navigate('crm', params={'customer_id': 123})
router.go_back()  # Browser-style zurück

# Navigation Guards
class AuthGuard(NavigationGuard):
    def can_navigate(self, to_page: str, params: dict) -> tuple[bool, str | None]:
        if not st.session_state.get('authenticated'):
            return False, "Login erforderlich"
        return True, None

router.add_guard(AuthGuard())

# Navigation Events
@dataclass
class NavigationEvent:
    event_id: str
    event_type: NavigationEventType  # NAVIGATE, BACK, FORWARD, REDIRECT
    from_page: str | None
    to_page: str
    params: dict[str, Any]
    timestamp: datetime
```

### Core Module: Session (`core/session.py` - 668 Zeilen)
**Pattern**: Enhanced Session Management mit Persistence

```python
from core.session import SessionManager, FormSnapshot

# Session Recovery nach Browser-Refresh
from core_integration import bootstrap_session

session_id_param = st.query_params.get('session_id')
user_session = bootstrap_session(
    session_id=session_id_param,
    user_id=st.session_state.get('user_id')
)

if user_session:
    st.toast("Sitzung wiederhergestellt")

# Form Snapshots (Undo/Redo)
@dataclass
class FormSnapshot:
    snapshot_id: str
    form_id: str
    data: dict[str, Any]
    timestamp: datetime
    description: str = ""

# Navigation History
@dataclass
class NavigationEntry:
    page: str
    params: dict[str, Any]
    timestamp: datetime
```

### Core Module: Form Manager (`core/form_manager.py` - 1620 Zeilen)
**Pattern**: Enterprise-Grade Form Validation & State

```python
from core.form_manager import FormManager, FormState

form_mgr = FormManager()

# Form mit Validierung
form_state = form_mgr.create_form(
    form_id='customer_form',
    fields={
        'name': {'type': 'text', 'required': True, 'min_length': 3},
        'email': {'type': 'email', 'required': True},
        'age': {'type': 'number', 'min': 18, 'max': 120}
    }
)

# Validierung
errors = form_mgr.validate(form_state)
if not errors:
    form_mgr.submit(form_state)

# Snapshots für Undo/Redo
form_mgr.create_snapshot(form_state, description="Before changes")
form_mgr.restore_snapshot(snapshot_id)
```

### Core Module: Jobs (`core/jobs.py`)
**Pattern**: Background Job Scheduling

```python
from core.jobs import JobManager

job_mgr = JobManager()

# Cron-basierte Jobs
job_mgr.schedule_job(
    name="contract_expiry_check",
    func=check_expiring_contracts,
    trigger="cron",
    hour=8,
    minute=0
)

# Intervall-basierte Jobs
job_mgr.schedule_job(
    name="cache_warmup",
    func=warmup_cache,
    trigger="interval",
    hours=1
)
```

### Core Module: Security (`core/security.py`)
**Pattern**: Role-Based Access Control

```python
from core.security import SecurityManager, Permission

security = SecurityManager()

# Permission Checks
@security.requires_permission(Permission.ADMIN)
def admin_function():
    pass

# Role-Based Access
if security.has_role(user_id, 'admin'):
    render_admin_panel()
```

## Environment Variables & Configuration

### Environment Setup
**Datei**: `.env.example` - Template für Konfiguration

**Kritische Variablen**:
```bash
# OpenAI (REQUIRED für KAI Agent)
OPENAI_API_KEY=sk-...

# Optional Features
TAVILY_API_KEY=tvly-...      # Web-Search
TWILIO_ACCOUNT_SID=AC...     # Telephony (simuliert)
ELEVEN_LABS_API_KEY=...      # Voice Synthesis

# Feature Toggles (alle default: true)
FEATURE_CONFIG=true
FEATURE_LOGGING=true
FEATURE_CACHE=true
FEATURE_SESSION_PERSISTENCE=true
FEATURE_DATABASE_POOLING=true
FEATURE_SECURITY=true
FEATURE_ROUTER=true
FEATURE_NAVIGATION_HISTORY=true
FEATURE_JOBS=true
FEATURE_MIGRATIONS=true
FEATURE_CACHE_EXTENSIONS=true
FEATURE_DB_EXTENSIONS=true
FEATURE_DI_CONTAINER=true
```

**Setup**:
```bash
# 1. Kopiere Template
cp .env.example .env

# 2. Fülle API Keys ein
# WICHTIG: .env NIEMALS committen!
```

**Zugriffspattern**:
```python
import os
from core_integration import is_feature_enabled

# Feature Check
if is_feature_enabled('logging'):
    # Use feature
    
# Environment Variable
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    # Fallback oder Fehler
```

## Developer Workflows

### Running the App
```powershell
# Standard Start (öffnet Browser automatisch)
streamlit run gui.py

# Mit spezifischem Port
$env:STREAMLIT_SERVER_PORT="8502"; streamlit run gui.py

# Admin Panel (Extended Dashboard)
streamlit run admin_core_status_extended_ui.py

# Video-Server wird automatisch im Hintergrund gestartet
# Prüfe Status: http://localhost:8503/health
```

**Config**: `.streamlit/config.toml`
- `headless = false` → Browser öffnet automatisch
- `gatherUsageStats = false` → Kein Telemetry
- `toolbarMode = "minimal"` → Produktions-UI ohne Dev-Toolbar
- `serverPort = 8501` → Standard Streamlit-Port

**Wichtig**: 
- Video-Server läuft parallel auf Port 8503+
- Bei Port-Konflikt: Server findet automatisch nächsten freien Port
- Beide Server (Streamlit + Video) müssen laufen für Intro-Screen

### Testing
```powershell
# Unit Tests
pytest tests/ -v

# Spezifische Test-Suites
pytest tests/test_crm_integration.py
pytest tests/test_pdf_generation.py
pytest tests/test_agent_isolation.py
```

### Database Migrations
```python
# Automatisch bei App-Start via init_db()
from database import get_db_connection, init_db

conn = get_db_connection()
init_db(conn)  # Erstellt/migriert alle Tabellen
```

### Cache Management
```powershell
# Streamlit Cache löschen
python "nützliche tools/cache_leerer.py"

# Python Cache
python clear_python_cache.py
```

## Project-Specific Patterns

### 1. Module Loading (Fail-Safe Pattern)
**IMMER** mit Fallback laden:
```python
def import_module_with_fallback(module_name, error_dict):
    try:
        return importlib.import_module(module_name)
    except Exception as e:
        error_dict[module_name] = str(e)
        return None

# Usage
crm_module = import_module_with_fallback("crm", import_errors)
if crm_module and callable(getattr(crm_module, 'render_crm', None)):
    crm_module.render_crm(...)
else:
    st.warning("CRM nicht verfügbar")
```

### 2. Text/Lokalisierung
**Datei**: `locales.py` - Zentrales i18n-System

```python
from locales import get_text

# Mit Fallback
text = get_text("crm_tab_customers", "Kunden")
```

### 3. Deutsche Formatierung (Zahlen)
**Datei**: `german_formatting.py` - Zentrales Formatierungs-Modul

**IMMER** deutsche Formatierung verwenden:
```python
from german_formatting import (
    format_currency,      # → "23.403,11 €"
    format_percentage,    # → "25,5 %"
    format_kwh,          # → "10.234 kWh"
    format_kwp,          # → "9,8 kWp"
    format_years,        # → "15,2 Jahre"
    format_ct_kwh        # → "28,50 ct/kWh"
)

# Usage
price = format_currency(95464.18)  # → "95.464,18 €"
efficiency = format_percentage(25.5)  # → "25,5 %"
yield_kwh = format_kwh(10234)  # → "10.234 kWh"

# Custom Formatting
from german_formatting import format_german_number
value = format_german_number(23403.11, decimals=2, unit="kWp")
# → "23.403,11 kWp"
```

**Wichtig**:
- NIEMALS englische Formatierung (23,403.11) verwenden
- Immer Tausendertrenner (Punkt) und Dezimaltrenner (Komma)
- In PDF-Generation: Preise MÜSSEN deutsche Formatierung haben

**Pattern (DEPRECATED - Nutze german_formatting.py)**:
```python
# ALT (nur wenn german_formatting.py nicht verfügbar)
formatted = f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
# Beispiel: 95464.18 → "95.464,18 €"
```

### 4. PDF Coordinate Parsing
**Datei**: `pdf_template_engine/dynamic_overlay.py`

```python
def parse_coords_file(path: Path) -> list[dict]:
    """
    Liest seiteX.yml und gibt Elemente zurück:
    - Text: Platzhalter-Name
    - Position: (x0, y0, x1, y1)  # Bottom-left, Top-right
    - Schriftart: "Helvetica-Bold"
    - Schriftgröße: 9.989105224609375
    - Farbe: 3487029 (0xRRGGBB)
    """
```

**Text-Rendering**:
```python
# Links: drawString(x0, y, text)
# Rechts: drawRightString(x2, y, text)  # Wichtig für Preise!
# Zentriert: drawCentredString((x0+x2)/2, y, text)
```

### 5. Shadcn-UI Integration (Optional)
**Datei**: `components/shadcn_ui_integration.py` (1290 Zeilen)

**Verfügbare Komponenten** (mit Streamlit Fallbacks):
```python
from components.shadcn_ui_integration import (
    button,          # Button-Komponente
    badge,           # Badge (Status-Chip)
    card,            # Card-Layout
    alert,           # Alert-Nachrichten
    input_field,     # Input mit Label
    select,          # Dropdown-Select
    checkbox,        # Checkbox
    switch,          # Toggle-Switch
    slider,          # Range-Slider
    tabs,            # Tab-Navigation
    accordion,       # Accordion/Collapse
    dialog,          # Modal-Dialog
    is_available     # Prüft ob shadcn verfügbar
)

# Verfügbarkeit prüfen
if is_available():
    st.info(f"Using shadcn-ui version {get_version()}")
else:
    st.warning("Using Streamlit fallback components")
```

**Pattern: Button mit Varianten**:
```python
# Shadcn-Style Button
if button(
    text="Speichern",
    key="save_btn",
    variant="default",  # default, destructive, outline, secondary, ghost, link
    size="lg",          # default, sm, lg, icon
    disabled=False
):
    save_data()

# Fallback zu st.button wenn shadcn nicht verfügbar
```

**Pattern: Badge für Status**:
```python
badge(
    text="Aktiv",
    variant="default",  # default, secondary, destructive, outline
    key="status_badge"
)
```

**Pattern: Card-Layout**:
```python
with card(
    title="Kundendaten",
    description="Verwaltung der Kundeninformationen",
    key="customer_card"
):
    st.text_input("Name", key="name")
    st.text_input("E-Mail", key="email")
```

**Pattern: Alert-Nachrichten**:
```python
alert(
    title="Erfolg",
    description="Daten wurden erfolgreich gespeichert",
    variant="success",  # info, success, warning, error
    dismissible=True,
    key="success_alert"
)
```

**Graceful Degradation**:
```python
def button(text, key=None, variant="default", size="default", **kwargs):
    """Shadcn-Button mit Streamlit-Fallback"""
    if SHADCN_UI_AVAILABLE:
        try:
            return ui.button(
                text=text,
                key=key,
                variant=variant,
                size=size,
                **kwargs
            )
        except Exception as e:
            logger.error(f"Shadcn error: {e}")
            # Fallback
    
    # Native Streamlit als Fallback
    return st.button(text, key=key, **kwargs)
```

**Integration in GUI**:
```python
# In gui.py oder anderen Modulen
try:
    from components.shadcn_ui_integration import button, card, badge
    SHADCN_AVAILABLE = True
except ImportError:
    SHADCN_AVAILABLE = False
    # Use native Streamlit components
    button = st.button
```

### 6. Monitoring & Tracing (Optional)
```python
from app_tracing import app_tracer
from app_evaluation import track_success, track_error

@app_tracer(operation_name="generate_pdf")
def my_function():
    try:
        result = ...
        track_success("generate_pdf")
        return result
    except Exception as e:
        track_error("generate_pdf", str(e))
        raise
```

### 7. Error Handling & Validation
**Pattern**: Graceful Degradation mit Fallbacks

```python
# Module Loading mit Fehlerbehandlung
try:
    from optional_module import feature
    FEATURE_AVAILABLE = True
except ImportError as e:
    FEATURE_AVAILABLE = False
    print(f"Optional feature nicht verfügbar: {e}")
    
    # Fallback implementieren
    def feature(*args, **kwargs):
        return None  # oder Dummy-Implementation

# Usage
if FEATURE_AVAILABLE:
    result = feature()
else:
    st.warning("Feature nicht verfügbar")
```

**Custom Exceptions** (nach Bedarf):
```python
class ValidationError(Exception):
    """Validierungsfehler"""
    pass

class DatabaseError(Exception):
    """Datenbankfehler"""
    pass

# Usage
if period.status == PeriodStatus.LOCKED:
    raise ValidationError("Period is locked")
```

**Error Tracking**:
```python
# Sammle Fehler in zentraler Liste
from app_status import import_errors

try:
    risky_operation()
except Exception as e:
    error_msg = f"Operation fehlgeschlagen: {e}"
    import_errors.append(error_msg)
    # Weiter mit Fallback
```

### 8. Excel Integration
**Hauptdateien**: `excel_exporter.py`, `excel_processing.py`, `excel_grid_ui.py`

**Export-Pattern**:
```python
from excel_exporter import export_to_excel
import pandas as pd

# DataFrame Export
df = pd.DataFrame(data)
export_to_excel(
    df, 
    filename='export.xlsx',
    sheet_name='Data',
    include_index=False
)
```

**Import-Pattern**:
```python
from excel_processing import import_excel_data
import openpyxl

# Excel Datei lesen
wb = openpyxl.load_workbook('input.xlsx')
ws = wb.active

# Daten extrahieren
data = []
for row in ws.iter_rows(min_row=2, values_only=True):
    data.append(row)

# Als DataFrame
df = pd.DataFrame(data, columns=['col1', 'col2'])
```

**Grid-UI**:
```python
from excel_grid_ui import render_excel_grid

# Streamlit Excel-Grid rendern
df = render_excel_grid(
    data=initial_data,
    editable=True,
    key="excel_grid"
)

# Geänderte Daten verarbeiten
if df is not None:
    save_data(df)
```

## Critical Gotchas

### PDF System
1. **Koordinaten-System**: ReportLab nutzt Bottom-Left Origin, YAML speichert (x1, y1, x2, y2)
   ```python
   # FALSCH: drawString nutzt Top-Left Koordinate
   c.drawString(x1, y1, text)
   
   # RICHTIG: y-Position ist IMMER vom unteren Rand
   c.drawString(x1, y, text)  # y von unten!
   ```

2. **Multi-Firma-Pfade**: Template-Suffix muss `f{index+1}` sein (f1, f2, nicht f0, f1)
   ```python
   # FALSCH
   template_path = f"pdf_templates_static/multi/multi_nt_{page}_f{firm_index}.pdf"
   
   # RICHTIG (Index + 1!)
   template_path = f"pdf_templates_static/multi/multi_nt_{page}_f{firm_index + 1}.pdf"
   ```

3. **Rechtsbündigkeit**: Preisfelder MÜSSEN in `right_align_tokens_s7` Liste für korrekte €-Ausrichtung
   ```python
   # In dynamic_overlay.py
   right_align_tokens_s7 = [
       'Gesamtpreis_brutto',
       'Gesamtpreis_netto',
       'Mwst_betrag',
       'Anzahlung',
       'Restzahlung'
   ]
   
   # Rendering
   if placeholder_name in right_align_tokens_s7:
       c.drawRightString(x2, y, text)  # x2 = rechter Rand!
   else:
       c.drawString(x1, y, text)  # x1 = linker Rand
   ```

4. **Font-Namen**: Nur ReportLab-Fonts nutzen (Helvetica, Helvetica-Bold, Times-Roman, etc.)
   ```python
   # ERLAUBT
   c.setFont("Helvetica", 10)
   c.setFont("Helvetica-Bold", 12)
   c.setFont("Times-Roman", 10)
   
   # VERBOTEN (führt zu Fehler)
   c.setFont("Arial", 10)  # Arial nicht verfügbar!
   c.setFont("Calibri", 10)  # Calibri nicht verfügbar!
   ```

5. **YAML-Koordinaten Parsing**:
   ```python
   # coords_multi/seite1_f1.yml Format
   # Position: [x1, y1, x2, y2]  # Bottom-left zu Top-right
   # y-Werte MÜSSEN invertiert werden für Top-Down Layouts!
   
   y_inverted = page_height - y  # Für Top-Down Layouts
   ```

### Database
1. **Row Factory**: Vergiss NIEMALS `conn.row_factory = sqlite3.Row`
   ```python
   # FALSCH - Dict-Access funktioniert nicht
   conn = get_db_connection()
   cursor = conn.cursor()
   row = cursor.fetchone()
   name = row['name']  # KeyError!
   
   # RICHTIG
   conn = get_db_connection()
   conn.row_factory = sqlite3.Row  # KRITISCH!
   cursor = conn.cursor()
   row = cursor.fetchone()
   name = row['name']  # Funktioniert
   ```

2. **Migrations**: Nutze `PRAGMA table_info()` + `ALTER TABLE` NICHT `DROP TABLE`
   ```python
   # FALSCH - Datenverlust!
   cursor.execute("DROP TABLE IF EXISTS customers")
   cursor.execute("CREATE TABLE customers (...)")
   
   # RICHTIG - Prüfe und erweitere
   cursor.execute("PRAGMA table_info(customers)")
   cols = {row[1] for row in cursor.fetchall()}
   
   if 'new_column' not in cols:
       cursor.execute("ALTER TABLE customers ADD COLUMN new_column TEXT")
   ```

3. **Transactions**: Immer `conn.commit()` bei INSERT/UPDATE/DELETE
   ```python
   # FALSCH - Änderungen gehen verloren
   cursor.execute("INSERT INTO customers VALUES (...)")
   # Kein commit() → Rollback bei Connection Close!
   
   # RICHTIG
   cursor.execute("INSERT INTO customers VALUES (...)")
   conn.commit()  # KRITISCH!
   ```

4. **SQL Injection**: IMMER Parameterized Queries
   ```python
   # FALSCH - SQL Injection möglich!
   query = f"SELECT * FROM customers WHERE name = '{name}'"
   cursor.execute(query)
   
   # RICHTIG - Parameterized Query
   cursor.execute(
       "SELECT * FROM customers WHERE name = ?",
       (name,)  # Tuple mit trailing comma!
   )
   ```

### Streamlit
1. **Session State**: Custom Classes brauchen `__getstate__` / `__setstate__`
   ```python
   # FALSCH - PicklingError!
   class MyClass:
       def __init__(self):
           self.data = {}
   
   st.session_state['obj'] = MyClass()  # Fehler bei Rerun!
   
   # RICHTIG - Pickle-Serialisierbar
   class MyClass:
       def __getstate__(self):
           return self.__dict__.copy()
       
       def __setstate__(self, state):
           self.__dict__.update(state)
   
   st.session_state['obj'] = MyClass()  # Funktioniert
   ```

2. **Widget Keys**: Eindeutige Keys für alle Widgets (`key=f"btn_{id}"`)
   ```python
   # FALSCH - DuplicateWidgetID Error!
   for i in range(5):
       st.button("Click me")  # Alle haben gleichen implicit key!
   
   # RICHTIG
   for i in range(5):
       st.button("Click me", key=f"btn_{i}")
   ```

3. **Rerun**: Nach Session State Änderung: `st.rerun()` NICHT `st.experimental_rerun()`
   ```python
   # DEPRECATED (Alt)
   st.session_state['counter'] += 1
   st.experimental_rerun()
   
   # AKTUELL (Streamlit >= 1.27)
   st.session_state['counter'] += 1
   st.rerun()
   ```

4. **Cache Invalidation**:
   ```python
   # Problem: Cache wird nicht invalidiert bei Datenänderung
   @st.cache_data
   def load_data():
       return db.query("SELECT * FROM table")
   
   # Lösung: TTL oder Hash Parameter
   @st.cache_data(ttl=60)  # Cache 60 Sekunden
   def load_data(last_modified: str):  # Hash-Parameter
       return db.query("SELECT * FROM table")
   
   # Usage
   data = load_data(str(datetime.now().timestamp()))
   ```

### CRM
1. **Kunden/Projekte**: Getrennte Tabellen mit Foreign Key `customer_id`
   ```python
   # FALSCH - Projekt ohne Kunde
   project = {
       'name': 'Solar Installation',
       'address': '...'
   }
   save_project(project)  # customer_id fehlt!
   
   # RICHTIG - Immer mit Kunden-Referenz
   project = {
       'customer_id': 123,  # REQUIRED
       'name': 'Solar Installation',
       'address': '...'
   }
   save_project(project)
   ```

2. **Dokumente**: File-System Ablage in `customer_documents/` PLUS DB-Referenz
   ```python
   # Workflow
   # 1. Speichere Datei
   filepath = save_document_file(customer_id, file_data)
   # → customer_documents/{customer_id}/document.pdf
   
   # 2. Speichere DB-Referenz
   doc_id = add_customer_document(conn, {
       'customer_id': customer_id,
       'filepath': filepath,
       'filename': 'document.pdf',
       'doc_type': 'contract'
   })
   
   # NIEMALS nur Datei ODER nur DB-Eintrag!
   ```

3. **View Modes**: Navigation via `st.session_state['crm_view_mode']`
   ```python
   # Pattern für View-Navigation
   def handle_navigation(new_view: str, **params):
       st.session_state['crm_view_mode'] = new_view
       
       # Speichere zusätzliche Parameter
       for key, value in params.items():
           st.session_state[f'crm_{key}'] = value
       
       st.rerun()
   
   # Usage
   if st.button("Kunde ansehen"):
       handle_navigation('detail', selected_customer_id=customer_id)
   ```

### 3D Visualization
1. **PyVista Memory Leaks**: Immer `plotter.close()` aufrufen
   ```python
   # FALSCH - Memory Leak!
   def render_3d():
       plotter = pv.Plotter()
       plotter.add_mesh(mesh)
       plotter.show()
       # plotter bleibt im Speicher!
   
   # RICHTIG
   def render_3d():
       plotter = pv.Plotter()
       try:
           plotter.add_mesh(mesh)
           plotter.show()
       finally:
           plotter.close()  # KRITISCH!
   ```

2. **Mesh Normals**: Falsche Normals → unsichtbare Flächen
   ```python
   # Problem prüfen
   mesh = pv.PolyData(points, faces)
   if not mesh.is_all_triangles():
       mesh = mesh.triangulate()
   
   # Normals berechnen
   mesh.compute_normals(inplace=True)
   
   # Normals umdrehen wenn nötig
   if mesh_appears_black:
       mesh.flip_normals()
   ```

3. **Coordinate System**: PyVista nutzt rechte Hand Regel (Z nach oben)
   ```python
   # Standard Koordinaten-System
   # X: Rechts
   # Y: Vorne (Depth)
   # Z: Oben (Height)
   
   # Dach-Position: Z ist HÖHE, nicht Tiefe!
   roof_height = 5  # 5 Meter HOCH
   position = (x, y, roof_height)  # Z = Höhe!
   ```

### Controlling System
1. **Decimal Precision**: Verwende `Decimal` für Geld-Beträge
   ```python
   # FALSCH - Float-Rundungsfehler
   sales = 10000.10 + 0.20  # 10000.299999999999
   
   # RICHTIG
   from decimal import Decimal
   sales = Decimal('10000.10') + Decimal('0.20')  # 10000.30
   ```

2. **Period Locking**: Locked Periods dürfen nicht editiert werden
   ```python
   def save_performance_data(period_id, data):
       period = get_period(period_id)
       
       # KRITISCH: Prüfe Status
       if period.status == PeriodStatus.LOCKED:
           raise ValidationError("Period is locked")
       
       # Speichere
       save_data(data)
   ```

3. **Team Hierarchies**: Rekursion mit Depth Limit
   ```python
   # FALSCH - Unendliche Rekursion möglich
   def get_team_members(team_id):
       team = get_team(team_id)
       members = team.members
       
       for sub_team in team.sub_teams:
           members.extend(get_team_members(sub_team.id))
       
       return members
   
   # RICHTIG - Mit Depth Limit
   def get_team_members(team_id, max_depth=5, current_depth=0):
       if current_depth >= max_depth:
           raise ValueError("Max hierarchy depth exceeded")
       
       team = get_team(team_id)
       members = team.members
       
       for sub_team in team.sub_teams:
           members.extend(
               get_team_members(sub_team.id, max_depth, current_depth + 1)
           )
       
       return members
   ```

### Performance
1. **Large Lists in Session State**: Vermeide große Listen
   ```python
   # FALSCH - Langsam bei jedem Rerun
   st.session_state['all_products'] = load_all_products()  # 10.000+ Items
   
   # RICHTIG - Nutze Cache
   @st.cache_data(ttl=3600)
   def get_all_products():
       return load_all_products()
   
   products = get_all_products()  # Nur einmal geladen
   ```

2. **N+1 Query Problem**:
   ```python
   # FALSCH - N+1 Queries
   customers = get_all_customers()  # 1 Query
   for customer in customers:
       projects = get_projects(customer.id)  # N Queries!
   
   # RICHTIG - JOIN oder Batch Query
   query = """
       SELECT c.*, p.*
       FROM customers c
       LEFT JOIN projects p ON c.id = p.customer_id
   """
   results = cursor.execute(query).fetchall()
   ```

3. **PDF Chart Rendering**: Cache Charts
   ```python
   @st.cache_data
   def generate_chart_image(data_hash: str, chart_type: str):
       # Generiere Chart nur wenn Daten sich geändert haben
       return create_chart(data, chart_type)
   
   # Usage
   data_hash = hashlib.md5(str(data).encode()).hexdigest()
   chart = generate_chart_image(data_hash, 'bar')
   ```
4. **Vertragsverwaltung**: Automatische Ablauf-Erinnerungen (crm/features/contract_manager.py)

## CRM System (Detailliert)

### Architektur
**Hauptdatei**: `crm.py` (2390 Zeilen) - Haupt-UI und Orchestrierung

**Modulare Struktur**:
```
crm/
├── features/
│   ├── contract_manager.py    # Verträge & Garantien
│   ├── lead_management.py     # Lead-Tracking
│   └── activity_logger.py     # Aktivitäten-Historie
├── integration/
│   ├── pdf_integration.py     # PDF-Anbindung
│   └── email_integration.py   # E-Mail-Versand
└── utils/
    ├── validators.py          # Eingabe-Validierung
    └── formatters.py          # Daten-Formatierung
```

### View Modes Navigation
```python
# CRM nutzt State-Machine für Navigation
VIEW_MODES = [
    'list',           # Kundenliste
    'detail',         # Kundendetails
    'add_customer',   # Neuer Kunde
    'edit_customer',  # Kunde bearbeiten
    'projects',       # Projektliste
    'add_project',    # Neues Projekt
    'contracts',      # Verträge
    'documents'       # Dokumentenarchiv
]

# Navigation in crm.py
if st.session_state.get('crm_view_mode') == 'detail':
    customer_id = st.session_state.get('selected_customer_id')
    render_customer_detail(customer_id)
    
    if st.button("Zurück zur Liste"):
        st.session_state['crm_view_mode'] = 'list'
        st.rerun()
```

### Verträge & Garantien System
**Datei**: `crm/features/contract_manager.py` (1272 Zeilen)

**Hauptfunktionen**:
```python
def create_contract(
    customer_id: int,
    project_id: int,
    contract_type: str,  # 'service', 'maintenance', 'lease'
    start_date: date,
    duration_months: int,
    value: float
) -> int:
    """Erstellt Vertrag mit automatischer End-Date Berechnung"""
    
def get_expiring_contracts(days_ahead: int = 30) -> List[dict]:
    """Findet ablaufende Verträge für Erinnerungen"""
    
def add_warranty(
    project_id: int,
    warranty_type: str,  # 'product', 'installation', 'extended'
    duration_months: int,
    provider: str
) -> int:
    """Fügt Garantie zu Projekt hinzu"""
```

**CRM Features Ecosystem** (13+ Module):
- `contract_manager.py`: Verträge & Garantien (1272 Zeilen)
- `email_manager.py`: E-Mail-Integration mit SMTP
- `call_manager.py`: Anruf-Protokollierung
- `task_manager.py`: Aufgabenverwaltung
- `feedback_manager.py`: Feedback & Surveys
- `forecasting_engine.py`: Umsatz-Prognosen
- `knowledge_base.py`: Wissensdatenbank
- `lead_scoring.py`: Lead-Bewertung
- `offer_tracker.py`: Angebots-Tracking
- `reporting_engine.py`: Report-Generierung
- `tag_manager.py`: Tag-System
- `template_manager.py`: Template-Verwaltung
- `dashboard_widgets.py`: Dashboard-Widgets

**Datenbank-Schema**:
```sql
CREATE TABLE contracts (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    project_id INTEGER,
    contract_type TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    value REAL,
    status TEXT DEFAULT 'active',  -- active/expired/cancelled
    renewal_type TEXT,  -- auto/manual/none
    notice_period_days INTEGER,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE TABLE warranties (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    warranty_type TEXT NOT NULL,
    start_date DATE NOT NULL,
    duration_months INTEGER NOT NULL,
    provider TEXT,
    status TEXT DEFAULT 'active',
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

### Monitoring Integration
```python
try:
    from app_tracing import app_tracer
    from app_evaluation import track_success, track_error
    MONITORING_AVAILABLE = True
    
    @trace_crm
    def save_customer(customer_data):
        start_time = time.time()
        try:
            result = _save_customer_impl(customer_data)
            track_success("crm.save_customer")
            return result
        except Exception as e:
            track_error("crm.save_customer", str(e))
            raise
except ImportError:
    MONITORING_AVAILABLE = False
    def trace_crm(func): return func
```

## Pricing System (Matrizen & Regeln)

### Architektur
**Hauptdateien**: 
- `pricing/` - Pricing-Module (20+ Engines)
- `admin_price_matrix_upload.py` - Matrix-Upload
- `admin_pricing_rule_ui.py` - Regel-Verwaltung
- `admin_profit_margin_ui.py` - Gewinnmargen
- `price_matrix_lookup.py` - Preis-Lookup
- `price_modification_engine.py` - Preismodifikation

### Pricing Engines Ecosystem
**Verzeichnis**: `pricing/` (20+ Spezialisierte Engines)

```python
# 1. Enhanced Pricing Engine
from pricing.enhanced_pricing_engine import EnhancedPricingEngine

engine = EnhancedPricingEngine()
pricing = engine.calculate(
    product_id=123,
    quantity=20,
    customer_type='business',
    pricing_mode='matrix'  # oder 'direct'
)

# 2. Calculate Per Engine
from pricing.calculate_per_engine import CalculatePerEngine

engine = CalculatePerEngine()
price = engine.calculate_price(
    product=product,
    quantity=10,
    calculate_per='Stück'  # oder 'Meter', 'kWp', 'pauschal'
)

# 3. Combined Pricing Engine
from pricing.combined_pricing_engine import CombinedPricingEngine

engine = CombinedPricingEngine()
final_price = engine.combine(
    base_price=1000,
    modifiers=[
        {'type': 'quantity_discount', 'value': 10},
        {'type': 'seasonal', 'value': 5},
        {'type': 'customer_loyalty', 'value': 3}
    ]
)

# 4. PV Pricing Engine
from pricing.pv_pricing_engine import PVPricingEngine

engine = PVPricingEngine()
system_price = engine.calculate_system_price(
    modules=20,
    inverter_id=5,
    storage_id=3,
    mounting_system='flat_roof'
)

# 5. Pricing Modification Engine
from pricing.pricing_modification_engine import PricingModificationEngine

engine = PricingModificationEngine()
modified = engine.apply_modifications(
    base_price=10000,
    modifications=[
        {'type': 'margin', 'value': 20},  # +20%
        {'type': 'tax', 'value': 19},     # +19% MwSt
        {'type': 'discount', 'value': -5}  # -5%
    ]
)

# 6. Dynamic Key Manager
from pricing.dynamic_key_manager import DynamicKeyManager

key_mgr = DynamicKeyManager()
keys = key_mgr.generate_keys(
    product=product,
    calculation_result=calc_result,
    include_pricing=True
)

# 7. Profit Margin Manager
from pricing.profit_margin_manager import ProfitMarginManager

margin_mgr = ProfitMarginManager()
margin = margin_mgr.calculate_margin(
    purchase_price=80,
    selling_price=100,
    category='PV-Modul'
)

# 8. VAT Manager
from pricing.vat_manager import VATManager

vat_mgr = VATManager()
vat = vat_mgr.calculate_vat(
    net_price=1000,
    vat_rate=19,
    country='DE'
)

# 9. Pricing Cache
from pricing.pricing_cache import PricingCache

cache = PricingCache()
cache.set('product:123:price', price, ttl=3600)
cached_price = cache.get('product:123:price')

# 10. Pricing Validation
from pricing.pricing_validation import PricingValidator

validator = PricingValidator()
errors = validator.validate(
    price=100,
    min_margin=15,
    max_discount=30
)
```

### Price Matrices
**Datenbank-Tabellen**:
```sql
CREATE TABLE price_matrices (
    id INTEGER PRIMARY KEY,
    category TEXT NOT NULL,  -- 'pv_module', 'inverter', 'storage'
    manufacturer TEXT,
    model TEXT,
    power_range TEXT,        -- '0-10kW', '10-20kW', etc.
    base_price REAL,
    discount_pct REAL,
    valid_from DATE,
    valid_until DATE
);

CREATE TABLE pricing_rules (
    id INTEGER PRIMARY KEY,
    rule_type TEXT,          -- 'quantity_discount', 'bundle', 'seasonal'
    conditions TEXT,         -- JSON mit Bedingungen
    modifier_pct REAL,
    priority INTEGER
);

CREATE TABLE profit_margins (
    id INTEGER PRIMARY KEY,
    category TEXT,
    min_margin_pct REAL,
    target_margin_pct REAL,
    max_discount_pct REAL
);
```

### Price Lookup Pattern
```python
from price_matrix_lookup import get_product_price

# Basis-Preis holen
base_price = get_product_price(
    category='pv_module',
    manufacturer='Trina Solar',
    model='Vertex S 400W',
    quantity=20
)

# Mit Regeln anwenden
from pricing.rules import apply_pricing_rules

final_price = apply_pricing_rules(
    base_price=base_price,
    rules=['quantity_discount', 'seasonal'],
    context={
        'quantity': 20,
        'season': 'winter',
        'customer_type': 'business'
    }
)
```

### Multi-Firma Preis-Modifikation
**Integration mit PDF-System**:
```python
from price_modification_engine import apply_modification

# Firma 1: +15% Basisaufschlag
firm1_price = apply_modification(
    base_price=10000,
    modifier_pct=15,
    firm_index=0,
    progression_pct=5
)
# → 11.500 € (+15%)

# Firma 2: +20% (15% + 5% Progression)
firm2_price = apply_modification(
    base_price=10000,
    modifier_pct=15,
    firm_index=1,
    progression_pct=5
)
# → 12.000 € (+20%)
```

### Admin-UI für Preise
```python
# In admin_panel.py
from admin_pricing_rule_ui import render_pricing_rules_ui
from admin_profit_margin_ui import render_profit_margins_ui

tabs = st.tabs(["Preismatrizen", "Regeln", "Margen"])

with tabs[0]:
    render_price_matrix_upload()
    
with tabs[1]:
    render_pricing_rules_ui()
    
with tabs[2]:
    render_profit_margins_ui()
```

### Wichtig
- **Preise IMMER in Cent speichern** (INT) um Float-Rundungsfehler zu vermeiden
- **Oder nutze `Decimal`** für Geld-Beträge
- **Matrix-Cache**: Preise werden gecacht (TTL: 1 Stunde)
- **Validierung**: Margen müssen zwischen min/max liegen

```python
from decimal import Decimal

# RICHTIG - Decimal für Preise
price = Decimal('10000.50')
tax = price * Decimal('0.19')
total = price + tax

# FALSCH - Float-Rundungsfehler
price = 10000.50
tax = price * 0.19  # → 1900.0950000000003
```

### PDF Template Engine (`pdf_template_engine/`)
**Module**: 6 spezialisierte Module für PDF-Generierung

```python
# 1. Dynamic Overlay (Hauptmodul)
from pdf_template_engine.dynamic_overlay import apply_text_overlay

apply_text_overlay(
    template_pdf='multi_nt_1_f1.pdf',
    output_pdf='output.pdf',
    coords_file='seite1_f1.yml',
    placeholders={
        'Kundenname': 'Max Mustermann',
        'Gesamtpreis_brutto': '23.403,11 €',
        'Datum': '03.01.2026'
    }
)

# 2. Placeholders System
from pdf_template_engine.placeholders import PLACEHOLDER_MAPPING

PLACEHOLDER_MAPPING = {
    'customer_name': 'Kundenname',
    'total_price_gross': 'Gesamtpreis_brutto',
    'total_price_net': 'Gesamtpreis_netto',
    'date': 'Datum',
    'module_count': 'Modulanzahl',
    # ... 50+ weitere Mappings
}

# 3. Merger (Multi-Page PDFs)
from pdf_template_engine.merger import merge_pdfs

merge_pdfs(
    input_pdfs=['page1.pdf', 'page2.pdf', 'page3.pdf'],
    output_pdf='complete.pdf'
)

# 4. Overlay (Low-Level)
from pdf_template_engine.overlay import overlay_text_on_pdf

overlay_text_on_pdf(
    pdf_path='template.pdf',
    output_path='output.pdf',
    text_elements=[
        {'text': 'Max Mustermann', 'x': 100, 'y': 700, 'font': 'Helvetica', 'size': 12},
        {'text': '23.403,11 €', 'x': 500, 'y': 200, 'font': 'Helvetica-Bold', 'size': 10}
    ]
)

# 5. Prepare Backgrounds
from pdf_template_engine.prepare_backgrounds import prepare_multi_firm_backgrounds

prepare_multi_firm_backgrounds(
    firm_count=7,
    page_count=8,
    template_dir='pdf_templates_static/multi/'
)
```

**YAML Koordinaten Format** (`coords_multi/seite1_f1.yml`):
```yaml
- Text: "Kundenname"
  Position: [100.0, 700.0, 300.0, 720.0]  # [x1, y1, x2, y2]
  Font: "Helvetica-Bold"
  FontSize: 12.0
  Color: 0  # RGB Hex: 0x000000

- Text: "Gesamtpreis_brutto"
  Position: [450.0, 200.0, 550.0, 215.0]
  Font: "Helvetica"
  FontSize: 10.0
  Color: 3487029  # RGB Hex: 0x353535
  Alignment: "right"  # Für rechtsbündige Preise
```

**Wichtig**:
- **Koordinaten**: `(x1, y1)` = Bottom-Left, `(x2, y2)` = Top-Right
- **Rechtsbündige Preise**: `drawRightString(x2, y, text)` NICHT `drawString(x1, y, text)`
- **Fonts**: Nur ReportLab-Fonts (Helvetica, Times-Roman, Courier)
- **Deutsche Formatierung**: Nutze `german_formatting.py` für Zahlen

## Key Files Reference

**Entry Points**:
- `gui.py` - Haupt-Streamlit-App (4633 Zeilen)
- `admin_panel.py` - Admin-Interface

**Core Systems**:
- `database.py` - Zentrale DB-Logik
- `pdf_generator.py` - PDF-Hauptlogik
- `pdf_template_engine/dynamic_overlay.py` - Text-Overlay-Engine
- `crm.py` - CRM-Kern

**Calculations**:
- `calculations.py` - PV-Berechnungen
- `calculations_heatpump.py` - Wärmepumpen-Kalkulation
- `financial_calculations.py` - Finanzanalyse

**UI Components**:
- `components/shadcn_ui_integration.py` - UI-Wrapper
- `core/router.py` - Navigation
- `locales.py` - Texte

**Tests**:
- `tests/test_crm_*.py` - CRM-Tests
- `tests/test_pdf_*.py` - PDF-Tests

## Charting & Visualization Libraries

### Plotly Integration
**Hauptdatei**: `heatpump_ui.py`, `admin_pv_mounting_tab.py`, Charts in CRM

**Pattern**:
```python
import plotly.graph_objects as go
import plotly.express as px

# Erstelle interaktive Charts
fig = go.Figure()
fig.add_trace(go.Bar(
    x=['Jan', 'Feb', 'Mar'],
    y=[100, 200, 150],
    name='Umsatz'
))

# Shadcn-UI Design anwenden
def apply_shadcn_design(fig):
    """Wendet vollständiges Shadcn UI Design auf Plotly Figure an."""
    fig.update_layout(
        template='plotly_white',
        font=dict(family='Inter, sans-serif', size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# Render in Streamlit
st.plotly_chart(fig, use_container_width=True)
```

**Wichtig**:
- **Kaleido** wird für PNG-Export benötigt (requirements.txt: `kaleido==1.0.0`)
- **Interaktive Features**: Zoom, Pan, Export als PNG
- **Deutsche Formatierung**: Nutze `german_formatting.py` für Zahlen in Charts

### Altair Integration
**Verwendung**: Alternative für deklarative Charts

```python
import altair as alt

# Deklarative Chart-Erstellung
chart = alt.Chart(data).mark_bar().encode(
    x='category',
    y='value',
    color='category'
).properties(
    width=600,
    height=400
)

st.altair_chart(chart, use_container_width=True)
```

### Matplotlib Integration
**Verwendung**: PDF-eingebettete statische Charts

```python
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

# Chart erstellen
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x_data, y_data)
ax.set_xlabel('Zeit')
ax.set_ylabel('Wert')

# In PDF einbetten
from io import BytesIO
buf = BytesIO()
fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
buf.seek(0)

# Chart in ReportLab PDF
from reportlab.lib.utils import ImageReader
img = ImageReader(buf)
c.drawImage(img, x, y, width, height)
```

## Dependencies (Key)
- **Streamlit 1.49.1** - Web Framework
- **ReportLab 4.4.3** - PDF-Generierung
- **PyPDF2 / pypdf** - PDF-Merge
- **SQLite3** (builtin) - Datenbank
- **pandas 2.2.3** - Datenverarbeitung
- **pyvista 0.43+** - 3D-Visualisierung
- **plotly 6.3.0** - Interaktive Charts
- **altair 5.5.0** - Deklarative Visualisierung
- **matplotlib 3.10.6** - Statische Charts (PDF)
- **kaleido 1.0.0** - PNG-Export für Plotly
- **langchain 0.3+** - KI-Agent (optional)

**Installation**: `pip install -r requirements.txt`

## Git Repository
- **Remote**: `arschibald` (https://github.com/Greenkack/Arschibald.git)
- **Branch**: `snapshot-main-clean`

**Commit-Pattern**:
```bash
git add .
git commit -m "Feature: Beschreibung + Fix Details"
git push arschibald snapshot-main-clean
```

## Build & Distribution

### PyInstaller Build System
**Hauptdatei**: `ARSCHIBALD_COMPLETE.spec` - PyInstaller Konfiguration für vollständigen Build

**Build-Kommandos**:
```batch
# Automatischer Build (EMPFOHLEN)
BUILD_COMPLETE.bat

# Manueller Build
pyinstaller --clean --noconfirm ARSCHIBALD_COMPLETE.spec

# Setup.exe erstellen (benötigt Inno Setup)
iscc ARSCHIBALD_COMPLETE_SETUP.iss
```

**Wichtig**:
- **Dauer**: 10-20 Minuten
- **Ausgabe**: `dist\Ömers All in One Dingsbums\` (1.5 GB)
- **Hidden Imports**: Module MÜSSEN in `hiddenimports` sein wenn dynamisch geladen
- **Datas**: Alle nicht-.py Dateien via `datas` Liste inkludieren

**Build-Troubleshooting**:
- Module fehlen → `hiddenimports` in .spec erweitern
- Dateien fehlen → `datas` Liste prüfen (de.json, coords_multi/, etc.)
- SQLite Errors → Prüfe dass `data/app_data.db` kopiert wird
- Metadaten fehlen → `.dist-info` Ordner müssen kopiert werden

**Critical Hidden Imports**:
```python
hiddenimports = [
    # Streamlit Core
    'streamlit.runtime.scriptrunner.magic_funcs',
    'streamlit.components.v1',
    
    # PDF Generation
    'reportlab.pdfgen.canvas',
    'reportlab.lib.pagesizes',
    'PyPDF2',
    'pypdf',
    
    # 3D Visualization
    'pyvista',
    'vtk',
    'stpyvista',
    
    # Excel
    'openpyxl.cell._writer',
    'xlrd',
    
    # AI/Agent
    'langchain',
    'langchain_openai',
    'langchain_community',
    
    # Database
    'sqlalchemy.sql.default_comparator',
    
    # Plotly
    'plotly.graph_objs',
    'kaleido',
]
```

**Data Files Liste**:
```python
datas = [
    # KRITISCH - App startet nicht ohne diese
    ('de.json', '.'),
    ('locales.py', '.'),
    
    # Templates & Configs
    ('coords_multi', 'coords_multi'),
    ('pdf_templates_static', 'pdf_templates_static'),
    ('.streamlit', '.streamlit'),
    
    # Datenbanken & Daten
    ('data', 'data'),
    ('customer_documents', 'customer_documents'),
    
    # Module
    ('core', 'core'),
    ('crm', 'crm'),
    ('controlling', 'controlling'),
    ('components', 'components'),
    ('pdf_template_engine', 'pdf_template_engine'),
    
    # Assets
    ('static', 'static'),
    ('assets', 'assets'),
]

## 3D Visualisierung System (PyVista)

### Architektur
**Hauptdatei**: `pv3d.py` (4545 Zeilen) - 3D PV-Visualisierung Core Engine

**Unterstützende Module**:
- `solar_3d_view_module.py` - Streamlit-Integration
- `pv3d_plotly.py` - Alternative Plotly-basierte 3D-View
- `pv_visuals.py` - 2D Chart-Generierung

### Datenmodelle
```python
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class BuildingDims:
    """Gebäude-Dimensionen"""
    width: float          # Breite in Metern
    length: float         # Länge in Metern
    height: float         # Höhe in Metern
    roof_pitch: float     # Dachneigung in Grad (0-90)
    roof_type: str        # 'flat', 'gable', 'hip', 'pent', 'pyramid'

@dataclass
class ModuleTransform:
    """PV-Modul Transformation (Position + Rotation)"""
    position: Tuple[float, float, float]  # (x, y, z)
    rotation: Tuple[float, float, float]  # (rx, ry, rz) in Grad
    scale: Tuple[float, float, float]     # (sx, sy, sz)

@dataclass
class ModuleGroup:
    """Gruppe von Modulen mit gemeinsamen Eigenschaften"""
    name: str
    orientation: str      # 'south', 'east', 'west', 'north'
    tilt_angle: float     # Neigung in Grad
    modules: List[ModuleTransform]
    shading_factor: float # 0.0-1.0 (0=voll beschattet, 1=keine Beschattung)
```

### Kernfunktionen

**1. Dach-Geometrie**:
```python
def make_roof_gable(
    width: float,
    length: float,
    height: float,
    pitch: float  # in Grad
) -> pyvista.PolyData:
    """Erstellt Satteldach-Geometrie.
    
    Returns:
        PyVista PolyData Mesh mit korrekten Normalen
    """
    # Berechne Firsthöhe
    ridge_height = height + (width / 2) * math.tan(math.radians(pitch))
    
    # Definiere Vertices
    points = np.array([
        [0, 0, height],              # Front-links unten
        [width, 0, height],          # Front-rechts unten
        [width/2, 0, ridge_height],  # Front-First
        [0, length, height],         # Back-links unten
        [width, length, height],     # Back-rechts unten
        [width/2, length, ridge_height]  # Back-First
    ])
    
    # Erstelle Faces (Dreiecke)
    faces = np.array([
        [3, 0, 1, 2],  # Front-Seite
        [3, 3, 4, 5],  # Back-Seite
        [4, 0, 2, 5, 3],  # Links-Dachfläche
        [4, 1, 4, 5, 2]   # Rechts-Dachfläche
    ])
    
    mesh = pyvista.PolyData(points, faces)
    return mesh

def make_roof_flat(width, length, height):
    """Flachdach"""
    
def make_roof_hip(width, length, height, pitch):
    """Walmdach"""
    
def make_roof_pent(width, length, height, pitch):
    """Pultdach"""
```

**2. Modul-Platzierung**:
```python
def add_module(
    plotter: pyvista.Plotter,
    position: Tuple[float, float, float],
    rotation: Tuple[float, float, float] = (0, 0, 0),
    color: str = 'darkblue',
    module_dims: Tuple[float, float, float] = (1.7, 1.0, 0.04)
) -> pyvista.Actor:
    """Fügt PV-Modul zu Szene hinzu.
    
    Standard-Modul: 1.7m × 1.0m × 0.04m (Länge × Breite × Dicke)
    """
    length, width, thickness = module_dims
    
    # Erstelle Quader
    module = pyvista.Cube()
    module.scale([length/2, width/2, thickness/2], inplace=True)
    
    # Transformiere
    module.translate(position, inplace=True)
    module.rotate_x(rotation[0], inplace=True)
    module.rotate_y(rotation[1], inplace=True)
    module.rotate_z(rotation[2], inplace=True)
    
    # Füge zu Szene hinzu
    actor = plotter.add_mesh(
        module,
        color=color,
        show_edges=True,
        edge_color='black',
        opacity=0.9
    )
    
    return actor

def detect_collisions(
    existing_modules: List[ModuleTransform],
    new_module: ModuleTransform,
    tolerance: float = 0.05  # 5cm Mindestabstand
) -> bool:
    """Prüft auf Kollisionen zwischen Modulen."""
    for existing in existing_modules:
        if modules_overlap(existing, new_module, tolerance):
            return True
    return False
```

**3. Automatische Platzierung**:
```python
def grid_positions(
    roof_area: pyvista.PolyData,
    module_dims: Tuple[float, float],
    spacing: float = 0.05,  # 5cm Abstand
    orientation: str = 'portrait'  # oder 'landscape'
) -> List[Tuple[float, float, float]]:
    """Berechnet Grid-Positionen für Module auf Dachfläche.
    
    Algorithmus:
    1. Bestimme Dach-Bounds
    2. Berechne Anzahl Module pro Reihe
    3. Platziere in Grid mit Spacing
    4. Prüfe ob Position innerhalb Dach-Polygon
    """
    bounds = roof_area.bounds  # (xmin, xmax, ymin, ymax, zmin, zmax)
    
    module_length, module_width = module_dims
    if orientation == 'landscape':
        module_length, module_width = module_width, module_length
    
    positions = []
    
    # Grid-Iteration
    x = bounds[0] + spacing
    while x + module_length <= bounds[1]:
        y = bounds[2] + spacing
        while y + module_width <= bounds[3]:
            pos = (x + module_length/2, y + module_width/2, bounds[5])
            
            # Prüfe ob innerhalb Dach-Polygon
            if point_in_roof_polygon(pos, roof_area):
                positions.append(pos)
            
            y += module_width + spacing
        x += module_length + spacing
    
    return positions
```

**4. Export-Funktionen**:
```python
def export_stl(mesh: pyvista.PolyData, filepath: str):
    """Exportiert als STL für 3D-Druck"""
    mesh.save(filepath, binary=True)

def export_gltf(scene_data: dict, filepath: str):
    """Exportiert als GLTF für Web-Viewer"""
    # GLTF-Format mit Materialien und Texturen

def export_360_animation(
    plotter: pyvista.Plotter,
    output_path: str,
    frames: int = 120,
    fps: int = 30
):
    """Erstellt 360° Rotation-Animation als GIF/MP4"""
    plotter.open_movie(output_path, framerate=fps)
    
    for angle in range(frames):
        plotter.camera_position = calculate_camera_position(angle * 3)
        plotter.write_frame()
    
    plotter.close()

def export_multi_view_screenshots(
    scene: pyvista.Plotter,
    output_dir: str,
    views: List[str] = ['front', 'side', 'top', 'perspective']
):
    """Exportiert Screenshots aus verschiedenen Perspektiven"""
    for view in views:
        scene.camera_position = CAMERA_PRESETS[view]
        scene.screenshot(f"{output_dir}/{view}.png")
```

**5. Shading-Analyse**:
```python
def calculate_shading_for_module(
    module: ModuleTransform,
    surrounding_modules: List[ModuleTransform],
    sun_position: Tuple[float, float, float],
    time_of_day: int  # 0-23
) -> float:
    """Berechnet Verschattung eines Moduls.
    
    Returns:
        Shading factor 0.0-1.0 (0=voll beschattet, 1=keine Verschattung)
    """
    # Ray-Casting von Modul zu Sonne
    ray_origin = module.position
    ray_direction = normalize(sun_position - ray_origin)
    
    # Prüfe Schnitt mit anderen Modulen
    for other in surrounding_modules:
        if ray_intersects_module(ray_origin, ray_direction, other):
            return 0.5  # Partielle Verschattung
    
    return 1.0  # Keine Verschattung

def calculate_sun_position(latitude: float, longitude: float, 
                          date: datetime, time: int) -> Tuple[float, float, float]:
    """Berechnet Sonnenposition für Shading-Analyse"""
    # Solar Position Algorithm (SPA)
    # Vereinfachte Version
```

### Streamlit Integration
```python
import streamlit as st
from stpyvista import stpyvista

def render_3d_view(building_config, modules):
    """Rendert 3D-Ansicht in Streamlit"""
    
    # Erstelle PyVista Plotter
    plotter = pyvista.Plotter()
    
    # Füge Gebäude hinzu
    roof = make_roof_gable(
        building_config['width'],
        building_config['length'],
        building_config['height'],
        building_config['pitch']
    )
    plotter.add_mesh(roof, color='lightgray', opacity=0.7)
    
    # Füge Module hinzu
    for module in modules:
        add_module(plotter, module.position, module.rotation)
    
    # Render in Streamlit
    stpyvista(plotter, key="pv_3d_view")
    
    # Export-Buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Export STL"):
            export_stl(roof, "building.stl")
    with col2:
        if st.button("360° Animation"):
            export_360_animation(plotter, "animation.gif")
    with col3:
        if st.button("Screenshots"):
            export_multi_view_screenshots(plotter, "./exports")
```

### Performance-Optimierung
```python
# Caching für große Meshes
@st.cache_data
def load_building_mesh(config_hash: str) -> pyvista.PolyData:
    return make_roof_gable(**config)

# Lazy Loading von Modulen
def render_modules_lod(modules, camera_distance):
    """Level-of-Detail: Zeige weniger Details bei großer Entfernung"""
    if camera_distance > 50:
        # Low-Detail: Nur Bounding Boxes
        return [module.bounds for module in modules]
    else:
        # High-Detail: Vollständige Geometrie
        return modules
```

## Wärmepumpen-System

### Architektur
**Hauptdatei**: `calculations_heatpump.py` (1459 Zeilen) - Wärmepumpen-Berechnungen

**Begleitende Module**:
- `heatpump_ui.py` - Streamlit UI
- `heatpump_products_database.py` - Produkt-Datenbank
- `heatpump_pricing.py` - Preiskalkulation
- `heatpump_advanced_features.py` - Erweiterte Features

### Kernberechnungen

**1. Heizlast-Berechnung**:
```python
def calculate_building_heat_load(
    building_type: str,  # 'Neubau KFW40', 'Altbau saniert', etc.
    living_area_m2: float,
    insulation_quality: str  # 'Gut', 'Mittel', 'Schlecht'
) -> float:
    """Berechnet maximale Heizlast in kW.
    
    Basis: Spezifische Heizlast × Wohnfläche × Dämmungsfaktor
    """
    base_load_w_per_m2 = {
        "Neubau KFW40": 40.0,
        "Neubau KFW55": 55.0,
        "Altbau saniert": 70.0,
        "Altbau unsaniert": 120.0,
    }
    
    insulation_factor = {
        "Gut": 0.9,
        "Mittel": 1.0,
        "Schlecht": 1.2,
    }
    
    base_w_m2 = base_load_w_per_m2.get(building_type, 100.0)
    factor = insulation_factor.get(insulation_quality, 1.0)
    
    heat_load_watts = living_area_m2 * base_w_m2 * factor
    return heat_load_watts / 1000  # Konvertiere zu kW
```

**2. Wärmepumpen-Empfehlung**:
```python
def recommend_heat_pump(
    heat_load_kw: float,
    available_pumps: List[dict]
) -> dict:
    """Empfiehlt kleinste passende Wärmepumpe.
    
    Regel: Wärmepumpe muss >= 100% der Heizlast abdecken
    Bevorzugt: 110-120% für Reserve
    """
    suitable_pumps = [
        pump for pump in available_pumps
        if pump['power_kw'] >= heat_load_kw
    ]
    
    if not suitable_pumps:
        return None  # Keine passende Pumpe
    
    # Sortiere nach Leistung (kleinste zuerst)
    suitable_pumps.sort(key=lambda p: p['power_kw'])
    
    return suitable_pumps[0]
```

**3. Wirtschaftlichkeitsanalyse**:
```python
def calculate_heatpump_economics(
    heat_pump: dict,
    annual_heat_demand_kwh: float,
    electricity_price_per_kwh: float,
    comparison_system: str = 'gas',  # oder 'oil', 'district_heating'
    years: int = 20
) -> dict:
    """Berechnet 20-Jahres Wirtschaftlichkeit.
    
    Returns:
        {
            'total_cost_heatpump': float,
            'total_cost_comparison': float,
            'savings': float,
            'payback_years': float,
            'co2_reduction_tons': float
        }
    """
    # Wärmepumpe
    cop = heat_pump.get('cop', 3.5)  # Coefficient of Performance
    annual_electricity_kwh = annual_heat_demand_kwh / cop
    annual_electricity_cost = annual_electricity_kwh * electricity_price_per_kwh
    
    installation_cost = heat_pump.get('installation_cost', 15000)
    maintenance_annual = heat_pump.get('maintenance_annual', 200)
    
    total_heatpump = (
        installation_cost +
        (annual_electricity_cost * years) +
        (maintenance_annual * years)
    )
    
    # Vergleichssystem
    comparison_costs = calculate_comparison_system_costs(
        comparison_system,
        annual_heat_demand_kwh,
        years
    )
    
    # Ergebnisse
    savings = comparison_costs - total_heatpump
    payback_years = installation_cost / (comparison_costs/years - total_heatpump/years)
    
    return {
        'total_cost_heatpump': total_heatpump,
        'total_cost_comparison': comparison_costs,
        'savings': savings,
        'payback_years': payback_years,
        'co2_reduction_tons': calculate_co2_reduction(annual_heat_demand_kwh, cop)
    }
```

**4. PV-Integration**:
```python
def calculate_pv_self_consumption_heatpump(
    pv_annual_yield_kwh: float,
    heatpump_annual_consumption_kwh: float,
    self_consumption_rate: float = 0.3  # 30% Eigenverbrauch typisch
) -> dict:
    """Berechnet Eigenverbrauch der Wärmepumpe mit PV."""
    
    # PV-Strom für Wärmepumpe
    pv_for_heatpump = min(
        pv_annual_yield_kwh * self_consumption_rate,
        heatpump_annual_consumption_kwh
    )
    
    # Netzstrom-Bedarf
    grid_consumption = heatpump_annual_consumption_kwh - pv_for_heatpump
    
    return {
        'pv_for_heatpump_kwh': pv_for_heatpump,
        'grid_consumption_kwh': grid_consumption,
        'self_sufficiency_rate': pv_for_heatpump / heatpump_annual_consumption_kwh
    }
```

**5. BEG-Förderung** (Bundesförderung effiziente Gebäude):
```python
def calculate_beg_subsidy(
    heat_pump: dict,
    building_type: str,
    old_heating_system: str  # 'gas', 'oil', 'electric'
) -> dict:
    """Berechnet BEG-Förderung für Wärmepumpe.
    
    Basis-Förderung: 25-35% der förderfähigen Kosten
    Boni:
    - Wärmepumpe mit natürlichem Kältemittel: +5%
    - Austausch Öl/Gas/Nachtspeicher: +10%
    - iSFP (individueller Sanierungsfahrplan): +5%
    
    Max: 70.000€ förderfähige Kosten
    """
    eligible_costs = min(heat_pump.get('total_cost', 0), 70000)
    
    # Basis-Förderung
    base_rate = 0.25  # 25%
    
    # Boni
    bonus = 0
    if heat_pump.get('natural_refrigerant', False):
        bonus += 0.05
    if old_heating_system in ['oil', 'gas', 'electric']:
        bonus += 0.10
    
    total_rate = min(base_rate + bonus, 0.70)  # Max 70%
    subsidy = eligible_costs * total_rate
    
    return {
        'subsidy_amount': subsidy,
        'subsidy_rate': total_rate,
        'net_cost': heat_pump.get('total_cost', 0) - subsidy
    }
```

## Testing System

### Test-Struktur
```
tests/
├── test_crm_*.py           # CRM-Tests (Integration + Unit)
├── test_pdf_*.py           # PDF-Generierung
├── test_3d_*.py            # 3D-Visualisierung
├── test_calculations*.py   # PV/WP-Berechnungen
├── test_controlling_*.py   # Controlling-System
├── test_database*.py       # Datenbank-Operationen
├── test_integration*.py    # End-to-End Tests
└── test_performance*.py    # Performance-Tests
```

### Testing-Patterns

**1. CRM Integration Tests**:
```python
# tests/test_crm_integration.py
import pytest
from database import get_db_connection
from crm import save_customer, load_customer

@pytest.fixture
def db_connection():
    """Test-Datenbank"""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()

def test_customer_crud(db_connection):
    """Test Create-Read-Update-Delete Workflow"""
    # Create
    customer_id = save_customer(db_connection, {
        'name': 'Test Kunde',
        'email': 'test@example.com'
    })
    assert customer_id > 0
    
    # Read
    customer = load_customer(db_connection, customer_id)
    assert customer['name'] == 'Test Kunde'
    
    # Update
    save_customer(db_connection, {
        'id': customer_id,
        'name': 'Updated Name'
    })
    updated = load_customer(db_connection, customer_id)
    assert updated['name'] == 'Updated Name'
```

**2. PDF Generation Tests**:
```python
# tests/test_pdf_generation.py
from pdf_generator import generate_multi_offer_pdfs
from pathlib import Path

def test_multi_pdf_generation():
    """Test Multi-Firma PDF-Erstellung"""
    config = {
        'customer_name': 'Test GmbH',
        'firms': [1, 2, 3],  # 3 Firmen-Varianten
        'products': {
            'pv_module': {'id': 1, 'quantity': 20},
            'inverter': {'id': 5}
        }
    }
    
    output_files = generate_multi_offer_pdfs(config)
    
    # Prüfe dass 3 PDFs erstellt wurden
    assert len(output_files) == 3
    
    # Prüfe dass Dateien existieren
    for filepath in output_files:
        assert Path(filepath).exists()
        assert Path(filepath).stat().st_size > 10000  # Min 10KB
```

**3. 3D Visualization Tests**:
```python
# tests/test_3d_visualization.py
import pyvista as pv
from pv3d import make_roof_gable, add_module, detect_collisions

def test_roof_generation():
    """Test Dach-Geometrie Erstellung"""
    roof = make_roof_gable(
        width=10,
        length=15,
        height=5,
        pitch=35
    )
    
    assert roof.n_points > 0
    assert roof.n_cells > 0
    
    # Prüfe Bounds
    bounds = roof.bounds
    assert bounds[1] - bounds[0] == 10  # Width
    assert bounds[3] - bounds[2] == 15  # Length

def test_collision_detection():
    """Test Kollisionserkennung"""
    modules = [
        ModuleTransform(position=(0, 0, 0), rotation=(0, 0, 0)),
        ModuleTransform(position=(2, 0, 0), rotation=(0, 0, 0))
    ]
    
    # Zu nah → Kollision
    new_module = ModuleTransform(position=(0.5, 0, 0), rotation=(0, 0, 0))
    assert detect_collisions(modules, new_module) == True
    
    # Weit genug → Keine Kollision
    new_module = ModuleTransform(position=(5, 0, 0), rotation=(0, 0, 0))
    assert detect_collisions(modules, new_module) == False
```

**4. Performance Tests**:
```python
# tests/test_performance.py
import time
import pytest

@pytest.mark.performance
def test_pdf_generation_speed():
    """PDF-Generierung sollte < 5 Sekunden sein"""
    start = time.time()
    generate_single_pdf(test_config)
    duration = time.time() - start
    
    assert duration < 5.0, f"PDF-Generierung zu langsam: {duration}s"

@pytest.mark.performance
def test_database_query_performance():
    """DB-Queries sollten < 100ms sein"""
    conn = get_db_connection()
    
    start = time.time()
    result = load_all_customers(conn)
    duration = (time.time() - start) * 1000  # ms
    
    assert duration < 100, f"DB-Query zu langsam: {duration}ms"
```

**5. Integration Tests**:
```python
# tests/test_integration_complete.py
def test_end_to_end_workflow():
    """Kompletter Workflow: Kunde → Angebot → PDF"""
    
    # 1. Kunde anlegen
    customer_id = create_test_customer()
    
    # 2. Projekt erstellen
    project_id = create_test_project(customer_id)
    
    # 3. Berechnungen durchführen
    calc_results = perform_calculations(project_config)
    
    # 4. PDF generieren
    pdf_path = generate_pdf(calc_results, customer_id)
    
    # 5. Prüfe Ergebnis
    assert Path(pdf_path).exists()
    assert validate_pdf_content(pdf_path)
```

### Test-Kommandos
```powershell
# Alle Tests
pytest tests/ -v

# Nur CRM-Tests
pytest tests/test_crm*.py -v

# Nur Integration-Tests
pytest tests/test_integration*.py -v

# Mit Coverage
pytest tests/ --cov=. --cov-report=html

# Performance-Tests (markiert)
pytest tests/ -m performance

# Parallel (schneller)
pytest tests/ -n auto
```

### Mocking-Pattern
```python
from unittest.mock import Mock, patch

@patch('product_db.list_products')
def test_with_mocked_database(mock_list_products):
    """Test mit gemockter Datenbank"""
    
    # Mock-Rückgabewert definieren
    mock_list_products.return_value = [
        {'id': 1, 'name': 'Test Module', 'power_wp': 400}
    ]
    
    # Funktion testen
    result = get_available_modules()
    
    # Assertions
    assert len(result) == 1
    assert result[0]['name'] == 'Test Module'
    mock_list_products.assert_called_once()
```

## Agent/AI Integration (Optional)

### KAI Agent System
**Dateien**: `Agent/`, `agent_ui.py`, `ai_companion.py`

**Workspace-Isolation**: Agent kann NUR in `agent_workspace/` schreiben
- Sandbox: `Agent/sandbox/` (Docker-basiert)
- Knowledge Base: `knowledge_base/` (PDF-Dokumente für RAG)
- Projekte: `agent_workspace/{project_name}/`

**Pattern**:
```python
# Agent-Funktionen isoliert verwenden
from agent_ui import render_agent_interface

if is_feature_enabled('agent'):
    render_agent_interface()
```

## Controlling System (Mitarbeiter-Performance)

### Architektur
**Hauptdatei**: `controlling_ui.py` (2798 Zeilen) - Haupt-UI

**Module**:
```
controlling/
├── models.py           # SQLAlchemy Datenmodelle
├── managers.py         # Business Logic (Employee, Position, Performance)
├── database.py         # DB Session Management
├── report_generator.py # Report-Erstellung
├── chart_generator.py  # Visualisierungen
├── analytics.py        # Erweiterte Analysen
├── team_manager.py     # Team-Verwaltung
├── ranking_system.py   # Mitarbeiter-Rankings
└── notifications.py    # Benachrichtigungen
```

### Hauptkonzepte

**1. Evaluation Periods** (Auswertungsperioden):
```python
class PeriodType(Enum):
    WEEKLY = "weekly"      # Wöchentlich
    MONTHLY = "monthly"    # Monatlich
    QUARTERLY = "quarterly" # Quartalsweise
    YEARLY = "yearly"      # Jährlich

class PeriodStatus(Enum):
    ACTIVE = "active"      # Aktuell
    LOCKED = "locked"      # Abgeschlossen
    ARCHIVED = "archived"  # Archiviert
```

**2. Performance Data** (Leistungsdaten):
```python
class PerformanceData:
    employee_id: int
    period_id: int
    position_id: int
    
    # Kennzahlen
    sales_volume: float        # Umsatz
    customer_visits: int       # Kundenbesuche
    quotes_created: int        # Angebote erstellt
    contracts_closed: int      # Verträge abgeschlossen
    conversion_rate: float     # Abschlussquote
    
    # Berechnet
    score: float               # Gesamtpunktzahl
    rank: int                  # Ranking
```

**3. Positions & Criteria** (Positionen & Kriterien):
```python
# Controlling nutzt dynamische Kriterien pro Position
positions = [
    {
        'name': 'Vertriebsmitarbeiter',
        'criteria': {
            'sales_volume': {'weight': 40, 'min': 0, 'max': 100000},
            'contracts_closed': {'weight': 30, 'min': 0, 'max': 50},
            'customer_visits': {'weight': 30, 'min': 0, 'max': 100}
        }
    },
    {
        'name': 'Projektmanager',
        'criteria': {
            'projects_completed': {'weight': 50, 'min': 0, 'max': 20},
            'customer_satisfaction': {'weight': 50, 'min': 0, 'max': 100}
        }
    }
]
```

### Manager-Pattern
```python
from controlling.managers import (
    EmployeeManager,
    PositionManager,
    PerformanceDataManager
)

# Verwendung
with SessionLocal() as db:
    emp_mgr = EmployeeManager(db)
    
    # Mitarbeiter anlegen
    employee = emp_mgr.create_employee(
        name="Max Mustermann",
        position_id=1,
        hire_date=date.today()
    )
    
    # Performance erfassen
    perf_mgr = PerformanceDataManager(db)
    perf_mgr.record_performance(
        employee_id=employee.id,
        period_id=current_period.id,
        data={
            'sales_volume': 50000,
            'contracts_closed': 10
        }
    )
```

### Report Generation
```python
from controlling.report_generator import ReportGenerator
from controlling.models import ReportType

generator = ReportGenerator(db)

# Verschiedene Report-Typen
report = generator.generate_report(
    period_id=period.id,
    report_type=ReportType.TEAM_PERFORMANCE,
    filters={'department': 'Sales'},
    include_charts=True
)

# Export als PDF oder Excel
generator.export_pdf(report, 'team_report.pdf')
```

### Team Analytics
```python
from controlling.team_analytics import TeamAnalytics

analytics = TeamAnalytics(db)

# Team-Vergleich
comparison = analytics.compare_teams(
    period_id=period.id,
    metrics=['sales_volume', 'conversion_rate']
)

# Top Performer
top_performers = analytics.get_top_performers(
    period_id=period.id,
    limit=10
)
```

### UI-Integration mit Streamlit
```python
def render_controlling_page():
    st.header("🎯 Controlling")
    
    # Tab-basierte Navigation
    tabs = st.tabs([
        "📊 Dashboard",
        "📝 Datenerfassung",
        "📈 Auswertungen",
        "👥 Teams",
        "⚙️ Einstellungen"
    ])
    
    with tabs[0]:  # Dashboard
        render_dashboard()
    
    with tabs[1]:  # Datenerfassung
        render_data_entry()
```

### Notifications System
```python
from controlling.notifications import NotificationManager

notif_mgr = NotificationManager(db)

# Automatische Erinnerungen
notif_mgr.check_and_notify(
    notification_type='period_closing',
    days_before=3
)

# Manuelle Benachrichtigung
notif_mgr.send_notification(
    employee_id=employee.id,
    message="Bitte Performance-Daten eintragen",
    priority='high'
)
```

## SQLAlchemy & Database Migrations

### SQLAlchemy ORM
**Hauptdateien**: `controlling/models.py`, `backend/core/database.py`

**Controlling nutzt SQLAlchemy** für komplexe Datenmodelle:
```python
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.core.database import Base

class Employee(Base):
    __tablename__ = "controlling_employees"
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    position_id = Column(Integer, ForeignKey("controlling_positions.id"))
    
    # Relationships
    position = relationship("Position", back_populates="employees")
    performance_data = relationship("PerformanceData", back_populates="employee")
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
```

**Wichtig für Streamlit Session State**:
```python
# SQLAlchemy Models MÜSSEN pickle-serializable sein für Session State
class MyModel(Base):
    # Alle Enums müssen von str erben!
    class Status(str, enum.Enum):
        ACTIVE = "active"
        LOCKED = "locked"
    
    status = Column(SQLEnum(Status), default=Status.ACTIVE)
```

### Alembic Migrations
**Config**: `core/alembic/` - Migrations-Verzeichnis

**Kommandos**:
```bash
# Auto-generate Migration aus SQLAlchemy Models
alembic revision --autogenerate -m "Add new columns"

# Migration anwenden
alembic upgrade head

# Rollback
alembic downgrade -1

# Historie anzeigen
alembic history

# Aktuellen Stand prüfen
alembic current
```

**Migration erstellen**:
```python
# core/alembic/versions/xxxx_add_agent_name.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('controlling_employees',
        sa.Column('agent_name', sa.String(100), nullable=True)
    )

def downgrade():
    op.drop_column('controlling_employees', 'agent_name')
```

**Integration in App**:
```python
from backend.core.database import SessionLocal, engine
from controlling.models import Base

# Erstelle alle Tabellen
Base.metadata.create_all(bind=engine)

# Session verwenden
with SessionLocal() as db:
    employees = db.query(Employee).filter(Employee.is_active == True).all()
```

## Core Integration System

### Feature Flags
**Datei**: `core_integration.py` - Zentrales Feature-Toggle-System

**Verfügbare Features**:
- `config`: Konfigurationsverwaltung
- `logging`: Strukturiertes Logging
- `cache`: Performance-Caching
- `session`: Session-Persistenz
- `database`: DB Connection Pooling
- `security`: Authentifizierung & Authorization
- `router`: Multi-Page Routing
- `navigation`: Browser-Style History
- `jobs`: Background Job Scheduler
- `migrations`: Database Migrations
- `di`: Dependency Injection Container

**Aktivierung via ENV**:
```bash
FEATURE_CONFIG=true
FEATURE_LOGGING=true
# Alle Features default: true
```

**Usage Pattern**:
```python
from core_integration import is_feature_enabled, log_info

if is_feature_enabled('logging'):
    log_info("my_operation", data={"key": "value"})
```

### Core Module: Router (`core/router.py` - 834 Zeilen)
**Pattern**: Browser-Style Navigation mit History & Guards

```python
from core.router import get_router, navigate

# Navigation mit Parametern
router = get_router()
navigate('crm', params={'customer_id': 123})  # Navigate with params
router.go_back()  # Browser-style zurück

# Navigation Guards
class AuthGuard(NavigationGuard):
    def can_navigate(self, to_page: str, params: dict) -> tuple[bool, str | None]:
        if not st.session_state.get('authenticated'):
            return False, "Login erforderlich"
        return True, None

router.add_guard(AuthGuard())

# Navigation Events
@dataclass
class NavigationEvent:
    event_id: str
    event_type: NavigationEventType  # NAVIGATE, BACK, FORWARD, REDIRECT
    from_page: str | None
    to_page: str
    params: dict[str, Any]
    timestamp: datetime
```

### Core Module: Session (`core/session.py` - 668 Zeilen)
**Pattern**: Enhanced Session Management mit Persistence

```python
from core.session import SessionManager, FormSnapshot

# Session Recovery nach Browser-Refresh
from core_integration import bootstrap_session

session_id_param = st.query_params.get('session_id')
user_session = bootstrap_session(
    session_id=session_id_param,
    user_id=st.session_state.get('user_id')
)

if user_session:
    st.toast("Sitzung wiederhergestellt")

# Form Snapshots (Undo/Redo)
@dataclass
class FormSnapshot:
    snapshot_id: str
    form_id: str
    data: dict[str, Any]
    timestamp: datetime
    description: str = ""

# Navigation History
@dataclass
class NavigationEntry:
    page: str
    params: dict[str, Any]
    timestamp: datetime
```

### Core Module: Form Manager (`core/form_manager.py` - 1620 Zeilen)
**Pattern**: Enterprise-Grade Form Validation & State

```python
from core.form_manager import FormManager, FormState

form_mgr = FormManager()

# Form mit Validierung
form_state = form_mgr.create_form(
    form_id='customer_form',
    fields={
        'name': {'type': 'text', 'required': True, 'min_length': 3},
        'email': {'type': 'email', 'required': True},
        'age': {'type': 'number', 'min': 18, 'max': 120}
    }
)

# Validierung
errors = form_mgr.validate(form_state)
if not errors:
    form_mgr.submit(form_state)

# Snapshots für Undo/Redo
form_mgr.create_snapshot(form_state, description="Before changes")
form_mgr.restore_snapshot(snapshot_id)
```

### Core Module: Jobs (`core/jobs.py` - Job Scheduler)
**Pattern**: Background Job Scheduling

```python
from core.jobs import JobManager, Job

job_mgr = JobManager()

# Cron-basierte Jobs
job_mgr.schedule_job(
    name="contract_expiry_check",
    func=check_expiring_contracts,
    trigger="cron",
    hour=8,
    minute=0
)

# Intervall-basierte Jobs
job_mgr.schedule_job(
    name="cache_warmup",
    func=warmup_cache,
    trigger="interval",
    hours=1
)

# One-time Jobs
job_mgr.schedule_job(
    name="send_reminder",
    func=send_reminder,
    trigger="date",
    run_date=datetime.now() + timedelta(days=7),
    args=[customer_id]
)
```

### Core Module: Security (`core/security.py`)
**Pattern**: Role-Based Access Control

```python
from core.security import SecurityManager, Permission

security = SecurityManager()

# Permission Checks
@security.requires_permission(Permission.ADMIN)
def admin_function():
    pass

# Role-Based Access
if security.has_role(user_id, 'admin'):
    render_admin_panel()
```

### Monitoring & Tracing (Optional)
**Dateien**: `app_tracing.py`, `app_evaluation.py`, `app_status.py`

**Performance Tracking**:
```python
@app_tracer(operation_name="my_function")
def my_function():
    # Automatisches Tracing
    pass

# Manuelle Events
track_success("operation_name")
track_error("operation_name", error_message)
evaluate_performance("operation_name", execution_time)
```

## Background Jobs & Scheduling

### APScheduler Integration
**Package**: `APScheduler==3.11.0` - Background Job Scheduler

**Pattern**:
```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit

# Initialisiere Scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Shutdown bei App-Exit
atexit.register(lambda: scheduler.shutdown())

# Cron-basierte Jobs
scheduler.add_job(
    func=check_expiring_contracts,
    trigger=CronTrigger(hour=8, minute=0),  # Täglich um 8:00
    id='contract_check',
    replace_existing=True
)

# Intervall-basierte Jobs
scheduler.add_job(
    func=update_cache,
    trigger='interval',
    hours=1,
    id='cache_refresh'
)

# One-time delayed Jobs
scheduler.add_job(
    func=send_reminder,
    trigger='date',
    run_date=datetime.now() + timedelta(days=7),
    args=[customer_id]
)
```

**Typische Use Cases**:
- **Contract Expiry Checks**: Täglich ablaufende Verträge prüfen
- **Cache Warmup**: Stündlich häufig genutzte Daten vorladen
- **Report Generation**: Wöchentliche/monatliche Reports
- **Data Cleanup**: Alte Daten archivieren/löschen

### Redis Integration (Optional)
**Package**: `redis==6.4.0` - In-Memory Cache/Queue

**Pattern**:
```python
import redis

# Connection
r = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

# Caching
r.setex('product:123', 3600, json.dumps(product_data))  # TTL: 1h
cached = json.loads(r.get('product:123'))

# Pub/Sub für Events
r.publish('new_order', json.dumps({'order_id': 456}))

# Task Queue
r.lpush('pdf_generation_queue', json.dumps({
    'customer_id': 123,
    'template': 'multi_offer'
}))

# Worker konsumiert Queue
while True:
    task = r.brpop('pdf_generation_queue', timeout=5)
    if task:
        process_pdf_task(json.loads(task[1]))
```

**Wichtig**:
- **Redis ist OPTIONAL** - App funktioniert auch ohne
- **Fallback**: Nutze Streamlit `st.cache_data` wenn Redis nicht verfügbar
- **Connection Pool**: Für Production mit Connection Pooling

---

## OpenTelemetry Monitoring (Optional)

### Architektur
**Dateien**: `app_tracing.py`, `app_evaluation.py`

**Dependencies**:
```
opentelemetry-api>=1.20.0
opentelemetry-sdk>=1.20.0
opentelemetry-exporter-otlp>=1.20.0
opentelemetry-instrumentation-requests>=0.41b0
opentelemetry-instrumentation-sqlite3>=0.41b0
prometheus_client==0.22.1
```

**Setup**:
```python
# app_tracing.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Initialize Tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# OTLP Exporter (AI Toolkit: http://localhost:4318)
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4318",
    insecure=True
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)

# Decorator für Auto-Tracing
def app_tracer(operation_name: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(operation_name) as span:
                span.set_attribute("function", func.__name__)
                try:
                    result = func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(trace.Status(
                        trace.StatusCode.ERROR,
                        description=str(e)
                    ))
                    span.record_exception(e)
                    raise
        return wrapper
    return decorator
```

**Usage in Code**:
```python
from app_tracing import app_tracer
from app_evaluation import track_success, track_error

@app_tracer(operation_name="generate_pdf")
def generate_pdf(customer_id: int):
    try:
        # Business Logic
        pdf_path = create_pdf(customer_id)
        track_success("pdf_generation")
        return pdf_path
    except Exception as e:
        track_error("pdf_generation", str(e))
        raise
```

**Viewing Traces**:
```bash
# In VSCode mit AI Toolkit
# Ctrl+Shift+P → "AI Toolkit: Open Tracing"
# Zeigt alle Spans, Execution Times, Errors
```

**Prometheus Metrics**:
```python
from prometheus_client import Counter, Histogram, start_http_server

# Metrics definieren
pdf_generated = Counter('pdf_generated_total', 'Total PDFs generated')
pdf_generation_time = Histogram('pdf_generation_seconds', 'PDF generation time')

# Metrics nutzen
with pdf_generation_time.time():
    generate_pdf(customer_id)
pdf_generated.inc()

# Metrics Server starten
start_http_server(8000)  # Metrics auf http://localhost:8000/metrics
```

**Wichtig**:
- **OPTIONAL**: App funktioniert ohne Monitoring vollständig
- **AI Toolkit Integration**: VSCode Extension für Trace-Visualisierung
- **Environment Toggle**: `ENABLE_TRACING=false` um zu deaktivieren

## Backend API System (FastAPI/Pydantic)

### Architektur
**Verzeichnis**: `solar-calculator-pro/backend/api/v1/` - REST API Endpoints

**Stack**:
- **FastAPI 0.116.1** - Modern API Framework
- **Pydantic 2.11.9** - Data Validation
- **Uvicorn 0.35.0** - ASGI Server

**Pattern**:
```python
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/customers", tags=["CRM"])

class CustomerCreate(BaseModel):
    """Pydantic Model für Eingabe-Validierung."""
    name: str = Field(..., min_length=1, max_length=200)
    email: str | None = Field(None, pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    phone: str | None = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Max Mustermann",
                "email": "max@example.com",
                "phone": "+49 123 456789"
            }
        }

class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str | None
    created_at: str

@router.post("/", response_model=CustomerResponse, status_code=201)
async def create_customer(customer: CustomerCreate):
    """Erstellt neuen Kunden."""
    try:
        # Business Logic
        customer_id = save_customer_to_db(customer.model_dump())
        return CustomerResponse(
            id=customer_id,
            name=customer.name,
            email=customer.email,
            created_at=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int):
    customer = load_customer_from_db(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
```

**Server starten**:
```python
# backend/main.py
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Solar Calculator API", version="1.0.0")

# Register Routers
from backend.api.v1 import crm, contracts
app.include_router(crm.router)
app.include_router(contracts.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Wichtig**:
- **Pydantic Models** für Type Safety und Auto-Dokumentation
- **Async/Await** für IO-intensive Operationen
- **OpenAPI Docs**: Automatisch unter `/docs` verfügbar
- **CORS**: Für Frontend-Integration konfigurieren

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Video Server System (Intro-Screen)
**Hauptdatei**: `video_server.py` - HTTP Server für Video-Streaming

**Architektur**:
- Separater HTTP-Server (Port 8503+) neben Streamlit
- Singleton-Pattern verhindert doppelte Server-Starts
- Auto-Port-Finding bei belegtem Port
- Videos aus `static/intro_videos/`

**Integration in gui.py**:
```python
from video_server import start_video_server, get_server_status

# Prüfe ob Server bereits läuft
server_status = get_server_status()
if not server_status.get('running', False):
    def _start_video_server_safe():
        success, port, msg = start_video_server(port=8503, retry_attempts=3)
        if success:
            print(f"✓ Video-Server auf http://localhost:{port}")
    
    video_server_thread = threading.Thread(
        target=_start_video_server_safe, 
        daemon=True, 
        name="VideoServer"
    )
    video_server_thread.start()
```

**Wichtig**:
- Server MUSS als Daemon-Thread starten (`daemon=True`)
- NIEMALS `server.serve_forever()` im Main-Thread aufrufen
- Health-Check Endpoint: `http://localhost:8503/health`
- CORS-Header automatisch gesetzt für Cross-Origin-Requests

---

**Letzte Aktualisierung**: 2026-01-03
**Version**: 1.3

---

## Navigation & Routing System

### 4. Navigation & Routing System
**Dateien**: `core/router.py`, `core/navigation_history.py`

**Pattern**:
```python
from core.router import get_router, navigate

router = get_router()
navigate('crm', params={'customer_id': 123})  # Navigate with params
router.go_back()  # Browser-style navigation
```

**Breadcrumbs**: `render_breadcrumbs()` für Navigation-Historie

## Additional Tools & Utilities

### Excel Processing Tools
**Dateien**: `excel_exporter.py`, `excel_processing.py`, `excel_grid_ui.py`

```python
# Excel Export
from excel_exporter import export_to_excel
import pandas as pd

df = pd.DataFrame(data)
export_to_excel(df, filename='export.xlsx', sheet_name='Data')

# Excel Grid UI
from excel_grid_ui import render_excel_grid

df = render_excel_grid(
    data=initial_data,
    editable=True,
    key="excel_grid"
)
```

### Analysis & Debugging Tools
**Verzeichnis**: `nützliche tools/`

Wichtige Utilities:
- `cache_leerer.py`: Streamlit Cache leeren
- `analyze_alle_duplikate.py`: Duplikate finden
- `app_diagnostics.py`: Diagnostik-Tools
- `app_auto_fixer.py`: Automatische Fehlerbehebung
- `add_all_declarations.py`: Type Annotations hinzufügen

### Monitoring Tools
**Dateien**: `app_tracing.py`, `app_evaluation.py`, `app_status.py`, `app_health_monitor.py`

```python
# Tracing Decorator
from app_tracing import app_tracer

@app_tracer(operation_name="my_function")
def my_function():
    # Automatisches Performance-Tracking
    pass

# Success/Error Tracking
from app_evaluation import track_success, track_error

track_success("operation_name")
track_error("operation_name", error_message)

# Health Monitoring
from app_health_monitor import HealthMonitor

monitor = HealthMonitor()
status = monitor.check_all()  # Prüft DB, Cache, APIs, etc.
```

## Important Module Groups

### Admin UI Modules (15+ Dateien)
Alle beginnen mit `admin_*`:
- `admin_panel.py`: Haupt-Admin-Interface
- `admin_product_database_ui.py`: Produktdatenbank-Verwaltung
- `admin_security.py`: Sicherheits-Layer (358 Zeilen)
- `admin_price_matrix_upload.py`: Preis-Matrizen
- `admin_pv_mounting_ui.py`: PV-Unterkonstruktionen
- `admin_heatpump_settings_ui.py`: Wärmepumpen-Einstellungen
- `admin_controlling_settings_ui.py`: Controlling-Konfiguration
- `admin_logo_management_ui.py`: Logo-Verwaltung
- `admin_pdf_settings_ui.py`: PDF-Vorlagen

### CRM Module (50+ Dateien)
**Hauptdatei**: `crm.py` (2390 Zeilen)

**Features-Verzeichnis** (`crm/features/`):
- `contract_manager.py` (1272 Zeilen): Verträge & Garantien
- `email_manager.py`: E-Mail-Integration
- `call_manager.py`: Anruf-Protokollierung
- `task_manager.py`: Aufgabenverwaltung
- `feedback_manager.py`: Feedback-System
- `forecasting_engine.py`: Umsatz-Prognosen
- `knowledge_base.py`: Wissensdatenbank
- `lead_scoring.py`: Lead-Bewertung
- `offer_tracker.py`: Angebots-Tracking
- `reporting_engine.py`: Report-Generierung
- `tag_manager.py`: Tag-System
- `template_manager.py`: Template-Verwaltung
- `dashboard_widgets.py`: 6+ Widget-Klassen
- `geo_mapper.py`: Geo-Visualisierung
- `note_manager.py`: Notizen

**Integration Module** (`crm/integration/`):
- `pdf_integration.py`: PDF-Anbindung
- `email_integration.py`: E-Mail-Versand

### Controlling Modules (15+ Dateien)
**Hauptdatei**: `controlling_ui.py` (2798 Zeilen)

**Core Module** (`controlling/`):
- `models.py`: SQLAlchemy ORM-Modelle
- `managers.py`: EmployeeManager, PositionManager, CriterionManager, PerformanceDataManager
- `analytics.py`: AnalyticsEngine für Auswertungen
- `team_manager.py`: Team-Hierarchien
- `period_manager.py`: Auswertungsperioden
- `ranking_system.py`: Mitarbeiter-Rankings
- `notifications.py`: Benachrichtigungen
- `report_generator.py`: Report-Erstellung
- `chart_generator.py`: Chart-Generierung
- `pdf_config.py`: PDF-Export-Konfiguration

### Pricing Modules (20+ Dateien)
**Verzeichnis**: `pricing/`

**Engines**:
- `pv_pricing_engine.py`: PV-System-Preisberechnung
- `enhanced_pricing_engine.py`: Erweiterte Preislogik
- `combined_pricing_engine.py`: Multi-Modifier-Kombination
- `calculate_per_engine.py`: "Berechnen pro" Logik (Stück/Meter/kWp/pauschal)
- `pricing_modification_engine.py`: Preisanpassungen
- `dynamic_pricing_engine.py`: Dynamische Preise

**Managers**:
- `profit_margin_manager.py`: Gewinnmargen-Verwaltung
- `vat_manager.py`: Mehrwertsteuer-Berechnung
- `dynamic_key_manager.py`: Dynamische Key-Generierung

**Utilities**:
- `pricing_cache.py`: Preis-Caching
- `pricing_validation.py`: Preis-Validierung
- `pricing_audit.py`: Audit-Trail
- `real_time_pricing_updates.py`: Live-Updates

### Core Modules (80+ Dateien)
**Verzeichnis**: `core/`

**Navigation & Routing**:
- `router.py` (834 Zeilen): Browser-Style Navigation
- `navigation_history.py`: Navigation-Historie

**Session Management**:
- `session.py` (668 Zeilen): Session-Persistenz
- `session_manager.py`: Session-Verwaltung

**Forms & Validation**:
- `form_manager.py` (1620 Zeilen): Form-Validierung & State
- `forms.py`: Form-Helpers
- `widget_validation.py`: Widget-Validierung

**Caching**:
- `cache.py`: Cache-Core
- `cache_warming.py`: Cache-Preloading
- `cache_invalidation.py`: Cache-Invalidierung
- `cache_monitoring.py`: Cache-Metriken

**Jobs & Scheduling**:
- `jobs.py`: Job-Manager
- `job_scheduler.py`: Scheduler-Integration
- `background_tasks.py`: Background-Tasks
- `job_repository.py`: Job-Persistenz
- `job_notifications.py`: Job-Benachrichtigungen

**Database**:
- `database.py`: DatabaseManager
- `connection_manager.py`: Connection-Pooling mit Failover
- `db_performance.py`: Performance-Optimierung
- `db_extensions.py`: DB-Erweiterungen
- `migrations.py`: Migration-System
- `migration_manager.py`: Migration-Verwaltung
- `migration_templates.py`: Migration-Templates

**Logging & Monitoring**:
- `logging_system.py`: Strukturiertes Logging
- `logging_config.py`: Log-Konfiguration

**Security & Access Control**:
- `security.py`: RBAC-System
- `authentication.py`: Auth-Manager

**Dependency Injection**:
- `dependency_injection.py`: DI-Container
- `containers.py`: Service-Container

**Widgets & Components**:
- `widgets.py`: Widget-System
- `widget_persistence.py`: Widget-Persistenz
- `accessibility.py`: Accessibility-Features

### PDF Template Engine (6 Dateien)
**Verzeichnis**: `pdf_template_engine/`

- `dynamic_overlay.py`: Text-Overlays mit ReportLab
- `merger.py`: Multi-Page PDF-Merging
- `placeholders.py`: 50+ Placeholder-Mappings
- `overlay.py`: Low-Level PDF-Overlay
- `prepare_backgrounds.py`: Multi-Firma Background-Vorbereitung
- `template_manager.py`: Template-Verwaltung

### Calculations Modules
- `calculations.py`: PV-Berechnungen
- `calculations_heatpump.py` (1459 Zeilen): Wärmepumpen-Berechnungen
- `financial_calculations.py`: Finanzanalysen
- `amortisation_calculation.py`: Amortisationsberechnungen
- `yield_optimization.py`: Ertragsoptimierung

### 3D Visualization
- `pv3d.py` (4545 Zeilen): PyVista 3D-Engine
- `solar_3d_view_module.py`: Streamlit-Integration
- `pv3d_plotly.py`: Plotly-Alternative
- `pv_visuals.py`: 2D-Chart-Generierung

### Agent/AI System
**Verzeichnis**: `Agent/`
- `agent_ui.py`: Agent-Interface
- `ai_companion.py`: KI-Companion
- Workspace-Isolation: `agent_workspace/` (Sandbox)

## Critical File Sizes & Complexity

**Mega-Dateien** (1000+ Zeilen):
- `gui.py`: 4633 Zeilen - Main entry point
- `pv3d.py`: 4545 Zeilen - 3D visualization engine
- `controlling_ui.py`: 2798 Zeilen - Controlling UI
- `database.py`: 2900+ Zeilen - Database core
- `crm.py`: 2390 Zeilen - CRM orchestrator
- `product_db.py`: 1811 Zeilen - Product database
- `core/form_manager.py`: 1620 Zeilen - Form validation
- `calculations_heatpump.py`: 1459 Zeilen - Heat pump calculations
- `components/shadcn_ui_integration.py`: 1290 Zeilen - UI components
- `crm/features/contract_manager.py`: 1272 Zeilen - Contract management
- `core/router.py`: 834 Zeilen - Navigation system
- `core/session.py`: 668 Zeilen - Session management

## Packaging & Dependencies

### pyproject.toml vs requirements.txt
**Achtung**: Project nutzt **requirements.txt** (248 Pakete), KEIN pyproject.toml!

**Kritische Dependencies**:
```
streamlit==1.49.1
reportlab==4.4.3
PyPDF2
pypdf
pyvista>=0.43.0
vtk>=9.3.0
stpyvista
sqlalchemy==2.0.43
alembic==1.16.5
fastapi==0.116.1
pydantic==2.11.9
uvicorn==0.35.0
langchain==0.3.27
langchain-openai
opentelemetry-api>=1.20.0
opentelemetry-sdk>=1.20.0
plotly==6.3.0
altair==5.5.0
matplotlib==3.10.6
kaleido==1.0.0
pandas==2.3.2
numpy==2.3.2
APScheduler==3.11.0
redis==6.4.0
pytest==8.4.2
PyInstaller==6.15.0
openpyxl
xlrd
```

### Build System
**Build-Dateien**:
- `ARSCHIBALD_COMPLETE.spec`: PyInstaller Spec (kritisch für Build)
- `ARSCHIBALD_COMPLETE_SETUP.iss`: Inno Setup Config
- `BUILD_COMPLETE.bat`: Automatischer Build-Prozess
- `ARSCHIBALD_STARTEN.bat`: App-Starter

**Hidden Imports Pattern** (in .spec):
```python
hiddenimports = [
    'streamlit.runtime.scriptrunner.magic_funcs',
    'streamlit.components.v1',
    'reportlab.pdfgen.canvas',
    'reportlab.lib.pagesizes',
    'PyPDF2',
    'pypdf',
    'pyvista',
    'vtk',
    'stpyvista',
    'openpyxl.cell._writer',
    'langchain',
    'langchain_openai',
    'langchain_community',
    'sqlalchemy.sql.default_comparator',
    'plotly.graph_objs',
    'kaleido',
]
```

## Important Patterns & Conventions

### Naming Conventions
- **Admin UI**: `admin_*.py` (15+ files)
- **Tests**: `test_*.py` in `tests/` directory
- **Engines**: `*_engine.py` (26+ files)
- **Handlers**: `*_handler.py` (8+ files)
- **Managers**: `*_manager.py` (20+ files)
- **UI Rendering**: `render_*()` functions (100+ occurrences)
- **Calculations**: `calculate_*()` functions
- **Generators**: `generate_*()` functions

### Import Pattern für Optional Dependencies
```python
# Pattern für optionale Features
try:
    from optional_module import feature
    FEATURE_AVAILABLE = True
except ImportError as e:
    FEATURE_AVAILABLE = False
    
    # Fallback oder Dummy
    def feature(*args, **kwargs):
        return None

# Usage mit Feature-Flag
if FEATURE_AVAILABLE:
    result = feature()
else:
    st.warning("Feature nicht verfügbar")
```

### Streamlit Multi-Page Pattern
```python
# gui.py orchestriert alle Pages
import importlib

pages = {
    "CRM": "crm",
    "Controlling": "controlling_ui",
    "3D Visualisierung": "pv3d",
    "Wärmepumpen": "heatpump_ui",
    "Admin": "admin_panel"
}

selected_page = st.sidebar.selectbox("Navigation", pages.keys())
module_name = pages[selected_page]

try:
    module = importlib.import_module(module_name)
    if hasattr(module, 'render'):
        module.render()
except Exception as e:
    st.error(f"Fehler beim Laden von {selected_page}: {e}")
```

---

## Complete Module Reference

### Alle 26 Engine-Dateien
**Gefunden via `file_search(*_engine.py)`**:

1. **dynamic_pricing_engine.py**: Dynamische Echtzeit-Preisanpassungen
2. **product_rotation_engine.py**: Multi-Firma Produkt-Variation
3. **price_modification_engine.py**: Basis-Preismodifikation (+15% etc.)
4. **statistics_engine.py**: Statistische Analysen
5. **live_calculation_engine.py**: Live-Berechnungen während Eingabe
6. **pricing/enhanced_pricing_engine.py**: Erweiterte Preislogik mit Matrix
7. **pricing/pricing_modification_engine.py**: Pricing-Modifikationen
8. **pricing/combined_pricing_engine.py**: Multi-Modifier Kombination
9. **pricing/calculate_per_engine.py**: "Berechnen pro" (Stück/Meter/kWp)
10. **pricing/pv_pricing_engine.py**: PV-System Gesamt-Preisberechnung
11. **excel/excel_formula_engine.py**: Excel-Formel-Interpreter
12. **crm/features/forecasting_engine.py**: Umsatz-Prognosen
13. **crm/features/reporting_engine.py**: Report-Generierung
14. **backend/services/formula_engine.py**: Formel-Parsing für Backend
15. **core/cache_warming.py** → `CacheWarmingEngine`: Cache-Preloading
16. **core/cache_invalidation.py** → `InvalidationEngine`: Cache-Invalidierung
17. **core/session_persistence.py** → `SessionPersistenceEngine`: Session-Wiederherstellung
18. **core/widget_persistence.py** → `WidgetPersistenceEngine`: Widget-State-Persistenz
19. **core/widget_validation.py** → `ValidationEngine`: Widget-Validierung
20. **backend/core/pdf_bytes.py** → `PDFRenderingEngine`: PDF zu Bytes Konvertierung
21. **backend/tests/test_analytics_engine.py**: Analytics-Engine Tests
22. **backend/tests/test_formula_engine.py**: Formel-Engine Tests
23. **backend/tests/test_pricing_modification_engine.py**: Pricing-Mod Tests
24. **backend/tests/test_pv_pricing_engine.py**: PV-Pricing Tests
25. **nützliche tools/behavioral_analysis_engine.py**: Benutzerverhalten-Analyse
26. **controlling/analytics.py** → `AnalyticsEngine`: Employee-Performance-Analyse

### Alle 8 Handler-Dateien
**Gefunden via `file_search(*_handler.py)`**:

1. **price_matrix_error_handler.py**: Fehlerbehandlung für Preis-Matrizen
2. **verify_task2_placement_handler.py**: 3D-Platzierungs-Verifizierung
3. **utils/pv3d_placement_handler.py**: PV-Modul 3D-Platzierung
4. **ui_settings_handler.py**: UI-Einstellungen Handler
5. **theming/error_handler.py**: Theme-System Fehlerbehandlung
6. **performance_handler.py**: Performance-Monitoring
7. **backend/middleware/error_handler.py**: FastAPI Error Middleware
8. **components/progress_manager.py** → Handler-Pattern für Progress

### Alle 76 Manager-Dateien
**Top 20 Wichtigste** (aus 76 gefunden):

1. **password_manager.py**: Passwort-Verwaltung
2. **theme_manager.py**: Theme-System
3. **ui_state_manager.py**: UI-State-Verwaltung
4. **theming/security_manager.py**: Theme-Security
5. **theming/state_manager.py**: Theme-State
6. **theming/hot_reload_manager.py**: Hot-Reload für Themes
7. **pricing/dynamic_key_manager.py**: Dynamische Key-Generierung
8. **pricing/profit_margin_manager.py**: Gewinnmargen
9. **pricing/vat_manager.py**: MwSt-Verwaltung
10. **excel/excel_manager.py**: Excel-Integration
11. **core/connection_manager.py**: DB Connection Pooling + Failover
12. **core/session_manager.py**: Session-Verwaltung
13. **core/migration_manager.py**: Migration-System
14. **core/form_manager.py**: Form-Validation (1620 Zeilen)
15. **core/jobs.py** → `JobManager`: Background Jobs
16. **crm/utils/notification_manager.py**: CRM-Benachrichtigungen
17. **crm/utils/import_export_manager.py**: CRM Import/Export
18. **crm/features/feedback_manager.py**: Feedback-System
19. **crm/features/email_manager.py**: E-Mail-Integration
20. **crm/features/note_manager.py**: Notizen-Verwaltung

Vollständige Liste inkl.:
- `controlling/team_manager.py`: Team-Hierarchien
- `controlling/period_manager.py`: Auswertungsperioden
- `controlling/notifications.py` → `NotificationManager`
- `controlling/pdf_config.py` → `PDFConfigManager`
- `components/progress_manager.py` → `ProgressManager`
- `crm/features/knowledge_base.py` → `KnowledgeBaseManager`
- `crm/features/dashboard_widgets.py` → `WidgetManager`
- `backend/migrations/migration_manager.py`
- `backend/core/security_manager.py` → `SecurityManager`
- `backend/core/websocket_manager.py` → `WebSocketManager`
- **+56 weitere Manager-Dateien**

### Alle 100+ Manager/Engine/Handler Klassen
**Gefunden via grep "^class.*Engine|Manager|Handler"**:

**Security**:
- `SecurityManager` (backend/core/security_manager.py)
- `AuthenticationManager` (core/security.py)
- `AuthorizationManager` (core/security.py)
- `MFAManager` (core/security.py)
- `SessionManager` (core/security.py)
- `DataProtectionManager` (core/security.py)
- `ThemeSecurityManager` (.kiro/specs)

**Database & Migrations**:
- `DatabaseManager` (core/database.py)
- `MigrationManager` (core/migrations.py, core/migration_manager.py)
- `DatabaseFailoverManager` (core/connection_manager.py)
- `EnhancedConnectionManager` (core/connection_manager.py)

**Forms & Validation**:
- `FormManager` (core/form_manager.py - 1620 Zeilen)
- `ValidationEngine` (core/widget_validation.py)
- `WidgetPersistenceEngine` (core/widget_persistence.py)

**Jobs & Background Tasks**:
- `JobManager` (core/jobs.py)
- `JobNotificationManager` (core/job_notifications.py)
- `BackgroundTaskManager` (background_tasks.py)

**Caching**:
- `CacheWarmingEngine` (core/cache_warming.py)
- `InvalidationEngine` (core/cache_invalidation.py)

**Logging**:
- `LoggingConfigManager` (core/logging_config.py)

**Pricing**:
- `EnhancedPricingEngine` (calculations.py)
- `PricingEngine` (.kiro/specs)
- `DynamicKeyManager` (pricing/)
- `CalculatePerEngine` (pricing/)
- `ProfitMarginManager` (pricing/)
- `PricingModificationEngine` (pricing/)

**Controlling**:
- `EmployeeManager` (controlling/managers.py)
- `PositionManager` (controlling/managers.py)
- `CriterionManager` (controlling/managers.py)
- `PerformanceDataManager` (controlling/managers.py)
- `AnalyticsEngine` (controlling/analytics.py)
- `TeamManager` (controlling/team_manager.py)
- `PeriodManager` (controlling/period_manager.py)
- `NotificationManager` (controlling/notifications.py)
- `PDFConfigManager` (controlling/pdf_config.py)

**CRM**:
- `KnowledgeBaseManager` (crm/features/knowledge_base.py)
- `WidgetManager` (crm/features/dashboard_widgets.py)
- `NotificationManager` (crm/utils/notification_manager.py)

**Excel**:
- `ExcelManager` (excel/excel_manager.py)
- `FormulaEngine` (excel/excel_formula_engine.py)
- `BatchOperationManager` (excel/excel_batch_operations.py)

**PDF**:
- `PDFRenderingEngine` (backend/core/pdf_bytes.py)
- `PDFConfigManager` (controlling/pdf_config.py)

**Theming**:
- `ThemeManager` (theme_manager.py, theming/theme_manager.py)
- `HotReloadManager` (theming/hot_reload_manager.py)
- `ThemeStateManager` (.kiro/specs)
- `ErrorHandler` (theming/error_handler.py)

**Session**:
- `SessionManager` (core/session_manager.py, core/security.py)
- `SessionPersistenceEngine` (core/session_persistence.py)

**Components**:
- `ProgressManager` (components/progress_manager.py)
- `CSSTemplateManager` (css_template_manager.py)

**Backend**:
- `WebSocketManager` (backend/core/websocket_manager.py)
- `BackendProcessManager` (backend/tests/)
- `UpdateManager` (.kiro/specs)
- `EmojiManager` (.kiro/specs)

**+50 weitere Klassen** in Tests, Specs, und Backup-Ordnern

### Alle 150+ render_* Funktionen
**Gefunden via grep "^def render_"**:

**Core UI Functions**:
- `render_protected_admin_section()` - Admin-Bereiche mit Passwort
- `render_live_cost_preview()` - Live-Kosten-Vorschau (gui.py)
- `render_intro_screen()` - Intro mit Video
- `render_registration_form()` - Registration-Form

**Controlling (controlling_ui.py - 2798 Zeilen)**:
- `render_controlling_page()` - Haupt-Controlling-Seite
- `render_performance_entry_tab()` - Datenerfassung
- `render_report_generation_tab()` - Report-Generierung
- `render_report_dashboard()` - Report-Dashboard
- `render_archive_tab()` - Archiv
- `render_team_analysis_tab()` - Team-Analysen
- `render_comparison_tab()` - Vergleiche
- `render_ranking_tab()` - Rankings
- `render_pdf_color_settings()` - PDF-Farben

**Wärmepumpen (heatpump_ui.py - 5000+ Zeilen)**:
- `render_heatpump_analysis()` - Haupt-Analyse
- `render_building_analysis()` - Gebäude-Analyse
- `render_heatpump_selection()` - WP-Auswahl
- `render_radiator_check()` - Heizkörper-Check
- `render_economics_analysis()` - Wirtschaftlichkeit
- `render_pv_integration()` - PV-Integration
- `render_results_summary()` - Ergebnis-Zusammenfassung
- `render_3d_building_animation()` - 3D-Animation
- `render_renovation_planner()` - Sanierungs-Planer
- `render_optimization_tools()` - Optimierungs-Tools
- `render_subsidy_co2()` - Förderung & CO2
- `render_roi_benchmarking()` - ROI-Vergleich
- `render_heatpump()` - Main Entry Point
- `render_dynamic_tariff_tab()` - Dynamische Tarife
- `render_advanced_analysis()` - Erweiterte Analysen

**Excel (excel_grid_ui.py, excel_product_pricing_ui.py)**:
- `render_excel_grid_ui()` - Excel-Grid
- `render_price_matrix_tab()` - Preis-Matrix
- `render_product_price_config_ui()` - Produkt-Preis-Konfig
- `render_product_price_config_inline()` - Inline-Konfig

**3D Visualization**:
- `render_3d_view()` - 3D-Ansicht (solar_3d_view_module.py, pv3d.py)
- `render_image_bytes()` - Image zu Bytes (pv3d.py)
- `render_modules_lod()` - Level-of-Detail für Module
- `render_module_placement_panel()` - Modul-Platzierung
- `render_export_action_buttons()` - Export-Buttons

**PV Visuals (pv_visuals.py)**:
- `render_yearly_production_pv_data()` - Jahresproduktion
- `render_break_even_pv_data()` - Break-Even
- `render_amortisation_pv_data()` - Amortisation
- `render_co2_savings_visualization()` - CO2-Einsparungen

**PDF System (repair_pdf/**, pdf_*.py)**:
- `render_pdf_ui()` - PDF-Haupt-UI
- `render_pdf_preview_interface()` - PDF-Vorschau
- `render_pdf_theme_manager()` - PDF-Theme
- `render_pdf_structure_manager()` - PDF-Struktur
- `render_pdf_debug_section()` - PDF-Debug
- `render_central_pdf_ui()` - Zentrale PDF-UI
- `render_multi_offer_generator()` - Multi-Angebots-Generator

**Analysis (repair_pdf/analysis.py - 8800+ Zeilen!)**:
- `render_analysis()` - Haupt-Analyse
- `render_pricing_modifications_ui()` - Preis-Modifikationen
- `render_daily_production_switcher()` - Tages-Produktion
- `render_tariff_cube_switcher()` - Tarif-Würfel
- `render_weekly_production_switcher()` - Wochen-Produktion
- `render_yearly_production_switcher()` - Jahres-Produktion
- `render_project_roi_matrix_switcher()` - ROI-Matrix
- `render_feed_in_revenue_switcher()` - Einspeise-Erlös
- `render_production_vs_consumption_switcher()` - Produktion vs Verbrauch
- `render_co2_savings_value_switcher()` - CO2-Einsparungen
- `render_investment_value_switcher()` - Investitionswert
- `render_storage_effect_switcher()` - Speicher-Effekt
- `render_selfuse_stack_switcher()` - Eigenverbrauch-Stack
- `render_cost_growth_switcher()` - Kosten-Wachstum
- `render_selfuse_ratio_switcher()` - Eigenverbrauchs-Quote
- `render_roi_comparison_switcher()` - ROI-Vergleich
- `render_scenario_comparison_switcher()` - Szenario-Vergleich
- `render_tariff_comparison_switcher()` - Tarif-Vergleich
- `render_income_projection_switcher()` - Einkommens-Projektion
- `render_advanced_economics()` - Erweiterte Wirtschaftlichkeit
- `render_detailed_energy_analysis()` - Detaillierte Energie-Analyse
- `render_technical_calculations()` - Technische Berechnungen
- `render_financial_scenarios()` - Finanz-Szenarien
- `render_environmental_calculations()` - Umwelt-Berechnungen
- `render_optimization_suggestions()` - Optimierungs-Vorschläge
- `render_financing_analysis()` - Finanzierungs-Analyse
- `render_advanced_calculations_section()` - Erweiterte Berechnungen
- `render_advanced_financial_analysis()` - Erweiterte Finanz-Analyse
- `render_advanced_energy_analysis()` - Erweiterte Energie-Analyse
- `render_advanced_environmental_analysis()` - Erweiterte Umwelt-Analyse
- `render_advanced_technical_analysis()` - Erweiterte Technik-Analyse
- `render_advanced_comparison_analysis()` - Erweiterte Vergleichs-Analyse

**Admin Panel (repair_pdf/admin_panel.py)**:
- `render_admin_panel()` - Haupt-Admin-Panel
- `render_company_crud_tab()` - Firmen-CRUD
- `render_product_management()` - Produkt-Verwaltung
- `render_general_settings_extended()` - Allgemeine Einstellungen
- `render_price_matrix()` - Preis-Matrix
- `render_tariff_management()` - Tarif-Verwaltung
- `render_visualization_settings()` - Visualisierungs-Einstellungen
- `render_advanced_settings()` - Erweiterte Einstellungen
- `render_pdf_design_settings()` - PDF-Design
- `render_api_key_settings()` - API-Keys
- `render_company_text_templates_tab()` - Firmen-Text-Templates
- `render_company_image_templates_tab()` - Firmen-Bild-Templates

**Weitere wichtige render_ Funktionen**:
- `render_info_platform()` - Info-Plattform
- `render_heating_calculator()` - Heizungs-Rechner
- `render_financial_tools_section()` - Finanz-Tools
- `render_quick_calc()` - Schnell-Rechner
- `render_options()` - Optionen
- `render_services_selection()` - Dienstleistungs-Auswahl
- `render_job_queue_widget()` - Job-Queue-Widget
- `render_job_card()` - Job-Karte
- `render_job_submission_form()` - Job-Formular
- `render_job_tracker()` - Job-Tracker
- `render_job_manager_admin()` - Job-Manager-Admin
- `render_logo_position_settings()` - Logo-Positionen
- `render_logo_upload_section()` - Logo-Upload
- `render_logo_management_section()` - Logo-Verwaltung
- `render_logo_edit_section()` - Logo-Bearbeitung
- `render_logo_statistics_section()` - Logo-Statistiken
- `render_help_sidebar()` - Hilfe-Sidebar
- `render_mounting_calculation_summary()` - Unterkonstruktions-Zusammenfassung
- `render_pv_mounting_selection()` - PV-Unterkonstruktions-Auswahl
- `render_solar_calculator_with_shadcn()` - Solar-Rechner mit Shadcn
- `render_service_display_config()` - Service-Display-Konfig
- `render_all_selected_charts_to_pdf()` - Charts zu PDF
- `render_financial_tools_to_pdf()` - Finanz-Tools zu PDF

**+50 weitere render_ Funktionen** in Specs, Tests, und Backup-Ordnern

### Vollständiges Datenbank-Schema
**26 CREATE TABLE Statements gefunden in database.py**:

```sql
-- Core System
CREATE TABLE IF NOT EXISTS admin_settings (...)
CREATE TABLE IF NOT EXISTS products (...)
CREATE TABLE IF NOT EXISTS companies (...)
CREATE TABLE IF NOT EXISTS company_documents (...)
CREATE TABLE IF NOT EXISTS pdf_templates (...)
CREATE TABLE IF NOT EXISTS company_text_templates (...)
CREATE TABLE IF NOT EXISTS company_image_templates (...)

-- CRM System
CREATE TABLE IF NOT EXISTS crm_customers (...)
CREATE TABLE IF NOT EXISTS crm_tasks (...)
CREATE TABLE IF NOT EXISTS crm_activities (...)
CREATE TABLE IF NOT EXISTS crm_reminders (...)
CREATE TABLE IF NOT EXISTS crm_tags (...)
CREATE TABLE IF NOT EXISTS customer_tags (...)
CREATE TABLE IF NOT EXISTS customer_documents (...)
CREATE TABLE IF NOT EXISTS project_calculations (...)

-- Dashboard & Analytics
CREATE TABLE IF NOT EXISTS user_dashboard_settings (...)
CREATE TABLE IF NOT EXISTS sales_targets (...)
CREATE TABLE IF NOT EXISTS sales_forecasts (...)

-- Knowledge Base
CREATE TABLE IF NOT EXISTS kb_categories (...)
CREATE TABLE IF NOT EXISTS kb_articles (...)
CREATE TABLE IF NOT EXISTS kb_ratings (...)

-- Heat Pumps
CREATE TABLE IF NOT EXISTS heat_pumps (...)
```

**SQLAlchemy Models** (controlling/models.py):
- `Employee`, `Position`, `Criterion`, `PerformanceData`
- `EvaluationPeriod`, `Team`, `Report`
- Alle mit `str`-basierten Enums für Pickle-Serialisierung

### FastAPI Backend API Endpoints
**160+ API-Dateien gefunden in backend/api/v1/**:

**Core APIs**:
- `auth_advanced.py`: Advanced Authentication
- `admin_dashboard.py`: Admin-Dashboard
- `application_monitoring.py`: App-Monitoring
- `audit.py`: Audit-Trail
- `backup_recovery.py`, `backup.py`: Backup-System
- `background_jobs.py`: Background Jobs API

**Database**:
- `database.py`, `database_management.py`: DB-Management
- `database_backup.py`: DB-Backup
- `database_optimization.py`: DB-Optimierung
- `database_production.py`: Production-DB
- `database_type.py`: DB-Type-Handling
- `data_migration.py`: Data-Migration
- `data_privacy.py`: Datenschutz

**PV/WP System**:
- `battery_storage.py`, `battery.py`: Batterie-Speicher
- `building_geometry.py`: Gebäude-Geometrie
- `combined_system.py`: Kombinierte Systeme
- `calculation_functions.py`: Berechnungs-Funktionen
- `catalog.py`: Produkt-Katalog

**PDF**:
- `batch_pdf.py`: Batch-PDF-Generierung
- `extended_pv_pdf.py`: Erweiterte PV-PDFs
- `extended_offer_pdf.py`: Erweiterte Angebots-PDFs
- `extended_wp_pdf.py`: Erweiterte WP-PDFs

**CRM**:
- `crm_advanced.py`: Erweiterte CRM-Features
- `crm_dashboard.py`: CRM-Dashboard
- `contract_warranty.py`: Verträge & Garantien
- `contracts.py`: Vertrags-Management
- `customer_data.py`: Kundendaten

**3D**:
- `animation_3d.py`: 3D-Animationen
- `collision_detection.py`: Kollisionserkennung
- `export_3d.py`: 3D-Export

**Utilities**:
- `advanced_charts.py`: Erweiterte Charts
- `additional_components.py`, `additional_features.py`: Zusatz-Features
- `caching_system.py`: Caching
- `component_toggles.py`: Feature-Toggles
- `currency.py`: Währungs-Konvertierung
- `encryption.py`: Verschlüsselung
- `exports.py`: Export-Funktionen
- `environment_config.py`: Umgebungs-Konfiguration
- `deployment_automation.py`: Deployment-Automation

**Companies**:
- `companies.py`, `company_management.py`: Firmen-Verwaltung
- `branding.py`: Branding-Management

**Documents**:
- `documents.py`: Dokumenten-Verwaltung

**Energy**:
- `energy_flow_visualization.py`: Energie-Fluss-Visualisierung

**+100 weitere API-Endpoints**

### Components Verzeichnis
**45 Dateien in components/**:

**Shadcn-UI Components**:
- `shadcn_ui_integration.py` (1290 Zeilen) - Haupt-Integration
- `accordion.py`, `alert.py`, `badge.py` - UI-Komponenten
- `breadcrumb.py`, `card.py`, `dropdown.py` - Navigation
- `form_components.py`, `forms.css` - Forms
- `metric_card.py` - Metriken
- `pagination.py`, `popover.py`, `progress.py` - Interaktive Elemente
- `skeleton.py`, `table.py` - Layout

**React Components** (TSX):
- `CalculationProgress.tsx` - Berechnungs-Fortschritt
- `CustomerForm.tsx`, `ProjectForm.tsx` - Formulare
- `ModernSolarCalculator.tsx`, `ModernSolarCalculator.css` - Solar-Rechner

**Manager & Settings**:
- `progress_manager.py` - Progress-Verwaltung
- `progress_settings.py` - Progress-Einstellungen
- `progress_demo.py` - Demo

**Documentation**:
- 12+ Markdown-Dateien mit QUICK_REFERENCE, REFERENCE, USAGE_EXAMPLE
- Für jede Komponente: Alert, Badge, Card, Extended Components, Form Components, Metric Card, Table

### .streamlit Konfiguration
**3 Dateien in .streamlit/**:
- `config.toml` - Streamlit-Konfiguration
- `secrets.toml` - API-Keys & Secrets
- `static/` - Statische Assets

**config.toml Struktur**:
```toml
[server]
port = 8501
headless = false
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
serverAddress = "localhost"

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"

[runner]
magicEnabled = true
installTracer = false
fixMatplotlib = true
```

---

## Advanced Patterns & Code Architecture

### @dataclass Usage Patterns (100+ Verwendungen)
**Kritische Dataclasses** für Streamlit Session State (pickle-serializable):

**Core System**:
- `core/config.py`: 7 @dataclass (AppConfig, DatabaseConfig, CacheConfig, LoggingConfig, SecurityConfig, SessionConfig, AppConfigValidator)
- `core/session.py`: 4 @dataclass (UserSession, FormState, NavigationEntry, FormSnapshot)
- `core/router.py`: 2 @dataclass (NavigationEvent, RouteConfig)
- `core/navigation_history.py`: 2 @dataclass (NavigationEntry, NavigationState)
- `core/jobs.py`: 2 @dataclass (Job, JobResult)
- `core/form_manager.py`: 3 @dataclass (FormState, ValidationResult, FormSnapshot)
- `core/cache.py`, `core/cache_monitoring.py`: 3 @dataclass (CacheEntry, CacheStats, InvalidationRule)
- `core/connection_manager.py`: 4 @dataclass (ConnectionConfig, ConnectionPool, ConnectionMetrics, FailoverStrategy)
- `core/dependency_injection.py`: 1 @dataclass (ServiceDescriptor)
- `core/db_performance.py`: 2 @dataclass (QueryMetrics, OptimizationHint)

**Controlling**:
- `controlling/notifications.py`: 2 @dataclass (Notification, NotificationTemplate)
- `controlling/pdf_config.py`: 1 @dataclass (PDFColorSettings)
- `controlling/position_criteria.py`: 1 @dataclass (CriterionWeight)

**Excel & Pricing**:
- `excel/excel_models.py`: 8 @dataclass (ExcelCell, ExcelRow, ExcelSheet, ExcelWorkbook, CellFormat, ValidationRule, Formula, ConditionalFormat)
- `excel/excel_lazy_loader.py`: 2 @dataclass (LoadState, CellData)
- `excel/excel_product_pricing.py`: 1 @dataclass (PricingConfig)
- `excel/custom_dynamic_calculation.py`: 1 @dataclass (CalculationContext)
- `financial_calculations.py`: 1 @dataclass (PriceBreakdown - frozen=True für Immutability)
- `heatpump_pricing.py`: 1 @dataclass (HeatPumpPricingConfig)

**Backend Services**:
- `backend/services/migration_service.py`: 2 @dataclass (MigrationTask, MigrationResult)
- `backend/services/dropdown_key_service.py`: 2 @dataclass (DropdownKey, DropdownConfig)
- `backend/services/calculation_result_key_service.py`: 2 @dataclass (CalculationKey, KeyMetadata)

**Testing & Monitoring**:
- `app_health_monitor.py`: 1 @dataclass (HealthStatus)
- `app_diagnostics.py`: 1 @dataclass (DiagnosticResult)
- `background_tasks.py`: 1 @dataclass (TaskConfig)
- `components/progress_manager.py`: 1 @dataclass (ProgressState)

**WICHTIG für Session State**:
```python
# ALLE @dataclass MÜSSEN pickle-serializable sein!
@dataclass
class MyData:
    # Automatisch serializable wenn alle Felder pickle-serializable sind
    value: int
    name: str
    items: list[str]
    
    # Für komplexe Typen: Explicit Pickle Support
    def __getstate__(self):
        return self.__dict__.copy()
    
    def __setstate__(self, state):
        self.__dict__.update(state)
```

### Streamlit Caching Patterns (49 Verwendungen)
**@st.cache_data und @st.cache_resource nutzen**:

```python
# Data Caching (für Funktions-Rückgabewerte)
@st.cache_data(ttl=3600, show_spinner=False)
def load_expensive_data():
    return expensive_computation()

# Resource Caching (für Singletons wie DB-Connections)
@st.cache_resource
def get_database_connection():
    return create_connection()

# Mit TTL (Time-To-Live)
@st.cache_data(ttl=60)  # Cache 60 Sekunden
def load_realtime_data():
    return fetch_from_api()

# Mit Hash-Funktion für Custom Objects
@st.cache_data(hash_funcs={MyClass: lambda obj: obj.id})
def process_custom_object(obj: MyClass):
    return obj.compute()
```

**Wichtig**:
- `@st.cache_data`: Für Daten (pickle-serializable)
- `@st.cache_resource`: Für Resources (nicht serializable)
- NIEMALS `@st.cache` verwenden (deprecated!)

### SQLAlchemy & Pydantic BaseModel (100+ Klassen)

**SQLAlchemy ORM Models** (class X(Base)):
- `controlling/models.py`: Team, Employee, Position, Criterion, PositionCriterion, PerformanceData, Report, EvaluationPeriod
- `core/security.py`: User, Role, Permission, AuthenticationSession, AuthenticationAuditLog, DataAccessLog, SecurityEvent
- `core/database.py`: AuditLog
- `core/form_manager.py`: FormDataModel, FormSnapshotModel, FormValidationModel
- `core/job_repository.py`: JobModel, JobResultModel
- `core/session_persistence.py`: SessionModel
- `core/session_repository.py`: SessionModel
- `core/widget_persistence.py`: WidgetStateModel
- `backend/models/database_models.py`: UniversalDatabaseModel

**Pydantic Schemas** (class X(BaseModel)):
- `backend/models/auth_schemas.py`: UserBase, UserUpdate, LoginRequest, TokenResponse, TokenRefreshRequest, PasswordChangeRequest, PasswordResetRequest, PasswordResetConfirm, SessionInfo, MessageResponse
- `backend/models/migration_schemas.py`: MigrationStartRequest, MigrationStartResponse, DataTypeProgress, MigrationProgressResponse, RollbackRequest, RollbackResponse, ValidationError, MigrationReportResponse, MigrationListItem, MigrationListResponse, ValidationRequest, ValidationCheck, ValidationResponse, CleanupRequest, CleanupResponse
- `backend/models/pdf_schemas.py`: PDFGenerationRequest, PDFPreviewRequest, PDFGenerationResponse, PDFStorageInfo, PDFListResponse, PDFTemplateInfo, PDFTemplatesResponse, PDFCacheStats, PDFDeleteResponse
- `backend/models/pricing_schemas.py`: PriceCalculationRequest, PriceCalculationResponse, MatrixCreateRequest, MatrixResponse, MatrixListResponse, MatrixFullResponse, MatrixUploadCSVRequest, MatrixUploadResponse, MatrixValidationResponse, MatrixExportCSVRequest, MatrixExportCSVResponse, AddRowRequest, AddColumnRequest, SetCellValueRequest, CRUDResponse, CacheStatsResponse

### Calculation Functions (100+ calculate_* Funktionen)

**Financial Calculations** (`financial_calculations.py`, `financial_tools.py`):
- `calculate_payback_years()` - Amortisationszeit
- `calculate_discount_amount()` - Rabatt-Berechnung
- `calculate_surcharge_amount()` - Aufschlag
- `calculate_vat_amount()` - MwSt-Berechnung
- `calculate_gross_from_net()` - Brutto aus Netto
- `calculate_net_from_gross()` - Netto aus Brutto
- `calculate_final_price()` - Endpreis mit allen Modifikatoren
- `calculate_annuity()` - Annuität für Kredite
- `calculate_leasing_costs()` - Leasing-Kosten
- `calculate_depreciation()` - Abschreibungen
- `calculate_financing_comparison()` - Finanzierungs-Vergleich
- `calculate_capital_gains_tax()` - Kapitalertragssteuer
- `calculate_contracting_costs()` - Contracting-Kosten

**Heatpump Calculations** (`heatpump_*.py`):
- `calculate_building_heat_load()` - Heizlast-Berechnung
- `calculate_heatpump_economics()` - Wirtschaftlichkeit
- `calculate_pv_self_consumption_heatpump()` - PV-Eigenverbrauch
- `calculate_beg_subsidy()` - BEG-Förderung
- `calculate_jaz_prognosis()` - JAZ-Prognose
- `calculate_buffer_tank_size()` - Pufferspeicher-Dimensionierung
- `calculate_price_scenarios()` - Preis-Szenarien
- `calculate_tax_benefits()` - Steuervorteile
- `calculate_noise_analysis()` - Lärmanalyse
- `calculate_smart_grid_benefits()` - Smart-Grid-Vorteile
- `calculate_grid_service_bonus()` - Netzdienlichkeits-Bonus
- `calculate_lifecycle_co2()` - Lebenszyklus-CO2
- `calculate_maintenance_schedule()` - Wartungsplan
- `calculate_insulation_upgrade()` - Dämmungs-Upgrade
- `calculate_window_upgrade()` - Fenster-Upgrade
- `calculate_subsidies()` - Förderungen
- `calculate_co2_footprint()` - CO2-Fußabdruck
- `calculate_hourly_electricity_costs()` - Stündliche Stromkosten
- `calculate_dynamic_tariff_comparison()` - Dynamischer Tarif-Vergleich
- `calculate_stromcloud_economics()` - Stromcloud-Wirtschaftlichkeit
- `calculate_smart_home_benefits()` - Smart-Home-Vorteile

**PV & 3D Calculations** (`pv3d.py`, `calculations.py`):
- `calculate_shading_for_module()` - Verschattungs-Analyse
- `calculate_sun_position()` - Sonnenstand
- `calculate_z_position()` - Z-Position für 3D-Module
- `calculate_module_grid()` - Modul-Grid-Platzierung

**Pricing Calculations** (`dynamic_pricing_engine.py`, `excel_product_pricing.py`):
- `calculate_dynamic_total_price()` - Dynamischer Gesamtpreis
- `calculate_hardware_pricing()` - Hardware-Preise
- `calculate_services_pricing_dynamic()` - Service-Preise
- `calculate_accessories_pricing()` - Zubehör-Preise
- `calculate_price_adjustments()` - Preis-Anpassungen
- `calculate_product_price_from_matrix()` - Matrix-basierte Preise
- `calculate_product_price_for_product()` - Produkt-spezifische Preise
- `calculate_special_products_cost()` - Spezialprodukte
- `calculate_services_cost()` - Service-Kosten
- `calculate_extras_cost()` - Extras-Kosten
- `calculate_all_extras()` - Alle Extras kombiniert

**Heating Calculations** (`heating_cost_calculator.py`, `heiz_calc.py`):
- `calculate_heating_costs()` - Heizkosten
- `calculate_heatpump_savings()` - Wärmepumpen-Einsparungen
- `calculate_heat_load_kw()` - Heizlast in kW

**Payment & Financing** (`payment_terms.py`):
- `compute_payment_schedule()` - Zahlungsplan
- `calculate_comprehensive_payment()` - Umfassende Zahlung

**Analysis Utils** (`analysis_utils.py`):
- `calculate_percentage_change()` - Prozentuale Änderung
- `calculate_compound_growth()` - Zinseszins-Wachstum
- `calculate_present_value()` - Barwert

### Test Suite (789 Test-Dateien!)

**Hauptkategorien**:
- **CRM Tests** (50+ Dateien): `test_crm_*.py`, `test_customer_*.py`, `test_contract_*.py`
- **Controlling Tests** (20+ Dateien): `test_controlling_*.py`, `test_team_*.py`, `test_performance_*.py`
- **PDF Tests** (30+ Dateien): `test_pdf_*.py`, `test_multi_pdf_*.py`
- **3D Tests** (15+ Dateien): `test_3d_*.py`, `test_collision_*.py`, `test_module_placement_*.py`
- **Heatpump Tests** (10+ Dateien): `test_heatpump_*.py`, `test_heating_*.py`
- **Admin Tests** (25+ Dateien): `test_admin_*.py`, `test_security_*.py`
- **Chart Tests** (10+ Dateien): `test_chart_*.py`, `test_visualization_*.py`
- **Integration Tests** (30+ Dateien): `test_integration_*.py`, `test_workflow_*.py`
- **Backend Tests** (100+ Dateien): `backend/tests/test_*.py`

**Wichtige Test-Patterns**:
```python
# pytest Fixtures
@pytest.fixture
def db_connection():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()

# Parametrized Tests
@pytest.mark.parametrize("input,expected", [
    (10, 20),
    (20, 40),
])
def test_calculation(input, expected):
    assert calculate(input) == expected

# Performance Tests
@pytest.mark.performance
def test_pdf_generation_speed():
    start = time.time()
    generate_pdf()
    assert time.time() - start < 5.0
```

### Build & Deployment Scripts (9 BAT-Dateien)

**Build System**:
- `BUILD_COMPLETE.bat`: Vollständiger Build-Prozess
- `BUILD_EXE.bat`: Erstelle EXE mit PyInstaller
- `CREATE_FINAL_SETUP.bat`: Inno Setup für Installer
- `TEST_EXE.bat`: Test der erstellten EXE

**Start Scripts**:
- `ARSCHIBALD_STARTEN.bat`: Hauptstart-Script
- `Start_ARSCHIBALD.bat`: Alternative Starter
- `Start_Ömers All in One Dingsbums.bat`: Legacy-Starter
- `OemersBokuk4all_Launcher.bat`: Launcher-Variante

**Utilities**:
- `VIDEO_KONVERTIEREN.bat`: Video-Konvertierung für Intro

**Pattern**:
```batch
@echo off
REM Automatischer Build mit Fehlerbehandlung

echo Starte Build-Prozess...

REM Umgebung prüfen
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python nicht gefunden!
    pause
    exit /b 1
)

REM PyInstaller ausführen
pyinstaller --clean --noconfirm ARSCHIBALD_COMPLETE.spec
if errorlevel 1 (
    echo FEHLER beim Build!
    pause
    exit /b 1
)

echo Build erfolgreich!
pause
```

### YAML/JSON Configuration Files

**YAML-Dateien** (94 Dateien):
- **PDF Koordinaten** (70+ Dateien):
  - `coords/seite1.yml` bis `seite8.yml` - Single-PDF Koordinaten
  - `coords_multi/seite{N}_f{X}.yml` - Multi-Firma Koordinaten (f1-f8, Seite 1-8)
  - `coords_wp/wp_seite1.yml` bis `wp_seite8.yml` - Wärmepumpen-PDFs
  
- **GitHub Workflows** (7 Dateien in `solar-calculator-pro/.github/workflows/`):
  - `ci.yml`, `ci-cd.yml` - CI/CD Pipeline
  - `build.yml` - Build-Automation
  - `security.yml` - Security-Scans
  - `performance.yml` - Performance-Tests
  - `release.yml` - Release-Automation

**JSON-Dateien** (1040+ Dateien):
- **Core Config**:
  - `de.json` - Deutsche Lokalisierung (3000+ Einträge)
  - `settings.json` - App-Einstellungen
  - `schema.json` - Datenbank-Schema
  - `.vscode/settings.json` - VS Code Config
  - `package.json` - NPM Dependencies
  
- **Data Files**:
  - `data/ui_effects_settings.json` - UI-Effekte
  - `waermepumpen_produkte_*.json` - Wärmepumpen-Katalog
  
- **Test Data** (20+ Dateien):
  - `tests/test_*_config.json` - Test-Konfigurationen
  - `tests/test_*_payload.json` - Test-Payloads
  
- **Theming** (20+ Dateien in `theming/themes/`):
  - `shadcn-default.json`, `shadcn-dark.json`
  - `shadcn-blue.json`, `shadcn-purple.json`, etc.
  
- **Backend** (100+ Dateien):
  - `solar-calculator-pro/frontend/tsconfig.json` - TypeScript Config
  - `solar-calculator-pro/frontend/components.json` - Component Registry
  - `solar-calculator-pro/backend/docs/postman_collection.json` - API Docs

### Markdown Documentation (2049+ MD-Dateien!)

**Hauptkategorien**:
- **Feature Docs** (500+ Dateien): `*_COMPLETE.md`, `*_IMPLEMENTATION*.md`
- **Reference Docs** (300+ Dateien): `*_REFERENCE.md`, `*_QUICK_REFERENCE.md`
- **Guides** (200+ Dateien): `*_GUIDE.md`, `*_ANLEITUNG.md`
- **Task Tracking** (100+ Dateien): `TASK_*_COMPLETE.md`
- **Backend Docs** (200+ Dateien): `backend/TASK_*.md`, `backend/docs/*.md`
- **Core Docs** (100+ Dateien): `core/*.md`
- **CRM Docs** (50+ Dateien): `crm/features/*.md`, `crm/utils/*.md`

**Wichtige Dokumentationen**:
- `BUILD_ANLEITUNG.md` - Build-Anleitung
- `AUSWERTUNGSPERIODEN_HANDBUCH.md` - Controlling-Handbuch
- `COMPLETE_PROJECT_ANALYSIS.md` - Projekt-Analyse
- `DEUTSCHE_FORMATIERUNG_DOKUMENTATION.md` - Formatierungs-Standard
- `3D_VISUALIZATION_TEST_ANLEITUNG.md` - 3D-Testing
- `Agent/DOCUMENTATION_INDEX.md` - Agent-Doku-Index

### Utils & Tools Verzeichnis (100+ Files)

**Haupt-Tools** (`nützliche tools/`):
- **50+ Nummerierte Tools** (`01_clean_imports.py` bis `50_wol.py`)
- **Code Quality**:
  - `cache_leerer.py` - Cache-Cleaner
  - `code_formatter.py` - Code-Formatierung
  - `dead_code_finder.py` - Toten Code finden
  - `dead_import_finder.py` - Ungenutzte Imports
  - `dependency_checker.py` - Dependency-Analyse
  - `import_bereiniger.py` - Import-Bereinigung
  
- **PDF Tools**:
  - `pdf_erstellen.py`, `pdf_erstellen_komplett.py` - PDF-Erstellung
  - `pdf_zu_markdown.py` - PDF → Markdown Converter
  - `pdf_zu_png.py` - PDF → PNG Converter
  - `txt_based_pdf_generator.py` - Text-basierte PDF-Gen
  
- **Security**:
  - `secret_scanner.py` - Secret-Detection
  - `scan_malware.py` - Malware-Scanner
  - `quantum_cryptographic_vault.py` - Krypto-Vault
  - `steganography_code_injector.py` - Steganographie
  
- **Analysis**:
  - `behavioral_analysis_engine.py` - Benutzerverhalten
  - `deep_code_archaelogist.py` - Code-Archäologie
  - `log_analyzer.py` - Log-Analyse
  - `performance_profiler.py` - Performance-Profiling
  
- **Database**:
  - `datenbank_bereiniger.py` - DB-Cleaning
  - `backup_manager.py` - Backup-Verwaltung
  
- **Automation**:
  - `docker_helper.py` - Docker-Automation
  - `master_optimierer.py` - Master-Optimizer
  - `python_tool_generator.py` - Tool-Generator
  - `neural_code_mutator.py` - Code-Mutation
  - `test_runner.py` - Test-Automation

**Utils-Dateien** (`utils/`):
- **3D-System** (15+ Dateien):
  - `pv3d.py`, `pv3d_plotly.py` - 3D-Engines
  - `pv3d_module_placement_ui.py` - Modul-Platzierung
  - `pv3d_export.py`, `pv3d_export_buttons.py` - Export
  - `pv3d_performance.py`, `pv3d_optimization.py` - Optimierung
  - `pv3d_mounting_logic.py` - Montage-Logik
  - `pv3d_grid_calculator.py` - Grid-Berechnungen
  
- **PDF-Utils**:
  - `pdf_visual_inject.py` - Visual-Injection
  - `export_coords.py` - Koordinaten-Export
  
- **UI-Helpers**:
  - `shadcn_sidebar.py` - Sidebar-Komponente
  - `shadcn_migration_helpers.py` - Migration-Helpers
  - `solar_animation.py` - Animationen

### Config & Settings Files (79 Dateien)

**Config-Module**:
- `core/config.py` (800+ Zeilen) - Haupt-Konfig mit 7 @dataclass
- `core/logging_config.py` - Logging-Konfiguration
- `Agent/config.py` - Agent-Konfiguration
- `backend/core/config.py` - Backend-Config
- `controlling/pdf_config.py` - PDF-Config für Controlling
- `solar-calculator-pro/backend/config.py` - Solar-Calculator Backend

**Settings-Module**:
- `admin_controlling_settings_ui.py` - Controlling-Settings-UI
- `admin_pdf_settings_ui.py` - PDF-Settings-UI
- `admin_heatpump_settings_ui.py` - Wärmepumpen-Settings
- `admin_intro_settings_ui.py` - Intro-Settings
- `admin_ui_effects_settings.py` - UI-Effekte-Settings
- `admin_heating_costs_config_ui.py` - Heizkosten-Config
- `ui_settings_handler.py` - Settings-Handler
- `components/progress_settings.py` - Progress-Settings

**Backend Config Services**:
- `backend/services/configuration_service.py` - Konfig-Service
- `backend/services/pdf_configuration_service.py` - PDF-Konfig
- `backend/services/system_config_service.py` - System-Konfig
- `backend/services/system_settings_service.py` - System-Settings

**Patterns**:
```python
# Config mit Environment-Variablen
from core.config import AppConfig

config = AppConfig.from_env()
if config.debug:
    enable_debug_mode()

# Settings mit Streamlit UI
def render_settings_ui():
    st.header("Einstellungen")
    
    # Lade aktuelle Settings
    settings = load_settings()
    
    # UI für Änderungen
    new_value = st.text_input("Setting", value=settings.get('key'))
    
    if st.button("Speichern"):
        save_settings({'key': new_value})
        st.success("Gespeichert!")
```

---

## Complete Module Reference

### Alle 26 Engine-Dateien
**Gefunden via `file_search(*_engine.py)`**:

1. **dynamic_pricing_engine.py**: Dynamische Echtzeit-Preisanpassungen
2. **product_rotation_engine.py**: Multi-Firma Produkt-Variation
3. **price_modification_engine.py**: Basis-Preismodifikation (+15% etc.)
4. **statistics_engine.py**: Statistische Analysen
5. **live_calculation_engine.py**: Live-Berechnungen während Eingabe
6. **pricing/enhanced_pricing_engine.py**: Erweiterte Preislogik mit Matrix
7. **pricing/pricing_modification_engine.py**: Pricing-Modifikationen
8. **pricing/combined_pricing_engine.py**: Multi-Modifier Kombination
9. **pricing/calculate_per_engine.py**: "Berechnen pro" (Stück/Meter/kWp)
10. **pricing/pv_pricing_engine.py**: PV-System Gesamt-Preisberechnung
11. **excel/excel_formula_engine.py**: Excel-Formel-Interpreter
12. **crm/features/forecasting_engine.py**: Umsatz-Prognosen
13. **crm/features/reporting_engine.py**: Report-Generierung
14. **backend/services/formula_engine.py**: Formel-Parsing für Backend
15. **core/cache_warming.py** → `CacheWarmingEngine`: Cache-Preloading
16. **core/cache_invalidation.py** → `InvalidationEngine`: Cache-Invalidierung
17. **core/session_persistence.py** → `SessionPersistenceEngine`: Session-Wiederherstellung
18. **core/widget_persistence.py** → `WidgetPersistenceEngine`: Widget-State-Persistenz
19. **core/widget_validation.py** → `ValidationEngine`: Widget-Validierung
20. **backend/core/pdf_bytes.py** → `PDFRenderingEngine`: PDF zu Bytes Konvertierung
21. **backend/tests/test_analytics_engine.py**: Analytics-Engine Tests
22. **backend/tests/test_formula_engine.py**: Formel-Engine Tests
23. **backend/tests/test_pricing_modification_engine.py**: Pricing-Mod Tests
24. **backend/tests/test_pv_pricing_engine.py**: PV-Pricing Tests
25. **nützliche tools/behavioral_analysis_engine.py**: Benutzerverhalten-Analyse
26. **controlling/analytics.py** → `AnalyticsEngine`: Employee-Performance-Analyse

### Alle 8 Handler-Dateien
**Gefunden via `file_search(*_handler.py)`**:

1. **price_matrix_error_handler.py**: Fehlerbehandlung für Preis-Matrizen
2. **verify_task2_placement_handler.py**: 3D-Platzierungs-Verifizierung
3. **utils/pv3d_placement_handler.py**: PV-Modul 3D-Platzierung
4. **ui_settings_handler.py**: UI-Einstellungen Handler
5. **theming/error_handler.py**: Theme-System Fehlerbehandlung
6. **performance_handler.py**: Performance-Monitoring
7. **backend/middleware/error_handler.py**: FastAPI Error Middleware
8. **components/progress_manager.py** → Handler-Pattern für Progress

### Alle 76 Manager-Dateien
**Top 20 Wichtigste** (aus 76 gefunden):

1. **password_manager.py**: Passwort-Verwaltung
2. **theme_manager.py**: Theme-System
3. **ui_state_manager.py**: UI-State-Verwaltung
4. **theming/security_manager.py**: Theme-Security
5. **theming/state_manager.py**: Theme-State
6. **theming/hot_reload_manager.py**: Hot-Reload für Themes
7. **pricing/dynamic_key_manager.py**: Dynamische Key-Generierung
8. **pricing/profit_margin_manager.py**: Gewinnmargen
9. **pricing/vat_manager.py**: MwSt-Verwaltung
10. **excel/excel_manager.py**: Excel-Integration
11. **core/connection_manager.py**: DB Connection Pooling + Failover
12. **core/session_manager.py**: Session-Verwaltung
13. **core/migration_manager.py**: Migration-System
14. **core/form_manager.py**: Form-Validation (1620 Zeilen)
15. **core/jobs.py** → `JobManager`: Background Jobs
16. **crm/utils/notification_manager.py**: CRM-Benachrichtigungen
17. **crm/utils/import_export_manager.py**: CRM Import/Export
18. **crm/features/feedback_manager.py**: Feedback-System
19. **crm/features/email_manager.py**: E-Mail-Integration
20. **crm/features/note_manager.py**: Notizen-Verwaltung

Vollständige Liste inkl.:
- `controlling/team_manager.py`: Team-Hierarchien
- `controlling/period_manager.py`: Auswertungsperioden
- `controlling/notifications.py` → `NotificationManager`
- `controlling/pdf_config.py` → `PDFConfigManager`
- `components/progress_manager.py` → `ProgressManager`
- `crm/features/knowledge_base.py` → `KnowledgeBaseManager`
- `crm/features/dashboard_widgets.py` → `WidgetManager`
- `backend/migrations/migration_manager.py`
- `backend/core/security_manager.py` → `SecurityManager`
- `backend/core/websocket_manager.py` → `WebSocketManager`
- **+56 weitere Manager-Dateien**

### Alle 100+ Manager/Engine/Handler Klassen
**Gefunden via grep "^class.*Engine|Manager|Handler"**:

**Security**:
- `SecurityManager` (backend/core/security_manager.py)
- `AuthenticationManager` (core/security.py)
- `AuthorizationManager` (core/security.py)
- `MFAManager` (core/security.py)
- `SessionManager` (core/security.py)
- `DataProtectionManager` (core/security.py)
- `ThemeSecurityManager` (.kiro/specs)

**Database & Migrations**:
- `DatabaseManager` (core/database.py)
- `MigrationManager` (core/migrations.py, core/migration_manager.py)
- `DatabaseFailoverManager` (core/connection_manager.py)
- `EnhancedConnectionManager` (core/connection_manager.py)

**Forms & Validation**:
- `FormManager` (core/form_manager.py - 1620 Zeilen)
- `ValidationEngine` (core/widget_validation.py)
- `WidgetPersistenceEngine` (core/widget_persistence.py)

**Jobs & Background Tasks**:
- `JobManager` (core/jobs.py)
- `JobNotificationManager` (core/job_notifications.py)
- `BackgroundTaskManager` (background_tasks.py)

**Caching**:
- `CacheWarmingEngine` (core/cache_warming.py)
- `InvalidationEngine` (core/cache_invalidation.py)

**Logging**:
- `LoggingConfigManager` (core/logging_config.py)

**Pricing**:
- `EnhancedPricingEngine` (calculations.py)
- `PricingEngine` (.kiro/specs)
- `DynamicKeyManager` (pricing/)
- `CalculatePerEngine` (pricing/)
- `ProfitMarginManager` (pricing/)
- `PricingModificationEngine` (pricing/)

**Controlling**:
- `EmployeeManager` (controlling/managers.py)
- `PositionManager` (controlling/managers.py)
- `CriterionManager` (controlling/managers.py)
- `PerformanceDataManager` (controlling/managers.py)
- `AnalyticsEngine` (controlling/analytics.py)
- `TeamManager` (controlling/team_manager.py)
- `PeriodManager` (controlling/period_manager.py)
- `NotificationManager` (controlling/notifications.py)
- `PDFConfigManager` (controlling/pdf_config.py)

**CRM**:
- `KnowledgeBaseManager` (crm/features/knowledge_base.py)
- `WidgetManager` (crm/features/dashboard_widgets.py)
- `NotificationManager` (crm/utils/notification_manager.py)

**Excel**:
- `ExcelManager` (excel/excel_manager.py)
- `FormulaEngine` (excel/excel_formula_engine.py)
- `BatchOperationManager` (excel/excel_batch_operations.py)

**PDF**:
- `PDFRenderingEngine` (backend/core/pdf_bytes.py)
- `PDFConfigManager` (controlling/pdf_config.py)

**Theming**:
- `ThemeManager` (theme_manager.py, theming/theme_manager.py)
- `HotReloadManager` (theming/hot_reload_manager.py)
- `ThemeStateManager` (.kiro/specs)
- `ErrorHandler` (theming/error_handler.py)

**Session**:
- `SessionManager` (core/session_manager.py, core/security.py)
- `SessionPersistenceEngine` (core/session_persistence.py)

**Components**:
- `ProgressManager` (components/progress_manager.py)
- `CSSTemplateManager` (css_template_manager.py)

**Backend**:
- `WebSocketManager` (backend/core/websocket_manager.py)
- `BackendProcessManager` (backend/tests/)
- `UpdateManager` (.kiro/specs)
- `EmojiManager` (.kiro/specs)

**+50 weitere Klassen** in Tests, Specs, und Backup-Ordnern

### Alle 150+ render_* Funktionen
**Gefunden via grep "^def render_"**:

**Core UI Functions**:
- `render_protected_admin_section()` - Admin-Bereiche mit Passwort
- `render_live_cost_preview()` - Live-Kosten-Vorschau (gui.py)
- `render_intro_screen()` - Intro mit Video
- `render_registration_form()` - Registration-Form

**Controlling (controlling_ui.py - 2798 Zeilen)**:
- `render_controlling_page()` - Haupt-Controlling-Seite
- `render_performance_entry_tab()` - Datenerfassung
- `render_report_generation_tab()` - Report-Generierung
- `render_report_dashboard()` - Report-Dashboard
- `render_archive_tab()` - Archiv
- `render_team_analysis_tab()` - Team-Analysen
- `render_comparison_tab()` - Vergleiche
- `render_ranking_tab()` - Rankings
- `render_pdf_color_settings()` - PDF-Farben

**Wärmepumpen (heatpump_ui.py - 5000+ Zeilen)**:
- `render_heatpump_analysis()` - Haupt-Analyse
- `render_building_analysis()` - Gebäude-Analyse
- `render_heatpump_selection()` - WP-Auswahl
- `render_radiator_check()` - Heizkörper-Check
- `render_economics_analysis()` - Wirtschaftlichkeit
- `render_pv_integration()` - PV-Integration
- `render_results_summary()` - Ergebnis-Zusammenfassung
- `render_3d_building_animation()` - 3D-Animation
- `render_renovation_planner()` - Sanierungs-Planer
- `render_optimization_tools()` - Optimierungs-Tools
- `render_subsidy_co2()` - Förderung & CO2
- `render_roi_benchmarking()` - ROI-Vergleich
- `render_heatpump()` - Main Entry Point
- `render_dynamic_tariff_tab()` - Dynamische Tarife
- `render_advanced_analysis()` - Erweiterte Analysen

**Excel (excel_grid_ui.py, excel_product_pricing_ui.py)**:
- `render_excel_grid_ui()` - Excel-Grid
- `render_price_matrix_tab()` - Preis-Matrix
- `render_product_price_config_ui()` - Produkt-Preis-Konfig
- `render_product_price_config_inline()` - Inline-Konfig

**3D Visualization**:
- `render_3d_view()` - 3D-Ansicht (solar_3d_view_module.py, pv3d.py)
- `render_image_bytes()` - Image zu Bytes (pv3d.py)
- `render_modules_lod()` - Level-of-Detail für Module
- `render_module_placement_panel()` - Modul-Platzierung
- `render_export_action_buttons()` - Export-Buttons

**PV Visuals (pv_visuals.py)**:
- `render_yearly_production_pv_data()` - Jahresproduktion
- `render_break_even_pv_data()` - Break-Even
- `render_amortisation_pv_data()` - Amortisation
- `render_co2_savings_visualization()` - CO2-Einsparungen

**PDF System (repair_pdf/**, pdf_*.py)**:
- `render_pdf_ui()` - PDF-Haupt-UI
- `render_pdf_preview_interface()` - PDF-Vorschau
- `render_pdf_theme_manager()` - PDF-Theme
- `render_pdf_structure_manager()` - PDF-Struktur
- `render_pdf_debug_section()` - PDF-Debug
- `render_central_pdf_ui()` - Zentrale PDF-UI
- `render_multi_offer_generator()` - Multi-Angebots-Generator

**Analysis (repair_pdf/analysis.py - 8800+ Zeilen!)**:
- `render_analysis()` - Haupt-Analyse
- `render_pricing_modifications_ui()` - Preis-Modifikationen
- `render_daily_production_switcher()` - Tages-Produktion
- `render_tariff_cube_switcher()` - Tarif-Würfel
- `render_weekly_production_switcher()` - Wochen-Produktion
- `render_yearly_production_switcher()` - Jahres-Produktion
- `render_project_roi_matrix_switcher()` - ROI-Matrix
- `render_feed_in_revenue_switcher()` - Einspeise-Erlös
- `render_production_vs_consumption_switcher()` - Produktion vs Verbrauch
- `render_co2_savings_value_switcher()` - CO2-Einsparungen
- `render_investment_value_switcher()` - Investitionswert
- `render_storage_effect_switcher()` - Speicher-Effekt
- `render_selfuse_stack_switcher()` - Eigenverbrauch-Stack
- `render_cost_growth_switcher()` - Kosten-Wachstum
- `render_selfuse_ratio_switcher()` - Eigenverbrauchs-Quote
- `render_roi_comparison_switcher()` - ROI-Vergleich
- `render_scenario_comparison_switcher()` - Szenario-Vergleich
- `render_tariff_comparison_switcher()` - Tarif-Vergleich
- `render_income_projection_switcher()` - Einkommens-Projektion
- `render_advanced_economics()` - Erweiterte Wirtschaftlichkeit
- `render_detailed_energy_analysis()` - Detaillierte Energie-Analyse
- `render_technical_calculations()` - Technische Berechnungen
- `render_financial_scenarios()` - Finanz-Szenarien
- `render_environmental_calculations()` - Umwelt-Berechnungen
- `render_optimization_suggestions()` - Optimierungs-Vorschläge
- `render_financing_analysis()` - Finanzierungs-Analyse
- `render_advanced_calculations_section()` - Erweiterte Berechnungen
- `render_advanced_financial_analysis()` - Erweiterte Finanz-Analyse
- `render_advanced_energy_analysis()` - Erweiterte Energie-Analyse
- `render_advanced_environmental_analysis()` - Erweiterte Umwelt-Analyse
- `render_advanced_technical_analysis()` - Erweiterte Technik-Analyse
- `render_advanced_comparison_analysis()` - Erweiterte Vergleichs-Analyse

**Admin Panel (repair_pdf/admin_panel.py)**:
- `render_admin_panel()` - Haupt-Admin-Panel
- `render_company_crud_tab()` - Firmen-CRUD
- `render_product_management()` - Produkt-Verwaltung
- `render_general_settings_extended()` - Allgemeine Einstellungen
- `render_price_matrix()` - Preis-Matrix
- `render_tariff_management()` - Tarif-Verwaltung
- `render_visualization_settings()` - Visualisierungs-Einstellungen
- `render_advanced_settings()` - Erweiterte Einstellungen
- `render_pdf_design_settings()` - PDF-Design
- `render_api_key_settings()` - API-Keys
- `render_company_text_templates_tab()` - Firmen-Text-Templates
- `render_company_image_templates_tab()` - Firmen-Bild-Templates

**Weitere wichtige render_ Funktionen**:
- `render_info_platform()` - Info-Plattform
- `render_heating_calculator()` - Heizungs-Rechner
- `render_financial_tools_section()` - Finanz-Tools
- `render_quick_calc()` - Schnell-Rechner
- `render_options()` - Optionen
- `render_services_selection()` - Dienstleistungs-Auswahl
- `render_job_queue_widget()` - Job-Queue-Widget
- `render_job_card()` - Job-Karte
- `render_job_submission_form()` - Job-Formular
- `render_job_tracker()` - Job-Tracker
- `render_job_manager_admin()` - Job-Manager-Admin
- `render_logo_position_settings()` - Logo-Positionen
- `render_logo_upload_section()` - Logo-Upload
- `render_logo_management_section()` - Logo-Verwaltung
- `render_logo_edit_section()` - Logo-Bearbeitung
- `render_logo_statistics_section()` - Logo-Statistiken
- `render_help_sidebar()` - Hilfe-Sidebar
- `render_mounting_calculation_summary()` - Unterkonstruktions-Zusammenfassung
- `render_pv_mounting_selection()` - PV-Unterkonstruktions-Auswahl
- `render_solar_calculator_with_shadcn()` - Solar-Rechner mit Shadcn
- `render_service_display_config()` - Service-Display-Konfig
- `render_all_selected_charts_to_pdf()` - Charts zu PDF
- `render_financial_tools_to_pdf()` - Finanz-Tools zu PDF

**+50 weitere render_ Funktionen** in Specs, Tests, und Backup-Ordnern

### Vollständiges Datenbank-Schema
**26 CREATE TABLE Statements gefunden in database.py**:

```sql
-- Core System
CREATE TABLE IF NOT EXISTS admin_settings (...)
CREATE TABLE IF NOT EXISTS products (...)
CREATE TABLE IF NOT EXISTS companies (...)
CREATE TABLE IF NOT EXISTS company_documents (...)
CREATE TABLE IF NOT EXISTS pdf_templates (...)
CREATE TABLE IF NOT EXISTS company_text_templates (...)
CREATE TABLE IF NOT EXISTS company_image_templates (...)

-- CRM System
CREATE TABLE IF NOT EXISTS crm_customers (...)
CREATE TABLE IF NOT EXISTS crm_tasks (...)
CREATE TABLE IF NOT EXISTS crm_activities (...)
CREATE TABLE IF NOT EXISTS crm_reminders (...)
CREATE TABLE IF NOT EXISTS crm_tags (...)
CREATE TABLE IF NOT EXISTS customer_tags (...)
CREATE TABLE IF NOT EXISTS customer_documents (...)
CREATE TABLE IF NOT EXISTS project_calculations (...)

-- Dashboard & Analytics
CREATE TABLE IF NOT EXISTS user_dashboard_settings (...)
CREATE TABLE IF NOT EXISTS sales_targets (...)
CREATE TABLE IF NOT EXISTS sales_forecasts (...)

-- Knowledge Base
CREATE TABLE IF NOT EXISTS kb_categories (...)
CREATE TABLE IF NOT EXISTS kb_articles (...)
CREATE TABLE IF NOT EXISTS kb_ratings (...)

-- Heat Pumps
CREATE TABLE IF NOT EXISTS heat_pumps (...)
```

**SQLAlchemy Models** (controlling/models.py):
- `Employee`, `Position`, `Criterion`, `PerformanceData`
- `EvaluationPeriod`, `Team`, `Report`
- Alle mit `str`-basierten Enums für Pickle-Serialisierung

### FastAPI Backend API Endpoints
**160+ API-Dateien gefunden in backend/api/v1/**:

**Core APIs**:
- `auth_advanced.py`: Advanced Authentication
- `admin_dashboard.py`: Admin-Dashboard
- `application_monitoring.py`: App-Monitoring
- `audit.py`: Audit-Trail
- `backup_recovery.py`, `backup.py`: Backup-System
- `background_jobs.py`: Background Jobs API

**Database**:
- `database.py`, `database_management.py`: DB-Management
- `database_backup.py`: DB-Backup
- `database_optimization.py`: DB-Optimierung
- `database_production.py`: Production-DB
- `database_type.py`: DB-Type-Handling
- `data_migration.py`: Data-Migration
- `data_privacy.py`: Datenschutz

**PV/WP System**:
- `battery_storage.py`, `battery.py`: Batterie-Speicher
- `building_geometry.py`: Gebäude-Geometrie
- `combined_system.py`: Kombinierte Systeme
- `calculation_functions.py`: Berechnungs-Funktionen
- `catalog.py`: Produkt-Katalog

**PDF**:
- `batch_pdf.py`: Batch-PDF-Generierung
- `extended_pv_pdf.py`: Erweiterte PV-PDFs
- `extended_offer_pdf.py`: Erweiterte Angebots-PDFs
- `extended_wp_pdf.py`: Erweiterte WP-PDFs

**CRM**:
- `crm_advanced.py`: Erweiterte CRM-Features
- `crm_dashboard.py`: CRM-Dashboard
- `contract_warranty.py`: Verträge & Garantien
- `contracts.py`: Vertrags-Management
- `customer_data.py`: Kundendaten

**3D**:
- `animation_3d.py`: 3D-Animationen
- `collision_detection.py`: Kollisionserkennung
- `export_3d.py`: 3D-Export

**Utilities**:
- `advanced_charts.py`: Erweiterte Charts
- `additional_components.py`, `additional_features.py`: Zusatz-Features
- `caching_system.py`: Caching
- `component_toggles.py`: Feature-Toggles
- `currency.py`: Währungs-Konvertierung
- `encryption.py`: Verschlüsselung
- `exports.py`: Export-Funktionen
- `environment_config.py`: Umgebungs-Konfiguration
- `deployment_automation.py`: Deployment-Automation

**Companies**:
- `companies.py`, `company_management.py`: Firmen-Verwaltung
- `branding.py`: Branding-Management

**Documents**:
- `documents.py`: Dokumenten-Verwaltung

**Energy**:
- `energy_flow_visualization.py`: Energie-Fluss-Visualisierung

**+100 weitere API-Endpoints**

### Components Verzeichnis
**45 Dateien in components/**:

**Shadcn-UI Components**:
- `shadcn_ui_integration.py` (1290 Zeilen) - Haupt-Integration
- `accordion.py`, `alert.py`, `badge.py` - UI-Komponenten
- `breadcrumb.py`, `card.py`, `dropdown.py` - Navigation
- `form_components.py`, `forms.css` - Forms
- `metric_card.py` - Metriken
- `pagination.py`, `popover.py`, `progress.py` - Interaktive Elemente
- `skeleton.py`, `table.py` - Layout

**React Components** (TSX):
- `CalculationProgress.tsx` - Berechnungs-Fortschritt
- `CustomerForm.tsx`, `ProjectForm.tsx` - Formulare
- `ModernSolarCalculator.tsx`, `ModernSolarCalculator.css` - Solar-Rechner

**Manager & Settings**:
- `progress_manager.py` - Progress-Verwaltung
- `progress_settings.py` - Progress-Einstellungen
- `progress_demo.py` - Demo

**Documentation**:
- 12+ Markdown-Dateien mit QUICK_REFERENCE, REFERENCE, USAGE_EXAMPLE
- Für jede Komponente: Alert, Badge, Card, Extended Components, Form Components, Metric Card, Table

### .streamlit Konfiguration
**3 Dateien in .streamlit/**:
- `config.toml` - Streamlit-Konfiguration
- `secrets.toml` - API-Keys & Secrets
- `static/` - Statische Assets

**config.toml Struktur**:
```toml
[server]
port = 8501
headless = false
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
serverAddress = "localhost"

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"

[runner]
magicEnabled = true
installTracer = false
fixMatplotlib = true
```

## Advanced Patterns & Code Architecture

### @dataclass Usage Patterns (100+ Verwendungen)
**Kritische Dataclasses** für Streamlit Session State (pickle-serializable):

**Core System**:
- `core/config.py`: 7 @dataclass (AppConfig, DatabaseConfig, CacheConfig, LoggingConfig, SecurityConfig, SessionConfig, AppConfigValidator)
- `core/session.py`: 4 @dataclass (UserSession, FormState, NavigationEntry, FormSnapshot)
- `core/router.py`: 2 @dataclass (NavigationEvent, RouteConfig)
- `core/navigation_history.py`: 2 @dataclass (NavigationEntry, NavigationState)
- `core/jobs.py`: 2 @dataclass (Job, JobResult)
- `core/form_manager.py`: 3 @dataclass (FormState, ValidationResult, FormSnapshot)
- `core/cache.py`, `core/cache_monitoring.py`: 3 @dataclass (CacheEntry, CacheStats, InvalidationRule)
- `core/connection_manager.py`: 4 @dataclass (ConnectionConfig, ConnectionPool, ConnectionMetrics, FailoverStrategy)
- `core/dependency_injection.py`: 1 @dataclass (ServiceDescriptor)
- `core/db_performance.py`: 2 @dataclass (QueryMetrics, OptimizationHint)

**Controlling**:
- `controlling/notifications.py`: 2 @dataclass (Notification, NotificationTemplate)
- `controlling/pdf_config.py`: 1 @dataclass (PDFColorSettings)
- `controlling/position_criteria.py`: 1 @dataclass (CriterionWeight)

**Excel & Pricing**:
- `excel/excel_models.py`: 8 @dataclass (ExcelCell, ExcelRow, ExcelSheet, ExcelWorkbook, CellFormat, ValidationRule, Formula, ConditionalFormat)
- `excel/excel_lazy_loader.py`: 2 @dataclass (LoadState, CellData)
- `excel/excel_product_pricing.py`: 1 @dataclass (PricingConfig)
- `excel/custom_dynamic_calculation.py`: 1 @dataclass (CalculationContext)
- `financial_calculations.py`: 1 @dataclass (PriceBreakdown - frozen=True für Immutability)
- `heatpump_pricing.py`: 1 @dataclass (HeatPumpPricingConfig)

**Backend Services**:
- `backend/services/migration_service.py`: 2 @dataclass (MigrationTask, MigrationResult)
- `backend/services/dropdown_key_service.py`: 2 @dataclass (DropdownKey, DropdownConfig)
- `backend/services/calculation_result_key_service.py`: 2 @dataclass (CalculationKey, KeyMetadata)

**Testing & Monitoring**:
- `app_health_monitor.py`: 1 @dataclass (HealthStatus)
- `app_diagnostics.py`: 1 @dataclass (DiagnosticResult)
- `background_tasks.py`: 1 @dataclass (TaskConfig)
- `components/progress_manager.py`: 1 @dataclass (ProgressState)

**WICHTIG für Session State**:
```python
# ALLE @dataclass MÜSSEN pickle-serializable sein!
@dataclass
class MyData:
    # Automatisch serializable wenn alle Felder pickle-serializable sind
    value: int
    name: str
    items: list[str]
    
    # Für komplexe Typen: Explicit Pickle Support
    def __getstate__(self):
        return self.__dict__.copy()
    
    def __setstate__(self, state):
        self.__dict__.update(state)
```

### Streamlit Caching Patterns (49 Verwendungen)
**@st.cache_data und @st.cache_resource nutzen**:

```python
# Data Caching (für Funktions-Rückgabewerte)
@st.cache_data(ttl=3600, show_spinner=False)
def load_expensive_data():
    return expensive_computation()

# Resource Caching (für Singletons wie DB-Connections)
@st.cache_resource
def get_database_connection():
    return create_connection()

# Mit TTL (Time-To-Live)
@st.cache_data(ttl=60)  # Cache 60 Sekunden
def load_realtime_data():
    return fetch_from_api()

# Mit Hash-Funktion für Custom Objects
@st.cache_data(hash_funcs={MyClass: lambda obj: obj.id})
def process_custom_object(obj: MyClass):
    return obj.compute()
```

**Wichtig**:
- `@st.cache_data`: Für Daten (pickle-serializable)
- `@st.cache_resource`: Für Resources (nicht serializable)
- NIEMALS `@st.cache` verwenden (deprecated!)

### SQLAlchemy & Pydantic BaseModel (100+ Klassen)

**SQLAlchemy ORM Models** (class X(Base)):
- `controlling/models.py`: Team, Employee, Position, Criterion, PositionCriterion, PerformanceData, Report, EvaluationPeriod
- `core/security.py`: User, Role, Permission, AuthenticationSession, AuthenticationAuditLog, DataAccessLog, SecurityEvent
- `core/database.py`: AuditLog
- `core/form_manager.py`: FormDataModel, FormSnapshotModel, FormValidationModel
- `core/job_repository.py`: JobModel, JobResultModel
- `core/session_persistence.py`: SessionModel
- `core/session_repository.py`: SessionModel
- `core/widget_persistence.py`: WidgetStateModel
- `backend/models/database_models.py`: UniversalDatabaseModel

**Pydantic Schemas** (class X(BaseModel)):
- `backend/models/auth_schemas.py`: UserBase, UserUpdate, LoginRequest, TokenResponse, TokenRefreshRequest, PasswordChangeRequest, PasswordResetRequest, PasswordResetConfirm, SessionInfo, MessageResponse
- `backend/models/migration_schemas.py`: MigrationStartRequest, MigrationStartResponse, DataTypeProgress, MigrationProgressResponse, RollbackRequest, RollbackResponse, ValidationError, MigrationReportResponse, MigrationListItem, MigrationListResponse, ValidationRequest, ValidationCheck, ValidationResponse, CleanupRequest, CleanupResponse
- `backend/models/pdf_schemas.py`: PDFGenerationRequest, PDFPreviewRequest, PDFGenerationResponse, PDFStorageInfo, PDFListResponse, PDFTemplateInfo, PDFTemplatesResponse, PDFCacheStats, PDFDeleteResponse
- `backend/models/pricing_schemas.py`: PriceCalculationRequest, PriceCalculationResponse, MatrixCreateRequest, MatrixResponse, MatrixListResponse, MatrixFullResponse, MatrixUploadCSVRequest, MatrixUploadResponse, MatrixValidationResponse, MatrixExportCSVRequest, MatrixExportCSVResponse, AddRowRequest, AddColumnRequest, SetCellValueRequest, CRUDResponse, CacheStatsResponse

### Calculation Functions (100+ calculate_* Funktionen)

**Financial Calculations** (`financial_calculations.py`, `financial_tools.py`):
- `calculate_payback_years()` - Amortisationszeit
- `calculate_discount_amount()` - Rabatt-Berechnung
- `calculate_surcharge_amount()` - Aufschlag
- `calculate_vat_amount()` - MwSt-Berechnung
- `calculate_gross_from_net()` - Brutto aus Netto
- `calculate_net_from_gross()` - Netto aus Brutto
- `calculate_final_price()` - Endpreis mit allen Modifikatoren
- `calculate_annuity()` - Annuität für Kredite
- `calculate_leasing_costs()` - Leasing-Kosten
- `calculate_depreciation()` - Abschreibungen
- `calculate_financing_comparison()` - Finanzierungs-Vergleich
- `calculate_capital_gains_tax()` - Kapitalertragssteuer
- `calculate_contracting_costs()` - Contracting-Kosten

**Heatpump Calculations** (`heatpump_*.py`):
- `calculate_building_heat_load()` - Heizlast-Berechnung
- `calculate_heatpump_economics()` - Wirtschaftlichkeit
- `calculate_pv_self_consumption_heatpump()` - PV-Eigenverbrauch
- `calculate_beg_subsidy()` - BEG-Förderung
- `calculate_jaz_prognosis()` - JAZ-Prognose
- `calculate_buffer_tank_size()` - Pufferspeicher-Dimensionierung
- `calculate_price_scenarios()` - Preis-Szenarien
- `calculate_tax_benefits()` - Steuervorteile
- `calculate_noise_analysis()` - Lärmanalyse
- `calculate_smart_grid_benefits()` - Smart-Grid-Vorteile
- `calculate_grid_service_bonus()` - Netzdienlichkeits-Bonus
- `calculate_lifecycle_co2()` - Lebenszyklus-CO2
- `calculate_maintenance_schedule()` - Wartungsplan
- `calculate_insulation_upgrade()` - Dämmungs-Upgrade
- `calculate_window_upgrade()` - Fenster-Upgrade
- `calculate_subsidies()` - Förderungen
- `calculate_co2_footprint()` - CO2-Fußabdruck
- `calculate_hourly_electricity_costs()` - Stündliche Stromkosten
- `calculate_dynamic_tariff_comparison()` - Dynamischer Tarif-Vergleich
- `calculate_stromcloud_economics()` - Stromcloud-Wirtschaftlichkeit
- `calculate_smart_home_benefits()` - Smart-Home-Vorteile

**PV & 3D Calculations** (`pv3d.py`, `calculations.py`):
- `calculate_shading_for_module()` - Verschattungs-Analyse
- `calculate_sun_position()` - Sonnenstand
- `calculate_z_position()` - Z-Position für 3D-Module
- `calculate_module_grid()` - Modul-Grid-Platzierung

**Pricing Calculations** (`dynamic_pricing_engine.py`, `excel_product_pricing.py`):
- `calculate_dynamic_total_price()` - Dynamischer Gesamtpreis
- `calculate_hardware_pricing()` - Hardware-Preise
- `calculate_services_pricing_dynamic()` - Service-Preise
- `calculate_accessories_pricing()` - Zubehör-Preise
- `calculate_price_adjustments()` - Preis-Anpassungen
- `calculate_product_price_from_matrix()` - Matrix-basierte Preise
- `calculate_product_price_for_product()` - Produkt-spezifische Preise
- `calculate_special_products_cost()` - Spezialprodukte
- `calculate_services_cost()` - Service-Kosten
- `calculate_extras_cost()` - Extras-Kosten
- `calculate_all_extras()` - Alle Extras kombiniert

**Heating Calculations** (`heating_cost_calculator.py`, `heiz_calc.py`):
- `calculate_heating_costs()` - Heizkosten
- `calculate_heatpump_savings()` - Wärmepumpen-Einsparungen
- `calculate_heat_load_kw()` - Heizlast in kW

**Payment & Financing** (`payment_terms.py`):
- `compute_payment_schedule()` - Zahlungsplan
- `calculate_comprehensive_payment()` - Umfassende Zahlung

**Analysis Utils** (`analysis_utils.py`):
- `calculate_percentage_change()` - Prozentuale Änderung
- `calculate_compound_growth()` - Zinseszins-Wachstum
- `calculate_present_value()` - Barwert

### Test Suite (789 Test-Dateien!)

**Hauptkategorien**:
- **CRM Tests** (50+ Dateien): `test_crm_*.py`, `test_customer_*.py`, `test_contract_*.py`
- **Controlling Tests** (20+ Dateien): `test_controlling_*.py`, `test_team_*.py`, `test_performance_*.py`
- **PDF Tests** (30+ Dateien): `test_pdf_*.py`, `test_multi_pdf_*.py`
- **3D Tests** (15+ Dateien): `test_3d_*.py`, `test_collision_*.py`, `test_module_placement_*.py`
- **Heatpump Tests** (10+ Dateien): `test_heatpump_*.py`, `test_heating_*.py`
- **Admin Tests** (25+ Dateien): `test_admin_*.py`, `test_security_*.py`
- **Chart Tests** (10+ Dateien): `test_chart_*.py`, `test_visualization_*.py`
- **Integration Tests** (30+ Dateien): `test_integration_*.py`, `test_workflow_*.py`
- **Backend Tests** (100+ Dateien): `backend/tests/test_*.py`

**Wichtige Test-Patterns**:
```python
# pytest Fixtures
@pytest.fixture
def db_connection():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()

# Parametrized Tests
@pytest.mark.parametrize("input,expected", [
    (10, 20),
    (20, 40),
])
def test_calculation(input, expected):
    assert calculate(input) == expected

# Performance Tests
@pytest.mark.performance
def test_pdf_generation_speed():
    start = time.time()
    generate_pdf()
    assert time.time() - start < 5.0
```

### Build & Deployment Scripts (9 BAT-Dateien)

**Build System**:
- `BUILD_COMPLETE.bat`: Vollständiger Build-Prozess
- `BUILD_EXE.bat`: Erstelle EXE mit PyInstaller
- `CREATE_FINAL_SETUP.bat`: Inno Setup für Installer
- `TEST_EXE.bat`: Test der erstellten EXE

**Start Scripts**:
- `ARSCHIBALD_STARTEN.bat`: Hauptstart-Script
- `Start_ARSCHIBALD.bat`: Alternative Starter
- `Start_Ömers All in One Dingsbums.bat`: Legacy-Starter
- `OemersBokuk4all_Launcher.bat`: Launcher-Variante

**Utilities**:
- `VIDEO_KONVERTIEREN.bat`: Video-Konvertierung für Intro

**Pattern**:
```batch
@echo off
REM Automatischer Build mit Fehlerbehandlung

echo Starte Build-Prozess...

REM Umgebung prüfen
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python nicht gefunden!
    pause
    exit /b 1
)

REM PyInstaller ausführen
pyinstaller --clean --noconfirm ARSCHIBALD_COMPLETE.spec
if errorlevel 1 (
    echo FEHLER beim Build!
    pause
    exit /b 1
)

echo Build erfolgreich!
pause
```

### YAML/JSON Configuration Files

**YAML-Dateien** (94 Dateien):
- **PDF Koordinaten** (70+ Dateien):
  - `coords/seite1.yml` bis `seite8.yml` - Single-PDF Koordinaten
  - `coords_multi/seite{N}_f{X}.yml` - Multi-Firma Koordinaten (f1-f8, Seite 1-8)
  - `coords_wp/wp_seite1.yml` bis `wp_seite8.yml` - Wärmepumpen-PDFs
  
- **GitHub Workflows** (7 Dateien in `solar-calculator-pro/.github/workflows/`):
  - `ci.yml`, `ci-cd.yml` - CI/CD Pipeline
  - `build.yml` - Build-Automation
  - `security.yml` - Security-Scans
  - `performance.yml` - Performance-Tests
  - `release.yml` - Release-Automation

**JSON-Dateien** (1040+ Dateien):
- **Core Config**:
  - `de.json` - Deutsche Lokalisierung (3000+ Einträge)
  - `settings.json` - App-Einstellungen
  - `schema.json` - Datenbank-Schema
  - `.vscode/settings.json` - VS Code Config
  - `package.json` - NPM Dependencies
  
- **Data Files**:
  - `data/ui_effects_settings.json` - UI-Effekte
  - `waermepumpen_produkte_*.json` - Wärmepumpen-Katalog
  
- **Test Data** (20+ Dateien):
  - `tests/test_*_config.json` - Test-Konfigurationen
  - `tests/test_*_payload.json` - Test-Payloads
  
- **Theming** (20+ Dateien in `theming/themes/`):
  - `shadcn-default.json`, `shadcn-dark.json`
  - `shadcn-blue.json`, `shadcn-purple.json`, etc.
  
- **Backend** (100+ Dateien):
  - `solar-calculator-pro/frontend/tsconfig.json` - TypeScript Config
  - `solar-calculator-pro/frontend/components.json` - Component Registry
  - `solar-calculator-pro/backend/docs/postman_collection.json` - API Docs

### Markdown Documentation (2049+ MD-Dateien!)

**Hauptkategorien**:
- **Feature Docs** (500+ Dateien): `*_COMPLETE.md`, `*_IMPLEMENTATION*.md`
- **Reference Docs** (300+ Dateien): `*_REFERENCE.md`, `*_QUICK_REFERENCE.md`
- **Guides** (200+ Dateien): `*_GUIDE.md`, `*_ANLEITUNG.md`
- **Task Tracking** (100+ Dateien): `TASK_*_COMPLETE.md`
- **Backend Docs** (200+ Dateien): `backend/TASK_*.md`, `backend/docs/*.md`
- **Core Docs** (100+ Dateien): `core/*.md`
- **CRM Docs** (50+ Dateien): `crm/features/*.md`, `crm/utils/*.md`

**Wichtige Dokumentationen**:
- `BUILD_ANLEITUNG.md` - Build-Anleitung
- `AUSWERTUNGSPERIODEN_HANDBUCH.md` - Controlling-Handbuch
- `COMPLETE_PROJECT_ANALYSIS.md` - Projekt-Analyse
- `DEUTSCHE_FORMATIERUNG_DOKUMENTATION.md` - Formatierungs-Standard
- `3D_VISUALIZATION_TEST_ANLEITUNG.md` - 3D-Testing
- `Agent/DOCUMENTATION_INDEX.md` - Agent-Doku-Index

### Utils & Tools Verzeichnis (100+ Files)

**Haupt-Tools** (`nützliche tools/`):
- **50+ Nummerierte Tools** (`01_clean_imports.py` bis `50_wol.py`)
- **Code Quality**:
  - `cache_leerer.py` - Cache-Cleaner
  - `code_formatter.py` - Code-Formatierung
  - `dead_code_finder.py` - Toten Code finden
  - `dead_import_finder.py` - Ungenutzte Imports
  - `dependency_checker.py` - Dependency-Analyse
  - `import_bereiniger.py` - Import-Bereinigung
  
- **PDF Tools**:
  - `pdf_erstellen.py`, `pdf_erstellen_komplett.py` - PDF-Erstellung
  - `pdf_zu_markdown.py` - PDF → Markdown Converter
  - `pdf_zu_png.py` - PDF → PNG Converter
  - `txt_based_pdf_generator.py` - Text-basierte PDF-Gen
  
- **Security**:
  - `secret_scanner.py` - Secret-Detection
  - `scan_malware.py` - Malware-Scanner
  - `quantum_cryptographic_vault.py` - Krypto-Vault
  - `steganography_code_injector.py` - Steganographie
  
- **Analysis**:
  - `behavioral_analysis_engine.py` - Benutzerverhalten
  - `deep_code_archaelogist.py` - Code-Archäologie
  - `log_analyzer.py` - Log-Analyse
  - `performance_profiler.py` - Performance-Profiling
  
- **Database**:
  - `datenbank_bereiniger.py` - DB-Cleaning
  - `backup_manager.py` - Backup-Verwaltung
  
- **Automation**:
  - `docker_helper.py` - Docker-Automation
  - `master_optimierer.py` - Master-Optimizer
  - `python_tool_generator.py` - Tool-Generator
  - `neural_code_mutator.py` - Code-Mutation
  - `test_runner.py` - Test-Automation

**Utils-Dateien** (`utils/`):
- **3D-System** (15+ Dateien):
  - `pv3d.py`, `pv3d_plotly.py` - 3D-Engines
  - `pv3d_module_placement_ui.py` - Modul-Platzierung
  - `pv3d_export.py`, `pv3d_export_buttons.py` - Export
  - `pv3d_performance.py`, `pv3d_optimization.py` - Optimierung
  - `pv3d_mounting_logic.py` - Montage-Logik
  - `pv3d_grid_calculator.py` - Grid-Berechnungen
  
- **PDF-Utils**:
  - `pdf_visual_inject.py` - Visual-Injection
  - `export_coords.py` - Koordinaten-Export
  
- **UI-Helpers**:
  - `shadcn_sidebar.py` - Sidebar-Komponente
  - `shadcn_migration_helpers.py` - Migration-Helpers
  - `solar_animation.py` - Animationen

### Config & Settings Files (79 Dateien)

**Config-Module**:
- `core/config.py` (800+ Zeilen) - Haupt-Konfig mit 7 @dataclass
- `core/logging_config.py` - Logging-Konfiguration
- `Agent/config.py` - Agent-Konfiguration
- `backend/core/config.py` - Backend-Config
- `controlling/pdf_config.py` - PDF-Config für Controlling
- `solar-calculator-pro/backend/config.py` - Solar-Calculator Backend

**Settings-Module**:
- `admin_controlling_settings_ui.py` - Controlling-Settings-UI
- `admin_pdf_settings_ui.py` - PDF-Settings-UI
- `admin_heatpump_settings_ui.py` - Wärmepumpen-Settings
- `admin_intro_settings_ui.py` - Intro-Settings
- `admin_ui_effects_settings.py` - UI-Effekte-Settings
- `admin_heating_costs_config_ui.py` - Heizkosten-Config
- `ui_settings_handler.py` - Settings-Handler
- `components/progress_settings.py` - Progress-Settings

**Backend Config Services**:
- `backend/services/configuration_service.py` - Konfig-Service
- `backend/services/pdf_configuration_service.py` - PDF-Konfig
- `backend/services/system_config_service.py` - System-Konfig
- `backend/services/system_settings_service.py` - System-Settings

**Patterns**:
```python
# Config mit Environment-Variablen
from core.config import AppConfig

config = AppConfig.from_env()
if config.debug:
    enable_debug_mode()

# Settings mit Streamlit UI
def render_settings_ui():
    st.header("Einstellungen")
    
    # Lade aktuelle Settings
    settings = load_settings()
    
    # UI für Änderungen
    new_value = st.text_input("Setting", value=settings.get('key'))
    
    if st.button("Speichern"):
        save_settings({'key': new_value})
        st.success("Gespeichert!")
```

---

## CSS/Style System (261+ Dateien)

### Architektur
**Verzeichnisse**: `static/css/`, `theming/`, `solar-calculator-pro/frontend/src/`

**Core Styles**:
- `static/css/style.css` - Haupt-Stylesheet
- `static/css/dropdown_styling.css` - Dropdown-Komponenten
- `static/css/custom.css` - Custom Overrides
- `static/css/effects.css` - Animationen & Transitions
- `static/css/global.css` - Globale Variablen

**Theme System**:
- `theming/generated_theme.css` - Auto-generierte Themes
- `theming/accessibility.css` - WCAG-Konformität
- `theming/dark_mode.css` - Dark Mode Support
- `theming/theme_variables.css` - CSS Custom Properties

**Component Styles** (50+ Dateien):
```
components/
├── Alert.css
├── Badge.css
├── Button.css
├── Card.css
├── Dropdown.css
├── FormField.css
├── Header.css
├── Modal.css
├── ProgressBar.css
├── Sidebar.css
├── Table.css
└── ...
```

**Page-Specific Styles**:
- `pages/Admin.css` - Admin-Panel
- `pages/Dashboard.css` - Dashboard-Layout
- `pages/SolarCalculator.css` - Solar-Rechner
- `pages/Heatpump.css` - Wärmepumpen-Seite
- `pages/CRM.css` - CRM-Interface

**Layout Styles**:
- `layout/MainLayout.css` - Haupt-Layout
- `layout/Grid.css` - Grid-System
- `layout/Flex.css` - Flexbox-Utilities
- `layout/Responsive.css` - Media Queries

**Wichtig**:
- **Shadcn UI Integration**: Nutzt CSS Variables für Theme-Tokens
- **German Formatting**: Custom CSS für deutsche Zahlenformate
- **Print Styles**: Separate Styles für PDF-Export
- **Accessibility**: ARIA-kompatible Styles

**Pattern**:
```css
/* CSS Variables für Theming */
:root {
  --primary-color: #ff7800;
  --secondary-color: #353535;
  --background: #ffffff;
  --foreground: #0f0f0f;
  --border-radius: 0.5rem;
}

/* Component Style Pattern */
.st-alert {
  background-color: var(--background);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: 1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .st-container {
    padding: 0.5rem;
  }
}
```

---

## TypeScript/React Components (327+ TSX, 109+ TS)

### Architektur
**Verzeichnis**: `solar-calculator-pro/frontend/src/`

**Pages** (Haupt-Seiten):
```tsx
pages/
├── AdminModern.tsx               // Modern Admin Panel
├── DashboardModern.tsx           // Dashboard mit Charts
├── SolarCalculatorModern.tsx     // Solar-Rechner
├── HeatpumpCalculatorModern.tsx  // Wärmepumpen-Rechner
├── CRMModern.tsx                 // CRM Interface
├── ControllingModern.tsx         // Controlling Dashboard
├── PDFGeneratorModern.tsx        // PDF-Generator
└── SettingsModern.tsx            // Einstellungen
```

**Layout Components**:
```tsx
layout/
├── MainLayout.tsx        // Haupt-Layout mit Header/Sidebar
├── Header.tsx            // Navigations-Header
├── Sidebar.tsx           // Collapsible Sidebar
├── Footer.tsx            // Footer mit Links
├── Breadcrumb.tsx        // Breadcrumb-Navigation
└── PageContainer.tsx     // Page-Wrapper mit Padding
```

**Form Components**:
```tsx
forms/
├── FormField.tsx                // Generic Form Field
├── FormContainer.tsx            // Form Wrapper
├── GermanNumberInput.tsx        // Deutsche Zahlen-Eingabe
├── CurrencyInput.tsx            // Währungs-Eingabe
├── DatePicker.tsx               // Datums-Picker
├── FileUpload.tsx               // File-Upload mit Preview
├── MultiSelect.tsx              // Multi-Select Dropdown
└── ValidationMessage.tsx        // Validierungs-Feedback
```

**Data Display Components**:
```tsx
display/
├── DataTable.tsx                // Sortierbare Tabelle
├── Chart.tsx                    // Chart.js Wrapper
├── Card.tsx                     // Info-Karte
├── Badge.tsx                    // Status-Badge
├── MetricCard.tsx               // KPI-Karte
├── ProgressBar.tsx              // Fortschrittsbalken
└── Timeline.tsx                 // Timeline-Komponente
```

**Providers** (Context API):
```tsx
providers/
├── FeatureToggleProvider.tsx    // Feature Flags
├── GlobalFormattingProvider.tsx // Deutsche Formatierung
├── ThemeProvider.tsx             // Theme Management
├── AuthProvider.tsx              // Authentifizierung
└── DataProvider.tsx              // Globaler State
```

**Custom Hooks** (`hooks/*.ts`):
```typescript
hooks/
├── useGermanFormatting.ts       // Deutsche Formatierung
├── useFeatureToggle.ts          // Feature Flags
├── useDebounce.ts               // Debounce Input
├── useLocalStorage.ts           // LocalStorage Sync
├── usePagination.ts             // Pagination Logic
└── useAsync.ts                  // Async State Management
```

**Services** (`services/*.ts`):
```typescript
services/
├── api.ts                       // API Client (FastAPI)
├── auth.ts                      // Auth Service
├── calculations.ts              // Berechnungs-Service
├── pdf.ts                       // PDF Generation Service
├── pricing.ts                   // Pricing Service
└── validation.ts                // Validation Utils
```

**Types** (`types/*.ts`):
```typescript
types/
├── index.ts                     // Haupt-Types
├── api.ts                       // API Response Types
├── calculations.ts              // Calculation Types
├── crm.ts                       // CRM Types
└── forms.ts                     // Form Types
```

**Wichtig**:
- **Electron Migration**: React-App für Electron-Desktop-Version
- **Material-UI**: Nutzt MUI-Komponenten als Basis
- **TypeScript Strict Mode**: Alle Typen vollständig definiert
- **Storybook**: Component-Dokumentation (optional)

**Pattern**:
```tsx
// Modern React Component mit TypeScript
import React from 'react';
import { useGermanFormatting } from '@/hooks/useGermanFormatting';

interface PriceDisplayProps {
  price: number;
  currency?: string;
}

export const PriceDisplay: React.FC<PriceDisplayProps> = ({ 
  price, 
  currency = '€' 
}) => {
  const { formatCurrency } = useGermanFormatting();
  
  return (
    <div className="price-display">
      <span className="price-value">
        {formatCurrency(price)}
      </span>
      <span className="price-currency">{currency}</span>
    </div>
  );
};

export default PriceDisplay;
```

---

## JavaScript Libraries & Dependencies

### Chart.js Integration
**Dateien**: `static/js/chart.js`, `solar-calculator-pro/frontend/src/components/Chart.tsx`

**Verwendung**: Interaktive Charts für Wärmepumpen-Analysen
```javascript
// Chart.js Konfiguration
import Chart from 'chart.js/auto';

const chartConfig = {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Mar', ...],
    datasets: [{
      label: 'Stromverbrauch',
      data: [120, 150, 140, ...],
      borderColor: '#ff7800',
      backgroundColor: 'rgba(255, 120, 0, 0.1)'
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      tooltip: {
        callbacks: {
          label: (context) => `${context.parsed.y} kWh`
        }
      }
    }
  }
};
```

### Microsoft Clarity Analytics
**Datei**: `static/js/clarity.js`

**WICHTIG**: Datenschutz-kritisch!
```javascript
// Microsoft Clarity Tracking
(function(c,l,a,r,i,t,y){
  c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
  t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
  y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
})(window, document, "clarity", "script", "CLARITY_PROJECT_ID");
```

**Bedenken**:
- Tracking von Benutzerverhalten
- DSGVO-Konformität prüfen!
- Cookie-Banner erforderlich?
- Datenweitergabe an Microsoft

### Kaleido (Plotly PNG Export)
**Package**: `kaleido==1.0.0`

**Verwendung**: Server-side PNG-Export von Plotly-Charts
```python
import plotly.graph_objects as go
import kaleido

fig = go.Figure(data=go.Bar(y=[2, 3, 1]))
fig.write_image("chart.png", engine="kaleido")
```

**Wichtig**:
- Benötigt für PDF-eingebettete Charts
- Funktioniert headless (ohne Browser)
- Alternative zu orca (deprecated)

---

## HTML Templates & Static Content (5490+ Dateien)

### Demo Pages
**Verzeichnis**: Root-Verzeichnis

- `demo_module_details_hover.html` - Interaktive Modul-Details mit Hover-Effekten
- Weitere Demo-Seiten für Features

### Heat Pump Product Catalog
**Verzeichnis**: `mirror/www.heizungsdiscount24.de/waermepumpen/`

**Struktur**: 5000+ HTML-Seiten mit Produktinformationen

**Beispiel-Pfade**:
```
mirror/www.heizungsdiscount24.de/waermepumpen/
├── luft-wasser-waermepumpe/
│   ├── marke-a-modell-x.html
│   ├── marke-b-modell-y.html
│   └── ...
├── sole-wasser-waermepumpe/
│   └── ...
└── wasser-wasser-waermepumpe/
    └── ...
```

**Zweck**:
- Gespiegelter Produkt-Katalog von heizungsdiscount24.de
- Datenquelle für Wärmepumpen-Datenbank
- HTML-Parsing für Produktdaten-Import

**Wichtig**:
- Copyright/Lizenz prüfen!
- Möglicherweise automatisch generiert
- Synchronisierung mit Live-Website?

**Pattern für HTML-Parsing**:
```python
from bs4 import BeautifulSoup

def parse_heatpump_product(html_path: str) -> dict:
    """Extrahiert Produktdaten aus HTML"""
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    return {
        'name': soup.find('h1', class_='product-name').text,
        'price': extract_price(soup),
        'power_kw': extract_power(soup),
        'cop': extract_cop(soup),
        'manufacturer': soup.find('span', class_='brand').text
    }
```

---

## Enums, Constants & Configuration Classes (100+)

### Pricing Enums
```python
# pricing/enhanced_pricing_engine.py
class PricingMode(str, Enum):
    MATRIX = "matrix"        # Preis-Matrix-basiert
    DIRECT = "direct"        # Direkte Kalkulation
    HYBRID = "hybrid"        # Kombination

class MarginType(str, Enum):
    PERCENTAGE = "percentage"  # Prozentuale Marge
    FIXED = "fixed"           # Fixer Aufschlag
    TIERED = "tiered"         # Gestaffelte Marge

class CalculatePer(str, Enum):
    STUECK = "Stück"
    METER = "Meter"
    QUADRATMETER = "Quadratmeter"
    KWP = "kWp"
    PAUSCHAL = "pauschal"
```

### Cache System Enums
```python
# core/cache.py
class CacheStrategy(Enum):
    LRU = "lru"              # Least Recently Used
    LFU = "lfu"              # Least Frequently Used
    FIFO = "fifo"            # First In First Out
    TTL = "ttl"              # Time To Live

class InvalidationTrigger(Enum):
    TIME_BASED = "time_based"
    EVENT_BASED = "event_based"
    SIZE_BASED = "size_based"
    MANUAL = "manual"
```

### Controlling Enums
```python
# controlling/models.py
class PeriodType(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class PeriodStatus(str, Enum):
    ACTIVE = "active"
    LOCKED = "locked"
    ARCHIVED = "archived"

class EmployeeRole(str, Enum):
    SALES = "sales"
    MANAGER = "manager"
    ADMIN = "admin"
    VIEWER = "viewer"
```

### Notification Enums
```python
# controlling/notifications.py
class NotificationType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    REMINDER = "reminder"

class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
```

### Progress Management Enums
```python
# components/progress_manager.py
class ProgressStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

### Dependency Injection Enums
```python
# core/dependency_injection.py
class ServiceLifetime(Enum):
    SINGLETON = "singleton"    # Nur eine Instanz
    SCOPED = "scoped"         # Pro Request/Session
    TRANSIENT = "transient"   # Jedes Mal neue Instanz
```

### Validation Enums
```python
# core/widget_validation.py
class ValidationType(Enum):
    REQUIRED = "required"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    PATTERN = "pattern"
    CUSTOM = "custom"
```

**Wichtig**: 
- **Alle Enums erben von `str, Enum`** für Pickle-Serialisierung (Streamlit Session State!)
- **Naming Convention**: SCREAMING_SNAKE_CASE für Werte
- **Type Hints**: Verwende Enum-Typen in Function Signatures

---

## YAML Koordinaten-System (94 Dateien)

### Single-PDF Koordinaten
**Verzeichnis**: `coords/`
```yaml
# coords/seite1.yml
- Text: "Kundenname"
  Position: [100.0, 700.0, 300.0, 720.0]  # [x1, y1, x2, y2]
  Font: "Helvetica-Bold"
  FontSize: 12.0
  Color: 0  # RGB Hex: 0x000000
  Alignment: "left"

- Text: "Gesamtpreis_brutto"
  Position: [450.0, 200.0, 550.0, 215.0]
  Font: "Helvetica"
  FontSize: 10.0
  Color: 3487029  # RGB Hex: 0x353535
  Alignment: "right"  # Wichtig für Preise!
```

**Dateien**:
- `seite1.yml` bis `seite8.yml` - 8 Seiten Single-PDFs

### Multi-Firma Koordinaten
**Verzeichnis**: `coords_multi/`

**Namens-Pattern**: `seite{N}_f{X}.yml`
- `{N}`: Seite 1-8
- `{X}`: Firma f1-f8 (8 Firmen-Varianten)

**Beispiele**:
- `seite1_f1.yml` - Seite 1, Firma 1
- `seite1_f2.yml` - Seite 1, Firma 2
- `seite8_f8.yml` - Seite 8, Firma 8

**Total**: 8 Seiten × 8 Firmen = 64 Dateien

### Wärmepumpen-Koordinaten
**Verzeichnis**: `coords_wp/`

**Dateien**:
- `wp_seite1.yml` bis `wp_seite8.yml` - Wärmepumpen-PDFs

**YAML-Schema**:
```yaml
# Alle Felder
- Text: str                    # Platzhalter-Name
  Position: [x1, y1, x2, y2]  # Bottom-left zu Top-right
  Font: str                    # ReportLab-Font (Helvetica, Times-Roman, etc.)
  FontSize: float              # Schriftgröße in Punkten
  Color: int                   # RGB als Integer (0xRRGGBB)
  Alignment: str               # "left", "center", "right"
  Bold: bool                   # Optional: Fettdruck
  Italic: bool                 # Optional: Kursiv
```

**Wichtig**:
- **Koordinaten-System**: ReportLab nutzt Bottom-Left Origin
- **Rechtsbündige Preise**: IMMER `Alignment: "right"` für Geldbeträge
- **Farben**: Integer-Notation (3487029 = #353535)
- **Fonts**: Nur ReportLab-Fonts erlaubt!

**Parsing-Pattern**:
```python
import yaml

def parse_coords_file(path: str) -> list[dict]:
    """Lädt YAML-Koordinaten für PDF-Overlay"""
    with open(path, 'r', encoding='utf-8') as f:
        coords = yaml.safe_load(f)
    
    # Validierung
    for item in coords:
        assert 'Text' in item
        assert 'Position' in item
        assert len(item['Position']) == 4
        
    return coords
```

---

## Streamlit Configuration (.streamlit/config.toml)

### Vollständige Konfiguration
```toml
[server]
# Port Configuration
port = 8501
headless = false          # Browser öffnet automatisch
enableCORS = true
enableXsrfProtection = true
enableWebsocketCompression = true

# Upload Limits
maxUploadSize = 512       # MB
maxMessageSize = 200      # MB

# Performance
baseUrlPath = ""
cookieSecret = "auto-generated"

[client]
# Toolbar & UI
toolbarMode = "developer"  # "minimal" für Production!
showErrorDetails = true
showSidebarNavigation = true

[browser]
# Tracking
gatherUsageStats = false   # WICHTIG: Keine Telemetrie!
serverAddress = "localhost"
serverPort = 8501

[theme]
# Branding
base = "light"
primaryColor = "#ff7800"           # Orange
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#0f0f0f"
font = "Nunito"

[runner]
# Execution
magicEnabled = true                # Python Magics
installTracer = false
fixMatplotlib = true
postScriptGC = true
fastReruns = true
enforceSerializableSessionState = false  # Pickle-Warnings

[logger]
# Logging
level = "info"
messageFormat = "%(asctime)s %(message)s"

[deprecation]
# Warnings
showPyplotGlobalUse = false
showfileUploaderEncoding = false
```

**Wichtig**:
- **Production**: `toolbarMode = "minimal"` setzen!
- **Privacy**: `gatherUsageStats = false` beibehalten!
- **Upload**: 512 MB Limit für große Excel-Dateien
- **Performance**: `fastReruns = true` für bessere UX
- **Font**: Nunito muss in `static/fonts/` liegen

**Secrets (.streamlit/secrets.toml)**:
```toml
# NIEMALS committen!
[openai]
api_key = "sk-..."

[tavily]
api_key = "tvly-..."

[database]
encryption_key = "..."
```

---

## Sessions & Routing (@dataclass Patterns)

### Navigation Events
```python
# core/router.py
from dataclasses import dataclass
from datetime import datetime
from typing import Any

@dataclass
class NavigationEvent:
    """Browser-style Navigation Event"""
    event_id: str
    event_type: NavigationEventType  # NAVIGATE, BACK, FORWARD, REDIRECT
    from_page: str | None
    to_page: str
    params: dict[str, Any]
    timestamp: datetime
    
    def __post_init__(self):
        # Auto-generate event_id
        if not self.event_id:
            self.event_id = f"nav_{uuid.uuid4().hex[:8]}"

# Usage
event = NavigationEvent(
    event_id="",
    event_type=NavigationEventType.NAVIGATE,
    from_page="crm",
    to_page="project_detail",
    params={'project_id': 123},
    timestamp=datetime.now()
)
```

### Form Snapshots (Undo/Redo)
```python
# core/session.py
@dataclass
class FormSnapshot:
    """Snapshot für Undo/Redo Funktionalität"""
    snapshot_id: str
    form_id: str
    data: dict[str, Any]
    timestamp: datetime
    description: str = ""
    
    def __getstate__(self):
        """Pickle-Serialisierung für Session State"""
        return self.__dict__.copy()
    
    def __setstate__(self, state):
        """Pickle-Deserialisierung"""
        self.__dict__.update(state)

# Usage in Form Manager
from core.form_manager import FormManager

form_mgr = FormManager()
form_state = form_mgr.create_form('customer_form', fields={...})

# Create Snapshot before changes
snapshot = form_mgr.create_snapshot(
    form_state, 
    description="Before email change"
)

# Restore Snapshot
form_mgr.restore_snapshot(snapshot.snapshot_id)
```

### Navigation History
```python
# core/navigation_history.py
@dataclass
class NavigationEntry:
    """Eintrag in Browser-Historie"""
    page: str
    params: dict[str, Any]
    timestamp: datetime
    
@dataclass
class NavigationState:
    """Gesamter Navigations-Zustand"""
    history: list[NavigationEntry]
    current_index: int
    max_history_size: int = 50
    
    def can_go_back(self) -> bool:
        return self.current_index > 0
    
    def can_go_forward(self) -> bool:
        return self.current_index < len(self.history) - 1
    
    def go_back(self) -> NavigationEntry | None:
        if self.can_go_back():
            self.current_index -= 1
            return self.history[self.current_index]
        return None
```

**Pattern für Session State Persistenz**:
```python
# Nach Browser-Refresh wiederherstellen
from core.session import SessionManager

session_mgr = SessionManager()

# Session ID aus URL-Parameter
session_id = st.query_params.get('session_id')

if session_id:
    # Restore Session
    restored = session_mgr.restore_session(session_id)
    if restored:
        st.toast("Sitzung wiederhergestellt! 🎉")
        st.session_state.update(restored.data)
```

---

## Testing Infrastructure (789 Test-Dateien)

### Pytest Konfiguration
**Datei**: `pytest.ini` oder `pyproject.toml`

```ini
[pytest]
testpaths = tests backend/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    performance: Performance-Tests
    integration: Integration-Tests
    unit: Unit-Tests
    slow: Langsame Tests (> 1s)
addopts = 
    -v
    --tb=short
    --strict-markers
    --cov=.
    --cov-report=html
```

### Test-Struktur
```
tests/
├── conftest.py                      # Shared Fixtures
├── test_crm_*.py                    # CRM Tests (50+ Dateien)
├── test_controlling_*.py            # Controlling Tests (20+)
├── test_pdf_*.py                    # PDF Tests (30+)
├── test_3d_*.py                     # 3D Visualization (15+)
├── test_heatpump_*.py               # Wärmepumpen (10+)
├── test_calculations*.py            # Berechnungen (20+)
└── test_integration*.py             # E2E Tests (30+)

backend/tests/
├── test_api_*.py                    # FastAPI Endpoints (100+)
├── test_services_*.py               # Business Logic (50+)
└── test_models_*.py                 # Data Models (20+)
```

### Wichtige Fixtures (conftest.py)
```python
import pytest
import sqlite3
from database import get_db_connection

@pytest.fixture
def db_connection():
    """Test-Datenbank mit Row Factory"""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    
    # Setup
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers")
    cursor.execute("DELETE FROM projects")
    conn.commit()
    
    yield conn
    
    # Teardown
    conn.close()

@pytest.fixture
def sample_customer():
    """Beispiel-Kunde für Tests"""
    return {
        'name': 'Test GmbH',
        'email': 'test@example.com',
        'phone': '+49 123 456789',
        'address': 'Teststraße 1, 12345 Berlin'
    }

@pytest.fixture
def mock_pricing_engine(monkeypatch):
    """Gemockter Pricing Engine"""
    def mock_calculate(product, quantity):
        return product['price_euro'] * quantity
    
    monkeypatch.setattr(
        'pricing.enhanced_pricing_engine.EnhancedPricingEngine.calculate',
        mock_calculate
    )
```

### Parametrized Tests
```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (10000, "10.000,00 €"),
    (1234.56, "1.234,56 €"),
    (0.99, "0,99 €"),
])
def test_german_currency_formatting(input, expected):
    from german_formatting import format_currency
    assert format_currency(input) == expected

@pytest.mark.parametrize("kwp,expected_modules", [
    (10, 25),   # 10 kWp = 25 Module à 400W
    (15, 38),   # 15 kWp = 38 Module
    (20, 50),   # 20 kWp = 50 Module
])
def test_module_calculation(kwp, expected_modules):
    from calculations import calculate_required_modules
    result = calculate_required_modules(kwp, module_power=400)
    assert result == expected_modules
```

### Performance Tests
```python
import pytest
import time

@pytest.mark.performance
def test_pdf_generation_performance():
    """PDF-Generierung sollte < 5 Sekunden sein"""
    from pdf_generator import generate_single_pdf
    
    start = time.time()
    pdf_path = generate_single_pdf(test_config)
    duration = time.time() - start
    
    assert duration < 5.0, f"PDF-Gen zu langsam: {duration:.2f}s"
    assert os.path.exists(pdf_path)

@pytest.mark.performance
def test_database_query_performance():
    """DB-Queries sollten < 100ms sein"""
    from database import load_all_customers
    
    start = time.time()
    customers = load_all_customers()
    duration = (time.time() - start) * 1000  # ms
    
    assert duration < 100, f"Query zu langsam: {duration:.0f}ms"
```

### Integration Tests
```python
def test_end_to_end_customer_to_pdf(db_connection):
    """Kompletter Workflow: Kunde → Projekt → Berechnung → PDF"""
    
    # 1. Kunde anlegen
    customer_id = create_customer(db_connection, {
        'name': 'E2E Test GmbH',
        'email': 'e2e@test.com'
    })
    assert customer_id > 0
    
    # 2. Projekt erstellen
    project_id = create_project(db_connection, {
        'customer_id': customer_id,
        'name': 'Solar-Installation',
        'kwp': 10
    })
    assert project_id > 0
    
    # 3. Berechnung durchführen
    calc_result = perform_pv_calculation({
        'kwp': 10,
        'module_id': 1,
        'inverter_id': 5
    })
    assert calc_result['total_price_net'] > 0
    
    # 4. PDF generieren
    pdf_path = generate_pdf(calc_result, customer_id)
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 10000  # Min 10KB
```

### Test-Kommandos
```powershell
# Alle Tests
pytest tests/ -v

# Nur Performance-Tests
pytest tests/ -m performance

# Mit Coverage
pytest tests/ --cov=. --cov-report=html

# Parallel (schneller)
pytest tests/ -n auto

# Nur Failed Tests re-run
pytest tests/ --lf

# Verbose mit Stdout
pytest tests/ -v -s
```

---

## Pricing Enhancements (Dynamic Keys & Margin Types)

### Calculate Per Engine
**Datei**: `pricing/calculate_per_engine.py`

**Unterstützte Berechnungsbasen**:
```python
class CalculatePerEngine:
    SUPPORTED_UNITS = {
        'Stück': lambda price, qty: price * qty,
        'Meter': lambda price, length: price * length,
        'Quadratmeter': lambda price, area: price * area,
        'kWp': lambda price, kwp: price * kwp,
        'pauschal': lambda price, _: price
    }
    
    def calculate_price(
        self, 
        product: dict, 
        quantity: float,
        calculate_per: str = 'Stück'
    ) -> float:
        """Berechnet Preis basierend auf Berechnungsbasis"""
        base_price = product['price_euro']
        calc_func = self.SUPPORTED_UNITS.get(calculate_per)
        
        if not calc_func:
            raise ValueError(f"Unbekannte Einheit: {calculate_per}")
        
        return calc_func(base_price, quantity)
```

**Product Schema Enhancement**:
```python
# product_db.py
product = {
    'model_name': 'Vertex S 400W',
    'price_euro': 120.50,
    
    # NEU: Enhanced Pricing Fields
    'calculate_per': 'Stück',       # Berechnungsbasis
    'purchase_price_net': 95.00,    # EK netto
    'margin_type': 'percentage',    # oder 'fixed', 'tiered'
    'margin_value': 20.0,           # 20% Marge
    'is_special_product': 0,        # Matrix-Preislogik
}
```

### Margin Types Engine
**Datei**: `pricing/profit_margin_manager.py`

```python
class ProfitMarginManager:
    def calculate_selling_price(
        self,
        purchase_price: float,
        margin_type: str,
        margin_value: float
    ) -> float:
        """Berechnet VK-Preis aus EK + Marge"""
        
        if margin_type == 'percentage':
            # Prozentuale Marge
            return purchase_price * (1 + margin_value / 100)
        
        elif margin_type == 'fixed':
            # Fixer Aufschlag
            return purchase_price + margin_value
        
        elif margin_type == 'tiered':
            # Gestaffelte Marge nach Menge
            if purchase_price < 1000:
                margin = 25  # 25% bei kleinen Beträgen
            elif purchase_price < 5000:
                margin = 20  # 20% bei mittleren
            else:
                margin = 15  # 15% bei großen
            return purchase_price * (1 + margin / 100)
        
        else:
            raise ValueError(f"Unbekannter margin_type: {margin_type}")
```

### Dynamic Key Manager
**Datei**: `pricing/dynamic_key_manager.py`

**Zweck**: Auto-Generierung von Display-Keys für Dropdowns/PDFs

```python
class DynamicKeyManager:
    def generate_keys(
        self,
        product: dict,
        calculation_result: dict | None = None,
        include_pricing: bool = True
    ) -> dict[str, str]:
        """Generiert alle möglichen Display-Keys für ein Produkt"""
        
        keys = {
            # Basis-Keys
            'model_name': product['model_name'],
            'brand': product.get('brand', ''),
            'category': product['category'],
            
            # Spezifikations-Keys
            'capacity_w': f"{product.get('capacity_w', 0)} W",
            'power_kw': f"{product.get('power_kw', 0)} kW",
            'efficiency': f"{product.get('efficiency_percent', 0)}%",
            
            # Dimensions
            'dimensions': f"{product.get('length_m', 0)} × {product.get('width_m', 0)} m",
            'weight': f"{product.get('weight_kg', 0)} kg",
        }
        
        if include_pricing:
            from german_formatting import format_currency
            
            keys.update({
                'price_net': format_currency(product['price_euro']),
                'price_gross': format_currency(product['price_euro'] * 1.19),
                'calculate_per': product.get('calculate_per', 'Stück'),
            })
        
        if calculation_result:
            keys.update({
                'total_price': format_currency(calculation_result['total_price']),
                'quantity': str(calculation_result['quantity']),
            })
        
        return keys
```

**Usage Pattern**:
```python
from pricing.dynamic_key_manager import DynamicKeyManager

key_mgr = DynamicKeyManager()

# Produkt-Keys generieren
product = get_product_by_id(123)
keys = key_mgr.generate_keys(product, include_pricing=True)

# Keys in Dropdown-Label verwenden
dropdown_label = f"{keys['model_name']} ({keys['capacity_w']}) - {keys['price_net']}"

# Keys in PDF-Placeholders verwenden
placeholders = {
    'Modulname': keys['model_name'],
    'Modulleistung': keys['capacity_w'],
    'Modulpreis': keys['price_net'],
}
```

---

## Wärmepumpen Advanced Features

### JAZ (Jahresarbeitszahl) Prognose
**Datei**: `calculations_heatpump.py`

```python
def calculate_jaz_prognosis(
    heat_pump: dict,
    building_data: dict,
    climate_zone: str = 'Deutschland Mitte'
) -> dict:
    """Berechnet realistische JAZ-Prognose"""
    
    # Basis-COP (Herstellerangabe)
    nominal_cop = heat_pump.get('cop', 3.5)
    
    # Faktoren für reale Bedingungen
    factors = {
        'vorlauftemperatur': get_vorlauf_factor(building_data),
        'climate': get_climate_factor(climate_zone),
        'defrost': 0.95,  # 5% Verlust durch Abtauen
        'auxiliary_heating': 0.97,  # 3% Zusatzheizung
    }
    
    # Berechne JAZ
    jaz = nominal_cop
    for factor_name, factor_value in factors.items():
        jaz *= factor_value
    
    return {
        'jaz': round(jaz, 2),
        'nominal_cop': nominal_cop,
        'factors': factors,
        'efficiency_loss_pct': round((1 - jaz/nominal_cop) * 100, 1)
    }
```

### Noise Analysis (Lärmanalyse)
```python
def calculate_noise_analysis(
    heat_pump: dict,
    installation_location: dict,
    neighbor_distance_m: float
) -> dict:
    """Analysiert Lärmemissionen"""
    
    # Hersteller-Angaben
    noise_day_db = heat_pump.get('noise_level_day_db', 50)
    noise_night_db = heat_pump.get('noise_level_night_db', 45)
    
    # Schallausbreitung über Distanz
    # Schalldruckpegel nimmt mit 6 dB pro Distanzverdopplung ab
    reference_distance = 1  # meter
    attenuation = 20 * math.log10(neighbor_distance_m / reference_distance)
    
    noise_at_neighbor_day = noise_day_db - attenuation
    noise_at_neighbor_night = noise_night_db - attenuation
    
    # TA Lärm Grenzwerte
    limits = {
        'Wohngebiet Tag': 55,
        'Wohngebiet Nacht': 40,
        'Mischgebiet Tag': 60,
        'Mischgebiet Nacht': 45,
    }
    
    return {
        'noise_at_source_day': noise_day_db,
        'noise_at_source_night': noise_night_db,
        'noise_at_neighbor_day': round(noise_at_neighbor_day, 1),
        'noise_at_neighbor_night': round(noise_at_neighbor_night, 1),
        'ta_laerm_limits': limits,
        'compliant': noise_at_neighbor_night < limits['Wohngebiet Nacht']
    }
```

### Smart Grid Benefits
```python
def calculate_smart_grid_benefits(
    heat_pump: dict,
    electricity_tariff: str,  # 'dynamic' oder 'standard'
    pv_system: dict | None = None
) -> dict:
    """Berechnet Smart-Grid-Vorteile"""
    
    benefits = {
        'netzentgeltbefreiung': 0,
        'dynamic_tariff_savings': 0,
        'pv_self_consumption_bonus': 0,
        'grid_service_bonus': 0
    }
    
    # § 14a EnWG: Reduzierte Netzentgelte
    if heat_pump.get('smart_grid_ready', False):
        annual_grid_fees = 150  # EUR
        benefits['netzentgeltbefreiung'] = annual_grid_fees
    
    # Dynamischer Tarif-Vorteil
    if electricity_tariff == 'dynamic':
        # 20% günstigere Preise durch zeitliche Verschiebung
        annual_consumption = heat_pump.get('annual_consumption_kwh', 5000)
        avg_price_kwh = 0.30
        savings_pct = 0.20
        benefits['dynamic_tariff_savings'] = (
            annual_consumption * avg_price_kwh * savings_pct
        )
    
    # PV-Eigenverbrauch-Bonus
    if pv_system:
        pv_for_heatpump_kwh = calculate_pv_self_consumption_heatpump(
            pv_system['annual_yield_kwh'],
            heat_pump.get('annual_consumption_kwh', 5000)
        )
        grid_price_kwh = 0.30
        pv_cost_kwh = 0.10
        benefits['pv_self_consumption_bonus'] = (
            pv_for_heatpump_kwh * (grid_price_kwh - pv_cost_kwh)
        )
    
    # Netzdienlichkeits-Bonus
    if heat_pump.get('grid_service_ready', False):
        benefits['grid_service_bonus'] = 100  # EUR/Jahr
    
    return {
        'total_annual_benefit': sum(benefits.values()),
        'breakdown': benefits
    }
```

### Lifecycle CO2 Analysis
```python
def calculate_lifecycle_co2(
    heat_pump: dict,
    building_data: dict,
    lifetime_years: int = 20
) -> dict:
    """Komplette Lebenszyklus-CO2-Bilanz"""
    
    # Herstellung
    manufacturing_co2_kg = heat_pump.get('manufacturing_co2_kg', 500)
    
    # Transport
    transport_distance_km = 500
    transport_co2_kg = transport_distance_km * 0.1  # 0.1 kg CO2/km
    
    # Installation
    installation_co2_kg = 50
    
    # Betrieb (20 Jahre)
    annual_consumption_kwh = heat_pump.get('annual_consumption_kwh', 5000)
    electricity_co2_g_kwh = 400  # 400g CO2/kWh Strommix Deutschland
    operation_co2_kg = (
        annual_consumption_kwh * electricity_co2_g_kwh / 1000 * lifetime_years
    )
    
    # Entsorgung
    disposal_co2_kg = 100
    
    total_co2_kg = (
        manufacturing_co2_kg +
        transport_co2_kg +
        installation_co2_kg +
        operation_co2_kg +
        disposal_co2_kg
    )
    
    # Vergleich: Gas-Heizung
    annual_heat_demand_kwh = building_data.get('annual_heat_demand_kwh', 15000)
    gas_co2_g_kwh = 200  # 200g CO2/kWh Gas
    gas_total_co2_kg = annual_heat_demand_kwh * gas_co2_g_kwh / 1000 * lifetime_years
    
    return {
        'heat_pump_total_co2_kg': total_co2_kg,
        'gas_heating_total_co2_kg': gas_total_co2_kg,
        'co2_savings_kg': gas_total_co2_kg - total_co2_kg,
        'breakdown': {
            'manufacturing': manufacturing_co2_kg,
            'transport': transport_co2_kg,
            'installation': installation_co2_kg,
            'operation': operation_co2_kg,
            'disposal': disposal_co2_kg
        }
    }
```

---

## Docker/Container System (Agent Sandbox)

### Agent Workspace Isolation
**Verzeichnis**: `Agent/sandbox/`

**Zweck**: Isolierte Docker-Container für KI-Agent-Code-Execution

**Dockerfile**:
```dockerfile
# Agent/sandbox/Dockerfile
FROM python:3.13-slim

# System-Dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Python-Dependencies
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Arbeitsverzeichnis
WORKDIR /workspace

# User ohne Root-Rechte
RUN useradd -m -u 1000 agent && chown -R agent:agent /workspace
USER agent

# Execution Command
CMD ["python", "-u", "main.py"]
```

**docker-compose.yml**:
```yaml
# Agent/sandbox/docker-compose.yml
version: '3.8'

services:
  agent-sandbox:
    build: .
    container_name: arschibald_agent_sandbox
    volumes:
      - ./agent_workspace:/workspace:rw
      - ./knowledge_base:/knowledge_base:ro
    environment:
      - PYTHONUNBUFFERED=1
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    networks:
      - agent-network
    mem_limit: 2g
    cpus: 2
    restart: on-failure
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=100m

networks:
  agent-network:
    driver: bridge
```

**Agent Sandbox Pattern**:
```python
# agent_ui.py
import docker
import os

def execute_agent_code_in_sandbox(code: str) -> dict:
    """Führt Agent-Code in isoliertem Docker-Container aus"""
    
    client = docker.from_env()
    
    # Code in Workspace schreiben
    workspace_path = "Agent/sandbox/agent_workspace/"
    code_path = os.path.join(workspace_path, "main.py")
    
    with open(code_path, 'w', encoding='utf-8') as f:
        f.write(code)
    
    try:
        # Container starten
        container = client.containers.run(
            "arschibald_agent_sandbox",
            detach=True,
            remove=True,
            mem_limit="2g",
            cpu_quota=200000,  # 2 CPUs
            network_mode="none",  # Kein Netzwerk-Zugriff!
            volumes={
                workspace_path: {
                    'bind': '/workspace',
                    'mode': 'rw'
                }
            },
            environment={
                'PYTHONUNBUFFERED': '1'
            }
        )
        
        # Logs sammeln
        logs = container.logs(stream=True)
        output = []
        
        for line in logs:
            output.append(line.decode('utf-8'))
            if len(output) > 1000:  # Max 1000 Zeilen
                break
        
        # Exit Code
        result = container.wait()
        exit_code = result['StatusCode']
        
        return {
            'success': exit_code == 0,
            'output': ''.join(output),
            'exit_code': exit_code
        }
        
    except docker.errors.DockerException as e:
        return {
            'success': False,
            'output': '',
            'error': str(e)
        }
    
    finally:
        # Cleanup
        try:
            os.remove(code_path)
        except:
            pass
```

**Sicherheits-Features**:
- **Netzwerk-Isolation**: `network_mode="none"` - Kein Internet-Zugriff
- **Resource Limits**: 2 GB RAM, 2 CPUs max
- **Read-Only Filesystem**: Container kann nur in /workspace schreiben
- **Non-Root User**: Container läuft als User `agent` (UID 1000)
- **Timeout**: Container stirbt automatisch nach 5 Minuten

---

## Backup & Migration System

### Alembic Migration Manager
**Datei**: `core/migration_manager.py`

```python
class MigrationManager:
    """Verwaltet Datenbank-Migrationen mit Alembic"""
    
    def __init__(self, db_path: str = "data/app_data.db"):
        self.db_path = db_path
        self.alembic_cfg = Config("alembic.ini")
        self.alembic_cfg.set_main_option(
            "sqlalchemy.url",
            f"sqlite:///{db_path}"
        )
    
    def upgrade_to_head(self):
        """Führt alle ausstehenden Migrationen aus"""
        from alembic import command
        command.upgrade(self.alembic_cfg, "head")
    
    def downgrade_one_step(self):
        """Rollback um eine Migration"""
        from alembic import command
        command.downgrade(self.alembic_cfg, "-1")
    
    def create_migration(self, message: str):
        """Erstellt neue Migration (auto-detect)"""
        from alembic import command
        command.revision(
            self.alembic_cfg,
            message=message,
            autogenerate=True
        )
    
    def get_current_revision(self) -> str:
        """Gibt aktuelle DB-Revision zurück"""
        from alembic.script import ScriptDirectory
        from alembic.runtime.migration import MigrationContext
        
        script = ScriptDirectory.from_config(self.alembic_cfg)
        
        with get_db_connection() as conn:
            context = MigrationContext.configure(conn)
            current = context.get_current_revision()
            
        return current or "no_migration"
    
    def list_pending_migrations(self) -> list[str]:
        """Listet ausstehende Migrationen"""
        from alembic.script import ScriptDirectory
        
        script = ScriptDirectory.from_config(self.alembic_cfg)
        current = self.get_current_revision()
        
        revisions = []
        for rev in script.walk_revisions():
            if rev.revision != current:
                revisions.append(f"{rev.revision}: {rev.doc}")
            else:
                break
        
        return revisions
```

### Backup Manager
**Datei**: `nützliche tools/backup_manager.py`

```python
import shutil
import os
from datetime import datetime
import zipfile

class BackupManager:
    """Erstellt und verwaltet Datenbank-Backups"""
    
    BACKUP_DIR = "backups/"
    
    def create_backup(
        self,
        include_documents: bool = True,
        include_templates: bool = True
    ) -> str:
        """Erstellt vollständiges Backup"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.zip"
        backup_path = os.path.join(self.BACKUP_DIR, backup_name)
        
        os.makedirs(self.BACKUP_DIR, exist_ok=True)
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Datenbank
            zipf.write("data/app_data.db", "app_data.db")
            
            # Dokumente
            if include_documents:
                for root, dirs, files in os.walk("customer_documents/"):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path)
            
            # PDF-Templates
            if include_templates:
                for root, dirs, files in os.walk("pdf_templates_static/"):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path)
            
            # Koordinaten
            for coords_dir in ['coords/', 'coords_multi/', 'coords_wp/']:
                if os.path.exists(coords_dir):
                    for file in os.listdir(coords_dir):
                        file_path = os.path.join(coords_dir, file)
                        if file.endswith('.yml'):
                            zipf.write(file_path)
        
        return backup_path
    
    def restore_backup(self, backup_path: str):
        """Stellt Backup wieder her"""
        
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup nicht gefunden: {backup_path}")
        
        # Backup vor Restore
        current_backup = self.create_backup()
        print(f"Safety backup erstellt: {current_backup}")
        
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(".")
            
            print(f"✓ Backup wiederhergestellt: {backup_path}")
            
        except Exception as e:
            print(f"✗ Fehler beim Restore: {e}")
            print(f"  Safety backup: {current_backup}")
            raise
    
    def list_backups(self) -> list[dict]:
        """Listet alle verfügbaren Backups"""
        
        if not os.path.exists(self.BACKUP_DIR):
            return []
        
        backups = []
        for file in os.listdir(self.BACKUP_DIR):
            if file.endswith('.zip'):
                file_path = os.path.join(self.BACKUP_DIR, file)
                stat = os.stat(file_path)
                
                backups.append({
                    'filename': file,
                    'path': file_path,
                    'size_mb': round(stat.st_size / 1024 / 1024, 2),
                    'created': datetime.fromtimestamp(stat.st_mtime),
                })
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def cleanup_old_backups(self, keep_count: int = 10):
        """Löscht alte Backups (behält die neuesten N)"""
        
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            return
        
        to_delete = backups[keep_count:]
        for backup in to_delete:
            os.remove(backup['path'])
            print(f"Deleted old backup: {backup['filename']}")
```

**Usage Pattern**:
```python
from backup_manager import BackupManager

backup_mgr = BackupManager()

# Backup erstellen (vor Migration)
backup_path = backup_mgr.create_backup()
print(f"Backup erstellt: {backup_path}")

# Migration ausführen
from core.migration_manager import MigrationManager
migration_mgr = MigrationManager()
migration_mgr.upgrade_to_head()

# Bei Fehler: Restore
if migration_failed:
    backup_mgr.restore_backup(backup_path)
```

---

## Build & Deployment Infrastructure (21+ Kategorien)

### PowerShell Scripts (8 Scripts)

**Verzeichnis**: Root + tools/

**Scripts**:
```powershell
# 1. audit_and_dedupe.ps1 - Audit & Deduplizierung
# Scannt Codebase nach Duplikaten und Inkonsistenzen

# 2. migrate-to-pnpm.ps1 - Package Manager Migration
# Migriert von npm/yarn zu pnpm für schnellere Installs

# 3. restart_with_optimization.ps1 - Optimized Restart
# Neustart der App mit Performance-Optimierungen

# 4. convert_video_small_webm.ps1 - Video Compression
# Konvertiert Videos zu kleinen WebM-Dateien

# 5. convert_video_for_web.ps1 - Web Video Conversion
# Optimiert Videos für Web-Delivery

# 6. install.ps1 - Installation Script
# Automatische Installation aller Dependencies

# 7. Agent/sandbox/build.ps1 - Sandbox Build
# Baut Docker Sandbox für Agent

# 8. tools/build_installer.ps1 - Installer Creation
# Erstellt Windows-Installer mit Inno Setup
```

**Pattern**:
```powershell
# PowerShell Script Template
[CmdletBinding()]
param(
    [string]$Target = "all",
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

Write-Host "Starting process: $Target" -ForegroundColor Green

try {
    # Main Logic
    if ($Verbose) {
        Write-Verbose "Executing with verbose output"
    }
    
    # Execute commands
    & python setup.py install
    
    Write-Host "✓ Success!" -ForegroundColor Green
}
catch {
    Write-Error "✗ Error: $_"
    exit 1
}
```

### Shell Scripts (2 Scripts)

**Unix Build Scripts**:
```bash
# solar-calculator-pro/scripts/release-production.sh
#!/bin/bash
set -e

echo " Building Production Release..."

# Build Backend
cd backend
python -m pip install -r requirements.txt
python -m build

# Build Frontend
cd ../frontend
npm ci
npm run build

# Package
cd ..
tar -czf release.tar.gz dist/

echo "✓ Release package created"

# Agent/sandbox/build.sh
#!/bin/bash
docker build -t arschibald_agent_sandbox .
docker-compose up -d
echo "✓ Sandbox ready"
```

### Alembic Configuration (2 Files)

**core/alembic.ini**:
```ini
# Alembic Migration Config for Core DB
[alembic]
script_location = core/migrations
prepend_sys_path = .
version_path_separator = os

sqlalchemy.url = sqlite:///data/app_data.db

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

**backend/alembic.ini** - Separate config for backend database

### pyproject.toml (3 Files)

**Root pyproject.toml** (Hatchling Build System):
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "robust-streamlit-app"
version = "1.0.0"
description = "Maximal robuste Streamlit-Anwendung"
authors = [{name = "Developer", email = "dev@example.com"}]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.11"

dependencies = [
    # Core
    "streamlit==1.28.1",
    "pydantic==2.5.0",
    "sqlalchemy==2.0.23",
    "alembic==1.12.1",
    "duckdb==0.9.2",
    "pandas==2.1.3",
    "numpy==1.25.2",
    
    # Jobs & Async
    "apscheduler==3.10.4",
    "redis==5.0.1",
    
    # Security
    "python-dotenv==1.0.0",
    "cryptography==41.0.7",
    "bcrypt==4.1.1",
    
    # CLI
    "typer==0.9.0",
    "rich==13.7.0",
    
    # Metrics & Monitoring
    "prometheus-client==0.19.0",
    "structlog==23.2.0",
]

[project.optional-dependencies]
dev = [
    "pytest==7.4.3",
    "pytest-cov==4.1.0",
    "pytest-asyncio==0.21.1",
    "black==23.12.0",
    "ruff==0.1.8",
    "mypy==1.7.1",
]

[tool.hatch.build.targets.wheel]
packages = ["core", "components", "utils"]

[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
select = ["E", "F", "I"]

[tool.mypy]
python_version = "3.11"
strict = true
```

### setup.py (3 Files - 569 Lines!)

**Root setup.py** - Komplettes Installations-Paket v2.5.0:
```python
"""
Setup Script für Ömer's All in One DingsBums
=============================================
"""
from setuptools import setup, find_packages

VERSION = "2.5.0"
DESCRIPTION = "Ömer's All in One DingsBums"

REQUIRED_PACKAGES = [
    # Core (bereits dokumentiert)
    "streamlit==1.49.1",
    "pandas==2.3.2",
    "numpy==2.3.2",
    
    # PDF Processing (10+ Libraries!)
    "reportlab==4.4.3",
    "pypdf==6.0.0",
    "PyPDF2==3.0.1",
    "PyPDF3==1.0.6",
    "PyPDF4==1.27.0",
    "pdfplumber==0.11.7",
    "PyMuPDF==1.26.4",
    "pdf2image==1.17.0",
    "pdfminer.six==20250506",
    "pypdfium2==4.30.0",
    "pikepdf>=9.0.0",
    
    # Web Framework
    "fastapi==0.116.1",
    "uvicorn==0.35.0",
    
    # AI/Agent
    "langchain==0.3.27",
    "langchain-openai",
    "openai>=1.0.0",
    
    # 3D Visualization
    "pyvista>=0.43.0",
    "vtk>=9.3.0",
    "stpyvista",
    
    # Excel
    "openpyxl",
    "xlrd",
    "xlsxwriter",
]

setup(
    name="oemers-all-in-one",
    version=VERSION,
    description=DESCRIPTION,
    author="Bokuk2 Development Team",
    packages=find_packages(),
    install_requires=REQUIRED_PACKAGES,
    python_requires='>=3.13',
    entry_points={
        'console_scripts': [
            'arschibald=gui:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['*.yml', '*.yaml', '*.json', '*.toml', '*.ini'],
    },
)
```

### package.json (6 Files - Electron Monorepo!)

**Root package.json** - "kakerlake" Monorepo:
```json
{
  "name": "kakerlake",
  "private": true,
  "workspaces": [
    "apps/*",
    "packages/*"
  ],
  "scripts": {
    "dev": "concurrently -k \"pnpm run dev:renderer\" \"pnpm run dev:watch\" \"pnpm run dev:electron\"",
    "build": "pnpm --filter @kakerlake/core run build && pnpm --filter renderer run build && pnpm --filter @kakerlake/main run build",
    "dev:renderer": "pnpm exec vite --config apps/renderer/vite.config.ts",
    "dev:watch": "cd apps/main && ..\\..\\node_modules\\.bin\\tsup --watch --config tsup.config.ts",
    "dev:electron": "pnpm exec wait-on -t 90000 tcp:127.0.0.1:5173 && cd apps/main && ..\\..\\node_modules\\.bin\\electron ."
  },
  "devDependencies": {
    "@electron/rebuild": "^4.0.1",
    "concurrently": "^9.2.1",
    "cross-env": "^10.0.0",
    "electron": "31.7.7",
    "wait-on": "^8.0.4"
  },
  "dependencies": {
    "quill": "^1.3.7"
  }
}
```

**Wichtig**: 
- **Monorepo-Struktur**: Workspaces in `apps/*` und `packages/*`
- **Electron 31.7.7**: Desktop-Anwendung parallel zu Streamlit
- **pnpm**: Package Manager für schnellere Installs
- **Vite**: Dev Server für Renderer-Prozess
- **tsup**: TypeScript Bundler für Main-Prozess
- **concurrently**: Parallele Ausführung von dev:renderer + dev:watch + dev:electron

### Dockerfiles (3 Files)

**solar-calculator-pro/frontend/Dockerfile**:
```dockerfile
# Frontend React/TypeScript Container
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --silent

# Copy source
COPY . .

# Build
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**solar-calculator-pro/backend/Dockerfile**:
```dockerfile
# Backend FastAPI Container
FROM python:3.13-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run migrations
RUN alembic upgrade head

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Agent/sandbox/Dockerfile** - Agent Sandbox (bereits dokumentiert, aber erweitert):
```dockerfile
FROM python:3.13-slim

# Security: Non-root user
RUN useradd -m -u 1000 agent

# Install dependencies
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /workspace
RUN chown -R agent:agent /workspace

USER agent

# Resource limits enforced via docker-compose
CMD ["python", "-u", "main.py"]
```

### .gitignore (10 Files)

**Root .gitignore**:
```gitignore
# Python
__pycache__/
*.py[cod]
*.so
*.egg-info/
dist/
build/
.pytest_cache/

# Virtual Environments
venv/
env/
.venv/

# IDEs
.vscode/
.idea/
*.swp

# Databases
*.db
*.sqlite
*.sqlite3

# Environment
.env
.env.local

# Logs
*.log

# OS
.DS_Store
Thumbs.db

# Build outputs
dist/
build/
*.spec

# PDFs (generated)
customer_documents/
output_pdfs/

# Backups
backups/
*.backup

# Node
node_modules/
package-lock.json
yarn.lock

# Streamlit
.streamlit/secrets.toml
```

### .env Configuration (8 Files)

**.env.example** (100+ Zeilen - VOLLSTÄNDIGE API-KEYS-DOKU):
```dotenv
# KAI Agent Configuration
# ========================

# ==============================================================================
# REQUIRED API KEYS
# ==============================================================================

# OpenAI API Key (REQUIRED)
# Get your key from: https://platform.openai.com/api-keys
# Used for: GPT-4 agent reasoning and responses
OPENAI_API_KEY=sk-...

# ==============================================================================
# OPTIONAL API KEYS
# ==============================================================================

# Tavily API Key (Optional)
# Get your key from: https://tavily.com/
# Used for: Web search capabilities
TAVILY_API_KEY=tvly-...

# Twilio Credentials (Optional)
# Get credentials from: https://www.twilio.com/console
# Used for: Telephony features (currently simulated)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...

# ElevenLabs API Key (Optional)
# Get your key from: https://elevenlabs.io/
# Used for: Voice synthesis in telephony
ELEVEN_LABS_API_KEY=...

# ==============================================================================
# CONFIGURATION NOTES
# ==============================================================================
#
# 1. MINIMUM SETUP:
#    - Only OPENAI_API_KEY is required
#
# 2. SECURITY:
#    - Never share API keys
#    - Never commit .env to git
#    - Rotate keys regularly
#
# 3. COST MANAGEMENT:
#    - OpenAI: Charges per token
#    - Tavily: Free tier available
#    - Twilio: Charges per call/SMS
#    - ElevenLabs: Charges per character
#
# 4. VALIDATION:
#    - Run: python Agent/validate_config.py
```

### LICENSE (MIT License 2025)

**LICENSE.txt**:
```text
MIT License

Copyright (c) 2025 Bokuk2 Development Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Assets & Media (659 Files)

**SVG Icons (292 Files)**:
```
_extract_tmp/code/webseite/*_files/
├── head_search.svg
├── head_icon_search_gray.svg
├── head_icon_scart_gray.svg
├── head_icon_phone_gray.svg
├── head_icon_menu_gray.svg
├── head_icon_account_gray.svg
├── logo_shop_small.svg
├── logo_shop_big.svg
├── Gliederheizkoerper.svg
└── ... (280+ weitere Shop-Icons)
```

**PNG Images (358 Files)**:
```
Kategorien:
- data/product_datasheets/ - Produkt-Datenblätter (test_module_3.png)
- tests/ - Screenshot-Tests (test_screenshot_*.png)
- _extract_tmp/code/webseite/ - Shop-Assets:
  - rating-stars.png
  - trustedshops_logo.png
  - trustami_logo.png
  - Payment-Icons (paypalcheckout_*.png)
  - Siegel & Trust-Badges
```

**Video Files (5 Files)**:
```
Videos:
- .streamlit/static/intro_video.mp4 (Streamlit Intro)
- static/intro_videos/Glass Background.mp4 (Glasshintergrund)
- static/intro_videos/intro_video.webm (WebM Standard)
- static/intro_videos/intro_video_small.webm (WebM Komprimiert)
- data/intro_videos/intro_video.mp4 (Data Backup)
```

**App Icons (4 Files)**:
```
Icons:
- app_icon.ico (Root)
- data/Kakerlack.ico (Data)
- data/company_logos/app_icon.ico (Company)
- assets/Kakerlack.ico (Assets)
```

### Database Files (18 .db Files)

**Production Databases**:
```python
# Haupt-Datenbanken
data/app_data.db              # HAUPTDATENBANK (SQLite)
crm_database.db               # CRM separate DB
product_database.db           # Produkte separate DB
data/users.db                 # Benutzer-DB
data/pv_mounting_components.db # PV-Montage-DB
data/pricing_audit.db         # Pricing Audit-Trail

# Backend Databases
backend/solar_calculator.db   # Backend Solar Calc
backend/demo_auth.db          # Demo Auth DB
backend/test_data_api.db      # Test Data API
backend/test_auth.db          # Test Auth

# Agent Database
Agent/data/telephony.db       # Telephony Simulation

# Test Databases (7 Files)
test_migrations.db
tests/test_integration.db
tests/test_primary.db
tests/test_task_8_3.db

# Backups (2 Files)
data/backups/migration_backup_20251108_195359.db
data/backups/migration_backup_20251108_195019.db
data/app_data_backup_logic_20251207_003607.db
```

**Pattern für DB-Zugriff**:
```python
# Multi-Database Pattern
from sqlalchemy import create_engine

class DatabaseManager:
    """Verwaltet mehrere Datenbanken"""
    
    def __init__(self):
        self.databases = {
            'main': create_engine('sqlite:///data/app_data.db'),
            'crm': create_engine('sqlite:///crm_database.db'),
            'products': create_engine('sqlite:///product_database.db'),
            'users': create_engine('sqlite:///data/users.db'),
        }
    
    def get_connection(self, db_name: str = 'main'):
        """Gibt Connection für spezifische DB zurück"""
        engine = self.databases.get(db_name)
        if not engine:
            raise ValueError(f"Unknown database: {db_name}")
        return engine.connect()

# Usage
db_mgr = DatabaseManager()

with db_mgr.get_connection('crm') as conn:
    customers = conn.execute("SELECT * FROM customers")

with db_mgr.get_connection('products') as conn:
    products = conn.execute("SELECT * FROM products")
```

### PyInstaller Specs (3 Files)

**ARSCHIBALD_COMPLETE.spec** (Haupt-Build):
```python
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('de.json', '.'),
        ('locales.py', '.'),
        ('coords_multi', 'coords_multi'),
        ('pdf_templates_static', 'pdf_templates_static'),
        ('.streamlit', '.streamlit'),
        ('data', 'data'),
        ('core', 'core'),
        ('crm', 'crm'),
        ('controlling', 'controlling'),
        ('components', 'components'),
    ],
    hiddenimports=[
        'streamlit.runtime.scriptrunner.magic_funcs',
        'reportlab.pdfgen.canvas',
        'pyvista',
        'langchain',
        # ... 50+ weitere
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Ömers All in One Dingsbums',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='app_icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Ömers All in One Dingsbums'
)
```

### Inno Setup Scripts (7 Files)

**ARSCHIBALD_COMPLETE_SETUP.iss** (Windows Installer):
```pascal
[Setup]
AppName=ARSCHIBALD
AppVersion=2.5.0
DefaultDirName={autopf}\ARSCHIBALD
DefaultGroupName=ARSCHIBALD
OutputDir=Output
OutputBaseFilename=ARSCHIBALD_Setup_v2.5.0
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\Ömers All in One Dingsbums\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\ARSCHIBALD"; Filename: "{app}\Ömers All in One Dingsbums.exe"
Name: "{autodesktop}\ARSCHIBALD"; Filename: "{app}\Ömers All in One Dingsbums.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Ömers All in One Dingsbums.exe"; Description: "{cm:LaunchProgram,ARSCHIBALD}"; Flags: nowait postinstall skipifsilent
```

**Setup-Varianten**:
- `SETUP_SHORT_PATH.iss` - Kurze Pfade für Kompatibilität
- `SETUP_SIMPLE_COPY.iss` - Einfache Kopie ohne Kompression
- `SETUP_FULL_NO_COMPRESSION.iss` - Vollversion ohne Kompression
- `Ömers All in One Dingsbums_setup.iss` - Alternative
- `ARSCHIBALD_setup.iss` - Legacy

### Backend Service Architecture (100+ Classes)

**BaseService Pattern**:
```python
# backend/core/base_service.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from enum import Enum

T = TypeVar('T')

class ServiceStatus(Enum):
    INITIALIZING = "initializing"
    READY = "ready"
    DEGRADED = "degraded"
    OFFLINE = "offline"

class BaseService(ABC, Generic[T]):
    """Base class für alle Backend-Services
    
    Bietet:
    - Lifecycle Management (init, start, stop)
    - Health Checks
    - Dependency Injection
    - Error Handling
    """
    
    def __init__(self):
        self._status = ServiceStatus.INITIALIZING
        self._dependencies = []
    
    @abstractmethod
    async def initialize(self):
        """Service initialisieren"""
        pass
    
    @abstractmethod
    async def health_check(self) -> dict:
        """Health Check durchführen"""
        pass
    
    def get_status(self) -> ServiceStatus:
        """Aktueller Service-Status"""
        return self._status
```

**Service-Implementierungen**:
```python
# backend/services/auth_service.py
class AuthService(BaseService):
    """Authentifizierung & Authorization"""
    
    async def initialize(self):
        self.jwt_secret = os.getenv('JWT_SECRET')
        self._status = ServiceStatus.READY
    
    def create_token(self, user_id: int) -> str:
        return jwt.encode({'user_id': user_id}, self.jwt_secret)

# backend/services/crm_service.py
class CRMService(BaseService):
    """CRM Business Logic"""
    
    def get_customer(self, customer_id: int):
        # Load from database
        pass

# backend/services/pdf_service.py
class PDFGenerationService(BaseService):
    """PDF-Generierung mit Queue"""
    
    async def generate_pdf(self, template: str, data: dict):
        # Queue job
        pass

# backend/services/pricing_service.py
class PricingService(BaseService):
    """Preiskalkulation"""
    
    def calculate_price(self, product_id, quantity):
        # Apply pricing matrix
        pass

# backend/services/solar_service.py
class SolarCalculatorService(BaseService):
    """Solar-Berechnungen"""
    
    def calculate_yield(self, kwp, location):
        # Ertrag berechnen
        pass
```

**Service Discovery Pattern**:
```python
# backend/core/service_registry.py
class ServiceRegistry:
    """Zentrales Service-Registry"""
    
    _services = {}
    
    @classmethod
    def register(cls, name: str, service: BaseService):
        cls._services[name] = service
    
    @classmethod
    def get(cls, name: str) -> BaseService:
        return cls._services.get(name)
    
    @classmethod
    async def start_all(cls):
        """Startet alle registrierten Services"""
        for service in cls._services.values():
            await service.initialize()

# Usage
from backend.services import AuthService, CRMService, PDFGenerationService

ServiceRegistry.register('auth', AuthService())
ServiceRegistry.register('crm', CRMService())
ServiceRegistry.register('pdf', PDFGenerationService())

await ServiceRegistry.start_all()

# In Routes
auth = ServiceRegistry.get('auth')
token = auth.create_token(user_id)
```

### FastAPI Endpoints (200+ Routes)

**Route-Kategorien**:

**1. Additional Components (22 Endpoints)**:
```python
@router.get("/")                              # List all
@router.get("/categories")                    # Categories
@router.get("/wallboxes")                     # Wallboxen
@router.get("/ems")                           # Energy Management
@router.get("/optimizers")                    # Optimizers
@router.get("/emergency-power")               # Notstrom
@router.get("/animal-protection")             # Tierschutz
@router.get("/manufacturers")                 # Hersteller
@router.get("/{component_id}")                # Detail
@router.post("/calculate-optimizer-cost")     # Optimizer-Kosten
@router.post("/calculate-total-cost")         # Gesamtkosten
@router.post("/recommend")                    # Empfehlungen
```

**2. Advanced Charts (12 Endpoints)**:
```python
@router.post("/break-even")                   # Break-Even-Chart
@router.post("/lifecycle-cost")               # Lifecycle-Kosten
@router.post("/monthly-production")           # Monatsproduktion
@router.post("/electricity-projection")       # Strom-Projektion
@router.post("/cumulative-cashflow")          # Kumulativer Cashflow
@router.post("/consumption-coverage")         # Verbrauchsdeckung
@router.post("/pv-usage")                     # PV-Nutzung
@router.get("/types")                         # Chart-Typen
@router.get("/switchers")                     # Chart-Switcher
@router.get("/switchers/{switcher_id}")       # Switcher Detail
@router.post("/switchers/{switcher_id}/select") # Switcher Select
@router.get("/dashboard/complete")            # Komplettes Dashboard
```

**3. 3D Animation (10 Endpoints)**:
```python
@router.post("/rotation-360")                 # 360° Rotation
@router.post("/fly-through")                  # Fly-Through
@router.post("/assembly")                     # Montage-Animation
@router.post("/time-lapse")                   # Time-Lapse
@router.post("/presentation")                 # Präsentation
@router.post("/export")                       # Export
@router.get("/download/{animation_id}")       # Download
@router.get("/{animation_id}/metadata")       # Metadata
@router.delete("/{animation_id}")             # Löschen
```

**4. Admin Dashboard (10 Endpoints)**:
```python
@router.get("/summary")                       # Dashboard Summary
@router.get("/health/system")                 # System Health
@router.get("/health/database")               # DB Health
@router.get("/statistics/usage")              # Usage Stats
@router.get("/metrics/performance")           # Performance Metrics
@router.get("/activity/users")                # User Activity
@router.get("/alerts")                        # Alerts
@router.post("/alerts/{alert_id}/resolve")    # Resolve Alert
@router.get("/metrics/historical")            # Historical Metrics
@router.get("/ping")                          # Ping
```

**5. Application Monitoring (15 Endpoints)**:
```python
@router.get("/metrics")                       # Metrics
@router.get("/metrics/timeseries")            # Timeseries
@router.get("/metrics/prometheus")            # Prometheus Format
@router.get("/alerts")                        # All Alerts
@router.get("/alerts/active")                 # Active Alerts
@router.post("/alerts/{alert_id}/acknowledge") # Acknowledge
@router.post("/alerts/{alert_id}/resolve")    # Resolve
@router.get("/alerts/rules")                  # Alert Rules
@router.post("/alerts/rules")                 # Create Rule
@router.put("/alerts/rules/{rule_id}")        # Update Rule
@router.get("/logs")                          # Logs
@router.get("/logs/stats")                    # Log Stats
@router.get("/dashboards")                    # Dashboards
@router.get("/dashboards/{dashboard_id}")     # Dashboard Detail
@router.post("/dashboards")                   # Create Dashboard
```

**6. API Integration (18 Endpoints)**:
```python
@router.post("/")                             # Create Integration
@router.get("/")                              # List Integrations
@router.get("/{integration_id}")              # Get Integration
@router.put("/{integration_id}")              # Update Integration
@router.delete("/{integration_id}")           # Delete Integration
@router.post("/{integration_id}/oauth/authorize") # OAuth Authorize
@router.post("/{integration_id}/oauth/callback")  # OAuth Callback
@router.post("/{integration_id}/oauth/refresh")   # OAuth Refresh
@router.post("/{integration_id}/test")        # Test Connection
@router.post("/{integration_id}/webhook/test") # Webhook Test
@router.get("/{integration_id}/metrics")      # Integration Metrics
@router.post("/{integration_id}/cache/clear") # Clear Cache
@router.post("/{integration_id}/rate-limit/reset") # Reset Rate Limit
@router.get("/{integration_id}/webhooks")     # List Webhooks
@router.post("/{integration_id}/webhooks/{webhook_id}/retry") # Retry
```

**+130+ weitere Endpoints** in energy_flow, additional_features, etc.

### Repository Pattern (10+ Classes)

**Generic Repository**:
```python
# core/database.py
from typing import Generic, TypeVar, List, Optional
from sqlalchemy.orm import Session

T = TypeVar('T')

class Repository(Generic[T]):
    """Generic Repository für CRUD-Operationen"""
    
    def __init__(self, model_class: type[T], session: Session):
        self.model_class = model_class
        self.session = session
    
    def get(self, id: int) -> Optional[T]:
        """Get by ID"""
        return self.session.query(self.model_class).get(id)
    
    def list(self, skip: int = 0, limit: int = 100) -> List[T]:
        """List with pagination"""
        return self.session.query(self.model_class).offset(skip).limit(limit).all()
    
    def create(self, obj: T) -> T:
        """Create"""
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj
    
    def update(self, obj: T) -> T:
        """Update"""
        self.session.commit()
        self.session.refresh(obj)
        return obj
    
    def delete(self, id: int) -> bool:
        """Delete"""
        obj = self.get(id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
            return True
        return False
```

**Spezifische Repositories**:
```python
# core/session_repository.py
class SessionRepository(Repository[UserSession]):
    """Repository für User Sessions"""
    
    def find_by_token(self, token: str) -> Optional[UserSession]:
        return self.session.query(UserSession).filter_by(token=token).first()

# core/job_repository.py
class JobRepository(Repository[Job]):
    """Repository für Background Jobs"""
    
    def find_pending(self) -> List[Job]:
        return self.session.query(Job).filter_by(status='pending').all()

# core/form_manager.py
class FormRepository(Repository[FormData]):
    """Repository für Form Data"""
    
    def find_by_form_id(self, form_id: str) -> List[FormData]:
        return self.session.query(FormData).filter_by(form_id=form_id).all()
```

### README Documentation (30+ Files)

**Wichtige READMEs**:
```
controlling/README.md             - Controlling System
components/README.md              - UI Components
pricing/README.md                 - Pricing System
crm/README.md                     - CRM Documentation
backend/README.md                 - Backend Architecture
README_BUILD_SYSTEM.md            - Build System Guide
solar-calculator-pro/README.md    - Solar Calculator Pro
solar-calculator-pro/README_TASK_REORGANIZATION.md - Task Reorg
```

**Pattern für README-Struktur**:
```markdown
# Module Name

## Overview
Brief description of module purpose.

## Features
- Feature 1
- Feature 2
- Feature 3

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```python
from module import function
result = function()
```

## Architecture
Description of architecture patterns.

## API Reference
Detailed API documentation.

## Testing
```bash
pytest tests/test_module.py
```

## Contributing
Guidelines for contributors.
```

---

**Letzte Aktualisierung**: 2026-01-03
**Version**: 3.0 - ULTIMATE MEGA EDITION 🚀🔥

**Neu hinzugefügt** (Version 3.0):
- 21 zusätzliche Kategorien mit 3000+ Zeilen Dokumentation
- PowerShell Scripts (8 Files)
- Shell Scripts (2 Files)
- Alembic Configuration (2 Files)
- pyproject.toml (3 Files - Hatchling Build System)
- setup.py (3 Files - 569 Lines Total!)
- package.json (6 Files - Electron Monorepo "kakerlake")
- Dockerfiles (3 Files - Frontend/Backend/Sandbox)
- .gitignore (10 Files)
- .env Configuration (8 Files mit vollständiger API-Keys-Doku)
- LICENSE (MIT License 2025 Bokuk2)
- Assets & Media (659 Files - SVG/PNG/Video/Icons)
- Database Files (18 .db Files - Multi-DB Architecture)
- PyInstaller Specs (3 Files)
- Inno Setup Scripts (7 Files)
- Backend Service Architecture (100+ Classes - BaseService Pattern)
- FastAPI Endpoints (200+ Routes kategorisiert)
- Repository Pattern (10+ Classes - Generic CRUD)
- README Documentation (30+ Files)

**Version 2.0 Features** (bereits vorhanden):
- CSS/Style System (261+ Dateien)
- TypeScript/React Components (327+ TSX, 109+ TS)
- JavaScript Libraries (Chart.js, Clarity.js, Kaleido)
- HTML Templates (5490+ Dateien)
- Enums & Constants (100+)
- YAML Koordinaten-System (94 Dateien)
- Streamlit Configuration (vollständig)
- Sessions & Routing (@dataclass Patterns)
- Testing Infrastructure (789 Test-Dateien)
- Pricing Enhancements (Dynamic Keys, Margin Types)
- Wärmepumpen Advanced Features (JAZ, Noise, Smart Grid, CO2)
- Docker/Container System (Agent Sandbox)
- Backup & Migration System (Alembic + Backup Manager)

**Gesamt-Coverage**: ~10.000 Zeilen Dokumentation, 10.000+ Dateien dokumentiert 🎉

---

## PHASE 4 DISCOVERIES - Version 3.1 Ergänzungen ⚡💎

### Neu gefunden: 7 KRITISCHE Kategorien

**Status**: ✅ Phase 4 Discovery abgeschlossen (27 Tool-Operationen, 7 Major Gaps identifiziert)

---

## Requirements-Dateien (15 Files - 248 Pakete!)

### Haupt-requirements.txt
**Datei**: `requirements.txt` - **248 Zeilen** mit vollständiger Dependency-Spezifikation

**Core Dependencies (Auszug aus 248 Paketen)**:
```
# Streamlit & Web Framework
streamlit==1.49.1
fastapi==0.116.1
uvicorn==0.35.0

# Database & ORM
SQLAlchemy==2.0.43
alembic==1.16.5
duckdb==1.4.0

# Data Processing
pandas==2.3.2
numpy==2.3.2

# PDF Processing (10+ Libraries!)
reportlab==4.4.3
pypdf==6.0.0
PyPDF2==3.0.1
PyPDF3==1.0.6
PyPDF4==1.27.0
pdfplumber==0.11.7
PyMuPDF==1.26.4
pdf2image==1.17.0
pdfminer.six==20250506
pypdfium2==4.30.0
pikepdf>=9.0.0

# 3D Visualization
pyvista>=0.43.10
vtk>=9.3.0
stpyvista>=0.1.4

# AI/Agent Dependencies
langchain==0.3.27
langchain-openai==0.3.0
tavily-python==0.5.0
elevenlabs==2.20.1
faiss-cpu==1.10.0

# Testing
pytest==8.4.2
pytest-asyncio==1.2.0
pytest-cov>=7.0.0

# Monitoring & Tracing
prometheus_client==0.22.1
opentelemetry-api>=1.20.0
opentelemetry-sdk>=1.20.0

# Build & Deployment
pyinstaller==6.15.0
docker==7.1.0
```

**Requirements-Struktur**:
```
requirements.txt                  # Main (248 packages)
requirements_strict.txt           # Pinned versions
requirements_flexible.txt         # Version ranges
backend/requirements.txt          # Backend-specific
Agent/requirements.txt            # Agent-specific
solar-calculator-pro/backend/requirements.txt  # Solar backend
```

---

## GitHub Workflows (7 YAML-Dateien - CI/CD Pipeline)

**Verzeichnis**: `solar-calculator-pro/.github/workflows/`

**Workflows**:
- **ci.yml**: Linting + Testing (Python 3.11/3.12/3.13, ruff, black, mypy, pytest mit coverage)
- **ci-cd.yml**: Build & Deploy (Frontend npm build, Backend python build, Artifact upload)
- **security.yml**: Security Scans (pip-audit, TruffleHog secret detection, CodeQL)
- **performance.yml**: Performance Tests (Locust load testing, pytest benchmarks)
- **release.yml**: Release Automation (GitHub releases, PyInstaller Windows builds)
- **build.yml**: Multi-Platform Builds (Ubuntu/Windows/macOS × Python 3.11/3.12/3.13)
- **pages.yml**: GitHub Pages Deployment

---

## Alembic Migrations (42+ Dateien)

**Verzeichnisse**: 
- `core/alembic/versions/` (1 File)
- `backend/migrations/` (1 File)
- `solar-calculator-pro/backend/migrations/` (40+ Files)

**Migrations-Kategorien**:
- Schema Evolution: universal_columns, user_profile_fields
- Features: i18n_tables, feature_flags, component_toggles
- Security: encryption_tables, audit_tables
- Documents: document_tables, image_tables
- Financial: currency_tables, contract_tables
- CRM: lead_management_tables, company_tables
- Operations: maintenance_tables, api_integration_tables

---

## Test Coverage Configuration

**Datei**: `.coveragerc`

```ini
[run]
source = .
omit = */tests/*, */migrations/*, */alembic/*
branch = True
parallel = True

[report]
precision = 2
exclude_lines = pragma: no cover, if __name__ == .__main__.:
show_missing = True
```

**20+ Test-Klassen entdeckt**:
- Beta Testing: BetaTestingManager, TestBetaBuildDistribution, TestCrashReportMonitoring
- Security Testing: TestAuthenticationSecurity, TestXSSPrevention, TestSQLInjectionPrevention
- UAT: TestSolarCalculatorWorkflow, TestHeatPumpWorkflow, TestCRMWorkflow

---

## Jupyter Notebooks

**Datei**: `Agent/agent_workspace/demodataanalysis/notebooks/01_exploration.ipynb`

**Verwendung**: Data Analysis, Prototyping, Visualisierung für Agent Workspace

---

## i18n/Lokalisierung

**Dateien**: 
- `solar-calculator-pro/frontend/src/i18n/locales/de.json`
- `solar-calculator-pro/frontend/src/i18n/locales/en.json`

**Integration**: React i18next für TypeScript-Frontend mit hierarchischen Keys (common, navigation, solar, crm, validation)

---

## Executable Scripts (20+ CLI-Tools)

**Pattern**: `#!/usr/bin/env python` Shebang

**Kategorien**:
- **Database Tools (9)**: check_products_db.py, check_companies.py, check_price_matrix.py
- **Image Processing (3)**: check_product_image_details.py, add_test_product_images.py
- **Data Management (4)**: add_all_declarations.py, clean_sessions.py
- **Agent Tools (4)**: Agent/build_sandbox.py, Agent/setup_knowledge_base.py

---

## PHASE 5 DISCOVERIES - Version 3.2 MEGA UPDATE 🚀💎🔥

### Neu gefunden: 12 KRITISCHE Kategorien + Massive Backend-Architektur

**Status**: ✅ Phase 5 Discovery ABGESCHLOSSEN (35 Tool-Operationen durchgeführt)

---

## Linting & Code Quality Tools (5 Kategorien)

### .prettierrc Configuration (2 Files)
**Frontend Code-Formatierung**:
```json
// solar-calculator-pro/frontend/.prettierrc
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": false,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "endOfLine": "lf"
}
```

### .eslintrc.cjs Configuration (1 File)
**TypeScript/React Linting**:
```javascript
// solar-calculator-pro/frontend/.eslintrc.cjs
module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh'],
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
  },
}
```

### Ruff Configuration (pyproject.toml)
**Python Linting mit Ruff**:
```toml
[tool.ruff]
target-version = "py311"
line-length = 88
extend-exclude = [
    "archive",
    "tools",
    "tests",
]

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "PIE", "SIM", "RET"]
ignore = ["E501", "B008"]
```

### Black Configuration (pyproject.toml)
**Python Code-Formatierung**:
```toml
[tool.black]
target-version = ["py311"]
line-length = 88
```

### Mypy Configuration (pyproject.toml)
**Python Type Checking**:
```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
```

---

## Vite.js Build System (Frontend)

### vite.config.ts
**Datei**: `solar-calculator-pro/frontend/vite.config.ts`

**React + TypeScript Build-Konfiguration**:
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@services': path.resolve(__dirname, './src/services'),
      '@store': path.resolve(__dirname, './src/store'),
      '@types': path.resolve(__dirname, './src/types'),
      '@utils': path.resolve(__dirname, './src/utils'),
    },
  },
  server: {
    port: 3000,
    strictPort: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    // Manual chunk splitting for better caching
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'primereact-vendor': ['primereact', 'primeicons'],
          'chart-vendor': ['recharts', 'd3-scale', 'd3-shape'],
          '3d-vendor': ['three', '@react-three/fiber', '@react-three/drei'],
          'form-vendor': ['react-hook-form', '@hookform/resolvers', 'zod'],
          'utils-vendor': ['axios', 'socket.io-client', 'zustand'],
        },
      },
    },
    chunkSizeWarningLimit: 1000,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.log in production
        drop_debugger: true,
      },
    },
  },
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'primereact',
      'recharts',
    ],
  },
})
```

**Features**:
- **Path Aliasing**: `@components`, `@hooks`, etc.
- **Code Splitting**: Manuelle Chunk-Aufteilung für besseres Caching
- **Production Optimization**: `drop_console`, `drop_debugger`, Terser Minification
- **Dev Server**: Port 3000, strictPort für Electron-Kompatibilität

---

## PostCSS & TailwindCSS Configuration

### postcss.config.js
**Datei**: `solar-calculator-pro/frontend/postcss.config.js`

**CSS Processing Pipeline**:
```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

### tailwind.config.js
**Datei**: `solar-calculator-pro/frontend/tailwind.config.js`

**TailwindCSS Konfiguration** (ca. 150+ Zeilen):
```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fff7ed',
          100: '#ffedd5',
          500: '#ff7800', // Brand Orange
          600: '#ea580c',
          700: '#c2410c',
        },
        // ... 20+ weitere Farbdefinitionen
      },
      fontFamily: {
        sans: ['Nunito', 'sans-serif'],
      },
      boxShadow: {
        'inner-lg': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
      },
    },
  },
  plugins: [],
}
```

---

## wp_implements Verzeichnis (Wärmepumpen Prototypen)

### Struktur
**Verzeichnis**: `wp_implements/`

**Inhalt**:
```
wp_implements/
├── angebot/
│   └── Angebot Wärmepumpe 2.pdf        # Beispiel-Angebot
├── excel/
│   ├── 1.xlsx - 5.xlsx                  # Excel-Daten
├── heatpump-calculator-main/            # Heat Pump Calculator (JS)
├── jazmax-main/                         # JAZ Calculator (Node.js)
├── heat_pump_calculator.py              # Python-Implementierung
├── heat_pump_ui.py                      # Streamlit UI
├── wp_bridge.py                         # Bridge-Modul
└── WP_implementierung.pdf               # Dokumentation
```

**Zweck**: Prototypen & Referenz-Implementierungen für Wärmepumpen-Berechnungen

---

## MASSIVE Backend API Architecture (160+ Endpoint-Dateien!)

### FastAPI Backend Endpoints (200+ API-Dateien)

**Verzeichnisse**:
- `backend/api/v1/` (23 Dateien)
- `solar-calculator-pro/backend/api/v1/` (158 Dateien) ← **MASSIV!**

**Kategorien** (solar-calculator-pro/backend):

**Admin & Management (10+ Files)**:
- `admin_dashboard.py` - Admin Dashboard API
- `user_role_management.py` - RBAC
- `permissions.py` - Permission Management
- `company_management.py` - Firmen-Verwaltung
- `preferences.py` - Benutzer-Präferenzen

**Database & Data (15+ Files)**:
- `database.py`, `database_management.py` - DB-Management
- `database_backup.py`, `backup_recovery.py` - Backup-System
- `database_optimization.py` - DB-Optimierung
- `database_production.py` - Production-DB
- `database_type.py` - DB-Typ-Handling
- `data_migration.py` - Data-Migration
- `data_privacy.py` - Datenschutz
- `encryption.py` - Verschlüsselung

**CRM & Customer (10+ Files)**:
- `crm_advanced.py`, `crm_dashboard.py` - CRM-Kern
- `customer_data.py` - Kundendaten
- `contracts.py`, `contract_warranty.py` - Verträge
- `leads.py` - Lead-Management
- `pipeline.py` - Sales-Pipeline

**PDF Generation (15+ Files)**:
- `pdf_advanced.py` - Erweiterte PDF-Generierung
- `pdf_archiving.py` - PDF-Archivierung
- `pdf_compression.py` - PDF-Kompression
- `pdf_configuration.py` - PDF-Konfiguration
- `pdf_export.py` - Export-Funktionen
- `pdf_template_system.py` - Template-System
- `batch_pdf.py` - Batch-Generierung
- `multi_offer_pdf.py` - Multi-Angebote
- `extended_pv_pdf.py`, `extended_wp_pdf.py`, `extended_offer_pdf.py` - Erweiterte PDFs
- `standard_pv_pdf.py`, `standard_wp_pdf.py`, `standard_offer_pdf.py` - Standard-PDFs

**3D Visualization (8+ Files)**:
- `animation_3d.py` - 3D-Animationen
- `interactive_3d.py` - Interaktive 3D-Ansicht
- `export_3d.py` - 3D-Export
- `collision_detection.py` - Kollisionserkennung
- `visualization_advanced.py` - Erweiterte Visualisierung
- `visualization_3d_advanced.py` - Advanced 3D Features
- `pv_module_placement.py` - Modul-Platzierung
- `screenshot_export.py` - Screenshot-Export

**Calculations & Analysis (20+ Files)**:
- `calculation_functions.py` - Kern-Berechnungen
- `financial_calculations.py`, `financial_analysis.py` - Finanzanalysen
- `quick_calculation.py` - Schnell-Berechnungen
- `live_calculation.py` - Live-Updates
- `scenario_comparison.py` - Szenario-Vergleiche
- `tariff_optimization.py`, `tariff_management.py` - Tarif-Optimierung
- `shading.py` - Verschattungs-Analyse
- `weather.py` - Wetter-Integration
- `pvgis_integration.py` - PVGIS API
- `results_dashboard.py`, `results_visualization.py` - Ergebnis-Visualisierung
- `result_history.py` - Historie

**Heatpump APIs (5 Files)**:
- `heatpump_building.py` - Gebäude-Analyse
- `heatpump_financing.py` - Finanzierung
- `heatpump_models.py` - Modelle
- `heatpump_products.py` - Produkte
- `heatpump_results.py` - Ergebnisse

**Products & Pricing (20+ Files)**:
- `product_management.py`, `product_advanced.py` - Produkt-Verwaltung
- `product_import_export.py` - Import/Export
- `product_rotation.py` - Produkt-Rotation
- `pricing.py`, `pricing_advanced.py` - Preiskalkulation
- `price_matrix_management.py` - Matrix-Verwaltung
- `price_matrix_validation.py` - Validierung
- `price_matrix_versioning.py` - Versionierung
- `price_matrix_performance.py` - Performance-Optimierung
- `price_matrix_extras.py` - Extras
- `price_increase.py` - Preiserhöhungen
- `catalog.py` - Produkt-Katalog
- `inventory.py` - Inventar
- `pv_modules.py`, `inverters.py`, `battery.py` - Komponenten

**Monitoring & System (15+ Files)**:
- `monitoring.py`, `performance_monitoring.py` - Monitoring
- `application_monitoring.py` - App-Monitoring
- `audit.py` - Audit-Trail
- `security_audit.py` - Security-Audit
- `performance_tuning.py` - Performance-Tuning
- `scalability.py` - Skalierbarkeit
- `load_balancing.py` - Load-Balancing
- `caching_system.py` - Caching
- `background_jobs.py` - Background Jobs
- `regression_testing.py` - Regression-Tests
- `maintenance.py`, `maintenance_updates.py` - Wartung

**Integration & External (10+ Files)**:
- `api_integration.py` - API-Integration
- `integrations.py` - Externe Integrationen
- `google_calendar.py` - Google Calendar
- `notifications.py` - Benachrichtigungen
- `sync.py` - Synchronisation
- `import_export.py` - Import/Export
- `deployment_automation.py` - Deployment-Automation
- `environment_config.py` - Umgebungs-Konfiguration

**Additional Features (20+ Files)**:
- `additional_features.py`, `additional_components.py` - Zusatz-Features
- `advanced_charts.py` - Erweiterte Charts
- `battery_storage.py` - Batterie-Speicher
- `building_geometry.py` - Gebäude-Geometrie
- `combined_system.py` - Kombinierte Systeme
- `component_toggles.py` - Feature-Toggles
- `branding.py` - Branding
- `companies.py` - Firmen
- `currency.py` - Währungs-Konvertierung
- `documents.py` - Dokumenten-Verwaltung
- `energy_flow_visualization.py` - Energie-Fluss
- `exports.py` - Export-Funktionen
- `feature_flags.py` - Feature-Flags
- `final_integration.py` - Finale Integration
- `grid_integration.py` - Netz-Integration
- `help_documentation.py` - Hilfe-Dokumentation
- `i18n.py` - Internationalisierung
- `images.py` - Bild-Verwaltung
- `launch_support.py` - Launch-Support
- `license.py` - Lizenz-Verwaltung
- `mounting_system.py` - Montage-System
- `navigation_system.py` - Navigation
- `news_portal.py` - News-Portal
- `module_features.py` - Modul-Features
- `migration.py` - Migration-API
- `pdf_preview_debug.py` - PDF-Preview-Debug
- `pv_heatpump_integration.py` - PV+WP Integration
- `production_config.py` - Production-Konfiguration
- `reporting.py`, `reports.py` - Reporting
- `search.py` - Suche
- `system_config.py`, `system_settings.py` - System-Einstellungen
- `theme_system.py` - Theme-System
- `ui_components.py`, `ui_components_interactive.py` - UI-Komponenten
- `user_feedback_integration.py` - Benutzer-Feedback
- `users.py` - Benutzer-Verwaltung

**TOTAL**: 158 API-Dateien im solar-calculator-pro Backend! 🚀

---

## Admin UI Module (67+ Dateien)

**Root Admin-Dateien** (22 Files mit ~50.000 Zeilen Code!):
- `admin_panel.py` (4749 Zeilen) - Haupt-Admin-Interface
- `admin_panel_shadcn.py` - Shadcn-UI Variante
- `admin_core_status_extended_ui.py` - Extended Core Status
- `admin_core_status_ui.py` - Core Status Dashboard
- `admin_product_database_ui.py` - Produktdatenbank
- `admin_product_database_ui_optimized.py` - Optimierte Version mit Pagination
- `admin_heatpump_products_optimized.py` - Wärmepumpen-Produkte
- `admin_heatpump_settings_ui.py` - Wärmepumpen-Einstellungen
- `admin_heating_costs_config_ui.py` - Heizkosten-Konfiguration
- `admin_controlling_settings_ui.py` - Controlling-Settings
- `admin_intro_settings_ui.py` - Intro-Settings
- `admin_logo_management_ui.py` - Logo-Verwaltung
- `admin_logo_positions_ui.py` - Logo-Positionierung
- `admin_brand_logo_management_ui.py` - Brand-Logo-Management
- `admin_pdf_settings_ui.py` - PDF-Einstellungen
- `admin_payment_terms_ui.py` - Zahlungsbedingungen
- `admin_price_matrix_upload.py` - Preis-Matrix-Upload
- `admin_pricing_rule_ui.py` - Pricing-Regeln
- `admin_profit_margin_ui.py` - Gewinnmargen
- `admin_pv_mounting_tab.py`, `admin_pv_mounting_ui.py` - PV-Unterkonstruktion
- `admin_services_ui.py` - Dienstleistungen
- `admin_ui_effects_settings.py` - UI-Effekte
- `admin_user_management_ui.py` - Benutzerverwaltung
- `admin_security.py` (358 Zeilen) - Security-Layer
- `admin_product_attributes_ui.py` - Produkt-Attribute
- `admin_module_alias_mapping_ui.py` - Modul-Alias-Mapping
- `admin_build_infos_ui.py` - Build-Informationen

**Pattern - Optimized vs Legacy**:
```python
# admin_panel.py Pattern
try:
    from admin_product_database_ui_optimized import render_product_admin_ui_optimized as render_product_admin_ui
    PRODUCT_DB_OPTIMIZED = True
    print("✓ Produktverwaltung OPTIMIERT geladen (mit Pagination)")
except ImportError:
    from admin_product_database_ui import render_product_admin_ui
    PRODUCT_DB_OPTIMIZED = False
    print("⚠ Produktverwaltung ALTE VERSION geladen")
```

**Monitoring Integration**:
```python
try:
    from app_tracing import app_tracer
    from app_evaluation import track_success, track_error
    MONITORING_AVAILABLE = True
    
    def trace_admin(func):
        """Decorator for admin panel operations tracing."""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            operation_name = f"admin.{func.__name__}"
            try:
                result = func(*args, **kwargs)
                track_success(operation_name)
                evaluate_performance(operation_name, time.time() - start_time)
                return result
            except Exception as e:
                track_error(operation_name, str(e))
                raise
        return wrapper
except ImportError:
    MONITORING_AVAILABLE = False
    def trace_admin(func): return func
```

---

## Streamlit Advanced Config

### .streamlit/config.toml (erweitert)
**Datei**: `.streamlit/config.toml` (80+ Zeilen vollständige Konfiguration)

**Kritische Einstellungen**:
```toml
[server]
headless = false                     # Browser öffnet automatisch
fileWatcherType = "poll"             # Stabilität: "poll" statt "auto"
enableCORS = true
enableXsrfProtection = true
maxUploadSize = 512                  # MB
runOnSave = false                    # WICHTIG: Kein Auto-Reload (Stabilität!)
enableStaticServing = true           # Statische Dateien effizienter
enableWebsocketCompression = true    # Performance
port = 8501
maxMessageSize = 500                 # Max WebSocket Message Size in MB

[browser]
gatherUsageStats = true            # WICHTIG: Kein Telemetry!

[client]
showErrorDetails = true
toolbarMode = "developer"            # "minimal" für Production!
showSidebarNavigation = true

[runner]
magicEnabled = true
fastReruns = true                    # Schnellere Reruns
postScriptGC = true                  # Garbage Collection nach Script
enforceSerializableSessionState = true  # Pickle-Warnings für Session State

[theme]
base = "light"
primaryColor = "#ff7800"             # Brand Orange
backgroundColor = "#d8dce1"
secondaryBackgroundColor = "#e5e7ea"
textColor = "#1a202c"
font = "Nunito, sans-serif"
baseFontSize = 16

[[theme.fontFaces]]
family = "Nunito"
url = "https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&display=swap"

[logger]
level = "error"
enableRich = false                   # Einfaches Logging (weniger Overhead)

[global]
developmentMode = false              # Production-Modus
showWarningOnDirectExecution = false
```

**Wichtig**:
- `runOnSave = false` → Verhindert ständige Reruns (Stabilität!)
- `gatherUsageStats = false` → Datenschutz!
- `toolbarMode = "developer"` → Für Production auf `"minimal"` setzen!
- `enforceSerializableSessionState = true` → Pickle-Warnings für Session State

---

## Desktop.ini & Weitere System-Dateien

### desktop.ini
**Datei**: Root-Verzeichnis

**Windows Folder Customization**:
```ini
[.ShellClassInfo]
IconResource=C:\WINDOWS\System32\SHELL32.dll,3
[ViewState]
Mode=
Vid=
FolderType=Generic
```

---

**Letzte Aktualisierung**: 2026-01-03
**Version**: 3.2 - MEGA ULTRA SUPREME EDITION 🚀🔥💎✨🎉

**Neu hinzugefügt** (Version 3.2):
- Linting & Code Quality Tools (5 Kategorien: Prettier, ESLint, Ruff, Black, Mypy)
- Vite.js Build System (vollständige Konfiguration mit Code-Splitting)
- PostCSS & TailwindCSS Configuration (CSS-Processing-Pipeline)
- wp_implements Verzeichnis (Wärmepumpen-Prototypen & Excel-Daten)
- **MASSIVE Backend API Architecture** (160+ Endpoint-Dateien, 158 im solar-calculator-pro!)
- Admin UI Module (67+ Dateien mit ~50.000 Zeilen Code!)
- Streamlit Advanced Config (vollständige .streamlit/config.toml Dokumentation)
- desktop.ini & System-Dateien

**Version 3.1 Features** (bereits vorhanden):
- Requirements-Dateien (15 Files, 248 Pakete)
- GitHub Workflows (7 CI/CD YAML-Dateien)
- Alembic Migrations (42+ Dateien)
- Test Coverage Configuration (.coveragerc + 20+ Test-Klassen)
- Jupyter Notebooks (Data Analysis)
- i18n/Lokalisierung (Deutsch/Englisch)
- Executable Scripts (20+ CLI-Tools)

**Gesamt-Coverage**: ~14.800 Zeilen Dokumentation, 10.000+ Dateien dokumentiert, **53 Kategorien total** 🎉💯🚀💥

**API-Endpoints dokumentiert**: 200+ FastAPI Routes über 160+ Dateien!
