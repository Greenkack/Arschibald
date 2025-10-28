# Bokuk2 Solar Calculator - Setup & Distribution Guide

## 🎯 Übersicht

Dieses Repository enthält alle notwendigen Tools, um die Bokuk2 Solar Calculator App für die Distribution vorzubereiten und zu installieren.

## 📦 Distribution erstellen

### Schnellstart

```powershell
# Komplettes Distribution-Package erstellen (mit ZIP)
.\build_distribution.ps1 -CreateZip

# Mit Standalone .exe (benötigt PyInstaller)
.\build_distribution.ps1 -CreateZip -BuildExe
```

### Was wird erstellt?

- **Bokuk2_SolarCalculator_Distribution/** - Komplettes Installations-Package
  - Alle Python-Dateien
  - Alle PDF-Templates und Koordinaten
  - Alle Assets und statischen Dateien
  - Installations-Skripte
  - Dokumentation

- **Bokuk2_SolarCalculator_v2.0.0_TIMESTAMP.zip** - Komprimiertes Package für Verteilung

## 🚀 Installation (für End-Benutzer)

### Methode 1: Automatische Installation (Empfohlen)

1. ZIP-Datei entpacken
2. Doppelklick auf `install.bat`
3. Anweisungen folgen
4. Nach Installation: Doppelklick auf `start.bat`

### Methode 2: Manuelle Installation

```powershell
# In PowerShell (als Administrator)
powershell -ExecutionPolicy Bypass -File install.ps1 -CreateDesktopShortcut
```

#### Installations-Optionen

```powershell
# Standard-Installation
.\install.ps1

# Mit Desktop-Verknüpfung
.\install.ps1 -CreateDesktopShortcut

# Benutzerdefinierter Pfad
.\install.ps1 -InstallPath "C:\Programme\Bokuk2"

# Python-Check überspringen (wenn Python sicher vorhanden)
.\install.ps1 -SkipPythonCheck
```

## 📋 Systemanforderungen

### Minimum

- **OS:** Windows 10 oder höher
- **Python:** 3.10 oder höher
- **RAM:** 4 GB
- **Festplatte:** 2 GB freier Speicher
- **Internet:** Für Installation erforderlich

### Empfohlen

- **OS:** Windows 11
- **Python:** 3.13
- **RAM:** 8 GB
- **Festplatte:** 5 GB freier Speicher
- **Browser:** Chrome, Firefox, oder Edge (neueste Version)

## 🔧 Build-Optionen

### Standard Distribution Build

```powershell
.\build_distribution.ps1
```

Erstellt ein komplettes Package im `dist/` Verzeichnis.

### Mit ZIP-Archiv

```powershell
.\build_distribution.ps1 -CreateZip
```

Erstellt zusätzlich ein ZIP-Archiv für einfache Verteilung.

### Mit Standalone .exe

```powershell
# PyInstaller installieren (falls noch nicht vorhanden)
pip install pyinstaller

# Build mit .exe
.\build_distribution.ps1 -CreateZip -BuildExe
```

Erstellt eine standalone .exe die ohne Python-Installation läuft.

### Benutzerdefiniertes Output-Verzeichnis

```powershell
.\build_distribution.ps1 -OutputDir "C:\Releases" -CreateZip
```

## 📁 Verzeichnisstruktur (Installation)

Nach der Installation:

```
C:\Users\<USERNAME>\AppData\Local\Bokuk2\
├── .venv\                          # Virtuelle Python-Umgebung
├── pdf_templates_static\           # PDF-Templates
│   ├── multi\                      # Multi-Firma Templates
│   └── notext\                     # Standard Templates
├── coords\                         # PDF-Koordinaten Standard
├── coords_multi\                   # PDF-Koordinaten Multi-Firma
├── coords_wp\                      # PDF-Koordinaten Wärmepumpen
├── assets\                         # Bilder, Icons
├── static\                         # Statische Dateien
├── json\                           # JSON-Konfigurationen
├── .streamlit\                     # Streamlit-Konfiguration
├── pricing\                        # Preis-Engine Module
├── pdf_template_engine\            # PDF-Generator
├── components\                     # UI-Komponenten
├── core\                           # Core-Funktionalität
├── utils\                          # Utilities
├── pages\                          # Streamlit Pages
├── widgets\                        # Custom Widgets
├── theming\                        # Theme-System
├── .env                            # Umgebungsvariablen
├── product_database.db             # SQLite Datenbank
├── start.bat                       # Windows Starter
├── start.ps1                       # PowerShell Starter
└── *.py                            # Python Module
```

## 🎮 Verwendung

### App starten

**Windows:**
```batch
REM Doppelklick oder im Terminal:
start.bat
```

**PowerShell:**
```powershell
.\start.ps1
```

**Manuell:**
```powershell
# Virtuelle Umgebung aktivieren
.\.venv\Scripts\Activate.ps1

# Streamlit starten
streamlit run gui.py
```

### App stoppen

- Im Terminal: `STRG + C`
- Browser-Tab schließen (App läuft weiter im Hintergrund)
- Für komplettes Beenden: Terminal schließen

## 🔍 Fehlerbehebung

### Port 8501 bereits belegt

```powershell
# Anderen Port verwenden
streamlit run gui.py --server.port 8502
```

### Python nicht gefunden

1. Python von https://www.python.org/downloads/ installieren
2. Bei Installation "Add to PATH" aktivieren
3. Terminal neu starten

### Datenbank-Fehler

```powershell
# Datenbank neu initialisieren
python init_database.py
```

### Fehlende Pakete

```powershell
# Virtuelle Umgebung aktivieren
.\.venv\Scripts\Activate.ps1

# Pakete neu installieren
pip install -r requirements.txt
```

### Template-Dateien fehlen

Stellen Sie sicher, dass alle Verzeichnisse kopiert wurden:
- `pdf_templates_static/`
- `coords/`
- `coords_multi/`
- `coords_wp/`

## 🏗️ Entwickler-Informationen

### Setup für Entwicklung

```powershell
# Repository klonen
git clone https://github.com/Greenkack/Arschibald.git
cd Arschibald

# Virtuelle Umgebung erstellen
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Dependencies installieren
pip install -r requirements.txt

# Datenbank initialisieren
python init_database.py

# Development Server starten
streamlit run gui.py
```

### Distribution für Entwickler

```powershell
# Vollständiger Build mit allen Optionen
.\build_distribution.ps1 -CreateZip -BuildExe -OutputDir ".\releases"
```

### Python Package erstellen

```powershell
# Build Package
python setup.py sdist bdist_wheel

# Installieren
pip install .
```

## 📝 Lizenz

MIT License - Siehe [LICENSE](LICENSE) für Details

## 🆘 Support

- **GitHub Issues:** https://github.com/Greenkack/Arschibald/issues
- **Email:** support@bokuk2.com
- **Dokumentation:** Siehe `/docs` Verzeichnis

## 🔄 Updates

### Für End-Benutzer

1. Alte Installation deinstallieren (Verzeichnis löschen)
2. Neue Version installieren
3. Datenbank wird automatisch migriert

### Für Entwickler

```powershell
git pull origin main
pip install -r requirements.txt
python init_database.py  # Falls Schema geändert wurde
```

## ✨ Features

- ✅ Automatische Installation
- ✅ Virtuelle Umgebung-Management
- ✅ Desktop-Verknüpfung (optional)
- ✅ Datenbank-Auto-Migration
- ✅ Komplette Fehlerbehandlung
- ✅ Standalone .exe möglich
- ✅ ZIP-Distribution
- ✅ Update-fähig

## 🎯 Roadmap

- [ ] Linux/Mac Support
- [ ] Docker Container
- [ ] Auto-Update Funktion
- [ ] Signierte .exe
- [ ] MSI Installer
- [ ] Portable Version (ohne Installation)

---

**Version:** 2.0.0  
**Letzte Aktualisierung:** 2025-10-28  
**Maintainer:** Greenkack
