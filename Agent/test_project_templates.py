"""
Test project structure generation templates
Verify SOLID principles and best practices
"""
from agent.tools import coding_tools
import os
import shutil
import sys

# Add paths
agent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, agent_dir)


AGENT_WORKSPACE = coding_tools.AGENT_WORKSPACE


def setup_workspace():
    """Clean workspace before tests."""
    if os.path.exists(AGENT_WORKSPACE):
        shutil.rmtree(AGENT_WORKSPACE)
    os.makedirs(AGENT_WORKSPACE)


def teardown_workspace():
    """Clean workspace after tests."""
    if os.path.exists(AGENT_WORKSPACE):
        shutil.rmtree(AGENT_WORKSPACE)


def test_flask_api_solid_principles():
    """Test Flask API follows SOLID principles."""
    setup_workspace()
    try:
        result = coding_tools.generate_project_structure.invoke({
            "project_name": "FlaskAPI",
            "project_type": "flask_api"
        })

        project_path = os.path.join(AGENT_WORKSPACE, "flaskapi")

        # Check separation of concerns (SOLID)
        assert os.path.exists(os.path.join(project_path, "app", "models"))
        assert os.path.exists(os.path.join(project_path, "app", "routes"))
        assert os.path.exists(os.path.join(project_path, "app", "services"))
        assert os.path.exists(os.path.join(project_path, "app", "utils"))

        # Check configuration files
        assert os.path.exists(os.path.join(project_path, "config.py"))
        assert os.path.exists(os.path.join(project_path, ".env.example"))
        assert os.path.exists(os.path.join(project_path, ".gitignore"))

        # Check test structure
        assert os.path.exists(os.path.join(project_path, "tests"))

        print("✓ Flask API follows SOLID principles")
    finally:
        teardown_workspace()


def test_fastapi_clean_architecture():
    """Test FastAPI follows clean architecture."""
    setup_workspace()
    try:
        result = coding_tools.generate_project_structure.invoke({
            "project_name": "FastAPIService",
            "project_type": "fastapi_service"
        })

        project_path = os.path.join(AGENT_WORKSPACE, "fastapiservice")

        # Check clean architecture layers
        assert os.path.exists(os.path.join(project_path, "app", "api"))
        assert os.path.exists(os.path.join(project_path, "app", "core"))
        assert os.path.exists(os.path.join(project_path, "app", "models"))
        assert os.path.exists(os.path.join(project_path, "app", "schemas"))
        assert os.path.exists(os.path.join(project_path, "app", "services"))

        # Check main.py exists
        main_path = os.path.join(project_path, "app", "main.py")
        assert os.path.exists(main_path)

        # Verify main.py content
        with open(main_path, encoding='utf-8') as f:
            content = f.read()
            assert "FastAPI" in content
            assert "CORSMiddleware" in content
            assert "@app.get" in content

        print("✓ FastAPI follows clean architecture")
    finally:
        teardown_workspace()


def test_python_package_structure():
    """Test Python package has proper structure."""
    setup_workspace()
    try:
        result = coding_tools.generate_project_structure.invoke({
            "project_name": "MyPackage",
            "project_type": "python_package"
        })

        project_path = os.path.join(AGENT_WORKSPACE, "mypackage")

        # Check package structure
        assert os.path.exists(os.path.join(project_path, "src"))
        assert os.path.exists(os.path.join(project_path, "tests"))
        assert os.path.exists(os.path.join(project_path, "docs"))

        # Check setup files
        assert os.path.exists(os.path.join(project_path, "setup.py"))
        assert os.path.exists(os.path.join(project_path, "pyproject.toml"))

        # Verify setup.py content
        setup_path = os.path.join(project_path, "setup.py")
        with open(setup_path, encoding='utf-8') as f:
            content = f.read()
            assert "setuptools" in content
            assert "find_packages" in content
            assert "mypackage" in content

        # Verify pyproject.toml content
        pyproject_path = os.path.join(project_path, "pyproject.toml")
        with open(pyproject_path, encoding='utf-8') as f:
            content = f.read()
            assert "[build-system]" in content
            assert "[tool.pytest.ini_options]" in content
            assert "[tool.black]" in content

        print("✓ Python package has proper structure")
    finally:
        teardown_workspace()


