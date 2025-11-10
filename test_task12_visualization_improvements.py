"""
Test für Task 12: Visualisierungs-Verbesserungen

Dieser Test verifiziert die Implementierung von:
1. Farb-Unterscheidung für normale Module (dunkelblau)
2. Farb-Unterscheidung für ausgewählte Module (hellblau)
3. Farb-Unterscheidung für ungültige Positionen (rot)
4. Modul-Nummern Anzeige (optional)
5. Raster-Overlay (optional)

Requirements: 1.2, 8.5
"""

import sys
import traceback


def test_color_differentiation():
    """
    Test 1: Farb-Unterscheidung für verschiedene Modul-Zustände
    
    Requirements:
        - 1.2: Module haben erkennbare Farbe
    """
    print("\n=== Test 1: Farb-Unterscheidung ===")
    
    try:
        from utils.pv3d_plotly import create_pv_module_3d
        
        # Test 1.1: Normales Modul (dunkelblau)
        print("\n📋 Test 1.1: Normales Modul (dunkelblau #1a1a2e)")
        module_normal, vertices_normal = create_pv_module_3d(
            x=0.0, y=0.0, z=5.0,
            azimuth_deg=0, tilt_deg=30,
            color="#1a1a2e",
            selected=False,
            invalid=False,
            roof_type="Flachdach"
        )
        
        assert module_normal.color == "#1a1a2e", \
            f"Normale Modul-Farbe sollte #1a1a2e sein, ist aber {module_normal.color}"
        assert "PV Module" in module_normal.name, \
            f"Modul-Name sollte 'PV Module' enthalten, ist aber {module_normal.name}"
        print("✓ Normales Modul hat korrekte Farbe (dunkelblau)")
        
        # Test 1.2: Ausgewähltes Modul (hellblau)
        print("\n📋 Test 1.2: Ausgewähltes Modul (hellblau #4a90e2)")
        module_selected, vertices_selected = create_pv_module_3d(
            x=1.0, y=0.0, z=5.0,
            azimuth_deg=0, tilt_deg=30,
            color="#1a1a2e",
            selected=True,
            invalid=False,
            roof_type="Flachdach"
        )
        
        assert module_selected.color == "#4a90e2", \
            f"Ausgewählte Modul-Farbe sollte #4a90e2 sein, ist aber {module_selected.color}"
        assert "Ausgewählt" in module_selected.name, \
            f"Modul-Name sollte 'Ausgewählt' enthalten, ist aber {module_selected.name}"
        print("✓ Ausgewähltes Modul hat korrekte Farbe (hellblau)")
        
        # Test 1.3: Ungültiges Modul (rot)
        print("\n📋 Test 1.3: Ungültiges Modul (rot #e74c3c)")
        module_invalid, vertices_invalid = create_pv_module_3d(
            x=2.0, y=0.0, z=5.0,
            azimuth_deg=0, tilt_deg=30,
            color="#1a1a2e",
            selected=False,
            invalid=True,
            roof_type="Flachdach"
        )
        
        assert module_invalid.color == "#e74c3c", \
            f"Ungültige Modul-Farbe sollte #e74c3c sein, ist aber {module_invalid.color}"
        assert "Ungültig" in module_invalid.name, \
            f"Modul-Name sollte 'Ungültig' enthalten, ist aber {module_invalid.name}"
        print("✓ Ungültiges Modul hat korrekte Farbe (rot)")
        
        # Test 1.4: Priorität - Invalid überschreibt Selected
        print("\n📋 Test 1.4: Priorität - Invalid überschreibt Selected")
        module_both, vertices_both = create_pv_module_3d(
            x=3.0, y=0.0, z=5.0,
            azimuth_deg=0, tilt_deg=30,
            color="#1a1a2e",
            selected=True,
            invalid=True,
            roof_type="Flachdach"
        )
        
        assert module_both.color == "#e74c3c", \
            f"Ungültig sollte Priorität haben, Farbe sollte #e74c3c sein, ist aber {module_both.color}"
        print("✓ Invalid-Status hat Priorität über Selected-Status")
        
        print("\n✅ Test 1: Farb-Unterscheidung erfolgreich")
        return True
        
    except Exception as e:
        print(f"\n❌ Test 1 fehlgeschlagen: {e}")
        traceback.print_exc()
        return False


