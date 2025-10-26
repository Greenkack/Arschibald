#!/usr/bin/env python3
"""Prüft die Preise der Produkte in der Datenbank"""

from product_db import list_products


def check_module_prices():
    """Zeigt die ersten 20 Module mit ihren Preisen"""
    modules = list_products('module')

    print("=" * 100)
    print("MODUL-PREISE IN DER DATENBANK")
    print("=" * 100)
    print(f"{'Marke':<20} {'Modell':<45} {'Leistung':>10} {'Preis':>12}")
    print("-" * 100)

    for i, m in enumerate(modules[:20], 1):
        brand = (m.get("brand") or "?")[:19]
        model = (m.get("model_name") or "?")[:44]
        power = m.get("power_wp") or m.get("capacity_kwh") or "?"
        price = m.get("price_euro") or 0

        print(f"{brand:<20} {model:<45} {power:>10} {price:>11.2f} €")

    print("=" * 100)

    # Statistik
    prices = [m.get("price_euro", 0) for m in modules if m.get("price_euro")]
    if prices:
        print(f"\nPreis-Statistik ({len(prices)} Module):")
        print(f"  Min:    {min(prices):>8.2f} €")
        print(f"  Max:    {max(prices):>8.2f} €")
        print(f"  Ø:      {sum(prices) / len(prices):>8.2f} €")

    # Prüfe ob Preise identisch sind
    unique_prices = set(prices)
    if len(unique_prices) == 1:
        print(
            f"\n⚠️  PROBLEM: Alle Module haben den GLEICHEN Preis: {
                list(unique_prices)[0]:.2f} €")
    elif len(unique_prices) < 5:
        print(
            f"\n⚠️  WARNUNG: Nur {
                len(unique_prices)} verschiedene Preise gefunden!")
        print(f"   Preise: {sorted(unique_prices)}")
    else:
        print(f"\n✓ {len(unique_prices)} verschiedene Preise gefunden (gut!)")


if __name__ == "__main__":
    check_module_prices()
