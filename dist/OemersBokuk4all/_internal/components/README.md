# shadcn/ui Components für Streamlit

Diese Bibliothek bietet shadcn/ui-styled Komponenten für Streamlit-Anwendungen.

## Übersicht

Die Component Library basiert auf dem shadcn/ui Design-System und bietet:

- **Konsistentes Design**: Alle Komponenten folgen dem shadcn/ui Design-System
- **Theme-Support**: Vollständige Integration mit dem Theme-System
- **Responsive**: Alle Komponenten sind responsive und mobile-friendly
- **Accessibility**: WCAG 2.1 Level AA konform
- **Type-Safe**: Vollständige Type-Hints für bessere IDE-Unterstützung

## Installation

Die Komponenten sind Teil des Projekts und benötigen keine separate Installation.

```python
from components import Card, ShadcnComponent
```

## Basis-Komponente

### ShadcnComponent

Die Basis-Klasse für alle shadcn-Komponenten.

```python
from components import ShadcnComponent

class MyComponent(ShadcnComponent):
    def render(self, **kwargs):
        # Zugriff auf Theme-Tokens
        primary_color = self.get_token('colors.primary')
        
        # CSS injizieren
        self.inject_css(f'''
            .my-component {{
                color: {primary_color};
            }}
        ''')
        
        # HTML rendern
        st.markdown('<div class="my-component">Content</div>', 
                   unsafe_allow_html=True)
```

#### Methoden

- `get_token(path, default)`: Holt Theme-Token-Wert
- `get_css_var(token_path)`: Gibt CSS-Variable für Token zurück
- `inject_css(css)`: Injiziert CSS in die App
- `render(**kwargs)`: Rendert die Komponente (muss überschrieben werden)

## Card-Komponente

Eine flexible Card-Komponente mit Header, Body und Footer.

### Features

- ✅ Header mit Titel, Beschreibung, Icon und Badge
- ✅ Body für Hauptinhalt
- ✅ Footer für Aktionen
- ✅ 3 Varianten: default, outlined, elevated
- ✅ Hover-Effekte mit Transitions
- ✅ Responsive Design
- ✅ Theme-Integration

### Basis-Verwendung

```python
from components import Card

card = Card()
card.render(
    title="Meine Card",
    content="Hier steht der Inhalt"
)
```

### Mit allen Features

```python
card = Card()
card.render(
    title="Solar-Analyse",
    description="Aktuelle Daten vom 15.11.2025",
    content="""
        <p>Die Solaranlage produziert heute:</p>
        <ul>
            <li>Leistung: 4.5 kW</li>
            <li>Ertrag: 28 kWh</li>
            <li>Effizienz: 94%</li>
        </ul>
    """,
    footer="Letzte Aktualisierung: vor 5 Minuten",
    variant="elevated",
    icon="☀️",
    badge="Live",
    badge_variant="success",
    hover_effect=True
)
```

### Varianten

#### Default

```python
card.render(
    title="Default Card",
    content="Standard-Variante mit leichtem Schatten",
    variant="default"
)
```

#### Outlined

```python
card.render(
    title="Outlined Card",
    content="Variante mit Border, ohne Schatten",
    variant="outlined"
)
```

#### Elevated

```python
card.render(
    title="Elevated Card",
    content="Variante mit starkem Schatten für Hervorhebung",
    variant="elevated"
)
```

### Badge-Varianten

```python
# Success Badge
card.render(
    title="Erfolg",
    badge="Aktiv",
    badge_variant="success"
)

# Warning Badge
card.render(
    title="Warnung",
    badge="Achtung",
    badge_variant="warning"
)

# Error Badge
card.render(
    title="Fehler",
    badge="Offline",
    badge_variant="error"
)

# Info Badge
card.render(
    title="Information",
    badge="Beta",
    badge_variant="info"
)
```

### Convenience-Funktion

Für schnellere Verwendung gibt es eine Shortcut-Funktion:

```python
from components.card import card

card(
    title="Quick Card",
    content="Schnell erstellt mit der card() Funktion",
    variant="elevated"
)
```

### Custom CSS

Sie können zusätzliches CSS hinzufügen:

```python
card.render(
    title="Custom Styled Card",
    content="Mit eigenem CSS",
    custom_css="""
        .shadcn-card-body-* {
            font-weight: bold;
            text-align: center;
        }
    """
)
```

### Responsive Layout

Cards passen sich automatisch an die Bildschirmgröße an:

```python
col1, col2, col3 = st.columns(3)

with col1:
    card(title="Card 1", content="Inhalt 1")

with col2:
    card(title="Card 2", content="Inhalt 2")

with col3:
    card(title="Card 3", content="Inhalt 3")
```

## Best Practices

