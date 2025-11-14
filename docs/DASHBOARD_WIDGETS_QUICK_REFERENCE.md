# Dashboard Widgets System - Quick Reference

## Übersicht

Das Dashboard Widget System ermöglicht ein konfigurierbares, modulares Dashboard mit Echtzeit-Updates für das CRM-System.

## Verfügbare Widgets

### 1. Offene Aufgaben Widget (📋)
- Zeigt die nächsten 10 offenen Aufgaben
- Sortiert nach Priorität und Fälligkeit
- Hebt überfällige Aufgaben rot hervor
- Zeigt Prioritäts-Icons (🔴 Hoch, 🟡 Mittel, 🟢 Niedrig)

### 2. Anstehende Termine Widget (📅)
- Zeigt Termine der nächsten 7 Tage
- Hebt heutige Termine rot hervor
- Zeigt morgige Termine gelb hervor
- Inkludiert Zeit und Ort

### 3. Pipeline-Übersicht Widget (🎯)
- Zeigt Lead-Status-Verteilung
- Visualisiert Anzahl und Wert pro Stage
- Farbcodierte Status-Karten
- Fokus auf aktive Stages (Neu, Qualifiziert, Angebot, Verhandlung)

### 4. Umsatz-Tracking Widget (💰)
- Monatsumsatz
- Jahresumsatz
- Durchschnittliche Deal-Größe
- Conversion Rate
- Alle Werte basierend auf gewonnenen Deals

## Widget-Konfiguration

### Sichtbarkeit steuern

```python
from crm.features.dashboard_widgets import WidgetManager

manager = WidgetManager()

# Konfiguration laden
config = manager.get_widget_config(user_id="default")

# Widget verstecken
config['open_tasks']['visible'] = False

# Speichern
manager.save_widget_config(user_id="default", config=config)
```

### Reihenfolge ändern

```python
# Niedrigere Order-Werte werden zuerst angezeigt
config['revenue_tracking']['order'] = 1  # Zuerst
config['open_tasks']['order'] = 2        # Zweiter
config['pipeline_overview']['order'] = 3  # Dritter
config['upcoming_appointments']['order'] = 4  # Vierter

manager.save_widget_config(user_id="default", config=config)
```

## Auto-Refresh

### Aktivieren

```python
from crm.features.dashboard_widgets import render_dashboard_with_widgets

render_dashboard_with_widgets(
    texts=texts,
    user_id="default",
    auto_refresh=True,
    refresh_interval=60  # Sekunden
)
```

### Verfügbare Intervalle
- 30 Sekunden
- 60 Sekunden (Standard)
- 120 Sekunden (2 Minuten)
- 300 Sekunden (5 Minuten)

## Integration in CRM Dashboard

### In crm_dashboard_ui.py

```python
def render_widgets_section(texts: dict[str, str]):
    """Widget-Sektion des CRM Dashboards"""
    
    from crm.features.dashboard_widgets import render_dashboard_with_widgets
    
    # Auto-Refresh Einstellungen aus Session State
    auto_refresh = st.session_state.get('dashboard_auto_refresh', False)
    refresh_interval = st.session_state.get('dashboard_refresh_interval', 60)
    
    # Rendere Dashboard mit Widgets
    render_dashboard_with_widgets(
        texts=texts,
        user_id="default",
        auto_refresh=auto_refresh,
        refresh_interval=refresh_interval
    )
```

## Eigene Widgets erstellen

### Widget-Klasse erstellen

```python
from crm.features.dashboard_widgets import DashboardWidget

class MyCustomWidget(DashboardWidget):
    """Mein eigenes Widget"""
    
    def __init__(self):
        super().__init__(
            widget_id="my_custom_widget",
            title="Mein Widget",
            icon="🎨",
            default_visible=True
        )
    
    def get_data(self):
        """Daten für das Widget holen"""
        # Implementiere Datenabfrage
        return {"key": "value"}
    
    def render(self, **kwargs):
        """Widget rendern"""
        import streamlit as st
        data = self.get_data()
        
        st.markdown(f"### {self.icon} {self.title}")
        st.write(data)
```

### Widget registrieren

```python
from crm.features.dashboard_widgets import WidgetManager

# In WidgetManager.__init__()
self.widgets = {
    'open_tasks': OpenTasksWidget(),
    'upcoming_appointments': UpcomingAppointmentsWidget(),
    'pipeline_overview': PipelineOverviewWidget(),
    'revenue_tracking': RevenueTrackingWidget(),
    'my_custom_widget': MyCustomWidget()  # Neues Widget
}
```

