
"""Jahresenergieertrag kWh pro Jahr – calculate_annual_energy_yield

Zweck: Berechnet den erwarteten jährlichen Energieertrag der PV-Anlage in kWh basierend auf
der installierten Leistung (pv_peak_power_kwp) und einem spezifischen Ertrag pro kWp.
Diese Kennzahl gibt an, wie viel Energie die Anlage im Jahr produziert.
"""

from calculations_extended import (
    calc_direct_consumption_kwh,
    calc_battery_charge_kwh,
    calc_battery_discharge_kwh,
    calc_battery_surplus_kwh,
    calc_grid_feed_in_kwh,
    calc_feed_in_revenue_eur,
    calc_savings_from_storage_usage_eur,
    calc_revenue_from_battery_surplus_eur,
    calc_savings_from_direct_consumption_eur,
    calc_vat_saved_eur,
    calc_pv_system_size_kwp,
    calc_grid_purchase_kwh,
    calc_cumulative_grid_costs_with_increase,
    calc_cumulative_grid_costs_no_increase,
)
from typing import Dict, Any


def calculate_annual_energy_yield(pv_peak_power_kwp: float,
                                  specific_yield_kwh_per_kwp: float) -> float:
    """Jahresenergieertrag kWh pro Jahr"""
    return pv_peak_power_kwp * specific_yield_kwh_per_kwp


"""Eigenverbrauchsquote in % – calculate_self_consumption_quote

Zweck: Berechnet den Prozentsatz des PV-Stroms, der selbst verbraucht wird.
Diese Eigenverbrauchsquote (auch Selbstverbrauchsquote) gibt an, wie viel vom erzeugten PV-Strom unmittelbar
im Haushalt genutzt wird, anstatt ins Netz eingespeist zu werden.
"""


def calculate_self_consumption_quote(self_consumed_kwh: float,
                                     total_generation_kwh: float) -> float:
    """Eigenverbrauchsquote in %"""
    if total_generation_kwh == 0:
        return 0.0
    return (self_consumed_kwh / total_generation_kwh) * 100


"""Autarkiegrad in % – calculate_autarky_degree

Zweck: Bestimmt den Autarkiegrad, also den Anteil des gesamten Stromverbrauchs, der durch die PV-Anlage
gedeckt wird. Ein Autarkiegrad von 100 % würde bedeuten, dass der Haushalt rechnerisch komplett
durch selbst erzeugten PV-Strom versorgt wird.
"""


def calculate_autarky_degree(self_consumed_kwh: float,
                             total_consumption_kwh: float) -> float:
    """Autarkiegrad in % """
    if total_consumption_kwh == 0:
        return 0.0
    return (self_consumed_kwh / total_consumption_kwh) * 100


"""Spezifischer Ertrag kWh / kWp – calculate_specific_yield

Zweck: Ermittelt den spezifischen Ertrag der PV-Anlage, also die Jahresproduktion pro kW_p installierter Leistung.
Dieser Wert (kWh pro kWp) erlaubt den Vergleich der Produktivität unterschiedlicher Anlagen unabhängig von deren Größe.
"""


def calculate_specific_yield(annual_yield_kwh: float,
                             pv_peak_power_kwp: float) -> float:
    """Spezifischer Ertrag kWh / kWp """
    if pv_peak_power_kwp == 0:
        return 0.0
    return annual_yield_kwh / pv_peak_power_kwp


"""Flächenspezifischer Ertrag kWh / m² – calculate_area_specific_yield

Zweck: Berechnet den Ertrag pro belegter Modulfläche. Dieser flächenspezifische
Ertrag zeigt, wie effizient die genutzte Dachfläche in Energieertrag umgewandelt wird.
Er ist hilfreich, um z.B. verschiedene Modultypen oder Dachnutzungen zu vergleichen.
"""


def calculate_area_specific_yield(annual_yield_kwh: float,
                                  occupied_area_m2: float) -> float:
    """Flächenspezifischer Ertrag kWh / m²  """
    if occupied_area_m2 == 0:
        return 0.0
    return annual_yield_kwh / occupied_area_m2


"""Performance Ratio – calculate_performance_ratio

Zweck: Berechnet die Performance Ratio der PV-Anlage. Die PR ist ein Maß für die technische
Leistungsfähigkeit der Anlage und definiert sich als Verhältnis aus tatsächlichem Ertrag und theoretisch
möglichem Ertrag unter Standard-Testbedingungen (bereinigt um Einstrahlung und Modulleistung).
Eine PR von ~80 % ist für gut geplante Anlagen typisch.
"""


def calculate_performance_ratio(
        actual_yield_kwh: float,
        global_radiation_kwh_per_m2: float,
        pv_area_m2: float) -> float:
    """Performance Ratio - …"""
    theoretical_yield = global_radiation_kwh_per_m2 * pv_area_m2
    if theoretical_yield == 0:
        return 0.0
    return actual_yield_kwh / theoretical_yield


"""PV-Modulwirkungsgrad in % – calculate_pv_module_efficiency

Zweck: Ermittelt den Wirkungsgrad der PV-Module anhand deren Nennleistung und Fläche.
So lässt sich prüfen, ob Module z.B. einen typischen Wirkungsgrad (~18–20 %) aufweisen.
"""


def calculate_pv_module_efficiency(module_power_wp: float,
                                   module_area_m2: float) -> float:
    """Effizienz der PV-Module in % """
    if module_area_m2 == 0:
        return 0.0
    # 1000 W/m² Einstrahlung unter STC
    return (module_power_wp / (module_area_m2 * 1000)) * 100


"""Amortisationszeit in Jahre – calculate_payback_period

Zweck: Berechnet die statische Amortisationszeit der PV-Anlage in Jahren.
Diese gibt an, nach wie vielen Jahren sich die Investition durch die kumulierten
jährlichen Einsparungen bezahlt gemacht hat.
"""


def calculate_payback_period(investment_costs: float,
                             annual_savings: float) -> float:
    """Amortisationszeit in Jahre"""
    if annual_savings == 0:
        return float('inf')
    return investment_costs / annual_savings


"""Jährliche Stromkostenersparnis in € – calculate_annual_cost_savings

Zweck: Ermittelt die jährliche Ersparnis an Strombezugskosten durch den Eigenverbrauch
von PV-Strom. Diese Kennzahl multipliziert den selbst verbrauchten PV-Strom (self_consumed_kwh)
mit dem Strompreis und zeigt, wie viel Geld pro Jahr eingespart wird.
"""


def calculate_annual_cost_savings(self_consumed_kwh: float,
                                  electricity_price: float) -> float:
    """Jährliche Stromkostenersparnis in € """
    return self_consumed_kwh * electricity_price


"""Jährliche Einspeisevergütung in € – calculate_feed_in_tariff_revenue

Zweck: Berechnet die jährlichen Einnahmen aus der Einspeisung überschüssigen PV-Stroms ins öffentliche Netz.
Hierzu wird die eingespeiste Energiemenge (feed_in_kwh) mit dem Vergütungssatz (feed_in_rate_eur) multipliziert.
"""


def calculate_feed_in_tariff_revenue(feed_in_kwh: float,
                                     feed_in_rate_eur: float) -> float:
    """jährliche Einspeisevergütung in €"""
    return feed_in_kwh * feed_in_rate_eur


"""Effektiver PV-Strompreis ct / kWh – calculate_effective_pv_electricity_price

Zweck: Gibt an, was eine selbst erzeugte Kilowattstunde effektiv kostet. Diese Kennzahl –
oft als Levelized Cost of Energy (LCOE) bezeichnet – wird hier vereinfacht berechnet als Quotient aus gesamten
Systemkosten (total_costs) und dem gesamten Energieertrag über die Lebensdauer (total_generated_kwh), in Cent pro kWh.
Sie zeigt, ob der PV-Strom günstiger ist als Netzstrom.
"""


def calculate_effective_pv_electricity_price(
        total_costs: float,
        total_generated_kwh: float) -> float:
    """Effektiver Strompreis durch PV in ct / kWh"""
    if total_generated_kwh == 0:
        return float('inf')
    return (total_costs / total_generated_kwh) * 100


"""Kapitalwert – calculate_npv (generische Cashflow-Variante)

Zweck: Berechnet den Nettobarwert (NPV) einer Reihe von Cashflows. Die Funktion calculate_npv summiert die
diskontierten Cashflows (cashflows-Liste, wobei der erste typischerweise die negative Investition ist) auf. Sie nutzt dafür die
Finanzbibliothek oder implementiert es per Summation. Ein positiver NPV bedeutet, dass das Projekt über die Laufzeit einen Wertzuwachs generiert.
"""


def calculate_npv(cashflows: List[float], discount_rate: float) -> float:
    """Nettobarwert NPV"""
    # … npf.npv erwartet Rate und Cashflows
    return npf.npv(discount_rate, cashflows)


"""Kapitalwert für konstante Erträge – calculate_net_present_value

Zweck: Berechnet den Nettobarwert (NPV) der PV-Investition bei gleichbleibender jährlicher Ersparnis. Diese spezielle NPV-Berechnung nimmt an,
dass die jährliche Ersparnis über die gesamte Lebensdauer (LIFESPAN_YEARS, standardmäßig 25) konstant ist. Sie liefert direkt den Kapitalwert
unter Verwendung des Kalkulationszinses.
"""


def calculate_net_present_value(
        investment: float,
        annual_savings: float) -> float:
    """Kapitalwert (NPV) der Investition"""
    cash_flows = [annual_savings] * LIFESPAN_YEARS
    return npf.npv(DISCOUNT_RATE, cash_flows) - investment


"""Interner Zinsfuß (IRR) – calculate_irr (generische Cashflow-Variante)

Zweck: Berechnet den internen Zinsfuß eines gegebenen Cashflow-Stroms. calculate_irr liefert jenen Zinssatz (in %),
bei dem der Kapitalwert der Cashflows Null wäre. Sie nutzt numpy_financial.irr im Hintergrund. Diese generische Variante
arbeitet mit einer Liste von Cashflows (erster Eintrag typischerweise -Investition, folgende Einträge jährliche Überschüsse).
"""


def calculate_irr(cashflows: List[float]) -> float:
    """Interner Zinsfuß (IRR) """
    try:
        return npf.irr(cashflows) * 100
    except BaseException:
        return 0.0


