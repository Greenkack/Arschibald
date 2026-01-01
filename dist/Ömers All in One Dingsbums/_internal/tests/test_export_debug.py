"""
Debug-Skript für Export-Funktionen
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from pv3d import (
    BuildingDims,
    LayoutConfig,
    export_stl,
    export_gltf
)

# Test-Daten
project_data = {
    "project_details": {
        "roof_orientation": "Süd",
        "roof_inclination_deg": 35.0,
        "roof_covering_type": "Ziegel"
    }
}

dims = BuildingDims(
    length_m=10.0,
    width_m=6.0,
    wall_height_m=6.0
)

layout = LayoutConfig(mode="auto")

print("Test STL-Export...")
try:
    success = export_stl(
        project_data=project_data,
        dims=dims,
        roof_type="Flachdach",
        module_quantity=20,
        layout_config=layout,
        filepath="debug_test.stl"
    )
    print(f"STL Success: {success}")
except Exception as e:
    print(f"STL Error: {e}")
    import traceback
    traceback.print_exc()

print("\nTest glTF-Export...")
try:
    success = export_gltf(
        project_data=project_data,
        dims=dims,
        roof_type="Flachdach",
        module_quantity=20,
        layout_config=layout,
        filepath="debug_test.glb"
    )
    print(f"glTF Success: {success}")
except Exception as e:
    print(f"glTF Error: {e}")
    import traceback
    traceback.print_exc()
