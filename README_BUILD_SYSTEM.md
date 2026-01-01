# 📦 ARSCHIBALD - Vollständiges EXE Setup System

## 🎯 Überblick

Dieses Build-System erstellt eine **100% eigenständige Windows-Installation** für ARSCHIBALD mit:

- ✅ **Python Runtime** eingebettet (keine Installation erforderlich)
- ✅ **Alle Dependencies** (Streamlit, pandas, ReportLab, PyVista, etc.)
- ✅ **Alle Daten** (Datenbank, PDFs, Templates, Configs, Logos)
- ✅ **Windows Setup-Installer** (.exe mit Installationsassistent)
- ✅ **Portable Version** (.zip für USB-Stick ohne Installation)

**Endkunden benötigen NICHTS außer Windows!** 🎉

---

## 📁 Build-System Dateien

| Datei | Beschreibung |
|-------|--------------|
| **BUILD_EXE.bat** | ⭐ **Start hier!** Automatischer Build (Doppelklick) |
| **build_exe_setup.py** | Haupt-Build-Script (Python) |
| **check_build_requirements.py** | Prüft alle Voraussetzungen |
| **TEST_EXE.bat** | Testet erstellte EXE |
| **BUILD_ANLEITUNG.md** | Detaillierte Dokumentation |
| **QUICK_START.md** | Schnellstart in 3 Schritten |

---

## 🚀 Schnellstart (3 Schritte)

### 1️⃣ Voraussetzungen prüfen

```powershell
python check_build_requirements.py
```

**Automatische Installation** fehlender Packages wird angeboten!

### 2️⃣ Build starten

**Einfach:**

```
Doppelklick auf: BUILD_EXE.bat
```

**Oder manuell:**

```powershell
python build_exe_setup.py
```

⏱️ **Dauer:** 5-10 Minuten (je nach CPU)

### 3️⃣ Testen & Verteilen

**Testen:**

```
Doppelklick auf: TEST_EXE.bat
```

**Verteilen:**

- `ARSCHIBALD_Setup_v2.0.0.exe` → Endkunden (Installation)
- `ARSCHIBALD_Portable_v2.0.0.zip` → USB-Stick (keine Installation)

---

## 📦 Was wird erstellt?

Nach erfolgreichem Build findest du:

### 📂 dist/ARSCHIBALD/

Eigenständige App (200-500 MB)

```
ARSCHIBALD/
├── ARSCHIBALD.exe          ← Haupt-Programm
├── _internal/              ← Python + Dependencies
│   ├── streamlit/
│   ├── pandas/
│   ├── reportlab/
│   └── ...
├── data/                   ← Datenbank & Settings
├── pdf_templates_static/   ← PDF-Templates
├── coords_multi/           ← Koordinaten
├── customer_documents/     ← Kundendaten
└── .streamlit/             ← Streamlit-Config
```

**Verwendung:** Direkt `ARSCHIBALD.exe` starten

### 📄 ARSCHIBALD_Setup_v2.0.0.exe

Windows Installer (150-300 MB komprimiert)

**Features:**

- 🎨 Professioneller Installationsassistent
- 📍 Installation nach `C:\Program Files\ARSCHIBALD`
- 🖥️ Desktop-Verknüpfung
- 📋 Startmenü-Eintrag
- 🗑️ Saubere Deinstallation
- 🔐 Optional: Admin-Rechte

**Verwendung:** Doppelklick → Installationsassistent folgen

### 📦 ARSCHIBALD_Portable_v2.0.0.zip

Portable Version (200-400 MB)

**Vorteile:**

- 💾 Läuft von USB-Stick
- 🚫 Keine Installation
- 🔓 Keine Admin-Rechte erforderlich
- 📁 Alle Daten lokal

**Verwendung:** Entpacken → `ARSCHIBALD.exe` starten

---

## ⚙️ Build-Konfiguration

