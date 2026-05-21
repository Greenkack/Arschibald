# 3D PV-Visualisierung - Schnellreferenz

## Tastenkombinationen & Interaktion

### 3D-Ansicht Navigation
- **Linke Maustaste + Ziehen:** Ansicht drehen
- **Rechte Maustaste + Ziehen:** Ansicht verschieben
- **Mausrad:** Zoom in/out
- **Doppelklick:** Ansicht zurücksetzen

### Modul-Interaktion
- **Hover über Modul:** Zeigt Modul-Details
- **Klick auf Modul:** Wählt Modul aus (wenn aktiviert)
- **Strg + Klick:** Mehrfachauswahl

---

## Schnellstart-Workflows

### Workflow 1: Einfache Planung (5 Min)
```
1. Gebäudedaten eingeben
   └─ Länge: 12m, Breite: 10m, Höhe: 3m
   
2. Dachform wählen
   └─ z.B. "Satteldach"
   
3. Optimierung starten
   └─ Ziel: "Ausgewogen"
   └─ Button: "🚀 Optimierung starten"
   
4. Screenshot exportieren
   └─ Format: PNG
   └─ Auflösung: Full HD
```

### Workflow 2: Verschattungs-Analyse (10 Min)
```
1. Basis-Konfiguration erstellen
   └─ Gebäude + Dachform eingeben
   
2. Verschattungs-Analyse aktivieren
   └─ ☑️ Verschattungs-Analyse aktivieren
   
3. Tageszeit einstellen
   └─ Slider: 12:00 Uhr (Mittag)
   
4. Jahreszeit wählen
   └─ "Sommer (21. Juni)"
   
5. Ergebnis prüfen
   └─ Grün = gut, Rot = schlecht
   
6. Andere Zeiten testen
   └─ Morgens: 8:00 Uhr
   └─ Abends: 18:00 Uhr
   └─ Winter: 21. Dezember
```

### Workflow 3: Ertrag optimieren (15 Min)
```
1. Ertrags-Heatmap aktivieren
   └─ ☑️ Ertrags-Heatmap aktivieren
   └─ Metrik: "Jahresertrag (kWh)"
   
2. Schwache Module identifizieren
   └─ Rote/Orange Module = niedriger Ertrag
   
3. Module manuell entfernen
   └─ Belegungsmodus: "Manuell"
   └─ Indizes eingeben: z.B. "0,5,10"
   
4. Optimierung durchführen
   └─ Ziel: "Maximaler Ertrag"
   └─ Button: "🚀 Optimierung starten"
   
5. Ertragsprognose prüfen
   └─ ☑️ Ertragsprognose aktivieren
   └─ Strompreis eingeben: 0.30 €/kWh
```

### Workflow 4: Vollständige Dokumentation (20 Min)
```
1. Optimale Konfiguration erstellen
   └─ Alle vorherigen Schritte
   
2. Multi-View Export
   └─ ☑️ Multi-View Export
   └─ Auflösung: HD (1600x1000)
   └─ Ergebnis: 4 Perspektiven als ZIP
   
3. 360° Animation
   └─ ☑️ 360° Animation exportieren
   └─ Frames: 36
   └─ Auflösung: Mittel (800x600)
   
4. Daten exportieren
   └─ ☑️ CSV Export (für Excel)
   └─ ☑️ JSON Export (für Backup)
   
5. 3D-Modell exportieren
   └─ ☑️ 3D-Modell exportieren
   └─ Format: STL (für CAD)
```

---

## Checkliste: Vor dem Export

### Basis-Prüfung
- [ ] Gebäudedimensionen korrekt?
- [ ] Dachform passend?
- [ ] Modulanzahl realistisch?
- [ ] Keine Kollisionswarnungen?

### Qualitäts-Prüfung
- [ ] Verschattungs-Analyse durchgeführt?
- [ ] Ertrags-Heatmap geprüft?
- [ ] Schwache Module entfernt?
- [ ] Optimierung durchgeführt?

### Export-Prüfung
- [ ] Richtige Auflösung gewählt?
- [ ] Alle benötigten Formate aktiviert?
- [ ] Dateinamen sinnvoll?
- [ ] Backup erstellt (JSON)?

---

## Häufige Einstellungen

### Einfamilienhaus (Standard)
```yaml
Gebäude:
  Länge: 12m
  Breite: 10m
  Höhe: 3m
  Dachform: Satteldach

Aufständerung:
  Typ: Süd
  Neigung: 30°

Module:
  Anzahl: ~20-30
  Leistung: ~8-12 kWp
```

### Mehrfamilienhaus
```yaml
Gebäude:
  Länge: 20m
  Breite: 15m
  Höhe: 9m
  Dachform: Flachdach

Aufständerung:
  Typ: Ost-West
  Neigung: 15°

Module:
  Anzahl: ~60-80
  Leistung: ~25-35 kWp
```

### Gewerbe
```yaml
Gebäude:
  Länge: 30m
  Breite: 20m
  Höhe: 4m
  Dachform: Flachdach

Aufständerung:
  Typ: Süd
  Neigung: 15°

Module:
  Anzahl: ~120-150
  Leistung: ~50-65 kWp
```

---

## Optimierungs-Tipps

### Maximaler Ertrag
1. ✅ Süd-Ausrichtung (Azimuth 0°)
2. ✅ Optimale Neigung (30-35° in Deutschland)
3. ✅ Verschattungsfreie Bereiche
4. ✅ Hochwertige Module (>20% Wirkungsgrad)
5. ❌ Keine Nord-Ausrichtung
6. ❌ Keine stark verschatteten Module

