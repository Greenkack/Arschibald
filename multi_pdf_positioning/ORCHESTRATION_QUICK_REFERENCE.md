# Multi-PDF Positioning System - Quick Reference

## Quick Start

### Run Complete Workflow
```bash
python -m multi_pdf_positioning.cli run
```

### Generate with Parallel Processing
```bash
python -m multi_pdf_positioning.cli generate --parallel --workers 4
```

## CLI Commands

### analyze
Analyze PDF templates and extract design information.

```bash
# Analyze all PDFs
python -m multi_pdf_positioning.cli analyze

# Analyze specific firmen
python -m multi_pdf_positioning.cli analyze --firmen 1,2,3

# Analyze specific seiten
python -m multi_pdf_positioning.cli analyze --seiten 1-4

# Save results to file
python -m multi_pdf_positioning.cli analyze --output analysis.json

# Verbose output
python -m multi_pdf_positioning.cli analyze --verbose
```

### generate
Generate optimized YML files with new positions.

```bash
# Generate all combinations
python -m multi_pdf_positioning.cli generate

# Generate with parallel processing
python -m multi_pdf_positioning.cli generate --parallel

# Specify number of workers
python -m multi_pdf_positioning.cli generate --parallel --workers 4

# Generate specific combinations
python -m multi_pdf_positioning.cli generate --firmen 1,2 --seiten 1-4

# Verbose output
python -m multi_pdf_positioning.cli generate --verbose
```

### validate
Validate YML coordinate files.

```bash
# Validate all files
python -m multi_pdf_positioning.cli validate

# Validate specific files
python -m multi_pdf_positioning.cli validate --firmen 1 --seiten 1

# Verbose output (shows details for each file)
python -m multi_pdf_positioning.cli validate --verbose
```

### backup
Create backup of YML files.

```bash
# Create backup
python -m multi_pdf_positioning.cli backup
```

### restore
Restore YML files from backup.

```bash
# List available backups
python -m multi_pdf_positioning.cli restore

# Restore specific backup (dry-run)
python -m multi_pdf_positioning.cli restore --backup-id backup_2025-01-10_14-30-00

# Actually restore
python -m multi_pdf_positioning.cli restore --backup-id backup_2025-01-10_14-30-00 --force
```

### run
Run complete workflow (backup, analyze, generate, validate).

```bash
# Run complete workflow
python -m multi_pdf_positioning.cli run

# Run for specific combinations
python -m multi_pdf_positioning.cli run --firmen 1,2,3 --seiten 1-4

# Skip backup
python -m multi_pdf_positioning.cli run --no-backup

# Skip validation
python -m multi_pdf_positioning.cli run --no-validate

# Quiet mode (no progress output)
python -m multi_pdf_positioning.cli run --quiet
```

## Global Options

```bash
--pdf-dir PATH        # PDF templates directory
--yml-dir PATH        # YML coordinates directory
--backup-dir PATH     # Backup directory
--output-dir PATH     # Output directory
-v, --verbose         # Enable verbose output
--version             # Show version
```

## Python API

### Main Workflow

```python
from multi_pdf_positioning.main_workflow import main

# Run complete workflow
summary = main()

# Run for specific firmen
summary = main(firmen=[1, 2, 3])

# Run for specific seiten
summary = main(seiten=[1, 2, 3, 4])

# Run without backup
summary = main(create_backup=False)

# Run without validation
summary = main(validate_output=False)

# Custom directories
summary = main(
    pdf_dir="path/to/pdfs",
    yml_dir="path/to/ymls",
    output_dir="path/to/output"
)
```

### Batch Processor

```python
from multi_pdf_positioning.batch_processor import process_all_combinations

# Sequential processing
summary = process_all_combinations()

# Parallel processing
summary = process_all_combinations(parallel=True, max_workers=4)

# Process specific combinations
summary = process_all_combinations(
    firmen=[1, 2],
    seiten=[1, 2, 3]
)

# Custom log level
summary = process_all_combinations(log_level="DEBUG")
```

### Individual Components

```python
# YML Parser
from multi_pdf_positioning.yml_parser import YMLParser
parser = YMLParser()
elements = parser.parse_yml("coords_multi/seite1_f1.yml")

# PDF Analyzer
from multi_pdf_positioning.pdf_analyzer import PDFAnalyzer
analyzer = PDFAnalyzer("pdf_templates_static/multi")
analysis = analyzer.analyze_pdf("pdf_templates_static/multi/multi_nt_01_f1.pdf")

# Position Calculator
from multi_pdf_positioning.position_calculator import PositionCalculator
calculator = PositionCalculator()
new_positions = calculator.calculate_positions(elements, analysis)

# YML Generator
from multi_pdf_positioning.yml_generator import YMLGenerator
generator = YMLGenerator()
generator.generate_yml(elements, new_positions, "output/seite1_f1.yml")

# Validation System
from multi_pdf_positioning.validation_system import ValidationSystem
validator = ValidationSystem()
report = validator.validate_positions(new_positions, elements)

# Backup Manager
from multi_pdf_positioning.backup_manager import BackupManager
backup_mgr = BackupManager("coords_multi", "coords_multi_backup")
backup_id = backup_mgr.create_backup()
```

## Argument Formats

### Firmen/Seiten Arguments

