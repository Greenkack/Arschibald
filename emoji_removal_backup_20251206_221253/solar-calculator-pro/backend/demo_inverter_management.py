"""
Demo Script for Inverter Management System

Demonstrates all key features of the inverter management system.

Requirements: 1.3, 6.1
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from services.inverter_service import InverterService
import json


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_json(data, indent=2):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=indent, ensure_ascii=False))


def demo_inverter_selection():
    """Demonstrate inverter selection"""
    print_section("1. INVERTER SELECTION")
    
    service = InverterService()
    
    # Create sample inverters
    sample_inverters = [
        {
            'id': 1,
            'model_name': 'Huawei SUN2000-10KTL-M1',
            'brand': 'Huawei',
            'power_kw': 10.0,
            'efficiency_percent': 98.6,
            'max_dc_voltage': 1100.0,
            'mppt_count': 2,
            'max_dc_current': 26.0,
            'price_euro': 2800.0,
            'additional_cost_netto': 100.0,
            'warranty_years': 10,
            'weight_kg': 17.0,
            'description': 'String inverter with smart features',
            'technology': 'String Inverter',
            'smart_home': True
        },
        {
            'id': 2,
            'model_name': 'SMA Sunny Tripower 10.0',
            'brand': 'SMA',
            'power_kw': 10.0,
            'efficiency_percent': 98.4,
            'max_dc_voltage': 1000.0,
            'mppt_count': 2,
            'max_dc_current': 33.0,
            'price_euro': 3200.0,
            'additional_cost_netto': 150.0,
            'warranty_years': 10,
            'weight_kg': 34.0,
            'description': 'Reliable string inverter',
            'technology': 'String Inverter',
            'smart_home': False
        },
        {
            'id': 3,
            'model_name': 'Fronius Symo 10.0-3-M',
            'brand': 'Fronius',
            'power_kw': 10.0,
            'efficiency_percent': 98.1,
            'max_dc_voltage': 1000.0,
            'mppt_count': 2,
            'max_dc_current': 28.0,
            'price_euro': 3000.0,
            'additional_cost_netto': 120.0,
            'warranty_years': 10,
            'weight_kg': 20.5,
            'description': 'Premium string inverter',
            'technology': 'String Inverter',
            'smart_home': True
        }
    ]
    
    # Mock the database query
    service._get_available_inverters = lambda: sample_inverters
    
    # Select inverter for 10kWp system
    print("Selecting inverter for 10kWp PV system...")
    result = service.select_inverter(pv_power_kwp=10.0)
    
    print(f"\n✓ Selected Inverter: {result['selected_inverter']['model_name']}")
    print(f"  Manufacturer: {result['selected_inverter']['manufacturer']}")
    print(f"  Power: {result['selected_inverter']['power_kw']}kW")
    print(f"  Efficiency: {result['selected_inverter']['efficiency_percent']}%")
    print(f"  Selection Score: {result['selection_score']:.1f}/100")
    print(f"  DC/AC Ratio: {result['sizing_ratio']:.2f}")
    
    print(f"\n{result['selection_reasoning']}")
    
    print(f"\nAlternatives ({len(result['alternatives'])}):")
    for i, alt in enumerate(result['alternatives'], 1):
        print(f"  {i}. {alt['inverter']['model_name']} (Score: {alt['score']:.1f})")
    
    return result['selected_inverter']


def demo_inverter_sizing():
    """Demonstrate inverter sizing calculations"""
    print_section("2. INVERTER SIZING CALCULATIONS")
    
    service = InverterService()
    
    # System configuration
    pv_power_kwp = 10.0
    module_voltage = 40.5  # Vmp
    module_current = 10.2  # Imp
    string_config = {
        'modules_per_string': 10,
        'number_of_strings': 2
    }
    
    print(f"PV System Configuration:")
    print(f"  Total Power: {pv_power_kwp}kWp")
    print(f"  Module Voltage (Vmp): {module_voltage}V")
    print(f"  Module Current (Imp): {module_current}A")
    print(f"  Modules per String: {string_config['modules_per_string']}")
    print(f"  Number of Strings: {string_config['number_of_strings']}")
    
    # Calculate sizing
    sizing = service.calculate_inverter_sizing(
        pv_power_kwp=pv_power_kwp,
        module_voltage=module_voltage,
        module_current=module_current,
        string_configuration=string_config
    )
    
    print(f"\n✓ Sizing Results:")
    print(f"\nRequired Inverter Power: {sizing['required_power_kw']}kW")
    
    print(f"\nRecommended Power Range:")
    print(f"  Minimum: {sizing['recommended_power_range']['min_kw']}kW")
    print(f"  Optimal: {sizing['recommended_power_range']['optimal_kw']}kW")
    print(f"  Maximum: {sizing['recommended_power_range']['max_kw']}kW")
    
    print(f"\nDC Specifications:")
    print(f"  String Voltage: {sizing['dc_specifications']['string_voltage']}V")
    print(f"  Required Max Voltage: {sizing['dc_specifications']['required_max_voltage']}V (with 20% margin)")
    print(f"  Total Current: {sizing['dc_specifications']['total_current']}A")
    print(f"  Required Max Current: {sizing['dc_specifications']['required_max_current']}A (with 10% margin)")
    
    print(f"\nMPPT Configuration:")
    print(f"  Recommended MPPT Count: {sizing['mppt_configuration']['recommended_mppt_count']}")
    print(f"  Strings per MPPT: {sizing['mppt_configuration']['strings_per_mppt']}")
    print(f"  Current per MPPT: {sizing['mppt_configuration']['current_per_mppt']}A")
    
    return sizing


def demo_compatibility_check(inverter):
    """Demonstrate compatibility checking"""
    print_section("3. COMPATIBILITY CHECK")
    
    service = InverterService()
    
    # PV system specifications
    pv_system = {
        'pv_power_kwp': 10.0,
        'string_voltage': 405.0,  # 10 modules × 40.5V
        'total_current': 20.4,    # 2 strings × 10.2A
        'number_of_strings': 2
    }
    
    print(f"Checking compatibility of {inverter['model_name']}...")
    print(f"\nPV System:")
    print(f"  Power: {pv_system['pv_power_kwp']}kWp")
    print(f"  String Voltage: {pv_system['string_voltage']}V")
    print(f"  Total Current: {pv_system['total_current']}A")
    print(f"  Number of Strings: {pv_system['number_of_strings']}")
    
    # Check compatibility
    compatibility = service.check_inverter_compatibility(
        inverter=inverter,
        pv_system=pv_system
    )
    
    print(f"\n✓ Compatibility Results:")
    print(f"\nOverall: {'✓ COMPATIBLE' if compatibility['is_compatible'] else '✗ NOT COMPATIBLE'}")
    print(f"Compatibility Score: {compatibility['compatibility_score']:.1f}%")
    
    print(f"\nDetailed Checks:")
    for check in compatibility['checks']:
        status_symbol = {
            'OK': '✓',
            'WARNUNG': '⚠',
            'FEHLER': '✗'
        }.get(check['status'], '?')
        print(f"  {status_symbol} {check['check']}: {check['status']}")
        print(f"     {check['details']}")
    
    if compatibility['warnings']:
        print(f"\nWarnings:")
        for warning in compatibility['warnings']:
            print(f"  ⚠ {warning}")
    
    print(f"\nRecommendation:")
    print(f"  {compatibility['recommendation']}")
    
    return compatibility


def demo_multi_inverter_configuration():
    """Demonstrate multi-inverter configuration"""
    print_section("4. MULTI-INVERTER CONFIGURATION")
    
    service = InverterService()
    
    # Create sample inverters
    sample_inverters = [
        {
            'id': 1,
            'model_name': 'Huawei SUN2000-10KTL-M1',
            'brand': 'Huawei',
            'power_kw': 10.0,
            'efficiency_percent': 98.6,
            'max_dc_voltage': 1100.0,
            'mppt_count': 2,
            'max_dc_current': 26.0,
            'price_euro': 2800.0,
            'additional_cost_netto': 100.0,
            'warranty_years': 10,
            'weight_kg': 17.0,
            'description': 'String inverter',
            'technology': 'String Inverter',
            'smart_home': True
        }
    ]
    
    service._get_available_inverters = lambda: sample_inverters
    
    # Large system with multiple roof sections
    system_layout = {
        'roof_sections': [
            {
                'section_id': 'South',
                'orientation': 180,
                'tilt': 30,
                'area_sqm': 100,
                'power_kwp': 20.0
            },
            {
                'section_id': 'East',
                'orientation': 90,
                'tilt': 30,
                'area_sqm': 100,
                'power_kwp': 20.0
            }
        ]
    }
    
    print("Configuring multi-inverter system...")
    print(f"\nSystem Layout:")
    print(f"  Total Power: 40kWp")
    print(f"  Roof Sections: {len(system_layout['roof_sections'])}")
    for section in system_layout['roof_sections']:
        print(f"    - {section['section_id']}: {section['power_kwp']}kWp, "
              f"Orientation: {section['orientation']}°, Tilt: {section['tilt']}°")
    
    # Create configuration
    config = service.create_multi_inverter_configuration(
        pv_power_kwp=40.0,
        system_layout=system_layout
    )
    
    print(f"\n✓ Multi-Inverter Configuration:")
    print(f"\nConfiguration Type: {config['configuration_type'].upper()}")
    print(f"Number of Inverters: {config['inverter_count']}")
    print(f"Total Inverter Power: {config['total_power_kw']}kW")
    
    if config.get('power_distribution'):
        print(f"\nPower Distribution:")
        for dist in config['power_distribution']:
            inverter = dist['inverter']
            section = dist.get('roof_section')
            print(f"  Inverter {dist['inverter_index'] + 1}: {inverter['model_name']}")
            print(f"    Power: {inverter['power_kw']}kW")
            print(f"    Assigned PV: {dist['assigned_power_kwp']}kWp")
            if section:
                print(f"    Roof Section: {section['section_id']}")
    
    print(f"\nReasoning:")
    for line in config['reasoning'].split('\n'):
        if line.strip():
            print(f"  {line}")
    
    return config


def demo_monitoring_integration(inverter):
    """Demonstrate monitoring integration"""
    print_section("5. MONITORING INTEGRATION")
    
    service = InverterService()
    
    # Monitoring configuration
    monitoring_config = {
        'protocol': 'Modbus TCP',
        'update_interval': 60,
        'retention_days': 365
    }
    
    print(f"Configuring monitoring for {inverter['model_name']}...")
    print(f"\nMonitoring Configuration:")
    print(f"  Protocol: {monitoring_config['protocol']}")
    print(f"  Update Interval: {monitoring_config['update_interval']}s")
    print(f"  Data Retention: {monitoring_config['retention_days']} days")
    
    # Integrate monitoring
    integration = service.integrate_monitoring(
        inverter=inverter,
        monitoring_config=monitoring_config
    )
    
    if integration['monitoring_supported']:
        print(f"\n✓ Monitoring Integration Successful")
        print(f"\nInverter: {integration['inverter_model']}")
        print(f"Manufacturer: {integration['manufacturer']}")
        print(f"Protocol: {integration['communication_protocol']}")
        
        print(f"\nData Points ({len(integration['data_points'])}):")
        for i, data_point in enumerate(integration['data_points'][:8], 1):
            print(f"  {i}. {data_point}")
        if len(integration['data_points']) > 8:
            print(f"  ... and {len(integration['data_points']) - 8} more")
        
        print(f"\nAlert Configuration:")
        for alert in integration['alerts']:
            threshold_str = f" (threshold: {alert['threshold']})" if alert['threshold'] else ""
            print(f"  • {alert['type']}{threshold_str}")
            print(f"    {alert['description']}")
        
        print(f"\nAPI Endpoints:")
        for name, endpoint in integration['api_endpoints'].items():
            print(f"  {name}: {endpoint}")
    else:
        print(f"\n✗ Monitoring Not Supported")
        print(f"  {integration['message']}")
        if integration.get('alternative'):
            print(f"  Alternative: {integration['alternative']}")
    
    return integration


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("  SOLAR INVERTER MANAGEMENT SYSTEM - DEMONSTRATION")
    print("=" * 80)
    
    try:
        # Demo 1: Inverter Selection
        selected_inverter = demo_inverter_selection()
        
        # Demo 2: Inverter Sizing
        sizing = demo_inverter_sizing()
        
        # Demo 3: Compatibility Check
        compatibility = demo_compatibility_check(selected_inverter)
        
        # Demo 4: Multi-Inverter Configuration
        multi_config = demo_multi_inverter_configuration()
        
        # Demo 5: Monitoring Integration
        monitoring = demo_monitoring_integration(selected_inverter)
        
        # Summary
        print_section("DEMONSTRATION COMPLETE")
        print("All inverter management features demonstrated successfully!")
        print("\nKey Features:")
        print("  ✓ Intelligent inverter selection with scoring")
        print("  ✓ Detailed sizing calculations with safety margins")
        print("  ✓ Comprehensive compatibility checking")
        print("  ✓ Multi-inverter configuration for large systems")
        print("  ✓ Monitoring system integration")
        
        print("\nFor more information, see:")
        print("  - docs/INVERTER_MANAGEMENT_GUIDE.md")
        print("  - docs/INVERTER_MANAGEMENT_QUICK_REFERENCE.md")
        print("  - tests/test_inverter_service.py")
        
    except Exception as e:
        print(f"\n✗ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
