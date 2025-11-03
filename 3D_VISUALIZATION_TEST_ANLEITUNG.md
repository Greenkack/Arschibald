# 3D-Visualisierung - Test-Anleitung

## Schnelltest (5 Minuten)

### 1. Automatischer Test
```bash
python test_3d_visualization_fixes.py
```

**Erwartetes Ergebnis:**
```
✅ TEST 1 BESTANDEN: Alle Traufhöhen korrekt!
✅ TEST 2 BESTANDEN: Modul-Platzierung funktioniert!
✅ TEST 3 BESTANDEN: Modul-Konstanten sind korrekt!
✅ TEST 4 BESTANDEN: BuildingDims funktioniert!

🎉 ALLE TESTS BESTANDEN! 🎉
```

---

## Manueller Test in der App (10 Minuten)

### Test 1: Traufhöhe (3m statt 6m)

1. **Starte die App:**
   ```bash
   streamlit run gui.py
   ```

2. **Navigiere zur 3D-Visualisierung:**
   - Menü: "3D PV-Visualisierung"

3. **Prüfe Standard-Traufhöhe:**
   - Sidebar → "Basis-Einstellungen"
   - Feld "Traufhöhe (m)" sollte **3.0** anzeigen (nicht 6.0!)
   - ✅ **PASS:** Wert ist 3.0
   - ❌ **FAIL:** Wert ist 6.0 oder anders

4. **Erstelle Visualisierung:**
   - Button "🎨 3D-Visualisierung erstellen/aktualisieren"
   - Gebäude sollte **niedriger** aussehen als vorher

---

### Test 2: Modul-Platzierung (korrekte Abstände)

1. **Setze Gebäudegröße:**
   - Länge: 10m
   - Breite: 6m
   - Traufhöhe: 3m

2. **Setze Modulanzahl:**
   - Gehe zum Solarcalculator
   - Setze z.B. 20 Module

3. **Erstelle Visualisierung:**
   - Zurück zur 3D-Visualisierung
   - Button "🎨 3D-Visualisierung erstellen/aktualisieren"

4. **Prüfe Modul-Platzierung:**
   - ✅ Module sollten **zentriert** auf dem Dach sein
   - ✅ **Randabstände** sollten sichtbar sein (ca. 50cm)
   - ✅ Module sollten **gleichmäßig verteilt** sein
   - ✅ **Keine Überlappungen**

5. **Prüfe Konsolen-Ausgabe:**
   - Sollte zeigen: "✓ X Module aus PlacementManager gerendert!"
   - Oder: Warnmeldung wenn zu viele Module

---

### Test 3: Kein doppelter Visualisierer

1. **Erstelle Visualisierung:**
   - Button "🎨 3D-Visualisierung erstellen/aktualisieren"

2. **Prüfe Anzahl der Visualisierungen:**
   - ✅ **PASS:** Nur EINE 3D-Visualisierung sichtbar
   - ❌ **FAIL:** Zwei oder mehr Visualisierungen erscheinen

3. **Klicke mehrmals auf den Button:**
   - Visualisierung sollte sich aktualisieren
   - ✅ **PASS:** Immer noch nur EINE Visualisierung
   - ❌ **FAIL:** Mehrere Visualisierungen stapeln sich

---

### Test 4: PDF-Screenshot

1. **Erstelle Visualisierung:**
   - Button "🎨 3D-Visualisierung erstellen/aktualisieren"

2. **Erstelle Screenshot:**
   - Scrolle nach unten zu "Export"
   - Button "📸 Screenshot für PDF erstellen"

3. **Prüfe Ergebnis:**
   - ✅ Download-Button erscheint
   - ✅ Meldung: "📄 Screenshot für PDF-Seite 6 gespeichert!"
   - ✅ Erfolgsmeldung: "✓ Screenshot erstellt und für PDF vorbereitet!"

4. **Teste PDF-Export:**
   - Gehe zur PDF-Erstellung
   - Erstelle PDF
   - Öffne PDF und gehe zu Seite 6
   - ✅ **PASS:** Screenshot ist auf Seite 6 sichtbar
   - ❌ **FAIL:** Kein Screenshot oder falsche Position

---

### Test 5: Aufständerung Sichtbarkeit

1. **Wähle Flachdach:**
   - Dachform: "Flachdach"

2. **Wähle Aufständerung:**
   - Sidebar → "Modul-Belegung"
   - Aufständerungstyp: "Süd" (15° Neigung)

3. **Erstelle Visualisierung:**
   - Button "🎨 3D-Visualisierung erstellen/aktualisieren"

4. **Prüfe Aufständerung:**
   - ✅ Module sollten **schräg** stehen (nicht flach)
   - ✅ Module sollten **höher** über dem Dach sein (Gestell sichtbar)
   - ✅ Neigung sollte **deutlich erkennbar** sein

5. **Teste verschiedene Aufständerungen:**
   - "Ost-West": Module sollten alternierend nach Ost/West geneigt sein
   - "Süd-Ost": Module sollten nach Süd-Ost geneigt sein
   - "Individuell": Eigene Werte sollten angewendet werden

