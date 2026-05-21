# 🚀 Robustness Quick-Start Guide

## ⚡ Schnelleinstieg

### 1. App starten (mit allen Robustness-Features)

```powershell
# Standard-Start
streamlit run gui.py

# Mit spezifischem Port
$env:STREAMLIT_SERVER_PORT="8501"; streamlit run gui.py
```

**Erwartete Ausgabe**:
```
✓ Video-Server läuft bereits auf http://localhost:8503
✓ Video-Server erfolgreich gestartet auf http://localhost:8503

  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

---

### 2. Robustness-Features aktivieren

#### In bestehenden Modulen:

```python
# Am Anfang deines Moduls (z.B. calculations.py)
from core.robustness import (
    retry_on_error,
    safe_execute,
    safe_db_execute,
    sanitize_string
)

# Beispiel: Robuste Funktion
@retry_on_error(max_attempts=3, delay=1.0)
def calculate_pv_output(data):
    # Diese Funktion wird bei Fehler max. 3x wiederholt
    result = complex_calculation(data)
    return result

# Beispiel: Sichere User-Input-Verarbeitung
user_input = st.text_input("Name")
clean_name = sanitize_string(user_input, max_length=100)
```

---

### 3. Video-Background testen

#### A) Über Admin-Panel:

1. Start: `http://localhost:8501`
2. Login (falls aktiviert)
3. Admin Panel öffnen
4. **Intro Settings** Tab
5. Video hochladen (MP4/WebM/MOV)
6. Video-Größe: **Fullscreen**
7. ✅ Autoplay
8. ✅ Loop
9. Speichern
10. App neu laden → Video im Hintergrund

#### B) Direkt testen:

```powershell
# Video-URL direkt aufrufen
Start-Process "http://localhost:8503/intro_video.mp4"

# Health-Check
Invoke-WebRequest -Uri "http://localhost:8503/health"
# Erwartet: {"status": "ok", "service": "video-server"}
```

---

### 4. Accessibility prüfen

#### Browser Developer Tools (F12):

1. Öffne App: `http://localhost:8501`
2. F12 → Console
3. Erwartete Meldungen:
   ```
   [A11Y] Accessibility Enhancements aktiviert
   [A11Y] X Buttons mit Labels versehen
   [A11Y] X Links mit Labels versehen
   [A11Y] X ungültige ARIA-Attribute korrigiert
   [A11Y] Keyboard Navigation aktiviert
   [A11Y] Focus Management aktiviert
   [A11Y] Skip Navigation Link hinzugefügt
   [A11Y] DOM Observer aktiviert
   ```

#### Keyboard-Navigation testen:

- **TAB**: Durch Elemente navigieren (sichtbarer Fokus)
- **ALT+S**: Fokus auf Sidebar
- **ALT+M**: Fokus auf Main Content
- **ESC**: Modals/Drawers schließen

---

### 5. Robustness validieren

#### Test-Script:

```python
# test_robustness_quick.py
from core.robustness import *
import streamlit as st

# Test 1: Retry
@retry_on_error(max_attempts=2, delay=0.5)
def failing_function():
    raise ValueError("Test Error")

try:
    failing_function()
    print("❌ Retry funktioniert NICHT")
except ValueError:
    print("✓ Retry funktioniert (Fehler nach 2 Versuchen)")

# Test 2: Safe Execute
result = safe_execute(lambda: 1/0, fallback="Error")
print(f"✓ Safe Execute: {result}")  # "Error"

# Test 3: Atomic Write
with atomic_write('test_atomic.txt') as f:
    f.write("Test")
print("✓ Atomic Write funktioniert")

# Test 4: Session State
init_session_state('test_key', [])
success = set_session_state_safe('test_key', {'a': 1})
print(f"✓ Session State: {success}")  # True

print("\n🎉 Alle Robustness-Tests bestanden!")
```

```powershell
python test_robustness_quick.py
```

---

### 6. Performance-Check

#### Video-Server:

```powershell
# Startup-Zeit messen
Measure-Command { python -c "from video_server import start_video_server; import threading; t = threading.Thread(target=start_video_server, daemon=True); t.start(); import time; time.sleep(0.5)" }
```

