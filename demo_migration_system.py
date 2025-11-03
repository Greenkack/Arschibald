"""Demo: Database Migration System

This script demonstrates the database migration system with Alembic.
"""

import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.migrations import (
    MigrationManager,
    create_migration,
    get_migration_manager,
    migrate,
    rollback,
)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.table import Table

    console = Console()
except ImportError:
    print("Install rich for better output: pip install rich")
    sys.exit(1)


def demo_initialization():
    """Demo: Initialize migration environment"""
    console.print(Panel.fit("🔧 Demo 1: Initialize Migration Environment", style="bold cyan"))

    try:
        manager = get_migration_manager()
        manager.initialize_alembic()

        console.print("[green]✓[/green] Migration environment initialized")
        console.print(f"[dim]Location: {Path(__file__).parent / 'core' / 'alembic'}[/dim]")

        # Show created files
        alembic_dir = Path(__file__).parent / "core" / "alembic"
        if alembic_dir.exists():
            console.print("\n[cyan]Created files:[/cyan]")
            for file in alembic_dir.rglob("*"):
                if file.is_file():
                    console.print(f"  • {file.relative_to(alembic_dir)}")

    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")

    console.print()


def demo_current_state():
    """Demo: Show current migration state"""
    console.print(Panel.fit("📊 Demo 2: Current Migration State", style="bold cyan"))

    try:
        manager = get_migration_manager()

        # Current revision
        current = manager.get_current_revision()
        console.print(f"[cyan]Current Revision:[/cyan] {current or 'None (no migrations applied)'}")

        # Pending migrations
        pending = manager.get_pending_migrations()
        console.print(f"[cyan]Pending Migrations:[/cyan] {len(pending)}")

        if pending:
            for rev in pending:
                console.print(f"  • {rev}")

    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")

    console.print()


def demo_validation():
    """Demo: Validate migration state"""
    console.print(Panel.fit("✅ Demo 3: Validate Migration State", style="bold cyan"))

    try:
        manager = get_migration_manager()
        results = manager.validate_migrations()

        # Create results table
        table = Table(title="Validation Results")
        table.add_column("Check", style="cyan")
        table.add_column("Result", style="white")

        table.add_row("Status", f"[{'green' if results['status'] == 'success' else 'red'}]{results['status']}[/]")
        table.add_row("Current Revision", results["current_revision"] or "None")
        table.add_row("Pending Migrations", str(len(results["pending_migrations"])))
        table.add_row("Errors", str(len(results["errors"])))
        table.add_row("Warnings", str(len(results["warnings"])))

        console.print(table)

        if results["errors"]:
            console.print("\n[red]Errors:[/red]")
            for error in results["errors"]:
                console.print(f"  • {error}")

        if results["warnings"]:
            console.print("\n[yellow]Warnings:[/yellow]")
            for warning in results["warnings"]:
                console.print(f"  • {warning}")

    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")

    console.print()


def demo_templates():
    """Demo: Create migration templates"""
    console.print(Panel.fit("📝 Demo 4: Migration Templates", style="bold cyan"))

    templates = ["add_column", "add_index", "add_table", "add_foreign_key"]

    try:
        manager = get_migration_manager()

        for template_name in templates:
            template_path = manager.create_migration_template(template_name)
            console.print(f"[green]✓[/green] Created template: [cyan]{template_name}[/cyan]")

            # Show template content
            if template_path.exists():
                content = template_path.read_text()
                # Show first few lines
                lines = content.split("\n")[:10]
                syntax = Syntax("\n".join(lines), "python", theme="monokai", line_numbers=True)
                console.print(syntax)
                console.print("[dim]...[/dim]\n")

    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")

    console.print()


