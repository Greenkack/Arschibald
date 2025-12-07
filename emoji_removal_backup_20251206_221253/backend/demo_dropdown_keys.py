"""
Demo: Dropdown and Selection Dynamic Keys

This demo showcases the comprehensive dropdown key management system
including cascading dropdowns and selection history.

Requirements: 14.7
Task: 224
"""

try:
    from backend.services.dropdown_key_service import (
        DropdownKeyManager,
        DropdownType,
        get_dropdown_manager
    )
except ImportError:
    from services.dropdown_key_service import (
        DropdownKeyManager,
        DropdownType,
        get_dropdown_manager
    )


def demo_basic_dropdown():
    """Demo: Basic dropdown with dynamic keys"""
    print("\n" + "=" * 60)
    print("DEMO 1: Basic Dropdown with Dynamic Keys")
    print("=" * 60)

    manager = DropdownKeyManager()

    # Register a simple dropdown
    module_options = [
        {"value": "mono", "label": "Monocrystalline", "sort_order": 1},
        {"value": "poly", "label": "Polycrystalline", "sort_order": 2},
        {"value": "thin", "label": "Thin Film", "sort_order": 3}
    ]

    dropdown = manager.register_dropdown(
        dropdown_id="module_type",
        dropdown_type=DropdownType.SINGLE_SELECT,
        label="Solar Module Type",
        options=module_options,
        form_id="solar_calculator_form",
        searchable=True
    )

    print(f"\n✓ Created dropdown: {dropdown.label}")
    print(f"  Key: {dropdown.key}")
    print(f"  Type: {dropdown.dropdown_type.value}")
    print(f"  Options: {len(dropdown.get_options())}")

    print("\n  Available Options:")
    for option in dropdown.get_options():
        print(f"    - {option.label} (value: {option.value})")
        print(f"      Key: {option.key}")


def demo_grouped_dropdown():
    """Demo: Grouped dropdown options"""
    print("\n" + "=" * 60)
    print("DEMO 2: Grouped Dropdown Options")
    print("=" * 60)

    manager = DropdownKeyManager()

    # Register dropdown with grouped options
    product_options = [
        {
            "value": "trina_400",
            "label": "Trina Solar 400W",
            "group": "Premium"
        },
        {
            "value": "trina_350",
            "label": "Trina Solar 350W",
            "group": "Standard"
        },
        {
            "value": "jinko_420",
            "label": "JinkoSolar 420W",
            "group": "Premium"
        },
        {
            "value": "jinko_380",
            "label": "JinkoSolar 380W",
            "group": "Standard"
        }
    ]

    dropdown = manager.register_dropdown(
        dropdown_id="solar_module",
        dropdown_type=DropdownType.GROUPED,
        label="Solar Module Selection",
        options=product_options
    )

    print(f"\n✓ Created grouped dropdown: {dropdown.label}")

    # Group options by group
    groups = {}
    for option in dropdown.get_options():
        group = option.group or "Ungrouped"
        if group not in groups:
            groups[group] = []
        groups[group].append(option)

    print("\n  Options by Group:")
    for group_name, options in groups.items():
        print(f"\n    {group_name}:")
        for option in options:
            print(f"      - {option.label}")
            print(f"        Key: {option.key}")


def demo_cascading_dropdown():
    """Demo: Cascading dropdown with parent-child relationship"""
    print("\n" + "=" * 60)
    print("DEMO 3: Cascading Dropdown")
    print("=" * 60)

    manager = DropdownKeyManager()

    # Register country dropdown with nested states
    country_options = [
        {
            "value": "USA",
            "label": "United States",
            "children": [
                {"value": "CA", "label": "California"},
                {"value": "NY", "label": "New York"},
                {"value": "TX", "label": "Texas"}
            ]
        },
        {
            "value": "Germany",
            "label": "Germany",
            "children": [
                {"value": "BY", "label": "Bavaria"},
                {"value": "BE", "label": "Berlin"},
                {"value": "HH", "label": "Hamburg"}
            ]
        }
    ]

    country_dropdown = manager.register_dropdown(
        dropdown_id="country",
        dropdown_type=DropdownType.CASCADING,
        label="Country",
        options=country_options,
        form_id="address_form"
    )

    print(f"\n✓ Created cascading dropdown: {country_dropdown.label}")
    print(f"  Key: {country_dropdown.key}")

    print("\n  Countries and States:")
    for country_opt in country_dropdown.get_options():
        print(f"\n    {country_opt.label}:")
        print(f"      Key: {country_opt.key}")

        # Get child options
        if country_opt.children_keys:
            print(f"      States ({len(country_opt.children_keys)}):")
            for child_key in country_opt.children_keys:
                child_opt = manager.get_option_by_key(child_key)
                if child_opt:
                    print(f"        - {child_opt.label}")
                    print(f"          Key: {child_opt.key}")


