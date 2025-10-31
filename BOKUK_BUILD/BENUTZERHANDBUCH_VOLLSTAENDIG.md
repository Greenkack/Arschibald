# 🚀 ÖMER'S CALCULATOR - VOLLSTÄNDIGES SETUP SYSTEM

## ✅ Was ist enthalten?

Diese Setup.exe ist ein **100% vollständiges, eigenständiges Installationssystem** mit:

### 🐍 Python Environment

- **Python 3.11.9 Embedded** (vollständig integriert)
- **Keine separate Python-Installation nötig**
- **252 Wheel-Dateien** (~536 MB) - Alle Dependencies offline

### 📦 Alle Python-Pakete (194 Pakete)

```
✅ streamlit 1.49.1          - Web-Framework
✅ pandas 2.3.2              - Datenanalyse
✅ numpy 2.3.2               - Numerische Berechnungen
✅ plotly 6.3.0              - Interaktive Charts
✅ altair 5.5.0              - Deklarative Visualisierungen
✅ sqlalchemy 2.0.43         - Datenbank-ORM
✅ alembic 1.16.5            - Datenbank-Migrationen
✅ PyMuPDF 1.26.4            - PDF-Verarbeitung
✅ reportlab 4.4.3           - PDF-Generierung
✅ openpyxl 3.1.5            - Excel-Support
✅ Pillow 11.3.0             - Bildverarbeitung
✅ matplotlib 3.10.6         - Plotting
✅ scipy 1.16.1              - Wissenschaftliche Berechnungen
✅ scikit-learn 1.7.1        - Machine Learning
✅ cryptography 45.0.7       - Verschlüsselung
✅ langchain 0.3.27          - AI Agent Framework
✅ faiss-cpu 1.10.0          - Vektor-Suche
✅ + 177 weitere Pakete
```

### 🎯 Vollständige App (~884 MB)

- **Alle .py Dateien** - Kompletter Quellcode
- **Core-Module (Phase 1-12)** - 31 integrierte Module:
  - Config-System (3 Module)
  - Logging-System (2 Module)
  - Cache-System (4 Module)
  - Session-Management (3 Module)
  - Datenbank-System (5 Module)
  - Security & Router (2 Module)
  - Forms & Widgets (2 Module)
  - Navigation & Jobs (2 Module)
  - Migrations (2 Module)
  - Cache-Extensions (3 Module)
  - DB-Extensions (2 Module)

- **Agent-System** - KI-Assistent mit Tools
- **PDF-System** - Erweiterte Generierung (8-seitige PDFs)
- **Chart-System** - 55+ Diagrammtypen
- **CRM-System** - Kundenverwaltung
- **Excel-Integration** - Import/Export
- **Multi-Firma Support** - 8 Firmenkonfigurationen

### 📊 Datenbanken & Daten

```
data/
├── app_data.db           - Hauptdatenbank
├── users.db              - Benutzerverwaltung
├── crm_database.db       - CRM-Daten
└── product_database.db   - Produktkatalog
```

### 🎨 Assets & Ressourcen

```
assets/
├── Kakerlack.ico         - App-Icon
├── logos/                - Firmenlogos
└── images/               - UI-Bilder

pdf_templates_static/
├── multi/                - PDF-Templates (48 Dateien)
│   ├── Firma 1-8 Templates
│   └── Koordinaten-Dateien
└── notext/               - Blanko-Templates

coords/                   - Koordinaten für PDFs
coords_multi/             - Multi-Firma Koordinaten
theming/                  - UI-Themes
```

### ⚙️ Konfigurationen

```
.streamlit/
└── config.toml           - Streamlit-Einstellungen

.env                      - Environment-Variablen
requirements.txt          - Package-Liste
```

---

## 📥 INSTALLATION

### Systemanforderungen

- **Betriebssystem:** Windows 10/11 (64-bit)
- **RAM:** Mindestens 4 GB (empfohlen: 8 GB+)
- **Festplatte:** ~3 GB freier Speicher
- **Prozessor:** Intel/AMD x64
- **Browser:** Chrome, Firefox oder Edge
- **Rechte:** Administrator

### Schritt-für-Schritt Installation

#### 1️⃣ Setup starten

```
Doppelklick auf: OemersCalculator_Complete_Setup_v2.0.0.exe
```

#### 2️⃣ Installationsassistent

1. **Willkommen** → Weiter
2. **Zielordner wählen:**
   - Standard: `C:\Program Files\OemersCalculatorAllInOne`
   - Oder eigenen Pfad wählen
3. **Administrator-Rechte** bestätigen (UAC-Dialog)
4. **Installation** → Warten Sie ~2-5 Minuten
   - Dateien werden kopiert (~2 GB)
   - Python wird entpackt
   - Pakete werden installiert

#### 3️⃣ Automatische Paket-Installation

Der Installer führt automatisch aus:

```powershell
install.ps1
├── Entpacke python-embed.zip
├── Konfiguriere Python-Paths
├── Installiere pip
└── Installiere alle 194 Pakete aus wheelhouse (offline)
```

**Dauer:** ~5-10 Minuten (je nach System)

#### 4️⃣ Abschluss

- ✅ Desktop-Verknüpfung: "Ömer's Calculator All in One"
- ✅ Startmenü-Eintrag
- ✅ Uninstaller registriert

---

## 🚀 APP STARTEN

### Methode 1: Desktop-Icon (empfohlen)

```
Doppelklick auf: Ömer's Calculator All in One
```

### Methode 2: Startmenü

```
Start → Ömer's Calculator → Ömer's Calculator All in One
```

### Methode 3: Kommandozeile

```powershell
cd "C:\Program Files\OemersCalculatorAllInOne"
.\run_app_embed.cmd
```

### Methode 4: PowerShell

```powershell
cd "C:\Program Files\OemersCalculatorAllInOne"
powershell -ExecutionPolicy Bypass -File .\run_app_embed.ps1
```

---

## 🌐 BROWSER-ZUGRIFF

Nach dem Start:

1. **Terminal-Fenster öffnet sich** (nicht schließen!)
2. **Browser öffnet automatisch:** `http://localhost:8501`
3. **Falls nicht:**
   - Manuell öffnen: `http://localhost:8501`
   - Port ändern in `run_app_embed.ps1` falls belegt

---

## 🔧 PROBLEMBEHANDLUNG

### ❌ Problem: "Python nicht gefunden"

**Ursache:** Installation wurde nicht abgeschlossen

**Lösung:**

```powershell
cd "C:\Program Files\OemersCalculatorAllInOne"
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

---

### ❌ Problem: "Streamlit nicht gefunden"

**Ursache:** Pakete nicht installiert

**Lösung:**

```powershell
cd "C:\Program Files\OemersCalculatorAllInOne"
.\python_embed\python.exe -m pip install --no-index --find-links=wheelhouse streamlit
```

---

### ❌ Problem: "Port 8501 bereits belegt"

**Ursache:** Andere App nutzt Port

**Lösung:**
Öffne `run_app_embed.ps1` und ändere:

```powershell
# Von:
--server.port=8501

# Zu:
--server.port=8502
```

---

### ❌ Problem: "Modul XYZ nicht gefunden"

**Ursache:** Einzelnes Paket fehlt

**Lösung:**

```powershell
cd "C:\Program Files\OemersCalculatorAllInOne"
.\python_embed\python.exe -m pip install --no-index --find-links=wheelhouse <package-name>
```

---

### ❌ Problem: "Datenbank-Fehler"

**Ursache:** Datenbank beschädigt oder fehlt

**Lösung:**

```powershell
cd "C:\Program Files\OemersCalculatorAllInOne\app"
..\python_embed\python.exe init_database.py
```

---

### ❌ Problem: Administrator-Rechte fehlen

**Lösung:**

1. Rechtsklick auf `run_app_embed.cmd`
2. "Als Administrator ausführen"

---

## 🛠️ ERWEITERTE KONFIGURATION

### Python-Pakete hinzufügen

```powershell
cd "C:\Program Files\OemersCalculatorAllInOne"
.\python_embed\python.exe -m pip install <package-name>
```

### Logs einsehen

```
C:\Program Files\OemersCalculatorAllInOne\
├── install.log           - Installations-Log
└── app\logs\             - App-Logs
    ├── app_YYYYMMDD.log
    └── errors_YYYYMMDD.log
```

### Streamlit-Config anpassen

```toml
# C:\Program Files\OemersCalculatorAllInOne\app\.streamlit\config.toml

[server]
port = 8501
address = "localhost"
headless = true

[theme]
primaryColor = "#FF4B4B"
```

### Datenbank-Backup

```powershell
# Backup erstellen
Copy-Item "C:\Program Files\OemersCalculatorAllInOne\app\data\*.db" "C:\Backup\"

