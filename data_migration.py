"""data_migration.py - Data Migration System"""
import sqlite3
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

class DataMigration:
    """Daten-Migrations-Manager"""
    
    def __init__(self, db_path: str = "data/app_data.db"):
        self.db_path = db_path
    
    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """Erstelle Datenbank-Backup"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backups/db_backup_{timestamp}.db"
        
        Path(backup_path).parent.mkdir(parents=True, exist_ok=True)
        
        source_conn = sqlite3.connect(self.db_path)
        backup_conn = sqlite3.connect(backup_path)
        
        source_conn.backup(backup_conn)
        
        source_conn.close()
        backup_conn.close()
        
        return backup_path
    
    def export_table_to_json(self, table_name: str, output_file: str):
        """Exportiere Tabelle nach JSON"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        data = [dict(row) for row in rows]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        conn.close()
    
    def import_table_from_json(self, table_name: str, input_file: str, clear_existing: bool = False):
        """Importiere Tabelle aus JSON"""
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if clear_existing:
            cursor.execute(f"DELETE FROM {table_name}")
        
        if data:
            columns = list(data[0].keys())
            placeholders = ','.join(['?' for _ in columns])
            sql = f"INSERT OR REPLACE INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
            
            for row in data:
                values = [row[col] for col in columns]
                cursor.execute(sql, values)
        
        conn.commit()
        conn.close()
    
    def migrate_schema(self, migration_script: str):
        """Führe Schema-Migration aus"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Führe Migration aus
        cursor.executescript(migration_script)
        
        conn.commit()
        conn.close()
    
    def get_table_row_count(self, table_name: str) -> int:
        """Hole Zeilenanzahl einer Tabelle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def verify_migration(self, expected_counts: Dict[str, int]) -> Dict[str, bool]:
        """Verifiziere Migration"""
        results = {}
        for table_name, expected_count in expected_counts.items():
            actual_count = self.get_table_row_count(table_name)
            results[table_name] = (actual_count == expected_count)
        return results
