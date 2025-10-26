#!/usr/bin/env python3
"""
Tests for Database Optimization Module
Tests performance improvements, connection pooling, and query optimization.
"""

from pricing.database_optimization import (
    DatabaseConnectionPool,
    DatabaseOptimizer,
    PricingQueryBuilder,
)
import os
import sqlite3

# Import the modules to test
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDatabaseConnectionPool:
    """Test the database connection pool functionality"""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        # Create a simple test database
        conn = sqlite3.connect(path)
        conn.execute("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                model_name TEXT,
                category TEXT,
                calculate_per TEXT,
                purchase_price_net REAL,
                margin_type TEXT,
                margin_value REAL
            )
        """)

        # Insert test data
        test_products = [
            (1, 'Test Module 1', 'Modul', 'Stück', 100.0, 'percentage', 25.0),
            (2, 'Test Module 2', 'Modul', 'Stück', 150.0, 'percentage', 30.0),
            (3, 'Test Cable 1', 'Kabel', 'Meter', 5.0, 'fixed', 2.0),
            (4, 'Test Service 1', 'Service', 'pauschal', 500.0, 'percentage', 20.0),
        ]

        conn.executemany(
            "INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?)",
            test_products
        )
        conn.commit()
        conn.close()

        yield path

        # Cleanup
        if os.path.exists(path):
            os.unlink(path)

    def test_connection_pool_creation(self, temp_db):
        """Test that connection pool can be created successfully"""
        pool = DatabaseConnectionPool(temp_db, pool_size=5)
        assert pool.pool_size == 5
        assert pool.db_path == temp_db

        # Test getting a connection
        with pool.get_connection() as conn:
            assert conn is not None
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
            assert count == 4

        pool.close_all()

    def test_connection_pool_concurrent_access(self, temp_db):
        """Test concurrent access to connection pool"""
        pool = DatabaseConnectionPool(temp_db, pool_size=3)
        results = []

        def query_database(thread_id):
            try:
                with pool.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT COUNT(*) FROM products WHERE category = ?", ('Modul',))
                    count = cursor.fetchone()[0]
                    time.sleep(0.1)  # Simulate some work
                    return {
                        'thread_id': thread_id,
                        'count': count,
                        'success': True}
            except Exception as e:
                return {
                    'thread_id': thread_id,
                    'error': str(e),
                    'success': False}

        # Run concurrent queries
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(query_database, i) for i in range(10)]
            results = [future.result() for future in as_completed(futures)]

        # All queries should succeed
        successful_results = [r for r in results if r['success']]
        assert len(successful_results) == 10

        # All should return the same count
        counts = [r['count'] for r in successful_results]
        assert all(count == 2 for count in counts)  # 2 modules in test data

        pool.close_all()


class TestDatabaseOptimizer:
    """Test the database optimizer functionality"""

    @pytest.fixture
    def temp_db_with_optimizer(self):
        """Create a temporary database with optimizer"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        # Create test database with full schema
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row

        # Create products table with all pricing fields
        conn.execute("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                model_name TEXT NOT NULL UNIQUE,
                brand TEXT,
                price_euro REAL,
                calculate_per TEXT DEFAULT 'Stück',
                purchase_price_net REAL DEFAULT 0.0,
                margin_type TEXT DEFAULT 'percentage',
                margin_value REAL DEFAULT 0.0,
                margin_priority INTEGER DEFAULT 0,
                pricing_category TEXT DEFAULT '',
                last_price_update TEXT DEFAULT '',
                technology TEXT DEFAULT '',
                feature TEXT DEFAULT '',
                design TEXT DEFAULT '',
                upgrade TEXT DEFAULT '',
                capacity_w REAL DEFAULT 0.0,
                power_kw REAL DEFAULT 0.0,
                efficiency_percent REAL DEFAULT 0.0,
                length_m REAL DEFAULT 0.0,
                width_m REAL DEFAULT 0.0,
                company_id INTEGER
            )
        """)

        # Create pricing tables
        conn.execute("""
            CREATE TABLE pricing_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_name TEXT NOT NULL,
                rule_type TEXT NOT NULL,
                applies_to TEXT NOT NULL,
                target_id INTEGER,
                rule_config TEXT,
                is_active INTEGER DEFAULT 1,
                priority INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE pricing_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                field_name TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                change_reason TEXT,
                changed_by TEXT,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE admin_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        # Insert comprehensive test data
        test_products = [
            (1,
             'Modul',
             'Test Module 1',
             'Brand A',
             200.0,
             'Stück',
             100.0,
             'percentage',
             25.0,
             0,
             'solar',
             '',
             'mono',
             'standard',
             'black',
             '',
             400.0,
             0.0,
             20.5,
             2.0,
             1.0,
             1),
            (2,
             'Modul',
             'Test Module 2',
             'Brand B',
             300.0,
             'Stück',
             150.0,
             'percentage',
             30.0,
             0,
             'solar',
             '',
             'poly',
             'premium',
             'silver',
             'bifacial',
             450.0,
             0.0,
             21.0,
             2.1,
             1.1,
             1),
            (3,
             'Kabel',
             'Test Cable 1',
             'Brand C',
             7.0,
             'Meter',
             5.0,
             'fixed',
             2.0,
             0,
             'electrical',
             '',
             '',
             '',
             '',
             '',
             0.0,
             0.0,
             0.0,
             0.0,
             0.0,
             1),
            (4,
             'Wechselrichter',
             'Test Inverter 1',
             'Brand D',
             800.0,
             'Stück',
             600.0,
             'percentage',
             20.0,
             0,
             'power',
             '',
             'string',
             'standard',
             '',
             '',
             0.0,
             5.0,
             97.5,
             0.5,
             0.3,
             1),
            (5,
             'Service',
             'Installation Service',
             'Brand E',
             1000.0,
             'pauschal',
             800.0,
             'percentage',
             25.0,
             0,
             'service',
             '',
             '',
             '',
             '',
             '',
             0.0,
             0.0,
             0.0,
             0.0,
             0.0,
             1),
        ]

        conn.executemany("""
            INSERT INTO products (
                id, category, model_name, brand, price_euro, calculate_per,
                purchase_price_net, margin_type, margin_value, margin_priority,
                pricing_category, last_price_update, technology, feature, design, upgrade,
                capacity_w, power_kw, efficiency_percent, length_m, width_m, company_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, test_products)

        # Insert test pricing rules
        test_rules = [
            (1,
             'Global Margin Rule',
             'margin',
             'global',
             None,
             '{"margin_type": "percentage", "margin_value": 25.0}',
             1,
             0),
            (2,
             'Module Discount Rule',
             'discount',
             'category',
             1,
             '{"discount_type": "percentage", "discount_value": 5.0}',
             1,
             1),
        ]

        conn.executemany("""
            INSERT INTO pricing_rules (id, rule_name, rule_type, applies_to, target_id, rule_config, is_active, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, test_rules)

        conn.commit()
        conn.close()

        # Create optimizer instance
        optimizer = DatabaseOptimizer(path)

        yield path, optimizer

        # Cleanup
        optimizer.close()
        if os.path.exists(path):
            os.unlink(path)

    def test_create_pricing_indexes(self, temp_db_with_optimizer):
        """Test creation of pricing-related indexes"""
        db_path, optimizer = temp_db_with_optimizer

        # Create indexes
        success = optimizer.create_pricing_indexes()
        assert success

        # Verify indexes were created
        with optimizer.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = [row[0] for row in cursor.fetchall()]

            # Check for key indexes
            expected_indexes = [
                'idx_products_category',
                'idx_products_calculate_per',
                'idx_products_pricing_category',
                'idx_pricing_rules_applies_to',
                'idx_pricing_history_product'
            ]

            for expected_index in expected_indexes:
                assert expected_index in indexes, f"Index {expected_index} not found"

    def test_optimized_queries(self, temp_db_with_optimizer):
        """Test that optimized queries work correctly"""
        db_path, optimizer = temp_db_with_optimizer

        # Create indexes first
        optimizer.create_pricing_indexes()

        queries = optimizer.optimize_product_queries()

        with optimizer.get_connection() as conn:
            cursor = conn.cursor()

            # Test category query with pricing
            cursor.execute(
                queries['products_by_category_with_pricing'], ('Modul',))
            results = cursor.fetchall()
            assert len(results) == 2  # 2 modules in test data

            # Verify calculated selling price
            for row in results:
                row_dict = dict(row)
                assert 'calculated_selling_price' in row_dict
                assert row_dict['calculated_selling_price'] > 0

            # Test calculate_per query
            cursor.execute(queries['products_by_calculate_per'], ('Stück',))
            results = cursor.fetchall()
            assert len(results) == 3  # 2 modules + 1 inverter

            # Test pricing calculation query
            cursor.execute(queries['product_pricing_calculation'], (1,))
            result = cursor.fetchone()
            assert result is not None
            result_dict = dict(result)
            assert result_dict['model_name'] == 'Test Module 1'
            assert result_dict['purchase_price_net'] == 100.0

    def test_query_performance_analysis(self, temp_db_with_optimizer):
        """Test query performance analysis functionality"""
        db_path, optimizer = temp_db_with_optimizer

        # Create indexes for better performance
        optimizer.create_pricing_indexes()

        # Analyze a simple query
        query = "SELECT * FROM products WHERE category = ?"
        params = ('Modul',)

        analysis = optimizer.analyze_query_performance(query, params)

        assert 'execution_time_ms' in analysis
        assert 'result_count' in analysis
        assert 'query_plan' in analysis
        assert 'uses_index' in analysis
        assert 'optimization_suggestions' in analysis

        # Should use index after optimization
        assert analysis['uses_index']
        assert analysis['result_count'] == 2

    def test_database_statistics(self, temp_db_with_optimizer):
        """Test database statistics collection"""
        db_path, optimizer = temp_db_with_optimizer

        stats = optimizer.get_database_statistics()

        # Check expected statistics
        assert 'products_count' in stats
        assert 'pricing_rules_count' in stats
        assert 'pricing_history_count' in stats
        assert 'database_size_mb' in stats
        assert 'products_with_calc_per' in stats

        # Verify counts match test data
        assert stats['products_count'] == 5
        assert stats['pricing_rules_count'] == 2
        # All products have calculate_per set
        assert stats['products_with_calc_per'] == 5

    def test_database_maintenance(self, temp_db_with_optimizer):
        """Test database maintenance operations"""
        db_path, optimizer = temp_db_with_optimizer

        # Test VACUUM operation
        vacuum_success = optimizer.vacuum_database()
        assert vacuum_success

        # Test ANALYZE operation
        analyze_success = optimizer.analyze_database()
        assert analyze_success


class TestPricingQueryBuilder:
    """Test the pricing query builder functionality"""

    @pytest.fixture
    def query_builder_with_data(self):
        """Create query builder with test data"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        # Create and populate test database
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row

        conn.execute("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                category TEXT,
                model_name TEXT,
                brand TEXT,
                calculate_per TEXT,
                purchase_price_net REAL,
                margin_type TEXT,
                margin_value REAL,
                price_euro REAL
            )
        """)

        test_data = [
            (1, 'Modul', 'Module A', 'Brand X',
             'Stück', 100.0, 'percentage', 25.0, 125.0),
            (2, 'Modul', 'Module B', 'Brand Y',
             'Stück', 150.0, 'percentage', 30.0, 195.0),
            (3, 'Kabel', 'Cable A', 'Brand Z', 'Meter',
             None, None, None, 5.0),  # Pricing issues
            (4, 'Service', 'Service A', 'Brand W',
             'pauschal', 500.0, 'fixed', 100.0, 600.0),
        ]

        conn.executemany(
            "INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            test_data
        )
        conn.commit()
        conn.close()

        # Create optimizer and query builder
        optimizer = DatabaseOptimizer(path)
        optimizer.create_pricing_indexes()
        query_builder = PricingQueryBuilder()
        query_builder.optimizer = optimizer  # Override with test optimizer

        yield query_builder

        # Cleanup
        optimizer.close()
        if os.path.exists(path):
            os.unlink(path)

    def test_get_products_by_category_with_pricing(
            self, query_builder_with_data):
        """Test getting products by category with pricing calculations"""
        products = query_builder_with_data.get_products_by_category_with_pricing(
            'Modul')

        assert len(products) == 2

        # Check that calculated pricing is included
        for product in products:
            assert 'calculated_selling_price' in product
            assert product['calculated_selling_price'] > 0

    def test_get_products_by_calculate_per(self, query_builder_with_data):
        """Test getting products by calculation method"""
        products_per_piece = query_builder_with_data.get_products_by_calculate_per(
            'Stück')
        assert len(products_per_piece) == 2

        products_per_meter = query_builder_with_data.get_products_by_calculate_per(
            'Meter')
        assert len(products_per_meter) == 1

        products_lump_sum = query_builder_with_data.get_products_by_calculate_per(
            'pauschal')
        assert len(products_lump_sum) == 1

    def test_get_product_pricing_data(self, query_builder_with_data):
        """Test getting comprehensive pricing data for a product"""
        pricing_data = query_builder_with_data.get_product_pricing_data(1)

        assert pricing_data is not None
        assert pricing_data['model_name'] == 'Module A'
        assert pricing_data['purchase_price_net'] == 100.0
        assert pricing_data['margin_type'] == 'percentage'
        assert pricing_data['margin_value'] == 25.0

    def test_get_products_with_pricing_issues(self, query_builder_with_data):
        """Test identifying products with pricing configuration issues"""
        problem_products = query_builder_with_data.get_products_with_pricing_issues()

        # Should find the cable product with missing pricing info
        assert len(problem_products) >= 1

        cable_product = next(
            (p for p in problem_products if p['category'] == 'Kabel'), None)
        assert cable_product is not None
        assert cable_product['purchase_price_net'] is None


