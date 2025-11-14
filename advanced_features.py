# advanced_features.py
"""
Erweiterte Features für die Photovoltaik-Anwendung
Implementiert die 8 fehlenden Features aus der Feature-Analyse
"""

from __future__ import annotations

import math
from typing import Any

# ============================================================================
# FEATURE 1: Grid Tariff Optimization - Stromtarif-Optimierung
# ============================================================================


def grid_tariff_optimization(
    project_data: dict[str, Any],
    analysis_results: dict[str, Any]
) -> dict[str, Any]:
    """
    Optimiert die Stromtarif-Auswahl basierend auf Verbrauchsprofil und PV-Produktion.

    Analysiert:
    - Verschiedene Tarifmodelle (Einheitstarif, HT/NT, dynamisch)
    - Einsparungspotenzial je Tarif
    - Optimale Tarif-Kombination mit PV-Anlage
    - Lastverschiebungspotenzial

    Args:
        project_data: Projektdaten mit Verbrauchsprofil
        analysis_results: Analyseergebnisse mit PV-Produktion

    Returns:
        Dict mit Tarif-Optimierungsergebnissen
    """
    try:
        # Basis-Daten extrahieren
        annual_consumption = project_data.get('annual_consumption', 5000)
        pv_production = analysis_results.get('total_pv_production_year', 0)
        grid_import = analysis_results.get(
            'grid_import_kwh', annual_consumption)

        # Standard-Tarif (Einheitstarif)
        standard_tariff_rate = project_data.get(
            'electricity_price_per_kwh', 0.35)
        standard_cost = grid_import * standard_tariff_rate

        # HT/NT-Tarif (Hoch-/Niedertarif)
        # Annahme: 40% Hochtarif (06:00-22:00), 60% Niedertarif (22:00-06:00)
        ht_rate = standard_tariff_rate * 1.15  # +15% Hochtarif
        nt_rate = standard_tariff_rate * 0.75  # -25% Niedertarif
        ht_consumption = grid_import * 0.4  # 40% in Hochtarif-Zeit
        nt_consumption = grid_import * 0.6  # 60% in Niedertarif-Zeit
        ht_nt_cost = (ht_consumption * ht_rate) + (nt_consumption * nt_rate)
        ht_nt_savings = standard_cost - ht_nt_cost

        # Dynamischer Tarif (simuliert)
        # Annahme: Börsenpreise schwanken zwischen -20% und +30%
        dynamic_avg_rate = standard_tariff_rate * 0.95  # Durchschnittlich 5% günstiger
        dynamic_cost = grid_import * dynamic_avg_rate
        dynamic_savings = standard_cost - dynamic_cost

        # Lastverschiebungspotenzial berechnen
        # Wenn Batterie vorhanden, kann mehr Last verschoben werden
        has_battery = analysis_results.get('has_battery_storage', False)
        battery_capacity = analysis_results.get('battery_capacity_kwh', 0)

        if has_battery and battery_capacity > 0:
            # Mit Batterie: Bis zu 30% der Last kann verschoben werden
            shiftable_load_percentage = 0.30
        else:
            # Ohne Batterie: Nur direkte Lastverschiebung (10-15%)
            shiftable_load_percentage = 0.12

        shiftable_load_kwh = grid_import * shiftable_load_percentage
        shiftable_load_savings = shiftable_load_kwh * (ht_rate - nt_rate)

        # Optimaler Tarif ermitteln
        tariff_options = {
            'Einheitstarif': {
                'cost': standard_cost,
                'savings': 0,
                'rate': standard_tariff_rate,
                'description': 'Standard-Einheitstarif ohne Zeitabhängigkeit'
            },
            'HT/NT-Tarif': {
                'cost': ht_nt_cost,
                'savings': ht_nt_savings,
                'rate_ht': ht_rate,
                'rate_nt': nt_rate,
                'description': 'Hoch-/Niedertarif mit Tageszeitenabhängigkeit'
            },
            'Dynamischer Tarif': {
                'cost': dynamic_cost,
                'savings': dynamic_savings,
                'rate_avg': dynamic_avg_rate,
                'description': 'Börsenbasierter dynamischer Tarif (stündlich)'
            }
        }

        # Beste Option finden
        best_tariff = min(tariff_options.items(), key=lambda x: x[1]['cost'])

        return {
            'tariff_options': tariff_options,
            'recommended_tariff': best_tariff[0],
            'recommended_tariff_data': best_tariff[1],
            'potential_savings': best_tariff[1]['savings'],
            'shiftable_load_kwh': shiftable_load_kwh,
            'shiftable_load_savings': shiftable_load_savings,
            'total_optimization_potential': best_tariff[1]['savings'] + shiftable_load_savings,
            'has_battery': has_battery,
            'battery_advantage': shiftable_load_savings if has_battery else 0}

    except Exception as e:
        return {
            'error': str(e),
            'tariff_options': {},
            'recommended_tariff': 'Einheitstarif',
            'potential_savings': 0
        }


