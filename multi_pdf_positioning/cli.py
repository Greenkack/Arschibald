"""
Command-Line Interface for Multi-PDF Positioning System

This module provides a comprehensive CLI with commands for:
- analyze: Analyze PDF templates
- generate: Generate optimized YML files
- validate: Validate YML files
- backup: Create backups
- restore: Restore from backup
- run: Run complete workflow

Requirements: All (Task 9.3)
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

# Import workflow components
from multi_pdf_positioning.main_workflow import main as run_workflow
from multi_pdf_positioning.batch_processor import process_all_combinations
from multi_pdf_positioning.pdf_analyzer import PDFAnalyzer
from multi_pdf_positioning.yml_parser import YMLParser
from multi_pdf_positioning.validation_system import ValidationSystem
from multi_pdf_positioning.backup_manager import BackupManager
from multi_pdf_positioning.config import (
    PDF_DIR, YML_DIR, BACKUP_DIR, OUTPUT_DIR, FIRMEN, SEITEN
)


def parse_list_arg(arg: str) -> List[int]:
    """
    Parse a comma-separated list of integers.
    
    Args:
        arg: String like "1,2,3" or "1-3"
        
    Returns:
        List of integers
        
    Examples:
        >>> parse_list_arg("1,2,3")
        [1, 2, 3]
        >>> parse_list_arg("1-3")
        [1, 2, 3]
        >>> parse_list_arg("1,3-5,7")
        [1, 3, 4, 5, 7]
    """
    result = []
    
    for part in arg.split(','):
        part = part.strip()
        
        if '-' in part:
            # Range like "1-3"
            start, end = part.split('-')
            result.extend(range(int(start), int(end) + 1))
        else:
            # Single number
            result.append(int(part))
    
    return sorted(set(result))  # Remove duplicates and sort


def cmd_analyze(args):
    """
    Analyze PDF templates.
    
    Args:
        args: Parsed command-line arguments
    """
    print("\n=== PDF Analysis ===\n")
    
    # Parse firmen and seiten
    firmen = parse_list_arg(args.firmen) if args.firmen else FIRMEN
    seiten = parse_list_arg(args.seiten) if args.seiten else SEITEN
    
    print(f"Analyzing {len(firmen) * len(seiten)} PDF templates...")
    print(f"  Firmen: {firmen}")
    print(f"  Seiten: {seiten}")
    print(f"  PDF Directory: {args.pdf_dir}")
    
    # Create analyzer
    analyzer = PDFAnalyzer(str(args.pdf_dir))
    
    # Analyze PDFs
    try:
        analyses = analyzer.analyze_all_pdfs(
            str(args.pdf_dir),
            firmen=firmen,
            seiten=seiten
        )
        
        print(f"\n[OK] Successfully analyzed {len(analyses)} PDFs")
        
        # Save results if output specified
        if args.output:
            output_path = Path(args.output)
            analyzer.save_analysis_results(str(output_path), include_summary=True)
            print(f"  Results saved to: {output_path}")
        
        # Display summary
        if args.verbose:
            print("\nSummary by Firma:")
            for firma in firmen:
                firma_analyses = [a for a in analyses if a.firma == firma]
                print(f"  Firma {firma}: {len(firma_analyses)} PDFs")
                
                if firma_analyses:
                    colors = firma_analyses[0].color_palette
                    print(f"    Color palette: {', '.join(colors)}")
        
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_generate(args):
    """
    Generate optimized YML files.
    
    Args:
        args: Parsed command-line arguments
    """
    print("\n=== Generate Optimized YML Files ===\n")
    
    # Parse firmen and seiten
    firmen = parse_list_arg(args.firmen) if args.firmen else FIRMEN
    seiten = parse_list_arg(args.seiten) if args.seiten else SEITEN
    
    print(f"Generating YML files for {len(firmen) * len(seiten)} combinations...")
    print(f"  Firmen: {firmen}")
    print(f"  Seiten: {seiten}")
    print(f"  Parallel: {args.parallel}")
    if args.parallel:
        print(f"  Workers: {args.workers or 'auto'}")
    
    # Run batch processing
    try:
        summary = process_all_combinations(
            firmen=firmen,
            seiten=seiten,
            parallel=args.parallel,
            max_workers=args.workers,
            pdf_dir=args.pdf_dir,
            yml_dir=args.yml_dir,
            output_dir=args.output_dir,
            log_level="DEBUG" if args.verbose else "INFO"
        )
        
        print(f"\n[OK] Generation complete")
        print(f"  Successful: {summary.successful}/{summary.total_processed}")
        print(f"  Failed: {summary.failed}")
        print(f"  Total time: {summary.total_time:.2f}s")
        print(f"  Output directory: {args.output_dir}")
        
        return 0 if summary.failed == 0 else 1
        
    except Exception as e:
        print(f"\n[ERROR] Generation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_validate(args):
    """
    Validate YML files.
    
    Args:
        args: Parsed command-line arguments
    """
    print("\n=== Validate YML Files ===\n")
    
    # Parse firmen and seiten
    firmen = parse_list_arg(args.firmen) if args.firmen else FIRMEN
    seiten = parse_list_arg(args.seiten) if args.seiten else SEITEN
    
    print(f"Validating {len(firmen) * len(seiten)} YML files...")
    
    # Create components
    yml_parser = YMLParser()
    validator = ValidationSystem()
    
    total_errors = 0
    total_warnings = 0
    failed_files = []
    
    for firma in firmen:
        for seite in seiten:
            yml_filename = f"seite{seite}_f{firma}.yml"
            if yml_filename != 0:
                yml_path = args.yml_dir / yml_filename
            else:
                yml_path = 0.0
            
            try:
                # Parse YML
                elements = yml_parser.parse_yml(str(yml_path))
                
                # Extract positions
                positions = [elem.position for elem in elements]
                
                # Validate
                report = validator.generate_validation_report(
                    positions,
                    elements,
                    firma,
                    seite
                )
                
                errors = len(report.get_errors())
                warnings = len(report.get_warnings())
                
                total_errors += errors
                total_warnings += warnings
                
                if not report.is_valid:
                    failed_files.append(yml_filename)
                    
                    if args.verbose:
                        print(f"\n[ERROR] {yml_filename}:")
                        for error in report.get_errors()[:3]:
                            print(f"    Error: {error.message}")
                        for warning in report.get_warnings()[:3]:
                            print(f"    Warning: {warning.message}")
                elif args.verbose:
                    print(f"[OK] {yml_filename}: Valid")
                
            except Exception as e:
                print(f"[ERROR] {yml_filename}: Failed to validate - {e}")
                failed_files.append(yml_filename)
    
    # Summary
    print(f"\n=== Validation Summary ===")
    print(f"Total files: {len(firmen) * len(seiten)}")
    print(f"Valid: {len(firmen) * len(seiten) - len(failed_files)}")
    print(f"Invalid: {len(failed_files)}")
    print(f"Total errors: {total_errors}")
    print(f"Total warnings: {total_warnings}")
    
    if failed_files:
        print(f"\nFailed files:")
        for filename in failed_files:
            print(f"  - {filename}")
    
    return 0 if len(failed_files) == 0 else 1


def cmd_backup(args):
    """
    Create backup of YML files.
    
    Args:
        args: Parsed command-line arguments
    """
    print("\n=== Create Backup ===\n")
    
    # Create backup manager
    backup_manager = BackupManager(args.yml_dir, args.backup_dir)
    
    # Get list of YML files
    yml_files = list(args.yml_dir.glob("*.yml"))
    
    if not yml_files:
        print(f"[ERROR] No YML files found in {args.yml_dir}")
        return 1
    
    print(f"Creating backup of {len(yml_files)} YML files...")
    print(f"  Source: {args.yml_dir}")
    print(f"  Backup directory: {args.backup_dir}")
    
    try:
        backup_id = backup_manager.create_backup(yml_files)
        
        print(f"\n[OK] Backup created successfully")
        print(f"  Backup ID: {backup_id}")
        print(f"  Location: {args.backup_dir / backup_id}")
        
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] Backup failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_restore(args):
    """
    Restore YML files from backup.
    
    Args:
        args: Parsed command-line arguments
    """
    print("\n=== Restore from Backup ===\n")
    
    # Create backup manager
    backup_manager = BackupManager(args.yml_dir, args.backup_dir)
    
    # If no backup ID specified, list available backups
    if not args.backup_id:
        print("Available backups:")
        backups = backup_manager.list_backups()
        
        if not backups:
            print("  No backups found")
            return 1
        
        for backup in backups:
            print(f"\n  Backup ID: {backup['backup_id']}")
            print(f"    Timestamp: {backup.get('timestamp', 'unknown')}")
            print(f"    Files: {backup.get('files_count', 'unknown')}")
        
        print("\nTo restore a backup, use: --backup-id <backup_id>")
        return 0
    
    # Validate backup
    print(f"Validating backup: {args.backup_id}")
    validation = backup_manager.validate_backup(args.backup_id)
    
    if not validation['valid']:
        print(f"\n[ERROR] Backup validation failed:")
        for error in validation['errors']:
            print(f"    {error}")
        return 1
    
    print(f"[OK] Backup is valid")
    
    # Restore (dry-run first if not forced)
    if not args.force:
        print("\nDry-run mode (use --force to actually restore):")
        backup_manager.restore_backup(args.backup_id, confirm=False)
        return 0
    
    print(f"\nRestoring backup: {args.backup_id}")
    
    try:
        success = backup_manager.restore_backup(args.backup_id, confirm=True)
        
        if success:
            print(f"\n[OK] Backup restored successfully")
            return 0
        else:
            print(f"\n[ERROR] Backup restoration failed")
            return 1
            
    except Exception as e:
        print(f"\n[ERROR] Restore failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_run(args):
    """
    Run complete workflow.
    
    Args:
        args: Parsed command-line arguments
    """
    print("\n=== Run Complete Workflow ===\n")
    
    # Parse firmen and seiten
    firmen = parse_list_arg(args.firmen) if args.firmen else None
    seiten = parse_list_arg(args.seiten) if args.seiten else None
    
    # Run workflow
    try:
        summary = run_workflow(
            firmen=firmen,
            seiten=seiten,
            pdf_dir=args.pdf_dir,
            yml_dir=args.yml_dir,
            backup_dir=args.backup_dir,
            output_dir=args.output_dir,
            create_backup=not args.no_backup,
            validate_output=not args.no_validate,
            show_progress=not args.quiet
        )
        
        return 0 if summary.successful == summary.total_combinations else 1
        
    except Exception as e:
        print(f"\n[ERROR] Workflow failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def create_parser() -> argparse.ArgumentParser:
    """
    Create the argument parser with all commands and options.
    
    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog='multi-pdf-positioning',
        description='Multi-PDF Positioning System - Optimize text positions in PDF templates',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete workflow
  %(prog)s run
  
  # Run for specific firmen
  %(prog)s run --firmen 1,2,3
  
  # Run for specific seiten
  %(prog)s run --seiten 1-4
  
  # Generate with parallel processing
  %(prog)s generate --parallel --workers 4
  
  # Analyze PDFs and save results
  %(prog)s analyze --output analysis.json
  
  # Validate YML files
  %(prog)s validate --verbose
  
  # Create backup
  %(prog)s backup
  
  # List available backups
  %(prog)s restore
  
  # Restore specific backup
  %(prog)s restore --backup-id backup_2025-01-10_14-30-00 --force

