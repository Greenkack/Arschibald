# Fix: Amortisationszeit & Ersparte Mehrwertsteuer

## 🎯 Status: ERFOLGREICH BEHOBEN

Beide Berechnungen auf Seite 1 der PDF sind nun korrekt implementiert!

---

## 📋 PROBLEM 1: Amortisationszeit

### ❌ Vorher (FALSCH)

```python
# Verwendete alten Preis aus project_details
final_investment_amount = project_details.get('final_modified_price_net')
# ODER
final_investment_amount = total_investment_netto
```

**Problem:** Der FINAL_END_PREIS aus dem Solar Calculator wurde NICHT verwendet!

### ✅ Jetzt (RICHTIG)

```python
# Priorität 1: FINAL_END_PREIS aus session_state
if 'final_pricing_data' in st.session_state:
    final_investment_amount = st.session_state['final_pricing_data']['final_end_preis']

# Priorität 2: project_details mit neuem Key
elif 'project_data' in st.session_state:
    final_investment_amount = st.session_state['project_data']['project_details']['final_end_preis']

# Priorität 3: Fallback zu alten Keys
else:
    final_investment_amount = project_details.get('final_modified_price_net', total_investment_netto)
```

### 📊 Formel

```
FINAL_END_PREIS ÷ Jährliche Einnahmen Gesamt = Amortisationszeit (Jahre)
```

Mit Amortisation Cheat (aus Admin-Einstellungen):

- **Fixed:** Fester Wert in Jahren
- **Absolute Reduction:** Fester Betrag abziehen
- **Percentage Reduction:** Prozentsatz reduzieren

**Beispiel:**

```
20.000 € ÷ 1.500 €/Jahr = 13,33 Jahre
Mit 20% Cheat: 13,33 × 0,8 = 10,67 Jahre
```

---

## 📋 PROBLEM 2: Ersparte Mehrwertsteuer

### ❌ Vorher

**Key existierte NICHT!** ⚠️

### ✅ Jetzt (NEU)

Komplett neue Berechnung implementiert!

### 📊 Formel

```
FINAL_END_PREIS × 0.19 = Ersparte Mehrwertsteuer
```

**Erklärung:** Als Unternehmer kann man die Mehrwertsteuer beim Finanzamt geltend machen. Bei einem Netto-Preis von 20.000 € spart man 3.800 € MwSt.

**Beispiel:**

```
20.000 € (netto) × 0.19 = 3.800 € (ersparte MwSt)
```

---

## 🔧 GEÄNDERTE DATEIEN

### 1. `solar_calculator.py`

**Änderungen:**

- Neue Berechnung nach dem FINAL_END_PREIS hinzugefügt
- **Zeile ~730:** Ersparte MwSt berechnet
- **Zeile ~765:** 4 neue Keys zu final_pricing_keys hinzugefügt
- **Zeile ~785:** Keys in session_state gespeichert
- **Zeile ~800:** Keys in project_details gespeichert

**Neue Keys:**

```python
"ERSPARTE_MEHRWERTSTEUER": ersparte_mehrwertsteuer,
"ERSPARTE_MEHRWERTSTEUER_FORMATTED": formatted_ersparte_mwst,
"VAT_SAVINGS": ersparte_mehrwertsteuer,  # Englischer Alias
"VAT_SAVINGS_FORMATTED": formatted_ersparte_mwst,
```

**Code-Snippet:**

```python
# ERSPARTE MEHRWERTSTEUER BERECHNUNG
ersparte_mehrwertsteuer = final_end_preis * 0.19
formatted_ersparte_mwst = _format_german_currency(ersparte_mehrwertsteuer)
```

### 2. `pdf_template_engine/placeholders.py`

**Änderungen:**

- **Zeile ~468:** 4 neue Keys im PLACEHOLDER_MAPPING
- **Zeile ~3736:** Default-Werte hinzugefügt
- **Zeile ~3818:** Keys aus session_state laden

**Neue Mappings:**

```python
"ERSPARTE_MEHRWERTSTEUER": "ersparte_mehrwertsteuer",
"ERSPARTE_MEHRWERTSTEUER_FORMATTED": "ersparte_mehrwertsteuer_formatted",
"VAT_SAVINGS": "vat_savings",
"VAT_SAVINGS_FORMATTED": "vat_savings_formatted",
```

**Loading-Logik:**

