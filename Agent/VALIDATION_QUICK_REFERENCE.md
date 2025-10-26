# KAI Agent Validation - Quick Reference

## One-Command Validation

```bash
cd Agent && python run_final_validation.py
```

## Individual Test Suites

```bash
# Task 19.1: End-to-End Testing
python Agent/test_end_to_end.py

# Task 19.2: Performance Testing
python Agent/test_performance.py

# Task 19.3: Security Audit
python Agent/test_security_audit.py
```

## Using pytest

```bash
# All tests with verbose output
pytest Agent/test_end_to_end.py Agent/test_performance.py Agent/test_security_audit.py -v

# Specific test class
pytest Agent/test_security_audit.py::TestDockerIsolation -v

# With print statements visible
pytest Agent/test_performance.py -v -s
```

## Expected Results

### ✅ Success

```
==============================================================================
✓ ALL VALIDATION TESTS PASSED
==============================================================================

Security Audit Summary:
  ✓ Docker isolation verified
  ✓ Path validation working
  ✓ API key security confirmed
  ✓ Input sanitization active
```

### ⚠️ Skipped Tests (Normal)

```
SKIPPED [1] test_performance.py:45: No knowledge base documents available
SKIPPED [1] test_security_audit.py:78: Docker not available
```

These are expected when Docker or knowledge base documents are not available.

## Generated Reports

- `Agent/final_validation_report.json` - Overall validation results
- `Agent/performance_report.json` - Performance metrics

## Test Coverage

| Suite | Tests | Duration | Coverage |
|-------|-------|----------|----------|
| End-to-End | ~25 | 30-60s | All functional requirements |
| Performance | ~15 | 60-120s | All performance NFRs |
| Security | ~25 | 30-60s | All security NFRs |

## Prerequisites

### Required
- Python 3.11+
- pytest (`pip install pytest`)
- psutil (`pip install psutil`)
- Agent dependencies (`pip install -r Agent/requirements.txt`)

### Optional
- Docker (for Docker tests)
- PDF documents in `Agent/knowledge_base/` (for knowledge base tests)
- API keys in `.env` (for integration tests)

## Troubleshooting

### Import Errors
```bash
# Run from project root
python Agent/test_end_to_end.py
```

### Docker Tests Fail
```bash
# Check Docker is running
docker ps

# Build sandbox image
python Agent/build_sandbox.py
```

### Knowledge Base Tests Skip
```bash
# Add PDFs to knowledge base
cp your_pdfs/*.pdf Agent/knowledge_base/

# Setup knowledge base
python Agent/setup_knowledge_base.py
```

## Next Steps After Validation

1. ✅ Review `final_validation_report.json`
2. ✅ Follow `DEPLOYMENT_GUIDE.md`
3. ✅ Configure `.env` with API keys
4. ✅ Build Docker sandbox
5. ✅ Setup knowledge base
6. ✅ Integrate with main app

## Documentation

- `VALIDATION_GUIDE.md` - Complete validation guide
- `TROUBLESHOOTING.md` - Common issues
- `DEPLOYMENT_GUIDE.md` - Deployment instructions
- `README.md` - General documentation

## Support

For detailed information, see `Agent/VALIDATION_GUIDE.md`