"""Interner Zinsfuß – erweiterte Berechnung – calculate_irr_advanced

Zweck: Führt eine erweiterte Berechnung des internen Zinsfußes (IRR) durch, inklusive zusätzlicher Finanzkennzahlen. Sie berechnet aus den
Ergebnissen (calc_results) zunächst die Cashflow-Serie (Investition gefolgt von jährlichem Nutzen über 25 Jahre), ermittelt dann iterativ den IRR,
und berechnet zudem den modifizierten IRR (MIRR) und den Profitability Index (PI). Ergebnis ist ein Dict mit diesen Werten in Prozent.
"""


def calculate_irr_advanced(
        self, calc_results: Dict[str, Any]) -> Dict[str, Any]:
    """Erweiterte IRR-Berechnung"""
    investment = calc_results.get("total_investment_netto", 20000)
    annual_benefit = calc_results.get("annual_financial_benefit_year1", 1500)
    lifetime = 25
    # Cash Flow generieren
    cash_flows = [-investment] + [annual_benefit] * lifetime
    # IRR iterativ berechnen
    irr = 0.0
    try:
        for rate in np.arange(0.01, 0.20, 0.001):
            npv = sum(cf / (1 + rate) ** i for i, cf in enumerate(cash_flows))
            if abs(npv) < 100:
                irr = rate
                break
    except BaseException:
        irr = 0.05  # Fallback
    # MIRR (vereinfacht)
    finance_rate = 0.04
    reinvest_rate = 0.03
    mirr = ((annual_benefit * lifetime / investment) ** (1 / lifetime)) - 1
    # Profitability Index
    pi = (sum(annual_benefit / (1 + 0.04) ** year
              for year in range(1, lifetime + 1)) / investment)
    return {"irr": irr * 100, "mirr": mirr * 100, "profitability_index": pi}


"""Rentabilitätsindex (Profitability Index) – calculate_profitability_index

Zweck: Berechnet den Rentabilitätsindex (PI) des PV-Projekts. Der PI ist definiert als Verhältnis des Kapitalwertes der
zukünftigen Cashflows zur Anfangsinvestition. Ein PI > 1 bedeutet, dass der Kapitalwert die Investition
übersteigt (Projekt wirtschaftlich attraktiv).
"""


def calculate_profitability_index(
        investment: float,
        annual_savings: float) -> float:
    """Rentabilitätsindex."""
    if investment <= 0:
        return 0.0
    npv_of_future_cash_flows = npf.npv(
        DISCOUNT_RATE, [annual_savings] * LIFESPAN_YEARS)
    return npv_of_future_cash_flows / investment


"""Gesamtrendite über Lebensdauer – calculate_total_roi

Zweck: Berechnet die Gesamtverzinsung bzw. Rendite der PV-Anlage über die gesamte Lebensdauer. Dieser Return on Investment (ROI) in Prozent gibt an,
um wie viel Prozent sich das eingesetzte Kapital über z.B. 25 Jahre vermehrt. Hier definiert als: (Gesamtgewinn / Investition) * 100.
"""


def calculate_total_roi(investment: float, annual_savings: float) -> float:
    """Gesamtrendite über die gesamte Lebensdauer."""
    if investment <= 0:
        return 0.0
    total_profit = (annual_savings * LIFESPAN_YEARS) - investment
    return (total_profit / investment) * 100


"""Durchschnittliche Eigenkapitalrendite (%) – calculate_annual_equity_return

Zweck: Gibt an, welche jährliche Rendite das investierte Kapital im Durchschnitt erzielt. Diese Kennzahl –
hier als durchschnittliche Eigenkapitalrendite berechnet – entspricht (jährliche Einsparung / Investition) * 100. Im Grunde
ist dies der Kehrwert der statischen Amortisationszeit und gibt eine grobe Renditeabschätzung pro Jahr.
"""


def calculate_annual_equity_return(
        investment: float,
        annual_savings: float) -> float:
    """durchschnittliche jährliche Eigenkapitalrendite"""
    if investment <= 0:
        return 0.0
    return (annual_savings / investment) * 100


"""Gewinn nach X Jahren – calculate_profit_after_x_years

Zweck: Berechnet den kumulierten Gewinn nach einer bestimmten Anzahl von Jahren. Hier wird angenommen, dass jedes Jahr eine konstante Ersparnis (annual_savings) erzielt wird.
Für years Jahre ergibt sich Gewinn = (Ersparnis * Jahre) - Investition. Diese Kennzahl ist etwa für die Zwischenbetrachtung interessant („Nach 10 Jahren hat die Anlage insgesamt Y € Gewinn erzielt.“).
"""


def calculate_profit_after_x_years(investment: float,
                                   annual_savings: float,
                                   years: int) -> float:
    """kumulierter Gewinn nach … Jahren"""
    return (annual_savings * years) - investment


"""Monte-Carlo Risikoanalyse – run_monte_carlo_simulation

Zweck: Führt eine Monte-Carlo-Simulation zur Risikobewertung der Wirtschaftlichkeit durch.
Dabei werden zahlreiche Zufallssimulationen durchgeführt, indem Investitionskosten, jährliche Erträge und Diskontsatz innerhalb gewisser
Streuungen variiert werden. Das Ergebnis sind Verteilungen des Kapitalwerts (NPV), aus denen Kennzahlen wie durchschnittlicher NPV,
Standardabweichung, Konfidenzintervalle und Erfolgswahrscheinlichkeit (Wahrscheinlichkeit, dass NPV > 0) abgeleitet werden.
"""


def run_monte_carlo_simulation(self,
                               calc_results: Dict[str,
                                                  Any],
                               n_simulations: int,
                               confidence_level: int) -> Dict[str,
                                                              Any]:
    """Monte-Carlo-Simulation für Risikobewertung"""
    np.random.seed(42)
    base_investment = calc_results.get("total_investment_netto", 20000)
    base_annual_benefit = calc_results.get(
        "annual_financial_benefit_year1", 1500)
    lifetime = 25
    npv_distribution = []
    for _ in range(n_simulations):
        # Parameter variieren (normalverteilt)
        investment = np.random.normal(base_investment, base_investment * 0.1)
        annual_benefit = np.random.normal(
            base_annual_benefit, base_annual_benefit * 0.15)
        discount_rate = np.random.normal(0.04, 0.01)
        # NPV berechnen
        npv = -investment
        for year in range(1, lifetime + 1):
            npv += annual_benefit / (1 + discount_rate) ** year
        npv_distribution.append(npv)
    npv_distribution = np.array(npv_distribution)
    # Statistiken
    npv_mean = np.mean(npv_distribution)
    npv_std = np.std(npv_distribution)
    # Konfidenzintervall
    alpha = (100 - confidence_level) / 2
    npv_lower_bound = np.percentile(npv_distribution, alpha)
    npv_upper_bound = np.percentile(npv_distribution, 100 - alpha)
    # Value at Risk
    var_5 = np.percentile(npv_distribution, 5)
    # Erfolgswahrscheinlichkeit
    success_probability = (npv_distribution > 0).sum() / n_simulations * 100
    # Sensitivitätsanalyse (vereinfacht)
    sensitivity_analysis = [...]
    return {
        "npv_distribution": npv_distribution.tolist(),
        "npv_mean": npv_mean,
        "npv_std": npv_std,
        "npv_lower_bound": npv_lower_bound,
        "npv_upper_bound": npv_upper_bound,
        "var_5": var_5,
        "success_probability": success_probability,
        "sensitivity_analysis": sensitivity_analysis,
    }


"""Speicherdeckungsgrad (%) – calculate_storage_coverage_degree

Zweck: Gibt an, wieviel vom gesamten Eigenverbrauch durch den Batteriespeicher bereitgestellt wird.
Mit anderen Worten: welcher Prozentsatz des selbst verbrauchten PV-Stroms stammt aus dem Speicher. Ein hoher Speicherdeckungsgrad
bedeutet, dass der Speicher einen Großteil des Verbrauchs puffert. Formel: gespeicherter Eigenverbrauch / Gesamt-Eigenverbrauch * 100.
"""


def calculate_storage_coverage_degree(
        stored_self_consumption_kwh: float,
        total_self_consumption_kwh: float) -> float:
    """Deckungsquote des Batteriespeichers in %"""
    if total_self_consumption_kwh == 0:
        return 0.0
    return (stored_self_consumption_kwh / total_self_consumption_kwh) * 100


"""Batteriezyklen und Lebensdauer – _calculate_battery_cycles

Zweck: Schätzt die jährliche Anzahl an Vollzyklen des Batteriespeichers und daraus grob die Lebensdauer. In dieser vereinfachten Berechnung wird angenommen,
der Speicher (mit gegebener Kapazität) wird eine bestimmte Anzahl Male pro Jahr voll be- und entladen. Daraus wird dann eine prognostizierte Lebensdauer in Jahren
abgeleitet, meist unter Annahme einer maximalen Zyklenanzahl. (In der Beispiel-Implementierung werden Werte simuliert oder Platzhalter genutzt.)
"""


def _calculate_battery_cycles(
        self, base_data: Dict[str, Any]) -> Dict[str, Any]:
    """Batteriezyklen und Lebensdauer"""
    battery_capacity = base_data.get("battery_capacity_kwh", 10)
    # Annahme: 250 Zyklen pro Jahr (aus global constants)
    cycles_per_year = base_data.get("storage_cycles_per_year", 250)
    total_cycles = cycles_per_year * \
        base_data.get("simulation_period_years", 20)
    # Lebensdauer in Jahren bei 5000 Zyklen Gesamtlebensdauer
    est_lifetime = 5000 / \
        cycles_per_year if cycles_per_year > 0 else float("inf")
    return {
        "annual_cycles": cycles_per_year,
        "total_cycles_over_lifetime": total_cycles,
        "estimated_lifetime_years": est_lifetime
    }


"""Optimale Batteriespeichergröße (kWh) – calculate_optimal_storage_size

Zweck: Schätzt auf einfache Weise eine empfohlene Batteriespeicherkapazität. Hier wird als Heuristik der tägliche Verbrauch herangezogen,
abzüglich eines Verlustfaktors. Die Idee ist, dass ein Speicher ungefähr den Tagesverbrauch (bzw. Nachtverbrauch) aufnehmen sollte, minus Verluste.
Diese Berechnung ist stark vereinfacht und dient nur der Orientierung.
"""


