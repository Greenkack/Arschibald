# Intro-Seitenbilder Feature - Dokumentation

## 📋 Übersicht

Das Intro-Bildschirm wurde um eine **3-Bilder-Ansicht** erweitert, die es ermöglicht, neben dem Hauptlogo zwei zusätzliche kleine Logos/Bilder links und rechts anzuzeigen.

## ✅ Implementierte Features

### 1. **Hauptbild (Mitte)**

- Großes Logo/Bild in der Mitte (400px max-width)
- Upload-Funktion im Admin-Panel
- Max. Dateigröße: 5MB
- Formate: PNG, JPG, JPEG
- Pfad: `data/company_logos/intro_main_[dateiname]`

### 2. **Linkes Seitenbild**

- Kleines Logo links vom Hauptbild (150px max-width)
- Upload-Funktion im Admin-Panel
- Max. Dateigröße: 2MB
- Formate: PNG, JPG, JPEG
- Pfad: `data/company_logos/intro_left_[dateiname]`

### 3. **Rechtes Seitenbild**

- Kleines Logo rechts vom Hauptbild (150px max-width)
- Upload-Funktion im Admin-Panel
- Max. Dateigröße: 2MB
- Formate: PNG, JPG, JPEG
- Pfad: `data/company_logos/intro_right_[dateiname]`

### 4. **Seitenbilder aktivieren/deaktivieren**

- Checkbox im Admin-Panel: "Seitenbilder aktivieren"
- Bei Deaktivierung: Nur Hauptbild wird angezeigt (Original-Layout)
- Bei Aktivierung: 3-Bilder-Layout mit Animation

## 🎨 Design & Animation

### CSS-Effekte (intro_screen.py)

```css
/* Hauptbild */
.intro-logo {
    max-width: 400px;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    animation: float 3s ease-in-out infinite;
    z-index: 10;
}

/* Seitenbilder */
.intro-logo-side {
    max-width: 150px;
    border-radius: 15px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    animation: float 3s ease-in-out infinite;
    opacity: 0.8;
}

.intro-logo-side:hover {
    opacity: 1;
    transform: scale(1.05);
}

/* Float Animation */
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-20px); }
}
```

### Layout-Struktur

```
┌──────────────────────────────────────────┐
│         Intro-Bildschirm Layout          │
├──────────────────────────────────────────┤
│                                          │
│  [Klein]     [GROSS]      [Klein]        │
│   Links      Mitte        Rechts         │
│  (150px)    (400px)       (150px)        │
│                                          │
│          Titel & Text                    │
│                                          │
│      [Login] | [Registrieren]            │
│                                          │
└──────────────────────────────────────────┘
```

## 🔧 Admin-Panel Konfiguration

### Zugriff

1. Öffne **Admin-Panel** (Menü F)
2. Wähle Tab: **"Intro-Einstellungen"**
3. Scrolle zu **"Medien-Anzeige"**

### Hauptbild konfigurieren

1. Medien-Typ: `Bild` auswählen
2. **Hauptbild-Pfad**: Pfad eingeben oder
3. **"Hauptbild hochladen"**: Datei auswählen (max. 5MB)
4. Vorschau erscheint automatisch

### Seitenbilder aktivieren

1. Checkbox **"Seitenbilder aktivieren"** anklicken
2. **Linkes Bild**:
   - Pfad eingeben oder Upload
   - Max. 2MB
   - Vorschau wird angezeigt
3. **Rechtes Bild**:
   - Pfad eingeben oder Upload
   - Max. 2MB
   - Vorschau wird angezeigt
4. **Layout-Vorschau**: Zeigt 3-Spalten-Ansicht aller Bilder

### Einstellungen speichern

- Button: **"Einstellungen speichern"**
- Bestätigung: Gespeicherte Bildpfade werden angezeigt
- Änderungen wirken beim nächsten App-Start

## 📂 Dateisystem-Struktur

```
Bokuk2/
├── data/
│   ├── company_logos/
│   │   ├── intro_main_[name].png     # Hauptbild
│   │   ├── intro_left_[name].png     # Linkes Seitenbild
│   │   ├── intro_right_[name].png    # Rechtes Seitenbild
│   │   └── ...
│   └── intro_settings.json            # Gespeicherte Einstellungen
├── intro_screen.py                    # Intro-Rendering
├── admin_intro_settings_ui.py         # Admin-Konfiguration
└── INTRO_SEITENBILDER_FEATURE.md      # Diese Dokumentation
```

## 📝 JSON-Konfiguration (intro_settings.json)

```json
{
  "enabled": true,
  "media_type": "image",
  "image_path": "data/company_logos/intro_main_logo.png",
  "image_left_path": "data/company_logos/intro_left_partner1.png",
  "image_right_path": "data/company_logos/intro_right_partner2.png",
  "show_side_images": true,
  "require_login": true,
  "allow_registration": true,
  "title": "Ömers All in One Machine",
  "subtitle": "",
  "description": ""
}
```

## 🎯 Empfohlene Bildgrößen

### Hauptbild (Mitte)

- **Optimale Größe**: 800x800px oder 1000x1000px
- **Seitenverhältnis**: Quadratisch (1:1) oder Hochformat
- **Format**: PNG mit Transparenz für besten Effekt
- **Max. Dateigröße**: 5MB

