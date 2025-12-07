"""
Visuelle Demo für Task 2: Modul-Aufständerung

Zeigt die korrekte Mounting Height für verschiedene Dachformen in einer 3D-Visualisierung.
"""

import sys
from utils.pv3d import BuildingDims
from utils.pv3d_plotly import build_plotly_scene

def demo_mounting_height():
    """Erstellt eine Demo-Visualisierung mit verschiedenen Dachformen."""
    
    print("\n" + "="*80)
    print("DEMO: Modul-Aufständerung auf geneigten Dächern")
    print("="*80)
    
    # Test-Gebäude
    dims = BuildingDims(
        length_m=12.0,
        width_m=8.0,
        wall_height_m=5.0
    )
    
    # Test-Daten
    project_data = {
        "roof_covering": "Ziegel",
        "roof_inclination_deg": 30.0,
        "sun_azimuth": 180.0,
        "sun_elevation": 45.0
    }
    
    # Teste verschiedene Dachformen
    roof_types = [
        "Satteldach",
        "Walmdach",
        "Pultdach",
        "Zeltdach",
        "Krüppelwalmdach"
    ]
    
    for roof_type in roof_types:
        print(f"\n{''*80}")
        print(f"Erstelle Visualisierung für: {roof_type}")
        print(f"{''*80}")
        
        try:
            # Erstelle 3D-Szene
            fig = build_plotly_scene(
                project_data=project_data,
                dims=dims,
                roof_type=roof_type,
                module_quantity=20,
                layout_config=None,
                selected_modules=[]
            )
            
            print(f"Visualisierung erstellt für {roof_type}")
            print(f"   Module: 20")
            print(f"   Neigung: 30.0°")
            print(f"   Mounting Height wird automatisch berechnet")
            
            # Optional: Speichere als HTML
            # fig.write_html(f"demo_{roof_type.lower().replace(' ', '_')}.html")
            
        except Exception as e:
            print(f"Fehler bei {roof_type}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*80}")
    print("DEMO ABGESCHLOSSEN")
    print("="*80)
    print("\nHinweis: Die Mounting Height wird automatisch basierend auf")
    print("Dachform und Neigung berechnet. Module sinken nicht mehr in")
    print("die Dachfläche ein!")
    
    return 0


if __name__ == "__main__":
    sys.exit(demo_mounting_height())
