"""
Excel Integration - Data Models

Dieses Modul definiert die Datenmodelle für die Excel-Integration.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime


@dataclass
class Cell:
    """
    Repräsentiert eine einzelne Zelle in der Excel-Matrix
    
    Attributes:
        row: Zeilennummer (0-basiert)
        col: Spaltennummer (0-basiert)
        value: Berechneter Wert der Zelle
        formula: Excel-Formel (falls vorhanden, beginnt mit '=')
        raw_input: Ursprüngliche Benutzereingabe
        formatted_value: Formatierter Anzeigewert
        data_type: Datentyp ('text', 'number', 'date', 'formula', 'error')
        style: Optionale Formatierungsinformationen
        error: Fehlermeldung falls Formel fehlerhaft
    """
    row: int
    col: int
    value: Any = None
    formula: Optional[str] = None
    raw_input: Optional[str] = None
    formatted_value: Optional[str] = None
    data_type: str = "text"
    style: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def is_formula(self) -> bool:
        """Prüft ob die Zelle eine Formel enthält"""
        return self.formula is not None and self.formula.startswith('=')
    
    def is_error(self) -> bool:
        """Prüft ob die Zelle einen Fehler enthält"""
        return self.error is not None
    
    def get_display_value(self) -> str:
        """
        Gibt den Anzeigewert der Zelle zurück
        
        Returns:
            Formatierter String für die Anzeige
        """
        if self.is_error():
            return self.error
        
        if self.formatted_value is not None:
            return self.formatted_value
        
        if self.value is not None:
            return str(self.value)
        
        return ""
    
    def get_cell_reference(self) -> str:
        """
        Gibt die Zellreferenz im A1-Format zurück
        
        Returns:
            Zellreferenz z.B. 'A1', 'B2', 'AA10'
        """
        from excel.excel_utils import cell_to_a1
        return cell_to_a1(self.row, self.col)


@dataclass
class ExcelMatrix:
    """
    Repräsentiert eine vollständige Excel-Matrix
    
    Attributes:
        id: Eindeutige ID der Matrix (aus Datenbank)
        name: Name der Matrix
        description: Beschreibung der Matrix
        rows: Anzahl der Zeilen
        columns: Anzahl der Spalten
        cells: Dictionary mit Zellen, Key ist (row, col) Tupel
        metadata: Zusätzliche Metadaten
        created_at: Erstellungszeitpunkt
        updated_at: Letzter Änderungszeitpunkt
    """
    id: Optional[int] = None
    name: str = "Neue Matrix"
    description: str = ""
    rows: int = 100
    columns: int = 26
    cells: Dict[Tuple[int, int], Cell] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def get_cell(self, row: int, col: int) -> Cell:
        """
        Gibt eine Zelle zurück, erstellt leere Zelle falls nicht vorhanden
        
        Args:
            row: Zeilennummer (0-basiert)
            col: Spaltennummer (0-basiert)
            
        Returns:
            Cell-Objekt
        """
        if (row, col) not in self.cells:
            self.cells[(row, col)] = Cell(row=row, col=col)
        return self.cells[(row, col)]
    
    def set_cell(self, row: int, col: int, cell: Cell):
        """
        Setzt eine Zelle in der Matrix
        
        Args:
            row: Zeilennummer (0-basiert)
            col: Spaltennummer (0-basiert)
            cell: Cell-Objekt
        """
        self.cells[(row, col)] = cell
    
    def get_cell_value(self, row: int, col: int) -> Any:
        """
        Gibt den Wert einer Zelle zurück
        
        Args:
            row: Zeilennummer (0-basiert)
            col: Spaltennummer (0-basiert)
            
        Returns:
            Zellwert oder None
        """
        cell = self.get_cell(row, col)
        return cell.value
    
    def set_cell_value(self, row: int, col: int, value: Any, raw_input: Optional[str] = None):
        """
        Setzt den Wert einer Zelle
        
        Args:
            row: Zeilennummer (0-basiert)
            col: Spaltennummer (0-basiert)
            value: Zu setzender Wert
            raw_input: Optionale Benutzereingabe
        """
        cell = self.get_cell(row, col)
        cell.value = value
        if raw_input is not None:
            cell.raw_input = raw_input
            # Prüfe ob Formel
            if raw_input.startswith('='):
                cell.formula = raw_input
                cell.data_type = "formula"
            else:
                cell.formula = None
                # Bestimme Datentyp
                if isinstance(value, (int, float)):
                    cell.data_type = "number"
                elif isinstance(value, datetime):
                    cell.data_type = "date"
                else:
                    cell.data_type = "text"
    
    def get_all_cells(self) -> List[Cell]:
        """
        Gibt alle Zellen der Matrix zurück
        
        Returns:
            Liste aller Cell-Objekte
        """
        return list(self.cells.values())
    
    def get_cells_with_formulas(self) -> List[Cell]:
        """
        Gibt alle Zellen mit Formeln zurück
        
        Returns:
            Liste aller Zellen die Formeln enthalten
        """
        return [cell for cell in self.cells.values() if cell.is_formula()]
    
    def clear_cell(self, row: int, col: int):
        """
        Löscht den Inhalt einer Zelle
        
        Args:
            row: Zeilennummer (0-basiert)
            col: Spaltennummer (0-basiert)
        """
        if (row, col) in self.cells:
            del self.cells[(row, col)]
    
    def get_used_range(self) -> Tuple[int, int, int, int]:
        """
        Gibt den benutzten Bereich der Matrix zurück
        
        Returns:
            Tupel (min_row, min_col, max_row, max_col)
        """
        if not self.cells:
            return (0, 0, 0, 0)
        
        rows = [cell.row for cell in self.cells.values()]
        cols = [cell.col for cell in self.cells.values()]
        
        return (min(rows), min(cols), max(rows), max(cols))


@dataclass
class FormulaError(Exception):
    """Basis-Klasse für Formel-Fehler"""
    message: str
    display: str = "#ERROR!"
    
    def __str__(self):
        return self.display


@dataclass
class SyntaxError(FormulaError):
    """Syntaxfehler in Formel"""
    display: str = "#ERROR!"


@dataclass
class ReferenceError(FormulaError):
    """Ungültige Zellreferenz"""
    display: str = "#REF!"


@dataclass
class DivisionByZeroError(FormulaError):
    """Division durch Null"""
    display: str = "#DIV/0!"


@dataclass
class CircularReferenceError(FormulaError):
    """Zirkelbezug erkannt"""
    display: str = "#CIRCULAR!"


@dataclass
class NameError(FormulaError):
    """Unbekannte Funktion"""
    display: str = "#NAME?"


@dataclass
class ValueError(FormulaError):
    """Falscher Wert-Typ"""
    display: str = "#VALUE!"
