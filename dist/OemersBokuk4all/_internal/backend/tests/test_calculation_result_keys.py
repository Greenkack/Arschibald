"""
Tests for Calculation Results Dynamic Keys Service

Requirements: 14.7
Task: 225
"""

import pytest
from datetime import datetime
import json

try:
    from backend.services.calculation_result_key_service import (
        CalculationResultKeyManager,
        CalculationType,
        CalculationResult,
        CalculationResultVersion,
        CalculationComparison,
        get_calculation_result_manager
    )
    from backend.core.dynamic_keys import KeyPrefix
except ImportError:
    from services.calculation_result_key_service import (
        CalculationResultKeyManager,
        CalculationType,
        CalculationResult,
        CalculationResultVersion,
        CalculationComparison,
        get_calculation_result_manager
    )
    from core.dynamic_keys import KeyPrefix


@pytest.fixture
def manager():
    """Create a fresh manager for each test"""
    return CalculationResultKeyManager()


@pytest.fixture
def sample_solar_data():
    """Sample solar calculation data"""
    return {
        'system_size': 10.5,
        'module_count': 30,
        'annual_production': 12000,
        'self_consumption_rate': 0.35,
        'payback_period': 8.5,
        'total_cost': 15000,
        'savings_25_years': 45000,
        'co2_savings': 180000
    }


@pytest.fixture
def sample_heatpump_data():
    """Sample heat pump calculation data"""
    return {
        'heat_pump_size': 8.0,
        'cop': 4.2,
        'annual_heating_demand': 15000,
        'annual_electricity_consumption': 3571,
        'annual_cost': 1071,
        'savings_vs_gas': 800,
        'payback_period': 12.5
    }


class TestResultKeyCreation:
    """Test result key creation"""

    def test_create_solar_result_key(self, manager):
        """Test creating a solar calculation result key"""
        key = manager.create_result_key(
            CalculationType.SOLAR,
            project_id="PRJ_123"
        )

        assert key is not None
        assert "SOL_" in key
        assert "PRJ_123" in key

    def test_create_heatpump_result_key(self, manager):
        """Test creating a heat pump result key"""
        key = manager.create_result_key(
            CalculationType.HEATPUMP,
            user_id="USER_456"
        )

        assert key is not None
        assert "HP_" in key
        assert "USER_456" in key

    def test_create_key_with_custom_suffix(self, manager):
        """Test creating key with custom suffix"""
        key = manager.create_result_key(
            CalculationType.SOLAR,
            custom_suffix="test_calc"
        )

        assert key is not None
        assert "test_calc" in key


class TestResultRegistration:
    """Test result registration"""

    def test_register_solar_result(self, manager, sample_solar_data):
        """Test registering a solar calculation result"""
        result = manager.register_calculation_result(
            CalculationType.SOLAR,
            sample_solar_data,
            project_id="PRJ_123"
        )

        assert result is not None
        assert result.key is not None
        assert result.calculation_type == CalculationType.SOLAR
        assert result.data == sample_solar_data
        assert result.project_id == "PRJ_123"

    def test_register_result_creates_version(self, manager, sample_solar_data):
        """Test that registering creates initial version"""
        result = manager.register_calculation_result(
            CalculationType.SOLAR,
            sample_solar_data
        )

        versions = manager.get_versions(result.key)
        assert len(versions) == 1
        assert versions[0].version_number == 1
        assert versions[0].data == sample_solar_data

    def test_get_result_by_key(self, manager, sample_solar_data):
        """Test retrieving result by key"""
        result = manager.register_calculation_result(
            CalculationType.SOLAR,
            sample_solar_data
        )

        retrieved = manager.get_result_by_key(result.key)
        assert retrieved is not None
        assert retrieved.key == result.key
        assert retrieved.data == sample_solar_data


class TestResultVersioning:
    """Test result versioning"""

    def test_create_version(self, manager, sample_solar_data):
        """Test creating a new version"""
        result = manager.register_calculation_result(
            CalculationType.SOLAR,
            sample_solar_data
        )

        # Update data
        updated_data = sample_solar_data.copy()
        updated_data['system_size'] = 12.0

        version = manager.create_version(
            result.key,
            updated_data,
            change_summary="Increased system size"
        )

        assert version is not None
        assert version.version_number == 2
        assert version.data['system_size'] == 12.0
        assert version.change_summary == "Increased system size"

    def test_get_versions(self, manager, sample_solar_data):
        """Test getting all versions"""
        result = manager.register_calculation_result(
            CalculationType.SOLAR,
            sample_solar_data
        )

        # Create additional versions
        for i in range(3):
            updated_data = sample_solar_data.copy()
            updated_data['system_size'] = 10.5 + i
            manager.create_version(result.key, updated_data)

        versions = manager.get_versions(result.key)
        assert len(versions) == 4  # Initial + 3 updates

    def test_get_specific_version(self, manager, sample_solar_data):
        """Test getting a specific version"""
        result = manager.register_calculation_result(
            CalculationType.SOLAR,
            sample_solar_data
        )

        # Create version 2
        updated_data = sample_solar_data.copy()
        updated_data['system_size'] = 12.0
        manager.create_version(result.key, updated_data)

        version = manager.get_version(result.key, 2)
        assert version is not None
        assert version.version_number == 2
        assert version.data['system_size'] == 12.0

    def test_get_latest_version(self, manager, sample_solar_data):
        """Test getting the latest version"""
        result = manager.register_calculation_result(
            CalculationType.SOLAR,
            sample_solar_data
        )

        # Create multiple versions
        for i in range(3):
            updated_data = sample_solar_data.copy()
            updated_data['system_size'] = 10.5 + i
            manager.create_version(result.key, updated_data)

        latest = manager.get_latest_version(result.key)
        assert latest is not None
        assert latest.version_number == 4
        assert latest.data['system_size'] == 12.5

    def test_update_result_creates_version(self, manager, sample_solar_data):
        """Test that updating result creates new version"""
        result = manager.register_calculation_result(
            CalculationType.SOLAR,
            sample_solar_data
        )

        updated_data = sample_solar_data.copy()
        updated_data['system_size'] = 12.0

        success = manager.update_result(
            result.key,
            updated_data,
            change_summary="Updated system size"
        )

        assert success is True
        versions = manager.get_versions(result.key)
        assert len(versions) == 2


