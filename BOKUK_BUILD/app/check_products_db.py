#!/usr/bin/env python3
"""
Script zum Überprüfen der Produktdatenbank Struktur
"""
import os
import sqlite3

import pandas as pd


def check_excel_products():
    """Überprüft die Excel Produktdatenbank"""
    excel_path = "data/Produkte.xlsx"
    if os.path.exists(excel_path):
        try:
            df = pd.read_excel(excel_path)
            print("=== PRODUKTDATENBANK EXCEL STRUKTUR ===")
            print(f"Anzahl Zeilen: {len(df)}")
            print(f"Anzahl Spalten: {len(df.columns)}")
            print(f"\nSpalten: {list(df.columns)}")

            print("\nErste 3 Zeilen:")
            print(df.head(3).to_string())

            # Kategorien analysieren
            if 'kategorie' in df.columns:
                print("\nKategorien:")
                print(df['kategorie'].value_counts())

            # Hersteller analysieren
            if 'hersteller' in df.columns:
                print("\nHersteller:")
                print(df['hersteller'].value_counts())

        except Exception as e:
            print(f"Fehler beim Lesen der Excel: {e}")
    else:
        print("Excel Datei nicht gefunden!")


def check_sqlite_products():
    """Überprüft ob bereits eine Produkttabelle in SQLite existiert"""
    db_path = "data/app_data.db"
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Tabellen auflisten
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print("=== SQLITE TABELLEN ===")
            for table in tables:
                print(f"- {table[0]}")

            # Prüfen ob products Tabelle existiert
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='products';")
            if cursor.fetchone():
                cursor.execute("SELECT COUNT(*) FROM products")
                count = cursor.fetchone()[0]
                print(f"\nProducts Tabelle: {count} Einträge")

                cursor.execute("PRAGMA table_info(products)")
                columns = cursor.fetchall()
                print("Spalten in products:")
                for col in columns:
                    print(f"  {col[1]} - {col[2]}")
            else:
                print("\nKeine products Tabelle gefunden")

            conn.close()
        except Exception as e:
            print(f"Fehler beim SQLite Check: {e}")
    else:
        print("SQLite DB nicht gefunden!")


if __name__ == "__main__":
    check_excel_products()
    print("\n" + "=" * 50 + "\n")
    check_sqlite_products()
