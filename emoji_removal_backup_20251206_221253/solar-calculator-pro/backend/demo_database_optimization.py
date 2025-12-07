"""
Database Optimization Demo

Demonstrates all database optimization features:
- Query analysis and optimization
- Index management
- Partitioning analysis
- Data archiving
- Vacuum and analyze operations
- Performance monitoring

Requirements: 8.4
"""

from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime
from datetime import datetime, timedelta
from services.database_optimization_service import DatabaseOptimizationService
import json


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_json(data: dict, indent: int = 2):
    """Print JSON data"""
    print(json.dumps(data, indent=indent, default=str))


def create_demo_database():
    """Create demo database with sample data"""
    print_section("Creating Demo Database")
    
    engine = create_engine("sqlite:///demo_optimization.db")
    metadata = MetaData()
    
    # Create tables
    users = Table(
        'users',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(100)),
        Column('email', String(100)),
        Column('created_at', DateTime)
    )
    
    orders = Table(
        'orders',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('user_id', Integer),
        Column('amount', Integer),
        Column('order_date', DateTime)
    )
    
    products = Table(
        'products',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(200)),
        Column('price', Integer),
        Column('category', String(50)),
        Column('created_at', DateTime)
    )
    
    metadata.create_all(engine)
    
    # Insert sample data
    with engine.connect() as conn:
        print("Inserting 1000 users...")
        for i in range(1000):
            conn.execute(
                text("INSERT INTO users (name, email, created_at) VALUES (:name, :email, :created_at)"),
                {
                    "name": f"User {i}",
                    "email": f"user{i}@example.com",
                    "created_at": datetime.now() - timedelta(days=i % 730)  # Up to 2 years old
                }
            )
        
        print("Inserting 5000 orders...")
        for i in range(5000):
            conn.execute(
                text("INSERT INTO orders (user_id, amount, order_date) VALUES (:user_id, :amount, :order_date)"),
                {
                    "user_id": i % 1000,
                    "amount": 100 + (i % 500),
                    "order_date": datetime.now() - timedelta(days=i % 730)
                }
            )
        
        print("Inserting 500 products...")
        categories = ["Electronics", "Clothing", "Food", "Books", "Toys"]
        for i in range(500):
            conn.execute(
                text("INSERT INTO products (name, price, category, created_at) VALUES (:name, :price, :category, :created_at)"),
                {
                    "name": f"Product {i}",
                    "price": 10 + (i % 100),
                    "category": categories[i % len(categories)],
                    "created_at": datetime.now() - timedelta(days=i % 365)
                }
            )
        
        conn.commit()
    
    print("\n✓ Demo database created successfully!")
    print(f"  - 1000 users")
    print(f"  - 5000 orders")
    print(f"  - 500 products")
    
    return engine


def demo_query_optimization(service: DatabaseOptimizationService):
    """Demonstrate query optimization features"""
    print_section("Query Optimization")
    
    # Analyze simple query
    print("1. Analyzing simple SELECT query:")
    query1 = "SELECT * FROM users WHERE email = 'user100@example.com'"
    result1 = service.analyze_query(query1)
    print(f"   Query: {query1}")
    print(f"   Execution time: {result1['execution_time_ms']}ms")
    print(f"   Issues found: {len(result1['issues'])}")
    if result1['issues']:
        for issue in result1['issues']:
            print(f"     - {issue}")
    if result1['suggestions']:
        print(f"   Suggestions:")
        for suggestion in result1['suggestions']:
            print(f"     - {suggestion}")
    
    # Analyze JOIN query
    print("\n2. Analyzing JOIN query:")
    query2 = """
        SELECT u.name, COUNT(o.id) as order_count, SUM(o.amount) as total_amount
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        GROUP BY u.id
        HAVING order_count > 5
    """
    result2 = service.analyze_query(query2)
    print(f"   Execution time: {result2['execution_time_ms']}ms")
    print(f"   Issues found: {len(result2['issues'])}")
    if result2['suggestions']:
        print(f"   Suggestions:")
        for suggestion in result2['suggestions']:
            print(f"     - {suggestion}")


