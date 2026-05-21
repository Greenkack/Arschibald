"""
Excel Integration - Batch Operations

Dieses Modul implementiert Batch-Operationen für effiziente Updates
mehrerer Zellen gleichzeitig mit transaktionalen Datenbank-Operationen.
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import sqlite3
from contextlib import contextmanager

from excel.excel_models import Cell, ExcelMatrix
from excel.excel_utils import a1_to_cell, cell_to_a1


class BatchOperation:
    """
    Repräsentiert eine einzelne Batch-Operation
    
    Attributes:
        operation_type: Typ der Operation ('set_value', 'clear', 'delete_row', etc.)
        params: Parameter für die Operation
    """
    
    def __init__(self, operation_type: str, **params):
        """
        Initialisiert eine Batch-Operation
        
        Args:
            operation_type: Typ der Operation
            **params: Parameter für die Operation
        """
        self.operation_type = operation_type
        self.params = params
        self.timestamp = datetime.now()
    
    def __repr__(self) -> str:
        return f"BatchOperation({self.operation_type}, {self.params})"


class BatchOperationManager:
    """
    Verwaltet Batch-Operationen für Excel-Matrizen
    
    Diese Klasse ermöglicht:
    - Batch-Updates für mehrere Zellen
    - Transaktionale Datenbank-Operationen
    - Performance-Optimierung für große Updates
    - Rollback bei Fehlern
    """
    
    def __init__(self, excel_manager):
        """
        Initialisiert den Batch-Operation-Manager
        
        Args:
            excel_manager: ExcelManager-Instanz
        """
        self.excel_manager = excel_manager
        self.operations: List[BatchOperation] = []
        self.in_batch = False
    
    @contextmanager
    def batch_context(self, save_undo: bool = True):
        """
        Context Manager für Batch-Operationen
        
        Alle Operationen innerhalb des Kontexts werden gesammelt
        und am Ende in einer Transaktion ausgeführt.
        
        Args:
            save_undo: Ob ein Undo-State gespeichert werden soll
            
        Example:
            with batch_manager.batch_context():
                batch_manager.set_cell_value(0, 0, 10)
                batch_manager.set_cell_value(0, 1, 20)
                # Beide Operationen werden am Ende zusammen ausgeführt
        """
        self.in_batch = True
        self.operations.clear()
        
        # Speichere Undo-State vor Batch
        if save_undo:
            self.excel_manager._save_undo_state()
        
        try:
            yield self
            # Führe alle gesammelten Operationen aus
            self._execute_batch()
        except Exception as e:
            # Bei Fehler: Rollback
            self.operations.clear()
            raise e
        finally:
            self.in_batch = False
            self.operations.clear()
    
    def set_cell_value(
        self,
        row: int,
        col: int,
        value: Any,
        raw_input: Optional[str] = None
    ):
        """
        Fügt eine Set-Cell-Value-Operation zum Batch hinzu
        
        Args:
            row: Zeilennummer
            col: Spaltennummer
            value: Zu setzender Wert
            raw_input: Optionale Benutzereingabe
        """
        if self.in_batch:
            self.operations.append(
                BatchOperation(
                    'set_value',
                    row=row,
                    col=col,
                    value=value,
                    raw_input=raw_input
                )
            )
        else:
            # Direkte Ausführung wenn nicht im Batch-Modus
            self.excel_manager.set_cell_value(row, col, value, raw_input)
    
    def clear_cell(self, row: int, col: int):
        """
        Fügt eine Clear-Cell-Operation zum Batch hinzu
        
        Args:
            row: Zeilennummer
            col: Spaltennummer
        """
        if self.in_batch:
            self.operations.append(
                BatchOperation('clear', row=row, col=col)
            )
        else:
            self.excel_manager.clear_cell(row, col, save_undo=False)
    
    def set_range_values(
        self,
        start_row: int,
        start_col: int,
        values: List[List[Any]]
    ):
        """
        Setzt Werte für einen Bereich von Zellen
        
        Args:
            start_row: Start-Zeile
            start_col: Start-Spalte
            values: 2D-Liste mit Werten
            
        Example:
            # Setzt Werte in A1:B2
            batch_manager.set_range_values(0, 0, [[1, 2], [3, 4]])
        """
        for row_offset, row_values in enumerate(values):
            for col_offset, value in enumerate(row_values):
                self.set_cell_value(
                    start_row + row_offset,
                    start_col + col_offset,
                    value
                )
    
    def clear_range(
        self,
        start_row: int,
        start_col: int,
        end_row: int,
        end_col: int
    ):
        """
        Löscht einen Bereich von Zellen
        
        Args:
            start_row: Start-Zeile
            start_col: Start-Spalte
            end_row: End-Zeile
            end_col: End-Spalte
        """
        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                self.clear_cell(row, col)
    
    def _execute_batch(self):
        """
        Führt alle gesammelten Operationen aus
        
        Operationen werden in optimaler Reihenfolge ausgeführt:
        1. Alle Set-Value-Operationen
        2. Alle Clear-Operationen
        3. Neuberechnung aller betroffenen Formeln
        """
        if not self.operations:
            return
        
        # Sammle alle betroffenen Zellen
        affected_cells = set()
        
        # Führe alle Operationen aus (ohne Undo-Save und ohne Neuberechnung)
        for op in self.operations:
            if op.operation_type == 'set_value':
                row = op.params['row']
                col = op.params['col']
                value = op.params['value']
                raw_input = op.params.get('raw_input')
                
                # Setze Wert direkt ohne Neuberechnung
                self._set_cell_value_direct(row, col, value, raw_input)
                affected_cells.add((row, col))
                
            elif op.operation_type == 'clear':
                row = op.params['row']
                col = op.params['col']
                
                # Lösche Zelle direkt
                self.excel_manager.matrix.clear_cell(row, col)
                affected_cells.add((row, col))
        
        # Invalidiere Cache für alle betroffenen Zellen
        self.excel_manager.formula_engine.invalidate_cache(list(affected_cells))
        
        # Rebuild Dependency Graph
        self.excel_manager._rebuild_dependency_graph()
        
        # Berechne alle betroffenen Formeln neu (einmalig am Ende)
        for cell_pos in affected_cells:
            self.excel_manager._recalculate_affected_cells(cell_pos[0], cell_pos[1])
        
        # Update Timestamp
        self.excel_manager.matrix.updated_at = datetime.now()
        self.excel_manager.has_unsaved_changes = True
    
    def _set_cell_value_direct(
        self,
        row: int,
        col: int,
        value: Any,
        raw_input: Optional[str] = None
    ):
        """
        Setzt einen Zellwert direkt ohne Neuberechnung
        
        Args:
            row: Zeilennummer
            col: Spaltennummer
            value: Zu setzender Wert
            raw_input: Optionale Benutzereingabe
        """
        # Wenn raw_input eine Formel ist, berechne den Wert
        if raw_input and raw_input.startswith('='):
            # Setze Formel in Matrix
            self.excel_manager.matrix.set_cell_value(row, col, None, raw_input)
            
            # Aktualisiere Dependency Graph
            self.excel_manager._update_dependencies_for_cell(row, col, raw_input)
            
            # Berechne Formel
            try:
                context = self.excel_manager._build_context()
                result = self.excel_manager.formula_engine.execute_formula(
                    raw_input,
                    context
                )
                
                # Setze berechneten Wert
                cell = self.excel_manager.matrix.get_cell(row, col)
                cell.value = result
                cell.error = None
            except Exception as e:
                # Setze Fehlerwert
                cell = self.excel_manager.matrix.get_cell(row, col)
                cell.error = "#ERROR!"
                cell.value = None
        else:
            # Normaler Wert (keine Formel)
            self.excel_manager.matrix.set_cell_value(row, col, value, raw_input)
    
    def batch_update_from_dict(
        self,
        updates: Dict[Tuple[int, int], Any],
        save_undo: bool = True
    ):
        """
        Führt Batch-Update aus Dictionary aus
        
        Args:
            updates: Dictionary mit {(row, col): value}
            save_undo: Ob Undo-State gespeichert werden soll
            
        Example:
            updates = {
                (0, 0): 10,
                (0, 1): 20,
                (1, 0): 30
            }
            batch_manager.batch_update_from_dict(updates)
        """
        with self.batch_context(save_undo=save_undo):
            for (row, col), value in updates.items():
                self.set_cell_value(row, col, value)
    
    def batch_update_from_list(
        self,
        updates: List[Tuple[int, int, Any]],
        save_undo: bool = True
    ):
        """
        Führt Batch-Update aus Liste aus
        
        Args:
            updates: Liste von (row, col, value) Tupeln
            save_undo: Ob Undo-State gespeichert werden soll
            
        Example:
            updates = [
                (0, 0, 10),
                (0, 1, 20),
                (1, 0, 30)
            ]
            batch_manager.batch_update_from_list(updates)
        """
        with self.batch_context(save_undo=save_undo):
            for row, col, value in updates:
                self.set_cell_value(row, col, value)
    
    def get_operation_count(self) -> int:
        """
        Gibt die Anzahl der gesammelten Operationen zurück
        
        Returns:
            Anzahl der Operationen im aktuellen Batch
        """
        return len(self.operations)


def batch_save_to_database(
    excel_manager,
    matrix_id: int,
    cells_to_save: Optional[List[Tuple[int, int]]] = None
) -> bool:
    """
    Speichert mehrere Zellen in einer Transaktion in die Datenbank
    
    Args:
        excel_manager: ExcelManager-Instanz
        matrix_id: ID der Matrix
        cells_to_save: Liste von Zellen die gespeichert werden sollen
                      (None = alle Zellen)
    
    Returns:
        True wenn erfolgreich, False bei Fehler
    """
    try:
        from price_matrix_store import get_matrix_full
        from database import get_db_connection
        
        # Lade Matrix-Struktur aus Datenbank
        matrix_data = get_matrix_full(matrix_id)
        if not matrix_data:
            raise ValueError(f"Matrix mit ID {matrix_id} nicht in Datenbank gefunden")
        
        # Erstelle Mapping von Position zu DB-IDs
        row_id_map = {r['position']: r['id'] for r in matrix_data['rows']}
        col_id_map = {c['position']: c['id'] for c in matrix_data['columns']}
        
        # Bestimme welche Zellen gespeichert werden sollen
        if cells_to_save is None:
            cells_to_save = list(excel_manager.matrix.cells.keys())
        
        # Öffne Datenbankverbindung
        conn = get_db_connection()
        if not conn:
            return False
        
        cur = conn.cursor()
        
        try:
            # Starte Transaktion
            cur.execute("BEGIN TRANSACTION")
            
            # Speichere alle Zellen in einer Transaktion
            for row, col in cells_to_save:
                if row in row_id_map and col in col_id_map:
                    row_id = row_id_map[row]
                    col_id = col_id_map[col]
                    
                    cell = excel_manager.matrix.get_cell(row, col)
                    
                    # Prüfe ob Zelle bereits existiert
                    cur.execute(
                        """
                        SELECT id FROM price_matrix_cells 
                        WHERE matrix_id=? AND row_id=? AND column_id=?
                        """,
                        (matrix_id, row_id, col_id)
                    )
                    existing = cur.fetchone()
                    
                    if existing:
                        # Update
                        cur.execute(
                            """
                            UPDATE price_matrix_cells 
                            SET value=?, raw_input=?, updated_at=CURRENT_TIMESTAMP 
                            WHERE id=?
                            """,
                            (cell.value, cell.formula or cell.raw_input, existing[0])
                        )
                    else:
                        # Insert
                        cur.execute(
                            """
                            INSERT INTO price_matrix_cells 
                            (matrix_id, row_id, column_id, value, raw_input) 
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (matrix_id, row_id, col_id, cell.value, 
                             cell.formula or cell.raw_input)
                        )
            
            # Commit Transaktion
            conn.commit()
            
            # Markiere als gespeichert
            excel_manager.has_unsaved_changes = False
            excel_manager.last_save_time = datetime.now()
            
            return True
            
        except Exception as e:
            # Rollback bei Fehler
            conn.rollback()
            print(f"Fehler beim Batch-Speichern: {str(e)}")
            return False
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Fehler beim Batch-Speichern: {str(e)}")
        return False


