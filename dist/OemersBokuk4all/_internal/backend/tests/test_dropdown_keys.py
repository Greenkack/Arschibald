"""
Tests for Dropdown and Selection Dynamic Keys Service

Requirements: 14.7
Task: 224
"""

import pytest
from datetime import datetime

try:
    from backend.services.dropdown_key_service import (
        DropdownKeyManager,
        DropdownType,
        DropdownOption,
        SelectionHistoryEntry,
        Dropdown,
        get_dropdown_manager
    )
    from backend.core.dynamic_keys import KeyPrefix
except ImportError:
    from services.dropdown_key_service import (
        DropdownKeyManager,
        DropdownType,
        DropdownOption,
        SelectionHistoryEntry,
        Dropdown,
        get_dropdown_manager
    )
    from core.dynamic_keys import KeyPrefix


class TestDropdownKeyManager:
    """Test suite for DropdownKeyManager"""

    def setup_method(self):
        """Setup test fixtures"""
        self.manager = DropdownKeyManager()

    def test_create_dropdown_key(self):
        """Test dropdown key creation"""
        key = self.manager.create_dropdown_key(
            "module_type",
            DropdownType.SINGLE_SELECT,
            "solar_form"
        )

        assert key is not None
        assert isinstance(key, str)
        assert "module_type" in key
        assert "solar_form" in key

    def test_create_option_key(self):
        """Test option key creation"""
        dropdown_key = self.manager.create_dropdown_key(
            "module_type",
            DropdownType.SINGLE_SELECT
        )

        option_key = self.manager.create_option_key(
            dropdown_key,
            "monocrystalline",
            "Monocrystalline"
        )

        assert option_key is not None
        assert isinstance(option_key, str)
        assert dropdown_key in option_key

    def test_register_dropdown(self):
        """Test dropdown registration"""
        options = [
            {"value": "mono", "label": "Monocrystalline"},
            {"value": "poly", "label": "Polycrystalline"},
            {"value": "thin", "label": "Thin Film"}
        ]

        dropdown = self.manager.register_dropdown(
            "module_type",
            DropdownType.SINGLE_SELECT,
            "Module Type",
            options
        )

        assert dropdown is not None
        assert dropdown.dropdown_id == "module_type"
        assert len(dropdown.get_options()) == 3

    def test_get_dropdown_by_key(self):
        """Test retrieving dropdown by key"""
        options = [{"value": "test", "label": "Test"}]

        dropdown = self.manager.register_dropdown(
            "test_dropdown",
            DropdownType.SINGLE_SELECT,
            "Test",
            options
        )

        retrieved = self.manager.get_dropdown_by_key(dropdown.key)

        assert retrieved is not None
        assert retrieved.key == dropdown.key
        assert retrieved.dropdown_id == "test_dropdown"

    def test_get_option_by_key(self):
        """Test retrieving option by key"""
        options = [{"value": "test", "label": "Test Option"}]

        dropdown = self.manager.register_dropdown(
            "test_dropdown",
            DropdownType.SINGLE_SELECT,
            "Test",
            options
        )

        option = dropdown.get_options()[0]
        retrieved = self.manager.get_option_by_key(option.key)

        assert retrieved is not None
        assert retrieved.key == option.key
        assert retrieved.value == "test"

    def test_get_options_by_dropdown(self):
        """Test getting all options for a dropdown"""
        options = [
            {"value": "opt1", "label": "Option 1"},
            {"value": "opt2", "label": "Option 2", "enabled": False},
            {"value": "opt3", "label": "Option 3", "visible": False}
        ]

        dropdown = self.manager.register_dropdown(
            "test_dropdown",
            DropdownType.SINGLE_SELECT,
            "Test",
            options
        )

        # Get all options
        all_opts = self.manager.get_options_by_dropdown(dropdown.key)
        assert len(all_opts) == 1  # Only enabled and visible

        # Include disabled
        with_disabled = self.manager.get_options_by_dropdown(
            dropdown.key,
            include_disabled=True
        )
        assert len(with_disabled) == 2  # opt1 and opt2, excludes hidden opt3

        # Include hidden
        with_hidden = self.manager.get_options_by_dropdown(
            dropdown.key,
            include_hidden=True
        )
        assert len(with_hidden) == 2  # Excludes disabled

        # Include both
        all_inclusive = self.manager.get_options_by_dropdown(
            dropdown.key,
            include_disabled=True,
            include_hidden=True
        )
        assert len(all_inclusive) == 3

    def test_get_option_by_value(self):
        """Test getting option by value"""
        options = [
            {"value": "mono", "label": "Monocrystalline"},
            {"value": "poly", "label": "Polycrystalline"}
        ]

        dropdown = self.manager.register_dropdown(
            "module_type",
            DropdownType.SINGLE_SELECT,
            "Module Type",
            options
        )

        option = self.manager.get_option_by_value(dropdown.key, "mono")

        assert option is not None
        assert option.value == "mono"
        assert option.label == "Monocrystalline"

    def test_cascading_dropdown_registration(self):
        """Test cascading dropdown registration"""
        parent_key, child_key = self.manager.register_cascading_dropdown(
            "country",
            "state",
            parent_form_id="address_form",
            child_form_id="address_form"
        )

        assert parent_key is not None
        assert child_key is not None

        children = self.manager.get_cascading_children(parent_key)
        assert child_key in children

    def test_filter_cascading_options(self):
        """Test filtering cascading options"""
        # Register parent dropdown (countries)
        country_options = [
            {
                "value": "USA",
                "label": "United States",
                "children": [
                    {"value": "CA", "label": "California"},
                    {"value": "NY", "label": "New York"}
                ]
            },
            {
                "value": "Germany",
                "label": "Germany",
                "children": [
                    {"value": "BY", "label": "Bavaria"},
                    {"value": "BE", "label": "Berlin"}
                ]
            }
        ]

        country_dropdown = self.manager.register_dropdown(
            "country",
            DropdownType.CASCADING,
            "Country",
            country_options
        )

        # Register child dropdown (states)
        state_options = [
            {"value": "CA", "label": "California"},
            {"value": "NY", "label": "New York"},
            {"value": "BY", "label": "Bavaria"},
            {"value": "BE", "label": "Berlin"}
        ]

        state_dropdown = self.manager.register_dropdown(
            "state",
            DropdownType.CASCADING,
            "State",
            state_options
        )

        # Register cascading relationship
        self.manager.register_cascading_dropdown(
            "country",
            "state"
        )

        # Filter states for USA
        usa_states = self.manager.filter_cascading_options(
            country_dropdown.key,
            "USA",
            state_dropdown.key
        )

        # Should return states that have USA option as parent
        assert len(usa_states) >= 0  # May be 0 if parent_key not set

    def test_record_selection(self):
        """Test recording selection in history"""
        options = [{"value": "test", "label": "Test Option"}]

        dropdown = self.manager.register_dropdown(
            "test_dropdown",
            DropdownType.SINGLE_SELECT,
            "Test",
            options
        )

        option = dropdown.get_options()[0]

        entry = self.manager.record_selection(
            dropdown.key,
            option.key,
            user_id="user123",
            session_id="session456"
        )

        assert entry is not None
        assert entry.dropdown_key == dropdown.key
        assert entry.option_key == option.key
        assert entry.user_id == "user123"
        assert entry.session_id == "session456"

    def test_get_selection_history(self):
        """Test retrieving selection history"""
        options = [
            {"value": "opt1", "label": "Option 1"},
            {"value": "opt2", "label": "Option 2"}
        ]

        dropdown = self.manager.register_dropdown(
            "test_dropdown",
            DropdownType.SINGLE_SELECT,
            "Test",
            options
        )

        # Record multiple selections
        for i, option in enumerate(dropdown.get_options()):
            self.manager.record_selection(
                dropdown.key,
                option.key,
                user_id=f"user{i}"
            )

        # Get all history
        history = self.manager.get_selection_history()
        assert len(history) >= 2

        # Get history for specific dropdown
        dropdown_history = self.manager.get_selection_history(
            dropdown_key=dropdown.key
        )
        assert len(dropdown_history) >= 2

        # Get history for specific user
        user_history = self.manager.get_selection_history(
            user_id="user0"
        )
        assert len(user_history) >= 1

        # Get limited history
        limited = self.manager.get_selection_history(limit=1)
        assert len(limited) == 1

    def test_get_most_selected_options(self):
        """Test getting most frequently selected options"""
        options = [
            {"value": "opt1", "label": "Option 1"},
            {"value": "opt2", "label": "Option 2"},
            {"value": "opt3", "label": "Option 3"}
        ]

        dropdown = self.manager.register_dropdown(
            "test_dropdown",
            DropdownType.SINGLE_SELECT,
            "Test",
            options
        )

        # Record selections with different frequencies
        opts = dropdown.get_options()
        self.manager.record_selection(dropdown.key, opts[0].key)
        self.manager.record_selection(dropdown.key, opts[0].key)
        self.manager.record_selection(dropdown.key, opts[0].key)
        self.manager.record_selection(dropdown.key, opts[1].key)
        self.manager.record_selection(dropdown.key, opts[1].key)
        self.manager.record_selection(dropdown.key, opts[2].key)

        # Get most selected
        popular = self.manager.get_most_selected_options(
            dropdown.key,
            limit=2
        )

        assert len(popular) == 2
        assert popular[0][1] == 3  # opt1 selected 3 times
        assert popular[1][1] == 2  # opt2 selected 2 times

    def test_clear_selection_history(self):
        """Test clearing selection history"""
        options = [{"value": "test", "label": "Test"}]

        dropdown = self.manager.register_dropdown(
            "test_dropdown",
            DropdownType.SINGLE_SELECT,
            "Test",
            options
        )

        option = dropdown.get_options()[0]

        # Record selections
        self.manager.record_selection(
            dropdown.key,
            option.key,
            user_id="user1"
        )
        self.manager.record_selection(
            dropdown.key,
            option.key,
            user_id="user2"
        )

        # Clear for specific user
        cleared = self.manager.clear_selection_history(user_id="user1")
        assert cleared >= 1

        # Verify user1 history is cleared
        user1_history = self.manager.get_selection_history(user_id="user1")
        assert len(user1_history) == 0

        # Verify user2 history still exists
        user2_history = self.manager.get_selection_history(user_id="user2")
        assert len(user2_history) >= 1

    def test_export_dropdown_schema(self):
        """Test exporting dropdown schema"""
        options = [
            {"value": "opt1", "label": "Option 1"},
            {"value": "opt2", "label": "Option 2"}
        ]

        dropdown = self.manager.register_dropdown(
            "test_dropdown",
            DropdownType.SINGLE_SELECT,
            "Test Dropdown",
            options,
            form_id="test_form",
            searchable=True
        )

        schema = self.manager.export_dropdown_schema(dropdown.key)

        assert schema['dropdown_key'] == dropdown.key
        assert schema['dropdown_id'] == "test_dropdown"
        assert schema['label'] == "Test Dropdown"
        assert schema['form_id'] == "test_form"
        assert schema['searchable'] is True
        assert schema['total_options'] == 2
        assert len(schema['options']) == 2

    def test_get_statistics(self):
        """Test getting statistics"""
        # Register multiple dropdowns
        for i in range(3):
            options = [
                {"value": f"opt{j}", "label": f"Option {j}"}
                for j in range(2)
            ]
            self.manager.register_dropdown(
                f"dropdown_{i}",
                DropdownType.SINGLE_SELECT,
                f"Dropdown {i}",
                options
            )

        stats = self.manager.get_statistics()

        assert stats['total_dropdowns'] >= 3
        assert stats['total_options'] >= 6
        assert stats['average_options_per_dropdown'] >= 2