# ============================================================================
# FEATURE 2: Tax Benefit Calculator - Steuervorteile
# ============================================================================

def tax_benefit_calculator(
    project_data: dict[str, Any],
    analysis_results: dict[str, Any]
) -> dict[str, Any]:
    """
    Berechnet steuerliche Vorteile der PV-Anlage.

    Berücksichtigt:
    - Umsatzsteuererstattung
    - Einkommensteuer (Liebhaberei vs. Gewinnerzielungsabsicht)
    - Abschreibungen (AfA)
    - Kleinunternehmerregelung
    - Sonderabschreibungen

    Args:
        project_data: Projektdaten mit Investitionssumme
        analysis_results: Analyseergebnisse mit Einnahmen

    Returns:
        Dict mit Steuervorteilen
    """
    try:
        # Basis-Daten
        total_investment = analysis_results.get('total_investment', 0)
        annual_feed_in_revenue = analysis_results.get(
            'annual_feed_in_revenue', 0)
        annual_savings = analysis_results.get('annual_savings_after_pv', 0)

        # Customer data
        customer_data = project_data.get('customer_data', {})
        is_business = customer_data.get('is_business', False)
        tax_rate = customer_data.get(
            'tax_rate_percent',
            30) / 100  # Standard 30%

        # 1. Umsatzsteuer (19%)
        # Ab 2023: PV-Anlagen bis 30 kWp sind von der Umsatzsteuer befreit
        # Aber: Ältere Anlagen oder >30kWp → Umsatzsteuer kann erstattet werden
        pv_power_kw = project_data.get('pv_power_kw', 10)

        if pv_power_kw <= 30:
            # Keine Umsatzsteuer-Erstattung (aber auch keine USt-Pflicht)
            vat_refund = 0
            vat_note = "Steuerbefreit (§ 12 Abs. 3 UStG)"
        else:
            # Umsatzsteuer-Erstattung möglich (19% vom
            # Netto-Investitionsbetrag)
            vat_refund = total_investment * 0.19 / 1.19  # Von Brutto auf Netto-USt
            vat_note = "Vorsteuerabzug möglich"

        # 2. Abschreibung (AfA)
        # Linear über 20 Jahre: 5% p.a.
        # Oder degressiv: 2,5-fache lineare AfA (max. 25%)

        # Lineare AfA
        afa_years = 20
        linear_afa_rate = 1 / afa_years  # 5%
        annual_linear_afa = total_investment * linear_afa_rate

        # Degressive AfA (falls zulässig)
        # Aktuell nur für bestimmte Wirtschaftsgüter
        degressive_afa_rate = min(linear_afa_rate * 2.5, 0.25)  # Max 25%
        annual_degressive_afa = total_investment * degressive_afa_rate

        # Steuervorteil durch AfA (Einkommensteuer-Ersparnis)
        afa_tax_benefit_linear = annual_linear_afa * tax_rate
        afa_tax_benefit_degressive = annual_degressive_afa * tax_rate

        # 3. Einkommensteuer auf Einspeisevergütung
        # Einnahmen aus Einspeisung sind steuerpflichtig
        # Aber: Kosten können gegengerechnet werden (Betriebskosten, AfA)

        # Geschätzte jährliche Betriebskosten (1-2% der Investition)
        annual_operating_costs = total_investment * 0.015

        # Gewinn = Einnahmen - Kosten - AfA
        taxable_income_linear = annual_feed_in_revenue - \
            annual_operating_costs - annual_linear_afa
        taxable_income_degressive = annual_feed_in_revenue - \
            annual_operating_costs - annual_degressive_afa

        # Steuer auf Gewinn (kann auch negativ sein = Verlust)
        income_tax_linear = max(0, taxable_income_linear * tax_rate)
        income_tax_degressive = max(0, taxable_income_degressive * tax_rate)

        # 4. Gesamte Steuervorteile
        # Jahr 1: Umsatzsteuer-Erstattung + AfA-Vorteil - Einkommensteuer
        first_year_benefit_linear = vat_refund + \
            afa_tax_benefit_linear - income_tax_linear
        first_year_benefit_degressive = vat_refund + \
            afa_tax_benefit_degressive - income_tax_degressive

        # 20-Jahres-Summe
        total_20y_benefit_linear = vat_refund + \
            (afa_tax_benefit_linear * 20) - (income_tax_linear * 20)
        total_20y_benefit_degressive = vat_refund + \
            (afa_tax_benefit_degressive * 20) - (income_tax_degressive * 20)

        # 5. Kleinunternehmerregelung
        # Umsatz < 22.000 € → Keine USt, aber auch kein Vorsteuerabzug
        is_kleinunternehmer = annual_feed_in_revenue < 22000

        return {
            'vat_refund': vat_refund,
            'vat_note': vat_note,
            'pv_power_kw': pv_power_kw,
            'afa_options': {
                'linear': {
                    'rate': linear_afa_rate,
                    'annual_amount': annual_linear_afa,
                    'tax_benefit': afa_tax_benefit_linear,
                    'years': afa_years
                },
                'degressive': {
                    'rate': degressive_afa_rate,
                    'annual_amount': annual_degressive_afa,
                    'tax_benefit': afa_tax_benefit_degressive,
                    'note': 'Nur für bestimmte Anlagen verfügbar'
                }
            },
            'taxable_income': {
                'linear': taxable_income_linear,
                'degressive': taxable_income_degressive,
                'annual_feed_in_revenue': annual_feed_in_revenue,
                'annual_operating_costs': annual_operating_costs
            },
            'income_tax': {
                'linear': income_tax_linear,
                'degressive': income_tax_degressive,
                'tax_rate': tax_rate
            },
            'total_benefit': {
                'first_year_linear': first_year_benefit_linear,
                'first_year_degressive': first_year_benefit_degressive,
                'total_20y_linear': total_20y_benefit_linear,
                'total_20y_degressive': total_20y_benefit_degressive
            },
            'kleinunternehmer': {
                'is_applicable': is_kleinunternehmer,
                'threshold': 22000,
                'annual_revenue': annual_feed_in_revenue
            },
            'recommended_option': 'degressive' if annual_degressive_afa > annual_linear_afa else 'linear'
        }

    except Exception as e:
        return {
            'error': str(e),
            'vat_refund': 0,
            'total_benefit': {'first_year_linear': 0, 'total_20y_linear': 0}
        }


