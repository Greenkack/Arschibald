"""
Universal-Template für Expander/Dropdown-Hover (wird in JEDEN Effekt eingefügt)
"""


def generate_universal_hover_css(effect_name, effect_properties):
    """
    Generiert universelle Hover-CSS für Expander, Dropdowns, Number Inputs, Checkboxes

    Args:
        effect_name: Name des Effekts (z.B. "GRADIENT + SLIDE")
        effect_properties: Dict mit spezifischen CSS-Properties pro Element-Typ
    """

    template = f"""
        /* ========== EXPANDER HOVER ({effect_name}) ========== */
        details[data-testid="stExpander"] summary:hover,
        .streamlit-expanderHeader:hover,
        details summary:hover,
        section[data-testid="stSidebar"] details[data-testid="stExpander"] summary:hover,
        section[data-testid="stSidebar"] .streamlit-expanderHeader:hover {{
            {effect_properties.get('expander', 'transform: scale(1.01); box-shadow: 0 4px 12px rgba(0,0,0,0.15);')}
        }}

        /* ========== DROPDOWN HOVER ({effect_name}) ========== */
        div[data-baseweb="select"]:hover,
        .stSelectbox > div > div:hover,
        div[data-testid="stSelectbox"] > div:hover,
        section[data-testid="stSidebar"] div[data-baseweb="select"]:hover,
        section[data-testid="stSidebar"] .stSelectbox > div > div:hover {{
            {effect_properties.get('dropdown', 'transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.15);')}
        }}

        /* ========== NUMBER INPUT HOVER ({effect_name}) ========== */
        button[data-testid="stNumberInputStepUp"]:hover,
        button[data-testid="stNumberInputStepDown"]:hover,
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"]:hover,
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"]:hover {{
            {effect_properties.get('number_input', 'transform: scale(1.08); box-shadow: 0 4px 12px rgba(0,0,0,0.2);')}
        }}

        /* ========== CHECKBOX HOVER ({effect_name}) ========== */
        div[data-baseweb="checkbox"]:hover,
        div[data-testid="stCheckbox"] label:hover,
        section[data-testid="stSidebar"] div[data-baseweb="checkbox"]:hover {{
            {effect_properties.get('checkbox', 'transform: scale(1.05); box-shadow: 0 2px 8px rgba(0,0,0,0.15);')}
        }}
"""
    return template


# Beispiele für verschiedene Effekte
effects_config = {
    "gradient_slide": {
        "name": "GRADIENT + SLIDE",
        "expander": "background: linear-gradient(90deg, rgba(255,0,150,0.3), rgba(0,204,255,0.3)); transform: translateX(5px);",
        "dropdown": "background: linear-gradient(90deg, rgba(255,0,150,0.2), rgba(0,204,255,0.2)); transform: translateX(3px);",
        "number_input": "background: linear-gradient(135deg, rgba(255,0,150,0.3), rgba(0,204,255,0.3)); transform: scale(1.1);",
        "checkbox": "background: linear-gradient(135deg, rgba(255,0,150,0.2), rgba(0,204,255,0.2)); transform: scale(1.05);"
    },
    "glass_morph": {
        "name": "GLASS MORPH",
        "expander": "background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0,0,0,0.1);",
        "dropdown": "background: rgba(255, 255, 255, 0.12); backdrop-filter: blur(8px); box-shadow: 0 6px 24px rgba(0,0,0,0.08);",
        "number_input": "background: rgba(255, 255, 255, 0.2); backdrop-filter: blur(6px); transform: scale(1.05);",
        "checkbox": "background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(5px);"
    }
}

print("Universal Hover Template Generator\n" + "=" * 50)
for effect_key, config in effects_config.items():
    print(f"\n{'=' * 50}")
    print(f"Effekt: {config['name']}")
    print(f"{'=' * 50}")
    print(generate_universal_hover_css(config['name'], config))
