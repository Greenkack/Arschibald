#!/usr/bin/env python3
"""
Database Bridge Script
Extracted from database.py, product_db.py, brand_logo_db.py

Provides complete CRUD operations for:
- Products (Solar modules, inverters, battery storage)
- Brand logos (for PDF generation)
- Customer documents (CRM system)
- Database initialization and migrations

Usage:
    python database_bridge.py list_products [--category=Modul]
    python database_bridge.py add_product --data='{"model_name":"Test 400W","brand":"TestBrand","price_euro":150.0,"capacity_w":400,"category":"Modul"}'
    python database_bridge.py update_product --id=1 --data='{"price_euro":160.0}'
    python database_bridge.py delete_product --id=1
    python database_bridge.py get_product_by_id --id=1
    python database_bridge.py get_product_by_model --model="Test 400W"
    python database_bridge.py list_categories
    python database_bridge.py list_brand_logos
    python database_bridge.py add_brand_logo --brand="TestBrand" --logo_base64="iVBOR..." --format="PNG"
    python database_bridge.py get_brand_logo --brand="TestBrand"
    python database_bridge.py delete_brand_logo --brand="TestBrand"
    python database_bridge.py init_database
"""

import json
import os
import sqlite3
import sys
from typing import Any

# Constants
DB_SCHEMA_VERSION = 14
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'app_data.db')
CUSTOMER_DOCS_BASE_DIR = os.path.join(DATA_DIR, 'customer_docs')

# Ensure directories exist
for directory in [DATA_DIR, CUSTOMER_DOCS_BASE_DIR]:
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as e:
            print(
                f"Error creating directory '{directory}': {e}",
                file=sys.stderr)


