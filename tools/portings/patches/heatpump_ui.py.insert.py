# === AUTO-GENERATED INSERT PATCH ===
# target_module: heatpump_ui.py
# insert_blocks follow; keep formatting unchanged

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

import streamlit as st


# --- DEF BLOCK START: func render_components_offer_tab ---
def render_components_offer_tab(texts: dict[str, str]):
    """Neue Tab-Seite: Strukturierte Anzeige Hauptkomponenten + Zubehör, Preislogik, Förderung & Finanzierung."""
    st.subheader(" Komponenten & Angebot")
    try:
        from heatpump_pricing import (
            apply_discounts_and_surcharges,
            build_full_heatpump_offer,
            calculate_annuity_loan,
            calculate_base_price,
            calculate_beg_subsidy,
            load_heatpump_components,
        )
    except Exception as e:
        st.warning(f"Preis-/Fördermodul nicht verfügbar: {e}")
        return

    # Komponenten laden
    comps = load_heatpump_components()
    main_comps = comps.get("main", [])
    accessory_comps = comps.get("accessories", [])

    if not (main_comps or accessory_comps):
        st.info(
            "Keine Wärmepumpen-Komponenten in der Produkt-DB gefunden. Bitte im Admin-Panel anlegen.")
        return

    # Hauptkomponenten Abschnitt
    st.markdown("### Hauptkomponenten")
    for c in main_comps:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col1:
            st.markdown(f"**{c.name}**")
            if c.description:
                st.caption(c.description[:180])
        with col2:
            st.write(f"Material: {c.material_net:,.0f} €")
        with col3:
            if c.labor_hours:
                st.write(f"Arbeitsstd.: {c.labor_hours:g}")
            else:
                st.write("-")
        with col4:
            st.write(f"Gesamt: {c.total_net:,.0f} €")

    # Zubehör / Dienstleistungen
    with st.expander("Zubehör und Leistungen", expanded=False):
        for c in accessory_comps:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.write(c.name)
            with col2:
                st.write(f"{c.material_net:,.0f} €")
            with col3:
                st.write(f"{c.labor_hours:g}h" if c.labor_hours else "-")
            with col4:
                st.write(f"{c.total_net:,.0f} €")

    base = calculate_base_price(comps)
    st.markdown("### Basispreis")
    colb1, colb2, colb3 = st.columns(3)
    colb1.metric("Material", f"{base['material_sum_net']:,.0f} €")
    colb2.metric("Arbeit", f"{base['labor_sum_net']:,.0f} €")
    colb3.metric("Summe Netto", f"{base['base_total_net']:,.0f} €")

    st.markdown("### Rabatte / Aufpreise")
    colr1, colr2, colr3, colr4 = st.columns(4)
    with colr1:
        rabatt_pct = st.number_input(
            "Rabatt %",
            min_value=0.0,
            max_value=50.0,
            value=0.0,
            step=1.0)
    with colr2:
        rabatt_abs = st.number_input(
            "Rabatt €",
            min_value=0.0,
            max_value=50000.0,
            value=0.0,
            step=500.0)
    with colr3:
        zuschlag_pct = st.number_input(
            "Zuschlag %",
            min_value=0.0,
            max_value=50.0,
            value=0.0,
            step=1.0)
    with colr4:
        zuschlag_abs = st.number_input(
            "Zuschlag €",
            min_value=0.0,
            max_value=50000.0,
            value=0.0,
            step=500.0)

    mods = apply_discounts_and_surcharges(
        base['base_total_net'],
        rabatt_pct,
        rabatt_abs,
        zuschlag_pct,
        zuschlag_abs)
    colm1, colm2, colm3 = st.columns(3)
    colm1.metric("Nach Rabatt/Zuschlag", f"{mods['final_price_net']:,.0f} €")
    colm2.metric("Rabatt gesamt",
                 f"-{mods['rabatt_pct_amount'] + mods['rabatt_abs']:,.0f} €")
    colm3.metric(
        "Zuschläge gesamt", f"{
            mods['zuschlag_pct_amount'] + mods['zuschlag_abs']:,.0f} €")

    st.markdown("### BEG-Förderung")
    colf1, colf2, colf3, colf4 = st.columns(4)
    with colf1:
        natural_ref = st.checkbox(
            "Natürliches Kältemittel",
            value=True,
            help="R290 Bonus +5%")
    with colf2:
        replace_old = st.checkbox(
            "Heizungstausch",
            value=False,
            help="+20% Bonus")
    with colf3:
        low_income = st.checkbox(
            "Einkommen <40 T€",
            value=False,
            help="+20% Bonus")
    with colf4:
        st.write("Max 70%")
    subsidy = calculate_beg_subsidy(
        mods['final_price_net'],
        natural_ref,
        replace_old,
        low_income)
    colsub1, colsub2, colsub3 = st.columns(3)
    colsub1.metric("Förder-%", f"{subsidy['applied_pct']:.0f}%")
    colsub2.metric("Förderbetrag", f"{subsidy['subsidy_amount_net']:,.0f} €")
    colsub3.metric(
        "Netto nach Förderung", f"{
            subsidy['effective_total_after_subsidy_net']:,.0f} €")

    st.markdown("### Finanzierung (Annuität)")
    colfin1, colfin2, colfin3, colfin4 = st.columns(4)
    with colfin1:
        years = st.number_input(
            "Laufzeit Jahre",
            min_value=1,
            max_value=30,
            value=15)
    with colfin2:
        interest = st.number_input(
            "Zins % p.a.",
            min_value=0.0,
            max_value=15.0,
            value=3.0,
            step=0.1)
    with colfin3:
        equity_pct = st.number_input(
            "Eigenkapital %",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=5.0)
    with colfin4:
        st.write("")
    equity_amount = subsidy['effective_total_after_subsidy_net'] * \
        (equity_pct / 100.0)
    principal = subsidy['effective_total_after_subsidy_net'] - equity_amount
    fin = calculate_annuity_loan(
        principal,
        interest,
        int(years)) if principal > 0 else {
        "monthly_rate": 0,
        "total_interest": 0}
    colfinm1, colfinm2, colfinm3 = st.columns(3)
    colfinm1.metric("Kreditsumme", f"{principal:,.0f} €")
    colfinm2.metric("Monatsrate", f"{fin['monthly_rate']:,.0f} €")
    colfinm3.metric("Gesamtzinsen", f"{fin['total_interest']:,.0f} €")

    # Komplettes Angebotsobjekt im Session-State bereitstellen für PDF /
    # Platzhalter
    try:
        from heatpump_pricing import (
            build_full_heatpump_offer,
        )
        offer = build_full_heatpump_offer(
            rabatt_pct=rabatt_pct,
            rabatt_abs=rabatt_abs,
            zuschlag_pct=zuschlag_pct,
            zuschlag_abs=zuschlag_abs,
            beg_flags={
                "natural_refrigerant": natural_ref,
                "replace_old": replace_old,
                "low_income": low_income},
            financing={
                "equity_amount": equity_amount,
                "interest_pct": interest,
                "years": years})
        st.session_state['heatpump_offer'] = offer
        st.success("Angebotsdaten aktualisiert und gespeichert.")
    except Exception as e:
        st.warning(f"Offer-Erstellung fehlgeschlagen: {e}")

    if st.checkbox("Details anzeigen (Debug)"):
        st.json(st.session_state.get('heatpump_offer'))
# --- DEF BLOCK END ---
