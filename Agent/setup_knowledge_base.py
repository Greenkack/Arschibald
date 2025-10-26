#!/usr/bin/env python3
"""
Knowledge Base Setup Script

This script helps set up and manage the KAI Agent knowledge base.

Features:
- Create knowledge base directory
- Add sample documents
- Index existing documents
- Verify knowledge base
- Clear and rebuild index

Usage:
    python Agent/setup_knowledge_base.py [command]

Commands:
    init     - Initialize knowledge base directory
    index    - Index all PDF documents
    verify   - Verify knowledge base setup
    clear    - Clear existing index
    rebuild  - Clear and rebuild index
    sample   - Create sample documents
"""

import argparse
import shutil
import sys
from pathlib import Path


class Colors:
    """ANSI color codes."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_info(text):
    """Print info message."""
    print(f"{Colors.CYAN}ℹ {text}{Colors.RESET}")


def print_header(text):
    """Print header."""
    print()
    print("=" * 70)
    print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.RESET}")
    print("=" * 70)
    print()


def init_knowledge_base():
    """Initialize knowledge base directory."""
    print_header("Initializing Knowledge Base")

    kb_dir = Path("Agent/knowledge_base")

    if kb_dir.exists():
        print_warning(f"Knowledge base directory already exists: {kb_dir}")
        return True

    try:
        kb_dir.mkdir(parents=True, exist_ok=True)
        print_success(f"Created knowledge base directory: {kb_dir}")

        # Create README
        readme_path = kb_dir / "README.md"
        readme_content = """# Knowledge Base

This directory contains PDF documents that the KAI Agent uses for domain knowledge.

## Adding Documents

1. Place PDF files in this directory
2. The agent will automatically index them on first use
3. Supported formats: PDF only

## Best Practices

- Use descriptive filenames
- Keep documents focused on specific topics
- Limit to < 1000 PDFs for best performance
- Update regularly with latest information

## Document Types

Recommended document types:
- Product datasheets
- Technical specifications
- Sales materials
- Installation guides
- Troubleshooting guides
- Market research
- Regulatory information

## Indexing

The knowledge base is automatically indexed using:
- FAISS vector database
- OpenAI embeddings
- Chunk size: 1000 characters
- Chunk overlap: 100 characters

## Maintenance

To rebuild the index:
```bash
python Agent/setup_knowledge_base.py rebuild
```

