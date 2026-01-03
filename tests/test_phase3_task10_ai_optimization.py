import pytest
import math
from utils.pv3d_ai_optimization import AILayoutOptimizer, LayoutScore, OptimizationResult

@pytest.fixture
def flat_roof_optimizer():
    return AILayoutOptimizer(
        roof_length=10.0, roof_width=8.0, roof_type="Flachdach", roof_pitch=0.0,
        module_width=1.05, module_height=1.76, module_power_w=400.0,
        module_cost_eur=200.0, electricity_price_eur_kwh=0.30
    )

def test_layout_score_creation():
    score = LayoutScore(
        total_yield_kwh=5000.0, module_count=15, aesthetic_score=75.0,
        cost_eur=3000.0, roi_years=8.5, coverage_percent=60.0, symmetry_score=80.0
    )
    assert score.total_yield_kwh == 5000.0

def test_optimizer_initialization(flat_roof_optimizer):
    assert flat_roof_optimizer.roof_length == 10.0

def test_optimize_for_max_yield_basic(flat_roof_optimizer):
    result = flat_roof_optimizer.optimize_for_max_yield()
    assert isinstance(result, OptimizationResult)
    assert len(result.positions) > 0

def test_optimize_for_max_count_basic(flat_roof_optimizer):
    result = flat_roof_optimizer.optimize_for_max_count()
    assert isinstance(result, OptimizationResult)
    assert len(result.positions) > 0

def test_optimize_for_aesthetics_basic(flat_roof_optimizer):
    result = flat_roof_optimizer.optimize_for_aesthetics()
    assert isinstance(result, OptimizationResult)
    assert len(result.positions) > 0