## Datenbank-Schema

### user_dashboard_settings Tabelle

```sql
CREATE TABLE user_dashboard_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL UNIQUE,
    widget_config TEXT,  -- JSON mit Widget-Konfiguration
    auto_refresh_enabled BOOLEAN DEFAULT 0,
    refresh_interval INTEGER DEFAULT 60,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Widget-Konfiguration JSON-Format

```json
{
    "open_tasks": {
        "visible": true,
        "order": 1
    },
    "upcoming_appointments": {
        "visible": true,
        "order": 2
    },
    "pipeline_overview": {
        "visible": false,
        "order": 3
    },
    "revenue_tracking": {
        "visible": true,
        "order": 4
    }
}
```

## Best Practices

### Performance

1. **Limitiere Datenabfragen**: Widgets sollten nur die nötigsten Daten laden
2. **Verwende Indizes**: Stelle sicher, dass häufig abgefragte Felder indiziert sind
3. **Cache wo möglich**: Nutze Streamlit's `@st.cache_data` für teure Berechnungen

### Benutzerfreundlichkeit

1. **Klare Icons**: Verwende eindeutige Emojis für jeden Widget-Typ
2. **Farbcodierung**: Nutze Farben konsistent (Rot = Dringend, Grün = OK)
3. **Tooltips**: Füge Erklärungen für komplexe Metriken hinzu

### Fehlerbehandlung

1. **Graceful Degradation**: Widgets sollten bei Fehlern Info-Meldungen zeigen
2. **Leere Zustände**: Zeige hilfreiche Meldungen wenn keine Daten vorhanden
3. **Datenbankfehler**: Fange Fehler ab und zeige Benutzer-freundliche Meldungen

## Troubleshooting

### Widget wird nicht angezeigt

1. Prüfe ob Widget in Konfiguration sichtbar ist:
   ```python
   config = manager.get_widget_config(user_id)
   print(config['widget_id']['visible'])
   ```

2. Prüfe ob Widget registriert ist:
   ```python
   manager = WidgetManager()
   print(manager.widgets.keys())
   ```

### Daten werden nicht geladen

1. Prüfe Datenbankverbindung:
   ```python
   from database import get_db_connection
   conn = get_db_connection()
   print(conn is not None)
   ```

2. Prüfe SQL-Queries in Widget's `get_data()` Methode

### Auto-Refresh funktioniert nicht

1. Stelle sicher, dass `auto_refresh=True` gesetzt ist
2. Prüfe ob `st.session_state.last_refresh` aktualisiert wird
3. Verifiziere dass `st.rerun()` aufgerufen wird

## Beispiele

### Minimales Dashboard

```python
import streamlit as st
from crm.features.dashboard_widgets import render_dashboard_with_widgets

st.set_page_config(page_title="CRM Dashboard", layout="wide")

texts = {"dashboard": "Dashboard"}

render_dashboard_with_widgets(
    texts=texts,
    user_id="demo_user",
    auto_refresh=False
)
```

### Dashboard mit Auto-Refresh

```python
import streamlit as st
from crm.features.dashboard_widgets import render_dashboard_with_widgets

st.set_page_config(page_title="CRM Dashboard", layout="wide")

texts = {"dashboard": "Dashboard"}

# Auto-Refresh alle 2 Minuten
render_dashboard_with_widgets(
    texts=texts,
    user_id="demo_user",
    auto_refresh=True,
    refresh_interval=120
)
```

### Benutzerdefinierte Widget-Konfiguration

```python
from crm.features.dashboard_widgets import WidgetManager

manager = WidgetManager()

# Nur Umsatz und Pipeline anzeigen
custom_config = {
    'open_tasks': {'visible': False, 'order': 3},
    'upcoming_appointments': {'visible': False, 'order': 4},
    'pipeline_overview': {'visible': True, 'order': 1},
    'revenue_tracking': {'visible': True, 'order': 2}
}

manager.save_widget_config("sales_manager", custom_config)
```

## Weitere Ressourcen

- **Modul**: `crm/features/dashboard_widgets.py`
- **Tests**: `crm/features/test_dashboard_widgets.py`
- **Integration**: `crm_dashboard_ui.py`
- **Datenbank**: `database.py` (user_dashboard_settings Tabelle)

## Support

Bei Fragen oder Problemen:
1. Prüfe die Tests für Beispiele
2. Schaue in die Modul-Dokumentation
3. Kontaktiere das Entwicklungsteam
