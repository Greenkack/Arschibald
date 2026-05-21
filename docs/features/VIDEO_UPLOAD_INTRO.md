# Video-Upload Funktion - Intro Screen

**Datum**: 2025-12-09  
**Feature**: Video-Upload für Intro-Bildschirm  
**Teil von**: Phase 4 - Intro Screen Modernization

---

## Übersicht

Die Video-Upload-Funktion ermöglicht es, Videos direkt in die Anwendung hochzuladen und im Intro-Bildschirm anzuzeigen, als Alternative zu YouTube-URLs oder Bild-Anzeigen.

---

## Unterstützte Formate

- **MP4** (empfohlen - beste Kompatibilität)
- **AVI**
- **MOV**
- **MKV**
- **WebM**

---

## Verwendung

### 1. Admin-Panel öffnen

Navigiere zu: **Admin-Panel** → **Intro-Einstellungen**

### 2. Media-Typ auswählen

Wähle **"Video"** als Media-Typ

### 3. Video-Quelle wählen

Du hast zwei Optionen:

#### Option A: Video hochladen (empfohlen)

1. Wähle **"Upload (MP4, AVI, MOV)"**
2. Klicke auf **"Browse files"**
3. Wähle deine Video-Datei aus
4. Warte auf Upload-Bestätigung
5. Vorschau wird automatisch angezeigt

**Vorteile**:
- Keine Abhängigkeit von externen Diensten
- Schnelleres Laden (lokal gespeichert)
- Volle Kontrolle über Video-Inhalt
- Funktioniert offline

**Speicherort**: `data/intro_videos/intro_video.[extension]`

#### Option B: Video-URL verwenden

1. Wähle **"URL (YouTube oder direkt)"**
2. Gib YouTube-URL oder direkten Video-Link ein
3. Vorschau wird für YouTube-Videos angezeigt

**Unterstützte URLs**:
- YouTube: `https://www.youtube.com/watch?v=xxxxx`
- YouTube Short: `https://youtu.be/xxxxx`
- Direkte Video-Links: `https://example.com/video.mp4`

---

## Technische Details

### Dateistruktur

```
data/
  intro_videos/
    intro_video.mp4      # Hochgeladenes Video (überschreibt vorheriges)
    intro_video.mov      # Alternative Formate
    intro_video.avi
```

### Konfiguration (intro_settings.json)

```json
{
  "enabled": true,
  "media_type": "video",
  "video_file_path": "data/intro_videos/intro_video.mp4",
  "video_url": "",
  ...
}
```

**Wichtig**: 
- `video_file_path` hat Priorität vor `video_url`
- Wenn Upload verwendet wird, wird `video_url` geleert
- Wenn URL verwendet wird, wird `video_file_path` geleert

---

## Code-Änderungen

### 1. intro_screen.py

**Neue Logik** (Zeile ~395):
```python
if media_type == 'video':
    # Prüfe zuerst ob hochgeladenes Video vorhanden
    video_file_path = settings.get('video_file_path', '')
    video_url = settings.get('video_url', '')
    
    if video_file_path and Path(video_file_path).exists():
        # Hochgeladenes Video abspielen
        st.video(str(video_file_path))
    elif video_url:
        # Fallback auf URL
        # YouTube oder direkte URL
        ...
```

**Priorität**:
1. Hochgeladene Datei (video_file_path)
2. Video-URL (video_url)
3. Info-Nachricht falls nichts konfiguriert

---

### 2. admin_intro_settings_ui.py

**Neue UI** (Zeile ~311):
```python
elif media_type == 'video':
    video_source = st.radio(
        "Video-Quelle",
        options=["Upload (MP4, AVI, MOV)", "URL (YouTube oder direkt)"]
    )
    
    if video_source == "Upload (MP4, AVI, MOV)":
        uploaded_video = st.file_uploader(
            "Video hochladen",
            type=["mp4", "avi", "mov", "mkv", "webm"]
        )
        
        if uploaded_video is not None:
            # Speichere in data/intro_videos/
            video_path = Path("data/intro_videos") / f"intro_video.{extension}"
            with open(video_path, "wb") as f:
                f.write(uploaded_video.getbuffer())
            
            st.success(f"Video hochgeladen: {video_filename}")
            st.video(str(video_path))  # Vorschau
```

---

### 3. Neue Settings-Keys

**intro_settings.json**:
```json
{
  "video_file_path": "data/intro_videos/intro_video.mp4"  // NEU
}
```

---

## Workflow-Diagramm

```
Admin-Panel: Intro-Einstellungen
    |
    v
Media-Typ: Video auswählen
    |
    v
Video-Quelle wählen
    |
    +-- Upload (MP4, AVI, MOV)
    |       |
    |       v
    |   File Uploader
    |       |
    |       v
    |   Speichere in data/intro_videos/
    |       |
    |       v
    |   Setze video_file_path in Settings
    |       |
    |       v
    |   Vorschau anzeigen
    |
    +-- URL (YouTube oder direkt)
            |
            v
        Text Input für URL
            |
            v
        Setze video_url in Settings
            |
            v
        YouTube-Vorschau (falls YouTube-URL)

Speichern-Button klicken
    |
    v
Schreibe intro_settings.json
    |
    v
Intro-Screen zeigt Video beim nächsten Laden
```

