#!/usr/bin/env python3
# Quick smoke test for repair_pdf multi-offer price flow
import repair_pdf.multi_offer_generator as mg
import pdf_generator
from repair_pdf.multi_offer_generator import MultiCompanyOfferGenerator
import streamlit as st
import types
import io
import sys
import os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# Minimal st.session_state mock

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


# Monkey patch generate_offer_pdf to inspect dynamic data


def fake_generate_offer_pdf(
        project_data,
        analysis_results,
        company_info=None,
        **kwargs):
    price_keys = [
        'final_offer_price_net',
        'final_price_with_provision',
        'final_price_net',
        'final_price_netto',
        'final_price_brutto']
    pd = project_data.get('project_details', {})
    vals = {k: pd.get(k) for k in price_keys}
    print(
        f"COMPANY {
            company_info.get(
                'id',
                '?')}: project_details prices -> {vals}")
    return b"PDF"


pdf_generator.generate_offer_pdf = fake_generate_offer_pdf
mg.generate_offer_pdf = fake_generate_offer_pdf

# Build generator
mc = MultiCompanyOfferGenerator()

# Wrap apply_price_scaling to log
orig_apply = mc.apply_price_scaling


def wrapped_apply(idx, settings, results):
    out = orig_apply(idx, settings, results)
    print(
        f"APPLY idx={idx} settings={{inc={
            settings.get('price_increment_percent')}, mode={
            settings.get('price_calculation_mode')}}} in={
                results.get('total_investment_netto')} -> out={
                    out.get('total_investment_netto')}")
    return out


mc.apply_price_scaling = wrapped_apply

# Simulate offer data for 3 companies
companies = [{'id': 1, 'name': 'A'}, {
    'id': 2, 'name': 'B'}, {'id': 3, 'name': 'C'}]
customer = {'first_name': 'Test', 'last_name': 'User'}
settings = {}
project_data = {}

for i, comp in enumerate(companies):
    offer = mc._prepare_offer_data(customer, comp, settings, project_data, i)
    pdf = mc._generate_company_pdf(offer, comp, i)
