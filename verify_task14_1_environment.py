"""
Verification Script für Phase 3 - Task 14.1: 3D-Objekt-Bibliothek

Testet alle Funktionen des Umgebungsobjekt-Systems.
"""

import sys
import numpy as np
import plotly.graph_objects as go

# Import der zu testenden Module
from utils.pv3d_environment import (
    EnvironmentObject,
    Tree,
    NeighborBuilding,
    Chimney,
    Antenna,
    ShadowData,
    add_environment_objects_to_scene,
    calculate_environment_shading,
    _point_in_polygon
)


def test_environment_object_base():
    """Test 1: EnvironmentObject Basis-Klasse."""
    print("Test 1: EnvironmentObject Basis-Klasse...")
    
    obj = EnvironmentObject(x=5.0, y=3.0, z=0.0, width=2.0, length=3.0, height=4.0, name="TestObj")
    
    assert obj.x == 5.0, "X-Position falsch"
    assert obj.y == 3.0, "Y-Position falsch"
    assert obj.z == 0.0, "Z-Position falsch"
    assert obj.width == 2.0, "Breite falsch"
    assert obj.length == 3.0, "Länge falsch"
    assert obj.height == 4.0, "Höhe falsch"
    assert obj.name == "TestObj", "Name falsch"
    
    print("✓ EnvironmentObject Basis-Klasse funktioniert")
    return True


def test_shadow_calculation():
    """Test 2: Schatten-Berechnung."""
    print("\nTest 2: Schatten-Berechnung...")
    
    obj = EnvironmentObject(x=0, y=0, z=0, width=2, length=2, height=5)
    shadow = obj.calculate_shadow(sun_azimuth=180, sun_elevation=45)
    
    assert isinstance(shadow, ShadowData), "Shadow ist kein ShadowData"
    assert shadow.corners.shape == (4, 2), "Schatten-Polygon hat falsche Form"
    assert 0.0 <= shadow.intensity <= 1.0, "Intensität außerhalb Bereich"
    assert shadow.source_object == "Object", "Source-Object falsch"
    
    print("✓ Schatten-Berechnung funktioniert")
    return True


def test_tree_creation():
    """Test 3: Baum-Erstellung."""
    print("\nTest 3: Baum-Erstellung...")
    
    # Laubbaum
    tree = Tree(x=5, y=3, height=8, tree_type="Laubbaum")
    assert tree.x == 5, "X-Position falsch"
    assert tree.y == 3, "Y-Position falsch"
    assert tree.height == 8, "Höhe falsch"
    assert tree.tree_type == "Laubbaum", "Baumart falsch"
    assert tree.trunk_height == 8 * 0.4, "Stammhöhe falsch"
    assert tree.crown_radius == 8 * 0.3, "Kronenradius falsch"
    
    # Nadelbaum
    tree_nadel = Tree(x=0, y=0, height=10, tree_type="Nadelbaum")
    assert tree_nadel.crown_radius == 10 * 0.2, "Nadelbaum-Kronenradius falsch"
    
    # Palme
    tree_palme = Tree(x=0, y=0, height=10, tree_type="Palme")
    assert tree_palme.trunk_height == 10 * 0.7, "Palmen-Stammhöhe falsch"
    
    print("✓ Baum-Erstellung funktioniert")
    return True


def test_tree_mesh():
    """Test 4: Baum-Mesh-Generierung."""
    print("\nTest 4: Baum-Mesh-Generierung...")
    
    tree = Tree(x=0, y=0, height=5)
    meshes = tree.to_mesh()
    
    assert isinstance(meshes, list), "Meshes ist keine Liste"
    assert len(meshes) == 2, "Baum sollte 2 Meshes haben (Stamm + Krone)"
    assert all(isinstance(m, go.Mesh3d) for m in meshes), "Nicht alle Meshes sind Mesh3d"
    
    # Prüfe Stamm
    trunk = meshes[0]
    assert trunk.color == '#8B4513', "Stamm-Farbe falsch"
    
    # Prüfe Krone
    crown = meshes[1]
    assert crown.color in ['#228B22', '#32CD32'], "Kronen-Farbe falsch"
    
    print("✓ Baum-Mesh-Generierung funktioniert")
    return True


def test_neighbor_building():
    """Test 5: Nachbargebäude-Erstellung."""
    print("\nTest 5: Nachbargebäude-Erstellung...")
    
    building = NeighborBuilding(
        x=10, y=5,
        width=8, length=10, height=12,
        building_type="Wohnhaus"
    )
    
    assert building.x == 10, "X-Position falsch"
    assert building.y == 5, "Y-Position falsch"
    assert building.width == 8, "Breite falsch"
    assert building.length == 10, "Länge falsch"
    assert building.height == 12, "Höhe falsch"
    assert building.building_type == "Wohnhaus", "Gebäudetyp falsch"
    assert "Wohnhaus" in building.name, "Name enthält nicht Gebäudetyp"
    
    print("✓ Nachbargebäude-Erstellung funktioniert")
    return True


