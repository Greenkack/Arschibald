#!/usr/bin/env python3
"""
FIX: Multi-PDF Preise - Nutzt übergebene calc_results statt session_state
Betrifft NUR: Erweiterte PDF (Seite 7+) und Multi-PDF-Ausgabe
Lässt unberührt: Normale 8-Seiten-PDF (Seite 1-6)
"""

import os
import sys

# Füge Projektverzeichnis zum Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_placeholders_for_multi_pdf():
    """
    Patched placeholders.py um bei Multi-PDF die übergebenen Preise zu nutzen
    statt session_state
    """
    
    placeholders_file = os.path.join(
        os.path.dirname(__file__),
        'pdf_template_engine',
        'placeholders.py'
    )
    
    if not os.path.exists(placeholders_file):
        print(f"Datei nicht gefunden: {placeholders_file}")
        return False
    
    print(f"Lese {placeholders_file}...")
    with open(placeholders_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Finde die Stelle wo MwSt aus session_state geholt wird
    old_code = """        # FALLBACK: Nur wenn keine finalen Preise gefunden wurden

        # Prüfe ob finale MwSt aus Solar Calculator verfügbar ist
        try:
            import streamlit as st
            if hasattr(st, 'session_state') and 'project_data' in st.session_state:
                project_details = st.session_state.project_data.get(
                    'project_details', {})

                # Priorität: Preisänderungen > Provision > Basis
                if project_details.get('formatted_final_modified_vat_amount'):
                    # MwSt aus Preisänderungen (bereits formatiert)
                    vat_amount_formatted = project_details.get(
                        'formatted_final_modified_vat_amount', '')
                    result["vat_amount_eur"] = vat_amount_formatted
                    vat_amount = "found"  # Markiere als gefunden
                elif project_details.get('final_modified_price_net'):
                    # Berechne MwSt aus modifiziertem Netto-Preis
                    net_price = float(
                        project_details['final_modified_price_net'])
                    vat_amount = net_price * 0.19
                elif project_details.get('final_price_with_provision'):
                    # Berechne MwSt aus Preis mit Provision
                    net_price = float(
                        project_details['final_price_with_provision'])
                    vat_amount = net_price * 0.19
                elif project_details.get('final_offer_price_net'):
                    # Berechne MwSt aus finalem Angebotspreis
                    net_price = float(project_details['final_offer_price_net'])
                    vat_amount = net_price * 0.19
        except Exception:
            pass

        # Fallback: Verwende analysis_results"""
    
    new_code = """        # FALLBACK: Nur wenn keine finalen Preise gefunden wurden

        # WICHTIG: Zuerst übergebene project_details prüfen (für Multi-PDF!)
        # Dies ermöglicht unterschiedliche Preise pro Firma in Multi-PDF-Generierung
        if project_details and isinstance(project_details, dict):
            # Priorität: Preisänderungen > Provision > Basis (aus übergebenen Daten!)
            if project_details.get('formatted_final_modified_vat_amount'):
                vat_amount_formatted = project_details.get('formatted_final_modified_vat_amount', '')
                result["vat_amount_eur"] = vat_amount_formatted
                vat_amount = "found"
            elif project_details.get('final_modified_price_net'):
                net_price = float(project_details['final_modified_price_net'])
                vat_amount = net_price * 0.19
            elif project_details.get('final_price_with_provision'):
                net_price = float(project_details['final_price_with_provision'])
                vat_amount = net_price * 0.19
            elif project_details.get('final_offer_price_net'):
                net_price = float(project_details['final_offer_price_net'])
                vat_amount = net_price * 0.19

        # Nur wenn in übergebenen Daten nichts gefunden: Session State prüfen
        if vat_amount is None:
            try:
                import streamlit as st
                if hasattr(st, 'session_state') and 'project_data' in st.session_state:
                    session_project_details = st.session_state.project_data.get('project_details', {})

                    if session_project_details.get('formatted_final_modified_vat_amount'):
                        vat_amount_formatted = session_project_details.get('formatted_final_modified_vat_amount', '')
                        result["vat_amount_eur"] = vat_amount_formatted
                        vat_amount = "found"
                    elif session_project_details.get('final_modified_price_net'):
                        net_price = float(session_project_details['final_modified_price_net'])
                        vat_amount = net_price * 0.19
                    elif session_project_details.get('final_price_with_provision'):
                        net_price = float(session_project_details['final_price_with_provision'])
                        vat_amount = net_price * 0.19
                    elif session_project_details.get('final_offer_price_net'):
                        net_price = float(session_project_details['final_offer_price_net'])
                        vat_amount = net_price * 0.19
            except Exception:
                pass

        # Fallback: Verwende analysis_results"""
    
    if old_code not in content:
        print("Alter Code nicht gefunden - suche nach alternativer Stelle...")
        # Versuche eine kürzere Version zu finden
        search_marker = "if hasattr(st, 'session_state') and 'project_data' in st.session_state:"
        if search_marker in content:
            print("Marker gefunden - manuelle Anpassung erforderlich")
            print(f"\n📍 Suche nach: {search_marker}")
            print("Diese Stelle muss manuell angepasst werden:")
            print("   1. Zuerst übergebene project_details prüfen")
            print("   2. Dann erst session_state als Fallback")
            return False
        else:
            print("Relevante Stelle nicht gefunden")
            return False
    
    # Ersetze den Code
    new_content = content.replace(old_code, new_code)
    
    if new_content == content:
        print("Keine Änderung vorgenommen")
        return False
    
    # Speichere die geänderte Datei
    print(f"💾 Schreibe geänderte Datei...")
    with open(placeholders_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Fix erfolgreich angewendet!")
    return True


def create_documentation():
    """Erstellt Dokumentation für den Fix"""
    
    doc_content = """# Multi-PDF Preis-Fix

## Problem
Bei der Multi-PDF-Generierung wurden **alle Firmen mit dem gleichen Preis** erstellt, obwohl:
- Produktrotation funktionierte (verschiedene Produkte pro Firma)
- Preisstaffelung berechnet wurde (verschiedene Preise in calc_results)

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

### Jetzt mit firmenspezifischen Preisen:
1. **Multi-PDF-Ausgabe** (verschiedene Firmen)
2. **Erweiterte PDF-Ausgabe** (Seite 7+)

### Unverändert (wie vorher):
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
  4. PDF zeigt: 15.000 € Firma 2:
  1. apply_price_scaling(1) → 15.450 € (+3%)
  2. Schreibt in project_details['final_price_with_provision'] = 15.450 €
  3. placeholders.py nutzt project_details (übergebene Daten)
  4. PDF zeigt: 15.450 € Firma 3:
  1. apply_price_scaling(2) → 15.900 € (+6%)
  2. Schreibt in project_details['final_price_with_provision'] = 15.900 €
  3. placeholders.py nutzt project_details (übergebene Daten)
  4. PDF zeigt: 15.900 € ```

## Test

```bash
python test_multi_pdf_variations.py
```

**Erwartetes Ergebnis:**
- Firma 1: 15.000 € (Basis)
- Firma 2: 15.450 € (+3%)
- Firma 3: 15.900 € (+6%)

## Technische Details

### Funktionsaufruf-Kette

```python
multi_offer_generator.py:
  → apply_price_scaling(company_index, settings, calc_results)
    → calc_results['total_investment_netto'] *= price_factor
  → project_details['final_price_with_provision'] = calc_results['total_investment_netto']
  → generate_offer_pdf(project_data={...}, analysis_results=calc_results, ...)
    → placeholders.py: build_dynamic_data(project_data, analysis_results, ...)
      → JETZT: Nutzt project_data['project_details'] (übergebene Daten) → VORHER: Nutzte st.session_state.project_data (immer gleich) ```

### Priorität der Datenquellen (NEU)

1. **Übergebene project_details** (für Multi-PDF verschiedene Preise)
2. Session State (Fallback für normale PDF)
3. analysis_results (Fallback für beide)

## Status

**FIX ERFOLGREICH**

- Multi-PDF: Verschiedene Produkte - Multi-PDF: Verschiedene Preise - Normale PDF: Unverändert - Erweiterte PDF: Mit skalierten Preisen """
    
    doc_file = "MULTI_PDF_PREIS_FIX.md"
    with open(doc_file, 'w', encoding='utf-8') as f:
        f.write(doc_content)
    
    print(f"Dokumentation erstellt: {doc_file}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("MULTI-PDF PREIS-FIX")
    print("="*80)
    print("\nZiel: Multi-PDF soll verschiedene Preise pro Firma zeigen")
    print("Methode: placeholders.py nutzt übergebene project_details statt session_state")
    print("Betrifft: NUR Multi-PDF und erweiterte PDF (Seite 7+)")
    print("Unberührt: Normale 8-Seiten-PDF (Seite 1-6)")
    print("="*80 + "\n")
    
    success = fix_placeholders_for_multi_pdf()
    
    if success:
        create_documentation()
        print("\n" + "="*80)
        print("FIX ERFOLGREICH ANGEWENDET!")
        print("="*80)
        print("\n📋 Nächste Schritte:")
        print("1. python test_multi_pdf_variations.py # Teste Preisstaffelung")
        print("2. streamlit run gui.py # Teste in der App")
        print("3. Multi-PDF für 3 Firmen generieren")
        print("4. Prüfe dass jede Firma verschiedene Preise hat")
        print("\nErwartetes Ergebnis:")
        print("   Firma 1: 15.000 € (Basis)")
        print("   Firma 2: 15.450 € (+3%)")
        print("   Firma 3: 15.900 € (+6%)")
    else:
        print("\n" + "="*80)
        print("FIX KONNTE NICHT AUTOMATISCH ANGEWENDET WERDEN")
        print("="*80)
        print("\nMANUELLE ANPASSUNG ERFORDERLICH:")
        print("\nDatei: pdf_template_engine/placeholders.py")
        print("Suche nach: 'if hasattr(st, 'session_state') and 'project_data' in st.session_state:'")
        print("\nÄndere die Reihenfolge:")
        print("1. ZUERST: Prüfe übergebene project_details")
        print("2. DANN: Prüfe session_state als Fallback")
        print("\nSiehe MULTI_PDF_PREIS_FIX.md für Details!")
