# Multi-PDF Positioning System - Quick Start Guide

## Installation (5 minutes)

```bash
# 1. Clone or download the repository
cd multi_pdf_positioning

# 2. Run automated installation
python install.py

# 3. Verify installation
multi-pdf-positioning --version
```

## Configuration (2 minutes)

Edit `config.py` with your paths:

```python
PDF_DIR = Path("path/to/pdf_templates_static/multi")
YML_DIR = Path("path/to/coords_multi")
OUTPUT_DIR = Path("path/to/output")
```

## Quick Test (1 minute)

```bash
# Test with one combination
multi-pdf-positioning run --firmen 1 --seiten 1
```

## Full Run (3-5 minutes)

```bash
# Process all 48 combinations
multi-pdf-positioning run
```

## Common Commands

```bash
# Analyze PDFs
multi-pdf-positioning analyze

# Generate optimized YML files
multi-pdf-positioning generate

# Validate generated files
multi-pdf-positioning validate

# Create backup
multi-pdf-positioning backup

# Restore from backup
multi-pdf-positioning restore --backup-id <id> --force

# Get help
multi-pdf-positioning --help
```

## Performance Optimization

```bash
# Enable parallel processing (faster)
multi-pdf-positioning run --parallel --workers 4

# Measure performance
python performance_optimizer.py
```

## Validation

```bash
# Run final validation
python final_validator.py

# Validate specific files
multi-pdf-positioning validate --firmen 1,2 --seiten 1,2,3 --verbose
```

## Troubleshooting

### Issue: "PDF not found"
```bash
# Check PDF directory
python -c "from multi_pdf_positioning.config import PDF_DIR; print(PDF_DIR); print(PDF_DIR.exists())"
```

### Issue: "Permission denied"
```bash
# Check permissions
ls -la output/
chmod 755 output/  # Linux/macOS
```

### Issue: Slow performance
```bash
# Use parallel processing
multi-pdf-positioning run --parallel --workers 4

# Or enable caching
python -c "from multi_pdf_positioning.performance_optimizer import measure_performance; measure_performance(enable_cache=True)"
```

## Documentation

- **Full Guide**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **System Requirements**: [SYSTEM_REQUIREMENTS.md](SYSTEM_REQUIREMENTS.md)
- **User Guide**: [USER_GUIDE.md](USER_GUIDE.md)
- **CLI Reference**: [CLI_REFERENCE.md](CLI_REFERENCE.md)

## Support

For issues:
1. Check log files: `logs/multi_pdf_positioning.log`
2. Review documentation
3. Run diagnostics: `python test_performance.py`

---

**Total Time**: ~10-15 minutes from installation to first run
**Processing Time**: 2-3 minutes for all 48 combinations (with cache and parallel processing)
