# Task 5: CRUD-Operationen für Zeilen und Spalten - Abgeschlossen

## Übersicht

Task 5 der Excel-Integration wurde erfolgreich implementiert. Alle CRUD-Operationen für Zeilen und Spalten sind vollständig funktionsfähig, inklusive automatischer Formel-Aktualisierung.

## Implementierte Features

### 1. Zeilen-Operationen

#### add_row(position, save_undo)
- Fügt eine neue Zeile an der angegebenen Position ein
- `position=None` fügt die Zeile am Ende hinzu
- Verschiebt alle Zellen ab der Position um 1 nach unten
- Aktualisiert automatisch alle Formel-Referenzen
- Unterstützt Undo/Redo

#### delete_row(row, save_undo)
- Löscht eine Zeile an der angegebenen Position
- Verschiebt alle Zellen nach der gelöschten Zeile um 1 nach oben
- Aktualisiert automatisch alle Formel-Referenzen
- Unterstützt Undo/Redo

### 2. Spalten-Operationen

#### add_column(position, save_undo)
- Fügt eine neue Spalte an der angegebenen Position ein
- `position=None` fügt die Spalte am Ende hinzu
- Verschiebt alle Zellen ab der Position um 1 nach rechts
- Aktualisiert automatisch alle Formel-Referenzen
- Unterstützt Undo/Redo

#### delete_column(col, save_undo)
- Löscht eine Spalte an der angegebenen Position
- Verschiebt alle Zellen nach der gelöschten Spalte um 1 nach links
- Aktualisiert automatisch alle Formel-Referenzen
- Unterstützt Undo/Redo

### 3. Intelligente Formel-Aktualisierung

Die Formel-Aktualisierung wurde erweitert um:

#### update_formula_references() - Erweiterte Version
```python
def update_formula_references(
    formula: str,
    row_offset: int,
    col_offset: int,
    min_row: Optional[int] = None,
    min_col: Optional[int] = None
) -> str
```

**Neue Parameter:**
- `min_row`: Nur Zeilen >= min_row werden aktualisiert
- `min_col`: Nur Spalten >= min_col werden aktualisiert

**Intelligentes Verhalten:**
- Beim Einfügen einer Zeile bei Position 1:
  - `A1` bleibt `A1` (row < 1)
  - `A2` wird zu `A3` (row >= 1)
  - `=A1+A2` wird zu `=A1+A3`
  
- Beim Löschen einer Zeile bei Position 1:
  - `A1` bleibt `A1` (row <= 1)
  - `A3` wird zu `A2` (row > 1)
  - `=A1+A3` wird zu `=A1+A2`

**Unterstützt:**
- Einzelne Zellreferenzen: `A1`, `B2`
- Bereiche: `A1:A10`, `B1:D5`
- Komplexe Formeln: `=IF(A1>5, SUM(A1:A3), A2)`
- Verschachtelte Funktionen

## Technische Details

### Implementierung in excel_manager.py

Alle vier CRUD-Operationen folgen dem gleichen Muster:

1. **Undo-State speichern** (falls aktiviert)
2. **Zellen verschieben/löschen**
   - Betroffene Zellen identifizieren
   - Zellpositionen aktualisieren
   - Formeln mit korrekten min_row/min_col Parametern aktualisieren
3. **Matrix-Größe anpassen**
4. **Dependency Graph neu aufbauen**
5. **Timestamp aktualisieren**

### Beispiel: add_row()

```python
def add_row(self, position: Optional[int] = None, save_undo: bool = True):
    if save_undo:
        self._save_undo_state()
    
    if position is None:
        position = self.matrix.rows
    
    # Verschiebe alle Zellen ab position um 1 nach unten
    cells_to_move = [
        (r, c, cell) 
        for (r, c), cell in self.matrix.cells.items() 
        if r >= position
    ]
    
    for old_row, col, cell in cells_to_move:
        del self.matrix.cells[(old_row, col)]
        cell.row = old_row + 1
        self.matrix.cells[(old_row + 1, col)] = cell
        
        # Aktualisiere Formeln - nur Referenzen >= position
        if cell.is_formula():
            cell.formula = update_formula_references(
                cell.formula, 1, 0, min_row=position
            )
    
    self.matrix.rows += 1
    self._rebuild_dependency_graph()
    self.matrix.updated_at = datetime.now()
```

## Tests

Alle 18 Tests bestanden erfolgreich:

### Basis-Tests
- ✅ `test_add_row` - Zeile hinzufügen
- ✅ `test_add_row_at_end` - Zeile am Ende hinzufügen
- ✅ `test_add_column` - Spalte hinzufügen
- ✅ `test_add_column_at_end` - Spalte am Ende hinzufügen
- ✅ `test_delete_row` - Zeile löschen
- ✅ `test_delete_column` - Spalte löschen

### Formel-Aktualisierungs-Tests
- ✅ `test_add_row_with_formula_update` - Formel bei Zeilen-Einfügung
- ✅ `test_add_row_with_range_formula_update` - Bereichs-Formel bei Zeilen-Einfügung
- ✅ `test_add_column_with_formula_update` - Formel bei Spalten-Einfügung
- ✅ `test_add_column_with_range_formula_update` - Bereichs-Formel bei Spalten-Einfügung
- ✅ `test_delete_row_with_formula_update` - Formel bei Zeilen-Löschung
- ✅ `test_delete_row_with_range_formula_update` - Bereichs-Formel bei Zeilen-Löschung
- ✅ `test_delete_column_with_formula_update` - Formel bei Spalten-Löschung
- ✅ `test_delete_column_with_range_formula_update` - Bereichs-Formel bei Spalten-Löschung

### Undo/Redo-Tests
- ✅ `test_row_operations_with_undo` - Zeilen-Operationen mit Undo
- ✅ `test_column_operations_with_undo` - Spalten-Operationen mit Undo

### Komplexe Formel-Tests
- ✅ `test_complex_formula_update_on_row_insert` - Komplexe Formel bei Zeilen-Einfügung
- ✅ `test_complex_formula_update_on_column_insert` - Komplexe Formel bei Spalten-Einfügung

## Beispiel-Verwendung

```python
from excel.excel_manager import ExcelManager

# Manager erstellen
manager = ExcelManager()

# Werte setzen
manager.set_cell_value(0, 0, 10)  # A1 = 10
manager.set_cell_value(1, 0, 20)  # A2 = 20
manager.set_cell_value(2, 0, None, raw_input="=A1+A2")  # A3 = =A1+A2

# Zeile bei Position 1 einfügen
manager.add_row(position=1)

# Ergebnis:
# A1 = 10 (unverändert)
# A2 = leer (neue Zeile)
# A3 = 20 (vorher A2)
# A4 = =A1+A3 (Formel aktualisiert!)

# Spalte löschen
manager.delete_column(1)

# Undo
manager.undo()

# Redo
manager.redo()
```

## Erfüllte Requirements

Alle Requirements aus der Spezifikation wurden erfüllt:

- ✅ **Requirement 3.1**: Funktion zum Hinzufügen von Zeilen
- ✅ **Requirement 3.2**: Funktion zum Hinzufügen von Spalten
- ✅ **Requirement 3.3**: Funktion zum Löschen von Zeilen
- ✅ **Requirement 3.4**: Funktion zum Löschen von Spalten
- ✅ **Requirement 3.5**: Automatische Formel-Anpassung bei Zeilen/Spalten-Änderungen

## Nächste Schritte

Task 5 ist vollständig abgeschlossen. Die nächsten Tasks sind:

- **Task 6**: Undo/Redo Funktionalität (bereits implementiert in Task 4)
- **Task 6.1**: Unit Tests für ExcelManager (teilweise vorhanden, kann erweitert werden)
- **Task 7**: Admin Panel Integration
- **Task 8**: Excel Grid UI Basis-Komponente

## Dateien

### Geänderte Dateien
- `excel/excel_manager.py` - CRUD-Operationen implementiert
- `excel/excel_utils.py` - update_formula_references erweitert
- `test_excel_manager.py` - Umfangreiche Tests hinzugefügt

### Neue Dateien
- `TASK_5_CRUD_OPERATIONS_COMPLETE.md` - Diese Dokumentation

## Zusammenfassung

Task 5 wurde erfolgreich implementiert mit:
- ✅ Alle 4 CRUD-Operationen (add_row, add_column, delete_row, delete_column)
- ✅ Intelligente Formel-Aktualisierung mit min_row/min_col Parametern
- ✅ Vollständige Undo/Redo-Unterstützung
- ✅ 18 umfangreiche Tests (alle bestanden)
- ✅ Unterstützung für einfache und komplexe Formeln
- ✅ Unterstützung für Bereiche und verschachtelte Funktionen

Die Implementierung ist robust, gut getestet und bereit für die Integration in die UI-Komponenten.
