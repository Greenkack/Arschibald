# Alert & Badge Komponenten - Vollständige Referenz

## Übersicht

Dieses Dokument beschreibt die Alert und Badge Komponenten des shadcn/ui Design-Systems für Streamlit.

### Komponenten

1. **Alert** - Benachrichtigungen und Meldungen
2. **AlertDialog** - Modale Bestätigungs-Dialoge
3. **Badge** - Labels und Status-Anzeigen
4. **BadgeGroup** - Gruppierte Badges

## Alert Komponente

### Beschreibung

Die Alert-Komponente zeigt wichtige Nachrichten und Benachrichtigungen an. Sie unterstützt verschiedene Typen (info, success, warning, error) mit passenden Farben und Icons.

### Klasse: `Alert`

```python
class Alert(ShadcnComponent):
    """shadcn/ui Alert-Komponente"""
```

### Methode: `render()`

```python
def render(
    self,
    message: str,
    type: Literal["info", "success", "warning", "error"] = "info",
    title: Optional[str] = None,
    icon: Optional[str] = None,
    dismissible: bool = False,
    custom_css: Optional[str] = None,
    key: Optional[str] = None
) -> None
```

#### Parameter

- **message** (str, erforderlich)
  - Die Haupt-Nachricht des Alerts
  - Wird als HTML gerendert
  - Beispiel: `"Die Daten wurden gespeichert"`

- **type** (Literal["info", "success", "warning", "error"], default: "info")
  - Der Typ des Alerts, bestimmt Farbe und Standard-Icon
  - `"info"`: Blau, für Informationen
  - `"success"`: Grün, für erfolgreiche Aktionen
  - `"warning"`: Orange, für Warnungen
  - `"error"`: Rot, für Fehler

- **title** (Optional[str], default: None)
  - Optionaler Titel über der Nachricht
  - Wird fett dargestellt
  - Beispiel: `"Erfolg"`

- **icon** (Optional[str], default: None)
  - Custom Icon (überschreibt Standard-Icon)
  - Kann Emoji oder Unicode-Zeichen sein
  - Beispiel: `"📧"`, `"✓"`

- **dismissible** (bool, default: False)
  - Ob der Alert geschlossen werden kann
  - Zeigt einen Close-Button (×)
  - Status wird im Session State gespeichert

- **custom_css** (Optional[str], default: None)
  - Zusätzliches Custom-CSS
  - Wird nach dem Standard-CSS injiziert

- **key** (Optional[str], default: None)
  - Eindeutiger Key für die Komponente
  - Wichtig für dismissible Alerts

#### Rückgabewert

Keine (rendert direkt in Streamlit)

#### Beispiele

**Einfacher Alert:**
```python
from components import Alert

alert = Alert()
alert.render(
    message="Dies ist eine Info-Nachricht",
    type="info"
)
```

**Alert mit Titel:**
```python
alert.render(
    message="Die Aktion wurde erfolgreich ausgeführt",
    type="success",
    title="Erfolg"
)
```

**Alert mit Custom Icon:**
```python
alert.render(
    message="Neue E-Mail erhalten",
    type="info",
    title="Posteingang",
    icon="📧"
)
```

**Dismissible Alert:**
```python
alert.render(
    message="Dieser Alert kann geschlossen werden",
    type="info",
    dismissible=True,
    key="my_dismissible_alert"
)
```

### Convenience-Funktion: `alert()`

```python
def alert(
    message: str,
    type: Literal["info", "success", "warning", "error"] = "info",
    title: Optional[str] = None,
    icon: Optional[str] = None,
    dismissible: bool = False,
    custom_css: Optional[str] = None,
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> None
```

Shortcut-Funktion zum schnellen Rendern eines Alerts.

**Beispiel:**
```python
from components.alert import alert

alert(
    message="Schnelle Nachricht",
    type="success"
)
```

### Standard-Icons

Die Alert-Komponente verwendet folgende Standard-Icons:

- **info**: ℹ️
- **success**: ✓
- **warning**: ⚠️
- **error**: ✕

Diese können mit dem `icon`-Parameter überschrieben werden.

### Styling

Die Alert-Komponente verwendet folgende Theme-Tokens:

- `colors.info`, `colors.success`, `colors.warning`, `colors.error`
- `colors.background`, `colors.foreground`
- `borders.border_radius_md`
- `spacing.spacing_4`
- `animations.transition_base`

## AlertDialog Komponente

### Beschreibung

Der AlertDialog zeigt modale Dialoge für wichtige Benachrichtigungen und Bestätigungen an. Er blockiert die Interaktion mit dem Rest der App bis der Dialog geschlossen wird.

### Klasse: `AlertDialog`