### 1. Theme-Manager verwenden

Übergeben Sie den Theme-Manager für konsistentes Styling:

```python
theme_manager = st.session_state.get('theme_manager')
card = Card(theme_manager=theme_manager)
```

### 2. Eindeutige Keys

Verwenden Sie eindeutige Keys bei mehreren Cards:

```python
for i in range(5):
    card(
        title=f"Card {i}",
        content=f"Inhalt {i}",
        key=f"card_{i}"
    )
```

### 3. HTML-Content sanitizen

Bei User-Input sollten Sie HTML escapen:

```python
from html import escape

user_input = "<script>alert('XSS')</script>"
card(
    title="User Content",
    content=escape(user_input)
)
```

### 4. Streamlit-Komponenten in Cards

Sie können Streamlit-Komponenten in Cards verwenden:

```python
card = Card()
card.render(title="Interaktive Card")

# Streamlit-Komponenten nach der Card
st.slider("Wert", 0, 100, 50)
st.button("Aktion")
```

## Beispiele

### Dashboard-Card

```python
card(
    title="Gesamtertrag",
    description="Heute",
    content="<h1 style='margin:0; font-size: 3rem;'>28.5 kWh</h1>",
    footer="↑ 12% vs. gestern",
    variant="elevated",
    icon="⚡",
    badge="+12%",
    badge_variant="success"
)
```

### Info-Card

```python
card(
    title="System-Status",
    description="Alle Systeme betriebsbereit",
    content="""
        <div style='display: flex; gap: 1rem;'>
            <div>✅ Wechselrichter</div>
            <div>✅ Speicher</div>
            <div>✅ Monitoring</div>
        </div>
    """,
    variant="outlined",
    icon="🔧"
)
```

### Warnung-Card

```python
card(
    title="Wartung erforderlich",
    description="Nächste Wartung überfällig",
    content="Bitte kontaktieren Sie den Service für eine Wartung.",
    footer="Fällig seit: 10.11.2025",
    variant="default",
    icon="⚠️",
    badge="Dringend",
    badge_variant="warning"
)
```

## API-Referenz

### Card.render()

```python
def render(
    title: Optional[str] = None,
    description: Optional[str] = None,
    content: Optional[str] = None,
    footer: Optional[str] = None,
    variant: Literal["default", "outlined", "elevated"] = "default",
    icon: Optional[str] = None,
    badge: Optional[str] = None,
    badge_variant: Literal["default", "success", "warning", "error", "info"] = "default",
    hover_effect: bool = True,
    clickable: bool = False,
    on_click: Optional[Callable] = None,
    custom_css: Optional[str] = None,
    key: Optional[str] = None
) -> None
```

#### Parameter

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| `title` | `str` | `None` | Titel der Card |
| `description` | `str` | `None` | Beschreibung unter dem Titel |
| `content` | `str` | `None` | Hauptinhalt (HTML erlaubt) |
| `footer` | `str` | `None` | Footer-Inhalt |
| `variant` | `Literal` | `"default"` | Card-Variante |
| `icon` | `str` | `None` | Icon (Emoji oder Unicode) |
| `badge` | `str` | `None` | Badge-Text |
| `badge_variant` | `Literal` | `"default"` | Badge-Farbe |
| `hover_effect` | `bool` | `True` | Hover-Effekt aktivieren |
| `clickable` | `bool` | `False` | Card klickbar machen |
| `on_click` | `Callable` | `None` | Click-Handler |
| `custom_css` | `str` | `None` | Zusätzliches CSS |
| `key` | `str` | `None` | Eindeutiger Key |

## Troubleshooting

### Card wird nicht angezeigt

Stellen Sie sicher, dass der Theme-Manager initialisiert ist:

```python
if 'theme_manager' not in st.session_state:
    from theming import ThemeManager
    st.session_state.theme_manager = ThemeManager()
```

### Styling funktioniert nicht

Prüfen Sie, ob CSS korrekt injiziert wird:

```python
# Debug-Modus
card = Card()
card.render(title="Test")
st.write("Theme Manager:", card.theme_manager)
```

### HTML wird escaped

Verwenden Sie `unsafe_allow_html=True` ist bereits in der Komponente aktiviert.
Wenn Sie zusätzliches HTML rendern, verwenden Sie `st.markdown(..., unsafe_allow_html=True)`.

## Nächste Schritte

- [ ] Alert-Komponente implementieren
- [ ] Badge-Komponente implementieren
- [ ] Table-Komponente implementieren
- [ ] Weitere Komponenten aus dem Design-System

## Support

Bei Fragen oder Problemen:
1. Prüfen Sie die Dokumentation
2. Schauen Sie sich die Beispiele an
3. Erstellen Sie ein Issue im Repository
