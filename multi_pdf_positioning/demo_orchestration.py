"""
Demo script for Multi-PDF Positioning System Orchestration

This script demonstrates the main orchestration features:
1. Main workflow
2. Batch processing
3. CLI usage examples

Run this script to see the orchestration system in action.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from multi_pdf_positioning.main_workflow import MainWorkflow, WorkflowSummary
from multi_pdf_positioning.batch_processor import BatchProcessor, BatchSummary
fr