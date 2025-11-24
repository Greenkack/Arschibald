#!/usr/bin/env python3
"""
Demo script for Results Reporting System

This script demonstrates all report types and formats.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models.report_schemas import (
    ReportGenerationRequest, ReportType, ReportFormat
)
from backend.services.report_generation_service import ReportGenerationService


# Sample project data
SAMPLE_PROJECT = {
    "name": "Residential Solar Installation - Berlin",
    "customer_name": "Max Mustermann",
    "location": "Berlin, Germany",
    "system_size": 10.5,
    "module_count": 30,
    "module_type": "Premium 350W Monocrystalline",
    "module_power": 350,
    "module_efficiency": 21.5,
    "module_dimensions": "1722 x 1134 x 30 mm",
    "inverter": "SMA Sunny Tripower 10.0",
    "inverter_power": 10000,
    "inverter_efficiency": 98.3,
    "battery": "Tesla Powerwall 2 (13.5 kWh)",
    "mounting_type": "Roof-mounted with aluminum rails",
    "roof_type": "Pitched roof",
    "roof_area": 60.0,
    "roof_angle": 30.0,
    "orientation": "South",
    "shading_factor": 0.95,
    "annual_production": 12500,
    "specific_yield": 1190,
    "self_consumption_rate": 0.35,
    "grid_feed_in": 8125,
    "performance_ratio": 0.85,
    "total_cost": 16999.00,
    "equipment_cost": 13500.00,
    "installation_cost": 2500.00,
    "other_costs": 999.00,
    "module_cost": 6000.00,
    "inverter_cost": 2500.00,
    "battery_cost": 5000.00,
    "mounting_cost": 1500.00,
    "permit_cost": 499.00,
    "annual_savings": 1850.00,
    "payback_period": 9.2,
    "roi_25_years": 245.5,
    "roi_percentage": 245.5,
    "npv": 25000.00,
    "irr": 0.12,
    "co2_savings": 6250,
    "co2_savings_25_years": 156250,
    "trees_equivalent": 312,
    "cars_equivalent": 1,
    "fossil_fuel_avoided": 5000,
    "water_saved": 15000,
    "renewable_percentage": 85.0,
    "energy_payback_time": 2.5,
    "co2_payback_time": 1.8,
    "recommendations": [
        "System is optimally sized for your annual consumption of 4,500 kWh",
        "Battery storage increases self-consumption from 35% to 65%",
        "South orientation provides maximum energy yield",
        "Regular maintenance recommended every 6 months",
        "Consider adding 2-3 more modules if consumption increases"
    ],
    "monthly_production": [800, 950, 1200, 1350, 1450, 1500, 1480, 1400, 1250, 1050, 850, 750],
    "cost_breakdown": {
        "PV Modules": 6000,
        "Inverter": 2500,
        "Battery Storage": 5000,
        "Mounting System": 1500,
        "Installation": 2500,
        "Permits & Fees": 499
    },
    "annual_cash_flows": [-16999, 1850, 1900, 1950, 2000, 2050, 2100, 2150, 2200, 2250, 2300],
    "cumulative_cash_flow": [-16999, -15149, -13249, -11299, -9299, -7249, -5149, -2999, -799, 1451, 3751]
}


async def demo_all_reports():
    """Generate all report types in all formats"""
    
    print("=" * 80)
    print("RESULTS REPORTING SYSTEM - DEMO")
    print("=" * 80)
    print()
    
    service = ReportGenerationService()
    
    # Report types to generate
    report_types = [
        (ReportType.DETAILED, "Detailed Report"),
        (ReportType.EXECUTIVE, "Executive Summary"),
        (ReportType.TECHNICAL, "Technical Report"),
        (ReportType.FINANCIAL, "Financial Report"),
        (ReportType.ENVIRONMENTAL, "Environmental Report"),
    ]
    
    # Formats to generate
    formats = [
        (ReportFormat.PDF, "PDF"),
        (ReportFormat.HTML, "HTML"),
        (ReportFormat.JSON, "JSON"),
        (ReportFormat.EXCEL, "Excel"),
        (ReportFormat.CSV, "CSV"),
    ]
    
    generated_reports = []
    
    # Generate one of each report type in PDF format
    print("Generating reports...")
    print()
    
    for report_type, type_name in report_types:
        print(f"📄 Generating {type_name}...")
        
        request = ReportGenerationRequest(
            project_id=1,
            report_type=report_type,
            format=ReportFormat.PDF,
            include_charts=True,
            include_tables=True,
            language="de"
        )
        
        try:
            result = await service.generate_report(
                request=request,
                project_data=SAMPLE_PROJECT,
                user_id="demo_user"
            )
            
            generated_reports.append(result)
            
            print(f"   ✅ Generated: {result.report_id}")
            print(f"   📊 Size: {result.metadata.file_size:,} bytes")
            print(f"   📥 Download: {result.download_url}")
            print()
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            print()
    
    # Generate detailed report in all formats
    print("=" * 80)
    print("Generating Detailed Report in all formats...")
    print()
    
    for format_type, format_name in formats:
        print(f"📄 Generating {format_name} format...")
        
        request = ReportGenerationRequest(
            project_id=1,
            report_type=ReportType.DETAILED,
            format=format_type,
            include_charts=True,
            include_tables=True,
            language="de"
        )
        
        try:
            result = await service.generate_report(
                request=request,
                project_data=SAMPLE_PROJECT,
                user_id="demo_user"
            )
            
            generated_reports.append(result)
            
            print(f"   ✅ Generated: {result.report_id}")
            print(f"   📊 Size: {result.metadata.file_size:,} bytes")
            print(f"   📥 Download: {result.download_url}")
            print()
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total reports generated: {len(generated_reports)}")
    print(f"Total size: {sum(r.metadata.file_size or 0 for r in generated_reports):,} bytes")
    print()
    print("Reports saved to: ./reports/")
    print()
    
    # Display sample data
    print("=" * 80)
    print("SAMPLE PROJECT DATA")
    print("=" * 80)
    print(f"Project: {SAMPLE_PROJECT['name']}")
    print(f"Customer: {SAMPLE_PROJECT['customer_name']}")
    print(f"Location: {SAMPLE_PROJECT['location']}")
    print()
    print(f"System Size: {SAMPLE_PROJECT['system_size']} kWp")
    print(f"Module Count: {SAMPLE_PROJECT['module_count']}")
    print(f"Annual Production: {SAMPLE_PROJECT['annual_production']:,} kWh")
    print()
    print(f"Total Cost: €{SAMPLE_PROJECT['total_cost']:,.2f}")
    print(f"Annual Savings: €{SAMPLE_PROJECT['annual_savings']:,.2f}")
    print(f"Payback Period: {SAMPLE_PROJECT['payback_period']:.1f} years")
    print(f"ROI (25 years): {SAMPLE_PROJECT['roi_percentage']:.1f}%")
    print()
    print(f"CO₂ Savings: {SAMPLE_PROJECT['co2_savings']:,} kg/year")
    print(f"Trees Equivalent: {SAMPLE_PROJECT['trees_equivalent']}")
    print()
    
    return generated_reports


async def demo_custom_report():
    """Generate a custom report with specific sections"""
    
    print("=" * 80)
    print("CUSTOM REPORT DEMO")
    print("=" * 80)
    print()
    
    from backend.models.report_schemas import ReportSection
    
    service = ReportGenerationService()
    
    # Define custom sections
    custom_sections = [
        ReportSection(
            title="Executive Overview",
            content={
                "system_size": SAMPLE_PROJECT["system_size"],
                "total_cost": SAMPLE_PROJECT["total_cost"],
                "annual_savings": SAMPLE_PROJECT["annual_savings"],
                "payback_period": SAMPLE_PROJECT["payback_period"]
            },
            order=1,
            visible=True,
            charts=[
                {
                    "type": "pie",
                    "title": "Cost Distribution",
                    "data": SAMPLE_PROJECT["cost_breakdown"]
                }
            ]
        ),
        ReportSection(
            title="Environmental Impact",
            content={
                "co2_savings": SAMPLE_PROJECT["co2_savings"],
                "trees_equivalent": SAMPLE_PROJECT["trees_equivalent"],
                "cars_equivalent": SAMPLE_PROJECT["cars_equivalent"]
            },
            order=2,
            visible=True,
            charts=[
                {
                    "type": "bar",
                    "title": "CO₂ Savings",
                    "data": {"Annual": SAMPLE_PROJECT["co2_savings"]}
                }
            ]
        )
    ]
    
    request = ReportGenerationRequest(
        project_id=1,
        report_type=ReportType.CUSTOM,
        format=ReportFormat.PDF,
        custom_sections=custom_sections,
        include_charts=True,
        include_tables=False,
        language="de"
    )
    
    print("Generating custom report with 2 sections...")
    
    try:
        result = await service.generate_report(
            request=request,
            project_data=SAMPLE_PROJECT,
            user_id="demo_user"
        )
        
        print(f"✅ Generated: {result.report_id}")
        print(f"📊 Size: {result.metadata.file_size:,} bytes")
        print(f"📥 Download: {result.download_url}")
        print()
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print()
        return None


async def main():
    """Main demo function"""
    
    print()
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "RESULTS REPORTING SYSTEM DEMO" + " " * 29 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    # Generate all standard reports
    reports = await demo_all_reports()
    
    # Generate custom report
    custom_report = await demo_custom_report()
    
    print("=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print()
    print("✅ All reports generated successfully!")
    print()
    print("Next steps:")
    print("1. Check the ./reports/ directory for generated files")
    print("2. Open PDF files to view formatted reports")
    print("3. Open HTML files in browser for web preview")
    print("4. Open JSON files to see data structure")
    print("5. Open Excel files for data analysis")
    print()
    print("For more information, see:")
    print("- docs/RESULTS_REPORTING_GUIDE.md")
    print("- docs/RESULTS_REPORTING_QUICK_REFERENCE.md")
    print()


if __name__ == "__main__":
    asyncio.run(main())
