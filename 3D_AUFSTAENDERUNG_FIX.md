# 3D Visualisierung: Fix für Modul-Aufständerung bei verschiedenen Dachtypen

## 🐛 Problem

**User-Beschreibung:**
"bei der 3d visualisierung, ist ein logik falsch! es dürfen keine aufständerungen verwendet werden wenn man eine dachart wählt die kein flachdach ist! egal welche dachart man wählt man sollte nur bei flachdächern aufständerungen verwenden!"

**Technische Analyse:**
Die 3D-Visualisierung hat Module auf **allen** Dachtypen mit Aufständerung (Mounting Height) gerendert, obwohl dies nur bei **Flachdächern** korrekt ist.

### Bisheriges Verhalten (FALSCH):
- **Flachdach:** `default_tilt = 15.0°` → Aufständerung ✅
- **Satteldach:** `default_tilt = roof_inclination` (z.B. 35°) → Aufständerung ❌ **FALSCH**
- **Walmdach:** `default_tilt = roof_inclination` (z.B. 35°) → Aufständerung ❌ **FALSCH**
- **Pultdach:** `default_tilt = roof_inclination` → Aufständerung ❌ **FALSCH**
- **Zeltdach:** `default_tilt = roof_inclination` → Aufständerung ❌ **FALSCH**

### Gewünschtes Verhalten (KORREKT):
- **Flachdach:** `default_tilt = 15.0°` → Aufständerung ✅
- **Alle anderen Dächer:** `default_tilt = 0.0°` → **KEINE** Aufständerung, Module liegen direkt auf Dachfläche ✅

---

## ✅ Lösung

### Änderung 1: `default_tilt` auf 0.0° bei geneigten Dächern

**Datei:** `utils/pv3d_plotly.py`
**Funktion:** `build_plotly_scene()`

**Geänderte Zeilen:**
- Satteldach (ca. Zeile 1028)
- Satteldach mit Gaube (ca. Zeile 1053)
- Walmdach (ca. Zeile 1079)
- Krüppelwalmdach (ca. Zeile 1106)
- Pultdach (ca. Zeile 1133)
- Zeltdach (ca. Zeile 1160)

**Vorher:**
```python
module_base_z = roof_z + 0.15
default_tilt = roof_inclination  # Z.B. 35° → FALSCH!
```

**Nachher:**
```python
module_base_z = roof_z + 0.15
default_tilt = 0.0  # FIX: Module liegen flach auf Dachfläche, keine Aufständerung
```

---

### Änderung 2: Mounting Height nur bei Flachdach

**Datei:** `utils/pv3d_plotly.py`
**Funktion:** `create_pv_module_3d()`
**Zeilen:** ca. 442-470

**Vorher:**
```python
pitched_roofs = ["Satteldach", "Satteldach mit Gaube", "Walmdach", "Krüppelwalmdach", "Pultdach", "Zeltdach"]

if roof_type in pitched_roofs and tilt_deg > 5.0:
    # Geneigte Dächer: Sichtbare Aufständerung ← FALSCH!
    mounting_height = min(0.3, (tilt_deg / 90.0) * 0.5)
    
    if show_mounting:
        mounting_height += 0.05
    
elif roof_type == "Flachdach" and tilt_deg > 5.0:
    # Flachdach mit Aufständerung
    mounting_height = 0.3 + (tilt_deg / 90.0) * 0.5
    mounting_height = min(0.8, mounting_height)
    
    if show_mounting:
        mounting_height += 0.05
```

**Nachher:**
```python
pitched_roofs = ["Satteldach", "Satteldach mit Gaube", "Walmdach", "Krüppelwalmdach", "Pultdach", "Zeltdach"]

# KRITISCH: Nur bei Flachdach Aufständerung verwenden!
if roof_type == "Flachdach" and tilt_deg > 5.0:
    # Flachdach mit Aufständerung: Höhere Aufständerung
    mounting_height = 0.3 + (tilt_deg / 90.0) * 0.5
    mounting_height = min(0.8, mounting_height)
    
    if show_mounting:
        mounting_height += 0.05

# BEI ALLEN ANDEREN DACHTYPEN: KEINE AUFSTÄNDERUNG!
# Module liegen direkt auf der Dachfläche
```

---

## 📊 Technische Details

### Physikalische Begründung:

#### **Flachdach:**
- Dachneigung: 0° - 5°
- Module müssen **aufgeständert** werden für optimale Neigung (typisch 10-35°)
- Mounting Height: 0.3m - 0.8m (abhängig von Neigung)
- `default_tilt = 15.0°` → Module werden geneigt montiert

