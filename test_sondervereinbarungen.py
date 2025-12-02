"""
Quick Test: Sondervereinbarungen Feature
Prüft ob der Placeholder korrekt ersetzt wird
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from pdf_template_engine.placeholders import build_dynamic_data

# Test 1: Mit Custom Text
print("=" * 60)
print("TEST 1: Mit Custom Text")
print("=" * 60)

# Simuliere Session State
test_session_state = {
    "special_agreements_text": "Kostenlose Wartung für 2 Jahre\nErweiterte Garantie auf alle Komponenten\nPrioritäts-Support"
}

# Mock session_get function
def mock_session_get(key, default=""):
    return test_session_state.get(key, default)

# Monkey-patch
import pdf_template_engine.placeholders as placeholders_module
placeholders_module.session_get = mock_session_get

# Build dynamic data
dynamic_data = build_dynamic_data()

# Check result
if "special_agreements_custom_text" in dynamic_data:
    text = dynamic_data["special_agreements_custom_text"]
    print(f"✅ Placeholder gefunden!")
    print(f"📝 Länge: {len(text)} Zeichen")
    print(f"📄 Zeilen: {len(text.split(chr(10)))}")
    print(f"\nInhalt:")
    print("-" * 40)
    print(text)
    print("-" * 40)
else:
    print("❌ Placeholder NICHT gefunden!")
    print(f"Keys in dynamic_data: {list(dynamic_data.keys())[:10]}...")

print("\n")

# Test 2: Ohne Custom Text (Fallback)
print("=" * 60)
print("TEST 2: Ohne Custom Text (Fallback)")
print("=" * 60)

test_session_state = {"special_agreements_text": ""}

dynamic_data = build_dynamic_data()

if "special_agreements_custom_text" in dynamic_data:
    text = dynamic_data["special_agreements_custom_text"]
    print(f"✅ Fallback-Text aktiv!")
    print(f"📝 Länge: {len(text)} Zeichen")
    print(f"\nInhalt:")
    print("-" * 40)
    print(text[:100] + "..." if len(text) > 100 else text)
    print("-" * 40)
else:
    print("❌ Placeholder NICHT gefunden!")

print("\n" + "=" * 60)
print("✅ Test abgeschlossen!")
print("=" * 60)