def demo_selection_history():
    """Demo: Selection history tracking"""
    print("\n" + "=" * 60)
    print("DEMO 4: Selection History Tracking")
    print("=" * 60)

    manager = DropdownKeyManager()

    # Register dropdown
    options = [
        {"value": "mono", "label": "Monocrystalline"},
        {"value": "poly", "label": "Polycrystalline"},
        {"value": "thin", "label": "Thin Film"}
    ]

    dropdown = manager.register_dropdown(
        dropdown_id="module_type",
        dropdown_type=DropdownType.SINGLE_SELECT,
        label="Module Type",
        options=options
    )

    print(f"\n✓ Created dropdown: {dropdown.label}")

    # Simulate user selections
    print("\n  Recording selections...")
    selections = [
        ("mono", "user1", "session1"),
        ("mono", "user2", "session2"),
        ("poly", "user1", "session1"),
        ("mono", "user3", "session3"),
        ("thin", "user2", "session2")
    ]

    for value, user_id, session_id in selections:
        option = manager.get_option_by_value(dropdown.key, value)
        if option:
            manager.record_selection(
                dropdown.key,
                option.key,
                user_id=user_id,
                session_id=session_id
            )
            print(f"    - {user_id} selected {option.label}")

    # Get selection history
    print("\n  Selection History (all):")
    history = manager.get_selection_history(limit=10)
    for entry in history:
        print(f"    - {entry.option_label} by {entry.user_id}")
        print(f"      at {entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

    # Get most selected options
    print("\n  Most Popular Options:")
    popular = manager.get_most_selected_options(dropdown.key, limit=3)
    for option, count in popular:
        print(f"    - {option.label}: {count} selections")


def demo_multi_select_dropdown():
    """Demo: Multi-select dropdown"""
    print("\n" + "=" * 60)
    print("DEMO 5: Multi-Select Dropdown")
    print("=" * 60)

    manager = DropdownKeyManager()

    # Register multi-select dropdown
    feature_options = [
        {"value": "monitoring", "label": "Real-time Monitoring"},
        {"value": "optimizer", "label": "Power Optimizers"},
        {"value": "battery", "label": "Battery Storage"},
        {"value": "smart_meter", "label": "Smart Meter"},
        {"value": "ev_charger", "label": "EV Charger Integration"}
    ]

    dropdown = manager.register_dropdown(
        dropdown_id="system_features",
        dropdown_type=DropdownType.MULTI_SELECT,
        label="System Features",
        options=feature_options,
        multiple=True
    )

    print(f"\n✓ Created multi-select dropdown: {dropdown.label}")
    print(f"  Key: {dropdown.key}")
    print(f"  Multiple selection: {dropdown.multiple}")

    print("\n  Available Features:")
    for option in dropdown.get_options():
        print(f"    - {option.label}")
        print(f"      Key: {option.key}")


def demo_searchable_dropdown():
    """Demo: Searchable dropdown with many options"""
    print("\n" + "=" * 60)
    print("DEMO 6: Searchable Dropdown")
    print("=" * 60)

    manager = DropdownKeyManager()

    # Register searchable dropdown with many options
    city_options = [
        {"value": "berlin", "label": "Berlin"},
        {"value": "munich", "label": "Munich"},
        {"value": "hamburg", "label": "Hamburg"},
        {"value": "cologne", "label": "Cologne"},
        {"value": "frankfurt", "label": "Frankfurt"},
        {"value": "stuttgart", "label": "Stuttgart"},
        {"value": "dusseldorf", "label": "Düsseldorf"},
        {"value": "dortmund", "label": "Dortmund"},
        {"value": "essen", "label": "Essen"},
        {"value": "leipzig", "label": "Leipzig"}
    ]

    dropdown = manager.register_dropdown(
        dropdown_id="city",
        dropdown_type=DropdownType.SEARCHABLE,
        label="City Selection",
        options=city_options,
        searchable=True
    )

    print(f"\n✓ Created searchable dropdown: {dropdown.label}")
    print(f"  Key: {dropdown.key}")
    print(f"  Searchable: {dropdown.searchable}")
    print(f"  Total options: {len(dropdown.get_options())}")

    print("\n  Sample Options:")
    for option in dropdown.get_options()[:5]:
        print(f"    - {option.label}")


def demo_dropdown_schema_export():
    """Demo: Export dropdown schema"""
    print("\n" + "=" * 60)
    print("DEMO 7: Dropdown Schema Export")
    print("=" * 60)

    manager = DropdownKeyManager()

    # Register dropdown
    options = [
        {"value": "opt1", "label": "Option 1", "metadata": {"price": 100}},
        {"value": "opt2", "label": "Option 2", "metadata": {"price": 200}}
    ]

    dropdown = manager.register_dropdown(
        dropdown_id="test_dropdown",
        dropdown_type=DropdownType.SINGLE_SELECT,
        label="Test Dropdown",
        options=options,
        form_id="test_form",
        searchable=True,
        metadata={"category": "test"}
    )

    print(f"\n✓ Created dropdown: {dropdown.label}")

    # Export schema
    schema = manager.export_dropdown_schema(dropdown.key)

    print("\n  Exported Schema:")
    print(f"    Dropdown ID: {schema['dropdown_id']}")
    print(f"    Label: {schema['label']}")
    print(f"    Type: {schema['dropdown_type']}")
    print(f"    Form ID: {schema['form_id']}")
    print(f"    Searchable: {schema['searchable']}")
    print(f"    Total Options: {schema['total_options']}")

    print("\n    Options:")
    for opt in schema['options']:
        print(f"      - {opt['label']} (value: {opt['value']})")
        if opt['metadata']:
            print(f"        Metadata: {opt['metadata']}")


def demo_statistics():
    """Demo: Get statistics about dropdowns"""
    print("\n" + "=" * 60)
    print("DEMO 8: Dropdown Statistics")
    print("=" * 60)

    manager = DropdownKeyManager()

    # Register multiple dropdowns
    dropdowns_data = [
        ("module_type", DropdownType.SINGLE_SELECT, 3),
        ("inverter_type", DropdownType.SINGLE_SELECT, 4),
        ("country", DropdownType.CASCADING, 5),
        ("features", DropdownType.MULTI_SELECT, 6)
    ]

    for dropdown_id, dtype, num_options in dropdowns_data:
        options = [
            {"value": f"opt{i}", "label": f"Option {i}"}
            for i in range(num_options)
        ]
        manager.register_dropdown(
            dropdown_id,
            dtype,
            dropdown_id.replace("_", " ").title(),
            options
        )

    # Get statistics
    stats = manager.get_statistics()

    print("\n  Statistics:")
    print(f"    Total Dropdowns: {stats['total_dropdowns']}")
    print(f"    Total Options: {stats['total_options']}")
    print(f"    Total Selections: {stats['total_selections']}")
    print(f"    Avg Options/Dropdown: "
          f"{stats['average_options_per_dropdown']:.2f}")

    print("\n    Dropdowns by Type:")
    for dtype, count in stats['dropdowns_by_type'].items():
        print(f"      - {dtype}: {count}")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("DROPDOWN AND SELECTION DYNAMIC KEYS - COMPREHENSIVE DEMO")
    print("=" * 60)

    demos = [
        demo_basic_dropdown,
        demo_grouped_dropdown,
        demo_cascading_dropdown,
        demo_selection_history,
        demo_multi_select_dropdown,
        demo_searchable_dropdown,
        demo_dropdown_schema_export,
        demo_statistics
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\n❌ Error in {demo.__name__}: {e}")

    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
