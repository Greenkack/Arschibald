# State Manager Reference

## Overview

Das State Management System verwaltet Theme-Präferenzen über mehrere Backend-Optionen und implementiert Fallback-Mechanismen für maximale Zuverlässigkeit.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              ThemeStateManager                          │
│                                                         │
│  - Zentrale Verwaltung                                 │
│  - Multi-Backend-Support                               │
│  - Automatisches Fallback                              │
│  - State Recovery                                      │
└────────────┬────────────────────────────────────────────┘
             │
             ├──────────────┬──────────────┬──────────────┐
             │              │              │              │
    ┌────────▼────────┐ ┌──▼──────────┐ ┌─▼─────────────┐
    │ SessionState    │ │ LocalStorage│ │ Database      │
    │ Backend         │ │ Backend     │ │ Backend       │
    │                 │ │             │ │               │
    │ - Schnell       │ │ - Persistent│ │ - Zentral     │
    │ - Temporär      │ │ - Browser   │ │ - Multi-User  │
    └─────────────────┘ └─────────────┘ └───────────────┘
```

## Components

### ThemeStateManager

Zentrale Klasse für State Management.

```python
from theming.state_manager import ThemeStateManager

# Initialisierung
state_manager = ThemeStateManager(
    backends=['session', 'local_storage', 'database']
)

# Theme speichern
state_manager.save_theme_preference(
    user_id='user123',
    theme_name='shadcn-dark'
)

# Theme laden
theme_name = state_manager.load_theme_preference(user_id='user123')

# State Recovery
recovered_theme = state_manager.recover_state(user_id='user123')
```

### SessionStateBackend

Speichert Theme-Präferenzen in Streamlit Session State.

**Eigenschaften:**
- ✅ Sehr schnell
- ✅ Keine Persistierung nötig
- ❌ Verloren bei Browser-Refresh
- ❌ Nicht zwischen Tabs geteilt

```python
from theming.state_manager import SessionStateBackend

backend = SessionStateBackend()

# Speichern
backend.save('user123', 'shadcn-dark')

# Laden
theme = backend.load('user123')

# Prüfen
exists = backend.exists('user123')

# Löschen
backend.delete('user123')
```

### LocalStorageBackend

Speichert Theme-Präferenzen im Browser Local Storage.

**Eigenschaften:**
- ✅ Persistent über Browser-Refreshs
- ✅ Zwischen Tabs synchronisierbar
- ✅ Kein Server-Zugriff nötig
- ❌ Browser-spezifisch
- ❌ Begrenzte Größe (5-10MB)

```python
from theming.state_manager import LocalStorageBackend

backend = LocalStorageBackend()

# Speichern (mit JavaScript)
backend.save('user123', 'shadcn-dark')

# Laden
theme = backend.load('user123')

# Tab-Synchronisation aktivieren
backend.sync_listener()
```

**JavaScript-Integration:**

Das Backend verwendet JavaScript für Local Storage Zugriff:

```javascript
// Automatisch generierter Code
localStorage.setItem('shadcn_theme_user123', JSON.stringify({
    theme_name: 'shadcn-dark',
    timestamp: new Date().toISOString(),
    backend: 'local_storage'
}));

// Storage Event für Tab-Sync
window.addEventListener('storage', function(e) {
    if (e.key && e.key.startsWith('shadcn_theme_')) {
        window.location.reload();
    }
});
```

### DatabaseBackend

Speichert Theme-Präferenzen in SQLite-Datenbank.

**Eigenschaften:**
- ✅ Zentrale Speicherung
- ✅ Multi-User-Support
- ✅ Historisierung möglich
- ✅ Backup-fähig
- ❌ Langsamer als andere Backends

```python
from theming.state_manager import DatabaseBackend

backend = DatabaseBackend(db_path='theming/theme_preferences.db')

# Speichern mit Metadata
backend.save('user123', 'shadcn-dark', metadata={
    'device': 'desktop',
    'browser': 'chrome'
})

# Laden
theme = backend.load('user123')

# Alle Präferenzen abrufen
all_prefs = backend.get_all_preferences()
```

**Datenbank-Schema:**

```sql
CREATE TABLE user_theme_preferences (
    user_id TEXT PRIMARY KEY,
    theme_name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata TEXT
);
```

## Usage Examples

### Basic Usage

```python
import streamlit as st
from theming.state_manager import ThemeStateManager

# Initialisierung (einmalig beim App-Start)
if 'state_manager' not in st.session_state:
    st.session_state.state_manager = ThemeStateManager(
        backends=['session', 'local_storage']
    )

state_manager = st.session_state.state_manager

# User-ID ermitteln (z.B. aus Login-System)
user_id = st.session_state.get('user_id', 'default_user')

