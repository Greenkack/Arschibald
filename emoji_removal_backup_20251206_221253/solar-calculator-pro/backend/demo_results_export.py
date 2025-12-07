"""
Demo script for Results Export System.

This script demonstrates all export formats and options.
"""

import asyncio
import json
from pathlib import Path

from services.export_service import ExportService
from models.export_schemas import (
    ExportRequest, PDFExportOptions, ExcelExportOptions,
    CSVExportOptions, JSONExportOptions, XMLExportOptions,
    BatchExportRequest
)


# Sample result data
SAMPLE_RESULT = {
    "id": 123,
    "title": "Solar Calculation Result #123",
    "summary": {
        "System Size": "10.5 kWp",
        "Annual Production": "12,500 kWh",
        "Total Cost": "16.999,00 €",
        "Payback Period": "8.5 years",
        "25-Year Savings": "45.000,00 €",
        "CO2 Savings": "125 tons",
        "Self-Consumption Rate": "65%",
        "Grid Feed-in": "4,375 kWh/year"
    },
    "tables": {
        "Monthly Production": [
            ["Month", "Production (kWh)", "Consumption (kWh)", "Grid Feed-in (kWh)", "Self-Consumption (%)"],
            ["January", "650", "400", "250", "61.5"],
            ["February", "800", "380", "420", "47.5"],
            ["March", "1100", "350", "750", "31.8"],
            ["April", "1250", "320", "930", "25.6"],
            ["May", "1400", "300", "1100", "21.4"],
            ["June", "1450", "280", "1170", "19.3"],
            ["July", "1500", "270", "1230", "18.0"],
            ["August", "1380", "290", "1090", "21.0"],
            ["September", "1150", "310", "840", "27.0"],
            ["October", "900", "340", "560", "37.8"],
            ["November", "700", "370", "330", "52.9"],
            ["December", "620", "390", "230", "62.9"]
        ],
        "Financial Analysis": [
            ["Year", "Production Value (€)", "Savings (€)", "Cumulative Savings (€)", "ROI (%)"],
            ["1", "2.500,00", "1.800,00", "1.800,00", "10.6"],
            ["2", "2.500,00", "1.800,00", "3.600,00", "21.2"],
            ["3", "2.500,00", "1.800,00", "5.400,00", "31.8"],
            ["5", "2.500,00", "1.800,00", "9.000,00", "52.9"],
            ["10", "2.500,00", "1.800,00", "18.000,00", "105.9"],
            ["15", "2.500,00", "1.800,00", "27.000,00", "158.8"],
            ["20", "2.500,00", "1.800,00", "36.000,00", "211.8"],
            ["25", "2.500,00", "1.800,00", "45.000,00", "264.7"]
        ],
        "System Components": [
            ["Component", "Manufacturer", "Model", "Quantity", "Unit Price (€)", "Total Price (€)"],
            ["PV Modules", "Trina Solar", "TSM-400W", "26", "180,00", "4.680,00"],
            ["Inverter", "SMA", "Sunny Tripower 10.0", "1", "2.500,00", "2.500,00"],
            ["Battery Storage", "BYD", "Battery-Box Premium HVS 10.2", "1", "6.500,00", "6.500,00"],
            ["Mounting System", "K2 Systems", "CrossRail", "1", "1.200,00", "1.200,00"],
            ["Installation", "Professional", "Full Service", "1", "2.119,00", "2.119,00"]
        ]
    },
    "chart_data": {
        "line_chart": {
            "title": "Monthly Energy Production",
            "x_label": "Month",
            "y_label": "Energy (kWh)",
            "data": [
                {"x": "Jan", "y": 650},
                {"x": "Feb", "y": 800},
                {"x": "Mar", "y": 1100},
                {"x": "Apr", "y": 1250},
                {"x": "May", "y": 1400},
                {"x": "Jun", "y": 1450},
                {"x": "Jul", "y": 1500},
                {"x": "Aug", "y": 1380},
                {"x": "Sep", "y": 1150},
                {"x": "Oct", "y": 900},
                {"x": "Nov", "y": 700},
                {"x": "Dec", "y": 620}
            ]
        }
    }
}


async def demo_pdf_export():
    """Demonstrate PDF export"""
    print("\n" + "="*60)
    print("PDF EXPORT DEMO")
    print("="*60)
    
    export_service = ExportService()
    
    request = ExportRequest(
        result_id=123,
        format='pdf',
        options={
            'include_charts': True,
            'include_tables': True,
            'include_summary': True,
            'page_size': 'A4',
            'orientation': 'portrait'
        }
    )
    
    response = await export_service.export_result(request, SAMPLE_RESULT)
    
    print(f"✅ PDF Export Created")
    print(f"   Export ID: {response.export_id}")
    print(f"   File Name: {response.file_name}")
    print(f"   File Size: {response.file_size:,} bytes")
    print(f"   Download URL: {response.download_url}")
    print(f"   Expires At: {response.expires_at}")


async def demo_excel_export():
    """Demonstrate Excel export"""
    print("\n" + "="*60)
    print("EXCEL EXPORT DEMO")
    print("="*60)
    
    export_service = ExportService()
    
    request = ExportRequest(
        result_id=123,
        format='excel',
        options={
            'include_charts': True,
            'include_formulas': False,
            'sheet_names': ['Summary', 'Monthly Data', 'Financial Analysis', 'Components'],
            'freeze_panes': True,
            'auto_filter': True
        }
    )
    
    response = await export_service.export_result(request, SAMPLE_RESULT)
    
    print(f"✅ Excel Export Created")
    print(f"   Export ID: {response.export_id}")
    print(f"   File Name: {response.file_name}")
    print(f"   File Size: {response.file_size:,} bytes")
    print(f"   Sheets: Summary, Monthly Data, Financial Analysis, Components")


