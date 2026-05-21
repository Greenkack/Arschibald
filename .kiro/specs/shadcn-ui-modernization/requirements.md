# Requirements Document

## Introduction

Diese Spezifikation beschreibt die vollständige Modernisierung der Streamlit-Anwendung mit einem shadcn/ui-ähnlichen Design-System. Das Ziel ist es, die App in eine moderne, React-ähnliche Anwendung zu verwandeln, die alle Streamlit-Komponenten (Buttons, Slider, Cards, Charts, Inputs, etc.) mit einem konsistenten, professionellen Design ausstattet. Das System soll mehrere Themes unterstützen, zwischen denen live gewechselt werden kann, ohne die bestehende Funktionalität zu beeinträchtigen.

## Glossary

- **Streamlit App**: Die bestehende Solar-Kalkulationsanwendung (gui.py und alle Module)
- **shadcn/ui**: Ein modernes Design-System basierend auf Radix UI und Tailwind CSS
- **Theme System**: Ein Mechanismus zum Definieren und Wechseln von Farbschemata und Styles
- **CSS Injection**: Das Einbetten von Custom CSS via st.markdown() in Streamlit
- **streamlit-shadcn-ui**: Eine Python-Bibliothek, die shadcn/ui-Komponenten für Streamlit bereitstellt
- **Design Token**: Wiederverwendbare Design-Variablen (Farben, Abstände, Schriftarten)
- **Component Wrapper**: Python-Funktionen, die native Streamlit-Komponenten mit Custom-Styling umhüllen

## Requirements

### Requirement 1: Theme-System-Infrastruktur

**User Story:** Als Entwickler möchte ich ein zentrales Theme-System haben, damit ich konsistente Design-Tokens in der gesamten App verwenden kann.

#### Acceptance Criteria

1. WHEN die App startet, THEN THE Theme System SHALL ein Standard-Theme (shadcn-default) laden
2. THE Theme System SHALL mindestens 5 vordefinierte Themes bereitstellen (shadcn-default, shadcn-dark, shadcn-ocean, shadcn-forest, shadcn-sunset)
3. THE Theme System SHALL Design-Tokens für Farben, Typografie, Abstände, Schatten und Border-Radius definieren
4. THE Theme System SHALL eine Python-API bereitstellen, um Theme-Werte programmatisch abzurufen
5. WHERE ein Theme gewechselt wird, THE Theme System SHALL alle CSS-Variablen dynamisch aktualisieren

### Requirement 2: Live Theme-Wechsel

**User Story:** Als Benutzer möchte ich zwischen verschiedenen Themes wechseln können, damit ich das Design an meine Präferenzen anpassen kann.

#### Acceptance Criteria

1. THE App SHALL einen Theme-Selector in der Sidebar anzeigen
2. WHEN ein Benutzer ein Theme auswählt, THEN THE App SHALL das neue Theme sofort anwenden ohne Seiten-Reload
3. THE App SHALL die Theme-Auswahl im Session State speichern
4. THE App SHALL die Theme-Auswahl optional im Browser Local Storage persistieren
5. THE Theme Selector SHALL eine Live-Vorschau der Theme-Farben anzeigen

### Requirement 3: Basis-Komponenten-Styling

**User Story:** Als Entwickler möchte ich, dass alle Streamlit-Basis-Komponenten automatisch im shadcn/ui-Stil gerendert werden, damit die App ein konsistentes Erscheinungsbild hat.

#### Acceptance Criteria

1. THE App SHALL Custom CSS für st.button() mit shadcn/ui-Styling injizieren
2. THE App SHALL Custom CSS für st.text_input(), st.number_input(), st.text_area() mit shadcn/ui-Styling injizieren
3. THE App SHALL Custom CSS für st.selectbox(), st.multiselect() mit shadcn/ui-Styling injizieren
4. THE App SHALL Custom CSS für st.slider(), st.select_slider() mit shadcn/ui-Styling injizieren
5. THE App SHALL Custom CSS für st.checkbox(), st.radio(), st.toggle() mit shadcn/ui-Styling injizieren
6. THE App SHALL Custom CSS für st.tabs() mit shadcn/ui-Styling injizieren
7. THE App SHALL alle Hover-, Focus- und Active-States im shadcn/ui-Stil implementieren

