#!/usr/bin/env python3
"""
Test-Skript um zu prüfen, ob die pdf_template_engine importiert werden kann
"""

print("Testing pdf_template_engine import...")

try:
    from pdf_template_engine import (
        build_dynamic_data,
        generate_overlay,
        merge_with_background,
    )
    print("✓ SUCCESS: pdf_template_engine import erfolgreich")
    print(f"  build_dynamic_data: {build_dynamic_data}")
    print(f"  generate_overlay: {generate_overlay}")
    print(f"  merge_with_background: {merge_with_background}")
except Exception as e:
    print(f"✗ FEHLER: pdf_template_engine import fehlgeschlagen: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting individual module imports...")

try:
    from pdf_template_engine.placeholders import build_dynamic_data
    print("✓ placeholders.build_dynamic_data importiert")
except Exception as e:
    print(f"✗ placeholders.build_dynamic_data fehlgeschlagen: {e}")

try:
    from pdf_template_engine.dynamic_overlay import (
        generate_overlay,
        merge_with_background,
    )
    print("✓ dynamic_overlay Funktionen importiert")
except Exception as e:
    print(f"✗ dynamic_overlay Funktionen fehlgeschlagen: {e}")

print("\nTemplate engine test abgeschlossen.")
