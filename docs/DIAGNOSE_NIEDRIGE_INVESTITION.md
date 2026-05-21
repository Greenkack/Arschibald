# 🔍 Diagnose: Niedrige Investitionsbeträge (z.B. 700€)

## Problem-Übersicht

Wenn in den Logs die Meldung erscheint:
```
DEBUG: Amortisation verwendet Fallback total_investment_netto: 700.0
```

...bedeutet das, dass die Investitionsberechnung **NICHT richtig funktioniert** hat.

---

## ✅ Normale Investitionsbeträge

Typische Photovoltaik-Anlagen kosten:
- **Klein (3-5 kWp)**: 8.000 - 15.000 €
- **Mittel (6-10 kWp)**: 15.000 - 25.000 €
- **Groß (>10 kWp)**: 25.000 - 50.000+ €

**Ein Betrag von 700€ ist unrealistisch niedrig!**

---

## 🔎 Ursachen-Analyse

### 1. **Preismatrix nicht geladen**

**Symptom**: `base_matrix_price_netto = 0€`

**Lösung**:
- Admin-Panel öffnen → "Preismatrizen & Kalkulation"
- Sicherstellen dass für gewählte kWp-Größe ein Preis existiert
- Beispiel: 10 kWp sollte ~18.000-22.000€ kosten

```python
# In calculations.py Zeile ~3774:
total_investment_netto = subtotal_netto - one_time_bonus_eur
```

### 2. **Sehr hoher Bonus abgezogen**

**Symptom**: `one_time_bonus_eur` ist zu hoch (z.B. 19.300€ bei 20.000€ Investition)

**Lösung**:
- Admin-Panel → "Globale Konstanten"
- `one_time_bonus_eur` prüfen und anpassen
- Typischer Bonus: 0-2.000€

### 3. **Zusatzkosten negativ**

**Symptom**: `total_additional_costs_netto` ist negativ

**Lösung**:
- Prüfen Sie alle Aufpreis-Felder in der Produktdatenbank
- Keine negativen Werte eintragen (außer bei Rabatten)

### 4. **Projekt-Snapshot fehlerhaft**

**Symptom**: Alte/fehlerhafte Projekt-Daten geladen

**Lösung**:
- Neue Berechnung durchführen (nicht alten Snapshot laden)
- Projektdaten neu erfassen im Solar Calculator

---

## 🛠️ Debugging-Schritte

### Schritt 1: Konsole beobachten

Neue Debug-Ausgaben zeigen jetzt mehr Details:

```
✓ Amortisation verwendet final_offer_price_net: 18500.00€
```
oder
```
⚠️ Amortisation verwendet Fallback total_investment_netto: 700.00€
   ⚠️ WARNUNG: Investitionsbetrag sehr niedrig! Prüfen Sie:
      - base_matrix_price_netto: 0.00€          ← PROBLEM!
      - total_additional_costs_netto: 700.00€
      - subtotal_netto: 700.00€
      - one_time_bonus_eur: 0.00€
```

### Schritt 2: Werte überprüfen

**Im Solar Calculator:**
1. System-Größe (kWp) eingegeben?
2. Komponenten ausgewählt?
3. "Berechnen" Button geklickt?

**Im Admin-Panel:**
1. Preismatrix für gewählte Größe vorhanden?
2. Globale Konstanten korrekt?
3. Bonus nicht zu hoch?

### Schritt 3: Berechnungslog analysieren

Suchen Sie in der Konsole nach:
```python
# Zeile 3774 in calculations.py:
total_investment_netto = subtotal_netto - one_time_bonus_eur

# Sollte ergeben:
# subtotal_netto = 20.000€
# one_time_bonus_eur = 500€
# total_investment_netto = 19.500€ ✓
```

---

## 💡 Schnell-Checks

### ✅ Checklist für korrekte Berechnung:

- [ ] Preismatrix im Admin-Panel vollständig ausgefüllt
- [ ] System-Größe (kWp) > 0 eingegeben
- [ ] Module, Wechselrichter, ggf. Speicher ausgewählt
- [ ] "Berechnen" Button geklickt (nicht alter Snapshot)
- [ ] `base_matrix_price_netto > 5000€` (mindestens)
- [ ] `one_time_bonus_eur < 2000€` (maximal)
- [ ] Keine negativen Zusatzkosten

### ⚠️ Typische Fehler:

❌ Preismatrix leer → `base_matrix_price_netto = 0€`  
❌ Bonus zu hoch → `subtotal - bonus = negativ`  
❌ Alter Projekt-Snapshot → veraltete/fehlerhafte Daten  
❌ Keine Komponenten gewählt → nur Minimalpreis  

---

## 🎯 Sofort-Lösung

Falls Sie schnell weiterarbeiten müssen:

1. **Admin-Panel öffnen**
2. **Preismatrizen & Kalkulation**
3. **Für alle kWp-Größen Preise eintragen**:
   - 3 kWp: 9.000€
   - 5 kWp: 13.000€
   - 8 kWp: 18.000€
   - 10 kWp: 21.000€
   - 15 kWp: 30.000€

4. **Globale Konstanten prüfen**:
   - `one_time_bonus_eur`: max. 1.500€

5. **Neue Berechnung durchführen**

---

## 📊 Erwartete Konsolen-Ausgabe (Korrekt)

```
✓ Amortisation verwendet final_offer_price_net: 19850.00€
✓ ROI-Analyse: Jährlicher Benefit = 1850.00€
```

## 📊 Fehlerhafte Ausgabe

```
⚠️ Amortisation verwendet Fallback total_investment_netto: 700.00€
   ⚠️ WARNUNG: Investitionsbetrag sehr niedrig! Prüfen Sie:
      - base_matrix_price_netto: 0.00€          ← Hier liegt das Problem!
```

---

## 📞 Support

Wenn das Problem weiterhin besteht:
1. Konsolen-Log kopieren
2. Admin-Panel → Preismatrizen Screenshot
3. Verwendete kWp-Größe notieren
4. Support kontaktieren

---

**Hinweis**: Diese Diagnose-Datei hilft Ihnen, niedrige Investitionsbeträge schnell zu identifizieren und zu beheben.
