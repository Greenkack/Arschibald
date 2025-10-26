# 🔧 Multi-PDF Preis-Fix

## Problem
Bei der Multi-PDF-Generierung wurden **alle Firmen mit dem gleichen Preis** erstellt, obwohl:
- ✅ Produktrotation funktionierte (verschiedene Produkte pro Firma)
- ✅ Preisstaffelung berechnet wurde (verschiedene Preise in calc_results)

**Ursache:** `placeholders.py` holte Preise IMMER aus `st.session_state` statt aus den übergebenen `project_details`.

## Lösung

### Geänderte Datei
- `pdf_template_engine/placeholders.py`

### Änderung
**VORHER:**
```python
# Prüft NUR session_state
if hasattr(st, 'session_state') and 'project_data' in st.session_state:
    project_details = st.session_state.project_data.get('project_details', {})
    # Nutzt session_state project_details
```

**NACHHER:**
```python
# Prüft ZUERST übergebene project_details (für Multi-PDF!)
if project_details and isinstance(project_details, dict):
    # Nutzt übergebene project_details (mit firmenspezifischen Preisen)
    ...

# NUR als Fallback: session_state
if vat_amount is None:
    if hasattr(st, 'session_state') and 'project_data' in st.session_state:
        session_project_details = st.session_state.project_data.get('project_details', {})
        # Nutzt session_state nur wenn in übergebenen Daten nichts gefunden
```

## Betroffene PDFs

### ✅ Jetzt mit firmenspezifischen Preisen:
1. **Multi-PDF-Ausgabe** (verschiedene Firmen)
2. **Erweiterte PDF-Ausgabe** (Seite 7+)

### ✅ Unverändert (wie vorher):
1. **Normale 8-Seiten-PDF** (Seite 1-6)
   - Nutzt weiterhin session_state
   - Keine Änderung am Verhalten

## Ablauf

### Multi-PDF-Generierung

```
Firma 1:
  1. apply_price_scaling(0) → 15.000 €
  2. Schreibt in project_details['final_price_with_provision'] = 15.000 €
  3. placeholders.py nutzt project_details (übergebene Daten)
  4. PDF zeigt: 15.000 € ✅

Firma 2:
  1. apply_price_scaling(1) → 15.450 € (+3%)
  2. Schreibt in project_details['final_price_with_provision'] = 15.450 €
  3. placeholders.py nutzt project_details (übergebene Daten)
  4. PDF zeigt: 15.450 € ✅

Firma 3:
  1. apply_price_scaling(2) → 15.900 € (+6%)
  2. Schreibt in project_details['final_price_with_provision'] = 15.900 €
  3. placeholders.py nutzt project_details (übergebene Daten)
  4. PDF zeigt: 15.900 € ✅
```

## Test

```bash
python test_multi_pdf_variations.py
```

**Erwartetes Ergebnis:**
- ✅ Firma 1: 15.000 € (Basis)
- ✅ Firma 2: 15.450 € (+3%)
- ✅ Firma 3: 15.900 € (+6%)

## Technische Details

### Funktionsaufruf-Kette

```python
multi_offer_generator.py:
  → apply_price_scaling(company_index, settings, calc_results)
    → calc_results['total_investment_netto'] *= price_factor
  → project_details['final_price_with_provision'] = calc_results['total_investment_netto']
  → generate_offer_pdf(project_data={...}, analysis_results=calc_results, ...)
    → placeholders.py: build_dynamic_data(project_data, analysis_results, ...)
      → JETZT: Nutzt project_data['project_details'] (übergebene Daten) ✅
      → VORHER: Nutzte st.session_state.project_data (immer gleich) ❌
```

### Priorität der Datenquellen (NEU)

1. **Übergebene project_details** (für Multi-PDF verschiedene Preise)
2. Session State (Fallback für normale PDF)
3. analysis_results (Fallback für beide)

## Status

✅ **FIX ERFOLGREICH**

- Multi-PDF: Verschiedene Produkte ✅
- Multi-PDF: Verschiedene Preise ✅
- Normale PDF: Unverändert ✅
- Erweiterte PDF: Mit skalierten Preisen ✅
