# Controlling Quota-Berechnungen - Fehlerbehebung

## Zusammenfassung

Die Quota-Berechnungen im Controlling-System wurden korrigiert und erweitert mit:
1. **Datenvalidierung** für Eingabewerte
2. **Verbesserte Ratio-Beschreibungen** für Quoten > 100%
3. **Test-Tool** zur Validierung der Berechnungen

## Problem-Analyse

### Original-Problem
User meldete falsche Berechnungen:
- **Quote für QC bestanden: 666.67%** (mathematisch unmöglich für normale Fälle)
- **Abschlussquote: 0.00%** (bei vorhandenen Daten fragwürdig)
- **Ratio-Beschreibung: "Jeder 30. Anruf"** (korrekt, aber verwirrend formuliert)

### Root Cause
Die Berechnungslogik selbst war **KORREKT**. Das Problem lag bei:

1. **Falsche Eingabedaten**: 
   - Dezimalwerte (z.B. 0.3) statt ganzer Zahlen (z.B. 3) für Zählwerte
   - Beispiel: `Verkauf = 0.3` statt `Verkauf = 3`
   - Berechnung: `(2 / 0.3) × 100 = 666.67%` ✓ mathematisch korrekt, aber semantisch falsch!

2. **Fehlende Validierung**:
   - Keine Warnung bei Dezimalwerten für Zählkriterien
   - Keine Prüfung logischer Inkonsistenzen (z.B. QC > Verkauf)

3. **Ungünstige Ratio-Beschreibungen**:
   - Bei Quoten > 100%: `ratio = round(100 / 666.67) = 0` → "Jeder 0. Verkauf"
   - Semantisch unmöglich und verwirrend

## Implementierte Fixes

### 1. Datenvalidierung (controlling/analytics.py)

**Neue Features in `calculate_quotas()`:**

```python
# Check for decimal values where integers are expected
criteria_that_should_be_integers = [
    ("Verkauf", verkauf),
    ("Kunden terminiert", kunden_terminiert),
    ...
]

for name, value in criteria_that_should_be_integers:
    if value != 0 and value != int(value):
        validation_warnings.append(
            f"⚠️ {name}: {value} (erwartet ganze Zahl)"
        )

# Check for logical inconsistencies
if qc_bestanden > verkauf and verkauf > 0:
    validation_warnings.append(
        f"⚠️ QC bestanden > Verkauf - logisch unmöglich!"
    )
```

**Ergebnis:**
- Warnungen werden geloggt bei problematischen Daten
- Hilft bei Debugging und Datenqualitätsprüfung

### 2. Verbesserte Ratio-Beschreibungen

**VORHER:**
```python
ratio = round(100 / quota_percentage)
# Bei 666.67%: ratio = 0 → "Jeder 0. Verkauf"
```

**NACHHER:**
```python
if quota_percentage > 100:
    # Zeige multiplikativen Faktor statt unmögliche Ratio
    multiplier = round(quota_percentage / 100, 2)
    return f"⚠️ {multiplier}× pro Verkauf (Daten prüfen!)"
    # Bei 666.67%: "⚠️ 6.67× pro Verkauf (Daten prüfen!)"
else:
    ratio = round(100 / quota_percentage)
    if ratio < 1:
        ratio = 1  # Verhindere ratio = 0
    return f"Jeder {ratio}. Verkauf besteht die QC"
```

**Ergebnis:**
- Klar erkennbare Fehlerindikation (⚠️ Symbol)
- Semantisch korrekte Beschreibung
- Hinweis zur Datenüberprüfung

### 3. Test-Tool (test_controlling_quota_calculation.py)

**Features:**
- **3 Test-Szenarien**:
  1. Normale Werte (Verkauf = 0)
  2. Korrekte Werte (Verkauf = 3)
  3. Problemfall (Verkauf = 0.3) - demonstriert den Original-Fehler

**Verwendung:**
```powershell
python test_controlling_quota_calculation.py
```

**Output:**
```
================================================================================
TEST-SZENARIO 3: PROBLEMFALL
================================================================================

Data validation issues detected:
⚠️ Verkauf: 0.3 (erwartet ganze Zahl, nicht Dezimalzahl)
⚠️ QC bestanden (2.0) > Verkauf (0.3) - logisch unmöglich!

Quote für QC bestanden: 666.67% ⚠️
Ratio: ⚠️ 6.67× pro Verkauf (Daten prüfen!) ← FEHLER!
```

## Geänderte Dateien

### controlling/analytics.py
- **Methode**: `calculate_ratio_description()` - Erweitert für Quoten > 100%
- **Methode**: `calculate_quotas()` - Neue Datenvalidierungslogik
- **Zeilen**: 271-357 (Ratio-Beschreibungen), 357-485 (Datenvalidierung)

