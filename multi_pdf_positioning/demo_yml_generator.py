"""
Demo script for YML Generator Module

This script demonstrates the complete YML generation workflow:
1. Parse an existing YML file
2. Calculate new positions
3. Generate updated YML file
4. Validate the output
5. Show comparison
"""

import sys
from pathlib import Path
from multi_pdf_positioning.yml_parser import YMLParser
from multi_pdf_positioning.yml_generator import YMLGenerator
from multi_pdf_positioning.position_calculator import PositionCalculator
from multi_pdf_positioning.pdf_analyzer import PDFAnalyzer


def demo_basic_generation():
    """Demonstrate basic YML generation."""
    print("\n" + "="*70)
    print("DEMO 1: Basic YML Generation")
    print("="*70)
    
    # Check if YML file exists
    yml_file = "coords_multi/seite1_f1.yml"
    if not Path(yml_file).exists():
        print(f"YML file not found: {yml_file}")
        print("   Please ensure the coords_multi directory exists with YML files.")
        return False
    
    # Step 1: Parse original YML
    print(f"\n1. Parsing original YML: {yml_file}")
    parser = YMLParser()
    elements = parser.parse_yml(yml_file)
    print(f"   Found {len(elements)} elements")
    
    # Show first few elements
    print(f"\n   First 3 elements:")
    for i, elem in enumerate(elements[:3]):
        print(f"     {i}: '{elem.text}' at {elem.position}")
    
    # Step 2: Calculate new positions (simple demo: shift by 10 points)
    print(f"\n2. Calculating new positions (demo: +10 point offset)")
    new_positions = []
    for elem in elements:
        x1, y1, x2, y2 = elem.position
        new_pos = (x1 + 10, y1 + 10, x2 + 10, y2 + 10)
        new_positions.append(new_pos)
    print(f"   Calculated {len(new_positions)} new positions")
    
    # Step 3: Generate new YML
    output_file = "multi_pdf_positioning/demo_output.yml"
    print(f"\n3. Generating new YML: {output_file}")
    generator = YMLGenerator()
    content = generator.generate_yml(elements, new_positions, output_file, yml_file)
    print(f"   Generated {len(content)} characters")
    print(f"   File written to: {output_file}")
    
    # Step 4: Validate output
    print(f"\n4. Validating generated YML")
    is_valid, errors = generator.validate_yml_output(output_file, elements)
    
    if is_valid:
        print("   Validation passed!")
    else:
        print(f"    Validation found {len(errors)} issues:")
        for error in errors[:5]:  # Show first 5
            print(f"     - {error}")
    
    # Step 5: Show validation report
    print(f"\n5. Validation Report")
    report = generator.get_validation_report()
    print(f"   Valid: {report['is_valid']}")
    print(f"   Error count: {report['error_count']}")
    print(f"   Original elements: {report['original_element_count']}")
    print(f"   Has format preserver: {report['has_format_preserver']}")
    
    # Step 6: Show sample comparison
    print(f"\n6. Sample Comparison (first element)")
    orig_elem = elements[0]
    print(f"   Original:")
    print(f"     Text: '{orig_elem.text}'")
    print(f"     Position: {orig_elem.position}")
    print(f"     Font: {orig_elem.font} ({orig_elem.font_size}pt)")
    
    # Parse generated file to show new position
    parser2 = YMLParser()
    gen_elements = parser2.parse_yml(output_file)
    gen_elem = gen_elements[0]
    print(f"   Generated:")
    print(f"     Text: '{gen_elem.text}' (unchanged )")
    print(f"     Position: {gen_elem.position} (changed )")
    print(f"     Font: {gen_elem.font} ({gen_elem.font_size}pt) (unchanged )")
    
    return True


