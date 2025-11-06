"""
PV-Unterkonstruktions-Berechnungs-Engine
========================================

Dynamische Berechnungen für PV-Montagekomponenten basierend auf
Modulanzahl, Dachtyp, Ausrichtung und Herstellersystem.

Autor: Bokuk2 System
Version: 2.0.0 - Enhanced with Robustness Patterns
Datum: 2025-11-06
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import math

from pv_mounting_database import read_components

# Robustness Integration
try:
    from robustness_core import (
        PickleSerializable,
        safe_function,
        validate_numeric,
        logger,
        performance_timer
    )
    ROBUSTNESS_AVAILABLE = True
except ImportError:
    # Fallback: No robustness features
    ROBUSTNESS_AVAILABLE = False
    
    class PickleSerializable:
        pass
    
    def safe_function(fallback_value=None, error_message=""):
        def decorator(func):
            return func
        return decorator
    
    def validate_numeric(value, **kwargs):
        return float(value) if value is not None else kwargs.get('default')
    
    import logging
    logger = logging.getLogger(__name__)
    
    from contextlib import contextmanager
    @contextmanager
    def performance_timer(operation, **kwargs):
        yield


# ==================== Datenklassen (mit Pickle-Support) ====================

@dataclass
class ModuleConfiguration(PickleSerializable):
    """Konfiguration der PV-Module."""
    count: int  # Anzahl Module
    width_mm: float = 1134  # Standard: 1134mm
    height_mm: float = 1722  # Standard: 1722mm
    weight_kg: float = 21.5  # Standard: 21.5kg
    orientation: str = "Portrait"  # Portrait oder Landscape
    rows: int = 1  # Anzahl Reihen
    modules_per_row: int = None  # Module pro Reihe (wird berechnet falls None)


@dataclass
class RoofConfiguration(PickleSerializable):
    """Konfiguration des Daches."""
    roof_type: str  # Ziegeldach, Flachdach, etc.
    pitch_degrees: float = 35.0  # Dachneigung in Grad
    orientation: str = "Süd"  # Süd, Ost-West, etc.
    rafter_spacing_mm: float = 800.0  # Sparrenabstand
    snow_load_zone: int = 2  # Schneelastzone 1-3
    wind_load_zone: int = 2  # Windlastzone 1-4


@dataclass
class ComponentRequirement(PickleSerializable):
    """Berechnete Komponentenanforderung."""
    component_id: int
    product_name: str
    category: str
    manufacturer: str
    quantity: float
    unit: str
    price_per_unit: float
    total_price: float
    notes: str = ""


@dataclass
class MountingCalculationResult(PickleSerializable):
    """Ergebnis der Unterkonstruktions-Berechnung."""
    module_config: ModuleConfiguration
    roof_config: RoofConfiguration
    components: List[ComponentRequirement]
    total_components_count: int
    total_price_netto: float
    total_weight_kg: float
    calculation_notes: List[str]
    warnings: List[str]


# ==================== Berechnungsfunktionen (mit Robustness) ====================

@safe_function(fallback_value=0, error_message="Module-per-row calculation failed")
def calculate_modules_per_row(module_config: ModuleConfiguration) -> int:
    """
    Berechnet Module pro Reihe basierend auf Gesamtanzahl und Reihen.
    
    Args:
        module_config: Modul-Konfiguration
        
    Returns:
        int: Module pro Reihe
    """
    if module_config.modules_per_row:
        return module_config.modules_per_row
    
    # Validation
    count = validate_numeric(module_config.count, min_value=1, default=1)
    rows = validate_numeric(module_config.rows, min_value=1, default=1)
    
    return math.ceil(count / rows)


@safe_function(fallback_value=(0, ["Calculation failed"]), error_message="Roof hooks calculation failed")
def calculate_roof_hooks_required(
    module_config: ModuleConfiguration,
    roof_config: RoofConfiguration
) -> Tuple[int, List[str]]:
    """
    Berechnet Anzahl benötigter Dachhaken.
    
    Logik:
    - Standard: 2 Dachhaken pro Modul
    - Bei Betondach oder hoher Schneelast: 3 Dachhaken pro Modul
    - Bei Flachdach: 0 (Ballastierung)
    - Bei Sparrenabstand >900mm: +1 Dachhaken pro Modul
    
    Args:
        module_config: Modul-Konfiguration
        roof_config: Dach-Konfiguration
        
    Returns:
        Tuple[int, List[str]]: (Anzahl Dachhaken, Berechnungshinweise)
    """
    notes = []
    
    if roof_config.roof_type == "Flachdach":
        notes.append("Flachdach: Keine Dachhaken erforderlich (Ballastierung)")
        return 0, notes
    
    # Basis: 2 Haken pro Modul
    hooks_per_module = 2.0
    notes.append(f"Basis: {hooks_per_module} Dachhaken pro Modul")
    
    # Betondach oder hohe Schneelast
    snow_zone = validate_numeric(roof_config.snow_load_zone, min_value=1, max_value=5, default=2)
    if roof_config.roof_type == "Betondach" or snow_zone >= 3:
        hooks_per_module = 3.0
        notes.append(f"Betondach/Schneelastzone {snow_zone}: {hooks_per_module} Dachhaken pro Modul")
    
    # Großer Sparrenabstand
    rafter_spacing = validate_numeric(roof_config.rafter_spacing_mm, min_value=300, max_value=1500, default=800)
    if rafter_spacing > 900:
        hooks_per_module += 1.0
        notes.append(f"Sparrenabstand {rafter_spacing}mm > 900mm: +1 Dachhaken pro Modul")
    
    module_count = validate_numeric(module_config.count, min_value=1, default=1)
    total_hooks = int(math.ceil(module_count * hooks_per_module))
    notes.append(f"Gesamt: {module_count} Module × {hooks_per_module} = {total_hooks} Dachhaken")
    
    logger.info("Roof hooks calculated", total=total_hooks, per_module=hooks_per_module)
    
    return total_hooks, notes


@safe_function(fallback_value=(0.0, ["Calculation failed"]), error_message="Rails calculation failed")
def calculate_rails_required(
    module_config: ModuleConfiguration,
    roof_config: RoofConfiguration
) -> Tuple[float, List[str]]:
    """
    Berechnet benötigte Schienenlänge in Metern.
    
    Logik:
    - 2 Schienen pro Modulreihe (bei Portrait-Ausrichtung)
    - Schienenlänge = Modulanzahl pro Reihe × Modulbreite + 10% Verschnitt
    - Bei Flachdach: Kürzere Schienen (MiniRails)
    
    Args:
        module_config: Modul-Konfiguration
        roof_config: Dach-Konfiguration
        
    Returns:
        Tuple[float, List[str]]: (Länge in Metern, Berechnungshinweise)
    """
    notes = []
    
    modules_per_row = calculate_modules_per_row(module_config)
    
    # Modul-Abmessung je nach Ausrichtung
    if module_config.orientation == "Portrait":
        module_length_mm = validate_numeric(module_config.width_mm, min_value=500, max_value=2000, default=1134)
        rails_per_row = 2
    else:  # Landscape
        module_length_mm = validate_numeric(module_config.height_mm, min_value=500, max_value=2500, default=1722)
        rails_per_row = 2
    
    # Schienenlänge pro Reihe
    rail_length_per_row_m = (modules_per_row * module_length_mm) / 1000.0
    
    # Verschnitt 10%
    rail_length_per_row_m *= 1.10
    
    notes.append(f"{module_config.orientation}: {modules_per_row} Module/Reihe × {module_length_mm}mm = {rail_length_per_row_m:.2f}m/Reihe")
    
    # Flachdach: MiniRails
    if roof_config.roof_type == "Flachdach":
        # Bei Flachdach: 4 MiniRails pro Modul (statt langen Schienen)
        total_mini_rails = module_config.count * 4
        notes.append(f"Flachdach: {total_mini_rails} MiniRails (4 pro Modul)")
        return total_mini_rails, notes  # Rückgabe als Stückzahl
    
    # Gesamtlänge für alle Reihen
    total_rail_length_m = rail_length_per_row_m * module_config.rows * rails_per_row
    
    notes.append(f"Gesamt: {module_config.rows} Reihen × {rails_per_row} Schienen × {rail_length_per_row_m:.2f}m = {total_rail_length_m:.2f}m")
    
    return total_rail_length_m, notes


def calculate_clamps_required(
    module_config: ModuleConfiguration,
    roof_config: RoofConfiguration
) -> Tuple[Dict[str, int], List[str]]:
    """
    Berechnet Anzahl End- und Mittelklemmen.
    
    Logik:
    - Endklemmen: 2 pro Modul (an den Rändern)
    - Mittelklemmen: Zwischen Modulen geteilt
    - Pro Modulreihe: (Module - 1) × 2 Mittelklemmen
    
    Args:
        module_config: Modul-Konfiguration
        roof_config: Dach-Konfiguration
        
    Returns:
        Tuple[Dict, List[str]]: ({end_clamps, mid_clamps}, Hinweise)
    """
    notes = []
    
    modules_per_row = calculate_modules_per_row(module_config)
    
    # Endklemmen: 2 pro Modulreihe (Anfang + Ende)
    # Bei mehreren Modulen pro Reihe: 2 Endklemmen pro Reihe
    end_clamps_per_row = 2 * 2  # 2 Schienen × 2 Enden
    total_end_clamps = end_clamps_per_row * module_config.rows
    
    notes.append(f"Endklemmen: {end_clamps_per_row} pro Reihe × {module_config.rows} Reihen = {total_end_clamps}")
    
    # Mittelklemmen: Zwischen Modulen
    # Pro Reihe: (Module - 1) Verbindungen × 2 Schienen × 2 Klemmen
    mid_clamps_per_row = (modules_per_row - 1) * 2 * 2 if modules_per_row > 1 else 0
    total_mid_clamps = mid_clamps_per_row * module_config.rows
    
    notes.append(f"Mittelklemmen: {mid_clamps_per_row} pro Reihe × {module_config.rows} Reihen = {total_mid_clamps}")
    
    return {
        'end_clamps': total_end_clamps,
        'mid_clamps': total_mid_clamps
    }, notes


def calculate_screws_required(
    roof_hooks_count: int,
    roof_config: RoofConfiguration
) -> Tuple[int, List[str]]:
    """
    Berechnet Anzahl benötigter Holzschrauben.
    
    Logik:
    - 2 Schrauben pro Dachhaken (Standard)
    - Bei Aufdachdämmung: 3 Schrauben pro Haken
    
    Args:
        roof_hooks_count: Anzahl Dachhaken
        roof_config: Dach-Konfiguration
        
    Returns:
        Tuple[int, List[str]]: (Anzahl Schrauben, Hinweise)
    """
    notes = []
    
    screws_per_hook = 2
    
    # Bei bestimmten Dachtypen mehr Schrauben
    if roof_config.roof_type in ["Sandwichplatten", "Biberschwanzdach"]:
        screws_per_hook = 3
        notes.append(f"{roof_config.roof_type}: {screws_per_hook} Schrauben pro Dachhaken")
    else:
        notes.append(f"Standard: {screws_per_hook} Schrauben pro Dachhaken")
    
    total_screws = roof_hooks_count * screws_per_hook
    notes.append(f"Gesamt: {roof_hooks_count} Dachhaken × {screws_per_hook} = {total_screws} Schrauben")
    
    return total_screws, notes


def calculate_cable_length(
    module_config: ModuleConfiguration,
    distance_to_inverter_m: float = 10.0
) -> Tuple[Dict[str, float], List[str]]:
    """
    Berechnet benötigte Kabellänge.
    
    Logik:
    - 1m pro Modul (Modul-zu-Modul-Verkabelung)
    - + Distanz zum Wechselrichter
    - + 30m Reserve
    - Rot und Schwarz getrennt
    
    Args:
        module_config: Modul-Konfiguration
        distance_to_inverter_m: Distanz zum Wechselrichter
        
    Returns:
        Tuple[Dict, List[str]]: ({red, black, total}, Hinweise)
    """
    notes = []
    
    # Basis: 1m pro Modul
    module_cables_m = module_config.count * 1.0
    
    # + Distanz zum WR
    # + 30m Reserve
    total_per_color = module_cables_m + distance_to_inverter_m + 30.0
    
    notes.append(f"Modulkabel: {module_config.count} Module × 1m = {module_cables_m}m")
    notes.append(f"Distanz WR: {distance_to_inverter_m}m")
    notes.append(f"Reserve: 30m")
    notes.append(f"Gesamt pro Farbe: {total_per_color}m")
    
    return {
        'red_cable_m': total_per_color,
        'black_cable_m': total_per_color,
        'total_cable_m': total_per_color * 2
    }, notes


def calculate_ballast_for_flat_roof(
    module_config: ModuleConfiguration,
    wind_load_zone: int = 2
) -> Tuple[float, List[str]]:
    """
    Berechnet benötigte Ballastierung für Flachdach.
    
    Logik:
    - Windlastzone 1: 15 kg/Modul
    - Windlastzone 2: 20 kg/Modul
    - Windlastzone 3: 25 kg/Modul
    - Windlastzone 4: 30 kg/Modul
    
    Args:
        module_config: Modul-Konfiguration
        wind_load_zone: Windlastzone 1-4
        
    Returns:
        Tuple[float, List[str]]: (Ballast in kg, Hinweise)
    """
    notes = []
    
    ballast_per_module_kg = {
        1: 15.0,
        2: 20.0,
        3: 25.0,
        4: 30.0
    }.get(wind_load_zone, 20.0)
    
    total_ballast_kg = module_config.count * ballast_per_module_kg
    
    notes.append(f"Windlastzone {wind_load_zone}: {ballast_per_module_kg} kg/Modul")
    notes.append(f"Gesamt: {module_config.count} Module × {ballast_per_module_kg} kg = {total_ballast_kg} kg")
    
    return total_ballast_kg, notes


# ==================== Hauptberechnung ====================

def calculate_mounting_system(
    module_config: ModuleConfiguration,
    roof_config: RoofConfiguration,
    manufacturer: str = "K2 Systems",
    distance_to_inverter_m: float = 10.0
) -> MountingCalculationResult:
    """
    Führt vollständige Berechnung der Unterkonstruktion durch.
    
    Args:
        module_config: Modul-Konfiguration
        roof_config: Dach-Konfiguration
        manufacturer: Hersteller-Präferenz
        distance_to_inverter_m: Distanz zum Wechselrichter
        
    Returns:
        MountingCalculationResult: Berechnungsergebnis mit allen Komponenten
    """
    components: List[ComponentRequirement] = []
    all_notes: List[str] = []
    warnings: List[str] = []
    
    # 1. Dachhaken berechnen
    roof_hooks_count, hooks_notes = calculate_roof_hooks_required(module_config, roof_config)
    all_notes.extend(hooks_notes)
    
    if roof_hooks_count > 0:
        # Dachhaken aus DB holen
        hook_filter = {
            'manufacturer': manufacturer,
            'category': 'Dachhaken',
            'roof_type': roof_config.roof_type
        }
        
        hooks_db = read_components(filters=hook_filter, limit=1)
        
        if hooks_db:
            hook = hooks_db[0]
            components.append(ComponentRequirement(
                component_id=hook['id'],
                product_name=hook['product_name'],
                category='Dachhaken',
                manufacturer=hook['manufacturer'],
                quantity=roof_hooks_count,
                unit=hook['unit'],
                price_per_unit=hook['price_netto'],
                total_price=roof_hooks_count * hook['price_netto'],
                notes=f"Berechnet: {roof_hooks_count} Stück"
            ))
        else:
            warnings.append(f"Keine Dachhaken für {manufacturer} + {roof_config.roof_type} in DB gefunden!")
    
    # 2. Schienen berechnen
    rail_length_m, rail_notes = calculate_rails_required(module_config, roof_config)
    all_notes.extend(rail_notes)
    
    if roof_config.roof_type == "Flachdach":
        # MiniRails
        rail_filter = {
            'manufacturer': manufacturer,
            'category': 'Trapezblechschiene',  # MiniRails als Kategorie
            'roof_type': 'Flachdach'
        }
        
        rails_db = read_components(filters=rail_filter, limit=1)
        
        if rails_db:
            rail = rails_db[0]
            components.append(ComponentRequirement(
                component_id=rail['id'],
                product_name=rail['product_name'],
                category='MiniRail/Kurzschiene',
                manufacturer=rail['manufacturer'],
                quantity=rail_length_m,  # Ist bereits Stückzahl bei Flachdach
                unit='Stk',
                price_per_unit=rail['price_netto'],
                total_price=rail_length_m * rail['price_netto'],
                notes=f"Berechnet: {rail_length_m} Stück MiniRails"
            ))
    else:
        # Normale Montageschienen
        rail_filter = {
            'manufacturer': manufacturer,
            'category': 'Montageschiene',
            'roof_type': roof_config.roof_type
        }
        
        rails_db = read_components(filters=rail_filter, limit=1)
        
        if rails_db:
            rail = rails_db[0]
            components.append(ComponentRequirement(
                component_id=rail['id'],
                product_name=rail['product_name'],
                category='Montageschiene',
                manufacturer=rail['manufacturer'],
                quantity=rail_length_m,
                unit='m',
                price_per_unit=rail['price_netto'],
                total_price=rail_length_m * rail['price_netto'],
                notes=f"Berechnet: {rail_length_m:.2f} m"
            ))
        else:
            warnings.append(f"Keine Montageschienen für {manufacturer} + {roof_config.roof_type} in DB gefunden!")
    
    # 3. Klemmen berechnen
    clamps_dict, clamps_notes = calculate_clamps_required(module_config, roof_config)
    all_notes.extend(clamps_notes)
    
    # Endklemmen
    end_clamp_filter = {
        'manufacturer': manufacturer,
        'category': 'Modulklemme (End)'
    }
    
    end_clamps_db = read_components(filters=end_clamp_filter, limit=1)
    
    if end_clamps_db:
        end_clamp = end_clamps_db[0]
        components.append(ComponentRequirement(
            component_id=end_clamp['id'],
            product_name=end_clamp['product_name'],
            category='Modulklemme (End)',
            manufacturer=end_clamp['manufacturer'],
            quantity=clamps_dict['end_clamps'],
            unit=end_clamp['unit'],
            price_per_unit=end_clamp['price_netto'],
            total_price=clamps_dict['end_clamps'] * end_clamp['price_netto'],
            notes=f"Berechnet: {clamps_dict['end_clamps']} Stück"
        ))
    
    # Mittelklemmen
    mid_clamp_filter = {
        'manufacturer': manufacturer,
        'category': 'Modulklemme (Mittel)'
    }
    
    mid_clamps_db = read_components(filters=mid_clamp_filter, limit=1)
    
    if mid_clamps_db:
        mid_clamp = mid_clamps_db[0]
        components.append(ComponentRequirement(
            component_id=mid_clamp['id'],
            product_name=mid_clamp['product_name'],
            category='Modulklemme (Mittel)',
            manufacturer=mid_clamp['manufacturer'],
            quantity=clamps_dict['mid_clamps'],
            unit=mid_clamp['unit'],
            price_per_unit=mid_clamp['price_netto'],
            total_price=clamps_dict['mid_clamps'] * mid_clamp['price_netto'],
            notes=f"Berechnet: {clamps_dict['mid_clamps']} Stück"
        ))
    
    # 4. Schrauben berechnen
    screws_count, screws_notes = calculate_screws_required(roof_hooks_count, roof_config)
    all_notes.extend(screws_notes)
    
    if screws_count > 0:
        screw_filter = {
            'manufacturer': manufacturer,
            'category': 'Schrauben'
        }
        
        screws_db = read_components(filters=screw_filter, limit=1)
        
        if screws_db:
            screw = screws_db[0]
            components.append(ComponentRequirement(
                component_id=screw['id'],
                product_name=screw['product_name'],
                category='Schrauben',
                manufacturer=screw['manufacturer'],
                quantity=screws_count,
                unit=screw['unit'],
                price_per_unit=screw['price_netto'],
                total_price=screws_count * screw['price_netto'],
                notes=f"Berechnet: {screws_count} Stück"
            ))
    
    # 5. Kabel berechnen
    cable_dict, cable_notes = calculate_cable_length(module_config, distance_to_inverter_m)
    all_notes.extend(cable_notes)
    
    cable_filter = {
        'category': 'Kabel'
    }
    
    cables_db = read_components(filters=cable_filter, limit=2)  # Rot + Schwarz
    
    if cables_db:
        for cable_color, length_m in [('red', cable_dict['red_cable_m']), ('black', cable_dict['black_cable_m'])]:
            # Versuche passende Kabelfarbe zu finden
            cable = cables_db[0]  # Fallback: erstes Kabel
            
            for c in cables_db:
                if cable_color in c['product_name'].lower() or cable_color == 'red' and 'rot' in c['product_name'].lower():
                    cable = c
                    break
            
            components.append(ComponentRequirement(
                component_id=cable['id'],
                product_name=cable['product_name'],
                category='Kabel',
                manufacturer=cable.get('manufacturer', 'Standard'),
                quantity=length_m,
                unit='m',
                price_per_unit=cable['price_netto'],
                total_price=length_m * cable['price_netto'],
                notes=f"Berechnet: {length_m:.2f} m ({cable_color})"
            ))
    
    # 6. Ballast bei Flachdach
    if roof_config.roof_type == "Flachdach":
        ballast_kg, ballast_notes = calculate_ballast_for_flat_roof(module_config, roof_config.wind_load_zone)
        all_notes.extend(ballast_notes)
        all_notes.append(f"Hinweis: Ballast {ballast_kg} kg erforderlich (nicht in Komponentenliste)")
    
    # Summen berechnen
    total_price = sum(c.total_price for c in components)
    total_weight = sum(c.quantity * 0.5 for c in components)  # Geschätzt: 0.5kg/Komponente
    
    return MountingCalculationResult(
        module_config=module_config,
        roof_config=roof_config,
        components=components,
        total_components_count=len(components),
        total_price_netto=total_price,
        total_weight_kg=total_weight,
        calculation_notes=all_notes,
        warnings=warnings
    )


# ==================== Preset-Konfigurationen ====================

def get_preset_configurations() -> Dict[str, Dict[str, Any]]:
    """
    Gibt vordefinierte Konfigurations-Presets zurück.
    
    Returns:
        Dict: Preset-Konfigurationen
    """
    return {
        "Klein (10 Module, Ziegeldach)": {
            "module_config": ModuleConfiguration(
                count=10,
                orientation="Portrait",
                rows=2
            ),
            "roof_config": RoofConfiguration(
                roof_type="Ziegeldach",
                pitch_degrees=35.0,
                rafter_spacing_mm=800.0,
                snow_load_zone=2,
                wind_load_zone=2
            )
        },
        "Mittel (20 Module, Flachdach)": {
            "module_config": ModuleConfiguration(
                count=20,
                orientation="Portrait",
                rows=2
            ),
            "roof_config": RoofConfiguration(
                roof_type="Flachdach",
                pitch_degrees=0.0,
                orientation="Süd",
                snow_load_zone=2,
                wind_load_zone=2
            )
        },
        "Groß (40 Module, Trapezblech)": {
            "module_config": ModuleConfiguration(
                count=40,
                orientation="Landscape",
                rows=4
            ),
            "roof_config": RoofConfiguration(
                roof_type="Blechdach (Trapezblech)",
                pitch_degrees=5.0,
                snow_load_zone=1,
                wind_load_zone=3
            )
        }
    }
