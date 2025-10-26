"""Admin Pricing Rule Management UI

Provides a comprehensive interface for managing discount and surcharge rules.
Supports rule priority, condition configuration, and testing functionality.
"""

import json
import traceback

import pandas as pd
import streamlit as st

try:
    from pricing.dynamic_key_manager import DynamicKeyManager
    from pricing.pricing_modification_engine import (
        AccessoryConfig,
        DiscountConfig,
        ModificationType,
        PricingModificationEngine,
        SurchargeConfig,
    )
    PRICING_AVAILABLE = True
except ImportError as e:
    st.error(f"Pricing modules not available: {e}")
    PRICING_AVAILABLE = False

    # Fallback classes for UI testing
    class DiscountConfig:
        def __init__(
                self,
                discount_type: str,
                discount_value: float,
                description: str = "",
                applies_to: str = "total",
                conditions: dict = None,
                priority: int = 0,
                minimum_amount: float = 0.0,
                maximum_discount: float | None = None,
                is_active: bool = True):
            self.discount_type = discount_type
            self.discount_value = discount_value
            self.description = description
            self.applies_to = applies_to
            self.conditions = conditions or {}
            self.priority = priority
            self.minimum_amount = minimum_amount
            self.maximum_discount = maximum_discount
            self.is_active = is_active
            self.dynamic_key = f"DISCOUNT_{
                description.upper().replace(
                    ' ', '_')}"

    class SurchargeConfig:
        def __init__(
                self,
                surcharge_type: str,
                surcharge_value: float,
                description: str = "",
                applies_to: str = "total",
                conditions: dict = None,
                priority: int = 0,
                minimum_amount: float = 0.0,
                maximum_surcharge: float | None = None,
                is_active: bool = True):
            self.surcharge_type = surcharge_type
            self.surcharge_value = surcharge_value
            self.description = description
            self.applies_to = applies_to
            self.conditions = conditions or {}
            self.priority = priority
            self.minimum_amount = minimum_amount
            self.maximum_surcharge = maximum_surcharge
            self.is_active = is_active
            self.dynamic_key = f"SURCHARGE_{
                description.upper().replace(
                    ' ', '_')}"

    class AccessoryConfig:
        def __init__(self, accessory_id: int, name: str, price: float,
                     quantity: int = 1, category: str = "accessory",
                     description: str = "", is_optional: bool = True):
            self.accessory_id = accessory_id
            self.name = name
            self.price = price
            self.quantity = quantity
            self.category = category
            self.description = description
            self.is_optional = is_optional
            self.dynamic_key = f"ACCESSORY_{name.upper().replace(' ', '_')}"

    class PricingModificationEngine:
        def __init__(self):
            self.discounts = []
            self.surcharges = []
            self.accessories = []

        def add_discount(self, config):
            self.discounts.append(config)

        def add_surcharge(self, config):
            self.surcharges.append(config)

        def add_accessory(self, config):
            self.accessories.append(config)

        def calculate_modifications(
                self,
                base_price: float,
                selected_accessories=None,
                context=None):
            return {
                'original_amount': base_price,
                'accessories_cost': 0.0,
                'total_discounts': 0.0,
                'total_surcharges': 0.0,
                'final_amount': base_price,
                'applied_modifications': [],
                'dynamic_keys': {}
            }

        def calculate_detailed_breakdown(
                self,
                base_price: float,
                selected_accessories=None,
                context=None):
            return {
                'step_1_base_price': base_price,
                'step_10_final_amount': base_price,
                'validation_checks': {'final_amount_valid': True}
            }


def render_pricing_rule_management_ui():
    """Main function to render the pricing rule management interface"""

    st.header("⚙️ Preisregel-Verwaltung")
    st.markdown("Verwalten Sie Rabatte, Zuschläge und Zubehör-Preisregeln.")

    if not PRICING_AVAILABLE:
        st.warning("⚠️ Pricing-Module nicht verfügbar. UI läuft im Test-Modus.")

    # Initialize pricing modification engine
    try:
        if 'pricing_engine' not in st.session_state:
            st.session_state.pricing_engine = PricingModificationEngine()
    except Exception as e:
        st.error(f"Fehler beim Initialisieren der Pricing Engine: {e}")
        return

    # Create tabs for different rule management areas
    tab1, tab2, tab3, tab4 = st.tabs([
        "💰 Rabatt-Regeln",
        "📈 Zuschlag-Regeln",
        "🔧 Zubehör-Regeln",
        "🧪 Regel-Test"
    ])

    with tab1:
        render_discount_rules_tab(st.session_state.pricing_engine)

    with tab2:
        render_surcharge_rules_tab(st.session_state.pricing_engine)

    with tab3:
        render_accessory_rules_tab(st.session_state.pricing_engine)

    with tab4:
        render_rule_testing_tab(st.session_state.pricing_engine)