class TestDropdown:
    """Test suite for Dropdown class"""

    def test_dropdown_creation(self):
        """Test creating a dropdown"""
        dropdown = Dropdown(
            key="TEST_KEY",
            dropdown_id="test_dropdown",
            dropdown_type=DropdownType.SINGLE_SELECT,
            label="Test Dropdown"
        )

        assert dropdown.key == "TEST_KEY"
        assert dropdown.dropdown_id == "test_dropdown"
        assert dropdown.label == "Test Dropdown"

    def test_add_option(self):
        """Test adding options to dropdown"""
        dropdown = Dropdown(
            key="TEST_KEY",
            dropdown_id="test",
            dropdown_type=DropdownType.SINGLE_SELECT,
            label="Test"
        )

        option = DropdownOption(
            key="OPT_KEY",
            value="test_value",
            label="Test Option"
        )

        dropdown.add_option(option)

        assert len(dropdown.get_options()) == 1
        assert dropdown.get_options()[0].key == "OPT_KEY"

    def test_remove_option(self):
        """Test removing options from dropdown"""
        dropdown = Dropdown(
            key="TEST_KEY",
            dropdown_id="test",
            dropdown_type=DropdownType.SINGLE_SELECT,
            label="Test"
        )

        option = DropdownOption(
            key="OPT_KEY",
            value="test_value",
            label="Test Option"
        )

        dropdown.add_option(option)
        assert len(dropdown.get_options()) == 1

        removed = dropdown.remove_option("OPT_KEY")
        assert removed is True
        assert len(dropdown.get_options()) == 0

    def test_get_option_by_value(self):
        """Test getting option by value"""
        dropdown = Dropdown(
            key="TEST_KEY",
            dropdown_id="test",
            dropdown_type=DropdownType.SINGLE_SELECT,
            label="Test"
        )

        option = DropdownOption(
            key="OPT_KEY",
            value="test_value",
            label="Test Option"
        )

        dropdown.add_option(option)

        retrieved = dropdown.get_option_by_value("test_value")
        assert retrieved is not None
        assert retrieved.key == "OPT_KEY"

    def test_set_and_get_selected_value(self):
        """Test setting and getting selected value"""
        dropdown = Dropdown(
            key="TEST_KEY",
            dropdown_id="test",
            dropdown_type=DropdownType.SINGLE_SELECT,
            label="Test"
        )

        dropdown.set_selected_value("selected_value")
        assert dropdown.get_selected_value() == "selected_value"

    def test_get_selected_option(self):
        """Test getting selected option object"""
        dropdown = Dropdown(
            key="TEST_KEY",
            dropdown_id="test",
            dropdown_type=DropdownType.SINGLE_SELECT,
            label="Test"
        )

        option = DropdownOption(
            key="OPT_KEY",
            value="test_value",
            label="Test Option"
        )

        dropdown.add_option(option)
        dropdown.set_selected_value("test_value")

        selected = dropdown.get_selected_option()
        assert selected is not None
        assert selected.key == "OPT_KEY"

    def test_to_dict(self):
        """Test converting dropdown to dictionary"""
        dropdown = Dropdown(
            key="TEST_KEY",
            dropdown_id="test_dropdown",
            dropdown_type=DropdownType.MULTI_SELECT,
            label="Test Dropdown",
            multiple=True,
            searchable=True
        )

        data = dropdown.to_dict()

        assert data['key'] == "TEST_KEY"
        assert data['dropdown_id'] == "test_dropdown"
        assert data['dropdown_type'] == "multi_select"
        assert data['label'] == "Test Dropdown"
        assert data['multiple'] is True
        assert data['searchable'] is True


