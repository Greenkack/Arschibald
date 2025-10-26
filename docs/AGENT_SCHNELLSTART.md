# 🚀 A.G.E.N.T. Schnellstart

## Das A.G.E.N.T.-Menü ist jetzt freigeschaltet! ✅

### Sofort loslegen in 3 Schritten:

## 1️⃣ API-Key konfigurieren

Erstelle eine `.env` Datei im Hauptverzeichnis (falls noch nicht vorhanden):

```env
OPENAI_API_KEY=sk-your-openai-key-here
```

**Wo bekomme ich den Key?**
- Gehe zu [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- Erstelle einen neuen API-Key
- Kopiere ihn in die `.env` Datei

## 2️⃣ Anwendung starten

```bash
streamlit run gui.py
```

## 3️⃣ A.G.E.N.T. öffnen

- Klicke im Menü auf **"A.G.E.N.T."**
- Das Agent-Interface wird geladen
- Gib deine erste Aufgabe ein!

---

## 🎯 Erste Aufgaben zum Ausprobieren

### Beispiel 1: Photovoltaik-Beratung
```
Was sind die wichtigsten Vorteile von Photovoltaik-Anlagen für Privathaushalte?
```

### Beispiel 2: Code-Generierung
```
Schreibe eine Python-Funktion, die prüft, ob eine Zahl eine Primzahl ist.
Füge Type Hints und Docstring hinzu.
```

### Beispiel 3: ROI-Berechnung
```
Berechne den ROI für eine 10 kWp PV-Anlage:
- Investition: 15.000 €
- Jahresverbrauch: 4.500 kWh
- Strompreis: 0,35 €/kWh
- Eigenverbrauch: 30%
```

---

## 📚 Mehr lernen?

- **Anfänger**: [Basic Usage Tutorial](Agent/BASIC_USAGE_TUTORIAL.md)
- **Fortgeschritten**: [Advanced Features Guide](Agent/ADVANCED_FEATURES_GUIDE.md)
- **Beispiele**: [Example Tasks](Agent/EXAMPLE_TASKS.md) - 21 fertige Beispiele
- **Hilfe**: [User Troubleshooting Guide](Agent/USER_TROUBLESHOOTING_GUIDE.md)

---

## ⚙️ Optional: Erweiterte Funktionen

### Docker für Code-Ausführung (optional)
Wenn du Code im Sandbox ausführen möchtest:

1. Installiere [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Starte Docker
3. Baue das Sandbox-Image:
   ```bash
   python Agent/build_sandbox.py
   ```

### Knowledge Base einrichten (optional)
Für domänenspezifisches Wissen:

1. Kopiere PDF-Dateien nach `Agent/knowledge_base/`
2. Indexiere sie:
   ```bash
   python Agent/setup_knowledge_base.py
   ```

### Weitere API-Keys (optional)
Für erweiterte Funktionen in `.env` hinzufügen:

```env
# Web-Suche
TAVILY_API_KEY=your-tavily-key

# Sprachsynthese
ELEVENLABS_API_KEY=your-elevenlabs-key

# Telefonie-Simulation
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-number
```

---

## ❓ Probleme?

### "Module not found" Fehler?
```bash
python -m pip install -r Agent/requirements.txt
```

### "API Key missing" Warnung?
Überprüfe deine `.env` Datei - `OPENAI_API_KEY` muss gesetzt sein!

### Weitere Hilfe?
Siehe [User Troubleshooting Guide](Agent/USER_TROUBLESHOOTING_GUIDE.md)

---

## 🎉 Viel Erfolg!

Das A.G.E.N.T.-System steht dir jetzt zur Verfügung. Probiere es aus und entdecke die Möglichkeiten!

**Vollständige Dokumentation**: [Training Materials Index](Agent/TRAINING_MATERIALS_INDEX.md)