def calculate_optimal_storage_size(daily_consumption_kwh: float,
                                   losses_percent: float = 10.0) -> float:
    """Optimale Speichergröße in kWh"""
    return daily_consumption_kwh * (1 - losses_percent / 100)


"""Lastverschiebepotenzial (kWh) – calculate_load_shifting_potential

Zweck: Ermittelt, wieviel PV-Überschuss durch verschiebbare Lasten genutzt werden könnte. Das Lastverschiebepotenzial ist definiert als Minimum aus verschiebbarer
Verbrauchsmenge (controllable_load_kwh) und PV-Überschuss (pv_surplus_kwh). Es quantifiziert die Energiemenge, die durch z.B. Einschalten flexibler
Verbraucher (Waschmaschine, E-Auto laden) zusätzlich selbst genutzt werden kann.
"""


def calculate_load_shifting_potential(controllable_load_kwh: float,
                                      pv_surplus_kwh: float) -> float:
    """Lastverschiebepotenzial durch Verbraucher in kWh """
    return min(controllable_load_kwh, pv_surplus_kwh)


"""PV-Deckungsgrad für Wärmepumpe (%) – calculate_pv_coverage_for_heatpump

Zweck: Gibt an, zu wieviel Prozent der Jahresstrombedarf einer Wärmepumpe durch PV-Überschuss gedeckt werden kann. Diese Kennzahl berechnet sich aus dem PV-Strom,
der zur Wärmebereitstellung genutzt wird (pv_surplus_to_hp_kwh), relativ zum gesamten jährlichen Strombedarf der Wärmepumpe.
"""


def calculate_pv_coverage_for_heatpump(
        pv_surplus_to_hp_kwh: float,
        heatpump_annual_consumption_kwh: float) -> float:
    """PV-Deckungsgrad für Wärmepumpe in %"""
    if heatpump_annual_consumption_kwh == 0:
        return 0.0
    return (pv_surplus_to_hp_kwh / heatpump_annual_consumption_kwh) * 100


"""Lastspitzenkappung (Peak Shaving) – _calculate_peak_shaving

Zweck: Schätzt, wie stark Lastspitzen durch einen Speicher reduziert werden können. In der Beispielimplementierung von _calculate_peak_shaving werden
Lastprofile angenommen und verglichen – letztlich würde diese Funktion z.B. die Differenz zwischen originaler Spitzenlast und optimierter Spitzenlast berechnen.
Das Ergebnis könnte sein: Reduktion um X kW (und ggf. prozentuale Senkung).
"""


