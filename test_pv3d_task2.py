"""
Test für Task 2: Core 3D Engine - Datenstrukturen und Hilfsfunktionen
"""

import sys
import math

# Import des Moduls
from utils.pv3d import (
    PV_W, PV_H, PV_T,
    ROOF_COLORS,
    _deg_to_rad,
    BuildingDims,
    LayoutConfig,
    _safe_get_orientation,
    _safe_get_roof_inclination_deg,
    _safe_get_roof_covering,
    _roof_color_from_covering
)


def test_constants():
    """Test PV-Modul Konstanten"""
    print("Testing constants...")
    assert PV_W == 1.05, f"PV_W should be 1.05, got {PV_W}"
    assert PV_H == 1.76, f"PV_H should be 1.76, got {PV_H}"
    assert PV_T == 0.04, f"PV_T should be 0.04, got {PV_T}"
    print("✓ Constants OK")


def test_roof_colors():
    """Test ROOF_COLORS Dictionary"""
    print("\nTesting ROOF_COLORS...")
    assert "Ziegel" in ROOF_COLORS
    assert "Beton" in ROOF_COLORS
    assert "Schiefer" in ROOF_COLORS
    assert "Eternit" in ROOF_COLORS
    assert "Trapezblech" in ROOF_COLORS
    assert "Bitumen" in ROOF_COLORS
    assert "default" in ROOF_COLORS
    assert ROOF_COLORS["Ziegel"] == "#c96a2d"
    assert ROOF_COLORS["default"] == "#b0b5ba"
    print("✓ ROOF_COLORS OK")


def test_deg_to_rad():
    """Test _deg_to_rad Funktion"""
    print("\nTesting _deg_to_rad...")
    assert abs(_deg_to_rad(0) - 0) < 0.001
    assert abs(_deg_to_rad(90) - math.pi/2) < 0.001
    assert abs(_deg_to_rad(180) - math.pi) < 0.001
    assert abs(_deg_to_rad(360) - 2*math.pi) < 0.001
    print("✓ _deg_to_rad OK")


def test_building_dims():
    """Test BuildingDims Datenklasse"""
    print("\nTesting BuildingDims...")
    dims = BuildingDims()
    assert dims.length_m == 10.0
    assert dims.width_m == 6.0
    assert dims.wall_height_m == 6.0

    dims2 = BuildingDims(length_m=15.0, width_m=8.0, wall_height_m=7.0)
    assert dims2.length_m == 15.0
    assert dims2.width_m == 8.0
    assert dims2.wall_height_m == 7.0
    print("✓ BuildingDims OK")


def test_layout_config():
    """Test LayoutConfig Datenklasse"""
    print("\nTesting LayoutConfig...")
    config = LayoutConfig()
    assert config.mode == "auto"
    assert config.use_garage is False
    assert config.use_facade is False
    assert config.removed_indices == []
    assert config.garage_dims == (6.0, 3.0, 3.0)
    print("✓ LayoutConfig OK")


def test_layout_config_json():
    """Test LayoutConfig JSON Serialisierung"""
    print("\nTesting LayoutConfig JSON...")
    config = LayoutConfig(
        mode="manual",
        use_garage=True,
        use_facade=True,
        removed_indices=[0, 1, 2],
        garage_dims=(7.0, 4.0, 3.5)
    )

    # Serialisierung
    json_str = config.to_json()
    assert isinstance(json_str, str)
    assert "manual" in json_str
    assert "true" in json_str.lower()

    # Deserialisierung
    config2 = LayoutConfig.from_json(json_str)
    assert config2.mode == "manual"
    assert config2.use_garage is True
    assert config2.use_facade is True
    assert config2.removed_indices == [0, 1, 2]
    assert config2.garage_dims == (7.0, 4.0, 3.5)
    print("✓ LayoutConfig JSON OK")