### Requirement 4: Card-Komponenten

**User Story:** Als Entwickler möchte ich wiederverwendbare Card-Komponenten haben, damit ich Inhalte strukturiert und ansprechend darstellen kann.

#### Acceptance Criteria

1. THE App SHALL eine Card-Komponente mit Header, Body und Footer bereitstellen
2. THE Card Component SHALL verschiedene Varianten unterstützen (default, outlined, elevated)
3. THE Card Component SHALL optional ein Icon oder Badge im Header anzeigen
4. THE Card Component SHALL Hover-Effekte mit sanften Transitions haben
5. THE Card Component SHALL responsive sein und sich an verschiedene Bildschirmgrößen anpassen

### Requirement 5: Chart-Styling

**User Story:** Als Benutzer möchte ich, dass alle Diagramme im modernen shadcn/ui-Stil dargestellt werden, damit die Visualisierungen professionell aussehen.

#### Acceptance Criteria

1. THE App SHALL eine apply_chart_theme() Funktion bereitstellen, die Plotly-Charts styled
2. THE Chart Theme SHALL shadcn/ui-Farben für Linien, Balken und Flächen verwenden
3. THE Chart Theme SHALL moderne Schriftarten (Inter, system-ui) verwenden
4. THE Chart Theme SHALL Gradient-Fills für Area-Charts unterstützen
5. THE Chart Theme SHALL glatte Spline-Kurven statt eckiger Linien verwenden
6. THE Chart Theme SHALL responsive Margins und Padding haben
7. THE Chart Theme SHALL Dark-Mode-Unterstützung haben

### Requirement 6: Erweiterte Komponenten

**User Story:** Als Entwickler möchte ich Zugriff auf erweiterte shadcn/ui-Komponenten haben, damit ich komplexe UI-Patterns implementieren kann.

#### Acceptance Criteria

1. THE App SHALL eine Accordion-Komponente bereitstellen
2. THE App SHALL eine Alert/AlertDialog-Komponente bereitstellen
3. THE App SHALL eine Badge-Komponente bereitstellen
4. THE App SHALL eine Breadcrumb-Komponente bereitstellen
5. THE App SHALL eine Dropdown-Menu-Komponente bereitstellen
6. THE App SHALL eine Popover-Komponente bereitstellen
7. THE App SHALL eine Progress-Komponente bereitstellen
8. THE App SHALL eine Skeleton-Loader-Komponente bereitstellen
9. THE App SHALL eine Table-Komponente mit Sorting und Filtering bereitstellen
10. THE App SHALL eine Pagination-Komponente bereitstellen

### Requirement 7: Sidebar und Navigation

**User Story:** Als Benutzer möchte ich eine moderne, übersichtliche Sidebar-Navigation haben, damit ich schnell zwischen verschiedenen Bereichen der App wechseln kann.

#### Acceptance Criteria

1. THE Sidebar SHALL im shadcn/ui-Stil gestyled sein
2. THE Sidebar SHALL Menü-Gruppen mit Überschriften unterstützen
3. THE Sidebar SHALL Icons für Menü-Einträge anzeigen
4. THE Sidebar SHALL den aktiven Menü-Eintrag visuell hervorheben
5. THE Sidebar SHALL Hover-Effekte für Menü-Einträge haben
6. THE Sidebar SHALL optional kollabierbar sein

### Requirement 8: Formular-Komponenten

**User Story:** Als Entwickler möchte ich moderne Formular-Komponenten haben, damit Benutzereingaben intuitiv und ansprechend sind.

