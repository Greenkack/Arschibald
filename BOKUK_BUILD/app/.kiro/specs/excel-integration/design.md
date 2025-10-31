# Design Document

## Overview

Das Excel-Integration-System erweitert die bestehende Streamlit-Anwendung um eine vollständige Excel-ähnliche Funktionalität. Das System nutzt die bereits vorhandene `price_matrix_store.py` Infrastruktur und erweitert diese um eine interaktive Grid-Oberfläche, eine Formel-Engine und Import/Export-Funktionen.

### Hauptziele

1. Nahtlose Integration in das bestehende Admin Panel
2. 100% Excel-Formel-Kompatibilität mit den bereits vorhandenen Python-Funktionen
3. Performante Handhabung großer Datensätze
4. Intuitive Benutzeroberfläche ohne Schulungsbedarf

### Technologie-Stack

- **Frontend**: Streamlit mit ag-Grid oder Streamlit-DataEditor
- **Backend**: Python mit pandas für Datenmanipulation
- **Formel-Engine**: Bestehende `excel/python_function_recipes.py` erweitern
- **Persistenz**: SQLite über bestehende `price_matrix_store.py`
- **Import/Export**: pandas, openpyxl, xlrd

## Architecture

### Komponenten-Übersicht

```
┌─────────────────────────────────────────────────────────────┐
│                     Admin Panel UI                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Preis Matrix Tab (Neues Menü)                       │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │  Excel Grid Component                          │  │  │
│  │  │  - Toolbar (Save, Load, Import, Export)        │  │  │
│  │  │  - Formula Bar                                  │  │  │
│  │  │  - Grid (Cells, Rows, Columns)                 │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Excel Manager (excel_manager.py)               │
│  - Grid State Management                                    │
│  - Cell Value Updates                                       │
│  - Formula Parsing & Execution                              │
│  - Undo/Redo Stack                                          │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│  Formula Engine          │  │  Price Matrix Store      │
│  (excel_formula_engine)  │  │  (price_matrix_store.py) │
│  - Parse Formulas        │  │  - CRUD Operations       │
│  - Execute Functions     │  │  - Database Access       │
│  - Dependency Graph      │  │  - Export/Import         │
└──────────────────────────┘  └──────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────┐
│         Excel Function Library                               │
│         (excel/python_function_recipes.py - erweitert)       │
│  - Mathematische Funktionen (SUM, AVERAGE, etc.)             │
│  - Logische Funktionen (IF, AND, OR, etc.)                   │
│  - Lookup-Funktionen (VLOOKUP, HLOOKUP, etc.)                │
│  - Datums-/Textfunktionen                                    │
└──────────────────────────────────────────────────────────────┘
```


## Components and Interfaces

### 1. Admin Panel Integration (`admin_panel.py`)

**Erweiterung des bestehenden Admin Panels:**

```python
# Neuer Tab-Key in ADMIN_TAB_KEYS_DEFINITION_GLOBAL
ADMIN_TAB_KEYS_DEFINITION_GLOBAL = [
    "admin_tab_company_management_new",
    "admin_tab_product_management",
    "admin_tab_logo_management",
    "admin_tab_product_database_crud",
    "admin_tab_services_management",
    "admin_tab_price_matrix",  # NEU
    "admin_tab_general_settings",
    # ... rest
]
```

**Integration Point:**
- Neuer Tab wird in der bestehenden Tab-Struktur eingefügt
- Verwendet `_render_stateful_selector` für konsistente Navigation
- Lädt `excel_grid_ui.py` Komponente

### 2. Excel Grid UI Component (`excel_grid_ui.py`)

**Hauptkomponente für die Grid-Darstellung:**

```python
def render_excel_grid_ui():
    """
    Hauptfunktion für Excel-Grid-Oberfläche
    
    Features:
    - Matrix-Auswahl (Dropdown)
    - Toolbar (Neu, Speichern, Laden, Import, Export)
    - Formelleiste
    - Grid-Darstellung
    - Zell-Bearbeitung
    """
    
    # Matrix-Auswahl
    matrices = list_matrices()
    selected_matrix = st.selectbox("Matrix auswählen", matrices)
    
    # Toolbar
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("Neue Matrix"):
            create_new_matrix_dialog()
    with col2:
        if st.button("Speichern"):
            save_current_matrix()
    # ... weitere Buttons
    
    # Formelleiste
    render_formula_bar()
    
    # Grid
    render_grid(selected_matrix)
```