def render_discount_rules_tab(pricing_engine: PricingModificationEngine):
    """Render the discount rules configuration tab"""

    st.subheader("💰 Rabatt-Regeln")
    st.markdown(
        "Konfigurieren Sie Rabattregeln mit Bedingungen und Prioritäten.")

    # Display current discount rules
    if hasattr(pricing_engine, 'discounts') and pricing_engine.discounts:
        st.markdown("**Aktuelle Rabatt-Regeln:**")

        for i, discount in enumerate(pricing_engine.discounts):
            with st.expander(f"💰 {discount.description or f'Rabatt {i + 1}'}", expanded=False):
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])

                col1.metric(
                    "Typ",
                    "Prozentual" if discount.discount_type == "percentage" else "Fester Betrag")
                col2.metric(
                    "Wert", f"{
                        discount.discount_value:.2f}{
                        '%' if discount.discount_type == 'percentage' else '€'}")
                col3.metric("Priorität", discount.priority)
                col4.metric("Aktiv", "✅" if discount.is_active else "❌")

                # Show conditions if any
                if discount.conditions:
                    st.markdown("**Bedingungen:**")
                    for key, value in discount.conditions.items():
                        st.text(f"• {key}: {value}")

                # Show limits
                if discount.minimum_amount > 0:
                    st.info(f"Mindestbetrag: {discount.minimum_amount:.2f}€")

                if discount.maximum_discount:
                    st.info(f"Max. Rabatt: {discount.maximum_discount:.2f}€")

                if col5.button(
                    "🗑️",
                    key=f"delete_discount_{i}",
                        help="Rabatt löschen"):
                    pricing_engine.discounts.pop(i)
                    st.rerun()
    else:
        st.info("ℹ️ Keine Rabatt-Regeln konfiguriert.")

    st.markdown("---")

    # Add new discount rule
    st.markdown("**Neue Rabatt-Regel hinzufügen:**")

    with st.form("add_discount_rule"):
        col1, col2 = st.columns(2)

        with col1:
            discount_description = st.text_input(
                "Beschreibung",
                placeholder="z.B. Frühbucher-Rabatt",
                help="Beschreibung der Rabatt-Regel"
            )

            discount_type = st.selectbox(
                "Rabatt-Typ",
                options=["percentage", "fixed"],
                format_func=lambda x: "Prozentual (%)" if x == "percentage" else "Fester Betrag (€)"
            )

            discount_value = st.number_input(
                "Rabatt-Wert",
                min_value=0.0,
                value=5.0 if discount_type == "percentage" else 100.0,
                step=0.1,
                help="Prozentsatz oder fester Betrag"
            )

            applies_to = st.selectbox(
                "Anwendung auf",
                options=["total", "category", "product"],
                format_func=lambda x: {
                    "total": "Gesamtbetrag",
                    "category": "Kategorie",
                    "product": "Einzelprodukt"
                }[x]
            )

        with col2:
            priority = st.number_input(
                "Priorität",
                min_value=0,
                max_value=100,
                value=50,
                help="Höhere Zahlen = höhere Priorität"
            )

            minimum_amount = st.number_input(
                "Mindestbetrag (€)",
                min_value=0.0,
                value=0.0,
                step=0.01,
                help="Mindestbestellwert für Rabatt"
            )

            maximum_discount = st.number_input(
                "Max. Rabatt (€)",
                min_value=0.0,
                value=0.0,
                step=0.01,
                help="Maximaler Rabattbetrag (0 = unbegrenzt)"
            )

            is_active = st.checkbox(
                "Aktiv",
                value=True,
                help="Regel ist aktiv und wird angewendet"
            )

        # Conditions section
        st.markdown("**Bedingungen (optional):**")
        conditions_json = st.text_area(
            "Bedingungen (JSON)",
            placeholder='{"customer_type": "premium", "order_date": "2024"}',
            help="JSON-Format für erweiterte Bedingungen"
        )

        submitted = st.form_submit_button("➕ Rabatt-Regel hinzufügen")

        if submitted:
            try:
                # Parse conditions
                conditions = {}
                if conditions_json.strip():
                    conditions = json.loads(conditions_json)

                # Create discount config
                config = DiscountConfig(
                    discount_type=discount_type,
                    discount_value=discount_value,
                    description=discount_description,
                    applies_to=applies_to,
                    conditions=conditions,
                    priority=priority,
                    minimum_amount=minimum_amount,
                    maximum_discount=maximum_discount if maximum_discount > 0 else None,
                    is_active=is_active)

                pricing_engine.add_discount(config)
                st.success(
                    f"✅ Rabatt-Regel '{discount_description}' erfolgreich hinzugefügt!")
                st.rerun()

            except json.JSONDecodeError:
                st.error("❌ Ungültiges JSON-Format in den Bedingungen")
            except Exception as e:
                st.error(f"❌ Fehler: {e}")


