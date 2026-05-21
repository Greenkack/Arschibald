#!/usr/bin/env python3
"""
Deutsche Zahlenformatierung für die gesamte App
"""


def format_german_number(
        value: int | float,
        decimals: int = 2,
        unit: str = "") -> str:
    """
    Formatiert Zahlen im deutschen Format: 23.403,11
    """
    if value is None:
        return "0,00"

    try:
        # Konvertiere zu float
        num_value = float(value)

        # Formatiere mit deutschen Standards
        if decimals == 0:
            formatted = f"{
                num_value:,.0f}".replace(
                ",",
                "X").replace(
                ".",
                ",").replace(
                "X",
                ".")
        else:
            formatted = f"{
                num_value:,.{decimals}f}".replace(
                ",",
                "X").replace(
                ".",
                ",").replace(
                "X",
                ".")

        # Füge Einheit hinzu
        if unit:
            return f"{formatted} {unit}"
        return formatted

    except (ValueError, TypeError):
        return "0,00"


def format_currency(value: int | float) -> str:
    """Formatiert Währung im deutschen Format"""
    return format_german_number(value, 2, "€")


def format_percentage(value: int | float) -> str:
    """Formatiert Prozentsätze im deutschen Format"""
    return format_german_number(value, 1, "%")


def format_kwh(value: int | float) -> str:
    """Formatiert kWh-Werte im deutschen Format"""
    return format_german_number(value, 0, "kWh")


def format_kwp(value: int | float) -> str:
    """Formatiert kWp-Werte im deutschen Format"""
    return format_german_number(value, 1, "kWp")


def format_years(value: int | float) -> str:
    """Formatiert Jahre im deutschen Format"""
    return format_german_number(value, 1, "Jahre")


def format_ct_kwh(value: int | float) -> str:
    """Formatiert ct/kWh im deutschen Format"""
    return format_german_number(value, 2, "ct/kWh")


# Test der Formatierung
if __name__ == "__main__":
    test_values = [
        (23403.11, "23.403,11"),
        (433792.52, "433.792,52"),
        (1632.02, "1.632,02"),
        (0.3245, "0,32"),
        (1000000, "1.000.000,00")
    ]

    for value, expected in test_values:
        result = format_german_number(value)
        print(f"Input: {value} -> Output: {result} (Expected: {expected})")
