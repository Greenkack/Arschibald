"""csv_importer.py - CSV Import System"""
import pandas as pd
import csv
from typing import List, Dict, Any, Optional
from pathlib import Path

class CSVImporter:
    """CSV-Import-Manager"""
    
    def __init__(self, encoding: str = 'utf-8', delimiter: str = ','):
        self.encoding = encoding
        self.delimiter = delimiter
    
    def import_csv(self, file_path: str, has_header: bool = True) -> pd.DataFrame:
        """Importiere CSV-Datei"""
        try:
            if has_header:
                df = pd.read_csv(file_path, encoding=self.encoding, delimiter=self.delimiter)
            else:
                df = pd.read_csv(file_path, encoding=self.encoding, delimiter=self.delimiter, header=None)
            
            return df
        except Exception as e:
            raise Exception(f"Fehler beim Importieren der CSV: {e}")
    
    def validate_columns(self, df: pd.DataFrame, required_columns: List[str]) -> tuple[bool, List[str]]:
        """Validiere erforderliche Spalten"""
        missing = []
        for col in required_columns:
            if col not in df.columns:
                missing.append(col)
        
        return len(missing) == 0, missing
    
    def import_products(self, file_path: str) -> List[Dict[str, Any]]:
        """Importiere Produkte aus CSV"""
        df = self.import_csv(file_path)
        
        required_cols = ['name', 'category', 'price']
        valid, missing = self.validate_columns(df, required_cols)
        
        if not valid:
            raise ValueError(f"Fehlende Spalten: {', '.join(missing)}")
        
        products = []
        for _, row in df.iterrows():
            products.append({
                'name': row['name'],
                'category': row['category'],
                'price': float(row['price']),
                'description': row.get('description', ''),
                'manufacturer': row.get('manufacturer', '')
            })
        
        return products
    
    def import_customers(self, file_path: str) -> List[Dict[str, Any]]:
        """Importiere Kunden aus CSV"""
        df = self.import_csv(file_path)
        
        required_cols = ['name', 'email']
        valid, missing = self.validate_columns(df, required_cols)
        
        if not valid:
            raise ValueError(f"Fehlende Spalten: {', '.join(missing)}")
        
        customers = []
        for _, row in df.iterrows():
            customers.append({
                'name': row['name'],
                'email': row['email'],
                'phone': row.get('phone', ''),
                'address': row.get('address', ''),
                'city': row.get('city', ''),
                'postal_code': row.get('postal_code', '')
            })
        
        return customers
    
    def detect_delimiter(self, file_path: str) -> str:
        """Erkenne Delimiter automatisch"""
        with open(file_path, 'r', encoding=self.encoding) as f:
            sample = f.read(1024)
            sniffer = csv.Sniffer()
            return sniffer.sniff(sample).delimiter
