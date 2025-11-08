"""
Demo: Excel Product Pricing Integration

Demonstriert die Verwendung der Produktpreis-Berechnung aus Matrizen.
"""

from excel.excel_product_pricing import (
    calculate_product_price_from_matrix,
    get_price_preview,
    validate_matrix_for_product_pricing
)
from price_matrix_store import (
    create_matrix,
    add_row,
    add_column,
    set_cell_value,
    set_active_matrix,
    update_matrix_pricing_mode,
    delete_matrix
)


def demo_pauschal_pricing():
    """Demo: Pauschal-Preisberechnung"""
    print("\n" + "="*60)
    print("DEMO 1: Pauschal-Preisberechnung")
    print("="*60)
    
    # Erstelle Matrix
    matrix_id = create_matrix(
        "PV System Pauschalpreise",
        "Komplettpreise für PV-Systeme",
        pricing_mode='pauschal'
    )
    
    # Füge Zeilen hinzu (Modulanzahl)
    print("\n📊 Erstelle Preismatrix...")
    rows = {}
    for modules in [10, 15, 20, 25, 30]:
        rows[modules] = add_row(matrix_id, str(modules))
        print(f"  ✓ Zeile hinzugefügt: {modules} Module")
    
    # Füge Spalten hinzu (Speicher-Größen)
    cols = {}
    for storage in [5, 10, 15, 20]:
        cols[storage] = add_column(matrix_id, f"{storage}kWh")
        print(f"  ✓ Spalte hinzugefügt: {storage}kWh Speicher")
    
    # Setze Preise (Basis: 500€ pro Modul + 1000€ pro kWh Speicher)
    print("\n💰 Setze Preise...")
    for modules, row_id in rows.items():
        for storage, col_id in cols.items():
            price = modules * 500 + storage * 1000
            set_cell_value(matrix_id, row_id, col_id, float(price))
    print("  ✓ Alle Preise gesetzt")
    
    # Setze als aktiv
    set_active_matrix(matrix_id)
    print("\n✓ Matrix als aktiv gesetzt")
    
    # Validiere Matrix
    print("\n🔍 Validiere Matrix...")
    validation = validate_matrix_for_product_pricing()
    if validation['valid']:
        print("  ✓ Matrix ist gültig")
        print(f"  - Zeilen: {validation['info']['row_count']}")
        print(f"  - Spalten: {validation['info']['column_count']}")
        print(f"  - Zellen: {validation['info']['cell_count']}")
    
    # Berechne Beispiel-Preise
    print("\n💵 Berechne Preise...")
    
    # Beispiel 1: Exakte Übereinstimmung
    result = calculate_product_price_from_matrix("20", "10kWh")
    if result.is_valid():
        print(f"\n  20 Module + 10kWh Speicher:")
        print(f"    Preis: {result.total_price:,.2f}€")
        print(f"    Matrix: {result.matrix_name}")
        print(f"    Modus: {result.pricing_mode}")
    
    # Beispiel 2: Floor-Matching
    result = calculate_product_price_from_matrix("22", "10kWh")
    if result.is_valid():
        print(f"\n  22 Module + 10kWh Speicher (Floor-Matching):")
        print(f"    Preis: {result.total_price:,.2f}€")
        print(f"    Verwendete Zeile: {result.row_used} (angefragt: 22)")
        print(f"    Floor-Source: {result.row_floor_source}")
    
    # Beispiel 3: Verschiedene Speicher-Größen
    print("\n  Preise für 25 Module mit verschiedenen Speichern:")
    for storage in ["5kWh", "10kWh", "15kWh", "20kWh"]:
        result = calculate_product_price_from_matrix("25", storage)
        if result.is_valid():
            print(f"    {storage}: {result.total_price:,.2f}€")
    
    # Cleanup
    delete_matrix(matrix_id)
    print("\n✓ Demo abgeschlossen")


def demo_additiv_pricing():
    """Demo: Additiv-Preisberechnung mit Zubehör"""
    print("\n" + "="*60)
    print("DEMO 2: Additiv-Preisberechnung mit Zubehör")
    print("="*60)
    
    # Erstelle Matrix im Additiv-Modus
    matrix_id = create_matrix(
        "PV System Basis-Preise",
        "Basis-Preise ohne Zubehör",
        pricing_mode='additiv'
    )
    update_matrix_pricing_mode(
        matrix_id,
        'additiv',
        include_accessories=True,
        include_misc=True
    )
    
    print("\n📊 Erstelle Basis-Preismatrix (Additiv-Modus)...")
    
    # Füge Daten hinzu
    rows = {}
    for modules in [10, 20, 30]:
        rows[modules] = add_row(matrix_id, str(modules))
    
    cols = {}
    for storage in [5, 10, 15]:
        cols[storage] = add_column(matrix_id, f"{storage}kWh")
    
    # Setze Basis-Preise (nur Module + Speicher, ohne Zubehör)
    for modules, row_id in rows.items():
        for storage, col_id in cols.items():
            base_price = modules * 400 + storage * 800  # Niedrigere Basis-Preise
            set_cell_value(matrix_id, row_id, col_id, float(base_price))
    
    set_active_matrix(matrix_id)
    print("  ✓ Basis-Preise gesetzt")
    
    # Berechne mit verschiedenen Zubehör-Kombinationen
    print("\n💵 Berechne Preise mit Zubehör...")
    
    # Ohne Zubehör
    result = calculate_product_price_from_matrix("20", "10kWh")
    if result.is_valid():
        print(f"\n  20 Module + 10kWh (ohne Zubehör):")
        print(f"    Basis-Preis: {result.base_price:,.2f}€")
        print(f"    Gesamt: {result.total_price:,.2f}€")
    
    # Mit Zubehör
    result = calculate_product_price_from_matrix(
        "20", "10kWh",
        accessories_price=1500.0,
        misc_price=500.0
    )
    if result.is_valid():
        print(f"\n  20 Module + 10kWh (mit Zubehör):")
        print(f"    Basis-Preis: {result.base_price:,.2f}€")
        print(f"    Zubehör: {result.accessories_price:,.2f}€")
        print(f"    Sonstiges: {result.misc_price:,.2f}€")
        print(f"    Gesamt: {result.total_price:,.2f}€")
    
    # Mit nur Zubehör (Sonstiges ausgeschlossen)
    update_matrix_pricing_mode(
        matrix_id,
        'additiv',
        include_accessories=True,
        include_misc=False
    )
    
    result = calculate_product_price_from_matrix(
        "20", "10kWh",
        accessories_price=1500.0,
        misc_price=500.0
    )
    if result.is_valid():
        print(f"\n  20 Module + 10kWh (nur Zubehör, kein Sonstiges):")
        print(f"    Basis-Preis: {result.base_price:,.2f}€")
        print(f"    Zubehör: {result.accessories_price:,.2f}€")
        print(f"    Sonstiges: {result.misc_price:,.2f}€ (nicht einbezogen)")
        print(f"    Gesamt: {result.total_price:,.2f}€")
    
    # Cleanup
    delete_matrix(matrix_id)
    print("\n✓ Demo abgeschlossen")


