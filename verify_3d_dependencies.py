"""
Verification script for 3D PV Visualization dependencies.
Tests that all required packages can be imported successfully.
"""

import sys
from typing import List, Tuple


def test_imports() -> List[Tuple[str, bool, str]]:
    """Test all required imports for 3D visualization."""
    results = []
    
    # Test pyvista
    try:
        import pyvista as pv
        version = pv.__version__
        results.append(("pyvista", True, f"v{version}"))
    except ImportError as e:
        results.append(("pyvista", False, str(e)))
    
    # Test vtk
    try:
        import vtk
        version = vtk.vtkVersion.GetVTKVersion()
        results.append(("vtk", True, f"v{version}"))
    except ImportError as e:
        results.append(("vtk", False, str(e)))
    
    # Test stpyvista
    try:
        import stpyvista
        results.append(("stpyvista", True, "OK"))
    except ImportError as e:
        results.append(("stpyvista", False, str(e)))
    
    # Test numpy (should already be installed)
    try:
        import numpy as np
        version = np.__version__
        results.append(("numpy", True, f"v{version}"))
    except ImportError as e:
        results.append(("numpy", False, str(e)))
    
    # Test trimesh
    try:
        import trimesh
        version = trimesh.__version__
        results.append(("trimesh", True, f"v{version}"))
    except ImportError as e:
        results.append(("trimesh", False, str(e)))
    
    # Test reportlab (should already be installed)
    try:
        import reportlab
        version = reportlab.Version
        results.append(("reportlab", True, f"v{version}"))
    except ImportError as e:
        results.append(("reportlab", False, str(e)))
    
    # Test pikepdf
    try:
        import pikepdf
        version = pikepdf.__version__
        results.append(("pikepdf", True, f"v{version}"))
    except ImportError as e:
        results.append(("pikepdf", False, str(e)))
    
    # Test Pillow (should already be installed)
    try:
        from PIL import Image
        import PIL
        version = PIL.__version__
        results.append(("Pillow", True, f"v{version}"))
    except ImportError as e:
        results.append(("Pillow", False, str(e)))
    
    return results


def main():
    """Run import tests and display results."""
    print("=" * 60)
    print("3D PV Visualization - Dependency Verification")
    print("=" * 60)
    print()
    
    results = test_imports()
    
    all_passed = True
    for package, success, info in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status:8} | {package:15} | {info}")
        if not success:
            all_passed = False
    
    print()
    print("=" * 60)
    
    if all_passed:
        print("✓ All dependencies are installed and working correctly!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some dependencies are missing or failed to import.")
        print("  Run: pip install -r requirements.txt")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
