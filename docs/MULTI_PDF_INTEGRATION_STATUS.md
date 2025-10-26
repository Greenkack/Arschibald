# MULTI-PDF & WÄRMEPUMPEN INTEGRATION - DOKUMENTATION

## ✅ Was wurde erstellt?

### 📁 `multi_pdf_integration.py` (558 Zeilen)

**Kompakte Integration** der Multi-PDF & Wärmepumpen-Logik aus `repair_pdf/`:

#### **TEIL 1: Multi-PDF Kernlogik** (Zeilen 1-310)

- ✅ `init_multi_pdf_session_state()` - Session State Verwaltung
- ✅ `load_customer_data_from_project()` - Automatische Kundendatenübernahme aus Projekt/Bedarfsanalyse
- ✅ `render_multi_pdf_customer_input()` - Kundendaten-UI mit Auto-Import
- ✅ `render_multi_pdf_company_selection()` - Unbegrenzte Firmenauswahl (2-20+)
- ✅ `render_multi_pdf_settings()` - Produktrotation & Preisstaffelung
- ✅ Erweiterte PDF-Optionen pro Firma + Master-Toggle

#### **TEIL 2: Wärmepumpen-Integration** (Zeilen 311-380)

- ✅ `init_heatpump_session_state()` - WP Session State
- ✅ `render_heatpump_integration_toggle()` - WP Ein/Aus mit Status-Anzeige
- ✅ Automatische Übernahme aus Bedarfsanalyse

#### **TEIL 3: Helper-Funktionen** (Zeilen 381-450)

- ✅ `create_multi_pdf_zip()` - ZIP-Erstellung für alle PDFs
- ✅ `calculate_rotation_products()` - Produktrotations-Engine (Skelett)
- ✅ `apply_price_increment()` - Preisstaffelung

#### **TEIL 4: Haupt-UI** (Zeilen 451-558)

- ✅ `render_multi_pdf_generator()` - Komplette 4-Schritt-UI
- ✅ Integration aller Komponenten

---

## 🎯 Nächste Schritte

### 1. **Vervollständigung der Produktrotations-Logik**

```python
# TODO in multi_pdf_integration.py Zeile 432-435:
def calculate_rotation_products(...):
    # Implementierung aus repair_pdf/multi_offer_generator.py extrahieren
```

**Quelle:** `repair_pdf/multi_offer_generator.py` Zeilen 200-350

### 2. **PDF-Generierungs-Pipeline**

```python
# TODO in render_multi_pdf_generator() Zeile 547-550:
# Implementierung der Batch-PDF-Generierung mit Fortschrittsanzeige
```

**Quelle:** `repair_pdf/multi_offer_generator.py` Zeilen 573-800

### 3. **Wärmepumpen-Berechnung Integration**

Bestehende Module nutzen:

- ✅ `calculations_heatpump.py` - bereits vorhanden
- ✅ `heatpump_pricing.py` - bereits vorhanden
- ✅ `heatpump_ui.py` - bereits vorhanden

**Integration:** Einfach importieren und verwenden!

---

## 📊 Architektur-Übersicht

```
┌─────────────────────────────────────────────────────┐
│           MULTI-PDF INTEGRATION                     │
│                                                      │
│  ┌──────────────────┐    ┌───────────────────┐    │
│  │  Kundendaten     │───►│  Firmenauswahl    │    │
│  │  (Auto-Import)   │    │  (2-20+ Firmen)   │    │
│  └──────────────────┘    └───────────────────┘    │
│           │                       │                 │
│           ▼                       ▼                 │
│  ┌──────────────────┐    ┌───────────────────┐    │
│  │  Einstellungen   │    │  Wärmepumpe       │    │
│  │  • Rotation      │    │  (Optional)       │    │
│  │  • Preise        │    └───────────────────┘    │
│  └──────────────────┘             │                │
│           │                       │                 │
│           └───────────┬───────────┘                │
│                       ▼                             │
│            ┌──────────────────┐                    │
│            │  PDF Generierung │                    │
│            │  (Batch-Prozess) │                    │
│            └──────────────────┘                    │
│                       │                             │
│                       ▼                             │
│            ┌──────────────────┐                    │
│            │  ZIP Download    │                    │
│            └──────────────────┘                    │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 So verwenden Sie das Modul

### In `gui.py` oder separater Seite integrieren

```python
# In gui.py importieren:
try:
    from multi_pdf_integration import render_multi_pdf_generator
    MULTI_PDF_AVAILABLE = True
