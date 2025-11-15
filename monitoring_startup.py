"""
Application Startup Monitor

Initializes and verifies all monitoring components at application startup.
"""

import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def verify_monitoring_setup() -> dict:
    """
    Verify all monitoring components are properly set up.
    
    Returns:
        Status dictionary with component availability
    """
    status = {
        "tracing": False,
        "evaluation": False,
        "diagnostics": False,
        "health_monitor": False,
        "dashboard": False,
        "overall": False
    }
    
    # Check tracing
    try:
        from app_tracing import app_tracer, initialize_tracing
        status["tracing"] = True
        logger.info("Tracing module available")
    except ImportError as e:
        logger.warning(f"Tracing not available: {e}")
    
    # Check evaluation
    try:
        from app_evaluation import evaluation_system
        status["evaluation"] = True
        logger.info("Evaluation module available")
    except ImportError as e:
        logger.warning(f"Evaluation not available: {e}")
    
    # Check diagnostics
    try:
        from app_diagnostics import ApplicationScanner
        status["diagnostics"] = True
        logger.info("Diagnostics module available")
    except ImportError as e:
        logger.warning(f"Diagnostics not available: {e}")
    
    # Check health monitor
    try:
        from app_health_monitor import health_monitor
        status["health_monitor"] = True
        logger.info("Health monitor available")
    except ImportError as e:
        logger.warning(f"Health monitor not available: {e}")
    
    # Check dashboard
    try:
        from monitoring_dashboard import render_monitoring_dashboard
        status["dashboard"] = True
        logger.info("Monitoring dashboard available")
    except ImportError as e:
        logger.warning(f"Dashboard not available: {e}")
    
    # Overall status
    status["overall"] = all([
        status["tracing"],
        status["evaluation"],
        status["dashboard"]
    ])
    
    return status


def initialize_monitoring(auto_start: bool = False):
    """
    Initialize monitoring system.
    
    Args:
        auto_start: Start continuous monitoring automatically
    """
    logger.info("="*80)
    logger.info("MONITORING SYSTEM INITIALIZATION")
    logger.info("="*80)
    
    status = verify_monitoring_setup()
    
    if not status["overall"]:
        logger.error("Monitoring system incomplete - check installation")
        logger.info("\nTo install missing components:")
        logger.info("  pip install opentelemetry-api opentelemetry-sdk")
        logger.info("  pip install opentelemetry-exporter-otlp-proto-http")
        logger.info("  pip install opentelemetry-instrumentation-requests")
        logger.info("  pip install opentelemetry-instrumentation-sqlite3")
        logger.info("  pip install psutil")
        return status
    
    # Initialize tracing
    if status["tracing"]:
        try:
            from app_tracing import initialize_tracing
            import atexit
            from app_tracing import shutdown_tracing
            
            initialize_tracing()
            atexit.register(shutdown_tracing)
            logger.info("Tracing initialized")
        except Exception as e:
            logger.error(f"Failed to initialize tracing: {e}")
    
    # Start health monitoring if requested
    if auto_start and status["health_monitor"]:
        try:
            from app_health_monitor import start_health_monitoring
            start_health_monitoring(interval=60)
            logger.info("Health monitoring started (60s interval)")
        except Exception as e:
            logger.error(f"Failed to start health monitoring: {e}")
    
    logger.info("="*80)
    logger.info("MONITORING READY")
    logger.info("="*80)
    logger.info("\nAccess dashboard:")
    logger.info("  Streamlit: Sidebar → Monitoring")
    logger.info("\nManual commands:")
    logger.info("  Code Analysis: python app_diagnostics.py")
    logger.info("  Health Report: python app_health_monitor.py --report")
    logger.info("  Auto-Fix: python fix_all_issues.py --live")
    logger.info("="*80 + "\n")
    
    return status


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize Application Monitoring')
    parser.add_argument('--auto-start', action='store_true', help='Start continuous monitoring')
    parser.add_argument('--verify-only', action='store_true', help='Only verify setup without initializing')
    
    args = parser.parse_args()
    
    if args.verify_only:
        status = verify_monitoring_setup()
        print(f"\nMonitoring Status: {'READY' if status['overall'] else 'INCOMPLETE'}")
        sys.exit(0 if status['overall'] else 1)
    else:
        status = initialize_monitoring(auto_start=args.auto_start)
        sys.exit(0 if status['overall'] else 1)
