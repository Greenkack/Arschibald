# XLSX Upload Anleitung - Fehlerbehebung

## Häufige Fehler und deren Behebung

### 1. "Fehlende Pflichtfelder" - Fehler

**Problem:** Die Spalten `model_name` und `category` sind Pflichtfelder und dürfen nicht leer sein.

**Lösung:**

- Stellen Sie sicher, dass jede Zeile einen Wert in der Spalte `model_name` hat
- Die Spalte `category` muss einen der folgenden Werte enthalten:
  - `module` (für PV-Module)
  - `inverter` (für Wechselrichter)  
  - `storage` (für Batteriespeicher)

**Beispiel für korrekte Daten:**

```
model_name          | category | manufacturer
Jinko Solar 420W    | module   | Jinko Solar
SMA Sunny Boy 5.0   | inverter | SMA
BYD Battery Box     | storage  | BYD
```

### 2. "Ungültige Zahlenformate" - Fehler

**Problem:** Numerische Werte können nicht konvertiert werden.

**Betroffene Spalten:**

- `price_euro`
- `capacity_w` (für Module)
- `power_kw` (für Wechselrichter/Speicher)
- `storage_power_kw`
- `warranty_years`
- `efficiency_percent`
- `rating`

**Häufige Ursachen:**

- Verwendung von Komma statt Punkt als Dezimaltrennzeichen
- Text in numerischen Spalten (z.B. "450 Watt" statt "450")
- Leerzeichen oder Sonderzeichen in Zahlen
- Leere Zellen in numerischen Spalten

**Korrekte Formate:**

```
✅ Richtig:           ❌ Falsch:
price_euro: 299.99    price_euro: 299,99 €
capacity_w: 420       capacity_w: 420 Watt
efficiency_percent: 21.5   efficiency_percent: 21,5%
warranty_years: 25    warranty_years: 25 Jahre
```

### 3. Spaltennamen-Normalisierung

Das System normalisiert automatisch Spaltennamen:

- Großbuchstaben werden zu Kleinbuchstaben
- Leerzeichen werden zu Unterstrichen

**Beispiele:**

```
"Model Name" → "model_name"
"Price Euro" → "price_euro"
"Capacity W" → "capacity_w"
```

## Empfohlene Spaltenstruktur

### Für PV-Module (category: "module")

```
model_name | category | manufacturer | capacity_w | price_euro | efficiency_percent | warranty_years
```

### Für Wechselrichter (category: "inverter")

```
model_name | category | manufacturer | power_kw | price_euro | efficiency_percent | warranty_years
```

### Für Batteriespeicher (category: "storage")

```
model_name | category | manufacturer | capacity_kwh | storage_power_kw | price_euro | warranty_years
```

## Schritt-für-Schritt Fehlerbehebung

### Schritt 1: Datei in Excel öffnen

1. Öffnen Sie Ihre XLSX-Datei in Excel
2. Gehen Sie zu der Zeile mit dem Fehler (z.B. Zeile 5 oder 23)

### Schritt 2: Pflichtfelder prüfen

1. Prüfen Sie Spalte `model_name` - darf nicht leer sein
2. Prüfen Sie Spalte `category` - muss "module", "inverter" oder "storage" enthalten

### Schritt 3: Numerische Werte korrigieren

1. Markieren Sie alle numerischen Spalten
2. Ersetzen Sie Kommas durch Punkte (Suchen & Ersetzen: "," → ".")
3. Entfernen Sie Text aus Zahlenspalten (z.B. "Watt", "€", "%")
4. Stellen Sie sicher, dass leere Zellen wirklich leer sind (keine Leerzeichen)

### Schritt 4: Datei speichern und erneut hochladen

1. Speichern Sie die korrigierte Datei
2. Laden Sie sie erneut im Admin-Bereich hoch

## Beispiel für eine korrekte XLSX-Datei

```
model_name           | category | manufacturer | capacity_w | price_euro | efficiency_percent | warranty_years
Jinko Solar JKM420N  | module   | Jinko Solar  | 420        | 180.50     | 21.5              | 25
Canadian Solar 410W  | module   | Canadian     | 410        | 175.00     | 21.0              | 25
SMA Sunny Boy 5.0    | inverter | SMA          |            | 1250.00    | 96.5              | 10
Fronius Primo 6.0    | inverter | Fronius      |            | 1450.00    | 97.0              | 10
BYD Battery-Box      | storage  | BYD          |            | 3500.00    |                   | 10
```

## Weitere Tipps

1. **Dezimaltrennzeichen:** Verwenden Sie immer Punkt (.) statt Komma (,)
2. **Einheiten:** Geben Sie nur die Zahl ein, ohne Einheiten wie "Watt", "€", "%"
3. **Leere Felder:** Lassen Sie optionale numerische Felder komplett leer
4. **Encoding:** Speichern Sie die Datei im UTF-8 Format für Umlaute
5. **Backup:** Erstellen Sie eine Sicherungskopie bevor Sie Änderungen vornehmen

Bei weiteren Problemen prüfen Sie die Konsolen-Ausgabe im Admin-Bereich für detaillierte Fehlermeldungen.
