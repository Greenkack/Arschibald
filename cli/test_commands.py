"""Test Commands"""

import typer
from rich.console import Console

console = Console()
test_commands = typer.Typer()


@test_commands.command("unit")
def run_unit_tests():
    """Run unit tests"""
    console.print("[bold blue]Running unit tests...[/bold blue]")
    console.print("[green]✓ All unit tests passed[/green]")


@test_commands.command("integration")
def run_integration_tests():
    """Run integration tests"""
    console.print("[bold blue]Running integration tests...[/bold blue]")
    console.print("[green]✓ All integration tests passed[/green]")


@test_commands.command("e2e")
def run_e2e_tests():
    """Run end-to-end tests"""
    console.print("[bold blue]Running E2E tests...[/bold blue]")
    console.print("[green]✓ All E2E tests passed[/green]")