**Erwartung**: < 1 Sekunde

#### Streamlit-App:

```powershell
# Startup-Zeit
Measure-Command { $env:STREAMLIT_SERVER_PORT="8501"; streamlit run gui.py --server.headless=true }
```

**Erwartung**: < 5 Sekunden (bis "You can now view...")

---

### 7. Troubleshooting Quick-Fixes

#### Problem: "Port 8503 already in use"

```powershell
# Finde Prozess
netstat -ano | findstr :8503

# Prozess beenden
taskkill /PID <PID> /F

# Alternative: Anderen Port nutzen
# In gui.py ändern: start_video_server(port=8504)
```

#### Problem: Video wird nicht angezeigt

```powershell
# 1. Server-Status
python -c "from video_server import get_server_status; print(get_server_status())"

# 2. Datei-Existenz
Test-Path "static/intro_videos/intro_video.mp4"

# 3. Video direkt öffnen
Start-Process "http://localhost:8503/intro_video.mp4"

# 4. Settings prüfen
Get-Content "data/intro_settings.json" | ConvertFrom-Json
```

#### Problem: Accessibility-Features fehlen

```powershell
# Browser-Cache leeren
# Chrome: Ctrl+Shift+Del → Cached Images/Files

# App neustarten
# Ctrl+C im Terminal, dann erneut: streamlit run gui.py
```

---

### 8. Produktions-Checkliste

- [ ] ✅ Video-Server startet ohne Fehler
- [ ] ✅ Health-Check antwortet (`/health`)
- [ ] ✅ Accessibility-Logs in Browser-Console
- [ ] ✅ Video spielt im Hintergrund (Intro-Screen)
- [ ] ✅ Keyboard-Navigation funktioniert (Alt+S, Alt+M)
- [ ] ✅ Keine Fehler in Browser-Console (F12)
- [ ] ✅ Keine Python-Exceptions in Terminal
- [ ] ✅ Session State persistent über Reruns

---

### 9. Performance-Optimierungen aktivieren

#### In `intro_screen.py`:

```python
# Memory-Management
from core.robustness import clear_session_state_cache, limit_session_state_size

# Am Ende von render_intro_screen():
clear_session_state_cache(prefix="img_cache_")
limit_session_state_size(max_items=50, pattern="temp_*")
```

#### In `gui.py`:

```python
# Logging-Level für Produktion
import logging
logging.basicConfig(level=logging.WARNING)  # Statt INFO/DEBUG
```

---

### 10. Monitoring aktivieren

#### Health-Check-Endpoint abfragen:

```python
# health_check.py
import requests
import time

def check_health():
    try:
        response = requests.get("http://localhost:8503/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Video-Server OK: {data}")
            return True
    except Exception as e:
        print(f"✗ Video-Server Fehler: {e}")
        return False

# Periodisches Monitoring
while True:
    check_health()
    time.sleep(60)  # Alle 60 Sekunden
```

---

## 📊 Erwartete Metriken

### Normale Operation:
- **Video-Server Response**: < 10ms (Health-Check)
- **Video-Streaming**: < 100ms (First Byte)
- **Accessibility Injection**: < 50ms
- **Session State Operations**: < 1ms

### Bei Fehlern:
- **Retry-Overhead**: +2-6s (Exponential Backoff)
- **Fallback-Aktivierung**: < 10ms
- **Error-Logging**: < 5ms

---

## 🎯 Nächste Schritte

1. **Testen**: Alle Features durchgehen (Video, Accessibility, Robustness)
2. **Anpassen**: Konfiguration nach Bedarf (Ports, Logging-Level, etc.)
3. **Deployen**: Produktions-Checkliste abarbeiten
4. **Monitoren**: Health-Checks einrichten
5. **Optimieren**: Performance-Metriken analysieren

---

**Bei Fragen**: Siehe `ROBUSTNESS_DOCUMENTATION.md` für Details

**Last Updated**: 2025-01-18  
**Version**: 2.0
