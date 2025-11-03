"""Admin Profit Margin Management UI

Provides a comprehensive interface for managing profit margins at product, category, and global levels.
Supports different calculation methods (calculate_per) and includes margin preview and validation.
"""

import traceback
from typing import Any

import pandas as pd
import streamlit as st

from ui_state_manager import request_rerun

try:
    from pricing.profit_margin_manager import (
        MarginBreakdown,
        MarginConfig,
        ProfitMarginManager,
    )
    from product_db import get_product_by_id, list_product_categories, list_products
    PRICING_AVAILABLE = True
except ImportError as e:
    st.error(f"Pricing modules not available: {e}")
    PRICING_AVAILABLE = False

    # Fallback classes for UI testing
    class MarginConfig:
        def __getstate__(self):
            """Ermöglicht Pickle-Serialisierung für Session State"""
            return self.__dict__.copy()
        
        def __setstate__(self, state):
            """Ermöglicht Pickle-Deserialisierung für Session State"""
            self.__dict__.update(state)
        
        def __init__(
                self,
                margin_type: str,
                margin_value: float,
                applies_to: str,
                priority: int = 0):
            self.margin_type = margin_type
            self.margin_value = margin_value
            self.applies_to = applies_to
            self.priority = priority

    class MarginBreakdown:
        def __getstate__(self):
            """Ermöglicht Pickle-Serialisierung für Session State"""
            return self.__dict__.copy()
        
        def __setstate__(self, state):
            """Ermöglicht Pickle-Deserialisierung für Session State"""
            self.__dict__.update(state)
        
        def __init__(
                self,
                purchase_price: float,
                margin_amount: float,
                selling_price: float,
                margin_percentage: float,
                source: str,
                calculate_per_method: str | None = None,
                quantity: float = 1.0):
            self.purchase_price = purchase_price
            self.margin_amount = margin_amount
            self.selling_price = selling_price
            self.margin_percentage = margin_percentage
            self.source = source
            self.calculate_per_method = calculate_per_method
            self.quantity = quantity

    class ProfitMarginManager:
        def __getstate__(self):
            """Ermöglicht Pickle-Serialisierung für Session State"""
            return self.__dict__.copy()
        
        def __setstate__(self, state):
            """Ermöglicht Pickle-Deserialisierung für Session State"""
            self.__dict__.update(state)
        
        def __init__(self):
            pass

        def get_all_margins(self):
            return {'global_margins': {}, 'category_margins': {}}

        def set_global_margin(self, config, category=None):
            return True

        def set_product_margin(self, product_id, config):
            return True

        def get_margin_breakdown(
                self,
                purchase_price: float,
                product_id: int | None = None,
                category: str | None = None,
                calculate_per: str | None = None,
                quantity: float = 1.0) -> MarginBreakdown:
            return MarginBreakdown(
                purchase_price,
                0.0,
                purchase_price,
                0.0,
                'none',
                calculate_per,
                quantity)

        def calculate_total_price_with_margin(self,
                                              purchase_price: float,
                                              quantity: float,
                                              calculate_per: str,
                                              product_id: int | None = None,
                                              category: str | None = None) -> dict[str,
                                                                                   float]:
            return {
                'unit_purchase_price': purchase_price,
                'unit_selling_price': purchase_price,
                'unit_margin_amount': 0.0,
                'quantity': quantity,
                'calculate_per': calculate_per,
                'total_purchase_price': purchase_price * quantity,
                'total_selling_price': purchase_price * quantity,
                'total_margin_amount': 0.0,
                'margin_percentage': 0.0,
                'margin_source': 'none'
            }

        def get_available_categories(self) -> list[str]:
            return ["Modul", "Wechselrichter", "Batteriespeicher", "Zubehör"]

        def set_category_margin(
                self,
                category: str,
                margin_config: MarginConfig) -> bool:
            return True

        def remove_category_margin(self, category: str) -> bool:
            return True

        def apply_margin_to_category_products(
                self, category: str, margin_config: MarginConfig) -> dict[str, Any]:
            return {
                'success': True,
                'updated_count': 0,
                'failed_count': 0,
                'products': []}


