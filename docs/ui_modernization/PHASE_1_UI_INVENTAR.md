# Phase 1: UI/UX Inventar & Analyse

**Datum**: 2025-12-09  
**Status**: IN PROGRESS  
**Ziel**: Vollständige Bestandsaufnahme aller UI-Komponenten für Modernisierung mit shadcn/ui

---

## 1. INTRO_SCREEN.PY - Startbildschirm (760 Zeilen)

### Aktuelle Komponenten

#### Layout-Struktur
- **3-Column Layout**: `st.columns([1, 5, 1])` (Zeile 387)
  - Zentrale Spalte für Hauptinhalt
  - Seitenränder für optionale Logo-Bilder

#### Text & Content
- **st.markdown** (16x verwendet):
  - Hero Section mit HTML/CSS (Zeile 377-430)
  - Styling mit inline CSS
  - Gradient Backgrounds
  - Responsive Text

#### Eingabefelder (Login/Registrierung)
- **st.text_input** (10x):
  - Username (Zeile 487, 592)
  - Password (Zeile 489, 594, 598)
  - Email (Zeile 603)
  - Phone (Zeile 606)
  - Full Name (Zeile 600)
  - Firmeninfo-Felder (bei Registrierung)

#### Video/Bild-Anzeige
- **st.video**: Video-Embed (Zeile 412)
- **st.image**: Kein direkter Aufruf (Base64-Embed via HTML)

#### Sektionen
- **st.markdown("---")**: Trennlinien (3x)
- **st.markdown("#### Titel")**: Überschriften (2x)

### Verbesserungspotenzial (shadcn/ui)

#### Hero Section
- **Card Component**: Logo + Title in elevated Card statt HTML
- **Badge**: Version Badge unten rechts
- **Gradient Background**: CSS-basiert beibehalten

#### Feature Carousel
- **Carousel Component**: 5 Slides für Features
  - Photovoltaik-Kalkulator
  - Wärmepumpen-Planung
  - CRM-System
  - Controlling & Analytics
  - PDF-Angebotserstellung
- **Auto-Advance**: 5 Sekunden Timer
- **Navigation Dots**: Slide-Indikatoren

#### Login/Registrierung
- **Form Component**: Strukturiertes Formular
  - Input Fields mit Validation Badges
  - Error Alerts bei falschem Login
  - Success Toast bei Registrierung
- **Button Component**: Primary/Secondary Variants
- **Drawer**: Registrierung in Side Drawer statt Expander

#### Quick Start
- **Drawer Component**: "Los geht's" Side Drawer
  - Schnellzugriff-Links zu Hauptfunktionen
  - Neueste Berechnungen (falls vorhanden)

#### Status Indicators
- **Badge**: System Health (Datenbank Status)
- **Tooltip**: Letzte Aktualisierung

---

## 2. GUI.PY - Hauptnavigation & Orchestrator (3219 Zeilen)

### Aktuelle Komponenten

#### Navigation (Sidebar)
- **st.button** (20+ Navigations-Buttons):
  - HAUPTMENÜ (7 Buttons): PV-Rechner, Wärmepumpe, Daten, Analyse, PDF, Einstellungen, Info
  - BUSINESS (5 Buttons): CRM, Controlling, etc.
  - TOOLS (5 Buttons): Admin, Theme, etc.
- **Button Styling**: Custom CSS mit Icons (Zeile 1684, 1707, 1730)
- **st.markdown**: Kategorie-Header (Zeile 1669, 1695, 1718)

#### Top Navigation
- **st.tabs**: Haupttabs für verschiedene Bereiche (Zeile 2215)
  - tab_single_pdf
  - tab_pdf_preview
  - tab_multi_offers

#### Layout
- **st.columns**: 2-Column Layouts (Zeile 1821, 1844, 2302, 2455)
- **st.expander**: Collapsible Sections (Zeile 1866)
- **st.markdown("---")**: Trennlinien (10x)

#### Interaktive Elemente
- **st.selectbox**: Firmen-Auswahl (Zeile 1807)
- **st.checkbox**: Debug-Optionen (Zeile 2392, 2409)
- **st.subheader**: Sektions-Titel (Zeile 1764, 1842, 2281)
- **st.header**: Seiten-Titel (Zeile 2137, 2144, 2211)

### Verbesserungspotenzial (shadcn/ui)

#### Sidebar Navigation
- **Card Components**: Navigation Cards statt Buttons
  - Icon + Text in Card Layout
  - Active State Highlighting (Border + Background)
  - Hover Effects (Elevation)
- **Badge**: Notification Counts (z.B. "CRM (3 neue)")

#### Top Bar
- **Breadcrumbs**: Navigation History
  - Startseite > PV-Rechner > Ergebnis
  - Click-to-Navigate
