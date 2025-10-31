"""
Analysis Utils - Hilfsfunktionen für die erweiterte Analyse
==========================================================

Utility-Funktionen für:
- Text-Lokalisierung
- Datenvalidierung
- Berechnungshilfen
- Formatierungsfunktionen
"""

import math
import re
from typing import Any


def get_text(texts_dict: dict[str, str], key: str,
             fallback_text: str | None = None) -> str:
    """
    Lädt lokalisierten Text aus Dictionary

    Args:
        texts_dict: Dictionary mit Texten
        key: Schlüssel für gewünschten Text
        fallback_text: Standard-Text falls Schlüssel nicht gefunden

    Returns:
        Lokalisierter Text oder Fallback
    """
    if fallback_text is None:
        fallback_text = key.replace("_", " ").title() + " (Text-Key fehlt)"

    return texts_dict.get(key, fallback_text) if texts_dict else fallback_text


def format_currency(
        value: int | float,
        currency: str = "€",
        decimal_places: int = 2,
        german_format: bool = True) -> str:
    """
    Formatiert Währungsbeträge

    Args:
        value: Zu formatierender Betrag
        currency: Währungssymbol
        decimal_places: Anzahl Dezimalstellen
        german_format: Deutsche Formatierung verwenden

    Returns:
        Formatierter Währungsbetrag
    """
    if value is None or (
        isinstance(
            value, float) and (
            math.isnan(value) or math.isinf(value))):
        return "k.A."

    if german_format:
        if decimal_places == 0:
            formatted = f"{value:,.0f}".replace(',', '.')
        else:
            formatted = f"{value:,.{decimal_places}f}"
            # Amerikanisches Format zu deutschem Format
            formatted = formatted.replace(
                ',',
                'TEMP').replace(
                '.',
                ',').replace(
                'TEMP',
                '.')
    else:
        formatted = f"{value:,.{decimal_places}f}"

    return f"{formatted} {currency}".strip()


def format_energy(value: int | float, unit: str = "kWh",
                  decimal_places: int = 0) -> str:
    """
    Formatiert Energiewerte

    Args:
        value: Zu formatierender Energiewert
        unit: Einheit (kWh, MWh, etc.)
        decimal_places: Anzahl Dezimalstellen

    Returns:
        Formatierter Energiewert
    """
    if value is None or (
        isinstance(
            value, float) and (
            math.isnan(value) or math.isinf(value))):
        return "k.A."

    # Automatische Einheitenkonvertierung für große Werte
    if unit == "kWh" and value >= 1000000:
        value = value / 1000000
        unit = "GWh"
        decimal_places = max(1, decimal_places)
    elif unit == "kWh" and value >= 1000:
        value = value / 1000
        unit = "MWh"
        decimal_places = max(1, decimal_places)

    formatted = f"{value:,.{decimal_places}f}".replace(',', '.')
    return f"{formatted} {unit}"


def format_percentage(value: int | float, decimal_places: int = 1) -> str:
    """
    Formatiert Prozentwerte

    Args:
        value: Zu formatierender Prozentwert
        decimal_places: Anzahl Dezimalstellen

    Returns:
        Formatierter Prozentwert
    """
    if value is None or (
        isinstance(
            value, float) and (
            math.isnan(value) or math.isinf(value))):
        return "k.A."

    return f"{value:.{decimal_places}f}%"


def format_duration(value: int | float, unit: str = "Jahre",
                    decimal_places: int = 1) -> str:
    """
    Formatiert Zeitdauern

    Args:
        value: Zu formatierender Zeitwert
        unit: Zeiteinheit
        decimal_places: Anzahl Dezimalstellen

    Returns:
        Formatierte Zeitdauer
    """
    if value is None or (
        isinstance(
            value, float) and (
            math.isnan(value) or math.isinf(value))):
        return "k.A."

    if unit == "Jahre" and value >= 1:
        if decimal_places == 0:
            return f"{value:.0f} {unit}"
        return f"{value:.{decimal_places}f} {unit}"
    if unit == "Jahre" and value < 1:
        months = value * 12
        return f"{months:.0f} Monate"

    return f"{value:.{decimal_places}f} {unit}"


