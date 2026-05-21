"""
Data Transformation System
Handles complex data transformations during migrations.
"""

import logging
from typing import Any, Dict, List, Callable, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
import json

logger = logging.getLogger(__name__)


class DataTransformer:
    """
    Data transformation engine for migrations
    
    Features:
    - Column transformations
    - Data type conversions
    - Value mapping
    - Batch processing
    - Progress tracking
    - Error handling
    """
    
    def __init__(self, session: Session):
        """
        Initialize data transformer
        
        Args:
            session: Database session
        """
        self.session = session
        self.transformations_applied = 0
        self.errors = []
    
    def transform_column(self, 
                        table: str,
                        column: str,
                        transform_func: Callable[[Any], Any],
                        batch_size: int = 1000,
                        where_clause: Optional[str] = None) -> int:
        """
        Transform values in a column
        
        Args:
            table: Table name
            column: Column name
            transform_func: Function to transform each value
            batch_size: Number of rows to process at once
            where_clause: Optional WHERE clause to filter rows
            
        Returns:
            Number of rows transformed
        """
        logger.info(f"Transforming column {table}.{column}")
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM {table}"
        if where_clause:
            count_query += f" WHERE {where_clause}"
        
        total_rows = self.session.execute(text(count_query)).scalar()
        logger.info(f"Total rows to transform: {total_rows}")
        
        rows_transformed = 0
        offset = 0
        
        while offset < total_rows:
            # Fetch batch
            select_query = f"""
                SELECT id, {column} FROM {table}
                {f'WHERE {where_clause}' if where_clause else ''}
                LIMIT {batch_size} OFFSET {offset}
            """
            
            rows = self.session.execute(text(select_query)).fetchall()
            
            # Transform and update
            for row in rows:
                row_id, value = row
                
                try:
                    transformed_value = transform_func(value)
                    
                    update_query = f"""
                        UPDATE {table}
                        SET {column} = :value
                        WHERE id = :id
                    """
                    
                    self.session.execute(
                        text(update_query),
                        {'value': transformed_value, 'id': row_id}
                    )
                    
                    rows_transformed += 1
                    
                except Exception as e:
                    logger.error(f"Error transforming row {row_id}: {str(e)}")
                    self.errors.append({
                        'table': table,
                        'column': column,
                        'row_id': row_id,
                        'error': str(e)
                    })
            
            # Commit batch
            self.session.commit()
            
            offset += batch_size
            
            # Log progress
            progress = min(100, (offset / total_rows) * 100)
            logger.info(f"Progress: {progress:.1f}% ({rows_transformed}/{total_rows})")
        
        self.transformations_applied += rows_transformed
        logger.info(f"Transformation complete: {rows_transformed} rows transformed")
        
        return rows_transformed
    
    def map_values(self,
                   table: str,
                   column: str,
                   value_map: Dict[Any, Any],
                   default_value: Optional[Any] = None,
                   batch_size: int = 1000) -> int:
        """
        Map values in a column using a dictionary
        
        Args:
            table: Table name
            column: Column name
            value_map: Dictionary mapping old values to new values
            default_value: Default value for unmapped values
            batch_size: Batch size for processing
            
        Returns:
            Number of rows updated
        """
        def map_func(value):
            return value_map.get(value, default_value if default_value is not None else value)
        
        return self.transform_column(table, column, map_func, batch_size)
    
    def convert_type(self,
                     table: str,
                     column: str,
                     target_type: type,
                     batch_size: int = 1000) -> int:
        """
        Convert column data type
        
        Args:
            table: Table name
            column: Column name
            target_type: Target Python type (int, float, str, etc.)
            batch_size: Batch size for processing
            
        Returns:
            Number of rows converted
        """
        def convert_func(value):
            if value is None:
                return None
            try:
                return target_type(value)
            except (ValueError, TypeError):
                logger.warning(f"Could not convert value {value} to {target_type.__name__}")
                return value
        
        return self.transform_column(table, column, convert_func, batch_size)
    
    def normalize_text(self,
                      table: str,
                      column: str,
                      lowercase: bool = False,
                      strip: bool = True,
                      remove_extra_spaces: bool = True,
                      batch_size: int = 1000) -> int:
        """
        Normalize text values
        
        Args:
            table: Table name
            column: Column name
            lowercase: Convert to lowercase
            strip: Strip leading/trailing whitespace
            remove_extra_spaces: Remove extra spaces
            batch_size: Batch size for processing
            
        Returns:
            Number of rows normalized
        """
        def normalize_func(value):
            if not isinstance(value, str):
                return value
            
            result = value
            
            if strip:
                result = result.strip()
            
            if remove_extra_spaces:
                result = ' '.join(result.split())
            
            if lowercase:
                result = result.lower()
            
            return result
        
        return self.transform_column(table, column, normalize_func, batch_size)
    
    def split_column(self,
                     table: str,
                     source_column: str,
                     target_columns: List[str],
                     separator: str = ',',
                     batch_size: int = 1000) -> int:
        """
        Split a column into multiple columns
        
        Args:
            table: Table name
            source_column: Source column to split
            target_columns: List of target column names
            separator: Separator character
            batch_size: Batch size for processing
            
        Returns:
            Number of rows processed
        """
        logger.info(f"Splitting column {table}.{source_column} into {target_columns}")
        
        # Get rows
        select_query = f"SELECT id, {source_column} FROM {table}"
        rows = self.session.execute(text(select_query)).fetchall()
        
        rows_processed = 0
        
        for row in rows:
            row_id, value = row
            
            if not value:
                continue
            
            try:
                # Split value
                parts = str(value).split(separator)
                
                # Update target columns
                for i, target_col in enumerate(target_columns):
                    if i < len(parts):
                        update_query = f"""
                            UPDATE {table}
                            SET {target_col} = :value
                            WHERE id = :id
                        """
                        
                        self.session.execute(
                            text(update_query),
                            {'value': parts[i].strip(), 'id': row_id}
                        )
                
                rows_processed += 1
                
                if rows_processed % batch_size == 0:
                    self.session.commit()
                    logger.info(f"Processed {rows_processed} rows")
                
            except Exception as e:
                logger.error(f"Error splitting row {row_id}: {str(e)}")
                self.errors.append({
                    'table': table,
                    'row_id': row_id,
                    'error': str(e)
                })
        
        self.session.commit()
        logger.info(f"Split complete: {rows_processed} rows processed")
        
        return rows_processed
    
    def merge_columns(self,
                     table: str,
                     source_columns: List[str],
                     target_column: str,
                     separator: str = ' ',
                     batch_size: int = 1000) -> int:
        """
        Merge multiple columns into one
        
        Args:
            table: Table name
            source_columns: List of source columns to merge
            target_column: Target column name
            separator: Separator to use when merging
            batch_size: Batch size for processing
            
        Returns:
            Number of rows processed
        """
        logger.info(f"Merging columns {source_columns} into {table}.{target_column}")
        
        # Build select query
        columns_str = ', '.join(source_columns)
        select_query = f"SELECT id, {columns_str} FROM {table}"
        rows = self.session.execute(text(select_query)).fetchall()
        
        rows_processed = 0
        
        for row in rows:
            row_id = row[0]
            values = row[1:]
            
            try:
                # Merge values
                merged_value = separator.join(
                    str(v) for v in values if v is not None
                )
                
                # Update target column
                update_query = f"""
                    UPDATE {table}
                    SET {target_column} = :value
                    WHERE id = :id
                """
                
                self.session.execute(
                    text(update_query),
                    {'value': merged_value, 'id': row_id}
                )
                
                rows_processed += 1
                
                if rows_processed % batch_size == 0:
                    self.session.commit()
                    logger.info(f"Processed {rows_processed} rows")
                
            except Exception as e:
                logger.error(f"Error merging row {row_id}: {str(e)}")
                self.errors.append({
                    'table': table,
                    'row_id': row_id,
                    'error': str(e)
                })
        
        self.session.commit()
        logger.info(f"Merge complete: {rows_processed} rows processed")
        
        return rows_processed
    
    def migrate_json_data(self,
                         table: str,
                         column: str,
                         transform_func: Callable[[Dict], Dict],
                         batch_size: int = 1000) -> int:
        """
        Transform JSON data in a column
        
        Args:
            table: Table name
            column: Column name containing JSON
            transform_func: Function to transform JSON object
            batch_size: Batch size for processing
            
        Returns:
            Number of rows transformed
        """
        def json_transform(value):
            if not value:
                return value
            
            try:
                # Parse JSON
                data = json.loads(value) if isinstance(value, str) else value
                
                # Transform
                transformed = transform_func(data)
                
                # Serialize back
                return json.dumps(transformed)
                
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON value: {value}")
                return value
        
        return self.transform_column(table, column, json_transform, batch_size)
    
    def deduplicate_rows(self,
                        table: str,
                        unique_columns: List[str],
                        keep: str = 'first') -> int:
        """
        Remove duplicate rows based on unique columns
        
        Args:
            table: Table name
            unique_columns: Columns that should be unique
            keep: Which duplicate to keep ('first' or 'last')
            
        Returns:
            Number of rows deleted
        """
        logger.info(f"Deduplicating table {table} on columns {unique_columns}")
        
        columns_str = ', '.join(unique_columns)
        
        # Find duplicates
        find_duplicates_query = f"""
            SELECT {columns_str}, COUNT(*) as count, 
                   {'MIN' if keep == 'first' else 'MAX'}(id) as keep_id
            FROM {table}
            GROUP BY {columns_str}
            HAVING COUNT(*) > 1
        """
        
        duplicates = self.session.execute(text(find_duplicates_query)).fetchall()
        
        rows_deleted = 0
        
        for dup in duplicates:
            keep_id = dup[-1]
            
            # Build WHERE clause for duplicates
            where_parts = []
            for i, col in enumerate(unique_columns):
                where_parts.append(f"{col} = :{col}")
            
            where_clause = ' AND '.join(where_parts)
            
            # Delete duplicates except the one to keep
            delete_query = f"""
                DELETE FROM {table}
                WHERE {where_clause} AND id != :keep_id
            """
            
            params = {col: dup[i] for i, col in enumerate(unique_columns)}
            params['keep_id'] = keep_id
            
            result = self.session.execute(text(delete_query), params)
            rows_deleted += result.rowcount
        
        self.session.commit()
        logger.info(f"Deduplication complete: {rows_deleted} rows deleted")
        
        return rows_deleted
    
    def get_transformation_summary(self) -> Dict[str, Any]:
        """Get summary of transformations applied"""
        return {
            'transformations_applied': self.transformations_applied,
            'errors_count': len(self.errors),
            'errors': self.errors
        }