def demo_price_preview():
    """Demo: Preis-Vorschau"""
    print("\n" + "="*60)
    print("DEMO 3: Preis-Vorschau")
    print("="*60)
    
    # Erstelle größere Matrix
    matrix_id = create_matrix("Große Preismatrix")
    
    print("\n📊 Erstelle große Matrix (10x8)...")
    
    # Füge viele Zeilen und Spalten hinzu
    rows = []
    for i in range(10):
        rows.append(add_row(matrix_id, f"{(i+1)*10}"))
    
    cols = []
    for i in range(8):
        cols.append(add_column(matrix_id, f"{(i+1)*5}kWh"))
    
    # Setze Preise
    for i, row_id in enumerate(rows):
        for j, col_id in enumerate(cols):
            price = (i + 1) * 1000 + (j + 1) * 500
            set_cell_value(matrix_id, row_id, col_id, float(price))
    
    set_active_matrix(matrix_id)
    print("  ✓ Matrix erstellt")
    
    # Hole Vorschau
    print("\n🔍 Hole Preis-Vorschau (erste 5x5)...")
    preview = get_price_preview(max_rows=5, max_cols=5)
    
    print(f"\n  Matrix: {preview['matrix_name']}")
    print(f"  Modus: {preview['pricing_mode']}")
    print(f"  Truncated: {preview['truncated']}")
    
    # Zeige Preise als Tabelle
    print("\n  Preis-Tabelle:")
    print("  " + "-" * 60)
    
    # Header
    header = "  Module  |"
    for col in preview['columns']:
        header += f" {col:>8} |"
    print(header)
    print("  " + "-" * 60)
    
    # Zeilen
    for row in preview['rows']:
        line = f"  {row:>7} |"
        for col in preview['columns']:
            price = preview['prices'].get((row, col))
            if price:
                line += f" {price:>7.0f}€ |"
            else:
                line += "        - |"
        print(line)
    
    print("  " + "-" * 60)
    
    # Cleanup
    delete_matrix(matrix_id)
    print("\n✓ Demo abgeschlossen")


def demo_error_handling():
    """Demo: Fehlerbehandlung"""
    print("\n" + "="*60)
    print("DEMO 4: Fehlerbehandlung")
    print("="*60)
    
    # Erstelle einfache Matrix
    matrix_id = create_matrix("Test Matrix")
    row_id = add_row(matrix_id, "10")
    col_id = add_column(matrix_id, "5kWh")
    set_cell_value(matrix_id, row_id, col_id, 1000.0)
    set_active_matrix(matrix_id)
    
    print("\n🔍 Teste verschiedene Fehlerszenarien...")
    
    # Fehler 1: Ungültige Spalte
    print("\n  1. Ungültige Spalte:")
    result = calculate_product_price_from_matrix("10", "999kWh")
    if not result.is_valid():
        print(f"    ❌ {result.error}")
    
    # Fehler 2: Nicht-numerische Zeile ohne Übereinstimmung
    print("\n  2. Nicht-numerische Zeile ohne Übereinstimmung:")
    result = calculate_product_price_from_matrix("ABC", "5kWh")
    if not result.is_valid():
        print(f"    ❌ {result.error}")
    
    # Erfolg: Gültige Anfrage
    print("\n  3. Gültige Anfrage:")
    result = calculate_product_price_from_matrix("10", "5kWh")
    if result.is_valid():
        print(f"    ✓ Preis: {result.total_price}€")
    
    # Cleanup
    delete_matrix(matrix_id)
    
    # Fehler 3: Keine aktive Matrix
    print("\n  4. Keine aktive Matrix:")
    result = calculate_product_price_from_matrix("10", "5kWh")
    if not result.is_valid():
        print(f"    ❌ {result.error}")
    
    print("\n✓ Demo abgeschlossen")


def main():
    """Führt alle Demos aus"""
    print("\n" + "="*60)
    print("Excel Product Pricing Integration - Demos")
    print("="*60)
    
    try:
        demo_pauschal_pricing()
        demo_additiv_pricing()
        demo_price_preview()
        demo_error_handling()
        
        print("\n" + "="*60)
        print("✓ Alle Demos erfolgreich abgeschlossen")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
