"""
Debug script to check what data is being passed to ExtendedPDFGenerator
"""


def debug_project_data(project_data, analysis_results):
    """Print all price-related fields from project_data and analysis_results"""

    print("=" * 80)
    print("DEBUG: Extended PDF Data Analysis")
    print("=" * 80)

    print("\n1. ANALYSIS_RESULTS Price Fields:")
    print("-" * 80)
    if isinstance(analysis_results, dict):
        price_fields = [
            'final_price', 'final_price_netto', 'total_investment_brutto',
            'total_investment_netto', 'subtotal_netto', 'grand_total'
        ]
        for field in price_fields:
            value = analysis_results.get(field)
            print(f"  {field}: {value} (type: {type(value).__name__})")
    else:
        print(f"  analysis_results is not a dict: {type(analysis_results)}")

    print("\n2. OFFER_DATA (project_data) Price Fields:")
    print("-" * 80)
    if isinstance(project_data, dict):
        # Top level
        print("  Top level:")
        top_fields = ['grand_total', 'net_total', 'vat']
        for field in top_fields:
            value = project_data.get(field)
            print(f"    {field}: {value} (type: {type(value).__name__})")

        # pv_details
        print("\n  pv_details:")
        pv_details = project_data.get('pv_details', {})
        if isinstance(pv_details, dict):
            pv_fields = ['final_end_preis', 'total_price', 'net_price']
            for field in pv_fields:
                value = pv_details.get(field)
                print(f"    {field}: {value} (type: {type(value).__name__})")
            print(f"    Total keys in pv_details: {len(pv_details)}")
            print(f"    Keys: {list(pv_details.keys())[:10]}")  # First 10 keys
        else:
            print(f"    pv_details is not a dict: {type(pv_details)}")

        # project_details
        print("\n  project_details:")
        project_details = project_data.get('project_details', {})
        if isinstance(project_details, dict):
            proj_fields = [
                'final_end_preis',
                'final_offer_price_net',
                'total_price']
            for field in proj_fields:
                value = project_details.get(field)
                print(f"    {field}: {value} (type: {type(value).__name__})")
            print(f"    Total keys in project_details: {len(project_details)}")
            print(
                f"    Keys: {
                    list(
                        project_details.keys())[
                        :10]}")  # First 10 keys
        else:
            print(
                f"    project_details is not a dict: {
                    type(project_details)}")
    else:
        print(f"  project_data is not a dict: {type(project_data)}")

    print("\n3. RECOMMENDED FIX:")
    print("-" * 80)

    # Determine what value should be used
    final_price = None
    source = None

    if isinstance(analysis_results, dict):
        if analysis_results.get('final_price'):
            final_price = analysis_results.get('final_price')
            source = "analysis_results['final_price']"
        elif analysis_results.get('total_investment_brutto'):
            final_price = analysis_results.get('total_investment_brutto')
            source = "analysis_results['total_investment_brutto']"

    if not final_price and isinstance(project_data, dict):
        if project_data.get('grand_total'):
            final_price = project_data.get('grand_total')
            source = "project_data['grand_total']"

    if final_price:
        print(f"  ✅ Found price: {final_price:,.2f} € from {source}")
        print("  This value should be used for financing calculations")
    else:
        print("  ❌ No valid price found!")
        print("  Check your data structure")

    print("\n" + "=" * 80)


# Example usage - you can call this from pdf_generator.py
if __name__ == "__main__":
    # Test with sample data
    test_project_data = {
        'grand_total': 25000.0,
        'net_total': 21000.0,
        'vat': 4000.0,
        'pv_details': {
            'anlage_kwp': 10.5
        },
        'project_details': {
            'customer_name': 'Test Customer'
        }
    }

    test_analysis_results = {
        'final_price': 25000.0,
        'total_investment_brutto': 25000.0,
        'annual_pv_production_kwh': 10500
    }

    debug_project_data(test_project_data, test_analysis_results)