def demo_migration_history():
    """Demo: Show migration history"""
    console.print(Panel.fit("📜 Demo 5: Migration History", style="bold cyan"))

    try:
        manager = get_migration_manager()
        history = manager.get_migration_history()

        if not history:
            console.print("[yellow]No migrations found[/yellow]")
        else:
            table = Table(title="Migration History")
            table.add_column("Revision", style="cyan")
            table.add_column("Down Revision", style="dim")
            table.add_column("Message", style="white")
            table.add_column("Status", style="green")

            for entry in history:
                status = "✓ Current" if entry["is_current"] else ""
                table.add_row(
                    entry["revision"][:8],
                    entry["down_revision"][:8] if entry["down_revision"] else "-",
                    entry["message"] or "No message",
                    status,
                )

            console.print(table)

    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")

    console.print()


def demo_usage_examples():
    """Demo: Show usage examples"""
    console.print(Panel.fit("💡 Demo 6: Usage Examples", style="bold cyan"))

    examples = [
        ("Initialize migrations", "from core.migrations import get_migration_manager\nmanager = get_migration_manager()\nmanager.initialize_alembic()"),
        ("Create migration", "from core.migrations import create_migration\ncreate_migration('add_user_table', autogenerate=True)"),
        ("Run migrations", "from core.migrations import migrate\nmigrate()  # Upgrade to head"),
        ("Rollback migration", "from core.migrations import rollback\nrollback('-1')  # Rollback one step"),
        ("Check current state", "manager = get_migration_manager()\ncurrent = manager.get_current_revision()\npending = manager.get_pending_migrations()"),
    ]

    for title, code in examples:
        console.print(f"\n[cyan]{title}:[/cyan]")
        syntax = Syntax(code, "python", theme="monokai")
        console.print(syntax)

    console.print()


def demo_cli_commands():
    """Demo: Show CLI commands"""
    console.print(Panel.fit("🖥️  Demo 7: CLI Commands", style="bold cyan"))

    commands = [
        ("Initialize", "python -m core.cli_migrations init"),
        ("Create migration", "python -m core.cli_migrations create 'add_user_table' --auto"),
        ("Run migrations", "python -m core.cli_migrations upgrade"),
        ("Rollback", "python -m core.cli_migrations downgrade --revision -1"),
        ("Show current", "python -m core.cli_migrations current"),
        ("Show history", "python -m core.cli_migrations history"),
        ("Show pending", "python -m core.cli_migrations pending"),
        ("Validate", "python -m core.cli_migrations validate"),
        ("Create template", "python -m core.cli_migrations template add_column"),
    ]

    table = Table(title="Available CLI Commands")
    table.add_column("Action", style="cyan")
    table.add_column("Command", style="white")

    for action, command in commands:
        table.add_row(action, command)

    console.print(table)
    console.print()


def demo_safety_features():
    """Demo: Show safety features"""
    console.print(Panel.fit("🛡️  Demo 8: Safety Features", style="bold cyan"))

    features = [
        ("Transaction per migration", "Each migration runs in its own transaction for safety"),
        ("Rollback capability", "All migrations can be rolled back with safety checks"),
        ("Production warnings", "Extra confirmation required for production rollbacks"),
        ("Validation", "Comprehensive validation before applying migrations"),
        ("Audit trail", "Complete history of all migrations applied"),
        ("Zero-downtime", "Migrations designed for zero-downtime deployments"),
    ]

    for feature, description in features:
        console.print(f"[green]✓[/green] [cyan]{feature}:[/cyan] {description}")

    console.print()


def main():
    """Run all demos"""
    console.print(Panel.fit(
        "Database Migration System Demo\n"
        "Comprehensive Alembic integration with safety features",
        style="bold white on blue"
    ))
    console.print()

    demos = [
        demo_initialization,
        demo_current_state,
        demo_validation,
        demo_templates,
        demo_migration_history,
        demo_usage_examples,
        demo_cli_commands,
        demo_safety_features,
    ]

    for demo in demos:
        try:
            demo()
        except KeyboardInterrupt:
            console.print("\n[yellow]Demo interrupted[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Demo error: {e}[/red]")
            continue

    console.print(Panel.fit(
        "Demo Complete!\n"
        "Check the created files in core/alembic/",
        style="bold green"
    ))


if __name__ == "__main__":
    main()
