# ==============================================================================
# Agent/agent/tools/coding_tools.py
# File system tools for secure agent workspace operations
# ==============================================================================
import os
import time
from typing import Optional

# LangChain 1.0+ Import
from langchain_core.tools import tool

# Import logging utilities
from agent.logging_config import get_logger, log_tool_execution

# Import error classes
from agent.errors import ToolError

# Import security utilities (Task 12.1)
from agent.security import (
    sanitize_file_path,
    sanitize_filename,
    PathTraversalError,
    InputValidationError
)

# Get logger for this module
logger = get_logger(__name__)

# Define the secure workspace directory for the agent
# All file operations are restricted to this directory
AGENT_WORKSPACE = "Agent/agent_workspace"

# Ensure the workspace directory exists
if not os.path.exists(AGENT_WORKSPACE):
    os.makedirs(AGENT_WORKSPACE)
    logger.info(f"Created agent workspace directory: {AGENT_WORKSPACE}")


def _validate_path(path: str) -> tuple[bool, str, Optional[str]]:
    """
    Validate that a path is safe and within the agent workspace.

    Uses centralized security module for validation (Task 12.1).

    Args:
        path: Relative path to validate

    Returns:
        Tuple of (is_valid, full_path, error_message)
    """
    try:
        # Use centralized security validation
        validated_path = sanitize_file_path(path, AGENT_WORKSPACE)
        return True, validated_path, None

    except PathTraversalError as e:
        error_msg = f"Fehler: {str(e)}"
        return False, "", error_msg

    except Exception as e:
        return False, "", f"Fehler bei der Pfadvalidierung: {e}"


@tool
def write_file(path: str, content: str) -> str:
    """
    Schreibt Inhalt in eine Datei unter dem angegebenen Pfad.
    Erstellt die Datei und alle notwendigen Verzeichnisse.
    Überschreibt die Datei, wenn sie bereits existiert.

    Sicherheit:
    - Operationen auf agent_workspace Verzeichnis beschränkt
    - Directory Traversal wird verhindert
    - Automatische Erstellung von Elternverzeichnissen
    - UTF-8 Encoding

    Args:
        path: Relativer Pfad zur Datei (z.B. "project/main.py")
        content: Inhalt, der in die Datei geschrieben werden soll

    Returns:
        Erfolgsmeldung oder Fehlerbeschreibung
    """
    start_time = time.time()
    logger.info(f"Writing file: {path}")

    try:
        # Security validation
        is_valid, full_path, error = _validate_path(path)
        if not is_valid:
            logger.warning(f"Path validation failed for {path}: {error}")
            return error

        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Write file with UTF-8 encoding
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        duration = time.time() - start_time
        content_size = len(content)
        logger.info(
            f"File written successfully: {path} ({content_size} bytes) in {
                duration:.2f}s")

        # Log tool execution
        log_tool_execution(
            logger,
            tool_name="write_file",
            input_summary=f"path={path}, size={content_size}",
            success=True,
            duration=duration
        )

        return f"Datei erfolgreich nach '{path}' geschrieben."

    except PermissionError as e:
        duration = time.time() - start_time
        error_msg = f"Keine Berechtigung zum Schreiben der Datei '{path}'"
        logger.error(error_msg)

        log_tool_execution(
            logger,
            tool_name="write_file",
            input_summary=f"path={path}",
            success=False,
            duration=duration,
            error=str(e)
        )

        return f"Fehler: {error_msg}."

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Error writing file {path}: {e}", exc_info=True)

        log_tool_execution(
            logger,
            tool_name="write_file",
            input_summary=f"path={path}",
            success=False,
            duration=duration,
            error=str(e)
        )

        return f"Fehler beim Schreiben der Datei: {e}"


