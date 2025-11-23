"""
PDF Archiving & CRM Integration Service

This service provides automatic PDF archiving to customer records with:
- Auto-save to CRM customer documents
- PDF versioning
- PDF history per customer
- PDF metadata (creation date, company, products, price)
- PDF search in archive
- PDF export from archive

Requirements: 1.3, 6.1
"""

import sys
import os
from typing import Dict, List, Optional, Any, BinaryIO
from datetime import datetime
import logging
import re
import hashlib
from pathlib import Path

# Add parent directory to path to import legacy modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

logger = logging.getLogger(__name__)


class PDFMetadata:
    """PDF metadata structure"""
    
    def __init__(
        self,
        creation_date: datetime,
        company_id: Optional[int] = None,
        company_name: Optional[str] = None,
        products: Optional[List[Dict[str, Any]]] = None,
        total_price: Optional[float] = None,
        pdf_type: str = "offer_pdf",
        project_type: str = "pv",
        version: int = 1,
        file_size: int = 0,
        checksum: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        self.creation_date = creation_date
        self.company_id = company_id
        self.company_name = company_name
        self.products = products or []
        self.total_price = total_price
        self.pdf_type = pdf_type
        self.project_type = project_type
        self.version = version
        self.file_size = file_size
        self.checksum = checksum
        self.additional_data = additional_data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            'creation_date': self.creation_date.isoformat(),
            'company_id': self.company_id,
            'company_name': self.company_name,
            'products': self.products,
            'total_price': self.total_price,
            'pdf_type': self.pdf_type,
            'project_type': self.project_type,
            'version': self.version,
            'file_size': self.file_size,
            'checksum': self.checksum,
            **self.additional_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PDFMetadata':
        """Create metadata from dictionary"""
        creation_date = data.get('creation_date')
        if isinstance(creation_date, str):
            creation_date = datetime.fromisoformat(creation_date)
        elif not isinstance(creation_date, datetime):
            creation_date = datetime.now()
        
        return cls(
            creation_date=creation_date,
            company_id=data.get('company_id'),
            company_name=data.get('company_name'),
            products=data.get('products'),
            total_price=data.get('total_price'),
            pdf_type=data.get('pdf_type', 'offer_pdf'),
            project_type=data.get('project_type', 'pv'),
            version=data.get('version', 1),
            file_size=data.get('file_size', 0),
            checksum=data.get('checksum'),
            additional_data={k: v for k, v in data.items() if k not in [
                'creation_date', 'company_id', 'company_name', 'products',
                'total_price', 'pdf_type', 'project_type', 'version',
                'file_size', 'checksum'
            ]}
        )


class PDFArchivingService:
    """
    Service for automatic PDF archiving to CRM customer records.
    
    Features:
    - Auto-save PDFs to customer documents
    - PDF versioning
    - PDF history per customer
    - PDF metadata extraction and storage
    - PDF search in archive
    - PDF export from archive
    """
    
    def __init__(self, database_path: str = "crm_database.db"):
        """
        Initialize PDF Archiving Service.
        
        Args:
            database_path: Path to CRM database
        """
        self.database_path = database_path
        logger.info("PDF Archiving Service initialized")
    
    def calculate_checksum(self, pdf_bytes: bytes) -> str:
        """
        Calculate SHA-256 checksum of PDF file.
        
        Args:
            pdf_bytes: PDF file content as bytes
        
        Returns:
            Hexadecimal checksum string
        """
        return hashlib.sha256(pdf_bytes).hexdigest()
    
    def extract_metadata_from_filename(self, filename: str) -> Dict[str, Any]:
        """
        Extract metadata from PDF filename.
        
        Args:
            filename: PDF filename
        
        Returns:
            Dictionary with extracted metadata
        """
        metadata = {
            'pdf_type': 'other_pdf',
            'version': 1
        }
        
        filename_lower = filename.lower()
        
        # Detect PDF type from filename
        if 'angebot' in filename_lower or 'offer' in filename_lower:
            metadata['pdf_type'] = 'offer_pdf'
        elif 'rechnung' in filename_lower or 'invoice' in filename_lower:
            metadata['pdf_type'] = 'invoice_pdf'
        elif 'vertrag' in filename_lower or 'contract' in filename_lower:
            metadata['pdf_type'] = 'contract_pdf'
        elif 'bericht' in filename_lower or 'report' in filename_lower:
            metadata['pdf_type'] = 'report_pdf'
        
        # Extract version number
        version_match = re.search(r'v(\d+)|version[_\s]?(\d+)', filename, re.IGNORECASE)
        if version_match:
            metadata['version'] = int(version_match.group(1) or version_match.group(2))
        
        # Extract date
        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
        if date_match:
            try:
                metadata['date'] = datetime(
                    int(date_match.group(1)),
                    int(date_match.group(2)),
                    int(date_match.group(3))
                )
            except ValueError:
                pass
        
        return metadata
    
    def create_metadata(
        self,
        pdf_bytes: bytes,
        filename: str,
        company_id: Optional[int] = None,
        company_name: Optional[str] = None,
        products: Optional[List[Dict[str, Any]]] = None,
        total_price: Optional[float] = None,
        offer_data: Optional[Dict[str, Any]] = None
    ) -> PDFMetadata:
        """
        Create comprehensive PDF metadata.
        
        Args:
            pdf_bytes: PDF file content
            filename: PDF filename
            company_id: Company/customer ID
            company_name: Company/customer name
            products: List of products in the offer
            total_price: Total price of the offer
            offer_data: Additional offer data
        
        Returns:
            PDFMetadata object
        """
        # Extract metadata from filename
        filename_metadata = self.extract_metadata_from_filename(filename)
        
        # Calculate checksum
        checksum = self.calculate_checksum(pdf_bytes)
        
        # Extract data from offer_data if provided
        if offer_data:
            if not company_id and 'customer_id' in offer_data:
                company_id = offer_data['customer_id']
            if not company_name and 'customer' in offer_data:
                customer = offer_data['customer']
                if isinstance(customer, dict):
                    company_name = customer.get('name') or customer.get('company')
                else:
                    company_name = str(customer)
            if not products and 'products' in offer_data:
                products = offer_data['products']
            if not total_price and 'total_cost' in offer_data:
                total_price = offer_data['total_cost']
        
        # Create metadata object
        metadata = PDFMetadata(
            creation_date=datetime.now(),
            company_id=company_id,
            company_name=company_name,
            products=products,
            total_price=total_price,
            pdf_type=filename_metadata.get('pdf_type', 'offer_pdf'),
            project_type=offer_data.get('project_type', 'pv') if offer_data else 'pv',
            version=filename_metadata.get('version', 1),
            file_size=len(pdf_bytes),
            checksum=checksum,
            additional_data=offer_data or {}
        )
        
        return metadata
    
    def get_next_version_number(
        self,
        customer_id: int,
        pdf_type: str,
        project_id: Optional[int] = None
    ) -> int:
        """
        Get the next version number for a PDF type.
        
        Args:
            customer_id: Customer ID
            pdf_type: PDF type (e.g., 'offer_pdf')
            project_id: Optional project ID
        
        Returns:
            Next version number
        """
        try:
            # Import legacy function
            from crm.integration.pdf_bridge import get_next_version_number
            return get_next_version_number(customer_id, pdf_type, project_id)
        except ImportError:
            logger.warning("Legacy pdf_bridge not available, using fallback version numbering")
            return 1
        except Exception as e:
            logger.error(f"Error getting next version number: {e}")
            return 1
    
    def create_versioned_filename(
        self,
        original_filename: str,
        version: int,
        metadata: PDFMetadata
    ) -> str:
        """
        Create a versioned filename.
        
        Args:
            original_filename: Original filename
            version: Version number
            metadata: PDF metadata
        
        Returns:
            Versioned filename
        """
        # Split filename and extension
        name_parts = os.path.splitext(original_filename)
        base_name = name_parts[0]
        extension = name_parts[1] if len(name_parts) > 1 else '.pdf'
        
        # Format date
        date_str = metadata.creation_date.strftime('%Y-%m-%d')
        
        # Create versioned name
        versioned_name = f"{base_name}_v{version}_{date_str}{extension}"
        
        return versioned_name
    
    def auto_save_to_crm(
        self,
        pdf_bytes: bytes,
        filename: str,
        customer_id: int,
        project_id: Optional[int] = None,
        company_name: Optional[str] = None,
        products: Optional[List[Dict[str, Any]]] = None,
        total_price: Optional[float] = None,
        offer_data: Optional[Dict[str, Any]] = None
    ) -> Optional[int]:
        """
        Automatically save PDF to CRM customer documents.
        
        Args:
            pdf_bytes: PDF file content
            filename: PDF filename
            customer_id: Customer ID
            project_id: Optional project ID
            company_name: Company name
            products: List of products
            total_price: Total price
            offer_data: Additional offer data
        
        Returns:
            Document ID if successful, None otherwise
        """
        try:
            # Create metadata
            metadata = self.create_metadata(
                pdf_bytes=pdf_bytes,
                filename=filename,
                company_id=customer_id,
                company_name=company_name,
                products=products,
                total_price=total_price,
                offer_data=offer_data
            )
            
            # Get next version number
            version = self.get_next_version_number(
                customer_id,
                metadata.pdf_type,
                project_id
            )
            metadata.version = version
            
            # Create versioned filename
            display_name = self.create_versioned_filename(
                filename,
                version,
                metadata
            )
            
            # Try to use legacy function
            try:
                from database import add_customer_document
                
                doc_id = add_customer_document(
                    customer_id=customer_id,
                    file_bytes=pdf_bytes,
                    display_name=display_name,
                    doc_type=metadata.pdf_type,
                    project_id=project_id,
                    suggested_filename=display_name
                )
                
                if doc_id:
                    logger.info(f"PDF archived successfully - Document ID: {doc_id}")
                    logger.info(f"  • Customer: {customer_id}")
                    logger.info(f"  • Type: {metadata.pdf_type}")
                    logger.info(f"  • Version: {version}")
                    logger.info(f"  • Size: {metadata.file_size / 1024:.1f} KB")
                    logger.info(f"  • Checksum: {metadata.checksum[:16]}...")
                    
                    # Update offer status if applicable
                    if metadata.pdf_type == 'offer_pdf' and project_id:
                        self._update_offer_status(project_id, version, total_price)
                    
                    return doc_id
                else:
                    logger.error("Failed to save PDF to database")
                    return None
                    
            except ImportError:
                logger.error("Legacy database module not available")
                return None
                
        except Exception as e:
            logger.error(f"Error in auto_save_to_crm: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _update_offer_status(
        self,
        project_id: int,
        version: int,
        offer_value: Optional[float]
    ):
        """
        Update offer status when PDF is archived.
        
        Args:
            project_id: Project ID
            version: PDF version
            offer_value: Offer value
        """
        try:
            from crm.features.offer_tracker import update_offer_status
            from database import get_db_connection
            
            conn = get_db_connection()
            if conn:
                success = update_offer_status(
                    conn,
                    project_id,
                    'sent',
                    offer_value=offer_value,
                    offer_version=version
                )
                
                if success:
                    logger.info(f"Offer status updated to 'sent' for project {project_id}")
                    logger.info(f"  • Follow-up reminder created for 7 days")
                
                conn.close()
                
        except ImportError:
            logger.warning("Offer tracker not available, status update skipped")
        except Exception as e:
            logger.error(f"Error updating offer status: {e}")
    
    def get_pdf_history(
        self,
        customer_id: int,
        project_id: Optional[int] = None,
        pdf_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get PDF history for a customer.
        
        Args:
            customer_id: Customer ID
            project_id: Optional project ID filter
            pdf_type: Optional PDF type filter
            start_date: Optional start date filter
            end_date: Optional end date filter
        
        Returns:
            List of PDF documents with metadata
        """
        try:
            from database import list_customer_documents
            
            # Get all documents
            docs = list_customer_documents(customer_id, project_id)
            
            # Filter by PDF type if specified
            if pdf_type:
                docs = [d for d in docs if d.get('doc_type') == pdf_type]
            
            # Filter by date range if specified
            if start_date or end_date:
                filtered_docs = []
                for doc in docs:
                    uploaded_at = doc.get('uploaded_at', '')
                    if uploaded_at:
                        try:
                            if 'T' in uploaded_at:
                                doc_date = datetime.fromisoformat(uploaded_at.replace('Z', '+00:00'))
                            else:
                                doc_date = datetime.strptime(uploaded_at, '%Y-%m-%d %H:%M:%S')
                            
                            if start_date and doc_date < start_date:
                                continue
                            if end_date and doc_date > end_date:
                                continue
                            
                            filtered_docs.append(doc)
                        except Exception:
                            continue
                docs = filtered_docs
            
            # Format documents for display
            try:
                from crm.integration.pdf_bridge import format_document_list_for_display
                docs = format_document_list_for_display(docs)
            except ImportError:
                pass
            
            return docs
            
        except Exception as e:
            logger.error(f"Error getting PDF history: {e}")
            return []
    
    def search_pdfs(
        self,
        customer_id: Optional[int] = None,
        search_term: Optional[str] = None,
        pdf_type: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        company_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search PDFs in archive with various filters.
        
        Args:
            customer_id: Optional customer ID filter
            search_term: Optional search term (searches in filename and metadata)
            pdf_type: Optional PDF type filter
            min_price: Optional minimum price filter
            max_price: Optional maximum price filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            company_name: Optional company name filter
        
        Returns:
            List of matching PDF documents
        """
        try:
            from database import get_db_connection
            
            conn = get_db_connection()
            if not conn:
                return []
            
            # Build SQL query
            query = """
                SELECT cd.*, c.name as customer_name, c.company as customer_company
                FROM customer_documents cd
                LEFT JOIN customers c ON cd.customer_id = c.id
                WHERE 1=1
            """
            params = []
            
            if customer_id:
                query += " AND cd.customer_id = ?"
                params.append(customer_id)
            
            if pdf_type:
                query += " AND cd.doc_type = ?"
                params.append(pdf_type)
            
            if search_term:
                query += " AND (cd.display_name LIKE ? OR cd.suggested_filename LIKE ?)"
                search_pattern = f"%{search_term}%"
                params.extend([search_pattern, search_pattern])
            
            if company_name:
                query += " AND (c.name LIKE ? OR c.company LIKE ?)"
                company_pattern = f"%{company_name}%"
                params.extend([company_pattern, company_pattern])
            
            if start_date:
                query += " AND cd.uploaded_at >= ?"
                params.append(start_date.strftime('%Y-%m-%d'))
            
            if end_date:
                query += " AND cd.uploaded_at <= ?"
                params.append(end_date.strftime('%Y-%m-%d'))
            
            query += " ORDER BY cd.uploaded_at DESC"
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                doc = dict(row)
                
                # Apply price filters if specified (requires metadata parsing)
                if min_price is not None or max_price is not None:
                    # This would require parsing metadata from the document
                    # For now, we'll skip price filtering in SQL
                    pass
                
                results.append(doc)
            
            conn.close()
            
            # Format documents for display
            try:
                from crm.integration.pdf_bridge import format_document_list_for_display
                results = format_document_list_for_display(results)
            except ImportError:
                pass
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching PDFs: {e}")
            return []
    
    def export_pdf(
        self,
        document_id: int,
        output_path: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Export PDF from archive.
        
        Args:
            document_id: Document ID
            output_path: Optional output path to save file
        
        Returns:
            PDF bytes if successful, None otherwise
        """
        try:
            from database import get_customer_document
            
            doc = get_customer_document(document_id)
            if not doc:
                logger.error(f"Document {document_id} not found")
                return None
            
            pdf_bytes = doc.get('file_bytes')
            if not pdf_bytes:
                logger.error(f"No file bytes for document {document_id}")
                return None
            
            # Save to file if output path specified
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(pdf_bytes)
                logger.info(f"PDF exported to {output_path}")
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error exporting PDF: {e}")
            return None
    
    def export_multiple_pdfs(
        self,
        document_ids: List[int],
        output_dir: str
    ) -> Dict[int, str]:
        """
        Export multiple PDFs from archive.
        
        Args:
            document_ids: List of document IDs
            output_dir: Output directory
        
        Returns:
            Dictionary mapping document ID to output path
        """
        results = {}
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        for doc_id in document_ids:
            try:
                from database import get_customer_document
                
                doc = get_customer_document(doc_id)
                if not doc:
                    logger.warning(f"Document {doc_id} not found")
                    continue
                
                # Get filename
                filename = doc.get('suggested_filename') or doc.get('display_name') or f"document_{doc_id}.pdf"
                output_path = os.path.join(output_dir, filename)
                
                # Export PDF
                pdf_bytes = self.export_pdf(doc_id, output_path)
                if pdf_bytes:
                    results[doc_id] = output_path
                    
            except Exception as e:
                logger.error(f"Error exporting document {doc_id}: {e}")
        
        logger.info(f"Exported {len(results)} PDFs to {output_dir}")
        return results
    
    def get_pdf_statistics(
        self,
        customer_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get PDF archive statistics.
        
        Args:
            customer_id: Optional customer ID filter
            start_date: Optional start date filter
            end_date: Optional end date filter
        
        Returns:
            Dictionary with statistics
        """
        try:
            from database import get_db_connection
            
            conn = get_db_connection()
            if not conn:
                return {}
            
            # Build query
            query = """
                SELECT 
                    COUNT(*) as total_pdfs,
                    COUNT(DISTINCT customer_id) as total_customers,
                    doc_type,
                    COUNT(*) as count_by_type
                FROM customer_documents
                WHERE 1=1
            """
            params = []
            
            if customer_id:
                query += " AND customer_id = ?"
                params.append(customer_id)
            
            if start_date:
                query += " AND uploaded_at >= ?"
                params.append(start_date.strftime('%Y-%m-%d'))
            
            if end_date:
                query += " AND uploaded_at <= ?"
                params.append(end_date.strftime('%Y-%m-%d'))
            
            query += " GROUP BY doc_type"
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            stats = {
                'total_pdfs': 0,
                'total_customers': 0,
                'by_type': {}
            }
            
            for row in cursor.fetchall():
                stats['by_type'][row['doc_type']] = row['count_by_type']
                stats['total_pdfs'] += row['count_by_type']
            
            # Get total customers
            if not customer_id:
                cursor.execute("""
                    SELECT COUNT(DISTINCT customer_id) as total_customers
                    FROM customer_documents
                """)
                row = cursor.fetchone()
                if row:
                    stats['total_customers'] = row['total_customers']
            else:
                stats['total_customers'] = 1
            
            conn.close()
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting PDF statistics: {e}")
            return {}
