# Preismatrix-Struktur Anleitung

## Überblick

Die Preismatrix ermöglicht die Definition von schlüsselfertigen Preisen für PV-Anlagen basierend auf:
- **Modulanzahl** (Zeilen)
- **Speichermodell** (Spalten)

## Matrix-Struktur

### Grundaufbau

```
         A              B              C              D
    (Modulanzahl)  (Speicher 1)   (Speicher 2)   (Kein Speicher)
1   Modulanzahl    10kWh          15kWh          Kein Speicher
2   10             15000.00       17500.00       12000.00
3   15             18000.00       20500.00       15000.00
4   20             21000.00       23500.00       18000.00
5   25             24000.00       26500.00       21000.00
```

### Spalte A: Modulanzahl

**Zweck:** Definiert die Anzahl der PV-Module für jede Zeile

**Regeln:**
- ✓ Muss **numerische Werte** enthalten (z.B. 10, 15, 20, 25)
- ✓ Werte sollten **aufsteigend sortiert** sein
- ✓ Dezimalzahlen sind erlaubt (z.B. 12.5)
- ✗ Keine Text-Werte (außer in Zeile 1 als Header)

**Beispiele:**
```
Gültig:
- 10
- 15
- 20.5
- 25

Ungültig:
- "zehn"
- "10-15"
- leer
```

### Zeile 1: Speichermodelle

**Zweck:** Definiert die verfügbaren Batteriespeicher-Modelle

**Regeln:**
- ✓ Muss **Text-Werte** enthalten (Modellnamen)
- ✓ Mindestens eine **"Kein Speicher"** Spalte erforderlich
- ✓ Eindeutige Namen verwenden
- ✗ Keine leeren Spalten

**Beispiele:**
```
Gültig:
- "10kWh"
- "BYD HVS 10.2"
- "Kein Speicher"
- "Ohne Speicher"

Ungültig:
- leer
- nur Zahlen (z.B. "10")
```

**"Kein Speicher" Spalte:**

Die Matrix muss mindestens eine Spalte für Konfigurationen ohne Batteriespeicher enthalten.

Erkannte Bezeichnungen:
- "Kein Speicher"
- "Ohne Speicher"
- "No Storage"
- "None"

### Preis-Zellen (B2 und weiter)

**Zweck:** Enthält die schlüsselfertigen Preise für jede Kombination

**Regeln:**
- ✓ Muss **numerische Werte** enthalten (Preise in Euro)
- ✓ Dezimalzahlen erlaubt (z.B. 15000.50)
- ✓ Leere Zellen sind erlaubt (führen zu Fehler bei Preisabfrage)
- ✗ Keine Text-Werte
- ✗ Keine Formeln (in dieser Version)

**Beispiele:**
```
Gültig:
- 15000
- 15000.50
- 15.000,50 (wird automatisch konvertiert)
- leer

Ungültig:
- "15000 EUR"
- "ca. 15000"
- "=B2+1000"
```

## Beispiel-Matrix mit Dummy-Daten

### Kleine Anlage (10-25 Module)

```
Modulanzahl | 10kWh    | 15kWh    | 20kWh    | Kein Speicher
------------|----------|----------|----------|---------------
10          | 15000.00 | 17500.00 | 20000.00 | 12000.00
15          | 18000.00 | 20500.00 | 23000.00 | 15000.00
20          | 21000.00 | 23500.00 | 26000.00 | 18000.00
25          | 24000.00 | 26500.00 | 29000.00 | 21000.00
```

### Mittlere Anlage (30-50 Module)

```
Modulanzahl | 10kWh    | 15kWh    | 20kWh    | Kein Speicher
------------|----------|----------|----------|---------------
30          | 27000.00 | 29500.00 | 32000.00 | 24000.00
35          | 30000.00 | 32500.00 | 35000.00 | 27000.00
40          | 33000.00 | 35500.00 | 38000.00 | 30000.00
45          | 36000.00 | 38500.00 | 41000.00 | 33000.00
50          | 39000.00 | 41500.00 | 44000.00 | 36000.00
```

