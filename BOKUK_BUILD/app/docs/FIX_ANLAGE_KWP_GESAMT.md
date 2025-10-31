# Fix: anlage_kwp_gesamt in PDF Seite 7

## 🐛 Problem

Der Placeholder `anlage_kwp_gesamt` auf PDF Seite 7 blieb leer, obwohl die Anlagengröße berechnet wurde.

## 🔍 Ursache

1. Die Anlagengröße wurde korrekt in Zeile ~775-805 berechnet und in `result["anlage_kwp"]` gespeichert
2. ABER: Die `seite7_defaults` (Zeile 4295-4360) wurden DANACH mit `result.update()` angewendet (Zeile 4683)
3. Dies überschrieb ALLE vorher gesetzten Werte, die nicht in `seite7_defaults` enthalten waren
4. `anlage_kwp_gesamt` war nicht in `seite7_defaults` → wurde überschrieben/gelöscht

## ✅ Lösung

### 1. Robustere Berechnung (Zeile 773-805)

```python
# Anlagengröße (kWp): bevorzugt aus analysis_results, sonst aus project_details berechnen
anlage_kwp = analysis_results.get("anlage_kwp")
if anlage_kwp is None:
    # Berechnung: Anzahl Module × Leistung pro Modul (Wp) / 1000
    try:
        mod_qty = float(project_details.get("module_quantity") or 0)
        mod_wp = float(project_details.get("selected_module_capacity_w") or 0)
        anlage_kwp_calc = (mod_qty * mod_wp) / 1000.0 if mod_qty > 0 and mod_wp > 0 else project_details.get("anlage_kwp")
        anlage_kwp = anlage_kwp_calc
    except Exception:
        anlage_kwp = project_details.get("anlage_kwp")

# Falls immer noch None, versuche weitere Quellen
if anlage_kwp is None:
    anlage_kwp = project_details.get("anlage_kwp")

# Wenn wir einen Wert haben, formatiere und fülle alle Placeholder
if anlage_kwp is not None and anlage_kwp > 0:
    result["anlage_kwp"] = fmt_number(anlage_kwp, 2, "kWp")
    result["kWp_anlage_anlage"] = result["anlage_kwp"]
    result["pv_power_kWp"] = fmt_number(anlage_kwp, 2, "kWp")
    result["anlage_kwp_gesamt"] = fmt_number(anlage_kwp, 2, "kWp")  # NEU!
else:
    # Fallback: Setze Placeholder auf "0.00 kWp"
    result["anlage_kwp"] = "0.00 kWp"
    result["kWp_anlage_anlage"] = "0.00 kWp"
    result["pv_power_kWp"] = "0.00 kWp"
    result["anlage_kwp_gesamt"] = "0.00 kWp"  # NEU!
```

### 2. Wiederherstellung nach seite7_defaults (Zeile 4684-4695)

```python
except Exception as e:
    print(f"WARN Seite 7 Preisberechnung Fehler: {e}")
    result.update(seite7_defaults)

# --- Stelle sicher dass Anlagengröße NACH seite7_defaults wieder gesetzt ist ---
# Die Anlagengröße wurde weiter oben berechnet (Zeile ~775-805), aber seite7_defaults
# könnte sie überschrieben haben. Setze sie erneut aus den bereits berechneten Werten.
if "anlage_kwp" in result and result["anlage_kwp"] and result["anlage_kwp"] != "0.00 kWp":
    # Kopiere die bereits berechnete Anlagengröße nach anlage_kwp_gesamt
    result["anlage_kwp_gesamt"] = result["anlage_kwp"]
elif "kWp_anlage_anlage" in result and result["kWp_anlage_anlage"] and result["kWp_anlage_anlage"] != "0.00 kWp":
    # Fallback: verwende kWp_anlage_anlage wenn vorhanden
    result["anlage_kwp_gesamt"] = result["kWp_anlage_anlage"]
```

## 🎯 Warum diese Lösung?

### Alternative A: anlage_kwp_gesamt zu seite7_defaults hinzufügen

❌ **Problem**: `seite7_defaults` enthält nur Preis-bezogene Defaults. Anlagengröße ist eine dynamische Berechnung, kein Default-Wert.

### Alternative B: result.update() vermeiden

❌ **Problem**: `seite7_defaults` wird an mehreren Stellen verwendet (Zeile 4360, 4683). Komplettes Refactoring nötig.

### Alternative C: Wert nach seite7_defaults wiederherstellen ✅

✅ **Vorteile**:

- Minimale Änderung
- Nutzt bereits berechnete Werte
- Kein Risiko für andere Seiten
- Fallback-Logik für Robustheit

## 📊 Berechnungsquellen (Priorität)

1. **analysis_results.anlage_kwp** - aus Berechnungsmodul
2. **Berechnet**: `module_quantity × selected_module_capacity_w ÷ 1000`
3. **project_details.anlage_kwp** - direkt aus Projekt-Daten
4. **Fallback**: "0.00 kWp"

## 🔧 Getestete Szenarien

1. ✅ Anlagengröße aus analysis_results vorhanden
2. ✅ Anlagengröße muss berechnet werden (Module × Wp)
3. ✅ Anlagengröße nur in project_details
4. ✅ Keine Anlagengröße verfügbar (Fallback "0.00 kWp")
5. ✅ seite7_defaults überschreibt Werte → Wiederherstellung greift

## 📝 Änderungen

**Datei**: `pdf_template_engine/placeholders.py`

- **Zeile 773-805**: Robustere Anlagengröße-Berechnung mit Fallbacks
- **Zeile 4684-4695**: Wiederherstellung von `anlage_kwp_gesamt` nach `seite7_defaults`

## 🎨 PDF-Seiten

- **Seite 1**: `kWp_anlage_anlage` (Position: 50.0, 725.0) - Helvetica-Bold 30pt
- **Seite 7**: `anlage_kwp_gesamt` (Position: 375.0, 178.0) - Helvetica-Bold 10pt

Beide zeigen jetzt konsistent die gleiche Anlagengröße an! ✅