---

### Test 6: Modulanzahl-Synchronisation

1. **Setze Modulanzahl im Solarcalculator:**
   - Gehe zum Solarcalculator
   - Setze z.B. 25 Module
   - Speichere/Berechne

2. **Gehe zur 3D-Visualisierung:**
   - Menü: "3D PV-Visualisierung"

3. **Prüfe Konsolen-Ausgabe:**
   - Sollte zeigen: "✓ Modulanzahl aus analysis_results: 25"
   - Oder: "✓ Modulanzahl aus project_data: 25"

4. **Erstelle Visualisierung:**
   - Button "🎨 3D-Visualisierung erstellen/aktualisieren"

5. **Prüfe Status-Metriken:**
   - Rechte Spalte → "Status"
   - "Gewählte Module" sollte **25** anzeigen
   - "Platzierte Module" sollte **≤ 25** anzeigen (abhängig von Dachgröße)

---

## Erweiterte Tests (Optional)

### Test 7: Verschiedene Dachformen

Teste mit folgenden Dachformen:
- ✅ Flachdach
- ✅ Satteldach
- ✅ Satteldach mit Gaube
- ✅ Walmdach
- ✅ Krüppelwalmdach
- ✅ Pultdach
- ✅ Zeltdach

**Für jede Dachform prüfen:**
- Dach wird korrekt dargestellt
- Module werden auf dem Dach platziert
- Keine Löcher oder Fehler im Dach

---

### Test 8: Verschiedene Gebäudegrößen

Teste mit folgenden Größen:
- Klein: 8m x 5m
- Mittel: 10m x 6m
- Groß: 15m x 10m
- Sehr groß: 20m x 12m

**Für jede Größe prüfen:**
- Module passen auf das Dach
- Randabstände werden eingehalten
- Zentrierung ist korrekt

---

### Test 9: Zu viele Module

1. **Setze kleine Gebäudegröße:**
   - Länge: 8m
   - Breite: 5m

2. **Setze viele Module:**
   - z.B. 50 Module

3. **Erstelle Visualisierung:**
   - Konsole sollte Warnung zeigen:
     ```
     ⚠️ WARNUNG: Nur X von 50 Modulen passen auf das Dach!
     ```

4. **Prüfe Visualisierung:**
   - Nur die Module die passen sollten angezeigt werden
   - Keine Überlappungen
   - Status-Metrik "Fehlende Module" sollte > 0 sein

---

## Fehlersuche

### Problem: Tests schlagen fehl

**Lösung 1: Dependencies prüfen**
```bash
pip install -r requirements.txt
```

**Lösung 2: Python-Version prüfen**
```bash
python --version  # Sollte 3.10+ sein
```

**Lösung 3: Cache leeren**
```bash
streamlit cache clear
```

---

### Problem: Visualisierung lädt nicht

**Lösung 1: Browser-Cache leeren**
- Strg + Shift + R (Windows/Linux)
- Cmd + Shift + R (Mac)

**Lösung 2: Andere Browser testen**
- Chrome, Firefox, Edge

**Lösung 3: Konsole prüfen**
- F12 → Console Tab
- Fehler notieren und melden

---

### Problem: Module werden nicht angezeigt

**Lösung 1: Modulanzahl prüfen**
- Solarcalculator → Modulanzahl setzen
- Speichern/Berechnen

**Lösung 2: Konsolen-Ausgabe prüfen**
- Terminal wo Streamlit läuft
- Suche nach Fehlermeldungen

**Lösung 3: Session State zurücksetzen**
- Sidebar → "Reset (Auto-Belegung)"
- Oder: App neu starten

---

## Checkliste

### Vor dem Test
- [ ] App läuft ohne Fehler
- [ ] Solarcalculator hat Daten
- [ ] Browser ist aktuell

### Nach dem Test
- [ ] Alle 6 Haupttests durchgeführt
- [ ] Ergebnisse dokumentiert
- [ ] Fehler gemeldet (falls vorhanden)

---

## Ergebnis-Dokumentation

### Test-Protokoll

**Datum:** _____________
**Tester:** _____________
**App-Version:** _____________

| Test | Status | Bemerkungen |
|------|--------|-------------|
| 1. Traufhöhe | ☐ Pass ☐ Fail | |
| 2. Modul-Platzierung | ☐ Pass ☐ Fail | |
| 3. Kein doppelter Visualisierer | ☐ Pass ☐ Fail | |
| 4. PDF-Screenshot | ☐ Pass ☐ Fail | |
| 5. Aufständerung | ☐ Pass ☐ Fail | |
| 6. Modulanzahl-Sync | ☐ Pass ☐ Fail | |

**Gesamtergebnis:** ☐ Alle Tests bestanden ☐ Einige Tests fehlgeschlagen

**Zusätzliche Bemerkungen:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

---

**Erstellt:** 2025-01-03
**Version:** 1.0
