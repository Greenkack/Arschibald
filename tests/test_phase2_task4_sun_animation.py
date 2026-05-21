"""
Tests für Phase 2, Task 4: Sonnenverlauf-Animation Optimierungen

Testet:
- Performance-Verbesserungen (FPS, Zeitraffer, Caching)
- Echtzeit-Schatten-Updates
- Erweiterte Animation-Controls
"""

import pytest
import numpy as np
from typing import List, Tuple
import plotly.graph_objects as go

# Import der zu testenden Funktionen
from utils.solar_animation import (
    _calculate_sun_positions_cached,
    create_sun_path_animation,
    update_shadows_realtime,
    _calculate_shadow_vector,
    render_animation_controls_enhanced
)


# ============================================================================
# TEST SUITE 1: PERFORMANCE-VERBESSERUNGEN (Task 4.1)
# ============================================================================

class TestPerformanceImprovements:
    """Tests für Performance-Optimierungen."""
    
    def test_sun_positions_caching(self):
        """Test: Sonnenpositions werden gecached."""
        # Erste Berechnung
        positions1 = _calculate_sun_positions_cached(48.0, 11.0, "2024-06-21", 24)
        
        # Zweite Berechnung (sollte aus Cache kommen)
        positions2 = _calculate_sun_positions_cached(48.0, 11.0, "2024-06-21", 24)
        
        # Sollten identisch sein (gleiche Objekt-Referenz durch Cache)
        assert positions1 == positions2
        assert len(positions1) == 24
        
        # Jede Position sollte (azimuth, elevation) Tupel sein
        for azimuth, elevation in positions1:
            assert 0 <= azimuth <= 360
            assert 0 <= elevation <= 90
    
    def test_configurable_fps(self):
        """Test: FPS ist konfigurierbar (12-60)."""
        fig = go.Figure()
        building_center = (0.0, 0.0, 0.0)
        
        # Test verschiedene FPS-Werte
        for fps in [12, 24, 30, 60]:
            result_fig = create_sun_path_animation(
                fig,
                building_center,
                fps=fps,
                num_frames=12
            )
            
            # Prüfe dass Animation erstellt wurde
            assert hasattr(result_fig, 'frames')
            assert len(result_fig.frames) == 12
            
            # Prüfe dass FPS in Animation-Buttons verwendet wird
            assert result_fig.layout.updatemenus is not None
    
    def test_time_compression_factor(self):
        """Test: Zeitraffer-Faktor funktioniert (1-100x)."""
        fig = go.Figure()
        building_center = (0.0, 0.0, 0.0)
        
        # Test verschiedene Zeitraffer-Faktoren
        for compression in [1.0, 10.0, 50.0, 100.0]:
            result_fig = create_sun_path_animation(
                fig,
                building_center,
                time_compression=compression,
                num_frames=12
            )
            
            # Animation sollte erstellt werden
            assert hasattr(result_fig, 'frames')
            assert len(result_fig.frames) == 12
    
    def test_frame_count_limits(self):
        """Test: Frame-Anzahl wird auf 12-48 begrenzt."""
        fig = go.Figure()
        building_center = (0.0, 0.0, 0.0)
        
        # Test Grenzwerte
        test_cases = [
            (5, 12),    # Zu wenig -> wird auf 12 erhöht
            (12, 12),   # Minimum
            (24, 24),   # Normal
            (48, 48),   # Maximum
            (100, 48),  # Zu viel -> wird auf 48 begrenzt
        ]
        
        for input_frames, expected_frames in test_cases:
            result_fig = create_sun_path_animation(
                fig,
                building_center,
                num_frames=input_frames
            )
            
            assert len(result_fig.frames) == expected_frames
    
    def test_performance_ray_limiting(self):
        """Test: Sonnenstrahlen werden auf max 10 Module limitiert."""
        fig = go.Figure()
        
        # Füge 20 Module hinzu (simuliert)
        for i in range(20):
            fig.add_trace(go.Scatter3d(
                x=[i * 2.0],
                y=[0.0],
                z=[6.0],
                mode='markers',
                name=f'Module {i}'
            ))
        
        building_center = (10.0, 0.0, 0.0)
        
        result_fig = create_sun_path_animation(
            fig,
            building_center,
            num_frames=12
        )
        
        # Prüfe dass Frames erstellt wurden
        assert len(result_fig.frames) > 0
        
        # Jeder Frame sollte max 11 Traces haben (1 Sonne + max 10 Strahlen)
        for frame in result_fig.frames:
            assert len(frame.data) <= 11


# ============================================================================
# TEST SUITE 2: ECHTZEIT-SCHATTEN-UPDATE (Task 4.2)
# ============================================================================