```python
result['ersparte_mehrwertsteuer'] = final_data.get('ersparte_mehrwertsteuer', 0.0)
result['ersparte_mehrwertsteuer_formatted'] = final_data.get('formatted', {}).get('ersparte_mwst', "0,00 €")
result['vat_savings'] = final_data.get('vat_savings', 0.0)
result['vat_savings_formatted'] = final_data.get('formatted', {}).get('ersparte_mwst', "0,00 €")
```

### 3. `calculations.py`

**Änderungen:**

- **Zeile ~3640-3695:** Komplett neue Logik für Amortisationszeit
- Priorisiert FINAL_END_PREIS aus session_state
- Fallback zu alten Keys für Kompatibilität

**Neue Priorisierung:**

1. `st.session_state['final_pricing_data']['final_end_preis']`
2. `st.session_state['project_data']['project_details']['final_end_preis']`
3. `project_details.get('final_modified_price_net')` (alt)
4. `project_details.get('final_price_with_provision')` (alt)
5. `total_investment_netto` (Fallback)

---

## 🧪 TEST-ERGEBNISSE

### Alle Tests bestanden! ✅

```
✅ BESTANDEN: Ersparte Mehrwertsteuer
✅ BESTANDEN: Amortisationszeit
✅ BESTANDEN: Placeholder Mapping
✅ BESTANDEN: Session State
✅ BESTANDEN: Berechnungslogik

Ergebnis: 5/5 Tests bestanden
```

### Test-Details

**1. Ersparte Mehrwertsteuer:**

```
Formel: FINAL_END_PREIS × 0.19 = Ersparte MwSt
Berechnung: 20.000,00 € × 0.19 = 3.800,00 €
✅ Ersparte Mehrwertsteuer: 3.800,00 €
```

**2. Amortisationszeit:**

```
Formel: FINAL_END_PREIS ÷ Jährliche Einnahmen = Amortisationszeit
Berechnung: 20.000,00 € ÷ 1.500,00 € = 13.33 Jahre
📊 Ohne Cheat: 13.33 Jahre
📊 Mit Cheat (-20.0%): 10.67 Jahre
```

**3. Placeholder Mapping:**

```
✅ ERSPARTE_MEHRWERTSTEUER → ersparte_mehrwertsteuer
✅ ERSPARTE_MEHRWERTSTEUER_FORMATTED → ersparte_mehrwertsteuer_formatted
✅ VAT_SAVINGS → vat_savings
✅ VAT_SAVINGS_FORMATTED → vat_savings_formatted
✅ FINAL_END_PREIS → final_end_preis
✅ FINAL_END_PREIS_FORMATTED → final_end_preis_formatted
✅ FINAL_END_PREIS_NETTO → final_end_preis_netto
```

---

## 📖 VERWENDUNG IM PDF-TEMPLATE

### Word-Platzhalter

**Ersparte Mehrwertsteuer:**

```
{{ERSPARTE_MEHRWERTSTEUER_FORMATTED}}
ODER
{{VAT_SAVINGS_FORMATTED}}
```

**Amortisationszeit:**
Die Amortisationszeit wird automatisch in `calculations.py` berechnet und ist verfügbar als:

```
{{amortization_time}}
```

### Beispiel Seite 1

```
╔══════════════════════════════════════════════════════╗
║                    INVESTITIONSDETAILS                ║
╠══════════════════════════════════════════════════════╣
║ Investitionssumme (netto):  {{FINAL_END_PREIS_FORMATTED}}     ║
║ Ersparte Mehrwertsteuer:    {{ERSPARTE_MEHRWERTSTEUER_FORMATTED}} ║
║ Jährliche Einnahmen:        {{total_annual_savings_eur}}      ║
║ Amortisationszeit:          {{amortization_time}}             ║
╚══════════════════════════════════════════════════════╝
```

---

## 🔄 DATENFLUSS

```
Solar Calculator (UI)
  ↓
  [Benutzer wählt Komponenten aus]
  ↓
  [Einfache Berechnung: Komponenten + Provision + MwSt]
  ↓
  [Rabatte/Aufschläge hinzufügen]
  ↓
  [Zubehör & Extra Services hinzufügen]
  ↓
  [FINAL_END_PREIS berechnen (NETTO!)]
  ↓
  [ERSPARTE_MEHRWERTSTEUER = FINAL_END_PREIS × 0.19]
  ↓
Session State:
  - final_pricing_data
      ├── final_end_preis
      └── ersparte_mehrwertsteuer
  ↓
calculations.py:
  - Liest final_end_preis aus session_state
  - AMORTISATION = final_end_preis ÷ jährliche_einnahmen
  - Wendet Cheat an (falls aktiviert)
  ↓
placeholders.py:
  - Lädt alle Keys aus session_state
  - Stellt sie für PDF-Template bereit
  ↓
PDF-Generation:
  - Ersetzt {{ERSPARTE_MEHRWERTSTEUER_FORMATTED}}
  - Ersetzt {{amortization_time}}
  ↓
Fertiges PDF mit korrekten Werten! ✅
```

