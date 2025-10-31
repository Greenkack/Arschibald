# Solar Calculator Enhancements - Zusammenfassung

## Implementierte Verbesserungen

### 1. ✅ Wechselrichter Berechnungsart korrigiert

- **Problem**: Berechnungsart bei Wechselrichtern war leer
- **Lösung**: Überprüfung ergab, dass alle Wechselrichter bereits "Stück" als `calculate_per` haben
- **Status**: Bereits korrekt implementiert

### 2. ✅ Manuelle Provision hinzugefügt

- **Implementierung**: Neues Provisionsfeld im Solar Calculator
- **Features**:
  - Eingabefeld für Provision in Prozent (0-100%)
  - Berechnung basiert auf dem finalen Angebotspreis (Nettobetrag)
  - Anzeige der Provisionsberechnung nur wenn Provision > 0
  - Endpreis mit Provision wird prominent angezeigt
  - Daten werden in `st.session_state.project_data['project_details']` gespeichert
- **Verhalten**:
  - Wenn Provision = 0: Keine Änderung am Endpreis
  - Wenn Provision > 0: Neuer Endpreis = Nettobetrag + (Nettobetrag × Provision%)

### 3. ✅ Rabatte & Aufpreise in Solar Calculator verschoben

- **Von**: `analysis.py` (Ergebnisse & Dashboard)
- **Nach**: `solar_calculator.py`
- **Implementierte Felder**:
  - **Rabatte & Nachlässe**:
    - Rabatt (%) - Prozentualer Rabatt auf Bruttobetrag
    - Pauschale Rabatte (€) - Feste Rabattbeträge
  - **Aufpreise & Zusatzkosten**:
    - Aufpreis (%) - Prozentualer Aufpreis auf Bruttobetrag
    - Sonderkosten (€) - Besondere Zusatzkosten (z.B. Gerüst, Kran)
    - Sonstiges (€) - Sonstige Kosten oder Anpassungen

### 4. ✅ Bruttobetrag-basierte Berechnung

- **Basis**: Alle Rabatte und Aufpreise werden auf den **Bruttobetrag** angewendet
- **Berechnungsreihenfolge**:
  1. Grundpreis (Brutto inkl. MwSt)
  2. Falls Provision vorhanden: Brutto + Provision
  3. Rabatte abziehen (% und €)
  4. Aufpreise hinzufügen (% und €)
  5. Neue MwSt berechnen basierend auf finalem Preis
- **Vorteil**: MwSt passt sich automatisch an modifizierten Preis an

## Technische Details

### Session State Integration

Alle neuen Werte werden in `st.session_state.project_data['project_details']` gespeichert:

**Provision:**

- `provision_percent`
- `provision_amount`
- `final_price_with_provision`
- `formatted_provision`
- `formatted_final_with_provision`

**Rabatte & Aufpreise:**

- `discount_percent`, `rebates_eur`
- `surcharge_percent`, `special_costs_eur`, `miscellaneous_eur`
- `total_discounts`, `total_surcharges`
- `final_modified_price`, `modified_net_price`, `modified_vat_amount`
- Formatierte Versionen für PDF-Generierung

### UI/UX Verbesserungen

- **Klare Struktur**: Provision → Rabatte & Aufpreise → Finaler Endpreis
- **Bedingte Anzeige**: Berechnungen werden nur angezeigt wenn Werte > 0
- **Deutsche Formatierung**: Alle Preise in deutschem Format (1.234,56 €)
- **Hilfe-Texte**: Erklärungen für alle Eingabefelder
- **Visuelle Trennung**: Markdown-Trennlinien zwischen Bereichen

### Kompatibilität

- **Rückwärtskompatibel**: Bestehende Funktionen bleiben unverändert
- **PDF-Integration**: Alle neuen Werte stehen für PDF-Generierung zur Verfügung
- **Fallback-Verhalten**: Wenn keine Modifikationen vorgenommen werden, bleibt alles beim ursprünglichen Preis

## Entfernte Funktionen

- **analysis.py**: Rabatt- und Aufpreisfelder entfernt
- **Ersetzt durch**: Hinweis, dass diese Funktionen jetzt im Solar Calculator verfügbar sind

## Nächste Schritte

Die Implementierung ist vollständig und einsatzbereit. Alle Anforderungen wurden erfüllt:

1. ✅ Wechselrichter haben korrekte Berechnungsart ("Stück")
2. ✅ Manuelle Provision implementiert (nur Endpreis-Verknüpfung)
3. ✅ Rabatte & Aufpreise in Solar Calculator verschoben
4. ✅ Bruttobetrag-basierte Berechnung mit automatischer MwSt-Anpassung

Die Lösung ist produktionsreif und kann sofort verwendet werden.
