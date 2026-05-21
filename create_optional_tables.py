"""create_optional_tables.py - Erstellt fehlende optionale Datenbank-Tabellen"""
import sqlite3
from pathlib import Path

DB_PATH = "data/app_data.db"

def create_optional_tables():
    """Erstelle alle fehlenden optionalen Tabellen"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # CRM Notizen
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crm_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            project_id INTEGER,
            note_text TEXT,
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)
    
    # CRM Anrufe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crm_calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            call_type TEXT,
            duration INTEGER,
            outcome TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)
    
    # CRM E-Mails
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crm_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            subject TEXT,
            body TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)
    
    # Produktkategorien
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            description TEXT,
            parent_category_id INTEGER,
            FOREIGN KEY (parent_category_id) REFERENCES product_categories(id)
        )
    """)
    
    # Preismatrizen
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_matrices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            min_kwp REAL,
            max_kwp REAL,
            price_per_kwp REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Gewinnmargen
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profit_margins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            min_value REAL,
            max_value REAL,
            margin_percent REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Wärmepumpen-Produkte
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS heatpump_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer TEXT,
            model TEXT,
            type TEXT,
            capacity_kw REAL,
            cop REAL,
            price REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # PV-Module
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pv_modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer TEXT,
            model TEXT,
            power_wp INTEGER,
            efficiency REAL,
            price REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Wechselrichter
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inverters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer TEXT,
            model TEXT,
            power_kw REAL,
            efficiency REAL,
            price REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Speichersysteme
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS storage_systems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer TEXT,
            model TEXT,
            capacity_kwh REAL,
            efficiency REAL,
            price REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Zahlungsbedingungen
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_terms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            terms_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    print(f"✅ 11 optionale Tabellen erstellt/aktualisiert")
    
    # Überprüfe erstellte Tabellen
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"✅ Gesamt-Tabellen: {len(tables)}")
    
    conn.close()

if __name__ == "__main__":
    create_optional_tables()