def demo_index_management(service: DatabaseOptimizationService):
    """Demonstrate index management features"""
    print_section("Index Management")
    
    # Get current indexes
    print("1. Current indexes:")
    indexes = service.get_indexes()
    for table, table_indexes in indexes.items():
        print(f"\n   Table: {table}")
        if table_indexes:
            for idx in table_indexes:
                print(f"     - {idx['name']}: {', '.join(idx['columns'])} {'(UNIQUE)' if idx['unique'] else ''}")
        else:
            print(f"     No indexes")
    
    # Analyze index usage
    print("\n2. Analyzing index usage for 'users' table:")
    analysis = service.analyze_index_usage("users")
    print(f"   Row count: {analysis['row_count']}")
    print(f"   Indexes: {len(analysis['indexes'])}")
    if analysis['recommendations']:
        print(f"   Recommendations:")
        for rec in analysis['recommendations']:
            print(f"     - {rec}")
    
    # Create new indexes
    print("\n3. Creating new indexes:")
    
    # Email index
    result1 = service.create_index("users", ["email"], unique=True)
    if result1['success']:
        print(f"   ✓ Created index: {result1['index_name']}")
    
    # User ID index on orders
    result2 = service.create_index("orders", ["user_id"])
    if result2['success']:
        print(f"   ✓ Created index: {result2['index_name']}")
    
    # Category index on products
    result3 = service.create_index("products", ["category"])
    if result3['success']:
        print(f"   ✓ Created index: {result3['index_name']}")
    
    # Composite index
    result4 = service.create_index("orders", ["user_id", "order_date"])
    if result4['success']:
        print(f"   ✓ Created index: {result4['index_name']}")


def demo_partitioning_analysis(service: DatabaseOptimizationService):
    """Demonstrate partitioning analysis"""
    print_section("Table Partitioning Analysis")
    
    candidates = service.analyze_partitioning_candidates()
    
    if candidates:
        print(f"Found {len(candidates)} table(s) that could benefit from partitioning:\n")
        for candidate in candidates:
            print(f"Table: {candidate['table_name']}")
            print(f"  Row count: {candidate['row_count']:,}")
            print(f"  Partition columns: {', '.join(candidate['partition_columns'])}")
            print(f"  Strategy: {candidate['strategy']}")
            print(f"  Reason: {candidate['reason']}\n")
    else:
        print("No partitioning candidates found (tables may be too small)")


def demo_data_archiving(service: DatabaseOptimizationService):
    """Demonstrate data archiving features"""
    print_section("Data Archiving")
    
    # Find archiving candidates
    print("1. Finding archiving candidates (data older than 365 days):")
    candidates = service.analyze_archiving_candidates(age_threshold_days=365)
    
    if candidates:
        print(f"\n   Found {len(candidates)} table(s) with old data:\n")
        for candidate in candidates:
            print(f"   Table: {candidate['table_name']}")
            print(f"     Date column: {candidate['date_column']}")
            print(f"     Old records: {candidate['old_records_count']:,}")
            print(f"     Threshold: {candidate['threshold_date']}")
            print(f"     {candidate['recommendation']}\n")
        
        # Archive data from first candidate
        if candidates:
            first_candidate = candidates[0]
            print(f"2. Archiving old data from '{first_candidate['table_name']}':")
            
            threshold = datetime.fromisoformat(first_candidate['threshold_date'])
            result = service.archive_old_data(
                table_name=first_candidate['table_name'],
                date_column=first_candidate['date_column'],
                threshold_date=threshold
            )
            
            if result['success']:
                print(f"   ✓ Archived {result['archived_count']} records")
                print(f"   ✓ Archive table: {result['archive_table']}")
    else:
        print("   No archiving candidates found")