@tool
def read_file(path: str) -> str:
    """
    Liest den Inhalt einer Datei und gibt ihn zurück.

    Sicherheit:
    - Operationen auf agent_workspace Verzeichnis beschränkt
    - Directory Traversal wird verhindert
    - UTF-8 Encoding

    Args:
        path: Relativer Pfad zur Datei (z.B. "project/main.py")

    Returns:
        Dateiinhalt oder Fehlerbeschreibung
    """
    start_time = time.time()
    logger.info(f"Reading file: {path}")

    try:
        # Security validation
        is_valid, full_path, error = _validate_path(path)
        if not is_valid:
            logger.warning(f"Path validation failed for {path}: {error}")
            return error

        # Check if file exists
        if not os.path.exists(full_path):
            logger.warning(f"File not found: {path}")
            return f"Fehler: Datei '{path}' nicht gefunden."

        if not os.path.isfile(full_path):
            logger.warning(f"Path is not a file: {path}")
            return f"Fehler: '{path}' ist keine Datei."

        # Read file with UTF-8 encoding
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        duration = time.time() - start_time
        content_size = len(content)
        logger.info(
            f"File read successfully: {path} ({content_size} bytes) in {
                duration:.2f}s")

        # Log tool execution
        log_tool_execution(
            logger,
            tool_name="read_file",
            input_summary=f"path={path}",
            success=True,
            duration=duration
        )

        return content

    except PermissionError as e:
        duration = time.time() - start_time
        error_msg = f"Keine Berechtigung zum Lesen der Datei '{path}'"
        logger.error(error_msg)

        log_tool_execution(
            logger,
            tool_name="read_file",
            input_summary=f"path={path}",
            success=False,
            duration=duration,
            error=str(e)
        )

        return f"Fehler: {error_msg}."

    except UnicodeDecodeError as e:
        duration = time.time() - start_time
        error_msg = f"Datei '{path}' konnte nicht als UTF-8 dekodiert werden"
        logger.error(error_msg)

        log_tool_execution(
            logger,
            tool_name="read_file",
            input_summary=f"path={path}",
            success=False,
            duration=duration,
            error=str(e)
        )

        return f"Fehler: {error_msg}."

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Error reading file {path}: {e}", exc_info=True)

        log_tool_execution(
            logger,
            tool_name="read_file",
            input_summary=f"path={path}",
            success=False,
            duration=duration,
            error=str(e)
        )

        return f"Fehler beim Lesen der Datei: {e}"


@tool
def list_files(path: str = ".") -> str:
    """
    Listet alle Dateien und Verzeichnisse im Arbeitsbereich auf.

    Sicherheit:
    - Operationen auf agent_workspace Verzeichnis beschränkt
    - Directory Traversal wird verhindert

    Args:
        path: Relativer Pfad zum Verzeichnis (Standard: ".")

    Returns:
        Formatierte Liste von Dateien und Verzeichnissen
    """
    start_time = time.time()
    logger.info(f"Listing files in: {path}")

    try:
        # Security validation
        is_valid, full_path, error = _validate_path(path)
        if not is_valid:
            logger.warning(f"Path validation failed for {path}: {error}")
            return error

        # Check if directory exists
        if not os.path.exists(full_path):
            logger.warning(f"Directory not found: {path}")
            return f"Fehler: Verzeichnis '{path}' nicht gefunden."

        if not os.path.isdir(full_path):
            logger.warning(f"Path is not a directory: {path}")
            return f"Fehler: '{path}' ist kein Verzeichnis."

        # List directory contents
        items = []
        for item in sorted(os.listdir(full_path)):
            item_path = os.path.join(full_path, item)
            if os.path.isdir(item_path):
                items.append(f"[DIR]  {item}/")
            else:
                # Get file size
                size = os.path.getsize(item_path)
                size_str = _format_file_size(size)
                items.append(f"[FILE] {item} ({size_str})")

        duration = time.time() - start_time
        logger.info(f"Listed {len(items)} items in {path} in {duration:.2f}s")

        # Log tool execution
        log_tool_execution(
            logger,
            tool_name="list_files",
            input_summary=f"path={path}",
            success=True,
            duration=duration
        )

        if not items:
            return f"Das Verzeichnis '{path}' ist leer."

        return "\n".join(items)

    except PermissionError as e:
        duration = time.time() - start_time
        error_msg = f"Keine Berechtigung zum Auflisten des Verzeichnisses '{path}'"
        logger.error(error_msg)

        log_tool_execution(
            logger,
            tool_name="list_files",
            input_summary=f"path={path}",
            success=False,
            duration=duration,
            error=str(e)
        )

        return f"Fehler: {error_msg}."

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Error listing files in {path}: {e}", exc_info=True)

        log_tool_execution(
            logger,
            tool_name="list_files",
            input_summary=f"path={path}",
            success=False,
            duration=duration,
            error=str(e)
        )

        return f"Fehler beim Auflisten der Dateien: {e}"


