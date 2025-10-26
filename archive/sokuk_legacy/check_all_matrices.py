#!/usr/bin/env python3
"""
Alle Matrix-Dateien überprüfen
"""

import os

import pandas as pd


def check_matrix_file(file_path):
    """Überprüfe eine Matrix-Datei"""
    print(f"\n📁 {file_path}")
    print("=" * 50)

    if not os.path.exists(file_path):
        print("❌ Datei existiert nicht!")
        return

    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, index_col=0)
        else:
            df = pd.read_excel(file_path, index_col=0)

        print(f"📊 Shape: {df.shape}")
        print(f"📋 Index range: {df.index.min()} - {df.index.max()}")

        # Prüfe 'Ohne Speicher' Spalte
        if 'Ohne Speicher' in df.columns:
            ohne_speicher = df['Ohne Speicher']
            print("\n💰 'Ohne Speicher' Preise:")
            for modules in [7, 10, 15, 20, 25, 30]:
                if modules in ohne_speicher.index:
                    preis = ohne_speicher.loc[modules]
                    print(f"   {modules} Module: {preis} €")

            # Spezifische Checks
            if 20 in ohne_speicher.index:
                preis_20 = ohne_speicher.loc[20]
                if preis_20 == 15113.50:
                    print("✅ 20 Module haben den erwarteten Preis!")
                elif preis_20 == 13855.30:
                    print("❌ 20 Module haben den alten falschen Preis!")
                else:
                    print(f"❓ 20 Module: unerwarteter Preis {preis_20}")
        else:
            print("❌ 'Ohne Speicher' Spalte nicht gefunden!")
            print(f"Verfügbare Spalten: {list(df.columns)[:5]}...")

    except Exception as e:
        print(f"❌ Fehler beim Lesen: {e}")


def main():
    print("🔍 ALLE MATRIX-DATEIEN ÜBERPRÜFEN")
    print("=" * 50)

    # Alle Matrix-Dateien checken
    matrix_files = [
        "data/price_matrix.xlsx",
        "data/price_matrix.csv",
        "data/price_matrix_test2.xlsx"
    ]

    for file_path in matrix_files:
        check_matrix_file(file_path)

    print("\n🔍 PRÜFE AUCH CALCULATIONS.PY FÜR HARDCODED WERTE...")

    # Suche nach hardcoded Preisen in calculations.py
    try:
        with open('calculations.py', encoding='utf-8') as f:
            content = f.read()
            if '13855' in content or '15113' in content:
                print("⚠️  GEFUNDEN: calculations.py enthält hardcoded Preise!")
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if '13855' in line or '15113' in line:
                        print(f"   Zeile {i + 1}: {line.strip()}")
            else:
                print("✅ Keine hardcoded Preise in calculations.py gefunden")
    except Exception as e:
        print(f"❌ Fehler beim Lesen von calculations.py: {e}")


if __name__ == "__main__":
    main()
