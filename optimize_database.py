#!/usr/bin/env python3
"""
Database Optimization Script for Enhanced Pricing System
Run this script to optimize the database for better pricing performance.
"""

from pricing.performance_monitor import run_performance_analysis
from pricing.database_optimization import DatabaseOptimizer
import os
import sys
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    """Main optimization routine"""
    print("=" * 60)
    print("DATABASE OPTIMIZATION FOR ENHANCED PRICING SYSTEM")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check if database exists
    db_path = os.path.join('data', 'app_data.db')
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("Please ensure the application database exists before running optimization.")
        return False

    print(f"✓ Database found: {db_path}")
    print(f"  Size: {round(os.path.getsize(db_path) / (1024 * 1024), 2)} MB")
    print()

    # Initialize optimizer
    print("Initializing database optimizer...")
    optimizer = DatabaseOptimizer(db_path)

    # Get initial statistics
    print("Collecting initial database statistics...")
    initial_stats = optimizer.get_database_statistics()

    print("Initial Database Statistics:")
    print(f"  Products: {initial_stats.get('products_count', 'N/A')}")
    print(
        f"  Pricing Rules: {
            initial_stats.get(
                'pricing_rules_count',
                'N/A')}")
    print(
        f"  Pricing History: {
            initial_stats.get(
                'pricing_history_count',
                'N/A')}")
    print(
        f"  Product Indexes: {
            initial_stats.get(
                'product_indexes_count',
                'N/A')}")
    print(
        f"  Products with Calculate Per: {
            initial_stats.get(
                'products_with_calc_per',
                'N/A')}")
    print(
        f"  Products with Purchase Price: {
            initial_stats.get(
                'products_with_purchase_price',
                'N/A')}")
    print(
        f"  Products with Margin Config: {
            initial_stats.get(
                'products_with_margin_config',
                'N/A')}")
    print()

    # Create indexes
    print("Creating pricing-related indexes...")
    index_success = optimizer.create_pricing_indexes()

    if index_success:
        print("✓ Indexes created successfully")
    else:
        print("❌ Some indexes could not be created")
    print()

    # Run database maintenance
    print("Running database maintenance...")

    print("  Running ANALYZE to update query planner statistics...")
    analyze_success = optimizer.analyze_database()
    if analyze_success:
        print("  ✓ ANALYZE completed")
    else:
        print("  ❌ ANALYZE failed")

    print("  Running VACUUM to optimize storage...")
    vacuum_success = optimizer.vacuum_database()
    if vacuum_success:
        print("  ✓ VACUUM completed")
    else:
        print("  ❌ VACUUM failed")
    print()

    # Get final statistics
    print("Collecting final database statistics...")
    final_stats = optimizer.get_database_statistics()

    print("Final Database Statistics:")
    print(f"  Products: {final_stats.get('products_count', 'N/A')}")
    print(
        f"  Product Indexes: {
            final_stats.get(
                'product_indexes_count',
                'N/A')}")
    print(f"  Database Size: {final_stats.get('database_size_mb', 'N/A')} MB")
    print(f"  Cache Size: {final_stats.get('cache_size', 'N/A')}")
    print(f"  Journal Mode: {final_stats.get('journal_mode', 'N/A')}")
    print()

    # Show improvement
    initial_indexes = initial_stats.get('product_indexes_count', 0)
    final_indexes = final_stats.get('product_indexes_count', 0)

    if final_indexes > initial_indexes:
        print(
            f"✓ Added {
                final_indexes -
                initial_indexes} new indexes for better performance")

    # Run performance benchmark
    print("Running performance benchmark...")
    try:
        results = run_performance_analysis()
        print("✓ Performance benchmark completed")
        print("  Check performance_results_*.json and performance_metrics_*.json for detailed results")
    except Exception as e:
        print(f"❌ Performance benchmark failed: {e}")

    print()

    # Cleanup
    optimizer.close()

    print("=" * 60)
    print("DATABASE OPTIMIZATION COMPLETED")
    print("=" * 60)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Summary
    print("\nSUMMARY:")
    print(f"  Indexes created: {'✓' if index_success else '❌'}")
    print(f"  Database analyzed: {'✓' if analyze_success else '❌'}")
    print(f"  Database vacuumed: {'✓' if vacuum_success else '❌'}")
    print(f"  Performance benchmark: {'✓' if 'results' in locals() else '❌'}")

    print("\nRECOMMENDations:")
    print("  - Run this optimization script periodically (monthly)")
    print("  - Monitor query performance using the performance_monitor module")
    print("  - Consider adding more specific indexes if you notice slow queries")
    print("  - Use connection pooling for high-load scenarios")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