#### **Geneigte Dächer (Satteldach, Walmdach, etc.):**
- Dachneigung: bereits optimal (typisch 25° - 45°)
- Module liegen **direkt auf der Dachfläche**
- KEINE zusätzliche Aufständerung notwendig
- `default_tilt = 0.0°` → Module folgen der Dachneigung
- Mounting Height: 0.0m

---

## 🧪 Test-Szenarien

### Test 1: Flachdach ✅
**Setup:**
- Dachtyp: Flachdach
- Modul-Anzahl: 20

**Erwartetes Verhalten:**
- `default_tilt = 15.0°`
- Mounting Height > 0 (z.B. 0.35m)
- Module sind sichtbar aufgeständert
- Module haben 15° Neigung

**Status:** ✅ KORREKT (unverändert)

---

### Test 2: Satteldach ✅
**Setup:**
- Dachtyp: Satteldach
- Dachneigung: 35°
- Modul-Anzahl: 20

**Erwartetes Verhalten:**
- `default_tilt = 0.0°` (vorher: 35° ❌)
- Mounting Height = 0.0m
- Module liegen flach auf Dachfläche
- Module folgen der Dachneigung von 35°

**Status:** ✅ GEFIXT

---

### Test 3: Walmdach ✅
**Setup:**
- Dachtyp: Walmdach
- Dachneigung: 30°
- Modul-Anzahl: 20

**Erwartetes Verhalten:**
- `default_tilt = 0.0°` (vorher: 30° ❌)
- Mounting Height = 0.0m
- Module liegen flach auf Dachfläche
- Module folgen der Dachneigung von 30°

**Status:** ✅ GEFIXT

---

### Test 4: Pultdach ✅
**Setup:**
- Dachtyp: Pultdach
- Dachneigung: 25°
- Modul-Anzahl: 20

**Erwartetes Verhalten:**
- `default_tilt = 0.0°` (vorher: 25° ❌)
- Mounting Height = 0.0m
- Module liegen flach auf Dachfläche
- Module folgen der Dachneigung von 25°

**Status:** ✅ GEFIXT

---

## 📝 Code-Änderungs-Zusammenfassung

### Geänderte Dateien:
1. `utils/pv3d_plotly.py`

### Anzahl Änderungen:
- **7 Änderungen** total:
  - 6x `default_tilt` von `roof_inclination` → `0.0` (Satteldach, Satteldach mit Gaube, Walmdach, Krüppelwalmdach, Pultdach, Zeltdach)
  - 1x Mounting Height Logik in `create_pv_module_3d()` vereinfacht

### Zeilen geändert:
- Ca. 30 Zeilen Code modifiziert
- 6 Kommentare hinzugefügt: `# FIX: Module liegen flach auf Dachfläche, keine Aufständerung`

---

## 🎯 Wichtige Erkenntnis

**Die Logik war falsch auf 2 Ebenen:**

1. **`default_tilt` bei geneigten Dächern:** Wurde auf `roof_inclination` gesetzt (z.B. 35°), was bedeutet, dass Module **zusätzlich** zur Dachneigung noch 35° geneigt wurden → **DOPPELTE NEIGUNG**

2. **Mounting Height bei geneigten Dächern:** Wurde basierend auf `tilt_deg` berechnet, was zu sichtbarer Aufständerung führte → **FALSCHE HÖHE**

**Lösung:**
- `default_tilt = 0.0°` → Module folgen exakt der Dachfläche, keine zusätzliche Neigung
- Mounting Height nur bei `roof_type == "Flachdach"` → Keine Aufständerung bei geneigten Dächern

---

## ✅ Status

**FIX COMPLETE** - Datum: 2025-11-09

**Tester:** Bitte überprüfen:
1. Flachdach → Module aufgeständert ✅
2. Satteldach → Module liegen flach auf Dachfläche ✅
3. Walmdach → Module liegen flach auf Dachfläche ✅
4. Pultdach → Module liegen flach auf Dachfläche ✅
5. Zeltdach → Module liegen flach auf Dachfläche ✅

---

## 📚 Referenzen

- **User-Request:** "es dürfen keine aufständerungen verwendet werden wenn man eine dachart wählt die kein flachdach ist!"
- **Betroffene Datei:** `utils/pv3d_plotly.py`
- **Betroffene Funktionen:**
  - `build_plotly_scene()` (Zeilen 913-1400)
  - `create_pv_module_3d()` (Zeilen 417-545)
