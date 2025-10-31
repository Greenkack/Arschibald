#!/usr/bin/env python3
"""
Database Optimization Module for Enhanced Pricing System
Provides database query optimization, indexing, and connection pooling for pricing operations.
"""

import logging
import os
import sqlite3
import threading
import time
import traceback
from contextlib import contextmanager
from queue import Empty, Queue
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConnectionPool:
    """
    Connection pool for SQLite database to handle high-load scenarios.
    """

    def __init__(
            self,
            db_path: str,
            pool_size: int = 10,
            timeout: float = 30.0):
        self.db_path = db_path
        self.pool_size = pool_size
        self.timeout = timeout
        self.pool = Queue(maxsize=pool_size)
        self.active_connections = 0
        self.lock = threading.Lock()

        # Initialize pool with connections
        self._initialize_pool()

    def _initialize_pool(self):
        """Initialize the connection pool with connections"""
        for _ in range(self.pool_size):
            try:
                conn = self._create_connection()
                if conn:
                    self.pool.put(conn)
            except Exception as e:
                logger.error(f"Failed to create initial connection: {e}")

    def _create_connection(self) -> sqlite3.Connection | None:
        """Create a new database connection with optimized settings"""
        try:
            conn = sqlite3.connect(
                self.db_path,
                timeout=self.timeout,
                check_same_thread=False
            )
            conn.row_factory = sqlite3.Row

            # Optimize SQLite settings for performance
            conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
            # Balance safety and speed
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")  # Increase cache size
            # Use memory for temp tables
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.execute("PRAGMA mmap_size=268435456")  # 256MB memory mapping

            return conn
        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            return None

    @contextmanager
    def get_connection(self):
        """Get a connection from the pool (context manager)"""
        conn = None
        try:
            # Try to get connection from pool
            try:
                conn = self.pool.get(timeout=5.0)
            except Empty:
                # Pool is empty, create new connection if under limit
                with self.lock:
                    if self.active_connections < self.pool_size * 2:  # Allow overflow
                        conn = self._create_connection()
                        if conn:
                            self.active_connections += 1
                    else:
                        # Wait for connection to become available
                        conn = self.pool.get(timeout=self.timeout)

            if not conn:
                raise Exception("Could not obtain database connection")

            yield conn

        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                try:
                    # Return connection to pool if it's still valid
                    conn.execute("SELECT 1")  # Test connection
                    self.pool.put(conn, timeout=1.0)
                except (sqlite3.Error, Empty):
                    # Connection is invalid or pool is full, close it
                    try:
                        conn.close()
                    except BaseException:
                        pass
                    with self.lock:
                        self.active_connections = max(
                            0, self.active_connections - 1)

    def close_all(self):
        """Close all connections in the pool"""
        while not self.pool.empty():
            try:
                conn = self.pool.get_nowait()
                conn.close()
            except (Empty, sqlite3.Error):
                pass


