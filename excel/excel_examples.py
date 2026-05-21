"""
Excel Integration - Example Matrices

Dieses Modul stellt Beispiel-Matrizen bereit die Benutzer
als Vorlagen verwenden können.
"""

from typing import Dict, List, Any


# Beispiel-Matrizen Definitionen
EXAMPLE_MATRICES = {
    "einfache_preisliste": {
        "name": "Einfache Preisliste",
        "description": "Grundlegende Preisliste mit Produkten und Preisen",
        "rows": 10,
        "columns": 5,
        "data": {
            # Header
            (0, 0): {"value": "Produkt", "type": "text"},
            (0, 1): {"value": "Einzelpreis", "type": "text"},
            (0, 2): {"value": "Menge", "type": "text"},
            (0, 3): {"value": "Gesamt", "type": "text"},
            (0, 4): {"value": "MwSt. 19%", "type": "text"},
            
            # Daten
            (1, 0): {"value": "PV-Modul 400W", "type": "text"},
            (1, 1): {"value": 250, "type": "number"},
            (1, 2): {"value": 20, "type": "number"},
            (1, 3): {"formula": "=B2*C2", "type": "formula"},
            (1, 4): {"formula": "=D2*0.19", "type": "formula"},
            
            (2, 0): {"value": "Wechselrichter 10kW", "type": "text"},
            (2, 1): {"value": 1500, "type": "number"},
            (2, 2): {"value": 1, "type": "number"},
            (2, 3): {"formula": "=B3*C3", "type": "formula"},
            (2, 4): {"formula": "=D3*0.19", "type": "formula"},
            
            (3, 0): {"value": "Speicher 10kWh", "type": "text"},
            (3, 1): {"value": 5000, "type": "number"},
            (3, 2): {"value": 1, "type": "number"},
            (3, 3): {"formula": "=B4*C4", "type": "formula"},
            (3, 4): {"formula": "=D4*0.19", "type": "formula"},
            
            (4, 0): {"value": "Montagesystem", "type": "text"},
            (4, 1): {"value": 800, "type": "number"},
            (4, 2): {"value": 1, "type": "number"},
            (4, 3): {"formula": "=B5*C5", "type": "formula"},
            (4, 4): {"formula": "=D5*0.19", "type": "formula"},
            
            # Summen
            (6, 0): {"value": "Summe Netto", "type": "text"},
            (6, 3): {"formula": "=SUM(D2:D5)", "type": "formula"},
            
            (7, 0): {"value": "Summe MwSt.", "type": "text"},
            (7, 3): {"formula": "=SUM(E2:E5)", "type": "formula"},
            
            (8, 0): {"value": "Summe Brutto", "type": "text"},
            (8, 3): {"formula": "=D7+D8", "type": "formula"},
        }
    },
    
    "staffelpreise": {
        "name": "Staffelpreise nach Modulanzahl",
        "description": "Preismatrix mit Staffelpreisen basierend auf Modulanzahl",
        "rows": 12,
        "columns": 6,
        "data": {
            # Header
            (0, 0): {"value": "Module", "type": "text"},
            (0, 1): {"value": "Ohne Speicher", "type": "text"},
            (0, 2): {"value": "5 kWh", "type": "text"},
            (0, 3): {"value": "10 kWh", "type": "text"},
            (0, 4): {"value": "15 kWh", "type": "text"},
            (0, 5): {"value": "20 kWh", "type": "text"},
            
            # Staffelpreise
            (1, 0): {"value": "10", "type": "number"},
            (1, 1): {"value": 8000, "type": "number"},
            (1, 2): {"value": 13000, "type": "number"},
            (1, 3): {"value": 18000, "type": "number"},
            (1, 4): {"value": 23000, "type": "number"},
            (1, 5): {"value": 28000, "type": "number"},
            
            (2, 0): {"value": "15", "type": "number"},
            (2, 1): {"value": 11000, "type": "number"},
            (2, 2): {"value": 16000, "type": "number"},
            (2, 3): {"value": 21000, "type": "number"},
            (2, 4): {"value": 26000, "type": "number"},
            (2, 5): {"value": 31000, "type": "number"},
            
            (3, 0): {"value": "20", "type": "number"},
            (3, 1): {"value": 14000, "type": "number"},
            (3, 2): {"value": 19000, "type": "number"},
            (3, 3): {"value": 24000, "type": "number"},
            (3, 4): {"value": 29000, "type": "number"},
            (3, 5): {"value": 34000, "type": "number"},
            
            (4, 0): {"value": "25", "type": "number"},
            (4, 1): {"value": 16500, "type": "number"},
            (4, 2): {"value": 21500, "type": "number"},
            (4, 3): {"value": 26500, "type": "number"},
            (4, 4): {"value": 31500, "type": "number"},
            (4, 5): {"value": 36500, "type": "number"},
            
            (5, 0): {"value": "30", "type": "number"},
            (5, 1): {"value": 19000, "type": "number"},
            (5, 2): {"value": 24000, "type": "number"},
            (5, 3): {"value": 29000, "type": "number"},
            (5, 4): {"value": 34000, "type": "number"},
            (5, 5): {"value": 39000, "type": "number"},
            
            # Preis pro Modul Berechnung
            (7, 0): {"value": "Preis/Modul bei 20:", "type": "text"},
            (7, 1): {"formula": "=B4/A4", "type": "formula"},
            
            (8, 0): {"value": "Ersparnis 30 vs 10:", "type": "text"},
            (8, 1): {"formula": "=B2-B6", "type": "formula"},
        }
    },
    
    "kalkulation_mit_formeln": {
        "name": "Kalkulation mit Formeln",
        "description": "Beispiel für komplexe Berechnungen mit verschachtelten Formeln",
        "rows": 15,
        "columns": 4,
        "data": {
            # Header
            (0, 0): {"value": "Position", "type": "text"},
            (0, 1): {"value": "Wert", "type": "text"},
            (0, 2): {"value": "Berechnung", "type": "text"},
            (0, 3): {"value": "Ergebnis", "type": "text"},
            
            # Eingabewerte
            (1, 0): {"value": "Modulanzahl", "type": "text"},
            (1, 1): {"value": 25, "type": "number"},
            
            (2, 0): {"value": "Modulleistung (W)", "type": "text"},
            (2, 1): {"value": 400, "type": "number"},
            
            (3, 0): {"value": "Preis pro Modul", "type": "text"},
            (3, 1): {"value": 250, "type": "number"},
            
            (4, 0): {"value": "Wechselrichter", "type": "text"},
            (4, 1): {"value": 1500, "type": "number"},
            
            (5, 0): {"value": "Montage", "type": "text"},
            (5, 1): {"value": 2000, "type": "number"},
            
            # Berechnungen
            (7, 0): {"value": "Gesamtleistung", "type": "text"},
            (7, 2): {"value": "Module * Leistung / 1000", "type": "text"},
            (7, 3): {"formula": "=B2*B3/1000", "type": "formula"},
            
            (8, 0): {"value": "Materialkosten", "type": "text"},
            (8, 2): {"value": "Module * Preis", "type": "text"},
            (8, 3): {"formula": "=B2*B4", "type": "formula"},
            
            (9, 0): {"value": "Gesamtkosten", "type": "text"},
            (9, 2): {"value": "Material + WR + Montage", "type": "text"},
            (9, 3): {"formula": "=D9+B5+B6", "type": "formula"},
            
            (10, 0): {"value": "Preis pro kWp", "type": "text"},
            (10, 2): {"value": "Gesamtkosten / Leistung", "type": "text"},
            (10, 3): {"formula": "=D10/D8", "type": "formula"},
            
            (12, 0): {"value": "Rabatt ab 20 Module", "type": "text"},
            (12, 2): {"value": "IF(Module>=20, 10%, 0%)", "type": "text"},
            (12, 3): {"formula": "=IF(B2>=20, D10*0.1, 0)", "type": "formula"},
            
            (13, 0): {"value": "Endpreis", "type": "text"},
            (13, 2): {"value": "Gesamtkosten - Rabatt", "type": "text"},
            (13, 3): {"formula": "=D10-D13", "type": "formula"},
        }
    },
    
    "lookup_beispiel": {
        "name": "VLOOKUP Beispiel",
        "description": "Demonstration von VLOOKUP für Preissuche",
        "rows": 12,
        "columns": 5,
        "data": {
            # Preistabelle
            (0, 0): {"value": "Produkt-ID", "type": "text"},
            (0, 1): {"value": "Produktname", "type": "text"},
            (0, 2): {"value": "Preis", "type": "text"},
            
            (1, 0): {"value": "M400", "type": "text"},
            (1, 1): {"value": "Modul 400W", "type": "text"},
            (1, 2): {"value": 250, "type": "number"},
            
            (2, 0): {"value": "M450", "type": "text"},
            (2, 1): {"value": "Modul 450W", "type": "text"},
            (2, 2): {"value": 280, "type": "number"},
            
            (3, 0): {"value": "WR10", "type": "text"},
            (3, 1): {"value": "Wechselrichter 10kW", "type": "text"},
            (3, 2): {"value": 1500, "type": "number"},
            
            (4, 0): {"value": "SP10", "type": "text"},
            (4, 1): {"value": "Speicher 10kWh", "type": "text"},
            (4, 2): {"value": 5000, "type": "number"},
            
            # Lookup-Beispiel
            (6, 0): {"value": "Suche Produkt:", "type": "text"},
            (6, 1): {"value": "M400", "type": "text"},
            
            (7, 0): {"value": "Gefundener Name:", "type": "text"},
            (7, 1): {"formula": "=VLOOKUP(B7, A2:C5, 2, FALSE)", "type": "formula"},
            
            (8, 0): {"value": "Gefundener Preis:", "type": "text"},
            (8, 1): {"formula": "=VLOOKUP(B7, A2:C5, 3, FALSE)", "type": "formula"},
            
            (10, 0): {"value": "Menge:", "type": "text"},
            (10, 1): {"value": 20, "type": "number"},
            
            (11, 0): {"value": "Gesamtpreis:", "type": "text"},
            (11, 1): {"formula": "=B9*B11", "type": "formula"},
        }
    }
}


