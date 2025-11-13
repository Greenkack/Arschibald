# Preismatrix-System - Quick Reference

## Schnellzugriff

### Preis berechnen

```python
from price_matrix_lookup import calculate_price_from_matrix

result = calculate_price_from_matrix(20, "15kWh")
if result['success']:
    print(f"Preis: {result['base_price']} EUR")
```

### Matrix hochladen

```python
from admin_price_matrix_upload import upload_price_matrix

success, msg = upload_price_matrix(csv_data, "Matrix Name")
```

### Performance prüfen

```python
from price_matrix_performance import get_global_monitor

monitor = get_global_monitor()
print(monitor.generate_report())
```

## Wichtige Funktionen

| Funktion | Modul | Beschreibung |
|----------|-------|--------------|
| `calculate_price_from_matrix()` | price_matrix_lookup | Hauptfunktion für Preis-Lookup |
| `list_matrices()` | price_matrix_store | Alle Matrizen auflisten |
| `set_active_matrix()` | price_matrix_store | Matrix aktivieren |
| `get_matrix_full()` | price_matrix_store | Matrix-Daten abrufen |
| `benchmark_matrix_lookup()` | price_matrix_performance | Performance-Test |

## Fehlertypen

- `invalid_input` - Ungültige Parameter
- `no_matrix` - Keine Matrix aktiv
- `no_row` - Modulanzahl nicht gefunden
- `no_column` - Speichermodell nicht gefunden
- `no_price` - Keine Preis-Zelle
- `invalid_price` - Ungültiger Preis

## Performance-Tipps

1. ✅ Cache nutzen durch wiederholte Lookups
2. ✅ Fallback nur wenn nötig aktivieren
3. ✅ Performance-Monitoring in Produktion
4. ✅ Regelmäßig Optimierungen prüfen

## Weitere Dokumentation

- [Vollständige API-Dokumentation](PRICE_MATRIX_API_DOCUMENTATION.md)
- [Fehlerbehandlungs-Guide](PRICE_MATRIX_ERROR_HANDLING_GUIDE.md)
- [Admin Matrix Upload Guide](ADMIN_MATRIX_UPLOAD_GUIDE.md)