```python
class AlertDialog(ShadcnComponent):
    """shadcn/ui AlertDialog-Komponente"""
```

### Methode: `render()`

```python
def render(
    self,
    title: str,
    message: str,
    type: Literal["info", "success", "warning", "error"] = "info",
    icon: Optional[str] = None,
    confirm_text: str = "OK",
    cancel_text: Optional[str] = None,
    on_confirm: Optional[Callable] = None,
    on_cancel: Optional[Callable] = None,
    key: Optional[str] = None
) -> bool
```

#### Parameter

- **title** (str, erforderlich)
  - Der Titel des Dialogs
  - Wird prominent dargestellt

- **message** (str, erforderlich)
  - Die Haupt-Nachricht des Dialogs
  - Wird unter dem Titel angezeigt

- **type** (Literal["info", "success", "warning", "error"], default: "info")
  - Der Typ des Dialogs, bestimmt Farbe und Icon

- **icon** (Optional[str], default: None)
  - Custom Icon (überschreibt Standard-Icon)

- **confirm_text** (str, default: "OK")
  - Text für den Bestätigungs-Button

- **cancel_text** (Optional[str], default: None)
  - Text für den Abbrechen-Button
  - Wenn None, wird kein Abbrechen-Button angezeigt

- **on_confirm** (Optional[Callable], default: None)
  - Callback-Funktion bei Bestätigung
  - Wird aufgerufen wenn Bestätigungs-Button geklickt wird

- **on_cancel** (Optional[Callable], default: None)
  - Callback-Funktion bei Abbruch
  - Wird aufgerufen wenn Abbrechen-Button geklickt wird

- **key** (Optional[str], default: None)
  - Eindeutiger Key für die Komponente

#### Rückgabewert

- **bool**: `True` wenn bestätigt, `False` sonst

#### Beispiele

**Einfacher Dialog:**
```python
from components import AlertDialog

dialog = AlertDialog()
if dialog.render(
    title="Information",
    message="Dies ist eine wichtige Information",
    type="info"
):
    st.success("Dialog bestätigt!")
```

**Dialog mit Bestätigung/Abbruch:**
```python
if dialog.render(
    title="Löschen bestätigen",
    message="Möchten Sie diesen Eintrag wirklich löschen?",
    type="error",
    confirm_text="Ja, löschen",
    cancel_text="Abbrechen"
):
    # Lösch-Aktion durchführen
    delete_item()
    st.success("Gelöscht!")
else:
    st.info("Abgebrochen")
```

**Dialog mit Callbacks:**
```python
def on_confirm():
    st.session_state.confirmed = True
    st.success("Bestätigt!")

def on_cancel():
    st.session_state.confirmed = False
    st.info("Abgebrochen!")

dialog.render(
    title="Bestätigung erforderlich",
    message="Möchten Sie fortfahren?",
    type="warning",
    confirm_text="Ja",
    cancel_text="Nein",
    on_confirm=on_confirm,
    on_cancel=on_cancel
)
```

### Convenience-Funktion: `alert_dialog()`

```python
def alert_dialog(
    title: str,
    message: str,
    type: Literal["info", "success", "warning", "error"] = "info",
    icon: Optional[str] = None,
    confirm_text: str = "OK",
    cancel_text: Optional[str] = None,
    on_confirm: Optional[Callable] = None,
    on_cancel: Optional[Callable] = None,
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> bool
```

**Beispiel:**
```python
from components.alert import alert_dialog

if alert_dialog(
    title="Bestätigung",
    message="Fortfahren?",
    type="warning",
    cancel_text="Abbrechen"
):
    # Aktion durchführen
    pass
```

## Badge Komponente

### Beschreibung

Die Badge-Komponente zeigt Labels, Status und Tags an. Sie ist kompakt und kann mit Icons und Dot-Indikatoren versehen werden.

### Klasse: `Badge`

```python
class Badge(ShadcnComponent):
    """shadcn/ui Badge-Komponente"""
```

### Methode: `render()`

```python
def render(
    self,
    text: str,
    variant: Literal[
        "default", "success", "warning", "error",
        "info", "outline", "secondary"
    ] = "default",
    size: Literal["sm", "md", "lg"] = "md",
    icon: Optional[str] = None,
    dot: bool = False,
    custom_css: Optional[str] = None,
    key: Optional[str] = None
) -> None
```

#### Parameter

- **text** (str, erforderlich)
  - Der Text des Badges

- **variant** (Literal, default: "default")
  - Die Variante des Badges
  - `"default"`: Dunkel (primary)
  - `"secondary"`: Hell (secondary)
  - `"success"`: Grün
  - `"warning"`: Orange
  - `"error"`: Rot
  - `"info"`: Blau
  - `"outline"`: Transparent mit Border

