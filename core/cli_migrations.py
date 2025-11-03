"""CLI Commands for Database Migrations"""

import sys
from pathlib import Path

try:
    import typer
    from rich.console import Console
    from rich.table import Table
except ImportError:
    print("Error: typer and rich are required for CLI. Install with: pip install typer rich")
    sys.exit(1)

from .migrations import get_migration_manager

app = typer.Typer(help="Database migration management commands")
console = Console()


@app.command("init")
def init_migrations():
    """Initialize Alembic migration environment"""
    try:
        manager = get_migration_manager()
        manager.initialize_alembic()
        console.print("[green]✓[/green] Migration environment initialized successfully")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to initialize migrations: {e}")
        raise typer.Exit(1)


@app.command("create")
def create_migration(
    message: str = typer.Argument(..., help="Migration description"),
    autogenerate: bool = typer.Option(True, "--auto/--manual", help="Auto-generate from model changes"),
):
    """Create a new migration"""
    try:
        manager = get_migration_manager()
        revision = manager.create_migration(message, autogenerate)
        console.print(f"[green]✓[/green] Migration created: {revision}")
        console.print(f"[dim]Message: {message}[/dim]")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to create migration: {e}")
        raise typer.Exit(1)


@app.command("upgrade")
def upgrade_database(
    revision: str = typer.Option("head", "--revision", "-r", help="Target revision"),
):
    """Run pending migrations"""
    try:
        manager = get_migration_manager()

        # Show pending migrations
        pending = manager.get_pending_migrations()
        if not pending:
            console.print("[yellow]No pending migrations[/yellow]")
            return

        console.print(f"[cyan]Applying {len(pending)} migration(s)...[/cyan]")

        manager.run_migrations(revision)
        console.print("[green]✓[/green] Migrations applied successfully")

    except Exception as e:
        console.print(f"[red]✗[/red] Migration failed: {e}")
        raise typer.Exit(1)


@app.command("downgrade")
def downgrade_database(
    revision: str = typer.Option("-1", "--revision", "-r", help="Target revision"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Rollback migrations"""
    try:
        manager = get_migration_manager()
        current = manager.get_current_revision()

        if not force:
            console.print(f"[yellow]⚠[/yellow]  Current revision: {current}")
            console.print(f"[yellow]⚠[/yellow]  Target revision: {revision}")

            confirm = typer.confirm("Are you sure you want to rollback?")
            if not confirm:
                console.print("[dim]Rollback cancelled[/dim]")
                raise typer.Exit(0)

        manager.rollback_migration(revision)
        console.print("[green]✓[/green] Rollback completed successfully")

    except Exception as e:
        console.print(f"[red]✗[/red] Rollback failed: {e}")
        raise typer.Exit(1)


@app.command("current")
def show_current():
    """Show current migration revision"""
    try:
        manager = get_migration_manager()
        current = manager.get_current_revision()

        if current:
            console.print(f"[green]Current revision:[/green] {current}")
        else:
            console.print("[yellow]No migrations applied yet[/yellow]")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to get current revision: {e}")
        raise typer.Exit(1)


@app.command("history")
def show_history():
    """Show migration history"""
    try:
        manager = get_migration_manager()
        history = manager.get_migration_history()

        if not history:
            console.print("[yellow]No migrations found[/yellow]")
            return

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
                status
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to get history: {e}")
        raise typer.Exit(1)


@app.command("pending")
def show_pending():
    """Show pending migrations"""
    try:
        manager = get_migration_manager()
        pending = manager.get_pending_migrations()

        if not pending:
            console.print("[green]✓[/green] No pending migrations")
            return

        console.print(f"[yellow]⚠[/yellow]  {len(pending)} pending migration(s):")
        for rev in pending:
            console.print(f"  • {rev}")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to get pending migrations: {e}")
        raise typer.Exit(1)


@app.command("validate")
def validate_migrations():
    """Validate migration state"""
    try:
        manager = get_migration_manager()
        results = manager.validate_migrations()

        console.print("[cyan]Migration Validation Results[/cyan]")
        console.print(f"Status: [{'green' if results['status'] == 'success' else 'red'}]{results['status']}[/]")
        console.print(f"Current Revision: {results['current_revision'] or 'None'}")
        console.print(f"Pending Migrations: {len(results['pending_migrations'])}")

        if results["errors"]:
            console.print("\n[red]Errors:[/red]")
            for error in results["errors"]:
                console.print(f"  • {error}")

        if results["warnings"]:
            console.print("\n[yellow]Warnings:[/yellow]")
            for warning in results["warnings"]:
                console.print(f"  • {warning}")

        if results["status"] == "success" and not results["warnings"]:
            console.print("\n[green]✓[/green] All validations passed")

    except Exception as e:
        console.print(f"[red]✗[/red] Validation failed: {e}")
        raise typer.Exit(1)


@app.command("template")
def create_template(
    template_name: str = typer.Argument(..., help="Template name (add_column, add_index, add_table, add_foreign_key)"),
):
    """Create migration template for common operations"""
    try:
        manager = get_migration_manager()
        template_path = manager.create_migration_template(template_name)
        console.print(f"[green]✓[/green] Template created: {template_path}")
        console.print("[dim]Copy and modify this template for your migration[/dim]")

    except ValueError as e:
        console.print(f"[red]✗[/red] {e}")
        console.print("\n[cyan]Available templates:[/cyan]")
        console.print("  • add_column")
        console.print("  • add_index")
        console.print("  • add_table")
        console.print("  • add_foreign_key")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to create template: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
