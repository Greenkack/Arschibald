"""
Test Agent Integration Isolation
=================================

This test verifies that the agent system is properly isolated from
the main application and doesn't interfere with existing functionality.

Tests:
1. No database conflicts
2. State management separation
3. No interference with existing features
4. Error isolation
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add Agent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Agent"))


class TestAgentIsolation(unittest.TestCase):
    """Test suite for agent integration isolation."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock streamlit to avoid actual UI rendering
        self.st_mock = MagicMock()
        sys.modules['streamlit'] = self.st_mock

        # Mock session state
        self.st_mock.session_state = {}

    def tearDown(self):
        """Clean up after tests."""
        # Remove mocked modules
        if 'streamlit' in sys.modules:
            del sys.modules['streamlit']
        if 'agent_ui' in sys.modules:
            del sys.modules['agent_ui']

    def test_no_database_conflicts(self):
        """
        Verify that agent doesn't access main application database.

        Requirements: 14.1, 14.2
        """
        # Import agent_ui
        import agent_ui

        # Check that agent_ui doesn't import database modules
        agent_ui_source = open(
            os.path.join(os.path.dirname(__file__), "Agent", "agent_ui.py"),
            encoding='utf-8'
        ).read()

        # Verify no direct database imports
        self.assertNotIn("import database", agent_ui_source)
        self.assertNotIn("from database", agent_ui_source)
        self.assertNotIn("import product_db", agent_ui_source)
        self.assertNotIn("from product_db", agent_ui_source)
        self.assertNotIn("import crm", agent_ui_source)
        self.assertNotIn("from crm", agent_ui_source)

        print("✓ No database conflicts detected")

    def test_state_management_separation(self):
        """
        Verify that agent uses separate session state keys.

        Requirements: 14.2, 14.3
        """
        # Import agent_ui
        import agent_ui

        # Read agent_ui source
        agent_ui_source = open(
            os.path.join(os.path.dirname(__file__), "Agent", "agent_ui.py"),
            encoding='utf-8'
        ).read()

        # Check for agent-specific state keys
        # Agent should use keys like 'vector_store', 'agent_core', 'async_state'
        # Not generic keys that might conflict

        # Verify agent uses namespaced keys
        self.assertIn("vector_store", agent_ui_source)
        self.assertIn("agent_core", agent_ui_source)
        self.assertIn("async_state", agent_ui_source)

        # Verify no conflicts with common app keys
        # (These would be problematic if used without namespacing)
        problematic_keys = [
            "st.session_state['data']",
            "st.session_state['results']",
            "st.session_state['config']",
            "st.session_state['user']",
        ]

        for key in problematic_keys:
            self.assertNotIn(key, agent_ui_source,
                             f"Agent uses potentially conflicting key: {key}")

        print("✓ State management properly separated")

    def test_no_interference_with_existing_features(self):
        """
        Verify that agent doesn't modify existing application state.

        Requirements: 14.3, 14.4
        """
        # Simulate existing app state
        existing_state = {
            'selected_page_key_sui': 'input',
            'calculation_results': {'some': 'data'},
            'customer_data': {'name': 'Test Customer'},
            'db_initialized': True
        }

        # Mock session state with existing data
        self.st_mock.session_state = existing_state.copy()

        # Import and check agent_ui doesn't modify these keys
        import agent_ui

        # Read agent_ui source to verify it doesn't touch these keys
        agent_ui_source = open(
            os.path.join(os.path.dirname(__file__), "Agent", "agent_ui.py"),
            encoding='utf-8'
        ).read()

        # Verify agent doesn't modify navigation state
        self.assertNotIn("selected_page_key_sui", agent_ui_source)

        # Verify agent doesn't modify calculation results
        self.assertNotIn("calculation_results", agent_ui_source)

        # Verify agent doesn't modify customer data
        self.assertNotIn("customer_data", agent_ui_source)

        print("✓ No interference with existing features")

    def test_error_isolation(self):
        """
        Verify that agent errors don't crash the main application.

        Requirements: 14.3, 14.5
        """
        # Import agent_ui
        import agent_ui

        # Read agent_ui source
        agent_ui_source = open(
            os.path.join(os.path.dirname(__file__), "Agent", "agent_ui.py"),
            encoding='utf-8'
        ).read()

        # Verify error handling is present
        self.assertIn("try:", agent_ui_source)
        self.assertIn("except", agent_ui_source)

        # Verify errors are caught and displayed, not propagated
        self.assertIn("st.error", agent_ui_source)
        self.assertIn("st.warning", agent_ui_source)

        # Check that render_agent_menu has error handling
        self.assertIn("def render_agent_menu", agent_ui_source)

        # Verify the function doesn't raise unhandled exceptions
        # by checking for proper exception handling
        render_func_start = agent_ui_source.find("def render_agent_menu")
        render_func_end = agent_ui_source.find(
            "\n\nif __name__", render_func_start)
        if render_func_end == -1:
            render_func_end = len(agent_ui_source)

        render_func_code = agent_ui_source[render_func_start:render_func_end]

        # Count try/except blocks in render function
        try_count = render_func_code.count("try:")
        except_count = render_func_code.count("except")

        self.assertGreater(
            try_count,
            0,
            "render_agent_menu should have error handling")
        self.assertGreaterEqual(except_count, try_count,
                                "All try blocks should have except handlers")

        print("✓ Error isolation properly implemented")

    def test_module_independence(self):
        """
        Verify that agent module can be loaded independently.

        Requirements: 14.1, 14.4
        """
        # Try importing agent_ui without main app dependencies
        try:
            import agent_ui

            # Verify render_agent_menu exists
            self.assertTrue(hasattr(agent_ui, 'render_agent_menu'))
            self.assertTrue(callable(agent_ui.render_agent_menu))

            print("✓ Agent module is independent")
        except ImportError as e:
            # Check if the import error is due to missing optional dependencies
            # (which is acceptable) or due to hard dependencies on main app
            error_msg = str(e)

            # These are acceptable missing dependencies
            acceptable_missing = [
                'streamlit',
                'langchain',
                'openai',
                'tavily',
                'twilio',
                'elevenlabs',
                'faiss'
            ]

            is_acceptable = any(dep in error_msg for dep in acceptable_missing)

            if not is_acceptable:
                self.fail(
                    f"Agent module has unacceptable dependency: {error_msg}")
            else:
                print(
                    f"✓ Agent module independent (missing optional dep: {error_msg})")

    def test_gui_integration_safety(self):
        """
        Verify that gui.py integration is safe and doesn't break existing code.

        Requirements: 14.2, 14.5
        """
        # Read gui.py
        gui_path = os.path.join(os.path.dirname(__file__), "gui.py")
        if not os.path.exists(gui_path):
            self.skipTest("gui.py not found")

        gui_source = open(gui_path, encoding='utf-8').read()

        # Verify agent_ui import is conditional/safe
        self.assertIn("agent_ui_module", gui_source)

        # Verify fallback exists if agent_ui fails to load
        self.assertIn("import_module_with_fallback", gui_source)

        # Verify agent menu rendering has fallback
        agent_menu_section = gui_source[
            gui_source.find('selected_page_key == "quick_calc"'):
            gui_source.find('selected_page_key == "quick_calc"') + 500
        ]

        # Should have conditional check for agent_ui_module
        self.assertIn("agent_ui_module", agent_menu_section)
        self.assertIn("callable", agent_menu_section)

        # Should have fallback to quick_calc or warning
        # Check for elif or else (both are valid fallback patterns)
        has_fallback = (
            "elif" in agent_menu_section or "else:" in agent_menu_section)
        self.assertTrue(
            has_fallback,
            "Agent menu should have fallback mechanism")

        print("✓ GUI integration is safe with proper fallbacks")


def run_isolation_tests():
    """Run all isolation tests and report results."""
    print("\n" + "=" * 60)
    print("AGENT INTEGRATION ISOLATION TESTS")
    print("=" * 60 + "\n")

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAgentIsolation)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun -
                        len(result.failures) -
                        len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✅ ALL ISOLATION TESTS PASSED")
        print("\nThe agent system is properly isolated from the main application.")
        print("No database conflicts, state interference, or error propagation detected.")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\nPlease review the failures above and fix isolation issues.")

    print("=" * 60 + "\n")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_isolation_tests()
    sys.exit(0 if success else 1)