#### Acceptance Criteria

1. THE App SHALL Input-Felder mit Floating Labels unterstützen
2. THE App SHALL Input-Validierung mit visuellen Feedback (Fehler/Erfolg) anzeigen
3. THE App SHALL Input-Felder mit Icons (Prefix/Suffix) unterstützen
4. THE App SHALL eine DatePicker-Komponente im shadcn/ui-Stil bereitstellen
5. THE App SHALL eine Calendar-Komponente bereitstellen
6. THE App SHALL eine Input-OTP-Komponente für Code-Eingaben bereitstellen

### Requirement 9: Tabellen und Daten-Anzeige

**User Story:** Als Benutzer möchte ich Daten in modernen, interaktiven Tabellen sehen, damit ich Informationen schnell erfassen und filtern kann.

#### Acceptance Criteria

1. THE App SHALL st.dataframe() mit shadcn/ui-Styling überschreiben
2. THE Table Component SHALL Zebra-Striping (alternierende Zeilen-Farben) haben
3. THE Table Component SHALL Hover-Effekte für Zeilen haben
4. THE Table Component SHALL sortierbare Spalten-Header haben
5. THE Table Component SHALL responsive sein und horizontal scrollen bei Bedarf

### Requirement 10: Metriken und KPIs

**User Story:** Als Benutzer möchte ich wichtige Kennzahlen in ansprechenden Metric-Cards sehen, damit ich schnell einen Überblick über wichtige Werte bekomme.

#### Acceptance Criteria

1. THE App SHALL eine MetricCard-Komponente bereitstellen
2. THE MetricCard SHALL Wert, Label, Trend-Indikator und optionales Icon anzeigen
3. THE MetricCard SHALL Trend-Änderungen farblich hervorheben (grün/rot)
4. THE MetricCard SHALL verschiedene Größen unterstützen (small, medium, large)
5. THE MetricCard SHALL animierte Wert-Änderungen unterstützen

### Requirement 11: Animations und Transitions

**User Story:** Als Benutzer möchte ich sanfte Animationen und Übergänge sehen, damit die App sich flüssig und modern anfühlt.

#### Acceptance Criteria

1. THE App SHALL CSS-Transitions für alle interaktiven Elemente definieren (200-300ms)
2. THE App SHALL Fade-In-Animationen für neu geladene Inhalte verwenden
3. THE App SHALL Slide-Animationen für Sidebar und Drawer verwenden
4. THE App SHALL Skeleton-Loader während Lade-Vorgängen anzeigen
5. THE App SHALL keine ruckartigen Layout-Shifts haben

### Requirement 12: Responsive Design

**User Story:** Als Benutzer möchte ich die App auf verschiedenen Geräten nutzen können, damit sie auf Desktop, Tablet und Mobile gut aussieht.

#### Acceptance Criteria

1. THE App SHALL Media Queries für Breakpoints (mobile, tablet, desktop) definieren
2. THE App SHALL auf mobilen Geräten eine kollabierbare Sidebar haben
3. THE App SHALL auf mobilen Geräten gestapelte Layouts statt Spalten verwenden
4. THE App SHALL Touch-freundliche Buttons und Inputs haben (min. 44px Höhe)
5. THE App SHALL horizontales Scrollen vermeiden auf allen Bildschirmgrößen

### Requirement 13: Dark Mode

**User Story:** Als Benutzer möchte ich zwischen Light und Dark Mode wechseln können, damit ich die App in verschiedenen Lichtverhältnissen komfortabel nutzen kann.

#### Acceptance Criteria

1. THE App SHALL einen Dark-Mode-Toggle in der Sidebar bereitstellen
2. WHEN Dark Mode aktiviert wird, THEN THE App SHALL alle Farben invertieren
3. THE Dark Mode SHALL ausreichend Kontrast für Lesbarkeit haben (WCAG AA)
4. THE Dark Mode SHALL die Präferenz im Session State speichern
5. THE Dark Mode SHALL optional die System-Präferenz des Browsers erkennen

