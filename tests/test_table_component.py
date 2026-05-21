"""
Tests für Table-Komponente

Testet die Funktionalität der shadcn/ui Table-Komponente.
"""

import pytest
import pandas as pd
from components.table import Table, table, override_dataframe_styling
from theming.theme_manager import ThemeManager


@pytest.fixture
def sample_dataframe():
    """Erstellt ein Beispiel-DataFrame für Tests"""
    return pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie', 'Diana'],
        'Age': [25, 30, 35, 28],
        'City': ['Berlin', 'München', 'Hamburg', 'Köln'],
        'Salary': [50000, 60000, 70000, 55000]
    })


@pytest.fixture
def theme_manager():
    """Erstellt einen ThemeManager für Tests"""
    manager = ThemeManager()
    manager.set_theme('shadcn-default')
    return manager


class TestTableComponent:
    """Tests für Table-Komponente"""

    def test_table_initialization(self, theme_manager):
        """Test: Table kann initialisiert werden"""
        table_component = Table(theme_manager=theme_manager)
        assert table_component is not None
        assert table_component.theme_manager == theme_manager

    def test_table_render_basic(self, sample_dataframe, theme_manager):
        """Test: Table kann mit Basis-Parametern gerendert werden"""
        table_component = Table(theme_manager=theme_manager)

        # Sollte ohne Fehler rendern
        result = table_component.render(
            data=sample_dataframe,
            key="test_table_1"
        )

        # Bei sortable=True sollte DataFrame zurückgegeben werden
        assert result is not None
        assert isinstance(result, pd.DataFrame)

    def test_table_render_not_sortable(self, sample_dataframe, theme_manager):
        """Test: Table ohne Sortierung gibt None zurück"""
        table_component = Table(theme_manager=theme_manager)

        result = table_component.render(
            data=sample_dataframe,
            sortable=False,
            key="test_table_2"
        )

        # Bei sortable=False sollte None zurückgegeben werden
        assert result is None

    def test_table_sizes(self, sample_dataframe, theme_manager):
        """Test: Table unterstützt verschiedene Größen"""
        table_component = Table(theme_manager=theme_manager)

        sizes = ['compact', 'default', 'comfortable']

        for size in sizes:
            result = table_component.render(
                data=sample_dataframe,
                size=size,
                key=f"test_table_size_{size}"
            )
            assert result is not None

    def test_table_with_options(self, sample_dataframe, theme_manager):
        """Test: Table mit verschiedenen Optionen"""
        table_component = Table(theme_manager=theme_manager)

        result = table_component.render(
            data=sample_dataframe,
            sortable=True,
            striped=True,
            hover=True,
            bordered=True,
            show_index=True,
            sticky_header=True,
            max_height="400px",
            key="test_table_options"
        )

        assert result is not None

    def test_table_with_custom_css(self, sample_dataframe, theme_manager):
        """Test: Table mit Custom CSS"""
        table_component = Table(theme_manager=theme_manager)

        custom_css = """
        .test-table {
            background: red;
        }
        """

        result = table_component.render(
            data=sample_dataframe,
            custom_css=custom_css,
            key="test_table_custom_css"
        )

        assert result is not None

    def test_table_empty_dataframe(self, theme_manager):
        """Test: Table mit leerem DataFrame"""
        table_component = Table(theme_manager=theme_manager)

        empty_df = pd.DataFrame()

        # Sollte ohne Fehler rendern (auch wenn leer)
        result = table_component.render(
            data=empty_df,
            key="test_table_empty"
        )

        assert result is not None

    def test_table_single_column(self, theme_manager):
        """Test: Table mit nur einer Spalte"""
        table_component = Table(theme_manager=theme_manager)

        single_col_df = pd.DataFrame({'A': [1, 2, 3]})

        result = table_component.render(
            data=single_col_df,
            key="test_table_single_col"
        )

        assert result is not None

    def test_table_single_row(self, theme_manager):
        """Test: Table mit nur einer Zeile"""
        table_component = Table(theme_manager=theme_manager)

        single_row_df = pd.DataFrame({'A': [1], 'B': [2], 'C': [3]})

        result = table_component.render(
            data=single_row_df,
            key="test_table_single_row"
        )

        assert result is not None


class TestTableConvenienceFunction:
    """Tests für table() Convenience-Funktion"""

    def test_table_function(self, sample_dataframe, theme_manager):
        """Test: table() Funktion funktioniert"""
        result = table(
            data=sample_dataframe,
            theme_manager=theme_manager,
            key="test_func_table"
        )

        assert result is not None

    def test_table_function_with_options(
        self, sample_dataframe, theme_manager
    ):
        """Test: table() mit verschiedenen Optionen"""
        result = table(
            data=sample_dataframe,
            sortable=True,
            striped=False,
            hover=True,
            size="compact",
            theme_manager=theme_manager,
            key="test_func_table_options"
        )

        assert result is not None


