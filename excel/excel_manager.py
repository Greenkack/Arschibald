"""
Excel Integration - Excel Manager

Zentrale Verwaltungsklasse für Excel-Matrizen.
Verwaltet den Zustand, Operationen und die Integration mit der Datenbank.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime
import copy

from excel.excel_models import (
    Cell, 
    ExcelMatrix, 
    FormulaError,
    SyntaxError,
    ReferenceError,
    CircularReferenceError
)
from excel.excel_utils import (
    cell_to_a1,
    a1_to_cell,
    parse_range,
    extract_cell_references,
    update_formula_references
)
from excel.excel_formula_engine import FormulaEngine
from excel.excel_batch_operations import BatchOperationManager


class ExcelManager:
    """
    Verwaltet den Zustand und die Operationen einer Excel-Matrix
    
    Diese Klasse ist die zentrale Schnittstelle für alle Operationen
    auf einer Excel-Matrix. Sie verwaltet:
    - Zellwerte und Formeln
    - Undo/Redo-Funktionalität
    - Abhängigkeitsgraph für Formeln
    - Integration mit der Datenbank
    """
    
    def __init__(
        self,
        matrix: Optional[ExcelMatrix] = None,
        enable_cache: bool = True
    ):
        """
        Initialisiert den ExcelManager
        
        Args:
            matrix: Optionale ExcelMatrix, erstellt neue wenn None
            enable_cache: Ob Formel-Caching aktiviert werden soll
        """
        if matrix is None:
            matrix = ExcelMatrix()
        
        self.matrix = matrix
        self.formula_engine = FormulaEngine(enable_cache=enable_cache)
        self.undo_stack: List[ExcelMatrix] = []
        self.redo_stack: List[ExcelMatrix] = []
        self.dependency_graph: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}
        self.max_undo_steps = 50
        
        # Batch-Operations-Manager
        self.batch_manager = BatchOperationManager(self)
        
        # Änderungs-Tracking für Auto-Save
        self.has_unsaved_changes = False
        self.last_save_time: Optional[datetime] = None
        
        # Baue initialen Dependency Graph
        self._build_dependency_graph()
        
        # Baue Dependency-Cache für schnelle Abfragen
        self.formula_engine.build_dependency_cache(self.matrix.cells)
    
    def get_cell(self, row: int, col: int) -> Cell:
        """
        Gibt eine Zelle zurück
        
        Args:
            row: Zeilennummer (0-basiert)
            col: Spaltennummer (0-basiert)
            
        Returns:
            Cell-Objekt
        """
        return self.matrix.get_cell(row, col)
    
    def get_cell_value(self, row: int, col: int) -> Any:
        """
        Gibt den Wert einer Zelle zurück
        
        Args:
            row: Zeilennummer (0-basiert)
            col: Spaltennummer (0-basiert)
            
        Returns:
            Zellwert oder None
        """
        return self.matrix.get_cell_value(row, col)
    
    def set_cell_value(
        self, 
        row: int, 
        col: int, 
        value: Any, 
        raw_input: Optional[str] = None,
        save_undo: bool = True
    ):
        """
        Setzt den Wert einer Zelle
        
        Args:
            row: Zeilennummer (0-basiert)
            col: Spaltennummer (0-basiert)
            value: Zu setzender Wert
            raw_input: Optionale Benutzereingabe
            save_undo: Ob Undo-State gespeichert werden soll
        """
        if save_undo:
            self._save_undo_state()
        
        # Wenn raw_input eine Formel ist, berechne den Wert
        if raw_input and raw_input.startswith('='):
            # Setze Formel in Matrix
            self.matrix.set_cell_value(row, col, None, raw_input)
            
            # Aktualisiere Dependency Graph
            self._update_dependencies_for_cell(row, col, raw_input)
            
            # Berechne Formel
            try:
                context = self._build_context()
                result = self.formula_engine.execute_formula(raw_input, context)
                
                # Setze berechneten Wert
                cell = self.matrix.get_cell(row, col)
                cell.value = result
                cell.error = None
            except FormulaError as e:
                # Setze Fehlerwert
                cell = self.matrix.get_cell(row, col)
                cell.error = e.display
                cell.value = None
            except Exception as e:
                # Fange alle anderen Fehler ab
                cell = self.matrix.get_cell(row, col)
                cell.error = "#ERROR!"
                cell.value = None
        else:
            # Normaler Wert (keine Formel)
            self.matrix.set_cell_value(row, col, value, raw_input)
        
        # Invalidiere Cache für betroffene Zellen
        self.formula_engine.invalidate_cache([(row, col)])
        
        # Trigger Neuberechnung abhängiger Zellen
        self._recalculate_affected_cells(row, col)
        
        # Update timestamp und markiere als geändert
        self.matrix.updated_at = datetime.now()
        self.has_unsaved_changes = True
    
    def clear_cell(self, row: int, col: int, save_undo: bool = True):
        """
        Löscht den Inhalt einer Zelle
        
        Args:
            row: Zeilennummer (0-basiert)
            col: Spaltennummer (0-basiert)
            save_undo: Ob Undo-State gespeichert werden soll
        """
        if save_undo:
            self._save_undo_state()
        
        self.matrix.clear_cell(row, col)
        
        # Entferne aus Dependency Graph
        if (row, col) in self.dependency_graph:
            del self.dependency_graph[(row, col)]
        
        # Invalidiere Cache für betroffene Zellen
        self.formula_engine.invalidate_cache([(row, col)])
        
        # Trigger Neuberechnung abhängiger Zellen
        self._recalculate_affected_cells(row, col)
        
        self.matrix.updated_at = datetime.now()
        self.has_unsaved_changes = True
    
    def add_row(self, position: Optional[int] = None, save_undo: bool = True):
        """
        Fügt eine neue Zeile hinzu
        
        Args:
            position: Position wo die Zeile eingefügt werden soll (None = am Ende)
            save_undo: Ob Undo-State gespeichert werden soll
        """
        if save_undo:
            self._save_undo_state()
        
        if position is None:
            position = self.matrix.rows
        
        # Verschiebe alle Zellen ab position um 1 nach unten
        cells_to_move = [(r, c, cell) for (r, c), cell in self.matrix.cells.items() if r >= position]
        
        for old_row, col, cell in cells_to_move:
            # Entferne alte Position
            del self.matrix.cells[(old_row, col)]
            
            # Setze neue Position
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
        self.has_unsaved_changes = True
    
    def add_column(self, position: Optional[int] = None, save_undo: bool = True):
        """
        Fügt eine neue Spalte hinzu
        
        Args:
            position: Position wo die Spalte eingefügt werden soll (None = am Ende)
            save_undo: Ob Undo-State gespeichert werden soll
        """
        if save_undo:
            self._save_undo_state()
        
        if position is None:
            position = self.matrix.columns
        
        # Verschiebe alle Zellen ab position um 1 nach rechts
        cells_to_move = [(r, c, cell) for (r, c), cell in self.matrix.cells.items() if c >= position]
        
        for row, old_col, cell in cells_to_move:
            # Entferne alte Position
            del self.matrix.cells[(row, old_col)]
            
            # Setze neue Position
            cell.col = old_col + 1
            self.matrix.cells[(row, old_col + 1)] = cell
            
            # Aktualisiere Formeln - nur Referenzen >= position
            if cell.is_formula():
                cell.formula = update_formula_references(
                    cell.formula, 0, 1, min_col=position
                )
        
        self.matrix.columns += 1
        self._rebuild_dependency_graph()
        self.matrix.updated_at = datetime.now()
        self.has_unsaved_changes = True
    
    def delete_row(self, row: int, save_undo: bool = True):
        """
        Löscht eine Zeile
        
        Args:
            row: Zu löschende Zeilennummer (0-basiert)
            save_undo: Ob Undo-State gespeichert werden soll
        """
        if save_undo:
            self._save_undo_state()
        
        # Lösche alle Zellen in der Zeile
        cells_to_delete = [(r, c) for (r, c) in self.matrix.cells.keys() if r == row]
        for cell_pos in cells_to_delete:
            del self.matrix.cells[cell_pos]
        
        # Verschiebe alle Zellen nach der gelöschten Zeile um 1 nach oben
        cells_to_move = [(r, c, cell) for (r, c), cell in self.matrix.cells.items() if r > row]
        
        for old_row, col, cell in cells_to_move:
            # Entferne alte Position
            del self.matrix.cells[(old_row, col)]
            
            # Setze neue Position
            cell.row = old_row - 1
            self.matrix.cells[(old_row - 1, col)] = cell
            
            # Aktualisiere Formeln - nur Referenzen > row
            if cell.is_formula():
                cell.formula = update_formula_references(
                    cell.formula, -1, 0, min_row=row + 1
                )
        
        self.matrix.rows -= 1
        self._rebuild_dependency_graph()
        self.matrix.updated_at = datetime.now()
        self.has_unsaved_changes = True
    
    def delete_column(self, col: int, save_undo: bool = True):
        """
        Löscht eine Spalte
        
        Args:
            col: Zu löschende Spaltennummer (0-basiert)
            save_undo: Ob Undo-State gespeichert werden soll
        """
        if save_undo:
            self._save_undo_state()
        
        # Lösche alle Zellen in der Spalte
        cells_to_delete = [(r, c) for (r, c) in self.matrix.cells.keys() if c == col]
        for cell_pos in cells_to_delete:
            del self.matrix.cells[cell_pos]
        
        # Verschiebe alle Zellen nach der gelöschten Spalte um 1 nach links
        cells_to_move = [(r, c, cell) for (r, c), cell in self.matrix.cells.items() if c > col]
        
        for row, old_col, cell in cells_to_move:
            # Entferne alte Position
            del self.matrix.cells[(row, old_col)]
            
            # Setze neue Position
            cell.col = old_col - 1
            self.matrix.cells[(row, old_col - 1)] = cell
            
            # Aktualisiere Formeln - nur Referenzen > col
            if cell.is_formula():
                cell.formula = update_formula_references(
                    cell.formula, 0, -1, min_col=col + 1
                )
        
        self.matrix.columns -= 1
        self._rebuild_dependency_graph()
        self.matrix.updated_at = datetime.now()
        self.has_unsaved_changes = True
    
    def undo(self) -> bool:
        """
        Macht letzte Änderung rückgängig
        
        Returns:
            True wenn erfolgreich, False wenn kein Undo verfügbar
        """
        if not self.undo_stack:
            return False
        
        # Speichere aktuellen State für Redo
        self.redo_stack.append(copy.deepcopy(self.matrix))
        
        # Stelle vorherigen State wieder her
        self.matrix = self.undo_stack.pop()
        
        # Rebuild dependency graph
        self._rebuild_dependency_graph()
        
        return True
    
    def redo(self) -> bool:
        """
        Wiederholt rückgängig gemachte Änderung
        
        Returns:
            True wenn erfolgreich, False wenn kein Redo verfügbar
        """
        if not self.redo_stack:
            return False
        
        # Speichere aktuellen State für Undo
        self.undo_stack.append(copy.deepcopy(self.matrix))
        
        # Stelle Redo-State wieder her
        self.matrix = self.redo_stack.pop()
        
        # Rebuild dependency graph
        self._rebuild_dependency_graph()
        
        return True
    
    def can_undo(self) -> bool:
        """Prüft ob Undo verfügbar ist"""
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Prüft ob Redo verfügbar ist"""
        return len(self.redo_stack) > 0
    
    # Private Hilfsmethoden
    
    def _save_undo_state(self):
        """Speichert aktuellen State für Undo"""
        # Deep copy der Matrix
        state = copy.deepcopy(self.matrix)
        self.undo_stack.append(state)
        
        # Limitiere Stack-Größe
        if len(self.undo_stack) > self.max_undo_steps:
            self.undo_stack.pop(0)
        
        # Lösche Redo-Stack bei neuer Änderung
        self.redo_stack.clear()
    
    def _build_dependency_graph(self):
        """Baut den Abhängigkeitsgraphen für alle Formeln"""
        self.dependency_graph.clear()
        
        for cell in self.matrix.get_cells_with_formulas():
            self._update_dependencies_for_cell(cell.row, cell.col, cell.formula)
    
    def _rebuild_dependency_graph(self):
        """Baut den Abhängigkeitsgraphen neu"""
        self._build_dependency_graph()
        # Baue auch Dependency-Cache neu
        self.formula_engine.build_dependency_cache(self.matrix.cells)
        # Invalidiere Formel-Cache da sich Abhängigkeiten geändert haben
        self.formula_engine.clear_cache()
    
    def _update_dependencies_for_cell(self, row: int, col: int, formula: str):
        """
        Aktualisiert Abhängigkeiten für eine Zelle
        
        Args:
            row: Zeilennummer
            col: Spaltennummer
            formula: Formel der Zelle
        """
        # Extrahiere alle Zellreferenzen aus der Formel
        cell_refs = extract_cell_references(formula)
        
        dependencies = []
        for ref in cell_refs:
            try:
                # Parse Referenz(en)
                cells = parse_range(ref)
                dependencies.extend(cells)
            except ValueError:
                # Ignoriere ungültige Referenzen
                pass
        
        # Speichere Abhängigkeiten
        self.dependency_graph[(row, col)] = dependencies
    
    def _recalculate_affected_cells(self, changed_row: int, changed_col: int):
        """
        Berechnet alle von einer Änderung betroffenen Zellen neu
        
        Args:
            changed_row: Geänderte Zeile
            changed_col: Geänderte Spalte
        """
        # Finde alle Zellen die direkt oder indirekt von der geänderten Zelle abhängen
        affected_cells = self._get_all_affected_cells_recursive(
            (changed_row, changed_col),
            set()
        )
        
        if not affected_cells:
            return
        
        # Sortiere nach Berechnungsreihenfolge (topologisch)
        # Zellen die von weniger anderen Zellen abhängen kommen zuerst
        try:
            calc_order = self.formula_engine.get_calculation_order(
                self.matrix.cells
            )
            # Filtere nur betroffene Zellen und behalte Reihenfolge
            ordered_affected = [
                cell for cell in calc_order if cell in affected_cells
            ]
        except CircularReferenceError:
            # Bei Zirkelbezug: Berechne in beliebiger Reihenfolge
            ordered_affected = list(affected_cells)
        
        # Berechne alle betroffenen Zellen neu mit FormulaEngine
        context = self._build_context()
        
        for row, col in ordered_affected:
            cell = self.matrix.get_cell(row, col)
            if cell.is_formula():
                try:
                    # Führe Formel aus
                    result = self.formula_engine.execute_formula(
                        cell.formula,
                        context
                    )
                    # Aktualisiere Zellwert
                    cell.value = result
                    cell.error = None
                    # Aktualisiere Kontext für nachfolgende Berechnungen
                    context[(row, col)] = result
                except FormulaError as e:
                    # Setze Fehlerwert
                    cell.error = e.display
                    cell.value = None
                    context[(row, col)] = None
    
    def _get_all_affected_cells_recursive(
        self,
        cell: Tuple[int, int],
        visited: Set[Tuple[int, int]]
    ) -> Set[Tuple[int, int]]:
        """
        Findet rekursiv alle Zellen die von einer Zelle abhängen
        
        Args:
            cell: Ausgangszelle (row, col)
            visited: Bereits besuchte Zellen
            
        Returns:
            Set aller betroffenen Zellen
        """
        if cell in visited:
            return set()
        
        visited.add(cell)
        affected = set()
        
        # Finde direkt abhängige Zellen
        for cell_pos, dependencies in self.dependency_graph.items():
            if cell in dependencies:
                affected.add(cell_pos)
                # Rekursiv für abhängige Zellen
                affected.update(
                    self._get_all_affected_cells_recursive(cell_pos, visited)
                )
        
        return affected
    
    def _detect_circular_reference(self, start_cell: Tuple[int, int]) -> bool:
        """
        Erkennt Zirkelbezüge ausgehend von einer Zelle
        
        Args:
            start_cell: Start-Zelle (row, col)
            
        Returns:
            True wenn Zirkelbezug gefunden
        """
        visited = set()
        stack = [start_cell]
        
        while stack:
            current = stack.pop()
            
            if current in visited:
                return True  # Zirkelbezug gefunden
            
            visited.add(current)
            
            # Füge Abhängigkeiten zum Stack hinzu
            if current in self.dependency_graph:
                stack.extend(self.dependency_graph[current])
        
        return False
    
    def get_matrix(self) -> ExcelMatrix:
        """Gibt die verwaltete Matrix zurück"""
        return self.matrix
    
    def get_matrix_info(self) -> Dict[str, Any]:
        """
        Gibt Informationen über die Matrix zurück
        
        Returns:
            Dictionary mit Matrix-Informationen
        """
        return {
            'id': self.matrix.id,
            'name': self.matrix.name,
            'description': self.matrix.description,
            'rows': self.matrix.rows,
            'columns': self.matrix.columns,
            'cell_count': len(self.matrix.cells),
            'formula_count': len(self.matrix.get_cells_with_formulas()),
            'created_at': self.matrix.created_at,
            'updated_at': self.matrix.updated_at,
            'can_undo': self.can_undo(),
            'can_redo': self.can_redo()
        }
    
    def parse_and_execute_formula(
        self,
        formula: str,
        row: Optional[int] = None,
        col: Optional[int] = None
    ) -> Any:
        """
        Parst und führt eine Formel aus
        
        Args:
            formula: Die auszuführende Formel (mit oder ohne '=')
            row: Optionale Zeilennummer für Kontext
            col: Optionale Spaltennummer für Kontext
            
        Returns:
            Berechnetes Ergebnis
            
        Raises:
            FormulaError: Bei Fehlern in der Formel
        """
        # Baue Kontext mit allen Zellwerten
        context = self._build_context()
        
        # Prüfe auf Zirkelbezüge wenn Zellposition angegeben
        if row is not None and col is not None:
            if self._would_create_circular_reference(row, col, formula):
                raise CircularReferenceError(
                    "Formel würde Zirkelbezug erstellen",
                    display="#CIRCULAR!"
                )
        
        # Führe Formel aus
        return self.formula_engine.execute_formula(formula, context)
    
    def _build_context(self) -> Dict[Tuple[int, int], Any]:
        """
        Baut einen Kontext mit allen Zellwerten für Formelberechnungen
        
        Returns:
            Dictionary mit {(row, col): value}
        """
        context = {}
        
        for (row, col), cell in self.matrix.cells.items():
            # Verwende den berechneten Wert, nicht die Formel
            if cell.value is not None:
                context[(row, col)] = cell.value
            elif not cell.is_formula():
                # Leere Zelle ohne Formel = 0 für Berechnungen
                context[(row, col)] = 0
        
        return context
    
    def _would_create_circular_reference(
        self,
        row: int,
        col: int,
        formula: str
    ) -> bool:
        """
        Prüft ob eine Formel einen Zirkelbezug erstellen würde
        
        Args:
            row: Zeilennummer der Zelle
            col: Spaltennummer der Zelle
            formula: Die zu prüfende Formel
            
        Returns:
            True wenn Zirkelbezug entstehen würde
        """
        # Extrahiere Zellreferenzen aus der Formel
        cell_refs = extract_cell_references(formula)
        
        # Baue temporären Abhängigkeitsgraphen
        temp_dependencies = []
        
        for ref in cell_refs:
            try:
                if ':' in ref:
                    # Bereich
                    cells = parse_range(ref)
                    temp_dependencies.extend(cells)
                else:
                    # Einzelne Zelle
                    dep_row, dep_col = a1_to_cell(ref)
                    temp_dependencies.append((dep_row, dep_col))
            except ValueError:
                # Ungültige Referenz ignorieren
                pass
        
        # Prüfe ob die Zelle sich selbst referenziert
        if (row, col) in temp_dependencies:
            return True
        
        # Prüfe ob eine der Abhängigkeiten zurück zur Zelle führt
        visited = set()
        
        def has_path_to_cell(from_cell: Tuple[int, int]) -> bool:
            """Rekursiv prüfen ob Pfad zur Zielzelle existiert"""
            if from_cell == (row, col):
                return True
            
            if from_cell in visited:
                return False
            
            visited.add(from_cell)
            
            # Prüfe alle Abhängigkeiten dieser Zelle
            if from_cell in self.dependency_graph:
                for dep in self.dependency_graph[from_cell]:
                    if has_path_to_cell(dep):
                        return True
            
            return False
        
        # Prüfe für alle direkten Abhängigkeiten
        for dep in temp_dependencies:
            if has_path_to_cell(dep):
                return True
        
        return False
    
    def recalculate_all_formulas(self):
        """
        Berechnet alle Formeln in der Matrix neu
        
        Dies ist nützlich nach dem Laden einer Matrix oder
        nach größeren Änderungen.
        """
        # Baue Kontext
        context = self._build_context()
        
        # Hole alle Zellen mit Formeln
        formula_cells = self.matrix.get_cells_with_formulas()
        
        # Berechne Reihenfolge basierend auf Abhängigkeiten
        try:
            calc_order = self.formula_engine.get_calculation_order(
                self.matrix.cells
            )
            # Filtere nur Zellen mit Formeln
            ordered_formula_cells = [
                cell for cell in formula_cells
                if (cell.row, cell.col) in calc_order
            ]
        except CircularReferenceError:
            # Bei Zirkelbezug: Berechne in beliebiger Reihenfolge
            ordered_formula_cells = formula_cells
        
        # Berechne alle Formeln
        for cell in ordered_formula_cells:
            try:
                result = self.formula_engine.execute_formula(
                    cell.formula,
                    context
                )
                cell.value = result
                cell.error = None
                # Aktualisiere Kontext für nachfolgende Berechnungen
                context[(cell.row, cell.col)] = result
            except FormulaError as e:
                cell.error = e.display
                cell.value = None
                context[(cell.row, cell.col)] = None
    
    def save_to_database(self) -> bool:
        """
        Speichert die Matrix in die Datenbank
        
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            from price_matrix_store import get_matrix_full, set_cell_value as db_set_cell_value
            
            matrix_id = self.matrix.id
            
            if matrix_id is None:
                raise ValueError("Matrix hat keine ID. Kann nicht gespeichert werden.")
            
            # Lade Matrix-Struktur aus Datenbank
            matrix_data = get_matrix_full(matrix_id)
            if not matrix_data:
                raise ValueError(f"Matrix mit ID {matrix_id} nicht in Datenbank gefunden")
            
            # Erstelle Mapping von Position zu DB-IDs
            row_id_map = {r['position']: r['id'] for r in matrix_data['rows']}
            col_id_map = {c['position']: c['id'] for c in matrix_data['columns']}
            
            # Speichere alle Zellen
            for (row, col), cell in self.matrix.cells.items():
                if row in row_id_map and col in col_id_map:
                    row_id = row_id_map[row]
                    col_id = col_id_map[col]
                    
                    # Speichere in Datenbank (Task 3.2: mit data_type)
                    db_set_cell_value(
                        matrix_id,
                        row_id,
                        col_id,
                        cell.value,
                        raw_input=cell.formula or cell.raw_input,
                        data_type=cell.data_type
                    )
            
            # Markiere als gespeichert
            self.has_unsaved_changes = False
            self.last_save_time = datetime.now()
            
            return True
            
        except Exception as e:
            print(f"Fehler beim Speichern: {str(e)}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Gibt Cache-Statistiken zurück
        
        Returns:
            Dictionary mit Cache-Statistiken
        """
        return self.formula_engine.get_cache_stats()
    
    def clear_cache(self):
        """Leert den Formel-Cache"""
        self.formula_engine.clear_cache()
    
    def enable_cache(self):
        """Aktiviert das Formel-Caching"""
        self.formula_engine.enable_cache()
    
    def disable_cache(self):
        """Deaktiviert das Formel-Caching"""
        self.formula_engine.disable_cache()
    
    @staticmethod
    def load_from_database(matrix_id: int) -> 'ExcelManager':
        """
        Lädt eine Matrix aus der Datenbank
        
        Args:
            matrix_id: ID der zu ladenden Matrix
            
        Returns:
            ExcelManager mit geladener Matrix
            
        Raises:
            ValueError: Wenn Matrix nicht gefunden
        """
        try:
            from price_matrix_store import get_matrix_full
            
            # Lade Matrix-Daten aus Datenbank
            matrix_data = get_matrix_full(matrix_id)
            
            # Erstelle ExcelMatrix aus Daten
            matrix = ExcelMatrix(
                id=matrix_data['meta']['id'],
                name=matrix_data['meta']['name'],
                description=matrix_data['meta'].get('description', ''),
                rows=len(matrix_data['rows']),
                columns=len(matrix_data['columns'])
            )
            
            # Lade Zellen
            for (row_id, col_id), cell_data in matrix_data['cells'].items():
                # Finde row/col Index
                row_idx = next(
                    i for i, r in enumerate(matrix_data['rows'])
                    if r['id'] == row_id
                )
                col_idx = next(
                    i for i, c in enumerate(matrix_data['columns'])
                    if c['id'] == col_id
                )
                
                # Erstelle Cell
                raw_input = cell_data.get('raw_input')
                value = cell_data.get('value')
                
                cell = Cell(
                    row=row_idx,
                    col=col_idx,
                    value=value,
                    formula=raw_input if raw_input and raw_input.startswith('=') else None,
                    data_type=cell_data.get('data_type', 'text')
                )
                
                matrix.cells[(row_idx, col_idx)] = cell
            
            # Erstelle Manager
            manager = ExcelManager(matrix)
            
            # Berechne alle Formeln
            manager.recalculate_all_formulas()
            
            # Markiere als gespeichert
            manager.has_unsaved_changes = False
            manager.last_save_time = datetime.now()
            
            return manager
            
        except ImportError:
            raise ValueError(
                "price_matrix_store nicht verfügbar"
            )
        except Exception as e:
            raise ValueError(
                f"Fehler beim Laden der Matrix: {str(e)}"
            )
