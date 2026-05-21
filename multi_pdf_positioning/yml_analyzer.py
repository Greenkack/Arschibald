"""
YML File Analyzer
Analyzes all YML coordinate files to understand structure and content
"""
import yaml
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, field
import json
from collections import defaultdict

from .config import YML_DIR, FIRMEN, SEITEN, ANALYSIS_DIR


@dataclass
class YMLElement:
    """Represents a single text element from YML file"""
    text: str
    position: tuple  # (x1, y1, x2, y2)
    font: str
    font_size: float
    color: int
    index: int  # Original position in file
    
    @property
    def is_dynamic(self) -> bool:
        """Check if text is a dynamic placeholder"""
        return self.text and ('_' in self.text or self.text.islower())
    
    @property
    def is_empty(self) -> bool:
        """Check if text is empty"""
        return not self.text or self.text.strip() == ''


def parse_yml_file(yml_path: Path) -> List[YMLElement]:
    """
    Parse a YML coordinate file and extract all text elements
    
    Args:
        yml_path: Path to YML file
        
    Returns:
        List of YMLElement objects
    """
    elements = []
    
    with open(yml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by separator
    blocks = content.split('----------------------------------------')
    
    for index, block in enumerate(blocks):
        if not block.strip():
            continue
            
        lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
        
        if len(lines) < 5:
            continue
        
        # Parse each field
        element_data = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if key == 'Text':
                    element_data['text'] = value
                elif key == 'Position':
                    # Parse tuple: (x1, y1, x2, y2)
                    pos_str = value.strip('()')
                    try:
                        coords = [float(x.strip()) for x in pos_str.split(',') if x.strip()]
                        if len(coords) == 4:
                            element_data['position'] = tuple(coords)
                    except (ValueError, IndexError):
                        # Skip invalid positions
                        pass
                elif key == 'Schriftart':
                    element_data['font'] = value
                elif key == 'Schriftgröße':
                    element_data['font_size'] = float(value)
                elif key == 'Farbe':
                    element_data['color'] = int(value)
        
        if 'position' in element_data:
            elements.append(YMLElement(
                text=element_data.get('text', ''),
                position=element_data['position'],
                font=element_data.get('font', 'Helvetica-Regular'),
                font_size=element_data.get('font_size', 10.0),
                color=element_data.get('color', 0),
                index=index
            ))
    
    return elements


def analyze_all_yml_files() -> Dict[str, Any]:
    """
    Analyze all 48 YML files and extract statistics
    
    Returns:
        Dictionary with analysis results
    """
    analysis = {
        'total_files': 0,
        'files_analyzed': [],
        'element_statistics': {
            'total_elements': 0,
            'dynamic_elements': 0,
            'static_elements': 0,
            'empty_elements': 0
        },
        'unique_texts': {
            'static': set(),
            'dynamic': set()
        },
        'fonts_used': set(),
        'font_sizes_used': set(),
        'colors_used': set(),
        'per_firma': defaultdict(lambda: {
            'files': 0,
            'elements': 0,
            'dynamic': 0,
            'static': 0
        }),
        'per_seite': defaultdict(lambda: {
            'files': 0,
            'elements': 0,
            'dynamic': 0,
            'static': 0
        }),
        'position_ranges': {
            'x_min': float('inf'),
            'x_max': float('-inf'),
            'y_min': float('inf'),
            'y_max': float('-inf')
        }
    }
    
    for firma in FIRMEN:
        for seite in SEITEN:
            if f != 0:
                yml_file = YML_DIR / f"seite{seite}_f{firma}.yml"
            else:
                yml_file = 0.0
            
            if not yml_file.exists():
                print(f"Warning: {yml_file} not found")
                continue
            
            analysis['total_files'] += 1
            analysis['files_analyzed'].append(str(yml_file.name))
            
            # Parse file
            elements = parse_yml_file(yml_file)
            
            # Update statistics
            analysis['element_statistics']['total_elements'] += len(elements)
            analysis['per_firma'][firma]['files'] += 1
            analysis['per_firma'][firma]['elements'] += len(elements)
            analysis['per_seite'][seite]['files'] += 1
            analysis['per_seite'][seite]['elements'] += len(elements)
            
            for elem in elements:
                # Categorize elements
                if elem.is_empty:
                    analysis['element_statistics']['empty_elements'] += 1
                elif elem.is_dynamic:
                    analysis['element_statistics']['dynamic_elements'] += 1
                    analysis['unique_texts']['dynamic'].add(elem.text)
                    analysis['per_firma'][firma]['dynamic'] += 1
                    analysis['per_seite'][seite]['dynamic'] += 1
                else:
                    analysis['element_statistics']['static_elements'] += 1
                    analysis['unique_texts']['static'].add(elem.text)
                    analysis['per_firma'][firma]['static'] += 1
                    analysis['per_seite'][seite]['static'] += 1
                
                # Collect attributes
                analysis['fonts_used'].add(elem.font)
                analysis['font_sizes_used'].add(elem.font_size)
                analysis['colors_used'].add(elem.color)
                
                # Track position ranges
                x1, y1, x2, y2 = elem.position
                analysis['position_ranges']['x_min'] = min(analysis['position_ranges']['x_min'], x1)
                analysis['position_ranges']['x_max'] = max(analysis['position_ranges']['x_max'], x2)
                analysis['position_ranges']['y_min'] = min(analysis['position_ranges']['y_min'], y1)
                analysis['position_ranges']['y_max'] = max(analysis['position_ranges']['y_max'], y2)
    
    # Convert sets to sorted lists for JSON serialization
    analysis['unique_texts']['static'] = sorted(list(analysis['unique_texts']['static']))
    analysis['unique_texts']['dynamic'] = sorted(list(analysis['unique_texts']['dynamic']))
    analysis['fonts_used'] = sorted(list(analysis['fonts_used']))
    analysis['font_sizes_used'] = sorted(list(analysis['font_sizes_used']))
    analysis['colors_used'] = sorted(list(analysis['colors_used']))
    analysis['per_firma'] = dict(analysis['per_firma'])
    analysis['per_seite'] = dict(analysis['per_seite'])
    
    return analysis


def save_analysis_report(analysis: Dict[str, Any], output_file: Path = None):
    """
    Save analysis report to JSON file
    
    Args:
        analysis: Analysis dictionary
        output_file: Output file path (default: analysis/yml_analysis.json)
    """
    if output_file is None:
        output_file = ANALYSIS_DIR / "yml_analysis.json"
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"Analysis report saved to: {output_file}")


