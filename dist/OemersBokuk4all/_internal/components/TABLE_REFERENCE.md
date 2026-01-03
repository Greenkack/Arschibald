# Table Component - Vollständige Referenz

## Übersicht

Die `Table`-Komponente bietet eine moderne, shadcn/ui-gestylte Tabelle für Streamlit mit umfangreichen Features wie Sortierung, Zebra-Striping, Hover-Effekten und responsivem Design.

## Features

- ✅ **Zebra-Striping**: Alternierende Zeilen-Farben für bessere Lesbarkeit
- ✅ **Hover-Effekte**: Interaktive Zeilen-Hervorhebung
- ✅ **Sortierbare Spalten**: Einfache Sortierung nach beliebigen Spalten
- ✅ **Responsive Design**: Automatischer horizontaler Scroll auf kleinen Bildschirmen
- ✅ **Sticky Header**: Header bleibt beim Scrollen sichtbar
- ✅ **Verschiedene Größen**: compact, default, comfortable
- ✅ **Custom CSS**: Vollständig anpassbar
- ✅ **st.dataframe() Override**: Globales Styling für Standard-DataFrames

## Installation

```python
from components.table import Table, table, override_dataframe_styling
```

## Basis-Verwendung

### Klassen-basiert

```python
import pandas as pd
from components.table import Table

# Daten erstellen
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'City': ['Berlin', 'München', 'Hamburg']
})

# Table-Instanz erstellen
table_component = Table()

# Tabelle rendern
sorted_df = table_component.render(
    data=df,
    sortable=True,
    striped=True,
    hover=True
)
```

### Funktions-basiert (Shortcut)

```python
from components.table import table

# Direkt rendern
sorted_df = table(
    data=df,
    sortable=True,
    striped=True,
    hover=True
)
```

## API-Referenz

### Table.render()

```python
def render(
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
) -> Optional[pd.DataFrame]
```

#### Parameter

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| `data` | `pd.DataFrame` | **Required** | Pandas DataFrame mit Tabellendaten |
| `sortable` | `bool` | `True` | Aktiviert Sortier-Controls |
| `striped` | `bool` | `True` | Aktiviert Zebra-Striping |
| `hover` | `bool` | `True` | Aktiviert Hover-Effekt |
| `size` | `Literal` | `"default"` | Größe: `"compact"`, `"default"`, `"comfortable"` |
| `sticky_header` | `bool` | `False` | Header bleibt beim Scrollen fixiert |
| `max_height` | `Optional[str]` | `None` | Max. Höhe (z.B. `"400px"`) |
| `bordered` | `bool` | `True` | Zeigt Borders an |
| `show_index` | `bool` | `False` | Zeigt DataFrame-Index an |
| `column_config` | `Optional[Dict]` | `None` | Spalten-Konfiguration |
| `custom_css` | `Optional[str]` | `None` | Zusätzliches CSS |
| `key` | `Optional[str]` | `None` | Eindeutiger Komponenten-Key |

#### Rückgabewert

- `pd.DataFrame` wenn `sortable=True` (sortiertes DataFrame)
- `None` wenn `sortable=False`

## Beispiele

### 1. Einfache Tabelle

```python
import pandas as pd
from components.table import table

df = pd.DataFrame({
    'Produkt': ['Solar Panel A', 'Solar Panel B', 'Wechselrichter'],
    'Preis': [299.99, 349.99, 599.99],
    'Lager': [50, 30, 20]
})

table(data=df)
```

### 2. Sortierbare Tabelle

```python
sorted_df = table(
    data=df,
    sortable=True,
    size="comfortable"
)

if sorted_df is not None:
    st.write(f"Sortiert nach: {sorted_df.columns[0]}")
```

### 3. Kompakte Tabelle mit Scroll

```python
table(
    data=large_df,
    size="compact",
    max_height="300px",
    sticky_header=True
)
```

### 4. Tabelle ohne Striping

```python
table(
    data=df,
    striped=False,
    hover=True,
    bordered=False
)
```

### 5. Tabelle mit Index

```python
table(
    data=df,
    show_index=True,
    sortable=True
)
```

### 6. Custom CSS

```python
custom_css = """
.shadcn-table-my_table tbody tr:hover {
    background: #fef3c7 !important;
}

.shadcn-table-my_table th {
    background: #3b82f6;
    color: white !important;
}
"""

table(
    data=df,
    custom_css=custom_css,
    key="my_table"
)
```

### 7. st.dataframe() Override

```python
from components.table import override_dataframe_styling

# Am Anfang der App aufrufen
override_dataframe_styling()

# Alle st.dataframe() haben jetzt shadcn/ui-Styling
st.dataframe(df)
st.dataframe(another_df)
```

## Größen-Vergleich

### Compact
- **Cell Padding**: `0.25rem 0.5rem`
- **Header Padding**: `0.5rem`
- **Verwendung**: Viele Daten auf wenig Platz

### Default
- **Cell Padding**: `0.5rem 0.75rem`
- **Header Padding**: `0.75rem`
- **Verwendung**: Standard-Anwendungsfälle

### Comfortable
- **Cell Padding**: `0.75rem 1rem`
- **Header Padding**: `1rem`
- **Verwendung**: Bessere Lesbarkeit, weniger Daten

## Responsive Design

Die Tabelle ist vollständig responsive:

- **Desktop**: Volle Breite, alle Spalten sichtbar
- **Tablet**: Horizontaler Scroll bei Bedarf
- **Mobile**: Automatischer horizontaler Scroll, min-width: 600px

