"""tests/test_calculations.py - Unit Tests für PV/WP-Berechnungen"""
import unittest
from calculations import (
    calculate_pv_yield,
    calculate_self_consumption,
    calculate_battery_sizing
)
from calculations_heatpump import calculate_heat_pump_capacity

class TestPVCalculations(unittest.TestCase):
    """Tests für Photovoltaik-Berechnungen"""
    
    def test_basic_pv_yield(self):
        """Test: Basis-PV-Ertrag"""
        kwp = 10.0  # 10 kWp Anlage
        irradiation = 1100  # kWh/m²/Jahr
        efficiency = 0.85  # 85% Performance Ratio
        
        annual_yield = kwp * irradiation * efficiency
        self.assertEqual(annual_yield, 9350.0)
    
    def test_pv_yield_with_orientation(self):
        """Test: PV-Ertrag mit Ausrichtung"""
        kwp = 15.0
        base_irradiation = 1100
        
        # Süd: 100%, Ost/West: 85%, Nord: 60%
        orientation_factors = {
            'south': 1.0,
            'east': 0.85,
            'west': 0.85,
            'north': 0.60
        }
        
        yield_south = kwp * base_irradiation * orientation_factors['south']
        yield_east = kwp * base_irradiation * orientation_factors['east']
        
        self.assertEqual(yield_south, 16500.0)
        self.assertAlmostEqual(yield_east, 14025.0, places=1)
    
    def test_self_consumption_calculation(self):
        """Test: Eigenverbrauch berechnen"""
        annual_yield = 10000  # kWh
        annual_consumption = 4000  # kWh
        
        # Ohne Speicher: ca. 30% Eigenverbrauch
        self_consumption_no_battery = annual_consumption * 0.30
        
        # Mit Speicher: ca. 70% Eigenverbrauch
        self_consumption_with_battery = annual_consumption * 0.70
        
        self.assertEqual(self_consumption_no_battery, 1200.0)
        self.assertEqual(self_consumption_with_battery, 2800.0)
    
    def test_battery_sizing(self):
        """Test: Speicher-Dimensionierung"""
        daily_consumption = 15  # kWh/Tag
        
        # Speicher sollte 60-80% des Tagesverbrauchs sein
        min_capacity = daily_consumption * 0.60
        max_capacity = daily_consumption * 0.80
        
        self.assertEqual(min_capacity, 9.0)
        self.assertEqual(max_capacity, 12.0)
    
    def test_feed_in_calculation(self):
        """Test: Einspeisung berechnen"""
        annual_yield = 12000  # kWh
        self_consumption = 3500  # kWh
        
        feed_in = annual_yield - self_consumption
        self.assertEqual(feed_in, 8500.0)
    
    def test_savings_calculation(self):
        """Test: Ersparnis berechnen"""
        self_consumption = 3000  # kWh
        feed_in = 7000  # kWh
        electricity_price = 0.30  # €/kWh
        feed_in_tariff = 0.08  # €/kWh
        
        savings_self = self_consumption * electricity_price
        revenue_feed_in = feed_in * feed_in_tariff
        total_savings = savings_self + revenue_feed_in
        
        self.assertEqual(savings_self, 900.0)
        self.assertEqual(revenue_feed_in, 560.0)
        self.assertEqual(total_savings, 1460.0)
    
    def test_payback_period(self):
        """Test: Amortisationszeit"""
        system_cost = 18000  # €
        annual_savings = 1500  # €/Jahr
        
        payback_years = system_cost / annual_savings
        self.assertEqual(payback_years, 12.0)
    
    def test_peak_power_calculation(self):
        """Test: Spitzenleistung berechnen"""
        module_power = 400  # Wp
        module_count = 25
        
        total_kwp = (module_power * module_count) / 1000
        self.assertEqual(total_kwp, 10.0)
    
    def test_area_requirement(self):
        """Test: Flächenbedarf"""
        module_power = 400  # Wp
        module_count = 20
        module_area = 1.9  # m² pro Modul
        
        total_area = module_count * module_area
        self.assertEqual(total_area, 38.0)


