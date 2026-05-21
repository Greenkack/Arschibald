#!/usr/bin/env python
"""
Simple test runner for 2D conversion tests.
Bypasses pytest configuration issues.
"""

import sys
import subprocess

# Run pytest without config
result = subprocess.run(
    [sys.executable, '-m', 'pytest', 'tests/test_2d_conversion.py', '-v', '-s', '--override-ini=addopts='],
    capture_output=False
)

sys.exit(result.returncode)