def test_neighbor_building_mesh():
    """Test 6: Nachbargebäude-Mesh."""
    print("\nTest 6: Nachbargebäude-Mesh...")
    
    building = NeighborBuilding(
        x=0, y=0,
        width=10, length=8, height=15
    )
    
    mesh = building.to_mesh()
    
    assert isinstance(mesh, go.Mesh3d), "Mesh ist kein Mesh3d"
    assert mesh.name == building.name, "Mesh-Name falsch"
    
    print("✓ Nachbargebäude-Mesh funktioniert")
    return True


def test_chimney():
    """Test 7: Schornstein-Erstellung."""
    print("\nTest 7: Schornstein-Erstellung...")
    
    chimney = Chimney(x=2, y=3, height=4)
    
    assert chimney.x == 2, "X-Position falsch"
    assert chimney.y == 3, "Y-Position falsch"
    assert chimney.height == 4, "Höhe falsch"
    assert chimney.width == 0.5, "Breite falsch"
    assert chimney.name == "Schornstein", "Name falsch"
    
    mesh = chimney.to_mesh()
    assert isinstance(mesh, go.Mesh3d), "Mesh ist kein Mesh3d"
    assert mesh.color == '#8B0000', "Farbe falsch (sollte dunkelrot sein)"
    
    print("✓ Schornstein-Erstellung funktioniert")
    return True


def test_antenna():
    """Test 8: Antennen-Erstellung."""
    print("\nTest 8: Antennen-Erstellung...")
    
    antenna = Antenna(x=1, y=2, height=2.5)
    
    assert antenna.x == 1, "X-Position falsch"
    assert antenna.y == 2, "Y-Position falsch"
    assert antenna.height == 2.5, "Höhe falsch"
    assert antenna.width == 0.2, "Breite falsch"
    assert antenna.name == "Antenne", "Name falsch"
    
    mesh = antenna.to_mesh()
    assert isinstance(mesh, go.Mesh3d), "Mesh ist kein Mesh3d"
    assert mesh.color == '#C0C0C0', "Farbe falsch (sollte silber sein)"
    
    print("✓ Antennen-Erstellung funktioniert")
    return True


def test_add_objects_to_scene():
    """Test 9: Objekte zur Szene hinzufügen."""
    print("\nTest 9: Objekte zur Szene hinzufügen...")
    
    fig = go.Figure()
    
    tree = Tree(x=5, y=5, height=8)
    building = NeighborBuilding(x=-10, y=0, width=8, length=10, height=12)
    chimney = Chimney(x=0, y=0, height=3)
    antenna = Antenna(x=2, y=2, height=2)
    
    fig = add_environment_objects_to_scene(fig, [tree, building, chimney, antenna])
    
    # Tree: 2 Meshes, Building: 1, Chimney: 1, Antenna: 1 = 5 total
    assert len(fig.data) == 5, f"Falsche Anzahl Meshes: {len(fig.data)} (erwartet 5)"
    
    print("✓ Objekte zur Szene hinzufügen funktioniert")
    return True


def test_shading_calculation():
    """Test 10: Verschattungs-Berechnung."""
    print("\nTest 10: Verschattungs-Berechnung...")
    
    tree = Tree(x=2, y=2, height=8)
    building = NeighborBuilding(x=-5, y=-5, width=8, length=8, height=12)
    
    module_positions = [(0, 0, 0.3), (5, 5, 0.3), (10, 10, 0.3)]
    
    shading = calculate_environment_shading(
        objects=[tree, building],
        module_positions=module_positions,
        sun_azimuth=180,
        sun_elevation=45
    )
    
    assert len(shading) == 3, "Falsche Anzahl Verschattungswerte"
    assert all(0.0 <= s <= 1.0 for s in shading.values()), "Verschattungswerte außerhalb Bereich"
    assert all(isinstance(k, int) for k in shading.keys()), "Schlüssel sind keine Integers"
    
    print("✓ Verschattungs-Berechnung funktioniert")
    return True


def test_point_in_polygon():
    """Test 11: Point-in-Polygon Algorithmus."""
    print("\nTest 11: Point-in-Polygon Algorithmus...")
    
    # Quadrat
    polygon = np.array([
        [0, 0],
        [10, 0],
        [10, 10],
        [0, 10]
    ])
    
    assert _point_in_polygon((5, 5), polygon) is True, "Punkt sollte im Polygon sein"
    assert _point_in_polygon((15, 15), polygon) is False, "Punkt sollte außerhalb sein"
    
    # Dreieck
    triangle = np.array([
        [0, 0],
        [10, 0],
        [5, 10]
    ])
    
    assert _point_in_polygon((5, 3), triangle) is True, "Punkt sollte im Dreieck sein"
    assert _point_in_polygon((0, 10), triangle) is False, "Punkt sollte außerhalb sein"
    
    print("✓ Point-in-Polygon Algorithmus funktioniert")
    return True


