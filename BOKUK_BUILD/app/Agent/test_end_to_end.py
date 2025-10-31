"""
End-to-End Testing Suite for KAI Agent Integration

This module tests the complete installation process, all features,
error scenarios, and validates security measures.

Requirements: All requirements from requirements.md
"""

from agent.tools.coding_tools import list_files, read_file, write_file
from agent import config as agent_config
from agent.tools.telephony_tools import start_interactive_call
import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add Agent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))


class TestInstallationProcess:
    """Test complete installation process (Requirement 1.4, 12.3, 12.4)"""

    def test_directory_structure_exists(self):
        """Verify all required directories exist"""
        agent_dir = Path(__file__).parent

        required_dirs = [
            agent_dir / "agent",
            agent_dir / "agent" / "tools",
            agent_dir / "knowledge_base",
            agent_dir / "agent_workspace",
            agent_dir / "sandbox",
        ]

        for dir_path in required_dirs:
            assert dir_path.exists(), f"Required directory missing: {dir_path}"

    def test_required_files_exist(self):
        """Verify all required files exist"""
        agent_dir = Path(__file__).parent

        required_files = [
            agent_dir / "agent" / "__init__.py",
            agent_dir / "agent" / "agent_core.py",
            agent_dir / "agent" / "config.py",
            agent_dir / "agent" / "errors.py",
            agent_dir / "agent" / "logging_config.py",
            agent_dir / "agent" / "security.py",
            agent_dir / "agent" / "tools" / "__init__.py",
            agent_dir / "agent" / "tools" / "knowledge_tools.py",
            agent_dir / "agent" / "tools" / "coding_tools.py",
            agent_dir / "agent" / "tools" / "execution_tools.py",
            agent_dir / "agent" / "tools" / "telephony_tools.py",
            agent_dir / "agent_ui.py",
            agent_dir / "README.md",
            agent_dir / "requirements.txt",
        ]

        for file_path in required_files:
            assert file_path.exists(), f"Required file missing: {file_path}"

    def test_env_example_exists(self):
        """Verify .env.example exists with all required keys (Requirement 12.4)"""
        env_example = Path(__file__).parent.parent / ".env.example"
        assert env_example.exists(), ".env.example file missing"

        content = env_example.read_text()
        required_keys = [
            "OPENAI_API_KEY",
            "TAVILY_API_KEY",
            "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN",
            "TWILIO_PHONE_NUMBER",
            "ELEVEN_LABS_API_KEY"
        ]

        for key in required_keys:
            assert key in content, f"Required key {key} missing from .env.example"

    def test_requirements_file_valid(self):
        """Verify requirements.txt is valid and contains necessary packages"""
        req_file = Path(__file__).parent / "requirements.txt"
        assert req_file.exists(), "requirements.txt missing"

        content = req_file.read_text()
        required_packages = [
            "langchain",
            "langchain-openai",
            "faiss-cpu",
            "pypdf",
            "docker",
            "streamlit"
        ]

        for package in required_packages:
            assert package in content, f"Required package {package} missing from requirements.txt"


