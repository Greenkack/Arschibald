"""
Customer Data Service

Provides customer data management with CRM integration,
PDF placeholder generation, and import/export functionality.

Requirements: funktionen.txt - "CRM-System gespeichert"
"""

import sys
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import json
import csv
from io import StringIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

logger = logging.getLogger(__name__)


class CustomerDataService:
    """
    Customer Data Service for CRM integration, PDF placeholders,
    and data import/export functionality.
    """
    
    # PDF Placeholder mapping for customer data
    PDF_PLACEHOLDERS = {
        'customer_name': '{{KUNDE_NAME}}',
        'customer_first_name': '{{KUNDE_VORNAME}}',
        'customer_last_name': '{{KUNDE_NACHNAME}}',
        'customer_company': '{{KUNDE_FIRMA}}',
        'customer_street': '{{KUNDE_STRASSE}}',
        'customer_house_number': '{{KUNDE_HAUSNUMMER}}',
        'customer_postal_code': '{{KUNDE_PLZ}}',
        'customer_city': '{{KUNDE_ORT}}',
        'customer_bundesland': '{{KUNDE_BUNDESLAND}}',
        'customer_full_address': '{{KUNDE_ADRESSE_KOMPLETT}}',
        'customer_email': '{{KUNDE_EMAIL}}',
        'customer_phone': '{{KUNDE_TELEFON}}',
        'customer_mobile': '{{KUNDE_MOBIL}}',
        'customer_salutation': '{{KUNDE_ANREDE}}',
        'customer_title': '{{KUNDE_TITEL}}',
        'customer_id': '{{KUNDE_ID}}',
        'customer_created_at': '{{KUNDE_ERSTELLT_AM}}',
        'customer_notes': '{{KUNDE_NOTIZEN}}',
    }
    
    def __init__(self, database_path: str = "crm_database.db"):
        """Initialize Customer Data Service."""
        self.database_path = database_path
        self._init_database()
        logger.info("Customer Data Service initialized")
    
    def _init_database(self):
        """Initialize database tables if needed."""
        try:
            import sqlite3
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    salutation TEXT,
                    title TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    company TEXT,
                    street TEXT,
                    house_number TEXT,
                    postal_code TEXT,
                    city TEXT,
                    bundesland TEXT,
                    email TEXT,
                    phone TEXT,
                    mobile TEXT,
                    notes TEXT,
                    tags TEXT,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_customers_postal_code ON customers(postal_code)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(last_name, first_name)
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    # ==================== CRUD Operations ====================
    
    def create_customer(self, customer_data: Dict[str, Any]) -> int:
        """
        Create a new customer in CRM.
        
        Args:
            customer_data: Customer information
            
        Returns:
            Customer ID
        """
        try:
            import sqlite3
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO customers (
                    salutation, title, first_name, last_name, company,
                    street, house_number, postal_code, city, bundesland,
                    email, phone, mobile, notes, tags, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                customer_data.get('salutation', ''),
                customer_data.get('title', ''),
                customer_data.get('first_name', ''),
                customer_data.get('last_name', ''),
                customer_data.get('company', ''),
                customer_data.get('street', ''),
                customer_data.get('house_number', ''),
                customer_data.get('postal_code', ''),
                customer_data.get('city', ''),
                customer_data.get('bundesland', ''),
                customer_data.get('email', ''),
                customer_data.get('phone', ''),
                customer_data.get('mobile', ''),
                customer_data.get('notes', ''),
                json.dumps(customer_data.get('tags', [])),
                customer_data.get('source', 'manual')
            ))
            
            customer_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Created customer with ID: {customer_id}")
            return customer_id
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            raise
    
    def get_customer(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Get customer by ID."""
        try:
            import sqlite3
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self._row_to_dict(row)
            return None
        except Exception as e:
            logger.error(f"Error getting customer: {e}")
            raise
    
    def update_customer(self, customer_id: int, updates: Dict[str, Any]) -> bool:
        """Update customer data."""
        try:
            import sqlite3
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            set_clauses = []
            values = []
            for key, value in updates.items():
                if key in ['salutation', 'title', 'first_name', 'last_name', 'company',
                          'street', 'house_number', 'postal_code', 'city', 'bundesland',
                          'email', 'phone', 'mobile', 'notes', 'source']:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
                elif key == 'tags':
                    set_clauses.append("tags = ?")
                    values.append(json.dumps(value))
            
            if set_clauses:
                set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                values.append(customer_id)
                
                cursor.execute(f'''
                    UPDATE customers SET {', '.join(set_clauses)} WHERE id = ?
                ''', values)
                
                conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error updating customer: {e}")
            raise
    
    def delete_customer(self, customer_id: int) -> bool:
        """Delete customer."""
        try:
            import sqlite3
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error deleting customer: {e}")
            raise
    
    # ==================== Search & Retrieval ====================
    
    def search_customers(self, query: str, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Search customers by name, email, address, etc.
        
        Args:
            query: Search query
            filters: Optional filters (postal_code, city, bundesland, tags)
            
        Returns:
            List of matching customers
        """
        try:
            import sqlite3
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            where_clauses = []
            params = []
            
            if query:
                where_clauses.append('''
                    (first_name LIKE ? OR last_name LIKE ? OR company LIKE ? 
                     OR email LIKE ? OR city LIKE ? OR street LIKE ?)
                ''')
                search_term = f'%{query}%'
                params.extend([search_term] * 6)
            
            if filters:
                if filters.get('postal_code'):
                    where_clauses.append('postal_code LIKE ?')
                    params.append(f"{filters['postal_code']}%")
                if filters.get('city'):
                    where_clauses.append('city LIKE ?')
                    params.append(f"%{filters['city']}%")
                if filters.get('bundesland'):
                    where_clauses.append('bundesland = ?')
                    params.append(filters['bundesland'])
            
            sql = 'SELECT * FROM customers'
            if where_clauses:
                sql += ' WHERE ' + ' AND '.join(where_clauses)
            sql += ' ORDER BY last_name, first_name LIMIT 100'
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            conn.close()
            
            return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error searching customers: {e}")
            raise
    
    def get_all_customers(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all customers with pagination."""
        try:
            import sqlite3
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM customers 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting customers: {e}")
            raise
    
    # ==================== PDF Placeholder Generation ====================
    
    def get_pdf_placeholders(self, customer_id: int) -> Dict[str, str]:
        """
        Generate PDF placeholders for a customer.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Dictionary mapping placeholder keys to values
        """
        customer = self.get_customer(customer_id)
        if not customer:
            return {}
        
        full_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
        full_address = self._format_full_address(customer)
        
        return {
            self.PDF_PLACEHOLDERS['customer_name']: full_name,
            self.PDF_PLACEHOLDERS['customer_first_name']: customer.get('first_name', ''),
            self.PDF_PLACEHOLDERS['customer_last_name']: customer.get('last_name', ''),
            self.PDF_PLACEHOLDERS['customer_company']: customer.get('company', ''),
            self.PDF_PLACEHOLDERS['customer_street']: customer.get('street', ''),
            self.PDF_PLACEHOLDERS['customer_house_number']: customer.get('house_number', ''),
            self.PDF_PLACEHOLDERS['customer_postal_code']: customer.get('postal_code', ''),
            self.PDF_PLACEHOLDERS['customer_city']: customer.get('city', ''),
            self.PDF_PLACEHOLDERS['customer_bundesland']: customer.get('bundesland', ''),
            self.PDF_PLACEHOLDERS['customer_full_address']: full_address,
            self.PDF_PLACEHOLDERS['customer_email']: customer.get('email', ''),
            self.PDF_PLACEHOLDERS['customer_phone']: customer.get('phone', ''),
            self.PDF_PLACEHOLDERS['customer_mobile']: customer.get('mobile', ''),
            self.PDF_PLACEHOLDERS['customer_salutation']: customer.get('salutation', ''),
            self.PDF_PLACEHOLDERS['customer_title']: customer.get('title', ''),
            self.PDF_PLACEHOLDERS['customer_id']: str(customer.get('id', '')),
            self.PDF_PLACEHOLDERS['customer_created_at']: customer.get('created_at', ''),
            self.PDF_PLACEHOLDERS['customer_notes']: customer.get('notes', ''),
        }
    
    def get_placeholder_list(self) -> List[Dict[str, str]]:
        """Get list of available PDF placeholders."""
        return [
            {'key': key, 'placeholder': value, 'description': self._get_placeholder_description(key)}
            for key, value in self.PDF_PLACEHOLDERS.items()
        ]
    
    # ==================== Import/Export ====================
    
    def export_customers_csv(self, customer_ids: Optional[List[int]] = None) -> str:
        """
        Export customers to CSV format.
        
        Args:
            customer_ids: Optional list of customer IDs to export
            
        Returns:
            CSV string
        """
        try:
            if customer_ids:
                customers = [self.get_customer(cid) for cid in customer_ids if self.get_customer(cid)]
            else:
                customers = self.get_all_customers()
            
            output = StringIO()
            fieldnames = ['id', 'salutation', 'title', 'first_name', 'last_name', 'company',
                         'street', 'house_number', 'postal_code', 'city', 'bundesland',
                         'email', 'phone', 'mobile', 'notes', 'created_at']
            
            writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            for customer in customers:
                writer.writerow(customer)
            
            return output.getvalue()
        except Exception as e:
            logger.error(f"Error exporting customers: {e}")
            raise
    
    def export_customers_json(self, customer_ids: Optional[List[int]] = None) -> str:
        """Export customers to JSON format."""
        try:
            if customer_ids:
                customers = [self.get_customer(cid) for cid in customer_ids if self.get_customer(cid)]
            else:
                customers = self.get_all_customers()
            
            return json.dumps(customers, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error exporting customers: {e}")
            raise
    
    def import_customers_csv(self, csv_content: str, source: str = 'csv_import') -> Dict[str, Any]:
        """
        Import customers from CSV.
        
        Args:
            csv_content: CSV string content
            source: Import source identifier
            
        Returns:
            Import result with counts
        """
        try:
            reader = csv.DictReader(StringIO(csv_content))
            imported = 0
            errors = []
            
            for row in reader:
                try:
                    customer_data = {
                        'salutation': row.get('salutation', row.get('Anrede', '')),
                        'title': row.get('title', row.get('Titel', '')),
                        'first_name': row.get('first_name', row.get('Vorname', '')),
                        'last_name': row.get('last_name', row.get('Nachname', '')),
                        'company': row.get('company', row.get('Firma', '')),
                        'street': row.get('street', row.get('Straße', '')),
                        'house_number': row.get('house_number', row.get('Hausnummer', '')),
                        'postal_code': row.get('postal_code', row.get('PLZ', '')),
                        'city': row.get('city', row.get('Ort', '')),
                        'bundesland': row.get('bundesland', row.get('Bundesland', '')),
                        'email': row.get('email', row.get('Email', '')),
                        'phone': row.get('phone', row.get('Telefon', '')),
                        'mobile': row.get('mobile', row.get('Mobil', '')),
                        'notes': row.get('notes', row.get('Notizen', '')),
                        'source': source
                    }
                    self.create_customer(customer_data)
                    imported += 1
                except Exception as e:
                    errors.append(str(e))
            
            return {'imported': imported, 'errors': errors}
        except Exception as e:
            logger.error(f"Error importing customers: {e}")
            raise
    
    def import_customers_json(self, json_content: str, source: str = 'json_import') -> Dict[str, Any]:
        """Import customers from JSON."""
        try:
            customers = json.loads(json_content)
            imported = 0
            errors = []
            
            for customer_data in customers:
                try:
                    customer_data['source'] = source
                    self.create_customer(customer_data)
                    imported += 1
                except Exception as e:
                    errors.append(str(e))
            
            return {'imported': imported, 'errors': errors}
        except Exception as e:
            logger.error(f"Error importing customers: {e}")
            raise
    
    # ==================== Helper Methods ====================
    
    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convert database row to dictionary."""
        result = dict(row)
        if result.get('tags'):
            try:
                result['tags'] = json.loads(result['tags'])
            except:
                result['tags'] = []
        return result
    
    def _format_full_address(self, customer: Dict[str, Any]) -> str:
        """Format full address string."""
        parts = []
        street_line = customer.get('street', '')
        if customer.get('house_number'):
            street_line += f" {customer['house_number']}"
        if street_line:
            parts.append(street_line)
        
        city_line = ''
        if customer.get('postal_code'):
            city_line = customer['postal_code']
        if customer.get('city'):
            city_line += f" {customer['city']}" if city_line else customer['city']
        if city_line:
            parts.append(city_line)
        
        return ', '.join(parts)
    
    def _get_placeholder_description(self, key: str) -> str:
        """Get description for placeholder key."""
        descriptions = {
            'customer_name': 'Vollständiger Name (Vorname Nachname)',
            'customer_first_name': 'Vorname',
            'customer_last_name': 'Nachname',
            'customer_company': 'Firmenname',
            'customer_street': 'Straße',
            'customer_house_number': 'Hausnummer',
            'customer_postal_code': 'Postleitzahl',
            'customer_city': 'Ort',
            'customer_bundesland': 'Bundesland',
            'customer_full_address': 'Vollständige Adresse',
            'customer_email': 'E-Mail-Adresse',
            'customer_phone': 'Telefonnummer',
            'customer_mobile': 'Mobilnummer',
            'customer_salutation': 'Anrede (Herr/Frau)',
            'customer_title': 'Titel (Dr., Prof., etc.)',
            'customer_id': 'Kunden-ID',
            'customer_created_at': 'Erstellungsdatum',
            'customer_notes': 'Notizen',
        }
        return descriptions.get(key, key)
    
    def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        try:
            import sqlite3
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM customers')
            count = cursor.fetchone()[0]
            conn.close()
            return {'status': 'healthy', 'customer_count': count}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