To verify the setup:
```bash
python Agent/setup_knowledge_base.py verify
```
"""
        readme_path.write_text(readme_content, encoding='utf-8')
        print_success("Created README.md")

        return True
    except Exception as e:
        print_error(f"Failed to create knowledge base directory: {e}")
        return False


def index_documents():
    """Index all PDF documents in knowledge base."""
    print_header("Indexing Documents")

    kb_dir = Path("Agent/knowledge_base")

    if not kb_dir.exists():
        print_error("Knowledge base directory does not exist")
        print_info("Run: python Agent/setup_knowledge_base.py init")
        return False

    # Find all PDFs
    pdf_files = list(kb_dir.glob("*.pdf"))

    if not pdf_files:
        print_warning("No PDF documents found in knowledge base")
        print_info(f"Add PDF files to: {kb_dir}")
        return True

    print_info(f"Found {len(pdf_files)} PDF document(s)")
    for pdf in pdf_files:
        print(f"  - {pdf.name}")
    print()

    # Try to import and run indexing
    try:
        from agent.tools.knowledge_tools import setup_knowledge_base

        print_info("Starting indexing process...")
        print_info("This may take a few minutes for large document sets...")
        print()

        vector_store = setup_knowledge_base(
            path=str(kb_dir),
            db_path="Agent/faiss_index"
        )

        print()
        print_success("Knowledge base indexed successfully")
        print_info("Index saved to: Agent/faiss_index")
        return True

    except ImportError:
        print_error("Failed to import knowledge tools")
        print_info("Make sure dependencies are installed:")
        print_info("  pip install -r Agent/requirements.txt")
        return False
    except Exception as e:
        print_error(f"Failed to index documents: {e}")
        return False


def verify_knowledge_base():
    """Verify knowledge base setup."""
    print_header("Verifying Knowledge Base")

    kb_dir = Path("Agent/knowledge_base")
    index_dir = Path("Agent/faiss_index")

    # Check directory exists
    if not kb_dir.exists():
        print_error("Knowledge base directory does not exist")
        return False
    print_success(f"Knowledge base directory exists: {kb_dir}")

    # Check for PDFs
    pdf_files = list(kb_dir.glob("*.pdf"))
    if not pdf_files:
        print_warning("No PDF documents found")
        print_info("Add PDF files to the knowledge base directory")
    else:
        print_success(f"Found {len(pdf_files)} PDF document(s)")

    # Check for index
    if not index_dir.exists():
        print_warning("FAISS index not found")
        print_info("Run: python Agent/setup_knowledge_base.py index")
    else:
        print_success(f"FAISS index exists: {index_dir}")

        # Check index files
        index_file = index_dir / "index.faiss"
        pkl_file = index_dir / "index.pkl"

        if index_file.exists():
            print_success("  - index.faiss found")
        else:
            print_warning("  - index.faiss not found")

        if pkl_file.exists():
            print_success("  - index.pkl found")
        else:
            print_warning("  - index.pkl not found")

    # Try to load and test
    try:
        from agent.tools.knowledge_tools import setup_knowledge_base

        print()
        print_info("Testing knowledge base search...")

        vector_store = setup_knowledge_base(
            path=str(kb_dir),
            db_path="Agent/faiss_index"
        )

        # Try a test search
        results = vector_store.similarity_search("test", k=1)

        if results:
            print_success("Knowledge base search is working")
            print_info(f"Test search returned {len(results)} result(s)")
        else:
            print_warning("Knowledge base search returned no results")

        return True

    except ImportError:
        print_warning(
            "Cannot test knowledge base (dependencies not installed)")
        return True
    except Exception as e:
        print_error(f"Error testing knowledge base: {e}")
        return False


def clear_index():
    """Clear existing FAISS index."""
    print_header("Clearing Index")

    index_dir = Path("Agent/faiss_index")

    if not index_dir.exists():
        print_info("No index to clear")
        return True

    try:
        shutil.rmtree(index_dir)
        print_success("Index cleared successfully")
        return True
    except Exception as e:
        print_error(f"Failed to clear index: {e}")
        return False


def rebuild_index():
    """Clear and rebuild index."""
    print_header("Rebuilding Index")

    if not clear_index():
        return False

    print()
    return index_documents()


def create_sample_documents():
    """Create sample PDF documents."""
    print_header("Creating Sample Documents")

    print_info("This will create sample PDF documents for testing")
    print_warning("This requires reportlab to be installed")
    print()

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas
    except ImportError:
        print_error("reportlab is not installed")
        print_info("Install with: pip install reportlab")
        return False

    kb_dir = Path("Agent/knowledge_base")

    if not kb_dir.exists():
        print_error("Knowledge base directory does not exist")
        print_info("Run: python Agent/setup_knowledge_base.py init")
        return False

    # Sample document 1: Photovoltaics
    sample1_path = kb_dir / "sample_photovoltaics.pdf"
    if sample1_path.exists():
        print_warning(f"Sample document already exists: {sample1_path.name}")
    else:
        try:
            c = canvas.Canvas(str(sample1_path), pagesize=letter)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(
                1 * inch,
                10 * inch,
                "Photovoltaik-Anlagen: Vorteile und Nutzen")
            c.setFont("Helvetica", 12)
            y = 9.5 * inch

            content = [
                "Vorteile von Photovoltaik-Anlagen:",
                "",
                "1. Umweltfreundlich: Saubere, erneuerbare Energie ohne CO2-Emissionen",
                "2. Kosteneinsparung: Reduzierung der Stromkosten um bis zu 70%",
                "3. Unabhängigkeit: Weniger abhängig von Energieversorgern",
                "4. Wertsteigerung: Erhöht den Wert der Immobilie",
                "5. Förderung: Staatliche Zuschüsse und Einspeisevergütung",
                "",
                "Technische Daten:",
                "- Leistung: 5-20 kWp für Einfamilienhäuser",
                "- Lebensdauer: 25-30 Jahre",
                "- Amortisation: 10-15 Jahre",
                "- Wirkungsgrad: 15-22%",
            ]

            for line in content:
                c.drawString(1 * inch, y, line)
                y -= 0.3 * inch

            c.save()
            print_success(f"Created: {sample1_path.name}")
        except Exception as e:
            print_error(f"Failed to create sample document: {e}")
            return False

    # Sample document 2: Heat Pumps
    sample2_path = kb_dir / "sample_heat_pumps.pdf"
    if sample2_path.exists():
        print_warning(f"Sample document already exists: {sample2_path.name}")
    else:
        try:
            c = canvas.Canvas(str(sample2_path), pagesize=letter)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(
                1 * inch,
                10 * inch,
                "Wärmepumpen: Effiziente Heiztechnologie")
            c.setFont("Helvetica", 12)
            y = 9.5 * inch

            content = [
                "Vorteile von Wärmepumpen:",
                "",
                "1. Hohe Effizienz: COP von 3-5 (300-500% Wirkungsgrad)",
                "2. Niedrige Betriebskosten: Bis zu 50% Einsparung gegenüber Gas",
                "3. Umweltfreundlich: Nutzt erneuerbare Umweltenergie",
                "4. Vielseitig: Heizen und Kühlen möglich",
                "5. Wartungsarm: Geringe Wartungskosten",
                "",
                "Typen:",
                "- Luft-Wasser-Wärmepumpe: Am häufigsten, einfache Installation",
                "- Sole-Wasser-Wärmepumpe: Höchste Effizienz, Erdbohrung nötig",
                "- Wasser-Wasser-Wärmepumpe: Sehr effizient, Grundwasser nötig",
            ]

            for line in content:
                c.drawString(1 * inch, y, line)
                y -= 0.3 * inch

            c.save()
            print_success(f"Created: {sample2_path.name}")
        except Exception as e:
            print_error(f"Failed to create sample document: {e}")
            return False

    print()
    print_success("Sample documents created")
    print_info("You can now index them with:")
    print_info("  python Agent/setup_knowledge_base.py index")

    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="KAI Agent Knowledge Base Setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  init     - Initialize knowledge base directory
  index    - Index all PDF documents
  verify   - Verify knowledge base setup
  clear    - Clear existing index
  rebuild  - Clear and rebuild index
  sample   - Create sample documents

Examples:
  python Agent/setup_knowledge_base.py init
  python Agent/setup_knowledge_base.py index
  python Agent/setup_knowledge_base.py verify
        """
    )

    parser.add_argument(
        'command',
        choices=['init', 'index', 'verify', 'clear', 'rebuild', 'sample'],
        help='Command to execute'
    )

    args = parser.parse_args()

    # Execute command
    commands = {
        'init': init_knowledge_base,
        'index': index_documents,
        'verify': verify_knowledge_base,
        'clear': clear_index,
        'rebuild': rebuild_index,
        'sample': create_sample_documents,
    }

    success = commands[args.command]()

    print()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