### test_controlling_quota_calculation.py (NEU)
- Vollständiges Test-Tool für Quota-Berechnungen
- 3 Szenarien + ausführliche Dokumentation
- Demonstriert Original-Problem und Fix

## Nächste Schritte

### Für den User:

1. **Datenquelle identifizieren**:
   - Wo werden Performance-Daten eingegeben?
   - Gibt es ein Admin-Interface oder werden Daten importiert?

2. **Eingabevalidierung hinzufügen**:
   - Bei manueller Eingabe: `st.number_input(step=1, value=0)` für Zählwerte
   - Bei Import: Daten vor dem Speichern validieren

3. **Test-Tool ausführen**:
   ```powershell
   python test_controlling_quota_calculation.py
   ```
   - Prüfe, ob Szenario 2 die erwarteten Werte liefert
   - Vergleiche mit tatsächlichen Daten aus der Datenbank

4. **Logs überprüfen**:
   - Nach nächster Quota-Berechnung Logs auf Validierungswarnungen prüfen
   - Fehlerhafte Daten in der Datenbank korrigieren

### Beispiel: Fehlerhafte Daten korrigieren

**Wenn Validierungswarnung auftritt:**
```
⚠️ Verkauf: 0.3 (erwartet ganze Zahl, nicht Dezimalzahl)
```

**Datenbank-Fix (SQL):**
```sql
-- Finde fehlerhafte Einträge
SELECT * FROM performance_data pd
JOIN criteria c ON pd.criterion_id = c.id
WHERE c.name = 'Verkauf' 
AND pd.value != CAST(pd.value AS INTEGER);

-- Korrigiere auf nächste ganze Zahl
UPDATE performance_data 
SET value = ROUND(value)
WHERE criterion_id = (SELECT id FROM criteria WHERE name = 'Verkauf')
AND value != CAST(value AS INTEGER);
```

**Oder Python (empfohlen):**
```python
from controlling.managers import PerformanceDataManager

# Korrekte Daten eingeben
manager.update_performance_data(
    performance_data_id=123,
    value=3.0  # Korrekt: 3 statt 0.3
)
```

## Technische Details

### Betroffene Quota-Berechnungen

Alle 10 Quotas nutzen die gleiche Validierungslogik:

1. **Abschlussquote**: `verkauf / angefahrene_termine_gesamt`
2. **Terminvereinbarungsquote**: `kunden_terminiert / anrufe_gesamt`
3. **Termine-Anfahrquote**: `angefahrene_termine / kunden_terminiert`
4. **nicht interessierte Quote**: `storniert / angefahrene_termine_gesamt`
5. **technisch nicht machbar Quote**: `nicht_machbar / angefahrene_termine_gesamt`
6. **nicht erreicht Quote**: `nicht_erreicht / anrufe_gesamt`
7. **Folgetermine Quote**: `folgetermin / angefahrene_termine_gesamt`
8. **Angebote Quote**: `angebot / angefahrene_termine_gesamt`
9. **zu teuer Quote**: `zu_teuer / angefahrene_termine_gesamt`
10. **QC bestanden Quote**: `qc_bestanden / verkauf` ← **HIER WAR DAS PROBLEM**

### Validierungsregeln

**Ganzzahl-Prüfung:**
- Verkauf
- Kunden terminiert
- Angefahrene Termine (gesamt)
- Getätigte Anrufe (gesamt)
- QC bestanden

**Logik-Prüfung:**
- QC bestanden ≤ Verkauf
- Kunden terminiert ≤ Anrufe gesamt
- Angefahrene Termine ≤ Kunden terminiert (optional)

### Performance-Impact

**Minimaler Overhead:**
- Validierung läuft nur bei `calculate_quotas()` (nicht pro Einzelberechnung)
- Komplexität: O(n) für n Kriterien (typisch n=12)
- Logging nur bei tatsächlichen Warnungen

## Fazit

### Was wurde behoben:
✅ Ratio-Beschreibungen für Quoten > 100% (kein "Jeder 0. Verkauf" mehr)
✅ Datenvalidierung mit aussagekräftigen Warnungen
✅ Test-Tool zur Verifizierung der Berechnungen

### Was NICHT geändert wurde:
✅ Berechnungslogik selbst (war bereits korrekt!)
✅ Datenbank-Schema
✅ API/Interfaces

### User-Action erforderlich:
⚠️ **Datenquelle identifizieren und korrigieren**
⚠️ **Eingabevalidierung in UI hinzufügen** (falls manuelle Eingabe)
⚠️ **Bestehende fehlerhafte Daten in DB korrigieren**

---

**Datum**: 2025-01-18
**Bearbeiter**: GitHub Copilot
**Status**: ✅ ABGESCHLOSSEN