def render_profit_margin_management_ui():
    """Main function to render the profit margin management interface"""

    st.header("🎯 Gewinnspannen-Verwaltung")
    st.markdown(
        "Verwalten Sie Gewinnspannen auf Produkt-, Kategorie- und globaler Ebene.")

    if not PRICING_AVAILABLE:
        st.warning("⚠️ Pricing-Module nicht verfügbar. UI läuft im Test-Modus.")

    # Initialize margin manager
    try:
        margin_manager = ProfitMarginManager()
    except Exception as e:
        st.error(f"Fehler beim Initialisieren des Margin Managers: {e}")
        return

    # Create tabs for different margin management areas
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌍 Globale Spannen",
        "📂 Kategorie-Spannen",
        "📦 Produkt-Spannen",
        "🧮 Kalkulations-Vorschau"
    ])

    with tab1:
        render_global_margins_tab(margin_manager)

    with tab2:
        render_category_margins_tab(margin_manager)

    with tab3:
        render_product_margins_tab(margin_manager)

    with tab4:
        render_margin_preview_tab(margin_manager)


def render_global_margins_tab(margin_manager: ProfitMarginManager):
    """Render the global margins configuration tab"""

    st.subheader("🌍 Globale Gewinnspannen")
    st.markdown(
        "Konfigurieren Sie Standard-Gewinnspannen, die als Fallback verwendet werden.")

    # Get current global margins
    try:
        all_margins = margin_manager.get_all_margins()
        global_margins = all_margins.get('global_margins', {})
    except Exception as e:
        st.error(f"Fehler beim Laden der globalen Spannen: {e}")
        global_margins = {}

    # Display current global margins
    if global_margins:
        st.markdown("**Aktuelle globale Spannen:**")

        for key, margin_data in global_margins.items():
            with st.expander(f"📊 {key.title()} Spanne", expanded=False):
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

                col1.metric("Typ", margin_data.get('margin_type', 'N/A'))
                col2.metric(
                    "Wert", f"{
                        margin_data.get(
                            'margin_value', 0):.2f}{
                        '%' if margin_data.get('margin_type') == 'percentage' else '€'}")
                col3.metric("Priorität", margin_data.get('priority', 0))

                if col4.button(
                    "🗑️",
                    key=f"delete_global_{key}",
                        help="Globale Spanne löschen"):
                    # Note: Implementation would need a delete method in
                    # ProfitMarginManager
                    st.warning(f"Löschen von '{key}' noch nicht implementiert")
    else:
        st.info("ℹ️ Keine globalen Spannen konfiguriert.")

    st.markdown("---")

    # Add new global margin
    st.markdown("**Neue globale Spanne hinzufügen:**")

    with st.form("add_global_margin"):
        col1, col2 = st.columns(2)

        with col1:
            margin_key = st.selectbox(
                "Berechnungsart",
                options=["default", "pauschal", "stück", "meter", "kwp"],
                help="Wählen Sie die Berechnungsart für diese Spanne"
            )

            margin_type = st.selectbox(
                "Spannen-Typ",
                options=["percentage", "fixed"],
                format_func=lambda x: "Prozentual (%)" if x == "percentage" else "Fester Betrag (€)"
            )

        with col2:
            margin_value = st.number_input(
                "Spannen-Wert",
                min_value=0.0,
                value=25.0 if margin_type == "percentage" else 50.0,
                step=0.1,
                help="Prozentsatz (z.B. 25 für 25%) oder fester Betrag in Euro"
            )

            priority = st.number_input(
                "Priorität",
                min_value=0,
                max_value=100,
                value=0,
                help="Höhere Zahlen = höhere Priorität"
            )

        submitted = st.form_submit_button("➕ Globale Spanne hinzufügen")

        if submitted:
            try:
                config = MarginConfig(
                    margin_type=margin_type,
                    margin_value=margin_value,
                    applies_to='global',
                    priority=priority,
                    calculate_per_method=margin_key if margin_key != "default" else None)

                success = margin_manager.set_global_margin(config)

                if success:
                    st.success(
                        f"✅ Globale Spanne '{margin_key}' erfolgreich hinzugefügt!")
                    request_rerun()
                else:
                    st.error("❌ Fehler beim Hinzufügen der globalen Spanne")

            except Exception as e:
                st.error(f"❌ Fehler: {e}")


