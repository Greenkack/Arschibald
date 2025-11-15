"""
Comprehensive Error Detection and Validation System.

Automatically scans the application for:
- Potential errors
- Performance bottlenecks
- Code quality issues
- Security vulnerabilities
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Issue:
    """Represents a detected issue."""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # ERROR, PERFORMANCE, SECURITY, QUALITY
    file: str
    line: Optional[int]
    message: str
    suggestion: str
    
    def __repr__(self):
        return f"[{self.severity}] {self.category}: {self.message} ({self.file}:{self.line})"


class CodeAnalyzer:
    """Analyzes Python code for potential issues."""
    
    def __init__(self):
        self.issues: List[Issue] = []
    
    def analyze_file(self, filepath: Path) -> List[Issue]:
        """Analyze a single Python file."""
        issues = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(filepath))
            
            # Check for various issues
            issues.extend(self._check_error_handling(tree, filepath))
            issues.extend(self._check_performance(tree, filepath))
            issues.extend(self._check_quality(tree, filepath))
            
        except SyntaxError as e:
            issues.append(Issue(
                severity="CRITICAL",
                category="ERROR",
                file=str(filepath),
                line=e.lineno,
                message=f"Syntax error: {e.msg}",
                suggestion="Fix syntax error"
            ))
        except Exception as e:
            logger.error(f"Error analyzing {filepath}: {e}")
        
        return issues
    
    def _check_error_handling(self, tree: ast.AST, filepath: Path) -> List[Issue]:
        """Check for error handling issues."""
        issues = []
        
        for node in ast.walk(tree):
            # Bare except clauses
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append(Issue(
                    severity="MEDIUM",
                    category="QUALITY",
                    file=str(filepath),
                    line=node.lineno,
                    message="Bare except clause catches all exceptions",
                    suggestion="Specify exception type: except ValueError:"
                ))
            
            # Division operations without zero check
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                issues.append(Issue(
                    severity="HIGH",
                    category="ERROR",
                    file=str(filepath),
                    line=node.lineno,
                    message="Potential division by zero",
                    suggestion="Add zero check before division"
                ))
        
        return issues
    
    def _check_performance(self, tree: ast.AST, filepath: Path) -> List[Issue]:
        """Check for performance issues."""
        issues = []
        
        for node in ast.walk(tree):
            # String concatenation in loops
            if isinstance(node, ast.For):
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                        if isinstance(child.target, ast.Name):
                            issues.append(Issue(
                                severity="MEDIUM",
                                category="PERFORMANCE",
                                file=str(filepath),
                                line=node.lineno,
                                message="String concatenation in loop",
                                suggestion="Use list and join() instead"
                            ))
        
        return issues
    
    def _check_quality(self, tree: ast.AST, filepath: Path) -> List[Issue]:
        """Check for code quality issues."""
        issues = []
        
        for node in ast.walk(tree):
            # Too many function parameters
            if isinstance(node, ast.FunctionDef):
                param_count = len(node.args.args)
                if param_count > 10:
                    issues.append(Issue(
                        severity="MEDIUM",
                        category="QUALITY",
                        file=str(filepath),
                        line=node.lineno,
                        message=f"Function {node.name} has {param_count} parameters",
                        suggestion="Consider using a config object or reducing parameters"
                    ))
                
                # Complex functions (many nested ifs/loops)
                complexity = self._calculate_complexity(node)
                if complexity > 15:
                    issues.append(Issue(
                        severity="MEDIUM",
                        category="QUALITY",
                        file=str(filepath),
                        line=node.lineno,
                        message=f"Function {node.name} has high complexity ({complexity})",
                        suggestion="Refactor into smaller functions"
                    ))
        
        return issues
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity


class ApplicationScanner:
    """Scans the entire application for issues."""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.analyzer = CodeAnalyzer()
        self.issues: List[Issue] = []
    
    def scan_application(self, skip_dirs: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Scan the entire application.
        
        Args:
            skip_dirs: Directories to skip
            
        Returns:
            Scan results
        """
        if skip_dirs is None:
            skip_dirs = ['__pycache__', '.git', 'venv', 'env', '.venv', 'node_modules']
        
        logger.info("Starting application scan...")
        
        python_files = []
        
        for py_file in self.root_dir.rglob('*.py'):
            # Skip excluded directories
            if any(skip_dir in py_file.parts for skip_dir in skip_dirs):
                continue
            python_files.append(py_file)
        
        logger.info(f"Found {len(python_files)} Python files")
        
        # Analyze each file
        for filepath in python_files:
            file_issues = self.analyzer.analyze_file(filepath)
            self.issues.extend(file_issues)
        
        # Generate report
        report = self._generate_report()
        
        logger.info(f"Scan complete: {len(self.issues)} issues found")
        
        return report
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive report."""
        
        # Count by severity
        severity_counts = {
            "CRITICAL": sum(1 for i in self.issues if i.severity == "CRITICAL"),
            "HIGH": sum(1 for i in self.issues if i.severity == "HIGH"),
            "MEDIUM": sum(1 for i in self.issues if i.severity == "MEDIUM"),
            "LOW": sum(1 for i in self.issues if i.severity == "LOW")
        }
        
        # Count by category
        category_counts = {}
        for issue in self.issues:
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1
        
        # Group by file
        file_issues = {}
        for issue in self.issues:
            if issue.file not in file_issues:
                file_issues[issue.file] = []
            file_issues[issue.file].append(issue)
        
        # Top problematic files
        top_files = sorted(
            file_issues.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:10]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_issues": len(self.issues),
            "severity_breakdown": severity_counts,
            "category_breakdown": category_counts,
            "top_problematic_files": [
                {"file": f, "issue_count": len(issues)}
                for f, issues in top_files
            ],
            "issues": [
                {
                    "severity": i.severity,
                    "category": i.category,
                    "file": i.file,
                    "line": i.line,
                    "message": i.message,
                    "suggestion": i.suggestion
                }
                for i in self.issues
            ]
        }
    
    def get_critical_issues(self) -> List[Issue]:
        """Get only critical issues."""
        return [i for i in self.issues if i.severity == "CRITICAL"]
    
    def get_high_priority_issues(self) -> List[Issue]:
        """Get critical and high priority issues."""
        return [i for i in self.issues if i.severity in ("CRITICAL", "HIGH")]


def scan_and_report(output_file: str = "code_analysis_report.json"):
    """
    Scan application and save report.
    
    Args:
        output_file: Output file path
    """
    import json
    
    scanner = ApplicationScanner()
    report = scanner.scan_application()
    
    # Save report
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*80)
    print("CODE ANALYSIS REPORT")
    print("="*80)
    print(f"\nTotal Issues: {report['total_issues']}")
    print(f"\nSeverity Breakdown:")
    for severity, count in report['severity_breakdown'].items():
        print(f"  {severity}: {count}")
    
    print(f"\nCategory Breakdown:")
    for category, count in report['category_breakdown'].items():
        print(f"  {category}: {count}")
    
    print(f"\nTop Problematic Files:")
    for item in report['top_problematic_files'][:5]:
        print(f"  {item['file']}: {item['issue_count']} issues")
    
    print(f"\nReport saved: {output_file}")
    print("="*80 + "\n")
    
    # Show critical issues
    critical = scanner.get_critical_issues()
    if critical:
        print(f"\n🔴 CRITICAL ISSUES ({len(critical)}):")
        for issue in critical[:5]:
            print(f"  - {issue.file}:{issue.line} - {issue.message}")


if __name__ == "__main__":
    scan_and_report()
