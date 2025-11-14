"""
Debug-Script für Modul-Rendering Problem

Testet ob Module bei verschiedenen Dachtypen korrekt platziert und gerendert werden.
"""

import sys


def test_module_placement_for_roof_types():
    """Testet Modul-Platzierung für verschiedene Dachtypen"""
    from utils.pv3d_placement_handler import handle_auto_placement, calculate_z_position, calculate_tilt_angle
    
    print("\n" + "=" * 70)
    print("TEST: MODUL-PLATZIERUNG FÜR VERSCHIEDENE DACHTYPEN")
    print("=" * 70)
    
    roof_types = [
        ("Flachdach", 0.0),
        ("Satteldach", 35.0),
        ("Pultdach", 25.0),
        ("Walmdach", 40.0),
    ]
    
    # Mock Streamlit session state
    class MockSessionState:
        def __init__(self):
            self.data = {}
        
        def get(self, key, default=None):
            return self.data.get(key, default)
        
        def __setitem__(self, key, value):
            self.data[key] = value
        
        def __getitem__(self, key):
            return self.data[key]
        
        def __contains__(self, key):
            return key in self.data
    
    import streamlit as st
    st.session_state = MockSessionState()
    
    for roof_type, roof_pitch in roof_types:
        print(f"\n{'='*70}")
        print(f"Dachtyp: {roof_type} (Neigung: {roof_pitch}°)")
        print(f"{'='*70}")
        
        # Test 1: Z-Position berechnen
        z_pos = calculate_z_position(roof_type, roof_pitch)
        print(f"[OK] Z-Position: {z_pos:.3f}m")
        
        # Test 2: Tilt-Winkel berechnen
        tilt = calculate_tilt_angle(roof_type, roof_pitch)
        print(f"[OK] Tilt-Winkel: {tilt:.1f}°")
        
        # Test 3: Module platzieren
        result = handle_auto_placement(
            roof_length=10.0,
            roof_width=8.0,
            module_quantity=20,
            roof_type=roof_type,
            roof_pitch=roof_pitch
        )
        
        if result["success"]:
            print(f"[OK] Platzierung erfolgreich!")
            print(f"   - Platzierte Module: {result['count']}")
            print(f"   - Positionen: {len(result['positions'])}")
            if result['positions']:
                first_pos = result['positions'][0]
                print(f"   - Erste Position: ({first_pos[0]:.2f}, {first_pos[1]:.2f}, {first_pos[2]:.2f})")
        else:
            print(f"[ERROR] Platzierung fehlgeschlagen!")
            print(f"   - Fehler: {result['message']}")
        
        # Test 4: Session State prüfen
        placed_positions = st.session_state.get("placed_module_positions", [])
        placed_count = st.session_state.get("placed_module_count", 0)
        print(f"[OK] Session State:")
        print(f"   - placed_module_count: {placed_count}")
        print(f"   - placed_module_positions: {len(placed_positions)} Positionen")


def test_module_rendering_in_scene():
    """Testet ob Module in der 3D-Szene gerendert werden"""
    print("\n" + "=" * 70)
    print("TEST: MODUL-RENDERING IN 3D-SZENE")
    print("=" * 70)
    
    # Mock Streamlit session state mit Modulen
    class MockSessionState:
        def __init__(self):
            self.data = {
                "placed_module_positions": [
                    (0.0, 0.0, 0.05),  # Satteldach-Position
                    (1.1, 0.0, 0.05),
                    (2.2, 0.0, 0.05),
                ],
                "placed_module_count": 3
            }
        
        def get(self, key, default=None):
            return self.data.get(key, default)
        
        def __setitem__(self, key, value):
            self.data[key] = value
        
        def __getitem__(self, key):
            return self.data[key]
        
        def __contains__(self, key):
            return key in self.data
    
    import streamlit as st
    st.session_state = MockSessionState()
    
    print(f"\n[OK] Session State vorbereitet:")
    print(f"   - placed_module_count: {st.session_state['placed_module_count']}")
    print(f"   - placed_module_positions: {len(st.session_state['placed_module_positions'])} Positionen")
    
    # Prüfe ob Positionen vorhanden sind
    placed_positions = st.session_state.get("placed_module_positions", [])
    
    if placed_positions:
        print(f"\n[OK] Module in Session State gefunden!")
        print(f"   Diese sollten in build_plotly_scene() gerendert werden.")
        print(f"\n   Positionen:")
        for i, pos in enumerate(placed_positions):
            print(f"   - Modul {i+1}: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")
    else:
        print(f"\n[ERROR] KEINE Module in Session State!")
        print(f"   Das ist das Problem - Module werden nicht platziert.")


def test_create_pv_module_3d():
    """Testet ob create_pv_module_3d für alle Dachtypen funktioniert"""
    from utils.pv3d_plotly import create_pv_module_3d
    
    print("\n" + "=" * 70)
    print("TEST: CREATE_PV_MODULE_3D FÜR VERSCHIEDENE DACHTYPEN")
    print("=" * 70)
    
    roof_types = [
        ("Flachdach", 30.0),
        ("Satteldach", 35.0),
        ("Pultdach", 25.0),
    ]
    
    for roof_type, tilt_deg in roof_types:
        print(f"\n{roof_type} (Neigung: {tilt_deg}°):")
        
        try:
            module, vertices = create_pv_module_3d(
                x=0.0,
                y=0.0,
                z=5.0,
                azimuth_deg=0,
                tilt_deg=tilt_deg,
                color="#1a1a2e",
                selected=False,
                show_mounting=True,
                roof_type=roof_type
            )
            
            print(f"   [OK] Modul erstellt")
            print(f"   - Vertices: {len(vertices)}")
            print(f"   - Farbe: {module.color}")
            print(f"   - Name: {module.name}")
            
        except Exception as e:
            print(f"   [ERROR] Fehler: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    print("=" * 70)
    print("DEBUG: MODUL-RENDERING PROBLEM")
    print("=" * 70)
    print("\nDieses Script testet:")
    print("1. Modul-Platzierung für verschiedene Dachtypen")
    print("2. Session State nach Platzierung")
    print("3. Modul-Erstellung für verschiedene Dachtypen")
    
    try:
        test_module_placement_for_roof_types()
        test_module_rendering_in_scene()
        test_create_pv_module_3d()
        
        print("\n" + "=" * 70)
        print("ZUSAMMENFASSUNG")
        print("=" * 70)
        print("\nWenn alle Tests bestanden haben, liegt das Problem")
        print("wahrscheinlich in der UI-Integration oder im Rendering-Prozess.")
        print("\nMögliche Ursachen:")
        print("1. Session State wird nicht korrekt aktualisiert")
        print("2. build_plotly_scene() wird nicht aufgerufen")
        print("3. Module werden erstellt aber nicht zur Figure hinzugefügt")
        
    except Exception as e:
        print(f"\n[ERROR] KRITISCHER FEHLER: {e}")
        import traceback
        traceback.print_exc()
