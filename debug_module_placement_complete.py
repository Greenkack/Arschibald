"""
Debug-Script für vollständige Modul-Platzierung

Dieses Script simuliert den kompletten Ablauf und zeigt wo das Problem liegt.
"""


def debug_complete_flow():
    """
    Simuliert den kompletten Ablauf der Modul-Platzierung.
    """
    print("=" * 70)
    print("DEBUG: Vollständiger Modul-Platzierungs-Ablauf")
    print("=" * 70)
    print()
    
    # Simuliere Session State
    session_state = {
        "placed_module_positions": [],
        "placed_module_count": 0,
        "trigger_auto_placement": False
    }
    
    # Test-Parameter
    building_length = 10.0
    building_width = 8.0
    module_quantity = 20
    roof_type = "Satteldach"
    roof_pitch = 30.0
    
    print("SCHRITT 1: Initialisierung")
    print("-" * 70)
    print(f"  Gebäude: {building_length}m x {building_width}m")
    print(f"  Gewünschte Module: {module_quantity}")
    print(f"  Dachtyp: {roof_type}")
    print(f"  Dachneigung: {roof_pitch}°")
    print(f"  Session State:")
    print(f"    placed_module_count: {session_state['placed_module_count']}")
    print(f"    placed_module_positions: {len(session_state['placed_module_positions'])} Module")
    print()
    
    # SCHRITT 2: Automatische Platzierung beim ersten Laden
    print("SCHRITT 2: Automatische Platzierung (beim ersten Laden)")
    print("-" * 70)
    
    current_placed = session_state.get("placed_module_count", 0)
    
    if current_placed == 0 and module_quantity > 0:
        print("  ✓ Bedingung erfüllt: Keine Module platziert, starte Auto-Placement")
        
        from utils.pv3d_placement_handler import handle_auto_placement
        
        result = handle_auto_placement(
            roof_length=building_length,
            roof_width=building_width,
            module_quantity=module_quantity,
            roof_type=roof_type,
            roof_pitch=roof_pitch
        )
        
        print(f"  Ergebnis:")
        print(f"    Success: {result['success']}")
        print(f"    Count: {result['count']}")
        print(f"    Message: {result['message']}")
        print(f"    Positions: {len(result['positions'])} Module")
        
        if result["success"]:
            # Update Session State
            session_state["placed_module_positions"] = result["positions"]
            session_state["placed_module_count"] = result["count"]
            current_placed = result["count"]
            
            print(f"  ✓ Session State aktualisiert:")
            print(f"    placed_module_count: {session_state['placed_module_count']}")
            print(f"    placed_module_positions: {len(session_state['placed_module_positions'])} Module")
        else:
            print(f"  ❌ Platzierung fehlgeschlagen!")
    else:
        print(f"  ⚠️ Bedingung NICHT erfüllt:")
        print(f"    current_placed = {current_placed}")
        print(f"    module_quantity = {module_quantity}")
    
    print()
    
    # SCHRITT 3: 3D-Szene Rendering
    print("SCHRITT 3: 3D-Szene Rendering")
    print("-" * 70)
    
    placed_positions = session_state.get("placed_module_positions", [])
    
    print(f"  Lade Module aus Session State:")
    print(f"    placed_positions: {len(placed_positions)} Module")
    
    if placed_positions:
        print(f"  ✓ Module gefunden, rendere...")
        
        # Zeige erste 3 Positionen
        for i, pos in enumerate(placed_positions[:3]):
            x, y, z_rel = pos
            wall_height = 6.0  # Beispiel
            z_abs = wall_height + z_rel
            print(f"    Modul {i}: ({x:.2f}, {y:.2f}, {z_rel:.2f}) → Z_abs: {z_abs:.2f}m")
        
        if len(placed_positions) > 3:
            print(f"    ... und {len(placed_positions) - 3} weitere Module")
        
        print(f"  ✓ Module sollten in 3D-Szene sichtbar sein!")
    else:
        print(f"  ❌ KEINE Module gefunden!")
        print(f"  Problem: Session State ist leer oder wurde nicht aktualisiert")
    
    print()
    
    # SCHRITT 4: Zusammenfassung
    print("=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)
    print()
    
    if session_state["placed_module_count"] > 0:
        print(f"✅ SUCCESS: {session_state['placed_module_count']} Module platziert!")
        print()
        print("Module sollten sichtbar sein wenn:")
        print("  1. ✓ Session State korrekt aktualisiert")
        print("  2. ✓ build_plotly_scene liest Session State")
        print("  3. ✓ create_pv_module_3d rendert Module")
        print()
        
        # Prüfe Z-Positionen
        print("Z-Positions-Prüfung:")
        if placed_positions:
            z_rel = placed_positions[0][2]
            wall_height = 6.0
            z_abs = wall_height + z_rel
            print(f"  Relative Z: {z_rel:.2f}m")
            print(f"  Wall Height: {wall_height:.2f}m")
            print(f"  Absolute Z: {z_abs:.2f}m")
            
            if z_abs > wall_height:
                print(f"  ✓ Module sind ÜBER der Wandhöhe (auf dem Dach)")
            else:
                print(f"  ❌ Module sind UNTER der Wandhöhe (Problem!)")
    else:
        print(f"❌ FEHLER: Keine Module platziert!")
        print()
        print("Mögliche Ursachen:")
        print("  1. handle_auto_placement gibt success=False zurück")
        print("  2. Session State wird nicht aktualisiert")
        print("  3. Bedingung für Auto-Placement nicht erfüllt")
    
    print()


if __name__ == "__main__":
    debug_complete_flow()