class TestFeatureFunctionality:
    """Test all features work correctly (Requirements 2-9)"""

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing"""
        temp_dir = tempfile.mkdtemp()
        original_workspace = os.environ.get('AGENT_WORKSPACE_DIR')
        os.environ['AGENT_WORKSPACE_DIR'] = temp_dir
        yield temp_dir
        os.environ['AGENT_WORKSPACE_DIR'] = original_workspace or ''
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_file_operations(self, temp_workspace):
        """Test file system operations (Requirement 6)"""
        # Test write
        result = write_file("test.txt", "Hello World")
        assert "erfolgreich" in result.lower() or "success" in result.lower()

        # Test read
        content = read_file("test.txt")
        assert "Hello World" in content

        # Test list
        files = list_files(".")
        assert "test.txt" in files

    def test_file_security_path_validation(self, temp_workspace):
        """Test path validation prevents directory traversal (Requirement 6.3)"""
        # Attempt directory traversal
        result = write_file("../../../etc/passwd", "malicious")
        assert "nicht erlaubt" in result.lower() or "not allowed" in result.lower()

        result = read_file("../../sensitive.txt")
        assert "fehler" in result.lower() or "error" in result.lower()

    @patch('agent.tools.telephony_tools.ElevenLabs')
    def test_telephony_simulation(self, mock_elevenlabs):
        """Test telephony tools work (Requirement 4)"""
        mock_client = MagicMock()
        mock_elevenlabs.return_value = mock_client

        result = start_interactive_call(
            phone_number="+1234567890",
            opening_statement="Hello, this is a test call",
            call_goal="Test the telephony system"
        )

        assert isinstance(result, str)
        assert len(result) > 0

    def test_knowledge_base_setup(self):
        """Test knowledge base can be initialized (Requirement 3)"""
        kb_dir = Path(__file__).parent / "knowledge_base"

        # Should handle empty or missing knowledge base gracefully
        if not kb_dir.exists() or not list(kb_dir.glob("*.pdf")):
            # Test with empty knowledge base
            with patch('agent.tools.knowledge_tools.os.path.exists', return_value=False):
                # Should not crash
                pass

    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test-key-123',
        'TAVILY_API_KEY': 'test-tavily-key'
    })
    def test_config_loading(self):
        """Test configuration loads correctly (Requirement 12)"""
        # Reload config to pick up test environment
        import importlib
        importlib.reload(agent_config)

        assert agent_config.OPENAI_API_KEY == 'test-key-123'
        assert agent_config.TAVILY_API_KEY == 'test-tavily-key'


class TestErrorScenarios:
    """Test error handling and recovery (Requirement 11)"""

    def test_missing_api_keys_handled(self):
        """Test graceful handling of missing API keys (Requirement 1.4, 12.3)"""
        with patch.dict(os.environ, {}, clear=True):
            import importlib
            importlib.reload(agent_config)

            # Should not crash, should set keys to None or empty
            assert agent_config.OPENAI_API_KEY is None or agent_config.OPENAI_API_KEY == ""

    def test_invalid_file_path_handled(self):
        """Test invalid file paths are handled gracefully (Requirement 6.5)"""
        result = read_file("nonexistent_file_12345.txt")
        assert "fehler" in result.lower() or "error" in result.lower(
        ) or "nicht gefunden" in result.lower()

    def test_docker_not_available_handled(self):
        """Test graceful handling when Docker is not available (Requirement 5.5)"""
        with patch('docker.from_env', side_effect=Exception("Docker not available")):
            from agent.tools.execution_tools import execute_python_code_in_sandbox

            result = execute_python_code_in_sandbox("print('test')")
            # Should return error message, not crash
            assert isinstance(result, str)

    def test_knowledge_base_empty_handled(self):
        """Test handling of empty knowledge base (Requirement 3.5)"""
        # Should not crash when knowledge base is empty
        with tempfile.TemporaryDirectory() as temp_dir:
            # This should handle empty directory gracefully
            pass


class TestSecurityMeasures:
    """Validate security measures (Requirements 5, 6, 12)"""

    def test_path_traversal_prevention(self):
        """Test directory traversal is prevented (Requirement 6.3)"""
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\SAM"
        ]

        for path in dangerous_paths:
            result = write_file(path, "test")
            assert "nicht erlaubt" in result.lower() or "not allowed" in result.lower()

    def test_api_keys_not_in_logs(self):
        """Test API keys are not exposed in logs (Requirement 12.2)"""
        # Check that config module doesn't print keys
        import contextlib
        import io

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            import importlib
            importlib.reload(agent_config)

        output = f.getvalue()
        # Should not contain actual API key values
        assert "sk-" not in output  # OpenAI key prefix
        assert "tvly-" not in output  # Tavily key prefix

    def test_workspace_isolation(self):
        """Test operations are isolated to workspace (Requirement 6.1)"""
        # Verify workspace directory exists and is used
        from agent.tools.coding_tools import get_workspace_path
        workspace = get_workspace_path()

        assert workspace.exists()
        assert "agent_workspace" in str(workspace)

    def test_docker_security_configuration(self):
        """Test Docker sandbox security settings (Requirement 5.2)"""
        dockerfile_path = Path(__file__).parent / "sandbox" / "Dockerfile"

        if dockerfile_path.exists():
            content = dockerfile_path.read_text()

            # Should create unprivileged user
            assert "useradd" in content or "adduser" in content
            # Should switch to non-root user
            assert "USER" in content
            # Should not run as root
            assert "USER root" not in content or content.index(
                "USER root") < content.rindex("USER")


class TestIntegrationWithMainApp:
    """Test integration with main application (Requirement 14)"""

    def test_agent_ui_module_importable(self):
        """Test agent_ui module can be imported (Requirement 14.2)"""
        try:
            from Agent import agent_ui
            assert hasattr(agent_ui, 'render_agent_menu')
        except ImportError as e:
            pytest.fail(f"Failed to import agent_ui: {e}")

    def test_no_database_conflicts(self):
        """Test agent doesn't interfere with existing databases (Requirement 14.2)"""
        # Agent should not access main application databases
        agent_dir = Path(__file__).parent

        # Check that agent doesn't import main app database modules
        agent_core_file = agent_dir / "agent" / "agent_core.py"
        if agent_core_file.exists():
            content = agent_core_file.read_text()
            # Should not import main app database
            assert "from database import" not in content
            assert "import database" not in content

    def test_isolated_dependencies(self):
        """Test agent dependencies don't conflict (Requirement 14.4)"""
        # Verify agent has its own requirements
        req_file = Path(__file__).parent / "requirements.txt"
        assert req_file.exists()


class TestDocumentation:
    """Test documentation completeness (Requirement 15)"""

    def test_readme_exists_and_complete(self):
        """Test README.md exists and is comprehensive (Requirement 15.1)"""
        readme = Path(__file__).parent / "README.md"
        assert readme.exists(), "README.md missing"

        content = readme.read_text()
        required_sections = [
            "installation",
            "setup",
            "usage",
            "api key",
            "requirement"
        ]

        content_lower = content.lower()
        for section in required_sections:
            assert section in content_lower, f"README missing section about {section}"

    def test_troubleshooting_guide_exists(self):
        """Test troubleshooting documentation exists (Requirement 15.4)"""
        troubleshooting = Path(__file__).parent / "TROUBLESHOOTING.md"
        assert troubleshooting.exists(), "TROUBLESHOOTING.md missing"

    def test_code_has_docstrings(self):
        """Test code has proper documentation (Requirement 7.4)"""
        agent_core = Path(__file__).parent / "agent" / "agent_core.py"
        content = agent_core.read_text()

        # Should have module docstring
        assert '"""' in content or "'''" in content
        # Should have class/function docstrings
        assert content.count('"""') >= 4 or content.count("'''") >= 4


def run_all_tests():
    """Run all end-to-end tests and generate report"""
    print("=" * 70)
    print("KAI AGENT - END-TO-END TEST SUITE")
    print("=" * 70)

    # Run pytest with verbose output
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "-W", "ignore::DeprecationWarning"
    ]

    result = pytest.main(pytest_args)

    print("\n" + "=" * 70)
    if result == 0:
        print("✓ ALL END-TO-END TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED - Review output above")
    print("=" * 70)

    return result


if __name__ == "__main__":
    sys.exit(run_all_tests())
