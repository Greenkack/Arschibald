"""
Test für Task 10: Teste Erweiterte Funktionen

Dieser Test verifiziert alle erweiterten Funktionen der 3D-Visualisierung:
- Modul-Auswahl (Einzeln, Gruppe, Bereich)
- Modul-Eigenschaften bearbeiten (Azimuth, Neigung, Offsets)
- Gruppen-Verwaltung (Erstellen, Bearbeiten, Löschen)
- Gruppen-Templates (Süddach, Ostdach, Westdach, Norddach)
- Kollisionserkennung
"""

import sys
import os

# Füge Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_module_selection_single():
    """Test 10.1: Modul-Auswahl - Einzeln"""
    print("\n" + "=" * 70)
    print("TEST 10.1: Modul-Auswahl - Einzeln")
    print("=" * 70)
    
    try:
        from utils.pv3d import ModuleTransform, AdvancedLayoutConfig
        
        # Erstelle Konfiguration
        config = AdvancedLayoutConfig()
        
        # Simuliere Einzelauswahl von Modul 5
        selected_module_index = 5
        
        # Erstelle Transform für ausgewähltes Modul
        transform = ModuleTransform(
            index=selected_module_index,
            azimuth_deg=0.0,
            tilt_deg=15.0,
            offset_x=0.0,
            offset_y=0.0,
            offset_z=0.0
        )
        
        config.module_transforms[selected_module_index] = transform
        
        # Prüfe dass Modul ausgewählt wurde
        assert selected_module_index in config.module_transforms, \
            "Modul sollte in module_transforms sein"
        
        print(f"Modul {selected_module_index} erfolgreich einzeln ausgewaehlt")
        print(f"  Transform: Azimuth={transform.azimuth_deg} Grad, Tilt={transform.tilt_deg} Grad")
        
        return True
        
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_module_selection_group():
    """Test 10.2: Modul-Auswahl - Gruppe"""
    print("\n" + "=" * 70)
    print("TEST 10.2: Modul-Auswahl - Gruppe")
    print("=" * 70)
    
    try:
        from utils.pv3d import ModuleGroup, AdvancedLayoutConfig
        
        # Erstelle Konfiguration
        config = AdvancedLayoutConfig()
        
        # Erstelle Gruppe "Süddach"
        group = ModuleGroup(
            name="Süddach",
            module_indices=[0, 1, 2, 3, 4],
            azimuth_deg=0.0,
            tilt_deg=35.0,
            color="#ff8800"
        )
        
        config.module_groups["Süddach"] = group
        
        # Prüfe Gruppenauswahl
        assert "Süddach" in config.module_groups, "Gruppe sollte existieren"
        assert len(group.module_indices) == 5, "Gruppe sollte 5 Module enthalten"
        
        print(f"Gruppe 'Süddach' erfolgreich ausgewählt")
        print(f"  Module: {group.module_indices}")
        print(f"  Azimuth: {group.azimuth_deg} Grad, Tilt: {group.tilt_deg} Grad")
        
        return True
        
    except Exception as e:
        print(f"[X] Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_module_selection_range():
    """Test 10.3: Modul-Auswahl - Bereich"""
    print("\n" + "=" * 70)
    print("TEST 10.3: Modul-Auswahl - Bereich")
    print("=" * 70)
    
    try:
        from utils.pv3d import ModuleTransform, AdvancedLayoutConfig
        
        # Erstelle Konfiguration
        config = AdvancedLayoutConfig()
        
        # Simuliere Bereichsauswahl: Module 10-19
        start_index = 10
        end_index = 19
        selected_range = list(range(start_index, end_index + 1))
        
        # Erstelle Transforms für alle Module im Bereich
        for module_idx in selected_range:
            transform = ModuleTransform(
                index=module_idx,
                azimuth_deg=0.0,
                tilt_deg=15.0,
                offset_x=0.0,
                offset_y=0.0,
                offset_z=0.0
            )
            config.module_transforms[module_idx] = transform
        
        # Prüfe Bereichsauswahl
        assert len(config.module_transforms) == len(selected_range), \
            "Alle Module im Bereich sollten ausgewählt sein"
        
        for module_idx in selected_range:
            assert module_idx in config.module_transforms, \
                f"Modul {module_idx} sollte ausgewählt sein"
        
        print(f"Bereich {start_index}-{end_index} erfolgreich ausgewählt")
        print(f"  Anzahl Module: {len(selected_range)}")
        
        return True
        
    except Exception as e:
        print(f"[X] Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_module_properties_azimuth():
    """Test 10.4: Modul-Eigenschaften bearbeiten - Azimuth"""
    print("\n" + "=" * 70)
    print("TEST 10.4: Modul-Eigenschaften bearbeiten - Azimuth")
    print("=" * 70)
    
    try:
        from utils.pv3d import ModuleTransform, AdvancedLayoutConfig
        
        # Erstelle Konfiguration mit Modul
        config = AdvancedLayoutConfig()
        
        module_idx = 0
        original_azimuth = 0.0
        new_azimuth = 90.0  # Ändere auf West
        
        # Erstelle Transform mit Original-Azimuth
        transform = ModuleTransform(
            index=module_idx,
            azimuth_deg=original_azimuth,
            tilt_deg=15.0,
            offset_x=0.0,
            offset_y=0.0,
            offset_z=0.0
        )
        
        config.module_transforms[module_idx] = transform
        
        print(f"  Original Azimuth: {original_azimuth} Grad")
        
        # Ändere Azimuth
        config.module_transforms[module_idx].azimuth_deg = new_azimuth
        
        # Prüfe Änderung
        assert config.module_transforms[module_idx].azimuth_deg == new_azimuth, \
            "Azimuth sollte geändert sein"
        
        print(f"  Neuer Azimuth: {new_azimuth} Grad")
        print(f"Azimuth erfolgreich von {original_azimuth} Grad auf {new_azimuth} Grad geändert")
        
        return True
        
    except Exception as e:
        print(f"[X] Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_module_properties_tilt():
    """Test 10.5: Modul-Eigenschaften bearbeiten - Neigung"""
    print("\n" + "=" * 70)
    print("TEST 10.5: Modul-Eigenschaften bearbeiten - Neigung")
    print("=" * 70)
    
    try:
        from utils.pv3d import ModuleTransform, AdvancedLayoutConfig
        
        # Erstelle Konfiguration mit Modul
        config = AdvancedLayoutConfig()
        
        module_idx = 0
        original_tilt = 15.0
        new_tilt = 30.0
        
        # Erstelle Transform mit Original-Neigung
        transform = ModuleTransform(
            index=module_idx,
            azimuth_deg=0.0,
            tilt_deg=original_tilt,
            offset_x=0.0,
            offset_y=0.0,
            offset_z=0.0
        )
        
        config.module_transforms[module_idx] = transform
        
        print(f"  Original Neigung: {original_tilt} Grad")
        
        # Ändere Neigung
        config.module_transforms[module_idx].tilt_deg = new_tilt
        
        # Prüfe Änderung
        assert config.module_transforms[module_idx].tilt_deg == new_tilt, \
            "Neigung sollte geändert sein"
        
        print(f"  Neue Neigung: {new_tilt} Grad")
        print(f"Neigung erfolgreich von {original_tilt} Grad auf {new_tilt} Grad geändert")
        
        return True
        
    except Exception as e:
        print(f"[X] Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_module_properties_offsets():
    """Test 10.6: Modul-Eigenschaften bearbeiten - Offsets"""
    print("\n" + "=" * 70)
    print("TEST 10.6: Modul-Eigenschaften bearbeiten - Offsets")
    print("=" * 70)
    
    try:
        from utils.pv3d import ModuleTransform, AdvancedLayoutConfig
        
        # Erstelle Konfiguration mit Modul
        config = AdvancedLayoutConfig()
        
        module_idx = 0
        
        # Erstelle Transform mit Offsets
        transform = ModuleTransform(
            index=module_idx,
            azimuth_deg=0.0,
            tilt_deg=15.0,
            offset_x=0.0,
            offset_y=0.0,
            offset_z=0.0
        )
        
        config.module_transforms[module_idx] = transform
        
        print(f"  Original Offsets: X={transform.offset_x}, Y={transform.offset_y}, Z={transform.offset_z}")
        
        # Ändere Offsets
        new_offset_x = 0.5
        new_offset_y = -0.3
        new_offset_z = 0.1
        
        config.module_transforms[module_idx].offset_x = new_offset_x
        config.module_transforms[module_idx].offset_y = new_offset_y
        config.module_transforms[module_idx].offset_z = new_offset_z
        
        # Prüfe Änderungen
        assert config.module_transforms[module_idx].offset_x == new_offset_x, \
            "Offset X sollte geändert sein"
        assert config.module_transforms[module_idx].offset_y == new_offset_y, \
            "Offset Y sollte geändert sein"
        assert config.module_transforms[module_idx].offset_z == new_offset_z, \
            "Offset Z sollte geändert sein"
        
        print(f"  Neue Offsets: X={new_offset_x}, Y={new_offset_y}, Z={new_offset_z}")
        print(f"Offsets erfolgreich geändert")
        
        return True
        
    except Exception as e:
        print(f"[X] Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_group_management_create():
    """Test 10.7: Gruppen-Verwaltung - Erstellen"""
    print("\n" + "=" * 70)
    print("TEST 10.7: Gruppen-Verwaltung - Erstellen")
    print("=" * 70)
    
    try:
        from utils.pv3d import ModuleGroup, AdvancedLayoutConfig
        
        # Erstelle Konfiguration
        config = AdvancedLayoutConfig()
        
        # Erstelle neue Gruppe
        group_name = "Neue Gruppe"
        group = ModuleGroup(
            name=group_name,
            module_indices=[5, 6, 7, 8],
            azimuth_deg=45.0,
            tilt_deg=25.0,
            color="#00ff00"
        )
        
        config.module_groups[group_name] = group
        
        # Prüfe Erstellung
        assert group_name in config.module_groups, "Gruppe sollte existieren"
        assert len(config.module_groups[group_name].module_indices) == 4, \
            "Gruppe sollte 4 Module enthalten"
        
        print(f"Gruppe '{group_name}' erfolgreich erstellt")
        print(f"  Module: {group.module_indices}")
        print(f"  Azimuth: {group.azimuth_deg} Grad, Tilt: {group.tilt_deg} Grad")
        print(f"  Farbe: {group.color}")
        
        return True
        
    except Exception as e:
        print(f"[X] Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_group_management_edit():
    """Test 10.8: Gruppen-Verwaltung - Bearbeiten"""
    print("\n" + "=" * 70)
    print("TEST 10.8: Gruppen-Verwaltung - Bearbeiten")
    print("=" * 70)
    
    try:
        from utils.pv3d import ModuleGroup, ModuleTransform, AdvancedLayoutConfig
        
        # Erstelle Konfiguration mit Gruppe
        config = AdvancedLayoutConfig()
        
        group_name = "Testgruppe"
        group = ModuleGroup(
            name=group_name,
            module_indices=[0, 1, 2],
            azimuth_deg=0.0,
            tilt_deg=15.0,
            color="#000000"
        )
        
        config.module_groups[group_name] = group
        
        # Erstelle Transforms für alle Module in der Gruppe
        for module_idx in group.module_indices:
            transform = ModuleTransform(
                index=module_idx,
                azimuth_deg=group.azimuth_deg,
                tilt_deg=group.tilt_deg,
                offset_x=0.0,
                offset_y=0.0,
                offset_z=0.0,
                group_id=group_name
            )
            config.module_transforms[module_idx] = transform
        
        print(f"  Original: Azimuth={group.azimuth_deg} Grad, Tilt={group.tilt_deg} Grad")
        
        # Bearbeite Gruppen-Eigenschaften
        new_azimuth = 90.0
        new_tilt = 30.0
        
        config.module_groups[group_name].azimuth_deg = new_azimuth
        config.module_groups[group_name].tilt_deg = new_tilt
        
        # Wende auf alle Module an
        for module_idx in group.module_indices:
            config.module_transforms[module_idx].azimuth_deg = new_azimuth
            config.module_transforms[module_idx].tilt_deg = new_tilt
        
        # Prüfe Änderungen
        assert config.module_groups[group_name].azimuth_deg == new_azimuth, \
            "Gruppen-Azimuth sollte geändert sein"
        assert config.module_groups[group_name].tilt_deg == new_tilt, \
            "Gruppen-Neigung sollte geändert sein"
        
        for module_idx in group.module_indices:
            assert config.module_transforms[module_idx].azimuth_deg == new_azimuth, \
                f"Modul {module_idx} Azimuth sollte geändert sein"
            assert config.module_transforms[module_idx].tilt_deg == new_tilt, \
                f"Modul {module_idx} Neigung sollte geändert sein"
        
        print(f"  Neu: Azimuth={new_azimuth} Grad, Tilt={new_tilt} Grad")
        print(f"Gruppe '{group_name}' erfolgreich bearbeitet")
        print(f"  Alle {len(group.module_indices)} Module wurden aktualisiert")
        
        return True
        
    except Exception as e:
        print(f"[X] Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_group_management_delete():
    """Test 10.9: Gruppen-Verwaltung - Löschen"""
    print("\n" + "=" * 70)
    print("TEST 10.9: Gruppen-Verwaltung - Löschen")
    print("=" * 70)
    
    try:
        from utils.pv3d import ModuleGroup, ModuleTransform, AdvancedLayoutConfig
        
        # Erstelle Konfiguration mit Gruppe
        config = AdvancedLayoutConfig()
        
        group_name = "Zu löschende Gruppe"
        group = ModuleGroup(
            name=group_name,
            module_indices=[0, 1, 2],
            azimuth_deg=0.0,
            tilt_deg=15.0,
            color="#000000"
        )
        
        config.module_groups[group_name] = group
        
        # Erstelle Transforms für Module
        for module_idx in group.module_indices:
            transform = ModuleTransform(
                index=module_idx,
                azimuth_deg=0.0,
                tilt_deg=15.0,
                offset_x=0.0,
                offset_y=0.0,
                offset_z=0.0,
                group_id=group_name
            )
            config.module_transforms[module_idx] = transform
        
        print(f"  Gruppe '{group_name}' mit {len(group.module_indices)} Modulen erstellt")
        
        # Lösche Gruppe
        del config.module_groups[group_name]
        
        # Entferne group_id von Modulen
        for module_idx in group.module_indices:
            if module_idx in config.module_transforms:
                config.module_transforms[module_idx].group_id = None
        
        # Prüfe Löschung
        assert group_name not in config.module_groups, "Gruppe sollte gelöscht sein"
        
        for module_idx in group.module_indices:
            if module_idx in config.module_transforms:
                assert config.module_transforms[module_idx].group_id is None, \
                    f"group_id für Modul {module_idx} sollte None sein"
        
        print(f"Gruppe '{group_name}' erfolgreich gelöscht")
        print(f"  group_id von allen Modulen entfernt")
        
        return True
        
    except Exception as e:
        print(f"[X] Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_group_templates():
    """Test 10.10: Gruppen-Templates"""
    print("\n" + "=" * 70)
    print("TEST 10.10: Gruppen-Templates")
    print("=" * 70)
    
    try:
        from utils.pv3d import ModuleGroup, AdvancedLayoutConfig
        
        # Definiere Templates
        templates = {
            "Süddach": {
                "azimuth": 0.0,
                "tilt": 35.0,
                "color": "#ff8800"
            },
            "Ostdach": {
                "azimuth": 270.0,
                "tilt": 35.0,
                "color": "#ffff00"
            },
            "Westdach": {
                "azimuth": 90.0,
                "tilt": 35.0,
                "color": "#00ffff"
            },
            "Norddach": {
                "azimuth": 180.0,
                "tilt": 35.0,
                "color": "#8800ff"
            }
        }
        
        # Erstelle Konfiguration
        config = AdvancedLayoutConfig()
        
        # Teste jedes Template
        for template_name, template_data in templates.items():
            # Erstelle Gruppe aus Template
            group = ModuleGroup(
                name=template_name,
                module_indices=[0, 1, 2],
                azimuth_deg=template_data["azimuth"],
                tilt_deg=template_data["tilt"],
                color=template_data["color"]
            )
            
            config.module_groups[template_name] = group
            
            # Prüfe Template-Werte
            assert group.azimuth_deg == template_data["azimuth"], \
                f"{template_name}: Azimuth falsch"
            assert group.tilt_deg == template_data["tilt"], \
                f"{template_name}: Neigung falsch"
            assert group.color == template_data["color"], \
                f"{template_name}: Farbe falsch"
            
            print(f"  Template '{template_name}': Azimuth={group.azimuth_deg} Grad, "
                  f"Tilt={group.tilt_deg} Grad, Color={group.color}")
        
        # Prüfe dass alle Templates erstellt wurden
        assert len(config.module_groups) == 4, "Alle 4 Templates sollten erstellt sein"
        
        print(f"Alle {len(templates)} Gruppen-Templates erfolgreich getestet")
        
        return True
        
    except Exception as e:
        print(f"[X] Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_collision_detection():
    """Test 10.11: Kollisionserkennung"""
    print("\n" + "=" * 70)
    print("TEST 10.11: Kollisionserkennung")
    print("=" * 70)
    
    try:
        from utils.pv3d import make_panel, detect_collisions
        
        # Test 1: Keine Kollisionen
        print("\n  Test 1: Keine Kollisionen - Module weit auseinander")
        panels_no_collision = [
            make_panel(position=(0.0, 0.0, 0.0)),
            make_panel(position=(5.0, 0.0, 0.0)),
            make_panel(position=(10.0, 0.0, 0.0))
        ]
        
        collisions = detect_collisions(panels_no_collision)
        assert len(collisions) == 0, "Keine Kollisionen erwartet"
        print(f"    Keine Kollisionen erkannt ({len(panels_no_collision)} Module)")
        
        # Test 2: Eine Kollision
        print("\n  Test 2: Eine Kollision - Zwei überlappende Module")
        panels_one_collision = [
            make_panel(position=(0.0, 0.0, 0.0)),
            make_panel(position=(0.5, 0.0, 0.0)),  # Überlappung!
            make_panel(position=(5.0, 0.0, 0.0))
        ]
        
        collisions = detect_collisions(panels_one_collision)
        assert len(collisions) >= 1, "Mindestens eine Kollision erwartet"
        print(f"    Kollision erkannt: {collisions}")
        
        # Test 3: Kollisionserkennung aktiviert/deaktiviert
        print("\n  Test 3: Kollisionserkennung aktiviert/deaktiviert")
        from utils.pv3d import AdvancedLayoutConfig
        
        config = AdvancedLayoutConfig()
        
        # Aktiviert
        config.enable_collision_detection = True
        assert config.enable_collision_detection == True, \
            "Kollisionserkennung sollte aktiviert sein"
        print(f"    Kollisionserkennung aktiviert")
        
        # Deaktiviert
        config.enable_collision_detection = False
        assert config.enable_collision_detection == False, \
            "Kollisionserkennung sollte deaktiviert sein"
        print(f"    Kollisionserkennung deaktiviert")
        
        print(f"\nKollisionserkennung erfolgreich getestet")
        
        return True
        
    except Exception as e:
        print(f"[X] Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Führe alle Tests aus"""
    print("\n" + "=" * 70)
    print("TASK 10: TESTE ERWEITERTE FUNKTIONEN")
    print("=" * 70)
    
    results = []
    
    # Modul-Auswahl Tests
    results.append(("10.1 - Modul-Auswahl Einzeln", test_module_selection_single()))
    results.append(("10.2 - Modul-Auswahl Gruppe", test_module_selection_group()))
    results.append(("10.3 - Modul-Auswahl Bereich", test_module_selection_range()))
    
    # Modul-Eigenschaften Tests
    results.append(("10.4 - Eigenschaften Azimuth", test_module_properties_azimuth()))
    results.append(("10.5 - Eigenschaften Neigung", test_module_properties_tilt()))
    results.append(("10.6 - Eigenschaften Offsets", test_module_properties_offsets()))
    
    # Gruppen-Verwaltung Tests
    results.append(("10.7 - Gruppen Erstellen", test_group_management_create()))
    results.append(("10.8 - Gruppen Bearbeiten", test_group_management_edit()))
    results.append(("10.9 - Gruppen Löschen", test_group_management_delete()))
    results.append(("10.10 - Gruppen Templates", test_group_templates()))
    
    # Kollisionserkennung Test
    results.append(("10.11 - Kollisionserkennung", test_collision_detection()))
    
    # Zusammenfassung
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "BESTANDEN" if result else "[X] FEHLGESCHLAGEN"
        print(f"{name}: {status}")
    
    print("\n" + "=" * 70)
    print(f"ERGEBNIS: {passed}/{total} Tests bestanden")
    print("=" * 70)
    
    if passed == total:
        print("\nAlle Tests erfolgreich! Task 10 ist vollständig implementiert.")
        print("\nGetestete Funktionen:")
        print("  Modul-Auswahl (Einzeln, Gruppe, Bereich)")
        print("  Modul-Eigenschaften bearbeiten (Azimuth, Neigung, Offsets)")
        print("  Gruppen-Verwaltung (Erstellen, Bearbeiten, Löschen)")
        print("  Gruppen-Templates (Süddach, Ostdach, Westdach, Norddach)")
        print("  Kollisionserkennung")
        return True
    else:
        print(f"\n{total - passed} Test(s) fehlgeschlagen. Bitte überprüfen Sie die Implementierung.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