def test_module_numbers():
    """
    Test 2: Modul-Nummern Anzeige
    
    Requirements:
        - 8.5: Modul-Nummern anzeigen (optional)
    """
    print("\n=== Test 2: Modul-Nummern Anzeige ===")
    
    try:
        from utils.pv3d_plotly import create_pv_module_3d, create_module_number_annotation
        
        # Test 2.1: Modul ohne Nummer
        print("\n📋 Test 2.1: Modul ohne Nummer")
        module_no_number, _ = create_pv_module_3d(
            x=0.0, y=0.0, z=5.0,
            azimuth_deg=0, tilt_deg=30,
            color="#1a1a2e",
            selected=False,
            invalid=False,
            module_number=None,
            roof_type="Flachdach"
        )
        
        assert "#" not in module_no_number.name, \
            f"Modul ohne Nummer sollte keine # im Namen haben, ist aber {module_no_number.name}"
        print("✓ Modul ohne Nummer hat keinen Nummern-Suffix")
        
        # Test 2.2: Modul mit Nummer
        print("\n📋 Test 2.2: Modul mit Nummer")
        module_with_number, _ = create_pv_module_3d(
            x=1.0, y=0.0, z=5.0,
            azimuth_deg=0, tilt_deg=30,
            color="#1a1a2e",
            selected=False,
            invalid=False,
            module_number=42,
            roof_type="Flachdach"
        )
        
        assert "#42" in module_with_number.name, \
            f"Modul mit Nummer sollte '#42' im Namen haben, ist aber {module_with_number.name}"
        print("✓ Modul mit Nummer hat korrekten Nummern-Suffix")
        
        # Test 2.3: Modul-Nummern Annotation
        print("\n📋 Test 2.3: Modul-Nummern Annotation")
        annotation = create_module_number_annotation(
            x=0.0, y=0.0, z=5.0,
            module_number=123,
            offset_z=0.3
        )
        
        assert annotation.mode == 'text', \
            f"Annotation sollte Text-Modus haben, ist aber {annotation.mode}"
        assert annotation.text == ['123'] or annotation.text == ('123',), \
            f"Annotation sollte Text '123' haben, ist aber {annotation.text}"
        # Plotly can return tuples or lists, both are acceptable
        assert (annotation.x == [0.0] or annotation.x == (0.0,)), \
            f"Annotation X sollte [0.0] sein, ist aber {annotation.x}"
        assert (annotation.y == [0.0] or annotation.y == (0.0,)), \
            f"Annotation Y sollte [0.0] sein, ist aber {annotation.y}"
        assert (annotation.z == [5.3] or annotation.z == (5.3,)), \
            f"Annotation Z sollte [5.3] sein (5.0 + 0.3), ist aber {annotation.z}"
        print("✓ Modul-Nummern Annotation korrekt erstellt")
        
        print("\n✅ Test 2: Modul-Nummern Anzeige erfolgreich")
        return True
        
    except Exception as e:
        print(f"\n❌ Test 2 fehlgeschlagen: {e}")
        traceback.print_exc()
        return False


def test_grid_overlay():
    """
    Test 3: Raster-Overlay
    
    Requirements:
        - 8.5: Raster anzeigen (optional)
    """
    print("\n=== Test 3: Raster-Overlay ===")
    
    try:
        from utils.pv3d_plotly import create_placement_grid
        
        # Test 3.1: Raster-Erstellung
        print("\n📋 Test 3.1: Raster-Erstellung")
        grid = create_placement_grid(
            roof_length=10.0,
            roof_width=8.0,
            base_z=5.0,
            grid_spacing=1.0,
            color='rgba(128, 128, 128, 0.3)',
            line_width=1
        )
        
        assert grid.mode == 'lines', \
            f"Raster sollte Linien-Modus haben, ist aber {grid.mode}"
        assert len(grid.x) > 0, \
            "Raster sollte X-Koordinaten haben"
        assert len(grid.y) > 0, \
            "Raster sollte Y-Koordinaten haben"
        assert len(grid.z) > 0, \
            "Raster sollte Z-Koordinaten haben"
        print(f"✓ Raster erstellt mit {len(grid.x)} Punkten")
        
        # Test 3.2: Raster-Dimensionen
        print("\n📋 Test 3.2: Raster-Dimensionen")
        # Raster sollte von -5 bis +5 in X (10m) und -4 bis +4 in Y (8m) gehen
        x_coords = [x for x in grid.x if x is not None]
        y_coords = [y for y in grid.y if y is not None]
        
        assert min(x_coords) >= -5.0, \
            f"Raster X-Min sollte >= -5.0 sein, ist aber {min(x_coords)}"
        assert max(x_coords) <= 5.0, \
            f"Raster X-Max sollte <= 5.0 sein, ist aber {max(x_coords)}"
        assert min(y_coords) >= -4.0, \
            f"Raster Y-Min sollte >= -4.0 sein, ist aber {min(y_coords)}"
        assert max(y_coords) <= 4.0, \
            f"Raster Y-Max sollte <= 4.0 sein, ist aber {max(y_coords)}"
        print("✓ Raster-Dimensionen korrekt")
        
        # Test 3.3: Raster-Spacing
        print("\n📋 Test 3.3: Raster-Spacing")
        # Mit 1m Spacing sollten wir 11 vertikale Linien (X: -5 bis +5)
        # und 9 horizontale Linien (Y: -4 bis +4) haben
        # Jede Linie hat 3 Punkte (start, end, None)
        expected_points = (11 * 3) + (9 * 3)  # 60 Punkte
        actual_points = len(grid.x)
        print(f"  Erwartete Punkte: ~{expected_points}, Tatsächliche: {actual_points}")
        # Toleranz für Rundungsfehler
        assert abs(actual_points - expected_points) < 10, \
            f"Raster sollte ~{expected_points} Punkte haben, hat aber {actual_points}"
        print("✓ Raster-Spacing korrekt")
        
        print("\n✅ Test 3: Raster-Overlay erfolgreich")
        return True
        
    except Exception as e:
        print(f"\n❌ Test 3 fehlgeschlagen: {e}")
        traceback.print_exc()
        return False


