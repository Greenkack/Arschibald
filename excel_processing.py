"""excel_processing.py - Excel File Processing"""
import pandas as pd
import openpyxl
from pathlib import Path
from typing import Optional, Dict, Any

def read_excel_file(file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
    """Lese Excel-Datei"""
    try:
        return pd.read_excel(file_path, sheet_name=sheet_name)
    except Exception as e:
        raise Exception(f"Fehler beim Lesen der Excel-Datei: {e}")

def write_excel_file(df: pd.DataFrame, file_path: str, sheet_name: str = "Sheet1"):
    """Schreibe DataFrame in Excel"""
    try:
        df.to_excel(file_path, sheet_name=sheet_name, index=False)
    except Exception as e:
        raise Exception(f"Fehler beim Schreiben der Excel-Datei: {e}")

def process_price_matrix(file_path: str) -> Dict[str, Any]:
    """Verarbeite Preismatrix aus Excel"""
    df = read_excel_file(file_path)
    
    price_matrix = {}
    for _, row in df.iterrows():
        key = row.get('key', '')
        value = row.get('value', 0)
        price_matrix[key] = value
    
    return price_matrix
