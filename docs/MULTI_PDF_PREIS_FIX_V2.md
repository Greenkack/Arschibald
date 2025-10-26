# 🔧 Multi-PDF Preis-Fix V2 - VOLLSTÄNDIG

## Problem
Nach dem ersten Fix waren die Preise **IMMER NOCH gleich** in allen PDFs!

## Ursache gefunden
Der erste Fix hat nur die **MwSt** angepasst, aber nicht die **HAUPT-Preise**!

`placeholders.py` hatte ZWEI Stellen wo Preise gesetzt werden:
1. ✅ MwSt-Berechnung (Zeile ~2870) - BEREITS gefixt
2. ❌ Haupt-Preis-Berechnung (Zeile ~4640-4661) - **ÜBERSCHREIBT** den korrekten Preis!

## Die beiden Fixes

### Fix 1: Fallback-Reihenfolge (Zeile ~4735-4748)

**VORHER:**
```python
for candidate in (
    project_details.get("final_modified_price_net"),
    project_details.get("final_price_netto"),
    project_details.get("total_investment_netto"),  # Nicht skaliert!
    analysis_results.get("total_investment_netto"),  # Auch nicht skaliert!
):
```

**NACHHER:**
```python
for candidate in (
    project_details.get("final_modified_price_net"),
    project_details.get("final_offer_price_net"),  # MULTI-PDF: Skalierte Preise! ✅
    project_details.get("final_price_with_provision"),  # MULTI-PDF: Skalierte Preise! ✅
    project_details.get("final_price_netto"),
    project_details.get("final_price_net"),  # MULTI-PDF: Skalierte Preise! ✅
    project_details.get("total_investment_netto"),
    analysis_results.get("total_investment_netto"),  # Fallback nur wenn project_details nichts hat
):
```

### Fix 2: Überschreib-Schutz (Zeile ~4661)

**VORHER:**
```python
final_net_value = max(base_net_value + addons_net_value - discount_net_value + surcharge_net_value, 0.0)
result['final_end_preis_formatted'] = fmt_number(final_net_value, 2, "€")
# ❌ ÜBERSCHREIBT IMMER - auch wenn schon korrekt aus project_details gesetzt!
```

**NACHHER:**
```python
final_net_value = max(base_net_value + addons_net_value - discount_net_value + surcharge_net_value, 0.0)
# WICHTIG: NUR überschreiben wenn noch nicht gesetzt (für Multi-PDF!)
# Wenn project_details.final_offer_price_net bereits gesetzt ist, NICHT überschreiben!
if not result.get('final_end_preis_formatted') or result.get('final_end_preis_formatted') == '0,00 €':
    result['final_end_preis_formatted'] = fmt_number(final_net_value, 2, "€")
# ✅ Bewahrt den korrekten Preis aus project_details!
```

## Ablauf VORHER (falsch)

```
1. _alias_value() setzt result['final_end_preis_formatted'] 
   → AUS project_details.get('final_offer_price_net')
   → 21.000 € (Firma 2, +5%) ✅

2. Später: Neuberechnung aus simple_brutto_value
   →  final_net_value = base_net + addons - discounts
   → result['final_end_preis_formatted'] = fmt_number(final_net_value, 2, "€")
   → ÜBERSCHREIBT mit 20.000 € ❌

3. PDF zeigt: 20.000 € (falsch - nicht skaliert!)
```

## Ablauf NACHHER (richtig)

```
1. _alias_value() setzt result['final_end_preis_formatted']
   → AUS project_details.get('final_offer_price_net')
   → 21.000 € (Firma 2, +5%) ✅

2. Später: Neuberechnung prüft ZUERST
   → if not result.get('final_end_preis_formatted'):
   → NEIN, ist schon gesetzt!
   → ÜBERSCHREIBT NICHT ✅

3. PDF zeigt: 21.000 € (richtig - skaliert!)
```

## Test

```bash
python debug_multi_pdf_price_flow.py
```

**Erwartetes Ergebnis:**
```
Firma 1: 20.000 € (Basis, +0%)
Firma 2: 21.000 € (+5%)
Firma 3: 22.000 € (+10%)
```

## Änderungen

**Datei:** `pdf_template_engine/placeholders.py`

**2 Stellen geändert:**
1. Zeile ~4735-4748: Priorisiert `final_offer_price_net` (skaliert)
2. Zeile ~4661: Überschreibt NICHT wenn schon gesetzt

## Status

✅ **JETZT SOLLTE ES FUNKTIONIEREN!**

- Firma 1: Modul A + 20.000 €
- Firma 2: Modul B + 21.000 € (+5%)
- Firma 3: Modul C + 22.000 € (+10%)

**Teste jetzt in der App mit echten PDFs!** 🎯