def test_safe_get_orientation():
    """Test _safe_get_orientation Funktion"""
    print("\nTesting _safe_get_orientation...")

    # Test mit project_details
    data1 = {"project_details": {"roof_orientation": "Ost"}}
    assert _safe_get_orientation(data1) == "Ost"

    # Test mit direktem Key
    data2 = {"roof_orientation": "West"}
    assert _safe_get_orientation(data2) == "West"

    # Test mit orientation Key
    data3 = {"orientation": "Nord"}
    assert _safe_get_orientation(data3) == "Nord"

    # Test Fallback
    assert _safe_get_orientation({}) == "Süd"
    assert _safe_get_orientation(None) == "Süd"
    print("✓ _safe_get_orientation OK")


def test_safe_get_roof_inclination_deg():
    """Test _safe_get_roof_inclination_deg Funktion"""
    print("\nTesting _safe_get_roof_inclination_deg...")

    # Test mit project_details
    data1 = {"project_details": {"roof_inclination_deg": 45.0}}
    assert _safe_get_roof_inclination_deg(data1) == 45.0

    # Test mit direktem Key
    data2 = {"roof_inclination_deg": 30.0}
    assert _safe_get_roof_inclination_deg(data2) == 30.0

    # Test String-Konvertierung
    data3 = {"roof_inclination_deg": "25"}
    assert _safe_get_roof_inclination_deg(data3) == 25.0

    # Test Bereichsvalidierung
    data4 = {"roof_inclination_deg": 100.0}
    assert _safe_get_roof_inclination_deg(data4) == 90.0

    data5 = {"roof_inclination_deg": -10.0}
    assert _safe_get_roof_inclination_deg(data5) == 0.0

    # Test Fallback
    assert _safe_get_roof_inclination_deg({}) == 35.0
    assert _safe_get_roof_inclination_deg(None) == 35.0
    print("✓ _safe_get_roof_inclination_deg OK")


def test_safe_get_roof_covering():
    """Test _safe_get_roof_covering Funktion"""
    print("\nTesting _safe_get_roof_covering...")

    # Test mit project_details
    data1 = {"project_details": {"roof_covering_type": "Ziegel"}}
    assert _safe_get_roof_covering(data1) == "Ziegel"

    # Test mit direktem Key
    data2 = {"roof_covering_type": "Beton"}
    assert _safe_get_roof_covering(data2) == "Beton"

    # Test Fallback
    assert _safe_get_roof_covering({}) == "default"
    assert _safe_get_roof_covering(None) == "default"
    print("✓ _safe_get_roof_covering OK")


def test_roof_color_from_covering():
    """Test _roof_color_from_covering Funktion"""
    print("\nTesting _roof_color_from_covering...")

    # Test exakte Übereinstimmung
    assert _roof_color_from_covering("Ziegel") == "#c96a2d"
    assert _roof_color_from_covering("Beton") == "#9ea3a8"

    # Test case-insensitive
    assert _roof_color_from_covering("ziegel") == "#c96a2d"
    assert _roof_color_from_covering("BETON") == "#9ea3a8"

    # Test Fallback
    assert _roof_color_from_covering("Unbekannt") == "#b0b5ba"
    assert _roof_color_from_covering("") == "#b0b5ba"
    print("✓ _roof_color_from_covering OK")


def main():
    """Führe alle Tests aus"""
    print("=" * 60)
    print("Task 2 Tests: Core 3D Engine - Datenstrukturen")
    print("=" * 60)

    try:
        test_constants()
        test_roof_colors()
        test_deg_to_rad()
        test_building_dims()
        test_layout_config()
        test_layout_config_json()
        test_safe_get_orientation()
        test_safe_get_roof_inclination_deg()
        test_safe_get_roof_covering()
        test_roof_color_from_covering()

        print("\n" + "=" * 60)
        print("✓ ALLE TESTS ERFOLGREICH!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ TEST FEHLGESCHLAGEN: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ FEHLER: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