### Requirement 14: Komponenten-Bibliothek Integration

**User Story:** Als Entwickler möchte ich die streamlit-shadcn-ui-Bibliothek vollständig integrieren, damit ich alle verfügbaren Komponenten nutzen kann.

#### Acceptance Criteria

1. THE App SHALL alle Komponenten von <https://shadcn.streamlit.app/> importieren
2. THE App SHALL Wrapper-Funktionen für jede shadcn-Komponente bereitstellen
3. THE App SHALL Beispiele und Dokumentation für jede Komponente haben
4. THE App SHALL die Komponenten in einem Demo-Bereich zeigen
5. THE App SHALL Fallbacks für Komponenten haben, falls die Bibliothek nicht verfügbar ist

### Requirement 15: Performance und Kompatibilität

**User Story:** Als Benutzer möchte ich, dass die App trotz des neuen Designs schnell lädt und funktioniert, damit die Benutzererfahrung nicht beeinträchtigt wird.

#### Acceptance Criteria

1. THE App SHALL CSS nur einmal beim App-Start injizieren
2. THE App SHALL CSS-Variablen statt Inline-Styles verwenden wo möglich
3. THE App SHALL keine bestehenden Funktionen durch das neue Design brechen
4. THE App SHALL in allen modernen Browsern (Chrome, Firefox, Safari, Edge) funktionieren
5. THE App SHALL eine Ladezeit von unter 3 Sekunden haben

### Requirement 16: Theme-Generator-Tool

**User Story:** Als Administrator möchte ich ein Tool haben, das automatisch mehrere Theme-Varianten generiert, damit ich schnell neue Designs erstellen kann.

#### Acceptance Criteria

1. THE App SHALL ein Skript theme_generator.py bereitstellen
2. THE Theme Generator SHALL aus einer Basis-Farbe ein vollständiges Theme generieren
3. THE Theme Generator SHALL Komplementär- und Akzentfarben automatisch berechnen
4. THE Theme Generator SHALL Theme-Dateien im JSON-Format exportieren
5. THE Theme Generator SHALL eine Vorschau des generierten Themes anzeigen

### Requirement 17: Dokumentation und Beispiele

**User Story:** Als Entwickler möchte ich umfassende Dokumentation und Beispiele haben, damit ich das neue Design-System effektiv nutzen kann.

#### Acceptance Criteria

1. THE App SHALL eine Design-System-Dokumentation in docs/SHADCN_UI_GUIDE.md haben
2. THE Documentation SHALL alle verfügbaren Komponenten auflisten
3. THE Documentation SHALL Code-Beispiele für jede Komponente enthalten
4. THE Documentation SHALL Best Practices für das Styling beschreiben
5. THE App SHALL eine Demo-Seite mit allen Komponenten haben

### Requirement 18: Rückwärtskompatibilität

**User Story:** Als Entwickler möchte ich, dass bestehender Code weiterhin funktioniert, damit ich nicht alle Module sofort anpassen muss.

#### Acceptance Criteria

1. THE App SHALL bestehende Streamlit-Komponenten nicht brechen
2. THE App SHALL ein Feature-Flag für das neue Design haben (enable_shadcn_ui)
3. WHERE das Feature-Flag deaktiviert ist, THE App SHALL im Original-Design laufen
4. THE App SHALL schrittweise Migration einzelner Module ermöglichen
5. THE App SHALL keine Breaking Changes in bestehenden APIs einführen

### Requirement 19: Error Handling und Robustheit

**User Story:** Als Benutzer möchte ich, dass die App auch bei Fehlern stabil läuft, damit meine Arbeit nicht unterbrochen wird.

#### Acceptance Criteria