def batch_load_cells(
    matrix_id: int,
    cell_range: Optional[Tuple[int, int, int, int]] = None
) -> Dict[Tuple[int, int], Cell]:
    """
    Lädt mehrere Zellen in einer Abfrage aus der Datenbank
    
    Args:
        matrix_id: ID der Matrix
        cell_range: Optional (start_row, start_col, end_row, end_col)
    
    Returns:
        Dictionary mit {(row, col): Cell}
    """
    try:
        from price_matrix_store import get_matrix_full
        
        # Lade Matrix-Daten
        matrix_data = get_matrix_full(matrix_id)
        if not matrix_data:
            return {}
        
        # Erstelle Mapping von DB-IDs zu Positionen
        row_pos_map = {r['id']: r['position'] for r in matrix_data['rows']}
        col_pos_map = {c['id']: c['position'] for c in matrix_data['columns']}
        
        cells = {}
        
        # Lade Zellen
        for (row_id, col_id), cell_data in matrix_data['cells'].items():
            row_pos = row_pos_map.get(row_id)
            col_pos = col_pos_map.get(col_id)
            
            if row_pos is None or col_pos is None:
                continue
            
            # Prüfe ob Zelle im gewünschten Bereich liegt
            if cell_range:
                start_row, start_col, end_row, end_col = cell_range
                if not (start_row <= row_pos <= end_row and 
                       start_col <= col_pos <= end_col):
                    continue
            
            # Erstelle Cell
            raw_input = cell_data.get('raw_input')
            value = cell_data.get('value')
            
            cell = Cell(
                row=row_pos,
                col=col_pos,
                value=value,
                formula=raw_input if raw_input and raw_input.startswith('=') else None,
                data_type='formula' if raw_input and raw_input.startswith('=') else 'text'
            )
            
            cells[(row_pos, col_pos)] = cell
        
        return cells
        
    except Exception as e:
        print(f"Fehler beim Batch-Laden: {str(e)}")
        return {}


__all__ = [
    'BatchOperation',
    'BatchOperationManager',
    'batch_save_to_database',
    'batch_load_cells'
]