### Seitenbilder (Links/Rechts)

- **Optimale Größe**: 300x300px oder 500x500px
- **Seitenverhältnis**: Quadratisch (1:1)
- **Format**: PNG mit Transparenz
- **Max. Dateigröße**: 2MB je Bild

### Tipps für beste Ergebnisse

- ✅ Verwende transparente PNGs (alpha channel)
- ✅ Quadratische Bilder für symmetrisches Layout
- ✅ Konsistente Farbpalette über alle 3 Bilder
- ✅ Hochauflösende Bilder für Retina-Displays
- ✅ Komprimiere Bilder vor Upload (z.B. mit TinyPNG)

## 🚀 Verwendung

### Beispiel 1: Hauptfirma + Partner-Logos

```
[Partner A]  [Hauptfirma]  [Partner B]
  Logo 1        Logo          Logo 2
```

### Beispiel 2: Zertifizierungen + Hauptlogo

```
[ISO 9001]  [Firmenloge]  [TÜV SÜD]
```

### Beispiel 3: Produkt-Highlights

```
[Solarmodul]  [Firmenloge]  [Speicher]
```

## 🔍 Fehlerbehandlung

### Bild nicht gefunden

```python
# intro_screen.py prüft automatisch:
if image_left_path.exists():
    img_left_base64 = get_image_base64(image_left_path)
    if img_left_base64:
        st.markdown(f'<img src="data:image/png;base64,{img_left_base64}" ...>')
```

### Datei zu groß

- Admin-Panel zeigt Fehlermeldung
- Upload wird abgebrochen
- Alte Einstellung bleibt erhalten

### Ungültiges Format

- Nur PNG, JPG, JPEG erlaubt
- File-Uploader filtert automatisch

## ✨ Button-Effekte auch im Intro

Alle Buttons im Intro-Bildschirm haben jetzt die gleichen **Shimmer + Pulse Effekte** wie im Rest der App:

### Implementierte Effekte

- ✅ **Shimmer-Animation**: Glänzender Sweep-Effekt bei Hover
- ✅ **Pulse-Animation**: Primary Buttons pulsieren bei Hover
- ✅ **Transform-Effekte**: `translateY(-3px)` Lift-Effekt
- ✅ **Enhanced Shadows**: Dynamische Schatten-Verstärkung
- ✅ **Disabled State**: Keine Animationen bei deaktivierten Buttons

### CSS-Implementierung (intro_screen.py, Zeilen 145-267)

```css
/* Shimmer-Effekt */
button::before {
    content: '';
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    left: -100%;
    transition: left 0.5s ease;
}

button:hover::before {
    left: 100%;
}

/* Pulse-Animation */
@keyframes introPulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.02); }
}

button[type="primary"]:hover {
    animation: introPulse 2s ease-in-out infinite;
}
```

### Abgedeckte Button-Typen

- `.stButton button` - Standard Streamlit Buttons
- `button[data-testid="baseButton-primary"]` - Primary Buttons
- `button[data-testid="baseButton-secondary"]` - Secondary Buttons
- `.stForm button[type="submit"]` - Form Submit Buttons (Login/Registrierung)
- `div[data-baseweb="button"]` - Base-Web Buttons

## 📊 Technische Details

### Dateigrößen-Limits

| Bild | Max. Größe | Grund |
|------|-----------|-------|
| Hauptbild | 5MB | Große Anzeige, zentrale Position |
| Seitenbilder | 2MB | Kleinere Anzeige, Ladezeit-Optimierung |

### Browser-Kompatibilität

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile Browsers (responsive Layout)

### Performance

- Bilder werden als Base64 im HTML eingebettet
- Lazy Loading bei großen Bildern
- CSS-Animationen mit Hardware-Beschleunigung
- Float-Animation: 3s infinite (optimiert für smooth 60fps)

## 🐛 Bekannte Limitierungen

1. **Dateigröße**: Bei sehr großen Bildern (>5MB) kann Upload fehlschlagen
2. **Base64-Encoding**: Erhöht HTML-Größe um ca. 33%
3. **Mobile View**: Seitenbilder werden auf kleinen Screens möglicherweise untereinander angezeigt
4. **Float-Animation**: Läuft kontinuierlich (kann nicht pausiert werden)

## 🔮 Zukünftige Erweiterungen

### Geplante Features

- [ ] Drag & Drop Upload im Admin-Panel
- [ ] Bild-Editor (Zuschneiden, Drehen, Filter)
- [ ] Mehrere Bildsets (z.B. Tag/Nacht-Modus)
- [ ] GIF-Animation Support
- [ ] Video als Seitenbild-Option
- [ ] Animationsgeschwindigkeit anpassbar
- [ ] Mehr Layout-Varianten (2-Bilder, 4-Bilder, Karussell)

## 📞 Support

Bei Fragen oder Problemen:

1. Überprüfe diese Dokumentation
2. Prüfe die Konsole auf Fehler (F12)
3. Kontrolliere Dateipfade in `intro_settings.json`
4. Validiere Bildformate und -größen

---

**Letzte Aktualisierung**: 2025-01-23  
**Version**: 1.0.0  
**Autor**: GitHub Copilot  
**Status**: ✅ Produktionsbereit