class TestResultComparison:
    """Test result comparison"""

    def test_compare_results(
        self,
        manager,
        sample_solar_data,
        sample_heatpump_data
    ):
        """Test comparing two results"""
        result1 = manager.register_calculation_result(
            CalculationType.SOLAR,
            sample_solar_data
        )

        # Create similar but different data
        data2 = sample_solar_data.copy()
        data2['system_size'] = 12.0
        data2['annual_production'] = 14000

        result2 = manager.register_calculation_result(
            CalculationType.SOLAR,
            data2
        )

        comparison = manager.compare_results(result1.key, result2.key)

        assert comparison is not None
        assert comparison.result_key_1 == result1.key
        assert comparison.result_key_2 == result2.key
        assert 'system_size' in comparison.differences
        assert 'annual_production' in comparison.differences

    def test_comparison_similarity_score(self, manager, sample_solar_data):
        """Test similarity score calculation"""
        result1 = manager.register_calculation_result(
            CalculationType.SOLAR,
            sample_solar_data
        )

        # Create identical data
        result2 = manager.register_calculation_result(
            CalculationType.SOLAR,
            sample_solar_data.copy()
        )

        comparison = manager.compare_results(result1.key, result2.key)
        assert comparison.similarity_score == 1.0

        # Create partially different data
        data3 = sample_solar_data.copy()
        data3['system_size'] = 12.0

        result3 = manager.register_calculation_result(
            CalculationType.SOLAR,
            data3
        )

        comparison2 = manager.compare_results(result1.key, result3.key)
        assert 0.0 < comparison2.similarity_score < 1.0

    def test_comparison_change_calculation(self, manager, sample_solar_data):
        """Test change calculation in comparison"""
        result1 = manager.register_calculation_result(
            CalculationType.SOLAR,
            sample_solar_data
        )

        data2 = sample_solar_data.copy()
        data2['system_size'] = 12.0  # 10.5 -> 12.0 = ~14.3% increase

        result2 = manager.register_calculation_result(
            CalculationType.SOLAR,
            data2
        )

        comparison = manager.compare_results(result1.key, result2.key)
        change = comparison.differences['system_size']['change']

        assert isinstance(change, float)
        assert change > 0  # Positive change


class TestResultHistory:
    """Test result history"""

    def test_get_result_history(self, manager, sample_solar_data):
        """Test getting result history"""
        # Register multiple results
        for i in range(3):
            manager.register_calculation_result(
                CalculationType.SOLAR,
                sample_solar_data
            )

        history = manager.get_result_history()
        assert len(history) >= 3

    def test_filter_history_by_type(self, manager, sample_solar_data):
        """Test filtering history by calculation type"""
        manager.register_calculation_result(
            CalculationType.SOLAR,
            sample_solar_data
        )
        manager.register_calculation_result(
            CalculationType.HEATPUMP,
            {'cop': 4.2}
        )

        solar_history = manager.get_result_history(
            calculation_type=CalculationType.SOLAR
        )

        assert len(solar_history) >= 1
        assert all(
            e.get('calculation_type') == CalculationType.SOLAR.value
            for e in solar_history
        )

    def test_history_limit(self, manager, sample_solar_data):
        """Test history limit"""
        # Register multiple results
        for i in range(10):
            manager.register_calculation_result(
                CalculationType.SOLAR,
                sample_solar_data
            )

        history = manager.get_result_history(limit=5)
        assert len(history) == 5


