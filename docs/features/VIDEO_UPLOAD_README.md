# Video-Upload Feature - Quick Start Guide

## Was ist neu?

Du kannst jetzt **Videos direkt hochladen** für den Intro-Bildschirm, ohne auf YouTube oder externe Links angewiesen zu sein!

## Schnellstart

### 1. Admin-Panel öffnen

```powershell
streamlit run admin_panel.py
```

### 2. Intro-Einstellungen aufrufen

Navigation: **Intro-Einstellungen** (in der Sidebar)

### 3. Video-Upload aktivieren

1. **Media-Typ**: Wähle "Video"
2. **Video-Quelle**: Wähle "Upload (MP4, AVI, MOV)"
3. **Browse files**: Klicke und wähle deine Video-Datei

### 4. Speichern

Klicke auf **"Einstellungen speichern"**

### 5. Testen

```powershell
streamlit run gui.py
```

Der Intro-Screen zeigt jetzt dein hochgeladenes Video!

---

## Unterstützte Formate

- MP4 (empfohlen)
- AVI
- MOV
- MKV
- WebM

---

## Features

### Option 1: Video hochladen
- Lokale Speicherung in `data/intro_videos/`
- Keine externen Abhängigkeiten
- Funktioniert offline
- Schnelleres Laden

### Option 2: Video-URL (wie vorher)
- YouTube-URLs
- Direkte Video-Links
- Automatische YouTube-Vorschau im Admin-Panel

---

## Beispiel-Workflow

```
1. Video vorbereiten (z.B. Firmenvideo, Produkt-Demo)
   -> Optimale Größe: < 50 MB
   -> Optimale Auflösung: 1280x720
   
2. Admin-Panel öffnen
   -> "Intro-Einstellungen"
   
3. Media-Typ "Video" wählen
   
4. "Upload (MP4, AVI, MOV)" wählen
   
5. Video hochladen
   -> Vorschau wird angezeigt
   -> Dateigröße wird angezeigt
   
6. "Einstellungen speichern" klicken
   
7. Intro-Screen testen
   -> streamlit run gui.py
   -> Video wird automatisch abgespielt
```

---

## Tipps

### Video-Optimierung

Zu große Videos? Nutze **HandBrake** (kostenlos):
1. Download: https://handbrake.fr/
2. Video laden
3. Preset: "Fast 720p30"
4. Start Encode

### Alternative: FFmpeg

```bash
ffmpeg -i input.avi -vcodec h264 -acodec aac -b:v 3M -s 1280x720 output.mp4
```

---

## Troubleshooting

### Video wird nicht angezeigt?

**Lösung 1**: Seite neu laden (F5)

**Lösung 2**: Format prüfen
- MP4 ist am kompatibelsten
- Konvertiere AVI/MOV zu MP4 falls Probleme

**Lösung 3**: Browser prüfen
- Chrome/Edge: Beste Unterstützung
- Firefox: Gut
- Safari: Gut für MOV

### Upload schlägt fehl?

**Lösung 1**: Dateigröße reduzieren
- Maximal: 200 MB (Streamlit-Standard)
- Empfohlen: < 50 MB

**Lösung 2**: Anderes Format
- Versuche MP4 statt AVI/MOV

---

## Technische Details

### Speicherort
```
data/
  intro_videos/
    intro_video.mp4    # Dein hochgeladenes Video
```

### Konfiguration
```json
{
  "media_type": "video",
  "video_file_path": "data/intro_videos/intro_video.mp4",
  "video_url": ""
}
```

---

## Migration von YouTube zu Upload

1. Download YouTube-Video (yt-dlp oder Online-Tools)
2. Optional: Konvertiere zu MP4
3. Admin-Panel → Intro-Einstellungen
4. "Upload" wählen
5. Video hochladen

---

## Dokumentation

Vollständige Dokumentation: `docs/features/VIDEO_UPLOAD_INTRO.md`

---

**Status**: IMPLEMENTIERT & GETESTET  
**Version**: 1.0.0  
**Datum**: 2025-12-09
