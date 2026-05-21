"""
Excel Integration - Utility Functions

Hilfsfunktionen für die Excel-Integration, insbesondere für Zellreferenzen.
"""

import re
from typing import Tuple, List, Optional


def col_to_letter(col: int) -> str:
    """
    Konvertiert Spaltennummer zu Buchstaben (A1-Notation)
    
    Args:
        col: Spaltennummer (0-basiert)
        
    Returns:
        Spaltenbuchstabe(n) z.B. 'A', 'B', 'AA', 'ZZ'
        
    Examples:
        >>> col_to_letter(0)
        'A'
        >>> col_to_letter(25)
        'Z'
        >>> col_to_letter(26)
        'AA'
        >>> col_to_letter(701)
        'ZZ'
    """
    result = ""
    col += 1  # Excel ist 1-basiert
    
    while col > 0:
        col -= 1
        result = chr(65 + (col % 26)) + result
        col //= 26
    
    return result


def letter_to_col(letter: str) -> int:
    """
    Konvertiert Spaltenbuchstaben zu Nummer (0-basiert)
    
    Args:
        letter: Spaltenbuchstabe(n) z.B. 'A', 'B', 'AA'
        
    Returns:
        Spaltennummer (0-basiert)
        
    Examples:
        >>> letter_to_col('A')
        0
        >>> letter_to_col('Z')
        25
        >>> letter_to_col('AA')
        26
        >>> letter_to_col('ZZ')
        701
    """
    col = 0
    for char in letter.upper():
        col = col * 26 + (ord(char) - ord('A') + 1)
    return col - 1


def cell_to_a1(row: int, col: int) -> str:
    """
    Konvertiert Zeilen- und Spaltennummer zu A1-Notation
    
    Args:
        row: Zeilennummer (0-basiert)
        col: Spaltennummer (0-basiert)
        
    Returns:
        Zellreferenz im A1-Format z.B. 'A1', 'B2', 'AA10'
        
    Examples:
        >>> cell_to_a1(0, 0)
        'A1'
        >>> cell_to_a1(9, 1)
        'B10'
        >>> cell_to_a1(0, 26)
        'AA1'
    """
    return f"{col_to_letter(col)}{row + 1}"


def a1_to_cell(cell_ref: str) -> Tuple[int, int]:
    """
    Konvertiert A1-Notation zu Zeilen- und Spaltennummer
    
    Args:
        cell_ref: Zellreferenz im A1-Format z.B. 'A1', 'B2', 'AA10'
        
    Returns:
        Tupel (row, col) mit 0-basierten Indizes
        
    Raises:
        ValueError: Wenn die Zellreferenz ungültig ist
        
    Examples:
        >>> a1_to_cell('A1')
        (0, 0)
        >>> a1_to_cell('B10')
        (9, 1)
        >>> a1_to_cell('AA1')
        (0, 26)
    """
    match = re.match(r'^([A-Z]+)(\d+)$', cell_ref.upper())
    if not match:
        raise ValueError(f"Ungültige Zellreferenz: {cell_ref}")
    
    col_letter, row_str = match.groups()
    row = int(row_str) - 1  # Konvertiere zu 0-basiert
    col = letter_to_col(col_letter)
    
    return (row, col)


def parse_range(range_ref: str) -> List[Tuple[int, int]]:
    """
    Parst einen Zellbereich und gibt alle Zellen zurück
    
    Args:
        range_ref: Bereichsreferenz z.B. 'A1:B3', 'A1:A10'
        
    Returns:
        Liste von (row, col) Tupeln für alle Zellen im Bereich
        
    Raises:
        ValueError: Wenn die Bereichsreferenz ungültig ist
        
    Examples:
        >>> parse_range('A1:B2')
        [(0, 0), (0, 1), (1, 0), (1, 1)]
        >>> parse_range('A1:A3')
        [(0, 0), (1, 0), (2, 0)]
    """
    if ':' not in range_ref:
        # Einzelne Zelle
        row, col = a1_to_cell(range_ref)
        return [(row, col)]
    
    # Bereich
    start_ref, end_ref = range_ref.split(':')
    start_row, start_col = a1_to_cell(start_ref)
    end_row, end_col = a1_to_cell(end_ref)
    
    # Stelle sicher dass start <= end
    if start_row > end_row:
        start_row, end_row = end_row, start_row
    if start_col > end_col:
        start_col, end_col = end_col, start_col
    
    cells = []
    for row in range(start_row, end_row + 1):
        for col in range(start_col, end_col + 1):
            cells.append((row, col))
    
    return cells


def is_valid_cell_reference(cell_ref: str) -> bool:
    """
    Prüft ob eine Zellreferenz gültig ist
    
    Args:
        cell_ref: Zu prüfende Zellreferenz
        
    Returns:
        True wenn gültig, sonst False
        
    Examples:
        >>> is_valid_cell_reference('A1')
        True
        >>> is_valid_cell_reference('AA10')
        True
        >>> is_valid_cell_reference('1A')
        False
        >>> is_valid_cell_reference('ABC')
        False
    """
    try:
        a1_to_cell(cell_ref)
        return True
    except ValueError:
        return False


def is_valid_range_reference(range_ref: str) -> bool:
    """
    Prüft ob eine Bereichsreferenz gültig ist
    
    Args:
        range_ref: Zu prüfende Bereichsreferenz
        
    Returns:
        True wenn gültig, sonst False
        
    Examples:
        >>> is_valid_range_reference('A1:B2')
        True
        >>> is_valid_range_reference('A1')
        True
        >>> is_valid_range_reference('A1:B')
        False
    """
    try:
        parse_range(range_ref)
        return True
    except ValueError:
        return False


