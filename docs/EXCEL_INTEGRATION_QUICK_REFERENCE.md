# Excel-Integration Schnellreferenz

## Tastatur-Shortcuts

### Navigation
- `↑↓←→` - Zellen navigieren
- `Tab` - Nächste Zelle
- `Enter` - Zelle darunter
- `Ctrl+Home` - Erste Zelle (A1)

### Bearbeitung
- `Ctrl+Z` - Rückgängig
- `Ctrl+Y` - Wiederholen
- `Ctrl+C` - Kopieren
- `Ctrl+V` - Einfügen
- `Delete` - Löschen
- `Ctrl+S` - Speichern

## Häufige Formeln

### Mathematik
```
=SUM(A1:A10)           Summe
=AVERAGE(A1:A10)       Durchschnitt
=MIN(A1:A10)           Minimum
=MAX(A1:A10)           Maximum
=ROUND(A1, 2)          Runden auf 2 Stellen
=COUNT(A1:A10)         Anzahl Zahlen
=ABS(-5)               Absolutwert
=POWER(2, 3)           Potenz (2^3)
=SQRT(16)              Quadratwurzel
=MOD(10, 3)            Rest der Division
=CEILING(4.3, 1)       Aufrunden
=FLOOR(4.7, 1)         Abrunden
=RAND()                Zufallszahl 0-1
=RANDBETWEEN(1, 100)   Zufallszahl im Bereich
```

### Statistik
```
=MEDIAN(A1:A10)        Median
=MODE(A1:A10)          Häufigster Wert
=STDEV(A1:A10)         Standardabweichung
=VAR(A1:A10)           Varianz
=PERCENTILE(A1:A10, 0.75)  75. Perzentil
=QUARTILE(A1:A10, 1)   1. Quartil
=RANK(A1, A1:A10, 0)   Rang
=LARGE(A1:A10, 2)      Zweitgrößter Wert
=SMALL(A1:A10, 2)      Zweitkleinster Wert
```

### Logik
```
=IF(A1>10, "Ja", "Nein")              Bedingung
=IFS(A1>=90, "A", A1>=80, "B")        Mehrere Bedingungen
=SWITCH(A1, 1, "Eins", 2, "Zwei")     Fallunterscheidung
=CHOOSE(2, "A", "B", "C")             Auswahl aus Liste
=AND(A1>5, B1<10)                     Alle wahr
=OR(A1>5, B1<10)                      Mindestens eine wahr
=IFERROR(A1/B1, 0)                    Fehlerbehandlung
```

### Erweiterte Aggregation
```
=AVERAGEIF(A1:A10, ">50", B1:B10)     Durchschnitt mit Bedingung
=AVERAGEIFS(C1:C10, A1:A10, ">50", B1:B10, "<100")  Mehrere Bedingungen
=MAXIFS(C1:C10, A1:A10, ">50")        Maximum mit Bedingungen
=MINIFS(C1:C10, A1:A10, ">50")        Minimum mit Bedingungen
=COUNTIFS(A1:A10, ">50", B1:B10, "<100")  Zählen mit Bedingungen
=COUNTBLANK(A1:A10)                   Leere Zellen zählen
```

### Text
```
=LEFT("Hallo", 3)      Erste Zeichen
=RIGHT("Hallo", 3)     Letzte Zeichen
=MID("Hallo", 2, 3)    Zeichen aus Mitte
=LEN("Hallo")          Länge
=LOWER("HALLO")        Kleinbuchstaben
=UPPER("hallo")        Großbuchstaben
=TRIM("  Text  ")      Leerzeichen entfernen
=FIND("lo", "Hallo")   Text finden
=SUBSTITUTE("alt", "neu")  Text ersetzen
=TEXTJOIN(", ", TRUE, A1:A5)  Mit Trennzeichen verbinden
```

### Lookup
```
=VLOOKUP(A1, B1:D10, 2, FALSE)        Vertikale Suche
=HLOOKUP(A1, B1:J2, 2, FALSE)         Horizontale Suche
=INDEX(A1:C10, 5, 2)                  Wert nach Position
=MATCH("Apfel", A1:A10, 0)            Position suchen
```

### Datum
```
=TODAY()               Heutiges Datum
=DATE(2024, 12, 25)    Datum erstellen
=YEAR(TODAY())         Jahr
=MONTH(TODAY())        Monat
=DAY(TODAY())          Tag
```

## Fehler-Codes

| Code | Bedeutung | Lösung |
|------|-----------|--------|
| `#DIV/0!` | Division durch Null | `=IFERROR(A1/B1, 0)` |
| `#REF!` | Ungültige Referenz | Zellreferenzen prüfen |
| `#CIRCULAR!` | Zirkelbezug | Formel-Kette brechen |
| `#NAME?` | Unbekannte Funktion | Schreibweise prüfen |
| `#VALUE!` | Falscher Typ | Datentypen prüfen |
| `#ERROR!` | Syntaxfehler | Formel-Syntax prüfen |

## Zellformate

- **Auto** - Automatisch
- **Zahl** - 1234.56
- **Währung** - 1.234,56 €
- **Prozent** - 12,34%
- **Datum** - 25.12.2024
- **Text** - Als Text

## Tipps

✅ Auto-Save aktivieren  
✅ Formeln mit `=` beginnen  
✅ IFERROR für Fehlerbehandlung  
✅ Tastaturnavigation nutzen  
✅ Beispiel-Matrizen laden  
✅ Regelmäßig speichern (Ctrl+S)  

## Beispiele

### Preisberechnung
```
Einzelpreis: A1 = 250
Menge: B1 = 20
Gesamt: C1 = =A1*B1
MwSt: D1 = =C1*0.19
Brutto: E1 = =C1+D1
```

### Staffelpreis
```
=IF(A1>=30, 900, IF(A1>=20, 950, IF(A1>=10, 1000, 1100)))
```

### VLOOKUP Preissuche
```
Produkt-ID: A1 = "M400"
Preis: B1 = =VLOOKUP(A1, Preisliste!A:C, 3, FALSE)
```

### Durchschnitt ohne Fehler
```
=IFERROR(AVERAGE(A1:A10), 0)
```

---

**Vollständige Dokumentation:** EXCEL_INTEGRATION_USER_GUIDE.md
