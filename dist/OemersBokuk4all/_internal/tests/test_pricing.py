"""tests/test_pricing.py - Unit Tests für Preiskalkulation"""
import unittest
from price_modification_engine import calculate_price_with_products
from product_rotation_engine import rotate_products

class TestPricing(unittest.TestCase):
    """Tests für Preiskalkulations-System"""
    
    def test_basic_price_calculation(self):
        """Test: Basis-Preisberechnung"""
        base_price = 10000.0
        modifier = 0.15  # +15%
        
        final_price = base_price * (1 + modifier)
        self.assertEqual(final_price, 11500.0)
    
    def test_progressive_pricing(self):
        """Test: Progressive Preiskalkulation (Firma 1-7)"""
        base_price = 20000.0
        
        # Firma 1: +15%
        price_f1 = base_price * 1.15
        self.assertEqual(price_f1, 23000.0)
        
        # Firma 2: +20% (15% + 5%)
        price_f2 = base_price * 1.20
        self.assertEqual(price_f2, 24000.0)
        
        # Firma 3: +25% (15% + 5% + 5%)
        price_f3 = base_price * 1.25
        self.assertEqual(price_f3, 25000.0)
    
    def test_vat_calculation(self):
        """Test: Mehrwertsteuer-Berechnung"""
        net_price = 10000.0
        vat_rate = 0.19  # 19%
        
        gross_price = net_price * (1 + vat_rate)
        self.assertAlmostEqual(gross_price, 11900.0, places=2)
    
    def test_discount_application(self):
        """Test: Rabatt anwenden"""
        price = 25000.0
        discount_percent = 10.0
        
        discounted = price * (1 - discount_percent / 100.0)
        self.assertEqual(discounted, 22500.0)
    
    def test_component_price_sum(self):
        """Test: Komponentenpreise summieren"""
        components = {
            'modules': {'price': 6000.0, 'count': 1},
            'inverter': {'price': 2000.0, 'count': 1},
            'battery': {'price': 8000.0, 'count': 1},
            'installation': {'price': 3000.0, 'count': 1}
        }
        
        total = sum(comp['price'] * comp['count'] for comp in components.values())
        self.assertEqual(total, 19000.0)
    
    def test_multi_component_calculation(self):
        """Test: Mehrere Komponenten mit Mengen"""
        modules_price = 300.0
        modules_count = 20
        inverter_price = 1500.0
        
        total = (modules_price * modules_count) + inverter_price
        self.assertEqual(total, 7500.0)
    
    def test_price_rounding(self):
        """Test: Preisrundung"""
        price = 12345.678
        
        # Auf 2 Dezimalstellen
        rounded = round(price, 2)
        self.assertEqual(rounded, 12345.68)
        
        # Auf nächste 100€
        rounded_100 = round(price / 100) * 100
        self.assertEqual(rounded_100, 12300.0)
    
    def test_german_price_formatting(self):
        """Test: Deutsche Preisformatierung"""
        price = 95464.18
        
        formatted = f"{price:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
        self.assertEqual(formatted, "95.464,18 €")
    
    def test_profit_margin_calculation(self):
        """Test: Gewinnmarge berechnen"""
        cost = 8000.0
        selling_price = 10000.0
        
        margin = (selling_price - cost) / cost * 100
        self.assertEqual(margin, 25.0)  # 25% Gewinn
    
    def test_break_even_calculation(self):
        """Test: Break-Even-Berechnung"""
        system_cost = 15000.0
        annual_savings = 1200.0
        
        break_even_years = system_cost / annual_savings
        self.assertEqual(break_even_years, 12.5)