class TestDataFrameOverride:
    """Tests für override_dataframe_styling()"""

    def test_override_function_exists(self):
        """Test: override_dataframe_styling() Funktion existiert"""
        assert callable(override_dataframe_styling)

    def test_override_function_runs(self, theme_manager):
        """Test: override_dataframe_styling() läuft ohne Fehler"""
        # Sollte ohne Fehler ausführen
        override_dataframe_styling(theme_manager=theme_manager)
        # Test besteht wenn kein Exception geworfen wird
        assert True


class TestTableWithDifferentDataTypes:
    """Tests für Table mit verschiedenen Datentypen"""

    def test_table_with_mixed_types(self, theme_manager):
        """Test: Table mit gemischten Datentypen"""
        mixed_df = pd.DataFrame({
            'Text': ['A', 'B', 'C'],
            'Number': [1, 2, 3],
            'Float': [1.1, 2.2, 3.3],
            'Boolean': [True, False, True]
        })

        table_component = Table(theme_manager=theme_manager)
        result = table_component.render(
            data=mixed_df,
            key="test_mixed_types"
        )

        assert result is not None

    def test_table_with_dates(self, theme_manager):
        """Test: Table mit Datums-Spalten"""
        date_df = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=3),
            'Value': [100, 200, 300]
        })

        table_component = Table(theme_manager=theme_manager)
        result = table_component.render(
            data=date_df,
            key="test_dates"
        )

        assert result is not None

    def test_table_with_nulls(self, theme_manager):
        """Test: Table mit NULL-Werten"""
        null_df = pd.DataFrame({
            'A': [1, None, 3],
            'B': [None, 2, 3],
            'C': [1, 2, None]
        })

        table_component = Table(theme_manager=theme_manager)
        result = table_component.render(
            data=null_df,
            key="test_nulls"
        )

        assert result is not None


class TestTableTokenAccess:
    """Tests für Theme-Token-Zugriff"""

    def test_table_uses_theme_tokens(self, sample_dataframe, theme_manager):
        """Test: Table verwendet Theme-Tokens"""
        table_component = Table(theme_manager=theme_manager)

        # Prüfe ob Tokens abgerufen werden können
        bg = table_component.get_token('colors.background')
        fg = table_component.get_token('colors.foreground')

        assert bg is not None
        assert fg is not None

        # Rendere Table
        result = table_component.render(
            data=sample_dataframe,
            key="test_tokens"
        )

        assert result is not None


class TestTableEdgeCases:
    """Tests für Edge Cases"""

    def test_table_with_very_long_text(self, theme_manager):
        """Test: Table mit sehr langen Texten"""
        long_text_df = pd.DataFrame({
            'Short': ['A', 'B', 'C'],
            'Long': [
                'A' * 100,
                'B' * 100,
                'C' * 100
            ]
        })

        table_component = Table(theme_manager=theme_manager)
        result = table_component.render(
            data=long_text_df,
            key="test_long_text"
        )

        assert result is not None

    def test_table_with_many_columns(self, theme_manager):
        """Test: Table mit vielen Spalten"""
        many_cols_df = pd.DataFrame({
            f'Col_{i}': range(5) for i in range(20)
        })

        table_component = Table(theme_manager=theme_manager)
        result = table_component.render(
            data=many_cols_df,
            key="test_many_cols"
        )

        assert result is not None

    def test_table_with_many_rows(self, theme_manager):
        """Test: Table mit vielen Zeilen"""
        many_rows_df = pd.DataFrame({
            'A': range(1000),
            'B': range(1000, 2000)
        })

        table_component = Table(theme_manager=theme_manager)
        result = table_component.render(
            data=many_rows_df,
            max_height="400px",
            key="test_many_rows"
        )

        assert result is not None

    def test_table_with_special_characters(self, theme_manager):
        """Test: Table mit Sonderzeichen"""
        special_df = pd.DataFrame({
            'Text': ['<script>', '&nbsp;', '"quotes"', "'apostrophe'"],
            'Symbols': ['€', '©', '™', '®']
        })

        table_component = Table(theme_manager=theme_manager)
        result = table_component.render(
            data=special_df,
            key="test_special_chars"
        )

        assert result is not None


def test_table_without_theme_manager(sample_dataframe):
    """Test: Table funktioniert auch ohne expliziten ThemeManager"""
    table_component = Table()

    # Sollte mit Fallback-Werten funktionieren
    _ = table_component.render(
        data=sample_dataframe,
        key="test_no_theme"
    )

    # Kann None sein wenn kein Theme Manager verfügbar
    # Aber sollte nicht crashen
    assert True  # Test besteht wenn kein Exception geworfen wird


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