```bash
# Single value
--firmen 1

# Multiple values (comma-separated)
--firmen 1,2,3

# Range
--firmen 1-6

# Mixed
--firmen 1,3-5,7
# Results in: [1, 3, 4, 5, 7]
```

## Common Workflows

### Workflow 1: First Time Setup
```bash
# 1. Analyze PDFs
python -m multi_pdf_positioning.cli analyze --output analysis.json

# 2. Create backup
python -m multi_pdf_positioning.cli backup

# 3. Generate optimized YML files
python -m multi_pdf_positioning.cli generate --parallel --workers 4

# 4. Validate results
python -m multi_pdf_positioning.cli validate --verbose
```

### Workflow 2: Quick Test
```bash
# Test with single combination
python -m multi_pdf_positioning.cli run --firmen 1 --seiten 1 --no-backup
```

### Workflow 3: Production Run
```bash
# Full production run with all safety checks
python -m multi_pdf_positioning.cli run
```

### Workflow 4: Iterative Development
```bash
# 1. Test with subset
python -m multi_pdf_positioning.cli generate --firmen 1,2 --seiten 1-4

# 2. Validate
python -m multi_pdf_positioning.cli validate --firmen 1,2 --seiten 1-4 --verbose

# 3. If good, run full set
python -m multi_pdf_positioning.cli generate --parallel --workers 4
```

### Workflow 5: Recovery
```bash
# 1. List backups
python -m multi_pdf_positioning.cli restore

# 2. Restore specific backup
python -m multi_pdf_positioning.cli restore --backup-id backup_2025-01-10_14-30-00 --force

# 3. Verify restoration
python -m multi_pdf_positioning.cli validate
```

## Performance Tips

### Sequential vs Parallel

**Sequential (default):**
- Simpler, more predictable
- Better for debugging
- ~2-3 minutes for 48 combinations

**Parallel:**
- Faster processing
- Uses multiple CPU cores
- ~45-60 seconds for 48 combinations with 4 workers
- Use `--parallel --workers 4`

### Optimal Worker Count

```bash
# Auto (recommended)
--parallel

# Manual (4 workers is usually optimal)
--parallel --workers 4

# More workers (diminishing returns after 4-6)
--parallel --workers 8
```

## Troubleshooting

### Issue: "No YML files found"
**Solution:** Check `--yml-dir` path

### Issue: "PDF not found"
**Solution:** Check `--pdf-dir` path

### Issue: "Validation failed"
**Solution:** Run with `--verbose` to see details
```bash
python -m multi_pdf_positioning.cli validate --verbose
```

### Issue: "Backup failed"
**Solution:** Check write permissions on backup directory

### Issue: Slow processing
**Solution:** Use parallel processing
```bash
python -m multi_pdf_positioning.cli generate --parallel --workers 4
```

## Log Files

### Location
Default: `multi_pdf_positioning/positioning.log`

### View Logs
```bash
# View entire log
cat multi_pdf_positioning/positioning.log

# View last 50 lines
tail -n 50 multi_pdf_positioning/positioning.log

# Follow log in real-time
tail -f multi_pdf_positioning/positioning.log
```

### Log Levels
- **DEBUG:** Detailed information
- **INFO:** General progress
- **WARNING:** Non-critical issues
- **ERROR:** Critical failures

## Exit Codes

- `0` - Success
- `1` - Failure
- `130` - Interrupted by user (Ctrl+C)

## Configuration

Edit `multi_pdf_positioning/config.py` to change defaults:

```python
# Directories
PDF_DIR = Path("pdf_templates_static/multi")
YML_DIR = Path("coords_multi")
BACKUP_DIR = Path("coords_multi_backup")
OUTPUT_DIR = Path("multi_pdf_positioning/output")

# Processing
FIRMEN = [1, 2, 3, 4, 5, 6]
SEITEN = [1, 2, 3, 4, 5, 6, 7, 8]
CREATE_BACKUP = True
VALIDATE_OUTPUT = True
PARALLEL_PROCESSING = False

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = Path("multi_pdf_positioning/positioning.log")
```

## Help

### Get Help
```bash
# General help
python -m multi_pdf_positioning.cli --help

# Command-specific help
python -m multi_pdf_positioning.cli run --help
python -m multi_pdf_positioning.cli generate --help
```

### Version
```bash
python -m multi_pdf_positioning.cli --version
```

## Examples

### Example 1: Quick Test
```bash
python -m multi_pdf_positioning.cli run --firmen 1 --seiten 1 --no-backup
```

### Example 2: Production Run
```bash
python -m multi_pdf_positioning.cli run
```

### Example 3: Parallel Generation
```bash
python -m multi_pdf_positioning.cli generate --parallel --workers 4
```

### Example 4: Validate Specific Files
```bash
python -m multi_pdf_positioning.cli validate --firmen 1,2,3 --verbose
```

### Example 5: Backup and Restore
```bash
# Backup
python -m multi_pdf_positioning.cli backup

# Restore
python -m multi_pdf_positioning.cli restore --backup-id backup_2025-01-10_14-30-00 --force
```

## Support

For issues or questions:
1. Check this quick reference
2. Run with `--verbose` for detailed output
3. Check log file: `multi_pdf_positioning/positioning.log`
4. Review documentation: `TASK_9_COMPLETE.md`
