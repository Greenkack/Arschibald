# Video Fullscreen Background - Intro Screen

**Datum**: 2025-01-18
**Feature**: Autoplay Background-Video mit Größen-Optionen

## Übersicht

Das Intro-Video kann jetzt als Fullscreen-Hintergrund mit automatischem Start und Endlos-Wiederholung angezeigt werden.

## Features

### 1. Video-Größen

Vier Größen-Optionen verfügbar:

| Größe | Auflösung | Beschreibung | Verwendung |
|-------|-----------|--------------|------------|
| **Small** | 640x360 | Kompakt | Kleine Vorschau |
| **Medium** | 854x480 | Standard | Normale Darstellung |
| **Large** | 1280x720 | HD | Große Darstellung |
| **Fullscreen** | 100vw x 100vh | Vollbild | Hintergrund (empfohlen) |

### 2. Wiedergabe-Optionen

#### Automatisch starten (Autoplay)
- **Default**: Aktiviert
- Video startet automatisch beim Laden
- **Wichtig**: Video wird automatisch stummgeschaltet (Browser-Anforderung)

#### Endlos wiederholen (Loop)
- **Default**: Aktiviert
- Video wiederholt sich automatisch
- Perfekt für Hintergrund-Videos

### 3. Fullscreen Background

**Besonderheiten**:
- Video füllt gesamten Bildschirm
- `position: fixed` → Video bleibt im Hintergrund
- `object-fit: cover` → Video skaliert ohne Verzerrung
- `z-index: -1` → Inhalt liegt über dem Video

## Technische Details

### HTML5-Video (Lokale Dateien)

```html
<video autoplay loop muted playsinline
    style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; object-fit: cover; z-index: -1;">
    <source src="data/intro_videos/intro_video.mp4" type="video/mp4">
    Ihr Browser unterstützt das Video-Tag nicht.
</video>
```

**Attribute**:
- `autoplay` - Automatischer Start
- `loop` - Endlos-Wiederholung
- `muted` - Stumm (erforderlich für Autoplay)
- `playsinline` - Verhindert Fullscreen auf iOS

### YouTube-Video

```html
<iframe style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1;"
    src="https://www.youtube.com/embed/VIDEO_ID?autoplay=1&loop=1&mute=1&playlist=VIDEO_ID&controls=0"
    frameborder="0" allow="autoplay; encrypted-media" allowfullscreen>
</iframe>
```

**Parameter**:
- `autoplay=1` - Automatischer Start
- `loop=1` - Endlos-Wiederholung
- `mute=1` - Stumm
- `playlist=VIDEO_ID` - Erforderlich für Loop
- `controls=0` - Keine Player-Controls

## Admin-Einstellungen

### Video-Größe auswählen

```python
video_size = st.selectbox(
    "Größe/Darstellung des Videos",
    options=["small", "medium", "large", "fullscreen"],
    index=3,  # Default: fullscreen
    format_func=lambda x: {
        'small': 'Klein (640x360) - Kompakt',
        'medium': 'Mittel (854x480) - Standard',
        'large': 'Groß (1280x720) - HD',
        'fullscreen': 'Vollbild - Hintergrund (empfohlen)'
    }[x]
)
```

### Wiedergabe-Optionen

```python
video_autoplay = st.checkbox("Automatisch starten", value=True)
video_loop = st.checkbox("Endlos wiederholen", value=True)
```

## Settings Schema

### intro_settings.json

```json
{
  "media_type": "video",
  "video_file_path": "data/intro_videos/intro_video.mp4",
  "video_url": "",
  "video_size": "fullscreen",
  "video_autoplay": true,
  "video_loop": true
}
```

### Default-Werte

```python
default_settings = {
    "video_size": "fullscreen",
    "video_autoplay": True,
    "video_loop": True
}
```

## Code-Änderungen

### intro_screen.py

**Hinzugefügt** (Lines ~73-75):
```python
"video_size": "fullscreen",
"video_autoplay": True,
"video_loop": True,
```

**Geändert** (Lines ~396-445):
- Entfernt: `st.video()` (Play-Button)
- Hinzugefügt: HTML5 `<video>` Tag mit Autoplay/Loop
- Hinzugefügt: YouTube iframe mit Autoplay-Parametern
- Hinzugefügt: Größen-Logik mit CSS

### admin_intro_settings_ui.py

**Hinzugefügt** (Lines ~312-345):
```python
# Video-Größe Auswahl
video_size = st.selectbox(...)

# Wiedergabe-Optionen
video_autoplay = st.checkbox("Automatisch starten", ...)
video_loop = st.checkbox("Endlos wiederholen", ...)
```

