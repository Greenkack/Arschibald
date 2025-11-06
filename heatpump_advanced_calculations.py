"""
Erweiterte Wärmepumpen-Berechnungen
Advanced Heat Pump Calculations Module

Enthält professionelle Berechnungen für:
- JAZ-Prognose (Feature 1.1)
- Pufferspeicher-Dimensionierung (Feature 1.2)
- Preisszenario-Analyse (Feature 2.2)
- Steuerliche Vorteile (Feature 2.3)
- Lautstärke-Analyse (Feature 3.2)
- Jahresganglinie (Feature 3.3)
- Smart-Grid Integration (Feature 4.1)
- Netzdienlichkeits-Bonus (Feature 4.2)
- Hybridheizung-Vergleich (Feature 4.3)
- Ökobilanz (Feature 6.1)
- Kältemittel-Vergleich (Feature 6.2)
- Wartungskosten (Feature 8.1)
- Extremwetter-Szenario (Feature 8.2)

Author: GitHub Copilot
Date: 2025-11-06
"""

from typing import Dict, List, Tuple, Any
import math


# ============================================================================
# FEATURE 1.1: INTELLIGENTE JAZ-PROGNOSE
# ============================================================================

def calculate_jaz_prognosis(
    building_data: Dict[str, Any],
    heatpump_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Berechnet realistische Jahresarbeitszahl (JAZ) unter Berücksichtigung aller Faktoren
    
    Parameter:
    - building_data: Gebäudedaten (system_temp, insulation, outside_temp, etc.)
    - heatpump_data: Wärmepumpen-Daten (scop, type, manufacturer)
    
    Returns:
    - Dict mit JAZ-Prognosen und Einflussfaktoren
    """
    
    # Basis: SCOP (Seasonal Coefficient of Performance)
    base_scop = heatpump_data.get('scop', 4.0)
    
    # Faktor 1: Vorlauftemperatur-Einfluss
    system_temp = building_data.get('system_temp', 55)
    if system_temp <= 35:
        temp_factor = 1.15  # Fußbodenheizung optimal
    elif system_temp <= 45:
        temp_factor = 1.05  # Niedertemperatur-Heizkörper
    elif system_temp <= 55:
        temp_factor = 0.95  # Standard-Heizkörper
    else:
        temp_factor = 0.85  # Alte Heizkörper, hohe Vorlauftemp
    
    # Faktor 2: Dämmqualität
    insulation = building_data.get('insulation', 'Durchschnittlich')
    if insulation in ['Sehr gut', 'Passivhaus']:
        insulation_factor = 1.10
    elif insulation == 'Gut':
        insulation_factor = 1.05
    elif insulation == 'Durchschnittlich':
        insulation_factor = 1.00
    else:  # Schlecht, Unsaniert
        insulation_factor = 0.90
    
    # Faktor 3: Klimazone (Außentemperatur)
    outside_temp = building_data.get('outside_temp', -12)
    if outside_temp >= -10:
        climate_factor = 1.05  # Mild
    elif outside_temp >= -15:
        climate_factor = 1.00  # Standard
    else:
        climate_factor = 0.95  # Kalt
    
    # Faktor 4: Wärmepumpentyp
    wp_type = heatpump_data.get('type', 'Luft-Wasser')
    if 'Sole' in wp_type or 'Wasser' in wp_type:
        type_factor = 1.10  # Erdwärme/Grundwasser effizienter
    else:
        type_factor = 1.00  # Luft-Wasser
    
    # Faktor 5: Teillastbetrieb & Regelung
    # Moderne Inverter-WP arbeiten im Teillast besser
    inverter_factor = 0.98  # Kleine Verluste durch Regelung
    
    # Faktor 6: Abtauverluste (nur Luft-WP)
    if 'Luft' in wp_type:
        defrost_factor = 0.95  # 5% Verlust durch Abtauen
    else:
        defrost_factor = 1.00
    
    # Faktor 7: Hydraulischer Abgleich
    # Annahme: Neubau hat hydraulischen Abgleich
    building_year = building_data.get('year', 2000)
    if building_year >= 2010:
        hydraulic_factor = 1.00
    else:
        hydraulic_factor = 0.93  # 7% Verlust ohne Abgleich
    
    # Realistische JAZ berechnen
    jaz_realistic = base_scop * temp_factor * insulation_factor * climate_factor * \
                    type_factor * inverter_factor * defrost_factor * hydraulic_factor
    
    # Optimistische JAZ (beste Bedingungen)
    jaz_optimistic = base_scop * 1.15 * 1.10 * 1.05 * type_factor
    
    # Pessimistische JAZ (schlechteste Bedingungen)
    jaz_pessimistic = base_scop * 0.85 * 0.90 * 0.95 * inverter_factor * defrost_factor * hydraulic_factor
    
    # Vergleich zu Norm-SCOP
    jaz_deviation_percent = ((jaz_realistic - base_scop) / base_scop) * 100
    
    return {
        'jaz_realistic': round(jaz_realistic, 2),
        'jaz_optimistic': round(jaz_optimistic, 2),
        'jaz_pessimistic': round(jaz_pessimistic, 2),
        'base_scop': base_scop,
        'deviation_percent': round(jaz_deviation_percent, 1),
        'factors': {
            'vorlauftemperatur': {
                'value': system_temp,
                'factor': temp_factor,
                'impact_percent': round((temp_factor - 1) * 100, 1)
            },
            'dämmung': {
                'value': insulation,
                'factor': insulation_factor,
                'impact_percent': round((insulation_factor - 1) * 100, 1)
            },
            'klimazone': {
                'value': outside_temp,
                'factor': climate_factor,
                'impact_percent': round((climate_factor - 1) * 100, 1)
            },
            'wärmepumpentyp': {
                'value': wp_type,
                'factor': type_factor,
                'impact_percent': round((type_factor - 1) * 100, 1)
            },
            'abtauverluste': {
                'factor': defrost_factor,
                'impact_percent': round((defrost_factor - 1) * 100, 1)
            },
            'hydraulischer_abgleich': {
                'factor': hydraulic_factor,
                'impact_percent': round((hydraulic_factor - 1) * 100, 1)
            }
        },
        'interpretation': _interpret_jaz(jaz_realistic),
        'recommendations': _get_jaz_recommendations(
            temp_factor, insulation_factor, hydraulic_factor, building_year
        )
    }


def _interpret_jaz(jaz: float) -> str:
    """Interpretiert die JAZ"""
    if jaz >= 4.5:
        return "Hervorragend - Top-Effizienz"
    elif jaz >= 4.0:
        return "Sehr gut - Hohe Effizienz"
    elif jaz >= 3.5:
        return "Gut - Solide Effizienz"
    elif jaz >= 3.0:
        return "Befriedigend - Verbesserungspotenzial"
    else:
        return "Unzureichend - Dringend optimieren"


def _get_jaz_recommendations(
    temp_factor: float,
    insulation_factor: float,
    hydraulic_factor: float,
    building_year: int
) -> List[str]:
    """Gibt Empfehlungen zur JAZ-Verbesserung"""
    recommendations = []
    
    if temp_factor < 1.0:
        recommendations.append(
            "🔧 Vorlauftemperatur senken: Größere Heizkörper oder Fußbodenheizung installieren (JAZ-Gewinn: +10-20%)"
        )
    
    if insulation_factor < 1.0:
        recommendations.append(
            "🏠 Dämmung verbessern: Dach, Fassade oder Keller dämmen (JAZ-Gewinn: +5-10%)"
        )
    
    if hydraulic_factor < 1.0:
        recommendations.append(
            "⚙️ Hydraulischen Abgleich durchführen (Kosten: ~500€, JAZ-Gewinn: +7%)"
        )
    
    if not recommendations:
        recommendations.append("✅ System bereits optimal ausgelegt - keine weiteren Maßnahmen erforderlich")
    
    return recommendations


# ============================================================================
# FEATURE 1.2: PUFFERSPEICHER-DIMENSIONIERUNG
# ============================================================================

def calculate_buffer_tank_size(
    building_data: Dict[str, Any],
    heatpump_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Berechnet optimale Pufferspeichergröße
    
    Faktoren:
    - Heizleistung WP
    - Mindestlaufzeit (10-15 Min)
    - Gebäudewärmebedarf
    - Hydraulische Einbindung
    
    Returns:
    - Dict mit Empfehlung und Begründung
    """
    
    heat_load_kw = building_data.get('heat_load_kw', 10)
    wp_power_kw = heatpump_data.get('heating_power', heat_load_kw * 1.2)
    building_area = building_data.get('area', 150)
    
    # Methode 1: Nach Mindestlaufzeit (15 Minuten)
    # Puffer = WP-Leistung × Mindestlaufzeit / Temperaturspreizung
    min_runtime_hours = 0.25  # 15 Minuten
    temp_spread = 10  # K (typisch: 45°C Vorlauf, 35°C Rücklauf)
    
    # Wärmekapazität Wasser: 4,18 kJ/(kg·K) = 1,16 kWh/(m³·K)
    buffer_by_runtime = (wp_power_kw * min_runtime_hours) / (1.16 * temp_spread)
    buffer_by_runtime_liters = buffer_by_runtime * 1000
    
    # Methode 2: Nach Wohnfläche (Faustformel)
    # 15-20 Liter pro kW Heizleistung
    buffer_by_power = wp_power_kw * 17.5  # Mittelwert
    
    # Methode 3: Nach Gebäudetyp
    building_type = building_data.get('type', 'Einfamilienhaus')
    if building_type == 'Mehrfamilienhaus':
        buffer_by_type = max(500, building_area * 2.5)
    else:
        buffer_by_type = max(200, building_area * 1.5)
    
    # Empfohlene Größe: Maximum der drei Methoden
    recommended_size = max(buffer_by_runtime_liters, buffer_by_power, buffer_by_type)
    
    # Standardgrößen anpassen (marktüblich: 200, 300, 500, 800, 1000 L)
    standard_sizes = [200, 300, 500, 800, 1000, 1500, 2000]
    recommended_standard = min([s for s in standard_sizes if s >= recommended_size], default=2000)
    
    # Minimalgröße (gegen Takten)
    min_size = max(100, wp_power_kw * 10)
    
    # Maximalgröße (Wirtschaftlichkeit)
    max_size = wp_power_kw * 30
    
    # Hydraulische Einbindung prüfen
    wp_type = heatpump_data.get('type', 'Luft-Wasser')
    if 'Luft' in wp_type:
        hydraulic_note = "Luft-WP: Pufferspeicher empfohlen zur Taktreduzierung"
        buffer_priority = "Hoch"
    else:
        hydraulic_note = "Sole/Wasser-WP: Pufferspeicher optional, aber vorteilhaft"
        buffer_priority = "Mittel"
    
    # Kostenabschätzung
    cost_per_liter = 1.5  # € pro Liter (inkl. Installation)
    estimated_cost = recommended_standard * cost_per_liter
    
    return {
        'recommended_size_liters': int(recommended_standard),
        'min_size_liters': int(min_size),
        'max_size_liters': int(max_size),
        'calculation_methods': {
            'by_runtime': int(buffer_by_runtime_liters),
            'by_power': int(buffer_by_power),
            'by_building_type': int(buffer_by_type)
        },
        'reasoning': f"Basierend auf {wp_power_kw:.1f} kW WP-Leistung und {building_area} m² Wohnfläche",
        'hydraulic_note': hydraulic_note,
        'buffer_priority': buffer_priority,
        'estimated_cost_eur': int(estimated_cost),
        'benefits': [
            "Reduziert Takthäufigkeit der Wärmepumpe",
            "Verlängert Lebensdauer des Verdichters",
            "Ermöglicht bessere Nutzung von PV-Strom",
            "Puffert Lastspitzen ab",
            "Verbessert Regelverhalten"
        ],
        'alternatives': {
            'ohne_puffer': {
                'description': "Direktbetrieb ohne Puffer",
                'geeignet_für': "Sehr gut gedämmte Neubauten mit Fußbodenheizung",
                'risiken': ["Häufiges Takten", "Kürzere Lebensdauer"]
            },
            'kleinerer_puffer': {
                'size_liters': int(recommended_standard * 0.7),
                'description': "Kompromisslösung bei Platzmangel",
                'nachteile': ["Geringerer Taktschutz", "Weniger Speicherkapazität"]
            }
        }
    }


# ============================================================================
# FEATURE 2.2: PREISSZENARIO-ANALYSE
# ============================================================================

def calculate_price_scenarios(
    building_data: Dict[str, Any],
    heatpump_data: Dict[str, Any],
    economics_data: Dict[str, Any],
    years: int = 20
) -> Dict[str, Any]:
    """
    Simuliert verschiedene Energiepreis-Entwicklungsszenarien
    
    Szenarien:
    - Konservativ: +2% pro Jahr
    - Realistisch: +5% pro Jahr
    - Pessimistisch: +10% pro Jahr
    
    Returns:
    - Dict mit Szenarien und Visualisierungsdaten
    """
    
    # Aktuelle Kosten
    annual_heating_cost_old = building_data.get('heating_costs', {}).get('total_annual', 3000)
    annual_heating_cost_wp = economics_data.get('annual_hp_cost', 1500)
    investment = heatpump_data.get('price', 15000) + economics_data.get('installation_cost', 3000)
    subsidy = economics_data.get('subsidy_amount', 4500)
    net_investment = investment - subsidy
    
    # Strompreis-Annahmen
    electricity_price_kwh = economics_data.get('electricity_price', 32) / 100
    
    scenarios = {}
    
    # Szenario-Parameter
    scenario_configs = {
        'konservativ': {
            'increase_rate_old': 0.02,
            'increase_rate_electricity': 0.02,
            'description': 'Moderate Preissteigerung',
            'probability': 'Hoch (60%)'
        },
        'realistisch': {
            'increase_rate_old': 0.05,
            'increase_rate_electricity': 0.04,
            'description': 'Realistische Preisentwicklung basierend auf historischen Daten',
            'probability': 'Mittel (30%)'
        },
        'pessimistisch': {
            'increase_rate_old': 0.10,
            'increase_rate_electricity': 0.08,
            'description': 'Starke Preissteigerung (Energiekrise-Szenario)',
            'probability': 'Niedrig (10%)'
        }
    }
    
    for scenario_name, config in scenario_configs.items():
        cumulative_cost_old = 0
        cumulative_cost_wp = net_investment
        cumulative_savings = -net_investment  # Start mit Investition
        
        yearly_data = []
        
        cost_old = annual_heating_cost_old
        cost_wp = annual_heating_cost_wp
        
        payback_year = None
        
        for year in range(years + 1):
            if year > 0:
                # Preiserhöhung anwenden
                cost_old *= (1 + config['increase_rate_old'])
                cost_wp *= (1 + config['increase_rate_electricity'])
            
            cumulative_cost_old += cost_old
            cumulative_cost_wp += cost_wp
            cumulative_savings = cumulative_cost_old - cumulative_cost_wp
            
            # Amortisationsjahr ermitteln
            if cumulative_savings >= 0 and payback_year is None and year > 0:
                payback_year = year
            
            yearly_data.append({
                'year': year,
                'cost_old_annual': round(cost_old, 2),
                'cost_wp_annual': round(cost_wp, 2),
                'cumulative_cost_old': round(cumulative_cost_old, 2),
                'cumulative_cost_wp': round(cumulative_cost_wp, 2),
                'cumulative_savings': round(cumulative_savings, 2),
                'annual_savings': round(cost_old - cost_wp, 2) if year > 0 else 0
            })
        
        # Gesamtersparnis nach 20 Jahren
        total_savings = cumulative_savings
        roi_percent = (total_savings / net_investment) * 100 if net_investment > 0 else 0
        
        scenarios[scenario_name] = {
            'config': config,
            'yearly_data': yearly_data,
            'payback_year': payback_year if payback_year else "> 20",
            'total_savings_20y': round(total_savings, 2),
            'roi_percent': round(roi_percent, 1),
            'final_annual_cost_old': round(cost_old, 2),
            'final_annual_cost_wp': round(cost_wp, 2),
            'final_annual_savings': round(cost_old - cost_wp, 2)
        }
    
    # Best-Case / Worst-Case
    best_case = scenarios['pessimistisch']  # Bei hohen Preisen spart WP am meisten
    worst_case = scenarios['konservativ']
    
    return {
        'scenarios': scenarios,
        'best_case': {
            'scenario': 'pessimistisch',
            'total_savings': best_case['total_savings_20y'],
            'payback': best_case['payback_year']
        },
        'worst_case': {
            'scenario': 'konservativ',
            'total_savings': worst_case['total_savings_20y'],
            'payback': worst_case['payback_year']
        },
        'recommendation': _get_scenario_recommendation(scenarios),
        'net_investment': net_investment,
        'sensitivity_analysis': {
            'investment_impact': 'Jede 1.000€ mehr Investment verschiebt Amortisation um ~1 Jahr',
            'price_increase_impact': 'Jedes +1% Preissteigerung verbessert ROI um ~15%'
        }
    }


def _get_scenario_recommendation(scenarios: Dict) -> str:
    """Gibt Empfehlung basierend auf Szenarien"""
    realistic_payback = scenarios['realistisch']['payback_year']
    realistic_savings = scenarios['realistisch']['total_savings_20y']
    
    if isinstance(realistic_payback, int) and realistic_payback <= 10:
        return f"✅ Sehr empfehlenswert: Amortisation in {realistic_payback} Jahren, Ersparnis nach 20J: {realistic_savings:,.2f}€"
    elif isinstance(realistic_payback, int) and realistic_payback <= 15:
        return f"👍 Empfehlenswert: Amortisation in {realistic_payback} Jahren, langfristig rentabel"
    else:
        return "⚠️ Langfristige Investition: Amortisation >15 Jahre, andere Faktoren (Komfort, CO₂) berücksichtigen"


# ============================================================================
# FEATURE 2.3: STEUERLICHE VORTEILE RECHNER
# ============================================================================

def calculate_tax_benefits(
    heatpump_data: Dict[str, Any],
    building_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Berechnet steuerliche Absetzbarkeit
    
    Regelungen:
    1. Handwerkerleistungen: 20% von max. 6.000€ = max. 1.200€/Jahr
    2. Energetische Sanierung (§35c EStG): 20% über 3 Jahre (max. 40.000€)
    
    Returns:
    - Dict mit Steuervorteilen
    """
    
    device_price = heatpump_data.get('price', 15000)
    installation_price = heatpump_data.get('installation_price', 3000)
    total_investment = device_price + installation_price
    
    building_year = building_data.get('year', 2000)
    is_old_building = building_year < 2002  # Vor 2002 = Altbau
    
    tax_benefits = {
        'handwerkerleistungen': {},
        'energetische_sanierung': {},
        'total_benefit': 0,
        'net_investment_after_tax': 0
    }
    
    # 1. Handwerkerleistungen (§35a EStG)
    # 20% von Arbeitskosten, max. 1.200€/Jahr
    labor_cost = installation_price
    max_deductible_labor = min(labor_cost, 6000)
    handwerker_benefit = max_deductible_labor * 0.20
    handwerker_benefit = min(handwerker_benefit, 1200)
    
    tax_benefits['handwerkerleistungen'] = {
        'labor_cost': labor_cost,
        'deductible_amount': max_deductible_labor,
        'tax_benefit': handwerker_benefit,
        'description': 'Jährlich absetzbar für Arbeitskosten',
        'paragraph': '§35a EStG',
        'requirements': [
            'Rechnung mit ausgewiesenen Arbeitskosten',
            'Überweisung (keine Barzahlung)',
            'Arbeit im eigenen Haushalt'
        ]
    }
    
    # 2. Energetische Sanierung (§35c EStG)
    # Nur für Altbauten (>10 Jahre alt)
    if is_old_building:
        max_sanierung_investment = 200000  # Maximale Bemessungsgrundlage
        eligible_amount = min(total_investment, max_sanierung_investment)
        
        # 20% über 3 Jahre verteilt: 7%, 7%, 6%
        year1_benefit = eligible_amount * 0.07
        year2_benefit = eligible_amount * 0.07
        year3_benefit = eligible_amount * 0.06
        total_sanierung_benefit = year1_benefit + year2_benefit + year3_benefit
        
        tax_benefits['energetische_sanierung'] = {
            'eligible_amount': eligible_amount,
            'year1_benefit': year1_benefit,
            'year2_benefit': year2_benefit,
            'year3_benefit': year3_benefit,
            'total_benefit_3years': total_sanierung_benefit,
            'description': 'Steuerermäßigung für energetische Sanierung',
            'paragraph': '§35c EStG',
            'requirements': [
                'Gebäude älter als 10 Jahre',
                'Selbstgenutzte Immobilie',
                'Bescheinigung des Fachbetriebs',
                'Antrag binnen 4 Monaten nach Abschluss'
            ],
            'timeline': {
                'jahr_1': f"{year1_benefit:,.2f}€ (7% Steuerermäßigung)",
                'jahr_2': f"{year2_benefit:,.2f}€ (7% Steuerermäßigung)",
                'jahr_3': f"{year3_benefit:,.2f}€ (6% Steuerermäßigung)"
            }
        }
        
        # Kombination mit Handwerkerleistung
        # Wichtig: Keine Doppelförderung! Entweder/Oder
        tax_benefits['combination_note'] = (
            "⚠️ WICHTIG: §35c (energetische Sanierung) schließt §35a (Handwerkerleistungen) aus! "
            "Wählen Sie die für Sie günstigere Option."
        )
        
        # Vergleich welche Option besser ist
        if total_sanierung_benefit > handwerker_benefit:
            tax_benefits['recommendation'] = {
                'option': 'energetische_sanierung',
                'benefit': total_sanierung_benefit,
                'reason': f'§35c bringt {total_sanierung_benefit - handwerker_benefit:,.2f}€ mehr Vorteil über 3 Jahre'
            }
            tax_benefits['total_benefit'] = total_sanierung_benefit
        else:
            tax_benefits['recommendation'] = {
                'option': 'handwerkerleistungen',
                'benefit': handwerker_benefit,
                'reason': '§35a ist in diesem Fall vorteilhafter (sofortige Erstattung)'
            }
            tax_benefits['total_benefit'] = handwerker_benefit
    else:
        # Nur Handwerkerleistungen möglich
        tax_benefits['energetische_sanierung'] = {
            'eligible': False,
            'reason': f'Gebäude von {building_year} ist noch keine 10 Jahre alt',
            'alternative': 'Nur Handwerkerleistungen (§35a) absetzbar'
        }
        tax_benefits['total_benefit'] = handwerker_benefit
        tax_benefits['recommendation'] = {
            'option': 'handwerkerleistungen',
            'benefit': handwerker_benefit,
            'reason': 'Einzige verfügbare Option für neuere Gebäude'
        }
    
    # Netto-Investition nach allen Vorteilen
    # Annahme: BEG-Förderung wurde bereits abgezogen
    tax_benefits['net_investment_after_tax'] = total_investment - tax_benefits['total_benefit']
    
    # Kombination mit BEG-Förderung
    tax_benefits['important_notes'] = [
        "💰 Steuervorteile kommen ZUSÄTZLICH zur BEG-Förderung",
        "📄 Fachunternehmererklärung erforderlich",
        "⏰ Antrag nach Fertigstellung stellen",
        "🏦 Nur bei Eigennutzung (nicht Vermietung)"
    ]
    
    return tax_benefits


# ============================================================================
# FEATURE 3.2: LAUTSTÄRKE-ANALYSE & AUFSTELLORT (TA LÄRM)
# ============================================================================

def calculate_noise_analysis(
    heatpump_data: Dict[str, Any],
    building_data: Dict[str, Any],
    neighbor_distance_m: float = 5.0
) -> Dict[str, Any]:
    """
    Prüft Schallimmission nach TA Lärm
    
    Parameter:
    - heatpump_data: WP-Daten (noise_level, manufacturer)
    - building_data: Gebäudetyp
    - neighbor_distance_m: Abstand zu Nachbargrundstücken
    
    Returns:
    - Dict mit Lautstärke-Analyse und Empfehlungen
    """
    
    # Schallleistungspegel der WP (dB(A))
    noise_level_wp = heatpump_data.get('noise_level', 45)  # Typisch 35-65 dB(A)
    
    # TA Lärm Grenzwerte (Immissionsrichtwerte in dB(A))
    area_limits = {
        'Industriegebiet': {'day': 70, 'night': 70},
        'Gewerbegebiet': {'day': 65, 'night': 50},
        'Mischgebiet': {'day': 60, 'night': 45},
        'Wohngebiet': {'day': 55, 'night': 40},
        'reines_Wohngebiet': {'day': 50, 'night': 35},
        'Kurgebiet': {'day': 45, 'night': 35}
    }
    
    # Gebietstypbestimmung (vereinfacht)
    building_type = building_data.get('type', 'Einfamilienhaus')
    if 'Mehrfamilienhaus' in building_type:
        area_type = 'Wohngebiet'
    else:
        area_type = 'reines_Wohngebiet'  # Konservative Annahme
    
    limits = area_limits.get(area_type, area_limits['Wohngebiet'])
    
    # Schallausbreitung berechnen
    # Pegelverlust durch Abstand: ΔL = 20 × log10(r2/r1)
    # Referenzabstand meist 1m oder 3m (Herstellerangabe)
    reference_distance = 1.0  # m
    
    # Punktschallquelle: -6 dB pro Abstandsverdopplung
    distance_attenuation = 20 * math.log10(neighbor_distance_m / reference_distance)
    
    # Bodendämpfung (ca. 1-3 dB bei größeren Entfernungen)
    if neighbor_distance_m > 10:
        ground_attenuation = 2.0
    elif neighbor_distance_m > 5:
        ground_attenuation = 1.0
    else:
        ground_attenuation = 0.0
    
    # Luftdämpfung (vernachlässigbar bei kurzen Distanzen)
    air_attenuation = 0.1 * (neighbor_distance_m / 100)
    
    # Gesamtdämpfung
    total_attenuation = distance_attenuation + ground_attenuation + air_attenuation
    
    # Schallimmissionspegel am Nachbargrundstück
    noise_at_neighbor = noise_level_wp - total_attenuation
    
    # Nachtbetrieb: WP läuft nachts (22-6 Uhr)
    # Bewertung gegen Nachtwert
    night_limit = limits['night']
    day_limit = limits['day']
    
    # Compliance-Check
    night_compliant = noise_at_neighbor <= night_limit
    day_compliant = noise_at_neighbor <= day_limit
    
    # Sicherheitszuschlag
    safety_margin_night = night_limit - noise_at_neighbor
    safety_margin_day = day_limit - noise_at_neighbor
    
    # Schallschutzmaßnahmen berechnen
    required_reduction = max(0, noise_at_neighbor - night_limit + 3)  # +3 dB Sicherheit
    
    measures = []
    if required_reduction > 0:
        measures = _get_noise_reduction_measures(required_reduction, neighbor_distance_m)
    
    # Optimaler Aufstellort
    optimal_location = _determine_optimal_location(
        noise_level_wp, neighbor_distance_m, night_limit
    )
    
    return {
        'wp_noise_level_dba': noise_level_wp,
        'area_type': area_type,
        'limits': limits,
        'neighbor_distance_m': neighbor_distance_m,
        'noise_at_neighbor_dba': round(noise_at_neighbor, 1),
        'attenuation': {
            'distance': round(distance_attenuation, 1),
            'ground': round(ground_attenuation, 1),
            'air': round(air_attenuation, 1),
            'total': round(total_attenuation, 1)
        },
        'compliance': {
            'night_compliant': night_compliant,
            'day_compliant': day_compliant,
            'safety_margin_night_db': round(safety_margin_night, 1),
            'safety_margin_day_db': round(safety_margin_day, 1)
        },
        'assessment': _assess_noise_situation(night_compliant, safety_margin_night),
        'required_reduction_db': round(required_reduction, 1) if required_reduction > 0 else 0,
        'measures': measures,
        'optimal_location': optimal_location,
        'additional_notes': [
            "TA Lärm gilt für Außenaufstellung",
            "Innenaufstellung hat ggf. andere Anforderungen (Körperschall)",
            "Messungen sollten von Fachbetrieb durchgeführt werden",
            "Nachbarschaftliche Einigung oft hilfreich"
        ]
    }


def _get_noise_reduction_measures(required_db: float, distance: float) -> List[Dict[str, Any]]:
    """Gibt Schallschutzmaßnahmen zurück"""
    measures = []
    
    if required_db <= 3:
        measures.append({
            'measure': 'Schallschutzhaube',
            'reduction_db': 3,
            'cost_eur': '500-1.500',
            'description': 'Umhüllung der Außeneinheit'
        })
    
    if required_db > 3 and required_db <= 6:
        measures.append({
            'measure': 'Schallschutzwand',
            'reduction_db': 5,
            'cost_eur': '1.000-3.000',
            'description': f'L-förmige Wand, Höhe 2m, {distance + 0.5:.1f}m Abstand zur WP'
        })
    
    if required_db > 6:
        measures.append({
            'measure': 'Schallgedämmtes Gehäuse + Fundament-Entkopplung',
            'reduction_db': 10,
            'cost_eur': '2.000-5.000',
            'description': 'Professionelle Schalldämmung mit schwingungsgedämpftem Fundament'
        })
    
    # Immer verfügbar:
    measures.append({
        'measure': 'Nachtabsenkung / Flüstermodus',
        'reduction_db': 5,
        'cost_eur': '0 (Software)',
        'description': 'WP-Leistung nachts reduzieren, mit Pufferspeicher kombinieren'
    })
    
    return measures


def _determine_optimal_location(noise_level: float, distance: float, limit: float) -> Dict[str, Any]:
    """Bestimmt optimalen Aufstellort"""
    
    # Berechne erforderliche Mindestdistanz
    # noise_at_distance = noise_level - 20*log10(distance)
    # Auflösen nach distance: distance = 10^((noise_level - limit) / 20)
    
    min_distance = 10 ** ((noise_level - limit) / 20)
    min_distance = max(min_distance, 3.0)  # Mindestens 3m aus praktischen Gründen
    
    recommendations = []
    
    if distance < min_distance:
        recommendations.append(
            f"⚠️ Aktueller Abstand ({distance}m) zu gering - mind. {min_distance:.1f}m empfohlen"
        )
    else:
        recommendations.append(
            f"✅ Aktueller Abstand ({distance}m) ist ausreichend (mind. {min_distance:.1f}m)"
        )
    
    recommendations.extend([
        "Aufstellort auf Hausseite OHNE Schlafzimmer bevorzugen",
        "Nicht direkt vor Fenster/Terrasse des Nachbarn",
        "Mindestens 3m Abstand zur Grundstücksgrenze",
        "Weiche Unterlage (Gummipuffer) gegen Körperschall",
        "Freier Luftstrom - nicht eingemauert"
    ])
    
    return {
        'min_distance_required_m': round(min_distance, 1),
        'current_distance_adequate': distance >= min_distance,
        'recommendations': recommendations
    }


def _assess_noise_situation(compliant: bool, margin: float) -> str:
    """Bewertet Lärmsituation"""
    if not compliant:
        return "❌ KRITISCH - Grenzwerte überschritten, Maßnahmen erforderlich"
    elif margin >= 5:
        return "✅ UNKRITISCH - Deutlich unter Grenzwerten"
    elif margin >= 2:
        return "⚠️ GRENZWERTIG - Knapp unter Grenzwerten, Maßnahmen empfohlen"
    else:
        return "⚠️ KRITISCH - Sehr knapp an Grenzwerten, Maßnahmen dringend empfohlen"


# ============================================================================
# FEATURE 3.3: JAHRESGANGLINIE & HEIZPROFIL
# ============================================================================

def generate_annual_load_profile(
    building_data: Dict[str, Any],
    heatpump_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Erstellt monatliches Heizprofil über das Jahr
    
    Returns:
    - Dict mit monatlichen Werten und Visualisierungsdaten
    """
    
    heat_load_kw = building_data.get('heat_load_kw', 10)
    outside_temp_design = building_data.get('outside_temp', -12)
    heating_days = building_data.get('heating_days', 220)
    
    # Typische Außentemperaturen pro Monat (Deutschland, Mittelwert)
    monthly_temps = {
        'Januar': -1, 'Februar': 0, 'März': 4, 'April': 9,
        'Mai': 14, 'Juni': 17, 'Juli': 19, 'August': 18,
        'September': 14, 'Oktober': 9, 'November': 4, 'Dezember': 1
    }
    
    # Heiztage pro Monat (vereinfacht)
    monthly_heating_days = {
        'Januar': 31, 'Februar': 28, 'März': 31, 'April': 20,
        'Mai': 10, 'Juni': 0, 'Juli': 0, 'August': 0,
        'September': 5, 'Oktober': 20, 'November': 30, 'Dezember': 31
    }
    
    indoor_temp = building_data.get('desired_temp', 20)
    
    # JAZ-Prognose für Effizienz
    jaz_data = calculate_jaz_prognosis(building_data, heatpump_data)
    jaz = jaz_data['jaz_realistic']
    
    monthly_profile = []
    total_heat_kwh = 0
    total_electricity_kwh = 0
    
    for month, avg_temp in monthly_temps.items():
        heating_days_month = monthly_heating_days[month]
        
        if heating_days_month == 0:
            # Kein Heizbedarf
            heat_demand_kwh = 0
            electricity_kwh = 0
            wp_runtime_hours = 0
        else:
            # Heizlast temperaturabhängig
            # Q = Q_design × (T_innen - T_außen) / (T_innen - T_design)
            temp_ratio = (indoor_temp - avg_temp) / (indoor_temp - outside_temp_design)
            temp_ratio = max(0, min(1, temp_ratio))  # Begrenzen auf 0-1
            
            current_heat_load = heat_load_kw * temp_ratio
            
            # Tägliche Betriebsstunden (vereinfacht: 12-18h je nach Last)
            if temp_ratio > 0.8:  # Sehr kalt
                daily_runtime = 18
            elif temp_ratio > 0.5:  # Kalt
                daily_runtime = 14
            elif temp_ratio > 0.3:  # Mild
                daily_runtime = 10
            else:  # Übergangszeit
                daily_runtime = 6
            
            wp_runtime_hours = daily_runtime * heating_days_month
            heat_demand_kwh = current_heat_load * wp_runtime_hours
            electricity_kwh = heat_demand_kwh / jaz
        
        total_heat_kwh += heat_demand_kwh
        total_electricity_kwh += electricity_kwh
        
        monthly_profile.append({
            'month': month,
            'avg_temp_c': avg_temp,
            'heating_days': heating_days_month,
            'heat_demand_kwh': round(heat_demand_kwh, 0),
            'electricity_consumption_kwh': round(electricity_kwh, 0),
            'wp_runtime_hours': round(wp_runtime_hours, 0),
            'temp_ratio': round(temp_ratio, 2)
        })
    
    # Warmwasserbedarf (ganzjährig)
    hot_water_demand = building_data.get('hot_water', 'Mittel')
    hw_kwh_per_person_year = {'Niedrig': 400, 'Mittel': 600, 'Hoch': 800}.get(hot_water_demand, 600)
    
    # Personen schätzen (2,5 Personen pro 100m²)
    area = building_data.get('area', 150)
    persons = max(1, area / 100 * 2.5)
    
    annual_hw_kwh = hw_kwh_per_person_year * persons
    monthly_hw_kwh = annual_hw_kwh / 12
    monthly_hw_electricity = monthly_hw_kwh / 3.0  # COP für Warmwasser ~3.0
    
    # Zu jedem Monat Warmwasser addieren
    for month_data in monthly_profile:
        month_data['hot_water_kwh'] = round(monthly_hw_kwh, 0)
        month_data['hot_water_electricity_kwh'] = round(monthly_hw_electricity, 0)
        month_data['total_electricity_kwh'] = round(
            month_data['electricity_consumption_kwh'] + month_data['hot_water_electricity_kwh'], 0
        )
    
    total_electricity_kwh += annual_hw_kwh / 3.0
    
    return {
        'monthly_profile': monthly_profile,
        'annual_summary': {
            'total_heat_demand_kwh': round(total_heat_kwh, 0),
            'total_hot_water_kwh': round(annual_hw_kwh, 0),
            'total_heat_and_hw_kwh': round(total_heat_kwh + annual_hw_kwh, 0),
            'total_electricity_kwh': round(total_electricity_kwh, 0),
            'average_jaz': jaz,
            'heating_days_per_year': sum(m['heating_days'] for m in monthly_profile)
        },
        'peak_month': max(monthly_profile, key=lambda x: x['heat_demand_kwh']),
        'lowest_month': min(monthly_profile, key=lambda x: x['heat_demand_kwh']),
        'interpretation': {
            'heating_season': 'Oktober bis April',
            'peak_consumption': f"Januar/Februar ({max(monthly_profile, key=lambda x: x['heat_demand_kwh'])['month']})",
            'summer_operation': 'Nur Warmwasser (Juni-August)'
        }
    }


# ============================================================================
# FEATURE 4.1: SMART-GRID-READY INTEGRATION
# ============================================================================

def calculate_smart_grid_benefits(
    building_data: Dict[str, Any],
    heatpump_data: Dict[str, Any],
    pv_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Berechnet Mehrwert von SG-Ready Funktion
    
    SG-Ready Betriebsmodi:
    - Modus 1: Zwangsabschaltung (Netz-Notfall)
    - Modus 2: Normalbetrieb
    - Modus 3: Einschaltempfehlung (PV-Überschuss / günstiger Strom)
    - Modus 4: Einschaltbefehl (maximale Leistung)
    
    Returns:
    - Dict mit Einsparpotenzialen
    """
    
    # Jahresganglinie laden
    load_profile = generate_annual_load_profile(building_data, heatpump_data)
    total_electricity_kwh = load_profile['annual_summary']['total_electricity_kwh']
    
    # Standard-Strompreis
    electricity_price_kwh = 0.32  # €/kWh
    
    # Szenarien
    scenarios = {}
    
    # Szenario 1: Ohne Smart-Grid (Basis)
    annual_cost_base = total_electricity_kwh * electricity_price_kwh
    
    scenarios['ohne_smart_grid'] = {
        'annual_cost': annual_cost_base,
        'description': 'Konstanter Betrieb nach Heizkurve'
    }
    
    # Szenario 2: Mit PV-Überschuss-Optimierung
    if pv_data:
        pv_production_annual = pv_data.get('annual_production_kwh', 0)
        
        # Annahme: 30% der WP-Last kann in PV-Überschusszeiten verschoben werden
        shiftable_percentage = 0.30
        shiftable_kwh = total_electricity_kwh * shiftable_percentage
        
        # Von dieser kann 60% tatsächlich mit PV gedeckt werden
        pv_covered_kwh = min(shiftable_kwh * 0.6, pv_production_annual * 0.4)
        
        # Einsparung: PV-Strom (0€) vs. Netzbezug (32 Cent)
        savings_pv = pv_covered_kwh * electricity_price_kwh
        
        scenarios['mit_pv_optimierung'] = {
            'annual_cost': annual_cost_base - savings_pv,
            'pv_covered_kwh': round(pv_covered_kwh, 0),
            'savings_eur': round(savings_pv, 2),
            'description': f'{round(pv_covered_kwh / total_electricity_kwh * 100, 1)}% Eigenverbrauch'
        }
    
    # Szenario 3: Mit dynamischem Stromtarif
    # Annahme: Durchschnittlich 20% günstigere Zeiten nutzen
    dynamic_tariff_discount = 0.20
    optimizable_load = total_electricity_kwh * 0.50  # 50% der Last ist zeitlich flexibel
    
    savings_dynamic = optimizable_load * electricity_price_kwh * dynamic_tariff_discount
    
    scenarios['mit_dynamischem_tarif'] = {
        'annual_cost': annual_cost_base - savings_dynamic,
        'savings_eur': round(savings_dynamic, 2),
        'description': 'Lastverschiebung in günstige Tarifzeiten'
    }
    
    # Szenario 4: Kombination PV + Dynamischer Tarif
    if pv_data:
        total_savings_combined = savings_pv + savings_dynamic * 0.7  # 70% des dynamischen Potenzials zusätzlich
        scenarios['kombiniert'] = {
            'annual_cost': annual_cost_base - total_savings_combined,
            'savings_eur': round(total_savings_combined, 2),
            'description': 'Optimale Kombination aller Funktionen'
        }
    
    # § 14a EnWG Bonus (separates Feature 4.2, hier nur erwähnt)
    grid_bonus_annual = 130  # Durchschnitt
    
    # Investitionskosten Smart-Grid-Ready
    sg_ready_cost = 0  # Meist Standard bei neuen WP
    if 'smart_control' in heatpump_data and not heatpump_data['smart_control']:
        sg_ready_cost = 500  # Nachrüstung
    
    # Best-Case Szenario
    best_scenario = max(scenarios.items(), key=lambda x: annual_cost_base - x[1]['annual_cost'])
    
    return {
        'scenarios': scenarios,
        'base_annual_cost': round(annual_cost_base, 2),
        'best_scenario': {
            'name': best_scenario[0],
            'annual_cost': round(best_scenario[1]['annual_cost'], 2),
            'annual_savings': round(annual_cost_base - best_scenario[1]['annual_cost'], 2)
        },
        'sg_ready_cost': sg_ready_cost,
        'grid_bonus_annual': grid_bonus_annual,
        'total_benefit_first_year': round(
            (annual_cost_base - best_scenario[1]['annual_cost']) + grid_bonus_annual - sg_ready_cost, 2
        ),
        'payback_years': round(sg_ready_cost / ((annual_cost_base - best_scenario[1]['annual_cost']) + grid_bonus_annual), 1) if sg_ready_cost > 0 else 0,
        'requirements': [
            'Smart-Grid-Ready Wärmepumpe (SG-Ready Label)',
            'Steuerungsgerät / Energy-Management-System',
            'Internetanbindung für Preissignale',
            'Pufferspeicher empfohlen (min. 500L)'
        ],
        'recommendations': _get_smart_grid_recommendations(pv_data, scenarios)
    }


def _get_smart_grid_recommendations(pv_data: Dict, scenarios: Dict) -> List[str]:
    """Gibt Smart-Grid Empfehlungen"""
    recs = []
    
    if pv_data:
        recs.append("✅ PV-Anlage vorhanden - Smart-Grid-Ready sehr sinnvoll für Eigenverbrauchsoptimierung")
        recs.append("💡 PV-Überschuss-Steuerung installieren (ca. 300-800€)")
    else:
        recs.append("⚠️ Ohne PV-Anlage ist Nutzen begrenzt - dynamischer Tarif empfohlen")
    
    recs.extend([
        "🔌 Dynamischen Stromtarif wählen (z.B. Tibber, aWATTar)",
        "📱 Home-Energy-Management-System einplanen",
        "🔋 Pufferspeicher mind. 500L für Lastverschiebung"
    ])
    
    return recs


# ============================================================================
# FEATURE 4.2: NETZDIENLICHKEIT & § 14a EnWG BONUS
# ============================================================================

def calculate_grid_service_bonus(
    heatpump_data: Dict[str, Any],
    building_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Berechnet § 14a EnWG Bonus für steuerbare Verbrauchseinrichtungen
    
    § 14a EnWG: Netzbetreiber kann WP bei Netzüberlastung dimmen,
    dafür gibt es reduzierte Netzentgelte (110-190€/Jahr je nach Netzbetreiber)
    
    Returns:
    - Dict mit Bonus-Berechnung und Anforderungen
    """
    
    wp_power_kw = heatpump_data.get('heating_power', 10)
    
    # Typische Bonushöhen nach § 14a EnWG (ab 2024)
    # Variante 1: Prozentual (60% Rabatt auf Netzentgelt)
    # Variante 2: Pauschalbetrag
    
    # Netzentgelt typisch: 6-8 Cent/kWh
    network_charge_kwh = 0.07  # €/kWh
    
    # Jahresverbrauch WP
    load_profile = generate_annual_load_profile(building_data, heatpump_data)
    annual_consumption_kwh = load_profile['annual_summary']['total_electricity_kwh']
    
    # Variante 1: Prozentrabatt
    network_cost_full = annual_consumption_kwh * network_charge_kwh
    discount_percentage = 0.60  # 60% Rabatt
    bonus_prozentual = network_cost_full * discount_percentage
    
    # Variante 2: Pauschale (abhängig von Anschlussleistung)
    if wp_power_kw <= 7:
        bonus_pauschal = 110
    elif wp_power_kw <= 11:
        bonus_pauschal = 150
    elif wp_power_kw <= 15:
        bonus_pauschal = 190
    else:
        bonus_pauschal = 190 + (wp_power_kw - 15) * 10
    
    # Netzbetreiber wählt wirtschaftlich günstigere Variante (für sich)
    # → Meist Pauschale für kleinere WP, Prozent für größere
    if bonus_pauschal < bonus_prozentual:
        bonus_variant = 'Pauschale'
        bonus_annual = bonus_pauschal
    else:
        bonus_variant = 'Prozentual'
        bonus_annual = bonus_prozentual
    
    # Anforderungen § 14a EnWG
    requirements_met = {
        'steuerbare_verbrauchseinrichtung': True,  # WP ist per Definition steuerbar
        'anmeldung_beim_netzbetreiber': None,  # Muss vom Nutzer gemacht werden
        'smart_meter': None,  # Kann erforderlich sein
        'technische_einrichtung': 'smart_grid_ready' in str(heatpump_data).lower()
    }
    
    requirements_met_count = sum(1 for v in requirements_met.values() if v is True)
    requirements_total = 4
    
    # Verpflichtung: Netzbetreiber kann WP dimmen
    # Maximale Abregelung: 0% (nur Dimmen, kein komplettes Abschalten von Heizung)
    dimming_details = {
        'max_dimming_percentage': 100,  # Kann bis auf 0% gedimmt werden (nur Außeneinheit)
        'max_dimming_duration_hours': 2,  # Pro Steuereingriff max. 2 Stunden
        'max_interventions_per_day': 3,  # Selten, nur bei Netzengpässen
        'notification': 'Keine Vorankündigung erforderlich',
        'comfort_impact': 'Minimal (Pufferspeicher überbrückt)'
    }
    
    # Amortisation zusätzlicher Smart-Meter-Kosten
    smart_meter_cost_annual = 20  # €/Jahr (Differenz zu Ferraris-Zähler)
    net_benefit_annual = bonus_annual - smart_meter_cost_annual
    
    return {
        'eligible': requirements_met['steuerbare_verbrauchseinrichtung'],
        'bonus_annual_eur': round(bonus_annual, 2),
        'bonus_variant': bonus_variant,
        'alternative_bonus_prozentual': round(bonus_prozentual, 2),
        'alternative_bonus_pauschal': round(bonus_pauschal, 2),
        'requirements': requirements_met,
        'requirements_met_percentage': round(requirements_met_count / requirements_total * 100, 0),
        'dimming_details': dimming_details,
        'net_benefit_annual': round(net_benefit_annual, 2),
        'benefit_20_years': round(net_benefit_annual * 20, 2),
        'application_process': [
            '1. Wärmepumpe beim Netzbetreiber anmelden',
            '2. Formular "Steuerbare Verbrauchseinrichtung" ausfüllen',
            '3. Technische Spezifikation der WP beifügen',
            '4. Smart Meter Gateway installieren lassen (falls erforderlich)',
            '5. Reduzierte Netzentgelte werden automatisch verrechnet'
        ],
        'important_notes': [
            "§ 14a EnWG ist seit 2024 verpflichtend für neue WP-Anlagen",
            "Bonus variiert stark nach Netzbetreiber (110-190€ typisch)",
            "Pufferspeicher empfohlen zur Überbrückung von Abregelungen",
            "Comfort-Einbußen sind minimal bei guter Planung"
        ]
    }


# ============================================================================
# FEATURE 4.3: HYBRID-HEIZUNG (BIVALENT)
# ============================================================================

def compare_hybrid_heating(
    building_data: Dict[str, Any],
    heatpump_data: Dict[str, Any],
    backup_system: str = 'Gaskessel'
) -> Dict[str, Any]:
    """
    Vergleicht Hybrid-System (WP + Backup) mit reiner WP
    
    Bivalenzpunkt: Temperatur, ab der Backup-System zugeschaltet wird
    
    Parameter:
    - building_data: Gebäudedaten
    - heatpump_data: WP-Daten
    - backup_system: 'Gaskessel', 'Ölkessel', 'Elektroheizstab'
    
    Returns:
    - Dict mit Wirtschaftlichkeitsvergleich
    """
    
    heat_load_kw = building_data.get('heat_load_kw', 10)
    outside_temp_design = building_data.get('outside_temp', -12)
    wp_power_kw = heatpump_data.get('heating_power', 8)
    
    # Bivalenzpunkt berechnen
    # Beispiel: WP liefert 8 kW bei -12°C Design, aber nur 6 kW bei -7°C
    # → Bivalenzpunkt bei ca. -5°C wenn WP 60% der Last decken soll
    
    # Vereinfacht: Bivalenzpunkt so wählen, dass WP 95% der Jahresarbeit leistet
    bivalence_temp_95_percent = -5  # °C (typischer Wert)
    bivalence_temp_monovalent = -10  # °C (WP alleine bis -10°C)
    
    # Jahresganglinie
    load_profile = generate_annual_load_profile(building_data, heatpump_data)
    
    # Szenario 1: Reine Wärmepumpe (monovalent)
    wp_size_monovalent = heat_load_kw * 1.1  # 10% Reserve
    wp_price_monovalent = heatpump_data.get('price', 15000) * (wp_size_monovalent / wp_power_kw)
    
    electricity_kwh_monovalent = load_profile['annual_summary']['total_electricity_kwh']
    electricity_price = 0.32  # €/kWh
    operating_cost_monovalent = electricity_kwh_monovalent * electricity_price
    
    # Szenario 2: Hybrid (bivalent-parallel)
    # WP kleiner dimensioniert (für 60-70% der Heizlast)
    wp_size_hybrid = heat_load_kw * 0.65
    wp_price_hybrid = heatpump_data.get('price', 15000) * (wp_size_hybrid / wp_power_kw)
    
    # Backup-System Kosten
    backup_costs = {
        'Gaskessel': {'investment': 5000, 'fuel_price_kwh': 0.10, 'efficiency': 0.95},
        'Ölkessel': {'investment': 6000, 'fuel_price_kwh': 0.11, 'efficiency': 0.90},
        'Elektroheizstab': {'investment': 800, 'fuel_price_kwh': 0.32, 'efficiency': 1.0}
    }
    
    backup_data = backup_costs.get(backup_system, backup_costs['Gaskessel'])
    
    # Anteil Backup-System: Bei Temp < Bivalenzpunkt
    # Vereinfacht: Backup liefert 5% der Jahresarbeit
    backup_percentage = 0.05
    wp_percentage_hybrid = 0.95
    
    total_heat_demand = load_profile['annual_summary']['total_heat_and_hw_kwh']
    
    heat_by_wp_hybrid = total_heat_demand * wp_percentage_hybrid
    heat_by_backup = total_heat_demand * backup_percentage
    
    # WP-Stromverbrauch (nur 95% der Last)
    jaz_data = calculate_jaz_prognosis(building_data, heatpump_data)
    jaz = jaz_data['jaz_realistic']
    
    electricity_kwh_hybrid = heat_by_wp_hybrid / jaz
    
    # Backup-Brennstoffverbrauch
    fuel_kwh_backup = heat_by_backup / backup_data['efficiency']
    fuel_cost_backup = fuel_kwh_backup * backup_data['fuel_price_kwh']
    
    # Betriebskosten Hybrid
    operating_cost_hybrid = electricity_kwh_hybrid * electricity_price + fuel_cost_backup
    
    # Investitionskosten
    investment_monovalent = wp_price_monovalent + 3000  # Installation
    investment_hybrid = wp_price_hybrid + backup_data['investment'] + 3500  # Installation beider Systeme
    
    # Wirtschaftlichkeit
    annual_savings_hybrid = operating_cost_monovalent - operating_cost_hybrid
    additional_investment_hybrid = investment_hybrid - investment_monovalent
    
    if annual_savings_hybrid > 0:
        payback_years_hybrid = additional_investment_hybrid / annual_savings_hybrid
    else:
        payback_years_hybrid = float('inf')
    
    # 20-Jahres-Betrachtung
    total_cost_20y_monovalent = investment_monovalent + operating_cost_monovalent * 20
    total_cost_20y_hybrid = investment_hybrid + operating_cost_hybrid * 20
    
    return {
        'bivalence_point_celsius': bivalence_temp_95_percent,
        'monovalent_system': {
            'wp_size_kw': round(wp_size_monovalent, 1),
            'investment_eur': round(investment_monovalent, 2),
            'annual_operating_cost_eur': round(operating_cost_monovalent, 2),
            'total_cost_20y_eur': round(total_cost_20y_monovalent, 2),
            'electricity_consumption_kwh': round(electricity_kwh_monovalent, 0)
        },
        'hybrid_system': {
            'wp_size_kw': round(wp_size_hybrid, 1),
            'backup_system': backup_system,
            'investment_eur': round(investment_hybrid, 2),
            'annual_operating_cost_eur': round(operating_cost_hybrid, 2),
            'total_cost_20y_eur': round(total_cost_20y_hybrid, 2),
            'electricity_consumption_kwh': round(electricity_kwh_hybrid, 0),
            'backup_fuel_kwh': round(fuel_kwh_backup, 0),
            'backup_fuel_cost_eur': round(fuel_cost_backup, 2),
            'wp_coverage_percentage': wp_percentage_hybrid * 100,
            'backup_coverage_percentage': backup_percentage * 100
        },
        'comparison': {
            'additional_investment_hybrid_eur': round(additional_investment_hybrid, 2),
            'annual_savings_hybrid_eur': round(annual_savings_hybrid, 2),
            'payback_years': round(payback_years_hybrid, 1) if payback_years_hybrid != float('inf') else 'Nicht wirtschaftlich',
            'total_savings_20y_eur': round(total_cost_20y_monovalent - total_cost_20y_hybrid, 2),
            'recommendation': _get_hybrid_recommendation(
                payback_years_hybrid, additional_investment_hybrid, backup_system
            )
        },
        'advantages_hybrid': [
            f'Kleinere WP ausreichend ({wp_size_hybrid:.1f} kW statt {wp_size_monovalent:.1f} kW)',
            'Redundanz bei WP-Ausfall',
            f'Nutzt günstigen {backup_system}-Brennstoff bei Extremkälte',
            'Geringere Stromspitzen'
        ],
        'disadvantages_hybrid': [
            f'Höhere Investition (+{additional_investment_hybrid:.0f}€)',
            f'Zwei Systeme → doppelter Wartungsaufwand',
            f'{backup_system} nutzt fossile Energie',
            'Komplexere Steuerung erforderlich'
        ]
    }


def _get_hybrid_recommendation(payback_years: float, additional_invest: float, backup: str) -> str:
    """Empfehlung für Hybrid-System"""
    if payback_years < 10 and 'Gas' in backup:
        return f"✅ SINNVOLL - Amortisation in {payback_years:.1f} Jahren, bestehender Gasanschluss kann genutzt werden"
    elif payback_years < 15:
        return f"⚠️ GRENZWERTIG - Amortisation {payback_years:.1f} Jahre, nur bei bestehendem {backup} sinnvoll"
    elif additional_invest < 3000:
        return "⚠️ ÜBERDENKEN - Geringe Mehrkosten, aber Wartungsaufwand für zweites System"
    else:
        return f"❌ NICHT EMPFOHLEN - Zu lange Amortisation, monovalente WP wirtschaftlicher"


# ============================================================================
# FEATURE 6.1: LEBENSZYKLUS-CO2-BILANZ
# ============================================================================

def calculate_lifecycle_co2(
    building_data: Dict[str, Any],
    heatpump_data: Dict[str, Any],
    old_system: str = 'Gasheizung',
    electricity_co2_factor: float = 0.420  # kg CO2/kWh (Deutschland 2024)
) -> Dict[str, Any]:
    """
    Berechnet vollständige CO2-Bilanz über 20 Jahre
    
    Phasen:
    1. Herstellung (embodied carbon)
    2. Betrieb (operational carbon)
    3. Entsorgung / Recycling
    
    Returns:
    - Dict mit CO2-Bilanz und Break-Even-Analyse
    """
    
    # Phase 1: Herstellung
    # Wärmepumpe: ca. 1.500-2.500 kg CO2 (je nach Größe)
    wp_power_kw = heatpump_data.get('heating_power', 10)
    co2_manufacturing_wp = 150 * wp_power_kw  # kg CO2 (Schätzung: 150 kg/kW)
    
    # Alte Heizung (Referenz)
    co2_manufacturing_old = {
        'Gasheizung': 800,  # kg CO2
        'Ölheizung': 900,
        'Elektroheizung': 300,
        'Nachtspeicher': 500
    }.get(old_system, 800)
    
    # Phase 2: Betrieb (20 Jahre)
    load_profile = generate_annual_load_profile(building_data, heatpump_data)
    annual_heat_demand_kwh = load_profile['annual_summary']['total_heat_and_hw_kwh']
    
    # WP Betrieb
    jaz_data = calculate_jaz_prognosis(building_data, heatpump_data)
    jaz = jaz_data['jaz_realistic']
    
    annual_electricity_kwh_wp = annual_heat_demand_kwh / jaz
    
    # CO2-Faktor Strom sinkt über die Jahre (Energiewende)
    # Annahme: -3% pro Jahr
    co2_operation_wp_20y = 0
    for year in range(20):
        year_co2_factor = electricity_co2_factor * (0.97 ** year)
        co2_operation_wp_20y += annual_electricity_kwh_wp * year_co2_factor
    
    # Alte Heizung Betrieb
    old_system_efficiency = {
        'Gasheizung': 0.90,
        'Ölheizung': 0.85,
        'Elektroheizung': 0.95,
        'Nachtspeicher': 0.90
    }.get(old_system, 0.90)
    
    old_system_co2_factor = {
        'Gasheizung': 0.201,  # kg CO2/kWh
        'Ölheizung': 0.266,
        'Elektroheizung': electricity_co2_factor,
        'Nachtspeicher': electricity_co2_factor
    }.get(old_system, 0.201)
    
    annual_fuel_kwh_old = annual_heat_demand_kwh / old_system_efficiency
    co2_operation_old_20y = annual_fuel_kwh_old * old_system_co2_factor * 20
    
    # Phase 3: Entsorgung
    # WP: ca. 5% der Herstellungs-Emissionen (Recycling-Gutschrift: -10%)
    co2_disposal_wp = co2_manufacturing_wp * 0.05 - co2_manufacturing_wp * 0.10
    
    co2_disposal_old = co2_manufacturing_old * 0.05
    
    # Gesamt-Bilanz
    total_co2_wp = co2_manufacturing_wp + co2_operation_wp_20y + co2_disposal_wp
    total_co2_old = co2_manufacturing_old + co2_operation_old_20y + co2_disposal_old
    
    co2_savings_20y = total_co2_old - total_co2_wp
    co2_savings_annual = co2_savings_20y / 20
    
    # Break-Even Jahr
    # Jahr, in dem kumulierte WP-CO2 < kumulierte alte Heizung CO2
    break_even_year = None
    cumulative_wp = co2_manufacturing_wp
    cumulative_old = co2_manufacturing_old
    
    for year in range(1, 21):
        year_co2_factor = electricity_co2_factor * (0.97 ** (year - 1))
        cumulative_wp += annual_electricity_kwh_wp * year_co2_factor
        cumulative_old += annual_fuel_kwh_old * old_system_co2_factor
        
        if cumulative_wp < cumulative_old and break_even_year is None:
            break_even_year = year
            break
    
    return {
        'wärmepumpe': {
            'herstellung_kg_co2': round(co2_manufacturing_wp, 0),
            'betrieb_20y_kg_co2': round(co2_operation_wp_20y, 0),
            'entsorgung_kg_co2': round(co2_disposal_wp, 0),
            'gesamt_20y_kg_co2': round(total_co2_wp, 0),
            'annual_operation_kg_co2': round(co2_operation_wp_20y / 20, 0)
        },
        'alte_heizung': {
            'system': old_system,
            'herstellung_kg_co2': round(co2_manufacturing_old, 0),
            'betrieb_20y_kg_co2': round(co2_operation_old_20y, 0),
            'entsorgung_kg_co2': round(co2_disposal_old, 0),
            'gesamt_20y_kg_co2': round(total_co2_old, 0),
            'annual_operation_kg_co2': round(co2_operation_old_20y / 20, 0)
        },
        'einsparung': {
            'total_20y_kg_co2': round(co2_savings_20y, 0),
            'total_20y_tonnen_co2': round(co2_savings_20y / 1000, 1),
            'annual_kg_co2': round(co2_savings_annual, 0),
            'break_even_year': break_even_year if break_even_year else 'Nie (WP hat höhere Emissionen)',
            'percentage_reduction': round((co2_savings_20y / total_co2_old) * 100, 1) if total_co2_old > 0 else 0
        },
        'interpretation': _interpret_co2_savings(co2_savings_20y, break_even_year),
        'context': [
            f"CO2-Faktor Strom 2024: {electricity_co2_factor} kg/kWh",
            "Prognose: Strom-CO2 sinkt -3%/Jahr (Energiewende)",
            "WP-Vorteil steigt mit grünerem Strommix",
            f"Äquivalent: {round(co2_savings_20y / 1000 / 20 * 12, 1)} Langstreckenflüge pro Jahr vermieden"
        ]
    }


def _interpret_co2_savings(savings_kg: float, break_even_year: int) -> str:
    """Interpretiert CO2-Einsparungen"""
    if break_even_year is None or break_even_year > 20:
        return "❌ WP hat höhere Lebenszyklus-Emissionen - Strom-CO2-Faktor zu hoch"
    elif break_even_year <= 2:
        return f"✅ HERVORRAGEND - Break-Even nach {break_even_year} Jahren, massive CO2-Einsparung ({savings_kg/1000:.1f} t)"
    elif break_even_year <= 5:
        return f"✅ SEHR GUT - Break-Even nach {break_even_year} Jahren, deutliche CO2-Reduktion ({savings_kg/1000:.1f} t)"
    elif break_even_year <= 10:
        return f"⚠️ AKZEPTABEL - Break-Even nach {break_even_year} Jahren, moderate Einsparung ({savings_kg/1000:.1f} t)"
    else:
        return f"⚠️ GRENZWERTIG - Break-Even erst nach {break_even_year} Jahren"


# ============================================================================
# FEATURE 6.2: KÄLTEMITTEL-VERGLEICH
# ============================================================================

def compare_refrigerants(
    heatpump_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Vergleicht Kältemittel nach GWP und F-Gas-Verordnung
    
    GWP = Global Warming Potential (CO2-Äquivalent über 100 Jahre)
    
    Returns:
    - Dict mit Kältemittel-Bewertung
    """
    
    current_refrigerant = heatpump_data.get('refrigerant', 'R32')
    
    # Kältemittel-Datenbank
    refrigerants_db = {
        'R32': {
            'gwp': 675,
            'name': 'Difluormethan',
            'status': 'Aktueller Standard',
            'f_gas_compliant_until': 2030,
            'safety_class': 'A2L (schwach brennbar)',
            'efficiency': 'Sehr gut',
            'availability': 'Sehr gut',
            'cost_factor': 1.0
        },
        'R290': {
            'gwp': 3,
            'name': 'Propan',
            'status': 'Zukunftssicher (natürlich)',
            'f_gas_compliant_until': 9999,
            'safety_class': 'A3 (brennbar)',
            'efficiency': 'Hervorragend',
            'availability': 'Gut',
            'cost_factor': 1.1
        },
        'R410A': {
            'gwp': 2088,
            'name': 'Gemisch (R32+R125)',
            'status': 'Auslaufmodell',
            'f_gas_compliant_until': 2025,
            'safety_class': 'A1 (nicht brennbar)',
            'efficiency': 'Gut',
            'availability': 'Abnehmend',
            'cost_factor': 1.3
        },
        'R454C': {
            'gwp': 148,
            'name': 'R32/R1234yf-Gemisch',
            'status': 'Neu (F-Gas-konform)',
            'f_gas_compliant_until': 2035,
            'safety_class': 'A2L (schwach brennbar)',
            'efficiency': 'Sehr gut',
            'availability': 'Mittel',
            'cost_factor': 1.2
        },
        'R1234yf': {
            'gwp': 4,
            'name': 'Tetrafluorpropen',
            'status': 'Zukunftssicher (synthetisch)',
            'f_gas_compliant_until': 2035,
            'safety_class': 'A2L (schwach brennbar)',
            'efficiency': 'Gut',
            'availability': 'Mittel',
            'cost_factor': 1.5
        },
        'R744': {
            'gwp': 1,
            'name': 'CO2 (Kohlendioxid)',
            'status': 'Natürlich (Hochdruck)',
            'f_gas_compliant_until': 9999,
            'safety_class': 'A1 (nicht brennbar)',
            'efficiency': 'Gut (bei spezieller Auslegung)',
            'availability': 'Spezialisiert',
            'cost_factor': 1.4
        }
    }
    
    current_data = refrigerants_db.get(current_refrigerant, refrigerants_db['R32'])
    
    # F-Gas-Verordnung (EU) 517/2014 & Novelle
    # Phase-Down-Plan: GWP-gewichtete Menge wird bis 2030 um 79% reduziert
    # → Hochgwp-Kältemittel werden teurer und knapper
    
    current_year = 2024
    years_until_restriction = current_data['f_gas_compliant_until'] - current_year
    
    # CO2-Äquivalent bei Leckage
    # Typische Füllmenge: 1-3 kg (abhängig von WP-Größe)
    wp_power_kw = heatpump_data.get('heating_power', 10)
    refrigerant_charge_kg = 0.15 * wp_power_kw  # Faustregel: 0.15 kg/kW
    
    # Worst-Case: 100% Leckage (Totalschaden)
    co2_equivalent_total_leak = refrigerant_charge_kg * current_data['gwp']
    
    # Realistisch: 2% Leckage pro Jahr (Verschleiß)
    co2_equivalent_annual_leak = refrigerant_charge_kg * 0.02 * current_data['gwp']
    
    # Vergleich mit Alternativen
    alternatives = []
    for ref_name, ref_data in refrigerants_db.items():
        if ref_name == current_refrigerant:
            continue
        
        # Bewertung
        score = 0
        if ref_data['gwp'] < 150:
            score += 40  # Sehr niedriges GWP
        elif ref_data['gwp'] < 700:
            score += 25
        else:
            score += 10
        
        if ref_data['f_gas_compliant_until'] > 2030:
            score += 30  # Zukunftssicher
        elif ref_data['f_gas_compliant_until'] > 2027:
            score += 15
        
        if ref_data['efficiency'] == 'Hervorragend':
            score += 20
        elif ref_data['efficiency'] == 'Sehr gut':
            score += 15
        else:
            score += 10
        
        if ref_data['cost_factor'] <= 1.1:
            score += 10
        
        alternatives.append({
            'refrigerant': ref_name,
            'gwp': ref_data['gwp'],
            'status': ref_data['status'],
            'score': score,
            'cost_factor': ref_data['cost_factor'],
            **ref_data
        })
    
    # Sortiere nach Score
    alternatives.sort(key=lambda x: x['score'], reverse=True)
    
    return {
        'current_refrigerant': {
            'name': current_refrigerant,
            'full_name': current_data['name'],
            'gwp': current_data['gwp'],
            'status': current_data['status'],
            'f_gas_compliant_until': current_data['f_gas_compliant_until'],
            'years_until_restriction': years_until_restriction,
            'safety_class': current_data['safety_class'],
            'refrigerant_charge_kg': round(refrigerant_charge_kg, 2),
            'co2_equivalent_total_leak_kg': round(co2_equivalent_total_leak, 0),
            'co2_equivalent_annual_leak_kg': round(co2_equivalent_annual_leak, 1)
        },
        'assessment': _assess_refrigerant(current_data, years_until_restriction),
        'alternatives': alternatives[:3],  # Top 3
        'future_proofing': {
            'recommendation': alternatives[0]['refrigerant'] if alternatives else current_refrigerant,
            'reason': f"Niedrigstes GWP ({alternatives[0]['gwp']}) und {alternatives[0]['status']}" if alternatives else "Keine Alternative gefunden",
            'upgrade_possible': 'Nein - Kältemittelwechsel erfordert neue WP',
            'next_purchase_advice': f"Bei nächster WP {alternatives[0]['refrigerant']} wählen" if alternatives else "Aktuelles Kältemittel beibehalten"
        },
        'f_gas_regulation': {
            'phase_down_schedule': {
                '2024': '100% (Basis)',
                '2027': '45% (Stark reduziert)',
                '2030': '21% (Sehr stark reduziert)',
                '2033': '15% (Minimal)'
            },
            'impact': 'Hochgwp-Kältemittel werden ab 2027 deutlich teurer',
            'advice': 'Neuanlagen sollten GWP < 150 nutzen'
        }
    }


def _assess_refrigerant(data: Dict, years_left: int) -> str:
    """Bewertet aktuelles Kältemittel"""
    if data['gwp'] < 10:
        return f"✅ HERVORRAGEND - Natürliches Kältemittel mit minimalem GWP ({data['gwp']})"
    elif data['gwp'] < 150:
        return f"✅ SEHR GUT - F-Gas-konform, niedriges GWP ({data['gwp']})"
    elif data['gwp'] < 700 and years_left > 5:
        return f"⚠️ AKZEPTABEL - Mittleres GWP ({data['gwp']}), noch {years_left} Jahre compliant"
    elif data['gwp'] < 700:
        return f"⚠️ GRENZWERTIG - Mittleres GWP ({data['gwp']}), nur noch {years_left} Jahre compliant"
    else:
        return f"❌ PROBLEMATISCH - Hohes GWP ({data['gwp']}), Auslaufmodell (bis {data['f_gas_compliant_until']})"


# ============================================================================
# FEATURE 8.1: WARTUNGSPLAN (20 JAHRE)
# ============================================================================

def calculate_maintenance_schedule(
    heatpump_data: Dict[str, Any],
    building_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Erstellt detaillierten 20-Jahres-Wartungsplan
    
    Returns:
    - Dict mit Wartungsintervallen und Kosten
    """
    
    wp_power_kw = heatpump_data.get('heating_power', 10)
    
    # Wartungskomponenten und Intervalle
    maintenance_items = {
        'Jährliche Inspektion': {
            'interval_years': 1,
            'cost_eur': 150 + wp_power_kw * 10,  # Größenabhängig
            'description': 'Sichtprüfung, Druckkontrolle, Filterreinigung, Funktionstest'
        },
        'Kältemittel nachfüllen': {
            'interval_years': 5,  # Bei Bedarf (Leckage)
            'cost_eur': 200 + refrigerant_charge_cost(heatpump_data.get('refrigerant', 'R32')),
            'description': 'Kältemittelstand prüfen und ggf. nachfüllen',
            'probability': 0.3  # 30% Wahrscheinlichkeit
        },
        'Pufferspeicher-Wartung': {
            'interval_years': 2,
            'cost_eur': 80,
            'description': 'Entlüftung, Anodenwechsel (bei Email-Speichern)'
        },
        'Heizkreispumpe tauschen': {
            'interval_years': 12,
            'cost_eur': 300,
            'description': 'Verschleißteil: Pumpe tauschen'
        },
        'Verdichter-Revision': {
            'interval_years': 15,
            'cost_eur': 1500 + wp_power_kw * 100,
            'description': 'Großer Service: Verdichter überholen'
        },
        'Plattenwärmetauscher reinigen': {
            'interval_years': 10,
            'cost_eur': 400,
            'description': 'Wärmetauscher demontieren und reinigen (Kalkablagerungen)'
        },
        'Elektrik-Check': {
            'interval_years': 5,
            'cost_eur': 120,
            'description': 'Elektrische Verbindungen prüfen, Kontakte reinigen'
        },
        'Außeneinheit-Reinigung': {
            'interval_years': 3,
            'cost_eur': 100,
            'description': 'Lamellen reinigen, Kondensatablauf prüfen'
        }
    }
    
    # 20-Jahres-Plan erstellen
    schedule_20y = []
    total_cost_20y = 0
    
    for year in range(1, 21):
        year_items = []
        year_cost = 0
        
        for item_name, item_data in maintenance_items.items():
            interval = item_data['interval_years']
            
            # Prüfen ob Wartung fällig
            if year % interval == 0:
                probability = item_data.get('probability', 1.0)
                cost = item_data['cost_eur'] * probability
                
                year_items.append({
                    'item': item_name,
                    'cost_eur': round(cost, 2),
                    'description': item_data['description']
                })
                year_cost += cost
        
        total_cost_20y += year_cost
        
        schedule_20y.append({
            'year': year,
            'items': year_items,
            'total_cost_eur': round(year_cost, 2)
        })
    
    # Durchschnittskosten
    average_annual_cost = total_cost_20y / 20
    
    # Ersatzinvestitionen
    major_replacements = {
        'Jahr 15-18': {
            'component': 'Verdichter oder komplette WP-Erneuerung',
            'cost_eur': heatpump_data.get('price', 15000) * 0.6,  # 60% des Neupreises
            'note': 'Lebenserwartung WP: 15-20 Jahre'
        }
    }
    
    return {
        'schedule_20_years': schedule_20y,
        'summary': {
            'total_maintenance_cost_20y_eur': round(total_cost_20y, 2),
            'average_annual_cost_eur': round(average_annual_cost, 2),
            'major_services': [
                'Jahr 1: Erstinspektion (150-200€)',
                'Jahr 5: Elektrik-Check + Kältemittel-Prüfung (~400€)',
                'Jahr 10: Wärmetauscher-Reinigung (~400€)',
                'Jahr 15: Verdichter-Revision (~1.500-2.500€)',
                'Jahr 20: Ggf. WP-Ersatz'
            ]
        },
        'major_replacements': major_replacements,
        'warranty_info': {
            'standard_warranty_years': 2,
            'extended_warranty_available': True,
            'extended_warranty_cost_eur': 500,
            'extended_warranty_years': 5,
            'recommendation': 'Erweiterte Garantie für teure Komponenten (Verdichter) sinnvoll'
        },
        'diy_savings': {
            'possible_diy': [
                'Filter reinigen (halbjährlich)',
                'Außeneinheit von Laub befreien',
                'Sichtkontrolle Kondensatablauf',
                'Luftansaugung freihalten'
            ],
            'annual_savings_eur': 50,
            'note': 'Jährliche Fachinspektion bleibt Pflicht für Gewährleistung'
        }
    }


def refrigerant_charge_cost(refrigerant: str) -> float:
    """Berechnet Kältemittel-Nachfüllkosten"""
    cost_per_kg = {
        'R32': 40,
        'R290': 30,
        'R410A': 80,  # Teurer wegen Phase-Out
        'R454C': 60,
        'R1234yf': 100,
        'R744': 20
    }
    return cost_per_kg.get(refrigerant, 40) * 0.5  # 0.5 kg Nachfüllung typisch


# ============================================================================
# FEATURE 8.2: EXTREMWETTER-SIMULATION
# ============================================================================

def simulate_extreme_weather(
    building_data: Dict[str, Any],
    heatpump_data: Dict[str, Any],
    scenario: str = 'Kältewelle'
) -> Dict[str, Any]:
    """
    Simuliert Extrem-Szenarien und deren Auswirkungen
    
    Szenarien:
    - 'Kältewelle': -20°C für 7 Tage
    - 'Blackout': 24h Stromausfall
    - 'Hitzewelle': +38°C im Sommer (Kühlen)
    
    Returns:
    - Dict mit Szenario-Analyse
    """
    
    heat_load_kw = building_data.get('heat_load_kw', 10)
    wp_power_kw = heatpump_data.get('heating_power', 8)
    scop = heatpump_data.get('scop', 4.5)
    
    # Szenarien
    if scenario == 'Kältewelle':
        result = _simulate_cold_wave(building_data, heatpump_data, heat_load_kw, wp_power_kw, scop)
    elif scenario == 'Blackout':
        result = _simulate_blackout(building_data, heatpump_data, heat_load_kw)
    elif scenario == 'Hitzewelle':
        result = _simulate_heat_wave(building_data, heatpump_data)
    else:
        result = {'error': f'Unbekanntes Szenario: {scenario}'}
    
    return result


def _simulate_cold_wave(
    building_data: Dict,
    heatpump_data: Dict,
    heat_load_kw: float,
    wp_power_kw: float,
    scop: float
) -> Dict[str, Any]:
    """Simuliert 7-tägige Kältewelle mit -20°C"""
    
    outside_temp_design = building_data.get('outside_temp', -12)
    indoor_temp_target = building_data.get('desired_temp', 20)
    
    # Temperaturverhältnis
    extreme_temp = -20
    temp_ratio_extreme = (indoor_temp_target - extreme_temp) / (indoor_temp_target - outside_temp_design)
    
    # Heizlast bei -20°C
    heat_load_extreme_kw = heat_load_kw * temp_ratio_extreme
    
    # WP-Leistung bei -20°C (sinkt um ca. 20-30%)
    wp_power_at_extreme = wp_power_kw * 0.75  # 25% Leistungsverlust
    
    # Deckungsgrad
    coverage = wp_power_at_extreme / heat_load_extreme_kw
    
    # Pufferspeicher
    buffer_data = calculate_buffer_tank_size(heatpump_data, building_data)
    buffer_size_liters = buffer_data['recommended_size_liters']
    buffer_energy_kwh = buffer_size_liters * 0.058  # 1 Liter Wasser ≈ 0.058 kWh (ΔT=50K)
    
    # Szenario-Analyse
    if coverage >= 1.0:
        # WP kann Last decken
        runtime_hours_per_day = 18  # Sehr lange Laufzeit
        electricity_per_day_kwh = (heat_load_extreme_kw * runtime_hours_per_day) / (scop * 0.8)  # 20% COP-Verlust bei Extremkälte
        electricity_7_days_kwh = electricity_per_day_kwh * 7
        cost_7_days = electricity_7_days_kwh * 0.32
        
        assessment = "✅ WP AUSREICHEND - Kann Extremkälte bewältigen"
        recommendation = ["WP ist ausreichend dimensioniert", "Pufferspeicher hilft bei Spitzenlast"]
    else:
        # WP zu klein
        deficit_kw = heat_load_extreme_kw - wp_power_at_extreme
        
        # Wie lange reicht Pufferspeicher?
        buffer_runtime_hours = buffer_energy_kwh / deficit_kw if deficit_kw > 0 else 24
        
        # Notheizung erforderlich
        emergency_heating_kwh_per_day = deficit_kw * (24 - min(buffer_runtime_hours, 24))
        emergency_cost_per_day = emergency_heating_kwh_per_day * 0.32  # Elektroheizstab
        
        electricity_per_day_kwh = (wp_power_at_extreme * 18) / (scop * 0.8) + emergency_heating_kwh_per_day
        electricity_7_days_kwh = electricity_per_day_kwh * 7
        cost_7_days = electricity_7_days_kwh * 0.32
        
        assessment = f"⚠️ WP UNTERDIMENSIONIERT - {round((1 - coverage) * 100, 0)}% Leistungsdefizit"
        recommendation = [
            f"Zusatzheizung erforderlich: {round(deficit_kw, 1)} kW",
            "Elektroheizstab oder Gaskessel als Backup empfohlen",
            f"Pufferspeicher überbrückt nur {round(buffer_runtime_hours, 1)}h"
        ]
    
    return {
        'scenario': 'Kältewelle -20°C (7 Tage)',
        'conditions': {
            'außentemperatur_celsius': extreme_temp,
            'dauer_tage': 7,
            'heizlast_bei_extremkälte_kw': round(heat_load_extreme_kw, 1),
            'wp_leistung_bei_extremkälte_kw': round(wp_power_at_extreme, 1),
            'deckungsgrad_prozent': round(coverage * 100, 0)
        },
        'impact': {
            'stromverbrauch_7_tage_kwh': round(electricity_7_days_kwh, 0),
            'kosten_7_tage_eur': round(cost_7_days, 2),
            'durchschnittliche_laufzeit_h_pro_tag': runtime_hours_per_day if coverage >= 1.0 else 24,
            'pufferspeicher_überbrückung_h': round(buffer_runtime_hours, 1) if coverage < 1.0 else 'Nicht erforderlich'
        },
        'assessment': assessment,
        'recommendations': recommendation,
        'grid_impact': {
            'peak_load_kw': round(heat_load_extreme_kw / (scop * 0.8), 1),
            'note': 'Gleichzeitige Kältewelle führt zu Netz-Spitzenlasten',
            'sg_ready_benefit': '§14a EnWG erlaubt Netzbetreiber Dimmung bei Überlastung'
        }
    }


def _simulate_blackout(building_data: Dict, heatpump_data: Dict, heat_load_kw: float) -> Dict[str, Any]:
    """Simuliert 24h Stromausfall"""
    
    indoor_temp_start = building_data.get('desired_temp', 20)
    outside_temp = building_data.get('outside_temp', -5)
    
    # Gebäude-Wärmeverlust
    insulation_quality = building_data.get('insulation', 'Mittel')
    
    # Abkühlgeschwindigkeit (K/h) abhängig von Dämmung
    cooling_rate_per_hour = {
        'Schlecht': 1.2,  # Altbau
        'Mittel': 0.7,
        'Gut': 0.4,
        'Sehr gut': 0.2   # Passivhaus
    }.get(insulation_quality, 0.7)
    
    # Temperaturverlauf über 24h
    temp_progression = []
    current_temp = indoor_temp_start
    
    for hour in range(25):
        temp_progression.append({
            'hour': hour,
            'indoor_temp_celsius': round(current_temp, 1)
        })
        
        # Abkühlung berechnen
        current_temp -= cooling_rate_per_hour
        current_temp = max(current_temp, outside_temp)  # Nicht kälter als außen
    
    final_temp = temp_progression[-1]['indoor_temp_celsius']
    temp_drop = indoor_temp_start - final_temp
    
    # Bewertung
    if final_temp > 16:
        assessment = "✅ UNKRITISCH - Temperatur bleibt bewohnbar"
    elif final_temp > 12:
        assessment = "⚠️ UNBEQUEM - Temperatur sinkt deutlich, aber kein Frostschutz nötig"
    else:
        assessment = "❌ KRITISCH - Frostgefahr für Leitungen möglich"
    
    return {
        'scenario': 'Stromausfall (24 Stunden)',
        'conditions': {
            'außentemperatur_celsius': outside_temp,
            'ausgangstemperatur_innen_celsius': indoor_temp_start,
            'dämmqualität': insulation_quality,
            'abkühlrate_k_pro_stunde': cooling_rate_per_hour
        },
        'impact': {
            'endtemperatur_nach_24h_celsius': round(final_temp, 1),
            'temperaturabfall_k': round(temp_drop, 1),
            'temp_progression': temp_progression[::4]  # Alle 4h
        },
        'assessment': assessment,
        'recommendations': [
            'Notstromaggregat (3-5 kW) für kritische Infrastruktur',
            'PV + Batteriespeicher mit Inselfunktion als autarke Lösung',
            'Kaminofen als Backup-Heizung',
            'Bei Altbau: Frostschutz-Heizregister (12°C Minimum)'
        ],
        'mitigation': {
            'notstromaggregat_kosten_eur': 2000,
            'pv_batteriespeicher_kosten_eur': 12000,
            'kaminofen_kosten_eur': 3000
        }
    }


def _simulate_heat_wave(building_data: Dict, heatpump_data: Dict) -> Dict[str, Any]:
    """Simuliert Hitzewelle (Kühlfunktion)"""
    
    area = building_data.get('area', 150)
    
    # Kühllast grob: 50 W/m² (Wohngebäude)
    cooling_load_kw = area * 0.050
    
    # Reversible WP?
    reversible = 'reversibel' in str(heatpump_data.get('model', '')).lower() or \
                 'kühlfunktion' in str(heatpump_data.get('features', [])).lower()
    
    if not reversible:
        return {
            'scenario': 'Hitzewelle +38°C',
            'assessment': '❌ KEINE KÜHLFUNKTION - WP nicht reversibel',
            'recommendations': [
                'Bei Neukauf reversible WP wählen (Mehrkosten: 1.000-2.000€)',
                'Alternativ: Split-Klimaanlage nachrüsten',
                'Passive Kühlung: Nachtlüftung, Verschattung'
            ],
            'retrofit_options': {
                'reversible_wp_upgrade': 'Nicht möglich - neue WP erforderlich',
                'split_ac_cost_eur': 2500,
                'passive_cooling': 'Verschattung, Nachtlüftung (kostenlos)'
            }
        }
    
    # Reversible WP: Kühlen möglich
    # EER (Energy Efficiency Ratio) typisch 3-4
    eer = 3.5
    
    # Kühlbetrieb im Sommer (60 Tage)
    cooling_hours_per_day = 8  # Tageskühlung
    cooling_days = 60
    
    cooling_electricity_kwh = (cooling_load_kw * cooling_hours_per_day * cooling_days) / eer
    cooling_cost_eur = cooling_electricity_kwh * 0.32
    
    # PV-Synergieeffekt (Sommer = hohe PV-Produktion)
    pv_coverage_percentage = 70  # 70% kann mit PV gedeckt werden
    actual_grid_cost = cooling_cost_eur * (1 - pv_coverage_percentage / 100)
    
    return {
        'scenario': 'Hitzewelle +38°C (60 Tage Sommer)',
        'conditions': {
            'außentemperatur_celsius': 38,
            'kühllast_kw': round(cooling_load_kw, 1),
            'kühlbetrieb_h_pro_tag': cooling_hours_per_day,
            'anzahl_tage': cooling_days
        },
        'impact': {
            'stromverbrauch_kühlung_kwh': round(cooling_electricity_kwh, 0),
            'kosten_ohne_pv_eur': round(cooling_cost_eur, 2),
            'kosten_mit_pv_70_prozent_eur': round(actual_grid_cost, 2),
            'eer': eer
        },
        'assessment': '✅ KÜHLFUNKTION VERFÜGBAR - Reversible WP kann kühlen',
        'recommendations': [
            f'PV-Anlage optimal: {round(cooling_electricity_kwh / 60 * 0.3, 1)} kWp Zusatzleistung für Kühlung',
            'Fußbodenheizung als Flächenkühlung nutzen',
            'Taupunkt beachten: Max. 3K unter Raumtemperatur kühlen',
            'Außenjalousien für passive Kühlung kombinieren'
        ],
        'comfort': {
            'innentemperatur_ziel_celsius': 24,
            'kühlleistung_ausreichend': cooling_load_kw <= heatpump_data.get('heating_power', 10),
            'flächenkühlung': 'Möglich über Fußbodenheizung (18-20°C Vorlauf)'
        }
    }