def render_surcharge_rules_tab(pricing_engine: PricingModificationEngine):
    """Render the surcharge rules configuration tab"""

    st.subheader("📈 Zuschlag-Regeln")
    st.markdown(
        "Konfigurieren Sie Zuschlagsregeln mit Bedingungen und Prioritäten.")

    # Display current surcharge rules
    if hasattr(pricing_engine, 'surcharges') and pricing_engine.surcharges:
        st.markdown("**Aktuelle Zuschlag-Regeln:**")

        for i, surcharge in enumerate(pricing_engine.surcharges):
            with st.expander(f"📈 {surcharge.description or f'Zuschlag {i + 1}'}", expanded=False):
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])

                col1.metric(
                    "Typ",
                    "Prozentual" if surcharge.surcharge_type == "percentage" else "Fester Betrag")
                col2.metric(
                    "Wert", f"{
                        surcharge.surcharge_value:.2f}{
                        '%' if surcharge.surcharge_type == 'percentage' else '€'}")
                col3.metric("Priorität", surcharge.priority)
                col4.metric("Aktiv", "✅" if surcharge.is_active else "❌")

                # Show conditions if any
                if surcharge.conditions:
                    st.markdown("**Bedingungen:**")
                    for key, value in surcharge.conditions.items():
                        st.text(f"• {key}: {value}")

                # Show limits
                if surcharge.minimum_amount > 0:
                    st.info(f"Mindestbetrag: {surcharge.minimum_amount:.2f}€")

                if surcharge.maximum_surcharge:
                    st.info(
                        f"Max. Zuschlag: {
                            surcharge.maximum_surcharge:.2f}€")

                if col5.button(
                    "🗑️",
                    key=f"delete_surcharge_{i}",
                        help="Zuschlag löschen"):
                    pricing_engine.surcharges.pop(i)
                    st.rerun()
    else:
        st.info("ℹ️ Keine Zuschlag-Regeln konfiguriert.")

    st.markdown("---")

    # Add new surcharge rule
    st.markdown("**Neue Zuschlag-Regel hinzufügen:**")

    with st.form("add_surcharge_rule"):
        col1, col2 = st.columns(2)

        with col1:
            surcharge_description = st.text_input(
                "Beschreibung",
                placeholder="z.B. Express-Zuschlag",
                help="Beschreibung der Zuschlag-Regel"
            )

            surcharge_type = st.selectbox(
                "Zuschlag-Typ",
                options=["percentage", "fixed"],
                format_func=lambda x: "Prozentual (%)" if x == "percentage" else "Fester Betrag (€)"
            )

            surcharge_value = st.number_input(
                "Zuschlag-Wert",
                min_value=0.0,
                value=5.0 if surcharge_type == "percentage" else 100.0,
                step=0.1,
                help="Prozentsatz oder fester Betrag"
            )

            applies_to = st.selectbox(
                "Anwendung auf",
                options=["total", "category", "product"],
                format_func=lambda x: {
                    "total": "Gesamtbetrag",
                    "category": "Kategorie",
                    "product": "Einzelprodukt"
                }[x],
                key="surcharge_applies_to"
            )

        with col2:
            priority = st.number_input(
                "Priorität",
                min_value=0,
                max_value=100,
                value=50,
                help="Höhere Zahlen = höhere Priorität",
                key="surcharge_priority"
            )

            minimum_amount = st.number_input(
                "Mindestbetrag (€)",
                min_value=0.0,
                value=0.0,
                step=0.01,
                help="Mindestbestellwert für Zuschlag",
                key="surcharge_minimum"
            )

            maximum_surcharge = st.number_input(
                "Max. Zuschlag (€)",
                min_value=0.0,
                value=0.0,
                step=0.01,
                help="Maximaler Zuschlagsbetrag (0 = unbegrenzt)",
                key="surcharge_maximum"
            )

            is_active = st.checkbox(
                "Aktiv",
                value=True,
                help="Regel ist aktiv und wird angewendet",
                key="surcharge_active"
            )

        # Conditions section
        st.markdown("**Bedingungen (optional):**")
        conditions_json = st.text_area(
            "Bedingungen (JSON)",
            placeholder='{"delivery_type": "express", "region": "remote"}',
            help="JSON-Format für erweiterte Bedingungen",
            key="surcharge_conditions"
        )

        submitted = st.form_submit_button("➕ Zuschlag-Regel hinzufügen")

        if submitted:
            try:
                # Parse conditions
                conditions = {}
                if conditions_json.strip():
                    conditions = json.loads(conditions_json)

                # Create surcharge config
                config = SurchargeConfig(
                    surcharge_type=surcharge_type,
                    surcharge_value=surcharge_value,
                    description=surcharge_description,
                    applies_to=applies_to,
                    conditions=conditions,
                    priority=priority,
                    minimum_amount=minimum_amount,
                    maximum_surcharge=maximum_surcharge if maximum_surcharge > 0 else None,
                    is_active=is_active)

                pricing_engine.add_surcharge(config)
                st.success(
                    f"✅ Zuschlag-Regel '{surcharge_description}' erfolgreich hinzugefügt!")
                st.rerun()

            except json.JSONDecodeError:
                st.error("❌ Ungültiges JSON-Format in den Bedingungen")
            except Exception as e:
                st.error(f"❌ Fehler: {e}")


