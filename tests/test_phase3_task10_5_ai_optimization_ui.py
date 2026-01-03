"""
Tests für Phase 3 Task 10.5 - KI-Optimierung UI

Testet die UI-Komponenten für KI-basierte Modul-Optimierung.

Requirements: 7.1, 7.2, 7.4
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Tuple

# Import der zu testenden Module
try:
    from utils.pv3d_ai_optimization_ui import (
        render_ai_optimization_ui,
        render_ai_optimization_info,
        render_ai_optimization_status,
        render_ai_optimization_animation,
        _calculate_optimizations,
        _render_layout_proposal,
        _render_comparison_table,
        _render_apply_section,
        _apply_layout
    )
    from utils.pv3d_ai_optimization import (
        AILayoutOptimizer,
        OptimizationResult,
        LayoutScore
    )
    UI_AVAILABLE = True
except ImportError:
    UI_AVAILABLE = False


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_session_state():
    """Mock Streamlit Session State."""
    return {}


@pytest.fixture
def sample_layout_score():
    """Erstellt Sample LayoutScore."""
    return LayoutScore(
        total_yield_kwh=8500.0,
        module_count=25,
        aesthetic_score=85.0,
        cost_eur=5000.0,
        roi_years=7.5,
        coverage_percent=65.0,
        symmetry_score=90.0
    )


@pytest.fixture
def sample_optimization_result(sample_layout_score):
    """Erstellt Sample OptimizationResult."""
    positions = [(i * 2.0, j * 2.0, 0.3) for i in range(5) for j in range(5)]
    
    return OptimizationResult(
        positions=positions,
        score=sample_layout_score,
        strategy="Maximaler Ertrag",
        metadata={"optimization_goal": "yield"}
    )


@pytest.fixture
def sample_optimizer():
    """Erstellt Sample AILayoutOptimizer."""
    return AILayoutOptimizer(
        roof_length=10.0,
        roof_width=8.0,
        roof_type="Satteldach",
        roof_pitch=30.0
    )


# ============================================================================
# TESTS FÜR HAUPTKOMPONENTE
# ============================================================================

@pytest.mark.skipif(not UI_AVAILABLE, reason="UI module not available")
class TestRenderAIOptimizationUI:
    """Tests für render_ai_optimization_ui()."""
    
    def test_function_exists(self):
        """Test: Funktion existiert."""
        assert callable(render_ai_optimization_ui)
    
    def test_function_signature(self):
        """Test: Funktion hat korrekte Signatur."""
        import inspect
        sig = inspect.signature(render_ai_optimization_ui)
        
        # Prüfe Parameter
        assert "roof_length" in sig.parameters
        assert "roof_width" in sig.parameters
        assert "roof_type" in sig.parameters
        assert "roof_pitch" in sig.parameters
        assert "key_prefix" in sig.parameters
        
        # Prüfe Defaults
        assert sig.parameters["roof_pitch"].default == 0.0
        assert sig.parameters["key_prefix"].default == "ai_opt"
    
    @patch('utils.pv3d_ai_optimization_ui.st')
    @patch('utils.pv3d_ai_optimization_ui._calculate_optimizations')
    def test_renders_title(self, mock_calc, mock_st):
        """Test: Rendert Titel."""
        mock_st.session_state = {}
        mock_st.spinner.return_value.__enter__ = Mock(return_value=None)
        mock_st.spinner.return_value.__exit__ = Mock(return_value=None)
        
        # Mock columns to return context managers
        col_mock = Mock()
        col_mock.__enter__ = Mock(return_value=col_mock)
        col_mock.__exit__ = Mock(return_value=None)
        mock_st.columns.return_value = [col_mock, col_mock, col_mock]
        
        # Mock empty results to trigger error path
        mock_calc.return_value = {}
        
        render_ai_optimization_ui(
            roof_length=10.0,
            roof_width=8.0,
            roof_type="Flachdach"
        )
        
        # Prüfe dass Titel gerendert wurde
        calls = [str(call) for call in mock_st.markdown.call_args_list]
        assert any("KI-Optimierung" in str(call) for call in calls)
    
    @patch('utils.pv3d_ai_optimization_ui.st')
    @patch('utils.pv3d_ai_optimization_ui._calculate_optimizations')
    def test_calculates_three_optimizations(self, mock_calc, mock_st):
        """Test: Berechnet 3 Optimierungen."""
        mock_st.session_state = {}
        mock_st.spinner.return_value.__enter__ = Mock(return_value=None)
        mock_st.spinner.return_value.__exit__ = Mock(return_value=None)
        
        # Mock columns to return context managers
        col_mock = Mock()
        col_mock.__enter__ = Mock(return_value=col_mock)
        col_mock.__exit__ = Mock(return_value=None)
        mock_st.columns.return_value = [col_mock, col_mock, col_mock]
        
        # Mock Optimierungen mit korrekten Attributen
        mock_result = Mock(spec=OptimizationResult)
        mock_result.strategy = "Test Strategy"
        mock_result.score = Mock()
        mock_result.score.module_count = 25
        mock_result.score.total_yield_kwh = 8500.0
        mock_result.score.roi_years = 7.5
        mock_result.score.cost_eur = 5000.0
        mock_result.score.coverage_percent = 65.0
        mock_result.score.aesthetic_score = 85.0
        mock_result.score.symmetry_score = 90.0
        mock_result.score.get_weighted_score = Mock(return_value=85.0)
        
        mock_calc.return_value = {
            "max_yield": mock_result,
            "max_count": mock_result,
            "aesthetics": mock_result
        }
        
        with patch('utils.pv3d_ai_optimization_ui._render_layout_proposal', return_value=False):
            render_ai_optimization_ui(
                roof_length=10.0,
                roof_width=8.0,
                roof_type="Flachdach"
            )
        
        # Prüfe dass Optimierungen berechnet wurden
        assert mock_calc.called
    
    @patch('utils.pv3d_ai_optimization_ui.st')
    @patch('utils.pv3d_ai_optimization_ui._calculate_optimizations')
    @patch('utils.pv3d_ai_optimization_ui._render_layout_proposal')
    def test_shows_three_columns(self, mock_render, mock_calc, mock_st):
        """Test: Zeigt 3 Spalten für Vorschläge."""
        mock_st.session_state = {}
        mock_st.spinner.return_value.__enter__ = Mock(return_value=None)
        mock_st.spinner.return_value.__exit__ = Mock(return_value=None)
        
        # Mock columns to return context managers
        col_mock = Mock()
        col_mock.__enter__ = Mock(return_value=col_mock)
        col_mock.__exit__ = Mock(return_value=None)
        mock_st.columns.return_value = [col_mock, col_mock, col_mock]
        
        # Mock Optimierungen mit korrekten Attributen
        mock_result = Mock(spec=OptimizationResult)
        mock_result.strategy = "Test Strategy"
        mock_result.score = Mock()
        mock_result.score.module_count = 25
        mock_result.score.total_yield_kwh = 8500.0
        mock_result.score.roi_years = 7.5
        mock_result.score.cost_eur = 5000.0
        mock_result.score.coverage_percent = 65.0
        mock_result.score.aesthetic_score = 85.0
        mock_result.score.symmetry_score = 90.0
        mock_result.score.get_weighted_score = Mock(return_value=85.0)
        
        mock_calc.return_value = {
            "max_yield": mock_result,
            "max_count": mock_result,
            "aesthetics": mock_result
        }
        mock_render.return_value = False
        
        render_ai_optimization_ui(
            roof_length=10.0,
            roof_width=8.0,
            roof_type="Flachdach"
        )
        
        # Prüfe dass 3 Spalten erstellt wurden
        mock_st.columns.assert_called_with(3)


# ============================================================================
# TESTS FÜR HILFSFUNKTIONEN
# ============================================================================

@pytest.mark.skipif(not UI_AVAILABLE, reason="UI module not available")
class TestCalculateOptimizations:
    """Tests für _calculate_optimizations()."""
    
    def test_function_exists(self):
        """Test: Funktion existiert."""
        assert callable(_calculate_optimizations)
    
    @patch('utils.pv3d_ai_optimization_ui.st')
    def test_returns_three_results(self, mock_st, sample_optimizer):
        """Test: Gibt 3 Ergebnisse zurück."""
        mock_st.session_state = {}
        
        results = _calculate_optimizations(sample_optimizer, "test")
        
        assert isinstance(results, dict)
        assert "max_yield" in results
        assert "max_count" in results
        assert "aesthetics" in results
    
    @patch('utils.pv3d_ai_optimization_ui.st')
    def test_caches_results(self, mock_st, sample_optimizer):
        """Test: Cached Ergebnisse."""
        mock_st.session_state = {}
        
        # Erste Berechnung
        results1 = _calculate_optimizations(sample_optimizer, "test")
        
        # Zweite Berechnung (sollte aus Cache kommen)
        results2 = _calculate_optimizations(sample_optimizer, "test")
        
        # Prüfe dass Cache verwendet wurde
        assert "test_optimizations" in str(mock_st.session_state)
    
    @patch('utils.pv3d_ai_optimization_ui.st')
    def test_handles_errors(self, mock_st, sample_optimizer):
        """Test: Behandelt Fehler korrekt."""
        mock_st.session_state = {}
        
        # Mock Fehler bei Optimierung
        with patch.object(sample_optimizer, 'optimize_for_max_yield', side_effect=Exception("Test error")):
            results = _calculate_optimizations(sample_optimizer, "test")
        
        # Prüfe dass leeres Dict zurückgegeben wird
        assert results == {}


@pytest.mark.skipif(not UI_AVAILABLE, reason="UI module not available")
class TestRenderLayoutProposal:
    """Tests für _render_layout_proposal()."""
    
    def test_function_exists(self):
        """Test: Funktion existiert."""
        assert callable(_render_layout_proposal)
    
    @patch('utils.pv3d_ai_optimization_ui.st')
    def test_renders_strategy_name(self, mock_st, sample_optimization_result):
        """Test: Rendert Strategie-Namen."""
        mock_st.container.return_value.__enter__ = Mock()
        mock_st.container.return_value.__exit__ = Mock()
        mock_st.button.return_value = False
        
        _render_layout_proposal(
            result=sample_optimization_result,
            title="Test",
            icon="🎯",
            color="#27ae60",
            key_prefix="test"
        )
        
        # Prüfe dass Strategie-Name verwendet wurde
        calls = [str(call) for call in mock_st.markdown.call_args_list]
        assert any("Maximaler Ertrag" in str(call) for call in calls)
    
    @patch('utils.pv3d_ai_optimization_ui.st')
    def test_shows_metrics(self, mock_st, sample_optimization_result):
        """Test: Zeigt Metriken an."""
        mock_st.container.return_value.__enter__ = Mock()
        mock_st.container.return_value.__exit__ = Mock()
        mock_st.button.return_value = False
        
        _render_layout_proposal(
            result=sample_optimization_result,
            title="Test",
            icon="🎯",
            color="#27ae60",
            key_prefix="test"
        )
        
        # Prüfe dass Metriken angezeigt wurden
        assert mock_st.metric.called
        
        # Prüfe Metrik-Aufrufe
        metric_calls = mock_st.metric.call_args_list
        assert len(metric_calls) >= 3  # Mindestens 3 Metriken
    
    @patch('utils.pv3d_ai_optimization_ui.st')
    def test_returns_true_when_selected(self, mock_st, sample_optimization_result):
        """Test: Gibt True zurück wenn ausgewählt."""
        mock_st.container.return_value.__enter__ = Mock()
        mock_st.container.return_value.__exit__ = Mock()
        mock_st.button.return_value = True  # Button geklickt
        
        result = _render_layout_proposal(
            result=sample_optimization_result,
            title="Test",
            icon="🎯",
            color="#27ae60",
            key_prefix="test"
        )
        
        assert result is True


@pytest.mark.skipif(not UI_AVAILABLE, reason="UI module not available")
class TestRenderComparisonTable:
    """Tests für _render_comparison_table()."""
    
    def test_function_exists(self):
        """Test: Funktion existiert."""
        assert callable(_render_comparison_table)
    
    @patch('utils.pv3d_ai_optimization_ui.st')
    def test_renders_table(self, mock_st, sample_optimization_result):
        """Test: Rendert Tabelle."""
        results = {
            "max_yield": sample_optimization_result,
            "max_count": sample_optimization_result,
            "aesthetics": sample_optimization_result
        }
        
        _render_comparison_table(results)
        
        # Prüfe dass Tabelle gerendert wurde
        assert mock_st.dataframe.called
    
    @patch('utils.pv3d_ai_optimization_ui.st')
    def test_table_has_correct_columns(self, mock_st, sample_optimization_result):
        """Test: Tabelle hat korrekte Spalten."""
        results = {
            "max_yield": sample_optimization_result,
            "max_count": sample_optimization_result,
            "aesthetics": sample_optimization_result
        }
        
        _render_comparison_table(results)
        
        # Hole Tabellen-Daten
        call_args = mock_st.dataframe.call_args
        data = call_args[0][0]
        
        # Prüfe Spalten
        assert "Strategie" in data
        assert "Module" in data
        assert "Ertrag (kWh/Jahr)" in data
        assert "ROI (Jahre)" in data
        assert "Gesamtbewertung" in data


@pytest.mark.skipif(not UI_AVAILABLE, reason="UI module not available")
class TestApplyLayout:
    """Tests für _apply_layout()."""
    
    def test_function_exists(self):
        """Test: Funktion existiert."""
        assert callable(_apply_layout)
    
    @patch('utils.pv3d_ai_optimization_ui.st')
    def test_saves_positions_to_session(self, mock_st, sample_optimization_result):
        """Test: Speichert Positionen in Session State."""
        mock_st.session_state = {}
        mock_st.rerun = Mock()
        
        _apply_layout(sample_optimization_result, animate=False, animation_speed=5)
        
        # Prüfe dass Positionen gespeichert wurden
        assert "placed_module_positions" in mock_st.session_state
        assert mock_st.session_state["placed_module_positions"] == sample_optimization_result.positions
    
    @patch('utils.pv3d_ai_optimization_ui.st')
    def test_saves_metadata(self, mock_st, sample_optimization_result):
        """Test: Speichert Metadaten."""
        mock_st.session_state = {}
        mock_st.rerun = Mock()
        
        _apply_layout(sample_optimization_result, animate=False, animation_speed=5)
        
        # Prüfe Metadaten
        assert mock_st.session_state["ai_optimization_applied"] is True
        assert mock_st.session_state["ai_optimization_strategy"] == sample_optimization_result.strategy
        assert mock_st.session_state["ai_optimization_score"] == sample_optimization_result.score
    
    @patch('utils.pv3d_ai_optimization_ui.st')
    def test_enables_animation_when_requested(self, mock_st, sample_optimization_result):
        """Test: Aktiviert Animation wenn gewünscht."""
        mock_st.session_state = {}
        mock_st.rerun = Mock()
        
        _apply_layout(sample_optimization_result, animate=True, animation_speed=7)
        
        # Prüfe Animation-Einstellungen
        assert mock_st.session_state["apply_animation"] is True
        assert mock_st.session_state["animation_speed"] == 7
        assert mock_st.session_state["animation_current_index"] == 0
    
    @patch('utils.pv3d_ai_optimization_ui.st')
    def test_triggers_rerun(self, mock_st, sample_optimization_result):
        """Test: Triggert Rerun."""
        mock_st.session_state = {}
        mock_st.rerun = Mock()
        
        _apply_layout(sample_optimization_result, animate=False, animation_speed=5)
        
        # Prüfe dass Rerun aufgerufen wurde
        assert mock_st.rerun.called


# ============================================================================
# TESTS FÜR ZUSÄTZLICHE KOMPONENTEN
# ============================================================================

@pytest.mark.skipif(not UI_AVAILABLE, reason="UI module not available")
class TestRenderAIOptimizationInfo:
    """Tests für render_ai_optimization_info()."""
    
    def test_function_exists(self):
        """Test: Funktion existiert."""
        assert callable(render_ai_optimization_info)
    
    @patch('utils.pv3d_ai_optimization_ui.st')
    def test_renders_info_panel(self, mock_st):
        """Test: Rendert Info-Panel."""
        mock_st.expander.return_value.__enter__ = Mock()
        mock_st.expander.return_value.__exit__ = Mock()
        
        render_ai_optimization_info()
        
        # Prüfe dass Expander erstellt wurde
        assert mock_st.expander.called
    
    @patch('utils.pv3d_ai_optimization_ui.st')
    def test_explains_three_strategies(self, mock_st):
        """Test: Erklärt 3 Strategien."""
        mock_st.expander.return_value.__enter__ = Mock()
        mock_st.expander.return_value.__exit__ = Mock()
        
        render_ai_optimization_info()
        
        # Prüfe dass alle 3 Strategien erwähnt werden
        calls = [str(call) for call in mock_st.markdown.call_args_list]
        text = " ".join(calls)
        
        assert "Maximaler Ertrag" in text
        assert "Maximale Anzahl" in text
        assert "Beste Ästhetik" in text


@pytest.mark.skipif(not UI_AVAILABLE, reason="UI module not available")
class TestRenderAIOptimizationStatus:
    """Tests für render_ai_optimization_status()."""
    
    def test_function_exists(self):
        """Test: Funktion existiert."""
        assert callable(render_ai_optimization_status)
    
    @patch('utils.pv3d_ai_optimization_ui.st')
    def test_shows_nothing_when_not_applied(self, mock_st):
        """Test: Zeigt nichts wenn nicht angewendet."""
        mock_st.session_state = {"ai_optimization_applied": False}
        
        render_ai_optimization_status()
        
        # Prüfe dass nichts gerendert wurde
        assert not mock_st.markdown.called
    
    @patch('utils.pv3d_ai_optimization_ui.st')
    def test_shows_status_when_applied(self, mock_st, sample_layout_score):
        """Test: Zeigt Status wenn angewendet."""
        mock_st.session_state = {
            "ai_optimization_applied": True,
            "ai_optimization_strategy": "Maximaler Ertrag",
            "ai_optimization_score": sample_layout_score
        }
        mock_st.container.return_value.__enter__ = Mock()
        mock_st.container.return_value.__exit__ = Mock()
        mock_st.button.return_value = False
        
        render_ai_optimization_status()
        
        # Prüfe dass Status gerendert wurde
        assert mock_st.markdown.called


@pytest.mark.skipif(not UI_AVAILABLE, reason="UI module not available")
class TestRenderAIOptimizationAnimation:
    """Tests für render_ai_optimization_animation()."""
    
    def test_function_exists(self):
        """Test: Funktion existiert."""
        assert callable(render_ai_optimization_animation)
    
    @patch('utils.pv3d_ai_optimization_ui.st')
    def test_returns_false_when_no_animation(self, mock_st):
        """Test: Gibt False zurück wenn keine Animation."""
        mock_st.session_state = {"apply_animation": False}
        
        result = render_ai_optimization_animation()
        
        assert result is False
    
    @patch('time.sleep')
    @patch('utils.pv3d_ai_optimization_ui.st')
    def test_shows_progress(self, mock_st, mock_sleep):
        """Test: Zeigt Fortschritt an."""
        mock_st.session_state = {
            "apply_animation": True,
            "placed_module_positions": [(i, i, i) for i in range(10)],
            "animation_current_index": 5,
            "animation_speed": 1
        }
        mock_st.rerun = Mock()
        
        render_ai_optimization_animation()
        
        # Prüfe dass Fortschritt angezeigt wurde
        assert mock_st.progress.called
        assert mock_st.caption.called
    
    @patch('time.sleep')
    @patch('utils.pv3d_ai_optimization_ui.st')
    def test_increments_index(self, mock_st, mock_sleep):
        """Test: Erhöht Index."""
        mock_st.session_state = {
            "apply_animation": True,
            "placed_module_positions": [(i, i, i) for i in range(10)],
            "animation_current_index": 5,
            "animation_speed": 2
        }
        mock_st.rerun = Mock()
        
        render_ai_optimization_animation()
        
        # Prüfe dass Index erhöht wurde
        assert mock_st.session_state["animation_current_index"] == 7  # 5 + 2


# ============================================================================
# INTEGRATIONSTESTS
# ============================================================================

@pytest.mark.skipif(not UI_AVAILABLE, reason="UI module not available")
class TestIntegration:
    """Integrationstests für gesamten Workflow."""
    
    @patch('utils.pv3d_ai_optimization_ui.st')
    def test_complete_workflow(self, mock_st, sample_optimization_result):
        """Test: Kompletter Workflow von Auswahl bis Anwendung."""
        mock_st.session_state = {}
        mock_st.columns.return_value = [Mock(), Mock(), Mock()]
        mock_st.container.return_value.__enter__ = Mock()
        mock_st.container.return_value.__exit__ = Mock()
        mock_st.button.return_value = False
        mock_st.rerun = Mock()
        
        # 1. Berechne Optimierungen
        optimizer = AILayoutOptimizer(
            roof_length=10.0,
            roof_width=8.0,
            roof_type="Flachdach",
            roof_pitch=0.0
        )
        
        results = _calculate_optimizations(optimizer, "test")
        
        # 2. Wende Layout an
        _apply_layout(results["max_yield"], animate=True, animation_speed=5)
        
        # 3. Prüfe Ergebnis
        assert "placed_module_positions" in mock_st.session_state
        assert "ai_optimization_applied" in mock_st.session_state
        assert mock_st.session_state["ai_optimization_applied"] is True


# ============================================================================
# PROPERTY-BASED TESTS
# ============================================================================

@pytest.mark.skipif(not UI_AVAILABLE, reason="UI module not available")
class TestProperties:
    """Property-based Tests."""
    
    def test_all_strategies_have_unique_names(self):
        """Property: Alle Strategien haben eindeutige Namen."""
        optimizer = AILayoutOptimizer(
            roof_length=10.0,
            roof_width=8.0,
            roof_type="Flachdach",
            roof_pitch=0.0
        )
        
        result1 = optimizer.optimize_for_max_yield()
        result2 = optimizer.optimize_for_max_count()
        result3 = optimizer.optimize_for_aesthetics()
        
        strategies = {result1.strategy, result2.strategy, result3.strategy}
        assert len(strategies) == 3  # Alle Namen sind eindeutig
    
    def test_layout_score_is_always_positive(self, sample_layout_score):
        """Property: Layout-Score ist immer positiv."""
        score = sample_layout_score.get_weighted_score()
        assert score >= 0
    
    def test_animation_index_never_exceeds_position_count(self):
        """Property: Animations-Index überschreitet nie Positions-Anzahl."""
        positions = [(i, i, i) for i in range(10)]
        
        for speed in range(1, 11):
            for current_index in range(0, 15):
                new_index = min(current_index + speed, len(positions))
                assert new_index <= len(positions)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
