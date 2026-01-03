# Card Component - Quick Reference

## Import

```python
from components import Card
from components.card import card  # Convenience function
```

## Basis-Verwendung

```python
# Mit Klasse
card_component = Card()
card_component.render(
    title="Meine Card",
    content="Inhalt"
)

# Mit Convenience-Funktion
card(
    title="Meine Card",
    content="Inhalt"
)
```

## Parameter

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| `title` | `str` | `None` | Titel der Card |
| `description` | `str` | `None` | Beschreibung unter dem Titel |
| `content` | `str` | `None` | Hauptinhalt (HTML erlaubt) |
| `footer` | `str` | `None` | Footer-Inhalt |
| `variant` | `"default"` \| `"outlined"` \| `"elevated"` | `"default"` | Card-Variante |
| `icon` | `str` | `None` | Icon (Emoji oder Unicode) |
| `badge` | `str` | `None` | Badge-Text |
| `badge_variant` | `"default"` \| `"success"` \| `"warning"` \| `"error"` \| `"info"` | `"default"` | Badge-Farbe |
| `hover_effect` | `bool` | `True` | Hover-Effekt aktivieren |
| `clickable` | `bool` | `False` | Card klickbar machen |
| `on_click` | `Callable` | `None` | Click-Handler |
| `custom_css` | `str` | `None` | Zusätzliches CSS |
| `key` | `str` | `None` | Eindeutiger Key |

## Varianten

### Default
```python
card(title="Default", variant="default")
```
Standard mit leichtem Schatten und Border.

### Outlined
```python
card(title="Outlined", variant="outlined")
```
Stärkerer Border, ohne Schatten.

### Elevated
```python
card(title="Elevated", variant="elevated")
```
Starker Schatten für Hervorhebung.

## Badge-Varianten

```python
# Success (grün)
card(badge="Aktiv", badge_variant="success")

# Warning (orange)
card(badge="Achtung", badge_variant="warning")

# Error (rot)
card(badge="Offline", badge_variant="error")

# Info (blau)
card(badge="Beta", badge_variant="info")
```

## Häufige Patterns

### Dashboard-Metrik
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

### Status-Card
```python
card(
    title="System-Status",
    description="Alle Systeme betriebsbereit",
    content="✅ Wechselrichter<br>✅ Speicher<br>✅ Monitoring",
    variant="outlined",
    icon="🔧",
    badge="Online",
    badge_variant="success"
)
```

### Warnung
```python
card(
    title="Wartung erforderlich",
    description="Nächste Wartung überfällig",
    content="Bitte kontaktieren Sie den Service.",
    footer="Fällig seit: 10.11.2025",
    icon="⚠️",
    badge="Dringend",
    badge_variant="warning"
)
```

### Grid-Layout
```python
col1, col2, col3 = st.columns(3)

with col1:
    card(title="Card 1", content="Inhalt 1")

with col2:
    card(title="Card 2", content="Inhalt 2")

with col3:
    card(title="Card 3", content="Inhalt 3")
```

### Mehrere Cards in Schleife
```python
for i in range(5):
    card(
        title=f"Card {i+1}",
        content=f"Inhalt {i+1}",
        key=f"card_{i}"  # Wichtig: Eindeutiger Key!
    )
```

## Mit Theme-Manager

```python
from theming import ThemeManager

theme_manager = st.session_state.theme_manager
card_component = Card(theme_manager=theme_manager)

card_component.render(
    title="Themed Card",
    content="Verwendet Theme-Tokens"
)
```

## Custom CSS

```python
card(
    title="Custom Styled",
    content="Mit eigenem CSS",
    custom_css="""
        .shadcn-card-body-* {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 0.5rem;
        }
    """
)
```

## HTML-Content

```python
card(
    title="Rich Content",
    content="""
        <div>
            <h2>Überschrift</h2>
            <p>Text mit <strong>Formatierung</strong></p>
            <ul>
                <li>Punkt 1</li>
                <li>Punkt 2</li>
            </ul>
        </div>
    """
)
```

## Best Practices

### ✅ DO

```python
# Eindeutige Keys bei mehreren Cards
for i in range(5):
    card(title=f"Card {i}", key=f"card_{i}")

# Theme-Manager verwenden
card_component = Card(theme_manager=theme_manager)

# HTML escapen bei User-Input
from html import escape
card(content=escape(user_input))
```

### ❌ DON'T

```python
# Keine Keys bei mehreren Cards
for i in range(5):
    card(title=f"Card {i}")  # ❌ Kann zu Problemen führen

# Unescaped User-Input
card(content=user_input)  # ❌ XSS-Risiko
```

## Troubleshooting

### Card wird nicht angezeigt
```python
# Prüfe Theme-Manager
if 'theme_manager' not in st.session_state:
    from theming import ThemeManager
    st.session_state.theme_manager = ThemeManager()
```

### Styling funktioniert nicht
```python
# Debug-Modus
card = Card()
st.write("Theme Manager:", card.theme_manager)
```

## Demo

Führen Sie die Demo aus:
```bash
streamlit run demo_card_component.py
```

## Weitere Infos

- Vollständige Dokumentation: `components/README.md`
- Tests: `tests/test_card_component.py`
- Design-Spezifikation: `.kiro/specs/shadcn-ui-modernization/design.md`
