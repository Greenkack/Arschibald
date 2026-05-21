# Video Fullscreen Background - Quick Start

## Was wurde implementiert?

Das Intro-Video läuft jetzt **automatisch** als **Fullscreen-Hintergrund** mit **Endlos-Wiederholung**.

### Vorher
- st.video() mit Play-Button
- Video musste manuell gestartet werden
- Feste Größe
- Keine Loop-Option

### Nachher
- Automatischer Start (Autoplay)
- Endlos-Wiederholung (Loop)
- 4 Größen-Optionen (small, medium, large, **fullscreen**)
- Kein Play-Button mehr
- Video als Hintergrund

## So verwendest du es

### 1. Video hochladen

**Admin-Panel** → **Intro-Einstellungen**:

1. **Media-Typ**: Video auswählen
2. **Video-Quelle**: "Upload (MP4, AVI, MOV)"
3. **Datei hochladen**: Dein Video auswählen
4. **Video-Größe**: **Fullscreen** (empfohlen für Hintergrund)
5. **Automatisch starten**: ✓ (aktiviert)
6. **Endlos wiederholen**: ✓ (aktiviert)
7. **Speichern** klicken

### 2. Ergebnis

Der Intro-Screen zeigt jetzt:
- Video füllt **gesamten Bildschirm**
- Startet **automatisch** (stumm)
- Wiederholt sich **endlos**
- Login-Formular liegt **über dem Video**

## Video-Größen

| Größe | Auflösung | Verwendung |
|-------|-----------|------------|
| Small | 640x360 | Kleine Vorschau |
| Medium | 854x480 | Standard-Darstellung |
| Large | 1280x720 | HD-Darstellung |
| **Fullscreen** | 100vw x 100vh | **Hintergrund (empfohlen)** |

## Wichtige Hinweise

### Video wird automatisch stummgeschaltet

**Warum?**
- Browser erlauben Autoplay nur mit `muted`
- Ohne Stummschaltung: User muss Play-Button klicken

**Lösung für Ton**:
- Video mit Hintergrundmusik = stumm OK
- Für Videos mit wichtigem Audio: Autoplay deaktivieren

### Empfohlene Video-Formate

**Format**: MP4 (H.264)
**Auflösung**: 1920x1080 oder niedriger
**Dateigröße**: < 10 MB
**Bitrate**: 2-5 Mbps

### Video optimieren

**Mit HandBrake** (kostenlos):
1. HandBrake öffnen
2. Video laden
3. Preset: "Web" → "YouTube HQ 1080p60"
4. Start klicken

**Mit FFmpeg** (Command-Line):
```bash
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -c:a aac -b:a 128k output.mp4
```

## Einstellungen im Detail

### Automatisch starten (Autoplay)

- **Standard**: Aktiviert ✓
- Video startet beim Laden
- **Browser-Anforderung**: Muss stumm sein

### Endlos wiederholen (Loop)

- **Standard**: Aktiviert ✓
- Video wiederholt sich automatisch
- Perfekt für Hintergrund-Videos

### Video-Größe: Fullscreen

- **CSS**: `position: fixed; width: 100vw; height: 100vh;`
- Video bleibt im Hintergrund (`z-index: -1`)
- Skaliert ohne Verzerrung (`object-fit: cover`)
- Inhalt liegt über dem Video

## Beispiel-Videos

### Gute Hintergrund-Videos

- Abstrakte Animationen
- Langsame Kamera-Fahrten
- Zeitraffer (Wolken, Sterne)
- Geometrische Muster
- Farbverläufe

### Zu vermeiden

- Videos mit viel Text (wird unlesbar)
- Schnelle Schnitte (ablenken vom Login)
- Grelle Farben (stören Formular)
- Zu dunkle Videos (Login schwer lesbar)

## Troubleshooting

### Video startet nicht automatisch

**Lösung**:
1. Prüfe: "Automatisch starten" aktiviert?
2. Browser-Konsole öffnen (F12) → Fehler prüfen
3. Teste mit anderem Browser

### Video zu groß / langsam

**Lösung**:
1. Video komprimieren (siehe oben)
2. Kleinere Auflösung (z.B. 1280x720)
3. Bitrate reduzieren

### Video sieht verzerrt aus

**Lösung**:
- Fullscreen nutzt `object-fit: cover` → automatische Anpassung
- Für andere Größen: Video mit 16:9 Seitenverhältnis

### Login-Formular schwer lesbar

**Lösung**:
1. Helleres/dunkleres Video verwenden
2. Video-Transparenz/Overlay in CSS anpassen
3. Größere Schrift im Formular

## YouTube-Videos

### YouTube als Hintergrund

1. **Video-Quelle**: "URL (YouTube oder direkt)"
2. **URL eingeben**: `https://youtu.be/VIDEO_ID`
3. **Video-Größe**: Fullscreen
4. **Automatisch starten**: ✓
5. **Endlos wiederholen**: ✓

**YouTube-Parameter** (automatisch):
- `autoplay=1` - Automatischer Start
- `loop=1` - Endlos-Wiederholung
- `mute=1` - Stummschaltung
- `controls=0` - Keine Player-Controls

## Test

```powershell
# Tests ausführen
python test_video_fullscreen.py

# App starten und Intro-Screen prüfen
streamlit run gui.py
```

## Nächste Schritte

1. **Video hochladen** im Admin-Panel
2. **Fullscreen aktivieren**
3. **Autoplay + Loop aktivieren**
4. **App neu starten**
5. **Intro-Screen testen**

---

**Viel Erfolg mit deinem Fullscreen-Background-Video!**

Bei Fragen: Siehe [VIDEO_FULLSCREEN_BACKGROUND.md](VIDEO_FULLSCREEN_BACKGROUND.md) für Details.
