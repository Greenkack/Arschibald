"""
Automated Issue Fixer

Automatically fixes detected issues from app_diagnostics.py scan.
"""

import json
import re
import ast
from pathlib import Path
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IssueFixer:
    """Automatically fixes common code issues."""
    
    def __init__(self, report_file: str = "code_analysis_report.json"):
        with open(report_file, 'r', encoding='utf-8') as f:
            self.report = json.load(f)
        self.fixed_count = 0
        self.skipped_count = 0
    
    def fix_all_issues(self, auto_fix: bool = False):
        """Fix all automatically fixable issues."""
        
        logger.info(f"Found {self.report['total_issues']} issues")
        
        # Group issues by file
        file_issues = {}
        for issue in self.report['issues']:
            filepath = issue['file']
            if filepath not in file_issues:
                file_issues[filepath] = []
            file_issues[filepath].append(issue)
        
        # Fix each file
        for filepath, issues in file_issues.items():
            if not Path(filepath).exists():
                continue
            
            # Skip backup directories
            if '_backup' in filepath or '__pycache__' in filepath:
                logger.info(f"Skipping backup file: {filepath}")
                continue
            
            logger.info(f"Processing {filepath} ({len(issues)} issues)")
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Apply fixes
                for issue in issues:
                    if issue['category'] == 'ERROR' and 'division by zero' in issue['message'].lower():
                        content = self._fix_division_by_zero(content, issue)
                    elif issue['category'] == 'QUALITY' and 'bare except' in issue['message'].lower():
                        content = self._fix_bare_except(content, issue)
                
                # Save if changed
                if content != original_content:
                    if auto_fix:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        logger.info(f"[OK] Fixed {filepath}")
                        self.fixed_count += 1
                    else:
                        logger.info(f"[WARNING] Would fix {filepath} (use --auto-fix)")
                        self.skipped_count += 1
            
            except Exception as e:
                logger.error(f"Error processing {filepath}: {e}")
    
    def _fix_division_by_zero(self, content: str, issue: Dict) -> str:
        """Add zero checks before division operations."""
        
        lines = content.split('\n')
        if issue['line'] is None or issue['line'] > len(lines):
            return content
        
        line_idx = issue['line'] - 1
        line = lines[line_idx]
        
        # Find division operations
        if '/' in line and '//' not in line:
            # Extract variable being divided
            match = re.search(r'(\w+)\s*/\s*(\w+)', line)
            if match:
                divisor = match.group(2)
                indent = len(line) - len(line.lstrip())
                
                # Add zero check
                check = f"{' ' * indent}if {divisor} != 0:\n"
                check += f"{line}\n"
                check += f"{' ' * indent}else:\n"
                
                # Find what's being assigned
                if '=' in line:
                    var_name = line.split('=')[0].strip()
                    check += f"{' ' * (indent + 4)}{var_name} = 0.0\n"
                
                lines[line_idx] = check.rstrip()
        
        return '\n'.join(lines)
    
    def _fix_bare_except(self, content: str, issue: Dict) -> str:
        """Replace bare except with Exception."""
        
        lines = content.split('\n')
        if issue['line'] is None or issue['line'] > len(lines):
            return content
        
        line_idx = issue['line'] - 1
        line = lines[line_idx]
        
        # Replace 'except:' with 'except Exception:'
        if line.strip() == 'except:':
            lines[line_idx] = line.replace('except:', 'except Exception:')
        
        return '\n'.join(lines)
    
    def generate_fix_report(self) -> Dict:
        """Generate report of fixes applied."""
        return {
            "fixed": self.fixed_count,
            "skipped": self.skipped_count,
            "total": self.fixed_count + self.skipped_count
        }


def apply_critical_fixes():
    """Apply fixes to critical syntax errors."""
    
    critical_fixes = [
        {
            "file": "multi_pdf_positioning/demo_orchestration.py",
            "line": 136,
            "fix": lambda content: content.replace('print("\\n" + "=', 'print("\\n" + "=" * 70)')
        }
    ]
    
    for fix_info in critical_fixes:
        filepath = fix_info['file']
        if not Path(filepath).exists():
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            fixed_content = fix_info['fix'](content)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            logger.info(f"[OK] Fixed critical issue in {filepath}")
        
        except Exception as e:
            logger.error(f"Failed to fix {filepath}: {e}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Automatically fix code issues')
    parser.add_argument('--auto-fix', action='store_true', help='Actually apply fixes (default: dry-run)')
    parser.add_argument('--critical-only', action='store_true', help='Only fix critical issues')
    
    args = parser.parse_args()
    
    if args.critical_only:
        apply_critical_fixes()
    else:
        fixer = IssueFixer()
        fixer.fix_all_issues(auto_fix=args.auto_fix)
        
        report = fixer.generate_fix_report()
        print(f"\n{'='*80}")
        print(f"FIX REPORT")
        print(f"{'='*80}")
        print(f"Fixed: {report['fixed']}")
        print(f"Skipped: {report['skipped']}")
        print(f"Total: {report['total']}")
        print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