- **size** (Literal["sm", "md", "lg"], default: "md")
  - Die Größe des Badges
  - `"sm"`: Klein (0.75rem)
  - `"md"`: Mittel (0.875rem)
  - `"lg"`: Groß (1rem)

- **icon** (Optional[str], default: None)
  - Optionales Icon vor dem Text
  - Beispiel: `"✓"`, `"⭐"`

- **dot** (bool, default: False)
  - Zeigt einen Dot-Indikator vor dem Text
  - Nützlich für Status-Anzeigen

- **custom_css** (Optional[str], default: None)
  - Zusätzliches Custom-CSS

- **key** (Optional[str], default: None)
  - Eindeutiger Key für die Komponente

#### Beispiele

**Einfaches Badge:**
```python
from components import Badge

badge = Badge()
badge.render(text="Neu", variant="success")
```

**Badge mit Icon:**
```python
badge.render(
    text="Verified",
    variant="success",
    icon="✓"
)
```

**Badge mit Dot:**
```python
badge.render(
    text="Online",
    variant="success",
    dot=True
)
```

**Verschiedene Größen:**
```python
badge.render(text="Small", size="sm")
badge.render(text="Medium", size="md")
badge.render(text="Large", size="lg")
```

### Convenience-Funktion: `badge()`

```python
def badge(
    text: str,
    variant: Literal[...] = "default",
    size: Literal["sm", "md", "lg"] = "md",
    icon: Optional[str] = None,
    dot: bool = False,
    custom_css: Optional[str] = None,
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> None
```

**Beispiel:**
```python
from components.badge import badge

badge(text="Premium", variant="warning", icon="⭐")
```

## BadgeGroup Komponente

### Beschreibung

Die BadgeGroup zeigt mehrere Badges zusammen an. Sie unterstützt verschiedene Spacing-Optionen und Wrapping.

### Klasse: `BadgeGroup`

```python
class BadgeGroup(ShadcnComponent):
    """Badge-Gruppe für mehrere Badges"""
```

### Methode: `render()`

```python
def render(
    self,
    badges: list[dict],
    spacing: Literal["sm", "md", "lg"] = "md",
    wrap: bool = True,
    key: Optional[str] = None
) -> None
```

#### Parameter

- **badges** (list[dict], erforderlich)
  - Liste von Badge-Konfigurationen
  - Jedes Dict enthält Parameter für ein Badge
  - Beispiel: `[{"text": "Tag 1", "variant": "default"}]`

- **spacing** (Literal["sm", "md", "lg"], default: "md")
  - Abstand zwischen Badges
  - `"sm"`: 0.25rem
  - `"md"`: 0.5rem
  - `"lg"`: 0.75rem

- **wrap** (bool, default: True)
  - Ob Badges umbrechen sollen
  - `True`: Badges brechen um wenn kein Platz
  - `False`: Badges bleiben in einer Zeile (horizontal scroll)

- **key** (Optional[str], default: None)
  - Eindeutiger Key für die Komponente

#### Badge-Konfiguration

Jedes Badge in der `badges`-Liste ist ein Dict mit folgenden Parametern:

```python
{
    "text": str,              # erforderlich
    "variant": str,           # optional, default: "default"
    "size": str,              # optional, default: "md"
    "icon": str,              # optional
    "dot": bool,              # optional, default: False
    "custom_css": str,        # optional
    "key": str                # optional
}
```

#### Beispiele

**Einfache Badge-Gruppe:**
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

**Mit Icons:**
```python
group.render(
    badges=[
        {"text": "Verified", "variant": "success", "icon": "✓"},
        {"text": "Premium", "variant": "warning", "icon": "⭐"},
        {"text": "New", "variant": "info", "icon": "🎉"}
    ]
)
```

**Mit verschiedenen Größen:**
```python
group.render(
    badges=[
        {"text": "Small", "size": "sm"},
        {"text": "Medium", "size": "md"},
        {"text": "Large", "size": "lg"}
    ]
)
```

**Mit Spacing:**
```python
# Small spacing
group.render(badges=[...], spacing="sm")

# Large spacing
group.render(badges=[...], spacing="lg")
```

**Ohne Wrapping:**
```python
group.render(
    badges=[...],
    wrap=False  # Badges bleiben in einer Zeile
)
```

### Convenience-Funktion: `badge_group()`

```python
def badge_group(
    badges: list[dict],
    spacing: Literal["sm", "md", "lg"] = "md",
    wrap: bool = True,
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> None
```

**Beispiel:**
```python
from components.badge import badge_group

badge_group(
    badges=[
        {"text": "Tag 1", "variant": "default"},
        {"text": "Tag 2", "variant": "success"}
    ]
)
```

