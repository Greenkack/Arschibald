"""
Solar Inverter Management Service

This service handles all inverter-related operations including:
- Inverter data extraction and management
- Inverter selection algorithms
- Inverter sizing calculations
- Compatibility checks
- Multi-inverter configurations
- Monitoring integration

Requirements: 1.3, 6.1
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import math

logger = logging.getLogger(__name__)


class InverterSpecs:
    """Inverter specifications for matching and sizing"""
    
    def __init__(
        self,
        power_kw: float,
        efficiency_percent: float = 97.0,
        max_dc_voltage: float = 1000.0,
        mppt_count: int = 2,
        max_dc_current: float = 30.0,
        manufacturer: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.power_kw = power_kw
        self.efficiency_percent = efficiency_percent
        self.max_dc_voltage = max_dc_voltage
        self.mppt_count = mppt_count
        self.max_dc_current = max_dc_current
        self.manufacturer = manufacturer
        self.model = model


class InverterService:
    """Service for managing solar inverters"""
    
    def __init__(self, db_connection=None):
        """
        Initialize inverter service
        
        Args:
            db_connection: Database connection for product queries
        """
        self.db_connection = db_connection
        self.logger = logger
    
    def extract_inverter_data(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and normalize inverter data from product database
        
        Args:
            product_data: Raw product data from database
            
        Returns:
            Normalized inverter data dictionary
        """
        try:
            inverter_data = {
                'id': product_data.get('id'),
                'model_name': product_data.get('model_name', ''),
                'manufacturer': product_data.get('brand', product_data.get('manufacturer', '')),
                'power_kw': float(product_data.get('power_kw', 0.0) or 0.0),
                'efficiency_percent': float(product_data.get('efficiency_percent', 97.0) or 97.0),
                'max_dc_voltage': float(product_data.get('max_dc_voltage', 1000.0) or 1000.0),
                'mppt_count': int(product_data.get('mppt_count', 2) or 2),
                'max_dc_current': float(product_data.get('max_dc_current', 30.0) or 30.0),
                'price_netto': float(product_data.get('price_euro', 0.0) or 0.0),
                'additional_cost_netto': float(product_data.get('additional_cost_netto', 0.0) or 0.0),
                'warranty_years': int(product_data.get('warranty_years', 10) or 10),
                'weight_kg': float(product_data.get('weight_kg', 0.0) or 0.0),
                'description': product_data.get('description', ''),
                'technology': product_data.get('technology', ''),
                'features': self._extract_features(product_data),
                'created_at': product_data.get('created_at', datetime.now().isoformat()),
                'updated_at': product_data.get('updated_at', datetime.now().isoformat())
            }
            
            self.logger.info(f"Extracted inverter data for {inverter_data['model_name']}")
            return inverter_data
            
        except Exception as e:
            self.logger.error(f"Error extracting inverter data: {e}")
            raise
    
    def _extract_features(self, product_data: Dict[str, Any]) -> List[str]:
        """Extract inverter features from product data"""
        features = []
        
        # Check for common features
        if product_data.get('smart_home'):
            features.append('Smart Home Integration')
        if product_data.get('shadow_fading'):
            features.append('Shadow Management')
        if product_data.get('outdoor_opt'):
            features.append('Outdoor Optimized')
        
        # Add technology-based features
        tech = product_data.get('technology', '')
        if 'hybrid' in tech.lower():
            features.append('Hybrid Capable')
        if 'battery' in tech.lower():
            features.append('Battery Ready')
        
        return features
    
    def select_inverter(
        self,
        pv_power_kwp: float,
        system_voltage: float = 400.0,
        available_inverters: Optional[List[Dict[str, Any]]] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Select optimal inverter based on PV system specifications
        
        Args:
            pv_power_kwp: PV system power in kWp
            system_voltage: System voltage (default 400V)
            available_inverters: List of available inverters
            preferences: User preferences (manufacturer, features, etc.)
            
        Returns:
            Selected inverter with selection reasoning
        """
        try:
            if not available_inverters:
                available_inverters = self._get_available_inverters()
            
            if not available_inverters:
                raise ValueError("No inverters available for selection")
            
            # Calculate optimal inverter size (typically 0.8-1.0 of PV power)
            optimal_power_kw = pv_power_kwp * 0.9
            min_power_kw = pv_power_kwp * 0.8
            max_power_kw = pv_power_kwp * 1.0
            
            # Score each inverter
            scored_inverters = []
            for inverter in available_inverters:
                score = self._score_inverter(
                    inverter,
                    optimal_power_kw,
                    min_power_kw,
                    max_power_kw,
                    preferences or {}
                )
                scored_inverters.append((score, inverter))
            
            # Sort by score (highest first)
            scored_inverters.sort(key=lambda x: x[0], reverse=True)
            
            best_inverter = scored_inverters[0][1]
            best_score = scored_inverters[0][0]
            
            result = {
                'selected_inverter': self.extract_inverter_data(best_inverter),
                'selection_score': best_score,
                'sizing_ratio': pv_power_kwp / best_inverter['power_kw'],
                'alternatives': [
                    {
                        'inverter': self.extract_inverter_data(inv),
                        'score': score
                    }
                    for score, inv in scored_inverters[1:4]  # Top 3 alternatives
                ],
                'selection_reasoning': self._generate_selection_reasoning(
                    best_inverter,
                    pv_power_kwp,
                    best_score
                )
            }
            
            self.logger.info(
                f"Selected inverter: {best_inverter['model_name']} "
                f"({best_inverter['power_kw']}kW) for {pv_power_kwp}kWp system"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error selecting inverter: {e}")
            raise
    
    def _score_inverter(
        self,
        inverter: Dict[str, Any],
        optimal_power_kw: float,
        min_power_kw: float,
        max_power_kw: float,
        preferences: Dict[str, Any]
    ) -> float:
        """
        Score an inverter based on multiple criteria
        
        Returns:
            Score between 0 and 100
        """
        score = 0.0
        
        inverter_power = inverter.get('power_kw', 0.0)
        
        # Power sizing score (40 points max)
        if min_power_kw <= inverter_power <= max_power_kw:
            power_diff = abs(inverter_power - optimal_power_kw)
            power_score = 40 * (1 - power_diff / optimal_power_kw)
            score += max(0, power_score)
        else:
            # Penalty for out of range
            score -= 20
        
        # Efficiency score (20 points max)
        efficiency = inverter.get('efficiency_percent', 95.0)
        efficiency_score = (efficiency - 90) * 4  # 95% = 20 points, 90% = 0 points
        score += max(0, min(20, efficiency_score))
        
        # Manufacturer preference (15 points max)
        preferred_manufacturer = preferences.get('manufacturer')
        if preferred_manufacturer:
            if inverter.get('brand', '').lower() == preferred_manufacturer.lower():
                score += 15
        
        # Feature matching (15 points max)
        required_features = preferences.get('features', [])
        if required_features:
            inverter_features = self._extract_features(inverter)
            matching_features = sum(
                1 for feature in required_features
                if any(feature.lower() in inv_feature.lower() for inv_feature.lower() in inverter_features)
            )
            feature_score = (matching_features / len(required_features)) * 15
            score += feature_score
        
        # Price score (10 points max) - lower is better
        price = inverter.get('price_euro', 0.0)
        if price > 0:
            # Normalize price score (assuming typical range 500-5000 EUR)
            normalized_price = min(price / 5000, 1.0)
            price_score = 10 * (1 - normalized_price)
            score += price_score
        
        return max(0, score)
    
    def _generate_selection_reasoning(
        self,
        inverter: Dict[str, Any],
        pv_power_kwp: float,
        score: float
    ) -> str:
        """Generate human-readable reasoning for inverter selection"""
        inverter_power = inverter.get('power_kw', 0.0)
        sizing_ratio = pv_power_kwp / inverter_power if inverter_power > 0 else 0
        
        reasoning = f"Wechselrichter {inverter['model_name']} ausgewählt:\n"
        reasoning += f"- Leistung: {inverter_power}kW (DC/AC-Verhältnis: {sizing_ratio:.2f})\n"
        reasoning += f"- Wirkungsgrad: {inverter.get('efficiency_percent', 0)}%\n"
        reasoning += f"- Auswahlpunktzahl: {score:.1f}/100\n"
        
        if 0.8 <= sizing_ratio <= 1.0:
            reasoning += "- Optimale Dimensionierung für maximale Effizienz\n"
        elif sizing_ratio > 1.0:
            reasoning += f"- Überdimensionierung um {(sizing_ratio - 1) * 100:.1f}% (erhöhte Sicherheit)\n"
        else:
            reasoning += f"- Unterdimensionierung um {(1 - sizing_ratio) * 100:.1f}% (Spitzenlastbegrenzung)\n"
        
        return reasoning
    
    def calculate_inverter_sizing(
        self,
        pv_power_kwp: float,
        module_voltage: float,
        module_current: float,
        string_configuration: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate detailed inverter sizing requirements
        
        Args:
            pv_power_kwp: Total PV power in kWp
            module_voltage: Module voltage (Vmp)
            module_current: Module current (Imp)
            string_configuration: String layout configuration
            
        Returns:
            Detailed sizing calculations
        """
        try:
            modules_per_string = string_configuration.get('modules_per_string', 10)
            number_of_strings = string_configuration.get('number_of_strings', 2)
            
            # Calculate string voltage and current
            string_voltage = module_voltage * modules_per_string
            string_current = module_current
            total_current = string_current * number_of_strings
            
            # Calculate required inverter specifications
            # Add safety margins
            required_max_voltage = string_voltage * 1.2  # 20% safety margin
            required_max_current = total_current * 1.1   # 10% safety margin
            required_power_kw = pv_power_kwp * 0.9      # Typical sizing ratio
            
            # Calculate optimal MPPT configuration
            mppt_count = self._calculate_optimal_mppt_count(number_of_strings)
            strings_per_mppt = math.ceil(number_of_strings / mppt_count)
            
            sizing_data = {
                'required_power_kw': required_power_kw,
                'recommended_power_range': {
                    'min_kw': pv_power_kwp * 0.8,
                    'optimal_kw': pv_power_kwp * 0.9,
                    'max_kw': pv_power_kwp * 1.0
                },
                'dc_specifications': {
                    'string_voltage': string_voltage,
                    'required_max_voltage': required_max_voltage,
                    'total_current': total_current,
                    'required_max_current': required_max_current
                },
                'mppt_configuration': {
                    'recommended_mppt_count': mppt_count,
                    'strings_per_mppt': strings_per_mppt,
                    'current_per_mppt': total_current / mppt_count
                },
                'sizing_ratio': {
                    'dc_ac_ratio': 1.0 / 0.9,  # Typical oversizing
                    'description': 'DC/AC-Verhältnis (PV-Leistung / Wechselrichterleistung)'
                },
                'safety_margins': {
                    'voltage_margin_percent': 20,
                    'current_margin_percent': 10
                }
            }
            
            self.logger.info(f"Calculated inverter sizing for {pv_power_kwp}kWp system")
            return sizing_data
            
        except Exception as e:
            self.logger.error(f"Error calculating inverter sizing: {e}")
            raise
    
    def _calculate_optimal_mppt_count(self, number_of_strings: int) -> int:
        """Calculate optimal number of MPPT trackers"""
        if number_of_strings <= 2:
            return 1
        elif number_of_strings <= 4:
            return 2
        elif number_of_strings <= 6:
            return 3
        else:
            return 4
    
    def check_inverter_compatibility(
        self,
        inverter: Dict[str, Any],
        pv_system: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if inverter is compatible with PV system
        
        Args:
            inverter: Inverter specifications
            pv_system: PV system specifications
            
        Returns:
            Compatibility check results
        """
        try:
            compatibility_checks = []
            is_compatible = True
            warnings = []
            
            # Extract specifications
            inverter_power = inverter.get('power_kw', 0.0)
            pv_power = pv_system.get('pv_power_kwp', 0.0)
            string_voltage = pv_system.get('string_voltage', 0.0)
            total_current = pv_system.get('total_current', 0.0)
            
            # Check 1: Power compatibility
            sizing_ratio = pv_power / inverter_power if inverter_power > 0 else 0
            if 0.8 <= sizing_ratio <= 1.2:
                compatibility_checks.append({
                    'check': 'Leistungsanpassung',
                    'status': 'OK',
                    'details': f'DC/AC-Verhältnis: {sizing_ratio:.2f} (optimal: 0.8-1.2)'
                })
            elif sizing_ratio > 1.2:
                is_compatible = False
                compatibility_checks.append({
                    'check': 'Leistungsanpassung',
                    'status': 'FEHLER',
                    'details': f'PV-Leistung zu hoch: {sizing_ratio:.2f} (max: 1.2)'
                })
            else:
                warnings.append('Wechselrichter überdimensioniert')
                compatibility_checks.append({
                    'check': 'Leistungsanpassung',
                    'status': 'WARNUNG',
                    'details': f'Wechselrichter überdimensioniert: {sizing_ratio:.2f}'
                })
            
            # Check 2: Voltage compatibility
            max_dc_voltage = inverter.get('max_dc_voltage', 1000.0)
            if string_voltage <= max_dc_voltage * 0.9:  # 90% of max for safety
                compatibility_checks.append({
                    'check': 'Spannungskompatibilität',
                    'status': 'OK',
                    'details': f'String-Spannung: {string_voltage}V (max: {max_dc_voltage}V)'
                })
            else:
                is_compatible = False
                compatibility_checks.append({
                    'check': 'Spannungskompatibilität',
                    'status': 'FEHLER',
                    'details': f'String-Spannung zu hoch: {string_voltage}V > {max_dc_voltage}V'
                })
            
            # Check 3: Current compatibility
            max_dc_current = inverter.get('max_dc_current', 30.0)
            mppt_count = inverter.get('mppt_count', 2)
            current_per_mppt = total_current / mppt_count
            
            if current_per_mppt <= max_dc_current * 0.9:
                compatibility_checks.append({
                    'check': 'Stromkompatibilität',
                    'status': 'OK',
                    'details': f'Strom pro MPPT: {current_per_mppt:.1f}A (max: {max_dc_current}A)'
                })
            else:
                is_compatible = False
                compatibility_checks.append({
                    'check': 'Stromkompatibilität',
                    'status': 'FEHLER',
                    'details': f'Strom zu hoch: {current_per_mppt:.1f}A > {max_dc_current}A'
                })
            
            # Check 4: MPPT configuration
            number_of_strings = pv_system.get('number_of_strings', 0)
            if number_of_strings <= mppt_count * 2:
                compatibility_checks.append({
                    'check': 'MPPT-Konfiguration',
                    'status': 'OK',
                    'details': f'{number_of_strings} Strings auf {mppt_count} MPPTs'
                })
            else:
                warnings.append('Zu viele Strings pro MPPT')
                compatibility_checks.append({
                    'check': 'MPPT-Konfiguration',
                    'status': 'WARNUNG',
                    'details': f'Viele Strings pro MPPT: {number_of_strings}/{mppt_count}'
                })
            
            result = {
                'is_compatible': is_compatible,
                'compatibility_score': sum(
                    1 for check in compatibility_checks if check['status'] == 'OK'
                ) / len(compatibility_checks) * 100,
                'checks': compatibility_checks,
                'warnings': warnings,
                'recommendation': self._generate_compatibility_recommendation(
                    is_compatible,
                    warnings,
                    inverter,
                    pv_system
                )
            }
            
            self.logger.info(
                f"Compatibility check: {inverter.get('model_name')} - "
                f"{'Compatible' if is_compatible else 'Not compatible'}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error checking inverter compatibility: {e}")
            raise
    
    def _generate_compatibility_recommendation(
        self,
        is_compatible: bool,
        warnings: List[str],
        inverter: Dict[str, Any],
        pv_system: Dict[str, Any]
    ) -> str:
        """Generate compatibility recommendation"""
        if is_compatible and not warnings:
            return f"Wechselrichter {inverter.get('model_name')} ist vollständig kompatibel mit dem PV-System."
        elif is_compatible and warnings:
            return f"Wechselrichter {inverter.get('model_name')} ist kompatibel, aber beachten Sie: {', '.join(warnings)}"
        else:
            return f"Wechselrichter {inverter.get('model_name')} ist NICHT kompatibel. Bitte wählen Sie einen anderen Wechselrichter."
    
    def create_multi_inverter_configuration(
        self,
        pv_power_kwp: float,
        system_layout: Dict[str, Any],
        available_inverters: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Create multi-inverter configuration for large systems
        
        Args:
            pv_power_kwp: Total PV power in kWp
            system_layout: System layout with roof sections
            available_inverters: Available inverters
            
        Returns:
            Multi-inverter configuration
        """
        try:
            # Determine if multi-inverter setup is needed
            # Typically for systems > 30kWp or multiple roof orientations
            needs_multi_inverter = (
                pv_power_kwp > 30 or
                len(system_layout.get('roof_sections', [])) > 1
            )
            
            if not needs_multi_inverter:
                # Single inverter is sufficient
                single_config = self.select_inverter(pv_power_kwp, available_inverters=available_inverters)
                return {
                    'configuration_type': 'single',
                    'inverter_count': 1,
                    'inverters': [single_config['selected_inverter']],
                    'total_power_kw': single_config['selected_inverter']['power_kw'],
                    'reasoning': 'Einzelwechselrichter ausreichend für Systemgröße'
                }
            
            # Calculate optimal number of inverters
            roof_sections = system_layout.get('roof_sections', [])
            
            if len(roof_sections) > 1:
                # One inverter per roof section (if different orientations)
                inverter_count = len(roof_sections)
                power_per_inverter = pv_power_kwp / inverter_count
            else:
                # Multiple inverters for large system
                # Use 10-15kW inverters for optimal efficiency
                optimal_inverter_size = 12.0  # kW
                inverter_count = math.ceil(pv_power_kwp / optimal_inverter_size)
                power_per_inverter = pv_power_kwp / inverter_count
            
            # Select inverters
            selected_inverters = []
            for i in range(inverter_count):
                inverter_selection = self.select_inverter(
                    power_per_inverter,
                    available_inverters=available_inverters
                )
                selected_inverters.append(inverter_selection['selected_inverter'])
            
            total_inverter_power = sum(inv['power_kw'] for inv in selected_inverters)
            
            configuration = {
                'configuration_type': 'multi',
                'inverter_count': inverter_count,
                'inverters': selected_inverters,
                'total_power_kw': total_inverter_power,
                'power_distribution': [
                    {
                        'inverter_index': i,
                        'inverter': inv,
                        'assigned_power_kwp': power_per_inverter,
                        'roof_section': roof_sections[i] if i < len(roof_sections) else None
                    }
                    for i, inv in enumerate(selected_inverters)
                ],
                'sizing_ratio': pv_power_kwp / total_inverter_power,
                'reasoning': self._generate_multi_inverter_reasoning(
                    inverter_count,
                    pv_power_kwp,
                    roof_sections
                )
            }
            
            self.logger.info(
                f"Created multi-inverter configuration: {inverter_count} inverters "
                f"for {pv_power_kwp}kWp system"
            )
            
            return configuration
            
        except Exception as e:
            self.logger.error(f"Error creating multi-inverter configuration: {e}")
            raise
    
    def _generate_multi_inverter_reasoning(
        self,
        inverter_count: int,
        pv_power_kwp: float,
        roof_sections: List[Dict[str, Any]]
    ) -> str:
        """Generate reasoning for multi-inverter configuration"""
        reasoning = f"Multi-Wechselrichter-Konfiguration mit {inverter_count} Wechselrichtern:\n"
        
        if len(roof_sections) > 1:
            reasoning += f"- {len(roof_sections)} Dachflächen mit unterschiedlichen Ausrichtungen\n"
            reasoning += "- Separate Wechselrichter für optimale MPP-Tracking pro Dachfläche\n"
        else:
            reasoning += f"- Große Anlage ({pv_power_kwp}kWp) erfordert mehrere Wechselrichter\n"
            reasoning += "- Verteilung auf mehrere Geräte für bessere Effizienz und Redundanz\n"
        
        reasoning += f"- Gesamtleistung: {pv_power_kwp}kWp auf {inverter_count} Wechselrichter verteilt\n"
        reasoning += "- Vorteile: Höhere Systemverfügbarkeit, besseres Teillastverhalten\n"
        
        return reasoning
    
    def integrate_monitoring(
        self,
        inverter: Dict[str, Any],
        monitoring_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Integrate inverter with monitoring system
        
        Args:
            inverter: Inverter specifications
            monitoring_config: Monitoring system configuration
            
        Returns:
            Integration configuration
        """
        try:
            # Check if inverter supports monitoring
            supports_monitoring = (
                'smart_home' in self._extract_features({'smart_home': True}) or
                inverter.get('technology', '').lower().find('smart') >= 0
            )
            
            if not supports_monitoring:
                return {
                    'monitoring_supported': False,
                    'message': 'Wechselrichter unterstützt keine direkte Überwachung',
                    'alternative': 'Externe Überwachungslösung erforderlich'
                }
            
            # Generate monitoring integration config
            integration_config = {
                'monitoring_supported': True,
                'inverter_id': inverter.get('id'),
                'inverter_model': inverter.get('model_name'),
                'manufacturer': inverter.get('manufacturer'),
                'communication_protocol': monitoring_config.get('protocol', 'Modbus TCP'),
                'data_points': [
                    'AC Power Output (kW)',
                    'DC Power Input (kW)',
                    'Efficiency (%)',
                    'Daily Energy (kWh)',
                    'Total Energy (kWh)',
                    'DC Voltage (V)',
                    'DC Current (A)',
                    'AC Voltage (V)',
                    'AC Current (A)',
                    'Temperature (°C)',
                    'Status',
                    'Error Codes'
                ],
                'update_interval_seconds': monitoring_config.get('update_interval', 60),
                'data_retention_days': monitoring_config.get('retention_days', 365),
                'alerts': [
                    {
                        'type': 'low_efficiency',
                        'threshold': 90,
                        'description': 'Wirkungsgrad unter 90%'
                    },
                    {
                        'type': 'high_temperature',
                        'threshold': 70,
                        'description': 'Temperatur über 70°C'
                    },
                    {
                        'type': 'error_state',
                        'threshold': None,
                        'description': 'Fehlerzustand erkannt'
                    }
                ],
                'api_endpoints': {
                    'real_time_data': f"/api/v1/monitoring/inverter/{inverter.get('id')}/realtime",
                    'historical_data': f"/api/v1/monitoring/inverter/{inverter.get('id')}/history",
                    'statistics': f"/api/v1/monitoring/inverter/{inverter.get('id')}/statistics",
                    'alerts': f"/api/v1/monitoring/inverter/{inverter.get('id')}/alerts"
                }
            }
            
            self.logger.info(
                f"Monitoring integration configured for {inverter.get('model_name')}"
            )
            
            return integration_config
            
        except Exception as e:
            self.logger.error(f"Error integrating monitoring: {e}")
            raise
    
    def _get_available_inverters(self) -> List[Dict[str, Any]]:
        """Get available inverters from database"""
        # This would query the database for inverters
        # For now, return empty list - will be implemented with database integration
        if self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("""
                    SELECT * FROM products 
                    WHERE category = 'Wechselrichter' OR category = 'Inverter'
                    ORDER BY power_kw ASC
                """)
                columns = [description[0] for description in cursor.description]
                inverters = [dict(zip(columns, row)) for row in cursor.fetchall()]
                return inverters
            except Exception as e:
                self.logger.error(f"Error fetching inverters from database: {e}")
                return []
        return []