def test_color_legend():
    """
    Test 4: Farb-Legende
    
    Requirements:
        - 1.2: Erkennbare Farben dokumentieren
    """
    print("\n=== Test 4: Farb-Legende ===")
    
    try:
        from utils.pv3d_plotly import create_color_legend
        
        # Test 4.1: Legende erstellen
        print("\n📋 Test 4.1: Legende erstellen")
        legend_items = create_color_legend()
        
        assert isinstance(legend_items, list), \
            f"Legende sollte Liste sein, ist aber {type(legend_items)}"
        assert len(legend_items) == 3, \
            f"Legende sollte 3 Einträge haben (Normal, Ausgewählt, Ungültig), hat aber {len(legend_items)}"
        print(f"✓ Legende erstellt mit {len(legend_items)} Einträgen")
        
        # Test 4.2: Legende-Einträge prüfen
        print("\n📋 Test 4.2: Legende-Einträge prüfen")
        names = [item.name for item in legend_items]
        colors = [item.marker.color for item in legend_items]
        
        assert "Normal" in names, \
            f"Legende sollte 'Normal' enthalten, hat aber {names}"
        assert "Ausgewählt" in names, \
            f"Legende sollte 'Ausgewählt' enthalten, hat aber {names}"
        assert "Ungültig" in names, \
            f"Legende sollte 'Ungültig' enthalten, hat aber {names}"
        
        assert "#1a1a2e" in colors, \
            f"Legende sollte dunkelblau (#1a1a2e) enthalten, hat aber {colors}"
        assert "#4a90e2" in colors, \
            f"Legende sollte hellblau (#4a90e2) enthalten, hat aber {colors}"
        assert "#e74c3c" in colors, \
            f"Legende sollte rot (#e74c3c) enthalten, hat aber {colors}"
        
        print("✓ Alle Legende-Einträge korrekt")
        
        # Test 4.3: Legende ist unsichtbar (nur für Legende)
        print("\n📋 Test 4.3: Legende ist unsichtbar")
        for item in legend_items:
            assert item.visible == 'legendonly', \
                f"Legende-Eintrag sollte 'legendonly' sein, ist aber {item.visible}"
        print("✓ Legende-Einträge sind unsichtbar (nur in Legende)")
        
        print("\n✅ Test 4: Farb-Legende erfolgreich")
        return True
        
    except Exception as e:
        print(f"\n❌ Test 4 fehlgeschlagen: {e}")
        traceback.print_exc()
        return False


def test_ui_options():
    """
    Test 5: UI-Optionen aktiviert
    
    Requirements:
        - 8.5: Visualisierungs-Optionen
    """
    print("\n=== Test 5: UI-Optionen aktiviert ===")
    
    try:
        from utils.pv3d_module_placement_ui import render_module_placement_panel
        import inspect
        
        # Test 5.1: Prüfe dass Checkboxen nicht mehr disabled sind
        print("\n📋 Test 5.1: Prüfe UI-Code")
        
        # Lese den Quellcode der Funktion
        source = inspect.getsource(render_module_placement_panel)
        
        # Prüfe dass "disabled=False" für beide Checkboxen vorhanden ist
        assert 'disabled=False' in source, \
            "UI sollte 'disabled=False' für Checkboxen enthalten"
        
        # Prüfe dass TASK 12 Kommentare vorhanden sind
        assert 'TASK 12' in source, \
            "UI sollte TASK 12 Kommentare enthalten"
        
        print("✓ UI-Optionen sind aktiviert (disabled=False)")
        print("✓ TASK 12 Kommentare vorhanden")
        
        print("\n✅ Test 5: UI-Optionen aktiviert erfolgreich")
        return True
        
    except Exception as e:
        print(f"\n❌ Test 5 fehlgeschlagen: {e}")
        traceback.print_exc()
        return False


def run_all_tests():
    """Führt alle Tests aus und gibt Zusammenfassung aus."""
    print("=" * 70)
    print("TASK 12: VISUALISIERUNGS-VERBESSERUNGEN - TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Farb-Unterscheidung", test_color_differentiation),
        ("Modul-Nummern Anzeige", test_module_numbers),
        ("Raster-Overlay", test_grid_overlay),
        ("Farb-Legende", test_color_legend),
        ("UI-Optionen aktiviert", test_ui_options),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Kritischer Fehler in Test '{test_name}': {e}")
            traceback.print_exc()
            results.append((test_name, False))
    
    # Zusammenfassung
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ BESTANDEN" if result else "❌ FEHLGESCHLAGEN"
        print(f"{status}: {test_name}")
    
    print(f"\nErgebnis: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("\n🎉 Alle Tests erfolgreich! Task 12 ist vollständig implementiert.")
        return True
    else:
        print(f"\n⚠️ {total - passed} Test(s) fehlgeschlagen. Bitte Fehler beheben.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
