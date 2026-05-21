#!/usr/bin/env python3
"""
Theme Validation CLI Tool

Kommandozeilen-Tool zur Validierung von Theme-Dateien.

Usage:
    python tools/validate_theme.py <theme_file.json>
    python tools/validate_theme.py <theme_file.json> --fix
    python tools/validate_theme.py <theme_file.json> --fix --save
    python tools/validate_theme.py --validate-all
"""

import sys
import argparse
from pathlib import Path
from typing import List
import json

# Füge Parent-Directory zum Path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))

from theming.theme_validator import ThemeValidator, validate_theme_file, ValidationResult


def print_colored(text: str, color: str = 'white') -> None:
    """Gibt farbigen Text aus (falls Terminal unterstützt)"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m'
    }
    
    if sys.stdout.isatty():
        print(f"{colors.get(color, '')}{text}{colors['reset']}")
    else:
        print(text)


def print_validation_result(result: ValidationResult, verbose: bool = False) -> None:
    """Gibt Validierungs-Ergebnis formatiert aus"""
    
    # Summary
    if result.is_valid:
        print_colored("\n✅ THEME IST GÜLTIG!", 'green')
    else:
        print_colored("\n❌ THEME IST UNGÜLTIG!", 'red')
    
    print_colored(f"\nFehler: {len(result.errors)}", 'red' if result.errors else 'white')
    print_colored(f"Warnungen: {len(result.warnings)}", 'yellow' if result.warnings else 'white')
    print_colored(f"Hinweise: {len(result.info)}", 'cyan' if result.info else 'white')
    
    # Fehler
    if result.errors:
        print_colored("\n━━━ FEHLER ━━━", 'red')
        for error in result.errors:
            print_colored(f"  {error}", 'red')
    
    # Warnungen
    if result.warnings and verbose:
        print_colored("\n━━━ WARNUNGEN ━━━", 'yellow')
        for warning in result.warnings:
            print_colored(f"  {warning}", 'yellow')
    
    # Hinweise
    if result.info and verbose:
        print_colored("\n━━━ HINWEISE ━━━", 'cyan')
        for info in result.info:
            print_colored(f"  {info}", 'cyan')
    
    print()


def validate_single_file(filepath: str, fix: bool = False, save: bool = False, verbose: bool = False) -> bool:
    """
    Validiert eine einzelne Theme-Datei.
    
    Returns:
        True wenn Theme gültig ist, sonst False
    """
    print_colored(f"\n{'='*60}", 'cyan')
    print_colored(f"Validiere: {filepath}", 'cyan')
    print_colored(f"{'='*60}", 'cyan')
    
    if not Path(filepath).exists():
        print_colored(f"\n❌ Datei nicht gefunden: {filepath}", 'red')
        return False
    
    result = validate_theme_file(filepath, fix_errors=fix, save_fixed=save)
    print_validation_result(result, verbose)
    
    return result.is_valid


def validate_all_themes(themes_dir: str = "theming/themes", fix: bool = False, save: bool = False, verbose: bool = False) -> None:
    """Validiert alle Theme-Dateien in einem Verzeichnis"""
    themes_path = Path(themes_dir)
    
    if not themes_path.exists():
        print_colored(f"\n❌ Verzeichnis nicht gefunden: {themes_dir}", 'red')
        return
    
    theme_files = list(themes_path.glob("*.json"))
    
    if not theme_files:
        print_colored(f"\n⚠️  Keine Theme-Dateien gefunden in: {themes_dir}", 'yellow')
        return
    
    print_colored(f"\n{'='*60}", 'magenta')
    print_colored(f"Validiere {len(theme_files)} Theme-Dateien", 'magenta')
    print_colored(f"{'='*60}", 'magenta')
    
    results = []
    for theme_file in theme_files:
        is_valid = validate_single_file(str(theme_file), fix, save, verbose)
        results.append((theme_file.name, is_valid))
    
    # Zusammenfassung
    print_colored(f"\n{'='*60}", 'magenta')
    print_colored("ZUSAMMENFASSUNG", 'magenta')
    print_colored(f"{'='*60}", 'magenta')
    
    valid_count = sum(1 for _, is_valid in results if is_valid)
    invalid_count = len(results) - valid_count
    
    for name, is_valid in results:
        status = "✅" if is_valid else "❌"
        color = 'green' if is_valid else 'red'
        print_colored(f"{status} {name}", color)
    
    print_colored(f"\nGültig: {valid_count}/{len(results)}", 'green' if invalid_count == 0 else 'yellow')
    print_colored(f"Ungültig: {invalid_count}/{len(results)}", 'red' if invalid_count > 0 else 'white')
    print()


def create_example_theme(output_path: str = "example_theme.json") -> None:
    """Erstellt eine Beispiel-Theme-Datei"""
    from theming.theme_validator import DEFAULT_THEME_VALUES
    
    example_theme = {
        "name": "example-theme",
        "display_name": "Example Theme",
        **DEFAULT_THEME_VALUES
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(example_theme, f, indent=2, ensure_ascii=False)
    
    print_colored(f"\n✅ Beispiel-Theme erstellt: {output_path}", 'green')


def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(
        description='Theme Validation CLI Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  # Einzelne Datei validieren
  python tools/validate_theme.py theming/themes/shadcn-default.json
  
  # Mit automatischer Fehlerkorrektur
  python tools/validate_theme.py theming/themes/my-theme.json --fix
  
  # Korrigiertes Theme speichern
  python tools/validate_theme.py theming/themes/my-theme.json --fix --save
  
  # Alle Themes validieren
  python tools/validate_theme.py --validate-all
  
  # Alle Themes mit Details validieren
  python tools/validate_theme.py --validate-all --verbose
  
  # Beispiel-Theme erstellen
  python tools/validate_theme.py --create-example
        """
    )
    
    parser.add_argument(
        'theme_file',
        nargs='?',
        help='Pfad zur Theme-JSON-Datei'
    )
    
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Fehlende Properties automatisch mit Defaults auffüllen'
    )
    
    parser.add_argument(
        '--save',
        action='store_true',
        help='Korrigiertes Theme als *_fixed.json speichern (benötigt --fix)'
    )
    
    parser.add_argument(
        '--validate-all',
        action='store_true',
        help='Alle Theme-Dateien im themes/ Verzeichnis validieren'
    )
    
    parser.add_argument(
        '--themes-dir',
        default='theming/themes',
        help='Verzeichnis mit Theme-Dateien (Standard: theming/themes)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Zeige detaillierte Ausgabe mit Warnungen und Hinweisen'
    )
    
    parser.add_argument(
        '--create-example',
        action='store_true',
        help='Erstelle eine Beispiel-Theme-Datei'
    )
    
    parser.add_argument(
        '--output',
        default='example_theme.json',
        help='Ausgabepfad für Beispiel-Theme (Standard: example_theme.json)'
    )
    
    args = parser.parse_args()
    
    # Beispiel-Theme erstellen
    if args.create_example:
        create_example_theme(args.output)
        return 0
    
    # Alle Themes validieren
    if args.validate_all:
        validate_all_themes(args.themes_dir, args.fix, args.save, args.verbose)
        return 0
    
    # Einzelne Datei validieren
    if args.theme_file:
        is_valid = validate_single_file(args.theme_file, args.fix, args.save, args.verbose)
        return 0 if is_valid else 1
    
    # Keine Argumente: Hilfe anzeigen
    parser.print_help()
    return 1


if __name__ == '__main__':
    sys.exit(main())