def _calculate_peak_shaving(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
    """Lastspitzenkappung"""
    # Beispielhafte Lastprofile
    original_peak = 5.0  # kW (z.B. gemessene Spitze)
    reduced_peak = 4.0   # kW (durch Speicher)
    shaving_effect = original_peak - reduced_peak
    return {
        "original_peak_kw": original_peak,
        "reduced_peak_kw": reduced_peak,
        "peak_shaving_effect_kw": shaving_effect
    }


"""Energieautarkie-Analyse (%) – _calculate_energy_independence

Zweck: Analysiert die Energieunabhängigkeit über die Zeit. Diese Funktion würde z.B. untersuchen, wie der Autarkiegrad sich im
Jahresverlauf entwickelt oder wie lange die Anlage netzunabhängig betrieben werden kann (z.B. mit Speicher). In der Vorlage könnte sie
Kennzahlen wie monatliche Autarkie oder Anzahl autarker Tage liefern.
"""


def _calculate_energy_independence(
        self, base_data: Dict[str, Any]) -> Dict[str, Any]:
    """Energieunabhängigkeit über Zeit"""
    # (Im Code sind keine Details implementiert – Stub)
    independence = base_data.get("autarkie_grad_percent", 50)  # z.B. 50%
    return {"current_independence_percent": independence}


``` *(Pseudo - Code gemäß Beschreibung)*

# Technische Anlagenanalysen

"""Degradationsanalyse – `_calculate_degradation`
Zweck: Berechnet die Leistungsabnahme der PV-Module über 25 Jahre aufgrund der Moduldegradation. Dabei wird pro Jahr ein konstanter
Degradationsfaktor (hier 0,5 % Leistungsabfall pro Jahr) angenommen. Die Funktion liefert die verbleibende Leistung über die Jahre, den
kumulierten Energieverlust sowie die finale Restleistung in Prozent der Anfangsleistung nach 25 Jahren.
"""


def _calculate_degradation(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
    """Degradation über 25 Jahre"""
    years = 25
    initial_power = base_data.get("anlage_kwp", 10) * 1000  # in Watt
    degradation_rate = 0.005  # 0.5% pro Jahr
    power_over_time = []
    energy_loss = []
    for year in range(years + 1):
        current_power = initial_power * (1 - degradation_rate) ** year
        power_over_time.append(current_power)
        if year > 0:
            annual_loss = (initial_power - current_power) * \
                1700  # kWh pro Jahr
            energy_loss.append(annual_loss)
    return {
        "years": list(range(years + 1)),
        "power_kw": [p / 1000 for p in power_over_time],
        "total_energy_loss_kwh": sum(energy_loss),
        "final_performance_percent": (power_over_time[-1] / initial_power) * 100,
        "average_degradation_rate": degradation_rate * 100,
    }


"""Verschattungsverluste (%) – _calculate_shading

Zweck: Führt eine detaillierte Abschätzung der Verschattungsverluste durch. In der Implementierung wird für jede Stunde
von 6–19 Uhr und jeden Monat ein Verschattungsfaktor berechnet (morgen/abends mehr Schatten, im Winter mehr Schatten). Daraus entsteht
eine 12×? Matrix (Stunden vs. Monate) der Verschattung. Aus dem Mittelwert wird ein jährlicher Verschattungsverlust in kWh berechnet und der
durchschnittliche prozentuale Abschattungssatz. Außerdem werden die optimalen Sonnenstunden (z.B. 10–15 Uhr ohne starke Verschattung) angegeben.
"""


def _calculate_shading(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
    """detaillierte Verschattungsverluste"""
    hours_of_day = list(range(6, 20))  # 6:00 bis 19:00
    months = [
        "Jan",
        "Feb",
        "Mär",
        "Apr",
        "Mai",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Okt",
        "Nov",
        "Dez"]
    shading_matrix = []
    for month_idx in range(12):
        month_shading = []
        for hour in hours_of_day:
            base_shading = 0.1  # 10% Basis-Verschattung
            if hour < 9 or hour > 17:
                base_shading += 0.2  # morgens/abends +20%
            if month_idx in [0, 1, 10, 11]:
                base_shading += 0.15  # Winter +15%
            month_shading.append(min(base_shading, 0.9))
        shading_matrix.append(month_shading)
    # jährlicher Verlust
    avg_shading = np.mean(shading_matrix)
    annual_loss_kwh = base_data.get(
        "annual_pv_production_kwh",
        10000) * avg_shading
    return {
        "hours": hours_of_day,
        "months": months,
        "shading_matrix": shading_matrix,
        "average_shading_percent": avg_shading * 100,
        "annual_shading_loss_kwh": annual_loss_kwh,
        "optimal_hours": [h for h in hours_of_day if 10 <= h <= 15],
    }


"""Verschattungsanalyse (einfach) – calculate_shading_analysis

Zweck: Vereinfachte Verschattungsanalyse-Funktion, die ebenfalls eine Verschattungsmatrix erzeugt, aber mit etwas
abweichenden Parametern (Stunden 6–18 Uhr, andere Prozentwerte). Sie liefert neben Matrix und durchschnittlichem Verlust auch den Monat mit der stärksten
Verschattung, dessen Durchschnittsverlust und ein Optimierungspotenzial (z.B. durch Maßnahmen könnten 30% der Verluste reduziert werden). Diese Variante ist
offenbar ein später ergänzter Stub mit gleichem Ziel.
"""


def calculate_shading_analysis(
        self, project_data: Dict[str, Any]) -> Dict[str, Any]:
    """Verschattungsanalyse"""
    shading_matrix = []
    for month in range(12):
        month_data = []
        for hour in range(6, 19):
            base_shading = 5  # 5% Grundverschattung
            if hour < 9 or hour > 16:
                base_shading += 10  # morgens/abends +10%
            if month in [0, 1, 10, 11]:
                base_shading += 15  # Winter +15%
            month_data.append(min(base_shading, 50))
        shading_matrix.append(month_data)
    annual_loss = np.mean(shading_matrix)
    energy_loss_kwh = project_data.get(
        "annual_production", 10000) * annual_loss / 100
    worst_month_idx = np.argmax([np.mean(month) for month in shading_matrix])
    worst_month = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun",
                   "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"][worst_month_idx]
    worst_month_loss = np.mean(shading_matrix[worst_month_idx])
    optimization_potential = energy_loss_kwh * 0.3
    return {
        "shading_matrix": shading_matrix,
        "annual_shading_loss": annual_loss,
        "energy_loss_kwh": energy_loss_kwh,
        "worst_month": worst_month,
        "worst_month_loss": worst_month_loss,
        "optimization_potential": optimization_potential,
    }


"""Temperatureffekte – calculate_temperature_effects

Zweck: Analysiert den Einfluss der Temperatur auf die PV-Leistung. Es wird von Durchschnittstemperaturen pro Monat (Umgebung) ausgegangen und
daraus Modultemperaturen geschätzt (+25°C). Mit einem Temperaturkoeffizienten (hier -0,4%/°C) wird die prozentuale Leistungsabnahme für jeden Monat
berechnet. Die Funktion liefert die Liste der monatlichen Leistungsverluste in %, den Durchschnitt und Maximum, sowie die daraus resultierende
geschätzte jährliche Energieeinbuße in kWh.
"""


def calculate_temperature_effects(self, calc_results: Dict[str, Any],
                                  project_data: Dict[str, Any]) -> Dict[str, Any]:
    """Temperatureffekte und Auswirkungen auf die PV-Anlage"""
    ambient_temps = [2, 4, 8, 13, 18, 21, 23,
                     22, 18, 13, 7, 3]  # Monatsmittel (°C)
    module_temps = [temp + 25 for temp in ambient_temps]
    temp_coefficient = -0.004  # -0,4% pro °C
    reference_temp = 25  # °C
    power_loss_percent = []
    for temp in module_temps:
        loss = abs(temp_coefficient * (temp - reference_temp)) * 100
        power_loss_percent.append(loss)
    avg_temp_loss = np.mean(power_loss_percent)
    max_module_temp = max(module_temps)
    max_temp_delta = max_module_temp - max(ambient_temps)
    annual_energy_loss = (calc_results.get("annual_pv_production_kwh", 10000)
                          * avg_temp_loss / 100)
    return {
        "ambient_temperatures": ambient_temps,
        "module_temperatures": module_temps,
        "power_loss_percent": power_loss_percent,
        "avg_temp_loss": avg_temp_loss,
        "max_module_temp": max_module_temp,
        "max_temp_delta": max_temp_delta,
        "annual_energy_loss": annual_energy_loss,
    }


"""Wechselrichter-Effizienzanalyse – calculate_inverter_efficiency

Zweck: Untersucht die Wirkungsgradcharakteristik des Wechselrichters. Es wird eine typische Wirkungsgradkurve über der Auslastung (%) modelliert:
bei niedriger Last geringerer Wirkungsgrad, Maximalwirkungsgrad um ~98% im Teillastbereich, etc. Zusätzlich werden Kennwerte wie Euro- und CEC-Wirkungsgrad
berechnet (gewichtete Durchschnittswerte nach Standardverfahren). Die Funktion liefert die Wirkungsgradkurve (Liste), Beispiel-Operating-Points und deren Effizienzen,
die berechneten Euro- und CEC-Wirkungsgrade, und abschätzbare jährliche Verluste in kWh basierend auf dem durchschnittlichen Wirkungsgrad. Außerdem berechnet sie einen
Dimensionierungsfaktor (DC-zu-AC Überdimensionierung in %).
"""


def calculate_inverter_efficiency(self, calc_results: Dict[str, Any],
                                  project_data: Dict[str, Any]) -> Dict[str, Any]:
    """Wechselrichter-Effizienzanalyse"""
    load_percentages = list(range(0, 101, 5))
    efficiency_curve = []
    for load in load_percentages:
        if load < 5:
            eff = 0
        elif load < 10:
            eff = 85 + load * 1.5
        elif load < 20:
            eff = 95 + (load - 10) * 0.3
        elif load < 100:
            eff = 98 - (load - 20) * 0.025
        else:
            eff = 96
        efficiency_curve.append(eff)
    operating_points = [20, 30, 50, 70, 100]
    operating_efficiencies = [
        efficiency_curve[int(p / 5)] for p in operating_points]
    # Euro-Effizienz (gewichtete Durchschnittswerte)
    euro_points = [
        efficiency_curve[1],
        efficiency_curve[2],
        efficiency_curve[4],
        efficiency_curve[6],
        efficiency_curve[10],
        efficiency_curve[20]]
    euro_efficiency = np.average(
        euro_points, weights=[
            0.03, 0.06, 0.13, 0.1, 0.48, 0.2])
    # CEC-Effizienz
    cec_points = [
        efficiency_curve[2],
        efficiency_curve[4],
        efficiency_curve[6],
        efficiency_curve[10],
        efficiency_curve[15],
        efficiency_curve[20]]
    cec_efficiency = np.average(
        cec_points, weights=[
            0.04, 0.05, 0.12, 0.21, 0.53, 0.05])
    # Verluste
    annual_production = calc_results.get("annual_pv_production_kwh", 10000)
    avg_efficiency = np.mean(efficiency_curve[4:21])  # 20-100% Auslastung
    annual_losses = annual_production * (100 - avg_efficiency) / 100
    loss_percentage = 100 - avg_efficiency
    # Dimensionierung (DC-AC Verhältnis)
    dc_power = calc_results.get("anlage_kwp", 10)
    ac_power = project_data.get("inverter_power_kw", dc_power * 0.9)
    sizing_factor = (dc_power / ac_power * 100) if ac_power > 0 else 110
    return {
        "efficiency_curve": efficiency_curve,
        "operating_points": operating_points,
        "operating_efficiencies": operating_efficiencies,
        "euro_efficiency": euro_efficiency,
        "cec_efficiency": cec_efficiency,
        "annual_losses": annual_losses,
        "loss_percentage": loss_percentage,
        "sizing_factor": sizing_factor,
    }


"""Wartungsplan und -kosten – _calculate_maintenance

Zweck: Erstellt einen beispielhaften Wartungsplan mit jährlichen Kosten. Hier wird z.B. aus der Anlagengröße (anlage_kwp) ein Basiswert berechnet und eventuell
über Jahre gesteigert. In der Vorlage nimmt _calculate_maintenance einen pauschalen Ansatz – sie würde z.B. die jährlichen Wartungskosten (fix + variabel pro kWp)
über die Lebensdauer summieren und einen Plan ausgeben.
"""


def _calculate_maintenance(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
    """Wartungsplan mit Kosten"""
    system_size_kwp = base_data.get("anlage_kwp", 10)
    fixed_costs = base_data.get("maintenance_fixed_eur_pa", 50.0)
    variable_costs = base_data.get("maintenance_variable_eur_per_kwp_pa", 5.0)
    increase_percent = base_data.get("maintenance_increase_percent_pa", 2.0)
    years = base_data.get("simulation_period_years", 20)
    annual_costs = []
    for year in range(1, years + 1):
        cost = fixed_costs + variable_costs * system_size_kwp
        # jährliche Steigerung
        cost *= ((1 + increase_percent / 100) ** (year - 1))
        annual_costs.append(cost)
    total_maintenance = sum(annual_costs)
    return {
        "annual_costs": [round(c, 2) for c in annual_costs],
        "total_maintenance_costs": round(total_maintenance, 2),
        "average_annual_cost": round(total_maintenance / years, 2)
    }


"""Netzinteraktions-Analyse – _calculate_grid_interaction

Zweck: Betrachtet die Einspeisung und den Bezug mit dem Netz. Hier könnten Kennzahlen ermittelt werden wie z.B. Jahresüberschuss eingespeist, Restbezug aus dem Netz,
Eigenverbrauchsanteil etc. In der gegebenen Dummy-Implementierung wird mit Platzhalterwerten gearbeitet (z.B. 500 kWh für jeden Monat als Produktion). Letztlich würde
die echte Implementierung Input aus Last- und Erzeugungsprofilen benötigen, um z.B. monatliche Einspeisung/Bezug zu liefern.
"""


def _calculate_grid_interaction(
        self, base_data: Dict[str, Any]) -> Dict[str, Any]:
    """Netzinteraktion"""
    monthly_production = base_data.get("monthly_production", [500] * 12)
    monthly_consumption = base_data.get("monthly_consumption", [400] * 12)
    grid_feed = []
    grid_draw = []
    for prod, cons in zip(monthly_production, monthly_consumption):
        # Einspeisung = Überschuss, Netzbezug = Verbrauchüberschuss
        feed = max(0, prod - cons)
        draw = max(0, cons - prod)
        grid_feed.append(feed)
        grid_draw.append(draw)
    return {
        "monthly_grid_feed_in": grid_feed,
        "monthly_grid_purchase": grid_draw,
        "annual_feed_in": sum(grid_feed),
        "annual_grid_purchase": sum(grid_draw)
    }


"""DC/AC-Überdimensionierung – calculate_dc_ac_oversizing_factor

Zweck: Berechnet den Überdimensionierungsfaktor der PV-Anlage bezogen auf Wechselrichterleistung. Das Ergebnis = PV-Leistung (kWp) / WR-Leistung (kW)
als Faktor. Ein Wert > 1 bedeutet, die PV-Generatorleistung übersteigt die WR-Nennleistung (was gängige Praxis bis etwa 1.2 ist).
"""


def calculate_dc_ac_oversizing_factor(
        pv_power_kwp: float,
        inverter_power_kw: float) -> float:
    """DC / AC-Überdimensionierungsfaktor"""
    if inverter_power_kw == 0:
        return float('inf')
    return pv_power_kwp / inverter_power_kw


"""Dachflächenausnutzung – calculate_roof_usage

Zweck: Berechnet, wie viele PV-Module auf einer gegebenen Dachfläche installiert werden können. Dazu wird die verfügbare Dachfläche (roof_area_m2) durch die
Fläche eines einzelnen Moduls (module_length_m * module_width_m) geteilt. Das Ergebnis ist die (abgerundete) Anzahl Module.
"""


def calculate_roof_usage(roof_area_m2: float, module_length_m: float,
                         module_width_m: float) -> int:
    """Dachflächennutzung - Anzahl Module """
    module_area = module_length_m * module_width_m
    if module_area == 0:
        return 0
    return int(roof_area_m2 / module_area)


"""Notstromfähigkeit (kWh/Tag) – calculate_emergency_power_capacity

Zweck: Berechnet, wieviel Energie ein Batteriespeicher im Notstrombetrieb pro Tag liefern kann. Formel: Speicher nutzbare Kapazität (storage_kwh) * (Nutzungsgrad %).
Wenn z.B. 10 kWh Speicher und 80% nutzbar als Notstrom, ergäbe das 8 kWh pro Tag.
"""


def calculate_emergency_power_capacity(
        storage_kwh: float,
        usable_capacity_percent: float) -> float:
    """Notstromfähigkeit in kWh / Tag) """
    return storage_kwh * (usable_capacity_percent / 100)


"""Anlagenerweiterung – calculate_plant_expansion

Zweck: Vergleicht zwei Anlagenzustände (alt vs. neu) und gibt die Differenz der KPI-Werte aus. Diese Funktion nimmt zwei Dicts (old_kpis, new_kpis) und bildet für
jeden Schlüssel die Differenz: neuer Wert minus alter Wert. So kann man sehen, wie sich z.B. jährlicher Ertrag, Autarkie, ROI etc. durch eine Erweiterung verändern.
"""


def calculate_plant_expansion(old_kpis: Dict, new_kpis: Dict) -> Dict:
    """Anlagenerweiterung"""
    return {k: new_kpis.get(k, 0) - old_kpis.get(k, 0) for k in new_kpis}


"""Umwelt- und Nachhaltigkeitsmetriken
CO₂-Einsparung (kg/Jahr) – calculate_co2_savings

Zweck: Berechnet die jährliche CO₂-Ersparnis durch die PV-Anlage in Kilogramm. Multipliziert den jährlichen PV-Ertrag (annual_yield_kwh) mit einem
Emissionsfaktor (co2_factor_kg_per_kwh). Standardwert hier ~0,401 kg CO₂ pro kWh (deutscher Strommix 2023). Das Ergebnis sind kg CO₂, die pro Jahr
vermieden werden, weil dieser PV-Strom nicht aus dem Netz bezogen wird.
"""


def calculate_co2_savings(annual_yield_kwh: float,
                          co2_factor_kg_per_kwh: float = 0.401) -> float:
    """CO2-Einsparung in kg pro Jahr"""
    return annual_yield_kwh * co2_factor_kg_per_kwh


"""CO₂-Amortisationszeit (Jahre) – calculate_co2_payback_time

Zweck: Ermittelt die Zeit in Jahren, bis die CO₂-Emissionen, die bei Herstellung/Installation der PV-Anlage anfielen, durch die Einsparungen kompensiert sind.
Dazu wird die “graue” CO₂-Emission der Anlage (hier angenommen CO2_EMBODIED_PV_KWP kg pro kWp, multipliziert mit Anlagen-kWp) durch die jährliche
CO₂-Ersparnis (kg/Jahr) geteilt. Ergebnis: Jahre bis zur CO₂-Neutralität der Anlage.
"""


def calculate_co2_payback_time(pv_size_kwp: float,
                               annual_production_kwh: float) -> float:
    """CO2-Amortisationszeit"""
    total_embodied_co2 = pv_size_kwp * CO2_EMBODIED_PV_KWP
    annual_co2_savings_kg = annual_production_kwh * CO2_EMISSIONS_GRID_KWH
    if annual_co2_savings_kg <= 0:
        return float('inf')
    return total_embodied_co2 / annual_co2_savings_kg


"""Detaillierte CO₂-Bilanz – calculate_detailed_co2_analysis

Zweck: Liefert eine umfassende CO₂-Bilanz der PV-Anlage über die Lebensdauer. Sie berechnet jährliche CO₂-Ersparnis (in Tonnen), die kumulierte Ersparnis über
25 Jahre, die CO₂-Emissionen für Produktion der Anlage, daraus die CO₂-Amortisationszeit (Jahre), die gesamte Netto-CO₂-Einsparung über 25 Jahre (Einsparung minus
Produktions-Emissionen). Zusätzlich werden Äquivalente berechnet: wie viele Bäume diese Einsparung entspricht, wie viele Autokilometer, sowie weitere
Umweltaspekte (eingesparte Primärenergie, Wasser, vermiedene Schadstoffe SO₂, NOx, Partikel).
"""


def calculate_detailed_co2_analysis(
        self, calc_results: Dict[str, Any]) -> Dict[str, Any]:
    """Detaillierte CO2-Bilanz"""
    annual_production = calc_results.get("annual_pv_production_kwh", 10000)
    system_kwp = calc_results.get("anlage_kwp", 10)
    years = 25
    co2_factor_kg_kwh = 0.474  # kg CO2 pro kWh (Deutschland)
    annual_co2_savings = annual_production * \
        co2_factor_kg_kwh / 1000  # Tonnen/Jahr
    years_list = list(range(1, years + 1))
    cumulative_savings = [annual_co2_savings * year for year in years_list]
    production_emissions = system_kwp * 1000 * 0.05  # Tonnen (50g/Wp)
    carbon_payback_time = (production_emissions / annual_co2_savings
                           if annual_co2_savings > 0 else 99)
    total_co2_savings = annual_co2_savings * years - production_emissions
    tree_equivalent = total_co2_savings * 47  # 22 kg CO2/Jahr pro Baum -> 47 Bäume
    car_km_equivalent = total_co2_savings * 1000 / 0.12  # 120g/km -> km
    primary_energy_saved = annual_production * years * 2.8  # kWh Primärenergie
    water_saved = annual_production * years * 1.2  # Liter Wasser
    so2_avoided = total_co2_savings * 0.474 * 0.001  # kg SO2
    nox_avoided = total_co2_savings * 0.474 * 0.0008  # kg NOx
    particulates_avoided = total_co2_savings * 0.474 * 0.00005  # kg Feinstaub
    return {
        "years": years_list,
        "cumulative_savings": cumulative_savings,
        "production_emissions": production_emissions,
        "carbon_payback_time": carbon_payback_time,
        "total_co2_savings": total_co2_savings,
        "tree_equivalent": tree_equivalent,
        "car_km_equivalent": car_km_equivalent,
        "primary_energy_saved": primary_energy_saved,
        "water_saved": water_saved,
        "so2_avoided": so2_avoided,
        "nox_avoided": nox_avoided,
        "particulates_avoided": particulates_avoided,
    }


"""Primärenergie- und Schadstoff-Einsparungen – in obiger Funktion enthalten

Zweck: Innerhalb von calculate_detailed_co2_analysis werden zusätzliche Umweltmetriken berechnet:

Primärenergieeinsparung (kWh): Multipliziert den PV-Strom über 25 Jahre mit einem Faktor (2,8 kWh Primärenergie pro kWh Strom) – zeigt, wie
viel Primärenergie (z.B. Kohle, Gas) eingespart wird.

Wasser-Ersparnis (Liter): Multipliziert PV-Strom mit 1,2 L/kWh – zeigt eingespartes Kühlwasser in Kraftwerken.

Vermeidene SO₂, NOx, Feinstaub (kg): Aus der gesamten CO₂-Einsparung werden mit Faktoren kleine Mengen an klassischen Luftschadstoffen abgeleitet,
die ebenfalls vermieden werden (nur symbolische Rechnung).

Diese Werte werden im zurückgegebenen Dict unter primary_energy_saved, water_saved, so2_avoided, nox_avoided, particulates_avoided bereitgestellt.
Im UI werden sie derzeit nicht einzeln angezeigt, könnten aber im PDF-Bericht oder auf Wunsch im Nachhaltigkeits-Tab erwähnt werden (z.B. “Insgesamt sparen
Sie X MWh Primärenergie, Y kg NOx-Emissionen…”). Die Berechnungen sind bereits integriert in obiger Funktion und somit automatisch Teil der Ergebnisse,
die in analysis.py weiterverarbeitet werden könnten.
"""
# kein code extra

"""Material-Recycling-Potenzial – calculate_recycling_potential

Zweck: Analysiert die Zusammensetzung der PV-Anlage und ihr Recyclingpotenzial. Die Funktion berechnet anhand der Anlagengröße (system_kwp) die Masse
von Materialien (Silizium, Aluminium, Glas, Kunststoff) in der Anlage und kennzeichnet sie als recyclebar oder nicht. Zudem werden für die Materialien potentielle
Werte (€/kg) angenommen, um einen möglichen Erlös aus Recycling zu schätzen. Weiter gibt die Funktion an: Recyclingrate in %, CO₂-Einsparung durch
Recycling (z.B. Annahme 0,5 Tonnen CO₂ pro kWp), Entsorgungskosten am Lebensende und potenzieller Recyclingerlös.
"""


def calculate_recycling_potential(
        self, calc_results: Dict[str, Any], project_data: Dict[str, Any]) -> Dict[str, Any]:
    """Stub für Recycling-Potenzial"""
    system_kwp = calc_results.get("anlage_kwp", 10.0)
    silicon_weight = system_kwp * 15  # kg Silizium pro kWp
    aluminum_weight = system_kwp * 25  # kg Aluminium pro kWp
    glass_weight = system_kwp * 50  # kg Glas pro kWp
    plastic_weight = system_kwp * 8  # kg Kunststoff pro kWp
    return {
        "material_composition": [
            {"material": "Silizium", "weight_kg": silicon_weight,
                "recyclable": True, "value_per_kg": 15.0},
            {"material": "Aluminium", "weight_kg": aluminum_weight,
                "recyclable": True, "value_per_kg": 2.5},
            {"material": "Glas", "weight_kg": glass_weight,
                "recyclable": True, "value_per_kg": 0.1},
            {"material": "Kunststoff", "weight_kg": plastic_weight,
                "recyclable": False, "value_per_kg": 0.0},
        ],
        "recycling_rate": 85.0,  # Prozent recycelbar
        "material_value": (silicon_weight * 15.0 + aluminum_weight * 2.5 + glass_weight * 0.1),
        # Tonnen CO2-Einsparung durch Recycling
        "co2_savings_recycling": system_kwp * 0.5,
        "end_of_life_cost": system_kwp * 50,  # Entsorgungskosten in €
        "recycling_revenue": system_kwp * 75,  # Erlös aus Recycling in €
    }


"""Förderszenarien – calculate_subsidy_scenarios

Zweck: Simuliert verschiedene Fördermodelle und deren Einfluss auf die Wirtschaftlichkeit. In der Implementierung werden vier Szenarien betrachtet:

Ohne Förderung – normaler Cashflow.

KfW-Kredit (1%) – Annahme: 80% der Investition als Kredit zu 1% Zins, rest selbst getragen.

Zuschuss 10% – 10% Investitionszuschuss (also geringere Anfangskosten).

Kombination – 20% Zuschuss + Kredit (70% zu 0,5% Zins).

Für jedes Szenario wird ein Cashflow über 25 Jahre berechnet (Year 1 beinhaltet Investition minus Zuschuss/Kreditanteil etc., folgende Jahre
jeweils die Ersparnis minus Zins/Kreditkosten). Aus den Endwerten der Cashflows werden dann Kennzahlen gebildet (NPV, IRR, Amortisation, Förderungssumme).
"""


def calculate_subsidy_scenarios(
        self, calc_results: Dict[str, Any]) -> Dict[str, Any]:
    """Förderszenarien"""
    base_investment = calc_results.get("total_investment_netto", 20000)
    annual_benefit = calc_results.get("annual_financial_benefit_year1", 1500)
    years = 25
    scenarios = {
        "Jahr": list(range(1, years + 1)),
        "Ohne Förderung": [],
        "KfW-Kredit (1%)": [],
        "Zuschuss 10%": [],
        "Kombination": [],
    }
    # Cashflow für jedes Szenario berechnen
    for year in range(1, years + 1):
        # Ohne Förderung
        cf_none = (-base_investment + annual_benefit) if year == 1 else (
            scenarios["Ohne Förderung"][-1] + annual_benefit)
        scenarios["Ohne Förderung"].append(cf_none)
        # KfW-Kredit (1%)
        if year == 1:
            cf_kfw = (-base_investment * 0.2 + annual_benefit -
                      base_investment * 0.8 * 0.01)
        else:
            cf_kfw = scenarios["KfW-Kredit (1%)"][-1] + \
                annual_benefit - base_investment * 0.8 * 0.01
        scenarios["KfW-Kredit (1%)"].append(cf_kfw)
        # 10% Zuschuss
        cf_grant = (-base_investment * 0.9 + annual_benefit) if year == 1 else (
            scenarios["Zuschuss 10%"][-1] + annual_benefit)
        scenarios["Zuschuss 10%"].append(cf_grant)
        # Kombination
        if year == 1:
            cf_combo = (-base_investment * 0.8 + annual_benefit -
                        base_investment * 0.7 * 0.005)
        else:
            cf_combo = scenarios["Kombination"][-1] + \
                annual_benefit - base_investment * 0.7 * 0.005
        scenarios["Kombination"].append(cf_combo)
    # Vergleichstabelle erstellen
    comparison = [{"Szenario": "Ohne Förderung",
                   "NPV": float(scenarios["Ohne Förderung"][-1]),
                   "IRR": 5.2,
                   "Amortisation": 13.3,
                   "Förderung": 0.0},
                  {"Szenario": "KfW-Kredit",
                   "NPV": float(scenarios["KfW-Kredit (1%)"][-1]),
                   "IRR": 7.1,
                   "Amortisation": 11.8,
                   "Förderung": float(base_investment * 0.8 * 0.03)},
                  {"Szenario": "Zuschuss 10%",
                   "NPV": float(scenarios["Zuschuss 10%"][-1]),
                   "IRR": 8.4,
                   "Amortisation": 10.2,
                   "Förderung": float(base_investment * 0.1)},
                  {"Szenario": "Kombination",
                   "NPV": float(scenarios["Kombination"][-1]),
                   "IRR": 9.8,
                   "Amortisation": 8.9,
                   "Förderung": float(base_investment * 0.2 + base_investment * 0.7 * 0.025)},
                  ]
    return {"scenarios": scenarios, "comparison": comparison}


"""Investitionsszenarien (A/B/C) – analyze_investment_scenarios

Zweck: Platzhalter-Funktion, die mehrere vordefinierte Investitionsszenarien vergleicht. Erwartet ein Dict scenarios, das z.B. drei verschiedene
Konfigurationen (A, B, C) mit ihren KPI-Werten enthält, und gibt es unverändert zurück. Eigentlich sollte hier pro Szenario die Berechnung
aller KPIs erfolgen, um einen Vergleich zu ermöglichen.
"""


def analyze_investment_scenarios(scenarios: Dict[str, Dict]) -> Dict:
    """Investitionsszenarien"""
    # Platzhalter-Funktion
    return {name: kpis for name, kpis in scenarios.items()}


"""Risikoanalyse (erwarteter Verlust) – analyze_risk

Zweck: Berechnet einen erwarteten Schaden/Verlust im Falle eines Risikoszenarios. Nimmt einen potenziellen Schadenbetrag (damage_amount)
und eine Eintrittswahrscheinlichkeit (probability_percent) und gibt das Produkt als Erwartungswert aus. Im Prinzip entspricht dies dem
Value-at-Risk bei gegebener Wahrscheinlichkeit (hier linear, ohne Zeitbezug).
"""


def analyze_risk(damage_amount: float, probability_percent: float) -> float:
    """Ausfallwahrscheinlichkeit / Kosten Risikoanalyse"""
    return damage_amount * (probability_percent / 100)


"""Optimierungsvorschläge – generate_optimization_suggestions

Zweck: Generiert eine Liste von vordefinierten Optimierungsmaßnahmen für die PV-Anlage inklusive Beschreibung, Kategorie, Aufwand, Nutzenpotential,
ROI-Verbesserung und Kostenschätzung. Im Code sind fünf Beispiele aufgeführt (Batteriespeicher erweitern, Optimierer installieren, Warmwasser-Integration,
Smart Home, E-Auto Ladestation) mit jeweiligen fiktiven Werten. Die Funktion sortiert diese Vorschläge nach ROI-Verbesserung, ergänzt für jeden Vorschlag
noch berechnete Felder (z.B. payback = Kosten/Nutzen, difficulty = Einordnung des Aufwands in “Einfach/Mittel/Komplex”). Außerdem werden pauschal optimale
Systemparameter angegeben (Neigungswinkel, Ausrichtung, optimale Batteriegröße, DC-AC-Verhältnis).
"""


def generate_optimization_suggestions(
        self, calc_results: Dict[str, Any], project_data: Dict[str, Any]) -> Dict[str, Any]:
    """Optimierungsvorschläge"""
    optimization_potentials = [{"title": "Batteriespeicher erweitern",
                                "description": "Vergrößerung des Batteriespeichers für höheren Eigenverbrauch",
                                "category": "Speicher",
                                "implementation_effort": 30,
                                "benefit_potential": 400,
                                "roi_improvement": 1.2,
                                "cost_estimate": 3000,
                                },
                               {"title": "Optimierer installieren",
                                "description": "Leistungsoptimierer für verschattete Module",
                                "category": "Technik",
                                "implementation_effort": 50,
                                "benefit_potential": 600,
                                "roi_improvement": 2.1,
                                "cost_estimate": 2000,
                                },
                               {"title": "Warmwasser-Integration",
                                "description": "Elektrische Warmwasserbereitung für PV-Überschuss",
                                "category": "Integration",
                                "implementation_effort": 40,
                                "benefit_potential": 300,
                                "roi_improvement": 0.8,
                                "cost_estimate": 1500,
                                },
                               {"title": "Smart Home System",
                                "description": "Intelligente Laststeuerung für optimalen Verbrauch",
                                "category": "Automatisierung",
                                "implementation_effort": 60,
                                "benefit_potential": 250,
                                "roi_improvement": 0.6,
                                "cost_estimate": 2500,
                                },
                               {"title": "Ladestation E-Auto",
                                "description": "Elektroauto-Ladestation für PV-Strom",
                                "category": "Mobilität",
                                "implementation_effort": 35,
                                "benefit_potential": 800,
                                "roi_improvement": 3.2,
                                "cost_estimate": 1200,
                                },
                               ]
    # Top-Empfehlungen sortieren
    top_recommendations = sorted(
        optimization_potentials,
        key=lambda x: x["roi_improvement"],
        reverse=True)
    # Zusätzliche Details ergänzen
    for rec in top_recommendations:
        rec["annual_benefit"] = rec["benefit_potential"]
        rec["investment"] = rec["cost_estimate"]
        rec["payback"] = (
            rec["investment"] /
            rec["annual_benefit"] if rec["annual_benefit"] > 0 else 99)
        rec["difficulty"] = ("Einfach" if rec["implementation_effort"] < 40 else
                             "Mittel" if rec["implementation_effort"] < 60 else "Komplex")
    system_optimization = {
        "optimal_tilt": 30,  # Optimaler Neigungswinkel
        "optimal_azimuth": 0,  # Süd
        "optimal_battery_size": 8.0,  # kWh
        "optimal_dc_ac_ratio": 1.15,
    }
    return {
        "optimization_potentials": optimization_potentials,
        "top_recommendations": top_recommendations,
        "system_optimization": system_optimization,
    }


"""Finanzierungsmodelle und Steuern
Annuitätenkredit-Rechner – calculate_annuity

Zweck: Berechnet die Details eines Annuitätendarlehens (gleichbleibende Raten). Aus Darlehensbetrag (principal), Zinssatz (annual_interest_rate) und
Laufzeit in Jahren wird die monatliche Kreditrate berechnet sowie Gesamtzins und Tilgungsplan (Monat für Monat Aufschlüsselung von Zins, Tilgung und Restschuld).
So kann der Nutzer sehen, welche Kreditkosten über die Laufzeit entstehen.
"""


def calculate_annuity(principal: float,
                      annual_interest_rate: float,
                      duration_years: int) -> Dict[str,
                                                   Any]:
    """Annuität / Kredit mit gleichbleibenden Raten"""
    if principal <= 0 or annual_interest_rate < 0 or duration_years <= 0:
        return {"error": "Ungültige Eingabeparameter"}
    monthly_rate = annual_interest_rate / 100 / 12
    num_payments = duration_years * 12
    if monthly_rate == 0:  # zinsfrei
        monthly_payment = principal / num_payments
        total_interest = 0
    else:
        # Annuitätenformel
        monthly_payment = principal * \
            (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        total_interest = (monthly_payment * num_payments) - principal
    tilgungsplan = []
    remaining_principal = principal
    for month in range(1, int(num_payments) + 1):
        if monthly_rate == 0:
            interest_payment = 0
            principal_payment = monthly_payment
        else:
            interest_payment = remaining_principal * monthly_rate
            principal_payment = monthly_payment - interest_payment
        remaining_principal -= principal_payment
        tilgungsplan.append({
            'monat': month,
            'rate': round(monthly_payment, 2),
            'zinsen': round(interest_payment, 2),
            'tilgung': round(principal_payment, 2),
            'restschuld': round(max(0, remaining_principal), 2)
        })
    return {
        "monatliche_rate": round(monthly_payment, 2),
        "gesamtzinsen": round(total_interest, 2),
        "gesamtkosten": round(principal + total_interest, 2),
        "effective_rate": round(annual_interest_rate, 2),
        "tilgungsplan": tilgungsplan,
        "laufzeit_monate": num_payments
    }


"""Leasingkostenrechner – calculate_leasing_costs

Zweck: Berechnet die Kosten eines PV-Leasings. Nimmt die Investitionssumme (total_investment), einen monatlichen Leasingfaktor (Prozent des Invest pro Monat),
die Laufzeit in Monaten und ggf. einen Restwert-Prozentsatz. Liefert monatliche Rate, Gesamtkosten über die Laufzeit, kalkulierten Restwert und effektive
Kosten (Gesamtkosten minus Restwert). Ebenfalls wird ein Vergleichswert ausgegeben (kostenvorteil_vs_kauf), was man gegenüber einem direkten
Kauf spart (Investition minus effektive Kosten).
"""


def calculate_leasing_costs(total_investment: float,
                            leasing_factor: float,
                            duration_months: int,
                            residual_value_percent: float = 1.0) -> Dict[str,
                                                                         Any]:
    """Leasingkostenberechnung"""
    if total_investment <= 0 or leasing_factor <= 0 or duration_months <= 0:
        return {"error": "Ungültige Parameter"}
    monthly_leasing_rate = total_investment * (leasing_factor / 100)
    total_leasing_costs = monthly_leasing_rate * duration_months
    residual_value = total_investment * (residual_value_percent / 100)
    effective_costs = total_leasing_costs - residual_value
    return {
        "monatliche_rate": round(monthly_leasing_rate, 2),
        "gesamtkosten": round(total_leasing_costs, 2),
        "restwert": round(residual_value, 2),
        "effektive_kosten": round(effective_costs, 2),
        "leasingfaktor": leasing_factor,
        "laufzeit_monate": duration_months,
        "kostenvorteil_vs_kauf": round(total_investment - effective_costs, 2)
    }


"""Abschreibungsrechner – calculate_depreciation

Zweck: Berechnet die Abschreibung der PV-Anlage über die Nutzungsdauer. Derzeit nur lineare Abschreibung implementiert: Teilt den
Anschaffungswert (initial_value) gleichmäßig auf die Jahre (useful_life_years) auf. Liefert einen Abschreibungsplan pro Jahr (Abschreibung und
Restbuchwert) sowie Gesamtabschreibung und eine einfache Steuerersparnis-Annahme (z.B. 30% Steuersatz).
"""


def calculate_depreciation(initial_value: float,
                           useful_life_years: int,
                           method: str = "linear") -> Dict[str,
                                                           Any]:
    """Abschreibungsberechnung"""
    if initial_value <= 0 or useful_life_years <= 0:
        return {"error": "Ungültige Parameter"}
    abschreibungsplan = []
    if method == "linear":
        annual_depreciation = initial_value / useful_life_years
        for year in range(1, useful_life_years + 1):
            book_value = initial_value - (annual_depreciation * year)
            abschreibungsplan.append({
                'jahr': year,
                'abschreibung': round(annual_depreciation, 2),
                'buchwert': round(max(0, book_value), 2),
                'kumulierte_abschreibung': round(annual_depreciation * year, 2)
            })
    return {
        "methode": method,
        "jaehrliche_abschreibung": round(annual_depreciation, 2),
        "gesamtabschreibung": round(initial_value, 2),
        "abschreibungsplan": abschreibungsplan,
        "steuerersparnis_30_prozent": round(initial_value * 0.30, 2)
    }


"""Kapitaldienstfähigkeit – check_debt_service_capability

Zweck: Prüft, ob der Jahresüberschuss der Anlage ausreicht, um die jährliche Kreditbelastung (Annuität) zu decken. Gibt einen Faktor zurück:
Jahresüberschuss / Annuität. Ist dieser > 1, kann der Kredit bedient werden; >1.2 gilt meist als komfortabel.
"""


def check_debt_service_capability(
        annual_surplus: float,
        annuity: float) -> float:
    """Kapitaldienstfähigkeitsprüfung als Faktor"""
    if annuity == 0:
        return float('inf')
    return annual_surplus / annuity


"""Restwert der Anlage – calculate_residual_value

Zweck: Berechnet den Restwert der PV-Anlage nach X Jahren, bei linearer Wertminderung. Annahme: pro Jahr fällt der Wert um einen bestimmten
Prozentsatz (annual_depreciation_percent). Die Formel: Investition * (1 - Abschreibungsrate)^Jahre. Dies ist eher eine vereinfachte degressive Abschätzung.
"""


def calculate_residual_value(
        investment: float,
        annual_depreciation_percent: float,
        years: int) -> float:
    """Restwert der Anlage (nach x Jahren)"""
    return investment * ((1 - annual_depreciation_percent / 100) ** years)


"""Ersparnis durch Förderung – calculate_costs_after_funding

Zweck: Berechnet die effektiven Investitionskosten nach Abzug von Fördermitteln. Einfach: investment - funding_amount. Diese Funktion zeigt,
wie stark z.B. ein Zuschuss die anfänglichen Kosten reduziert.
"""


def calculate_costs_after_funding(
        investment: float,
        funding_amount: float) -> float:
    """Ersparnis durch Fördermittel / Kredite (effektive Kosten) """
    return investment - funding_amount


"""Netzanschlusskosten – calculate_grid_connection_costs

Zweck: Summiert beliebige übergebene Kostenwerte auf. Diese Funktion nimmt eine variable Anzahl an Kostenpositionen (*costs) und gibt deren Summe zurück.
Gedacht, um sämtliche Netzanschluss-bezogenen Posten (z.B. Zähler, Anschlussgebühr, etc.) zusammenzufassen.
"""


def calculate_grid_connection_costs(*costs: float) -> float:
    """Netzanschlusskosten """
    return sum(costs)


"""PV vs. Balkonkraftwerk – compare_pv_vs_balcony

Zweck: Vergleicht Kennzahlen einer vollwertigen PV-Anlage mit einer Balkon-PV. Nimmt die Kosten und Erträge beider und gibt ein Dict mit
Differenzen aus: cost_difference und yield_difference. Idee: Man kann sehen, um wieviel teurer und ertragreicher die große Anlage gegenüber einem Balkonkraftwerk ist.
"""


def compare_pv_vs_balcony(costs_pv: float, yield_pv: float,
                          costs_balcony: float, yield_balcony: float) -> Dict:
    """Vergleich Photovoltaik vs. Balkonkraftwerk """
    return {
        'cost_difference': costs_pv - costs_balcony,
        'yield_difference': yield_pv - yield_balcony
    }


"""Kapitalertragsteuer (KESt) – calculate_capital_gains_tax

Zweck: Berechnet die Steuerlast auf Gewinne aus der PV-Anlage (z.B. bei Einspeisevergütung in AT, 27,5% KESt oder in DE ggf. ESt). In dieser Implementierung
Standard 26,375% (österreichischer KESt-Satz) auf den übergebenen Gewinnbetrag. Gibt Bruttogewinn, Steuerbetrag und Nettogewinn zurück, plus Steuersatz.
"""


def calculate_capital_gains_tax(
        profit: float, tax_rate: float = 26.375) -> Dict[str, Any]:
    """Kapitalerstragssteuer-Berechnung"""
    if profit <= 0:
        return {"steuer": 0, "netto_gewinn": profit, "steuer_rate": tax_rate}
    tax_amount = profit * (tax_rate / 100)
    net_profit = profit - tax_amount
    return {
        "brutto_gewinn": round(profit, 2),
        "steuer": round(tax_amount, 2),
        "netto_gewinn": round(net_profit, 2),
        "steuer_rate": tax_rate,
        "steuer_optimierung_tipps": [
            "Investitionsabzugsbetrag nutzen",
            "Sonderabschreibungen prüfen",
            "Verlustvorträge berücksichtigen"
        ]
    }


"""Contracting-Kosten – calculate_contracting_costs

Zweck: Berechnet die jährlichen und gesamten Stromkosten in einem Contracting-Modell (wenn der Kunde PV-Strom als Dienstleistung bezieht). Nimmt eine
monatliche Grundgebühr (base_fee), einen Arbeitspreis pro kWh (consumption_price), den verbrauchten Strom pro Jahr (consumed_kwh) und die Vertragslaufzeit
in Jahren. Gibt die jährliche Grundgebühr (12 * Monatsgebühr), jährliche Verbrauchskosten, jährliche Gesamtkosten und Gesamtkosten über die Vertragslaufzeit
aus. Zusätzlich berechnet sie einen effektiven Strompreis pro kWh aus der Summe der jährlichen Kosten.
"""


def calculate_contracting_costs(base_fee: float,
                                consumption_price: float,
                                consumed_kwh: float,
                                period_years: int = 1) -> Dict[str,
                                                               Any]:
    """Contracting-Kosten"""
    annual_base_fee = base_fee * 12 if period_years >= 1 else base_fee
    annual_consumption_costs = consumption_price * consumed_kwh
    annual_total = annual_base_fee + annual_consumption_costs
    total_costs_period = annual_total * period_years
    return {
        "jaehrliche_grundgebuehr": round(annual_base_fee, 2),
        "jaehrliche_verbrauchskosten": round(annual_consumption_costs, 2),
        "jaehrliche_gesamtkosten": round(annual_total, 2),
        "gesamtkosten_laufzeit": round(total_costs_period, 2),
        "kosten_pro_kwh_effektiv": round(annual_total / consumed_kwh if consumed_kwh > 0 else 0, 4),
        "laufzeit_jahre": period_years
    }


Speichernutzung

Einnahmen aus Einspeisevergütung _annual_feed_in_euro
Netzeinspeisung
Ersparnis aus Speichernutzung
Einnahmen aus Batterieüberschuss
Ersparnis durch direkter Verbrauch
Ersparte Mehrwertsteuer
PV - Anlagengröße
Netzbezug

Stromkosten kumuliert mit Erhöhung auf 10 Jahre
Stromkosten kumuliert ohne Erhöhung auf 10 Jahre
Stromkosten kumuliert mit Erhöhung auf 20 Jahre
Stromkosten kumuliert ohne Erhöhung auf 20 Jahre


"""Direkter Verbrauch (kWh)
Direkter Verbrauch (aus PV tagsüber):"""


def calc_direct_consumption_kwh(results: Dict[str, Any]) -> float:

    direct = float(results.get('direct_consumption_kwh', 0.0))
    if direct > 0:
        return direct
    cons = float(results.get('annual_consumption_kwh', 0.0))
    autark = float(results.get('self_supply_rate_percent', 0.0))
    direct = max(0.0, min(cons, cons * autark / 100.0))
    return direct

# from calculations_extended import calc_direct_consumption_kwh
# direct_consumption_kwh_ext = calc_direct_consumption_kwh(results)


"""Speicherladung (kWh)
"""


def calc_battery_charge_kwh(
        results: Dict[str, Any], days_per_year: int = 365) -> float:
    """
    Jahres-Speicherladung in kWh (durch PV gedeckelt).
    """
    cap = max(0.0, float(results.get('battery_capacity_kwh', 0.0)))
    pv = max(0.0, float(results.get('annual_pv_production_kwh', 0.0)))
    direct = calc_direct_consumption_kwh(results)
    possible = max(0.0, pv - direct)
    return max(0.0, min(possible, cap * float(days_per_year)))

# from calculations_extended import calc_battery_charge_kwh
# battery_charged_kwh_ext = calc_battery_charge_kwh(results)


"""Speichernutzung / -Entladung (kWh)"""


def calc_battery_discharge_kwh(
        results: Dict[str, Any], days_per_year: int = 365) -> float:
    """
    Jahres-Speicherentladung (nutzbare Speicherenergie für den Haushalt).
    """
    direct = calc_direct_consumption_kwh(results)
    cons = max(0.0, float(results.get('annual_consumption_kwh', 0.0)))
    remain = max(0.0, cons - direct)
    charge = calc_battery_charge_kwh(results, days_per_year=days_per_year)
    return max(0.0, min(remain, charge))

# from calculations_extended import calc_battery_discharge_kwh
# battery_discharge_kwh_ext = calc_battery_discharge_kwh(results)


"""Netzeinspeisung (kWh)"""


def calc_grid_feed_in_kwh(
        results: Dict[str, Any], days_per_year: int = 365) -> float:
    """
    Netzeinspeisung aus direktem PV-Überschuss (kWh/Jahr).
    """
    pv = max(0.0, float(results.get('annual_pv_production_kwh', 0.0)))
    direct = calc_direct_consumption_kwh(results)
    charge = calc_battery_charge_kwh(results, days_per_year=days_per_year)
    return max(0.0, pv - direct - charge)

# from calculations_extended import calc_grid_feed_in_kwh
# grid_feed_in_kwh_ext = calc_grid_feed_in_kwh(results)


"""Einnahmen aus Einspeisevergütung (€/a)"""


def _resolve_feed_in_eur_per_kwh(results: Dict[str, Any]) -> float:
    if float(results.get('feed_in_tariff_ct_kwh', 0.0)) > 0.0:
        return float(results.get('feed_in_tariff_ct_kwh')) / 100.0
    return float(results.get('eeg_eur_per_kwh', 0.0))


def calc_feed_in_revenue_eur(
        results: Dict[str, Any], days_per_year: int = 365) -> float:
    """
    Jährliche Einnahmen aus EEG/Einspeisevergütung in Euro.
    """
    feed_in = calc_grid_feed_in_kwh(results, days_per_year=days_per_year)
    tariff = _resolve_feed_in_eur_per_kwh(results)
    return feed_in * tariff


"""Ersparnis aus Speichernutzung (€/a)"""


def _resolve_price_eur_per_kwh(results: Dict[str, Any]) -> float:
    price_ct = float(results.get('stromtarif_ct_kwh', 0.0))
    if price_ct > 0.0:
        return price_ct / 100.0
    annual_cost = float(results.get('monthly_electricity_cost', 0.0)) * 12.0
    cons = float(results.get('annual_consumption_kwh', 0.0))
    return (annual_cost / cons) if cons > 0 else 0.0


def calc_savings_from_storage_usage_eur(
        results: Dict[str, Any], days_per_year: int = 365) -> float:
    """
    Ersparnis durch genutzte Speicherenergie (€/Jahr).
    """
    discharge = calc_battery_discharge_kwh(
        results, days_per_year=days_per_year)
    price = _resolve_price_eur_per_kwh(results)
    return discharge * price


"""Einnahmen aus Batterieüberschuss (€/a)"""


def calc_battery_surplus_kwh(
        results: Dict[str, Any], days_per_year: int = 365) -> float:
    """
    Jährlicher Batterieüberschuss (kWh), der nicht verbraucht werden konnte.
    """
    charge = calc_battery_charge_kwh(results, days_per_year=days_per_year)
    discharge = calc_battery_discharge_kwh(
        results, days_per_year=days_per_year)
    return max(0.0, charge - discharge)


def calc_revenue_from_battery_surplus_eur(
        results: Dict[str, Any], days_per_year: int = 365) -> float:
    """
    Einnahmen aus Batterieüberschuss (€/Jahr) bei Netzeinspeisung.
    """
    surplus = calc_battery_surplus_kwh(results, days_per_year=days_per_year)
    tariff = _resolve_feed_in_eur_per_kwh(results)
    return surplus * tariff


"""Ersparnis durch direkten Verbrauch (€/a)"""


def calc_savings_from_direct_consumption_eur(results: Dict[str, Any]) -> float:
    """
    Ersparnis durch direkt verbrauchte PV-Energie (€/Jahr).
    """
    direct = calc_direct_consumption_kwh(results)
    price = _resolve_price_eur_per_kwh(results)
    return direct * price


"""Ersparte Mehrwertsteuer (€, einmalig)"""


def calc_vat_saved_eur(results: Dict[str, Any]) -> float:
    """
    Ersparte Mehrwertsteuer (Brutto-Netto oder 19% des Netto als Fallback für Privatkunden).
    """
    customer_type = str(results.get('customer_type', '')).lower()
    is_private = customer_type in [
        'privat',
        'private',
        'privatperson',
        'privatkunde']
    brutto = float(results.get('total_investment_brutto', 0.0))
    netto = float(results.get('total_investment_netto', 0.0))
    if is_private:
        if brutto > 0.0 and netto > 0.0:
            return max(0.0, brutto - netto)
        if netto > 0.0:
            return max(0.0, netto * 0.19)
    return max(0.0, brutto - netto) if (brutto > 0.0 and netto > 0.0) else 0.0


"""PV-Anlagengröße (kWp)"""


def calc_pv_system_size_kwp(results: Dict[str, Any]) -> float:
    """
    PV-Anlagengröße in kWp (nutzt 'anlage_kwp' oder berechnet aus Moduldaten).
    """
    kwp = float(results.get('anlage_kwp', 0.0))
    if kwp > 0.0:
        return kwp
    qty = float(results.get('module_quantity', 0.0))
    wp = float(results.get('module_power_wp', 0.0))
    return max(0.0, (qty * wp) / 1000.0)


"""Netzbezug (kWh)"""


def calc_grid_purchase_kwh(
        results: Dict[str, Any], days_per_year: int = 365) -> float:
    """
    Netzbezug in kWh/Jahr (nach Direkt- und Speichernutzung).
    """
    cons = max(0.0, float(results.get('annual_consumption_kwh', 0.0)))
    direct = calc_direct_consumption_kwh(results)
    discharge = calc_battery_discharge_kwh(
        results, days_per_year=days_per_year)
    return max(0.0, cons - direct - discharge)


"""Stromkosten kumuliert (ohne PV) – mit/ohne Erhöhung (10/20 Jahre)"""


def calc_cumulative_grid_costs_with_increase(
        results: Dict[str, Any], years: int) -> float:
    """
    Kumulierte Stromkosten mit jährlicher Preissteigerung (ohne PV), €.
    """
    base = float(results.get('monthly_electricity_cost', 0.0)) * 12.0
    r = float(
        results.get(
            'electricity_price_increase_rate_effective_percent',
            0.0)) / 100.0
    total = 0.0
    for y in range(years):
        total += base * ((1.0 + r) ** y)
    return max(0.0, total)


def calc_cumulative_grid_costs_no_increase(
        results: Dict[str, Any], years: int) -> float:
    """
    Kumulierte Stromkosten ohne Preissteigerung (ohne PV), €.
    """
    base = float(results.get('monthly_electricity_cost', 0.0)) * 12.0
    return max(0.0, base * float(years))

# c10_inc = calc_cumulative_grid_costs_with_increase(results, 10)
# c10_flat = calc_cumulative_grid_costs_no_increase(results, 10)
# c20_inc = calc_cumulative_grid_costs_with_increase(results, 20)
# c20_flat = calc_cumulative_grid_costs_no_increase(results, 20)


"""
Importe erweitern
"""

"""
Berechnungen vor Rückgabe
"""

# Zusätzliche Kennzahlen (Formel-Bibliothek)
_direct = calc_direct_consumption_kwh(results)
_charge = calc_battery_charge_kwh(results)
_discharge = calc_battery_discharge_kwh(results)
_surplus_batt = calc_battery_surplus_kwh(results)
_feed_in = calc_grid_feed_in_kwh(results)
_feed_in_rev = calc_feed_in_revenue_eur(results)
_save_storage = calc_savings_from_storage_usage_eur(results)
_rev_batt_surplus = calc_revenue_from_battery_surplus_eur(results)
_save_direct = calc_savings_from_direct_consumption_eur(results)
_vat_saved = calc_vat_saved_eur(results)
_kwp = calc_pv_system_size_kwp(results)
_grid_bezug = calc_grid_purchase_kwh(results)
_c10_inc = calc_cumulative_grid_costs_with_increase(results, 10)
_c10_flat = calc_cumulative_grid_costs_no_increase(results, 10)
_c20_inc = calc_cumulative_grid_costs_with_increase(results, 20)
_c20_flat = calc_cumulative_grid_costs_no_increase(results, 20)

"""
Rückgabe-Dict erweitern
"""
'grid_feed_in_kwh': _feed_in,
'grid_bezug_kwh': _grid_bezug,
'savings_from_direct_consumption_eur': _save_direct,
'savings_from_battery_usage_eur': _save_storage,
'revenue_from_battery_surplus_eur': _rev_batt_surplus,
'feed_in_revenue_eur': _feed_in_rev,
'battery_surplus_kwh': _surplus_batt,
'pv_system_size_kwp': _kwp,
'cumulative_grid_costs_10y_with_increase_eur': _c10_inc,
'cumulative_grid_costs_10y_no_increase_eur': _c10_flat,
'cumulative_grid_costs_20y_with_increase_eur': _c20_inc,
'cumulative_grid_costs_20y_no_increase_eur': _c20_flat,
'vat_saved_eur': _vat_saved,