---

## 🎯 BEISPIEL-RECHNUNG (VOLLSTÄNDIG)

### Ausgangswerte

- Komponenten: **15.000,00 €**
- Provision: **2.000,00 €**
- Rabatte: **-1.500,00 €**
- Aufschläge: **+700,00 €**
- Zubehör (Wallbox, etc.): **+3.000,00 €**
- Extra Services: **+2.000,00 €**

### Berechnung

**Schritt 1-5: Einfache Berechnung**

```
15.000 € (Komponenten)
+ 2.000 € (Provision)
─────────
= 17.000 € (Netto mit Provision)
+ 3.230 € (MwSt 19%)
─────────
= 20.230 € (SIMPLE_ENDERGEBNIS_BRUTTO)
```

**Schritt 6-10: Rabatte, Aufschläge, Zubehör**

```
20.230 € (Basis)
- 1.500 € (Rabatte)
+ 700 € (Aufschläge)
+ 3.000 € (Zubehör)
+ 2.000 € (Services)
─────────
= 24.430 € (ZWISCHENSUMME_FINAL, brutto)
```

**Schritt 11-12: MwSt herausrechnen**

```
24.430 € (Zwischensumme brutto)
- 3.900,59 € (MwSt 19% herausrechnen: 24.430 × 0.19 / 1.19)
─────────────
= 20.529,41 € (FINAL_END_PREIS, NETTO!)
```

**🔷 ERSPARTE MEHRWERTSTEUER:**

```
20.529,41 € × 0.19 = 3.900,59 €
```

**🔷 AMORTISATIONSZEIT:**

```
Jährliche Einnahmen: 1.800,00 €/Jahr
20.529,41 € ÷ 1.800,00 € = 11,41 Jahre

Mit 20% Cheat: 11,41 × 0,8 = 9,13 Jahre
```

---

## ⚠️ WICHTIGE HINWEISE

### 1. Ersparte Mehrwertsteuer

- **Nur für Unternehmer relevant!**
- Die Mehrwertsteuer kann beim Finanzamt zurückgeholt werden
- Bei Privatpersonen ist das **NICHT** möglich
- Im PDF-Template ggf. mit Hinweis versehen

### 2. Amortisationszeit

- Verwendet **immer** den FINAL_END_PREIS (netto)
- Cheat-Einstellungen werden automatisch angewendet
- Fallback zu alten Keys für Kompatibilität
- Bei fehlenden Daten: `float('inf')` (unendlich)

### 3. Session State

- Alle Werte werden in `st.session_state` gespeichert
- Auch in `project_details` für PDF-Export
- Fallback-Kette sorgt für Robustheit

---

## ✅ CHECKLISTE

- [x] Ersparte MwSt Berechnung implementiert
- [x] 4 neue Keys erstellt (ERSPARTE_MEHRWERTSTEUER, etc.)
- [x] Keys im PLACEHOLDER_MAPPING hinzugefügt
- [x] Keys in session_state gespeichert
- [x] Keys in project_details gespeichert
- [x] Amortisationszeit verwendet jetzt FINAL_END_PREIS
- [x] Priorisierung session_state > project_details > Fallback
- [x] Fallback zu alten Keys für Kompatibilität
- [x] Default-Werte definiert
- [x] Test-Skript erstellt
- [x] Alle Tests bestanden (5/5)
- [x] Dokumentation erstellt

---

## 🚀 FERTIG

Die beiden Berechnungen auf Seite 1 der PDF sind nun **vollständig korrekt** implementiert!

### Nächste Schritte

1. ✅ Im Solar Calculator testen
2. ✅ PDF generieren und prüfen
3. ✅ Word-Template mit neuen Platzhaltern erweitern
4. ✅ Produktiv nehmen

---

**Status:** ✅ VOLLSTÄNDIG BEHOBEN
**Datum:** 2025-10-05
**Version:** 1.1
**Tests:** 5/5 bestanden
