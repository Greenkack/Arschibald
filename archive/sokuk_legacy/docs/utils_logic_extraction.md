# utils.py — Logik-Extraktion

Kurzüberblick: Hilfsfunktionen mit zwei alten Platzhaltern (E-Mail-Validierung, Euro-Format) und drei neuen, fachlich relevanten CO2-Äquivalenzfunktionen für Bäume, Auto-km und Flüge.

## Funktionen und Verträge

- is_valid_email(email: str) -> bool
  - Placeholder: immer True. In produktiver Migration durch echte Regex prüfen.

- format_euro(amount: float) -> str
  - Placeholder: gibt formatierte Zeichenkette "{amount:.2f} € (Placeholder)" zurück.

- kwh_to_trees_equivalent(kwh_savings, tree_absorption_kg_co2_per_year, grid_co2_g_per_kwh) -> float
  - Formel: co2_saved_kg = (kwh_savings * grid_co2_g_per_kwh) / 1000; trees = co2_saved_kg / tree_absorption
  - Validierung: Gibt 0.0 zurück, wenn tree_absorption oder grid_co2 <= 0.

- kwh_to_car_km_equivalent(kwh_savings, car_co2_g_per_km, grid_co2_g_per_kwh) -> float
  - Formel: co2_saved_g = kwh_savings * grid_co2_g_per_kwh; km = co2_saved_g / car_co2_g_per_km
  - Validierung: 0.0, wenn car_co2 <= 0 oder grid_co2 <= 0.

- kwh_to_flights_equivalent(kwh_savings, flight_co2_kg_per_person, grid_co2_g_per_kwh) -> float
  - Formel: co2_saved_kg = (kwh_savings * grid_co2_g_per_kwh) / 1000; flights = co2_saved_kg / flight_co2
  - Validierung: 0.0, wenn flight_co2 <= 0 oder grid_co2 <= 0.

## Nutzung im Projekt

- calculations.py kann diese Funktionen verwenden, um aus simulierten Einsparungen (kWh) begleitende Storytelling-KPIs abzuleiten:
  - co2_equivalent_trees_per_year
  - co2_equivalent_car_km_per_year
  - co2_equivalent_flights_per_year (falls benötigt)

## Migration zu TypeScript

- Implementierung 1:1 mit number-Guards und klaren Units; Rückgabe als number.
- Centralized config: Emissionsfaktoren (grid, car, flight, tree_absorption) aus Options/Admin-Settings laden.

## Tests

- Edge: Negative/Null-Faktoren -> 0.0
- Happy: Beispielwerte (5000 kWh, 388 g/kWh, 120 g/km, 22 kg/Baum, 180 kg/Flug) ergeben plausibel skalierende Ergebnisse.
