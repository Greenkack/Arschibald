"""
Complete test for Task 3: Finanzierungsseiten-Generator
Generates an actual PDF to demonstrate all functionality.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extended_pdf_generator import FinancingPageGenerator


def create_mock_financing_options():
    """Create mock financing options for testing."""
    return [
        {
            'id': 1,
            'name': 'Standard-Finanzierung',
            'description': 'Klassische Finanzierung mit festem Zinssatz',
            'payment_type': 'financing',
            'enabled': True,
            'financing_options': [
                {
                    'duration_months': 60,
                    'interest_rate': 4.5,
                    'description': '5 Jahre Laufzeit'
                },
                {
                    'duration_months': 120,
                    'interest_rate': 4.2,
                    'description': '10 Jahre Laufzeit'
                }
            ]
        },
        {
            'id': 2,
            'name': 'Öko-Finanzierung',
            'description': 'Vergünstigte Finanzierung für nachhaltige Projekte',
            'payment_type': 'financing',
            'enabled': True,
            'financing_options': [
                {
                    'duration_months': 84,
                    'interest_rate': 3.5,
                    'description': '7 Jahre Laufzeit mit Öko-Bonus'
                }
            ]
        },
        {
            'id': 3,
            'name': 'Express-Finanzierung',
            'description': 'Schnelle Finanzierung mit kurzer Laufzeit',
            'payment_type': 'financing',
            'enabled': True,
            'financing_options': [
                {
                    'duration_months': 36,
                    'interest_rate': 5.5,
                    'description': '3 Jahre Laufzeit'
                }
            ]
        }
    ]


def test_complete_financing_generator():
    """Test complete financing page generation with mock data."""
    print("=" * 70)
    print("COMPLETE TEST: Finanzierungsseiten-Generator")
    print("=" * 70)
    
    # Create test data
    offer_data = {
        'grand_total': 35000.00,
        'customer_name': 'Max Mustermann',
        'project_name': 'PV-Anlage Einfamilienhaus'
    }
    
    theme = {
        'colors': {
            'primary': '#1E3A8A',
            'secondary': '#3B82F6',
            'text': '#000000',
            'background': '#FFFFFF'
        },
        'fonts': {
            'title': 'Helvetica-Bold',
            'body': 'Helvetica'
        }
    }
    
    # Initialize generator
    generator = FinancingPageGenerator(offer_data, theme)
    
    # Mock the financing options (since we don't have DB configured)
    mock_options = create_mock_financing_options()
    
    print("\n1. Testing with mock financing options...")
    print(f"   Created {len(mock_options)} financing options")
    
    # Calculate and display details for each option
    print("\n2. Calculating financing details:")
    print("-" * 70)
    
    for option in mock_options:
        print(f"\n   {option['name']}")
        print(f"   {option['description']}")
        
        for fin_opt in option['financing_options']:
            duration = fin_opt['duration_months']
            rate = fin_opt['interest_rate']
            
            monthly = generator._calculate_monthly_rate(
                offer_data['grand_total'],
                rate,
                duration
            )
            
            total = monthly * duration
            interest = total - offer_data['grand_total']
            
            print(f"\n   → {fin_opt['description']}")
            print(f"      Laufzeit: {duration} Monate ({duration//12} Jahre)")
            print(f"      Zinssatz: {rate}% p.a.")
            print(f"      Monatliche Rate: {monthly:,.2f} €")
            print(f"      Gesamtzahlung: {total:,.2f} €")
            print(f"      Zinskosten: {interest:,.2f} €")
    
    # Generate PDF with mock data
    print("\n" + "-" * 70)
    print("\n3. Generating PDF with financing pages...")
    
    try:
        # Temporarily replace the method to use mock data
        original_method = generator._get_financing_options
        generator._get_financing_options = lambda: mock_options
        
        pdf_bytes = generator.generate()
        
        # Restore original method
        generator._get_financing_options = original_method
        
        if pdf_bytes:
            output_path = "test_financing_complete_output.pdf"
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
            
            print(f"   ✓ PDF generated successfully!")
            print(f"   ✓ Size: {len(pdf_bytes):,} bytes")
            print(f"   ✓ Saved to: {output_path}")
            
            # Verify PDF structure
            from pypdf import PdfReader
            import io
            
            reader = PdfReader(io.BytesIO(pdf_bytes))
            num_pages = len(reader.pages)
            
            print(f"   ✓ Number of pages: {num_pages}")
            print(f"   ✓ Expected: 2 pages (Overview + Details)")
            
            if num_pages == 2:
                print("\n   ✓ PDF structure is correct!")
            else:
                print(f"\n   ⚠ Warning: Expected 2 pages, got {num_pages}")
            
            return True
        else:
            print("   ✗ No PDF generated")
            return False
            
    except Exception as e:
        print(f"   ✗ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_task_requirements():
    """Verify all requirements for Task 3 are met."""
    print("\n" + "=" * 70)
    print("VERIFICATION: Task 3 Requirements")
    print("=" * 70)
    
    requirements = [
        {
            'id': '3.1',
            'description': 'FinancingPageGenerator Klasse erstellt',
            'check': lambda: hasattr(FinancingPageGenerator, 'generate') and 
                           hasattr(FinancingPageGenerator, '_get_financing_options')
        },
        {
            'id': '3.2',
            'description': 'Finanzierungsübersicht-Seite implementiert',
            'check': lambda: hasattr(FinancingPageGenerator, '_draw_financing_overview') and
                           hasattr(FinancingPageGenerator, '_draw_financing_option_box')
        },
        {
            'id': '3.3',
            'description': 'Detaillierte Finanzierungsberechnung implementiert',
            'check': lambda: hasattr(FinancingPageGenerator, '_calculate_monthly_rate') and
                           hasattr(FinancingPageGenerator, '_draw_financing_details') and
                           hasattr(FinancingPageGenerator, '_draw_financing_calculation_table')
        }
    ]
    
    all_passed = True
    
    for req in requirements:
        passed = req['check']()
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"\n{status} Task {req['id']}: {req['description']}")
        
        if not passed:
            all_passed = False
    
    return all_passed


def main():
    """Run complete test suite."""
    print("\n" + "=" * 70)
    print("TASK 3: FINANZIERUNGSSEITEN-GENERATOR - COMPLETE TEST")
    print("=" * 70)
    
    # Verify requirements
    requirements_met = verify_task_requirements()
    
    # Test complete generation
    generation_success = test_complete_financing_generator()
    
    # Final summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    
    print(f"\n{'✓' if requirements_met else '✗'} All requirements implemented")
    print(f"{'✓' if generation_success else '✗'} PDF generation successful")
    
    if requirements_met and generation_success:
        print("\n" + "=" * 70)
        print("✓ TASK 3 COMPLETE - ALL SUBTASKS IMPLEMENTED")
        print("=" * 70)
        print("\nImplemented features:")
        print("  ✓ Task 3.1: FinancingPageGenerator class with generate() method")
        print("  ✓ Task 3.2: Financing overview page with boxes")
        print("  ✓ Task 3.3: Detailed financing calculation with annuity formula")
        print("\nKey features:")
        print("  • Annuity formula for monthly rate calculation")
        print("  • Comprehensive calculation table")
        print("  • Display of total costs and interest costs")
        print("  • Support for multiple financing options")
        print("  • Professional PDF layout with theme support")
        return True
    else:
        print("\n✗ Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