### Maximale Modulanzahl
1. ✅ Alle verfügbaren Flächen nutzen
2. ✅ Garage/Carport hinzufügen
3. ✅ Fassadenbelegung aktivieren
4. ✅ Minimale Abstände
5. ⚠️ Ertragsverluste akzeptieren
6. ⚠️ Höhere Installationskosten

### Eigenverbrauch optimieren
1. ✅ Ost-West-Ausrichtung
2. ✅ Mittlere Modulanzahl
3. ✅ Gleichmäßige Produktion über Tag
4. ✅ Kombination mit Speicher
5. ❌ Nicht zu viele Module (Überschuss)

---

## Fehlerbehebung Schnellhilfe

### Problem: Keine Module sichtbar
**Lösung:**
```
1. Prüfe Gebäudegröße (min. 8x5m)
2. Wähle andere Dachform
3. Aktiviere "Garage/Carport"
4. Aktualisiere Seite (F5)
```

### Problem: Kollisionswarnungen
**Lösung:**
```
1. Deaktiviere Kollisionserkennung
2. Nutze Optimierungs-Assistent
3. Vergrößere Gebäude
4. Reduziere Modulanzahl
```

### Problem: Export schlägt fehl
**Lösung:**
```
1. Reduziere Auflösung
2. Weniger Frames (bei Animation)
3. Erlaube Downloads im Browser
4. Versuche anderen Format
```

### Problem: Langsame Performance
**Lösung:**
```
1. Schließe andere Browser-Tabs
2. Deaktiviere Analysen
3. Reduziere Modulanzahl
4. Nutze niedrigere Auflösungen
```

---

## Tooltips-Übersicht

### Basis-Einstellungen
| Element | Tooltip |
|---------|---------|
| Gebäudelänge | Länge des Gebäudes in Metern |
| Gebäudebreite | Breite des Gebäudes in Metern |
| Traufhöhe | Höhe der Außenwände (Traufhöhe) |
| Dachform | Wählen Sie die Dachform Ihres Gebäudes |

### Modul-Belegung
| Element | Tooltip |
|---------|---------|
| Belegungsmodus | Automatisch: gleichmäßig verteilt. Manuell: einzelne Module entfernen |
| Aufständerungstyp | Wählen Sie die Ausrichtung für optimalen Ertrag |
| Azimuth | Ausrichtung: 0°=Süd, 90°=West, 180°=Nord, 270°=Ost |
| Neigung | Neigungswinkel: 0°=horizontal, 90°=vertikal |
| Garage/Carport | Fügt Garage hinzu, wenn Module nicht auf Hauptdach passen |
| Fassadenbelegung | Platziert Module an Südfassade bei Platzmangel |

### Erweiterte Kontrolle
| Element | Tooltip |
|---------|---------|
| Kollisionserkennung | Prüft auf Überschneidungen und zeigt Warnungen |
| Auswahl-Modus | Wählen Sie, wie Sie Module auswählen möchten |
| Modul-Index | Index des auszuwählenden Moduls (0 = erstes Modul) |

### Analyse
| Element | Tooltip |
|---------|---------|
| Optimierungs-Ziel | Max. Module / Max. Ertrag / Ausgewogen |
| Verschattungs-Analyse | Färbt Module basierend auf Verschattungsgrad |
| Tageszeit | Wählen Sie Tageszeit für Verschattungs-Analyse |
| Jahreszeit | Wählen Sie Jahreszeit für Sonnenstandsberechnung |
| Breitengrad | Breitengrad des Standorts (Standard: 51.0 für Deutschland) |
| Ertrags-Heatmap | Färbt Module basierend auf Ertragspotential |
| Ertragsprognose | Zeigt detaillierte Ertragsprognose |

### Export
| Element | Tooltip |
|---------|---------|
| Screenshot | Exportiert aktuelle Ansicht als Bild |
| Multi-View | Erstellt Screenshots aus 4 Perspektiven |
| 360° Animation | Erstellt 360° Rotation als GIF |
| 3D-Modell | Exportiert 3D-Modell (STL/GLTF/OBJ) |
| CSV Export | Exportiert Modul-Details als CSV |
| JSON Export | Exportiert Layout-Konfiguration als JSON |

---

## Keyboard Shortcuts (geplant)

```
Strg + S     = Screenshot speichern
Strg + E     = Export-Menü öffnen
Strg + O     = Optimierung starten
Strg + R     = Ansicht zurücksetzen
Strg + Z     = Rückgängig
Strg + Y     = Wiederholen
Leertaste    = Analyse pausieren/fortsetzen
Esc          = Auswahl aufheben
```

---

## Best Practices

### ✅ DO
- Präzise Gebäudedaten verwenden
- Mehrere Konfigurationen testen
- Verschattungs-Analyse durchführen
- Regelmäßig Backups erstellen (JSON)
- Dokumentation exportieren

### ❌ DON'T
- Unrealistische Dimensionen eingeben
- Kollisionswarnungen ignorieren
- Nur eine Konfiguration testen
- Ohne Analyse exportieren
- Zu hohe Auflösungen bei langsamer Hardware

---

## Kontakt & Support

**Dokumentation:** Siehe `3D_VISUALIZATION_USER_GUIDE.md`

**Tooltips:** Hover über UI-Elemente für Hilfe

**Updates:** Prüfen Sie regelmäßig auf neue Features

---

*Letzte Aktualisierung: November 2025*
