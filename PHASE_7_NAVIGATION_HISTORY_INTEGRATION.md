# Phase 7: Navigation History Integration - Dokumentation

## Übersicht

Phase 7 implementiert ein vollständiges **Navigation History System** für ARSCHIBALD mit:
- User Navigation Tracking
- Browser-ähnliche Back/Forward-Navigation  
- Automatische Breadcrumb-Generierung
- Seiten-Besuchsstatistiken
- Session-Persistenz

## Architektur

### Komponenten

1. **NavigationHistory** (`core/navigation_history.py`)
   - Verwaltet Navigation-Stack mit max. 100 Einträgen
   - Speichert Page, Params, Timestamp, Duration, User-ID
   - Pickle-serializable für Session State

2. **Router Integration** (`core/router.py`)
   - Automatisches Tracking bei jeder Navigation
   - Integration mit Middleware & Guards
   - Event-basierte Benachrichtigungen

3. **Core Integration** (`core_integration.py`)
   - `get_navigation_history()` - Globale Instanz abrufen
   - `track_navigation()` - Manuelles Tracking
   - Feature-Flag: `FEATURE_NAVIGATION_HISTORY=true`

4. **Admin Dashboard** (`admin_core_status_extended_ui.py`)
   - Echtzeit-Statistiken
   - History Size, Current Position
   - Top 10 Seiten-Besuche
   - Aktuelle Breadcrumbs

## Verwendung

### 1. Navigation Tracking (Automatisch)

```python
from core.router import get_router

router = get_router()

# Navigate automatisch tracked in NavigationHistory
router.navigate('crm', params={'customer_id': 123})
```

### 2. Manuelles Tracking

```python
from core_integration import track_navigation

# Manuell tracken (falls Router nicht genutzt wird)
track_navigation(
    page='pdf_generation',
    user_id='user_123',
    params={'project_id': 456},
    metadata={'source': 'button_click'}
)
```

### 3. Breadcrumbs Rendern

```python
from core_integration import get_navigation_history
from core.navigation_history import render_breadcrumbs

# NavigationHistory holen
nav_hist = get_navigation_history()

# Seiten-Titel registrieren
nav_hist.register_page_title('home', 'Startseite')
nav_hist.register_page_title('crm', 'CRM')
nav_hist.register_page_title('pdf', 'PDF-Generierung')

# Icons registrieren (optional)
nav_hist.register_page_icon('home', '🏠')
nav_hist.register_page_icon('crm', '👥')
nav_hist.register_page_icon('pdf', '📄')

# Breadcrumbs abrufen und rendern
breadcrumbs = nav_hist.get_breadcrumbs(max_items=5, include_home=True)

def on_breadcrumb_click(page, params):
    router.navigate(page, params)

render_breadcrumbs(breadcrumbs, on_click=on_breadcrumb_click)
```

### 4. Back/Forward Navigation

```python
from core_integration import get_navigation_history

nav_hist = get_navigation_history()

# Zurück navigieren
if nav_hist.can_go_back():
    prev_entry = nav_hist.back()
    router.navigate(prev_entry.page, prev_entry.params)

# Vorwärts navigieren
if nav_hist.can_go_forward():
    next_entry = nav_hist.forward()
    router.navigate(next_entry.page, next_entry.params)
```

### 5. Seiten-Statistiken

```python
from core_integration import get_navigation_history

nav_hist = get_navigation_history()

# Top-besuchte Seiten
page_visits = nav_hist.get_page_visits()
print(f"CRM-Besuche: {page_visits.get('crm', 0)}")

# Komplette User Journey
journey = nav_hist.get_journey()
for entry in journey:
    print(f"{entry.timestamp}: {entry.page} (Duration: {entry.duration})")
```

## Integration in gui.py

### Beispiel-Integration