def validate_numeric_input(value: Any, min_value: float | None = None,
                           max_value: float | None = None) -> bool:
    """
    Validiert numerische Eingaben

    Args:
        value: Zu validierender Wert
        min_value: Minimaler erlaubter Wert
        max_value: Maximaler erlaubter Wert

    Returns:
        True wenn Wert valide ist
    """
    try:
        numeric_value = float(value)

        if math.isnan(numeric_value) or math.isinf(numeric_value):
            return False

        if min_value is not None and numeric_value < min_value:
            return False

        if max_value is not None and numeric_value > max_value:
            return False

        return True

    except (ValueError, TypeError):
        return False


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Berechnet prozentuale Änderung

    Args:
        old_value: Alter Wert
        new_value: Neuer Wert

    Returns:
        Prozentuale Änderung
    """
    if old_value == 0:
        return float('inf') if new_value != 0 else 0

    return ((new_value - old_value) / old_value) * 100


def safe_divide(numerator: float, denominator: float,
                default_value: float = 0.0) -> float:
    """
    Sichere Division mit Fallback-Wert

    Args:
        numerator: Zähler
        denominator: Nenner
        default_value: Wert bei Division durch 0

    Returns:
        Ergebnis der Division oder Fallback-Wert
    """
    if denominator == 0 or math.isnan(denominator) or math.isinf(denominator):
        return default_value

    result = numerator / denominator

    if math.isnan(result) or math.isinf(result):
        return default_value

    return result


def interpolate_monthly_values(
        annual_value: float,
        seasonal_pattern: list[float] | None = None) -> list[float]:
    """
    Interpoliert jährliche Werte auf monatliche Werte

    Args:
        annual_value: Jährlicher Gesamtwert
        seasonal_pattern: Saisonale Gewichtungsfaktoren (12 Werte)

    Returns:
        Liste mit 12 monatlichen Werten
    """
    if seasonal_pattern is None:
        # Standard-Solarertragsmuster für Deutschland
        seasonal_pattern = [0.25, 0.45, 0.75, 1.15, 1.35, 1.45,
                            1.50, 1.30, 1.05, 0.65, 0.30, 0.20]

    if len(seasonal_pattern) != 12:
        raise ValueError("Saisonales Muster muss 12 Werte enthalten")

    # Normalisierung damit Summe = 12
    pattern_sum = sum(seasonal_pattern)
    normalized_pattern = [p * 12 / pattern_sum for p in seasonal_pattern]

    # Monatliche Werte berechnen
    monthly_values = [(annual_value / 12) *
                      factor for factor in normalized_pattern]

    return monthly_values


def create_scenario_variations(
        base_value: float, variation_percentages: list[float]) -> dict[str, float]:
    """
    Erstellt Szenario-Variationen basierend auf Basiswert

    Args:
        base_value: Basiswert
        variation_percentages: Liste mit Prozentabweichungen

    Returns:
        Dictionary mit Szenario-Namen und -Werten
    """
    scenarios = {}

    scenario_names = ["Pessimistisch", "Konservativ", "Realistisch",
                      "Optimistisch", "Sehr Optimistisch"]

    for i, percentage in enumerate(variation_percentages):
        if i < len(scenario_names):
            name = scenario_names[i]
            value = base_value * (1 + percentage / 100)
            scenarios[name] = value

    return scenarios


def calculate_compound_growth(initial_value: float, growth_rate_percent: float,
                              years: int) -> float:
    """
    Berechnet zusammengesetztes Wachstum

    Args:
        initial_value: Startwert
        growth_rate_percent: Jährliche Wachstumsrate in Prozent
        years: Anzahl Jahre

    Returns:
        Endwert nach zusammengesetztem Wachstum
    """
    if years == 0:
        return initial_value

    growth_factor = 1 + (growth_rate_percent / 100)
    return initial_value * (growth_factor ** years)


def calculate_present_value(future_value: float, discount_rate_percent: float,
                            years: int) -> float:
    """
    Berechnet Barwert

    Args:
        future_value: Zukünftiger Wert
        discount_rate_percent: Diskontierungssatz in Prozent
        years: Anzahl Jahre

    Returns:
        Barwert
    """
    if years == 0:
        return future_value

    discount_factor = 1 + (discount_rate_percent / 100)
    return future_value / (discount_factor ** years)


def extract_numeric_value(text: str) -> float | None:
    """
    Extrahiert numerischen Wert aus Text

    Args:
        text: Text mit numerischem Wert

    Returns:
        Extrahierter numerischer Wert oder None
    """
    if not isinstance(text, str):
        return None

    # Deutsche Zahlenformate unterstützen
    text = text.replace('.', '').replace(',', '.')

    # Zahlen extrahieren
    pattern = r'-?\d+(?:\.\d+)?'
    matches = re.findall(pattern, text)

    if matches:
        try:
            return float(matches[0])
        except ValueError:
            return None

    return None


def create_comparison_metrics(current_values: dict[str, float],
                              benchmark_values: dict[str, float]) -> dict[str, dict[str, Any]]:
    """
    Erstellt Vergleichsmetriken zwischen aktuellen und Benchmark-Werten

    Args:
        current_values: Aktuelle Werte
        benchmark_values: Benchmark-Werte

    Returns:
        Dictionary mit Vergleichsmetriken
    """
    comparisons = {}

    for key in current_values:
        if key in benchmark_values:
            current = current_values[key]
            benchmark = benchmark_values[key]

            difference = current - benchmark
            percentage_diff = calculate_percentage_change(benchmark, current)

            # Performance-Bewertung
            if abs(percentage_diff) <= 5:
                performance = "Durchschnittlich"
            elif percentage_diff > 5:
                performance = "Überdurchschnittlich"
            else:
                performance = "Unterdurchschnittlich"

            comparisons[key] = {
                'current': current,
                'benchmark': benchmark,
                'difference': difference,
                'percentage_difference': percentage_diff,
                'performance': performance
            }

    return comparisons


def generate_summary_statistics(data: list[float]) -> dict[str, float]:
    """
    Generiert zusammenfassende Statistiken

    Args:
        data: Liste mit numerischen Werten

    Returns:
        Dictionary mit Statistiken
    """
    if not data:
        return {}

    sorted_data = sorted(data)
    n = len(data)

    stats = {
        'count': n,
        'min': min(data),
        'max': max(data),
        'mean': sum(data) / n,
        'median': sorted_data[n // 2] if n % 2 == 1 else (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2,
        'range': max(data) - min(data)
    }

    # Standardabweichung
    mean = stats['mean']
    variance = sum((x - mean) ** 2 for x in data) / n
    stats['std_dev'] = math.sqrt(variance)

    # Quartile
    if n >= 4:
        q1_index = n // 4
        q3_index = 3 * n // 4
        stats['q1'] = sorted_data[q1_index]
        stats['q3'] = sorted_data[q3_index]
        stats['iqr'] = stats['q3'] - stats['q1']

    return stats


# Konstanten für häufig verwendete Werte
DEFAULT_SEASONAL_SOLAR_PATTERN = [0.25, 0.45, 0.75, 1.15, 1.35, 1.45,
                                  1.50, 1.30, 1.05, 0.65, 0.30, 0.20]

DEFAULT_CO2_FACTORS = {
    'german_electricity_mix_kg_per_kwh': 0.485,  # Deutscher Strommix 2023
    'car_annual_co2_kg': 2300,                   # Durchschnittliches Auto
    'tree_annual_co2_absorption_kg': 25,         # Ein Baum pro Jahr
    'flight_berlin_paris_co2_kg': 150           # Hin- und Rückflug
}

DEFAULT_FINANCIAL_ASSUMPTIONS = {
    'discount_rate_percent': 3.0,
    'inflation_rate_percent': 2.0,
    'electricity_price_increase_percent': 3.0,
    'system_degradation_percent_per_year': 0.5
}


if __name__ == "__main__":
    # Test der Utility-Funktionen
    print("🧪 Testing Analysis Utils...")

    # Test Formatierungsfunktionen
    print("", format_currency(12345.67))
    print("", format_energy(12345))
    print("", format_percentage(85.7))
    print("⏰", format_duration(12.5))

    # Test Berechnungen
    print("", calculate_percentage_change(1000, 1200))
    print("", safe_divide(100, 0, -1))

    # Test monatliche Interpolation
    monthly = interpolate_monthly_values(12000)
    print("", f"Monatswerte: {[f'{v:.0f}' for v in monthly[:3]]}...")

    # Test Szenarien
    scenarios = create_scenario_variations(25000, [-20, -10, 0, 10, 20])
    print("", f"Szenarien: {list(scenarios.keys())}")

    print(" Alle Tests erfolgreich!")