**Grid-Rendering-Optionen:**

Option A: **Streamlit Data Editor** (Empfohlen für MVP)
- Native Streamlit-Komponente
- Einfache Integration
- Gute Performance für mittelgroße Tabellen
- Eingeschränkte Anpassungsmöglichkeiten

Option B: **ag-Grid** (Für erweiterte Features)
- Professionelle Grid-Komponente
- Volle Excel-ähnliche Features
- Bessere Performance bei großen Daten
- Komplexere Integration

### 3. Excel Manager (`excel_manager.py`)

**Zentrale Logik-Schicht:**

```python
class ExcelManager:
    """
    Verwaltet den Zustand und die Operationen einer Excel-Matrix
    """
    
    def __init__(self, matrix_id: int):
        self.matrix_id = matrix_id
        self.data = self._load_matrix()
        self.formula_engine = FormulaEngine()
        self.undo_stack = []
        self.redo_stack = []
    
    def get_cell_value(self, row: int, col: int) -> Any:
        """Gibt den Wert einer Zelle zurück"""
        
    def set_cell_value(self, row: int, col: int, value: Any):
        """Setzt den Wert einer Zelle und triggert Neuberechnung"""
        
    def parse_and_execute_formula(self, formula: str) -> Any:
        """Parst und führt eine Formel aus"""
        
    def add_row(self, position: int = None):
        """Fügt eine neue Zeile hinzu"""
        
    def add_column(self, position: int = None):
        """Fügt eine neue Spalte hinzu"""
        
    def delete_row(self, row: int):
        """Löscht eine Zeile"""
        
    def delete_column(self, col: int):
        """Löscht eine Spalte"""
        
    def undo(self):
        """Macht letzte Änderung rückgängig"""
        
    def redo(self):
        """Wiederholt rückgängig gemachte Änderung"""
```


### 4. Formula Engine (`excel_formula_engine.py`)

**Formel-Parser und -Executor:**

```python
class FormulaEngine:
    """
    Parst und führt Excel-Formeln aus
    """
    
    def __init__(self):
        self.functions = self._load_excel_functions()
        self.dependency_graph = {}
    
    def parse_formula(self, formula: str) -> dict:
        """
        Parst eine Formel und extrahiert:
        - Funktionsname
        - Argumente
        - Zellreferenzen
        - Bereiche
        
        Beispiel: "=SUM(A1:A10)" -> {
            'function': 'SUM',
            'args': ['A1:A10'],
            'cell_refs': ['A1', 'A2', ..., 'A10']
        }
        """
        
    def execute_formula(self, formula: str, context: dict) -> Any:
        """
        Führt eine Formel aus
        
        Args:
            formula: Die Formel (z.B. "=SUM(A1:A10)")
            context: Dict mit Zellwerten {('A', 1): 10, ('A', 2): 20, ...}
        
        Returns:
            Berechnetes Ergebnis oder Fehlerwert
        """
        
    def build_dependency_graph(self, cells: dict):
        """
        Erstellt einen Abhängigkeitsgraphen für effiziente Neuberechnung
        """
        
    def recalculate_affected_cells(self, changed_cell: tuple):
        """
        Berechnet alle von einer Änderung betroffenen Zellen neu
        """
```

**Formel-Parsing-Strategie:**

1. **Regex-basiertes Parsing** für einfache Formeln
2. **AST (Abstract Syntax Tree)** für komplexe verschachtelte Formeln
3. **Verwendung der bestehenden `python_function_recipes.py`** Funktionen

**Unterstützte Formel-Syntax:**

```
=SUM(A1:A10)                    # Bereich
=A1+B1                          # Arithmetik
=IF(A1>10, "Ja", "Nein")       # Logik
=VLOOKUP(A1, B1:C10, 2, FALSE) # Lookup
=SUM(A1:A10)*0.19              # Kombiniert
```

### 5. Data Models

**Cell Model:**

