# Feature: Auto-Auswahl von Produktdatenblättern im PDF-Generator

## Zusammenfassung

Produktdatenblätter der im Solar Calculator ausgewählten Produkte werden automatisch für die PDF-Generierung vorausgewählt. Der User kann die Auswahl jederzeit manuell anpassen oder auf die Auto-Auswahl zurücksetzen.

## Problem

Bisher musste der User manuell alle Produktdatenblätter auswählen, auch wenn die Produkte bereits im Solar Calculator konfiguriert wurden. Dies führte zu:

- ❌ Doppelter Arbeit
- ❌ Vergessenen Datenblättern
- ❌ Inkonsistenz zwischen Solar Calculator und PDF

## Lösung

### 1. Automatische Vorauswahl

Das System erkennt automatisch alle im Solar Calculator gewählten Produkte und markiert deren Datenblätter:

**Unterstützte Produkte:**

- ⭐ PV-Module (`selected_module_id`)
- ⭐ Wechselrichter (`selected_inverter_id`)
- ⭐ Batteriespeicher (`selected_battery_id`)
- ⭐ Leistungsoptimierer (`selected_optimizer_id`)
- ⭐ Wallboxen (`selected_wallbox_id`)
- ⭐ Carports (`selected_carport_id`)
- ⭐ Notstromversorgung (`selected_notstrom_id`)
- ⭐ Tierabwehrschutz (`selected_tierabwehr_id`)

### 2. Visuelle Kennzeichnung

Auto-ausgewählte Produkte werden mit einem ⭐ Stern-Icon markiert:

```
✨ 3 Produkt(e) aus dem Solar Calculator automatisch vorausgewählt (anpassbar)

☑ ⭐ Trina Solar Vertex S+ 425W (Modul)
☑ ⭐ Fronius Symo GEN24 10.0 Plus (Wechselrichter)
☑ ⭐ BYD Battery-Box Premium HVS 10.2 (Batteriespeicher)
☐ SMA Sunny Boy 5.0 (Wechselrichter)
```

### 3. Manuelle Anpassung

Der User kann jederzeit:

- ✅ Produkte abwählen (Checkbox deaktivieren)
- ✅ Zusätzliche Produkte hinzufügen (andere Checkboxen aktivieren)
- ✅ Zur Auto-Auswahl zurückkehren (🔄 Zurücksetzen Button)

### 4. Zurücksetzen-Funktion

Der "🔄 Zurücksetzen" Button stellt die ursprüngliche Auto-Auswahl wieder her:

- Alle manuellen Änderungen werden verworfen
- Nur die im Solar Calculator gewählten Produkte bleiben ausgewählt
- Nützlich nach versehentlichen Änderungen

## Technische Implementierung

### Datei: `pdf_ui.py` (Zeilen ~2706-2818)

#### Schritt 1: Produkt-IDs aus Solar Calculator sammeln

```python
# Get selected product IDs from Solar Calculator
auto_selected_product_ids = set()
project_details = st.session_state.get('project_data', {}).get('project_details', {})

# Collect all selected product IDs
selected_product_keys = [
    'selected_module_id',
    'selected_inverter_id',
    'selected_battery_id',
    # ... weitere Keys
]

for key in selected_product_keys:
    product_id = project_details.get(key)
    if product_id is not None and isinstance(product_id, int):
        auto_selected_product_ids.add(product_id)
```

#### Schritt 2: Initiale Auto-Auswahl

```python
# Initialize selected datasheets with auto-selection
if "selected_product_datasheets" not in st.session_state.pdf_inclusion_options:
    # First time: auto-select products from solar calculator
    st.session_state.pdf_inclusion_options["selected_product_datasheets"] = list(auto_selected_product_ids)
```

#### Schritt 3: Visuelle Kennzeichnung

```python
# Mark auto-selected products with icon
if product_id in auto_selected_product_ids:
    label = f"⭐ {product_name} ({product_type})"
else:
    label = f"{product_name} ({product_type})"
```

#### Schritt 4: Zurücksetzen-Button

```python
if st.button("🔄 Zurücksetzen", ...):
    st.session_state.pdf_inclusion_options["selected_product_datasheets"] = list(auto_selected_product_ids)
    st.success("✅ Auswahl auf Solar Calculator Produkte zurückgesetzt")
    st.rerun()
```

## User-Flow

### Szenario 1: Erster PDF-Export

1. User konfiguriert Produkte im Solar Calculator:
   - Modul: Trina Solar Vertex S+ 425W (ID: 15)
   - Wechselrichter: Fronius Symo GEN24 10.0 (ID: 23)
   - Batterie: BYD HVS 10.2 (ID: 42)

2. User öffnet PDF-Generator → "Erweiterte Ausgabe"

3. System zeigt:

   ```
   📄 Produktdatenblätter
   ✨ 3 Produkt(e) aus dem Solar Calculator automatisch vorausgewählt (anpassbar)
   
   ☑ ⭐ Trina Solar Vertex S+ 425W (Modul)
   ☑ ⭐ Fronius Symo GEN24 10.0 Plus (Wechselrichter)
   ☑ ⭐ BYD Battery-Box Premium HVS 10.2 (Batteriespeicher)
   ```

4. User klickt "PDF generieren" → Alle 3 Datenblätter werden automatisch angehängt ✅