def render_category_margins_tab(margin_manager: ProfitMarginManager):
    """Render the category margins configuration tab"""

    st.subheader("📂 Kategorie-Gewinnspannen")
    st.markdown(
        "Konfigurieren Sie spezifische Gewinnspannen für Produktkategorien.")

    # Get available categories
    try:
        categories = margin_manager.get_available_categories()
    except Exception as e:
        st.error(f"Fehler beim Laden der Kategorien: {e}")
        categories = []

    if not categories:
        st.warning("⚠️ Keine Produktkategorien gefunden.")
        return

    # Get current category margins
    try:
        all_margins = margin_manager.get_all_margins()
        category_margins = all_margins.get('category_margins', {})
    except Exception as e:
        st.error(f"Fehler beim Laden der Kategorie-Spannen: {e}")
        category_margins = {}

    # Display current category margins
    if category_margins:
        st.markdown("**Aktuelle Kategorie-Spannen:**")

        for category, margin_data in category_margins.items():
            with st.expander(f"📂 {category}", expanded=False):
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])

                col1.metric("Typ", margin_data.get('margin_type', 'N/A'))
                col2.metric(
                    "Wert", f"{
                        margin_data.get(
                            'margin_value', 0):.2f}{
                        '%' if margin_data.get('margin_type') == 'percentage' else '€'}")
                col3.metric("Priorität", margin_data.get('priority', 0))

                # Apply to all products in category button
                if col4.button(
                    "📦 Auf alle Produkte anwenden",
                        key=f"apply_cat_{category}"):
                    try:
                        config = MarginConfig(
                            margin_type=margin_data.get('margin_type'),
                            margin_value=margin_data.get('margin_value'),
                            applies_to='product',
                            priority=margin_data.get('priority', 50)
                        )

                        result = margin_manager.apply_margin_to_category_products(
                            category, config)

                        if result.get('success'):
                            st.success(
                                f"✅ Spanne auf {
                                    result.get(
                                        'updated_count',
                                        0)} Produkte angewendet")
                        else:
                            st.error(
                                f"❌ {
                                    result.get(
                                        'message',
                                        'Unbekannter Fehler')}")

                    except Exception as e:
                        st.error(f"❌ Fehler: {e}")

                if col5.button(
                    "🗑️",
                    key=f"delete_cat_{category}",
                        help="Kategorie-Spanne löschen"):
                    try:
                        success = margin_manager.remove_category_margin(
                            category)
                        if success:
                            st.success(
                                f"✅ Kategorie-Spanne für '{category}' gelöscht")
                            request_rerun()
                        else:
                            st.error("❌ Fehler beim Löschen")
                    except Exception as e:
                        st.error(f"❌ Fehler: {e}")

    st.markdown("---")

    # Add new category margin
    st.markdown("**Neue Kategorie-Spanne hinzufügen:**")

    with st.form("add_category_margin"):
        col1, col2 = st.columns(2)

        with col1:
            selected_category = st.selectbox(
                "Kategorie",
                options=categories,
                help="Wählen Sie die Produktkategorie"
            )

            margin_type = st.selectbox(
                "Spannen-Typ",
                options=[
                    "percentage",
                    "fixed"],
                format_func=lambda x: "Prozentual (%)" if x == "percentage" else "Fester Betrag (€)",
                key="cat_margin_type")

        with col2:
            margin_value = st.number_input(
                "Spannen-Wert",
                min_value=0.0,
                value=30.0 if margin_type == "percentage" else 75.0,
                step=0.1,
                help="Prozentsatz oder fester Betrag in Euro",
                key="cat_margin_value"
            )

            priority = st.number_input(
                "Priorität",
                min_value=0,
                max_value=100,
                value=50,
                help="Höhere Zahlen = höhere Priorität",
                key="cat_priority"
            )

        submitted = st.form_submit_button("➕ Kategorie-Spanne hinzufügen")

        if submitted:
            try:
                config = MarginConfig(
                    margin_type=margin_type,
                    margin_value=margin_value,
                    applies_to='category',
                    priority=priority
                )

                success = margin_manager.set_category_margin(
                    selected_category, config)

                if success:
                    st.success(
                        f"✅ Kategorie-Spanne für '{selected_category}' erfolgreich hinzugefügt!")
                    request_rerun()
                else:
                    st.error("❌ Fehler beim Hinzufügen der Kategorie-Spanne")

            except Exception as e:
                st.error(f"❌ Fehler: {e}")


