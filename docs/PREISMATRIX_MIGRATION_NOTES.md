# Preismatrix Migration (Legacy Re-Integration)

Datum: 2025-09-22

## Hintergrund

Die zuvor integrierte neue Preismatrix-Architektur (PriceMatrix / StorageModelResolver / MatrixLoader)
lieferte weiterhin falsche oder unvollständige Ergebnisse (u.a. Speicher-Spalten wurden nicht erkannt).
Zur schnellen Wiederherstellung korrekter Preise wurde die funktionierende Legacy-Logik aus einem Backup
selektiv re‑integriert.

## Kernänderungen

1. Entfernen der direkten Abhängigkeit vom Klassen-Wrapper in `perform_calculations`.
2. Einführung robuster Normalisierung (trim, lower, Mehrfach‑Spaces, `_` → Leerzeichen).
3. Nearest-Lower Row Auswahl (größte Zeile <= angeforderte Modulanzahl) – verhindert starre Index-Offsets.
4. Fuzzy Matching für Speicher-Spalten (Teilstrings, Entfernung von "kwh").
5. Sauberer Fallback auf Spalte `Ohne Speicher` mit Fehlerhinweis falls weder spezifische noch Fallback-Spalte vorhanden.

## Tests

`test_price_matrix_legacy.py` deckt typische Fälle ab:

| Module | Speicher | Erwartet | Ergebnis |
|--------|----------|----------|----------|
| 20     | -        | 15113.50 | OK       |
| 20     | 15 kWh   | 18113.50 | OK       |
| 20     | 10 kWh   | 17113.50 | OK       |
| 33     | -        | 19410.43 | OK       |
| 33     | 15 kWh   | 23110.43 | OK       |

## Offene Punkte / Next Steps

- Validierung gegen echte Produktionsmatrix (Excel) erneut durchführen.
- Optional: Logging-Flag für detaillierte Preis-Matrix-Diagnostik hinzufügen.
- Harmonisierung von Spaltennamen in Admin-Upload (Normalisierung dort statt beim Lookup).

## Rollback

Die Änderungen beschränken sich auf den Kostenblock in `perform_calculations` und sind isoliert.
Ein Rollback besteht aus dem Wiederherstellen der vorherigen Fassung dieses Codeabschnitts.

## Wartungshinweis

Künftige Erweiterungen (z.B. Staffelpreise oder dynamische Aufschläge) sollten diese Pipeline respektieren:

1. Zeilenbestimmung
2. Spaltenauflösung
3. Validierung / Fallback
4. Konversion & Negativschutz
