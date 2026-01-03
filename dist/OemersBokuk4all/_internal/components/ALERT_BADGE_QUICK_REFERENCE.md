# Alert & Badge Komponenten - Quick Reference

## Alert Komponente

### Basis-Verwendung

```python
from components import Alert

alert = Alert()
alert.render(
    message="Dies ist eine Nachricht",
    type="info",
    title="Information"
)
```

### Convenience-Funktion

```python
from components.alert import alert

alert(
    message="Schnelle Nachricht",
    type="success",
    title="Erfolg"
)
```

### Parameter

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| `message` | str | - | Haupt-Nachricht (erforderlich) |
| `type` | Literal | "info" | Alert-Typ: info, success, warning, error |
| `title` | str | None | Optionaler Titel |
| `icon` | str | None | Custom Icon (überschreibt Standard) |
| `dismissible` | bool | False | Ob Alert geschlossen werden kann |
| `custom_css` | str | None | Zusätzliches CSS |
| `key` | str | None | Eindeutiger Key |

### Alert-Typen

```python
# Info (blau)
alert.render(message="Info", type="info")

# Success (grün)
alert.render(message="Erfolg", type="success")

# Warning (orange)
alert.render(message="Warnung", type="warning")

# Error (rot)
alert.render(message="Fehler", type="error")
```

### Mit Custom Icon

```python
alert.render(
    message="Neue Nachricht",
    type="info",
    icon="📧"
)
```

### Dismissible Alert

```python
alert.render(
    message="Kann geschlossen werden",
    type="info",
    dismissible=True,
    key="my_alert"
)
```

## AlertDialog Komponente

### Basis-Verwendung

```python
from components import AlertDialog

dialog = AlertDialog()
if dialog.render(
    title="Bestätigung",
    message="Fortfahren?",
    type="warning",
    confirm_text="Ja",
    cancel_text="Nein"
):
    # Bestätigt
    st.success("Bestätigt!")
```

### Convenience-Funktion

```python
from components.alert import alert_dialog

if alert_dialog(
    title="Löschen?",
    message="Wirklich löschen?",
    type="error",
    cancel_text="Abbrechen"
):
    # Löschen durchführen
    pass
```

### Parameter

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| `title` | str | - | Dialog-Titel (erforderlich) |
| `message` | str | - | Dialog-Nachricht (erforderlich) |
| `type` | Literal | "info" | Dialog-Typ: info, success, warning, error |
| `icon` | str | None | Custom Icon |
| `confirm_text` | str | "OK" | Text für Bestätigungs-Button |
| `cancel_text` | str | None | Text für Abbrechen-Button (None = kein Button) |
| `on_confirm` | Callable | None | Callback bei Bestätigung |
| `on_cancel` | Callable | None | Callback bei Abbruch |
| `key` | str | None | Eindeutiger Key |

### Mit Callbacks

```python
def on_confirm():
    st.success("Bestätigt!")

def on_cancel():
    st.info("Abgebrochen!")

dialog.render(
    title="Aktion",
    message="Fortfahren?",
    on_confirm=on_confirm,
    on_cancel=on_cancel
)
```

## Badge Komponente

### Basis-Verwendung

```python
from components import Badge

badge = Badge()
badge.render(
    text="Neu",
    variant="success"
)
```

### Convenience-Funktion

```python
from components.badge import badge

badge(
    text="Premium",
    variant="warning",
    icon="⭐"
)
```

### Parameter

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| `text` | str | - | Badge-Text (erforderlich) |
| `variant` | Literal | "default" | Variante: default, secondary, success, warning, error, info, outline |
| `size` | Literal | "md" | Größe: sm, md, lg |
| `icon` | str | None | Optionales Icon vor Text |
| `dot` | bool | False | Zeigt Dot-Indikator |
| `custom_css` | str | None | Zusätzliches CSS |
| `key` | str | None | Eindeutiger Key |

### Badge-Varianten

```python
# Default (dunkel)
badge.render(text="Default", variant="default")

# Secondary (hell)
badge.render(text="Secondary", variant="secondary")

# Success (grün)
badge.render(text="Success", variant="success")

# Warning (orange)
badge.render(text="Warning", variant="warning")

# Error (rot)
badge.render(text="Error", variant="error")

# Info (blau)
badge.render(text="Info", variant="info")

# Outline (transparent mit Border)
badge.render(text="Outline", variant="outline")
```

### Badge-Größen

```python
# Small
badge.render(text="Small", size="sm")

# Medium (Standard)
badge.render(text="Medium", size="md")

# Large
badge.render(text="Large", size="lg")
```

### Mit Icon

```python
badge.render(
    text="Verified",
    variant="success",
    icon="✓"
)
```

### Mit Dot-Indikator

```python
badge.render(
    text="Online",
    variant="success",
    dot=True
)
```

## Badge Group Komponente

### Basis-Verwendung

