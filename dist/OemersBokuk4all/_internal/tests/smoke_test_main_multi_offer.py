#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smoke Test für Hauptdatei multi_offer_generator.py
Prüft, dass jede Firma einen anderen Preis bekommt.
"""
import multi_offer_generator as mog
from multi_offer_generator import MultiCompanyOfferGenerator
import streamlit as st
import io
import sys
import os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

# Mock session_state


class SS(dict):
    pass


ss = SS()
ss['calculation_results'] = {
    'total_investment_netto': 20000.0,
    'total_investment_brutto': 23800.0,
}
ss['multi_offer_settings'] = {
    'price_increment_percent': 5.0,
    'price_calculation_mode': 'linear',
}
ss['multi_offer_selected_companies'] = [1, 2, 3]

st.session_state = ss


# Patch generate_offer_pdf to intercept prices

def fake_gen(project_data, analysis_results, company_info=None, **kwargs):
    pd = project_data.get('project_details', {})
    price_keys = [
        'final_offer_price_net',
        'final_price_with_provision',
        'final_price_net',
        'final_price_netto',
        'total_investment_netto']
    vals = {k: pd.get(k) for k in price_keys}
    print(
        f"COMPANY {
            company_info.get(
                'id',
                '?')} ({
            company_info.get(
                'name',
                '?')}): {vals}")
    return b"PDF"


mog.generate_offer_pdf = fake_gen

# Build generator
mc = MultiCompanyOfferGenerator()

# Wrap apply_price_scaling to log
orig_apply = mc.apply_price_scaling


def wrapped_apply(idx, settings, results):
    out = orig_apply(idx, settings, results)
    print(
        f"[apply_price_scaling] idx={idx}: total_investment_netto {
            results.get('total_investment_netto')} -> {
            out.get('total_investment_netto')}")
    return out


mc.apply_price_scaling = wrapped_apply

# Simulate 3 companies
companies = [{'id': 1, 'name': 'Firma A'}, {
    'id': 2, 'name': 'Firma B'}, {'id': 3, 'name': 'Firma C'}]
customer = {'first_name': 'Test', 'last_name': 'User'}
settings = {}
project_data = {}

print("\n" + "=" * 80)
print("SMOKE TEST: multi_offer_generator.py (MAIN)")
print("=" * 80)
print("Basis-Preis: 20.000 EUR")
print("Erwartet: +5% pro Firma (Firma 1=20k, 2=21k, 3=22k)")
print("=" * 80 + "\n")

for i, comp in enumerate(companies):
    print(f"\n--- Firma {i + 1} ---")
    offer = mc._prepare_offer_data(customer, comp, settings, project_data, i)
    pdf = mc._generate_company_pdf(offer, comp, i)

print("\n" + "=" * 80)
print("RESULTAT:")
print("=" * 80)
print("Erfolg, wenn jede Firma einen ANDEREN Preis zeigt!")
print("=" * 80)