```python
@dataclass
class Cell:
    row: int
    col: int
    value: Any = None
    formula: str = None
    formatted_value: str = None
    data_type: str = "text"  # text, number, date, formula
    style: dict = None
    
    def is_formula(self) -> bool:
        return self.formula is not None and self.formula.startswith('=')
    
    def get_display_value(self) -> str:
        if self.formatted_value:
            return self.formatted_value
        return str(self.value) if self.value is not None else ""
```

**Matrix Model:**

```python
@dataclass
class ExcelMatrix:
    id: int
    name: str
    description: str
    rows: List[Row]
    columns: List[Column]
    cells: Dict[Tuple[int, int], Cell]
    metadata: dict
    
    def get_cell(self, row: int, col: int) -> Cell:
        return self.cells.get((row, col), Cell(row, col))
    
    def set_cell(self, row: int, col: int, cell: Cell):
        self.cells[(row, col)] = cell
    
    def to_dataframe(self) -> pd.DataFrame:
        """Konvertiert Matrix zu pandas DataFrame"""
```


## Error Handling

### Formel-Fehler

**Fehlertypen und Behandlung:**

```python
class FormulaError(Exception):
    """Basis-Klasse für Formel-Fehler"""
    pass

class SyntaxError(FormulaError):
    """Syntaxfehler in Formel"""
    display = "#ERROR!"

class ReferenceError(FormulaError):
    """Ungültige Zellreferenz"""
    display = "#REF!"

class DivisionByZeroError(FormulaError):
    """Division durch Null"""
    display = "#DIV/0!"

class CircularReferenceError(FormulaError):
    """Zirkelbezug erkannt"""
    display = "#CIRCULAR!"

class NameError(FormulaError):
    """Unbekannte Funktion"""
    display = "#NAME?"

class ValueError(FormulaError):
    """Falscher Wert-Typ"""
    display = "#VALUE!"
```

**Fehlerbehandlung in der UI:**

1. Fehler werden in der Zelle als Text angezeigt (z.B. "#DIV/0!")
2. Tooltip zeigt detaillierte Fehlermeldung
3. Fehlerhafte Zellen werden farblich markiert
4. Fehler-Log für Debugging

### Validierung

**Input-Validierung:**

```python
def validate_cell_input(value: str, expected_type: str) -> Tuple[bool, Any, str]:
    """
    Validiert Benutzereingabe
    
    Returns:
        (is_valid, parsed_value, error_message)
    """
    if value.startswith('='):
        # Formel-Validierung
        try:
            parse_formula(value)
            return (True, value, "")
        except FormulaError as e:
            return (False, None, str(e))
    
    # Typ-Validierung
    if expected_type == "number":
        try:
            parsed = float(value.replace(',', '.'))
            return (True, parsed, "")
        except ValueError:
            return (False, None, "Ungültige Zahl")
    
    return (True, value, "")
```

## Testing Strategy

### Unit Tests

**Test-Bereiche:**

1. **Formel-Engine Tests** (`test_formula_engine.py`)
   - Alle Excel-Funktionen einzeln testen
   - Verschachtelte Formeln
   - Fehlerbehandlung
   - Edge Cases

2. **Excel Manager Tests** (`test_excel_manager.py`)
   - CRUD-Operationen
   - Undo/Redo
   - Dependency Graph
   - Performance

3. **Import/Export Tests** (`test_import_export.py`)
   - CSV Import/Export
   - Excel Import/Export
   - Formel-Erhaltung
   - Große Dateien

**Beispiel-Test:**

```python
def test_sum_formula():
    engine = FormulaEngine()
    context = {
        ('A', 1): 10,
        ('A', 2): 20,
        ('A', 3): 30
    }
    result = engine.execute_formula("=SUM(A1:A3)", context)
    assert result == 60

def test_nested_formula():
    engine = FormulaEngine()
    context = {
        ('A', 1): 10,
        ('B', 1): 20
    }
    result = engine.execute_formula("=IF(A1>5, SUM(A1:B1), 0)", context)
    assert result == 30
```

### Integration Tests

1. **End-to-End Workflow Tests**
   - Matrix erstellen → Daten eingeben → Formeln → Speichern → Laden
   - Import → Bearbeiten → Export
   - Produktpreis-Integration