# ============================================================================
# FEATURE 3: Subsidy Optimizer - Förderungs-Optimierung
# ============================================================================

def subsidy_optimizer(
    project_data: dict[str, Any],
    analysis_results: dict[str, Any]
) -> dict[str, Any]:
    """
    Optimiert die Auswahl verfügbarer Förderungen.

    Analysiert:
    - Bundesförderungen (BAFA, KfW)
    - Landesförderungen
    - Kommunale Förderungen
    - Kombinationsmöglichkeiten
    - Optimale Antragsstrategie

    Args:
        project_data: Projektdaten mit Standort und Komponenten
        analysis_results: Analyseergebnisse

    Returns:
        Dict mit Förderungsempfehlungen
    """
    try:
        # Basis-Daten
        total_investment = analysis_results.get('total_investment', 0)
        pv_power_kw = project_data.get('pv_power_kw', 10)
        has_battery = analysis_results.get('has_battery_storage', False)
        battery_capacity = analysis_results.get('battery_capacity_kwh', 0)
        has_heat_pump = project_data.get('has_heat_pump', False)

        # Standort
        customer_data = project_data.get('customer_data', {})
        postal_code = customer_data.get('postal_code', '')
        state = customer_data.get('state', 'Deutschland')

        available_subsidies = []

        # 1. KfW 270 - Erneuerbare Energien Standard
        kfw_270 = {
            'name': 'KfW 270 - Erneuerbare Energien',
            'type': 'Kredit',
            'amount': total_investment * 1.0,  # Bis zu 100% finanzierbar
            'interest_rate': 0.01,  # Aktuell ~1% (stark vereinfacht)
            'conditions': 'Zinsgünstiger Kredit für PV-Anlagen',
            'combinable': True,
            'application': 'Über Hausbank vor Projektbeginn'
        }
        available_subsidies.append(kfw_270)

        # 2. KfW 442 - Solarstrom für Elektroautos (wenn E-Auto vorhanden)
        has_ev = customer_data.get('has_electric_vehicle', False)
        if has_ev and has_battery:
            kfw_442_amount = min(
                10200,  # Maximum
                600 * battery_capacity + 600 * pv_power_kw + 1200  # Staffelung
            )
            kfw_442 = {
                'name': 'KfW 442 - Solarstrom für Elektroautos',
                'type': 'Zuschuss',
                'amount': kfw_442_amount,
                'conditions': 'PV + Speicher + Ladestation + E-Auto erforderlich',
                'combinable': True,
                'application': 'Online über KfW-Zuschussportal'}
            available_subsidies.append(kfw_442)

        # 3. BAFA - Bundesförderung effiziente Gebäude (mit Wärmepumpe)
        if has_heat_pump:
            # Wärmepumpe kann mit 25-40% gefördert werden
            heat_pump_investment = total_investment * 0.3  # Annahme: 30% für Wärmepumpe
            bafa_amount = heat_pump_investment * 0.30  # 30% Förderung

            bafa = {
                'name': 'BAFA - BEG Einzelmaßnahmen (Wärmepumpe)',
                'type': 'Zuschuss',
                'amount': bafa_amount,
                'conditions': 'Wärmepumpe mit JAZ ≥ 3,5 erforderlich',
                'combinable': True,
                'application': 'Online vor Vertragsschluss'
            }
            available_subsidies.append(bafa)

        # 4. Landesförderungen (Beispiele)
        # Diese variieren stark nach Bundesland

        # Bayern: 10.000-Häuser-Programm (Stand 2023, kann sich ändern)
        if 'Bayern' in state or postal_code.startswith(('8', '9')):
            if has_battery and battery_capacity >= 5:
                bayern_battery = {
                    'name': 'Bayern: PV-Speicher-Programm',
                    'type': 'Zuschuss',
                    # 200€/kWh, max 3.200€
                    'amount': min(3200, battery_capacity * 200),
                    'conditions': 'Speicher ≥ 5 kWh, PV-Anlage neu',
                    'combinable': True,
                    'application': 'Online beim Landesamt',
                    'state': 'Bayern'
                }
                available_subsidies.append(bayern_battery)

        # NRW: progres.nrw
        if 'Nordrhein-Westfalen' in state or 'NRW' in state or postal_code.startswith(
                ('4', '5')):
            if has_battery:
                nrw_battery = {
                    'name': 'NRW: progres.nrw - Speicherförderung',
                    'type': 'Zuschuss',
                    # 150€/kWh, max 3.000€
                    'amount': min(3000, battery_capacity * 150),
                    'conditions': 'Neuer Speicher mit neuer oder bestehender PV',
                    'combinable': True,
                    'application': 'Online bei Bezirksregierung',
                    'state': 'Nordrhein-Westfalen'
                }
                available_subsidies.append(nrw_battery)

        # 5. Kommunale Förderungen
        # Beispiel: Städte mit eigenem Klimaschutzprogramm
        municipal_subsidy = {
            'name': 'Kommunale Förderung (falls vorhanden)',
            'type': 'Zuschuss',
            'amount': 500,  # Durchschnittlich 500-2000€
            'conditions': 'Prüfen Sie bei Ihrer Stadt/Gemeinde',
            'combinable': True,
            'application': 'Bei lokaler Verwaltung anfragen',
            'note': 'Viele Kommunen bieten zusätzliche Förderungen'
        }
        available_subsidies.append(municipal_subsidy)

        # 6. Gesamte Förderung berechnen
        total_grants = sum(
            [s['amount'] for s in available_subsidies if s['type'] == 'Zuschuss'])
        total_loans = sum([s['amount']
                          for s in available_subsidies if s['type'] == 'Kredit'])

        # Netto-Investition nach Förderung
        net_investment = total_investment - total_grants

        # Förderquote
        grant_rate = (
            total_grants /
            total_investment *
            100) if total_investment > 0 else 0

        # Optimale Kombination ermitteln
        # Sortiere nach Höhe der Zuschüsse
        grants_sorted = sorted(
            [s for s in available_subsidies if s['type'] == 'Zuschuss'],
            key=lambda x: x['amount'],
            reverse=True
        )

        return {
            'available_subsidies': available_subsidies,
            'total_grants': total_grants,
            'total_loans': total_loans,
            'net_investment': net_investment,
            'grant_rate_percent': grant_rate,
            'top_3_subsidies': grants_sorted[:3],
            'application_order': [
                '1. KfW-Förderung beantragen (VOR Vertragsschluss)',
                '2. BAFA-Antrag stellen (VOR Vertragsschluss)',
                '3. Landesförderung prüfen',
                '4. Kommunale Förderung anfragen',
                '5. Nach Bewilligung: Auftrag erteilen'
            ],
            'important_notes': [
                '[WARNING] Förderungen IMMER vor Vertragsschluss beantragen!',
                '[OK] Mehrere Förderungen sind oft kombinierbar',
                '📅 Fristen und Budget beachten (teilweise begrenzt)',
                '[FILE] Alle Nachweise und Belege aufbewahren'
            ],
            'has_battery': has_battery,
            'has_heat_pump': has_heat_pump,
            'has_ev': has_ev
        }

    except Exception as e:
        return {
            'error': str(e),
            'available_subsidies': [],
            'total_grants': 0,
            'net_investment': total_investment
        }


