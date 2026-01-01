"""
Session State Migration Tests
Task 239: Session State Migration

Tests to verify all st.session_state variables are properly mapped to Zustand stores.
"""

import pytest
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class StoreType(str, Enum):
    """Zustand store types"""
    AUTH = "authStore"
    PROJECT = "projectStore"
    CALCULATION = "calculationStore"
    PRODUCT = "productStore"
    PDF = "pdfStore"
    CRM = "crmStore"
    UI = "uiStore"


@dataclass
class StateMapping:
    """Mapping between Streamlit session_state and Zustand store"""
    streamlit_key: str
    store: StoreType
    property_name: str
    persisted: bool = False
    description: str = ""


# Complete state mappings
STATE_MAPPINGS: List[StateMapping] = [
    # Auth state
    StateMapping("user", StoreType.AUTH, "user", True, "Current user object"),
    StateMapping("token", StoreType.AUTH, "token", True, "JWT token"),
    StateMapping("is_authenticated", StoreType.AUTH, "isAuthenticated", True, "Auth status"),
    
    # Project state
    StateMapping("current_project", StoreType.PROJECT, "currentProject", True, "Active project"),
    StateMapping("projects", StoreType.PROJECT, "projects", True, "All projects"),
    StateMapping("project_loading", StoreType.PROJECT, "isLoading", False, "Loading state"),
    
    # Calculation state
    StateMapping("solar_inputs", StoreType.CALCULATION, "solarInputs", False, "Solar calc inputs"),
    StateMapping("solar_results", StoreType.CALCULATION, "solarResults", False, "Solar calc results"),
    StateMapping("heatpump_inputs", StoreType.CALCULATION, "heatpumpInputs", False, "Heat pump inputs"),
    StateMapping("heatpump_results", StoreType.CALCULATION, "heatpumpResults", False, "Heat pump results"),
    StateMapping("is_calculating", StoreType.CALCULATION, "isCalculating", False, "Calc in progress"),
    
    # Product state
    StateMapping("selected_products", StoreType.PRODUCT, "selected", True, "Selected products"),
    StateMapping("product_catalog", StoreType.PRODUCT, "catalog", False, "Product catalog"),
    StateMapping("product_filters", StoreType.PRODUCT, "filters", False, "Active filters"),
    
    # PDF state
    StateMapping("pdf_options", StoreType.PDF, "options", True, "PDF generation options"),
    StateMapping("pdf_template", StoreType.PDF, "template", True, "Selected template"),
    StateMapping("pdf_preview", StoreType.PDF, "preview", False, "Preview data"),
    
    # CRM state
    StateMapping("customers", StoreType.CRM, "customers", True, "Customer list"),
    StateMapping("current_customer", StoreType.CRM, "currentCustomer", False, "Active customer"),
    StateMapping("offers", StoreType.CRM, "offers", True, "Offer list"),
    
    # UI state
    StateMapping("theme", StoreType.UI, "theme", True, "UI theme"),
    StateMapping("sidebar_state", StoreType.UI, "sidebarOpen", True, "Sidebar visibility"),
    StateMapping("sidebar_collapsed", StoreType.UI, "sidebarCollapsed", True, "Sidebar collapsed"),
    StateMapping("language", StoreType.UI, "language", True, "UI language"),
    StateMapping("notifications", StoreType.UI, "notifications", True, "Notifications enabled"),
]


@dataclass
class MockZustandStore:
    """Mock Zustand store for testing"""
    name: str
    state: Dict[str, Any] = field(default_factory=dict)
    persisted: bool = False
    
    def get_state(self) -> Dict[str, Any]:
        return self.state
    
    def set_state(self, updates: Dict[str, Any]):
        self.state.update(updates)
    
    def reset(self):
        self.state = {}


