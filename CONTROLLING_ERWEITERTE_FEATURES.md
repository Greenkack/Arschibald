# Controlling - Erweiterte Funktionen

## Neue Features (Dokumentation)

### 1. 🏢 Team-Auswertung

**Funktion:** Auswertung aller Mitarbeiter einer Position als Team

**Features:**

- Aggregierte Team-Leistungsquoten (Gesamtwerte)
- Statistiken: Durchschnitt, Min, Max für jede Quote
- Identifikation von Top- und Low-Performern
- Detaillierte Einzelauswertung pro Mitarbeiter
- PDF-Export mit allen Team-Daten

**Verwendung:**

1. Navigiere zu: `controlling_advanced_features_ui.py` → Tab "Team-Auswertung"
2. Wähle Position (z.B. "Call Agent")
3. Optional: Inaktive Mitarbeiter einbeziehen
4. Wähle Zeitraum (Von - Bis)
5. Klicke "Team-Auswertung erstellen"
6. Exportiere als PDF mit "Als PDF exportieren"

**Beispiel-Output:**

```
Team-Leistungsquoten (Gesamt):
- Abschlussquote: 18.50%
- Terminvereinbarungsquote: 35.20%
- Termine-Anfahrquote: 65.80%

Statistiken:
Abschlussquote:
  Durchschnitt: 18.50%
  Min: 12.00% (Mitarbeiter A)
  Max: 25.00% (Mitarbeiter B)
```

**Technische Implementierung:**

- Datei: `controlling/team_analytics.py`
- Klasse: `TeamAnalytics.generate_team_report()`
- PDF-Export: `ReportGenerator.export_team_report_to_pdf()`

---

### 2. 🔍 Mitarbeiter-Vergleich

**Funktion:** Direkter Vergleich von 2+ Mitarbeitern (gleiche oder verschiedene Positionen)

**Features:**

- Ranking-System für jede Leistungsquote (1., 2., 3., ...)
- Berechnung von absoluten und relativen Unterschieden
- Detaillierte Vergleichstabellen
- PDF-Export mit Ranking und Unterschieden

**Verwendung:**

1. Navigiere zu: `controlling_advanced_features_ui.py` → Tab "Mitarbeiter-Vergleich"
2. Optional: Nach Position filtern
3. Wähle mindestens 2 Mitarbeiter aus
4. Wähle Zeitraum (Von - Bis)
5. Klicke "Vergleich erstellen"
6. Exportiere als PDF mit "Als PDF exportieren"

**Beispiel-Output:**

```
Leistungsranking - Abschlussquote:
🥇 1. Mitarbeiter B: 25.00%
🥈 2. Mitarbeiter C: 20.00%
🥉 3. Mitarbeiter A: 12.00%

Leistungsunterschiede:
Bester: Mitarbeiter B (25.00%)
Schlechtester: Mitarbeiter A (12.00%)
Differenz: 13.00% (absolut)
Differenz: 108.33% (relativ)
```

**Technische Implementierung:**

- Datei: `controlling/team_analytics.py`
- Klasse: `TeamAnalytics.generate_comparison_report()`
- PDF-Export: `ReportGenerator.export_comparison_report_to_pdf()`

---

### 3. 📄 PDF-Export mit PDF Bytes

**Funktion:** Alle Auswertungen werden direkt als PDF-Bytes generiert (ohne Dateisystem)

**Vorteile:**

- ✅ Keine temporären Dateien
- ✅ Direkter Download über Streamlit
- ✅ Speichereffizient
- ✅ Sicherer (keine Datei-Leaks)

**Unterstützte Berichte:**

- Einzelmitarbeiter-Berichte (vorher schon vorhanden)
- Team-Auswertungen (NEU)
- Mitarbeiter-Vergleiche (NEU)

**Technische Details:**

```python
# Beispiel-Code
report_gen = ReportGenerator(db)
pdf_bytes = report_gen.export_team_report_to_pdf(team_data)

# Streamlit Download
st.download_button(
    label="PDF herunterladen",
    data=pdf_bytes,
    file_name="team_auswertung.pdf",
    mime="application/pdf"
)
```

**Methoden:**

- `export_report_to_pdf()` - Einzelmitarbeiter
- `export_team_report_to_pdf()` - Team
- `export_comparison_report_to_pdf()` - Vergleich

---

### 4. 🎨 PDF-Farbeinstellungen

**Funktion:** Individuelle Anpassung aller PDF-Farben

**Features:**

- 6 vordefinierte Farbschemata
- Individuelle Farbanpassung (14 Farboptionen)
- Live-Vorschau
- Speicherung in JSON-Datei

**Vordefinierte Schemata:**

1. **Standard (Blau)** - #366092 (Original)
2. **Grün** - #2E7D32 (Natürlich)
3. **Rot** - #C62828 (Kraftvoll)
4. **Orange** - #E65100 (Energetisch)
5. **Lila** - #6A1B9A (Kreativ)
6. **Grau (Monochrom)** - #424242 (Professionell)
7. **Dunkel** - #1A1A1A (Modern)

