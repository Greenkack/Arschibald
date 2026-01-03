# Erweiterte Komponenten - Kurzreferenz

## Accordion

```python
from components import accordion

accordion(
    items=[
        {"title": "Titel", "content": "Inhalt", "icon": "📄"}
    ],
    type="single",  # oder "multiple"
    default_open=[0],
    key="acc1"
)
```

## Breadcrumb

```python
from components import breadcrumb

breadcrumb(
    items=[
        {"label": "Home", "icon": "🏠"},
        {"label": "Projekte"}
    ],
    separator="/",
    on_click=lambda idx: print(idx),
    key="bc1"
)
```

## Dropdown Menu

```python
from components import dropdown_menu

selected = dropdown_menu(
    trigger_label="Aktionen",
    trigger_icon="⚙️",
    items=[
        {"label": "Bearbeiten", "icon": "✏️", "value": "edit"},
        {"separator": True},
        {"label": "Löschen", "icon": "🗑️", "value": "delete"}
    ],
    key="dd1"
)
```

## Popover

```python
from components import popover

popover(
    trigger_label="Info",
    content="Zusätzliche Informationen",
    title="Titel",
    position="top",  # top, bottom, left, right
    trigger_type="click",  # click oder hover
    key="pop1"
)
```

## Progress

```python
from components import progress

progress(
    value=75,
    label="Upload",
    show_percentage=True,
    variant="success",  # default, success, warning, error
    size="md",  # sm, md, lg
    animated=True,
    key="prog1"
)
```

## Skeleton Loader

```python
from components import skeleton, skeleton_card

# Einfacher Skeleton
skeleton(
    variant="text",  # text, circle, rectangle
    lines=3,
    animated=True,
    key="skel1"
)

# Card Skeleton
skeleton_card(
    show_avatar=True,
    show_footer=True,
    key="skelcard1"
)
```

## Pagination

```python
from components import pagination

current_page = pagination(
    total_pages=10,
    current_page=1,
    max_visible_pages=5,
    show_first_last=True,
    show_prev_next=True,
    on_page_change=lambda page: print(page),
    key="pag1"
)
```

## Alle Komponenten auf einen Blick

| Komponente | Hauptverwendung | Key Features |
|------------|----------------|--------------|
| **Accordion** | Zusammenklappbare Inhalte | Single/Multiple Mode, Icons |
| **Breadcrumb** | Hierarchische Navigation | Klickbar, Custom Separator |
| **Dropdown Menu** | Aktionsmenüs | Separatoren, Disabled Items |
| **Popover** | Zusatzinformationen | Click/Hover, Positionierung |
| **Progress** | Fortschrittsanzeige | Varianten, Animation |
| **Skeleton** | Lade-Zustände | Verschiedene Formen, Pulse |
| **Pagination** | Seitennavigation | Ellipsis, First/Last |

## Wichtige Parameter

### Gemeinsame Parameter

- `key` (str): Eindeutiger Key für Session State
- `custom_css` (str): Zusätzliches CSS
- `theme_manager`: Theme Manager Instanz (optional)

### Callbacks

- `on_click` (Breadcrumb): Callback bei Item-Klick
- `on_select` (Dropdown): Callback bei Item-Auswahl
- `on_page_change` (Pagination): Callback bei Seitenwechsel

### Varianten

- **Progress**: default, success, warning, error
- **Skeleton**: text, circle, rectangle
- **Accordion**: single, multiple

### Positionen

- **Popover**: top, bottom, left, right
- **Dropdown**: left, right (align)

## Tipps

1. **Eindeutige Keys**: Verwenden Sie immer eindeutige Keys
2. **Theme Integration**: Übergeben Sie theme_manager für konsistentes Styling
3. **Callbacks**: Nutzen Sie Callbacks für interaktive Funktionen
4. **Session State**: Komponenten speichern State automatisch
5. **Rerun**: Verwenden Sie `st.rerun()` nach State-Änderungen

## Demo

Siehe `demo_extended_components.py` für vollständige Beispiele.