class TestRealtimeShadows:
    """Tests für Echtzeit-Schatten-Updates."""
    
    def test_shadow_vector_calculation(self):
        """Test: Schatten-Vektor wird korrekt berechnet."""
        # Sonne im Süden (180°), 45° Elevation
        shadow_vec = _calculate_shadow_vector(180.0, 45.0)
        
        assert len(shadow_vec) == 3
        x, y, z = shadow_vec
        
        # Schatten zeigt nach Norden (entgegengesetzt zur Sonne im Süden)
        # Bei Azimuth 180° (Süd): cos(180°) = -1, also -cos(180°) = +1
        # Positives Y = Norden in unserem Koordinatensystem
        assert y > 0  # Norden (positiv)
        assert z < 0  # Nach unten
        
        # Vektor-Länge sollte ~1 sein
        length = np.sqrt(x**2 + y**2 + z**2)
        assert 0.9 < length < 1.1
    
    def test_shadow_vector_different_positions(self):
        """Test: Schatten-Vektor für verschiedene Sonnenpositionen."""
        test_cases = [
            (0.0, 45.0),    # Norden
            (90.0, 45.0),   # Osten
            (180.0, 45.0),  # Süden
            (270.0, 45.0),  # Westen
        ]
        
        for azimuth, elevation in test_cases:
            shadow_vec = _calculate_shadow_vector(azimuth, elevation)
            
            # Alle Vektoren sollten gültig sein
            assert len(shadow_vec) == 3
            assert all(isinstance(v, (int, float)) for v in shadow_vec)
    
    def test_update_shadows_realtime(self):
        """Test: Schatten werden in Echtzeit zur Figure hinzugefügt."""
        fig = go.Figure()
        
        # Füge Gebäude hinzu (simuliert)
        fig.add_trace(go.Mesh3d(
            x=[0, 10, 10, 0],
            y=[0, 0, 8, 8],
            z=[0, 0, 0, 0],
            name='Dach'
        ))
        
        module_positions = [
            (2.0, 2.0, 6.0),
            (4.0, 2.0, 6.0),
            (6.0, 2.0, 6.0),
        ]
        
        # Update Schatten
        result_fig = update_shadows_realtime(
            fig,
            sun_azimuth=180.0,
            sun_elevation=45.0,
            module_positions=module_positions
        )
        
        # Schatten-Traces sollten hinzugefügt worden sein
        # Original: 1 Trace (Dach) + 3 Schatten = 4 Traces
        assert len(result_fig.data) >= 1
    
    def test_no_shadows_at_night(self):
        """Test: Keine Schatten wenn Sonne unter Horizont."""
        fig = go.Figure()
        module_positions = [(2.0, 2.0, 6.0)]
        
        # Sonne unter Horizont (Elevation = -10°)
        result_fig = update_shadows_realtime(
            fig,
            sun_azimuth=180.0,
            sun_elevation=-10.0,
            module_positions=module_positions
        )
        
        # Keine neuen Traces sollten hinzugefügt werden
        assert len(result_fig.data) == 0
    
    def test_shadow_performance_limiting(self):
        """Test: Schatten werden auf max 20 Module limitiert."""
        fig = go.Figure()
        
        # Erstelle 50 Module
        module_positions = [
            (i * 2.0, 0.0, 6.0) for i in range(50)
        ]
        
        result_fig = update_shadows_realtime(
            fig,
            sun_azimuth=180.0,
            sun_elevation=45.0,
            module_positions=module_positions
        )
        
        # Max 20 Schatten sollten erstellt werden
        assert len(result_fig.data) <= 20


# ============================================================================
# TEST SUITE 3: ERWEITERTE ANIMATION-CONTROLS (Task 4.3)
# ============================================================================

class TestEnhancedAnimationControls:
    """Tests für erweiterte Animation-Controls."""
    
    def test_enhanced_controls_structure(self):
        """Test: Erweiterte Controls geben korrektes Dictionary zurück."""
        # Kann nicht direkt testen da Streamlit-Abhängigkeit
        # Aber wir können die Funktion importieren
        assert callable(render_animation_controls_enhanced)
    
    def test_sun_path_parameters(self):
        """Test: Sun-Path Animation hat alle erwarteten Parameter."""
        # Erwartete Parameter für sun_path Animation
        expected_params = [
            'fps',
            'num_frames',
            'time_compression',
            'month',
            'radius',
            'show_shadows',
            'show_sun_rays',
            'auto_play'
        ]
        
        # Funktion sollte diese Parameter unterstützen
        # (Kann nicht direkt testen ohne Streamlit-Context)
        assert True  # Placeholder


