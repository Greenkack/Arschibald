# Multi-PDF Positioning System - Deployment Guide

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Deployment Steps](#deployment-steps)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

## System Requirements

### Hardware Requirements

- **CPU**: Dual-core processor or better (quad-core recommended for parallel processing)
- **RAM**: Minimum 4 GB (8 GB recommended)
- **Storage**: Minimum 500 MB free space for installation and data
- **Disk I/O**: SSD recommended for better performance

### Software Requirements

- **Operating System**: 
  - Windows 10/11
  - Linux (Ubuntu 20.04+, Debian 11+, or equivalent)
  - macOS 10.15+
  
- **Python**: Version 3.8 or higher (3.10+ recommended)
  
- **Dependencies**:
  - PyYAML >= 6.0
  - PyPDF2 >= 3.0.0
  - pdfplumber >= 0.10.0
  - Pillow >= 10.0.0 (optional, for visualization)

### Network Requirements

- No network connectivity required (system runs locally)
- Optional: Network access for downloading dependencies during installation

## Installation

### Method 1: Using pip (Recommended)

```bash
# Clone or download the repository
cd multi_pdf_positioning

# Install the package
pip install -e .

# Verify installation
multi-pdf-positioning --version
```

### Method 2: Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Add to Python path (optional)
export PYTHONPATH="${PYTHONPATH}:/path/to/multi_pdf_positioning"
```

### Method 3: Virtual Environment (Recommended for Production)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install package
pip install -e .
```

## Configuration

### 1. Directory Structure

Ensure the following directory structure exists:

```
project_root/
├── pdf_templates_static/
│   └── multi/
│       ├── multi_nt_01_f1.pdf
│       ├── multi_nt_01_f2.pdf
│       └── ... (48 PDF files total)
├── coords_multi/
│   ├── seite1_f1.yml
│   ├── seite1_f2.yml
│   └── ... (48 YML files total)
├── multi_pdf_positioning/
│   └── (system files)
└── output/
    └── (generated files will be placed here)
```

### 2. Configuration File

Edit `multi_pdf_positioning/config.py` to set your paths:

```python
# PDF templates directory
PDF_DIR = Path("C:/Users/win10/Desktop/Bokuk2 - Kopie/pdf_templates_static/multi")

# YML coordinates directory
YML_DIR = Path("coords_multi")

# Output directory
OUTPUT_DIR = Path("output")

# Backup directory
BACKUP_DIR = Path("coords_multi_backup")

# Firmen and Seiten to process
FIRMEN = [1, 2, 3, 4, 5, 6]
SEITEN = [1, 2, 3, 4, 5, 6, 7, 8]
```

### 3. Verify Configuration

```bash
# Test configuration
python -c "from multi_pdf_positioning.config import *; print(f'PDF Dir: {PDF_DIR}'); print(f'YML Dir: {YML_DIR}')"
```

## Deployment Steps

### Step 1: Pre-Deployment Checks

```bash
# 1. Verify all PDF files exist
python -c "from multi_pdf_positioning.pdf_inventory import verify_all_pdfs; verify_all_pdfs()"

# 2. Verify all YML files exist
python -c "from multi_pdf_positioning.yml_analyzer import verify_all_ymls; verify_all_ymls()"

# 3. Run system tests
python multi_pdf_positioning/test_performance.py
```

### Step 2: Create Backup

**IMPORTANT**: Always create a backup before deployment!

```bash
# Create backup using CLI
multi-pdf-positioning backup

# Or using Python
python -c "from multi_pdf_positioning.backup_manager import BackupManager; from pathlib import Path; bm = BackupManager(Path('coords_multi'), Path('coords_multi_backup')); print(bm.create_backup(list(Path('coords_multi').glob('*.yml'))))"
```

### Step 3: Run Performance Measurement

```bash
# Measure performance with cache enabled
python multi_pdf_positioning/performance_optimizer.py

# Review performance metrics
cat multi_pdf_positioning/performance_metrics_cached.json
```

### Step 4: Run Final Validation

```bash
# Run complete validation
python multi_pdf_positioning/final_validator.py

# Review validation report
cat multi_pdf_positioning/final_validation_report.json
```

### Step 5: Deploy to Production

```bash
# Run complete workflow
multi-pdf-positioning run

# Or with specific options
multi-pdf-positioning run --no-backup --parallel --workers 4
```

### Step 6: Verify Deployment

```bash
# Validate all generated files
multi-pdf-positioning validate --verbose

# Compare with original files
python -c "from multi_pdf_positioning.final_validator import FinalValidator; fv = FinalValidator(); comp = fv.compare_with_original(); print(comp)"
```

## Verification

### Automated Verification

```bash
# Run all verification tests
python multi_pdf_positioning/final_validator.py
```

### Manual Verification

1. **Check Output Files**:
   ```bash
   ls -la output/
   # Should show 48 YML files
   ```

2. **Verify File Count**:
   ```bash
   # Should output: 48
   ls output/*.yml | wc -l
   ```

3. **Check File Sizes**:
   ```bash
   # All files should have reasonable sizes (> 0 bytes)
   du -h output/*.yml
   ```

4. **Validate YML Format**:
   ```bash
   # Test parsing a few files
   python -c "from multi_pdf_positioning.yml_parser import YMLParser; p = YMLParser(); print(len(p.parse_yml('output/seite1_f1.yml')))"
   ```

### Performance Verification

Expected performance metrics:
- **Total time for 48 combinations**: 3-5 minutes (without cache), 2-3 minutes (with cache)
- **Average time per combination**: 3-6 seconds
- **Cache hit rate**: > 50% (if enabled)
- **Success rate**: 100%

## Troubleshooting

### Common Issues

#### Issue 1: PDF Files Not Found

**Symptom**: Error message "PDF not found"

**Solution**:
```bash
# Check PDF directory path
python -c "from multi_pdf_positioning.config import PDF_DIR; print(PDF_DIR); print(PDF_DIR.exists())"

# Update config.py with correct path
```

#### Issue 2: YML Parsing Errors

**Symptom**: "Failed to parse YML"

**Solution**:
```bash
# Validate YML format
python -c "from multi_pdf_positioning.yml_parser import YMLParser; p = YMLParser(); p.parse_yml('coords_multi/seite1_f1.yml')"

# Check for encoding issues
file coords_multi/seite1_f1.yml
```

#### Issue 3: Permission Errors

**Symptom**: "Permission denied" when writing files

**Solution**:
```bash
# Check directory permissions
ls -la output/

# Fix permissions (Linux/macOS)
chmod 755 output/

# Fix permissions (Windows)
# Right-click folder → Properties → Security → Edit permissions
```

#### Issue 4: Memory Issues

**Symptom**: "MemoryError" or system slowdown

**Solution**:
```bash
# Reduce parallel workers
multi-pdf-positioning run --parallel --workers 2

# Or disable parallel processing
multi-pdf-positioning run
```

#### Issue 5: Validation Failures

**Symptom**: Validation errors in final report

**Solution**:
```bash
# Review validation report
cat multi_pdf_positioning/final_validation_report.json

# Check specific file
multi-pdf-positioning validate --firmen 1 --seiten 1 --verbose

# Restore from backup if needed
multi-pdf-positioning restore --backup-id <backup_id> --force
```

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
# Set log level to DEBUG
export LOG_LEVEL=DEBUG

# Run with verbose output
multi-pdf-positioning run --verbose
```

### Getting Help

1. Check log files:
   ```bash
   cat logs/multi_pdf_positioning.log
   ```

2. Run diagnostics:
   ```bash
   python multi_pdf_positioning/test_performance.py
   ```

3. Review documentation:
   - [User Guide](USER_GUIDE.md)
   - [CLI Reference](CLI_REFERENCE.md)
   - [API Documentation](docs/)

## Maintenance

### Regular Maintenance Tasks

#### Daily
- Monitor log files for errors
- Check disk space

#### Weekly
- Review performance metrics
- Validate generated files

#### Monthly
- Clean up old backups
- Update dependencies
- Review and optimize performance

### Backup Management

```bash
# List all backups
multi-pdf-positioning restore

# Create manual backup
multi-pdf-positioning backup

# Clean up old backups (keep last 10)
python -c "from multi_pdf_positioning.backup_manager import BackupManager; from pathlib import Path; bm = BackupManager(Path('coords_multi'), Path('coords_multi_backup')); bm.cleanup_old_backups(keep=10)"
```

### Performance Monitoring

```bash
# Run performance measurement
python multi_pdf_positioning/performance_optimizer.py

# Compare with baseline
# Review performance_metrics_cached.json and compare with previous runs
```

### Updates and Upgrades

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Reinstall package
pip install -e . --force-reinstall

# Verify installation
multi-pdf-positioning --version
```

### Log Rotation

```bash
# Archive old logs
mkdir -p logs/archive
mv logs/multi_pdf_positioning.log logs/archive/multi_pdf_positioning_$(date +%Y%m%d).log

# Or use logrotate (Linux)
# Add to /etc/logrotate.d/multi-pdf-positioning:
# /path/to/logs/multi_pdf_positioning.log {
#     daily
#     rotate 7
#     compress
#     missingok
#     notifempty
# }
```

## Production Checklist

Before deploying to production, verify:

- [ ] All system requirements met
- [ ] Python 3.8+ installed
- [ ] All dependencies installed
- [ ] Configuration file updated with correct paths
- [ ] All 48 PDF files present
- [ ] All 48 YML files present
- [ ] Backup created
- [ ] Performance measurement completed
- [ ] Final validation passed
- [ ] Output directory has write permissions
- [ ] Log directory configured
- [ ] Documentation reviewed
- [ ] Team trained on system usage

## Support

For issues or questions:
- Review this deployment guide
- Check the [User Guide](USER_GUIDE.md)
- Review log files
- Contact system administrator

## Version History

- **v1.0.0** (2025-01-10): Initial release
  - Complete workflow implementation
  - Performance optimization
  - Final validation system
  - Deployment automation

---

**Last Updated**: 2025-01-10
**Document Version**: 1.0.0