- **Drawer**: User Menu (rechts oben)
  - Profil-Einstellungen
  - Abmelden
- **Toggle**: Theme Switcher (Dark/Light Mode)

#### Tab Navigation
- **Modern Tabs**: shadcn Tabs mit Icons
  - Tab Counts/Badges
  - Active Indicator (Underline Animation)
  - Smooth Transitions

#### Loading States
- **Skeleton Loader**: Während Page Load
- **Progress Bar**: Für lange Operationen (z.B. PDF-Generierung)

#### Drawer Components
- **Firmen-Auswahl**: Large Drawer statt Selectbox
  - Card pro Firma mit Logo + Details
  - Quick Switch Actions
- **Notizen**: Drawer für Notiz-Hinzufügen
  - Gespeicherte Notizen als Cards

---

## 3. DATA_INPUT.PY - Dateneingabe (1701 Zeilen)

### Aktuelle Komponenten (basierend auf Imports)

#### Eingabefelder
- **st.text_input**: Kundendaten, Adresse, etc.
- **st.number_input**: Numerische Werte (kWh, kWp, etc.)
- **st.selectbox**: Auswahl-Felder (Salutation, Region, etc.)
- **st.checkbox**: Optionen (Speicher, Monitoring, etc.)
- **st.slider**: Bereiche (Dachneigung, Ausrichtung, etc.)

#### Session Widgets (bereits integriert)
- **session_text_input**: Persistente Texteingabe
- **session_number_input**: Persistente Zahleingabe
- **session_selectbox**: Persistente Auswahl
- **session_checkbox**: Persistente Checkbox

#### shadcn/ui (bereits vorbereitet)
- **SUI_AVAILABLE**: Fallback-Pattern implementiert
- Wrapper für shadcn Components

### Verbesserungspotenzial (shadcn/ui)

#### Form Cards
- **Card für Kundendaten**:
  - Header: "Kundendaten"
  - Content: Eingabefelder
  - Footer: Speichern/Zurücksetzen Buttons
- **Card für Standortdaten**:
  - Map Icon im Header
  - PLZ mit Auto-Complete
  - Adresse mit Validation Badge
- **Card für Dachparameter**:
  - Dachtyp-Auswahl (Radio Cards mit Icons)
  - Neigung Slider (0-90°) mit Visual Indicator
  - Ausrichtung Slider (0-360°) mit Kompass-Icon
- **Card für Stromverbrauch**:
  - kWh Input mit Live-Feedback
  - Verbrauchsprofil-Chart Preview

#### Smart Input Components
- **PLZ Input**: Auto-Complete mit Dropdown
- **Validation Badges**:
  - Success (grün) bei korrekter Eingabe
  - Error (rot) bei Fehlern
  - Warning (gelb) bei Empfehlungen
- **Tooltips**: Hilfe-Texte bei Hover
- **Slider mit Live Preview**:
  - Dachneigung: Visual Roof Angle
  - Ausrichtung: Compass Visualization
  - Modulanzahl: kWp-Berechnung live

#### Accordion Sections
- **Erweiterte Optionen**: Accordion
  - Verschattungsanalyse
  - Monitoring-Optionen
  - Garantie-Details
- **Speicher-Optionen**: Accordion
  - Batterietyp-Auswahl
  - Kapazität Slider
  - Lademanagement

#### Progress Indicator
- **Multi-Step Form**:
  - Step 1/5: Kundendaten
  - Step 2/5: Standort
  - Step 3/5: Dach
  - Step 4/5: Verbrauch
  - Step 5/5: Optionen
- **Completion Ring**: Prozent-Anzeige

#### Quick Actions Drawer
- **"Beispieldaten laden"**: Drawer mit Templates
- **"Letzte Eingaben"**: Historie als Cards
- **"Favoriten"**: Häufige Konfigurationen speichern

---

## 4. ANALYSIS.PY - Analyse & Charts (2000+ Zeilen)

### Aktuelle Komponenten

#### Layout
- **st.columns**: Grid Layouts
  - 6-Column Grid (Zeile 549): KPI Metrics
  - 4-Column Grid (Zeile 623): Economic Metrics
  - 3-Column Grid (Zeile 699): Financial Metrics
  - 2-Column Grid (Zeile 948): Chart Comparison

#### Metrics Display
- **st.metric** (15x verwendet):
  - Gesamtertrag (kWh)
  - Autarkie (%)
  - ROI (Jahre)
  - CO2-Einsparung (kg)
  - Investitionskosten (EUR)
  - Fördersumme (EUR)
  - Eigenverbrauch (%)
  - Netzeinspeisung (kWh)
  - Etc.