def demo_maintenance_operations(service: DatabaseOptimizationService):
    """Demonstrate maintenance operations"""
    print_section("Maintenance Operations")
    
    # Run ANALYZE
    print("1. Running ANALYZE to update statistics:")
    analyze_result = service.analyze_tables()
    if analyze_result['success']:
        print(f"   ✓ ANALYZE completed in {analyze_result['duration_seconds']}s")
    
    # Run VACUUM
    print("\n2. Running VACUUM to reclaim space:")
    vacuum_result = service.vacuum_database()
    if vacuum_result['success']:
        print(f"   ✓ VACUUM completed in {vacuum_result['duration_seconds']}s")
        print(f"   ✓ Space freed: {vacuum_result['space_freed_mb']} MB")
        print(f"   ✓ Size before: {vacuum_result['size_before_bytes'] / (1024*1024):.2f} MB")
        print(f"   ✓ Size after: {vacuum_result['size_after_bytes'] / (1024*1024):.2f} MB")
    
    # Configure maintenance schedule
    print("\n3. Configuring automatic maintenance schedule:")
    schedule = service.schedule_maintenance(
        vacuum_enabled=True,
        analyze_enabled=True,
        vacuum_schedule="weekly",
        analyze_schedule="daily"
    )
    print(f"   ✓ VACUUM: {schedule['vacuum']['schedule']} (enabled: {schedule['vacuum']['enabled']})")
    print(f"   ✓ ANALYZE: {schedule['analyze']['schedule']} (enabled: {schedule['analyze']['enabled']})")


def demo_performance_monitoring(service: DatabaseOptimizationService):
    """Demonstrate performance monitoring"""
    print_section("Performance Monitoring")
    
    # Get performance metrics
    print("1. Current performance metrics:")
    metrics = service.get_performance_metrics()
    
    print(f"\n   Database size: {metrics['database_size_mb']} MB")
    print(f"   Total tables: {metrics['table_count']}")
    print(f"   Total rows: {metrics['total_rows']:,}")
    print(f"   Total indexes: {metrics['total_indexes']}")
    
    print(f"\n   Table statistics:")
    for stat in metrics['table_statistics']:
        print(f"     - {stat['table_name']}: {stat['row_count']:,} rows")


def demo_optimization_report(service: DatabaseOptimizationService):
    """Demonstrate comprehensive optimization report"""
    print_section("Comprehensive Optimization Report")
    
    print("Generating complete optimization analysis...\n")
    report = service.get_optimization_report()
    
    # Performance metrics
    print("1. Performance Metrics:")
    metrics = report['performance_metrics']
    print(f"   Database size: {metrics['database_size_mb']} MB")
    print(f"   Total tables: {metrics['table_count']}")
    print(f"   Total rows: {metrics['total_rows']:,}")
    print(f"   Total indexes: {metrics['total_indexes']}")
    
    # Index analysis
    print("\n2. Index Analysis:")
    for table, analysis in report['index_analysis'].items():
        print(f"\n   Table: {table}")
        print(f"     Row count: {analysis['row_count']:,}")
        print(f"     Indexes: {len(analysis['indexes'])}")
        if analysis['recommendations']:
            print(f"     Recommendations:")
            for rec in analysis['recommendations']:
                print(f"       - {rec}")
    
    # Partitioning candidates
    if report['partitioning_candidates']:
        print(f"\n3. Partitioning Candidates: {len(report['partitioning_candidates'])}")
        for candidate in report['partitioning_candidates']:
            print(f"   - {candidate['table_name']}: {candidate['reason']}")
    
    # Archiving candidates
    if report['archiving_candidates']:
        print(f"\n4. Archiving Candidates: {len(report['archiving_candidates'])}")
        total_archivable = sum(c['old_records_count'] for c in report['archiving_candidates'])
        print(f"   Total archivable records: {total_archivable:,}")
    
    # Overall recommendations
    if report['recommendations']:
        print(f"\n5. Overall Recommendations:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"   {i}. {rec}")


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("  DATABASE OPTIMIZATION DEMO")
    print("  Comprehensive Database Performance Management")
    print("=" * 80)
    
    # Create demo database
    engine = create_demo_database()
    service = DatabaseOptimizationService(engine)
    
    # Run demos
    demo_query_optimization(service)
    demo_index_management(service)
    demo_partitioning_analysis(service)
    demo_data_archiving(service)
    demo_maintenance_operations(service)
    demo_performance_monitoring(service)
    demo_optimization_report(service)
    
    print_section("Demo Complete")
    print("All database optimization features demonstrated successfully!")
    print("\nKey Features:")
    print("  ✓ Query analysis and optimization")
    print("  ✓ Index management and recommendations")
    print("  ✓ Table partitioning analysis")
    print("  ✓ Data archiving for old records")
    print("  ✓ VACUUM and ANALYZE operations")
    print("  ✓ Performance monitoring and metrics")
    print("  ✓ Comprehensive optimization reports")
    print("\nDemo database saved as: demo_optimization.db")


if __name__ == "__main__":
    main()