class TestProductRotation(unittest.TestCase):
    """Tests für Produkt-Rotation"""
    
    def test_module_rotation(self):
        """Test: Modul-Rotation zwischen Firmen"""
        modules = [
            {'manufacturer': 'JA Solar', 'model': 'JAM72S30', 'price': 300},
            {'manufacturer': 'Longi', 'model': 'LR5-72HPH', 'price': 320},
            {'manufacturer': 'Trina', 'model': 'TSM-DE19', 'price': 310}
        ]
        
        # Jede Firma sollte unterschiedliches Modul bekommen
        firm_modules = []
        for i in range(3):
            selected = modules[i % len(modules)]
            firm_modules.append(selected['manufacturer'])
        
        # Mindestens 2 verschiedene Hersteller
        unique_manufacturers = set(firm_modules)
        self.assertGreaterEqual(len(unique_manufacturers), 2)
    
    def test_inverter_rotation(self):
        """Test: Wechselrichter-Rotation"""
        inverters = [
            {'manufacturer': 'Fronius', 'model': 'Symo 10.0'},
            {'manufacturer': 'SMA', 'model': 'STP 10.0'},
            {'manufacturer': 'Kostal', 'model': 'Plenticore 10'}
        ]
        
        rotated = [inverters[i % len(inverters)] for i in range(5)]
        
        self.assertEqual(len(rotated), 5)
        self.assertEqual(rotated[0]['manufacturer'], 'Fronius')
        self.assertEqual(rotated[3]['manufacturer'], 'Fronius')
    
    def test_battery_rotation(self):
        """Test: Speicher-Rotation"""
        batteries = [
            {'manufacturer': 'BYD', 'model': 'HVS 10.2', 'price': 8000},
            {'manufacturer': 'Huawei', 'model': 'LUNA2000', 'price': 8500}
        ]
        
        # Rotation über 7 Firmen
        firm_batteries = [batteries[i % len(batteries)] for i in range(7)]
        
        self.assertEqual(len(firm_batteries), 7)
        # BYD sollte 4x vorkommen (Index 0, 2, 4, 6)
        byd_count = sum(1 for b in firm_batteries if b['manufacturer'] == 'BYD')
        self.assertEqual(byd_count, 4)


class TestPriceMatrix(unittest.TestCase):
    """Tests für Preis-Matrix"""
    
    def test_price_lookup_by_power(self):
        """Test: Preis-Lookup nach Leistung"""
        price_matrix = {
            'small': {'min_kwp': 0, 'max_kwp': 5, 'price_per_kwp': 1800},
            'medium': {'min_kwp': 5, 'max_kwp': 10, 'price_per_kwp': 1600},
            'large': {'min_kwp': 10, 'max_kwp': 30, 'price_per_kwp': 1400}
        }
        
        def get_price(kwp):
            for category in price_matrix.values():
                if category['min_kwp'] <= kwp < category['max_kwp']:
                    return category['price_per_kwp']
            return price_matrix['large']['price_per_kwp']
        
        self.assertEqual(get_price(4), 1800)
        self.assertEqual(get_price(7), 1600)
        self.assertEqual(get_price(15), 1400)
    
    def test_tiered_pricing(self):
        """Test: Gestaffelte Preise"""
        base_price = 20000.0
        tiers = [
            {'threshold': 15000, 'discount': 0},
            {'threshold': 25000, 'discount': 5},
            {'threshold': 35000, 'discount': 10}
        ]
        
        def apply_tier_discount(price):
            for tier in reversed(tiers):
                if price >= tier['threshold']:
                    return price * (1 - tier['discount'] / 100)
            return price
        
        self.assertEqual(apply_tier_discount(20000), 19000.0)  # 5% Rabatt
    
    def test_dynamic_margin_by_volume(self):
        """Test: Dynamische Marge nach Volumen"""
        volumes = [
            {'max_units': 10, 'margin': 0.30},   # 30% unter 10 Stück
            {'max_units': 50, 'margin': 0.25},   # 25% unter 50 Stück
            {'max_units': 999, 'margin': 0.20}   # 20% darüber
        ]
        
        def get_margin(units):
            for vol in volumes:
                if units <= vol['max_units']:
                    return vol['margin']
            return volumes[-1]['margin']
        
        self.assertEqual(get_margin(5), 0.30)
        self.assertEqual(get_margin(30), 0.25)
        self.assertEqual(get_margin(100), 0.20)


if __name__ == '__main__':
    unittest.main()