1. WHEN ein Theme nicht geladen werden kann, THEN THE App SHALL ein Fallback-Theme verwenden
2. WHEN CSS-Injection fehlschlägt, THEN THE App SHALL mit Standard-Streamlit-Styling weiterlaufen
3. WHEN eine Komponente einen Fehler wirft, THEN THE App SHALL auf native Streamlit-Komponente zurückfallen
4. THE App SHALL alle Fehler im Theme-System loggen
5. THE App SHALL Benutzer über nicht-kritische Fehler mit st.warning() informieren
6. THE App SHALL bei kritischen Fehlern eine Fehlerseite mit Recovery-Optionen anzeigen
7. THE App SHALL automatische Error-Recovery-Mechanismen haben

### Requirement 20: Logging und Monitoring

**User Story:** Als Administrator möchte ich detaillierte Logs über Theme-Wechsel und Komponenten-Nutzung haben, damit ich Probleme diagnostizieren kann.

#### Acceptance Criteria

1. THE App SHALL alle Theme-Wechsel mit Timestamp loggen
2. THE App SHALL CSS-Injection-Ereignisse loggen
3. THE App SHALL Komponenten-Rendering-Fehler mit Stack-Trace loggen
4. THE App SHALL Performance-Metriken für CSS-Generierung loggen
5. THE App SHALL ein Dashboard für Theme-System-Statistiken bereitstellen
6. THE App SHALL Log-Level konfigurierbar machen (DEBUG, INFO, WARNING, ERROR)

### Requirement 21: Caching und Performance

**User Story:** Als Benutzer möchte ich, dass die App schnell lädt und reagiert, damit ich effizient arbeiten kann.

#### Acceptance Criteria

1. THE App SHALL generiertes CSS cachen und nur bei Theme-Wechsel neu generieren
2. THE App SHALL Theme-JSON-Dateien beim Start einmalig laden und cachen
3. THE App SHALL Komponenten-Rendering mit @st.cache_data optimieren wo möglich
4. THE App SHALL CSS-Minification für Produktion unterstützen
5. THE App SHALL lazy Loading für nicht-sichtbare Komponenten implementieren
6. THE App SHALL Performance-Budgets definieren (CSS < 50KB, Render < 100ms)

### Requirement 22: Accessibility (A11y)

**User Story:** Als Benutzer mit Einschränkungen möchte ich die App barrierefrei nutzen können, damit ich alle Funktionen zugänglich habe.

#### Acceptance Criteria

1. THE App SHALL WCAG 2.1 Level AA Kontrast-Anforderungen erfüllen
2. THE App SHALL Keyboard-Navigation für alle interaktiven Elemente unterstützen
3. THE App SHALL ARIA-Labels für alle Komponenten bereitstellen
4. THE App SHALL Focus-Indikatoren für Keyboard-Navigation haben
5. THE App SHALL Screen-Reader-freundliche Komponenten haben
6. THE App SHALL Farbblindheit-freundliche Farbpaletten anbieten
7. THE App SHALL Text-Skalierung bis 200% ohne Layout-Bruch unterstützen

### Requirement 23: Internationalisierung (i18n)

**User Story:** Als internationaler Benutzer möchte ich die UI in meiner Sprache sehen, damit ich die App besser verstehen kann.

#### Acceptance Criteria

1. THE App SHALL Theme-Namen und Beschreibungen in mehreren Sprachen unterstützen
2. THE App SHALL Komponenten-Labels übersetzbar machen
3. THE App SHALL RTL (Right-to-Left) Layouts für arabische/hebräische Sprachen unterstützen
4. THE App SHALL Datums- und Zahlenformate lokalisieren
5. THE App SHALL mindestens Deutsch und Englisch unterstützen

### Requirement 24: Theme-Validierung

**User Story:** Als Administrator möchte ich, dass Theme-Dateien validiert werden, damit fehlerhafte Themes die App nicht brechen.

