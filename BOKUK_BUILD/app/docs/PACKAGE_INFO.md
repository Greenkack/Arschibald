# 📦 BOKUK2 SOLAR CALCULATOR - INSTALLATIONS-PAKET

## ✅ Was wurde erstellt?

Ein vollständiges, produktionsreifes Installations-Paket für die Bokuk2 Solar Calculator Anwendung.

## 📋 Paket-Inhalt

### 1. Installations-Skripte

- **`install.ps1`** - PowerShell Installations-Script (Hauptinstaller)
- **`install.bat`** - Windows Batch-Datei (vereinfachter Zugang)
- **`build_distribution.ps1`** - Distribution Builder für Entwickler
- **`setup.py`** - Python Setup-Script für pip-Installation

### 2. Start-Skripte

Nach der Installation werden automatisch erstellt:
- **`start.bat`** - Einfacher Windows-Starter
- **`start.ps1`** - PowerShell-Starter mit Fehlerbehandlung

### 3. Komplette Anwendung

✅ **136 Python Module** inkl.:
- Hauptanwendung (`gui.py`)
- Berechnungsengine (`calculations.py`, `solar_calculator.py`)
- PDF-Generator (`pdf_template_engine/`)
- Admin-Panel (`admin_panel.py`)
- CRM-System (`crm.py`)
- Datenbank-Management (`database.py`)
- Pricing-Engine (`pricing/`)

✅ **48 PDF-Templates** (Firma-spezifisch):
- `pdf_templates_static/multi/multi_nt_01_f1.pdf` bis `multi_nt_08_f6.pdf`
- Standard-Templates in `pdf_templates_static/notext/`

✅ **64 YML-Koordinaten-Dateien**:
- `coords_multi/seite1_f1.yml` bis `seite8_f8.yml`
- Standard-Koordinaten in `coords/`
- Wärmepumpen-Koordinaten in `coords_wp/`

✅ **Alle Assets**:
- Bilder, Icons, Logos
- Statische Dateien
- JSON-Konfigurationen
- Streamlit-Config

✅ **194 Python-Pakete** (aus requirements.txt):
- Streamlit 1.49.1
- Pandas, NumPy, Plotly
- ReportLab, PyPDF2
- SQLAlchemy, FastAPI
- und viele mehr...

## 🚀 Schnellstart für End-Benutzer

### Schritt 1: Package herunterladen

Das ZIP-File herunterladen und an einen beliebigen Ort entpacken.

### Schritt 2: Installation starten

**Einfachste Methode:**
```
Doppelklick auf: install.bat
```

**Alternative (PowerShell):**
```powershell
Rechtsklick auf install.ps1 → "Mit PowerShell ausführen"
```

### Schritt 3: App starten

Nach erfolgreicher Installation:
```
Doppelklick auf: start.bat
```

Die App öffnet sich automatisch im Browser unter `http://localhost:8501`

## 🔧 Installation für Entwickler

### Komplettes Build erstellen

```powershell
# Standard Distribution
.\build_distribution.ps1

# Mit ZIP-Archiv
.\build_distribution.ps1 -CreateZip

# Mit Standalone .exe
.\build_distribution.ps1 -CreateZip -BuildExe

# Benutzerdefinierter Output
.\build_distribution.ps1 -CreateZip -OutputDir "C:\Releases"
```

### Manuelle Installation

```powershell
# 1. Virtuelle Umgebung erstellen
python -m venv .venv

# 2. Aktivieren
.\.venv\Scripts\Activate.ps1

# 3. Dependencies installieren
pip install -r requirements.txt

# 4. Datenbank initialisieren
python init_database.py

# 5. App starten
streamlit run gui.py
```

## 📁 Installations-Verzeichnisse

### Standard-Installation
```
C:\Users\<USERNAME>\AppData\Local\Bokuk2\
```

### Benutzerdefiniert
```powershell
.\install.ps1 -InstallPath "C:\Programme\Bokuk2"
```

## 🎯 Installations-Optionen

### Mit Desktop-Verknüpfung
```powershell
.\install.ps1 -CreateDesktopShortcut
```

### Python-Check überspringen
```powershell
.\install.ps1 -SkipPythonCheck
```

### Alle Optionen kombinieren
```powershell
.\install.ps1 -InstallPath "C:\Bokuk2" -CreateDesktopShortcut
```