### Szenario 2: Manuelle Anpassung

1. User will zusätzliches Datenblatt hinzufügen
2. Aktiviert Checkbox bei "SMA Sunny Boy 5.0"
3. Jetzt sind 4 Datenblätter ausgewählt
4. PDF wird mit 4 Datenblättern generiert ✅

### Szenario 3: Versehentliche Änderung

1. User hat mehrere Produkte abgewählt
2. Klickt "🔄 Zurücksetzen"
3. System stellt Auto-Auswahl wieder her
4. Nur Solar Calculator Produkte sind ausgewählt ✅

### Szenario 4: Keine Produkte im Solar Calculator

1. User hat noch keine Produkte konfiguriert
2. Produktdatenblätter-Expander zeigt:

   ```
   📄 Produktdatenblätter
   ℹ️ Keine Auto-Auswahl (Solar Calculator nicht konfiguriert)
   
   ☐ Trina Solar Vertex S+ 425W (Modul)
   ☐ Fronius Symo GEN24 10.0 Plus (Wechselrichter)
   ...
   ```

3. User muss manuell auswählen oder zuerst Solar Calculator konfigurieren

## Vorteile

### Für den User

- ⚡ **Schneller**: Keine manuelle Suche nach Produktdatenblättern
- 🎯 **Genauer**: Garantiert die richtigen Datenblätter
- 🔄 **Konsistent**: Immer synchron mit Solar Calculator
- 💡 **Intuitiv**: Klare visuelle Kennzeichnung (⭐)
- 🛡️ **Fehlersicher**: Keine vergessenen Datenblätter

### Für den Workflow

- ✅ Reduziert Klicks von ~10 auf ~1
- ✅ Vermeidet Inkonsistenzen zwischen Konfiguration und PDF
- ✅ Ermöglicht trotzdem vollständige Kontrolle
- ✅ Unterstützt komplexe Konfigurationen mit vielen Komponenten

## Edge Cases & Fehlerbehandlung

### 1. Produkt ohne Datenblatt

```python
# Nur Produkte MIT Datenblatt werden angezeigt
datasheet_path = _resolve_datasheet_path(product)
if datasheet_path:
    products_with_datasheets.append(product)
```

→ Produkte ohne Datenblatt erscheinen nicht in der Liste

### 2. Ungültige Produkt-ID

```python
if product_id is not None and isinstance(product_id, int):
    auto_selected_product_ids.add(product_id)
```

→ Nur valide Integer-IDs werden berücksichtigt

### 3. Produkt gelöscht aber noch im Solar Calculator

→ Auto-Auswahl wird ignoriert, da Produkt nicht in `products_with_datasheets` ist
→ Keine Fehlermeldung, System arbeitet mit verfügbaren Produkten

### 4. Session State fehlt

```python
project_details = st.session_state.get('project_data', {}).get('project_details', {})
```

→ Fallback auf leeres Dictionary, keine Auto-Auswahl, keine Fehler

## Testing

### Test 1: Auto-Auswahl funktioniert

1. Wähle Produkte im Solar Calculator
2. Öffne PDF-Generator
3. ✅ Prüfe: Produkte sind vorausgewählt mit ⭐

### Test 2: Manuelle Anpassung möglich

1. Deaktiviere ein vorausgewähltes Produkt
2. Aktiviere ein anderes Produkt
3. ✅ Prüfe: Änderungen bleiben erhalten

### Test 3: Zurücksetzen funktioniert

1. Ändere Auswahl manuell
2. Klicke "🔄 Zurücksetzen"
3. ✅ Prüfe: Original Auto-Auswahl wiederhergestellt

### Test 4: PDF enthält korrekte Datenblätter

1. Wähle Produkte aus (auto oder manuell)
2. Generiere PDF
3. ✅ Prüfe: Nur ausgewählte Datenblätter im PDF

### Test 5: Ohne Solar Calculator Konfiguration

1. Starte mit leerem Projekt
2. Öffne PDF-Generator
3. ✅ Prüfe: Keine Auto-Auswahl, alle Checkboxen leer

## Zukünftige Erweiterungen

### Idee 1: Smart-Vorschlag

System schlägt zusätzliche Datenblätter vor basierend auf:

- Kompatibilität (z.B. passende Optimierer für gewählte Module)
- Häufig kombinierte Produkte
- Firmen-Templates

### Idee 2: Kategorien-Filter

Ermögliche Auswahl nach Kategorien:

- [ ] Alle Module
- [ ] Alle Wechselrichter
- [ ] Alle Speicher

### Idee 3: Batch-Aktionen

- "Alle Solar Calculator Produkte"
- "Alle Zubehör"
- "Alles auswählen"
- "Alles abwählen"

## Betroffene Dateien

- ✅ `pdf_ui.py` (Zeilen ~2706-2818) - Hauptimplementierung
- ℹ️ Keine Änderungen an `pdf_generator.py` nötig (verwendet bereits `selected_product_datasheets`)
- ℹ️ Keine Datenbankänderungen nötig

## Wartung

- Wenn neue Produkt-Typen zum Solar Calculator hinzugefügt werden, müssen sie zu `selected_product_keys` hinzugefügt werden
- Format: `selected_<produkt_typ>_id`
- Beispiel für neuen Typ "Monitoring": `'selected_monitoring_id'`