### Große Anlage (60-100 Module)

```
Modulanzahl | 10kWh    | 15kWh    | 20kWh    | Kein Speicher
------------|----------|----------|----------|---------------
60          | 45000.00 | 47500.00 | 50000.00 | 42000.00
70          | 51000.00 | 53500.00 | 56000.00 | 48000.00
80          | 57000.00 | 59500.00 | 62000.00 | 54000.00
90          | 63000.00 | 65500.00 | 68000.00 | 60000.00
100         | 69000.00 | 71500.00 | 74000.00 | 66000.00
```

## Preisberechnung - Lookup-Logik

### Exakte Übereinstimmung

Wenn die gewählte Modulanzahl **exakt** in Spalte A vorhanden ist:

```
Benutzer wählt: 20 Module + 15kWh Speicher
Matrix enthält: Zeile mit "20" in Spalte A
Ergebnis: Preis aus Zelle C4 = 23500.00 EUR
```

### Floor-Logik (Nächst-kleinere Zahl)

Wenn die gewählte Modulanzahl **nicht exakt** vorhanden ist:

```
Benutzer wählt: 22 Module + 15kWh Speicher
Matrix enthält: 10, 15, 20, 25 in Spalte A
Verwendete Zeile: 20 (nächst-kleinere Zahl)
Ergebnis: Preis aus Zelle C4 = 23500.00 EUR
```

**Wichtig:** Es wird immer die **nächst-kleinere** Modulanzahl verwendet, nie die nächst-größere!

### Kein Speicher

Wenn der Benutzer **keinen Speicher** wählt:

```
Benutzer wählt: 20 Module + Kein Speicher
Matrix enthält: Spalte "Kein Speicher"
Ergebnis: Preis aus Zelle D4 = 18000.00 EUR
```

## Validierung

### Automatische Validierung

Die Matrix wird automatisch validiert wenn:
- Sie im Admin-Panel als aktiv gesetzt wird
- Der Preisberechnungsmodus auf "Preismatrix" umgeschaltet wird
- Eine Preisberechnung durchgeführt wird

### Validierungsfehler

**Fehler 1: Spalte A nicht numerisch**
```
Fehler: Spalte A muss numerische Werte (Modulanzahl) enthalten
Lösung: Ersetzen Sie Text-Werte durch Zahlen (z.B. "zehn" → 10)
```

**Fehler 2: Zeile 1 leer**
```
Fehler: Zeile 1 muss Text-Werte (Speichermodell-Namen) enthalten
Lösung: Fügen Sie Speichermodell-Namen in Zeile 1 ein
```

**Fehler 3: Keine "Kein Speicher" Spalte**
```
Fehler: Keine "Kein Speicher" Spalte gefunden
Lösung: Fügen Sie eine Spalte mit dem Namen "Kein Speicher" hinzu
```

**Fehler 4: Preis-Zellen nicht numerisch**
```
Fehler: Preis-Zellen müssen numerische Werte enthalten
Lösung: Entfernen Sie Text aus Preis-Zellen (z.B. "15000 EUR" → 15000)
```

### Warnungen

**Warnung 1: Leere Preis-Zellen**
```
Warnung: X Preis-Zellen sind leer
Auswirkung: Preisberechnung schlägt fehl für diese Kombinationen
Lösung: Füllen Sie alle Preis-Zellen mit gültigen Werten
```

**Warnung 2: Zu wenige Zeilen/Spalten**
```
Warnung: Matrix hat nur eine Zeile/Spalte
Auswirkung: Eingeschränkte Funktionalität
Lösung: Fügen Sie weitere Zeilen/Spalten hinzu
```

## Best Practices

### 1. Vollständige Matrix

✓ **Empfohlen:** Alle Preis-Zellen ausfüllen
```
Modulanzahl | 10kWh    | 15kWh    | Kein Speicher
------------|----------|----------|---------------
10          | 15000.00 | 17500.00 | 12000.00
15          | 18000.00 | 20500.00 | 15000.00
20          | 21000.00 | 23500.00 | 18000.00
```