def render_accessory_rules_tab(pricing_engine: PricingModificationEngine):
    """Render the accessory rules configuration tab"""

    st.subheader("🔧 Zubehör-Regeln")
    st.markdown("Verwalten Sie Zubehör-Artikel und deren Preise.")

    # Display current accessories
    if hasattr(pricing_engine, 'accessories') and pricing_engine.accessories:
        st.markdown("**Verfügbare Zubehör-Artikel:**")

        for i, accessory in enumerate(pricing_engine.accessories):
            with st.expander(f"🔧 {accessory.name}", expanded=False):
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])

                col1.metric("Preis", f"{accessory.price:.2f}€")
                col2.metric("Menge", accessory.quantity)
                col3.metric("Kategorie", accessory.category)
                col4.metric("Optional", "✅" if accessory.is_optional else "❌")

                if accessory.description:
                    st.markdown(f"**Beschreibung:** {accessory.description}")

                if col5.button(
                    "🗑️",
                    key=f"delete_accessory_{i}",
                        help="Zubehör löschen"):
                    pricing_engine.accessories.pop(i)
                    st.rerun()
    else:
        st.info("ℹ️ Keine Zubehör-Artikel konfiguriert.")

    st.markdown("---")

    # Add new accessory
    st.markdown("**Neuen Zubehör-Artikel hinzufügen:**")

    with st.form("add_accessory"):
        col1, col2 = st.columns(2)

        with col1:
            accessory_name = st.text_input(
                "Name",
                placeholder="z.B. Monitoring-System",
                help="Name des Zubehör-Artikels"
            )

            accessory_price = st.number_input(
                "Preis (€)",
                min_value=0.0,
                value=100.0,
                step=0.01,
                help="Preis pro Einheit"
            )

            accessory_quantity = st.number_input(
                "Standard-Menge",
                min_value=1,
                value=1,
                help="Standard-Anzahl bei Auswahl"
            )

        with col2:
            accessory_category = st.selectbox(
                "Kategorie",
                options=[
                    "accessory",
                    "monitoring",
                    "installation",
                    "service",
                    "warranty"],
                format_func=lambda x: {
                    "accessory": "Zubehör",
                    "monitoring": "Überwachung",
                    "installation": "Installation",
                    "service": "Service",
                    "warranty": "Garantie"}.get(
                    x,
                    x))

            is_optional = st.checkbox(
                "Optional",
                value=True,
                help="Artikel ist optional wählbar"
            )

            accessory_description = st.text_area(
                "Beschreibung",
                placeholder="Detaillierte Beschreibung des Zubehörs...",
                help="Optionale Beschreibung"
            )

        submitted = st.form_submit_button("➕ Zubehör hinzufügen")

        if submitted:
            try:
                # Generate unique ID
                accessory_id = len(pricing_engine.accessories) + 1

                # Create accessory config
                config = AccessoryConfig(
                    accessory_id=accessory_id,
                    name=accessory_name,
                    price=accessory_price,
                    quantity=accessory_quantity,
                    category=accessory_category,
                    description=accessory_description,
                    is_optional=is_optional
                )

                pricing_engine.add_accessory(config)
                st.success(
                    f"✅ Zubehör '{accessory_name}' erfolgreich hinzugefügt!")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Fehler: {e}")