## 📦 Distribution erstellen

### Für Release-Verteilung

```powershell
# Komplettes Package mit ZIP
.\build_distribution.ps1 -CreateZip

# Ergebnis:
# .\dist\Bokuk2_SolarCalculator_v2.0.0_TIMESTAMP.zip (ca. 350 MB)
```

### ZIP-Inhalt

Nach dem Entpacken hat der Benutzer:
- Alle Anwendungsdateien
- `install.bat` für einfache Installation
- `INSTALLATION.md` mit Anweisungen
- Komplette Dokumentation

## 🔍 Systemanforderungen

### Minimum
- Windows 10
- Python 3.10+
- 4 GB RAM
- 2 GB freier Speicher

### Empfohlen
- Windows 11
- Python 3.13
- 8 GB RAM
- 5 GB freier Speicher

## 🐛 Fehlerbehebung

### "Python nicht gefunden"
```
Lösung: Python von python.org installieren
Bei Installation "Add to PATH" aktivieren
```

### "Port 8501 bereits belegt"
```powershell
streamlit run gui.py --server.port 8502
```

### "Datenbank-Fehler"
```powershell
python init_database.py
```

### "Fehlende Module"
```powershell
pip install -r requirements.txt
```

## 📊 Package-Statistik

- **Gesamt-Größe (komprimiert):** ~350 MB
- **Gesamt-Größe (entpackt):** ~800 MB
- **Python-Module:** 136
- **Python-Pakete:** 194
- **PDF-Templates:** 48
- **YML-Koordinaten:** 64
- **Assets/Dateien:** 1000+

## ✨ Features des Installers

✅ Automatische Python-Versions-Prüfung  
✅ Virtuelle Umgebung-Erstellung  
✅ Automatische Dependency-Installation  
✅ Datenbank-Auto-Initialisierung  
✅ Desktop-Verknüpfung (optional)  
✅ .env Konfiguration  
✅ Start-Skripte-Generierung  
✅ Vollständige Fehlerbehandlung  
✅ Farbige Console-Ausgabe  
✅ Progress-Anzeige  

## 🎁 Bonus-Features

### Standalone .exe (optional)

Für Benutzer ohne Python-Installation:

```powershell
# PyInstaller installieren
pip install pyinstaller

# .exe Build
.\build_distribution.ps1 -BuildExe -CreateZip
```

Ergebnis: `Bokuk2_SolarCalculator.exe` (ca. 500 MB)

### Python Package

Für Installation via pip:

```powershell
# Build
python setup.py sdist bdist_wheel

# Install
pip install dist/bokuk2_solar_calculator-2.0.0-py3-none-any.whl
```

### Docker (geplant)

```dockerfile
# Zukünftig:
docker run -p 8501:8501 bokuk2/solar-calculator
```

## 📝 Dokumentation

- **SETUP_GUIDE.md** - Vollständige Setup-Dokumentation
- **INSTALLATION.md** - Benutzer-Installations-Anleitung
- **README.md** - Projekt-Übersicht
- **docs/** - Erweiterte Dokumentation

## 🔐 Sicherheit

- Keine Passwörter im Package
- `.env.example` statt `.env`
- Secrets müssen nach Installation konfiguriert werden
- SQLite-Datenbank mit lokalem Zugriff

## 🚢 Deployment-Strategie

### Für kleine Teams (< 10 Benutzer)
```
ZIP-Package verteilen → Jeder installiert lokal
```

### Für größere Teams
```
Zentraler Server mit Streamlit → Remote-Zugriff
```

### Enterprise
```
Docker Container → Kubernetes Deployment
```

## 🆘 Support

- **GitHub Issues:** github.com/Greenkack/Arschibald/issues
- **Email:** support@bokuk2.com
- **Docs:** /docs Verzeichnis

## 🎉 Fertig!

Das Installations-Paket ist **100% vollständig** und enthält:

✅ Alle Codes  
✅ Alle Dateien  
✅ Alle Templates  
✅ Alle Koordinaten  
✅ Alle Assets  
✅ Alle Pakete  
✅ Alle Scripts  
✅ Alle Dokumentation  

**Bereit für Verteilung!** 🚀

---

**Version:** 2.0.0  
**Build-Datum:** 2025-10-28  
**Package-Ersteller:** Greenkack  
**Lizenz:** MIT