#### Charts (Plotly)
- **st.plotly_chart** (10+ Charts):
  - 20-Jahre Ertragsprognose (Zeile 878)
  - Amortisationszeit (Zeile 906)
  - Kostenstruktur (Zeile 914)
  - Dynamische Tarife (Zeile 922)
  - Verbrauchsprofil (Zeile 942)

#### Collapsible Sections
- **st.expander** (Smart Expander):
  - Preismodifikationen (Zeile 359)
  - Chart Sections (auto-generiert)

### Verbesserungspotenzial (shadcn/ui)

#### Dashboard Grid
- **4-Column KPI Cards**:
  - **Gesamtertrag Card**:
    - Icon: Sun/Lightning
    - Value: Large Display (kWh)
    - Trend: Delta Arrow (vs. letztes Jahr)
  - **Autarkie Card**:
    - Icon: Battery/Shield
    - Value: Percentage Ring (circular progress)
    - Info Tooltip
  - **ROI Card**:
    - Icon: Chart/Timeline
    - Value: Jahre
    - Countdown Visualization
  - **CO2-Einsparung Card**:
    - Icon: Leaf/Tree
    - Value: kg CO2
    - Tree Equivalents Badge

#### Chart Cards
- **Chart in Card Layout**:
  - **Card Header**:
    - Titel
    - Export Button (PNG/SVG)
    - Fullscreen Button
  - **Card Content**:
    - Plotly Chart (responsive)
    - Chart Type Selector (Tabs)
  - **Card Footer**:
    - Legende
    - Data Source Info

#### Data Tables (wenn vorhanden)
- **Table Card**:
  - Sticky Header
  - Row Hover Highlighting
  - Sortable Columns (Icon Indicators)
  - Filter Drawer (Side Drawer)
  - Pagination
  - Rows per Page Selector

#### Comparison Features
- **Scenario Carousel**:
  - Verschiedene PV-Konfigurationen
  - Swipe zwischen Varianten
  - Side-by-Side Comparison Drawer

#### Export Options
- **Export Drawer**:
  - Format-Auswahl (Radio Cards):
    - PDF
    - Excel
    - CSV
    - JSON
  - Optionen:
    - Include Charts (Toggle)
    - Data Resolution (Dropdown)
  - Progress Indicator während Export

---

## 5. COMPONENTS/SHADCN_UI_INTEGRATION.PY - UI Library (871 Zeilen)

### Bereits implementierte Komponenten

#### Button Components (Zeile 49-84)
- **button()**: Default, Destructive, Outline, Secondary, Ghost, Link
- **Sizes**: Default, Small, Large, Icon
- **Fallback**: Native st.button

#### Badge Component (Zeile 93-132)
- **badge()**: Default, Secondary, Destructive, Outline
- **Fallback**: Styled st.markdown

#### Card Component (Zeile 141-150)
- **card()**: Title, Description, Content
- **Fallback**: NICHT SICHTBAR (nur Header)

### Fehlende Komponenten (zu implementieren)

#### Carousel
- **carousel()**: Slides mit Navigation
- **carousel_slide()**: Einzelne Slide
- **carousel_dots()**: Pagination Dots

#### Drawer/Sheet
- **drawer()**: Side Drawer (left/right)
- **sheet()**: Modal Drawer
- **drawer_trigger()**: Button zum Öffnen

#### Slider
- **slider()**: Value Slider mit Formatierung
- **range_slider()**: Range Selection

#### Alert
- **alert()**: Info, Success, Warning, Error
- **alert_title()**: Alert Header
- **alert_description()**: Alert Body

#### Skeleton Loader
- **skeleton()**: Skeleton für Loading States
- **skeleton_card()**: Card Skeleton
- **skeleton_text()**: Text Skeleton

#### Progress
- **progress()**: Linear Progress Bar
- **progress_circle()**: Circular Progress

#### Tooltip & Popover
- **tooltip()**: Tooltip bei Hover
- **popover()**: Click-to-Show Info

#### Tabs (Modern)
- **tabs()**: Tab Container
- **tab_item()**: Einzelner Tab

#### Accordion
- **accordion()**: Accordion Container
- **accordion_item()**: Einzelner Accordion

---

## 6. Fehlende Seiten (noch zu analysieren)

### CRM.PY
- Kunden-Übersicht (Grid/List)
- Kunden-Detail Drawer
- Such- und Filter-System
- Aktivitäten Timeline
- Dokument-Management

### CONTROLLING_UI.PY
- Dashboard Header (KPI Cards)
- Chart Section
- Mitarbeiter-Cards
- Team-Auswertung Carousel
- Report Export Drawer
- Rangliste (Podium + Cards)

### ADMIN_PANEL.PY
- Vertical Tab Navigation
- Produkt-Verwaltung (Grid)
- Preismatrix Upload
- Benutzer-Verwaltung
- Einstellungen Cards
- System Logs (Table)

