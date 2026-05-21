"""
Verification Script for Phase 3 Task 13.1 - Vergleichs-System

Testet alle Funktionen des Vergleichs-Systems.

Author: PV3D Team
Date: 2025-01-03
"""

import sys
import streamlit as st
from typing import Dict, Any

# Import der zu testenden Funktionen
from utils.pv3d_comparison import (
    create_comparison_view,
    highlight_differences,
    create_comparison_table,
    save_configuration,
    delete_configuration,
    list_saved_configurations,
    init_comparison_session_state,
    _positions_equal,
    _build_scene_traces
)


def create_sample_config_a() -> Dict[str, Any]:
    """Erstellt Beispiel-Konfiguration A."""
    return {
        "name": "Optimiert fuer Ertrag",
        "module_positions": [
            (0.0, 0.0, 0.3),
            (2.0, 0.0, 0.3),
            (4.0, 0.0, 0.3)
        ],
        "building_dims": {
            "length": 10.0,
            "width": 8.0,
            "height": 5.0
        },
        "roof_type": "Flachdach",
        "module_transforms": {
            0: {"azimuth": 180.0, "tilt": 30.0},
            1: {"azimuth": 180.0, "tilt": 30.0},
            2: {"azimuth": 180.0, "tilt": 30.0}
        },
        "module_count": 3,
        "total_yield_kwh": 4500.0,
        "total_cost_eur": 6000.0,
        "roi_years": 8.5,
        "co2_savings_kg": 2250.0
    }


def create_sample_config_b() -> Dict[str, Any]:
    """Erstellt Beispiel-Konfiguration B."""
    return {
        "name": "Optimiert fuer Anzahl",
        "module_positions": [
            (0.0, 0.0, 0.3),
            (1.5, 0.0, 0.3),
            (3.0, 0.0, 0.3),
            (4.5, 0.0, 0.3)
        ],
        "building_dims": {
            "length": 10.0,
            "width": 8.0,
            "height": 5.0
        },
        "roof_type": "Flachdach",
        "module_transforms": {},
        "module_count": 4,
        "total_yield_kwh": 5200.0,
        "total_cost_eur": 8000.0,
        "roi_years": 9.2,
        "co2_savings_kg": 2600.0
    }


