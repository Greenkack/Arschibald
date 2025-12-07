# Auswertungsperioden-System - Benutzerhandbuch

## 🎯 Übersicht

Das **Auswertungsperioden-System** ermöglicht strukturierte, zeitraum-basierte Leistungserfassung und -auswertung im Controlling-Bereich. Du kannst Auswertungen erstellen, speichern, bearbeiten und archivieren.

---

## ✨ Neue Funktionen

### 1. 🗓️ Auswertungsperioden erstellen

Im Tab **"📝 Leistungsdaten erfassen"** findest du ganz oben die Perioden-Verwaltung:

#### **Button: "➕ Neue Auswertung starten"**
Klicke diesen Button, um eine neue Auswertungsperiode zu erstellen.

#### **Zeitraum-Typen:**
- **📅 Täglich** - Einzelner Tag
- **📆 Wöchentlich** - 7-Tage-Zeitraum
- **📊 Monatlich** - Automatische Monatsgrenzen (z.B. 1.-31. Dezember)
- **📈 Quartalsweise** - Q1-Q4 mit automatischen Grenzen
- **📉 Jährlich** - 1. Januar - 31. Dezember
- **🎯 Benutzerdefiniert** - Freie Datumswahl

#### **Automatische Namensgebung:**
Bei Standard-Typen (Monatlich, Quartalsweise, Jährlich) wird der Name automatisch generiert:
- Monatlich: "Dezember 2025"
- Quartalsweise: "Q1 2025"
- Jährlich: "Jahr 2025"

Du kannst den Namen aber auch manuell anpassen!

---

### 2. 💾 Perioden-Auswahl & Verknüpfung

#### **Aktive Periode wählen:**
Nach dem Erstellen kannst du eine Periode aus der Dropdown-Liste wählen.  
**WICHTIG:** Alle Leistungsdaten, die du erfasst, werden automatisch mit der aktiven Periode verknüpft!

#### **Direkter Modus:**
Wenn du **"Keine Periode (direkter Modus)"** wählst, werden Daten OHNE Periodenverknüpfung gespeichert (wie bisher).

#### **Perioden-Löschen:**
Mit dem **"🗑️ Periode löschen"** Button kannst du Perioden entfernen.  
⚠️ **Achtung:** Alle Leistungsdaten der Periode werden ebenfalls gelöscht!

---

### 3. 📊 Leistungsdaten mit Perioden erfassen

1. **Periode auswählen** (oder "Direkter Modus")
2. **Mitarbeiter wählen**
3. **Datum eingeben**
4. **Kriterien ausfüllen** (wie gewohnt)
5. **Speichern** → Daten werden mit gewählter Periode verknüpft

✅ **Bestätigung:** Nach dem Speichern siehst du: *"X Leistungsdaten erfolgreich gespeichert! (Periode: Dezember 2025)"*

---

### 4. 📁 Archiv mit Perioden-Management

Im Tab **"📁 Archiv"** gibt es jetzt 2 Bereiche:

#### **📊 Berichte** (wie bisher)
Gespeicherte Reports anzeigen und laden.

#### **🗓️ Auswertungsperioden** (NEU!)
Alle Perioden mit folgenden Funktionen:

**Filter:**
- **Status:** 🟢 Aktiv / 🔵 Abgeschlossen / ⚫ Archiviert
- **Typ:** Täglich, Monatlich, Jährlich, etc.

**Aktionen pro Periode:**
- **✅ Abschließen** - Aktive Periode als abgeschlossen markieren
- **📂 Aktivieren** - Periode zur aktiven Periode machen
- **📦 Archivieren** - Abgeschlossene Periode archivieren
- **🗑️ Löschen** - Periode + zugehörige Daten löschen

**Anzeige:**
- Name & Zeitraum
- Typ & Status
- Dauer in Tagen
- Beschreibung (falls vorhanden)
- Mitarbeiter-Zuordnung (oder "Alle (global)")
- **Anzahl Leistungsdaten** - Wie viele Einträge in dieser Periode gespeichert sind

---

## 🔄 Workflow-Beispiel

### Monatliche Auswertung erstellen:

1. **Controlling → Tab "📝 Leistungsdaten erfassen"**
2. Klicke **"➕ Neue Auswertung starten"**
3. Wähle **"📊 Monatlich"**
4. Wähle **Monat**: Dezember, **Jahr**: 2025
5. Optional: Beschreibung eingeben (z.B. "Jahresendauswertung")
6. Klicke **"✅ Periode erstellen"**

✅ Periode ist jetzt automatisch aktiv!

7. Wähle **Mitarbeiter**
8. Erfasse **Leistungsdaten** wie gewohnt
9. Klicke **"Leistungsdaten speichern"**

✅ Daten sind jetzt mit "Dezember 2025" verknüpft!

