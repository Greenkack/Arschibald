# Multi-PDF Positioning System - CLI Reference

## Quick Reference

### Most Common Commands

```bash
# Process everything
python -m multi_pdf_positioning.cli --all

# Process with visualizations and statistics
python -m multi_pdf_positioning.cli --all --visualize --statistics

# Process single firma
python -m multi_pdf_positioning.cli --firma 1

# Process single combination
python -m multi_pdf_positioning.cli --firma 1 --seite 1

# Restore from backup
python -m multi_pdf_positioning.cli --restore backup_20250110_143000
```

## Complete CLI Options

### Selection Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--all` | `-a` | Process all 48 combinations | `--all` |
| `--firma NUMMER` | `-f` | Process specific firma(s) | `--firma 1` or `-f 1,2,3` |
| `--seite NUMMER` | `-s` | Process specific seite(n) | `--seite 1` or `-s 1,2,3` |

### Analysis Options

| Option | Description | Example |
|--------|-------------|---------|
| `--analyze` | Perform PDF analysis only | `--analyze` |
| `--analyze-output PATH` | Output path for analysis | `--analyze-output analysis.json` |

### Generation Options

| Option | Description | Example |
|--------|-------------|---------|
| `--generate` | Generate YML files | `--generate` |
| `--output-dir PATH` | Output directory | `--output-dir output/` |
| `--no-backup` | Skip backup creation | `--no-backup` |

### Validation Options

| Option | Description | Example |
|--------|-------------|---------|
| `--validate` | Perform validation only | `--validate` |
| `--no-validate` | Skip validation | `--no-validate` |
| `--validation-report PATH` | Save validation report | `--validation-report report.txt` |

### Backup Options

| Option | Description | Example |
|--------|-------------|---------|
| `--backup` | Create backup | `--backup` |
| `--restore BACKUP_ID` | Restore from backup | `--restore backup_20250110_143000` |
| `--list-backups` | List available backups | `--list-backups` |

### Visualization Options

| Option | Description | Example |
|--------|-------------|---------|
| `--visualize` | Create visualizations | `--visualize` |
| `--viz-output PATH` | Output directory for images | `--viz-output viz/` |
| `--viz-type TYPE` | Visualization type | `--viz-type overlay` |

**Visualization Types:**
- `overlay` - Old (red) and new (green) positions overlaid
- `comparison` - Side-by-side comparison
- `movement` - Movement arrows showing changes
- `collision` - Collision highlighting
- `all` - All types (default)

### Statistics Options

| Option | Description | Example |
|--------|-------------|---------|
| `--statistics` | Generate statistics | `--statistics` |
| `--stats-output PATH` | Output path | `--stats-output stats.json` |
| `--stats-format FORMAT` | Output format | `--stats-format json` |

**Statistics Formats:**
- `txt` - Human-readable text (default)
- `json` - Machine-readable JSON
- `csv` - Spreadsheet-compatible CSV

### Output Options

| Option | Description | Example |
|--------|-------------|---------|
| `--quiet` | Suppress progress output | `--quiet` |
| `--verbose` | Detailed output | `--verbose` |
| `--help` | Show help message | `--help` |

## Usage Examples

### Basic Usage

```bash
# Process all combinations with default settings
python -m multi_pdf_positioning.cli --all

# Process specific firma
python -m multi_pdf_positioning.cli --firma 1

# Process specific seite
python -m multi_pdf_positioning.cli --seite 1

# Process specific combination
python -m multi_pdf_positioning.cli --firma 1 --seite 1

# Process multiple firmen
python -m multi_pdf_positioning.cli --firma 1,2,3

# Process multiple seiten
python -m multi_pdf_positioning.cli --seite 1,2,3
```

### Analysis Only

```bash
# Analyze PDFs without generating YML files
python -m multi_pdf_positioning.cli --analyze --all

# Analyze and save results
python -m multi_pdf_positioning.cli --analyze --all --analyze-output analysis.json

# Analyze specific firma
python -m multi_pdf_positioning.cli --analyze --firma 1
```

### Generation with Options

```bash
# Generate without backup
python -m multi_pdf_positioning.cli --all --no-backup

# Generate to custom output directory
python -m multi_pdf_positioning.cli --all --output-dir custom_output/

# Generate without validation
python -m multi_pdf_positioning.cli --all --no-validate
```

### Validation

```bash
# Validate existing YML files
python -m multi_pdf_positioning.cli --validate --all

# Validate and save report
python -m multi_pdf_positioning.cli --validate --all --validation-report validation.txt

# Validate specific combination
python -m multi_pdf_positioning.cli --validate --firma 1 --seite 1
```

### Backup and Restore

```bash
# Create backup only
python -m multi_pdf_positioning.cli --backup

# List available backups
python -m multi_pdf_positioning.cli --list-backups

# Restore from specific backup
python -m multi_pdf_positioning.cli --restore backup_20250110_143000

# Process with backup
python -m multi_pdf_positioning.cli --all --backup
```

### Visualization

```bash
# Create all visualization types
python -m multi_pdf_positioning.cli --all --visualize

# Create specific visualization type
python -m multi_pdf_positioning.cli --all --visualize --viz-type overlay

# Create visualizations for specific combination
python -m multi_pdf_positioning.cli --firma 1 --seite 1 --visualize

# Save to custom directory
python -m multi_pdf_positioning.cli --all --visualize --viz-output my_visualizations/

# Create only comparison views
python -m multi_pdf_positioning.cli --all --visualize --viz-type comparison
```

