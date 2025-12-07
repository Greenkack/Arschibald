"""
Admin Dashboard Service Demo
Demonstrates usage of the Admin Dashboard Service
"""

import asyncio
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.admin_dashboard_service import AdminDashboardService


# Setup database (using SQLite for demo)
engine = create_engine('sqlite:///demo.db')
SessionLocal = sessionmaker(bind=engine)


def demo_system_health():
    """Demo: Get system health metrics"""
    print("\n" + "="*60)
    print("DEMO: System Health Monitoring")
    print("="*60)
    
    db = SessionLocal()
    service = AdminDashboardService(db)
    
    health = service.get_system_health()
    
    print(f"\nOverall Status: {health['status'].upper()}")
    print(f"Timestamp: {health['timestamp']}")
    print(f"\nCPU:")
    print(f"  Usage: {health['cpu']['usage_percent']}%")
    print(f"  Cores: {health['cpu']['count']}")
    print(f"  Status: {health['cpu']['status']}")
    
    print(f"\nMemory:")
    print(f"  Total: {health['memory']['total_gb']} GB")
    print(f"  Used: {health['memory']['used_gb']} GB")
    print(f"  Available: {health['memory']['available_gb']} GB")
    print(f"  Usage: {health['memory']['usage_percent']}%")
    print(f"  Status: {health['memory']['status']}")
    
    print(f"\nDisk:")
    print(f"  Total: {health['disk']['total_gb']} GB")
    print(f"  Used: {health['disk']['used_gb']} GB")
    print(f"  Free: {health['disk']['free_gb']} GB")
    print(f"  Usage: {health['disk']['usage_percent']}%")
    print(f"  Status: {health['disk']['status']}")
    
    if health['issues']:
        print(f"\n  Issues Detected:")
        for issue in health['issues']:
            print(f"  - {issue}")
    else:
        print(f"\n No issues detected")
    
    db.close()


def demo_database_health():
    """Demo: Get database health"""
    print("\n" + "="*60)
    print("DEMO: Database Health Monitoring")
    print("="*60)
    
    db = SessionLocal()
    service = AdminDashboardService(db)
    
    health = service.get_database_health()
    
    print(f"\nStatus: {health['status'].upper()}")
    print(f"Connection: {health['connection']}")
    print(f"Timestamp: {health['timestamp']}")
    
    if 'tables' in health:
        print(f"\nTable Statistics:")
        for table, count in health['tables'].items():
            print(f"  {table}: {count} records")
        print(f"\nTotal Records: {health['total_records']}")
    
    db.close()


def demo_usage_statistics():
    """Demo: Get usage statistics"""
    print("\n" + "="*60)
    print("DEMO: Usage Statistics")
    print("="*60)
    
    db = SessionLocal()
    service = AdminDashboardService(db)
    
    for period in ['today', 'week', 'month']:
        stats = service.get_usage_statistics(period)
        
        print(f"\n{period.upper()} Statistics:")
        print(f"Period: {stats['start_date']} to {stats['end_date']}")
        
        print(f"\nUsers:")
        print(f"  Total: {stats['users']['total_users']}")
        print(f"  Active: {stats['users']['active_users']}")
        print(f"  New: {stats['users']['new_users']}")
        
        print(f"\nProjects:")
        print(f"  Total: {stats['projects']['total_projects']}")
        print(f"  New: {stats['projects']['new_projects']}")
        print(f"  Completed: {stats['projects']['completed_projects']}")
        
        print(f"\nCalculations: {stats['calculations']['total_calculations']}")
        print(f"PDFs Generated: {stats['pdfs']['total_pdfs']}")
        
        print("-" * 60)
    
    db.close()


def demo_performance_metrics():
    """Demo: Get performance metrics"""
    print("\n" + "="*60)
    print("DEMO: Performance Metrics")
    print("="*60)
    
    db = SessionLocal()
    service = AdminDashboardService(db)
    
    metrics = service.get_performance_metrics()
    
    print(f"\nTimestamp: {metrics['timestamp']}")
    
    print(f"\nResponse Times:")
    rt = metrics['response_times']
    print(f"  Average: {rt['average_ms']}ms")
    print(f"  P50: {rt['p50_ms']}ms")
    print(f"  P95: {rt['p95_ms']}ms")
    print(f"  P99: {rt['p99_ms']}ms")
    print(f"  Max: {rt['max_ms']}ms")
    
    print(f"\nThroughput:")
    tp = metrics['throughput']
    print(f"  Requests/sec: {tp['requests_per_second']}")
    print(f"  Requests/min: {tp['requests_per_minute']}")
    print(f"  Requests/hour: {tp['requests_per_hour']}")
    print(f"  Peak RPS: {tp['peak_rps']} at {tp['peak_time']}")
    
    print(f"\nError Rates:")
    er = metrics['error_rates']
    print(f"  Error Rate: {er['error_rate_percent']}%")
    print(f"  Total Errors: {er['total_errors']}")
    
    print(f"\nCache Performance:")
    cp = metrics['cache_performance']
    print(f"  Hit Rate: {cp['hit_rate_percent']}%")
    print(f"  Miss Rate: {cp['miss_rate_percent']}%")
    print(f"  Cache Size: {cp['cache_size_mb']} MB")
    
    db.close()