class TestResultExport:
    """Test result export"""

    def test_export_result_json(self, manager, sample_solar_data):
        """Test exporting result as JSON"""
        result = manager.register_calculation_result(
            CalculationType.SOLAR,
            sample_solar_data
        )

        exported = manager.export_result(result.key, format='json')

        assert isinstance(exported, str)
        data = json.loads(exported)
        assert data['key'] == result.key
        assert data['calculation_type'] == CalculationType.SOLAR.value

    def test_export_result_dict(self, manager, sample_solar_data):
        """Test exporting result as dictionary"""
        result = manager.register_calculation_result(
            CalculationType.SOLAR,
            sample_solar_data
        )

        exported = manager.export_result(result.key, format='dict')

        assert isinstance(exported, dict)
        assert exported['key'] == result.key
        assert exported['data'] == sample_solar_data

    def test_export_with_versions(self, manager, sample_solar_data):
        """Test exporting result with versions"""
        result = manager.register_calculation_result(
            CalculationType.SOLAR,
            sample_solar_data
        )

        # Create additional version
        updated_data = sample_solar_data.copy()
        updated_data['system_size'] = 12.0
        manager.create_version(result.key, updated_data)

        exported = manager.export_result(
            result.key,
            format='dict',
            include_versions=True
        )

        assert 'versions' in exported
        assert len(exported['versions']) == 2

    def test_export_with_german_formatting(self, manager, sample_solar_data):
        """Test exporting with German number formatting"""
        result = manager.register_calculation_result(
            CalculationType.SOLAR,
            sample_solar_data
        )

        exported = manager.export_result(
            result.key,
            format='dict',
            apply_german_formatting=True
        )

        # Check that numbers are formatted
        system_size = exported['data']['system_size']
        assert isinstance(system_size, str)
        assert ',' in system_size  # German decimal separator

    def test_export_comparison(self, manager, sample_solar_data):
        """Test exporting comparison"""
        result1 = manager.register_calculation_result(
            CalculationType.SOLAR,
            sample_solar_data
        )

        data2 = sample_solar_data.copy()
        data2['system_size'] = 12.0

        result2 = manager.register_calculation_result(
            CalculationType.SOLAR,
            data2
        )

        comparison = manager.compare_results(result1.key, result2.key)
        exported = manager.export_comparison(
            comparison.comparison_key,
            format='json'
        )

        assert isinstance(exported, str)
        data = json.loads(exported)
        assert 'differences' in data
        assert 'similarity_score' in data


class TestStatistics:
    """Test statistics"""

    def test_get_statistics(self, manager, sample_solar_data):
        """Test getting statistics"""
        # Register multiple results
        manager.register_calculation_result(
            CalculationType.SOLAR,
            sample_solar_data
        )
        manager.register_calculation_result(
            CalculationType.HEATPUMP,
            {'cop': 4.2}
        )

        stats = manager.get_statistics()

        assert stats['total_results'] >= 2
        assert stats['total_versions'] >= 2
        assert 'results_by_type' in stats
        assert CalculationType.SOLAR.value in stats['results_by_type']


class TestGlobalManager:
    """Test global manager instance"""

    def test_get_global_manager(self):
        """Test getting global manager instance"""
        manager = get_calculation_result_manager()
        assert manager is not None
        assert isinstance(manager, CalculationResultKeyManager)

    def test_global_manager_singleton(self):
        """Test that global manager is singleton"""
        manager1 = get_calculation_result_manager()
        manager2 = get_calculation_result_manager()
        assert manager1 is manager2


class TestCalculationResultClass:
    """Test CalculationResult class"""

    def test_create_calculation_result(self, sample_solar_data):
        """Test creating a CalculationResult"""
        result = CalculationResult(
            key="SOL_TEST_123",
            calculation_type=CalculationType.SOLAR,
            data=sample_solar_data,
            project_id="PRJ_123"
        )

        assert result.key == "SOL_TEST_123"
        assert result.calculation_type == CalculationType.SOLAR
        assert result.data == sample_solar_data
        assert result.project_id == "PRJ_123"

    def test_update_data(self, sample_solar_data):
        """Test updating calculation data"""
        result = CalculationResult(
            key="SOL_TEST_123",
            calculation_type=CalculationType.SOLAR,
            data=sample_solar_data
        )

        new_data = {'system_size': 12.0}
        result.update_data(new_data)

        assert result.data == new_data

    def test_get_value(self, sample_solar_data):
        """Test getting specific value"""
        result = CalculationResult(
            key="SOL_TEST_123",
            calculation_type=CalculationType.SOLAR,
            data=sample_solar_data
        )

        system_size = result.get_value('system_size')
        assert system_size == 10.5

        missing = result.get_value('missing_key', default='N/A')
        assert missing == 'N/A'

    def test_set_value(self, sample_solar_data):
        """Test setting specific value"""
        result = CalculationResult(
            key="SOL_TEST_123",
            calculation_type=CalculationType.SOLAR,
            data=sample_solar_data
        )

        result.set_value('system_size', 12.0)
        assert result.data['system_size'] == 12.0

    def test_to_dict(self, sample_solar_data):
        """Test converting to dictionary"""
        result = CalculationResult(
            key="SOL_TEST_123",
            calculation_type=CalculationType.SOLAR,
            data=sample_solar_data,
            metadata={'source': 'test'}
        )

        result_dict = result.to_dict()

        assert result_dict['key'] == "SOL_TEST_123"
        assert result_dict['calculation_type'] == CalculationType.SOLAR.value
        assert result_dict['data'] == sample_solar_data
        assert 'metadata' in result_dict


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