---

## Fehlerbehandlung

### Video kann nicht geladen werden

**Symptom**: `st.error("Video konnte nicht geladen werden")`

**Mögliche Ursachen**:
1. Video-Datei wurde gelöscht oder verschoben
2. Datei-Format nicht unterstützt
3. Datei korrupt

**Lösung**:
1. Video erneut hochladen
2. Anderes Format versuchen (MP4 empfohlen)
3. Video-URL als Fallback verwenden

---

### Vorschau nicht verfügbar

**Symptom**: `st.warning("Vorschau nicht verfügbar")`

**Mögliche Ursachen**:
1. Browser unterstützt Video-Codec nicht
2. Video zu groß für Browser-Rendering

**Lösung**:
- Video wird trotzdem gespeichert
- Testen im Intro-Screen nach Speichern

---

### YouTube-Vorschau nicht verfügbar

**Symptom**: `st.warning("YouTube-Vorschau nicht verfügbar")`

**Mögliche Ursachen**:
1. Ungültige YouTube-URL
2. Video ist privat oder eingebettet deaktiviert
3. Netzwerkproblem

**Lösung**:
1. URL-Format prüfen: `https://www.youtube.com/watch?v=xxxxx`
2. Video-Einstellungen auf YouTube prüfen
3. Direkte Video-Datei hochladen als Alternative

---

## Best Practices

### Datei-Größe

**Empfohlen**: < 50 MB
- Schnelleres Laden
- Weniger Server-Last
- Bessere Performance

**Maximum**: Abhängig von Streamlit-Konfiguration (Standard: 200 MB)

### Video-Optimierung

**Tools für Komprimierung**:
- HandBrake (kostenlos, Open Source)
- FFmpeg (Command-Line)
- Online-Tools: CloudConvert, Online-Convert

**Empfohlene Einstellungen**:
- Auflösung: 1280x720 (HD Ready)
- Codec: H.264
- Bitrate: 2-5 Mbps
- Format: MP4

### Beispiel FFmpeg-Befehl:
```bash
ffmpeg -i input.avi -vcodec h264 -acodec aac -b:v 3M -s 1280x720 output.mp4
```

---

## Sicherheit

### Upload-Validierung

**Implementiert**:
- File-Type Validierung (nur erlaubte Formate)
- Dateiname-Sanitization
- Speicherung in geschütztem Verzeichnis

**TODO** (Phase 22 - Security Audit):
- Dateigröße-Limit enforcing
- Virus-Scan für Uploads
- Content-Type Validierung

---

## Performance

### Lazy Loading

Aktuell: Video wird bei Seiten-Load geladen

**Zukünftige Optimierung** (Phase 23):
- Lazy Loading mit Thumbnail-Vorschau
- Video-Streaming statt vollständigem Download
- Caching-Strategie

---

## Migration

### Von URL zu Upload

1. Lade Video von YouTube herunter (z.B. mit yt-dlp)
2. Konvertiere zu MP4 falls nötig
3. Lade in Admin-Panel hoch
4. Video-URL wird automatisch geleert

### Von Upload zu URL

1. Wähle "URL" als Video-Quelle
2. Gib YouTube-URL ein
3. Video-Datei bleibt gespeichert (kann manuell gelöscht werden)

---

## Troubleshooting

### Video wird nicht angezeigt

**Checkliste**:
1. [ ] Media-Typ ist "video" in Settings
2. [ ] Video-Datei existiert in `data/intro_videos/`
3. [ ] Pfad in `intro_settings.json` korrekt
4. [ ] Browser unterstützt Video-Format
5. [ ] Seite neu geladen (F5)

### Upload schlägt fehl

**Checkliste**:
1. [ ] Dateigröße < 200 MB
2. [ ] Datei-Format unterstützt (MP4, AVI, MOV, MKV, WebM)
3. [ ] Verzeichnis `data/intro_videos/` existiert
4. [ ] Schreibrechte für Verzeichnis vorhanden

---

## Changelog

**2025-12-09 - Video Upload implementiert**:
- Added: File Uploader in admin_intro_settings_ui.py
- Added: video_file_path zu intro_settings.json
- Modified: intro_screen.py - Priorität für hochgeladene Videos
- Created: data/intro_videos/ Verzeichnis
- Added: Vorschau für hochgeladene Videos
- Added: Option zum Entfernen aktueller Videos
- Added: YouTube-Vorschau für URLs

---

**Status**: IMPLEMENTIERT  
**Getestet**: Pending  
**Teil von Phase 4**: In Progress