### Statistics

```bash
# Generate statistics in text format
python -m multi_pdf_positioning.cli --all --statistics

# Generate statistics in JSON format
python -m multi_pdf_positioning.cli --all --statistics --stats-format json --stats-output stats.json

# Generate statistics in CSV format
python -m multi_pdf_positioning.cli --all --statistics --stats-format csv --stats-output stats.csv

# Generate statistics for specific firma
python -m multi_pdf_positioning.cli --firma 1 --statistics
```

### Combined Operations

```bash
# Full workflow with visualizations and statistics
python -m multi_pdf_positioning.cli --all --visualize --statistics

# Process, visualize, and generate JSON statistics
python -m multi_pdf_positioning.cli --all \
  --visualize --viz-output viz/ \
  --statistics --stats-format json --stats-output stats.json

# Process specific firma with all features
python -m multi_pdf_positioning.cli --firma 1 \
  --visualize \
  --statistics --stats-format csv --stats-output firma1_stats.csv

# Quiet mode with output to files
python -m multi_pdf_positioning.cli --all --quiet \
  --validation-report validation.txt \
  --stats-output stats.txt
```

### Advanced Usage

```bash
# Process without backup or validation (fast mode)
python -m multi_pdf_positioning.cli --all --no-backup --no-validate

# Analyze, generate, validate, visualize, and create statistics
python -m multi_pdf_positioning.cli --all \
  --analyze --analyze-output analysis.json \
  --generate --output-dir output/ \
  --validate --validation-report validation.txt \
  --visualize --viz-output visualizations/ \
  --statistics --stats-format json --stats-output stats.json

# Process with verbose output
python -m multi_pdf_positioning.cli --all --verbose

# Test run on single combination
python -m multi_pdf_positioning.cli --firma 1 --seite 1 \
  --visualize --statistics --verbose
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - All combinations processed successfully |
| 1 | Partial failure - Some combinations failed |
| 2 | Complete failure - No combinations processed |
| 3 | Configuration error - Invalid paths or settings |
| 4 | Backup/restore error |

## Environment Variables

You can set these environment variables to override default settings:

```bash
# Set PDF directory
export MULTI_PDF_DIR="/path/to/pdfs"

# Set YML directory
export MULTI_YML_DIR="/path/to/ymls"

# Set backup directory
export MULTI_BACKUP_DIR="/path/to/backups"

# Set output directory
export MULTI_OUTPUT_DIR="/path/to/output"

# Run with environment variables
python -m multi_pdf_positioning.cli --all
```

## Configuration File

You can also use a configuration file:

```bash
# Create config file
cat > multi_pdf_config.json << EOF
{
  "pdf_dir": "/path/to/pdfs",
  "yml_dir": "/path/to/ymls",
  "backup_dir": "/path/to/backups",
  "output_dir": "/path/to/output",
  "create_backup": true,
  "validate_output": true,
  "show_progress": true
}
EOF

# Run with config file
python -m multi_pdf_positioning.cli --config multi_pdf_config.json --all
```

## Troubleshooting

### Command Not Found

```bash
# If module not found, ensure you're in the correct directory
cd /path/to/project

# Or use full path
python /path/to/project/multi_pdf_positioning/cli.py --all
```

### Permission Errors

```bash
# On Unix/Linux, you may need to make the script executable
chmod +x multi_pdf_positioning/cli.py

# Or run with python explicitly
python -m multi_pdf_positioning.cli --all
```

### Import Errors

```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Or install individually
pip install PyPDF2 PyYAML Pillow
```

## Tips and Best Practices

### 1. Always Create Backups

```bash
# Good practice: Always backup before processing
python -m multi_pdf_positioning.cli --backup
python -m multi_pdf_positioning.cli --all
```

### 2. Test on Single Combination First

```bash
# Test on one combination before processing all
python -m multi_pdf_positioning.cli --firma 1 --seite 1 --visualize --statistics
```

### 3. Use Validation Reports

```bash
# Always save validation reports for review
python -m multi_pdf_positioning.cli --all --validation-report validation.txt
```

### 4. Generate Visualizations for Review

```bash
# Create visualizations to review changes
python -m multi_pdf_positioning.cli --all --visualize --viz-output viz/
```

### 5. Keep Statistics for Documentation

```bash
# Export statistics in multiple formats
python -m multi_pdf_positioning.cli --all \
  --statistics \
  --stats-format json --stats-output stats.json
python -m multi_pdf_positioning.cli --all \
  --statistics \
  --stats-format csv --stats-output stats.csv
```

## Batch Processing Scripts

### Windows Batch Script

```batch
@echo off
REM Process all combinations with full reporting
python -m multi_pdf_positioning.cli --all ^
  --visualize --viz-output visualizations/ ^
  --statistics --stats-format json --stats-output stats.json ^
  --validation-report validation.txt

echo Processing complete!
pause
```

### Unix/Linux Shell Script

```bash
#!/bin/bash
# Process all combinations with full reporting
python -m multi_pdf_positioning.cli --all \
  --visualize --viz-output visualizations/ \
  --statistics --stats-format json --stats-output stats.json \
  --validation-report validation.txt

echo "Processing complete!"
```

---

**Last Updated**: 2025-01-10  
**Version**: 1.0.0