```python
import streamlit as st
from core_integration import get_navigation_history, is_feature_enabled
from core.navigation_history import render_breadcrumbs
from core.router import get_router

def render_app():
    """Haupt-App mit Navigation Tracking"""
    
    # Router & NavigationHistory holen
    router = get_router()
    nav_hist = get_navigation_history() if is_feature_enabled('navigation') else None
    
    # Seiten-Titel registrieren
    if nav_hist:
        nav_hist.register_page_title('home', 'Startseite')
        nav_hist.register_page_title('pv', 'PV-Konfiguration')
        nav_hist.register_page_title('heatpump', 'Wärmepumpe')
        nav_hist.register_page_title('crm', 'CRM')
        nav_hist.register_page_title('pdf', 'PDF-Angebote')
        nav_hist.register_page_title('admin', 'Administration')
        
        # Icons
        nav_hist.register_page_icon('home', '🏠')
        nav_hist.register_page_icon('pv', '☀️')
        nav_hist.register_page_icon('heatpump', '🔥')
        nav_hist.register_page_icon('crm', '👥')
        nav_hist.register_page_icon('pdf', '📄')
        nav_hist.register_page_icon('admin', '⚙️')
    
    # Breadcrumbs rendern (oben auf jeder Seite)
    if nav_hist:
        breadcrumbs = nav_hist.get_breadcrumbs(max_items=5, include_home=True)
        if breadcrumbs:
            def on_breadcrumb_click(page, params):
                router.navigate(page, params)
            
            render_breadcrumbs(breadcrumbs, on_click=on_breadcrumb_click)
    
    # Back/Forward Buttons in Sidebar
    if nav_hist:
        st.sidebar.markdown("---")
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if nav_hist.can_go_back():
                if st.button("◄ Zurück", key="nav_back"):
                    prev_entry = nav_hist.back()
                    router.navigate(prev_entry.page, prev_entry.params)
                    st.rerun()
        
        with col2:
            if nav_hist.can_go_forward():
                if st.button("Vorwärts ►", key="nav_forward"):
                    next_entry = nav_hist.forward()
                    router.navigate(next_entry.page, next_entry.params)
                    st.rerun()
    
    # Tab-Auswahl (Tracking automatisch via Router)
    selected_tab = st.sidebar.radio(
        "Navigation",
        ['home', 'pv', 'heatpump', 'crm', 'pdf', 'admin']
    )
    
    # Navigation via Router (automatisches Tracking!)
    if selected_tab != router.current_page:
        router.navigate(selected_tab)
    
    # Tab-Content rendern
    render_tab_content(selected_tab)
```

## Konfiguration

### Environment Variables

```bash
# Phase 7 aktivieren (Standard: true)
FEATURE_NAVIGATION_HISTORY=true
```

### Feature-Flags in core_integration.py

```python
FEATURES = {
    'navigation': os.getenv('FEATURE_NAVIGATION_HISTORY', 'true').lower() == 'true',
}
```

## Admin Dashboard

### Statistiken anzeigen

```bash
# Admin Dashboard starten
streamlit run admin_core_status_extended_ui.py
```

**Anzeige umfasst:**
- ✅ History Size (Anzahl Einträge)
- ✅ Current Position (Index im Stack)
- ✅ Can Go Back/Forward (Boolean)
- ✅ Top 10 Seiten-Besuche (Page → Count)
- ✅ Aktuelle Breadcrumbs mit Icons

## API-Referenz

### NavigationHistory Class

```python
class NavigationHistory:
    def push(page: str, params: dict = None, user_id: str = None, 
             session_id: str = None, metadata: dict = None) -> None
        """Push new entry to history"""
    
    def back() -> HistoryEntry | None
        """Navigate back in history"""
    
    def forward() -> HistoryEntry | None
        """Navigate forward in history"""
    
    def can_go_back() -> bool
        """Check if can navigate back"""
    
    def can_go_forward() -> bool
        """Check if can navigate forward"""
    
    def get_current() -> HistoryEntry | None
        """Get current history entry"""
    
    def get_breadcrumbs(max_items: int = 5, include_home: bool = True) -> list[Breadcrumb]
        """Generate breadcrumbs from history"""
    
    def get_page_visits() -> dict[str, int]
        """Get page visit counts"""
    
    def get_journey() -> list[HistoryEntry]
        """Get complete user journey"""
    
    def clear() -> None
        """Clear history"""
```

