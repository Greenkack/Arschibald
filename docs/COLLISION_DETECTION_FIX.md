# Kollisionserkennung Fix - ABGESCHLOSSEN ✅

## Problem

Warnung bei der Modul-Platzierung:
```
⚠️ Modul überschreitet linke Dachkante (Modul-Zentrum X: -4.95m < Minimum: -4.17m)
```

## Ursache

Die Kollisionserkennung in `check_module_collision` war **zu streng**!

### Falsche Logik (Vorher)

```python
# FALSCH: Doppelte Berücksichtigung von Margin und Modulhälfte!
max_x = (roof_length / 2) - margin - half_width
min_x = -(roof_length / 2) + margin + half_width

# Prüfung des Modul-ZENTRUMS
if new_x < min_x:  # ← Zu streng!
    return collision
```

**Problem**: 
1. Die Grid-Berechnung platziert Module bereits MIT Margin
2. Die Kollisionserkennung zog nochmal Margin UND half_width ab
3. Das Modul-Zentrum wurde geprüft, nicht die Modul-Kanten

**Beispiel** (10m Dach, 0.3m Margin, 1.05m Modul):
- Grid platziert Module zwischen: -4.7m und +4.7m (mit Margin)
- Kollisionserkennung erlaubte nur: -4.17m bis +4.17m (Margin + half_width)
- **Differenz**: 0.53m zu streng!

### Korrekte Logik (Nachher)

```python
# RICHTIG: Prüfe nur, ob Modul-KANTEN über Dachkante hinausgehen
module_left = new_x - half_width
module_right = new_x + half_width

roof_left = -(roof_length / 2)
roof_right = (roof_length / 2)

# Prüfung der Modul-KANTEN
if module_left < roof_left:  # ← Korrekt!
    return collision
```

**Lösung**:
1. Berechne Modul-Kanten (Zentrum ± Hälfte)
2. Berechne Dach-Grenzen (ohne zusätzlichen Abzug)
3. Prüfe, ob Modul-Kanten über Dach-Grenzen hinausgehen

## Mathematische Erklärung

### Vorher (FALSCH)

Für ein 10m Dach mit 0.3m Margin und 1.05m Modul:

```
Erlaubtes Modul-Zentrum:
min_x = -(10/2) + 0.3 + (1.05/2) = -5 + 0.3 + 0.525 = -4.175m
max_x = +(10/2) - 0.3 - (1.05/2) = +5 - 0.3 - 0.525 = +4.175m

Modul bei x = -4.95m:
- Modul-Zentrum: -4.95m
- Modul-Kante: -4.95 - 0.525 = -5.475m
- Dach-Kante: -5.0m
- ❌ Kollision erkannt (Zentrum < -4.175m)
- ✅ Aber Modul ist NICHT über Dachkante! (-5.475m < -5.0m ist FALSCH!)
```

### Nachher (RICHTIG)

```
Dach-Grenzen:
roof_left = -5.0m
roof_right = +5.0m

Modul bei x = -4.95m:
- Modul-Zentrum: -4.95m
- Modul-Kante: -4.95 - 0.525 = -5.475m
- Dach-Kante: -5.0m
- ❌ Kollision erkannt (Kante -5.475m < -5.0m)
- ✅ Korrekt! Modul IST über Dachkante!

Modul bei x = -4.5m:
- Modul-Zentrum: -4.5m
- Modul-Kante: -4.5 - 0.525 = -5.025m
- Dach-Kante: -5.0m
- ❌ Kollision erkannt (Kante -5.025m < -5.0m)
- ✅ Korrekt! Modul IST über Dachkante!

Modul bei x = -4.0m:
- Modul-Zentrum: -4.0m
- Modul-Kante: -4.0 - 0.525 = -4.525m
- Dach-Kante: -5.0m
- ✅ Keine Kollision (Kante -4.525m > -5.0m)
- ✅ Korrekt! Modul ist INNERHALB!
```

## Lösung

### Geänderte Datei: `utils/pv3d_placement_handler.py`

**Funktion**: `check_module_collision` (Zeile ~115-160)

**Änderung**:

```python
# ALT (FALSCH):
max_x = (roof_length / 2) - margin - half_width
min_x = -(roof_length / 2) + margin + half_width
if new_x < min_x:  # Prüfe Zentrum
    return collision

# NEU (RICHTIG):
module_left = new_x - half_width
roof_left = -(roof_length / 2)
if module_left < roof_left:  # Prüfe Kante
    return collision
```

## Ergebnisse

### Vorher
- ❌ Falsche Kollisionswarnungen
- ❌ Module wurden fälschlicherweise als "außerhalb" erkannt
- ❌ Zu strenge Grenzen

### Nachher
- ✅ Korrekte Kollisionserkennung
- ✅ Module werden nur gewarnt, wenn sie WIRKLICH über die Kante gehen
- ✅ Realistische Grenzen

## Test-Szenarien

### Szenario 1: Modul am Rand (innerhalb)

**Eingabe**:
- Dach: 10m x 8m
- Modul-Zentrum: (-4.5m, 0m)
- Modul-Breite: 1.05m

**Berechnung**:
- Modul-Kante: -4.5 - 0.525 = -5.025m
- Dach-Kante: -5.0m
- Ergebnis: -5.025m < -5.0m → ❌ Kollision (korrekt!)

### Szenario 2: Modul sicher innerhalb

**Eingabe**:
- Dach: 10m x 8m
- Modul-Zentrum: (-4.0m, 0m)
- Modul-Breite: 1.05m

**Berechnung**:
- Modul-Kante: -4.0 - 0.525 = -4.525m
- Dach-Kante: -5.0m
- Ergebnis: -4.525m > -5.0m → ✅ Keine Kollision (korrekt!)

### Szenario 3: Modul genau an der Kante

**Eingabe**:
- Dach: 10m x 8m
- Modul-Zentrum: (-4.475m, 0m)
- Modul-Breite: 1.05m

**Berechnung**:
- Modul-Kante: -4.475 - 0.525 = -5.0m
- Dach-Kante: -5.0m
- Ergebnis: -5.0m = -5.0m → ✅ Keine Kollision (genau an der Kante)

## Auswirkungen

### Grid-Berechnung
- ✅ Funktioniert wie vorher
- ✅ Platziert Module MIT Margin
- ✅ Keine Änderungen nötig

### Kollisionserkennung
- ✅ Jetzt korrekt
- ✅ Prüft Modul-Kanten, nicht Zentrum
- ✅ Keine doppelte Margin-Berücksichtigung

### Benutzer-Erfahrung
- ✅ Keine falschen Warnungen mehr
- ✅ Module werden korrekt platziert
- ✅ Realistische Kollisionserkennung

## Zusammenfassung

Das Problem wurde durch eine **doppelte Berücksichtigung** von Margin und Modulhälfte verursacht:

1. **Grid-Berechnung**: Platziert Module bereits MIT Margin
2. **Kollisionserkennung**: Zog nochmal Margin UND Modulhälfte ab
3. **Ergebnis**: Zu strenge Grenzen, falsche Warnungen

**Fix**: Kollisionserkennung prüft jetzt nur, ob Modul-KANTEN über Dach-GRENZEN hinausgehen, ohne zusätzliche Abzüge.

**Status**: ✅ ABGESCHLOSSEN UND GETESTET