10. Am Monatsende: **Archiv → Tab "🗓️ Auswertungsperioden"**
11. Finde "Dezember 2025", klicke **"✅ Abschließen"**

✅ Periode ist jetzt abgeschlossen und kann archiviert werden!

---

## 🎨 Perioden-Status-Workflow

```
🟢 AKTIV
   ↓ (Abschließen-Button)
🔵 ABGESCHLOSSEN
   ↓ (Archivieren-Button)
⚫ ARCHIVIERT
```

**Hinweise:**
- Aktive Perioden kannst du jederzeit aktivieren/bearbeiten
- Abgeschlossene Perioden sind "eingefroren" aber sichtbar
- Archivierte Perioden sind langfristig gespeichert

---

## 📊 Kalender-Integration

### Monatliche Auswertung:
- Automatische Berechnung: 1. bis letzter Tag des Monats
- Beispiel: Januar → 1.1. - 31.1.
- Beispiel: Februar → 1.2. - 28./29.2. (Schaltjahr-fähig!)

### Quartalsweise:
- Q1: 1. Januar - 31. März
- Q2: 1. April - 30. Juni
- Q3: 1. Juli - 30. September
- Q4: 1. Oktober - 31. Dezember

### Jährliche Auswertung:
- Automatisch: 1. Januar - 31. Dezember

### Benutzerdefiniert:
- Freie Start- und Enddatum-Wahl
- Ideal für projektbezogene Auswertungen

---

## 🔒 Rückwärtskompatibilität

✅ **Keine Sorge!** Das System ist vollständig rückwärtskompatibel:

- **Alte Leistungsdaten** bleiben unverändert erhalten
- **Direkter Modus** (ohne Periode) funktioniert weiterhin
- **Bestehende Berichte** funktionieren normal
- **Keine Daten gehen verloren** bei der Migration

**Migration automatisch durchgeführt:**
- Neue Tabelle `controlling_evaluation_periods` erstellt
- Spalte `period_id` zu `controlling_performance_data` hinzugefügt (nullable!)

---

## 💡 Tipps & Best Practices

### ✅ Empfehlungen:

1. **Monatliche Perioden für Standardauswertungen**
   - Erstelle am Monatsanfang die Periode für den aktuellen Monat
   - Erfasse täglich Daten innerhalb dieser Periode
   - Schließe die Periode am Monatsende ab

2. **Beschreibungen nutzen**
   - Notiere Ziele oder Besonderheiten der Periode
   - Beispiel: "Urlaubsmonat - reduzierte Ziele"

3. **Globale vs. Mitarbeiter-spezifische Perioden**
   - **Global** (kein Mitarbeiter): Für allgemeine Zeiträume
   - **Mitarbeiter-spezifisch**: Für individuelle Auswertungen (z.B. Probezeit)

4. **Archivierung**
   - Schließe Perioden ab, sobald sie vorbei sind
   - Archiviere alte Perioden, um die Liste übersichtlich zu halten

5. **Keine Überlappungen**
   - Das System warnt bei überlappenden Perioden
   - Idealerweise: Lückenlose, nicht überlappende Perioden

---

## 🆘 Troubleshooting

### ❓ "Ich sehe meine Periode nicht in der Liste"
- **Lösung:** Überprüfe den Status-Filter im Archiv
- Aktive Perioden: Status-Filter auf "🟢 Aktiv" setzen

### ❓ "Ich habe versehentlich eine Periode gelöscht"
- **Problem:** Gelöschte Perioden + Daten sind permanent weg
- **Vorbeugung:** Nutze "Archivieren" statt "Löschen"

### ❓ "Leistungsdaten erscheinen nicht in meiner Periode"
- **Lösung 1:** Überprüfe, ob die Periode beim Speichern aktiv war
- **Lösung 2:** Datum der Leistungsdaten muss im Zeitraum der Periode liegen

### ❓ "Kann ich Daten nachträglich zu einer Periode hinzufügen?"
- **Ja!** Wähle die Periode aus und erfasse neue Daten
- Die Daten werden automatisch verknüpft

---

## 🎯 Zusammenfassung

**Was du jetzt kannst:**
✅ Strukturierte Auswertungen erstellen (täglich bis jährlich)
✅ Leistungsdaten mit Zeiträumen verknüpfen
✅ Perioden speichern, bearbeiten, abschließen
✅ Archiv mit Statusverwaltung nutzen
✅ Übersicht über alle Auswertungen behalten

**Kernvorteil:**
Statt unstrukturierter Dateneingabe hast du jetzt **organisierte, zeitraum-basierte Auswertungen** mit vollständiger Kontrolle über den Lebenszyklus (Aktiv → Abgeschlossen → Archiviert).

---

**Viel Erfolg mit dem neuen Auswertungsperioden-System! 🚀**