```python
from components import BadgeGroup

group = BadgeGroup()
group.render(
    badges=[
        {"text": "Python", "variant": "info"},
        {"text": "React", "variant": "success"},
        {"text": "TypeScript", "variant": "warning"}
    ]
)
```

### Convenience-Funktion

```python
from components.badge import badge_group

badge_group(
    badges=[
        {"text": "Tag 1", "variant": "default"},
        {"text": "Tag 2", "variant": "success"}
    ]
)
```

### Parameter

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| `badges` | list[dict] | - | Liste von Badge-Konfigurationen (erforderlich) |
| `spacing` | Literal | "md" | Abstand: sm, md, lg |
| `wrap` | bool | True | Ob Badges umbrechen sollen |
| `key` | str | None | Eindeutiger Key |

### Badge-Konfiguration

Jedes Badge in der Liste ist ein Dict mit folgenden Parametern:

```python
{
    "text": "Badge-Text",
    "variant": "success",  # optional
    "size": "md",          # optional
    "icon": "✓",           # optional
    "dot": False,          # optional
    "custom_css": "",      # optional
    "key": "unique_key"    # optional
}
```

### Mit verschiedenen Spacing

```python
# Small Spacing
group.render(badges=[...], spacing="sm")

# Medium Spacing (Standard)
group.render(badges=[...], spacing="md")

# Large Spacing
group.render(badges=[...], spacing="lg")
```

### Mit/ohne Wrapping

```python
# Mit Wrapping (Standard)
group.render(badges=[...], wrap=True)

# Ohne Wrapping (horizontal scroll)
group.render(badges=[...], wrap=False)
```

## Beispiele

### Alert mit allen Features

```python
from components.alert import alert

alert(
    message="Ihre Daten wurden erfolgreich gespeichert!",
    type="success",
    title="Erfolg",
    icon="💾",
    dismissible=True,
    key="save_success"
)
```

### AlertDialog mit Bestätigung

```python
from components.alert import alert_dialog

if st.button("Löschen"):
    if alert_dialog(
        title="Bestätigung erforderlich",
        message="Möchten Sie diesen Eintrag wirklich löschen?",
        type="error",
        confirm_text="Ja, löschen",
        cancel_text="Abbrechen",
        key="delete_confirm"
    ):
        # Lösch-Aktion durchführen
        delete_item()
        st.success("Gelöscht!")
```

### Badge mit Icon und Dot

```python
from components.badge import badge

badge(
    text="Premium User",
    variant="warning",
    size="lg",
    icon="⭐",
    dot=True
)
```

### Badge Group mit verschiedenen Badges

```python
from components.badge import badge_group

badge_group(
    badges=[
        {"text": "Python", "variant": "info", "icon": "🐍"},
        {"text": "React", "variant": "success", "icon": "⚛️"},
        {"text": "TypeScript", "variant": "warning", "icon": "📘"},
        {"text": "Node.js", "variant": "default", "icon": "🟢"}
    ],
    spacing="md",
    wrap=True
)
```

## Standard-Icons

### Alert Standard-Icons

- **info**: ℹ️
- **success**: ✓
- **warning**: ⚠️
- **error**: ✕

Diese Icons werden automatisch verwendet, können aber mit dem `icon`-Parameter überschrieben werden.

## Styling-Tipps

### Custom CSS

```python
alert.render(
    message="Custom styled alert",
    type="info",
    custom_css="""
        .shadcn-alert-{id} {
            border-width: 2px;
            font-weight: bold;
        }
    """
)
```

### Theme-Integration

Die Komponenten verwenden automatisch die Theme-Tokens:

- `colors.info`, `colors.success`, `colors.warning`, `colors.error`
- `borders.border_radius_md`, `borders.border_radius_full`
- `spacing.spacing_4`
- `animations.transition_base`

## Best Practices

1. **Verwende passende Alert-Typen**
   - `info` für Informationen
   - `success` für erfolgreiche Aktionen
   - `warning` für Warnungen
   - `error` für Fehler

2. **Verwende Titel für wichtige Alerts**
   ```python
   alert(message="...", type="error", title="Fehler")
   ```

3. **Verwende dismissible für nicht-kritische Alerts**
   ```python
   alert(message="...", dismissible=True)
   ```

4. **Verwende AlertDialog für Bestätigungen**
   ```python
   if alert_dialog(title="Löschen?", ...):
       delete_item()
   ```

5. **Verwende Badge-Varianten konsistent**
   - `success` für positive Status
   - `warning` für Aufmerksamkeit
   - `error` für Probleme
   - `info` für neutrale Informationen

6. **Verwende Badge Groups für Tags**
   ```python
   badge_group(badges=[
       {"text": "Tag 1", "variant": "default"},
       {"text": "Tag 2", "variant": "default"}
   ])
   ```

## Demo

Führe die Demo-Datei aus, um alle Features zu sehen:

```bash
streamlit run demo_alert_badge.py
```
