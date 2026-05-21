"""
Excel Integration - Lazy Loading

Implementiert Lazy Loading für große Datensätze mit virtuellem Scrolling.
Lädt nur sichtbare Zellen und verwendet Batch-Loading bei Scroll-Operationen.
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
import pandas as pd

from excel.excel_models import Cell, ExcelMatrix


@dataclass
class ViewportRange:
    """
    Repräsentiert den sichtbaren Bereich (Viewport) im Grid
    
    Attributes:
        start_row: Erste sichtbare Zeile (0-basiert)
        end_row: Letzte sichtbare Zeile (exklusiv)
        start_col: Erste sichtbare Spalte (0-basiert)
        end_col: Letzte sichtbare Spalte (exklusiv)
    """
    start_row: int = 0
    end_row: int = 100
    start_col: int = 0
    end_col: int = 26
    
    def contains(self, row: int, col: int) -> bool:
        """Prüft ob eine Zelle im Viewport liegt"""
        return (self.start_row <= row < self.end_row and
                self.start_col <= col < self.end_col)
    
    def get_cell_count(self) -> int:
        """Gibt die Anzahl der Zellen im Viewport zurück"""
        return (self.end_row - self.start_row) * (self.end_col - self.start_col)
    
    def expand(self, buffer_rows: int = 10, buffer_cols: int = 5) -> 'ViewportRange':
        """
        Erweitert den Viewport um einen Buffer
        
        Args:
            buffer_rows: Anzahl zusätzlicher Zeilen oben und unten
            buffer_cols: Anzahl zusätzlicher Spalten links und rechts
            
        Returns:
            Erweiterter ViewportRange
        """
        return ViewportRange(
            start_row=max(0, self.start_row - buffer_rows),
            end_row=self.end_row + buffer_rows,
            start_col=max(0, self.start_col - buffer_cols),
            end_col=self.end_col + buffer_cols
        )


@dataclass
class LazyLoadCache:
    """
    Cache für geladene Zellen mit LRU-Strategie
    
    Attributes:
        cells: Dictionary mit geladenen Zellen
        max_size: Maximale Anzahl gecachter Zellen
        access_order: Liste mit Zugriffs-Reihenfolge für LRU
    """
    cells: Dict[Tuple[int, int], Cell] = field(default_factory=dict)
    max_size: int = 10000
    access_order: List[Tuple[int, int]] = field(default_factory=list)
    
    def get(self, row: int, col: int) -> Optional[Cell]:
        """
        Holt eine Zelle aus dem Cache
        
        Args:
            row: Zeilennummer
            col: Spaltennummer
            
        Returns:
            Cell oder None wenn nicht im Cache
        """
        key = (row, col)
        if key in self.cells:
            # Aktualisiere Zugriffs-Reihenfolge (LRU)
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
            return self.cells[key]
        return None
    
    def put(self, row: int, col: int, cell: Cell):
        """
        Fügt eine Zelle zum Cache hinzu
        
        Args:
            row: Zeilennummer
            col: Spaltennummer
            cell: Cell-Objekt
        """
        key = (row, col)
        
        # Prüfe Cache-Größe und entferne älteste Einträge
        if len(self.cells) >= self.max_size and key not in self.cells:
            # Entferne ältesten Eintrag (LRU)
            if self.access_order:
                oldest_key = self.access_order.pop(0)
                if oldest_key in self.cells:
                    del self.cells[oldest_key]
        
        # Füge Zelle hinzu
        self.cells[key] = cell
        
        # Aktualisiere Zugriffs-Reihenfolge
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
    
    def put_batch(self, cells: Dict[Tuple[int, int], Cell]):
        """
        Fügt mehrere Zellen auf einmal hinzu
        
        Args:
            cells: Dictionary mit Zellen
        """
        for (row, col), cell in cells.items():
            self.put(row, col, cell)
    
    def clear(self):
        """Leert den Cache"""
        self.cells.clear()
        self.access_order.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Gibt Cache-Statistiken zurück
        
        Returns:
            Dictionary mit Statistiken
        """
        return {
            'size': len(self.cells),
            'max_size': self.max_size,
            'utilization': len(self.cells) / self.max_size if self.max_size > 0 else 0
        }


