"""
End-to-End Test für das Monitoring-System

Testet alle integrierten Module und überprüft Tracing-Funktionalität.
"""

import sys
import time
from pathlib import Path

# Initialisiere Monitoring
from monitoring_startup import initialize_monitoring

def test_calculations():
    """Test calculation module tracing."""
    print("\n[CHART] Testing Calculations Module...")
    try:
        from calculations import calculate_enhanced_pricing
        from app_evaluation import track_success, track_error
        
        # Beispiel-Daten
        start_time = time.time()
        result = calculate_enhanced_pricing(
            module_power_wp=400,
            module_quantity=20,
            battery_kwh=10.0,
            inverter_kw=8.0,
            selected_profile="haushalt"
        )
        
        execution_time = time.time() - start_time
        print(f"  [OK] Calculation completed in {execution_time:.3f}s")
        print(f"  [MONEY] Total price: {result.get('total_price', 0):.2f}€")
        
        return True
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        return False


def test_database():
    """Test database module tracing."""
    print("\n🗄️  Testing Database Module...")
    try:
        from database import get_db_connection
        
        start_time = time.time()
        conn = get_db_connection()
        execution_time = time.time() - start_time
        
        if conn:
            print(f"  [OK] Database connection established in {execution_time:.3f}s")
            conn.close()
            return True
        else:
            print("  [WARNING]  Database connection returned None")
            return False
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        return False


def test_crm():
    """Test CRM module tracing."""
    print("\n👥 Testing CRM Module...")
    try:
        from crm import save_customer, load_all_customers
        from database import get_db_connection
        
        conn = get_db_connection()
        if not conn:
            print("  [WARNING]  No database connection")
            return False
        
        # Test load customers
        start_time = time.time()
        customers = load_all_customers(conn)
        execution_time = time.time() - start_time
        
        print(f"  [OK] Loaded {len(customers)} customers in {execution_time:.3f}s")
        conn.close()
        return True
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        return False


def test_evaluation_system():
    """Test evaluation system."""
    print("\n[STATS] Testing Evaluation System...")
    try:
        from app_evaluation import evaluation_system, evaluate_performance
        
        # Generate some test metrics
        evaluate_performance("test.operation_1", 0.5)
        evaluate_performance("test.operation_2", 0.8)
        evaluate_performance("test.operation_3", 0.3)
        
        # Generate report
        report = evaluation_system.generate_report()
        
        print(f"  [OK] Report generated:")
        print(f"     Session: {report['session_id']}")
        print(f"     Total operations: {report['summary']['errors']['total_operations']}")
        print(f"     Success rate: {report['summary']['errors']['success_rate']:.2%}")
        
        # Health status
        health = evaluation_system.get_health_status()
        print(f"  🏥 Health Status: {health['status']}")
        
        return True
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        return False


def test_tracing_export():
    """Test tracing data export to AI Toolkit."""
    print("\n[SEARCH] Testing Tracing Export...")
    try:
        from app_tracing import app_tracer
        
        # Create test span
        with app_tracer.create_span("test.e2e_test", {"test_id": "end_to_end"}) as span:
            time.sleep(0.1)  # Simulate work
            span.set_attribute("test_result", "success")
        
        print("  [OK] Test span created and exported")
        print("  📡 Check AI Toolkit at: http://localhost:4318/v1/traces")
        print("  [IDEA] In VSCode: Ctrl+Shift+P → 'AI Toolkit: Open Tracing'")
        
        return True
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        return False


def main():
    """Run all end-to-end tests."""
    print("="*80)
    print("END-TO-END MONITORING TEST")
    print("="*80)
    
    # Initialize monitoring
    print("\n[LAUNCH] Initializing monitoring system...")
    status = initialize_monitoring(auto_start=False)
    
    if not status["overall"]:
        print("\n[ERROR] Monitoring system not ready - aborting tests")
        return 1
    
    # Run tests
    tests = [
        ("Calculations", test_calculations),
        ("Database", test_database),
        ("CRM", test_crm),
        ("Evaluation System", test_evaluation_system),
        ("Tracing Export", test_tracing_export),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n[ERROR] Test '{name}' crashed: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for name, result in results.items():
        status_icon = "[OK]" if result else "[ERROR]"
        print(f"{status_icon} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        print("\n[CHART] Next steps:")
        print("  1. Open AI Toolkit in VSCode: Ctrl+Shift+P → 'AI Toolkit: Open Tracing'")
        print("  2. Run Streamlit app: streamlit run gui.py")
        print("  3. Check monitoring dashboard in app sidebar")
        print("  4. Generate evaluation report: evaluation_system.generate_report()")
        return 0
    else:
        print(f"\n[WARNING]  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
