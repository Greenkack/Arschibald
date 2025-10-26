# admin_product_attributes_ui.py
# Kleines Streamlit-UI zur Verwaltung von Produkt-Attributen (separat,
# keine bestehenden UIs geändert)
from __future__ import annotations

import streamlit as st

from product_attributes import (
    delete_attribute,
    export_attributes_to_csv,
    import_attributes_from_csv,
    list_attributes,
    upsert_attribute,
)
from product_db import get_product_by_model_name, list_products

st.set_page_config(page_title="Produkt-Attribute", layout="wide")
st.title("Produkt-Attribute verwalten")

with st.sidebar:
    st.header("CSV Import/Export")
    exp_col, imp_col = st.columns(2)
    with exp_col:
        if st.button("Export CSV"):
            path = st.text_input(
                "Pfad für Export",
                value="attributes_export.csv",
                key="exp_path")
            if path:
                ok = export_attributes_to_csv(path)
                st.success("Exportiert") if ok else st.error(
                    "Fehler beim Export")
    with imp_col:
        upf = st.file_uploader("CSV importieren", type=["csv"], key="imp_csv")
        if upf is not None:
            import os
            import tempfile
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
            tmp.write(upf.read())
            tmp.close()
            count = import_attributes_from_csv(tmp.name)
            os.unlink(tmp.name)
            st.success(f"Importiert/Upsertet: {count}")

st.subheader("Produkte")
category = st.selectbox(
    "Kategorie",
    options=[
        "",
        "Modul",
        "Wechselrichter",
        "Batteriespeicher"],
    index=1)
products = list_products(category=category or None)
model_names = [p.get("model_name") for p in products]
selected_model = st.selectbox("Modell wählen", options=[""] + model_names)

if selected_model:
    prod = get_product_by_model_name(selected_model)
    if not prod:
        st.warning("Produkt nicht gefunden.")
    else:
        st.write(f"ID: {prod['id']} | Marke: {prod.get('brand')}")
        st.markdown("---")
        st.subheader("Attribute")
        attrs = list_attributes(int(prod['id']))
        for a in attrs:
            cols = st.columns([2, 3, 1, 1, 1])
            cols[0].write(a.get('attribute_key'))
            cols[1].write(a.get('attribute_value'))
            cols[2].write(a.get('unit') or "")
            cols[3].write(a.get('display_order'))
            if cols[4].button("Löschen", key=f"del_{a['id']}"):
                delete_attribute(int(a['id']))
                st.rerun()

        st.markdown("---")
        st.subheader("Neues/Update Attribut")
        with st.form("attr_form"):
            akey = st.text_input("Key (z. B. cell_technology)")
            aval = st.text_input("Wert")
            unit = st.text_input("Einheit", value="")
            dord = st.number_input("Reihenfolge", value=0, step=1)
            submitted = st.form_submit_button("Speichern")
            if submitted:
                if akey:
                    ok_id = upsert_attribute(int(prod['id']), prod.get(
                        'category') or category or '', akey, aval or None, unit or None, int(dord))
                    if ok_id:
                        st.success("Gespeichert")
                        st.rerun()
                else:
                    st.error("Key fehlt")