Anpassungen in `build_exe_setup.py`:

```python
# App-Informationen
APP_NAME = "ARSCHIBALD"           # Anwendungsname
APP_VERSION = "2.0.0"             # Version
APP_AUTHOR = "Ömer"               # Autor/Firma
APP_DESCRIPTION = "PV- und Wärmepumpen-Software"

# Icon (optional)
ICON_FILE = "data/company_logos/app_icon.ico"

# Zusätzliche Daten einbinden
datas = [
    ('data', 'data'),
    ('mein_ordner', 'mein_ordner'),  # Hier hinzufügen
]

# Module explizit einbinden
hiddenimports = [
    'streamlit',
    'pandas',
    'mein_modul',  # Hier hinzufügen
]
```

---

## 🔧 Erweiterte Optionen

### Console-Modus aktivieren (Debugging)

In `ARSCHIBALD.spec` ändern:

```python
exe = EXE(
    ...
    console=True,  # Zeigt Console-Fenster
    ...
)
```

Neu bauen: `pyinstaller ARSCHIBALD.spec --clean`

### Größe reduzieren

1. **Ungenutzte Packages entfernen:**
   - In `requirements.txt` löschen
   - In `.spec` zu `excludes` hinzufügen

2. **UPX Kompression:**

   ```python
   exe = EXE(..., upx=True, ...)
   ```

3. **Onefile-Build** (ein einzige EXE statt Verzeichnis):

   ```python
   exe = EXE(
       ...
       exclude_binaries=False,  # Statt True
       ...
   )
   # COLLECT Block entfernen
   ```

### Code Signing (Empfohlen für Production)

Windows SmartScreen-Warnung vermeiden:

```powershell
# Mit SignTool von Windows SDK
signtool sign /f "Zertifikat.pfx" /p "Passwort" /t http://timestamp.digicert.com "ARSCHIBALD_Setup_v2.0.0.exe"
```

**Vorteile:**

- ✅ Keine SmartScreen-Warnung
- ✅ Vertrauen bei Endkunden
- ✅ Professionell

**Kosten:** ca. 100-300€/Jahr für Code-Signing Zertifikat

---

## 🐛 Troubleshooting

### Problem: Build schlägt fehl

**Lösung 1:** Prüfe Voraussetzungen

```powershell
python check_build_requirements.py
```

**Lösung 2:** Installiere alles neu

```powershell
pip install -r requirements.txt --upgrade
pip install pyinstaller --upgrade
```

**Lösung 3:** Bereinige Build-Cache

```powershell
rmdir /s /q build dist
python build_exe_setup.py
```

### Problem: EXE startet nicht

**Lösung:** Console-Modus aktivieren

1. In `ARSCHIBALD.spec`: `console=True`
2. Neu bauen: `pyinstaller ARSCHIBALD.spec --clean`
3. Starte EXE → Lies Fehlerausgabe in Console

### Problem: "Modul XYZ nicht gefunden"

**Lösung:** Modul explizit einbinden

In `ARSCHIBALD.spec` zu `hiddenimports` hinzufügen:

```python
hiddenimports = [
    'streamlit',
    'pandas',
    'xyz',  # Fehlendes Modul
]
```

### Problem: Datei fehlt zur Laufzeit

**Lösung:** Datei/Ordner zu `datas` hinzufügen

In `ARSCHIBALD.spec`:

```python
datas = [
    ('data', 'data'),
    ('fehlende_datei.txt', '.'),
    ('fehlender_ordner', 'fehlender_ordner'),
]
```

### Problem: Setup-Installer wird nicht erstellt

**Ursache:** Inno Setup nicht installiert (optional)

**Lösungen:**

- **Option A:** Installiere Inno Setup: <https://jrsoftware.org/isdl.php>
- **Option B:** Nutze Portable ZIP (funktioniert ohne Inno Setup)
- **Option C:** Kompiliere manuell: Öffne `ARSCHIBALD_setup.iss` in Inno Setup