#### Acceptance Criteria

1. THE App SHALL Theme-JSON-Dateien gegen ein Schema validieren
2. WHEN ein Theme ungültig ist, THEN THE App SHALL detaillierte Validierungs-Fehler anzeigen
3. THE App SHALL fehlende Theme-Eigenschaften mit Defaults auffüllen
4. THE App SHALL Theme-Farben auf gültige Hex/RGB-Werte prüfen
5. THE App SHALL ein CLI-Tool zur Theme-Validierung bereitstellen

### Requirement 25: Hot Reload für Theme-Entwicklung

**User Story:** Als Theme-Designer möchte ich Änderungen an Themes sofort sehen, damit ich schnell iterieren kann.

#### Acceptance Criteria

1. THE App SHALL Theme-Dateien auf Änderungen überwachen (File Watcher)
2. WHEN eine Theme-Datei geändert wird, THEN THE App SHALL das Theme automatisch neu laden
3. THE App SHALL einen Development-Mode mit Hot Reload haben
4. THE App SHALL Theme-Änderungen ohne vollständigen App-Reload anwenden
5. THE App SHALL Validierungs-Fehler in Echtzeit anzeigen

### Requirement 26: Component Library Showcase

**User Story:** Als Entwickler möchte ich eine interaktive Showcase-Seite haben, damit ich alle Komponenten und ihre Varianten sehen kann.

#### Acceptance Criteria

1. THE App SHALL eine dedizierte Showcase-Seite für alle Komponenten haben
2. THE Showcase SHALL Code-Beispiele für jede Komponente anzeigen
3. THE Showcase SHALL interaktive Props-Editor für Komponenten haben
4. THE Showcase SHALL Copy-to-Clipboard für Code-Beispiele unterstützen
5. THE Showcase SHALL alle Komponenten in allen Themes zeigen
6. THE Showcase SHALL Responsive-Vorschau für verschiedene Bildschirmgrößen haben

### Requirement 27: CSS-in-JS Alternative

**User Story:** Als Entwickler möchte ich Komponenten mit Python-Dictionaries stylen können, damit ich kein CSS schreiben muss.

#### Acceptance Criteria

1. THE App SHALL eine style() Funktion bereitstellen, die Python-Dicts in CSS konvertiert
2. THE App SHALL Tailwind-ähnliche Utility-Funktionen bereitstellen (z.B. px(), py(), bg())
3. THE App SHALL Style-Composition unterstützen (Merging von Style-Dicts)
4. THE App SHALL Auto-Completion für Style-Properties in IDEs ermöglichen
5. THE App SHALL Type-Hints für alle Style-Funktionen haben

### Requirement 28: Theme-Presets für Branchen

**User Story:** Als Benutzer möchte ich branchenspezifische Theme-Presets haben, damit die App zu meinem Geschäftsbereich passt.

#### Acceptance Criteria

1. THE App SHALL Theme-Presets für verschiedene Branchen bereitstellen (Solar, Finance, Healthcare, etc.)
2. THE App SHALL Theme-Kategorien im Theme-Selector anzeigen
3. THE App SHALL Theme-Vorschau-Bilder für jeden Preset haben
4. THE App SHALL Custom-Themes basierend auf Presets erstellen können
5. THE App SHALL mindestens 10 verschiedene Theme-Presets haben

### Requirement 29: Export und Sharing

**User Story:** Als Administrator möchte ich Themes exportieren und mit anderen teilen können, damit Teams konsistente Designs verwenden.

#### Acceptance Criteria

1. THE App SHALL Themes als JSON-Datei exportieren können
2. THE App SHALL Themes als CSS-Datei exportieren können
3. THE App SHALL Theme-Import aus Datei unterstützen
4. THE App SHALL Theme-Sharing via URL unterstützen
5. THE App SHALL Theme-Versionierung unterstützen

### Requirement 30: Advanced Customization

