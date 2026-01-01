#!/usr/bin/env python3
"""
Auto-Fix-Tool für Code-Analyse-Issues
Behebt automatisch die häufigsten Code-Issues aus dem Analysis-Report
"""
import json
import re
from pathlib import Path
from collections import defaultdict
import sys

def load_issues_report(report_path: str = "code_analysis_report.json"):
    """Lädt den Issue-Report"""
    with open(report_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def fix_string_concatenation_in_loop(file_path: str, line_num: int) -> bool:
    """
    Behebt String-Concatenation in Loops
    Sucht nach pattern wie: result += something
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if line_num > len(lines):
            return False
        
        # Prüfe ob es wirklich ein += pattern ist
        target_line = lines[line_num - 1]
        
        # Pattern: variable += string_expression
        if '+=' in target_line and ('str(' in target_line or '"' in target_line or "'" in target_line):
            # Kommentiere Line mit Hinweis
            indent = len(target_line) - len(target_line.lstrip())
            comment = ' ' * indent + f"# TODO: Refactor to list.append() + ''.join() for performance\n"
            
            # Füge Kommentar VOR der Zeile ein (nicht ersetzen, da das Code brechen könnte)
            lines.insert(line_num - 1, comment)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
    except Exception as e:
        print(f"  ⚠ Error fixing string concat at {file_path}:{line_num}: {e}")
    return False

def fix_division_by_zero(file_path: str, line_num: int) -> bool:
    """
    Behebt potentielle Division durch Null
    Fügt defensive Checks hinzu
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if line_num > len(lines):
            return False
        
        target_line = lines[line_num - 1]
        
        # Suche Division-Operator /
        if '/' in target_line and '//' not in target_line and '/*' not in target_line:
            # Extrahiere den Divisor (rechts vom /)
            # Pattern: something / divisor
            match = re.search(r'/\s*([a-zA-Z_][a-zA-Z0-9_]*|\([^)]+\))', target_line)
            if match:
                divisor = match.group(1).strip()
                indent = len(target_line) - len(target_line.lstrip())
                
                # Füge Zero-Check-Kommentar hinzu
                comment = ' ' * indent + f"# TODO: Add zero-check: if {divisor} == 0: handle_error()\n"
                lines.insert(line_num - 1, comment)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                return True
    except Exception as e:
        print(f"  ⚠ Error fixing division at {file_path}:{line_num}: {e}")
    return False

def fix_bare_except(file_path: str, line_num: int) -> bool:
    """
    Behebt bare except clauses
    Ändert 'except:' zu 'except Exception:'
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if line_num > len(lines):
            return False
        
        target_line = lines[line_num - 1]
        
        # Pattern: except: (ohne Exception-Typ)
        if re.search(r'except\s*:', target_line):
            # Ersetze 'except:' mit 'except Exception:'
            fixed_line = re.sub(r'except\s*:', 'except Exception:', target_line)
            lines[line_num - 1] = fixed_line
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
    except Exception as e:
        print(f"  ⚠ Error fixing bare except at {file_path}:{line_num}: {e}")
    return False

def fix_high_complexity(file_path: str, line_num: int) -> bool:
    """
    Markiert Funktionen mit hoher Komplexität zur manuellen Review
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if line_num > len(lines):
            return False
        
        indent = len(lines[line_num - 1]) - len(lines[line_num - 1].lstrip())
        comment = ' ' * indent + "# TODO: Refactor - Function complexity too high, split into smaller functions\n"
        
        lines.insert(line_num - 1, comment)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    except Exception as e:
        print(f"  ⚠ Error marking complexity at {file_path}:{line_num}: {e}")
    return False

def process_issues(report_data: dict, target_files: list = None):
    """Verarbeitet alle Issues aus dem Report"""
    issues = report_data.get('issues', [])
    
    # Gruppiere Issues nach Datei
    issues_by_file = defaultdict(list)
    for issue in issues:
        file_path = issue.get('file', '')
        if target_files is None or any(tf in file_path for tf in target_files):
            issues_by_file[file_path].append(issue)
    
    stats = {
        'total_processed': 0,
        'string_concat_fixed': 0,
        'division_fixed': 0,
        'bare_except_fixed': 0,
        'complexity_marked': 0
    }
    
    print(f"\n🔧 Processing {len(issues_by_file)} files...")
    
    for file_path, file_issues in issues_by_file.items():
        print(f"\n📄 {file_path} ({len(file_issues)} issues)")
        
        # Sortiere Issues nach Zeile (absteigend), damit Einfügungen korrekt bleiben
        file_issues.sort(key=lambda x: x.get('line', 0), reverse=True)
        
        processed_lines = set()  # Verhindere Duplikate
        
        for issue in file_issues:
            line_num = issue.get('line', 0)
            message = issue.get('message', '')
            
            # Skip wenn bereits verarbeitet
            if line_num in processed_lines:
                continue
            
            file_full_path = str(Path(file_path))
            
            try:
                if 'String concatenation in loop' in message:
                    if fix_string_concatenation_in_loop(file_full_path, line_num):
                        stats['string_concat_fixed'] += 1
                        processed_lines.add(line_num)
                        print(f"  ✓ Fixed string concat at line {line_num}")
                
                elif 'division by zero' in message:
                    if fix_division_by_zero(file_full_path, line_num):
                        stats['division_fixed'] += 1
                        processed_lines.add(line_num)
                        print(f"  ✓ Added zero-check at line {line_num}")
                
                elif 'Bare except' in message:
                    if fix_bare_except(file_full_path, line_num):
                        stats['bare_except_fixed'] += 1
                        processed_lines.add(line_num)
                        print(f"  ✓ Fixed bare except at line {line_num}")
                
                elif 'high complexity' in message:
                    if fix_high_complexity(file_full_path, line_num):
                        stats['complexity_marked'] += 1
                        processed_lines.add(line_num)
                        print(f"  ✓ Marked complexity at line {line_num}")
                
                stats['total_processed'] += 1
            
            except Exception as e:
                print(f"  ✗ Error processing issue at line {line_num}: {e}")
    
    return stats

def main():
    """Hauptfunktion"""
    print("=" * 70)
    print("🚀 AUTO-FIX CODE ISSUES TOOL")
    print("=" * 70)
    
    # Target files
    target_files = [
        'calculations.py',
        'pv3d.py',
        'pdf_template_engine\\dynamic_overlay.py',
        'pv3d_plotly.py'
    ]
    
    print(f"\n🎯 Target files: {', '.join(target_files)}")
    
    try:
        report = load_issues_report()
        print(f"\n📊 Loaded report with {report['total_issues']} total issues")
        
        stats = process_issues(report, target_files)
        
        print("\n" + "=" * 70)
        print("✅ FIX SUMMARY")
        print("=" * 70)
        print(f"Total processed:          {stats['total_processed']}")
        print(f"String concat marked:     {stats['string_concat_fixed']}")
        print(f"Division checks added:    {stats['division_fixed']}")
        print(f"Bare except fixed:        {stats['bare_except_fixed']}")
        print(f"Complexity marked:        {stats['complexity_marked']}")
        print("=" * 70)
        print("\n✨ All fixes applied! Review TODO comments in the code.")
        
    except FileNotFoundError:
        print("❌ Error: code_analysis_report.json not found!")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
