"""
Demo für Task 8.2: Modul-Details im Hover-Text

Zeigt wie die Modul-Details in der 3D-Visualisierung angezeigt werden.
"""

import sys
import os

# Füge utils zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.pv3d_plotly import create_pv_module_3d
import plotly.graph_objects as go


def demo_module_details():
    """
    Erstellt eine Demo-Visualisierung mit mehreren Modulen
    die verschiedene Details im Hover-Text zeigen.
    """
    print("\n" + "=" * 70)
    print("DEMO: MODUL-DETAILS IM HOVER-TEXT")
    print("=" * 70)
    print("\nErstelle 3D-Visualisierung mit 6 Modulen...")
    
    # Erstelle Figure
    fig = go.Figure()
    
    # Modul-Konfigurationen für Demo
    modules = [
        {
            "x": -3.0, "y": -2.0, "z": 5.0,
            "azimuth": 0, "tilt": 30,
            "number": 1, "power": 400,
            "description": "Süd-Ausrichtung, 400W"
        },
        {
            "x": 0.0, "y": -2.0, "z": 5.0,
            "azimuth": 45, "tilt": 30,
            "number": 2, "power": 420,
            "description": "Süd-West, 420W"
        },
        {
            "x": 3.0, "y": -2.0, "z": 5.0,
            "azimuth": 90, "tilt": 30,
            "number": 3, "power": 450,
            "description": "West-Ausrichtung, 450W"
        },
        {
            "x": -3.0, "y": 2.0, "z": 5.0,
            "azimuth": 180, "tilt": 25,
            "number": 4, "power": 400,
            "description": "Nord-Ausrichtung, 400W"
        },
        {
            "x": 0.0, "y": 2.0, "z": 5.0,
            "azimuth": 270, "tilt": 35,
            "number": 5, "power": 430,
            "description": "Ost-Ausrichtung, 430W"
        },
        {
            "x": 3.0, "y": 2.0, "z": 5.0,
            "azimuth": 315, "tilt": 30,
            "number": 6, "power": 400,
            "description": "Süd-Ost, 400W"
        },
    ]
    
    # Erstelle Module
    for module_config in modules:
        module, _ = create_pv_module_3d(
            x=module_config["x"],
            y=module_config["y"],
            z=module_config["z"],
            azimuth_deg=module_config["azimuth"],
            tilt_deg=module_config["tilt"],
            module_number=module_config["number"],
            module_power_w=module_config["power"]
        )
        fig.add_trace(module)
        
        print(f"  [OK] Modul #{module_config['number']}: {module_config['description']}")
    
    # Layout konfigurieren
    fig.update_layout(
        title=dict(
            text="Task 8.2: Modul-Details im Hover-Text<br><sub>Bewegen Sie die Maus über ein Modul um Details zu sehen</sub>",
            font=dict(size=20, color='#333333')
        ),
        scene=dict(
            xaxis=dict(title="X (m)", range=[-5, 5]),
            yaxis=dict(title="Y (m)", range=[-5, 5]),
            zaxis=dict(title="Z (m)", range=[0, 10]),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2)
            ),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=0.5)
        ),
        width=1200,
        height=800,
        showlegend=False,
        hovermode='closest'
    )
    
    # Speichere als HTML
    output_file = "demo_module_details_hover.html"
    fig.write_html(output_file)
    
    print(f"\n[OK] Demo-Visualisierung erstellt: {output_file}")
    print("\nÖffnen Sie die Datei im Browser und bewegen Sie die Maus über die Module.")
    print("Sie sehen dann folgende Informationen:")
    print("  • Modul-Nummer (z.B. 'Modul #1')")
    print("  • Leistung in Watt (z.B. '400 W')")
    print("  • Azimut in Grad und Himmelsrichtung (z.B. '0.0° (Süd)')")
    print("  • Neigung in Grad (z.B. '30.0°')")
    print("  • Position in Metern (z.B. '(-3.00, -2.00, 5.00) m')")
    
    print("\n" + "=" * 70)
    print("HOVER-TEXT BEISPIELE:")
    print("=" * 70)
    
    for module_config in modules:
        print(f"\nModul #{module_config['number']} ({module_config['description']}):")
        print(f"  Leistung: {module_config['power']} W")
        print(f"  Azimut: {module_config['azimuth']}°")
        print(f"  Neigung: {module_config['tilt']}°")
        print(f"  Position: ({module_config['x']:.2f}, {module_config['y']:.2f}, {module_config['z']:.2f}) m")
    
    print("\n")


if __name__ == "__main__":
    try:
        demo_module_details()
    except Exception as e:
        print(f"\n[ERROR] FEHLER: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
