"""
PV Module Service

Provides PV module selection, specifications, and calculations.
Integrates with product database for manufacturer/model selection.

Requirements: funktionen.txt - "PV-Module"
"""

import sys
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

logger = logging.getLogger(__name__)


@dataclass
class PVModuleSpec:
    """PV Module Specification"""
    id: int
    manufacturer: str
    model: str
    power_wp: int  # Watt peak
    efficiency: float  # Percentage (e.g., 21.5)
    width_mm: int  # Width in mm
    height_mm: int  # Height in mm
    weight_kg: float
    cell_type: str  # Mono, Poly, Bifacial
    warranty_years: int
    price_net: float
    price_gross: float
    datasheet_url: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None


class PVModuleService:
    """
    PV Module Service for module selection and calculations.
    """
    
    # Standard module dimensions for calculations
    STANDARD_MODULE_WIDTH_M = 1.05
    STANDARD_MODULE_HEIGHT_M = 1.76
    
    def __init__(self, database_path: str = "product_database.db"):
        """Initialize PV Module Service."""
        self.database_path = database_path
        self._init_database()
        logger.info("PV Module Service initialized")
    
    def _init_database(self):
        """Initialize database tables."""
        try:
            import sqlite3
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pv_modules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    manufacturer TEXT NOT NULL,
                    model TEXT NOT NULL,
                    power_wp INTEGER NOT NULL,
                    efficiency REAL NOT NULL,
                    width_mm INTEGER NOT NULL,
                    height_mm INTEGER NOT NULL,
                    weight_kg REAL NOT NULL,
                    cell_type TEXT NOT NULL,
                    warranty_years INTEGER DEFAULT 25,
                    price_net REAL NOT NULL,
                    price_gross REAL NOT NULL,
                    datasheet_url TEXT,
                    image_url TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(manufacturer, model)
                )
            ''')
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_pv_manufacturer ON pv_modules(manufacturer)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_pv_power ON pv_modules(power_wp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_pv_active ON pv_modules(is_active)')
            
            # Insert sample data if empty
            cursor.execute('SELECT COUNT(*) FROM pv_modules')
            if cursor.fetchone()[0] == 0:
                self._insert_sample_modules(cursor)
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    def _insert_sample_modules(self, cursor):
        """Insert sample PV modules."""
        sample_modules = [
            ('Trina Solar', 'Vertex S+ TSM-440NEG9R.28', 440, 22.0, 1096, 1754, 21.0, 'Mono N-Type', 30, 180.00, 214.20),
            ('Trina Solar', 'Vertex S TSM-425DE09R.08', 425, 21.3, 1096, 1754, 21.5, 'Mono PERC', 25, 165.00, 196.35),
            ('JA Solar', 'JAM54S30-415/MR', 415, 21.0, 1096, 1722, 21.0, 'Mono PERC', 25, 155.00, 184.45),
            ('JA Solar', 'JAM72S30-545/MR', 545, 21.2, 1134, 2278, 28.5, 'Mono PERC', 25, 210.00, 249.90),
            ('Longi', 'Hi-MO 5 LR5-54HTH-430M', 430, 21.5, 1096, 1754, 21.0, 'Mono PERC', 25, 170.00, 202.30),
            ('Longi', 'Hi-MO 6 LR5-72HTH-570M', 570, 22.3, 1134, 2278, 28.0, 'Mono N-Type', 30, 235.00, 279.65),
            ('Canadian Solar', 'HiKu6 CS6R-420MS', 420, 21.0, 1096, 1754, 21.5, 'Mono PERC', 25, 160.00, 190.40),
            ('Canadian Solar', 'HiKu7 CS7N-665TB-AG', 665, 21.8, 1303, 2384, 34.4, 'Bifacial', 30, 280.00, 333.20),
            ('Jinko Solar', 'Tiger Neo N-type JKM440N-54HL4R-V', 440, 22.02, 1096, 1754, 21.0, 'Mono N-Type', 30, 175.00, 208.25),
            ('Jinko Solar', 'Tiger Pro JKM545M-72HL4-V', 545, 21.13, 1134, 2278, 28.0, 'Mono PERC', 25, 205.00, 243.95),
            ('Meyer Burger', 'White 395', 395, 21.7, 1048, 1767, 19.5, 'Heterojunction', 30, 250.00, 297.50),
            ('SunPower', 'Maxeon 6 AC', 440, 22.8, 1046, 1690, 19.0, 'IBC', 40, 350.00, 416.50),
            ('REC', 'Alpha Pure-R 430', 430, 22.3, 1016, 1821, 19.5, 'Heterojunction', 25, 220.00, 261.80),
            ('Q CELLS', 'Q.PEAK DUO ML-G11S+ 410', 410, 20.6, 1096, 1754, 21.0, 'Mono PERC', 25, 165.00, 196.35),
            ('Solarwatt', 'Panel vision AM 4.0 pure 420', 420, 21.5, 1096, 1754, 21.0, 'Mono PERC', 30, 195.00, 232.05),
        ]
        
        for module in sample_modules:
            cursor.execute('''
                INSERT INTO pv_modules (manufacturer, model, power_wp, efficiency, width_mm, height_mm,
                                       weight_kg, cell_type, warranty_years, price_net, price_gross)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', module)
    
    # ==================== Module CRUD ====================
    
    def get_module(self, module_id: int) -> Optional[PVModuleSpec]:
        """Get module by ID."""
        try:
            import sqlite3
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM pv_modules WHERE id = ?', (module_id))
            row = cursor.fetchone()
            conn.close()
            return self._row_to_spec(row) if row else None
        except Exception as e:
            logger.error(f"Error getting module: {e}")
            raise
    
    def get_all_modules(self, active_only: bool = True) -> List[PVModuleSpec]:
        """Get all modules."""
        try:
            import sqlite3
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            sql = 'SELECT * FROM pv_modules'
            if active_only:
                sql += ' WHERE is_active = 1'
            sql += ' ORDER BY manufacturer, power_wp DESC'
            
            cursor.execute(sql)
            rows = cursor.fetchall()
            conn.close()
            return [self._row_to_spec(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting modules: {e}")
            raise
    
    def get_manufacturers(self) -> List[str]:
        """Get list of all manufacturers."""
        try:
            import sqlite3
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT manufacturer FROM pv_modules WHERE is_active = 1 ORDER BY manufacturer')
            manufacturers = [row[0] for row in cursor.fetchall()]
            conn.close()
            return manufacturers
        except Exception as e:
            logger.error(f"Error getting manufacturers: {e}")
            raise
    
    def get_modules_by_manufacturer(self, manufacturer: str) -> List[PVModuleSpec]:
        """Get modules by manufacturer."""
        try:
            import sqlite3
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM pv_modules 
                WHERE manufacturer = ? AND is_active = 1 
                ORDER BY power_wp DESC
            ''', (manufacturer))
            rows = cursor.fetchall()
            conn.close()
            return [self._row_to_spec(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting modules by manufacturer: {e}")
            raise
    
    # ==================== Calculations ====================
    
    def calculate_system_power(self, module_id: int, module_count: int) -> Dict[str, Any]:
        """
        Calculate total system power from module count.
        
        Args:
            module_id: PV module ID
            module_count: Number of modules
            
        Returns:
            Dictionary with system power calculations
        """
        module = self.get_module(module_id)
        if not module:
            raise ValueError(f"Module {module_id} not found")
        
        total_wp = module.power_wp * module_count
        total_kwp = total_wp / 1000
        
        # Calculate area
        module_area_m2 = (module.width_mm / 1000) * (module.height_mm / 1000)
        total_area_m2 = module_area_m2 * module_count
        
        # Calculate weight
        total_weight_kg = module.weight_kg * module_count
        
        # Calculate price
        total_price_net = module.price_net * module_count
        total_price_gross = module.price_gross * module_count
        
        return {
            'module': {
                'id': module.id,
                'manufacturer': module.manufacturer,
                'model': module.model,
                'power_wp': module.power_wp,
                'efficiency': module.efficiency
            },
            'module_count': module_count,
            'total_power_wp': total_wp,
            'total_power_kwp': round(total_kwp, 2),
            'module_area_m2': round(module_area_m2, 2),
            'total_area_m2': round(total_area_m2, 2),
            'total_weight_kg': round(total_weight_kg, 1),
            'price_net': round(total_price_net, 2),
            'price_gross': round(total_price_gross, 2),
            'price_per_kwp_net': round(total_price_net / total_kwp, 2) if total_kwp > 0 else 0
        }
    
    def recommend_modules_for_roof(self, roof_area_m2: float, target_kwp: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Recommend modules based on roof size and optional target power.
        
        Args:
            roof_area_m2: Available roof area in m²
            target_kwp: Optional target system size in kWp
            
        Returns:
            List of recommendations with module counts
        """
        modules = self.get_all_modules(active_only=True)
        recommendations = []
        
        for module in modules:
            module_area = (module.width_mm / 1000) * (module.height_mm / 1000)
            
            # Calculate max modules that fit (with 10% spacing factor)
            usable_area = roof_area_m2 * 0.9
            max_modules = int(usable_area / module_area)
            
            if max_modules < 1:
                continue
            
            # Calculate optimal module count
            if target_kwp:
                optimal_count = int((target_kwp * 1000) / module.power_wp)
                optimal_count = min(optimal_count, max_modules)
            else:
                optimal_count = max_modules
            
            if optimal_count < 1:
                continue
            
            total_kwp = (module.power_wp * optimal_count) / 1000
            total_price = module.price_gross * optimal_count
            
            recommendations.append({
                'module': {
                    'id': module.id,
                    'manufacturer': module.manufacturer,
                    'model': module.model,
                    'power_wp': module.power_wp,
                    'efficiency': module.efficiency,
                    'cell_type': module.cell_type
                },
                'recommended_count': optimal_count,
                'max_count': max_modules,
                'total_kwp': round(total_kwp, 2),
                'total_price_gross': round(total_price, 2),
                'price_per_kwp': round(total_price / total_kwp, 2) if total_kwp > 0 else 0,
                'roof_utilization': round((optimal_count * module_area / roof_area_m2) * 100, 1)
            })
        
        # Sort by efficiency (best first)
        recommendations.sort(key=lambda x: x['module']['efficiency'], reverse=True)
        return recommendations[:10]  # Top 10 recommendations
    
    def compare_modules(self, module_ids: List[int]) -> Dict[str, Any]:
        """
        Compare multiple modules side by side.
        
        Args:
            module_ids: List of module IDs to compare
            
        Returns:
            Comparison data
        """
        modules = []
        for mid in module_ids:
            module = self.get_module(mid)
            if module:
                modules.append({
                    'id': module.id,
                    'manufacturer': module.manufacturer,
                    'model': module.model,
                    'power_wp': module.power_wp,
                    'efficiency': module.efficiency,
                    'dimensions': f"{module.width_mm}x{module.height_mm} mm",
                    'weight_kg': module.weight_kg,
                    'cell_type': module.cell_type,
                    'warranty_years': module.warranty_years,
                    'price_net': module.price_net,
                    'price_gross': module.price_gross,
                    'price_per_wp': round(module.price_gross / module.power_wp, 3)
                })
        
        if not modules:
            return {'modules': [], 'best': {}}
        
        # Find best in each category
        best = {
            'highest_power': max(modules, key=lambda x: x['power_wp'])['id'],
            'highest_efficiency': max(modules, key=lambda x: x['efficiency'])['id'],
            'lowest_price': min(modules, key=lambda x: x['price_gross'])['id'],
            'best_value': min(modules, key=lambda x: x['price_per_wp'])['id'],
            'longest_warranty': max(modules, key=lambda x: x['warranty_years'])['id'],
            'lightest': min(modules, key=lambda x: x['weight_kg'])['id']
        }
        
        return {'modules': modules, 'best': best}
    
    def estimate_annual_yield(self, module_id: int, module_count: int, 
                              location_factor: float = 1000, 
                              orientation_factor: float = 1.0) -> Dict[str, Any]:
        """
        Estimate annual energy yield.
        
        Args:
            module_id: PV module ID
            module_count: Number of modules
            location_factor: kWh/kWp/year for location (default: 1000 for Germany)
            orientation_factor: Factor for roof orientation (0.7-1.0)
            
        Returns:
            Yield estimation
        """
        system = self.calculate_system_power(module_id, module_count)
        
        annual_yield_kwh = system['total_power_kwp'] * location_factor * orientation_factor
        
        # Degradation over 25 years (0.5% per year)
        yields_over_time = []
        for year in range(1, 26):
            degradation = 1 - (0.005 * (year - 1))
            yields_over_time.append({
                'year': year,
                'yield_kwh': round(annual_yield_kwh * degradation, 0),
                'degradation_percent': round((1 - degradation) * 100, 1)
            })
        
        total_25_years = sum(y['yield_kwh'] for y in yields_over_time)
        
        return {
            'system_kwp': system['total_power_kwp'],
            'location_factor': location_factor,
            'orientation_factor': orientation_factor,
            'first_year_yield_kwh': round(annual_yield_kwh, 0),
            'total_25_years_kwh': round(total_25_years, 0),
            'average_annual_kwh': round(total_25_years / 25, 0),
            'yields_by_year': yields_over_time
        }
    
    # ==================== Helper Methods ====================
    
    def _row_to_spec(self, row) -> PVModuleSpec:
        """Convert database row to PVModuleSpec."""
        return PVModuleSpec(
            id=row['id'],
            manufacturer=row['manufacturer'],
            model=row['model'],
            power_wp=row['power_wp'],
            efficiency=row['efficiency'],
            width_mm=row['width_mm'],
            height_mm=row['height_mm'],
            weight_kg=row['weight_kg'],
            cell_type=row['cell_type'],
            warranty_years=row['warranty_years'],
            price_net=row['price_net'],
            price_gross=row['price_gross'],
            datasheet_url=row['datasheet_url'],
            image_url=row['image_url'],
            is_active=bool(row['is_active']),
            created_at=row['created_at']
        )
    
    def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        try:
            import sqlite3
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM pv_modules WHERE is_active = 1')
            count = cursor.fetchone()[0]
            conn.close()
            return {'status': 'healthy', 'active_modules': count}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}


# Singleton instance
pv_module_service = PVModuleService()
