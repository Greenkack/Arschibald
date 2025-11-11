"""
PDF Template Inventory
Lists all PDF templates and validates mapping with YML files
"""
from pathlib import Path
from typing import Dict, List, Tuple
import json
from PyPDF2 import PdfReader

from .config import PDF_DIR, YML_DIR, FIRMEN, SEITEN, ANALYSIS_DIR


def get_pdf_filename(seite: int, firma: int) -> str:
    """Generate expected PDF filename"""
    return f"multi_nt_{seite:02d}_f{firma}.pdf"


def get_yml_filename(seite: int, firma: int) -> str:
    """Generate expected YML filename"""
    return f"seite{seite}_f{firma}.yml"


def inventory_pdfs() -> Dict:
    """
    Create inventory of all PDF templates
    
    Returns:
        Dictionary with inventory data
    """
    inventory = {
        'total_expected': len(FIRMEN) * len(SEITEN),
        'total_found': 0,
        'missing_pdfs': [],
        'found_pdfs': [],
        'pdf_details': {},
        'mapping': {
            'complete': [],
            'missing_yml': [],
            'missing_pdf': []
        }
    }
    
    for firma in FIRMEN:
        for seite in SEITEN:
            pdf_filename = get_pdf_filename(seite, firma)
            yml_filename = get_yml_filename(seite, firma)
            
            pdf_path = PDF_DIR / pdf_filename
            yml_path = YML_DIR / yml_filename
            
            pdf_exists = pdf_path.exists()
            yml_exists = yml_path.exists()
            
            combination_key = f"f{firma}_s{seite}"
            
            if pdf_exists:
                inventory['total_found'] += 1
                inventory['found_pdfs'].append(pdf_filename)
                
                # Get PDF details
                try:
                    reader = PdfReader(pdf_path)
                    page = reader.pages[0]
                    
                    inventory['pdf_details'][combination_key] = {
                        'filename': pdf_filename,
                        'firma': firma,
                        'seite': seite,
                        'path': str(pdf_path),
                        'pages': len(reader.pages),
                        'width': float(page.mediabox.width),
                        'height': float(page.mediabox.height),
                        'yml_exists': yml_exists,
                        'yml_filename': yml_filename if yml_exists else None
                    }
                except Exception as e:
                    print(f"Error reading {pdf_filename}: {e}")
                    inventory['pdf_details'][combination_key] = {
                        'filename': pdf_filename,
                        'firma': firma,
                        'seite': seite,
                        'path': str(pdf_path),
                        'error': str(e),
                        'yml_exists': yml_exists
                    }
            else:
                inventory['missing_pdfs'].append(pdf_filename)
            
            # Check mapping
            if pdf_exists and yml_exists:
                inventory['mapping']['complete'].append({
                    'firma': firma,
                    'seite': seite,
                    'pdf': pdf_filename,
                    'yml': yml_filename
                })
            elif pdf_exists and not yml_exists:
                inventory['mapping']['missing_yml'].append({
                    'firma': firma,
                    'seite': seite,
                    'pdf': pdf_filename,
                    'yml': yml_filename
                })
            elif not pdf_exists and yml_exists:
                inventory['mapping']['missing_pdf'].append({
                    'firma': firma,
                    'seite': seite,
                    'pdf': pdf_filename,
                    'yml': yml_filename
                })
    
    return inventory


