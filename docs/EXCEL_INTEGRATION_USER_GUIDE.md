# Excel-Integration Benutzerhandbuch

## Inhaltsverzeichnis

1. [Einführung](#einführung)
2. [Erste Schritte](#erste-schritte)
3. [Matrizen verwalten](#matrizen-verwalten)
4. [Zellen bearbeiten](#zellen-bearbeiten)
5. [Formeln verwenden](#formeln-verwenden)
6. [Import und Export](#import-und-export)
7. [Tastatur-Shortcuts](#tastatur-shortcuts)
8. [Tipps und Tricks](#tipps-und-tricks)
9. [Fehlerbehebung](#fehlerbehebung)

---

## Einführung

Die Excel-Integration ermöglicht es Ihnen, Preismatrizen und andere tabellarische Daten 
direkt in der Anwendung zu erstellen und zu verwalten. Sie bietet eine Excel-ähnliche 
Oberfläche mit vollständiger Formel-Unterstützung.

### Hauptfunktionen

- ✅ Excel-ähnliche Grid-Oberfläche
- ✅ Vollständige Formel-Unterstützung (SUM, AVERAGE, IF, VLOOKUP, etc.)
- ✅ Import/Export von CSV und Excel-Dateien
- ✅ Undo/Redo-Funktionalität
- ✅ Auto-Save
- ✅ Tastatur-Shortcuts
- ✅ Zellformatierung

---

## Erste Schritte

### Matrix erstellen

1. Öffnen Sie das Admin Panel
2. Navigieren Sie zum Tab **"Preis Matrix"**
3. Klicken Sie auf **"➕ Neue Matrix"**
4. Geben Sie einen Namen ein (z.B. "Preisliste 2024")
5. Wählen Sie die Anzahl der Zeilen und Spalten
6. Klicken Sie auf **"Erstellen"**

### Matrix laden

1. Wählen Sie eine Matrix aus dem Dropdown-Menü
2. Die Matrix wird automatisch geladen
3. Sie können nun mit der Bearbeitung beginnen

---

## Matrizen verwalten

### Matrix speichern

**Manuell speichern:**
- Klicken Sie auf **"💾 Speichern"**
- Oder drücken Sie **Strg+S**

**Auto-Save aktivieren:**
- Aktivieren Sie das Kontrollkästchen **"🔄 Auto-Save"**
- Die Matrix wird automatisch alle 60 Sekunden gespeichert

### Matrix löschen

1. Laden Sie die zu löschende Matrix
2. Klicken Sie auf **"🗑️ Löschen"** (in der Matrix-Verwaltung)
3. Bestätigen Sie die Löschung

### Matrix klonen

1. Laden Sie die zu klonende Matrix
2. Klicken Sie auf **"📋 Klonen"**
3. Geben Sie einen neuen Namen ein
4. Die Matrix wird mit allen Daten kopiert

---

## Zellen bearbeiten

### Wert eingeben

1. Klicken Sie auf eine Zelle
2. Die Zelle wird in der **Formelleiste** angezeigt
3. Geben Sie einen Wert ein
4. Drücken Sie **Enter** oder klicken Sie auf **"✓ Übernehmen"**

### Zelle löschen

1. Wählen Sie die Zelle aus
2. Drücken Sie **Delete**
3. Oder geben Sie einen leeren Wert ein

### Zellformat ändern

1. Wählen Sie die Zelle aus
2. Wählen Sie ein Format aus dem Dropdown:
   - **Auto** - Automatische Erkennung
   - **Zahl** - Numerische Formatierung
   - **Währung** - Währungsformat (€)
   - **Prozent** - Prozentformat (%)
   - **Datum** - Datumsformat
   - **Text** - Textformat

---

## Formeln verwenden

### Formel erstellen

1. Wählen Sie eine Zelle
2. Beginnen Sie mit **"="**
3. Geben Sie die Formel ein
4. Drücken Sie **Enter**

**Beispiel:**
```
=SUM(A1:A10)
```

### Unterstützte Funktionen

#### Mathematische Funktionen

| Funktion | Beschreibung | Beispiel |
|----------|--------------|----------|
| `SUM` | Summiert Zahlen | `=SUM(A1:A10)` |
| `AVERAGE` | Durchschnitt | `=AVERAGE(A1:A10)` |
| `MIN` | Kleinster Wert | `=MIN(A1:A10)` |
| `MAX` | Größter Wert | `=MAX(A1:A10)` |
| `ROUND` | Runden | `=ROUND(A1, 2)` |
| `COUNT` | Anzahl Zahlen | `=COUNT(A1:A10)` |

#### Logische Funktionen

| Funktion | Beschreibung | Beispiel |
|----------|--------------|----------|
| `IF` | Bedingung | `=IF(A1>10, "Ja", "Nein")` |
| `AND` | Alle Bedingungen wahr | `=AND(A1>5, B1<10)` |
| `OR` | Mindestens eine wahr | `=OR(A1>5, B1<10)` |
| `IFERROR` | Fehlerbehandlung | `=IFERROR(A1/B1, 0)` |

#### Lookup-Funktionen

| Funktion | Beschreibung | Beispiel |
|----------|--------------|----------|
| `VLOOKUP` | Vertikale Suche | `=VLOOKUP(A1, B1:D10, 2, FALSE)` |
| `HLOOKUP` | Horizontale Suche | `=HLOOKUP(A1, B1:J2, 2, FALSE)` |
| `INDEX` | Wert nach Position | `=INDEX(A1:C10, 5, 2)` |
| `MATCH` | Position suchen | `=MATCH("Apfel", A1:A10, 0)` |

#### Datumsfunktionen

| Funktion | Beschreibung | Beispiel |
|----------|--------------|----------|
| `TODAY` | Heutiges Datum | `=TODAY()` |
| `DATE` | Datum erstellen | `=DATE(2024, 12, 25)` |
| `YEAR` | Jahr extrahieren | `=YEAR(TODAY())` |
| `MONTH` | Monat extrahieren | `=MONTH(TODAY())` |
| `DAY` | Tag extrahieren | `=DAY(TODAY())` |

### Verschachtelte Formeln

Sie können Formeln verschachteln:

```
=IF(SUM(A1:A10)>100, "Hoch", "Niedrig")
```

```
=ROUND(AVERAGE(A1:A10), 2)
```

### Zellreferenzen

**Einzelne Zelle:**
```
=A1
```

**Bereich:**
```
=SUM(A1:A10)
```

**Mehrere Bereiche:**
```
=SUM(A1:A10, C1:C10)
```

---

## Import und Export

### CSV Import

1. Klicken Sie auf **"📥 CSV Import"**
2. Wählen Sie eine CSV-Datei
3. Die Datei wird automatisch geparst
4. Geben Sie einen Namen für die neue Matrix ein
5. Klicken Sie auf **"Importieren"**

**Unterstützte Formate:**
- Delimiter: `;`, `,`, `\t`
- Encoding: UTF-8, Latin-1

### Excel Import

1. Klicken Sie auf **"📥 Excel Import"**
2. Wählen Sie eine Excel-Datei (.xlsx, .xls)
3. Wählen Sie ein Sheet (bei mehreren Sheets)
4. **Formeln werden automatisch übernommen!**
5. Geben Sie einen Namen ein
6. Klicken Sie auf **"Importieren"**

### CSV Export

1. Laden Sie die zu exportierende Matrix
2. Klicken Sie auf **"📤 CSV Export"**
3. Die Datei wird heruntergeladen

### Excel Export

1. Laden Sie die zu exportierende Matrix
2. Klicken Sie auf **"📤 Excel Export"**
3. Die Datei wird als XLSX heruntergeladen
4. **Formeln bleiben erhalten!**

---

## Tastatur-Shortcuts

### Navigation

| Shortcut | Aktion |
|----------|--------|
| `↑` / `↓` / `←` / `→` | Zwischen Zellen navigieren |
| `Tab` | Zur nächsten Zelle (rechts) |
| `Shift + Tab` | Zur vorherigen Zelle (links) |
| `Enter` | Zur Zelle darunter |
| `Shift + Enter` | Zur Zelle darüber |
| `Ctrl + Home` | Zur ersten Zelle (A1) |
| `Ctrl + End` | Zur letzten Zelle |

### Bearbeitung

| Shortcut | Aktion |
|----------|--------|
| `F2` | Zelle bearbeiten |
| `Esc` | Bearbeitung abbrechen |
| `Delete` | Zellinhalt löschen |
| `Ctrl + Z` | Rückgängig (Undo) |
| `Ctrl + Y` | Wiederholen (Redo) |
| `Ctrl + C` | Kopieren |
| `Ctrl + V` | Einfügen |
| `Ctrl + X` | Ausschneiden |

### Formeln

| Shortcut | Aktion |
|----------|--------|
| `=` | Formel beginnen |
| `Ctrl + Enter` | Formel übernehmen |
| `F9` | Formel neu berechnen |

### Speichern

| Shortcut | Aktion |
|----------|--------|
| `Ctrl + S` | Matrix speichern |

---

## Tipps und Tricks

### 1. Auto-Save nutzen

Aktivieren Sie Auto-Save um Datenverlust zu vermeiden:
- Kontrollkästchen **"🔄 Auto-Save"** aktivieren
- Speichert automatisch alle 60 Sekunden

### 2. Formeln anzeigen

Zeigen Sie Formeln statt Werte an:
- Kontrollkästchen **"Formeln anzeigen"** aktivieren
- Nützlich zum Debuggen

### 3. Beispiel-Matrizen nutzen

Lernen Sie von Beispielen:
- Laden Sie eine Beispiel-Matrix
- Erkunden Sie die Formeln
- Passen Sie sie an Ihre Bedürfnisse an

### 4. Undo/Redo verwenden

Keine Angst vor Fehlern:
- Bis zu 50 Schritte rückgängig machen
- **Strg+Z** für Undo
- **Strg+Y** für Redo

### 5. Zellformatierung

Formatieren Sie Zellen für bessere Lesbarkeit:
- **Währung** für Preise
- **Prozent** für Anteile
- **Datum** für Zeitangaben

### 6. IFERROR verwenden

Vermeiden Sie Fehleranzeigen:
```
=IFERROR(A1/B1, 0)
```
Gibt 0 zurück wenn Division durch Null

### 7. Tastaturnavigation

Arbeiten Sie schneller:
- Aktivieren Sie **"⌨️ Tastaturnavigation"**
- Nutzen Sie Pfeiltasten statt Maus

---

## Fehlerbehebung

### Häufige Fehler

#### #DIV/0! - Division durch Null

**Problem:** Sie versuchen durch Null zu teilen

**Lösung:**
```
=IFERROR(A1/B1, 0)
```

#### #REF! - Ungültige Referenz

**Problem:** Die Formel verweist auf eine nicht existierende Zelle

**Lösung:**
- Überprüfen Sie alle Zellreferenzen
- Stellen Sie sicher dass die Zellen existieren

#### #CIRCULAR! - Zirkelbezug

**Problem:** Die Formel verweist auf sich selbst

**Lösung:**
- Überprüfen Sie die Formel
- Brechen Sie die Zirkelkette

#### #NAME? - Unbekannte Funktion

**Problem:** Funktionsname falsch geschrieben

**Lösung:**
- Überprüfen Sie die Schreibweise
- Verwenden Sie Großbuchstaben: `SUM` statt `sum`

#### #VALUE! - Falscher Werttyp

**Problem:** Falsche Datentypen in der Formel

**Lösung:**
- Überprüfen Sie die Argumente
- Stellen Sie sicher dass Zahlen als Zahlen eingegeben sind

### Performance-Probleme

**Problem:** Matrix lädt langsam

**Lösungen:**
- Reduzieren Sie die Anzahl der Formeln
- Verwenden Sie einfachere Formeln
- Aktivieren Sie Caching (standardmäßig aktiv)

**Problem:** Neuberechnung dauert lange

**Lösungen:**
- Vermeiden Sie Zirkelbezüge
- Reduzieren Sie verschachtelte Formeln
- Teilen Sie komplexe Berechnungen auf

### Import-Probleme

**Problem:** CSV-Import schlägt fehl

**Lösungen:**
- Überprüfen Sie das Encoding (UTF-8 empfohlen)
- Prüfen Sie den Delimiter (`;` oder `,`)
- Stellen Sie sicher dass die Datei gültig ist

**Problem:** Excel-Formeln werden nicht übernommen

**Lösungen:**
- Verwenden Sie .xlsx statt .xls
- Stellen Sie sicher dass Formeln mit `=` beginnen
- Prüfen Sie ob die Funktionen unterstützt werden

---

## Support

Bei weiteren Fragen oder Problemen:

1. Schauen Sie in die **Fehlerdetails** (bei Fehlern in Zellen)
2. Nutzen Sie die **Tooltips** (Maus über Elemente bewegen)
3. Laden Sie eine **Beispiel-Matrix** zum Lernen
4. Kontaktieren Sie den Support

---

**Version:** 1.0  
**Letzte Aktualisierung:** November 2024
