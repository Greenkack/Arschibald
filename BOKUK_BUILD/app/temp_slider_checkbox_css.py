# Temporäre Datei - CSS für Slider und Checkboxen
# Diesen Code in gui.py nach Zeile 1291 einfügen

SLIDER_CHECKBOX_CSS = """
    # ========================================================================
    # ZUSÄTZLICHE GLOBALE EFFEKTE: SLIDER & CHECKBOXEN
    # ========================================================================
    st.markdown('''
    <style>
    /* ========== GLOBALE SLIDER-EFFEKTE (+ / - BUTTONS) ========== */
    /* Shimmer- und Pulse-Animationen für Slider-Increment/Decrement-Buttons */

    /* Slider Plus/Minus Buttons */
    button[data-testid="stNumberInputStepUp"],
    button[data-testid="stNumberInputStepDown"],
    div[data-testid="stNumberInput"] button,
    .step-up,
    .step-down {
        position: relative !important;
        overflow: hidden !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
    }

    /* Shimmer-Effekt für Slider-Buttons */
    button[data-testid="stNumberInputStepUp"]::before,
    button[data-testid="stNumberInputStepDown"]::before,
    div[data-testid="stNumberInput"] button::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.25), transparent) !important;
        transition: left 0.4s ease !important;
        pointer-events: none !important;
        z-index: 1 !important;
    }

    /* Shimmer aktivieren beim Hover */
    button[data-testid="stNumberInputStepUp"]:hover::before,
    button[data-testid="stNumberInputStepDown"]:hover::before,
    div[data-testid="stNumberInput"] button:hover::before {
        left: 100% !important;
    }

    /* Hover-Effekte für Slider-Buttons */
    button[data-testid="stNumberInputStepUp"]:hover,
    button[data-testid="stNumberInputStepDown"]:hover,
    div[data-testid="stNumberInput"] button:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(102, 126, 234, 0.08) 100%) !important;
        box-shadow: 0 3px 10px rgba(102, 126, 234, 0.2) !important;
        transform: scale(1.05) !important;
        animation: sliderButtonPulse 1.5s ease-in-out infinite !important;
    }

    @keyframes sliderButtonPulse {
        0%, 100% {
            box-shadow: 0 3px 10px rgba(102, 126, 234, 0.2);
            transform: scale(1.05);
        }
        50% {
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
            transform: scale(1.08);
        }
    }

    /* Active State (beim Klicken) */
    button[data-testid="stNumberInputStepUp"]:active,
    button[data-testid="stNumberInputStepDown"]:active,
    div[data-testid="stNumberInput"] button:active {
        transform: scale(0.95) !important;
        box-shadow: 0 1px 5px rgba(102, 126, 234, 0.3) inset !important;
    }

    /* Slider Track Hover */
    div[data-testid="stSlider"] div[role="slider"]:hover {
        box-shadow: 0 0 0 8px rgba(102, 126, 234, 0.15) !important;
        transform: scale(1.1) !important;
        transition: all 0.3s ease !important;
    }

    /* ========== ENDE GLOBALE SLIDER-EFFEKTE ========== */

    /* ========== GLOBALE CHECKBOX-EFFEKTE ========== */
    /* Shimmer- und Pulse-Animationen für Checkboxen */

    /* Checkbox Container */
    div[data-testid="stCheckbox"],
    .stCheckbox,
    label[data-testid="stCheckbox"] {
        position: relative !important;
        cursor: pointer !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    /* Checkbox Label Hover-Effekt */
    div[data-testid="stCheckbox"]:hover,
    .stCheckbox:hover,
    label[data-testid="stCheckbox"]:hover {
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.05) 0%, transparent 100%) !important;
        padding-left: 8px !important;
        border-radius: 6px !important;
        transform: translateX(3px) !important;
    }

    /* Checkbox Input Box */
    div[data-testid="stCheckbox"] input[type="checkbox"],
    .stCheckbox input[type="checkbox"],
    input[type="checkbox"] {
        position: relative !important;
        cursor: pointer !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    /* Checkbox Hover-Effekt - Shimmer */
    div[data-testid="stCheckbox"]:hover input[type="checkbox"],
    .stCheckbox:hover input[type="checkbox"] {
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15) !important;
        border-color: rgba(102, 126, 234, 0.6) !important;
        animation: checkboxPulse 1.5s ease-in-out infinite !important;
    }

    @keyframes checkboxPulse {
        0%, 100% {
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15);
            transform: scale(1);
        }
        50% {
            box-shadow: 0 0 0 6px rgba(102, 126, 234, 0.25);
            transform: scale(1.05);
        }
    }

    /* Checked Checkbox - Pulse-Effekt */
    div[data-testid="stCheckbox"] input[type="checkbox"]:checked,
    .stCheckbox input[type="checkbox"]:checked,
    input[type="checkbox"]:checked {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(102, 126, 234, 0.7) 100%) !important;
        border-color: rgba(102, 126, 234, 1) !important;
        animation: checkboxCheckedPulse 2s ease-in-out infinite !important;
    }

    @keyframes checkboxCheckedPulse {
        0%, 100% {
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
        }
        50% {
            box-shadow: 0 0 0 5px rgba(102, 126, 234, 0.3);
        }
    }

    /* Checkbox Checkmark - Shimmer-Effekt */
    div[data-testid="stCheckbox"] input[type="checkbox"]:checked::after,
    .stCheckbox input[type="checkbox"]:checked::after {
        animation: checkmarkShimmer 2s ease-in-out infinite !important;
    }

    @keyframes checkmarkShimmer {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.8;
            filter: brightness(1.2);
        }
    }

    /* Radio Buttons - Ähnliche Effekte */
    div[data-testid="stRadio"] label:hover,
    .stRadio label:hover {
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.05) 0%, transparent 100%) !important;
        padding-left: 8px !important;
        border-radius: 6px !important;
        transform: translateX(3px) !important;
        transition: all 0.3s ease !important;
    }

    div[data-testid="stRadio"] input[type="radio"]:hover,
    .stRadio input[type="radio"]:hover {
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15) !important;
        animation: checkboxPulse 1.5s ease-in-out infinite !important;
    }

    /* ========== ENDE GLOBALE CHECKBOX-EFFEKTE ========== */

    </style>
    ''', unsafe_allow_html=True)
"""
