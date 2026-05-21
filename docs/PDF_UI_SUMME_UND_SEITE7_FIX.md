# PDF UI Summe und Seite 7 Final Price Fix

## Probleme behoben

### 1. ❌ **Problem**: PDF UI zeigt Summe mit 0,00 €

**Ursache**: `base_cost` war 0, weil `calculation_results` nicht gesetzt waren

**✅ Lösung**: PDF UI verwendet jetzt Solar Calculator Preise als Fallback

```python
# Fallback: Verwende Solar Calculator Netto-Preis als base_cost
if base_cost == 0.0:
    # Suche nach verschiedenen Netto-Preis Keys
    for key in ['net_total_amount', 'total_net_price', 'base_net_price']:
        if key in project_details and project_details[key] > 0:
            base_cost = float(project_details[key])
            break
    
    # Fallback: Berechne Netto aus Brutto
    if base_cost == 0.0 and 'final_price_with_provision' in project_details:
        brutto_price = float(project_details['final_price_with_provision'])
        base_cost = brutto_price / 1.19  # Netto-Preis
```

### 2. ❌ **Problem**: Seite 7 `final_end_preis` Platzhalter nicht mit dynamischem Wert verknüpft

**Ursache**: Platzhalter existierte in seite7.yml, aber nicht im PLACEHOLDER_MAPPING

**✅ Lösung**:

1. **PLACEHOLDER_MAPPING erweitert**:

   ```python
   "final_end_preis": "final_end_preis_formatted",
   ```

2. **Dynamischer Wert aus Solar Calculator**:

   ```python
   # 1. Priorität: Formatierter finaler Preis mit Provision
   if 'formatted_final_with_provision' in project_details:
       final_end_preis = str(project_details['formatted_final_with_provision'])
   
   # 2. Fallback: Numerischer finaler Preis mit Provision
   elif 'final_price_with_provision' in project_details:
       price_value = float(project_details['final_price_with_provision'])
       final_end_preis = f"{price_value:,.2f} €".replace(',', 'X').replace('.', ',').replace('X', '.')
   ```

## Geänderte Dateien

### pdf_ui.py

- **Zeile ~119**: `base_cost` Berechnung erweitert um Solar Calculator Fallback
- Verwendet jetzt `net_total_amount` oder berechnet Netto aus `final_price_with_provision`

### pdf_template_engine/placeholders.py

- **PLACEHOLDER_MAPPING**: `"final_end_preis": "final_end_preis_formatted"` hinzugefügt
- **build_dynamic_data()**: Neue Sektion für `final_end_preis_formatted` vor `return result`

## Testergebnisse

✅ **Test 1**: PDF UI base_cost Fix funktioniert (27.310,50 €)  
✅ **Test 2**: Seite 7 final_end_preis Fix funktioniert (32.500,75 €)  

## Funktionsweise

### PDF UI Summen-Berechnung

```
Solar Calculator → net_total_amount (27.310,50 €)
                ↓
PDF UI → base_cost = 27.310,50 €
       ↓
Rabatte/Aufschläge angewendet
       ↓
final_price = berechneter Endpreis (nicht mehr 0,00 €)
```

### Seite 7 Endpreis-Anzeige

```
Solar Calculator → formatted_final_with_provision ("32.500,75 €")
                ↓
placeholders.py → final_end_preis_formatted = "32.500,75 €"
                ↓
Seite 7 PDF → final_end_preis zeigt "32.500,75 €"
```

## Prioritätshierarchie

### PDF UI base_cost

1. `calculation_results.base_matrix_price_netto`
2. `session_state.base_matrix_price_netto`
3. **NEU**: `project_details.net_total_amount` (Solar Calculator)
4. **NEU**: `project_details.final_price_with_provision / 1.19` (Netto aus Brutto)

### Seite 7 final_end_preis

1. **NEU**: `project_details.formatted_final_with_provision`
2. **NEU**: `project_details.final_price_with_provision` (formatiert)
3. Fallback: andere Preis-Keys

## Auswirkungen

- **PDF UI**: Zeigt jetzt echte Summen statt 0,00 €
- **Seite 7**: Zeigt echten Endpreis aus Solar Calculator
- **Zahlungsmodalitäten**: Verwenden bereits den korrekten Preis (vorheriger Fix)
- **Robustheit**: Funktioniert auch ohne `calculation_results`

## Status: ✅ BEHOBEN

Beide Probleme sind behoben:

1. PDF UI Summe zeigt echten Preis aus Solar Calculator
2. Seite 7 final_end_preis zeigt echten Endpreis mit Provision