**Anpassbare Farben:**

**Hauptfarben:**

- Primärfarbe (Hauptelemente)
- Sekundärfarbe (Akzente)

**Textfarben:**

- Titel
- Standard-Text
- Header-Text (auf farbigem Hintergrund)

**Hintergrundfarben:**

- Tabellen-Header
- Tabellenzeilen
- Alternative Zeilen

**Akzentfarben:**

- Erfolg (Grün)
- Warnung (Gelb)
- Fehler (Rot)
- Info (Blau)

**Rahmen & Linien:**

- Rahmenfarbe
- Rasterlinien

**Verwendung:**

1. Navigiere zu: `controlling_advanced_features_ui.py` → Tab "PDF-Farben"
2. **Option A:** Wähle vordefiniertes Schema → "Schema anwenden"
3. **Option B:** Passe individuelle Farben an → "Farben speichern"
4. Vorschau ansehen im Tab "Vorschau"

**Technische Implementierung:**

- Datei: `controlling/pdf_config.py`
- Klasse: `PDFConfigManager`
- Dataclass: `PDFColorScheme`
- Speicherort: `data/pdf_colors.json`

**Beispiel JSON:**

```json
{
  "primary_color": "#366092",
  "secondary_color": "#5B9BD5",
  "title_color": "#366092",
  "text_color": "#000000",
  "header_text_color": "#FFFFFF",
  "table_header_bg": "#366092",
  "table_row_bg": "#F5F5DC",
  "table_alt_row_bg": "#FFFFFF",
  "success_color": "#28A745",
  "warning_color": "#FFC107",
  "error_color": "#DC3545",
  "info_color": "#17A2B8",
  "border_color": "#000000",
  "grid_color": "#CCCCCC"
}
```

**Code-Integration:**

```python
from controlling.pdf_config import get_color_scheme

# In PDF-Generierung
color_scheme = get_color_scheme()

# Verwende Farben
title_style = ParagraphStyle(
    'CustomTitle',
    textColor=colors.HexColor(color_scheme.title_color)
)

table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(color_scheme.table_header_bg)),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(color_scheme.header_text_color)),
]))
```

---

## Zusammenfassung

**Alle 4 Anforderungen erfüllt:**

✅ **1. Team-Auswertung** - Alle Mitarbeiter einer Position gemeinsam auswerten  
✅ **2. Mitarbeiter-Vergleich** - Direkter Vergleich von Mitarbeitern derselben Position  
✅ **3. PDF Bytes Export** - Alle Ergebnisse als PDF mit Bytes-Rückgabe (kein Dateisystem)  
✅ **4. PDF-Farbeinstellungen** - Individuelle Anpassung aller PDF-Farben  

---

## Verwendung starten

**1. Starte die erweiterten Features:**

```powershell
streamlit run controlling_advanced_features_ui.py
```

**2. Oder integriere in Haupt-App:**

```python
# In gui.py oder controlling_ui.py

from controlling_advanced_features_ui import (
    render_team_analysis_tab,
    render_comparison_tab,
    render_pdf_color_settings
)

# Füge neue Tabs hinzu
tab_team, tab_comp, tab_colors = st.tabs([
    "Team-Auswertung",
    "Mitarbeiter-Vergleich",
    "PDF-Farben"
])

with tab_team:
    render_team_analysis_tab()

with tab_comp:
    render_comparison_tab()

with tab_colors:
    render_pdf_color_settings()
```

---

## Dateien-Übersicht

**Neu erstellte Dateien:**

1. `controlling/team_analytics.py` - Team-Auswertung & Vergleich
2. `controlling/pdf_config.py` - PDF-Farbkonfiguration
3. `controlling_advanced_features_ui.py` - Streamlit UI
4. `CONTROLLING_ERWEITERTE_FEATURES.md` - Diese Dokumentation

**Geänderte Dateien:**

1. `controlling/report_generator.py` - PDF-Export-Methoden erweitert
   - `export_team_report_to_pdf()` hinzugefügt
   - `export_comparison_report_to_pdf()` hinzugefügt
   - Farbschema-Integration in `export_report_to_pdf()`

---

## Technische Details

**Dependencies:**

- SQLAlchemy (bereits vorhanden)
- ReportLab (bereits vorhanden)
- Streamlit (bereits vorhanden)

**Keine zusätzlichen Installationen erforderlich!**

**Datenbank:**

- Nutzt bestehende Controlling-Tabellen
- Keine Schema-Änderungen erforderlich

**Performance:**

- Team-Auswertung: O(n) für n Mitarbeiter
- Vergleich: O(n log n) wegen Sortierung für Rankings
- PDF-Generierung: ~1-3 Sekunden pro Bericht

---

**Erstellt am:** 2025-12-07  
**Version:** 1.0  
**Status:** Produktionsbereit ✅