For more information, visit: https://github.com/your-repo/multi-pdf-positioning
        """
    )
    
    # Global options
    parser.add_argument(
        '--pdf-dir',
        type=Path,
        default=PDF_DIR,
        help=f'PDF templates directory (default: {PDF_DIR})'
    )
    parser.add_argument(
        '--yml-dir',
        type=Path,
        default=YML_DIR,
        help=f'YML coordinates directory (default: {YML_DIR})'
    )
    parser.add_argument(
        '--backup-dir',
        type=Path,
        default=BACKUP_DIR,
        help=f'Backup directory (default: {BACKUP_DIR})'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=OUTPUT_DIR,
        help=f'Output directory (default: {OUTPUT_DIR})'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(
        title='commands',
        description='Available commands',
        dest='command',
        required=True
    )
    
    # Command: analyze
    parser_analyze = subparsers.add_parser(
        'analyze',
        help='Analyze PDF templates',
        description='Analyze PDF templates and extract design information'
    )
    parser_analyze.add_argument(
        '--firmen',
        type=str,
        help='Comma-separated list of firmen (e.g., "1,2,3" or "1-6")'
    )
    parser_analyze.add_argument(
        '--seiten',
        type=str,
        help='Comma-separated list of seiten (e.g., "1,2,3" or "1-8")'
    )
    parser_analyze.add_argument(
        '-o', '--output',
        type=str,
        help='Output file for analysis results (JSON)'
    )
    parser_analyze.set_defaults(func=cmd_analyze)
    
    # Command: generate
    parser_generate = subparsers.add_parser(
        'generate',
        help='Generate optimized YML files',
        description='Generate optimized YML files with new positions'
    )
    parser_generate.add_argument(
        '--firmen',
        type=str,
        help='Comma-separated list of firmen (e.g., "1,2,3" or "1-6")'
    )
    parser_generate.add_argument(
        '--seiten',
        type=str,
        help='Comma-separated list of seiten (e.g., "1,2,3" or "1-8")'
    )
    parser_generate.add_argument(
        '--parallel',
        action='store_true',
        help='Enable parallel processing'
    )
    parser_generate.add_argument(
        '--workers',
        type=int,
        help='Number of parallel workers (default: auto)'
    )
    parser_generate.set_defaults(func=cmd_generate)
    
    # Command: validate
    parser_validate = subparsers.add_parser(
        'validate',
        help='Validate YML files',
        description='Validate YML coordinate files'
    )
    parser_validate.add_argument(
        '--firmen',
        type=str,
        help='Comma-separated list of firmen (e.g., "1,2,3" or "1-6")'
    )
    parser_validate.add_argument(
        '--seiten',
        type=str,
        help='Comma-separated list of seiten (e.g., "1,2,3" or "1-8")'
    )
    parser_validate.set_defaults(func=cmd_validate)
    
    # Command: backup
    parser_backup = subparsers.add_parser(
        'backup',
        help='Create backup of YML files',
        description='Create a timestamped backup of all YML files'
    )
    parser_backup.set_defaults(func=cmd_backup)
    
    # Command: restore
    parser_restore = subparsers.add_parser(
        'restore',
        help='Restore YML files from backup',
        description='Restore YML files from a previous backup'
    )
    parser_restore.add_argument(
        '--backup-id',
        type=str,
        help='Backup ID to restore (omit to list available backups)'
    )
    parser_restore.add_argument(
        '--force',
        action='store_true',
        help='Actually restore (without this, only shows what would be restored)'
    )
    parser_restore.set_defaults(func=cmd_restore)
    
    # Command: run
    parser_run = subparsers.add_parser(
        'run',
        help='Run complete workflow',
        description='Run the complete workflow: backup, analyze, generate, validate'
    )
    parser_run.add_argument(
        '--firmen',
        type=str,
        help='Comma-separated list of firmen (e.g., "1,2,3" or "1-6")'
    )
    parser_run.add_argument(
        '--seiten',
        type=str,
        help='Comma-separated list of seiten (e.g., "1,2,3" or "1-8")'
    )
    parser_run.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip backup creation'
    )
    parser_run.add_argument(
        '--no-validate',
        action='store_true',
        help='Skip validation'
    )
    parser_run.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress output'
    )
    parser_run.set_defaults(func=cmd_run)
    
    return parser


def main():
    """
    Main CLI entry point.
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Execute command
    try:
        exit_code = args.func(args)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
