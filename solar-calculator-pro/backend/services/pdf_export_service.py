"""
PDF Export Service
Handles single and batch PDF downloads, email sending, and export management
"""

import os
import io
import zipfile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from typing import List, Dict, Any, Optional, BinaryIO
from datetime import datetime
from pathlib import Path
import base64
import logging

logger = logging.getLogger(__name__)


class PDFExportService:
    """Service for PDF export, download, and email functionality"""
    
    def __init__(self, pdf_storage_path: str = "pdf_exports"):
        self.storage_path = Path(pdf_storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
    def export_single_pdf(
        self,
        pdf_bytes: bytes,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Export a single PDF file
        
        Args:
            pdf_bytes: PDF file content as bytes
            filename: Name for the PDF file
            metadata: Optional metadata about the PDF
            
        Returns:
            Dictionary with export information
        """
        try:
            # Ensure filename has .pdf extension
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            
            # Save to storage
            file_path = self.storage_path / filename
            with open(file_path, 'wb') as f:
                f.write(pdf_bytes)
            
            # Calculate file size
            file_size = len(pdf_bytes)
            
            export_info = {
                'filename': filename,
                'file_path': str(file_path),
                'file_size': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'exported_at': datetime.now().isoformat(),
                'metadata': metadata or {},
                'success': True
            }
            
            logger.info(f"Successfully exported PDF: {filename} ({export_info['file_size_mb']} MB)")
            return export_info
            
        except Exception as e:
            logger.error(f"Error exporting PDF {filename}: {str(e)}")
            return {
                'filename': filename,
                'success': False,
                'error': str(e)
            }
    
    def export_batch_pdfs(
        self,
        pdfs: List[Dict[str, Any]],
        zip_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export multiple PDFs as a ZIP file
        
        Args:
            pdfs: List of dictionaries with 'bytes' and 'filename' keys
            zip_filename: Optional name for the ZIP file
            
        Returns:
            Dictionary with ZIP file information
        """
        try:
            if not zip_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                zip_filename = f"pdf_batch_{timestamp}.zip"
            
            if not zip_filename.endswith('.zip'):
                zip_filename += '.zip'
            
            zip_path = self.storage_path / zip_filename
            
            # Create ZIP file
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for pdf_info in pdfs:
                    pdf_bytes = pdf_info.get('bytes')
                    filename = pdf_info.get('filename', f'document_{pdfs.index(pdf_info)}.pdf')
                    
                    if not filename.endswith('.pdf'):
                        filename += '.pdf'
                    
                    # Add PDF to ZIP
                    zipf.writestr(filename, pdf_bytes)
            
            # Get ZIP file size
            zip_size = os.path.getsize(zip_path)
            
            result = {
                'zip_filename': zip_filename,
                'zip_path': str(zip_path),
                'zip_size': zip_size,
                'zip_size_mb': round(zip_size / (1024 * 1024), 2),
                'pdf_count': len(pdfs),
                'exported_at': datetime.now().isoformat(),
                'success': True
            }
            
            logger.info(f"Successfully created ZIP with {len(pdfs)} PDFs: {zip_filename}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating PDF batch ZIP: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_pdf_email(
        self,
        pdf_bytes: bytes,
        filename: str,
        recipient_email: str,
        subject: str,
        body: str,
        smtp_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send PDF via email
        
        Args:
            pdf_bytes: PDF file content
            filename: PDF filename
            recipient_email: Recipient email address
            subject: Email subject
            body: Email body text
            smtp_config: SMTP configuration (host, port, username, password)
            
        Returns:
            Dictionary with send status
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = smtp_config['username']
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Attach PDF
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            
            part = MIMEBase('application', 'pdf')
            part.set_payload(pdf_bytes)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            msg.attach(part)
            
            # Send email
            with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
                if smtp_config.get('use_tls', True):
                    server.starttls()
                server.login(smtp_config['username'], smtp_config['password'])
                server.send_message(msg)
            
            result = {
                'recipient': recipient_email,
                'filename': filename,
                'sent_at': datetime.now().isoformat(),
                'success': True
            }
            
            logger.info(f"Successfully sent PDF email to {recipient_email}")
            return result
            
        except Exception as e:
            logger.error(f"Error sending PDF email: {str(e)}")
            return {
                'recipient': recipient_email,
                'success': False,
                'error': str(e)
            }
    
    def send_batch_pdf_email(
        self,
        pdfs: List[Dict[str, Any]],
        recipient_email: str,
        subject: str,
        body: str,
        smtp_config: Dict[str, Any],
        as_zip: bool = True
    ) -> Dict[str, Any]:
        """
        Send multiple PDFs via email (as ZIP or separate attachments)
        
        Args:
            pdfs: List of PDF dictionaries
            recipient_email: Recipient email
            subject: Email subject
            body: Email body
            smtp_config: SMTP configuration
            as_zip: If True, send as ZIP; if False, send as separate attachments
            
        Returns:
            Dictionary with send status
        """
        try:
            if as_zip:
                # Create ZIP and send
                zip_result = self.export_batch_pdfs(pdfs)
                if not zip_result['success']:
                    return zip_result
                
                with open(zip_result['zip_path'], 'rb') as f:
                    zip_bytes = f.read()
                
                return self.send_pdf_email(
                    zip_bytes,
                    zip_result['zip_filename'],
                    recipient_email,
                    subject,
                    body,
                    smtp_config
                )
            else:
                # Send multiple attachments
                msg = MIMEMultipart()
                msg['From'] = smtp_config['username']
                msg['To'] = recipient_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain', 'utf-8'))
                
                # Attach all PDFs
                for pdf_info in pdfs:
                    pdf_bytes = pdf_info.get('bytes')
                    filename = pdf_info.get('filename', f'document_{pdfs.index(pdf_info)}.pdf')
                    
                    if not filename.endswith('.pdf'):
                        filename += '.pdf'
                    
                    part = MIMEBase('application', 'pdf')
                    part.set_payload(pdf_bytes)
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                    msg.attach(part)
                
                # Send email
                with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
                    if smtp_config.get('use_tls', True):
                        server.starttls()
                    server.login(smtp_config['username'], smtp_config['password'])
                    server.send_message(msg)
                
                return {
                    'recipient': recipient_email,
                    'pdf_count': len(pdfs),
                    'sent_at': datetime.now().isoformat(),
                    'success': True
                }
                
        except Exception as e:
            logger.error(f"Error sending batch PDF email: {str(e)}")
            return {
                'recipient': recipient_email,
                'success': False,
                'error': str(e)
            }
    
    def get_pdf_for_preview(self, pdf_bytes: bytes) -> str:
        """
        Convert PDF bytes to base64 for browser preview
        
        Args:
            pdf_bytes: PDF file content
            
        Returns:
            Base64-encoded PDF string
        """
        return base64.b64encode(pdf_bytes).decode('utf-8')
    
    def get_pdf_for_download(self, file_path: str) -> Optional[bytes]:
        """
        Read PDF file for download
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            PDF bytes or None if file not found
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"PDF file not found: {file_path}")
                return None
            
            with open(path, 'rb') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Error reading PDF file: {str(e)}")
            return None
    
    def cleanup_old_exports(self, days: int = 7) -> Dict[str, Any]:
        """
        Clean up old exported PDF files
        
        Args:
            days: Delete files older than this many days
            
        Returns:
            Dictionary with cleanup statistics
        """
        try:
            cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
            deleted_count = 0
            deleted_size = 0
            
            for file_path in self.storage_path.glob('*'):
                if file_path.is_file():
                    file_time = file_path.stat().st_mtime
                    if file_time < cutoff_time:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        deleted_count += 1
                        deleted_size += file_size
            
            result = {
                'deleted_count': deleted_count,
                'deleted_size_mb': round(deleted_size / (1024 * 1024), 2),
                'cutoff_days': days,
                'success': True
            }
            
            logger.info(f"Cleaned up {deleted_count} old PDF exports")
            return result
            
        except Exception as e:
            logger.error(f"Error cleaning up old exports: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