def _format_file_size(size: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


# ==============================================================================
# Project Structure Generation
# ==============================================================================

# Project templates following SOLID principles and best practices
PROJECT_TEMPLATES = {
    "flask_api": {
        "description": "Flask REST API with clean architecture",
        "structure": {
            "app/": {
                "__init__.py": "",
                "models/": {
                    "__init__.py": "",
                },
                "routes/": {
                    "__init__.py": "",
                },
                "services/": {
                    "__init__.py": "",
                },
                "utils/": {
                    "__init__.py": "",
                },
            },
            "tests/": {
                "__init__.py": "",
                "test_routes.py": "",
                "test_services.py": "",
            },
            "config.py": "",
            "requirements.txt": (
                "flask>=2.3.0\n"
                "flask-cors>=4.0.0\n"
                "python-dotenv>=1.0.0"
            ),
            ".env.example": (
                "FLASK_APP=app\n"
                "FLASK_ENV=development\n"
                "SECRET_KEY=your-secret-key-here"
            ),
            ".gitignore": (
                ".env\n"
                "__pycache__/\n"
                "*.pyc\n"
                ".pytest_cache/\n"
                "venv/\n"
                ".vscode/"
            ),
        }
    },
    "streamlit_app": {
        "description": "Streamlit application with modular structure",
        "structure": {
            "app.py": "",
            "pages/": {
                "__init__.py": "",
            },
            "components/": {
                "__init__.py": "",
            },
            "utils/": {
                "__init__.py": "",
            },
            "tests/": {
                "__init__.py": "",
                "test_app.py": "",
            },
            "requirements.txt": (
                "streamlit>=1.28.0\n"
                "pandas>=2.0.0\n"
                "plotly>=5.17.0"
            ),
            ".streamlit/": {
                "config.toml": (
                    "[theme]\n"
                    "primaryColor = '#FF4B4B'\n"
                    "backgroundColor = '#FFFFFF'\n"
                    "secondaryBackgroundColor = '#F0F2F6'"
                ),
            },
            ".gitignore": (
                "__pycache__/\n"
                "*.pyc\n"
                ".pytest_cache/\n"
                "venv/\n"
                ".vscode/"
            ),
        }
    },
    "python_package": {
        "description": "Python package with proper structure",
        "structure": {
            "src/": {
                "__init__.py": "",
            },
            "tests/": {
                "__init__.py": "",
                "test_core.py": "",
            },
            "docs/": {
                "index.md": "",
            },
            "setup.py": "",
            "pyproject.toml": "",
            "requirements.txt": "",
            "requirements-dev.txt": (
                "pytest>=7.4.0\n"
                "pytest-cov>=4.1.0\n"
                "black>=23.0.0\n"
                "flake8>=6.1.0"
            ),
            ".gitignore": (
                "__pycache__/\n"
                "*.pyc\n"
                ".pytest_cache/\n"
                "dist/\n"
                "build/\n"
                "*.egg-info/\n"
                "venv/"
            ),
        }
    },
    "fastapi_service": {
        "description": "FastAPI microservice with clean architecture",
        "structure": {
            "app/": {
                "__init__.py": "",
                "main.py": "",
                "api/": {
                    "__init__.py": "",
                    "v1/": {
                        "__init__.py": "",
                        "endpoints/": {
                            "__init__.py": "",
                        },
                    },
                },
                "core/": {
                    "__init__.py": "",
                    "config.py": "",
                },
                "models/": {
                    "__init__.py": "",
                },
                "schemas/": {
                    "__init__.py": "",
                },
                "services/": {
                    "__init__.py": "",
                },
            },
            "tests/": {
                "__init__.py": "",
                "test_api.py": "",
            },
            "requirements.txt": (
                "fastapi>=0.104.0\n"
                "uvicorn[standard]>=0.24.0\n"
                "pydantic>=2.4.0\n"
                "python-dotenv>=1.0.0"
            ),
            ".env.example": (
                "API_V1_STR=/api/v1\n"
                "PROJECT_NAME=FastAPI Service\n"
                "DEBUG=True"
            ),
            ".gitignore": (
                ".env\n"
                "__pycache__/\n"
                "*.pyc\n"
                ".pytest_cache/\n"
                "venv/\n"
                ".vscode/"
            ),
        }
    },
    "data_analysis": {
        "description": "Data analysis project structure",
        "structure": {
            "data/": {
                "raw/": {},
                "processed/": {},
            },
            "notebooks/": {
                "01_exploration.ipynb": "",
            },
            "src/": {
                "__init__.py": "",
                "data_processing.py": "",
                "visualization.py": "",
                "analysis.py": "",
            },
            "tests/": {
                "__init__.py": "",
                "test_processing.py": "",
            },
            "requirements.txt": (
                "pandas>=2.0.0\n"
                "numpy>=1.24.0\n"
                "matplotlib>=3.7.0\n"
                "seaborn>=0.12.0\n"
                "jupyter>=1.0.0"
            ),
            ".gitignore": (
                "data/raw/*\n"
                "data/processed/*\n"
                "__pycache__/\n"
                "*.pyc\n"
                ".ipynb_checkpoints/\n"
                "venv/"
            ),
        }
    },
}


def _create_directory_structure(
    base_path: str,
    structure: dict,
    project_name: str
) -> list:
    """
    Recursively create directory structure from template.

    Args:
        base_path: Base path where to create the structure
        structure: Dictionary representing the directory structure
        project_name: Name of the project for substitution

    Returns:
        List of created files and directories
    """
    created_items = []

    for name, content in structure.items():
        item_path = os.path.join(base_path, name)

        if isinstance(content, dict):
            # It's a directory
            os.makedirs(item_path, exist_ok=True)
            created_items.append(f"[DIR]  {name}")
            # Recursively create subdirectories
            sub_items = _create_directory_structure(
                item_path, content, project_name)
            created_items.extend([f"  {item}" for item in sub_items])
        else:
            # It's a file
            file_content = content

            # Apply template substitutions
            if name == "README.md":
                file_content = _generate_readme(project_name)
            elif name == "setup.py":
                file_content = _generate_setup_py(project_name)
            elif name == "pyproject.toml":
                file_content = _generate_pyproject_toml(project_name)
            elif (name == "app.py" and
                  "streamlit" in base_path.lower()):
                file_content = _generate_streamlit_app(project_name)
            elif (name == "main.py" and
                  "fastapi" in base_path.lower()):
                file_content = _generate_fastapi_main(project_name)
            elif name == "config.py":
                file_content = _generate_config_py()

            with open(item_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            created_items.append(f"[FILE] {name}")

    return created_items


def _generate_readme(project_name: str) -> str:
    """Generate README.md content."""
    return f"""# {project_name}

## Beschreibung

{project_name} - Automatisch generiert mit KAI Agent

## Installation

```bash
# Virtuelle Umgebung erstellen
python -m venv venv

# Virtuelle Umgebung aktivieren
# Windows:
venv\\Scripts\\activate
# Linux/Mac:
source venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```

## Verwendung

Siehe Dokumentation in den jeweiligen Modulen.

## Tests

```bash
pytest tests/
```

## Lizenz

Alle Rechte vorbehalten.
"""


def _generate_setup_py(project_name: str) -> str:
    """Generate setup.py content."""
    package_name = (
        project_name.lower()
        .replace(" ", "_")
        .replace("-", "_")
    )
    return f"""from setuptools import setup, find_packages

setup(
    name="{package_name}",
    version="0.1.0",
    description="{project_name}",
    author="KAI Agent",
    packages=find_packages(where="src"),
    package_dir={{"": "src"}},
    python_requires=">=3.8",
    install_requires=[
        # Add your dependencies here
    ],
    extras_require={{
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.1.0",
        ],
    }},
)
"""


def _generate_pyproject_toml(project_name: str) -> str:
    """Generate pyproject.toml content."""
    package_name = (
        project_name.lower()
        .replace(" ", "_")
        .replace("-", "_")
    )
    return f"""[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{package_name}"
version = "0.1.0"
description = "{project_name}"
readme = "README.md"
requires-python = ">=3.8"
authors = [
    {{name = "KAI Agent"}}
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311']

[tool.flake8]
max-line-length = 100
extend-ignore = ["E203", "W503"]
"""


def _generate_streamlit_app(project_name: str) -> str:
    """Generate Streamlit app.py content."""
    return f'''"""
{project_name}
Streamlit Application
"""
import streamlit as st


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="{project_name}",
        page_icon="🚀",
        layout="wide"
    )

    st.title("{project_name}")
    st.write("Willkommen zu Ihrer Streamlit-Anwendung!")

    # Add your application logic here
    st.info(
        "Diese Anwendung wurde automatisch "
        "mit KAI Agent generiert."
    )


if __name__ == "__main__":
    main()
'''


def _generate_fastapi_main(project_name: str) -> str:
    """Generate FastAPI main.py content."""
    return f'''"""
{project_name}
FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="{project_name}",
    description="API generiert mit KAI Agent",
    version="0.1.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {{"message": "Willkommen zu {project_name}"}}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {{"status": "healthy"}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''


def _generate_config_py() -> str:
    """Generate config.py content."""
    return '''"""
Configuration management
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration class."""

    # Environment
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # Add your configuration variables here

    @classmethod
    def get(
        cls,
        key: str,
        default: Optional[str] = None
    ) -> Optional[str]:
        """Get configuration value."""
        return os.getenv(key, default)


# Create config instance
config = Config()
'''


@tool
def generate_project_structure(
    project_name: str,
    project_type: str,
    features: str = ""
) -> str:
    """
    Generiert eine vollständige Projektstruktur.
    Basiert auf Best Practices und SOLID-Prinzipien.

    Unterstützte Projekttypen:
    - flask_api: Flask REST API mit Clean Architecture
    - streamlit_app: Streamlit-Anwendung mit Modulstruktur
    - python_package: Python-Paket mit korrekter Struktur
    - fastapi_service: FastAPI-Microservice
    - data_analysis: Datenanalyse-Projektstruktur

    Args:
        project_name: Name des Projekts (z.B. "MeinProjekt")
        project_type: Typ des Projekts (siehe oben)
        features: Optionale zusätzliche Features (kommagetrennt)

    Returns:
        Zusammenfassung der erstellten Dateien
    """
    start_time = time.time()
    logger.info(
        f"Generating project structure: {project_name} (type={project_type})")

    try:
        # Validate project type
        if project_type not in PROJECT_TEMPLATES:
            available_types = ", ".join(PROJECT_TEMPLATES.keys())
            logger.warning(f"Unknown project type: {project_type}")
            return (
                f"Fehler: Unbekannter Projekttyp '{project_type}'. "
                f"Verfügbare Typen: {available_types}"
            )

        # Sanitize project name for directory
        safe_project_name = (
            project_name
            .replace(" ", "_")
            .replace("-", "_")
            .lower()
        )
        logger.debug(f"Sanitized project name: {safe_project_name}")

        # Validate path
        is_valid, project_path, error = _validate_path(safe_project_name)
        if not is_valid:
            logger.warning(f"Path validation failed: {error}")
            return error

        # Check if project already exists
        if os.path.exists(project_path):
            logger.warning(f"Project already exists: {safe_project_name}")
            return (
                f"Fehler: Projekt '{safe_project_name}' "
                f"existiert bereits im Arbeitsbereich."
            )

        # Create project directory
        logger.debug(f"Creating project directory: {project_path}")
        os.makedirs(project_path, exist_ok=True)

        # Get template
        template = PROJECT_TEMPLATES[project_type]
        logger.debug(f"Using template: {template['description']}")

        # Create structure
        logger.info("Creating project structure from template")
        created_items = _create_directory_structure(
            project_path,
            template["structure"],
            project_name
        )

        # Create README.md
        readme_path = os.path.join(project_path, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(_generate_readme(project_name))
        created_items.append("[FILE] README.md")

        duration = time.time() - start_time
        logger.info(
            f"Project structure generated successfully in {
                duration:.2f}s ({
                len(created_items)} items)")

        # Log tool execution
        log_tool_execution(
            logger,
            tool_name="generate_project_structure",
            input_summary=f"name={project_name}, type={project_type}",
            success=True,
            duration=duration
        )

        # Build summary
        summary = f"""Projekt '{project_name}' erfolgreich erstellt!

Typ: {template['description']}
Pfad: {safe_project_name}/

Erstellte Struktur:
"""
        summary += "\n".join(created_items)

        summary += f"""

Nächste Schritte:
1. Navigieren Sie zum Projektverzeichnis
2. Erstellen Sie eine virtuelle Umgebung: python -m venv venv
3. Aktivieren Sie die virtuelle Umgebung
4. Installieren Sie: pip install -r requirements.txt
5. Beginnen Sie mit der Entwicklung!

Hinweis: Alle Dateien befinden sich im
Agent/agent_workspace/{safe_project_name}/ Verzeichnis.
"""

        return summary

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Error generating project structure: {e}", exc_info=True)

        # Log failed tool execution
        log_tool_execution(
            logger,
            tool_name="generate_project_structure",
            input_summary=f"name={project_name}, type={project_type}",
            success=False,
            duration=duration,
            error=str(e)
        )

        return f"Fehler beim Generieren der Projektstruktur: {e}"
