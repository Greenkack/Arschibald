"""
Test für Task 14: Interaktive Modul-Auswahl und Bearbeitung

Dieser Test verifiziert die Implementierung der Modul-Auswahl-Funktionalität:
- Task 14.1: Modul-Auswahl-System
- Task 14.2: Modul-Hervorhebung
- Task 14.3: Eigenschaften-Panel
"""

import sys
import os

# Füge Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_module_selection_imports():
    """Test 14.1: Prüfe ob alle erforderlichen Imports verfügbar sind"""
    print("=" * 70)
    print("TEST 14.1: Modul-Auswahl-System - Imports")
    print("=" * 70)
    
    try:
        from utils.pv3d import (
            BuildingDims,
            LayoutConfig,
            AdvancedLayoutConfig,
            ModuleTransform,
            ModuleGroup,
            build_scene
        )
        print("[OK] Alle erforderlichen Klassen importiert")
        return True
    except ImportError as e:
        print(f"[ERROR] Import-Fehler: {e}")
        return False


def test_module_transform_creation():
    """Test 14.1: Teste ModuleTransform-Erstellung"""
    print("\n" + "=" * 70)
    print("TEST 14.1: ModuleTransform-Erstellung")
    print("=" * 70)
    
    try:
        from utils.pv3d import ModuleTransform
        
        # Erstelle ModuleTransform mit Standard-Werten
        transform1 = ModuleTransform(
            index=0,
            azimuth_deg=90.0,
            tilt_deg=25.0,
            offset_x=0.5,
            offset_y=-0.3,
            offset_z=0.1
        )
        
        print(f"[OK] ModuleTransform erstellt: Index={transform1.index}, "
              f"Azimuth={transform1.azimuth_deg}°, Tilt={transform1.tilt_deg}°")
        
        # Teste to_dict und from_dict
        transform_dict = transform1.to_dict()
        transform2 = ModuleTransform.from_dict(transform_dict)
        
        assert transform2.index == transform1.index
        assert transform2.azimuth_deg == transform1.azimuth_deg
        assert transform2.tilt_deg == transform1.tilt_deg
        
        print("[OK] to_dict() und from_dict() funktionieren korrekt")
        
        # Teste Validierung
        try:
            invalid_transform = ModuleTransform(
                index=0,
                azimuth_deg=400.0,  # Ungültig: > 360°
                tilt_deg=25.0
            )
            print("[ERROR] Validierung fehlgeschlagen: Ungültiger Azimuth wurde akzeptiert")
            return False
        except ValueError:
            print("[OK] Validierung funktioniert: Ungültige Werte werden abgelehnt")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_module_group_creation():
    """Test 14.1: Teste ModuleGroup-Erstellung"""
    print("\n" + "=" * 70)
    print("TEST 14.1: ModuleGroup-Erstellung")
    print("=" * 70)
    
    try:
        from utils.pv3d import ModuleGroup
        
        # Erstelle ModuleGroup
        group = ModuleGroup(
            name="Süddach",
            module_indices=[0, 1, 2, 3, 4],
            azimuth_deg=0.0,
            tilt_deg=15.0,
            color="#000000"
        )
        
        print(f"[OK] ModuleGroup erstellt: Name='{group.name}', "
              f"Module={len(group.module_indices)}")
        
        # Teste add_module
        group.add_module(5)
        assert 5 in group.module_indices
        print("[OK] add_module() funktioniert")
        
        # Teste remove_module
        group.remove_module(5)
        assert 5 not in group.module_indices
        print("[OK] remove_module() funktioniert")
        
        # Teste has_module
        assert group.has_module(0) == True
        assert group.has_module(99) == False
        print("[OK] has_module() funktioniert")
        
        # Teste to_dict und from_dict
        group_dict = group.to_dict()
        group2 = ModuleGroup.from_dict(group_dict)
        
        assert group2.name == group.name
        assert group2.module_indices == group.module_indices
        print("[OK] to_dict() und from_dict() funktionieren korrekt")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_advanced_layout_config():
    """Test 14.1: Teste AdvancedLayoutConfig mit Transformationen"""
    print("\n" + "=" * 70)
    print("TEST 14.1: AdvancedLayoutConfig mit Transformationen")
    print("=" * 70)
    
    try:
        from utils.pv3d import AdvancedLayoutConfig, ModuleTransform, ModuleGroup
        
        # Erstelle AdvancedLayoutConfig
        config = AdvancedLayoutConfig(
            mode="manual",
            use_garage=False,
            use_facade=False,
            enable_collision_detection=True,
            enable_shading_analysis=False
        )
        
        print("[OK] AdvancedLayoutConfig erstellt")
        
        # Füge ModuleTransform hinzu
        transform = ModuleTransform(
            index=0,
            azimuth_deg=45.0,
            tilt_deg=20.0,
            offset_x=0.5,
            offset_y=0.0,
            offset_z=0.0
        )
        config.module_transforms[0] = transform
        
        print(f"[OK] ModuleTransform hinzugefügt: {len(config.module_transforms)} Transform(s)")
        
        # Füge ModuleGroup hinzu
        group = ModuleGroup(
            name="Testgruppe",
            module_indices=[0, 1, 2],
            azimuth_deg=0.0,
            tilt_deg=15.0
        )
        config.module_groups["Testgruppe"] = group
        
        print(f"[OK] ModuleGroup hinzugefügt: {len(config.module_groups)} Gruppe(n)")
        
        # Teste JSON-Serialisierung
        json_str = config.to_json()
        config2 = AdvancedLayoutConfig.from_json(json_str)
        
        assert len(config2.module_transforms) == len(config.module_transforms)
        assert len(config2.module_groups) == len(config.module_groups)
        assert config2.enable_collision_detection == config.enable_collision_detection
        
        print("[OK] JSON-Serialisierung funktioniert korrekt")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_build_scene_with_selected_modules():
    """Test 14.2: Teste build_scene mit selected_modules Parameter"""
    print("\n" + "=" * 70)
    print("TEST 14.2: build_scene mit selected_modules (Hervorhebung)")
    print("=" * 70)
    
    try:
        from utils.pv3d import BuildingDims, LayoutConfig, build_scene
        
        # Erstelle Test-Daten
        dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        layout = LayoutConfig(mode="auto")
        project_data = {
            "project_details": {
                "roof_orientation": "Süd",
                "roof_inclination_deg": 30.0,
                "roof_covering_type": "Ziegel"
            }
        }
        
        # Teste ohne ausgewählte Module
        print("Test 1: Ohne ausgewählte Module...")
        plotter1, panels1 = build_scene(
            project_data=project_data,
            dims=dims,
            roof_type="Flachdach",
            module_quantity=10,
            layout_config=layout,
            off_screen=True,
            selected_modules=[]
        )
        
        print(f"[OK] Szene erstellt: {len(panels1.get('main', []))} Hauptdach-Module")
        plotter1.close()
        
        # Teste mit ausgewählten Modulen
        print("Test 2: Mit ausgewählten Modulen [0, 1, 2]...")
        plotter2, panels2 = build_scene(
            project_data=project_data,
            dims=dims,
            roof_type="Flachdach",
            module_quantity=10,
            layout_config=layout,
            off_screen=True,
            selected_modules=[0, 1, 2]
        )
        
        print(f"[OK] Szene mit Hervorhebung erstellt: {len(panels2.get('main', []))} Module")
        print("[OK] Module 0, 1, 2 sollten orange/gelb hervorgehoben sein")
        plotter2.close()
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_apply_module_transform():
    """Test 14.3: Teste apply_module_transform Funktion"""
    print("\n" + "=" * 70)
    print("TEST 14.3: apply_module_transform (Eigenschaften-Panel Backend)")
    print("=" * 70)
    
    try:
        from utils.pv3d import ModuleTransform, apply_module_transform
        
        # Erstelle Transform
        transform = ModuleTransform(
            index=0,
            azimuth_deg=90.0,
            tilt_deg=25.0,
            offset_x=0.5,
            offset_y=-0.3,
            offset_z=0.1
        )
        
        # Wende Transform an
        base_position = (5.0, 3.0, 6.0)
        panel = apply_module_transform(base_position, transform)
        
        print(f"[OK] Modul-Transform angewendet")
        print(f"  Basis-Position: {base_position}")
        print(f"  Azimuth: {transform.azimuth_deg}°")
        print(f"  Neigung: {transform.tilt_deg}°")
        print(f"  Offset: ({transform.offset_x}, {transform.offset_y}, {transform.offset_z})")
        print(f"  Resultat: Panel mit {panel.n_points} Punkten")
        
        # Prüfe ob Panel erstellt wurde
        assert panel is not None
        assert panel.n_points > 0
        
        print("[OK] apply_module_transform funktioniert korrekt")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Führe alle Tests aus"""
    print("\n" + "=" * 70)
    print("TASK 14: INTERAKTIVE MODUL-AUSWAHL UND BEARBEITUNG - TESTS")
    print("=" * 70)
    
    results = []
    
    # Task 14.1 Tests
    results.append(("14.1 - Imports", test_module_selection_imports()))
    results.append(("14.1 - ModuleTransform", test_module_transform_creation()))
    results.append(("14.1 - ModuleGroup", test_module_group_creation()))
    results.append(("14.1 - AdvancedLayoutConfig", test_advanced_layout_config()))
    
    # Task 14.2 Tests
    results.append(("14.2 - Hervorhebung", test_build_scene_with_selected_modules()))
    
    # Task 14.3 Tests
    results.append(("14.3 - apply_module_transform", test_apply_module_transform()))
    
    # Zusammenfassung
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[OK] BESTANDEN" if result else "[ERROR] FEHLGESCHLAGEN"
        print(f"{name}: {status}")
    
    print("\n" + "=" * 70)
    print(f"ERGEBNIS: {passed}/{total} Tests bestanden")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 Alle Tests erfolgreich! Task 14 ist vollständig implementiert.")
        return True
    else:
        print(f"\n[WARNING] {total - passed} Test(s) fehlgeschlagen. Bitte überprüfen Sie die Implementierung.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