def test_streamlit_app_modular_structure():
    """Test Streamlit app has modular structure."""
    setup_workspace()
    try:
        result = coding_tools.generate_project_structure.invoke({
            "project_name": "StreamlitDashboard",
            "project_type": "streamlit_app"
        })

        project_path = os.path.join(AGENT_WORKSPACE, "streamlitdashboard")

        # Check modular structure
        assert os.path.exists(os.path.join(project_path, "pages"))
        assert os.path.exists(os.path.join(project_path, "components"))
        assert os.path.exists(os.path.join(project_path, "utils"))

        # Check app.py
        app_path = os.path.join(project_path, "app.py")
        assert os.path.exists(app_path)

        # Verify app.py content
        with open(app_path, encoding='utf-8') as f:
            content = f.read()
            assert "streamlit" in content
            assert "st.set_page_config" in content
            assert "StreamlitDashboard" in content

        # Check Streamlit config
        config_path = os.path.join(project_path, ".streamlit", "config.toml")
        assert os.path.exists(config_path)

        print("✓ Streamlit app has modular structure")
    finally:
        teardown_workspace()


def test_data_analysis_project_structure():
    """Test data analysis project structure."""
    setup_workspace()
    try:
        result = coding_tools.generate_project_structure.invoke({
            "project_name": "DataAnalysis",
            "project_type": "data_analysis"
        })

        project_path = os.path.join(AGENT_WORKSPACE, "dataanalysis")

        # Check data directories
        assert os.path.exists(os.path.join(project_path, "data", "raw"))
        assert os.path.exists(os.path.join(project_path, "data", "processed"))

        # Check notebooks directory
        assert os.path.exists(os.path.join(project_path, "notebooks"))

        # Check src directory with modules
        assert os.path.exists(os.path.join(project_path, "src"))

        # Check requirements include data science packages
        req_path = os.path.join(project_path, "requirements.txt")
        with open(req_path, encoding='utf-8') as f:
            content = f.read()
            assert "pandas" in content
            assert "numpy" in content
            assert "matplotlib" in content

        print("✓ Data analysis project has proper structure")
    finally:
        teardown_workspace()


def test_readme_generation():
    """Test README.md is generated with proper content."""
    setup_workspace()
    try:
        result = coding_tools.generate_project_structure.invoke({
            "project_name": "TestProject",
            "project_type": "flask_api"
        })

        project_path = os.path.join(AGENT_WORKSPACE, "testproject")
        readme_path = os.path.join(project_path, "README.md")

        assert os.path.exists(readme_path)

        with open(readme_path, encoding='utf-8') as f:
            content = f.read()
            assert "# TestProject" in content
            assert "Installation" in content
            assert "python -m venv venv" in content
            assert "pip install -r requirements.txt" in content
            assert "Tests" in content

        print("✓ README.md generated with proper content")
    finally:
        teardown_workspace()


def test_gitignore_generation():
    """Test .gitignore is generated."""
    setup_workspace()
    try:
        result = coding_tools.generate_project_structure.invoke({
            "project_name": "TestProject",
            "project_type": "flask_api"
        })

        project_path = os.path.join(AGENT_WORKSPACE, "testproject")
        gitignore_path = os.path.join(project_path, ".gitignore")

        assert os.path.exists(gitignore_path)

        with open(gitignore_path, encoding='utf-8') as f:
            content = f.read()
            assert "__pycache__" in content
            assert "*.pyc" in content
            assert "venv" in content

        print("✓ .gitignore generated properly")
    finally:
        teardown_workspace()


def test_requirements_txt_generation():
    """Test requirements.txt is generated with dependencies."""
    setup_workspace()
    try:
        result = coding_tools.generate_project_structure.invoke({
            "project_name": "TestProject",
            "project_type": "flask_api"
        })

        project_path = os.path.join(AGENT_WORKSPACE, "testproject")
        req_path = os.path.join(project_path, "requirements.txt")

        assert os.path.exists(req_path)

        with open(req_path, encoding='utf-8') as f:
            content = f.read()
            assert "flask" in content
            assert "flask-cors" in content
            assert "python-dotenv" in content

        print("✓ requirements.txt generated with dependencies")
    finally:
        teardown_workspace()


def run_all_tests():
    """Run all template tests."""
    print("\n" + "=" * 60)
    print("Testing Project Structure Templates")
    print("=" * 60 + "\n")

    tests = [
        test_flask_api_solid_principles,
        test_fastapi_clean_architecture,
        test_python_package_structure,
        test_streamlit_app_modular_structure,
        test_data_analysis_project_structure,
        test_readme_generation,
        test_gitignore_generation,
        test_requirements_txt_generation,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
