"""
Database Query Optimization Module

This module provides database query optimization utilities including:
- Query optimization helpers
- Index management
- Connection pooling configuration
- Query performance monitoring
"""

from typing import Any, Dict, List, Optional, Type
from sqlalchemy import Index, inspect, text
from sqlalchemy.orm import Session, Query
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine import Engine
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """Optimize database queries for better performance"""
    
    def __init__(self, session: Session):
        self.session = session
        self.query_stats: Dict[str, Dict[str, Any]] = {}
    
    def optimize_query(self, query: Query) -> Query:
        """
        Apply optimization strategies to a query
        
        Args:
            query: SQLAlchemy query object
            
        Returns:
            Optimized query
        """
        # Enable query result caching
        query = query.execution_options(compiled_cache={})
        
        return query
    
    def add_eager_loading(self, query: Query, *relationships) -> Query:
        """
        Add eager loading for relationships to avoid N+1 queries
        
        Args:
            query: SQLAlchemy query object
            *relationships: Relationship attributes to eager load
            
        Returns:
            Query with eager loading
        """
        from sqlalchemy.orm import joinedload
        
        for relationship in relationships:
            query = query.options(joinedload(relationship))
        
        return query
    
    def add_pagination(self, query: Query, page: int = 1, page_size: int = 50) -> Query:
        """
        Add pagination to query
        
        Args:
            query: SQLAlchemy query object
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Paginated query
        """
        offset = (page - 1) * page_size
        return query.limit(page_size).offset(offset)
    
    def track_query_performance(self, query_name: str):
        """
        Decorator to track query performance
        
        Args:
            query_name: Name to identify the query
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Track statistics
                if query_name not in self.query_stats:
                    self.query_stats[query_name] = {
                        'count': 0,
                        'total_time': 0,
                        'avg_time': 0,
                        'max_time': 0,
                        'min_time': float('inf')
                    }
                
                stats = self.query_stats[query_name]
                stats['count'] += 1
                stats['total_time'] += duration
                stats['avg_time'] = stats['total_time'] / stats['count']
                stats['max_time'] = max(stats['max_time'], duration)
                stats['min_time'] = min(stats['min_time'], duration)
                
                # Log slow queries
                if duration > 1.0:  # Queries taking more than 1 second
                    logger.warning(
                        f"Slow query detected: {query_name} took {duration:.2f}s"
                    )
                
                return result
            return wrapper
        return decorator
    
    def get_query_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get query performance statistics"""
        return self.query_stats


class IndexManager:
    """Manage database indexes for optimal query performance"""
    
    def __init__(self, engine: Engine):
        self.engine = engine
    
    def create_index(
        self,
        table_name: str,
        column_names: List[str],
        index_name: Optional[str] = None,
        unique: bool = False
    ):
        """
        Create an index on specified columns
        
        Args:
            table_name: Name of the table
            column_names: List of column names to index
            index_name: Optional custom index name
            unique: Whether the index should be unique
        """
        if not index_name:
            index_name = f"idx_{table_name}_{'_'.join(column_names)}"
        
        columns_str = ', '.join(column_names)
        unique_str = 'UNIQUE' if unique else ''
        
        sql = f"""
        CREATE {unique_str} INDEX IF NOT EXISTS {index_name}
        ON {table_name} ({columns_str})
        """
        
        with self.engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
        
        logger.info(f"Created index {index_name} on {table_name}({columns_str})")
    
    def drop_index(self, index_name: str):
        """Drop an index"""
        sql = f"DROP INDEX IF EXISTS {index_name}"
        
        with self.engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
        
        logger.info(f"Dropped index {index_name}")
    
    def list_indexes(self, table_name: str) -> List[Dict[str, Any]]:
        """
        List all indexes for a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of index information dictionaries
        """
        inspector = inspect(self.engine)
        indexes = inspector.get_indexes(table_name)
        return indexes
    
    def analyze_missing_indexes(self, model: Type[DeclarativeMeta]) -> List[str]:
        """
        Analyze a model and suggest missing indexes
        
        Args:
            model: SQLAlchemy model class
            
        Returns:
            List of suggested index creation statements
        """
        suggestions = []
        inspector = inspect(self.engine)
        table_name = model.__tablename__
        
        # Get existing indexes
        existing_indexes = {
            tuple(idx['column_names']) 
            for idx in inspector.get_indexes(table_name)
        }
        
        # Check foreign keys
        for fk in inspector.get_foreign_keys(table_name):
            columns = tuple(fk['constrained_columns'])
            if columns not in existing_indexes:
                suggestions.append(
                    f"CREATE INDEX idx_{table_name}_{'_'.join(columns)} "
                    f"ON {table_name} ({', '.join(columns)})"
                )
        
        return suggestions


