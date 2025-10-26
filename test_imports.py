#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("🚀 Python-Test startet...")

try:
    print("1. Importiere sys...")
    import sys
    print(f"   ✅ Python Version: {sys.version}")
    
    print("2. Teste Streamlit Import...")
    import streamlit as st
    print(f"   ✅ Streamlit Version: {st.__version__}")
    
    print("3. Teste weitere Module...")
    import pandas as pd
    print(f"   ✅ Pandas: {pd.__version__}")
    
    import numpy as np
    print(f"   ✅ NumPy: {np.__version__}")
    
    print("4. Teste Database Import...")
    import os
    if os.path.exists("database.py"):
        try:
            import database
            print("   ✅ Database-Modul geladen")
        except Exception as e:
            print(f"   ❌ Database-Fehler: {e}")
    else:
        print("   ⚠️ Database.py nicht gefunden")
    
    print("\n🎉 Alle Tests erfolgreich!")
    
except Exception as e:
    print(f"❌ FEHLER: {e}")
    import traceback
    print("\nDetaillierter Traceback:")
    traceback.print_exc()