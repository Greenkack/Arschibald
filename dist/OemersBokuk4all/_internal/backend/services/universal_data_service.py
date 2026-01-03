"""
Universal Data Service

Service layer for managing universal data operations including
dynamic key generation, PDF byte generation, and bulk operations.

Requirements: 14.4, 14.7
"""

from typing import List, Dict, Any, Optional, Type
from sqlalchemy.orm import Session
from sqlalchemy import inspect
import json

from backend.core.universal_data import UniversalDataModel
from backend.core.dynamic_keys import KeyPrefix, DynamicKeyIndex
from backend.core.pdf_bytes import PDFMetadata
from backend.models.database_models import UniversalDatabaseModel


class UniversalDataService:
    """
    Service for managing universal data operations.
    
    Provides methods for:
    - Generating dynamic keys for database records
    - Generating PDF bytes for database records
    - Bulk operations on multiple records
    - Key-based lookups and queries
    """
    
    def __init__(self, db: Session):
        """
        Initialize service with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.key_index = DynamicKeyIndex()
    
    def generate_key_for_record(
        self,
        record: UniversalDatabaseModel,
        prefix: KeyPrefix,
        commit: bool = True
    ) -> str:
        """
        Generate and store dynamic key for a database record.
        
        Args:
            record: Database record instance
            prefix: Key prefix to use
            commit: Whether to commit changes to database
        
        Returns:
            Generated dynamic key
        """
        key = record.generate_and_store_key(prefix)
        
        # Add to index
        self.key_index.add(key, record)
        
        if commit:
            self.db.commit()
            self.db.refresh(record)
        
        return key
    
    def generate_pdf_for_record(
        self,
        record: UniversalDatabaseModel,
        metadata: Optional[PDFMetadata] = None,
        commit: bool = True
    ) -> bytes:
        """
        Generate and store PDF bytes for a database record.
        
        Args:
            record: Database record instance
            metadata: Optional PDF metadata
            commit: Whether to commit changes to database
        
        Returns:
            Generated PDF bytes
        """
        pdf_bytes = record.generate_and_store_pdf(metadata)
        
        if commit:
            self.db.commit()
            self.db.refresh(record)
        
        return pdf_bytes
    
    def generate_key_and_pdf(
        self,
        record: UniversalDatabaseModel,
        prefix: KeyPrefix,
        metadata: Optional[PDFMetadata] = None,
        commit: bool = True
    ) -> tuple[str, bytes]:
        """
        Generate both dynamic key and PDF bytes for a record.
        
        Args:
            record: Database record instance
            prefix: Key prefix to use
            metadata: Optional PDF metadata
            commit: Whether to commit changes to database
        
        Returns:
            Tuple of (dynamic_key, pdf_bytes)
        """
        key = self.generate_key_for_record(record, prefix, commit=False)
        pdf_bytes = self.generate_pdf_for_record(record, metadata, commit=False)
        
        if commit:
            self.db.commit()
            self.db.refresh(record)
        
        return key, pdf_bytes
    
    def bulk_generate_keys(
        self,
        records: List[UniversalDatabaseModel],
        prefix: KeyPrefix,
        commit: bool = True
    ) -> List[str]:
        """
        Generate dynamic keys for multiple records.
        
        Args:
            records: List of database record instances
            prefix: Key prefix to use for all records
            commit: Whether to commit changes to database
        
        Returns:
            List of generated dynamic keys
        """
        keys = []
        
        for record in records:
            key = record.generate_and_store_key(prefix)
            keys.append(key)
            self.key_index.add(key, record)
        
        if commit:
            self.db.commit()
            for record in records:
                self.db.refresh(record)
        
        return keys
    
    def bulk_generate_pdfs(
        self,
        records: List[UniversalDatabaseModel],
        metadata: Optional[PDFMetadata] = None,
        commit: bool = True
    ) -> List[bytes]:
        """
        Generate PDF bytes for multiple records.
        
        Args:
            records: List of database record instances
            metadata: Optional PDF metadata (same for all)
            commit: Whether to commit changes to database
        
        Returns:
            List of generated PDF bytes
        """
        pdf_list = []
        
        for record in records:
            pdf_bytes = record.generate_and_store_pdf(metadata)
            pdf_list.append(pdf_bytes)
        
        if commit:
            self.db.commit()
            for record in records:
                self.db.refresh(record)
        
        return pdf_list
    
    def bulk_generate_keys_and_pdfs(
        self,
        records: List[UniversalDatabaseModel],
        prefix: KeyPrefix,
        metadata: Optional[PDFMetadata] = None,
        commit: bool = True
    ) -> List[tuple[str, bytes]]:
        """
        Generate both keys and PDFs for multiple records.
        
        Args:
            records: List of database record instances
            prefix: Key prefix to use for all records
            metadata: Optional PDF metadata (same for all)
            commit: Whether to commit changes to database
        
        Returns:
            List of tuples (dynamic_key, pdf_bytes)
        """
        results = []
        
        for record in records:
            key = record.generate_and_store_key(prefix)
            pdf_bytes = record.generate_and_store_pdf(metadata)
            results.append((key, pdf_bytes))
            self.key_index.add(key, record)
        
        if commit:
            self.db.commit()
            for record in records:
                self.db.refresh(record)
        
        return results
    
    def get_by_dynamic_key(
        self,
        model_class: Type[UniversalDatabaseModel],
        key: str
    ) -> Optional[UniversalDatabaseModel]:
        """
        Get a record by its dynamic key.
        
        Args:
            model_class: Model class to query
            key: Dynamic key to search for
        
        Returns:
            Record instance or None if not found
        """
        # Try index first
        record = self.key_index.get(key)
        if record:
            return record
        
        # Fall back to database query
        return self.db.query(model_class).filter(
            model_class.dynamic_key == key
        ).first()
    
    def get_by_prefix(
        self,
        model_class: Type[UniversalDatabaseModel],
        prefix: str
    ) -> List[UniversalDatabaseModel]:
        """
        Get all records with a specific key prefix.
        
        Args:
            model_class: Model class to query
            prefix: Key prefix to search for
        
        Returns:
            List of matching records
        """
        return self.db.query(model_class).filter(
            model_class.dynamic_key.like(f"{prefix}_%")
        ).all()
    
    def get_records_with_pdf(
        self,
        model_class: Type[UniversalDatabaseModel]
    ) -> List[UniversalDatabaseModel]:
        """
        Get all records that have PDF bytes stored.
        
        Args:
            model_class: Model class to query
        
        Returns:
            List of records with PDF bytes
        """
        return self.db.query(model_class).filter(
            model_class.pdf_bytes.isnot(None)
        ).all()
    
    def get_records_without_pdf(
        self,
        model_class: Type[UniversalDatabaseModel]
    ) -> List[UniversalDatabaseModel]:
        """
        Get all records that don't have PDF bytes stored.
        
        Args:
            model_class: Model class to query
        
        Returns:
            List of records without PDF bytes
        """
        return self.db.query(model_class).filter(
            model_class.pdf_bytes.is_(None)
        ).all()
    
    def regenerate_pdf(
        self,
        record: UniversalDatabaseModel,
        metadata: Optional[PDFMetadata] = None,
        commit: bool = True
    ) -> bytes:
        """
        Regenerate PDF bytes for a record (overwrites existing).
        
        Args:
            record: Database record instance
            metadata: Optional PDF metadata
            commit: Whether to commit changes to database
        
        Returns:
            Newly generated PDF bytes
        """
        return self.generate_pdf_for_record(record, metadata, commit)
    
    def delete_pdf(
        self,
        record: UniversalDatabaseModel,
        commit: bool = True
    ) -> bool:
        """
        Delete PDF bytes from a record.
        
        Args:
            record: Database record instance
            commit: Whether to commit changes to database
        
        Returns:
            True if PDF was deleted, False if no PDF existed
        """
        if not record.has_pdf():
            return False
        
        record.pdf_bytes = None
        
        if commit:
            self.db.commit()
            self.db.refresh(record)
        
        return True
    
    def get_formatted_data(
        self,
        record: UniversalDatabaseModel,
        locale: str = 'de-DE',
        include_keys: bool = True
    ) -> Dict[str, Any]:
        """
        Get formatted data from a record.
        
        Args:
            record: Database record instance
            locale: Locale for formatting
            include_keys: Whether to include dynamic key info
        
        Returns:
            Dictionary with formatted data
        """
        return record.to_dict(
            include_keys=include_keys,
            formatted=True,
            locale=locale
        )
    
    def export_to_json(
        self,
        record: UniversalDatabaseModel,
        include_pdf: bool = False
    ) -> str:
        """
        Export record to JSON string.
        
        Args:
            record: Database record instance
            include_pdf: Whether to include PDF bytes (base64 encoded)
        
        Returns:
            JSON string
        """
        data = record.to_json_serializable()
        
        if not include_pdf and 'pdf_bytes' in data:
            del data['pdf_bytes']
        elif include_pdf and record.has_pdf():
            import base64
            data['pdf_bytes'] = base64.b64encode(record.pdf_bytes).decode('utf-8')
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def get_statistics(
        self,
        model_class: Type[UniversalDatabaseModel]
    ) -> Dict[str, Any]:
        """
        Get statistics about universal data usage for a model.
        
        Args:
            model_class: Model class to analyze
        
        Returns:
            Dictionary with statistics
        """
        total = self.db.query(model_class).count()
        with_keys = self.db.query(model_class).filter(
            model_class.dynamic_key.isnot(None)
        ).count()
        with_pdfs = self.db.query(model_class).filter(
            model_class.pdf_bytes.isnot(None)
        ).count()
        
        return {
            'model': model_class.__name__,
            'total_records': total,
            'records_with_keys': with_keys,
            'records_without_keys': total - with_keys,
            'records_with_pdfs': with_pdfs,
            'records_without_pdfs': total - with_pdfs,
            'key_coverage_percent': (with_keys / total * 100) if total > 0 else 0,
            'pdf_coverage_percent': (with_pdfs / total * 100) if total > 0 else 0
        }
    
    def rebuild_key_index(
        self,
        model_class: Type[UniversalDatabaseModel]
    ) -> int:
        """
        Rebuild the in-memory key index from database.
        
        Args:
            model_class: Model class to index
        
        Returns:
            Number of keys indexed
        """
        records = self.db.query(model_class).filter(
            model_class.dynamic_key.isnot(None)
        ).all()
        
        count = 0
        for record in records:
            self.key_index.add(record.dynamic_key, record)
            count += 1
        
        return count


class BulkPDFGenerator:
    """
    Specialized service for bulk PDF generation with progress tracking.
    """
    
    def __init__(self, db: Session):
        """
        Initialize bulk PDF generator.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.service = UniversalDataService(db)
    
    def generate_pdfs_batch(
        self,
        records: List[UniversalDatabaseModel],
        batch_size: int = 100,
        metadata: Optional[PDFMetadata] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Generate PDFs in batches with progress tracking.
        
        Args:
            records: List of records to process
            batch_size: Number of records per batch
            metadata: Optional PDF metadata
            progress_callback: Optional callback function(current, total)
        
        Returns:
            Dictionary with generation results
        """
        total = len(records)
        generated = 0
        errors = []
        
        for i in range(0, total, batch_size):
            batch = records[i:i + batch_size]
            
            try:
                self.service.bulk_generate_pdfs(batch, metadata, commit=True)
                generated += len(batch)
                
                if progress_callback:
                    progress_callback(generated, total)
                    
            except Exception as e:
                error_msg = f"Error in batch {i//batch_size + 1}: {str(e)}"
                errors.append(error_msg)
                print(error_msg)
        
        return {
            'total_records': total,
            'generated': generated,
            'failed': total - generated,
            'errors': errors,
            'success_rate': (generated / total * 100) if total > 0 else 0
        }
    
    def regenerate_all_pdfs(
        self,
        model_class: Type[UniversalDatabaseModel],
        batch_size: int = 100,
        metadata: Optional[PDFMetadata] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Regenerate PDFs for all records of a model.
        
        Args:
            model_class: Model class to process
            batch_size: Number of records per batch
            metadata: Optional PDF metadata
            progress_callback: Optional callback function(current, total)
        
        Returns:
            Dictionary with generation results
        """
        records = self.db.query(model_class).all()
        return self.generate_pdfs_batch(
            records,
            batch_size,
            metadata,
            progress_callback
        )
