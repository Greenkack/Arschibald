# 🎯 QUICK START - EXE Setup in 3 Schritten

## 📋 Was du brauchst

- ✅ Windows 10/11
- ✅ Python 3.10+ (<https://www.python.org/downloads/>)
- ✅ Internetverbindung (für Downloads)

---

## 🚀 Schritt 1: Build starten

### Option A: Automatisch (Empfohlen)

Doppelklick auf:

```
BUILD_EXE.bat
```

### Option B: Manuell

```powershell
python build_exe_setup.py
```

**Wartezeit:** 5-10 Minuten ☕

---

## ✅ Schritt 2: Testen

Nach dem Build:

```
TEST_EXE.bat
```

Wähle Option **[1]** zum Testen mit Console-Output.

---

## 📦 Schritt 3: Verteilen

Du findest in `dist/`:

### 1. **Für Installation** (Endkunden)

```
ARSCHIBALD_Setup_v2.0.0.exe
```

→ Doppelklick installiert alles automatisch

### 2. **Portable** (USB-Stick, keine Installation)

```
ARSCHIBALD_Portable_v2.0.0.zip
```

→ Entpacken und EXE starten

### 3. **Developer-Version** (zum Testen)

```
dist/ARSCHIBALD/ARSCHIBALD.exe
```

→ Direkt ausführbar

---

## 🎉 Fertig

Die App ist jetzt als eigenständige Windows-Anwendung verpackt!

**Keine Python-Installation beim Endkunden erforderlich!** 🎊

---

## ⚠️ Probleme?

### "Python nicht gefunden"

→ Installiere Python: <https://www.python.org/downloads/>
→ Aktiviere "Add to PATH" bei Installation!

### "Build fehlgeschlagen"

→ Führe aus: `pip install -r requirements.txt`
→ Starte neu: `BUILD_EXE.bat`

### "EXE startet nicht"

→ Teste mit Console: `TEST_EXE.bat` → Option [1]
→ Prüfe Fehlerausgabe

---

## 📞 Weitere Hilfe

Siehe: `BUILD_ANLEITUNG.md` für Details

---

**Happy Building! 🚀**
