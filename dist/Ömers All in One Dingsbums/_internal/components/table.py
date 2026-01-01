"""
shadcn/ui Table-Komponente für Streamlit

Diese Komponente bietet eine moderne Tabelle mit Sorting, Zebra-Striping,
Hover-Effekten und responsivem Design.
"""

from typing import Optional, Dict, Any, Literal
import streamlit as st
import pandas as pd
from .shadcn_base import ShadcnComponent


class Table(ShadcnComponent):
    """
    shadcn/ui Table-Komponente

    Eine flexible Tabellen-Komponente mit modernem Design.

    Features:
    - Zebra-Striping (alternierende Zeilen-Farben)
    - Hover-Effekte für Zeilen
    - Sortierbare Spalten-Header
    - Responsive Design mit horizontalem Scroll
    - Verschiedene Größen (compact, default, comfortable)
    - Optional: Sticky Header
    - Optional: Row Selection

    Example:
        ```python
        from components import Table
        import pandas as pd

        df = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie'],
            'Age': [25, 30, 35],
            'City': ['Berlin', 'München', 'Hamburg']
        })

        table = Table()
        table.render(
            data=df,
            sortable=True,
            striped=True,
            hover=True
        )
        ```
    """

    def render(
        self,
        data: pd.DataFrame,
        sortable: bool = True,
        striped: bool = True,
        hover: bool = True,
        size: Literal["compact", "default", "comfortable"] = "default",
        sticky_header: bool = False,
        max_height: Optional[str] = None,
        bordered: bool = True,
        show_index: bool = False,
        column_config: Optional[Dict[str, Dict[str, Any]]] = None,
        custom_css: Optional[str] = None,
        key: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        Rendert eine Table-Komponente

        Args:
            data: Pandas DataFrame mit den Tabellendaten
            sortable: Ob Spalten sortierbar sein sollen
            striped: Ob Zebra-Striping aktiviert sein soll
            hover: Ob Hover-Effekt für Zeilen aktiviert sein soll
            size: Größe der Tabelle ('compact', 'default', 'comfortable')
            sticky_header: Ob Header beim Scrollen fixiert sein soll
            max_height: Maximale Höhe der Tabelle (z.B. '400px')
            bordered: Ob Tabelle Borders haben soll
            show_index: Ob DataFrame-Index angezeigt werden soll
            column_config: Konfiguration für Spalten (Breite, Alignment)
            custom_css: Zusätzliches Custom-CSS
            key: Eindeutiger Key für die Komponente

        Returns:
            Sortiertes DataFrame wenn sortable=True, sonst None

        Example:
            ```python
            table = Table()
            sorted_df = table.render(
                data=df,
                sortable=True,
                size="comfortable",
                max_height="500px"
            )
            ```
        """
        # Generiere eindeutige ID
        table_id = key or self._generate_unique_id("table")

        # Hole Theme-Tokens
        bg = self.get_token('colors.background', '#ffffff')
        fg = self.get_token('colors.foreground', '#0a0a0a')
        border = self.get_token('colors.border', '#e4e4e7')
        muted = self.get_token('colors.muted', '#f4f4f5')
        primary = self.get_token('colors.primary', '#18181b')
        radius_md = self.get_token('borders.border_radius_md', '0.375rem')
        transition = self.get_token(
            'animations.transition_base',
            '200ms cubic-bezier(0.4, 0, 0.2, 1)'
        )

        # Größen-spezifische Paddings
        size_paddings = {
            'compact': ('0.25rem 0.5rem', '0.5rem'),
            'default': ('0.5rem 0.75rem', '0.75rem'),
            'comfortable': ('0.75rem 1rem', '1rem')
        }
        cell_padding, header_padding = size_paddings[size]

        # Sortierung
        sorted_data = data.copy()
        sort_column = None
        sort_order = 'asc'

        if sortable:
            # Session State für Sortierung
            sort_key = f"table_sort_{table_id}"
            if sort_key not in st.session_state:
                st.session_state[sort_key] = {'column': None, 'order': 'asc'}

            # Sortier-Controls
            cols = st.columns([3, 1, 1])
            with cols[0]:
                sort_column = st.selectbox(
                    "Sortieren nach",
                    options=[None] + list(data.columns),
                    key=f"{table_id}_sort_col",
                    index=0
                )
            with cols[1]:
                sort_order = st.radio(
                    "Reihenfolge",
                    options=['asc', 'desc'],
                    key=f"{table_id}_sort_order",
                    horizontal=True,
                    label_visibility="collapsed"
                )

            # Sortiere Daten
            if sort_column:
                sorted_data = sorted_data.sort_values(
                    by=sort_column,
                    ascending=(sort_order == 'asc')
                )
                st.session_state[sort_key] = {
                    'column': sort_column,
                    'order': sort_order
                }

        # Striping-Farbe
        stripe_color = muted if striped else bg

        # Hover-Farbe
        hover_bg = "rgba(0, 0, 0, 0.02)" if hover else bg

        # Border-Style
        border_style = f"1px solid {border}" if bordered else "none"

        # Max-Height für scrollbare Tabelle
        max_height_style = (
            f"max-height: {max_height};" if max_height else ""
        )
        overflow_style = "overflow-y: auto;" if max_height else ""

        # Sticky Header Style
        sticky_style = (
            "position: sticky; top: 0; z-index: 10;"
            if sticky_header else ""
        )

        # CSS für Table
        table_css = f"""
        <style>
        .shadcn-table-wrapper-{table_id} {{
            width: 100%;
            {max_height_style}
            {overflow_style}
            border-radius: {radius_md};
            border: {border_style};
            overflow-x: auto;
        }}

        .shadcn-table-{table_id} {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.875rem;
            background: {bg};
            color: {fg};
        }}

        .shadcn-table-{table_id} thead {{
            {sticky_style}
            background: {muted};
        }}

        .shadcn-table-{table_id} th {{
            padding: {header_padding};
            text-align: left;
            font-weight: 600;
            color: {fg};
            border-bottom: 2px solid {border};
            white-space: nowrap;
        }}

        .shadcn-table-{table_id} td {{
            padding: {cell_padding};
            border-bottom: 1px solid {border};
        }}

        .shadcn-table-{table_id} tbody tr:nth-child(even) {{
            background: {stripe_color};
        }}

        .shadcn-table-{table_id} tbody tr:hover {{
            background: {hover_bg};
            transition: background {transition};
        }}

        .shadcn-table-{table_id} tbody tr:last-child td {{
            border-bottom: none;
        }}

        /* Responsive: Horizontal Scroll auf kleinen Bildschirmen */
        @media (max-width: 768px) {{
            .shadcn-table-wrapper-{table_id} {{
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }}

            .shadcn-table-{table_id} {{
                min-width: 600px;
            }}
        }}

        /* Sortierbare Spalten-Header */
        .shadcn-table-{table_id} th.sortable {{
            cursor: pointer;
            user-select: none;
        }}

        .shadcn-table-{table_id} th.sortable:hover {{
            background: {border};
        }}

        .shadcn-table-{table_id} th.sorted {{
            color: {primary};
        }}

        {custom_css or ''}
        </style>
        """

        # Injiziere CSS
        st.markdown(table_css, unsafe_allow_html=True)

        # Baue HTML-Tabelle
        html_parts = [f'<div class="shadcn-table-wrapper-{table_id}">']
        html_parts.append(f'<table class="shadcn-table-{table_id}">')

        # Header
        html_parts.append('<thead><tr>')
        if show_index:
            html_parts.append('<th>Index</th>')

        for col in sorted_data.columns:
            sortable_class = 'sortable' if sortable else ''
            sorted_class = 'sorted' if sort_column == col else ''
            html_parts.append(
                f'<th class="{sortable_class} {sorted_class}">{col}</th>'
            )
        html_parts.append('</tr></thead>')

        # Body
        html_parts.append('<tbody>')
        for idx, row in sorted_data.iterrows():
            html_parts.append('<tr>')

            if show_index:
                html_parts.append(f'<td>{idx}</td>')

            for col in sorted_data.columns:
                value = row[col]

                # Formatierung basierend auf column_config
                if column_config and col in column_config:
                    config = column_config[col]
                    if 'format' in config:
                        value = config['format'](value)

                html_parts.append(f'<td>{value}</td>')

            html_parts.append('</tr>')
        html_parts.append('</tbody>')

        html_parts.append('</table>')
        html_parts.append('</div>')

        # Rendere HTML
        html = ''.join(html_parts)
        st.markdown(html, unsafe_allow_html=True)

        # Rückgabe sortiertes DataFrame
        return sorted_data if sortable else None


def table(
    data: pd.DataFrame,
    sortable: bool = True,
    striped: bool = True,
    hover: bool = True,
    size: Literal["compact", "default", "comfortable"] = "default",
    sticky_header: bool = False,
    max_height: Optional[str] = None,
    bordered: bool = True,
    show_index: bool = False,
    column_config: Optional[Dict[str, Dict[str, Any]]] = None,
    custom_css: Optional[str] = None,
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> Optional[pd.DataFrame]:
    """
    Convenience-Funktion zum Rendern einer Table

    Dies ist eine Shortcut-Funktion, die eine Table-Instanz erstellt
    und rendert.

    Args:
        Siehe Table.render() für Parameter-Dokumentation

    Returns:
        Sortiertes DataFrame wenn sortable=True, sonst None

    Example:
        ```python
        from components.table import table
        import pandas as pd

        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        sorted_df = table(data=df, sortable=True, striped=True)
        ```
    """
    table_component = Table(theme_manager=theme_manager)
    return table_component.render(
        data=data,
        sortable=sortable,
        striped=striped,
        hover=hover,
        size=size,
        sticky_header=sticky_header,
        max_height=max_height,
        bordered=bordered,
        show_index=show_index,
        column_config=column_config,
        custom_css=custom_css,
        key=key
    )


def override_dataframe_styling(theme_manager: Optional[Any] = None) -> None:
    """
    Überschreibt das Standard-Styling von st.dataframe()

    Diese Funktion injiziert globales CSS, das das Aussehen von
    st.dataframe() im shadcn/ui-Stil anpasst.

    Args:
        theme_manager: ThemeManager-Instanz für Token-Zugriff

    Example:
        ```python
        from components.table import override_dataframe_styling

        # Am Anfang der App aufrufen
        override_dataframe_styling()

        # Danach haben alle st.dataframe() shadcn/ui-Styling
        st.dataframe(df)
        ```
    """
    # Erstelle temporäre Komponente für Token-Zugriff
    temp_component = Table(theme_manager=theme_manager)

    # Hole Theme-Tokens
    bg = temp_component.get_token('colors.background', '#ffffff')
    fg = temp_component.get_token('colors.foreground', '#0a0a0a')
    border = temp_component.get_token('colors.border', '#e4e4e7')
    muted = temp_component.get_token('colors.muted', '#f4f4f5')
    radius_md = temp_component.get_token(
        'borders.border_radius_md',
        '0.375rem'
    )
    transition = temp_component.get_token(
        'animations.transition_base',
        '200ms cubic-bezier(0.4, 0, 0.2, 1)'
    )

    # Globales CSS für st.dataframe()
    dataframe_css = f"""
    <style>
    /* Streamlit DataFrame Styling Override */
    div[data-testid="stDataFrame"] {{
        border-radius: {radius_md};
        border: 1px solid {border};
        overflow: hidden;
    }}

    div[data-testid="stDataFrame"] table {{
        font-size: 0.875rem;
        background: {bg};
        color: {fg};
    }}

    div[data-testid="stDataFrame"] thead {{
        background: {muted};
    }}

    div[data-testid="stDataFrame"] th {{
        font-weight: 600;
        padding: 0.75rem;
        border-bottom: 2px solid {border};
    }}

    div[data-testid="stDataFrame"] td {{
        padding: 0.5rem 0.75rem;
        border-bottom: 1px solid {border};
    }}

    div[data-testid="stDataFrame"] tbody tr:nth-child(even) {{
        background: {muted};
    }}

    div[data-testid="stDataFrame"] tbody tr:hover {{
        background: rgba(0, 0, 0, 0.02);
        transition: background {transition};
    }}
    </style>
    """

    st.markdown(dataframe_css, unsafe_allow_html=True)
