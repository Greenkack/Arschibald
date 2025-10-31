#!/usr/bin/env python3
"""
Master-Tool: Führt alle Optimierungen in einem Rutsch durch
"""


def run_all_optimizations():
    """Führt alle Optimierungstools aus"""

    print("🚀 MASTER-OPTIMIERUNG GESTARTET")
    print("=" * 50)

    optimizations = [
        ("🧹 Emoji-Bereinigung", "remove_emojis_from_files()"),
        ("🔧 Streamlit-Fixes", "fix_streamlit_deprecations()"),
        ("📊 Code-Statistiken", "analyze_code_stats()"),
        ("🗄️ Datenbank-Bereinigung", "clean_database()"),
        ("🧹 Debug-Bereinigung", "clean_debug_statements()"),
        ("🔍 Duplikat-Suche", "find_duplicate_files()"),
    ]

    for name, func_call in optimizations:
        print(f"\n{name}...")
        try:
            exec(func_call)
            print(f"✅ {name} abgeschlossen")
        except Exception as e:
            print(f"❌ Fehler bei {name}: {e}")

    print("\n🎉 MASTER-OPTIMIERUNG ABGESCHLOSSEN!")
    print("📋 Empfohlene nächste Schritte:")
    print("   1. Git-Commit der bereinigten Dateien")
    print("   2. Tests ausführen")
    print("   3. App-Performance prüfen")


if __name__ == "__main__":
    run_all_optimizations()