# Restore
Copy-Item "C:\Backup\*.db" "C:\Program Files\OemersCalculatorAllInOne\app\data\"
```

---

## 🗑️ DEINSTALLATION

### Methode 1: Windows-Einstellungen

1. **Windows-Einstellungen** → Apps
2. Suche: "Ömer's Calculator All in One"
3. Klick → **Deinstallieren**

### Methode 2: Startmenü

1. **Start** → Ömer's Calculator
2. **Deinstallieren** → Folge Anweisungen

### Methode 3: Uninstaller direkt

```
C:\Program Files\OemersCalculatorAllInOne\unins000.exe
```

**Hinweis:** User-Daten in `%APPDATA%` bleiben erhalten (optional löschen)

---

## 📦 INHALT DES INSTALLATIONSORDNERS

```
C:\Program Files\OemersCalculatorAllInOne\
│
├── 📁 app\                          (~884 MB - Vollständige App)
│   ├── gui.py                      - Hauptdatei
│   ├── core\                       - 31 Core-Module
│   ├── Agent\                      - KI-Agent System
│   ├── data\                       - Datenbanken
│   ├── assets\                     - Icons, Bilder
│   ├── pdf_templates_static\       - PDF-Templates
│   ├── coords\                     - Koordinaten
│   ├── .streamlit\                 - Streamlit-Config
│   ├── requirements.txt
│   └── ... (alle anderen Dateien)
│
├── 📁 python_embed\                 (~1.2 GB - Python 3.11.9)
│   ├── python.exe
│   ├── python311.dll
│   ├── Lib\
│   ├── site-packages\              - Installierte Pakete
│   └── Scripts\
│
├── 📁 wheelhouse\                   (~536 MB - 252 Wheels)
│   ├── streamlit-1.49.1-*.whl
│   ├── pandas-2.3.2-*.whl
│   ├── numpy-2.3.2-*.whl
│   └── ... (249 weitere)
│
├── 📄 python-embed.zip              (~25 MB - Backup)
├── 📄 install.ps1                  - Installations-Script
├── 📄 install.bat                  - Batch-Wrapper
├── 📄 run_app_embed.ps1            - Start-Script (PowerShell)
├── 📄 run_app_embed.cmd            - Start-Script (Batch)
├── 📄 install.log                  - Installations-Log
└── 📄 unins000.exe                 - Deinstaller
```

**Gesamt:** ~2.6 GB nach Installation

---

## 🎓 FEATURES ÜBERBLICK

### Core-System (Phase 1-12)

- ✅ **Config-System** - Zentrale Konfiguration
- ✅ **Logging-System** - Strukturiertes Logging
- ✅ **Cache-System** - Performance-Optimierung
- ✅ **Session-Management** - User-Sessions
- ✅ **Datenbank-System** - SQLAlchemy + Migrations
- ✅ **Security** - Authentifizierung & Autorisierung
- ✅ **Router** - Page-Navigation
- ✅ **Forms & Widgets** - UI-Komponenten
- ✅ **Jobs** - Background-Tasks
- ✅ **Migrations** - Alembic-Integration
- ✅ **Cache-Extensions** - Invalidation, Monitoring, Warming
- ✅ **DB-Extensions** - Performance-Monitor, Query-Builder

### Hauptfunktionen

- 🔢 **Solarrechner** - PV-Anlagen Berechnung
- 💰 **Kostenanalyse** - ROI, Amortisation
- 📊 **55+ Charts** - Plotly, Altair, Matplotlib
- 📄 **PDF-Export** - 8-seitige Angebote
- 👥 **CRM-System** - Kundenverwaltung
- 📈 **Finanzierung** - Kredit-Rechner
- 🏢 **Multi-Firma** - 8 Firmenkonfigurationen
- 🤖 **KI-Agent** - Automatisierung

---

## 📞 SUPPORT

### Dokumentation

- **Haupt-Repo:** <https://github.com/Greenkack/Arschibald>
- **Issues:** <https://github.com/Greenkack/Arschibald/issues>
- **Releases:** <https://github.com/Greenkack/Arschibald/releases>

### Logs für Support anfragen

```powershell
# Logs sammeln
$logPath = "C:\Program Files\OemersCalculatorAllInOne"
Compress-Archive -Path "$logPath\install.log","$logPath\app\logs\*" -DestinationPath "C:\Users\$env:USERNAME\Desktop\OemersCalc_Logs.zip"
```

### System-Info sammeln

```powershell
# System-Info
systeminfo > "C:\Users\$env:USERNAME\Desktop\systeminfo.txt"

# Python-Info
cd "C:\Program Files\OemersCalculatorAllInOne"
.\python_embed\python.exe --version > "C:\Users\$env:USERNAME\Desktop\python_info.txt"
.\python_embed\python.exe -m pip list >> "C:\Users\$env:USERNAME\Desktop\python_info.txt"
```

---

## 📝 VERSIONS-INFO

| Komponente | Version |
|------------|---------|
| **App** | 2.0.0 |
| **Python** | 3.11.9 (Embedded) |
| **Streamlit** | 1.49.1 |
| **Pandas** | 2.3.2 |
| **NumPy** | 2.3.2 |
| **Plotly** | 6.3.0 |
| **SQLAlchemy** | 2.0.43 |
| **Total Packages** | 194 |
| **Total Wheels** | 252 |

---

## 🎉 ERSTE SCHRITTE

Nach erfolgreicher Installation:

1. **App starten** (Desktop-Icon)
2. **Browser öffnet** → <http://localhost:8501>
3. **Login** (falls konfiguriert)
4. **Hauptmenü** erscheint
5. **Solar-Rechner** öffnen
6. **Projekt erstellen**
7. **PDF exportieren**

**Fertig! Viel Erfolg!** 🚀

---

**Erstellt mit COMPLETE_SETUP_BUILDER.ps1**
**Build-Datum:** 2025-10-30
**Ersteller:** Ömer's Software Solutions