def run_tests():
    """Führt alle Verifikations-Tests aus."""
    print("=" * 80)
    print("PHASE 3 TASK 13.1 - VERGLEICHS-SYSTEM VERIFICATION")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    # Test 1: create_comparison_view
    print("Test 1: create_comparison_view() erstellt Figure mit 2 Subplots")
    try:
        config_a = create_sample_config_a()
        config_b = create_sample_config_b()
        fig = create_comparison_view(config_a, config_b)
        
        assert fig is not None, "Figure ist None"
        assert hasattr(fig, 'data'), "Figure hat kein data Attribut"
        assert len(fig.data) > 0, "Figure hat keine Traces"
        assert 'scene' in fig.layout, "Figure hat keine scene"
        assert 'scene2' in fig.layout, "Figure hat keine scene2"
        
        print("✓ PASSED")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()
    
    # Test 2: Kamera-Synchronisation
    print("Test 2: Kamera-Synchronisation funktioniert")
    try:
        config_a = create_sample_config_a()
        config_b = create_sample_config_b()
        fig = create_comparison_view(config_a, config_b, sync_camera=True)
        
        scene1_camera = fig.layout.scene.camera
        scene2_camera = fig.layout.scene2.camera
        
        assert scene1_camera == scene2_camera, "Kameras sind nicht synchronisiert"
        
        print("✓ PASSED")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()
    
    # Test 3: Gebaeude-Meshes
    print("Test 3: Figure enthaelt Gebaeude-Meshes")
    try:
        config_a = create_sample_config_a()
        config_b = create_sample_config_b()
        fig = create_comparison_view(config_a, config_b)
        
        building_traces = [
            trace for trace in fig.data
            if hasattr(trace, 'name') and 'Box' in str(trace.name)
        ]
        
        assert len(building_traces) >= 2, f"Nur {len(building_traces)} Gebaeude-Meshes gefunden"
        
        print(f"✓ PASSED ({len(building_traces)} Gebaeude-Meshes gefunden)")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()
    
    # Test 4: Modul-Meshes
    print("Test 4: Figure enthaelt Modul-Meshes")
    try:
        config_a = create_sample_config_a()
        config_b = create_sample_config_b()
        fig = create_comparison_view(config_a, config_b)
        
        module_traces = [
            trace for trace in fig.data
            if hasattr(trace, 'name') and 'Modul' in str(trace.name)
        ]
        
        assert len(module_traces) >= 7, f"Nur {len(module_traces)} Modul-Meshes gefunden (erwartet: 7)"
        
        print(f"✓ PASSED ({len(module_traces)} Modul-Meshes gefunden)")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()
    
    # Test 5: highlight_differences - Module nur in A
    print("Test 5: highlight_differences() markiert Module nur in A (rot)")
    try:
        config_a = create_sample_config_a()
        config_b = create_sample_config_b()
        fig = create_comparison_view(config_a, config_b)
        fig = highlight_differences(fig, config_a, config_b)
        
        red_markers = [
            trace for trace in fig.data
            if hasattr(trace, 'marker') and 
            hasattr(trace.marker, 'color') and
            trace.marker.color == 'red'
        ]
        
        assert len(red_markers) > 0, "Keine roten Marker gefunden"
        
        print(f"✓ PASSED ({len(red_markers)} rote Marker gefunden)")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()
    
    # Test 6: highlight_differences - Module nur in B
    print("Test 6: highlight_differences() markiert Module nur in B (gruen)")
    try:
        config_a = create_sample_config_a()
        config_b = create_sample_config_b()
        fig = create_comparison_view(config_a, config_b)
        fig = highlight_differences(fig, config_a, config_b)
        
        green_markers = [
            trace for trace in fig.data
            if hasattr(trace, 'marker') and 
            hasattr(trace.marker, 'color') and
            trace.marker.color == 'green'
        ]
        
        assert len(green_markers) > 0, "Keine gruenen Marker gefunden"
        
        print(f"✓ PASSED ({len(green_markers)} gruene Marker gefunden)")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()
    
    # Test 7: create_comparison_table
    print("Test 7: create_comparison_table() erstellt DataFrame")
    try:
        config_a = create_sample_config_a()
        config_b = create_sample_config_b()
        df = create_comparison_table(config_a, config_b)
        
        import pandas as pd
        assert isinstance(df, pd.DataFrame), "Kein DataFrame erstellt"
        assert len(df) > 0, "DataFrame ist leer"
        
        print(f"✓ PASSED (DataFrame mit {len(df)} Zeilen)")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()
    
    # Test 8: Tabelle enthaelt alle Metriken
    print("Test 8: Tabelle enthaelt alle Metriken")
    try:
        config_a = create_sample_config_a()
        config_b = create_sample_config_b()
        df = create_comparison_table(config_a, config_b)
        
        expected_metrics = [
            "Modulanzahl",
            "Gesamtertrag (kWh/Jahr)",
            "Kosten (€)",
            "ROI (Jahre)",
            "CO₂-Einsparung (kg/Jahr)",
            "Ertrag pro Modul (kWh)"
        ]
        
        for metric in expected_metrics:
            assert metric in df["Metrik"].values, f"Metrik '{metric}' fehlt"
        
        print(f"✓ PASSED (Alle {len(expected_metrics)} Metriken vorhanden)")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()
    
    # Test 9: Tabelle berechnet Differenzen
    print("Test 9: Tabelle berechnet Differenzen")
    try:
        config_a = create_sample_config_a()
        config_b = create_sample_config_b()
        df = create_comparison_table(config_a, config_b)
        
        assert "Differenz (B - A)" in df.columns, "Differenz-Spalte fehlt"
        
        for diff in df["Differenz (B - A)"]:
            assert diff is not None, "Differenz ist None"
            assert len(str(diff)) > 0, "Differenz ist leer"
        
        print("✓ PASSED")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()
    
    # Test 10: save_configuration
    print("Test 10: save_configuration() speichert Konfiguration")
    try:
        st.session_state.clear()
        config_a = create_sample_config_a()
        
        success = save_configuration(
            name=config_a["name"],
            module_positions=config_a["module_positions"],
            building_dims=config_a["building_dims"],
            roof_type=config_a["roof_type"],
            metrics={
                "total_yield_kwh": config_a["total_yield_kwh"],
                "module_count": config_a["module_count"]
            }
        )
        
        assert success is True, "Speichern fehlgeschlagen"
        assert "saved_configurations" in st.session_state, "Session State nicht initialisiert"
        assert config_a["name"] in st.session_state["saved_configurations"], "Konfiguration nicht gespeichert"
        
        print("✓ PASSED")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()
    
    # Test 11: delete_configuration
    print("Test 11: delete_configuration() loescht Konfiguration")
    try:
        st.session_state.clear()
        config_a = create_sample_config_a()
        
        save_configuration(
            name=config_a["name"],
            module_positions=config_a["module_positions"],
            building_dims=config_a["building_dims"],
            roof_type=config_a["roof_type"]
        )
        
        success = delete_configuration(config_a["name"])
        
        assert success is True, "Loeschen fehlgeschlagen"
        assert config_a["name"] not in st.session_state.get("saved_configurations", {}), "Konfiguration noch vorhanden"
        
        print("✓ PASSED")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()
    
    # Test 12: list_saved_configurations
    print("Test 12: list_saved_configurations() listet Konfigurationen")
    try:
        st.session_state.clear()
        config_a = create_sample_config_a()
        config_b = create_sample_config_b()
        
        save_configuration(
            name=config_a["name"],
            module_positions=config_a["module_positions"],
            building_dims=config_a["building_dims"],
            roof_type=config_a["roof_type"]
        )
        
        save_configuration(
            name=config_b["name"],
            module_positions=config_b["module_positions"],
            building_dims=config_b["building_dims"],
            roof_type=config_b["roof_type"]
        )
        
        configs = list_saved_configurations()
        
        assert len(configs) == 2, f"Falsche Anzahl: {len(configs)}"
        assert config_a["name"] in configs, "Config A fehlt"
        assert config_b["name"] in configs, "Config B fehlt"
        
        print(f"✓ PASSED ({len(configs)} Konfigurationen gefunden)")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()
    
    # Test 13: init_comparison_session_state
    print("Test 13: init_comparison_session_state() initialisiert Session State")
    try:
        st.session_state.clear()
        
        init_comparison_session_state()
        
        assert "saved_configurations" in st.session_state, "saved_configurations fehlt"
        assert "comparison_sync_camera" in st.session_state, "comparison_sync_camera fehlt"
        assert "comparison_show_differences" in st.session_state, "comparison_show_differences fehlt"
        
        print("✓ PASSED")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()
    
    # Test 14: _positions_equal - identische Positionen
    print("Test 14: _positions_equal() erkennt identische Positionen")
    try:
        pos1 = (0.0, 0.0, 0.3)
        pos2 = (0.0, 0.0, 0.3)
        
        assert _positions_equal(pos1, pos2, tolerance=0.1) is True, "Identische Positionen nicht erkannt"
        
        print("✓ PASSED")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()
    
    # Test 15: _positions_equal - Toleranz
    print("Test 15: _positions_equal() beruecksichtigt Toleranz")
    try:
        pos1 = (0.0, 0.0, 0.3)
        pos2 = (0.05, 0.05, 0.3)
        
        assert _positions_equal(pos1, pos2, tolerance=0.1) is True, "Positionen innerhalb Toleranz nicht erkannt"
        assert _positions_equal(pos1, pos2, tolerance=0.01) is False, "Positionen ausserhalb Toleranz falsch erkannt"
        
        print("✓ PASSED")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()
    
    # Test 16: _build_scene_traces
    print("Test 16: _build_scene_traces() erstellt Gebaeude und Module")
    try:
        config_a = create_sample_config_a()
        traces = _build_scene_traces(config_a)
        
        assert len(traces) > 0, "Keine Traces erstellt"
        assert len(traces) >= 4, f"Zu wenige Traces: {len(traces)} (erwartet: >= 4)"
        
        building_trace = traces[0]
        assert hasattr(building_trace, 'name'), "Trace hat keinen Namen"
        assert 'Box' in building_trace.name, "Erstes Trace ist kein Gebaeude"
        
        module_traces = [t for t in traces if 'Modul' in str(t.name)]
        assert len(module_traces) == 3, f"Falsche Anzahl Module: {len(module_traces)}"
        
        print(f"✓ PASSED ({len(traces)} Traces, davon {len(module_traces)} Module)")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        failed += 1
    print()
    
    # Zusammenfassung
    print("=" * 80)
    print("ZUSAMMENFASSUNG")
    print("=" * 80)
    print(f"Tests bestanden: {passed}/16")
    print(f"Tests fehlgeschlagen: {failed}/16")
    print(f"Erfolgsrate: {(passed/16)*100:.1f}%")
    print()
    
    if failed == 0:
        print("✓ ALLE TESTS BESTANDEN!")
        return 0
    else:
        print(f"✗ {failed} TEST(S) FEHLGESCHLAGEN")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