def print_analysis_summary(analysis: Dict[str, Any]):
    """Print a human-readable summary of the analysis"""
    print("\n" + "="*60)
    print("YML FILES ANALYSIS SUMMARY")
    print("="*60)
    
    print(f"\nTotal files analyzed: {analysis['total_files']}")
    
    print("\n--- Element Statistics ---")
    stats = analysis['element_statistics']
    print(f"Total elements: {stats['total_elements']}")
    print(f"  - Dynamic elements: {stats['dynamic_elements']}")
    print(f"  - Static elements: {stats['static_elements']}")
    print(f"  - Empty elements: {stats['empty_elements']}")
    
    print("\n--- Unique Text Elements ---")
    print(f"Unique static texts: {len(analysis['unique_texts']['static'])}")
    print(f"Unique dynamic placeholders: {len(analysis['unique_texts']['dynamic'])}")
    
    print("\n--- Fonts Used ---")
    for font in analysis['fonts_used']:
        print(f"  - {font}")
    
    print(f"\n--- Font Sizes Used ---")
    print(f"Range: {min(analysis['font_sizes_used']):.1f} - {max(analysis['font_sizes_used']):.1f}")
    print(f"Unique sizes: {len(analysis['font_sizes_used'])}")
    
    print(f"\n--- Colors Used ---")
    print(f"Unique colors: {len(analysis['colors_used'])}")
    
    print("\n--- Position Ranges ---")
    pr = analysis['position_ranges']
    print(f"X: {pr['x_min']:.2f} - {pr['x_max']:.2f}")
    print(f"Y: {pr['y_min']:.2f} - {pr['y_max']:.2f}")
    
    print("\n--- Per Firma Statistics ---")
    for firma in sorted(analysis['per_firma'].keys()):
        data = analysis['per_firma'][firma]
        print(f"Firma {firma}: {data['files']} files, {data['elements']} elements "
              f"({data['dynamic']} dynamic, {data['static']} static)")
    
    print("\n--- Per Seite Statistics ---")
    for seite in sorted(analysis['per_seite'].keys()):
        data = analysis['per_seite'][seite]
        print(f"Seite {seite}: {data['files']} files, {data['elements']} elements "
              f"({data['dynamic']} dynamic, {data['static']} static)")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    print("Analyzing all YML files...")
    analysis = analyze_all_yml_files()
    print_analysis_summary(analysis)
    save_analysis_report(analysis)