async def demo_csv_export():
    """Demonstrate CSV export with German formatting"""
    print("\n" + "="*60)
    print("CSV EXPORT DEMO (German Formatting)")
    print("="*60)
    
    export_service = ExportService()
    
    request = ExportRequest(
        result_id=123,
        format='csv',
        options={
            'delimiter': ',',
            'encoding': 'utf-8',
            'include_headers': True,
            'decimal_separator': ',',
            'thousands_separator': '.'
        }
    )
    
    response = await export_service.export_result(request, SAMPLE_RESULT)
    
    print(f"✅ CSV Export Created")
    print(f"   Export ID: {response.export_id}")
    print(f"   File Name: {response.file_name}")
    print(f"   File Size: {response.file_size:,} bytes")
    print(f"   Formatting: German (16.999,00 €)")
    
    # Show sample content
    file_path = export_service.get_export_file(response.export_id)
    if file_path and file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:5]
            print("\n   Sample Content:")
            for line in lines:
                print(f"   {line.strip()}")


async def demo_json_export():
    """Demonstrate JSON export"""
    print("\n" + "="*60)
    print("JSON EXPORT DEMO")
    print("="*60)
    
    export_service = ExportService()
    
    request = ExportRequest(
        result_id=123,
        format='json',
        options={
            'pretty_print': True,
            'include_metadata': True,
            'date_format': 'iso'
        }
    )
    
    response = await export_service.export_result(request, SAMPLE_RESULT)
    
    print(f"✅ JSON Export Created")
    print(f"   Export ID: {response.export_id}")
    print(f"   File Name: {response.file_name}")
    print(f"   File Size: {response.file_size:,} bytes")
    
    # Show sample content
    file_path = export_service.get_export_file(response.export_id)
    if file_path and file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print("\n   Sample Content:")
            print(f"   Title: {data.get('title')}")
            print(f"   Summary Keys: {list(data.get('summary', {}).keys())}")
            if '_metadata' in data:
                print(f"   Metadata: {data['_metadata']}")


async def demo_xml_export():
    """Demonstrate XML export"""
    print("\n" + "="*60)
    print("XML EXPORT DEMO")
    print("="*60)
    
    export_service = ExportService()
    
    request = ExportRequest(
        result_id=123,
        format='xml',
        options={
            'root_element': 'calculation_result',
            'include_schema': False,
            'pretty_print': True
        }
    )
    
    response = await export_service.export_result(request, SAMPLE_RESULT)
    
    print(f"✅ XML Export Created")
    print(f"   Export ID: {response.export_id}")
    print(f"   File Name: {response.file_name}")
    print(f"   File Size: {response.file_size:,} bytes")
    
    # Show sample content
    file_path = export_service.get_export_file(response.export_id)
    if file_path and file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:10]
            print("\n   Sample Content:")
            for line in lines:
                print(f"   {line.rstrip()}")


async def demo_batch_export():
    """Demonstrate batch export"""
    print("\n" + "="*60)
    print("BATCH EXPORT DEMO")
    print("="*60)
    
    export_service = ExportService()
    
    # Create multiple result datasets
    results_data = [SAMPLE_RESULT.copy() for _ in range(3)]
    for i, result in enumerate(results_data, start=1):
        result['id'] = 120 + i
        result['title'] = f"Solar Calculation Result #{120 + i}"
    
    request = BatchExportRequest(
        result_ids=[121, 122, 123],
        format='pdf',
        options={'include_charts': True},
        combine_files=False
    )
    
    responses = await export_service.batch_export(request, results_data)
    
    print(f"✅ Batch Export Created ({len(responses)} files)")
    for i, response in enumerate(responses, start=1):
        print(f"\n   File {i}:")
        print(f"   - Export ID: {response.export_id}")
        print(f"   - File Name: {response.file_name}")
        print(f"   - File Size: {response.file_size:,} bytes")


async def demo_format_comparison():
    """Compare all export formats"""
    print("\n" + "="*60)
    print("FORMAT COMPARISON")
    print("="*60)
    
    export_service = ExportService()
    formats = ['pdf', 'excel', 'csv', 'json', 'xml']
    results = []
    
    for fmt in formats:
        request = ExportRequest(
            result_id=123,
            format=fmt,
            options={}
        )
        response = await export_service.export_result(request, SAMPLE_RESULT)
        results.append((fmt, response))
    
    print("\n{:<10} {:<40} {:<15}".format("Format", "File Name", "Size"))
    print("-" * 70)
    for fmt, response in results:
        print("{:<10} {:<40} {:>10,} bytes".format(
            fmt.upper(),
            response.file_name,
            response.file_size
        ))


async def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("RESULTS EXPORT SYSTEM - COMPLETE DEMO")
    print("="*60)
    print("\nDemonstrating all export formats with German number formatting")
    print("All numbers formatted as: 16.999,00 € (German standard)")
    
    await demo_pdf_export()
    await demo_excel_export()
    await demo_csv_export()
    await demo_json_export()
    await demo_xml_export()
    await demo_batch_export()
    await demo_format_comparison()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("\n✅ All export formats demonstrated successfully")
    print("📁 Export files saved in: exports/")
    print("⏰ Files expire after 24 hours")
    print("\nFor more information, see:")
    print("  - docs/RESULTS_EXPORT_GUIDE.md")
    print("  - docs/RESULTS_EXPORT_QUICK_REFERENCE.md")


if __name__ == "__main__":
    asyncio.run(main())
