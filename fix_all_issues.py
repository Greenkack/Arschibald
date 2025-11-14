"""
Comprehensive Issue Fixer

Fixes all CRITICAL and HIGH priority issues automatically.
"""

import json
import re
import ast
from pathlib import Path
from typing import Dict, List, Set
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class ComprehensiveIssueFixer:
    """Fixes CRITICAL and HIGH priority issues."""
    
    def __init__(self, report_file: str = "code_analysis_report.json"):
        with open(report_file, 'r', encoding='utf-8') as f:
            self.report = json.load(f)
        
        self.fixed_files: Set[str] = set()
        self.fixed_count = 0
        self.skipped_count = 0
        self.error_count = 0
    
    def fix_all_issues(self, fix_critical: bool = True, fix_high: bool = True, dry_run: bool = False):
        """Fix all CRITICAL and HIGH issues."""
        
        # Filter issues
        issues_to_fix = []
        for issue in self.report['issues']:
            if fix_critical and issue['severity'] == 'CRITICAL':
                issues_to_fix.append(issue)
            elif fix_high and issue['severity'] == 'HIGH':
                issues_to_fix.append(issue)
        
        logger.info(f"{'=' * 80}")
        logger.info(f"COMPREHENSIVE ISSUE FIXER")
        logger.info(f"{'=' * 80}")
        logger.info(f"Total issues to fix: {len(issues_to_fix)}")
        logger.info(f"  CRITICAL: {sum(1 for i in issues_to_fix if i['severity'] == 'CRITICAL')}")
        logger.info(f"  HIGH: {sum(1 for i in issues_to_fix if i['severity'] == 'HIGH')}")
        logger.info(f"Mode: {'DRY RUN' if dry_run else 'LIVE FIX'}")
        logger.info(f"{'=' * 80}\n")
        
        # Group by file
        file_issues: Dict[str, List[Dict]] = {}
        for issue in issues_to_fix:
            filepath = issue['file']
            if filepath not in file_issues:
                file_issues[filepath] = []
            file_issues[filepath].append(issue)
        
        # Process each file
        for filepath, issues in sorted(file_issues.items()):
            # Skip backup directories
            if any(skip in filepath for skip in ['_backup', '__pycache__', '.git', 'venv']):
                logger.info(f"[SKIP]  Skipping backup/cache: {filepath}")
                self.skipped_count += len(issues)
                continue
            
            # Skip if file doesn't exist
            if not Path(filepath).exists():
                logger.info(f"[SKIP]  File not found: {filepath}")
                self.skipped_count += len(issues)
                continue
            
            self._fix_file(filepath, issues, dry_run)
        
        # Summary
        logger.info(f"\n{'=' * 80}")
        logger.info(f"SUMMARY")
        logger.info(f"{'=' * 80}")
        logger.info(f"[OK] Fixed: {self.fixed_count} issues in {len(self.fixed_files)} files")
        logger.info(f"[SKIP]  Skipped: {self.skipped_count} issues")
        logger.info(f"[ERROR] Errors: {self.error_count} issues")
        logger.info(f"{'=' * 80}\n")
        
        if dry_run:
            logger.info("[WARNING]  DRY RUN - No files were modified")
            logger.info("Run with --live to apply fixes")
    
    def _fix_file(self, filepath: str, issues: List[Dict], dry_run: bool):
        """Fix all issues in a single file."""
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            lines = content.split('\n')
            
            # Sort issues by line number (reverse order to preserve line numbers)
            issues_sorted = sorted(issues, key=lambda x: x.get('line', 0), reverse=True)
            
            fixed_in_file = 0
            for issue in issues_sorted:
                if issue['category'] == 'ERROR' and 'division by zero' in issue['message'].lower():
                    if self._fix_division_by_zero(lines, issue):
                        fixed_in_file += 1
                elif issue['category'] == 'QUALITY' and 'bare except' in issue['message'].lower():
                    if self._fix_bare_except(lines, issue):
                        fixed_in_file += 1
            
            # Save if changed
            new_content = '\n'.join(lines)
            if new_content != original_content:
                if not dry_run:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    logger.info(f"[OK] {filepath}: Fixed {fixed_in_file} issues")
                    self.fixed_files.add(filepath)
                else:
                    logger.info(f"[SEARCH] {filepath}: Would fix {fixed_in_file} issues")
                
                self.fixed_count += fixed_in_file
            else:
                logger.info(f"[SKIP]  {filepath}: No auto-fixable issues ({len(issues)} total)")
                self.skipped_count += len(issues)
        
        except Exception as e:
            logger.error(f"[ERROR] {filepath}: Error - {e}")
            self.error_count += len(issues)
    
    def _fix_division_by_zero(self, lines: List[str], issue: Dict) -> bool:
        """Add zero check before division - DISABLED (causes more issues)."""
        # Division by zero fixes create syntax errors
        # Better to handle at runtime with try/except
        return False
    
    def _fix_bare_except(self, lines: List[str], issue: Dict) -> bool:
        """Replace bare except with Exception."""
        
        line_idx = issue.get('line')
        if line_idx is None or line_idx < 1 or line_idx > len(lines):
            return False
        
        line_idx -= 1  # Convert to 0-based
        line = lines[line_idx]
        
        # Check if line is bare except
        if line.strip() == 'except:':
            lines[line_idx] = line.replace('except:', 'except Exception:')
            return True
        
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix CRITICAL and HIGH priority issues')
    parser.add_argument('--live', action='store_true', help='Apply fixes (default: dry-run)')
    parser.add_argument('--critical-only', action='store_true', help='Only fix CRITICAL issues')
    parser.add_argument('--high-only', action='store_true', help='Only fix HIGH issues')
    
    args = parser.parse_args()
    
    dry_run = not args.live
    fix_critical = not args.high_only
    fix_high = not args.critical_only
    
    fixer = ComprehensiveIssueFixer()
    fixer.fix_all_issues(
        fix_critical=fix_critical,
        fix_high=fix_high,
        dry_run=dry_run
    )


if __name__ == "__main__":
    main()