# Theme laden
current_theme = state_manager.load_theme_preference(user_id)
if not current_theme:
    current_theme = 'shadcn-default'

# Theme-Selector
new_theme = st.selectbox(
    'Theme',
    ['shadcn-default', 'shadcn-dark', 'shadcn-ocean'],
    index=['shadcn-default', 'shadcn-dark', 'shadcn-ocean'].index(current_theme)
)

# Theme speichern wenn geändert
if new_theme != current_theme:
    state_manager.save_theme_preference(user_id, new_theme)
    st.rerun()
```

### Multi-Backend Strategy

```python
# Speichere in allen Backends für maximale Redundanz
results = state_manager.save_theme_preference(
    user_id='user123',
    theme_name='shadcn-dark',
    backends=['session', 'local_storage', 'database']
)

# Prüfe Erfolg
for backend, success in results.items():
    if success:
        st.success(f"✅ Saved to {backend}")
    else:
        st.warning(f"⚠️ Failed to save to {backend}")
```

### State Recovery

```python
# Bei App-Start: Versuche State Recovery
user_id = st.session_state.get('user_id', 'default_user')

# Prüfe ob Theme in Session State vorhanden
if 'current_theme' not in st.session_state:
    # Versuche Recovery aus anderen Backends
    recovered_theme = state_manager.recover_state(user_id)
    
    if recovered_theme:
        st.session_state.current_theme = recovered_theme
        st.success(f"🔄 Theme wiederhergestellt: {recovered_theme}")
    else:
        # Fallback auf Default-Theme
        st.session_state.current_theme = 'shadcn-default'
```

### Tab Synchronization

```python
# Aktiviere Tab-Synchronisation
state_manager.enable_tab_sync()

# Wenn Theme in einem Tab geändert wird, werden andere Tabs
# automatisch neu geladen und zeigen das neue Theme
```

### Backend Synchronization

```python
# Synchronisiere Theme von einem Backend zu allen anderen
results = state_manager.sync_across_backends(
    user_id='user123',
    source_backend='database'
)

# Prüfe Sync-Status
for backend, success in results.items():
    st.write(f"{backend}: {'✅' if success else '❌'}")
```

## Advanced Features

### Custom Backend Priority

```python
# Lade Theme mit custom Backend-Reihenfolge
theme = state_manager.load_theme_preference(
    user_id='user123',
    backends=['database', 'local_storage', 'session']  # Priorität
)
```

### Backend Status Monitoring

```python
# Prüfe Status aller Backends
status = state_manager.get_backend_status()

for backend_name, info in status.items():
    st.write(f"{backend_name}: {info['type']}")
    if info['available']:
        st.success("✅ Available")
    else:
        st.error("❌ Unavailable")
```

### Selective Backend Usage

```python
# Speichere nur in bestimmten Backends
state_manager.save_theme_preference(
    user_id='user123',
    theme_name='shadcn-dark',
    backends=['session']  # Nur Session State
)

# Lade nur aus bestimmten Backends
theme = state_manager.load_theme_preference(
    user_id='user123',
    backends=['local_storage', 'database']  # Nicht Session State
)
```

## Integration with Theme Manager

```python
from theming.theme_manager import ThemeManager
from theming.state_manager import ThemeStateManager

# Initialisierung
theme_manager = ThemeManager()
state_manager = ThemeStateManager()

user_id = 'user123'

# Lade gespeicherte Theme-Präferenz
saved_theme = state_manager.load_theme_preference(user_id)

if saved_theme:
    # Setze Theme
    theme_manager.set_theme(saved_theme)
else:
    # Fallback auf Default
    theme_manager.set_theme('shadcn-default')

# Bei Theme-Wechsel
def on_theme_change(new_theme: str):
    theme_manager.set_theme(new_theme)
    state_manager.save_theme_preference(user_id, new_theme)
    st.rerun()
```

## Error Handling

```python
import logging

# Logging aktivieren
logging.basicConfig(level=logging.DEBUG)

try:
    # Theme speichern
    results = state_manager.save_theme_preference('user123', 'shadcn-dark')
    
    # Prüfe ob mindestens ein Backend erfolgreich war
    if not any(results.values()):
        st.error("❌ Konnte Theme in keinem Backend speichern")
    elif all(results.values()):
        st.success("✅ Theme in allen Backends gespeichert")
    else:
        st.warning("⚠️ Theme nur in einigen Backends gespeichert")
        
except Exception as e:
    st.error(f"❌ Fehler beim Speichern: {e}")
    # Fallback: Verwende nur Session State
    st.session_state.current_theme = 'shadcn-dark'
