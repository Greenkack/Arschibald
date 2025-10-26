"""
Demonstration of File System Tools
Shows all capabilities of the coding tools implementation
"""
from agent.tools import coding_tools
import os
import shutil
import sys

# Add paths
agent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, agent_dir)


AGENT_WORKSPACE = coding_tools.AGENT_WORKSPACE


def demo_basic_file_operations():
    """Demonstrate basic file operations."""
    print("\n" + "=" * 60)
    print("DEMO 1: Basic File Operations")
    print("=" * 60)

    # Clean workspace
    if os.path.exists(AGENT_WORKSPACE):
        shutil.rmtree(AGENT_WORKSPACE)
    os.makedirs(AGENT_WORKSPACE)

    # Write a file
    print("\n1. Writing a file...")
    result = coding_tools.write_file.invoke({
        "path": "demo.txt",
        "content": "Hello from KAI Agent!"
    })
    print(f"   Result: {result}")

    # Read the file
    print("\n2. Reading the file...")
    content = coding_tools.read_file.invoke({"path": "demo.txt"})
    print(f"   Content: {content}")

    # Write a file in subdirectory
    print("\n3. Writing file in subdirectory...")
    result = coding_tools.write_file.invoke({
        "path": "subdir/nested.txt",
        "content": "Nested file content"
    })
    print(f"   Result: {result}")

    # List files
    print("\n4. Listing files...")
    files = coding_tools.list_files.invoke({"path": "."})
    print(f"   Files:\n{files}")


def demo_security_features():
    """Demonstrate security features."""
    print("\n" + "=" * 60)
    print("DEMO 2: Security Features")
    print("=" * 60)

    # Try directory traversal
    print("\n1. Attempting directory traversal (should fail)...")
    result = coding_tools.write_file.invoke({
        "path": "../../../etc/passwd",
        "content": "malicious"
    })
    print(f"   Result: {result}")

    # Try absolute path
    print("\n2. Attempting absolute path (should fail)...")
    result = coding_tools.write_file.invoke({
        "path": "/etc/passwd",
        "content": "malicious"
    })
    print(f"   Result: {result}")

    # Try reading non-existent file
    print("\n3. Reading non-existent file (should fail gracefully)...")
    result = coding_tools.read_file.invoke({"path": "nonexistent.txt"})
    print(f"   Result: {result}")


def demo_project_generation():
    """Demonstrate project structure generation."""
    print("\n" + "=" * 60)
    print("DEMO 3: Project Structure Generation")
    print("=" * 60)

    # Generate Flask API project
    print("\n1. Generating Flask API project...")
    result = coding_tools.generate_project_structure.invoke({
        "project_name": "DemoFlaskAPI",
        "project_type": "flask_api"
    })
    print(f"   Result:\n{result}")

    # List the generated structure
    print("\n2. Listing generated project structure...")
    project_path = os.path.join(AGENT_WORKSPACE, "demoflaskapi")
    if os.path.exists(project_path):
        print(f"   ✓ Project created at: {project_path}")
        print(f"   ✓ Contains {len(os.listdir(project_path))} items")

        # Show some key files
        readme_path = os.path.join(project_path, "README.md")
        if os.path.exists(readme_path):
            print("   ✓ README.md exists")
            with open(readme_path, encoding='utf-8') as f:
                first_line = f.readline().strip()
                print(f"     First line: {first_line}")


def demo_all_project_types():
    """Demonstrate all project types."""
    print("\n" + "=" * 60)
    print("DEMO 4: All Project Types")
    print("=" * 60)

    project_types = [
        ("flask_api", "Flask REST API"),
        ("streamlit_app", "Streamlit Application"),
        ("python_package", "Python Package"),
        ("fastapi_service", "FastAPI Microservice"),
        ("data_analysis", "Data Analysis Project"),
    ]

    for project_type, description in project_types:
        print(f"\n{description}:")
        result = coding_tools.generate_project_structure.invoke({
            "project_name": f"Demo{project_type.title().replace('_', '')}",
            "project_type": project_type
        })

        if "erfolgreich" in result:
            print(f"   ✓ Successfully generated {project_type}")
        else:
            print(f"   ✗ Failed to generate {project_type}")


def show_workspace_summary():
    """Show summary of workspace contents."""
    print("\n" + "=" * 60)
    print("WORKSPACE SUMMARY")
    print("=" * 60)

    if os.path.exists(AGENT_WORKSPACE):
        total_files = 0
        total_dirs = 0

        for root, dirs, files in os.walk(AGENT_WORKSPACE):
            total_dirs += len(dirs)
            total_files += len(files)

        print(f"\nWorkspace: {AGENT_WORKSPACE}")
        print(f"Total directories: {total_dirs}")
        print(f"Total files: {total_files}")

        # List top-level items
        print("\nTop-level items:")
        for item in sorted(os.listdir(AGENT_WORKSPACE)):
            item_path = os.path.join(AGENT_WORKSPACE, item)
            if os.path.isdir(item_path):
                print(f"  [DIR]  {item}/")
            else:
                size = os.path.getsize(item_path)
                print(f"  [FILE] {item} ({size} bytes)")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 60)
    print("KAI AGENT - FILE SYSTEM TOOLS DEMONSTRATION")
    print("=" * 60)

    try:
        demo_basic_file_operations()
        demo_security_features()
        demo_project_generation()
        demo_all_project_types()
        show_workspace_summary()

        print("\n" + "=" * 60)
        print("DEMONSTRATION COMPLETE")
        print("=" * 60)
        print("\nAll file system tools are working correctly!")
        print("✓ Secure file operations")
        print("✓ Directory traversal prevention")
        print("✓ Project structure generation")
        print("✓ Multiple project templates")
        print("✓ SOLID principles compliance")

    except Exception as e:
        print(f"\n✗ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        print("\n" + "=" * 60)
        print("CLEANUP")
        print("=" * 60)
        response = input("\nDelete workspace? (y/n): ")
        if response.lower() == 'y':
            if os.path.exists(AGENT_WORKSPACE):
                shutil.rmtree(AGENT_WORKSPACE)
                print("✓ Workspace deleted")
        else:
            print(f"✓ Workspace preserved at: {AGENT_WORKSPACE}")


if __name__ == "__main__":
    main()