# ============================================================================
# FEATURE 4: Advanced Battery Optimization - Erweiterte Batterie-Optimierung
# ============================================================================

def advanced_battery_optimization(
    project_data: dict[str, Any],
    analysis_results: dict[str, Any]
) -> dict[str, Any]:
    """
    Erweiterte Optimierung der Batteriespeicher-Konfiguration.

    Analysiert:
    - Optimale Speichergröße (kWh)
    - C-Rate und Entladeverhalten
    - Zyklen-Optimierung
    - Winterbetrieb vs. Sommerbetrieb
    - ROI-Optimierung
    - Mehrwert durch Peak Shaving

    Args:
        project_data: Projektdaten mit PV und Verbrauch
        analysis_results: Analyseergebnisse

    Returns:
        Dict mit Batterie-Optimierung
    """
    try:
        # Basis-Daten
        annual_consumption = project_data.get('annual_consumption', 5000)
        pv_production = analysis_results.get('total_pv_production_year', 0)
        daily_consumption = annual_consumption / 365
        daily_production = pv_production / 365

        current_battery_capacity = analysis_results.get(
            'battery_capacity_kwh', 0)
        has_battery = current_battery_capacity > 0

        # Verschiedene Speichergrößen simulieren
        battery_options = []

        for capacity_kwh in [0, 5, 7, 10, 13, 15, 20]:
            # Eigenverbrauchsquote berechnen
            # Vereinfachte Formel: Mehr Speicher = mehr Eigenverbrauch
            # Aber: Diminishing Returns ab bestimmter Größe

            if capacity_kwh == 0:
                self_consumption_rate = 0.30  # Ohne Speicher ~30%
            else:
                # Mit Speicher: Basis 30% + Speicherfaktor
                # Optimal bei ~1-1,5x Tagesverbrauch
                optimal_capacity = daily_consumption * 1.2
                capacity_factor = min(1.0, capacity_kwh / optimal_capacity)

                # Maximale Erhöhung: +40% Eigenverbrauch
                self_consumption_increase = 0.40 * capacity_factor

                # Sättigungskurve: Je größer, desto weniger zusätzlicher Nutzen
                saturation = math.exp(-capacity_kwh / optimal_capacity / 2)
                self_consumption_rate = 0.30 + \
                    (self_consumption_increase * (1 - saturation * 0.3))

            # Eigenverbrauch und Netzbezug
            self_consumed_kwh = pv_production * self_consumption_rate
            grid_import_kwh = annual_consumption - self_consumed_kwh
            grid_feed_in_kwh = pv_production - self_consumed_kwh

            # Autarkie
            autarky_rate = self_consumed_kwh / \
                annual_consumption if annual_consumption > 0 else 0

            # Kosten
            electricity_price = project_data.get(
                'electricity_price_per_kwh', 0.35)
            feed_in_tariff = project_data.get('feed_in_tariff', 0.08)

            grid_cost = grid_import_kwh * electricity_price
            feed_in_revenue = grid_feed_in_kwh * feed_in_tariff
            savings_from_self_consumption = self_consumed_kwh * \
                (electricity_price - feed_in_tariff)
            annual_benefit = savings_from_self_consumption + feed_in_revenue

            # Batteriekosten
            battery_price_per_kwh = 800  # ca. 800€/kWh inkl. Installation
            battery_investment = capacity_kwh * battery_price_per_kwh

            # ROI (vereinfacht)
            if battery_investment > 0:
                # Zusätzlicher Nutzen durch Batterie
                base_benefit = battery_options[0]['annual_benefit'] if battery_options else annual_benefit
                additional_benefit = annual_benefit - base_benefit

                if additional_benefit > 0:
                    payback_years = battery_investment / additional_benefit
                else:
                    payback_years = 999
            else:
                payback_years = 0

            # Zyklen-Analyse
            daily_cycles = self_consumed_kwh / 365 / \
                capacity_kwh if capacity_kwh > 0 else 0
            annual_cycles = daily_cycles * 365

            # Lebensdauer (typisch 6000-10000 Zyklen)
            cycle_lifetime = 6000
            battery_lifetime_years = cycle_lifetime / \
                annual_cycles if annual_cycles > 0 else 20

            battery_options.append({
                'capacity_kwh': capacity_kwh,
                'self_consumption_rate': self_consumption_rate,
                'self_consumed_kwh': self_consumed_kwh,
                'grid_import_kwh': grid_import_kwh,
                'grid_feed_in_kwh': grid_feed_in_kwh,
                'autarky_rate': autarky_rate,
                'grid_cost': grid_cost,
                'feed_in_revenue': feed_in_revenue,
                'annual_benefit': annual_benefit,
                'battery_investment': battery_investment,
                'payback_years': payback_years,
                'daily_cycles': daily_cycles,
                'annual_cycles': annual_cycles,
                'battery_lifetime_years': min(battery_lifetime_years, 20)
            })

        # Optimale Größe finden
        # Kriterium: Beste Balance zwischen Autarkie und ROI
        # Payback sollte < 15 Jahre sein

        viable_options = [
            opt for opt in battery_options if opt['capacity_kwh'] > 0 and opt['payback_years'] < 15]

        if viable_options:
            # Beste Option: Höchste Autarkie mit akzeptablem Payback
            best_option = max(viable_options, key=lambda x: x['autarky_rate'])
        else:
            # Keine wirtschaftliche Option → Kleinste Batterie
            best_option = battery_options[1] if len(
                battery_options) > 1 else battery_options[0]

        # Empfehlung
        if best_option['capacity_kwh'] == 0:
            recommendation = "Batterie nicht wirtschaftlich sinnvoll"
        elif best_option['capacity_kwh'] != current_battery_capacity:
            if current_battery_capacity == 0:
                recommendation = f"Batterie mit {
                    best_option['capacity_kwh']} kWh empfohlen"
            else:
                recommendation = f"Optimierung: {
                    best_option['capacity_kwh']} kWh (aktuell: {current_battery_capacity} kWh)"
        else:
            recommendation = "Aktuelle Konfiguration bereits optimal"

        return {
            'current_capacity': current_battery_capacity,
            'battery_options': battery_options,
            'optimal_capacity': best_option['capacity_kwh'],
            'optimal_data': best_option,
            'recommendation': recommendation,
            'improvement_potential': {
                'autarky_increase': best_option['autarky_rate'] - battery_options[0]['autarky_rate'],
                'additional_savings': best_option['annual_benefit'] - battery_options[0]['annual_benefit'],
                'investment_required': best_option['battery_investment']}}

    except Exception as e:
        return {
            'error': str(e),
            'current_capacity': 0,
            'battery_options': [],
            'recommendation': 'Fehler bei Berechnung'
        }