class LazyGridLoader:
    """
    Lazy Loader für Excel-Grids mit virtuellem Scrolling
    
    Diese Klasse implementiert Lazy Loading für große Datensätze:
    - Lädt nur sichtbare Zellen
    - Verwendet Batch-Loading für bessere Performance
    - Cached geladene Zellen mit LRU-Strategie
    - Unterstützt virtuelles Scrolling
    """
    
    def __init__(
        self,
        matrix: ExcelMatrix,
        viewport_rows: int = 100,
        viewport_cols: int = 26,
        buffer_rows: int = 20,
        buffer_cols: int = 5,
        cache_size: int = 10000
    ):
        """
        Initialisiert den Lazy Loader
        
        Args:
            matrix: ExcelMatrix mit allen Daten
            viewport_rows: Anzahl sichtbarer Zeilen
            viewport_cols: Anzahl sichtbarer Spalten
            buffer_rows: Buffer-Zeilen für Prefetching
            buffer_cols: Buffer-Spalten für Prefetching
            cache_size: Maximale Anzahl gecachter Zellen
        """
        self.matrix = matrix
        self.viewport = ViewportRange(0, viewport_rows, 0, viewport_cols)
        self.buffer_rows = buffer_rows
        self.buffer_cols = buffer_cols
        self.cache = LazyLoadCache(max_size=cache_size)
        
        # Lade initiale Zellen
        self._load_viewport_cells()
    
    def _load_viewport_cells(self):
        """Lädt Zellen für den aktuellen Viewport mit Buffer"""
        expanded = self.viewport.expand(self.buffer_rows, self.buffer_cols)
        cells_to_load = {}
        
        for row in range(expanded.start_row, expanded.end_row):
            for col in range(expanded.start_col, expanded.end_col):
                # Prüfe ob bereits im Cache
                if self.cache.get(row, col) is None:
                    # Hole Zelle aus Matrix
                    cell = self.matrix.get_cell(row, col)
                    cells_to_load[(row, col)] = cell
        
        # Batch-Insert in Cache
        if cells_to_load:
            self.cache.put_batch(cells_to_load)
    
    def get_cell(self, row: int, col: int) -> Cell:
        """
        Holt eine Zelle (aus Cache oder lädt sie)
        
        Args:
            row: Zeilennummer
            col: Spaltennummer
            
        Returns:
            Cell-Objekt
        """
        # Versuche aus Cache zu holen
        cell = self.cache.get(row, col)
        
        if cell is None:
            # Lade aus Matrix
            cell = self.matrix.get_cell(row, col)
            self.cache.put(row, col, cell)
        
        return cell
    
    def set_viewport(self, start_row: int, end_row: int, start_col: int = 0, end_col: int = 26):
        """
        Setzt den Viewport und lädt neue Zellen
        
        Args:
            start_row: Erste sichtbare Zeile
            end_row: Letzte sichtbare Zeile (exklusiv)
            start_col: Erste sichtbare Spalte
            end_col: Letzte sichtbare Spalte (exklusiv)
        """
        old_viewport = self.viewport
        self.viewport = ViewportRange(start_row, end_row, start_col, end_col)
        
        # Prüfe ob sich Viewport signifikant geändert hat
        if (abs(old_viewport.start_row - start_row) > self.buffer_rows or
            abs(old_viewport.start_col - start_col) > self.buffer_cols):
            # Lade neue Zellen
            self._load_viewport_cells()
    
    def get_visible_dataframe(self) -> pd.DataFrame:
        """
        Gibt einen DataFrame mit den sichtbaren Zellen zurück
        
        Returns:
            pandas DataFrame mit sichtbaren Daten
        """
        data = []
        
        for row in range(self.viewport.start_row, self.viewport.end_row):
            row_data = []
            for col in range(self.viewport.start_col, self.viewport.end_col):
                cell = self.get_cell(row, col)
                row_data.append(cell.get_display_value())
            data.append(row_data)
        
        # Erstelle Spalten-Labels (A, B, C, ...)
        col_labels = [self._col_num_to_label(col) for col in range(
            self.viewport.start_col, self.viewport.end_col
        )]
        
        # Erstelle Zeilen-Labels (1, 2, 3, ...)
        row_labels = [str(row + 1) for row in range(
            self.viewport.start_row, self.viewport.end_row
        )]
        
        return pd.DataFrame(data, columns=col_labels, index=row_labels)
    
    def scroll_down(self, rows: int = 10):
        """
        Scrollt nach unten
        
        Args:
            rows: Anzahl Zeilen zum Scrollen
        """
        new_start = self.viewport.start_row + rows
        new_end = self.viewport.end_row + rows
        
        # Begrenze auf Matrix-Größe
        max_row = self.matrix.rows
        if new_end > max_row:
            new_end = max_row
            new_start = max(0, new_end - (self.viewport.end_row - self.viewport.start_row))
        
        self.set_viewport(new_start, new_end, self.viewport.start_col, self.viewport.end_col)
    
    def scroll_up(self, rows: int = 10):
        """
        Scrollt nach oben
        
        Args:
            rows: Anzahl Zeilen zum Scrollen
        """
        new_start = max(0, self.viewport.start_row - rows)
        new_end = new_start + (self.viewport.end_row - self.viewport.start_row)
        
        self.set_viewport(new_start, new_end, self.viewport.start_col, self.viewport.end_col)
    
    def scroll_right(self, cols: int = 5):
        """
        Scrollt nach rechts
        
        Args:
            cols: Anzahl Spalten zum Scrollen
        """
        new_start = self.viewport.start_col + cols
        new_end = self.viewport.end_col + cols
        
        # Begrenze auf Matrix-Größe
        max_col = self.matrix.columns
        if new_end > max_col:
            new_end = max_col
            new_start = max(0, new_end - (self.viewport.end_col - self.viewport.start_col))
        
        self.set_viewport(self.viewport.start_row, self.viewport.end_row, new_start, new_end)
    
    def scroll_left(self, cols: int = 5):
        """
        Scrollt nach links
        
        Args:
            cols: Anzahl Spalten zum Scrollen
        """
        new_start = max(0, self.viewport.start_col - cols)
        new_end = new_start + (self.viewport.end_col - self.viewport.start_col)
        
        self.set_viewport(self.viewport.start_row, self.viewport.end_row, new_start, new_end)
    
    def jump_to_cell(self, row: int, col: int):
        """
        Springt zu einer bestimmten Zelle
        
        Args:
            row: Zielzeile
            col: Zielspalte
        """
        # Berechne neuen Viewport mit Zelle in der Mitte
        viewport_height = self.viewport.end_row - self.viewport.start_row
        viewport_width = self.viewport.end_col - self.viewport.start_col
        
        new_start_row = max(0, row - viewport_height // 2)
        new_end_row = new_start_row + viewport_height
        
        new_start_col = max(0, col - viewport_width // 2)
        new_end_col = new_start_col + viewport_width
        
        self.set_viewport(new_start_row, new_end_row, new_start_col, new_end_col)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Gibt Cache-Statistiken zurück
        
        Returns:
            Dictionary mit Statistiken
        """
        return {
            **self.cache.get_cache_stats(),
            'viewport_size': self.viewport.get_cell_count(),
            'viewport_range': {
                'rows': (self.viewport.start_row, self.viewport.end_row),
                'cols': (self.viewport.start_col, self.viewport.end_col)
            }
        }
    
    def clear_cache(self):
        """Leert den Cache"""
        self.cache.clear()
    
    def refresh_viewport(self):
        """Lädt den aktuellen Viewport neu"""
        self.cache.clear()
        self._load_viewport_cells()
    
    @staticmethod
    def _col_num_to_label(col: int) -> str:
        """
        Konvertiert Spaltennummer zu Label (0 -> A, 1 -> B, ...)
        
        Args:
            col: Spaltennummer (0-basiert)
            
        Returns:
            Spalten-Label (A, B, C, ..., Z, AA, AB, ...)
        """
        label = ""
        col += 1  # Excel ist 1-basiert
        
        while col > 0:
            col -= 1
            label = chr(65 + (col % 26)) + label
            col //= 26
        
        return label


def create_lazy_loader(
    matrix: ExcelMatrix,
    viewport_rows: int = 100,
    viewport_cols: int = 26
) -> LazyGridLoader:
    """
    Factory-Funktion zum Erstellen eines LazyGridLoader
    
    Args:
        matrix: ExcelMatrix
        viewport_rows: Anzahl sichtbarer Zeilen
        viewport_cols: Anzahl sichtbarer Spalten
        
    Returns:
        LazyGridLoader-Instanz
    """
    return LazyGridLoader(
        matrix=matrix,
        viewport_rows=viewport_rows,
        viewport_cols=viewport_cols
    )