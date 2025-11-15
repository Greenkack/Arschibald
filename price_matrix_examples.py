"""
Preismatrix-Beispiele

Dieses Modul stellt Beispiel-Matrizen mit Dummy-Daten bereit.
Diese können als Vorlage für neue Matrizen verwendet werden.
"""

from typing import Dict, List, Any
from price_matrix_store import create_matrix, add_row, add_column, set_cell_value


def create_example_matrix_small() -> int:
    """
    Erstellt eine Beispiel-Matrix für kleine Anlagen (10-25 Module)
    
    Returns:
        Matrix-ID der erstellten Matrix
    
    Requirement: 2.5
    """
    # Erstelle Matrix
    matrix_id = create_matrix(
        name="Beispiel: Kleine Anlage (10-25 Module)",
        description="Beispiel-Matrix mit Dummy-Daten für kleine PV-Anlagen"
    )
    
    if not matrix_id:
        raise ValueError("Fehler beim Erstellen der Matrix")
    
    # Definiere Struktur
    storage_models = ["10kWh", "15kWh", "20kWh", "Kein Speicher"]
    module_counts = [10, 15, 20, 25]
    
    # Preise (Dummy-Daten)
    prices = {
        10: [15000.00, 17500.00, 20000.00, 12000.00],
        15: [18000.00, 20500.00, 23000.00, 15000.00],
        20: [21000.00, 23500.00, 26000.00, 18000.00],
        25: [24000.00, 26500.00, 29000.00, 21000.00]
    }
    
    # Erstelle Spalten (Speichermodelle)
    column_ids = {}
    
    # Spalte A: Modulanzahl (Header)
    col_a_id = add_column(matrix_id, "Modulanzahl", position=0)
    column_ids["Modulanzahl"] = col_a_id
    
    # Weitere Spalten: Speichermodelle
    for idx, model in enumerate(storage_models):
        col_id = add_column(matrix_id, model, position=idx + 1)
        column_ids[model] = col_id
    
    # Erstelle Zeilen
    row_ids = {}
    
    # Zeile 1: Header (Speichermodelle)
    row_1_id = add_row(matrix_id, "Modulanzahl", position=0)
    row_ids["header"] = row_1_id
    
    # Fülle Header-Zeile mit Speichermodell-Namen
    for model in storage_models:
        set_cell_value(
            matrix_id,
            row_1_id,
            column_ids[model],
            value=None,
            raw_input=model,
            data_type='text'
        )
    
    # Weitere Zeilen: Modulanzahlen
    for idx, count in enumerate(module_counts):
        row_id = add_row(matrix_id, str(count), position=idx + 1)
        row_ids[count] = row_id
        
        # Spalte A: Modulanzahl
        set_cell_value(
            matrix_id,
            row_id,
            col_a_id,
            value=float(count),
            raw_input=str(count),
            data_type='number'
        )
        
        # Preis-Zellen
        for model_idx, model in enumerate(storage_models):
            price = prices[count][model_idx]
            set_cell_value(
                matrix_id,
                row_id,
                column_ids[model],
                value=price,
                raw_input=str(price),
                data_type='number'
            )
    
    return matrix_id