except ImportError:
    MULTI_PDF_AVAILABLE = False

# Als Seite hinzufügen:
if selected_page == "multi_offer" and MULTI_PDF_AVAILABLE:
    render_multi_pdf_generator()
```

### Oder als separate Streamlit-Page

```python
# pages/5_📊_Multi_Angebote.py
from multi_pdf_integration import render_multi_pdf_generator

render_multi_pdf_generator()
```

---

## 📋 Checkliste für vollständige Integration

### ✅ Bereits erledigt

- [x] Multi-PDF Session State Management
- [x] Automatische Kundendatenübernahme
- [x] Firmenauswahl-UI (unbegrenzt)
- [x] Erweiterte PDF-Optionen pro Firma
- [x] Master-Toggle für alle erweiterten PDFs
- [x] Einstellungen UI (Rotation + Preise)
- [x] Wärmepumpen-Toggle
- [x] Helper-Funktionen (ZIP, Preise)
- [x] Haupt-UI-Struktur (4 Schritte)

### 🔄 Noch zu tun

- [ ] Produktrotations-Logik implementieren (aus repair_pdf extrahieren)
- [ ] PDF-Batch-Generierung implementieren (aus repair_pdf extrahieren)
- [ ] Fortschrittsanzeige mit tqdm
- [ ] Fehlerbehandlung pro Firma
- [ ] In gui.py/Menü integrieren
- [ ] Tests mit echten Firmendaten

---

## 🎨 Features nach Priorität

### 🔴 **KRITISCH (für MVP):**

1. ✅ Kundendaten-Übernahme aus Projekt
2. ✅ Firmenauswahl 2-20+
3. ⏳ Basis-PDF-Generierung (ohne Rotation)
4. ⏳ ZIP-Download

### 🟡 **WICHTIG (für Vollversion):**

1. ⏳ Produktrotation (linear)
2. ⏳ Preisstaffelung
3. ⏳ Erweiterte PDFs (ab Seite 7)
4. ⏳ Fortschrittsanzeige

### 🟢 **NICE-TO-HAVE:**

1. ⏳ Wärmepumpen-Integration vollständig
2. ⏳ Zufällige Produktrotation
3. ⏳ Kategorie-spezifische Rotation
4. ⏳ Custom Preisfaktoren pro Firma

---

## 💡 Nächster Schritt

**Priorität 1:** Vervollständigen Sie die PDF-Generierungs-Pipeline:

```bash
# Extrahieren Sie aus repair_pdf/multi_offer_generator.py:
# - Zeilen 573-800: generate_multi_offers() Methode
# - Zeilen 200-350: Produktrotations-Logik
# - Zeilen 900-1000: PDF-Batch-Erstellung

# Fügen Sie in multi_pdf_integration.py ein:
# - Funktion: generate_single_offer_pdf()
# - Funktion: batch_generate_offers()
# - Integration in render_multi_pdf_generator()
```

---

## 📖 Referenz-Dokumentation

Siehe auch:

- `MULTI_PDF_WAERMEPUMPEN_DOKU.md` - Vollständige Architektur-Doku
- `repair_pdf/multi_offer_generator.py` - Original-Implementierung (1.256 Zeilen)
- `calculations_heatpump.py` - Wärmepumpen-Berechnungen
- `heatpump_pricing.py` - Wärmepumpen-Preise
- `heatpump_ui.py` - Wärmepumpen-UI

---

**Stand:** 18. Oktober 2025
**Version:** 1.0 - Kompakte Integration erstellt
**Autor:** GitHub Copilot