def render_product_margins_tab(margin_manager: ProfitMarginManager):
    """Render the product-specific margins configuration tab"""

    st.subheader("📦 Produkt-spezifische Gewinnspannen")
    st.markdown(
        "Konfigurieren Sie individuelle Gewinnspannen für einzelne Produkte.")

    # Product selection
    try:
        if PRICING_AVAILABLE:
            products = list_products()
        else:
            products = []
    except Exception as e:
        st.error(f"Fehler beim Laden der Produkte: {e}")
        products = []

    if not products:
        st.warning("⚠️ Keine Produkte gefunden.")
        return

    # Filter products by category
    categories = ["Alle"] + \
        list(set(p.get('category', 'Unbekannt') for p in products))
    selected_category_filter = st.selectbox(
        "Kategorie filtern",
        options=categories,
        key="product_category_filter"
    )

    if selected_category_filter != "Alle":
        filtered_products = [p for p in products if p.get(
            'category') == selected_category_filter]
    else:
        filtered_products = products

    # Create product selection
    product_options = {f"{p.get('model_name',
                                'Unbekannt')} ({p.get('brand',
                                                      'Unbekannt')})": p for p in filtered_products}

    if not product_options:
        st.info("ℹ️ Keine Produkte in der ausgewählten Kategorie gefunden.")
        return

    selected_product_key = st.selectbox(
        "Produkt auswählen",
        options=list(product_options.keys()),
        key="selected_product"
    )

    if selected_product_key:
        selected_product = product_options[selected_product_key]
        product_id = selected_product.get('id')

        # Display current product information
        with st.expander("📋 Produkt-Informationen", expanded=True):
            col1, col2, col3, col4 = st.columns(4)

            col1.metric("ID", product_id)
            col2.metric("Marke", selected_product.get('brand', 'N/A'))
            col3.metric("Kategorie", selected_product.get('category', 'N/A'))
            col4.metric(
                "Berechnungsart",
                selected_product.get(
                    'calculate_per',
                    'Stück'))

            # Show current pricing information
            purchase_price = selected_product.get('price_euro', 0.0)
            current_margin_type = selected_product.get('margin_type')
            current_margin_value = selected_product.get('margin_value')

            if purchase_price > 0:
                st.markdown("**Aktuelle Preis-Informationen:**")
                price_col1, price_col2, price_col3 = st.columns(3)

                price_col1.metric("Einkaufspreis", f"{purchase_price:.2f} €")

                if current_margin_type and current_margin_value is not None:
                    price_col2.metric(
                        "Aktuelle Spanne", f"{
                            current_margin_value:.2f}{
                            '%' if current_margin_type == 'percentage' else '€'}")

                    # Calculate current selling price
                    try:
                        breakdown = margin_manager.get_margin_breakdown(
                            purchase_price=purchase_price,
                            product_id=product_id
                        )
                        price_col3.metric(
                            "Verkaufspreis", f"{
                                breakdown.selling_price:.2f} €")
                    except Exception as e:
                        price_col3.error(f"Fehler: {e}")
                else:
                    price_col2.info("Keine Spanne konfiguriert")
                    price_col3.metric(
                        "Verkaufspreis", f"{
                            purchase_price:.2f} €")

        # Margin configuration form
        st.markdown("**Gewinnspanne konfigurieren:**")

        with st.form(f"product_margin_{product_id}"):
            col1, col2 = st.columns(2)

            with col1:
                margin_type = st.selectbox(
                    "Spannen-Typ",
                    options=[
                        "percentage",
                        "fixed"],
                    format_func=lambda x: "Prozentual (%)" if x == "percentage" else "Fester Betrag (€)",
                    index=0 if current_margin_type == "percentage" else 1 if current_margin_type == "fixed" else 0,
                    key=f"prod_margin_type_{product_id}")

                priority = st.number_input(
                    "Priorität",
                    min_value=0,
                    max_value=100,
                    value=selected_product.get('margin_priority', 100),
                    help="Höhere Zahlen = höhere Priorität",
                    key=f"prod_priority_{product_id}"
                )

            with col2:
                default_value = current_margin_value if current_margin_value is not None else (
                    25.0 if margin_type == "percentage" else 50.0)
                margin_value = st.number_input(
                    "Spannen-Wert",
                    min_value=0.0,
                    value=float(default_value),
                    step=0.1,
                    help="Prozentsatz oder fester Betrag in Euro",
                    key=f"prod_margin_value_{product_id}"
                )

            # Live preview
            if purchase_price > 0:
                try:
                    if margin_type == "percentage":
                        preview_selling_price = purchase_price * \
                            (1 + margin_value / 100)
                        preview_margin_amount = purchase_price * \
                            (margin_value / 100)
                    else:
                        preview_selling_price = purchase_price + margin_value
                        preview_margin_amount = margin_value

                    st.markdown("**Vorschau:**")
                    prev_col1, prev_col2, prev_col3 = st.columns(3)
                    prev_col1.metric(
                        "Einkaufspreis", f"{
                            purchase_price:.2f} €")
                    prev_col2.metric(
                        "Spanne", f"{
                            preview_margin_amount:.2f} €")
                    prev_col3.metric(
                        "Verkaufspreis", f"{
                            preview_selling_price:.2f} €")

                except Exception as e:
                    st.error(f"Vorschau-Fehler: {e}")

            col_submit, col_remove = st.columns([1, 1])

            with col_submit:
                submitted = st.form_submit_button("💾 Spanne speichern")

            with col_remove:
                remove_margin = st.form_submit_button("🗑️ Spanne entfernen")

            if submitted:
                try:
                    config = MarginConfig(
                        margin_type=margin_type,
                        margin_value=margin_value,
                        applies_to='product',
                        priority=priority
                    )

                    success = margin_manager.set_product_margin(
                        product_id, config)

                    if success:
                        st.success(
                            f"✅ Gewinnspanne für '{
                                selected_product.get('model_name')}' erfolgreich gespeichert!")
                        request_rerun()
                    else:
                        st.error("❌ Fehler beim Speichern der Gewinnspanne")

                except Exception as e:
                    st.error(f"❌ Fehler: {e}")

            if remove_margin:
                try:
                    # Set margin to 0 to effectively remove it
                    config = MarginConfig(
                        margin_type="percentage",
                        margin_value=0.0,
                        applies_to='product',
                        priority=0
                    )

                    success = margin_manager.set_product_margin(
                        product_id, config)

                    if success:
                        st.success(
                            f"✅ Gewinnspanne für '{
                                selected_product.get('model_name')}' entfernt!")
                        request_rerun()
                    else:
                        st.error("❌ Fehler beim Entfernen der Gewinnspanne")

                except Exception as e:
                    st.error(f"❌ Fehler: {e}")