def create_example_matrix_medium() -> int:
    """
    Erstellt eine Beispiel-Matrix für mittlere Anlagen (30-50 Module)
    
    Returns:
        Matrix-ID der erstellten Matrix
    
    Requirement: 2.5
    """
    matrix_id = create_matrix(
        name="Beispiel: Mittlere Anlage (30-50 Module)",
        description="Beispiel-Matrix mit Dummy-Daten für mittlere PV-Anlagen"
    )
    
    if not matrix_id:
        raise ValueError("Fehler beim Erstellen der Matrix")
    
    storage_models = ["10kWh", "15kWh", "20kWh", "Kein Speicher"]
    module_counts = [30, 35, 40, 45, 50]
    
    prices = {
        30: [27000.00, 29500.00, 32000.00, 24000.00],
        35: [30000.00, 32500.00, 35000.00, 27000.00],
        40: [33000.00, 35500.00, 38000.00, 30000.00],
        45: [36000.00, 38500.00, 41000.00, 33000.00],
        50: [39000.00, 41500.00, 44000.00, 36000.00]
    }
    
    column_ids = {}
    col_a_id = add_column(matrix_id, "Modulanzahl", position=0)
    column_ids["Modulanzahl"] = col_a_id
    
    for idx, model in enumerate(storage_models):
        col_id = add_column(matrix_id, model, position=idx + 1)
        column_ids[model] = col_id
    
    row_ids = {}
    row_1_id = add_row(matrix_id, "Modulanzahl", position=0)
    row_ids["header"] = row_1_id
    
    for model in storage_models:
        set_cell_value(
            matrix_id,
            row_1_id,
            column_ids[model],
            value=None,
            raw_input=model,
            data_type='text'
        )
    
    for idx, count in enumerate(module_counts):
        row_id = add_row(matrix_id, str(count), position=idx + 1)
        row_ids[count] = row_id
        
        set_cell_value(
            matrix_id,
            row_id,
            col_a_id,
            value=float(count),
            raw_input=str(count),
            data_type='number'
        )
        
        for model_idx, model in enumerate(storage_models):
            price = prices[count][model_idx]
            set_cell_value(
                matrix_id,
                row_id,
                column_ids[model],
                value=price,
                raw_input=str(price),
                data_type='number'
            )
    
    return matrix_id


def create_example_matrix_large() -> int:
    """
    Erstellt eine Beispiel-Matrix für große Anlagen (60-100 Module)
    
    Returns:
        Matrix-ID der erstellten Matrix
    
    Requirement: 2.5
    """
    matrix_id = create_matrix(
        name="Beispiel: Große Anlage (60-100 Module)",
        description="Beispiel-Matrix mit Dummy-Daten für große PV-Anlagen"
    )
    
    if not matrix_id:
        raise ValueError("Fehler beim Erstellen der Matrix")
    
    storage_models = ["10kWh", "15kWh", "20kWh", "Kein Speicher"]
    module_counts = [60, 70, 80, 90, 100]
    
    prices = {
        60: [45000.00, 47500.00, 50000.00, 42000.00],
        70: [51000.00, 53500.00, 56000.00, 48000.00],
        80: [57000.00, 59500.00, 62000.00, 54000.00],
        90: [63000.00, 65500.00, 68000.00, 60000.00],
        100: [69000.00, 71500.00, 74000.00, 66000.00]
    }
    
    column_ids = {}
    col_a_id = add_column(matrix_id, "Modulanzahl", position=0)
    column_ids["Modulanzahl"] = col_a_id
    
    for idx, model in enumerate(storage_models):
        col_id = add_column(matrix_id, model, position=idx + 1)
        column_ids[model] = col_id
    
    row_ids = {}
    row_1_id = add_row(matrix_id, "Modulanzahl", position=0)
    row_ids["header"] = row_1_id
    
    for model in storage_models:
        set_cell_value(
            matrix_id,
            row_1_id,
            column_ids[model],
            value=None,
            raw_input=model,
            data_type='text'
        )
    
    for idx, count in enumerate(module_counts):
        row_id = add_row(matrix_id, str(count), position=idx + 1)
        row_ids[count] = row_id
        
        set_cell_value(
            matrix_id,
            row_id,
            col_a_id,
            value=float(count),
            raw_input=str(count),
            data_type='number'
        )
        
        for model_idx, model in enumerate(storage_models):
            price = prices[count][model_idx]
            set_cell_value(
                matrix_id,
                row_id,
                column_ids[model],
                value=price,
                raw_input=str(price),
                data_type='number'
            )
    
    return matrix_id