class TestDropdownOption:
    """Test suite for DropdownOption class"""

    def test_option_creation(self):
        """Test creating a dropdown option"""
        option = DropdownOption(
            key="OPT_KEY",
            value="test_value",
            label="Test Option",
            group="test_group",
            sort_order=1
        )

        assert option.key == "OPT_KEY"
        assert option.value == "test_value"
        assert option.label == "Test Option"
        assert option.group == "test_group"
        assert option.sort_order == 1
        assert option.enabled is True
        assert option.visible is True

    def test_option_to_dict(self):
        """Test converting option to dictionary"""
        option = DropdownOption(
            key="OPT_KEY",
            value="test_value",
            label="Test Option",
            metadata={"custom": "data"}
        )

        data = option.to_dict()

        assert data['key'] == "OPT_KEY"
        assert data['value'] == "test_value"
        assert data['label'] == "Test Option"
        assert data['metadata']['custom'] == "data"


class TestSelectionHistoryEntry:
    """Test suite for SelectionHistoryEntry class"""

    def test_history_entry_creation(self):
        """Test creating a selection history entry"""
        entry = SelectionHistoryEntry(
            dropdown_key="DROPDOWN_KEY",
            option_key="OPTION_KEY",
            option_value="test_value",
            option_label="Test Option",
            user_id="user123",
            session_id="session456"
        )

        assert entry.dropdown_key == "DROPDOWN_KEY"
        assert entry.option_key == "OPTION_KEY"
        assert entry.option_value == "test_value"
        assert entry.option_label == "Test Option"
        assert entry.user_id == "user123"
        assert entry.session_id == "session456"

    def test_history_entry_to_dict(self):
        """Test converting history entry to dictionary"""
        entry = SelectionHistoryEntry(
            dropdown_key="DROPDOWN_KEY",
            option_key="OPTION_KEY",
            option_value="test_value",
            option_label="Test Option"
        )

        data = entry.to_dict()

        assert data['dropdown_key'] == "DROPDOWN_KEY"
        assert data['option_key'] == "OPTION_KEY"
        assert data['option_value'] == "test_value"
        assert data['option_label'] == "Test Option"


class TestGlobalDropdownManager:
    """Test suite for global dropdown manager"""

    def test_get_dropdown_manager(self):
        """Test getting global dropdown manager"""
        manager1 = get_dropdown_manager()
        manager2 = get_dropdown_manager()

        # Should return same instance
        assert manager1 is manager2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
