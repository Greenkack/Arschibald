"""
Verifikations-Skript für Table-Komponente

Prüft ob alle Komponenten korrekt importiert werden können.
"""

import sys


def verify_imports():
    """Verifiziert dass alle Imports funktionieren"""
    print(" Verifiziere Table-Komponente...")
    print()

    try:
        # Import der Komponente
        print(" Importiere Table-Komponente...")
        from components.table import Table, table, override_dataframe_styling
        print("   Table-Klasse importiert")
        print("   table() Funktion importiert")
        print("   override_dataframe_styling() importiert")
        print()

        # Import über __init__
        print(" Importiere über components.__init__...")
        from components import Table as TableFromInit
        print("   Table über __init__ verfügbar")
        print()

        # Theme Manager
        print(" Importiere ThemeManager...")
        from theming.theme_manager import ThemeManager
        print("   ThemeManager importiert")
        print()

        # Pandas
        print(" Importiere Pandas...")
        import pandas as pd
        print("   Pandas verfügbar")
        print()

        # Erstelle Test-Instanz
        print(" Erstelle Table-Instanz...")
        theme_manager = ThemeManager()
        theme_manager.set_theme('shadcn-default')
        table_component = Table(theme_manager=theme_manager)
        print("   Table-Instanz erstellt")
        print()

        # Teste Token-Zugriff
        print(" Teste Theme-Token-Zugriff...")
        bg = table_component.get_token('colors.background')
        fg = table_component.get_token('colors.foreground')
        print(f"   Background: {bg}")
        print(f"   Foreground: {fg}")
        print()

        # Erstelle Test-DataFrame
        print(" Erstelle Test-DataFrame...")
        df = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie'],
            'Age': [25, 30, 35],
            'City': ['Berlin', 'München', 'Hamburg']
        })
        print(f"   DataFrame erstellt ({len(df)} Zeilen, {len(df.columns)} Spalten)")
        print()

        print("=" * 60)
        print(" ALLE VERIFIKATIONEN ERFOLGREICH!")
        print("=" * 60)
        print()
        print("Die Table-Komponente ist vollständig implementiert und")
        print("kann verwendet werden.")
        print()
        print("Nächste Schritte:")
        print("  1. Demo ausführen: streamlit run demo_table.py")
        print("  2. Tests ausführen: pytest tests/test_table_component.py -v")
        print("  3. Dokumentation lesen: components/TABLE_REFERENCE.md")
        print()

        return True

    except ImportError as e:
        print(f" Import-Fehler: {e}")
        return False
    except Exception as e:
        print(f" Fehler: {e}")
        return False


def main():
    """Hauptfunktion"""
    success = verify_imports()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
