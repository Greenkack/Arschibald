# Copilot Instructions - ARSCHIBALD (Bokuk2)

## Project Overview
**ARSCHIBALD** ist eine Enterprise-Anwendung für Photovoltaik- und Wärmepumpen-Konfiguration mit automatisierter PDF-Angebotserstellung, 3D-Visualisierung und CRM-Integration. Haupteinstiegspunkt: `gui.py` (Streamlit Multi-Page-App).

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
2. `rotate_products()` variiert Hersteller/Modelle zwischen Firmen
3. `calculate_price_with_products()` berechnet kaskadierende Preise (Firma 1: +15%, weitere: +5% progressiv)
4. `generate_multi_firm_pdf()` erstellt firma-spezifische PDFs mit `coords_multi/` und `multi/` Templates

### 2. Database System (SQLite)
**Hauptdatei**: `database.py` (2900+ Zeilen) - Zentrales Datenbank-Modul

**Tabellen-Struktur**:
- **CRM**: `customers`, `projects`, `crm_leads`, `crm_tasks`, `crm_activities`
- **Produkte**: `products` (PV-Module, Wechselrichter, Speicher, etc.)
- **Preise**: `price_matrices`, `pricing_rules`, `profit_margins`
- **PDF-Archiv**: `customer_documents`, `project_calculations`
- **Verträge**: `contracts`, `warranties` (siehe `crm/features/contract_manager.py`)

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

### 3. Streamlit Session State Management
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

## Developer Workflows

### Running the App
```powershell
# Standard Start
streamlit run gui.py

# Mit spezifischem Port
$env:STREAMLIT_SERVER_PORT="8502"; streamlit run gui.py

# Admin Panel (Extended Dashboard)
streamlit run admin_core_status_extended_ui.py
```

**Config**: `.streamlit/config.toml`
- `headless = false` → Browser öffnet automatisch
- `gatherUsageStats = false` → Kein Telemetry
- `toolbarMode = "minimal"` → Produktions-UI ohne Dev-Toolbar

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
**IMMER** deutsche Formatierung für Währung/Zahlen:
```python
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

### 5. shadcn-ui Integration (Optional)
**Datei**: `components/shadcn_ui_integration.py`

Fallback-Pattern für UI-Komponenten:
```python
from components.shadcn_ui_integration import button, card

# Nutzt streamlit-shadcn-ui wenn verfügbar, sonst native Streamlit
if button("Speichern", key="save_btn"):
    # Action
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

## Critical Gotchas

### PDF System
1. **Koordinaten-System**: ReportLab nutzt Bottom-Left Origin, YAML speichert (x1, y1, x2, y2)
2. **Multi-Firma-Pfade**: Template-Suffix muss `f{index+1}` sein (f1, f2, nicht f0, f1)
3. **Rechtsbündigkeit**: Preisfelder MÜSSEN in `right_align_tokens_s7` Liste für korrekte €-Ausrichtung
4. **Font-Namen**: Nur ReportLab-Fonts nutzen (Helvetica, Helvetica-Bold, Times-Roman, etc.)

### Database
1. **Row Factory**: Vergiss NIEMALS `conn.row_factory = sqlite3.Row`
2. **Migrations**: Nutze `PRAGMA table_info()` + `ALTER TABLE` NICHT `DROP TABLE`
3. **Transactions**: Immer `conn.commit()` bei INSERT/UPDATE/DELETE

### Streamlit
1. **Session State**: Custom Classes brauchen `__getstate__` / `__setstate__`
2. **Widget Keys**: Eindeutige Keys für alle Widgets (`key=f"btn_{id}"`)
3. **Rerun**: Nach Session State Änderung: `st.rerun()` NICHT `st.experimental_rerun()`

### CRM
1. **Kunden/Projekte**: Getrennte Tabellen mit Foreign Key `customer_id`
2. **Dokumente**: File-System Ablage in `customer_documents/` PLUS DB-Referenz
3. **View Modes**: Navigation via `st.session_state['crm_view_mode']`

## Key Files Reference

**Entry Points**:
- `gui.py` - Haupt-Streamlit-App (3000+ Zeilen)
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

## Dependencies (Key)
- **Streamlit 1.49.1** - Web Framework
- **ReportLab 4.4.3** - PDF-Generierung
- **PyPDF2 / pypdf** - PDF-Merge
- **SQLite3** (builtin) - Datenbank
- **pandas 2.2.3** - Datenverarbeitung
- **pyvista 0.43+** - 3D-Visualisierung
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

---

**Letzte Aktualisierung**: 2025-01-18
**Version**: 1.0
