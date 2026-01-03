"""tests/test_database.py - Unit Tests für Datenbank-Layer"""
import unittest
import sqlite3
import tempfile
import shutil
from pathlib import Path
from database import get_db_connection, init_db

class TestDatabase(unittest.TestCase):
    """Tests für Datenbank-Operationen"""
    
    def setUp(self):
        """Setup vor jedem Test"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_db = self.temp_dir / "test.db"
        
        # Test-Datenbank mit Row Factory
        self.conn = sqlite3.connect(str(self.test_db))
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def tearDown(self):
        """Cleanup nach jedem Test"""
        if self.conn:
            self.conn.close()
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_connection_row_factory(self):
        """Test: Row Factory ist gesetzt"""
        self.assertIsNotNone(self.conn.row_factory)
        self.assertEqual(self.conn.row_factory, sqlite3.Row)
    
    def test_create_customers_table(self):
        """Test: Kunden-Tabelle erstellen"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
        
        # Tabelle sollte existieren
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers'")
        result = self.cursor.fetchone()
        self.assertIsNotNone(result)
    
    def test_insert_customer(self):
        """Test: Kunde einfügen"""
        self.cursor.execute("""
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT
            )
        """)
        
        self.cursor.execute("""
            INSERT INTO customers (name, email) 
            VALUES (?, ?)
        """, ("Max Mustermann", "max@example.com"))
        self.conn.commit()
        
        # Kunde sollte existieren
        self.cursor.execute("SELECT * FROM customers WHERE email = ?", ("max@example.com",))
        row = self.cursor.fetchone()
        
        self.assertIsNotNone(row)
        self.assertEqual(row['name'], "Max Mustermann")
        self.assertEqual(row['email'], "max@example.com")
    
    def test_update_customer(self):
        """Test: Kunde aktualisieren"""
        self.cursor.execute("""
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY,
                name TEXT,
                phone TEXT
            )
        """)
        
        self.cursor.execute("INSERT INTO customers (name, phone) VALUES (?, ?)", 
                          ("Test", "123"))
        self.conn.commit()
        
        self.cursor.execute("UPDATE customers SET phone = ? WHERE name = ?", 
                          ("456", "Test"))
        self.conn.commit()
        
        self.cursor.execute("SELECT phone FROM customers WHERE name = ?", ("Test",))
        row = self.cursor.fetchone()
        self.assertEqual(row['phone'], "456")
    
    def test_delete_customer(self):
        """Test: Kunde löschen"""
        self.cursor.execute("""
            CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT)
        """)
        
        self.cursor.execute("INSERT INTO customers (name) VALUES (?)", ("Delete Me",))
        self.conn.commit()
        
        self.cursor.execute("DELETE FROM customers WHERE name = ?", ("Delete Me",))
        self.conn.commit()
        
        self.cursor.execute("SELECT * FROM customers WHERE name = ?", ("Delete Me",))
        row = self.cursor.fetchone()
        self.assertIsNone(row)
    
    def test_foreign_key_constraint(self):
        """Test: Foreign Key zwischen Projekten und Kunden"""
        self.cursor.execute("""
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE projects (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                name TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)
        
        self.cursor.execute("INSERT INTO customers (name) VALUES (?)", ("Test Kunde",))
        customer_id = self.cursor.lastrowid
        
        self.cursor.execute("INSERT INTO projects (customer_id, name) VALUES (?, ?)", 
                          (customer_id, "Test Projekt"))
        self.conn.commit()
        
        # Projekt sollte Kunde referenzieren
        self.cursor.execute("""
            SELECT p.name, c.name as customer_name 
            FROM projects p 
            JOIN customers c ON p.customer_id = c.id
        """)
        row = self.cursor.fetchone()
        self.assertEqual(row['customer_name'], "Test Kunde")
    
    def test_transaction_rollback(self):
        """Test: Transaction Rollback"""
        self.cursor.execute("CREATE TABLE test (id INTEGER, value TEXT)")
        self.cursor.execute("INSERT INTO test VALUES (1, 'before')")
        self.conn.commit()
        
        # Transaktion starten
        self.cursor.execute("INSERT INTO test VALUES (2, 'during')")
        self.conn.rollback()
        
        # Zweiter Eintrag sollte nicht existieren
        self.cursor.execute("SELECT * FROM test WHERE id = 2")
        row = self.cursor.fetchone()
        self.assertIsNone(row)
    
    def test_pragma_table_info(self):
        """Test: PRAGMA table_info für Migration"""
        self.cursor.execute("""
            CREATE TABLE test (
                id INTEGER PRIMARY KEY,
                name TEXT,
                age INTEGER
            )
        """)
        
        self.cursor.execute("PRAGMA table_info(test)")
        columns = self.cursor.fetchall()
        
        column_names = [col['name'] for col in columns]
        self.assertIn('id', column_names)
        self.assertIn('name', column_names)
        self.assertIn('age', column_names)
    
    def test_add_column_migration(self):
        """Test: Spalte hinzufügen (Migration)"""
        self.cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        
        # Prüfe ob Spalte existiert
        self.cursor.execute("PRAGMA table_info(test)")
        columns = [col['name'] for col in self.cursor.fetchall()]
        
        if 'email' not in columns:
            self.cursor.execute("ALTER TABLE test ADD COLUMN email TEXT")
            self.conn.commit()
        
        # Spalte sollte jetzt existieren
        self.cursor.execute("PRAGMA table_info(test)")
        columns = [col['name'] for col in self.cursor.fetchall()]
        self.assertIn('email', columns)
    
    def test_json_storage(self):
        """Test: JSON-Daten speichern"""
        import json
        
        self.cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, data TEXT)")
        
        test_data = {'key': 'value', 'number': 123}
        json_str = json.dumps(test_data)
        
        self.cursor.execute("INSERT INTO test (data) VALUES (?)", (json_str,))
        self.conn.commit()
        
        self.cursor.execute("SELECT data FROM test")
        row = self.cursor.fetchone()
        loaded_data = json.loads(row['data'])
        
        self.assertEqual(loaded_data['key'], 'value')
        self.assertEqual(loaded_data['number'], 123)


class TestDatabaseQueries(unittest.TestCase):
    """Tests für komplexe Queries"""
    
    def setUp(self):
        """Setup"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_db = self.temp_dir / "test.db"
        self.conn = sqlite3.connect(str(self.test_db))
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        # Test-Daten
        self.cursor.execute("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name TEXT,
                category TEXT,
                price REAL
            )
        """)
        
        test_products = [
            ("Module A", "modules", 300.0),
            ("Module B", "modules", 350.0),
            ("Inverter X", "inverters", 1500.0),
            ("Battery Y", "batteries", 5000.0)
        ]
        
        self.cursor.executemany("INSERT INTO products (name, category, price) VALUES (?, ?, ?)", 
                              test_products)
        self.conn.commit()
    
    def tearDown(self):
        """Cleanup"""
        self.conn.close()
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_filter_by_category(self):
        """Test: Nach Kategorie filtern"""
        self.cursor.execute("SELECT * FROM products WHERE category = ?", ("modules",))
        rows = self.cursor.fetchall()
        
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row['category'] == 'modules' for row in rows))
    
    def test_aggregate_sum(self):
        """Test: Summe berechnen"""
        self.cursor.execute("SELECT SUM(price) as total FROM products WHERE category = ?", 
                          ("modules",))
        row = self.cursor.fetchone()
        
        self.assertEqual(row['total'], 650.0)
    
    def test_count_by_category(self):
        """Test: Anzahl pro Kategorie"""
        self.cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM products 
            GROUP BY category
        """)
        rows = self.cursor.fetchall()
        
        self.assertGreaterEqual(len(rows), 3)


if __name__ == '__main__':
    unittest.main()
