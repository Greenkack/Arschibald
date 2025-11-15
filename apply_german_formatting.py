"""
Skript zum Ersetzen aller Zahlenformatierungen in heatpump_ui.py
von englischer zu deutscher Notation
"""

import re

# Lese die Datei
with open('heatpump_ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Zähler für Ersetzungen
replacements = 0

# Pattern 1: :,.2f → format_german_number(value, 2)
# Findet: {variable:,.2f}
pattern1 = r'\{([^}:]+):,\.2f\}'
matches1 = re.findall(pattern1, content)
print(f"Gefunden: {len(matches1)} Vorkommen von {{x:,.2f}}")

for match in set(matches1):  # set() um Duplikate zu vermeiden
    old = f"{{{match}:,.2f}}"
    new = f"{{format_german_number({match}, 2)}}"
    content = content.replace(old, new)
    replacements += 1

# Pattern 2: :,.0f → format_german_number(value, 0)
# Findet: {variable:,.0f}
pattern2 = r'\{([^}:]+):,\.0f\}'
matches2 = re.findall(pattern2, content)
print(f"Gefunden: {len(matches2)} Vorkommen von {{x:,.0f}}")

for match in set(matches2):
    old = f"{{{match}:,.0f}}"
    new = f"{{format_german_number({match}, 0)}}"
    content = content.replace(old, new)
    replacements += 1

# Pattern 3: :.2f → format_german_number(value, 2)
# Findet: {variable:.2f} (ohne Komma-Separator)
pattern3 = r'\{([^}:]+):\.2f\}'
matches3 = re.findall(pattern3, content)
print(f"Gefunden: {len(matches3)} Vorkommen von {{x:.2f}}")

for match in set(matches3):
    old = f"{{{match}:.2f}}"
    new = f"{{format_german_number({match}, 2)}}"
    content = content.replace(old, new)
    replacements += 1

# Pattern 4: :.0f → format_german_number(value, 0)
# Findet: {variable:.0f} (ohne Komma-Separator)
pattern4 = r'\{([^}:]+):\.0f\}'
matches4 = re.findall(pattern4, content)
print(f"Gefunden: {len(matches4)} Vorkommen von {{x:.0f}}")

for match in set(matches4):
    old = f"{{{match}:.0f}}"
    new = f"{{format_german_number({match}, 0)}}"
    content = content.replace(old, new)
    replacements += 1

# Spezialfälle manuell prüfen und ersetzen
# "0 €" sollte "0,00 €" werden
content = content.replace('"0 €"', '"0,00 €"')
content = content.replace("'0 €'", "'0,00 €'")

# Schreibe die aktualisierte Datei
with open('heatpump_ui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nErfolgreich {replacements} verschiedene Patterns ersetzt!")
print("Die Datei heatpump_ui.py wurde aktualisiert.")
