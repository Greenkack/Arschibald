"""
Test script for YML Parser and Format Preserver

Tests the YML parser and format preservation with multiple YML files.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from multi_pdf_positioning.yml_parser import YMLParser, parse_yml
from multi_pdf_positioning.yml_format_preserver import YMLFormatPreserver, preserve_yml_format


def test_yml_parser():
    """Test the YML parser with multiple files."""
    print("=" * 60)
    print("Testing YML Parser")
    print("=" * 60)
    
    test_files = [
        "coords_multi/seite1_f1.yml",
        "coords_multi/seite1_f2.yml",
        "coords_multi/seite2_f1.yml",
        "coords_multi/seite3_f3.yml"
    ]
    
    for yml_file in test_files:
        if not Path(yml_file).exists():
            print(f"\n⚠ Skipping {yml_file} (not found)")
            continue
        
        print(f"\n{'─' * 60}")
        print(f"Testing: {yml_file}")
        print('─' * 60)
        
        try:
            # Parse the file
            parser = YMLParser()
            elements = parser.parse_yml(yml_file)
            
            # Get statistics
            stats = parser.get_statistics()
            print(f"\n[CHART] Statistics:")
            print(f"   Total elements: {stats['total_elements']}")
            print(f"   Non-empty elements: {stats['non_empty_elements']}")
            print(f"   Empty elements: {stats['empty_elements']}")
            print(f"   Unique fonts: {stats['unique_fonts']}")
            print(f"   Unique colors: {stats['unique_colors']}")
            
            # Show some sample elements
            print(f"\n[NOTE] Sample Elements (first 3):")
            for elem in elements[:3]:
                print(f"\n   Element {elem.index}:")
                print(f"      Text: '{elem.text}'")
                print(f"      Position: {elem.position}")
                print(f"      Font: {elem.font} ({elem.font_size}pt)")
                print(f"      Color: {elem.color}")
            
            # Validate
            is_valid, errors = parser.validate_elements()
            if is_valid:
                print(f"\n[OK] All elements validated successfully")
            else:
                print(f"\n[ERROR] Validation errors found:")
                for error in errors[:5]:  # Show first 5 errors
                    print(f"   - {error}")
            
            # Test specific queries
            non_empty = parser.get_non_empty_elements()
            print(f"\n[SEARCH] Query Results:")
            print(f"   Non-empty text elements: {len(non_empty)}")
            
            # Find specific elements
            photovoltaik = parser.get_element_by_text("PHOTOVOLTAIK")
            if photovoltaik:
                print(f"   Found 'PHOTOVOLTAIK' at position {photovoltaik.position}")
            
            angebot = parser.get_element_by_text("ANGEBOT")
            if angebot:
                print(f"   Found 'ANGEBOT' at position {angebot.position}")
            
        except Exception as e:
            print(f"\n[ERROR] Error: {e}")
            import traceback
            traceback.print_exc()


def test_format_preserver():
    """Test the format preservation with multiple files."""
    print("\n\n" + "=" * 60)
    print("Testing Format Preserver")
    print("=" * 60)
    
    test_files = [
        "coords_multi/seite1_f1.yml",
        "coords_multi/seite1_f2.yml"
    ]
    
    for yml_file in test_files:
        if not Path(yml_file).exists():
            print(f"\n⚠ Skipping {yml_file} (not found)")
            continue
        
        print(f"\n{'─' * 60}")
        print(f"Testing: {yml_file}")
        print('─' * 60)
        
        try:
            # Parse the file
            parser = YMLParser()
            elements = parser.parse_yml(yml_file)
            
            # Load format preserver
            preserver = YMLFormatPreserver()
            preserver.load_original(yml_file)
            
            # Get structure info
            info = preserver.get_structure_info()
            print(f"\n📋 Structure Info:")
            print(f"   Line ending: {repr(info['line_ending'])}")
            print(f"   Separator: '{info['separator']}'")
            print(f"   Number of blocks: {info['num_blocks']}")
            print(f"   Has patterns: {info['has_patterns']}")
            
            # Test reconstruction with same positions
            original_positions = [elem.position for elem in elements]
            reconstructed = preserver.reconstruct_yml(elements, original_positions)
            
            # Validate preservation
            is_valid, differences = preserver.validate_preservation(yml_file, reconstructed)
            if is_valid:
                print(f"\n[OK] Format preservation validated successfully")
            else:
                print(f"\n⚠ Format preservation differences:")
                for diff in differences:
                    print(f"   - {diff}")
            
            # Test with modified positions (shift everything by 10 points)
            new_positions = [(x1+10, y1+10, x2+10, y2+10) for x1, y1, x2, y2 in original_positions]
            reconstructed_modified = preserver.reconstruct_yml(elements, new_positions)
            
            print(f"\n🔄 Testing with modified positions:")
            print(f"   Original first position: {original_positions[0]}")
            print(f"   Modified first position: {new_positions[0]}")
            
            # Check that only positions changed
            original_lines = [line for line in preserver.original_content.split('\n') 
                            if line.strip() and not line.startswith('Position:')]
            modified_lines = [line for line in reconstructed_modified.split('\n') 
                            if line.strip() and not line.startswith('Position:')]
            
            if original_lines == modified_lines:
                print(f"   [OK] All non-position attributes preserved")
            else:
                print(f"   [ERROR] Some non-position attributes changed")
            
        except Exception as e:
            print(f"\n[ERROR] Error: {e}")
            import traceback
            traceback.print_exc()


def test_integration():
    """Test integration of parser and format preserver."""
    print("\n\n" + "=" * 60)
    print("Testing Integration")
    print("=" * 60)
    
    yml_file = "coords_multi/seite1_f1.yml"
    
    if not Path(yml_file).exists():
        print(f"\n⚠ Skipping integration test ({yml_file} not found)")
        return
    
    print(f"\nTesting with: {yml_file}")
    
    try:
        # Parse
        elements = parse_yml(yml_file)
        print(f"\n[OK] Parsed {len(elements)} elements")
        
        # Create new positions (example: move everything to center)
        new_positions = []
        for elem in elements:
            x1, y1, x2, y2 = elem.position
            width = x2 - x1
            height = y2 - y1
            # Center horizontally, keep vertical position
            new_x1 = 297.5 - width / 2  # A4 center is 297.5
            new_x2 = new_x1 + width
            new_positions.append((new_x1, y1, new_x2, y2))
        
        # Preserve format with new positions
        new_content = preserve_yml_format(yml_file, elements, new_positions)
        print(f"[OK] Generated new YML content ({len(new_content)} characters)")
        
        # Validate
        preserver = YMLFormatPreserver()
        preserver.load_original(yml_file)
        is_valid, differences = preserver.validate_preservation(yml_file, new_content)
        
        if is_valid:
            print(f"[OK] Format preservation validated")
        else:
            print(f"⚠ Format differences: {len(differences)}")
        
        # Show sample of new content
        print(f"\n[FILE] Sample of new content (first 500 chars):")
        print(new_content[:500])
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n" + "🧪 YML Parser & Format Preserver Test Suite" + "\n")
    
    test_yml_parser()
    test_format_preserver()
    test_integration()
    
    print("\n\n" + "=" * 60)
    print("[OK] Test Suite Complete")
    print("=" * 60)