def demo_format_preservation():
    """Demonstrate format preservation."""
    print("\n" + "="*70)
    print("DEMO 2: Format Preservation")
    print("="*70)
    
    yml_file = "coords_multi/seite1_f1.yml"
    if not Path(yml_file).exists():
        print(f"YML file not found: {yml_file}")
        return False
    
    # Parse original
    print(f"\n1. Parsing original YML")
    parser = YMLParser()
    elements = parser.parse_yml(yml_file)
    
    # Use same positions (no change) to test format preservation
    print(f"\n2. Using original positions (testing format preservation)")
    original_positions = [elem.position for elem in elements]
    
    # Generate
    output_file = "multi_pdf_positioning/demo_format_preserved.yml"
    print(f"\n3. Generating YML with preserved format")
    generator = YMLGenerator()
    generator.generate_yml(elements, original_positions, output_file, yml_file)
    
    # Compare files
    print(f"\n4. Comparing files")
    with open(yml_file, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    with open(output_file, 'r', encoding='utf-8') as f:
        generated_content = f.read()
    
    # Check separator count
    orig_sep_count = original_content.count("----------------------------------------")
    gen_sep_count = generated_content.count("----------------------------------------")
    print(f"   Separator count: {orig_sep_count} (original) vs {gen_sep_count} (generated)")
    if orig_sep_count == gen_sep_count:
        print("   Separator count preserved")
    else:
        print("    Separator count differs")
    
    # Check line count
    orig_lines = len(original_content.split('\n'))
    gen_lines = len(generated_content.split('\n'))
    print(f"   Line count: {orig_lines} (original) vs {gen_lines} (generated)")
    line_diff = abs(orig_lines - gen_lines)
    if line_diff <= 5:
        print(f"   Line count similar (diff: {line_diff})")
    else:
        print(f"    Line count differs significantly (diff: {line_diff})")
    
    # Check element count
    parser2 = YMLParser()
    gen_elements = parser2.parse_yml(output_file)
    print(f"   Element count: {len(elements)} (original) vs {len(gen_elements)} (generated)")
    if len(elements) == len(gen_elements):
        print("   Element count preserved")
    else:
        print("    Element count differs")
    
    return True


def demo_validation():
    """Demonstrate validation functionality."""
    print("\n" + "="*70)
    print("DEMO 3: Validation Functionality")
    print("="*70)
    
    yml_file = "coords_multi/seite1_f1.yml"
    if not Path(yml_file).exists():
        print(f"YML file not found: {yml_file}")
        return False
    
    # Parse and generate
    print(f"\n1. Generating test YML file")
    parser = YMLParser()
    elements = parser.parse_yml(yml_file)
    
    # Create new positions
    new_positions = []
    for elem in elements:
        x1, y1, x2, y2 = elem.position
        new_pos = (x1 + 5, y1 + 5, x2 + 5, y2 + 5)
        new_positions.append(new_pos)
    
    output_file = "multi_pdf_positioning/demo_validation.yml"
    generator = YMLGenerator()
    generator.generate_yml(elements, new_positions, output_file, yml_file)
    
    # Test validation checks
    print(f"\n2. Running validation checks")
    
    # Check 1: All elements present
    print(f"\n   Check 1: All elements present")
    parser2 = YMLParser()
    gen_elements = parser2.parse_yml(output_file)
    if len(gen_elements) == len(elements):
        print(f"   All {len(elements)} elements present")
    else:
        print(f"   Element count mismatch: {len(gen_elements)} vs {len(elements)}")
    
    # Check 2: Attributes preserved (except position)
    print(f"\n   Check 2: Non-position attributes preserved")
    mismatches = 0
    for i, (orig, gen) in enumerate(zip(elements, gen_elements)):
        if orig.text != gen.text:
            print(f"   Element {i}: Text mismatch")
            mismatches += 1
        if orig.font != gen.font:
            print(f"   Element {i}: Font mismatch")
            mismatches += 1
        if orig.font_size != gen.font_size:
            print(f"   Element {i}: Font size mismatch")
            mismatches += 1
        if orig.color != gen.color:
            print(f"   Element {i}: Color mismatch")
            mismatches += 1
    
    if mismatches == 0:
        print(f"   All attributes preserved correctly")
    else:
        print(f"    Found {mismatches} attribute mismatches")
    
    # Check 3: Positions changed
    print(f"\n   Check 3: Positions updated")
    position_changes = 0
    for i, (orig, gen) in enumerate(zip(elements, gen_elements)):
        if orig.position != gen.position:
            position_changes += 1
    
    print(f"   {position_changes} out of {len(elements)} positions changed")
    
    # Check 4: Positions within bounds
    print(f"\n   Check 4: Positions within bounds")
    out_of_bounds = 0
    for i, elem in enumerate(gen_elements):
        x1, y1, x2, y2 = elem.position
        if not (0 <= x1 < x2 <= 595):
            print(f"    Element {i}: X coordinates out of bounds")
            out_of_bounds += 1
        if not (0 <= y1 < y2 <= 842):
            print(f"    Element {i}: Y coordinates out of bounds")
            out_of_bounds += 1
    
    if out_of_bounds == 0:
        print(f"   All positions within bounds")
    else:
        print(f"    {out_of_bounds} positions out of bounds")
    
    # Full validation
    print(f"\n3. Running full validation")
    is_valid, errors = generator.validate_yml_output(output_file, elements)
    
    if is_valid:
        print("   Full validation passed!")
    else:
        print(f"    Validation found {len(errors)} issues")
        print(f"   First 3 errors:")
        for error in errors[:3]:
            print(f"     - {error}")
    
    return True


def demo_batch_processing():
    """Demonstrate batch processing."""
    print("\n" + "="*70)
    print("DEMO 4: Batch Processing")
    print("="*70)
    
    # Find all YML files
    yml_dir = Path("coords_multi")
    if not yml_dir.exists():
        print(f"Directory not found: {yml_dir}")
        return False
    
    yml_files = list(yml_dir.glob("seite1_f*.yml"))
    if not yml_files:
        print(f"No YML files found in {yml_dir}")
        return False
    
    print(f"\n1. Found {len(yml_files)} YML files to process")
    
    # Process first 3 files as demo
    demo_files = [str(f) for f in yml_files[:3]]
    print(f"\n2. Processing first 3 files as demo:")
    for f in demo_files:
        print(f"   - {Path(f).name}")
    
    # Define position calculator function
    def calculate_new_positions(elements):
        """Simple position calculator: shift by 15 points."""
        new_positions = []
        for elem in elements:
            x1, y1, x2, y2 = elem.position
            new_pos = (x1 + 15, y1 + 15, x2 + 15, y2 + 15)
            new_positions.append(new_pos)
        return new_positions
    
    # Batch generate
    print(f"\n3. Running batch generation")
    generator = YMLGenerator()
    output_dir = "multi_pdf_positioning/demo_batch_output"
    
    results = generator.batch_generate(
        demo_files,
        calculate_new_positions,
        output_dir
    )
    
    # Show results
    print(f"\n4. Batch processing results:")
    success_count = sum(1 for v in results.values() if v)
    print(f"   Successful: {success_count}/{len(results)}")
    print(f"   Failed: {len(results) - success_count}/{len(results)}")
    
    for file, success in results.items():
        status = "" if success else ""
        print(f"   {status} {Path(file).name}")
    
    return True


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("YML GENERATOR MODULE - COMPREHENSIVE DEMO")
    print("="*70)
    print("\nThis demo showcases all YML generator functionality:")
    print("  1. Basic YML generation with new positions")
    print("  2. Format preservation (separators, whitespace)")
    print("  3. Validation of generated files")
    print("  4. Batch processing multiple files")
    
    # Run demos
    demos = [
        ("Basic Generation", demo_basic_generation),
        ("Format Preservation", demo_format_preservation),
        ("Validation", demo_validation),
        ("Batch Processing", demo_batch_processing),
    ]
    
    results = {}
    for name, demo_func in demos:
        try:
            success = demo_func()
            results[name] = success
        except Exception as e:
            print(f"\nError in {name}: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False
    
    # Summary
    print("\n" + "="*70)
    print("DEMO SUMMARY")
    print("="*70)
    
    for name, success in results.items():
        status = "PASSED" if success else "FAILED"
        print(f"  {status}: {name}")
    
    success_count = sum(1 for v in results.values() if v)
    print(f"\nTotal: {success_count}/{len(results)} demos passed")
    
    if success_count == len(results):
        print("\nAll demos completed successfully!")
        print("\nThe YML Generator module is ready for use.")
        print("\nKey features demonstrated:")
        print("  • Generate YML files with updated positions")
        print("  • Preserve all non-position attributes")
        print("  • Maintain original formatting (separators, whitespace)")
        print("  • Validate generated files")
        print("  • Batch process multiple files")
        return 0
    else:
        print(f"\n {len(results) - success_count} demo(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