def test_cylinder_creation():
    """Test 12: Zylinder-Erstellung."""
    print("\nTest 12: Zylinder-Erstellung...")
    
    obj = EnvironmentObject(x=0, y=0, z=0, width=1, length=1, height=1)
    
    cylinder = obj._create_cylinder(
        x=0, y=0, z=0,
        radius=1.0,
        height=5.0,
        color='#FF0000',
        segments=16
    )
    
    assert isinstance(cylinder, go.Mesh3d), "Zylinder ist kein Mesh3d"
    assert cylinder.color == '#FF0000', "Farbe falsch"
    assert len(cylinder.x) > 0, "Keine X-Koordinaten"
    assert len(cylinder.y) > 0, "Keine Y-Koordinaten"
    assert len(cylinder.z) > 0, "Keine Z-Koordinaten"
    
    print("✓ Zylinder-Erstellung funktioniert")
    return True


def test_cone_creation():
    """Test 13: Kegel-Erstellung."""
    print("\nTest 13: Kegel-Erstellung...")
    
    obj = EnvironmentObject(x=0, y=0, z=0, width=1, length=1, height=1)
    
    cone = obj._create_cone(
        x=0, y=0, z=0,
        radius=2.0,
        height=5.0,
        color='#00FF00',
        segments=16
    )
    
    assert isinstance(cone, go.Mesh3d), "Kegel ist kein Mesh3d"
    assert cone.color == '#00FF00', "Farbe falsch"
    assert len(cone.x) > 0, "Keine X-Koordinaten"
    assert len(cone.y) > 0, "Keine Y-Koordinaten"
    assert len(cone.z) > 0, "Keine Z-Koordinaten"
    
    print("✓ Kegel-Erstellung funktioniert")
    return True


def test_all_object_types():
    """Test 14: Alle Objekttypen zusammen."""
    print("\nTest 14: Alle Objekttypen zusammen...")
    
    objects = [
        Tree(x=5, y=5, height=8, tree_type="Laubbaum"),
        Tree(x=-5, y=5, height=10, tree_type="Nadelbaum"),
        Tree(x=5, y=-5, height=12, tree_type="Palme"),
        NeighborBuilding(x=-10, y=0, width=8, length=10, height=12, building_type="Wohnhaus"),
        NeighborBuilding(x=10, y=0, width=10, length=10, height=25, building_type="Hochhaus"),
        Chimney(x=0, y=0, height=3),
        Antenna(x=2, y=2, height=2)
    ]
    
    fig = go.Figure()
    fig = add_environment_objects_to_scene(fig, objects)
    
    # 3 Bäume (je 2 Meshes) + 2 Gebäude (je 1) + Schornstein (1) + Antenne (1) = 10
    expected_meshes = 3*2 + 2 + 1 + 1
    assert len(fig.data) == expected_meshes, f"Falsche Anzahl Meshes: {len(fig.data)} (erwartet {expected_meshes})"
    
    print("✓ Alle Objekttypen zusammen funktionieren")
    return True


def test_shadow_intensity_variation():
    """Test 15: Schatten-Intensität variiert mit Sonnenstand."""
    print("\nTest 15: Schatten-Intensität variiert mit Sonnenstand...")
    
    obj = EnvironmentObject(x=0, y=0, z=0, width=2, length=2, height=5)
    
    shadow_low = obj.calculate_shadow(sun_azimuth=180, sun_elevation=15)
    shadow_mid = obj.calculate_shadow(sun_azimuth=180, sun_elevation=45)
    shadow_high = obj.calculate_shadow(sun_azimuth=180, sun_elevation=75)
    
    # Niedrigere Sonne = höhere Intensität
    assert shadow_low.intensity > shadow_mid.intensity, "Niedrige Sonne sollte stärkeren Schatten haben"
    assert shadow_mid.intensity > shadow_high.intensity, "Mittlere Sonne sollte stärkeren Schatten als hohe haben"
    
    print("✓ Schatten-Intensität variiert korrekt")
    return True


def run_all_tests():
    """Führt alle Tests aus."""
    print("=" * 70)
    print("VERIFICATION: Phase 3 - Task 14.1: 3D-Objekt-Bibliothek")
    print("=" * 70)
    
    tests = [
        test_environment_object_base,
        test_shadow_calculation,
        test_tree_creation,
        test_tree_mesh,
        test_neighbor_building,
        test_neighbor_building_mesh,
        test_chimney,
        test_antenna,
        test_add_objects_to_scene,
        test_shading_calculation,
        test_point_in_polygon,
        test_cylinder_creation,
        test_cone_creation,
        test_all_object_types,
        test_shadow_intensity_variation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"✗ Test fehlgeschlagen: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test-Fehler: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"ERGEBNIS: {passed}/{len(tests)} Tests bestanden")
    if failed > 0:
        print(f"FEHLER: {failed} Tests fehlgeschlagen")
    else:
        print("✓ ALLE TESTS BESTANDEN!")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