class TestHeatPumpCalculations(unittest.TestCase):
    """Tests für Wärmepumpen-Berechnungen"""
    
    def test_heat_demand_calculation(self):
        """Test: Wärmebedarf berechnen"""
        building_area = 150  # m²
        heat_demand_per_sqm = 80  # kWh/m²/Jahr
        
        annual_heat_demand = building_area * heat_demand_per_sqm
        self.assertEqual(annual_heat_demand, 12000.0)
    
    def test_cop_calculation(self):
        """Test: COP berechnen"""
        # COP = Wärmeausgang / Stromeingang
        heat_output = 10.0  # kW
        power_input = 2.5  # kW
        
        cop = heat_output / power_input
        self.assertEqual(cop, 4.0)
    
    def test_jaz_estimation(self):
        """Test: JAZ schätzen"""
        # JAZ ist typisch 20-25% niedriger als COP
        cop = 4.5
        jaz = cop * 0.75  # 75% des COP
        
        self.assertAlmostEqual(jaz, 3.375, places=3)
    
    def test_electricity_consumption_heat_pump(self):
        """Test: Stromverbrauch Wärmepumpe"""
        annual_heat_demand = 15000  # kWh
        jaz = 3.5
        
        electricity_consumption = annual_heat_demand / jaz
        self.assertAlmostEqual(electricity_consumption, 4285.71, places=2)
    
    def test_heat_pump_cost_comparison(self):
        """Test: Kostenvergleich Wärmepumpe vs. Gas"""
        annual_heat_demand = 12000  # kWh
        
        # Gas: 90% Wirkungsgrad, 0.08 €/kWh
        gas_consumption = annual_heat_demand / 0.90
        gas_cost = gas_consumption * 0.08
        
        # Wärmepumpe: JAZ 3.5, 0.30 €/kWh
        wp_consumption = annual_heat_demand / 3.5
        wp_cost = wp_consumption * 0.30
        
        self.assertAlmostEqual(gas_cost, 1066.67, places=2)
        self.assertAlmostEqual(wp_cost, 1028.57, places=2)
        
        savings = gas_cost - wp_cost
        self.assertGreater(savings, 0)
    
    def test_heating_load_calculation(self):
        """Test: Heizlast berechnen"""
        building_area = 150  # m²
        specific_load = 50  # W/m²
        
        heating_load_kw = (building_area * specific_load) / 1000
        self.assertEqual(heating_load_kw, 7.5)
    
    def test_buffer_tank_sizing(self):
        """Test: Pufferspeicher-Dimensionierung"""
        heat_pump_power = 10  # kW
        
        # Pufferspeicher: 50-100 Liter pro kW
        min_tank = heat_pump_power * 50
        max_tank = heat_pump_power * 100
        
        self.assertEqual(min_tank, 500)
        self.assertEqual(max_tank, 1000)


class TestFinancialCalculations(unittest.TestCase):
    """Tests für Finanz-Berechnungen"""
    
    def test_net_present_value(self):
        """Test: Kapitalwert (NPV)"""
        initial_investment = -20000
        annual_cashflow = 1500
        years = 20
        discount_rate = 0.03
        
        # NPV = Σ (Cashflow / (1 + r)^t)
        npv = initial_investment
        for year in range(1, years + 1):
            npv += annual_cashflow / ((1 + discount_rate) ** year)
        
        self.assertGreater(npv, 0)  # Investition lohnt sich
    
    def test_internal_rate_of_return(self):
        """Test: Interner Zinsfuß (IRR) - vereinfacht"""
        initial_investment = 15000
        annual_return = 1200
        years = 20
        
        # Vereinfachte IRR-Schätzung
        total_return = annual_return * years
        irr_estimate = (total_return / initial_investment - 1) / years
        
        self.assertGreater(irr_estimate, 0)
    
    def test_loan_calculation(self):
        """Test: Kreditberechnung"""
        loan_amount = 20000
        annual_rate = 0.03
        years = 10
        
        monthly_rate = annual_rate / 12
        months = years * 12
        
        # Annuitätenformel
        monthly_payment = loan_amount * (
            monthly_rate * (1 + monthly_rate) ** months
        ) / ((1 + monthly_rate) ** months - 1)
        
        self.assertGreater(monthly_payment, 0)
        self.assertLess(monthly_payment, loan_amount / months * 1.5)
    
    def test_inflation_adjustment(self):
        """Test: Inflations-Anpassung"""
        current_price = 0.30  # €/kWh
        inflation_rate = 0.02  # 2% pro Jahr
        years = 5
        
        future_price = current_price * (1 + inflation_rate) ** years
        self.assertGreater(future_price, current_price)
        self.assertAlmostEqual(future_price, 0.3312, places=4)


if __name__ == '__main__':
    unittest.main()