def get_example_matrix(example_key: str) -> Dict[str, Any]:
    """
    Gibt eine Beispiel-Matrix zurück
    
    Args:
        example_key: Schlüssel der Beispiel-Matrix
        
    Returns:
        Dictionary mit Matrix-Daten oder None
    """
    return EXAMPLE_MATRICES.get(example_key)


def get_all_examples() -> Dict[str, Dict[str, Any]]:
    """
    Gibt alle Beispiel-Matrizen zurück
    
    Returns:
        Dictionary mit allen Beispielen
    """
    return EXAMPLE_MATRICES


def create_example_matrix_in_db(example_key: str) -> int:
    """
    Erstellt eine Beispiel-Matrix in der Datenbank
    
    Args:
        example_key: Schlüssel der Beispiel-Matrix
        
    Returns:
        ID der erstellten Matrix oder None bei Fehler
    """
    example = get_example_matrix(example_key)
    
    if not example:
        return None
    
    try:
        from price_matrix_store import (
            create_matrix,
            add_row,
            add_column,
            set_cell_value
        )
        
        # Erstelle Matrix
        matrix_id = create_matrix(
            name=example['name'],
            description=example['description']
        )
        
        # Erstelle Zeilen
        for row_idx in range(example['rows']):
            add_row(matrix_id, str(row_idx + 1))
        
        # Erstelle Spalten
        column_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        for col_idx in range(example['columns']):
            add_column(matrix_id, column_labels[col_idx])
        
        # Lade Matrix-Struktur
        from price_matrix_store import get_matrix_full
        matrix_data = get_matrix_full(matrix_id)
        
        # Erstelle Mapping
        row_id_map = {r['position']: r['id'] for r in matrix_data['rows']}
        col_id_map = {c['position']: c['id'] for c in matrix_data['columns']}
        
        # Fülle Zellen
        for (row, col), cell_data in example['data'].items():
            if row in row_id_map and col in col_id_map:
                row_id = row_id_map[row]
                col_id = col_id_map[col]
                
                if 'formula' in cell_data:
                    # Formel
                    set_cell_value(
                        matrix_id,
                        row_id,
                        col_id,
                        None,
                        raw_input=cell_data['formula']
                    )
                else:
                    # Wert
                    set_cell_value(
                        matrix_id,
                        row_id,
                        col_id,
                        cell_data['value'],
                        raw_input=str(cell_data['value'])
                    )
        
        return matrix_id
        
    except Exception as e:
        print(f"Fehler beim Erstellen der Beispiel-Matrix: {str(e)}")
        return None


def get_example_list() -> List[Dict[str, str]]:
    """
    Gibt eine Liste aller Beispiele mit Namen und Beschreibung zurück
    
    Returns:
        Liste von Dictionaries mit 'key', 'name' und 'description'
    """
    examples = []
    
    for key, example in EXAMPLE_MATRICES.items():
        examples.append({
            'key': key,
            'name': example['name'],
            'description': example['description']
        })
    
    return examples