def validate_mapping(inventory: Dict) -> Tuple[bool, List[str]]:
    """
    Validate that all PDFs have corresponding YML files
    
    Args:
        inventory: Inventory dictionary
        
    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []
    
    if inventory['missing_pdfs']:
        issues.append(f"Missing {len(inventory['missing_pdfs'])} PDF files")
    
    if inventory['mapping']['missing_yml']:
        issues.append(f"Missing {len(inventory['mapping']['missing_yml'])} YML files for existing PDFs")
    
    if inventory['mapping']['missing_pdf']:
        issues.append(f"Found {len(inventory['mapping']['missing_pdf'])} YML files without corresponding PDFs")
    
    is_valid = len(issues) == 0
    
    return is_valid, issues


def save_inventory_report(inventory: Dict, output_file: Path = None):
    """
    Save inventory report to JSON file
    
    Args:
        inventory: Inventory dictionary
        output_file: Output file path (default: analysis/pdf_inventory.json)
    """
    if output_file is None:
        output_file = ANALYSIS_DIR / "pdf_inventory.json"
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)
    
    print(f"Inventory report saved to: {output_file}")


def print_inventory_summary(inventory: Dict):
    """Print a human-readable summary of the inventory"""
    print("\n" + "="*60)
    print("PDF TEMPLATES INVENTORY SUMMARY")
    print("="*60)
    
    print(f"\nExpected PDF files: {inventory['total_expected']}")
    print(f"Found PDF files: {inventory['total_found']}")
    print(f"Missing PDF files: {len(inventory['missing_pdfs'])}")
    
    if inventory['missing_pdfs']:
        print("\nMissing PDFs:")
        for pdf in inventory['missing_pdfs']:
            print(f"  - {pdf}")
    
    print("\n--- Mapping Status ---")
    print(f"Complete mappings (PDF + YML): {len(inventory['mapping']['complete'])}")
    print(f"PDFs without YML: {len(inventory['mapping']['missing_yml'])}")
    print(f"YMLs without PDF: {len(inventory['mapping']['missing_pdf'])}")
    
    if inventory['mapping']['missing_yml']:
        print("\nPDFs without corresponding YML:")
        for item in inventory['mapping']['missing_yml']:
            print(f"  - Firma {item['firma']}, Seite {item['seite']}: {item['pdf']}")
    
    if inventory['mapping']['missing_pdf']:
        print("\nYMLs without corresponding PDF:")
        for item in inventory['mapping']['missing_pdf']:
            print(f"  - Firma {item['firma']}, Seite {item['seite']}: {item['yml']}")
    
    # Validate
    is_valid, issues = validate_mapping(inventory)
    
    print("\n--- Validation ---")
    if is_valid:
        print("✓ All mappings are complete!")
    else:
        print("✗ Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    
    # PDF dimensions summary
    if inventory['pdf_details']:
        print("\n--- PDF Dimensions ---")
        dimensions = set()
        for key, details in inventory['pdf_details'].items():
            if 'width' in details and 'height' in details:
                dimensions.add((details['width'], details['height']))
        
        for width, height in sorted(dimensions):
            count = sum(1 for d in inventory['pdf_details'].values() 
                       if d.get('width') == width and d.get('height') == height)
            print(f"  {width:.1f} x {height:.1f} points: {count} files")
    
    print("\n" + "="*60)


def create_mapping_table(inventory: Dict) -> str:
    """
    Create a visual mapping table
    
    Returns:
        String representation of the mapping table
    """
    table = "\n" + "="*80 + "\n"
    table += "PDF-YML MAPPING TABLE\n"
    table += "="*80 + "\n\n"
    
    # Header
    table += "Seite | " + " | ".join([f"F{f}" for f in FIRMEN]) + "\n"
    table += "------+" + "+".join(["-----" for _ in FIRMEN]) + "\n"
    
    # Rows
    for seite in SEITEN:
        row = f"  {seite}   |"
        for firma in FIRMEN:
            pdf_filename = get_pdf_filename(seite, firma)
            yml_filename = get_yml_filename(seite, firma)
            
            pdf_exists = (PDF_DIR / pdf_filename).exists()
            yml_exists = (YML_DIR / yml_filename).exists()
            
            if pdf_exists and yml_exists:
                status = " ✓ "
            elif pdf_exists and not yml_exists:
                status = " P "
            elif not pdf_exists and yml_exists:
                status = " Y "
            else:
                status = " ✗ "
            
            row += f" {status} |"
        
        table += row + "\n"
    
    table += "\nLegend: ✓ = Both exist, P = PDF only, Y = YML only, ✗ = Neither\n"
    table += "="*80 + "\n"
    
    return table


if __name__ == "__main__":
    print("Creating PDF inventory...")
    inventory = inventory_pdfs()
    print_inventory_summary(inventory)
    print(create_mapping_table(inventory))
    save_inventory_report(inventory)
