"""
Database Optimization Service

Provides comprehensive database optimization including:
- Query optimization and analysis
- Index management and recommendations
- Table partitioning strategies
- Data archiving and cleanup
- Vacuum and analyze automation
- Performance monitoring and metrics

Requirements: 8.4
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy import text, inspect, MetaData, Table
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
import logging
import json
import time

logger = logging.getLogger(__name__)


class DatabaseOptimizationService:
    """Service for database optimization and performance management"""
    
    def __init__(self, engine: Engine):
        """
        Initialize database optimization service
        
        Args:
            engine: SQLAlchemy engine instance
        """
        self.engine = engine
        self.metadata = MetaData()
        self.metadata.reflect(bind=engine)
        
    # ==================== Query Optimization ====================
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze query performance and provide optimization suggestions
        
        Args:
            query: SQL query to analyze
            
        Returns:
            Dictionary with analysis results and suggestions
        """
        try:
            with self.engine.connect() as conn:
                # Get query plan
                explain_query = f"EXPLAIN QUERY PLAN {query}"
                result = conn.execute(text(explain_query))
                plan = [dict(row._mapping) for row in result]
                
                # Measure execution time
                start_time = time.time()
                conn.execute(text(query))
                execution_time = time.time() - start_time
                
                # Analyze plan for issues
                issues = self._analyze_query_plan(plan)
                suggestions = self._generate_query_suggestions(plan, issues)
                
                return {
                    "query": query,
                    "execution_time_ms": round(execution_time * 1000, 2),
                    "query_plan": plan,
                    "issues": issues,
                    "suggestions": suggestions,
                    "analyzed_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error analyzing query: {e}")
            return {
                "error": str(e),
                "query": query
            }
    
    def _analyze_query_plan(self, plan: List[Dict]) -> List[str]:
        """Analyze query plan for performance issues"""
        issues = []
        
        for step in plan:
            detail = step.get('detail', '').lower()
            
            # Check for full table scans
            if 'scan table' in detail and 'using index' not in detail:
                issues.append(f"Full table scan detected: {detail}")
            
            # Check for temporary tables
            if 'use temp b-tree' in detail:
                issues.append(f"Temporary B-tree created: {detail}")
            
            # Check for sorting
            if 'use temp b-tree for order by' in detail:
                issues.append(f"Sorting requires temporary storage: {detail}")
        
        return issues
    
    def _generate_query_suggestions(
        self, 
        plan: List[Dict], 
        issues: List[str]
    ) -> List[str]:
        """Generate optimization suggestions based on query plan"""
        suggestions = []
        
        if any('full table scan' in issue.lower() for issue in issues):
            suggestions.append("Consider adding indexes on frequently queried columns")
        
        if any('temporary' in issue.lower() for issue in issues):
            suggestions.append("Consider optimizing JOIN conditions or adding covering indexes")
        
        if any('sorting' in issue.lower() for issue in issues):
            suggestions.append("Consider adding index on ORDER BY columns")
        
        return suggestions
    
    def get_slow_queries(
        self, 
        threshold_ms: float = 1000.0,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get list of slow queries from query log
        
        Args:
            threshold_ms: Minimum execution time in milliseconds
            limit: Maximum number of queries to return
            
        Returns:
            List of slow queries with execution statistics
        """
        # Note: This would require query logging to be enabled
        # For SQLite, we'd need to implement custom logging
        logger.info(f"Retrieving slow queries (threshold: {threshold_ms}ms)")
        
        # Placeholder - would be implemented with actual query logging
        return []
    
    # ==================== Index Management ====================
    
    def get_indexes(self, table_name: Optional[str] = None) -> Dict[str, List[Dict]]:
        """
        Get all indexes in database or for specific table
        
        Args:
            table_name: Optional table name to filter indexes
            
        Returns:
            Dictionary mapping table names to their indexes
        """
        try:
            inspector = inspect(self.engine)
            indexes = {}
            
            tables = [table_name] if table_name else inspector.get_table_names()
            
            for table in tables:
                table_indexes = inspector.get_indexes(table)
                indexes[table] = [
                    {
                        "name": idx['name'],
                        "columns": idx['column_names'],
                        "unique": idx.get('unique', False)
                    }
                    for idx in table_indexes
                ]
            
            return indexes
            
        except Exception as e:
            logger.error(f"Error getting indexes: {e}")
            return {}
    
    def analyze_index_usage(self, table_name: str) -> Dict[str, Any]:
        """
        Analyze index usage and effectiveness for a table
        
        Args:
            table_name: Name of table to analyze
            
        Returns:
            Dictionary with index usage statistics and recommendations
        """
        try:
            indexes = self.get_indexes(table_name)
            table_indexes = indexes.get(table_name, [])
            
            # Get table statistics
            with self.engine.connect() as conn:
                # Get row count
                count_query = f"SELECT COUNT(*) as count FROM {table_name}"
                result = conn.execute(text(count_query))
                row_count = result.scalar()
                
                # Analyze each index
                index_analysis = []
                for idx in table_indexes:
                    analysis = {
                        "index_name": idx['name'],
                        "columns": idx['columns'],
                        "unique": idx['unique'],
                        "estimated_size_kb": self._estimate_index_size(
                            table_name, 
                            idx['columns'], 
                            row_count
                        )
                    }
                    index_analysis.append(analysis)
            
            recommendations = self._generate_index_recommendations(
                table_name,
                table_indexes,
                row_count
            )
            
            return {
                "table_name": table_name,
                "row_count": row_count,
                "indexes": index_analysis,
                "recommendations": recommendations,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing index usage: {e}")
            return {"error": str(e)}
    
    def _estimate_index_size(
        self, 
        table_name: str, 
        columns: List[str], 
        row_count: int
    ) -> float:
        """Estimate index size in KB"""
        # Rough estimation: 8 bytes per row per column + overhead
        bytes_per_row = len(columns) * 8 + 16  # 16 bytes overhead
        total_bytes = bytes_per_row * row_count
        return round(total_bytes / 1024, 2)
    
    def _generate_index_recommendations(
        self,
        table_name: str,
        indexes: List[Dict],
        row_count: int
    ) -> List[str]:
        """Generate index recommendations"""
        recommendations = []
        
        # Check if table has any indexes
        if not indexes:
            recommendations.append(
                f"Table {table_name} has no indexes. Consider adding indexes on frequently queried columns."
            )
        
        # Check for tables with many rows but few indexes
        if row_count > 10000 and len(indexes) < 2:
            recommendations.append(
                f"Table {table_name} has {row_count} rows but only {len(indexes)} index(es). "
                "Consider adding more indexes for better query performance."
            )
        
        return recommendations
    
    def create_index(
        self,
        table_name: str,
        columns: List[str],
        index_name: Optional[str] = None,
        unique: bool = False
    ) -> Dict[str, Any]:
        """
        Create an index on specified columns
        
        Args:
            table_name: Name of table
            columns: List of column names
            index_name: Optional custom index name
            unique: Whether index should be unique
            
        Returns:
            Dictionary with creation result
        """
        try:
            if not index_name:
                index_name = f"idx_{table_name}_{'_'.join(columns)}"
            
            unique_clause = "UNIQUE" if unique else ""
            columns_str = ", ".join(columns)
            
            create_sql = f"""
                CREATE {unique_clause} INDEX IF NOT EXISTS {index_name}
                ON {table_name} ({columns_str})
            """
            
            with self.engine.connect() as conn:
                conn.execute(text(create_sql))
                conn.commit()
            
            logger.info(f"Created index {index_name} on {table_name}({columns_str})")
            
            return {
                "success": True,
                "index_name": index_name,
                "table_name": table_name,
                "columns": columns,
                "unique": unique
            }
            
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def drop_index(self, index_name: str) -> Dict[str, Any]:
        """
        Drop an index
        
        Args:
            index_name: Name of index to drop
            
        Returns:
            Dictionary with drop result
        """
        try:
            drop_sql = f"DROP INDEX IF EXISTS {index_name}"
            
            with self.engine.connect() as conn:
                conn.execute(text(drop_sql))
                conn.commit()
            
            logger.info(f"Dropped index {index_name}")
            
            return {
                "success": True,
                "index_name": index_name
            }
            
        except Exception as e:
            logger.error(f"Error dropping index: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ==================== Table Partitioning ====================
    
    def analyze_partitioning_candidates(self) -> List[Dict[str, Any]]:
        """
        Analyze tables that could benefit from partitioning
        
        Returns:
            List of tables with partitioning recommendations
        """
        try:
            inspector = inspect(self.engine)
            candidates = []
            
            for table_name in inspector.get_table_names():
                with self.engine.connect() as conn:
                    # Get row count
                    count_query = f"SELECT COUNT(*) as count FROM {table_name}"
                    result = conn.execute(text(count_query))
                    row_count = result.scalar()
                    
                    # Get columns
                    columns = inspector.get_columns(table_name)
                    
                    # Check for date/timestamp columns
                    date_columns = [
                        col['name'] for col in columns
                        if 'date' in col['name'].lower() or 'time' in col['name'].lower()
                    ]
                    
                    # Recommend partitioning for large tables with date columns
                    if row_count > 100000 and date_columns:
                        candidates.append({
                            "table_name": table_name,
                            "row_count": row_count,
                            "partition_columns": date_columns,
                            "strategy": "range",
                            "reason": f"Large table ({row_count} rows) with date columns"
                        })
            
            return candidates
            
        except Exception as e:
            logger.error(f"Error analyzing partitioning candidates: {e}")
            return []
    
    # ==================== Data Archiving ====================
    
    def analyze_archiving_candidates(
        self,
        age_threshold_days: int = 365
    ) -> List[Dict[str, Any]]:
        """
        Analyze tables that have old data suitable for archiving
        
        Args:
            age_threshold_days: Age threshold for archiving
            
        Returns:
            List of tables with archiving recommendations
        """
        try:
            inspector = inspect(self.engine)
            candidates = []
            
            for table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                
                # Find date columns
                date_columns = [
                    col['name'] for col in columns
                    if 'date' in col['name'].lower() or 
                       'created' in col['name'].lower() or
                       'updated' in col['name'].lower()
                ]
                
                if not date_columns:
                    continue
                
                # Check for old records
                date_col = date_columns[0]
                threshold_date = datetime.now() - timedelta(days=age_threshold_days)
                
                with self.engine.connect() as conn:
                    count_query = f"""
                        SELECT COUNT(*) as count 
                        FROM {table_name}
                        WHERE {date_col} < :threshold
                    """
                    result = conn.execute(
                        text(count_query),
                        {"threshold": threshold_date}
                    )
                    old_count = result.scalar()
                    
                    if old_count > 0:
                        candidates.append({
                            "table_name": table_name,
                            "date_column": date_col,
                            "old_records_count": old_count,
                            "threshold_date": threshold_date.isoformat(),
                            "recommendation": f"Archive {old_count} records older than {age_threshold_days} days"
                        })
            
            return candidates
            
        except Exception as e:
            logger.error(f"Error analyzing archiving candidates: {e}")
            return []
    
    def archive_old_data(
        self,
        table_name: str,
        date_column: str,
        threshold_date: datetime,
        archive_table_suffix: str = "_archive"
    ) -> Dict[str, Any]:
        """
        Archive old data to separate table
        
        Args:
            table_name: Source table name
            date_column: Column to use for date filtering
            threshold_date: Date threshold for archiving
            archive_table_suffix: Suffix for archive table name
            
        Returns:
            Dictionary with archiving results
        """
        try:
            archive_table = f"{table_name}{archive_table_suffix}"
            
            with self.engine.connect() as conn:
                # Create archive table if it doesn't exist
                create_archive = f"""
                    CREATE TABLE IF NOT EXISTS {archive_table}
                    AS SELECT * FROM {table_name} WHERE 1=0
                """
                conn.execute(text(create_archive))
                
                # Move old records to archive
                insert_archive = f"""
                    INSERT INTO {archive_table}
                    SELECT * FROM {table_name}
                    WHERE {date_column} < :threshold
                """
                result = conn.execute(
                    text(insert_archive),
                    {"threshold": threshold_date}
                )
                archived_count = result.rowcount
                
                # Delete archived records from main table
                delete_old = f"""
                    DELETE FROM {table_name}
                    WHERE {date_column} < :threshold
                """
                conn.execute(text(delete_old), {"threshold": threshold_date})
                
                conn.commit()
            
            logger.info(f"Archived {archived_count} records from {table_name}")
            
            return {
                "success": True,
                "table_name": table_name,
                "archive_table": archive_table,
                "archived_count": archived_count,
                "threshold_date": threshold_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error archiving data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ==================== Vacuum and Analyze ====================
    
    def vacuum_database(self) -> Dict[str, Any]:
        """
        Run VACUUM to reclaim space and defragment database
        
        Returns:
            Dictionary with vacuum results
        """
        try:
            start_time = time.time()
            
            with self.engine.connect() as conn:
                # Get database size before vacuum
                size_before = self._get_database_size(conn)
                
                # Run VACUUM
                conn.execute(text("VACUUM"))
                
                # Get database size after vacuum
                size_after = self._get_database_size(conn)
            
            duration = time.time() - start_time
            space_freed = size_before - size_after
            
            logger.info(f"VACUUM completed in {duration:.2f}s, freed {space_freed} bytes")
            
            return {
                "success": True,
                "duration_seconds": round(duration, 2),
                "size_before_bytes": size_before,
                "size_after_bytes": size_after,
                "space_freed_bytes": space_freed,
                "space_freed_mb": round(space_freed / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"Error running VACUUM: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_tables(
        self,
        table_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run ANALYZE to update statistics for query optimizer
        
        Args:
            table_names: Optional list of specific tables to analyze
            
        Returns:
            Dictionary with analyze results
        """
        try:
            start_time = time.time()
            
            with self.engine.connect() as conn:
                if table_names:
                    for table in table_names:
                        conn.execute(text(f"ANALYZE {table}"))
                else:
                    conn.execute(text("ANALYZE"))
            
            duration = time.time() - start_time
            
            logger.info(f"ANALYZE completed in {duration:.2f}s")
            
            return {
                "success": True,
                "duration_seconds": round(duration, 2),
                "tables_analyzed": table_names or "all"
            }
            
        except Exception as e:
            logger.error(f"Error running ANALYZE: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_database_size(self, conn) -> int:
        """Get database file size in bytes"""
        try:
            result = conn.execute(text("PRAGMA page_count"))
            page_count = result.scalar()
            
            result = conn.execute(text("PRAGMA page_size"))
            page_size = result.scalar()
            
            return page_count * page_size
        except:
            return 0
    
    def schedule_maintenance(
        self,
        vacuum_enabled: bool = True,
        analyze_enabled: bool = True,
        vacuum_schedule: str = "weekly",
        analyze_schedule: str = "daily"
    ) -> Dict[str, Any]:
        """
        Configure automatic maintenance schedule
        
        Args:
            vacuum_enabled: Enable automatic VACUUM
            analyze_enabled: Enable automatic ANALYZE
            vacuum_schedule: Schedule for VACUUM (daily, weekly, monthly)
            analyze_schedule: Schedule for ANALYZE (daily, weekly)
            
        Returns:
            Dictionary with schedule configuration
        """
        config = {
            "vacuum": {
                "enabled": vacuum_enabled,
                "schedule": vacuum_schedule
            },
            "analyze": {
                "enabled": analyze_enabled,
                "schedule": analyze_schedule
            },
            "configured_at": datetime.now().isoformat()
        }
        
        logger.info(f"Maintenance schedule configured: {config}")
        
        return config
    
    # ==================== Performance Monitoring ====================
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive database performance metrics
        
        Returns:
            Dictionary with performance metrics
        """
        try:
            with self.engine.connect() as conn:
                # Get database size
                db_size = self._get_database_size(conn)
                
                # Get table statistics
                inspector = inspect(self.engine)
                table_stats = []
                
                for table_name in inspector.get_table_names():
                    count_query = f"SELECT COUNT(*) as count FROM {table_name}"
                    result = conn.execute(text(count_query))
                    row_count = result.scalar()
                    
                    table_stats.append({
                        "table_name": table_name,
                        "row_count": row_count
                    })
                
                # Get index count
                total_indexes = sum(
                    len(self.get_indexes(table)) 
                    for table in inspector.get_table_names()
                )
                
                return {
                    "database_size_bytes": db_size,
                    "database_size_mb": round(db_size / (1024 * 1024), 2),
                    "table_count": len(table_stats),
                    "total_rows": sum(t['row_count'] for t in table_stats),
                    "total_indexes": total_indexes,
                    "table_statistics": table_stats,
                    "measured_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {"error": str(e)}
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive optimization report
        
        Returns:
            Dictionary with complete optimization analysis
        """
        try:
            report = {
                "generated_at": datetime.now().isoformat(),
                "performance_metrics": self.get_performance_metrics(),
                "index_analysis": {},
                "partitioning_candidates": self.analyze_partitioning_candidates(),
                "archiving_candidates": self.analyze_archiving_candidates(),
                "recommendations": []
            }
            
            # Analyze indexes for each table
            inspector = inspect(self.engine)
            for table_name in inspector.get_table_names():
                report["index_analysis"][table_name] = self.analyze_index_usage(table_name)
            
            # Generate overall recommendations
            if report["partitioning_candidates"]:
                report["recommendations"].append(
                    f"Consider partitioning {len(report['partitioning_candidates'])} large tables"
                )
            
            if report["archiving_candidates"]:
                total_archivable = sum(
                    c['old_records_count'] 
                    for c in report['archiving_candidates']
                )
                report["recommendations"].append(
                    f"Archive {total_archivable} old records to improve performance"
                )
            
            # Check if VACUUM is needed
            db_size_mb = report["performance_metrics"].get("database_size_mb", 0)
            if db_size_mb > 100:
                report["recommendations"].append(
                    "Run VACUUM to reclaim space and optimize database"
                )
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating optimization report: {e}")
            return {"error": str(e)}
