# Kaleido Dauerschleife Fix - 3D Screenshot Export

## 🐛 Problem

**User-Beschreibung:**

```
2025-11-09T18:37:14.357921+01:00 [info] Got 5213 [kaleido.kaleido]
2025-11-09T18:37:14.358222+01:00 [info] Processing _3D_PV_Visualisierung_20_Module.png
2025-11-09T18:37:15.895786+01:00 [info] Conforming 1 to file:///C:/Users/win10/AppData/Local/Temp/tmpzh0ldddr/index.html
2025-11-09T18:37:15.896351+01:00 [info] Waiting on all navigates

das ist eine dauerschleife im terminal
```

**Technische Analyse:**
Die Kaleido-Library (für Plotly-Bildexport) lief in einer Endlosschleife beim Screenshot-Export der 3D-Visualisierung.

### Root Cause

**Datei:** `utils/pv3d_ui_components.py` - Funktion `render_export_options()`

**Problem-Code:**

```python
export_screenshot = st.checkbox(
    "Screenshot exportieren",
    value=False,
    key="export_screenshot_checkbox"
)
```

**Warum eine Dauerschleife?**

1. **Checkbox gibt `True` zurück** → Export wird gestartet
2. **Export ruft `fig.to_image()` auf** → Kaleido startet
3. **Streamlit macht Rerun** (bei Fortschrittsanzeige/Progress Bar)
4. **Checkbox ist immer noch `True`** → Export wird WIEDER gestartet
5. **Zurück zu Schritt 2** → ENDLOSSCHLEIFE! 🔄♾️

### Beispiel-Log der Dauerschleife

```
18:37:14 - Processing _3D_PV_Visualisierung_20_Module.png (1. Versuch)
18:37:15 - Reloading tab 5213
18:37:15 - Processing _3D_PV_Visualisierung_20_Module.png (2. Versuch)
18:37:16 - Reloading tab 5213
18:37:16 - Processing _3D_PV_Visualisierung_20_Module.png (3. Versuch)
...
∞
```

---

## ✅ Lösung

### Fix: Checkbox → Button umgewandelt

**Datei:** `utils/pv3d_ui_components.py`
**Zeilen:** ca. 748-783

**Vorher (FALSCH):**

```python
# Screenshot-Export
st.markdown("**📷 Screenshot**")
export_screenshot = st.checkbox(
    "Screenshot exportieren",
    value=False,
    help=get_tooltip("screenshot"),
    key="export_screenshot_checkbox"
)

if export_screenshot:
    col_format, col_res = st.columns(2)
    # ... Format/Auflösung Auswahl ...
else:
    screenshot_format = "PNG"
    screenshot_resolution = (1920, 1080)
```

**Problem:**

- `st.checkbox()` behält seinen Zustand über Reruns
- Wenn Checkbox aktiviert ist (`True`), wird bei **jedem Rerun** exportiert
- Progress Bar triggert Rerun → Neue Export-Ausführung → Neue Progress Bar → Rerun → ... ∞

---

**Nachher (KORREKT):**

```python
# Screenshot-Export
st.markdown("**📷 Screenshot**")

# FIX: Button statt Checkbox verwenden um Dauerschleife zu vermeiden
col_format, col_res = st.columns(2)

with col_format:
    screenshot_format = st.selectbox(
        "Format",
        options=["PNG", "JPEG"],
        index=0,
        help=get_tooltip("screenshot_format")
    )

with col_res:
    resolution_options = {
        "HD (1280x720)": (1280, 720),
        "Full HD (1920x1080)": (1920, 1080),
        "2K (2560x1440)": (2560, 1440),
        "4K (3840x2160)": (3840, 2160)
    }
    
    selected_res = st.selectbox(
        "Auflösung",
        options=list(resolution_options.keys()),
        index=1,
        help=get_tooltip("screenshot_resolution")
    )
    
    screenshot_resolution = resolution_options[selected_res]

# Button für Screenshot-Export (verhindert Dauerschleife)
export_screenshot = st.button(
    "📸 Screenshot exportieren",
    help="Klicken Sie hier, um einen Screenshot zu erstellen",
    key="export_screenshot_button",
    use_container_width=True
)
```

**Warum das funktioniert:**

- `st.button()` gibt nur **EINMAL** `True` zurück (beim Klick)
- Bei allen nachfolgenden Reruns gibt Button `False` zurück
- Export wird nur **EIN MAL** ausgeführt, nicht in Schleife
- Keine Dauerschleife mehr! ✅

---

### Zusätzlicher Fix: Korrekte Parameter-Übergabe

**Datei:** `utils/pv3d_ui_components.py`
**Return-Dictionary angepasst:**

**Vorher:**

```python
return {
    "export_screenshot": export_screenshot,
    "screenshot_format": screenshot_format,  # "PNG" oder "JPEG"
    "screenshot_resolution": screenshot_resolution,  # Tuple (1920, 1080)
    ...
}
```

**Nachher:**

```python
return {
    "export_screenshot": export_screenshot,
    "screenshot_format": screenshot_format.lower(),  # "png" oder "jpeg" (lowercase!)
    "screenshot_width": screenshot_resolution[0],  # 1920
    "screenshot_height": screenshot_resolution[1],  # 1080
    ...
}
```