def get_matrix_structure_help() -> str:
    """
    Gibt Hilfetext zur Matrix-Struktur zurück
    
    Returns:
        Formatierter Hilfetext
    
    Requirement: 2.5
    """
    return """
📋 PREISMATRIX-STRUKTUR

Die Preismatrix definiert schlüsselfertige Preise basierend auf:
• Modulanzahl (Zeilen)
• Speichermodell (Spalten)

AUFBAU:

Spalte A (Position 0):
  → Modulanzahl (numerisch)
  → Beispiel: 10, 15, 20, 25

Zeile 1 (Position 0):
  → Speichermodell-Namen (Text)
  → Beispiel: "10kWh", "15kWh", "Kein Speicher"

Preis-Zellen (ab B2):
  → Schlüsselfertige Preise (numerisch)
  → Beispiel: 15000.00, 17500.00

REGELN:

1. Spalte A: Nur Zahlen (Modulanzahl)
2. Zeile 1: Nur Text (Speichermodell-Namen)
3. Mindestens eine "Kein Speicher" Spalte
4. Preis-Zellen: Nur Zahlen oder leer

BEISPIEL:

         A          B        C        D
    Modulanzahl  10kWh    15kWh    Kein Speicher
1   Modulanzahl  10kWh    15kWh    Kein Speicher
2   10           15000    17500    12000
3   15           18000    20500    15000
4   20           21000    23500    18000

TIPPS:

• Verwenden Sie die Beispiel-Matrizen als Vorlage
• Füllen Sie alle Preis-Zellen aus
• Sortieren Sie Modulanzahlen aufsteigend
• Verwenden Sie eindeutige Speichermodell-Namen

📖 Weitere Informationen: docs/PRICE_MATRIX_STRUCTURE_GUIDE.md
"""


def get_quick_help_tooltips() -> Dict[str, str]:
    """
    Gibt Tooltip-Texte für verschiedene UI-Elemente zurück
    
    Returns:
        Dictionary mit Tooltip-Texten
    
    Requirement: 2.5
    """
    return {
        'column_a': (
            "Spalte A: Modulanzahl\n\n"
            "Hier tragen Sie die Anzahl der PV-Module ein.\n"
            "Verwenden Sie nur numerische Werte (z.B. 10, 15, 20).\n\n"
            "Gültig: 10, 15, 20.5\n"
            "Ungültig: 'zehn', '10-15', leer"
        ),
        'row_1': (
            "Zeile 1: Speichermodelle\n\n"
            "Hier tragen Sie die Namen der Batteriespeicher-Modelle ein.\n"
            "Verwenden Sie Text-Werte (z.B. '10kWh', 'BYD HVS 10.2').\n\n"
            "Gültig: '10kWh', 'BYD HVS 10.2', 'Kein Speicher'\n"
            "Ungültig: leer, nur Zahlen"
        ),
        'price_cells': (
            "Preis-Zellen\n\n"
            "Hier tragen Sie die schlüsselfertigen Preise ein.\n"
            "Verwenden Sie nur numerische Werte (z.B. 15000, 15000.50).\n\n"
            "Gültig: 15000, 15000.50, 15.000,50\n"
            "Ungültig: '15000 EUR', 'ca. 15000', Formeln"
        ),
        'no_storage': (
            "'Kein Speicher' Spalte\n\n"
            "Mindestens eine Spalte muss für Konfigurationen ohne\n"
            "Batteriespeicher vorhanden sein.\n\n"
            "Erkannte Bezeichnungen:\n"
            "• 'Kein Speicher'\n"
            "• 'Ohne Speicher'\n"
            "• 'No Storage'\n"
            "• 'None'"
        ),
        'validation': (
            "Matrix-Validierung\n\n"
            "Die Matrix wird automatisch validiert:\n"
            "• Spalte A: Numerische Werte\n"
            "• Zeile 1: Text-Werte\n"
            "• 'Kein Speicher' Spalte vorhanden\n"
            "• Preis-Zellen: Numerisch oder leer\n\n"
            "Fehler werden rot markiert."
        ),
        'example_matrix': (
            "Beispiel-Matrix erstellen\n\n"
            "Erstellt eine vorgefertigte Matrix mit Dummy-Daten.\n"
            "Verwenden Sie diese als Vorlage für Ihre eigene Matrix.\n\n"
            "Verfügbare Beispiele:\n"
            "• Kleine Anlage (10-25 Module)\n"
            "• Mittlere Anlage (30-50 Module)\n"
            "• Große Anlage (60-100 Module)"
        )
    }


__all__ = [
    'create_example_matrix_small',
    'create_example_matrix_medium',
    'create_example_matrix_large',
    'get_matrix_structure_help',
    'get_quick_help_tooltips'
]
