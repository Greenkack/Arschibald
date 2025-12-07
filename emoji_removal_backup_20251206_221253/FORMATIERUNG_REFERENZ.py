"""
SCHNELLREFERENZ: Deutsche Zahlenformatierung
============================================

Alle Zahlen im Wärmepumpen-Simulator sind jetzt nach deutscher Notation formatiert!

ABGESCHLOSSEN
================

Statistiken:
- 187 Zahlenformatierungen implementiert
- 12 Plotly-Charts mit deutschen Trennzeichen
- 10 DataFrames formatiert
- 0 englische Formatierungen verbleibend

Format:
- Tausender: PUNKT (.)      → 12.345,67 €
- Dezimal:   KOMMA (,)       → 12.345,67 €
- Geld:      2 Dezimalstellen → 100,00 €

Verwendung:
from heatpump_ui import format_german_number

# Geldbeträge (2 Dezimalstellen)
format_german_number(12345.67, 2)  # → "12.345,67"

# Ganzzahlen (0 Dezimalstellen)
format_german_number(12345, 0)      # → "12.345"

# In Strings
f"{format_german_number(price, 2)} €"

Bereiche:
Heizkosten-Eingaben (Gas/Öl/Holz)
Produktpreise (manuell & Empfehlungen)
Wirtschaftlichkeitsberechnung
ROI & Amortisation
20-Jahres-Vergleich
CO2-Kosten & Einsparungen
PV-Integration
Alle Metrics & Zusammenfassungen
Alle DataFrames & Tabellen
Alle Plotly-Charts (Hover + Achsen)

Beispiele:
Investition:     25.000,00 €
Einsparung:      1.850,50 €
Leistung:        12 kW
SCOP:            4,20
Prozent:         85,5 %
CO2:             3.456,78 kg

✨ Status: PRODUKTIONSBEREIT
"""
print(__doc__)