### HistoryEntry Dataclass

```python
@dataclass
class HistoryEntry:
    page: str
    params: dict[str, Any]
    timestamp: datetime
    duration: timedelta | None = None
    user_id: str | None = None
    session_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
```

### Breadcrumb Dataclass

```python
@dataclass
class Breadcrumb:
    label: str
    page: str
    params: dict[str, Any] = field(default_factory=dict)
    icon: str | None = None
    is_current: bool = False
```

## Testing

### Unit Tests

```python
import pytest
from core.navigation_history import NavigationHistory

def test_navigation_push():
    nav = NavigationHistory()
    nav.push('home')
    nav.push('crm', params={'customer_id': 123})
    
    assert len(nav.history) == 2
    assert nav.current_index == 1

def test_navigation_back_forward():
    nav = NavigationHistory()
    nav.push('home')
    nav.push('crm')
    nav.push('pdf')
    
    # Back
    entry = nav.back()
    assert entry.page == 'crm'
    assert nav.current_index == 1
    
    # Forward
    entry = nav.forward()
    assert entry.page == 'pdf'
    assert nav.current_index == 2

def test_breadcrumbs():
    nav = NavigationHistory()
    nav.register_page_title('home', 'Startseite')
    nav.register_page_title('crm', 'CRM')
    
    nav.push('home')
    nav.push('crm', params={'customer_id': 123})
    
    breadcrumbs = nav.get_breadcrumbs()
    assert len(breadcrumbs) == 2
    assert breadcrumbs[0].label == 'Startseite'
    assert breadcrumbs[1].label == 'CRM'
    assert breadcrumbs[1].is_current == True
```

## Troubleshooting

### Problem: NavigationHistory nicht verfügbar

**Ursache:** Feature deaktiviert oder Import-Fehler

**Lösung:**
```python
from core_integration import is_feature_enabled

if not is_feature_enabled('navigation'):
    # Aktivieren in .env
    # FEATURE_NAVIGATION_HISTORY=true
    pass
```

### Problem: Breadcrumbs zeigen falsche Titel

**Ursache:** Seiten-Titel nicht registriert

**Lösung:**
```python
nav_hist = get_navigation_history()
nav_hist.register_page_title('my_page', 'Mein Seitentitel')
```

### Problem: Back/Forward funktioniert nicht

**Ursache:** Router nicht synchronisiert mit NavigationHistory

**Lösung:**
```python
# Verwende Router für Navigation (nicht direktes Session State Update)
from core.router import get_router

router = get_router()
router.navigate('page', params)  # Automatisches Tracking!
```

## Performance

### Speicherverbrauch

- **Max History Size:** 100 Einträge (konfigurierbar)
- **Pro Entry:** ~200 Bytes (ohne große Params)
- **Gesamt:** ~20 KB pro User-Session

### Optimierungen

1. **Deque mit maxlen:** Automatisches Pruning alter Einträge
2. **Pickle-Serialization:** Effiziente Session State Speicherung
3. **Lazy Loading:** Breadcrumbs nur bei Bedarf generiert

## Roadmap

### Phase 7.1 - Analytics (Geplant)

- [ ] Navigation-Heatmaps
- [ ] User-Flow-Visualisierung
- [ ] A/B-Testing Support
- [ ] Export zu Analytics-Tools

### Phase 7.2 - Advanced Features (Geplant)

- [ ] Named Navigation States
- [ ] Deeplink-Support
- [ ] Navigation Guards mit Async
- [ ] Multi-Session Navigation

---

**Status:** ✅ **Vollständig implementiert und getestet**  
**Version:** 1.0  
**Letzte Aktualisierung:** 2025-01-18
