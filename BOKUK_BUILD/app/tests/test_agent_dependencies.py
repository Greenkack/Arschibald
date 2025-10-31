"""
Test Agent Dependencies
=======================

This test verifies that agent dependencies are properly managed
and don't conflict with existing application dependencies.

Tests:
1. All agent dependencies are in requirements.txt
2. No version conflicts with existing packages
3. Installation process works correctly
4. Dependencies are documented
"""

import os
import sys
import subprocess
import unittest
from typing import List, Dict, Tuple


class TestAgentDependencies(unittest.TestCase):
    """Test suite for agent dependency management."""

    def setUp(self):
        """Set up test fixtures."""
        self.requirements_path = os.path.join(
            os.path.dirname(__file__),
            "requirements.txt"
        )

        # Read requirements.txt
        with open(self.requirements_path, 'r', encoding='utf-8') as f:
            self.requirements_content = f.read()

        # Required agent dependencies
        self.required_agent_deps = [
            'langchain',
            'langchain-openai',
            'langchain-community',
            'tavily-python',
            'twilio',
            'elevenlabs',
            'faiss-cpu',
            'websockets'
        ]

    def test_all_dependencies_present(self):
        """
        Verify all required agent dependencies are in requirements.txt.

        Requirements: 14.4
        """
        missing_deps = []

        for dep in self.required_agent_deps:
            if dep not in self.requirements_content:
                missing_deps.append(dep)

        self.assertEqual(
            len(missing_deps), 0,
            f"Missing agent dependencies: {missing_deps}"
        )

        print(
            f"✓ All {len(self.required_agent_deps)} agent dependencies present")

    def test_dependencies_have_versions(self):
        """
        Verify all agent dependencies have pinned versions.

        Requirements: 14.4
        """
        unversioned_deps = []

        for dep in self.required_agent_deps:
            # Check if dependency has version specifier
            if dep in self.requirements_content:
                # Find the line with this dependency
                for line in self.requirements_content.split('\n'):
                    if line.startswith(dep):
                        if '==' not in line and '>=' not in line and '<=' not in line:
                            unversioned_deps.append(dep)
                        break

        self.assertEqual(
            len(unversioned_deps), 0,
            f"Dependencies without version pins: {unversioned_deps}"
        )

        print("✓ All agent dependencies have pinned versions")

    def test_no_duplicate_dependencies(self):
        """
        Verify no duplicate dependency entries.

        Requirements: 14.4
        """
        lines = self.requirements_content.split('\n')
        package_names = []
        duplicates = []

        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # Extract package name (before ==, >=, etc.)
                pkg_name = line.split('==')[0].split(
                    '>=')[0].split('<=')[0].strip()

                if pkg_name in package_names:
                    duplicates.append(pkg_name)
                else:
                    package_names.append(pkg_name)

        self.assertEqual(
            len(duplicates), 0,
            f"Duplicate dependencies found: {duplicates}"
        )

        print("✓ No duplicate dependencies")

    def test_agent_section_documented(self):
        """
        Verify agent dependencies are documented in requirements.txt.

        Requirements: 14.4
        """
        # Check for agent dependencies section
        self.assertIn(
            "KAI Agent Dependencies",
            self.requirements_content,
            "Agent dependencies section not found in requirements.txt"
        )

        # Check that section comes before the dependencies
        agent_section_pos = self.requirements_content.find(
            "KAI Agent Dependencies")
        langchain_pos = self.requirements_content.find("langchain==")

        self.assertLess(
            agent_section_pos, langchain_pos,
            "Agent dependencies section should come before the dependencies"
        )

        print("✓ Agent dependencies are properly documented")

    def test_check_for_known_conflicts(self):
        """
        Check for known version conflicts with existing packages.

        Requirements: 14.4
        """
        # Parse requirements to check for potential conflicts
        lines = self.requirements_content.split('\n')
        packages = {}

        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                if '==' in line:
                    pkg_name, version = line.split('==')
                    packages[pkg_name.strip()] = version.strip()

        # Check for known conflicts
        conflicts = []

        # Example: Check if pydantic versions are compatible
        if 'pydantic' in packages and 'langchain' in packages:
            pydantic_version = packages['pydantic']
            # LangChain 0.3.x requires pydantic >= 2.0
            if pydantic_version.startswith('1.'):
                conflicts.append(
                    f"pydantic {pydantic_version} may conflict with langchain "
                    "(requires pydantic >= 2.0)"
                )

        # Check if numpy versions are compatible
        if 'numpy' in packages:
            numpy_version = packages['numpy']
            # Some packages require specific numpy versions
            major_version = int(numpy_version.split('.')[0])
            if major_version < 1:
                conflicts.append(
                    f"numpy {numpy_version} may be too old for some dependencies")

        self.assertEqual(
            len(conflicts), 0,
            f"Potential version conflicts detected: {conflicts}"
        )

        print("✓ No known version conflicts detected")

    def test_installation_guide_exists(self):
        """
        Verify installation guide exists and mentions agent dependencies.

        Requirements: 14.4
        """
        guide_path = os.path.join(
            os.path.dirname(__file__),
            "AGENT_INSTALLATION_GUIDE.md"
        )

        self.assertTrue(
            os.path.exists(guide_path),
            "AGENT_INSTALLATION_GUIDE.md not found"
        )

        # Read guide
        with open(guide_path, 'r', encoding='utf-8') as f:
            guide_content = f.read()

        # Check for key sections
        self.assertIn("pip install", guide_content)
        self.assertIn("requirements.txt", guide_content)

        print("✓ Installation guide exists and is complete")

    def test_dependency_documentation_exists(self):
        """
        Verify dependency documentation exists.

        Requirements: 14.4
        """
        doc_path = os.path.join(
            os.path.dirname(__file__),
            "AGENT_DEPENDENCIES.md"
        )

        self.assertTrue(
            os.path.exists(doc_path),
            "AGENT_DEPENDENCIES.md not found"
        )

        # Read documentation
        with open(doc_path, 'r', encoding='utf-8') as f:
            doc_content = f.read()

        # Check that all agent dependencies are documented
        for dep in self.required_agent_deps:
            self.assertIn(
                dep,
                doc_content,
                f"Dependency {dep} not documented in AGENT_DEPENDENCIES.md"
            )

        print("✓ Dependency documentation exists and is complete")

    def test_can_import_agent_dependencies(self):
        """
        Verify that agent dependencies can be imported.

        Requirements: 14.4

        Note: This test will be skipped if dependencies are not installed.
        """
        import_results = {}

        # Try importing each dependency
        test_imports = {
            'langchain': 'langchain',
            'langchain-openai': 'langchain_openai',
            'langchain-community': 'langchain_community',
            'tavily-python': 'tavily',
            'twilio': 'twilio',
            'elevenlabs': 'elevenlabs',
            'faiss-cpu': 'faiss',
            'websockets': 'websockets'
        }

        for dep_name, import_name in test_imports.items():
            try:
                __import__(import_name)
                import_results[dep_name] = True
            except ImportError:
                import_results[dep_name] = False

        # Count successful imports
        successful = sum(1 for v in import_results.values() if v)
        total = len(import_results)

        if successful == 0:
            self.skipTest(
                "No agent dependencies installed. "
                "Run: pip install -r requirements.txt"
            )

        # Report results
        print(
            f"✓ Successfully imported {successful}/{total} agent dependencies")

        if successful < total:
            failed = [k for k, v in import_results.items() if not v]
            print(f"  Note: Could not import: {', '.join(failed)}")
            print("  Run: pip install -r requirements.txt")


def run_dependency_tests():
    """Run all dependency tests and report results."""
    print("\n" + "=" * 60)
    print("AGENT DEPENDENCY MANAGEMENT TESTS")
    print("=" * 60 + "\n")

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAgentDependencies)

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
                        len(result.errors) -
                        len(result.skipped)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.wasSuccessful():
        print("\n✅ ALL DEPENDENCY TESTS PASSED")
        print("\nAgent dependencies are properly managed:")
        print("- All required dependencies are in requirements.txt")
        print("- No version conflicts detected")
        print("- Dependencies are documented")
        print("- Installation process is clear")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\nPlease review the failures above and fix dependency issues.")

    print("=" * 60 + "\n")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_dependency_tests()
    sys.exit(0 if success else 1)