# ============================================================================
# FEATURE 5: Financing Scenario Comparison - Vollständiger Finanzierungs-Vergleich
# ============================================================================

def financing_scenario_comparison(
    project_data: dict[str, Any],
    analysis_results: dict[str, Any]
) -> dict[str, Any]:
    """
    Vollständiger Vergleich aller Finanzierungsszenarien.

    Vergleicht:
    - Barkauf
    - Bankkredit (verschiedene Laufzeiten)
    - Leasing
    - Mietkauf / PPA
    - Mit und ohne Eigenkapital

    Args:
        project_data: Projektdaten mit Finanzierung
        analysis_results: Analyseergebnisse

    Returns:
        Dict mit Finanzierungs-Szenarien-Vergleich
    """
    try:
        # Basis-Daten
        total_investment = analysis_results.get('total_investment', 0)
        annual_savings = analysis_results.get('annual_savings_after_pv', 0)
        annual_feed_in = analysis_results.get('annual_feed_in_revenue', 0)
        annual_benefit = annual_savings + annual_feed_in

        scenarios = []

        # 1. Barkauf (Vollzahlung)
        cash_purchase = {
            'name': 'Barkauf (Vollzahlung)',
            'type': 'cash',
            'initial_payment': total_investment,
            'monthly_payment': 0,
            'total_payment_20y': total_investment,
            'total_interest': 0,
            'annual_cost': 0,
            'net_benefit_year1': annual_benefit,
            'net_benefit_20y': annual_benefit * 20,
            'roi_20y': (
                annual_benefit * 20 - total_investment) / total_investment * 100,
            'payback_years': total_investment / annual_benefit if annual_benefit > 0 else 999,
            'description': 'Einmalige Zahlung, keine laufenden Kosten'}
        scenarios.append(cash_purchase)

        # 2. Bankkredit (verschiedene Laufzeiten)
        for loan_years in [10, 15, 20]:
            interest_rate = 0.035  # 3.5% Standard-Zinssatz

            # Annuitätenberechnung
            monthly_rate = interest_rate / 12
            num_payments = loan_years * 12

            if monthly_rate > 0:
                monthly_payment = total_investment * \
                    (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
            else:
                monthly_payment = total_investment / num_payments

            total_payment = monthly_payment * num_payments
            total_interest = total_payment - total_investment
            annual_loan_cost = monthly_payment * 12

            # Nach Kreditende: Volle Einsparungen
            years_after_loan = 20 - loan_years
            total_benefit_20y = (annual_benefit - annual_loan_cost) * \
                loan_years + annual_benefit * years_after_loan

            loan_scenario = {
                'name': f'Bankkredit {loan_years} Jahre',
                'type': 'loan',
                'initial_payment': 0,
                'monthly_payment': monthly_payment,
                'loan_years': loan_years,
                'interest_rate': interest_rate * 100,
                'total_payment_20y': total_payment,
                'total_interest': total_interest,
                'annual_cost': annual_loan_cost,
                'net_benefit_year1': annual_benefit - annual_loan_cost,
                'net_benefit_20y': total_benefit_20y,
                'roi_20y': (
                    total_benefit_20y / total_payment * 100) if total_payment > 0 else 0,
                'payback_years': loan_years + (
                    total_payment - total_investment) / annual_benefit if annual_benefit > 0 else 999,
                'description': f'Monatliche Rate über {loan_years} Jahre'}
            scenarios.append(loan_scenario)

        # 3. Leasing
        leasing_years = 15
        leasing_factor = 0.012  # 1.2% pro Monat vom Investitionswert
        monthly_leasing = total_investment * leasing_factor
        total_leasing_payment = monthly_leasing * 12 * leasing_years
        annual_leasing_cost = monthly_leasing * 12

        # Nach Leasing: Kauf oder Rückgabe (hier: Kauf für 10% des Wertes)
        residual_value = total_investment * 0.10
        total_payment_leasing = total_leasing_payment + residual_value

        years_after_leasing = 20 - leasing_years
        total_benefit_leasing = (annual_benefit - annual_leasing_cost) * \
            leasing_years + annual_benefit * years_after_leasing

        leasing_scenario = {
            'name': 'Leasing 15 Jahre',
            'type': 'leasing',
            'initial_payment': 0,
            'monthly_payment': monthly_leasing,
            'lease_years': leasing_years,
            'leasing_factor': leasing_factor * 100,
            'total_payment_20y': total_payment_leasing,
            'residual_value': residual_value,
            'annual_cost': annual_leasing_cost,
            'net_benefit_year1': annual_benefit - annual_leasing_cost,
            'net_benefit_20y': total_benefit_leasing,
            'roi_20y': (
                total_benefit_leasing / total_payment_leasing * 100) if total_payment_leasing > 0 else 0,
            'description': 'Monatliche Leasingrate, Restwert am Ende'}
        scenarios.append(leasing_scenario)

        # 4. Mietkauf / PPA (Power Purchase Agreement)
        # Vereinfachtes Modell: Kein Kauf, nur Miete für 20 Jahre
        monthly_rental = total_investment * 0.008  # 0.8% monatliche Miete
        annual_rental_cost = monthly_rental * 12
        total_rental_20y = annual_rental_cost * 20

        # Bei PPA: Nutzen reduziert um Mietkosten
        net_benefit_ppa = annual_benefit - annual_rental_cost
        total_benefit_ppa = net_benefit_ppa * 20

        ppa_scenario = {
            'name': 'Mietkauf / PPA 20 Jahre',
            'type': 'ppa',
            'initial_payment': 0,
            'monthly_payment': monthly_rental,
            'rental_years': 20,
            'total_payment_20y': total_rental_20y,
            'annual_cost': annual_rental_cost,
            'net_benefit_year1': net_benefit_ppa,
            'net_benefit_20y': total_benefit_ppa,
            'roi_20y': (
                total_benefit_ppa /
                total_rental_20y *
                100) if total_rental_20y > 0 else 0,
            'description': 'Keine Eigentumsübertragung, laufende Miete',
            'note': 'Anlage bleibt Eigentum des Vermieters'}
        scenarios.append(ppa_scenario)

        # Beste Option ermitteln
        # Kriterium: Höchster Netto-Nutzen nach 20 Jahren
        best_scenario = max(scenarios, key=lambda x: x['net_benefit_20y'])

        # Rankings
        by_net_benefit = sorted(
            scenarios,
            key=lambda x: x['net_benefit_20y'],
            reverse=True)
        by_payback = sorted([s for s in scenarios if 'payback_years' in s],
                            key=lambda x: x.get('payback_years', 999))
        by_monthly_cost = sorted(
            [s for s in scenarios if s['monthly_payment'] > 0], key=lambda x: x['monthly_payment'])

        return {
            'scenarios': scenarios, 'best_scenario': best_scenario, 'rankings': {
                'by_net_benefit': [
                    s['name'] for s in by_net_benefit], 'by_payback': [
                    s['name'] for s in by_payback], 'by_monthly_cost': [
                    s['name'] for s in by_monthly_cost] if by_monthly_cost else []}, 'comparison_matrix': {
                        'initial_payment': {
                            s['name']: s['initial_payment'] for s in scenarios}, 'monthly_payment': {
                                s['name']: s['monthly_payment'] for s in scenarios}, 'total_cost_20y': {
                                    s['name']: s['total_payment_20y'] for s in scenarios}, 'net_benefit_20y': {
                                        s['name']: s['net_benefit_20y'] for s in scenarios}, 'roi_20y': {
                                            s['name']: s['roi_20y'] for s in scenarios}}, 'recommendation': f"Beste Option: {
                                                best_scenario['name']} mit {
                                                    best_scenario['net_benefit_20y']:,.0f} € Netto-Nutzen über 20 Jahre"}

    except Exception as e:
        return {
            'error': str(e),
            'scenarios': [],
            'recommendation': 'Fehler bei Berechnung'
        }


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def get_all_advanced_features(
    project_data: dict[str, Any],
    analysis_results: dict[str, Any]
) -> dict[str, Any]:
    """
    Führt alle erweiterten Features aus und gibt Ergebnisse zurück.

    Args:
        project_data: Projektdaten
        analysis_results: Analyseergebnisse

    Returns:
        Dict mit allen Feature-Ergebnissen
    """
    return {
        'grid_tariff_optimization': grid_tariff_optimization(project_data, analysis_results),
        'tax_benefits': tax_benefit_calculator(project_data, analysis_results),
        'subsidy_optimization': subsidy_optimizer(project_data, analysis_results),
        'battery_optimization': advanced_battery_optimization(project_data, analysis_results),
        'financing_scenarios': financing_scenario_comparison(project_data, analysis_results)
    }