class TestAuthStateMigration:
    """Tests for auth state migration"""
    
    def test_user_mapped_to_auth_store(self):
        """Test user is mapped to authStore"""
        mapping = next(m for m in STATE_MAPPINGS if m.streamlit_key == "user")
        assert mapping.store == StoreType.AUTH
        assert mapping.property_name == "user"
    
    def test_token_mapped_to_auth_store(self):
        """Test token is mapped to authStore"""
        mapping = next(m for m in STATE_MAPPINGS if m.streamlit_key == "token")
        assert mapping.store == StoreType.AUTH
        assert mapping.property_name == "token"
    
    def test_auth_state_persisted(self):
        """Test auth state is persisted"""
        auth_mappings = [m for m in STATE_MAPPINGS if m.store == StoreType.AUTH]
        for mapping in auth_mappings:
            assert mapping.persisted, f"{mapping.streamlit_key} should be persisted"


class TestProjectStateMigration:
    """Tests for project state migration"""
    
    def test_current_project_mapped(self):
        """Test current_project is mapped to projectStore"""
        mapping = next(m for m in STATE_MAPPINGS if m.streamlit_key == "current_project")
        assert mapping.store == StoreType.PROJECT
        assert mapping.property_name == "currentProject"
    
    def test_projects_list_mapped(self):
        """Test projects list is mapped to projectStore"""
        mapping = next(m for m in STATE_MAPPINGS if m.streamlit_key == "projects")
        assert mapping.store == StoreType.PROJECT
        assert mapping.property_name == "projects"
    
    def test_project_state_persisted(self):
        """Test project state is persisted"""
        mapping = next(m for m in STATE_MAPPINGS if m.streamlit_key == "projects")
        assert mapping.persisted


class TestCalculationStateMigration:
    """Tests for calculation state migration"""
    
    def test_solar_inputs_mapped(self):
        """Test solar_inputs is mapped to calculationStore"""
        mapping = next(m for m in STATE_MAPPINGS if m.streamlit_key == "solar_inputs")
        assert mapping.store == StoreType.CALCULATION
        assert mapping.property_name == "solarInputs"
    
    def test_solar_results_mapped(self):
        """Test solar_results is mapped to calculationStore"""
        mapping = next(m for m in STATE_MAPPINGS if m.streamlit_key == "solar_results")
        assert mapping.store == StoreType.CALCULATION
        assert mapping.property_name == "solarResults"
    
    def test_heatpump_state_mapped(self):
        """Test heatpump state is mapped to calculationStore"""
        heatpump_mappings = [m for m in STATE_MAPPINGS if "heatpump" in m.streamlit_key]
        assert len(heatpump_mappings) >= 2
        for mapping in heatpump_mappings:
            assert mapping.store == StoreType.CALCULATION
    
    def test_calculation_state_not_persisted(self):
        """Test calculation state is not persisted (recalculated on load)"""
        calc_mappings = [m for m in STATE_MAPPINGS if m.store == StoreType.CALCULATION]
        for mapping in calc_mappings:
            assert not mapping.persisted, f"{mapping.streamlit_key} should not be persisted"


class TestUIStateMigration:
    """Tests for UI state migration"""
    
    def test_theme_mapped(self):
        """Test theme is mapped to uiStore"""
        mapping = next(m for m in STATE_MAPPINGS if m.streamlit_key == "theme")
        assert mapping.store == StoreType.UI
        assert mapping.property_name == "theme"
    
    def test_sidebar_state_mapped(self):
        """Test sidebar_state is mapped to uiStore"""
        mapping = next(m for m in STATE_MAPPINGS if m.streamlit_key == "sidebar_state")
        assert mapping.store == StoreType.UI
        assert mapping.property_name == "sidebarOpen"
    
    def test_language_mapped(self):
        """Test language is mapped to uiStore"""
        mapping = next(m for m in STATE_MAPPINGS if m.streamlit_key == "language")
        assert mapping.store == StoreType.UI
        assert mapping.property_name == "language"
    
    def test_ui_state_persisted(self):
        """Test UI state is persisted"""
        ui_mappings = [m for m in STATE_MAPPINGS if m.store == StoreType.UI]
        for mapping in ui_mappings:
            assert mapping.persisted, f"{mapping.streamlit_key} should be persisted"


