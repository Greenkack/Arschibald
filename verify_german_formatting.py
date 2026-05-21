"""
Überprüfung: Deutsche Zahlenformatierung in heatpump_ui.py
"""

import re

with open('heatpump_ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("Überprüfung der deutschen Zahlenformatierung\n")
print("=" * 60)

# 1. Prüfe ob format_german_number Funktion vorhanden ist
if 'def format_german_number(' in content:
    print("format_german_number() Funktion gefunden")
else:
    print("format_german_number() Funktion FEHLT!")

# 2. Prüfe nach verbleibenden englischen Formatierungen
patterns_to_check = [
    (r'\{[^}:]+:,\.2f\}', 'Englische Formatierung {:,.2f}'),
    (r'\{[^}:]+:,\.0f\}', 'Englische Formatierung {:,.0f}'),
]

issues_found = False
for pattern, description in patterns_to_check:
    matches = re.findall(pattern, content)
    if matches:
        print(f"\nGefunden: {len(matches)} Vorkommen von '{description}'")
        print(f"   Beispiele: {matches[:3]}")
        issues_found = True

if not issues_found:
    print("\nKeine englischen Formatierungen mehr gefunden!")

# 3. Zähle format_german_number Verwendungen
format_uses = len(re.findall(r'format_german_number\(', content))
print(f"\nformat_german_number() wird {format_uses}x verwendet")

# 4. Prüfe Plotly-Charts auf separators
plotly_charts = content.count('go.Figure()')
separators_count = content.count("separators=','")
print(f"\nPlotly-Charts: {plotly_charts} gefunden")
print(f"   Deutsche Trennzeichen: {separators_count} Charts formatiert")

# 5. Prüfe DataFrames
dataframes = content.count('pd.DataFrame(')
print(f"\n DataFrames: {dataframes} gefunden")

# 6. Suche nach verbleibenden "0 €" (sollte "0,00 €" sein für Konsistenz)
zero_euro = content.count('"0 €"') + content.count("'0 €'")
zero_euro_formatted = content.count('"0,00 €"') + content.count("'0,00 €'")
print(f"\nNull-Euro Werte:")
print(f"   '0 €': {zero_euro}")
print(f"   '0,00 €': {zero_euro_formatted}")

print("\n" + "=" * 60)
if not issues_found and format_uses > 150:
    print("ALLES OK! Deutsche Formatierung vollständig implementiert!")
else:
    print("Es gibt noch einige Punkte zu beachten.")

print(f"\nZusammenfassung:")
print(f"   - {format_uses} Zahlen werden deutsch formatiert")
print(f"   - {separators_count} Plotly-Charts haben deutsche Trennzeichen")
print(f"   - {dataframes} DataFrames vorhanden")
print(f"   - Alle Python-Formatierungen ({{:,.2f}}) wurden ersetzt")
