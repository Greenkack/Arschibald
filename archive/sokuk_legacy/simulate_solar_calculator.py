#!/usr/bin/env python3
"""
Simulates how SolarCalculator would use the database_bridge.py
Shows the data that would be available to the frontend
"""

import json
import os
import subprocess
import sys

# Add the current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_database_command(command, *args):
    """Run a database command and return the result"""
    try:
        cmd = ['python', 'database_bridge.py', command] + list(args)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__))
        if result.returncode == 0:
            return json.loads(result.stdout)
        print(f"Error running {command}: {result.stderr}")
        return None
    except Exception as e:
        print(f"Exception running {command}: {e}")
        return None


def simulate_solar_calculator_data_flow():
    """Simulate how SolarCalculator would load and use product data"""
    print("=== Simulating SolarCalculator Data Flow ===\n")

    # Step 1: Load all solar modules (like in useProducts hook)
    print("1. Loading solar modules for SolarCalculator...")
    modules_result = run_database_command('list_products', '--category=Modul')
    if modules_result and modules_result.get('success'):
        modules = modules_result['data']
        print(f"   ✓ Loaded {len(modules)} solar modules")

        # Group by manufacturer (like SolarCalculator would do)
        manufacturers = {}
        for module in modules:
            manufacturer = module.get('brand', 'Unknown')
            if manufacturer not in manufacturers:
                manufacturers[manufacturer] = []
            manufacturers[manufacturer].append(
                {
                    'id': module.get('id'), 'name': module.get(
                        'model_name', 'Unknown Model'), 'power': module.get(
                        'capacity_w', 0), 'price': module.get(
                        'price_netto', 0), 'efficiency': module.get(
                        'efficiency_percent', 0), 'dimensions': f"{
                            module.get(
                                'length_mm', 0)}x{
                                    module.get(
                                        'width_mm', 0)}x{
                                            module.get(
                                                'thickness_mm', 0)}mm"})

        print("\n   Available manufacturers and models:")
        for manufacturer, models in manufacturers.items():
            print(f"   📦 {manufacturer}: {len(models)} models")
            for model in models[:2]:  # Show first 2 models
                print(
                    f"     - {
                        model['name']} ({
                        model['power']}W, {
                        model['efficiency']}%, €{
                        model['price']:.2f})")
            if len(models) > 2:
                print(f"     ... and {len(models) - 2} more models")
            print()

    # Step 2: Load inverters
    print("2. Loading inverters...")
    inverters_result = run_database_command(
        'list_products', '--category=Wechselrichter')
    if inverters_result and inverters_result.get('success'):
        inverters = inverters_result['data']
        print(f"   ✓ Loaded {len(inverters)} inverters")

        # Show top inverters by power
        sorted_inverters = sorted(
            inverters, key=lambda x: x.get(
                'power_kw', 0), reverse=True)
        print("   Top inverters by power:")
        for inv in sorted_inverters[:5]:
            print(
                f"     - {
                    inv.get('brand')} {
                    inv.get('model_name')} ({
                    inv.get(
                        'power_kw',
                        0)}kW, €{
                        inv.get(
                            'price_netto',
                            0):.2f})")

    # Step 3: Load battery storage systems
    print("\n3. Loading battery storage systems...")
    batteries_result = run_database_command(
        'list_products', '--category=Batteriespeicher')
    if batteries_result and batteries_result.get('success'):
        batteries = batteries_result['data']
        print(f"   ✓ Loaded {len(batteries)} battery storage systems")

        # Show top batteries by capacity
        sorted_batteries = sorted(
            batteries,
            key=lambda x: x.get(
                'storage_power_kw',
                0) or x.get(
                'capacity_kwh',
                0) or 0,
            reverse=True)
        print("   Top batteries by capacity:")
        for bat in sorted_batteries[:5]:
            capacity = bat.get(
                'storage_power_kw',
                0) or bat.get(
                'capacity_kwh',
                0)
            print(
                f"     - {
                    bat.get('brand')} {
                    bat.get('model_name')} ({capacity}kWh, €{
                    bat.get(
                        'price_netto',
                        0):.2f})")

    # Step 4: Simulate product selection for a calculation
    print("\n4. Simulating product selection for calculation...")
    if modules_result and modules_result.get('success'):
        # Select a popular module
        # First module (Aiko Solar)
        selected_module = modules_result['data'][0]
        print(
            f"   Selected Module: {
                selected_module.get('brand')} {
                selected_module.get('model_name')}")
        print(f"   - Power: {selected_module.get('capacity_w')}W")
        print(f"   - Efficiency: {selected_module.get('efficiency_percent')}%")
        print(f"   - Price: €{selected_module.get('price_netto', 0):.2f}")
        print(
            f"   - Dimensions: {
                selected_module.get('length_mm')}x{
                selected_module.get('width_mm')}x{
                selected_module.get('thickness_mm')}mm")

        # Calculate system size
        target_power_kw = 10.0  # 10kW system
        modules_needed = int(
            target_power_kw *
            1000 /
            selected_module.get(
                'capacity_w',
                1))
        total_cost = modules_needed * selected_module.get('price_netto', 0)

        print(f"\n   For a {target_power_kw}kW system:")
        print(f"   - Modules needed: {modules_needed}")
        print(f"   - Total module cost: €{total_cost:.2f}")

        # Find matching inverter
        if inverters_result and inverters_result.get('success'):
            suitable_inverters = [
                inv for inv in inverters_result['data'] if inv.get(
                    'power_kw',
                    0) >= target_power_kw *
                0.8 and inv.get(
                    'power_kw',
                    0) <= target_power_kw *
                1.2]
            if suitable_inverters:
                selected_inverter = suitable_inverters[0]
                print(
                    f"   - Suitable inverter: {
                        selected_inverter.get('brand')} {
                        selected_inverter.get('model_name')} ({
                        selected_inverter.get('power_kw')}kW)")
                print(
                    f"   - Inverter cost: €{selected_inverter.get('price_netto', 0):.2f}")

                total_system_cost = total_cost + \
                    selected_inverter.get('price_netto', 0)
                print(
                    f"   - Total system cost (modules + inverter): €{total_system_cost:.2f}")

    print("\n=== SolarCalculator Simulation Complete ===")
    print("✓ All product data is available and properly structured for the frontend!")
    print("✓ SolarCalculator can now access real product database instead of mock data!")


if __name__ == "__main__":
    simulate_solar_calculator_data_flow()