**Hinzugefügt** (Lines ~505-515):
```python
'video_size': video_size if media_type == 'video' else ...,
'video_autoplay': video_autoplay if media_type == 'video' else ...,
'video_loop': video_loop if media_type == 'video' else ...,
```

## Browser-Kompatibilität

### Autoplay-Einschränkungen

**Chrome/Edge**:
- Autoplay funktioniert nur mit `muted`
- Ohne `muted` → User-Interaktion erforderlich

**Firefox**:
- Autoplay funktioniert nur mit `muted`
- Ähnliche Policy wie Chrome

**Safari**:
- Autoplay funktioniert nur mit `muted` + `playsinline`
- iOS: Autoplay nur in bestimmten Kontexten

### Lösung

**Immer muted verwenden**:
```html
<video autoplay loop muted playsinline>
```

Wenn Ton gewünscht:
- Nutzer muss Video manuell starten
- Button "Mit Ton abspielen" hinzufügen

## Performance-Optimierung

### Video-Komprimierung

**Empfohlene Tools**:
- **HandBrake** (kostenlos)
- **FFmpeg** (Command-Line)

**Empfohlene Einstellungen**:
```bash
# FFmpeg Kommando für optimiertes Web-Video
ffmpeg -i input.mp4 -c:v libx264 -preset slow -crf 23 -c:a aac -b:a 128k output.mp4
```

**Ziel**:
- Dateigröße: < 10 MB für Fullscreen
- Auflösung: 1920x1080 oder niedriger
- Bitrate: 2-5 Mbps

### Lazy Loading

Video wird nur geladen wenn Intro-Screen aktiv:
```python
if media_type == 'video':
    # Video-Code hier
```

## Beispiel-Workflow

### 1. Video hochladen

Admin-Panel → Intro-Einstellungen:
1. Media-Typ: **Video**
2. Video-Quelle: **Upload (MP4, AVI, MOV)**
3. Datei auswählen: `intro_background.mp4`
4. Video-Größe: **Fullscreen**
5. Automatisch starten: **✓**
6. Endlos wiederholen: **✓**
7. **Speichern**

### 2. Ergebnis

Intro-Screen zeigt:
- Video als Fullscreen-Hintergrund
- Automatischer Start (stumm)
- Endlos-Wiederholung
- Login-Formular über dem Video

## Troubleshooting

### Problem: Video startet nicht automatisch

**Ursache**: Browser blockiert Autoplay

**Lösung**:
1. Prüfe ob `muted` gesetzt ist
2. Prüfe Browser-Konsole auf Fehler
3. Teste mit anderem Browser

### Problem: Video zu groß / langsam

**Ursache**: Unkomprimiertes Video

**Lösung**:
1. Video komprimieren (siehe Performance-Optimierung)
2. Kleinere Auflösung verwenden
3. Bitrate reduzieren

### Problem: Video verzerrt

**Ursache**: Falsches Seitenverhältnis

**Lösung**:
- Fullscreen nutzt `object-fit: cover` → kein Letterboxing
- Für andere Größen: Video mit korrektem Seitenverhältnis (16:9)

## Sicherheit

### Datei-Upload

- Validierung: Nur `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`
- Speicherort: `data/intro_videos/` (nicht öffentlich)
- Größenlimit: Streamlit-Standard (~200 MB)

### XSS-Schutz

- Video-URLs werden escaped
- Kein JavaScript in Video-Pfaden

## Zukünftige Erweiterungen

### Geplant

1. **Audio-Toggle**
   - Button "Mit Ton abspielen"
   - User kann Ton aktivieren

2. **Playlists**
   - Mehrere Videos hintereinander
   - Zufällige Auswahl

3. **Untertitel**
   - WebVTT-Support
   - Multi-Sprache

4. **Fortschrittsbalken**
   - Zeige Video-Position
   - Skip-Button

## Changelog

### 2025-01-18 - Initial Release

- Video-Größen: Small, Medium, Large, Fullscreen
- Autoplay-Option (Default: aktiviert)
- Loop-Option (Default: aktiviert)
- HTML5-Video für lokale Dateien
- YouTube-iframe mit Autoplay-Parametern
- Admin-UI für alle Optionen
- Dokumentation

## Siehe auch

- [VIDEO_UPLOAD_INTRO.md](VIDEO_UPLOAD_INTRO.md) - Video-Upload-Feature
- [VIDEO_UPLOAD_README.md](VIDEO_UPLOAD_README.md) - Quick Start
- [Admin Intro Settings](../../admin_intro_settings_ui.py)
- [Intro Screen](../../intro_screen.py)