✗ **Nicht empfohlen:** Leere Zellen
```
Modulanzahl | 10kWh    | 15kWh    | Kein Speicher
------------|----------|----------|---------------
10          | 15000.00 |          | 12000.00
15          |          | 20500.00 | 15000.00
20          | 21000.00 | 23500.00 |
```

### 2. Konsistente Abstände

✓ **Empfohlen:** Gleichmäßige Abstände zwischen Modulanzahlen
```
10, 15, 20, 25, 30, 35, 40, ...
(Abstand: 5 Module)
```

✗ **Nicht empfohlen:** Unregelmäßige Abstände
```
10, 12, 18, 25, 40, 55, ...
```

### 3. Eindeutige Speichermodell-Namen

✓ **Empfohlen:** Klare, eindeutige Namen
```
"BYD HVS 10.2", "BYD HVS 15.4", "Kein Speicher"
```

✗ **Nicht empfohlen:** Mehrdeutige Namen
```
"10kWh", "10", "Speicher 1"
```

### 4. Sortierung

✓ **Empfohlen:** Aufsteigende Sortierung der Modulanzahlen
```
10, 15, 20, 25, 30, ...
```

✗ **Nicht empfohlen:** Unsortiert
```
25, 10, 30, 15, 20, ...
```

## Häufige Fehler

### Fehler 1: Text in Spalte A

**Problem:**
```
Modulanzahl | 10kWh    | 15kWh
------------|----------|----------
"10 Module" | 15000.00 | 17500.00
```

**Lösung:**
```
Modulanzahl | 10kWh    | 15kWh
------------|----------|----------
10          | 15000.00 | 17500.00
```

### Fehler 2: Zahlen in Zeile 1

**Problem:**
```
Modulanzahl | 10       | 15
------------|----------|----------
10          | 15000.00 | 17500.00
```

**Lösung:**
```
Modulanzahl | 10kWh    | 15kWh
------------|----------|----------
10          | 15000.00 | 17500.00
```

### Fehler 3: Fehlende "Kein Speicher" Spalte

**Problem:**
```
Modulanzahl | 10kWh    | 15kWh
------------|----------|----------
10          | 15000.00 | 17500.00
```

**Lösung:**
```
Modulanzahl | 10kWh    | 15kWh    | Kein Speicher
------------|----------|----------|---------------
10          | 15000.00 | 17500.00 | 12000.00
```

### Fehler 4: Text in Preis-Zellen

**Problem:**
```
Modulanzahl | 10kWh        | 15kWh
------------|--------------|-------------
10          | "15000 EUR"  | "17500 EUR"
```

**Lösung:**
```
Modulanzahl | 10kWh    | 15kWh
------------|----------|----------
10          | 15000.00 | 17500.00
```

## Checkliste für neue Matrix

Bevor Sie eine Matrix aktivieren, prüfen Sie:

- [ ] Spalte A enthält nur numerische Werte (Modulanzahlen)
- [ ] Zeile 1 enthält Text-Werte (Speichermodell-Namen)
- [ ] Mindestens eine "Kein Speicher" Spalte vorhanden
- [ ] Alle Preis-Zellen enthalten Zahlen oder sind bewusst leer
- [ ] Modulanzahlen sind aufsteigend sortiert
- [ ] Speichermodell-Namen sind eindeutig
- [ ] Keine leeren Zeilen oder Spalten in der Mitte
- [ ] Matrix wurde validiert (keine Fehler)

## Weitere Hilfe

Bei Fragen oder Problemen:
1. Prüfen Sie die Validierungsmeldungen im Admin-Panel
2. Verwenden Sie die Beispiel-Matrizen als Vorlage
3. Kontaktieren Sie den Support

---

**Version:** 1.0  
**Letzte Aktualisierung:** 2024  
**Anforderungen:** 2.1, 2.2, 2.3, 2.4, 2.5