**User Story:** Als Power-User möchte ich erweiterte Anpassungsmöglichkeiten haben, damit ich das Design perfekt auf meine Bedürfnisse abstimmen kann.

#### Acceptance Criteria

1. THE App SHALL Custom CSS-Injection für einzelne Komponenten erlauben
2. THE App SHALL CSS-Variablen-Override auf Komponenten-Ebene unterstützen
3. THE App SHALL Custom-Fonts via URL oder Upload unterstützen
4. THE App SHALL Gradient-Editor für Hintergründe bereitstellen
5. THE App SHALL Animation-Timing-Anpassungen erlauben

### Requirement 31: State Management

**User Story:** Als Entwickler möchte ich ein robustes State-Management für Theme-Einstellungen haben, damit Präferenzen zuverlässig gespeichert werden.

#### Acceptance Criteria

1. THE App SHALL Theme-Einstellungen in Session State speichern
2. THE App SHALL Theme-Einstellungen in Browser Local Storage persistieren
3. THE App SHALL Theme-Einstellungen in Datenbank speichern können (optional)
4. THE App SHALL Theme-Einstellungen pro Benutzer verwalten
5. THE App SHALL Theme-Einstellungen synchronisieren zwischen Tabs

### Requirement 32: Testing Infrastructure

**User Story:** Als Entwickler möchte ich umfassende Tests für das Theme-System haben, damit Änderungen keine Regressionen verursachen.

#### Acceptance Criteria

1. THE App SHALL Unit-Tests für alle Theme-System-Komponenten haben
2. THE App SHALL Integration-Tests für Theme-Wechsel haben
3. THE App SHALL Visual-Regression-Tests für alle Komponenten haben
4. THE App SHALL Performance-Tests für CSS-Generierung haben
5. THE App SHALL Test-Coverage von mindestens 80% haben
6. THE App SHALL automatisierte Tests in CI/CD-Pipeline integrieren

### Requirement 33: Documentation und Onboarding

**User Story:** Als neuer Entwickler möchte ich schnell verstehen, wie das Theme-System funktioniert, damit ich produktiv arbeiten kann.

#### Acceptance Criteria

1. THE App SHALL ein interaktives Tutorial für Theme-Erstellung haben
2. THE App SHALL API-Dokumentation mit Beispielen haben
3. THE App SHALL Video-Tutorials für häufige Aufgaben haben
4. THE App SHALL einen Migration-Guide von Standard-Streamlit haben
5. THE App SHALL Best-Practices-Dokumentation haben
6. THE App SHALL Troubleshooting-Guide haben

### Requirement 34: Security

**User Story:** Als Administrator möchte ich, dass Theme-Uploads sicher sind, damit keine schädlichen Inhalte injiziert werden.

#### Acceptance Criteria

1. THE App SHALL Theme-JSON-Dateien auf schädliche Inhalte prüfen
2. THE App SHALL CSS-Injection gegen XSS-Angriffe absichern
3. THE App SHALL Theme-Uploads nur für autorisierte Benutzer erlauben
4. THE App SHALL Theme-Dateien in isoliertem Verzeichnis speichern
5. THE App SHALL Content-Security-Policy für Custom-CSS implementieren

### Requirement 35: Analytics und Insights

**User Story:** Als Product Owner möchte ich verstehen, welche Themes und Komponenten am meisten genutzt werden, damit ich Prioritäten setzen kann.

#### Acceptance Criteria

1. THE App SHALL Theme-Nutzungs-Statistiken sammeln
2. THE App SHALL Komponenten-Nutzungs-Statistiken sammeln
3. THE App SHALL Performance-Metriken pro Theme sammeln
4. THE App SHALL Analytics-Dashboard bereitstellen
5. THE App SHALL Daten-Export für externe Analyse unterstützen
6. THE App SHALL Privacy-konforme Analytics implementieren (DSGVO)
