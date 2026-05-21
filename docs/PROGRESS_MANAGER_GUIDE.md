# Progress Manager Integration Guide

## 🎯 Überblick

Das Progress Manager System ersetzt die Standard-Streamlit-Spinner durch professionelle, konfigurierbare Ladebalken im shadcn UI Design.

## 📁 Dateien

- `components/progress_manager.py` - Haupt-Progress-System
- `components/progress_settings.py` - UI für Einstellungen  
- `components/__init__.py` - Package-Initialisierung
- `components/progress_demo.py` - Demo & Tests

## 🚀 Verwendung

### Einfacher Progress Bar

```python
from components.progress_manager import create_progress_bar

progress_bar = create_progress_bar("Lade Daten...", st.container())

for i in range(0, 101, 20):
    progress_bar.update(i, f"Schritt {i//20 + 1}/5")
    time.sleep(0.5)

progress_bar.complete("Fertig!")
```

### Context Manager

```python
from components.progress_manager import ProgressContext

with ProgressContext("Verarbeite Daten...") as progress:
    for i in range(5):
        progress.update((i + 1) * 20, f"Schritt {i + 1}/5")
        # Ihre Berechnung hier
```

### Decorator

```python
from components.progress_manager import progress_decorator

@progress_decorator("Führe komplexe Berechnung durch...")
def complex_function():
    # Ihre Funktion hier
    return result
```

## 🎨 Design-Themes

5 verschiedene shadcn UI-kompatible Themes:

- **SHADCN_DEFAULT** - Standard Design
- **SHADCN_MINIMAL** - Minimalistisch
- **SHADCN_GRADIENT** - Mit Farbverläufen
- **SHADCN_ANIMATED** - Animierte Effekte
- **SHADCN_MODERN** - Modernes Design

### Theme ändern

```python
from components.progress_manager import set_progress_style, ProgressStyle

set_progress_style(ProgressStyle.SHADCN_GRADIENT)
```

## ⚙️ Konfiguration

### Farben anpassen

```python
from components.progress_manager import set_progress_colors

set_progress_colors(
    primary="#3b82f6",    # Hauptfarbe
    secondary="#10b981",  # Akzentfarbe  
    background="#f1f5f9"  # Hintergrund
)
```

### Globale Einstellungen

Über das Optionen-Menü in der App:

- Gehe zu "Optionen" → "🎨 Ladebalken Design"
- Wähle Theme und Farben
- Teste mit der Vorschau-Funktion

## 🔧 Bereits integriert in

- ✅ `analysis.py` - Berechnungsmodul
- ✅ `pdf_generator.py` - PDF-Erstellung
- ✅ `options.py` - Einstellungsmenü
- ✅ `gui.py` - Hauptanwendung

## 📱 Features

- **Responsive Design** - Passt sich automatisch an
- **Session State Management** - Einstellungen bleiben erhalten
- **Error Handling** - Graceful Fallbacks bei Fehlern
- **Customizable** - Vollständig anpassbar
- **Lightweight** - Minimale Performance-Auswirkung

## 🎯 Verwendungsbeispiele

### In Berechnungen

```python
def perform_calculations(data):
    progress_bar = create_progress_bar("Berechne...", st.container())
    
    progress_bar.update(20, "Lade Eingabedaten...")
    # Daten laden
    
    progress_bar.update(50, "Führe Hauptberechnungen durch...")
    # Berechnungen
    
    progress_bar.update(80, "Erstelle Ergebnisse...")
    # Ergebnisse formatieren
    
    progress_bar.complete("Berechnungen abgeschlossen!")
    return results
```

### In PDF-Generierung

```python
def create_pdf():
    progress_bar = create_progress_bar("Erstelle PDF...", st.container())
    
    progress_bar.update(25, "Initialisiere PDF-Document...")
    progress_bar.update(50, "Füge Inhalte hinzu...")
    progress_bar.update(75, "Erstelle finale Datei...")
    progress_bar.complete("PDF erfolgreich erstellt!")
```

## 🔄 Migration von st.spinner

**Alt:**

```python
with st.spinner("Lade..."):
    # Code hier
```

**Neu:**

```python
with ProgressContext("Lade...") as progress:
    # Code hier
    progress.update(50, "Halbzeit...")
```

## 🧪 Testen

Führe die Demo aus:

```bash
streamlit run components/progress_demo.py
```

## ⚠️ Fallback-Verhalten

Falls Abhängigkeiten fehlen, fällt das System automatisch auf `st.spinner` zurück:

- Keine Anwendungsfehler
- Grundfunktionalität bleibt erhalten
- Nahtlose User Experience

## 🎨 CSS-Anpassungen

Die CSS-Klassen folgen shadcn UI-Konventionen:

- `.progress-container` - Hauptcontainer
- `.progress-bar` - Balken-Element
- `.progress-text` - Text-Element
- `.progress-percentage` - Prozent-Anzeige

## 📈 Performance

- **Minimaler Overhead** (~1-2ms)
- **Lazy Loading** der CSS-Styles
- **Session State Caching** für Einstellungen
- **Optimierte DOM-Updates**

## 🐛 Troubleshooting

**Problem:** Progress Bar erscheint nicht
**Lösung:** Prüfe, ob Container korrekt übergeben wurde

**Problem:** Styles werden nicht angewendet
**Lösung:** Leere Browser-Cache und Session State

**Problem:** Import-Fehler
**Lösung:** Fallback-Implementierung wird automatisch verwendet

## 🔮 Roadmap

- [ ] Dark Mode Support
- [ ] Weitere Animation-Optionen
- [ ] Sound-Feedback (optional)
- [ ] Integration mit anderen UI-Libraries
- [ ] Performance-Metriken

---

*Erstellt für die Solar-App mit ❤️ und shadcn UI Design*
