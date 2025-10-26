#!/usr/bin/env python3
"""
Automatischer Test-Runner für die App
"""
import glob
import importlib.util
import os
import subprocess
import sys
import time


def run_python_tests():
    """Führt alle Python-Tests aus"""

    # Finde Test-Dateien
    test_files = glob.glob("test_*.py") + \
        glob.glob("*_test.py") + glob.glob("tests/*.py")

    if not test_files:
        print("❌ Keine Test-Dateien gefunden")
        return

    print(f"🧪 TESTE {len(test_files)} Test-Dateien:")

    passed = 0
    failed = 0

    for test_file in test_files:
        print(f"\n📋 {os.path.basename(test_file)}:")
        try:
            result = subprocess.run([sys.executable, test_file],
                                    capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                print("  ✅ BESTANDEN")
                passed += 1
            else:
                print("  ❌ FEHLGESCHLAGEN")
                print(f"     {result.stderr[:200]}...")
                failed += 1

        except subprocess.TimeoutExpired:
            print("  ⏱️ TIMEOUT")
            failed += 1
        except Exception as e:
            print(f"  ❌ FEHLER: {e}")
            failed += 1

    print("\n📊 TEST-ERGEBNISSE:")
    print(f"✅ Bestanden: {passed}")
    print(f"❌ Fehlgeschlagen: {failed}")
    print(f"📈 Erfolgsrate: {passed / (passed + failed) * 100:.1f}%" if (
        passed + failed) > 0 else "Keine Tests")


def smoke_test_app():
    """Führt Smoke-Tests der Hauptfunktionen aus"""

    print("\n🔥 SMOKE-TESTS:")

    tests = [
        ("Import gui.py",
         lambda: importlib.util.spec_from_file_location(
             "gui",
             "gui.py") is not None),
        ("Import data_input.py",
         lambda: importlib.util.spec_from_file_location(
             "data_input",
             "data_input.py") is not None),
        ("Database exists",
         lambda: os.path.exists("solar_app.db")),
        ("Input folder exists",
         lambda: os.path.exists("input/")),
        ("Requirements file",
         lambda: os.path.exists("requirements.txt")),
    ]

    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"  ✅ {test_name}")
            else:
                print(f"  ❌ {test_name}")
        except Exception as e:
            print(f"  ❌ {test_name}: {e}")


def benchmark_key_functions():
    """Benchmarkt wichtige App-Funktionen"""

    print("\n⚡ PERFORMANCE-BENCHMARK:")

    # Importiere relevante Module
    try:
        import importlib.util

        # Test verschiedene Module
        modules_to_test = [
            "analysis.py",
            "calculations.py",
            "complete_crm_system.py"
        ]

        for module_file in modules_to_test:
            if os.path.exists(module_file):
                start_time = time.time()

                try:
                    spec = importlib.util.spec_from_file_location(
                        "test_module", module_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    import_time = time.time() - start_time
                    print(f"  📦 {module_file}: {import_time:.3f}s Import-Zeit")

                except Exception:
                    print(f"  ❌ {module_file}: Import-Fehler")

    except Exception as e:
        print(f"  ❌ Benchmark-Fehler: {e}")


if __name__ == "__main__":
    run_python_tests()
    smoke_test_app()
    benchmark_key_functions()