class TestPerformanceBenchmarks:
    """Performance benchmark tests"""

    def test_connection_pool_vs_direct_performance(self):
        """Compare performance of connection pool vs direct connections"""
        # Create temporary database
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        # Setup test database
        conn = sqlite3.connect(path)
        conn.execute(
            "CREATE TABLE test_table (id INTEGER PRIMARY KEY, value TEXT)")
        conn.executemany(
            "INSERT INTO test_table VALUES (?, ?)",
            [(i, f"value_{i}") for i in range(1000)]
        )
        conn.commit()
        conn.close()

        # Test direct connections
        def direct_connection_test():
            start_time = time.time()
            for _ in range(50):
                conn = sqlite3.connect(path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM test_table")
                cursor.fetchone()
                conn.close()
            return time.time() - start_time

        # Test connection pool
        def pool_connection_test():
            pool = DatabaseConnectionPool(path, pool_size=5)
            start_time = time.time()
            for _ in range(50):
                with pool.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM test_table")
                    cursor.fetchone()
            pool.close_all()
            return time.time() - start_time

        direct_time = direct_connection_test()
        pool_time = pool_connection_test()

        print(f"Direct connections: {direct_time:.3f}s")
        print(f"Connection pool: {pool_time:.3f}s")

        # Pool should be faster or at least not significantly slower
        assert pool_time <= direct_time * 1.5  # Allow 50% overhead at most

        # Cleanup
        os.unlink(path)

    def test_index_performance_improvement(self):
        """Test that indexes improve query performance"""
        # Create temporary database
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        # Setup large test database
        conn = sqlite3.connect(path)
        conn.execute("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                category TEXT,
                model_name TEXT,
                calculate_per TEXT,
                purchase_price_net REAL
            )
        """)

        # Insert many test records
        test_data = []
        categories = ['Modul', 'Wechselrichter', 'Kabel', 'Service']
        calc_methods = ['Stück', 'Meter', 'pauschal', 'kWp']

        for i in range(5000):
            test_data.append((
                i + 1,
                categories[i % len(categories)],
                f"Product_{i}",
                calc_methods[i % len(calc_methods)],
                100.0 + (i % 500)
            ))

        conn.executemany(
            "INSERT INTO products VALUES (?, ?, ?, ?, ?)",
            test_data
        )
        conn.commit()

        # Test query performance without indexes
        def query_without_index():
            start_time = time.time()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM products WHERE category = ? AND calculate_per = ?",
                ('Modul',
                 'Stück'))
            results = cursor.fetchall()
            return time.time() - start_time, len(results)

        time_without_index, result_count = query_without_index()

        # Create indexes
        conn.execute("CREATE INDEX idx_category ON products(category)")
        conn.execute("CREATE INDEX idx_calc_per ON products(calculate_per)")
        conn.execute(
            "CREATE INDEX idx_category_calc_per ON products(category, calculate_per)")

        # Test query performance with indexes
        def query_with_index():
            start_time = time.time()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM products WHERE category = ? AND calculate_per = ?",
                ('Modul',
                 'Stück'))
            results = cursor.fetchall()
            return time.time() - start_time, len(results)

        time_with_index, result_count_indexed = query_with_index()

        print(
            f"Query without index: {
                time_without_index:.4f}s ({result_count} results)")
        print(
            f"Query with index: {
                time_with_index:.4f}s ({result_count_indexed} results)")

        # Results should be the same
        assert result_count == result_count_indexed

        # Indexed query should be faster (allow some variance for small
        # datasets)
        if time_without_index > 0.01:  # Only test if query takes meaningful time
            assert time_with_index <= time_without_index

        conn.close()
        os.unlink(path)


if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v"])