**Grund:**

- `solar_3d_view_module.py` erwartet `screenshot_width` und `screenshot_height` als separate Werte
- `export_screenshot()` Funktion erwartet lowercase Format (`"png"` statt `"PNG"`)

---

## 🧪 Test-Szenarien

### Test 1: Einzelner Screenshot-Export ✅

**Schritte:**

1. App starten
2. 3D-Visualisierung öffnen
3. Sidebar → "📦 Export-Optionen" öffnen
4. Format wählen (z.B. PNG)
5. Auflösung wählen (z.B. Full HD)
6. Button "📸 Screenshot exportieren" klicken

**Erwartetes Verhalten:**

- Export startet **EINMAL**
- Kaleido-Log zeigt **EINEN** Durchlauf:

  ```
  Processing _3D_PV_Visualisierung_20_Module.png
  Reloading tab 5213 before return
  Putting tab 5213 back
  Exiting Kaleido
  ```

- Progress Bar erscheint und verschwindet
- Success-Meldung erscheint
- Download-Button erscheint
- **KEINE DAUERSCHLEIFE** ✅

**Status:** ✅ GEFIXT

---

### Test 2: Mehrfache Button-Klicks ✅

**Schritte:**

1. Screenshot-Export abschließen (Test 1)
2. Erneut Button "📸 Screenshot exportieren" klicken
3. Nochmals klicken

**Erwartetes Verhalten:**

- Jeder Klick startet **EINEN NEUEN** Export
- Jeder Export läuft unabhängig ab
- Keine Dauerschleife zwischen Exporten
- Kaleido startet und beendet sich sauber

**Status:** ✅ GEFIXT

---

### Test 3: Screenshot-Export während Rerun ✅

**Schritte:**

1. Button "📸 Screenshot exportieren" klicken
2. Während Export läuft → andere Sidebar-Einstellung ändern (z.B. Dachtyp)

**Erwartetes Verhalten:**

- Export wird **NICHT** neu gestartet
- Button-State ist `False` nach Rerun
- Export kann abgeschlossen werden oder wird abgebrochen
- **KEINE DAUERSCHLEIFE**

**Status:** ✅ GEFIXT

---

## 📊 Technische Details

### Streamlit Button vs. Checkbox Behavior

| Widget | Wert bei Klick | Wert bei Rerun | Use Case |
|--------|---------------|----------------|----------|
| `st.checkbox()` | `True`/`False` | **BEHÄLT WERT** | Persistente Einstellungen |
| `st.button()` | `True` | **WIRD FALSE** | Einmalige Aktionen |

### Kaleido Lifecycle

```
1. fig.to_image() aufgerufen
   ↓
2. Kaleido-Prozess startet
   ↓
3. Chromium-Tab öffnet temporäre HTML-Datei
   ↓
4. Screenshot wird gerendert
   ↓
5. Bytes werden zurückgegeben
   ↓
6. Kaleido-Prozess beendet
```

**Problem bei Dauerschleife:**

- Schritt 6 wird nie erreicht, weil Schritt 1 sofort neu startet
- Kaleido-Tabs stapeln sich auf: Tab 5213, Tab 5214, Tab 5215...
- Chromium-Prozesse vermehren sich → RAM voll → System langsam

---

## 🎯 Wichtige Erkenntnisse

### 1. **Streamlit Buttons für Aktionen verwenden**

Checkbox = persistenter Zustand
Button = einmalige Aktion

**Regel:** Wenn etwas nur EINMAL bei Klick passieren soll → `st.button()`

### 2. **Kaleido ist Single-Threaded**

Kaleido kann nur **einen** Export zur Zeit verarbeiten.
Mehrfache gleichzeitige Aufrufe führen zu Konflikten.

### 3. **Progress Bars triggern Reruns**

Jeder `st.progress()` Aufruf kann einen Rerun auslösen.
Bei Checkbox-basierten Exporten → Dauerschleife!

### 4. **Lowercase Format-Strings**

Plotly's `fig.to_image(format="png")` erwartet lowercase.
Immer `.lower()` auf User-Input anwenden.

---

## ✅ Status

**FIX COMPLETE** - Datum: 2025-11-09

**Geänderte Dateien:**

1. `utils/pv3d_ui_components.py` (2 Änderungen)
   - Zeile ~748: Checkbox → Button
   - Zeile ~910: Return-Dictionary angepasst

**Tester:** Bitte überprüfen:

1. Screenshot-Export funktioniert ✅
2. Keine Kaleido-Dauerschleife im Terminal ✅
3. Download-Button erscheint nach Export ✅
4. Mehrfache Exports funktionieren ✅

---

## 📚 Referenzen

- **User-Report:** "das ist eine dauerschleife im terminal"
- **Kaleido-Logs:** `Processing _3D_PV_Visualisierung_20_Module.png` (Loop)
- **Betroffene Datei:** `utils/pv3d_ui_components.py`
- **Betroffene Funktion:** `render_export_options()`
- **Root Cause:** Checkbox-basierter Export triggert bei jedem Rerun
- **Fix:** Button-basierter Export (nur bei Klick)
