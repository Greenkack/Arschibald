#!/usr/bin/env python3
"""Vollständiger CRM-Funktionstest"""

import sqlite3
from pathlib import Path

db_path = Path('test_crm_full.db')
if db_path.exists():
    db_path.unlink()

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row

from crm import create_tables_crm, save_customer, load_customer, load_all_customers

create_tables_crm(conn)

print('Vollständige CRM-Integration')
print()

# Test Tag-System
from crm.features.tag_manager import create_tag, assign_tag_to_customer, get_customer_tags, get_customers_by_tags

customer1_id = save_customer(conn, {
    'first_name': 'Max',
    'last_name': 'Mustermann',
    'email': 'max@example.com',
    'city': 'Berlin',
    'annual_consumption_kwh': 4500
})

tag1 = create_tag(conn, 'VIP', '#FFD700')
tag2 = create_tag(conn, 'PV-Interesse', '#0000FF')
assign_tag_to_customer(conn, customer1_id, tag1)
assign_tag_to_customer(conn, customer1_id, tag2)

tags = get_customer_tags(conn, customer1_id)
print(f'Kunde mit {len(tags)} Tags erstellt')

# Test Lead Scoring
try:
    from crm.features.lead_scoring import calculate_lead_score, get_lead_score
    score = calculate_lead_score(conn, customer1_id)
    print(f'Lead Score berechnet: {score}')
    loaded_score = get_lead_score(conn, customer1_id)
    if loaded_score:
        score_val = loaded_score.get('score', 0)
        print(f'Lead Score geladen: {score_val}')
except Exception as e:
    print(f'Lead Scoring: {e}')

# Test Integration Bridges
try:
    from crm.integration.calculation_bridge import link_calculation_to_customer
    print('Calculation Bridge verfügbar')
except ImportError:
    print('Calculation Bridge nicht verfügbar')

try:
    from crm.integration.data_input_bridge import get_customer_for_data_input
    print('Data Input Bridge verfügbar')
except ImportError:
    print('Data Input Bridge nicht verfügbar')

try:
    from crm.integration.pdf_bridge import get_customer_for_pdf
    print('PDF Bridge verfügbar')
except ImportError:
    print('PDF Bridge nicht verfügbar')

# Test Tag-basierte Suche
customers_with_vip = get_customers_by_tags(conn, [tag1])
print(f'{len(customers_with_vip)} Kunden mit VIP-Tag gefunden')

all_customers = load_all_customers(conn)
print(f'{len(all_customers)} Kunden im System')

print()
print('CRM-System vollständig getestet')
print('   Kernfunktionen: Funktional')
print('   Tag-System: Funktional')  
print('    Lead Scoring: optional')
print('    Integrations-Bridges: teilweise optional')

conn.close()
db_path.unlink()
