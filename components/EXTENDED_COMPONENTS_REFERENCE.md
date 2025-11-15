# Erweiterte shadcn/ui Komponenten - Referenz

Diese Dokumentation beschreibt alle erweiterten UI-Komponenten des shadcn/ui-Systems.

## Inhaltsverzeichnis

1. [Accordion](#accordion)
2. [Breadcrumb](#breadcrumb)
3. [Dropdown Menu](#dropdown-menu)
4. [Popover](#popover)
5. [Progress](#progress)
6. [Skeleton Loader](#skeleton-loader)
7. [Pagination](#pagination)

---

## Accordion

Ein Accordion für zusammenklappbare Content-Bereiche.

### Features

- Single oder Multiple Items gleichzeitig offen
- Smooth Transitions
- Icons für Expand/Collapse
- Responsive Design

### Verwendung

```python
from components import Accordion

accordion = Accordion()
accordion.render(
    items=[
        {
            "title": "Abschnitt 1",
            "content": "Inhalt 1",
            "icon": "📄"
        },
        {
            "title": "Abschnitt 2",
            "content": "Inhalt 2"
        }
    ],
    type="single",  # oder "multiple"
    default_open=[0],
    key="my_accordion"
)
```

### Parameter

- `items` (List[Dict]): Liste von Items mit 'title', 'content', optional 'icon'
- `type` (str): 'single' (nur ein Item offen) oder 'multiple'
- `default_open` (List[int]): Indizes der initial geöffneten Items
- `custom_css` (str): Zusätzliches CSS
- `key` (str): Eindeutiger Key

### Rückgabewert

Liste der aktuell geöffneten Item-Indizes

---

## Breadcrumb

Eine Breadcrumb-Navigation für hierarchische Pfade.

### Features

- Klickbare Links
- Custom Separator
- Icons für Items
- Responsive Design

### Verwendung

```python
from components import Breadcrumb

breadcrumb = Breadcrumb()
breadcrumb.render(
    items=[
        {"label": "Home", "icon": "🏠"},
        {"label": "Projekte", "icon": "📁"},
        {"label": "Solar-Anlage"}
    ],
    separator="/",
    on_click=lambda idx: print(f"Clicked item {idx}"),
    key="my_breadcrumb"
)
```

### Parameter

- `items` (List[Dict]): Liste von Items mit 'label', optional 'icon'
- `separator` (str): Trennzeichen zwischen Items (default: "/")
- `on_click` (Callable): Callback mit Item-Index bei Klick
- `custom_css` (str): Zusätzliches CSS
- `key` (str): Eindeutiger Key

### Rückgabewert

Index des geklickten Items oder None

---

## Dropdown Menu

Ein Dropdown-Menü für Aktionen und Navigation.

### Features

- Gruppierte Menu-Items
- Icons und Shortcuts
- Separatoren
- Disabled Items

### Verwendung

```python
from components import DropdownMenu

dropdown = DropdownMenu()
selected = dropdown.render(
    trigger_label="Aktionen",
    trigger_icon="⚙️",
    items=[
        {"label": "Bearbeiten", "icon": "✏️", "value": "edit"},
        {"label": "Löschen", "icon": "🗑️", "value": "delete"},
        {"separator": True},
        {"label": "Exportieren", "icon": "📤", "value": "export"}
    ],
    on_select=lambda val: print(f"Selected: {val}"),
    key="my_dropdown"
)
```

### Parameter

- `trigger_label` (str): Label für Trigger-Button
- `items` (List[Dict]): Menu-Items mit 'label', 'value', 'icon', 'disabled', 'separator'
- `trigger_icon` (str): Icon für Trigger-Button
- `align` (str): Ausrichtung ('left' oder 'right')
- `on_select` (Callable): Callback mit Item-Value bei Auswahl
- `custom_css` (str): Zusätzliches CSS
- `key` (str): Eindeutiger Key

### Rückgabewert

Value des ausgewählten Items oder None

---

## Popover

Ein Popover für zusätzliche Informationen und Inhalte.

### Features

- Verschiedene Positionen (top, bottom, left, right)
- Trigger on hover oder click
- Arrow/Pointer
- Responsive Design

### Verwendung

```python
from components import Popover

popover = Popover()
popover.render(
    trigger_label="Info",
    trigger_icon="ℹ️",
    title="Wichtige Information",
    content="Zusätzliche Informationen hier",
    position="top",
    trigger_type="click",  # oder "hover"
    key="my_popover"
)
```

### Parameter

- `trigger_label` (str): Label für Trigger-Element
- `content` (str): Popover-Inhalt
- `title` (str): Optionaler Titel
- `position` (str): Position ('top', 'bottom', 'left', 'right')
- `trigger_type` (str): Trigger-Art ('click' oder 'hover')
- `trigger_icon` (str): Icon für Trigger
- `custom_css` (str): Zusätzliches CSS
- `key` (str): Eindeutiger Key

---

## Progress

Eine Progress-Bar für Fortschrittsanzeigen.

### Features

- Verschiedene Varianten (default, success, warning, error)
- Animierte Transitions
- Label und Prozentanzeige
- Verschiedene Größen

### Verwendung

```python
from components import Progress

progress = Progress()
progress.render(
    value=75,
    max_value=100,
    label="Upload",
    show_percentage=True,
    variant="success",
    size="md",
    animated=True,
    key="my_progress"
)
```

### Parameter

- `value` (float): Aktueller Wert
- `max_value` (float): Maximalwert (default: 100)
- `label` (str): Optionales Label
- `show_percentage` (bool): Ob Prozentanzeige gezeigt werden soll
- `variant` (str): Farb-Variante ('default', 'success', 'warning', 'error')
- `size` (str): Größe ('sm', 'md', 'lg')
- `animated` (bool): Ob animiert werden soll
- `custom_css` (str): Zusätzliches CSS
- `key` (str): Eindeutiger Key

---

## Skeleton Loader

Skeleton-Loader für Lade-Zustände.

### Features

- Verschiedene Formen (text, circle, rectangle)
- Animierte Pulse-Effekte
- Verschiedene Größen
- Kombinierbare Layouts

### Verwendung

```python
from components import Skeleton, SkeletonCard

# Einfacher Skeleton
skeleton = Skeleton()
skeleton.render(
    variant="text",
    lines=3,
    animated=True,
    key="my_skeleton"
)

# Card Skeleton
skeleton_card = SkeletonCard()
skeleton_card.render(
    show_avatar=True,
    show_footer=True,
    key="my_skeleton_card"
)
```

### Skeleton Parameter

- `variant` (str): Form ('text', 'circle', 'rectangle')
- `width` (str): Breite (CSS-Wert)
- `height` (str): Höhe (CSS-Wert)
- `lines` (int): Anzahl Zeilen (nur bei variant='text')
- `animated` (bool): Ob Pulse-Animation gezeigt werden soll
- `custom_css` (str): Zusätzliches CSS
- `key` (str): Eindeutiger Key

### SkeletonCard Parameter

- `show_avatar` (bool): Ob Avatar-Skeleton gezeigt werden soll
- `show_footer` (bool): Ob Footer-Skeleton gezeigt werden soll
- `custom_css` (str): Zusätzliches CSS
- `key` (str): Eindeutiger Key

---

## Pagination

Eine Pagination für seitenweise Navigation.

### Features

- Erste/Letzte Seite
- Vorherige/Nächste Seite
- Seitenzahlen mit Ellipsis
- Responsive Design

### Verwendung

```python
from components import Pagination

pagination = Pagination()
current_page = pagination.render(
    total_pages=10,
    current_page=1,
    max_visible_pages=5,
    show_first_last=True,
    show_prev_next=True,
    on_page_change=lambda page: print(f"Page {page}"),
    key="my_pagination"
)
```

### Parameter

- `total_pages` (int): Gesamtanzahl Seiten
- `current_page` (int): Aktuelle Seite (1-basiert)
- `max_visible_pages` (int): Maximale Anzahl sichtbarer Seitenzahlen
- `show_first_last` (bool): Ob Erste/Letzte-Buttons gezeigt werden sollen
- `show_prev_next` (bool): Ob Vorherige/Nächste-Buttons gezeigt werden sollen
- `on_page_change` (Callable): Callback mit neuer Seitenzahl
- `custom_css` (str): Zusätzliches CSS
- `key` (str): Eindeutiger Key

### Rückgabewert

Aktuelle Seitenzahl

---

## Convenience-Funktionen

Alle Komponenten haben auch Convenience-Funktionen für einfachere Verwendung:

```python
from components import (
    accordion,
    breadcrumb,
    dropdown_menu,
    popover,
    progress,
    skeleton,
    skeleton_card,
    pagination
)

# Verwendung ohne Instanziierung
accordion(items=[...], type="single", key="acc1")
breadcrumb(items=[...], separator="/", key="bc1")
dropdown_menu(trigger_label="Menu", items=[...], key="dd1")
popover(trigger_label="Info", content="...", key="pop1")
progress(value=75, label="Upload", key="prog1")
skeleton(variant="text", lines=3, key="skel1")
skeleton_card(show_avatar=True, key="skelcard1")
pagination(total_pages=10, current_page=1, key="pag1")
```

---

## Best Practices

### 1. Accordion

- Verwenden Sie `type="single"` für FAQ-Bereiche
- Verwenden Sie `type="multiple"` für Filter oder Einstellungen
- Fügen Sie Icons hinzu für bessere Erkennbarkeit

### 2. Breadcrumb

- Halten Sie die Hierarchie flach (max. 4-5 Ebenen)
- Verwenden Sie aussagekräftige Labels
- Der letzte Item sollte nicht klickbar sein

### 3. Dropdown Menu

- Gruppieren Sie verwandte Aktionen mit Separatoren
- Verwenden Sie Icons für bessere Erkennbarkeit
- Markieren Sie destruktive Aktionen (z.B. Löschen) visuell

### 4. Popover

- Verwenden Sie `trigger_type="hover"` für Tooltips
- Verwenden Sie `trigger_type="click"` für komplexere Inhalte
- Halten Sie den Content kurz und prägnant

### 5. Progress

- Verwenden Sie `animated=True` für laufende Prozesse
- Verwenden Sie `animated=False` für abgeschlossene Prozesse
- Wählen Sie die passende Variante für den Status

### 6. Skeleton Loader

- Verwenden Sie Skeleton während Daten geladen werden
- Matchen Sie die Skeleton-Form mit dem finalen Content
- Verwenden Sie `animated=True` für besseres UX

### 7. Pagination

- Passen Sie `max_visible_pages` an die Bildschirmgröße an
- Verwenden Sie `on_page_change` für Daten-Nachladen
- Zeigen Sie die aktuelle Seite deutlich an

---

## Beispiele

Siehe `demo_extended_components.py` für vollständige Beispiele aller Komponenten.

---

## Theme-Integration

Alle Komponenten nutzen automatisch das aktuelle Theme:

```python
from theming import ThemeManager

# Theme Manager initialisieren
theme_manager = ThemeManager()
theme_manager.set_theme('shadcn-dark')

# Komponenten mit Theme Manager
accordion = Accordion(theme_manager=theme_manager)
breadcrumb = Breadcrumb(theme_manager=theme_manager)
# ... etc.
```

---

## Troubleshooting

### Problem: Komponente wird nicht angezeigt

**Lösung**: Stellen Sie sicher, dass das Theme CSS injiziert wurde:

```python
css = theme_manager.generate_css()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
```

### Problem: Accordion öffnet nicht

**Lösung**: Verwenden Sie eindeutige Keys für jedes Accordion:

```python
accordion.render(items=[...], key="unique_key_1")
```

### Problem: Pagination springt nicht zur richtigen Seite

**Lösung**: Verwenden Sie `on_page_change` Callback und `st.rerun()`:

```python
def handle_page_change(page):
    st.session_state.current_page = page
    st.rerun()

pagination.render(
    total_pages=10,
    on_page_change=handle_page_change
)
```

---

## Support

Bei Fragen oder Problemen siehe:
- `demo_extended_components.py` für Beispiele
- `components/EXTENDED_COMPONENTS_QUICK_REFERENCE.md` für Kurzreferenz
- Komponenten-Sourcecode für Details