```

## Performance Considerations

### Backend Performance

| Backend | Save | Load | Persistent | Multi-Tab |
|---------|------|------|------------|-----------|
| Session | 🟢 <1ms | 🟢 <1ms | ❌ | ❌ |
| LocalStorage | 🟡 ~10ms | 🟡 ~10ms | ✅ | ✅ |
| Database | 🔴 ~50ms | 🔴 ~50ms | ✅ | ✅ |

### Optimization Tips

1. **Use Session State for Active Theme**
   ```python
   # Schneller Zugriff während Session
   current_theme = st.session_state.get('current_theme')
   ```

2. **Lazy Database Writes**
   ```python
   # Speichere in DB nur bei wichtigen Events
   if user_logged_in:
       state_manager.save_theme_preference(
           user_id, theme_name, backends=['database']
       )
   ```

3. **Batch Operations**
   ```python
   # Speichere mehrere Präferenzen auf einmal
   for user_id, theme in user_themes.items():
       state_manager.save_theme_preference(user_id, theme)
   ```

## Testing

```python
# Test Session State Backend
def test_session_backend():
    backend = SessionStateBackend()
    
    # Save
    assert backend.save('test_user', 'shadcn-dark') == True
    
    # Load
    assert backend.load('test_user') == 'shadcn-dark'
    
    # Exists
    assert backend.exists('test_user') == True
    
    # Delete
    assert backend.delete('test_user') == True
    assert backend.exists('test_user') == False

# Test State Manager
def test_state_manager():
    manager = ThemeStateManager(backends=['session'])
    
    # Save
    results = manager.save_theme_preference('test_user', 'shadcn-dark')
    assert results['session'] == True
    
    # Load
    theme = manager.load_theme_preference('test_user')
    assert theme == 'shadcn-dark'
    
    # Recovery
    recovered = manager.recover_state('test_user')
    assert recovered == 'shadcn-dark'
```

## Troubleshooting

### Theme nicht persistent

**Problem:** Theme geht bei Browser-Refresh verloren

**Lösung:**
```python
# Stelle sicher dass Local Storage oder Database Backend aktiv ist
state_manager = ThemeStateManager(
    backends=['session', 'local_storage']  # Nicht nur 'session'
)
```

### Tab-Synchronisation funktioniert nicht

**Problem:** Theme-Änderungen werden nicht in anderen Tabs angezeigt

**Lösung:**
```python
# Aktiviere Tab-Sync explizit
state_manager.enable_tab_sync()

# Stelle sicher dass Local Storage Backend verwendet wird
if 'local_storage' not in state_manager.backend_names:
    st.warning("Local Storage Backend nicht aktiv")
```

### Database Errors

**Problem:** SQLite-Fehler beim Speichern

**Lösung:**
```python
# Prüfe Datenbankpfad und Berechtigungen
import os
db_path = 'theming/theme_preferences.db'

if not os.path.exists(os.path.dirname(db_path)):
    os.makedirs(os.path.dirname(db_path))

# Verwende absoluten Pfad
db_path = os.path.abspath(db_path)
state_manager = ThemeStateManager(
    backends=['database'],
    db_path=db_path
)
```

## Best Practices

1. **Use Multiple Backends**
   - Session State für Performance
   - Local Storage für Persistenz
   - Database für Multi-Device-Support

2. **Implement Fallbacks**
   - Immer Default-Theme bereitstellen
   - Graceful Degradation bei Backend-Fehlern

3. **Log Everything**
   - Aktiviere Logging für Debugging
   - Monitore Backend-Erfolgsraten

4. **Test Recovery**
   - Teste State Recovery regelmäßig
   - Simuliere Browser-Refreshs

5. **Secure User Data**
   - Validiere User-IDs
   - Sanitize Theme-Namen
   - Implementiere Access Control

## API Reference

### ThemeStateManager

#### `__init__(backends, db_path)`
Initialisiert State Manager

#### `save_theme_preference(user_id, theme_name, backends)`
Speichert Theme-Präferenz

#### `load_theme_preference(user_id, backends)`
Lädt Theme-Präferenz

#### `delete_theme_preference(user_id, backends)`
Löscht Theme-Präferenz

#### `sync_across_backends(user_id, source_backend)`
Synchronisiert über Backends

#### `recover_state(user_id)`
State Recovery

#### `get_backend_status()`
Backend-Status

#### `enable_tab_sync()`
Tab-Synchronisation

### StateBackend (Interface)

#### `save(user_id, theme_name)`
Speichert Theme

#### `load(user_id)`
Lädt Theme

#### `delete(user_id)`
Löscht Theme

#### `exists(user_id)`
Prüft Existenz

## See Also

- [Theme Manager Reference](THEME_MANAGER_REFERENCE.md)
- [Theme Selector Reference](THEME_SELECTOR_REFERENCE.md)
- [Error Handling Reference](ERROR_HANDLING_REFERENCE.md)
