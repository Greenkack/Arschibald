# Table Component - Quick Reference

## Import

```python
from components.table import Table, table, override_dataframe_styling
```

## Schnellstart

```python
import pandas as pd
from components.table import table

df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35]
})

# Einfachste Verwendung
table(data=df)
```

## Häufige Verwendungen

### Sortierbare Tabelle

```python
sorted_df = table(data=df, sortable=True)
```

### Kompakte Tabelle

```python
table(data=df, size="compact")
```

### Scrollbare Tabelle

```python
table(data=df, max_height="400px", sticky_header=True)
```

### Ohne Striping

```python
table(data=df, striped=False)
```

### Mit Index

```python
table(data=df, show_index=True)
```

### Custom Styling

```python
custom_css = """
.shadcn-table-my_table tbody tr:hover {
    background: #fef3c7 !important;
}
"""

table(data=df, custom_css=custom_css, key="my_table")
```

### st.dataframe() Override

```python
# Am Anfang der App
override_dataframe_styling()

# Alle st.dataframe() haben jetzt shadcn/ui-Styling
st.dataframe(df)
```

## Parameter-Übersicht

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| `data` | `DataFrame` | **Required** | Tabellendaten |
| `sortable` | `bool` | `True` | Sortierung aktivieren |
| `striped` | `bool` | `True` | Zebra-Striping |
| `hover` | `bool` | `True` | Hover-Effekt |
| `size` | `str` | `"default"` | `"compact"`, `"default"`, `"comfortable"` |
| `sticky_header` | `bool` | `False` | Fixierter Header |
| `max_height` | `str` | `None` | z.B. `"400px"` |
| `bordered` | `bool` | `True` | Borders anzeigen |
| `show_index` | `bool` | `False` | Index anzeigen |
| `custom_css` | `str` | `None` | Zusätzliches CSS |
| `key` | `str` | `None` | Eindeutiger Key |

## Größen

- **compact**: Platzsparend, viele Daten
- **default**: Standard-Größe
- **comfortable**: Große Abstände, bessere Lesbarkeit

## Tipps

✅ Verwende `max_height` für lange Tabellen
✅ Verwende `sticky_header` für bessere Navigation
✅ Verwende `size="compact"` für viele Daten
✅ Verwende `key` für eindeutige Identifikation
✅ Verwende `override_dataframe_styling()` für globales Styling

## Beispiel: Vollständige Konfiguration

```python
table(
    data=df,
    sortable=True,
    striped=True,
    hover=True,
    size="comfortable",
    sticky_header=True,
    max_height="500px",
    bordered=True,
    show_index=False,
    custom_css=my_css,
    key="main_table"
)
```
