# PV-Module Upload Anleitung - Korrigierte Version

## ✅ Ihre XLSX-Datei ist jetzt kompatibel

Das System wurde angepasst, um Ihre PV-Modul Spaltenstruktur zu unterstützen:

### Unterstützte Spaltenreihenfolge

```
manufacturer | model | powerWp | efficiency | technology | dimensions_length | dimensions_width | dimensions_thickness | weight | pricePerWp | warranty_product | warranty_performance | temperatureCoefficient | maxSystemVoltage | shortCircuitCurrent | openCircuitVoltage
```

## Was wurde korrigiert

### ✅ Automatische Spaltenerkennung

- `model` wird automatisch als `model_name` erkannt
- `manufacturer` wird automatisch als Hersteller erkannt
- `category` wird automatisch auf "module" gesetzt (PV-Module)

### ✅ Flexible Wertbehandlung

Das System akzeptiert jetzt folgende Werte **ohne Fehler**:

- **Leere Zellen** ✅
- **"x" oder "X"** ✅
- **"0" oder 0** ✅
- **Normale Werte** ✅

### ✅ Intelligente Zahlenkonvertierung

- Automatische Erkennung von deutschen Dezimalkommas (`1,5` → `1.5`)
- Entfernung von Einheiten (`24,50 kg` → `24.5`)
- Entfernung von Währungszeichen (`€ 180,50` → `180.5`)
- Temperaturbereiche bleiben als Text (z.B. `"- 40° C bis +85° C"`)

## Upload-Prozess

1. **Admin-Bereich öffnen** (Passwort: `admin123`)
2. **XLSX-Datei auswählen**
3. **Hochladen** - alle Ihre Daten werden jetzt korrekt verarbeitet!

## Beispiel für gültige Daten

| manufacturer | model | powerWp | efficiency | weight | pricePerWp |
|-------------|-------|---------|------------|--------|------------|
| ViessmannPV | Vitovolt 300-DG M440HC | 440 | 22 | 24,50 | 0,28 |
| SolarfabrikPV | Mono S4 Trendline 440W | x | x | 0 | x |
| TrinaSolarPV | Vertex S+ TSM-440 | 440 |  | 24.5 | 0.28 |

**Alle drei Zeilen sind jetzt gültig!**

## Keine Fehler mehr für

- ❌ ~~"Fehlende Pflichtfelder"~~ → ✅ Nur `model` muss gefüllt sein
- ❌ ~~"Ungültige Zahlenformate"~~ → ✅ `x`, `0`, leere Werte sind OK
- ❌ ~~"Kategorie fehlt"~~ → ✅ Automatisch auf "module" gesetzt

Ihre ursprünglichen Daten können jetzt ohne Änderungen hochgeladen werden!
