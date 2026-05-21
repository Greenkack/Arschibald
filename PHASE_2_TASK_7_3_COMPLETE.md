# Phase 2 - Task 7.3: Kopieren & Einfügen (Copy & Paste) - COMPLETE ✅

## Übersicht

Task 7.3 implementiert eine Kopieren & Einfügen Funktionalität für PV-Module, die es ermöglicht, einzelne Module oder Modul-Gruppen zu duplizieren und an neuen Positionen einzufügen.

**Status**: ✅ COMPLETE (10/10 Tests bestanden)

## Implementierte Features

### 1. Kopieren-Funktion

**Funktion**: `copy_module_group(module_indices)`

Kopiert ausgewählte Module in die Zwischenablage (Session State).

**Features**:
- Kopiert einzelne oder mehrere Module
- Speichert Modul-Positionen (X, Y, Z)
- Speichert Original-Indizes für Referenz
- Validiert Modul-Indizes
- Speichert in Session State (`module_clipboard`)

**Parameter**:
- `module_indices`: Liste der zu kopierenden Modul-Indizes

**Rückgabe**:
```python
{
    "success": bool,           # Ob Kopieren erfolgreich war
    "message": str,            # Status oder Fehlermeldung
    "clipboard_data": list,    # Kopierte Modul-Daten
    "count": int               # Anzahl kopierter Module
}
```

**Beispiel**:
```python
from utils.pv3d_placement_handler import copy_module_group

# Kopiere Module 0, 1, 2
result = copy_module_group([0, 1, 2])

if result["success"]:
    print(f"✓ {result['message']}")  # "3 Module kopiert"
else:
    print(f"✗ {result['message']}")
```

### 2. Einfügen-Funktion

**Funktion**: `paste_module_group()`

Fügt kopierte Module mit konfigurierbarem Offset ein.

**Features**:
- Fügt Module aus Zwischenablage ein
- Konfigurierbare X/Y-Offsets
- Automatische Z-Positions-Berechnung basierend auf Dachtyp
- Optional: Kollisionsprüfung
- Überspringt Module bei Kollision
- Aktualisiert Session State

**Parameter**:
- `offset_x`: X-Offset in Metern (default: 1.0m)
- `offset_y`: Y-Offset in Metern (default: 1.0m)
- `roof_type`: Dachtyp (default: "Flachdach")
- `roof_pitch`: Dachneigung in Grad (default: 0.0)
- `roof_width`: Dachbreite in Metern (default: 10.0m)
- `roof_length`: Dachlänge in Metern (default: 10.0m)
- `orientation`: Modul-Orientierung (default: "portrait")
- `check_collisions`: Kollisionsprüfung aktivieren? (default: True)

**Rückgabe**:
```python
{
    "success": bool,              # Ob Einfügen erfolgreich war
    "message": str,               # Status oder Fehlermeldung
    "pasted_positions": list,     # Eingefügte Positionen
    "pasted_count": int,          # Anzahl eingefügter Module
    "skipped_count": int          # Anzahl übersprungener Module
}
```

**Beispiel**:
```python
from utils.pv3d_placement_handler import paste_module_group

# Füge Module mit 2m X-Offset und 1m Y-Offset ein
result = paste_module_group(
    offset_x=2.0,
    offset_y=1.0,
    roof_type="Satteldach",
    roof_pitch=30.0,
    roof_width=10.0,
    roof_length=12.0,