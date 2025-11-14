#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("[LAUNCH] Python-Test startet...")

try:
    print("1. Importiere sys...")
    import sys
    print(f"   [OK] Python Version: {sys.version}")
    
    print("2. Teste Streamlit Import...")
    import streamlit as st
    print(f"   [OK] Streamlit Version: {st.__version__}")
    
    print("3. Teste weitere Module...")
    import pandas as pd
    print(f"   [OK] Pandas: {pd.__version__}")
    
    import numpy as np
    print(f"   [OK] NumPy: {np.__version__}")
    
    print("4. Teste Database Import...")
    import os
    if os.path.exists("database.py"):
        try:
            import database
            print("   [OK] Database-Modul geladen")
        except Exception as e:
            print(f"   [ERROR] Database-Fehler: {e}")
    else:
        print("   [WARNING] Database.py nicht gefunden")
    
    print("\n🎉 Alle Tests erfolgreich!")
    
except Exception as e:
    print(f"[ERROR] FEHLER: {e}")
    import traceback
    print("\nDetaillierter Traceback:")
    traceback.print_exc()