class ConnectionPoolManager:
    """Manage database connection pooling"""
    
    @staticmethod
    def get_pool_config(
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 3600
    ) -> Dict[str, Any]:
        """
        Get connection pool configuration
        
        Args:
            pool_size: Number of connections to maintain
            max_overflow: Maximum overflow connections
            pool_timeout: Timeout for getting connection from pool
            pool_recycle: Recycle connections after this many seconds
            
        Returns:
            Pool configuration dictionary
        """
        return {
            'poolclass': QueuePool,
            'pool_size': pool_size,
            'max_overflow': max_overflow,
            'pool_timeout': pool_timeout,
            'pool_recycle': pool_recycle,
            'pool_pre_ping': True,  # Verify connections before using
        }
    
    @staticmethod
    def get_pool_status(engine: Engine) -> Dict[str, Any]:
        """
        Get current connection pool status
        
        Args:
            engine: SQLAlchemy engine
            
        Returns:
            Pool status information
        """
        pool = engine.pool
        
        # Handle both callable and property access
        size = pool.size() if callable(pool.size) else pool.size
        
        # Some pool types don't have overflow (e.g., SingletonThreadPool)
        overflow = 0
        if hasattr(pool, 'overflow'):
            overflow = pool.overflow() if callable(pool.overflow) else pool.overflow
        
        # Some pool types don't have checkedin/checkedout (e.g., SingletonThreadPool)
        checked_in = 0
        checked_out = 0
        if hasattr(pool, 'checkedin'):
            checked_in = pool.checkedin()
        if hasattr(pool, 'checkedout'):
            checked_out = pool.checkedout()
        
        return {
            'size': size,
            'checked_in': checked_in,
            'checked_out': checked_out,
            'overflow': overflow,
            'total_connections': size + overflow,
        }


class AsyncQueryHelper:
    """Helper for async database operations"""
    
    @staticmethod
    async def execute_async(session: Session, query: Query) -> List[Any]:
        """
        Execute query asynchronously
        
        Args:
            session: Database session
            query: Query to execute
            
        Returns:
            Query results
        """
        # Note: This is a placeholder for async implementation
        # In production, use SQLAlchemy async session
        return query.all()
    
    @staticmethod
    async def bulk_insert_async(
        session: Session,
        model: Type[DeclarativeMeta],
        data: List[Dict[str, Any]]
    ):
        """
        Bulk insert records asynchronously
        
        Args:
            session: Database session
            model: SQLAlchemy model class
            data: List of dictionaries with record data
        """
        objects = [model(**item) for item in data]
        session.bulk_save_objects(objects)
        await session.commit()


def create_common_indexes(engine: Engine):
    """
    Create common indexes for frequently queried fields
    
    Args:
        engine: SQLAlchemy engine
    """
    index_manager = IndexManager(engine)
    
    # Common indexes for user-related queries
    common_indexes = [
        ('users', ['email'], True),  # Unique index on email
        ('users', ['username'], True),  # Unique index on username
        ('users', ['created_at']),
        ('projects', ['user_id']),
        ('projects', ['created_at']),
        ('projects', ['status']),
        ('calculations', ['project_id']),
        ('calculations', ['created_at']),
        ('price_matrices', ['active']),
        ('price_matrices', ['version']),
    ]
    
    for table, columns, *unique in common_indexes:
        is_unique = unique[0] if unique else False
        try:
            index_manager.create_index(table, columns, unique=is_unique)
        except Exception as e:
            logger.warning(f"Could not create index on {table}({columns}): {e}")


# Query performance monitoring decorator
def monitor_query_performance(query_name: str):
    """
    Decorator to monitor query performance
    
    Args:
        query_name: Name to identify the query
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(
                    f"Query '{query_name}' completed in {duration:.3f}s"
                )
                
                if duration > 1.0:
                    logger.warning(
                        f"Slow query detected: '{query_name}' took {duration:.3f}s"
                    )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Query '{query_name}' failed after {duration:.3f}s: {e}"
                )
                raise
        return wrapper
    return decorator