def demo_user_activity():
    """Demo: Get user activity overview"""
    print("\n" + "="*60)
    print("DEMO: User Activity Overview")
    print("="*60)
    
    db = SessionLocal()
    service = AdminDashboardService(db)
    
    activity = service.get_user_activity_overview(limit=5)
    
    print(f"\nTimestamp: {activity['timestamp']}")
    
    print(f"\nActive Sessions:")
    sessions = activity['active_sessions']
    print(f"  Total Active: {sessions['total_active']}")
    print(f"  By Role:")
    for role, count in sessions['by_role'].items():
        print(f"    {role}: {count}")
    
    print(f"\nRecent Logins:")
    for login in activity['recent_logins'][:5]:
        print(f"  {login['username']} - {login['login_time']}")
    
    print(f"\nRecent Actions:")
    for action in activity['user_actions'][:5]:
        print(f"  {action['username']}: {action['action']} - {action['timestamp']}")
    
    print(f"\nTop Users by Activity:")
    for user in activity['top_users'][:5]:
        print(f"  {user['username']}: {user['action_count']} actions")
    
    db.close()


def demo_system_alerts():
    """Demo: Get system alerts"""
    print("\n" + "="*60)
    print("DEMO: System Alerts")
    print("="*60)
    
    db = SessionLocal()
    service = AdminDashboardService(db)
    
    alerts = service.get_system_alerts()
    
    if alerts:
        print(f"\n  {len(alerts)} Active Alert(s):")
        for alert in alerts:
            severity_icon = {
                'info': 'ℹ',
                'warning': '',
                'critical': ''
            }.get(alert['severity'], '')
            
            print(f"\n{severity_icon} [{alert['severity'].upper()}] {alert['title']}")
            print(f"   Type: {alert['type']}")
            print(f"   Message: {alert['message']}")
            print(f"   Time: {alert['timestamp']}")
    else:
        print(f"\n No active alerts - System is healthy!")
    
    db.close()


def demo_dashboard_summary():
    """Demo: Get complete dashboard summary"""
    print("\n" + "="*60)
    print("DEMO: Complete Dashboard Summary")
    print("="*60)
    
    db = SessionLocal()
    service = AdminDashboardService(db)
    
    summary = service.get_dashboard_summary()
    
    print(f"\nTimestamp: {summary['timestamp']}")
    
    print(f"\n System Health: {summary['system_health']['status'].upper()}")
    print(f" Database: {summary['database_health']['status'].upper()}")
    
    stats = summary['usage_statistics']
    print(f"\n Active Users: {stats['users']['active_users']}")
    print(f" New Projects: {stats['projects']['new_projects']}")
    print(f" Calculations: {stats['calculations']['total_calculations']}")
    print(f" PDFs Generated: {stats['pdfs']['total_pdfs']}")
    
    metrics = summary['performance_metrics']
    print(f"\n Avg Response Time: {metrics['response_times']['average_ms']}ms")
    print(f" Throughput: {metrics['throughput']['requests_per_second']} req/s")
    print(f" Error Rate: {metrics['error_rates']['error_rate_percent']}%")
    
    alerts = summary['active_alerts']
    if alerts:
        print(f"\n  {len(alerts)} Active Alert(s)")
    else:
        print(f"\n No Active Alerts")
    
    db.close()


def demo_historical_metrics():
    """Demo: Get historical metrics"""
    print("\n" + "="*60)
    print("DEMO: Historical Metrics")
    print("="*60)
    
    db = SessionLocal()
    service = AdminDashboardService(db)
    
    # System health history
    print(f"\nSystem Health History (Week):")
    health_history = service.get_historical_metrics('system_health', 'week')
    print(f"Period: {health_history['period']['start']} to {health_history['period']['end']}")
    print(f"Data points: {len(health_history['data'])}")
    
    # Usage history
    print(f"\nUsage History (Week):")
    usage_history = service.get_historical_metrics('usage', 'week')
    print(f"Period: {usage_history['period']['start']} to {usage_history['period']['end']}")
    print(f"Data points: {len(usage_history['data'])}")
    
    # Performance history
    print(f"\nPerformance History (Week):")
    perf_history = service.get_historical_metrics('performance', 'week')
    print(f"Period: {perf_history['period']['start']} to {perf_history['period']['end']}")
    print(f"Data points: {len(perf_history['data'])}")
    
    db.close()


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("ADMIN DASHBOARD SERVICE - COMPREHENSIVE DEMO")
    print("="*60)
    print(f"Started at: {datetime.now()}")
    
    try:
        # Run all demos
        demo_system_health()
        demo_database_health()
        demo_usage_statistics()
        demo_performance_metrics()
        demo_user_activity()
        demo_system_alerts()
        demo_dashboard_summary()
        demo_historical_metrics()
        
        print("\n" + "="*60)
        print(" ALL DEMOS COMPLETED SUCCESSFULLY")
        print("="*60)
        
    except Exception as e:
        print(f"\n Error running demos: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
