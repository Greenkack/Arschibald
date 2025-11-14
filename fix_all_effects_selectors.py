"""
Script um ALLE Effekte mit modernen Expander/Dropdown-Selektoren zu erweitern
"""

# Neue Selektoren die zu JEDEM Effekt hinzugefügt werden müssen
MODERN_SELECTORS = {
    "expander": [
        "details[data-testid=\"stExpander\"] summary",
        ".streamlit-expanderHeader",
        "details summary",
        "section[data-testid=\"stSidebar\"] details[data-testid=\"stExpander\"] summary",
        "section[data-testid=\"stSidebar\"] .streamlit-expanderHeader"
    ],
    "dropdown": [
        "div[data-baseweb=\"select\"]",
        ".stSelectbox > div > div",
        "div[data-testid=\"stSelectbox\"] > div",
        "section[data-testid=\"stSidebar\"] div[data-baseweb=\"select\"]",
        "section[data-testid=\"stSidebar\"] .stSelectbox > div > div"
    ],
    "number_input": [
        "button[data-testid=\"stNumberInputStepUp\"]",
        "button[data-testid=\"stNumberInputStepDown\"]",
        "section[data-testid=\"stSidebar\"] button[data-testid=\"stNumberInputStepUp\"]",
        "section[data-testid=\"stSidebar\"] button[data-testid=\"stNumberInputStepDown\"]"
    ],
    "checkbox": [
        "div[data-baseweb=\"checkbox\"]",
        "div[data-testid=\"stCheckbox\"] label",
        "section[data-testid=\"stSidebar\"] div[data-baseweb=\"checkbox\"]"
    ]
}

# Alte Selektoren die ersetzt werden müssen
OLD_SELECTORS = {
    "expander": [".streamlit-expanderHeader"],
    "dropdown": [],  # Oft gar nicht vorhanden
    "number_input": ["button[data-testid=\"stNumberInputStepUp\"]", "button[data-testid=\"stNumberInputStepDown\"]"],
    "checkbox": ["div[data-baseweb=\"checkbox\"]"]
}

print("Modernisierung der Selektoren:")
print(f"\n[OK] Expander: {len(MODERN_SELECTORS['expander'])} Selektoren")
print(f"[OK] Dropdown: {len(MODERN_SELECTORS['dropdown'])} Selektoren")
print(f"[OK] Number Input: {len(MODERN_SELECTORS['number_input'])} Selektoren")
print(f"[OK] Checkbox: {len(MODERN_SELECTORS['checkbox'])} Selektoren")

print("\n📋 Beispiel neuer Expander-Selektor-Block:")
print(",\n        ".join(MODERN_SELECTORS['expander']) + ":hover {")
print("    /* Effekt-spezifische Styles hier */")
print("}")