2. **Performance Tests**
   - 1000 Zeilen × 50 Spalten
   - 100 Formeln mit Abhängigkeiten
   - Import großer Dateien

### Manual Testing Checklist

- [ ] Neue Matrix erstellen
- [ ] Zeilen/Spalten hinzufügen/löschen
- [ ] Zellwerte eingeben
- [ ] Formeln eingeben und validieren
- [ ] Undo/Redo testen
- [ ] Matrix speichern und laden
- [ ] CSV importieren
- [ ] Excel importieren
- [ ] Export testen
- [ ] Produktpreis-Integration
- [ ] Fehlerbehandlung
- [ ] Performance mit großen Daten


## Performance Optimization

### Caching-Strategie

```python
class CachedFormulaEngine:
    """
    Formel-Engine mit Caching für bessere Performance
    """
    
    def __init__(self):
        self.formula_cache = {}  # {formula_str: result}
        self.dependency_cache = {}  # {cell: [dependent_cells]}
    
    def execute_with_cache(self, formula: str, context: dict) -> Any:
        # Cache-Key aus Formel + relevanten Zellwerten
        cache_key = self._build_cache_key(formula, context)
        
        if cache_key in self.formula_cache:
            return self.formula_cache[cache_key]
        
        result = self.execute_formula(formula, context)
        self.formula_cache[cache_key] = result
        return result
    
    def invalidate_cache(self, changed_cells: List[tuple]):
        """Invalidiert Cache für betroffene Zellen"""
        for cell in changed_cells:
            affected = self.dependency_cache.get(cell, [])
            for affected_cell in affected:
                # Entferne aus Cache
                self._remove_from_cache(affected_cell)
```

### Lazy Loading

```python
class LazyGrid:
    """
    Grid mit Lazy Loading für große Datensätze
    """
    
    def __init__(self, matrix_id: int):
        self.matrix_id = matrix_id
        self.visible_range = (0, 100)  # Nur sichtbare Zeilen laden
        self.loaded_cells = {}
    
    def load_visible_cells(self, start_row: int, end_row: int):
        """Lädt nur sichtbare Zellen"""
        if (start_row, end_row) == self.visible_range:
            return  # Bereits geladen
        
        self.visible_range = (start_row, end_row)
        # Lade nur benötigte Zellen aus DB
        self.loaded_cells = self._load_cells_range(start_row, end_row)
```

### Batch Operations

```python
def batch_update_cells(updates: List[Tuple[int, int, Any]]):
    """
    Aktualisiert mehrere Zellen in einer Transaktion
    
    Args:
        updates: Liste von (row, col, value) Tupeln
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        for row, col, value in updates:
            cur.execute(
                "UPDATE price_matrix_cells SET value=? WHERE row_id=? AND column_id=?",
                (value, row, col)
            )
        conn.commit()
    finally:
        conn.close()
```

## Import/Export Implementation

### CSV Import

```python
def import_csv(file_path: str, matrix_name: str) -> int:
    """
    Importiert CSV-Datei als neue Matrix
    
    Unterstützt:
    - Verschiedene Delimiter (;, ,, \t)
    - Encoding-Erkennung (UTF-8, Latin-1)
    - Formeln (wenn mit = beginnen)
    """
    # Encoding erkennen
    encoding = detect_encoding(file_path)
    
    # CSV lesen
    df = pd.read_csv(file_path, encoding=encoding, delimiter=';')
    
    # Matrix erstellen
    matrix_id = create_matrix(matrix_name)
    
    # Spalten hinzufügen
    for col_name in df.columns:
        add_column(matrix_id, col_name)
    
    # Zeilen und Zellen hinzufügen
    for idx, row in df.iterrows():
        row_id = add_row(matrix_id, str(idx))
        for col_idx, value in enumerate(row):
            if pd.notna(value):
                set_cell_value(matrix_id, row_id, col_idx, value)
    
    return matrix_id
```

### Excel Import

