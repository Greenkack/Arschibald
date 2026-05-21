"""
Demo: Multi-PDF Batch Generation

This demo shows how to use the batch PDF generation system to create
multiple PDFs for different companies with a single request.

**Concept**: One click → All selected company PDFs generated simultaneously

**Example**: 8 companies selected → 8 PDFs with one click

**Features**:
- Same analysis data for all offers
- Company-specific branding and data
- Automatic product rotation (different products per offer)
- Automatic price increase (each offer more expensive)
- Parallel generation for performance
- Progress tracking
- ZIP download with all PDFs
- Individual PDF downloads
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.batch_pdf_service import (
    BatchPDFService,
    BatchPDFRequest
)


# Mock services for demo
class MockPDFService:
    """Mock PDF service"""
    def generate_pdf(self, template_type, data, options):
        """Generate mock PDF"""
        import time
        time.sleep(0.1)  # Simulate PDF generation time
        
        company_name = data.get("company", {}).get("name", "Unknown")
        price = data.get("total_price", 0)
        
        content = f"""
        PDF for {company_name}
        Offer #{data.get('offer_number', 1)}
        Price: {price:,.2f} €
        Products: {data.get('products', {})}
        """.encode('utf-8')
        
        return content


class MockCompanyService:
    """Mock company service"""
    def get_company(self, company_id):
        """Get mock company"""
        from types import SimpleNamespace
        
        companies = {
            1: {"name": "Solar Solutions GmbH", "color": "#FF5733"},
            2: {"name": "Green Energy AG", "color": "#33FF57"},
            3: {"name": "Eco Power Systems", "color": "#3357FF"},
            4: {"name": "Renewable Tech Ltd", "color": "#FF33F5"},
            5: {"name": "Sun Power Pro", "color": "#F5FF33"},
            6: {"name": "Energy Future GmbH", "color": "#33FFF5"},
            7: {"name": "Solar Experts AG", "color": "#FF8C33"},
            8: {"name": "Clean Energy Solutions", "color": "#8C33FF"},
        }
        
        if company_id not in companies:
            return None
        
        company_data = companies[company_id]
        company = SimpleNamespace(
            id=company_id,
            name=company_data["name"],
            logo_path=f"/logos/company_{company_id}.png",
            branding={"color": company_data["color"]}
        )
        company.dict = lambda: {
            "id": company_id,
            "name": company_data["name"],
            "logo_path": f"/logos/company_{company_id}.png",
            "branding": {"color": company_data["color"]}
        }
        
        return company


class MockProductRotationService:
    """Mock product rotation service"""
    def rotate_products(self, products, offer_index):
        """Rotate products for each offer"""
        modules = ["Trina Solar 400W", "JA Solar 410W", "Longi 420W", "Canadian Solar 405W"]
        inverters = ["Fronius Symo", "SMA Sunny Tripower", "Huawei SUN2000", "SolarEdge SE"]
        batteries = ["BYD Battery-Box", "Tesla Powerwall", "Sonnen Batterie", "LG Chem RESU"]
        
        return {
            "pv_module": modules[offer_index % len(modules)],
            "inverter": inverters[offer_index % len(inverters)],
            "battery": batteries[offer_index % len(batteries)]
        }


class MockPriceIncreaseService:
    """Mock price increase service"""
    def apply_increase(self, base_price, offer_index, increase_percentage):
        """Apply price increase"""
        # Each subsequent offer is more expensive
        multiplier = 1 + (increase_percentage / 100) * offer_index
        return base_price * multiplier


async def demo_basic_batch():
    """Demo: Basic batch PDF generation"""
    print("\n" + "="*80)
    print("DEMO 1: Basic Batch PDF Generation")
    print("="*80)
    
    # Create service
    service = BatchPDFService(
        pdf_service=MockPDFService(),
        company_service=MockCompanyService(),
        product_rotation_service=MockProductRotationService(),
        price_increase_service=MockPriceIncreaseService(),
        max_workers=4
    )
    
    # Create request for 3 companies
    request = BatchPDFRequest(
        company_ids=[1, 2, 3],
        analysis_data={
            "roof_area": 50.0,
            "roof_type": "gable",
            "module_count": 30,
            "annual_consumption": 4500.0,
            "base_price": 16999.00,
            "products": {
                "pv_module": "Trina Solar 400W",
                "inverter": "Fronius Symo",
                "battery": "BYD Battery-Box"
            }
        },
        template_type="standard_pv",
        options={"price_increase_percentage": 7.0}
    )
    
    print(f"\n Request:")
    print(f"   Companies: {request.company_ids}")
    print(f"   Base Price: {request.analysis_data['base_price']:,.2f} €")
    print(f"   Price Increase: {request.options['price_increase_percentage']}%")
    
    # Generate batch
    print(f"\n Starting batch generation...")
    result = await service.generate_batch(request)
    
    # Display results
    print(f"\n Batch Generation Complete!")
    print(f"   Batch ID: {result.batch_id}")
    print(f"   Total Companies: {result.total_companies}")
    print(f"   Successful: {result.successful}")
    print(f"   Failed: {result.failed}")
    print(f"   Total Time: {result.total_time:.2f}s")
    print(f"   ZIP Size: {result.zip_size:,} bytes")
    
    print(f"\n Individual Results:")
    for i, company_result in enumerate(result.results, 1):
        status = "" if company_result.success else ""
        print(f"   {status} {company_result.company_name}")
        if company_result.success:
            print(f"      File: {Path(company_result.pdf_path).name}")
            print(f"      Size: {company_result.file_size:,} bytes")
            print(f"      Time: {company_result.generation_time:.2f}s")
        else:
            print(f"      Error: {company_result.error_message}")


async def demo_large_batch():
    """Demo: Large batch with 8 companies"""
    print("\n" + "="*80)
    print("DEMO 2: Large Batch (8 Companies)")
    print("="*80)
    
    # Create service
    service = BatchPDFService(
        pdf_service=MockPDFService(),
        company_service=MockCompanyService(),
        product_rotation_service=MockProductRotationService(),
        price_increase_service=MockPriceIncreaseService(),
        max_workers=4
    )
    
    # Create request for 8 companies
    request = BatchPDFRequest(
        company_ids=list(range(1, 9)),  # Companies 1-8
        analysis_data={
            "roof_area": 75.0,
            "module_count": 40,
            "base_price": 22999.00,
            "products": {
                "pv_module": "JA Solar 410W",
                "inverter": "SMA Sunny Tripower",
                "battery": "Tesla Powerwall"
            }
        },
        template_type="standard_pv",
        options={"price_increase_percentage": 7.0}
    )
    
    print(f"\n Request:")
    print(f"   Companies: {len(request.company_ids)}")
    print(f"   Base Price: {request.analysis_data['base_price']:,.2f} €")
    
    # Generate batch
    print(f"\n Starting batch generation...")
    result = await service.generate_batch(request)
    
    # Display results
    print(f"\n Batch Generation Complete!")
    print(f"   Total Time: {result.total_time:.2f}s")
    print(f"   Average Time per PDF: {result.total_time / result.total_companies:.2f}s")
    print(f"   ZIP Size: {result.zip_size:,} bytes")
    
    print(f"\n Price Progression (7% increase per offer):")
    for i, company_result in enumerate(result.results, 1):
        if company_result.success:
            print(f"   Offer {i}: {company_result.company_name}")


async def demo_progress_tracking():
    """Demo: Progress tracking during generation"""
    print("\n" + "="*80)
    print("DEMO 3: Progress Tracking")
    print("="*80)
    
    # Create service
    service = BatchPDFService(
        pdf_service=MockPDFService(),
        company_service=MockCompanyService(),
        product_rotation_service=MockProductRotationService(),
        price_increase_service=MockPriceIncreaseService(),
        max_workers=2  # Slower for demo
    )
    
    # Create request
    request = BatchPDFRequest(
        company_ids=[1, 2, 3, 4, 5],
        analysis_data={"base_price": 16999.00},
        template_type="standard_pv"
    )
    
    print(f"\n Generating PDFs for {len(request.company_ids)} companies...")
    
    # Start generation in background
    task = asyncio.create_task(service.generate_batch(request))
    
    # Track progress
    batch_id = None
    while not task.done():
        await asyncio.sleep(0.2)
        
        # Get batch ID from progress tracker
        if not batch_id and service.progress_tracker:
            batch_id = list(service.progress_tracker.keys())[0]
        
        if batch_id:
            progress = service.get_progress(batch_id)
            if progress:
                print(f"\r   Progress: {progress.completed}/{progress.total} "
                      f"({progress.percentage:.1f}%) - {progress.status}", end="")
    
    print()  # New line
    
    # Get result
    result = await task
    
    print(f"\n Complete!")
    print(f"   Total Time: {result.total_time:.2f}s")


async def demo_product_rotation():
    """Demo: Product rotation across offers"""
    print("\n" + "="*80)
    print("DEMO 4: Product Rotation")
    print("="*80)
    
    # Create service
    service = BatchPDFService(
        pdf_service=MockPDFService(),
        company_service=MockCompanyService(),
        product_rotation_service=MockProductRotationService(),
        price_increase_service=MockPriceIncreaseService(),
        max_workers=4
    )
    
    # Create request
    request = BatchPDFRequest(
        company_ids=[1, 2, 3, 4],
        analysis_data={
            "base_price": 16999.00,
            "products": {
                "pv_module": "Trina Solar 400W",
                "inverter": "Fronius Symo",
                "battery": "BYD Battery-Box"
            }
        },
        template_type="standard_pv"
    )
    
    print(f"\n Original Products:")
    print(f"   PV Module: {request.analysis_data['products']['pv_module']}")
    print(f"   Inverter: {request.analysis_data['products']['inverter']}")
    print(f"   Battery: {request.analysis_data['products']['battery']}")
    
    # Generate batch
    result = await service.generate_batch(request)
    
    print(f"\n Rotated Products per Offer:")
    rotation_service = MockProductRotationService()
    for i in range(4):
        rotated = rotation_service.rotate_products(request.analysis_data["products"], i)
        print(f"\n   Offer {i+1}:")
        print(f"      PV Module: {rotated['pv_module']}")
        print(f"      Inverter: {rotated['inverter']}")
        print(f"      Battery: {rotated['battery']}")


async def demo_price_increase():
    """Demo: Price increase across offers"""
    print("\n" + "="*80)
    print("DEMO 5: Price Increase (7% per offer)")
    print("="*80)
    
    base_price = 16999.00
    increase_percentage = 7.0
    
    print(f"\n Base Price: {base_price:,.2f} €")
    print(f" Increase: {increase_percentage}% per offer")
    
    price_service = MockPriceIncreaseService()
    
    print(f"\n Price Progression:")
    for i in range(5):
        price = price_service.apply_increase(base_price, i, increase_percentage)
        increase = price - base_price
        percentage = (increase / base_price) * 100
        
        print(f"   Offer {i+1}: {price:,.2f} € (+{increase:,.2f} € / +{percentage:.1f}%)")


async def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("MULTI-PDF BATCH GENERATION DEMO")
    print("="*80)
    print("\nThis demo shows how to generate multiple PDFs for different companies")
    print("with a single request, featuring:")
    print("  • Parallel PDF generation")
    print("  • Progress tracking")
    print("  • Product rotation")
    print("  • Automatic price increase")
    print("  • ZIP download")
    
    try:
        await demo_basic_batch()
        await demo_large_batch()
        await demo_progress_tracking()
        await demo_product_rotation()
        await demo_price_increase()
        
        print("\n" + "="*80)
        print("ALL DEMOS COMPLETED SUCCESSFULLY! ")
        print("="*80)
        
    except Exception as e:
        print(f"\n Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
