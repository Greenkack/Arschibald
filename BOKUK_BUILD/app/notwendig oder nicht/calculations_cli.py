#!/usr/bin/env python3
"""
CLI‑Wrapper für die Photovoltaik‑Berechnungen.

Dieses Skript liest ein JSON‑Objekt von der Standard‑Eingabe, ruft die
Funktion ``perform_calculations`` aus dem Modul ``calculations`` auf und
gibt das Ergebnis als JSON zurück. Dadurch kann die bestehende
Berechnungslogik aus Electron/Node.js heraus über einen subprocess
angesprochen werden.

Eingabeformat (stdin):
```
{
  "project_data": { ... },    // Anlagen‑ und Kundendaten
  "texts": { ... },           // optionale Textbausteine (können leer sein)
  "errors_list": [],          // Liste für Fehlermeldungen (kann leer sein)
  "simulation_duration_user": null,
  "electricity_price_increase_user": null
}
```

Ausgabeformat (stdout): JSON‑Serialisierung des Ergebnis‑Dictionaries, so
wie es ``perform_calculations`` zurückliefert.
"""
import json
import sys
from typing import Any

try:
    from calculations import perform_calculations
except ImportError as exc:
    raise ImportError(
        "Das Modul 'calculations' konnte nicht importiert werden. Stelle sicher, "
        "dass es sich im Python‑Pfad befindet.") from exc


def main() -> None:
    """Liest JSON von stdin, führt die Berechnung aus und schreibt das Ergebnis."""
    try:
        data: dict[str, Any] = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Ungültiges JSON auf der Eingabe: {exc}")

    project_data: dict[str, Any] = data.get("project_data", {})
    texts: dict[str, str] = data.get("texts", {})
    errors_list: list[str] = data.get("errors_list", [])
    simulation_duration_user: int | None = data.get("simulation_duration_user")
    electricity_price_increase_user: float | None = data.get(
        "electricity_price_increase_user"
    )

    results: dict[str, Any] = perform_calculations(
        project_data,
        texts,
        errors_list,
        simulation_duration_user,
        electricity_price_increase_user,
    )

    json.dump(results, sys.stdout, ensure_ascii=False)
    sys.stdout.flush()


if __name__ == "__main__":
    main()
