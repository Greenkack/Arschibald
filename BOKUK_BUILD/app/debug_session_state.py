#!/usr/bin/env python3
"""
Debug-Script: Zeigt die aktuellen Session-State-Einstellungen für Multi-Angebote.
Nutze dies um zu prüfen, welche Werte tatsächlich in der App gesetzt sind.
"""

import streamlit as st

st.set_page_config(page_title="Debug Session State", page_icon="🔍")

st.title("🔍 Debug: Multi-Offer Session State")

st.markdown("---")

# Multi-Offer Settings anzeigen
st.subheader("📋 Multi-Offer Einstellungen")

if "multi_offer_settings" in st.session_state:
    settings = st.session_state.multi_offer_settings

    st.json(settings)

    # Wichtige Werte hervorheben
    st.markdown("### 🎯 Kritische Werte:")

    col1, col2, col3 = st.columns(3)

    with col1:
        rotation_enabled = settings.get("enable_product_rotation", False)
        if rotation_enabled:
            st.success("✅ Produktrotation: **EIN**")
        else:
            st.error("❌ Produktrotation: **AUS**")

        st.info(
            f"Rotations-Schritt: **{settings.get('product_rotation_step', 1)}**")

    with col2:
        price_increment = settings.get("price_increment_percent", 0)
        if price_increment > 0:
            st.success(f"✅ Preisstaffelung: **{price_increment}%**")
        else:
            st.error(
                f"❌ Preisstaffelung: **{price_increment}%** (DEAKTIVIERT!)")

        st.info(
            f"Modus: **{settings.get('price_calculation_mode', 'linear')}**")

    with col3:
        st.info(f"Module-Anzahl: **{settings.get('module_quantity', 20)}**")

        storage_enabled = settings.get("include_storage", False)
        if storage_enabled:
            st.success("✅ Speicher: **EIN**")
        else:
            st.warning("⚠️ Speicher: **AUS**")

    # Vorschau
    st.markdown("### 📊 Preis-Vorschau (5 Firmen)")

    if price_increment > 0:
        calc_mode = settings.get("price_calculation_mode", "linear")

        preview_data = []
        for i in range(5):
            if calc_mode == "linear":
                factor = 1.0 + (i * price_increment / 100.0)
            elif calc_mode == "exponentiell":
                exponent = settings.get("price_exponent", 1.03)
                factor = exponent ** i
            else:
                factor = 1.0

            base_price = 20000  # Beispiel
            scaled_price = base_price * factor

            preview_data.append({
                "Firma": i + 1,
                "Faktor": f"{factor:.3f}",
                "Basispreis": f"{base_price:.2f} €",
                "Skalierter Preis": f"{scaled_price:.2f} €",
                "Differenz": f"+{(factor - 1) * 100:.1f}%"
            })

        import pandas as pd
        df = pd.DataFrame(preview_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning(
            "⚠️ Preisstaffelung deaktiviert (0%) - alle Firmen bekommen den gleichen Preis!")

else:
    st.error("❌ `multi_offer_settings` nicht in Session State gefunden!")
    st.info(
        "Gehe zuerst zur Multi-Angebote-Seite, um die Einstellungen zu initialisieren.")

st.markdown("---")

# Alle Session-State Keys anzeigen
with st.expander("🔑 Alle Session State Keys"):
    keys = list(st.session_state.keys())
    st.write(f"Anzahl Keys: {len(keys)}")
    st.write(keys)

# Reset-Button
if st.button("🔄 Session State zurücksetzen"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.success("Session State wurde zurückgesetzt!")
    st.rerun()