---

## 📊 Technische Details

### Build-Prozess

1. **Analyse:** PyInstaller analysiert `gui.py` und alle Imports
2. **Sammeln:** Kopiert Python-Runtime + Dependencies nach `dist/`
3. **Kompilieren:** Erstellt Bootloader (`ARSCHIBALD.exe`)
4. **Packen:** Bundelt alles in `dist/ARSCHIBALD/`
5. **Installer:** Inno Setup erstellt Setup-EXE (optional)
6. **ZIP:** Portable Version wird erstellt

### Dateigrößen (Richtwerte)

| Komponente | Größe |
|------------|-------|
| Python Runtime | 30-50 MB |
| Streamlit + Dependencies | 150-300 MB |
| Deine App-Dateien | 20-50 MB |
| **Gesamt (unkomprimiert)** | **200-500 MB** |
| Setup-Installer (komprimiert) | 150-300 MB |
| Portable ZIP (komprimiert) | 200-400 MB |

### Unterstützte Python-Versionen

- ✅ Python 3.10
- ✅ Python 3.11
- ✅ Python 3.12
- ⚠️ Python 3.9 (möglich, aber nicht empfohlen)

### Unterstützte Windows-Versionen

- ✅ Windows 11 (alle Versionen)
- ✅ Windows 10 (64-bit)
- ⚠️ Windows 10 (32-bit) - erfordert 32-bit Python
- ❌ Windows 7/8 (nicht getestet)

---

## 📋 Checkliste vor Auslieferung

Vor Verteilung an Endkunden:

- [ ] **Funktionalität:** Alle Features getestet
- [ ] **Performance:** App läuft flüssig
- [ ] **Stabilität:** Keine Crashes bei normaler Nutzung
- [ ] **Console:** `console=False` in `.spec` (keine Console-Fenster)
- [ ] **Icon:** Eigenes App-Icon eingebunden
- [ ] **Version:** Korrekte Versionsnummer in `build_exe_setup.py`
- [ ] **README:** README.txt angepasst
- [ ] **Lizenz:** LICENSE.txt vorhanden
- [ ] **Setup-Test:** Installer auf sauberem System getestet
- [ ] **Portable-Test:** ZIP-Version getestet
- [ ] **Deinstallation:** Setup-Deinstallation getestet
- [ ] **Antivirus:** Scan durchgeführt (keine False Positives)
- [ ] **Code Signing:** Optional, aber empfohlen
- [ ] **Dokumentation:** Benutzerhandbuch vorhanden

---

## 🎓 Weiterführende Informationen

### PyInstaller Dokumentation

<https://pyinstaller.org/en/stable/>

### Inno Setup Dokumentation

<https://jrsoftware.org/ishelp/>

### Code Signing

- Windows SDK: <https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/>
- Zertifikate: Sectigo, DigiCert, GlobalSign

### Alternativen zu PyInstaller

- **cx_Freeze:** <https://cx-freeze.readthedocs.io/>
- **py2exe:** <http://www.py2exe.org/> (nur Windows)
- **Nuitka:** <https://nuitka.net/> (Python-zu-C Compiler)

---

## 📞 Support & Kontakt

Bei Fragen oder Problemen:

1. 📖 Lies [BUILD_ANLEITUNG.md](BUILD_ANLEITUNG.md)
2. 🔍 Prüfe Troubleshooting-Abschnitt oben
3. 🧪 Teste mit Console-Modus (`console=True`)
4. 📝 Prüfe Build-Logs in `build/`

---

## 📄 Lizenz

Copyright (c) 2025 Ömer
Alle Rechte vorbehalten.

---

## 🎉 Viel Erfolg

Deine ARSCHIBALD-App ist jetzt bereit für professionelle Distribution als eigenständige Windows-Anwendung!

**Happy Deploying! 🚀**