def extract_cell_references(formula: str) -> List[str]:
    """
    Extrahiert alle Zellreferenzen aus einer Formel
    
    Args:
        formula: Excel-Formel (mit oder ohne führendes '=')
        
    Returns:
        Liste aller gefundenen Zellreferenzen
        
    Examples:
        >>> extract_cell_references('=A1+B2')
        ['A1', 'B2']
        >>> extract_cell_references('=SUM(A1:A10)')
        ['A1:A10']
        >>> extract_cell_references('=IF(A1>10, B1, C1)')
        ['A1', 'B1', 'C1']
    """
    # Entferne führendes '=' falls vorhanden
    if formula.startswith('='):
        formula = formula[1:]
    
    # Regex für Zellreferenzen und Bereiche
    # Matcht: A1, AA10, A1:B2, etc.
    pattern = r'\b([A-Z]+\d+(?::[A-Z]+\d+)?)\b'
    
    matches = re.findall(pattern, formula.upper())
    return matches


def get_column_range(start_col: int, end_col: int) -> List[int]:
    """
    Gibt eine Liste von Spaltennummern zurück
    
    Args:
        start_col: Start-Spalte (0-basiert)
        end_col: End-Spalte (0-basiert, inklusiv)
        
    Returns:
        Liste von Spaltennummern
        
    Examples:
        >>> get_column_range(0, 2)
        [0, 1, 2]
    """
    return list(range(start_col, end_col + 1))


def get_row_range(start_row: int, end_row: int) -> List[int]:
    """
    Gibt eine Liste von Zeilennummern zurück
    
    Args:
        start_row: Start-Zeile (0-basiert)
        end_row: End-Zeile (0-basiert, inklusiv)
        
    Returns:
        Liste von Zeilennummern
        
    Examples:
        >>> get_row_range(0, 2)
        [0, 1, 2]
    """
    return list(range(start_row, end_row + 1))


def offset_cell_reference(cell_ref: str, row_offset: int, col_offset: int) -> str:
    """
    Verschiebt eine Zellreferenz um die angegebenen Offsets
    
    Args:
        cell_ref: Ursprüngliche Zellreferenz
        row_offset: Zeilen-Offset (kann negativ sein)
        col_offset: Spalten-Offset (kann negativ sein)
        
    Returns:
        Neue Zellreferenz
        
    Raises:
        ValueError: Wenn die resultierende Referenz ungültig ist
        
    Examples:
        >>> offset_cell_reference('A1', 1, 0)
        'A2'
        >>> offset_cell_reference('B2', 0, 1)
        'C2'
        >>> offset_cell_reference('B2', -1, -1)
        'A1'
    """
    row, col = a1_to_cell(cell_ref)
    new_row = row + row_offset
    new_col = col + col_offset
    
    if new_row < 0 or new_col < 0:
        raise ValueError(f"Ungültige Zellreferenz nach Offset: row={new_row}, col={new_col}")
    
    return cell_to_a1(new_row, new_col)


def update_formula_references(
    formula: str,
    row_offset: int,
    col_offset: int,
    min_row: Optional[int] = None,
    min_col: Optional[int] = None
) -> str:
    """
    Aktualisiert Zellreferenzen in einer Formel um die angegebenen Offsets
    
    Args:
        formula: Ursprüngliche Formel
        row_offset: Zeilen-Offset
        col_offset: Spalten-Offset
        min_row: Nur Zeilen >= min_row werden aktualisiert (None = alle)
        min_col: Nur Spalten >= min_col werden aktualisiert (None = alle)
        
    Returns:
        Formel mit aktualisierten Referenzen
        
    Examples:
        >>> update_formula_references('=A1+B1', 1, 0)
        '=A2+B2'
        >>> update_formula_references('=SUM(A1:A10)', 0, 1)
        '=SUM(B1:B10)'
        >>> update_formula_references('=A1+A2', 1, 0, min_row=1)
        '=A1+A3'
    """
    def replace_ref(match):
        """Callback für regex replacement"""
        ref = match.group(0)
        try:
            if ':' in ref:
                # Bereich
                start_ref, end_ref = ref.split(':')
                start_row, start_col = a1_to_cell(start_ref)
                end_row, end_col = a1_to_cell(end_ref)
                
                # Prüfe ob Start-Zelle aktualisiert werden soll
                if (min_row is None or start_row >= min_row) and \
                   (min_col is None or start_col >= min_col):
                    new_start = offset_cell_reference(
                        start_ref, row_offset, col_offset
                    )
                else:
                    new_start = start_ref
                
                # Prüfe ob End-Zelle aktualisiert werden soll
                if (min_row is None or end_row >= min_row) and \
                   (min_col is None or end_col >= min_col):
                    new_end = offset_cell_reference(
                        end_ref, row_offset, col_offset
                    )
                else:
                    new_end = end_ref
                
                return f"{new_start}:{new_end}"
            else:
                # Einzelne Zelle
                row, col = a1_to_cell(ref)
                
                # Prüfe ob Zelle aktualisiert werden soll
                if (min_row is None or row >= min_row) and \
                   (min_col is None or col >= min_col):
                    return offset_cell_reference(ref, row_offset, col_offset)
                else:
                    return ref
        except ValueError:
            # Behalte ungültige Referenzen
            return ref
    
    # Regex für Zellreferenzen und Bereiche mit Word Boundaries
    pattern = r'\b([A-Z]+\d+(?::[A-Z]+\d+)?)\b'
    
    return re.sub(pattern, replace_ref, formula, flags=re.IGNORECASE)