def render_rule_testing_tab(pricing_engine: PricingModificationEngine):
    """Render the rule testing and preview tab"""

    st.subheader("🧪 Regel-Test")
    st.markdown("Testen Sie Ihre Preisregeln mit verschiedenen Szenarien.")

    # Test parameters
    st.markdown("**Test-Parameter:**")

    col1, col2 = st.columns(2)

    with col1:
        base_price = st.number_input(
            "Basis-Preis (€)",
            min_value=0.0,
            value=1000.0,
            step=0.01,
            key="test_base_price"
        )

        # Accessory selection
        if hasattr(
                pricing_engine,
                'accessories') and pricing_engine.accessories:
            st.markdown("**Zubehör auswählen:**")
            selected_accessories = []

            for accessory in pricing_engine.accessories:
                if st.checkbox(
                    f"{accessory.name} ({accessory.price:.2f}€)",
                    key=f"test_acc_{accessory.accessory_id}"
                ):
                    selected_accessories.append(accessory.accessory_id)
        else:
            selected_accessories = []

    with col2:
        # Context parameters
        st.markdown("**Kontext-Parameter:**")
        context_json = st.text_area(
            "Kontext (JSON)",
            placeholder='{"customer_type": "premium", "delivery_type": "express"}',
            help="JSON-Format für Regel-Bedingungen",
            key="test_context")

    # Test button
    if st.button("🧪 Preisberechnung testen", key="test_pricing"):
        try:
            # Parse context
            context = {}
            if context_json.strip():
                context = json.loads(context_json)

            # Calculate modifications
            result = pricing_engine.calculate_modifications(
                base_price=base_price,
                selected_accessories=selected_accessories,
                context=context
            )

            # Display results
            st.markdown("**📊 Test-Ergebnisse:**")

            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Basis-Preis", f"{result['original_amount']:.2f}€")
            col2.metric("Zubehör", f"{result['accessories_cost']:.2f}€")
            col3.metric("Rabatte", f"-{result['total_discounts']:.2f}€")
            col4.metric("Zuschläge", f"+{result['total_surcharges']:.2f}€")

            # Final amount
            st.metric("**Endpreis**", f"{result['final_amount']:.2f}€")

            # Detailed breakdown
            if PRICING_AVAILABLE:
                try:
                    breakdown = pricing_engine.calculate_detailed_breakdown(
                        base_price=base_price,
                        selected_accessories=selected_accessories,
                        context=context
                    )

                    st.markdown("**🔍 Detaillierte Aufschlüsselung:**")

                    with st.expander("Berechnungsschritte anzeigen", expanded=False):
                        steps = [
                            ("1. Basis-Preis", breakdown.get('step_1_base_price', 0)),
                            ("2. Zubehör", breakdown.get('step_2_accessories', {}).get('total_cost', 0)),
                            ("3. Basis + Zubehör", breakdown.get('step_3_base_with_accessories', 0)),
                            ("4. Nach %-Rabatten", breakdown.get('step_5_after_pct_discounts', 0)),
                            ("5. Nach %-Zuschlägen", breakdown.get('step_7_after_pct_surcharges', 0)),
                            ("6. Endpreis", breakdown.get('step_10_final_amount', 0))
                        ]

                        for step_name, step_value in steps:
                            st.text(f"{step_name}: {step_value:.2f}€")

                        # Validation
                        validation = breakdown.get('validation_checks', {})
                        if validation.get('prevented_negative'):
                            st.warning(
                                "⚠️ Negativer Preis wurde auf 0€ korrigiert")

                        if validation.get('final_amount_valid'):
                            st.success(
                                "✅ Preisberechnung erfolgreich validiert")

                except Exception as e:
                    st.warning(
                        f"Detaillierte Aufschlüsselung nicht verfügbar: {e}")

            # Applied modifications
            if 'applied_modifications' in result and result['applied_modifications']:
                st.markdown("**📋 Angewendete Regeln:**")

                modifications_data = []
                for mod in result['applied_modifications']:
                    config = mod.config if hasattr(mod, 'config') else mod
                    modifications_data.append(
                        {
                            "Typ": mod.modification_type.value if hasattr(
                                mod, 'modification_type') else "Unbekannt", "Beschreibung": getattr(
                                config, 'description', getattr(
                                    config, 'name', 'Unbekannt')), "Betrag": f"{
                                mod.applied_amount if hasattr(
                                    mod, 'applied_amount') else 0:.2f}€"})

                if modifications_data:
                    df_modifications = pd.DataFrame(modifications_data)
                    st.dataframe(df_modifications, use_container_width=True)
            else:
                st.info("ℹ️ Keine Regeln angewendet")

            # Dynamic keys
            if 'dynamic_keys' in result and result['dynamic_keys']:
                with st.expander("🔑 Generierte PDF-Schlüssel", expanded=False):
                    for key, value in result['dynamic_keys'].items():
                        st.text(f"{key}: {value}")

        except json.JSONDecodeError:
            st.error("❌ Ungültiges JSON-Format im Kontext")
        except Exception as e:
            st.error(f"❌ Fehler beim Testen: {e}")
            st.error(f"Details: {traceback.format_exc()}")

    # Rule priority preview
    st.markdown("---")
    st.markdown("**📊 Regel-Prioritäten:**")

    # Show discount priorities
    if hasattr(pricing_engine, 'discounts') and pricing_engine.discounts:
        st.markdown("*Rabatt-Regeln (nach Priorität):*")
        discount_data = []
        for discount in sorted(
                pricing_engine.discounts,
                key=lambda x: x.priority,
                reverse=True):
            discount_data.append(
                {
                    "Priorität": discount.priority,
                    "Beschreibung": discount.description,
                    "Typ": "Prozentual" if discount.discount_type == "percentage" else "Fest",
                    "Wert": f"{
                        discount.discount_value:.2f}{
                        '%' if discount.discount_type == 'percentage' else '€'}",
                    "Aktiv": "✅" if discount.is_active else "❌"})

        if discount_data:
            df_discounts = pd.DataFrame(discount_data)
            st.dataframe(df_discounts, use_container_width=True)

    # Show surcharge priorities
    if hasattr(pricing_engine, 'surcharges') and pricing_engine.surcharges:
        st.markdown("*Zuschlag-Regeln (nach Priorität):*")
        surcharge_data = []
        for surcharge in sorted(
                pricing_engine.surcharges,
                key=lambda x: x.priority,
                reverse=True):
            surcharge_data.append(
                {
                    "Priorität": surcharge.priority,
                    "Beschreibung": surcharge.description,
                    "Typ": "Prozentual" if surcharge.surcharge_type == "percentage" else "Fest",
                    "Wert": f"{
                        surcharge.surcharge_value:.2f}{
                        '%' if surcharge.surcharge_type == 'percentage' else '€'}",
                    "Aktiv": "✅" if surcharge.is_active else "❌"})

        if surcharge_data:
            df_surcharges = pd.DataFrame(surcharge_data)
            st.dataframe(df_surcharges, use_container_width=True)


# Main entry point
if __name__ == "__main__":
    render_pricing_rule_management_ui()