class DatabaseOptimizer:
    """
    Database optimization utilities for pricing system.
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            try:
                from database import DB_PATH
                self.db_path = DB_PATH
            except ImportError:
                self.db_path = os.path.join('data', 'app_data.db')
        else:
            self.db_path = db_path

        self.connection_pool = None
        self._initialize_pool()

    def _initialize_pool(self):
        """Initialize connection pool if database exists"""
        if os.path.exists(self.db_path):
            self.connection_pool = DatabaseConnectionPool(self.db_path)

    def get_connection(self):
        """Get optimized database connection"""
        if self.connection_pool:
            return self.connection_pool.get_connection()
        # Fallback to direct connection
        return self._get_direct_connection()

    @contextmanager
    def _get_direct_connection(self):
        """Direct connection fallback"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            # Apply optimizations
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")

            yield conn
        finally:
            if conn:
                conn.close()

    def create_pricing_indexes(self) -> bool:
        """Create comprehensive indexes for pricing-related queries"""
        # First, check which columns and tables exist
        existing_columns = self._get_existing_columns()
        existing_tables = self._get_existing_tables()

        # Build index list based on what exists
        indexes = []

        # Basic product indexes
        if 'category' in existing_columns.get('products', []):
            indexes.append(
                "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)")
        if 'brand' in existing_columns.get('products', []):
            indexes.append(
                "CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand)")
        if 'model_name' in existing_columns.get('products', []):
            indexes.append(
                "CREATE INDEX IF NOT EXISTS idx_products_model_name ON products(model_name)")
        if 'calculate_per' in existing_columns.get('products', []):
            indexes.append(
                "CREATE INDEX IF NOT EXISTS idx_products_calculate_per ON products(calculate_per)")
        if 'pricing_category' in existing_columns.get('products', []):
            indexes.append(
                "CREATE INDEX IF NOT EXISTS idx_products_pricing_category ON products(pricing_category)")
        if 'last_price_update' in existing_columns.get('products', []):
            indexes.append(
                "CREATE INDEX IF NOT EXISTS idx_products_last_price_update ON products(last_price_update)")
        if 'purchase_price_net' in existing_columns.get('products', []):
            indexes.append(
                "CREATE INDEX IF NOT EXISTS idx_products_purchase_price ON products(purchase_price_net)")
        if 'margin_type' in existing_columns.get('products', []):
            indexes.append(
                "CREATE INDEX IF NOT EXISTS idx_products_margin_type ON products(margin_type)")
        if 'technology' in existing_columns.get('products', []):
            indexes.append(
                "CREATE INDEX IF NOT EXISTS idx_products_technology ON products(technology)")
        if 'feature' in existing_columns.get('products', []):
            indexes.append(
                "CREATE INDEX IF NOT EXISTS idx_products_feature ON products(feature)")
        if 'company_id' in existing_columns.get('products', []):
            indexes.append(
                "CREATE INDEX IF NOT EXISTS idx_products_company_id ON products(company_id)")

        # Composite indexes
        product_cols = existing_columns.get('products', [])
        if 'category' in product_cols and 'brand' in product_cols:
            indexes.append(
                "CREATE INDEX IF NOT EXISTS idx_products_category_brand ON products(category, brand)")
        if 'category' in product_cols and 'calculate_per' in product_cols:
            indexes.append(
                "CREATE INDEX IF NOT EXISTS idx_products_category_calc_per ON products(category, calculate_per)")
        if all(
            col in product_cols for col in [
                'purchase_price_net',
                'margin_type',
                'margin_value']):
            indexes.append(
                "CREATE INDEX IF NOT EXISTS idx_products_margin_calc ON products(purchase_price_net, margin_type, margin_value)")

        # Pricing rules table indexes
        if 'pricing_rules' in existing_tables:
            indexes.extend([
                "CREATE INDEX IF NOT EXISTS idx_pricing_rules_applies_to ON pricing_rules(applies_to, target_id)",
                "CREATE INDEX IF NOT EXISTS idx_pricing_rules_active ON pricing_rules(is_active, priority)",
                "CREATE INDEX IF NOT EXISTS idx_pricing_rules_type ON pricing_rules(rule_type, is_active)"
            ])

        # Pricing history table indexes
        if 'pricing_history' in existing_tables:
            indexes.extend([
                "CREATE INDEX IF NOT EXISTS idx_pricing_history_product ON pricing_history(product_id, changed_at)",
                "CREATE INDEX IF NOT EXISTS idx_pricing_history_field ON pricing_history(field_name, changed_at)"
            ])

        # Admin settings indexes
        if 'admin_settings' in existing_tables:
            indexes.append(
                "CREATE INDEX IF NOT EXISTS idx_admin_settings_key ON admin_settings(key)")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                created_count = 0
                for index_sql in indexes:
                    try:
                        cursor.execute(index_sql)
                        created_count += 1
                        logger.info(
                            f"Created index: {
                                index_sql.split('idx_')[1].split(' ')[0] if 'idx_' in index_sql else 'unknown'}")
                    except sqlite3.Error as e:
                        if "already exists" not in str(e).lower():
                            logger.warning(
                                f"Could not create index: {index_sql}, Error: {e}")

                conn.commit()
                logger.info(
                    f"Successfully created {created_count} pricing-related indexes")
                return True

        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            traceback.print_exc()
            return False

    def _get_existing_columns(self) -> dict[str, list[str]]:
        """Get existing columns for each table"""
        columns = {}
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Get all tables
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]

                for table in tables:
                    try:
                        cursor.execute(f"PRAGMA table_info({table})")
                        table_columns = [row[1] for row in cursor.fetchall()]
                        columns[table] = table_columns
                    except sqlite3.Error:
                        columns[table] = []

        except Exception as e:
            logger.error(f"Failed to get existing columns: {e}")

        return columns

    def _get_existing_tables(self) -> list[str]:
        """Get list of existing tables"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get existing tables: {e}")
            return []

    def _build_flexible_pricing_query(self) -> str:
        """Build pricing calculation query based on available columns"""
        existing_columns = self._get_existing_columns()
        product_cols = existing_columns.get('products', [])

        # Base columns that should always exist
        base_cols = ['id', 'model_name']

        # Optional pricing columns
        optional_cols = [
            'purchase_price_net',
            'margin_type',
            'margin_value',
            'calculate_per',
            'technology',
            'feature',
            'design',
            'upgrade',
            'capacity_w',
            'power_kw',
            'efficiency_percent',
            'length_m',
            'width_m',
            'price_euro']

        # Build column list
        select_cols = []
        for col in base_cols:
            if col in product_cols:
                select_cols.append(f'p.{col}')

        for col in optional_cols:
            if col in product_cols:
                select_cols.append(f'p.{col}')

        if not select_cols:
            # Fallback if no columns found
            return "SELECT p.* FROM products p WHERE p.id = ?"

        return f"SELECT {
            ', '.join(select_cols)} FROM products p WHERE p.id = ?"

    def optimize_product_queries(self) -> dict[str, str]:
        """
        Return optimized SQL queries for common product operations.
        """
        return {
            # Optimized product lookup by category with pricing info
            'products_by_category_with_pricing': """
                SELECT p.*,
                       CASE
                           WHEN p.purchase_price_net > 0 AND p.margin_type = 'percentage'
                           THEN p.purchase_price_net * (1 + p.margin_value / 100.0)
                           WHEN p.purchase_price_net > 0 AND p.margin_type = 'fixed'
                           THEN p.purchase_price_net + p.margin_value
                           ELSE p.price_euro
                       END as calculated_selling_price
                FROM products p
                WHERE p.category = ?
                ORDER BY p.brand, p.model_name
            """,

            # Fast product lookup by calculate_per method
            'products_by_calculate_per': """
                SELECT p.id, p.model_name, p.brand, p.category, p.calculate_per,
                       p.purchase_price_net, p.margin_type, p.margin_value, p.price_euro
                FROM products p
                WHERE p.calculate_per = ?
                ORDER BY p.category, p.model_name
            """,

            # Optimized pricing calculation query (flexible column selection)
            'product_pricing_calculation': self._build_flexible_pricing_query(),

            # Fast category and brand lookup
            'distinct_categories': """
                SELECT DISTINCT category
                FROM products
                WHERE category IS NOT NULL AND category != ''
                ORDER BY category
            """,

            'distinct_brands': """
                SELECT DISTINCT brand
                FROM products
                WHERE brand IS NOT NULL AND brand != ''
                ORDER BY brand
            """,

            # Products with pricing issues (for maintenance)
            'products_pricing_issues': """
                SELECT p.id, p.model_name, p.category, p.purchase_price_net,
                       p.margin_type, p.margin_value, p.price_euro
                FROM products p
                WHERE (p.purchase_price_net IS NULL OR p.purchase_price_net <= 0)
                   OR (p.margin_type IS NULL OR p.margin_type = '')
                   OR (p.calculate_per IS NULL OR p.calculate_per = '')
                ORDER BY p.category, p.model_name
            """,

            # Recent pricing updates
            'recent_pricing_updates': """
                SELECT p.id, p.model_name, p.last_price_update, p.purchase_price_net, p.margin_value
                FROM products p
                WHERE p.last_price_update IS NOT NULL
                  AND p.last_price_update > datetime('now', '-30 days')
                ORDER BY p.last_price_update DESC
            """
        }

    def analyze_query_performance(
            self, query: str, params: tuple = ()) -> dict[str, Any]:
        """
        Analyze query performance and provide optimization suggestions.
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Get query plan
                explain_query = f"EXPLAIN QUERY PLAN {query}"
                cursor.execute(explain_query, params)
                query_plan = cursor.fetchall()

                # Measure execution time
                start_time = time.time()
                cursor.execute(query, params)
                results = cursor.fetchall()
                execution_time = time.time() - start_time

                # Analyze plan for optimization opportunities
                suggestions = []
                uses_index = any("USING INDEX" in str(row)
                                 for row in query_plan)

                if not uses_index:
                    suggestions.append(
                        "Consider adding indexes for WHERE clause columns")

                if execution_time > 0.1:  # More than 100ms
                    suggestions.append(
                        "Query execution time is high, consider optimization")

                if len(results) > 1000:
                    suggestions.append(
                        "Large result set, consider adding LIMIT clause")

                return {
                    'execution_time_ms': execution_time * 1000,
                    'result_count': len(results),
                    'query_plan': [dict(row) for row in query_plan],
                    'uses_index': uses_index,
                    'optimization_suggestions': suggestions
                }

        except Exception as e:
            logger.error(f"Query analysis failed: {e}")
            return {'error': str(e)}

    def get_database_statistics(self) -> dict[str, Any]:
        """Get comprehensive database statistics for performance monitoring"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                stats = {}
                existing_tables = self._get_existing_tables()
                existing_columns = self._get_existing_columns()

                # Table sizes
                if 'products' in existing_tables:
                    cursor.execute("SELECT COUNT(*) FROM products")
                    stats['products_count'] = cursor.fetchone()[0]
                else:
                    stats['products_count'] = 0

                if 'pricing_rules' in existing_tables:
                    cursor.execute("SELECT COUNT(*) FROM pricing_rules")
                    stats['pricing_rules_count'] = cursor.fetchone()[0]
                else:
                    stats['pricing_rules_count'] = 0

                if 'pricing_history' in existing_tables:
                    cursor.execute("SELECT COUNT(*) FROM pricing_history")
                    stats['pricing_history_count'] = cursor.fetchone()[0]
                else:
                    stats['pricing_history_count'] = 0

                # Index usage statistics
                if 'products' in existing_tables:
                    cursor.execute("PRAGMA index_list(products)")
                    product_indexes = cursor.fetchall()
                    stats['product_indexes_count'] = len(product_indexes)
                else:
                    stats['product_indexes_count'] = 0

                # Database file size
                if os.path.exists(self.db_path):
                    stats['database_size_mb'] = round(
                        os.path.getsize(self.db_path) / (1024 * 1024), 2)

                # Pricing-specific statistics (only if columns exist)
                product_cols = existing_columns.get('products', [])

                if 'calculate_per' in product_cols:
                    cursor.execute(
                        "SELECT COUNT(*) FROM products WHERE calculate_per IS NOT NULL")
                    stats['products_with_calc_per'] = cursor.fetchone()[0]
                else:
                    stats['products_with_calc_per'] = 0

                if 'purchase_price_net' in product_cols:
                    cursor.execute(
                        "SELECT COUNT(*) FROM products WHERE purchase_price_net > 0")
                    stats['products_with_purchase_price'] = cursor.fetchone()[
                        0]
                else:
                    stats['products_with_purchase_price'] = 0

                if 'margin_type' in product_cols:
                    cursor.execute(
                        "SELECT COUNT(*) FROM products WHERE margin_type IS NOT NULL")
                    stats['products_with_margin_config'] = cursor.fetchone()[0]
                else:
                    stats['products_with_margin_config'] = 0

                # Performance metrics
                cursor.execute("PRAGMA cache_size")
                stats['cache_size'] = cursor.fetchone()[0]

                cursor.execute("PRAGMA journal_mode")
                stats['journal_mode'] = cursor.fetchone()[0]

                return stats

        except Exception as e:
            logger.error(f"Failed to get database statistics: {e}")
            return {'error': str(e)}

    def vacuum_database(self) -> bool:
        """Perform database maintenance (VACUUM) to optimize storage"""
        try:
            with self.get_connection() as conn:
                logger.info("Starting database VACUUM operation...")
                conn.execute("VACUUM")
                logger.info("Database VACUUM completed successfully")
                return True
        except Exception as e:
            logger.error(f"Database VACUUM failed: {e}")
            return False

    def analyze_database(self) -> bool:
        """Analyze database to update query planner statistics"""
        try:
            with self.get_connection() as conn:
                logger.info("Starting database ANALYZE operation...")
                conn.execute("ANALYZE")
                logger.info("Database ANALYZE completed successfully")
                return True
        except Exception as e:
            logger.error(f"Database ANALYZE failed: {e}")
            return False

    def close(self):
        """Close connection pool and cleanup resources"""
        if self.connection_pool:
            self.connection_pool.close_all()


# Global optimizer instance
_optimizer_instance = None


def get_database_optimizer() -> DatabaseOptimizer:
    """Get global database optimizer instance"""
    global _optimizer_instance
    if _optimizer_instance is None:
        _optimizer_instance = DatabaseOptimizer()
    return _optimizer_instance


def optimize_pricing_queries() -> bool:
    """Convenience function to optimize all pricing-related queries"""
    optimizer = get_database_optimizer()
    return optimizer.create_pricing_indexes()


def get_optimized_connection():
    """Get optimized database connection (context manager)"""
    optimizer = get_database_optimizer()
    return optimizer.get_connection()

# Query builder for common pricing operations


class PricingQueryBuilder:
    """
    Builder class for constructing optimized pricing queries.
    """

    def __init__(self):
        self.optimizer = get_database_optimizer()
        self.queries = self.optimizer.optimize_product_queries()

    def get_products_by_category_with_pricing(
            self, category: str) -> list[dict[str, Any]]:
        """Get products by category with calculated pricing"""
        try:
            with self.optimizer.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    self.queries['products_by_category_with_pricing'], (category,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get products by category: {e}")
            return []

    def get_products_by_calculate_per(
            self, calculate_per: str) -> list[dict[str, Any]]:
        """Get products by calculation method"""
        try:
            with self.optimizer.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    self.queries['products_by_calculate_per'], (calculate_per,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get products by calculate_per: {e}")
            return []

    def get_product_pricing_data(
            self, product_id: int) -> dict[str, Any] | None:
        """Get comprehensive pricing data for a product"""
        try:
            with self.optimizer.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    self.queries['product_pricing_calculation'], (product_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get product pricing data: {e}")
            return None

    def get_products_with_pricing_issues(self) -> list[dict[str, Any]]:
        """Get products that have pricing configuration issues"""
        try:
            with self.optimizer.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(self.queries['products_pricing_issues'])
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get products with pricing issues: {e}")
            return []


if __name__ == "__main__":
    # Test the optimization system
    optimizer = DatabaseOptimizer()

    print("Creating pricing indexes...")
    success = optimizer.create_pricing_indexes()
    print(f"Index creation: {'Success' if success else 'Failed'}")

    print("\nDatabase statistics:")
    stats = optimizer.get_database_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\nTesting query builder...")
    query_builder = PricingQueryBuilder()

    # Test category query
    products = query_builder.get_products_by_category_with_pricing("Modul")
    print(f"Found {len(products)} products in 'Modul' category")

    # Test calculate_per query
    products_per_piece = query_builder.get_products_by_calculate_per("Stück")
    print(
        f"Found {
            len(products_per_piece)} products with 'Stück' calculation method")

    optimizer.close()
    print("\nOptimization test completed!")