### DOC_OUTPUT.PY
- PDF Preview Card
- Aktionen Toolbar (Fixed Bottom)
- Share Drawer
- Version History Drawer
- Template Selector Carousel

### HEATPUMP_UI.PY
- Konfiguration Cards
- Verbrauchsprognose Charts
- Kostenrechnung Cards
- Produkt-Vergleich Drawer
- Tarif-Optimierung

### OPTIONS.PY
- Einstellungen Cards
- Theme-Auswahl
- Sprach-Auswahl
- Benachrichtigungen

---

## 7. Emoji-Bestand (zu entfernen)

### Suche durchgeführt
- **Regex-Fehler**: Unicode-Range zu groß für grep_search
- **Alternative**: Manual Search in bekannten Bereichen

### Bekannte Emoji-Verwendung (aus Controlling-Projekt)
- **controlling_ui.py**: 150+ Emojis entfernt
- **admin_controlling_settings_ui.py**: 60+ Emojis entfernt
- **controlling/migrations/*.py**: Logger Emojis entfernt
- **controlling/analytics.py**: Warning Emojis entfernt

### Nächste Schritte für Emoji-Removal
1. **Python-Script erstellen**: `scripts/remove_all_emojis.py`
   - Regex: `[\U0001F300-\U0001F9FF]` (breiterer Range)
   - Batch-Replace in allen .py Dateien
2. **Mapping erstellen**: Emoji -> Text-Äquivalent
3. **Pre-Commit Hook**: Emoji-Detection
4. **Test**: `tests/test_no_emojis.py`

---

## 8. Zusammenfassung & Prioritäten

### Hohe Priorität (Phase 1 Fokus)
1. **INTRO_SCREEN.PY**: Hero Section, Feature Carousel, Login Card
2. **GUI.PY**: Sidebar Navigation Cards, Breadcrumbs, Modern Tabs
3. **DATA_INPUT.PY**: Form Cards, Smart Inputs, Progress Indicator
4. **ANALYSIS.PY**: Dashboard KPI Cards, Chart Cards

### Mittlere Priorität (Phase 2-3)
5. **CRM.PY**: Kunden Cards, Detail Drawer, Timeline
6. **CONTROLLING_UI.PY**: Dashboard, Employee Cards, Export Drawer
7. **COMPONENTS/SHADCN_UI_INTEGRATION.PY**: Fehlende Komponenten ergänzen

### Niedrige Priorität (Phase 4+)
8. **ADMIN_PANEL.PY**: Vertical Tabs, Product Grid
9. **DOC_OUTPUT.PY**: PDF Preview, Share Drawer
10. **HEATPUMP_UI.PY**: Config Cards, Comparison Drawer
11. **OPTIONS.PY**: Settings Cards

---

## 9. Technische Anforderungen

### shadcn/ui Components
- **Bereits installiert**: `streamlit-shadcn-ui` in requirements.txt
- **Integration**: `components/shadcn_ui_integration.py` vorhanden
- **Fallback-Pattern**: Bereits implementiert

### CSS Framework
- **Tailwind CSS**: Für Styling (optional)
- **Custom CSS**: Via st.markdown (bereits verwendet)
- **Theme System**: `theme_manager.py` vorhanden

### Icons
- **Icon Library**: Lucide Icons (empfohlen für shadcn/ui)
- **Alternative**: Heroicons, Material Icons

### Responsive Design
- **Breakpoints**: Mobile < 768px, Tablet 768-1024px, Desktop > 1024px
- **CSS Grid**: Für flexible Layouts
- **Media Queries**: In `theming/responsive.css` (zu erstellen)

---

## 10. Nächste Schritte (Phase 2)

### shadcn/ui Komponenten erweitern
1. **Carousel implementieren**: carousel.py in components/
2. **Drawer implementieren**: drawer.py in components/
3. **Alert implementieren**: alert.py in components/
4. **Skeleton implementieren**: skeleton.py in components/
5. **Progress implementieren**: progress.py in components/

### Design-System definieren (Phase 3)
1. **Farb-Palette**: Primary, Secondary, Accent, Status Colors
2. **Typography Scale**: H1-H6, Body, Caption
3. **Spacing System**: Margins, Paddings (4px, 8px, 16px, 24px, 32px)
4. **Component Variants**: Button Sizes, Card Styles

### Dokumentation erstellen
- **Component Library**: Alle Komponenten mit Props + Examples
- **Usage Guide**: Best Practices für Entwickler
- **Demo Page**: Interactive Playground (`demo_ui_components.py`)

---

**Analyse-Status**: ABGESCHLOSSEN  
**Nächste Phase**: shadcn/ui Integration vorbereiten (Phase 2)
