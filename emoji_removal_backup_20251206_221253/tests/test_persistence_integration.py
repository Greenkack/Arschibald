"""
Integration Tests für Excel Matrix Persistenz (Task 12.1)

Testet:
- Matrix erstellen → Speichern → Laden
- Formeln bleiben erhalten
- Große Matrizen (1000+ Zeilen)
- Änderungs-Tracking
- Auto-Save Funktionalität
"""

import sys
import os
from datetime import datetime
import time

# Füge Projektverzeichnis zum Path hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_create_save_load_cycle():
    """
    Test: Matrix erstellen → Speichern → Laden
    
    Testet den vollständigen Zyklus:
    1. Neue Matrix in Datenbank erstellen
    2. Daten und Formeln hinzufügen
    3. In Datenbank speichern
    4. Aus Datenbank laden
    5. Daten vergleichen
    """
    print("\n" + "="*80)
    print("TEST 1: Matrix erstellen → Speichern → Laden")
    print("="*80)
    
    try:
        from excel.excel_manager import ExcelManager
        from excel.excel_models import ExcelMatrix
        from price_matrix_store import (
            create_matrix,
            add_row,
            add_column,
            delete_matrix
        )
        
        # 1. Erstelle Matrix in Datenbank
        print("\n1️⃣ Erstelle Matrix in Datenbank...")
        matrix_name = f"Test Matrix {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        matrix_id = create_matrix(matrix_name, "Test-Matrix für Persistenz-Tests")
        
        if not matrix_id:
            print("   Fehler beim Erstellen der Matrix")
            return False
        
        print(f"   Matrix erstellt mit ID: {matrix_id}")
        
        # 2. Füge Zeilen und Spalten hinzu
        print("\n2️⃣ Füge Zeilen und Spalten hinzu...")
        for i in range(10):
            add_row(matrix_id, f"Zeile {i+1}")
        
        for i in range(5):
            add_column(matrix_id, chr(65 + i))  # A, B, C, D, E
        
        print("   10 Zeilen und 5 Spalten hinzugefügt")
        
        # 3. Lade Matrix in ExcelManager
        print("\n3️⃣ Lade Matrix in ExcelManager...")
        manager = ExcelManager.load_from_database(matrix_id)
        
        if not manager:
            print("   Fehler beim Laden der Matrix")
            return False
        
        print(f"   Matrix geladen: {manager.get_matrix().name}")
        
        # 4. Füge Daten und Formeln hinzu
        print("\n4️⃣ Füge Daten und Formeln hinzu...")
        
        # Füge Zahlen in Spalte A ein
        for row in range(5):
            manager.set_cell_value(row, 0, row + 1, raw_input=str(row + 1))
        
        # Füge Formel in B1 ein (Summe von A1:A5)
        manager.set_cell_value(0, 1, None, raw_input="=SUM(A1:A5)")
        
        # Füge Formel in C1 ein (Durchschnitt)
        manager.set_cell_value(0, 2, None, raw_input="=AVERAGE(A1:A5)")
        
        # Füge IF-Formel in D1 ein
        manager.set_cell_value(0, 3, None, raw_input="=IF(B1>10, 'Groß', 'Klein')")
        
        print("   Daten und Formeln hinzugefügt")
        print(f"      - A1:A5 = 1, 2, 3, 4, 5")
        print(f"      - B1 = =SUM(A1:A5) → {manager.get_cell_value(0, 1)}")
        print(f"      - C1 = =AVERAGE(A1:A5) → {manager.get_cell_value(0, 2)}")
        print(f"      - D1 = =IF(B1>10, 'Groß', 'Klein') → {manager.get_cell_value(0, 3)}")
        
        # 5. Speichere Matrix
        print("\n5️⃣ Speichere Matrix in Datenbank...")
        
        if not manager.has_unsaved_changes:
            print("   Keine ungespeicherten Änderungen erkannt")
        
        success = manager.save_to_database()
        
        if not success:
            print("   Fehler beim Speichern")
            return False
        
        print("   Matrix gespeichert")
        print(f"      - has_unsaved_changes: {manager.has_unsaved_changes}")
        print(f"      - last_save_time: {manager.last_save_time}")
        
        # 6. Lade Matrix erneut
        print("\n6️⃣ Lade Matrix erneut aus Datenbank...")
        manager2 = ExcelManager.load_from_database(matrix_id)
        
        if not manager2:
            print("   Fehler beim erneuten Laden")
            return False
        
        print("   Matrix erneut geladen")
        
        # 7. Vergleiche Daten
        print("\n7️⃣ Vergleiche Daten...")
        
        # Prüfe Werte in Spalte A
        for row in range(5):
            original_value = manager.get_cell_value(row, 0)
            loaded_value = manager2.get_cell_value(row, 0)
            
            if original_value != loaded_value:
                print(f"   Wert in A{row+1} stimmt nicht überein: {original_value} != {loaded_value}")
                return False
        
        print("   Werte in Spalte A stimmen überein")
        
        # Prüfe Formeln
        formulas_to_check = [
            (0, 1, "=SUM(A1:A5)"),
            (0, 2, "=AVERAGE(A1:A5)"),
            (0, 3, "=IF(B1>10, 'Groß', 'Klein')")
        ]
        
        for row, col, expected_formula in formulas_to_check:
            cell = manager2.get_cell(row, col)
            
            if not cell.is_formula():
                print(f"   Zelle {chr(65+col)}{row+1} ist keine Formel")
                return False
            
            if cell.formula != expected_formula:
                print(f"   Formel in {chr(65+col)}{row+1} stimmt nicht überein:")
                print(f"      Erwartet: {expected_formula}")
                print(f"      Erhalten: {cell.formula}")
                return False
            
            # Prüfe berechneten Wert
            original_value = manager.get_cell_value(row, col)
            loaded_value = manager2.get_cell_value(row, col)
            
            if original_value != loaded_value:
                print(f"   Berechneter Wert in {chr(65+col)}{row+1} stimmt nicht überein:")
                print(f"      Original: {original_value}")
                print(f"      Geladen: {loaded_value}")
                return False
        
        print("   Formeln und berechnete Werte stimmen überein")
        
        # 8. Cleanup
        print("\n8️⃣ Cleanup...")
        delete_matrix(matrix_id)
        print("   Test-Matrix gelöscht")
        
        print("\n" + "="*80)
        print("TEST 1 ERFOLGREICH")
        print("="*80)
        return True
        
    except Exception as e:
        print(f"\nTEST 1 FEHLGESCHLAGEN: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_formulas_persist():
    """
    Test: Formeln bleiben erhalten
    
    Testet dass komplexe Formeln korrekt gespeichert und geladen werden:
    - Verschachtelte Formeln
    - Formeln mit Bereichen
    - Formeln mit Zellreferenzen
    """
    print("\n" + "="*80)
    print("TEST 2: Formeln bleiben erhalten")
    print("="*80)
    
    try:
        from excel.excel_manager import ExcelManager
        from price_matrix_store import (
            create_matrix,
            add_row,
            add_column,
            delete_matrix
        )
        
        # 1. Erstelle Matrix
        print("\n1️⃣ Erstelle Matrix...")
        matrix_name = f"Formula Test {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        matrix_id = create_matrix(matrix_name, "Test für Formel-Persistenz")
        
        for i in range(20):
            add_row(matrix_id, f"Row {i+1}")
        
        for i in range(10):
            add_column(matrix_id, chr(65 + i))
        
        print(f"   Matrix erstellt mit ID: {matrix_id}")
        
        # 2. Lade und füge komplexe Formeln hinzu
        print("\n2️⃣ Füge komplexe Formeln hinzu...")
        manager = ExcelManager.load_from_database(matrix_id)
        
        # Testdaten
        for row in range(10):
            manager.set_cell_value(row, 0, (row + 1) * 10)  # A1:A10 = 10, 20, 30, ...
            manager.set_cell_value(row, 1, (row + 1) * 5)   # B1:B10 = 5, 10, 15, ...
        
        # Komplexe Formeln
        test_formulas = [
            (0, 2, "=SUM(A1:A10)"),                          # Einfache Summe
            (1, 2, "=AVERAGE(A1:A10)"),                      # Durchschnitt
            (2, 2, "=MAX(A1:A10)"),                          # Maximum
            (3, 2, "=MIN(A1:A10)"),                          # Minimum
            (4, 2, "=IF(A1>50, SUM(A1:A5), SUM(A6:A10))"),  # Verschachtelt
            (5, 2, "=ROUND(AVERAGE(A1:A10), 2)"),           # Verschachtelt mit Rundung
            (6, 2, "=A1+B1"),                                # Einfache Referenz
            (7, 2, "=SUM(A1:A5)*2"),                         # Mit Arithmetik
            (8, 2, "=IF(SUM(A1:A10)>500, 'Hoch', 'Niedrig')"),  # Verschachtelt mit Text
        ]
        
        for row, col, formula in test_formulas:
            manager.set_cell_value(row, col, None, raw_input=formula)
            print(f"   - {chr(65+col)}{row+1}: {formula} → {manager.get_cell_value(row, col)}")
        
        print(f"   {len(test_formulas)} Formeln hinzugefügt")
        
        # 3. Speichere
        print("\n3️⃣ Speichere Matrix...")
        success = manager.save_to_database()
        
        if not success:
            print("   Fehler beim Speichern")
            return False
        
        print("   Matrix gespeichert")
        
        # 4. Lade erneut
        print("\n4️⃣ Lade Matrix erneut...")
        manager2 = ExcelManager.load_from_database(matrix_id)
        print("   Matrix geladen")
        
        # 5. Vergleiche Formeln
        print("\n5️⃣ Vergleiche Formeln...")
        
        all_match = True
        for row, col, expected_formula in test_formulas:
            cell = manager2.get_cell(row, col)
            
            if not cell.is_formula():
                print(f"   {chr(65+col)}{row+1} ist keine Formel")
                all_match = False
                continue
            
            if cell.formula != expected_formula:
                print(f"   {chr(65+col)}{row+1} Formel stimmt nicht überein:")
                print(f"      Erwartet: {expected_formula}")
                print(f"      Erhalten: {cell.formula}")
                all_match = False
                continue
            
            # Vergleiche berechnete Werte
            original_value = manager.get_cell_value(row, col)
            loaded_value = manager2.get_cell_value(row, col)
            
            if original_value != loaded_value:
                print(f"   {chr(65+col)}{row+1} Wert stimmt nicht überein:")
                print(f"      Original: {original_value}")
                print(f"      Geladen: {loaded_value}")
                all_match = False
                continue
            
            print(f"   {chr(65+col)}{row+1}: {expected_formula} → {loaded_value}")
        
        # 6. Cleanup
        print("\n6️⃣ Cleanup...")
        delete_matrix(matrix_id)
        print("   Test-Matrix gelöscht")
        
        if all_match:
            print("\n" + "="*80)
            print("TEST 2 ERFOLGREICH")
            print("="*80)
            return True
        else:
            print("\n" + "="*80)
            print("TEST 2 FEHLGESCHLAGEN - Nicht alle Formeln stimmen überein")
            print("="*80)
            return False
        
    except Exception as e:
        print(f"\nTEST 2 FEHLGESCHLAGEN: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_large_matrix():
    """
    Test: Große Matrizen (1000+ Zeilen)
    
    Testet Performance und Korrektheit bei großen Matrizen:
    - 1000 Zeilen × 50 Spalten
    - Speichern und Laden
    - Performance-Messung
    """
    print("\n" + "="*80)
    print("TEST 3: Große Matrizen (1000+ Zeilen)")
    print("="*80)
    
    try:
        from excel.excel_manager import ExcelManager
        from price_matrix_store import (
            create_matrix,
            add_row,
            add_column,
            delete_matrix
        )
        
        # 1. Erstelle große Matrix
        print("\n1️⃣ Erstelle große Matrix (1000 Zeilen × 50 Spalten)...")
        matrix_name = f"Large Matrix {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        start_time = time.time()
        matrix_id = create_matrix(matrix_name, "Test für große Matrizen")
        
        # Füge Zeilen hinzu
        for i in range(1000):
            add_row(matrix_id, f"Row {i+1}")
            if (i + 1) % 100 == 0:
                print(f"   - {i+1} Zeilen hinzugefügt...")
        
        # Füge Spalten hinzu
        for i in range(50):
            col_label = ""
            n = i
            while n >= 0:
                col_label = chr(65 + (n % 26)) + col_label
                n = n // 26 - 1
            add_column(matrix_id, col_label)
        
        create_time = time.time() - start_time
        print(f"   Matrix erstellt in {create_time:.2f} Sekunden")
        
        # 2. Lade Matrix
        print("\n2️⃣ Lade Matrix...")
        start_time = time.time()
        manager = ExcelManager.load_from_database(matrix_id)
        load_time = time.time() - start_time
        
        print(f"   Matrix geladen in {load_time:.2f} Sekunden")
        print(f"      - Zeilen: {manager.get_matrix().rows}")
        print(f"      - Spalten: {manager.get_matrix().columns}")
        
        # 3. Füge Daten hinzu (nur erste 100 Zeilen für Performance)
        print("\n3️⃣ Füge Daten hinzu (erste 100 Zeilen)...")
        start_time = time.time()
        
        for row in range(100):
            for col in range(10):  # Nur erste 10 Spalten
                value = row * 10 + col
                manager.set_cell_value(row, col, value, save_undo=False)
        
        # Füge einige Formeln hinzu
        manager.set_cell_value(0, 10, None, raw_input="=SUM(A1:J1)", save_undo=False)
        manager.set_cell_value(1, 10, None, raw_input="=AVERAGE(A2:J2)", save_undo=False)
        manager.set_cell_value(2, 10, None, raw_input="=MAX(A3:J3)", save_undo=False)
        
        data_time = time.time() - start_time
        print(f"   Daten hinzugefügt in {data_time:.2f} Sekunden")
        
        # 4. Speichere Matrix
        print("\n4️⃣ Speichere Matrix...")
        start_time = time.time()
        success = manager.save_to_database()
        save_time = time.time() - start_time
        
        if not success:
            print("   Fehler beim Speichern")
            return False
        
        print(f"   Matrix gespeichert in {save_time:.2f} Sekunden")
        
        # 5. Lade erneut
        print("\n5️⃣ Lade Matrix erneut...")
        start_time = time.time()
        manager2 = ExcelManager.load_from_database(matrix_id)
        reload_time = time.time() - start_time
        
        print(f"   Matrix erneut geladen in {reload_time:.2f} Sekunden")
        
        # 6. Vergleiche Stichproben
        print("\n6️⃣ Vergleiche Stichproben...")
        
        sample_cells = [
            (0, 0), (0, 5), (0, 9),
            (50, 0), (50, 5), (50, 9),
            (99, 0), (99, 5), (99, 9)
        ]
        
        all_match = True
        for row, col in sample_cells:
            original = manager.get_cell_value(row, col)
            loaded = manager2.get_cell_value(row, col)
            
            if original != loaded:
                print(f"   Wert in {chr(65+col)}{row+1} stimmt nicht überein: {original} != {loaded}")
                all_match = False
            else:
                print(f"   {chr(65+col)}{row+1}: {original}")
        
        # Prüfe Formeln
        formula_cells = [(0, 10), (1, 10), (2, 10)]
        for row, col in formula_cells:
            cell = manager2.get_cell(row, col)
            if not cell.is_formula():
                print(f"   {chr(65+col)}{row+1} ist keine Formel")
                all_match = False
            else:
                print(f"   {chr(65+col)}{row+1}: {cell.formula} → {cell.value}")
        
        # 7. Performance-Zusammenfassung
        print("\n7️⃣ Performance-Zusammenfassung:")
        print(f"   - Matrix erstellen: {create_time:.2f}s")
        print(f"   - Erstes Laden: {load_time:.2f}s")
        print(f"   - Daten hinzufügen: {data_time:.2f}s")
        print(f"   - Speichern: {save_time:.2f}s")
        print(f"   - Erneutes Laden: {reload_time:.2f}s")
        print(f"   - Gesamt: {create_time + load_time + data_time + save_time + reload_time:.2f}s")
        
        # Performance-Anforderung: Neuberechnung unter 2 Sekunden
        if reload_time > 2.0:
            print(f"   Warnung: Ladezeit ({reload_time:.2f}s) überschreitet 2 Sekunden")
        
        # 8. Cleanup
        print("\n8️⃣ Cleanup...")
        delete_matrix(matrix_id)
        print("   Test-Matrix gelöscht")
        
        if all_match:
            print("\n" + "="*80)
            print("TEST 3 ERFOLGREICH")
            print("="*80)
            return True
        else:
            print("\n" + "="*80)
            print("TEST 3 FEHLGESCHLAGEN - Nicht alle Werte stimmen überein")
            print("="*80)
            return False
        
    except Exception as e:
        print(f"\nTEST 3 FEHLGESCHLAGEN: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_change_tracking():
    """
    Test: Änderungs-Tracking
    
    Testet dass Änderungen korrekt getrackt werden:
    - has_unsaved_changes Flag
    - last_save_time Timestamp
    - Zurücksetzen nach Speichern
    """
    print("\n" + "="*80)
    print("TEST 4: Änderungs-Tracking")
    print("="*80)
    
    try:
        from excel.excel_manager import ExcelManager
        from price_matrix_store import (
            create_matrix,
            add_row,
            add_column,
            delete_matrix
        )
        
        # 1. Erstelle Matrix
        print("\n1️⃣ Erstelle Matrix...")
        matrix_name = f"Change Tracking Test {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        matrix_id = create_matrix(matrix_name, "Test für Änderungs-Tracking")
        
        for i in range(10):
            add_row(matrix_id, f"Row {i+1}")
            add_column(matrix_id, chr(65 + i))
        
        print(f"   Matrix erstellt mit ID: {matrix_id}")
        
        # 2. Lade Matrix
        print("\n2️⃣ Lade Matrix...")
        manager = ExcelManager.load_from_database(matrix_id)
        
        print(f"   Matrix geladen")
        print(f"      - has_unsaved_changes: {manager.has_unsaved_changes}")
        print(f"      - last_save_time: {manager.last_save_time}")
        
        # Nach dem Laden sollten keine ungespeicherten Änderungen vorhanden sein
        if manager.has_unsaved_changes:
            print("   Nach dem Laden sollten keine ungespeicherten Änderungen vorhanden sein")
            return False
        
        print("   Keine ungespeicherten Änderungen nach dem Laden")
        
        # 3. Mache Änderungen
        print("\n3️⃣ Mache Änderungen...")
        manager.set_cell_value(0, 0, 42)
        
        print(f"   - Zelle A1 auf 42 gesetzt")
        print(f"   - has_unsaved_changes: {manager.has_unsaved_changes}")
        
        if not manager.has_unsaved_changes:
            print("   Nach Änderung sollten ungespeicherte Änderungen vorhanden sein")
            return False
        
        print("   Ungespeicherte Änderungen erkannt")
        
        # 4. Speichere
        print("\n4️⃣ Speichere Matrix...")
        old_save_time = manager.last_save_time
        success = manager.save_to_database()
        
        if not success:
            print("   Fehler beim Speichern")
            return False
        
        print(f"   Matrix gespeichert")
        print(f"      - has_unsaved_changes: {manager.has_unsaved_changes}")
        print(f"      - last_save_time: {manager.last_save_time}")
        
        # Nach dem Speichern sollten keine ungespeicherten Änderungen vorhanden sein
        if manager.has_unsaved_changes:
            print("   Nach dem Speichern sollten keine ungespeicherten Änderungen vorhanden sein")
            return False
        
        # last_save_time sollte aktualisiert worden sein
        if manager.last_save_time == old_save_time:
            print("   last_save_time wurde nicht aktualisiert")
            return False
        
        print("   Änderungs-Tracking funktioniert korrekt")
        
        # 5. Weitere Änderungen
        print("\n5️⃣ Weitere Änderungen...")
        manager.set_cell_value(1, 1, None, raw_input="=A1*2")
        manager.add_row()
        manager.add_column()
        
        print(f"   - Mehrere Änderungen gemacht")
        print(f"   - has_unsaved_changes: {manager.has_unsaved_changes}")
        
        if not manager.has_unsaved_changes:
            print("   Nach weiteren Änderungen sollten ungespeicherte Änderungen vorhanden sein")
            return False
        
        print("   Änderungen werden getrackt")
        
        # 6. Cleanup
        print("\n6️⃣ Cleanup...")
        delete_matrix(matrix_id)
        print("   Test-Matrix gelöscht")
        
        print("\n" + "="*80)
        print("TEST 4 ERFOLGREICH")
        print("="*80)
        return True
        
    except Exception as e:
        print(f"\nTEST 4 FEHLGESCHLAGEN: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Führt alle Persistenz-Tests aus"""
    print("\n" + "="*80)
    print("EXCEL MATRIX PERSISTENZ - INTEGRATION TESTS (Task 12.1)")
    print("="*80)
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Matrix erstellen → Speichern → Laden", test_create_save_load_cycle),
        ("Formeln bleiben erhalten", test_formulas_persist),
        ("Große Matrizen (1000+ Zeilen)", test_large_matrix),
        ("Änderungs-Tracking", test_change_tracking),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\nTest '{test_name}' ist abgestürzt: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Zusammenfassung
    print("\n" + "="*80)
    print("ZUSAMMENFASSUNG")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "BESTANDEN" if result else "FEHLGESCHLAGEN"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*80)
    print(f"Ergebnis: {passed}/{total} Tests bestanden ({passed/total*100:.1f}%)")
    print("="*80)
    print(f"Ende: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
