#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from product_db import list_products

modules = list_products('module')
print(f"✅ Gefunden: {len(modules)} Module")

for m in modules[:5]:
    print(
        f"  - {
            m.get(
                'model_name',
                '?')} ({
            m.get(
                'price_euro',
                0):.2f} €, {
            m.get(
                'capacity_w',
                0)} W)")

inverters = list_products('inverter')
print(f"\n✅ Gefunden: {len(inverters)} Wechselrichter")

storage = list_products('storage')
print(f"✅ Gefunden: {len(storage)} Speicher")