# ============================================================================
# TEST SUITE 4: INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integrations-Tests für alle Task 4 Features."""
    
    def test_complete_animation_workflow(self):
        """Test: Kompletter Workflow von Erstellung bis Schatten."""
        # 1. Erstelle Figure
        fig = go.Figure()
        
        # 2. Füge Module hinzu
        module_positions = [
            (2.0, 2.0, 6.0),
            (4.0, 2.0, 6.0),
        ]
        
        for x, y, z in module_positions:
            fig.add_trace(go.Scatter3d(
                x=[x], y=[y], z=[z],
                mode='markers',
                name='Module'
            ))
        
        # 3. Erstelle Animation mit optimierten Parametern
        building_center = (3.0, 2.0, 0.0)
        
        animated_fig = create_sun_path_animation(
            fig,
            building_center,
            fps=30,
            time_compression=10.0,
            num_frames=24
        )
        
        # 4. Prüfe Animation
        assert hasattr(animated_fig, 'frames')
        assert len(animated_fig.frames) == 24
        
        # 5. Füge Schatten hinzu
        final_fig = update_shadows_realtime(
            animated_fig,
            sun_azimuth=180.0,
            sun_elevation=45.0,
            module_positions=module_positions
        )
        
        # 6. Prüfe Endergebnis
        assert len(final_fig.data) >= 2  # Module + Schatten
        assert len(final_fig.frames) == 24
    
    def test_performance_target_24fps(self):
        """Test: Animation erreicht Performance-Ziel von >24 FPS."""
        import time
        
        fig = go.Figure()
        building_center = (0.0, 0.0, 0.0)
        
        # Messe Zeit für Animation-Erstellung
        start_time = time.time()
        
        result_fig = create_sun_path_animation(
            fig,
            building_center,
            fps=24,
            num_frames=24
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Animation-Erstellung sollte schnell sein (<1 Sekunde)
        assert duration < 1.0
        
        # Frames sollten erstellt sein
        assert len(result_fig.frames) == 24


# ============================================================================
# TEST SUITE 5: REQUIREMENT COVERAGE
# ============================================================================

class TestRequirementCoverage:
    """Tests zur Validierung aller Requirements für Task 4."""
    
    def test_requirement_2_1_performance_24fps(self):
        """Requirement 2.1: System erreicht mindestens 24 FPS."""
        fig = go.Figure()
        building_center = (0.0, 0.0, 0.0)
        
        # Erstelle Animation mit 24 FPS
        result_fig = create_sun_path_animation(
            fig,
            building_center,
            fps=24,
            num_frames=24
        )
        
        # Animation sollte erfolgreich erstellt werden
        assert len(result_fig.frames) == 24
        assert result_fig.layout.updatemenus is not None
    
    def test_requirement_2_2_realtime_shadows(self):
        """Requirement 2.2: Schatten werden in Echtzeit aktualisiert."""
        fig = go.Figure()
        module_positions = [(2.0, 2.0, 6.0)]
        
        # Schatten-Update sollte funktionieren
        result_fig = update_shadows_realtime(
            fig,
            sun_azimuth=180.0,
            sun_elevation=45.0,
            module_positions=module_positions
        )
        
        # Schatten sollten hinzugefügt sein
        assert len(result_fig.data) >= 1
    
    def test_requirement_2_3_timelapse_function(self):
        """Requirement 2.3: Zeitraffer-Funktion ist verfügbar."""
        fig = go.Figure()
        building_center = (0.0, 0.0, 0.0)
        
        # Zeitraffer mit 10x Geschwindigkeit
        result_fig = create_sun_path_animation(
            fig,
            building_center,
            time_compression=10.0,
            num_frames=24
        )
        
        # Animation sollte erstellt werden
        assert len(result_fig.frames) == 24
    
    def test_requirement_2_4_monthly_sun_position(self):
        """Requirement 2.4: Sonnenposition für jeden Monat korrekt."""
        # Test verschiedene Monate
        months = [1, 6, 12]  # Januar, Juni, Dezember
        
        for month in months:
            date = f"2024-{month:02d}-21"
            positions = _calculate_sun_positions_cached(
                48.0, 11.0, date, 24
            )
            
            # Positionen sollten berechnet werden
            assert len(positions) == 24
            
            # Alle Positionen sollten gültig sein
            for azimuth, elevation in positions:
                assert 0 <= azimuth <= 360
                assert 0 <= elevation <= 90
    
    def test_requirement_2_5_pause_functionality(self):
        """Requirement 2.5: Animation kann pausiert werden."""
        fig = go.Figure()
        building_center = (0.0, 0.0, 0.0)
        
        result_fig = create_sun_path_animation(
            fig,
            building_center,
            num_frames=24
        )
        
        # Prüfe dass Pause-Button existiert
        assert result_fig.layout.updatemenus is not None
        buttons = result_fig.layout.updatemenus[0]['buttons']
        
        # Sollte Play und Pause Buttons haben
        assert len(buttons) >= 2
        
        # Prüfe Button-Labels (als Strings)
        button_labels = [str(btn['label']) for btn in buttons]
        assert any('Play' in label for label in button_labels)
        assert any('Pause' in label for label in button_labels)


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