def render_margin_preview_tab(margin_manager: ProfitMarginManager):
    """Render the margin calculation preview and validation tab"""

    st.subheader("🧮 Kalkulations-Vorschau")
    st.markdown(
        "Testen Sie Gewinnspannen-Berechnungen mit verschiedenen Parametern.")

    # Input section
    st.markdown("**Kalkulations-Parameter:**")

    col1, col2 = st.columns(2)

    with col1:
        purchase_price = st.number_input(
            "Einkaufspreis (€)",
            min_value=0.0,
            value=100.0,
            step=0.01,
            key="preview_purchase_price"
        )

        quantity = st.number_input(
            "Menge",
            min_value=0.1,
            value=1.0,
            step=0.1,
            key="preview_quantity"
        )

    with col2:
        calculate_per = st.selectbox(
            "Berechnungsart",
            options=["Stück", "Meter", "pauschal", "kWp"],
            key="preview_calculate_per"
        )

        # Optional product selection for product-specific margins
        try:
            if PRICING_AVAILABLE:
                products = list_products()
                product_options = ["Keine Auswahl"] + [
                    f"{p.get('model_name', 'Unbekannt')} ({p.get('brand', 'Unbekannt')})" for p in products]
                selected_product_preview = st.selectbox(
                    "Produkt (optional)",
                    options=product_options,
                    key="preview_product"
                )

                if selected_product_preview != "Keine Auswahl":
                    # Find the selected product
                    selected_product_data = None
                    for p in products:
                        if f"{
                            p.get(
                                'model_name',
                                'Unbekannt')} ({
                            p.get(
                                'brand',
                                'Unbekannt')})" == selected_product_preview:
                            selected_product_data = p
                            break
                else:
                    selected_product_data = None
            else:
                selected_product_data = None
        except Exception as e:
            st.error(f"Fehler beim Laden der Produkte: {e}")
            selected_product_data = None

    # Category selection for category-specific margins
    try:
        categories = margin_manager.get_available_categories()
        category_options = ["Keine Auswahl"] + categories
        selected_category_preview = st.selectbox(
            "Kategorie (optional)",
            options=category_options,
            key="preview_category"
        )

        if selected_category_preview == "Keine Auswahl":
            selected_category_preview = None
    except Exception as e:
        st.error(f"Fehler beim Laden der Kategorien: {e}")
        selected_category_preview = None

    st.markdown("---")

    # Calculation section
    if st.button("🧮 Berechnung durchführen", key="calculate_preview"):
        try:
            # Get margin breakdown
            product_id = selected_product_data.get(
                'id') if selected_product_data else None

            breakdown = margin_manager.get_margin_breakdown(
                purchase_price=purchase_price,
                product_id=product_id,
                category=selected_category_preview,
                calculate_per=calculate_per,
                quantity=quantity
            )

            # Get total calculation
            total_calc = margin_manager.calculate_total_price_with_margin(
                purchase_price=purchase_price,
                quantity=quantity,
                calculate_per=calculate_per,
                product_id=product_id,
                category=selected_category_preview
            )

            # Display results
            st.markdown("**📊 Berechnungs-Ergebnisse:**")

            # Unit calculations
            st.markdown("*Einzel-Kalkulation:*")
            unit_col1, unit_col2, unit_col3, unit_col4 = st.columns(4)

            unit_col1.metric(
                "Einkaufspreis", f"{
                    breakdown.purchase_price:.2f} €")
            unit_col2.metric("Spanne", f"{breakdown.margin_amount:.2f} €")
            unit_col3.metric(
                "Verkaufspreis", f"{
                    breakdown.selling_price:.2f} €")
            unit_col4.metric("Spanne %", f"{breakdown.margin_percentage:.1f}%")

            # Total calculations
            st.markdown("*Gesamt-Kalkulation:*")
            total_col1, total_col2, total_col3, total_col4 = st.columns(4)

            total_col1.metric("Gesamt-Einkauf",
                              f"{total_calc['total_purchase_price']:.2f} €")
            total_col2.metric("Gesamt-Spanne",
                              f"{total_calc['total_margin_amount']:.2f} €")
            total_col3.metric("Gesamt-Verkauf",
                              f"{total_calc['total_selling_price']:.2f} €")
            total_col4.metric(
                "Spannen-Quelle",
                total_calc['margin_source'].title())

            # Additional information
            st.markdown("**ℹ️ Zusätzliche Informationen:**")
            info_col1, info_col2, info_col3 = st.columns(3)

            info_col1.info(f"**Berechnungsart:** {calculate_per}")
            info_col2.info(f"**Menge:** {quantity}")
            info_col3.info(f"**Spannen-Herkunft:** {breakdown.source.title()}")

            # Validation warnings
            if breakdown.margin_percentage < 10:
                st.warning("⚠️ Niedrige Gewinnspanne (< 10%)")
            elif breakdown.margin_percentage > 100:
                st.warning("⚠️ Sehr hohe Gewinnspanne (> 100%)")

            if breakdown.source == 'none':
                st.warning(
                    "⚠️ Keine Gewinnspanne konfiguriert - Verkaufspreis = Einkaufspreis")

        except Exception as e:
            st.error(f"❌ Fehler bei der Berechnung: {e}")
            st.error(f"Details: {traceback.format_exc()}")

    # Margin comparison section
    st.markdown("---")
    st.markdown("**📈 Spannen-Vergleich:**")

    if st.button("📊 Vergleich erstellen", key="create_comparison"):
        try:
            # Create comparison for different margin scenarios
            scenarios = [
                ("10% Spanne", "percentage", 10.0),
                ("20% Spanne", "percentage", 20.0),
                ("30% Spanne", "percentage", 30.0),
                ("50€ Spanne", "fixed", 50.0),
                ("100€ Spanne", "fixed", 100.0)
            ]

            comparison_data = []

            for scenario_name, margin_type, margin_value in scenarios:
                if margin_type == "percentage":
                    selling_price = purchase_price * (1 + margin_value / 100)
                    margin_amount = purchase_price * (margin_value / 100)
                    margin_percentage = margin_value
                else:
                    selling_price = purchase_price + margin_value
                    margin_amount = margin_value
                    margin_percentage = (
                        margin_amount /
                        purchase_price *
                        100) if purchase_price > 0 else 0

                total_selling = selling_price * quantity
                total_margin = margin_amount * quantity

                comparison_data.append({
                    "Szenario": scenario_name,
                    "Verkaufspreis": f"{selling_price:.2f} €",
                    "Spanne €": f"{margin_amount:.2f} €",
                    "Spanne %": f"{margin_percentage:.1f}%",
                    "Gesamt-Verkauf": f"{total_selling:.2f} €",
                    "Gesamt-Spanne": f"{total_margin:.2f} €"
                })

            df_comparison = pd.DataFrame(comparison_data)
            st.dataframe(df_comparison, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Fehler beim Erstellen des Vergleichs: {e}")


# Main entry point
if __name__ == "__main__":
    render_profit_margin_management_ui()