## Theme-Integration

Alle Komponenten verwenden Theme-Tokens für konsistentes Styling:

### Farben

- `colors.info` - Info-Farbe (blau)
- `colors.success` - Erfolg-Farbe (grün)
- `colors.warning` - Warn-Farbe (orange)
- `colors.error` - Fehler-Farbe (rot)
- `colors.primary` - Primär-Farbe
- `colors.secondary` - Sekundär-Farbe
- `colors.background` - Hintergrund-Farbe
- `colors.foreground` - Vordergrund-Farbe
- `colors.border` - Border-Farbe
- `colors.muted_foreground` - Gedämpfte Vordergrund-Farbe

### Borders

- `borders.border_radius_md` - Mittlerer Border-Radius
- `borders.border_radius_lg` - Großer Border-Radius
- `borders.border_radius_full` - Voller Border-Radius (Kreis)

### Spacing

- `spacing.spacing_4` - 1rem
- `spacing.spacing_6` - 1.5rem

### Shadows

- `shadows.shadow_sm` - Kleiner Schatten
- `shadows.shadow_md` - Mittlerer Schatten
- `shadows.shadow_lg` - Großer Schatten
- `shadows.shadow_xl` - Extra großer Schatten

### Animations

- `animations.transition_base` - Standard-Transition (200ms)

## Best Practices

### Alert

1. **Verwende passende Typen**
   - `info` für allgemeine Informationen
   - `success` für erfolgreiche Aktionen
   - `warning` für Warnungen
   - `error` für Fehler

2. **Verwende Titel für wichtige Alerts**
   ```python
   alert(message="...", type="error", title="Fehler")
   ```

3. **Verwende dismissible für nicht-kritische Alerts**
   ```python
   alert(message="...", dismissible=True, key="unique_key")
   ```

4. **Verwende eindeutige Keys für dismissible Alerts**
   ```python
   alert(message="...", dismissible=True, key="my_alert_1")
   ```

### AlertDialog

1. **Verwende für Bestätigungen**
   ```python
   if alert_dialog(title="Löschen?", ...):
       delete_item()
   ```

2. **Verwende cancel_text für wichtige Entscheidungen**
   ```python
   alert_dialog(
       title="Warnung",
       message="...",
       cancel_text="Abbrechen"
   )
   ```

3. **Verwende Callbacks für komplexe Logik**
   ```python
   alert_dialog(
       title="...",
       message="...",
       on_confirm=handle_confirm,
       on_cancel=handle_cancel
   )
   ```

### Badge

1. **Verwende konsistente Varianten**
   - `success` für positive Status
   - `warning` für Aufmerksamkeit
   - `error` für Probleme
   - `info` für neutrale Informationen

2. **Verwende Icons für bessere Erkennbarkeit**
   ```python
   badge(text="Verified", variant="success", icon="✓")
   ```

3. **Verwende Dot für Status-Anzeigen**
   ```python
   badge(text="Online", variant="success", dot=True)
   ```

4. **Verwende passende Größen**
   - `sm` für kompakte Darstellung
   - `md` für Standard-Darstellung
   - `lg` für prominente Darstellung

### BadgeGroup

1. **Verwende für Tags und Labels**
   ```python
   badge_group(badges=[
       {"text": "Tag 1", "variant": "default"},
       {"text": "Tag 2", "variant": "default"}
   ])
   ```

2. **Verwende wrap für viele Badges**
   ```python
   badge_group(badges=[...], wrap=True)
   ```

3. **Verwende konsistentes Spacing**
   ```python
   badge_group(badges=[...], spacing="md")
   ```

## Fehlerbehandlung

Alle Komponenten sind robust gegen Fehler:

- Fehlende Theme-Manager werden aus Session State geladen
- Ungültige Parameter verwenden Fallback-Werte
- CSS-Injection-Fehler werden abgefangen
- Komponenten funktionieren auch ohne Theme-System

## Performance

- CSS wird nur einmal pro Komponente injiziert
- Dismissible Alerts verwenden Session State für Persistenz
- Badge Groups rendern effizient viele Badges
- Keine unnötigen Re-Renders

## Accessibility

- Alle Komponenten verwenden semantisches HTML
- Farben haben ausreichend Kontrast (WCAG AA)
- Icons sind optional und ergänzen Text
- Keyboard-Navigation wird unterstützt

## Browser-Kompatibilität

Alle Komponenten funktionieren in:
- Chrome/Edge (neueste Versionen)
- Firefox (neueste Versionen)
- Safari (neueste Versionen)

## Demo

Führe die Demo-Datei aus, um alle Features zu sehen:

```bash
streamlit run demo_alert_badge.py
```