```python
def import_excel(file_path: str, matrix_name: str, sheet_name: str = None) -> int:
    """
    Importiert Excel-Datei (.xls, .xlsx)
    
    Features:
    - Mehrere Sheets (optional)
    - Formeln werden erkannt und übernommen
    - Formatierung wird ignoriert (nur Werte)
    """
    # Excel lesen mit openpyxl für Formel-Support
    wb = openpyxl.load_workbook(file_path, data_only=False)
    
    if sheet_name:
        ws = wb[sheet_name]
    else:
        ws = wb.active
    
    matrix_id = create_matrix(matrix_name)
    
    # Spalten aus erster Zeile
    first_row = list(ws.iter_rows(min_row=1, max_row=1, values_only=True))[0]
    for col_name in first_row:
        add_column(matrix_id, str(col_name))
    
    # Daten ab Zeile 2
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=False)):
        row_id = add_row(matrix_id, str(row_idx))
        
        for col_idx, cell in enumerate(row):
            if cell.value is not None:
                # Prüfe ob Formel
                if isinstance(cell, openpyxl.cell.cell.Cell) and cell.data_type == 'f':
                    # Formel speichern
                    formula = f"={cell.value}"
                    set_cell_value(matrix_id, row_id, col_idx, None, raw_input=formula)
                else:
                    # Wert speichern
                    set_cell_value(matrix_id, row_id, col_idx, cell.value)
    
    return matrix_id
```

### Export

```python
def export_to_excel(matrix_id: int, file_path: str):
    """
    Exportiert Matrix als Excel-Datei mit Formeln
    """
    full = get_matrix_full(matrix_id)
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = full['meta']['name']
    
    # Header
    for col_idx, col in enumerate(full['columns'], start=1):
        ws.cell(1, col_idx, col['label'])
    
    # Daten
    for row_idx, row in enumerate(full['rows'], start=2):
        ws.cell(row_idx, 1, row['label'])
        
        for col_idx, col in enumerate(full['columns'], start=2):
            cell_data = full['cells'].get((row['id'], col['id']))
            
            if cell_data:
                if cell_data.get('raw_input') and cell_data['raw_input'].startswith('='):
                    # Formel
                    ws.cell(row_idx, col_idx, cell_data['raw_input'])
                else:
                    # Wert
                    ws.cell(row_idx, col_idx, cell_data.get('value'))
    
    wb.save(file_path)
```

## Integration with Product Pricing

### Produktpreis-Berechnung aus Matrix

```python
def calculate_product_price_from_matrix(
    product_id: int,
    module_count: int,
    storage_variant: str
) -> float:
    """
    Berechnet Produktpreis aus aktiver Matrix
    
    Args:
        product_id: Produkt-ID
        module_count: Anzahl Module (Row-Label)
        storage_variant: Speicher-Variante (Column-Label)
    
    Returns:
        Berechneter Preis oder None
    """
    # Aktive Matrix laden
    matrix_id = get_active_matrix_id()
    if not matrix_id:
        return None
    
    # Preis aus Matrix holen
    price = lookup_price(matrix_id, str(module_count), storage_variant)
    
    # Optional: Zusätzliche Berechnungen
    full = get_matrix_full(matrix_id)
    if full['meta']['pricing_mode'] == 'additiv':
        # Addiere Zubehör-Preise
        if full['meta']['include_accessories']:
            price += get_accessories_price(product_id)
    
    return price
```

### UI-Integration

```python
def render_product_price_config():
    """
    UI für Produktpreis-Konfiguration
    """
    st.subheader("Preisberechnung")
    
    price_mode = st.radio(
        "Preismodus",
        ["Einzelpreis", "Matrix-Preis"],
        help="Einzelpreis: Manuell eingeben. Matrix-Preis: Aus Preismatrix berechnen"
    )
    
    if price_mode == "Einzelpreis":
        price = st.number_input("Preis (€)", min_value=0.0)
    else:
        # Matrix-Auswahl
        matrices = list_matrices()
        selected = st.selectbox("Matrix", [m['name'] for m in matrices])
        
        # Vorschau
        if selected:
            st.info("Preis wird automatisch aus Matrix berechnet")
            # Zeige Beispiel-Berechnung
            example_price = calculate_product_price_from_matrix(
                product_id=1,
                module_count=20,
                storage_variant="10kWh"
            )
            st.write(f"Beispiel (20 Module, 10kWh): {example_price}€")
```

