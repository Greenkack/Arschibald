"""
Demo für shadcn/ui Table-Komponente

Zeigt alle Features der Table-Komponente.
"""

import streamlit as st
import pandas as pd
import numpy as np
from components.table import Table, table, override_dataframe_styling
from theming.theme_manager import ThemeManager


def main():
    st.set_page_config(
        page_title="shadcn/ui Table Demo",
        page_icon="",
        layout="wide"
    )

    st.title(" shadcn/ui Table-Komponente Demo")
    st.markdown("---")

    # Theme Manager initialisieren
    if 'theme_manager' not in st.session_state:
        st.session_state.theme_manager = ThemeManager()
        st.session_state.theme_manager.set_theme('shadcn-default')

    theme_manager = st.session_state.theme_manager

    # Beispiel-Daten erstellen
    @st.cache_data
    def create_sample_data():
        np.random.seed(42)
        return pd.DataFrame({
            'Name': [
                'Alice Schmidt', 'Bob Müller', 'Charlie Weber',
                'Diana Fischer', 'Erik Wagner', 'Fiona Becker',
                'Georg Hoffmann', 'Hannah Schulz', 'Ivan Koch'
            ],
            'Alter': np.random.randint(25, 65, 9),
            'Stadt': [
                'Berlin', 'München', 'Hamburg', 'Köln', 'Frankfurt',
                'Stuttgart', 'Düsseldorf', 'Dortmund', 'Essen'
            ],
            'Gehalt': np.random.randint(40000, 120000, 9),
            'Abteilung': [
                'IT', 'Marketing', 'Vertrieb', 'IT', 'HR',
                'Marketing', 'Vertrieb', 'IT', 'HR'
            ],
            'Bewertung': np.round(np.random.uniform(3.0, 5.0, 9), 1)
        })

    df = create_sample_data()

    # Sidebar für Optionen
    with st.sidebar:
        st.header(" Table-Optionen")

        sortable = st.checkbox("Sortierbar", value=True)
        striped = st.checkbox("Zebra-Striping", value=True)
        hover = st.checkbox("Hover-Effekt", value=True)
        bordered = st.checkbox("Borders", value=True)
        show_index = st.checkbox("Index anzeigen", value=False)
        sticky_header = st.checkbox("Sticky Header", value=False)

        size = st.selectbox(
            "Größe",
            options=["compact", "default", "comfortable"],
            index=1
        )

        use_max_height = st.checkbox("Max. Höhe setzen", value=False)
        max_height = None
        if use_max_height:
            max_height = st.slider(
                "Max. Höhe (px)",
                min_value=200,
                max_value=800,
                value=400,
                step=50
            )
            max_height = f"{max_height}px"

    # Demo 1: Basis-Tabelle
    st.header("1⃣ Basis-Tabelle")
    st.markdown("Einfache Tabelle mit allen Standard-Features")

    table_component = Table(theme_manager=theme_manager)
    sorted_df = table_component.render(
        data=df,
        sortable=sortable,
        striped=striped,
        hover=hover,
        size=size,
        sticky_header=sticky_header,
        max_height=max_height,
        bordered=bordered,
        show_index=show_index,
        key="demo_table_1"
    )

    if sorted_df is not None and sortable:
        st.info(f" Tabelle wurde sortiert. Zeige {len(sorted_df)} Zeilen.")

    st.markdown("---")

    # Demo 2: Convenience-Funktion
    st.header("2⃣ Convenience-Funktion")
    st.markdown("Verwendung der `table()` Shortcut-Funktion")

    with st.expander("Code anzeigen"):
        st.code("""
from components.table import table

table(
    data=df,
    sortable=True,
    striped=True,
    hover=True,
    size="comfortable"
)
        """, language="python")

    table(
        data=df.head(5),
        sortable=False,
        striped=True,
        hover=True,
        size="comfortable",
        theme_manager=theme_manager,
        key="demo_table_2"
    )

    st.markdown("---")

    # Demo 3: Kompakte Tabelle
    st.header("3⃣ Kompakte Tabelle")
    st.markdown("Platzsparende Darstellung für viele Daten")

    table(
        data=df,
        sortable=True,
        striped=True,
        hover=True,
        size="compact",
        max_height="300px",
        theme_manager=theme_manager,
        key="demo_table_3"
    )

    st.markdown("---")

    # Demo 4: Große Tabelle mit Sticky Header
    st.header("4⃣ Scrollbare Tabelle mit Sticky Header")
    st.markdown("Header bleibt beim Scrollen sichtbar")

    # Erstelle größere Tabelle
    large_df = pd.concat([df] * 5, ignore_index=True)

    table(
        data=large_df,
        sortable=True,
        striped=True,
        hover=True,
        size="default",
        sticky_header=True,
        max_height="400px",
        theme_manager=theme_manager,
        key="demo_table_4"
    )

    st.markdown("---")

    # Demo 5: Custom CSS
    st.header("5⃣ Tabelle mit Custom CSS")
    st.markdown("Angepasstes Styling mit zusätzlichem CSS")

    custom_css = """
    .shadcn-table-demo_table_5 tbody tr:hover {
        background: #fef3c7 !important;
        transform: scale(1.01);
    }

    .shadcn-table-demo_table_5 th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    """

    table(
        data=df.head(5),
        sortable=False,
        striped=False,
        hover=True,
        size="default",
        custom_css=custom_css,
        theme_manager=theme_manager,
        key="demo_table_5"
    )

    st.markdown("---")

    # Demo 6: st.dataframe() Override
    st.header("6⃣ st.dataframe() mit shadcn/ui-Styling")
    st.markdown("Standard Streamlit DataFrame mit überschriebenem Styling")

    # Override aktivieren
    override_dataframe_styling(theme_manager=theme_manager)

    st.dataframe(df, use_container_width=True)

    st.markdown("---")

    # Demo 7: Verschiedene Datentypen
    st.header("7⃣ Verschiedene Datentypen")
    st.markdown("Tabelle mit verschiedenen Spaltentypen")

    mixed_df = pd.DataFrame({
        'Text': ['Alpha', 'Beta', 'Gamma', 'Delta'],
        'Zahl': [100, 200, 300, 400],
        'Float': [1.23, 4.56, 7.89, 10.11],
        'Boolean': [True, False, True, False],
        'Datum': pd.date_range('2024-01-01', periods=4)
    })

    table(
        data=mixed_df,
        sortable=True,
        striped=True,
        hover=True,
        size="default",
        show_index=True,
        theme_manager=theme_manager,
        key="demo_table_7"
    )

    st.markdown("---")

    # Demo 8: Responsive Design
    st.header("8⃣ Responsive Design")
    st.markdown(
        "Tabelle passt sich an Bildschirmgröße an (horizontal "
        "scrollbar auf kleinen Bildschirmen)"
    )

    wide_df = pd.DataFrame({
        f'Spalte_{i}': np.random.randint(0, 100, 5)
        for i in range(1, 11)
    })

    table(
        data=wide_df,
        sortable=True,
        striped=True,
        hover=True,
        size="default",
        theme_manager=theme_manager,
        key="demo_table_8"
    )

    st.markdown("---")

    # Statistiken
    st.header(" Tabellen-Statistiken")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Zeilen", len(df))

    with col2:
        st.metric("Spalten", len(df.columns))

    with col3:
        st.metric("Gesamt-Zellen", len(df) * len(df.columns))

    with col4:
        memory_kb = df.memory_usage(deep=True).sum() / 1024
        st.metric("Speicher", f"{memory_kb:.1f} KB")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        ** Tipp:** Die Table-Komponente unterstützt:
        -  Zebra-Striping für bessere Lesbarkeit
        -  Hover-Effekte für interaktive Erfahrung
        -  Sortierbare Spalten
        -  Responsive Design mit horizontalem Scroll
        -  Sticky Header für lange Tabellen
        -  Verschiedene Größen (compact, default, comfortable)
        -  Custom CSS für individuelle Anpassungen
        """
    )


if __name__ == "__main__":
    main()