```python
# Breite Tabelle - scrollt automatisch auf kleinen Bildschirmen
wide_df = pd.DataFrame({
    f'Spalte_{i}': range(10) for i in range(1, 15)
})

table(data=wide_df)
```

## Sticky Header

Für lange Tabellen mit vielen Zeilen:

```python
table(
    data=long_df,
    sticky_header=True,
    max_height="500px"
)
```

Der Header bleibt beim Scrollen am oberen Rand fixiert.

## Sortierung

### Automatische Sortierung

```python
sorted_df = table(
    data=df,
    sortable=True
)

# sorted_df enthält die sortierten Daten
if sorted_df is not None:
    # Weiterverarbeitung mit sortierten Daten
    st.write(sorted_df.head())
```

### Sortier-State

Die Sortierung wird im Session State gespeichert:

```python
# Zugriff auf Sortier-State
sort_state = st.session_state.get(f"table_sort_{key}")
if sort_state:
    st.write(f"Sortiert nach: {sort_state['column']}")
    st.write(f"Reihenfolge: {sort_state['order']}")
```

## Column Configuration

```python
column_config = {
    'Preis': {
        'format': lambda x: f"€ {x:,.2f}"
    },
    'Datum': {
        'format': lambda x: x.strftime('%d.%m.%Y')
    }
}

table(
    data=df,
    column_config=column_config
)
```

## Theme-Integration

Die Tabelle verwendet automatisch das aktuelle Theme:

```python
from theming.theme_manager import ThemeManager

# Theme Manager initialisieren
theme_manager = ThemeManager()
theme_manager.set_theme('shadcn-dark')

# Tabelle verwendet automatisch Dark Theme
table(data=df, theme_manager=theme_manager)
```

## Performance-Tipps

### 1. Große Datensätze

```python
# Verwende max_height für bessere Performance
table(
    data=large_df,
    max_height="400px",
    size="compact"
)
```

### 2. Caching

```python
@st.cache_data
def load_data():
    return pd.read_csv('large_file.csv')

df = load_data()
table(data=df)
```

### 3. Pagination

```python
# Manuelle Pagination für sehr große Datensätze
page_size = 50
page = st.number_input('Seite', min_value=1, max_value=len(df)//page_size + 1)

start_idx = (page - 1) * page_size
end_idx = start_idx + page_size

table(data=df.iloc[start_idx:end_idx])
```

## Styling-Anpassungen

### Farben ändern

```python
custom_css = """
.shadcn-table-my_table {
    background: #f0f9ff;
}

.shadcn-table-my_table thead {
    background: #0ea5e9;
}

.shadcn-table-my_table th {
    color: white !important;
}
"""

table(data=df, custom_css=custom_css, key="my_table")
```

### Borders anpassen

```python
custom_css = """
.shadcn-table-my_table {
    border: 2px solid #3b82f6;
    border-radius: 0.75rem;
}

.shadcn-table-my_table td {
    border-bottom: 1px dashed #cbd5e1;
}
"""

table(data=df, custom_css=custom_css, key="my_table")
```

### Hover-Effekt anpassen

```python
custom_css = """
.shadcn-table-my_table tbody tr:hover {
    background: linear-gradient(90deg, #fef3c7 0%, #fde68a 100%);
    transform: translateX(5px);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
"""

table(data=df, custom_css=custom_css, key="my_table")
```

## Accessibility

Die Tabelle ist barrierefrei:

- ✅ Semantisches HTML (`<table>`, `<thead>`, `<tbody>`)
- ✅ Ausreichender Kontrast (WCAG AA)
- ✅ Keyboard-Navigation
- ✅ Screen-Reader-freundlich

## Browser-Kompatibilität

- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari
- ✅ Mobile Browser

## Bekannte Einschränkungen

1. **Sortierung**: Nur clientseitig, nicht für sehr große Datensätze (>10.000 Zeilen) geeignet
2. **Filtering**: Nicht eingebaut, muss manuell implementiert werden
3. **Inline-Editing**: Nicht unterstützt
4. **Row Selection**: Nicht eingebaut

## Troubleshooting

### Tabelle wird nicht angezeigt

```python
# Stelle sicher, dass Theme Manager initialisiert ist
if 'theme_manager' not in st.session_state:
    from theming.theme_manager import ThemeManager
    st.session_state.theme_manager = ThemeManager()
    st.session_state.theme_manager.set_theme('shadcn-default')
```

### Sortierung funktioniert nicht

```python
# Stelle sicher, dass ein eindeutiger Key verwendet wird
table(data=df, sortable=True, key="unique_table_key")
```

### Custom CSS wird nicht angewendet

```python
# Verwende !important für höhere Spezifität
custom_css = """
.shadcn-table-my_table tbody tr:hover {
    background: red !important;
}
"""
```

## Weitere Ressourcen

- [shadcn/ui Dokumentation](https://ui.shadcn.com/)
- [Pandas DataFrame Dokumentation](https://pandas.pydata.org/docs/)
- [Streamlit Dokumentation](https://docs.streamlit.io/)

## Changelog

### Version 1.0.0
- ✅ Initiale Implementierung
- ✅ Zebra-Striping
- ✅ Hover-Effekte
- ✅ Sortierbare Spalten
- ✅ Responsive Design
- ✅ Sticky Header
- ✅ st.dataframe() Override