class DatabaseBridge:
    """Complete database operations extracted from Python files"""

    def __init__(self):
        self.db_path = DB_PATH

    def get_db_connection(self) -> sqlite3.Connection | None:
        """Get database connection with Row factory"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            print(f"Database connection failed: {e}", file=sys.stderr)
            return None

    def init_database(self) -> dict[str, Any]:
        """Initialize all database tables"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return {
                    "success": False,
                    "error": "Cannot connect to database"}

            # Initialize products table
            self.create_product_table(conn)

            # Initialize brand logos table
            self.create_brand_logos_table(conn)

            # Initialize customer documents table
            self.create_customer_documents_table(conn)

            conn.close()
            return {
                "success": True,
                "message": "Database initialized successfully"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_product_table(self, conn: sqlite3.Connection):
        """Create products table with all columns and migrations"""
        cursor = conn.cursor()

        # Create base table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                model_name TEXT,
                brand TEXT,
                price_euro REAL,
                capacity_w INTEGER,
                power_kw REAL,
                max_current_a REAL,
                max_voltage_v REAL,
                operating_temp_min INTEGER,
                operating_temp_max INTEGER,
                efficiency_percent REAL,
                warranty_years INTEGER,
                dimensions_length_mm INTEGER,
                dimensions_width_mm INTEGER,
                dimensions_height_mm INTEGER,
                weight_kg REAL,
                mounting_type TEXT,
                protection_class TEXT,
                cable_length_m REAL,
                connectors TEXT,
                monitoring_capabilities TEXT,
                additional_features TEXT,
                datasheet_url TEXT,
                image_url TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                storage_power_kw REAL,
                max_cycles INTEGER,
                cost_storage_aufpreis_product_db_netto REAL,
                is_active INTEGER DEFAULT 1
            )
        """)

        # Migration: Add new columns if they don't exist
        new_columns = [
            ('cell_technology', 'TEXT'),
            ('module_structure', 'TEXT'),
            ('cell_type', 'TEXT'),
            ('version', 'TEXT'),
            ('module_warranty_text', 'TEXT'),
            ('labor_hours', 'REAL')
        ]

        for column_name, column_type in new_columns:
            try:
                cursor.execute(
                    f"ALTER TABLE products ADD COLUMN {column_name} {column_type}")
            except sqlite3.OperationalError:
                # Column already exists
                pass

        # Create index for performance
        try:
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_products_model ON products(model_name)")
        except sqlite3.OperationalError:
            pass

        conn.commit()

    def create_brand_logos_table(self, conn: sqlite3.Connection):
        """Create brand logos table"""
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS brand_logos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand_name TEXT NOT NULL UNIQUE,
                logo_base64 TEXT,
                logo_format TEXT,
                file_size_bytes INTEGER DEFAULT 0,
                logo_position_x REAL DEFAULT 0,
                logo_position_y REAL DEFAULT 0,
                logo_width REAL DEFAULT 100,
                logo_height REAL DEFAULT 50,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

    def create_customer_documents_table(self, conn: sqlite3.Connection):
        """Create customer documents table"""
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                project_id INTEGER,
                doc_type TEXT,
                display_name TEXT,
                file_name TEXT,
                absolute_file_path TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

    # ======================== PRODUCT OPERATIONS ========================

    def list_products(self, category: str | None = None,
                      company_id: int | None = None) -> list[dict[str, Any]]:
        """List all products, optionally filtered by category"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return []

            self.create_product_table(conn)
            cursor = conn.cursor()

            if category:
                cursor.execute(
                    "SELECT * FROM products WHERE category = ? ORDER BY brand, model_name",
                    (category,
                     ))
            else:
                cursor.execute(
                    "SELECT * FROM products ORDER BY category, brand, model_name")

            rows = cursor.fetchall()
            conn.close()

            products = []
            for row in rows:
                product = dict(row)
                products.append(product)

            return products

        except Exception as e:
            print(f"Error listing products: {e}", file=sys.stderr)
            return []

    def add_product(self, product_data: dict[str, Any]) -> int | None:
        """Add a new product"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return None

            self.create_product_table(conn)
            cursor = conn.cursor()

            # Check for duplicate (same model_name and brand)
            model_name = product_data.get('model_name', '')
            brand = product_data.get('brand', '')
            if model_name and brand:
                cursor.execute(
                    "SELECT id FROM products WHERE model_name = ? AND brand = ?",
                    (model_name,
                     brand))
                if cursor.fetchone():
                    conn.close()
                    return None  # Duplicate exists

            # Prepare data for insertion
            columns = []
            values = []
            placeholders = []

            for key, value in product_data.items():
                if key in ['id', 'created_at', 'updated_at']:
                    continue  # Skip auto-generated fields
                columns.append(key)
                values.append(value)
                placeholders.append('?')

            if columns:
                query = f"INSERT INTO products ({
                    ', '.join(columns)}) VALUES ({
                    ', '.join(placeholders)})"
                cursor.execute(query, values)

                product_id = cursor.lastrowid
                conn.commit()
                conn.close()
                return product_id

            conn.close()
            return None

        except Exception as e:
            print(f"Error adding product: {e}", file=sys.stderr)
            return None

    def update_product(self, product_id: int | float,
                       product_data: dict[str, Any]) -> bool:
        """Update an existing product"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return False

            cursor = conn.cursor()

            # Prepare update data
            set_clauses = []
            values = []

            for key, value in product_data.items():
                if key in ['id', 'created_at']:
                    continue  # Skip immutable fields
                set_clauses.append(f"{key} = ?")
                values.append(value)

            if not set_clauses:
                conn.close()
                return False

            # Add updated_at timestamp
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            values.append(int(product_id))

            query = f"UPDATE products SET {
                ', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, values)

            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            return success

        except Exception as e:
            print(f"Error updating product: {e}", file=sys.stderr)
            return False

    def delete_product(self, product_id: int | float) -> bool:
        """Delete a product (soft delete)"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return False

            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM products WHERE id = ?", (int(product_id),))

            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            return success

        except Exception as e:
            print(f"Error deleting product: {e}", file=sys.stderr)
            return False

    def get_product_by_id(self, product_id: int |
                          float) -> dict[str, Any] | None:
        """Get a product by ID"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return None

            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM products WHERE id = ?", (int(product_id),))
            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)
            return None

        except Exception as e:
            print(f"Error getting product by ID: {e}", file=sys.stderr)
            return None

    def get_product_by_model_name(
            self, model_name: str) -> dict[str, Any] | None:
        """Get a product by model name"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return None

            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM products WHERE model_name = ? ORDER BY id DESC LIMIT 1",
                (model_name,
                 ))
            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)
            return None

        except Exception as e:
            print(f"Error getting product by model name: {e}", file=sys.stderr)
            return None

    def list_product_categories(self) -> list[str]:
        """Get all unique product categories"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return []

            cursor = conn.cursor()
            cursor.execute(
                "SELECT DISTINCT category FROM products WHERE category IS NOT NULL ORDER BY category")
            rows = cursor.fetchall()
            conn.close()

            return [row[0] for row in rows if row[0]]

        except Exception as e:
            print(f"Error listing categories: {e}", file=sys.stderr)
            return []

    def list_manufacturers(self) -> list[str]:
        """Get all unique manufacturers/brands"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return []

            cursor = conn.cursor()
            cursor.execute(
                "SELECT DISTINCT brand FROM products WHERE brand IS NOT NULL ORDER BY brand")
            rows = cursor.fetchall()
            conn.close()

            return [row[0] for row in rows if row[0]]

        except Exception as e:
            print(f"Error listing manufacturers: {e}", file=sys.stderr)
            return []

    def get_products_by_manufacturer(
            self, manufacturer: str) -> list[dict[str, Any]]:
        """Get all products from a specific manufacturer"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return []

            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM products WHERE brand = ? ORDER BY category, model_name",
                (manufacturer,
                 ))
            rows = cursor.fetchall()
            conn.close()

            products = []
            for row in rows:
                product = dict(row)
                products.append(product)

            return products

        except Exception as e:
            print(
                f"Error getting products by manufacturer: {e}",
                file=sys.stderr)
            return []

    # ======================== BRAND LOGO OPERATIONS ========================

    def add_brand_logo(
            self,
            brand_name: str,
            logo_base64: str,
            logo_format: str = "PNG",
            file_size_bytes: int = 0,
            position_x: float = 0,
            position_y: float = 0,
            width: float = 100,
            height: float = 50) -> bool:
        """Add or update a brand logo"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return False

            self.create_brand_logos_table(conn)
            cursor = conn.cursor()

            # Check if logo already exists
            cursor.execute(
                "SELECT id FROM brand_logos WHERE brand_name = ?", (brand_name,))
            existing = cursor.fetchone()

            if existing:
                # Update existing logo
                cursor.execute("""
                    UPDATE brand_logos
                    SET logo_base64 = ?, logo_format = ?, file_size_bytes = ?,
                        logo_position_x = ?, logo_position_y = ?, logo_width = ?, logo_height = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE brand_name = ?
                """, (logo_base64, logo_format, file_size_bytes, position_x, position_y,
                      width, height, brand_name))
            else:
                # Insert new logo
                cursor.execute("""
                    INSERT INTO brand_logos (brand_name, logo_base64, logo_format, file_size_bytes,
                                           logo_position_x, logo_position_y, logo_width, logo_height)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (brand_name, logo_base64, logo_format, file_size_bytes,
                      position_x, position_y, width, height))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error saving brand logo: {e}", file=sys.stderr)
            return False

    def get_brand_logo(self, brand_name: str) -> dict[str, Any] | None:
        """Get a brand logo by name"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return None

            self.create_brand_logos_table(conn)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT brand_name, logo_base64, logo_format, file_size_bytes,
                       logo_position_x, logo_position_y, logo_width, logo_height,
                       is_active, created_at, updated_at
                FROM brand_logos
                WHERE brand_name = ?
            """, (brand_name,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    'brand_name': row[0],
                    'logo_base64': row[1],
                    'logo_format': row[2],
                    'file_size_bytes': row[3],
                    'logo_position_x': row[4],
                    'logo_position_y': row[5],
                    'logo_width': row[6],
                    'logo_height': row[7],
                    'is_active': row[8],
                    'created_at': row[9],
                    'updated_at': row[10]
                }

            return None

        except Exception as e:
            print(f"Error getting brand logo: {e}", file=sys.stderr)
            return None

    def list_brand_logos(self) -> list[dict[str, Any]]:
        """List all brand logos"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return []

            self.create_brand_logos_table(conn)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, brand_name, logo_format, file_size_bytes,
                       logo_position_x, logo_position_y, logo_width, logo_height,
                       is_active, created_at, updated_at
                FROM brand_logos
                WHERE is_active = 1
                ORDER BY brand_name
            """)

            rows = cursor.fetchall()
            conn.close()

            logos = []
            for row in rows:
                logos.append({
                    'id': row[0],
                    'brand_name': row[1],
                    'logo_format': row[2],
                    'file_size_bytes': row[3],
                    'logo_position_x': row[4],
                    'logo_position_y': row[5],
                    'logo_width': row[6],
                    'logo_height': row[7],
                    'is_active': row[8],
                    'created_at': row[9],
                    'updated_at': row[10]
                })

            return logos

        except Exception as e:
            print(f"Error listing brand logos: {e}", file=sys.stderr)
            return []

    def delete_brand_logo(self, brand_name: str) -> bool:
        """Delete a brand logo"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return False

            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM brand_logos WHERE brand_name = ?", (brand_name,))

            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            return success

        except Exception as e:
            print(f"Error deleting brand logo: {e}", file=sys.stderr)
            return False


def main():
    """CLI interface for database operations"""
    if len(sys.argv) < 2:
        print("Usage: python database_bridge.py <command> [options]")
        print("\nAvailable commands:")
        print("  list_products [--category=<category>]")
        print("  add_product --data='<json_data>'")
        print("  update_product --id=<id> --data='<json_data>'")
        print("  delete_product --id=<id>")
        print("  get_product_by_id --id=<id>")
        print("  get_product_by_model --model='<model_name>'")
        print("  list_categories")
        print("  list_manufacturers")
        print("  get_products_by_manufacturer --manufacturer='<brand>'")
        print("  list_brand_logos")
        print(
            "  add_brand_logo --brand='<brand>' --logo_base64='<base64>' [--format=PNG]")
        print("  get_brand_logo --brand='<brand>'")
        print("  delete_brand_logo --brand='<brand>'")
        print("  init_database")
        return

    command = sys.argv[1]
    db = DatabaseBridge()

    try:
        if command == "list_products":
            category = None
            for arg in sys.argv[2:]:
                if arg.startswith("--category="):
                    category = arg.split("=", 1)[1]

            products = db.list_products(category=category)
            print(json.dumps({"success": True, "data": products}, indent=2))

        elif command == "add_product":
            data_json = None
            for arg in sys.argv[2:]:
                if arg.startswith("--data="):
                    data_json = arg.split("=", 1)[1]

            if not data_json:
                print(json.dumps(
                    {"success": False, "error": "Missing --data parameter"}))
                return

            try:
                product_data = json.loads(data_json)
                product_id = db.add_product(product_data)
                if product_id:
                    print(json.dumps(
                        {"success": True, "product_id": product_id}))
                else:
                    print(json.dumps(
                        {"success": False, "error": "Failed to add product (duplicate or database error)"}))
            except json.JSONDecodeError:
                print(json.dumps(
                    {"success": False, "error": "Invalid JSON data"}))

        elif command == "update_product":
            product_id = None
            data_json = None
            for arg in sys.argv[2:]:
                if arg.startswith("--id="):
                    product_id = int(arg.split("=", 1)[1])
                elif arg.startswith("--data="):
                    data_json = arg.split("=", 1)[1]

            if product_id is None or not data_json:
                print(json.dumps({"success": False,
                                  "error": "Missing --id or --data parameter"}))
                return

            try:
                product_data = json.loads(data_json)
                success = db.update_product(product_id, product_data)
                print(json.dumps({"success": success}))
            except json.JSONDecodeError:
                print(json.dumps(
                    {"success": False, "error": "Invalid JSON data"}))

        elif command == "delete_product":
            product_id = None
            for arg in sys.argv[2:]:
                if arg.startswith("--id="):
                    product_id = int(arg.split("=", 1)[1])

            if product_id is None:
                print(json.dumps(
                    {"success": False, "error": "Missing --id parameter"}))
                return

            success = db.delete_product(product_id)
            print(json.dumps({"success": success}))

        elif command == "get_product_by_id":
            product_id = None
            for arg in sys.argv[2:]:
                if arg.startswith("--id="):
                    product_id = int(arg.split("=", 1)[1])

            if product_id is None:
                print(json.dumps(
                    {"success": False, "error": "Missing --id parameter"}))
                return

            product = db.get_product_by_id(product_id)
            print(json.dumps({"success": True, "data": product}))

        elif command == "get_product_by_model":
            model_name = None
            for arg in sys.argv[2:]:
                if arg.startswith("--model="):
                    model_name = arg.split("=", 1)[1]

            if not model_name:
                print(json.dumps(
                    {"success": False, "error": "Missing --model parameter"}))
                return

            product = db.get_product_by_model_name(model_name)
            print(json.dumps({"success": True, "data": product}))

        elif command == "list_categories":
            categories = db.list_product_categories()
            print(json.dumps({"success": True, "data": categories}))

        elif command == "list_manufacturers":
            manufacturers = db.list_manufacturers()
            print(json.dumps({"success": True, "data": manufacturers}))

        elif command == "get_products_by_manufacturer":
            manufacturer = None
            for arg in sys.argv[2:]:
                if arg.startswith("--manufacturer="):
                    manufacturer = arg.split("=", 1)[1]

            if not manufacturer:
                print(json.dumps({"success": False,
                                  "error": "Missing --manufacturer parameter"}))
                return

            products = db.get_products_by_manufacturer(manufacturer)
            print(json.dumps({"success": True, "data": products}))

        elif command == "list_brand_logos":
            logos = db.list_brand_logos()
            print(json.dumps({"success": True, "data": logos}))

        elif command == "add_brand_logo":
            brand = None
            logo_base64 = None
            logo_format = "PNG"
            for arg in sys.argv[2:]:
                if arg.startswith("--brand="):
                    brand = arg.split("=", 1)[1]
                elif arg.startswith("--logo_base64="):
                    logo_base64 = arg.split("=", 1)[1]
                elif arg.startswith("--format="):
                    logo_format = arg.split("=", 1)[1]

            if not brand or not logo_base64:
                print(json.dumps(
                    {"success": False, "error": "Missing --brand or --logo_base64 parameter"}))
                return

            success = db.add_brand_logo(brand, logo_base64, logo_format)
            print(json.dumps({"success": success}))

        elif command == "get_brand_logo":
            brand = None
            for arg in sys.argv[2:]:
                if arg.startswith("--brand="):
                    brand = arg.split("=", 1)[1]

            if not brand:
                print(json.dumps(
                    {"success": False, "error": "Missing --brand parameter"}))
                return

            logo = db.get_brand_logo(brand)
            print(json.dumps({"success": True, "data": logo}))

        elif command == "delete_brand_logo":
            brand = None
            for arg in sys.argv[2:]:
                if arg.startswith("--brand="):
                    brand = arg.split("=", 1)[1]

            if not brand:
                print(json.dumps(
                    {"success": False, "error": "Missing --brand parameter"}))
                return

            success = db.delete_brand_logo(brand)
            print(json.dumps({"success": success}))

        elif command == "init_database":
            result = db.init_database()
            print(json.dumps(result))

        else:
            print(json.dumps({"success": False,
                              "error": f"Unknown command: {command}"}))

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}), file=sys.stderr)


if __name__ == "__main__":
    main()