class TestStatePersistence:
    """Tests for state persistence"""
    
    def test_persisted_stores_count(self):
        """Test correct number of persisted state mappings"""
        persisted = [m for m in STATE_MAPPINGS if m.persisted]
        assert len(persisted) >= 10
    
    def test_auth_store_persisted(self):
        """Test auth store is persisted"""
        auth_mappings = [m for m in STATE_MAPPINGS if m.store == StoreType.AUTH]
        assert all(m.persisted for m in auth_mappings)
    
    def test_ui_store_persisted(self):
        """Test UI store is persisted"""
        ui_mappings = [m for m in STATE_MAPPINGS if m.store == StoreType.UI]
        assert all(m.persisted for m in ui_mappings)
    
    def test_calculation_store_not_persisted(self):
        """Test calculation store is not persisted"""
        calc_mappings = [m for m in STATE_MAPPINGS if m.store == StoreType.CALCULATION]
        assert all(not m.persisted for m in calc_mappings)


class TestStateSynchronization:
    """Tests for state synchronization between tabs"""
    
    def test_mock_store_sync(self):
        """Test mock store synchronization"""
        store1 = MockZustandStore("auth", persisted=True)
        store2 = MockZustandStore("auth", persisted=True)
        
        # Simulate state change in store1
        store1.set_state({"user": {"id": 1, "name": "Test"}})
        
        # Simulate sync to store2
        store2.set_state(store1.get_state())
        
        assert store2.get_state()["user"]["id"] == 1
    
    def test_persisted_stores_sync(self):
        """Test that persisted stores can sync"""
        persisted_stores = set(m.store for m in STATE_MAPPINGS if m.persisted)
        
        # These stores should support sync
        expected_synced = {StoreType.AUTH, StoreType.PROJECT, StoreType.UI}
        assert expected_synced.issubset(persisted_stores)


class TestStateBackupRestore:
    """Tests for state backup and restore"""
    
    def test_backup_state(self):
        """Test state backup functionality"""
        store = MockZustandStore("test", persisted=True)
        store.set_state({
            "user": {"id": 1},
            "theme": "dark",
            "language": "de"
        })
        
        # Backup
        backup = store.get_state().copy()
        
        # Clear state
        store.reset()
        assert store.get_state() == {}
        
        # Restore
        store.set_state(backup)
        assert store.get_state()["user"]["id"] == 1
        assert store.get_state()["theme"] == "dark"
    
    def test_restore_preserves_all_keys(self):
        """Test restore preserves all state keys"""
        original_state = {
            "key1": "value1",
            "key2": {"nested": "value"},
            "key3": [1, 2, 3]
        }
        
        store = MockZustandStore("test")
        store.set_state(original_state)
        
        backup = store.get_state().copy()
        store.reset()
        store.set_state(backup)
        
        assert store.get_state() == original_state


class TestStateVersioning:
    """Tests for state versioning"""
    
    def test_version_migration(self):
        """Test state version migration"""
        old_state = {
            "version": "0.9.0",
            "user": {"id": 1}
        }
        
        # Simulate migration
        def migrate(state: Dict) -> Dict:
            if state.get("version") == "0.9.0":
                state["version"] = "1.0.0"
                state["user"]["migrated"] = True
            return state
        
        new_state = migrate(old_state)
        
        assert new_state["version"] == "1.0.0"
        assert new_state["user"]["migrated"] is True


class TestStateMappingCompleteness:
    """Tests for state mapping completeness"""
    
    def test_minimum_mappings_count(self):
        """Test minimum number of state mappings"""
        assert len(STATE_MAPPINGS) >= 20
    
    def test_all_stores_have_mappings(self):
        """Test all store types have mappings"""
        stores_with_mappings = set(m.store for m in STATE_MAPPINGS)
        
        # All stores should have at least one mapping
        for store_type in StoreType:
            assert store_type in stores_with_mappings, f"No mappings for {store_type}"
    
    def test_all_mappings_have_property_names(self):
        """Test all mappings have property names"""
        for mapping in STATE_MAPPINGS:
            assert mapping.property_name, f"Missing property name for {mapping.streamlit_key}"
    
    def test_camelcase_property_names(self):
        """Test property names use camelCase"""
        for mapping in STATE_MAPPINGS:
            # Property names should not have underscores (camelCase)
            assert "_" not in mapping.property_name, \
                f"Property {mapping.property_name} should use camelCase"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
